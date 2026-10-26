class UploadSession:
    def __init__(self):
        self.state = "idle"
        self.result = None
        self._last_attempt = 0
        self._active_attempt = None

    def begin(self):
        if self.state == "waiting":
            self._active_attempt = None
            raise RuntimeError("already waiting")
        self._last_attempt += 1
        self._active_attempt = self._last_attempt
        self.state = "waiting"
        self.result = None
        return self._active_attempt

    def complete(self, attempt_id, value):
        if self.state != "waiting" or attempt_id != self._active_attempt:
            return False
        self.state = "done"
        self.result = value
        self._active_attempt = None
        return True

    def cancel(self):
        if self.state != "waiting":
            return False
        self.state = "cancelled"
        self.result = None
        self._active_attempt = None
        return True
