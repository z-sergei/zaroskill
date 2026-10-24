# C08 — граница отправки welcome

Источник: task.md. Newsletter.subscribe для disabled должен вернуть disabled и не обратиться к почтовому порту; для enabled — subscribed и один запрос Welcome указанному адресату. test_newsletter.py:11-15 проверяет отсутствие эффекта, 17-21 — положительный эффект с точными получателем, телом и количеством. Настоящий Newsletter вызывает записывающий Mailer; решение enabled не подменено.

По коду безусловная отправка нарушит assertEqual([], port.messages); удаление отправки нарушит положительный assertEqual списка сообщений. Это статические аргументы, не выполненные мутации. Реальная доставка до почтового ящика не обещана; покрытие SMTP-адаптера задано условием и здесь не запускалось. Валидация входов уже выполнена до API.

## Запуск локальной выборки

Команда: `python3 -B -m unittest discover -v`

Код выхода: 0

```text
test_disabled_subscription_sends_nothing (test_newsletter.NewsletterTests.test_disabled_subscription_sends_nothing) ... ok
test_enabled_subscription_requests_welcome_mail (test_newsletter.NewsletterTests.test_enabled_subscription_requests_welcome_mail) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

2 теста обнаружены, выполнены и проходят без пропусков. Проверены локальное решение и запрос внешнего эффекта; SMTP-suite не входит в предоставленные файлы.

Оригинальные newsletter.py и test_newsletter.py побайтно сохранены. Дополнительная проба не нужна: обе альтернативы явно различаются существующими утверждениями.
