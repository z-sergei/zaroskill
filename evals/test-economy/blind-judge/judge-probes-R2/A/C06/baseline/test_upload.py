import unittest
from upload import UploadSession


class UploadTests(unittest.TestCase):
    def test_successful_upload(self):
        session = UploadSession()
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
        self.assertIsInstance(attempt, int)
        self.assertGreater(attempt, 0)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "report.csv"))
        self.assertEqual((session.state, session.result), ("done", "report.csv"))

    def test_cancel_active_upload(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertTrue(session.cancel())
        self.assertEqual((session.state, session.result), ("cancelled", None))
        self.assertFalse(session.complete(attempt, "late.csv"))
        self.assertEqual((session.state, session.result), ("cancelled", None))
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("cancelled", None))

    def test_unknown_completion_preserves_current_attempt(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertFalse(session.complete(attempt + 1, "wrong.csv"))
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "right.csv"))
        self.assertEqual((session.state, session.result), ("done", "right.csv"))

    def test_idle_rejects_completion_and_cancellation(self):
        session = UploadSession()
        self.assertFalse(session.complete(1, "unsolicited.csv"))
        self.assertEqual((session.state, session.result), ("idle", None))
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
        self.assertTrue(session.complete(attempt, "first.csv"))
        self.assertEqual((session.state, session.result), ("done", "first.csv"))

    def test_completion_wins_before_cancel_and_duplicate_completion(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertTrue(session.complete(attempt, "accepted.csv"))
        self.assertEqual((session.state, session.result), ("done", "accepted.csv"))
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("done", "accepted.csv"))
        for other_id in (attempt, attempt + 1):
            with self.subTest(completion_id=other_id):
                self.assertFalse(session.complete(other_id, "replacement.csv"))
                self.assertEqual((session.state, session.result), ("done", "accepted.csv"))

    def test_rejected_begin_preserves_the_waiting_attempt(self):
        session = UploadSession()
        attempt = session.begin()
        with self.assertRaises(RuntimeError):
            session.begin()
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "original.csv"))
        self.assertEqual((session.state, session.result), ("done", "original.csv"))

    def test_restart_after_success_clears_result_and_rejects_old_completions(self):
        session = UploadSession()
        previous_attempts = []
        # Three successes distinguish monotonic identity from a two-id cycle.
        for value in ("first.csv", "second.csv", "third.csv"):
            with self.subTest(result=value):
                attempt = session.begin()
                self.assertIsInstance(attempt, int)
                self.assertGreater(attempt, previous_attempts[-1] if previous_attempts else 0)
                self.assertEqual((session.state, session.result), ("waiting", None))
                for old_attempt in previous_attempts:
                    with self.subTest(stale_id=old_attempt):
                        self.assertFalse(session.complete(old_attempt, "stale.csv"))
                        self.assertEqual((session.state, session.result), ("waiting", None))
                self.assertTrue(session.complete(attempt, value))
                self.assertEqual((session.state, session.result), ("done", value))
                previous_attempts.append(attempt)

    def test_restart_after_cancel_rejects_old_completion_before_accepting_new(self):
        session = UploadSession()
        cancelled_attempt = session.begin()
        self.assertTrue(session.cancel())
        self.assertEqual((session.state, session.result), ("cancelled", None))
        current_attempt = session.begin()
        self.assertIsInstance(current_attempt, int)
        self.assertGreater(current_attempt, cancelled_attempt)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertFalse(session.complete(cancelled_attempt, "stale.csv"))
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(current_attempt, "current.csv"))
        self.assertEqual((session.state, session.result), ("done", "current.csv"))
