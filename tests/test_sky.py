"""Airmass from altitude: one declared formula, and honest gaps."""

import math

from sagitta.sky import AIRMASS_FORMULA, airmass_from_altitude

# Real (CENTALT, AIRMASS) pairs from N.I.N.A. 3.2.0.9001 headers, Soul Nebula,
# 2026-08-29 and 2026-08-30. N.I.N.A. declares Gueymard 1993; we use
# Kasten-Young 1989. The two agree far more closely than any use we make of
# the number, which is what makes recomputing safe.
NINA_SAMPLES = [
    (24.3139376496665, 2.41721897315115),
    (40.3190010266495, 1.54342760541189),
    (41.5955425644902, 1.50447586609865),
]


def test_zenith_is_essentially_one():
    value = airmass_from_altitude(90.0)
    assert value is not None
    assert abs(value - 1.0) < 5e-4


def test_reproduces_nina_header_values():
    """Our formula must agree with the acquisition software on real headers.

    Not to prove Kasten-Young is Gueymard, but to prove that replacing the
    header value with our own changes nothing measurable.
    """
    for altitude_deg, header_airmass in NINA_SAMPLES:
        value = airmass_from_altitude(altitude_deg)
        assert value is not None
        relative = abs(value - header_airmass) / header_airmass
        assert relative < 1e-3, f"alt {altitude_deg}: {value} vs {header_airmass}"


def test_decreases_as_the_target_rises():
    values = [airmass_from_altitude(h) for h in (20.0, 30.0, 45.0, 60.0, 90.0)]
    assert all(v is not None for v in values)
    assert values == sorted(values, reverse=True)


def test_horizon_is_finite_and_large():
    value = airmass_from_altitude(0.0)
    assert value is not None
    assert 35.0 < value < 40.0


def test_below_the_horizon_is_unknown():
    assert airmass_from_altitude(-0.1) is None
    assert airmass_from_altitude(-30.0) is None


def test_above_the_zenith_is_unknown():
    assert airmass_from_altitude(90.1) is None


def test_non_finite_altitude_is_unknown():
    assert airmass_from_altitude(float("nan")) is None
    assert airmass_from_altitude(math.inf) is None


def test_formula_is_named_so_a_report_can_declare_it():
    assert "Kasten" in AIRMASS_FORMULA
    assert "1989" in AIRMASS_FORMULA
