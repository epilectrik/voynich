# SECTION_ARCHITECTURE Phase Findings

**Date:** 2026-01-29
**Status:** COMPLETE

## Objective

Investigate structural differences between Currier B sections (BIO, HERBAL_B, PHARMA, RECIPE_B) to determine if they represent different program types or content variations.

## Key Findings

### 1. HT-EN Inverse Correlation

**Folio-level correlation: rho = -0.506** (strong inverse)

| HT Level | n paragraphs | HT Rate | EN Rate |
|----------|--------------|---------|---------|
| Low (<15%) | 98 | 10.5% | 39.8% |
| Medium | 207 | 21.9% | 30.9% |
| High (>30%) | 103 | 39.5% | 22.5% |

**Interpretation:** HT (identification vocabulary) and EN (execution vocabulary) are structural substitutes. High-HT content identifies/references, high-EN content executes operations.

### 2. Section Profiles (P+R placement text only)

| Section | Tokens | HT Rate | Character |
|---------|--------|---------|-----------|
| BIO | 6,195 | 21.9% | Execution-heavy |
| HERBAL_B | 2,675 | 32.3% | Balanced |
| PHARMA | 200* | 42.5% | Identification-heavy |
| RECIPE_B | 12,360 | 34.1% | Balanced |

*PHARMA text only (f57r + f66v). f66r is indexed format, counted separately.

### 3. f66r Is Unique Indexed Format

**Critical discovery:** f66r is NOT a standard text folio or AZC diagram.

Structure:
- **L-placement (15 tokens):** Paragraph-level index markers
- **M-placement (34 tokens):** Line-level single-character markers
- **R-placement (297 tokens):** Main text (74.3% B vocabulary overlap)

The R-placement text IS legitimate Currier B content, just in unusual layout. Margin labels (L/M) should be excluded from operational analysis.

**Documented in:** `data/folio_annotations/pharma/f66r.json`

### 4. PHARMA Is Genuinely Different

Even excluding f66r's margin labels, PHARMA text (f57r + f66v) has:
- Highest HT rate (42.5%)
- Smallest corpus (200 tokens)
- May represent reference/index material rather than operational procedures

## Constraints

No new Tier 2 constraints proposed. Findings are descriptive rather than structural rules.

**Key insight added to methodology:**
- R-placement does NOT always mean "ring diagram" - check folio annotations
- f66r requires special handling in any section-level analysis

## Files

| File | Purpose |
|------|---------|
| `results/section_census.json` | Baseline section profiles |
| `results/ht_en_inverse.json` | HT-EN correlation data |
| `results/pharma_text_only.json` | Corrected PHARMA counts |
| `data/folio_annotations/pharma/f66r.json` | f66r structure documentation |

## Implications

1. **Sections reflect program complexity** - not just content variation
2. **HT-EN tradeoff is systematic** - architectural, not random
3. **f66r handling matters** - exclude margin labels, include R-placement text
4. **PHARMA statistics are weak** - only 200 text tokens, use caution
