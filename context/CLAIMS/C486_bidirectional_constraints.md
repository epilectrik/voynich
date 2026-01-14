# C486: Bidirectional Constraint Coherence

**Tier:** 3 | **Status:** CLOSED | **Scope:** CROSS_SYSTEM

## Statement

The A->AZC->B pipeline exhibits bidirectional constraint coherence: while information flows unidirectionally (A defines vocabulary, AZC gates legality, B executes), constraint compatibility flows bidirectionally. B execution behavior successfully constrains inference about upstream A zone preferences.

## Evidence

### Test 1A: B->A Back-Inference

High-escape B folios preferentially use P-zone (peripheral) MIDDLEs:

| B Behavior | P-zone Usage | Difference | p-value |
|------------|--------------|------------|---------|
| High escape (>15%) | 28.3% | +10.4% | <0.0001 |
| Low escape (<10%) | 17.9% | baseline | - |

### Zone Differentiation by Behavior

| B Metric | Zone Preference | Significance |
|----------|-----------------|--------------|
| High escape density | P-zone (permissive) | p < 0.0001 |
| High hazard density | S-zone (boundary) | p < 0.05 |
| High link density | R-zone (restricting) | p < 0.05 |

### Option Space Narrowing

Given distinctive B behavior, viable upstream zone profiles narrow by **24%** (from 4 zones to ~3 viable).

## Interpretation

This does NOT violate C384 (no entry-level A-B coupling) because:

1. **No token-level mapping** - We cannot say "token X came from zone Y"
2. **Statistical constraint only** - High-escape programs *tend to* draw from P-zone MIDDLEs
3. **Consistency, not reference** - The constraint is about compatibility, not identity

The insight is:

> **The pipeline is bidirectionally constrained, even though information flow is unidirectional.**

This is a hallmark of coherent control system design. The layers are not independent - they are mutually constraining.

### What This Means

| Direction | What Flows | Type |
|-----------|-----------|------|
| A -> B | Vocabulary, discrimination | Reference |
| AZC -> B | Legality, escape permission | Gating |
| **B -> A** | **Behavior constrains zone inference** | **Consistency** |

You cannot freely choose A-layer zones and then independently design B behavior. The layers must be compatible.

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
