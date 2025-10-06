from typing import List, Sequence
import heapq
import itertools
from decimal import Decimal, ROUND_DOWN
from .models import Package, Vehicle

# ---------- helpers ----------

def _trunc2(x: float) -> float:
    """Truncate to 2 decimals (not round)."""
    return float(Decimal(str(x)).quantize(Decimal('0.00'), rounding=ROUND_DOWN))


def _max_packages_first_then_heaviest(packages: Sequence[Package], capacity: float) -> List[int]:
    """
    Return indices of packages (relative to 'packages') for a shipment that:
    1) maximizes the number of packages (cardinality), and
    2) among those, maximizes total weight,
    subject to the vehicle capacity.

    Strategy:
    - Greedy (ascending by weight) to get max cardinality k.
    - If feasible, search all C(n, k) combinations to find the heaviest within capacity.
      Falls back to greedy result if combinations are too many.
    """
    n = len(packages)
    if n == 0:
        return []

    # Greedy to maximize count
    sorted_by_weight_idx = sorted(range(n), key=lambda i: packages[i].weight)
    greedy_indices: List[int] = []
    greedy_total_weight = 0.0
    for idx in sorted_by_weight_idx:
        w = packages[idx].weight
        if greedy_total_weight + w <= capacity:
            greedy_indices.append(idx)
            greedy_total_weight += w

    max_packages_count = len(greedy_indices)
    if max_packages_count == 0:
        return []
    if max_packages_count == n:
        return list(range(n))

    # Among combos with same count, pick heaviest total weight (limit search)
    from math import comb
    combinations_count = comb(n, max_packages_count)
    if combinations_count > 2_000_000:   # safety
        return greedy_indices

    best_combo = greedy_indices
    best_total_weight = greedy_total_weight
    for combo in itertools.combinations(range(n), max_packages_count):
        total_weight = sum(packages[i].weight for i in combo)
        if total_weight <= capacity and total_weight > best_total_weight:
            best_total_weight = total_weight
            best_combo = list(combo)

    return best_combo


def _assign_delivery_times(departure_time: float, vehicle_speed: float, chosen: Sequence[Package]) -> None:
    """Set delivery_time for each chosen package (full precision)."""
    for pkg in chosen:
        pkg.delivery_time = departure_time + (pkg.distance / vehicle_speed)


def _update_vehicle_availability(departure_time: float, vehicle: Vehicle, chosen: Sequence[Package]) -> None:
    """
    Update vehicle.available_time based on PDF rule:
    - One-way trip time = max(distance)/speed
    - Truncate one-way time to 2 decimals BEFORE doubling for return.
    """
    max_distance = max(pkg.distance for pkg in chosen)
    one_way = max_distance / vehicle.speed
    vehicle.available_time = departure_time + 2 * _trunc2(one_way)


# ---------- main API ----------

def schedule_packages(packages: List[Package], vehicles: List[Vehicle]) -> None:
    """
    Assign shipments to vehicles and populate each Package.delivery_time.

    The algorithm:
    - Keep a min-heap of vehicles by 'available_time'.
    - At each step, pop the earliest-available vehicle and form a shipment that
      maximizes package count (and among ties, the heaviest) under its capacity.
    - Set per-package delivery times (using full precision, truncated only at print).
    - Update vehicle's available_time using the PDF truncation rule for the return trip.
    - Repeat until all packages are scheduled.

    Args:
        packages: mutable list of packages (delivery_time is updated in-place).
        vehicles: list of vehicles with speed and capacity.

    Raises:
        ValueError: if no vehicles provided or if at least one remaining package
                    cannot fit into any vehicle (capacity too small).
    """
    if not vehicles:
        raise ValueError("No vehicles provided")

    # Min-heap of (available_time, index)
    heap = [(v.available_time, i) for i, v in enumerate(vehicles)]
    heapq.heapify(heap)

    remaining: List[Package] = list(packages)

    while remaining and heap:
        available_time, vehicle_idx = heapq.heappop(heap)
        vehicle = vehicles[vehicle_idx]

        # Make a shipment for this vehicle
        shipment_indices = _max_packages_first_then_heaviest(remaining, vehicle.max_load)
        if not shipment_indices:
            # If no remaining package fits this vehicle, check if *any* vehicle can take any remaining package.
            any_vehicle_can = any(
                any(pkg.weight <= v.max_load for pkg in remaining) for v in vehicles
            )
            if not any_vehicle_can:
                raise ValueError("At least one package exceeds all vehicle capacities; cannot schedule.")
            # Push this vehicle back with a tiny time increment to avoid busy-loop
            heapq.heappush(heap, (available_time + 1e-6, vehicle_idx))
            continue

        chosen = [remaining[i] for i in shipment_indices]

        # Per-package delivery times
        _assign_delivery_times(available_time, vehicle.speed, chosen)

        # Remove chosen from 'remaining' (by identity)
        for pkg in chosen:
            remaining.remove(pkg)

        # Vehicle availability for next trip
        _update_vehicle_availability(available_time, vehicle, chosen)
        heapq.heappush(heap, (vehicle.available_time, vehicle_idx))
