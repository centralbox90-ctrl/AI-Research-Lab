# Architecture Status

Этот документ описывает только подтверждённое состояние реализации AI Research Lab.

Целевая архитектура определяет ответственности и границы доменов. Статус реализации показывает, насколько эти ответственности представлены в текущем репозитории. Физическая структура каталогов может временно отличаться от целевой доменной структуры.

## Значения статусов

- **Confirmed** — основной сценарий реализован и покрыт автоматическими тестами.
- **Partial** — часть ответственности реализована, но доменный цикл или границы ещё не завершены.
- **Planned** — ответственность определена архитектурой, специализированная реализация отсутствует.
- **Unknown** — состояние не подтверждено кодом и тестами.

Статус Confirmed не означает, что развитие домена завершено.

## Матрица соответствия

| Домен | Architecture Status | Implementation Status | Подтверждённое состояние |
|---|---|---|---|
| Research | Core | Partial | Реализованы сравнительные исследования и полный пользовательский поток validated CampaignDesign JSON → ResearchCampaignPlan → validated registrations → resolved MarketExperimentSpecification → последовательное выполнение → версионированный JSON-артефакт через CLI. |
| Experiment | Core | Partial | Поддерживаются воспроизводимые результаты, планы оценки и исследовательские артефакты. Унифицированный жизненный цикл всех типов экспериментов ещё не завершён. |
| Market Data | Core | Partial | Реализованы загрузчики, generated market data и canonical dataset provider. Legacy-представления используются не во всех сценариях через единый контракт. |
| Calculation | Core | Confirmed | Реализованы индикаторы, их автоматическое обнаружение и вычислительные исследовательские сценарии. |
| Signal | Core | Confirmed | Генерация сигналов и интеграция с существующим execution-контуром присутствуют. Декларативная композиция правил ограничена. |
| Execution | Core | Confirmed | Technical Execution Stabilization завершена: BacktestEngine координирует жизненный цикл позиции, PositionFactory создаёт открытые LONG/SHORT позиции, PositionExitEvaluator определяет выход, TradeFactory формирует закрытые сделки. |
| Analysis | Core | Confirmed | Реализован и протестирован полный сценарий Observation → Evidence → Finding → HypothesisEvaluation. Строгий JSON loader, CLI-команда, presenters, composition roots и пользовательский маршрут общего ResearchCli подключены. |
| Knowledge | Core | Partial | Реализован и протестирован поток KnowledgeCandidate → validation → immutable KnowledgeItem → KnowledgeRevision → versioned InMemoryKnowledgeRepository. Repository сохраняет append-only историю, возвращает latest/version/history и проверяет последовательность версий и UTC-хронологию. KnowledgeApplicabilityQuery поддерживает режимы ALL/ANY, а repository выполняет детерминированный поиск по последним KnowledgeItem. Добавлен immutable KnowledgeContradiction с точными ссылками на версии, fingerprint и конфликтующую applicability. Contradiction detector и repository registration ещё не реализованы. |
| Infrastructure | Supporting | Partial | Реализованы composition roots, CLI-компоненты, presenters, артефакты и CI. Границы инфраструктурных адаптеров продолжают уточняться. |

## Подтверждённый вертикальный срез

Наиболее развитый вертикальный срез проходит через сравнительное исследование индикаторов:

1. получение canonical market dataset;
2. выбор и расчёт индикаторов;
3. выполнение сравнительного исследования;
4. получение воспроизводимого результата;
5. экспорт версионированного исследовательского артефакта;
6. загрузка и проверка схемы артефакта;
7. статистическая оценка по явному evaluation plan;
8. агрегация оценок в immutable evidence;
9. прикладная orchestration через composition root;
10. преобразование Evidence в immutable Finding;
11. формальная оценка набора Findings;
12. запуск и представление результата через общий CLI.

Этот срез подтверждает движение от отдельных вычислений к архитектурному циклу Research → Experiment → Calculation → Analysis.

## Подтверждённые компоненты

### Market Data

- пакет `src/data/`;
- загрузка рыночных данных;
- deterministic generated market data;
- canonical market dataset provider;
- explicit LegacyMarketDataProvider and LegacyMarketDataFrameAdapter boundaries for legacy OHLC DataFrames;
- интеграция сравнительного исследования с MetaTrader 5.

### Calculation

- пакет `src/indicators/`;
- автоматическое обнаружение indicator plugins;
- инвалидирование import cache перед discovery;
- тесты динамического добавления plugin;
- исследовательские расчёты индикаторов.

### Research и Experiment

- существующая изменяемая runtime-модель ResearchCampaign;
- immutable CampaignDesign с детерминированной идентичностью;
- строгий CampaignDesignLoader с проверкой schema version и вычисленного ID;
- CampaignExperimentSpecification и immutable ResearchCampaignPlan;
- детерминированный ResearchPlanner с ограничением Cartesian expansion;
- ResearchCampaignPlanMarketAdapter с проверкой соответствия инструмента и таймфрейма;
- сохранение связи resolved market experiment с исходной плановой спецификацией;
- InMemoryMarketExperimentSpecificationResolver с явными неизменяемыми регистрациями;
- строгий MarketExperimentRegistrationLoader с проверкой plan ID и полного набора;
- RunMarketResearchCampaign с полным разрешением плана до начала выполнения;
- типизированный результат кампании с сохранением порядка и связи с плановыми спецификациями;
- MarketResearchCampaignPresenter и версионированный JSON-артефакт кампании;
- RunMarketResearchCampaignCommand, общий CLI-маршрут и production composition root;
- synchronized CampaignDesign and registration JSON examples with an end-to-end CLI test;
- comparative research application;
- воспроизводимый comparative research result;
- версионированный формат research artifact;
- атомарный экспорт артефактов;
- загрузка, валидация и сравнение артефактов;
- replicated comparative research.

