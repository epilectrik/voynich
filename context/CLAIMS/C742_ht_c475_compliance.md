# C742: HT C475 Line-Level Compliance

**Tier:** 2
**Phase:** HT_RECONCILIATION
**Test:** T3
**Scope:** B

## Statement

When HT tokens co-occur with classified tokens on the same B line, their MIDDLEs violate C475 incompatibility at 0.69% — comparable to the classified-classified baseline of 0.63%. HT-HT violation rate is 0.44%. All rates are below the 2% compliance threshold. HT tokens obey C475 at the same rate as classified tokens.

## Evidence

| Pair category | Pairs checked | Violations | Rate |
|---------------|--------------|------------|------|
| Classified-Classified | 55,293 | 348 | 0.63% |
| HT-Classified | 44,666 | 310 | 0.69% |
| HT-HT | 11,471 | 50 | 0.44% |

- Lines with both HT and classified tokens: 2,253/2,420 (93.1%)

### Permutation Test (1000 shuffles within folio)

| Metric | Value |
|--------|-------|
| Observed cross violations | 310 |
| Null mean | 281.1 |
| Null std | 16.59 |
| Z-score | +1.74 |
| P(fewer) | 0.048 |

HT does not show significantly fewer violations than random (z=+1.74, p=0.048 marginally non-significant). HT MIDDLEs are placed on lines WITHOUT active avoidance of illegal pairs — they simply comply at the ambient rate.

## Interpretation

HT tokens are C475-compliant not because they actively avoid illegal pairs, but because the incompatibility graph is sparse relative to the MIDDLE space. The compliance is a consequence of structural sparsity, not active rule enforcement. This is consistent with C404-C405 (HT non-operational).

## Provenance

- Phase: HT_RECONCILIATION/results/ht_c475_compliance.json
- Script: ht_c475_compliance.py
- Related: C475 (MIDDLE incompatibility), C404 (HT non-operational)
