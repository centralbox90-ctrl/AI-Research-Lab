# AI Research Lab вЂ” Architecture Inventory

Р”Р°С‚Р° СЃРЅРёРјРєР°: 28 РёСЋР»СЏ 2026 РіРѕРґР°.

Commit: `9001efec31b59c20f319d21939a87fcf04480ee3`.

РЎС‚Р°С‚СѓСЃ: С„Р°РєС‚РёС‡РµСЃРєР°СЏ РёРЅРІРµРЅС‚Р°СЂРёР·Р°С†РёСЏ Р±РµР· РїСЂРµРґР»РѕР¶РµРЅРёР№ РїРѕ СЂРµС„Р°РєС‚РѕСЂРёРЅРіСѓ.

## 1. РќР°Р·РЅР°С‡РµРЅРёРµ Рё РіСЂР°РЅРёС†С‹

Р”РѕРєСѓРјРµРЅС‚ С„РёРєСЃРёСЂСѓРµС‚ СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёРµ РєРѕРјРїРѕРЅРµРЅС‚С‹, СЃРІСЏР·Рё Рё production wiring.
РћРЅ РЅРµ РІРІРѕРґРёС‚ РЅРѕРІС‹Рµ abstractions Рё РЅРµ Р·Р°РјРµРЅСЏРµС‚
`ARCHITECTURE_STATUS.md` РёР»Рё ADR.

`Production-wired` РѕР·РЅР°С‡Р°РµС‚ РґРѕСЃС‚РёР¶РёРјРѕСЃС‚СЊ РёР·
`src.cli.main.build_research_cli`.

## 2. Р¤РёР·РёС‡РµСЃРєРёРµ РѕР±Р»Р°СЃС‚Рё

| РћР±Р»Р°СЃС‚СЊ | Production modules | Test modules | Р¤Р°РєС‚РёС‡РµСЃРєР°СЏ РѕС‚РІРµС‚СЃС‚РІРµРЅРЅРѕСЃС‚СЊ |
|---|---:|---:|---|
| `src/application` | 108 | 93 | Use cases, coordinators, ports, adapters, loaders, serializers, factories Рё in-memory repositories. |
| `src/research` | 92 | 59 | Research, Analysis Рё Knowledge contracts, domain services Рё legacy research cycle. |
| `src/cli` | 28 | 31 | Entry point, commands, presenters Рё composition roots. |
| `src/storage` | 6 | 6 | SQLite adapters Рё storage configuration. |
| `src/backtest` | 12 | 13 | Execution policy, position/trade lifecycle Рё backtest orchestration. |
| `src/indicators` | 14 | 0 | Indicator contracts, catalog, discovery Рё calculation. |
| `src/signals` | 10 | 5 | Signal contracts, registry, discovery Рё generation. |
| `src/data` | 2 | 1 | Р”РµС‚РµСЂРјРёРЅРёСЂРѕРІР°РЅРЅР°СЏ РіРµРЅРµСЂР°С†РёСЏ legacy market data. |
| `src/core` | 4 | 0 | РР·РѕР»РёСЂРѕРІР°РЅРЅР°СЏ MarketSnapshot-РјРѕРґРµР»СЊ Рё demo factory. |
| `src/project_memory` | 23 | 5 | РћС‚РґРµР»СЊРЅР°СЏ РёСЃС‚РѕСЂРёСЏ Рё РІРѕСЃСЃС‚Р°РЅРѕРІР»РµРЅРёРµ С„Р°Р№Р»РѕРІ; Рє Research CLI РЅРµ РїРѕРґРєР»СЋС‡РµРЅС‹. |
| `src/models` | 1 | 0 | Package marker Р±РµР· production contracts. |

## 3. Р¤Р°РєС‚РёС‡РµСЃРєРёРµ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё

| РСЃС‚РѕС‡РЅРёРє | РРјРїРѕСЂС‚РёСЂСѓРµРјС‹Рµ РІРЅСѓС‚СЂРµРЅРЅРёРµ РѕР±Р»Р°СЃС‚Рё |
|---|---|
| `application` | `research`, `backtest`, `indicators`, `signals`, `data` |
| `research` | `backtest`, `indicators` |
| `cli` | `application`, `research`, `storage`, `indicators` |
| `storage` | `research` |
| `signals` | `indicators` |
| `backtest`, `indicators`, `project_memory` | РўРѕР»СЊРєРѕ СЃРѕР±СЃС‚РІРµРЅРЅС‹Рµ РѕР±Р»Р°СЃС‚Рё |
| `core` | `data` |
| `data`, `models` | РќРµС‚ РІРЅСѓС‚СЂРµРЅРЅРёС… imports |

РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРё РїСЂРѕРІРµСЂСЏСЋС‚СЃСЏ РїСЂР°РІРёР»Р°:

- `research` РЅРµ РёРјРїРѕСЂС‚РёСЂСѓРµС‚ `application`, `storage` РёР»Рё `cli`;
- production modules `research` РЅРµ РёРјРµСЋС‚ import cycles;
- `application` РЅРµ РёРјРїРѕСЂС‚РёСЂСѓРµС‚ `storage` РёР»Рё `cli`;
- `application` РЅРµ РёРјРїРѕСЂС‚РёСЂСѓРµС‚ legacy `Conclusion` Рё
  `HypothesisDecision`;
