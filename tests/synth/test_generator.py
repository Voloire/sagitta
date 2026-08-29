import numpy as np
import pytest

from sagitta.synth.generator import Truth, generate_frame


def _median_in_box(image, x0, x1, y0, y1):
    return float(np.median(image[y0:y1, x0:x1]))


def test_clean_frame_has_stars_and_background():
    truth = Truth(seeing_sigma_px=2.0)
    image = generate_frame(600, 600, truth, n_stars=200, seed=1)
    assert image.shape == (600, 600)
    assert image.max() > 100.0
    assert np.median(image) == pytest.approx(100.0, abs=5.0)


def test_generation_is_reproducible_with_the_same_seed():
    truth = Truth(seeing_sigma_px=2.0)
    a = generate_frame(300, 300, truth, n_stars=50, seed=42)
    b = generate_frame(300, 300, truth, n_stars=50, seed=42)
    assert np.array_equal(a, b)


def test_different_seeds_give_different_frames():
    truth = Truth(seeing_sigma_px=2.0)
    a = generate_frame(300, 300, truth, n_stars=50, seed=1)
    b = generate_frame(300, 300, truth, n_stars=50, seed=2)
    assert not np.array_equal(a, b)


def test_spacing_error_leaves_the_centre_clean():
    """Errore di spaziatura: nullo al centro, cresce col raggio."""
    clean = Truth(seeing_sigma_px=2.0)
    spaced = Truth(seeing_sigma_px=2.0, spacing_error=3.0)
    a = generate_frame(600, 600, clean, n_stars=600, seed=3)
    b = generate_frame(600, 600, spaced, n_stars=600, seed=3)
    # Stesso seed, stesse posizioni: il confronto appaiato isola l'allargamento
    # invece di misurare quali stelle sono capitate dentro la finestra.
    corner_clean = _median_in_box(a, 20, 140, 20, 140)
    corner_spaced = _median_in_box(b, 20, 140, 20, 140)
    centre_clean = _median_in_box(a, 240, 360, 240, 360)
    centre_spaced = _median_in_box(b, 240, 360, 240, 360)
    assert corner_spaced - corner_clean > 5.0
    assert centre_spaced - centre_clean < 0.5


def test_guide_elongation_affects_the_centre_too():
    """L'errore di guida allunga anche le stelle centrali."""
    clean = Truth(seeing_sigma_px=2.0)
    guided = Truth(seeing_sigma_px=2.0, guide_elongation=2.0, guide_angle_deg=30.0)
    a = generate_frame(400, 400, clean, n_stars=300, seed=4)
    b = generate_frame(400, 400, guided, n_stars=300, seed=4)
    # stesse posizioni (stesso seed), ma le stelle centrali sono piu' larghe
    assert _median_in_box(b, 180, 220, 180, 220) > _median_in_box(a, 180, 220, 180, 220)


def test_tilt_makes_opposite_corners_differ():
    truth = Truth(seeing_sigma_px=2.0, tilt_x=3.0)
    image = generate_frame(600, 600, truth, n_stars=600, seed=5)
    left = _median_in_box(image, 0, 80, 260, 340)
    right = _median_in_box(image, 520, 600, 260, 340)
    assert abs(left - right) > 0.5
