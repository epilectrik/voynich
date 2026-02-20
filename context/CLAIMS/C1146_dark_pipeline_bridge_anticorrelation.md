# C1146: Dark Pipeline Token Density Anti-Correlates with Bridge Tokens

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / A->B pipeline architecture
**Phase:** 409 (DARK_PIPELINE_INTERNAL_ARCHITECTURE)

## Finding

Per-folio dark-pipeline token rate is **strongly anti-correlated** with bridge token rate (r = -0.865) and positively correlated with general HT rate (r = 0.715). Section identity explains only 19.3% of dark-pipeline density variance; the bridge anti-correlation persists within every section.

### Variance Decomposition

| Component | Value |
|-----------|-------|
| Grand mean dark rate | 7.40% |
| Section R² | 0.193 |
| Within-section fraction | 80.7% |
| SS total | 0.057 |

### Section Means

| Section | Mean Dark Rate | n Folios |
|---------|---------------|----------|
| T | 11.2% | 2 |
| C | 8.5% | 5 |
| S | 8.2% | 23 |
| H | 7.5% | 32 |
| B | 5.7% | 20 |

### Correlation Structure

| Correlation | Overall | B (n=20) | C (n=5) | H (n=32) | S (n=23) |
|-------------|---------|----------|---------|----------|----------|
| dark vs HT | 0.715 | 0.586 | 0.819 | 0.623 | 0.782 |
| **dark vs bridge** | **-0.865** | **-0.880** | **-0.835** | **-0.819** | **-0.868** |

The bridge anti-correlation is remarkably stable across all four testable sections (r = -0.82 to -0.88), indicating this is not a section confound. Within any given section, folios with more bridge-grammar tokens systematically have fewer dark-pipeline tokens.

## Evidence

- Phase 409, Test 4: ANOVA-style R² for section, Pearson r for folio-level rates
- 82 folios analyzed (1 folio excluded due to zero tokens after filtering)
- Dark rate = dark_tokens / total_tokens per folio; bridge rate = bridge_tokens / total_tokens per folio

## Implication

Dark-pipeline and bridge MIDDLEs are in **complementary distribution** at the folio level. This is the strongest structural finding of Phase 409: the two A->B vocabulary channels (85 bridge MIDDLEs carrying grammar structure, 300 dark-pipeline MIDDLEs carrying HT identification vocabulary) trade off within folios. Folios that invest more tokens in grammar execution (bridge) invest fewer in identification (dark pipeline), and vice versa.

This is consistent with a fixed total token budget per folio, where the allocation between grammar and identification channels varies. Section identity modulates the baseline rate (R²=0.19) but the complementary distribution is the dominant signal (within-section R² from bridge alone would be ~0.67-0.77).

## Provenance

- Source: Phase 409, Test 4
- Related: C1139 (bridge-dark disjoint), C1013 (85 bridges), C1137 (dark pipeline HT substrate), C1140 (four-way partition)
