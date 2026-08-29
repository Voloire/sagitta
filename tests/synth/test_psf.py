import numpy as np
import pytest

from sagitta.synth.psf import render_gaussian


def test_renders_flux_at_the_requested_position():
    image = np.zeros((100, 100))
    render_gaussian(
        image, cx=30.0, cy=70.0, sigma_major=2.0, sigma_minor=2.0, theta_deg=0.0, amplitude=100.0
    )
    peak_y, peak_x = np.unravel_index(np.argmax(image), image.shape)
    assert peak_x == 30
    assert peak_y == 70


def test_circular_star_is_symmetric():
    image = np.zeros((60, 60))
    render_gaussian(image, 30.0, 30.0, 3.0, 3.0, 0.0, 100.0)
    assert image[30, 20] == pytest.approx(image[20, 30], rel=1e-6)


def test_elongated_star_is_wider_along_the_major_axis():
    image = np.zeros((60, 60))
    render_gaussian(
        image, 30.0, 30.0, sigma_major=5.0, sigma_minor=2.0, theta_deg=0.0, amplitude=100.0
    )
    # theta 0 -> asse maggiore lungo x
    assert image[30, 24] > image[24, 30]


def test_rotation_moves_the_major_axis():
    image = np.zeros((60, 60))
    render_gaussian(image, 30.0, 30.0, 5.0, 2.0, theta_deg=90.0, amplitude=100.0)
    assert image[24, 30] > image[30, 24]


def test_rendering_accumulates():
    image = np.zeros((60, 60))
    render_gaussian(image, 30.0, 30.0, 2.0, 2.0, 0.0, 100.0)
    first = image[30, 30]
    render_gaussian(image, 30.0, 30.0, 2.0, 2.0, 0.0, 100.0)
    assert image[30, 30] == pytest.approx(2 * first, rel=1e-9)
