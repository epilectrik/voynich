# C1429: Cross-Line Category Independence

**Tier:** 2 (ESTABLISHED)
**Scope:** B, line, independence, category, cross-line
**Phase:** LINE_LEVEL_ARCHITECTURE (Phase 519)
**Extends:** C670 (adjacent-line vocabulary coupling = zero), C673 (CC trigger sequential independence), C674 (EN lane balance autocorrelation = zero), C1233 (cross-line independence)
**Relates to:** C681 (sequential coupling verdict), C964 (boundary-constrained free-interior), C1312 (no cross-line sequential category coupling)

---

## Statement

Adjacent lines are categorically independent: suffix mode MI=0.003 bits, dominant category MI=0.032 bits, boundary category MI=0.025 bits, vocabulary Jaccard=0.153. Line length correlation=0.406 is entirely folio-mediated (folios with long lines have consistently long lines, not sequential propagation). Lines are fresh samples from the folio's operational profile, with no sequential memory.

### Metric Summary

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Suffix mode MI | 0.003 bits | Negligible |
| Dominant category MI | 0.032 bits | Very weak |
| Boundary category MI | 0.025 bits | Very weak |
| Line length correlation | 0.406 | Folio-mediated |
| Mean vocabulary Jaccard | 0.153 | Low overlap |

### Context

This extends a family of independence results:
- C670: Adjacent-line MIDDLE Jaccard = random (0.140 observed, 0/79 folios significant)
- C673: CC trigger type re-selected independently (permutation p=1.0)
- C674: QO fraction autocorrelation entirely folio-driven (within-folio p=1.0)
- C1233: Cross-line FL, mode alternation, channel switching near-random entropy (97.8%)

The new finding adds category-level and suffix-mode independence, confirming that the line is a complete, self-contained execution unit.

### Implication

Each line is independently composed from the folio's operational profile. No information propagates from one line to the next beyond what the folio-level parameterization provides. The grammar generates lines as i.i.d. samples conditioned on folio identity.

---

## Falsification Criteria

1. If cross-line category MI exceeds 0.10 bits
2. If line-length correlation persists after folio-level detrending at rho > 0.15

---

## Method

- 2,338 consecutive line pairs within folios
- MI computed from contingency tables of dominant category, suffix mode, boundary category
- Line length Pearson correlation on adjacent pairs
- Vocabulary Jaccard = |intersection| / |union| of MIDDLE sets

**Script:** `phases/LINE_LEVEL_ARCHITECTURE/scripts/line_architecture.py` (T7)
**Results:** `phases/LINE_LEVEL_ARCHITECTURE/results/line_architecture.json`
