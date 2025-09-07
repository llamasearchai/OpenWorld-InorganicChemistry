from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from scipaper_cli.utils.parse import parse_file, parse_ids_from_text, format_output, ID_PATTERNS

router = APIRouter()
