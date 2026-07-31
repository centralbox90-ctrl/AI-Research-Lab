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
- HTTP и MCP adapters предоставляют одинаковые три read-only
  Application use case; authentication, authorization, TLS и внешняя
  deployment configuration отсутствуют; отдельный ChatGPT adapter
  добавляется только при подтверждённом consumer contract.

## Приоритеты следующего этапа

Knowledge feature development остаётся замороженной. Разрешены
исправления, тесты, документация, integration существующих contracts и
миграция подтверждённых boundaries.

Общие workflow, lifecycle, pipeline и orchestration abstractions
по-прежнему запрещены без трёх независимых production scenarios с
одинаковой технической семантикой.

Первым внешним adapter выбран HTTP.

Подтверждены:

- отдельный transport package;
- три read-only public use case;
- repository-backed artifact comparison;
- SQLite production composition;
- versioned response DTO;
- JSON error contract для statuses 400, 404 и 422;
- OpenAPI 3.1 document с API version 1.1.0;
- local-only Flask server entry point;
- отдельный production Waitress WSGI entry point;
- закреплённая Waitress dependency;
- MCP SDK 2.0.0;
- read-only MCP tools `list_research_cycles`,
  `get_research_artifact` и `compare_research_artifacts`;
- repository-backed MCP composition для трёх публичных use cases;
- stdio MCP entry point;
- protocol contract и SQLite integration tests через настоящий MCP
  client.

Следующий режим разработки:

1. Расширять HTTP только по одному публичному Application use case.
2. Не добавлять write endpoints до отдельного решения об
   authentication, authorization и idempotency.
3. Сохранять отдельный transport DTO для каждого сценария.
4. Не раскрывать repositories, composition internals и Domain objects.
5. Размещать production Waitress server только внутри отдельного
   security и network deployment boundary.
6. Сохранять MCP surface read-only; новые tools добавлять только поверх
   стабильного `src.application.public_api`, а отдельный ChatGPT adapter
   — только при подтверждённом consumer contract.
7. Мигрировать legacy boundaries только по ADR-006 и при наличии
   конкретного production consumer.
8. Добавлять artifact readers или stores только для подтверждённого
   внешнего сценария.

## Критерий обновления

Этот документ необходимо обновлять, когда изменение:

- добавляет новый архитектурный контракт;
- завершает или расширяет вертикальный срез;
- меняет статус домена;
- устраняет архитектурное отклонение;
- добавляет подтверждённый инфраструктурный механизм.

На момент обновления полный набор автоматических тестов успешно проходит локально и в GitHub Actions.