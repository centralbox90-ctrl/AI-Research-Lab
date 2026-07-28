# ADR-002: Research and Runtime Boundary

Дата: 28 июля 2026 года
Статус: Accepted

## Контекст

Research Domain уже содержит предметные состояния исследования и эксперимента.

Experiment изменяет состояния NEW, RUNNING, COMPLETED и FAILED через ExperimentRunner.

ResearchCampaign изменяет состояния NEW, RUNNING, COMPLETED и FAILED в процессе выполнения ResearchEngine.

ResearchExecution является широкой изменяемой compatibility-моделью. Она связывает идентификаторы вопроса, гипотезы, эксперимента, evidence, finding и knowledge, а также хранит результат, ошибку и временные метки. Модель используется AIScientist, но не является основой текущих production CLI-сценариев.

Application Layer уже определяет порядок вызовов через сценарии запуска исследования, кампании, подготовки сессии, выполнения эксперимента и сохранения результата.

ResearchRuntimeConfiguration содержит версии кода и методов, а также random seed. Несмотря на название, это конфигурация воспроизводимости исследования, а не модель очереди или workflow runtime.

В проекте пока нет необходимости в workers, leases, heartbeat, retries или scheduling. Добавление этих обязанностей в Research Domain смешало бы техническое управление заданиями с научной семантикой.

## Решение

Устанавливается явная граница между Research Domain, ExperimentExecution, Application Layer и будущей runtime-инфраструктурой.

### Research Domain

Research Domain определяет:

- что и почему исследовать;
- исследовательские вопросы и гипотезы;
- дизайн и план исследования;
- спецификацию эксперимента;
- научную интерпретацию результата;
- evidence, finding и hypothesis evaluation;
- предметные состояния исследовательских объектов.

Research Domain не управляет технической доставкой или распределением заданий.

### ExperimentExecution

Будущий ExperimentExecution описывает факт выполнения одной конкретной спецификации эксперимента и наблюдаемый технический результат выполнения.

Он может фиксировать:

- собственную идентичность;
- ссылку на спецификацию;
- начало и завершение;
- успешный, ошибочный или отменённый результат;
- provenance и ссылки на созданные artifacts;
- сведения об ошибке выполнения.

Точный контракт ExperimentExecution определяется отдельным ADR.

ExperimentExecution не содержит научного решения о поддержке или отклонении гипотезы.

### Application Layer

Application Layer:

- реализует пользовательские use cases;
- определяет порядок вызовов domain services и ports;
- создаёт execution context;
- передаёт спецификацию исполнителю;
- сохраняет результаты через repositories;
- выполняет последствия доменных решений;
- определяет границы application-транзакций.

Application Layer может выполнять сценарий синхронно. В будущем тот же публичный use case может быть вызван runtime-адаптером без изменения доменной семантики.

### Runtime infrastructure

Будущая runtime-инфраструктура отвечает за:

- постановку заданий в очередь;
- scheduling;
- retries и backoff;
- worker assignment;
- leases;
- heartbeat;
- timeout и техническое восстановление;
- технические статусы доставки задания.

Runtime вызывает Application Layer, но не принимает исследовательских или эпистемических решений.

## Архитектурные инварианты

1. Domain statuses не используются для управления очередью.
2. FAILED execution означает техническую невозможность завершить выполнение.
3. NOT_SUPPORTED или REJECTED hypothesis означает научный результат успешно выполненного исследования.
4. Retry count, lease owner, worker identifier, heartbeat, queue name и next retry time не добавляются в Research Domain.
5. Runtime identifiers не заменяют доменные идентичности.
6. Runtime не принимает решения о knowledge promotion.
7. PromotionPolicy остаётся доменной политикой, а Application Layer выполняет последствия PromotionDecision.
8. ResearchPlanner не управляет расписанием workers и retry policy.
9. ResearchEngine и ResearchCampaign не расширяются инфраструктурным управлением заданиями.
10. Correlation identifiers используются только для трассировки.

## Существующие модели

ResearchExecution и AIScientist считаются compatibility boundary до отдельного решения об ExperimentExecution. В них не добавляются runtime-поля.

ExperimentStatus и ResearchStatus сохраняют предметный смысл и не расширяются состояниями очереди.

ResearchRuntimeConfiguration продолжает описывать воспроизводимую среду исследования. Возможное переименование рассматривается отдельным рефакторингом.

Этот ADR не вводит WorkflowRun, ExecutionJob, scheduler, worker или универсальный workflow engine.

## Отклонённые варианты

### Использовать ResearchExecution как runtime job

Отклонено, потому что модель уже связывает множество доменных результатов и станет центральным изменяемым объектом всей системы.

### Управлять очередью через ExperimentStatus

Отклонено, потому что статус эксперимента описывает выполнение, а не доставку задания конкретному worker.

### Создать универсальный WorkflowEngine сейчас

Отклонено до появления минимум трёх независимых production-сценариев с одинаковым подтверждённым техническим lifecycle.

### Поместить retries в ResearchEngine

Отклонено, потому что retry является технической политикой выполнения.

## Последствия

Research Domain сохраняет независимость от runtime-технологии.

Синхронное выполнение остаётся допустимым production-вариантом.

Очередь или scheduler можно будет добавить как внешний adapter без изменения основных use cases.

Ошибки выполнения и отрицательные научные результаты моделируются и тестируются отдельно.

Следующим решением должен быть минимальный lifecycle ExperimentExecution на основе одного существующего market experiment path.

## Связанные документы

- `ARCHITECTURE_INVENTORY.md`
- `ARCHITECTURE_STATUS.md`
- `docs/adr/ADR-001-knowledge-feature-freeze.md`