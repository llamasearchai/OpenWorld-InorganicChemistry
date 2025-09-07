"""Full-text parsing and citation extraction."""
from typing import List, Dict, Any

import re
from loguru import logger

def parse_full_text(text: str) -> Dict[str, Any]:
    """Parse full text to extract citations and key sections."""
    citations = re.findall(r'(?:\[|\(|\{)([A-Z][a-z]+ et al\., \d{4}| \d{4}| \d{4a}\)| \d{4b}\))', text)
    sections = re.split(r'(Abstract|Introduction|Methods|Results|Discussion|Conclusion)', text)
    
    parsed = {
        "citations": citations,
        "sections": dict(zip(sections[1::2], sections[2::2])),
        "word_count": len(text.split()),
        "sentence_count": len(re.split(r'[.!?]', text))
    }
    logger.info(f"Parsed {len(citations)} citations and {len(parsed['sections'])} sections")
    return parsed

def extract_citations(text: str) -> List[str]:
    """Extract citations from text."""
    citations = re.findall(r'(\[?\d+\]?|\([A-Z][a-z]+ et al\., \d{4}\))', text)
    return list(set(citations))