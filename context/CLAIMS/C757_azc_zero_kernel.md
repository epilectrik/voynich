# C757: AZC Zero Kernel/Link

**Status:** VALIDATED | **Tier:** 2 | **Phase:** AZC_FOLIO_DIFFERENTIATION | **Scope:** AZC

## Finding

AZC diagram text contains zero KERNEL tokens and zero LINK tokens. The AZC vocabulary is entirely outside the kernel control layer.

### Evidence

| Role | AZC Tokens | Percentage |
|------|------------|------------|
| KERNEL (k, h, e) | 0 | 0.0% |
| LINK | 0 | 0.0% |
| OPERATIONAL | 1,426 | 50.4% |
| UN (unclassified) | 1,404 | 49.6% |

Total AZC diagram tokens: 2,830 (P-text excluded)

### Family Comparison

| Family | Folios | Tokens | OPERATIONAL | UN |
|--------|--------|--------|-------------|-----|
| Zodiac | 13 | 1,465 | 50.6% | 49.4% |
| A/C | 15 | 1,365 | 50.2% | 49.8% |

Both families show identical role composition (chi-squared p=0.86).

## Implication

AZC is structurally distinct from Currier B:
- B contains KERNEL and LINK as execution infrastructure
- AZC lacks this infrastructure entirely
- AZC cannot execute B-style control programs

This confirms AZC's role as "context-locking scaffold" rather than "execution layer."

## Provenance

- Phase: AZC_FOLIO_DIFFERENTIATION
- Script: t1_azc_role_coverage.py
- Related: C121 (49 classes), C332 (KERNEL structure)
