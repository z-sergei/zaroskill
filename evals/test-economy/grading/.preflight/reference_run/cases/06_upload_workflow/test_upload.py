import unittest
from upload import UploadSession


class UploadTests(unittest.TestCase):
    def test_initial_ignored_events_then_success(self):
        session = UploadSession()
        self.assertEqual((session.state, session.result), ("idle", None))
        self.assertFalse(session.cancel())
        self.assertFalse(session.complete(1, "early"))
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
        self.assertIsInstance(attempt, int)
        self.assertGreater(attempt, 0)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "first"))
        self.assertEqual((session.state, session.result), ("done", "first"))

    def test_wrong_and_duplicate_completion_preserve_result_and_progress(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertFalse(session.complete(attempt + 1, "wrong"))
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "right"))
        self.assertFalse(session.complete(attempt, "duplicate"))
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("done", "right"))

    def test_cancel_late_completion_restart_and_stale_completion(self):
        session = UploadSession()
        old = session.begin()
        self.assertTrue(session.cancel())
        self.assertFalse(session.complete(old, "late"))
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("cancelled", None))
        current = session.begin()
        self.assertGreater(current, old)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertFalse(session.complete(old, "stale"))
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(current, "current"))
        self.assertEqual((session.state, session.result), ("done", "current"))

    def test_restart_after_success_clears_result_and_rejects_previous_id(self):
        session = UploadSession()
        old = session.begin()
        session.complete(old, "old result")
        current = session.begin()
        self.assertGreater(current, old)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertFalse(session.complete(old, "stale"))
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(current, "fresh"))
        self.assertEqual((session.state, session.result), ("done", "fresh"))

    def test_begin_while_waiting_preserves_active_attempt(self):
        session = UploadSession()
        attempt = session.begin()
        with self.assertRaises(RuntimeError):
            session.begin()
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "still active"))
        self.assertEqual((session.state, session.result), ("done", "still active"))
