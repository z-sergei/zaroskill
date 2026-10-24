# C01 — журнал TDD

Источник требований: task.md. Граница: реальные TicketDesk/Receipt, публичные reserve и owner, один процесс. Внешних эффектов нет.

| Требование | Сценарий и ожидаемое наблюдение | План проверки |
|---|---|---|
| Начальное состояние и первая бронь | owner=None; первая заявка Ada принята, owner=Ada | test_first_reservation_assigns_the_seat |
| Одно место | после Ada заявка Ben отклонена, owner=Ada | test_another_customer_cannot_take_the_occupied_seat |
| Повтор заявки | повтор принятой и отклонённой заявки возвращает исходную квитанцию | test_repeating_a_request_returns_its_original_receipt |
| ID закреплён за клиентом; сохранение и повторное использование | чужой клиент с занятым ID получает ValueError; бронь/квитанции сохранены; последующие вызовы работают | test_reusing_an_id_for_another_customer_preserves_the_booking |

Ожидания получены из task.md; идентичность Python-объекта Receipt не навязывается. Новая заявка того же владельца отдельно не специфицируется.

## Исходный запуск

Команда (в work/C01): `python3 -B -m unittest discover -v`

Код выхода: 5

```text

----------------------------------------------------------------------
Ran 0 tests in 0.000s

NO TESTS RAN
```

Обнаружено 0 тестов: это исходное отсутствие проверок, не поведенческий green.

## Срез 1: red до реализации первой брони

Команда: `python3 -B -m unittest -v test_booking.TicketDeskTests.test_first_reservation_assigns_the_seat`

Код выхода: 1

```text
test_first_reservation_assigns_the_seat (test_booking.TicketDeskTests.test_first_reservation_assigns_the_seat) ... ERROR

======================================================================
ERROR: test_first_reservation_assigns_the_seat (test_booking.TicketDeskTests.test_first_reservation_assigns_the_seat)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C01/test_booking.py", line 11, in test_first_reservation_assigns_the_seat
    receipt = desk.reserve("Ada", "booking-a")
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C01/booking.py", line 13, in reserve
    raise NotImplementedError('reservation is not implemented')
NotImplementedError: reservation is not implemented

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

Валидный первый вызов дошёл до reserve и получил NotImplementedError. Это точное отсутствие требуемой реализации, а не ошибка импорта или подготовки.

## Срез 1: green

Команда: `python3 -B -m unittest -v test_booking.TicketDeskTests.test_first_reservation_assigns_the_seat`

Код выхода: 0

```text
test_first_reservation_assigns_the_seat (test_booking.TicketDeskTests.test_first_reservation_assigns_the_seat) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

После red реализованы назначение владельца и принятие первой брони. Ожидания теста не менялись.

## Срез 1: регрессии

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_first_reservation_assigns_the_seat (test_booking.TicketDeskTests.test_first_reservation_assigns_the_seat) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

Вся имеющаяся выборка: 1 тест прошёл.

## Срез 2: red до защиты занятого места

Команда: `python3 -B -m unittest -v test_booking.TicketDeskTests.test_another_customer_cannot_take_the_occupied_seat`

Код выхода: 1

```text
test_another_customer_cannot_take_the_occupied_seat (test_booking.TicketDeskTests.test_another_customer_cannot_take_the_occupied_seat) ... FAIL

======================================================================
FAIL: test_another_customer_cannot_take_the_occupied_seat (test_booking.TicketDeskTests.test_another_customer_cannot_take_the_occupied_seat)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C01/test_booking.py", line 22, in test_another_customer_cannot_take_the_occupied_seat
    self.assertEqual(Receipt("Ben", False), receipt)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Receipt(customer='Ben', accepted=False) != Receipt(customer='Ben', accepted=True)

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

Новая заявка Ben обязана получить accepted=False после брони Ada.

## Срез 2: green

Команда: `python3 -B -m unittest -v test_booking.TicketDeskTests.test_another_customer_cannot_take_the_occupied_seat`

Код выхода: 0

```text
test_another_customer_cannot_take_the_occupied_seat (test_booking.TicketDeskTests.test_another_customer_cannot_take_the_occupied_seat) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

Решение о принятии зависит от наличия свободного места; отклонение сохраняет владельца.

## Срез 2: регрессии

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_another_customer_cannot_take_the_occupied_seat (test_booking.TicketDeskTests.test_another_customer_cannot_take_the_occupied_seat) ... ok
test_first_reservation_assigns_the_seat (test_booking.TicketDeskTests.test_first_reservation_assigns_the_seat) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

2 теста прошли без изменения ожиданий.

## Срез 3: red до повторного использования квитанции

