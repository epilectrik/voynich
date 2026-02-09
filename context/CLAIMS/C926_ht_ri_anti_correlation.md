# C926: HT-RI Line-Level Anti-Correlation

## Status
- **Tier**: 2 (STRUCTURAL)
- **Scope**: A
- **Status**: CLOSED
- **Source**: Phase EXTENSION_DISTRIBUTION_PATTERNS

## Statement

HT and RI are anti-correlated at line level within Currier A (0.48x enrichment, chi2=105.83, p<0.0001). Despite sharing derivational morphology (C924), they partition vocabulary space rather than co-occur. HT tracks discrimination complexity (C461); RI encodes specific instances (C916).

## Evidence

### Line-Level Co-Occurrence

| Metric | Value |
|--------|-------|
| Lines with HT | 3,460 |
| Lines without HT | 980 |
| RI rate in lines WITH HT | 1.98% |
| RI rate in lines WITHOUT HT | 4.16% |
| **Enrichment** | **0.48x** |
| Chi-square | 105.83 |
| p-value | < 0.0001 |

RI is significantly LESS common in lines where HT appears.

### Folio-Level Correlation

| Metric | Value |
|--------|-------|
| Folios with both HT and RI | 112 |
| Correlation (HT rate vs RI rate) | r = 0.164 |
| p-value | 0.083 (not significant) |

Weak positive at folio level - the effect is line-positional, not folio-compositional.

### Shared PP Bases

| Metric | Value |
|--------|-------|
| Average PP base overlap per folio | 1.3 |
| Average Jaccard similarity | 0.060 |

HT and RI reference different PP bases even within the same folio.

### Dual-Use PP Bases

| Metric | Value |
|--------|-------|
| PP bases with both HT and A/B prefixes | 316 |
| Total PP bases with any prefix | 1,018 |
| Dual-use rate | 31.0% |

Despite anti-correlation, 31% of PP bases CAN appear with either prefix type - confirming shared vocabulary access (C924).

## Interpretation

### Complementary Modes

HT and RI share the same derivational system (C924) but serve **complementary functions**:

| Layer | Function | Mode |
|-------|----------|------|
| HT | Tracks discrimination complexity | Annotation/reference |
| RI | Encodes specific discriminations | Instance identification |

They respond to the same underlying complexity but in different modes, partitioning the space rather than co-occurring.

### Not "Working Together"

The anti-correlation indicates HT and RI are **alternative access modes**, not coordinated systems:
- Same vocabulary (PP + extension)
- Different prefixes (HT vs A/B)
- Different positions (don't co-occur)
- Different functions (tracking vs encoding)

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C924 | HT-RI Shared Derivational Morphology - same system, different modes |
| C461 | HT correlates with rare MIDDLEs - tracks complexity |
| C916 | RI Instance Identification - encodes instances |
| C452 | HT Unified Prefix Vocabulary - consistent across systems |
| C404 | HT Terminal Independence - HT is non-operational |

## Falsification Criteria

Disproven if:
1. Larger analysis shows HT-RI co-occurrence (enrichment > 1.0)
2. The anti-correlation is explained by A vs B system mixing
3. HT and RI shown to reference same PP bases at same positions
