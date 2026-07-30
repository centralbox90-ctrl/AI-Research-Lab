# AI Research Lab

[![Tests](https://github.com/centralbox90-ctrl/AI-Research-Lab/actions/workflows/tests.yml/badge.svg)](https://github.com/centralbox90-ctrl/AI-Research-Lab/actions/workflows/tests.yml)

AI Research Lab — исследовательская платформа для систематического изучения финансовых рынков.

Проект развивает полный исследовательский цикл: от получения рыночных данных и расчёта индикаторов до сравнительной оценки результатов, формирования evidence и последующего накопления знаний. Отдельный backtest или значение метрики рассматривается как результат эксперимента, но не как готовый научный вывод.

## Текущий статус

В репозитории реализованы и покрыты тестами:

- загрузка и каноническое представление рыночных данных;
- автоматическое обнаружение подключаемых индикаторов;
- расчёт индикаторов и исследовательские сервисы;
- сравнительное исследование индикаторов;
- статистическая оценка сравнительных результатов;
- формирование evidence, Findings и формальная оценка гипотезы;
- запуск полного сравнительного Analysis-потока через JSON CLI-команду;
- воспроизводимое планирование и запуск рыночных исследовательских кампаний из согласованных JSON-контрактов;
- immutable и идемпотентное хранение research artifacts по `result_id`;
- integrity validation сохранённых artifact envelopes при публичном чтении;
- read-only просмотр append-only истории `ExperimentExecution` через CLI;
- read-only обнаружение сохранённых `ExperimentExecution` identities через CLI;
- end-to-end проверка связи production market research result, validated envelope и append-only `ExperimentExecution` history;
- composition roots для сборки прикладных сценариев;
- append-only Knowledge persistence и repository-backed feedback path;
- read-only HTTP API с OpenAPI 3.1 contract;
- отдельные local Flask и production Waitress entry points;
- read-only MCP adapter с repository-backed stdio server;
- автоматическая проверка чистого checkout через GitHub Actions.

Основной этап архитектурной консолидации завершён. Knowledge feature development временно заморожена; текущий этап развивает внешние adapters поверх стабильного Application API.

## Архитектурный цикл

Целевая архитектура разделяет исследовательский процесс на последовательные домены:

1. Research — постановка вопроса и управление исследованием.
2. Experiment — описание и выполнение воспроизводимого эксперимента.
3. Calculation — расчёт индикаторов и других производных данных.
4. Signal — преобразование вычислений в торговые намерения.
5. Execution — моделирование исполнения и получение результата.
6. Analysis — интерпретация результатов и построение evidence.
7. Knowledge — сохранение подтверждённых выводов и их версий.

Основные архитектурные принципы:

- canonical market data является внутренним контрактом;
- Research не зависит от конкретного механизма Execution;
- расчёт индикаторов отделён от генерации сигналов;
- legacy-компоненты изолируются адаптерами;
- миграция выполняется вертикальными срезами;
- результат эксперимента не считается научным выводом без анализа.

## Структура проекта

- `src/application/` — прикладные сценарии и orchestration;
- `src/api/` — HTTP transport, OpenAPI и WSGI entry points;
- `src/mcp_adapter/` — MCP tools, composition root и stdio entry point;
- `src/cli/` — команды, composition roots и presenters;
- `src/data/` — загрузка рыночных данных;
- `src/indicators/` — индикаторы и механизм их обнаружения;
- `src/research/` — исследовательские модели и вычислительная оценка;
- `.github/workflows/` — автоматические проверки репозитория;
- `requirements.txt` — воспроизводимый набор зависимостей.

Архитектурные ответственности не обязаны полностью совпадать с физическими каталогами. Один домен может временно размещаться в нескольких модулях во время вертикальной миграции.

## Требования

Основной профиль разработки и CI:

- Windows;
- Python 3.13;
- MetaTrader 5 для сценариев, использующих терминал;
- виртуальное окружение Python.

MetaTrader5 устанавливается только на Windows. Остальные зависимости определены в `requirements.txt`.

## Установка

```powershell
git clone https://github.com/centralbox90-ctrl/AI-Research-Lab.git
cd AI-Research-Lab

py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python -m pip check
```

## Проверка

Полный набор тестов:

```powershell
python -m pytest -q
```

Та же проверка автоматически выполняется в GitHub Actions при push и pull request в ветку `main`.

## История ExperimentExecution

Полную append-only историю одного технического выполнения можно получить по `execution_id`:

```powershell
python -m src.cli.main `
    --database .research_lab/research-cycles.db `
    get-experiment-execution-history `
    <execution_id> `
    --compact
```

Команда возвращает versioned JSON с количеством snapshots и точной последовательностью состояний. Научные `Evidence`, `Finding` и `HypothesisEvaluation` не смешиваются с техническим execution status.

Список доступных `execution_id` можно получить отдельно:

```powershell
python -m src.cli.main `
    --database .research_lab/research-cycles.db `
    list-experiment-executions `
    --compact
```

Команда возвращает детерминированно отсортированный список identities из того же append-only SQLite recorder. Listing не изменяет состояния выполнений и не дублирует snapshots.

## HTTP API

HTTP boundary предоставляет три read-only операции: список research cycles, получение artifact и сравнение двух artifacts.

OpenAPI 3.1 contract доступен через `/openapi.json`.

Локальный development server:

```powershell
python -m src.api --database .research_lab/research-cycles.db --host 127.0.0.1 --port 8000
```

Production WSGI server:

```powershell
python -m src.api.production_server --database .research_lab/research-cycles.db --host 127.0.0.1 --port 8080 --threads 4
```

Production server по умолчанию использует loopback interface. Внешнее размещение, TLS, authentication, authorization, CORS и rate limiting настраиваются отдельным deployment boundary. Встроенный Flask server не предназначен для production.

## MCP adapter

MCP adapter использует официальный MCP Python SDK 2.0.0 и предоставляет три read-only tools:

- `list_research_cycles` — список сохранённых research cycles;
- `get_research_artifact` — получение одного artifact по `result_id`;
- `compare_research_artifacts` — сравнение двух сохранённых artifacts.

MCP host должен запускать server через stdio:

```powershell
python -m src.mcp_adapter --database .research_lab/research-cycles.db
```

При ручном запуске команда ожидает MCP-сообщения через stdin и не возвращает обычное приглашение терминала. Остановить server можно через Ctrl+C.

## Пример исследовательской кампании

Репозиторий содержит согласованные примеры входных документов:

- `examples/campaign_design.json`;
- `examples/campaign_registrations.json`.

Запуск примера:

```powershell
python -m src.cli.main `
    --database .research_lab/example-campaign.db `
    run-market-research-campaign `
    --design examples/campaign_design.json `
    --registrations examples/campaign_registrations.json
```

Registration JSON содержит идентификаторы, детерминированно вычисленные из Campaign Design. Поэтому оба файла необходимо изменять и проверять совместно.

## Локальные данные и артефакты

Каталоги локальных данных, исследовательского состояния и сгенерированных артефактов не публикуются в Git:

- `/data/`;
- `.project_memory/`;
- `.research_lab/`;
- `artifacts/`;
- локальные базы данных `*.db`.

Пакет `src/data/` является частью исходного кода и публикуется в репозитории.

## Правило развития

Каждый новый вертикальный срез должен включать:

1. доменный или прикладной контракт;
2. реализацию сценария;
3. composition root;
4. автоматические тесты;
5. обновление документации текущего состояния;
6. успешное прохождение GitHub Actions.