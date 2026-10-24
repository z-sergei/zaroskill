# Свидетельства C03

Контракт: после двух begin допустимы оба порядка finish; устаревший результат не должен заменять текущий документ. Просмотрены единственный test_upload.py и реальный Upload. В цикле active всегда равен app.current, поэтому условие строки 12 ложно; finish и смысловой assert строк 13–14 не выполняются. Счётчик states равен 1+...+20=210 и доказывает только число запусков.

## Исходный единственный тест

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C03`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.033 с.

```text
test_previous_upload_cannot_replace_current_document (test_upload.UploadTests.test_previous_upload_cannot_replace_current_document) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

Проба: в отдельной копии условие finish заменено на True. Любой старый token теперь может записать document. Оригинальный test_upload.py скопирован без изменений.

## Проба: исходный тест с отключённой защитой

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/cedar-task-probes/C03-unguarded`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.033 с.

```text
test_previous_upload_cannot_replace_current_document (test_upload.UploadTests.test_previous_upload_cannot_replace_current_document) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

## Свидетель: текущий результат, затем старый на неисправной копии

Команда: `python3 -c 'from upload import Upload; import unittest; app=Upload(); older=app.begin(); current=app.begin(); app.finish(current,"current-document"); app.finish(older,"older-document"); print("expected=current-document, actual="+str(app.document), flush=True); unittest.TestCase().assertEqual("current-document",app.document)'`

Каталог: `/private/tmp/cedar-task-probes/C03-unguarded`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 1; 0.030 с.

```text
expected=current-document, actual=older-document
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from upload import Upload; import unittest; app=Upload(); older=app.begin(); current=app.begin(); app.finish(current,"current-document"); app.finish(older,"older-document"); print("expected=current-document, actual="+str(app.document), flush=True); unittest.TestCase().assertEqual("current-document",app.document)
                                                                                                                                                                                                                                                             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.4/Frameworks/Python.framework/Versions/3.14/lib/python3.14/unittest/case.py", line 925, in assertEqual
    assertion_func(first, second, msg=msg)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.4/Frameworks/Python.framework/Versions/3.14/lib/python3.14/unittest/case.py", line 1291, in assertMultiLineEqual
    self.fail(self._formatMessage(msg, standardMsg))
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.4/Frameworks/Python.framework/Versions/3.14/lib/python3.14/unittest/case.py", line 750, in fail
    raise self.failureException(msg)
AssertionError: 'current-document' != 'older-document'
- current-document
+ older-document
```

## Тот же свидетель на исходной реализации

Команда: `python3 -c 'from upload import Upload; import unittest; app=Upload(); older=app.begin(); current=app.begin(); app.finish(current,"current-document"); app.finish(older,"older-document"); print("expected=current-document, actual="+str(app.document), flush=True); unittest.TestCase().assertEqual("current-document",app.document)'`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C03`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.029 с.

```text
expected=current-document, actual=current-document
```

В исходной реализации свидетель прошёл. В неисправной копии исходный тест остался зелёным (1 тест), а допустимая трасса показала older-document вместо current-document и завершилась AssertionError. Это подтверждает пробел теста, а не дефект текущего Upload. Изменён только disposable probe.

Финальная проверка сохранности: SHA-256 исходных upload.py, test_upload.py совпали с сохранёнными до работы. Посторонние исходные файлы не менялись.

