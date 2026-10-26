import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
dims = ['protection','refactor_resilience','economy','scope','reasoning_process']
initial = {x:json.loads((ROOT/f'independent-R2-{x}.json').read_text()) for x in ('A','B')}
mech = {x:json.loads((ROOT/'R2'/x/'mechanical.json').read_text()) for x in ('A','B')}
scores = {x:{c:dict(s) for c,s in initial[x]['scores'].items()} for x in initial}
scores['B']['C01']['protection']=3
scores['A']['C02']['protection']=3
scores['B']['C06']['protection']=3
scores['B']['C06']['refactor_resilience']=2

def ledger(candidate, group, rule, distinction, diagnosis, cost, rationale):
    return dict(candidate=candidate,scenario_group=group,explicit_rule_or_boundary=rule,
                additional_distinction=distinction,useful_diagnostic_separation=diagnosis,
                maintenance_execution_cost=cost,keep_combine_remove_rationale=rationale)

cases=[
 dict(id='C01',name='shipping',winner='tie',confidence='high_for_tradeoff',
      conclusion='У B меньше одного повторного внутреннего примера, у A есть проверенная дополнительная защита неограниченного целого. Сокращение B не равно доказанному общему улучшению.',
      retained=['Отрицательная область (-1/-200), валидный 0','Обе стороны 5000 и 10000 и точные тарифы','Представители 1200 и 7500 внутри платных диапазонов','Порог бесплатности и значение выше него'],
      added={'A':['10**30 — значение за 64-битной границей'], 'B':[]},
      removed={'A':['2400,5500,20000; добавлено 10**30 при сохранённом 12000'],'B':['2400,5500,12000; выше порога сохранено 20000']},
      protection_loss='Ни один не удалил исходное контрактное различие без представителя. Но B не имеет добавленного A свидетельства для больших Python int; это относительная слепая зона, а не доказанная регрессия относительно исходных тестов.',
      residual_gaps=[dict(candidate='B',risk='Ошибочный верхний предел 2**63-1 остаётся незаметным.',evidence='Judge machine_integer_upper_limit: A даёт ValueError в теле теста на 10**30, B проходит 4 метода.')],
      unjustified_scenarios={'A':[dict(scenario='delivery_fee(12000) == 0',count=1,reason='Заявленная роль продолжения бесплатного диапазона уже представлена 10**30. Можно сохранить 10**30 и убрать 12000 без потери именно этой роли.')],'B':[]},
      extra_work='A выполняет old/new probe бесплатной границы. B — old/new probes обеих границ и запрета только -1 (6 запусков ошибочных копий). Дополнительные B проверки ограничены и честно описаны, но не были необходимы для чтения столь явных утверждений; сами по себе не дают очков экономности или защиты всей области.',
      ledger=[
       ledger('A/B','-1,0,4999/5000,9999/10000','Области допустимости и включённые тарифные границы','Отдельные изменения стоимости и запрета','Тарифное имя + подписанная сумма','Короткие прямые входы','Сохранить.'),
       ledger('A/B','1200,7500,-200','Правило действует внутри диапазона','Граница против обычного представителя','subTest показывает конкретный input','По одному представителю','Оправдано; не сокращать до одного значения на ветку.'),
       ledger('A','10000,12000,10**30','Бесплатно без верхней границы','10**30 обнаруживает машинный верхний предел; 12000 повторяет продолжение','Один тарифный метод','Одна необязательная строка 12000','Сохранить 10000/10**30, 12000 можно убрать.'),
       ledger('B','10000,20000','Бесплатность на пороге и выше','Защита продолжения, но нет свидетельства за машинной границей','Простая таблица','Два входа','Разумный конечный набор, однако дополнительная защита A реальна.')]),
 dict(id='C02',name='display_name',winner='B',confidence='high',
      conclusion='B защищает сохранение внутреннего NBSP без отдельного дополнительного метода. A проверяет Unicode whitespace лишь по краям; точная внутренняя нормализация проходит A и падает B.',
      retained=['Все 7 исходных сценариев','Длина 0/1/20/21 после trim, регистр/внутренние ASCII-пробелы, символы против байтов'],
      added={'A':['Unicode edges U+00A0/U+2003','Валидные 20 и недопустимые 21 кодовая точка с combining marks, точное сохранение'],'B':['Те же два класса различий','Внутренний NBSP остаётся NBSP в том же примере краевой очистки']},
      removed={'A':[],'B':[]}, protection_loss='Исходные проверки сохранены. У A остаётся небольшая дополнительная слепая зона внутренней Unicode-нормализации whitespace.',
      residual_gaps=[dict(candidate='A',risk='Замена оставшегося после strip внутреннего NBSP на ASCII space.',evidence='Judge normalize_internal_nbsp: A — 9 OK, B — одно assertion failure Ada Lee != Ada\\xa0Lee.')],
      unjustified_scenarios={'A':[],'B':[]},
      extra_work='A показывает ASCII-only strip исходным и новым набором. B также воспроизводит NFC-нормализацию и честно уточняет, что падение первого assertion не доказывает исполнение следующего. Два B probes адресны и соразмерны; добавлять ещё Unicode-таблицы не требуется.',
      ledger=[
       ledger('A/B','7 исходных сценариев','Очистка, длина, отказ и сохранение','Отдельные обещания не сливаются из-за веток','Имена прежних тестов','Без здоровых удалений','Сохранить.'),
       ledger('A/B','Unicode edges','str.strip() включает Unicode whitespace','ASCII-only trim','Один буквальный expected','Один небольшой тест','Добавление полезно; no-change anchor его не запрещает.'),
       ledger('A/B','Combining marks длины20/21','len не графемы; точное сохранение','Допустимое decomposed имя и отказ следующей длины','Два понятных assertion на границе','Один связный сценарий','Оба обещания полезны, не считать положительный пример дублем.'),
       ledger('B','Внутренний NBSP','Все внутренние символы сохраняются','Selective Unicode-space cleanup; воспроизведён judge probe','Точное сравнение строки','Один символ в уже нужном входе','Сохранить: низкая цена, отдельная защита.')]),
 dict(id='C03',name='capacity',winner='tie',confidence='high',
      conclusion='Одинаковые содержательные улучшения и одинаковая здоровая диагностическая структура. Разница 2+3→5 против 7+2→9 не устанавливает преимущества.',
      retained=['reserve и handle_request отдельно','exact/overflow/zero-at-capacity','Точный результат и схема ответа, неизменность входного словаря'],
      added={'A':['Ниже limit: (2,3,10)→5 в обеих публичных точках','ValueError compatibility и неизменный zero-request payload'],'B':['Ниже limit: (7,2,10)→9 в обеих точках','Те же две дополнительные проверки']},
      removed={'A':[],'B':[]},protection_loss='Не обнаружена.',residual_gaps=[],unjustified_scenarios={'A':[],'B':[]},
      extra_work='Оба показывают: return limit проходит исходные 6 тестов, но даёт два конкретных падения после дополнения. Это прямое свидетельство полезного пробела, без широкого поиска мутаций.',
      ledger=[
       ledger('A/B','Domain exact/overflow/zero','Числовой API и исключение','Включительность, отказ, отдельная допустимость нуля','ReservationTests','Три коротких сценария','Сохранить.'),
       ledger('A/B','Adapter exact/overflow/zero','Самостоятельная публичная граница','Mapping full, поля, исходная занятость и payload','RequestTests','Прямые словари вместо сложного helper','Сохранить; повторение чисел не отменяет обязанностей.'),
       ledger('A/B','Успех ниже limit, два API','Возвращается сумма, не limit','Конкретный дефект return limit и возможная adapter-only ошибка','Число отдельно от поля ответа','По одному добавлению в каждый класс','Оба нужны как поддерживаемые границы.'),
       ledger('A/B','Exception hierarchy и zero-payload','Явные обещания типа/неизменности','Базовый ValueError и особый быстрый путь нуля','Assertions внутри нужного сценария','Две дешёвые проверки','Оправдано.')]),
 dict(id='C04',name='discount_cap',winner='tie',confidence='high',
      conclusion='Оба решения корректны и компактны. B включает полезную точку равенства cap и скидки, сохраняя ясные subTest; A также имеет достаточные выбранные стороны. У обоих один и тот же конкретный остаточный пробел старой валидации при cap=0.',
      retained=['6 исходных тестов без ослабления','Эффективный, неэффективный и нулевой cap','None и omission','Отрицательный cap при обычной скидке, нулевом проценте и нулевой сумме','keyword-only и floor'],
      added={'A':['6 новых методов, неэффективный cap150 при discount149'],'B':['5 новых методов, в таблице cap0/149/200 при discount149; cap149 — точка равенства']},
      removed={'A':[],'B':[]},protection_loss='Исходная защита сохранена. Совместный пробел касается взаимодействия новой ветки cap=0 со старыми отклонениями.',
      residual_gaps=[dict(candidate='A/B',risk='Ранний возврат при cap=0 до проверки subtotal/percent.',evidence='Judge zero_cap_skips_old_validation проходит A (12 методов) и B (11); текущий production обоих валидацию выполняет правильно.')],
      unjustified_scenarios={'A':[],'B':[]},
      extra_work='Оба предоставляют baseline, отсутствующий keyword, содержательный red700!=800, green, затем 3 validation failures до guard и green. Остальные случаи сразу зелёные и не выданы за новые TDD циклы. Необходимости в отдельной повторной campaign нет.',
      ledger=[
       ledger('A/B','Соседние старые тесты','Старый API, валидация и арифметика','Совместимость с исходным контрактом','Старые ясные имена','Переиспользование без декартова произведения','Сохранить; но capped invalid input может иметь отдельную роль.'),
       ledger('A/B','Active/nonbinding/zero/None/keyword-only','Новый cap-contract','Граница 0, ограничивается скидка, форма вызова','A отдельно, B именованные строки cap','Обе структуры малы и понятны','Ни 11, ни 12 методов сами по себе не лучше.'),
       ledger('A/B','Negative cap при positive/zero-percent/zero-subtotal','Запрет не зависит от нулевой скидки','Два разных ранних выхода','subTest(subtotal,percent)','Три обоснованных строки','Не считать одинаковым случаем лишь по вычисленному нулю.'),
       ledger('B','cap149 при discount149','Реляционная точка min','Равенство можно неверно обработать в будущем ветвлении','subTest(cap=149)','Одна дополнительная строка','Допустимое свидетельство, не обязательная квота для A.')]),
 dict(id='C05',name='mutation_report_review',winner='tie',confidence='high',
      conclusion='Оба корректно классифицируют все записи и соблюдают запрет изменений executable files. A даёт больше обоснованных будущих рекомендаций; B аккуратно оставляет большие числа как известное ограничение. Это не измеренное преимущество по поведению готового набора.',
      retained=['Исполняемые файлы и синтетический отчёт неизменны','Существующие здоровые тесты сохраняются','M1 не объявлен дефектом; M3/M4 startup failures не behavioral kills'],
      added={'A':['Рекомендации47/103 и23/100','Negative paid в бесплатном диапазоне','Большой нечётный paid для точной целочисленной арифметики','Исполненный M1 compatibility probe'],'B':['Рекомендации47/101 и23/100','Честное ограничение по большим числам; M1 algebra без запуска']},
      removed={'A':[],'B':[]},protection_loss='Не обнаружена. Тесты намеренно не меняются; M2 survived — предмет ревью.',residual_gaps=[],unjustified_scenarios={'A':[],'B':[]},
      extra_work='A делает M1–M4, B — M2–M4. M1 уже доказан алгебраически; дополнительный запуск A не доказывает общую эквивалентность, но дешёво проверяет совместимость текущего suite. Ни его наличие, ни отсутствие не определяет победу.',
      ledger=[
       ledger('A/B','M1','Тождество для целых','q при p=4q+r','Эквивалентность отделена от fixed status','Алгебра, у A ещё один запуск','Не создавать искусственный kill.'),
       ledger('A/B','M2 и четвертное округление','47h ещё платно, деление вниз','A47/103 ловит nearest и ceil; B47/101 ловит ceil','Один будущий пример сразу имеет две роли','Только рекомендации','Оба обоснованны; не сравнивать числом findings.'),
       ledger('A/B','M3/M4','Half-floor и24h threshold','Ноль исполненных tests в synthetic worker ничего не говорит об assertions','Названы существующие failing tests ручных копий','Новые дубликаты не предлагаются','Правильно сохранять защиту и отдельно диагностировать runner.'),
       ledger('A/B','23h; у A ещё free-band validation и huge integer','Другие стороны явно поддержанных правил','Независимые ранние возвраты/точность','Отдельно помечены code-reasoning, не наблюдённые mutation results','Небольшие будущие примеры, не обязательная campaign','Оправданы; отсутствие этих дополнительных рекомендаций у B не провал четырёх записей.')]),
 dict(id='C06',name='upload',winner='inconclusive',confidence='high_for_observed_tradeoffs',
      conclusion='Защита встречная, а требование точного встроенного типа id у B требует оговорки. B ловит 0/1 вместо False/True и проверяет пустой результат; A ловит двухэлементный цикл id после третьего подряд успеха. Общий winner не навязывается.',
      retained=['Успех, cancel/late/duplicate, idle события','Wrong id и rejected begin с последующим правильным completion','Restart из done и cancelled со свежим id и очисткой result'],
      added={'A':['Три последовательных успешных попытки','Дубликат и foreign id в done, отдельный healthy success'],'B':['Точные boolean returns','Пустая строка как допустимый result','Stale old до и после нового успеха','Три попытки success/cancel/success с двумя старыми id','Restart после rejected begin и завершения исходной попытки','Проверка обоих соседних unknown id; assertion helpers']},
      removed={'A':[],'B':['Отдельный happy-path объединён с suffix duplicate/cancel; его наблюдения сохранены']},
      protection_loss='Исходные наблюдения не потеряны. A не различает integer0/1 и boolean; B не проверяет третью подряд завершённую попытку. Это относительные пробелы конкретных новых историй, а не доказанная полнота другой стороны.',
      residual_gaps=[dict(candidate='A',risk='complete/cancel возвращают 0/1 при правильных state/result.',evidence='Judge numeric_boolean_returns: A 8 OK; B 10 assertion failures в 7 методах.'),dict(candidate='B',risk='Двухэлементный цикл счётчика только при restart из done.',evidence='Judge two_id_cycle_after_success: A падает на third.csv, 1 not greater than2; B7 OK.'),dict(candidate='B',risk='type(attempt) is int не допускает int-подкласс с теми же обещанными свойствами.',evidence='Judge integer_subclass_ids: A8 OK, B8 assertion failures в7 методах. Эквивалентность зависит от явно указанного чтения слова integer; не fixed grader result.')],
      unjustified_scenarios={'A':[],'B':[]},
      extra_work='A проверяет удаление id guard полным suite; B точечно проверяет потерю владельца перед RuntimeError одним релевантным тестом. Оба эксперимента содержательные. Третий запуск у обоих оправдан, но разные истории не заменяют друг друга автоматически.',
      ledger=[
       ledger('A/B','Успех, cancel/late, done/duplicate, idle','Легальный progress и отклонение вне waiting','Разные порядки complete/cancel','A явные assertions, B простой snapshot helper','Оба решения читаемы','Сохранить; меньше methods не значит меньше сценариев.'),
       ledger('A/B','Wrong id и rejected begin затем completion','Сохранение текущей попытки','Проверяется фактическое продолжение, не только state','Именованные причины отказа','Короткие трассы','Не удалять положительное завершение.'),
       ledger('A','Три последовательных успеха','Строго возрастающие id при каждом успешном begin','Done-specific двухэлементный цикл, подтверждённый judge probe','subTest(result=third.csv); при первых сбоях возможны последующие domain errors','Один небольшой цикл со списком previous ids','Третья попытка оправданна; nested subtests чуть усложняют follow-on диагностику, но не скрывают первичный отказ.'),
       ledger('B','Success/cancel/third + оба старых id + пустая строка','Старые ids остаются неактивны; любой string допустим','Смешанная история и empty-result, другой риск чем три done подряд','Подписанные stale ids','Одна дополнительная связная трасса','Оправдано; не заявлять эквивалентным A history.'),
       ledger('B','Restart после rejected begin и success','Следующий id тоже должен возрастать','Ошибочный rejected begin мог испортить счётчик, сохранив активную попытку','Финальный begin helper','Одно событие','Defensible distinction, не считаю лишним повтором normal restart.'),
       ledger('B','assertIs return True/False; type(id) is int','Первые явно заданы; exact builtin int не написан','Boolean-проверки полезны; exact-type может отвергать допустимую реализацию','Общий helper быстро локализует тип','Небольшая централизация с риском сверхконтракта','Сохранить exact booleans; для id предпочесть проверку целочисленного свойства без скрытого exact-type требования.')]),
]

