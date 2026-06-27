# Server

## Что делает сервис

`server` принимает лог-строки, валидирует их, сохраняет в PostgreSQL и отдаёт записи через HTTP API.

Структура:
- `api` — роуты и зависимости.
- `services` — прикладная логика.
- `database/crud` — SQLAlchemy-запросы.
- `database/models` — ORM-модели.

## Запуск

Из корня проекта:

```bash
cp .env.example .env
docker compose up --build server db
```

Сервис доступен на `http://localhost:8000`.

## Технологии

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy Async
- asyncpg
- PostgreSQL
- Alembic

## Переменные окружения

- `LOG_LEVEL`
- `LOG_FORMAT`
- `API_HOST`
- `API_PORT`
- `API_RELOAD`
- `DATABASE_URL`
- `DATABASE_URL_DOCKER`

## API

### `POST /api/data`

Принимает:

```json
{
  "log": "192.168.1.1 GET /api/users 200"
}
```

Возвращает `201 Created` с `id`, `created_at` и разобранным `log`.

### `GET /api/data`

Поддерживает:
- `limit`
- `offset`
- `method`
- `status_code`
- `cursor_created_at`
- `cursor_id`

### `GET /api/stats`

Возвращает агрегированную статистику по методам и статус-кодам на основе записей в БД.

## Решения и допущения

- Миграции применяются при старте контейнера командой `alembic upgrade head`.
- Для `GET /api/data` используется offset-пагинация и cursor для `worker`.
- Для `GET /api/stats` используются агрегирующие SQL-запросы, без загрузки всех строк в Python.
