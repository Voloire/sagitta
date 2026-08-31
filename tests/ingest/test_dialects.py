from sagitta.ingest.dialects import apply_dialect, detect_dialect, load_dialects


def test_generic_dialect_always_available():
    dialects = load_dialects()
    assert "generic" in dialects
    assert "nina" in dialects
    assert "asiair" in dialects


def test_detect_nina_from_software_keyword():
    header = {"SWCREATE": "N.I.N.A. 3.1.2.9001", "EXPTIME": 300.0}
    assert detect_dialect(header) == "nina"


def test_detect_asiair():
    header = {"SWCREATE": "ASIAIR V2.1", "EXPOSURE": 120.0}
    assert detect_dialect(header) == "asiair"


def test_unknown_software_falls_back_to_generic():
    header = {"SWCREATE": "SoftwareMaiVisto 1.0"}
    assert detect_dialect(header) == "generic"


def test_apply_dialect_maps_canonical_fields():
    header = {
        "DATE-OBS": "2026-08-29T21:30:00",
        "EXPTIME": 300.0,
        "NAXIS1": 6248,
        "NAXIS2": 4176,
        "FILTER": "Ha",
        "XPIXSZ": 3.76,
        "FOCALLEN": 530.0,
        "GAIN": 100,
    }
    canonical, unknown = apply_dialect(header, "generic")
    assert canonical["exposure_s"] == 300.0
    assert canonical["width"] == 6248
    assert canonical["height"] == 4176
    assert canonical["filter_name"] == "Ha"
    assert canonical["pixel_size_um"] == 3.76
    assert canonical["focal_length_mm"] == 530.0
    assert canonical["gain"] == 100
    assert unknown == {}


def test_apply_dialect_collects_unknown_keywords():
    header = {"EXPTIME": 60.0, "PIPPO": "qualcosa"}
    canonical, unknown = apply_dialect(header, "generic")
    assert canonical["exposure_s"] == 60.0
    assert unknown == {"PIPPO": "qualcosa"}


def test_header_measured_values_are_never_mapped():
    """HFR e FWHM nell'header vanno ignorati, mai promossi a campo canonico."""
    header = {"EXPTIME": 60.0, "HFR": 2.31, "FWHM": 3.9}
    canonical, unknown = apply_dialect(header, "generic")
    assert "hfr" not in canonical
    assert "fwhm" not in canonical
    assert "HFR" not in unknown
    assert "FWHM" not in unknown


def test_altitude_is_mapped_from_centalt():
    header = {"EXPTIME": 300.0, "CENTALT": 24.3139376496665}
    canonical, unknown = apply_dialect(header, "generic")
    assert canonical["altitude_deg"] == 24.3139376496665
    assert "CENTALT" not in unknown


def test_header_airmass_is_never_mapped():
    """AIRMASS is redundant with the altitude and hides its own formula.

    Discarded for the same reason as HFR: a number another program computed
    with an undeclared method must not enter the canonical metadata.
    """
    header = {"EXPTIME": 300.0, "CENTALT": 40.0, "AIRMASS": 1.55}
    canonical, unknown = apply_dialect(header, "generic")
    assert "airmass" not in canonical
    assert "AIRMASS" not in unknown
