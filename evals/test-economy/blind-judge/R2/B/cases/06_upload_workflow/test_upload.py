import unittest
from upload import UploadSession


class UploadTests(unittest.TestCase):
    # Contract: only a waiting attempt may commit its own result. Rejected
    # events preserve observations AND ownership, checked by a later success.
    # Calls are sequential; these traces make no timing or concurrency claim.
    def assert_snapshot(self, session, state, result):
        self.assertEqual((session.state, session.result), (state, result))

    def begin_attempt(self, session, previous=0):
        attempt = session.begin()
        self.assertIs(type(attempt), int)
        self.assertGreater(attempt, previous)
        self.assert_snapshot(session, "waiting", None)
        return attempt

    def test_idle_ignores_completion_and_cancellation(self):
        session = UploadSession()
        self.assert_snapshot(session, "idle", None)
        self.assertIs(session.complete(1, "too-early.csv"), False)
        self.assert_snapshot(session, "idle", None)
        self.assertIs(session.cancel(), False)
        self.assert_snapshot(session, "idle", None)
        attempt = self.begin_attempt(session)
        self.assertIs(session.complete(attempt, "first.csv"), True)
        self.assert_snapshot(session, "done", "first.csv")

    def test_success_is_not_overwritten_by_duplicate_or_cancel(self):
        session = UploadSession()
        attempt = self.begin_attempt(session)
        self.assertIs(session.complete(attempt, "report.csv"), True)
        self.assert_snapshot(session, "done", "report.csv")
        self.assertIs(session.complete(attempt, "duplicate.csv"), False)
        self.assert_snapshot(session, "done", "report.csv")
        self.assertIs(session.cancel(), False)
        self.assert_snapshot(session, "done", "report.csv")
        self.assertIs(session.complete(attempt + 1, "foreign.csv"), False)
        self.assert_snapshot(session, "done", "report.csv")

    def test_cancel_prevents_late_completion_and_is_idempotent(self):
        session = UploadSession()
        attempt = self.begin_attempt(session)
        self.assertIs(session.cancel(), True)
        self.assert_snapshot(session, "cancelled", None)
        self.assertIs(session.complete(attempt, "late.csv"), False)
        self.assert_snapshot(session, "cancelled", None)
        self.assertIs(session.cancel(), False)
        self.assert_snapshot(session, "cancelled", None)

    def test_unknown_completion_preserves_current_attempt(self):
        session = UploadSession()
        attempt = self.begin_attempt(session)
        for unknown in (attempt - 1, attempt + 1):
            with self.subTest(unknown=unknown):
                self.assertIs(session.complete(unknown, "wrong.csv"), False)
                self.assert_snapshot(session, "waiting", None)
        self.assertIs(session.complete(attempt, "right.csv"), True)
        self.assert_snapshot(session, "done", "right.csv")

    def test_rejected_begin_preserves_current_attempt(self):
        session = UploadSession()
        attempt = self.begin_attempt(session)
        with self.assertRaises(RuntimeError):
            session.begin()
        self.assert_snapshot(session, "waiting", None)
        self.assertIs(session.complete(attempt, "original.csv"), True)
        self.assert_snapshot(session, "done", "original.csv")
        self.begin_attempt(session, previous=attempt)

    def test_restart_rejects_stale_results_before_and_after_current_result(self):
        for terminal in ("done", "cancelled"):
            with self.subTest(previous_terminal=terminal):
                session = UploadSession()
                old = self.begin_attempt(session)
                if terminal == "done":
                    self.assertIs(session.complete(old, "old.csv"), True)
                    self.assert_snapshot(session, "done", "old.csv")
                else:
                    self.assertIs(session.cancel(), True)
                    self.assert_snapshot(session, "cancelled", None)

                current = self.begin_attempt(session, previous=old)
                self.assertIs(session.complete(old, "stale-before.csv"), False)
                self.assert_snapshot(session, "waiting", None)
                self.assertIs(session.complete(current, "current.csv"), True)
                self.assert_snapshot(session, "done", "current.csv")
                self.assertIs(session.complete(old, "stale-after.csv"), False)
                self.assert_snapshot(session, "done", "current.csv")

    def test_three_attempts_keep_completed_and_cancelled_ids_obsolete(self):
        session = UploadSession()
        first = self.begin_attempt(session)
        self.assertIs(session.complete(first, "first.csv"), True)
        self.assert_snapshot(session, "done", "first.csv")
        second = self.begin_attempt(session, previous=first)
        self.assertIs(session.cancel(), True)
        self.assert_snapshot(session, "cancelled", None)
        third = self.begin_attempt(session, previous=second)
        for old in (first, second):
            with self.subTest(stale_attempt=old):
                self.assertIs(session.complete(old, "obsolete.csv"), False)
                self.assert_snapshot(session, "waiting", None)
        self.assertIs(session.complete(third, ""), True)
        self.assert_snapshot(session, "done", "")


if __name__ == "__main__":
    unittest.main()
