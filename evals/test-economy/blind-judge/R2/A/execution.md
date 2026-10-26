# Фактическое выполнение

Все команды запускаются в изолированном корне или указанном случае; зависимости не устанавливались, сеть не использовалась.

## 06_upload_workflow — state-machine-verification

- Исходный `python -m unittest discover -v`: exit 127, `python` отсутствует.
- Исходный `python3 -m unittest discover -v`: exit 0, 3 tests, OK.
- После изменений `python3 -m unittest discover -v`: exit 0, 8 tests, OK.
- В одноразовой копии `probes/06_upload_identity` удалена проверка соответствия id в `complete`; production-файл случая не изменён. Команда `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 1:

```text
test_cancel_active_upload (test_upload.UploadTests.test_cancel_active_upload) ... ok
test_completion_wins_before_cancel_and_duplicate_completion (test_upload.UploadTests.test_completion_wins_before_cancel_and_duplicate_completion) ... ok
test_idle_rejects_completion_and_cancellation (test_upload.UploadTests.test_idle_rejects_completion_and_cancellation) ... ok
test_rejected_begin_preserves_the_waiting_attempt (test_upload.UploadTests.test_rejected_begin_preserves_the_waiting_attempt) ... ok
test_restart_after_cancel_rejects_old_completion_before_accepting_new (test_upload.UploadTests.test_restart_after_cancel_rejects_old_completion_before_accepting_new) ... FAIL
test_restart_after_success_clears_result_and_rejects_old_completions (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_completions) ... 
  test_restart_after_success_clears_result_and_rejects_old_completions (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_completions) (stale_id=1, result='second.csv') ... FAIL
  test_restart_after_success_clears_result_and_rejects_old_completions (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_completions) (result='second.csv') ... FAIL
  test_restart_after_success_clears_result_and_rejects_old_completions (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_completions) (stale_id=1, result='third.csv') ... FAIL
  test_restart_after_success_clears_result_and_rejects_old_completions (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_completions) (result='third.csv') ... FAIL
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... FAIL

======================================================================
FAIL: test_restart_after_cancel_rejects_old_completion_before_accepting_new (test_upload.UploadTests.test_restart_after_cancel_rejects_old_completion_before_accepting_new)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_upload_identity/test_upload.py", line 92, in test_restart_after_cancel_rejects_old_completion_before_accepting_new
    self.assertFalse(session.complete(cancelled_attempt, "stale.csv"))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not false

======================================================================
FAIL: test_restart_after_success_clears_result_and_rejects_old_completions (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_completions) (stale_id=1, result='second.csv')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_upload_identity/test_upload.py", line 77, in test_restart_after_success_clears_result_and_rejects_old_completions
    self.assertFalse(session.complete(old_attempt, "stale.csv"))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not false

======================================================================
FAIL: test_restart_after_success_clears_result_and_rejects_old_completions (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_completions) (result='second.csv')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_upload_identity/test_upload.py", line 79, in test_restart_after_success_clears_result_and_rejects_old_completions
    self.assertTrue(session.complete(attempt, value))
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true

======================================================================
FAIL: test_restart_after_success_clears_result_and_rejects_old_completions (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_completions) (stale_id=1, result='third.csv')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_upload_identity/test_upload.py", line 77, in test_restart_after_success_clears_result_and_rejects_old_completions
    self.assertFalse(session.complete(old_attempt, "stale.csv"))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not false

======================================================================
FAIL: test_restart_after_success_clears_result_and_rejects_old_completions (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_completions) (result='third.csv')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_upload_identity/test_upload.py", line 79, in test_restart_after_success_clears_result_and_rejects_old_completions
    self.assertTrue(session.complete(attempt, value))
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true

======================================================================
FAIL: test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_upload_identity/test_upload.py", line 29, in test_unknown_completion_preserves_current_attempt
    self.assertFalse(session.complete(attempt + 1, "wrong.csv"))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not false

----------------------------------------------------------------------
Ran 8 tests in 0.001s

FAILED (failures=6)
```

## 05_mutation_report — test-quality-review

Приложенный JSON — синтетическая фикстура, не наш запуск инструмента. Ниже — отдельно исполненные ручные локальные пробы в копиях с неизменёнными тестами.

### Исходный набор

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
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

### Ручная проба M1

Изменение: `return paid_cents // 4` → `return (paid_cents - paid_cents % 4) // 4`.

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
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

