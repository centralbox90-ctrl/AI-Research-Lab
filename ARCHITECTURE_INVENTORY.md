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

## 19. Market research campaign envelope checkpoint

Commit checkpoint: `5ca8bcb`.

Этот раздел фиксирует фактическую дельту после Knowledge
research-question envelope checkpoint. Предыдущие разделы сохраняют
состояние соответствующих архитектурных снимков.

### 19.1 Типизированный Campaign result

`MarketResearchCampaignExperimentResult.result` больше не является
`object`. Campaign execution использует
`NextExperimentResearchCycleResult` как явный Application contract.

`MarketResearchExperimentRunner.execute` возвращает тот же
типизированный result. `RunMarketResearchCampaign` проверяет runtime
тип каждого результата до включения в Campaign result.

Технический статус отдельных запусков продолжает принадлежать
`ExperimentExecution`. Campaign result агрегирует завершённые
Application results и не вводит общий lifecycle aggregate.

### 19.2 Campaign artifact payload boundary

Создан
`MarketResearchCampaignArtifactPayloadFactory`.

Factory формирует Campaign payload из:

- identity и fingerprint `ResearchCampaignPlan`;
- полного сериализованного Campaign plan;
- количества экспериментов;
- planned experiment identities;
- вложенных market research artifacts.

`MarketResearchCampaignPresenter` делегирует построение payload этой
factory и сохраняет legacy artifact version 1 для немигрированных
composition roots.

Payload factory является boundary adapter. Она не становится domain
base class и не изменяет модели Research Campaign.

### 19.3 Четвёртый production envelope scenario

Создана специализированная
`MarketResearchCampaignArtifactEnvelopeFactory`.

Factory использует общий `ResearchArtifactEnvelopeFactory` и формирует:

- artifact type `market_research_campaign`;
- payload schema version 1;
- Campaign payload из специализированной payload factory;
- exact ResearchCampaignPlan source reference с fingerprint;
- source reference каждого выполненного ExperimentResult;
- Campaign plan identity, fingerprint и experiment count в provenance;
- canonical payload fingerprint.

Главный `build_research_cli` передаёт Campaign envelope factory в
`RunMarketResearchCampaignCommand`.

`producer_version` получается через `GitCodeVersionProvider`.
Production producer имеет identity `market-research-campaign`.

Без envelope factory command продолжает использовать legacy
`MarketResearchCampaignPresenter`. Главный production composition root
всегда использует envelope factory.

Общий `ResearchArtifactEnvelope` теперь подтверждён четырьмя
production scenarios:

1. market research cycle;
2. comparative HypothesisEvaluation;
3. repository-backed Knowledge research questions;
4. market research campaign.

Новый общий workflow, lifecycle, pipeline или orchestration mechanism
для этого не вводился.

### 19.4 Campaign lifecycle correlation

CLI route `run-market-research-campaign` поддерживает необязательный
`--correlation-id`.

`ResearchCli` передаёт значение в
`RunMarketResearchCampaignCommand`, а command передаёт его только в
Campaign envelope factory.

`correlation_id` нормализуется общим envelope contract и используется
только для трассировки. Он не заменяет:

- CampaignDesign identity;
- ResearchCampaignPlan identity и fingerprint;
- planned experiment identity;
- ExperimentExecution identity;
- ExperimentResult identity.

Без явного CLI-параметра `correlation_id` остаётся `null`.

### 19.5 Production Campaign execution path

Фактический production path имеет вид:

CampaignDesign JSON
→ `ResearchPlanner`
→ deterministic `ResearchCampaignPlan`
→ registration resolver
→ `ResearchCampaignPlanMarketAdapter`
→ tracking-enabled `RunMarketResearch`
→ отдельный `ExperimentExecution` для каждого market experiment
→ typed `NextExperimentResearchCycleResult`
→ typed `MarketResearchCampaignResult`
→ Campaign payload factory
→ Campaign envelope factory
→ CLI JSON.

Campaign планирует, разрешает и агрегирует исследовательские
эксперименты. Scheduling, retries, worker leases и heartbeat в
Research Domain не добавлялись.

### 19.6 Сохраняющиеся ограничения

На commit `5ca8bcb`:

- Campaign envelope возвращается через CLI, но не имеет отдельного
  persistent artifact store;
- специализированный integrity-aware Campaign artifact loader пока
  отсутствует;
- вложенные market research artifacts сохраняют существующий
  сериализованный контракт;
- Campaign не управляет retries, scheduling или worker state;
- Evidence и Finding standalone artifacts остаются legacy;
- полный автоматический запуск от experiment specification до
  follow-up ResearchQuestion не является одним Application use case;
- production contradiction rules пока отсутствуют;
- correlation между отдельными use cases передаётся клиентом явно;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся;
- новые Knowledge domain entities не добавлялись.

## 20. Comparative ExperimentExecution production checkpoint

Commit checkpoint: `3fc7999`.

Этот раздел фиксирует фактическое завершение production wiring
технического lifecycle для comparative analysis. Предыдущие разделы
сохраняют состояние соответствующих архитектурных снимков.

### 20.1 Reproducible comparative execution specification

Создан immutable
`IndicatorComparativeExecutionSpecification`.

Specification фиксирует полный воспроизводимый вход одного
comparative analysis execution:

- market experiment specification;
- точный период market data;
- indicator research specification;
- forward outcome specification;
- baseline identity.

Specification имеет deterministic fingerprint.

