# PHASE_771 — What is a label's initial o? Do line-edge forms appear at drawing breaks?

**Status: COMPLETE.**
- **Lock:** `phase771-lock` (commit ea2bac5), after a lean-expert lock audit and a confirmation pass.
- **Run:** `scripts/run771.py`, 1,111 s at Idle priority. The lock and the input checksums were verified before any data
  were loaded. The raw results were committed before this write-up (76c41c8): `results/phase771_results.json`,
  `results/run_log.txt`.
- **Registered as:**
  - **C2088** (Arm L, Tier 2 measurement);
  - **C2089** (Arm E, Tier 2 measurement).
- **Wording:** checked by expert-advisor and lean-expert, whose corrections are applied.
- **Post-hoc descriptives** (not verdicts) are labelled as such, with intervals from committed scripts:
  - `scripts/posthoc771.py` → `results/posthoc771.json`;
  - `scripts/audit/audit_results.py` → `results/posthoc_audit_results.txt`;
  - `scripts/audit/audit_results2.py` → `results/posthoc_audit_results2.txt`.

**Terms used below:**
- **Units:** glyph units (PHASE_754): a benched gallows is one unit, and a minim group with its final is one unit.
- **α:** the Dirichlet concentration of folio clustering. Lower α means stronger clustering.
- **Edge index I:** 0 means words look like position-matched mid-line words; 1 means they look like continuation-line
  edges.
- **E-seg / E-line:** the edge forms follow the pen segment, or the logical line.

## Verdicts (pre-registered rules)
| Arm / cell | Verdict |
|---|---|
| **L** — what a label's initial *o* corresponds to | **MIXED / UNRESOLVED [no mixture of the three fits] [fragile: ordinary o-words]** |
| **E, A start** | **UNRESOLVED** (I 0.37, 95% CI 0.18–0.56) |
| **E, A end** | **UNRESOLVED** (I 0.74, CI 0.51–0.99) |
| **E, B start** | **UNRESOLVED** (I 0.51, CI 0.30–0.70) |
| **E, B end** | **descriptive (UNRESOLVED)**: not evaluable, since calibrated E-seg power was 0.646 < 0.8 (I 0.20, CI 0.08–0.35) |
| **E, arm level, start** | **UNRESOLVED** (A and B agree) |
| **E, arm level, end** | **no statement** (B end is not evaluable) |

## Arm L — the label's initial o

### Primary result
- **Sample:** 608 ZL label o-words on 53 folios (words starting with *o* but not *qo*, of at least 2 units).
- **Model:** grouped EM over length strata 2…7+ against length-matched references:
  - R_qo, from text qo-words of L+1 units;
  - R_o, from text o-words of L units;
  - R_init, from text words of L−1 units.
- **Uncertainty:** folio bootstrap, 2,000 replicates.

| Reference | Weight | 95% CI |
|---|---|---|
| ordinary o-words (w_o) | 0.81 | 0.575–1.00 |
| qo without q (w_qo) | 0.19 | 0.00–0.42 |
| o added to a word (w_add) | 0.00 | 0.00–0.02 |

- **Call:** MIXED / UNRESOLVED. The lower bound of w_o is 0.575, below the 2/3 bar.
- **Fit check:** p = 0.0005, the smallest value attainable with 2,000 draws, at α_fc 9.8. No mixture of the three
  references fits the labels.
- **Power** at the labels' own clustering (α 9.8) is 1.00 under each pure reference, so the call is informative.
- **Fragile:** the bio labels alone give a pure "ordinary o-words" (w_o 0.999, CI 0.73–1.00; 72 words on 11 folios).
  s7 is also pure but report-only.
- **Within-label mixture?** Per the pre-registered rule, the result is "mixed across systems or unresolved". Only the
  fit check fails; the systems share the same largest-weight reference (o).

### Departures from the best fit
Residuals are observed minus expected under the best-fitting mixture. Intervals come from a folio bootstrap with the
weights refitted in each replicate. Because the fit fails, these describe departures from a model that does not fit.

| Unit after the o | Observed − expected | 95% CI |
|---|---|---|
| l | −60 (42 against 102) | −102 to −34 |
| k | −38 | −67 to −15 |
| t | +35 | +2 to +71 |
| p/f | +34 (77 against 43) | −1 to +96 |
| r | +13 | +4 to +25 |
| s | +9 | +3 to +18 |
| e | +9 | −4 to +26 |

**Concentration on one folio.** 32 of the 77 *p/f* words are on the Rosettes foldout, which holds 92 of the 608 label
o-words. Leaving out any one folio gives:

