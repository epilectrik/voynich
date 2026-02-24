# C1247: aii REGIME_3 Specificity

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** APPARATUS_VOCABULARY_CLASSIFICATION (Phase 445)
**Extends:** C179 (4 stable REGIMEs), C506 (intra-class behavioral heterogeneity)
**Relates to:** C1134 (section specificity is frequency-modulated), F-BRU-020 (output category vocabulary signatures)

---

## Statement

The MIDDLE `aii` ("unseal") is 41x enriched in REGIME_3 relative to REGIME_1. 14/20 REGIME_3 folios contain aii (70%), versus 1/32 REGIME_1 folios (3.1%). The lone R1 occurrence (f107v) is a single token. Total: 32 aii tokens across 21 folios, with REGIME_3 accounting for 23/32 (72%).

| REGIME | Folios with aii | Total folios | Presence rate |
|--------|----------------|--------------|---------------|
| REGIME_1 | 1 | 32 | 3.1% |
| REGIME_2 | 3 | 15 | 20.0% |
| REGIME_3 | 14 | 20 | 70.0% |
| REGIME_4 | 3 | 15 | 20.0% |

Within REGIME_3, aii concentrates in Section S (pharmaceutical folios): 11 of the 14 R3 aii-folios are Section S, with the remainder in H and C.

---

## Line Context Pattern

aii tokens sit at a structural transition point within lines. Tokens preceding aii are closing/checking operations; tokens following aii are opening/continuation operations:

**Before aii:** ar (close), sar (scaffold-close), cheo (test-cool), odor (collect-portion), otchor (scaffold-test-close)
**After aii:** ai (open), aiin (iterate), al (complete), sheo (monitor-cool), eol (sustain-output)

The pattern: close/check → **unseal** → open/continue. This is consistent with a batch-processing cycle requiring physical unsealing between runs.

---

## Token Forms

The dominant form is `aiir` (aii + suffix -r = "unseal, input"): 16/32 tokens across 13 folios. Other forms: `lkaiir` (L-compound), `olaiir` (LINK), `okaiir` (vessel-unseal), `aiidy` (unseal-close), `aiis` (unseal-next).

---

## Structural Implication

REGIME_3 (per ignem / direct fire) operates as an open-cycle batch process: the apparatus must be physically opened between distillation runs. REGIME_1 (standard fire) operates as a continuous-run process without unsealing. This vocabulary asymmetry is the strongest single-MIDDLE REGIME discriminator in the grammar.

---

## Method

- 82 Currier B folios (H-track, ≥50 tokens)
- MIDDLE frequency per folio via `Morphology.extract()`
- REGIME assignments from `data/regime_folio_mapping.json`
- Line context: ±1 token window around aii tokens in R3

**Script:** `phases/APPARATUS_VOCABULARY_CLASSIFICATION/scripts/apparatus_profiles.py`
**Results:** `phases/APPARATUS_VOCABULARY_CLASSIFICATION/results/apparatus_profiles.json`
