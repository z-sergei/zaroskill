import unittest
from upload import Upload

class UploadTests(unittest.TestCase):
    def test_previous_upload_cannot_replace_current_document(self):
        states = 0
        for count in range(1, 21):
            app = Upload()
            for _ in range(count):
                active = app.begin()
            states += count
            if active != app.current:
                app.finish(active, 'older-document')
                self.assertIsNone(app.document)
        self.assertGreater(states, 100)
