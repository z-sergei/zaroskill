# Execution log

## 06_upload_workflow — state-machine-verification

Read task, local SKILL.md and references/temporal-checks.md. Production upload.py unchanged.

Baseline, cwd work/cases/06_upload_workflow:
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`
Exit 0; Ran 3 tests in 0.000s; OK.

An initial apply_patch request was rejected because it used delete/add for the same path; no files changed. Retried with an update patch successfully.

After test changes, same command and cwd:
Exit 0; Ran 7 tests in 0.000s; OK.

Targeted sensitivity check in probes/06_rejected_begin_loses_owner, changed only the disposable production copy to lose active ownership before rejecting begin:

```text
Command: python3 -m unittest -v test_upload.UploadTests.test_rejected_begin_preserves_current_attempt
Exit: 1
test_rejected_begin_preserves_current_attempt (test_upload.UploadTests.test_rejected_begin_preserves_current_attempt) ... FAIL

======================================================================
FAIL: test_rejected_begin_preserves_current_attempt (test_upload.UploadTests.test_rejected_begin_preserves_current_attempt)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_rejected_begin_loses_owner/test_upload.py", line 68, in test_rejected_begin_preserves_current_attempt
    self.assertIs(session.complete(attempt, "original.csv"), True)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not True

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

## 05_mutation_report — test-quality-review

Read task, local SKILL.md and references/probes.md. Supplied JSON is a synthetic fixture, not a tool run.

Original baseline; cwd work/cases/05_mutation_report; PYTHONDONTWRITEBYTECODE=1:
```text
python3 -m unittest discover -v
Exit: 0
test_at_day_boundary (test_cancellation.CancellationTests.test_at_day_boundary) ... ok
test_at_free_boundary (test_cancellation.CancellationTests.test_at_free_boundary) ... ok
test_early_cancellation (test_cancellation.CancellationTests.test_early_cancellation) ... ok
test_half_fee_rounds_down (test_cancellation.CancellationTests.test_half_fee_rounds_down) ... ok
test_late_cancellation (test_cancellation.CancellationTests.test_late_cancellation) ... ok
test_negative_arguments (test_cancellation.CancellationTests.test_negative_arguments) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

Targeted disposable-copy probe M2 (unchanged tests):
```text
Exact supplied change M2: if hours_before >= 48: -> if hours_before >= 47:
Command: python3 -m unittest discover -v
Exit: 0
test_at_day_boundary (test_cancellation.CancellationTests.test_at_day_boundary) ... ok
test_at_free_boundary (test_cancellation.CancellationTests.test_at_free_boundary) ... ok
test_early_cancellation (test_cancellation.CancellationTests.test_early_cancellation) ... ok
test_half_fee_rounds_down (test_cancellation.CancellationTests.test_half_fee_rounds_down) ... ok
test_late_cancellation (test_cancellation.CancellationTests.test_late_cancellation) ... ok
test_negative_arguments (test_cancellation.CancellationTests.test_negative_arguments) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
Independent contract witness (47, 100): required 25, observed 0
```

Targeted disposable-copy probe M3 (unchanged tests):
```text
Exact supplied change M3: return paid_cents // 2 -> return (paid_cents + 1) // 2
Command: python3 -m unittest discover -v
Exit: 1
test_at_day_boundary (test_cancellation.CancellationTests.test_at_day_boundary) ... ok
test_at_free_boundary (test_cancellation.CancellationTests.test_at_free_boundary) ... ok
test_early_cancellation (test_cancellation.CancellationTests.test_early_cancellation) ... ok
test_half_fee_rounds_down (test_cancellation.CancellationTests.test_half_fee_rounds_down) ... FAIL
test_late_cancellation (test_cancellation.CancellationTests.test_late_cancellation) ... ok
test_negative_arguments (test_cancellation.CancellationTests.test_negative_arguments) ... ok

======================================================================
FAIL: test_half_fee_rounds_down (test_cancellation.CancellationTests.test_half_fee_rounds_down)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/05_M3/test_cancellation.py", line 19, in test_half_fee_rounds_down
    self.assertEqual(cancellation_fee(12, 101), 50)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 51 != 50

----------------------------------------------------------------------
Ran 6 tests in 0.000s

