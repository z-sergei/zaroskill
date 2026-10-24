Use khorikov-unit-testing. Add valuable tests for SearchApp; preserve production code.
The UI calls search(query). Each call starts one request on the supplied gateway
and returns its token. Gateway completions arrive through receive(token, items).
Only the active request can update visible results. Starting another search keeps
the last visible results until its own answer arrives. Tokens are opaque identities;
their numerical values are not a consumer promise. The gateway is the external
port and there are no threads in this fixture. Use unittest and run the tests.
Explain the scenario/property coverage and its actual boundary.
