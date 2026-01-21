# ANIMAL_PRECISION_CORRELATION Phase Summary

**Date:** 2026-01-21
**Status:** COMPLETE
**Result:** MIXED - Structural distinctiveness confirmed, semantic hypothesis reframed

---

## Research Question

Does REGIME_4 (precision) show distinctive morphological signatures consistent with animal distillation's categorical procedural differences?

---

## Background

From prior work (BRUNSCHWIG phases):
- Puff Chapter 71 ("Kudreck" = cow dung) is the ONLY animal-based chapter in 83-chapter corpus
- Brunschwig documents ~30 animal waters requiring 4th degree fire
- 18 tokens with P(animal) = 1.00 were identified as "PRECISION-exclusive"
- Tier 4 speculative mapping associated f75r with Kudreck

---

## Pre-Registered Predictions

| ID | Prediction | Result |
|----|------------|--------|
| **P1** (Strong) | REGIME_4 hazard CV within 0.04-0.11 | **PASS** |
| **P2** (Medium) | REGIME_4 ch-prefix enrichment >1.2x | **FAIL** |
| **P3** (Medium) | f75r distinctive within REGIME_1 | **FAIL** |
| **P4** (Weak) | <20% L-compound in PRECISION tokens | **PASS** |
| **P5** (Exploratory) | REGIME_4 lower escape density | **SUPPORTED** |

---

## Test Results

### Test A: Design Clamp Validation

**P1: PASS** - C458 validated

| REGIME | Hazard CV | Recovery CV |
|--------|-----------|-------------|
| REGIME_1 | 0.057 | 0.520 |
| REGIME_2 | 0.094 | 0.893 |
| REGIME_3 | 0.069 | 0.546 |
| REGIME_4 | **0.060** | 0.649 |

All REGIMEs show clamped hazard (CV 0.04-0.11). REGIME_4 conforms to the design clamp.

**Key Discovery:** REGIME_4 has **0.37x the recovery operations** of other REGIMEs. Precision procedures have much less recovery activity - consistent with "get it right or fail" rather than "try, adjust, retry."

---

### Test B: PRECISION-Exclusive Token Classification

**P4: PASS** - 0% L-compound (threshold <20%)

**Critical Discovery:** All 18 "PRECISION-exclusive" tokens are **A-Exclusive**:

| Classification | Count | % |
|---------------|-------|---|
| A-Exclusive | 18 | 100% |
| B-Exclusive | 0 | 0% |
| L-compound | 0 | 0% |

These tokens exist in Currier A's registry but **never appear in Currier B's execution layer**. The "animal distillation" connection is about **A's material cataloguing**, not **B's procedural execution**.

This reframes the hypothesis: the Brunschwig material-class priors were computed from A entries, not B execution.

---

### Test C: f75r Investigation

**P3 (Adjusted): NOT DISTINCTIVE**

The Tier 4 mapping of Kudreck→f75r is not structurally supported:

| Fact | Value |
|------|-------|
| f75r actual REGIME | REGIME_1 (not REGIME_4) |
| f75r B-exclusive rate | 26.3% (REGIME_1 mean: 25.3%) |
| f75r z-score | +0.18 (not distinctive) |
| Hazard density | +1.73 z (borderline elevated) |

f75r is a typical REGIME_1 folio. The speculative mapping was correlational, not architecturally grounded.

---

### Test D: PREFIX Distribution by REGIME

**P2: FAIL** - ch-prefix enrichment ratio is 1.04x (not >1.2x)

However, REGIME_4 shows **significantly different** PREFIX distribution (chi-square p<0.000001):

| PREFIX | REGIME_4 Enrichment |
|--------|---------------------|
| da | **1.48x** |
| ok | **1.24x** |
| ct | **1.84x** |
| qo | 0.68x (depleted) |
| ch | 1.04x (baseline) |

REGIME_4's signature is da/ok/ct enrichment, not ch enrichment. This suggests precision procedures favor different PREFIX families than the ch-dominance hypothesis predicted.

---

### Test E: Singleton MIDDLE Density by REGIME

No significant difference:

| REGIME | Singleton Rate |
|--------|----------------|
| REGIME_1 | 48.9% |
| REGIME_2 | 34.6% |
| REGIME_3 | 32.2% |
| REGIME_4 | 37.2% |

