# Фактическое выполнение

Разрешённая папка: `/private/tmp/zaroskill-economy-n9eezds3/followup/runs/cedar`. Порядок из `order.json`: `04_discount_cap`, затем `06_upload_workflow`. Сеть, делегирование и установка зависимостей не использовались.

## 04_discount_cap

- Прочитаны `prompt.txt`, `order.json`, затем `work/cases/04_discount_cap/task.md`.
- Прочитаны локальный `skills/requirements-tdd/SKILL.md` и references `behavior-properties.md`, `existing-code.md`.
- `rg --files -g 'AGENTS.md' -g '*.py' -g '*.toml' -g '*.cfg' -g 'README*' work/cases/04_discount_cap`: найдены только `discounts.py`, `test_discounts.py`; оба прочитаны.
- Из папки задания: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -v` → exit 127, `command not found: python`. Это проблема команды запуска, не behavioral red.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` → exit 0, 6 тестов, OK. Исходный baseline.
- До реализации записан план требований в `response.md` и добавлен тест `test_discount_is_limited_by_cap` с буквальным ожидаемым значением 900.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_discount_is_limited_by_cap` → exit 1, 1 ERROR: неожиданный `max_discount_cents`.
- Добавлена только декларация keyword-only аргумента с `None`; та же команда → exit 1, 1 FAIL: `850 != 900`. Наблюдаемое behavioral red.
- Реализовано ограничение через `min` при заданном лимите. Та же команда → exit 0, 1 OK. `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` → exit 0, 7 OK.
- Добавлен тест отрицательного лимита (обычная скидка, нулевая сумма, нулевой процент, округление до нуля). `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_rejected_even_when_discount_is_zero` → exit 1, 4 subtest failures: `ValueError not raised`.
- Добавлена проверка отрицательного лимита перед вычислением скидки. Та же команда → exit 0, 1 OK. `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` → exit 0, 8 OK.
- Добавлены проверки `None`, равного/большего лимита, нулевого лимита, keyword-only и старой валидации при нулевом лимите. `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` → exit 0, 13 OK. Новые проверки сразу зелёные и не называются red/green-циклами.
- `cat discounts.py test_discounts.py`: проверены итоговые исходники и сохранность прежних тестов; правки ограничены разрешёнными файлами. `response.md` содержит итоговую связь требований, проверки и обоснование стоимости тестов. Первое задание завершено до чтения второго.

## 06_upload_workflow

- После завершения первого задания прочитан `work/cases/06_upload_workflow/task.md`, затем локальный `skills/state-machine-verification/SKILL.md` и `references/temporal-checks.md`.
- `rg --files -g 'AGENTS.md' -g '*.py' -g '*.toml' -g '*.cfg' -g 'README*' work/cases/06_upload_workflow`: найдены `upload.py`, `test_upload.py`; прочитаны оба.
- Из папки задания `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` → exit 0, 3 OK. Использован `python3`, поскольку отсутствие команды `python` уже установлено первым заданием.
- `shasum -a 256 upload.py` → `2eb255004f3ff1076292c96bc960c8abcee553e989f3605de4e8bb101c77b725`. Production не изменяется.
- В `response.md` записана карта публичного контракта и различающих последовательностей; в `test_upload.py` сохранены прежние три теста, добавлены пять сценариев и проверка целочисленного id в исходном успешном сценарии.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` → exit 0, 8 OK.
- Создан `probes/upload_sensitivity.py`: читает только текущий случай, создаёт одноразовые копии в `probes/`, меняет один названный дефект на копию и запускает неизменённые тесты. `PYTHONDONTWRITEBYTECODE=1 python3 probes/upload_sensitivity.py` → exit 0; полные команды и результаты — `probes/results.json`, выводы — `probes/<variant>/output.txt`.
  - `rejected_begin_loses_active`: целевой `test_rejected_begin_preserves_the_active_attempt` → exit 1, 1 assertion failure (`False is not true`).
  - `cancelled_accepts_late_completion`: целевой `test_cancelled_attempt_ignores_late_completion_and_repeated_cancel` → exit 1, 1 assertion failure (`True is not false`).
  - `restart_reuses_completed_id`: целевой `test_restarts_keep_old_results_out_of_new_attempts` → exit 1, 2 subtest failures (`1 not greater than 1`, `2 not greater than 2`).
  - `rejected_duplicate_overwrites_result`: целевой `test_completed_result_survives_repeated_completion_and_cancel` → exit 1, 3 assertions; запрещённый результат перезаписывает исходный и сохраняется в дальнейших наблюдениях этого сценария.
  - `restart_retains_previous_result`: целевой `test_restarts_keep_old_results_out_of_new_attempts` → exit 1, 2 subtest failures: прежний результат остаётся в waiting.
  - `valid_ids_increase_by_seven`: полный набор → exit 0, 8 OK. Разрешённая смена стратегии id не ломает тесты.
- Проверка SHA-256 в скрипте и повторная `shasum -a 256 upload.py` подтвердили исходное значение: `2eb255004f3ff1076292c96bc960c8abcee553e989f3605de4e8bb101c77b725`.
- После проверок копий `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` в настоящем случае → exit 0, 8 OK.
- `cat test_upload.py`: просмотрены финальные утверждения, соответствие имён и сценариев, отсутствие доступа к приватному API. `response.md` завершён с границами доказательства и обоснованием стоимости. Второе задание завершено.

## Итоговые артефакты

- Сохранён `summary.json` с порядком выполнения, фактическими red/green, числами тестов, ограничениями доказательства и путями к ответам.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m json.tool summary.json` → exit 0: итоговый JSON корректен.
- Оба задания завершены. Другие задания, grading, родители и соседние папки не читались.