FAILED (failures=1)
Independent contract witness (12, 101): required 50, observed 51
```

Targeted disposable-copy probe M4 (unchanged tests):
```text
Exact supplied change M4: if hours_before >= 24: -> if hours_before >= 25:
Command: python3 -m unittest discover -v
Exit: 1
test_at_day_boundary (test_cancellation.CancellationTests.test_at_day_boundary) ... FAIL
test_at_free_boundary (test_cancellation.CancellationTests.test_at_free_boundary) ... ok
test_early_cancellation (test_cancellation.CancellationTests.test_early_cancellation) ... ok
test_half_fee_rounds_down (test_cancellation.CancellationTests.test_half_fee_rounds_down) ... ok
test_late_cancellation (test_cancellation.CancellationTests.test_late_cancellation) ... ok
test_negative_arguments (test_cancellation.CancellationTests.test_negative_arguments) ... ok

======================================================================
FAIL: test_at_day_boundary (test_cancellation.CancellationTests.test_at_day_boundary)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/05_M4/test_cancellation.py", line 10, in test_at_day_boundary
    self.assertEqual(cancellation_fee(24, 100), 25)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 50 != 25

----------------------------------------------------------------------
Ran 6 tests in 0.000s

FAILED (failures=1)
Independent contract witness (24, 100): required 25, observed 50
```

SHA-256 before/after matched for original cancellation.py, test_cancellation.py, mutation-report.json and task.md. No original executable or fixture was modified.

## 04_discount_cap — requirements-tdd

Read task, local SKILL.md and references/existing-code.md.

Baseline, cwd work/cases/04_discount_cap, PYTHONDONTWRITEBYTECODE=1:
```text
python3 -m unittest discover -v
Exit: 0
test_discount_rounds_down_to_whole_cents (test_discounts.DiscountTests.test_discount_rounds_down_to_whole_cents) ... ok
test_full_discount (test_discounts.DiscountTests.test_full_discount) ... ok
test_invalid_percent (test_discounts.DiscountTests.test_invalid_percent) ... ok
test_invalid_subtotal (test_discounts.DiscountTests.test_invalid_subtotal) ... ok
test_no_discount (test_discounts.DiscountTests.test_no_discount) ... ok
test_percentage_discount (test_discounts.DiscountTests.test_percentage_discount) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

TDD 1a — new test, production unchanged; absent API (not yet the arithmetic assertion):
```text
python3 -m unittest -v test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total
Exit: 1
test_cap_limits_discount_not_payable_total (test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total) ... ERROR

======================================================================
ERROR: test_cap_limits_discount_not_payable_total (test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 8, in test_cap_limits_discount_not_payable_total
    discounted_total(1000, 30, max_discount_cents=200), 800
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: discounted_total() got an unexpected keyword argument 'max_discount_cents'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

TDD 1b RED — declaration-only keyword scaffold, discount calculation unchanged:
```text
python3 -m unittest -v test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total
Exit: 1
test_cap_limits_discount_not_payable_total (test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total) ... FAIL

======================================================================
FAIL: test_cap_limits_discount_not_payable_total (test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 7, in test_cap_limits_discount_not_payable_total
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        discounted_total(1000, 30, max_discount_cents=200), 800
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: 700 != 800

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

TDD 1 GREEN — min(computed discount, cap), expected values unchanged:
```text
python3 -m unittest -v test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total
Exit: 0
test_cap_limits_discount_not_payable_total (test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

TDD 1 GREEN — min(computed discount, cap), expected values unchanged:
```text
python3 -m unittest discover -v
Exit: 0
test_cap_limits_discount_not_payable_total (test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total) ... ok
test_discount_rounds_down_to_whole_cents (test_discounts.DiscountTests.test_discount_rounds_down_to_whole_cents) ... ok
test_full_discount (test_discounts.DiscountTests.test_full_discount) ... ok
test_invalid_percent (test_discounts.DiscountTests.test_invalid_percent) ... ok
test_invalid_subtotal (test_discounts.DiscountTests.test_invalid_subtotal) ... ok
test_no_discount (test_discounts.DiscountTests.test_no_discount) ... ok
test_percentage_discount (test_discounts.DiscountTests.test_percentage_discount) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.000s

OK
```

TDD 2 RED — negative cap rejection test before validation implementation:
```text
python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount
Exit: 1
test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) ... 
  test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) (subtotal=1000, percent=30) ... FAIL
  test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) (subtotal=0, percent=30) ... FAIL
  test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) (subtotal=1000, percent=0) ... FAIL

