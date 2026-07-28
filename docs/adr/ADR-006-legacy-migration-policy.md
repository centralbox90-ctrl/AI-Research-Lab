# ADR-006: Legacy Migration Policy

Дата: 28 июля 2026 года
Статус: Accepted

## Контекст

Проект содержит несколько поколений research, analysis, execution и persistence contracts.

Часть legacy-компонентов остаётся в production path. Другие уже не используются production code, но сохраняются в repository вместе с тестами и exports.

Текущие compatibility boundaries включают:

- ResearchEngine;
- LegacyEvidence;
- Conclusion;
- HypothesisDecision;
- mutable Knowledge;
- ResearchExecution;
- AIScientist;
- mutable ResearchCampaign;
- Question, Hypothesis, Experiment и ExperimentResult;
- legacy serialized persistence use cases;
- LegacyMarketDataProvider;
- LegacyMarketDataFrameAdapter;
- LegacyMarketBacktestExecutor;
- legacy signal mapper;
- ResearchRecommendationQuestionAdapter;
- ResearchArtifact compatibility model;
- tracked recovery file `src/research/engine.py.broken`.

Некоторые границы уже защищены architecture tests.

Application Layer не может напрямую импортировать Conclusion и HypothesisDecision.

Production code не может использовать RunResearchCycle, RunAndStoreSerializedResearchCycle и RunAndStoreSerializedResearchCampaign.

Research Layer не зависит от Application, Storage или CLI.

Application Layer не зависит от Storage или CLI.

Storage Layer не зависит от Application или CLI.

При этом RunMarketResearch всё ещё использует ResearchEngine через RunAndStoreResearchArtifact.

LegacyMarketDataFrameAdapter остаётся production boundary для преобразования legacy OHLC columns в canonical dataset.

ResearchRecommendationQuestionAdapter остаётся частью production knowledge-feedback path.

Массовое удаление legacy сейчас нарушило бы работающие vertical paths и могло бы сделать сохранённые artifacts нечитаемыми.

## Решение

Legacy мигрирует постепенно по strangler pattern.

Каждая legacy boundary сначала изолируется, затем получает replacement contract, после чего production consumer переводится на replacement.

Удаление выполняется только после доказанного отсутствия production dependency и отдельным commit.

Legacy migration не объединяется с добавлением новой пользовательской функциональности.

## Определение legacy

Компонент считается legacy, если выполняется хотя бы одно условие:

- существует более современный контракт с тем же назначением;
- компонент содержит смешанную ответственность нескольких lifecycle stages;
- модель изменяема там, где целевая архитектура требует immutable fact;
- компонент использует устаревшую persistence или serialization boundary;
- production dependency сохраняется только ради совместимости;
- новый Application Layer не должен создавать на него зависимости;
- компонент не входит в production wiring и сохранён только для старых tests или consumers.

Название Legacy не обязательно должно присутствовать в имени класса.

Legacy status не означает, что компонент ошибочен или должен быть немедленно удалён.

## Статусы миграции

Для inventory используются следующие документальные статусы.

### ACTIVE_COMPATIBILITY

Компонент используется production path и пока не имеет полностью подключённой замены.

### CONTAINED

Компонент используется, но новые зависимости на него запрещены или ограничены compatibility adapter.

### REPLACEMENT_AVAILABLE

Замена реализована и протестирована, но ещё не обслуживает все production consumers.

### RETIRED_FROM_PRODUCTION

Production wiring больше не использует компонент, но он остаётся для backward reads, tests или переходного периода.

### REMOVABLE

Все removal gates выполнены. Компонент можно удалить отдельным commit.

### REMOVED

Компонент удалён, exports и документация обновлены, а полный suite прошёл.

Эти статусы не вводятся как runtime enum или новые классы.

## Основные правила

1. Новая functionality не строится на legacy contract.

2. Legacy component не расширяется новой доменной ответственностью.

3. Compatibility adapter должен быть узким и однонаправленным.

4. Новая модель не наследуется от legacy model ради повторного использования полей.

5. Replacement сначала проходит production vertical slice.

6. Старый path не удаляется в том же commit, в котором впервые появился replacement.

7. Удаление legacy выполняется отдельным commit.

8. Persisted data не переписываются без явной migration strategy.

9. Architecture tests запрещают появление новых legacy consumers.

10. Rollback должен быть возможен обычным revert без переписывания истории main.

## Процесс миграции одной boundary

Каждая миграция выполняется в следующем порядке.

### 1. Inventory

Фиксируются:

- legacy component;
- текущие production consumers;
- tests;
- public exports;
- persisted formats;
- replacement contract;
- removal gates.

### 2. Characterization

До изменения production behavior добавляются или подтверждаются characterization tests текущего пути.

