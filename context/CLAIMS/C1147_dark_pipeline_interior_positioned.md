# C1147: Dark Pipeline Tokens Are Interior-Enriched Within Lines

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / line structure
**Phase:** 409 (DARK_PIPELINE_INTERNAL_ARCHITECTURE)

## Finding

Dark-pipeline tokens preferentially occupy line-interior positions (73.2% MIDDLE), significantly more so than general HT tokens (67.7% MIDDLE), with fewer tokens at line boundaries.

### Line Position Distribution

| Position | Dark Pipeline | General HT | Grammar |
|----------|--------------|------------|---------|
| FIRST | 15.3% (260) | 16.5% (880) | 8.0% (1,280) |
| MIDDLE | 73.2% (1,241) | 67.7% (3,618) | 83.5% (13,403) |
| LAST | 11.5% (195) | 15.9% (848) | 8.5% (1,371) |
| **Total** | **1,696** | **5,346** | **16,054** |
| **Boundary rate** | **26.8%** | **32.3%** | **16.5%** |

### Chi-Square Tests

| Comparison | Chi-square | df | p |
|------------|-----------|-----|---|
| Dark vs General HT | 23.21 | 2 | < 0.0001 |
| Dark vs Grammar | 130.69 | 2 | < 0.0001 |

### Paragraph Stratification

| Context | Dark MIDDLE% (n) | HT MIDDLE% (n) |
|---------|-------------------|-----------------|
| Paragraph line-1 | 76.6% (602) | 68.6% (1,765) |
| Body lines | 71.3% (1,094) | 67.2% (3,581) |

Interior enrichment is consistent across both paragraph contexts. Line-1 dark tokens are even more interior-enriched (76.6%) than body dark tokens (71.3%).

## Evidence

- Phase 409, Test 5: Position classified by token index within line (0=FIRST, last=LAST, else MIDDLE)
- 1,696 dark-pipeline tokens, 5,346 general HT (non-dark, non-grammar), 16,054 grammar tokens
- Single-token lines classified as FIRST

## Implication

Dark-pipeline tokens are structurally intermediate between general HT and grammar in their positional behavior. They avoid line boundaries more than general HT but less than grammar tokens. This interior preference means dark-pipeline tokens are embedded within the line's structural flow rather than anchoring line boundaries — consistent with their role as identification vocabulary that fills the interior of lines while grammar tokens provide the structural skeleton.

## Provenance

- Source: Phase 409, Test 5
- Related: C1137 (dark pipeline HT substrate), C803 (HT positional rates), C1138 (dark pipeline distinct construction grammar)
