# Baseline Control Profile

*Generated: 2025-12-31T21:22:16.787270*

---

## Overview

This profile is computed from **68 non-outlier folios**.
It establishes what 'normal' control behavior looks like in the Voynich manuscript.

## Sample Folios

- f26r
- f26v
- f31r
- f31v
- f33v

## Signature Statistics

| Metric | Mean | Std Dev |
|--------|------|---------|
| total_length | 927.765 | 510.241 |
| cycle_count | 108.779 | 67.203 |
| cycle_regularity | 3.522 | 0.529 |
| link_density | 0.379 | 0.056 |
| kernel_distance_mean | 1.379 | 0.056 |
| kernel_contact_ratio | 0.621 | 0.056 |
| hazard_density | 0.586 | 0.053 |
| near_miss_count | 23.588 | 15.308 |
| recovery_ops_count | 16.985 | 13.821 |
| phase_ordering_rigidity | 0.163 | 0.035 |

## Typical Patterns

- **Typical trajectory pattern:** stable
- **Pattern distribution:**
  - stable: 68

- **Typical terminal state:** STATE-C
- **Terminal state distribution:**
  - other: 29
  - STATE-C: 37
  - initial: 2

## Canonical Control Profile

A 'normal' Voynich folio exhibits:

1. **Length:** ~928 tokens
2. **Cycle count:** ~109 cycles
3. **Kernel contact ratio:** ~0.62
4. **Hazard density:** ~0.59
5. **Trajectory pattern:** stable
6. **Terminal state:** STATE-C