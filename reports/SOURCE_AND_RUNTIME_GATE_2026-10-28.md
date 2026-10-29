# Source and Windows runtime gate — 2026-10-28

Status: source inventory recorded; small-LP Windows preflight passed outside
the restricted sandbox. This does **not** certify the theory, large-model
license capacity, or any numerical replication.

## Local primary sources

| Source | Location | SHA-256 / status |
|---|---|---|
| Instructor prompt | `sources/10_MDPs (1).pdf` | `6f8535967a6b0be80f32cf12c4891ef83dd396846303f24ad0208c33e2858678` |
| Adelman (2007), full text | `sources/adelman/EBSCO-FullText-10_26_2026.pdf` | `546fd5808813c5535be3a0895cbbc310e98f92b84d539b34a42564240bd3a8d8` |

The 2007 PDF contains the printed Appendix on pp. 660-661. No separate
supplement or original numerical input files, random seeds, or arrival streams
are present in the workspace. The original paper's Table 1-2 design is
source-checkable, but its random instances cannot be exactly reconstructed
from the available source alone.

## Later hub-and-spoke reference, not the 2007 archive

The user supplied `https://github.com/INFORMSJoC/2023.0418`, associated with
Adelman, Barz, and Olivares-Nadal, *Dynamic Basis Function Generation for
Network Revenue Management* (2025), paper DOI `10.1287/ijoc.2023.0418`,
repository DOI `10.1287/ijoc.2023.0418.cd`. The public repository was inspected
at commit `840949ac3ee6a88aa73c2cbfd635b9ebae39ba73`.

Its `src/MAIN_fitresidualAA.run` sets random seed 1, defaults to `L=2` and
`T=20`, uses `m=2L` resources, and sets equal leg capacities by rounding
expected aggregate leg demand divided by `1.61m`. However, it calls
`data data_generation.dat`, and that file is not in the inspected repository
snapshot. The repository implements the later H-2PIAlg in AMPL with an affine
baseline; it does **not** contain the 2007 P1 column-generation implementation
or original 2007 instances. The 2025 paper's capacity table also differs from
the 2007 paper's Table 2. Therefore, use this as a documented, same-network-
architecture synthetic benchmark, not exact 2007 table replication.

## Windows solver check

Command: `python scripts/preflight.py` from `C:\ISE631`.

- Selected interpreter: `C:\Python313\python.exe`; Python 3.13.7;
  `gurobipy`/Gurobi 13.0.3; `is_wsl=false`.
- Restricted sandbox account: import succeeded, but the license handshake
  failed with a licensed-user mismatch. No LP was solved in that context.
- Normal Windows user context: Gurobi status 2 (OPTIMAL), tiny-LP objective
  0.5. The preflight now suppresses license metadata before starting Gurobi.
- Research-size license capacity remains unverified. Do not infer feasibility
  of the largest proposed MIPs from the tiny-LP solve.
- Redacted raw preflight JSON: results/preflight_windows_2026_10_28/preflight.json.
- Existing test suite: 5 passed in 0.30 seconds under the licensed Windows
  user context, using no pytest cache; JUnit output at
  results/preflight_windows_2026_10_28/pytest.xml.

Subsequent bounded baseline work is recorded in `reports/analysis_log.md` and
the `_final` Phase 2 result directories. The full Phase 1 source-to-equation
and advanced-proof audit remains open. Keep published results, synthetic
tests, and theorem checks in separate evidence classes.
