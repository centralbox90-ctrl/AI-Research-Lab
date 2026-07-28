# ADR-005: Application Layer Classification

Дата: 28 июля 2026 года
Статус: Accepted

## Контекст

Application Layer содержит более ста production modules.

В нём одновременно находятся:

- пользовательские use cases;
- внутренние coordinators;
- ports;
- adapters;
- loaders;
- serializers;
- factories;
- in-memory repositories;
- compatibility services.

Названия классов не всегда отражают архитектурную роль.

Суффикс Application используется как для production-фасада пользовательского сценария, так и для внутреннего шага orchestration.

Метод execute встречается у use cases, coordinators и adapters.

Architecture Inventory также показывает несколько компонентов одновременно среди production use cases и internal coordinators.

Без явной классификации возникают риски:

- внешний adapter начинает вызывать внутренний шаг;
- composition root содержит бизнес-ветвления;
- coordinator становится неявным публичным API;
- одинаковая orchestration копируется;
- будущий HTTP или MCP API фиксирует внутреннюю структуру Application Layer;
- универсальный workflow engine вводится до подтверждения общего lifecycle.

## Решение

Каждый Application Layer component получает одну основную архитектурную роль:

- Public Use Case;
- Internal Coordinator;
- Adapter;
- Factory;
- Composition Root;
- Port;
- Application DTO;
- Compatibility Boundary.

Основная роль определяется фактической ответственностью и направлением вызовов, а не названием класса.

Если production component является фасадом пользовательского намерения, роль Public Use Case имеет приоритет над внутренним фактом orchestration.

## Public Use Case

Public Use Case представляет одно завершённое пользовательское или внешнее application-намерение.

Он:

- имеет явно сформулированную цель;
- образует стабильную application boundary;
- может быть вызван CLI, HTTP, MCP или другим внешним adapter;
- определяет начало и завершение application-сценария;
- возвращает результат сценария или документированную ошибку;
- скрывает внутренние coordinators, factories и adapters;
- не зависит от CLI или конкретного storage implementation.

Наличие нескольких внутренних шагов не лишает компонент статуса Public Use Case.

Public Use Case не обязан быть одним domain service call.

## Текущие Public Use Cases

На основании фактического production wiring публичными считаются:

### Execution and analysis

- RunMarketResearch;
- RunMarketResearchCampaign;
- IndicatorComparativeHypothesisEvaluationApplication;
- GenerateResearchQuestionsFromKnowledgeSnapshot.

### Read and export

- GetStoredResearchCycle;
- GetStoredResearchArtifact;
- ExportStoredResearchArtifact;
- CompareStoredResearchArtifacts;
- ListStoredResearchCycles.

IndicatorComparativeHypothesisEvaluationApplication является Public Use Case, хотя координирует comparative research, Evidence, Finding и HypothesisEvaluation.

GenerateResearchQuestionsFromKnowledgeSnapshot является Public Use Case, хотя координирует gap detection, recommendation generation и преобразование recommendation в question.

Текущий список является allowlist, а не результатом автоматического экспорта всех классов из `src.application`.

## Реализованные, но не публичные сценарии

Следующие компоненты не входят в текущий public Application API, поскольку не подключены к production root или относятся к legacy path:

- GetResearchCycle;
- GetSerializedResearchCycle;
- GetStoredResearchCampaign;
- ListStoredResearchCampaigns;
- RunSelectedNextExperiment;
- RunResearchCycle;
- RunAndStoreSerializedResearchCycle;
- RunAndStoreSerializedResearchCampaign.

Наличие тестов или public export не делает компонент production Public Use Case.

Подключение любого из этих компонентов требует отдельного решения о boundary contract.

## Будущие сценарии

Следующие названия описывают roadmap, но не объявляются существующим API:

- GetExperimentExecution;
- PromoteHypothesisEvaluationToKnowledge;
- BuildKnowledgeSnapshot;
- GenerateResearchRecommendations.

Они становятся Public Use Cases только после реализации, production wiring и contract tests.

ADR не создаёт эти классы.

## Internal Coordinator

Internal Coordinator связывает несколько соседних application или domain capabilities внутри Public Use Case.

Он:

- не представляет самостоятельное внешнее намерение;
- не вызывается напрямую CLI или будущим HTTP/MCP adapter;
- может управлять последовательностью внутренних шагов;
- не формирует transport representation;
- не создаёт infrastructure dependencies самостоятельно;
- не становится универсальным workflow engine.

Текущими internal coordinators считаются:

