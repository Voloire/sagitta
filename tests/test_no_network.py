"""Dimostrazione eseguibile della promessa "tutto in locale".

Sabota la creazione di socket nella libreria standard e poi esegue l'intera
pipeline di misura. Se qualcuno un giorno introdurra' una chiamata di rete,
anche indiretta attraverso una dipendenza, questo test si rompe e la build
non passa.

E' l'unico controllo di sicurezza di questo progetto che verifica una
promessa fatta all'utente, invece di cercare difetti nel codice.
"""

import socket

import pytest

from sagitta.measure.frame import measure_frame
from sagitta.synth.generator import Truth, generate_frame, write_synthetic_fits


class NetworkAccessAttempted(AssertionError):
    pass


@pytest.fixture
def no_network(monkeypatch):
    def _forbidden(*args, **kwargs):
        raise NetworkAccessAttempted(
            "Sagitta ha tentato di aprire una connessione di rete. "
            "La spec lo vieta senza eccezioni: i dati dell'utente non "
            "lasciano la sua macchina."
        )

    monkeypatch.setattr(socket, "socket", _forbidden)
    monkeypatch.setattr(socket, "create_connection", _forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", _forbidden)


def test_measurement_pipeline_works_without_network(tmp_path, no_network):
    pixels = generate_frame(
        600, 600, Truth(seeing_sigma_px=2.0, spacing_error=2.0), n_stars=600, seed=9
    )
    path = write_synthetic_fits(tmp_path / "light.fits", pixels)

    result = measure_frame(path)

    assert result.n_stars > 100
    assert result.zones["center"].median_fwhm_px is not None


def test_the_guard_itself_works(no_network):
    """Se questo test non fallisce, il guard non sta guardando niente."""
    with pytest.raises(NetworkAccessAttempted):
        socket.socket()
