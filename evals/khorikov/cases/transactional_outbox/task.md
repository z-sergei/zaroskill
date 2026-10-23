# Test inventory reservation and notification delivery

Add useful automated tests for `fulfillment.py`. Production behavior is correct. Keep production files unchanged and place runnable standard-library `unittest` tests in `tests/test_*.py`. Use Python 3.10 or later and temporary local data; no network, credentials, package installation, or live services are needed.

This application owns its SQLite database. The notification provider is external and is passed through the `Notifications.send` interface. A store is initialized once with a catalog mapping each SKU to `(available_quantity, unit_price_in_cents)`. The public API includes `initialize`, `place_order`, `stock_levels`, `find_order`, and `dispatch_pending`; exception classes and `Order` are also public. Database tables, SQL statements, connection calls, and JSON serialization are implementation details.

The business contract is:

- `place_order` validates a nonempty request key, recipient, and item list. Each item has a nonempty SKU and a positive integer quantity. Duplicate SKUs are combined, and the order of input items has no business significance.
- A successful order reduces each item's stock by its combined quantity, calculates the total using integer cents, and durably records one order and one confirmation event. The returned `Order` contains its ID and total. These changes are visible immediately through a new connection, including `stock_levels` and `find_order`.
- Unknown SKUs or insufficient inventory raise `InsufficientStock`. Every reservation made earlier in the same attempt is rolled back, and no order or confirmation remains. Retrying a failed request with valid quantities can succeed.
- Reusing a request key with the same recipient and normalized quantities returns the original `Order` without further stock changes or another event, including after its confirmation has been delivered. Reusing it with a different recipient or normalized quantities raises `IdempotencyConflict` and leaves the original order intact.
- Placing an order only queues a confirmation. `dispatch_pending` sends pending confirmations in creation order and returns the number successfully delivered in that call. A confirmed send is recorded durably and skipped on later calls. Already delivered confirmations stay delivered if a later one fails.
- A send uses the order's recipient, idempotency key `order-confirmation:<order_id>`, and a dictionary payload with exactly `type: "order.confirmed"`, `order_id`, `total_cents`, and `items`. Items are sorted by SKU and each contains `sku` and the combined `quantity`.
- If `send` raises, dispatch stops, propagates that exception, and leaves that event pending for another call. A retry uses the same recipient, payload, and idempotency key. An external provider may accept a send before raising, or the process may stop after sending but before recording success. This design allows repeated attempts and relies on the provider's deduplication key where available; it does not promise exactly-once external delivery. Concurrent dispatchers and process-crash simulation are outside this task.

Run `python -m unittest discover -s tests -p 'test_*.py'` from the case directory. Finish with a concise explanation of the behaviors covered, how dependencies were handled, and the test result.
