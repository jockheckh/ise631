# Phase 1 source-to-code specification (draft for independent audit)

Scope: Adelman (2007), *Dynamic Bid Prices in Revenue Management*, printed
pp. 648-657. This fixes the mathematics for implementation. It is not solver
evidence or a completed theorem audit. The 2025 hub-and-spoke repository is an
instance-design reference only.

## State, timing, and action convention

Periods are \(t=1,\ldots,T\); there are \(m\) nonreplenishing resources and
\(n\) products. Source-model initial capacities are positive integers
\(c_i>0\); resource-use coefficients satisfy \(a_{ij}\in\mathbb Z_{\ge0}\),
and product revenues satisfy \(f_j>0\). Remaining prearrival capacity
belongs to \(\mathcal R_1=\{c\}\) in period 1 and
\(\mathcal R_t=\prod_i\{0,\ldots,c_i\}\) for \(t=2,\ldots,T\).
Class \(j\)
arrives with probability \(p_{tj}\ge0\), and \(\sum_jp_{tj}\le1\).
At most one request arrives per period. Product \(j\) earns \(f_j\) and
consumes \(A_j=(a_{1j},\ldots,a_{mj})\).

A prearrival action vector \(u\in\{0,1\}^n\) says which possible classes
would be accepted; feasibility is \(a_{ij}u_j\le r_i\) for every \(i,j\).
It is NOT \(\sum_j a_{ij}u_j\le r_i\), because only one class arrives.
No-arrival probability is \(p_{t0}=1-\sum_jp_{tj}\).
Terminal values are \(v_{T+1}(r)=0\). Adelman's model has no discount.
The instructor's generic discounted occupancy LP is a separate formulation.

## Exact oracle and LP — Adelman (1)-(3), pp. 648-649

\[
v_t(r)=\max_{u\in U(r)}
\left\{\sum_jp_{tj}[f_ju_j+v_{t+1}(r-A_ju_j)]
+p_{t0}v_{t+1}(r)\right\}.
\]

The exact Bellman LP minimizes \(v_1(c)\), subject to each value being at
least the displayed action value for every
\(t=1,\ldots,T,\ r\in\mathcal R_t,\ u\in U(r)\). Value variables
are free real variables. A distinct occupancy LP will be derived from these
constraints on small cases. Exact backward DP, Bellman LP, and occupancy-dual
objectives must agree within stated tolerance.

## Fluid primal and dual — Adelman (4)-(6), p. 650

Let \(d_j=\sum_t p_{tj}\). The fluid primal is
\[
\max_{Y\ge0}\ f^\top Y\quad
\text{s.t. }AY\le c,\quad Y_j\le d_j\ (\forall j).
\]
Its dual is
\[
\min_{\lambda,\mu\ge0}\ c^\top\lambda+d^\top\mu\quad
\text{s.t. }A_j^\top\lambda+\mu_j\ge f_j\ (\forall j).
\]
Verify primal-dual equality, dual signs, and complementary slackness on
toys. A fixed fluid policy accepts a feasible \(j\) when
\(f_j\ge A_j^\top\lambda\), with its tie convention recorded.

## Affine D1 and moment dual P1 — Adelman (14)-(21), p. 652

Set \(\widehat v_t(r)=\theta_t+b_t^\top r\) and terminal
\(\theta_{T+1}=b_{T+1}=0\). D1 minimizes \(\theta_1+b_1^\top c\)
over free \(\theta_t,b_{ti}\), subject to
\[
\theta_t-\theta_{t+1}+(b_t-b_{t+1})^\top r
+\sum_jp_{tj}u_jb_{t+1}^\top A_j
\ge\sum_jp_{tj}f_ju_j
\quad(\forall t=1,\ldots,T,\ r\in\mathcal R_t,\ u\in U(r)).
\]
The fixed-solve policy accepts feasible \(j\) when
\(f_j\ge A_j^\top b_{t+1}\). The intercept cancels. Prices vary with
time, not directly with inventory within a fixed solve.

P1 maximizes \(\sum_{t,r,u}X_t(r,u)\sum_jp_{tj}f_ju_j\) over
\(X_t(r,u)\ge0\). It has one mass equation
\(\sum_{r,u}X_t(r,u)=1\) per period and resource-moment equations
\[
\sum_{r,u}r_iX_1(r,u)=c_i,\qquad
\sum_{r,u}r_iX_t(r,u)=
\sum_{r,u}\left(r_i-\sum_jp_{t-1,j}a_{ij}u_j\right)
X_{t-1}(r,u)\quad(t\ge2,\ \forall i).
\]
P1 does NOT conserve statewise probability; feasible \(X\) need not
encode an implementable policy. Enumerated D1 and P1 objectives must agree.
For finite instances, P1 is feasible via the no-acceptance columns
\(X_t(c,0)=1\), and its per-period mass constraints bound revenue
above by \(T\max_j f_j\). D1 is feasible by choosing \(b_t=0\) and
sufficiently large backward-recursive intercepts \(\theta_t\).
Thus ordinary finite-dimensional LP strong duality applies.

