import numpy as np
import pytest

from sagitta.measure.cfa import (
    GREEN_SUBLATTICE_SCALE_FACTOR,
    extract_green_sublattice,
    is_bayer,
)


def test_is_bayer():
    assert is_bayer("RGGB") is True
    assert is_bayer("bggr") is True
    assert is_bayer(None) is False
    assert is_bayer("") is False
    assert is_bayer("MONO") is False


def test_green_sublattice_halves_both_dimensions():
    pixels = np.arange(8 * 6, dtype=np.float64).reshape(8, 6)
    green = extract_green_sublattice(pixels, "RGGB")
    assert green.shape == (4, 3)


def test_rggb_picks_the_green_at_row0_col1():
    # In RGGB il 2x2 e' [[R, G], [G, B]]: il verde della prima riga sta a (0, 1).
    pixels = np.zeros((4, 4), dtype=np.float64)
    pixels[0, 1] = 10.0
    pixels[0, 3] = 20.0
    pixels[2, 1] = 30.0
    pixels[2, 3] = 40.0
    green = extract_green_sublattice(pixels, "RGGB")
    assert green.tolist() == [[10.0, 20.0], [30.0, 40.0]]


def test_bggr_picks_the_same_offset_as_rggb():
    # In BGGR il 2x2 e' [[B, G], [G, R]]: il verde di riga 0 sta di nuovo a (0, 1).
    pixels = np.zeros((4, 4), dtype=np.float64)
    pixels[0, 1] = 7.0
    green = extract_green_sublattice(pixels, "BGGR")
    assert green[0, 0] == 7.0


def test_grbg_picks_the_green_at_row0_col0():
    # In GRBG il 2x2 e' [[G, R], [B, G]]: il verde di riga 0 sta a (0, 0).
    pixels = np.zeros((4, 4), dtype=np.float64)
    pixels[0, 0] = 5.0
    green = extract_green_sublattice(pixels, "GRBG")
    assert green[0, 0] == 5.0


def test_unknown_pattern_raises():
    with pytest.raises(ValueError, match="pattern"):
        extract_green_sublattice(np.zeros((4, 4)), "XXXX")


def test_scale_factor_is_two():
    assert GREEN_SUBLATTICE_SCALE_FACTOR == 2.0
