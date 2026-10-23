"""Deterministic page-oriented print spooler."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    job_id: str
    pages: int
    priority: int
    printed: int
    status: str


@dataclass
class _Record:
    job_id: str
    pages: int
    priority: int
    order: int
    printed: int = 0
    status: str = "queued"


class Spooler:
    def __init__(self, max_active: int = 1):
        if max_active <= 0:
            raise ValueError("max_active must be positive")
        self._max_active = max_active
        self._records = {}
        self._next_order = 0

    @staticmethod
    def _view(record):
        return Job(record.job_id, record.pages, record.priority,
                   record.printed, record.status)

    def submit(self, job_id: str, pages: int, priority: int = 0) -> Job:
        if not job_id or job_id in self._records or pages <= 0:
            raise ValueError("invalid submission")
        record = _Record(job_id, pages, priority, self._next_order)
        self._next_order += 1
        self._records[job_id] = record
        return self._view(record)

    def get(self, job_id: str) -> Job:
        return self._view(self._records[job_id])

    def jobs(self) -> tuple[Job, ...]:
        return tuple(self._view(record) for record in self._records.values())

    def start_next(self) -> Job | None:
        active = sum(record.status == "printing" for record in self._records.values())
        if active >= self._max_active:
            return None
        queued = [record for record in self._records.values() if record.status == "queued"]
        if not queued:
            return None
        record = min(queued, key=lambda item: (-item.priority, item.order))
        record.status = "printing"
        return self._view(record)

    def advance(self, job_id: str, pages: int) -> Job:
        record = self._records[job_id]
        if record.status != "printing" or pages <= 0 or pages > record.pages - record.printed:
            raise ValueError("invalid progress")
        record.printed += pages
        if record.printed == record.pages:
            record.status = "completed"
        return self._view(record)

    def pause(self, job_id: str) -> Job:
        record = self._records[job_id]
        if record.status != "printing":
            raise ValueError("only a printing job can be paused")
        record.status = "paused"
        return self._view(record)

    def resume(self, job_id: str) -> Job:
        record = self._records[job_id]
        if record.status != "paused":
            raise ValueError("only a paused job can be resumed")
        record.status = "queued"
        return self._view(record)

    def cancel(self, job_id: str) -> Job:
        record = self._records[job_id]
        if record.status not in {"queued", "printing", "paused"}:
            raise ValueError("terminal jobs cannot be cancelled")
        record.status = "cancelled"
        return self._view(record)
