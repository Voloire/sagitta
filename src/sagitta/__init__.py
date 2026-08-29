"""Sagitta: referto forense e banco di prova per astrofotografia."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("sagitta")
except PackageNotFoundError:  # eseguito da sorgente, senza installazione
    __version__ = "0.0.0"

__all__ = ["__version__"]
