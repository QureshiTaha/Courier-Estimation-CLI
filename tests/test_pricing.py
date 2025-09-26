from src.pricing import calculate_delivery_cost, apply_offer_and_price

def test_cost_basic():
    assert calculate_delivery_cost(100, 5, 5) == 175.0
    assert calculate_delivery_cost(100, 10, 100) == 700.0

def test_apply_offer():
    discount, total = apply_offer_and_price('PKG3', 100, 10, 100, 'OFR003')
    assert discount == 35.0
    assert total == 665.0
