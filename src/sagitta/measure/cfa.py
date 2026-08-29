"""Gestione delle sub a colori con matrice di Bayer.

Su una sub OSC grezza la forma stellare misurata e' un artefatto della
matrice: ogni canale campiona un pixel ogni due per riga e colonna, e la PSF
risulta deformata in modo dipendente dall'orientamento.

Si misura quindi su un solo sotto-reticolo verde, estratto SENZA
interpolazione. Non si usa una sub demosaicizzata: l'interpolazione del
demosaico arrotonda le stelle esattamente come fa la registrazione, e
falserebbe l'eccentricita' verso il basso.

Si prende un solo sotto-reticolo verde e non entrambi, perche' i due verdi
insieme formano un reticolo a quinconce e non una griglia regolare. Il prezzo
e' che il passo effettivo raddoppia in entrambi gli assi: da qui
GREEN_SUBLATTICE_SCALE_FACTOR, che va passato a evaluate_sampling.
"""

from __future__ import annotations

import numpy as np

GREEN_SUBLATTICE_SCALE_FACTOR = 2.0
"""Il sotto-reticolo verde ha passo doppio rispetto al pixel nativo."""

_BAYER_PATTERNS = {"RGGB", "BGGR", "GRBG", "GBRG"}

_GREEN_OFFSET = {
    "RGGB": (0, 1),
    "BGGR": (0, 1),
    "GRBG": (0, 0),
    "GBRG": (0, 0),
}


def is_bayer(pattern: str | None) -> bool:
    """Vero se la stringa e' un pattern di Bayer riconosciuto."""
    if not pattern:
        return False
    return pattern.strip().upper() in _BAYER_PATTERNS


def extract_green_sublattice(pixels: np.ndarray, pattern: str) -> np.ndarray:
    """Estrae un sotto-reticolo verde senza alcuna interpolazione.

    L'array risultante ha dimensioni (H // 2, W // 2) ed e' una griglia
    regolare, misurabile con lo stesso motore delle sub monocromatiche.
    """
    key = (pattern or "").strip().upper()
    if key not in _GREEN_OFFSET:
        raise ValueError(f"pattern di Bayer non riconosciuto: {pattern!r}")

    row_offset, col_offset = _GREEN_OFFSET[key]
    height, width = pixels.shape

    # Un campione ogni due, a partire dall'offset del verde. Il taglio a
    # (H // 2, W // 2) serve alle dimensioni dispari, dove lo slice con
    # offset 0 restituirebbe una riga o una colonna in piu' di quante ne
    # prometta la firma.
    view = pixels[row_offset::2, col_offset::2]
    return np.ascontiguousarray(view[: height // 2, : width // 2])
