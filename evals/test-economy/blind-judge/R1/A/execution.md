# Фактическое выполнение

Все команды ниже выполнялись внутри разрешённого корня. Чтение ограничено текущим случаем, `order.json`, `prompt.txt` и указанным навыком с его локальными references. Зависимости не устанавливались, сеть и делегирование не использовались.

## 01_shipping_bands

Ведущий навык: `skills/khorikov-unit-testing/SKILL.md`; прочитан `references/sources.md`.

Команда из `work/cases/01_shipping_bands`: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`.

1. До изменений: `Ran 13 tests in 0.000s`, `OK`, exit 0.
2. После изменения только `test_shipping.py`: `Ran 4 tests in 0.000s`, `OK`, exit 0. Четыре метода проверяют десять входов через `subTest`.

Сохранено объяснение в `work/cases/01_shipping_bands/response.md`. Дополнительные fault/refactor probes не выполнялись.

## 02_display_name

Ведущий навык: `khorikov-unit-testing`; применён отдельно к контракту имени, использованы уже прочитанные инструкции и `references/sources.md`.

Команда из `work/cases/02_display_name`: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`.

1. Исходные тесты: `Ran 7 tests in 0.000s`, `OK`, exit 0.
2. После двух добавлений в `test_names.py`: `Ran 9 tests in 0.000s`, `OK`, exit 0.

Сохранено объяснение в `work/cases/02_display_name/response.md`. Production не изменён; отдельные probes не выполнялись.

## 03_capacity_boundaries

Ведущий навык: `test-quality-review`; прочитаны `references/boundaries-and-traps.md`, `probes.md`, `sources.md`.

Команда для каждого набора: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`.

1. Реальная исходная папка: 6 tests, `OK`, exit 0.
2. Создана копия текущего случая в `probes/03_capacity`; контроль копии: 6 tests, `OK`, exit 0.
3. В копии заменено одно `return updated` в `reserve` на `return limit`: исходные 6 tests, `OK`, exit 0. Команда `python3 -c 'from capacity import reserve; print(reserve(3, 2, 10))'` дала `10`, хотя контракт требует `5`.
4. После добавления двух случаев и проверки payload их копия на том же дефекте: 8 tests, 2 assertion failures, exit 1 (`10 != 5` и словарь с `used: 10` вместо `5`). Полные результаты: `probes/03_capacity/initial_results.txt`, `strengthened_results.txt`.
5. Проверен неизменный SHA-256 настоящего `capacity.py`; исходник копии восстановлен. Настоящий проект: 8 tests, `OK`, exit 0.
6. Добавлена проверка `ValueError` к существующему случаю ошибки. Финальный настоящий проект: 8 tests, `OK`, exit 0.

Сохранено ревью `work/cases/03_capacity_boundaries/response.md`. Широкой mutation campaign и refactor probe не было.

## 04_discount_cap — наблюдаемая последовательность TDD

Ведущий навык: `requirements-tdd`; прочитан `references/existing-code.md`. Все команды из `work/cases/04_discount_cap`, с `PYTHONDONTWRITEBYTECODE=1`.

1. `python3 -m unittest discover -v`: исходные 6 tests, `OK`, exit 0.
2. Добавлен только `test_discount_cannot_exceed_the_cap` с ожидаемым 800 для `(1000, 30, max_discount_cents=200)`.
3. `python3 -m unittest -v test_discounts.DiscountTests.test_discount_cannot_exceed_the_cap`: 1 test, ERROR, exit 1; `TypeError: discounted_total() got an unexpected keyword argument 'max_discount_cents'`. Отсутствующий API, ещё не содержательная проверка вычисления.
4. В production добавлена только сигнатура `*, max_discount_cents=None`, тело прежнее. Та же команда: 1 test, FAIL, exit 1; `AssertionError: 700 != 800`. Это behavioral red до реализации ограничения.
5. Добавлены `if max_discount_cents is not None` и `discount = min(discount, max_discount_cents)`. Та же команда: 1 test, `OK`, exit 0. Затем `python3 -m unittest discover -v`: 7 tests, `OK`, exit 0.
6. Добавлен `test_negative_cap_is_invalid_even_when_the_discount_is_zero` с процентами 0 и 30, cap -1.
7. `python3 -m unittest -v test_discounts.DiscountTests.test_negative_cap_is_invalid_even_when_the_discount_is_zero`: 1 test, 2 failures, exit 1; оба `AssertionError: ValueError not raised`. Это red отдельного требования валидации.
8. Добавлен guard отрицательного лимита до расчёта. Та же команда: 1 test, `OK`, exit 0. Затем `python3 -m unittest discover -v`: 8 tests, `OK`, exit 0.
9. Добавлены явный None, высокий и нулевой лимиты, keyword-only форма вызова; прежние тесты отрицательной суммы и недопустимого процента расширены на нулевой лимит. `python3 -m unittest discover -v`: 12 tests, `OK`, exit 0. Эти дополнительные случаи сразу green и не названы самостоятельными red/green циклами.
10. Финальные `discounts.py` и `test_discounts.py` прочитаны и проверены: только заявленная сигнатура, guard и ограничение скидки; прежние значения ожидаемых результатов не ослаблялись.

Сохранено `work/cases/04_discount_cap/response.md`. Refactor и дополнительный fault-probe не требовались.

## 05_mutation_report

Ведущий навык: `test-quality-review`; применены ранее прочитанные локальные `probes.md`, `boundaries-and-traps.md`, `sources.md`. Приложенный JSON является synthetic fixture, не результатом нашего инструмента.

1. В `work/cases/05_mutation_report`: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v` — 6 tests, `OK`, exit 0.
2. Создана одноразовая копия `probes/05_cancellation`. Тестовый файл не менялся. Та же команда на исходной копии: 6 tests, `OK`, exit 0.
3. Ручная подмена M2, `>= 48` → `>= 47`: 6 tests, `OK`, exit 0. Отдельная команда `python3 -c 'from cancellation import cancellation_fee; print(cancellation_fee(47, 100))'` вернула 0 вместо требуемых 25.
4. Вновь от оригинала подмена M3, `paid_cents // 2` → `(paid_cents + 1) // 2`: 6 tests, 1 failure, exit 1; `test_half_fee_rounds_down`, `51 != 50`.
5. Вновь от оригинала подмена M4, `>= 24` → `>= 25`: 6 tests, 1 failure, exit 1; `test_at_day_boundary`, `50 != 25`.
6. Подмена в копии восстановлена; SHA-256 исходных `cancellation.py`, `test_cancellation.py`, `mutation-report.json` совпали с сохранёнными до probe.
7. Повтор исходной папки: 6 tests, `OK`, exit 0.

