"""Validated data for Adelman's finite-horizon network model.

Adelman (2007), equations (1)-(2), pp. 648-649, assumes one or zero customer
requests per period, nonreplenishing capacities, and no discount.  The
orientation of ``A`` is resource-by-product: ``A[i][j] = a_ij``.  Periods in
mathematical statements begin at 1; the stored ``p[t-1]`` uses Python's
zero-based row indexing.  Keeping this convention in one place prevents
quiet off-by-one errors in later LP and policy implementations.

The hub-and-spoke generator below is *synthetic*, not a reconstruction of the
unavailable 2007 random draws.  Every choice that is not specified in the
paper is made explicit in its signature or provenance string.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random


def _nonnegative_int(value: object, label: str) -> None:
    # bool is an int subclass, but True is not meaningful as a capacity.
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")


def _finite_nonnegative(value: object, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite nonnegative number")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} must be a finite nonnegative number")


@dataclass(frozen=True)
class NetworkInstance:
    """Immutable instance for the finite-horizon accept/reject MDP.

    ``T,m,n`` denote periods, resources, and classes. ``c`` is initial
    capacity; ``A[i][j]`` is units of resource ``i`` consumed by one class
    ``j`` sale; ``f[j]`` is its fare; ``p[t-1][j]`` is the probability that
    class ``j`` is the *only* request in period ``t``.  The implicit
    no-arrival probability is ``1 - sum_j p[t-1][j]``.

    Positive capacities and fares are Adelman's source assumptions. Zero
    capacities/fares are permitted here only for explicit boundary tests; a
    result using them must not be presented as a direct instance of every
    source theorem (notably structural-price statements).
    """

    T: int
    m: int
    n: int
    c: tuple[int, ...]
    A: tuple[tuple[int, ...], ...]
    f: tuple[float, ...]
    p: tuple[tuple[float, ...], ...]
    name: str = "unnamed"
    provenance: str = "user-specified instance"

    def __post_init__(self) -> None:
        # Freeze nested inputs as well: a frozen dataclass containing lists
        # would otherwise still be mutable through those list references.
        object.__setattr__(self, "c", tuple(self.c))
        object.__setattr__(self, "A", tuple(tuple(row) for row in self.A))
        object.__setattr__(self, "f", tuple(self.f))
        object.__setattr__(self, "p", tuple(tuple(row) for row in self.p))

        for label, count in (("T", self.T), ("m", self.m), ("n", self.n)):
            if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                raise ValueError(f"{label} must be a positive integer")
        if len(self.c) != self.m or len(self.A) != self.m:
            raise ValueError("c and A must each have m resource rows")
        if len(self.f) != self.n or len(self.p) != self.T:
            raise ValueError("f must have n entries and p must have T rows")
        if not self.name or not self.provenance:
            raise ValueError("name and provenance must be nonempty")

        for i, capacity in enumerate(self.c):
            _nonnegative_int(capacity, f"c[{i}]")
        for i, row in enumerate(self.A):
            if len(row) != self.n:
                raise ValueError(f"A[{i}] must have n product columns")
            for j, units in enumerate(row):
                _nonnegative_int(units, f"A[{i}][{j}]")
        for j, fare in enumerate(self.f):
            _finite_nonnegative(fare, f"f[{j}]")
        for t, row in enumerate(self.p, start=1):
            if len(row) != self.n:
                raise ValueError(f"p[{t - 1}] must have n class probabilities")
            for j, probability in enumerate(row):
                _finite_nonnegative(probability, f"p[{t - 1}][{j}]")
                if probability > 1:
                    raise ValueError("an arrival probability cannot exceed one")
            # Reject *any* overfull probability mass. A tolerance followed
            # by clipping p_t0 to zero would leave a transition kernel with
            # total mass greater than one, however small the discrepancy.
            if math.fsum(row) > 1.0:
                raise ValueError(f"period {t} arrival probabilities exceed one")

    def no_arrival_probability(self, t: int) -> float:
        """Return ``p_t0`` for mathematical period ``t`` (1 through T)."""
        if not 1 <= t <= self.T:
            raise ValueError("period t must be in 1..T")
        # Validation above ensures this is nonnegative. Do not silently clip
        # an overfull kernel or normalize probabilities without disclosure.
        return 1.0 - math.fsum(self.p[t - 1])

    def feasible(self, remaining: tuple[int, ...], j: int) -> bool:
        """Can one class-j request be accepted from this remaining state?"""
        if len(remaining) != self.m or not 0 <= j < self.n:
            raise ValueError("state dimension or class index is invalid")
        if any(
            isinstance(r, bool) or not isinstance(r, int) or r < 0 or r > self.c[i]
            for i, r in enumerate(remaining)
        ):
            raise ValueError("remaining state must be an integer vector within initial capacity")
        return all(self.A[i][j] <= remaining[i] for i in range(self.m))

    def after_acceptance(self, remaining: tuple[int, ...], j: int) -> tuple[int, ...]:
        """Apply one feasible sale, leaving capacities nonnegative."""
        if not self.feasible(remaining, j):
            raise ValueError("cannot accept a class without sufficient capacity")
        return tuple(remaining[i] - self.A[i][j] for i in range(self.m))

    def expected_class_demand(self) -> tuple[float, ...]:
        """Return ``d_j = sum_t p_tj`` used in Adelman's fluid LP (4)-(6)."""
        return tuple(math.fsum(self.p[t][j] for t in range(self.T)) for j in range(self.n))


