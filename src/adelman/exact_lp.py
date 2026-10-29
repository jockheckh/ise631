"""Enumerated exact Bellman LP and its independently constructed occupancy dual.

Adelman (2007), equation (3), printed p. 649, calls the exact value-function
minimization LP ``D0``.  Its (unlabeled in the paper) LP dual has nonnegative
state-action occupancy variables and *statewise* probability-flow equations.
This is a finite-horizon, undiscounted model, not the instructor's separate
generic discounted-MDP occupancy LP.

These models are intentionally limited to tiny instances.  We enumerate the
full capacity box after period 1, even when some states are unreachable; this
matches the paper's state sets.  Explicit size guards raise rather than
silently truncate states, actions, or Bellman inequalities.  LP/MIP solving
uses Gurobi; the independent exact-DP oracle in ``exact_dp.py`` uses none.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import math

from .instances import NetworkInstance


State = tuple[int, ...]
Action = tuple[int, ...]
StateKey = tuple[int, State]
ColumnKey = tuple[int, State, Action]


@dataclass(frozen=True)
class ExactLPSolution:
    """Objectives, dimensions, and directly recomputed LP residuals.

    ``value_function`` contains the Gurobi D0 solution, including states not
    reached by its optimal policy.  ``occupancy`` contains every dual column,
    including zeros.  A positive occupancy and a tight matching Bellman row
    illustrate complementary slackness; neither implies a unique action at
    an unvisited state.  ``primal_violation`` is the largest violated Bellman
    inequality; ``flow_residual`` includes every initial/transition equality;
    ``dual_violation`` also checks nonnegativity of occupancy variables.
    """

    primal_objective: float
    dual_objective: float
    value_function: dict[StateKey, float]
    occupancy: dict[ColumnKey, float]
    primal_status: int
    dual_status: int
    primal_runtime_seconds: float
    dual_runtime_seconds: float
    primal_iterations: float
    dual_iterations: float
    state_count: int
    state_action_count: int
    primal_variables: int
    primal_constraints: int
    dual_variables: int
    dual_constraints: int
    gurobi_version: str
    optimality_tolerance: float
    feasibility_tolerance: float
    primal_violation: float
    dual_violation: float
    flow_residual: float
    duality_gap: float
    complementarity_residual: float


def _enumerate_space(
    instance: NetworkInstance, *, max_states: int, max_state_action_pairs: int
) -> tuple[dict[int, tuple[State, ...]], dict[StateKey, tuple[Action, ...]], int, int]:
    """Materialize exactly R_1={c}, R_t=full capacity box (t>=2), U(r).

    U(r) consists of all binary prearrival acceptance vectors whose *each*
    marked class is individually feasible: a_ij*u_j <= r_i for all i,j.
    Summing class consumption would be wrong because at most one class
    arrives.  Count before materializing to avoid accidental giant models.
    """
    for label, limit in (("max_states", max_states), ("max_state_action_pairs", max_state_action_pairs)):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError(f"{label} must be a positive integer")

    box_size = math.prod(capacity + 1 for capacity in instance.c)
    state_count = 1 + (instance.T - 1) * box_size
    if state_count > max_states:
        raise ValueError(
            f"exact LP requires {state_count} time-states, exceeding max_states={max_states}; "
            "refusing to truncate the source model"
        )

    # A tuple is materialized only after the full-box count has passed, and
    # only when a second period exists.  For T=1 the paper uses just {c};
    # materializing a huge irrelevant capacity box would violate that spirit.
    capacity_box = (
        tuple(product(*(range(capacity + 1) for capacity in instance.c)))
        if instance.T >= 2 else ()
    )
    states: dict[int, tuple[State, ...]] = {1: (instance.c,)}
    for t in range(2, instance.T + 1):
        states[t] = capacity_box

    actions: dict[StateKey, tuple[Action, ...]] = {}
    pair_count = 0
    for t in range(1, instance.T + 1):
        for r in states[t]:
            feasible_classes = tuple(
                j for j in range(instance.n)
                if all(instance.A[i][j] <= r[i] for i in range(instance.m))
            )
            count_here = 1 << len(feasible_classes)
            pair_count += count_here
            if pair_count > max_state_action_pairs:
                raise ValueError(
                    f"exact LP requires more than max_state_action_pairs={max_state_action_pairs}; "
                    "refusing to omit Bellman rows or dual columns"
                )
            # Enumerating only feasible-class bits still creates an n-long
            # source action vector, with zero bits for infeasible classes.
            state_actions: list[Action] = []
            for bits in product((0, 1), repeat=len(feasible_classes)):
                u = [0] * instance.n
                for j, bit in zip(feasible_classes, bits):
                    u[j] = bit
                state_actions.append(tuple(u))
            actions[(t, r)] = tuple(state_actions)
    return states, actions, state_count, pair_count


def _stage_reward(instance: NetworkInstance, t: int, u: Action) -> float:
    """Expected immediate revenue q_t(r,u), independent of r once feasible."""
    return math.fsum(instance.p[t - 1][j] * instance.f[j] * u[j] for j in range(instance.n))


def _transition_probabilities(
    instance: NetworkInstance, t: int, r: State, u: Action
) -> dict[State, float]:
    """Construct P_t(s|r,u) independently of Gurobi expressions.

    No-arrival and rejected requests both preserve r.  The direct tuple
    subtraction intentionally does not reuse ExactDP's state-transition
    helper, allowing its LP comparison to catch some implementation errors.
    """
    transitions: dict[State, float] = {r: instance.no_arrival_probability(t)}
    for j, probability in enumerate(instance.p[t - 1]):
        if probability == 0:
            continue
        destination = (
            tuple(r[i] - instance.A[i][j] for i in range(instance.m))
            if u[j] else r
        )
        transitions[destination] = transitions.get(destination, 0.0) + probability
    return transitions


def solve_exact_lp(
    instance: NetworkInstance, *, max_states: int = 1000,
    max_state_action_pairs: int = 5000,
) -> ExactLPSolution:
    """Solve exact D0 and a separately assembled state-action occupancy LP.

    D0 minimizes free ``v_1(c)`` subject to, for every source time-state and
    feasible prearrival action, ``v_t(r) >= q_t(r,u) + E[v_(t+1)(R')]``;
    ``v_(T+1)=0``.  The dual maximizes ``sum q*x`` over ``x>=0`` with
    ``sum_u x_1(c,u)=1`` and, for later states, outgoing occupancy equal to
    previous-period incoming probability.  The dual constraints are coded
    as flow equations rather than inferred from Gurobi's primal row prices.

    Only OPTIMAL LP statuses are accepted; a license or model-size failure is
    surfaced to the caller.  Reported residuals are recomputed from numeric
    solutions and source equations, not inferred solely from solver status.
    """
    states, actions, state_count, pair_count = _enumerate_space(
        instance, max_states=max_states, max_state_action_pairs=max_state_action_pairs
    )
    # Perform the finite-size guard before importing/starting a solver. A
    # caller can therefore identify a model-size error independently of
    # whether the selected Windows interpreter has a usable Gurobi license.
    import gurobipy as gp

    with gp.Env(empty=True) as environment:
        environment.setParam("OutputFlag", 0)
        environment.setParam("Threads", 1)
        environment.start()

        # Bellman inequalities (D0).  No bound v>=0 is imposed: in the
        # source LP all value variables are free, and the inequalities plus
        # objective identify the initial optimal value.
        with gp.Model("adelman_exact_D0", env=environment) as primal:
            v = {
                (t, r): primal.addVar(lb=-gp.GRB.INFINITY, name=f"v_{t}_{'_'.join(map(str, r))}")
                for t in range(1, instance.T + 1) for r in states[t]
            }
            for t in range(1, instance.T + 1):
                for r in states[t]:
                    for u in actions[(t, r)]:
                        rhs = gp.LinExpr(_stage_reward(instance, t, u))
                        if t < instance.T:
                            # This continuation is constructed directly
                            # from each request branch, not from dual rows.
                            rhs += instance.no_arrival_probability(t) * v[(t + 1, r)]
                            for j, probability in enumerate(instance.p[t - 1]):
                                if probability == 0:
                                    continue
                                destination = (
                                    tuple(r[i] - instance.A[i][j] for i in range(instance.m))
                                    if u[j] else r
                                )
                                rhs += probability * v[(t + 1, destination)]
                        primal.addConstr(
                            v[(t, r)] >= rhs,
                            name=f"bellman_{t}_{'_'.join(map(str, r))}_{''.join(map(str, u))}",
                        )
            primal.setObjective(v[(1, instance.c)], gp.GRB.MINIMIZE)
            primal.optimize()
            if primal.Status != gp.GRB.OPTIMAL:
                raise RuntimeError(f"exact D0 Gurobi status {primal.Status}, not OPTIMAL")
            primal_status = int(primal.Status)
            primal_objective = float(primal.ObjVal)
            values = {key: float(variable.X) for key, variable in v.items()}
            primal_runtime = float(primal.Runtime)
            primal_iterations = float(primal.IterCount)
            primal_variables = int(primal.NumVars)
            primal_constraints = int(primal.NumConstrs)
            optimality_tolerance = float(primal.Params.OptimalityTol)
            feasibility_tolerance = float(primal.Params.FeasibilityTol)

        # Occupancy dual.  A nonnegative x_t(r,u) is the probability of
        # occupying prearrival state r and selecting u in period t.  Because
        # v_t(r) is free in D0, its Lagrangian coefficient must equal zero:
        # outgoing mass - incoming mass = initial unit mass at (1,c).
        with gp.Model("adelman_exact_occupancy", env=environment) as dual:
            x = {
                (t, r, u): dual.addVar(lb=0.0, name=f"x_{t}_{'_'.join(map(str, r))}_{''.join(map(str, u))}")
                for t in range(1, instance.T + 1)
                for r in states[t]
                for u in actions[(t, r)]
            }
            incoming: dict[StateKey, gp.LinExpr] = {
                (t, r): gp.LinExpr()
                for t in range(2, instance.T + 1) for r in states[t]
            }
            for t in range(1, instance.T):
                for r in states[t]:
                    for u in actions[(t, r)]:
                        # The probabilities are constructed independently
                        # from the primal's symbolic continuation terms.
                        for destination, probability in _transition_probabilities(instance, t, r, u).items():
                            incoming[(t + 1, destination)] += probability * x[(t, r, u)]
            for t in range(1, instance.T + 1):
                for r in states[t]:
                    outgoing = gp.quicksum(x[(t, r, u)] for u in actions[(t, r)])
                    if t == 1:
                        dual.addConstr(outgoing == 1.0, name="initial_mass")
                    else:
                        dual.addConstr(outgoing == incoming[(t, r)], name=f"flow_{t}_{'_'.join(map(str, r))}")
            dual.setObjective(
                gp.quicksum(
                    _stage_reward(instance, t, u) * x[(t, r, u)]
                    for t in range(1, instance.T + 1)
                    for r in states[t] for u in actions[(t, r)]
                ),
                gp.GRB.MAXIMIZE,
            )
            dual.optimize()
            if dual.Status != gp.GRB.OPTIMAL:
                raise RuntimeError(f"exact occupancy Gurobi status {dual.Status}, not OPTIMAL")
            dual_status = int(dual.Status)
            dual_objective = float(dual.ObjVal)
            occupancy = {key: float(variable.X) for key, variable in x.items()}
            dual_runtime = float(dual.Runtime)
            dual_iterations = float(dual.IterCount)
            dual_variables = int(dual.NumVars)
            dual_constraints = int(dual.NumConstrs)

    # Compute primal slack for *every* Bellman inequality, including those
    # for states that the optimal policy never reaches.  Numerically tiny
    # negative slacks are recorded as violations, not silently clipped out
    # of the model.  Complementarity is x times the matching row slack.
    slacks: dict[ColumnKey, float] = {}
    for t in range(1, instance.T + 1):
        for r in states[t]:
            for u in actions[(t, r)]:
                continuation = 0.0
                if t < instance.T:
                    continuation = math.fsum(
                        probability * values[(t + 1, destination)]
                        for destination, probability in _transition_probabilities(instance, t, r, u).items()
                    )
                slacks[(t, r, u)] = values[(t, r)] - _stage_reward(instance, t, u) - continuation
    primal_violation = max(0.0, *(-slack for slack in slacks.values()))

    # Recompute each dual conservation equation from the returned x values.
    # This provides an independent numerical diagnostic for wrong indices,
    # missing no-arrival mass, and accidental use of a discounted flow.
    incoming_numeric: dict[StateKey, float] = {
        (t, r): 0.0 for t in range(2, instance.T + 1) for r in states[t]
    }
    for t in range(1, instance.T):
        for r in states[t]:
            for u in actions[(t, r)]:
                mass = occupancy[(t, r, u)]
                for destination, probability in _transition_probabilities(instance, t, r, u).items():
                    incoming_numeric[(t + 1, destination)] += mass * probability
    flow_errors = []
    for t in range(1, instance.T + 1):
        for r in states[t]:
            outgoing = math.fsum(occupancy[(t, r, u)] for u in actions[(t, r)])
            target = 1.0 if t == 1 else incoming_numeric[(t, r)]
            flow_errors.append(abs(outgoing - target))
    flow_residual = max(flow_errors, default=0.0)
    dual_violation = max(flow_residual, 0.0, *(-mass for mass in occupancy.values()))
    complementarity = max(
        (abs(occupancy[key] * slack) for key, slack in slacks.items()), default=0.0
    )
    gap = abs(primal_objective - dual_objective)
    if gap > 1e-6 * max(1.0, abs(primal_objective), abs(dual_objective)):
        raise RuntimeError(f"exact Bellman/occupancy primal-dual disagreement {gap:.3g}")

    return ExactLPSolution(
        primal_objective=primal_objective,
        dual_objective=dual_objective,
        value_function=values,
        occupancy=occupancy,
        primal_status=primal_status,
        dual_status=dual_status,
        primal_runtime_seconds=primal_runtime,
        dual_runtime_seconds=dual_runtime,
        primal_iterations=primal_iterations,
        dual_iterations=dual_iterations,
        state_count=state_count,
        state_action_count=pair_count,
        primal_variables=primal_variables,
        primal_constraints=primal_constraints,
        dual_variables=dual_variables,
        dual_constraints=dual_constraints,
        gurobi_version=".".join(map(str, gp.gurobi.version())),
        optimality_tolerance=optimality_tolerance,
        feasibility_tolerance=feasibility_tolerance,
        primal_violation=primal_violation,
        dual_violation=dual_violation,
        flow_residual=flow_residual,
        duality_gap=gap,
        complementarity_residual=complementarity,
    )
