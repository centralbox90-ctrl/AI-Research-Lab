# ADR-005: Классификация Application use cases

Дата: 28 июля 2026 года
Статус: Accepted

## Контекст

Application Layer проекта содержит пользовательские сценарии,
внутренние coordinators, ports, adapters, loaders, serializers,
factories, composition helpers и legacy compatibility components.

`src.application.__init__` экспортирует компоненты разных категорий.
Сам факт package export сейчас не означает, что компонент является
стабильным публичным Application API.

В production composition root присутствуют несколько явно
наблюдаемых пользовательских намерений:

- выполнить одиночное market research;
- выполнить research campaign;
- выполнить comparative hypothesis evaluation;
- явно продвинуть HypothesisEvaluation в Knowledge;
- получить вопросы из сохранённого Knowledge;
- получить, экспортировать, сравнить или перечислить сохранённые
  research artifacts.

Одновременно многие классы связывают только соседние этапы:

- dataset и execution preparation;
- comparative analysis и statistical evaluation;
- Evidence и Finding;
- Finding и HypothesisEvaluation;
- Knowledge repositories и graph snapshot;
- graph snapshot, gaps, recommendations и ResearchQuestion.

Без явной классификации длинное имя Application-класса не позволяет
определить, является ли он пользовательским use case, внутренним
coordinator или boundary adapter.

Создание универсального WorkflowEngine для решения этой проблемы
запрещено действующим курсом консолидации.

## Решение

Application-компоненты классифицируются по фактической
ответственности, а не по суффиксу имени или месту package export.

Используются следующие категории:

1. Public Use Case.
2. Internal Coordinator.
3. Boundary Adapter.
4. Port.
5. Factory / Composition Root.
6. Legacy Compatibility Component.

Классификация описывает архитектурную роль. Она не требует общего
базового класса, marker interface или runtime registry.

## Public Use Case

Public Use Case представляет самостоятельное пользовательское или
внешнее системное намерение.

Public Use Case:

- принимает application-level input contract;
- выполняет один законченный сценарий;
- вызывает domain services и ports;
- возвращает application-level result;
- не зависит от CLI, HTTP, MCP или конкретного storage adapter;
- не раскрывает обязательность прямого управления repositories
  внешнему consumer.

Публичность определяется явным списком поддерживаемых use cases.
Наличие класса в `src.application.__init__` само по себе не делает его
публичным контрактом.

На текущем production checkpoint самостоятельные намерения
представляют:

- `RunMarketResearch`;
- `RunMarketResearchCampaign`;
- `IndicatorComparativeHypothesisEvaluationApplication`;
- `PromoteHypothesisEvaluationToKnowledge`;
- получение вопросов из persistent Knowledge;
- `GetStoredResearchCycle`;
- `GetStoredResearchArtifact`;
- `ExportStoredResearchArtifact`;
- `CompareStoredResearchArtifacts`;
- `ListStoredResearchCycles`.

Фактический repository-backed сценарий генерации вопросов сейчас
собран в CLI command из snapshot builder и application service.
До выделения application-level use case этот route считается
production-capable, но его публичный Application contract ещё не
стабилизирован.

## Internal Coordinator

Internal Coordinator связывает несколько domain services, adapters
или соседних application steps внутри публичного сценария.

Coordinator допустим, когда порядок шагов имеет конкретный доменный
смысл.

Coordinator:

- не считается внешним API по умолчанию;
- может принимать более узкие внутренние модели;
- не управляет retries, scheduling, worker leases или heartbeat;
- не превращает orchestration в конфигурируемый workflow language;
- не содержит transport parsing или output rendering.

К текущим internal coordinators относятся:

- `RunAndStoreResearchArtifact`;
- `MarketResearchSessionFactory`;
- `IndicatorComparativeResearchApplication`;
- `IndicatorComparativeEvidenceApplication`;
- `IndicatorComparativeFindingApplication`;
- `BuildKnowledgeGraphSnapshot`;
- `GenerateResearchQuestionsFromKnowledgeSnapshot`;
- `KnowledgeGraphRelationRegistrar`.

`IndicatorComparativeHypothesisEvaluationApplication` остаётся
публичным use case, потому что formal hypothesis evaluation является
самостоятельным пользовательским результатом, несмотря на наличие
внутренней orchestration.

## Boundary Adapter

Boundary Adapter преобразует данные между transport, persistence,
legacy или domain/application contracts.

К этой категории относятся:

- JSON request loaders;
- presenters;
- serializers;
- file exporters;
- legacy model adapters;
- recommendation-to-question adapter;
- CLI commands;
- SQLite adapters.

Boundary Adapter:

- не принимает научные решения;
- не определяет promotion policy;
- не создаёт contradiction semantics;
- не управляет domain lifecycle;
- не становится публичным Application use case только потому, что
  доступен внешнему transport.

CLI command является внешним adapter над use case или coordinator.
Он не является Application API.

## Port

Port определяет требуемую Application Layer возможность без выбора
конкретной инфраструктуры.

К ports относятся contracts для:

- persistence;
- clocks;
- identifiers;
- market data;
- execution;
- code version;
- artifact storage.

Public Use Case может зависеть от port. Он не должен импортировать
SQLite adapter или CLI implementation.

## Factory и Composition Root

