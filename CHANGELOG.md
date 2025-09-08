## Changelog

### v1.1.2
- CI: run pytest directly and install test deps
- Docs: Quickstart, CLI/API usage, Docker instructions
- Version: expose `__version__` and sync app version

### v1.1.0
- Add web search integration (DuckDuckGo fallback, optional Tavily/SerpAPI)
- Add Codex agent using OpenAI + web search context
- Extend CLI with `search` and `codex` commands
- Extend FastAPI with `/search` and `/codex` endpoints
- README updates with logo, CLI/API reference, Docker

### v1.0.0
- Initial release with CLI, FastAPI, Agents, EMT demo simulation, analysis plots, reporting, CI, Docker
