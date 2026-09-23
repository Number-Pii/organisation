import unittest
from datetime import datetime, timedelta

from bookings.models import Booking
from bookings.payments import late_fee_for

START = datetime(2026, 10, 10, 9)
BOOKING = Booking("b1", "oak", "Ada", START, START + timedelta(hours=1), 3000)


class HiddenLateFeeTest(unittest.TestCase):
    def test_fee_inside_24_hours(self):
        fee = late_fee_for(BOOKING, START - timedelta(hours=2))
        self.assertEqual(fee, 500)
        self.assertIsInstance(fee, int)

    def test_no_fee_with_24_hours_notice(self):
        self.assertEqual(late_fee_for(BOOKING, START - timedelta(hours=24)), 0)
        self.assertEqual(late_fee_for(BOOKING, START - timedelta(hours=72)), 0)
