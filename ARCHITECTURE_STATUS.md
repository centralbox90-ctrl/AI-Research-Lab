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
| Knowledge | Core | Partial | Реализован и протестирован поток KnowledgeCandidate → validation → immutable KnowledgeItem → KnowledgeRevision → versioned InMemoryKnowledgeRepository. Repository сохраняет append-only историю, возвращает latest/version/history и проверяет последовательность версий и UTC-хронологию. KnowledgeApplicabilityQuery поддерживает режимы ALL/ANY, а repository выполняет детерминированный поиск по последним KnowledgeItem. Добавлены immutable KnowledgeContradiction, KnowledgeContradictionRule и KnowledgeContradictionDetector. Detector применяет явные rules только к latest KnowledgeItem, учитывает пересечение applicability и возвращает результат в детерминированном порядке ID. InMemoryKnowledgeRepository выполняет append-only регистрацию KnowledgeContradiction, проверяет точные сохранённые версии и fingerprints и возвращает детерминированные списки. Добавлены immutable KnowledgeRelation и отдельный KnowledgeRelationRepository. InMemoryKnowledgeRelationRepository проверяет точные версии и fingerprints endpoints, сохраняет relations append-only и идемпотентно, а также выполняет детерминированные list/outgoing/incoming/relations_for с фильтрами версии и типа. Добавлен отдельный KnowledgeGraph read model с типизированными направлениями, детерминированными neighbors и breadth-first traversal с ограничением глубины, фильтрами и защитой от циклов. KnowledgeGraphRelationRegistrar автоматически проецирует уже сохранённые KnowledgeContradiction и KnowledgeRevision в идемпотентные relations contradicts и supersedes. KnowledgeGraphSnapshot фиксирует immutable набор точных версий KnowledgeItem и KnowledgeRelation, проверяет ссылочную целостность endpoints, канонизирует порядок и предоставляет schema v1 JSON и детерминированный fingerprint. Добавлен immutable KnowledgeGap с типами isolated_item, unsupported_item и unresolved_contradiction, точными ссылками на KnowledgeItem, applicability, причиной и fingerprint исходного snapshot. KnowledgeGapDetector анализирует KnowledgeGraphSnapshot без semantic heuristics, исключает superseded versions и детерминированно выявляет isolated, unsupported и unresolved contradiction gaps. Добавлен immutable ResearchRecommendation с типизированным priority, исследовательским вопросом, rationale, applicability из точного KnowledgeGap, полной gap provenance, schema v1 и детерминированным fingerprint. ResearchRecommendationGenerator применяет фиксированные templates по KnowledgeGapType, назначает low/medium/high priority и выполняет пакетную дедупликацию с детерминированным priority order. ResearchRecommendationQuestionAdapter преобразует рекомендацию в legacy ResearchQuestion, использует внедрённые clock и ID factory, нормализует created_at в UTC и сохраняет rationale, priority, applicability и fingerprints provenance в description. GenerateResearchQuestionsFromKnowledgeSnapshot оркестрирует полный поток KnowledgeGraphSnapshot → KnowledgeGapDetector → ResearchRecommendationGenerator → ResearchRecommendationQuestionAdapter, сохраняет priority order и отклоняет повторяющиеся ID вопросов. Production composition root build_knowledge_research_question_application связывает готовый сервис с system_utc_clock и fingerprint_research_question_id; ID основан на полном fingerprint рекомендации. KnowledgeGraphSnapshotLoader строго загружает schema v1 JSON, проверяет полный набор полей, вычисляемые KnowledgeItem fingerprints и точные relation endpoints, после чего восстанавливает канонический immutable snapshot. Presenter present_research_questions формирует versioned artifact knowledge_research_questions с fingerprint исходного snapshot, количеством вопросов и сохранением priority order. GenerateResearchQuestionsFromKnowledgeSnapshotCommand загружает snapshot, запускает application-service и возвращает deterministic JSON в pretty/compact режимах. Общий ResearchCli предоставляет маршрут generate-knowledge-research-questions с обязательным snapshot path, pretty/compact JSON, контролируемыми exit codes и обработкой ошибок загрузки. Production build_research_cli связывает маршрут с готовыми loader, application-service и presenter; end-to-end тест подтверждает полный file-to-JSON поток. SqliteKnowledgeRepository реализует persistent append-only revision history и contradictions, восстанавливает immutable domain objects с проверкой fingerprints, сохраняет sequence/UTC invariants и поддерживает детерминированные запросы после повторного открытия базы. SqliteKnowledgeRelationRepository реализует persistent append-only relations, проверяет точные сохранённые версии и fingerprints endpoints, обеспечивает идемпотентное сохранение и детерминированные запросы после повторного открытия базы. |
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
- persistent SqliteKnowledgeRepository, реализующий KnowledgeRepository protocol;
- persistent SqliteKnowledgeRelationRepository, реализующий KnowledgeRelationRepository protocol;
- SQLite append-only relation storage с проверкой точных endpoint versions и fingerprints;
- детерминированные list_all, outgoing, incoming и relations_for после повторного открытия базы;
- SQLite append-only revision history с транзакционной проверкой sequence и UTC chronology;
- persistent contradictions с foreign keys на точные KnowledgeItem versions;
- восстановление KnowledgeRevision и KnowledgeContradiction с проверкой schema и fingerprints;
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
- immutable KnowledgeContradictionRule с канонической парой нормализованных statements;
- точный case-insensitive rule matching без semantic heuristics;
- KnowledgeContradictionDetector над latest KnowledgeRepository.list_all();
- детерминированный pair enumeration с applicability overlap filtering;
- append-only регистрация KnowledgeContradiction по fingerprint;
- идемпотентное повторное сохранение одинакового противоречия;
- проверка точных сохранённых версий и fingerprints ссылочных KnowledgeItem;
- детерминированные list_contradictions и contradictions_for;
- immutable KnowledgeRelation между точными версиями KnowledgeItem;
- KnowledgeRelationType для supports, contradicts, extends, refines, supersedes и derived_from;
- направленная семантика relations и канонический порядок endpoints для contradicts;
- отдельный KnowledgeRelationRepository protocol;
- append-only InMemoryKnowledgeRelationRepository с идемпотентным сохранением по fingerprint;
- проверка точных сохранённых версий и fingerprints обоих relation endpoints;
- детерминированные list_all, outgoing, incoming и relations_for с фильтрами версии и типа;
- отдельный KnowledgeGraph read model, не изменяющий legacy ResearchGraph;
- типизированные направления outgoing, incoming и both;
- детерминированные neighbors по точным версиям KnowledgeItem;
- breadth-first traversal с max_depth, relation type filtering, дедупликацией и защитой от циклов;
- application-сервис KnowledgeGraphRelationRegistrar;
- проекция зарегистрированного KnowledgeContradiction в relation contradicts;
- проекция сохранённой superseding KnowledgeRevision в relation supersedes;
- обязательный порядок domain storage → graph projection и идемпотентная повторная регистрация;
- immutable KnowledgeGraphSnapshot с точными версиями graph items и relations;
- проверка ссылочной целостности relation endpoints внутри snapshot;
- канонический порядок items/relations и создание snapshot через KnowledgeGraph;
- schema v1 JSON serialization и детерминированный fingerprint snapshot;
- immutable KnowledgeGap для воспроизводимого результата gap detection;
- типы isolated_item, unsupported_item и unresolved_contradiction;
- канонические ссылки на точные KnowledgeItem и обязательная cardinality по типу gap;
- нормализованная applicability, причина, fingerprint исходного snapshot и schema v1 serialization;
- KnowledgeGapDetector над immutable KnowledgeGraphSnapshot;
- явные topology rules для isolated_item и unsupported_item через supports/derived_from;
- unresolved_contradiction только для активных пересекающихся applicability;
- исключение superseded versions, дедупликация и детерминированный порядок KnowledgeGap;
- immutable ResearchRecommendation, основанный на точном KnowledgeGap;
- типизированные приоритеты low, medium и high;
- нормализованные research question и rationale с applicability из gap;
- полная gap provenance, schema v1 serialization и детерминированный fingerprint recommendation;
- детерминированный ResearchRecommendationGenerator без semantic heuristics;
- фиксированные question/rationale templates для каждого KnowledgeGapType;
- priority mapping isolated → low, unsupported → medium, contradiction → high;
- пакетная дедупликация и детерминированная сортировка рекомендаций по priority;
- application-адаптер ResearchRecommendation → legacy ResearchQuestion;
- обязательные injected clock и ID factory без скрытого времени и случайного UUID;
- UTC-нормализация created_at и сохранение rationale, priority, applicability и fingerprints provenance в description;
- application-сервис GenerateResearchQuestionsFromKnowledgeSnapshot;
- явная оркестрация KnowledgeGapDetector → ResearchRecommendationGenerator → ResearchRecommendationQuestionAdapter;
- сохранение priority order, один ResearchQuestion на рекомендацию и запрет повторяющихся question ID;
- production composition root build_knowledge_research_question_application;
- явная default policy system_utc_clock с timezone-aware UTC;
- стабильный question ID из полного fingerprint ResearchRecommendation;
- strict KnowledgeGraphSnapshotLoader для schema v1 JSON;
- проверка обязательных и неизвестных полей, массивов и типов endpoint references;
- сверка вычисляемых KnowledgeItem fingerprints, точных relation endpoints и детерминированный round-trip;
- JSON presenter knowledge_research_questions с artifact version и snapshot fingerprint;
- GenerateResearchQuestionsFromKnowledgeSnapshotCommand для полного file-to-JSON потока;
- pretty/compact deterministic JSON без изменения priority order вопросов;
- маршрут общего ResearchCli generate-knowledge-research-questions с обязательным snapshot path;
- production composition root для loader → application-service → presenter;
- end-to-end CLI-тест полного KnowledgeGraphSnapshot file-to-ResearchQuestion JSON потока;
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

