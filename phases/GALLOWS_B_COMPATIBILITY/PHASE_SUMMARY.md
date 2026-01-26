# GALLOWS_B_COMPATIBILITY Phase Summary

**Date:** 2026-01-24
**Status:** CLOSED
**Outcome:** New constraints C502.a, C503.a, C508.a established; AZC-ACT updated; C508 revised

---

## Research Question

Do A gallows domains (k/t/p/f) predict B folio/program compatibility?

---

## Tests Conducted

### Test 1: Folio-Level Access (gallows_b_mapping.py)
- **Finding:** Every A folio can access every B folio (100% vocabulary overlap)
- **Gallows domain restriction:** NONE at folio level
- **Same-domain enrichment:** 1.07x stronger overlap (p<0.0001) — small but significant
- **Conclusion:** Gallows domains are preference gradients, not routing mechanisms

### Test 2: Record-Level PP Distribution (record_level_crippling.py)
- **Finding:** Mean 5.84 PP MIDDLEs per A record
- **94.6%** of records have sufficient PP (>2 MIDDLEs)
- **Only 0.4%** completely isolated (PP=0)
- **Conclusion:** Most A records have adequate B vocabulary access

### Test 3: Token-Level MIDDLE Filtering (token_level_filtering.py)
- **Finding:** 257 legal B tokens per A record (5.3% of 4889)
- **94.7%** of B vocabulary filtered per A context
- **Conclusion:** MIDDLE is the primary filter, more severe than previously documented

### Test 4: Full Morphological Filtering (prefix_suffix_filtering.py)
- **Key Finding:** PREFIX and SUFFIX add substantial additional filtering

| Filter | Legal Tokens | % of B | Additional Reduction |
|--------|-------------|--------|---------------------|
| MIDDLE only | 257.3 | 5.3% | — |
| + PREFIX | 92.4 | 1.9% | 64.1% |
| + SUFFIX | 129.9 | 2.7% | 49.5% |
| **Full morphology** | **38.5** | **0.8%** | **85.0%** |

### Test 5: Class Survival Under Full Morphology (class_survival_retest.py)
- **Key Finding:** Full morphological filtering dramatically reduces class survival

| Filter | Mean Classes | % of Total | Reduction from MIDDLE |
|--------|-------------|------------|----------------------|
| MIDDLE only | 41.5 | 65.9% | — |
| **Full morphology** | **6.8** | **10.8%** | **83.7%** |

- **Implication:** Each A record constrains B to ~7 instruction classes, not ~32
- **Note:** Test used 63 prefix-based classes; proportional reduction is key finding

### Test 6: C508 Retest - Class Discrimination Under Full Morphology (c508_retest.py)
- **Key Finding:** C508's claim "HOW MANY not WHICH" is REVISED under full morphology

| Metric | MIDDLE-only (C508) | Full Morphology |
|--------|-------------------|-----------------|
| Class Jaccard | 0.345 | **0.755** |
| Token Jaccard | 0.700 | **0.961** |
| Class mutual exclusion | 0.2% | **27.0%** |
| Token mutual exclusion | 27.5% | **69.0%** |

- **Implication:** Under full morphology, class-level discrimination is significant (not just token-level)
- **27% of class pairs never co-occur** - the "which" matters, not just "how many"

---

## Key Insights

1. **Filtering is token-level, not folio-level**
   - Every A folio can "reach" every B folio
   - But each A record constrains B to ~38 legal tokens (0.8%)

2. **Three cascading filters**
   - MIDDLE: primary (removes ~95%)
   - PREFIX: AZC family affinity (removes additional 64%)
   - SUFFIX: regime breadth (removes additional 50%)

3. **Gallows domain effect is secondary**
   - 1.07x vocabulary overlap enrichment within same domain
   - Not a routing mechanism, just weak thematic coherence

---

## Constraints Updated

### New: C502.a - Full Morphological Filtering Cascade
- **Tier:** 2
- **Scope:** A+B
- **Statement:** A→B filtering operates through three cascading morphological layers; all three components (PREFIX, MIDDLE, SUFFIX) contribute independently, reducing legal B vocabulary to 0.8% per A record

### New: C503.a - Class Survival Under Full Morphology
- **Tier:** 2
- **Scope:** A+B
- **Statement:** Full morphological filtering (PREFIX+MIDDLE+SUFFIX) reduces class survival to 6.8 mean (10.8%), an 83.7% reduction from MIDDLE-only filtering; ~7 classes form actual instruction budget per A context

### New: C508.a - Class-Level Discrimination Under Full Morphology
- **Tier:** 2
- **Scope:** A→B
- **Statement:** Revises C508 - under full morphology, class Jaccard=0.755 (vs 0.345), 27% class mutual exclusion (vs 0%); "WHICH" classes survive now matters, not just "HOW MANY"

### Updated: AZC-ACT vocabulary_legality section
- Added filtering_cascade with per-layer statistics
- Clarified legacy claim about "~80% filtered"

---

## Files Created

| File | Purpose |
|------|---------|
| `scripts/gallows_b_mapping.py` | Folio-level gallows domain analysis |
| `scripts/record_level_crippling.py` | Record-level PP distribution |
| `scripts/token_level_filtering.py` | Token-level MIDDLE filtering |
| `scripts/prefix_suffix_filtering.py` | Full morphological filtering cascade |
| `scripts/class_survival_retest.py` | Class survival under full morphology |
| `scripts/c508_retest.py` | C508 retest under full morphology |
| `PHASE_SUMMARY.md` | This file |

---

## Expert Validation

Expert-advisor confirmed (2026-01-24):
- No conflicts with existing Tier 0-2 constraints
- Findings are consistent with C472 (MIDDLE primary) and C473 (constraint bundle)
- Quantifies what C473 describes qualitatively
- Recommended as C502.a extension of C502

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C502 | Extended by C502.a |
| C503 | Extended by C503.a (class survival under full morphology) |
| C508 | Revised by C508.a (class discrimination under full morphology) |
| C472 | MIDDLE is primary carrier (confirmed) |
| C471 | PREFIX AZC family affinity (quantified) |
| C495 | SUFFIX regime breadth (quantified) |
| C473 | Constraint bundle (confirmed and quantified) |
| C384 | No context-free A→B coupling (confirmed at folio level) |

---

## Architectural Implication

The A→B pipeline works through **cascading restriction at vocabulary AND class level**:

```
A record: [PREFIX set] + [MIDDLE set] + [SUFFIX set]
              ↓              ↓              ↓
           64% cut       primary        50% cut
                         filter
              ↓              ↓              ↓
         B legal vocabulary: ~38 tokens (0.8% of 4889)
         B legal classes:    ~7 classes (10.8% of 63)
```

Each A record doesn't select programs — it **constrains programs to a tiny vocabulary slice AND a small instruction budget**.
