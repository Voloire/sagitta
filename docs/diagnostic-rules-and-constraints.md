# Diagnostic Rules and Product Constraints

**Decided 2026-08-29.** This document records constraints that are settled, not proposals
open for debate, plus the rule set that must replace human interpretation. It is written
to be read on its own: a future session with no memory of the conversation that produced
it should be able to act from this file alone.

Companion document: [`findings-from-real-data.md`](findings-from-real-data.md) holds the
evidence. This one holds the consequences.

---

## Part 1 — Non-negotiable constraints

### C1. Deterministic. No model at runtime, ever.

Same input produces the same output, always. No inference, no sampling, no temperature,
no API. The target user runs Windows with NINA, ASTAP and PHD2, and does not have a
frontier model available — nor should the tool require anyone to pay for one.

Current state, verified 2026-08-29: dependencies are `numpy`, `scipy`, `astropy`,
`PyYAML`. Nothing else. A test already asserts the absence of network access. This
constraint is therefore satisfied today and must never be traded away.

### C2. A single .exe on Windows.

Decided, not proposed. The audience does not run `pip install`. As long as Sagitta is a
Python package, its real reach is a fraction of its stated reach. Packaging is a product
problem, not a chore to defer.

Windows-only is already declared. This makes it real.

### C3. No network. Ever.

Already enforced by test. A tool that analyzes your images and talks to nobody is a
feature, not an omission. Keep it in the test suite as a hard gate.

### C4. The tool must be able to say "I don't know."

A classifier that always names a cause is a horoscope. The refusal path already exists in
the sampling guardrail; it must extend to diagnosis.

Worked example from real data, 2026-07-27: the correct verdict was *"not guiding — but
with one night's data I cannot separate differential flexure from field rotation."*
Printing either one of those two would have been a guess wearing a lab coat.

### C5. Every threshold ships with its derivation.

Not the number: the derivation. Which data, which procedure, which uncertainty.

This exists to defeat a specific failure mode. If a rule exists only because someone —
or something — derived it once, and nobody can re-derive it, then that deriver is a
**hidden dependency of the reasoning**, even when it appears nowhere in `pyproject.toml`.
The day somebody asks "why is the threshold 0.75?", the only honest answer must not be
"a machine said so, and it is gone."

A number a user can contest belongs to them. A number they can only accept still belongs
to whoever handed it over.

**Practical test:** an astrophotographer with a spreadsheet and the same logs must be able
to reproduce the threshold and disagree with it.

---

## Part 2 — Why these constraints exist

The gap that produced them was observed directly on 2026-08-29. Twenty guide logs and 27
subs were analyzed. **Sagitta produced the numbers; a human aided by a language model
produced the diagnosis.** A user with the identical archive would have received tables of
eccentricity and no answer.

That gap is the missing product. Filling it with a model would mean the tool only works
for people sitting next to one.

The distinction that keeps this honest is between a **build tool** and a **runtime
dependency**. Nobody ships the compiler, the IDE, or the documentation they read while
writing the code. If the output is deterministic Python grinding FITS files offline, then
whatever helped write it was scaffolding, not a component — provided C5 holds, because C5
is what stops the scaffolding from quietly becoming load-bearing.

The encouraging finding: **every diagnosis produced by hand that day reduces to
arithmetic.** None of it required intuition. It required rules that had not yet been
written down. They are written below.

---

## Part 3 — The rule set

Each rule states inputs, condition, verdict, and calibration status. A rule that is not
calibrated must not fire; it must report that it cannot yet decide. An uncalibrated rule
firing is worse than a silent one.

### R1 — Guiding excluded by trend divergence

- **Inputs:** per-sub center eccentricity, per-sub guiding RMS from the join.
- **Condition:** eccentricity rises across the session while RMS does not. Compare the
  median of the first quarter of the session against the last quarter, on both series,
  against a declared minimum delta. No p-values — a stated threshold on a stated
  comparison, so the user can redo it by hand.
- **Verdict:** *guiding is excluded as the cause of the elongation.* Does **not** name the
  actual cause: see C4.
- **Evidence:** 2026-07-27. RMS flat at 1.02–1.32 arcsec all night; center eccentricity
  0.26 → 0.45; position angle wandering 66° / 117° / 107° / 76° / 52°.
- **Status:** mechanism proven, delta threshold not yet calibrated.

### R2 — Guiding damage, in units of the star

- **Inputs:** windowed guiding RMS, measured FWHM (requires background subtraction to
  land first — see findings §1).
- **Condition:** `RMS_window / FWHM_measured > k`.
- **Verdict:** above `k`, guiding is a plausible contributor; below, it is excluded as a
  material cause.
- **Why a ratio:** the raw threshold observed on this rig (harmless below ~3 arcsec,
  visibly damaging by ~6) is an artifact of its 1.50 arcsec/px. Quoting it as an absolute
  would be wrong on any other focal length. The ratio transfers.
- **Evidence:** 2026-08-12 — Dec RMS 4–5× worse, star shape identical to the third
  decimal. 2026-08-05 — a continuous degradation sweep from 0.6 to 1057 arcsec.
- **Status:** `k` **unknown**. One night, one degradation event. Must not ship until
  rebuilt from several nights.