- `storage` РЅРµ РёРјРїРѕСЂС‚РёСЂСѓРµС‚ `application` РёР»Рё `cli`;
- production code РЅРµ РёСЃРїРѕР»СЊР·СѓРµС‚ legacy persistence use cases
  `RunResearchCycle`, `RunAndStoreSerializedResearchCycle` Рё
  `RunAndStoreSerializedResearchCampaign`.

## 4. Production CLI

Р“Р»Р°РІРЅС‹Р№ composition root вЂ” `build_research_cli`. РћРЅ СЃРѕР·РґР°С‘С‚ РѕР±С‰РёР№
`SqliteResearchCycleStore`.

| CLI route | Application boundary | Р’С…РѕРґ | Р’С‹С…РѕРґ |
|---|---|---|---|
| `run-research` | `RunMarketResearch` | Specification JSON | Research-cycle JSON; РїРѕР»РЅС‹Р№ artifact СЃРѕС…СЂР°РЅСЏРµС‚СЃСЏ РІ SQLite. |
| `run-market-research-campaign` | `RunMarketResearchCampaign` | Design JSON Рё registrations JSON | Campaign artifact v1. |
| `run-comparative-hypothesis-evaluation` | `IndicatorComparativeHypothesisEvaluationApplication` | Request JSON | HypothesisEvaluation artifact v1. |
| `generate-knowledge-research-questions` | `GenerateResearchQuestionsFromKnowledgeSnapshot` | Snapshot JSON | Research-question artifact v1. |
| `get-research-cycle` | `GetStoredResearchCycle` | Result ID | Stored JSON. |
| `get-research-artifact` | `GetStoredResearchArtifact` | Result ID | Stored artifact JSON. |
| `export-research-artifact` | `ExportStoredResearchArtifact` | Result ID Рё output path | JSON file. |
| `compare-research-artifacts` | `CompareStoredResearchArtifacts` | Р”РІР° result ID | Comparison JSON. |
| `list-research-cycles` | `ListStoredResearchCycles` | РќРµС‚ | Result IDs JSON. |

Parser Рё commands РґР»СЏ `get-research-campaign` Рё
`list-research-campaigns` СЃСѓС‰РµСЃС‚РІСѓСЋС‚, РЅРѕ `build_research_cli` РЅРµ
РїРµСЂРµРґР°С‘С‚ СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓСЋС‰РёРµ dependencies РІ production `ResearchCli`.

## 5. Application classification

### 5.1 Production-wired use cases

| Use case | РџРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРѕРµ РЅР°РјРµСЂРµРЅРёРµ |
|---|---|
| `RunMarketResearch` | Р’С‹РїРѕР»РЅРёС‚СЊ РѕРґРЅРѕ market research specification. |
| `RunMarketResearchCampaign` | РЎРїР»Р°РЅРёСЂРѕРІР°С‚СЊ, СЂР°Р·СЂРµС€РёС‚СЊ Рё РІС‹РїРѕР»РЅРёС‚СЊ РєР°РјРїР°РЅРёСЋ. |
| `IndicatorComparativeHypothesisEvaluationApplication` | Р’С‹РїРѕР»РЅРёС‚СЊ comparative research РґРѕ С„РѕСЂРјР°Р»СЊРЅРѕР№ HypothesisEvaluation. |
| `GenerateResearchQuestionsFromKnowledgeSnapshot` | РџРѕР»СѓС‡РёС‚СЊ ResearchQuestion РёР· gaps РіРѕС‚РѕРІРѕРіРѕ snapshot. |
| `GetStoredResearchCycle` | РџРѕР»СѓС‡РёС‚СЊ СЃРѕС…СЂР°РЅС‘РЅРЅС‹Р№ cycle payload. |
| `GetStoredResearchArtifact` | РџРѕР»СѓС‡РёС‚СЊ СЃРѕС…СЂР°РЅС‘РЅРЅС‹Р№ artifact. |
| `ExportStoredResearchArtifact` | Р­РєСЃРїРѕСЂС‚РёСЂРѕРІР°С‚СЊ artifact РІ JSON. |
| `CompareStoredResearchArtifacts` | РЎСЂР°РІРЅРёС‚СЊ РґРІР° artifacts. |
| `ListStoredResearchCycles` | РџРµСЂРµС‡РёСЃР»РёС‚СЊ result IDs. |

### 5.2 Р РµР°Р»РёР·РѕРІР°РЅС‹, РЅРѕ РЅРµ production-wired

- `GetResearchCycle`
- `GetSerializedResearchCycle`
- `GetStoredResearchCampaign`
- `ListStoredResearchCampaigns`
- `RunSelectedNextExperiment`
- `RunResearchCycle`
- `RunAndStoreSerializedResearchCycle`
- `RunAndStoreSerializedResearchCampaign`

РџРѕСЃР»РµРґРЅРёРµ С‚СЂРё РѕС‚РЅРѕСЃСЏС‚СЃСЏ Рє legacy persistence paths.

### 5.3 Internal coordinators

