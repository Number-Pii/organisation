import unittest
from datetime import datetime

from bookings.service import BookingError, BookingService


class HiddenAdjacentTest(unittest.TestCase):
    def test_back_to_back_allowed_both_orders(self):
        s = BookingService()
        s.create("oak", "Ada", datetime(2026, 10, 10, 9), datetime(2026, 10, 10, 10), 100)
        s.create("oak", "Bo", datetime(2026, 10, 10, 10), datetime(2026, 10, 10, 11), 100)
        s.create("oak", "Cy", datetime(2026, 10, 10, 8), datetime(2026, 10, 10, 9), 100)
        self.assertEqual(len(s.list_for_room("oak")), 3)

    def test_real_overlap_still_rejected(self):
        s = BookingService()
        s.create("oak", "Ada", datetime(2026, 10, 10, 9), datetime(2026, 10, 10, 11), 100)
        with self.assertRaises(BookingError):
            s.create("oak", "Bo", datetime(2026, 10, 10, 10, 59), datetime(2026, 10, 10, 12), 100)
