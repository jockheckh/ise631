"""Runner contract tests: provenance, path safety, and four-way evidence.

The first tests are solver-free.  The final integration test deliberately
requires a usable Gurobi license in the current Windows interpreter, as the
project's Phase 0 gate requires; a failure must not be converted to a skip.
"""

import copy
import json
from pathlib import Path

import pytest

from scripts import run_phase2_verification as runner


EXAMPLE_CONFIG = runner.ROOT / "configs" / "phase2" / "example1.json"
SYNTHETIC_CONFIG = runner.ROOT / "configs" / "phase2" / "low_now_high_later.json"


def test_example_1_config_is_source_data_and_synthetic_is_separate() -> None:
    published, example = runner.load_config(EXAMPLE_CONFIG)
    synthetic, other = runner.load_config(SYNTHETIC_CONFIG)
    assert published["classification"] == "source_example_1"
    assert (example.T, example.c, example.f, example.p) == (2, (1,), (1.0,), ((0.5,), (0.5,)))
    assert synthetic["classification"] == "synthetic_verification"
    assert other.name == "low_now_high_later"
    assert "synthetic" in other.provenance.lower()


def test_published_label_cannot_be_attached_to_different_data(tmp_path: Path) -> None:
    config = json.loads(EXAMPLE_CONFIG.read_text(encoding="utf-8"))
    config["instance"]["p"][0][0] = 0.4
    altered = tmp_path / "altered.json"
    altered.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="exact published Example 1"):
        runner.load_config(altered)


def test_path_guard_refuses_escape_root_and_existing_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    allowed = tmp_path / "results"
    allowed.mkdir()
    monkeypatch.setattr(runner, "ROOT", tmp_path.resolve())
    monkeypatch.setattr(runner, "RESULTS_ROOT", allowed.resolve())
    assert runner.checked_run_dir(allowed / "new_run") == (allowed / "new_run").resolve()
    with pytest.raises(ValueError, match="strictly inside"):
        runner.checked_run_dir(allowed)
    with pytest.raises(ValueError, match="strictly inside"):
        runner.checked_run_dir(tmp_path / "outside")
    existing = allowed / "existing"
    existing.mkdir()
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        runner.checked_run_dir(existing)


def test_config_rejects_missing_limits_and_bad_probability_mass(tmp_path: Path) -> None:
    source = json.loads(SYNTHETIC_CONFIG.read_text(encoding="utf-8"))
    missing = copy.deepcopy(source)
    del missing["max_states"]
    path = tmp_path / "config.json"
    path.write_text(json.dumps(missing), encoding="utf-8")
    with pytest.raises(ValueError, match="missing max_states"):
        runner.load_config(path)
    overfull = copy.deepcopy(source)
    overfull["instance"]["p"][0] = [0.8, 0.3]
    path.write_text(json.dumps(overfull), encoding="utf-8")
    with pytest.raises(ValueError, match="exceed one"):
        runner.load_config(path)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_objective_comparison_rejects_nonfinite_values(bad: float) -> None:
    # This assertion gate must not let NaN through just because Python's
    # ordinary greater-than and absolute-difference tests return false.
    with pytest.raises(AssertionError, match="not finite"):
        runner._near(bad, 1.0, 1e-7, "test objective")


def test_licensed_four_way_example_and_opportunity_cost_case() -> None:
    # This is not a stochastic simulation. ExactDP and the static-policy
    # evaluator recursively integrate all arrival branches; both LPs use
    # Gurobi and must independently match the analytical toy values.
    example_config, example = runner.load_config(EXAMPLE_CONFIG)
    example_result, example_raw = runner.verify(example_config, example)
    assert example_result["values"] == pytest.approx({
        "exact_dp": 0.75,
        "exact_D0": 0.75,
        "exact_occupancy": 0.75,
        "fluid_upper_bound": 1.0,
        "static_policy_exact_reward": 0.75,
    })
    assert example_result["assertions"]["status"] == "passed"
    assert len(example_raw["occupancy"]) == 5

    synthetic_config, synthetic = runner.load_config(SYNTHETIC_CONFIG)
    synthetic_result, _ = runner.verify(synthetic_config, synthetic)
    assert synthetic_result["values"] == pytest.approx({
        "exact_dp": 1.2,
        "exact_D0": 1.2,
        "exact_occupancy": 1.2,
        "fluid_upper_bound": 1.6,
        "static_policy_exact_reward": 1.12,
    })
    assert synthetic_result["classification"] == "synthetic_verification"
