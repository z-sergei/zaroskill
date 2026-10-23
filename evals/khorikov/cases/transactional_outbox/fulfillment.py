"""Local inventory reservations and an at-least-once confirmation outbox."""

import json
import sqlite3
from dataclasses import dataclass
from typing import Protocol


class InsufficientStock(Exception):
    pass


class IdempotencyConflict(Exception):
    pass


@dataclass(frozen=True)
class Order:
    order_id: int
    total_cents: int


class Notifications(Protocol):
    def send(self, *, recipient: str, payload: dict, idempotency_key: str) -> None:
        """Deliver externally; a raised exception leaves delivery unconfirmed."""


def initialize(database, catalog: dict[str, tuple[int, int]]) -> None:
    """Create an empty store; catalog values are (quantity, unit price in cents)."""
    with sqlite3.connect(database) as connection:
        connection.executescript("""
            CREATE TABLE stock (
                sku TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                unit_cents INTEGER NOT NULL CHECK(unit_cents >= 0)
            );
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_key TEXT NOT NULL UNIQUE,
                request_body TEXT NOT NULL,
                total_cents INTEGER NOT NULL
            );
            CREATE TABLE outbox (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL UNIQUE,
                recipient TEXT NOT NULL,
                payload TEXT NOT NULL,
                delivered INTEGER NOT NULL DEFAULT 0
            );
        """)
        connection.executemany(
            "INSERT INTO stock VALUES (?, ?, ?)",
            [(sku, quantity, price) for sku, (quantity, price) in catalog.items()],
        )


def stock_levels(database) -> dict[str, int]:
    """Read committed inventory using a new connection."""
    with sqlite3.connect(database) as connection:
        return dict(connection.execute("SELECT sku, quantity FROM stock"))


def find_order(database, request_key: str) -> Order | None:
    """Read a committed order using a new connection."""
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT order_id, total_cents FROM orders WHERE request_key = ?",
            (request_key,),
        ).fetchone()
    return Order(*row) if row else None


def place_order(database, request_key: str, recipient: str, items) -> Order:
    """Reserve stock, record the order, and enqueue its confirmation atomically."""
    if not request_key or not recipient:
        raise ValueError("request_key and recipient are required")
    quantities = {}
    for sku, quantity in items:
        if not sku or type(quantity) is not int or quantity <= 0:
            raise ValueError("items need a SKU and a positive integer quantity")
        quantities[sku] = quantities.get(sku, 0) + quantity
    if not quantities:
        raise ValueError("at least one item is required")
    normalized = sorted(quantities.items())
    request_body = json.dumps({"recipient": recipient, "items": normalized}, sort_keys=True)
    connection = sqlite3.connect(database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        existing = connection.execute(
            "SELECT order_id, total_cents, request_body FROM orders WHERE request_key = ?",
            (request_key,),
        ).fetchone()
        if existing:
            if existing[2] != request_body:
                raise IdempotencyConflict(request_key)
            return Order(existing[0], existing[1])
        total = 0
        for sku, quantity in normalized:
            available = connection.execute(
                "SELECT quantity, unit_cents FROM stock WHERE sku = ?", (sku,)
            ).fetchone()
            if available is None or available[0] < quantity:
                raise InsufficientStock(sku)
            connection.execute(
                "UPDATE stock SET quantity = quantity - ? WHERE sku = ?", (quantity, sku)
            )
            total += quantity * available[1]
        cursor = connection.execute(
            "INSERT INTO orders(request_key, request_body, total_cents) VALUES (?, ?, ?)",
            (request_key, request_body, total),
        )
        order = Order(cursor.lastrowid, total)
        payload = {
            "type": "order.confirmed",
            "order_id": order.order_id,
            "items": [{"sku": sku, "quantity": quantity} for sku, quantity in normalized],
            "total_cents": total,
        }
        connection.execute(
            "INSERT INTO outbox(order_id, recipient, payload) VALUES (?, ?, ?)",
            (order.order_id, recipient, json.dumps(payload)),
        )
        connection.commit()
        return order
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def dispatch_pending(database, notifications: Notifications) -> int:
    """Send pending events in creation order; stop and propagate a send failure."""
    with sqlite3.connect(database) as connection:
        pending = connection.execute(
            "SELECT event_id, recipient, payload, order_id FROM outbox "
            "WHERE delivered = 0 ORDER BY event_id"
        ).fetchall()
    delivered = 0
    for event_id, recipient, raw_payload, order_id in pending:
        notifications.send(
            recipient=recipient,
            payload=json.loads(raw_payload),
            idempotency_key=f"order-confirmation:{order_id}",
        )
        with sqlite3.connect(database) as connection:
            connection.execute("UPDATE outbox SET delivered = 1 WHERE event_id = ?", (event_id,))
        delivered += 1
    return delivered