Statistical evaluation plan намеренно не входит в execution
specification. Statistical evaluation выполняется после успешного
comparative analysis и относится к научной интерпретации результата,
а не к техническому выполнению эксперимента.

### 20.2 Comparative execution tracker

Создан специализированный
`IndicatorComparativeExecutionTracker`.

Tracker оборачивает один вызов
`IndicatorComparativeResearchService` и записывает immutable
`ExperimentExecution` snapshots:

1. `PENDING`;
2. `RUNNING`;
3. `SUCCEEDED` или `FAILED`.

Dataset preparation выполняется до tracker.

Comparative statistical evaluation, Evidence, Finding и
HypothesisEvaluation формируются после tracker и не изменяют
технический execution status.

Tracker не управляет:

- retries;
- scheduling;
- worker leases;
- heartbeat;
- очередями;
- runtime recovery.

Общий workflow или lifecycle engine не вводился.

### 20.3 Production persistence wiring

Главный `build_research_cli` создаёт общий
`SqliteExperimentExecutionRecorder`.

Тот же recorder используется:

- одиночным market research execution;
- market research campaign executions;
- comparative analysis executions.

Recorder передаётся через явные composition roots:

`build_research_cli`
→ comparative hypothesis-evaluation builder
→ comparative finding builder
→ comparative evidence builder
→ comparative research builder
→ `IndicatorComparativeExecutionTracker`.

Application и Research layers не импортируют SQLite adapter.
Persistence остаётся подключённой только в composition root через
`ExperimentExecutionRecorder` port.

Каждая попытка comparative analysis получает отдельный UUID
`execution_id`. Specification fingerprint и experiment identity
остаются deterministic и не подменяют identity конкретной попытки.

### 20.4 Environment and code version

Comparative research application формирует environment fingerprint из:

- canonical dataset fingerprint;
- application code version;
- comparative executor version.

Production code version поступает из существующего
`GitCodeVersionProvider`.

Техническое окружение сохраняется в `RUNNING`, `SUCCEEDED` и `FAILED`
execution snapshots. Оно не включается в scientific Evidence или
HypothesisEvaluation state.

### 20.5 Lifecycle correlation

`correlation_id` передаётся по фактическому production path:

Comparative request JSON
→ CLI command
→ HypothesisEvaluation application
→ Finding application
→ Evidence application
→ comparative research application
→ execution tracker
→ SQLite snapshots.

Correlation используется только для трассировки связанных executions
и artifacts.

Он не заменяет:

- execution identity;
- experiment identity;
- specification fingerprint;
- Finding identity;
- HypothesisEvaluation identity;
- Knowledge identity.

### 20.6 Production integration evidence

Production integration test выполняет реальный comparative request,
содержащий:

- две Finding requests;
- два независимых market data периода в каждой request;
- один общий lifecycle correlation identifier.

Тест подтверждает четыре отдельных comparative executions.

Для каждого execution SQLite содержит точную последовательность:

`PENDING`
→ `RUNNING`
→ `SUCCEEDED`.

Всего сохраняется двенадцать append-only snapshots.

Тест также подтверждает:

- отдельный UUID каждой попытки;
- последовательности snapshot numbers `1, 2, 3`;
- одинаковый request `correlation_id` во всех snapshots;
- отсутствие failure у успешных executions;
- наличие result identity в terminal snapshot.

### 20.7 Обновлённая граница execution и interpretation

Фактическая граница теперь выражена следующим образом:

`ExperimentExecution.status`
описывает техническое выполнение comparative analysis.

`ComparativeStatisticalEvaluation`,
`Evidence`,
`Finding` и
`HypothesisEvaluation`
описывают научную интерпретацию успешно полученного анализа.

`FAILED` execution не эквивалентен
`NOT_SUPPORTED`, `REJECTED` или `INCONCLUSIVE`
HypothesisEvaluation.

Domain statuses не используются для управления runtime queue.

### 20.8 Сохраняющиеся ограничения

На commit `3fc7999`:

- execution snapshots не имеют отдельного публичного CLI query use case;
- comparative HypothesisEvaluation envelope возвращается через CLI,
  но не сохраняется отдельным artifact store;
- Evidence и Finding standalone artifacts остаются legacy;
- полный автоматический запуск от experiment specification до
  follow-up ResearchQuestion не является одним Application use case;
- production contradiction rules пока отсутствуют;
- correlation между отдельными CLI use cases передаётся клиентом явно;
- retries, scheduling, worker leases и heartbeat не реализованы;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся;
- новые Knowledge domain entities не добавлялись.

## 21. HTTP API boundary checkpoint

Commit checkpoint: `55945d8`.

Этот раздел фиксирует первый внешний transport adapter после
завершения архитектурной консолидации.

### 21.1 Transport boundary

Создан отдельный package `src.api`.

HTTP adapter зависит только от явно переданных публичных Application
use cases.

Transport factory не импортирует:

- SQLite adapters;
- CLI commands;
- Research Domain services;
- Knowledge repositories;
- composition internals;
- indicator implementations.

HTTP adapter выполняет только:

- routing;
- вызов Application use case;
- формирование versioned transport DTO;
- преобразование отсутствующего результата в HTTP response.

Domain models и persistence contracts не становятся HTTP DTO.

### 21.2 Read-only use cases

Первый HTTP slice предоставляет два read-only operation:

- `GET /v1/research-cycles`;
- `GET /v1/research-artifacts/{result_id}`.

`GET /v1/research-cycles` вызывает
`ListStoredResearchCycles`.

Response schema version 1 содержит:

