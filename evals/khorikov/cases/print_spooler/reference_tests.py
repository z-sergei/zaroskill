import unittest

from spooler import Job, Spooler


class SpoolerContractTests(unittest.TestCase):
    def assertJob(self, actual, job_id, pages, priority, printed, status):
        self.assertEqual(actual, Job(job_id, pages, priority, printed, status))

    def assertStarted(self, spooler, job_id):
        started = spooler.start_next()
        self.assertIsNotNone(started)
        self.assertEqual(started.job_id, job_id)
        return started

    def test_empty_spooler_has_no_work(self):
        spooler = Spooler()
        self.assertEqual(spooler.jobs(), ())
        self.assertIsNone(spooler.start_next())

    def test_submission_values_and_observation_order(self):
        spooler = Spooler()
        self.assertJob(spooler.submit("zebra", 8), "zebra", 8, 0, 0, "queued")
        self.assertJob(spooler.submit("alpha", 3, -4), "alpha", 3, -4, 0, "queued")
        self.assertEqual(spooler.jobs(), (spooler.get("zebra"), spooler.get("alpha")))

    def test_priority_takes_precedence_over_arrival(self):
        spooler = Spooler(3)
        for job_id, priority in [("ordinary", 0), ("urgent", 12), ("low", -7)]:
            spooler.submit(job_id, 4, priority)
        observed = [spooler.start_next().job_id for _ in range(3)]
        self.assertEqual(observed, ["urgent", "ordinary", "low"])

    def test_equal_priority_uses_arrival_not_identifier(self):
        spooler = Spooler(3)
        for job_id in ["z-last-alphabetically", "a-first-alphabetically", "m-middle"]:
            spooler.submit(job_id, 4, 2)
        observed = [spooler.start_next().job_id for _ in range(3)]
        self.assertEqual(observed, ["z-last-alphabetically", "a-first-alphabetically", "m-middle"])

    def test_multiple_slots_and_full_capacity_are_observable(self):
        spooler = Spooler(2)
        for job_id in ["first", "second", "third"]:
            spooler.submit(job_id, 4)
        self.assertEqual(spooler.start_next().status, "printing")
        self.assertEqual(spooler.start_next().status, "printing")
        before = spooler.jobs()
        self.assertIsNone(spooler.start_next())
        self.assertEqual(spooler.jobs(), before)
        self.assertEqual(spooler.get("third").status, "queued")

    def test_submitting_higher_priority_does_not_preempt(self):
        spooler = Spooler()
        spooler.submit("running", 4)
        spooler.start_next()
        spooler.submit("urgent", 2, 99)
        self.assertEqual(spooler.get("running").status, "printing")
        self.assertEqual(spooler.get("urgent").status, "queued")
        self.assertIsNone(spooler.start_next())

    def test_progress_accumulates_before_completion(self):
        spooler = Spooler()
        spooler.submit("report", 10)
        spooler.start_next()
        self.assertJob(spooler.advance("report", 2), "report", 10, 0, 2, "printing")
        self.assertJob(spooler.advance("report", 3), "report", 10, 0, 5, "printing")
        self.assertEqual(spooler.get("report").printed, 5)

    def test_exact_completion_releases_capacity(self):
        spooler = Spooler()
        spooler.submit("one-page", 1)
        spooler.submit("next", 5)
        self.assertStarted(spooler, "one-page")
        self.assertJob(spooler.advance("one-page", 1), "one-page", 1, 0, 1, "completed")
        self.assertEqual(spooler.start_next().job_id, "next")
        self.assertEqual([job.job_id for job in spooler.jobs()], ["one-page", "next"])

    def test_partial_progress_then_final_page_completes(self):
        spooler = Spooler()
        spooler.submit("report", 6)
        spooler.start_next()
        spooler.advance("report", 5)
        self.assertJob(spooler.advance("report", 1), "report", 6, 0, 6, "completed")
        self.assertIsNone(spooler.start_next())

    def test_pause_releases_slot_without_making_paused_job_eligible(self):
        spooler = Spooler()
        spooler.submit("paused-urgent", 8, 10)
        spooler.submit("waiting", 3)
        self.assertStarted(spooler, "paused-urgent")
        spooler.advance("paused-urgent", 2)
        self.assertJob(spooler.pause("paused-urgent"), "paused-urgent", 8, 10, 2, "paused")
        started = spooler.start_next()
        self.assertIsNotNone(started)
        self.assertEqual(started.job_id, "waiting")
        self.assertEqual(spooler.get("paused-urgent").status, "paused")

    def test_only_paused_work_is_not_automatically_started(self):
        spooler = Spooler()
        spooler.submit("held", 5)
        spooler.start_next()
        spooler.pause("held")
        before = spooler.jobs()
        self.assertIsNone(spooler.start_next())
        self.assertEqual(spooler.jobs(), before)

    def test_resumed_job_keeps_original_tie_break_position(self):
        spooler = Spooler()
        spooler.submit("older", 10, 4)
        spooler.start_next()
        spooler.advance("older", 3)
        spooler.submit("newer", 3, 4)
        spooler.pause("older")
        self.assertJob(spooler.resume("older"), "older", 10, 4, 3, "queued")
        self.assertEqual(spooler.start_next().job_id, "older")
        self.assertEqual(spooler.get("older").printed, 3)
        self.assertEqual([job.job_id for job in spooler.jobs()], ["older", "newer"])

    def test_resume_is_allowed_at_capacity_and_preserves_priority(self):
        spooler = Spooler()
        spooler.submit("important", 10, 9)
        spooler.start_next()
        spooler.advance("important", 4)
        spooler.pause("important")
        spooler.submit("running", 2)
        self.assertStarted(spooler, "running")
        self.assertJob(spooler.resume("important"), "important", 10, 9, 4, "queued")
        self.assertIsNone(spooler.start_next())
        spooler.advance("running", 2)
        spooler.submit("less-important", 1, 3)
        self.assertStarted(spooler, "important")
        self.assertJob(spooler.advance("important", 6), "important", 10, 9, 10, "completed")

    def test_cancellation_from_each_live_state_preserves_progress(self):
        for state, printed in [("queued", 0), ("printing", 2), ("paused", 2)]:
            with self.subTest(state=state):
                spooler = Spooler()
                spooler.submit("target", 6, 3)
                if state != "queued":
                    spooler.start_next()
                    spooler.advance("target", 2)
                if state == "paused":
                    spooler.pause("target")
                self.assertJob(spooler.cancel("target"), "target", 6, 3, printed, "cancelled")
                spooler.submit("other", 2)
                self.assertEqual(spooler.start_next().job_id, "other")

    def test_returned_snapshots_retain_values_after_later_operations(self):
        spooler = Spooler()
        submitted = spooler.submit("report", 5, 2)
        started = spooler.start_next()
        partial = spooler.advance("report", 2)
        observed = spooler.jobs()
        spooler.cancel("report")
        self.assertJob(submitted, "report", 5, 2, 0, "queued")
        self.assertJob(started, "report", 5, 2, 0, "printing")
        self.assertJob(partial, "report", 5, 2, 2, "printing")
        self.assertEqual(observed, (partial,))
        self.assertEqual(spooler.get("report").status, "cancelled")

    def test_invalid_capacity_is_rejected(self):
        for capacity in [0, -2]:
            with self.subTest(capacity=capacity), self.assertRaises(ValueError):
                Spooler(capacity)

    def test_invalid_submissions_leave_existing_jobs_unchanged(self):
        spooler = Spooler()
        spooler.submit("existing", 4)
        before = spooler.jobs()
        for job_id, pages in [("", 5), ("zero", 0), ("negative", -2), ("existing", 3)]:
            with self.subTest(job_id=job_id, pages=pages):
                with self.assertRaises(ValueError):
                    spooler.submit(job_id, pages)
                self.assertEqual(spooler.jobs(), before)

    def test_terminal_job_identifiers_cannot_be_reused(self):
        for terminal in ["completed", "cancelled"]:
            with self.subTest(terminal=terminal):
                spooler = Spooler()
                spooler.submit("permanent-id", 2)
                if terminal == "completed":
                    spooler.start_next()
                    spooler.advance("permanent-id", 2)
                else:
                    spooler.cancel("permanent-id")
                before = spooler.jobs()
                with self.assertRaises(ValueError):
                    spooler.submit("permanent-id", 6)
                self.assertEqual(spooler.jobs(), before)

    def test_invalid_progress_is_atomic_and_does_not_consume_capacity(self):
        spooler = Spooler()
        spooler.submit("report", 5)
        spooler.submit("waiting", 2)
        self.assertStarted(spooler, "report")
        spooler.advance("report", 2)
        before = spooler.jobs()
        for increment in [0, -1, 4]:
            with self.subTest(increment=increment):
                with self.assertRaises(ValueError):
                    spooler.advance("report", increment)
                self.assertEqual(spooler.jobs(), before)
                self.assertIsNone(spooler.start_next())

    def test_invalid_state_transitions_are_atomic(self):
        invalid = {
            "queued": ["advance", "pause", "resume"],
            "printing": ["resume"],
            "paused": ["advance", "pause"],
            "completed": ["advance", "pause", "resume", "cancel"],
            "cancelled": ["advance", "pause", "resume", "cancel"],
        }
        for state, operations in invalid.items():
            spooler = Spooler()
            spooler.submit("target", 2)
            if state in {"printing", "paused", "completed"}:
                spooler.start_next()
            if state == "paused":
                spooler.pause("target")
            elif state == "completed":
                spooler.advance("target", 2)
            elif state == "cancelled":
                spooler.cancel("target")
            before = spooler.jobs()
            for operation in operations:
                with self.subTest(state=state, operation=operation):
                    with self.assertRaises(ValueError):
                        getattr(spooler, operation)("target", 1) if operation == "advance" else getattr(spooler, operation)("target")
                    self.assertEqual(spooler.jobs(), before)

    def test_unknown_identifiers_are_rejected_without_changes(self):
        spooler = Spooler()
        spooler.submit("existing", 4)
        before = spooler.jobs()
        for operation in ["get", "advance", "pause", "resume", "cancel"]:
            with self.subTest(operation=operation):
                with self.assertRaises(KeyError):
                    getattr(spooler, operation)("missing", 1) if operation == "advance" else getattr(spooler, operation)("missing")
                self.assertEqual(spooler.jobs(), before)


if __name__ == "__main__":
    unittest.main()
