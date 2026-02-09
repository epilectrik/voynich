# C824: A-Record Filtering Mechanism Validated

## Constraint

The A->B filtering mechanism is **structurally real**:
- Mean filtering rate: **81.3%** (confirms C502)
- Under C502 model: more PP = MORE token survival (rho=+0.734)
- Aggregation effect: line 11.2% -> paragraph 31.8% -> folio 50.0% survival
- **82.9%** of A-records have >2x routing lift

This confirms C502 (~80% filtering) and validates the token-filtering mechanism.

> **Aggregation Note (2026-01-30):** This constraint analyzes at line level (1,559 "A-records").
> Per C881, A records are paragraphs (342 units). Per C885, the operational unit for A-B
> vocabulary correspondence is the A FOLIO (114 units, 81% coverage). Line-level analysis
> shows that aggregation helps; folio-level is required for sufficient coverage.

**NOTE:** Original T1-T4 tests used a subset-viability model (later shown to be wrong question).
See C826 for model reconciliation: C502 token filtering is the correct interpretation.

## Evidence

| Metric | Value |
|--------|-------|
| A-records analyzed | 1,559 |
| B-folios | 82 |
| PP vocabulary | 404 MIDDLEs |
| Mean viability | 15.3 folios (18.7%) |
| Median viability | 5.0 folios |
| Universal records (all B viable) | 8 (0.5%) |
| Zero-viability records | 346 (22.2%) |
| Narrow records (<10 viable) | 939 (60.2%) |

### PP Count vs Viability

| PP Count | Records | Mean Viability | % of Max |
|----------|---------|----------------|----------|
| 0 PP | 6 | 82.0 | 100% |
| 1-2 PP | 78 | 44.1 | 54% |
| 3-5 PP | 633 | 21.0 | 26% |
| 6-10 PP | 798 | 8.2 | 10% |
| 11-20 PP | 44 | 3.4 | 4% |

Linear: slope = -3.58 folios/PP, R² = 0.171

## Interpretation

**REVISED per C826:** The filtering mechanism works via token allowance:
1. A-record PP vocabulary defines which B MIDDLEs are ALLOWED
2. B tokens with MIDDLEs in A's PP set are legal; others filtered out
3. More PP MIDDLEs = more B tokens survive = better operational coverage

The original T1-T4 tests used a "subset viability" model (B folio must CONTAIN all A's PP).
T7 proved this was the wrong question. The C502 token-filtering model is correct:
more aggregation = union of allowances = more tokens survive = better usability.

## Provenance

- Phase: A_RECORD_B_ROUTING_TOPOLOGY
- Scripts: t1_viability_profiles.py, t3_pp_breadth_prediction.py
- Related: C502 (~80% filtering), C689 (97.6% unique survivor sets)

## Tier

2 (Validated Finding - mechanism confirmed with quantitative precision)
