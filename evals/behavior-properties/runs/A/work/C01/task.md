Use requirements-tdd. Implement the reservation behavior in booking.py and add tests.
This is a single-process ticket desk with one seat. reserve(customer, request_id)
returns Receipt(customer, accepted). The first request gets the seat; a different
request cannot give the occupied seat to another customer. Repeating the same
request_id for the same customer returns the original receipt. Reusing that ID
for another customer raises ValueError and leaves the original booking intact.
The public owner field is None before booking and the accepted customer afterward.
The desk remains available for later calls. There is no expiry, cancellation,
database, UI, threading or network in this task. Use the Python standard library.
Keep the API. Work test-first and record actual red/green evidence. Run the tests.
