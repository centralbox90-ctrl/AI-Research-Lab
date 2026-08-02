# Private VPS Operations

Этот runbook описывает утверждённый эксплуатационный профиль AI Research Lab:

- закрытый однопользовательский VPS;
- один оператор;
- read-only HTTP API;
- Bearer token application boundary;
- TLS termination через Caddy;
- Waitress доступен только через loopback;
- SQLite остаётся authoritative persistence;
- public multi-user и SaaS-функции не входят в этот профиль.

## Deployment topology

Внешний трафик проходит только по следующему маршруту:

Client → HTTPS Caddy → 127.0.0.1:8080 Waitress → Application → SQLite

Ограничения:

- Порт 8080 не должен быть открыт во внешнем firewall.
- Caddy принимает внешний трафик на портах 80 и 443.
- Waitress принимает соединения только на 127.0.0.1.

## Filesystem layout

Рекомендуемые production paths:

- application: /opt/ai-research-lab/current
- virtual environment: /opt/ai-research-lab/venv
- SQLite state: /var/lib/ai-research-lab
- validated backups: /var/backups/ai-research-lab
- private environment: /etc/ai-research-lab/ai-research-lab.env
- systemd unit: /etc/systemd/system/ai-research-lab.service
- Caddy configuration: /etc/caddy/Caddyfile

## Host preparation

Создать отдельного системного пользователя:

```bash
sudo useradd \
  --system \
  --home /nonexistent \
  --shell /usr/sbin/nologin \
  ai-research-lab
```

Создать каталоги и назначить владельца:

```bash
sudo install -d -o ai-research-lab -g ai-research-lab \
  /opt/ai-research-lab/current \
  /opt/ai-research-lab/venv \
  /var/lib/ai-research-lab \
  /var/backups/ai-research-lab \
  /etc/ai-research-lab
```

Установить минимальные компоненты:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv caddy
```

## Application configuration

Секреты и токены должны храниться в приватном env-файле:

```bash
sudo install -m 600 /dev/null /etc/ai-research-lab/ai-research-lab.env
sudo tee /etc/ai-research-lab/ai-research-lab.env >/dev/null <<'EOF'
AI_RESEARCH_LAB_API_TOKEN=CHANGE_ME
EOF
```

## Service deployment

Скопировать приложение в production path и создать виртуальное окружение:

```bash
sudo rsync -a --delete /path/to/repo/ /opt/ai-research-lab/current/
sudo python3 -m venv /opt/ai-research-lab/venv
sudo /opt/ai-research-lab/venv/bin/pip install --upgrade pip
sudo /opt/ai-research-lab/venv/bin/pip install -r /opt/ai-research-lab/current/requirements.txt
```

Установить systemd unit и Caddy configuration:

```bash
sudo cp /opt/ai-research-lab/current/deploy/ai-research-lab.service /etc/systemd/system/ai-research-lab.service
sudo cp /opt/ai-research-lab/current/deploy/Caddyfile.example /etc/caddy/Caddyfile
```

После этого активировать сервисы:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-research-lab
sudo systemctl restart ai-research-lab caddy
sudo systemctl status ai-research-lab caddy
```

## Operational constraints

- API должен быть доступен только через локальный reverse proxy.
- Публичный доступ разрешён только на 80/443 у Caddy.
- Waitress должен слушать только 127.0.0.1:8080.
- SQLite файл должен находиться в /var/lib/ai-research-lab.
- Любые изменения конфигурации должны сопровождаться проверкой статуса сервисов и health endpoint.

## Backup and recovery

Рекомендуемая схема резервного копирования:

```bash
sudo mkdir -p /var/backups/ai-research-lab
sudo cp -a /var/lib/ai-research-lab /var/backups/ai-research-lab/$(date +%F_%H%M%S)
```

Перед восстановлением обязательно:

1. остановить сервис;
2. подтвердить наличие валидной резервной копии;
3. вернуть состояние в целевую директорию;
4. запустить сервис и проверить health endpoint.

## Security notes

- не раскрывать AI_RESEARCH_LAB_API_TOKEN в логах, issue tracker или чатах;
- не открывать порт 8080 во внешнем firewall;
- использовать только TLS через Caddy;
- хранить production env-файл с правами 0600;
- запрещено включать public multi-user или SaaS-функции в этом профиле.


## Application installation

Получить исходный код:

```bash
sudo git clone \
  https://github.com/centralbox90-ctrl/AI-Research-Lab.git \
  /opt/ai-research-lab/current
```

Создать production virtual environment:

