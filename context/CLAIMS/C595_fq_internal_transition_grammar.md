# C595: FQ Internal Transition Grammar

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> FQ internal class transitions are strongly non-random (chi2=111, p<0.0001, 470 pairs). Class 23→9 is 2.85x enriched (closer feeds back to connector). Class 9→13 is directionally asymmetric (46:10 = 4.6:1). All classes self-chain above random (9: 1.60x, 13: 1.39x, 14: 1.45x, 23: 1.27x). The 2×2 BARE/PREFIXED aggregate shows chi2=69.7, p<0.0001 — BARE tokens preferentially transition to other BARE tokens.

---

## Evidence

**Test:** `phases/FQ_ANATOMY/scripts/fq_transition_context.py`

### Transition Matrix (470 pairs)

| From \ To | 9 | 13 | 14 | 23 |
|-----------|---|----|----|-----|
| **9** | **54** | 46 | 28 | 16 |
| **13** | 10 | **102** | 56 | 14 |
| **14** | 18 | 35 | **40** | 9 |
| **23** | **28** | 6 | 3 | 5 |

### Enrichment vs Independence

| From \ To | 9 | 13 | 14 | 23 |
|-----------|---|----|----|-----|
| **9** | **1.60x** | 0.79x | 0.72x | 1.19x |
| **13** | 0.24x | **1.39x** | 1.14x | 0.82x |
| **14** | 0.75x | 0.85x | **1.45x** | 0.94x |
| **23** | **2.85x** | 0.36x | 0.26x | 1.27x |

### Key Patterns

| Pattern | Observed | Enrichment | Meaning |
|---------|----------|------------|---------|
| 23→9 | 28 | **2.85x** | Closer feeds back to connector |
| 9→13 | 46 vs 10 (reverse) | 4.6:1 ratio | Connector feeds workhorse directionally |
| Self-chain (all) | diagonal | 1.27-1.60x | All classes self-chain |

### Aggregate 2×2 (BARE vs PREFIXED)

| From \ To | BARE | PREFIXED |
|-----------|------|----------|
| **BARE** | 103 | 83 |
| **PREFIXED** | 51 | 233 |

Chi2 = 69.7, p = 6.8e-17. BARE→BARE and PREFIXED→PREFIXED both enriched.

### Statistical Summary

| Test | Value |
|------|-------|
| Chi-square (4×4) | 111.0 |
| p-value | 1.1e-16 |
| Chi-square (2×2) | 69.7 |
| p-value (2×2) | 6.8e-17 |

---

## Interpretation

FQ has an internal transition grammar with clear directional flow:
1. **Class 23 (CLOSER)** feeds back to **Class 9 (CONNECTOR)** at 2.85x — closing one FQ sequence initiates the next
2. **Class 9 (CONNECTOR)** feeds forward to **Class 13** at 4.6:1 directionality — connector opens into the workhorse
3. **Self-chaining** is universal, consistent with phrasal clustering (C550)
4. The BARE/PREFIXED aggregate confirms morphological groups transition preferentially within-group

This establishes FQ as having **internal sequential structure**, not random class mixing.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C550 | Refined - FQ self-transition 1.44x (role level) now decomposed to class level |
| C593 | Extended - 3-group structure now shown in transition patterns |
| C561 | Contextualized - or→aiin bigram (Class 9) is the connector transition |
| C597 | Related - Class 23 final dominance feeds into 23→9 restart pattern |

---

## Provenance

- **Phase:** FQ_ANATOMY
- **Date:** 2026-01-26
- **Script:** fq_transition_context.py

---

## Navigation

<- [C594_fq_13_14_vocabulary_bifurcation.md](C594_fq_13_14_vocabulary_bifurcation.md) | [INDEX.md](INDEX.md) ->
