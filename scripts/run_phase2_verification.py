"""Run a source-grounded *tiny* Phase 2 verification from PowerShell.

Usage::

    python -m scripts.run_phase2_verification --config configs/phase2/example1.json \
        --run-dir results/phase2_example1_001

This is not Adelman's approximate LP or a reproduction of his unpublished
hub-and-spoke random draws. It checks Bellman equation (1), exact D0 (3),
fluid primal (4)-(6), and their separately derived, unnumbered LP duals
from Adelman (2007) against separately coded models.
All policy values here are exact expectations, *not* Monte Carlo estimates.
The existing LP modules use Gurobi with OutputFlag=0 and Threads=1; their
status/iteration/residual metrics are persisted, but raw solver logs are not
yet exposed by those modules.  No model is silently downscaled.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
from typing import Any

from scripts.preflight import check_gurobi
from scripts.write_manifest import make_manifest
from src.adelman.exact_dp import ExactDP, evaluate_policy_exact
from src.adelman.exact_lp import solve_exact_lp
from src.adelman.fluid_lp import solve_fluid_lp, static_bid_price_accept
from src.adelman.instances import NetworkInstance


ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = (ROOT / "results").resolve()
PAPER = ROOT / "sources" / "adelman" / "EBSCO-FullText-10_26_2026.pdf"


def sha256_file(path: Path) -> str:
    """Hash bytes, rather than file timestamps, for stable provenance."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checked_run_dir(raw: str | Path) -> Path:
    """Require a *new* directory strictly below this repository's results/.

    Resolving first detects ``..`` paths and existing symlinks that point
    elsewhere.  Neither the workspace root nor results/ itself is writable
    via this CLI.  Existing runs are immutable: no resume/overwrite switch.
    """
    # A malicious or accidental results/ symlink outside the repository
    # would defeat the apparent relative-path guard. Refuse that too.
    if not RESULTS_ROOT.is_relative_to(ROOT.resolve()):
        raise ValueError("resolved results/ root must stay inside the repository")
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    resolved = candidate.resolve()
    if resolved == RESULTS_ROOT or not resolved.is_relative_to(RESULTS_ROOT):
        raise ValueError("run-dir must be strictly inside the repository results/ directory")
    if resolved.exists():
        raise FileExistsError(f"refusing to overwrite existing run directory: {resolved}")
    return resolved


def load_config(path: Path) -> tuple[dict[str, Any], NetworkInstance]:
    """Read an explicit small instance; never infer or adjust missing data.

    Reproduction has a stronger requirement than a label: every source
    Example 1 datum must equal the known published one-resource example.
    All other inputs are classified as synthetic verification and cannot
    masquerade as Adelman's published tables.
    """
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("config requires schema_version 1")
    if config.get("classification") not in {"source_example_1", "synthetic_verification"}:
        raise ValueError("classification must be source_example_1 or synthetic_verification")
    for key in ("instance", "max_states", "max_state_action_pairs", "assertion_tolerance"):
        if key not in config:
            raise ValueError(f"config is missing {key}")
    raw = config["instance"]
    if not isinstance(raw, dict):
        raise ValueError("instance must be a JSON object")
    expected_fields = {"T", "m", "n", "c", "A", "f", "p", "name", "provenance"}
    if set(raw) != expected_fields:
        raise ValueError(f"instance fields must be exactly {sorted(expected_fields)}")
    instance = NetworkInstance(**raw)
    for limit in ("max_states", "max_state_action_pairs"):
        value = config[limit]
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{limit} must be a positive integer")
    tolerance = config["assertion_tolerance"]
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or not 0 < tolerance <= 1e-4:
        raise ValueError("assertion_tolerance must be positive and at most 1e-4")
    if config["classification"] == "source_example_1":
        source_data = (2, 1, 1, (1,), ((1,),), (1.0,), ((0.5,), (0.5,)))
        observed = (instance.T, instance.m, instance.n, instance.c, instance.A, instance.f, instance.p)
        if observed != source_data:
            raise ValueError("source_example_1 label requires the exact published Example 1 data")
        if not PAPER.is_file():
            raise FileNotFoundError("the local Adelman 2007 source PDF is required for source_example_1")
    return config, instance