- `schema_version`;
- количество результатов;
- упорядоченные `result_ids`.

`GET /v1/research-artifacts/{result_id}` вызывает
`GetStoredResearchArtifact`.

Успешный response schema version 1 содержит:

- `schema_version`;
- точный `result_id`;
- сохранённый application-safe artifact payload.

Отсутствующий artifact возвращает JSON response со статусом 404 и
стабильным кодом `research_artifact_not_found`.

HTTP adapter не реконструирует Domain objects из сохранённого payload.

### 21.3 Production composition

Создан отдельный `src.api.composition_root`.

Composition root:

- создаёт `SqliteResearchCycleStore`;
- создаёт `GetStoredResearchArtifact`;
- создаёт `ListStoredResearchCycles`;
- передаёт use cases в transport factory.

SQLite выбирается только composition root.

`src.api.research_api` не зависит от `src.storage`.

Production integration tests подтверждают:

- чтение списка identifiers из реальной SQLite database;
- чтение сохранённого artifact;
- deterministic ordering;
- JSON 404 для отсутствующего artifact;
- пустую database без специальных branches в Application Layer.

### 21.4 OpenAPI contract

HTTP boundary публикует `GET /openapi.json`.

Документ использует OpenAPI 3.1.0 и API version 1.0.0.

OpenAPI document фиксирует:

- оба доступных path;
- уникальные operation identifiers;
- обязательный path parameter `result_id`;
- HTTP responses 200 и 404;
- exact transport schemas;
- обязательные DTO fields;
- запрет неизвестных верхнеуровневых response fields;
- свободный application-safe artifact object внутри
  `ResearchArtifact`.

OpenAPI contract строится отдельным boundary factory и не импортирует
Application, Domain или persistence models.

### 21.5 Local entry point

API можно запустить локально через module entry point:

`python -m src.api`.

Entry point принимает:

- SQLite database path;
- host;
- TCP port.

Без явных параметров используются:

- существующий default research database;
- host `127.0.0.1`;
- port `8000`.

Debug mode и automatic reloader отключены.

Port валидируется в диапазоне от 1 до 65535.

Пустой host отклоняется до запуска server.

Встроенный Flask server классифицирован только как local development
boundary. Он не считается production deployment server.

### 21.6 Подтверждённые границы

Первый HTTP slice не изменил:

- Domain Layer;
- Research lifecycle;
- ExperimentExecution;
- Knowledge Domain;
- public Application use cases;
- repositories;
- CLI routes;
- indicator plugin contract.

Новый indicator по-прежнему добавляется одним production module в
`src/indicators/implementations`.

HTTP adapter не создаёт universal request, response, workflow или
transport base class.

### 21.7 Сохраняющиеся ограничения

На commit `55945d8`:

- HTTP API является read-only;
- доступны только два публичных use case;
- authentication и authorization отсутствуют;
- TLS termination отсутствует;
- CORS policy не определена;
- rate limiting отсутствует;
- production WSGI deployment не настроен;
- встроенный server разрешён только для локальной разработки;
- MCP и ChatGPT adapters не реализованы;
- новые Knowledge domain entities не добавлялись;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся.
## 22. HTTP artifact comparison checkpoint

Commit checkpoint: `4be827d`.

Этот раздел фиксирует расширение read-only HTTP boundary после первого
HTTP API checkpoint. Предыдущие разделы сохраняют состояние
соответствующих архитектурных снимков.

### 22.1 Публичный comparison use case

HTTP adapter предоставляет новую операцию:

`GET /v1/research-artifact-comparisons`.

Операция вызывает существующий публичный Application use case
`CompareStoredResearchArtifacts`.

Обязательные query parameters:

- `artifact_a_result_id`;
- `artifact_b_result_id`.

Оба значения нормализуются на transport boundary и должны содержать
непустые строки.

HTTP adapter не загружает artifacts самостоятельно, не интерпретирует
их payload и не выполняет comparison rules. Эти ответственности
остаются в Application Layer.

### 22.2 Transport result

Успешный response использует schema version 1 и содержит:

- точный `artifact_a_result_id`;
- точный `artifact_b_result_id`;
- comparison DTO.

Comparison DTO содержит:

- идентичности сравниваемых artifacts;
- изменение гипотезы;
- изменение evidence;
- детерминированные metric deltas;
- изменение confidence.

Transport DTO формируется HTTP adapter из типизированного
`ArtifactComparison`.

HTTP response не сериализует repositories или persistence records и не
объявляет Application result HTTP-моделью.

### 22.3 Error contract

HTTP boundary явно различает три группы ошибок:

- status 400 для отсутствующих обязательных query parameters;
- status 404, если один из сохранённых artifacts не найден;
- status 422, если сохранённые artifacts не удовлетворяют comparison
  contract.

Каждый error response содержит:

- `schema_version`;
- стабильный error code;
- диагностическое message.

Неожиданные инфраструктурные исключения не маскируются под
application-level validation errors.

### 22.4 Production composition

`src.api.composition_root` создаёт
`CompareStoredResearchArtifacts` поверх того же
`GetStoredResearchArtifact`, который используется одиночным artifact
endpoint.

Для интерпретации сохранённых payload используется существующий
`ArtifactComparisonInputExtractor`.

Все три read-only HTTP operation используют одну
`SqliteResearchCycleStore`.

HTTP transport factory по-прежнему не импортирует SQLite adapter,
artifact extractor или composition internals.

Integration test подтверждает repository-backed comparison двух
сохранённых artifacts через реальную SQLite database.

