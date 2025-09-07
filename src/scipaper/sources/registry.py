"""Source registry and factory for dynamic source selection."""

from typing import Optional

from .base_source import BaseSource
from .implementations.arxiv import ArxivSource
from .implementations.crossref import CrossrefSource
from .implementations.pubmed import PubMedSource
from .implementations.semanticscholar import SemanticScholarSource
from .implementations.xrxiv_local import XrxivLocalSource
class SourceRegistry:
    """Registry for managing and instantiating data sources."""

    def __init__(self):
        self._sources: dict[str, type[BaseSource]] = {}
        self._register_default_sources()

    def _register_default_sources(self):
        """Register all built-in source implementations."""
        self.register("arxiv", ArxivSource)
        self.register("crossref", CrossrefSource)
        self.register("pubmed", PubMedSource)
        self.register("semanticscholar", SemanticScholarSource)
        self.register("xrxiv", XrxivLocalSource)

    def register(self, name: str, source_class: type[BaseSource]):
        """Register a new source class."""
        self._sources[name] = source_class

    def get(self, name: str) -> Optional[type[BaseSource]]:
        """Get a source class by name."""
        return self._sources.get(name.lower())

    def create(self, name: str, **kwargs) -> Optional[BaseSource]:
        """Create a source instance by name."""
        source_class = self.get(name)
        if source_class:
            return source_class(**kwargs)
        return None

    def list_available(self) -> list[str]:
        """List all available source names."""
        return list(self._sources.keys())

    def is_available(self, name: str) -> bool:
        """Check if a source is available."""
        return name.lower() in self._sources


# Global registry instance
registry = SourceRegistry()


def get_source(name: str, **kwargs) -> Optional[BaseSource]:
    """Convenience function to get a source instance."""
    return registry.create(name, **kwargs)


def list_sources() -> list[str]:
    """Convenience function to list available sources."""
    return registry.list_available()


def register_source(name: str, source_class: type[BaseSource]):
    """Convenience function to register a new source."""
    registry.register(name, source_class)