```bash
sudo python3 -m venv \
  /opt/ai-research-lab/venv

sudo /opt/ai-research-lab/venv/bin/python \
  -m pip install \
  --upgrade pip

sudo /opt/ai-research-lab/venv/bin/python \
  -m pip install \
  -r /opt/ai-research-lab/current/requirements.txt

sudo /opt/ai-research-lab/venv/bin/python \
  -m pip check
```

Перед первым запуском выполнить полный suite:

```bash
cd /opt/ai-research-lab/current

sudo /opt/ai-research-lab/venv/bin/python \
  -m pytest \
  -q
```

## API token

Production entry point требует переменную:

`AI_RESEARCH_LAB_API_TOKEN`

Требования:

- минимум 32 символа;
- только ASCII;
- без начальных и конечных пробелов;
- секрет не хранится в Git.

Сгенерировать token:

```bash
python3 -c \
  "import secrets; print(secrets.token_urlsafe(48))"
```

Установить environment template:

```bash
sudo install \
  -o root \
  -g root \
  -m 0600 \
  /opt/ai-research-lab/current/deploy/ai-research-lab.env.example \
  /etc/ai-research-lab/ai-research-lab.env
```

Открыть файл и заменить `CHANGE_ME` сгенерированным token:

```bash
sudoedit \
  /etc/ai-research-lab/ai-research-lab.env
```

Placeholder `CHANGE_ME` намеренно короче минимальной длины.
С ним production server обязан отказаться от запуска.

## systemd service

Установить unit:

```bash
sudo install \
  -o root \
  -g root \
  -m 0644 \
  /opt/ai-research-lab/current/deploy/ai-research-lab.service \
  /etc/systemd/system/ai-research-lab.service
```

Проверить unit до запуска:

```bash
sudo systemd-analyze verify \
  /etc/systemd/system/ai-research-lab.service
```

Перечитать конфигурацию и запустить приложение:

```bash
sudo systemctl daemon-reload

sudo systemctl enable \
  --now \
  ai-research-lab.service
```

Проверить состояние:

```bash
sudo systemctl status \
  ai-research-lab.service
```


## Caddy and TLS

Установить Caddy из официального репозитория для используемого
Linux distribution.

Скопировать template:

```bash
sudo install \
  -o root \
  -g root \
  -m 0644 \
  /opt/ai-research-lab/current/deploy/Caddyfile.example \
  /etc/caddy/Caddyfile
```

Заменить `research.example.com` реальным DNS-именем:

```bash
sudoedit /etc/caddy/Caddyfile
```

DNS A/AAAA records должны указывать на VPS. Внешние порты `80` и
`443` должны быть доступны Caddy. Порт `8080` должен оставаться
закрытым извне.

Проверить конфигурацию:

```bash
sudo caddy validate \
  --config /etc/caddy/Caddyfile
```

Применить конфигурацию:

```bash
sudo systemctl enable \
  --now \
  caddy

sudo systemctl reload caddy
```

При корректном DNS Caddy автоматически получает и обновляет TLS
certificate и выполняет redirect с HTTP на HTTPS.

Caddy HTTP access log в template не включён. Безопасный application
log не содержит query string, request body или Bearer token.

## Health and readiness

Liveness:

```bash
curl \
  --fail \
  --silent \
  https://research.example.com/health
```

Readiness:

```bash
curl \
  --fail \
  --silent \
  https://research.example.com/ready
```

`/health` подтверждает работу HTTP process.

`/ready` дополнительно подтверждает доступность SQLite.

Оба endpoint намеренно доступны без Bearer token и не возвращают
исследовательские данные.

Проверка защищённого endpoint без token должна вернуть `401`:

```bash
curl \
  --silent \
  --output /dev/null \
  --write-out '%{http_code}\n' \
  https://research.example.com/v1/research-cycles
```

Для authenticated smoke test передать настоящий token:

```bash
curl \
  --fail \
  --silent \
  --header "Authorization: Bearer REPLACE_WITH_TOKEN" \
  https://research.example.com/v1/research-cycles
```

## Logs

Application и Waitress logs поступают в systemd journal:

```bash
sudo journalctl \
  --unit ai-research-lab.service \
  --follow
```

Последние записи текущего boot:

```bash
sudo journalctl \
  --unit ai-research-lab.service \
  --boot \
  --no-pager
```

Caddy runtime errors:

```bash
sudo journalctl \
  --unit caddy \
  --follow
```

Application HTTP log содержит только:

- method;
- route template;
- response status;
- duration.

Query string, body и Authorization header не журналируются.


## Online backup

SQLite backup создаётся через SQLite backup API. Production service
может продолжать работать во время создания backup.

Перейти в application directory:

```bash
cd /opt/ai-research-lab/current
```

Сформировать уникальное UTC-имя:

