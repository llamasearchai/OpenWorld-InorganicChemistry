import re

ARXIV_NEW = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
ARXIV_OLD = re.compile(r"^[a-z-]+(\.[A-Z]{2})?/\d{7}(v\d+)?$", re.I)
DOI_RX = re.compile(r"^10.\d{4,9}/\S+$", re.I)


def classify_identifier(s: str) -> str:
    s = (s or "").strip()
    if s.startswith(("http://", "https://")):
        return "url"
    if ARXIV_NEW.match(s) or ARXIV_OLD.match(s):
        return "arxiv"
    if DOI_RX.match(s):
        return "doi"
    return "unknown"
