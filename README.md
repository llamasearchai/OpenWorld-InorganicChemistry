# SciPaper 📚🔬

A comprehensive scientific paper management and analysis tool with AI-powered insights and multi-source data integration.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-blue.svg)](.github/workflows/ci.yml)

**Transform your research workflow with intelligent paper discovery, analysis, and management.**

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [REST API](#rest-api)
  - [Docker Deployment](#docker-deployment)
- [Architecture](#architecture)
- [Data Sources](#data-sources)
- [AI Integration](#ai-integration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

### 🔍 Multi-Source Search & Discovery
- **Comprehensive Coverage**: Query papers from arXiv, Crossref, PubMed, Semantic Scholar, and local Xrxiv dumps
- **Unified Search**: Single query interface across all sources with intelligent result merging
- **Smart Ranking**: Results prioritized by relevance, recency, and source authority
- **Batch Operations**: Process multiple papers simultaneously for large-scale analysis

### 🤖 AI-Powered Analysis
- **OpenAI Agents SDK**: Advanced AI agent framework for paper analysis and insights
- **Ollama Integration**: Local AI processing with privacy-preserving capabilities
- **Intelligent Summarization**: Automatic paper summaries and key finding extraction
- **Research Synthesis**: Cross-paper analysis and relationship identification

### 📝 Smart Content Processing
- **Identifier Recognition**: Automatic detection of DOIs, arXiv IDs, ISBNs, PubMed IDs, and URLs
- **Metadata Extraction**: Comprehensive paper metadata including authors, abstracts, citations
- **Format Conversion**: Support for BibTeX, CSL JSON, and other academic formats
- **Text Mining**: Extract research concepts, methodologies, and experimental details

### 🛠️ Developer-Friendly
- **RESTful API**: FastAPI-based endpoints with automatic OpenAPI documentation
- **Rich CLI**: Interactive command-line interface with rich formatting and progress indicators
- **Docker Support**: Containerized deployment with multi-platform compatibility
- **Extensible Architecture**: Plugin system for custom data sources and analysis modules

### 🚀 Performance & Reliability
- **Caching System**: Redis-backed caching for improved performance and reduced API calls
- **Rate Limiting**: Intelligent rate limiting with automatic backoff and retry
- **Error Handling**: Comprehensive error handling with detailed logging and recovery
- **Async Processing**: Non-blocking operations for high-throughput processing

## Quick Start

Get SciPaper up and running in 5 minutes:

```bash
# 1. Clone and setup
git clone https://github.com/llamasearchai/OpenWorld-InorganicChemistry.git
cd OpenWorld-InorganicChemistry
python -m venv .venv && source .venv/bin/activate

# 2. Install and run
pip install -e .
scipaper health

# 3. Search for papers
scipaper search "quantum chemistry" --limit 5

# 4. Extract identifiers from text
scipaper parse "Check out this paper: doi:10.1000/example"
```

## Installation

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key (optional, for AI features)
- Ollama (optional, for local AI processing)
- Redis (optional, for caching)

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd OpenPaper
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables: create a `.env` in the repo root with the variables from the Configuration section below.

### Docker

Build and run the API server:
```bash
docker build -t scipaper:latest .
docker run --rm -p 8000:8000 --env-file .env scipaper:latest
```

Using docker-compose:
```bash
docker compose up --build
```

## Configuration

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2

# Ollama Configuration (for local AI processing)
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3.2

# API Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_DEBUG=false

# External API Keys
SEMANTICSCHOLAR_API_KEY=your_semanticscholar_key_here

# File Paths
DOWNLOADS_DIR=./downloads
XRXIV_DUMP_PATH=./data/xrxiv.jsonl

# Logging
LOG_LEVEL=INFO
```

## Usage

### Command Line Interface

```bash
# Health check
scipaper health

# Search for papers
scipaper search "transformer neural networks" --sources arxiv,crossref --limit 5

# Fetch paper by identifier
scipaper fetch "10.1038/nature12373"

# Parse text for identifiers
scipaper parse "Check out this paper: doi:10.1038/nature12373 and arXiv:2103.12345"

# AI agent analysis
scipaper agent "Analyze the impact of transformer architecture on NLP"
```

### API Endpoints

Run the API locally:
```bash
uvicorn scipaper.main:app --host 0.0.0.0 --port 8000 --reload
```

The service provides RESTful API endpoints at `http://localhost:8000/api/v1/`:

#### Health Check
```bash
GET /api/v1/health
```

#### Search Papers
```bash
POST /api/v1/search
Content-Type: application/json

{
  "query": "transformer neural networks",
  "sources": ["arxiv", "crossref"],
  "limit": 5
}
```

#### Fetch Paper
```bash
POST /api/v1/fetch
Content-Type: application/json

{
  "identifier": "10.1038/nature12373",
  "source": "crossref"
}
```

#### Parse Identifiers
```bash
POST /api/v1/parse
Content-Type: application/json

{
  "text": "Check out this paper: doi:10.1038/nature12373",
  "types": ["doi", "arxiv"],
  "format": "json"
}
```

#### AI Agent
```bash
POST /api/v1/agents/run
Content-Type: application/json

{
  "prompt": "Search for recent papers on graph neural networks"
}
```

## Architecture

### Core Components
- **Fetcher**: Central orchestration layer for multi-source paper retrieval with caching and rate limiting
- **Sources**: Modular data source implementations with unified interfaces
- **Agents**: AI-powered analysis agents with OpenAI and Ollama backends
- **Parsers**: Intelligent text processing for identifier extraction and metadata parsing
- **API**: FastAPI-based REST endpoints with automatic documentation
- **CLI**: Rich command-line interface with interactive features

### Data Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Request   │ -> │   Fetcher   │ -> │   Sources   │
│  (CLI/API)  │    │ (Orchestrate)│    │ (Retrieve) │
└─────────────┘    └─────────────┘    └─────────────┘
       ↑                  ↓                  ↓
       └─────────────┬────┘            ┌─────────────┐
                     └────────────────►│   Cache     │
                                      │  (Redis)    │
                                      └─────────────┘
```

## Data Sources

SciPaper integrates with multiple academic data sources:

### arXiv
- **API**: OAI-PMH protocol
- **Coverage**: Preprints in physics, mathematics, computer science, etc.
- **Features**: Search by title, author, abstract, category
- **Rate Limits**: 1 request/second for non-registered users

### Crossref
- **API**: REST API with JSON responses
- **Coverage**: 100M+ scholarly works from 50K+ publishers
- **Features**: DOI resolution, metadata retrieval, citation links
- **Rate Limits**: 50 requests/second with politeness delays

### PubMed
- **API**: E-utilities (Entrez)
- **Coverage**: Biomedical literature from Medline and PubMed Central
- **Features**: MeSH terms, author affiliations, publication types
- **Rate Limits**: 3 requests/second for non-registered users

### Semantic Scholar
- **API**: REST API with advanced features
- **Coverage**: Academic papers with AI-extracted insights
- **Features**: Citation analysis, influential citations, field-of-study classification
- **Rate Limits**: 100 requests/minute for free tier

### Local Xrxiv
- **Format**: JSONL dumps from xrxiv.org
- **Coverage**: Preprints from bioRxiv, medRxiv, arXiv
- **Features**: Full-text search, local processing, offline capability
- **Use Case**: Institutional repositories, offline analysis

## AI Integration

### OpenAI Agents SDK
```python
# Example agent usage
agent = PaperAgent()
result = await agent.analyze_papers(
    papers=papers,
    analysis_type="summary",
    context="Research on quantum chemistry"
)
```

### Ollama Integration
- **Local Processing**: Privacy-preserving AI analysis
- **Models**: Llama 3.2, Mistral, CodeLlama, etc.
- **Fallback Mechanism**: Automatic fallback to local models when OpenAI unavailable
- **Performance**: Optimized for local hardware with GPU acceleration

### Analysis Types
- **Summarization**: Key findings and contributions
- **Critical Analysis**: Methodology evaluation and limitations
- **Related Work**: Connection to existing literature
- **Future Directions**: Research gaps and opportunities

- **CLI**: Rich command-line interface built with Click and Rich

### Package Structure

```
src/scipaper/
├── api/                    # REST API endpoints
│   └── v1/
│       └── routers/       # Route handlers
├── agents/                 # AI agent implementations
├── core/                   # Business logic and models
├── sources/                # Data source implementations
│   └── implementations/   # Specific source classes
├── utils/                  # Utility functions
├── config.py              # Configuration management
├── exceptions.py          # Exception definitions
└── cli.py                 # Command-line interface
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/scipaper

# Run specific test categories
pytest tests/test_sources.py
pytest tests/test_api_endpoints.py
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Type checking
pyright src/ tests/

# Formatting
ruff format src/ tests/
```

### Pre-commit hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Troubleshooting

- OpenAI not configured: set `OPENAI_API_KEY` in `.env` or environment.
- Ollama connection errors: ensure `OLLAMA_HOST` and `OLLAMA_PORT` are reachable and the model is pulled.
- Crossref rate limits: respect API limits; set a descriptive `CROSSREF_USER_AGENT`.
- Port conflicts: change `FASTAPI_PORT` or stop conflicting services.

### Adding New Sources

1. Create a new source class inheriting from `BaseSource`
2. Implement the required methods (`search`, `fetch`)
3. Register the source in the `SourceRegistry`
4. Add tests for the new source

Example:
```python
from .base_source import BaseSource

class NewSource(BaseSource):
    name = "newsource"
    
    async def search(self, query: str, limit: int = 10, **kwargs):
        # Implementation here
        pass
    
    async def fetch(self, identifier: str, **kwargs):
        # Implementation here
        pass

# Register in registry.py
registry.register("newsource", NewSource)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

All contributions must pass lint, type checks, and tests. Commit authorship: Nik Jois <nikjois@llamasearch.ai>.

## Security

Report vulnerabilities privately to `nikjois@llamasearch.ai`. Please do not open public issues for security reports.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: nikjois@llamasearch.ai
- Issues: Use the GitHub issue tracker

## Acknowledgments

- OpenAI for the Agents SDK
- FastAPI for the web framework
- Click for the CLI framework
- Rich for terminal formatting
