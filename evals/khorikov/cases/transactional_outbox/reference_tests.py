"""Evaluator-only reference suite. Excluded from the evaluated agent's workspace."""

import tempfile
import unittest
from pathlib import Path

from fulfillment import (
    IdempotencyConflict,
    InsufficientStock,
    dispatch_pending,
    find_order,
    initialize,
    place_order,
    stock_levels,
)


class Recorder:
    def __init__(self, failures=0):
        self.calls = []
        self.failures = failures

    def send(self, *, recipient, payload, idempotency_key):
        self.calls.append((recipient, payload, idempotency_key))
        if self.failures:
            self.failures -= 1
            raise ConnectionError("provider did not confirm delivery")


class FulfillmentContract(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.database = Path(directory.name) / "shop.sqlite"
        initialize(self.database, {"apple": (10, 125), "tea": (8, 350)})

    def test_fresh_order_is_delivered_after_an_earlier_batch_completed(self):
        place_order(self.database, "earlier", "first@example.invalid", [("tea", 1)])
        self.assertEqual(1, dispatch_pending(self.database, Recorder()))
        later = place_order(self.database, "later", "later@example.invalid", [("apple", 2)])
        recorder = Recorder()

        self.assertEqual(1, dispatch_pending(self.database, recorder))
        self.assertEqual([("later@example.invalid", {
            "type": "order.confirmed", "order_id": later.order_id,
            "items": [{"sku": "apple", "quantity": 2}], "total_cents": 250,
        }, f"order-confirmation:{later.order_id}")], recorder.calls)
        self.assertEqual(0, dispatch_pending(self.database, recorder))
        self.assertEqual(1, len(recorder.calls))

    def test_creation_order_is_independent_of_recipient_and_sku_order(self):
        first = place_order(self.database, "purchase-z", "z@example.invalid", [("tea", 1)])
        second = place_order(self.database, "purchase-a", "a@example.invalid", [("apple", 2)])
        third = place_order(self.database, "purchase-m", "m@example.invalid", [("tea", 2)])
        recorder = Recorder()

        self.assertEqual(3, dispatch_pending(self.database, recorder))
        self.assertEqual([
            ("z@example.invalid", {"type": "order.confirmed", "order_id": first.order_id,
             "items": [{"sku": "tea", "quantity": 1}], "total_cents": 350},
             f"order-confirmation:{first.order_id}"),
            ("a@example.invalid", {"type": "order.confirmed", "order_id": second.order_id,
             "items": [{"sku": "apple", "quantity": 2}], "total_cents": 250},
             f"order-confirmation:{second.order_id}"),
            ("m@example.invalid", {"type": "order.confirmed", "order_id": third.order_id,
             "items": [{"sku": "tea", "quantity": 2}], "total_cents": 700},
             f"order-confirmation:{third.order_id}"),
        ], recorder.calls)
        self.assertEqual(0, dispatch_pending(self.database, recorder))
        self.assertEqual(3, len(recorder.calls))

    def test_order_is_committed_and_visible_through_fresh_readers(self):
        order = place_order(self.database, "purchase-1", "buyer@example.invalid", [("apple", 2), ("tea", 2)])
        self.assertEqual(950, order.total_cents)
        self.assertEqual(order, find_order(self.database, "purchase-1"))
        self.assertEqual({"apple": 8, "tea": 6}, stock_levels(self.database))

    def test_later_shortage_rolls_back_earlier_reservation_and_request_can_retry(self):
        with self.assertRaises(InsufficientStock):
            place_order(self.database, "purchase-1", "buyer@example.invalid", [("apple", 2), ("tea", 9)])
        self.assertEqual({"apple": 10, "tea": 8}, stock_levels(self.database))
        self.assertIsNone(find_order(self.database, "purchase-1"))
        recorder = Recorder()
        self.assertEqual(0, dispatch_pending(self.database, recorder))
        self.assertEqual([], recorder.calls)
        order = place_order(self.database, "purchase-1", "buyer@example.invalid", [("apple", 2), ("tea", 1)])
        self.assertEqual(600, order.total_cents)

    def test_unknown_later_sku_rolls_back_earlier_reservation(self):
        with self.assertRaises(InsufficientStock):
            place_order(self.database, "purchase-1", "buyer@example.invalid", [("apple", 2), ("zz-missing", 1)])
        self.assertEqual({"apple": 10, "tea": 8}, stock_levels(self.database))
        self.assertIsNone(find_order(self.database, "purchase-1"))

    def test_equivalent_retries_keep_one_reservation_and_one_confirmation(self):
        original = place_order(self.database, "purchase-1", "buyer@example.invalid", [("apple", 3), ("tea", 1)])
        try:
            retry = place_order(self.database, "purchase-1", "buyer@example.invalid", [("tea", 1), ("apple", 1), ("apple", 2)])
        except IdempotencyConflict as error:
            self.fail(f"An equivalent normalized request must reuse the order: {error}")
        self.assertEqual(original, retry)
        self.assertEqual({"apple": 7, "tea": 7}, stock_levels(self.database))
        recorder = Recorder()
        self.assertEqual(1, dispatch_pending(self.database, recorder))
        self.assertEqual(original, place_order(self.database, "purchase-1", "buyer@example.invalid", [("apple", 3), ("tea", 1)]))
        self.assertEqual({"apple": 7, "tea": 7}, stock_levels(self.database))
        self.assertEqual(0, dispatch_pending(self.database, recorder))
        self.assertEqual(1, len(recorder.calls))

    def test_conflicting_key_reuse_preserves_original_order(self):
        order = place_order(self.database, "purchase-1", "buyer@example.invalid", [("apple", 2)])
        for recipient, items in [("other@example.invalid", [("apple", 2)]), ("buyer@example.invalid", [("apple", 3)])]:
            with self.subTest(recipient=recipient, items=items):
                with self.assertRaises(IdempotencyConflict):
                    place_order(self.database, "purchase-1", recipient, items)
        self.assertEqual(order, find_order(self.database, "purchase-1"))
        self.assertEqual({"apple": 8, "tea": 8}, stock_levels(self.database))
        recorder = Recorder()
        self.assertEqual(1, dispatch_pending(self.database, recorder))
        self.assertEqual("buyer@example.invalid", recorder.calls[0][0])

    def test_duplicate_quantities_drive_price_inventory_and_confirmation(self):
        order = place_order(self.database, "purchase-1", "buyer@example.invalid", [("tea", 2), ("apple", 1), ("apple", 2)])
        self.assertEqual(1075, order.total_cents)
        self.assertEqual({"apple": 7, "tea": 6}, stock_levels(self.database))
        recorder = Recorder()
        self.assertEqual(1, dispatch_pending(self.database, recorder))
        self.assertEqual([("buyer@example.invalid", {
            "type": "order.confirmed",
            "order_id": order.order_id,
            "items": [{"sku": "apple", "quantity": 3}, {"sku": "tea", "quantity": 2}],
            "total_cents": 1075,
        }, f"order-confirmation:{order.order_id}")], recorder.calls)
        self.assertEqual(0, dispatch_pending(self.database, recorder))

    def test_failure_can_retry_the_same_external_effect(self):
        place_order(self.database, "purchase-1", "buyer@example.invalid", [("tea", 1)])
        recorder = Recorder(failures=1)
        with self.assertRaises(ConnectionError):
            dispatch_pending(self.database, recorder)
        self.assertEqual(1, dispatch_pending(self.database, recorder))
        self.assertEqual(2, len(recorder.calls))
        self.assertEqual(recorder.calls[0], recorder.calls[1])
        self.assertEqual(0, dispatch_pending(self.database, recorder))
        self.assertEqual({"apple": 10, "tea": 7}, stock_levels(self.database))

    def test_confirmed_delivery_survives_a_later_failure(self):
        first = place_order(self.database, "purchase-1", "first@example.invalid", [("tea", 1)])
        second = place_order(self.database, "purchase-2", "second@example.invalid", [("apple", 2)])
        third = place_order(self.database, "purchase-3", "third@example.invalid", [("apple", 1)])

        class FailsSecond(Recorder):
            def send(self, **kwargs):
                super().send(**kwargs)
                if len(self.calls) == 2:
                    raise ConnectionError("second delivery unconfirmed")

        recorder = FailsSecond()
        with self.assertRaises(ConnectionError):
            dispatch_pending(self.database, recorder)
        self.assertEqual([first.order_id, second.order_id], [call[1]["order_id"] for call in recorder.calls])
        self.assertEqual(2, dispatch_pending(self.database, recorder))
        self.assertEqual([first.order_id, second.order_id, second.order_id, third.order_id], [call[1]["order_id"] for call in recorder.calls])

    def test_invalid_input_has_no_effect(self):
        for items in [[], [("apple", 0)], [("apple", -1)], [("apple", True)], [("", 1)]]:
            with self.subTest(items=items):
                with self.assertRaises(ValueError):
                    place_order(self.database, "purchase-1", "buyer@example.invalid", items)
        self.assertEqual({"apple": 10, "tea": 8}, stock_levels(self.database))
        self.assertIsNone(find_order(self.database, "purchase-1"))
        self.assertEqual(0, dispatch_pending(self.database, Recorder()))


if __name__ == "__main__":
    unittest.main()
