## SHAE MATLAB Projectile Simulator v0.1.0

First release of the dependency-free **Python** projectile motion simulator, built in the spirit of MATLAB for the SHAE systems project.

### Highlights

- **Zero dependencies** — pure Python 3 standard library.
- **Four core metrics**: time of flight, maximum height, range, impact velocity (plus impact angle).
- **Five output formats**: summary, ASCII table, CSV, JSON, and a SHAE-styled SVG trajectory plot.
- **Full trajectory sampling** with configurable time step.
- **Known-answer test suite** — 12 tests validating against closed-form analytics.

### Usage

```bash
# Install the CLI
chmod +x scripts/install.sh
./scripts/install.sh

# Run
shae-projectile-simulator -v 50 -a 45
shae-projectile-simulator -v 30 -a 30 -dt 0.001 -o csv -f trajectory.csv
shae-projectile-simulator -v 25 -a 60 -o svg -f plot.svg
```

### Assets

- `shae-matlab-projectile-simulator-v0.1.0.tar.gz`
- `shae-matlab-projectile-simulator-v0.1.0.zip`
- SHA256 checksums

### Physics

Semi-implicit Euler integration with sub-step ground-impact interpolation. Validated against:

- T = 2·v₀·sin θ / g
- H = (v₀·sin θ)² / (2g)
- R = v₀²·sin(2θ) / g
