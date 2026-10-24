# C04 — проверки invoice при CI -O

Источник: task.md. Нормальные суммы должны давать amount+3; отрицательные примеры должны отвергаться ValueError. CI запускает точно `python3 -O check_rules.py`. В check_rules.py:5,12 проверки написаны через bare assert, которые оптимизация Python удаляет. Вызовы total и print при этом остаются. Поэтому ошибки вызова могут всё ещё уронить процесс, но неправильный возврат или отсутствие ValueError не проверяются.

## Исходная команда CI

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C04`

Команда: `python3 -O check_rules.py`

Код выхода: 0

```text
invoice checks passed
```

Скрипт завершился кодом 0 и напечатал успех; это не подтверждает выполнение удалённых assert.

## Проба неверного нормального итога при -O

Каталог: `/private/tmp/spruce-C04-ixy09y5n`

Команда: `python3 -O check_rules.py`

Код выхода: 0

```text
invoice checks passed
```

В копии изменена только надбавка с 3 на 30: total(7)=37 вместо 10. Неизменённый скрипт CI остаётся зелёным.

## Контроль той же ошибки без -O

Каталог: `/private/tmp/spruce-C04-ixy09y5n`

Команда: `python3 check_rules.py`

Код выхода: 1

```text
Traceback (most recent call last):
  File "/private/tmp/spruce-C04-ixy09y5n/check_rules.py", line 5, in <module>
    assert result == amount + 3
           ^^^^^^^^^^^^^^^^^^^^
AssertionError
```

Без оптимизации AssertionError на check_rules.py:5 подтверждает, что различие теряется именно из-за удаления assert.

## Проба принятия отрицательной суммы при -O

Каталог: `/private/tmp/spruce-C04-ixy09y5n`

Команда: `python3 -O check_rules.py`

Код выхода: 0

```text
invoice checks passed
```

В копии удалён только отказ для отрицательной суммы: total(-1)=2 без ValueError. Неизменённый скрипт CI остаётся зелёным.

## Контроль отсутствующего отказа без -O

Каталог: `/private/tmp/spruce-C04-ixy09y5n`

Команда: `python3 check_rules.py`

Код выхода: 1

```text
Traceback (most recent call last):
  File "/private/tmp/spruce-C04-ixy09y5n/check_rules.py", line 12, in <module>
    assert rejected
           ^^^^^^^^
AssertionError
```

Без оптимизации AssertionError на check_rules.py:12 ловит тот же дефект.

Оригинальные invoice.py и check_rules.py побайтно сохранены; временный каталог удалён. Это прямые локальные запуски точной CI-команды, а не запуск внешнего CI. Других тестов по условию нет.