### 22.5 OpenAPI 1.1

HTTP contract остаётся OpenAPI 3.1.0.

API version повышена с 1.0.0 до 1.1.0 как обратно совместимое
добавление нового read-only operation.

OpenAPI document фиксирует:

- оба обязательных query parameters;
- responses 200, 400, 404 и 422;
- exact comparison response schema;
- отдельные hypothesis, evidence и confidence evolution schemas;
- полный набор допустимых metric delta directions;
- точные error codes для statuses 400 и 422;
- запрет неизвестных верхнеуровневых DTO fields.

Произвольные evidence values остаются открытым application-safe
payload внутри строго типизированной transport envelope.

### 22.6 Подтверждённые границы

Расширение HTTP boundary не изменило:

- Domain Layer;
- Knowledge Domain;
- Knowledge feature freeze;
- Research lifecycle;
- ExperimentExecution;
- persistence schemas;
- CLI routes;
- public Application API;
- indicator plugin contract.

Comparison endpoint является read-only.

Write endpoints, общий transport base class, универсальный request DTO,
WorkflowEngine или lifecycle aggregate не добавлялись.

Добавление нового индикатора по-прежнему требует ровно одного
production module в `src/indicators/implementations`.

### 22.7 Сохраняющиеся ограничения

На commit `4be827d`:

- HTTP API остаётся read-only;
- доступны три публичных Application use case;
- authentication и authorization отсутствуют;
- TLS termination отсутствует;
- CORS policy не определена;
- rate limiting отсутствует;
- production WSGI deployment не настроен;
- встроенный Flask server используется только локально;
- MCP и ChatGPT adapters не реализованы;
- новые Knowledge domain entities не добавлялись;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся.

## 23. Production WSGI boundary checkpoint

Commit checkpoint: `253c324`.

Этот раздел фиксирует отдельный production server boundary после завершения read-only HTTP comparison slice.

### 23.1 Разделение entry points

Локальный entry point `python -m src.api` продолжает использовать встроенный Flask server только для разработки.

Production entry point `python -m src.api.production_server` использует Waitress и не вызывает `Flask.run`.

Оба entry point используют существующий `build_research_api` и не изменяют HTTP routes или Application use cases.

### 23.2 Runtime configuration

Production server принимает явные параметры:

- SQLite database path;
- bind host;
- TCP port;
- количество Waitress threads.

Defaults:

- существующая research database;
- host `127.0.0.1`;
- port `8080`;
- четыре threads.

Host не может быть пустым, port ограничен диапазоном 1–65535, количество threads должно быть положительным.

### 23.3 Dependency boundary

Waitress закреплён в `requirements.txt` точной версией 3.0.2.

Dependency импортируется только production server entry point и не входит в Application, Domain, Knowledge или storage contracts.

### 23.4 Security boundary

Production WSGI server не является полной network deployment configuration.

Отдельными deployment responsibilities остаются:

- TLS termination;
- authentication и authorization;
- CORS и rate limiting;
- reverse proxy;
- process supervision;
- secret management.

Default loopback binding предотвращает неявное внешнее опубликование API.

Write endpoints остаются запрещены до отдельного решения по authentication, authorization и idempotency.

### 23.5 Автоматические проверки

Тесты подтверждают использование Waitress, default и explicit runtime options, а также отклонение некорректных host, port и thread count.

Локальный Flask entry point тестируется отдельно.

Полный test suite и `pip check` проходят с закреплённой dependency.

### 23.6 Подтверждённые границы

Production WSGI slice не изменил:

- HTTP routes и OpenAPI contract;
- public Application API;
- Domain и Knowledge models;
- persistence schemas;
- Research lifecycle;
- indicator plugin contract.

WorkflowEngine, scheduler, worker queue, retries и lifecycle aggregate не добавлялись.

Добавление нового индикатора остаётся локальным изменением одного production module в `src/indicators/implementations`.

### 23.7 Сохраняющиеся ограничения

На commit `253c324`:

- HTTP API остаётся read-only;
- authentication, authorization и TLS отсутствуют;
- внешний reverse proxy и process supervision не настроены;
- MCP и ChatGPT adapters не реализованы;
- новые Knowledge domain entities не добавлялись;
- общий workflow, lifecycle, pipeline или orchestration engine не добавлялся.

## 24. First MCP adapter checkpoint

Commit checkpoint: `38b95c6`.

Этот раздел фиксирует первый работающий MCP vertical slice поверх
стабилизированного публичного Application API.

### 24.1 Protocol boundary

Создан отдельный пакет `src/mcp_adapter`.

MCP adapter использует закреплённый официальный Python SDK версии
2.0.0 и не изменяет:

- Domain models;
- Knowledge models;
- persistence contracts;
- HTTP API;
- Research lifecycle;
- indicator plugin contract.

MCP остаётся внешним adapter, аналогичным CLI и HTTP adapter.

### 24.2 Первый MCP tool contract

Опубликован read-only tool `list_research_cycles`.

Tool вызывает публичный Application use case
`ListStoredResearchCycles` и возвращает структурированный результат:

- schema version;
- количество результатов;
- упорядоченные result identities.

Tool явно помечен как:

- read-only;
- non-destructive;
- idempotent;
- closed-world.

MCP server не обращается напрямую к SQLite repository и не
восстанавливает Application orchestration внутри protocol adapter.

### 24.3 Production composition

Создан отдельный MCP composition root.

Фактическая цепочка зависимостей:

