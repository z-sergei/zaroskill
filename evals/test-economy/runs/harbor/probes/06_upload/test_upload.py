import unittest
from upload import UploadSession


class UploadTests(unittest.TestCase):
    def test_success_survives_duplicate_completion_and_cancel(self):
        session = UploadSession()
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
        self.assertIsInstance(attempt, int)
        self.assertGreater(attempt, 0)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "report.csv"))
        self.assertEqual((session.state, session.result), ("done", "report.csv"))
        self.assertFalse(session.complete(attempt, "duplicate.csv"))
        self.assertEqual((session.state, session.result), ("done", "report.csv"))
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("done", "report.csv"))

    def test_cancel_rejects_late_completion_and_repeated_cancel(self):
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
        for unknown_id in (-1, 0, attempt + 1):
            with self.subTest(unknown_id=unknown_id):
                self.assertFalse(session.complete(unknown_id, "wrong.csv"))
                self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "right.csv"))
        self.assertEqual((session.state, session.result), ("done", "right.csv"))

    def test_events_while_idle_do_not_prevent_a_later_upload(self):
        session = UploadSession()
        self.assertFalse(session.cancel())
        self.assertEqual((session.state, session.result), ("idle", None))
        self.assertFalse(session.complete(1, "unrequested.csv"))
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
        self.assertIsInstance(attempt, int)
        self.assertGreater(attempt, 0)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "requested.csv"))
        self.assertEqual((session.state, session.result), ("done", "requested.csv"))

    def test_rejected_begin_preserves_the_active_attempt(self):
        session = UploadSession()
        attempt = session.begin()
        with self.assertRaises(RuntimeError):
            session.begin()
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(attempt, "original.csv"))
        self.assertEqual((session.state, session.result), ("done", "original.csv"))

    def test_restart_after_success_clears_result_and_rejects_old_completion(self):
        session = UploadSession()
        first = session.begin()
        self.assertTrue(session.complete(first, "first.csv"))
        self.assertEqual((session.state, session.result), ("done", "first.csv"))

        second = session.begin()
        self.assertIsInstance(second, int)
        self.assertGreater(second, first)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertFalse(session.complete(first, "obsolete.csv"))
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(second, "second.csv"))
        self.assertEqual((session.state, session.result), ("done", "second.csv"))

    def test_restart_after_cancel_rejects_old_completion_and_accepts_new_attempt(self):
        session = UploadSession()
        first = session.begin()
        self.assertTrue(session.cancel())
        self.assertEqual((session.state, session.result), ("cancelled", None))

        second = session.begin()
        self.assertIsInstance(second, int)
        self.assertGreater(second, first)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertFalse(session.complete(first, "cancelled.csv"))
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertTrue(session.complete(second, "replacement.csv"))
        self.assertEqual((session.state, session.result), ("done", "replacement.csv"))