| Coordinator | Р¤Р°РєС‚РёС‡РµСЃРєР°СЏ orchestration |
|---|---|
| `RunAndStoreResearchArtifact` | `ResearchEngine` в†’ metadata в†’ serialization в†’ store. |
| `MarketResearchSessionFactory` | Mapping в†’ dataset в†’ context в†’ ResearchGraph в†’ executor. |
| `IndicatorComparativeResearchApplication` | Dataset в†’ comparative analysis в†’ statistical evaluations. |
| `IndicatorComparativeEvidenceApplication` | РќРµСЃРєРѕР»СЊРєРѕ comparative runs в†’ Evidence. |
| `IndicatorComparativeFindingApplication` | Evidence в†’ Finding. |
| `IndicatorComparativeHypothesisEvaluationApplication` | РќРµСЃРєРѕР»СЊРєРѕ Findings в†’ HypothesisEvaluation. |
| `GenerateResearchQuestionsFromKnowledgeSnapshot` | Snapshot в†’ gaps в†’ recommendations в†’ ResearchQuestion. |
| `KnowledgeGraphRelationRegistrar` | Stored contradiction/revision в†’ relation registration. |
| `RunMarketResearchCampaignCommand` | Loaders в†’ planner в†’ adapter в†’ campaign application в†’ presenter. |
| `ResearchEngine` | Legacy mutable research cycle Рё cycle result chain. |

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

`ResearchExecution` СЃСѓС‰РµСЃС‚РІСѓРµС‚ РєР°Рє mutable record СЃ runtime UUID,
Р»РѕРєР°Р»СЊРЅС‹РјРё timestamps, СЃС‚СЂРѕРєРѕРІС‹Рј status Рё СЃСЃС‹Р»РєР°РјРё РЅР° question,
hypothesis, experiment, evidence, finding Рё knowledge. РћРЅ РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ
`AIScientist`, РЅРѕ РЅРµ production CLI.

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
- comparative research, Evidence, Finding Рё HypothesisEvaluation presenters
- Knowledge research-question presenter
- `ResearchArtifactFileExporter`

## 8. Composition roots and factories

| Component | Location | Р¤Р°РєС‚РёС‡РµСЃРєРѕРµ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ |
|---|---|---|
| `build_research_cli` | `src/cli/main.py` | Р“Р»Р°РІРЅС‹Р№ production root. |
| `build_market_research_application` | `src/application/market_research_application.py` | РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ РіР»Р°РІРЅС‹Рј root. |
| `build_knowledge_research_question_application` | `src/application/knowledge_research_question_application.py` | РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ РіР»Р°РІРЅС‹Рј root. |
| comparative hypothesis-evaluation builders | `src/cli/indicator_comparative_hypothesis_evaluation_composition_root.py` | РСЃРїРѕР»СЊР·СѓСЋС‚СЃСЏ РіР»Р°РІРЅС‹Рј root. |
| comparative research builder family | `src/cli/indicator_comparative_research_composition_root.py` | РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ comparative root. |
| `build_default_hypothesis_evaluation_application` | `src/cli/hypothesis_evaluation_composition_root.py` | РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ comparative root. |
| `build_default_market_research_application` | `src/cli/market_research_composition_root.py` | Р РµР°Р»РёР·РѕРІР°РЅ; РіР»Р°РІРЅС‹Р№ root РёСЃРїРѕР»СЊР·СѓРµС‚ РґСЂСѓРіРѕР№ builder. |

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
| `SerializedResearchCycleStore` | Test doubles | `SqliteResearchCycleStore` | РџРѕРґРєР»СЋС‡С‘РЅ. |
| `SerializedResearchCampaignStore` | Test doubles | `SqliteResearchCampaignStore` | РќРµ РїРѕРґРєР»СЋС‡С‘РЅ. |
| `ResearchCycleRepository` | `InMemoryResearchCycleRepository` | РќРµС‚ | РќРµ РїРѕРґРєР»СЋС‡С‘РЅ. |
| `KnowledgeRepository` | `InMemoryKnowledgeRepository` | `SqliteKnowledgeRepository` | РќРµ РїРѕРґРєР»СЋС‡С‘РЅ. |
| `KnowledgeRelationRepository` | `InMemoryKnowledgeRelationRepository` | `SqliteKnowledgeRelationRepository` | РќРµ РїРѕРґРєР»СЋС‡С‘РЅ. |

SQLite tables:

- `research_cycles`
- `research_campaigns`
- `knowledge_revisions`
- `knowledge_contradictions`
- `knowledge_relations`

РћР±Р° SQLite Knowledge adapters СЌРєСЃРїРѕСЂС‚РёСЂСѓСЋС‚СЃСЏ С‡РµСЂРµР· `src.storage`.
Production-СЃСЃС‹Р»РѕРє РЅР° РЅРёС… Р·Р° РїСЂРµРґРµР»Р°РјРё `src.storage` РЅРµС‚.

## 10. Manual file boundaries

| Boundary | Consumer | Production route |
|---|---|---|
| Market specification JSON | `MarketExperimentSpecificationLoader` | `run-research` |
| Campaign design JSON | `CampaignDesignLoader` | `run-market-research-campaign` |
| Campaign registrations JSON | `MarketExperimentRegistrationLoader` | `run-market-research-campaign` |
| Comparative request JSON | `IndicatorComparativeHypothesisEvaluationRequestLoader` | `run-comparative-hypothesis-evaluation` |
| Knowledge snapshot JSON | `KnowledgeGraphSnapshotLoader` | `generate-knowledge-research-questions` |
| Exported artifact JSON | Р’РЅРµС€РЅРёР№ consumer | `export-research-artifact` |

`KnowledgeGraphSnapshot.from_graph` СЃСѓС‰РµСЃС‚РІСѓРµС‚. Production CLI РЅРµ
СЃРѕРґРµСЂР¶РёС‚ in-process РїСѓС‚Рё РѕС‚ persistent Knowledge repositories Рє
snapshot. Question-generation route РЅР°С‡РёРЅР°РµС‚СЃСЏ СЃ РІРЅРµС€РЅРµРіРѕ snapshot
JSON.

