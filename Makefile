.PHONY: deps test lint fmt type build docker run api

deps:
	@python -m pip install --upgrade pip
	@pip install -e ".[dev]"

test:
	@python -m tox -q

lint:
	@ruff check .

fmt:
	@black .

type:
	@mypy openinorganicchemistry

build:
	@python -m build

docker:
	@docker build -t openinorganicchemistry:latest .

run:
	@oic

api:
	@oic.api --host 127.0.0.1 --port 8000


