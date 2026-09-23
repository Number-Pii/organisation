from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Booking:
    id: str
    room: str
    guest: str
    start: datetime
    end: datetime
    price_pence: int
