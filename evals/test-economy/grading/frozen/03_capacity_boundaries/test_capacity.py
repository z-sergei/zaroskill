import unittest
from capacity import CapacityError, handle_request, reserve


class ReservationTests(unittest.TestCase):
    def test_domain_allows_exact_capacity(self):
        self.assertEqual(reserve(7, 3, 10), 10)

    def test_domain_rejects_over_capacity(self):
        with self.assertRaises(CapacityError):
            reserve(7, 4, 10)

    def test_domain_allows_zero_at_capacity(self):
        self.assertEqual(reserve(10, 0, 10), 10)


class RequestTests(unittest.TestCase):
    def test_request_reports_exact_capacity_without_mutating_input(self):
        payload = {"used": 7, "requested": 3, "limit": 10}
        self.assertEqual(handle_request(payload), {"status": "ok", "used": 10})
        self.assertEqual(payload, {"used": 7, "requested": 3, "limit": 10})

    def test_request_maps_over_capacity_without_mutating_input(self):
        payload = {"used": 7, "requested": 4, "limit": 10}
        self.assertEqual(handle_request(payload), {"status": "full", "used": 7})
        self.assertEqual(payload, {"used": 7, "requested": 4, "limit": 10})

    def test_request_reports_success_for_zero_at_capacity(self):
        self.assertEqual(
            handle_request({"used": 10, "requested": 0, "limit": 10}),
            {"status": "ok", "used": 10},
        )
