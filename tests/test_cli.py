from __future__ import annotations
import subprocess
import sys


def test_cli_help():
    out = subprocess.check_output([sys.executable, "-m", "openinorganicchemistry.cli", "--help"])
    assert b"OpenInorganicChemistry CLI" in out