def _near(left: float, right: float, tolerance: float, label: str) -> None:
    """Use one explicit, scale-aware tolerance for cross-model assertions."""
    if not math.isfinite(left) or not math.isfinite(right):
        raise AssertionError(f"{label}: a compared objective was not finite")
    if abs(left - right) > tolerance * max(1.0, abs(left), abs(right)):
        raise AssertionError(f"{label}: {left:.12g} versus {right:.12g}")


def verify(config: dict[str, Any], instance: NetworkInstance) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compute four different mathematical objects, then gate their claims.

    Exact policy reward <= exact optimum (DP = D0 = occupancy) <= fluid
    upper bound.  LP residuals and statuses are checked *in addition* to
    objective agreement.  They support numerical correctness on this case,
    not a proof of the general bound theorem or source correspondence.
    """
    tolerance = float(config["assertion_tolerance"])
    dp = ExactDP(instance).initial_value()
    exact = solve_exact_lp(
        instance,
        max_states=config["max_states"],
        max_state_action_pairs=config["max_state_action_pairs"],
    )
    fluid = solve_fluid_lp(instance)
    static_reward = evaluate_policy_exact(
        instance,
        lambda t, r, j: static_bid_price_accept(instance, r, j, fluid.prices),
    )

    # NaN is especially dangerous: comparisons such as NaN > tolerance are
    # false, so an otherwise sensible inequality gate can silently pass.
    for label, value in (
        ("exact DP", dp), ("exact D0", exact.primal_objective),
        ("exact occupancy", exact.dual_objective),
        ("fluid primal", fluid.primal_objective),
        ("fluid dual", fluid.dual_objective),
        ("static policy", static_reward),
    ):
        if not math.isfinite(value):
            raise AssertionError(f"{label} objective was not finite")

    for label, status in (
        ("exact D0", exact.primal_status), ("exact occupancy", exact.dual_status),
        ("fluid primal", fluid.primal_status), ("fluid dual", fluid.dual_status),
    ):
        if status != 2:  # gurobipy.GRB.OPTIMAL; no fallback solver is used.
            raise AssertionError(f"{label} status was {status}, not OPTIMAL (2)")
    _near(dp, exact.primal_objective, tolerance, "DP versus exact D0")
    _near(dp, exact.dual_objective, tolerance, "DP versus occupancy dual")
    _near(fluid.primal_objective, fluid.dual_objective, tolerance, "fluid primal versus dual")
    for label, residual in (
        ("exact primal violation", exact.primal_violation),
        ("exact dual violation", exact.dual_violation),
        ("exact flow residual", exact.flow_residual),
        ("exact duality gap", exact.duality_gap),
        ("exact complementarity", exact.complementarity_residual),
        ("fluid primal violation", fluid.primal_violation),
        ("fluid dual violation", fluid.dual_violation),
        ("fluid duality gap", fluid.duality_gap),
        ("fluid complementarity", fluid.complementarity_residual),
    ):
        if not math.isfinite(residual) or residual > tolerance:
            raise AssertionError(f"{label} {residual:.12g} exceeds tolerance {tolerance:.12g}")
    if static_reward > dp + tolerance * max(1.0, abs(dp)):
        raise AssertionError("static policy reward exceeds exact optimal reward")
    if dp > fluid.primal_objective + tolerance * max(1.0, abs(fluid.primal_objective)):
        raise AssertionError("exact optimal reward exceeds fluid upper bound")
    if config["classification"] == "source_example_1":
        for label, observed, expected in (
            ("Example 1 exact", dp, 0.75),
            ("Example 1 fluid", fluid.primal_objective, 1.0),
            ("Example 1 static policy", static_reward, 0.75),
        ):
            _near(observed, expected, tolerance, label)

    exact_data = asdict(exact)
    occupancy = exact_data.pop("occupancy")
    values = exact_data.pop("value_function")
    summary = {
        "classification": config["classification"],
        "instance_name": instance.name,
        "provenance": instance.provenance,
        "dimensions": {"T": instance.T, "m": instance.m, "n": instance.n,
                       "initial_capacity": instance.c, "time_states": exact.state_count,
                       "state_action_pairs": exact.state_action_count},
        "assertion_tolerance": tolerance,
        "values": {"exact_dp": dp, "exact_D0": exact.primal_objective,
                   "exact_occupancy": exact.dual_objective,
                   "fluid_upper_bound": fluid.primal_objective,
                   "static_policy_exact_reward": static_reward},
        "exact_lp": exact_data,
        "fluid_lp": asdict(fluid),
        # The current fluid module does not expose Gurobi NumVars/NumConstrs.
        # These are dimensions implied by its explicit source formulation,
        # not telemetry read from the solver instance.
        "fluid_formulation_dimensions_expected": {
            "primal_variables": instance.n,
            "primal_constraints": instance.m + instance.n,
            "dual_variables": instance.m + instance.n,
            "dual_constraints": instance.n,
        },
        "assertions": {"status": "passed", "dp_D0_occupancy_agree": True,
                       "fluid_primal_dual_agree": True, "residuals_within_tolerance": True,
                       "policy_le_exact_le_fluid": True},
        "interpretation_limit": (
            "Numerical verification of this tiny instance only; not an ALP, dynamic-policy, "
            "published Table 2 replication, general theorem proof, or Monte Carlo result."
        ),
    }
    # Tuple-valued dictionary keys are encoded as explicit indexed rows.
    # JSON cannot preserve Python tuple keys faithfully in an object map.
    raw_solution = {
        "value_function": [
            {"period": t, "remaining": r, "value": value}
            for (t, r), value in sorted(values.items())
        ],
        "occupancy": [
            {"period": t, "remaining": r, "action": u, "mass": mass}
            for (t, r, u), mass in sorted(occupancy.items())
        ],
    }
    return summary, raw_solution


def run(config_path: Path, run_dir: Path) -> Path:
    """Preflight, solve, verify, and persist a new immutable results directory."""
    destination = checked_run_dir(run_dir)
    config, instance = load_config(config_path)
    if platform.system() != "Windows":
        raise RuntimeError("project runtime is Windows Python; do not run this workflow in WSL")
    preflight = check_gurobi()
    if not preflight["usable_for_tiny_lp"]:
        raise RuntimeError(f"Gurobi unusable in {sys.executable}: {preflight.get('error', 'unknown error')}")
    summary, raw_solution = verify(config, instance)

    # Nothing is written before every numerical gate passes. An existing
    # run directory is never overwritten, including after a failed solve.
    destination.mkdir(parents=True, exist_ok=False)
    # Preserve the supplied bytes exactly. Re-serializing/sorting would
    # change the evidence while retaining the original input's hash.
    saved_config = destination / "input_config.json"
    saved_config.write_bytes(config_path.read_bytes())
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (destination / "exact_lp_raw_solution.json").write_text(
        json.dumps(raw_solution, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = make_manifest(f"phase2_{instance.name}", config.get("seed"))
    manifest.update({
        "python_executable": sys.executable,
        "runtime_decision": "Windows Python invoked from PowerShell; no WSL",
        "gurobi_preflight": preflight,
        "gurobi_version": summary["exact_lp"]["gurobi_version"],
        "model_definition": (
            "Adelman 2007 Bellman (1), D0 (3), fluid primal (4)-(6), "
            "unnumbered fluid dual after (6), and derived exact occupancy dual"
        ),
        "solver_settings": {"OutputFlag": 0, "Threads": 1,
                            "exact_OptimalityTol": summary["exact_lp"]["optimality_tolerance"],
                            "exact_FeasibilityTol": summary["exact_lp"]["feasibility_tolerance"],
                            "fluid_OptimalityTol": summary["fluid_lp"]["optimality_tolerance"],
                            "fluid_FeasibilityTol": summary["fluid_lp"]["feasibility_tolerance"]},
        "solver_log_note": "Existing model functions suppress raw Gurobi logs; status, timings, iterations, and residuals are in summary.json.",
        "input_data_hashes": {
            "source_config_sha256": sha256_file(config_path),
            "saved_input_config_sha256": sha256_file(saved_config),
            "source_pdf_sha256": sha256_file(PAPER) if PAPER.is_file() else None,
        },
        "source_config_repo_relative_path": (
            str(config_path.relative_to(ROOT)) if config_path.is_relative_to(ROOT) else None
        ),
        "runner_sha256": sha256_file(Path(__file__)),
        "paper_table_id": "Example 1, printed p. 653" if config["classification"] == "source_example_1" else None,
        "license_scope": "Only the tiny solved models were tested; larger license limits are unknown.",
    })
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="explicit JSON tiny-instance config")
    parser.add_argument("--run-dir", required=True, type=Path, help="new directory strictly under results/")
    args = parser.parse_args()
    config_path = args.config if args.config.is_absolute() else ROOT / args.config
    print(run(config_path.resolve(), args.run_dir))


if __name__ == "__main__":
    main()
