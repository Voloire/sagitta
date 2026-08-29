import numpy as np
import pytest

from sagitta.measure.shape import measure_shape


def _gaussian(size: int, sigma_x: float, sigma_y: float, theta_deg: float = 0.0):
    """Gaussiana ellittica centrata, ruotata di theta_deg in senso antiorario."""
    c = (size - 1) / 2.0
    yy, xx = np.mgrid[0:size, 0:size]
    dx = xx - c
    dy = yy - c
    t = np.deg2rad(theta_deg)
    xr = dx * np.cos(t) + dy * np.sin(t)
    yr = -dx * np.sin(t) + dy * np.cos(t)
    return np.exp(-0.5 * ((xr / sigma_x) ** 2 + (yr / sigma_y) ** 2))


def test_circular_star_has_zero_eccentricity():
    cutout = _gaussian(21, 2.0, 2.0)
    shape = measure_shape(cutout, 0, 0)
    assert shape is not None
    assert shape.eccentricity == pytest.approx(0.0, abs=0.02)


def test_circular_star_fwhm_matches_sigma():
    sigma = 2.0
    cutout = _gaussian(31, sigma, sigma)
    shape = measure_shape(cutout, 0, 0)
    expected = 2.0 * np.sqrt(2.0 * np.log(2.0)) * sigma
    assert shape.fwhm_px == pytest.approx(expected, rel=0.05)


def test_elongated_star_has_positive_eccentricity():
    cutout = _gaussian(31, 4.0, 2.0)
    shape = measure_shape(cutout, 0, 0)
    # e = sqrt(1 - (b/a)^2) = sqrt(1 - (2/4)^2) = 0.866
    assert shape.eccentricity == pytest.approx(0.866, abs=0.05)


def test_position_angle_zero_for_horizontal_elongation():
    cutout = _gaussian(31, 4.0, 2.0, theta_deg=0.0)
    shape = measure_shape(cutout, 0, 0)
    assert shape.position_angle_deg == pytest.approx(0.0, abs=3.0)


def test_position_angle_45_degrees():
    cutout = _gaussian(31, 4.0, 2.0, theta_deg=45.0)
    shape = measure_shape(cutout, 0, 0)
    assert shape.position_angle_deg == pytest.approx(45.0, abs=3.0)


def test_position_angle_is_wrapped_into_0_180():
    cutout = _gaussian(31, 4.0, 2.0, theta_deg=170.0)
    shape = measure_shape(cutout, 0, 0)
    assert 0.0 <= shape.position_angle_deg < 180.0
    assert shape.position_angle_deg == pytest.approx(170.0, abs=3.0)


def test_offset_is_added_to_centroid():
    cutout = _gaussian(21, 2.0, 2.0)
    shape = measure_shape(cutout, x0=100, y0=200)
    assert shape.x == pytest.approx(110.0, abs=0.2)
    assert shape.y == pytest.approx(210.0, abs=0.2)


def test_empty_cutout_returns_none():
    assert measure_shape(np.zeros((11, 11)), 0, 0) is None
