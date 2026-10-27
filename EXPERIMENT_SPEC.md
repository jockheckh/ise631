# Preregistration and replication plan — complete parameters before running experiments

Status: design, not executed or source-validated. Human researcher approves factor levels and minimum replication count before Phase 4.

## Comparators and estimands
- **Exact finite-horizon MDP value** from DP only for tractable state spaces; independent exhaustive enumeration for tiny validation.
- **Fluid LP objective**: candidate theoretical upper bound; validate direction and hypotheses from source.
- **Adelman ALP objective**: candidate stronger theoretical bound; validate formulation, dominance assumptions and direction, not solely sampled evidence.
- **Static bid-price policy** and **dynamic bid-price policy**: expected rewards estimated by properly coupled Monte Carlo. Don't call point estimates mathematical lower bounds.
- **Published results**: specific table/figure and exact instance definition, unavailable-data statement, replication tolerance; do not mislabel synthetic instances as published replication.

## Experimental factors (select specific levels before execution)
- Horizon and arrival rate; capacity/demand pressure; number of products/resources; network incidence structure; revenue spread; stochastic demand heterogeneity.
- Distinguish data fitting sample size from model structural scaling; keep random seeds and scenarios consistent across policies for paired comparisons.

## Outcomes and quality checks
- Objective values and admissible bound gaps with proven orientations; paired policy improvement, mean/SD/95% CI and n; Gurobi termination and primal/dual infeasibility; runtime, memory, cut/constraint/column counts.
- Truncation: full solve vs truncated solve; test omitted constraints on small exhaustive examples and held-out separation for larger examples; state clearly whether theoretical guarantees survive.
- Checks: terminal reward, zero demand, single resource/product, tight vs loose capacity, impossible action rejected, appropriate tie-breaking, reproducible solver results, numerical tolerance handling.

## Persistence
- One instance definition JSON, one run manifest JSON, one trial-level CSV or Parquet, and one interpretation markdown per experiment family. Never overwrite raw results.
- Use `python scripts/write_manifest.py --experiment <name> --seed <int> --output results/<run>/manifest.json` and supplement with model parameters and solver options in the experiment code.
