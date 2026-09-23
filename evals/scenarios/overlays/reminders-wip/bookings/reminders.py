"""Reminder emails: find bookings that start soon."""

from datetime import datetime, timedelta

from bookings.models import Booking


def due_reminders(bookings: list[Booking], now: datetime, hours: int = 24) -> list[Booking]:
    cutoff = now + timedelta(hours=hours)
    # TODO: exclude bookings that already started; sort by start; tests
    return [b for b in bookings if b.start <= cutoff]
