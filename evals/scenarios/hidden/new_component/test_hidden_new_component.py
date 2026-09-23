import unittest
from datetime import datetime, timedelta

from bookings.models import Booking
from bookings.reminders import due_reminders

NOW = datetime(2026, 10, 10, 9)


def b(i, start_hours):
    start = NOW + timedelta(hours=start_hours)
    return Booking(f"b{i}", "oak", "G", start, start + timedelta(hours=1), 100)


class HiddenRemindersTest(unittest.TestCase):
    def test_window_sorting_and_started_excluded(self):
        items = [b(1, 30), b(2, 5), b(3, -1), b(4, 1), b(5, 24)]
        due = due_reminders(items, NOW, hours=24)
        self.assertEqual([x.id for x in due], ["b4", "b2", "b5"])

    def test_default_window_is_24_hours(self):
        self.assertEqual([x.id for x in due_reminders([b(1, 23), b(2, 25)], NOW)], ["b1"])
