import asyncio
from typing import Dict, Any, List

import httpx
from scipaper_cli.utils.ids import classify_identifier
from scipaper_cli.utils.parse import find_pdf_url
from bs4 import BeautifulSoup
