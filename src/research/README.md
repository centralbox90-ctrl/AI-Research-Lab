# Research Package

Пакет `src/research/` содержит исследовательские контракты, неизменяемые модели результатов и доменные вычисления AI Research Lab.

Его задача — преобразовать зафиксированные наблюдения и рыночные данные в воспроизводимые результаты анализа и evidence. Пакет не отвечает за пользовательский интерфейс, подключение к MetaTrader 5 или форматирование вывода.

## Ответственности

Пакет отвечает за:

- спецификацию исследования;
- декларативный Campaign Design;
- описание измеряемого результата;
- фиксацию наблюдений;
- event study;
- построение безусловного baseline;
- сравнительный анализ;
- заранее объявленный план статистической оценки;
- воспроизводимую оценку неопределённости;
- классификацию replicated evaluations в evidence;
- идентичность исследования и набора данных.

## Границы

В `src/research/` не должны находиться:

- CLI и presenters;
- composition roots;
- подключение к MetaTrader 5;
- чтение пользовательской конфигурации;
- запись файлов и форматирование артефактов;
- управление HTTP-интерфейсами;
- торговое исполнение;
- Knowledge Repository.

Эти обязанности принадлежат application, infrastructure, CLI, execution или будущему Knowledge Domain.

## Текущий исследовательский поток

Подтверждённый поток сравнительного исследования:

1. `ResearchSpecification` фиксирует исследовательскую конфигурацию.
2. `Observation` представляет конкретный наблюдаемый случай.
3. `ForwardReturnSpecification` объявляет горизонты измерения результата.
4. `EventStudyService` рассчитывает результаты после наблюдений.
5. `UnconditionalBaselineService` создаёт сопоставимый baseline.
6. `ComparativeAnalysisService` формирует сравнительный анализ.
7. `ComparativeEvaluationPlan` заранее фиксирует правила оценки.
8. `ComparativeStatisticalEvaluator` оценивает неопределённость.
9. `ComparativeEvidenceEvaluator` объединяет репликации в `Evidence`.

`ComparativeEvidenceEvaluator` не создаёт Finding и не изменяет гипотезу. Интерпретация evidence в научный вывод остаётся отдельной ответственностью Analysis.

## Основные контракты

| Модуль | Контракт | Назначение |
|---|---|---|
| `specification.py` | `ResearchSpecification` | Неизменяемая спецификация и fingerprint исследования |
| `campaign_design.py` | `CampaignDesign` | Неизменяемые измерения и ссылки будущей исследовательской кампании |
| `research_planner.py` | `CampaignExperimentSpecification` | Один воспроизводимый элемент пространства экспериментов |
| `research_planner.py` | `ResearchCampaignPlan` | Неизменяемая запланированная кампания |
| `research_planner.py` | `ResearchPlanner` | Детерминированное разворачивание CampaignDesign в пространство экспериментов |
| `specification.py` | `IndicatorReference` | Версионированная ссылка на индикатор |
| `outcome_specification.py` | `ForwardReturnSpecification` | Горизонты и поле цены для измерения результата |
| `observations/observation.py` | `Observation` | Зафиксированный случай исследуемого события |
| `event_study_result.py` | `EventStudyResult` | Результаты измерений по наблюдениям |
| `comparative_analysis.py` | `ComparativeAnalysis` | Candidate, baseline и согласованные сравнения |
| `comparative_evaluation_plan.py` | `ComparativeEvaluationPlan` | Предварительно объявленные статистические правила |
| `comparative_statistical_evaluation.py` | `ComparativeStatisticalEvaluation` | Воспроизводимая оценка одного горизонта |
| `evidence.py` | `Evidence` | Неизменяемая оценка отношения данных к гипотезе |
| `finding.py` | `Finding` | Неизменяемая интерпретация Evidence с явным отношением к гипотезе |
| `hypothesis_evaluation.py` | `HypothesisEvaluation` | Воспроизводимый результат формальной оценки гипотезы |
| `hypothesis_evaluation_plan.py` | `HypothesisEvaluationPlan` | Предварительно объявленные правила формальной оценки гипотезы |
| `hypothesis_evaluator.py` | `HypothesisEvaluator` | Детерминированная оценка набора Findings по объявленному плану |
| `market_dataset_fingerprint.py` | `MarketDatasetFingerprint` | Версионированная идентичность canonical dataset |

## Доменные сервисы

### Event study

`EventStudyService` измеряет forward returns после наблюдений. `EventStudyAnalyzer` агрегирует результаты по горизонтам.

### Baseline

`UnconditionalBaselineService` создаёт baseline на том же наборе данных и с той же outcome specification. `BaselineComparator` сравнивает candidate и baseline.

### Comparative analysis

`ComparativeAnalysisService` координирует event study, baseline, статистики и сравнения. Результатом является неизменяемый `ComparativeAnalysis`.

### Statistical evaluation

`ComparativeStatisticalEvaluator` использует deterministic moving-block bootstrap. Все параметры поступают из `ComparativeEvaluationPlan`, включая confidence level, количество выборок, длину блока и random seed.

### Evidence

`ComparativeEvidenceEvaluator` применяет только правила, зафиксированные в evaluation plan. Он учитывает направление эффекта, размер выборки, количество репликаций, согласованность и ограничения.

## Воспроизводимость

Исследовательский результат должен быть воспроизводимым при одинаковых:

- research specification;
- dataset fingerprint;
- evaluation plan;
- версии индикатора;
- random seed;
- входных наблюдениях.

Изменение любого из этих элементов должно приводить к изменению соответствующего fingerprint или результата.

## Инварианты

Исследовательские модели должны:

