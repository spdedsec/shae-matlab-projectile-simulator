# ========================================================================
# SHAE MATLAB Projectile Simulator — Makefile
# Copyright (c) 2026 spdedsec <legendsatya7272@gmail.com>
# License: MIT
# ========================================================================

.PHONY: all test install build clean

all: test

test:
	@echo "==> Running trajectory test suite..."
	@python3 -m unittest tests.test_trajectory.test_trajectory -v

install:
	@echo "==> Installing shae-projectile-simulator to ~/.local/bin..."
	@bash scripts/install.sh

build:
	@echo "==> Building release archives..."
	@bash scripts/build.sh

clean:
	@echo "==> Cleaning..."
	@rm -rf dist
	@rm -f *.pyc
	@rm -rf __pycache__
	@rm -rf tests/__pycache__
	@rm -rf src/__pycache__