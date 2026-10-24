# Свидетельства C08

Контракт из task.md: enabled=False не отправляет welcome, enabled=True отправляет; SMTP-адаптер уже имеет отдельный contract suite, доставка в человеческий ящик не обещана. Граница здесь — реальный Newsletter и внешний mailer.send. Единственные два теста взаимно дополняются: точное отсутствие вызовов и точный один вызов с адресом/телом, плюс возвращаемый статус.

## Исходные дополняющие unittest

Команда: `python3 -m unittest discover -v`

Каталог: `/private/tmp/zaroskill-properties-yy0u92e2/runs/cedar/work/C08`

`PYTHONDONTWRITEBYTECODE=1`; код выхода 0; 0.034 с.

```text
test_disabled_subscription_sends_nothing (test_newsletter.NewsletterTests.test_disabled_subscription_sends_nothing) ... ok
test_enabled_subscription_requests_welcome_mail (test_newsletter.NewsletterTests.test_enabled_subscription_requests_welcome_mail) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

Обнаружены и выполнены 2 теста, OK. По коду отключение любой отправки нарушит ожидаемый непустой список во втором тесте; безусловная отправка нарушит пустой список в первом. Это вывод из проверок; дополнительные fault-пробы не выполнялись, поскольку дискриминаторы явны. Имеющийся SMTP contract suite принят как условие task.md и здесь не запускался.

Финальная проверка сохранности: SHA-256 исходных test_newsletter.py, newsletter.py совпали с сохранёнными до работы. Посторонние исходные файлы не менялись.

