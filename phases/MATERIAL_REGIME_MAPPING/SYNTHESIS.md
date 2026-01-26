# MATERIAL_REGIME_MAPPING: Synthesis

**Date:** 2026-01-25
**Status:** COMPLETE

---

## Executive Summary

Material classes (animal, herb) do NOT differentiate at REGIME or folio level - both prefer REGIME_4 (precision). Differentiation occurs at **token variant** level (Jaccard=0.38, 62% non-overlap).

---

## Key Findings

### 1. REGIME-Level: No Differentiation

| Material | Dominant REGIME | Enrichment | p-value |
|----------|-----------------|------------|---------|
| Animal   | REGIME_4        | 1.87x      | 0.024   |
| Herb     | REGIME_4        | 1.87x      | 0.011   |

Both material classes route preferentially to REGIME_4 (precision control).

### 2. Folio-Level: Same Pattern

- Correlation between animal and herb folio reception: **r = 0.845**
- Herb dominates 23/25 REGIME_4 folios (higher reception everywhere)
- This is a **vocabulary size** effect, not routing differentiation

### 3. Token-Level: STRONG Differentiation

| Metric | Value |
|--------|-------|
| Overall Jaccard | **0.382** |
| Animal-only tokens | 198 (26.6%) |
| Herb-only tokens | 684 (55.6%) |
| Per-class mean Jaccard | **0.371** |

Within the same instruction classes, animal and herb select **different token variants**.

Most differentiated classes:
- `ke`: Jaccard = 0.037 (near-zero overlap)
- `fch`: Jaccard = 0.111
- `ol`: Jaccard = 0.169
- `qo`: Jaccard = 0.322

---

## Tier 4 RI/PP Role Reconstruction

### PP Role: Behavioral Parameterization

PP profiles do NOT route materials to different REGIMEs or folios. Instead:

1. **Capacity**: PP COUNT determines how many B classes survive (C504, C506)
2. **Variant Selection**: PP COMPOSITION determines which TOKEN VARIANTS within classes are legal (C506.a)

```
PP Profile → Token Variant Selection (NOT REGIME Selection)
         → Jaccard=0.38 between material classes
         → ~62% of execution options differentiate
```

### RI Role: Identity Discrimination

RI functions as A-internal discriminator:

1. **Compatibility Specification**: RI creates multi-dimensional incompatibility space
2. **Never Propagates**: RI never reaches B execution (C498)
3. **Folio-Localized**: 87% of RI localized to 1-2 folios (substance-specific)

```
RI → A-Internal Identity → Compatibility Intersection
  → Determines WHICH A record this is
  → NOT which REGIME to use
```

### Combined Model

```
A Record Selection:
├── RI → Identity (which specific material/substance)
├── PP → Capacity + Variant Selection
│
AZC Filtering:
├── MIDDLE → Class availability
├── PREFIX → Class-specific filtering
├── SUFFIX → Additional restriction
│
B Execution:
├── REGIME → NOT material-determined (both prefer precision)
├── Folio → NOT material-determined (same pattern, r=0.845)
├── Token Variants → MATERIAL-DETERMINED (Jaccard=0.38)
```

---

## What This Means

### The Manuscript Distinguishes "What" vs "How"

| Dimension | Encodes | Evidence |
|-----------|---------|----------|
| RI | WHAT (identity) | 87% folio-localized, A-exclusive |
| PP | HOW (execution tuning) | Token variant differentiation |
| REGIME | NOT material-class | Both animal/herb → REGIME_4 |

### "Precision" is Universal

REGIME_4 (precision control) is not animal-specific:
- Both animal AND herb prefer REGIME_4
- This suggests precision is about OPERATIONAL requirements, not material class
- Materials that reach high-confidence threshold (strong PP signature) may share operational similarity

### Token Variants Carry Material Information

The 62% non-overlap in token variants means:
- Same grammatical class
- Different execution flow
- Material-appropriate behavioral tuning

This matches C506.a: "tokens within same class are positionally compatible but behaviorally distinct."

---

## Revised Tier 4 Interpretation

### Previous Model (Partially Wrong)
"PP profiles route materials to specific REGIMEs"

### Corrected Model
"PP profiles tune token variant selection within a shared REGIME preference"

The manuscript does NOT encode:
- Material → REGIME mapping (both prefer precision)
- Material → Folio mapping (same pattern)

The manuscript DOES encode:
- Material → Token variant mapping (Jaccard=0.38)
- Material → Execution tuning within shared grammar

---

## Constraint Implications

### C506 Confirmed
PP composition is irrelevant at CLASS level (both materials use same classes).

### C506.a Confirmed
PP composition IS relevant at TOKEN level (62% variant differentiation).

### C536 Refinement Needed
C536 showed animal → REGIME_4. This is TRUE but INCOMPLETE.
Herb ALSO → REGIME_4. The precision routing is not material-class-specific.

**Proposed revision:**
> "High-confidence material signatures (both animal AND herb) route to REGIME_4 at 1.87x enrichment. REGIME routing is NOT material-class-discriminating. Material differentiation occurs at token variant level (Jaccard=0.38 between classes)."

---

## Files

| File | Purpose |
|------|---------|
| `scripts/material_regime_mapping.py` | Initial REGIME mapping |
| `scripts/material_regime_mapping_v2.py` | With PP markers |
| `scripts/find_herb_markers.py` | PP marker discovery |
| `scripts/folio_level_differentiation.py` | Folio-level analysis |
| `scripts/token_variant_differentiation.py` | Token-level analysis |
| `results/material_regime_mapping_v2.json` | REGIME results |
| `results/token_variant_diff.json` | Token differentiation |

---

## Next Steps

1. Investigate WHY both material classes prefer REGIME_4
2. Test if there's a material class that prefers a DIFFERENT REGIME
3. Characterize the token variants that differentiate animal from herb