Tests фиксируют необходимое поведение, но не объявляют случайные implementation details новым контрактом.

### 3. Replacement

Создаётся минимальный replacement для одного реального сценария.

Replacement не обязан сразу поддерживать все legacy capabilities.

### 4. Compatibility seam

При необходимости создаётся однонаправленный adapter между текущим production path и replacement.

Adapter располагается на внешней стороне нового контракта.

Новый domain model не импортирует legacy adapter.

### 5. Production wiring

Один composition root переводится на replacement.

В одном commit не мигрируют несколько независимых production paths.

### 6. Protection

Architecture test или explicit allowlist запрещает появление новых production imports legacy component.

### 7. Consumer migration

Оставшиеся consumers мигрируют отдельными небольшими slices.

### 8. Data compatibility

Подтверждается чтение существующих SQLite rows и JSON artifacts либо выполняется явная versioned migration.

### 9. Removal

После выполнения removal gates legacy files, exports, tests и documentation удаляются отдельным commit.

## Removal gates

Legacy component получает статус REMOVABLE только когда одновременно выполнены условия:

1. replacement contract принят и протестирован;
2. replacement подключён к production composition root;
3. production code не импортирует legacy component;
4. public Application API не возвращает legacy model;
5. сохранённые данные остаются читаемыми или мигрированы;
6. CLI contracts сохранены либо versioned;
7. architecture tests блокируют повторное использование legacy path;
8. targeted tests проходят;
9. полный test suite проходит;
10. Architecture Inventory и Architecture Status обновлены;
11. поиск по repository не показывает необъяснённых consumers;
12. удаление не смешано с другой архитектурной задачей.

Наличие replacement class без production wiring недостаточно для удаления.

## ResearchEngine

ResearchEngine имеет статус ACTIVE_COMPATIBILITY.

Он остаётся внутри текущего RunAndStoreResearchArtifact path.

Первый ExperimentExecution slice оборачивает существующий ResearchEngine и фиксирует execution lifecycle вокруг него.

Первый slice не переписывает ResearchEngine и не переносит весь analysis pipeline.

Новые runtime, retry, scheduling или knowledge-promotion обязанности в ResearchEngine не добавляются.

ResearchEngine может стать REMOVABLE только после миграции всех production research paths на явные use cases и modern analysis services.

## Legacy analysis models

LegacyEvidence, Conclusion, HypothesisDecision и mutable Knowledge имеют статус CONTAINED.

Application Layer уже защищён от прямых imports Conclusion и HypothesisDecision.

Новые Analysis use cases используют Evidence, Finding и HypothesisEvaluation.

Legacy analysis models остаются внутри ResearchEngine, builders, cycle results и legacy serializers до миграции соответствующих consumers.

Они не становятся базовыми классами современных Analysis models.

Удаление возможно только после сохранения backward read существующих cycle artifacts.

## ResearchExecution and AIScientist

ResearchExecution и AIScientist имеют статус CONTAINED.

Они не используются текущим production CLI.

Новый ExperimentExecution не наследуется от ResearchExecution.

В ResearchExecution не добавляются:

- retry count;
- worker identity;
- lease;
- heartbeat;
- scheduling;
- artifact envelope;
- knowledge promotion.

После подключения нового ExperimentExecution необходимо добавить protection test, запрещающий его production replacement через ResearchExecution.

ResearchExecution и AIScientist удаляются только после проверки всех tests, examples и external imports.

## Mutable ResearchCampaign

Mutable ResearchCampaign является compatibility contract legacy ResearchEngine campaign path.

Новая campaign functionality использует ResearchPlanner, ResearchCampaignPlan и RunMarketResearchCampaign.

Mutable ResearchCampaign не расширяется partial completion, worker state или retry metadata.

Его удаление не входит в первый ExperimentExecution slice.

## Legacy persistence use cases

RunResearchCycle, RunAndStoreSerializedResearchCycle и RunAndStoreSerializedResearchCampaign имеют статус RETIRED_FROM_PRODUCTION.

Architecture test уже запрещает их использование другим production code.

До удаления необходимо проверить:

- package exports;
- direct tests;
- examples;
- stored cycle and campaign readers;
- внешние imports, если они документированы.

Удаление этих use cases не должно удалять backward readers существующих SQLite records.

Каждый persistence path удаляется отдельным commit или одним commit только при доказанно общей dependency boundary.

## Market data compatibility

LegacyMarketDataProvider и LegacyMarketDataFrameAdapter имеют статус ACTIVE_COMPATIBILITY.

LegacyMarketDataFrameAdapter является допустимым anti-corruption layer.

Новые domain и analysis services не должны знать legacy column names.

Миграция завершается, когда все production providers возвращают canonical timestamp и canonical OHLCV columns напрямую.

До этого adapter сохраняется и тестируется.