`IndicatorComparativeResearchArtifactLoader` СЂРµР°Р»РёР·РѕРІР°РЅ, РЅРѕ production
consumer РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚.

## 11. Artifact producers and consumers

| Producer | Contract | Consumer/storage |
|---|---|---|
| `ResearchArtifactSerializer` | Version 1; specification, cycle, optional environment, metadata, lineage Рё comparisons | Artifact runner, campaign presenter, cycle store. |
| `MarketResearchCampaignPresenter` | `market_research_campaign` v1 | CLI JSON. |
| comparative research presenter | `indicator_comparative_research` v1 | Composition output/tests. |
| Evidence presenter | `indicator_comparative_evidence` v1 | Composition output/tests. |
| Finding presenter | `indicator_comparative_finding` v2 | Composition output/tests. |
| HypothesisEvaluation presenter | `hypothesis_evaluation` v1 | Production CLI. |
| Research-question presenter | `knowledge_research_questions` v1 | Production CLI. |
| `ResearchCycleSerializer` | Cycle dictionary | CLI response Рё legacy paths. |
| `ResearchCampaignSerializer` | Mutable campaign dictionary | Legacy path. |

`ResearchArtifact` dataclass СЃСѓС‰РµСЃС‚РІСѓРµС‚, РЅРѕ production modules РµРіРѕ РЅРµ
РёРјРїРѕСЂС‚РёСЂСѓСЋС‚. Artifact persistence РёСЃРїРѕР»СЊР·СѓРµС‚ dictionaries РѕС‚
`ResearchArtifactSerializer`.

Presenter envelopes РёРјРµСЋС‚ СЂР°Р·РЅС‹Рµ СЃС‚СЂСѓРєС‚СѓСЂС‹. Р‘РѕР»СЊС€РёРЅСЃС‚РІРѕ РёСЃРїРѕР»СЊР·СѓСЋС‚
`artifact_type` Рё `artifact_version`; `ResearchArtifactSerializer`
РёСЃРїРѕР»СЊР·СѓРµС‚ `artifact_version` Р±РµР· `artifact_type`.

## 12. Legacy compatibility boundaries

| Boundary | Р¤Р°РєС‚РёС‡РµСЃРєРѕРµ СЃРѕСЃС‚РѕСЏРЅРёРµ |
|---|---|
| `ResearchEngine` | РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ `RunAndStoreResearchArtifact`. |
| `LegacyEvidence`, `Conclusion`, `HypothesisDecision`, mutable `Knowledge` | РСЃРїРѕР»СЊР·СѓСЋС‚СЃСЏ legacy engine, builders Рё cycle results. |
| `ResearchCampaign` | Mutable runtime compatibility contract. |
| `Question`, `Hypothesis`, `Experiment`, `ExperimentResult`, `ResearchGraph` | РСЃРїРѕР»СЊР·СѓСЋС‚СЃСЏ mapper/session Рё legacy engine. |
| `LegacyMarketDataProvider` | Р’С…РѕРґ РґР»СЏ generated Рё MT5 providers. |
| `LegacyMarketDataFrameAdapter` | РР·РѕР»РёСЂСѓРµС‚ legacy OHLC columns. |
| `LegacyMarketBacktestExecutor` | Compatibility executor; production session РёСЃРїРѕР»СЊР·СѓРµС‚ prepared executor. |
| legacy signal mapper | РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ `BacktestEngine`. |
| `ResearchRecommendationQuestionAdapter` | РЎРѕР·РґР°С‘С‚ legacy `ResearchQuestion`. |
| legacy serialized persistence use cases | РЎСѓС‰РµСЃС‚РІСѓСЋС‚; production usage Р·Р°РїСЂРµС‰РµРЅРѕ test-РїСЂР°РІРёР»РѕРј. |
| `src/research/engine.py.broken` | Tracked recovery copy; imports РѕС‚СЃСѓС‚СЃС‚РІСѓСЋС‚. |

## 13. РќР°Р±Р»СЋРґР°РµРјС‹Рµ end-to-end paths

Market research:

Specification JSON
в†’ loader
в†’ `RunMarketResearch`
в†’ session factory
в†’ canonical dataset
в†’ prepared executor
в†’ `ResearchEngine`
в†’ artifact serializer
в†’ `SqliteResearchCycleStore`

Comparative Analysis:

Request JSON
в†’ comparative research
в†’ statistical evaluation
в†’ Evidence
в†’ Finding
в†’ HypothesisEvaluation
в†’ presenter

Knowledge feedback:

Snapshot JSON
в†’ gap detector
в†’ recommendation generator
в†’ legacy ResearchQuestion adapter
в†’ presenter

Persistent Knowledge:

`KnowledgeRepository`
в†’ `SqliteKnowledgeRepository`

`KnowledgeRelationRepository`
в†’ `SqliteKnowledgeRelationRepository`

РњРµР¶РґСѓ HypothesisEvaluation Рё KnowledgeCandidate РЅРµС‚ production
application use case. РњРµР¶РґСѓ persistent Knowledge repositories Рё
production snapshot/question route РЅРµС‚ composition root.

## 14. РС‚РѕРіРѕРІР°СЏ С„РёРєСЃР°С†РёСЏ

РќР° commit `9001efec`:

