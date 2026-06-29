# Image shared by both processes (API + Telegram bot) on Fly.io.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app
COPY api ./api
COPY run.py ./run.py

# Default command (overridden per process group in fly.toml).
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
