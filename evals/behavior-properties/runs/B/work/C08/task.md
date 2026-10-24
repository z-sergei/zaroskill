Use test-quality-review. Review the evidence for "disabled newsletter subscriptions
do not send welcome mail, enabled subscriptions do". There are two complementary
tests below. The SMTP boundary itself is covered by an existing adapter contract
suite; delivery to a human inbox is not promised by this local API. Inputs are
already validated before reaching this service. Use unittest. Keep files unchanged;
report supported findings or no findings within this scope.
