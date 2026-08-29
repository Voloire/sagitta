"""Lettura di file FITS. Unico punto del progetto che tocca astropy."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
from astropy.io import fits

from sagitta.ingest.dialects import apply_dialect, detect_dialect, load_dialects
from sagitta.ingest.schema import FrameMeta


def _parse_date_obs(value: str, assume_utc: bool) -> dt.datetime:
    """Interpreta DATE-OBS. Senza timezone esplicita si assume UTC solo se
    il dialetto lo dichiara; altrimenti l'istante ambiguo viene rifiutato.

    L'assunzione va dichiarata all'utente: e' la sorgente di errore piu'
    comune nel join con i log di guida, specie nella notte del cambio ora.
    """
    text = value.strip().replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        if not assume_utc:
            raise ValueError(
                f"DATE-OBS {value!r} has no timezone and the dialect does not "
                "declare one: the instant is ambiguous, and guessing it would "
                "silently poison the join with the guiding logs"
            )
        parsed = parsed.replace(tzinfo=dt.UTC)
    return parsed


def read_frame(path: Path) -> tuple[FrameMeta, np.ndarray]:
    """Legge un FITS e restituisce metadati canonici piu' i pixel in float64."""
    path = Path(path)
    with fits.open(path, memmap=False) as hdul:
        hdu = next(h for h in hdul if h.data is not None)
        raw_header = {key: hdu.header[key] for key in hdu.header if key}
        pixels = np.asarray(hdu.data, dtype=np.float64)

    if pixels.ndim != 2:
        raise ValueError(f"{path.name}: attesa immagine 2D, trovate {pixels.ndim} dimensioni")

    dialect_name = detect_dialect(raw_header)
    dialect = load_dialects()[dialect_name]
    canonical, unknown = apply_dialect(raw_header, dialect_name)

    date_obs_raw = canonical.get("date_obs")
    if not isinstance(date_obs_raw, str):
        raise ValueError(f"{path.name}: DATE-OBS mancante o non testuale")
    date_obs = _parse_date_obs(date_obs_raw, dialect.date_obs_is_utc)

    exposure_s = float(canonical["exposure_s"])
    if dialect.date_obs_at_midpoint:
        date_obs = date_obs - dt.timedelta(seconds=exposure_s / 2.0)

    height, width = pixels.shape

    def _opt_float(key: str) -> float | None:
        value = canonical.get(key)
        return float(value) if value is not None else None

    def _opt_str(key: str) -> str | None:
        value = canonical.get(key)
        return str(value).strip() if value is not None else None

    meta = FrameMeta(
        path=str(path),
        date_obs=date_obs,
        exposure_s=exposure_s,
        width=width,
        height=height,
        filter_name=_opt_str("filter_name"),
        binning=int(canonical["binning"]) if canonical.get("binning") else None,
        gain=_opt_float("gain"),
        offset=_opt_float("offset"),
        sensor_temp_c=_opt_float("sensor_temp_c"),
        ambient_temp_c=_opt_float("ambient_temp_c"),
        pixel_size_um=_opt_float("pixel_size_um"),
        focal_length_mm=_opt_float("focal_length_mm"),
        site_latitude_deg=_opt_float("site_latitude_deg"),
        site_longitude_deg=_opt_float("site_longitude_deg"),
        pointing_ra_deg=_opt_float("pointing_ra_deg"),
        pointing_dec_deg=_opt_float("pointing_dec_deg"),
        rotation_deg=_opt_float("rotation_deg"),
        telescope=_opt_str("telescope"),
        instrument=_opt_str("instrument"),
        software=_opt_str("software"),
        bayer_pattern=_opt_str("bayer_pattern"),
        frame_kind="unknown",
        unknown_keywords=unknown,
    )
    return meta, pixels