- RunAndStoreResearchArtifact;
- IndicatorComparativeResearchApplication;
- IndicatorComparativeEvidenceApplication;
- IndicatorComparativeFindingApplication;
- KnowledgeGraphRelationRegistrar.

Coordinator может иметь execute method, но это не делает его Public Use Case.

Если coordinator становится нужен нескольким внешним adapters как самостоятельное намерение, его статус пересматривается отдельным изменением публичного allowlist.

## Компоненты, не являющиеся Application Coordinators

MarketResearchSessionFactory является Factory.

RunMarketResearchCampaignCommand является CLI Adapter.

ResearchEngine является legacy research-domain coordinator и Compatibility Boundary.

MarketResearchSession является application execution context holder.

ResearchArtifactSerializer является Adapter.

Класс не переносится в категорию Coordinator только потому, что вызывает несколько функций внутри своей технической ответственности.

## Adapter

Adapter преобразует данные или вызовы между границами.

Adapter может:

- загружать JSON;
- сериализовать результат;
- представлять DTO;
- преобразовывать одну модель в другую;
- предоставлять market data;
- выполнять инфраструктурный experiment contract;
- экспортировать файл;
- реализовывать persistence port.

Adapter не определяет научное решение и не управляет полным application lifecycle.

Текущие группы adapters:

- specification, design, registration и snapshot loaders;
- research, evidence, finding и hypothesis evaluation presenters;
- ResearchArtifactSerializer и ResearchCycleSerializer;
- MarketExperimentMapper;
- ResearchCampaignPlanMarketAdapter;
- ResearchRecommendationQuestionAdapter;
- market data providers;
- prepared and legacy executors;
- SQLite repositories;
- filesystem exporter.

Название Adapter не требуется, если роль однозначно зафиксирована inventory и tests.

## Factory

Factory создаёт объект или согласованный набор объектов.

Factory:

- получает необходимые dependencies;
- проверяет construction invariants;
- не выполняет пользовательский use case;
- не запускает research lifecycle;
- не сохраняет business result;
- не принимает научных решений.

Текущие factories:

- MarketResearchSessionFactory;
- MarketResearchCampaignSessionFactory;
- MarketResearchContextFactory;
- MarketSignalProviderFactory;
- IndicatorResearchExecutionFactory;
- NextExperimentFactory;
- ArtifactMetadataFactory;
- ArtifactComparisonFactory.

Factory может использовать adapters и builders, но не становится Composition Root автоматически.

## Composition Root

Composition Root только собирает dependency graph для конкретного entry point.

Он может:

- читать configuration;
- выбирать concrete adapters;
- создавать factories, coordinators и use cases;
- передавать dependencies;
- возвращать готовый entry point или Public Use Case.

Composition Root не должен:

- выполнять domain status transitions;
- анализировать Evidence;
- выбирать knowledge promotion;
- содержать lifecycle loops;
- реализовывать retries;
- сериализовать business payload вручную;
- обращаться к repository после запуска use case;
- дублировать orchestration Public Use Case.

Главным production Composition Root остаётся build_research_cli.

Application builders и comparative composition-root modules являются дочерними roots конкретных dependency graphs.

Условный выбор adapter по configuration допустим. Бизнес-ветвление по результатам исследования запрещено.

## Port

Port является application-defined protocol для внешней capability.

Port:

- выражает минимальную потребность use case;
- не содержит concrete infrastructure type;
- не зависит от CLI;
- не принимает универсальный dictionary вместо известного контракта без необходимости;
- не объединяет несвязанные operations.

Storage adapter может реализовать port структурно без импорта Application Layer, если это требуется существующими dependency rules.

Port не считается Public Use Case.

## Application DTO

Application DTO является стабильным входом или выходом публичного сценария.

DTO:

- не содержит open file handles, database connections или CLI parser objects;
- не зависит от transport format;
- не выполняет domain logic;
- может ссылаться на domain identities и immutable values;
- валидирует только boundary structure.

Не вводятся универсальные Request, Response, Context или Result base classes.

Общий DTO создаётся только при подтверждённом повторении минимум в трёх независимых сценариях.

## Compatibility Boundary

Compatibility Boundary изолирует компонент, который ещё нужен production path, но не соответствует целевой архитектуре.

К этой категории относятся:

- ResearchEngine;
- legacy mutable research-cycle models;
- legacy serialized persistence use cases;
- LegacyMarketDataProvider contracts;
- LegacyMarketDataFrameAdapter;
- LegacyMarketBacktestExecutor;
- ResearchRecommendationQuestionAdapter;
- существующий ResearchArtifact dataclass.

