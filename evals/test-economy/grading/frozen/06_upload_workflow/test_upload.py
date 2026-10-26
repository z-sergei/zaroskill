import unittest
from upload import UploadSession


class UploadTests(unittest.TestCase):
    def test_successful_upload(self):
        session = UploadSession()
        self.assertEqual((session.state, session.result), ("idle", None))
        attempt = session.begin()
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
