# C914: RI Label Enrichment

**Tier:** 2 (Structural)
**Scope:** A
**Status:** CLOSED
**Phase:** RI_EXTENSION_MAPPING

---

## Statement

RI vocabulary is 3.7x enriched in illustration labels (27.3% RI rate) vs paragraph text (7.4% RI rate). Labels identify specific illustrated items, requiring instance-specific vocabulary built via the PP+extension derivational system (C913).

---

## Evidence

**Phase:** RI_EXTENSION_MAPPING (2026-02-04)

**Primary findings:**

| Context | RI Rate | PP Rate | RI Tokens |
|---------|---------|---------|-----------|
| Labels | 27.3% | 72.7% | 411 |
| Text | 7.4% | 92.6% | 822 |
| **Ratio** | **3.7x** | - | - |

**Label types with highest RI concentration:**
- L01-L06 label placements show consistent RI enrichment
- RI tokens in labels are predominantly single-character extensions of PP roots

**Extension patterns in labels vs text:**
- Labels and text use the same extension characters
- No label-specific extensions identified
- Same PP + different extension appears in both contexts

**Source:** `scratchpad/what_does_ri_reference.py`, `scratchpad/ri_label_analysis.py`

---

## Implications

1. **Labels require instance-specificity** - labels point to specific illustrated items, not general categories
2. **RI extensions are identifiers** - when labeling illustration 3 vs illustration 7, different extensions are used
3. **Text uses general vocabulary** - paragraph text discusses categories/procedures using PP
4. **Consistent derivational system** - labels use the same PP+extension mechanism, just more frequently

---

## Functional Model

```
ILLUSTRATION: Plant drawing #3
    |
    +-- PP MIDDLE 'od' = general concept (shared with text, shared with B)
    |
    +-- RI MIDDLE 'odo' = THIS specific plant instance (label)
        (extension 'o' marks instance identity)
```

---

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C913 | Derivational morphology - mechanism for creating RI from PP |
| C498 | RI definition - label context explains function |
| C833 | RI first-line concentration - labels are de facto "first lines" |
| C915 | Section P entries - another context requiring instance-specificity |
