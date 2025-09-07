from __future__ import annotations
from openinorganicchemistry.core.dft_utils import quick_emt_energy


def test_quick_emt_energy_runs():
    e = quick_emt_energy("Ti")
    assert isinstance(e, float)


