"""Search screen state with latest-started-request ownership."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Callable, Protocol, Sequence


class SearchGateway(Protocol):
    async def search(self, query: str) -> Sequence[str]:
        ...


@dataclass(frozen=True)
class SearchState:
    query: str = ""
    status: str = "idle"
    results: tuple[str, ...] = ()
    error: str | None = None


class SearchController:
    def __init__(
        self,
        gateway: SearchGateway,
        on_change: Callable[[SearchState], None] | None = None,
    ) -> None:
        self._gateway = gateway
        self._on_change = on_change
        self._state = SearchState()
        self._generation = 0

    @property
    def state(self) -> SearchState:
        return self._state

    def _publish(self, state: SearchState) -> None:
        self._state = state
        if self._on_change is not None:
            self._on_change(state)

    async def search(self, query: str) -> None:
        normalized = query.strip()
        self._generation += 1
        request = self._generation
        if not normalized:
            self._publish(SearchState())
            return

        self._publish(SearchState(query=normalized, status="loading"))
        try:
            matches = tuple(await self._gateway.search(normalized))
        except asyncio.CancelledError:
            if request == self._generation:
                self._publish(SearchState(query=normalized))
            raise
        except Exception as error:
            if request == self._generation:
                self._publish(
                    SearchState(
                        query=normalized,
                        status="failed",
                        error=str(error) or "Search failed",
                    )
                )
        else:
            if request == self._generation:
                self._publish(
                    SearchState(query=normalized, status="ready", results=matches)
                )
