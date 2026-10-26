import unittest
from cancellation import cancellation_fee


class CancellationTests(unittest.TestCase):
    def test_late_cancellation(self):
        self.assertEqual(cancellation_fee(0, 100), 50)

    def test_at_day_boundary(self):
        self.assertEqual(cancellation_fee(24, 100), 25)

    def test_at_free_boundary(self):
        self.assertEqual(cancellation_fee(48, 100), 0)

    def test_early_cancellation(self):
        self.assertEqual(cancellation_fee(72, 100), 0)

    def test_half_fee_rounds_down(self):
        self.assertEqual(cancellation_fee(12, 101), 50)

    def test_negative_arguments(self):
        for hours, paid in [(-1, 100), (24, -1)]:
            with self.subTest(hours=hours, paid=paid), self.assertRaises(ValueError):
                cancellation_fee(hours, paid)


class AdditionalContractExamples(unittest.TestCase):
    def test_last_hour_before_free_cancellation(self):
        self.assertEqual(cancellation_fee(47, 100), 25)

    def test_last_hour_in_half_fee_band(self):
        self.assertEqual(cancellation_fee(23, 100), 50)
