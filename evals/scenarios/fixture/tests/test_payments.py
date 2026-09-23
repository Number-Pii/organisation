import unittest
from datetime import datetime, timedelta

from bookings.models import Booking
from bookings.payments import refund_for

START = datetime(2026, 10, 10, 9, 0)
BOOKING = Booking("b1", "oak", "Ada", START, START + timedelta(hours=1), 3000)


class RefundTest(unittest.TestCase):
    def test_full_refund_48_hours_out(self):
        self.assertEqual(refund_for(BOOKING, START - timedelta(hours=48)), 3000)

    def test_half_refund_between_24_and_48_hours(self):
        self.assertEqual(refund_for(BOOKING, START - timedelta(hours=30)), 1500)

    def test_no_refund_inside_24_hours(self):
        self.assertEqual(refund_for(BOOKING, START - timedelta(hours=2)), 0)


if __name__ == "__main__":
    unittest.main()
