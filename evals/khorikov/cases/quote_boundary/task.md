# Test a portable checkout quote

Add useful regression tests for the real `quote` function using Python standard-library unittest.
Put English tests in tests/test_*.py, keep pricing.py unchanged, and run the suite. Use no third-party
packages, live services, or duplicated production algorithm. Explain the contract and limits in report.md.

The function accepts any iterable of Line values, including a one-shot generator. An order must
contain at least one line. Each unit price is an integer number of minor currency units, zero or more;
each quantity is a strictly positive integer. Booleans do not count as integers for any money,
quantity, or percentage input. The discount is an integer percentage between 0 and 100 inclusive.
The supplied shipping charge is a non-negative integer number of minor currency units. Invalid
input raises ValueError; exact exception wording is not a public contract.

Gross is the combined line value, including quantities. Apply the percentage to the combined gross
once and round the resulting discount to the nearest minor unit, with half a minor unit rounded up.
Do not round separately per line. Physical orders qualify for free shipping when the discounted
subtotal is at least 5000 minor units; smaller subtotals pay the supplied shipping charge.
Digital orders always have zero shipping. The quote exposes immutable gross, discount, shipping,
and final total values. The final total is the discounted subtotal plus applicable shipping.

Choose compact, explicit examples whose expected values are independently calculated. Test behavior
through quote and the returned values. Private helper names, object identity, iteration counts,
implementation text, and exception wording are not part of this contract.