======================================================================
FAIL: test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) (subtotal=1000, percent=30)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 14, in test_negative_cap_is_rejected_even_with_zero_discount
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) (subtotal=0, percent=30)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 14, in test_negative_cap_is_rejected_even_with_zero_discount
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) (subtotal=1000, percent=0)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 14, in test_negative_cap_is_rejected_even_with_zero_discount
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=3)
```

TDD 2 GREEN — validate negative cap before computing discount, expected values unchanged:
```text
python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount
Exit: 0
test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

TDD 2 GREEN — validate negative cap before computing discount, expected values unchanged:
```text
python3 -m unittest discover -v
Exit: 0
test_cap_limits_discount_not_payable_total (test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total) ... ok
test_discount_rounds_down_to_whole_cents (test_discounts.DiscountTests.test_discount_rounds_down_to_whole_cents) ... ok
test_full_discount (test_discounts.DiscountTests.test_full_discount) ... ok
test_invalid_percent (test_discounts.DiscountTests.test_invalid_percent) ... ok
test_invalid_subtotal (test_discounts.DiscountTests.test_invalid_subtotal) ... ok
test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) ... ok
test_no_discount (test_discounts.DiscountTests.test_no_discount) ... ok
test_percentage_discount (test_discounts.DiscountTests.test_percentage_discount) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

Final compatibility and boundary evidence — new examples already green; no invented red cycle for behavior covered by the prior implementation:
```text
python3 -m unittest discover -v
Exit: 0
test_cap_limits_discount_not_payable_total (test_discounts.DiscountTests.test_cap_limits_discount_not_payable_total) ... ok
test_cap_must_be_passed_by_keyword (test_discounts.DiscountTests.test_cap_must_be_passed_by_keyword) ... ok
test_discount_rounds_down_to_whole_cents (test_discounts.DiscountTests.test_discount_rounds_down_to_whole_cents) ... ok
test_explicit_none_preserves_rounded_percentage_discount (test_discounts.DiscountTests.test_explicit_none_preserves_rounded_percentage_discount) ... ok
test_full_discount (test_discounts.DiscountTests.test_full_discount) ... ok
test_invalid_percent (test_discounts.DiscountTests.test_invalid_percent) ... ok
test_invalid_subtotal (test_discounts.DiscountTests.test_invalid_subtotal) ... ok
test_negative_cap_is_rejected_even_with_zero_discount (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_with_zero_discount) ... ok
test_no_discount (test_discounts.DiscountTests.test_no_discount) ... ok
test_percentage_discount (test_discounts.DiscountTests.test_percentage_discount) ... ok
test_zero_equal_and_larger_caps_keep_the_correct_payable_total (test_discounts.DiscountTests.test_zero_equal_and_larger_caps_keep_the_correct_payable_total) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.000s

OK
```

## 03_capacity_boundaries — test-quality-review

Read task; applied local review skill (already read) and references/boundaries-and-traps.md; reused local probes.md guidance.

Baseline:
```text
python3 -m unittest discover -v
Exit: 0
test_request_maps_over_capacity_without_mutating_input (test_capacity.RequestTests.test_request_maps_over_capacity_without_mutating_input) ... ok
test_request_reports_exact_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_exact_capacity_without_mutating_input) ... ok
test_request_reports_success_for_zero_at_capacity (test_capacity.RequestTests.test_request_reports_success_for_zero_at_capacity) ... ok
test_domain_allows_exact_capacity (test_capacity.ReservationTests.test_domain_allows_exact_capacity) ... ok
test_domain_allows_zero_at_capacity (test_capacity.ReservationTests.test_domain_allows_zero_at_capacity) ... ok
test_domain_rejects_over_capacity (test_capacity.ReservationTests.test_domain_rejects_over_capacity) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

