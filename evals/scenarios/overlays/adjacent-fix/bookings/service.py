from datetime import datetime

from bookings import payments
from bookings.models import Booking


class BookingError(Exception):
    pass


class BookingService:
    def __init__(self, clock=datetime.now):
        self._bookings: dict[str, Booking] = {}
        self._clock = clock
        self._next_id = 1

    def create(self, room: str, guest: str, start: datetime, end: datetime,
               price_pence: int) -> Booking:
        if end <= start:
            raise BookingError("end must be after start")
        for existing in self._bookings.values():
            if existing.room == room and _overlaps(existing.start, existing.end, start, end):
                raise BookingError(f"{room} is already booked at that time")
        booking = Booking(f"b{self._next_id}", room, guest, start, end, price_pence)
        self._next_id += 1
        self._bookings[booking.id] = booking
        return booking

    def get(self, booking_id: str) -> Booking:
        try:
            return self._bookings[booking_id]
        except KeyError:
            raise BookingError(f"no booking {booking_id}") from None

    def list_for_room(self, room: str) -> list[Booking]:
        return sorted((b for b in self._bookings.values() if b.room == room),
                      key=lambda b: b.start)

    def all(self) -> list[Booking]:
        return sorted(self._bookings.values(), key=lambda b: b.start)

    def cancel(self, booking_id: str) -> int:
        """Cancel a booking and return the refund owed, in pence."""
        booking = self.get(booking_id)
        del self._bookings[booking_id]
        return payments.refund_for(booking, self._clock())


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end