- быть неизменяемыми после создания;
- проверять типы и значения на границе;
- нормализовать идентификаторы;
- использовать стабильную сортировку коллекций;
- исключать неоднозначные или неполные результаты;
- сохранять provenance;
- не зависеть от порядка совместимых репликаций.

Evaluation plan должен быть сформирован до анализа результата. Это предотвращает изменение научных критериев после получения данных.

## Направление зависимостей

Допустимое направление:

`src/cli` → `src/application` → `src/research`

Research-код не должен импортировать CLI или application-слой. Прикладной слой может координировать несколько research-контрактов, но научные правила должны оставаться внутри `src/research/`.

Canonicalization рыночного набора сейчас частично находится в `market_dataset_fingerprint.py`. Это переходное размещение до окончательного выделения Market Data Domain.

## Campaign Design

`CampaignDesign` заранее фиксирует пространство будущей исследовательской кампании: гипотезы, инструменты, таймфреймы, периоды данных, конфигурации индикаторов, signal rules, execution policies, baselines, validation strategy и evaluation plan.

Все вычислительные элементы представлены непрозрачными версионированными ссылками. Research Domain выбирает их, но не реализует calculation, signal generation или execution. Идентичность design детерминирована его нормализованным содержимым и provenance.

Существующий изменяемый `ResearchCampaign` пока сохраняется как runtime-контракт совместимости. `ResearchPlanner` детерминированно разворачивает нормализованный `CampaignDesign` в полный Cartesian-набор `CampaignExperimentSpecification` и объединяет их в immutable `ResearchCampaignPlan`. Максимальный размер пространства ограничивается до создания спецификаций. `ResearchCampaignPlanMarketAdapter` разрешает каждый элемент плана в `MarketExperimentSpecification`, проверяет соответствие инструмента и таймфрейма и сохраняет связь с исходной спецификацией. `InMemoryMarketExperimentSpecificationResolver` реализует явный каталог полностью заполненных market specifications по детерминированным идентификаторам элементов плана и не интерпретирует непрозрачные ссылки. `MarketExperimentRegistrationLoader` загружает только полный набор регистраций, принадлежащий конкретному plan ID. `RunMarketResearchCampaign` объединяет планирование, полное предварительное разрешение и последовательное выполнение экспериментов. Внешний loader `CampaignDesign`, composition root и CLI-маршрут кампании ещё не реализованы.

## Campaign Execution

Подтверждённый поток выполнения исследовательской кампании:

1. `CampaignDesign` фиксирует пространство исследования.
2. `ResearchPlanner` создаёт детерминированный `ResearchCampaignPlan`.
3. `MarketExperimentRegistrationLoader` проверяет schema version, plan ID и полноту внешних регистраций.
4. `InMemoryMarketExperimentSpecificationResolver` находит явную регистрацию каждого элемента плана.
5. `ResearchCampaignPlanMarketAdapter` проверяет соответствие инструмента и таймфрейма.
6. `RunMarketResearchCampaign` завершает разрешение всего плана до первого запуска.
7. Каждый результат сохраняет связь с исходным `CampaignExperimentSpecification`.

Отсутствующая или несовместимая регистрация останавливает кампанию до выполнения первого эксперимента. Ошибка самого runner после начала выполнения распространяется вызывающему коду и не маскируется.

## Finding Pipeline

Новый воспроизводимый Analysis-поток использует следующие контракты:

- `Finding` — неизменяемая интерпретация Evidence с явным типизированным отношением к гипотезе;
- `FindingEvaluator` — детерминированное преобразование Evidence → Finding;
- `IndicatorComparativeFindingApplication` — orchestration сравнительного исследования через Evidence до Finding.

Composition root и presenter для Finding подключены.

## Hypothesis Evaluation

`HypothesisEvaluation` фиксирует формальный результат проверки гипотезы на основании Finding.

Допустимые состояния:

- `supported`;
- `partially_supported`;
- `inconclusive`;
- `rejected`.

Модель результата и `HypothesisEvaluationPlan` реализованы как immutable воспроизводимые контракты. `HypothesisEvaluator` детерминированно классифицирует согласованный набор Findings по объявленным порогам и минимальному количеству результатов. `HypothesisEvaluationApplication`, отдельный composition root и presenter формируют внешний контракт оценки готового набора Findings. `IndicatorComparativeHypothesisEvaluationApplication` выполняет end-to-end orchestration нескольких сравнительных Finding-запросов до формальной оценки гипотезы. Объединённый composition root подключает этот поток к canonical market data provider и обоим предварительно объявленным evaluation plans. `IndicatorComparativeHypothesisEvaluationRequestLoader` преобразует строгий JSON-контракт в типизированный прикладной запрос. `RunIndicatorComparativeHypothesisEvaluationCommand` выполняет запрос и возвращает версионированный JSON-артефакт через presenter. Команда зарегистрирована в общем `ResearchCli` как пользовательский маршрут полного Analysis-потока.

## Legacy Analysis

`Conclusion` и `HypothesisDecision` относятся к старому циклу `ResearchEngine`. Они используют runtime UUID, временные метки и изменяемое состояние.

Они временно сохраняются для совместимости с существующими `cycle_results`, `research_objects_builder`, `next_experiment_selector` и `hypothesis_decision_evaluator`.

Новый application-код не должен импортировать:

- `src.research.conclusion`;
- `src.research.hypothesis_decision`.

Эта граница контролируется архитектурным тестом.

## Тестирование

Все изменения research-контрактов должны проверять:

- успешный основной сценарий;
- неизменяемость модели;
- валидацию каждого публичного поля;
- детерминированность;
- порядок элементов и fingerprints;
- несовместимые specifications и datasets;
- граничные размеры выборок;
- отсутствие скрытой зависимости от порядка репликаций.

Проверка всего проекта:

`python -m pytest -q`

Проверка исследовательского пакета:

`python -m pytest -q src/research`