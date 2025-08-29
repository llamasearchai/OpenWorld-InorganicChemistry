from typing import Optional, Dict, Any, List
from pathlib import Path
from loguru import logger
import httpx
from scipaper.utils.ids import classify_identifier
from scipaper.utils.parse import find_pdf_url


class Fetcher:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client


    async def _attempt(self, url: str, path: Path) -> bool:
        try:
            async with self.client.stream("GET", url, follow_redirects=True, timeout=60) as r:
                r.raise_for_status()
                ctype = r.headers.get("content-type", "").lower()
                if "pdf" not in ctype and not url.endswith(".pdf"):
                    # Try to parse HTML to discover embedded PDF URL
                    text = await r.aread()
                    try:
                        html = text.decode("utf-8", errors="ignore")
                    except Exception:
                        html = ""
                    candidate = find_pdf_url(html)
                    if candidate and candidate != url:
                        return await self._attempt(candidate, path)
                    return False
                path.parent.mkdir(parents=True, exist_ok=True)
                tmp = path.with_suffix(".pdf.tmp")
                with open(tmp, "wb") as f:
                    async for chunk in r.aiter_bytes():
                        f.write(chunk)
                tmp.rename(path)
                return True
        except Exception as e:
            logger.warning(f"download failed from {url}: {e}")
            return False


    async def fetch(self,
                    meta: Dict[str,
                               Any],
                    out_dir: Path,
                    rename: bool = True) -> Optional[Path]:
        title = meta.get("title") or meta.get("id") or meta.get("doi") or "paper"
        safe = "".join(
            ch if ch.isalnum() or ch in (
                " ",
                "-",
                "_") else "_" for ch in title).strip().replace(
            " ",
            "_")
        dest = out_dir / f"{safe}.pdf"

        urls: List[str] = []
        kind = classify_identifier(meta.get("id", ""))
        if kind == "arxiv" and meta.get("id"):
            urls.append(f"https://arxiv.org/pdf/{meta['id']}.pdf")
        if meta.get("url"):
            urls.append(meta["url"])
        doi = meta.get("doi")
        if doi and doi.startswith("10."):
            # try common DOI resolution endpoints which sometimes reveal PDFs
            urls.append(f"https://doi.org/{doi}")
            urls.append(f"https://dx.doi.org/{doi}")

        for u in urls:
            if await self._attempt(u, dest):
                logger.success(f"saved {dest}")
                return dest
        return None