SQLite research cycle store
→ `ListStoredResearchCycles`
→ MCP server
→ `list_research_cycles`.

Composition root только собирает зависимости и не содержит
бизнес-ветвлений или lifecycle logic.

### 24.4 Stdio entry point

Создан production entry point:

`python -m src.mcp_adapter`.

Entry point принимает явный путь к SQLite database, собирает MCP
composition root и запускает стандартный stdio transport.

Запущенный stdio server ожидает MCP input. Для ручной остановки
используется `Ctrl+C`.

### 24.5 Protocol tests

Тесты используют настоящий in-memory MCP client из официального SDK.

Автоматически проверяются:

- discovery зарегистрированного tool;
- tool annotations;
- structured result contract;
- вызов публичного Application use case;
- repository-backed composition через временную SQLite database;
- default и explicit database path entry point;
- запуск stdio transport без блокировки тестового процесса.

### 24.6 Подтверждённые границы

Первый MCP slice не добавил:

- write tools;
- прямой доступ protocol adapter к repositories;
- новый Application use case;
- новую Knowledge entity;
- общий workflow engine;
- lifecycle aggregate;
- scheduler, retries или worker state;
- отдельную ChatGPT domain model.

Добавление нового индикатора по-прежнему требует ровно одного нового
production module в `src/indicators/implementations`.

### 24.7 Сохраняющиеся ограничения

На commit `38b95c6`:

- MCP adapter публикует только один read-only use case;
- получение отдельных artifacts через MCP ещё не реализовано;
- сравнение artifacts через MCP ещё не реализовано;
- authentication и authorization отсутствуют;
- внешний ChatGPT adapter отдельно не реализован;
- write operations через MCP запрещены;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся.

## 25. Complete read-only MCP surface checkpoint

Commit checkpoint: `be57383`.

Этот раздел фиксирует завершение read-only MCP surface поверх трёх
стабильных публичных Application use cases.

Предыдущий раздел сохраняет состояние первого MCP vertical slice на
commit `38b95c6`.

### 25.1 Три публичных MCP tools

MCP server предоставляет:

1. `list_research_cycles`;
2. `get_research_artifact`;
3. `compare_research_artifacts`.

Каждый tool:

- вызывает существующий public Application use case;
- возвращает отдельный structured transport DTO;
- помечен как read-only;
- помечен как non-destructive;
- помечен как idempotent;
- не объявляет open-world interaction.

MCP adapter не обращается напрямую к repositories.

### 25.2 Получение сохранённого artifact

Tool `get_research_artifact` вызывает
`GetStoredResearchArtifact`.

Входной `result_id` нормализуется на transport boundary.

Structured result содержит:

- schema version;
- нормализованный `result_id`;
- сохранённый artifact dictionary.

Отсутствующий artifact и некорректный Application result возвращаются
как контролируемые MCP tool errors.

Artifact не преобразуется в общий Domain object и не становится новой
Knowledge entity.

### 25.3 Сравнение сохранённых artifacts

Tool `compare_research_artifacts` вызывает
`CompareStoredResearchArtifacts`.

Входной contract содержит два независимых result identities.

Application use case:

- загружает artifacts через общий `GetStoredResearchArtifact`;
- интерпретирует legacy или enveloped payload через
  `ArtifactComparisonInputExtractor`;
- строит immutable `ArtifactComparison`.

MCP adapter только отображает готовый результат в structured DTO:

- hypothesis evolution;
- evidence evolution;
- metric deltas;
- confidence evolution.

Scientific comparison logic не дублируется внутри MCP adapter.

### 25.4 Production composition

MCP composition root собирает единую цепочку:

SQLite research cycle store
→ `GetStoredResearchArtifact`
→ `ListStoredResearchCycles`
→ `CompareStoredResearchArtifacts`
→ MCP server.

`CompareStoredResearchArtifacts` повторно использует тот же
`GetStoredResearchArtifact`, поэтому list, get и compare работают над
одним repository-backed состоянием.

Composition root выбирает infrastructure и adapters, но не содержит
transport routing, comparison rules или lifecycle transitions.

### 25.5 Protocol и integration tests

Protocol tests используют настоящий in-memory MCP client и проверяют:

- discovery трёх tools;
- input и output schemas;
- read-only annotations;
- нормализацию identifiers;
- structured results;
- контролируемые ошибки Application use cases;
- отклонение некорректных injected dependencies.

SQLite integration tests подтверждают:

- детерминированное перечисление research cycles;
- получение сохранённого artifact;
- сравнение двух реально сохранённых artifacts;
- передачу hypothesis, evidence, metric delta и confidence evolution.

HTTP и MCP adapters используют одинаковые public Application use cases,
но сохраняют отдельные transport DTO.

Общий transport serializer не вводился: повторяющийся lifecycle
mechanism на трёх независимых transport scenarios пока не подтверждён.

### 25.6 Подтверждённые архитектурные границы

Завершение read-only MCP surface не изменило:

- Domain models;
- Knowledge models;
- persistence schemas;
- Research lifecycle;
- ExperimentExecution lifecycle;
- HTTP routes и OpenAPI contract;
- CLI contracts;
- indicator plugin contract.

Write tools, authentication, authorization, retries, scheduling,
workers и queue state не добавлялись.

Добавление нового индикатора по-прежнему требует ровно одного нового
production module в `src/indicators/implementations`.

### 25.7 Сохраняющиеся ограничения

На commit `be57383`:

- MCP transport использует только stdio;
- MCP surface остаётся строго read-only;
- authentication и authorization отсутствуют;
- отдельный ChatGPT adapter не добавлен без подтверждённого consumer
  contract;
