"""Scala di campionamento e guardrail sulle metriche di forma.

Sotto un campionamento sufficiente, eccentricita' e angolo di posizione sono
quantizzati a rumore: una stella larga due pixel non ha una forma misurabile.
In quel caso Sagitta si rifiuta di rispondere invece di produrre un numero.
"""

from __future__ import annotations

from dataclasses import dataclass

from sagitta.ingest.schema import FrameMeta

ARCSEC_PER_RADIAN = 206264.806

MAX_SCALE_ARCSEC = 2.5
"""Soglia oltre la quale le metriche di forma non vengono prodotte."""


def pixel_scale_arcsec(pixel_size_um: float, focal_length_mm: float, binning: int = 1) -> float:
    """Scala in arcosecondi per pixel.

    scale = 206.265 * dimensione_pixel_um / focale_mm
    """
    if focal_length_mm <= 0:
        raise ValueError("focal_length_mm deve essere positiva")
    if pixel_size_um <= 0:
        raise ValueError("pixel_size_um deve essere positiva")
    binning = max(1, int(binning))
    return (ARCSEC_PER_RADIAN * pixel_size_um * binning) / (focal_length_mm * 1000.0)


@dataclass
class SamplingVerdict:
    scale_arcsec: float | None
    shape_metrics_allowed: bool
    reason: str


def evaluate_sampling(meta: FrameMeta, effective_pixel_factor: float = 1.0) -> SamplingVerdict:
    """Decide se le metriche di forma sono ammesse per questo frame.

    `effective_pixel_factor` vale 2.0 quando si misura su un sotto-reticolo
    verde di una matrice di Bayer, perche' il passo effettivo raddoppia.
    """
    if meta.pixel_size_um is None:
        return SamplingVerdict(
            None,
            False,
            "Dimensione del pixel assente nell'header: impossibile calcolare "
            "la scala, metriche di forma non prodotte.",
        )
    if meta.focal_length_mm is None:
        return SamplingVerdict(
            None,
            False,
            "Focale assente nell'header: impossibile calcolare la scala, "
            "metriche di forma non prodotte.",
        )

    scale = (
        pixel_scale_arcsec(meta.pixel_size_um, meta.focal_length_mm, meta.binning or 1)
        * effective_pixel_factor
    )

    if scale > MAX_SCALE_ARCSEC:
        return SamplingVerdict(
            scale,
            False,
            f"Campionamento insufficiente: {scale:.2f} arcsec/px, oltre la "
            f"soglia di {MAX_SCALE_ARCSEC} arcsec/px. Eccentricita' e angolo "
            f"sarebbero rumore quantizzato, quindi non vengono prodotti.",
        )

    return SamplingVerdict(scale, True, f"Campionamento adeguato: {scale:.2f} arcsec/px.")
