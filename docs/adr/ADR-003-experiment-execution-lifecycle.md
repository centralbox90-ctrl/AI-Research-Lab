# ADR-003: ExperimentExecution Lifecycle

Дата: 28 июля 2026 года
Статус: Accepted

## Контекст

Текущий production market path выполняется через RunMarketResearch.

MarketResearchSessionFactory подготавливает ResearchContext, ResearchGraph и executor. RunAndStoreResearchArtifact запускает ResearchEngine, создаёт metadata, сериализует artifact и сохраняет его.

Отдельного production-контракта, представляющего факт технического выполнения одной спецификации эксперимента, пока нет.

Experiment хранит изменяемые status, started_at и completed_at. ExperimentRunner переводит его между NEW, RUNNING, COMPLETED и FAILED.

ResearchExecution связывает множество стадий полного исследовательского цикла и используется AIScientist. Эта compatibility-модель слишком широка для роли минимального execution record.

Текущий artifact создаётся только после успешного выполнения и анализа. Если подготовка данных или executor завершается ошибкой, постоянной записи о failed execution не возникает.

MarketExperimentSpecification описывает полный market experiment, но пока не имеет собственного fingerprint.

Вложенный ResearchSpecification имеет deterministic fingerprint, однако он не включает источник данных, временной диапазон, торговые правила, risk parameters, costs и другие поля MarketExperimentSpecification.

ResearchEnvironmentRef уже предоставляет fingerprint воспроизводимой среды, включающий dataset, assumptions, code version, executor version, statistical method version и random seed.

## Решение

Вводится минимальный ExperimentExecution как технический факт одной попытки выполнить одну полную спецификацию эксперимента в одной воспроизводимой среде.

ExperimentExecution не является workflow job, artifact envelope, научной оценкой или универсальным lifecycle aggregate.

Первый implementation slice применяется только к одному существующему production market experiment path.

## Ответственность

ExperimentExecution отвечает на вопросы:

- какая спецификация выполнялась;
- какой Research Experiment выполнялся;
- в какой воспроизводимой среде выполнялся эксперимент;
- когда выполнение было создано, начато и завершено;
- завершился ли executor успешно;
- какой ExperimentResult был получен;
- какая техническая ошибка остановила выполнение.

ExperimentExecution не отвечает на вопросы:

- поддержана ли гипотеза;
- достаточно ли evidence;
- является ли finding значимым;
- разрешено ли knowledge promotion;
- сохранён ли downstream artifact;
- нужно ли повторить задание;
- какой worker должен выполнить задание.

## Размещение

Минимальная модель ExperimentExecution относится к research execution kernel и может быть размещена в `src/research/experiment_execution.py`.

Она не наследуется от Experiment, ResearchExecution, ResearchArtifact или других lifecycle-моделей.

Application Layer создаёт модель, выполняет переходы и организует persistence через port.

Runtime infrastructure может инициировать тот же application use case, но не изменяет семантику ExperimentExecution.

## Идентичность и ссылки

Минимальный контракт содержит:

- execution_id;
- optional correlation_id;
- experiment_id;
- specification_fingerprint;
- environment_fingerprint;
- status;
- created_at;
- started_at;
- finished_at;
- optional result_id;
- optional failure.

execution_id является собственной идентичностью конкретной попытки выполнения.

experiment_id ссылается на Research Experiment и не заменяется execution_id.

correlation_id используется только для трассировки связанных операций. Он не является доменной идентичностью и не определяет равенство execution records.

Повторная техническая попытка получает новый execution_id. Retry count и attempt number не входят в минимальную модель.

## Fingerprints

specification_fingerprint вычисляется по каноническому представлению полной MarketExperimentSpecification.

Fingerprint должен включать:

- executor type;
- данные вопроса, гипотезы и эксперимента;
- data source, symbol и timeframe;
- start_at и end_at;
- entry rule, exit rule и direction;
- risk parameters;
- commission и slippage;
- strategy parameters;
- tags;
- полное каноническое представление вложенной ResearchSpecification.

Использование только ResearchSpecification.fingerprint запрещено, потому что оно не идентифицирует полный market experiment.

environment_fingerprint получается из существующего ResearchEnvironmentRef.fingerprint.

Fingerprint не заменяет исходную specification или environment в воспроизводимом artifact.

## Статусы

Допустимые состояния:

- PENDING;
- RUNNING;
- SUCCEEDED;
- FAILED;
- CANCELLED.

### PENDING

Execution record создан после проверки входного application-контракта.

Подготовка canonical dataset, ResearchContext и executor ещё может не завершиться.

started_at и finished_at отсутствуют.

result_id и failure отсутствуют.

### RUNNING

Контекст подготовлен, и непосредственное выполнение experiment path начато.

started_at присутствует.

finished_at, result_id и failure отсутствуют.

### SUCCEEDED

