# Phase 1 theorem ledger and independent-audit record

Date: 2026-10-28. Scope: source-to-code readiness for the exact and fluid
baseline. This record does **not** mark numerical results or all project
claims verified.

Primary source: Adelman (2007), *Dynamic Bid Prices in Revenue Management*,
Operations Research 55(4):647-661, local PDF in sources/adelman. The
instructor's discounted generic MDP LP remains a separate formulation.

| Item | Source | Audit disposition / implementation gate |
|---|---|---|
| Instructor generic discounted-MDP occupancy LP | Instructor prompt p. 1 | Distinct from Adelman's finite-horizon model. A complete independently checked primal-dual derivation is still PENDING; no claim that the full Phase 1 exit or I01 is verified. |
| Exact finite-horizon Bellman and D0 | (1)-(3), pp. 648-649 | States, period-1 state set, no-arrival term, terminal convention, and signs independently checked; ready for toy DP/LP implementation. |
| Fluid primal and dual | (4)-(6), p. 650 | Capacity and demand constraints and nonnegative dual signs independently checked; ready for Gurobi baseline. |
| Affine D1/P1 | (14)-(21), p. 652 | Free coefficients, mass and moment equations, and next-period bid-price index independently checked; implementation deferred to Phase 3 after baseline tests. |
| Bound dominance, Theorem 1 | (22)-(24), p. 653 | Aggregation proof reconstructed. Initial draft erroneously omitted terminal-period consumption; independent audit caught it, and the corrected residual is in PHASE1_SOURCE_TO_CODE_SPEC.md. |
| Feasible restricted start, Proposition 2 | p. 651 | No-acceptance columns at state c in every period verified as a feasible starting solution; needed in Phase 3. |
| Pricing and Proposition 3 | p. 651; (33)-(36), pp. 655-656 | Reduced-profit signs and mass-balance certificate independently checked. A derivation is recorded in PHASE1_SOURCE_TO_CODE_SPEC.md. Pricing MIP and certificate implementation deferred to Phase 3. |
| Price monotonicity, Lemma 1 / Theorem 2 | (25)-(29), pp. 653-655 | Statement, positive-capacity/positive-arrival assumptions, and existence (not every optimum) checked. Full feasibility-preserving transformation proof is not yet reconstructed independently; monotonicity constraints are BLOCKED until that audit is complete. |
| Pricing complexity | (33)-(36), pp. 655-656 | Paper states integer-program formulation and reports empirical tractability. No general complexity class has been source-proved; complexity classification is BLOCKED pending independent derivation. |

Read-only specialist reviewers: theory_audit checked the displayed equations
against the 2007 PDF and found the terminal-residual error, missing
time-specific state quantifiers, and domain details; these were corrected.
independent_review checked the same specification and confirmed no remaining
sign/indexing/bound blocker for Phase 2 exact/fluid baseline work. Both noted
that advanced Theorem 2 proof and pricing-complexity work remain open.
Their reviews did not run solver models or certify any project result.

Phase decision: authorize a **bounded Phase 2 baseline implementation
exception**, not a claim that all Phase 1 requirements are complete. The
source-to-code equations required for that bounded work are audited. Theorem 2
and pricing-complexity questions are explicitly blocked from being used as
algorithmic assumptions or briefing claims until their separate audit is
completed; Phase 3 cannot claim their guarantees on the basis of this memo.

First Phase 2 code objective: reproduce Example 1 (exact DP 0.75, fluid LP
1.00), test independent exact LP/occupancy equality, verify fluid duality and
policy feasibility, and save Gurobi statuses/residuals. Exit when tiny and
edge-case tests pass and an independent reviewer audits at least two cases.
