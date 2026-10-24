import unittest

from booking import Receipt, TicketDesk


class TicketDeskTests(unittest.TestCase):
    def test_first_request_accepts_customer_and_sets_owner(self):
        desk = TicketDesk()
        self.assertIsNone(desk.owner)

        receipt = desk.reserve("Alice", "alice-first")

        self.assertEqual(Receipt("Alice", True), receipt)
        self.assertEqual("Alice", desk.owner)

    def test_occupied_seat_refuses_other_customers_and_keeps_owner(self):
        desk = TicketDesk()
        desk.reserve("Alice", "alice-first")

        self.assertEqual(Receipt("Bob", False), desk.reserve("Bob", "bob-first"))
        self.assertEqual("Alice", desk.owner)
        self.assertEqual(Receipt("Carol", False), desk.reserve("Carol", "carol-first"))
        self.assertEqual("Alice", desk.owner)

    def test_repeated_requests_return_original_receipts(self):
        desk = TicketDesk()
        accepted = desk.reserve("Alice", "alice-first")
        refused = desk.reserve("Bob", "bob-first")
        self.assertEqual(Receipt("Alice", True), accepted)
        self.assertEqual(Receipt("Bob", False), refused)

        self.assertEqual(accepted, desk.reserve("Alice", "alice-first"))
        self.assertEqual("Alice", desk.owner)
        self.assertEqual(refused, desk.reserve("Bob", "bob-first"))
        self.assertEqual("Alice", desk.owner)

    def test_reusing_request_id_for_another_customer_raises_without_changing_booking(self):
        desk = TicketDesk()
        accepted = desk.reserve("Alice", "alice-first")
        refused = desk.reserve("Bob", "bob-first")

        for request_id, customer, original in (
            ("alice-first", "Alice", accepted),
            ("bob-first", "Bob", refused),
        ):
            with self.subTest(request_id=request_id):
                with self.assertRaises(ValueError):
                    desk.reserve("Carol", request_id)
                self.assertEqual("Alice", desk.owner)
                self.assertEqual(original, desk.reserve(customer, request_id))

        self.assertEqual(Receipt("Dave", False), desk.reserve("Dave", "dave-first"))
        self.assertEqual("Alice", desk.owner)
