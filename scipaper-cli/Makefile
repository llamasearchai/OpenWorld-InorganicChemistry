VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
UVICORN=$(PY) -m uvicorn

setup:
	python3 -m venv $(VENV)
	$(PIP) install -U pip wheel
	$(PIP) install -e .

test:
	$(PY) -m pytest -q

serve:
	$(UVICORN) scipaper.main:app --host 127.0.0.1 --port 8000

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

.PHONY: setup test serve docker-build docker-up docker-down docker-logs
