# C745: HT Coverage Metric Sensitivity

**Tier:** 2
**Phase:** HT_RECONCILIATION
**Test:** T6
**Scope:** B, A-B

## Statement

Removing HT tokens from B vocabulary increases mean A-B coverage from 31.0% to 43.2% (delta 39.3%), but preserves the routing architecture: per-B-folio coverage correlation r=0.850, p=5.3e-24. The coverage increase is a definitional artifact — removing tokens that CANNOT pass the C502.a filter mechanically raises the pass rate. A folio variance share increases from 70.8% to 78.7%.

## Evidence

| Metric | Full vocab | Classified only | Delta % |
|--------|-----------|----------------|---------|
| Mean coverage | 31.0% | 43.2% | 39.3% |
| A variance share | 70.8% | 78.7% | 11.2% |
| B variance share | 20.1% | 11.3% | 43.8% |
| Mean lift | 2.21x | 2.05x | 7.5% |

Per-B-folio coverage correlation: r = 0.850, p = 5.3e-24.

## Interpretation

The large metric deltas (up to 43.8%) do NOT challenge C404 (HT non-operational). They reflect a measurement artifact: HT tokens are defined as those outside the classified grammar, which means they have uncommon MIDDLEs that rarely appear in A pools. Removing them from the denominator mechanically inflates coverage.

The preserved routing architecture (r=0.85) confirms that the STRUCTURE of A-B routing is unchanged — the same A folios prefer the same B folios regardless of whether HT is included. C404 is about operational function (predicting grammar state), not coverage statistics.

**C404 CONFIRMED**, not challenged.

## Provenance

- Phase: HT_RECONCILIATION/results/ht_coverage_impact.json
- Script: ht_coverage_impact.py
- Related: C404 (HT non-operational), C734-C739 (A-B routing architecture), C502.a (three-axis filtering)
