# Проект

Проект состоит из четырёх сервисов:
- `server` принимает лог-строки через FastAPI, валидирует их, сохраняет в PostgreSQL и отдаёт через API.
- `client` генерирует лог-строки и отправляет их в `server`.
- `worker` периодически читает данные из `server` через `GET /api/data` и сохраняет их в общий файл.
- `db` хранит записи `LogEntry`.

## Архитектура

Связи между сервисами простые:
- `client -> server`
- `worker -> server`
- `server -> db`

С базой данных работает только `server`.

Структура проекта:
- [server](D:/Workplace/TZMvideo/server) — API, валидация, логика работы с БД.
- [client](D:/Workplace/TZMvideo/client) — генерация и отправка логов.
- [worker](D:/Workplace/TZMvideo/worker) — периодический фоновый сбор данных из API.
- [core](D:/Workplace/TZMvideo/core) — общие настройки и логгирование.

## Запуск

1. Создать `.env` на основе `.env.example`.
2. Запустить проект:

```bash
docker compose up --build
```

После старта:
- API доступно на `http://localhost:8000`
- `client` отправляет логи в `server`
- `worker` периодически запрашивает `server` и пишет результат в файл внутри Docker volume

## Переменные окружения

Общие:
- `LOG_LEVEL` — уровень логирования.
- `LOG_FORMAT` — формат логов: `console` или `json`.

Server:
- `API_HOST`
- `API_PORT`
- `API_RELOAD`
- `DATABASE_URL`

PostgreSQL:
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST_DOCKER`
- `POSTGRES_PORT_DOCKER`

Client:
- `CLIENT_API_URL`
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
- `WORKER_POLL_INTERVAL_SECONDS`
- `WORKER_PAGE_SIZE`
- `WORKER_OUTPUT_FILE`
- `WORKER_OUTPUT_FILE_DOCKER`

## API

### `POST /api/data`

Принимает тело:

```json
{
  "log": "192.168.1.1 GET /api/users 200"
}
```

Возвращает `201 Created`:

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

Поддерживает параметры:
- `limit`
- `offset`
- `method`
- `status_code`
- `cursor_created_at`
- `cursor_id`

Пример обычного запроса:

```bash
curl "http://localhost:8000/api/data?limit=10&offset=0"
```

Пример cursor-запроса для `worker`:

```bash
curl "http://localhost:8000/api/data?limit=10&offset=0&cursor_created_at=2025-01-01T12:00:00Z&cursor_id=00000000-0000-0000-0000-000000000000"
```

## Принятые решения и допущения

- Основная модель данных называется `LogEntry`.
- Валидация лог-строки выполняется только в `server`.
- `client` и `worker` не работают с БД напрямую, только через HTTP API `server`.
- `worker` пишет записи в общий `JSONL`-файл: одна строка — один JSON-объект.
- Чтобы несколько экземпляров `worker` не писали в файл одновременно, используется file lock.
- Чтобы `worker` не записывал дубликаты, он берёт `created_at` и `id` из последней строки файла и продолжает чтение через cursor.
- При первом запуске `worker` сохраняет только первую страницу текущих записей, а дальше читает только новые.
