# Findings from Real Data — Input for Stage 0.2

**Date of the run:** 2026-08-29
**Material:** 20 PHD2 guide logs (2026-07-02 → 2026-08-13, 60 guiding sessions,
~56,600 Mount samples in August alone) and 27 raw subs measured with Sagitta 0.1.0.
**Rig:** Askar FRA400 at 400 mm, IMX585 mono at 1.50 arcsec/px, ASI120MM Mini guide
camera at 6.45 arcsec/px, Sky-Watcher AZ-EQ6 Pro via EQMOD.

This document records what real data taught us that the synthetic benchmark could not.
It is an input to planning, not a plan: each section states the evidence first and the
proposed change second, so a future reader can disagree with the change while keeping
the evidence.

Written in US English because that is the standing rule for this repository from
2026-08-29 onward, even though the surrounding documents still await Tasks 17 and 18.

---

## 0. Two results that validate the premise

Both are **negative results**, and that is precisely why they matter. Sagitta's claim is
that it separates causes rather than announcing that stars look bad. These are that claim
working, on data chosen by the sky rather than by us.

**Case A — flat guiding, degrading stars.** Night of 2026-07-27, Fish Head Nebula, 36
subs at 300 s. Guiding RMS was flat across the entire session: 1.02–1.32 arcsec, no trend,
sub by sub. Center eccentricity nonetheless climbed 0.26 → 0.45, with the position angle
wandering 66° / 117° / 107° / 76° / 52°. On the response curve of section 2, an
eccentricity of 0.45 would require roughly 4–5 arcsec of guiding error. The mount was
delivering 1.2. **Conclusion: not guiding.** Differential flexure between the 120 mm guide
scope and the main optics, or field rotation — two different remedies, neither of them a
PHD2 setting.

**Case B — bad guiding, unchanged stars.** Night of 2026-08-12, same target, same filter,
same night: EQMOD started with the Dec guide rate at 0.1× sidereal instead of 0.9×, and it
was corrected partway through. Eleven subs before the fix, twenty-two after.

| | RMS RA | RMS Dec | ecc center | ecc corners | FWHM px |
|---|---|---|---|---|---|
| Vel.DEC 0.1× (22:13–23:04) | 1.06 | **2.33–3.45** | 0.258–0.268 | 0.377–0.397 | 14.10 |
| Vel.DEC 0.9× (00:16–01:18) | 0.72 | **0.40–0.68** | 0.268–0.276 | 0.381–0.416 | 14.11 |

Guiding four to five times worse in Dec; star shape indistinguishable to the third
decimal. The arithmetic explains it: 3 arcsec RMS at 1.50 arcsec/px is 2 px of smear added
in quadrature to stars already 14 px across. **Conclusion: measurably bad, and harmless.**

Both cases belong in the README ahead of any feature list.

---

## 1. Background subtraction before second moments — priority one

**Evidence.** Measured FWHM was 14.10 px at 1.50 arcsec/px, i.e. 21 arcsec. That is
physically absurd. Worse, it is *stable*: 14.09–14.13 across ten subs, two different
nights, and a fourfold difference in guiding quality. Earlier exploratory runs had already
shown FWHM tracking the measurement window (22 / 14 / 8.7 / 6 px at cutout radius
16 / 10 / 6 / 4) instead of converging.

A number that wrong and that steady is not measuring stars. It is measuring the window.
Flux-weighted moments integrate every pixel in the cutout, so an unsubtracted pedestal
contributes a term that grows with window area and swamps the star.

**Note on scope:** the subs above were narrowband Ha. Background subtraction is therefore
**not** a broadband-only concern — the defect is fully present on the darkest data this
rig produces.

**Proposed change.** Estimate and subtract a local background before computing second
moments. Until this lands, `median_fwhm_px` should not be reported at all, or must carry
an explicit warning, because publishing a number that is wrong by a factor of five is
worse than publishing nothing.

Eccentricity and position angle are unaffected: both were stable across window sizes,
because a symmetric pedestal biases the two principal variances almost equally and largely
cancels in their ratio.

---

## 2. Express damage in units of the star, not in arcsec

**Evidence.** The night of 2026-08-05 handed us a free calibration sweep. Clouds rolled in
at 23:43 and guiding degraded continuously for the rest of the session, so a single night
produced a full response curve:

| RMS total (arcsec) | ecc center | stars detected |
|---|---|---|
| 0.6–1.2 | 0.22–0.24 | 2500–2900 |
| 6.2 | 0.53 | 1696 |
| 110 | 0.72 | 796 |
| 377 | 0.78 | 365 |
| 676 | 0.81 | 297 |
| 1057 | 0.80 | 284 |

Below roughly 3 arcsec the stars are indifferent; by 6 arcsec they are visibly damaged.

**But that threshold is an artifact of this rig's 1.50 arcsec/px.** Quoting "3 arcsec" as
a general number would be wrong on anybody else's setup and actively misleading on a
longer focal length.

**Proposed change.** Report guiding RMS as a fraction of the measured FWHM. That ratio is
scale-free, transfers to other rigs, and is the number a diagnostic classifier should
threshold on. It depends on section 1 landing first, since it needs a trustworthy FWHM.

**Caveat, to be stated in the code and the docs:** one night, one degradation event. The
curve is indicative, not established. It should be rebuilt from several nights before any
number derived from it is published as a threshold.

---

## 3. Eccentricity saturates near 0.80

**Evidence.** From the same sweep: 377 arcsec → 0.776, 676 → 0.813, 1057 → 0.804. The
metric stops responding above roughly 0.75 while the underlying damage keeps growing by
another factor of three.

This is inherent to `sqrt(1 - minor_var/major_var)`: the expression compresses hard as the
variance ratio approaches zero.

**Proposed change.** Report `axis_ratio` (minor/major) alongside `eccentricity`, and raise
an explicit saturation flag above ~0.75 so that no consumer treats a plateau as a
plateau in the physical quantity. `axis_ratio` also has the practical virtue of being the
number astrophotographers already reason about.

**Related, from an earlier correction in this session:** eccentricity is easy to misread.
0.26 corresponds to about 3% elongation — visually round. 0.45 is about 11% — still normal.
Whatever the report prints, it should make that mapping legible rather than leaving a bare
number that invites alarm.

---

## 4. Star count is the best failure detector we have, and it is already free

**Evidence.** Across the 08-05 collapse, detected star count fell 2900 → 284 and tracked
the failure more cleanly and monotonically than eccentricity, which saturated. The number
is already computed and already in the output; it simply is not treated as a headline.

**Proposed change.** Promote `n_stars` to a first-class reported quantity with a
per-configuration baseline, and flag large deviations from it.

**Important constraint discovered the same day.** The baseline must be per-configuration,
never global. Moving from IMX585 mono to an ASI2600MC Pro changes the sky area by 5.3×,
and a 3 nm dual-band filter passes roughly 6 nm total to what are continuum sources, so
stars become dramatically fainter. A star count that collapses because the filter changed
is not a fault, and a tool that cries wolf on a hardware change will be switched off.

---

## 5. The PHD2 join — three specifications learned the hard way

Implementing the join by hand for this analysis surfaced three requirements that a
from-scratch design would likely have missed:

1. **One file contains several guiding sessions.** Each `Guiding Begins at` line starts a
   new block with its own `t0`, and the frame `Time` column is seconds from that `t0`.
   Each block also re-declares `Pixel scale`, which can differ between blocks. Parsing a
   log as a single time series produces silent garbage. The 2026-07-27 file holds three
   blocks covering two different targets.
2. **`DATE-OBS` is UTC; the guide log is local time.** The join needs an explicit offset,
   and it must be declared rather than guessed. This is exactly what the `assume_utc`
   guard in the ingest layer exists to protect, and it is why that guard raises instead of
   defaulting.
3. **Sample-rate collapse is the most reliable failure signal in the whole archive.** A
   healthy session yields ~510 Mount rows per 10 minutes at 1 s exposure. Both
   "disasters" in twenty nights showed the count falling to under 100 while the reported
   distances exploded — clouds on 08-05, dawn on 08-13. Neither was bad seeing, and
   neither was a mount problem. Any join should compute samples-per-unit-time and surface
   it, because it distinguishes "the sky closed" from "the rig misbehaved," and those look
   identical in an RMS number.

A corollary worth encoding: **whole-session RMS is a misleading summary.** The 08-13
second block scores 7.36 arcsec overall, which reads as a bad night. It was an excellent
night (0.66–0.87) with a twenty-minute failure at the end. Report windowed statistics, not
a single aggregate.

---

## 6. A guide-rate guard nobody else ships

