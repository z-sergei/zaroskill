# Свидетельства C02

Контракт из task.md: каждый search начинает ровно один запрос и возвращает его непрозрачный token; только активный ответ меняет visible; до него прошлые результаты сохраняются. Граница: реальный SearchApp и записывающий gateway на внешнем порте. Исходных тестов нет; production не меняется. Тесты не утверждают числовой порядок, тип или значение token.

## Новые тесты против неизменённого SearchApp

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C02`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.033 с.

```text
test_new_search_keeps_visible_results_until_its_empty_answer (test_search.SearchAppTests.test_new_search_keeps_visible_results_until_its_empty_answer) ... ok
test_older_answer_cannot_change_visible_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_visible_results_in_either_completion_order) ... ok
test_search_starts_one_request_and_active_answer_becomes_visible (test_search.SearchAppTests.test_search_starts_one_request_and_active_answer_becomes_visible) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

Проба чувствительности в отдельной копии: единственное условие принятия ответа заменено на True; это допускает устаревший ответ. Тесты скопированы без изменения.

## Проба: все ответы принимаются

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/cedar-task-probes/C02-stale`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 1; 0.034 с.

```text
test_new_search_keeps_visible_results_until_its_empty_answer (test_search.SearchAppTests.test_new_search_keeps_visible_results_until_its_empty_answer) ... ok
test_older_answer_cannot_change_visible_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_visible_results_in_either_completion_order) ... 
  test_older_answer_cannot_change_visible_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_visible_results_in_either_completion_order) (completion_order=('older', 'current')) ... FAIL
  test_older_answer_cannot_change_visible_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_visible_results_in_either_completion_order) (completion_order=('current', 'older')) ... FAIL
test_search_starts_one_request_and_active_answer_becomes_visible (test_search.SearchAppTests.test_search_starts_one_request_and_active_answer_becomes_visible) ... ok

======================================================================
FAIL: test_older_answer_cannot_change_visible_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_visible_results_in_either_completion_order) (completion_order=('older', 'current'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/cedar-task-probes/C02-stale/test_search.py", line 62, in test_older_answer_cannot_change_visible_results_in_either_completion_order
    self.assertEqual(visible, app.visible)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Tuples differ: () != ('fox result',)

Second tuple contains 1 additional elements.
First extra element 0:
'fox result'

- ()
+ ('fox result',)

======================================================================
FAIL: test_older_answer_cannot_change_visible_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_visible_results_in_either_completion_order) (completion_order=('current', 'older'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/cedar-task-probes/C02-stale/test_search.py", line 62, in test_older_answer_cannot_change_visible_results_in_either_completion_order
    self.assertEqual(visible, app.visible)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Tuples differ: ('whale result',) != ('fox result',)

First differing element 0:
'whale result'
'fox result'

- ('whale result',)
?   ^^^^^

+ ('fox result',)
?   ^^^


----------------------------------------------------------------------
Ran 3 tests in 0.001s

FAILED (failures=2)
```

Проба устойчивости к рефакторингу: в другой копии монотонные числа заменены свежими object() на каждый search. Для предусмотренных входящих ответов token сохраняет только идентичность; внешний контракт не меняется. Тесты прежние.

## Проба: непрозрачные объектные токены

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/cedar-task-probes/C02-opaque`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.034 с.

```text
test_new_search_keeps_visible_results_until_its_empty_answer (test_search.SearchAppTests.test_new_search_keeps_visible_results_until_its_empty_answer) ... ok
test_older_answer_cannot_change_visible_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_visible_results_in_either_completion_order) ... ok
test_search_starts_one_request_and_active_answer_becomes_visible (test_search.SearchAppTests.test_search_starts_one_request_and_active_answer_becomes_visible) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

SHA-256 search.py совпал с исходным: production не изменён. Проба устаревшего ответа дала ровно 2 поведенческих отказа для двух порядков; замена чисел объектами сохранила 3 успешных теста.

## Итог против неизменённого production

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C02`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.034 с.

```text
test_new_search_keeps_visible_results_until_its_empty_answer (test_search.SearchAppTests.test_new_search_keeps_visible_results_until_its_empty_answer) ... ok
test_older_answer_cannot_change_visible_results_in_either_completion_order (test_search.SearchAppTests.test_older_answer_cannot_change_visible_results_in_either_completion_order) ... ok
test_search_starts_one_request_and_active_answer_becomes_visible (test_search.SearchAppTests.test_search_starts_one_request_and_active_answer_becomes_visible) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

Финальная проверка сохранности: SHA-256 исходных search.py совпали с сохранёнными до работы. Посторонние исходные файлы не менялись.

