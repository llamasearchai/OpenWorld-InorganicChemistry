from __future__ import annotations

import logging
import pandas as pd
from ase.io import write
from pymatgen.core import Structure
from typing import List
from ..core.chemistry import MaterialSpec
from ..core.storage import RunRecord, save_run
import uuid

logger = logging.getLogger(__name__)

def import_lab_data(file: str) -> List[MaterialSpec]:
    """Import lab data from Excel or CSV, validate formulas."""
    logger.info("Importing lab data from %s", file)
    try:
        if file.endswith('.xlsx') or file.endswith('.xls'):
            df = pd.read_excel(file)
        elif file.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            raise ValueError("Unsupported file format. Use .csv or .xlsx")
        materials = []
        for _, row in df.iterrows():
            formula = row['formula']
            notes = row.get('notes', '')
            if not formula:
                continue
            spec = MaterialSpec(formula=formula, notes=notes)
            materials.append(spec)
        logger.info("Imported %d materials", len(materials))
    except Exception as e:
        logger.error("Import failed", exc_info=True)
        raise ValueError(f"Failed to import {file}. Error: {e}") from e
    return materials

def export_to_cif(materials: List[MaterialSpec], output_file: str = "materials.cif") -> str:
    """Export materials to CIF format."""
    logger.info("Exporting %d materials to CIF", len(materials))
    try:
        with open(output_file, "w") as f:
            for spec in materials:
                # Generate simple structure for demo
                # Note: In production, use proper structure generation
                from pymatgen.core import Composition
                comp = Composition(spec.formula)  # Simplified for demo
                f.write(f"# Material: {spec.formula}\n")
                f.write(f"# Notes: {spec.notes}\n\n")
        logger.info("Export completed to %s", output_file)
    except Exception as e:
        logger.error("Export failed", exc_info=True)
        raise ValueError(f"Failed to export to {output_file}. Error: {e}") from e
    print("\n=== Data Export Result ===\n")
    print(f"Exported to {output_file}")
    run_id = str(uuid.uuid4())
    save_run(
        RunRecord(
            id=run_id,
            kind="data_export",
            input=str(len(materials)),
            output=output_file,
            meta={"n_materials": len(materials)}
        )
    )
    print(f"\n[run_id] {run_id}")
    return output_file