# Adelman (2007), Table 2, printed p. 656. These capacities are source-stated
# *comparison targets*, not a formula inferred from a 2025 implementation.
# The original probability draws that generated the accompanying load factors
# are not available, so inserting these values in our synthetic generator
# does not reproduce the original Table 2 instances or their exact loads.
_PUBLISHED_CAPACITIES: dict[int, dict[int, int]] = {
    20: {2: 3, 5: 1, 10: 1, 20: 1},
    50: {2: 7, 5: 4, 10: 2, 20: 2},
    100: {2: 15, 5: 8, 10: 4, 20: 2},
    200: {2: 31, 5: 16, 10: 9, 20: 4},
    500: {2: 79, 5: 42, 10: 22, 20: 12},
    1000: {2: 159, 5: 84, 10: 45, 20: 24},
}


def published_capacity_per_leg(*, spokes: int, horizon: int) -> int:
    """Look up, without interpolation, Adelman (2007) Table 2 capacity."""
    try:
        return _PUBLISHED_CAPACITIES[horizon][spokes]
    except KeyError as exc:
        raise ValueError("Table 2 has only L=2,5,10,20 and T=20,50,100,200,500,1000") from exc


def generate_hub_spoke_2007_inspired(
    *, spokes: int, horizon: int, capacity_per_leg: int, seed: int
) -> NetworkInstance:
    """Create a deterministic, *synthetic* 2007-inspired hub network.

    Source-stated design (Adelman 2007, Sec. 5, pp. 656-657): each spoke k
    has directed legs H->k and k->H; there are 2L one-leg itineraries and
    L(L-1) two-leg itineraries k->H->l (k != l). Each itinerary has a
    low class with integer fare uniformly drawn from 15..49 and a high
    class with fare 5 times that low fare. Demand is stationary, total
    arrival probability is 0.8, and its high/low split is 25%/75%.

    Explicit *our* choices, not stated in the 2007 paper: Python's
    ``random.Random(seed)`` stream; iid continuous Uniform(0,1) itinerary
    weights normalized to sum to one; and the caller's ``capacity_per_leg``.
    Supplying a Table 2 capacity via :func:`published_capacity_per_leg`
    matches only that one input, not Adelman's unpublished random instance.
    """
    for label, value in (("spokes", spokes), ("horizon", horizon)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{label} must be a positive integer")
    _nonnegative_int(capacity_per_leg, "capacity_per_leg")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")

    rng = random.Random(seed)
    legs = 2 * spokes
    itineraries: list[tuple[str, tuple[int, ...]]] = []
    for k in range(spokes):
        itineraries.append((f"H->{k + 1}", (k,)))
        itineraries.append((f"{k + 1}->H", (spokes + k,)))
    for k in range(spokes):
        for l in range(spokes):
            if k != l:
                itineraries.append((f"{k + 1}->H->{l + 1}", (spokes + k, l)))

    weights = [rng.random() for _ in itineraries]
    weight_total = math.fsum(weights)
    # A seed cannot realistically produce all-zero draws, but treating that
    # theoretical case explicitly avoids a hidden division-by-zero path.
    if weight_total == 0:
        raise RuntimeError("synthetic itinerary weights summed to zero")

    fares: list[float] = []
    probabilities: list[float] = []
    columns: list[tuple[int, ...]] = []
    for (_, resources), weight in zip(itineraries, weights):
        low_fare = rng.randint(15, 49)  # endpoints inclusive (discrete uniform)
        share = weight / weight_total
        # Put low then high for each itinerary. Only one class can arrive in
        # a period, so these are mutually exclusive request probabilities.
        fares.extend((float(low_fare), float(5 * low_fare)))
        probabilities.extend((0.8 * share * 0.75, 0.8 * share * 0.25))
        column = tuple(1 if i in resources else 0 for i in range(legs))
        columns.extend((column, column))

    classes = len(columns)
    matrix = tuple(tuple(columns[j][i] for j in range(classes)) for i in range(legs))
    stationary = tuple(probabilities)
    return NetworkInstance(
        T=horizon,
        m=legs,
        n=classes,
        c=(capacity_per_leg,) * legs,
        A=matrix,
        f=tuple(fares),
        p=(stationary,) * horizon,
        name=f"synthetic_hub_L{spokes}_T{horizon}_C{capacity_per_leg}_seed{seed}",
        provenance=(
            "synthetic 2007-inspired hub network; source-stated topology, fare "
            "distribution, 0.8 arrival mass, and 75/25 low/high split; our "
            f"iid Uniform(0,1) itinerary weights normalized; seed={seed}; "
            f"caller-selected equal capacity_per_leg={capacity_per_leg}; "
            "NOT an exact 2007 published-table replication"
        ),
    )
