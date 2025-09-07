from __future__ import annotations

import shutil
import subprocess
from typing import Optional


def run_sgpt_if_available(prompt: Optional[str] = None, shell: bool = False) -> None:
    """Invoke shell-gpt (sgpt) if present on PATH."""
    if not shutil.which("sgpt"):
        print("shell-gpt (sgpt) not installed. Install via: pip install shell-gpt")
        return
    args = ["sgpt"]
    if shell:
        args.append("--shell")
    if prompt is None:
        prompt = input("sgpt prompt: ").strip()  # nosec B322
    args.append(prompt)
    print("+", " ".join(args))
    subprocess.call(args)


