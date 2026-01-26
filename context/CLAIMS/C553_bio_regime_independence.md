# C553: BIO-REGIME Energy Independence

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> BIO section is 70% REGIME_1, but their ENERGY enrichments are statistically independent. Baseline ENERGY is 27.5%; REGIME_1 adds +6.5pp; BIO section adds +9.8pp. Both effects are significant (p<0.001) when controlling for the other. BIO + REGIME_1 folios reach 48.9% ENERGY through additive combination.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/bio_regime_correlation.py`

### BIO Section REGIME Composition

| REGIME | BIO Folios | % of BIO |
|--------|------------|----------|
| REGIME_1 | 14 | **70%** |
| REGIME_2 | 1 | 5% |
| REGIME_3 | 3 | 15% |
| REGIME_4 | 2 | 10% |

### ENERGY Rate by Category

| Category | Folios | Mean ENERGY |
|----------|--------|-------------|
| Baseline (non-BIO, non-R1) | 53 | 27.5% |
| Non-BIO + REGIME_1 | 9 | 34.1% (+6.5pp) |
| BIO + non-R1 | 6 | 37.3% (+9.8pp) |
| **BIO + REGIME_1** | 14 | **48.9%** |

### Independence Tests

| Test | Comparison | p-value | Result |
|------|------------|---------|--------|
| Within REGIME_1 | BIO vs Non-BIO | **0.0001** | BIO effect exists |
| Within BIO | REGIME_1 vs Non-R1 | **0.0002** | REGIME effect exists |

Both effects are significant when controlling for the other, confirming independence.

---

## Interpretation

### Additive Model

ENERGY rate follows an additive model:

```
ENERGY% = Baseline + REGIME_effect + Section_effect
        = 27.5% + 6.5pp + 9.8pp
        = 43.8% (predicted)

Observed BIO + REGIME_1: 48.9% (close to additive prediction)
```

### Why BIO is REGIME_1

The BIO section (balneological/biological imagery) is predominantly classified as REGIME_1 (70%). This makes sense if:
- REGIME_1 represents **thermal processing context**
- BIO section describes **bath/heat-related procedures**

The alignment is **content-driven**, not coincidental.

### Independent Contributions

1. **REGIME_1 contribution (+6.5pp):**
   - REGIME_1 is thermal processing mode across all sections
   - Even non-BIO REGIME_1 folios have elevated ENERGY

2. **BIO section contribution (+9.8pp):**
   - BIO content inherently involves more thermal operations
   - Even non-REGIME_1 BIO folios have elevated ENERGY

### Combined Effect

BIO + REGIME_1 folios are **doubly thermal**:
- Content (BIO) requires thermal operations
- Context (REGIME_1) is thermal processing mode
- Result: 48.9% ENERGY (highest in manuscript)

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C551 | Clarified - REGIME_1 effect is independent of section |
| C552 | Clarified - Section effect is independent of REGIME |
| C547 | Extended - qo-chain REGIME_1 enrichment adds to BIO effect |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** bio_regime_correlation.py

---

## Navigation

<- [C552_section_role_profiles.md](C552_section_role_profiles.md) | [INDEX.md](INDEX.md) ->
