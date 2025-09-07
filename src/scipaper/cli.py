"""Command-line interface for SciPaper."""
import asyncio
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger

from .agents.paper_agents import PaperAgent
from .config import is_ollama_available, is_openai_available, settings
from .core.fetcher import Fetcher
from .exceptions import FetcherError, SourceError, AgentError, ParseError
from .utils.parse import parse_text

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def main():
    """SciPaper: A comprehensive scientific paper management and analysis tool."""
    pass

@main.command()
def health():
    """Check the health of the SciPaper system."""
    logger_ctx = logger.bind(command="health")
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
        logger_ctx.info("Health check completed successfully")
    except Exception as e:
        logger_ctx.error(f"Health check failed: {e}")
        console.print(f"[red]Health check failed: {e}[/red]")
        raise click.ClickException(str(e))

@main.command()
@click.argument("query")
@click.option("--sources", "-s", help="Comma-separated list of sources to search")
@click.option("--limit", "-l", default=5, help="Maximum number of results")
@click.option("--format", "-f", default="table", type=click.Choice(["table", "json", "csv"]))
@click.option("--interactive", is_flag=True, help="Enable interactive mode")
def search(query: str, sources: str, limit: int, format: str, interactive: bool):
    """Search for papers across multiple sources."""
    logger_ctx = logger.bind(command="search", query=query, sources=sources, limit=limit, format=format)
    if interactive:
        if not click.confirm(f"Run search for '{query}' with {limit} results?"):
            logger_ctx.info("Search cancelled by user")
            return
    try:
        source_list = sources.split(",") if sources else None

        async def run_search():
            fetcher = Fetcher()
            results = await fetcher.search(query, source_list, limit)

            if format == "json":
                import json
                console.print(json.dumps(results, indent=2))
            elif format == "csv":
                import csv
                import io
                output = io.StringIO()
                if results:
                    writer = csv.DictWriter(output, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
                console.print(output.getvalue())
            elif results:
                table = Table(title=f"Search Results for: {query}")
                table.add_column("Title", style="cyan")
                table.add_column("Authors", style="green")
                table.add_column("Date", style="yellow")
                table.add_column("Source", style="blue")
                table.add_column("DOI", style="magenta")

                for paper in results:
                    table.add_row(
                        paper.get("title", "Unknown")[:60] + "..." if len(paper.get("title", "")) > 60 else paper.get("title", "Unknown"),
                        ", ".join(paper.get("authors", ["Unknown"]))[:40] + "..." if len(", ".join(paper.get("authors", ["Unknown"]))) > 40 else ", ".join(paper.get("authors", ["Unknown"])),
                        str(paper.get("date", "Unknown")),
                        paper.get("source", "Unknown"),
                        paper.get("doi", "Unknown")[:20] + "..." if len(paper.get("doi", "")) > 20 else paper.get("doi", "Unknown")
                    )
                console.print(table)
            else:
                console.print("[yellow]No results found.[/yellow]")

        asyncio.run(run_search())
        logger_ctx.info("Search command completed successfully")

    except FetcherError as e:
        logger_ctx.error(f"Fetcher error in search: {e}", details=e.details)
        console.print(f"[red]Search failed due to fetcher error: {e.message}[/red]")
        raise click.ClickException(str(e))
    except Exception as e:
        logger_ctx.error(f"Search failed: {e}")
        console.print(f"[red]Search failed: {e}[/red]")
        raise click.ClickException(str(e))

@main.command()
@click.argument("identifier")
@click.option("--source", "-s", help="Specific source to use")
@click.option("--format", "-f", default="table", type=click.Choice(["table", "json", "csv"]))
@click.option("--interactive", is_flag=True, help="Enable interactive mode")
def fetch(identifier: str, source: str, format: str, interactive: bool):
    """Fetch a specific paper by identifier (DOI, arXiv ID, etc.)."""
    logger_ctx = logger.bind(command="fetch", identifier=identifier, source=source, format=format)
    if interactive:
        if not click.confirm(f"Fetch paper '{identifier}' from {source or 'auto'}?"):
            logger_ctx.info("Fetch cancelled by user")
            return
    try:
        async def run_fetch():
            fetcher = Fetcher()
            result = await fetcher.fetch(identifier, source)

            if result:
                if format == "json":
                    import json
                    console.print(json.dumps(result, indent=2))
                elif format == "csv":
                    import csv
                    import io
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=result.keys())
                    writer.writeheader()
                    writer.writerow(result)
                    console.print(output.getvalue())
                else:  # table format
                    table = Table(title=f"Paper Details: {identifier}")
                    table.add_column("Field", style="cyan")
                    table.add_column("Value", style="green")

                    for key, value in result.items():
                        if isinstance(value, list):
                            value_str = ", ".join(str(v) for v in value)
                        else:
                            value_str = str(value)

                        # Truncate long values for display
                        if len(value_str) > 80:
                            value_str = value_str[:77] + "..."

                        table.add_row(key.title(), value_str)

                    console.print(table)
            else:
                console.print(f"[yellow]No paper found with identifier: {identifier}[/yellow]")

        asyncio.run(run_fetch())
        logger_ctx.info("Fetch command completed successfully")

    except FetcherError as e:
        logger_ctx.error(f"Fetcher error in fetch: {e}", details=e.details)
        console.print(f"[red]Fetch failed due to fetcher error: {e.message}[/red]")
        raise click.ClickException(str(e))
    except Exception as e:
        logger_ctx.error(f"Fetch failed: {e}")
        console.print(f"[red]Fetch failed: {e}[/red]")
        raise click.ClickException(str(e))

