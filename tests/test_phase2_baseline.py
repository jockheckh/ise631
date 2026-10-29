"""Small independent checks for the bounded exact/fluid baseline.

The non-Gurobi tests are analytical or pure-Python and can run even when a
solver license is unavailable. The fluid tests intentionally require an
actually usable Gurobi license in the current Windows interpreter; they must
not be silently skipped or replaced by another solver. Agreement on these
toys supports implementation verification, not a general theorem proof.
"""

from dataclasses import FrozenInstanceError
import math

import pytest

from src.adelman.exact_dp import ExactDP, evaluate_policy_exact
from src.adelman.fluid_lp import solve_fluid_lp, static_bid_price_accept
from src.adelman.instances import (
    NetworkInstance,
    generate_hub_spoke_2007_inspired,
    published_capacity_per_leg,
)


def example_1() -> NetworkInstance:
    """Adelman (2007), Example 1, printed p. 653."""
    return NetworkInstance(
        T=2, m=1, n=1, c=(1,), A=((1,),), f=(1.0,),
        p=((0.5,), (0.5,)), name="adelman_example_1",
        provenance="Adelman (2007), Example 1, p. 653",
    )


def test_example_1_exact_dp_and_exact_policy_evaluation() -> None:
    instance = example_1()
    oracle = ExactDP(instance)
    # The request is accepted if it arrives in either period; the only
    # zero-reward path is no arrival twice, with probability (1/2)^2.
    assert oracle.initial_value() == pytest.approx(0.75)
    assert oracle.value(3, (0,)) == 0
    assert oracle.optimal_accept(1, (1,), 0)
    assert oracle.optimal_accept(2, (1,), 0)
    assert not oracle.optimal_accept(2, (0,), 0)
    assert evaluate_policy_exact(instance, oracle.optimal_accept) == pytest.approx(0.75)


def test_zero_demand_zero_capacity_and_terminal_boundary() -> None:
    no_demand = NetworkInstance(
        T=2, m=1, n=1, c=(1,), A=((1,),), f=(7.0,),
        p=((0.0,), (0.0,)), name="zero_demand",
    )
    assert ExactDP(no_demand).initial_value() == 0
    assert no_demand.no_arrival_probability(1) == 1

    # Zero capacity is a deliberate implementation edge case outside the
    # source's strictly positive-capacity premise for structural theorems.
    no_capacity = NetworkInstance(
        T=1, m=1, n=1, c=(0,), A=((1,),), f=(7.0,), p=((1.0,),),
        name="zero_capacity_boundary",
    )
    assert ExactDP(no_capacity).initial_value() == 0
    assert not static_bid_price_accept(no_capacity, (0,), 0, (0.0,))

    terminal_sale = NetworkInstance(
        T=1, m=1, n=1, c=(1,), A=((1,),), f=(7.0,), p=((1.0,),),
        name="terminal_sale",
    )
    assert ExactDP(terminal_sale).initial_value() == 7.0
    assert ExactDP(terminal_sale).optimal_accept(1, (1,), 0)

    # Capacity is abundant relative to at most two potential purchases.
    loose_capacity = NetworkInstance(
        T=2, m=1, n=1, c=(10,), A=((1,),), f=(7.0,),
        p=((0.5,), (0.5,)), name="loose_capacity",
    )
    assert ExactDP(loose_capacity).initial_value() == pytest.approx(7.0)


def test_two_resource_opportunity_cost_and_coupled_feasibility() -> None:
    # At t=1 a single-leg $4 request certainly arrives; at t=2 a $10
    # request for *both* legs certainly arrives. The exact policy rejects
    # either early request despite its positive immediate revenue.
    instance = NetworkInstance(
        T=2, m=2, n=3, c=(1, 1),
        A=((1, 0, 1), (0, 1, 1)), f=(4.0, 4.0, 10.0),
        p=((0.5, 0.5, 0.0), (0.0, 0.0, 1.0)),
        name="two_resource_opportunity_cost",
    )
    oracle = ExactDP(instance)
    assert oracle.initial_value() == pytest.approx(10.0)
    assert not oracle.optimal_accept(1, (1, 1), 0)
    assert not oracle.optimal_accept(1, (1, 1), 1)
    assert oracle.optimal_accept(2, (1, 1), 2)
    assert not instance.feasible((0, 1), 2)


