"""Data source implementations for various academic databases."""

from .base_source import BaseSource
from .implementations.arxiv import ArxivSource
from .implementations.crossref import CrossrefSource
from .implementations.xrxiv_local import XrxivLocalSource
from .registry import SourceRegistry, get_source, list_sources, register_source

__all__ = [
    "ArxivSource",
    "BaseSource",
    "CrossrefSource",
    "SourceRegistry",
    "XrxivLocalSource",
    "get_source",
    "list_sources",
    "register_source",
]
