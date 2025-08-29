# scipaper-cli

OA-first scientific paper toolkit: FastAPI microservice + CLI, with optional OpenAI Agents SDK integration and local Ollama fallback.

## Features
- Search arXiv and return rich metadata
- Download PDFs via open-access routes
- REST API with `/api/v1/search`, `/api/v1/fetch`, `/api/v1/health`, `/api/v1/parse`, `/api/v1/agents/run`
- CLI for quick usage: `scipaper search`, `scipaper fetch`, `scipaper agent`
- Optional Agents backend (OpenAI) with tool usage; falls back to local Ollama prompts

## Installation
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Run the API
```bash
make serve
# In another shell
scipaper health
```

## CLI Usage
```bash
# Health
scipaper health

# Search arXiv
scipaper search "graph transformer" -s arxiv -l 5

# Fetch a paper PDF to downloads/
scipaper fetch 2401.12345 -o downloads --rename

# Agent (optional)
scipaper agent "search retrieval augmented generation for long papers"
```

Parse identifiers from text or files:
```bash
# From text
scipaper parse --text "doi 10.1109/83.544569 arXiv:2407.13619" --match doi --match arxiv --format jsonl

# From a file
scipaper parse --path ./examples/page.html --format csv
```

## API Endpoints
- GET `/api/v1/health`
- POST `/api/v1/search` body: `{ "query": str, "sources": ["arxiv"], "limit": int }`
- POST `/api/v1/fetch` body: `{ "identifier": str, "output_dir": str, "rename": bool }`
- POST `/api/v1/parse` body: `{ "text"?: str, "path"?: str, "types"?: [str], "format": "raw|jsonl|csv" }`
- POST `/api/v1/agents/run` body: `{ "prompt": str }`

## Agents Integration (Optional)
- Install extras: `pip install -e .[agents]`
- Set `OPENAI_API_KEY` in environment
- If Agents SDK is unavailable or key is missing, the API returns 501 for `/agents/run` and the CLI informs about availability
- Local model fallback uses `ollama` if installed; otherwise tools can be invoked via simple prompt routing

## Docker
```bash
docker build -t scipaper-cli .
docker run --rm -p 8000:8000 -e FASTAPI_HOST=0.0.0.0 scipaper-cli
curl http://localhost:8000/api/v1/health
```

To enable Agents inside Docker, pass `-e OPENAI_API_KEY=...` and ensure network egress is allowed.

## Development
```bash
make setup
make test
```

Static analysis runs in CI using basedpyright and ruff. Configure your IDE to use `.venv` and `pyrightconfig.json`.

## License
MIT
