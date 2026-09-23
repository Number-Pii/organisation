"""CSV export of bookings for the finance team."""

from bookings.models import Booking

HEADER = "id,room,guest,start,end,price_pence"


def export_csv(bookings: list[Booking]) -> str:
    lines = [HEADER]
    for b in bookings:
        lines.append(",".join([b.id, b.room, b.guest, b.start.isoformat(),
                               b.end.isoformat(), str(b.price_pence)]))
    return "\n".join(lines) + "\n"
