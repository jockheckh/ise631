# ISE 631 IPR 2 speaking and study notes

Companion to the Beamer brief. This is a source-based analytical draft. Project numerical verification is planned; no project DP, LP, policy, column-generation, or simulation result is claimed complete.

Sources: Daniel Adelman, *Dynamic Bid Prices in Revenue Management*, *Operations Research* 55(4):647–661 (2007), in sources/adelman; ISE 631 instructor prompt in sources. Paper page numbers below are the printed journal pages.

## Meeting map

| Time | Main slides | Purpose |
|---|---|---|
| 0–5 min | 1 | Questions and progress |
| 5–17 min | 2–5 | Model, LPs, approximation, bound proof |
| 17–25 min | 6 | Published example and verification gate |
| 25–30 min | 7 | Column generation |
| 30–37 min | 8 | Experiment design |
| 37–40 min | 9–10 | Application limits and decisions |

Keep full LP derivations in the backup slides. During the meeting, prioritize the direction of the bounds and the next-period index in the bid-price rule.

## Slide 1: Scope and progress

Questions 1–3 establish the theory: what the affine approximation changes, why its bound improves on the fluid bound, and how duality and column generation work. Questions 4–5 ask whether those changes improve policy revenue and computational performance. Question 6 asks whether the allocation mechanism could transfer to surveillance missions.

The paper and instructor prompt are available. The central equations have been checked against the paper, but a formal project audit artifact has not been filed. Implementations and experiments remain planned. The paper's printed Appendix appears on pp. 660–661; no data or seed package for its numerical tables has been identified. PLANS.md places the exact oracle and fluid/static baseline in Phase 2, and the source-faithful affine algorithm in Phase 3.

Suggested opening: “I can defend the model and principal bound. Today I am asking you to approve the numerical verification and experiment design, with project solver results still to come.”

## Slide 2: Model and assumptions

There are \(m\) resources, \(n\) request classes, and periods \(t=1,\ldots,T\). Initial integer capacity is \(c=(c_1,\ldots,c_m)\), and \(r_i\) is capacity available at the start of a period. Class \(j\) earns \(f_j>0\) and uses the nonnegative integer resource vector \(A_j=(a_{1j},\ldots,a_{mj})^\top\). In period \(t\), class \(j\) arrives with probability \(p_{tj}\); no arrival has probability \(p_{t0}=1-\sum_jp_{tj}\ge0\). At most one request arrives each period. Capacity does not replenish. See Adelman pp. 648–649, §2.1.

Adelman's action \(u=(u_1,\ldots,u_n)\) is a prearrival decision: \(u_j=1\) means “accept class \(j\) if it arrives.” Its feasible set is

\[
\mathcal U(r)=\{u\in\{0,1\}^n:a_{ij}u_j\le r_i\ \text{for every }i,j\}.
\]

Individual feasibility follows from the one-arrival assumption. A simultaneous-arrival model needs different constraints. Under \(u\), expected immediate reward is \(q_t(r,u)=\sum_jp_{tj}f_ju_j\). If accepted class \(j\) arrives, the next state is \(r-A_j\); rejection or no arrival leaves \(r\) unchanged.

Teaching intuition: an accepted request earns revenue now but uses capacity that might serve a more valuable future arrival.

## Slide 3: Exact Bellman recursion and LP

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

This gives the max-positive-part recursion on Slide 3. The indicator there prevents evaluating a negative-capacity next state. In Adelman's full-state formulation, state count is \(1+(T-1)\prod_i(c_i+1)\), including potentially unreachable states. It grows exponentially in the number of resources when capacities remain above zero. A prearrival state can have as many as \(2^n\) feasible action vectors.

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

## Slide 4: Fluid prices and affine prices

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

## Slide 5: Bound proof and monotone prices

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

## Slide 6: Hand example and verification plan

Adelman's Example 1 (p. 653) has one resource, capacity 1, one class with revenue and resource use 1, two periods, and arrival probability 0.5 in each period. At period 2 with a seat left, \(v_2(1)=0.5\). At period 1, an arrival earns 1. If no customer arrives, the period-2 chance remains:

\[
v_1(1)=0.5(1)+0.5(0.5)=0.75.
\]

