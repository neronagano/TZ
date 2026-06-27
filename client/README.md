# Client

## Что делает сервис

`client` генерирует лог-строки вида:

```text
<IP address> <HTTP method> <URI> <HTTP status code>
```

и отправляет их в `server` через `POST /api/data`.

## Как работает

- запускает несколько потоков
- делает случайную задержку между запросами
- логирует все отправки в файл

## Запуск

Из корня проекта:

```bash
cp .env.example .env
docker compose up --build client
```

По умолчанию сервис отправляет запросы в `http://server:8000`.

## Переменные окружения

- `LOG_LEVEL`
- `LOG_FORMAT`
- `API_URL`
- `API_URL_DOCKER`
- `CLIENT_WORKERS`
- `CLIENT_MAX_DELAY_MS`
- `CLIENT_REQUESTS_PER_WORKER`
- `CLIENT_LOG_FILE`
- `CLIENT_REQUEST_TIMEOUT_SECONDS`
- `CLIENT_MAX_ATTEMPTS`
- `CLIENT_RETRY_BACKOFF_MS`

## Решения

- Для конкурентной отправки используются потоки, этого достаточно для требований ТЗ.
- Формирование лог-строки и отправка разделены по разным сервисным модулям.
- Для локального запуска используется `API_URL`, а в Docker Compose адрес сервера задаётся через `API_URL_DOCKER`.
