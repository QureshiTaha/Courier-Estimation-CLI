import sys
from pathlib import Path
from .models import Package, Vehicle
from .pricing import apply_offer_and_price
from .scheduler import schedule_packages
from decimal import Decimal, ROUND_DOWN

def trunc2(x: float) -> str:
    return str(Decimal(str(x)).quantize(Decimal('0.00'), rounding=ROUND_DOWN))

def parse_input_lines(lines):
    it = iter(lines)
    first = next(it).strip().split()
    base_cost = float(first[0])
    num_packages = int(first[1])
    packages = []
    for _ in range(num_packages):
        parts = next(it).strip().split()
        pid = parts[0]
        weight = float(parts[1])
        distance = float(parts[2])
        offer = parts[3] if len(parts) > 3 else None
        packages.append(Package(id=pid, weight=weight, distance=distance, offer_code=offer))
    # Check if vehicle line exists
    try:
        vline = next(it).strip().split()
    except StopIteration:
        return base_cost, packages, []
    num_vehicles = int(vline[0])
    max_speed = float(vline[1])
    max_load = float(vline[2])
    vehicles = [Vehicle(id=i+1, max_load=max_load, speed=max_speed) for i in range(num_vehicles)]
    return base_cost, packages, vehicles

def main(argv):
    if len(argv) < 2:
        print("Usage: python -m src.cli <input_file>")
        return 1
    path = Path(argv[1])
    if not path.exists():
        print(f"Input file {path} not found")
        return 2
    lines = path.read_text().strip().splitlines()
    base_cost, packages, vehicles = parse_input_lines(lines)
    # Calculate pricing
    for p in packages:
        discount, total = apply_offer_and_price(p.id, base_cost, p.weight, p.distance, p.offer_code)
        p.discount = discount
        p.total_cost = total

    if vehicles:
        # Basic sanity: ensure each package weight <= max vehicle capacity
        max_vehicle_capacity = max(v.max_load for v in vehicles)
        for p in packages:
            if p.weight > max_vehicle_capacity:
                print(f"Error: package {p.id} weight {p.weight} exceeds max vehicle capacity {max_vehicle_capacity}")
                return 3
        schedule_packages(packages, vehicles)

    for p in packages:
        dt = p.delivery_time if p.delivery_time is not None else 0.0
        print(f"{p.id} {int(p.discount)} {int(p.total_cost)} {trunc2(dt)}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
