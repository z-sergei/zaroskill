# C05 — проверка покрытия тарифа

Источник: task.md. В целочисленном домене все 1..5 имеют ожидаемую стоимость 4, все 6..20 — 7; вне диапазона — ValueError. test_shipping.py:5-13 перебирает все 20 поддерживаемых целых весов с независимыми литеральными ожиданиями. Строки 15-19 проверяют ближайшие недопустимые границы 0/21 и дополнительные представители -2/99. Обращения только к реальной fee; I/O нет.

## Обычный unittest

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C05`

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_larger_supported_parcels_cost_seven (test_shipping.ShippingTests.test_larger_supported_parcels_cost_seven) ... ok
test_small_parcels_cost_four (test_shipping.ShippingTests.test_small_parcels_cost_four) ... ok
test_unsupported_weights_are_refused (test_shipping.ShippingTests.test_unsupported_weights_are_refused) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

Обнаружены и выполнены 3 метода тестов, без пропусков. Проверки unittest сохраняются при -O.

## unittest с оптимизацией

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C05`

Команда: `python3 -O -B -m unittest discover -v`

Код выхода: 0

```text
test_larger_supported_parcels_cost_seven (test_shipping.ShippingTests.test_larger_supported_parcels_cost_seven) ... ok
test_small_parcels_cost_four (test_shipping.ShippingTests.test_small_parcels_cost_four) ... ok
test_unsupported_weights_are_refused (test_shipping.ShippingTests.test_unsupported_weights_are_refused) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

Обнаружены и выполнены 3 метода тестов, без пропусков. Проверки unittest сохраняются при -O.

## Проба границы тарифа при -O

Каталог: `/private/tmp/spruce-C05-diymjapc`

Команда: `python3 -O -B -m unittest discover -v`

Код выхода: 1

```text
test_larger_supported_parcels_cost_seven (test_shipping.ShippingTests.test_larger_supported_parcels_cost_seven) ... ok
test_small_parcels_cost_four (test_shipping.ShippingTests.test_small_parcels_cost_four) ... 
  test_small_parcels_cost_four (test_shipping.ShippingTests.test_small_parcels_cost_four) (weight=5) ... FAIL
test_unsupported_weights_are_refused (test_shipping.ShippingTests.test_unsupported_weights_are_refused) ... ok

======================================================================
FAIL: test_small_parcels_cost_four (test_shipping.ShippingTests.test_small_parcels_cost_four) (weight=5)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/spruce-C05-diymjapc/test_shipping.py", line 8, in test_small_parcels_cost_four
    self.assertEqual(4, fee(weight))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
AssertionError: 4 != 7

----------------------------------------------------------------------
Ran 3 tests in 0.000s

FAILED (failures=1)
```

Только в копии <=5 заменено на <5: вес 5 ошибочно стоит 7. Исходные тесты обнаруживают дефект на subTest(weight=5), expected 4 != 7.

Исходные source/tests побайтно сохранены, временная копия удалена. Один целевой дефект проверяет чувствительность границы, не является полным mutation testing. Перечисление всех допустимых целых весов не доказывает все возможные неправильные реализации или все недопустимые значения.

## Уточнение входного домена

После сообщения о согласованном уточнении повторно прочитан work/C05/task.md: входы в этой границе уже валидированы как целые; прочие целые веса отвергаются. Уточнение не меняло shipping.py или test_shipping.py и не меняет результаты выполненных запусков. Проверка типов не требуется.
