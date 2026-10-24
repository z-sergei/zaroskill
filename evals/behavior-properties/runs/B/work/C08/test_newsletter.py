import unittest
from newsletter import Newsletter

class Mailer:
    def __init__(self):
        self.messages = []
    def send(self, email, body):
        self.messages.append((email, body))

class NewsletterTests(unittest.TestCase):
    def test_disabled_subscription_sends_nothing(self):
        port = Mailer()
        app = Newsletter(port)
        self.assertEqual('disabled', app.subscribe('reader@example.test', False))
        self.assertEqual([], port.messages)

    def test_enabled_subscription_requests_welcome_mail(self):
        port = Mailer()
        app = Newsletter(port)
        self.assertEqual('subscribed', app.subscribe('reader@example.test', True))
        self.assertEqual([('reader@example.test', 'Welcome')], port.messages)