### Ручная проба M2

Изменение: `if hours_before >= 48:` → `if hours_before >= 47:`.

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
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

Дополнительно выполнено прямое наблюдение (не часть исходного набора): `cancellation_fee(47, 103)` возвращает 25 в оригинале и 0 в M2. Контракт требует 25.

### Ручная проба M3

Изменение: `return paid_cents // 2` → `return (paid_cents + 1) // 2`.

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 1

```text
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
```

### Ручная проба M4

Изменение: `if hours_before >= 24:` → `if hours_before >= 25:`.

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 1

```text
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
```

## 04_discount_cap — requirements-tdd

### База до изменений

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
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

### Срез 1, тест до объявления API

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_cap_limits_discount_not_total`, exit 1

```text
test_cap_limits_discount_not_total (test_discounts.DiscountTests.test_cap_limits_discount_not_total) ... ERROR

======================================================================
ERROR: test_cap_limits_discount_not_total (test_discounts.DiscountTests.test_cap_limits_discount_not_total)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 28, in test_cap_limits_discount_not_total
    self.assertEqual(discounted_total(1000, 30, max_discount_cents=200), 800)
                     ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: discounted_total() got an unexpected keyword argument 'max_discount_cents'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

### Срез 1, RED: объявлен только инертный keyword-only аргумент

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_cap_limits_discount_not_total`, exit 1

```text
test_cap_limits_discount_not_total (test_discounts.DiscountTests.test_cap_limits_discount_not_total) ... FAIL

======================================================================
FAIL: test_cap_limits_discount_not_total (test_discounts.DiscountTests.test_cap_limits_discount_not_total)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 28, in test_cap_limits_discount_not_total
    self.assertEqual(discounted_total(1000, 30, max_discount_cents=200), 800)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 700 != 800

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

### Срез 1, GREEN: тот же тест

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_cap_limits_discount_not_total`, exit 0

```text
test_cap_limits_discount_not_total (test_discounts.DiscountTests.test_cap_limits_discount_not_total) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

### Срез 1, регрессии

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
test_cap_limits_discount_not_total (test_discounts.DiscountTests.test_cap_limits_discount_not_total) ... ok
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

### Срез 2, RED: отрицательный лимит до валидации

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero`, exit 1

```text
test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) ... 
  test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) (subtotal=1000, percent=15) ... FAIL
  test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) (subtotal=1000, percent=0) ... FAIL
  test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) (subtotal=0, percent=15) ... FAIL

======================================================================
FAIL: test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) (subtotal=1000, percent=15)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 32, in test_negative_cap_is_rejected_even_when_computed_discount_is_zero
    with self.subTest(subtotal=subtotal, percent=percent), self.assertRaises(ValueError):
                                                           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) (subtotal=1000, percent=0)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 32, in test_negative_cap_is_rejected_even_when_computed_discount_is_zero
    with self.subTest(subtotal=subtotal, percent=percent), self.assertRaises(ValueError):
                                                           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) (subtotal=0, percent=15)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 32, in test_negative_cap_is_rejected_even_when_computed_discount_is_zero
    with self.subTest(subtotal=subtotal, percent=percent), self.assertRaises(ValueError):
                                                           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=3)
```

### Срез 2, GREEN: тот же тест

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero`, exit 0

