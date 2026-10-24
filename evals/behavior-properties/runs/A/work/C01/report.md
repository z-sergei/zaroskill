# C01 — бронирование

Реализовано требуемое поведение с сохранением API: первый запрос занимает место, новые клиенты получают отказ, повтор ID возвращает исходную квитанцию, чужой клиент с тем же ID получает ValueError. Ошибка и отказы сохраняют owner; касса продолжает принимать вызовы.

Покрытие четырьмя тестами:
- `test_first_request_accepts_customer_and_sets_owner`: исходный owner=None, принятая квитанция и новый owner.
- `test_occupied_seat_refuses_other_customers_and_keeps_owner`: повторные обращения других клиентов не меняют владельца.
- `test_repeated_requests_return_original_receipts`: повторы принятой и отклонённой заявки сохраняют результат.
- `test_reusing_request_id_for_another_customer_raises_without_changing_booking`: конфликт обоих видов ID, исходная квитанция и владелец после ошибки, дальнейшее обращение.

Порядок test-first подтверждён реальными прогонами в evidence.md: NotImplementedError → green; неверное accepted=True → green; неверное accepted=False при повторе → green; два отсутствующих ValueError → green. Исходный запуск обнаружил 0 тестов (код 5), что не считалось red. Итоговый `python3 -m unittest discover -v`: 4 теста, OK.

Изменён только booking.py; добавлен test_booking.py и отчётные файлы. Доказательство ограничено заданным синхронным API; неопределённых обязательных требований и блокировок нет.
