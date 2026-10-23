# Print spooler contract tests

Write a maintainable automated test suite for `spooler.py`. The module is the
production implementation of a small deterministic print spooler. Your tests
should protect its observable behavior through the public API below.

Create only `tests/test_*.py` and `report.md`. Do not modify the production
module or other supplied files. Use Python 3.11+ and the standard library
`unittest` framework, with no third-party packages. The suite must run with:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

In `report.md`, briefly explain your coverage choices, important state and
boundary cases, and the command and outcome of your test run. Test the public
contract; do not depend on private attributes, internal method calls, a
particular scheduling algorithm, exception message text, or object identity.
The behavior below is authoritative.

## Public values and inputs

`from spooler import Job, Spooler` exposes the API. A `Job` is a value snapshot
with fields `job_id`, `pages`, `priority`, `printed`, and `status`. The first
three retain the submitted values. `printed` is the number of pages already
printed. Status is one of `queued`, `printing`, `paused`, `completed`, or
`cancelled`. A snapshot previously returned to a consumer keeps its field
values when the spooler later changes. Compare values rather than identity.

Callers use strings for IDs and integers (not booleans) for counts and
priorities. Handling other input types is outside this task.

## Creation, submission, and observation

* `Spooler(max_active=1)` creates an empty spooler. `max_active` must be positive;
  zero or negative values raise `ValueError`.
* `submit(job_id, pages, priority=0)` returns a new queued job with zero pages
  printed. IDs must be nonempty, page totals must be positive, and IDs must be
  unique for the entire lifetime of the spooler, including after completion or
  cancellation. A violation raises `ValueError`. Any integer priority is valid.
* `get(job_id)` returns that job's current snapshot.
* `jobs()` returns a tuple of current snapshots for every submitted job in
  original submission order. Completed and cancelled jobs remain observable.
* A method taking an unknown job ID raises `KeyError`.
* Every rejected operation leaves all existing jobs unchanged. A rejected
  submission does not create a job.

## Scheduling

`start_next()` starts at most one queued job and returns its snapshot with
status `printing`. It chooses the highest numeric priority first. Equal
priorities are resolved by original submission order, oldest first. Ordering
does not depend on ID spelling. Submission order remains the tie breaker when
a paused job is later resumed.

At most `max_active` jobs may be printing. `start_next()` returns `None` and
changes nothing when every printing slot is occupied, or when there is no
queued job. Paused jobs do not occupy a printing slot and are not eligible to
start until resumed. Completed and cancelled jobs are never eligible.
Submitting or resuming a job does not start it or interrupt another job;
selection only happens when `start_next()` is called.

## Progress and transitions

* `advance(job_id, pages)` is permitted only while the job is printing. The
  supplied positive page count is additional progress, accumulated across
  calls. It must not exceed the remaining pages. Invalid state or page count
  raises `ValueError`. Before all pages are printed the job stays printing;
  reaching its total exactly changes its status to completed and frees its
  printing slot immediately. The method returns the updated snapshot.
* `pause(job_id)` is permitted only while printing. It changes status to paused,
  preserves progress, frees the slot immediately, and returns the snapshot.
* `resume(job_id)` is permitted only while paused. It changes status to queued,
  preserves progress, priority, and original position for tie breaking, and
  returns the snapshot. Resuming is allowed even when all slots are occupied.
* `cancel(job_id)` is permitted while queued, printing, or paused. It changes
  status to cancelled, preserves progress, frees any occupied slot immediately,
  and returns the snapshot.
* A pause, resume, or cancel outside the listed source states raises
  `ValueError`. Completed and cancelled jobs are terminal: they cannot be
  restarted, progressed, paused, resumed, or cancelled again.

There are no clocks, background workers, automatic retries, or external print
devices. The API is used sequentially. Tests should demonstrate meaningful
consumer outcomes and state partitions without prescribing the implementation.