The fluid LP sees total expected demand 1 and allows \(Y=1\), giving 1. Every function on the two states \(r\in\{0,1\}\) can be represented by an affine intercept and slope, so full D1/P1 is exact and gives 0.75. There is a 25% chance no customer arrives in either period; the fluid total hides that path.

Evidence language: 0.75/0.75/1.00 is a published analytical example and a hand calculation. It is not a project solver result. Later verification should compare independent backward DP, exact Bellman LP, exact occupancy dual, fluid LP, and fully enumerated D1/P1. Then test a two-resource, three-class network and boundary cases. Record objective differences, feasibility residuals, solver statuses, and policy capacity checks. A solver's “optimal” status does not reveal a formulation coded incorrectly.

## Slide 7: Column generation and reduced costs

D1 has \(T(m+1)\) value coefficients yet retains a constraint for every time, state, and feasible action. P1 has the corresponding state-action columns and relatively few moment equations. Adelman therefore performs column generation on P1 (pp. 655–657). The no-acceptance columns \((t,c,0)\) are feasible starting columns (Proposition 2, p. 651).

After solving the restricted master, use its dual values \(\theta_t,b_t\). The reduced profit of a candidate column is

\[
\rho_t(r,u)=\sum_jp_{tj}(f_j-b_{t+1}^\top A_j)u_j
-(b_t-b_{t+1})^\top r-\theta_t+\theta_{t+1}.
\]

For a maximization master, a positive reduced profit can improve its objective. Maximizing \(\rho_t\) over feasible \(r,u\) is both a search for a P1 column and separation of D1 inequalities. Adelman writes the period problem as an integer program in equations (33)–(36), p. 656; Figure 2 adds a batch with up to one best column per period.

A hand-checkable first iteration uses Example 1. The no-acceptance master has value zero and admits dual values \(\theta=b=0\). At period 2, state \(r=1\), action \(u=1\), the omitted column has reduced profit \(p_2f=0.5\). Add that column and re-solve: keep the no-acceptance period-1 column, put all period-2 mass on the new accept column, and earn 0.5. The restricted objective rises from zero to 0.5. Further pricing is still needed to reach the full P1 value 0.75; this hand calculation illustrates one iteration, not a computational run.

Let \(Z_\Lambda\) be the restricted-master value and \(\rho_t^*=\max_{r,u}\rho_t(r,u)\) the globally valid period maximum. Proposition 3 proves

\[
Z_\Lambda\le z^{P1}\le Z_\Lambda+\sum_t\rho_t^*.
\]

To see why, multiply each P1 moment equality by its restricted-master dual value and sum. “Full objective minus dual objective” becomes the sum of reduced profits weighted by \(X\). The constant basis makes each period's \(X\)-mass equal one, so the sum is at most \(\sum_t\rho_t^*\). Restricted-master strong duality replaces the dual objective by \(Z_\Lambda\). When \(Z_\Lambda>0\), \(\sum_t\rho_t^*/Z_\Lambda\le\varepsilon\) suffices for a relative tolerance. Use an absolute tolerance in zero-objective cases. A computational certificate needs global pricing maxima or valid upper bounds on them, and numerical feasibility checks.

\(Z_\Lambda\) is a lower bound on the full P1 optimum. It is neither an implementable policy's expected reward nor automatically an upper bound on the exact MDP. Adelman explicitly says the Table 5 P1 figures computed at 5% stopping tolerance “do not strictly give an upper bound” (p. 658).

The article reports an integer pricing formulation and empirical CPLEX success, but no NP-hardness theorem. A separate derivation suggests this precise pricing problem reduces to maximum-weight closure and minimum cut. For fixed \(t>1\), set \(w_j=p_{tj}(f_j-b_{t+1}^\top A_j)\) and \(d_i=b_{t,i}-b_{t+1,i}\). If \(d_i>0\), an optimal \(r_i\) is the maximum \(a_{ij}\) among selected classes; if \(d_i<0\), it is \(c_i\). Product nodes of weight \(w_j\) can require resource-threshold nodes whose negative weights price the needed capacity. Distinct-level compression yields at most \(O(mn)\) threshold nodes. This is an independently derived, unimplemented observation. Keep it out of the main claims until its formal proof and exhaustive small-case comparisons are saved. It relies on Adelman's individual inequalities \(a_{ij}u_j\le r_i\); simultaneous-request constraints change the structure.

