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
        self.assertIs(session.complete(attempt, "report.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "report.csv"))
        self.assertIs(session.complete(attempt, "duplicate.csv"), False)
        self.assertEqual((session.state, session.result), ("done", "report.csv"))
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("done", "report.csv"))

    def test_cancel_rejects_late_completion_and_repeated_cancel(self):
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
        for unknown_id in (-1, 0, attempt + 1):
            with self.subTest(unknown_id=unknown_id):
                self.assertIs(session.complete(unknown_id, "wrong.csv"), False)
                self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "right.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "right.csv"))

    def test_events_while_idle_do_not_prevent_a_later_upload(self):
        session = UploadSession()
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("idle", None))
        self.assertIs(session.complete(1, "unrequested.csv"), False)
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
        self.assertIsInstance(attempt, int)
        self.assertGreater(attempt, 0)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "requested.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "requested.csv"))

    def test_rejected_begin_preserves_the_active_attempt(self):
        session = UploadSession()
        attempt = session.begin()
        with self.assertRaises(RuntimeError):
            session.begin()
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "original.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "original.csv"))

    def test_restart_after_success_clears_result_and_rejects_old_completion(self):
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

    def test_restart_after_cancel_rejects_old_completion_and_accepts_new_attempt(self):
        session = UploadSession()
        first = session.begin()
        self.assertIs(session.cancel(), True)
        self.assertEqual((session.state, session.result), ("cancelled", None))

        second = session.begin()
        self.assertIsInstance(second, int)
        self.assertGreater(second, first)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(first, "cancelled.csv"), False)
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(second, "replacement.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "replacement.csv"))
