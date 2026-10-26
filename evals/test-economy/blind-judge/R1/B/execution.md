# Фактическое выполнение

Все команды выполняются внутри указанного случая или разрешённой копии в `probes/`.
`PYTHONDONTWRITEBYTECODE=1` исключает создание файлов кэша в исходных случаях.

## 01_shipping_bands

1. `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -v` — exit 127: `python` отсутствует.
2. `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` — exit 0, `Ran 13 tests`, `OK` до изменения тестов.
3. Первая попытка заменить тесты через apply_patch отклонена из-за двух операций над одним путём; изменений не сделано. Затем записан новый `test_shipping.py`: четыре группы правил, одиннадцать явных примеров. Production не изменялся.

### После упрощения

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/01_shipping_bands`; exit 0.

```text
test_baskets_below_5000_cost_500_to_deliver (test_shipping.ShippingTests.test_baskets_below_5000_cost_500_to_deliver) ... ok
test_baskets_from_10000_have_free_delivery (test_shipping.ShippingTests.test_baskets_from_10000_have_free_delivery) ... ok
test_baskets_from_5000_to_9999_cost_250_to_deliver (test_shipping.ShippingTests.test_baskets_from_5000_to_9999_cost_250_to_deliver) ... ok
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

### Fault probe: порог 5000 заменён с >= на > только в копии

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/01_shipping_bands`; exit 1.

```text
test_baskets_below_5000_cost_500_to_deliver (test_shipping.ShippingTests.test_baskets_below_5000_cost_500_to_deliver) ... ok
test_baskets_from_10000_have_free_delivery (test_shipping.ShippingTests.test_baskets_from_10000_have_free_delivery) ... ok
test_baskets_from_5000_to_9999_cost_250_to_deliver (test_shipping.ShippingTests.test_baskets_from_5000_to_9999_cost_250_to_deliver) ... 
  test_baskets_from_5000_to_9999_cost_250_to_deliver (test_shipping.ShippingTests.test_baskets_from_5000_to_9999_cost_250_to_deliver) (subtotal=5000) ... FAIL
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... ok

======================================================================
FAIL: test_baskets_from_5000_to_9999_cost_250_to_deliver (test_shipping.ShippingTests.test_baskets_from_5000_to_9999_cost_250_to_deliver) (subtotal=5000)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/01_shipping_bands/test_shipping.py", line 20, in test_baskets_from_5000_to_9999_cost_250_to_deliver
    self.assertEqual(delivery_fee(subtotal), 250)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 500 != 250

----------------------------------------------------------------------
Ran 4 tests in 0.000s

FAILED (failures=1)
```

### Восстановленная копия после probe

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/01_shipping_bands`; exit 0.

```text
test_baskets_below_5000_cost_500_to_deliver (test_shipping.ShippingTests.test_baskets_below_5000_cost_500_to_deliver) ... ok
test_baskets_from_10000_have_free_delivery (test_shipping.ShippingTests.test_baskets_from_10000_have_free_delivery) ... ok
test_baskets_from_5000_to_9999_cost_250_to_deliver (test_shipping.ShippingTests.test_baskets_from_5000_to_9999_cost_250_to_deliver) ... ok
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

### Финальная проверка исходного production

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/01_shipping_bands`; exit 0.

```text
test_baskets_below_5000_cost_500_to_deliver (test_shipping.ShippingTests.test_baskets_below_5000_cost_500_to_deliver) ... ok
test_baskets_from_10000_have_free_delivery (test_shipping.ShippingTests.test_baskets_from_10000_have_free_delivery) ... ok
test_baskets_from_5000_to_9999_cost_250_to_deliver (test_shipping.ShippingTests.test_baskets_from_5000_to_9999_cost_250_to_deliver) ... ok
test_negative_subtotals_are_rejected (test_shipping.ShippingTests.test_negative_subtotals_are_rejected) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

Production shipping.py не изменён; SHA256: bc6cd30e8fc648b5509794e2f71eadfa41d8cf43ba5da70e7385c6174d078c4f.

## 02_display_name

Runner uses python3 because python is unavailable.

### Исходные тесты

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/02_display_name`; exit 0.

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

