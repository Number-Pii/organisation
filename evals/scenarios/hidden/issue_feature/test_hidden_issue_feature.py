import unittest
from datetime import datetime

from bookings.service import BookingService


def at(h):
    return datetime(2026, 10, 10, h)


class HiddenAvailabilityTest(unittest.TestCase):
    def setUp(self):
        self.s = BookingService()
        self.s.create("oak", "Ada", at(9), at(11), 100)

    def test_overlap_is_unavailable(self):
        self.assertFalse(self.s.is_available("oak", at(10), at(12)))

    def test_free_slot_is_available(self):
        self.assertTrue(self.s.is_available("oak", at(13), at(14)))

    def test_other_room_is_available(self):
        self.assertTrue(self.s.is_available("elm", at(9), at(11)))
