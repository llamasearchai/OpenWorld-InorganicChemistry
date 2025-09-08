# OpenWorld-InorganicChemistry

An open-source platform for inorganic materials discovery, synthesis, and analysis using LLMs and AI Agents.

## Overview

OpenWorld-InorganicChemistry accelerates discovery of new inorganic materials using modular agents for simulation, literature search, synthesis planning, and analysis. It provides a Python API, a CLI, and a FastAPI server, with optional web search integration.

## Quickstart

- Prereqs: Python 3.9+, `pip`, optional: `OPENAI_API_KEY` in your environment.

Install (editable):

```
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .
pip install pytest httpx
```

Run tests:

```
pytest -q
```

CLI help:

```
python -m openinorganicchemistry.cli --help
```

Run API locally:

```
uvicorn openinorganicchemistry.api:app --reload
```

Docker (API):

```
docker build -t oic-api .
docker run -p 8000:8000 oic-api
```

## Features

- Materials discovery: quick EMT simulation demo, DFT utilities, ML placeholders.
- Literature + Codex agents: query literature and synthesize answers with web context.
- Analysis: parse CSV results and generate convergence plots.
- API + CLI: FastAPI endpoints and command-line tasks.

## Configuration

- `.env` or environment variables provide keys (e.g., `OPENAI_API_KEY`).
- See `openinorganicchemistry/core/settings.py` for options and defaults.

## Development

- Format/lint: pre-commit hooks configured in `.pre-commit-config.yaml`.
- Tests: `pytest -q` (uses local mocks; no network required).
- CI: GitHub Actions runs tests on Ubuntu and macOS.

## License

MIT — see [LICENSE](LICENSE).

## Citation

See [CITATION.cff](CITATION.cff).
