from __future__ import annotations

import asyncio
import os
import shutil
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core.settings import Settings
from .agents.orchestration import run_workflow, list_agents
from .agents.literature import literature_query
from .agents.synthesis import propose_synthesis
from .agents.simulation import run_simulation
from .agents.analysis import analyze_results
from .agents.reporting import generate_report
from .integrations.sgpt import run_sgpt_if_available
from .integrations.websearch import web_search
from .agents.codex import codex_answer

app = typer.Typer(add_completion=False, help="OpenInorganicChemistry CLI")
console = Console()


def _banner() -> None:
	console.print(
		Panel.fit(
			"[bold]OpenInorganicChemistry[/bold]\nAI-Enhanced Solar Research Platform\n",
			border_style="cyan",
		)
	)


@app.command()
def menu() -> None:
	"""Interactive menu for day-to-day work."""
	_banner()
	actions = {
		"1": ("Literature Review", literature_query),
		"2": ("Propose Synthesis Pathways", propose_synthesis),
		"3": ("Run Simulation", run_simulation),
		"4": ("Analyze Results", analyze_results),
		"5": ("Generate Report", generate_report),
		"6": ("Run Agents Orchestration", lambda: asyncio.run(run_workflow(None))),
		"7": ("Shell-GPT (if installed)", run_sgpt_if_available),
		"8": ("Doctor (env check)", doctor),
		"9": ("Exit", lambda: None),
	}
	while True:
		table = Table(show_header=True, header_style="bold")
		table.add_column("Option", style="cyan", width=6)
		table.add_column("Action", style="white")
		for k, v in actions.items():
			table.add_row(k, v[0])
		console.print(table)
		choice = typer.prompt("Enter choice").strip()
		if choice == "9":
			break
		action = actions.get(choice)
		if action:
			try:
				action[1]()
			except Exception as e:  # pragma: no cover - interactive path
				console.print(f"[red]Error:[/red] {e}")
		else:
			console.print("[red]Invalid option[/red]")


@app.command()
def doctor() -> None:
	"""Check environment, versions, paths, and key setup."""
	_banner()
	s = Settings.load()
	rows = [
		("Python", os.popen("python --version").read().strip()),
		("OpenAI key present", "yes" if s.openai_api_key_masked else "no"),
		("Default LLM (general)", s.model_general),
		("Default LLM (fast)", s.model_fast),
		("sgpt available", "yes" if shutil.which("sgpt") else "no"),
	]
	table = Table(title="Environment")
	table.add_column("Item", style="bold")
	table.add_column("Value")
	for k, v in rows:
		table.add_row(k, v)
	console.print(table)


@app.command()
def agents(input_text: Optional[str] = typer.Option(None, help="Optional prompt to route via agents")) -> None:
	"""Run the multi-agent orchestration flow."""
	asyncio.run(run_workflow(input_text))


@app.command()
def literature(topic: str = typer.Argument(..., help="Topic to review, e.g., perovskite stability")) -> None:
	literature_query(topic)


@app.command()
def synth(target: str = typer.Argument(..., help="Target material formula, e.g., CH3NH3PbI3")) -> None:
	propose_synthesis(target)


@app.command()
def simulate(
	formula: str = typer.Argument(..., help="Material formula, e.g., TiO2"),
	backend: str = typer.Option("emt", help="Backend: emt|ase|external"),
	supercell: int = typer.Option(1, help="Supercell size (int)"),
) -> None:
	run_simulation(formula, backend=backend, supercell=supercell)


@app.command()
def analyze(path: str = typer.Argument(..., help="Path to results (csv/json)")) -> None:
	analyze_results(path)


@app.command()
def report(run_id: str = typer.Argument(..., help="Run identifier to compile report for")) -> None:
	generate_report(run_id)


@app.command()
def sgpt(
	prompt: str = typer.Argument(..., help="Prompt to send to shell-gpt"),
	shell: bool = typer.Option(False, "--shell", "-s", help="Use sgpt in shell mode"),
) -> None:
	run_sgpt_if_available(prompt=prompt, shell=shell)


@app.command()
def search(
	query: str = typer.Argument(..., help="Search query"),
	provider: str = typer.Option("auto", help="auto|tavily|serpapi|duckduckgo"),
	max_results: int = typer.Option(5, help="Max results"),
) -> None:
	results = web_search(query, provider=provider, max_results=max_results)
	table = Table(show_header=True, header_style="bold")
	table.add_column("Title")
	table.add_column("URL")
	table.add_column("Snippet")
	for r in results:
		trunc = r.snippet[:120] + ("..." if len(r.snippet) > 120 else "")
		table.add_row(r.title, r.url, trunc)
	console.print(table)


@app.command()
def codex(
	question: str = typer.Argument(..., help="Question to answer"),
	provider: str = typer.Option("auto", help="Search provider"),
	max_results: int = typer.Option(5, help="Max results"),
) -> None:
	codex_answer(question, provider=provider, max_results=max_results)


def main() -> None:
	# Default command is menu
	menu()


if __name__ == "__main__":
	import sys
	# If any CLI args provided, run Typer app (so `-m ... --help` works in tests)
	if len(sys.argv) > 1:
		app()
	else:
		main()