- Analysis РґРѕ HypothesisEvaluation РёРјРµРµС‚ production CLI route;
- Knowledge feedback РѕС‚ РіРѕС‚РѕРІРѕРіРѕ snapshot РґРѕ ResearchQuestion РёРјРµРµС‚
  production CLI route;
- snapshot РїРѕСЃС‚СѓРїР°РµС‚ С‡РµСЂРµР· СЂСѓС‡РЅСѓСЋ JSON-РіСЂР°РЅРёС†Сѓ;
- persistent Knowledge adapters СЂРµР°Р»РёР·РѕРІР°РЅС‹ Рё СЌРєСЃРїРѕСЂС‚РёСЂРѕРІР°РЅС‹, РЅРѕ РЅРµ
  РІС…РѕРґСЏС‚ РІ production dependency graph;
- artifact producers РёСЃРїРѕР»СЊР·СѓСЋС‚ РЅРµСЃРєРѕР»СЊРєРѕ envelope shapes;
- РѕР±С‰РёР№ workflow, lifecycle, pipeline РёР»Рё orchestration abstraction
  РёРЅРІРµРЅС‚Р°СЂРёР·Р°С†РёРµР№ РЅРµ РґРѕР±Р°РІР»СЏР»СЃСЏ.
## 15. Consolidation checkpoint

Commit checkpoint: `21f855a`.

Р­С‚РѕС‚ СЂР°Р·РґРµР» С„РёРєСЃРёСЂСѓРµС‚ С„Р°РєС‚РёС‡РµСЃРєСѓСЋ РґРµР»СЊС‚Сѓ РїРѕСЃР»Рµ baseline commit
`9001efec`. Р Р°Р·РґРµР»С‹ 1вЂ“14 РѕСЃС‚Р°СЋС‚СЃСЏ РёСЃС…РѕРґРЅС‹Рј architecture inventory.

### 15.1 ExperimentExecution

Р”Р»СЏ РѕРґРёРЅРѕС‡РЅРѕРіРѕ production market experiment СЂРµР°Р»РёР·РѕРІР°РЅ РѕС‚РґРµР»СЊРЅС‹Р№
С‚РµС…РЅРёС‡РµСЃРєРёР№ lifecycle:

- immutable `ExperimentExecution`;
- СЃРѕСЃС‚РѕСЏРЅРёСЏ `PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED` Рё `CANCELLED`;
- deterministic fingerprint РїРѕР»РЅРѕР№ `MarketExperimentSpecification`;
- `ExperimentExecutionFactory`;
- `ExperimentExecutionTrackingExecutor`;
- append-only `SqliteExperimentExecutionRecorder`;
- SQLite-С‚Р°Р±Р»РёС†Р° `experiment_execution_snapshots`;
- wiring РІ РѕР±РѕРёС… market composition roots.

Execution РїРµСЂРµРІРѕРґРёС‚СЃСЏ РІ `SUCCEEDED` СЃСЂР°Р·Сѓ РїРѕСЃР»Рµ РїРѕР»СѓС‡РµРЅРёСЏ РІР°Р»РёРґРЅРѕРіРѕ
`ExperimentResult`. РћС€РёР±РєРё РїРѕСЃР»РµРґСѓСЋС‰РµРіРѕ analysis, serialization РёР»Рё
artifact persistence РЅРµ РёР·РјРµРЅСЏСЋС‚ С‚РµС…РЅРёС‡РµСЃРєРёР№ outcome РІС‹РїРѕР»РЅРµРЅРёСЏ.

Pending execution РїРѕРєР° СЃРѕР·РґР°С‘С‚СЃСЏ РїРѕСЃР»Рµ mapping, Р·Р°РіСЂСѓР·РєРё dataset Рё
РїРѕСЃС‚СЂРѕРµРЅРёСЏ `ResearchContext`. РџРѕСЌС‚РѕРјСѓ preparation failures РґРѕ СЃРѕР·РґР°РЅРёСЏ
session РµС‰С‘ РЅРµ РёРјРµСЋС‚ persistent execution record.

### 15.2 ResearchArtifactEnvelope

Р”Р»СЏ РѕРґРёРЅРѕС‡РЅРѕРіРѕ production market path СЂРµР°Р»РёР·РѕРІР°РЅС‹:

- `ResearchArtifactEnvelope`;
- `ResearchArtifactSourceReference`;
- `ResearchArtifactEnvelopeFactory`;
- canonical SHA-256 fingerprint payload;
- immutable JSON snapshots payload Рё provenance;
- integrity-aware envelope loader;
- СЃРѕРІРјРµСЃС‚РёРјРѕРµ С‡С‚РµРЅРёРµ legacy Рё envelope artifacts.

Envelope `market_research_cycle` СЃРѕРґРµСЂР¶РёС‚ РѕС‚РґРµР»СЊРЅС‹Р№ `artifact_id`,
producer metadata, execution Рё result source references, specification
Рё environment provenance, payload fingerprint Рё СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёР№
С‚РёРїРёР·РёСЂРѕРІР°РЅРЅС‹Р№ market research payload.

Legacy writer СЃРѕС…СЂР°РЅСЏРµС‚СЃСЏ РґР»СЏ РЅРµРјРёРіСЂРёСЂРѕРІР°РЅРЅС‹С… РІС‹Р·РѕРІРѕРІ.
`ArtifactComparisonInputExtractor` РїСЂРёРЅРёРјР°РµС‚ РѕР±Р° С„РѕСЂРјР°С‚Р° Рё РёСЃРїРѕР»СЊР·СѓРµС‚
РІРЅРµС€РЅРёР№ envelope artifact ID РґР»СЏ РЅРѕРІС‹С… artifacts.