### Analysis

- comparative evaluation plan;
- comparative statistical evaluation model;
- comparative statistical evaluator;
- проверка результата относительно evaluation plan;
- immutable evidence model;
- агрегация сравнительных оценок;
- comparative evidence service и application;
- evidence presenter;
- immutable finding model;
- FindingEvaluator и IndicatorComparativeFindingApplication;
- finding presenter;
- immutable hypothesis evaluation model;
- predeclared hypothesis evaluation plan;
- deterministic HypothesisEvaluator;
- HypothesisEvaluationApplication;
- hypothesis evaluation presenter;
- IndicatorComparativeHypothesisEvaluationApplication;
- строгий comparative hypothesis evaluation JSON loader;
- специализированная CLI-команда;
- пользовательский маршрут общего ResearchCli.

### Knowledge

- immutable KnowledgeCandidate;
- immutable KnowledgeItem с положительной версией;
- immutable KnowledgeRevision с UTC valid_from и обязательной причиной изменения;
- последовательная связь каждой новой revision с непосредственно предыдущей версией;
- KnowledgeCandidateValidator с явными confidence и supporting Findings policy;
- детерминированное преобразование принятого кандидата в KnowledgeItem версии 1;
- version-aware KnowledgeRepository protocol;
- append-only InMemoryKnowledgeRepository с полной revision history;
- операции latest, version и history;
- идемпотентное сохранение одинаковой revision;
- запрет пропуска версий, конфликтующей записи и немонотонного valid_from;
- детерминированное перечисление последних версий знаний;
- сквозной контрактный тест Candidate → validation → KnowledgeItem → KnowledgeRevision → repository;
- типизированный KnowledgeApplicabilityQuery с режимами ALL и ANY;
- нормализация applicability terms и детерминированный matching;
- repository-level find_applicable по последним KnowledgeItem в детерминированном порядке ID;
- immutable KnowledgeContradiction с канонической парой версионированных KnowledgeItem;
- обязательные reason и пересечение conflicting applicability;
- обязательная область применимости;
- ссылки на supporting Findings и HypothesisEvaluation;
- обязательный provenance;
- воспроизводимые fingerprint и schema-versioned serialization;
- отдельные контракты, не изменяющие legacy Knowledge.

### Infrastructure

- composition roots и CLI-команда полного цикла формальной оценки гипотезы;
- presenters, отделённые от прикладных сервисов;
- воспроизводимый `requirements.txt`;
- автоматический запуск `python -m pytest -q`;
- GitHub Actions на Windows и Python 3.13;
- корректное разделение `/data/` и пакета `src/data/`.

## Текущие архитектурные отклонения

### Research orchestration

Существующий ResearchCampaign остаётся изменяемым runtime-контрактом совместимости. Новый поток CampaignDesignLoader, CampaignDesign, ResearchPlanner, строгий registration loader, resolver, adapter и RunMarketResearchCampaign выполняет запланированную кампанию через явные application-границы. MarketResearchCampaignPresenter формирует версионированный JSON-артефакт, RunMarketResearchCampaignCommand загружает согласованные входные документы, а production composition root подключает команду к общему ResearchCli.

### Market Data

Canonical market data ещё не является единственным внутренним представлением во всех подсистемах. Legacy-форматы должны оставаться за адаптерами.

### Execution

Production research sessions используют CanonicalMarketDatasetProvider и PreparedMarketBacktestExecutor. LegacyMarketBacktestExecutor сохранён только как compatibility-контракт. PositionFactory применяет entry slippage и создаёт LONG/SHORT Position. PositionExitEvaluator владеет детерминированными правилами выхода. TradeFactory применяет exit execution и формирует закрытый Trade. PreparedMarketBacktestExecutor передаёт зарегистрированные commission и slippage через ExecutionPolicy. BacktestEngine остаётся orchestration-компонентом и больше не создаёт открытые или закрытые позиции напрямую. Technical Execution Stabilization завершена.

### Legacy Analysis Pipeline

Conclusion и HypothesisDecision используются существующим ResearchEngine и связанными cycle results. Они изолированы как legacy-контракты: новый application-слой не может импортировать их напрямую.

### Knowledge

Immutable KnowledgeCandidate, KnowledgeItem, KnowledgeRevision, KnowledgeCandidateValidator и KnowledgeRepository реализованы как специализированные контракты Knowledge Domain. Существующий mutable Knowledge остаётся legacy-моделью ResearchEngine. InMemoryKnowledgeRepository хранит все KnowledgeRevision без удаления, возвращает latest/version/history, проверяет линейную последовательность и монотонный UTC valid_from. Repository-level find_applicable применяет типизированный KnowledgeApplicabilityQuery только к latest KnowledgeItem и возвращает результат в детерминированном порядке ID. Immutable KnowledgeContradiction регистрирует каноническую пару точных версий KnowledgeItem, их fingerprints, обязательную reason и пересечение applicability. Persistent repository, contradiction rules, detector и repository registration ещё не реализованы.

## Приоритеты развития

1. Добавить явные contradiction rules и детерминированный detector для последних KnowledgeItem.
2. Продолжить внедрение canonical market data через адаптеры.
3. Продолжить изоляцию и поэтапное удаление Legacy Analysis Pipeline.
4. Унифицировать ExperimentExecution для остальных типов экспериментов.

## Критерий обновления

Этот документ необходимо обновлять, когда изменение:

- добавляет новый архитектурный контракт;
- завершает или расширяет вертикальный срез;
- меняет статус домена;
- устраняет архитектурное отклонение;
- добавляет подтверждённый инфраструктурный механизм.

На момент обновления полный набор автоматических тестов успешно проходит локально и в GitHub Actions.