# C486: Bidirectional Constraint Coherence

**Tier:** 3 | **Status:** CLOSED | **Scope:** CROSS_SYSTEM

> **REVISION NOTES:**
>
> **P-text (PTEXT_FOLIO_ANALYSIS):** "P-zone" references refer to P-text
> (paragraph text) on AZC folios, which is linguistically Currier A (C758).
> P-text MIDDLEs have 76.7% transmission to B vs 39.9% for general A.
>
> **Escape terminology (2026-01-31):** "High-escape" was measured as qo_density
> in the source test. Per C397/C398 revision, qo is the energy lane (k-rich)
> that operates hazard-DISTANT. Replaced "escape" with "qo-density" throughout.

## Statement

The A->AZC->B pipeline exhibits bidirectional constraint coherence: while information flows unidirectionally (A defines vocabulary, AZC encodes position, B executes), constraint compatibility flows bidirectionally. B execution behavior successfully constrains inference about upstream A vocabulary preferences.

## Evidence

### Test 1A: B->A Back-Inference

High qo-density B folios preferentially use P-text (paragraph) MIDDLEs:

| B Behavior | P-text Usage | Difference | p-value |
|------------|--------------|------------|---------|
| High qo-density (>15%) | 28.3% | +10.4% | <0.0001 |
| Low qo-density (<10%) | 17.9% | baseline | - |

### Zone Differentiation by Behavior

| B Metric | Vocabulary/Zone Preference | Significance |
|----------|---------------------------|--------------|
| High qo-density | P-text vocabulary | p < 0.0001 |
| High hazard density | S-zone (boundary) | p < 0.05 |
| High link density | R-zone (restricting) | p < 0.05 |

### Option Space Narrowing

Given distinctive B behavior, viable upstream zone profiles narrow by **24%** (from 4 zones to ~3 viable).

## Interpretation

This does NOT violate C384 (no entry-level A-B coupling) because:

1. **No token-level mapping** - We cannot say "token X came from zone Y"
2. **Statistical constraint only** - High qo-density programs *tend to* draw from P-text MIDDLEs
3. **Consistency, not reference** - The constraint is about compatibility, not identity

The insight is:

> **The pipeline is bidirectionally constrained, even though information flow is unidirectional.**

This is a hallmark of coherent control system design. The layers are not independent - they are mutually constraining.

### What This Means

| Direction | What Flows | Type |
|-----------|-----------|------|
| A -> B | Vocabulary, discrimination | Reference |
| AZC -> B | Positional encoding, vocabulary character | Encoding |
| **B -> A** | **Behavior constrains zone inference** | **Consistency** |

You cannot freely choose A-layer zones and then independently design B behavior. The layers must be compatible.

### QO-Density Interpretation (2026-01-31)

The correlation between qo-density and P-text vocabulary suggests:
- QO lane (k-rich, energy operations) preferentially uses P-text MIDDLEs
- P-text is a privileged Currier A vocabulary subset with 76.7% B transmission
- High energy-intensity programs draw from this privileged vocabulary pool

## Constraint Relationship

This finding strengthens the overall architecture by showing that:
- Layers are not arbitrarily stacked
- Design choices at one layer propagate constraints to others
- The system is *coherent*, not merely *consistent*

## Related Constraints

- C384: No entry-level A-B coupling (NOT violated)
- C437-C444: AZC folio structure
- C441: Vocabulary-activated constraints

## Source

Phase: SEMANTIC_CEILING_EXTENSION
Test: 1A (b_to_a_inference.py)
Results: `results/b_to_a_inference.json`
