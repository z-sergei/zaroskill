class UploadSession:
    def __init__(self):
        self.state, self.result = "idle", None
        self._next = 1
        self._pending = None

    def begin(self):
        if self.state == "waiting":
            raise RuntimeError("attempt in progress")
        token = self._next
        self._next += 1
        self._pending = token
        self.state, self.result = "waiting", None
        return token

    def complete(self, attempt_id, value):
        if self.state == "waiting" and self._pending == attempt_id:
            self._pending = None
            self.state, self.result = "done", value
            return True
        return False

    def cancel(self):
        if self.state == "waiting":
            self._pending = None
            self.state, self.result = "cancelled", None
            return True
        return False
