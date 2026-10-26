import unittest
from upload import UploadSession


class Contract(unittest.TestCase):
    def test_state_lifecycle(self):
        s = UploadSession()
        self.assertEqual((s.state, s.result), ("idle", None))
        for operation in (lambda: s.complete(99, "x"), s.cancel):
            self.assertIs(operation(), False)
            self.assertEqual((s.state, s.result), ("idle", None))
        first = s.begin()
        self.assertIsInstance(first, int)
        self.assertGreater(first, 0)
        self.assertEqual((s.state, s.result), ("waiting", None))
        with self.assertRaises(RuntimeError):
            s.begin()
        self.assertEqual((s.state, s.result), ("waiting", None))
        self.assertIs(s.complete(first + 17, "foreign"), False)
        self.assertEqual((s.state, s.result), ("waiting", None))
        self.assertIs(s.complete(first, "a"), True)
        self.assertEqual((s.state, s.result), ("done", "a"))
        self.assertIs(s.complete(first, "overwrite"), False)
        self.assertIs(s.cancel(), False)
        self.assertEqual((s.state, s.result), ("done", "a"))
        second = s.begin()
        self.assertGreater(second, first)
        self.assertEqual((s.state, s.result), ("waiting", None))
        self.assertIs(s.complete(first, "old"), False)
        self.assertEqual((s.state, s.result), ("waiting", None))
        self.assertIs(s.cancel(), True)
        self.assertEqual((s.state, s.result), ("cancelled", None))
        self.assertIs(s.complete(second, "late"), False)
        self.assertIs(s.cancel(), False)
        self.assertEqual((s.state, s.result), ("cancelled", None))
        third = s.begin()
        self.assertGreater(third, second)
        self.assertIs(s.complete(second, "stale"), False)
        self.assertEqual((s.state, s.result), ("waiting", None))
        self.assertIs(s.complete(third, "c"), True)
        self.assertEqual((s.state, s.result), ("done", "c"))
