# Produktionsplanung. Ein Prozess, keine Hintergrundaufträge.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /usr/local/bin/uv

WORKDIR /app

# Erst die Abhängigkeiten, damit der Zwischenspeicher hält.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app
COPY docs ./docs
COPY tests/daten ./tests/daten

# Ablage für die SQLite-Datei und die Exportdateien.
RUN mkdir -p /app/data /app/export

ENV PP_DATENBANK_URL=sqlite:////app/data/app.db \
    PP_EXPORT_PFAD=/app/export \
    PP_STARTDATEN_LADEN=false

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
