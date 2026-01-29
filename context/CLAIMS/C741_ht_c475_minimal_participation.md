# C741: HT C475 Minimal Graph Participation

**Tier:** 2
**Phase:** HT_RECONCILIATION
**Test:** T2
**Scope:** B

## Statement

Only 4.6% of HT MIDDLE types (61/1,339) appear in the C475 incompatibility graph (top-100 strongest illegal pairs, 69 distinct MIDDLEs). However, those 61 MIDDLEs account for 38.5% of HT occurrences (2,711/7,042), indicating that the high-frequency HT MIDDLEs are shared with the classified system while the long tail of 1,278 HT-exclusive MIDDLEs is too rare to generate testable incompatibility.

By comparison, 38.6% of classified MIDDLE types (34/88) participate in the graph.

## Evidence

| Population | MIDDLE types | In graph | % |
|------------|-------------|----------|---|
| HT | 1,339 | 61 | 4.6% |
| Classified | 88 | 34 | 38.6% |

HT MIDDLEs in graph: mean degree 3.0, median 2.0, max 10.

## Interpretation

The 95.4% of HT MIDDLEs NOT in the C475 graph are overwhelmingly singletons/rare types (C406: 78.9% hapax). They lack sufficient co-occurrence data to establish incompatibility relationships. This does not mean they are exempt from C475 — it means C475 is untestable for them.

The 38.5% occurrence coverage means the high-traffic HT tokens DO participate in C475 constraints.

## Note

Tested against top-100 strongest illegal pairs stored in middle_incompatibility.json. The full graph has 309,713 illegal pairs across 808 MIDDLEs, but only the strongest are stored.

## Provenance

- Phase: HT_RECONCILIATION/results/ht_c475_compliance.json
- Script: ht_c475_compliance.py
- Related: C475 (MIDDLE incompatibility), C406 (HT Zipf/hapax)
