from pathlib import Path

import numpy as np
import pytest
from astropy.io import fits


@pytest.fixture
def write_fits(tmp_path: Path):
    """Scrive un FITS di test e ne restituisce il percorso."""

    def _write(name: str, data: np.ndarray, header_cards: dict) -> Path:
        hdu = fits.PrimaryHDU(data.astype(np.float32))
        for key, value in header_cards.items():
            hdu.header[key] = value
        path = tmp_path / name
        hdu.writeto(path, overwrite=True)
        return path

    return _write
