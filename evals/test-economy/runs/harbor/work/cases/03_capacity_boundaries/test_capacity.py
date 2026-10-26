import unittest
from capacity import CapacityError, handle_request, reserve


class ReservationTests(unittest.TestCase):
    def test_domain_returns_new_usage_below_capacity(self):
        self.assertEqual(reserve(3, 2, 10), 5)

    def test_domain_allows_exact_capacity(self):
        self.assertEqual(reserve(7, 3, 10), 10)

    def test_domain_rejects_over_capacity(self):
        with self.assertRaises(CapacityError) as raised:
            reserve(7, 4, 10)
        self.assertIsInstance(raised.exception, ValueError)

    def test_domain_allows_zero_at_capacity(self):
        self.assertEqual(reserve(10, 0, 10), 10)


class RequestTests(unittest.TestCase):
    def test_request_reports_partial_usage_without_mutating_input(self):
        payload = {"used": 3, "requested": 2, "limit": 10}
        self.assertEqual(handle_request(payload), {"status": "ok", "used": 5})
        self.assertEqual(payload, {"used": 3, "requested": 2, "limit": 10})

    def test_request_reports_exact_capacity_without_mutating_input(self):
        payload = {"used": 7, "requested": 3, "limit": 10}
        self.assertEqual(handle_request(payload), {"status": "ok", "used": 10})
        self.assertEqual(payload, {"used": 7, "requested": 3, "limit": 10})

    def test_request_maps_over_capacity_without_mutating_input(self):
        payload = {"used": 7, "requested": 4, "limit": 10}
        self.assertEqual(handle_request(payload), {"status": "full", "used": 7})
        self.assertEqual(payload, {"used": 7, "requested": 4, "limit": 10})

    def test_request_reports_success_for_zero_at_capacity_without_mutating_input(self):
        payload = {"used": 10, "requested": 0, "limit": 10}
        self.assertEqual(
            handle_request(payload),
            {"status": "ok", "used": 10},
        )
        self.assertEqual(payload, {"used": 10, "requested": 0, "limit": 10})