def test_exact_policy_evaluation_detects_capacity_violation() -> None:
    instance = example_1()
    with pytest.raises(ValueError, match="infeasible"):
        evaluate_policy_exact(instance, lambda t, r, j: True)


def test_static_bid_price_rule_feasibility_and_ties() -> None:
    instance = example_1()
    assert static_bid_price_accept(instance, (1,), 0, (1.0,), tie_accept=True)
    assert not static_bid_price_accept(instance, (1,), 0, (1.0,), tie_accept=False)
    assert static_bid_price_accept(instance, (1,), 0, (0.4,))
    assert not static_bid_price_accept(instance, (1,), 0, (2.0,))
    assert not static_bid_price_accept(instance, (0,), 0, (0.0,))


def test_network_data_are_deeply_immutable_and_validated() -> None:
    source_c = [1]
    source_A = [[1]]
    source_p = [[0.5]]
    instance = NetworkInstance(
        T=1, m=1, n=1, c=source_c, A=source_A, f=[2.0], p=source_p
    )
    source_c[0] = 9
    source_A[0][0] = 9
    source_p[0][0] = 0
    assert instance.c == (1,)
    assert instance.A == ((1,),)
    assert instance.p == ((0.5,),)
    with pytest.raises(FrozenInstanceError):
        instance.T = 3
    with pytest.raises(ValueError, match="exceed one"):
        NetworkInstance(T=1, m=1, n=2, c=(1,), A=((1, 1),),
                        f=(1.0, 1.0), p=((0.6, 0.5),))
    with pytest.raises(ValueError, match="exceed one"):
        # Even a 1e-13 excess must not yield an overfull transition kernel.
        NetworkInstance(T=1, m=1, n=2, c=(1,), A=((1, 1),),
                        f=(1.0, 1.0), p=((0.6, 0.4000000000001),))
    with pytest.raises(ValueError, match="nonnegative integer"):
        NetworkInstance(T=1, m=1, n=1, c=(1.5,), A=((1,),),
                        f=(1.0,), p=((0.5,),))


def test_source_stated_table_2_capacity_lookup() -> None:
    # The lookup matches printed p. 656, but original random demand draws
    # are unavailable; using these capacities cannot reproduce table loads.
    assert published_capacity_per_leg(spokes=2, horizon=20) == 3
    assert published_capacity_per_leg(spokes=20, horizon=1000) == 24
    assert published_capacity_per_leg(spokes=10, horizon=200) == 9
    with pytest.raises(ValueError, match="Table 2"):
        published_capacity_per_leg(spokes=3, horizon=20)


def test_synthetic_generator_dimensions_topology_probabilities_and_seed() -> None:
    a = generate_hub_spoke_2007_inspired(
        spokes=2, horizon=3, capacity_per_leg=2, seed=127
    )
    b = generate_hub_spoke_2007_inspired(
        spokes=2, horizon=3, capacity_per_leg=2, seed=127
    )
    other = generate_hub_spoke_2007_inspired(
        spokes=2, horizon=3, capacity_per_leg=2, seed=128
    )
    assert a == b
    assert (a.f, a.p) != (other.f, other.p)
    assert (a.m, a.n, a.T) == (4, 12, 3)
    assert a.c == (2, 2, 2, 2)
    assert "synthetic" in a.provenance
    assert "Uniform(0,1)" in a.provenance
    for t in range(1, a.T + 1):
        assert math.fsum(a.p[t - 1]) == pytest.approx(0.8)
        assert a.no_arrival_probability(t) == pytest.approx(0.2)

    # Class order is low/high for H->1, 1->H, H->2, 2->H,
    # 1->H->2, 2->H->1. Check directed two-leg incidence explicitly.
    assert tuple(a.A[i][8] for i in range(4)) == (0, 1, 1, 0)
    assert tuple(a.A[i][10] for i in range(4)) == (1, 0, 0, 1)
    for j in range(0, a.n, 2):
        assert 15 <= a.f[j] <= 49
        assert a.f[j + 1] == 5 * a.f[j]
        assert a.p[0][j] / a.p[0][j + 1] == pytest.approx(3.0)


