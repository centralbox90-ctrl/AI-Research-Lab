# AI Research Lab — Architecture Inventory

Дата снимка: 28 июля 2026 года.

Commit: `9001efec31b59c20f319d21939a87fcf04480ee3`.

Статус: фактическая инвентаризация без предложений по рефакторингу.

## 1. Назначение и границы

Документ фиксирует существующие компоненты, связи и production wiring.
Он не вводит новые abstractions и не заменяет
`ARCHITECTURE_STATUS.md` или ADR.

`Production-wired` означает достижимость из
`src.cli.main.build_research_cli`.

## 2. Физические области

| Область | Production modules | Test modules | Фактическая ответственность |
|---|---:|---:|---|
| `src/application` | 108 | 93 | Use cases, coordinators, ports, adapters, loaders, serializers, factories и in-memory repositories. |
| `src/research` | 92 | 59 | Research, Analysis и Knowledge contracts, domain services и legacy research cycle. |
| `src/cli` | 28 | 31 | Entry point, commands, presenters и composition roots. |
| `src/storage` | 6 | 6 | SQLite adapters и storage configuration. |
| `src/backtest` | 12 | 13 | Execution policy, position/trade lifecycle и backtest orchestration. |
| `src/indicators` | 14 | 0 | Indicator contracts, catalog, discovery и calculation. |
| `src/signals` | 10 | 5 | Signal contracts, registry, discovery и generation. |
| `src/data` | 2 | 1 | Детерминированная генерация legacy market data. |
| `src/core` | 4 | 0 | Изолированная MarketSnapshot-модель и demo factory. |
| `src/project_memory` | 23 | 5 | Отдельная история и восстановление файлов; к Research CLI не подключены. |
| `src/models` | 1 | 0 | Package marker без production contracts. |

## 3. Фактические зависимости

| Источник | Импортируемые внутренние области |
|---|---|
| `application` | `research`, `backtest`, `indicators`, `signals`, `data` |
| `research` | `backtest`, `indicators` |
| `cli` | `application`, `research`, `storage`, `indicators` |
| `storage` | `research` |
| `signals` | `indicators` |
| `backtest`, `indicators`, `project_memory` | Только собственные области |
| `core` | `data` |
| `data`, `models` | Нет внутренних imports |

Автоматически проверяются правила:

- `research` не импортирует `application`, `storage` или `cli`;
- production modules `research` не имеют import cycles;
- `application` не импортирует `storage` или `cli`;
- `application` не импортирует legacy `Conclusion` и
  `HypothesisDecision`;
- `storage` не импортирует `application` или `cli`;
- production code не использует legacy persistence use cases
  `RunResearchCycle`, `RunAndStoreSerializedResearchCycle` и
  `RunAndStoreSerializedResearchCampaign`.

## 4. Production CLI

Главный composition root — `build_research_cli`. Он создаёт общий
`SqliteResearchCycleStore`.

| CLI route | Application boundary | Вход | Выход |
|---|---|---|---|
| `run-research` | `RunMarketResearch` | Specification JSON | Research-cycle JSON; полный artifact сохраняется в SQLite. |
| `run-market-research-campaign` | `RunMarketResearchCampaign` | Design JSON и registrations JSON | Campaign artifact v1. |
| `run-comparative-hypothesis-evaluation` | `IndicatorComparativeHypothesisEvaluationApplication` | Request JSON | HypothesisEvaluation artifact v1. |
| `generate-knowledge-research-questions` | `GenerateResearchQuestionsFromKnowledgeSnapshot` | Snapshot JSON | Research-question artifact v1. |
| `get-research-cycle` | `GetStoredResearchCycle` | Result ID | Stored JSON. |
| `get-research-artifact` | `GetStoredResearchArtifact` | Result ID | Stored artifact JSON. |
| `export-research-artifact` | `ExportStoredResearchArtifact` | Result ID и output path | JSON file. |
| `compare-research-artifacts` | `CompareStoredResearchArtifacts` | Два result ID | Comparison JSON. |
| `list-research-cycles` | `ListStoredResearchCycles` | Нет | Result IDs JSON. |

