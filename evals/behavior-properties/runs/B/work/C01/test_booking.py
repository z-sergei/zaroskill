import unittest

from booking import Receipt, TicketDesk


class TicketDeskTests(unittest.TestCase):
    def test_first_reservation_assigns_the_seat(self):
        desk = TicketDesk()
        self.assertIsNone(desk.owner)

        receipt = desk.reserve("Ada", "booking-a")

        self.assertEqual(Receipt("Ada", True), receipt)
        self.assertEqual("Ada", desk.owner)

    def test_another_customer_cannot_take_the_occupied_seat(self):
        desk = TicketDesk()
        self.assertEqual(Receipt("Ada", True), desk.reserve("Ada", "booking-a"))

        receipt = desk.reserve("Ben", "booking-b")

        self.assertEqual(Receipt("Ben", False), receipt)
        self.assertEqual("Ada", desk.owner)

    def test_repeating_a_request_returns_its_original_receipt(self):
        desk = TicketDesk()
        accepted = desk.reserve("Ada", "booking-a")
        refused = desk.reserve("Ben", "booking-b")
        self.assertEqual(Receipt("Ada", True), accepted)
        self.assertEqual(Receipt("Ben", False), refused)

        self.assertEqual(accepted, desk.reserve("Ada", "booking-a"))
        self.assertEqual(refused, desk.reserve("Ben", "booking-b"))
        self.assertEqual("Ada", desk.owner)

    def test_reusing_an_id_for_another_customer_preserves_the_booking(self):
        for reused_id in ("booking-a", "booking-b"):
            with self.subTest(reused_id=reused_id):
                desk = TicketDesk()
                accepted = desk.reserve("Ada", "booking-a")
                refused = desk.reserve("Ben", "booking-b")
                self.assertEqual(Receipt("Ada", True), accepted)
                self.assertEqual(Receipt("Ben", False), refused)

                with self.assertRaises(ValueError):
                    desk.reserve("Cara", reused_id)

                self.assertEqual("Ada", desk.owner)
                self.assertEqual(accepted, desk.reserve("Ada", "booking-a"))
                self.assertEqual(refused, desk.reserve("Ben", "booking-b"))
                self.assertEqual(Receipt("Dara", False), desk.reserve("Dara", "booking-d"))
                self.assertEqual("Ada", desk.owner)