```text
test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

### Срез 2, регрессии

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
test_cap_limits_discount_not_total (test_discounts.DiscountTests.test_cap_limits_discount_not_total) ... ok
test_discount_rounds_down_to_whole_cents (test_discounts.DiscountTests.test_discount_rounds_down_to_whole_cents) ... ok
test_full_discount (test_discounts.DiscountTests.test_full_discount) ... ok
test_invalid_percent (test_discounts.DiscountTests.test_invalid_percent) ... ok
test_invalid_subtotal (test_discounts.DiscountTests.test_invalid_subtotal) ... ok
test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) ... ok
test_no_discount (test_discounts.DiscountTests.test_no_discount) ... ok
test_percentage_discount (test_discounts.DiscountTests.test_percentage_discount) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

### Финал: добавлены проверки уже полученного поведения, не новые RED/GREEN циклы

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
test_cap_limits_discount_not_total (test_discounts.DiscountTests.test_cap_limits_discount_not_total) ... ok
test_discount_cap_must_be_passed_by_keyword (test_discounts.DiscountTests.test_discount_cap_must_be_passed_by_keyword) ... ok
test_discount_rounds_down_to_whole_cents (test_discounts.DiscountTests.test_discount_rounds_down_to_whole_cents) ... ok
test_explicit_none_preserves_uncapped_discount (test_discounts.DiscountTests.test_explicit_none_preserves_uncapped_discount) ... ok
test_full_discount (test_discounts.DiscountTests.test_full_discount) ... ok
test_invalid_percent (test_discounts.DiscountTests.test_invalid_percent) ... ok
test_invalid_subtotal (test_discounts.DiscountTests.test_invalid_subtotal) ... ok
test_negative_cap_is_rejected_even_when_computed_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_computed_discount_is_zero) ... ok
test_no_discount (test_discounts.DiscountTests.test_no_discount) ... ok
test_nonbinding_cap_preserves_rounded_percentage_discount (test_discounts.DiscountTests.test_nonbinding_cap_preserves_rounded_percentage_discount) ... ok
test_percentage_discount (test_discounts.DiscountTests.test_percentage_discount) ... ok
test_zero_cap_prevents_any_discount (test_discounts.DiscountTests.test_zero_cap_prevents_any_discount) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
```

## 03_capacity_boundaries — test-quality-review

### База (исходные 6 тестов)

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
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

### Ручная проба: reserve возвращает limit вместо updated, исходные тесты

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
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

### После усиления, исходный production

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
test_request_maps_over_capacity_without_mutating_input (test_capacity.RequestTests.test_request_maps_over_capacity_without_mutating_input) ... ok
test_request_reports_exact_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_exact_capacity_without_mutating_input) ... ok
test_request_reports_partial_usage_without_mutating_input (test_capacity.RequestTests.test_request_reports_partial_usage_without_mutating_input) ... ok
test_request_reports_success_for_zero_at_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_success_for_zero_at_capacity_without_mutating_input) ... ok
test_domain_adds_request_below_capacity (test_capacity.ReservationTests.test_domain_adds_request_below_capacity) ... ok
test_domain_allows_exact_capacity (test_capacity.ReservationTests.test_domain_allows_exact_capacity) ... ok
test_domain_allows_zero_at_capacity (test_capacity.ReservationTests.test_domain_allows_zero_at_capacity) ... ok
test_domain_rejects_over_capacity (test_capacity.ReservationTests.test_domain_rejects_over_capacity) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

### Та же проба return limit, усиленный набор

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 1

```text
test_request_maps_over_capacity_without_mutating_input (test_capacity.RequestTests.test_request_maps_over_capacity_without_mutating_input) ... ok
test_request_reports_exact_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_exact_capacity_without_mutating_input) ... ok
test_request_reports_partial_usage_without_mutating_input (test_capacity.RequestTests.test_request_reports_partial_usage_without_mutating_input) ... FAIL
test_request_reports_success_for_zero_at_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_success_for_zero_at_capacity_without_mutating_input) ... ok
test_domain_adds_request_below_capacity (test_capacity.ReservationTests.test_domain_adds_request_below_capacity) ... FAIL
test_domain_allows_exact_capacity (test_capacity.ReservationTests.test_domain_allows_exact_capacity) ... ok
test_domain_allows_zero_at_capacity (test_capacity.ReservationTests.test_domain_allows_zero_at_capacity) ... ok
test_domain_rejects_over_capacity (test_capacity.ReservationTests.test_domain_rejects_over_capacity) ... ok

======================================================================
FAIL: test_request_reports_partial_usage_without_mutating_input (test_capacity.RequestTests.test_request_reports_partial_usage_without_mutating_input)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/03_return_limit/test_capacity.py", line 24, in test_request_reports_partial_usage_without_mutating_input
    self.assertEqual(handle_request(payload), {"status": "ok", "used": 5})
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'status': 'ok', 'used': 10} != {'status': 'ok', 'used': 5}
- {'status': 'ok', 'used': 10}
?                          ^^

+ {'status': 'ok', 'used': 5}
?                          ^


======================================================================
FAIL: test_domain_adds_request_below_capacity (test_capacity.ReservationTests.test_domain_adds_request_below_capacity)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/03_return_limit/test_capacity.py", line 7, in test_domain_adds_request_below_capacity
    self.assertEqual(reserve(2, 3, 10), 5)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 10 != 5

----------------------------------------------------------------------
Ran 8 tests in 0.001s

FAILED (failures=2)
```

