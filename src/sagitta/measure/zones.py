"""Stratificazione della misura per posizione nel campo.

Un singolo numero per frame non serve a niente: il discriminante fisico non e'
il valore medio dell'eccentricita' ma la sua dipendenza dalla posizione.
Un errore di inseguimento allunga le stelle in modo uniforme, centro compreso;
un'aberrazione del treno ottico e' nulla al centro e cresce verso i bordi.
Mediando su tutto il campo si butta via esattamente il segnale che serve.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from sagitta.measure.shape import StarShape

ZONE_NAMES = ("center", "mid", "corner_tl", "corner_tr", "corner_bl", "corner_br")

CENTER_MAX_RADIUS = 0.25
MID_MAX_RADIUS = 0.65


def normalized_radius(x: float, y: float, width: int, height: int) -> float:
    """Raggio normalizzato: 0 al centro, circa 1 negli angoli."""
    rx = (x - width / 2.0) / (width / 2.0)
    ry = (y - height / 2.0) / (height / 2.0)
    return math.hypot(rx, ry) / math.sqrt(2.0)


def zone_of(x: float, y: float, width: int, height: int) -> str:
    """Zona di appartenenza di una posizione nel campo."""
    radius = normalized_radius(x, y, width, height)
    if radius < CENTER_MAX_RADIUS:
        return "center"
    if radius < MID_MAX_RADIUS:
        return "mid"
    left = x < width / 2.0
    top = y < height / 2.0
    if top:
        return "corner_tl" if left else "corner_tr"
    return "corner_bl" if left else "corner_br"


@dataclass
class ZoneStats:
    zone: str
    n_stars: int
    median_fwhm_px: float | None
    median_eccentricity: float | None
    median_position_angle_deg: float | None


def _circular_median_angle(angles_deg: list[float]) -> float:
    """Mediana circolare per angoli definiti modulo 180 gradi.

    Un asse a 175 gradi e uno a 5 gradi distano 10 gradi, non 170. Si raddoppia
    l'angolo per portarlo su un cerchio intero, si media come vettore, si
    dimezza.
    """
    doubled = np.deg2rad(np.array(angles_deg) * 2.0)
    mean_vector = complex(np.cos(doubled).mean(), np.sin(doubled).mean())
    angle = math.degrees(math.atan2(mean_vector.imag, mean_vector.real)) / 2.0
    return angle % 180.0


def summarize_zones(
    stars: list[StarShape], width: int, height: int, min_stars: int = 8
) -> dict[str, ZoneStats]:
    """Statistiche per zona. Una zona con troppe poche stelle non conclude."""
    buckets: dict[str, list[StarShape]] = {name: [] for name in ZONE_NAMES}
    for star in stars:
        buckets[zone_of(star.x, star.y, width, height)].append(star)

    stats: dict[str, ZoneStats] = {}
    for name, members in buckets.items():
        if len(members) < min_stars:
            stats[name] = ZoneStats(name, len(members), None, None, None)
            continue
        stats[name] = ZoneStats(
            zone=name,
            n_stars=len(members),
            median_fwhm_px=float(np.median([s.fwhm_px for s in members])),
            median_eccentricity=float(np.median([s.eccentricity for s in members])),
            median_position_angle_deg=_circular_median_angle(
                [s.position_angle_deg for s in members]
            ),
        )
    return stats
