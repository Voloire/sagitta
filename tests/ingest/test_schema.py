import datetime as dt

from sagitta.ingest.schema import FrameMeta


def _minimal() -> FrameMeta:
    return FrameMeta(
        path="/tmp/light_0001.fits",
        date_obs=dt.datetime(2026, 8, 29, 21, 30, 0, tzinfo=dt.UTC),
        exposure_s=300.0,
        width=6248,
        height=4176,
    )


def test_minimal_frame_has_optional_fields_none():
    meta = _minimal()
    assert meta.filter_name is None
    assert meta.focal_length_mm is None
    assert meta.pixel_size_um is None
    assert meta.bayer_pattern is None
    assert meta.frame_kind == "unknown"


def test_date_obs_must_be_timezone_aware():
    naive = dt.datetime(2026, 8, 29, 21, 30, 0)
    try:
        FrameMeta(
            path="/tmp/a.fits",
            date_obs=naive,
            exposure_s=300.0,
            width=100,
            height=100,
        )
    except ValueError as exc:
        assert "timezone" in str(exc).lower()
    else:
        raise AssertionError("era attesa una ValueError su datetime naive")


def test_only_raw_frames_are_usable_for_shape():
    raw = _minimal()
    assert raw.is_usable_for_shape() is True

    registered = _minimal()
    registered.frame_kind = "registered"
    assert registered.is_usable_for_shape() is False

    calibrated = _minimal()
    calibrated.frame_kind = "calibrated"
    assert calibrated.is_usable_for_shape() is False