Immutable KnowledgeCandidate, KnowledgeItem, KnowledgeRevision, KnowledgeCandidateValidator и KnowledgeRepository реализованы как специализированные контракты Knowledge Domain. Существующий mutable Knowledge остаётся legacy-моделью ResearchEngine. InMemoryKnowledgeRepository хранит все KnowledgeRevision без удаления, возвращает latest/version/history, проверяет линейную последовательность и монотонный UTC valid_from. Repository-level find_applicable применяет типизированный KnowledgeApplicabilityQuery только к latest KnowledgeItem и возвращает результат в детерминированном порядке ID. Immutable KnowledgeContradiction регистрирует каноническую пару точных версий KnowledgeItem, их fingerprints, обязательную reason и пересечение applicability. KnowledgeContradictionRule явно задаёт две несовместимые нормализованные формулировки и выполняет точный case-insensitive matching. KnowledgeContradictionDetector получает latest items через KnowledgeRepository, проверяет уникальность knowledge ID и rules, учитывает applicability overlap и возвращает канонически упорядоченные KnowledgeContradiction. InMemoryKnowledgeRepository хранит KnowledgeContradiction append-only по fingerprint, проверяет точные версии и fingerprints ссылочных KnowledgeItem, сохраняет противоречия после superseding и предоставляет детерминированные list_contradictions/contradictions_for. KnowledgeRelation фиксирует типизированную направленную связь между точными версиями KnowledgeItem, нормализует reason и предоставляет schema-versioned serialization и fingerprint; contradicts канонизирует endpoints. Отдельный InMemoryKnowledgeRelationRepository хранит relations append-only по fingerprint, валидирует endpoints через KnowledgeRepository и поддерживает детерминированные запросы по ID, версии и типу relation. KnowledgeGraph является отдельным read model над KnowledgeRelationRepository, вычисляет детерминированных neighbors и выполняет ограниченный breadth-first traversal с защитой от циклов. KnowledgeGraphRelationRegistrar принимает только уже сохранённые domain records, проецирует KnowledgeContradiction в contradicts, а superseding KnowledgeRevision — в supersedes, сохраняя точные версии, причины и идемпотентность. KnowledgeGraphSnapshot фиксирует immutable набор точных версий KnowledgeItem и KnowledgeRelation, проверяет ссылочную целостность endpoints, канонизирует порядок и предоставляет schema v1 JSON и детерминированный fingerprint. Добавлен immutable KnowledgeGap с типами isolated_item, unsupported_item и unresolved_contradiction, точными ссылками на KnowledgeItem, applicability, причиной и fingerprint исходного snapshot. KnowledgeGapDetector анализирует KnowledgeGraphSnapshot без semantic heuristics, исключает superseded versions и детерминированно выявляет isolated, unsupported и unresolved contradiction gaps. Добавлен immutable ResearchRecommendation с типизированным priority, исследовательским вопросом, rationale, applicability из точного KnowledgeGap, полной gap provenance, schema v1 и детерминированным fingerprint. ResearchRecommendationGenerator применяет фиксированные templates по KnowledgeGapType, назначает low/medium/high priority и выполняет пакетную дедупликацию с детерминированным priority order. ResearchRecommendationQuestionAdapter преобразует рекомендацию в legacy ResearchQuestion, использует внедрённые clock и ID factory, нормализует created_at в UTC и сохраняет rationale, priority, applicability и fingerprints provenance в description. GenerateResearchQuestionsFromKnowledgeSnapshot оркестрирует полный поток KnowledgeGraphSnapshot → KnowledgeGapDetector → ResearchRecommendationGenerator → ResearchRecommendationQuestionAdapter, сохраняет priority order и отклоняет повторяющиеся ID вопросов. Production composition root build_knowledge_research_question_application связывает готовый сервис с system_utc_clock и fingerprint_research_question_id; ID основан на полном fingerprint рекомендации. KnowledgeGraphSnapshotLoader строго загружает schema v1 JSON, проверяет полный набор полей, вычисляемые KnowledgeItem fingerprints и точные relation endpoints, после чего восстанавливает канонический immutable snapshot. Presenter present_research_questions формирует versioned artifact knowledge_research_questions с fingerprint исходного snapshot, количеством вопросов и сохранением priority order. GenerateResearchQuestionsFromKnowledgeSnapshotCommand загружает snapshot, запускает application-service и возвращает deterministic JSON в pretty/compact режимах. Общий ResearchCli предоставляет маршрут generate-knowledge-research-questions с обязательным snapshot path, pretty/compact JSON, контролируемыми exit codes и обработкой ошибок загрузки. Production build_research_cli связывает маршрут с готовыми loader, application-service и presenter; end-to-end тест подтверждает полный file-to-JSON поток. SqliteKnowledgeRepository реализует persistent append-only revision history и contradictions, восстанавливает immutable domain objects с проверкой fingerprints, сохраняет sequence/UTC invariants и поддерживает детерминированные запросы после повторного открытия базы. SqliteKnowledgeRelationRepository реализует persistent append-only relations, проверяет точные сохранённые версии и fingerprints endpoints, обеспечивает идемпотентное сохранение и детерминированные запросы после повторного открытия базы.

