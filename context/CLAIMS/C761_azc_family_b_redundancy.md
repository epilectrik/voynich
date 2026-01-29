# C761: AZC Family B-Coverage Redundancy

**Status:** VALIDATED | **Tier:** 2 | **Phase:** AZC_FOLIO_DIFFERENTIATION | **Scope:** AZC, B

## Finding

Zodiac and A/C families provide redundant B vocabulary coverage. They do not serve different B folios.

### Evidence

Paired comparison of same B folios:

| Metric | Zodiac | A/C |
|--------|--------|-----|
| Mean B coverage | 68.1% | 67.5% |
| Standard deviation | 10.2% | 10.3% |

**Paired t-test:** t=1.20, p=0.23 (not significant)
**Wilcoxon signed-rank:** W=984, p=0.44 (not significant)
**Coverage correlation:** r=**0.903**, p<0.001

### B Folio Preference Distribution

| Category | B Folios |
|----------|----------|
| Zodiac-preferred (ratio > 1.2) | 1 |
| A/C-preferred (ratio < 0.8) | 0 |
| Balanced (0.8-1.2) | 81 |

81 of 82 B folios receive balanced coverage from both families.

### Family-Exclusive Vocabulary Impact

| Metric | Value |
|--------|-------|
| Zodiac-only MIDDLEs | 233 |
| A/C-only MIDDLEs | 233 |
| B folios using Zodiac-only | 79 (96.3%) |
| B folios using A/C-only | 79 (96.3%) |
| Mean Zodiac-only per B folio | 5.76 |
| Mean A/C-only per B folio | 5.28 |

Both families contribute ~5-6 exclusive MIDDLEs per B folio.

## Implication

1. **Families are functionally equivalent for B.** The Zodiac/A/C distinction does not create different B coverage profiles.

2. **Difference is structural, not functional.** C430 notes Zodiac is "uniform scaffold reused" while A/C is "varied scaffolds." This is about internal organization, not B serving.

3. **Supports "shared vocabulary pool" model.** Both families draw from the same operational vocabulary to constrain B.

4. **Not "routing" - both families cover all B.** There's no preferential A->Zodiac->B1 vs A->A/C->B2 pattern.

## Provenance

- Phase: AZC_FOLIO_DIFFERENTIATION
- Script: t7_family_b_coverage.py
- Related: C430 (Bifurcation), C753 (No Content Routing)