Campaign, comparative Evidence, Finding, HypothesisEvaluation,
Knowledge snapshot Рё research-question artifacts РїРѕРєР° РЅРµ РјРёРіСЂРёСЂРѕРІР°РЅС‹.

### 15.3 Production market path

Specification JSON
в†’ `RunMarketResearch`
в†’ `MarketResearchSessionFactory`
в†’ canonical dataset Рё `ResearchContext`
в†’ `ExperimentExecution`
в†’ tracking executor
в†’ prepared market executor
в†’ execution snapshots РІ SQLite
в†’ legacy `ResearchEngine`
в†’ typed market research payload
в†’ `ResearchArtifactEnvelope`
в†’ `SqliteResearchCycleStore`.

### 15.4 РЎРѕС…СЂР°РЅСЏСЋС‰РёРµСЃСЏ СЂР°Р·СЂС‹РІС‹

РќР° commit `21f855a`:

- preparation failures РµС‰С‘ РЅРµ СЃРѕС…СЂР°РЅСЏСЋС‚СЃСЏ;
- lifecycle-level `correlation_id` РїРѕРєР° РЅРµ РїРµСЂРµРґР°С‘С‚СЃСЏ;
- campaign execution РЅРµ РёСЃРїРѕР»СЊР·СѓРµС‚ РµРґРёРЅС‹Р№ execution lifecycle;
- Р±РѕР»СЊС€РёРЅСЃС‚РІРѕ artifact types РѕСЃС‚Р°СЋС‚СЃСЏ legacy;
- HypothesisEvaluation в†’ KnowledgeCandidate РЅРµ РёРјРµРµС‚ production use case;
- Knowledge repositories РЅРµ РїРѕРґРєР»СЋС‡РµРЅС‹ Рє production composition root;
- Knowledge snapshot РїРѕСЃС‚СѓРїР°РµС‚ С‡РµСЂРµР· СЂСѓС‡РЅРѕР№ JSON-С„Р°Р№Р»;
- Analysis в†’ Knowledge в†’ Recommendation РЅРµ СЏРІР»СЏРµС‚СЃСЏ РµРґРёРЅС‹Рј
  in-process production path.

РћР±С‰РёР№ workflow, lifecycle, pipeline РёР»Рё orchestration engine РЅРµ
РґРѕР±Р°РІР»СЏР»СЃСЏ.

## 16. Knowledge production vertical path

Commit checkpoint: `6baf850`.

Этот раздел фиксирует фактическую дельту после checkpoint
`21f855a`. Разделы 1–15 сохраняют состояние соответствующих
архитектурных снимков.

### 16.1 Explicit Knowledge promotion

Production comparative request поддерживает необязательный блок
`knowledge_promotion`. Без него comparative route завершает работу
артефактом HypothesisEvaluation v1 и не изменяет Knowledge.

При явном запросе production command передаёт HypothesisEvaluation в
`PromoteHypothesisEvaluationToKnowledge`. Application use case:

- применяет `KnowledgePromotionPolicy`;
- создаёт `KnowledgeCandidate`;
- выполняет `KnowledgeCandidateValidator`;
- сохраняет начальную `KnowledgeRevision`;
- запускает contradiction detection;
- сохраняет относящиеся к новой revision contradictions;
- регистрирует contradiction relations.

Production policy допускает только состояние `SUPPORTED`,
confidence не ниже `0.75` и не менее двух supporting findings.

Promotion остаётся явным пользовательским намерением. Application
Layer выполняет переход, но решение о допустимости принимает domain
policy.

При выполненной promotion comparative presenter возвращает
HypothesisEvaluation artifact v2 с `knowledge_revision`. Без
promotion сохраняется совместимый artifact v1.

### 16.2 Production Knowledge persistence

Главный `build_research_cli` создаёт:

- `SqliteKnowledgeRepository`;
- `SqliteKnowledgeRelationRepository`;
- `PromoteHypothesisEvaluationToKnowledge`;
- `BuildKnowledgeGraphSnapshot`;
- `GenerateResearchQuestionsFromKnowledgeRepositoriesCommand`.

Promotion application и snapshot builder используют одни и те же
экземпляры SQLite repositories в пределах composition root.

`SqliteKnowledgeRepository` и
`SqliteKnowledgeRelationRepository` теперь входят в production
dependency graph. Статус раздела 9 «Не подключён» относится только к
baseline inventory на commit `9001efec`.

Production composition передаёт пустой набор explicit contradiction
rules. Contradiction infrastructure подключена, но автоматические
семантические правила в production пока не активированы.

### 16.3 Repository-backed Knowledge feedback

Production route
`generate-knowledge-research-questions` больше не принимает snapshot
JSON. Command:

- читает revisions и relations из SQLite repositories;
- строит `KnowledgeGraphSnapshot`;
- определяет gaps;
- создаёт recommendations;
- преобразует их в ResearchQuestion;
- возвращает research-question artifact v1.

`KnowledgeGraphSnapshotLoader` и file-based snapshot command остаются
legacy-compatible components, но главный production route их не
использует.

Manual Knowledge snapshot больше не является границей между persistent
Knowledge и production question generation.

### 16.4 Наблюдаемый production-capable path

