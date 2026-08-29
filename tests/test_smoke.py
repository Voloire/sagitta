"""Smoke test end-to-end.

Esercita il programma come lo esercita un utente: lancia l'eseguibile
installato in un sottoprocesso e legge il JSON da stdout. Non importa nulla
dal package se non per fabbricare il file di input.

Copre cio' che nessun test unitario copre: che il packaging funzioni, che
l'entry point esista, che il JSON sia valido e che i campi del contratto ci
siano davvero.
"""

import json
import subprocess
import sys

import pytest

from sagitta.synth.generator import Truth, generate_frame, write_synthetic_fits

pytestmark = pytest.mark.smoke


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sagitta.cli", *args],
        capture_output=True,
        text=True,
        timeout=180,
    )


@pytest.fixture
def synthetic_light(tmp_path):
    pixels = generate_frame(
        1400, 1400, Truth(seeing_sigma_px=2.0, spacing_error=2.0), n_stars=700, seed=1
    )
    return write_synthetic_fits(tmp_path / "light_0001.fits", pixels)


def test_cli_measures_a_frame_and_emits_valid_json(synthetic_light):
    result = _run_cli("measure", str(synthetic_light))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert isinstance(payload, list)
    assert len(payload) == 1

    frame = payload[0]
    for key in ("path", "date_obs", "exposure_s", "sampling", "n_stars", "zones", "refusals"):
        assert key in frame, f"campo mancante nel contratto JSON: {key}"

    assert frame["n_stars"] > 300
    assert frame["sampling"]["shape_metrics_allowed"] is True
    assert set(frame["zones"]) == {
        "center",
        "mid",
        "corner_tl",
        "corner_tr",
        "corner_bl",
        "corner_br",
    }
    assert frame["zones"]["center"]["median_fwhm_px"] > 0


def test_cli_measures_multiple_frames(tmp_path, synthetic_light):
    second = write_synthetic_fits(
        tmp_path / "light_0002.fits",
        generate_frame(1400, 1400, Truth(seeing_sigma_px=2.4), n_stars=700, seed=2),
    )
    result = _run_cli("measure", str(synthetic_light), str(second))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload) == 2


def test_cli_reports_unreadable_file_without_crashing(tmp_path):
    broken = tmp_path / "non_e_un_fits.fits"
    broken.write_text("questo non e' un FITS")

    result = _run_cli("measure", str(broken))

    # Un file illeggibile e' un esito previsto, non un crash: esce 0 e lo dice.
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "error" in payload[0]


def test_cli_without_arguments_exits_nonzero_and_explains():
    result = _run_cli()
    assert result.returncode != 0
    assert "measure" in (result.stderr + result.stdout)
