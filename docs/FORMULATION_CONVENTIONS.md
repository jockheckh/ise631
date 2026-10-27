# Mathematical conventions to fix in Phase 1

Do not substitute this checklist for actual Adelman equations. Write down from source and derivation:
- Whether horizon is indexed forward (t=1..T) or backward, terminal condition, discount factor if any.
- State s=(remaining resource capacities,time); capacity dimension, product incidence matrix, request arrival distributions, admissible accept/reject decisions.
- LP objectives, inequality orientations, RHS signs, nonnegativity/free variables, quantifiers over states/actions/time.
- Relationship between Bellman super-solutions and valid upper bounds, and if/how the approximate affine representation contains or dominates the fluid bound.
- Difference between fluid LP dual multipliers, marginal differences of a time-dependent affine value function, and dynamically re-solved bid prices.
- Derivation of a separation oracle for violated ALP inequalities and, if taking a dual, the equivalent reduced-cost pricing problem; don't conflate the two.
- Exactly where simplex basis/reduced costs, complementary slackness and primal-dual gap checks apply to the selected source formulation.
- Whether affine coefficients are time-only or capacity-dependent; reconcile any tension between prompt description and paper mathematics with citations.

**Proof ledger convention:** Each item has `statement`, `hypotheses`, `source page/equation`, `formal steps`, `independent check`, `known limitation`, `status`. A test can reject a theorem implementation; it cannot alone establish a universal theorem.
