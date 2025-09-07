from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MaterialSpec:
    formula: str
    notes: str = ""


