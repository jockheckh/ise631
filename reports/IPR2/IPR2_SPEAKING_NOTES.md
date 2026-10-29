# ISE 631 IPR 2 speaking and study notes

Companion to the revised Beamer decision brief. This is a source-based analytical draft. Project numerical verification is planned; no project DP, LP, policy, column-generation, or simulation result is claimed complete. “Drafted” describes a presentation artifact, not a verified requirement.

Sources: Daniel Adelman, *Dynamic Bid Prices in Revenue Management*, *Operations Research* 55(4):647–661 (2007), in sources/adelman; ISE 631 instructor prompt in sources. Paper page numbers below are the printed journal pages.

## Meeting map

| Time | Main slides | Purpose |
|---|---|---|
| 0–4 min | 1–3 | Purpose, final-section crosswalk, IPR roadmap |
| 4–6 min | 4 | Questions and current progress |
| 6–18 min | 5–8 | Model, LPs, approximation, bound proof |
| 18–22 min | 9 | Published example and verification gate |
| 22–27 min | 10 | Column generation |
| 27–33 min | 11 | Experiment design |
| 33–35 min | 12 | Critical appraisal |
| 35–37 min | 13 | Application limits |
| 37–40 min | 14 | Decisions and IPR 3 gates |

Keep full LP derivations in the backup slides. During the meeting, prioritize the direction of the bounds and the next-period index in the bid-price rule. Every slide now carries a small header and a footer with the project name, presenter, and page number. Slides containing mathematical formulations include an on-slide variable key.

## Slide 1: IPR 2 purpose, agenda, and decisions

This slide follows the structure of the IPR 1 decision brief's opening page: purpose, requested decisions, today's agenda, and desired end state. Each requested decision points to its discussion slide: proof depth on 8, computation scope on 10, replication target on 11, and conceptual application on 13. Those slides mark their decision prompts with a colored star. Say explicitly that IPR 2 seeks approval of the mathematical interpretation and the *plan* for numerical evidence. The brief does not claim an executed DP, LP, or policy comparison. The optional application remains gated, as the user affirmed.

## Slide 2: Final-presentation crosswalk

Read the four columns as section, deliverable, status, and next action. Every table row has a horizontal rule. The color key means red = blocked by a project gate, yellow = draft material awaiting review, amber = not started, and green = complete with reviewed evidence. No crosswalk row is green yet. The literature review is not started as a source-verified project artifact; the separate synthetic extension is blocked by the gate. The IDs beside sections map all instructor requirements I01–I14. They do not mean the requirements are verified. The formal requirement register currently labels every ID planned and has blank evidence and reviewer fields. This is more conservative than the user-provided example, which called code and numerical results “started.” There is no project DP/LP/ALP implementation or simulation result on file, so the revised crosswalk marks those results “not started.” The slide compresses several requirements into section groups; backup slides A10–A11 and the full table below provide the row-level view.

| ID | Final section | Required evidence | Formal status | Next action |
|---|---|---|---|---|
| I01 | 2–4 | Discounted MDP Bellman LP, occupancy dual, flow, complementary slackness | Planned | Complete and independently audit derivation |
| I02 | 2 | Network MDP, time/capacity states, intractability | Planned | Finalize model and state-growth analysis |
| I03 | 2–3 | Fluid LP, static bid prices, limitations | Planned | Verify primal/dual and policy on toy case |
| I04 | 3–5 | Affine ALP, dynamic bids, large constraint family, algorithm | Planned | Audit source equations and test full tiny LP |
| I05 | 3 | Paper methodology and solution approach | Planned | File source-linked theory memo |
| I06 | 3–5 | LP course topics and correct bid-price computation | Planned | Verify duality, signs, and reduced costs |
| I07 | 4 | Principal theorem and proof technique | Planned | File independent proof review |
| I08 | 6 | Synthetic tests of fluid, static, dynamic policies | Planned | Implement after preflight and save raw results |
| I09 | 3–4 | Benefit and cost of affine approximation | Planned | Add independently verified example |
| I10 | 4 | ALP bound dominates fluid bound | Planned | Audit both inequality arguments |
| I11 | 5 | Pricing/separation difficulty and rationale | Planned | Verify formulation and qualify complexity claim |
| I12 | 6 | Dynamic policy, exact optimum, fluid gaps | Planned | Run controlled, paired comparisons |
| I13 | 7 | Reviewer critique and alternatives | Planned | Tie each critique to model or empirical evidence |
| I14 | 1, 5, 8 | Independent research questions | Planned | Link approved RQs to reviewed final analysis |

