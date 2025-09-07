FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY openinorganicchemistry ./openinorganicchemistry
COPY tools ./tools
COPY tests ./tests

RUN pip install --upgrade pip && pip install -e ".[dev]"

ENTRYPOINT ["oic"]
CMD ["--help"]


