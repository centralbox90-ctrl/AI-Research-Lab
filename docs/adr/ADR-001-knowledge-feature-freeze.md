# ADR-001: Knowledge Feature Freeze

Дата: 28 июля 2026 года
Статус: Accepted

## Контекст

Knowledge Domain уже поддерживает цепочку:

KnowledgeCandidate → KnowledgeItem → KnowledgeRevision → KnowledgeRelation → Contradiction → KnowledgeGraphSnapshot → KnowledgeGap → ResearchRecommendation.

Persistence-адаптеры для KnowledgeRevision и KnowledgeRelation реализованы.

При этом production-путь Analysis заканчивается на HypothesisEvaluation, а Knowledge feedback начинается с внешнего snapshot JSON. Единого production-сценария пока нет:

HypothesisEvaluation → KnowledgeCandidate → validation → revision storage → contradiction detection → relation registration → snapshot → recommendation.

Архитектурная ширина начала расти быстрее вертикальной интеграции. Каждая новая Knowledge-сущность требует дополнительной инфраструктуры, пока уже существующие компоненты не соединены в воспроизводимый lifecycle.

## Решение

Вводится временная заморозка развития Knowledge Domain.

До выполнения условий выхода разрешены:

- исправления дефектов, проблем безопасности и целостности данных;
- тестирование существующих контрактов и адаптеров;
- архитектурная документация и ADR;
- оптимизация производительности без изменения семантики;
- подключение существующих Knowledge-контрактов к production composition roots;
- завершение пути Analysis → Persistent Knowledge → Recommendation;
- инфраструктурные адаптеры, необходимые существующим контрактам.

Запрещены:

- новые Knowledge-сущности;
- новые значения RelationType и GapType;
- расширение Knowledge Graph за пределы существующих контрактов;
- новые семантические эвристики;
- новые Knowledge CLI-сценарии;
- общие workflow, lifecycle, pipeline или orchestration abstractions;
- скрытое автоматическое продвижение результатов в Knowledge;
- замена exact-version relations семантикой latest-version.

Исключение из заморозки требует отдельного ADR.

## Knowledge promotion

Решение о допустимости продвижения результата относится к доменной политике PromotionPolicy.

Application Layer выполняет последствия принятого решения:

- создаёт и валидирует KnowledgeCandidate;
- сохраняет KnowledgeRevision;
- выявляет противоречия;
- регистрирует KnowledgeRelation;
- строит snapshot;
- запускает генерацию рекомендаций.

Repositories и infrastructure adapters не принимают эпистемических решений.

PromotionPolicy и PromotionDecision не создаются до проверки существующих эквивалентов и отдельного архитектурного решения.

## Условия выхода

Заморозка может быть пересмотрена после выполнения следующих условий:

1. Architecture Inventory принят как фактическая архитектурная база.
2. Приняты ADR для границы Research и runtime, ExperimentExecution, artifact envelope, классификации Application Layer и миграции legacy.
3. Один market experiment проходит через единый execution lifecycle.
4. Analysis → Persistent Knowledge → Recommendation выполняется без ручного snapshot-файла.
5. Публичные application use cases явно определены и стабилизированы.
6. Полный цикл воспроизводится из specification, данных, версии кода и artifacts.

## Последствия

Приоритет разработки переносится с расширения модели на интеграцию, воспроизводимость и стабилизацию.

Существующий Knowledge Domain сохраняется. Заморозка не означает его удаление или отказ от него.

SQLite-адаптеры остаются доступными для подключения к production-пути.

Внешние API не должны формировать новую Knowledge-семантику напрямую. Они будут добавлены как тонкие adapters после стабилизации Application API.

Пересмотр этого решения выполняется через новый ADR.

## Связанные документы

- `ARCHITECTURE_INVENTORY.md`
- `ARCHITECTURE_STATUS.md`