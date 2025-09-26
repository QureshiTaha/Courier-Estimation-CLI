# Courier Service Estimation Calculator (Python)

## Overview
This repository contains a complete Python solution for the courier service.
It includes:
- Delivery cost calculation with offer codes.
- Scheduler that assigns packages to vehicles and computes estimated delivery times.
- Unit tests (pytest).
- Sample input & output.

## Assumptions
- Each package weight <= max carriable weight. If any package exceeds capacity, the program raises an error.
- Offers are applied according to rules defined in `src/offers.py`.
- For a multi-package shipment, the vehicle's trip time is based on the **maximum distance** among packages in that shipment.
- Delivery time for each package = `departure_time + package_distance / speed`.
- Input parsing follows the PDF samples. See `samples/sample_input_with_vehicles.txt`.

## How to run
Requirements: Python 3.10+
```bash
python -m venv .venv
source .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Run the CLI with a sample input:
```bash
python -m src.cli samples/sample_input_with_vehicles.txt
```

The program prints lines in the format:
`PKG1 <discount> <total_cost> <delivery_time_in_hours>`

## Tests
Run tests with:
```bash
pytest -q
```

**Windows note:** If you’re not using the included `pytest.ini`, you may need:
```bash
set PYTHONPATH=%CD%
pytest -q
```

## Design notes (short)
- SOLID: small classes (`Package`, `Offer`, `Vehicle`) and single-responsibility modules.
- TDD: tests provided that cover pricing, offers, and scheduling behaviors.
- Scheduler uses a combination of greedy heuristics and combinatorial search to maximize package count per shipment,
  and among equal-count shipments picks the heaviest shipment that fits capacity.

## Project Structure
- `src/` - source code
- `tests/` - pytest tests
- `samples/` - input/output examples

## screenshots
![output](image.png)
