"""Orchestrazione della misura di un singolo frame.

Unico modulo che conosce l'ordine delle operazioni: leggi, decidi se e' OSC,
valuta il campionamento, e solo se il campionamento lo consente misura la
forma. Il rifiuto e' un esito legittimo e viene sempre riportato.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from sagitta.ingest.fits_reader import read_frame
from sagitta.ingest.schema import FrameMeta
from sagitta.measure.cfa import (
    GREEN_SUBLATTICE_SCALE_FACTOR,
    extract_green_sublattice,
    is_bayer,
)
from sagitta.measure.detect import DetectionSettings, detect_stars
from sagitta.measure.sampling import SamplingVerdict, evaluate_sampling
from sagitta.measure.shape import StarShape
from sagitta.measure.zones import ZoneStats, summarize_zones


@dataclass
class FrameMeasurement:
    meta: FrameMeta
    sampling: SamplingVerdict
    n_stars: int
    zones: dict[str, ZoneStats]
    stars: list[StarShape] = field(default_factory=list)
    refusals: list[str] = field(default_factory=list)


def measure_frame(path: Path, settings: DetectionSettings | None = None) -> FrameMeasurement:
    """Misura un frame e restituisce statistiche per zona.

    Se il frame non e' utilizzabile per le metriche di forma, restituisce un
    risultato con zone vuote e il motivo del rifiuto.
    """
    meta, pixels = read_frame(Path(path))
    refusals: list[str] = []

    if not meta.is_usable_for_shape():
        refusals.append(
            f"Frame di tipo '{meta.frame_kind}': calibrazione e registrazione "
            f"alterano la forma stellare, metriche di forma non prodotte."
        )
        return FrameMeasurement(
            meta, SamplingVerdict(None, False, refusals[-1]), 0, {}, [], refusals
        )

    pixel_factor = 1.0
    if is_bayer(meta.bayer_pattern):
        pixels = extract_green_sublattice(pixels, meta.bayer_pattern or "")
        pixel_factor = GREEN_SUBLATTICE_SCALE_FACTOR

    sampling = evaluate_sampling(meta, effective_pixel_factor=pixel_factor)
    if not sampling.shape_metrics_allowed:
        refusals.append(sampling.reason)
        return FrameMeasurement(meta, sampling, 0, {}, [], refusals)

    stars = detect_stars(pixels, settings)
    height, width = pixels.shape
    zones = summarize_zones(stars, width, height)

    for name, stats in zones.items():
        if stats.median_eccentricity is None:
            refusals.append(
                f"Zona '{name}': solo {stats.n_stars} stelle usabili, "
                f"nessuna conclusione per questa zona."
            )

    return FrameMeasurement(meta, sampling, len(stars), zones, stars, refusals)
