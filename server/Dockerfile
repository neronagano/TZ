FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/server

WORKDIR /app

COPY pyproject.toml ./

RUN python - <<'PY'
import pathlib
import tomllib

pyproject = tomllib.loads(pathlib.Path("pyproject.toml").read_text(encoding="utf-8"))
dependencies = pyproject["project"]["dependencies"]
pathlib.Path("requirements.txt").write_text("\n".join(dependencies) + "\n", encoding="utf-8")
PY

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY alembic.ini ./
COPY alembic ./alembic
COPY server ./server

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python server/main.py"]