## Статус архитектурной консолидации

На commit `c0f80eb` основной этап архитектурной консолидации
подтверждён production wiring и автоматическими тестами.

Завершены:

- фактический Architecture Inventory;
- ADR-001 — ADR-006;
- Knowledge feature freeze;
- классификация Application Layer;
- явный `src.application.public_api`;
- минимальный immutable `ExperimentExecution` lifecycle;
- append-only SQLite snapshots технического выполнения;
- transactional validation append-only истории ExperimentExecution: обязательный первый PENDING, разрешённые transitions, immutable identity и запрет snapshots после terminal state;
- read-time validation persisted `ExperimentExecution` history: непрерывный sequence, согласованные status/payload и execution identity, обязательный первый `PENDING` и допустимые transitions;
- production CLI acceptance для повреждённой persisted execution history: exit code `1`, пустой stdout и диагностический stderr без выхода исключения за transport boundary;
- integrity-aware `get_latest`: последний `ExperimentExecution` возвращается только после проверки полной persisted history;
- integrity-aware `list_execution_ids`: каждая обнаруженная identity возвращается только после проверки полной persisted history;
- production CLI acceptance повреждённого execution listing: exit code `1`, пустой stdout и диагностический stderr без публикации частичного каталога;
- public read-only `GetExperimentExecutionHistory`;
- public read-only `ListExperimentExecutions`;
- production CLI query для полной истории технического выполнения;
- production CLI query для обнаружения сохранённых execution identities;
- production execution tracking для одиночного market research;
- end-to-end acceptance test production market research path: run → validated stored envelope → execution listing → append-only execution history;
- end-to-end acceptance test failed market execution path: persisted `PENDING → RUNNING → FAILED` history без создания research artifact;
- controlled `run-research` mapping для technical `RuntimeError`: exit code `1`, пустой stdout и диагностический stderr;
- production preparation failure tracking для dataset/context preparation: `PENDING → FAILED` со stage `PREPARATION` без перехода в `RUNNING`;
- SQLite acceptance test подтверждает восстановление persisted preparation failure через CLI после повторного открытия database;
- production execution tracking для Market Research Campaign;
- controlled `run-market-research-campaign` mapping для вложенного technical `RuntimeError`: exit code `1`, пустой stdout и диагностический stderr;
- controlled `run-comparative-hypothesis-evaluation` mapping для technical `RuntimeError`: exit code `1`, пустой stdout и диагностический stderr;
- production SQLite acceptance для failed comparative execution: persisted `PENDING → RUNNING → FAILED` с correlation, fingerprints и failure provenance;
- production execution tracking для comparative analysis;
- deterministic specification fingerprints;
- reproducимые independent generated market-data periods;
- явное разделение technical execution и scientific interpretation;
- общий `ResearchArtifactEnvelope` на границах хранения и обмена;
- immutable и идемпотентная SQLite persistence research artifacts по `result_id`;
- integrity-aware public read path для сохранённых `ResearchArtifactEnvelope`;
- strict top-level field contract для serialized `ResearchArtifactEnvelope`;
- controlled CLI error mapping для повреждённых stored artifact envelopes;
- market research envelope;
- comparative HypothesisEvaluation envelope;
- Knowledge research-question envelope;
- Market Research Campaign envelope;
- integrity-aware Market Research Campaign artifact reader;
- lifecycle correlation без подмены domain identities;
- явная `KnowledgePromotionPolicy`;
- production promotion в append-only Knowledge repositories;
- contradiction detection и relation registration;
- repository-backed KnowledgeGraphSnapshot;
- KnowledgeGap → ResearchRecommendation → ResearchQuestion;
- production Knowledge feedback path без подготовленного snapshot-файла;
- legacy migration policy и перечисленные legacy boundaries.

