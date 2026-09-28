# PHASE_755 — C2031 / C2032 reconciliation

**Status:** COMPLETE. Locked verdict **LENGTH-CONFOUNDED**. Annotations applied to C2031, C2032, C2053.
**Pre-registration:** `PRE_REGISTRATION.md` (commit e588555, before code). **Script:** `scripts/c2031_reconciliation.py` (5 s).
**Results:** `results/c2031_reconciliation.json`.

## Background
- C2031 (Tier 2) registered a period-2 e-depth signature in Section B (r21 = lag2/lag1 = −0.66) against a persistent
  pattern in matched Section S (+0.66); C2032 used the −0.66 as the "not natural language" sequential axis.
- A June off-books note reported r21 = +0.70 on **all of Currier B** — a different population from C2031's.
- A pre-registered length-stratified re-run on 2026-05-16 (`MENSURAL_NOTATION_HYPOTHESIS/results/length_stratified_c2031.json`)
  returned **FAIL: length confound confirmed**, and was never registered. Recorded here.

## Method
Canonical C2031 measurement (paragraphs split at `par_initial`; e-depth class 0/1/2+ from `Morphology.atomize`;
same-class rate at lag L minus the exact within-paragraph shuffle expectation). Reported statistic: the period-2
index **D = excess(lag 2) − excess(lag 1)** (positive = alternation), which does not divide by a near-zero lag-1.
Paragraph bootstrap, 2,000 resamples.

## Results
| Population (pooled) | Paragraphs | lag-1 excess | lag-2 excess | D [95% CI] | r21 (reference) |
|---|---|---|---|---|---|
| Section B, all (f75–f86) | 82 | −0.0171 | +0.0104 | **+0.0275 [+0.0077, +0.0471]** | −0.61 |
| matched-B (C2031's 15 folios) | 61 | −0.0155 | +0.0089 | +0.0245 [+0.0017, +0.0464] | −0.57 |
| Section S, all (f103–f116) | 283 | +0.0196 | +0.0126 | −0.0070 [−0.0204, +0.0064] | +0.64 |
| matched-S | 215 | +0.0259 | +0.0145 | −0.0114 [−0.0263, +0.0038] | +0.56 |
| all of Currier B | 462 | +0.0079 | +0.0119 | +0.0040 [−0.0056, +0.0131] | +1.50 |

Section B − Section S, pooled: **+0.0346 [+0.0116, +0.0581]**.

| Length stratum | Section B n | Section S n | D_B − D_S [95% CI] |
|---|---|---|---|
| 3–29 tokens | 5 | 125 | −0.104 [−0.251, −0.018] (B n too small) |
| **30–59** | 28 | 140 | +0.042 [−0.003, +0.090] |
| **60–119** | 39 | 14 | +0.051 [−0.008, +0.101] |
| 120+ | 10 | 4 | +0.044 [−0.010, +0.094] (S n too small) |

Qualifying strata (≥8 paragraphs in both groups): 30–59 and 60–119; neither interval excludes 0.

## Verdict (locked rules): LENGTH-CONFOUNDED
1. **Section B does alternate** (pooled D > 0 with the interval excluding 0), and the matched subset is not needed:
   all of Section B shows it. The June non-replication measured all of Currier B, where it is absent (D ≈ 0).
2. **The Section B vs Section S divergence is not established independently of paragraph length.** Section B
   paragraphs are long and Section S paragraphs short; within equal-length strata the difference is consistently
   positive but no stratum excludes 0. The comparison is underpowered, not refuted: the point estimates (+0.04 to
   +0.05) are close to the pooled +0.035.
3. r21 is unstable (for example −15.4 for all of Currier B at 120+ tokens) and should not be reported as a primary
   statistic.

## Consequences (as pre-registered)
- C2031(a) and the "Section B −0.66" in C2032/C2053 are rescoped: a period-2 e-depth alternation present in Section B
  paragraphs, not shown to be a section property independent of paragraph length.
- The section-divergence discriminator (D4 in the rival-panel design) cannot serve as a kill unless it is length-matched.
- C2032's NL comparison (Codicillus, Mesue, Rupescissa, Theophilus near 0) also stands on the unit caveat: Latin
  words, not letters. The Naibbe panel must include letter-unit baselines before "absent from natural language" is used.
- The v6.90 statement that C2032 "survives the 5-gram battery" was computed on the r21 metric and should be re-read in
  light of this rescope.