The six research questions have been approved as questions, but I14 itself has not yet been marked reviewed. Ask the professor whether the section emphasis covers the course prompt, especially I01's generic discounted occupancy LP, which is distinct from Adelman's undiscounted finite-horizon model.

## Slide 3: Roadmap

The roadmap now uses bullets inside each IPR column. IPR 1 approved the organizing questions and verification plan. IPR 2 establishes source-linked theory and requests approval of numerical design. IPR 3 should show reviewed computational evidence: an exact small oracle, fluid and affine bounds, policy comparisons, column-generation certificate, and scaling/truncation effects. The final brief synthesizes these and adds an evidence-based critique. The current-gate sentence is deliberately short so its line break stays readable. Do not present the IPR 1 roadmap's “initial code/results” aspiration as an accomplished IPR 2 result. Windows Python/Gurobi preflight remains a later gate, as the user directed.

## Slide 4: Scope and progress

Questions 1–3 establish the theory: what the affine approximation changes, why its bound improves on the fluid bound, and how duality and column generation work. Questions 4–5 ask whether those changes improve policy revenue and computational performance. Question 6 asks whether the allocation mechanism could transfer to surveillance missions.

The paper and instructor prompt are available. The central equations have been checked against the paper, but a formal project audit artifact has not been filed. Implementations and experiments remain planned. The paper's printed Appendix appears on pp. 660–661; no data or seed package for its numerical tables has been identified. PLANS.md places the exact oracle and fluid/static baseline in Phase 2, and the source-faithful affine algorithm in Phase 3.

Suggested opening: “I can defend the model and principal bound. Today I am asking you to approve the numerical verification and experiment design, with project solver results still to come.”

## Slide 5: Model and assumptions

There are \(m\) resources, \(n\) request classes, and periods \(t=1,\ldots,T\). Initial integer capacity is \(c=(c_1,\ldots,c_m)\), and \(r_i\) is capacity available at the start of a period. Class \(j\) earns \(f_j>0\) and uses the nonnegative integer resource vector \(A_j=(a_{1j},\ldots,a_{mj})^\top\). In period \(t\), class \(j\) arrives with probability \(p_{tj}\); no arrival has probability \(p_{t0}=1-\sum_jp_{tj}\ge0\). At most one request arrives each period. Capacity does not replenish. See Adelman pp. 648–649, §2.1.

Adelman's action \(u=(u_1,\ldots,u_n)\) is a prearrival decision: \(u_j=1\) means “accept class \(j\) if it arrives.” Its feasible set is

\[
\mathcal U(r)=\{u\in\{0,1\}^n:a_{ij}u_j\le r_i\ \text{for every }i,j\}.
\]

Individual feasibility follows from the one-arrival assumption. A simultaneous-arrival model needs different constraints. Under \(u\), expected immediate reward is \(q_t(r,u)=\sum_jp_{tj}f_ju_j\). If accepted class \(j\) arrives, the next state is \(r-A_j\); rejection or no arrival leaves \(r\) unchanged.

The left sketch starts at \((t,r)\). If class \(j\) arrives, acceptance earns \(f_j\) and moves to \((t+1,r-A_j)\); rejection moves to \((t+1,r)\) with no immediate reward. No arrival also leaves capacity unchanged. The right half restates Adelman's equation (2), p. 649:

\[
u^*_{tj}(r)=1\quad\Longleftrightarrow\quad
r\ge A_j\quad\text{and}\quad
f_j-\left[v_{t+1}(r)-v_{t+1}(r-A_j)\right]\ge0.
\]

Say it aloud: “Accept only if today’s fare covers the future value of the capacity consumed.” Equivalently, \(f_j+v_{t+1}(r-A_j)\ge v_{t+1}(r)\). The \(t+1\) index matters because the accepted request changes next period's state. The variable key at the bottom makes this slide usable without assuming an earlier slide.

## Slide 6: Exact Bellman recursion and LP

Set \(v_{T+1}(r)=0\). Conditional on the period's arrival,

