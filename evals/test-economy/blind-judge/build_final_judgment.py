import json
from pathlib import Path

root=Path(__file__).resolve().parent
r1=json.loads((root/'judgment-R1.json').read_text())
r2=json.loads((root/'judgment-R2.json').read_text())
assert r1['status']=='complete_for_R1_only' and r2['status']=='complete_for_R2'
assert len(r1['cases'])==len(r2['cases'])==6

aggregate=dict(
    conclusion='Однозначное общее улучшение экономности при сохранении всей наблюдаемой защиты не установлено. Есть небольшие локальные возможности сокращения и реальные встречные преимущества по контрактной защите. Версионного победителя без закрытого ключа и при таком объёме данных объявлять нельзя.',
    pair_outcomes={'R1':r1['aggregate'],'R2':r2['aggregate']},
    version_level_winner=None,
    pair_label_alignment='Unknown. A/B may denote different versions in R1 and R2; no cross-pair label identity inferred.',
    manual_economy_findings=[
        dict(pair='R1',candidate='B',case='C01',scenario='delivery_fee(12000) == 0',reason='Заявленная роль продолжения бесплатного диапазона уже представлена 10**30.'),
        dict(pair='R1',candidate='B',case='C04',scenario='discounted_total(1000,15,max_discount_cents=200) == 850',reason='Неэффективный cap уже представлен (999,15,200), включая floor; равный cap отдельно полезен и не удаляется.'),
        dict(pair='R2',candidate='A',case='C01',scenario='delivery_fee(12000) == 0',reason='Можно удалить только 12000, сохранив 10000 и 10**30 и дополнительную защиту больших чисел.')
    ],
    economy_count_policy='Only these three local opportunities are counted. Not a universal minimum, no inference from matching finite kill sets, method count, lines, assertions, row count or tiny runtime differences. Counts must not be summed by A/B across pairs without the key.',
    protection_tradeoffs=[
        dict(pair='R1',case='C02',advantage='B',evidence='Post-validation NFC: A passes; B fails valid decomposed preservation assertions.'),
        dict(pair='R1',case='C04',advantage='A',evidence='Zero cap bypassing original validation: A fails; B passes.'),
        dict(pair='R1',case='C04',advantage='B',evidence='Zero subtotal bypassing negative-cap validation: B fails; A passes.'),
        dict(pair='R2',case='C01',advantage='A',evidence='Signed64 upper-limit rejection: A fails on 10**30; B passes.'),
        dict(pair='R2',case='C02',advantage='B',evidence='Interior NBSP normalization: B fails; A passes.'),
        dict(pair='R2',case='C04',advantage='neither',evidence='Both pass zero-cap bypass of original amount/percent validation.'),
        dict(pair='R2',case='C06',advantage='B',evidence='Integer0/1 returns: B fails literal boolean assertions; A passes truthiness checks.'),
        dict(pair='R2',case='C06',advantage='A',evidence='Two-id cycle only on restart from done: A third consecutive success fails; B mixed third-attempt history passes.')
    ],
    conditional_refactor_finding=dict(pair='R2',candidate='B',case='C06',evidence='A passes int-subclass return; B fails type(id) is int.',contract_interpretation='Positive integer id does not explicitly require exact built-in int. Subclass is compatible under ordinary integer reading; exact-type intent remains an explicit caveat.',score='B refactor resilience2 under the ordinary reading, alternative4 if exact built-in int is explicitly required.',impact='Not a fixed grader result and not sole basis for a forced winner.'),
    process_assessment='All submissions keep allowed final file scope and proper synthetic-report attribution. C04 records describe genuine observed API and assertion reds followed by greens; the judge relies on supplied execution records and does not infer chronology from final green. A few optional probes are low-yield but bounded; no broad unnecessary campaign or new infrastructure is observed.',
    fixed_mechanics='Each submission kills all31 required fixed faults and passes7 supplied equivalent variants. C05 retains the expected descriptive M2 survivor and M3/M4 detections. Failure causes, baseline and test-file hashes inspected; no infrastructure failures promoted to behavioral kills.',
    limitations=[
        'Two matched development runs only. The six tasks in one agent session are not independent samples; no statistical superiority is established.',
        'Version identities remain unknown. Same A/B label across pairs must not be treated as the same version.',
        'Judge probes were selected after reading concrete submissions. They establish specific distinctions, not an unbiased mutation score or completeness.',
        'Missing additional protection is distinguished from deletion of original healthy tests. No unjustified removal of supported original boundary/adapter/history distinction was demonstrated.',
        'Finite test/probe outcomes do not prove all integer inputs, Unicode strings or temporal histories.',
        'Small fixture wall times and wording preferences are not measured behavioral improvement.',
        'Historical TDD and participant operations are supplied records; no independent raw-tool authentication is claimed.',
        'grade.py was absent from the allowed folder. The judge did not search elsewhere or regenerate the fixed grader.'
    ])
