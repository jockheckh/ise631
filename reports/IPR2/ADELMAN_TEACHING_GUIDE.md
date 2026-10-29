# Teaching Adelman’s *Dynamic Bid Prices in Revenue Management*

A source-based instructor guide for ISE 631. This document is meant to let you teach the paper from first principles, derive its central claims at the board, and interpret its numerical evidence accurately.

**Primary source:** Daniel Adelman, “Dynamic Bid Prices in Revenue Management,” *Operations Research* 55(4):647–661 (2007), in the local source PDF at sources/adelman/EBSCO-FullText-10_26_2026.pdf. Citations below use the paper’s printed page numbers. The ISE 631 instructor prompt in sources/10_MDPs (1).pdf also asks for a generic discounted MDP LP; that formulation is treated separately in §5. Mathematical statements identified as *derived* are our own reconstructions, not claims that the paper prints them in that form. This guide does not report a project solver run or an independent replication of Adelman’s tables.

## 1. What students should be able to do

At the end of a class, students should be able to:

1. Define Adelman’s finite-horizon network revenue-management MDP, including its prearrival actions and transition probabilities.
2. Derive the Bellman acceptance test as an opportunity-cost comparison.
3. Turn the Bellman equations into an exact LP and explain the meaning of its occupancy dual.
4. Derive the fluid LP, its resource prices, and its upper-bound property.
5. Substitute an affine value function into the exact Bellman LP and derive (D1), (P1), and the next-period bid-price rule.
6. Prove \(z^{LP}\ge z^{P1}\ge v_1(c)\), including both inequality directions and hypotheses.
7. Explain what Theorem 2 actually says about monotone bid prices.
8. Derive reduced profit, explain P1 column generation, and use Proposition 3’s stopping certificate.
9. Read the paper’s numerical tables without confusing optimization bounds, policy rewards, published evidence, and our own results.

The central teaching theme is that **value-function approximation changes both the LP and the policy**. It reduces the number of value parameters dramatically but leaves many Bellman inequalities. Its bound and policy quality are separate questions.

## 2. A 90-minute teaching route

| Minutes | Topic | Board or slide anchor |
|---:|---|---|
| 0–10 | Capacity scarcity and the model | \(r,c,A_j,p_{tj},f_j,u\) |
| 10–25 | Bellman recursion and opportunity cost | Equations (1)–(2); one-seat calculation |
| 25–38 | Exact Bellman LP and occupancy flow | (D0), equation (3); derived exact dual |
| 38–48 | Fluid LP and shadow prices | Equations (4)–(6); primal/dual |
| 48–65 | General and affine ALP; bound proof | Equations (7)–(24); Theorem 1 |
| 65–75 | Price monotonicity and column generation | Theorem 2; Proposition 3; equation (33) |
| 75–85 | How to read the numerical section | Tables 3, 5–11 and policy variants |
| 85–90 | Critique and exit questions | Bound versus policy, assumptions |

For a shorter class, assign §3 of the paper and the exact LP dual as preparatory reading. Keep the worked example, bound proof, and reduced-cost interpretation in class. Avoid spending the entire session on Theorem 2’s algebra; teach its proof architecture and state its hypotheses precisely.

## 3. Background: why revenue management is an MDP

Imagine one seat and two selling periods. A low-fare customer now competes with the chance of a high-fare customer later. If you accept now, you receive money but lose the option to sell the seat later. The opportunity cost of acceptance is a difference in future value functions, not simply the accounting cost of a seat.

An MDP supplies the language:

| MDP concept | Revenue-management meaning |
|---|---|
| State | Remaining capacities and current period |
| Action | Which request classes would be accepted if they arrive |
| Transition | Stochastic arrival, then capacity use if accepted |
| Reward | Accepted class’s fare |
| Value \(v_t(r)\) | Optimal expected revenue from periods \(t,\ldots,T\) |
| Policy | Rule mapping period, capacity, and request class to accept/reject |

The fluid LP is appealing because it has only \(n\) acceptance variables. It optimizes expected totals but does not specify which demand path occurs first. The exact MDP does, but its state vector has one coordinate per resource. The affine approximation is Adelman’s middle course: preserve time-specific value coefficients while reducing the number of coefficients from one per state to \(m+1\) per period.

**Important naming convention:** The paper labels the value-function minimization LP (D0) and its affine restriction (D1). It calls their state-action duals primal models (P1 for the affine case). Do not infer objective direction from the letter alone. “Dual prices” \(b_{t,i}\) are the variables of D1 when viewed as the dual of P1.

## 4. The model, transition kernel, and Bellman equations

