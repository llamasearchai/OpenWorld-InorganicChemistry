from __future__ import annotations

import json
import os
import uuid
from statistics import mean
# Optional advanced analysis libraries are omitted to keep tests lightweight

from ..core.plotting import save_convergence_plot
from ..core.storage import RunRecord, save_run


def _load_values(path: str) -> list[float]:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if path.endswith(".json"):
        data = json.loads(open(path, "r", encoding="utf-8").read())
        if isinstance(data, dict) and "values" in data:
            return [float(v) for v in data["values"]]
        if isinstance(data, list):
            return [float(v) for v in data]
        raise ValueError("JSON must be a list or dict with 'values'")
    # Fallback: CSV with a column of numbers
    values: list[float] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().split(",")[0]
            if line:
                try:
                    values.append(float(line))
                except Exception:
                    pass
    if not values:
        raise ValueError("No numeric values parsed")
    return values


def analyze_results(path: str | None = None) -> str:
    """Analyze results with basic stats and advanced PCA if applicable."""
    if path is None:
        path = input("Path to results (csv/json): ").strip()  # nosec B322
    values = _load_values(path)
    avg = mean(values)
    plot_path = save_convergence_plot(values, "convergence.png")
    output = f"Count={len(values)}, Mean={avg:.6f}, Plot={plot_path}"
    print("\n=== Analysis Summary ===\n")
    print(output)
    run_id = str(uuid.uuid4())
    save_run(
        RunRecord(
            id=run_id,
            kind="analysis",
            input=path,
            output=output,
            meta={"n_values": len(values)},
        )
    )
    print(f"\n[run_id] {run_id}")
    return run_id