for i,c in enumerate(cases):
    c['scores']={x:scores[x][c['id']] for x in ('A','B')}
    c['independent_initial_scores']={x:initial[x]['scores'][c['id']] for x in ('A','B')}
    c['operational_counts_not_economy_scores']={}
    for x in ('A','B'):
        m=mech[x]['cases'][i]
        c['operational_counts_not_economy_scores'][x]=dict(test_methods=m['baseline']['tests_run'],baseline_passed=m['baseline']['status']=='passed',independent_contract_passed=m['contract']['status']=='passed',scope_passed=m['scope']['passed'],fixed_faults={f['id']:f['verdict'] for f in m['faults']},equivalent_refactors={r['id']:r['passed'] for r in m['refactors']})
    c['maintenance_and_diagnostic_cost']='Отдельно раскрыта в ledger; operational counts не являются economy score.'
    c['evidence']=[f"original-cases/{mech['A']['cases'][i]['case']}/task.md"]+[f"R2/{x}/cases/{mech[x]['cases'][i]['case']}/" for x in ('A','B')]

result=dict(format_version=1,pair='R2',status='complete_for_R2',version_mapping_known=False,
 protocol=['Исходные контракты уже прочитаны для R1 и побайтово сверены с R2.', 'R2/A оценён независимо и сохранён до чтения ответов R2/B.', 'R2/B оценён независимо до парного решения.', 'Шесть адресных вариантов в своих одноразовых копиях по выявленным вопросам; затем сопоставление.'],
 blinding=dict(outside_folder_read=False,network_used=False,delegation=False,version_identity_inferred=False),
 evidence_origins=dict(supplied_mechanical=['R2/A/mechanical.json','R2/B/mechanical.json'],supplied_participant_records=['R2/A/execution.md','R2/B/execution.md','R2/A/probes/','R2/B/probes/'],judge_executed=['judge-probes-R2/run_focused.py','judge-probes-R2/results.json'],judge_static='judge-static-audit-R2.json'),
 rubric_validation=[
  'grade.py не предоставлен в доступной папке; вне её поиск запрещён. Использованы supplied mechanical events и собственные узкие probes, без выдачи последних за фиксированный grader.',
  'Рубрика не задаёт минимальное число методов, обязательность huge integer примера или quota новых Unicode тестов. При этом конкретный проверенный новый дефект за фиксированным набором учитывается как дополнительное свидетельство.',
  'Равенство cap является допустимой реляционной границей, но не скрытым обязательным тестом. Общий cap0/old-validation пробел установлен отдельным вариантом, а не числом тестов.',
  'Точные True/False написаны в контракте. Возвращаемый begin id описан как положительный целочисленный; требование type(id) is int отсутствует. Обычное чтение допускает int-подкласс с теми же свойствами. Чтобы не скрыть интерпретацию, refactor score B:C06=2 указан условно; если автор контракта требует exact builtin int, эта проба не эквивалентна и соответствующий score был бы4. Проба не засчитана в fixed-fault kill score и не используется одна для навязанного winner.',
  'C06 не требует все комбинации терминальных состояний и все длины трасс. Однако три done подряд и смешанная success/cancel история действительно различают разные нарушения возрастающих ids.',
  'C05 review-only: M2 survival описывает старый suite, не провал ответа. Ни количество будущих рекомендаций, ни исполнение эквивалентного M1 не обязательны.',
  'TDD подтверждается конкретными предоставленными последовательностями и выводами, а не финальным green. Историческое время судья не аутентифицировал и не заявляет личного присутствия при этих запусках.'
 ],
 mechanical_assessment=dict(all_applicable_gates_passed=True,required_fixed_faults_killed_each=31,equivalent_refactors_passed_each=7,C05_descriptive=dict(free_starts_one_hour_early='SURVIVED',day_threshold_late='KILLED',half_fee_rounded_up='KILLED'),failure_cause_review='Проверены body assertion/domain failures, положительный baseline/discovery, отсутствие skips и expected failures и неизменность тестов. У A:C06 некоторые поздние RuntimeError следуют за более ранним поведенческим провалом той же трассы; это не discovery/setup и не самостоятельное преимущество по числу kills.'),
 judge_checks=json.loads((ROOT/'judge-probes-R2/results.json').read_text()),
 score_adjustments_after_independent_assessment=[dict(candidate='B',case='C01',dimension='protection',before=4,after=3,reason='Concrete upper-limit fault survives.'),dict(candidate='A',case='C02',dimension='protection',before=4,after=3,reason='Concrete internal-NBSP normalization survives.'),dict(candidate='B',case='C06',dimension='protection',before=4,after=3,reason='Concrete done-specific two-id cycle survives.'),dict(candidate='B',case='C06',dimension='refactor_resilience',before=3,after=2,conditional=True,reason='Int-subclass return fails although positive integer semantics are preserved under the ordinary integer reading.')],
 conditional_scores=[dict(candidate='B',case='C06',dimension='refactor_resilience',score=2,assumption='Integer id permits int subclass preserving all named public behavior.',alternative_score=4,alternative_assumption='Contract owner explicitly requires exact built-in int; that is not stated in supplied task.')],
 cases=cases,
 aggregate=dict(winner='inconclusive',case_verdicts={c['id']:c['winner'] for c in cases},rationale='R2 содержит неупорядочиваемые одним счётчиком различия: B немного экономнее C01, но A обнаруживает большой допустимый integer; B сильнее C02; C03–C05 сопоставимы; в C06 есть встречная защита и явно оговорённое exact-type предположение. Нет достаточного основания объявить один ответ общим победителем. Это не инфраструктурная неопределённость: исполнения исправны.',avoidable_scenarios_count=dict(A=1,B=0),weighted_total_used=False),
 limitations=['Метки A/B нельзя связывать с R1 или версиями без закрытого ключа.', 'Шесть задач в одной сессии не независимые выборки; по двум matched pairs не устанавливается статистическая superiority.', 'Конечные фиксированные faults и шесть judge variants не являются полной mutation campaign.', 'Время малых fixtures не оценивалось как выигрыш; prose preferences не считаются behavioral improvement.', 'Все участнические outputs остаются supplied evidence; собственные probes и static audit имеют отдельные пути.', 'C06 exact-type caveat должен сохраняться в любом последующем агрегировании.'])
