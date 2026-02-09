# C826: Token Filtering Model Validation

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_ROUTING_TOPOLOGY | **Scope:** A-B

## Finding

The **C502 token-filtering model is the correct interpretation** of A->B mechanics. A-record PP MIDDLEs define what's ALLOWED in B, not what's REQUIRED. More PP = more token survival, not stricter requirements.

> **Note (2026-01-30):** This constraint validates the aggregation benefit across levels.
> C885 establishes that A FOLIO (114 units) is the operational unit for A-B vocabulary
> correspondence, achieving 81% coverage vs paragraph's 58%.

## Model Comparison

| Model | Mechanism | PP Effect | Aggregation Effect |
|-------|-----------|-----------|-------------------|
| C502 (CORRECT) | B token legal if MIDDLE in A's PP | More PP = more survival | HELPS usability |
| Subset (WRONG) | B folio must CONTAIN all A's PP | More PP = stricter | HURTS viability |

## Empirical Evidence

| Aggregation Level | Mean PP | C502 Survival | Subset Viability |
|-------------------|---------|---------------|------------------|
| Single Line | 5.8 | 11.2% | 15.3 folios |
| Paragraph | 20.2 | 31.8% | 1.6 folios |
| Full A-Folio | 38.9 | 50.0% | 0.0 folios |

**C502 Model Correlations:**
- Line level: PP -> Survival rho = +0.734 (p < 1e-200)
- Paragraph level: PP -> Survival rho = +0.862 (p < 1e-90)
- Folio level: PP -> Survival rho = +0.772 (p < 1e-20)

**Aggregation multiplier:** 4.45x improvement from line to folio (11.2% -> 50.0%)

## Interpretation

The A->B relationship is a **vocabulary allowance system**:

1. A record's PP MIDDLEs create a "legal vocabulary" filter
2. B tokens are legal if their MIDDLE appears in the filter
3. Aggregating A records (union of PP) EXPANDS the filter
4. More aggregation = more legal B tokens = better operational coherence

This validates:
- **C502:** Token-level filtering is the core mechanism
- **C693:** Aggregation helps usability (under correct model)
- **C738:** Union of A folios increases coverage

The "subset viability" question (does B folio CONTAIN all A's PP?) is structurally different and measures something else entirely. It does not represent how the system operates.

## Provenance

- Script: `phases/A_RECORD_B_ROUTING_TOPOLOGY/scripts/t7_model_reconciliation.py`
- Validates: C502, C502.a, C693, C738
- Supersedes: T3 interpretation (rho=-0.439 was wrong question)
