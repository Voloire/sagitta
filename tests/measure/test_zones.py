import pytest

from sagitta.measure.shape import StarShape
from sagitta.measure.zones import (
    ZONE_NAMES,
    normalized_radius,
    summarize_zones,
    zone_of,
)


def _star(x, y, fwhm=3.0, ecc=0.1, pa=0.0) -> StarShape:
    return StarShape(x=x, y=y, flux=1000.0, fwhm_px=fwhm, eccentricity=ecc, position_angle_deg=pa)


def test_radius_is_zero_at_centre():
    assert normalized_radius(50.0, 50.0, 100, 100) == pytest.approx(0.0, abs=1e-9)


def test_radius_is_one_at_corner():
    assert normalized_radius(0.0, 0.0, 100, 100) == pytest.approx(1.0, abs=0.02)
    assert normalized_radius(100.0, 100.0, 100, 100) == pytest.approx(1.0, abs=0.02)


def test_zone_names_cover_all_regions():
    assert ZONE_NAMES == (
        "center",
        "mid",
        "corner_tl",
        "corner_tr",
        "corner_bl",
        "corner_br",
    )


def test_zone_of_centre_and_corners():
    assert zone_of(500.0, 500.0, 1000, 1000) == "center"
    assert zone_of(20.0, 20.0, 1000, 1000) == "corner_tl"
    assert zone_of(980.0, 20.0, 1000, 1000) == "corner_tr"
    assert zone_of(20.0, 980.0, 1000, 1000) == "corner_bl"
    assert zone_of(980.0, 980.0, 1000, 1000) == "corner_br"


def test_zone_of_mid_ring():
    # raggio normalizzato circa 0.45, dentro l'anello intermedio
    assert zone_of(500.0, 180.0, 1000, 1000) == "mid"


def test_summarize_reports_medians_per_zone():
    stars = [_star(500 + i, 500, fwhm=3.0, ecc=0.05) for i in range(10)]
    stars += [_star(20 + i, 20, fwhm=6.0, ecc=0.40) for i in range(10)]

    stats = summarize_zones(stars, 1000, 1000, min_stars=8)

    assert stats["center"].n_stars == 10
    assert stats["center"].median_fwhm_px == pytest.approx(3.0, abs=0.01)
    assert stats["center"].median_eccentricity == pytest.approx(0.05, abs=0.01)

    assert stats["corner_tl"].n_stars == 10
    assert stats["corner_tl"].median_eccentricity == pytest.approx(0.40, abs=0.01)


def test_zone_with_too_few_stars_reports_none():
    stars = [_star(500, 500), _star(501, 500)]
    stats = summarize_zones(stars, 1000, 1000, min_stars=8)
    assert stats["center"].n_stars == 2
    assert stats["center"].median_fwhm_px is None
    assert stats["center"].median_eccentricity is None


def test_position_angle_median_is_circular():
    """Angoli a 175 e 5 gradi distano 10 gradi, non 170: la mediana deve saperlo."""
    stars = [_star(500 + i, 500, pa=175.0) for i in range(5)]
    stars += [_star(505 + i, 500, pa=5.0) for i in range(5)]
    stats = summarize_zones(stars, 1000, 1000, min_stars=8)
    angle = stats["center"].median_position_angle_deg
    assert angle is not None
    assert min(angle, 180.0 - angle) < 15.0
