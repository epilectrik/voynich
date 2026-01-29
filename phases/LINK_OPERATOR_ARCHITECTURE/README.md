# LINK_OPERATOR_ARCHITECTURE Phase

## Objective

Characterize the LINK operator architecture. LINK ('ol' in token, 13.2% of B tokens) was under-documented relative to its importance. Recent findings (C802: HT clusters near LINK) suggested uncharacterized structure.

## Key Findings

### C366 Transition Grammar Not Reproducible (C804)

The specific enrichment claims in C366 are not reproducible:
- Predecessor AUXILIARY: claimed 1.50x, actual 1.03x
- Predecessor FLOW_OPERATOR: claimed 1.30x, actual 0.91x
- Successor HIGH_IMPACT: claimed 2.70x, actual 1.16x (AX)
- Successor ENERGY_OPERATOR: claimed 1.15x, actual 1.10x

Predecessor distribution: p = 0.41 (NOT significant)
Successor distribution: p < 0.001 (significant but weak)

### C365 Spatial Uniformity REFUTED (C805)

LINK is NOT spatially uniform. It shows boundary enrichment like HT:
- Mean position: 0.476 vs 0.504 (p < 0.0001, earlier in line)
- First token: 17.2% LINK rate
- Middle tokens: 12.4% LINK rate
- Last token: 15.3% LINK rate

### LINK-HT Positive Association (C806)

LINK and HT overlap moderately:
- Odds ratio: 1.50 (p < 0.001)
- 38.3% of LINK tokens are HT
- 16.6% of HT tokens are LINK
- Driven by vocabulary: HT contains 'ol' more often

### LINK-FL Inverse Relationship (C807)

LINK and FL (escape) are **inversely related**:
- LINK farther from FL: 3.91 vs 3.38 distance (p < 0.0001)
- Folio correlation: rho = -0.222, p = 0.045 (negative)
- Depleted around FL: pre-FL 0.67x, post-FL 0.87x

### LINK 'ol' is PP MIDDLE (C808)

'ol' is a legitimate morphological component:
- 759 occurrences as standalone MIDDLE
- Present in Currier A vocabulary (PP)
- LINK PP rate: 92.4% (similar to non-LINK 93.9%)

### LINK-Kernel Separation (C809)

LINK is separated from kernel operators (k, h, e):
- Depleted of kernel primitives: k 0.86x, h 0.93x, e 0.82x
- Farther from kernel tokens: 1.31 vs 0.41 distance (p < 0.0001)
- Transition rates at baseline (no enrichment)

## Scripts

| Script | Purpose | Key Finding |
|--------|---------|-------------|
| t1_link_transition_grammar.py | Verify C366 claims | Predecessor claims not confirmed |
| t2_link_position_distribution.py | Within-line spatial patterns | Boundary enrichment (C365 refuted) |
| t3_link_ht_cooccurrence.py | HT overlap mechanism | OR=1.50, vocabulary-driven |
| t4_link_escape_path.py | LINK-FL relationship | Inverse (farther, depleted) |
| t5_link_morphology.py | MIDDLE profile | 'ol' is PP MIDDLE |
| t6_link_kernel_contact.py | Kernel interaction | Separated (morphology + distance) |

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C804 | LINK Transition Grammar Revision | C366 claims not reproducible |
| C805 | LINK Positional Bias | C365 refuted, boundary enrichment |
| C806 | LINK-HT Positive Association | OR=1.50, vocabulary-driven |
| C807 | LINK-FL Inverse | Farther, depleted, negatively correlated |
| C808 | LINK 'ol' is PP MIDDLE | Legitimate morphological component |
| C809 | LINK-Kernel Separation | Distinct zone from kernel operations |

## Architectural Interpretation

LINK marks **monitoring/waiting zones** that are distinct from both:
1. **Kernel operations** (k, h, e) - active processing
2. **Escape operations** (FL) - recovery/intervention

LINK occupies a third phase in the control loop:
```
[KERNEL processing] → [LINK monitoring] → [FL escape if needed]
```

This explains:
- Why HT clusters near LINK (C802): monitoring checkpoints
- Why HT correlates with escape at folio level (C796): high-escape folios have more monitoring
- Why LINK is inversely related to FL: complementary phases, not co-located

## Revisions to Existing Constraints

- **C365:** REFUTED (LINK is NOT spatially uniform)
- **C366:** Transition grammar claims need revision (enrichment ratios not reproducible)

## Dependencies

- C366 (LINK marks transitions - qualitative claim supported)
- C609 (LINK density 13.2% - confirmed)
- C802 (HT clusters near LINK - explained via C806)
- C796 (HT-escape correlation - reconciled via C807)

## Data Sources

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `scripts/voynich.py` (Transcript, Morphology)
