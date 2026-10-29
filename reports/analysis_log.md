# Executed analysis log

This log distinguishes source checks, mathematical audits, executable tests,
and published-result replication. A passing test does not prove a theorem or
recreate an unpublished random instance.

## 2026-10-28 — Windows source/runtime and Phase 2 tiny-model checks

- Question: Can the selected Windows Python/Gurobi interpreter solve LPs, and
  do independently implemented exact DP, exact Bellman/occupancy LP, fluid LP,
  and static-policy valuation agree on hand-checkable cases?
- Assumptions: finite horizon; at most one class arrives per period; known
  probabilities; nonreplenishing integer capacities; admissible accept/reject
  actions. See `reports/PHASE1_SOURCE_TO_CODE_SPEC.md` for the indexed source
  equations and model distinctions.
- Sources and provenance: `reports/SOURCE_AND_RUNTIME_GATE_2026-10-28.md`.
  The full Adelman (2007) PDF is local. Original 2007 instance draws and seeds
  are unavailable; the later INFORMS repository is a structural reference, not
  an archive of the 2007 numerical tables.
- Executed commands: `python scripts/preflight.py --output
  results/preflight_windows_2026_10_28/preflight.json` and
  `python -m pytest -q -p no:cacheprovider --junitxml=results/phase2_full_suite_2026_10_28/pytest.xml`
  in the licensed Windows user context. The final suite passed 39 tests in
  0.32 seconds. Gurobi 13.0.3 solved
  the preflight LP at objective 0.5; Python was 3.13.7 at
  `C:\Python313\python.exe`.
- Model tests: `tests/test_phase2_baseline.py` checks Example 1, zero demand,
  terminal/capacity boundaries, coupled resources, and source-inspired
  topology. `tests/test_phase2_exact_lp.py` also compares against a separate
  exhaustive action tree and checks a three-period probability-flow chain.
  `tests/test_phase2_runner.py` tests provenance and path safety, rejects
  non-finite comparison values, and checks both numerical cases.
- Final run evidence: `results/phase2_example1_final_2026_10_28/` and
  `results/phase2_low_now_high_later_final_2026_10_28/`. Each contains the
  exact saved input bytes, summary with asserted residuals/solver diagnostics,
  raw occupancy/value rows, and a manifest with matching source/snapshot
  input hashes. The earlier same-date runs without `_final` were preliminary
  and must not be cited as final evidence.
- Results: Example 1 exact DP/D0/occupancy = 0.75, fluid upper bound = 1.00,
  static policy exact reward = 0.75. The separate synthetic low-now/high-later
  case gives 1.20/1.20/1.20/1.60/1.12 in that same order. All recorded
  solver status, residual, primal-dual, and bound assertions passed at the
  configured `1e-7` run-level tolerance.
- Independent review: `theory_auditor` and `independent_reviewer` found no
  critical sign or state-flow fault in the bounded baseline/exact-LP code.
  Run-level residual assertions and persisted artifacts were added after this
  review. The independent reviewer then signed off the final runner, hashes,
  JUnit record, source labels, and toy values with no material blocker for the
  bounded Phase 2 claim. Structured Gurobi status, timing,
  iteration, tolerance, dimension, objective and residual fields are the
  solver log for this phase. Raw Gurobi text logs were suppressed to avoid
  exposing license metadata.
- Limits: no affine ALP, source P1 pricing/column generation, dynamic policy,
  2007 Table 2 replication, large-model license-capacity test, or simulation
  result has been established. The full Phase 1 theory audit remains open;
  this is a bounded Phase 2 baseline, not permission to claim Phase 3 results.