## Bound and column-generation checks

For P1-feasible \(X\), set
\(Y_j=\sum_{t,r,u}p_{tj}u_jX_t(r,u)\). Mass balance gives
\(Y_j\le d_j\). Summing resource moments gives
\[
c_i=\sum_ja_{ij}Y_j+
\sum_{r,u}\left(r_i-\sum_jp_{Tj}a_{ij}u_j\right)X_T(r,u).
\]
The residual is nonnegative: every feasible action satisfies
\(a_{ij}u_j\le r_i\) and \(\sum_jp_{Tj}\le1\). Thus
\(c_i\ge\sum_ja_{ij}Y_j\), so \(Y\) is fluid-feasible with the
same objective. Restricting the exact Bellman LP to affine values gives
the other half of Theorem 1 (p. 653):
\[
z^{LP}\ge z^{P1}\ge v_1(c).
\]
This does not prove policy dominance. A policy simulation mean is an
estimate, not a certified mathematical lower bound.

For a restricted P1 master, \(Z_\Lambda\le z^{P1}\). Pricing
globally maximizes reduced profit (Adelman (33)-(36), pp. 655-656)
\[
\rho_t(r,u)=\sum_jp_{tj}(f_j-b_{t+1}^\top A_j)u_j
-(b_t-b_{t+1})^\top r-\theta_t+\theta_{t+1},
\]
over integer \(0\le r_i\le c_i\), binary \(u_j\), and
\(a_{ij}u_j\le r_i\); at \(t=1\), \(r=c\). Gurobi pricing must
match exhaustive enumeration on tiny cases. Start the restricted
master with the \(T\) no-acceptance columns \((t,c,0)\) from
Proposition 2 (p. 651); they establish feasibility. Proposition 3
(p. 651) states \(z^{P1}\le Z_\Lambda+\sum_t\rho_t^*\), where each
\(\rho_t^*\) is the global period-\(t\) maximum reduced profit.
To derive it, multiply the full P1 mass and moment equalities by any
restricted-master optimal dual \((\theta,b)\). For any full-P1-feasible
\(X\), terms telescope to
\(z(X)-(\theta_1+b_1^\top c)=\sum_{t,r,u}\rho_t(r,u)X_t(r,u)\).
Since each period has unit nonnegative mass, this is at most
\(\sum_t\rho_t^*\). Restricted-master strong duality gives
\(\theta_1+b_1^\top c=Z_\Lambda\), proving the certificate.
If a pricing MIP stops short of proven optimality, use its valid
maximization upper bound, not its incumbent objective, in a
conservative certificate. Clamping a numerically negative period
bound to zero is a further conservative implementation safeguard,
not the literal statement of Proposition 3.
The restricted objective alone is not a certified MDP upper bound.

Zero-capacity instances will be tested as deliberate boundary cases for
the code, but they are outside source assumptions such as the positive
capacity premise used in the structural-price arguments.

Theorem 2, pp. 654-655, asserts the existence of an optimal solution
with nonincreasing resource prices under positive initial capacities
\(c_i>0\) and strictly positive arrivals \(p_{tj}>0\) for all
relevant \(i,t,j\), not that every
solver-returned alternate optimum is monotone. The proof and use of
monotonicity constraints need independent audit before implementation.

## Benchmark provenance and open questions

Adelman (2007) Section 5: one hub and \(L\) nonhub locations; \(m=2L\)
directed legs; \(m+L(L-1)\) itineraries; two fare classes per itinerary.
Low fares are discrete-uniform integers 15-49, paired high fares five
times as large; base no-arrival probability is 0.2, with a 25%/75%
high/low demand split. The distribution and seed for the remaining
random itinerary probabilities are not stated.

The 2025 repository at commit 840949ac3ee6a88aa73c2cbfd635b9ebae39ba73
uses the same network architecture and equal capacities chosen for load
near 1.61. Its main AMPL file refers to a missing data_generation.dat;
its 2025 capacities differ from 2007 Table 2. Implement a separately
labeled seeded synthetic generator, documenting every choice not fixed
by 2007. Do not substitute 2025 H-2PIAlg for 2007 D1/P1.

Before claiming policy-table reproduction, resolve the relationship
between basic equation (15), one-period lookahead, strict ties, and
five-epoch re-solving (printed pp. 658-659). Published tables remain
source-stated comparison targets, not results independently generated here.
