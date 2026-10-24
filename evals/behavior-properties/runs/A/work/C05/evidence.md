# Свидетельства C05

Повторно прочитан task.md после уточнения владельца задания: входы уже валидированы как целые числа. Проверяется только тариф 1..20 и отказ другим целым; валидация типов вне границы. Тесты охватывают каждый допустимый вес, обе стороны перехода 5/6 и границы 1/20, плюс недопустимые -2, 0, 21, 99. Источник ожидаемых значений — task.md. Используются методы unittest, не удаляемые встроенные assert.

## Исходный unittest: обычный режим

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C05`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.036 с.

```text
test_larger_supported_parcels_cost_seven (test_shipping.ShippingTests.test_larger_supported_parcels_cost_seven) ... ok
test_small_parcels_cost_four (test_shipping.ShippingTests.test_small_parcels_cost_four) ... ok
test_unsupported_weights_are_refused (test_shipping.ShippingTests.test_unsupported_weights_are_refused) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

## Исходный unittest: оптимизированный режим

Команда: `python3 -O -m unittest discover -v`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C05`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.134 с.

```text
test_larger_supported_parcels_cost_seven (test_shipping.ShippingTests.test_larger_supported_parcels_cost_seven) ... ok
test_small_parcels_cost_four (test_shipping.ShippingTests.test_small_parcels_cost_four) ... ok
test_unsupported_weights_are_refused (test_shipping.ShippingTests.test_unsupported_weights_are_refused) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

Оба запуска обнаружили и выполнили 3 теста: OK. Всего в каждом запуске проверены 20 допустимых весов и 4 недопустимых целых. Проверки без условных пропусков; assertRaises ловит только ожидаемый ValueError. Проба не требовалась: спорного дискриминатора или зависимости от внутренних деталей не найдено. Исходники не изменялись.

Финальная проверка сохранности: SHA-256 исходных shipping.py, test_shipping.py совпали с сохранёнными до работы. Посторонние исходные файлы не менялись.

