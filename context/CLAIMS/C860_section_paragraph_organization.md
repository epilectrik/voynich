# C860: Section Paragraph Organization

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Sections organize paragraphs differently. HERBAL_B uses few (2.2/folio), large, cohesive paragraphs. RECIPE_B/PHARMA use many (10-14/folio), smaller paragraphs.

## Evidence

```
Section         Pars/Folio    Tokens/Par    Cohesion
HERBAL_B        2.2           49.8          0.070
BIO             7.5           46.0          0.071
RECIPE_B       10.2           38.3          0.053
PHARMA         14.0           12.6          0.056
```

## Section Profiles

- **HERBAL_B:** Minimal paragraph decomposition, comprehensive units
- **BIO:** Moderate decomposition, moderate units
- **RECIPE_B:** High decomposition, procedural steps
- **PHARMA:** Maximum decomposition, micro-instructions

## First Paragraph HT Rate

```
BIO:      Par 1 = 31.1%, Later = 39.9% (ratio 0.78x)
PHARMA:   Par 1 = 26.5%, Later = 38.4% (ratio 0.69x)
HERBAL_B: Par 1 = 37.2%, Later = 34.3% (ratio 1.09x)
```

BIO and PHARMA show reduced HT in Par 1; HERBAL_B is neutral.

## Related

- C552 (section role profiles)
- C858 (complexity correlation)