### Fault probe: только ASCII whitespace; исходные тесты

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/02_display_name`; exit 0.

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

### ASCII-only strip probe с добавленными тестами

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/02_display_name`; exit 1.

```text
test_combining_codepoints_count_towards_the_length_limit (test_names.DisplayNameTests.test_combining_codepoints_count_towards_the_length_limit) ... ok
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_unicode_edges_are_trimmed_without_changing_inner_characters (test_names.DisplayNameTests.test_unicode_edges_are_trimmed_without_changing_inner_characters) ... FAIL
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

======================================================================
FAIL: test_unicode_edges_are_trimmed_without_changing_inner_characters (test_names.DisplayNameTests.test_unicode_edges_are_trimmed_without_changing_inner_characters)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/02_display_name/test_names.py", line 33, in test_unicode_edges_are_trimmed_without_changing_inner_characters
    self.assertEqual(clean_display_name("\u2003" + name + "\u00a0"), name)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: '\u2003A\tB\nC\xa0é!\xa0' != 'A\tB\nC\xa0é!'
-  A	B
? -
+ A	B
- C é! 
?      -
+ C é!


----------------------------------------------------------------------
Ran 9 tests in 0.000s

FAILED (failures=1)
```

### Восстановленная копия после probe

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/02_display_name`; exit 0.

```text
test_combining_codepoints_count_towards_the_length_limit (test_names.DisplayNameTests.test_combining_codepoints_count_towards_the_length_limit) ... ok
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_unicode_edges_are_trimmed_without_changing_inner_characters (test_names.DisplayNameTests.test_unicode_edges_are_trimmed_without_changing_inner_characters) ... ok
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.000s

OK
```

### Финальный набор на неизменённом production

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/02_display_name`; exit 0.

```text
test_combining_codepoints_count_towards_the_length_limit (test_names.DisplayNameTests.test_combining_codepoints_count_towards_the_length_limit) ... ok
test_empty_name_is_invalid (test_names.DisplayNameTests.test_empty_name_is_invalid) ... ok
test_inner_spacing_and_mixed_case_are_preserved (test_names.DisplayNameTests.test_inner_spacing_and_mixed_case_are_preserved) ... ok
test_length_counts_characters (test_names.DisplayNameTests.test_length_counts_characters) ... ok
test_longest_name_is_valid_after_trimming (test_names.DisplayNameTests.test_longest_name_is_valid_after_trimming) ... ok
test_one_character_too_long (test_names.DisplayNameTests.test_one_character_too_long) ... ok
test_shortest_name_preserves_case (test_names.DisplayNameTests.test_shortest_name_preserves_case) ... ok
test_unicode_edges_are_trimmed_without_changing_inner_characters (test_names.DisplayNameTests.test_unicode_edges_are_trimmed_without_changing_inner_characters) ... ok
test_whitespace_only_is_invalid (test_names.DisplayNameTests.test_whitespace_only_is_invalid) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.000s

OK
```

Production names.py не изменён; SHA256: 6d0c6298b3d946930a9ccf059a1794119d4c1fd7a7bae80f5963f7f56e5cc19a.

## 03_capacity_boundaries

### Исходный набор

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/03_capacity_boundaries`; exit 0.

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

### Fault probe: reserve возвращает limit при успехе; исходные тесты

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/03_capacity_boundaries`; exit 0.

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

### Возврат limit с дополненным набором

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/03_capacity_boundaries`; exit 1.

```text
test_request_maps_over_capacity_without_mutating_input (test_capacity.RequestTests.test_request_maps_over_capacity_without_mutating_input) ... ok
test_request_reports_exact_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_exact_capacity_without_mutating_input) ... ok
test_request_reports_new_occupancy_below_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_new_occupancy_below_capacity_without_mutating_input) ... FAIL
test_request_reports_success_for_zero_at_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_success_for_zero_at_capacity_without_mutating_input) ... ok
test_domain_allows_exact_capacity (test_capacity.ReservationTests.test_domain_allows_exact_capacity) ... ok
test_domain_allows_zero_at_capacity (test_capacity.ReservationTests.test_domain_allows_zero_at_capacity) ... ok
test_domain_rejects_over_capacity (test_capacity.ReservationTests.test_domain_rejects_over_capacity) ... ok
test_domain_returns_new_occupancy_below_capacity (test_capacity.ReservationTests.test_domain_returns_new_occupancy_below_capacity) ... FAIL

