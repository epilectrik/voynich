# C944: Paragraph Kernel Sequence Stereotypy

**Tier:** 2 | **Status:** CLOSED | **Scope:** B | **Source:** MATERIAL_LOCUS_SEARCH

## Statement

Paragraph kernel profile sequences follow section-specific patterns. Observed mean transition entropy (2.58 bits) is significantly lower than the permutation null (2.63 bits, p=0.004). Entropy varies dramatically across sections: section T (1.32 bits) and C (1.49 bits) show highly stereotyped paragraph ordering, while B (2.79 bits) and S (2.79 bits) use the full transition space.

## Evidence

### Section-Specific Transition Entropy

| Section | Entropy (bits) | Transitions | Pattern |
|---------|---------------|-------------|---------|
| T | 1.32 | 45 | Highly stereotyped (almost all BALANCED) |
| C | 1.49 | 22 | Highly stereotyped (BALANCED + occasional HIGH_E) |
| H | 2.50 | 25 | Moderate variety |
| B | 2.79 | 128 | Full range |
| S | 2.79 | 266 | Full range |

### Permutation Test

| Metric | Value |
|--------|-------|
| Observed mean entropy | 2.5814 bits |
| Null mean entropy | 2.6286 bits |
| Entropy permutation p | 0.004 |
| Chi-square permutation p | 0.233 |

### Paragraph Classification

585 paragraphs classified by kernel profile (tertile on k-e differential):
- BALANCED: 307 (52.5%)
- HIGH_E: 199 (34.0%)
- HIGH_K: 79 (13.5%)

### Method

59 folios with 3+ paragraphs, 486 transitions. Kernel proportions computed from MIDDLE content (k-class: contains 'k'; e-class: starts with 'e'). 1,000 permutations shuffling paragraph order within folios.

## Implication

Sections constrain not just which vocabulary is used but how paragraph types are sequenced. Section T runs nearly uniform BALANCED paragraphs (low entropy), while section S deploys all transition types freely (high entropy). This is consistent with sections representing different operational regimes with different procedural templates.

## Related

C827, C855, C909, C941