Original suite on disposable fault returning limit instead of actual updated occupancy:
```text
python3 -m unittest discover -v
Exit: 0
test_request_maps_over_capacity_without_mutating_input (test_capacity.RequestTests.test_request_maps_over_capacity_without_mutating_input) ... ok
test_request_reports_exact_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_exact_capacity_without_mutating_input) ... ok
test_request_reports_success_for_zero_at_capacity (test_capacity.RequestTests.test_request_reports_success_for_zero_at_capacity) ... ok
test_domain_allows_exact_capacity (test_capacity.ReservationTests.test_domain_allows_exact_capacity) ... ok
test_domain_allows_zero_at_capacity (test_capacity.ReservationTests.test_domain_allows_zero_at_capacity) ... ok
test_domain_rejects_over_capacity (test_capacity.ReservationTests.test_domain_rejects_over_capacity) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

Final working suite:
```text
python3 -m unittest discover -v
Exit: 0
test_request_maps_over_capacity_without_mutating_input (test_capacity.RequestTests.test_request_maps_over_capacity_without_mutating_input) ... ok
test_request_reports_exact_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_exact_capacity_without_mutating_input) ... ok
test_request_reports_usage_below_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_usage_below_capacity_without_mutating_input) ... ok
test_request_reports_zero_at_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_zero_at_capacity_without_mutating_input) ... ok
test_domain_allows_exact_capacity (test_capacity.ReservationTests.test_domain_allows_exact_capacity) ... ok
test_domain_allows_zero_at_capacity (test_capacity.ReservationTests.test_domain_allows_zero_at_capacity) ... ok
test_domain_rejects_over_capacity (test_capacity.ReservationTests.test_domain_rejects_over_capacity) ... ok
test_domain_returns_actual_usage_below_capacity (test_capacity.ReservationTests.test_domain_returns_actual_usage_below_capacity) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

Strengthened suite on the same return-limit fault:
```text
python3 -m unittest discover -v
Exit: 1
test_request_maps_over_capacity_without_mutating_input (test_capacity.RequestTests.test_request_maps_over_capacity_without_mutating_input) ... ok
test_request_reports_exact_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_exact_capacity_without_mutating_input) ... ok
test_request_reports_usage_below_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_usage_below_capacity_without_mutating_input) ... FAIL
test_request_reports_zero_at_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_zero_at_capacity_without_mutating_input) ... ok
test_domain_allows_exact_capacity (test_capacity.ReservationTests.test_domain_allows_exact_capacity) ... ok
test_domain_allows_zero_at_capacity (test_capacity.ReservationTests.test_domain_allows_zero_at_capacity) ... ok
test_domain_rejects_over_capacity (test_capacity.ReservationTests.test_domain_rejects_over_capacity) ... ok
test_domain_returns_actual_usage_below_capacity (test_capacity.ReservationTests.test_domain_returns_actual_usage_below_capacity) ... FAIL

======================================================================
FAIL: test_request_reports_usage_below_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_usage_below_capacity_without_mutating_input)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/03_returns_limit/test_capacity.py", line 24, in test_request_reports_usage_below_capacity_without_mutating_input
    self.assertEqual(handle_request(payload), {"status": "ok", "used": 9})
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'status': 'ok', 'used': 10} != {'status': 'ok', 'used': 9}
- {'status': 'ok', 'used': 10}
?                          ^^

+ {'status': 'ok', 'used': 9}
?                          ^


======================================================================
FAIL: test_domain_returns_actual_usage_below_capacity (test_capacity.ReservationTests.test_domain_returns_actual_usage_below_capacity)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/03_returns_limit/test_capacity.py", line 7, in test_domain_returns_actual_usage_below_capacity
    self.assertEqual(reserve(7, 2, 10), 9)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 10 != 9

----------------------------------------------------------------------
Ran 8 tests in 0.001s

FAILED (failures=2)
```

## 02_display_name — khorikov-unit-testing

Read task and local SKILL.md; pure output boundary, no doubles or generated properties.

Baseline:
```text
python3 -m unittest discover -v
Exit: 0
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.000s

OK
```

02_ascii_trim original tests, disposable copy only:
```text
def clean_display_name(raw):
    name = raw.strip(" \t\n")
    if not 1 <= len(name) <= 20:
        raise ValueError("display name must contain 1 to 20 characters")
    return name

python3 -m unittest discover -v
Exit: 0
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.000s

OK
```

02_normalizes_name original tests, disposable copy only:
```text
import unicodedata

def clean_display_name(raw):
    name = unicodedata.normalize("NFC", raw.strip())
    if not 1 <= len(name) <= 20:
        raise ValueError("display name must contain 1 to 20 characters")
    return name

python3 -m unittest discover -v
Exit: 0
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.000s

OK
```

