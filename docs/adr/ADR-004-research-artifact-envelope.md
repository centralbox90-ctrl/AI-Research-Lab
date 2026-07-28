# ADR-004: ResearchArtifactEnvelope

Дата: 28 июля 2026 года
Статус: Accepted

## Контекст

Проект уже производит несколько версионированных JSON artifacts:

- indicator comparative research версии 1;
- indicator comparative evidence версии 1;
- indicator comparative finding версии 2;
- hypothesis evaluation версии 1;
- knowledge research questions версии 1;
- market research campaign версии 1;
- serialized market research artifact версии 1.

Эти artifacts используют разные верхнеуровневые структуры.

Большинство presenters возвращают artifact_type и artifact_version рядом с типизированными полями payload.

ResearchArtifactSerializer возвращает artifact_version, specification и cycle, а optional metadata содержит отдельный schema_version со строковым значением.

MarketResearchCampaignPresenter вкладывает serialized experiment artifacts внутрь campaign artifact.

Loaders проверяют artifact type, version и обязательные секции отдельно для каждого формата.

ResearchArtifact dataclass существует в Application Layer, но не определяет единый production-контракт хранения и обмена.

Из-за этого невозможно одинаково выполнять:

- идентификацию artifact;
- трассировку research lifecycle;
- проверку целостности payload;
- определение producer;
- миграцию формата;
- построение общего API adapter;
- связывание artifacts с ExperimentExecution.

При этом Evidence, Finding, HypothesisEvaluation, KnowledgeSnapshot и другие payload имеют различную доменную семантику и не должны наследоваться от универсальной artifact-сущности.

## Решение

Вводится единый ResearchArtifactEnvelope для границ хранения и обмена.

Envelope является application-level boundary contract.

Он не является доменной сущностью, базовым классом или aggregate root.

Envelope оборачивает уже сериализованный типизированный payload и добавляет общую идентичность, версионирование, provenance, tracing и integrity metadata.

## Размещение

Контракт может быть размещён в `src/application/research_artifact_envelope.py`.

Создание envelope выполняется Application Layer через factory, использующую существующие Clock и IdGenerator ports.

CLI, HTTP, MCP и другие внешние adapters получают готовый envelope и только преобразуют его в транспортный формат.

Domain Layer не импортирует ResearchArtifactEnvelope.

Storage adapters сохраняют и возвращают envelope через application-defined ports, не изменяя его семантику.

## Минимальный контракт

ResearchArtifactEnvelope содержит:

- schema_version;
- artifact_type;
- payload_schema_version;
- artifact_id;
- created_at;
- producer;
- producer_version;
- optional correlation_id;
- source_references;
- provenance;
- payload_fingerprint;
- payload.

## Версионирование

schema_version определяет версию общей структуры envelope.

Начальная версия envelope равна 1.

payload_schema_version определяет версию контракта конкретного artifact_type.

Версия envelope и версия payload изменяются независимо.

Изменение полей общей оболочки требует новой schema_version.

Изменение структуры конкретного payload требует новой payload_schema_version только для соответствующего artifact_type.

Существующий artifact_version при миграции становится payload_schema_version.

Существующий вложенный metadata.schema_version не используется как версия нового envelope.

## Artifact identity

artifact_id является собственной стабильной идентичностью конкретного сохранённого artifact.

artifact_id не вычисляется из payload fingerprint.

Два artifacts могут иметь одинаковый payload_fingerprint, но разные artifact_id, created_at, producer или provenance.

Повторное чтение одного сохранённого artifact не создаёт новый artifact_id.

Создание нового artifact после повторного выполнения создаёт новый artifact_id.

## Artifact type

artifact_type является стабильным непустым строковым идентификатором типизированного payload.

Artifact type определяет:

- допустимый payload serializer;
- допустимый payload loader;
- payload schema version;
- validation contract.

Envelope factory не интерпретирует доменную семантику payload.

Dispatcher выбирает serializer или loader по паре artifact_type и payload_schema_version.

## Payload

