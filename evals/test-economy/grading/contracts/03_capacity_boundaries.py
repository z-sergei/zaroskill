import unittest
from capacity import CapacityError, handle_request, reserve


class Contract(unittest.TestCase):
    def test_both_public_entries(self):
        for used, requested, limit in [(0, 0, 0), (2, 3, 5), (2, 4, 5), (5, 0, 5), (1, 2, 9)]:
            payload = dict(used=used, requested=requested, limit=limit)
            before = dict(payload)
            fits = requested <= limit - used
            with self.subTest(entry="domain", payload=payload):
                if fits:
                    self.assertEqual(reserve(used, requested, limit), used + requested)
                else:
                    with self.assertRaises(CapacityError):
                        reserve(used, requested, limit)
            with self.subTest(entry="request", payload=payload):
                expected = {"status": "ok" if fits else "full", "used": used + requested if fits else used}
                self.assertEqual(handle_request(payload), expected)
                self.assertEqual(payload, before)