## 02_display_name — khorikov-unit-testing

### База до изменений

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
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

### Ручная проба: strip только ASCII whitespace, исходные тесты

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
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

### После изменений, исходный production

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
test_combining_characters_are_preserved_and_count_towards_length (test_names.DisplayNameTests.test_combining_characters_are_preserved_and_count_towards_length) ... ok
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_unicode_whitespace_is_trimmed_from_edges (test_names.DisplayNameTests.test_unicode_whitespace_is_trimmed_from_edges) ... ok
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.000s

OK
```

### ASCII-only strip с усиленным набором

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 1

```text
test_combining_characters_are_preserved_and_count_towards_length (test_names.DisplayNameTests.test_combining_characters_are_preserved_and_count_towards_length) ... ok
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_unicode_whitespace_is_trimmed_from_edges (test_names.DisplayNameTests.test_unicode_whitespace_is_trimmed_from_edges) ... FAIL
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

======================================================================
FAIL: test_unicode_whitespace_is_trimmed_from_edges (test_names.DisplayNameTests.test_unicode_whitespace_is_trimmed_from_edges)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/02_ascii_strip/test_names.py", line 32, in test_unicode_whitespace_is_trimmed_from_edges
    self.assertEqual(clean_display_name("\u00a0\u2003Ada\u2003\u00a0"), "Ada")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: '\xa0\u2003Ada\u2003\xa0' != 'Ada'
-   Ada  
+ Ada


----------------------------------------------------------------------
Ran 9 tests in 0.000s

FAILED (failures=1)
```

## 01_shipping_bands — khorikov-unit-testing

### База до изменений

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
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

### Ручная проба: бесплатность только при >10000, исходные тесты

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 1

```text
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
  File "<run>/probes/01_free_boundary/test_shipping.py", line 31, in test_at_free_threshold
    self.assertEqual(delivery_fee(10000), 0)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 250 != 0

----------------------------------------------------------------------
Ran 13 tests in 0.000s

FAILED (failures=1)
```

### Упрощённый набор, исходный production

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 0

```text
test_baskets_below_5000_cost_500 (test_shipping.ShippingTests.test_baskets_below_5000_cost_500) ... ok
test_baskets_from_10000_have_free_delivery (test_shipping.ShippingTests.test_baskets_from_10000_have_free_delivery) ... ok
test_baskets_from_5000_through_9999_cost_250 (test_shipping.ShippingTests.test_baskets_from_5000_through_9999_cost_250) ... ok
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

### Та же ошибка границы, упрощённый набор

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`, exit 1

```text
test_baskets_below_5000_cost_500 (test_shipping.ShippingTests.test_baskets_below_5000_cost_500) ... ok
test_baskets_from_10000_have_free_delivery (test_shipping.ShippingTests.test_baskets_from_10000_have_free_delivery) ... 
  test_baskets_from_10000_have_free_delivery (test_shipping.ShippingTests.test_baskets_from_10000_have_free_delivery) (subtotal=10000) ... FAIL
test_baskets_from_5000_through_9999_cost_250 (test_shipping.ShippingTests.test_baskets_from_5000_through_9999_cost_250) ... ok
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... ok

======================================================================
FAIL: test_baskets_from_10000_have_free_delivery (test_shipping.ShippingTests.test_baskets_from_10000_have_free_delivery) (subtotal=10000)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/01_free_boundary/test_shipping.py", line 19, in test_baskets_from_10000_have_free_delivery
    self.assertEqual(delivery_fee(subtotal), 0)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 250 != 0

----------------------------------------------------------------------
Ran 4 tests in 0.000s

FAILED (failures=1)
```

## Завершение

Все шесть обязательных файлов ответов существуют. Создан summary.json с порядком выполнения и итогами. Финальные наборы на рабочих исходниках: 06 — 8 OK; 05 — 6 OK; 04 — 12 OK; 03 — 8 OK; 02 — 9 OK; 01 — 4 метода / 11 примеров OK. После этих запусков изменялись только документы ответов и сводка. Все ручные пробы находятся в разрешённом probes/; их намеренные failures отдельно отмечены и не являются отказами рабочего кода.
