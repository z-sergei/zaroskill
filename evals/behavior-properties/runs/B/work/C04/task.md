Use test-quality-review. Review whether check_rules.py provides the stated
protection: invalid invoice amounts are refused and a normal amount gets the
correct total. CI runs exactly: python3 -O check_rules.py. Inspect and run if useful;
keep these files unchanged. There are no other tests. Record the evidence boundary.
