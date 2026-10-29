"""Independent, pure-Python oracle for Adelman (2007), equations (1)-(2).

The exact dynamic program is deliberately separate from any Gurobi model.
Agreement between two independently implemented formulations is useful
evidence that indexing, transition, and feasibility rules are correct;
agreement is not a proof of the paper's theorems.  State-space growth makes
these routines suitable only for small, explicitly bounded instances.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Callable

from .instances import NetworkInstance


# A policy observes the class that actually arrived, the current period,
# and the remaining prearrival capacities. It returns an accept/reject bit.
AcceptRule = Callable[[int, tuple[int, ...], int], bool]


class ExactDP:
    """Backward Bellman recursion for the source finite-horizon MDP.

    The source's prearrival action vector ``u`` specifies one decision for
    *each possible* class, yet only one class can arrive. Consequently the
    action maximization separates by class: for each feasible arrival, take
    the larger of today's fare plus next-state value and rejection's
    unchanged-state value. This is exactly equation (1), not a relaxation.

    The memoized recursion visits only states reachable from requested
    states. ``value(1, instance.c)`` is the exact optimal expected revenue.
    """

    def __init__(self, instance: NetworkInstance) -> None:
        self.instance = instance

    @lru_cache(maxsize=None)
    def value(self, t: int, remaining: tuple[int, ...]) -> float:
        """Return ``v_t(remaining)``; ``v_(T+1)`` is identically zero."""
        problem = self.instance
        if not 1 <= t <= problem.T + 1:
            raise ValueError("period t must be in 1..T+1")
        if len(remaining) != problem.m or any(
            isinstance(r, bool) or not isinstance(r, int) or r < 0 or r > problem.c[i]
            for i, r in enumerate(remaining)
        ):
            raise ValueError("remaining state must be an integer vector within initial capacity")
        if t == problem.T + 1:
            return 0.0

        continuation = self.value(t + 1, remaining)
        total = problem.no_arrival_probability(t) * continuation
        for j, probability in enumerate(problem.p[t - 1]):
            if probability == 0:
                continue
            if problem.feasible(remaining, j):
                accepted_state = problem.after_acceptance(remaining, j)
                accept_value = problem.f[j] + self.value(t + 1, accepted_state)
                total += probability * max(accept_value, continuation)
            else:
                # An infeasible arrival may still occur; it is rejected and
                # the next period begins with exactly the same capacities.
                total += probability * continuation
        return total

    def initial_value(self) -> float:
        """Exact benchmark ``v_1(c)`` (not an LP upper-bound estimate)."""
        return self.value(1, self.instance.c)

    def optimal_accept(
        self, t: int, remaining: tuple[int, ...], j: int, *, tolerance: float = 1e-12
    ) -> bool:
        """Apply the exact opportunity-cost decision after a class arrives.

        A tie is accepted. The opportunity cost is
        ``v_(t+1)(r) - v_(t+1)(r-A_j)``; the intercept or today's value does
        not enter. The tolerance only absorbs floating-point noise.
        """
        if not 1 <= t <= self.instance.T or not 0 <= j < self.instance.n:
            raise ValueError("period or class index is invalid")
        if tolerance < 0:
            raise ValueError("tolerance must be nonnegative")
        if not self.instance.feasible(remaining, j):
            return False
        opportunity_cost = self.value(t + 1, remaining) - self.value(
            t + 1, self.instance.after_acceptance(remaining, j)
        )
        return self.instance.f[j] >= opportunity_cost - tolerance


def evaluate_policy_exact(instance: NetworkInstance, accept: AcceptRule) -> float:
    """Calculate a fixed policy's *exact* expectation on a small instance.

    This performs probability-weighted recursion over all arrival branches,
    including no-arrival and infeasible-arrival branches. It introduces no
    Monte Carlo error and does not use Gurobi. A policy that attempts to
    consume unavailable capacity raises an error rather than being silently
    repaired; the latter would hide a serious implementation defect.
    """

    @lru_cache(maxsize=None)
    def reward(t: int, remaining: tuple[int, ...]) -> float:
        if t == instance.T + 1:
            return 0.0
        unchanged_value = reward(t + 1, remaining)
        expected = instance.no_arrival_probability(t) * unchanged_value
        for j, probability in enumerate(instance.p[t - 1]):
            if probability == 0:
                continue
            decision = accept(t, remaining, j)
            if decision and not instance.feasible(remaining, j):
                raise ValueError(f"policy accepted infeasible class {j} in period {t}")
            if decision:
                after = instance.after_acceptance(remaining, j)
                expected += probability * (instance.f[j] + reward(t + 1, after))
            else:
                expected += probability * unchanged_value
        return expected

    return reward(1, instance.c)