Factory создаёт согласованный объект или локальный dependency graph.

Composition Root выбирает concrete adapters и собирает production
dependency graph.

Composition Root:

- может импортировать infrastructure adapters;
- не содержит научных решений;
- не вычисляет domain outcome;
- не заменяет PromotionPolicy;
- не реализует lifecycle transitions;
- не выполняет retries или scheduling;
- передаёт явно выбранные policy objects в use cases.

Настройка порогов policy в composition root допустима.
Ветвление по результатам domain evaluation в composition root
недопустимо.

## Legacy Compatibility Component

Legacy component сохраняет совместимость с существующими models,
serialized formats или execution paths.

Legacy component:

- явно отмечается в inventory;
- не добавляется в новый публичный Application API;
- не используется как основа новой универсальной abstraction;
- удаляется только отдельным миграционным изменением;
- может временно оставаться production dependency, если граница
  зафиксирована.

К этой категории относятся legacy research-cycle persistence use
cases, mutable research models и compatibility serializers,
перечисленные в Architecture Inventory.

## Публичная поверхность Application Layer

Публичный Application API должен быть малым явным allowlist.

Он не обязан совпадать с `src.application.__all__`.

Стабилизация выполняется постепенно:

1. зафиксировать фактическую категорию компонента;
2. определить input и result contract публичного use case;
3. подтвердить production composition;
4. подтвердить integration test;
5. только после этого экспортировать use case как публичный контракт;
6. сохранить internal imports для немигрированных consumers;
7. удалять legacy exports отдельными изменениями.

Массовое переименование классов или очистка `__all__` этим ADR не
разрешается.

## Правило подтверждённого обобщения

Общая orchestration abstraction допускается только тогда, когда
одинаковый lifecycle подтверждён минимум тремя независимыми
production-сценариями.

Совпадение формы «получить input, вызвать service, вернуть result» не
является достаточным основанием для WorkflowEngine.

До такого подтверждения orchestration остаётся в конкретных
Application use cases и coordinators.

## Research и runtime

Application coordinators определяют порядок вызова исследовательских
возможностей.

Они не управляют:

- очередями;
- worker leases;
- heartbeat;
- retry counters;
- next retry time;
- scheduling;
- распределёнными блокировками.

Эти обязанности принадлежат будущему runtime adapter и не входят в
публичный Research Application API.

## Knowledge promotion

`KnowledgePromotionPolicy` принимает доменное решение о допустимости
promotion.

`PromoteHypothesisEvaluationToKnowledge` является Application use
case и выполняет разрешённый переход:

- candidate construction;
- validation;
- revision persistence;
- contradiction detection;
- relation registration.

Transport adapter может запросить promotion, но не может обойти
policy или самостоятельно записать KnowledgeRevision.

## Artifact boundaries

`ResearchArtifactEnvelope` остаётся boundary contract хранения и
обмена.

Envelope не используется как базовый тип public use cases.

Public use case возвращает типизированный application result.
Специализированный boundary adapter создаёт payload и envelope там,
где соответствующий artifact type уже мигрирован.

## Архитектурные инварианты

1. Public Use Case представляет пользовательское намерение.
2. Package export не равен публичному Application API.
3. Internal Coordinator не является публичным по умолчанию.
4. CLI command является adapter, а не use case.
5. Composition Root только собирает зависимости.
6. Domain policy принимает научное решение.
7. Application Layer выполняет разрешённый переход.
8. Runtime state не входит в Research use cases.
9. Legacy component не становится основой новой архитектуры.
10. Общая orchestration появляется только после трёх подтверждённых
    production-сценариев.
11. Классификация не требует общей base class.
12. Новые Knowledge entities этим решением не вводятся.

## Отклонённые варианты

### Считать все exports публичным API

Отклонено, потому что package экспортирует ports, adapters, factories,
legacy components и внутренние coordinators.

### Универсальный ApplicationService base class

Отклонено, потому что он не выражает пользовательское намерение и
создаёт формальную связь между семантически разными сценариями.

### WorkflowEngine до инвентаризации повторений

Отклонено из-за отсутствия трёх независимых подтверждённых lifecycle
и риска скрыть доменный процесс в конфигурации.

### Немедленно переименовать все Application classes

Отклонено из-за большого migration diff без улучшения вертикальной
интеграции.

### Перенести policy decisions в CLI или composition root

Отклонено, потому что научные решения должны оставаться в Domain
Layer.

## Последствия

Публичный Application API можно стабилизировать независимо от
внутреннего количества coordinators и adapters.

HTTP, MCP и ChatGPT adapters смогут зависеть от небольшого набора
явных use cases.

`src.application.__init__` потребуется очищать постепенно, без
массового breaking change.

Repository-backed generation of research questions требует отдельного
application-level use case перед включением в публичный allowlist.

Следующее implementation change должно выделить этот конкретный
repository-backed use case из CLI orchestration, сохранив CLI как
тонкий adapter.

## Связанные документы

- `ARCHITECTURE_INVENTORY.md`
- `docs/adr/ADR-001-knowledge-feature-freeze.md`
- `docs/adr/ADR-002-research-runtime-boundary.md`
- `docs/adr/ADR-003-experiment-execution-lifecycle.md`
- `docs/adr/ADR-004-research-artifact-envelope.md`