REGIME_4 is not distinctive for singleton density.

---

### P5 (Exploratory): Escape Density

**SUPPORTED** - REGIME_4 shows lowest escape events

| REGIME | Near-miss Count |
|--------|-----------------|
| REGIME_1 | 38.0 |
| REGIME_2 | 17.2 |
| REGIME_3 | 17.8 |
| REGIME_4 | **12.7** |

REGIME_4 has **0.52x the escape events** of other REGIMEs. This aligns with precision = lower intervention tolerance.

---

## Key Discoveries

### 1. PRECISION Tokens Are A-Exclusive

The 18 tokens with P(animal)=1.00 exist in Currier A but not Currier B. The Brunschwig "animal distillation" finding is about **registry cataloguing**, not **execution**.

### 2. REGIME_4 Has Distinctive Operational Profile

| Characteristic | REGIME_4 vs Others |
|----------------|-------------------|
| Recovery operations | **0.37x** (much less) |
| Near-miss events | **0.52x** (much less) |
| da-prefix | **1.48x** enriched |
| ok-prefix | **1.24x** enriched |
| ct-prefix | **1.84x** enriched |
| qo-prefix | **0.68x** depleted |

REGIME_4 is "get it right the first time" - less recovery, less near-miss, different PREFIX profile.

### 3. f75r is Not the "Animal Chapter Analog"

The Tier 4 speculative mapping of Kudreck→f75r is not supported. f75r is a typical REGIME_1 folio, not a REGIME_4 outlier.

---

## Architectural Interpretation

The investigation reveals a **clean separation** between:

1. **A's Registry Layer**: Catalogs materials including animal-derived substances requiring precision procedures (4th degree fire). These are marked with specific MIDDLEs that don't propagate to B.

2. **B's Execution Layer**: Contains actual precision procedures (REGIME_4) but these are **not linked to specific A entries**. C384 (no A-B entry coupling) is preserved.

The "animal distillation" finding was Tier 4 speculation about A's cataloguing function, not B's execution patterns. The structural evidence shows B's REGIME_4 has distinctive operational characteristics (low recovery, low escape, da/ok/ct-enriched) but these cannot be traced to specific material classes.

---

## Constraint Implications

| Constraint | Status |
|------------|--------|
| C458 (Design Clamp) | **VALIDATED** - all REGIMEs show clamped hazard |
| C494 (REGIME_4 = precision) | **SUPPORTED** - distinctive low-recovery/low-escape profile |
| C384 (No A-B coupling) | **PRESERVED** - PRECISION tokens are A-exclusive |
| C498 (RI vocabulary) | **SUPPORTED** - animal-associated MIDDLEs stay in A |

---

## Files Produced

```
phases/ANIMAL_PRECISION_CORRELATION/
├── scripts/
│   ├── test_a_design_clamp.py
│   ├── test_b_precision_tokens.py
│   ├── test_c_f75r_investigation.py
│   └── test_de_morphology_by_regime.py
├── results/
│   ├── test_a_design_clamp.json
│   ├── test_b_precision_tokens.json
│   ├── test_c_f75r_investigation.json
│   └── test_de_morphology.json
└── PHASE_SUMMARY.md
```

---

## Conclusion

The "animal distillation / REGIME_4 correlation" hypothesis is **partially supported but reframed**:

1. **Supported**: REGIME_4 has distinctive operational characteristics consistent with precision procedures (low recovery, low escape, different PREFIX profile)

2. **Not Supported**: The 18 "PRECISION-exclusive" tokens don't appear in B at all - they're A's registry vocabulary for cataloguing materials that would require precision procedures

3. **Reframed**: The connection between animal distillation and Voynich is at the **category level** (A catalogues precision-requiring materials) not the **execution level** (B doesn't contain animal-specific procedures)

This preserves the semantic ceiling: we can infer that A catalogues materials requiring precision procedures, but we cannot decode which specific B folios execute "animal distillation" procedures.

---

## Navigation

← [../B_EXCLUSIVE_MIDDLE_ORIGINS/PHASE_SUMMARY.md](../B_EXCLUSIVE_MIDDLE_ORIGINS/PHASE_SUMMARY.md) | ↑ [../../context/CLAUDE_INDEX.md](../../context/CLAUDE_INDEX.md)