Команда: `python3 -B -m unittest -v test_booking.TicketDeskTests.test_repeating_a_request_returns_its_original_receipt`

Код выхода: 1

```text
test_repeating_a_request_returns_its_original_receipt (test_booking.TicketDeskTests.test_repeating_a_request_returns_its_original_receipt) ... FAIL

======================================================================
FAIL: test_repeating_a_request_returns_its_original_receipt (test_booking.TicketDeskTests.test_repeating_a_request_returns_its_original_receipt)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C01/test_booking.py", line 32, in test_repeating_a_request_returns_its_original_receipt
    self.assertEqual(accepted, desk.reserve("Ada", "booking-a"))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Receipt(customer='Ada', accepted=True) != Receipt(customer='Ada', accepted=False)

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

Повтор ранее принятой заявки не должен превращаться в отказ из-за занятого места.

## Срез 3: green

Команда: `python3 -B -m unittest -v test_booking.TicketDeskTests.test_repeating_a_request_returns_its_original_receipt`

Код выхода: 0

```text
test_repeating_a_request_returns_its_original_receipt (test_booking.TicketDeskTests.test_repeating_a_request_returns_its_original_receipt) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

Квитанции принятия и отказа сохранены по request_id; повтор возвращает прежнее решение.

## Срез 3: регрессии

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_another_customer_cannot_take_the_occupied_seat (test_booking.TicketDeskTests.test_another_customer_cannot_take_the_occupied_seat) ... ok
test_first_reservation_assigns_the_seat (test_booking.TicketDeskTests.test_first_reservation_assigns_the_seat) ... ok
test_repeating_a_request_returns_its_original_receipt (test_booking.TicketDeskTests.test_repeating_a_request_returns_its_original_receipt) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

3 теста прошли.

## Срез 4: red до проверки владельца ID

Команда: `python3 -B -m unittest -v test_booking.TicketDeskTests.test_reusing_an_id_for_another_customer_preserves_the_booking`

Код выхода: 1

```text
test_reusing_an_id_for_another_customer_preserves_the_booking (test_booking.TicketDeskTests.test_reusing_an_id_for_another_customer_preserves_the_booking) ... 
  test_reusing_an_id_for_another_customer_preserves_the_booking (test_booking.TicketDeskTests.test_reusing_an_id_for_another_customer_preserves_the_booking) (reused_id='booking-a') ... FAIL
  test_reusing_an_id_for_another_customer_preserves_the_booking (test_booking.TicketDeskTests.test_reusing_an_id_for_another_customer_preserves_the_booking) (reused_id='booking-b') ... FAIL

======================================================================
FAIL: test_reusing_an_id_for_another_customer_preserves_the_booking (test_booking.TicketDeskTests.test_reusing_an_id_for_another_customer_preserves_the_booking) (reused_id='booking-a')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C01/test_booking.py", line 45, in test_reusing_an_id_for_another_customer_preserves_the_booking
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_reusing_an_id_for_another_customer_preserves_the_booking (test_booking.TicketDeskTests.test_reusing_an_id_for_another_customer_preserves_the_booking) (reused_id='booking-b')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/zaroskill-properties-yy0u92e2/runs/spruce/work/C01/test_booking.py", line 45, in test_reusing_an_id_for_another_customer_preserves_the_booking
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=2)
```

Чужой клиент должен получать ValueError как для принятого, так и для отклонённого request_id.

## Срез 4: green

Команда: `python3 -B -m unittest -v test_booking.TicketDeskTests.test_reusing_an_id_for_another_customer_preserves_the_booking`

Код выхода: 0

```text
test_reusing_an_id_for_another_customer_preserves_the_booking (test_booking.TicketDeskTests.test_reusing_an_id_for_another_customer_preserves_the_booking) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

## Итоговая выборка

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_another_customer_cannot_take_the_occupied_seat (test_booking.TicketDeskTests.test_another_customer_cannot_take_the_occupied_seat) ... ok
test_first_reservation_assigns_the_seat (test_booking.TicketDeskTests.test_first_reservation_assigns_the_seat) ... ok
test_repeating_a_request_returns_its_original_receipt (test_booking.TicketDeskTests.test_repeating_a_request_returns_its_original_receipt) ... ok
test_reusing_an_id_for_another_customer_preserves_the_booking (test_booking.TicketDeskTests.test_reusing_an_id_for_another_customer_preserves_the_booking) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

Все четыре поведенческих среза имеют наблюдавшиеся red и green. После исключения проверены исходная бронь, прежние квитанции и последующий новый вызов. Отдельный рефакторинг не требовался. Интеграционных границ в задании нет.
