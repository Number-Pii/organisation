"""Refund rules. doc/specs/payments.md is the policy these implement."""

from datetime import datetime

from bookings.models import Booking

FULL_REFUND_HOURS = 48
PARTIAL_REFUND_HOURS = 24
PARTIAL_REFUND_PERCENT = 50


def refund_for(booking: Booking, now: datetime) -> int:
    hours_before = (booking.start - now).total_seconds() / 3600
    if hours_before >= FULL_REFUND_HOURS:
        return booking.price_pence
    if hours_before >= PARTIAL_REFUND_HOURS:
        return booking.price_pence * PARTIAL_REFUND_PERCENT // 100
    return 0
