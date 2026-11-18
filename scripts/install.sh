#!/usr/bin/env bash
# ========================================================================
# SHAE MATLAB Projectile Simulator — Install Script
# Copyright (c) 2026 spdedsec <legendsatya7272@gmail.com>
# License: MIT
# ========================================================================
#
# Usage:
#   chmod +x scripts/install.sh
#   ./scripts/install.sh
#
# Installs the `shae-projectile-simulator` CLI tool to ~/.local/bin

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_DIR="${HOME}/.local/bin"
DEST_BIN="${DEST_DIR}/shae-projectile-simulator"

echo "===================================================================="
echo "  SHAE MATLAB Projectile Simulator — Installer"
echo "===================================================================="

# Ensure destination exists
mkdir -p "${DEST_DIR}"

# Create symlink
ln -sf "${SCRIPT_DIR}/src/simulate.py" "${DEST_BIN}"
chmod +x "${SCRIPT_DIR}/src/simulate.py"

echo "==> Installed to: ${DEST_BIN}"
echo "==> Test: ${DEST_BIN} -v 50 -a 45"