Основной production lifecycle существует как набор явных Application
use cases и internal coordinators.

Единый `ResearchLifecycle` aggregate, WorkflowEngine, универсальный
pipeline или конфигурируемый orchestration mechanism не создавались.

Composition roots выбирают adapters, версии producer и policy objects,
но не принимают научные решения.

Research Domain не управляет retries, scheduling, worker leases,
heartbeat или очередями.

Добавление нового индикатора остаётся локальным plugin-изменением:
один production module в `src/indicators/implementations`, экспортирующий
стандартный immutable `INDICATOR`. Catalog, discovery, composition roots,
Research Engine, Observation Layer и существующие indicators при этом
не изменяются.

### Выполненные критерии консолидации

1. Market и comparative experiments используют явный execution
   lifecycle.
2. Основные production results проходят через общий artifact envelope.
3. Analysis → Knowledge → ResearchQuestion работает без ручного
   snapshot-файла.
4. Публичные Application use cases перечислены явным allowlist.
5. Composition roots не содержат lifecycle transitions.
6. Research Domain не управляет runtime infrastructure.
7. Knowledge feature freeze соблюдается.
8. Legacy boundaries перечислены и защищены migration policy.
9. Specification, data periods, code version, environment fingerprints
   и artifacts обеспечивают воспроизводимость production paths.
