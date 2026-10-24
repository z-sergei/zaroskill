class Upload:
    def __init__(self):
        self.current = 0
        self.document = None

    def begin(self):
        self.current += 1
        return self.current

    def finish(self, token, document):
        if token == self.current:
            self.document = document
