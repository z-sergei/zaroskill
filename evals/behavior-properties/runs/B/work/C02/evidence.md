# C02 — граница и проверки

Источник: task.md. Реальный SearchApp + записывающий double внешнего gateway. Проверяем вызов start(token, query) один раз на search, возвращённый token как непрозрачную идентичность, сохранение видимого ответа при новой заявке и запрет применения устаревшего ответа. Завершения подаются вручную через receive; сетевой адаптер и доставка ответа за границей.

## Исходная выборка

Команда: `python3 -B -m unittest discover -v`

Код выхода: 5

```text

----------------------------------------------------------------------
Ran 0 tests in 0.000s

NO TESTS RAN
```

0 тестов — исходное отсутствие проверок. Производственный код не меняется.

## Добавленные сценарии

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_each_search_starts_one_request_with_its_returned_token (test_search.SearchAppTests.test_each_search_starts_one_request_with_its_returned_token) ... ok
test_new_search_keeps_visible_results_until_its_answer_arrives (test_search.SearchAppTests.test_new_search_keeps_visible_results_until_its_answer_arrives) ... ok
test_older_answer_cannot_change_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_results_in_either_completion_order) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

3 теста прошли на исходном search.py. Это подтверждение существующего поведения, не исторический цикл red/green. Два порядка ответов проверяют промежуточное состояние сразу после каждого callback.

## Проба чувствительности: принятие устаревшего ответа

Каталог: `/private/tmp/spruce-C02-d6oh5la_`

Команда: `python3 -B -m unittest discover -v`

Код выхода: 1

```text
test_each_search_starts_one_request_with_its_returned_token (test_search.SearchAppTests.test_each_search_starts_one_request_with_its_returned_token) ... ok
test_new_search_keeps_visible_results_until_its_answer_arrives (test_search.SearchAppTests.test_new_search_keeps_visible_results_until_its_answer_arrives) ... ok
test_older_answer_cannot_change_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_results_in_either_completion_order) ... 
  test_older_answer_cannot_change_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_results_in_either_completion_order) (order='older first') ... FAIL
  test_older_answer_cannot_change_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_results_in_either_completion_order) (order='current first') ... FAIL

======================================================================
FAIL: test_older_answer_cannot_change_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_results_in_either_completion_order) (order='older first')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/spruce-C02-d6oh5la_/test_search.py", line 65, in test_older_answer_cannot_change_results_in_either_completion_order
    self.assertEqual(("saved result",), app.visible)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Tuples differ: ('saved result',) != ('obsolete result',)

First differing element 0:
'saved result'
'obsolete result'

- ('saved result',)
?    ^^ ^

+ ('obsolete result',)
?   ++ ^^ ^^


======================================================================
FAIL: test_older_answer_cannot_change_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_results_in_either_completion_order) (order='current first')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/spruce-C02-d6oh5la_/test_search.py", line 72, in test_older_answer_cannot_change_results_in_either_completion_order
    self.assertEqual(("current result",), app.visible)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Tuples differ: ('current result',) != ('obsolete result',)

First differing element 0:
'current result'
'obsolete result'

- ('current result',)
+ ('obsolete result',)

----------------------------------------------------------------------
Ran 3 tests in 0.001s

FAILED (failures=2)
```

Только в временной копии удалён guard `if token == self._active`; receive безусловно присваивает visible. Оба допустимых порядка ответов должны отвергнуть такую ошибку.

## Проба устойчивости к непрозрачным token

Каталог: `/private/tmp/spruce-C02-d6oh5la_`

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_each_search_starts_one_request_with_its_returned_token (test_search.SearchAppTests.test_each_search_starts_one_request_with_its_returned_token) ... ok
test_new_search_keeps_visible_results_until_its_answer_arrives (test_search.SearchAppTests.test_new_search_keeps_visible_results_until_its_answer_arrives) ... ok
test_older_answer_cannot_change_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_results_in_either_completion_order) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

В отдельном состоянии временной копии счётчик заменён на object() на каждую заявку; начальное _active=None. Вызовы gateway, корреляция и consumer API сохранены. Числа token не являются контрактом; неизменённые тесты проходят.

## Финальная проверка исходного production

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C02`

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_each_search_starts_one_request_with_its_returned_token (test_search.SearchAppTests.test_each_search_starts_one_request_with_its_returned_token) ... ok
test_new_search_keeps_visible_results_until_its_answer_arrives (test_search.SearchAppTests.test_new_search_keeps_visible_results_until_its_answer_arrives) ... ok
test_older_answer_cannot_change_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_results_in_either_completion_order) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

Исходный search.py побайтно совпадает с сохранённым до проб. Временный каталог удалён; 3 теста проходят.
