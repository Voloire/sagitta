"""Validazione dello strato di misura contro verita' sintetica nota.

Non si valida un classificatore: qui si verifica che la dipendenza spaziale
dell'aberrazione iniettata sia quella che la misura restituisce.
"""

import numpy as np

from sagitta.measure.detect import DetectionSettings
from sagitta.measure.frame import measure_frame
from sagitta.synth.generator import Truth, generate_frame, write_synthetic_fits


def _measure(tmp_path, truth, name, n_stars=300, seed=11):
    pixels = generate_frame(900, 900, truth, n_stars=n_stars, seed=seed)
    path = write_synthetic_fits(tmp_path / f"{name}.fits", pixels)
    # Il ritaglio deve essere piu' largo della stella: con l'aberrazione
    # iniettata le stelle d'angolo arrivano a FWHM di circa 9 pixel, e una
    # finestra troppo stretta troncherebbe i momenti secondi, falsando
    # verso il basso sia FWHM che eccentricita'.
    settings = DetectionSettings(cutout_radius=10, border_margin=20)
    return measure_frame(path, settings)


def test_clean_frame_is_round_everywhere(tmp_path):
    result = _measure(tmp_path, Truth(seeing_sigma_px=2.5), "clean")
    assert result.zones["center"].median_eccentricity < 0.25
    assert result.zones["corner_tl"].median_eccentricity < 0.30


def test_guide_error_elongates_the_centre_as_much_as_the_corners(tmp_path):
    """Firma della guida: allungamento uniforme, centro compreso."""
    truth = Truth(seeing_sigma_px=2.0, guide_elongation=3.0, guide_angle_deg=0.0)
    result = _measure(tmp_path, truth, "guide")

    centre = result.zones["center"].median_eccentricity
    corner = result.zones["corner_br"].median_eccentricity
    assert centre > 0.6
    assert abs(centre - corner) < 0.2


def test_guide_error_position_angle_matches_the_injected_one(tmp_path):
    truth = Truth(seeing_sigma_px=2.0, guide_elongation=3.0, guide_angle_deg=30.0)
    result = _measure(tmp_path, truth, "guide30")
    measured = result.zones["center"].median_position_angle_deg
    difference = min(abs(measured - 30.0), 180.0 - abs(measured - 30.0))
    assert difference < 12.0


def test_spacing_error_leaves_the_centre_round(tmp_path):
    """Firma della spaziatura: nulla al centro, uguale nei quattro angoli."""
    truth = Truth(seeing_sigma_px=2.0, spacing_error=2.0)
    result = _measure(tmp_path, truth, "spacing")

    assert result.zones["center"].median_fwhm_px < 6.5

    corners = [
        result.zones[name].median_fwhm_px
        for name in ("corner_tl", "corner_tr", "corner_bl", "corner_br")
    ]
    assert min(corners) > result.zones["center"].median_fwhm_px
    assert max(corners) - min(corners) < 0.25 * np.mean(corners)


def test_tilt_makes_opposite_corners_asymmetric(tmp_path):
    """Firma del tilt: asimmetria fra angoli opposti, a differenza della spaziatura."""
    truth = Truth(seeing_sigma_px=2.0, tilt_x=2.0)
    result = _measure(tmp_path, truth, "tilt")

    left = np.mean(
        [
            result.zones["corner_tl"].median_fwhm_px,
            result.zones["corner_bl"].median_fwhm_px,
        ]
    )
    right = np.mean(
        [
            result.zones["corner_tr"].median_fwhm_px,
            result.zones["corner_br"].median_fwhm_px,
        ]
    )
    assert abs(right - left) > 0.25 * np.mean([left, right])


def test_spacing_and_tilt_are_distinguishable(tmp_path):
    """La differenza fra le due firme e' misurabile, e questo e' il punto."""
    spacing = _measure(tmp_path, Truth(2.0, spacing_error=2.0), "s2")
    tilt = _measure(tmp_path, Truth(2.0, tilt_x=2.0), "t2")

    def asymmetry(result):
        left = np.mean(
            [
                result.zones["corner_tl"].median_fwhm_px,
                result.zones["corner_bl"].median_fwhm_px,
            ]
        )
        right = np.mean(
            [
                result.zones["corner_tr"].median_fwhm_px,
                result.zones["corner_br"].median_fwhm_px,
            ]
        )
        return abs(right - left) / np.mean([left, right])

    assert asymmetry(spacing) < 0.15
    assert asymmetry(tilt) > 0.25
