# C724: Within-Class Suffix Accessibility Gradient

**Status:** VALIDATED | **Tier:** 2 | **Phase:** B_LEGALITY_GRADIENT | **Scope:** A-B

## Finding

Tokens within the same B instruction class show up to **19x accessibility variation** driven primarily by SUFFIX composition. Within Class 33 (EN): qokaiin=0.675 vs qokeedy=0.035. Same class, same PREFIX (qo), same role (EN) — the SUFFIX alone determines cross-system accessibility.

This is the first **within-class empirical demonstration** of C502.a's three-axis filtering at individual token resolution. The -aiin suffix is A-B balanced (C283), making tokens broadly accessible. The -eedy/-edy suffixes are heavily B-enriched (C283: -edy at 191x B-enriched), locking tokens to B.

Additional examples:
- or (FQ): 0.974 vs aiin (FQ): 0.746 — same role, different suffix
- ar (FL): 0.482 vs al (FL): 0.447 — similar within FL
- lkeedy (AX): 0.018 vs lkedy (AX): 0.009 — lk-prefix tokens nearly B-exclusive regardless of suffix

## Implication

SUFFIX is not a minor filtering dimension — it can override MIDDLE-level accessibility entirely. Two tokens sharing the same MIDDLE and PREFIX can have radically different cross-system reach based solely on their SUFFIX. This confirms C502.a's claim that PREFIX, MIDDLE, and SUFFIX filter independently (C509.d) and quantifies the magnitude of suffix-driven variation.

## Key Numbers

| Token | Class | Role | Accessibility | Suffix |
|-------|-------|------|--------------|--------|
| qokaiin | 33 | EN | 0.675 | -aiin |
| qokeedy | 33 | EN | 0.035 | -eedy |
| qokedy | 33 | EN | 0.088 | -edy |
| daiin | 10 | CC | 0.018 | -aiin |
| ol | 11 | CC | 0.982 | -ol |

## Provenance

- Script: `phases/B_LEGALITY_GRADIENT/scripts/legality_gradient.py` (special token analysis)
- Confirms: C502.a (three-axis morphological filtering), C509.d (independent dimensions)
- Extends: C283 (suffix A/B enrichment ratios)