Parser и commands для `get-research-campaign` и
`list-research-campaigns` существуют, но `build_research_cli` не
передаёт соответствующие dependencies в production `ResearchCli`.

## 5. Application classification

### 5.1 Production-wired use cases

| Use case | Пользовательское намерение |
|---|---|
| `RunMarketResearch` | Выполнить одно market research specification. |
| `RunMarketResearchCampaign` | Спланировать, разрешить и выполнить кампанию. |
| `IndicatorComparativeHypothesisEvaluationApplication` | Выполнить comparative research до формальной HypothesisEvaluation. |
| `GenerateResearchQuestionsFromKnowledgeSnapshot` | Получить ResearchQuestion из gaps готового snapshot. |
| `GetStoredResearchCycle` | Получить сохранённый cycle payload. |
| `GetStoredResearchArtifact` | Получить сохранённый artifact. |
| `ExportStoredResearchArtifact` | Экспортировать artifact в JSON. |
| `CompareStoredResearchArtifacts` | Сравнить два artifacts. |
| `ListStoredResearchCycles` | Перечислить result IDs. |

### 5.2 Реализованы, но не production-wired

- `GetResearchCycle`
- `GetSerializedResearchCycle`
- `GetStoredResearchCampaign`
- `ListStoredResearchCampaigns`
- `RunSelectedNextExperiment`
- `RunResearchCycle`
- `RunAndStoreSerializedResearchCycle`
- `RunAndStoreSerializedResearchCampaign`

Последние три относятся к legacy persistence paths.

### 5.3 Internal coordinators

| Coordinator | Фактическая orchestration |
|---|---|
| `RunAndStoreResearchArtifact` | `ResearchEngine` → metadata → serialization → store. |
| `MarketResearchSessionFactory` | Mapping → dataset → context → ResearchGraph → executor. |
| `IndicatorComparativeResearchApplication` | Dataset → comparative analysis → statistical evaluations. |
| `IndicatorComparativeEvidenceApplication` | Несколько comparative runs → Evidence. |
| `IndicatorComparativeFindingApplication` | Evidence → Finding. |
| `IndicatorComparativeHypothesisEvaluationApplication` | Несколько Findings → HypothesisEvaluation. |
| `GenerateResearchQuestionsFromKnowledgeSnapshot` | Snapshot → gaps → recommendations → ResearchQuestion. |
| `KnowledgeGraphRelationRegistrar` | Stored contradiction/revision → relation registration. |
| `RunMarketResearchCampaignCommand` | Loaders → planner → adapter → campaign application → presenter. |
| `ResearchEngine` | Legacy mutable research cycle и cycle result chain. |

## 6. Domain services

Research planning and execution:

- `ResearchPlanner`
- `ExperimentRunner`
- `ResearchEnvironmentBuilder`
- `ResearchObjectsBuilder`
- `NextExperimentSelector`
- `AIScientist`

Analysis:

- `ComparativeAnalysisService`
- `ComparativeStatisticalEvaluator`
- `ComparativeEvidenceEvaluator`
- `FindingEvaluator`
- `HypothesisEvaluator`
- `StatisticalEvaluator`
- `RobustnessEvaluator`
- `ContradictionEvaluator`
- `EvidenceStrengthEvaluator`
- `EvidenceStrengthRanker`
- `ExperimentEvaluator`
- `ExperimentComparator`
- `EventStudyService`
- `BaselineComparator`
- `UnconditionalBaselineService`
- `ForwardOutcomeCalculator`

Knowledge:

- `KnowledgeCandidateValidator`
- `KnowledgeContradictionDetector`
- `KnowledgeGraph`
- `KnowledgeGapDetector`
- `ResearchRecommendationGenerator`

Calculation, Signal and Execution:

- `IndicatorCalculationService`
- `IndicatorCatalog`
- `SignalGenerationService`
- `SignalRuleRegistry`
- `BacktestEngine`
- `ExecutionModel`
- `PositionFactory`
- `PositionExitEvaluator`
- `TradeFactory`
- `Statistics`