Поддержка нового legacy column variant не добавляется без отдельного входного contract decision.

## Backtest compatibility

LegacyMarketBacktestExecutor и legacy signal mapper имеют статус CONTAINED.

Новые execution contracts используют prepared executor boundary.

Удаление legacy executor возможно после подтверждения, что production composition roots, examples и tests используют prepared path.

Поведенческий parity для position, trade, commission, slippage и exit rules должен быть подтверждён tests.

## ResearchRecommendationQuestionAdapter

ResearchRecommendationQuestionAdapter имеет статус ACTIVE_COMPATIBILITY.

Он соединяет современную recommendation chain с существующим ResearchQuestion contract.

Adapter сохраняется до стабилизации публичного use case генерации research questions и его DTO.

Knowledge Domain не изменяется ради удаления этого adapter.

## ResearchArtifact compatibility models

Существующие ResearchArtifact, ArtifactMetadata, ArtifactLineage, ArtifactHistoryEntry и ArtifactComparison мигрируют только вместе с реальным ResearchArtifactEnvelope production slice.

Они не становятся base classes envelope.

Legacy artifact readers сохраняются до миграции соответствующего artifact_type.

Каждый artifact type мигрирует отдельно.

## Recovery file

`src/research/engine.py.broken` не импортируется production code.

Файл является кандидатом на статус REMOVABLE.

Перед удалением необходимо подтвердить:

- отсутствие imports и tooling references;
- отсутствие уникального необходимого кода;
- наличие истории восстановления в Git;
- прохождение полного suite после удаления.

Удаление выполняется отдельным housekeeping commit.

## Persistence and data migration

SQLite tables и JSON artifacts считаются пользовательскими данными.

Запрещено:

- удалять таблицу без versioned migration;
- изменять значение существующего поля на новый смысл;
- перезаписывать artifacts на месте без проверки;
- терять exact version references;
- предполагать, что старых данных нет.

Для изменяемого формата применяется порядок:

1. новый writer создаёт новую schema version;
2. reader временно поддерживает старую и новую версии;
3. migration tool или controlled read-upgrade тестируется на копии;
4. backup и rollback procedure документируются;
5. старый reader удаляется только после подтверждения миграции.

Dual write вводится только отдельным ADR, если действительно требуется.

## Architecture protection

Для каждой мигрируемой boundary предпочтителен architecture test, который:

- фиксирует разрешённых текущих consumers;
- запрещает новых consumers;
- допускает постепенное уменьшение allowlist;
- не требует импортировать legacy module для проверки;
- выдаёт точный список нарушений.

После удаления legacy component protection test либо удаляется вместе с ним, либо превращается в полный запрет на восстановление старого import path.

Architecture test не заменяет contract и integration tests.

## Commit policy

Один migration commit содержит один архитектурный шаг:

- replacement model;
- compatibility adapter;
- production wiring;
- consumer migration;
- protection test;
- data migration;
- legacy removal.

Несколько шагов можно объединить только если по отдельности repository не может оставаться в корректном состоянии и scope остаётся одной boundary.

Каждый commit проходит:

- targeted tests;
- полный test suite;
- git diff check;
- проверку точного списка staged files;
- отдельный push в main.

## Отклонённые варианты

### Полностью переписать ResearchEngine

Отклонено из-за риска потерять работающий production path и смешать несколько migrations.

### Немедленно удалить всё, что не подключено к CLI

Отклонено из-за возможных persisted-data, tests и external compatibility consumers.

### Сохранять legacy бессрочно

Отклонено. Для каждой boundary существуют проверяемые removal gates.

### Наследовать новые модели от legacy

Отклонено, потому что это переносит старые invariants в целевую архитектуру.

### Поддерживать два равноправных production paths

Отклонено. Legacy path существует только как временная compatibility boundary.

## Последствия

Migration станет измеримой по production consumers и removal gates, а не по возрасту файлов.

Работающий ResearchEngine останется доступным во время внедрения ExperimentExecution.

Persisted data и CLI contracts будут защищены от случайного разрушения.

Legacy adapters смогут временно существовать без проникновения в новую доменную модель.

После принятия этого ADR обязательный governance-набор для первого implementation slice завершён.

Следующей задачей является минимальный ExperimentExecution kernel для одного market experiment path.

## Связанные документы

- `ARCHITECTURE_INVENTORY.md`
- `ARCHITECTURE_STATUS.md`
- `docs/adr/ADR-001-knowledge-feature-freeze.md`
- `docs/adr/ADR-002-research-runtime-boundary.md`
- `docs/adr/ADR-003-experiment-execution-lifecycle.md`
- `docs/adr/ADR-004-research-artifact-envelope.md`
- `docs/adr/ADR-005-application-layer-classification.md`