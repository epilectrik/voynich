# Phase Summary: EXTENSION_DISTRIBUTION_PATTERNS

## Verdict: MIXED RESULTS

The extension operational context model is partially supported. Key finding: **labels have dramatically different extension profile than text**, with r-extension 10.9x enriched in labels.

## Test Results

### Test 1: Extension Section Profile
**Verdict: NULL RESULT**

- Chi-square p = 0.24 (not significant)
- Extensions distribute fairly uniformly across sections H, P, T
- Section concentration follows overall A content distribution

**Interpretation:** Sections don't strongly specialize by extension/operation type. This could mean:
1. Operational context doesn't map to manuscript sections
2. Sample sizes insufficient (only 512 total extension tokens in A)
3. Sections organize by topic, not operation type

### Test 2: Zodiac Folio Patterns
**Verdict: f57v is STRUCTURALLY UNIQUE**

| Metric | f57v | Other Zodiac (f70-f73) |
|--------|------|------------------------|
| Single-char rings (>=75%) | 2 (R2, R4) | 0 |
| h-rate overall | 4.3% | 7.4% |
| 100% single-char ring | YES (R2) | NO |
| 12-char period | YES (R2) | NO |

Fisher's exact p = 0.022 for h-rate difference.

**Interpretation:** f57v's pattern does NOT replicate on other zodiac folios. This suggests:
1. f57v serves a unique function among cosmological folios
2. The 12-char period / extension reference is f57v-specific, not zodiac-wide
3. Other zodiac folios use standard multi-char tokens (like Currier B text)

### Test 3: Label Extension Profile
**Verdict: HIGHLY SIGNIFICANT (p = 0.0005)**

| Extension | Label % | Text % | Enrichment | Significance |
|-----------|---------|--------|------------|--------------|
| **r** | 32% | 3% | **10.9x** | p < 0.0001 |
| a | 12% | 7% | 1.7x | - |
| k | 8% | 4% | 2.1x | - |
| o | 24% | 16% | 1.5x | - |
| **h** | 0% | 11% | **0x** | p = 0.096 |
| **d** | 0% | 9% | **0x** | - |
| **t** | 0% | 6% | **0x** | - |

**Interpretation:** Labels show dramatically different extension usage:
- **r-extension dominates labels** (32% vs 3% in text)
- **h/d/t extensions absent from labels** (0% in all cases)
- Labels use identification extensions (r, a, o), not operational extensions (h, d, t)

## New Findings for Constraint System

### Tier 2 Candidates

1. **f57v Structural Uniqueness** (extends C920-C922)
   - f57v's single-char ring pattern unique among zodiac/cosmological folios
   - Other zodiac folios use standard multi-char tokens

2. **Label Extension Bifurcation** (NEW)
   - r-extension 10.9x enriched in labels (p < 0.0001)
   - h/d/t extensions categorically absent from labels
   - Labels vs text show distinct extension profiles (p = 0.0005)

### Tier 3/4 Interpretations

1. **r = identification/reference extension**
   - Used for labeling/identifying illustrated items
   - Not used for operational context

2. **h/d/t = operational context extensions**
   - Used in text for procedural specification
   - Not used in identification/labeling

3. **Extension functional bifurcation**
   - Identification set: r, a, o, k
   - Operational set: h, d, t
   - This maps to label vs text usage

## Implications

1. **f57v is special** - Not a template for other zodiac folios. Its 12-char period / extension reference pattern is unique, possibly serving as a master reference or calendar.

2. **Extensions have functional categories** - Not all extensions serve the same purpose. Labels reveal that r/a/o are for identification, while h/d/t are for operational specification.

3. **The label finding refines C918** (A as operational configuration layer) - A uses extensions for BOTH:
   - Instance identification (labels): r, a, o extensions
   - Operational parameterization (text): h, d, t extensions

## Recommended Next Steps

1. Document the label extension bifurcation as C923
2. Investigate what r-extension specifically encodes (why 10.9x in labels?)
3. Examine the 25 label extension tokens in detail - what are they labeling?
