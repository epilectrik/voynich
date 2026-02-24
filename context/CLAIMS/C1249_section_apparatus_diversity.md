# C1249: Section-Conditioned Apparatus Diversity

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** APPARATUS_VOCABULARY_CLASSIFICATION (Phase 445)
**Extends:** C1134 (section specificity is frequency-modulated), C179 (4 stable REGIMEs)
**Relates to:** C1247 (aii R3 specificity), C1248 (apparatus co-occurrence), C1153 (generative design freedom)

---

## Statement

Section H (Herbal) is the most apparatus-diverse section. In mixed-apparatus REGIMEs (R2, R4), non-distillation folios are overwhelmingly Herbal:

- **R2-SEALED_VESSEL (9 folios):** ALL Section H (100%)
- **R2-DISTILLATION (6 folios):** 4 Section H + 2 Section C
- **R4-SEALED_VESSEL (3 folios):** ALL Section H (100%)
- **R4-SUSTAINED_HEAT (3 folios):** ALL Section H (100%)
- **R4-DISTILLATION (9 folios):** 6H + 1S + 1T + 1C

Other sections (B, S, C) are overwhelmingly DISTILLATION-dominant regardless of REGIME.

### Section apparatus profile means

| Section | DISTILLATION | SEALED_VESSEL | SUSTAINED_HEAT | PRECISION | n |
|---------|-------------|---------------|----------------|-----------|---|
| B (Bio) | **0.293** | 0.079 | 0.086 | 0.018 | 20 |
| S (Stars/Pharma) | 0.222 | 0.127 | 0.072 | 0.017 | 23 |
| H (Herbal) | 0.134 | **0.115** | **0.088** | **0.059** | 32 |
| C | 0.183 | 0.058 | 0.072 | 0.023 | 5 |

Section B has the highest distillation rate (0.293) and lowest precision rate (0.018). Section H has the lowest distillation rate (0.134) but the highest sealed vessel, sustained heat, and precision rates. Section H is the only section where no single apparatus profile dominates — its folios spread across all five profiles.

---

## Interpretation

The apparatus diversity of Section H reflects the variety of herbal processing: some herbs require gentle sealed extraction (balneum marie), others sustained maceration, others precision control. Section B (biological/pharmaceutical) procedures are more uniform — predominantly active distillation. This is consistent with the botanical content of Section H (diverse plant materials requiring material-specific processing) versus Section B (pharmaceutical preparations requiring standardized distillation).

---

## Weakest signatures

The 10 folios hardest to classify (smallest gap between top two profile scores) are ALL Section H:

| Folio | Dominant | Score | Gap | REGIME |
|-------|----------|-------|-----|--------|
| f105v | SEALED_VESSEL | 0.126 | 0.005 | R3 |
| f55r | SEALED_VESSEL | 0.129 | 0.008 | R2 |
| f34v | DISTILLATION | 0.096 | 0.009 | R3 |
| f40v | SEALED_VESSEL | 0.170 | 0.009 | R2 |
| f43v | DISTILLATION | 0.105 | 0.013 | R4 |
| f33r | SEALED_VESSEL | 0.111 | 0.014 | R2 |

These ambiguous folios may use multiple apparatus stages or represent simpler procedures that don't strongly engage any single apparatus vocabulary.

---

## Method

- 82 Currier B folios (H-track, ≥50 tokens)
- 5 apparatus profiles scored per folio (marker MIDDLE rates)
- Dominant profile = highest-scoring profile per folio
- Section assignment from transcript `token.section`

**Script:** `phases/APPARATUS_VOCABULARY_CLASSIFICATION/scripts/apparatus_profiles.py`
**Results:** `phases/APPARATUS_VOCABULARY_CLASSIFICATION/results/apparatus_profiles.json`