Executor вернул корректный ExperimentResult, связанный с ожидаемым experiment_id.

started_at, finished_at и result_id присутствуют.

failure отсутствует.

SUCCEEDED не означает, что гипотеза поддержана или что artifact успешно сохранён.

### FAILED

Подготовка выполнения или executor завершились технической ошибкой.

finished_at и failure присутствуют.

result_id отсутствует.

started_at может отсутствовать, если ошибка произошла до начала executor.

### CANCELLED

Выполнение было отменено до получения ExperimentResult.

finished_at присутствует.

result_id отсутствует.

started_at может отсутствовать, если отмена произошла до запуска executor.

## Переходы

Разрешены переходы:

- PENDING → RUNNING;
- PENDING → FAILED;
- PENDING → CANCELLED;
- RUNNING → SUCCEEDED;
- RUNNING → FAILED;
- RUNNING → CANCELLED.

SUCCEEDED, FAILED и CANCELLED являются terminal states.

Обратные переходы и изменение terminal status запрещены.

Retry создаёт новый ExperimentExecution и не возвращает FAILED execution в RUNNING.

## Failure

Failure является техническим value object, а не отдельной сущностью.

Минимальная информация:

- stage;
- error_type;
- message.

Допустимые начальные stages:

- PREPARATION;
- EXECUTION.

Traceback, credentials, environment variables и другие потенциально чувствительные данные не входят в persistence-контракт failure.

Ошибки evaluation, artifact serialization и artifact persistence не изменяют SUCCEEDED execution на FAILED.

## Временные метки

Все новые execution timestamps должны быть timezone-aware и храниться в UTC.

Создание идентичности и времени выполняется через существующие application ports IdGenerator и Clock.

Прямой вызов локального datetime.now внутри нового lifecycle не используется.

Для любого terminal state finished_at не может быть раньше created_at или started_at.

## Граница результата

ExperimentExecution считается SUCCEEDED после получения валидного ExperimentResult.

ExperimentResult.success не заменяет ExperimentExecution.status и не используется как состояние очереди.

Научная интерпретация ExperimentResult выполняется последующими стадиями evaluation, evidence, finding и hypothesis evaluation.

Artifact создаётся после execution и должен ссылаться на execution_id и result_id через будущий ResearchArtifactEnvelope.

result_artifact_id не входит в минимальное ядро ExperimentExecution. Это предотвращает зависимость execution status от успешности artifact persistence.

## Persistence

Failed и cancelled executions должны быть доступны для сохранения так же, как successful executions.

Конкретный repository protocol и SQLite adapter вводятся только вместе с первым production implementation slice.

Repository не выполняет переходы состояния и не принимает научных решений.

Persistence execution record не заменяет persistence ExperimentResult или ResearchArtifactEnvelope.

## Интеграция первого среза

Первым интегрируется существующий одиночный market research path.

Последовательность первого среза:

1. проверить MarketExperimentSpecification;
2. создать PENDING ExperimentExecution;
3. вычислить полный specification fingerprint;
4. подготовить MarketResearchSession и environment fingerprint;
5. перевести execution в RUNNING;
6. вызвать существующий executor через существующий research path;
7. при корректном ExperimentResult перевести execution в SUCCEEDED;
8. выполнить evaluation и artifact persistence как последующие application stages;
9. при preparation или execution error сохранить FAILED execution и повторно передать ошибку вызывающему адаптеру.

Campaign execution не мигрирует в первом срезе.

## Отклонённые варианты

### Расширить существующий ResearchExecution

Отклонено, потому что он уже связывает полный research lifecycle и содержит legacy-поля knowledge и result.

### Использовать только Experiment.status

Отклонено, потому что Experiment является исследовательским объектом, а разные попытки выполнения должны иметь отдельную идентичность.

### Считать artifact persistence частью SUCCEEDED

Отклонено, потому что ошибка хранения не отменяет факт успешного выполнения executor.

### Добавить retry metadata

Отклонено в соответствии с границей Research и runtime.

### Сразу мигрировать campaign path

Отклонено. Сначала один production experiment должен подтвердить минимальный lifecycle.

## Последствия

Появится отдельная идентичность каждой попытки выполнения.

Успешное выполнение будет отделено от научного результата и успешности artifact persistence.

Ошибочные выполнения смогут сохраняться и диагностироваться.

Для полной MarketExperimentSpecification потребуется deterministic fingerprint.

Потребуются application orchestration, persistence port, adapter и тесты, но только после принятия ADR и только для первого market experiment path.

Следующим архитектурным решением должен быть ResearchArtifactEnvelope, использующий реальные execution references.

## Связанные документы

- `ARCHITECTURE_INVENTORY.md`
- `docs/adr/ADR-001-knowledge-feature-freeze.md`
- `docs/adr/ADR-002-research-runtime-boundary.md`