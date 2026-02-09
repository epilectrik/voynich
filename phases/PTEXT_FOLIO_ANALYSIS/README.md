# Phase: PTEXT_FOLIO_ANALYSIS

**Status:** COMPLETE
**Date:** 2026-01-31
**Verdict:** STRUCTURAL INSIGHT

---

## Objective

Investigate why P-text (paragraph text) appears on 9 specific AZC folios, what distinguishes it from regular Currier A, and whether its placement is structurally meaningful.

---

## Background

C758 established that P-text is linguistically Currier A (0.974 PREFIX cosine), not AZC diagram material. This phase investigates the implications of that finding.

---

## Test Results

### Test 1: Folio Characteristics

| Finding | Value |
|---------|-------|
| P-text folios | 9 of 29 AZC folios |
| Folio range | f65v to f70r2 |
| All A/C family | Yes (none in Zodiac) |
| Foldout indicators | 7 of 9 folios |

**Anomaly:** f65v is 100% P-text with 0 diagram tokens.

### Test 2: P-text vs Currier A Vocabulary

| Metric | P-text | Currier A | Diagram |
|--------|--------|-----------|---------|
| Tokens | 397 | 11,346 | 2,830 |
| MIDDLEs | 129 | 1,052 | 605 |
| PREFIX cosine to P-text | 1.000 | **0.974** | 0.825 |

**Conclusion:** P-text is linguistically Currier A, not AZC diagram.

### Test 3: Same-Folio Relationship

| Metric | Value |
|--------|-------|
| Mean Jaccard (P-text to same-folio diagram) | **0.195** |
| Baseline (P-text to cross-folio diagram) | 0.040 |
| Difference | +0.156 |

**Conclusion:** P-text vocabulary has HIGHER overlap with same-folio diagram than baseline, suggesting content relationship.

### Test 4: Pipeline Position

| Metric | P-text | General A |
|--------|--------|-----------|
| MIDDLEs appearing in B | **76.7%** | 39.9% |
| Correlation (P-text usage vs B TTR) | r=0.524, p<0.0001 |

**Conclusion:** P-text vocabulary has **privileged transmission to B** and correlates significantly with high-escape B behavior, confirming C486.

### Test 5: Constraint Audit

**Reframed:**
- C492: `ct` PREFIX exclusive to P-text (not "P-zone")
- C486: P-text vocabulary correlates with high-escape B (strengthened)

**Correct as-is:**
- C758: P-text Currier A identity

---

## Key Findings

1. **P-text is a Currier A vocabulary subset** that appears on 9 specific AZC folios (f65v-f70r2), not a diagram position.

2. **P-text has privileged B transmission** (76.7% vs 39.9%) suggesting it represents a "core" or "active" subset of Currier A vocabulary.

3. **P-text relates to same-folio diagrams** (0.195 vs 0.040 Jaccard) suggesting content coordination, not independent annotation.

4. **f65v is anomalous** - entirely P-text with no diagram, unique among AZC folios.

5. **C486 is strengthened** - the correlation with high-escape B is vocabulary-based, not positional, which is a stronger finding.

---

## Interpretation (Tier 3)

P-text may represent **Currier A entries that are explicitly associated with AZC diagrams** - a registry subset that:
- Appears as paragraph annotations on diagram folios
- Has content relationship to adjacent diagrams
- Has high transmission rate to B execution
- Correlates with B escape behavior

This suggests P-text is not "text that happens to be on AZC folios" but rather "A entries that are tagged for diagram association."

---

## Constraint Updates

Updated:
- C492: Added reframing note, corrected "P-zone" to "P-text"
- C486: Added reframing note, corrected "P-zone" to "P-text vocabulary"

---

## Files

```
phases/PTEXT_FOLIO_ANALYSIS/
├── README.md
└── scripts/
    ├── t1_folio_characteristics.py
    ├── t2_ptext_vs_currier_a.py
    ├── t3_ptext_diagram_relation.py
    ├── t4_ptext_pipeline_position.py
    └── t5_constraint_audit.py
```

---

## Extended Investigation: Rosettes (Tests 11-26)

### Rosettes Classification

| Finding | Value |
|---------|-------|
| Rosettes sub-folios | f85r1, f85r2, f86v3-f86v6 |
| Total tokens | 1,847 |
| Currier classification | **B** (0.954 cosine) |
| Section | B (Balneological) |

**Conclusion:** Rosettes are Currier B, not AZC. They appear to be B execution text.

### Rosettes-Brunschwig Fit (Test 25)

