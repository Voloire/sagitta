import datetime as dt
from dataclasses import replace

import numpy as np
import pytest
from sagitta.ingest.fits_reader import read_frame

from sagitta.ingest.dialects import load_dialects


def test_reads_canonical_fields(write_fits):
    data = np.zeros((40, 60), dtype=np.float32)
    path = write_fits(
        "light.fits",
        data,
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 300.0,
            "FILTER": "Ha",
            "XPIXSZ": 3.76,
            "FOCALLEN": 530.0,
            "SWCREATE": "N.I.N.A. 3.1.2.9001",
        },
    )
    meta, pixels = read_frame(path)

    assert meta.exposure_s == 300.0
    assert meta.filter_name == "Ha"
    assert meta.pixel_size_um == 3.76
    assert meta.focal_length_mm == 530.0
    assert meta.software == "N.I.N.A. 3.1.2.9001"
    assert meta.width == 60
    assert meta.height == 40
    assert pixels.shape == (40, 60)
    assert pixels.dtype == np.float64


def test_date_obs_without_timezone_is_assumed_utc(write_fits):
    path = write_fits(
        "a.fits",
        np.zeros((10, 10), dtype=np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 60.0},
    )
    meta, _ = read_frame(path)
    assert meta.date_obs.tzinfo is dt.UTC
    assert meta.date_obs.hour == 21


def test_naive_date_obs_rejected_when_dialect_does_not_declare_timezone(write_fits, monkeypatch):
    path = write_fits(
        "naive-no-timezone.fits",
        np.zeros((10, 10), dtype=np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 60.0},
    )
    import sagitta.ingest.fits_reader as fits_reader

    dialects = load_dialects().copy()
    dialects["generic"] = replace(dialects["generic"], date_obs_is_utc=False)
    monkeypatch.setattr(fits_reader, "load_dialects", lambda: dialects)

    with pytest.raises(ValueError, match="does not declare"):
        read_frame(path)


def test_unknown_keywords_are_preserved(write_fits):
    path = write_fits(
        "b.fits",
        np.zeros((10, 10), dtype=np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 60.0, "PIPPO": "x"},
    )
    meta, _ = read_frame(path)
    assert meta.unknown_keywords["PIPPO"] == "x"


def test_header_hfr_is_discarded(write_fits):
    path = write_fits(
        "c.fits",
        np.zeros((10, 10), dtype=np.float32),
        {"DATE-OBS": "2026-08-29T21:30:00", "EXPTIME": 60.0, "HFR": 2.3},
    )
    meta, _ = read_frame(path)
    assert "HFR" not in meta.unknown_keywords


def test_bayer_pattern_is_read(write_fits):
    path = write_fits(
        "osc.fits",
        np.zeros((10, 10), dtype=np.float32),
        {
            "DATE-OBS": "2026-08-29T21:30:00",
            "EXPTIME": 60.0,
            "BAYERPAT": "RGGB",
        },
    )
    meta, _ = read_frame(path)
    assert meta.bayer_pattern == "RGGB"
