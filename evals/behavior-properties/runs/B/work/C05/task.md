Use test-quality-review. Assess the supplied tests for this small shipping-fee rule.
Inputs to this boundary are already validated integers. Supported weights are
1..20; weights 1..5 cost 4 and 6..20 cost 7. Other integer weights raise ValueError. This standalone pure rule has no persistence,
UI or network. Tests use unittest (also under python3 -O); there is no requirement
for a property-testing library. Review the actual evidence, run if useful, and
keep source/tests unchanged. Report material problems or a supported no-findings result.