10. Внешний adapter может быть добавлен поверх Application contracts
    без изменения Domain Layer.

### Сохраняющиеся ограничения

Следующие ограничения не блокируют завершение консолидации:

- standalone Evidence и Finding artifacts сохраняют legacy contracts;
- некоторые envelopes возвращаются через CLI без отдельного artifact
  store;
- production contradiction rules пока представлены пустой явной
  конфигурацией;
- correlation между отдельными use cases передаётся клиентом явно;
- legacy `ResearchEngine` и mutable Research models остаются
  изолированными compatibility boundaries;
- полный lifecycle намеренно не объединён в один универсальный
  Application use case;
- Production HTTP boundary использует mandatory Bearer authentication,
  loopback-only Waitress, Caddy TLS templates и operational runbook;
  fine-grained authorization, public multi-user и SaaS-функции
  отложены до отдельного подтверждённого product phase.

## Artifact persistence decision gate

Audit baseline: `d2da1d4`.

Публичное чтение сохранённых market research cycles теперь использует
единую integrity policy.

Подтверждены:

- полная validation `ResearchArtifactEnvelope`;
- повторное вычисление payload fingerprint;
- проверка artifact type и payload schema version;
- typed validation modern и legacy payload;
- совпадение storage key с `result_id` внутри payload;
- fail-closed listing без публикации частично доверенного списка;
- единая Application integrity error;
- контролируемое отображение corruption через CLI, HTTP и MCP.

