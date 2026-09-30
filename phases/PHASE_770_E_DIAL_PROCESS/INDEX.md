# PHASE_770 — What kind of process sets the e-dial?

**Status: COMPLETE.** Locked at the git tag `phase770-lock` (commit e5fc6b9). Run on B with `scripts/run_b770.py`: 52 minutes
at Idle priority, with the lock and bank checksums verified at start. Raw results were committed before the
registration review (0ab0d2d).
- Results: `results/e_dial_process_B.json`, `results/run_log.txt`.
- Pre-registration: `PRE_REGISTRATION.md`.
- Registered as **C2087** (Tier 2, measurement). The wording was checked by expert-advisor and lean-expert, and their
  corrections are applied.

## Verdicts (pre-registered rules)
| Arm | Question | Verdict |
|---|---|---|
| **0** | Does C2086 survive removal of the preceding token's two-glyph ending? | **Stands** against the preceding-glyph context model (additive, within folio) |
| **A** | Is the component static on the page or position-dependent? | **UNRESOLVED**: the fresh-draw gate failed on one check |
| **B** | Is it shared with ch/sh, k/t (as HEAD) or the minim count? | **UNRESOLVED for all three dials**: no dial met the SHARED criterion, and sharing is not excluded (power 0.16–0.49) |
| **C** (descriptive) | Continuity across page turns (present binding order)? | criteria not met; uninformative (power 0.06–0.12) |
| **D0** (descriptive) | e-dial component in Currier A? | not detected (low power; also a different hand and sections) |

**Dial names:**
- CS: sh vs ch.
- KTH: t vs k as the word's HEAD atom (qok-/qot-, chk-/cht-).
- OKOT: the ok/ot prefix.
- BENCH: benched vs plain gallows.
- MIN: 1 vs 2+ minims in a minim group.
- X: the cross-dial folio correlation.

## Arm 0 — preceding-glyph context
The within-folio additive effect of the preceding token's last two collapsed units is removed from the outcome, then S3c
is recomputed with standard cells.

| | S3c (unadjusted) | S3c_adj | p | Ratio | One-unit context |
|---|---|---|---|---|---|
| H | 0.298 | 0.306 | 0.0005 | 1.03 | 0.298 (p 0.0005) |
| ZL | 0.302 | 0.299 | 0.0005 | 0.99 | 0.301 (p 0.0005) |

- The calibrated power was 0.98 (H) and 0.96 (ZL). Context-only plants give S3c of about 0.
- **Baseline.** The unadjusted 0.298 is below C2086's 0.323 because the analysis set differs:
  - f76r is included;
  - f115r is assigned hand 3;
  - the legibility covariate is computed with every dial class collapsed.
- **Not controlled:** the following token. Run length changes the token's ending (C1225), and the ending routes the
  next token (C2082). The rival Arm 0 removes is preceding-token coupling (C1212, C1563, C2082) combined with folio
  vocabulary (C531).

## Arm A — shape over the page
On H, S3c is 0.298 and S3far 0.107, inside the bank window.

**The pre-registered gate failed, so the verdict is UNRESOLVED.**
- On fresh replicates at B's point, 12 of 13 gated checks passed.
- The failure: the 75% M1+M3 mixture (D14 0.51, gated as position-dependent) was called STATIC in 17.3% of 104 replicates, drawn from 2,000 draws. The limit was 15%.
  - The in-sample figure at B's point had been 11.1% (n 244); it was the optimistic one.
  - B (0.298, 0.107) borders the grid point (0.28, 0.12), where this mixture was already STATIC 17–22% before lock. The gate is marginal near B's point.
- The classifier's outputs before the gate are shown as "verdict" in the JSON (`armA.H`, `armA.ZL`, `noflip_*`). They are labels from before the gate, not verdicts.
  - H, ZL and all three no-flip sets classified POSITION-DEPENDENT.
  - Among them is the fullness-tercile cell, which answers part of the line-fullness caveat below.
  - Best-fitting model: M4-0.97, which is intermediate by D14 and is not distinguished from the M6 or M8 variants.

