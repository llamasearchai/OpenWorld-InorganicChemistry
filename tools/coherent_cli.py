from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Optional

import typer

app = typer.Typer(help="Coherent developer helpers: deps, build, test, cli")


def _run(cmd: list[str], cwd: Optional[str] = None) -> int:
    print("+", " ".join(cmd))
    return subprocess.call(cmd, cwd=cwd or os.getcwd())


@app.command()
def deps() -> None:
    """Install project dependencies using uv if available, else pip."""
    if shutil.which("uv"):
        _run(["uv", "venv"])
        if os.name == "posix":
            print("Activate with: source .venv/bin/activate")
        _run(["uv", "sync", "--all-extras"])
    else:
        print("uv not found; using pip")
        if not os.path.exists(".venv"):
            _run([sys.executable, "-m", "venv", ".venv"])
        activate = os.path.join(".venv", "bin", "activate")
        print(f"Activate with: source {activate}")
        _run([os.path.join(".venv", "bin", "python"), "-m", "pip", "install", "-e", ".[dev]"])


@app.command()
def build(docker: bool = typer.Option(False, help="Build docker image as well")) -> None:
    """Build wheel/sdist (and optionally Docker image)."""
    _run([sys.executable, "-m", "pip", "install", "--upgrade", "build"])
    _run([sys.executable, "-m", "build"])
    if docker:
        tag = "openinorganicchemistry:latest"
        _run(["docker", "build", "-t", tag, "."])


@app.command()
def test() -> None:
    """Run tox (pytests + linters)."""
    _run([sys.executable, "-m", "tox", "-q"])


@app.command()
def cli(cmd: str = typer.Option("oic --help", help="Run a CLI command")) -> None:
    """Quick runner for top-level CLI commands."""
    shell = os.environ.get("SHELL", "/bin/bash")
    _run([shell, "-lc", cmd])


if __name__ == "__main__":
    app()


