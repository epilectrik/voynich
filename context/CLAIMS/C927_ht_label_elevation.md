# C927: HT Elevation in Label Contexts

## Status
- **Tier**: 2 (Structural)
- **Scope**: A, HT
- **Status**: CLOSED
- **Source**: Phase LABEL_INVESTIGATION

## Statement

HT tokens are 2.42x enriched in label regions (45.0%) vs paragraph text (18.6%). Chi-square = 107.33, p < 0.0001. This is INCONSISTENT with C926's prediction that HT should be suppressed in RI-rich contexts.

## Evidence

### Sample
- Mixed folios (labels + text): 17
- Label tokens: 280
- Paragraph tokens: 3,065

### HT Density by Region

| Region | HT Count | Total | HT Rate |
|--------|----------|-------|---------|
| Labels | 126 | 280 | 45.0% |
| Paragraphs | 569 | 3,065 | 18.6% |
| **Ratio** | - | - | **2.42x** |

### Statistical Test
- Chi-square: 107.33
- p-value: <0.0001
- Highly significant

### C926 Prediction Check

C926 states: RI is 0.48x in lines with HT (anti-correlation).
C914 states: Labels are 3.7x RI-enriched.

If C926 extended to labels, we'd expect: HT suppressed in label regions (inverse of 0.48x = ~2x suppression expected).

**Observed:** HT is 2.42x *enriched* in labels - opposite direction.

## Interpretation

Labels represent a different context than paragraph text:

1. **Labels are annotation, not processing**: They identify illustrated items, not encode procedures.

2. **HT vocabulary serves identification**: The elevated HT in labels suggests HT-derived vocabulary (PP + extension via HT prefixes) is used for labeling illustrations.

3. **C926 scope limit**: The HT-RI anti-correlation (C926) applies within text lines, not across the label/text boundary. Labels are outside the "spare capacity" framework.

### Functional Model

```
PARAGRAPH TEXT:
  - PP vocabulary dominates
  - HT appears during "spare capacity" periods
  - RI appears for instance identification
  - HT-RI anti-correlated (C926)

LABELS:
  - RI dominates (C914: 3.7x)
  - HT also elevated (C927: 2.42x)
  - Both derive from PP + extension (C924)
  - Annotation context, not "spare capacity"
```

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C914 | RI 3.7x enriched in labels |
| C924 | HT-RI shared derivation (PP + extension) |
| C926 | HT-RI anti-correlation in text - NOT in labels |
| C923 | Extension bifurcation (refined by C927 context) |

## Falsification Criteria

Disproven if:
1. Larger sample shows HT suppressed in labels
2. The 2.42x enrichment is explained by confound (section, folio)
3. HT vocabulary in labels is functionally different from HT in text

## Provenance

```
phases/LABEL_INVESTIGATION/scripts/t2_label_ht_patterns.py
phases/LABEL_INVESTIGATION/results/label_ht_patterns.json
```