`ResearchExecution` существует как mutable record с runtime UUID,
локальными timestamps, строковым status и ссылками на question,
hypothesis, experiment, evidence, finding и knowledge. Он используется
`AIScientist`, но не production CLI.

## 7. Adapters

Market data and execution:

- `LegacyMarketDataFrameAdapter`
- `CanonicalMarketDataProvider`
- `GeneratedMarketDataProvider`
- `Mt5MarketDataProvider`
- `PreparedMarketBacktestExecutor`
- `LegacyMarketBacktestExecutor`
- legacy signal mapper

Mapping:

- `MarketExperimentMapper`
- `ResearchCampaignPlanMarketAdapter`
- `ResearchRecommendationQuestionAdapter`
- market assumption-set builder
- `IndicatorSpecificationMapper`

Loaders:

- `MarketExperimentSpecificationLoader`
- `CampaignDesignLoader`
- `MarketExperimentRegistrationLoader`
- `IndicatorComparativeHypothesisEvaluationRequestLoader`
- `IndicatorComparativeResearchArtifactLoader`
- `KnowledgeGraphSnapshotLoader`

Serializers, presenters and filesystem:

- `ResearchArtifactSerializer`
- `ResearchCycleSerializer`
- `ResearchCampaignSerializer`
- `ResearchCycleJsonPresenter`
- `MarketResearchCampaignPresenter`
- comparative research, Evidence, Finding и HypothesisEvaluation presenters
- Knowledge research-question presenter
- `ResearchArtifactFileExporter`

## 8. Composition roots and factories

| Component | Location | Фактическое использование |
|---|---|---|
| `build_research_cli` | `src/cli/main.py` | Главный production root. |
| `build_market_research_application` | `src/application/market_research_application.py` | Используется главным root. |
| `build_knowledge_research_question_application` | `src/application/knowledge_research_question_application.py` | Используется главным root. |
| comparative hypothesis-evaluation builders | `src/cli/indicator_comparative_hypothesis_evaluation_composition_root.py` | Используются главным root. |
| comparative research builder family | `src/cli/indicator_comparative_research_composition_root.py` | Используется comparative root. |
| `build_default_hypothesis_evaluation_application` | `src/cli/hypothesis_evaluation_composition_root.py` | Используется comparative root. |
| `build_default_market_research_application` | `src/cli/market_research_composition_root.py` | Реализован; главный root использует другой builder. |

Factories:

- `MarketResearchSessionFactory`
- `MarketResearchCampaignSessionFactory`
- `MarketResearchContextFactory`
- `MarketSignalProviderFactory`
- `IndicatorResearchExecutionFactory`
- `NextExperimentFactory`
- `ArtifactMetadataFactory`
- `ArtifactComparisonFactory`

## 9. Persistence

| Port | In-memory adapter | SQLite adapter | Production CLI |
|---|---|---|---|
| `SerializedResearchCycleStore` | Test doubles | `SqliteResearchCycleStore` | Подключён. |
| `SerializedResearchCampaignStore` | Test doubles | `SqliteResearchCampaignStore` | Не подключён. |
| `ResearchCycleRepository` | `InMemoryResearchCycleRepository` | Нет | Не подключён. |
| `KnowledgeRepository` | `InMemoryKnowledgeRepository` | `SqliteKnowledgeRepository` | Не подключён. |
| `KnowledgeRelationRepository` | `InMemoryKnowledgeRelationRepository` | `SqliteKnowledgeRelationRepository` | Не подключён. |

SQLite tables:

- `research_cycles`
- `research_campaigns`
- `knowledge_revisions`
- `knowledge_contradictions`
- `knowledge_relations`

Оба SQLite Knowledge adapters экспортируются через `src.storage`.
Production-ссылок на них за пределами `src.storage` нет.

## 10. Manual file boundaries

