#!/usr/bin/env bash
# ========================================================================
# SHAE MATLAB Projectile Simulator — Build & Packaging Automation
# Copyright (c) 2026 spdedsec <legendsatya7272@gmail.com>
# License: MIT
# ========================================================================

set -euo pipefail

VERSION="${1:-0.1.0}"
DIST_DIR="dist"
ARCHIVE_PREFIX="shae-matlab-projectile-simulator-v${VERSION}"

echo "===================================================================="
echo "  SHAE MATLAB Projectile Simulator — Build & Release Packaging"
echo "  Version: v${VERSION}"
echo "===================================================================="

# 1. Run unit test suite
echo "==> Running trajectory test suite..."
python3 -m unittest tests.test_trajectory.test_trajectory

# 2. Prepare distribution directory
echo "==> Preparing artifact output directory (${DIST_DIR})..."
rm -rf "${DIST_DIR}"
mkdir -p "${DIST_DIR}/${ARCHIVE_PREFIX}"

# 3. Copy source and assets into bundle
cp -r src "${DIST_DIR}/${ARCHIVE_PREFIX}/"
cp -r tests "${DIST_DIR}/${ARCHIVE_PREFIX}/"
cp -r scripts "${DIST_DIR}/${ARCHIVE_PREFIX}/"
cp Makefile README.md DESIGN.md LICENSE "${DIST_DIR}/${ARCHIVE_PREFIX}/"

# 4. Generate archives
echo "==> Generating compressed release archives..."
cd "${DIST_DIR}"
tar -czf "${ARCHIVE_PREFIX}.tar.gz" "${ARCHIVE_PREFIX}"
zip -rq "${ARCHIVE_PREFIX}.zip" "${ARCHIVE_PREFIX}"
cd ..

# 5. Checksum generation
echo "==> Generating SHA256 checksums..."
cd "${DIST_DIR}"
sha256sum "${ARCHIVE_PREFIX}.tar.gz" > "${ARCHIVE_PREFIX}.tar.gz.sha256"
sha256sum "${ARCHIVE_PREFIX}.zip" > "${ARCHIVE_PREFIX}.zip.sha256"
cd ..

echo "==> Build complete! Output artifacts in ${DIST_DIR}:"
ls -lh "${DIST_DIR}"/*.tar.gz "${DIST_DIR}"/*.zip