Compatibility Boundary не расширяется новой ответственностью.

Новый Public Use Case не должен зависеть от compatibility model, если существует стабильный современный контракт.

## Правила вызовов

Разрешённое направление:

External Adapter → Public Use Case → Internal Coordinator → Domain Service или Port.

Factory и Composition Root создают dependencies, но не находятся внутри business call chain как lifecycle steps.

Public Use Case может вызывать Port напрямую, если orchestration остаётся простой.

Internal Coordinator не вызывает CLI Adapter или Composition Root.

Adapter не вызывает другой внешний Adapter для построения скрытого workflow.

Domain Service не импортирует Application Layer.

## Публичный контракт

Public Application API является явным allowlist.

Экспорт через `src/application/__init__.py` сам по себе не считается публичным контрактом для внешних клиентов.

До появления отдельного API module источником allowlist являются:

- этот ADR;
- Architecture Inventory;
- production composition roots;
- contract tests публичных use cases.

Будущий HTTP, MCP или ChatGPT adapter вызывает только Public Use Cases из allowlist.

Он не вызывает coordinators, repositories, serializers или domain services напрямую.

## Правило обобщения

Общая workflow, lifecycle, pipeline или orchestration abstraction создаётся только если одинаковый lifecycle подтверждён минимум в трёх независимых production-сценариях.

Совпадение названий методов execute не является подтверждением общего lifecycle.

Повторение dependency injection, validation или serializer calls само по себе не является основанием для WorkflowEngine.

Сначала фиксируется повторяющаяся последовательность и её invariants. Затем принимается отдельный ADR.

## Testing

Каждый Public Use Case должен иметь contract tests для:

- валидного входа;
- результата;
- ошибок boundary validation;
- вызова необходимых ports;
- отсутствия зависимости от CLI и concrete storage.

Internal Coordinator тестируется как внутренний orchestration component.

Adapter тестируется на преобразование boundary contract.

Composition Root тестируется на корректное wiring и отсутствие пропущенных dependencies.

Architecture tests должны предотвращать:

- imports CLI из Application Layer;
- imports storage implementation из Application Layer;
- прямой вызов internal coordinators внешними API adapters;
- business branching в новых composition roots.

Новые architecture tests добавляются вместе с реальным refactoring slice, а не этим документационным commit.

## Migration

Этот ADR не переименовывает и не перемещает существующие классы.

Первый этап миграции:

1. сохранить текущий public allowlist;
2. пометить internal coordinators в документации;
3. не подключать новые adapters напрямую к coordinators;
4. стабилизировать ExperimentExecution use case;
5. внедрить ResearchArtifactEnvelope на этом use case;
6. затем определить отдельный application API module при наличии практической необходимости.

Количество классов не является метрикой успеха.

Допустимо сохранить несколько конкретных use cases, если они выражают разные пользовательские намерения.

## Отклонённые варианты

### Считать все Application classes публичными

Отклонено, потому что большинство классов являются внутренними шагами, adapters или factories.

### Определять роль по суффиксу имени

Отклонено, потому что текущие имена не обеспечивают такую гарантию.

### Объединить все execute methods в WorkflowEngine

Отклонено из-за отсутствия трёх подтверждённых одинаковых production lifecycle.

### Немедленно создать универсальные Request и Response

Отклонено как преждевременное обобщение.

### Переместить всю orchestration в Composition Root

Отклонено, потому что root должен только собирать dependencies.

## Последствия

Внешние adapters получат ограниченную и проверяемую поверхность Application API.

Внутренние coordinators можно будет изменять без нарушения внешнего контракта.

Composition roots станут проще проверять на отсутствие business logic.

Станет видно, какие длинные application classes являются оправданными use cases, а какие являются внутренней orchestration.

Следующим ADR должна быть Legacy Migration Policy.

После завершения обязательных ADR первым production refactoring slice остаётся единый ExperimentExecution path, а не создание новых общих abstractions.

## Связанные документы

- `ARCHITECTURE_INVENTORY.md`
- `ARCHITECTURE_STATUS.md`
- `docs/adr/ADR-001-knowledge-feature-freeze.md`
- `docs/adr/ADR-002-research-runtime-boundary.md`
- `docs/adr/ADR-003-experiment-execution-lifecycle.md`
- `docs/adr/ADR-004-research-artifact-envelope.md`