Legacy compatibility допускает отличающееся представление данных, но не
ослабляет требования целостности.

### Матрица persistence-решений

| Artifact boundary | Producer и envelope | Store и validated reader | Решение |
|---|---|---|---|
| `market_research_cycle` | Production producer и envelope подключены | SQLite store, validated public reader, CLI, HTTP и MCP | Required и completed |
| `market_research_campaign` | Production envelope и specialized loader существуют | Persisted reopen consumer отсутствует | Deferred до подтверждения долговременного чтения |
| `hypothesis_evaluation` | Production envelope и specialized loader существуют | Store и public persisted consumer отсутствуют | Deferred; первый кандидат при появлении reopen, audit или delayed Knowledge promotion scenario |
| `knowledge_research_questions` | Production envelope и specialized loader существуют | Результат воспроизводится из authoritative Knowledge repositories | Deferred; отдельный store не требуется |
| `indicator_comparative_research` | Legacy file producer, exporter и loader используются | Validated file-based comparison consumer существует | Сохранить специализированную file boundary без общего SQLite store |
| standalone `indicator_comparative_evidence` и `indicator_comparative_finding` | Specialized presenters существуют | Самостоятельный persisted consumer отсутствует | Отдельную persistence не добавлять |
| serialized `ResearchCampaign` | Legacy campaign-definition serializer и SQLite store существуют | Legacy CLI compatibility readers существуют | Не смешивать с executed Campaign artifact; мигрировать только по ADR-006 |

Наличие envelope или loader само по себе не является основанием для
создания persistence.

Новый store разрешён только при наличии сценария:

producer → envelope → store → validated reader → public use case →
подтверждённый transport consumer.

### Artifact identities

- `artifact_id` идентифицирует envelope;
- `result_id` идентифицирует исследовательский результат;
- `execution_id` идентифицирует техническую попытку;
- `experiment_id` идентифицирует определение эксперимента;
- `campaign_plan_id` идентифицирует план Campaign;
- `correlation_id` используется только для tracing.

Эти identities не являются взаимозаменяемыми aliases.

Для каждого нового persisted artifact type до реализации необходимо
явно определить storage key, payload identity, правило их совпадения и
collision semantics.

