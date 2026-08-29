"""Resa di stelle gaussiane ellittiche su un'immagine sintetica.

Questo modulo non importa nulla da `measure`: la validazione deve essere
indipendente dal codice che valida, altrimenti e' circolare.
"""

from __future__ import annotations

import math

import numpy as np


def render_gaussian(
    image: np.ndarray,
    cx: float,
    cy: float,
    sigma_major: float,
    sigma_minor: float,
    theta_deg: float,
    amplitude: float,
) -> None:
    """Somma una gaussiana ellittica all'immagine, in place.

    `theta_deg` e' l'angolo dell'asse maggiore, misurato dall'asse x verso
    l'asse y, nella stessa convenzione usata da measure_shape.
    """
    radius = int(math.ceil(max(sigma_major, sigma_minor) * 4.0))
    x_min = max(0, int(cx) - radius)
    x_max = min(image.shape[1], int(cx) + radius + 1)
    y_min = max(0, int(cy) - radius)
    y_max = min(image.shape[0], int(cy) + radius + 1)
    if x_min >= x_max or y_min >= y_max:
        return

    yy, xx = np.mgrid[y_min:y_max, x_min:x_max]
    dx = xx - cx
    dy = yy - cy

    theta = math.radians(theta_deg)
    x_rot = dx * math.cos(theta) + dy * math.sin(theta)
    y_rot = -dx * math.sin(theta) + dy * math.cos(theta)

    image[y_min:y_max, x_min:x_max] += amplitude * np.exp(
        -0.5 * ((x_rot / sigma_major) ** 2 + (y_rot / sigma_minor) ** 2)
    )