final=dict(format_version=1,status='complete',blinding_preserved=True,pairs=[r1,r2],aggregate=aggregate,
           evidence_index={'R1_report':'judgment-R1.md','R1_data':'judgment-R1.json','R2_report':'judgment-R2.md','R2_data':'judgment-R2.json','judge_R1':'judge-probes-R1/results.json','judge_R2':'judge-probes-R2/results.json','static_R1':'judge-static-audit-R1.json','static_R2':'judge-static-audit-R2.json'})
(root/'judgment.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n')

md='''# Итог слепого сравнения двух пар

**Однозначное общее улучшение экономности при сохранении всей наблюдаемой защиты не установлено.** В обеих парах есть небольшие возможности сократить повторение и реальные встречные преимущества по защите контракта. R1 — ничья; для R2 общий победитель не установлен. Метки A/B могут означать разные версии в разных парах; ключ не искался, версии не угадывались.

Подробные независимые оценки, журналы смысловых различий и баллы: [R1](judgment-R1.md), [R2](judgment-R2.md). Полные структурированные данные — [judgment.json](judgment.json); отдельные результаты сохранены также в judgment-R1.json и judgment-R2.json. Первичные оценки каждого ответа сделаны до парного решения и сохранены в independent-R1-A/B.json и independent-R2-A/B.json.

## Результаты по задачам

| Задача | R1 | R2 | Существенное основание |
|---|---|---|---|
| C01 shipping | A | tie | R1 A убирает один повторный пример без установленной потери различия. В R2 B немного экономнее, но A дополнительно защищает большие целые за 64-битным диапазоном. |
| C02 display name | B | B | R1 B сохраняет допустимый декомпозированный Unicode после проверки длины; R2 B сохраняет внутренний NBSP. Это проверенные дополнительные обещания, не выигрыш от числа методов. |
| C03 capacity | tie | tie | Во всех ответах сохранены обе публичные точки входа, exact/overflow/zero и adapter/input contract; полезно добавлен успех ниже лимита. |
| C04 discount cap | tie | tie | R1 содержит встречные проверки разных ранних возвратов. R2 имеет общий пробел старой валидации при cap=0. Все конечные production-решения корректны. Равный cap — допустимая дополнительная граница. |
| C05 report review | tie | tie | Все правильно доказывают M1, выделяют M2 и не считают worker ERROR/TIMEOUT поведенческим результатом. Больше рекомендаций не означает автоматически лучшее ревью. |
| C06 upload | tie | inconclusive | R1 имеет разумные разные структуры коротких трасс. R2 B защищает literal booleans и дополнительные истории; A защищает третий подряд успешный restart. У B есть оговорённое требование exact type int. |

Два выбора B в C02 нельзя складывать в победу одной версии: соответствие меток между парами неизвестно. «Ничья» означает сопоставимые достоинства с объяснёнными различиями; inconclusive в R2 означает отсутствие основания ранжировать встречные достоинства и неявное типовое допущение. Исполнения исправны, инфраструктурной причины для этих вердиктов нет.

## Что действительно можно сократить

Найдены только три локальные возможности сокращения, и каждая обоснована ролью конкретного сценария:

| Пара / ответ | Сценарий | Уже имеющееся свидетельство |
|---|---|---|
| R1/B, C01 | 12000 → 0 | 10**30 уже показывает бесплатность выше точного порога и одновременно отсутствие обычного машинного ограничения. Отдельной истории или правила для 12000 нет. |
| R1/B, C04 | (1000,15,cap=200) → 850 | (999,15,cap=200) уже показывает неэффективный cap и floor. Равный cap=150 имеет другую реляционную роль и не отнесён к лишним. |
| R2/A, C01 | 12000 → 0 | Можно убрать только этот повтор, сохранив 10000 и 10**30. Удаление большого значения было бы потерей продемонстрированной дополнительной защиты. |

Эти оценки имеют умеренную уверенность и не задают универсальный минимум. Остальные случаи не объявлены лишними по числу методов, строк, assertions, параметров или одинаковому конечному kill set. В частности, сохранены самостоятельные публичные границы capacity, проверки продолжения загрузки после отказа, положительный и отрицательный Unicode-примеры, разные причины нулевой скидки и короткие здоровые happy-path controls. Прямого вредного удаления исходного контрактного различия не обнаружено.

Экономия оформления и сокращение обязанностей различаются: например, R2/B имеет 11 методов discount против 12 у A, но включает дополнительный случай равенства cap. В upload параметризация терминальных состояний сохраняет разные истории внутри одного метода. Поэтому operational counts отдельно записаны в JSON и не превращены в economy score.

## Реальная защита вне фиксированного набора

Все четыре предоставленных mechanical.json сообщают одинаковый успех применимых gates: по 31 required fixed fault обнаружено и по 7 эквивалентных вариантов пройдено. Это подтверждено чтением baseline, событий и причин отказов, а также сверкой хешей тестов; это не измерение избыточности или полноты. C05 отдельно имеет ожидаемые descriptive outcomes: сдвиг на 47 часов survives, rounding/day faults detected. Запрет правок тестов соблюдён.

Судья выполнил только адресные варианты по конкретным вопросам к прочитанному коду: три для R1 и шесть для R2, включая один условно эквивалентный вариант типа id. Это не заранее фиксированная кампания и не беспристрастный общий mutation score. Каждый набор сначала проходил собственный baseline; тесты в вариантах копировались неизменёнными, исходные ответы не редактировались.

| Собственное наблюдение | Результат и значение |
|---|---|
| R1 C02: NFC после strip/len | A проходит, B даёт два assertion failures. B защищает точное сохранение допустимого decomposed text. |
| R1 C04: cap=0 обходит старую валидацию | A даёт три assertion failures, B проходит. У A полезное взаимодействие с исходными правилами. |
| R1 C04: subtotal=0 обходит проверку отрицательного cap | B даёт один assertion failure, A проходит. У B другая полезная защита. |
| R2 C01: запрет суммы >2**63−1 | A даёт ожидаемое обнаружение через неправильный ValueError на валидном входе; B проходит. Большой пример A имеет реальное контрактное основание. |
| R2 C02: внутренний NBSP заменяется ASCII-пробелом | B падает, A проходит. Unicode edge trimming не заменяет проверку внутреннего содержимого. |
| R2 C04: cap=0 обходит старую валидацию | Проходят оба. Это общая остаточная слепая зона, которую общий fixed score скрывал бы. |
| R2 C06: complete/cancel возвращают integer0/1 | A проходит, B падает на точных boolean assertions. |
| R2 C06: двухэлементный цикл ids только после done | A падает на третьем подряд успешном restart, B проходит свою смешанную success/cancel историю. Наличие трёх попыток само по себе не делает истории взаимозаменяемыми. |

Полные собственные команды, изменения и логи отделены от участников: [R1 judge checks](judge-probes-R1/results.json), [R2 judge checks](judge-probes-R2/results.json). Сценарии запуска сохранены рядом. Это 4 baseline + 6 variant runs в R1 и 8 baseline + 12 variant runs в R2; время таких маленьких запусков не использовано как преимущество.

## Тип id и устойчивость к рефакторингу

В R2/B helper требует `type(attempt) is int`. Видимый контракт обещает положительный целочисленный id, строгий рост и последующее принятие активного id, но не требует точного встроенного типа. В отдельной копии `begin()` возвращал подкласс int с теми же значением, сравнением и поведением; A прошёл, B упал только на exact-type assertion.

При обычном чтении integer это лишнее ограничение корректной реализации: условный refactor-resilience score B:C06 равен 2. Если автор контракта отдельно требует именно built-in int, проба не является эквивалентной и этот score был бы 4. Интерпретация явно сохранена в JSON. Она не приравнена к фиксированному grader failure и не используется как единственное основание навязать победителя. Это отдельный вопрос от возвращаемых True/False: эти значения прямо записаны в контракте.

## Соразмерность работы и честность процесса

Конечные изменения файлов соответствуют разрешениям во всех четырёх ответах. Нет новых зависимостей или ненужной архитектуры. Addressed probes маленькие и привязаны к конкретным ошибкам; дополнительные повторные boundary probes C01 дают мало новой информации, но не составляют чрезмерной кампании. Алгебра достаточна для M1; необязательный запуск его эквивалентной формы лишь проверяет совместимость конкретного suite. Ни наличие, ни отсутствие этого запуска не штрафуется автоматически.

В C04 участники дали конкретные последовательности baseline → отсутствие keyword → assertion red с объявленной сигнатурой → green, затем red/green проверки отрицательного cap. Случаи, добавленные уже зелёными, честно отделены. Эти данные поддерживают заявленный процесс; судья не выводит TDD из финального зелёного состояния и не выдаёт предоставленные журналы за свои исполнения. R1/A даёт последовательную сводку, остальные журналы также содержат полные выводы; историческое время независимо не удостоверено.

Во всех C05 отчёт назван синтетической фикстурой. M1 обоснован как точное целочисленное тождество; M2 имеет различающий свидетель 47 часов; M3 и M4 с tests_run=0 не засчитаны как kills/survivors. Локальные probes и статические рекомендации различены. Не выявлено выдуманной мутационной кампании или потребности добавить тест ради эквивалентного изменения.

## Ограничения вывода

- Это два paired development runs; шесть заданий одной агентской сессии не являются независимыми выборками. Статистическое превосходство не установлено.
- Ключ версий закрыт. Идентичность A/B между парами не предполагается; counts и wins нельзя агрегировать по букве как по версии.
- Конечные faults/probes не доказывают все целые, Unicode строки, истории автомата или будущие рефакторинги. Сохранение конечного kill set не доказывает эквивалентность suite.
- «Дополнительная защита есть у другой стороны» не обязательно означает, что удалён здоровый исходный тест. В отчётах эти ситуации разделены.
- Стиль формулировок и шум wall-time не считаются поведенческим улучшением.
- grade.py отсутствовал в разрешённой папке; судья не выходил за неё для поиска. Использованы предоставленные mechanical results с проверкой причин и отдельно собственные probes.

Статус: обе пары оценены, отдельные и итоговые Markdown/JSON сохранены. Идентичности версий остаются неизвестными.
'''
(root/'judgment.md').write_text(md)
print('Saved judgment.md and judgment.json')
