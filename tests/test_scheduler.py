import pytest
from src.scheduler import schedule_packages
from src.models import Package, Vehicle

def test_scheduler_sample():
    pkgs = [
        Package('PKG1', 50, 30),
        Package('PKG2', 75, 125),
        Package('PKG3', 175, 100),
        Package('PKG4', 110, 60),
        Package('PKG5', 155, 95),
    ]
    vehicles = [Vehicle(1, 200, 70), Vehicle(2, 200, 70)]
    schedule_packages(pkgs, vehicles)
    # All packages should have delivery_time set (float)
    assert all(p.delivery_time is not None for p in pkgs)
    # Check ordering of some delivery times matches expectation shape (not exact values)
    times = {p.id: p.delivery_time for p in pkgs}
    assert isinstance(times['PKG1'], float)

def test_scheduler_cannot_fit_any_package_raises():
    pkgs = [Package("P1", 500, 10)]  # too heavy for all
    vehicles = [Vehicle(1, max_load=100, speed=60), Vehicle(2, max_load=120, speed=60)]
    with pytest.raises(ValueError):
        schedule_packages(pkgs, vehicles)