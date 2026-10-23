"""Import UTF-8 delivery manifests into an in-memory inventory."""

from __future__ import annotations

import codecs
import csv
from dataclasses import dataclass
from typing import BinaryIO, Iterable, Iterator, Mapping


class InvalidManifest(ValueError):
    """The input is not a valid delivery manifest."""


@dataclass(frozen=True)
class DeliveryLine:
    sku: str
    quantity: int
    note: str


@dataclass(frozen=True)
class ImportSummary:
    line_count: int
    total_units: int
    skus: tuple[str, ...]


class Inventory:
    def __init__(self, initial_stock: Mapping[str, int] | None = None):
        self._quantities = dict(initial_stock or {})
        self._received_lines: tuple[DeliveryLine, ...] = ()

    @property
    def quantities(self) -> dict[str, int]:
        return dict(self._quantities)

    @property
    def received_lines(self) -> tuple[DeliveryLine, ...]:
        return self._received_lines

    def _commit(self, entries: Iterable[DeliveryLine]) -> None:
        entries = tuple(entries)
        updated = dict(self._quantities)
        for entry in entries:
            updated[entry.sku] = updated.get(entry.sku, 0) + entry.quantity
        self._quantities = updated
        self._received_lines += entries


def _decoded_lines(stream: BinaryIO, chunk_size: int) -> Iterator[str]:
    decoder = codecs.getincrementaldecoder("utf-8-sig")(errors="strict")
    pending = ""
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            pending += decoder.decode(b"", final=True)
            if pending:
                yield pending
            return
        pending += decoder.decode(chunk, final=False)
        while "\n" in pending:
            boundary = pending.index("\n") + 1
            yield pending[:boundary]
            pending = pending[boundary:]


def _read_entries(stream: BinaryIO, chunk_size: int) -> Iterator[DeliveryLine]:
    try:
        reader = (row for row in csv.reader(_decoded_lines(stream, chunk_size), strict=True) if row)
        if next(reader, None) != ["sku", "quantity", "note"]:
            raise InvalidManifest("Expected sku,quantity,note header")
        for row in reader:
            if len(row) != 3:
                raise InvalidManifest("Every record must have three fields")
            sku, quantity_text, note = row
            sku = sku.strip()
            quantity_text = quantity_text.strip()
            if not sku:
                raise InvalidManifest("SKU must not be blank")
            if not quantity_text or any(c not in "0123456789" for c in quantity_text):
                raise InvalidManifest("Quantity must contain ASCII digits")
            try:
                quantity = int(quantity_text.lstrip("0") or "0")
            except ValueError as exc:
                raise InvalidManifest("Quantity is too large") from exc
            if not 1 <= quantity <= 1_000_000:
                raise InvalidManifest("Quantity must be between 1 and 1000000")
            yield DeliveryLine(sku, quantity, note)
    except (UnicodeError, csv.Error) as exc:
        raise InvalidManifest("Invalid UTF-8 or CSV") from exc


def import_manifest(
    stream: BinaryIO, inventory: Inventory, *, chunk_size: int = 4096
) -> ImportSummary:
    """Validate the complete stream, then add all deliveries atomically."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    pending = list(_read_entries(stream, chunk_size))
    inventory._commit(pending)
    first_seen: list[str] = []
    for entry in pending:
        if entry.sku not in first_seen:
            first_seen.append(entry.sku)
    return ImportSummary(
        line_count=len(pending),
        total_units=sum(entry.quantity for entry in pending),
        skus=tuple(first_seen),
    )
