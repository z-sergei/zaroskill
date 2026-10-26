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

    def test_idle_rejects_completion_and_cancel_without_changes(self):
        session = UploadSession()
        for attempt in [-1, 0, 1]:
            with self.subTest(attempt=attempt):
                self.assertIs(session.complete(attempt, "unexpected.csv"), False)
                self.assertEqual((session.state, session.result), ("idle", None))
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
        self.assertIs(session.complete(attempt, "accepted.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "accepted.csv"))

    def test_rejected_begin_preserves_the_attempt_that_can_complete(self):
        session = UploadSession()
        attempt = session.begin()
        with self.assertRaises(RuntimeError):
            session.begin()
        self.assertEqual((session.state, session.result), ("waiting", None))
        self.assertIs(session.complete(attempt, "original.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "original.csv"))

    def test_completion_before_cancel_keeps_first_result(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertIs(session.complete(attempt, "first.csv"), True)
        self.assertEqual((session.state, session.result), ("done", "first.csv"))
        self.assertIs(session.complete(attempt, "duplicate.csv"), False)
        self.assertEqual((session.state, session.result), ("done", "first.csv"))
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("done", "first.csv"))
        self.assertIs(session.complete(attempt + 1, "foreign.csv"), False)
        self.assertEqual((session.state, session.result), ("done", "first.csv"))

    def test_cancel_before_completion_keeps_cancelled_state(self):
        session = UploadSession()
        attempt = session.begin()
        self.assertIs(session.cancel(), True)
        self.assertEqual((session.state, session.result), ("cancelled", None))
        self.assertIs(session.complete(attempt, "late.csv"), False)
        self.assertEqual((session.state, session.result), ("cancelled", None))
        self.assertIs(session.cancel(), False)
        self.assertEqual((session.state, session.result), ("cancelled", None))
        self.assertIs(session.complete(attempt + 1, "foreign.csv"), False)
        self.assertEqual((session.state, session.result), ("cancelled", None))

    def test_restarts_clear_results_and_reject_previous_attempts(self):
        for previous_state in ["done", "cancelled"]:
            with self.subTest(previous_state=previous_state):
                session = UploadSession()
                first = session.begin()
                if previous_state == "done":
                    self.assertIs(session.complete(first, "first.csv"), True)
                    self.assertEqual((session.state, session.result), ("done", "first.csv"))
                else:
                    self.assertIs(session.cancel(), True)
                    self.assertEqual((session.state, session.result), ("cancelled", None))

                second = session.begin()
                self.assertIsInstance(second, int)
                self.assertGreater(second, first)
                self.assertEqual((session.state, session.result), ("waiting", None))
                self.assertIs(session.complete(first, "late-first.csv"), False)
                self.assertEqual((session.state, session.result), ("waiting", None))
                self.assertIs(session.complete(second, "second.csv"), True)
                self.assertEqual((session.state, session.result), ("done", "second.csv"))

                third = session.begin()
                self.assertIsInstance(third, int)
                self.assertGreater(third, second)
                self.assertEqual((session.state, session.result), ("waiting", None))
                for old_attempt in [first, second]:
                    with self.subTest(old_attempt=old_attempt):
                        self.assertIs(session.complete(old_attempt, "obsolete.csv"), False)
                        self.assertEqual((session.state, session.result), ("waiting", None))
                self.assertIs(session.complete(third, "third.csv"), True)
                self.assertEqual((session.state, session.result), ("done", "third.csv"))
