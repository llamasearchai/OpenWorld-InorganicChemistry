from fastapi import APIRouter
from pydantic import BaseModel

from scipaper_cli.core.fetcher import Fetcher
from scipaper_cli.utils.ids import classify_identifier

router = APIRouter()