**Evidence.** PHD2 records, in each session header, the guide rate the mount declared:
`RA Guide Speed = 13.5 a-s/s, Dec Guide Speed = 13.5 a-s/s`. 13.5 arcsec/s is exactly
0.90× sidereal; 1.5 is 0.10×. Two sessions out of sixty show 1.5 in Dec.

**The failure mode is unusually nasty:**

- it quadruples the Dec error,
- it leaves **no trace whatsoever in the images** (see Case B in section 0),
- it lives in a single line of a log header that nobody reads,
- and on this rig EQMOD resets it at every mini-PC restart, so it is defeated only by an
  unbroken human ritual.

The "two out of sixty" figure is a **lower bound on the reset rate and an upper bound on
nothing**: the log only records the cases where the operator forgot to fix it before
guiding started. The true reset rate on this rig is every boot.

**Proposed change.** A cheap header check in the join: parse the declared guide rates,
convert to multiples of sidereal, and flag anything below roughly 0.5×. It costs one
regular expression, requires no image data, and catches a defect that is otherwise
invisible until months of subs have been taken.

---

## 7. The OSC guardrail — an open design question, not a decision

**Evidence.** Sagitta measures Bayer frames on a single green sub-lattice, without
interpolation, which is correct: demosaicing invents stellar shape. But the green
sub-lattice has double the native pitch, so `effective_pixel_factor = 2.0`, and the
sampling guardrail refuses above 2.5 arcsec/px.

Verified against the current code:

| Configuration | Effective scale | Shape metrics |
|---|---|---|
| IMX585 mono, FRA400 | 1.50 arcsec/px | allowed |
| ASI2600MC Pro, FRA400 | **3.88 arcsec/px** | **refused** |
| ASI2600MC Pro + 0.7× reducer | 5.54 arcsec/px | refused |

**The problem.** The ASI2600MC Pro is plausibly the most common sensor in amateur
astrophotography, and at a very common focal length Sagitta declines to say anything at
all. If the intended audience is global, this is not an edge case — it is the median user.

**The question, honestly open.** The ×2 model is unarguably right for FWHM, which is a
sampling-limited quantity. It may be too conservative for *shape*: second moments
integrate flux over tens of pixels, and eccentricity of a well-sampled-in-aggregate star
may survive a pitch that would destroy a FWHM estimate. Supporting evidence is that
eccentricity proved stable across cutout radii in real data while FWHM did not.

**This must be measured, not decided at a desk.** The proper experiment is to take mono
frames at a known scale, decimate them to simulate a green sub-lattice at 3.88 arcsec/px,
and compare recovered eccentricity against ground truth. If shape survives, the guardrail
should carry separate thresholds per metric rather than one verdict for all of them.

**One complication to fold in.** With a dual-band narrowband filter on an OSC sensor, the
green sub-lattice sees mostly OIII, because Ha at 656 nm falls where green pixels are
insensitive. Sagitta would therefore be measuring the weaker of the two bands. Any OSC
experiment must be run on the filter class the user actually owns.

---

## 8. Method note: harvest the bad nights

The single most useful dataset in this whole investigation was a night that failed
continuously. A session that degrades smoothly from good to catastrophic produces a full
response curve for free, with every confounding variable — optics, focus, target,
temperature, operator — held constant by construction.

This is worth keeping as a deliberate technique: when building or recalibrating a
threshold, look first for a night that broke slowly. Do not discard failed sessions.

---

## Ranked proposal for 0.2.0

| # | Change | Depends on | Evidence strength |
|---|---|---|---|
| 1 | Background subtraction before second moments | — | strong, reproduced across nights |
| 2 | `axis_ratio` + saturation flag above 0.75 | — | strong, single sweep |
| 3 | Guide-rate header guard | — | strong, mechanism understood |
| 4 | PHD2 join, per the three specs in section 5 | — | requirements verified by hand |
| 5 | `n_stars` promoted, with per-configuration baseline | — | strong |
| 6 | Damage in units of FWHM rather than arcsec | 1 | curve indicative only, needs more nights |
| 7 | Per-metric sampling guardrail for OSC | experiment | hypothesis only, must be measured |

Items 1–5 rest on evidence gathered here. Item 6 needs more nights before any number it
produces can be published. Item 7 is a hypothesis with a designed experiment attached and
no result yet — it must not be implemented on the strength of this document alone.