\[
v_t(r)=\max_{u\in\mathcal U(r)}
\left\{\sum_jp_{tj}[f_ju_j+v_{t+1}(r-A_ju_j)]
+p_{t0}v_{t+1}(r)\right\}.
\]

For a feasible class \(j\), compare acceptance value \(f_j+v_{t+1}(r-A_j)\) with rejection value \(v_{t+1}(r)\). At a tie, Adelman's basic rule accepts:

\[
f_j\ge v_{t+1}(r)-v_{t+1}(r-A_j).
\]

This gives the max-positive-part recursion on Slide 6. The indicator there prevents evaluating a negative-capacity next state. In Adelman's full-state formulation, state count is \(1+(T-1)\prod_i(c_i+1)\), including potentially unreachable states. It grows exponentially in the number of resources when capacities remain above zero. A prearrival state can have as many as \(2^n\) feasible action vectors.

The exact Bellman LP (D0), Adelman p. 649 equation (3), minimizes \(v_1(c)\) over free value variables subject to

\[
v_t(r)-\mathbb E[v_{t+1}(R_{t+1})\mid r,u]\ge q_t(r,u)
\quad\text{for every }t,r,u\in\mathcal U(r).
\]

Why does it work? Every feasible value function is a Bellman supersolution. At the terminal period it exceeds the best final reward; backward induction then puts it above the optimal value at every earlier time. The true optimal value function is feasible and attains the minimum.

The exact occupancy dual is an independent derivation from D0. With \(x_t(r,u)\ge0\), it maximizes \(\sum_{t,r,u}q_t(r,u)x_t(r,u)\) subject to

\[
\sum_u x_1(c,u)=1,\qquad
\sum_u x_t(r,u)=\sum_{s,u}P_{t-1}(r\mid s,u)x_{t-1}(s,u)
\quad(t=2,\ldots,T).
\]

These equalities conserve probability at each state and period. Strong duality gives the exact initial value. Complementary slackness says positive occupancy can occur only at a tight Bellman inequality. That identifies optimal actions on occupied states, but does not give a unique choice at irrelevant states. Adelman does not print or label this exact dual “P0.”

### Separate course formulation: generic discounted MDP

The instructor prompt p. 1 gives a generic discounted LP. For finite states, \(0\le\gamma<1\), and nonnegative starting weights \(\nu\), its primal is

