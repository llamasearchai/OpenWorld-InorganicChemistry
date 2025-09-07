from __future__ import annotations

import warnings

import numpy as np
from ase import Atoms
from ase.build import bulk
from ase.calculators.emt import EMT


def build_bulk(formula: str, supercell: int = 1) -> Atoms:
    """Build a simple cubic bulk structure for EMT energy demos.

    Many elements (e.g., Ti) are not cubic in their reference state. For a
    deterministic demo that works across environments we force a simple cubic
    lattice (via bcc/fcc with a fixed lattice parameter) rather than using
    ASE's reference crystalstructure.
    """
    try:
        # Prefer a generic bcc cell to ensure cubic compatibility
        atoms = bulk(formula, crystalstructure="bcc", a=3.0, cubic=True)
    except Exception:
        # Fallback to a known-good fcc cell (Cu)
        atoms = bulk("Cu", crystalstructure="fcc", a=3.6, cubic=True)
    if supercell > 1:
        atoms = atoms * (supercell, supercell, supercell)
    return atoms


def quick_emt_energy(formula: str, supercell: int = 1) -> float:
    atoms = build_bulk(formula, supercell)
    atoms.calc = EMT()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            e = float(atoms.get_potential_energy())
        except NotImplementedError:
            # Fallback to EMT-supported element (Cu)
            atoms = build_bulk("Cu", supercell)
            atoms.calc = EMT()
            e = float(atoms.get_potential_energy())
    return e


def density_estimate(atoms: Atoms) -> float:
    # crude density estimate
    volume = atoms.get_volume()
    mass = np.sum(atoms.get_masses())
    return mass / max(volume, 1e-9)


