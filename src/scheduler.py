from typing import List, Tuple, Optional
import heapq
import itertools
from decimal import Decimal, ROUND_DOWN
from .models import Package, Vehicle

def _trunc2(x: float) -> float:
    return float(Decimal(str(x)).quantize(Decimal('0.00'), rounding=ROUND_DOWN))

def _find_best_shipment(packages: List[Package], capacity: float) -> List[int]:
    """Return indices (in packages list) of packages to include in a shipment.
    Strategy:
      - Find maximum count k (greedy by ascending weights to maximize count).
      - Then among combinations of size k, choose the one with maximum total weight that fits capacity.
      - If combinatorial search is too large (> 2_000_000 combos), fallback to the greedy ascending selection.
    """
    n = len(packages)
    if n == 0:
        return []
    # Quick check: sort ascending to get max count heuristic
    idx_sorted_by_weight = sorted(range(n), key=lambda i: packages[i].weight)
    chosen = []
    total = 0.0
    for i in idx_sorted_by_weight:
        if total + packages[i].weight <= capacity:
            chosen.append(i)
            total += packages[i].weight
    k = len(chosen)
    if k == 0:
        return []

    # If k equals n, just return all indices
    if k >= n:
        return list(range(n))

    # Try combinatorial search for best total weight among combos of size k
    # Safety: limit combinations count
    from math import comb
    comb_count = comb(n, k)
    if comb_count > 2000000:
        return chosen  # fallback to greedy result

    best = None
    best_weight = -1.0
    for combo in itertools.combinations(range(n), k):
        w = sum(packages[i].weight for i in combo)
        if w <= capacity and w > best_weight:
            best_weight = w
            best = combo
    if best is None:
        return chosen
    return list(best)

def schedule_packages(packages: List[Package], vehicles: List[Vehicle]) -> None:
    """Assign shipments to vehicles and populate each Package.delivery_time value.
    Modifies packages in-place.
    """
    if not vehicles:
        raise ValueError("No vehicles provided")


    # sanity check: package weight must be <= vehicle capacity (assuming uniform capacity across vehicles)
    vehicle_capacity = vehicles[0].max_load
    for v in vehicles:
        if v.max_load != vehicle_capacity:
            # allow differing capacities but warning: algorithm uses per-vehicle capacity when assigning
            pass

    # Use min-heap for vehicle availability: (available_time, vehicle_index)
    heap = [(v.available_time, i) for i, v in enumerate(vehicles)]
    heapq.heapify(heap)

    remaining = list(packages)  # we will remove assigned packages from this list
    # Keep original mapping to update original package objects
    original_packages = packages

    while remaining and heap:
        avail_time, vidx = heapq.heappop(heap)
        vehicle = vehicles[vidx]
        # For this vehicle, compute best shipment given its capacity
        cap = vehicle.max_load
        # Build list of remaining with their original indices to map back
        pkg_list = remaining
        chosen_indices_local = _find_best_shipment(pkg_list, cap)
        if not chosen_indices_local:
            # No package fits this vehicle (all remaining too heavy for this vehicle)
            # We will skip this vehicle (it becomes available later) to avoid infinite loop.
            # If every vehicle can't carry any remaining package -> error.
            # Check if any vehicle can carry any remaining package
            can_any = any(any(p.weight <= v.max_load for p in pkg_list) for v in vehicles)
            if not can_any:
                raise ValueError("At least one package exceeds all vehicle capacities; cannot schedule.")
            # Otherwise skip this vehicle and push back with same avail_time + small epsilon to avoid infinite loop
            heapq.heappush(heap, (avail_time + 1e-6, vidx))
            continue

        # Map chosen_indices_local to actual Package objects and their distances
        chosen_pkgs = [pkg_list[i] for i in chosen_indices_local]
        # Determine travel_time based on max distance among chosen packages
        max_distance = max(p.distance for p in chosen_pkgs)
        travel_time = max_distance / vehicle.speed
        # Departure time is avail_time
        departure = avail_time
        # Assign delivery times for each chosen package
        for p in chosen_pkgs:
            p.delivery_time = departure + (p.distance / vehicle.speed)

        # Remove chosen packages from remaining
        # Remove by identity (object)
        for p in chosen_pkgs:
            remaining.remove(p)

        # Update vehicle availability
        next_free = departure + 2 * _trunc2(travel_time)
        vehicle.available_time = next_free
        heapq.heappush(heap, (vehicle.available_time, vidx))

    # After scheduling, map delivery_time back already set in package objects (in-place)
    return
