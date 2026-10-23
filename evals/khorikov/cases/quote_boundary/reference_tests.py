"""Evaluator-only reference tests, excluded from agent workspaces."""
import unittest
from pricing import Line, Quote, quote


class QuoteContractTests(unittest.TestCase):
    def test_large_integer_discount_preserves_exact_minor_units(self):
        result = quote([Line(9_007_199_254_740_993, 1)], 50, 250)
        self.assertEqual(
            (9_007_199_254_740_993, 4_503_599_627_370_497, 0, 4_503_599_627_370_496),
            (result.gross_minor, result.discount_minor, result.shipping_minor, result.total_minor),
        )

    def test_rounds_once_on_combined_gross_and_consumes_generator(self):
        self.assertEqual(quote((line for line in [Line(1, 1), Line(4, 1)]), 50, 20), Quote(5, 3, 20, 22))

    def test_free_shipping_threshold_is_inclusive_and_after_discount(self):
        self.assertEqual(quote([Line(2500, 2)], 0, 200), Quote(5000, 0, 0, 5000))
        self.assertEqual(quote([Line(2500, 2)], 1, 200), Quote(5000, 50, 200, 5150))

    def test_quantity_and_digital_shipping(self):
        self.assertEqual(quote([Line(701, 3)], 10, 300, digital=True), Quote(2103, 210, 0, 1893))

    def test_zero_price_full_discount_and_immutable_quote(self):
        self.assertEqual(quote([Line(10, 3)], 100, 20), Quote(30, 30, 20, 20))
        result = quote([Line(0, 1)], 0, 0)
        self.assertEqual(result, Quote(0, 0, 0, 0))
        try:
            result.total_minor = 5
        except Exception:
            pass  # The contract promises unchanged values, not a rejection exception.
        self.assertEqual((result.gross_minor, result.discount_minor, result.shipping_minor, result.total_minor), (0, 0, 0, 0))

    def test_invalid_inputs(self):
        cases = [([], 0, 0), ([Line(-1, 1)], 0, 0), ([Line(1, 0)], 0, 0),
                 ([Line(1, True)], 0, 0), ([Line(True, 1)], 0, 0),
                 ([Line(1, 1)], True, 0), ([Line(1, 1)], 101, 0), ([Line(1, 1)], 0, True)]
        for lines, percent, shipping in cases:
            with self.subTest(lines=lines, percent=percent, shipping=shipping):
                with self.assertRaises(ValueError):
                    quote(lines, percent, shipping)
