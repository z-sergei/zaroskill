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
        self.assertIs(session.complete(attempt, "report.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "report.csv"))

    def test_cancelled_upload_rejects_late_completion_and_repeated_cancel(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertIs(session.cancel(), True)
        self.assertEqual((session.state, session.result), ("cancelled", None))
        self.assertIs(session.complete(attempt, "late.csv"), False)
        self.assertEqual((session.state, session.result), ("cancelled", None))
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("cancelled", None))

    def test_unknown_completion_preserves_current_attempt(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertIs(session.complete(attempt + 1, "wrong.csv"), False)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "right.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "right.csv"))

    def test_idle_session_ignores_completion_and_cancel(self):
        session = UploadSession()
        self.assertIs(session.complete(1, "unsolicited.csv"), False)
        self.assertEqual((session.state, session.result), ("idle", None))
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
        self.assertIsInstance(attempt, int)
        self.assertGreater(attempt, 0)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "requested.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "requested.csv"))

    def test_rejected_begin_keeps_the_current_attempt_finishable(self):
        session = UploadSession()
        attempt = session.begin()
        with self.assertRaises(RuntimeError):
            session.begin()
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "original.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "original.csv"))

    def test_completed_upload_preserves_result_after_duplicate_and_cancel(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertIs(session.complete(attempt, "first.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "first.csv"))
        self.assertIs(session.complete(attempt, "duplicate.csv"), False)
        self.assertEqual((session.state, session.result), ("done", "first.csv"))
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("done", "first.csv"))

    def test_restart_after_success_clears_result_and_rejects_old_attempt(self):
        session = UploadSession()
        first = session.begin()
        self.assertIs(session.complete(first, "first.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "first.csv"))
        second = session.begin()
        self.assertIsInstance(second, int)
        self.assertGreater(second, first)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(first, "obsolete.csv"), False)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(second, "second.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "second.csv"))

    def test_restart_after_cancel_ignores_old_result_before_and_after_success(self):
        session = UploadSession()
        first = session.begin()
        self.assertIs(session.cancel(), True)
        self.assertEqual((session.state, session.result), ("cancelled", None))
        second = session.begin()
        self.assertIsInstance(second, int)
        self.assertGreater(second, first)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(first, "cancelled-before.csv"), False)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(second, "current.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "current.csv"))
        self.assertIs(session.complete(first, "cancelled-after.csv"), False)
        self.assertEqual((session.state, session.result), ("done", "current.csv"))
