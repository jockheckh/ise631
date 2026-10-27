# Sequenced analytical work plan and IPR gates

The project's IPR dates are not yet recorded; do not invent them. Add professor-specific requirements and dates in `DECISIONS.md`.

## Phase 0 — source / WSL / Gurobi preflight (before any claims)
- Ensure instructor PDF, Adelman full paper and appendices are available and hash-indexed; confirm title, page numbering, equations and appendix scope.
- Test local Python, Gurobi import, **actual solve through the usable license**, and pytest; resolve license issues without exposing credentials. Record a source manifest.
- Read the literal instructor prompt and audit `requirements.csv` for missing obligations.
- **Exit:** source inventory and successful Gurobi LP preflight, or a clearly documented blocker. The paper/appendices are user-provided, not bundled.

## Phase 1 — source-referenced theory / IPR 2
- Define the finite-horizon network RM MDP; derive exact Bellman recursion and a correctly indexed finite-horizon LP.
- Separately explain the instructor's generic discounted primal/occupancy dual and complementary slackness.
- Derive fluid LP and dual; derive source-matched affine ALP; formalize bid prices, bound dominance and proof technique.
- Determine the actual pricing/separation subproblem, its complexity and the role of simplex/dual variables.
- **Exit:** theorem ledger with paper pages/equations, audit memo, rigorous proof notes, all assumption/sign issues resolved or explicitly blocked.

## Phase 2 — exact oracle and baseline implementations / IPR 2
- Implement one tiny exact DP + independent enumeration, deterministic/fluid Gurobi LP and static bid-price policy.
- Test zero demand, terminal time, tight/loose capacities and single-resource/product cases.
- **Exit:** executable tests passing, solver logs, tiny instance data and reference values.

## Phase 3 — Adelman approximation / IPR 3
- Implement paper-faithful ALP/algorithm and dynamic policy only after Phase 1 source check.
- Check violated constraints, dual/reduced-cost signs, stopping criteria and numerical feasibility.
- Reproduce any available published instance precisely; if unavailable, mark published replication blocked instead of calling synthetic tests replication.
- **Exit:** independent reviewer checks two or more small cases against exact DP; saved manifests and raw evidence.

## Phase 4 — mandatory experiments / IPR 3
- Compare exact MDP (small cases), fluid upper bound, any certified ALP bound, static and dynamic policy expected returns; preserve CI vs deterministic-bound distinction.
- Perform approved scaling and truncation studies, measuring structural size, runtime, memory, iterations, gaps and lost certificates.
- Critique assumptions, alternate benchmarks and author claims; do not suppress negative results.
- **Exit:** all mandatory requirements and RQ1–RQ5 traced to independently reviewed evidence; professor-required published replications resolved, performed, or listed as irreproducible for a documented reason.

## Phase 5 — mandatory completeness / final analytic handoff
- Complete `requirements.csv` I01–I14 or explicitly report any unverified item, with reviewer file and evidence.
- Create `reports/FINAL_ANALYTICAL_HANDOFF.md`: confirmed equations, test-backed numbers, chart data, concise interpretations and audit exceptions.
- **Exit:** `python scripts/audit_coverage.py` and test suite pass, substantive independent review resolves all critical faults. No automatic surveillance-pricing work.

## Phase 6 — surveillance pricing (optional, only after human releases gate)
- Run `python scripts/check_extension_gate.py`; all instructor requirements must be verified and `DECISIONS.md` must include explicit human release.
- First complete a one-page structural mapping: state/actions/finite capacity/uncertain arrivals/reward, ethical data limits, availability and identification issues. If mapping fails, present it only as motivation/future work.
- Only then prototype a narrow real or realistically calibrated dataset application. Do not retroactively modify mandatory results.
