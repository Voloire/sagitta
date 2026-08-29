import numpy as np
import pytest

from sagitta.measure.frame import measure_frame


def _place_gaussian(image, cx, cy, sigma, amplitude=800.0):
    size = int(np.ceil(sigma * 6))
    yy, xx = np.mgrid[cy - size : cy + size + 1, cx - size : cx + size + 1]
    image[cy - size : cy + size + 1, cx - size : cx + size + 1] += amplitude * np.exp(
        -0.5 * (((xx - cx) / sigma) ** 2 + ((yy - cy) / sigma) ** 2)
    )


def _starfield(width=400, height=400, seed=7, sigma=2.0, step=20):
    rng = np.random.default_rng(seed)
    image = rng.normal(100.0, 2.0, size=(height, width))
    for cx in range(step, width - step, step):
        for cy in range(step, height - step, step):
            _place_gaussian(image, cx, cy, sigma)
    return image


def test_measures_stars_and_zones(write_fits):
    path = write_fits(
        "light.fits",
        _starfield().astype(np.float32),
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 300.0,
            "XPIXSZ": 3.76,
            "FOCALLEN": 530.0,
        },
    )
    result = measure_frame(path)

    assert result.sampling.shape_metrics_allowed is True
    assert result.n_stars > 30
    assert result.zones["center"].median_fwhm_px == pytest.approx(4.7, abs=1.0)
    assert result.refusals == []


def test_undersampled_frame_refuses_shape_metrics(write_fits):
    path = write_fits(
        "wide.fits",
        _starfield().astype(np.float32),
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 300.0,
            "XPIXSZ": 3.76,
            "FOCALLEN": 135.0,
        },
    )
    result = measure_frame(path)

    assert result.sampling.shape_metrics_allowed is False
    assert result.zones == {}
    assert result.stars == []
    assert any("campionamento" in r.lower() for r in result.refusals)


def test_osc_frame_is_measured_on_green_sublattice(write_fits):
    """Su OSC la misura avviene sul sotto-reticolo, quindi le dimensioni sono dimezzate."""
    image = _starfield(width=400, height=400, sigma=4.0, step=48)
    path = write_fits(
        "osc.fits",
        image.astype(np.float32),
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 120.0,
            "XPIXSZ": 1.5,
            "FOCALLEN": 530.0,
            "BAYERPAT": "RGGB",
        },
    )
    result = measure_frame(path)

    # 1.5 um su 530 mm = 0.58 arcsec/px, sul reticolo verde diventa 1.17
    assert result.sampling.scale_arcsec == pytest.approx(1.167, abs=0.02)
    assert result.sampling.shape_metrics_allowed is True
    assert all(star.x < 200 and star.y < 200 for star in result.stars)


def test_missing_focal_length_refuses_but_still_reports_metadata(write_fits):
    path = write_fits(
        "nofl.fits",
        _starfield().astype(np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 300.0, "XPIXSZ": 3.76},
    )
    result = measure_frame(path)

    assert result.sampling.shape_metrics_allowed is False
    assert result.meta.exposure_s == 300.0
    assert any("focale" in r.lower() for r in result.refusals)
