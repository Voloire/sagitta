"""Detection stellare e criteri di esclusione.

I criteri di esclusione contano piu' della fisica: dominano il risultato.
Una stella satura ha la cima piatta e un'eccentricita' casuale; un pixel caldo
sembra una stella perfetta; una stella tagliata dal bordo ha momenti falsati.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage

from sagitta.measure.shape import StarShape, measure_shape

MAD_TO_SIGMA = 1.4826
"""Fattore che converte la deviazione assoluta mediana in sigma gaussiana."""


@dataclass
class DetectionSettings:
    threshold_sigma: float = 5.0
    min_pixels: int = 5
    max_pixels: int = 2000
    cutout_radius: int = 10
    border_margin: int = 12
    max_flat_top_pixels: int = 3
    saturation_level: float | None = None


def estimate_background(pixels: np.ndarray) -> tuple[float, float]:
    """Fondo e rumore robusti: mediana e MAD riscalata.

    Si usano stimatori robusti perche' la media e la deviazione standard
    vengono trascinate dalle stelle stesse.
    """
    finite = pixels[np.isfinite(pixels)]
    median = float(np.median(finite))
    mad = float(np.median(np.abs(finite - median)))
    sigma = mad * MAD_TO_SIGMA
    if sigma <= 0.0:
        sigma = float(np.std(finite)) or 1.0
    return median, sigma


def detect_stars(pixels: np.ndarray, settings: DetectionSettings | None = None) -> list[StarShape]:
    """Trova le stelle usabili e ne misura la forma.

    Restituisce solo le stelle che superano tutti i criteri di esclusione.
    """
    cfg = settings or DetectionSettings()
    image = np.asarray(pixels, dtype=np.float64)
    height, width = image.shape

    median, sigma = estimate_background(image)
    threshold = median + cfg.threshold_sigma * sigma

    mask = image > threshold
    labels, count = ndimage.label(mask)
    if count == 0:
        return []

    objects = ndimage.find_objects(labels)
    stars: list[StarShape] = []

    for index, slices in enumerate(objects, start=1):
        if slices is None:
            continue
        blob = labels[slices] == index
        n_pixels = int(blob.sum())
        if n_pixels < cfg.min_pixels or n_pixels > cfg.max_pixels:
            continue

        values = image[slices][blob]
        peak = float(values.max())

        # Saturazione. Non si usa "il pixel piu' luminoso del frame per una
        # certa frazione": su un frame senza stelle sature quel criterio
        # scarta sempre la stella piu' luminosa, che e' proprio quella che
        # si vorrebbe misurare. La firma vera della saturazione e' la cima
        # piatta: molti pixel esattamente allo stesso valore massimo.
        if cfg.saturation_level is not None and peak >= cfg.saturation_level:
            continue
        flat_top = int(np.count_nonzero(values >= peak * (1.0 - 1e-6)))
        if flat_top > cfg.max_flat_top_pixels:
            continue

        y_slice, x_slice = slices
        cy = (y_slice.start + y_slice.stop - 1) / 2.0
        cx = (x_slice.start + x_slice.stop - 1) / 2.0

        if (
            cx < cfg.border_margin
            or cy < cfg.border_margin
            or cx >= width - cfg.border_margin
            or cy >= height - cfg.border_margin
        ):
            continue

        radius = cfg.cutout_radius
        x_start = int(round(cx)) - radius
        y_start = int(round(cy)) - radius
        cutout = image[
            y_start : y_start + 2 * radius + 1,
            x_start : x_start + 2 * radius + 1,
        ]
        if cutout.shape != (2 * radius + 1, 2 * radius + 1):
            continue

        shape = measure_shape(cutout - median, x_start, y_start)
        if shape is not None:
            stars.append(shape)

    return stars
