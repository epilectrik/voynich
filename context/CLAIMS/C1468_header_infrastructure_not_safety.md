# C1468: Header Infrastructure-First Composition (Not Safety-First)

**Tier:** 2
**Scope:** B, paragraph, header, hazard, LOW, ZERO, IMMUNE, composition, C1287, C1426, C1463, C1467
**Phase:** 529 (PARAGRAPH_HAZARD_GRADIENT)
**Date:** 2026-03-05

## Claim

Paragraph headers (first lines) have a distinctive hazard composition dominated by LOW-class tokens (1.130x enriched, 51.6% of header tokens) while ZERO and IMMUNE classes are both depleted (0.784x and 0.793x respectively). This contrasts sharply with line-level SPECIFICATION zones (C1463), where ZERO (e->y safe pathway) is enriched 1.236x and LOW is near baseline. Headers specify operations using infrastructure vocabulary, not safety vocabulary. The e->y safe pathway (C1457-C1462) is specifically depleted at headers (0.796x), concentrating instead in BODY lines (1.077x). k-HEAD IMMUNE tokens follow the same pattern: depleted at HEADER (0.793x), enriched at BODY (1.121x).

## Evidence

### Header vs Body vs Tail Hazard Profiles

| Metric | HEADER | BODY | TAIL |
|--------|--------|------|------|
| HIGH% | 21.9% | 19.4% | 23.5% |
| LOW% | **51.6%** | 43.8% | 42.9% |
| ZERO% | **15.8%** | 21.7% | 21.6% |
| IMMUNE% | **10.6%** | 15.1% | 12.1% |

Header vs Body divergence: chi2=198.3, p=9.62e-43, V=0.101 (strongest pairwise comparison).

### Safe Pathway (e->y) Depletion at Headers

| Zone | e->y enrichment |
|------|----------------|
| HEADER | **0.796x** (depleted) |
| BODY | 1.077x (enriched) |
| TAIL | 1.052x (enriched) |

e->y mean paragraph position: 0.492 (later than overall 0.467). Mann-Whitney e->y vs HIGH in paragraph position: p=0.007, r=-0.035 (e->y is later, not earlier as it is at line level).

### k-IMMUNE Depletion at Headers

| Zone | IMMUNE enrichment |
|------|------------------|
| HEADER | **0.793x** (depleted) |
| BODY | **1.121x** (enriched) |
| TAIL | 0.900x (depleted) |

## Interpretation

The line and paragraph levels use DIFFERENT specification strategies:

- **Line SPECIFICATION (C1463):** Uses categorically SAFE vocabulary (e->y frame, 0% hazard). The line opens with pre-emptive safety anchors.

- **Paragraph HEADER:** Uses INFRASTRUCTURE vocabulary (LOW class = default/uncharacterized frame hazard). These are the MARKING/STAGING tokens identified by C1287 -- they specify what the paragraph will do, using vocabulary that is not characterized as either safe or hazardous.

This resolves an apparent tension: if safe vocabulary concentrated at both line-initial AND paragraph-initial, there would be redundant safety layering. Instead, the two levels serve complementary functions: paragraphs open with specification (infrastructure), lines open with safety (e->y). The safety architecture operates WITHIN lines, not at paragraph boundaries.

## Falsification Criteria

1. If HEADER LOW enrichment drops below 1.05x
2. If HEADER ZERO enrichment rises above 1.05x (would indicate safety-first)
3. If e->y HEADER enrichment exceeds 1.0x
4. If HEADER vs BODY V drops below 0.05

## Method

- 23,090 Currier B tokens
- 590 paragraphs (gallows-initial boundaries per C864)
- Frame hazard classes from decoder_maps.json
- Chi-squared contingency with Cramer's V

**Script:** `phases/PARAGRAPH_HAZARD_GRADIENT/scripts/paragraph_hazard_gradient.py`
**Results:** `phases/PARAGRAPH_HAZARD_GRADIENT/results/paragraph_hazard_gradient.json`

## Dependencies

- C1287 (paragraph headers MARKING-enriched)
- C1426 (line-initial specification profile)
- C1457-C1462 (e->y safe pathway)
- C1463 (line-level zone-hazard routing -- contrasting pattern)
- C1467 (paragraph zone x hazard interaction -- parent finding)