По результатам decision gate новые Campaign, HypothesisEvaluation,
Knowledge-question, Evidence или Finding stores сейчас не создаются.

## Production hardening completion

Audit baseline: `7d92d81`.
Local test baseline: `2448 passed`.

Утверждённый архитектурный scope завершил этап
post-consolidation production hardening.

### Подтверждённые closure criteria

1. `ExperimentExecution` остаётся отдельным от Evidence, Finding,
   HypothesisEvaluation и Knowledge.
2. Append-only execution history проверяется при записи и при всех
   публичных вариантах чтения: history, latest и listing.
3. `ResearchArtifactEnvelope` используется как storage и exchange
   boundary, а не как базовый класс доменных моделей.
4. Modern и legacy market research artifacts проходят эквивалентную
   integrity policy.
5. Storage key проверяется против identity внутри artifact payload.
6. Listing сохранённых research cycles работает fail-closed.
7. Получение cycle, получение artifact, export и comparison не
   обходят validated Application reader.
8. CLI, HTTP и MCP преобразуют integrity failures в контролируемые
   transport results.
9. Стабильный `src.application.public_api` защищён точным allowlist.
10. Artifact persistence расширяется только при наличии
    подтверждённого persisted consumer.

### Решение по дальнейшему scope

Новые stores для Campaign result, HypothesisEvaluation, Knowledge
questions, standalone Evidence и Finding сейчас не требуются.

Legacy comparative file artifacts сохраняют специализированные
export, load и comparison boundaries.

Legacy serialized ResearchCampaign остаётся отдельной compatibility
boundary и не считается persistence executed Campaign artifact.

Architecture program не расширяется универсальным workflow engine,
scheduler, retry runtime, queue, worker state или общим artifact
repository.

Knowledge feature freeze сохраняется.

Дальнейшие security, authentication, authorization, TLS, deployment,
observability, UX и operational requirements относятся к отдельной
product-readiness программе и не являются незавершёнными частями
утверждённого архитектурного scope.

## Operational readiness completion

Audit baseline: `76f1261`.
Local test baseline: `2482 passed`.

В репозитории завершён утверждённый operational baseline для закрытого
однопользовательского private VPS.

Подтверждены:

- production Waitress entry point с обязательным Bearer token из
  environment и запретом non-loopback bind;
- публичные `/health` и SQLite-aware `/ready`;
- безопасный HTTP logging без query string, request body и token;
- validated online SQLite backup, integrity verification и restore
  только в отсутствующий target;
- systemd service с отдельным пользователем, private environment file
  и filesystem hardening;
- Caddy TLS termination перед loopback backend;
- воспроизводимый runbook для установки, обновления, backup, restore,
  диагностики и token rotation;
- явное исключение public multi-user и SaaS-функций из текущего scope.

Этот checkpoint подтверждает готовность repository-backed private-VPS
профиля к контролируемому развёртыванию. Он не утверждает, что выполнен
live deployment на конкретный VPS, и не означает готовность публичного
многопользовательского продукта.

## Приоритеты следующего этапа

Architecture program, Knowledge feature scope и private-VPS operational
baseline остаются замороженными.

Разрешённые направления:

1. Контролируемое развёртывание и smoke verification на конкретном VPS.
2. Исправления, integrity hardening и эксплуатационные тесты.
3. Consumer-driven research capabilities поверх стабильного
   `src.application.public_api`.
4. UX для подтверждённых пользовательских сценариев.
5. Новая artifact persistence только при наличии persisted consumer.

Без отдельного product decision по-прежнему не добавляются users,
roles, OAuth, multitenancy, public write API, PostgreSQL, queues,
distributed workers, Kubernetes или универсальный workflow engine.

## Критерий обновления

Этот документ необходимо обновлять, когда изменение:

- добавляет новый архитектурный контракт;
- завершает или расширяет вертикальный срез;
- меняет статус домена;
- устраняет архитектурное отклонение;
- добавляет подтверждённый инфраструктурный механизм.

На момент обновления полный набор автоматических тестов успешно проходит локально и в GitHub Actions.