02_ascii_trim new tests, same disposable fault:
```text
python3 -m unittest discover -v
Exit: 1
test_combining_marks_count_toward_the_length_limit (test_names.DisplayNameTests.test_combining_marks_count_toward_the_length_limit) ... ok
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_unicode_edge_whitespace_is_trimmed_and_inner_whitespace_preserved (test_names.DisplayNameTests.test_unicode_edge_whitespace_is_trimmed_and_inner_whitespace_preserved) ... FAIL
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

======================================================================
FAIL: test_unicode_edge_whitespace_is_trimmed_and_inner_whitespace_preserved (test_names.DisplayNameTests.test_unicode_edge_whitespace_is_trimmed_and_inner_whitespace_preserved)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/02_ascii_trim/test_names.py", line 32, in test_unicode_edge_whitespace_is_trimmed_and_inner_whitespace_preserved
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        clean_display_name("\u2003\u00a0Ada\u00a0Lee\u00a0\u2003"),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        "Ada\u00a0Lee",
        ^^^^^^^^^^^^^^^
    )
    ^
AssertionError: '\u2003\xa0Ada\xa0Lee\xa0\u2003' != 'Ada\xa0Lee'
-   Ada Lee  
? --       --
+ Ada Lee


----------------------------------------------------------------------
Ran 9 tests in 0.000s

FAILED (failures=1)
```

02_normalizes_name new tests, same disposable fault:
```text
python3 -m unittest discover -v
Exit: 1
test_combining_marks_count_toward_the_length_limit (test_names.DisplayNameTests.test_combining_marks_count_toward_the_length_limit) ... FAIL
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_unicode_edge_whitespace_is_trimmed_and_inner_whitespace_preserved (test_names.DisplayNameTests.test_unicode_edge_whitespace_is_trimmed_and_inner_whitespace_preserved) ... ok
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

======================================================================
FAIL: test_combining_marks_count_toward_the_length_limit (test_names.DisplayNameTests.test_combining_marks_count_toward_the_length_limit)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/02_normalizes_name/test_names.py", line 40, in test_combining_marks_count_toward_the_length_limit
    self.assertEqual(clean_display_name(name), name)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'éééééééééé' != 'éééééééééé'
- éééééééééé
+ éééééééééé


----------------------------------------------------------------------
Ran 9 tests in 0.000s

FAILED (failures=1)
```

Final unchanged production with strengthened tests:
```text
python3 -m unittest discover -v
Exit: 0
test_combining_marks_count_toward_the_length_limit (test_names.DisplayNameTests.test_combining_marks_count_toward_the_length_limit) ... ok
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_unicode_edge_whitespace_is_trimmed_and_inner_whitespace_preserved (test_names.DisplayNameTests.test_unicode_edge_whitespace_is_trimmed_and_inner_whitespace_preserved) ... ok
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.000s

OK
```

## 01_shipping_bands — khorikov-unit-testing

Read task; applied the already-read local skill separately to the shipping contract.

Baseline:
```text
python3 -m unittest discover -v
Exit: 0
test_another_discounted_basket (test_shipping.ShippingTests.test_another_discounted_basket) ... ok
test_at_first_threshold (test_shipping.ShippingTests.test_at_first_threshold) ... ok
test_at_free_threshold (test_shipping.ShippingTests.test_at_free_threshold) ... ok
test_below_first_threshold (test_shipping.ShippingTests.test_below_first_threshold) ... ok
test_below_free_threshold (test_shipping.ShippingTests.test_below_free_threshold) ... ok
test_discounted_basket (test_shipping.ShippingTests.test_discounted_basket) ... ok
test_large_basket (test_shipping.ShippingTests.test_large_basket) ... ok
test_medium_basket (test_shipping.ShippingTests.test_medium_basket) ... ok
test_negative_basket (test_shipping.ShippingTests.test_negative_basket) ... ok
test_negative_cent (test_shipping.ShippingTests.test_negative_cent) ... ok
test_small_basket (test_shipping.ShippingTests.test_small_basket) ... ok
test_very_large_basket (test_shipping.ShippingTests.test_very_large_basket) ... ok
test_zero (test_shipping.ShippingTests.test_zero) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.000s

OK
```