payload является JSON-compatible представлением конкретного результата.

Примеры payload:

- comparative research;
- evidence;
- finding;
- hypothesis evaluation;
- experiment execution;
- market research cycle;
- campaign execution;
- knowledge graph snapshot;
- research questions.

Evidence, Finding, HypothesisEvaluation и Knowledge models не наследуются от ResearchArtifactEnvelope.

Envelope не заменяет их validators, fingerprints или domain invariants.

Сериализация domain model в payload выполняется специализированным serializer или presenter.

## Payload fingerprint

payload_fingerprint является SHA-256 fingerprint канонического JSON-представления только payload.

Envelope metadata не входит в payload_fingerprint.

Каноническое представление версии 1 использует:

- UTF-8;
- JSON object keys в отсортированном порядке;
- компактные separators;
- сохранение порядка JSON arrays;
- запрет NaN и Infinity;
- datetime как timezone-aware ISO 8601 UTC strings;
- предварительное преобразование tuples и enums в JSON-compatible values.

Loader повторно вычисляет payload_fingerprint и отклоняет envelope при несовпадении.

Domain fingerprint может совпадать с payload_fingerprint только если использует точно тот же канонический контракт. Автоматически считать их одинаковыми запрещено.

## Producer

producer содержит стабильное логическое имя компонента, создавшего payload.

producer_version содержит версию artifact-producing кода.

В production producer_version должен быть связан с code version, release version или другим воспроизводимым software identifier.

producer_version не заменяет payload_schema_version.

Изменение реализации producer без изменения payload contract не требует новой payload_schema_version.

## Correlation identifier

correlation_id связывает artifacts одного research lifecycle.

correlation_id не заменяет:

- execution_id;
- experiment_id;
- result_id;
- evidence_id;
- finding_id;
- hypothesis_evaluation_id;
- knowledge_id;
- artifact_id.

Для artifacts нового ExperimentExecution path correlation_id передаётся из execution context, если он определён.

Во время миграции legacy artifact может иметь correlation_id со значением null.

Новые production use cases должны передавать correlation_id явно, когда artifact является частью уже начатого lifecycle.

## Source references

source_references является упорядоченным списком ссылок на непосредственные источники artifact.

Каждая ссылка содержит:

- reference_type;
- reference_id;
- optional reference_version;
- optional reference_fingerprint.

Примеры reference_type:

- experiment_execution;
- experiment_result;
- evidence;
- finding;
- hypothesis_evaluation;
- knowledge_revision;
- knowledge_graph_snapshot;
- parent_artifact.

Source references описывают происхождение, но не создают доменных отношений между объектами.

Exact-version Knowledge references должны указывать конкретную revision version.

correlation_id не используется вместо source references.

## Provenance

provenance является JSON-compatible объектом с дополнительными воспроизводимыми сведениями о создании payload.

Для market research provenance может включать:

- specification fingerprint;
- environment fingerprint;
- dataset fingerprint;
- assumption set fingerprint;
- code version;
- executor version;
- statistical method version;
- random seed.

Provenance не содержит credentials, access tokens, connection secrets, полный traceback или неконтролируемые environment variables.

Обязательные provenance-поля определяются конкретным artifact_type и payload_schema_version.

## Временные метки

created_at является timezone-aware UTC timestamp момента создания envelope.

created_at создаётся через Clock port.

Временные метки domain payload не заменяются created_at envelope.

Повторная сериализация существующего envelope не изменяет created_at.

## Validation

Envelope validator проверяет:

- поддерживаемую schema_version;
- непустые artifact_type, artifact_id, producer и producer_version;
- положительную payload_schema_version;
- timezone-aware UTC created_at;
- корректность optional correlation_id;
- уникальность полностью совпадающих source references;
- JSON compatibility provenance и payload;
- соответствие payload_fingerprint;
- наличие зарегистрированного payload contract.

Envelope validator не выполняет domain validation payload.

Сначала specialized payload loader проверяет доменный boundary contract, затем envelope передаёт данные соответствующему application use case.

