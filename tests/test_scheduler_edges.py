from src.models import Package, Vehicle
from src.scheduler import schedule_packages, _max_packages_first_then_heaviest as pick

def test_pick_returns_all_when_all_fit():
    pkgs = [Package("A", 10, 1), Package("B", 15, 1)]
    idxs = pick(pkgs, capacity=1000)
    assert set(idxs) == {0, 1}

def test_pick_returns_empty_when_none_fit():
    pkgs = [Package("A", 300, 1), Package("B", 400, 1)]
    idxs = pick(pkgs, capacity=100)
    assert idxs == []

def test_vehicle_skip_when_first_cannot_carry_but_second_can():
    # Vehicle 1 too small, Vehicle 2 big enough -> algorithm should skip v1 and use v2
    pkgs = [Package("P", 150, 10)]
    v1 = Vehicle(1, max_load=50, speed=70)
    v2 = Vehicle(2, max_load=200, speed=70)
    schedule_packages(pkgs, [v1, v2])
    assert pkgs[0].delivery_time is not None
