# Test the asynchronous search screen

Add deterministic regression tests for `SearchController` using Python's standard-library `unittest`. Keep the supplied application and gateway adapter unchanged. Put your tests in `tests/test_*.py`; they must run from this directory with `python -m unittest discover -s tests -v` and require no services or third-party packages.

The controller drives a search screen through its public `state` property and optional `on_change` callback. A gateway is an asynchronous collaborator, supplied through the constructor. Test the real controller and control gateway responses at this boundary.

## Screen contract

- A new controller has `SearchState()` as its state. Every published state is an immutable value, and the callback, when supplied, receives that value after `state` has been updated. Callbacks are synchronous and do not raise or start new searches.
- `search(query)` trims surrounding whitespace. Once the coroutine starts, a nonempty query publishes `loading` with the normalized query, empty results, and no error. It then waits for its gateway response. Tests may inspect this state while the response is pending.
- A successful current search publishes `ready`, preserving the gateway's result order and duplicates in an immutable tuple. Empty results are a successful search. A failed current search publishes `failed` with empty results and the exception's string as its error, or `Search failed` when that string is empty. Ordinary gateway exceptions are represented in state and do not escape `search`.
- The most recently started search owns the screen. An earlier request may finish before or after it; an earlier success or failure must neither replace current state nor notify the view. Each invocation is a distinct request, including successive invocations with the same query. Starting another search does not automatically cancel earlier work.
- A blank normalized query immediately clears the screen to `SearchState()`, superseding pending work without consulting the gateway. Later completion of that pending work cannot restore the old screen.
- Cancellation is cooperative. When the gateway propagates `asyncio.CancelledError`, `search` propagates it to its caller. If that request still owns the screen, cancellation publishes `idle` with its normalized query, empty results, and no error. Cancellation of an older request leaves the current screen and callback untouched. A gateway may instead consume cancellation and eventually return normally; its result follows the usual request ownership rule. A later search remains usable after a failure or cancellation.

## Deterministic coordination

`controlled_gateway.py` supplies a response-controlled gateway. Start the real search in an `asyncio` task, then await `gateway.next_request()` to obtain the request it issued. This is an explicit barrier: the request is now waiting for its response. Call the handle's `succeed(results)` or `fail(exception)`, then await the search task before asserting its completed outcome. You choose the completion order of overlapping requests.

The adapter normally propagates cancellation. With `ControlledGateway(ignore_cancellation=True)`, it records cancellation and continues waiting for a response. After cancelling the search task, await `request.cancellation_observed.wait()` to know the adapter has consumed cancellation; then complete the request. Complete or cancel all tasks that you create.

Use response handles, futures, queues, or events to coordinate work. Avoid sleeps, elapsed-time assertions, polling, private controller attributes, source inspection, and assertions about private helper calls or the gateway's internal call sequence. Use controller state and view notifications as evidence. Choose tests that protect distinct observable behavior rather than recreating the implementation or adding a separate search algorithm to a test double.

Finish by running the suite and briefly report the behavior covered and the result.