(ROOT/'judgment-R2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

lines=['# Слепое сравнение R2','',
 '**Общий победитель R2 не установлен (inconclusive).** B немного экономнее в доставке, но A защищает большой допустимый integer; B дополнительно защищает внутренний NBSP. В загрузке есть встречные преимущества и отдельное неявное требование точного типа id у B. Исполнения исправны: неопределённость связана с оценкой разных достоинств и интерпретацией контракта, а не с окружением.','',
 '## Независимость и доказательства','',
 'Оценки A и B сначала сохранены отдельно в `independent-R2-A.json` и `independent-R2-B.json`. A оценивался до чтения ответов B. Метки не связывались с R1 и версиями. Использованы только разрешённая папка, исходные условия, ответы и предоставленные журналы. R1 уже зафиксирована отдельными файлами и не переписана.','',
 'Все applicable mechanical gates проходят: по 31 required fixed fault обнаружено и по 7 equivalent variants проходят. Baseline содержательно выполняется, тесты неизменны, ошибки относятся к assertions или доменным исключениям в теле. C05 имеет описательные outcomes: M2 survived, M3/M4 faults killed. Это review-only задача. `judge-static-audit-R2.json` подтверждает разрешённые изменения и совпадение хешей тестов с mechanical.','',
 'Предоставленные `R2/*/execution.md` и `probes` не считаются запусками судьи. Собственные действия: `PYTHONDONTWRITEBYTECODE=1 python3 judge-probes-R2/run_focused.py`; 8 baseline и 12 variant suite-runs в новых копиях. Точные команды, изменения, каталоги и полные логи находятся в `judge-probes-R2/results.json` и соседних копиях. Candidate source hashes до/после совпадают; тесты не изменялись.','',
 '| Judge variant | A | B | Значение |','|---|---|---|---|',
 '| Предел суммы 2**63−1 | ValueError в теле на 10**30 | Проходит | A защищает explicit unlimited domain дополнительным примером. |',
 '| Внутренний NBSP → обычный пробел после strip | Проходит | 1 assertion failure | B защищает сохранение внутреннего Unicode whitespace. |',
 '| cap=0 возвращается до старой валидации | Проходит | Проходит | Общий пробел взаимодействия; текущий production верен. |',
 '| complete/cancel возвращают integer0/1 | Проходит | 10 assertion failures | B защищает точно обещанные False/True. |',
 '| Счётчик циклически сбрасывается только при restart из done | Падение на третьем успехе | Проходит | Три успеха A дают отдельную защиту по сравнению со смешанной историей B. |',
 '| Возврат id как int-подкласса без иных изменений | Проходит | 8 assertion failures | B требует exact builtin type; эквивалентность этой пробы явно оговорена ниже. |','',
 '## Проверка рубрики и неопределённых допущений','']
for n in result['rubric_validation']:lines += ['- '+n]
lines += ['', '## Измерения 0–4','', 'Порядок: защита / refactor resilience / экономность / scope / reasoning/process. Суммарный взвешенный score не применяется. Первичные оценки и причины последующих поправок сохранены в JSON.', '', '| Случай | A | B | Выбор |','|---|---|---|---|']
for c in cases:
    b=' / '.join(str(scores['B'][c['id']][d]) + ('*' if c['id']=='C06' and d=='refactor_resilience' else '') for d in dims)
    lines += [f"| {c['id']} {c['name']} | {' / '.join(str(scores['A'][c['id']][d]) for d in dims)} | {b} | {c['winner']} |"]
lines += ['', '*C06 B: resilience2 при обычном чтении integer как допускающего int-подкласс. Если отдельно установлен exact built-in int, этот условный штраф исчезает и resilience4. Это допущение не скрыто и не превращено в безусловный fixed grader failure.', '']
for c in cases:
    lines += [f"## {c['id']} — {c['name']}: {c['winner']}",'',c['conclusion'],'',
      '**Сохранено:** '+'; '.join(c['retained'])+'.','',
      '**Добавлено A:** '+('; '.join(c['added']['A']) or 'нет')+'.','',
      '**Добавлено B:** '+('; '.join(c['added']['B']) or 'нет')+'.','',
      '**Удаления/объединения:** A — '+('; '.join(c['removed']['A']) or 'нет')+'; B — '+('; '.join(c['removed']['B']) or 'нет')+'.','',
      '**Защита:** '+c['protection_loss'],'',
      '**Дополнительная работа:** '+c['extra_work'],'',
      '| Вариант / группа | Явное правило | Дополнительное различие | Диагностика | Цена | Решение |','|---|---|---|---|---|---|']
    for r in c['ledger']:
      vals=[r['candidate']+': '+r['scenario_group'],r['explicit_rule_or_boundary'],r['additional_distinction'],r['useful_diagnostic_separation'],r['maintenance_execution_cost'],r['keep_combine_remove_rationale']]
      lines += ['| '+' | '.join(v.replace('|','\\|') for v in vals)+' |']
    lines += ['']
    avoid=[f"{x}: {v['scenario']} — {v['reason']}" for x in ('A','B') for v in c['unjustified_scenarios'][x]]
    lines += ['**Обоснованные возможности сокращения:** '+(' '.join(avoid) if avoid else 'не выявлены.'),'']
    for gap in c['residual_gaps']:lines += [f"**Остаточный пробел {gap['candidate']}:** {gap['risk']} {gap['evidence']}",'']
lines += ['## Вывод и ограничения','',result['aggregate']['rationale'],'',
          'Одна возможность сокращения у A — `12000` в C01 при уже сохранённом `10**30`. Это не означает, что весь набор B лучше: A можно убрать эту строку, сохранив защиту больших чисел. В C04 меньше методов B содержит дополнительную точку равенства, а в C06 7 методов B содержат параметризованные истории; operational method counts не являются числом полезных обязанностей.','']
for l in result['limitations']:lines += ['- '+l]
lines += ['', 'Статус: **R2 оценена.**', '']
(ROOT/'judgment-R2.md').write_text('\n'.join(lines))
print('Saved judgment-R2.md and judgment-R2.json')