### R3 — The sky closed, not the rig

- **Inputs:** guide-log sample timestamps only. No image data needed.
- **Condition:** samples per minute below 50% of the session median.
- **Verdict:** frames were dropped. Subs in that window are marked *sky*, not *equipment*,
  and are excluded from equipment conclusions.
- **Evidence:** both catastrophes in twenty nights were this and nothing else — clouds on
  2026-08-05 at 23:43, dawn on 2026-08-13 at 04:01. Healthy sessions yield ~510 Mount rows
  per 10 minutes at 1 s exposure; both failures fell below 100 while reported distances
  exploded.
- **Status:** ready. Pure counting, and the most reliable signal in the entire archive.

### R4 — Guide rate misconfigured

- **Inputs:** the PHD2 session header line
  `RA Guide Speed = X a-s/s, Dec Guide Speed = Y a-s/s`.
- **Condition:** `Y / 15.041 < 0.5` (sidereal is 15.041 arcsec/s).
- **Verdict:** the mount was handed a guide rate too low to correct properly.
- **Why it matters:** this failure quadruples Dec error, leaves **no trace whatsoever in
  the images**, and lives in one header line nobody reads. On the reference rig, EQMOD
  resets it to 0.1× at every mini-PC restart and does not persist the correction, so it is
  defeated only by an unbroken human ritual.
- **Status:** ready. One regular expression.

### R5 — Polar drift

- **Inputs:** guide-log Dec raw distance.
- **Condition:** split the session into 10-minute windows, take the mean Dec error per
  window, count sign agreement. High agreement plus growing magnitude indicates
  systematic drift rather than seeing.
- **Verdict:** *polar alignment* as a candidate; a mid-session sign flip **excludes** it
  and points at flexure or a target change instead.
- **Evidence:** 2026-07-29, 41 of 41 windows positive, +0.76 → +1.26 arcsec. Contrast
  2026-08-06 and 2026-08-13, both of which flip sign mid-session.
- **Status:** mechanism proven, agreement threshold not calibrated.

### R6 — Field geometry

- **Inputs:** the zone table Sagitta already produces.
- **Conditions and verdicts**, as already specified in `design.md`:
  uniform elongation with a fixed angle, center included → guiding;
  radial and equal across the four corners → corrector spacing;
  asymmetry between opposite corners → field aberration;
  tangential with angle depending on position → field rotation.
- **Status:** deterministic geometry by construction; thresholds for "equal" and
  "asymmetric" not yet fixed.

### R7 — Metric saturation refusal

- **Inputs:** measured eccentricity.
- **Condition:** above ~0.75.
- **Verdict:** refuse to rank or compare. The metric has stopped responding.
- **Evidence:** 2026-08-05 sweep — 377 arcsec → 0.776, 676 → 0.813, 1057 → 0.804. Damage
  grew threefold while the number did not move.
- **Status:** ready once `axis_ratio` exists alongside it.

---

## Part 4 — Calibration status, at a glance

| Rule | Mechanism | Threshold | May ship |
|---|---|---|---|
| R3 sky closed | proven | fixed (50% of median) | **yes** |
| R4 guide rate | proven | fixed (0.5× sidereal) | **yes** |
| R7 saturation | proven | fixed (~0.75) | yes, after `axis_ratio` |
| R1 guiding excluded | proven | not calibrated | no |
| R5 polar drift | proven | not calibrated | no |
| R6 field geometry | by construction | not calibrated | no |
| R2 damage ratio | proven | `k` unknown | no |

Three rules are ready today. Four need calibration data before they are allowed to speak.
**Shipping an uncalibrated rule is the failure mode this table exists to prevent.**

---

## Part 5 — Distribution and the surrounding stack

**The .exe** is the gating item for reach (C2).

**ASTAP is an open question, deliberately unresolved.** Every user in this stack already
has it, it has a command-line interface, and plate solving would give the true pixel scale
instead of trusting `FOCALLEN` in the header — a real robustness gain. Against that: it
introduces an external dependency into a toolchain that is currently self-sufficient. This
should be decided with a stated reason, not adopted for convenience.

**NINA** writes the headers Sagitta reads and owns the folder layout
(`<object>\<date>\LIGHT`). A NINA plugin would mean C#/.NET and is out of scope for now;
reading its output is not.

**PHD2** supplies the guide logs. Three parsing requirements found the hard way are
recorded in `findings-from-real-data.md` §5 and must not be rediscovered: multiple
`Guiding Begins` blocks per file each with independent `t0` **and** pixel scale;
`DATE-OBS` in UTC against a log in local time; and whole-session RMS being a misleading
summary — report windowed statistics, never a single aggregate.

---

## Part 6 — What the report must show

Consequence of C4 and C5, and the piece that replaces the spoken explanation a user will
not have:

- **which rule fired**, on **which number**, against **which threshold**;
- which rules were evaluated and did **not** fire;
- which rules could not be evaluated, and what data was missing;
- explicit refusal where the data does not support a verdict.

Without this the user has an oracle, not an instrument. The whole point of a deterministic
diagnosis is that it can be checked — and a verdict nobody can check is no better than a
model's guess, only slower.
