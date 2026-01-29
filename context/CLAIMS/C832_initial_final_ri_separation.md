# C832: Initial/Final RI Vocabulary Separation

**Tier:** 2
**Scope:** A
**Phase:** A_RECORD_B_ROUTING_TOPOLOGY

## Constraint

INITIAL RI (position < 0.2 in paragraph) and FINAL RI (position > 0.8) use essentially disjoint vocabularies with Jaccard similarity of only 0.010. Only 4 words appear in both positions.

## Evidence

From t14_ri_initial_vs_final.py:

```
Unique words:
  INITIAL: 195
  FINAL: 220

Overlap:
  INITIAL & FINAL: 4 (1.8% of smaller set)

Jaccard similarity: 0.010
```

Morphological differentiation:

| Feature | INITIAL RI | FINAL RI | Bias |
|---------|-----------|----------|------|
| PREFIX po- | 8x | 1x | INITIAL |
| PREFIX do- | 4x | 1x | INITIAL |
| PREFIX ch- | 1x | 2.5x | FINAL |
| PREFIX ct- | 1x | 2.5x | FINAL |
| SUFFIX -or | 13x | 1x | INITIAL |
| SUFFIX -ry | 1x | 10x | FINAL |

## Interpretation

INITIAL and FINAL RI serve different structural functions:

- **INITIAL RI** - "Input" markers with po-, do- prefixes; specifies what context/source the record addresses
- **FINAL RI** - "Output" markers with ch-, ct- prefixes; specifies what result/target the record produces

The near-zero overlap (Jaccard=0.010) indicates these are not positional variants of the same tokens but genuinely different vocabularies.

## Provenance

- t14_ri_initial_vs_final.json: jaccard=0.010, overlap_count=4
- Related: C831 (three-tier structure), C835 (linkers are the 4 overlap tokens)

## Status

CONFIRMED - Vocabulary separation is empirically verified.
