# C1342: PREFIX Modulates Suffix Choice for Flexible MIDDLEs

**Tier:** 2
**Scope:** B
**Phase:** SUFFIX_MODE_CONTEXT (470)

## Constraint

For the 28 flexible MIDDLEs (selectivity <0.80), PREFIX is the strongest contextual determinant of suffix category. Conditional MI I(suffix_cat; PREFIX | MIDDLE) = 0.097 bits (2.82x null mean 0.034, perm p=0.001). Cramer's V = 0.23. PREFIX groups impose dramatically different suffix profiles on the same MIDDLE pool: da→93.1% bare, ok_group→51.9% terminal, qo→40.7% terminal + 40.4% iterate, BARE→41.4% bare + 40.2% iterate, ch→33.6% terminal + 32.8% bare.

## Evidence

From suffix_mode_context.py test T1 (5,611 flexible MIDDLE tokens, 28 MIDDLEs):

**PREFIX group suffix profiles:**

| PREFIX | n | terminal | connector | iterate | bare |
|--------|---|----------|-----------|---------|------|
| da | 160 | 1.3% | 0.6% | 5.0% | **93.1%** |
| BARE | 396 | 14.9% | 3.5% | 40.2% | **41.4%** |
| OTHER | 821 | 31.7% | 2.9% | 14.9% | 50.6% |
| ch | 991 | 33.6% | 4.3% | 29.3% | 32.8% |
| sh | 484 | 42.1% | 1.7% | 23.8% | 33.1% |
| qo | 2,019 | **40.7%** | 1.2% | **40.4%** | 17.7% |
| ok_group | 740 | **51.9%** | 3.4% | 20.7% | 24.1% |

**Key statistics:**

| Metric | Value |
|--------|-------|
| Chi2 | 886.8 |
| Cramer's V | 0.230 |
| Conditional MI | 0.097 bits |
| Null mean MI (1000 perms) | 0.034 bits |
| Perm p | 0.001 |
| MI ratio (observed/null) | 2.82x |

## Interpretation

PREFIX is the primary contextual channel for suffix modulation. The mechanism is clear: PREFIX determines which operational category context the MIDDLE operates in (C1297: V=0.311), and different category contexts require different suffix behaviors. Specifically:

- **da** (STAGING-dominant per C1297) suppresses suffixation almost entirely → bare tokens, Mode B contribution
- **qo** (THERMAL-dominant per C1297) biases toward terminal (specification) and iterate (repetition) → Mode A contribution
- **ok_group** (FLOW/TRANSITION per C1297) biases strongly toward terminal → Mode A contribution
- **BARE** (FLOW/STAGING, THERMAL-depleted per C1302) biases toward bare and iterate → Mode B contribution

This explains the THERMAL paradox from C1339: THERMAL MIDDLEs lean Mode B overall (mode_A_frac=0.406), but when they carry qo PREFIX they lean Mode A (terminal-heavy). The PREFIX determines whether the MIDDLE's thermal content gets suffixed (specification mode) or runs bare (execution mode).

## Provenance

- suffix_mode_context.json: test T1
- Extends: C1297 (PREFIX-category association — now shown to modulate suffix, not just category)
- Extends: C1302 (BARE distinctive profile — confirmed: BARE is THERMAL-depleted AND bare/iterate-biased in suffix)
- Extends: C1341 (mode emergent — PREFIX is the largest component of the ~20% contextual residual)
- Resolves: C1339 (THERMAL mode-B lean paradox — PREFIX controls whether THERMAL content is suffixed)

## Status

CONFIRMED — PREFIX is the dominant contextual suffix modulator (conditional MI 0.097 bits, V=0.23).