======================================================================
FAIL: test_request_reports_new_occupancy_below_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_new_occupancy_below_capacity_without_mutating_input)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/03_capacity_boundaries/test_capacity.py", line 24, in test_request_reports_new_occupancy_below_capacity_without_mutating_input
    self.assertEqual(handle_request(payload), {"status": "ok", "used": 5})
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'status': 'ok', 'used': 10} != {'status': 'ok', 'used': 5}
- {'status': 'ok', 'used': 10}
?                          ^^

+ {'status': 'ok', 'used': 5}
?                          ^


======================================================================
FAIL: test_domain_returns_new_occupancy_below_capacity (test_capacity.ReservationTests.test_domain_returns_new_occupancy_below_capacity)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/03_capacity_boundaries/test_capacity.py", line 7, in test_domain_returns_new_occupancy_below_capacity
    self.assertEqual(reserve(2, 3, 10), 5)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 10 != 5

----------------------------------------------------------------------
Ran 8 tests in 0.001s

FAILED (failures=2)
```

### Восстановленная копия после probe

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/03_capacity_boundaries`; exit 0.

```text
test_request_maps_over_capacity_without_mutating_input (test_capacity.RequestTests.test_request_maps_over_capacity_without_mutating_input) ... ok
test_request_reports_exact_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_exact_capacity_without_mutating_input) ... ok
test_request_reports_new_occupancy_below_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_new_occupancy_below_capacity_without_mutating_input) ... ok
test_request_reports_success_for_zero_at_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_success_for_zero_at_capacity_without_mutating_input) ... ok
test_domain_allows_exact_capacity (test_capacity.ReservationTests.test_domain_allows_exact_capacity) ... ok
test_domain_allows_zero_at_capacity (test_capacity.ReservationTests.test_domain_allows_zero_at_capacity) ... ok
test_domain_rejects_over_capacity (test_capacity.ReservationTests.test_domain_rejects_over_capacity) ... ok
test_domain_returns_new_occupancy_below_capacity (test_capacity.ReservationTests.test_domain_returns_new_occupancy_below_capacity) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

### Финальный набор на исходном production

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/03_capacity_boundaries`; exit 0.

```text
test_request_maps_over_capacity_without_mutating_input (test_capacity.RequestTests.test_request_maps_over_capacity_without_mutating_input) ... ok
test_request_reports_exact_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_exact_capacity_without_mutating_input) ... ok
test_request_reports_new_occupancy_below_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_new_occupancy_below_capacity_without_mutating_input) ... ok
test_request_reports_success_for_zero_at_capacity_without_mutating_input (test_capacity.RequestTests.test_request_reports_success_for_zero_at_capacity_without_mutating_input) ... ok
test_domain_allows_exact_capacity (test_capacity.ReservationTests.test_domain_allows_exact_capacity) ... ok
test_domain_allows_zero_at_capacity (test_capacity.ReservationTests.test_domain_allows_zero_at_capacity) ... ok
test_domain_rejects_over_capacity (test_capacity.ReservationTests.test_domain_rejects_over_capacity) ... ok
test_domain_returns_new_occupancy_below_capacity (test_capacity.ReservationTests.test_domain_returns_new_occupancy_below_capacity) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

Production capacity.py не изменён; SHA256: d1864fac8b217218471e1f41b7b1a851fc693b9d38822a94ec862636de35539c.

## 04_discount_cap — наблюдаемый TDD

### Baseline до изменений

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`; cwd: `work/cases/04_discount_cap`; exit 0.

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

### API ещё отсутствует — setup/API failure, не засчитывается как behavioral red

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total`; cwd: `work/cases/04_discount_cap`; exit 1.

```text
test_cap_limits_the_discount_not_the_total (test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total) ... ERROR

