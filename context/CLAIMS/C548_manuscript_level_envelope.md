# C548: Manuscript-Level Gateway/Terminal Envelope

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Gateway (Class 30) and terminal (Class 31) tokens exhibit manuscript-level envelope structure: 90.2% of folios contain both classes, counts correlate strongly (rho=0.499), and gateways are front-loaded (earlier folios) while terminals dominate later folios.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/folio_envelope_test.py`

### Folio Co-occurrence

| Category | Folios | Rate |
|----------|--------|------|
| Both gateway AND terminal | 74 | 90.2% |
| Gateway only | 4 | 4.9% |
| Terminal only | 4 | 4.9% |
| Neither | 0 | 0% |

### Statistical Tests

| Test | Value | p-value |
|------|-------|---------|
| Spearman count correlation | rho = 0.499 | p < 0.0001 |
| Sequential trend | rho = -0.368 | p = 0.0007 |

### Dominance Pattern

| Type | Folios | Examples |
|------|--------|----------|
| Terminal-dominant (>60%) | 41 | f76r, f103v, f111v, f116r |
| Balanced (40-60%) | 26 | - |
| Gateway-dominant (>60%) | 15 | f84r, f77v, f78r |

---

## Interpretation

The gateway/terminal pattern operates at **manuscript level**, not line level:

1. **Near-universal co-occurrence:** 90.2% of folios have both - the envelope spans the entire work
2. **Correlated intensity:** Folios with more hazard entries also have more hazard exits (0.499 correlation)
3. **Sequential arc:** Gateway-heavy folios cluster earlier; terminal-heavy folios cluster later
4. **Overall balance:** 2.7x more terminal-dominant folios, suggesting the manuscript emphasizes safe exit over hazardous entry

This refines C542 (Gateway/Terminal Asymmetry): the asymmetry is about hazard-adjacency roles, not line-level sequencing. The envelope exists at manuscript scale.

---

## Relationship to Line-Level Ordering

Within-line co-occurrence shows only 40.4% gateway→terminal order, which initially seemed to contradict C542. This finding resolves the apparent conflict:

- **C542 (hazard-adjacent):** 100% asymmetric at forbidden transition boundaries
- **C548 (manuscript-level):** Arc from gateway-heavy to terminal-heavy across folios
- **Line-level:** No required ordering (terminals can precede gateways within lines)

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C542 | **Reconciled** - C542 characterizes asymmetry (different enrichment patterns), C548 characterizes scope (manuscript-level). Both are true: asymmetry exists AND operates at manuscript scale, not line scale. |
| C541 | Extended - envelope scope for hazard classes |
| C155 | Consistent - piecewise-sequential geometry |
| C107 | Consistent - kernel boundary-adjacency to forbidden transitions |
| C400 | Consistent - boundary hazard depletion explains medial clustering |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** folio_envelope_test.py

---

## Navigation

<- [C547_qo_chain_regime_enrichment.md](C547_qo_chain_regime_enrichment.md) | [INDEX.md](INDEX.md) ->