```bash
BACKUP_PATH="/var/backups/ai-research-lab/research-$(date -u +%Y%m%dT%H%M%SZ).db"
```

Создать backup от имени service user:

```bash
sudo -u ai-research-lab \
  /opt/ai-research-lab/venv/bin/python \
  -m src.storage.sqlite_backup_cli \
  create \
  --database /var/lib/ai-research-lab/research.db \
  --backup "$BACKUP_PATH"
```

Повторно проверить backup:

```bash
sudo -u ai-research-lab \
  /opt/ai-research-lab/venv/bin/python \
  -m src.storage.sqlite_backup_cli \
  verify \
  --backup "$BACKUP_PATH"
```

Успешный backup необходимо копировать на отдельное защищённое
хранилище. Копия только на том же VPS не защищает от потери сервера.

Автоматическое удаление старых backups не включено: retention policy
должна быть утверждена до любых destructive cleanup commands.

## Restore

Restore является controlled maintenance operation.

До восстановления:

1. выбрать проверенный backup;
2. остановить application service;
3. сохранить текущую базу как recoverable rollback copy;
4. не удалять исходную базу;
5. восстановить backup только в отсутствующий target.

Остановить приложение:

```bash
sudo systemctl stop \
  ai-research-lab.service
```

Проверить выбранный backup:

```bash
cd /opt/ai-research-lab/current

sudo -u ai-research-lab \
  /opt/ai-research-lab/venv/bin/python \
  -m src.storage.sqlite_backup_cli \
  verify \
  --backup /var/backups/ai-research-lab/SELECTED_BACKUP.db
```

Переместить текущую базу в rollback copy:

```bash
RESTORE_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

sudo mv \
  /var/lib/ai-research-lab/research.db \
  "/var/lib/ai-research-lab/research.db.pre-restore-$RESTORE_STAMP"
```

Если существуют `research.db-wal` или `research.db-shm`, их также
необходимо переместить с тем же suffix.

Восстановить проверенный backup:

```bash
sudo -u ai-research-lab \
  /opt/ai-research-lab/venv/bin/python \
  -m src.storage.sqlite_backup_cli \
  restore \
  --backup /var/backups/ai-research-lab/SELECTED_BACKUP.db \
  --database /var/lib/ai-research-lab/research.db
```

Запустить service:

```bash
sudo systemctl start \
  ai-research-lab.service
```

Проверить readiness:

```bash
curl \
  --fail \
  --silent \
  https://research.example.com/ready
```

Rollback copy нельзя удалять до успешной проверки приложения и
исследовательских данных.


## Controlled application update

Перед обновлением:

1. создать и проверить backup;
2. записать текущий commit;
3. получить конкретный утверждённый commit;
4. обновить pinned dependencies;
5. выполнить полный suite;
6. перезапустить service;
7. проверить readiness и authenticated read.

Зафиксировать текущую версию:

```bash
cd /opt/ai-research-lab/current

PREVIOUS_COMMIT="$(git rev-parse HEAD)"
```

Получить новую версию:

```bash
sudo git fetch origin

sudo git checkout \
  --detach \
  APPROVED_COMMIT_SHA
```

Обновить зависимости и проверить проект:

```bash
sudo /opt/ai-research-lab/venv/bin/python \
  -m pip install \
  -r requirements.txt

sudo /opt/ai-research-lab/venv/bin/python \
  -m pip check

sudo /opt/ai-research-lab/venv/bin/python \
  -m pytest \
  -q
```

Перезапустить и проверить:

```bash
sudo systemctl restart \
  ai-research-lab.service

curl \
  --fail \
  --silent \
  https://research.example.com/ready
```

Если проверка не прошла, вернуть предыдущий commit, восстановить его
dependencies и снова перезапустить service:

```bash
sudo git checkout \
  --detach \
  "$PREVIOUS_COMMIT"
```

Database restore выполняется только при подтверждённой несовместимости
или повреждении данных. Обычный rollback кода не должен автоматически
откатывать SQLite.

## Token rotation

Сгенерировать новый token, заменить значение в root-only environment
file и перезапустить service:

```bash
sudoedit \
  /etc/ai-research-lab/ai-research-lab.env

sudo systemctl restart \
  ai-research-lab.service
```

После rotation старый token должен перестать проходить authentication.

## Explicitly deferred scope

Этот deployment profile не добавляет:

- пользователей и регистрацию;
- роли и permissions;
- OAuth;
- multitenancy;
- public write API;
- PostgreSQL;
- Redis;
- queues и workers;
- Kubernetes;
- distributed runtime;
- billing.

Переход к public multi-user product требует отдельной архитектурной и
security phase.