**Descriptive measurements, not a shape verdict.** A1, A4, A5 and the exclusion test re-express one covariance structure;
they are not independent lines of evidence.
- **Exclusion test** (B's 8-vector against each model's replicates near B's S3c):
  - These fit poorly (p 0.0006–0.0024, at the resolution floor: 0–3 of 566–1,700 replicates as extreme as B): the five static models (M1, M2a, M2b-2/4/6), M2c (first and last paragraph unexpressed) and M5 (linear trend).
  - Borderline: M3 (restart walk) 0.036; the 25% mixtures 0.011 and 0.020.
  - Fit well: M4-0.95/0.97, M6-0.95/0.97, M8-20/40 (p 0.96–0.98); M7 0.54; the 50% and 75% mixtures 0.11–0.72.
- **A1** quarter covariance, ×10⁻³:
  - mean at quarter distances 1, 2, 3: 4.9, 3.8, 1.5, against a mean diagonal of 6.3;
  - the first quarter is the least connected (C12 2.8);
  - effective folios 27;
  - leave-one-folio-out ranges: V1–V4 4.8–6.6, 4.0–5.9, 5.1–7.3, 5.5–9.1; D1–D3 3.7–5.5, 3.0–4.5, 0.5–2.4.
  - Per stratum:

    | Stratum | Folios | Mean diagonal | Distance 1 | Distance 3 |
    |---|---|---|---|---|
    | B/2 | 20 | 8.6 | 5.8 | 2.6 |
    | S/3 | 23 | 5.2 | 4.5 | 0.9 |
    | H/2 | 20 | negative (short pages; noise) | — | — |

    B/2 and S/3 carry the profile.
- **A4 edges** (S3far, stratum × quarter centred):
  - all lines 0.099;
  - without header and paragraph-final lines 0.130;
  - without the first and last 2 lines of each page 0.051;
  - without 4 lines 0.018.

  S3c stays at about 0.28–0.31. The fall is about one null SD, on nested subsets, with no envelope. The robust
  statement is only that S3far does not recover toward S3c once page edges are removed.
- **A5 variogram** on pages of 20 lines or more (×10⁻³). Separation bins run 1, 2, 3–4, 5–8, 9–16 and 17–32 lines.
  - **Same paragraph:** 9.9, 6.7, 6.8, 5.4, 0.3, 4.8. One line apart it exceeds the M1 envelope (≤ 4.8).
  - **Different paragraph:** 1.3, 8.2, 5.5, 4.6, 4.6, 4.1. These exceed M1 out to 17–32 lines, so part of the excess is level.
  - The shape evidence is the decline from about 8 to about 4.
  - **Across page turns:** 2.5, 5.6, 8.8, 1.3, −3.0, −0.7. This is mixed:
    - at 3–4 lines it is above the M1, M2b-4 and M3 envelopes;
    - at 5–32 lines it is below M6-0.97's envelope;
    - at 9–16 lines it is below M1's too.
    
    The envelopes are per bin and uncorrected.

**Line-fullness caveat:**
- E's residual tracks line fullness (crowding probe below).
- Line length falls along the page (C1782, C1783) and correlates between lines (C1728), so fullness could contribute to the quarter pattern.
- The fullness-tercile-cell analysis classified the same way (P(static) 0.001).
- This is consistent with ordinary scribal drift; the floor is untested.

## Arm B — sharing with other spelling choices
**B1, own components** (S3c; H under the within-cell null, ZL as the check):

| Dial | H | ZL | Own component (rule) | Strength (lower 80%) |
|---|---|---|---|---|
| CS (cell with the two-unit context) | 0.160 (p 0.023) | 0.219 (p 0.0025) | not established (H p > 0.01) | 0.33 (0.23) |
| KTH | 0.246 (p 0.0015) | 0.216 (p 0.004) | **yes**, as expected: k/t share is a REGIME-defining axis (C1715, C1920, C2070) | 0.46 (0.38) |
| MIN | withheld | withheld | withheld pending the §14 scan check | — |

- **Descriptive dials:** not detected for OKOT (S3c 0.002, p 0.50) or BENCH (0.027, p 0.39).
  - With the word frame fixed, OKOT is not detected and CS is not established on H. So the sister-choice folio share (C1182) is not shown to sit above the word.
- **Paragraph-specific components:** not detected for any dial at fixed word frame. S3P-within p is 0.46 (E), 0.35 (CS), 0.83 (KTH) and 0.95 (MIN). This is a frame-controlled statistic, not the composition results of C1811/C1812.
- **MIN** (minim count as read by H and ZL): the raw numbers are in `results/e_dial_process_B.json`. They are withheld from interpretation and registration until the §14 blind scan check.
  - H and ZL agreement is an upper bound.
  - The H–ZL gap on this statistic and F's disagreement both counsel caution.

**B2, sharing** (block split; joint shift null; SHARED needs |z| ≥ 3.2, the family-wise critical value, with the ZL leg):
- **E–CS:** X −0.17 on H (z −3.03), ZL −0.08 (z −1.64, p 0.10), runs read alike by H, F and ZL −0.13 (z −2.10). Not SHARED (UNRESOLVED).
  - The nominal permutation p is not size-valid.
  - CS has no established own component on H.
- **E–KTH:** X +0.13 (z +2.03), ZL +0.10 (p 0.09). UNRESOLVED.
- **E–MIN:** X +0.19 (z +1.69), ZL +0.16 (p 0.067). UNRESOLVED; withheld with MIN. NOT SHARED would need power ≥ 0.8; at the lower strength bound it was 0.42.
- **Summary:** no dial met the SHARED criterion. B2 power at ρ 0.7 is 0.16–0.49, so sharing is not excluded.
- **Other pairs** (descriptive, nominal p; the shift null is about 10% too narrow under the position-dependent models):
  - CS–MIN −0.215 (p 0.003);
  - CS–KTH −0.107 (p 0.18);
  - KTH–MIN +0.011 (p 0.90);
  - tetrads 0.026, 0.018, −0.008.
- **B3,** co-drift within pages (descriptive): not detected (|z| ≤ 1.6).
- **Crowding probe** (descriptive). Within folio and at fixed within-line position, E's residual falls as line fullness rises (p 0.0005). CS (0.20), KTH (0.47) and MIN (0.81) are not detected.
  - This does not identify space management as the source: in calibration, within-page drift plus lines shortening down the page produced it too.

## Arm C — page turns (descriptive)
- **C1,** present binding order (power 0.06–0.12, so uninformative):
  - K −0.224 on H (p(b) 0.91, p(a) 0.97); −0.197 on ZL (p(b) 0.87).
  - Every cut is negative: Q13, Q20, leaf turns, openings, all four quire halves, and the 80-folio set (−0.25).
  - The continuity criteria are not met: **no carry-over detected**.
- **Sheet-face K:** +0.029 (H), −0.021 (ZL).
- **C2:** not detected:
  - faces minus distance-matched pairs +0.0020 (p 0.34);
  - Gregory's-rule same-side contrast about 0 (p 0.94).

## D0 — Currier A (descriptive)
112 folios, 1,130 informative e-runs: S3c 0.0006 (p 0.49), so not detected. It has far fewer informative runs than B's 6,229,
and the comparison also spans a different hand and different sections.

## Reading (§11 guardrails)
- **Arm 0.** C2086 stands against the preceding-glyph context model (additive, within folio).
- **Arm A.** Its shape over the page is unresolved under the pre-registered rule; the gate was marginal near B's point.
  - Descriptively, the numbers are not those of a constant page setting: static models fit poorly, and S3far does not recover without page edges.
  - They do not distinguish mechanisms.
  - The floor ("every hand drifts") is untested.
- **Arm B.** Sharing with other spelling choices is unresolved, because B2 is underpowered.
- **Arm C.** No carry-over is detected across page turns, but C1 is uninformative.
- **The source question.** None of this discriminates between the §10 sources. Any process reading is echo-class and needs an external test or the human's sign-off.
- **Heat level, REGIME and fire degree stay Tier 3**, as in C2086's "no reading" clause. e-content loads on PC2, an axis REGIME is built from, so REGIME comparisons are circular.

## Scripts and calibration
See `PRE_REGISTRATION.md` §13 and the lock commit.
- **Engine:** `ed770.py`, `cal770.py`, `desc770.py`.
- **Arm A:** `bank770.py`, `clf770.py`, `thr770.py`, `excl770.py`.
- **Arm B:** `calB770.py`, `calBj770.py`, `calB3_770.py`.
- **Arm 0 and Arm C:** `cal0_770.py`, `calC770.py`.
- **Controls and pilot:** `neg770v3.py`, `pilot770.py`.
- **Run:** `run_b770.py`.
- **Audit:** the lean-expert's synthetic scripts in `audit/`.
- **Plant banks:** `.npz` files are gitignored and reproducible from seeds; checksums are in `results/calib/bank_checksums.txt`. The three no-flip banks were generated at run time.

## Deviations
None from the locked procedure.
- MIN's own-component and E–MIN results are withheld from interpretation pending the §14 scan check.
- The write-up's wording follows the expert-advisor and lean-expert checks of the results.