- write operations требуют отдельного решения по authorization,
  idempotency и audit;
- новые Knowledge domain entities не добавлялись;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся.

## 26. Campaign artifact reader checkpoint

Commit checkpoint: `2e2e124`.

Этот раздел фиксирует integrity-aware read boundary для уже
существующего Market Research Campaign envelope.

Предыдущие разделы сохраняют состояние соответствующих архитектурных
снимков.

### 26.1 Specialized Application loader

Создан `MarketResearchCampaignArtifactLoader`.

Loader принимает только `ResearchArtifactEnvelope` с:

- artifact type `market_research_campaign`;
- payload schema version 1;
- корректным общим payload fingerprint;
- полным Campaign plan;
- непустым набором experiment artifacts.

Общий envelope contract проверяет целостность serialized payload до
интерпретации Campaign semantics.

### 26.2 Восстановление типизированного плана

Loader восстанавливает:

- immutable `CampaignExperimentSpecification`;
- immutable `ResearchCampaignPlan`;
- deterministic specification identities;
- Campaign plan identity и fingerprint;
- plan provenance.

После восстановления выполняется canonical round-trip через
существующие `to_dict` contracts.

Serialized plan ID и каждый planned specification ID повторно
проверяются по вычисляемым fingerprints.

Новая Campaign domain model не создавалась.

### 26.3 Проверка experiment bindings

Для каждого experiment entry loader проверяет:

- точный набор обязательных полей;
- planned experiment identity;
- соответствие planned specification позиции в Campaign plan;
- artifact version;
- наличие serialized market specification;
- наличие research cycle;
- identity вложенного `ExperimentResult`.

Количество и порядок experiment entries должны точно соответствовать
детерминированному `ResearchCampaignPlan`.

### 26.4 Provenance и source references

Envelope provenance должен точно совпадать с:

- provenance Campaign plan;
- Campaign design identity;
- Campaign plan identity;
- Campaign plan fingerprint;
- question identity;
- experiment count.

Первый source reference должен указывать на точный
`ResearchCampaignPlan` и его fingerprint.

Остальные source references должны в том же порядке указывать на
точные identities вложенных `ExperimentResult`.

### 26.5 Loaded Application result

Loader возвращает immutable
`LoadedMarketResearchCampaignArtifact`.

Result содержит:

- восстановленный `ResearchCampaignPlan`;
- упорядоченные
  `LoadedMarketResearchCampaignExperimentArtifact`;
- исходный проверенный `ResearchArtifactEnvelope`.

Вложенные serialized market research artifacts остаются frozen
Application snapshots.

Loader не восстанавливает runtime `MarketResearchCampaignResult`,
не запускает experiments повторно и не обращается к repositories.

### 26.6 Подтверждённые границы

Campaign reader slice не добавил:

- общий artifact loader framework;
- universal payload DTO;
- новый public Application use case;
- новый CLI, HTTP или MCP route;
- новый persistent artifact store;
- новую Research или Knowledge entity;
- workflow, lifecycle, pipeline или orchestration engine;
- retries, scheduling, workers или queue state.

Knowledge feature freeze и локальный indicator plugin contract
сохранены.

### 26.7 Сохраняющиеся ограничения

На commit `2e2e124`:

- Campaign envelope возвращается через CLI без отдельного persistent
  artifact store;
- вложенные market research artifacts сохраняют существующий
  serialized contract;
- standalone Evidence и Finding artifacts остаются legacy;
- production contradiction rules представлены пустой явной
  конфигурацией;
- correlation между отдельными use cases передаётся клиентом явно;
- полный production lifecycle намеренно не объединён в один
  Application use case;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся.

## 27. ExperimentExecution history checkpoint

Commit checkpoint: `79445e9`.

Этот раздел фиксирует завершённый read-only vertical slice для
существующих append-only `ExperimentExecution` snapshots.

### 27.1 Public Application use case

Создан публичный use case `GetExperimentExecutionHistory`.

Use case:

- нормализует execution identity;
- читает полную append-only history через отдельный port;
- проверяет tuple contract и тип каждого snapshot;
- отклоняет snapshots другой execution identity;
- возвращает пустой tuple для отсутствующей history.

`GetExperimentExecutionHistory` добавлен в явный
`src.application.public_api`.

Use case не изменяет execution state и не интерпретирует научные
результаты.

### 27.2 Internal read port

Создан внутренний `ExperimentExecutionHistoryReader`.

Port определяет только операцию `history` и не экспортируется как
публичный Application use case.

Write-only `ExperimentExecutionRecorder` не расширялся.
Общий repository base class не создавался.

### 27.3 CLI contract

Создан `GetExperimentExecutionHistoryCommand` и route:

`get-experiment-execution-history <execution_id>`.

Versioned JSON schema 1 содержит:

- `execution_id`;
- `snapshot_count`;
- упорядоченный массив `snapshots`.

Route поддерживает pretty и compact JSON.

Exit codes:

- `0` — history найдена;
- `1` — history отсутствует или identifier отклонён;
- `2` — command dependency не настроена.

### 27.4 Production composition

Главный `build_research_cli` использует один
`SqliteExperimentExecutionRecorder` как write adapter и как read
adapter для `GetExperimentExecutionHistory`.

Новая таблица, второй repository и копирование snapshots не
создавались.

Production integration test записывает последовательность
`PENDING` → `RUNNING` → `SUCCEEDED` и читает её через реальный CLI
route из той же SQLite database.

