#!/usr/bin/env python3
"""
=======================================================================
SHAE MATLAB Projectile Simulator — Trajectory Test Suite
Known inputs / expected outputs for validation
Copyright (c) 2026 spdedsec <legendsatya7272@gmail.com>
License: MIT
=======================================================================
"""

import sys
import os
import math
import unittest

# Add src to path so we can import simulate
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from simulate import simulate


class TestTrajectory(unittest.TestCase):
    """Known-input / expected-output validation cases."""

    def setUp(self):
        self.tol = 0.05  # tolerance for floating point comparisons

    # ── 1. Basic flat-ground launch ────────────────────────────────

    def test_flat_ground_known_case(self):
        """v0=50 m/s, angle=45°, g=9.81 -> well-defined analytic outputs."""
        result = simulate(v0=50.0, angle_deg=45.0, g=9.81, dt=0.001)

        # Analytic: T = 2*v0*sin(theta)/g
        expected_T = 2 * 50.0 * math.sin(math.radians(45.0)) / 9.81
        expected_H = (50.0 * math.sin(math.radians(45.0))) ** 2 / (2 * 9.81)
        expected_R = 50.0 ** 2 * math.sin(2 * math.radians(45.0)) / 9.81

        self.assertAlmostEqual(result.time_of_flight, expected_T, delta=self.tol)
        self.assertAlmostEqual(result.max_height, expected_H, delta=self.tol)
        self.assertAlmostEqual(result.range_, expected_R, delta=self.tol)

    def test_flat_ground_45deg_30mps(self):
        """v0=30 m/s, angle=45°, g=9.81."""
        result = simulate(v0=30.0, angle_deg=45.0, g=9.81, dt=0.001)
        v0 = 30.0
        theta = math.radians(45.0)

        expected_T = 2 * v0 * math.sin(theta) / 9.81
        expected_H = (v0 * math.sin(theta)) ** 2 / (2 * 9.81)
        expected_R = v0 ** 2 * math.sin(2 * theta) / 9.81

        self.assertAlmostEqual(result.time_of_flight, expected_T, delta=self.tol)
        self.assertAlmostEqual(result.max_height, expected_H, delta=self.tol)
        self.assertAlmostEqual(result.range_, expected_R, delta=self.tol)

    # ── 2. Horizontal launch (angle=0) ─────────────────────────────

    def test_horizontal_launch(self):
        """v0=10 m/s, angle=0° -> purely horizontal initial velocity."""
        result = simulate(v0=10.0, angle_deg=0.0, g=9.81, dt=0.001)

        # T = sqrt(2*h/g) where h=0 for flat ground
        self.assertAlmostEqual(result.time_of_flight, 0.0, delta=self.tol)
        self.assertAlmostEqual(result.range_, 0.0, delta=self.tol)
        # Max height equals initial height (0)
        self.assertAlmostEqual(result.max_height, 0.0, delta=self.tol)

    # ── 3. Vertical launch (angle=90) ──────────────────────────────

    def test_vertical_launch(self):
        """v0=20 m/s, angle=90° -> range = 0, max height = v0^2/(2g)."""
        result = simulate(v0=20.0, angle_deg=90.0, g=9.81, dt=0.001)

        self.assertAlmostEqual(result.range_, 0.0, delta=self.tol)
        expected_H = 20.0 ** 2 / (2 * 9.81)
        self.assertAlmostEqual(result.max_height, expected_H, delta=self.tol)
        expected_T = 2 * 20.0 / 9.81
        self.assertAlmostEqual(result.time_of_flight, expected_T, delta=self.tol)

    # ── 4. Initial height offset ───────────────────────────────────

    def test_initial_height_offset(self):
        """v0=0 m/s dropped from y0=10 m -> T = sqrt(2*h/g)."""
        result = simulate(v0=0.1, angle_deg=0.0, g=9.81, dt=0.001, y0=10.0)

        # Time to fall from rest at height 10 m
        expected_T = math.sqrt(2 * 10.0 / 9.81)
        self.assertAlmostEqual(result.time_of_flight, expected_T, delta=0.05)
        self.assertAlmostEqual(result.max_height, 10.0, delta=self.tol)

    # ── 5. Time step convergence ───────────────────────────────────

    def test_time_step_convergence(self):
        """Smaller dt should approach analytic result."""
        coarse = simulate(v0=40.0, angle_deg=30.0, g=9.81, dt=0.1)
        fine = simulate(v0=40.0, angle_deg=30.0, g=9.81, dt=0.0001)

        # Fine dt should be closer to analytic
        v0 = 40.0
        theta = math.radians(30.0)
        expected_R = v0 ** 2 * math.sin(2 * theta) / 9.81

        err_coarse = abs(coarse.range_ - expected_R)
        err_fine = abs(fine.range_ - expected_R)
        self.assertLess(err_fine, err_coarse)

    # ── 6. Velocity decomposition ──────────────────────────────────

    def test_velocity_decomposition(self):
        """At t=0, vx = v0*cos(theta), vy = v0*sin(theta)."""
        result = simulate(v0=10.0, angle_deg=60.0, g=9.81, dt=0.001)
        p0 = result.points[0]

        self.assertAlmostEqual(p0.vx, 10.0 * math.cos(math.radians(60.0)), delta=self.tol)
        self.assertAlmostEqual(p0.vy, 10.0 * math.sin(math.radians(60.0)), delta=self.tol)
        self.assertAlmostEqual(p0.t, 0.0, delta=self.tol)
        self.assertAlmostEqual(p0.x, 0.0, delta=self.tol)
        self.assertAlmostEqual(p0.y, 0.0, delta=self.tol)

    # ── 7. Impact velocity symmetry (flat ground) ──────────────────

    def test_impact_symmetry_flat_ground(self):
        """On flat ground, impact speed equals launch speed."""
        result = simulate(v0=35.0, angle_deg=40.0, g=9.81, dt=0.001)
        self.assertAlmostEqual(result.impact_velocity, 35.0, delta=self.tol)

    # ── 8. Input validation ────────────────────────────────────────

    def test_negative_velocity_raises(self):
        with self.assertRaises(ValueError):
            simulate(v0=-5.0, angle_deg=45.0, g=9.81)

    def test_zero_velocity_raises(self):
        with self.assertRaises(ValueError):
            simulate(v0=0.0, angle_deg=45.0, g=9.81)

    def test_negative_gravity_raises(self):
        with self.assertRaises(ValueError):
            simulate(v0=10.0, angle_deg=45.0, g=-9.81)

    def test_negative_dt_raises(self):
        with self.assertRaises(ValueError):
            simulate(v0=10.0, angle_deg=45.0, g=9.81, dt=-0.01)


if __name__ == "__main__":
    unittest.main()