01_excludes_5000 on unchanged original tests:
```text
def delivery_fee(subtotal_cents):
    if subtotal_cents < 0:
        raise ValueError("subtotal cannot be negative")
    if subtotal_cents >= 10000:
        return 0
    if subtotal_cents > 5000:
        return 250
    return 500

python3 -m unittest discover -v
Exit: 1
test_another_discounted_basket (test_shipping.ShippingTests.test_another_discounted_basket) ... ok
test_at_first_threshold (test_shipping.ShippingTests.test_at_first_threshold) ... FAIL
test_at_free_threshold (test_shipping.ShippingTests.test_at_free_threshold) ... ok
test_below_first_threshold (test_shipping.ShippingTests.test_below_first_threshold) ... ok
test_below_free_threshold (test_shipping.ShippingTests.test_below_free_threshold) ... ok
test_discounted_basket (test_shipping.ShippingTests.test_discounted_basket) ... ok
test_large_basket (test_shipping.ShippingTests.test_large_basket) ... ok
test_medium_basket (test_shipping.ShippingTests.test_medium_basket) ... ok
test_negative_basket (test_shipping.ShippingTests.test_negative_basket) ... ok
test_negative_cent (test_shipping.ShippingTests.test_negative_cent) ... ok
test_small_basket (test_shipping.ShippingTests.test_small_basket) ... ok
test_very_large_basket (test_shipping.ShippingTests.test_very_large_basket) ... ok
test_zero (test_shipping.ShippingTests.test_zero) ... ok

======================================================================
FAIL: test_at_first_threshold (test_shipping.ShippingTests.test_at_first_threshold)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/01_excludes_5000/test_shipping.py", line 19, in test_at_first_threshold
    self.assertEqual(delivery_fee(5000), 250)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 500 != 250

----------------------------------------------------------------------
Ran 13 tests in 0.000s

FAILED (failures=1)
```

01_excludes_10000 on unchanged original tests:
```text
def delivery_fee(subtotal_cents):
    if subtotal_cents < 0:
        raise ValueError("subtotal cannot be negative")
    if subtotal_cents > 10000:
        return 0
    if subtotal_cents >= 5000:
        return 250
    return 500

python3 -m unittest discover -v
Exit: 1
test_another_discounted_basket (test_shipping.ShippingTests.test_another_discounted_basket) ... ok
test_at_first_threshold (test_shipping.ShippingTests.test_at_first_threshold) ... ok
test_at_free_threshold (test_shipping.ShippingTests.test_at_free_threshold) ... FAIL
test_below_first_threshold (test_shipping.ShippingTests.test_below_first_threshold) ... ok
test_below_free_threshold (test_shipping.ShippingTests.test_below_free_threshold) ... ok
test_discounted_basket (test_shipping.ShippingTests.test_discounted_basket) ... ok
test_large_basket (test_shipping.ShippingTests.test_large_basket) ... ok
test_medium_basket (test_shipping.ShippingTests.test_medium_basket) ... ok
test_negative_basket (test_shipping.ShippingTests.test_negative_basket) ... ok
test_negative_cent (test_shipping.ShippingTests.test_negative_cent) ... ok
test_small_basket (test_shipping.ShippingTests.test_small_basket) ... ok
test_very_large_basket (test_shipping.ShippingTests.test_very_large_basket) ... ok
test_zero (test_shipping.ShippingTests.test_zero) ... ok

======================================================================
FAIL: test_at_free_threshold (test_shipping.ShippingTests.test_at_free_threshold)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/01_excludes_10000/test_shipping.py", line 31, in test_at_free_threshold
    self.assertEqual(delivery_fee(10000), 0)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 250 != 0

----------------------------------------------------------------------
Ran 13 tests in 0.000s

FAILED (failures=1)
```

01_rejects_only_minus_one on unchanged original tests:
```text
def delivery_fee(subtotal_cents):
    if subtotal_cents == -1:
        raise ValueError("subtotal cannot be negative")
    if subtotal_cents >= 10000:
        return 0
    if subtotal_cents >= 5000:
        return 250
    return 500

python3 -m unittest discover -v
Exit: 1
test_another_discounted_basket (test_shipping.ShippingTests.test_another_discounted_basket) ... ok
test_at_first_threshold (test_shipping.ShippingTests.test_at_first_threshold) ... ok
test_at_free_threshold (test_shipping.ShippingTests.test_at_free_threshold) ... ok
test_below_first_threshold (test_shipping.ShippingTests.test_below_first_threshold) ... ok
test_below_free_threshold (test_shipping.ShippingTests.test_below_free_threshold) ... ok
test_discounted_basket (test_shipping.ShippingTests.test_discounted_basket) ... ok
test_large_basket (test_shipping.ShippingTests.test_large_basket) ... ok
test_medium_basket (test_shipping.ShippingTests.test_medium_basket) ... ok
test_negative_basket (test_shipping.ShippingTests.test_negative_basket) ... FAIL
test_negative_cent (test_shipping.ShippingTests.test_negative_cent) ... ok
test_small_basket (test_shipping.ShippingTests.test_small_basket) ... ok
test_very_large_basket (test_shipping.ShippingTests.test_very_large_basket) ... ok
test_zero (test_shipping.ShippingTests.test_zero) ... ok

======================================================================
FAIL: test_negative_basket (test_shipping.ShippingTests.test_negative_basket)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/01_rejects_only_minus_one/test_shipping.py", line 44, in test_negative_basket
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 13 tests in 0.000s

FAILED (failures=1)
```

