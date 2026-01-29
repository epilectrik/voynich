# C765 - AZC Kernel Access Bottleneck

**Tier:** 2 | **Status:** CLOSED | **Scope:** GLOBAL

## Statement

AZC constrains Currier B execution by limiting kernel access, not by limiting escape directly. AZC-mediated vocabulary is escape-prone (31.3%) but kernel-shallow (51.3% kernel contact), while B-native vocabulary is escape-resistant (21.5%) but kernel-deep (77.8% kernel contact). Folios with high AZC-mediation lack kernel depth, resulting in simpler execution with less escape needed.

## Evidence

### T1: Vocabulary Mediation (n=82 B folios)

- Mean 75.5% of B vocabulary is AZC-mediated
- Range: 54.5% to 94.9%
- Strong negative correlation with vocab size: r = -0.800 (p < 0.001)
- Larger B vocabularies have proportionally less AZC mediation

### T2: Folio-Level Behavior

AZC-mediated % correlates with B behavioral properties:

| Metric | Correlation with AZC % | p-value |
|--------|------------------------|---------|
| Escape rate | r = -0.311 | 0.0044 |
| Kernel contact rate | r = -0.420 | 0.0001 |
| Total tokens | r = -0.661 | < 0.0001 |

Higher AZC-mediation → lower escape and lower kernel contact at folio level.

BUT: Effect is mediated by vocabulary size (partial r = -0.159, p = 0.155).

### T3: Token-Level Analysis (n=23,096 tokens)

| Vocabulary Source | Escape Rate | Kernel Contact |
|-------------------|-------------|----------------|
| AZC-mediated (n=21,107) | 31.3% | 51.3% |
| B-native (n=1,989) | 21.5% | 77.8% |

Chi-squared tests:
- Escape difference: chi2 = 66.2, p = 3.98e-16
- Kernel difference: chi2 = 512.0, p = 2.34e-113

**AZC vocabulary has HIGHER escape but LOWER kernel contact.**

### T4: Resolution of Paradox

The folio-level finding (high AZC % → low escape) and token-level finding (AZC tokens escape MORE) are reconciled by:

1. High AZC % → fewer B-native tokens (r = -0.518, p < 0.0001)
2. B-native tokens have high kernel contact (77.8%)
3. Fewer B-native tokens → less kernel access
4. Less kernel access → simpler execution paths
5. Simpler execution → less need for escape recovery

## The Mechanism

```
A → AZC → B Pipeline

AZC provides:
  - Escape-prone vocabulary (31.3% escape rate)
  - Kernel-shallow vocabulary (51.3% kernel contact)

B-native adds:
  - Escape-resistant vocabulary (21.5% escape rate)
  - Kernel-deep vocabulary (77.8% kernel contact)

High AZC-mediation means:
  → Vocabulary is mostly AZC-sourced
  → Little B-native contribution
  → Little kernel depth
  → Simple execution paths
  → Less escape needed

Low AZC-mediation means:
  → More B-native vocabulary
  → More kernel depth
  → Complex execution paths
  → More escape needed
```

## Functional Interpretation

AZC acts as a **vocabulary bottleneck** that controls execution complexity:

1. **Not about filtering escape** - AZC vocabulary actually enables MORE escape per token
2. **About limiting kernel access** - AZC vocabulary has less kernel contact
3. **Controls complexity** - Kernel depth determines execution complexity
4. **Indirect escape control** - Simple execution needs less escape recovery

This explains why AZC has zero KERNEL/LINK tokens (C757) - AZC provides vocabulary that interacts with the kernel from the OUTSIDE, not vocabulary that participates in kernel execution directly.

## Cross-References

- C757 (AZC Zero Kernel/Link)
- C089 (Kernel is core within core)
- C366 (LINK marks grammar state transitions)
- C458 (Kernel operator frequency clamped)

## Source

AZC_B_CONSTRAINT_MECHANISM phase (T1-T4)
