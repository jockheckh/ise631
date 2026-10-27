# Copy/paste prompts for Codex CLI (one phase at a time)

## 0. Start here: read-only orientation and diagnosis
"Read AGENTS.md, PLANS.md, RESEARCH_QUESTIONS.md, requirements.csv, DECISIONS.md, and sources/ index. Run read-only preflight (python scripts/preflight.py) and python scripts/audit_coverage.py. Identify source availability, Gurobi license usability, mathematical unknowns, and missing instructor coverage. Return a Phase 0 plan with evidence paths and blocker list. Do not fabricate Adelman page/equation citations. Do not begin simulations or surveillance pricing."

## 1. Source ledger and verification of core models
"Execute Phase 1 only. Read the full Adelman paper and all appendices under sources/adelman, then the instructor prompt. Extract a model/equation/assumption/results ledger with page references; trace each to RQ1–RQ5 and I01–I14. Separately derive the generic discounted occupancy primal/dual and Adelman's finite-horizon RM formulation. Ask theory_auditor to independently check signs, hypotheses, bounds, proof and whether bid prices depend on inventory. Distinguish source findings from your deductions. Save a technical memo and findings; stop at the Phase 1 gate."

## 2. Exact DP oracle + first Gurobi benchmarks
"Execute Phase 2 only. Source equations must already pass Phase 1. Write a tiny finite-horizon exact DP and independent exhaustive enumeration and compare them on hand-checkable cases. Build Gurobi deterministic/fluid primal and dual, then static bid-price policy. Add pytest tests and save one run manifest and solver metadata. Request independent_reviewer to attempt falsification. No ALP implementation until exact oracle and baseline checks pass."

## 3. Implement and check approximate LP
"Execute Phase 3 only. Implement source-faithful Adelman ALP, pricing/separation subproblem and dynamic bid-price rule, citing the exact source equations. Before writing code explain whether the method generates violated rows or new columns and why. Validate against tiny exact DP, dual residuals and exhaustive separation. Use Gurobi with logged status/tolerances. Ask independent_reviewer for adversarial checks. Separate paper-table replication from new synthetic experiments. Stop at phase gate."

## 4. Comparative experiments and scalability
"Execute Phase 4 only using EXPERIMENT_SPEC.md. Preregister factor levels and comparators before runs. Use paired common random numbers across policies; report 95% paired CIs, theoretical upper bounds, exact DP where possible, and calibration settings. Measure runtime and constraint/column growth vs resources, capacities, products, horizon. Test truncation and distinguish certified correctness from approximate empirical agreement. Retain raw trial-level results, manifest and reviewer report."

## 5. Instructor requirement audit + final analytical handoff
"Execute Phase 5 only. Re-read the instructor prompt literally and map all I01–I14 to checkable artifacts and reviewer assessments; identify anything not answered or only inferred. Produce reports/FINAL_ANALYTICAL_HANDOFF.md with sourced theory, verified claims, gap comparison tables, reproducibility commands, critique and unresolved items. Use independent_reviewer. Do not generate slides and do not initiate surveillance pricing."

## 6. Optional surveillance-pricing extension
"Run python scripts/check_extension_gate.py first. If it fails STOP. If it passes, execute Phase 6 starting only with a theoretical state/action/reward/resource/arrival mapping and demand/data feasibility memo; do not pull personal data or assume surveillance price discrimination is a standard network RM problem. Seek human approval for any dataset acquisition or any model-fitting expansion."

## Universal skeptical review
"Have theory_auditor and independent_reviewer independently attempt to falsify the selected proof or numerical result. Require explicit counterexample search, source references, bound-sign audit, marginal value check, tiny-case recalculation and execution evidence. Return unresolved blockers even if implementation tests pass."