======================================================================
ERROR: test_cap_limits_the_discount_not_the_total (test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 29, in test_cap_limits_the_discount_not_the_total
    discounted_total(1000, 15, max_discount_cents=100), 900
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: discounted_total() got an unexpected keyword argument 'max_discount_cents'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

Добавлена только keyword-only декларация max_discount_cents=None; расчёт пока игнорирует лимит.

### RED 1: inert signature, assertion достигается до реализации лимита

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total`; cwd: `work/cases/04_discount_cap`; exit 1.

```text
test_cap_limits_the_discount_not_the_total (test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total) ... FAIL

======================================================================
FAIL: test_cap_limits_the_discount_not_the_total (test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 28, in test_cap_limits_the_discount_not_the_total
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        discounted_total(1000, 15, max_discount_cents=100), 900
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: 850 != 900

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

После RED 1 реализовано ограничение вычисленной скидки min(discount, max_discount_cents), когда лимит не None.

### GREEN 1: тот же новый тест

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total`; cwd: `work/cases/04_discount_cap`; exit 0.

```text
test_cap_limits_the_discount_not_the_total (test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

### GREEN 1: все соседние тесты

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`; cwd: `work/cases/04_discount_cap`; exit 0.

```text
test_cap_limits_the_discount_not_the_total (test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total) ... ok
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

### RED 2: отрицательный лимит ещё не отклоняется

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero`; cwd: `work/cases/04_discount_cap`; exit 1.

```text
test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) ... 
  test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) (subtotal=1000, percent=15) ... FAIL
  test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) (subtotal=1000, percent=0) ... FAIL
  test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) (subtotal=0, percent=100) ... FAIL
  test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) (subtotal=1, percent=1) ... FAIL

======================================================================
FAIL: test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) (subtotal=1000, percent=15)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 35, in test_negative_cap_is_rejected_even_when_discount_is_zero
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) (subtotal=1000, percent=0)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 35, in test_negative_cap_is_rejected_even_when_discount_is_zero
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) (subtotal=0, percent=100)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 35, in test_negative_cap_is_rejected_even_when_discount_is_zero
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) (subtotal=1, percent=1)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/work/cases/04_discount_cap/test_discounts.py", line 35, in test_negative_cap_is_rejected_even_when_discount_is_zero
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=4)
```

После RED 2 добавлена проверка отрицательного лимита до вычисления скидки. Исходные тесты и ожидания не менялись.

### GREEN 2: тот же validation test

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero`; cwd: `work/cases/04_discount_cap`; exit 0.

```text
test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

### GREEN 2: общий набор

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`; cwd: `work/cases/04_discount_cap`; exit 0.

```text
test_cap_limits_the_discount_not_the_total (test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total) ... ok
test_discount_rounds_down_to_whole_cents (test_discounts.DiscountTests.test_discount_rounds_down_to_whole_cents) ... ok
test_full_discount (test_discounts.DiscountTests.test_full_discount) ... ok
test_invalid_percent (test_discounts.DiscountTests.test_invalid_percent) ... ok
test_invalid_subtotal (test_discounts.DiscountTests.test_invalid_subtotal) ... ok
test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) ... ok
test_no_discount (test_discounts.DiscountTests.test_no_discount) ... ok
test_percentage_discount (test_discounts.DiscountTests.test_percentage_discount) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

### Финальная проверка всех требований

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`; cwd: `work/cases/04_discount_cap`; exit 0.

```text
test_cap_at_or_above_the_discount_preserves_the_calculation (test_discounts.DiscountTests.test_cap_at_or_above_the_discount_preserves_the_calculation) ... ok
test_cap_limits_the_discount_not_the_total (test_discounts.DiscountTests.test_cap_limits_the_discount_not_the_total) ... ok
test_cap_must_be_passed_by_keyword (test_discounts.DiscountTests.test_cap_must_be_passed_by_keyword) ... ok
test_discount_rounds_down_to_whole_cents (test_discounts.DiscountTests.test_discount_rounds_down_to_whole_cents) ... ok
test_full_discount (test_discounts.DiscountTests.test_full_discount) ... ok
test_invalid_percent (test_discounts.DiscountTests.test_invalid_percent) ... ok
test_invalid_subtotal (test_discounts.DiscountTests.test_invalid_subtotal) ... ok
test_negative_cap_is_rejected_even_when_discount_is_zero (test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero) ... ok
test_no_discount (test_discounts.DiscountTests.test_no_discount) ... ok
test_none_cap_preserves_the_uncapped_calculation (test_discounts.DiscountTests.test_none_cap_preserves_the_uncapped_calculation) ... ok
test_percentage_discount (test_discounts.DiscountTests.test_percentage_discount) ... ok
test_zero_cap_leaves_the_subtotal_unchanged (test_discounts.DiscountTests.test_zero_cap_leaves_the_subtotal_unchanged) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
```

