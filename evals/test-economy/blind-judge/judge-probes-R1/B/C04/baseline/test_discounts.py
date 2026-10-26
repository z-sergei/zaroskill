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

    def test_cap_limits_the_discount_not_the_total(self):
        self.assertEqual(
            discounted_total(1000, 15, max_discount_cents=100), 900
        )

    def test_negative_cap_is_rejected_even_when_discount_is_zero(self):
        for subtotal, percent in ((1000, 15), (1000, 0), (0, 100), (1, 1)):
            with self.subTest(subtotal=subtotal, percent=percent):
                with self.assertRaises(ValueError):
                    discounted_total(subtotal, percent, max_discount_cents=-1)

    def test_zero_cap_leaves_the_subtotal_unchanged(self):
        self.assertEqual(
            discounted_total(1000, 100, max_discount_cents=0), 1000
        )

    def test_cap_at_or_above_the_discount_preserves_the_calculation(self):
        for subtotal, cap in ((1000, 150), (1000, 200), (999, 200)):
            with self.subTest(subtotal=subtotal, cap=cap):
                self.assertEqual(
                    discounted_total(subtotal, 15, max_discount_cents=cap), 850
                )

    def test_none_cap_preserves_the_uncapped_calculation(self):
        self.assertEqual(
            discounted_total(999, 15, max_discount_cents=None), 850
        )

    def test_cap_must_be_passed_by_keyword(self):
        with self.assertRaises(TypeError):
            discounted_total(1000, 15, 100)
