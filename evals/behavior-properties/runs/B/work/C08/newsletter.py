class Newsletter:
    def __init__(self, mailer):
        self.mailer = mailer

    def subscribe(self, email, enabled):
        if enabled:
            self.mailer.send(email, 'Welcome')
        return 'subscribed' if enabled else 'disabled'
