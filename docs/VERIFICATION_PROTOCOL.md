# Claim acceptance, numerical labels, and review

1. **Source-stated:** precisely quote/paraphrase with source filename, paper page and equation/result number if applicable; instructor questions are not automatically established paper theorems.
2. **Derived:** show every implication from formal assumptions and prove the relevant direction; record alternatives or counterexample search.
3. **Implemented:** test smallest possible exact oracle, dimensions and feasibility; record solver status, tolerances and reproducibility metadata.
4. **Estimated:** state estimand, sampling design, sample size, paired differences and uncertainty; separate Monte Carlo noise from optimization error.
5. **Reviewed:** an agent not responsible for development checks source, signs, code, and counterexamples; file an audit document. Tests can pass while science remains unsupported.

Status transitions: `unverified` → `in_progress` → `submitted_for_review` → `verified`; `blocked` for inaccessible source, unestablished hypothesis, failed proof, license issue or irreproducible datum. Never use `verified` as a synonym for 'generated'.

For comparison charts, label: fluid theoretical bound, ALP theoretical bound, exact DP optimum (where computed), static-policy estimated value ± CI, dynamic-policy estimated value ± CI. Check inequalities only when the assumptions and objectives are aligned.