| Metric | Value |
|--------|-------|
| Overlap with S-section | 62.9% |
| Circle count | 9 |
| Brunschwig fire degrees | 4 |

**Problem:** 9 circles don't map to Brunschwig's 4 fire degrees. The Brewer-Lewis hypothesis (9 circles = 7 uterine chambers + 2 vaginal openings) is iconographic and not testable through text analysis.

### Circle Vocabulary Differentiation (Test 26)

| Metric | Value |
|--------|-------|
| Mean within-Rosettes Jaccard | 0.304 |
| Mean random B folio Jaccard | 0.198 |
| Circle-unique vocabulary | 21-42% per circle |

**Conclusion:** Circles have moderate vocabulary overlap, similar to random B folios. No evidence for strong chamber-specific vocabulary.

---

## Extended Investigation: Trotula Comparison (Tests 21-24)

Compared Voynich B grammar to Trotula gynecological recipes to test medical text hypothesis.

| Feature | Trotula | Voynich B |
|---------|---------|-----------|
| Role distribution | 78% OUTPUT, 17% MONITORING | 42% OUTPUT, 35% MONITORING |
| Control complexity | Simple (ingredient → application) | Complex (monitoring-heavy) |
| Scheduling | Day-based | Kernel-centric |

**Conclusion:** Trotula recipes are too simple to match Voynich B structure. Voynich B's monitoring-heavy grammar suggests process control, not recipe execution.

---

## Extended Investigation: f65v Anomaly (Tests 27-29)

### f65v/f66v Identification (Test 28)

Only 2 AZC folios are 100% P-text:

| Folio | Tokens | Cosine to A | Cosine to B |
|-------|--------|-------------|-------------|
| f65v | 44 | **0.941** | 0.847 |
| f66v | 103 | **0.941** | 0.847 |

Both are linguistically Currier A despite being in the cosmological section.

### Physical Layout (Test 29)

```
f65v (P-text) | f66r (ring diagram) | f66v (P-text)
```

f66r contains 295 tokens, all in R (ring) placement - a zodiac-style diagram.

### Vocabulary Relationship

| Comparison | Shared MIDDLEs | Jaccard |
|------------|----------------|---------|
| f65v ↔ f66r | 63.3% | 0.261 |
| f66v ↔ f66r | 59.0% | 0.240 |
| f65v ↔ f66v | - | 0.524 |

**Conclusion:** f65v and f66v are **Currier A text pages** that serve as annotations or material specifications for the f66r zodiac diagram. High vocabulary overlap confirms content relationship, not misplacement.

---

## Final Summary

1. **P-text is Currier A** - not diagram labels, but paragraph text that appears on 9 AZC folios
2. **P-text has privileged B transmission** - 76.7% vs 39.9% general A
3. **f65v/f66v are annotation pages** - linguistically A, physically flanking f66r zodiac
4. **Rosettes are Currier B** - not AZC, with 9 circles that don't map to Brunschwig
5. **Trotula comparison fails** - Voynich B is too monitoring-heavy for simple recipes

---

## Constraints Documented

- C492: `ct` PREFIX exclusive to P-text (updated)
- C486: P-text vocabulary correlates with high-escape B (strengthened)
- C758: P-text Currier A identity (confirmed)

---

## Files

```
phases/PTEXT_FOLIO_ANALYSIS/
├── README.md
└── scripts/
    ├── t1_folio_characteristics.py     # P-text folio mapping
    ├── t2_ptext_vs_currier_a.py        # Linguistic classification
    ├── t3_ptext_diagram_relation.py    # Same-folio relationship
    ├── t4_ptext_pipeline_position.py   # B transmission rates
    ├── t5_constraint_audit.py          # Constraint reframing
    ├── t6_line_structure.py            # Line organization
    ├── t7_transition_patterns.py       # Transition analysis
    ├── t8_paragraph_structure.py       # Paragraph patterns
    ├── t9_token_morphology.py          # Morphological profile
    ├── t10_vocabulary_overlap.py       # Cross-folio vocabulary
    ├── t11-t15_rosettes_*.py           # Rosettes exploration
    ├── t16-t19_*.py                    # Label classification
    ├── t20_rosettes_folio_references.py
    ├── t21-t24_trotula_*.py            # Trotula comparison
    ├── t25-t26_rosettes_*.py           # Brunschwig/differentiation
    ├── t27_f65v_investigation.py       # f65v deep dive
    ├── t28_ptext_only_folios.py        # P-text only census
    └── t29_f65v_f66_context.py         # f65v/f66v context
```
