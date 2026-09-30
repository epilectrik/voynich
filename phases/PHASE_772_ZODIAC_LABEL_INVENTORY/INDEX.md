# PHASE_772 — Do the zodiac labels form a shared per-sign inventory (a numeral-type crib)?

**Status: COMPLETE.**
- **Lock:** `phase772-lock` (2bb2919), after a lean-expert lock audit and a confirmation pass.
- **Run:** 103 s at Idle priority, with the lock verified. Raw results committed before this write-up (51920c6):
  `results/phase772_results.json`, `results/run_log.txt`.
- **Registered as C2090** (Tier 2 measurement, **partly unblinded**; see below).

## Verdict
**NO INVENTORY (bounded, λ\* = 8, the top of the calibrated grid).** Any set of about 30 forms used once in every sign
(for example degrees or days 1–30) is excluded as the label system, even with up to 77% of its copies visibly changed
at N2, plus any e-run, minim, ch/sh or gallows variation. **PALETTE was not called** (N1 p_high 0.0109 against the
0.01 bar).

**Blinding: partly unblinded.** An early smoke calibration built its palette model from the real labels (disclosed in
PRE_REGISTRATION §Blinding). Its N2 palette R, 0.138, already sat below every final threshold. So the R channel, and
with it NO INVENTORY at λ\* = 8, was foreseeable before the locked run, and the W channel was partly exposed too. The
verdict is a measurement, not a blind confirmation.

## Results (ZL 3b; 290 readable nymph labels on 10 signs)
| Level | R (recur in another sign) | W (within-sign share of duplicate pairs) | Exchangeable W | p (W low) | p (W high) | Types |
|---|---|---|---|---|---|---|
| N0 (descriptive) | 0.19 | 0.14 | 0.097 | 0.90 | 0.19 | 255 |
| N1 (e/i runs collapsed) | 0.23 | 0.20 | 0.097 | 0.99 | **0.011** | 244 |
| N2 (maximal collapse) | 0.35 | 0.17 | 0.097 | 0.998 | 0.004 | 218 |

- **Conservative word-level recurrence** (N2, a label recurs if any of its words does): 0.43, still below every
  inventory threshold.
- **Inventory thresholds** (R(N2), 1st percentile): 0.84 at λ = 1, 0.76 at λ = 3, 0.64 at λ = 8.
- **What the calibration can and cannot exclude:**
  - At λ = 1, a three-quarter inventory, or a half inventory whose remainder is random words, gives NO INVENTORY in at
    most 1 of 40 runs. Those are disfavoured, at λ = 1 only.
  - A half inventory with a palette-like remainder, or a quarter inventory, is **not** excluded.

## Descriptive
| Descriptive | Result |
|---|---|
| W by page (12 pages, N1) | 0.20 vs 0.086 exchangeable; p (high) 0.008 |
| Without the 13 top-row labels | W 0.18 (N1, p 0.05) / 0.17 (N2, p 0.014) |
| N2 with the first glyph unit stripped | R 0.39; W 0.17, p (high) 0.0015 |
| H track (placement S; 294 labels, not ZL's exact set) | R 0.20 (N1) / 0.30 (N2); W 0.18 / 0.19; p (high) 0.04 / 0.004 |
| Adjacency (N1) | clock-adjacent labels within a ring are no more similar than other pairs (effect +0.004, p 0.33) |

## Reading
- **Most labels occur in no other sign:** 77% at N1, 65% at N2, and 57% even when shared words count. This excludes the
  simplest numeral crib (one 1–30 set repeated in every sign) under the modelled variation.
- **Repeats lean within-sign, but PALETTE is not called.**
  - W is about twice the exchangeable share, but N1 missed the bar by less than the Monte Carlo standard error (0.0109,
    SE ≈ 0.001).
  - N2, by-page, first-unit-stripped and H-track N2 point the same way (p ≤ 0.008), but they reuse the same labels.
    H-track N1 (0.04) and the run without top rows (0.05) are weaker, and W was partly exposed before the lock.
  - All 13 within-sign pairs at N1 fall on the Gemini–Sagittarius pages. None falls on Pisces, Aries, Taurus or
    Cancer (compare C760; C531 covers Currier B only).
- **No adjacency pattern** (descriptive; power not calibrated; p 0.33). It bears only on numerals whose neighbours share
  written parts.
- **Scope limits** (not excluded):
  - partial inventories, as calibrated above;
  - sign-specific affixes;
  - two-word or medially varied numerals;
  - running counts that do not restart in each sign (day of the year, degrees 1–360);
  - transcription error.
- **Compatible, untested:** names, descriptions, meaningless forms. Random Currier A words also give NO INVENTORY, in
  97% of runs.
- **Consequence for the crib programme.** The labels are not a count restarting in each sign. Mostly sign-unique forms
  fit names, descriptions, running counts or random words alike. The next zodiac anchor has to come from outside the
  labels: the figures' attributes against the medieval degree tables (PHASE_773, design intent committed before any
  data).

## Scripts
- **Statistics and models:** `zod772.py`.
- **Calibration:** `cal772.py`.
- **Run:** `run772.py`.
- **Audits:** the lean-expert's scripts in `audit/` (`audit_structure.py`, `audit_model.py`, `audit_mixture.py`,
  `confirm_lock772.py`, and the post-run `results_check772.py`).

## Deviations
None from the locked procedure. The blinding problem arose before the lock and is disclosed in the pre-registration.
