from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from scipaper_cli.sources.arxiv import ArxivSource
from scipaper_cli.sources.crossref import CrossrefSource
from scipaper_cli.sources.semanticscholar import SemanticScholarSource
from scipaper_cli.sources.pubmed import PubMedSource
from scipaper_cli.sources.xrxiv_local import XrxivLocalSource

router = APIRouter()
