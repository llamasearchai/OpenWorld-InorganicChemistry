from __future__ import annotations

import asyncio
import os
from typing import Optional, Dict, Callable, Tuple, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .agents.orchestration import run_workflow
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
	actions: Dict[str, Tuple[str, Callable[..., Any]]] = {
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
	
	# Use the new comprehensive validation system
	from .core.validation import SystemValidator
	
	validator = SystemValidator()
	results = validator.run_all_checks()
	
	# Create enhanced table with validation results
	table = Table(title="System Validation Report")
	table.add_column("Check", style="bold", width=25)
	table.add_column("Status", width=10)
	table.add_column("Details", style="dim")
	
	for name, result in results.items():
		status_style = {
			"pass": "green",
			"warn": "yellow",
			"fail": "red"
		}.get(result.status, "white")
		
		status_icon = {
			"pass": "✅",
			"warn": "⚠️ ",
			"fail": "❌"
		}.get(result.status, "❓")
		
		table.add_row(
			name,
			f"[{status_style}]{status_icon}[/{status_style}]",
			result.message
		)
		
		if result.details:
			table.add_row("", "", f"[dim]→ {result.details}[/dim]")
	
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
def export_data(
    format: str = typer.Option("json", help="Export format: json, csv, sqlite"),
    output: str = typer.Option("export", help="Output file/directory path"),
    experiment: Optional[str] = typer.Option(None, help="Specific experiment to export")
) -> None:
    """Export experimental data in various formats."""
    from .core.data_formats import DataExporter
    
    console.print(f"[bold]Exporting data in {format} format...[/bold]")
    
    # Mock experimental data for demonstration
    sample_data = {
        "materials": [
            {"formula": "TiO2", "band_gap": 3.2, "synthesis_temp": 450},
            {"formula": "ZnO", "band_gap": 3.37, "synthesis_temp": 380},
            {"formula": "Al2O3", "band_gap": 8.8, "synthesis_temp": 1200}
        ],
        "experiments": [
            {"id": 1, "date": "2024-01-15", "success": True},
            {"id": 2, "date": "2024-01-16", "success": False}
        ]
    }
    
    try:
        if format == "json":
            DataExporter.to_json(sample_data, f"{output}.json")
        elif format == "csv":
            # Export each table as separate CSV
            for table_name, data in sample_data.items():
                if isinstance(data, list) and data:
                    DataExporter.to_csv(data, f"{output}_{table_name}.csv")
        elif format == "sqlite":
            DataExporter.to_sqlite(sample_data, f"{output}.db")
        else:
            console.print(f"[red]Unsupported format: {format}[/red]")
            return
        
        console.print(f"[green]✅ Data exported successfully to {output}[/green]")
    
    except Exception as e:
        console.print(f"[red]❌ Export failed: {e}[/red]")


@app.command()
def archive_experiment(
    name: str = typer.Argument(help="Experiment name"),
    description: Optional[str] = typer.Option(None, help="Experiment description")
) -> None:
    """Archive a complete experiment with all data and metadata."""
    from .core.data_formats import ExperimentArchiver
    
    console.print(f"[bold]Archiving experiment: {name}[/bold]")
    
    # Mock experimental data and metadata
    data = {
        "results": [
            {"material": "TiO2", "property": "band_gap", "value": 3.2},
            {"material": "ZnO", "property": "band_gap", "value": 3.37}
        ],
        "conditions": [
            {"temperature": 450, "pressure": 1.0, "duration": 24}
        ]
    }
    
    metadata = {
        "description": description or f"Archived experiment: {name}",
        "user": os.environ.get("USER", "unknown"),
        "git_commit": os.popen("git rev-parse HEAD 2>/dev/null").read().strip() or "unknown"
    }
    
    try:
        archiver = ExperimentArchiver()
        archive_path = archiver.archive_experiment(name, data, metadata)
        console.print(f"[green]✅ Experiment archived to: {archive_path}[/green]")
    
    except Exception as e:
        console.print(f"[red]❌ Archive failed: {e}[/red]")


@app.command()
def list_experiments() -> None:
    """List all archived experiments."""
    from .core.data_formats import ExperimentArchiver
    
    try:
        archiver = ExperimentArchiver()
        experiments = archiver.list_experiments()
        
        if not experiments:
            console.print("[yellow]No archived experiments found[/yellow]")
            return
        
        table = Table(title="Archived Experiments")
        table.add_column("Name", style="bold")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Path", style="dim")
        
        for exp in experiments:
            table.add_row(exp["name"], exp["timestamp"], exp["path"])
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]❌ Failed to list experiments: {e}[/red]")


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

