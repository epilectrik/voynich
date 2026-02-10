# C954: Section T FL Enrichment

**Tier:** 2 | **Scope:** B | **Phase:** FL_RESOLUTION_TEST

## Statement

Section T has a higher FL rate (28.4%) than strong-forward S/B folios (21.2%). The Section T gradient anomaly (rho = 0.188, p = 0.60) is NOT caused by FL suppression.

## Evidence

- Section T: 662 tokens, 188 FL (28.4%)
- Section S/B (strong-forward): 3,219 tokens, 684 FL (21.2%)
- Section T lines: 69, folios: 2
- Section T FL stages: {0:12, 1:2, 2:44, 3:56, 4:27, 5:47}
- Section T prefixes: _ (46), da (41), ot (19), ok (12), ch (11), sh (10)

Section T independently shows a suffix effect (NMI p = 0.038), similar to ch-FL.

## Interpretation

Section T is a text-heavy, monitoring-intensive context with MORE annotation, not less. The gradient anomaly must have a different cause: possibly restricted MIDDLE vocabulary, different positional dynamics, or meta-level content (describing how to monitor rather than performing assessment).

## Provenance

- `phases/FL_RESOLUTION_TEST/scripts/06_section_t_diagnostic.py`
- Refines understanding of FL gradient anomaly noted in earlier investigation
