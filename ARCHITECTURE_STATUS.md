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
| Research | Core | Partial | Реализованы сравнительные исследования и application-поток CampaignDesign → ResearchCampaignPlan → validated registrations → resolved MarketExperimentSpecification → последовательное выполнение кампании. Внешний loader CampaignDesign, composition root и CLI-маршрут кампании пока отсутствуют. |
| Experiment | Core | Partial | Поддерживаются воспроизводимые результаты, планы оценки и исследовательские артефакты. Унифицированный жизненный цикл всех типов экспериментов ещё не завершён. |
| Market Data | Core | Partial | Реализованы загрузчики, generated market data и canonical dataset provider. Legacy-представления используются не во всех сценариях через единый контракт. |
| Calculation | Core | Confirmed | Реализованы индикаторы, их автоматическое обнаружение и вычислительные исследовательские сценарии. |
| Signal | Core | Confirmed | Генерация сигналов и интеграция с существующим execution-контуром присутствуют. Декларативная композиция правил ограничена. |
| Execution | Core | Confirmed | Backtest Engine остаётся основной реализацией исполнения. Его внутренние ответственности ещё не полностью разделены. |
| Analysis | Core | Confirmed | Реализован и протестирован полный сценарий Observation → Evidence → Finding → HypothesisEvaluation. Строгий JSON loader, CLI-команда, presenters, composition roots и пользовательский маршрут общего ResearchCli подключены. |
| Knowledge | Core | Planned | Специализированные repository, versioning и contradiction detection пока отсутствуют. |
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
- CampaignExperimentSpecification и immutable ResearchCampaignPlan;
- детерминированный ResearchPlanner с ограничением Cartesian expansion;
- ResearchCampaignPlanMarketAdapter с проверкой соответствия инструмента и таймфрейма;
- сохранение связи resolved market experiment с исходной плановой спецификацией;
- InMemoryMarketExperimentSpecificationResolver с явными неизменяемыми регистрациями;
- строгий MarketExperimentRegistrationLoader с проверкой plan ID и полного набора;
- RunMarketResearchCampaign с полным разрешением плана до начала выполнения;
- типизированный результат кампании с сохранением порядка и связи с плановыми спецификациями;
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

### Infrastructure

- composition roots и CLI-команда полного цикла формальной оценки гипотезы;
- presenters, отделённые от прикладных сервисов;
- воспроизводимый `requirements.txt`;
- автоматический запуск `python -m pytest -q`;
- GitHub Actions на Windows и Python 3.13;
- корректное разделение `/data/` и пакета `src/data/`.

## Текущие архитектурные отклонения

### Research orchestration

Существующий ResearchCampaign остаётся изменяемым runtime-контрактом совместимости. Новый поток CampaignDesign, ResearchPlanner, строгий registration loader, resolver, adapter и RunMarketResearchCampaign выполняет запланированную кампанию через явные application-границы. Для пользовательского запуска ещё отсутствуют внешний loader CampaignDesign, composition root и CLI-маршрут.

### Market Data

Canonical market data ещё не является единственным внутренним представлением во всех подсистемах. Legacy-форматы должны оставаться за адаптерами.

### Execution

Существующий Backtest Engine объединяет моделирование брокера, исполнение и управление портфелем. Это допустимое переходное состояние, но не конечная граница домена.

### Legacy Analysis Pipeline

Conclusion и HypothesisDecision используются существующим ResearchEngine и связанными cycle results. Они изолированы как legacy-контракты: новый application-слой не может импортировать их напрямую.

### Knowledge

Результаты сохраняются как артефакты, но пока не образуют версионированную базу знаний с обнаружением противоречий.

## Приоритеты развития

1. Добавить строгий внешний loader CampaignDesign.
2. Подключить campaign use case через composition root и CLI.
3. Продолжить внедрение canonical market data через адаптеры.
4. Разделить оставшиеся ответственности Backtest Engine.
5. Реализовать первый минимальный вертикальный срез Knowledge Domain.
6. Продолжить изоляцию и поэтапное удаление Legacy Analysis Pipeline.

## Критерий обновления

Этот документ необходимо обновлять, когда изменение:

- добавляет новый архитектурный контракт;
- завершает или расширяет вертикальный срез;
- меняет статус домена;
- устраняет архитектурное отклонение;
- добавляет подтверждённый инфраструктурный механизм.

На момент обновления полный набор автоматических тестов успешно проходит локально и в GitHub Actions.