| Unit | Range of residuals |
|---|---|
| p/f | +9 to +35 |
| l | −62 to −44 |
| t | +26 to +42 |

**Per system.** Each system is fitted on its own, and the per-word *l* deficit differs by system:

| System | Words | Folios | Call | Weights | *l* deficit |
|---|---|---|---|---|---|
| astro/zodiac/cosmo | 408 | 22 | MIXED | w_o 0.65, w_qo 0.34 (CI 0.04–0.70) | −43 |
| pharma/herbal | 126 | 18 | MIXED | w_o 0.99 (lower bound 0.55) | −14 |
| bio | 72 | 11 | ordinary o-words | w_o 0.999 | none |

- The astro and pharma/herbal deficits are similar per word.

### Sensitivity analyses
| Analysis | Call | Weights qo / o / init | Feeds the fragile flag |
|---|---|---|---|
| s1 language-matched references | MIXED | 0.17 / 0.83 / 0 | no (smallest reference 34) |
| s2 line-initial references | MIXED | 0.72 / 0.28 / 0 | no (15) |
| s3 merged spaces | MIXED | 0.21 / 0.79 / 0 | yes |
| s4 H track | MIXED | 0.34 / 0.63 / 0.03 | yes |
| s6 R_init without o/q | MIXED | 0.20 / 0.77 / 0.03 | yes |
| s7 AZC labels vs AZC ring text | ordinary o-words | 0.16 / 0.84 / 0 | no (17) |
| s8 type-weighted references | MIXED | 0.59 (CI 0.33–0.82) / 0.41 / 0 | yes |

w_add is at most 0.03 in every analysis.

**Descriptive: stem families.** 404 of the 608 label o-words have a relative in running text.

| Relative in text | Labels, pooled | Labels, per-word mean | Matched text o-words, pooled | Matched text o-words, per-word mean |
|---|---|---|---|---|
| qoX | 0.39 | 0.26 | 0.31 | 0.23 |
| oX | 0.37 | 0.42 | 0.38 | 0.41 |
| X | 0.25 | 0.32 | 0.31 | 0.36 |

**Post hoc (descriptive): the header register.** Shares of the unit after the o, standardised to the label length
profile:

| Unit after o | Labels | Header-line o-words | Body o-words |
|---|---|---|---|
| p/f | 0.13 (CI 0.07–0.20; 0.085 without the Rosettes) | 0.25 | 0.01 |
| l | 0.07 (0.04–0.10) | 0.14 | 0.22 |
| k | 0.31 | 0.21 | 0.35 |
| t | 0.33 (0.28–0.39) | 0.29 | 0.29 |

On *p/f* and *l*, labels lean toward header lines (C1788); on *k*, toward body lines. The comparison is partial and
post hoc.

### Reading (Arm L)
- **Not "o added to a word".** The unit after a label's o is unlike the first unit of text words: w_add ≤ 0.03, with
  upper bounds ≤ 0.07, in every analysis.
- **The qo component depends on the references.** It is ≤ 0.42 with the primary references. It is the largest weight
  with type-weighted references (s8: 0.59, CI 0.33–0.82) or line-initial ones (s2: 0.72, report-only).
- **Nearest the ordinary o-word family, but no mixture fits.**
  - **Robust:** fewer *o-l* and *o-k* than the best fit.
  - **Marginal:** the *t* excess over the mixture. It is absent against text o-word shares (0.33, CI 0.28–0.39, against
    0.29).
  - **Mostly one folio:** the *p/f* excess over the mixture rests largely on the Rosettes. The excess over body
    o-words holds without it.
- **Possibly an AZC property rather than a label property.** Against AZC ring and circle text (s7, report-only), the
  AZC labels (two-thirds of the sample) fit ordinary o-words alone. The zodiac-led departure may therefore belong to
  AZC text generally (C1502, C1559) rather than to labels.
- **What this does not show:** why labels favour *o* (C525), or whether labels name anything.

## Arm E — line-edge forms at drawing breaks

### Results
- **Sample:** 725 ZL `<->` breaks inside paragraph lines. A: 512 breaks on 79 folios; B: 213 on 27 folios.
- **Edge models:** fitted on unbroken lines. Paragraph-first line starts and paragraph-last line ends are excluded from
  the edge classes. The models are cross-fitted by folio halves.

| Cell | I | 95% CI | Call | Sensitivity analyses t1–t5 |
|---|---|---|---|---|
| A start | 0.37 | 0.18–0.56 | UNRESOLVED | all UNRESOLVED (I 0.33–0.41) |
| A end | 0.74 | 0.51–0.99 | UNRESOLVED | all UNRESOLVED (I 0.68–0.77); four of five CIs include 1 |
| B start | 0.51 | 0.30–0.70 | UNRESOLVED | all UNRESOLVED (I 0.49–0.55) |
| B end (not evaluable) | 0.20 | 0.08–0.35 | descriptive (UNRESOLVED) | t1 and t5 give E-line; others UNRESOLVED (I 0.17–0.24) |

