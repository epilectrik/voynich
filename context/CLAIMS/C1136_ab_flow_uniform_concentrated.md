# C1136: A->B Flow Is Uniform-Pool and Concentration-Structured

**Tier:** 2
**Status:** Active
**Scope:** A->B
**Phase:** 406 (CROSS_SYSTEM_VOCABULARY_FLOW)

## Finding

The A->B vocabulary pipeline is a **section-blind uniform pool** with **highly concentrated** operational grammar coverage.

### Uniform Pool (confirming C846)

A-Herbal and A-Pharmaceutical produce indistinguishable B coverage profiles:
- A-H vs A-P cosine similarity: **0.9997**
- Within-A-section cosine: H=0.9987, P=0.9992, T=0.9995

All A sections cover B-Herbal best, B-Stars worst:

| A Section | B coverage -> B | B -> C | B -> H | B -> S | B -> T |
|-----------|-----------------|--------|--------|--------|--------|
| H | 0.277 | 0.257 | 0.362 | 0.202 | 0.208 |
| P | 0.368 | 0.344 | 0.480 | 0.284 | 0.294 |
| T | 0.473 | 0.425 | 0.587 | 0.358 | 0.371 |

A-T (3 folios) provides highest coverage — vocabulary-rich text-only folios contain the most PP MIDDLEs.

### Concentration Structure

12 A folios cover 100% of B's 89 classified MIDDLEs (operational grammar):
- 1 folio (f58v, Section T): 60.7% coverage alone
- 6 folios: 90% coverage
- 12 folios: 100% coverage

| Step | Folio | Section | Gain | Cumulative |
|------|-------|---------|------|------------|
| 1 | f58v | T | 54 | 60.7% |
| 2 | f29v | H | 11 | 73.0% |
| 3 | f7v | H | 6 | 79.8% |
| 4 | f16r | H | 4 | 84.3% |
| 5 | f89r2 | P | 3 | 87.6% |
| 6 | f24v | H | 3 | 91.0% |

Hub section distribution (top 10): T=1, H=7, P=2.

### Coverage Ceiling

For B's full MIDDLE inventory (1,293 types): all 114 A folios achieve only 30.4% coverage. The remaining 69.6% is completely B-internal (consistent with C727, C736, C792).

## A-Section Routing

Bridge MIDDLEs are uniformly sourced: A-H 70.8%, A-P 21.2%, A-T 8.0%. P-enriched bridges (P>30%, n=25) favor ENERGY_OPERATOR (14/25 = 56%), while H-dominant bridges (H>70%, n=60) show balanced AX/EN (30/26). Weak differential but not zero.

## Evidence

- Full 114x82 Jaccard coverage matrix (PP MIDDLEs only)
- Greedy forward selection for operational grammar coverage
- A-section cross-tabulation of mean B-section coverage
- Bridge A-section enrichment per B role

## Provenance

- Source: Phase 406, Tests B2 + C1 + C2
- Confirms: C846 (pool-based relationship), C885 (81.2% folio coverage)
- Related: C384 (no token-level lookup), C498.a (AZC-mediated vs B-native)
