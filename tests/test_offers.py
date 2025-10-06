from src.offers import calculate_discount_for

def test_offers_applicability():
    # OFR001 requires weight in [70,200] and distance <= 200
    assert calculate_discount_for('OFR001', 1000, 100, 100) == 100.0  # 10%
    assert calculate_discount_for('OFR001', 1000, 50, 100) == 0.0

def test_unknown_offer():
    assert calculate_discount_for('UNKNOWN', 500, 100, 100) == 0.0

def test_none_offer_returns_zero():
    assert calculate_discount_for(None, 700.0, 10, 100) == 0.0