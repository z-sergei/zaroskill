# Свидетельства C01

Источник ожидаемого поведения: task.md. Граница: настоящий TicketDesk, вызовы reserve и публичный owner; внешних зависимостей нет.

План: пустой owner и первая успешная бронь; отказ другому покупателю без смены owner и дальнейшие вызовы; повтор обоих видов квитанций; конфликт ID с ValueError и сохранением исходной брони. Ожидания заданы контрактом, не реализацией.

## Исходное состояние: тестов пока нет, это не поведенческий red

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 5; 0.034 с.

```text

----------------------------------------------------------------------
Ran 0 tests in 0.000s

NO TESTS RAN
```

## Red 1: первая бронь ещё не реализована

Команда: `python3 -m unittest -v test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 1; 0.034 с.

```text
test_first_request_accepts_customer_and_sets_owner (test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner) ... ERROR

======================================================================
ERROR: test_first_request_accepts_customer_and_sets_owner (test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01/test_booking.py", line 11, in test_first_request_accepts_customer_and_sets_owner
    receipt = desk.reserve("Alice", "alice-first")
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01/booking.py", line 13, in reserve
    raise NotImplementedError('reservation is not implemented')
NotImplementedError: reservation is not implemented

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

Red 1 достиг допустимого reserve и завершился именно NotImplementedError отсутствующего поведения; импорт и открытие кассы работали. Это реальный red до изменения booking.py.

## Green 1: первая бронь

Команда: `python3 -m unittest -v test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.034 с.

```text
test_first_request_accepts_customer_and_sets_owner (test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

Изменение 1: reserve сохраняет customer в owner и возвращает принятую квитанцию для любого первого клиента; специальных литералов теста в реализации нет.

## Red 2: занятое место нельзя отдать другому

Команда: `python3 -m unittest -v test_booking.TicketDeskTests.test_occupied_seat_refuses_other_customers_and_keeps_owner`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 1; 0.033 с.

```text
test_occupied_seat_refuses_other_customers_and_keeps_owner (test_booking.TicketDeskTests.test_occupied_seat_refuses_other_customers_and_keeps_owner) ... FAIL

======================================================================
FAIL: test_occupied_seat_refuses_other_customers_and_keeps_owner (test_booking.TicketDeskTests.test_occupied_seat_refuses_other_customers_and_keeps_owner)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01/test_booking.py", line 20, in test_occupied_seat_refuses_other_customers_and_keeps_owner
    self.assertEqual(Receipt("Bob", False), desk.reserve("Bob", "bob-first"))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Receipt(customer='Bob', accepted=False) != Receipt(customer='Bob', accepted=True)

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

## Green 2: занятое место и регрессии

Команда: `python3 -m unittest -v test_booking.TicketDeskTests.test_occupied_seat_refuses_other_customers_and_keeps_owner test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.034 с.

```text
test_occupied_seat_refuses_other_customers_and_keeps_owner (test_booking.TicketDeskTests.test_occupied_seat_refuses_other_customers_and_keeps_owner) ... ok
test_first_request_accepts_customer_and_sets_owner (test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

Red 2: для Bob пришло accepted=True вместо False. Изменение 2: занятость определяет принятие; последующие отказы сохраняют owner. Оба текущих теста прошли.

## Red 3: повтор принятого запроса должен сохранить результат

Команда: `python3 -m unittest -v test_booking.TicketDeskTests.test_repeated_requests_return_original_receipts`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 1; 0.034 с.

```text
test_repeated_requests_return_original_receipts (test_booking.TicketDeskTests.test_repeated_requests_return_original_receipts) ... FAIL

======================================================================
FAIL: test_repeated_requests_return_original_receipts (test_booking.TicketDeskTests.test_repeated_requests_return_original_receipts)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01/test_booking.py", line 32, in test_repeated_requests_return_original_receipts
    self.assertEqual(accepted, desk.reserve("Alice", "alice-first"))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Receipt(customer='Alice', accepted=True) != Receipt(customer='Alice', accepted=False)

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

## Green 3: повтор квитанций и регрессии

Команда: `python3 -m unittest -v test_booking.TicketDeskTests.test_repeated_requests_return_original_receipts test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner test_booking.TicketDeskTests.test_occupied_seat_refuses_other_customers_and_keeps_owner`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.037 с.

```text
test_repeated_requests_return_original_receipts (test_booking.TicketDeskTests.test_repeated_requests_return_original_receipts) ... ok
test_first_request_accepts_customer_and_sets_owner (test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner) ... ok
test_occupied_seat_refuses_other_customers_and_keeps_owner (test_booking.TicketDeskTests.test_occupied_seat_refuses_other_customers_and_keeps_owner) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

Red 3: повтор alice-first вернул accepted=False вместо исходного True. Изменение 3: сохраняются квитанции для каждого ID; повторы возвращают сохранённый результат. Все три теста прошли.

## Red 4: чужой покупатель не может повторно использовать ID

Команда: `python3 -m unittest -v test_booking.TicketDeskTests.test_reusing_request_id_for_another_customer_raises_without_changing_booking`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 1; 0.042 с.

```text
test_reusing_request_id_for_another_customer_raises_without_changing_booking (test_booking.TicketDeskTests.test_reusing_request_id_for_another_customer_raises_without_changing_booking) ... 
  test_reusing_request_id_for_another_customer_raises_without_changing_booking (test_booking.TicketDeskTests.test_reusing_request_id_for_another_customer_raises_without_changing_booking) (request_id='alice-first') ... FAIL
  test_reusing_request_id_for_another_customer_raises_without_changing_booking (test_booking.TicketDeskTests.test_reusing_request_id_for_another_customer_raises_without_changing_booking) (request_id='bob-first') ... FAIL

======================================================================
FAIL: test_reusing_request_id_for_another_customer_raises_without_changing_booking (test_booking.TicketDeskTests.test_reusing_request_id_for_another_customer_raises_without_changing_booking) (request_id='alice-first')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01/test_booking.py", line 47, in test_reusing_request_id_for_another_customer_raises_without_changing_booking
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_reusing_request_id_for_another_customer_raises_without_changing_booking (test_booking.TicketDeskTests.test_reusing_request_id_for_another_customer_raises_without_changing_booking) (request_id='bob-first')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01/test_booking.py", line 47, in test_reusing_request_id_for_another_customer_raises_without_changing_booking
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=2)
```

## Green 4: конфликт ID для принятой и отклонённой заявки

Команда: `python3 -m unittest -v test_booking.TicketDeskTests.test_reusing_request_id_for_another_customer_raises_without_changing_booking`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.036 с.

```text
test_reusing_request_id_for_another_customer_raises_without_changing_booking (test_booking.TicketDeskTests.test_reusing_request_id_for_another_customer_raises_without_changing_booking) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

## Итог: весь набор C01

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C01`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.034 с.

```text
test_first_request_accepts_customer_and_sets_owner (test_booking.TicketDeskTests.test_first_request_accepts_customer_and_sets_owner) ... ok
test_occupied_seat_refuses_other_customers_and_keeps_owner (test_booking.TicketDeskTests.test_occupied_seat_refuses_other_customers_and_keeps_owner) ... ok
test_repeated_requests_return_original_receipts (test_booking.TicketDeskTests.test_repeated_requests_return_original_receipts) ... ok
test_reusing_request_id_for_another_customer_raises_without_changing_booking (test_booking.TicketDeskTests.test_reusing_request_id_for_another_customer_raises_without_changing_booking) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

Red 4: ValueError не возникал для ID принятой и отклонённой заявки. Изменение 4: до любых изменений состояния проверяется customer сохранённой квитанции. Финальные 4 теста прошли; дополнительный рефакторинг не требовался. Проверки ограничены однопроцессной кассой без потоков, срока действия и внешних систем.

Финальная проверка сохранности: изменён только разрешённый booking.py; task.md не менялся. Добавлены test_booking.py и отчётные файлы.

