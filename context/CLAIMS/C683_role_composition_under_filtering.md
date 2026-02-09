# C683: Role Composition Under Filtering

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

A-record filtering depletes roles **asymmetrically**.

> **Aggregation Note (2026-01-30):** This constraint analyzes at line level (1,562 units).
> Per C881, A records are paragraphs (342 units). Per C885, the operational unit for
> A-B vocabulary correspondence is the A FOLIO (114 units, 81% coverage).

FLOW (FL) is the most depleted role (60.9% of records lose all FL classes), followed by CC (44.6%). FREQUENT (FQ) is the most resilient (only 12.5% depletion). The role hierarchy under filtering is: **FQ > EN > AX > CC > FL**.

## Key Numbers

| Role | Baseline Classes | Mean Surviving | Survival % | Full Depletion % |
|------|-----------------|----------------|------------|-----------------|
| CC | 4 | 0.71 | 17.7% | 44.6% |
| EN | 18 | 3.85 | 21.4% | 8.5% |
| FL | 4 | 0.48 | 12.0% | 60.9% |
| FQ | 4 | 1.73 | 43.2% | 12.5% |
| AX | 19 | 4.31 | 22.7% | 3.9% |

| Metric | Value |
|--------|-------|
| Mean role entropy | 1.611 / 2.322 max (69.4%) |
| Median role entropy | 1.689 |
| Zero-entropy records | 47 (3.0%) |

## Interpretation

FQ's resilience (43.2% survival, only 12.5% depletion) reflects the frequency-oriented nature of FQ tokens — they use common MIDDLEs shared widely between A and B. FL's fragility (12.0% survival, 60.9% depletion) indicates FLOW operators use specialized MIDDLEs rarely present in A records.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/survivor_population_profile.py` (Test 2)
- Extends: C121 (49 classes), C682 (distribution profile)
