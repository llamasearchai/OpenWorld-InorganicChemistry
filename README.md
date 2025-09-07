## OpenInorganicChemistry

Building better panels with fewer researchers. OpenInorganicChemistry is a macOS-compatible, Dockerizable Python research platform that automates solar materials workflows: literature review, synthesis planning, simulation, analysis, and reporting.

- Author: Nik Jois
- License: MIT

### Highlights
- OpenAI Agents SDK orchestration and OpenAI Responses API integration
- CLI (Typer + Rich) with interactive menu
- FastAPI service exposing all actions as HTTP endpoints
- Secure key handling (env, .env, macOS Keychain via keyring)
- Tests (pytest + tox) and CI (GitHub Actions)
- Dockerfile and Devcontainer

### Quickstart
1) Create a virtualenv and install
```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

2) Configure OpenAI API key
```bash
export OPENAI_API_KEY="sk-..."
# or copy .env.example to .env and fill in
```

3) Run the CLI
```bash
oic
```

4) Run the API server
```bash
oic.api --host 127.0.0.1 --port 8000
# or: uvicorn openinorganicchemistry.api:app --reload
```

5) Run tests
```bash
tox
```

### Agents SDK
Install Agents SDK extras if you plan to use the orchestration command:
```bash
pip install .[agents]
```

### Security
- Never commit secrets. Prefer env vars or macOS Keychain (keyring)

### License
MIT


