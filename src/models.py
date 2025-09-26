from dataclasses import dataclass
from typing import Optional

@dataclass
class Package:
    id: str
    weight: float
    distance: float
    offer_code: Optional[str] = None
    discount: float = 0.0
    total_cost: float = 0.0
    delivery_time: Optional[float] = None

@dataclass
class Vehicle:
    id: int
    max_load: float
    speed: float
    available_time: float = 0.0
