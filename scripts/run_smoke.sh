#!/usr/bin/env bash
set -euo pipefail
echo "==> Doctor"
oic doctor || true
echo "==> Literature (mock topic)"
oic literature "perovskite stability" || true
echo "==> Synthesis"
oic synth CH3NH3PbI3 || true
echo "==> Simulation"
oic simulate Ti --backend emt --supercell 1
echo "==> Analysis"
oic analyze data/sample_values.csv


