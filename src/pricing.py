from typing import Tuple
from .offers import calculate_discount_for

def calculate_delivery_cost(base_cost: float, weight: float, distance: float) -> float:
    # Base + weight*10 + distance*5
    return round(base_cost + weight * 10.0 + distance * 5.0, 2)

def apply_offer_and_price(pkg_id: str, base_cost: float, weight: float, distance: float, offer_code: str):
    delivery_cost = calculate_delivery_cost(base_cost, weight, distance)
    discount = calculate_discount_for(offer_code, delivery_cost, weight, distance)
    total = round(delivery_cost - discount, 2)
    return discount, total