Нулевой/равный/больший лимит, явный None и keyword-only прошли с первой попытки после двух slices: это уже существующее поведение, не дополнительные red/green циклы. Рефакторинг не потребовался.

## 05_mutation_report

Supplied mutation-report.json is synthetic, not an execution result. The checks below are four direct, local snippet probes using the unchanged tests; no mutation tool or external campaign was run.

### Исходный контроль

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/05_mutation_report`; exit 0.

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

### Контроль в одноразовой копии

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/05_mutation_report`; exit 0.

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

Probe M1: `return paid_cents // 4` → `return (paid_cents - paid_cents % 4) // 4`. Tests unchanged.

### M1 — отдельный локальный probe

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/05_mutation_report`; exit 0.

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

Probe M2: `if hours_before >= 48:` → `if hours_before >= 47:`. Tests unchanged.

### M2 — отдельный локальный probe

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/05_mutation_report`; exit 0.

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

M2 direct witness (47, 100): original=25, altered=0; required=25. Original six tests stayed green.

Probe M3: `return paid_cents // 2` → `return (paid_cents + 1) // 2`. Tests unchanged.

### M3 — отдельный локальный probe

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/05_mutation_report`; exit 1.

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
  File "<run>/probes/05_mutation_report/test_cancellation.py", line 19, in test_half_fee_rounds_down
    self.assertEqual(cancellation_fee(12, 101), 50)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 51 != 50

----------------------------------------------------------------------
Ran 6 tests in 0.000s

FAILED (failures=1)
```

Probe M4: `if hours_before >= 24:` → `if hours_before >= 25:`. Tests unchanged.

### M4 — отдельный локальный probe

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/05_mutation_report`; exit 1.

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
  File "<run>/probes/05_mutation_report/test_cancellation.py", line 10, in test_at_day_boundary
    self.assertEqual(cancellation_fee(24, 100), 25)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 50 != 25

----------------------------------------------------------------------
Ran 6 tests in 0.000s

FAILED (failures=1)
```

### Восстановленная копия после всех probes

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/05_mutation_report`; exit 0.

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

### Финальный исходный контроль

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/05_mutation_report`; exit 0.

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

cancellation.py unchanged; SHA256 77631e0fee7dff80278c365d7a3cf53b61bd7eb6bbb63b424f0cf216db68f507.

test_cancellation.py unchanged; SHA256 ad84b4151395b65abf88b8bc6e30ba48050811de72f7ca36e6dd79d40804180f.

mutation-report.json unchanged; SHA256 af68e0d0d2c52e67da2cce9a6bb1afa16a5a93ae3276e755cf024154ddbe6ff7.

## 06_upload_workflow

Required properties from task.md: only the waiting active attempt may complete; rejected events preserve public state and subsequent ability of that active attempt to complete; cancellation and completion are terminal for that attempt, with supported restart and increasing integer identities. No I/O, concurrent execution, deadline or eventual callback promise is claimed.

### Исходные три сценария

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/06_upload_workflow`; exit 0.

```text
test_cancel_active_upload (test_upload.UploadTests.test_cancel_active_upload) ... ok
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

### Контроль одноразовой копии

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/06_upload_workflow`; exit 0.

```text
test_cancel_active_upload (test_upload.UploadTests.test_cancel_active_upload) ... ok
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

### Fault probe: допускаются старые id, исходные три сценария

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/06_upload_workflow`; exit 0.

```text
test_cancel_active_upload (test_upload.UploadTests.test_cancel_active_upload) ... ok
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

