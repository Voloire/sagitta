"""Sky geometry derived from a frame's pointing.

Everything here is a pure function of numbers already in the canonical
metadata. Nothing in this module reads a file or trusts a value another
program computed.
"""

from __future__ import annotations

import math

AIRMASS_FORMULA = "Kasten & Young 1989"


def airmass_from_altitude(altitude_deg: float) -> float | None:
    """Relative air mass at a given apparent altitude, or None if undefined.

    Uses the Kasten & Young (1989) interpolation formula:

        X = 1 / (sin h + 0.50572 * (h + 6.07995) ** -1.6364)

    with `h` the altitude in degrees. It stays finite down to the horizon,
    where the plane-parallel `sec z` diverges and is already 0.5% wrong at
    24 degrees.

    We recompute rather than read the header's AIRMASS on purpose. That value
    carries no information beyond the altitude it was derived from, but it does
    carry an undeclared choice of formula: acquisition software variously
    writes Gueymard 1993, Kasten-Young, or plain `sec z`, and nothing in the
    file distinguishes them. Computing it here means the report can name the
    formula it used.

    Returns None outside [0, 90] degrees, and for non-finite input. Below the
    horizon there is no air mass to report, and inventing one would be a guess
    dressed as a measurement.

    Caveat on provenance, not on arithmetic: the altitude normally comes from
    the pointing the mount reported, not from an astrometric solution. A wrong
    pointing model propagates here silently.
    """
    if not math.isfinite(altitude_deg):
        return None
    if altitude_deg < 0.0 or altitude_deg > 90.0:
        return None
    denominator = (
        math.sin(math.radians(altitude_deg)) + 0.50572 * (altitude_deg + 6.07995) ** -1.6364
    )
    return 1.0 / denominator
