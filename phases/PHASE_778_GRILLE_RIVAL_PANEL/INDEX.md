# PHASE_778 — Rival-generator panel II: the table-and-grille method

**Status: COMPLETE.**
- **Question:** does any declared variant of the table-and-grille method (Rugg 2004; Hyde & Rugg 2014, "producing
  the text"; Rugg & Taylor 2016; Zandbergen 2021), with its composition fitted to Currier B, produce an ensemble
  containing B on the PHASE_757 discriminators D2–D6?
- **Lock:** `phase778-lock` (593d2d9), pre-registration v3 after a lean-expert design audit (fifteen edits) and a
  confirmation pass (eight edits). **Post-lock deviation:** the verdict stage crashed on a bookkeeping bug after the
  pooled rerun (never-run members read as NaN); fixed with no change to any statistic, criterion, N, seed, family,
  threshold or band, re-tagged `phase778-lock2` (5bce182); the controls, panel, near-fit and rerun arrays computed
  under the first tag were read unchanged. Equivalence check: the first-tag and second-tag verdict code give
  identical decisions and outside sets for all 130 variants on the first-pass array.
- **Run:** controls 6 min; panel 130 variants × 1,000 members, 21.8 h at Idle priority (chain-ordered steelman
  variants at folio scope cost up to a minute per member); near-fit 100 alternates × 200 members, 1.3 h; pooled rerun
  of two variants, 7 min. Raw arrays kept locally (`*.npz`, git-ignored, as in PHASE_757); certification, verdict and
  logs committed. Results check by the lean-expert: calls correct; wording below follows its edits.
- **Registered:** **C2096** (Tier 2; one row for the whole test). Scope notes on C173 (required) and C120.

## Verdict (locked rules)
| Tier | Variants | Excluding | FITTED (calibrated bar 1.165 / declared 1.0) | Verdict | BORDERLINE |
|---|---|---|---|---|---|
| **PUBLISHED** (Hyde & Rugg as described) | 8 | 8 | 0 / 0 | **EXCLUDED (PARTIAL FITS ONLY)** | 2 |
| **EXTENDED** (published sources beyond the description; public-implementation placement) | 84 | 83 | 50 / 25 | **NOT EXCLUDED** (one variant) | 12 |
| **STEELMAN-EXPOSED** (chain rows, junction redraw from B's junction table; D2 not counted, z\* 3.02) | 38 | 37 | 8 / 0 | **NOT EXCLUDED** (one variant) | 5 |

Tier labels are identical under the declared bar, without D2, without D6, and without the D5/D6 merge (switched
off by C3 before the lock). Every axis value excludes at least 95% of its variants. **No Tier-0 proposal:** the rule
allowed one only if PUBLISHED and EXTENDED were both EXCLUDED, and EXTENDED is not. Tier 0 is unchanged.

**The rule (locked):** outside = beyond the ensemble [min, max] and |z| > z\*; a variant excludes if two or more
discriminators are outside and at least one of them is D3 or D4, the two certified by controls that do not build
them in (D2, D5 and D6 are certified only by controls that do). The pre-registration's rationale: an exclusion must
not rest only on discriminators the controls build in. This clause is new relative to PHASE_757; C2080's Naibbe
exclusion meets it (D3 outside in 64 of 64 variants).

## The two variants not excluded
Both are the same walk group with two row arrangements, both FITTED under the calibrated bar (1.161, 1.091) and
PARTIAL under the declared bar: vertical moves of ±2, no line reset, repeats kept, no junction redraw, noise-free;
Stolfi parser; real rows (each a B word split in three, drawn from the P-text's word frequencies); one 500 × 20
table for the whole corpus; draw exponent 1.0; grille change 0.05 per line; all nine offsets. Random rows (EXTENDED)
and chain rows (STEELMAN). Pooled N = 2,000, no NaN member, k 5 and 4.

| | EXTENDED/random (counted D2–D6) | STEELMAN/chain (counted D3–D6) |
|---|---|---|
| D2 | outside: z +163.7, B above all 2,000 (ensemble 0.004 ± 0.001) | not counted (ensemble 0.011; z +101) |
| D3 | inside: z +0.21, rank 1,145 of 2,000 | inside: z +0.20, rank 1,124 |
| D4 | not outside: B above all 2,000 members (max 2.398, B 2.414) but z +2.67 < 3.09 | not outside: B above 1,995 of 2,000 (max 2.565), z +2.54 < 3.02; both legs fail |
| D5 | outside: z −10.2, B below all (ensemble 0.494) | outside: z −9.8, B below all (0.493) |
| D6 | outside: z +65.7, B above all (ensemble 0.000) | outside: z +69.1, B above all (0.000) |

Under the locked rule these two variants are NOT EXCLUDED. Each meets the count clause (EXTENDED: D2, D5, D6
outside; STEELMAN: D5, D6). Neither meets the clause that one outside discriminator be D3 or D4: D3 is at chance and
D4 is not outside. Their V1 twins exclude (D4 z 3.5–3.6, BORDERLINE); the first-pass and rerun values agree within
0.2; the rerun could only have turned non-exclusions into exclusions and did not. Not excluding a variant is not
evidence that it generates B. Descriptively, B lies outside both ensembles on D5 and D6, and the EXTENDED one on D2;
these discriminators are passed only by generators built to have the feature, so the tested walks lack B's boundary
coupling, order profile and line-zone dependence. For the STEELMAN survivor, "without D6" leaves only D5 outside
(n_out 1): still not excluded, now on both clauses.

## What the panel measured (B: D2 0.228, D3 0.015, D4 2.414, D5 0.038, D6 0.172; P-text skeleton)
| Discriminator | B outside in | Closest ensemble mean | Note |
|---|---|---|---|
| D2 edge-glyph coupling | 92 of 92 counted (z ≥ +38.5; PUBLISHED z +139 to +192) | 0.013 (frequency-ordered rows) | the steelman's junction redraw, not counted, reaches 0.11–0.18 (z +8 to +29) |
| D6 line-zone vocabulary | 130 of 130 (z ≥ +19.6) | 0.049 (the published line-reset rule) | |
| D4 cross-folio trigram recurrence | 126 of 130 | 1.18 (published 'avoid'; outside on D2, D3, D5, D6) | the four exceptions at z +1.6 to +2.7 |
| D5 order information beyond edge | 101 of 130 (both directions) | within 0.2 sd for some length-ordered rows | small moves give up to 0.74 bits/token; random placement near 0 |
| D3 adjacent repetition | 54 of 130 | at chance in the steelman (0 of 38) | 'avoid' variants suppress repeats to max run 1 (B 4) |

- **PUBLISHED tier.** All eight exclude: D2 z +139 to +192 (ensembles 0.001–0.006), D6 z +19.6 to +52
  (0.007–0.049), D4 z up to +359 for 'keep' and +1.6 to +9 for 'avoid', D5 z −15.6 to +3.3, D3 z +0.2 (keep) and
  +3.6 to +36 (avoid). No variant reaches either FITTED bar (best 1.51: independent columns cannot reach B's hapax
  share and type count), hence the qualifier. BORDERLINE: d2/avoid/V1 (D3 z 3.6) and d5/avoid/V1 (D3 z 3.7).
  **UNSTABLE-TO-FIT:** the d2/reset/keep families (2 of 8 variants): at N = 200, alternates 1 and 3 of their walk
  group (section tables 40 × 16 and 120 × 16) were not excluded by the same D3/D4 pattern (D3 z +0.3, rank 119 and
  113 of 200; D4 z +1.5 and +1.6, rank 198 and 196) while outside on D2 (z +141, +152), D5 (−15, −16) and D6 (+18,
  +21); alternates 2 and 4 excluded (D4 z +7.5, +21.8).
- **Steelman near-fit:** the d2/reset/keep/redraw group (4 variants) is UNSTABLE-TO-FIT: alternate 2 (section
  120 × 16) not excluded (D3 z +0.2, rank 109; D4 z +1.5, rank 196; outside D2 +21.7, D5 −14.8, D6 +24.0);
  alternates 1, 3, 4 excluded (D4 z +15 to +181). The label leaves verdicts unchanged.
- **BORDERLINE exclusions (19):** twelve rest on D3 at z 3.5–3.9 (all 'avoid' variants, where repeats are suppressed
  to a run of 1), five on D5 at |z| 3.2–4.0, two on D4 at z 3.5–3.6 (the survivors' V1 twins).
- **Descriptives (P-text skeleton; no verdict role).** Repeated within-line 5-token windows (B 0): published
  variants 0–18; length-ordered rows about 34; frequency-ordered rows about 2,070 with 48 duplicate lines and
  identical runs to 15. Fitted variants: types 4,500–6,800, hapax 0.45–0.65, Zipf −0.79 to −0.96 (B 4,640 / 0.669 /
  −1.051). Composition attribution: the published tier's D2 shortfall sits beside a first-glyph-unit divergence of
  2.7 scale units, the survivors' beside 0.8.
- **Pre-lock controls.** C1 self-consistency 0 of 350 false exclusions; C2 FAIL as declared (M1 1.165, G-EDGE 0.933
  against the declared 1.0: any with-replacement resampler of B misses B's hapax share and type count), FITTED bar
  calibrated on the M1 control's unrounded distance; C3 column-lock D5 0.029 (M1 99th percentile 0.051), no D5/D6
  merge; C5 chain D2 0.437, junction redraw 0.174 (threshold 0.119). Band counts under the calibrated / declared bar:
  PUBLISHED 0 / 0 FITTED, EXTENDED 50 / 25, STEELMAN 8 / 0.
- **Partial unblinding (disclosed before the lock):** D2–D6 were computed on fitted-variant members in C1 while B's
  PHASE_757 values were known (EXTENDED D2 ≈ 0.001, D5 0.01–0.02; PUBLISHED D5 0.20–0.25; junction redraw D2
  0.17–0.21); the FITTED bar was recalibrated after this; no other rule changed. The steelman was exposed to B's
  adjacent edge-glyph bigram table, which is why D2 is not counted for it.
- **B values** agree across the certification and verdict files (D4 2.414 here against 2.474 in PHASE_757, a
  shuffle-seed difference in the same statistic).

## Reading
- **The method as Hyde & Rugg describe it does not generate Currier B at any configuration that reaches B's
  composition, and none does.** Its text has almost no end-to-start glyph coupling (0.006 bits at best against B's
  0.228) and a quarter of B's line-zone dependence at best, while sequential reading carries far more cross-folio
  phrase recurrence and word-to-word predictability than B when the card moves little, and far less when it moves
  freely. EXCLUDED (PARTIAL FITS ONLY).
- **The extended and steelmanned forms are not excluded under the locked rule**, on one fitted variant each, for
  the reasons given above with the numbers. 121 of 122 such variants exclude.
- **Descriptively, across all 130 ensembles,** B lies outside on D6 (z ≥ 19.6), and outside all 92 ensembles where
  D2 is counted (z ≥ 38.5); the steelman's junction redraw, built from B's junction table, reaches 0.11–0.18 bits of
  coupling (z 8–29) and is not counted. No tested configuration reproduces B's line-zone dependence, or its
  edge-glyph coupling where counted. Only generators built to have these features pass them.
- **Scope.** The configurations tested: the published mechanics, their published extensions, the public
  implementations' placement, and the two exposed steelmen. A grille with boundary or line-position rules beyond the
  steelman's junction redraw is a new test. Excluding the published configuration is not evidence for the
  control-program reading (C120) or for meaning (C2052); not excluding a variant is not evidence that it generated B.
- **Follow-up (open).** The d2 / keep walks: V0 not excluded in EXTENDED and STEELMAN, V1 borderline, d2/reset/keep
  UNSTABLE-TO-FIT. A follow-up is a new pre-registered phase whose discriminator is certified on controls before it
  sees these variants. Extending PHASE_778's N or adding discriminators to re-decide it is not allowed.

## Design history (controls only; B blind until the lock)
1. Generator from the published mechanics (every Hyde & Rugg quotation verified against the source page); gates G1
   (page reproduction from a page-built table, Zandbergen's equivalence) and G2 (exact binomial lengths) passed.
2. Design audit (lean-expert): three tiers; per-word random placement (the public implementations' rule); junction
   redraw; grille sets; nine fit statistics; bands; pooled rerun; D5/D6 merge rule; sensitivities; controls C1–C5.
3. Fit stage: 25 walk groups × 1,296 (216 restricted) configurations on composition only, plus a declared extension
   (per-folio 250 × 20, α 0.25); every group PARTIAL (1.12–1.56). Per-variant banding on own distance.
4. Confirmation pass: FITTED bar calibrated on the M1 control (unrounded), all-PARTIAL tier rule, D5 NaN rule,
   partial-unblinding disclosure, composition attribution, C4 rule per walk group.
5. Lock, pipeline, verdict (with the post-lock verdict-stage fix and its equivalence check).

## Methods notes
- **A composition-fit band for a rival must be calibrated on B's own resampling controls** before it is declared:
  M1 misses B's hapax share by 5.5 tolerance units. Never round the control's value after seeing the rival's fits.
- **Report ranks beside z.** A variant can be not excluded while B sits above every one of its 2,000 members on a
  discriminator (|z| below the bar because the ensemble spread is wide). The label and the numbers must travel
  together; neither "effectively excluded" nor "generates B" follows.
- **Chain arrangements over large per-folio tables are the panel's cost driver** (a minute per member); size the
  steelman's tables or vectorise before locking.

## Files
- `PRE_REGISTRATION.md` (v3 + deviation), `scripts/grille778.py`, `gates778.py`, `fit778.py`, `fit_extend778.py`,
  `band778.py`, `prelock_controls778.py`, `run778.py`.
- Results: `results/gates778.json`, `b_surface778.json`, `fit778.json`, `variant_bands778.json`,
  `prelock_controls778.json`, `controls_certification778.json`, `panel_verdict778.json`, logs, `dryrun/`,
  `hyde_rugg_2014_part7.html` (source page for the quote check); raw `*.npz` local.
