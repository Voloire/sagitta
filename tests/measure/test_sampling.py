import datetime as dt

import pytest

from sagitta.ingest.schema import FrameMeta
from sagitta.measure.sampling import (
    MAX_SCALE_ARCSEC,
    evaluate_sampling,
    pixel_scale_arcsec,
)


def _meta(pixel_size_um=3.76, focal_length_mm=530.0, binning=1) -> FrameMeta:
    return FrameMeta(
        path="/tmp/x.fits",
        date_obs=dt.datetime(2026, 8, 29, 21, 0, tzinfo=dt.UTC),
        exposure_s=300.0,
        width=100,
        height=100,
        pixel_size_um=pixel_size_um,
        focal_length_mm=focal_length_mm,
        binning=binning,
    )


def test_pixel_scale_known_value():
    # 206.265 * 3.76 / 530 = 1.4632...
    assert pixel_scale_arcsec(3.76, 530.0) == pytest.approx(1.4633, abs=1e-3)


def test_pixel_scale_scales_with_binning():
    single = pixel_scale_arcsec(3.76, 530.0, binning=1)
    double = pixel_scale_arcsec(3.76, 530.0, binning=2)
    assert double == pytest.approx(2 * single, rel=1e-9)


def test_well_sampled_frame_allows_shape_metrics():
    verdict = evaluate_sampling(_meta())
    assert verdict.shape_metrics_allowed is True
    assert verdict.scale_arcsec == pytest.approx(1.4633, abs=1e-3)


def test_undersampled_frame_refuses_shape_metrics():
    # 3.76 um su 200 mm = 3.88 arcsec/px, ben oltre la soglia
    verdict = evaluate_sampling(_meta(focal_length_mm=200.0))
    assert verdict.shape_metrics_allowed is False
    assert "campionamento" in verdict.reason.lower()
    assert str(MAX_SCALE_ARCSEC) in verdict.reason


def test_missing_optics_data_refuses_and_says_so():
    meta = _meta()
    meta.focal_length_mm = None
    verdict = evaluate_sampling(meta)
    assert verdict.shape_metrics_allowed is False
    assert verdict.scale_arcsec is None
    assert "focale" in verdict.reason.lower()


def test_effective_pixel_factor_applies_for_osc():
    """Su OSC il sotto-reticolo verde raddoppia la scala effettiva."""
    mono = evaluate_sampling(_meta(), effective_pixel_factor=1.0)
    osc = evaluate_sampling(_meta(), effective_pixel_factor=2.0)
    assert osc.scale_arcsec == pytest.approx(2 * mono.scale_arcsec, rel=1e-9)
