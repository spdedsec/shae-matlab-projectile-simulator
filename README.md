# SHAE MATLAB Projectile Simulator

<div align="center">

```
  ____  _   _    _    _____     __  __    _  _____ _     ____
 / ___|| | | |  / \  | ____|   |  \/  |  / \|_   _| |   | __ )
 \___ \| |_| | / _ \ |  _|     | |\/| | / _ \ | | | |   |  _ \
  ___) |  _  |/ ___ \| |___    | |  | |/ ___ \| | | |___| |_) |
 |____/|_| |_/_/   \_\_____|   |_|  |_/_/   \_\_| |_____|____/
```

> **A dependency-free, numerically rigorous projectile motion simulator in the spirit of MATLAB, delivered as a fast, scriptable Python CLI with CSV, JSON and SVG export.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](#)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)](#)
[![Tests](https://img.shields.io/badge/Tests-12%20Passing-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

</div>

---

## Overview

**SHAE MATLAB Projectile Simulator** is a command-line ballistics engine that models the two-dimensional motion of a projectile launched with an initial velocity at an angle, under constant gravitational acceleration. It computes the canonical kinematics quantities — **time of flight, maximum height, range, and impact velocity** — and exposes the full time-stepped trajectory for analysis.

It is built entirely on the **Python 3 standard library** (`math`, `argparse`, `csv`, `json`, `dataclasses`). There is nothing to `pip install`.

### Features

- **Four core metrics:** time of flight, max height, range, impact velocity (and impact angle).
- **Full trajectory table** with per-step position, velocity, and speed.
- **Multiple output formats:** summary, ASCII table, CSV, JSON, and an SVG trajectory plot styled to the SHAE design system.
- **Configurable physics:** initial velocity, launch angle, gravity, time step, and initial height.
- **Known-answer test suite** validating against closed-form analytic results.
- **Graceful input validation** with clear error messages.

---

## Installation

### Prerequisites

- Python **3.8 or newer** (uses `dataclasses`).

Verify:
```bash
python3 --version
```

### Quick install (recommended)

Clone the repository and run the installer:

```bash
git clone https://github.com/spdedsec/shae-matlab-projectile-simulator.git
cd shae-matlab-projectile-simulator
chmod +x scripts/install.sh
./scripts/install.sh
```

This creates a symlink in `~/.local/bin/shae-projectile-simulator`. Ensure `~/.local/bin` is on your `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"   # add to ~/.bashrc or ~/.zshrc
```

Then run from anywhere:

```bash
shae-projectile-simulator -v 50 -a 45
```

### Run without installing

```bash
./src/simulate.py -v 50 -a 45
# or
python3 src/simulate.py -v 50 -a 45
```

---

## Usage

```
shae-projectile-simulator -v VELOCITY -a ANGLE [options]
```

### Arguments

| Flag | Long form | Description | Default |
|------|-----------|-------------|---------|
| `-v` | `--velocity` | Initial velocity magnitude (m/s) | **required** |
| `-a` | `--angle` | Launch angle above horizontal (degrees) | **required** |
| `-g` | `--gravity` | Gravitational acceleration (m/s²) | `9.81` |
| `-dt` | `--time-step` | Integration time step (s) | `0.01` |
| `-y0` | `--initial-height` | Initial launch height (m) | `0.0` |
| `-o` | `--output` | `summary` · `table` · `csv` · `svg` · `json` | `summary` |
| `-f` | `--file` | Output file path (required for csv/svg/json) | — |
| `--table` | — | Alias for `-o table` | — |
| `--max-rows` | — | Max rows in sampled table | `50` |

### Examples

**Summary of a 50 m/s launch at 45°:**
```bash
shae-projectile-simulator -v 50 -a 45
```

**Full trajectory table (sampled to 50 rows):**
```bash
shae-projectile-simulator -v 50 -a 45 --table
```

**Export to CSV at high resolution:**
```bash
shae-projectile-simulator -v 30 -a 30 -dt 0.001 -o csv -f trajectory.csv
```

**Generate a styled SVG plot:**
```bash
shae-projectile-simulator -v 25 -a 60 -o svg -f plot.svg
```

**Machine-readable JSON for downstream tooling:**
```bash
shae-projectile-simulator -v 40 -a 45 -o json -f run.json
```

**Launch from a 10 m platform:**
```bash
shae-projectile-simulator -v 20 -a 15 -y0 10
```

### Sample output

```
┌──────────────────────────────────────────────────────────┐
│              SHAE PROJECTILE SIMULATOR                   │
├──────────────────────────────────────────────────────────┤
│  Initial Velocity     │      50.00 m/s                  │
│  Launch Angle         │      45.00°                     │
│  Gravity              │       9.81 m/s²                 │
│  Time Step            │       0.0100 s                  │
│  Initial Height       │       0.00 m                    │
├──────────────────────────────────────────────────────────┤
│  Time of Flight       │       7.208 s                   │
│  Maximum Height       │      63.728 m                   │
│  Range                │     255.073 m                   │
│  Impact Velocity      │      50.000 m/s                 │
│  Impact Angle         │     -45.00°                     │
└──────────────────────────────────────────────────────────┘
```

---

## Physics & Validation

The engine uses **semi-implicit Euler integration** with sub-step interpolation at ground impact. Results are validated against the closed-form analytic solutions:

| Quantity | Analytic formula (flat ground) |
|----------|-------------------------------|
| Time of flight | T = 2·v₀·sin θ / g |
| Max height | H = (v₀·sin θ)² / (2g) |
| Range | R = v₀²·sin(2θ) / g |
| Impact speed | v = v₀ (energy conservation) |

The test suite (`tests/test_trajectory/`) asserts these identities within tolerance and covers horizontal launches (θ=0°), vertical launches (θ=90°), initial-height offsets, time-step convergence, velocity decomposition, and input validation.

---

## Testing

```bash
make test
# or
python3 -m unittest tests.test_trajectory.test_trajectory -v
```

Expected result: **12 tests, all passing.**

---

## Repository Layout

```
shae-matlab-projectile-simulator/
├── src/
│   └── simulate.py                  # CLI entrypoint + engine + formatters
├── tests/
│   └── test_trajectory/
│       └── test_trajectory.py       # Known-answer test suite
├── scripts/
│   └── install.sh                   # ~/.local/bin symlink installer
├── .github/
│   └── workflows/
│       └── release.yml              # Tag-driven GitHub Release
├── Makefile                         # test / install / build / clean
├── DESIGN.md                        # Design system rationale
├── LICENSE                          # MIT
└── README.md                        # This file
```

---

## License

MIT © 2026 [spdedsec](https://github.com/spdedsec) `<legendsatya7272@gmail.com>`

Developed under the **SHAE** language & systems architecture project.