### Старые id допускаются: новый набор

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/06_upload_workflow`; exit 1.

```text
test_cancelled_upload_rejects_late_completion_and_repeated_cancel (test_upload.UploadTests.test_cancelled_upload_rejects_late_completion_and_repeated_cancel) ... ok
test_completed_upload_preserves_result_after_duplicate_and_cancel (test_upload.UploadTests.test_completed_upload_preserves_result_after_duplicate_and_cancel) ... ok
test_idle_session_ignores_completion_and_cancel (test_upload.UploadTests.test_idle_session_ignores_completion_and_cancel) ... ok
test_rejected_begin_keeps_the_current_attempt_finishable (test_upload.UploadTests.test_rejected_begin_keeps_the_current_attempt_finishable) ... ok
test_restart_after_cancel_ignores_old_result_before_and_after_success (test_upload.UploadTests.test_restart_after_cancel_ignores_old_result_before_and_after_success) ... FAIL
test_restart_after_success_clears_result_and_rejects_old_attempt (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_attempt) ... FAIL
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... ok

======================================================================
FAIL: test_restart_after_cancel_ignores_old_result_before_and_after_success (test_upload.UploadTests.test_restart_after_cancel_ignores_old_result_before_and_after_success)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_upload_workflow/test_upload.py", line 89, in test_restart_after_cancel_ignores_old_result_before_and_after_success
    self.assertIs(session.complete(first, "cancelled-before.csv"), False)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not False

======================================================================
FAIL: test_restart_after_success_clears_result_and_rejects_old_attempt (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_attempt)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_upload_workflow/test_upload.py", line 75, in test_restart_after_success_clears_result_and_rejects_old_attempt
    self.assertIs(session.complete(first, "obsolete.csv"), False)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not False

----------------------------------------------------------------------
Ran 8 tests in 0.000s

FAILED (failures=2)
```

### Новый набор на восстановленной копии

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/06_upload_workflow`; exit 0.

```text
test_cancelled_upload_rejects_late_completion_and_repeated_cancel (test_upload.UploadTests.test_cancelled_upload_rejects_late_completion_and_repeated_cancel) ... ok
test_completed_upload_preserves_result_after_duplicate_and_cancel (test_upload.UploadTests.test_completed_upload_preserves_result_after_duplicate_and_cancel) ... ok
test_idle_session_ignores_completion_and_cancel (test_upload.UploadTests.test_idle_session_ignores_completion_and_cancel) ... ok
test_rejected_begin_keeps_the_current_attempt_finishable (test_upload.UploadTests.test_rejected_begin_keeps_the_current_attempt_finishable) ... ok
test_restart_after_cancel_ignores_old_result_before_and_after_success (test_upload.UploadTests.test_restart_after_cancel_ignores_old_result_before_and_after_success) ... ok
test_restart_after_success_clears_result_and_rejects_old_attempt (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_attempt) ... ok
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

### Fault probe: отклонённый begin меняет активный id до исключения

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/06_upload_workflow`; exit 1.

```text
test_cancelled_upload_rejects_late_completion_and_repeated_cancel (test_upload.UploadTests.test_cancelled_upload_rejects_late_completion_and_repeated_cancel) ... ok
test_completed_upload_preserves_result_after_duplicate_and_cancel (test_upload.UploadTests.test_completed_upload_preserves_result_after_duplicate_and_cancel) ... ok
test_idle_session_ignores_completion_and_cancel (test_upload.UploadTests.test_idle_session_ignores_completion_and_cancel) ... ok
test_rejected_begin_keeps_the_current_attempt_finishable (test_upload.UploadTests.test_rejected_begin_keeps_the_current_attempt_finishable) ... FAIL
test_restart_after_cancel_ignores_old_result_before_and_after_success (test_upload.UploadTests.test_restart_after_cancel_ignores_old_result_before_and_after_success) ... ok
test_restart_after_success_clears_result_and_rejects_old_attempt (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_attempt) ... ok
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... ok

======================================================================
FAIL: test_rejected_begin_keeps_the_current_attempt_finishable (test_upload.UploadTests.test_rejected_begin_keeps_the_current_attempt_finishable)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<run>/probes/06_upload_workflow/test_upload.py", line 53, in test_rejected_begin_keeps_the_current_attempt_finishable
    self.assertIs(session.complete(attempt, "original.csv"), True)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not True

----------------------------------------------------------------------
Ran 8 tests in 0.000s

FAILED (failures=1)
```