@main.command()
@click.argument("text")
@click.option("--types", "-t", help="Comma-separated list of identifier types to look for")
@click.option("--format", "-f", default="table", type=click.Choice(["table", "json", "csv"]))
@click.option("--interactive", is_flag=True, help="Enable interactive mode")
def parse(text: str, types: str, format: str, interactive: bool):
    """Parse text to extract identifiers (DOIs, arXiv IDs, etc.)."""
    logger_ctx = logger.bind(command="parse", text_length=len(text), types=types, format=format)
    if interactive:
        if not click.confirm(f"Parse text with length {len(text)}?"):
            logger_ctx.info("Parse cancelled by user")
            return
    try:
        type_list = types.split(",") if types else None
        results = parse_text(text, type_list)

        if format == "json":
            import json
            console.print(json.dumps(results, indent=2))
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            if results:
                writer = csv.DictWriter(output, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            console.print(output.getvalue())
        elif results:
            table = Table(title="Parsed Identifiers")
            table.add_column("Type", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Position", style="yellow")

            for item in results:
                table.add_row(
                    item.get("type", "Unknown"),
                    item.get("value", "Unknown"),
                    str(item.get("position", "Unknown"))
                )
            console.print(table)
        else:
            console.print("[yellow]No identifiers found in the text.[/yellow]")

        logger_ctx.info(f"Parse completed: {len(results)} identifiers found")
    except ParseError as e:
        logger_ctx.error(f"Parse error: {e}", details=e.details)
        console.print(f"[red]Parse failed due to parse error: {e.message}[/red]")
        raise click.ClickException(str(e))
    except Exception as e:
        logger_ctx.error(f"Parse failed: {e}")
        console.print(f"[red]Parse failed: {e}[/red]")
        raise click.ClickException(str(e))

@main.command()
@click.argument("prompt")
@click.option("--sources", "-s", help="Comma-separated list of sources to search")
@click.option("--limit", "-l", default=3, help="Maximum number of papers to analyze")
@click.option("--interactive", is_flag=True, help="Enable interactive mode")
def agent(prompt: str, sources: str, limit: int, interactive: bool):
    """Use AI agent to analyze papers and provide insights."""
    logger_ctx = logger.bind(command="agent", prompt=prompt[:50] + "..." if len(prompt) > 50 else prompt, sources=sources, limit=limit)
    if interactive:
        if not click.confirm(f"Run agent analysis for prompt '{prompt[:50]}...' with {limit} papers?"):
            logger_ctx.info("Agent analysis cancelled by user")
            return
    try:
        source_list = sources.split(",") if sources else None

        async def run_agent():
            agent_instance = PaperAgent()
            result = await agent_instance.search_and_analyze(prompt, source_list, limit)

            if result.get("papers"):
                console.print(Panel.fit(
                    f"[bold]AI Analysis Results[/bold]\n\n"
                    f"[cyan]Query:[/cyan] {result.get('query', 'Unknown')}\n"
                    f"[cyan]Sources:[/cyan] {', '.join(result.get('sources', []))}\n"
                    f"[cyan]Papers Found:[/cyan] {len(result.get('papers', []))}\n\n"
                    f"[bold green]Analysis:[/bold green]\n{result.get('analysis', 'No analysis available')}",
                    title="Agent Response"
                ))
            else:
                console.print("[yellow]No papers found for analysis.[/yellow]")

        asyncio.run(run_agent())
        logger_ctx.info("Agent command completed successfully")

    except AgentError as e:
        logger_ctx.error(f"Agent error: {e}", details=e.details)
        console.print(f"[red]Agent execution failed due to agent error: {e.message}[/red]")
        raise click.ClickException(str(e))
    except Exception as e:
        logger_ctx.error(f"Agent execution failed: {e}")
        console.print(f"[red]Agent execution failed: {e}[/red]")
        raise click.ClickException(str(e))

@main.command()
@click.argument("command", required=False)
@click.pass_context
def master(ctx, command: Optional[str]):
    """Master command interface with Ollama integration"""
    logger_ctx = logger.bind(command="master", subcommand=command)
    try:
        if not command:
            console.print("[bold]SciPaper Master Interface[/bold]")
            console.print("Available commands: health, search, fetch, agent, parse")
            logger_ctx.info("Master command displayed help")
            return  # Exit code 0

        if command == "health":
            ctx.invoke(health)
        elif command == "search":
            console.print("[yellow]Use: scipaper search <query> [options][/yellow]")
        elif command == "fetch":
            console.print("[yellow]Use: scipaper fetch <identifier> [options][/yellow]")
        elif command == "agent":
            console.print("[yellow]Use: scipaper agent <prompt> [options][/yellow]")
        elif command == "parse":
            console.print("[yellow]Use: scipaper parse <text> [options][/yellow]")
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            logger_ctx.warning(f"Unknown subcommand: {command}")
            ctx.exit(1)  # Exit with 1 for unknown command
        logger_ctx.info(f"Master command executed: {command}")

    except Exception as e:
        logger_ctx.error(f"Master command failed: {e}")
        console.print(f"[red]Master command failed: {e}[/red]")
        ctx.exit(1)


if __name__ == "__main__":
    main()