# SHAE MATLAB Projectile Simulator — DESIGN.md

> A pedagogical CLI ballistics engine implementing discrete time-step kinematic integration, following the SHAE field manual design system.

---

## Design Philosophy

**Precise over decorative.** The simulator outputs raw kinematic data with full numeric precision. The CLI is the primary interface; visualization is an output artifact, not a runtime dependency.

**Confident restraint.** Warm paper (#F2EEE5) ground, ink (#191712) text, oxide (#B3341B) signal for trajectory path and max-height marker. 0px radius, hairline 1px borders, no gradients, no shadows, no glassmorphism.

**Motion is typesetting.** No animation library; SVG and CSV are static output artifacts. CLI state changes are immediate.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              CLI ARGUMENTS                      │
│    -v velocity  -a angle  -g gravity  -dt dt    │
└──────────────────┬──────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────┐
│          simulate() Kinematic Engine            │
│  • Semi-implicit Euler integration              │
│  • Linear interpolation at ground impact        │
│  • Pure function, no side effects               │
└──────────────────┬──────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────┐
│           SimulationResult dataclass            │
│  • time_of_flight  • max_height  • range_       │
│  • impact_velocity  • impact_angle              │
│  • points: List[TrajectoryPoint]                │
└──────────────────┬──────────────────────────────┘
                   │
     ┌─────────────┼─────────────┬─────────────┐
     v             v             v             v
  summary        table           csv            svg
  (stdout)     (stdout)       (file)        (file)
```

---

## Physics Model

### Discrete Integration
- Semi-implicit Euler: position updates use current velocity; velocity updates use gravity after position.
- dt default: 0.01 s (configurable).
- Ground impact interpolated linearly between last two time steps for sub-step accuracy.

### Analytic Validation
- Time of flight (flat ground): T = 2·v0·sin(θ)/g
- Max height: H = (v0·sin θ)² / (2g)
- Range: R = v0²·sin(2θ) / g
- Impact speed = launch speed (energy conservation, flat ground).

### Domain Errors
- v0 ≤ 0 → ValueError
- dt ≤ 0 → ValueError
- g ≤ 0 → ValueError

---

## Output Formats

| Format | Destination | Content |
|--------|-------------|---------|
| `summary` | stdout | Formatted box with inputs + derived metrics |
| `table` | stdout | ASCII table of trajectory points (sampled) |
| `csv` | file | Full-resolution CSV: t,x,y,vx,vy,speed |
| `svg` | file | Trajectory plot in SHAE design system |
| `json` | file | Complete machine-readable simulation state |

---

## Typography & Color

- Display: Archivo (SVG title)
- Body / Labels: JetBrains Mono (SVG tick labels, CSV headers)
- Paper: #F2EEE5, Ink: #191712, Oxide: #B3341B

---

## Accessibility

- CLI is inherently keyboard-accessible.
- SVG uses `stroke-linecap="round"` for anti-aliased visibility.
- All SVG text uses ≥10px JetBrains Mono for legibility.
- No horizontal overflow in SVG viewBox.

---

## File Map

```
shae-matlab-projectile-simulator/
├── src/simulate.py              # CLI + engine + output formatters
├── tests/test_trajectory/       # Known-input / expected-output suite
├── scripts/install.sh           # ~/.local/bin symlink installer
├── Makefile                     # test, install, build, clean
├── DESIGN.md                    # This file
├── README.md                    # User-facing documentation
├── LICENSE                      # MIT
└── .github/workflows/release.yml
```