| Boundary | Consumer | Production route |
|---|---|---|
| Market specification JSON | `MarketExperimentSpecificationLoader` | `run-research` |
| Campaign design JSON | `CampaignDesignLoader` | `run-market-research-campaign` |
| Campaign registrations JSON | `MarketExperimentRegistrationLoader` | `run-market-research-campaign` |
| Comparative request JSON | `IndicatorComparativeHypothesisEvaluationRequestLoader` | `run-comparative-hypothesis-evaluation` |
| Knowledge snapshot JSON | `KnowledgeGraphSnapshotLoader` | `generate-knowledge-research-questions` |
| Exported artifact JSON | Внешний consumer | `export-research-artifact` |

`KnowledgeGraphSnapshot.from_graph` существует. Production CLI не
содержит in-process пути от persistent Knowledge repositories к
snapshot. Question-generation route начинается с внешнего snapshot
JSON.

`IndicatorComparativeResearchArtifactLoader` реализован, но production
consumer отсутствует.

## 11. Artifact producers and consumers

| Producer | Contract | Consumer/storage |
|---|---|---|
| `ResearchArtifactSerializer` | Version 1; specification, cycle, optional environment, metadata, lineage и comparisons | Artifact runner, campaign presenter, cycle store. |
| `MarketResearchCampaignPresenter` | `market_research_campaign` v1 | CLI JSON. |
| comparative research presenter | `indicator_comparative_research` v1 | Composition output/tests. |
| Evidence presenter | `indicator_comparative_evidence` v1 | Composition output/tests. |
| Finding presenter | `indicator_comparative_finding` v2 | Composition output/tests. |
| HypothesisEvaluation presenter | `hypothesis_evaluation` v1 | Production CLI. |
| Research-question presenter | `knowledge_research_questions` v1 | Production CLI. |
| `ResearchCycleSerializer` | Cycle dictionary | CLI response и legacy paths. |
| `ResearchCampaignSerializer` | Mutable campaign dictionary | Legacy path. |

`ResearchArtifact` dataclass существует, но production modules его не
импортируют. Artifact persistence использует dictionaries от
`ResearchArtifactSerializer`.

Presenter envelopes имеют разные структуры. Большинство используют
`artifact_type` и `artifact_version`; `ResearchArtifactSerializer`
использует `artifact_version` без `artifact_type`.

## 12. Legacy compatibility boundaries

| Boundary | Фактическое состояние |
|---|---|
| `ResearchEngine` | Используется `RunAndStoreResearchArtifact`. |
| `LegacyEvidence`, `Conclusion`, `HypothesisDecision`, mutable `Knowledge` | Используются legacy engine, builders и cycle results. |
| `ResearchCampaign` | Mutable runtime compatibility contract. |
| `Question`, `Hypothesis`, `Experiment`, `ExperimentResult`, `ResearchGraph` | Используются mapper/session и legacy engine. |
| `LegacyMarketDataProvider` | Вход для generated и MT5 providers. |
| `LegacyMarketDataFrameAdapter` | Изолирует legacy OHLC columns. |
| `LegacyMarketBacktestExecutor` | Compatibility executor; production session использует prepared executor. |
| legacy signal mapper | Используется `BacktestEngine`. |
| `ResearchRecommendationQuestionAdapter` | Создаёт legacy `ResearchQuestion`. |
| legacy serialized persistence use cases | Существуют; production usage запрещено test-правилом. |
| `src/research/engine.py.broken` | Tracked recovery copy; imports отсутствуют. |

## 13. Наблюдаемые end-to-end paths

Market research:

Specification JSON
→ loader
→ `RunMarketResearch`
→ session factory
→ canonical dataset
→ prepared executor
→ `ResearchEngine`
→ artifact serializer
→ `SqliteResearchCycleStore`

Comparative Analysis:

Request JSON
→ comparative research
→ statistical evaluation
→ Evidence
→ Finding
→ HypothesisEvaluation
→ presenter

Knowledge feedback:

Snapshot JSON
→ gap detector
→ recommendation generator
→ legacy ResearchQuestion adapter
→ presenter

