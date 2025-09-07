"""Paper export utilities."""
import csv
import io
from typing import List, Dict, Any, Union

from fpdf import FPDF


def export_papers(papers: List[Dict[str, Any]], format: str) -> Union[str, bytes]:
    """Export papers to different formats."""
    if format == "bibtex":
        bibtex = ""
        for paper in papers:
            bibtex += f"""@article{{{paper.get('id', 'unknown')},
  title = {{{paper.get('title', 'Unknown')}}},
  author = {{{', '.join(paper.get('authors', []))}}},
  journal = {{{paper.get('journal', 'Unknown')}}},
  year = {{{paper.get('date', 'Unknown')}}},
  doi = {{{paper.get('doi', 'Unknown')}}},
}}
"""
        return bibtex
    elif format == "csv":
        output = io.StringIO()
        if papers:
            writer = csv.DictWriter(output, fieldnames=papers[0].keys())
            writer.writeheader()
            writer.writerows(papers)
        return output.getvalue()
    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for paper in papers:
            pdf.cell(200, 10, txt=paper.get('title', 'Unknown'), ln=1)
            pdf.cell(200, 10, txt=f"Authors: {', '.join(paper.get('authors', []))}", ln=1)
            pdf.cell(200, 10, txt=f"Date: {paper.get('date', 'Unknown')}", ln=1)
            pdf.cell(200, 10, txt=f"Source: {paper.get('source', 'Unknown')}", ln=1)
            pdf.cell(200, 10, txt=f"DOI: {paper.get('doi', 'Unknown')}", ln=1)
            pdf.ln(10)
        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer.read()
    raise ValueError(f"Unsupported format: {format}")