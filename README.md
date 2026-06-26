# Проект

Проект состоит из трёх сервисов:
- `server` принимает лог-строки через FastAPI, валидирует их, сохраняет в PostgreSQL и отдаёт через API.
- `client` генерирует лог-строки и отправляет их в `server`.
- `db` хранит записи `LogEntry`.

## Архитектура

Структура сделана простой и прямой:
- [server](/D:/Workplace/TZMvideo/server) — HTTP API, бизнес-логика и работа с БД.
- [client](/D:/Workplace/TZMvideo/client) — генерация и отправка логов.
- [core](/D:/Workplace/TZMvideo/core) — общие настройки и логгирование.

Связи между сервисами такие:
- `client -> server`
- `server -> db`

С базой данных работает только `server`.

## Запуск

1. Создать `.env` на основе `.env.example`.
2. Запустить проект:

```bash
docker compose up --build
```

После старта:
- API доступно на `http://localhost:8000`
- client отправит заданное число логов и завершится

## Переменные окружения

Основные:
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
- `CLIENT_API_URL` — адрес `server` для клиента внутри Docker.
- `CLIENT_WORKERS` — количество потоков.
- `CLIENT_MAX_DELAY_MS` — максимальная случайная задержка между запросами.
- `CLIENT_REQUESTS_PER_WORKER` — сколько запросов отправляет каждый поток.
- `CLIENT_LOG_FILE` — путь к лог-файлу при локальном запуске.
- `CLIENT_LOG_FILE_DOCKER` — путь к лог-файлу в контейнере.
- `CLIENT_REQUEST_TIMEOUT_SECONDS`
- `CLIENT_MAX_ATTEMPTS`
- `CLIENT_RETRY_BACKOFF_MS`

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

Пример:

```bash
curl "http://localhost:8000/api/data?limit=10&offset=0&method=GET&status_code=200"
```

## Принятые решения

- Основная модель называется `LogEntry`.
- Валидация лог-строки сделана на стороне `server`, чтобы все входные данные проходили через одну точку.
- `client` не знает ничего о БД и работает только через HTTP.
- Docker Compose поднимает только `db`, `server` и `client`, без дополнительных сервисов.