01_excludes_5000 on simplified tests (same fault):
```text
python3 -m unittest discover -v
Exit: 1
test_free_delivery_from_10000_cents (test_shipping.ShippingTests.test_free_delivery_from_10000_cents) ... ok
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... ok
test_reduced_fee_from_5000_through_9999_cents (test_shipping.ShippingTests.test_reduced_fee_from_5000_through_9999_cents) ... 
  test_reduced_fee_from_5000_through_9999_cents (test_shipping.ShippingTests.test_reduced_fee_from_5000_through_9999_cents) (subtotal_cents=5000) ... FAIL
test_standard_fee_below_5000_cents (test_shipping.ShippingTests.test_standard_fee_below_5000_cents) ... ok

======================================================================
FAIL: test_reduced_fee_from_5000_through_9999_cents (test_shipping.ShippingTests.test_reduced_fee_from_5000_through_9999_cents) (subtotal_cents=5000)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/01_excludes_5000/test_shipping.py", line 14, in test_reduced_fee_from_5000_through_9999_cents
    self.assertEqual(delivery_fee(subtotal), 250)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 500 != 250

----------------------------------------------------------------------
Ran 4 tests in 0.000s

FAILED (failures=1)
```

01_excludes_10000 on simplified tests (same fault):
```text
python3 -m unittest discover -v
Exit: 1
test_free_delivery_from_10000_cents (test_shipping.ShippingTests.test_free_delivery_from_10000_cents) ... 
  test_free_delivery_from_10000_cents (test_shipping.ShippingTests.test_free_delivery_from_10000_cents) (subtotal_cents=10000) ... FAIL
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... ok
test_reduced_fee_from_5000_through_9999_cents (test_shipping.ShippingTests.test_reduced_fee_from_5000_through_9999_cents) ... ok
test_standard_fee_below_5000_cents (test_shipping.ShippingTests.test_standard_fee_below_5000_cents) ... ok

======================================================================
FAIL: test_free_delivery_from_10000_cents (test_shipping.ShippingTests.test_free_delivery_from_10000_cents) (subtotal_cents=10000)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/01_excludes_10000/test_shipping.py", line 19, in test_free_delivery_from_10000_cents
    self.assertEqual(delivery_fee(subtotal), 0)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 250 != 0

----------------------------------------------------------------------
Ran 4 tests in 0.000s

FAILED (failures=1)
```

01_rejects_only_minus_one on simplified tests (same fault):
```text
python3 -m unittest discover -v
Exit: 1
test_free_delivery_from_10000_cents (test_shipping.ShippingTests.test_free_delivery_from_10000_cents) ... ok
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... 
  test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) (subtotal_cents=-200) ... FAIL
test_reduced_fee_from_5000_through_9999_cents (test_shipping.ShippingTests.test_reduced_fee_from_5000_through_9999_cents) ... ok
test_standard_fee_below_5000_cents (test_shipping.ShippingTests.test_standard_fee_below_5000_cents) ... ok

======================================================================
FAIL: test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) (subtotal_cents=-200)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/01_rejects_only_minus_one/test_shipping.py", line 24, in test_negative_subtotals_are_rejected
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 4 tests in 0.000s

FAILED (failures=1)
```

Final unchanged production:
```text
python3 -m unittest discover -v
Exit: 0
test_free_delivery_from_10000_cents (test_shipping.ShippingTests.test_free_delivery_from_10000_cents) ... ok
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... ok
test_reduced_fee_from_5000_through_9999_cents (test_shipping.ShippingTests.test_reduced_fee_from_5000_through_9999_cents) ... ok
test_standard_fee_below_5000_cents (test_shipping.ShippingTests.test_standard_fee_below_5000_cents) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

## Completion

All six cases completed in order.json order. Required answer files and edited source/test files were checked for existence. summary.json records per-case outcomes. Final passing checks were already run after each final executable change; no further executable changes were made.
