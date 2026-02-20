# C1144: Dark Pipeline Ordering Divergence Is Genuine Grammar Modification

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / morphological construction
**Phase:** 409 (DARK_PIPELINE_INTERNAL_ARCHITECTURE)

## Finding

The 50% C1065 agreement rate (C1142) between dark-pipeline and general B atom ordering is **not explained** by the dark-exclusive atom pool. Dark-exclusive atoms appear in both matched and mismatched pairs with no significant enrichment in either direction.

### Contingency Table (Dark-Exclusive Presence x Match/Mismatch)

|  | Has Dark-Exc Atom | No Dark-Exc Atom | Total |
|--|-------------------|------------------|-------|
| **MATCH** | 5 | 2 | 7 |
| **MISMATCH** | 3 | 4 | 7 |
| **Total** | 8 | 6 | 14 |

### Fisher Exact Test

| Statistic | Value |
|-----------|-------|
| Odds ratio | 3.333 |
| p (two-sided) | 0.592 |

The odds ratio is >1 (dark-exclusive atoms slightly enriched in matches, not mismatches), but the effect is far from significant. This is the opposite direction from the hypothesis that dark-exclusive atoms cause ordering mismatches.

## Evidence

- Phase 409, Test 2: Fisher exact test on 14 tested C1065 pairs (7 MATCH, 7 MISMATCH)
- Pair-level analysis shows no systematic pattern: mismatched pairs include purely shared-atom pairs (ai/ka, eeo/te, ke/ok, eo/ke) as well as dark-exclusive pairs (ckh/eck)

## Implication

The dark pipeline's modified ordering grammar (50% C1065 agreement) is a **genuine structural modification**, not an artifact of using a different atom vocabulary. The dark-exclusive atoms are not systematically responsible for ordering reversals. This means the dark pipeline applies different sequencing rules to the same atoms, consistent with a genuine dialect operating on shared morphological infrastructure.

## Provenance

- Source: Phase 409, Test 2
- Related: C1142 (50% C1065 agreement), C1065 (atom bigram ordering grammar), C1143 (atom profile equivalence)
