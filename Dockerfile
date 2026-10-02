FROM python:3.12-slim AS builder
WORKDIR /app
RUN python -m venv .venv
COPY requirements.txt .
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home appuser
COPY --from=builder /app/.venv ./.venv
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]