Сохранены полные выводы в `probes/05_cancellation/*.txt` и итоговое `work/cases/05_mutation_report/review.md`. M1 обоснован алгебраически, отдельно не исполнялся. Новые рекомендованные тесты и реальный mutation worker не запускались.

## 06_upload_workflow

Ведущий навык: `state-machine-verification`; прочитан `references/temporal-checks.md`, также просмотрены design-checks; никаких новых продуктовых гарантий не вводилось.

Команда: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v`.

1. Исходная папка: 3 tests, `OK`, exit 0. Исходники и исходные тесты скопированы в `probes/06_upload` до изменений.
2. Усилен только `test_upload.py`: 7 tests, `OK`, exit 0.
3. Контроль копии с исходными тестами: 3 tests, `OK`, exit 0.
4. Fault `reuse_attempt_id_after_restart`: в копии перед `self._last_attempt += 1` добавлен сброс счётчика в 0 для `done`/`cancelled`. Исходные 3 tests: `OK`, exit 0. Усиленные 7 tests: 2 failures, exit 1; оба `assertGreater(second, first)` получили `1 not greater than 1`.
5. От оригинала fault `rejected_begin_loses_active_attempt`: перед `raise RuntimeError("already waiting")` добавлено `self._active_attempt = None`. Исходные 3 tests: `OK`, exit 0. Усиленные 7 tests: 1 failure, exit 1; `test_rejected_begin_preserves_the_active_attempt`, `False is not true` при завершении исходного id.
6. В копии восстановлен оригинал; совпал SHA-256 настоящего `upload.py`. Настоящий проект: 7 tests, `OK`, exit 0.
7. Assertions возвращаемых флагов уточнены до `assertIs(..., True/False)`. Финальная команда в настоящем проекте: 7 tests, `OK`, exit 0. Финальный тестовый файл прочитан для проверки имен и соответствия контракту.

Полные выводы fault-probe сохранены в `probes/06_upload/*.txt`, обоснование — `work/cases/06_upload_workflow/response.md`. Модель, exhaustive exploration, I/O и многопоточность не проверялись; production не менялся.
