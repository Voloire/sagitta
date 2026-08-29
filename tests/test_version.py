import re
import subprocess
import sys
from importlib.metadata import version as metadata_version

import sagitta


def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", sagitta.__version__), sagitta.__version__


def test_version_comes_from_package_metadata():
    """Un numero di versione scritto due volte e' un numero che divergera'."""
    assert sagitta.__version__ == metadata_version("sagitta")


def test_cli_reports_the_same_version():
    result = subprocess.run(
        [sys.executable, "-m", "sagitta.cli", "--version"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert sagitta.__version__ in result.stdout
