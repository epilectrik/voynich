# C1143: Dark-Exclusive and Shared Atoms Have Equivalent Section Profiles

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / morphological construction
**Phase:** 409 (DARK_PIPELINE_INTERNAL_ARCHITECTURE)

## Finding

The 25 dark-exclusive atoms and 25 shared atoms (identified in Phase 408) show **no significant difference** in section concentration, despite dark-exclusive atoms being rarer and less widespread.

### Atom Profile Comparison

| Metric | Dark-Exclusive (25) | Shared (25) |
|--------|-------------------|-------------|
| Mean char length | 2.80 | 2.24 |
| Mean B token freq | 15.2 | 41.5 |
| Mean folio spread | 11.4 | 22.1 |
| Mean section Herfindahl | 0.628 | 0.461 |

### Mann-Whitney U Test (Herfindahl)

| Statistic | Value |
|-----------|-------|
| U | 395.5 |
| z | 1.610 |
| p (two-sided) | 0.107 |
| n (dark-exc / shared) | 25 / 25 |

The 0.167 Herfindahl gap is directionally consistent with dark-exclusive atoms being more concentrated, but fails to reach significance. Much of the gap is driven by 8 singleton atoms (freq=1) that trivially have Herfindahl=1.0.

## Evidence

- Phase 409, Test 1: Mann-Whitney U on section Herfindahl, all 50 atoms observed in B dark-pipeline compounds
- Dark-exclusive atoms: aiin, ain, al, am, ar, ckh, cph, cth, ech, eck, ect, eek, eey, eod, eok, et, kch, keeo, lch, lk, lo, ly, olk, opch, or
- Shared atoms: ai, aii, ck, ct, dy, ed, ee, eeo, ek, eo, eol, ey, in, ka, kc, ke, kee, od, ok, ol, op, ot, pch, tch, te

## Implication

The dark-exclusive atom pool is not a structurally distinct subclass. Dark-exclusive atoms are simply rarer (2.7x lower frequency, 1.9x fewer folios) and longer (2.80 vs 2.24 chars), but they distribute across sections the same way shared atoms do. This reinforces C1142's finding that section concentration is not atom-driven — the atoms are interchangeable building blocks; section specificity arises from compound composition and frequency modulation.

## Provenance

- Source: Phase 409, Test 1
- Related: C1142 (section concentration not atom-driven, p=0.303), C1141 (bridge atom substrate), C1134 (frequency modulation)