Persistent Knowledge:

`KnowledgeRepository`
→ `SqliteKnowledgeRepository`

`KnowledgeRelationRepository`
→ `SqliteKnowledgeRelationRepository`

Между HypothesisEvaluation и KnowledgeCandidate нет production
application use case. Между persistent Knowledge repositories и
production snapshot/question route нет composition root.

## 14. Итоговая фиксация

На commit `9001efec`:

- Analysis до HypothesisEvaluation имеет production CLI route;
- Knowledge feedback от готового snapshot до ResearchQuestion имеет
  production CLI route;
- snapshot поступает через ручную JSON-границу;
- persistent Knowledge adapters реализованы и экспортированы, но не
  входят в production dependency graph;
- artifact producers используют несколько envelope shapes;
- общий workflow, lifecycle, pipeline или orchestration abstraction
  инвентаризацией не добавлялся.
## 15. Consolidation checkpoint

Commit checkpoint: `21f855a`.

Этот раздел фиксирует фактическую дельту после baseline commit
`9001efec`. Разделы 1–14 остаются исходным architecture inventory.

### 15.1 ExperimentExecution

Для одиночного production market experiment реализован отдельный
технический lifecycle:

- immutable `ExperimentExecution`;
- состояния `PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED` и `CANCELLED`;
- deterministic fingerprint полной `MarketExperimentSpecification`;
- `ExperimentExecutionFactory`;
- `ExperimentExecutionTrackingExecutor`;
- append-only `SqliteExperimentExecutionRecorder`;
- SQLite-таблица `experiment_execution_snapshots`;
- wiring в обоих market composition roots.

Execution переводится в `SUCCEEDED` сразу после получения валидного
`ExperimentResult`. Ошибки последующего analysis, serialization или
artifact persistence не изменяют технический outcome выполнения.

Pending execution пока создаётся после mapping, загрузки dataset и
построения `ResearchContext`. Поэтому preparation failures до создания
session ещё не имеют persistent execution record.

### 15.2 ResearchArtifactEnvelope

Для одиночного production market path реализованы:

- `ResearchArtifactEnvelope`;
- `ResearchArtifactSourceReference`;
- `ResearchArtifactEnvelopeFactory`;
- canonical SHA-256 fingerprint payload;
- immutable JSON snapshots payload и provenance;
- integrity-aware envelope loader;
- совместимое чтение legacy и envelope artifacts.

Envelope `market_research_cycle` содержит отдельный `artifact_id`,
producer metadata, execution и result source references, specification
и environment provenance, payload fingerprint и существующий
типизированный market research payload.

Legacy writer сохраняется для немигрированных вызовов.
`ArtifactComparisonInputExtractor` принимает оба формата и использует
внешний envelope artifact ID для новых artifacts.

Campaign, comparative Evidence, Finding, HypothesisEvaluation,
Knowledge snapshot и research-question artifacts пока не мигрированы.

### 15.3 Production market path

Specification JSON
→ `RunMarketResearch`
→ `MarketResearchSessionFactory`
→ canonical dataset и `ResearchContext`
→ `ExperimentExecution`
→ tracking executor
→ prepared market executor
→ execution snapshots в SQLite
→ legacy `ResearchEngine`
→ typed market research payload
→ `ResearchArtifactEnvelope`
→ `SqliteResearchCycleStore`.

### 15.4 Сохраняющиеся разрывы

На commit `21f855a`:

- preparation failures ещё не сохраняются;
- lifecycle-level `correlation_id` пока не передаётся;
- campaign execution не использует единый execution lifecycle;
- большинство artifact types остаются legacy;
- HypothesisEvaluation → KnowledgeCandidate не имеет production use case;
- Knowledge repositories не подключены к production composition root;
- Knowledge snapshot поступает через ручной JSON-файл;
- Analysis → Knowledge → Recommendation не является единым
  in-process production path.

Общий workflow, lifecycle, pipeline или orchestration engine не
добавлялся.
