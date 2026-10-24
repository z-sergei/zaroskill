# Свидетельства C04

Контракт: отрицательные суммы отклоняются; обычная сумма получает amount+3. Реальный CI запускает именно python3 -O check_rules.py. Строки 5 и 12 используют встроенный assert, удаляемый при -O. Вызовы total продолжают выполняться, но их правильность не проверяется.

## Исходный точный CI-запуск

Команда: `python3 -O check_rules.py`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C04`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.046 с.

```text
invoice checks passed
```

Проба в отдельной копии: total заменён функцией, всегда возвращающей 999. Теперь total(7) должен быть 10, но равен 999; total(-1) должен поднять ValueError, но возвращает 999. Исходный check_rules.py не изменён.

## Проба: обе гарантии нарушены, точный CI-запуск

Команда: `python3 -O check_rules.py`

Каталог: `/private/tmp/cedar-task-probes/C04-disabled-assertions`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.046 с.

```text
invoice checks passed
```

## Контроль пробы без оптимизации

Команда: `python3 check_rules.py`

Каталог: `/private/tmp/cedar-task-probes/C04-disabled-assertions`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 1; 0.029 с.

```text
Traceback (most recent call last):
  File "/private/tmp/cedar-task-probes/C04-disabled-assertions/check_rules.py", line 5, in <module>
    assert result == amount + 3
           ^^^^^^^^^^^^^^^^^^^^
AssertionError
```

## Наблюдаемые неверные результаты неисправной копии

Команда: `python3 -c 'from invoice import total; print("total(7):", total(7), "expected: 10"); print("total(-1):", total(-1), "expected: ValueError")'`

Каталог: `/private/tmp/cedar-task-probes/C04-disabled-assertions`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.018 с.

```text
total(7): 999 expected: 10
total(-1): 999 expected: ValueError
```

Финальная проверка сохранности: SHA-256 исходных check_rules.py, invoice.py совпали с сохранёнными до работы. Посторонние исходные файлы не менялись.

