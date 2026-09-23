import unittest
from datetime import datetime

from bookings.service import BookingError, BookingService


def at(hour: int, day: int = 10) -> datetime:
    return datetime(2026, 10, day, hour, 0)


class BookingServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = BookingService(clock=lambda: at(9, day=1))

    def test_create_and_list(self):
        self.service.create("oak", "Ada", at(9), at(10), 2000)
        self.service.create("oak", "Bo", at(13), at(14), 2000)
        self.assertEqual([b.guest for b in self.service.list_for_room("oak")], ["Ada", "Bo"])

    def test_overlapping_booking_rejected(self):
        self.service.create("oak", "Ada", at(9), at(11), 2000)
        with self.assertRaises(BookingError):
            self.service.create("oak", "Bo", at(10), at(12), 2000)

    def test_back_to_back_bookings_allowed(self):
        self.service.create("oak", "Ada", at(9), at(10), 2000)
        self.service.create("oak", "Bo", at(10), at(11), 2000)
        self.assertEqual(len(self.service.list_for_room("oak")), 2)

    def test_other_room_is_independent(self):
        self.service.create("oak", "Ada", at(9), at(11), 2000)
        self.service.create("elm", "Bo", at(9), at(11), 2000)
        self.assertEqual(len(self.service.all()), 2)

    def test_end_must_follow_start(self):
        with self.assertRaises(BookingError):
            self.service.create("oak", "Ada", at(11), at(9), 2000)

    def test_cancel_early_refunds_in_full(self):
        booking = self.service.create("oak", "Ada", at(9), at(10), 2000)
        self.assertEqual(self.service.cancel(booking.id), 2000)
        self.assertEqual(self.service.all(), [])


if __name__ == "__main__":
    unittest.main()
