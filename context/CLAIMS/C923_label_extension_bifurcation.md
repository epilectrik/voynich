# C923: Label Extension Bifurcation (r/h Axis)

## Status
- **Tier**: 2 (Structural)
- **Scope**: A
- **Status**: CLOSED
- **Source**: Phase EXTENSION_DISTRIBUTION_PATTERNS, LABEL_INVESTIGATION

## Statement

Extensions r and h mark the label/text boundary:
- **r-extension**: 4.9x enriched in labels (p<0.0001)
- **h-extension**: Categorically absent from labels (0% across all 11 folios, p=0.0002)
- **a-extension**: Moderately enriched (2.3x, p=0.012)

The broader groupings (r,a,o,k vs h,d,t) are NOT confirmed - o and d do not differentiate.

## Evidence

### LABEL_INVESTIGATION Phase (2026-02-05)

**Sample sizes:**
- Label extension tokens: 87 (3.5x larger than original n=25)
- Text extension tokens: 1,013
- Total: 1,100

### Per-Extension Analysis

| Extension | Label % | Text % | Enrichment | p-value | Verdict |
|-----------|---------|--------|------------|---------|---------|
| **r** | 17.2% | 3.6% | **4.9x** | <0.0001 | STRONG |
| **h** | 0.0% | 10.4% | **0.0x** | 0.0002 | STRONG |
| **a** | 13.8% | 6.1% | 2.3x | 0.0121 | MODERATE |
| o | 14.9% | 17.6% | 0.9x | 0.66 | NO EFFECT |
| d | 9.2% | 9.5% | 1.0x | 1.0 | NO EFFECT |
| k | 1.1% | 4.8% | 0.2x | 0.17 | MARGINAL |
| t | 1.1% | 5.2% | 0.2x | 0.12 | MARGINAL |

### Cross-Folio Consistency

| Pattern | Consistency |
|---------|-------------|
| **h-absence (0%)** | **11/11 folios (100%)** |
| r-enrichment (>10%) | 7/11 folios (64%) |

**h-absence is universal** - not a single h-extension appears in any label across all folios.

### Statistical Summary

Aggregated ID (r,a,o,k) vs OP (h,d,t) test:
- Chi-square: 11.62
- p-value: 0.00065
- Cramér's V: 0.136 (small effect)

## Revised Interpretation

The original claim of two broad groups (ID vs OP) is **too coarse**. The refined model:

| Extension | Context | Function | Strength |
|-----------|---------|----------|----------|
| **r** | Labels | Instance identification | STRONG (4.9x) |
| **a** | Labels | Instance identification | MODERATE (2.3x) |
| **h** | Text only | Monitoring/operational | STRONG (0% in labels) |
| o, d, k, t | Mixed | No clear label/text split | NOT CONFIRMED |

### Functional Model

```
A Entry = [PREFIX + MIDDLE + SUFFIX] + [EXTENSION]
                                           |
                               KEY EXTENSIONS:
                                           |
              +----------------+-----------+----------------+
              |                |                            |
            r (4.9x)      a (2.3x)                    h (0%)
        Identification   Identification            Operational
         (labels)         (labels)                 (text only)
              |                |                            |
              +-------+--------+                            |
                      |                                     |
              Instance markers                    Monitoring/process
```

## Tier 2 Justification

Promoted from Tier 3 based on:
1. **Sample size**: 87 label extensions (vs original 25)
2. **h-absence robustness**: 100% consistent across 11 folios
3. **r-enrichment significance**: p<0.0001
4. **Cross-validation**: Pattern holds across independent folios

The small Cramér's V (0.136) reflects that only r and h strongly differentiate. The aggregate ID/OP test is diluted by o and d not bifurcating.

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C914 | RI Label Enrichment (3.7x) - r/h pattern underlies this |
| C917 | Extension-Prefix Alignment - h aligns with ct- prefix |
| C918 | A as Operational Configuration - h is operational |
| C927 | HT Label Elevation - labels use HT-derived vocabulary |

## Falsification Criteria

Disproven if:
1. h-extension appears in labels at >5% rate in larger sample
2. r-enrichment disappears with more data
3. Cross-folio consistency falls below 50%

## Provenance

```
phases/EXTENSION_DISTRIBUTION_PATTERNS/results/label_extension_profile.json (original)
phases/LABEL_INVESTIGATION/scripts/t1_extension_validation.py (validation)
phases/LABEL_INVESTIGATION/scripts/t3_crossfolio_consistency.py (robustness)
phases/LABEL_INVESTIGATION/results/extension_validation.json
phases/LABEL_INVESTIGATION/results/crossfolio_consistency.json
```
