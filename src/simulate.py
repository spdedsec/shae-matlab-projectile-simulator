#!/usr/bin/env python3
"""
=======================================================================
SHAE MATLAB Projectile Simulator — CLI Ballistics Engine
Physics: Kinematic equations with discrete time-step integration
Copyright (c) 2026 spdedsec <legendsatya7272@gmail.com>
License: MIT
=======================================================================
"""

import sys
import math
import argparse
import csv
import json
from typing import List, Tuple, Optional
from dataclasses import dataclass


# ─── Design System Constants ────────────────────────────────────────
PAPER = "#F2EEE5"
INK = "#191712"
OXIDE = "#B3341B"


@dataclass
class TrajectoryPoint:
    """Single time-step snapshot of projectile state."""
    t: float          # Time (s)
    x: float          # Horizontal position (m)
    y: float          # Vertical position (m)
    vx: float         # Horizontal velocity (m/s)
    vy: float         # Vertical velocity (m/s)
    speed: float      # Magnitude of velocity (m/s)


@dataclass
class SimulationResult:
    """Complete simulation outputs."""
    time_of_flight: float
    max_height: float
    range_: float
    impact_velocity: float
    impact_angle: float
    points: List[TrajectoryPoint]


def simulate(
    v0: float,
    angle_deg: float,
    g: float = 9.81,
    dt: float = 0.01,
    y0: float = 0.0,
) -> SimulationResult:
    """
    Simulate projectile motion using discrete time-step integration.

    Args:
        v0: Initial velocity magnitude (m/s)
        angle_deg: Launch angle above horizontal (degrees)
        g: Gravitational acceleration (m/s^2), positive downward
        dt: Time step (s)
        y0: Initial height (m)

    Returns:
        SimulationResult with trajectory data and derived metrics.
    """
    if v0 <= 0:
        raise ValueError("Initial velocity must be positive")
    if dt <= 0:
        raise ValueError("Time step must be positive")
    if g <= 0:
        raise ValueError("Gravity must be positive")

    theta = math.radians(angle_deg)
    vx0 = v0 * math.cos(theta)
    vy0 = v0 * math.sin(theta)

    points: List[TrajectoryPoint] = []

    t = 0.0
    x = 0.0
    y = y0
    vx = vx0
    vy = vy0

    max_height = y0

    # Integration loop
    while y >= 0:
        speed = math.hypot(vx, vy)
        points.append(TrajectoryPoint(t, x, y, vx, vy, speed))

        if y > max_height:
            max_height = y

        # Euler integration step
        x += vx * dt
        y += vy * dt
        vy -= g * dt
        t += dt

    # Final point at ground impact (interpolated for accuracy)
    if len(points) >= 2:
        p1 = points[-2]
        p2 = points[-1]
        # Linear interpolation to y=0
        if p2.y != p1.y:
            alpha = -p1.y / (p2.y - p1.y)
            t_impact = p1.t + alpha * dt
            x_impact = p1.x + alpha * (p2.x - p1.x)
            vx_impact = p1.vx + alpha * (p2.vx - p1.vx)
            vy_impact = p1.vy + alpha * (p2.vy - p1.vy)
        else:
            t_impact = p2.t
            x_impact = p2.x
            vx_impact = p2.vx
            vy_impact = p2.vy
    else:
        t_impact = 0.0
        x_impact = 0.0
        vx_impact = vx0
        vy_impact = vy0

    impact_speed = math.hypot(vx_impact, vy_impact)
    impact_angle_deg = math.degrees(math.atan2(-vy_impact, vx_impact))

    return SimulationResult(
        time_of_flight=t_impact,
        max_height=max_height,
        range_=x_impact,
        impact_velocity=impact_speed,
        impact_angle=impact_angle_deg,
        points=points,
    )


