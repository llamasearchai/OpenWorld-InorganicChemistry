FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/

# Allow opting into agents deps at build time
ARG ENABLE_AGENTS=0
RUN python -m pip install --upgrade pip && \
    python -m pip install -e . && \
    if [ "$ENABLE_AGENTS" = "1" ]; then python -m pip install "openai-agents>=0.4.0"; fi

ENV FASTAPI_HOST=0.0.0.0 \
    FASTAPI_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["python", "-m", "uvicorn", "scipaper.main:app", "--host", "0.0.0.0", "--port", "8000"]
