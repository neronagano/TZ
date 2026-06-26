# Server

## 1. Краткое описание архитектуры решения
Сервер реализован на `FastAPI` и разделён на слои:
- `api` — HTTP-роуты и зависимости.
- `services` — прикладные сценарии.
- `database/crud` — работа с PostgreSQL.
- `database/models` — ORM-модели.
- `core` в корне проекта — общие настройки и логгирование для `server` и `client`.

## 2. Инструкция по запуску проекта
Из корня проекта:

```bash
cp .env.example .env
docker compose up --build
```

Сервер будет доступен по `http://localhost:8000`.

## 3. Используемые технологии
- Python 3.12
- FastAPI
- Pydantic / pydantic-settings
- SQLAlchemy Async + asyncpg
- PostgreSQL
- Alembic
- Docker / Docker Compose

## 4. Переменные окружения
- `LOG_LEVEL` — уровень логирования.
- `LOG_FORMAT` — формат логов: `console` или `json`.
- `API_HOST` — host для Uvicorn.
- `API_PORT` — порт сервера.
- `API_RELOAD` — autoreload для локального запуска.
- `DATABASE_URL` — строка подключения приложения к PostgreSQL.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — параметры базы для Docker Compose.
- `POSTGRES_HOST_DOCKER`, `POSTGRES_PORT_DOCKER` — адрес базы внутри docker-сети.

## 5. Архитектурные решения и допущения
- `POST /api/data` валидирует лог-строку, сохраняет запись в БД и возвращает `id`, `created_at`, `log`.
- `GET /api/data` поддерживает пагинацию и фильтры `limit`, `offset`, `method`, `status_code`.
- Список записей сортируется по `created_at DESC`.
- Миграции применяются командой `alembic upgrade head` при старте server-контейнера.
- Ошибки валидации возвращаются как клиентские, ошибки БД — как `500`.

## 6. Примеры запросов к API
Создание записи:

```bash
curl -X POST http://localhost:8000/api/data \
  -H "Content-Type: application/json" \
  -d "{\"log\":\"192.168.1.1 GET /api/users 200\"}"
```

Получение записей:

```bash
curl "http://localhost:8000/api/data?limit=10&offset=0&method=GET&status_code=200"
```
