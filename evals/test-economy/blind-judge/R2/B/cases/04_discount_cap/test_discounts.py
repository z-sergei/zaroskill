import unittest
from discounts import discounted_total


class DiscountTests(unittest.TestCase):
    def test_cap_limits_discount_not_payable_total(self):
        self.assertEqual(
            discounted_total(1000, 30, max_discount_cents=200), 800
        )

    def test_negative_cap_is_rejected_even_with_zero_discount(self):
        for subtotal, percent in [(1000, 30), (0, 30), (1000, 0)]:
            with self.subTest(subtotal=subtotal, percent=percent):
                with self.assertRaises(ValueError):
                    discounted_total(subtotal, percent, max_discount_cents=-1)

    def test_zero_equal_and_larger_caps_keep_the_correct_payable_total(self):
        # 15% of 999 gives a discount of 149 whole cents.
        for cap, expected in [(0, 999), (149, 850), (200, 850)]:
            with self.subTest(cap=cap):
                self.assertEqual(
                    discounted_total(999, 15, max_discount_cents=cap), expected
                )

    def test_explicit_none_preserves_rounded_percentage_discount(self):
        self.assertEqual(
            discounted_total(999, 15, max_discount_cents=None), 850
        )

    def test_cap_must_be_passed_by_keyword(self):
        with self.assertRaises(TypeError):
            discounted_total(1000, 30, 200)

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
