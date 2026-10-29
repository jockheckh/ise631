"""Gurobi fluid LP, explicit dual, and fixed static bid-price control.

Adelman (2007), equations (4)-(6), p. 650, aggregate requests over time.
The fluid LP is an upper bound on achievable expected revenue, not itself a
feasible stochastic policy. The static policy below is a *separate* object:
its exact expected revenue must be evaluated, not equated to the LP bound.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .instances import NetworkInstance


@dataclass(frozen=True)
class FluidLPSolution:
    """Numerical evidence from separate primal and dual Gurobi solves.

    ``prices`` are nonnegative capacity-constraint multipliers λ_i;
    ``demand_prices`` are nonnegative expected-demand multipliers μ_j.
    Residuals include primal/dual infeasibility, duality gap, and
    complementary slackness. ``shadow_price_disagreement`` is descriptive:
    the explicit dual and primal-shadow vectors may be different optimal
    multipliers in a degenerate LP. It is *not* an error residual that must
    vanish. Solver optimal status plus small residuals is not a proof of
    source correspondence; independent toy checks are also required.
    """

    primal_objective: float
    dual_objective: float
    acceptances: tuple[float, ...]
    prices: tuple[float, ...]
    demand_prices: tuple[float, ...]
    primal_status: int
    dual_status: int
    primal_runtime_seconds: float
    dual_runtime_seconds: float
    primal_iterations: float
    dual_iterations: float
    gurobi_version: str
    optimality_tolerance: float
    feasibility_tolerance: float
    primal_violation: float
    dual_violation: float
    duality_gap: float
    complementarity_residual: float
    shadow_price_disagreement: float


def solve_fluid_lp(instance: NetworkInstance) -> FluidLPSolution:
    """Solve Adelman's fluid primal (4)-(5) and independently coded dual (6).

    Primal, with ``d_j = sum_t p_tj``:

    ``max sum_j f_j Y_j`` subject to ``sum_j a_ij Y_j <= c_i`` for
    every resource i, ``Y_j <= d_j`` for every class j, and ``Y_j >= 0``.

    Dual:

    ``min sum_i c_i λ_i + sum_j d_j μ_j`` subject to
    ``sum_i a_ij λ_i + μ_j >= f_j`` for every class j, with
    ``λ_i, μ_j >= 0``. All LP models in this package use Gurobi; the
    pure-Python exact DP remains an independent small-instance oracle.

    An explicitly constructed silent Gurobi environment prevents license
    metadata from appearing in ordinary test output. Errors (including
    license limitations) propagate; this routine never downscales a model.
    """
    import gurobipy as gp

    demands = instance.expected_class_demand()
    with gp.Env(empty=True) as environment:
        environment.setParam("OutputFlag", 0)
        environment.setParam("Threads", 1)
        environment.start()

        with gp.Model("adelman_fluid_primal", env=environment) as primal:
            Y = primal.addVars(instance.n, lb=0.0, name="Y")
            capacity = primal.addConstrs(
                (
                    gp.quicksum(instance.A[i][j] * Y[j] for j in range(instance.n))
                    <= instance.c[i]
                    for i in range(instance.m)
                ),
                name="capacity",
            )
            demand_limit = primal.addConstrs(
                (Y[j] <= demands[j] for j in range(instance.n)), name="demand"
            )
            primal.setObjective(
                gp.quicksum(instance.f[j] * Y[j] for j in range(instance.n)),
                gp.GRB.MAXIMIZE,
            )
            primal.optimize()
            if primal.Status != gp.GRB.OPTIMAL:
                raise RuntimeError(f"fluid primal Gurobi status {primal.Status}, not OPTIMAL")
            primal_status = int(primal.Status)
            primal_objective = float(primal.ObjVal)
            acceptances = tuple(float(Y[j].X) for j in range(instance.n))
            # For a maximization with <= constraints, Gurobi's Pi is
            # nonnegative. These are diagnostics, not the only dual solve;
            # degeneracy may make them differ from the explicit dual optimum.
            primal_shadow_prices = tuple(float(capacity[i].Pi) for i in range(instance.m))
            primal_demand_prices = tuple(float(demand_limit[j].Pi) for j in range(instance.n))
            primal_runtime = float(primal.Runtime)
            primal_iterations = float(primal.IterCount)
            optimality_tolerance = float(primal.Params.OptimalityTol)
            feasibility_tolerance = float(primal.Params.FeasibilityTol)

        with gp.Model("adelman_fluid_dual", env=environment) as dual:
            lam = dual.addVars(instance.m, lb=0.0, name="lambda")
            mu = dual.addVars(instance.n, lb=0.0, name="mu")
            dual.addConstrs(
                (
                    gp.quicksum(instance.A[i][j] * lam[i] for i in range(instance.m))
                    + mu[j]
                    >= instance.f[j]
                    for j in range(instance.n)
                ),
                name="fare_cover",
            )
            dual.setObjective(
                gp.quicksum(instance.c[i] * lam[i] for i in range(instance.m))
                + gp.quicksum(demands[j] * mu[j] for j in range(instance.n)),
                gp.GRB.MINIMIZE,
            )
            dual.optimize()
            if dual.Status != gp.GRB.OPTIMAL:
                raise RuntimeError(f"fluid dual Gurobi status {dual.Status}, not OPTIMAL")
            dual_status = int(dual.Status)
            dual_objective = float(dual.ObjVal)
            prices = tuple(float(lam[i].X) for i in range(instance.m))
            demand_prices = tuple(float(mu[j].X) for j in range(instance.n))
            dual_runtime = float(dual.Runtime)
            dual_iterations = float(dual.IterCount)

    used_capacity = tuple(
        math.fsum(instance.A[i][j] * acceptances[j] for j in range(instance.n))
        for i in range(instance.m)
    )
    reduced_cost_slack = tuple(
        math.fsum(instance.A[i][j] * prices[i] for i in range(instance.m))
        + demand_prices[j]
        - instance.f[j]
        for j in range(instance.n)
    )
    primal_violation = max(
        0.0,
        *(used_capacity[i] - instance.c[i] for i in range(instance.m)),
        *(acceptances[j] - demands[j] for j in range(instance.n)),
        *(-acceptances[j] for j in range(instance.n)),
    )
    dual_violation = max(
        0.0,
        *(-prices[i] for i in range(instance.m)),
        *(-demand_prices[j] for j in range(instance.n)),
        *(-reduced_cost_slack[j] for j in range(instance.n)),
    )
    # Each term is theoretically zero at an optimum (complementary
    # slackness). Their magnitudes are more informative than rounding all
    # nonzero multipliers or activities to an arbitrary display precision.
    complementarity = max(
        0.0,
        *(abs(prices[i] * (instance.c[i] - used_capacity[i])) for i in range(instance.m)),
        *(abs(demand_prices[j] * (demands[j] - acceptances[j])) for j in range(instance.n)),
        *(abs(acceptances[j] * reduced_cost_slack[j]) for j in range(instance.n)),
    )
    shadow_disagreement = max(
        0.0,
        *(abs(prices[i] - primal_shadow_prices[i]) for i in range(instance.m)),
        *(abs(demand_prices[j] - primal_demand_prices[j]) for j in range(instance.n)),
    )
    gap = abs(primal_objective - dual_objective)
    if gap > 1e-6 * max(1.0, abs(primal_objective), abs(dual_objective)):
        raise RuntimeError(f"fluid primal/dual disagreement {gap:.3g}")

    return FluidLPSolution(
        primal_objective=primal_objective,
        dual_objective=dual_objective,
        acceptances=acceptances,
        prices=prices,
        demand_prices=demand_prices,
        primal_status=primal_status,
        dual_status=dual_status,
        primal_runtime_seconds=primal_runtime,
        dual_runtime_seconds=dual_runtime,
        primal_iterations=primal_iterations,
        dual_iterations=dual_iterations,
        gurobi_version=".".join(map(str, gp.gurobi.version())),
        optimality_tolerance=optimality_tolerance,
        feasibility_tolerance=feasibility_tolerance,
        primal_violation=primal_violation,
        dual_violation=dual_violation,
        duality_gap=gap,
        complementarity_residual=complementarity,
        shadow_price_disagreement=shadow_disagreement,
    )


def static_bid_price_accept(
    instance: NetworkInstance,
    remaining: tuple[int, ...],
    j: int,
    prices: tuple[float, ...],
    *,
    tie_accept: bool = True,
    tolerance: float = 1e-9,
) -> bool:
    """Implement a *fixed-solve* fluid bid-price acceptance test.

    A feasible class-j request is accepted when ``f_j >= A_j^T λ`` if
    ``tie_accept`` is true, or only when strictly greater otherwise. The
    caller chooses the tie convention because equality can materially
    affect policy reward. This rule never consumes unavailable capacity.
    It is not Adelman's dynamic next-period affine price rule.
    """
    if len(prices) != instance.m:
        raise ValueError("one resource price is required per resource")
    if tolerance < 0:
        raise ValueError("tolerance must be nonnegative")
    if not instance.feasible(remaining, j):
        return False
    opportunity_cost = math.fsum(instance.A[i][j] * prices[i] for i in range(instance.m))
    if tie_accept:
        return instance.f[j] >= opportunity_cost - tolerance
    return instance.f[j] > opportunity_cost + tolerance
