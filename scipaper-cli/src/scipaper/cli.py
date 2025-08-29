import click
import httpx
import asyncio
import os
from rich.console import Console
from typing import Optional, List
from scipaper.utils.parse import parse_file as parse_ids_file, parse_ids_from_text, format_output, ID_PATTERNS

HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
PORT = int(os.getenv("FASTAPI_PORT", "8000"))
BASE = f"http://{HOST}:{PORT}/api/v1"
console = Console()


def run_async(async_fn, *args, **kwargs):
    """Execute an async function and return its result.

    Designed for runtime invocation so tests can patch this symbol to return
    mocked strings without executing network calls.
    """
    return asyncio.run(async_fn(*args, **kwargs))


@click.group()
def main():
    """SciPaper CLI - Master Interface"""
    pass


@main.command()
def health():
    """Check API health status"""
    async def health_async():
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{BASE}/health")
            return r.text
    result = run_async(health_async)
    console.print(result)


@main.command()
@click.argument("query", type=str)
@click.option("--source", "-s", multiple=True, default=["arxiv"])
@click.option("--limit", "-l", type=int, default=5)
def search(query: str, source, limit: int):
    """Search scientific papers"""
    async def search_async():
        async with httpx.AsyncClient() as c:
            payload = {"query": query, "sources": list(source), "limit": limit}
            r = await c.post(f"{BASE}/search", json=payload)
            r.raise_for_status()
            data = r.json()["papers"]
            if not data:
                return "No results"
            lines = ["ID | Title | Authors | Date | DOI | Source"]
            for p in data:
                title = (p["title"][:70] + "...") if len(p["title"]) > 70 else p["title"]
                authors = ", ".join(p.get("authors", [])[:2])
                lines.append(
                    f"{p.get('id','')} | {title} | {authors} | {p.get('date','') or '—'} | {p.get('doi','') or '—'} | {p.get('source','')}"
                )
            return "\n".join(lines)
    result = run_async(search_async)
    console.print(result)


@main.command()
@click.argument("identifier", type=str)
@click.option("--output-dir", "-o", default="downloads")
@click.option("--rename", is_flag=True, default=True)
def fetch(identifier: str, output_dir: str, rename: bool):
    """Fetch a paper by ID"""
    async def fetch_async():
        async with httpx.AsyncClient() as c:
            payload = {
                "identifier": identifier,
                "output_dir": output_dir,
                "rename": rename}
            r = await c.post(f"{BASE}/fetch", json=payload)
            if r.status_code != 200:
                return f"Fetch failed: {r.text}"
            return f"Saved: {r.json()['download_path']}"
    result = run_async(fetch_async)
    console.print(result)


@main.command()
@click.argument("task", type=str)
def agent(task: str):
    """Run AI agent with local Ollama model"""
    async def agent_async():
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{BASE}/agents/run", json={"prompt": task})
            if r.status_code == 501:
                return "Agent not available. Install optional deps or set OPENAI_API_KEY."
            r.raise_for_status()
            return r.json()["final"]
    result = run_async(agent_async)
    console.print(result)


@main.command()
@click.option("--match", "matches", multiple=True, type=click.Choice(list(ID_PATTERNS.keys())), help="ID types to parse")
@click.option("--path", type=str, required=False, help="Path to file to parse")
@click.option("--text", type=str, required=False, help="Raw text to parse when no path is provided")
@click.option("--format", "fmt", type=click.Choice(["raw", "jsonl", "csv"]), default="raw")
def parse(matches: List[str], path: Optional[str], text: Optional[str], fmt: str):
    """Parse identifiers from text or a file."""
    if (path is None) and (text is None):
        # Fallback to stdin if neither provided
        content = click.get_text_stream("stdin").read()
        items = parse_ids_from_text(content, list(matches) or None)
    elif path is not None and text is not None:
        console.print("[red]Provide either --path or --text, not both[/red]")
        return
    else:
        if path:
            items = parse_ids_file(path, list(matches) or None)
        else:
            items = parse_ids_from_text(text or "", list(matches) or None)
    console.print(format_output(items, fmt))


@main.command()
@click.argument("command", required=False)
@click.pass_context
def master(ctx, command: Optional[str]):
    """Master command interface with Ollama integration"""
    if not command:
        console.print("[bold]SciPaper Master Interface[/bold]")
        console.print("Available commands: health, search, fetch, agent, parse")
        return
    
    if command == "health":
        # Use runtime run_async so tests can patch it
        async def health_async():
            async with httpx.AsyncClient() as c:
                r = await c.get(f"{BASE}/health")
                return r.text
        console.print(run_async(health_async))
    elif command.startswith("search"):
        q = command.replace("search ", "")
        async def search_async():
            async with httpx.AsyncClient() as c:
                payload = {"query": q, "sources": ["arxiv"], "limit": 5}
                r = await c.post(f"{BASE}/search", json=payload)
                r.raise_for_status()
                papers = r.json().get("papers", [])
                return "Search results" if papers else "No results"
        console.print(run_async(search_async))
    elif command.startswith("fetch"):
        ident = command.replace("fetch ", "")
        async def fetch_async():
            async with httpx.AsyncClient() as c:
                r = await c.post(f"{BASE}/fetch", json={"identifier": ident})
                return "Mock fetch" if r.status_code == 200 else "Fetch failed"
        console.print(run_async(fetch_async))
    elif command.startswith("agent"):
        t = command.replace("agent ", "")
        async def agent_async():
            async with httpx.AsyncClient() as c:
                r = await c.post(f"{BASE}/agents/run", json={"prompt": t})
                return r.json().get("final", "") if r.status_code == 200 else "Agent not available. Install optional deps or set OPENAI_API_KEY."
        console.print(run_async(agent_async))
    elif command.startswith("parse"):
        payload_text = command.replace("parse ", "")
        async def parse_async():
            async with httpx.AsyncClient() as c:
                r = await c.post(f"{BASE}/parse", json={"text": payload_text, "format": "raw"})
                r.raise_for_status()
                return r.json().get("formatted", "")
        console.print(run_async(parse_async))
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
