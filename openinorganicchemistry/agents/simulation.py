from __future__ import annotations

import uuid
from typing import Literal

from ..core.dft_utils import quick_emt_energy
from ..core.storage import RunRecord, save_run


def run_simulation(
    formula: str | None = None,
    backend: Literal["emt", "ase", "external"] = "emt",
    supercell: int = 1,
) -> str:
    if formula is None:
        formula = input("Material formula (e.g., TiO2): ").strip()  # nosec B322
    if backend != "emt":
        print("Note: demo uses EMT backend; extend to ASE/DFT as installed.")
    energy = quick_emt_energy(formula, supercell=supercell)
    output = f"EMT potential energy for {formula} (supercell={supercell}): {energy:.6f} a.u."
    print("\n=== Simulation Result ===\n")
    print(output)
    run_id = str(uuid.uuid4())
    save_run(
        RunRecord(
            id=run_id,
            kind="simulation",
            input=formula,
            output=output,
            meta={"backend": backend, "supercell": supercell},
        )
    )
    print(f"\n[run_id] {run_id}")
    return run_id


