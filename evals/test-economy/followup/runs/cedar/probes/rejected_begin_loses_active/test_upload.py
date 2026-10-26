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
        session.begin()
        self.assertTrue(session.cancel())
        self.assertEqual((session.state, session.result), ("cancelled", None))

    def test_unknown_completion_preserves_current_attempt(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertFalse(session.complete(attempt + 1, "wrong.csv"))
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "right.csv"))
        self.assertEqual((session.state, session.result), ("done", "right.csv"))

    def test_events_before_begin_preserve_idle(self):
        session = UploadSession()
        self.assertFalse(session.complete(1, "unexpected.csv"))
        self.assertEqual((session.state, session.result), ("idle", None))
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("idle", None))

    def test_rejected_begin_preserves_the_active_attempt(self):
        session = UploadSession()
        attempt = session.begin()
        with self.assertRaises(RuntimeError):
            session.begin()
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "right.csv"))
        self.assertEqual((session.state, session.result), ("done", "right.csv"))

    def test_completed_result_survives_repeated_completion_and_cancel(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertTrue(session.complete(attempt, "original.csv"))
        self.assertEqual((session.state, session.result), ("done", "original.csv"))
        for attempt_id in [attempt, attempt + 1]:
            with self.subTest(attempt_id=attempt_id):
                self.assertFalse(session.complete(attempt_id, "replacement.csv"))
                self.assertEqual((session.state, session.result), ("done", "original.csv"))
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("done", "original.csv"))

    def test_cancelled_attempt_ignores_late_completion_and_repeated_cancel(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertTrue(session.cancel())
        self.assertEqual((session.state, session.result), ("cancelled", None))
        self.assertFalse(session.complete(attempt, "late.csv"))
        self.assertEqual((session.state, session.result), ("cancelled", None))
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("cancelled", None))

    def test_restarts_keep_old_results_out_of_new_attempts(self):
        for first_outcome in ["done", "cancelled"]:
            with self.subTest(first_outcome=first_outcome):
                session = UploadSession()
                first = session.begin()
                self.assertIsInstance(first, int)
                self.assertGreater(first, 0)
                if first_outcome == "done":
                    self.assertTrue(session.complete(first, "first.csv"))
                    self.assertEqual((session.state, session.result), ("done", "first.csv"))
                else:
                    self.assertTrue(session.cancel())
                    self.assertEqual((session.state, session.result), ("cancelled", None))

                second = session.begin()
                self.assertIsInstance(second, int)
                self.assertGreater(second, first)
                self.assertEqual((session.state, session.result), ("waiting", None))
                self.assertFalse(session.complete(first, "stale.csv"))
                self.assertEqual((session.state, session.result), ("waiting", None))
                self.assertTrue(session.complete(second, "second.csv"))
                self.assertEqual((session.state, session.result), ("done", "second.csv"))
                self.assertFalse(session.complete(first, "later.csv"))
                self.assertEqual((session.state, session.result), ("done", "second.csv"))

                third = session.begin()
                self.assertIsInstance(third, int)
                self.assertGreater(third, second)
                self.assertEqual((session.state, session.result), ("waiting", None))
                for old_attempt in [first, second]:
                    with self.subTest(old_attempt=old_attempt):
                        self.assertFalse(session.complete(old_attempt, "obsolete.csv"))
                        self.assertEqual((session.state, session.result), ("waiting", None))
                self.assertTrue(session.complete(third, "third.csv"))
                self.assertEqual((session.state, session.result), ("done", "third.csv"))
