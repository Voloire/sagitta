"""Generazione di sub sintetiche con aberrazione iniettata nota.

E' il sostituto della verita' di riferimento che non possediamo: qui la
risposta e' scritta dentro il dato, quindi si puo' verificare che la misura la
restituisca. Ogni causa ha una dipendenza spaziale diversa, ed e' esattamente
quella che il motore di misura deve saper distinguere.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from sagitta.synth.psf import render_gaussian

BACKGROUND_LEVEL = 100.0
BACKGROUND_NOISE = 2.0


@dataclass
class Truth:
    """Verita' iniettata in un frame sintetico.

    `tilt_x` e `tilt_y` si chiamano cosi' perche' qui sono verita' nota e non
    stima: e' l'unico posto del progetto in cui la parola e' ammessa.
    """

    seeing_sigma_px: float = 2.0
    spacing_error: float = 0.0
    tilt_x: float = 0.0
    tilt_y: float = 0.0
    guide_elongation: float = 0.0
    guide_angle_deg: float = 0.0
    field_rotation: float = 0.0


def _local_shape(truth: Truth, rx: float, ry: float) -> tuple[float, float, float]:
    """Assi e orientamento della PSF in una posizione normalizzata del campo.

    rx e ry vanno da -1 a +1 rispetto al centro.
    """
    radius = math.hypot(rx, ry)

    # componente radialmente simmetrica: spaziatura errata
    radial = truth.spacing_error * radius * radius
    # componente lineare: tilt, asimmetrica fra angoli opposti
    linear = truth.tilt_x * rx + truth.tilt_y * ry

    optical = max(0.0, radial + linear)

    sigma_major = truth.seeing_sigma_px + optical
    sigma_minor = truth.seeing_sigma_px + optical
    theta = 0.0

    # Rotazione di campo: allungamento tangenziale crescente col raggio.
    # Ha la precedenza sull'orientamento perche' e' l'unica firma con un
    # angolo che dipende dalla posizione.
    if truth.field_rotation > 0.0 and radius > 1e-6:
        sigma_major += truth.field_rotation * radius
        theta = math.degrees(math.atan2(ry, rx)) + 90.0
        if truth.guide_elongation > 0.0:
            sigma_major += truth.guide_elongation
        return sigma_major, sigma_minor, theta

    # Errore di guida: uniforme su tutto il campo, centro compreso,
    # con un angolo fisso identico ovunque.
    if truth.guide_elongation > 0.0:
        sigma_major += truth.guide_elongation
        theta = truth.guide_angle_deg

    return sigma_major, sigma_minor, theta


def generate_frame(
    width: int, height: int, truth: Truth, n_stars: int = 400, seed: int = 0
) -> np.ndarray:
    """Genera un frame sintetico con l'aberrazione descritta da `truth`."""
    rng = np.random.default_rng(seed)
    image = rng.normal(BACKGROUND_LEVEL, BACKGROUND_NOISE, size=(height, width))

    margin = 20
    xs = rng.uniform(margin, width - margin, size=n_stars)
    ys = rng.uniform(margin, height - margin, size=n_stars)
    amplitudes = rng.uniform(300.0, 3000.0, size=n_stars)

    for cx, cy, amplitude in zip(xs, ys, amplitudes, strict=True):
        rx = (cx - width / 2.0) / (width / 2.0)
        ry = (cy - height / 2.0) / (height / 2.0)
        sigma_major, sigma_minor, theta = _local_shape(truth, rx, ry)
        render_gaussian(image, cx, cy, sigma_major, sigma_minor, theta, amplitude)

    return image


def write_synthetic_fits(
    path: Path,
    pixels: np.ndarray,
    pixel_size_um: float = 3.76,
    focal_length_mm: float = 530.0,
) -> Path:
    """Salva un frame sintetico come FITS con header minimo ma sufficiente."""
    from astropy.io import fits

    hdu = fits.PrimaryHDU(pixels.astype(np.float32))
    hdu.header["DATE-OBS"] = "2026-08-29T21:30:00"
    hdu.header["EXPTIME"] = 300.0
    hdu.header["XPIXSZ"] = pixel_size_um
    hdu.header["FOCALLEN"] = focal_length_mm
    hdu.header["SWCREATE"] = "sagitta-synth"
    path = Path(path)
    hdu.writeto(path, overwrite=True)
    return path