def test_example_1_fluid_primal_dual_and_static_policy() -> None:
    instance = example_1()
    result = solve_fluid_lp(instance)
    assert result.primal_status == 2  # Gurobi GRB.OPTIMAL
    assert result.dual_status == 2
    assert result.primal_objective == pytest.approx(1.0)
    assert result.dual_objective == pytest.approx(1.0)
    assert result.duality_gap < 1e-7
    assert result.primal_violation < 1e-7
    assert result.dual_violation < 1e-7
    assert result.complementarity_residual < 1e-7
    assert result.prices[0] >= -1e-9
    static_reward = evaluate_policy_exact(
        instance,
        lambda t, r, j: static_bid_price_accept(instance, r, j, result.prices),
    )
    assert static_reward == pytest.approx(0.75)
    assert static_reward <= ExactDP(instance).initial_value() + 1e-9


def test_low_now_high_later_fluid_and_static_policy() -> None:
    # Hand check: low fare 1 arrives with probability .4 now; high fare 3
    # arrives with probability .4 next period. Exact DP rejects low now:
    # keeping the seat is worth .4 * 3 = 1.2, exceeding today's fare 1.
    # Fluid LP expects .4 of each class, uses .8 < 1 seat, and gives 1.6.
    # Its unique resource price is λ=0; static BPC therefore accepts low,
    # earning .4*1 + (1-.4)*.4*3 = 1.12 in exact expectation.
    instance = NetworkInstance(
        T=2, m=1, n=2, c=(1,), A=((1, 1),), f=(1.0, 3.0),
        p=((0.4, 0.0), (0.0, 0.4)), name="low_now_high_later",
        provenance="hand-constructed synthetic verification case",
    )
    oracle = ExactDP(instance)
    assert oracle.initial_value() == pytest.approx(1.2)
    assert not oracle.optimal_accept(1, (1,), 0)
    result = solve_fluid_lp(instance)
    assert result.primal_objective == pytest.approx(1.6)
    assert result.dual_objective == pytest.approx(1.6)
    assert result.prices[0] == pytest.approx(0.0, abs=1e-8)
    reward = evaluate_policy_exact(
        instance,
        lambda t, r, j: static_bid_price_accept(instance, r, j, result.prices),
    )
    assert reward == pytest.approx(1.12)


def test_fluid_zero_demand_and_capacity_boundaries() -> None:
    no_demand = NetworkInstance(
        T=1, m=1, n=1, c=(1,), A=((1,),), f=(7.0,), p=((0.0,),),
        name="zero_demand_fluid",
    )
    no_capacity = NetworkInstance(
        T=1, m=1, n=1, c=(0,), A=((1,),), f=(7.0,), p=((1.0,),),
        name="zero_capacity_fluid",
    )
    assert solve_fluid_lp(no_demand).primal_objective == pytest.approx(0.0)
    assert solve_fluid_lp(no_capacity).primal_objective == pytest.approx(0.0)


def test_multiresource_fluid_coupling_and_duality() -> None:
    # Two single-leg classes and one both-leg class. For stationary
    # p=(.4,.4,.2) over two periods, demand caps are (.8,.8,.4).
    # A primal witness Y=(.6,.6,.4) earns 8.8; a dual witness
    # lambda=(4,4), mu=(0,0,2) costs 8.8. Weak duality proves these
    # hand-constructed witnesses are both optimal. Do not require the
    # solver to return these exact multipliers under degeneracy.
    instance = NetworkInstance(
        T=2, m=2, n=3, c=(1, 1),
        A=((1, 0, 1), (0, 1, 1)), f=(4.0, 4.0, 10.0),
        p=((0.4, 0.4, 0.2), (0.4, 0.4, 0.2)),
        name="coupled_resource_fluid",
        provenance="hand-constructed synthetic LP duality witness",
    )
    result = solve_fluid_lp(instance)
    assert result.primal_objective == pytest.approx(8.8)
    assert result.dual_objective == pytest.approx(8.8)
    assert result.primal_violation < 1e-7
    assert result.dual_violation < 1e-7
    assert result.duality_gap < 1e-7
    assert result.complementarity_residual < 1e-7