- No evaluable cell is fragile.
- **No interval meets any pre-registered bar.** The start intervals exclude 0 and 1. A end is not separated from 1.

### Pre-registered descriptives
Rates are shown with folio-bootstrap 95% intervals. Position-matched expectations are counts expected at the break
positions under the mid-line rate.

**Articulated starts** (C1417):

| Language | After a break | Continuation-line starts | Mid-line | Observed vs position-matched expectation |
|---|---|---|---|---|
| A | 0.090 (0.065–0.117) | 0.159 | 0.030 | 46 vs 21.6 |
| B | 0.113 (0.070–0.147) | 0.164 | 0.023 | 24 vs 6.0 |

- The ratio to line starts is 0.57 (0.40–0.77) in A and 0.69 (0.41–0.93) in B.
- The post-break rate differs both from line starts and from mid-line words, with CIs excluding 0 in both languages.

**-m endings** (C1002, C1486):

| Language | Before a break | Continuation-line ends | Mid-line | Observed vs position-matched expectation |
|---|---|---|---|---|
| A | 12/512 = 0.023 (0.012–0.037) | 0.104 | 0.019 | 12 vs 9.4 |
| B | 5/213 = 0.024 (0.005–0.050) | 0.205 | 0.005 | 5 vs 1.4 |

**Bare *aiin* after a break:** 3 in A and 2 in B. These are at or below the position-matched mid-line expectations of
5.2 and 4.1. Two of the five follow a bare *s* (f96r, f26r), which joins to *saiin*, so they may be a word cut by the
drawing. C1909 is a line-start exclusion.

**Post hoc (descriptive): the last unit before a break, Currier A.** Shares with folio-bootstrap intervals; "expected"
is the position-matched interior count.

| Last unit | Pre-break | Continuation-line final | Interior | Pre-break count vs expected |
|---|---|---|---|---|
| l | 0.12 (0.09–0.16) | 0.11 | 0.21 | 63 vs 102 |
| r | 0.07 (0.05–0.09) | 0.09 | 0.16 | 34 vs 80 |
| y | 0.41 | 0.35 | 0.33 | |
| s | 0.09 | 0.06 | 0.05 | |
| d | 0.06 | 0.04 | 0.01 | |
| iin | 0.10 | 0.14 | 0.11 | |
| o | 0.03 | 0.02 | 0.05 | |
| m (unit *m* only) | 0.02 | 0.10 | 0.02 | |

The *m* row counts the unit *m* only: 88 of 895 line ends, where the pre-registered *-m* counts 93.

### Reading (Arm E)
- **The index sits between the two references, and the rule leaves open which case applies.** Break words could be a
  mix of edge-like and mid-line-like words, or a third profile.
- **Descriptively, starts are intermediate.** Articulated starts follow a break at 57% (A) and 69% (B) of the
  line-start rate, clearly above the mid-line rate. Bare *aiin* is not informative here (see above).
- **Descriptively, ends split by feature.**
  - *-m* follows the line end, not the break. Before a break it is rare: at the mid-line rate in A, and in B about five
    times the mid-line rate but an eighth of the line-end rate.
  - Other line-end preferences do appear before breaks (post hoc, A): *-l* and *-r* are scarce, as at line ends; *-y,
    -s* and *-d* exceed both references; *-iin* is below both.
- **No mechanism is distinguished.** `<->` marks a gap in the writing surface, not an observed pause of the pen. As §4
  of the pre-registration notes, text written before the drawing would predict edge-free break words too.

## Registry updates
- **New rows:** C2088 (Arm L) and C2089 (Arm E).
- **Annotated:** C525, C1909, C1417, C1002 and C1486.
- **Not annotated:** C1788, C1427 and C1898. The PHASE_771 evidence bearing on them is post hoc, or was not measured.
  C1898's opener/embedded split at breaks is worth running.

## Scripts
- **Loader and statistics:** `zl771.py`, `stats771.py`.
- **Design and calibration:** `design771.py`, `cal771.py`.
- **Run:** `run771.py`.
- **Post hoc:** `posthoc771.py`.
- **Audits:** the lean-expert's scripts in `audit/` (including `audit_results.py` and `audit_results2.py`, the source of
  the post-hoc intervals).

## Deviations
None from the locked procedure. The post-hoc descriptives were added after the run and are labelled as such.
