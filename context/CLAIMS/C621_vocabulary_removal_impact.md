# C621: Vocabulary Removal Impact

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** UNIQUE_VOCABULARY_ROLE

## Statement

Removing all 868 tokens carrying unique MIDDLEs from B preserves 96.2% of token volume (22,228/23,096) with negligible grammatical impact: mean max role shift is 2.80 pp per folio, max shift is 7.04 pp, and only 1/82 folios loses ICC role coverage. The removal affects only UN tokens (UN drops -2.71 pp globally). Unique vocabulary is structurally dispensable — it contributes token volume but not grammatical diversity.

## Evidence

### Token Survival

| Metric | Value |
|--------|-------|
| Tokens before | 23,096 |
| Tokens after | 22,228 (96.2%) |
| Removed | 868 (3.8%) |
| Mean folio survival | 96.0% |
| Min folio survival | 89.4% |
| Max folio survival | 100.0% |
| Folios retaining >95% | 55/82 |

### Role Distribution Shift

| Role | With unique | Without | Shift |
|------|-----------|---------|-------|
| EN | 31.2% | 32.4% | +1.22 pp |
| AX | 17.9% | 18.6% | +0.70 pp |
| FQ | 12.5% | 13.0% | +0.49 pp |
| FL | 4.7% | 4.8% | +0.18 pp |
| CC | 3.2% | 3.3% | +0.12 pp |
| UN | 30.5% | 27.8% | -2.71 pp |

Only UN decreases. All classified roles increase proportionally due to denominator reduction.

### Per-Folio Impact

| Metric | Value |
|--------|-------|
| Mean max role shift | 2.80 pp |
| Max role shift (any folio) | 7.04 pp |
| Folios with shift >5 pp | 7/82 |
| Folios losing ICC role | 1/82 |

The 1 folio losing ICC role coverage is a marginal case (small folio with one rare role represented only by a unique MIDDLE token).

## Interpretation

C535's "vocabulary minimality" (81/82 folios needed for complete MIDDLE coverage) is numerically accurate but does not imply functional necessity. The 858 unique MIDDLEs contribute 3.8% of token volume and zero classified tokens. Their removal is invisible to the grammar: role distributions barely shift, hazard classes are unaffected, and 81/82 folios retain full ICC role coverage.

The vocabulary coverage metric measures MIDDLE TYPE diversity, not behavioral diversity. Each folio needs unique MIDDLEs for type coverage completeness, but not for grammatical execution.

## Refines

- **C535**: Confirms 81/82 folios needed for type coverage. Qualifies: coverage is for type diversity, not functional necessity. Removing unique vocabulary preserves 96.2% of tokens with <3 pp role shift.

## Related

C531, C535, C618, C619, C620
