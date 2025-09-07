from __future__ import annotations

import matplotlib

# Use non-interactive backend for headless environments (tests/CI)
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def save_convergence_plot(values: list[float], path: str = "convergence.png") -> str:
    plt.figure()
    plt.plot(list(range(1, len(values) + 1)), values, marker="o")
    plt.xlabel("Step")
    plt.ylabel("Energy (a.u.)")
    plt.title("Convergence")
    plt.tight_layout()
    plt.savefig(path)
    return path


