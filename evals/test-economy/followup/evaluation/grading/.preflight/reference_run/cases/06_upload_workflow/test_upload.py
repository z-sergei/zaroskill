import unittest
from upload import UploadSession


class UploadTests(unittest.TestCase):
    def test_initial_ignored_events_then_success(self):
        session = UploadSession()
        self.assertEqual((session.state, session.result), ("idle", None))
        self.assertIs(session.cancel(), False)
        self.assertIs(session.complete(1, "early"), False)
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
        self.assertIsInstance(attempt, int)
        self.assertGreater(attempt, 0)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "first"), True)
        self.assertEqual((session.state, session.result), ("done", "first"))

    def test_wrong_and_duplicate_completion_preserve_result_and_progress(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertIs(session.complete(attempt + 1, "wrong"), False)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "right"), True)
        self.assertIs(session.complete(attempt, "duplicate"), False)
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("done", "right"))

    def test_cancel_late_completion_restart_and_stale_completion(self):
        session = UploadSession()
        old = session.begin()
        self.assertIs(session.cancel(), True)
        self.assertIs(session.complete(old, "late"), False)
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("cancelled", None))
        current = session.begin()
        self.assertGreater(current, old)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(old, "stale"), False)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(current, "current"), True)
        self.assertEqual((session.state, session.result), ("done", "current"))

    def test_repeated_success_restarts_clear_result_and_reject_old_ids(self):
        session = UploadSession()
        old = session.begin()
        self.assertIs(session.complete(old, "old result"), True)
        current = session.begin()
        self.assertGreater(current, old)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(old, "stale"), False)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(current, "fresh"), True)
        self.assertEqual((session.state, session.result), ("done", "fresh"))
        following = session.begin()
        self.assertGreater(following, current)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(old, "oldest callback"), False)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(following, "newest"), True)
        self.assertEqual((session.state, session.result), ("done", "newest"))

    def test_begin_while_waiting_preserves_active_attempt(self):
        session = UploadSession()
        attempt = session.begin()
        with self.assertRaises(RuntimeError):
            session.begin()
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "still active"), True)
        self.assertEqual((session.state, session.result), ("done", "still active"))