## Slide 8: Experiment design and statistical interpretation

The bound ordering is a theorem under the model assumptions. Its *magnitude* is an empirical outcome. Dynamic-policy improvement is also empirical: a stronger upper bound does not imply that the induced online policy earns more.

Begin with hand-verifiable cases. Then vary number of resources and classes, horizon, capacity-to-demand load, fare spread, arrival timing, and one-resource versus multi-resource products. Record each instance's \(m,n,T,c,A,f,p\). The number of training rows or simulation trials is not state-space size. Full noninitial state count is \(\prod_i(c_i+1)\); P1 column count also reflects feasible actions.

Compare policies with declared solve schedules. “BPC fixed” solves the fluid LP once; “DBPC fixed” solves the affine LP once. Re-solving versions repeat their corresponding optimization at stated epochs. Adelman's published policy comparisons on pp. 658–659 also use a one-period lookahead refinement for DBPC and report an improvement when that DBPC variant rejects ties with a strict \(>\) rule. The paper uses five evenly spaced re-solves by default and 100 shared arrival paths. Implementing basic equation (15) is valuable verification, but it is not exact replication of those table values.

For tiny cases, compute policy expectation exactly where practical. For simulation, give every competing policy the same exogenous arrival sequence in replication \(k\). Report each policy's mean reward and 95% confidence interval. Let \(D_k=R_{k,\mathrm{dynamic}}-R_{k,\mathrm{static}}\). Report \(\bar D\), its sample standard deviation \(s_D\), and a 95% paired interval such as \(\bar D\pm t_{0.975,N-1}s_D/\sqrt N\). The paper's separate policy standard errors do not reveal uncertainty in a paired difference. Declare a pilot sample and precision rule before inspecting the main results; separate the pilot from the final sample if its variance determines \(N\).

When exact \(V^*>0\), useful ratios include \((z^{LP}-V^*)/V^*\), \((z^{P1}-V^*)/V^*\), and policy regret \((V^*-J(\pi))/V^*\). If \(V^*=0\), these ratios are undefined; report absolute differences. The true expected reward of any feasible policy cannot exceed \(V^*\), but a finite Monte Carlo mean may do so by sampling error. A confidence interval expresses uncertainty; it is not a deterministic lower-bound proof.

Separate three truncation operations: restricting master columns while still pricing all omitted columns; dropping states; shortening the horizon. The first can retain Proposition 3's certificate. The latter two may change the model and lose the original guarantee. Exhaustively check omitted Bellman constraints on tiny cases and use held-out checks on larger cases. Record runtime, memory when measurable, iteration count, generated columns, pricing gaps, and solver residuals alongside reward outcomes.

## Slide 9: Surveillance resource allocation

The defensible analogy is allocation of scarce resources. A class becomes a mission category; revenue becomes an explicit mission utility; capacity becomes available aircraft, sensors, or operator time. A bid price represents the opportunity cost of committing an asset. Calling this “surveillance pricing” can imply literal market pricing or price discrimination, neither of which follows from Adelman's model. Explain the meaning carefully.

Before transferring the formulation, ask whether resources are consumed irreversibly through the horizon, whether several missions can arrive together, whether mission utility is additive, and whether arrivals and rewards can be estimated credibly. Reusable assets or simultaneous requests require a modified MDP. IPR 2 only presents this conceptual mapping. Project governance requires verified mandatory work and separate human approval before surveillance data search or implementation.

## Slide 10: Decisions and next gates

Ask the professor three concrete questions:

1. Is a planned numerical verification gate acceptable at IPR 2, given that project solver evidence is still pending?
2. How much of full D1/P1, pricing, and column generation should be implemented by IPR 3?
3. Which published table or policy variant needs replication, and which proposed experiment factors and precision targets should be fixed?

Confirm that surveillance remains conceptual. The next technical sequence is source-linked proof memo and independent audit; exact DP and LP; fluid LP and static policy; full tiny D1/P1; pricing versus exhaustive search; then column generation, dynamic policy, and paired experiments. A later Windows preflight must test an actual solve under the account that will run the research.

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
