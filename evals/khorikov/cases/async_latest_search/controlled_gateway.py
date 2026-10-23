"""A deterministic test adapter: the test supplies every gateway response."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class PendingSearch:
    query: str
    _response: asyncio.Future[Sequence[str]]
    cancellation_observed: asyncio.Event

    def succeed(self, results: Sequence[str]) -> None:
        self._response.set_result(results)

    def fail(self, error: Exception) -> None:
        self._response.set_exception(error)


class ControlledGateway:
    """Use next_request() as the barrier proving a search has reached the gateway.

    ignore_cancellation models a transport that cannot abandon submitted work.
    Request handles remain completable after cancellation in that mode.
    """

    def __init__(self, *, ignore_cancellation: bool = False) -> None:
        self._ignore_cancellation = ignore_cancellation
        self._requests: asyncio.Queue[PendingSearch] = asyncio.Queue()

    async def next_request(self) -> PendingSearch:
        return await self._requests.get()

    async def search(self, query: str) -> Sequence[str]:
        response = asyncio.get_running_loop().create_future()
        request = PendingSearch(query, response, asyncio.Event())
        self._requests.put_nowait(request)
        while True:
            try:
                return await asyncio.shield(response)
            except asyncio.CancelledError:
                request.cancellation_observed.set()
                if not self._ignore_cancellation:
                    raise
