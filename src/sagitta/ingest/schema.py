"""Schema canonico dei metadati di un frame.

Unica struttura di metadati che attraversa il sistema. Ogni dialetto di header
viene normalizzato in questa forma prima di qualunque elaborazione.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Literal

FrameKind = Literal["raw", "calibrated", "registered", "unknown"]


@dataclass
class FrameMeta:
    """Metadati canonici di un singolo frame.

    Nota: i campi HFR/FWHM eventualmente presenti nell'header originale NON
    sono rappresentati qui di proposito. Sono incomparabili tra software e
    vanno sempre rimisurati dal motore interno.
    """

    path: str
    date_obs: dt.datetime
    exposure_s: float
    width: int
    height: int

    filter_name: str | None = None
    binning: int | None = None
    gain: float | None = None
    offset: float | None = None
    sensor_temp_c: float | None = None
    ambient_temp_c: float | None = None
    pixel_size_um: float | None = None
    focal_length_mm: float | None = None
    site_latitude_deg: float | None = None
    site_longitude_deg: float | None = None
    pointing_ra_deg: float | None = None
    pointing_dec_deg: float | None = None
    rotation_deg: float | None = None
    telescope: str | None = None
    instrument: str | None = None
    software: str | None = None
    bayer_pattern: str | None = None

    frame_kind: FrameKind = "unknown"
    unknown_keywords: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.date_obs.tzinfo is None:
            raise ValueError(
                "date_obs deve avere timezone: un istante naive rende "
                "impossibile il join con i log di guida"
            )
        if self.exposure_s <= 0:
            raise ValueError("exposure_s deve essere positiva")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width e height devono essere positive")

    def is_usable_for_shape(self) -> bool:
        """Solo le sub grezze entrano nelle metriche di forma.

        Calibrazione e registrazione alterano la PSF: l'interpolazione della
        registrazione arrotonda le stelle e abbassa sistematicamente
        l'eccentricita'. Includerle avvelena l'analisi in silenzio.
        """
        return self.frame_kind in ("raw", "unknown")
