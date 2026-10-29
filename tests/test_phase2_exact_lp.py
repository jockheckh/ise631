"""Exact source Bellman/occupancy LP checks against a separate action tree.

Solver tests are intentionally not skipped if Gurobi or its license fails:
the Windows preflight and licensed-user suite must reveal that condition.
The brute-force verifier below is pure Python and does not call ExactDP's
feasibility/transition helpers or the LP module's enumeration functions.
"""

from functools import lru_cache
from itertools import product
import math

import pytest

from src.adelman.exact_dp import ExactDP
from src.adelman.exact_lp import solve_exact_lp
from src.adelman.instances import NetworkInstance


def _example_1() -> NetworkInstance:
    """Adelman (2007), Example 1, printed p. 653."""
    return NetworkInstance(
        T=2, m=1, n=1, c=(1,), A=((1,),), f=(1.0,),
        p=((0.5,), (0.5,)), name="adelman_example_1",
        provenance="Adelman (2007), Example 1, printed p. 653",
    )


def _two_resource_case() -> NetworkInstance:
    """Hand-checkable opportunity-cost case with a both-resource class."""
    return NetworkInstance(
        T=2, m=2, n=3, c=(1, 1),
        A=((1, 0, 1), (0, 1, 1)), f=(4.0, 4.0, 10.0),
        p=((0.5, 0.5, 0.0), (0.0, 0.0, 1.0)),
        name="two_resource_high_later",
        provenance="independent hand-constructed synthetic verification",
    )


def exhaustive_action_tree(instance: NetworkInstance, *, max_pairs: int = 10000) -> float:
    """Optimize by testing *every* n-bit prearrival action on tiny states.

    Unlike ExactDP, this implementation does not separate decisions by
    arrival class and does not call ``instance.feasible`` or
    ``instance.after_acceptance``.  It enumerates policy actions, rejects
    vectors that mark an infeasible class, and weights all request/no-request
    branches directly.  Memoization avoids recomputing the same future
    state, but every feasible action at each visited state is still tested.
    A conservative combinatorial bound fails before exploring a large tree.
    """
    potential_pairs = instance.T * math.prod(c + 1 for c in instance.c) * (1 << instance.n)
    if potential_pairs > max_pairs:
        raise ValueError("exhaustive action tree would exceed max_pairs")

    @lru_cache(maxsize=None)
    def value(t: int, r: tuple[int, ...]) -> float:
        if t == instance.T + 1:
            return 0.0
        best = -math.inf
        no_arrival = 1.0 - math.fsum(instance.p[t - 1])
        for u in product((0, 1), repeat=instance.n):
            if any(
                u[j] and any(instance.A[i][j] > r[i] for i in range(instance.m))
                for j in range(instance.n)
            ):
                continue
            candidate = no_arrival * value(t + 1, r)
            for j, probability in enumerate(instance.p[t - 1]):
                if not probability:
                    continue
                if u[j]:
                    after = tuple(r[i] - instance.A[i][j] for i in range(instance.m))
                    candidate += probability * (instance.f[j] + value(t + 1, after))
                else:
                    candidate += probability * value(t + 1, r)
            best = max(best, candidate)
        return best

    return value(1, instance.c)


@pytest.mark.parametrize("instance,expected", [
    (_example_1(), 0.75),
    (_two_resource_case(), 10.0),
    (NetworkInstance(
        T=1, m=1, n=1, c=(1,), A=((1,),), f=(7.0,), p=((1.0,),),
        name="terminal_sale",
    ), 7.0),
    (NetworkInstance(
        T=2, m=1, n=1, c=(1,), A=((1,),), f=(7.0,),
        p=((0.0,), (0.0,)), name="zero_demand",
    ), 0.0),
])
def test_brute_action_tree_and_exact_dp_agree_without_solver(
    instance: NetworkInstance, expected: float
) -> None:
    assert exhaustive_action_tree(instance) == pytest.approx(expected, abs=1e-10)
    assert ExactDP(instance).initial_value() == pytest.approx(expected, abs=1e-10)


def test_brute_action_tree_guard_fails_loudly() -> None:
    with pytest.raises(ValueError, match="max_pairs"):
        exhaustive_action_tree(_two_resource_case(), max_pairs=1)


