"""Command-line interface for SciPaper."""

import asyncio
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger

from scipaper_cli.config import settings, is_openai_available, is_ollama_available
from scipaper_cli.core.fetcher import Fetcher
from scipaper_cli.agents.paper_agents import PaperAgent
from scipaper_cli.utils.parse import parse_text
from scipaper_cli.exceptions import FetcherError, SourceError, AgentError, ParseError

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def main():
    """SciPaper: A comprehensive scientific paper management and analysis tool."""
    pass


@main.command()
def health():
    """Check the health of the SciPaper system."""
    try:
        console.print(Panel.fit(
            "[bold green]SciPaper System Health Check[/bold green]\n"
            f"Version: 1.0.0\n"
            f"OpenAI API: {'[green]Available[/green]' if is_openai_available() else '[red]Not Configured[/red]'}\n"
            f"Ollama: {'[green]Available[/green]' if is_ollama_available() else '[red]Not Configured[/red]'}\n"
            f"Downloads Directory: {settings.downloads_dir}\n"
            f"Log Level: {settings.log_level}",
            title="System Status"
        ))
    except Exception as e:
        console.print(f"[red]Health check failed: {e}[/red]")
        raise click.ClickException(str(e))


@main.command()
@click.argument("query")
@click.option("--sources", "-s", help="Comma-separated list of sources to search")
@click.option("--limit", "-l", default=5, help="Maximum number of results")
@click.option("--format", "-f", default="table", type=click.Choice(["table", "json", "csv"]))
def search(query: str, sources: str, limit: int, format: str):
    """Search for papers across multiple sources."""
    try:
        source_list = sources.split(",") if sources else None

        async def run_search():
            fetcher = Fetcher()
            results = await fetcher.search(query, source_list, limit)

            if not results:
                console.print("[yellow]No results found.[/yellow]")
                return

            if format == "json":
                import json
                console.print(json.dumps(results, indent=2))
            elif format == "csv":
                import csv
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
                console.print(output.getvalue())
            else:  # table format
                table = Table(title=f"Search Results for: {query}")
                table.add_column("Title", style="cyan", max_width=60)
                table.add_column("Authors", style="green", max_width=40)
                table.add_column("Date", style="yellow")
                table.add_column("Source", style="blue")
                table.add_column("DOI", style="magenta", max_width=25)

                for paper in results:
                    table.add_row(
                        paper.get("title", ""),
                        ", ".join(paper.get("authors", [])),
                        str(paper.get("date", "")),
                        paper.get("source", ""),
                        paper.get("doi", "")
                    )
                console.print(table)

        asyncio.run(run_search())

    except Exception as e:
        console.print(f"[red]Search failed: {e}[/red]")
        raise click.ClickException(str(e))


@main.command()
@click.argument("identifier")
@click.option("--source", "-s", help="Specific source to use")
@click.option("--format", "-f", default="table", type=click.Choice(["table", "json", "csv"]))
def fetch(identifier: str, source: str, format: str):
    """Fetch a specific paper by identifier (DOI, arXiv ID, etc.)."""
    try:
        async def run_fetch():
            fetcher = Fetcher()
            result = await fetcher.fetch(identifier, source)
            # Similar formatting logic as search...

        asyncio.run(run_fetch())

    except Exception as e:
        console.print(f"[red]Fetch failed: {e}[/red]")
        raise click.ClickException(str(e))


@main.command()
@click.argument("text")
@click.option("--types", "-t", help="Comma-separated list of identifier types to look for")
@click.option("--format", "-f", default="table", type=click.Choice(["table", "json", "csv"]))
def parse(text: str, types: str, format: str):
    """Parse text to extract identifiers (DOIs, arXiv IDs, etc.)."""
    try:
        type_list = types.split(",") if types else None
        results = parse_text(text, type_list)
        # Similar formatting logic as search...

    except Exception as e:
        console.print(f"[red]Parse failed: {e}[/red]")
        raise click.ClickException(str(e))


@main.command()
@click.argument("prompt")
@click.option("--sources", "-s", help="Comma-separated list of sources to search")
@click.option("--limit", "-l", default=3, help="Maximum number of papers to analyze")
def agent(prompt: str, sources: str, limit: int):
    """Use AI agent to analyze papers and provide insights."""
    try:
        source_list = sources.split(",") if sources else None
        
        async def run_agent():
            agent_instance = PaperAgent()
            result = await agent_instance.search_and_analyze(prompt, source_list, limit)
            # Formatting logic here...

        asyncio.run(run_agent())
        
    except Exception as e:
        console.print(f"[red]Agent execution failed: {e}[/red]")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
