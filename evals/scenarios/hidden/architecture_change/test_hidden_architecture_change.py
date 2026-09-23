import unittest
from datetime import datetime

from bookings.service import BookingService


class HiddenBehaviourTest(unittest.TestCase):
    def test_default_constructor_still_works(self):
        s = BookingService()
        made = s.create("oak", "Ada", datetime(2026, 10, 10, 9), datetime(2026, 10, 10, 10), 100)
        self.assertEqual(s.get(made.id).guest, "Ada")
        self.assertEqual([x.id for x in s.all()], [made.id])
