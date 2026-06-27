# Проект

Проект состоит из четырёх сервисов:
- `server` принимает лог-строки через FastAPI, валидирует их, сохраняет в PostgreSQL и отдаёт через API.
- `client` генерирует лог-строки и отправляет их в `server`.
- `worker` периодически читает данные из `server` и пишет их в общий JSONL-файл.
- `db` хранит записи `LogEntry`.

## Архитектура

Связи между сервисами:
- `client -> server`
- `worker -> server`
- `server -> db`

С базой данных работает только `server`.

Структура проекта:
- [server](./server) — API, валидация, работа с БД.
- [client](./client) — генерация и отправка логов.
- [worker](./worker) — фоновая выгрузка данных из API в файл.
- [core](./core) — общие настройки и логгирование.
- [.env.example](./.env.example) — пример единого файла конфигурации.

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

После старта:
- API доступно на `http://localhost:8000`
- `client` отправляет логи в `server`
- `worker` сохраняет записи в Docker volume

Файл `worker` можно посмотреть так:

```bash
docker compose exec worker sh -c "tail -n 20 /app/worker/data/log_entries.jsonl"
```

## Переменные окружения

Общие:
- `LOG_LEVEL`
- `LOG_FORMAT`

PostgreSQL:
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

Server:
- `API_HOST`
- `API_PORT`
- `API_RELOAD`
- `DATABASE_URL`
- `DATABASE_URL_DOCKER`

Client:
- `API_URL`
- `API_URL_DOCKER`
- `CLIENT_WORKERS`
- `CLIENT_MAX_DELAY_MS`
- `CLIENT_REQUESTS_PER_WORKER`
- `CLIENT_LOG_FILE`
- `CLIENT_LOG_FILE_DOCKER`
- `CLIENT_REQUEST_TIMEOUT_SECONDS`
- `CLIENT_MAX_ATTEMPTS`
- `CLIENT_RETRY_BACKOFF_MS`

Worker:
- `WORKER_API_URL`
- `WORKER_API_URL_DOCKER`
- `WORKER_POLL_INTERVAL_SECONDS`
- `WORKER_PAGE_SIZE`
- `WORKER_OUTPUT_FILE`
- `WORKER_OUTPUT_FILE_DOCKER`

## API

### `POST /api/data`

Тело запроса:

```json
{
  "log": "192.168.1.1 GET /api/users 200"
}
```

Ответ `201 Created`:

```json
{
  "id": "uuid",
  "created_at": "2025-01-01T12:00:00Z",
  "log": {
    "ip": "192.168.1.1",
    "method": "GET",
    "uri": "/api/users",
    "status_code": 200
  }
}
```

### `GET /api/data`

Параметры:
- `limit`
- `offset`
- `method`
- `status_code`
- `cursor_created_at`
- `cursor_id`

Примеры:

```bash
curl "http://localhost:8000/api/data?limit=10&offset=0"
curl "http://localhost:8000/api/data?limit=10&offset=0&method=GET&status_code=200"
curl "http://localhost:8000/api/data?limit=10&cursor_created_at=2025-01-01T12:00:00Z&cursor_id=00000000-0000-0000-0000-000000000000"
```

### `GET /api/stats`

Возвращает агрегированную статистику по записям из БД:

```json
{
  "methods": {
    "GET": 120,
    "POST": 95
  },
  "status_codes": {
    "200": 210,
    "404": 15
  }
}
```

## Принятые решения

- Основная модель данных называется `LogEntry`.
- Валидация лог-строки выполняется только в `server`.
- `client` и `worker` не работают с БД напрямую.
- `worker` пишет записи в общий `JSONL`-файл.
- Чтобы несколько `worker` не писали в файл одновременно, используется file lock.
- Чтобы `worker` не писал дубликаты, он продолжает чтение через cursor по `created_at` и `id`.
- При первом запуске `worker` сохраняет только первую страницу текущих записей, после этого продолжает чтение новых записей через cursor.