def format_table(points: List[TrajectoryPoint], max_rows: int = 50) -> str:
    """Format trajectory points as aligned ASCII table."""
    if not points:
        return "No trajectory data."

    lines = []
    header = f"{'t (s)':>8}  {'x (m)':>10}  {'y (m)':>10}  {'vx (m/s)':>10}  {'vy (m/s)':>10}  {'speed (m/s)':>11}"
    lines.append(header)
    lines.append("─" * len(header))

    step = max(1, len(points) // max_rows)
    for i in range(0, len(points), step):
        p = points[i]
        lines.append(
            f"{p.t:8.3f}  {p.x:10.3f}  {p.y:10.3f}  {p.vx:10.3f}  {p.vy:10.3f}  {p.speed:11.3f}"
        )

    # Always include final impact point
    last = points[-1]
    if len(points) > 1 and (len(points) - 1) % step != 0:
        lines.append(
            f"{last.t:8.3f}  {last.x:10.3f}  {last.y:10.3f}  {last.vx:10.3f}  {last.vy:10.3f}  {last.speed:11.3f}"
        )

    return "\n".join(lines)


def write_csv(result: SimulationResult, outfile: str) -> None:
    """Write trajectory data to CSV file."""
    with open(outfile, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["t_s", "x_m", "y_m", "vx_m_s", "vy_m_s", "speed_m_s"])
        for p in result.points:
            writer.writerow([p.t, p.x, p.y, p.vx, p.vy, p.speed])


def write_svg(result: SimulationResult, outfile: str, width: int = 800, height: int = 400, margin: int = 50) -> None:
    """Generate SVG trajectory plot."""
    if not result.points:
        return

    max_x = max(p.x for p in result.points)
    max_y = max(p.y for p in result.points)

    # Scaling factors
    scale_x = (width - 2 * margin) / max_x if max_x > 0 else 1
    scale_y = (height - 2 * margin) / max_y if max_y > 0 else 1
    scale = min(scale_x, scale_y)

    # Path data
    path_points = []
    for p in result.points:
        sx = margin + p.x * scale
        sy = height - margin - p.y * scale
        path_points.append(f"{sx:.2f},{sy:.2f}")

    path_d = "M " + " L ".join(path_points)

    # Ground line
    ground_y = height - margin

    # Y-axis ticks
    y_ticks = []
    num_ticks = 5
    for i in range(num_ticks + 1):
        y_val = (max_y * i) / num_ticks
        sy = height - margin - y_val * scale
        y_ticks.append(f'<line x1="{margin - 5}" y1="{sy:.1f}" x2="{margin}" y2="{sy:.1f}" stroke="{INK}" stroke-width="1"/>')
        y_ticks.append(f'<text x="{margin - 10}" y="{sy + 4:.1f}" font-family="JetBrains Mono, monospace" font-size="10" fill="{INK}" text-anchor="end">{y_val:.1f}</text>')

    # X-axis ticks
    x_ticks = []
    for i in range(num_ticks + 1):
        x_val = (max_x * i) / num_ticks
        sx = margin + x_val * scale
        x_ticks.append(f'<line x1="{sx:.1f}" y1="{ground_y}" x2="{sx:.1f}" y2="{ground_y + 5}" stroke="{INK}" stroke-width="1"/>')
        x_ticks.append(f'<text x="{sx:.1f}" y="{ground_y + 18}" font-family="JetBrains Mono, monospace" font-size="10" fill="{INK}" text-anchor="middle">{x_val:.1f}</text>')

    # Max height marker
    max_h_point = max(result.points, key=lambda p: p.y)
    max_h_x = margin + max_h_point.x * scale
    max_h_y = height - margin - max_h_point.y * scale

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="100%" height="100%" fill="{PAPER}"/>

  <!-- Axes -->
  <line x1="{margin}" y1="{margin}" x2="{margin}" y2="{ground_y}" stroke="{INK}" stroke-width="1.5"/>
  <line x1="{margin}" y1="{ground_y}" x2="{width - margin}" y2="{ground_y}" stroke="{INK}" stroke-width="1.5"/>

  <!-- Y-axis ticks -->
  {"".join(y_ticks)}

  <!-- X-axis ticks -->
  {"".join(x_ticks)}

  <!-- Trajectory path -->
  <path d="{path_d}" fill="none" stroke="{OXIDE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Max height marker -->
  <circle cx="{max_h_x:.2f}" cy="{max_h_y:.2f}" r="4" fill="{OXIDE}"/>
  <text x="{max_h_x + 8:.2f}" y="{max_h_y - 8:.2f}" font-family="JetBrains Mono, monospace" font-size="10" fill="{OXIDE}">
    MAX H: {max_h_point.y:.2f} m
  </text>

  <!-- Labels -->
  <text x="{width / 2}" y="{margin - 15}" font-family="Archivo, sans-serif" font-size="14" fill="{INK}" text-anchor="middle" font-weight="600" letter-spacing="1px">
    PROJECTILE TRAJECTORY
  </text>
  <text x="{width / 2}" y="{height - 5}" font-family="JetBrains Mono, monospace" font-size="10" fill="{INK}" text-anchor="middle">
    RANGE: {result.range_:.2f} m  |  TIME OF FLIGHT: {result.time_of_flight:.2f} s  |  IMPACT V: {result.impact_velocity:.2f} m/s
  </text>
</svg>'''

    with open(outfile, "w") as f:
        f.write(svg)


def print_summary(result: SimulationResult, v0: float, angle_deg: float, g: float, dt: float, y0: float) -> None:
    """Print formatted simulation summary to stdout."""
    print()
    print("┌" + "─" * 58 + "┐")
    print("│" + " " * 14 + "SHAE PROJECTILE SIMULATOR" + " " * 15 + "│")
    print("├" + "─" * 58 + "┤")
    print(f"│  Initial Velocity     │ {v0:>10.2f} m/s                              │")
    print(f"│  Launch Angle         │ {angle_deg:>10.2f}°                                │")
    print(f"│  Gravity              │ {g:>10.2f} m/s²                              │")
    print(f"│  Time Step            │ {dt:>10.4f} s                                │")
    print(f"│  Initial Height       │ {y0:>10.2f} m                                │")
    print("├" + "─" * 58 + "┤")
    print(f"│  Time of Flight       │ {result.time_of_flight:>10.3f} s                              │")
    print(f"│  Maximum Height       │ {result.max_height:>10.3f} m                              │")
    print(f"│  Range                │ {result.range_:>10.3f} m                              │")
    print(f"│  Impact Velocity      │ {result.impact_velocity:>10.3f} m/s                              │")
    print(f"│  Impact Angle         │ {result.impact_angle:>10.2f}°                                │")
    print("└" + "─" * 58 + "┘")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SHAE MATLAB Projectile Simulator — CLI ballistics engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -v 50 -a 45
  %(prog)s -v 30 -a 30 -g 9.81 -dt 0.005 -o csv -f trajectory.csv
  %(prog)s -v 25 -a 60 -o svg -f plot.svg
  %(prog)s -v 40 -a 45 --table
        """,
    )
    parser.add_argument("-v", "--velocity", type=float, required=True, help="Initial velocity (m/s)")
    parser.add_argument("-a", "--angle", type=float, required=True, help="Launch angle (degrees)")
    parser.add_argument("-g", "--gravity", type=float, default=9.81, help="Gravitational acceleration (m/s^2) [default: 9.81]")
    parser.add_argument("-dt", "--time-step", type=float, default=0.01, help="Integration time step (s) [default: 0.01]")
    parser.add_argument("-y0", "--initial-height", type=float, default=0.0, help="Initial height (m) [default: 0.0]")
    parser.add_argument("-o", "--output", choices=["table", "csv", "svg", "json", "summary"], default="summary", help="Output format [default: summary]")
    parser.add_argument("-f", "--file", type=str, help="Output file path (required for csv, svg, json)")
    parser.add_argument("--table", action="store_true", help="Print trajectory table to stdout (alias for -o table)")
    parser.add_argument("--max-rows", type=int, default=50, help="Maximum rows in table output [default: 50]")

    args = parser.parse_args()

    if args.table:
        args.output = "table"

    if args.output in ("csv", "svg", "json") and not args.file:
        parser.error(f"Output format '{args.output}' requires --file/-f argument")

    try:
        result = simulate(
            v0=args.velocity,
            angle_deg=args.angle,
            g=args.gravity,
            dt=args.time_step,
            y0=args.initial_height,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.output == "summary":
        print_summary(result, args.velocity, args.angle, args.gravity, args.time_step, args.initial_height)
    elif args.output == "table":
        print_summary(result, args.velocity, args.angle, args.gravity, args.time_step, args.initial_height)
        print("TRAJECTORY TABLE (sampled)")
        print("=" * 72)
        print(format_table(result.points, args.max_rows))
    elif args.output == "csv":
        write_csv(result, args.file)
        print(f"Trajectory CSV written to {args.file}")
    elif args.output == "svg":
        write_svg(result, args.file)
        print(f"Trajectory SVG written to {args.file}")
    elif args.output == "json":
        data = {
            "inputs": {
                "velocity": args.velocity,
                "angle_deg": args.angle,
                "gravity": args.gravity,
                "time_step": args.time_step,
                "initial_height": args.initial_height,
            },
            "results": {
                "time_of_flight": result.time_of_flight,
                "max_height": result.max_height,
                "range": result.range_,
                "impact_velocity": result.impact_velocity,
                "impact_angle": result.impact_angle,
            },
            "trajectory": [
                {"t": p.t, "x": p.x, "y": p.y, "vx": p.vx, "vy": p.vy, "speed": p.speed}
                for p in result.points
            ],
        }
        with open(args.file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Simulation JSON written to {args.file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())