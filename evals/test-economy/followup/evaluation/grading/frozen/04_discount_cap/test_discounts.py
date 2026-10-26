import unittest
from discounts import discounted_total


class DiscountTests(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(discounted_total(1200, 0), 1200)

    def test_percentage_discount(self):
        self.assertEqual(discounted_total(1000, 15), 850)

    def test_discount_rounds_down_to_whole_cents(self):
        self.assertEqual(discounted_total(999, 15), 850)

    def test_full_discount(self):
        self.assertEqual(discounted_total(1000, 100), 0)

    def test_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            discounted_total(-1, 15)

    def test_invalid_percent(self):
        for percent in [-1, 101]:
            with self.subTest(percent=percent), self.assertRaises(ValueError):
                discounted_total(1000, percent)
