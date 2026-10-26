# Журнал фактического выполнения

Рабочий корень: `<run>`.
Порядок из `order.json`: `04_discount_cap`, затем `06_upload_workflow`.

## 04_discount_cap

Прочитаны `task.md`, локальный `skills/requirements-tdd/SKILL.md`, references `existing-code.md` и `behavior-properties.md`, исходники `discounts.py` и `test_discounts.py`.

Все приведённые ниже команды этого задания выполнены из `work/cases/04_discount_cap`, с `PYTHONDONTWRITEBYTECODE=1`, чтобы не создавать служебные файлы рядом с исходниками.

1. `python -m unittest discover -v` — код 127: `zsh:1: command not found: python`. Это проблема имени интерпретатора, не red.
2. `python3 -m unittest discover -v` — код 0, исходные 6 тестов прошли.

Добавлен `test_discount_cannot_exceed_cap`: скидка 150 центов ограничивается 100, ожидаемый итог 900. В production добавлено только объявление `*, max_discount_cents=None`; до red параметр не используется, старый расчёт сохранён.

3. `python3 -m unittest -v test_discounts.DiscountTests.test_discount_cannot_exceed_cap` — код 1, 1 тест, `AssertionError: 850 != 900`. Это наблюдаемое поведенческое red: объявленный лимит не применялся.

После red добавлено ограничение вычисленной скидки через `min(discount, max_discount_cents)`, только когда лимит не `None`.

4. Повтор `python3 -m unittest -v test_discounts.DiscountTests.test_discount_cannot_exceed_cap` — код 0, 1 тест прошёл (green).
5. `python3 -m unittest discover -v` — код 0, 7 тестов прошли.

Следующим добавлен тест отрицательного лимита: четыре входа `(0, 0)`, `(0, 100)`, `(1000, 0)`, `(1000, 15)`, каждый ожидает `ValueError` для лимита `-1`. Реализация проверки ещё не добавлена.

6. `python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_rejected_even_without_discount` — код 1, 1 тест с 4 упавшими subtest: `AssertionError: ValueError not raised`. Red вызван отсутствием валидации лимита, в том числе при нулевой скидке.

После red добавлена проверка `max_discount_cents < 0` до расчёта скидки, с исключением `ValueError`.

7. Повтор `python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_rejected_even_without_discount` — код 0, 1 тест прошёл (green).
8. `python3 -m unittest discover -v` — код 0, 8 тестов прошли.

Добавлены оставшиеся контрактные примеры: явный `None`, равный/больший лимит, нулевой лимит, keyword-only вызов, прежняя валидация при лимите 0. Эти тесты проверяют уже реализованное правило; production не менялся, отдельные red–green циклы для них не заявляются.

9. `python3 -m unittest discover -v` — код 0, итоговые 13 тестов прошли.
10. `cat discounts.py test_discounts.py` — итоговые файлы просмотрены; исходные шесть методов и их ожидания сохранены. Зависимости не добавлялись. Итоговый `response.md` содержит проверенную карту требований, оба реальных red–green цикла и объяснение стоимости тестов.

`04_discount_cap` завершено перед чтением следующего задания.

## 06_upload_workflow

Только после завершения первого задания прочитаны `task.md`, локальный `skills/state-machine-verification/SKILL.md`, reference `temporal-checks.md`, `upload.py` и `test_upload.py`. Новый ведущий процесс — проверка временных контрактов; TDD для уже корректного production не заявляется.

Рабочая папка команд: `work/cases/06_upload_workflow`, `PYTHONDONTWRITEBYTECODE=1`.

1. `python3 -m unittest discover -v` — код 0, исходные 3 теста прошли.
2. `python3 -c 'from pathlib import Path; import hashlib; print(hashlib.sha256(Path("upload.py").read_bytes()).hexdigest())'` — код 0; исходный SHA-256 `2eb255004f3ff1076292c96bc960c8abcee553e989f3605de4e8bb101c77b725`.

В `test_upload.py` добавлены пять сценариев только через публичный API и проверка целочисленного id в существующем успешном сценарии. `upload.py` не редактировался.

3. `python3 -m unittest discover -v` — код 0, 8 тестов прошли.
4. Из общего корня: `PYTHONDONTWRITEBYTECODE=1 python3 probes/upload_fault_probes.py` — код 0. Созданы три одноразовые копии текущего случая. Полные subprocess-команды и коды сохранены в `probes/upload_probe_results.json`:
   - `rejected_begin_changes_active_attempt`: исходные 3 теста — код 0; новый `test_rejected_begin_preserves_the_attempt_that_can_complete` — код 1, `False is not True` при завершении исходного id.
   - `predecessor_result_is_accepted`: исходные 3 теста — код 0; новый `test_restarts_clear_results_and_reject_previous_attempts` — код 1, два subtest с `True is not False` при устаревшем ответе.
   - `late_cancel_erases_result`: исходные 3 теста — код 0; новый `test_completion_before_cancel_keeps_first_result` — код 1, `('done', None) != ('done', 'first.csv')` после поздней отмены.
   Скрипт сравнил исходные и итоговые байты рабочего `upload.py`: одинаковы. SHA-256 остался `2eb255004f3ff1076292c96bc960c8abcee553e989f3605de4e8bb101c77b725`.
5. `python3 -m unittest discover -v` в рабочем случае после проб — код 0, все 8 тестов прошли.
6. Прочитаны три файла `probes/<имя>/distinguishing.txt`; подтверждены ошибки утверждений по нужному поведению, не ошибки импорта или runner.
7. `rg -n '_active|_last|^    def test_' test_upload.py` — просмотрены имена 8 тестов; обращений к приватным полям нет (совпадение `_active` есть только в имени существующего теста отмены).

`06_upload_workflow` завершено. Фиксированные конечные сценарии и три fault probe не выдаются за полный перебор или формальное доказательство. Итоговый `response.md` объясняет различающие истории, полезную защиту и стоимость поддержки.

## Итоговая проверка артефактов

Из общего корня выполнен `PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY' ... PY` со стандартными `json`, `pathlib`, `hashlib`: разобран `summary.json`, проверены статус и порядок двух завершённых случаев, существование всех указанных файлов, три результата probe (исходные тесты — код 0, различающий сценарий — код 1) и SHA-256 рабочего `upload.py`. Код 0. Вывод: `summary.json: valid; both responses and execution.md exist; 13 + 8 final passing tests recorded; 3 fault probes verified; upload.py hash unchanged`.

Сеть, чужие каталоги, установленные навыки, материалы оценки и делегирование не использовались. Новых зависимостей нет. Все записи находятся в разрешённых исходных файлах, двух `response.md`, общих `execution.md`/`summary.json` и `probes/`.
