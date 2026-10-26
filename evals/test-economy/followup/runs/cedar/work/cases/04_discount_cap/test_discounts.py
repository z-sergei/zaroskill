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

    def test_discount_is_limited_by_cap(self):
        self.assertEqual(discounted_total(1000, 15, max_discount_cents=100), 900)

    def test_negative_cap_is_rejected_even_when_discount_is_zero(self):
        for subtotal_cents, percent in [(1000, 15), (0, 15), (1000, 0), (1, 1)]:
            with self.subTest(subtotal_cents=subtotal_cents, percent=percent):
                with self.assertRaises(ValueError):
                    discounted_total(subtotal_cents, percent, max_discount_cents=-1)

    def test_none_cap_preserves_rounded_discount(self):
        self.assertEqual(discounted_total(999, 15, max_discount_cents=None), 850)

    def test_cap_at_or_above_discount_preserves_rounded_discount(self):
        for cap in [149, 150]:
            with self.subTest(cap=cap):
                self.assertEqual(discounted_total(999, 15, max_discount_cents=cap), 850)

    def test_zero_cap_disables_full_discount(self):
        self.assertEqual(discounted_total(1000, 100, max_discount_cents=0), 1000)

    def test_cap_is_keyword_only(self):
        with self.assertRaises(TypeError):
            discounted_total(1000, 15, 100)

    def test_zero_cap_still_rejects_invalid_subtotal_and_percent(self):
        for subtotal_cents, percent in [(-1, 15), (1000, -1), (1000, 101)]:
            with self.subTest(subtotal_cents=subtotal_cents, percent=percent):
                with self.assertRaises(ValueError):
                    discounted_total(subtotal_cents, percent, max_discount_cents=0)

    def test_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            discounted_total(-1, 15)

    def test_invalid_percent(self):
        for percent in [-1, 101]:
            with self.subTest(percent=percent), self.assertRaises(ValueError):
                discounted_total(1000, percent)
