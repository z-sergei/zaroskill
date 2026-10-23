"""Evaluator-only contract tests and isolated fixture validation.

Run `python reference_tests.py --validate-variants` to verify the baseline,
every individual fault, and every behavior-preserving transformation.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from controlled_gateway import ControlledGateway
from search_controller import SearchController, SearchState


class ReferenceSearchTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.tasks = []

    async def asyncTearDown(self) -> None:
        for task in self.tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)

    async def begin(self, controller, gateway, query):
        task = asyncio.create_task(controller.search(query))
        self.tasks.append(task)
        request = await gateway.next_request()
        return task, request

    async def test_pending_and_ready_values_are_published_to_the_view(self):
        gateway = ControlledGateway()
        notifications = []
        controller = None

        def observe(value):
            visible = controller.state if controller is not None else None
            notifications.append((value, visible))

        controller = SearchController(gateway, observe)
        self.assertEqual(SearchState("", "idle", (), None), controller.state)
        task, request = await self.begin(controller, gateway, "  tea  ")
        pending = controller.state
        response = ["Oolong", "Assam", "Oolong"]
        request.succeed(response)
        await task
        response.append("Added later")

        self.assertEqual(SearchState("tea", "loading", (), None), pending)
        expected = SearchState("tea", "ready", ("Oolong", "Assam", "Oolong"), None)
        self.assertEqual(expected, controller.state)
        self.assertIn((expected, expected), notifications)
        self.assertTrue(all(sent == visible for sent, visible in notifications if visible is not None))

    async def test_empty_results_are_a_success(self):
        gateway = ControlledGateway()
        controller = SearchController(gateway)
        task, request = await self.begin(controller, gateway, "unknown")
        request.succeed([])
        await task
        self.assertEqual(SearchState("unknown", "ready", (), None), controller.state)

    async def test_failure_and_retry_clear_error_while_waiting(self):
        gateway = ControlledGateway()
        controller = SearchController(gateway)
        failed_task, failed_request = await self.begin(controller, gateway, "tea")
        failed_request.fail(RuntimeError("Connection lost"))
        await failed_task
        failure = controller.state
        retry_task, retry_request = await self.begin(controller, gateway, "tea")
        retry_pending = controller.state
        retry_request.succeed(["Assam"])
        await retry_task

        self.assertEqual(SearchState("tea", "failed", (), "Connection lost"), failure)
        self.assertEqual(SearchState("tea", "loading", (), None), retry_pending)
        self.assertEqual(SearchState("tea", "ready", ("Assam",), None), controller.state)

    async def test_exception_without_text_has_a_visible_fallback(self):
        gateway = ControlledGateway()
        controller = SearchController(gateway)
        task, request = await self.begin(controller, gateway, "tea")
        request.fail(RuntimeError())
        await task
        self.assertEqual(SearchState("tea", "failed", (), "Search failed"), controller.state)

    async def test_repeated_query_keeps_newer_results_after_old_success(self):
        gateway = ControlledGateway()
        notifications = []
        controller = SearchController(gateway, notifications.append)
        old_task, old_request = await self.begin(controller, gateway, "tea")
        new_task, new_request = await self.begin(controller, gateway, "  tea ")
        new_request.succeed(["Fresh inventory"])
        await new_task
        before = list(notifications)
        old_request.succeed(["Outdated inventory"])
        await old_task

        self.assertEqual(SearchState("tea", "ready", ("Fresh inventory",), None), controller.state)
        self.assertEqual(before, notifications)

    async def test_exactly_identical_raw_queries_have_distinct_ownership(self):
        gateway = ControlledGateway()
        notifications = []
        controller = SearchController(gateway, notifications.append)
        old_task, old_request = await self.begin(controller, gateway, "tea")
        new_task, new_request = await self.begin(controller, gateway, "tea")
        new_request.succeed(["Fresh inventory"])
        await new_task
        before = list(notifications)
        old_request.succeed(["Outdated inventory"])
        await old_task

        self.assertEqual(SearchState("tea", "ready", ("Fresh inventory",), None), controller.state)
        self.assertEqual(before, notifications)

    async def test_old_success_leaves_newer_failure_and_view_unchanged(self):
        gateway = ControlledGateway()
        notifications = []
        controller = SearchController(gateway, notifications.append)
        old_task, old_request = await self.begin(controller, gateway, "tea")
        new_task, new_request = await self.begin(controller, gateway, "coffee")
        new_request.fail(RuntimeError("Current connection failed"))
        await new_task
        expected = SearchState("coffee", "failed", (), "Current connection failed")
        self.assertEqual(expected, controller.state)
        before = list(notifications)
        old_request.succeed(["Outdated inventory"])
        await old_task

        self.assertEqual(expected, controller.state)
        self.assertEqual(before, notifications)

    async def test_old_success_leaves_newer_request_loading(self):
        gateway = ControlledGateway()
        notifications = []
        controller = SearchController(gateway, notifications.append)
        old_task, old_request = await self.begin(controller, gateway, "tea")
        new_task, new_request = await self.begin(controller, gateway, "coffee")
        before = list(notifications)
        old_request.succeed(["Assam"])
        await old_task
        pending = controller.state
        after = list(notifications)
        new_request.succeed(["Arabica"])
        await new_task

        self.assertEqual(SearchState("coffee", "loading", (), None), pending)
        self.assertEqual(before, after)
        self.assertEqual(SearchState("coffee", "ready", ("Arabica",), None), controller.state)

    async def test_old_failure_leaves_newer_success_and_view_unchanged(self):
        gateway = ControlledGateway()
        notifications = []
        controller = SearchController(gateway, notifications.append)
        old_task, old_request = await self.begin(controller, gateway, "tea")
        new_task, new_request = await self.begin(controller, gateway, "coffee")
        new_request.succeed(["Arabica"])
        await new_task
        before = list(notifications)
        old_request.fail(RuntimeError("Old connection failed"))
        await old_task

        self.assertEqual(SearchState("coffee", "ready", ("Arabica",), None), controller.state)
        self.assertEqual(before, notifications)

    async def test_current_cancellation_propagates_and_next_search_recovers(self):
        gateway = ControlledGateway()
        controller = SearchController(gateway)
        task, _ = await self.begin(controller, gateway, "  tea ")
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        cancelled = controller.state
        retry_task, retry_request = await self.begin(controller, gateway, "coffee")
        retry_request.succeed(["Arabica"])
        await retry_task

        self.assertEqual(SearchState("tea", "idle", (), None), cancelled)
        self.assertEqual(SearchState("coffee", "ready", ("Arabica",), None), controller.state)

    async def test_old_cancellation_leaves_newer_pending_view_unchanged(self):
        gateway = ControlledGateway()
        notifications = []
        controller = SearchController(gateway, notifications.append)
        old_task, _ = await self.begin(controller, gateway, "tea")
        new_task, new_request = await self.begin(controller, gateway, "coffee")
        before = list(notifications)
        old_task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await old_task
        pending = controller.state
        after = list(notifications)
        new_request.succeed(["Arabica"])
        await new_task

        self.assertEqual(SearchState("coffee", "loading", (), None), pending)
        self.assertEqual(before, after)
        self.assertEqual(SearchState("coffee", "ready", ("Arabica",), None), controller.state)

    async def test_blank_queries_do_not_invoke_the_gateway(self):
        # The public contract forbids consultation itself, even if a returned
        # coroutine is never awaited. Observe this public boundary directly.
        gateway = SimpleNamespace(search=AsyncMock(return_value=()))
        notifications = []
        controller = SearchController(gateway, notifications.append)
        for query in ("", " \t\n "):
            with self.subTest(query=query):
                await controller.search(query)
                self.assertEqual(SearchState("", "idle", (), None), controller.state)
                self.assertEqual(controller.state, notifications[-1])
                gateway.search.assert_not_called()

    async def test_blank_clear_prevents_pending_results_from_returning(self):
        gateway = ControlledGateway()
        notifications = []
        controller = SearchController(gateway, notifications.append)
        task, request = await self.begin(controller, gateway, "tea")
        await controller.search(" \t\n ")
        cleared = controller.state
        before = list(notifications)
        request.succeed(["Assam"])
        await task

        self.assertEqual(SearchState("", "idle", (), None), cleared)
        self.assertEqual(SearchState("", "idle", (), None), controller.state)
        self.assertEqual(before, notifications)

    async def test_ignored_cancellation_does_not_authorize_old_results(self):
        gateway = ControlledGateway(ignore_cancellation=True)
        notifications = []
        controller = SearchController(gateway, notifications.append)
        old_task, old_request = await self.begin(controller, gateway, "tea")
        new_task, new_request = await self.begin(controller, gateway, "tea")
        old_task.cancel()
        await old_request.cancellation_observed.wait()
        new_request.succeed(["Fresh inventory"])
        await new_task
        before = list(notifications)
        old_request.succeed(["Outdated inventory"])
        await old_task

        self.assertEqual(SearchState("tea", "ready", ("Fresh inventory",), None), controller.state)
        self.assertEqual(before, notifications)


def validate_variants() -> int:
    root = Path(__file__).resolve().parent
    grading = json.loads((root / "grader.json").read_text())
    variants = [("baseline", None, True)]
    variants += [(entry["id"], entry, False) for entry in grading["mutants"]]
    variants += [(entry["id"], entry, True) for entry in grading["refactors"]]
    correct = True
    for label, patch, should_pass in variants:
        with tempfile.TemporaryDirectory(prefix="async-search-reference-") as directory:
            target = Path(directory)
            for name in ("search_controller.py", "controlled_gateway.py", "reference_tests.py"):
                shutil.copy2(root / name, target / name)
            if patch is not None:
                source = target / patch["source"]
                text = source.read_text()
                if text.count(patch["before"]) != 1:
                    raise ValueError(f"Replacement is not unique: {label}")
                source.write_text(text.replace(patch["before"], patch["after"], 1))
            for source in target.glob("*.py"):
                compile(source.read_text(), str(source), "exec")
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "-q", "reference_tests"],
                cwd=target,
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            passed = result.returncode == 0
            assertion_failure = "FAIL: test_" in result.stderr and "ERROR:" not in result.stderr
            expectation_met = passed if should_pass else assertion_failure
            correct &= expectation_met
            outcome = "PASS" if passed else "FAIL"
            expected = "PASS" if should_pass else "FAIL"
            print(f"{label}: {outcome} (expected {expected})")
            if not expectation_met:
                print(result.stdout + result.stderr)
    return 0 if correct else 1


if __name__ == "__main__":
    if "--validate-variants" in sys.argv:
        raise SystemExit(validate_variants())
    unittest.main()