### 27.5 Архитектурная граница

`ExperimentExecution.status` описывает только техническое
выполнение и не смешивается с `Evidence`, `Finding`,
`HypothesisEvaluation` или Knowledge promotion.

Queue, retries, scheduling, leases и heartbeat не добавлялись.

### 27.6 Подтверждённые ограничения

На commit `79445e9`:

- route остаётся read-only;
- HTTP и MCP surfaces не расширялись;
- persistence schema не изменялась;
- execution history не объявлялась новым artifact type;
- Knowledge feature freeze сохранён;
- добавление indicator остаётся локальным изменением одного
  production module;
- общий workflow, lifecycle, pipeline или orchestration engine не
  добавлялся.

## 28. ExperimentExecution listing checkpoint

Commit checkpoint: `72e5167`.

Этот раздел фиксирует завершённый read-only vertical slice для
обнаружения сохранённых technical execution identities.

### 28.1 Persistence query

`SqliteExperimentExecutionRecorder` предоставляет
`list_execution_ids`.

Query:

- читает distinct `execution_id` из существующей append-only таблицы;
- не загружает и не дублирует snapshots;
- возвращает identities в детерминированном порядке;
- возвращает пустой tuple для пустой базы.

Новая таблица, index или отдельный repository не создавались.

### 28.2 Public Application use case

Создан публичный use case `ListExperimentExecutions`.

Use case работает через внутренний `ExperimentExecutionCatalog`,
проверяет tuple contract, тип, непустую identity и уникальность каждого
`execution_id`, затем возвращает отсортированный tuple.

`ListExperimentExecutions` добавлен в явный
`src.application.public_api`.

Внутренний port не экспортируется как публичный Application use case.

### 28.3 CLI contract

Создан `ListExperimentExecutionsCommand` и route:

`list-experiment-executions`.

Versioned JSON schema 1 содержит:

- `execution_count`;
- детерминированно упорядоченный массив `execution_ids`.

Route поддерживает pretty и compact JSON.

Exit codes:

- `0` — listing успешно сформирован, включая пустой список;
- `1` — catalog contract отклонён;
- `2` — command dependency не настроена.

### 28.4 Production composition

Главный `build_research_cli` использует один и тот же
`SqliteExperimentExecutionRecorder` для:

- append-only записи execution snapshots;
- чтения полной execution history;
- обнаружения сохранённых execution identities.

Production integration tests подтверждают object identity общего
adapter и чтение listing через реальный CLI route из той же SQLite
database.

### 28.5 Подтверждённые границы

Execution listing остаётся read-only навигационным use case.

Slice не добавил:

- новую Research, ExperimentExecution или Knowledge entity;
- новый artifact type или artifact envelope;
- новую persistence schema;
- status filters, pagination или runtime queue semantics;
- HTTP или MCP route;
- workflow, lifecycle, pipeline или orchestration engine.

Knowledge feature freeze и локальный indicator plugin contract
сохранены.

## 29. Immutable research artifact persistence checkpoint

Commit checkpoint: `efda1fd`.

Этот раздел фиксирует усиление существующей persistence-границы
`SqliteResearchCycleStore` без добавления нового artifact store.

### 29.1 Сохранение по result identity

Первичная запись нового `result_id` сохраняет canonical JSON payload
в существующей таблице `research_cycles`.

Повторная запись того же `result_id` разрешена только при полном
совпадении canonical serialized payload.

Такой retry является идемпотентным и не изменяет persistent state.

Другой payload под существующим `result_id` отклоняется до записи.
Первоначальный artifact остаётся неизменным.

### 29.2 Transaction boundary

Проверка существующего payload и возможная первичная вставка
выполняются внутри `BEGIN IMMEDIATE` transaction.

Silent last-write-wins replacement между concurrent writers одного
SQLite database больше невозможен.

### 29.3 Подтверждённые границы

Slice не изменил:

- `SerializedResearchCycleStore` Application port;
- JSON schema сохранённых research artifacts;
- таблицу `research_cycles`;
- публичные Application use cases;
- Domain или Knowledge models;
- CLI, HTTP или MCP routes.

Новый repository base class, artifact framework, workflow, lifecycle,
pipeline или orchestration engine не добавлялись.

Standalone Evidence и Finding contracts остаются legacy.
Knowledge feature freeze и локальный indicator plugin contract
сохранены.

## 30. Stored envelope integrity checkpoint

Commit checkpoint: `58cc264`.

Этот раздел фиксирует integrity-aware public read path для
сохранённых research artifact envelopes.

### 30.1 Public Application read boundary

`GetStoredResearchArtifact` получает application-safe dictionary
через существующий `SerializedResearchCycleStore`.

Если сохранённое значение является `ResearchArtifactEnvelope`,
use case повторно загружает его через существующий
`load_research_artifact_envelope`.

До возврата клиенту проверяются:

- envelope schema version;
- обязательные metadata fields;
- timestamp и source reference contracts;
- JSON-safe provenance и payload;
- соответствие `payload_fingerprint` фактическому payload.

Повреждённый envelope отклоняется на Application boundary и не
передаётся в CLI, HTTP или MCP adapter.

### 30.2 Legacy compatibility

Сохранённый legacy research artifact без envelope markers
возвращается через существующий compatibility path без изменения.

Missing artifact по-прежнему возвращает `None`.

### 30.3 Подтверждённые границы

Slice переиспользует существующий envelope loader и не добавляет:

