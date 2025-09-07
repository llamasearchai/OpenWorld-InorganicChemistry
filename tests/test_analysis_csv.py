from __future__ import annotations
import os
from openinorganicchemistry.agents.analysis import analyze_results


def test_analyze_results(tmp_path):
    p = tmp_path / "vals.csv"
    p.write_text("1.0\n2.0\n3.0\n", encoding="utf-8")
    run_id = analyze_results(str(p))
    assert isinstance(run_id, str)
    assert os.path.exists("convergence.png")


