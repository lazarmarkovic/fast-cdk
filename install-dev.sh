#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="fastcdk_venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[-] removing old venv at $VENV_DIR (if any)..."
rm -rf "$VENV_DIR"

echo "[+] creating new venv with $PYTHON_BIN..."
$PYTHON_BIN -m venv "$VENV_DIR"

echo "[+] activating venv..."
# note: this only affects this script's shell; to use it in your shell, run: source .venv/bin/activate
source "$VENV_DIR/bin/activate"

echo "[+] upgrading pip..."
python -m pip install --upgrade pip

echo "[+] installing fastCDK in editable mode with dev extras..."
python -m pip install -e ".[dev]"

echo "[✓] done. to use the venv in a new shell, run:"
echo "    source $VENV_DIR/bin/activate"