- новый artifact loader framework;
- новый public Application use case;
- новый DTO или artifact type;
- новую persistence schema;
- новый CLI, HTTP или MCP route;
- Domain или Knowledge model;
- workflow, lifecycle, pipeline или orchestration engine.

Knowledge feature freeze и локальный indicator plugin contract
сохранены.

## 31. Strict artifact envelope schema checkpoint

Commit checkpoint: `e2f116c`.

Serialized `ResearchArtifactEnvelope` теперь проверяется по точному
набору top-level fields schema version 1.

Loader отдельно вычисляет missing и unknown fields.

Отсутствующие обязательные поля и любые неизвестные поля
отклоняются до восстановления immutable envelope.

Это предотвращает неявное расширение transport и persistence
contract без изменения schema version.

Все существующие production artifact producers подтверждены полным
набором автоматических тестов.

Slice не добавил новый artifact type, DTO, public use case, route,
repository, Domain model или общий artifact framework.

Knowledge feature freeze, legacy compatibility и локальный indicator
plugin contract сохранены.

## 32. CLI artifact integrity error checkpoint

Commit checkpoint: `24ebc63`.

CLI route `get-research-artifact` теперь преобразует ошибки
integrity validation в контролируемый command result.

При `TypeError` или `ValueError` от Application reader:

- stdout остаётся пустым;
- stderr содержит диагностическое сообщение;
- CLI возвращает exit code `1`;
- необработанное исключение не покидает transport boundary.

Missing artifact и unconfigured command сохраняют существующие
контракты и exit codes.

Slice не изменил Application use case, envelope schema,
persistence, HTTP, MCP, Domain или Knowledge contracts.

Новая общая error hierarchy или transport abstraction не
добавлялась.

## 33. Market research production lifecycle acceptance checkpoint

Commit checkpoint: `a7706d4`.

Добавлен end-to-end acceptance test существующего production market
research path через публичный CLI boundary.

Один тест использует одну временную SQLite database и последовательно:

1. запускает `run-research` по валидной generated market specification;
2. получает созданный research result;
3. обнаруживает техническое выполнение через
   `list-experiment-executions`;
4. читает полную append-only историю через
   `get-experiment-execution-history`;
5. загружает сохранённый validated envelope через
   `get-research-artifact`.

Тест подтверждает точную последовательность execution snapshots:

- `PENDING`;
- `RUNNING`;
- `SUCCEEDED`.

Terminal execution, research result и artifact envelope согласованы по:

- `execution_id`;
- `result_id`;
- `correlation_id`;
- `specification_fingerprint`;
- `environment_fingerprint`;
- typed source references.

Проверка проходит через реальный `main`, production composition root,
generated market-data provider, SQLite artifact store и SQLite execution
recorder.

Slice добавил только acceptance test и не изменил production-код,
Application contracts, persistence schema или artifact schema.

Новый общий workflow, lifecycle, pipeline или orchestration engine не
добавлялся.

Knowledge feature freeze и локальный indicator plugin contract
сохранены.

## 34. Failed market execution lifecycle acceptance checkpoint

Commit checkpoint: `9476102`.

Добавлен acceptance test существующего technical failure path для
одиночного market research execution.

Тест собирает реальный `RunMarketResearch` application graph через
`build_market_research_application` и использует одну SQLite database
для artifact store и execution recorder.

Контролируемая ошибка возникает внутри signal provider после создания
research context и перехода технического выполнения в `RUNNING`.

Append-only execution history сохраняет точную последовательность:

- `PENDING`;
- `RUNNING`;
- `FAILED`.

Через production CLI route `get-experiment-execution-history`
подтверждаются:

- identity исходной specification;
- сохранённый `environment_fingerprint`;
- отсутствие `result_id`;
- failure stage `EXECUTION`;
- тип `RuntimeError`;
- sanitized failure message.

Production CLI route `list-research-cycles` подтверждает, что failed
execution не создаёт частичный research artifact.

Slice добавил только acceptance test и не изменил production-код,
Application contracts, persistence schema, artifact schema или CLI
routes.

Technical failure остаётся состоянием `ExperimentExecution` и не
преобразуется в Evidence, Finding или HypothesisEvaluation.

Новый общий workflow, lifecycle, pipeline или orchestration engine не
добавлялся.

Knowledge feature freeze и локальный indicator plugin contract
сохранены.

## 35. Market execution runtime failure CLI checkpoint

Commit checkpoint: `db0fbb6`.

CLI route `run-research` теперь преобразует технический
`RuntimeError` от существующего Application execution path в
контролируемый command result.

При runtime failure:

- stdout остаётся пустым;
- stderr содержит сообщение `Unable to run research` и причину;
- CLI возвращает exit code `1`;
- исходное исключение не покидает transport boundary.

Изменение не перехватывает произвольный `Exception` и не вводит общую
error hierarchy. Существующие `ValueError` и `LookupError` contracts
сохранены.

Запись `ExperimentExecution` в состоянии `FAILED` выполняется ниже
CLI boundary существующим tracking executor до возврата command result.

Slice изменил только `ResearchCli` error mapping и его автоматический
тест.

Application use cases, execution recorder, persistence schema,
artifact schema, HTTP, MCP, Domain и Knowledge contracts не
изменялись.

Technical execution status не используется как научная оценка и не
подменяет Evidence, Finding или HypothesisEvaluation.

Новый общий workflow, lifecycle, pipeline или orchestration engine не
добавлялся.

Knowledge feature freeze и локальный indicator plugin contract
сохранены.
