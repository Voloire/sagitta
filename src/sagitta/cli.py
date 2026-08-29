"""Interfaccia a riga di comando di Sagitta.

In questo stadio espone solo la misura di un frame, con output JSON.
Nessuna diagnosi, nessuna attribuzione causale: solo numeri e rifiuti.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from sagitta import __version__
from sagitta.measure.frame import measure_frame


def _measurement_to_dict(result) -> dict:
    return {
        "path": result.meta.path,
        "date_obs": result.meta.date_obs.isoformat(),
        "exposure_s": result.meta.exposure_s,
        "filter": result.meta.filter_name,
        "sampling": asdict(result.sampling),
        "n_stars": result.n_stars,
        "zones": {name: asdict(stats) for name, stats in result.zones.items()},
        "refusals": result.refusals,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sagitta",
        description="Misura della forma stellare per zona del campo.",
    )
    parser.add_argument("--version", action="version", version=f"sagitta {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    measure = subparsers.add_parser("measure", help="misura uno o piu' frame")
    measure.add_argument("paths", nargs="+", type=Path)

    args = parser.parse_args(argv)

    if args.command == "measure":
        output = []
        for path in args.paths:
            try:
                output.append(_measurement_to_dict(measure_frame(path)))
            except (ValueError, OSError) as exc:
                output.append({"path": str(path), "error": str(exc)})
        json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
