# C03 — обзор теста старого upload

Источник: task.md; допустимы begin(A), begin(B), затем оба порядка завершений. Проверяемый результат — старый ответ не меняет документ, актуальный может примениться. Граница — Upload.begin/finish и document.

Статический вывод: test_upload.py:10 присваивает active последний результат begin(), равный current. Условие на строке 12 ложно во всех 20 итерациях; finish и assertIsNone не выполняются. Сумма states=210 подтверждает лишь число вызовов begin, не свойство документов.

## Исходный тест

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C03`

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_previous_upload_cannot_replace_current_document (test_upload.UploadTests.test_previous_upload_cannot_replace_current_document) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

1 тест обнаружен и проходит; выполненная проверка states не достигает контрактного поведения.

## Дефект в копии: finish принимает любой token

Каталог: `/private/tmp/spruce-C03-8i9oqime`

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_previous_upload_cannot_replace_current_document (test_upload.UploadTests.test_previous_upload_cannot_replace_current_document) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

Удалена только проверка актуальности token; исходный test_upload.py неизменён. Ошибочная реализация всё ещё проходит 1 тест.

## Достижимый контрпример на дефектной копии

Каталог: `/private/tmp/spruce-C03-8i9oqime`

Команда: `python3 -B -c 'from upload import Upload; app = Upload(); old = app.begin(); current = app.begin(); app.finish(current, "current-document"); print("after current:", app.document); app.finish(old, "older-document"); print("after old:", app.document); assert app.document == "current-document", "older result replaced the current document"'`

Код выхода: 1

```text
after current: current-document
after old: older-document
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from upload import Upload; app = Upload(); old = app.begin(); current = app.begin(); app.finish(current, "current-document"); print("after current:", app.document); app.finish(old, "older-document"); print("after old:", app.document); assert app.document == "current-document", "older result replaced the current document"
                                                                                                                                                                                                                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: older result replaced the current document
```

Два последовательных begin, актуальный ответ, затем старый. AssertionError подтверждает наблюдаемую потерю актуального документа; это не эквивалентная мутация.

## Тот же контрпример на исходной реализации

Каталог: `/private/tmp/spruce-C03-8i9oqime`

Команда: `python3 -B -c 'from upload import Upload; app = Upload(); old = app.begin(); current = app.begin(); app.finish(current, "current-document"); print("after current:", app.document); app.finish(old, "older-document"); print("after old:", app.document); assert app.document == "current-document", "older result replaced the current document"'`

Код выхода: 0

```text
after current: current-document
after old: current-document
```

Исходный guard сохраняет current-document; ошибка обнаружена в доказательстве теста, а не в исходном Upload.

Оригинальные upload.py и test_upload.py побайтно сохранены. Пробы были только в удалённой временной копии; повтор исходного теста после неё не нужен, т.к. исходные файлы не изменялись. Других тестов по условию нет.
