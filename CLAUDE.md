# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

OpenWorld-InorganicChemistry is a Python-based platform for inorganic materials discovery using LLMs and AI agents. The codebase is organized into several key modules:

### Core Package Structure

- `openinorganicchemistry/core/` - Core utilities and settings
  - `settings.py` - Configuration management with environment/keychain API key loading
  - `chemistry.py` - Chemical computation utilities
  - `dft_utils.py` - Density Functional Theory utilities
  - `storage.py` - Data storage and persistence
  - `plotting.py` - Visualization utilities

- `openinorganicchemistry/agents/` - AI agents for different tasks
  - `simulation.py` - Molecular simulation agent
  - `analysis.py` - Data analysis agent
  - `codex.py` - Code generation and execution agent
  - `literature.py` - Literature search and analysis
  - `synthesis.py` - Synthesis planning agent
  - `optimization.py` - Materials optimization
  - `orchestration.py` - Multi-agent coordination
  - `collaboration.py` - Team collaboration features
  - `ml_prediction.py` - Machine learning predictions
  - `data_io.py` - Data input/output handling
  - `reporting.py` - Report generation

- `openinorganicchemistry/integrations/` - External service integrations
  - `websearch.py` - Web search functionality
  - `lit_sources.py` - Literature source integrations
  - `sgpt.py` - Shell-GPT integration

### Entry Points

- `cli.py` - Command-line interface
- `api.py` - FastAPI web server

## Development Commands

### Environment Setup
```bash
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .
pip install pytest httpx
```

### Testing
```bash
pytest -q                    # Run all tests quietly
python -m tox -q            # Run tests via tox (preferred)
```

### Code Quality
```bash
ruff check .                # Lint code
black .                     # Format code
mypy openinorganicchemistry # Type checking
```

### Running the Application
```bash
python -m openinorganicchemistry.cli --help    # CLI help
uvicorn openinorganicchemistry.api:app --reload # Run API server
```

### Build and Deploy
```bash
python -m build             # Build package
docker build -t openinorganicchemistry:latest . # Build Docker image
docker run -p 8000:8000 openinorganicchemistry:latest # Run containerized
```

## Configuration

- Environment variables or `.env` file for configuration
- `OPENAI_API_KEY` - Required for LLM functionality
- `OIC_MODEL_GENERAL` - General purpose model (default: gpt-4o)
- `OIC_MODEL_FAST` - Fast model (default: gpt-4o-mini)
- `OIC_VERBOSE` - Enable verbose logging (default: 0)

API keys are loaded with precedence: Environment → macOS Keychain → None

## Testing Strategy

- Tests are in `tests/` directory
- Mock-based testing to avoid external API dependencies
- CI runs on Ubuntu and macOS via GitHub Actions
- Coverage tracking with `.coverage` file

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:
- Black formatting
- Ruff linting
- MyPy type checking

## Key Dependencies

- FastAPI + Uvicorn for API server
- LangChain for LLM integration
- OpenAI Python client
- Pydantic for data validation
- Motor for MongoDB integration
- Python-dotenv for environment management

## Development Patterns

- Type annotations throughout (`from __future__ import annotations`)
- Dataclass-based configuration
- Async/await patterns in API handlers
- Mock-based testing for external dependencies
- Modular agent architecture for extensibility