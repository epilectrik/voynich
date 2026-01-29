# C792: B-Exclusive Vocabulary = HT Identity

**Tier:** 2
**Scope:** A<>B, HT
**Phase:** A_B_FOLIO_SPECIFICITY (extension)

## Constraint

The 34.4% of B vocabulary that is never legal under any A folio (C736, C738) is **100% HT/UN tokens**. Zero classified tokens are B-exclusive. All 88 unique MIDDLEs used by classified tokens appear in the A PP pool.

## Evidence

| Category | Types | % of B-Exclusive |
|----------|-------|------------------|
| HT/UN | 1,285 | 100.0% |
| Classified | 0 | 0.0% |

| Population | Total MIDDLEs | In PP | B-Exclusive |
|------------|---------------|-------|-------------|
| Classified | 88 | 88 (100%) | 0 (0%) |
| HT/UN | 1,339 | 404 (30.2%) | 935 (69.8%) |

## Interpretation

C736's description of B-exclusive vocabulary as "B's autonomous grammar - structural operators, control flow, kernel vocabulary" is **incorrect**. The B-exclusive layer is the HT/UN non-operational vocabulary, not the classified grammar.

The classified 49-class grammar is **100% dependent on A's PP pool**. Every MIDDLE used by an operational B token exists in A. This confirms the constraint propagation model (C753): A doesn't route content to B, but A's vocabulary determines what B operations are available.

## Revision to C736

C736's structural interpretation should be revised:
- **Original:** "B-exclusive core (34.4%): B's autonomous grammar - structural operators, control flow, kernel vocabulary"
- **Revised:** "B-exclusive layer (34.4%): HT/UN non-operational tokens. The operational grammar uses exclusively PP vocabulary."

## Dependencies

- C736 (B vocabulary accessibility partition)
- C738 (union coverage ceiling)
- C740 (HT = UN identity)
- C584 (near-universal pipeline purity)

## Provenance

```
phases/A_B_FOLIO_SPECIFICITY/scripts/b_exclusive_breakdown.py
```