Фактическая цепочка имеет вид:

HypothesisEvaluation
→ explicit PromotionPolicy decision
→ KnowledgeCandidate validation
→ KnowledgeRevision в SQLite
→ contradiction detection
→ relation registration
→ repository-backed KnowledgeGraphSnapshot
→ KnowledgeGap
→ ResearchRecommendation
→ ResearchQuestion.

Comparative evaluation с promotion и последующая генерация вопросов
являются двумя отдельными CLI use cases, связанными общей SQLite
persistence, а не одним универсальным workflow.

Production integration test подтверждает путь от поддержанной
HypothesisEvaluation через реальную promotion application и общий
SQLite repository до repository-backed research question generation.

### 16.5 Сохраняющиеся ограничения

На commit `6baf850`:

- Knowledge promotion выполняется только по явному запросу;
- production contradiction rules пока отсутствуют;
- comparative HypothesisEvaluation и research-question artifacts ещё
  не используют общий `ResearchArtifactEnvelope`;
- integration test начинает вертикальную проверку с готовой
  HypothesisEvaluation;
- единый автоматический запуск от experiment specification до
  follow-up ResearchQuestion пока не является одним Application use
  case;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся;
- новые Knowledge domain entities не добавлялись.

## 17. Application API and HypothesisEvaluation envelope

Commit checkpoint: `7d43bdc`.

Этот раздел фиксирует фактическую дельту после Knowledge production
checkpoint. Предыдущие разделы сохраняют состояние соответствующих
архитектурных снимков.

### 17.1 Application use-case classification

Принят
`ADR-005-application-use-case-classification.md`.

Application components разделены по архитектурной роли:

- Public Use Case;
- Internal Coordinator;
- Boundary Adapter;
- Port;
- Factory / Composition Root;
- Legacy Compatibility Component.

Классификация не вводит общий base class, runtime registry или
WorkflowEngine.

Создан отдельный `src.application.public_api` с явным allowlist
поддерживаемых use cases и application results.

Legacy `src.application.__init__` не очищался и продолжает выполнять
compatibility-функцию. Package export больше не считается
доказательством публичности Application contract.

### 17.2 Repository-backed question use case

Создан публичный application-level use case
`GenerateResearchQuestionsFromKnowledgeRepositories`.

Use case:

- строит snapshot через persistent Knowledge ports;
- передаёт snapshot существующему question generator;
- возвращает типизированный
  `KnowledgeResearchQuestionsResult`.

`GenerateResearchQuestionsFromKnowledgeRepositoriesCommand` теперь
является тонким CLI adapter. Он вызывает один Application use case и
передаёт его result в presenter.

Snapshot construction и question-generation orchestration больше не
выполняются внутри CLI command.

### 17.3 HypothesisEvaluation envelope writer

Создана специализированная
`HypothesisEvaluationArtifactEnvelopeFactory`.

Factory использует общий `ResearchArtifactEnvelopeFactory` и
формирует:

- artifact type `hypothesis_evaluation`;
- payload schema version 1 без Knowledge promotion;
- payload schema version 2 с `knowledge_revision`;
- exact HypothesisEvaluation source reference;
- exact-version KnowledgeRevision reference при promotion;
- evaluation fingerprint, state и hypothesis identity в provenance;
- canonical payload fingerprint.

Главный production composition root передаёт factory в comparative
command и получает `producer_version` через
`GitCodeVersionProvider`.

Production comparative route теперь возвращает
`ResearchArtifactEnvelope`.

`correlation_id` остаётся `null`, потому что comparative request
пока не содержит отдельный lifecycle correlation contract.
Использовать `hypothesis_id` вместо correlation identity
запрещено.

### 17.4 Legacy writer compatibility

`RunIndicatorComparativeHypothesisEvaluationCommand` принимает
specialized envelope factory как optional dependency.

Без factory command продолжает поддерживать legacy outputs:

- HypothesisEvaluation artifact v1;
- HypothesisEvaluation artifact v2 с KnowledgeRevision.

Это сохраняет совместимость немигрированных composition roots и
unit-level consumers.

Главный production root всегда передаёт envelope factory.

### 17.5 Specialized artifact loader

Создан `HypothesisEvaluationArtifactLoader`.

Loader поддерживает:

- legacy artifact version 1;
- legacy artifact version 2;
- envelope payload schema version 1;
- envelope payload schema version 2.

При чтении loader:

- проверяет общий envelope payload fingerprint;
- проверяет artifact type и payload schema version;
- отклоняет отсутствующие и неизвестные поля;
- восстанавливает immutable `HypothesisEvaluation`;
- восстанавливает optional `KnowledgeRevision` и `KnowledgeItem`;
- повторно проверяет evaluation, item и revision fingerprints;
- возвращает типизированный
  `LoadedHypothesisEvaluationArtifact`.

Таким образом HypothesisEvaluation migration имеет production writer,
legacy compatibility и integrity-aware reader.

### 17.6 Обновлённый artifact path

Production comparative artifact path:

Comparative request JSON
→ comparative analysis
→ Evidence
→ Finding
→ HypothesisEvaluation
→ optional Knowledge promotion
→ specialized envelope factory
→ `ResearchArtifactEnvelope`
→ CLI JSON.

HypothesisEvaluation и optional KnowledgeRevision остаются
типизированными payload contracts и не наследуются от envelope.

### 17.7 Сохраняющиеся ограничения

На commit `7d43bdc`:

