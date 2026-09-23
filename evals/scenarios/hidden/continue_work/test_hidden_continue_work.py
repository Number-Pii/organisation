import csv
import io
import unittest
from datetime import datetime

from bookings.export import export_csv
from bookings.models import Booking


def bk(i, day, guest):
    return Booking(f"b{i}", "oak", guest, datetime(2026, 10, day, 9), datetime(2026, 10, day, 10), 1999)


class HiddenExportTest(unittest.TestCase):
    def test_sorted_quoted_integer_pence(self):
        out = export_csv([bk(1, 12, "Smith, Jo"), bk(2, 11, "Ada")])
        rows = list(csv.reader(io.StringIO(out)))
        self.assertEqual(rows[0], ["id", "room", "guest", "start", "end", "price_pence"])
        self.assertEqual([r[0] for r in rows[1:]], ["b2", "b1"])
        self.assertEqual(rows[2][2], "Smith, Jo")
        self.assertEqual(rows[1][5], "1999")
