"""Misura della forma stellare tramite momenti secondi pesati sul flusso.

Si usano i momenti invece di un fit di PSF perche' non richiedono di scegliere
un modello (gaussiana, Moffat, e con quale beta), sono deterministici e non
hanno problemi di convergenza. Il prezzo e' una maggiore sensibilita' al
fondo: per questo il ritaglio deve arrivare qui gia' sottratto del fondo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

FWHM_PER_SIGMA = 2.0 * math.sqrt(2.0 * math.log(2.0))
"""Fattore di conversione da sigma gaussiana a FWHM: circa 2.3548."""


@dataclass
class StarShape:
    x: float
    y: float
    flux: float
    fwhm_px: float
    eccentricity: float
    position_angle_deg: float


def measure_shape(cutout: np.ndarray, x0: int, y0: int) -> StarShape | None:
    """Momenti secondi di un ritaglio gia' sottratto del fondo.

    `x0`, `y0` sono le coordinate nell'immagine intera del pixel in alto a
    sinistra del ritaglio, e vengono sommate al centroide.

    Restituisce None se il flusso totale non e' positivo o se i momenti
    risultano degeneri.
    """
    weights = np.clip(np.asarray(cutout, dtype=np.float64), 0.0, None)
    total = float(weights.sum())
    if total <= 0.0:
        return None

    height, width = weights.shape
    yy, xx = np.mgrid[0:height, 0:width]

    x_bar = float((weights * xx).sum() / total)
    y_bar = float((weights * yy).sum() / total)

    dx = xx - x_bar
    dy = yy - y_bar
    m_xx = float((weights * dx * dx).sum() / total)
    m_yy = float((weights * dy * dy).sum() / total)
    m_xy = float((weights * dx * dy).sum() / total)

    if m_xx <= 0.0 or m_yy <= 0.0:
        return None

    half_sum = (m_xx + m_yy) / 2.0
    half_diff = (m_xx - m_yy) / 2.0
    root = math.sqrt(half_diff * half_diff + m_xy * m_xy)

    major_var = half_sum + root
    minor_var = half_sum - root
    if major_var <= 0.0:
        return None
    minor_var = max(minor_var, 0.0)

    eccentricity = math.sqrt(max(0.0, 1.0 - minor_var / major_var))

    # sigma media geometrica dei due assi -> FWHM equivalente circolare
    sigma_equiv = math.sqrt(half_sum)
    fwhm = FWHM_PER_SIGMA * sigma_equiv

    angle_rad = 0.5 * math.atan2(2.0 * m_xy, m_xx - m_yy)
    angle_deg = math.degrees(angle_rad) % 180.0
    if angle_deg >= 180.0 - 1e-12:
        angle_deg = 0.0

    return StarShape(
        x=x_bar + x0,
        y=y_bar + y0,
        flux=total,
        fwhm_px=fwhm,
        eccentricity=eccentricity,
        position_angle_deg=angle_deg,
    )