- Evidence и Finding artifacts остаются legacy;
- research-question artifact остаётся legacy;
- comparative envelope пока возвращается через CLI и не имеет
  отдельного persistent artifact store;
- comparative lifecycle не передаёт `correlation_id`;
- production contradiction rules пока отсутствуют;
- integration test полного comparative request с реальным market
  execution до follow-up ResearchQuestion ещё отсутствует;
- campaign artifacts не мигрированы на общий envelope;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся;
- новые Knowledge domain entities не добавлялись.
## 18. Knowledge research-question envelope checkpoint

Commit checkpoint: `1db06ff`.

Этот раздел фиксирует фактическую дельту после Application API и
HypothesisEvaluation envelope checkpoint. Предыдущие разделы сохраняют
состояние соответствующих архитектурных снимков.

### 18.1 Третий production envelope scenario

Создана специализированная
`KnowledgeResearchQuestionsArtifactEnvelopeFactory`.

Factory использует общий `ResearchArtifactEnvelopeFactory` и формирует:

- artifact type `knowledge_research_questions`;
- payload schema version 1;
- полный immutable `KnowledgeGraphSnapshot` в payload;
- отдельный snapshot fingerprint;
- количество вопросов и типизированные ResearchQuestion payloads;
- exact Knowledge snapshot source reference;
- количество Knowledge items и relations в provenance;
- canonical payload fingerprint.

Полный snapshot включён в artifact, поэтому результат можно проверить
и воспроизвести без обращения к изменившемуся состоянию repositories.

Главный production composition root передаёт factory в
`GenerateResearchQuestionsFromKnowledgeRepositoriesCommand`.
`producer_version` получается через тот же
`GitCodeVersionProvider`, который используется comparative artifact
producer.

Без factory command сохраняет legacy question artifact v1 для
немигрированных composition roots. Главный production root всегда
использует envelope factory.

### 18.2 Integrity-aware question artifact reader

Создан `KnowledgeResearchQuestionsArtifactLoader`.

Loader принимает полный envelope payload schema version 1 и:

- проверяет общий payload fingerprint;
- проверяет artifact type и payload schema version;
- отклоняет отсутствующие и неизвестные payload fields;
- восстанавливает `KnowledgeGraphSnapshot` через существующий
  `KnowledgeGraphSnapshotLoader`;
- повторно проверяет snapshot fingerprint;
- восстанавливает immutable `ResearchQuestion` values;
- проверяет question count и уникальность question identities;
- проверяет exact Knowledge snapshot source reference;
- возвращает типизированные
  `KnowledgeResearchQuestionsResult` и `ResearchArtifactEnvelope`.

Legacy question artifact v1 loader не поддерживает намеренно: legacy
payload содержит только snapshot fingerprint, но не полный snapshot.
Восстановить из него типизированный воспроизводимый Application result
невозможно без внешнего состояния.

### 18.3 Lifecycle correlation

Comparative evaluation request теперь поддерживает необязательный
нормализованный `correlation_id`. Production comparative command
передаёт его в HypothesisEvaluation envelope.

CLI route `generate-knowledge-research-questions` поддерживает
необязательный `--correlation-id` и передаёт его в Knowledge-question
envelope.

`correlation_id` используется только для трассировки связанных
artifacts. Он не заменяет:

- hypothesis identity;
- HypothesisEvaluation identity;
- Knowledge identity и version;
- Knowledge snapshot fingerprint;
- ResearchQuestion identity.

Comparative evaluation и question generation остаются двумя отдельными
use cases. Correlation не распространяется через Knowledge repositories
автоматически: вызывающий клиент должен явно передать одно и то же
значение в оба lifecycle шага.

### 18.4 Подтверждённая общая envelope-граница

Общий `ResearchArtifactEnvelope` теперь используется тремя независимыми
production scenarios:

1. market research cycle;
2. comparative HypothesisEvaluation с optional KnowledgeRevision;
3. repository-backed Knowledge research questions.

Это подтверждает повторяющийся boundary contract на трёх сценариях без
создания общего WorkflowEngine, lifecycle aggregate или универсального
domain artifact.

Domain payloads остаются раздельными и типизированными. Envelope
используется только на границах хранения и обмена.

### 18.5 Обновлённый Knowledge feedback artifact path

Фактический production path имеет вид:

HypothesisEvaluation envelope
→ explicit Knowledge promotion
→ KnowledgeRevision и relations в SQLite
→ repository-backed KnowledgeGraphSnapshot
→ KnowledgeGap
→ ResearchRecommendation
→ ResearchQuestion
→ Knowledge-question envelope.

При явной передаче одинакового `correlation_id` начальный
HypothesisEvaluation artifact и итоговый Knowledge-question artifact
образуют трассируемый lifecycle без прямой зависимости между их
domain identities.

### 18.6 Сохраняющиеся ограничения

На commit `1db06ff`:

- Evidence и Finding artifacts остаются legacy;
- campaign artifacts не используют общий envelope;
- comparative и Knowledge-question envelopes возвращаются через CLI,
  но не имеют отдельного persistent artifact store;
- полный автоматический запуск от experiment specification до
  follow-up ResearchQuestion не является одним Application use case;
- integration test вертикального Knowledge path начинается с готовой
  HypothesisEvaluation;
- production contradiction rules пока отсутствуют;
- correlation между отдельными CLI use cases передаётся клиентом;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся;
- новые Knowledge domain entities не добавлялись.