### Contract-preserving probe: ids растут на два, без требований подряд

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/06_upload_workflow`; exit 0.

```text
test_cancelled_upload_rejects_late_completion_and_repeated_cancel (test_upload.UploadTests.test_cancelled_upload_rejects_late_completion_and_repeated_cancel) ... ok
test_completed_upload_preserves_result_after_duplicate_and_cancel (test_upload.UploadTests.test_completed_upload_preserves_result_after_duplicate_and_cancel) ... ok
test_idle_session_ignores_completion_and_cancel (test_upload.UploadTests.test_idle_session_ignores_completion_and_cancel) ... ok
test_rejected_begin_keeps_the_current_attempt_finishable (test_upload.UploadTests.test_rejected_begin_keeps_the_current_attempt_finishable) ... ok
test_restart_after_cancel_ignores_old_result_before_and_after_success (test_upload.UploadTests.test_restart_after_cancel_ignores_old_result_before_and_after_success) ... ok
test_restart_after_success_clears_result_and_rejects_old_attempt (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_attempt) ... ok
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

### Финальная восстановленная копия

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `probes/06_upload_workflow`; exit 0.

```text
test_cancelled_upload_rejects_late_completion_and_repeated_cancel (test_upload.UploadTests.test_cancelled_upload_rejects_late_completion_and_repeated_cancel) ... ok
test_completed_upload_preserves_result_after_duplicate_and_cancel (test_upload.UploadTests.test_completed_upload_preserves_result_after_duplicate_and_cancel) ... ok
test_idle_session_ignores_completion_and_cancel (test_upload.UploadTests.test_idle_session_ignores_completion_and_cancel) ... ok
test_rejected_begin_keeps_the_current_attempt_finishable (test_upload.UploadTests.test_rejected_begin_keeps_the_current_attempt_finishable) ... ok
test_restart_after_cancel_ignores_old_result_before_and_after_success (test_upload.UploadTests.test_restart_after_cancel_ignores_old_result_before_and_after_success) ... ok
test_restart_after_success_clears_result_and_rejects_old_attempt (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_attempt) ... ok
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

### Финальный исходный production

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`

Cwd: `work/cases/06_upload_workflow`; exit 0.

```text
test_cancelled_upload_rejects_late_completion_and_repeated_cancel (test_upload.UploadTests.test_cancelled_upload_rejects_late_completion_and_repeated_cancel) ... ok
test_completed_upload_preserves_result_after_duplicate_and_cancel (test_upload.UploadTests.test_completed_upload_preserves_result_after_duplicate_and_cancel) ... ok
test_idle_session_ignores_completion_and_cancel (test_upload.UploadTests.test_idle_session_ignores_completion_and_cancel) ... ok
test_rejected_begin_keeps_the_current_attempt_finishable (test_upload.UploadTests.test_rejected_begin_keeps_the_current_attempt_finishable) ... ok
test_restart_after_cancel_ignores_old_result_before_and_after_success (test_upload.UploadTests.test_restart_after_cancel_ignores_old_result_before_and_after_success) ... ok
test_restart_after_success_clears_result_and_rejects_old_attempt (test_upload.UploadTests.test_restart_after_success_clears_result_and_rejects_old_attempt) ... ok
test_successful_upload (test_upload.UploadTests.test_successful_upload) ... ok
test_unknown_completion_preserves_current_attempt (test_upload.UploadTests.test_unknown_completion_preserves_current_attempt) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```

Production upload.py unchanged; SHA256: 2eb255004f3ff1076292c96bc960c8abcee553e989f3605de4e8bb101c77b725.

## Завершение

Все шесть случаев выполнены по order.json; проверено наличие каждого файла результата, создан summary.json. Последние фактические результаты случаев: 4, 9, 8, 12, 6, 8 тестовых методов, все OK. Это 47 методов суммарно с дополнительными subTest-примерами; после финальных проверок исполняемый код не менялся. Производственный код изменён только в разрешённом discounts.py.
