# Server

## 1. Краткое описание архитектуры решения
Сервер реализован на `FastAPI` и разделён на слои:
- `api` — HTTP-роуты и схемы зависимостей.
- `services` — прикладная логика сценариев.
- `database/crud` — работа с PostgreSQL.
- `database/models` — ORM-модели.
- `core` — настройки и логирование.

## 2. Инструкция по запуску проекта
Из корня проекта:

```bash
cp .env.example .env
docker compose up --build
```

После старта сервер доступен по `http://localhost:8000`.

## 3. Описание используемых технологий
- Python 3.12
- FastAPI
- Pydantic / pydantic-settings
- SQLAlchemy Async + asyncpg
- PostgreSQL
- Alembic
- Docker / Docker Compose

## 4. Перечень переменных окружения
- `LOG_LEVEL` — уровень логирования.
- `LOG_FORMAT` — формат логов: `console` или `json`.
- `API_HOST` — host для Uvicorn.
- `API_PORT` — порт сервера.
- `API_RELOAD` — режим autoreload для локального запуска.
- `POSTGRES_DB` — имя базы данных для Docker Compose.
- `POSTGRES_USER` — пользователь PostgreSQL.
- `POSTGRES_PASSWORD` — пароль PostgreSQL.
- `DATABASE_URL` — строка подключения приложения к PostgreSQL.

## 5. Описание принятых архитектурных решений и допущений
- `POST /api/data` валидирует лог-строку, сохраняет запись в БД и возвращает `id`, `created_at`, `log`.
- `GET /api/data` спроектирован с пагинацией и фильтрами: `limit`, `offset`, `method`, `status_code`.
- Сортировка списка записей выполняется по `created_at DESC`.
- Миграции применяются через `alembic upgrade head` при старте контейнера сервера.
- Ошибки парсинга возвращаются как ошибки клиента, ошибки БД — как `500`.

## 6. Примеры запросов к API
Создание записи:

```bash
curl -X POST http://localhost:8000/api/data/ \
  -H "Content-Type: application/json" \
  -d "{\"log\":\"192.168.1.1 GET /api/users 200\"}"
```

Получение записей:

```bash
curl "http://localhost:8000/api/data/?limit=10&offset=0&method=GET&status_code=200"
```
