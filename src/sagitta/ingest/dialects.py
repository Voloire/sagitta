"""Normalizzazione dei dialetti di header FITS verso lo schema canonico.

Le mappe vivono in file YAML versionati nel repository, non sono generate a
runtime. Aggiungere il supporto a un software di acquisizione significa
aggiungere un file YAML, ed e' un contributo che la community puo' mandare
come pull request.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DIALECTS_DIR = Path(__file__).resolve().parent.parent / "dialects"


@dataclass
class Dialect:
    name: str
    software_contains: list[str] = field(default_factory=list)
    map: dict[str, list[str]] = field(default_factory=dict)
    ignore: list[str] = field(default_factory=list)
    date_obs_is_utc: bool = True
    date_obs_at_midpoint: bool = False


@functools.lru_cache(maxsize=1)
def load_dialects() -> dict[str, Dialect]:
    """Carica tutti i dialetti da disco. Il risultato e' in cache."""
    raw: dict[str, dict] = {}
    for path in sorted(DIALECTS_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        raw[data["name"]] = data

    resolved: dict[str, Dialect] = {}
    for name, data in raw.items():
        merged_map: dict[str, list[str]] = {}
        ignore: list[str] = []
        parent_name = data.get("inherits")
        if parent_name:
            parent = raw[parent_name]
            merged_map.update(parent.get("map", {}))
            ignore.extend(parent.get("ignore", []))
        merged_map.update(data.get("map", {}))
        ignore.extend(data.get("ignore", []))

        resolved[name] = Dialect(
            name=name,
            software_contains=data.get("match", {}).get("software_contains", []),
            map=merged_map,
            ignore=sorted(set(ignore)),
            date_obs_is_utc=data.get("date_obs_is_utc", True),
            date_obs_at_midpoint=data.get("date_obs_at_midpoint", False),
        )
    return resolved


def detect_dialect(header: dict) -> str:
    """Identifica il dialetto dal software di acquisizione.

    Restituisce "generic" se nessun dialetto specifico corrisponde.
    """
    software = ""
    for key in ("SWCREATE", "PROGRAM", "CREATOR"):
        value = header.get(key)
        if isinstance(value, str) and value.strip():
            software = value
            break

    for name, dialect in load_dialects().items():
        if name == "generic":
            continue
        for token in dialect.software_contains:
            if token.lower() in software.lower():
                return name
    return "generic"


def apply_dialect(header: dict, dialect_name: str) -> tuple[dict[str, object], dict[str, object]]:
    """Traduce un header grezzo in campi canonici piu' keyword sconosciute.

    Le keyword nella lista `ignore` del dialetto non finiscono ne' fra i campi
    canonici ne' fra le sconosciute: sono scartate di proposito. E' il caso di
    HFR e FWHM, che sono incomparabili tra software e vanno rimisurati.
    """
    dialect = load_dialects()[dialect_name]

    canonical: dict[str, object] = {}
    consumed: set[str] = set()

    for canonical_name, candidates in dialect.map.items():
        for keyword in candidates:
            if keyword in header:
                canonical[canonical_name] = header[keyword]
                consumed.add(keyword)
                break

    structural = {"SIMPLE", "BITPIX", "NAXIS", "EXTEND", "END", "COMMENT", "HISTORY"}
    unknown = {
        key: value
        for key, value in header.items()
        if key not in consumed and key not in dialect.ignore and key not in structural
    }
    return canonical, unknown