@pytest.mark.parametrize("instance,expected", [
    (_example_1(), 0.75),
    (_two_resource_case(), 10.0),
    (NetworkInstance(
        T=1, m=1, n=1, c=(1,), A=((1,),), f=(7.0,), p=((1.0,),),
        name="terminal_sale_lp",
    ), 7.0),
    (NetworkInstance(
        T=2, m=1, n=1, c=(1,), A=((1,),), f=(7.0,),
        p=((0.0,), (0.0,)), name="zero_demand_lp",
    ), 0.0),
    (NetworkInstance(
        T=1, m=1, n=1, c=(0,), A=((1,),), f=(7.0,), p=((1.0,),),
        name="zero_capacity_lp",
    ), 0.0),
])
def test_bellman_occupancy_and_independent_oracles_agree(
    instance: NetworkInstance, expected: float
) -> None:
    result = solve_exact_lp(instance)
    assert result.primal_status == 2  # Gurobi GRB.OPTIMAL
    assert result.dual_status == 2
    assert result.primal_objective == pytest.approx(expected, abs=1e-8)
    assert result.dual_objective == pytest.approx(expected, abs=1e-8)
    assert result.primal_objective == pytest.approx(ExactDP(instance).initial_value(), abs=1e-8)
    assert result.dual_objective == pytest.approx(exhaustive_action_tree(instance), abs=1e-8)
    assert result.primal_violation < 1e-7
    assert result.dual_violation < 1e-7
    assert result.flow_residual < 1e-7
    assert result.duality_gap < 1e-7
    assert result.complementarity_residual < 1e-7
    assert result.primal_variables == result.state_count
    assert result.primal_constraints == result.state_action_count
    assert result.dual_variables == result.state_action_count
    assert result.dual_constraints == result.state_count


def test_example_1_state_flow_and_complementarity() -> None:
    result = solve_exact_lp(_example_1())
    # At t=1 accepting a request is the optimal prearrival action. Its
    # occupancy is one. At t=2 half the paths have r=0, half have r=1.
    assert result.occupancy[(1, (1,), (1,))] == pytest.approx(1.0)
    assert sum(mass for (t, r, _), mass in result.occupancy.items() if t == 2 and r == (0,)) == pytest.approx(0.5)
    assert sum(mass for (t, r, _), mass in result.occupancy.items() if t == 2 and r == (1,)) == pytest.approx(0.5)
    assert result.value_function[(1, (1,))] == pytest.approx(0.75)
    assert result.state_count == 3  # R1={(1,)}, R2={(0,),(1,)}
    assert result.state_action_count == 5  # 2 actions, then 1+2 actions


def test_three_period_occupancy_flow_tracks_survival_probability() -> None:
    # With one seat and one unit-fare class, accepting every feasible
    # arrival is optimal.  The seat survives to t=2 iff no arrival occurs
    # at t=1 (probability .9), and to t=3 iff neither of the first two
    # periods sees an arrival (.9*.8=.72).  The exact reward is the chance
    # of at least one arrival: 1-(.9*.8*.7)=.496.  These state masses check
    # transition timing independently of LP objective equality.
    instance = NetworkInstance(
        T=3, m=1, n=1, c=(1,), A=((1,),), f=(1.0,),
        p=((0.1,), (0.2,), (0.3,)), name="three_period_flow",
        provenance="independent analytical probability-flow verification",
    )
    result = solve_exact_lp(instance)
    assert result.primal_objective == pytest.approx(0.496, abs=1e-9)
    assert result.dual_objective == pytest.approx(0.496, abs=1e-9)
    assert ExactDP(instance).initial_value() == pytest.approx(0.496, abs=1e-9)
    assert exhaustive_action_tree(instance) == pytest.approx(0.496, abs=1e-9)
    available_t2 = sum(
        mass for (t, r, _), mass in result.occupancy.items() if t == 2 and r == (1,)
    )
    available_t3 = sum(
        mass for (t, r, _), mass in result.occupancy.items() if t == 3 and r == (1,)
    )
    assert available_t2 == pytest.approx(0.9, abs=1e-9)
    assert available_t3 == pytest.approx(0.72, abs=1e-9)
    assert result.occupancy[(1, (1,), (1,))] == pytest.approx(1.0, abs=1e-9)
    assert result.flow_residual < 1e-8
    assert result.complementarity_residual < 1e-8


def test_actions_are_individually_feasible_not_collectively_consuming() -> None:
    # Both products use the same single remaining seat, but only one class
    # can arrive. The prearrival action u=(1,1) is feasible and earns 1 with
    # certainty. A wrong sum_j a_ij*u_j <= r_i check would rule it out.
    instance = NetworkInstance(
        T=1, m=1, n=2, c=(1,), A=((1, 1),), f=(1.0, 1.0),
        p=((0.5, 0.5),), name="individually_feasible_actions",
        provenance="independent action-feasibility boundary case",
    )
    assert exhaustive_action_tree(instance) == pytest.approx(1.0)
    result = solve_exact_lp(instance)
    assert result.primal_objective == pytest.approx(1.0)
    assert result.dual_objective == pytest.approx(1.0)
    assert result.state_action_count == 4
    assert result.occupancy[(1, (1,), (1, 1))] == pytest.approx(1.0)


def test_full_enumeration_guard_does_not_silently_truncate() -> None:
    instance = _two_resource_case()
    with pytest.raises(ValueError, match="max_states"):
        solve_exact_lp(instance, max_states=1)
    with pytest.raises(ValueError, match="max_state_action_pairs"):
        solve_exact_lp(instance, max_state_action_pairs=1)
