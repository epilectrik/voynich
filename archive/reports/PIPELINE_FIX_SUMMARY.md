# Pipeline Fix Summary: Step 4 Intersection → Union

**Date:** 2026-01-17
**Fix Applied:** Changed vocabulary aggregation from INTERSECTION to UNION
**Status:** Ready for expert review

---

## The Fix

### Before (WRONG)
```python
effective_middles = None
for folio_id, projection in compatible_folios:
    folio_vocab = data_store.azc_folio_middles.get(folio_id, set())
    if effective_middles is None:
        effective_middles = folio_vocab.copy()
    else:
        effective_middles &= folio_vocab  # INTERSECTION
```

### After (CORRECT)
```python
effective_middles = set()
for folio_id, projection in compatible_folios:
    folio_vocab = data_store.azc_folio_middles.get(folio_id, set())
    effective_middles |= folio_vocab  # UNION
```

**Rationale:** AZC folios are alternative legality postures, not conjunctive constraints. Per C437 (Jaccard ≈ 0.056), folios are maximally orthogonal by design, so intersection produces artificial over-restriction.

---

## Test Results After Fix

### Sample A Records (First 20)

| Record | Tokens | MIDDLEs | Compatible AZC | Grammar | B Reachability |
|--------|--------|---------|----------------|---------|----------------|
| f1r.1 | 10 | 3 | 29 | 49/49 | 82R/0C/0U |
| f1r.2 | 11 | 3 | 1 | 44/49 | 0R/0C/82U |
| f1r.3 | 9 | 5 | 29 | 49/49 | 82R/0C/0U |
| f1r.4 | 9 | 4 | 29 | 49/49 | 82R/0C/0U |
| f1r.5 | 6 | 3 | 29 | 49/49 | 82R/0C/0U |
| f1r.7 | 11 | 1 | 29 | 49/49 | 82R/0C/0U |
| f1r.8 | 9 | 4 | 2 | 48/49 | 1R/78C/3U |
| f1r.9 | 4 | 3 | 29 | 49/49 | 82R/0C/0U |
| f1r.12 | 8 | 5 | 1 | 48/49 | 2R/77C/3U |
| f1r.13 | 9 | 4 | 3 | 47/49 | 0R/3C/79U |
| f1r.14 | 10 | 2 | 1 | 44/49 | 0R/0C/82U |
| f1r.19 | 8 | 3 | 1 | 46/49 | 0R/0C/82U |

**Key observations:**
- Records with no restricted MIDDLEs → AZC: 29, full grammar, all B REACHABLE
- Records with restricted MIDDLEs → AZC: 1-3, reduced grammar, differentiated B status

---

### Full Dataset Summary (1,533 Registry Entries)

#### AZC Compatibility Distribution
| Compatible Folios | Count | Percentage |
|-------------------|-------|------------|
| 0 | 117 | 7.6% |
| 1 | 188 | 12.3% |
| 2 | 186 | 12.1% |
| 3+ | 1042 | 68.0% |

**Note:** AZC compatibility is unchanged by this fix (determined by restricted-only disqualification logic).

#### B Folio Reachability
| Status | Records | Percentage |
|--------|---------|------------|
| Has REACHABLE B folios | 1225 | 79.9% |
| Only CONDITIONAL B folios | 80 | 5.2% |
| All UNREACHABLE B folios | 228 | 14.9% |

---

## Differentiation Analysis

### Grammar State by AZC Compatibility

Records with **few compatible AZC folios** (restricted MIDDLEs present):
- f1r.2: AZC=1, Grammar=44/49, B=all UNREACHABLE
- f1r.12: AZC=1, Grammar=48/49, B=2R/77C/3U
- f1r.14: AZC=1, Grammar=44/49, B=all UNREACHABLE

Records with **many compatible AZC folios** (no restricted MIDDLEs):
- f1r.1: AZC=29, Grammar=49/49, B=all REACHABLE
- f1r.3: AZC=29, Grammar=49/49, B=all REACHABLE

**Observation:** B reachability now differentiates based on which AZC folios are compatible and what vocabulary they provide.

---

## MIDDLE Classification

| Category | Count | Percentage | Treatment |
|----------|-------|------------|-----------|
| Restricted (1-3 folios) | 409 | 87% | CAN forbid compatibility |
| Universal (4+ folios) | 59 | 13% | CANNOT forbid compatibility |

**Universal MIDDLEs (examples):** a, air, al, ar, ch, che, cheo, cho, chos, ck

---

## Constraint Compliance

| Constraint | Status | Evidence |
|------------|--------|----------|
| C437 (5.6% Jaccard) | ✓ | Union preserves orthogonal folio structure |
| C440 (Uniform B sourcing) | ✓ | Union allows vocabulary from all compatible folios |
| C442 (Exception-based filter) | ✓ | Subtractive semantics preserved |
| C470 (MIDDLE restriction) | ✓ | Restricted MIDDLEs still control compatibility |
| C472 (77% exclusive) | ✓ | 87% restricted by type count |

---

## Questions for Expert

1. **Expected B reachability distribution:** We now see:
   - 79.9% of A records have at least one REACHABLE B folio
   - 14.9% have all UNREACHABLE B folios
   - Is this the expected behavior?

2. **Union vs Per-Folio Evaluation:** We implemented Option B (union). Would Option A (per-folio evaluation) show different/better differentiation?

3. **Zone Legality Impact:** After union, zone legality still applies (subtracts from the union). Is this the correct order of operations?

---

## Files Modified

| File | Change |
|------|--------|
| `core/reachability_engine.py:442-453` | Changed `&=` to `|=` for vocabulary aggregation |

---

## Next Steps

- Expert validation of fix
- Consider implementing Option A (per-folio evaluation) if more differentiation needed
- Update PIPELINE_LOGIC_REPORT.md with corrected Step 4
