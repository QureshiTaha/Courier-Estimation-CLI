from typing import Optional, Dict, Tuple
# Define offers here as: code -> (discount_percent, (min_weight, max_weight), (min_distance, max_distance))
# Distances and weights use inclusive boundaries as per problem statement examples.

OFFERS = {
    'OFR001': (10, (70, 200), (0, 200)),   # 10% discount if weight in [70,200] and distance <= 200
    'OFR002': (7, (100, 250), (50, 150)),  # 7% discount if weight in [100,250] and distance in [50,150]
    'OFR003': (5, (10, 150), (50, 250)),   # 5% discount if weight in [10,150] and distance in [50,250]
}

def get_offer(code: Optional[str]):
    if code is None:
        return None
    return OFFERS.get(code.upper())

def calculate_discount_for(code: Optional[str], delivery_cost: float, weight: float, distance: float) -> float:
    """Return discount amount (absolute) for the given offer code and package characteristics."""
    offer = get_offer(code)
    if not offer:
        return 0.0
    percent, (wmin, wmax), (dmin, dmax) = offer
    if (weight >= wmin and weight <= wmax) and (distance >= dmin and distance <= dmax):
        return round(delivery_cost * percent / 100.0, 2)
    return 0.0
