"""A small bounded cache whose deadlines use an injected monotonic clock."""

from collections import OrderedDict
from copy import deepcopy
from math import isfinite


class TTLCache:
    """Store detached values with time-to-live deadlines and LRU eviction."""

    def __init__(self, capacity, clock):
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if not callable(clock):
            raise TypeError("clock must be callable")
        self._capacity = capacity
        self._clock = clock
        self._entries = OrderedDict()

    @staticmethod
    def _validate_key(key):
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a nonempty string")

    @staticmethod
    def _validate_ttl(ttl):
        if isinstance(ttl, bool) or not isinstance(ttl, (int, float)):
            raise ValueError("ttl must be a positive finite number")
        try:
            seconds = float(ttl)
        except OverflowError:
            raise ValueError("ttl must be a positive finite number") from None
        if not isfinite(seconds) or seconds <= 0:
            raise ValueError("ttl must be a positive finite number")
        return seconds

    def _prepare(self, entries):
        prepared = []
        for entry in entries:
            try:
                key, value, ttl = entry
            except (TypeError, ValueError):
                raise ValueError("each entry must contain key, value, ttl") from None
            self._validate_key(key)
            seconds = self._validate_ttl(ttl)
            prepared.append((key, deepcopy(value), seconds))
        return prepared

    def _purge(self, now):
        expired_keys = [
            key
            for key, (_, expires_at) in self._entries.items()
            if expires_at <= now
        ]
        for key in expired_keys:
            del self._entries[key]

    def put(self, key, value, ttl):
        """Insert or replace one value; see put_many for shared semantics."""
        self.put_many([(key, value, ttl)])

    def put_many(self, entries):
        """Validate and copy the complete batch before changing cache state."""
        prepared = self._prepare(entries)
        if not prepared:
            return
        now = self._clock()
        self._purge(now)
        for key, value, ttl in prepared:
            self._entries[key] = (value, now + ttl)
            self._purge(now)
            if key in self._entries:
                self._entries.move_to_end(key)
            while len(self._entries) > self._capacity:
                self._entries.popitem(last=False)

    def get(self, key, default=None):
        """Return a detached value and make a live hit most recently used."""
        self._validate_key(key)
        now = self._clock()
        self._purge(now)
        if key not in self._entries:
            return default
        value, _ = self._entries[key]
        self._entries.move_to_end(key)
        return deepcopy(value)

    def snapshot(self):
        """Return a detached dict in least-to-most-recently-used order."""
        now = self._clock()
        self._purge(now)
        return {key: deepcopy(value) for key, (value, _) in self._entries.items()}