## ExperimentExecution integration

Первым envelope внедряется для нового одиночного market experiment path.

После SUCCEEDED ExperimentExecution создаётся market research cycle artifact.

Envelope этого artifact:

- получает новый artifact_id;
- использует execution correlation_id;
- ссылается на execution_id и result_id;
- сохраняет specification и environment fingerprints в provenance;
- содержит существующий типизированный research cycle payload;
- вычисляет payload_fingerprint;
- сохраняется через существующий storage boundary после его адаптации.

Ошибка artifact serialization или persistence не изменяет SUCCEEDED ExperimentExecution на FAILED.

## Campaign artifacts

Campaign artifact не мигрирует в первом implementation slice.

Новые campaign envelopes не должны вкладывать полные дочерние envelopes без явной необходимости.

Предпочтительно ссылаться на child artifact_id через source references или типизированный campaign payload.

Точное решение принимается после миграции одиночного market experiment path.

## Legacy migration

Существующие presenters, loaders и сохранённые JSON files продолжают поддерживаться до отдельной миграции каждого artifact type.

Миграция выполняется по одному artifact type.

При миграции:

1. существующий верхнеуровневый artifact_type сохраняется;
2. существующий artifact_version становится payload_schema_version;
3. типизированные поля перемещаются внутрь payload;
4. envelope получает schema_version 1;
5. создаются artifact identity, producer metadata и payload fingerprint;
6. loader временно поддерживает legacy и envelope formats;
7. legacy writer удаляется только после миграции consumers.

Массовая одновременная замена всех presenters запрещена.

## Существующий ResearchArtifact

Текущий ResearchArtifact dataclass не становится базовым классом нового envelope.

Он рассматривается как compatibility model.

Его удаление, переименование или адаптация выполняется отдельным небольшим изменением после первого production envelope.

ArtifactMetadata, ArtifactLineage, ArtifactHistoryEntry и ArtifactComparison не переносятся автоматически в общую оболочку.

Их данные мигрируют только при наличии подтверждённого общего смысла.

## Архитектурные инварианты

1. Envelope существует только на границах хранения и обмена.
2. Domain objects не наследуются от envelope.
3. Payload остаётся типизированным.
4. correlation_id обеспечивает tracing, но не identity.
5. payload fingerprint не включает envelope metadata.
6. Artifact identity не является content hash.
7. Envelope не принимает научных решений.
8. Storage не изменяет envelope.
9. CLI и API не конструируют domain semantics.
10. Каждый artifact type мигрирует отдельно.

## Отклонённые варианты

### Универсальная доменная Artifact base class

Отклонено, потому что Evidence, Finding, HypothesisEvaluation и Knowledge имеют разные invariants и lifecycle.

### Один version field

Отклонено, потому что envelope и payload развиваются независимо.

### Использовать artifact_id как payload hash

Отклонено, потому что идентичность сохранённого artifact и идентичность его содержимого имеют разный смысл.

### Использовать correlation_id вместо source references

Отклонено, потому что correlation показывает общий lifecycle, но не точное происхождение artifact.

### Немедленно мигрировать все presenters

Отклонено из-за высокого риска нарушения loaders, CLI contracts и сохранённых artifacts.

## Последствия

Появится единый внешний контракт для хранения, API и ChatGPT adapters.

Payload contracts сохранят доменную семантику и независимое версионирование.

Artifacts можно будет проверять на целостность и связывать с ExperimentExecution.

Потребуются envelope model, factory, validator, serializer, loader и application port.

Эти компоненты внедряются только вместе с первым production execution path и не создаются как самостоятельная горизонтальная подсистема.

Следующим архитектурным этапом является классификация публичных Application use cases и внутренних coordinators.

## Связанные документы

- `ARCHITECTURE_INVENTORY.md`
- `docs/adr/ADR-001-knowledge-feature-freeze.md`
- `docs/adr/ADR-002-research-runtime-boundary.md`
- `docs/adr/ADR-003-experiment-execution-lifecycle.md`