There are \(m\) resources, \(n\) request classes, and periods \(t=1,\ldots,T\). Initial capacity \(c_i>0\) is integer. At the beginning of period \(t\), \(r_i\in\{0,\ldots,c_i\}\) remains. Class \(j\) consumes \(a_{ij}\) units of resource \(i\), with \(a_{ij}\) a nonnegative integer, and earns \(f_j>0\). Let \(A_j\) be column \(j\) of the resource matrix. The probability of a class-\(j\) arrival in period \(t\) is \(p_{tj}\). At most one request arrives, so \(p_{t0}=1-\sum_jp_{tj}\ge0\) is the no-arrival probability. These are the source assumptions in §2.1, pp. 648–649.

Adelman chooses a **prearrival action vector** \(u\in\{0,1\}^n\), where \(u_j=1\) means “accept class \(j\) if it is the arriving class.” Feasibility is individual:

\[
\mathcal U(r)=\{u\in\{0,1\}^n:a_{ij}u_j\le r_i\ \forall i,j\}.
\]

Why individual rather than \(\sum_j a_{ij}u_j\le r_i\)? Only one \(j\) can arrive. The sum constraint would incorrectly require capacity for several mutually exclusive requests. If multiple requests can arrive together, Adelman’s action model needs modification.

The expected immediate reward is \(q_t(r,u)=\sum_jp_{tj}f_ju_j\). For any candidate next state \(r'\), the transition kernel is

\[
P_t(r'\mid r,u)=p_{t0}\mathbf1\{r'=r\}
+\sum_jp_{tj}\mathbf1\{r'=r-A_ju_j\}.
\]

Several terms may point to the same next state; add their probabilities. This is a derived compact statement of the transitions described on p. 649. The initial state is \(c\). The terminal value is \(v_{T+1}(r)=0\). There is no discount factor in this finite-horizon revenue model.

Conditioning on the arrival yields Adelman’s equation (1):

\[
v_t(r)=\max_{u\in\mathcal U(r)}
\left\{\sum_jp_{tj}\bigl[f_ju_j+v_{t+1}(r-A_ju_j)\bigr]
+p_{t0}v_{t+1}(r)\right\}.
\]

For a feasible class \(j\), acceptance is better than rejection exactly when

\[
f_j+v_{t+1}(r-A_j)\ge v_{t+1}(r),
\qquad\text{or}\qquad
f_j\ge\underbrace{v_{t+1}(r)-v_{t+1}(r-A_j)}_{\text{opportunity cost}}.
\]

That is equation (2). With a tie, the displayed basic rule accepts. If capacity is insufficient, acceptance is forbidden, even for a high fare. Because the action components are independent under the one-arrival assumption, we can rewrite the recursion as

\[
v_t(r)=v_{t+1}(r)
+\sum_{j:r\ge A_j}p_{tj}
\left[f_j-v_{t+1}(r)+v_{t+1}(r-A_j)\right]_+.
\]

**Board explanation:** “Start with tomorrow’s value if we do nothing. Each possible arrival contributes its probability times the positive gain from accepting it.” Here \([x]_+=\max\{x,0\}\).

The state count in the paper’s full-state convention is \(1+(T-1)\prod_i(c_i+1)\), since the period-1 state is fixed at \(c\) and later periods allow the whole rectangular capacity set (p. 656). This count can greatly exceed reachable states. Each state can have many feasible prearrival action vectors, up to \(2^n\).

## 5. Bellman LP duality and the separate discounted course LP

### 5.1 Exact finite-horizon value LP

Adelman’s (D0), p. 649 equation (3), minimizes \(v_1(c)\) over unrestricted real \(v_t(r)\), with \(v_{T+1}=0\), subject to

\[
v_t(r)-\sum_{r'}P_t(r'\mid r,u)v_{t+1}(r')
\ge q_t(r,u)
\quad\forall t=1,\ldots,T,\ r\in\mathcal R_t,\ u\in\mathcal U(r).
\]

For \(t=1\), \(\mathcal R_1=\{c\}\); the paper uses the full capacity rectangle for later \(\mathcal R_t\). Every feasible \(v\) is a Bellman supersolution. Prove it by backward induction: at \(T\), the inequalities dominate every action’s last-period reward, hence their maximum; if \(\hat v_{t+1}\ge v^*_{t+1}\), each inequality at \(t\) dominates the corresponding action evaluated with \(v^*_{t+1}\). Thus \(\hat v_t\ge v^*_t\). The exact optimal value function itself is feasible, so the LP objective equals \(v_1^*(c)\). This is Proposition 1’s logic (pp. 649–650).

### 5.2 Deriving the exact occupancy dual

This dual is independently derived; the paper does not display a separately labeled (P0). Attach \(x_t(r,u)\ge0\) to each D0 inequality written as \(q_t(r,u)-v_t(r)+\sum_{r'}P_t(r'\mid r,u)v_{t+1}(r')\le0\). Since every \(v_t(r)\) is free, finite minimization of the Lagrangian forces its coefficient to zero. For the initial state this gives total mass 1. For every later state it gives incoming mass equal to outgoing mass:

\[
\begin{aligned}
\max_{x\ge0}\quad&\sum_{t,r,u}q_t(r,u)x_t(r,u),\\
\text{s.t.}\quad&
\sum_u x_1(c,u)=1,\\
&\sum_u x_t(r,u)=
\sum_{s,u}P_{t-1}(r\mid s,u)x_{t-1}(s,u)
\quad\forall t=2,\ldots,T,\ r\in\mathcal R_t.
\end{aligned}
\]

These \(x\)'s are real state-action occupancy probabilities for randomized policies. Strong LP duality equates their maximum reward with \(v_1^*(c)\). Complementary slackness says \(x_t(r,u)>0\) implies the corresponding Bellman inequality is tight. It identifies an optimal action on a state actually occupied by the dual solution; it does not force a unique policy at unreachable states.

### 5.3 The instructor’s generic discounted LP

The instructor prompt p. 1 concerns a different, discounted MDP. With finite states \(S\), actions \(A(s)\), discount \(0\le\gamma<1\), transition \(P(s'\mid s,a)\), and nonnegative initial weight \(\nu(s)\), its primal is

\[
\min_{V\in\mathbb R^{S}}\sum_s\nu(s)V(s)
\quad\text{s.t.}\quad
V(s)-\gamma\sum_{s'}P(s'\mid s,a)V(s')\ge r(s,a)
\quad\forall s,\ a\in A(s).
\]

Collecting coefficients of the free \(V(s)\) gives the dual

\[
\max_{x\ge0}\sum_{s,a}r(s,a)x(s,a)
\quad\text{s.t.}\quad
\sum_a x(s,a)-\gamma\sum_{s',a'}P(s\mid s',a')x(s',a')=\nu(s)
\quad\forall s.
\]

The \(x(s,a)\) are \(\nu\)-weighted *discounted expected visit counts*. If \(\sum_s\nu(s)=1\), summing all flow equations gives \(\sum_{s,a}x(s,a)=1/(1-\gamma)\). For \(\nu(s)>0\) at every state, any optimal primal vector equals \(V^*\) everywhere. When some \(\nu(s)=0\), an optimal primal vector may be loose there although \(V^*\) remains an optimum. The course LP uses discounted stationary flow; Adelman’s exact LP uses undiscounted flow indexed by finite time.

## 6. The deterministic or “fluid” LP

Let \(d_j=\sum_{t=1}^T p_{tj}\) be expected class-\(j\) arrivals, and let \(Y_j\) be *expected* class-\(j\) acceptances. Equations (4)–(6), p. 650, are

\[
\begin{array}{ll}
z^{LP}=\max_{Y\ge0}&\displaystyle\sum_j f_jY_j\\
\text{s.t.}&\displaystyle\sum_j a_{ij}Y_j\le c_i\quad(\forall i),\\
&Y_j\le d_j\quad(\forall j).
\end{array}
\]

For any feasible policy, let \(N_j\) be its random number of class-\(j\) acceptances and set \(Y_j=E[N_j]\). Every sample path uses no more than \(c_i\) units, and \(N_j\) cannot exceed that path’s class-\(j\) arrivals. Expectations satisfy both LP constraint families, while expected policy revenue is \(\sum_j f_jY_j\). Therefore \(V^*\le z^{LP}\).

With resource prices \(\lambda_i\ge0\) and demand-cap prices \(\mu_j\ge0\), the fluid dual displayed on p. 650 is

\[
\begin{array}{ll}
\min_{\lambda,\mu\ge0}&\displaystyle\sum_i c_i\lambda_i+\sum_jd_j\mu_j\\
\text{s.t.}&\displaystyle\sum_i a_{ij}\lambda_i+\mu_j\ge f_j\quad(\forall j).
\end{array}
\]

The opportunity-cost approximation is \(A_j^\top\lambda\). A conventional bid-price rule accepts feasible \(j\) if \(f_j\ge A_j^\top\lambda\), with a stated tie rule. Explain that \(\lambda_i\) is a *marginal value in this deterministic LP*, not an exact MDP marginal value. If resource \(i\) has slack in an optimal fluid solution, complementary slackness gives \(\lambda_i=0\) for any paired optimal dual solution. If \(Y_j>0\), its dual inequality is tight: \(A_j^\top\lambda+\mu_j=f_j\). If \(Y_j<d_j\), then \(\mu_j=0\). A positive \(\mu_j\) values relaxing the *expected-demand* cap, not adding resource capacity.

The fluid LP mixes expected fractional demand from mutually exclusive arrival histories. It can allocate capacity to expected arrivals even when there is a material probability of no arrival at all. It also loses chronological information: accepting a low-value early request can preclude a high-value late request.

## 7. From an exact value function to an approximate LP

### 7.1 The general basis-function construction

Choose basis functions \(\phi_k(r)\) and write \(h_t(r)=\sum_{k=1}^K V_{tk}\phi_k(r)\). Substitute \(h\) for \(v\) in **every** D0 Bellman inequality and minimize \(h_1(c)\); set \(h_{T+1}=0\). This is equations (7)–(9), pp. 650–651. The coefficients \(V_{tk}\) are free unless an additional valid restriction is proved. The number of value coefficients falls from roughly \(T\prod_i(c_i+1)\) to \(TK\), but the Bellman-inequality family remains large.

The dual in equations (10)–(12) has nonnegative state-action variables \(X_t(r,u)\). For each basis function and period, it conserves only its *moment*:

\[
\sum_{r,u}\phi_k(r)X_1(r,u)=\phi_k(c),\qquad
\sum_{r,u}\phi_k(r)X_t(r,u)=
\sum_{s,u}E[\phi_k(R_t)\mid s,u]X_{t-1}(s,u),\quad t\ge2.
\]

Full statewise conservation is gone. Thus an \(X\) feasible for the approximate dual need not be an occupancy distribution of any implementable policy. Its objective is an optimization bound, not simulated policy revenue.

The approximate acceptance test has opportunity cost
\[
h_{t+1}(r)-h_{t+1}(r-A_j)
=\sum_kV_{t+1,k}\{\phi_k(r)-\phi_k(r-A_j)\}.
\]
Nonlinear bases can make this depend on remaining capacity. The affine basis below makes it independent of \(r\) inside one fixed solve.

### 7.2 Derive Adelman’s affine (D1)

Set \(h_t(r)=\theta_t+\sum_i b_{ti}r_i\) and \(\theta_{T+1}=b_{T+1,i}=0\). Start with D0’s one-period inequality
\(h_t(r)\ge\sum_j p_{tj}u_jf_j+E[h_{t+1}(R_{t+1})\mid r,u]\).
The transition expectation is
\[
E[h_{t+1}(R_{t+1})\mid r,u]
=\theta_{t+1}+\sum_i b_{t+1,i}r_i
-\sum_jp_{tj}u_j\sum_i a_{ij}b_{t+1,i}.
\]
Move the future affine value to the left. Substituting the affine ansatz (14) gives D1's objective (16) and constraints (17), p. 652:
\[
\boxed{\theta_t-\theta_{t+1}
+\sum_i(b_{ti}-b_{t+1,i})r_i
\ \ge\ \sum_jp_{tj}u_j
\left(f_j-\sum_i a_{ij}b_{t+1,i}\right)}
\quad\forall t,\ r\in\mathcal R_t,\ u\in\mathcal U(r).
\]
Minimize \(\theta_1+\sum_i c_ib_{1i}\). This is (D1). Circle the \(t+1\) subscript when teaching: revenue is earned now, but consumed capacity changes *next period’s* state. The intercept cancels when comparing acceptance with rejection, hence equation (15):
\[
\text{accept feasible class }j
\quad\Longleftrightarrow\quad f_j\ge A_j^\top b_{t+1},
\]
subject to the tie convention. The time path \(b_{t+1}\) changes with \(t\), but not directly with \(r\) for a fixed D1 solution. Feasibility still depends on \(r\); periodically re-solving D1 at a new state can create additional inventory responsiveness.

### 7.3 Derive the affine dual (P1), rather than guessing signs

Write a D1 inequality as \(q_t(r,u)-\theta_t+\theta_{t+1}-(b_t-b_{t+1})^\top r-\sum_jp_{tj}u_j b_{t+1}^\top A_j\le0\), where \(q_t(r,u)=\sum_jp_{tj}u_jf_j\). Multiply by \(X_t(r,u)\ge0\) and collect each free \(\theta_t\) and \(b_{ti}\). Their coefficients must vanish in the Lagrangian. The result is P1’s objective and constraints (18)–(21), p. 652:

\[
\begin{array}{ll}
z^{P1}=\max_{X\ge0}&\displaystyle\sum_{t,r,u}\sum_jp_{tj}u_jf_jX_t(r,u)\\
\text{s.t.}&\displaystyle\sum_{r,u}X_t(r,u)=1\quad(\forall t),\\
&\displaystyle\sum_{r,u}r_iX_1(r,u)=c_i\quad(\forall i),\\
&\displaystyle\sum_{r,u}r_iX_t(r,u)=
\sum_{r,u}\left(r_i-\sum_jp_{t-1,j}u_ja_{ij}\right)X_{t-1}(r,u)\\
&\hfill(\forall i,\ t=2,\ldots,T).
\end{array}
\]

At \(t=1\) the only state is \(c\), so the initial resource equalities are redundant given initial mass 1, but displaying them makes the basis-flow structure clear. P1 has one mass and \(m\) resource-moment equations per period, rather than one equation for each state. It can nevertheless have an enormous number of \(X_t(r,u)\) columns. D1 and P1 have equal optimal objectives by finite LP strong duality when feasible and bounded; they are two sides of *one* approximate LP, not two successive approximations.

**Board checkpoint:** Which equation was lost compared with the exact occupancy dual? Conservation of probability separately at each state. Preserving only total mass and mean resources is precisely how the dual relaxation can exceed the true MDP optimum.

## 8. Prove the central bound, one direction at a time

Theorem 1, p. 653, states
\[
\boxed{z^{LP}\ \ge\ z^{P1}\ \ge\ V^*=v_1(c).}
\]
The right inequality: D1 restricts the exact Bellman LP to an affine family but retains every Bellman inequality. Each D1-feasible value approximation is a supersolution, hence an upper bound on \(V^*\). Minimizing within the restricted family cannot do better than the unrestricted exact LP. Strong duality replaces the D1 objective by \(z^{P1}\).

For the left inequality, take any P1-feasible \(X\), not necessarily policy-realizable. Define (equation (22))
\[
Y_j=\sum_{t,r,u}p_{tj}u_jX_t(r,u).
\]
First, \(Y_j\le\sum_t p_{tj}=d_j\), because \(u_j\le1\) and each period’s \(X\)-mass is 1. Second, the resource-moment balance telescopes from initial mean \(c_i\) to final expected remaining resource:
\[
c_i-\sum_j a_{ij}Y_j
=\sum_{r,u}r_iX_T(r,u)
-\sum_{r,u,j}p_{Tj}u_ja_{ij}X_T(r,u)\ge0.
\]
The last expression is nonnegative because each feasible acceptance obeys \(a_{ij}u_j\le r_i\), and total arrival probability is at most one. Thus \(Y\) satisfies fluid capacity and demand constraints. Its fluid objective \(\sum_jf_jY_j\) equals the P1 objective of \(X\). Maximizing over a larger fluid feasible set gives \(z^{LP}\ge z^{P1}\). This is the aggregation in equations (22)–(24).

**Important qualification:** a tighter upper bound says nothing by itself about which derived policy earns more. For an *exactly evaluated* feasible policy \(\pi\), \(J(\pi)\le V^*\le z^{P1}\le z^{LP}\). A Monte Carlo mean \(\hat J\) estimates \(J(\pi)\) with uncertainty; it is not automatically a certified lower bound.

### 8.1 The quasi-static appendix is not the fluid LP

The Appendix, pp. 660–661, holds the slopes \(b_i\) constant over time while allowing time intercepts. Its equations (A1)–(A3) define a distinct quasi-static affine relaxation with
\[
z^{LP}\ge z^{quasi}\ge z^{P1}\ge V^*.
\]
Do not say “the fluid LP is D1 with constant prices.” The models have different constraints. The Appendix relates their bounds by an additional aggregation argument.

## 9. What the structural price theorem actually proves

Lemma 1 and Theorem 2, pp. 653–655, are **existence** results for an optimal affine-LP dual solution. Under the theorem’s assumptions \(c_i>0\) and \(p_{tj}>0\) for every resource, period, and request class, one can choose an optimal solution with nonnegative resource prices that are nonincreasing in time. For each resource, its price may be flat before a first-use threshold, then nonincreasing afterward. The intercept sequence can likewise be selected nonnegative and nonincreasing. The theorem does not require every optimal vector returned by a degenerate LP solver to have the same trajectory.

Teach the proof as four moves:

1. Lemma 1 uses P1’s mass and moment balances to identify relevant state-action support, including the first period in which a resource is used.
2. Complementary slackness makes the D1 Bellman constraints tight at positive P1 columns.
3. Compare feasible states differing by one unit of a resource in those tight constraints. The resulting inequalities constrain successive \(b_{ti}\) values; feasibility and positive arrivals matter here.
4. Where a price would rise before first use, transform the early slopes and intercepts while preserving D1 feasibility and objective. This selects a monotone optimum. Equations (25)–(29) contain the detailed construction.

The paper also closes the boundary case of a resource never used: its selected slopes are zero throughout. The feasible \(r=0,u=0\) constraint yields \(\theta_t\ge\theta_{t+1}\); the zero terminal intercept then yields \(\theta_t\ge0\) (p. 655).

Intuition: with fewer selling opportunities left, capacity’s future option value tends to decline. But intuition is not the proof, and it need not apply unchanged to replenishing capacity, arbitrary basis functions, or model changes. Corollary 1, p. 655, yields a class-dependent time-threshold property conditional on feasibility for this affine policy. Do not generalize it to an exact network MDP policy: state-dependent opportunity costs can destroy a simple threshold.

If a solver trajectory is nonmonotone, check whether it is another optimal solution, whether numerical tolerances or ties matter, and whether the theorem’s assumptions hold before calling the theorem false. Adding valid monotonicity inequalities can select a convenient optimum; any runtime benefit is empirical, not promised by the theorem.

## 10. Column generation and reduced profit

P1 has few moment equations but many state-action columns. A restricted master retains only a subset \(\Lambda_t\) of columns in each period. Start with feasible no-acceptance columns at the initial-capacity state across periods. These describe a zero-revenue feasible trajectory, so the restricted master is feasible. Solve it to get \(Z_\Lambda\) and dual \((\theta,b)\). Since this is a **maximization over fewer columns**, \(Z_\Lambda\le z^{P1}\); it is not automatically an upper bound on the exact MDP.

For a missing period-\(t\) column \((r,u)\), its reduced *profit* is
\[
\rho_t(r,u)
=\sum_jp_{tj}u_j(f_j-A_j^\top b_{t+1})
-(b_t-b_{t+1})^\top r-\theta_t+\theta_{t+1}.
\]
At \(t=1\), use \(r=c\); terminal \(\theta_{T+1}=b_{T+1}=0\). This is the negative slack of the D1 inequality. A positive maximum \(\rho_t^*\) means some omitted P1 column can improve the restricted objective. Pricing maximizes this expression over integer \(0\le r_i\le c_i\), binary \(u_j\), and \(a_{ij}u_j\le r_i\) for every \(i,j\). This is equations (33)–(36), pp. 655–656. The paper implements it as an integer program. It reports computational ease for its instances; it does **not** prove a general polynomial-time complexity classification.

Repeat: solve restricted master, price each period, add positive-profit columns, and re-solve. With globally solved pricing subproblems, Proposition 3, p. 651, supplies
\[
Z_\Lambda\le z^{P1}\le Z_\Lambda+\sum_{t=1}^T\max(0,\rho_t^*).
\]
The constant basis function is essential to this probability-mass-based certificate. An implementation should stop against a stated absolute or relative certificate, not merely because no sampled omitted columns happened to improve. A restricted-master value reported before exact pricing correction is not automatically a certified MDP upper bound.

**Small board exercise:** If \(Z_\Lambda=90\) and the globally maximized positive reduced profits are \(0.2,0,0.3\), then \(90\le z^{P1}\le90.5\). The number 90 alone is a feasible approximate-dual objective, not a valid upper bound on \(V^*\). The 90.5 certificate is an upper bound on \(z^{P1}\) and therefore on \(V^*\).

## 11. Two examples to teach from

### 11.1 Adelman’s Example 1: uncertain arrival, not uncertain fare

One resource, \(c=1\), one class, \(a=f=1\), two periods, each with arrival probability \(1/2\). The exact value is \(P(\text{at least one arrival})=1-(1/2)^2=3/4\). The fluid LP sees total expected demand 1, so \(z^{LP}=1\). The affine approximation is exact on a one-seat state space \(\{0,1\}\), so \(z^{P1}=3/4\) (Example 1, p. 653). A derived affine representation is \(h_2(r)=\frac12r\), \(h_1(r)=\frac34r\) on \(\{0,1\}\). It gives \(h_1(1)=3/4\) and \(h_1(0)=0\).

Ask: “Where did the missing quarter go?” There is probability \(1/4\) of no arrival in either period. The fluid LP can allocate its unit of expected demand without modeling that outcome.

### 11.2 An independently constructed chronology example

This is **not a paper instance or computational result**. One seat, two periods. At \(t=1\), a low class arrives with probability \(0.4\), fare 1. At \(t=2\), a high class arrives with probability \(0.4\), fare 3. No other class arrives. Thus \(v_2(1)=0.4(3)=1.2\), \(v_2(0)=0\). Accepting low now sacrifices expected future value 1.2 for immediate fare 1, so the exact policy rejects it and \(V^*=1.2\).

The fluid LP can set \(Y_L=Y_H=0.4\), using 0.8 expected seats, and obtains \(z^{LP}=0.4(1)+0.4(3)=1.6\). Capacity is slack, so the unique resource shadow price is \(\lambda=0\). A fluid-price rule solved once therefore accepts low. Its exact expected reward is \(0.4(1)+0.6(0.4)(3)=1.12\). Because any value function on the binary seat state is affine, D1 attains 1.2 and its next-period price \(b_2=1.2\) rejects the low request. In this constructed case the dynamic rule earns 1.2. This illustrates *a possible advantage*, not a universal policy-dominance theorem.

## 12. How to articulate Adelman’s computational comparisons

The experiments in §5, pp. 656–660, are **published, source-stated results**, not results independently reproduced in this project. The paper’s instance generator is synthetic. Table 1 varies the number of airports \(L\in\{2,5,10,20\}\), with \(m=2L\) flight-leg resources and \(n=2[m+L(L-1)]\) fare classes, producing \(n=12,60,220,840\). Horizons include 20, 50, 100, 200, 500, and 1000. The construction includes a stationary no-arrival probability of 0.2 in its base setting, low fares from integer 15–49, high fares five times low fares, and a 25%/75% high-/low-fare demand split. These details matter because each table compares particular generated instances, not all revenue-management systems.

| Source | What is being compared | Safe classroom statement |
|---|---|---|
| Table 2 | Capacity and load statistics | Check how network scarcity changes before attributing performance changes to a single factor. |
| Tables 3–4 | Runtime with structural constraints and changing load | Monotonicity constraints and lower load often help on these instances. Table 3’s average reported speedup is at least 21.32; its range is 2.06–157.10. Historical CPLEX 9.1 / 3.6 GHz Xeon / 3 GB timings do not predict current hardware. |
| Figure 3 | Relative bound improvement versus relative policy improvement | These are distinct outcomes; one need not track the other perfectly. |
| Table 5 | Fluid objective versus restricted P1 objective, 5% restricted-master tolerance | Ratios can reach 1.485 in the first 24 cases, meaning the fluid objective is 48.5% larger than the reported P1 value. The paper explicitly warns these P1 figures are **not strict upper bounds** at that tolerance. |
| Tables 6–8 | Bound comparison and simulated BPC/DBPC revenues under stationary or nonstationary arrivals | The reported fluid value can be up to 50.4% larger than the reported P1 value (ratio 1.504); simulated DBPC revenue can be up to 21.4% higher than BPC in displayed comparisons. These are different metrics and denominators; neither is a universal guarantee. |
| Table 9 | Re-solving every period versus re-solving five times | This isolates re-solving frequency within the studied setting; it is not a DBPC/BPC policy ratio. One reported ratio is 0.999, so “every period always wins” overstates the table. |
| Tables 10–11, Fig. 4 | Varying load | Advantages shrink as load decreases in these instances. This is an empirical pattern, not a theorem for all networks. |

The paper’s load factor is total expected resource use requested divided by total capacity:
\[
\rho=\frac{\sum_{t,j,i}p_{tj}a_{ij}}{\sum_i c_i}.
\]
When all legs have capacity \(c\), the denominator is \(mc\). A high \(\rho\) indicates scarcity pressure, but it does not isolate competition patterns or timing. In some table sequences horizon and capacity both change, so do not infer a pure causal horizon effect.

### 12.1 One row, read correctly

For the stationary \(L=3,T=20\) row of Table 6, the paper reports approximate P1 value 683.57 and fluid value 776.69. It also reports fixed-policy simulation means 503.34 for BPC (marginal standard error 17.15) and 561.13 for DBPC (21.55); with its re-solving convention, BPC 477.55 (17.50) and DBPC 567.78 (20.54). You can say, “In this reported row, the approximate LP figure is below the fluid bound, and the simulated dynamic policy mean is above the static mean.” You cannot conclude a precise paired significance level by subtracting the reported marginal standard errors; the paired-difference variance is not shown.

Crucially, the paper defines DBPC through the equation (15) rule and then reports exploring a one-period lookahead refinement and strict \(>\) tie convention. The available wording does not unambiguously attach both refinements to every entry in Tables 6–8. Its default *re-solved* variant uses five evenly spaced solves. A clean project comparison should separately test the bare price rule, lookahead, tie convention, and re-solving so gains are attributed correctly; do not claim exact policy-table replication until the published variant is resolved.

The policy simulations use 100 common arrival paths for compared policies. Common random numbers improve the design of a *paired* comparison, but the paper reports marginal standard errors, not the standard error of each paired policy difference. Published generated input files and seeds are not available here; exact table replication is therefore not presently established.

### 12.2 Four numbers that must never be conflated

1. \(V^*\): exact optimal MDP reward, normally computable only for small cases.
2. \(z^{LP}\) and \(z^{P1}\): mathematical upper bounds when the full programs are solved; a certified corrected column-generation bound requires Proposition 3.
3. \(Z_\Lambda\): restricted-master feasible P1 value, which can be below \(V^*\).
4. \(\hat J(\pi)\): sampled policy mean, with sampling uncertainty; it may numerically exceed a bound because of noise, but the true policy expectation cannot exceed \(V^*\).

If a table says “dynamic beats static,” ask: Was each policy solved once or re-solved? Was lookahead used? Were arrival paths paired? Is the difference large relative to the *paired* uncertainty? If a table says “better bound,” ask whether it is a full or certified P1 upper bound, which benchmark it uses, and whether both numbers correspond to the same instance.

### 12.3 Asymptotic and computational claims

The paper states an asymptotic-optimality relationship for P1 by sandwiching it between \(V^*\) and the fluid bound under joint linear scaling of horizon, expected demand, and capacities, relying on a cited fluid-limit result. Teach the logic of the sandwich, but do not present the cited result as independently proved in this guide. “More accurate bound” is not synonymous with “faster model”: D1 has few coefficients but many constraints, and column generation requires pricing work. Nor does a faster historical run establish a complexity theorem.

## 13. What to challenge in discussion

- The arrival distribution is known and exogenous, with at most one request per period. What changes if demand reacts to price or multiple requests arrive?
- Resource capacity does not replenish and there are no cancellations. A surveillance application with reusable assets needs a different transition model.
- Each accepted class has a fixed additive fare and fixed resource vector. What if rewards depend on the portfolio of accepted missions?
- The fixed affine bid-price trajectory is time-dependent, not inventory-dependent. Does re-solving improve decisions enough to justify runtime?
- A stronger bound is not a proof of better policy decisions. Can students construct a bound improvement with equal or worse policy reward?
- Published experiments use synthetic instances and no large-instance exact MDP benchmark. What can a policy simulation establish, and what can it not?
- “Truncation” may mean stopping column generation with a certificate, pruning states, or shortening the horizon. Only the first retains a direct P1 certificate under globally valid pricing. The others require new error analysis.

## 14. Exercises with short answers

**A. Bellman acceptance.** A feasible request pays 8; accepting reduces next-period value from 14 to 5. Accept? **No:** opportunity cost 9 exceeds fare 8. If the two future values were 14 and 7, accept; the opportunity cost would be 7.

**B. Fluid dual.** What does \(\lambda_i=0\) mean? **Answer:** At that LP optimum, marginally enlarging a slack resource does not improve the deterministic objective locally. It does not prove the resource is valueless on every stochastic path.

**C. Affine indexing.** Why \(b_{t+1}\) rather than \(b_t\) in the acceptance rule? **Answer:** Current reward is compared with the following period’s values at \(r\) and \(r-A_j\). Their intercepts cancel.

**D. Approximate dual.** Why can a P1-feasible \(X\) be nonimplementable? **Answer:** It conserves mass and mean capacities, not the probability flowing into each exact state.

**E. Bound proof.** Which P1 constraints give \(Y_j\le d_j\)? **Answer:** The per-period mass equations and \(u_j\le1\). Which give \(AY\le c\)? The resource-moment balances, terminal nonnegativity, and action feasibility.

**F. Restricted master.** If \(Z_\Lambda=100\) and certified pricing maxima sum to 2, can you call 100 an MDP upper bound? **No.** You may report the certified 102 upper bound and a 2-unit interval for P1.

**G. Statistical comparison.** Two policies share 100 arrival paths; the paper reports their separate standard errors. Can you calculate the paired-difference confidence interval from those alone? **No.** You also need their sample covariance or the paired differences themselves.

## 15. Closing explanation to deliver aloud

“Adelman starts with an exact but enormous finite-horizon MDP. Its Bellman inequalities form an LP. A deterministic fluid LP is cheap but forgets demand timing and arrival uncertainty. He restricts the Bellman LP to time-varying affine value functions; the resulting dual preserves probability mass and average resource flow, not full state flow. That relaxation is still an upper bound on the exact MDP and is at least as tight as the fluid bound. The slopes become next-period bid prices. Their useful monotonic structure can be selected under the paper’s assumptions. Column generation tackles the many state-action columns, with reduced-profit pricing and a stopping certificate. The experiments suggest tighter bounds and sometimes better policies, but the bound theorem does not imply policy dominance, and the published policy comparisons include lookahead and re-solving choices.” 

**Source map:** model/Bellman (printed pp. 648–649, eqs. (1)–(2)); exact LP/Proposition 1 (pp. 649–650, eq. (3)); fluid LP/dual (p. 650, eqs. (4)–(6)); general ALP/Propositions 2–3 (pp. 650–651, eqs. (7)–(12)); affine D1/P1 (p. 652, eqs. (14)–(21)); bound Theorem 1/Example 1 (p. 653, eqs. (22)–(24)); monotonicity Lemma 1/Theorem 2/Corollary 1 (pp. 653–655, eqs. (25)–(29)); pricing (pp. 655–656, eqs. (33)–(36)); numerical results (pp. 656–660, Tables 1–11); quasi-static Appendix (pp. 660–661, eqs. (A1)–(A3)).