\[
\min_{V\text{ free}}\sum_s\nu(s)V(s)
\quad\text{s.t.}\quad
V(s)-\gamma\sum_{s'}P(s'\mid s,a)V(s')\ge r(s,a)\quad\forall(s,a).
\]

Multiplying each inequality by \(x(s,a)\ge0\) and collecting the coefficient of each free \(V(s)\) yields the dual equation

\[
\sum_a x(s,a)-\gamma\sum_{s',a'}P(s\mid s',a')x(s',a')=\nu(s).
\]

Here \(x\) counts \(\nu\)-weighted discounted visits. If \(\nu\) is a probability distribution, total occupancy is \(1/(1-\gamma)\). Full support of \(\nu\) makes an optimal primal vector equal to \(V^*\) everywhere; without it, irrelevant states can remain loose. Adelman's finite-horizon model instead has time-indexed, undiscounted flow.

## Slide 7: Fluid prices and affine prices

Let \(d_j=\sum_tp_{tj}\). The fluid LP is

\[
z^{LP}=\max_{Y\ge0}\sum_jf_jY_j
\quad\text{s.t.}\quad AY\le c,\quad Y_j\le d_j\ \forall j.
\]

Its dual is

\[
\min_{\lambda,\mu\ge0}c^\top\lambda+d^\top\mu
\quad\text{s.t.}\quad A_j^\top\lambda+\mu_j\ge f_j\ \forall j.
\]

The resource multipliers \(\lambda_i\) are local capacity shadow prices of this LP. The associated online rule accepts a feasible request when \(f_j\ge A_j^\top\lambda\). Complementary slackness describes the LP optimum; it does not prove that this online rule is optimal. Re-solving the fluid LP later may update \(\lambda\), but that is a separate optimization.

Adelman's affine approximation (p. 652, equation (14)) is

\[
\hat v_t(r)=\theta_t+b_t^\top r,\qquad
\theta_{T+1}=0,\quad b_{T+1}=0.
\]

Because \(\mathbb E[R_{t+1}\mid r,u]=r-\sum_jp_{tj}A_ju_j\),

\[
\mathbb E[\hat v_{t+1}(R_{t+1})\mid r,u]
=\theta_{t+1}+b_{t+1}^\top r-\sum_jp_{tj}b_{t+1}^\top A_ju_j.
\]

Substitute this into D0 and collect terms to obtain D1 (equation (17)):

\[
\theta_t-\theta_{t+1}+(b_t-b_{t+1})^\top r
\ge\sum_jp_{tj}(f_j-b_{t+1}^\top A_j)u_j
\quad\forall(t,r,u).
\]

The objective is \(\min\theta_1+b_1^\top c\). Raw D1 coefficients are unrestricted real variables. The affine opportunity cost is

\[
\hat v_{t+1}(r)-\hat v_{t+1}(r-A_j)=b_{t+1}^\top A_j.
\]

The intercept cancels, and the index is \(t+1\). A fixed affine solve gives a time trajectory of prices, not a price directly dependent on remaining inventory. Inventory still determines feasibility. Re-solving from a new capacity state can change the trajectory.

## Slide 8: Bound proof and monotone prices

Theorem 1 (p. 653) is \(z^{LP}\ge z^{P1}\ge v_1(c)\). Smaller valid upper bounds are stronger.

For the second inequality, D1 searches only affine functions while retaining every D0 Bellman inequality. Proposition 1 proves every feasible D0 function exceeds the true value. Strong duality between D1 and P1 gives \(z^{P1}=z^{D1}\ge v_1(c)\).

For the first inequality, P1 has weights \(X_t(r,u)\ge0\), unit total mass in every period, and balance of expected resource coordinates (p. 652, equations (18)–(21)). Define

\[
Y_j=\sum_{t,r,u}p_{tj}u_jX_t(r,u).
\]

Mass conservation and \(u_j\le1\) imply \(Y_j\le d_j\). Summing the resource-moment equations across periods makes initial capacity equal expected consumption through \(T-1\) plus expected capacity at \(T\). At \(T\), feasibility and \(\sum_jp_{Tj}\le1\) imply \(r_i\ge\sum_jp_{Tj}a_{ij}u_j\). Therefore \(c_i\ge\sum_ja_{ij}Y_j\). The P1 objective equals \(\sum_jf_jY_j\), so each P1 solution maps to a fluid-feasible solution of equal value. The fluid maximum is at least P1's maximum.

P1's \(X\) does not necessarily represent a realizable policy. Suppose one resource starts with two units and a two-unit class is accepted if it arrives with probability \(1/2\). True next capacity is 0 or 2, each with probability \(1/2\). P1 preserves only mean capacity 1, and may put all period-2 weight on state 1. State 1 cannot actually follow the stated period-1 action. This is the difference between moment flow and exact statewise flow.

Theorem 2 (pp. 654–655, equations (25)–(29)) assumes \(c_i>0\) and \(p_{tj}>0\) for every \(i,t,j\). Under those assumptions, an optimal D1 solution can be selected with \(b_{t,i}\ge b_{t+1,i}\ge0\) and \(\theta_t\ge\theta_{t+1}\ge0\). Its proof uses first resource use in positive P1 support, complementary slackness, feasible-state comparisons, and dual changes that preserve optimality. The first-use index belongs to the LP support, not to observed use by an implementable policy.

“An optimum exists” matters. In Example 1, \((\theta_2,b_2)=(0,0.5)\) and \((\theta_1,b_1)=(0.75,0)\) is an optimal D1 solution with objective 0.75 but \(b_1<b_2\). A monotone optimum is \((\theta_2,b_2)=(0,0.5)\), \((\theta_1,b_1)=(0,0.75)\). Zero demand or zero capacity is outside the theorem's stated hypotheses.

## Slide 9: Hand example and verification plan

Adelman's Example 1 (p. 653) has one resource, capacity 1, one class with revenue and resource use 1, two periods, and arrival probability 0.5 in each period. At period 2 with a seat left, \(v_2(1)=0.5\). At period 1, an arrival earns 1. If no customer arrives, the period-2 chance remains:

\[
v_1(1)=0.5(1)+0.5(0.5)=0.75.
\]

The fluid LP sees total expected demand 1 and allows \(Y=1\), giving 1. Every function on the two states \(r\in\{0,1\}\) can be represented by an affine intercept and slope, so full D1/P1 is exact and gives 0.75. There is a 25% chance no customer arrives in either period; the fluid total hides that path.

Evidence language: 0.75/0.75/1.00 is a published analytical example and a hand calculation. It is not a project solver result. Later verification should compare independent backward DP, exact Bellman LP, exact occupancy dual, fluid LP, and fully enumerated D1/P1. Then test a two-resource, three-class network and boundary cases. Record objective differences, feasibility residuals, solver statuses, and policy capacity checks. A solver's “optimal” status does not reveal a formulation coded incorrectly.

## Slide 10: Column generation and reduced costs

D1 has \(T(m+1)\) value coefficients yet retains a constraint for every time, state, and feasible action. P1 has the corresponding state-action columns and relatively few moment equations. Adelman therefore performs column generation on P1 (pp. 655–657). The no-acceptance columns \((t,c,0)\) are feasible starting columns (Proposition 2, p. 651).

After solving the restricted primary, use its dual values \(\theta_t,b_t\). The deck uses “primary” as requested; the standard column-generation term in the literature is “restricted master.” The P1 model is the dual of the affine value-function LP D1. The reduced profit of a candidate column is

\[
\rho_t(r,u)=\sum_jp_{tj}(f_j-b_{t+1}^\top A_j)u_j
-(b_t-b_{t+1})^\top r-\theta_t+\theta_{t+1}.
\]

For a maximization primary, a positive reduced profit can improve its objective. Maximizing \(\rho_t\) over feasible \(r,u\) is both a search for a P1 column and separation of D1 inequalities. Adelman writes the period problem as an integer program in equations (33)–(36), p. 656; Figure 2 adds a batch with up to one best column per period.

A hand-checkable first iteration uses Example 1. The no-acceptance primary has value zero and admits dual values \(\theta=b=0\). At period 2, state \(r=1\), action \(u=1\), the omitted column has reduced profit \(p_2f=0.5\). Add that column and re-solve: keep the no-acceptance period-1 column, put all period-2 mass on the new accept column, and earn 0.5. The restricted objective rises from zero to 0.5. Further pricing is still needed to reach the full P1 value 0.75; this hand calculation illustrates one iteration, not a computational run.

Let \(Z_\Lambda\) be the restricted-primary value and \(\rho_t^*=\max_{r,u}\rho_t(r,u)\) the globally valid period maximum. Proposition 3 proves

\[
Z_\Lambda\le z^{P1}\le Z_\Lambda+\sum_t\rho_t^*.
\]

To see why, multiply each P1 moment equality by its restricted-primary dual value and sum. “Full objective minus dual objective” becomes the sum of reduced profits weighted by \(X\). The constant basis makes each period's \(X\)-mass equal one, so the sum is at most \(\sum_t\rho_t^*\). Restricted-primary strong duality replaces the dual objective by \(Z_\Lambda\). When \(Z_\Lambda>0\), \(\sum_t\rho_t^*/Z_\Lambda\le\varepsilon\) suffices for a relative tolerance. Use an absolute tolerance in zero-objective cases. A computational certificate needs global pricing maxima or valid upper bounds on them, and numerical feasibility checks.

\(Z_\Lambda\) is a lower bound on the full P1 optimum. It is neither an implementable policy's expected reward nor automatically an upper bound on the exact MDP. Adelman explicitly says the Table 5 P1 figures computed at 5% stopping tolerance “do not strictly give an upper bound” (p. 658).

The article reports an integer pricing formulation and empirical CPLEX success, but no NP-hardness theorem. A separate derivation suggests this precise pricing problem reduces to maximum-weight closure and minimum cut. For fixed \(t>1\), set \(w_j=p_{tj}(f_j-b_{t+1}^\top A_j)\) and \(d_i=b_{t,i}-b_{t+1,i}\). If \(d_i>0\), an optimal \(r_i\) is the maximum \(a_{ij}\) among selected classes; if \(d_i<0\), it is \(c_i\). Product nodes of weight \(w_j\) can require resource-threshold nodes whose negative weights price the needed capacity. Distinct-level compression yields at most \(O(mn)\) threshold nodes. This is an independently derived, unimplemented observation. Keep it out of the main claims until its formal proof and exhaustive small-case comparisons are saved. It relies on Adelman's individual inequalities \(a_{ij}u_j\le r_i\); simultaneous-request constraints change the structure.

## Slide 11: Experiment design and statistical interpretation

The bound ordering is a theorem under the model assumptions. Its *magnitude* is an empirical outcome. Dynamic-policy improvement is also empirical: a stronger upper bound does not imply that the induced online policy earns more.

Begin with hand-verifiable cases. Then vary number of resources and classes, horizon, capacity-to-demand load, fare spread, arrival timing, and one-resource versus multi-resource products. Record each instance's \(m,n,T,c,A,f,p\). The number of training rows or simulation trials is not state-space size. Full noninitial state count is \(\prod_i(c_i+1)\); P1 column count also reflects feasible actions.

Compare policies with declared solve schedules. “BPC fixed” solves the fluid LP once; “DBPC fixed” solves the affine LP once. Re-solving versions repeat their corresponding optimization at stated epochs. Adelman's published policy comparisons on pp. 658–659 also use a one-period lookahead refinement for DBPC and report an improvement when that DBPC variant rejects ties with a strict \(>\) rule. The paper uses five evenly spaced re-solves by default and 100 shared arrival paths. Implementing basic equation (15) is valuable verification, but it is not exact replication of those table values.

For tiny cases, compute policy expectation exactly where practical. For simulation, give every competing policy the same exogenous arrival sequence in replication \(k\). Report each policy's mean reward and 95% confidence interval. Let \(D_k=R_{k,\mathrm{dynamic}}-R_{k,\mathrm{static}}\). Report \(\bar D\), its sample standard deviation \(s_D\), and a 95% paired interval such as \(\bar D\pm t_{0.975,N-1}s_D/\sqrt N\). The paper's separate policy standard errors do not reveal uncertainty in a paired difference. Declare a pilot sample and precision rule before inspecting the main results; separate the pilot from the final sample if its variance determines \(N\).

When exact \(V^*>0\), useful ratios include \((z^{LP}-V^*)/V^*\), \((z^{P1}-V^*)/V^*\), and policy regret \((V^*-J(\pi))/V^*\). If \(V^*=0\), these ratios are undefined; report absolute differences. The true expected reward of any feasible policy cannot exceed \(V^*\), but a finite Monte Carlo mean may do so by sampling error. A confidence interval expresses uncertainty; it is not a deterministic lower-bound proof.

Separate three truncation operations: restricting primary columns while still pricing all omitted columns; dropping states; shortening the horizon. The first can retain Proposition 3's certificate. The latter two may change the model and lose the original guarantee. Exhaustively check omitted Bellman constraints on tiny cases and use held-out checks on larger cases. Record runtime, memory when measurable, iteration count, generated columns, pricing gaps, and solver residuals alongside reward outcomes.

## Slide 12: Critical appraisal

This slide should sound like a reviewer rather than a sales pitch. Adelman's main theorem answers a bound-comparison question under a finite-horizon arrival model. It does not prove policy superiority, solver scalability on arbitrary instances, or robustness to probability misspecification. The fixed affine price path changes with time but not directly with remaining inventory. Re-solving creates some inventory responsiveness, at computational cost. Keep assumptions and empirical limitations separate. For each criticism in the final brief, cite either a source assumption, a published-table limitation, or a project sensitivity result. Candidate stronger benchmarks include exact DP on tiny networks and a carefully defined re-solving or lookahead policy on moderate networks. Do not call an untested alternative superior.

## Slide 13: Adelman and individualized pricing

The slide treats the research list supplied by the user as *reading leads*, not as independently verified citations. We have not checked the later papers' full texts, bibliographies, dates, or the FTC document. In the meeting, do not say that a paper “explicitly cites Adelman” unless its reference list has been inspected. The only source-checked part of the slide is Adelman's own resource-capacity model. Explain the key distinction first: \(b_{t+1}^{\top}A_j\) is an internal opportunity cost of using capacity. It is not necessarily a price quoted to a consumer and contains no customer-specific data in the original model.

| Reading lead supplied by user | Proposed role in the discussion | Verification needed |
|---|---|---|
| Acquisti and Varian (2005), *Conditioning Prices on Purchase History* | Earlier, parallel price-discrimination lineage | Confirm publication details and exact claims |
| Zhang and Adelman (2009), *An Approximate Dynamic Programming Approach to Network Revenue Management with Customer Choice* | Direct author/method extension toward customer choice | Inspect model and source relationship |
| Aydin and Ziya (2009), *Personalized Dynamic Pricing of Limited Inventories*, DOI 10.1287/opre.1090.0701 | Parallel limited-inventory personalization using customer signals | Check bibliography before claiming no Adelman citation |
| Jahandideh et al. (2020), *Individualized Pricing for a Cloud Provider Hosting Interactive Applications* | Claimed citation trail into individualized service pricing | Inspect paper and reference list |
| Ban and Keskin (2021), *Personalized Dynamic Pricing with Machine Learning: High-Dimensional Features and Heterogeneous Elasticity* | Parallel customer-feature learning line | Confirm methods, data, and historical framing |
| Lei et al. (2023, revised 2025), *Joint Optimization of Pricing and Personalized Recommendations in Online Retailing* | Claimed citation trail into recommendations | Check version, citations, and uniform-price qualification |
| Barz et al. (2023), *Discrete Dynamic Pricing and Application of Network Revenue Management for FlixBus* | Related commercial revenue-management application | Check treatment of Adelman's ALP |
| Hausenblas et al. (2025), *Improving Network Dynamic Pricing Policies Through Offline Reinforcement Learning* | Claimed bridge to modern learning methods | Check bibliographic and methodological details |
| FTC January 2025 surveillance-pricing inquiry | Policy evidence about use of consumer data | Retrieve and verify the primary agency report before use |

An illustrative mathematical bridge for a single unit of inventory is

\[
p^*(z,t)\in\arg\max_{p\in\mathcal P}
\Pr(\text{purchase}\mid p,z)\,[p-\pi_t].
\]

Here \(z\) is a customer signal, \(p\) is an offered price, \(\mathcal P\) is the feasible price set, and \(\pi_t\) is a one-unit capacity opportunity cost such as Adelman's next-period slope \(b_{t+1}\). The expression combines a customer response model with a capacity opportunity cost. It is an *illustrative extension*, not an equation or result in Adelman (2007). Its use would require new assumptions about demand response, data quality, fairness, and the timing of offers. A citation trail supports an academic connection; it does not establish that Adelman created commercial surveillance-pricing systems.

The earlier mission-allocation analogy remains available if the professor asks about RQ6's resource-allocation side: class becomes mission type, fare becomes mission utility, and capacity becomes available assets. Reusable resources or simultaneous requests require a different transition model. The user has confirmed that application dataset search and implementation remain gated until mandatory requirements, independent review, and explicit later release. The starred decision asks whether a conceptual, source-checked connection suffices for the final brief.

## Slide 14: Decisions and next gates

This slide repeats the four colored-star decisions listed on slide 1, with their discussion-slide references. It no longer contains a separate “scope confirmation” row:

1. Slide 8: Is the theorem and LP treatment sufficient for the final brief?
2. Slide 10: How much pricing and column generation must IPR 3 implement?
3. Slide 11: Which published result and comparison protocol should IPR 3 target?
4. Slide 13: Is a conceptual, source-checked application connection sufficient?

The next technical sequence is source-linked proof memo and independent audit; exact DP and LP; fluid LP and static policy; full tiny D1/P1; pricing versus exhaustive search; then column generation, dynamic policy, and paired experiments. A later Windows preflight must test an actual solve under the account that will run the research.

## How the final 15-slide agenda should change

The nine-part order is sound: motivation leads into the stochastic allocation problem, then Adelman's formulation, proof, computation, empirical assessment, critique, and a carefully bounded application. The following changes make the allotted slides better match the instructor prompt and present evidence status:

1. **Slides 1–2, historical hook:** Define “surveillance pricing” precisely and source claims about prevalence, consumer/business effects, and history independently. Adelman (2007) supports the airline revenue-management connection, not a causal origin story for personalized pricing. If that sourcing is not ready, make slide 2 the research question and scope guardrail instead of a historical claim.
2. **Slides 3–8, theory:** Explicitly show the instructor's generic discounted Bellman/occupancy LP alongside Adelman's finite-horizon LP in a compact comparison, perhaps on slide 4 or in a clearly signposted appendix that you can present if asked. Slide 3 cannot carry both the full MDP and fluid LP in detail; reserve full quantifiers and proof algebra for backup slides. Keep the main theorem \(z^{LP}\ge z^{P1}\ge V^*\) separate from the policy relation \(J(\pi)\le V^*\). A sample mean is an estimate, not a mathematical lower bound.
3. **Slides 4–5, worked example:** Use a small hand-checkable capacity example to connect duality, complementary slackness, reduced profit, and the \(t+1\) bid-price index. A fluid shadow price and an affine bid price come from different LPs. Do not imply the fixed affine prices depend on current inventory except through feasibility or a re-solve.
4. **Slide 9, scaling:** State the pricing MIP and its constraints. Differentiate full enumeration, certified restricted-master column generation, state pruning, and horizon truncation. The paper supplies empirical runtime evidence, not a general complexity theorem. Any novel complexity reduction needs a saved proof and exhaustive tiny-case checks.
5. **Slides 10–11, experiment:** Give slide 10 to instance design, baselines, and preregistered metrics; reserve slide 11 for results only after verified runs. Include a simple feasible first-come baseline only if its tie and capacity rules are specified in advance. Separate fixed from re-solved policies and bare equation (15) from Adelman's published lookahead variant. Until runs exist, label slide 11 “planned output and validation gates,” without placeholder numbers or fabricated charts.
6. **Slides 13–14, extension:** Keep both slides conditional. One can present the conceptual capacity-opportunity-cost analogy and the missing historical/literature evidence. The other should present model-fit and ethics questions, not synthetic results, unless the mandatory course work and independent-review gate pass and the user later releases the application gate. If still gated near the final, reassign slide 14 to experiment sensitivity or the critical appraisal and use one extension slide.
7. **Slide 15, conclusion:** Draft the structure now but choose its three takeaways after the numerical study. Distinguish what Adelman proves, what his paper reports, and what this project verifies. Avoid a claim that the paper generated modern personalized-pricing systems.

The final deck is a target architecture, not the current IPR 2 deck. IPR 2 now has 14 main slides because it adds governance, crosswalk, and roadmap material before the theory discussion. Keep the meeting to 40 minutes by treating proof derivations and the full I01–I14 register as backup, while using the main crosswalk to demonstrate coverage.

## Six rapid answers to rehearse

1. **Why does the exact MDP admit an LP?** Bellman optimality is the smallest function satisfying every action-wise Bellman inequality. Finite states and actions make those inequalities linear; the dual conserves statewise probability.
2. **What changes with an affine value function?** One value variable per state becomes \(T(m+1)\) coefficients, while the Bellman inequalities remain. The dual preserves only the chosen basis moments.
3. **Why is the affine bound tighter than the fluid bound?** Any P1 solution aggregates to fluid-feasible expected acceptances with equal reward, so the fluid maximum is at least P1's maximum. D1 still bounds the exact MDP from above.
4. **Where do bid prices come from?** Fluid capacity duals yield static prices. Affine coefficients price resource-moment equations and give the next-period approximate opportunity cost in the acceptance rule.
5. **Why use column generation?** P1 has few balance equations but many columns. Pricing finds profitable omitted columns and gives a bound on their total possible effect.
6. **How do we separate bounds from policy value?** Bound strength follows from LP feasibility and duality. Policy reward must be computed exactly on small cases or estimated using paired trials and uncertainty.

## Evidence ledger for this draft

| Statement | Status | Evidence or next check |
|---|---|---|
| \(z^{LP}\ge z^{P1}\ge v_1(c)\) | Source-stated; derivation checked | Adelman p. 653, Theorem 1. Save a formal audit before marking the project claim verified. |
| A monotone optimal price trajectory exists | Source-stated under positive capacities and arrivals | Adelman pp. 654–655, Theorem 2. It is not a property of every optimum. |
| Example 1 gives 0.75, 0.75, 1.00 | Source-stated and hand derived | Adelman p. 653. Solver reproduction is pending. |
| Pricing reduces to minimum cut | Independently derived hypothesis | Formal proof and exhaustive toy tests pending; the paper itself does not state this. |
| Project policy gains, gaps, and scalability | Not measured | Approved implementation and experiments are pending. |

No claim or requirement status was changed in preparing these products. The brief supports a theory discussion and a reviewable verification plan while preserving the distinction between published evidence and project results.
