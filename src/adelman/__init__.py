"""Source-audited finite-horizon network revenue-management baselines.

The modules in this package implement bounded Phase 2 checks of Adelman
(2007).  They do not implement the affine approximate LP, column generation,
or any surveillance-pricing extension.
"""

from .instances import NetworkInstance, generate_hub_spoke_2007_inspired, published_capacity_per_leg
from .exact_dp import ExactDP, evaluate_policy_exact
from .fluid_lp import FluidLPSolution, solve_fluid_lp, static_bid_price_accept

__all__ = [
    "NetworkInstance",
    "generate_hub_spoke_2007_inspired",
    "published_capacity_per_leg",
    "ExactDP",
    "evaluate_policy_exact",
    "FluidLPSolution",
    "solve_fluid_lp",
    "static_bid_price_accept",
]
