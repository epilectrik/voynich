# C705: Folio-Level Class Survival

**Status:** VALIDATED | **Tier:** 2 | **Phase:** FOLIO_LEVEL_FILTERING | **Scope:** A-B

## Finding

Folio-level PP pooling produces **39.8/49 B classes** on average (81.2% survival), a 3.6x improvement over record-level filtering (11.08/49 from C682). Even the worst A folio retains 30/49 classes. The folio is the functional filtering unit.

## Role Survival at Folio Level

| Role | Mean Survival | Baseline | Depletion |
|------|---------------|----------|-----------|
| CC | 1.5/4 | 4 | 0.9% |
| EN | 16.1/18 | 18 | 0.0% |
| FL | 1.0/4 | 4 | **32.5%** |
| FQ | 3.9/4 | 4 | 0.0% |
| AX | 17.2/19 | 19 | 0.0% |

FL remains the most fragile role (C686), even at folio level.

## Key Numbers

| Metric | Record-Level (C682) | Folio-Level |
|--------|---------------------|-------------|
| Mean classes | 11.08/49 | **39.8/49** |
| Min classes | 0 | 30 |
| PP MIDDLEs input | 5.0 | 35.3 |
| B empty-line rate | 78% | **13.7%** |

## Provenance

- Script: `phases/FOLIO_LEVEL_FILTERING/scripts/folio_level_filtering.py` (T3.2)
- Extends: C682 (record-level baseline), C504 (PP count correlation)
