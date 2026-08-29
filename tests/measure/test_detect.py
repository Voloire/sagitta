import numpy as np
import pytest

from sagitta.measure.detect import (
    DetectionSettings,
    detect_stars,
    estimate_background,
)


def _place_gaussian(image, cx, cy, sigma, amplitude):
    # Il ritaglio va limitato ai bordi dell'immagine. Uno slice che parte da un
    # indice negativo, in Python, conta dalla fine: per una stella a (5, 5) il
    # ritaglio non verrebbe tagliato, verrebbe vuoto, e la somma fallirebbe.
    size = int(np.ceil(sigma * 6))
    height, width = image.shape
    y0, y1 = max(cy - size, 0), min(cy + size + 1, height)
    x0, x1 = max(cx - size, 0), min(cx + size + 1, width)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    image[y0:y1, x0:x1] += amplitude * np.exp(
        -0.5 * (((xx - cx) / sigma) ** 2 + ((yy - cy) / sigma) ** 2)
    )
    return image


def _field(width=200, height=200, background=100.0, noise=2.0, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(background, noise, size=(height, width))


def test_estimate_background_recovers_median_and_sigma():
    image = _field(background=250.0, noise=5.0)
    median, sigma = estimate_background(image)
    assert median == pytest.approx(250.0, abs=1.0)
    assert sigma == pytest.approx(5.0, rel=0.2)


def test_detects_isolated_stars():
    image = _field(seed=1)
    for cx, cy in [(50, 50), (150, 60), (100, 140)]:
        _place_gaussian(image, cx, cy, sigma=2.0, amplitude=500.0)

    stars = detect_stars(image)
    assert len(stars) == 3

    found = sorted((round(s.x), round(s.y)) for s in stars)
    assert found == [(50, 50), (100, 140), (150, 60)]


def test_rejects_stars_touching_the_border():
    image = _field(seed=2)
    _place_gaussian(image, 5, 5, sigma=2.0, amplitude=500.0)
    _place_gaussian(image, 100, 100, sigma=2.0, amplitude=500.0)

    stars = detect_stars(image)
    assert len(stars) == 1
    assert round(stars[0].x) == 100


def test_rejects_saturated_stars():
    image = _field(seed=3)
    _place_gaussian(image, 100, 100, sigma=2.0, amplitude=500.0)
    # stella satura: cima piatta al valore massimo
    image[70:76, 70:76] = 65535.0

    stars = detect_stars(image, DetectionSettings(max_flat_top_pixels=3))
    positions = [round(s.x) for s in stars]
    assert 100 in positions
    assert 72 not in positions


def test_brightest_unsaturated_star_is_kept():
    """Il criterio di saturazione non deve scartare la stella piu' luminosa
    solo perche' e' la piu' luminosa: deve guardare la cima piatta."""
    image = _field(seed=31)
    _place_gaussian(image, 60, 60, sigma=2.0, amplitude=500.0)
    _place_gaussian(image, 140, 140, sigma=2.0, amplitude=20000.0)

    stars = detect_stars(image)
    positions = sorted(round(s.x) for s in stars)
    assert positions == [60, 140]


def test_rejects_single_hot_pixel():
    image = _field(seed=4)
    image[120, 130] = 60000.0
    _place_gaussian(image, 60, 60, sigma=2.0, amplitude=500.0)

    stars = detect_stars(image, DetectionSettings(min_pixels=5))
    positions = [round(s.x) for s in stars]
    assert 60 in positions
    assert 130 not in positions


def test_empty_field_returns_no_stars():
    assert detect_stars(_field(seed=5)) == []
