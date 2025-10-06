import sys
from pathlib import Path
from typing import List, Tuple
from decimal import Decimal, ROUND_DOWN
from .models import Package, Vehicle
from .pricing import apply_offer_and_price
from .scheduler import schedule_packages

# ---------- formatting helpers ----------

def _trunc2_str(x: float) -> str:
    """Truncate to 2 decimals (string) for display/output consistency."""
    return str(Decimal(str(x)).quantize(Decimal("0.00"), rounding=ROUND_DOWN))


# ---------- parsing ----------

def _normalize_offer(code: str | None) -> str | None:
    """
    Normalize offer code. Treat 'NA'/'na' or empty as None.
    Keep others as-is; scheduler/pricing handle validity.
    """
    if code is None:
        return None
    code = code.strip()
    if not code or code.upper() == "NA":
        return None
    return code


def parse_input_lines(lines: List[str]) -> Tuple[float, List[Package], List[Vehicle]]:
    """
    Parse input lines as per the PDF format.
    Robust to blank lines; raises ValueError on malformed input.

    Returns:
        base_cost, packages, vehicles (vehicles may be empty if not provided)
    """
    # strip blank lines
    clean = [ln.strip() for ln in lines if ln.strip()]
    if not clean:
        raise ValueError("Input is empty")

    # first line: base_cost num_packages
    try:
        first = clean[0].split()
        base_cost = float(first[0])
        num_packages = int(first[1])
    except Exception as exc:
        raise ValueError("Invalid header line. Expected: '<base_cost> <no_of_packages>'") from exc

    # next num_packages lines
    if len(clean) < 1 + num_packages:
        raise ValueError(f"Expected {num_packages} package lines; found {len(clean) - 1}")

    packages: List[Package] = []
    for i in range(1, 1 + num_packages):
        parts = clean[i].split()
        if len(parts) < 3:
            raise ValueError(f"Invalid package line {i}: '{clean[i]}'")
        pkg_id = parts[0]
        try:
            weight = float(parts[1])
            distance = float(parts[2])
        except Exception as exc:
            raise ValueError(f"Invalid numeric values in line {i}: '{clean[i]}'") from exc
        offer = _normalize_offer(parts[3]) if len(parts) > 3 else None
        packages.append(Package(id=pkg_id, weight=weight, distance=distance, offer_code=offer))

    vehicles: List[Vehicle] = []
    # optional vehicle line exists?
    if len(clean) > 1 + num_packages:
        vparts = clean[1 + num_packages].split()
        if len(vparts) != 3:
            raise ValueError("Invalid vehicle line. Expected: '<no_of_vehicles> <max_speed> <max_load>'")
        try:
            no_of_vehicles = int(vparts[0])
            max_speed = float(vparts[1])
            max_load = float(vparts[2])
        except Exception as exc:
            raise ValueError("Invalid vehicle line numbers.") from exc
        vehicles = [Vehicle(id=i + 1, max_load=max_load, speed=max_speed) for i in range(no_of_vehicles)]

    return base_cost, packages, vehicles


# ---------- core ----------

def _compute_costs(base_cost: float, packages: List[Package]) -> None:
    """Populate discount and total_cost for each package."""
    for pkg in packages:
        discount, total = apply_offer_and_price(pkg.id, base_cost, pkg.weight, pkg.distance, pkg.offer_code)
        pkg.discount = discount
        pkg.total_cost = total


def _validate_capacity(packages: List[Package], vehicles: List[Vehicle]) -> None:
    """Raise ValueError if any package exceeds all vehicle capacities."""
    if not vehicles:
        return
    max_capacity = max(v.max_load for v in vehicles)
    too_heavy = [p.id for p in packages if p.weight > max_capacity]
    if too_heavy:
        raise ValueError(f"Package(s) exceed max vehicle capacity {max_capacity}: {', '.join(too_heavy)}")


def _print_results(packages: List[Package]) -> None:
    """Print results in required format."""
    for pkg in packages:
        delivered_at = pkg.delivery_time if pkg.delivery_time is not None else 0.0
        print(f"{pkg.id} {int(pkg.discount)} {int(pkg.total_cost)} {_trunc2_str(delivered_at)}")


# ---------- entry ----------

def main(argv: List[str]) -> int:
    """
    CLI entry point.

    Usage:
        python -m src.cli <input_file | ->
        - Use '-' to read from stdin.
    """
    if len(argv) < 2:
        print("Usage: python -m src.cli <input_file | ->")
        return 1

    if argv[1] == "-":
        raw_lines = sys.stdin.read().strip().splitlines()
    else:
        path = Path(argv[1])
        if not path.exists():
            print(f"Input file {path} not found")
            return 2
        raw_lines = path.read_text(encoding="utf-8").splitlines()

    try:
        base_cost, packages, vehicles = parse_input_lines(raw_lines)
    except ValueError as err:
        print(f"Input error: {err}")
        return 3

    _compute_costs(base_cost, packages)

    try:
        _validate_capacity(packages, vehicles)
    except ValueError as err:
        print(f"Validation error: {err}")
        return 4

    if vehicles:
        schedule_packages(packages, vehicles)

    _print_results(packages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
