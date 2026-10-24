class SearchApp:
    def __init__(self, gateway):
        self.gateway = gateway
        self._active = 0
        self.visible = ()

    def search(self, query):
        self._active += 1
        token = self._active
        self.gateway.start(token, query)
        return token

    def receive(self, token, items):
        if token == self._active:
            self.visible = tuple(items)
