# Worker

## Что делает сервис

`worker` периодически запрашивает `server` через `GET /api/data` и сохраняет полученные записи в общий `JSONL`-файл.

## Как работает

- при первом запуске сохраняет первую страницу записей
- дальше читает только новые записи через cursor
- пишет результат в Docker volume
- использует file lock, чтобы несколько экземпляров не писали в файл одновременно

## Запуск

Из корня проекта:

```bash
cp .env.example .env
docker compose up --build worker
```

По умолчанию сервис читает API по адресу `http://server:8000`.

## Переменные окружения

- `LOG_LEVEL`
- `LOG_FORMAT`
- `WORKER_API_URL`
- `WORKER_API_URL_DOCKER`
- `WORKER_POLL_INTERVAL_SECONDS`
- `WORKER_PAGE_SIZE`
- `WORKER_OUTPUT_FILE`

## Решения

- `worker` не работает с БД напрямую, только через API `server`.
- Для защиты от дублей используется cursor по `created_at` и `id`.
- Формат файла — `JSONL`: одна строка — одна запись.
- При первом запуске `worker` сохраняет только первую страницу текущих записей, после этого продолжает чтение новых записей через cursor.

## Как посмотреть файл

Результат сохраняется в `worker/data/log_entries.jsonl`.

```bash
docker compose exec worker sh -c "tail -n 20 /app/worker/data/log_entries.jsonl"
```
