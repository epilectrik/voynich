# C767: Class Compound Bimodality

## Constraint

The 49-class grammar exhibits bimodal compound usage: 21 classes use exclusively base MIDDLEs (0-5% compound), while 3 classes use exclusively compound MIDDLEs (85%+).

## Quantitative Evidence

| Category | Classes | Tokens | % of Grammar |
|----------|---------|--------|--------------|
| BASE-ONLY (0-5%) | 21 | 7,470 | 46.5% |
| LOW (5-30%) | 12 | 2,420 | 15.1% |
| MEDIUM (30-60%) | 5 | 2,119 | 13.2% |
| HIGH (60-85%) | 7 | 2,682 | 16.7% |
| COMPOUND-HEAVY (85%+) | 3 | 1,363 | 8.5% |

## Base-Only Classes (21)

Classes: 6, 7, 11, 14, 15, 18, 20, 21, 22, 23, 25, 30, 31, 32, 33, 35, 36, 37, 38, 40, 41

- Use 49 unique MIDDLEs total
- 73.5% of those MIDDLEs ARE core MIDDLEs themselves
- MIDDLEs: `m, l, y, i, d, h, g, o, n, r, s, e, k, t, lo, ok, ee, ot, om, tc...`

## Compound-Heavy Classes (3)

| Class | Compound% | Tokens | MIDDLEs |
|-------|-----------|--------|---------|
| 8 | 90.2% | 1,006 | `edy, ol` |
| 10 | 100% | 314 | `iin` only |
| 44 | 100% | 43 | `keeo, kec, teo, pch, kch` |

## Single-Function Classes

- **Class 10**: Uses ONLY 'iin' (100% compound, single MIDDLE)
- **Class 11**: Uses ONLY 'ol' (0% compound, single MIDDLE)

These are operators with exactly one MIDDLE type - maximally specialized.

## Implications

1. **Grammar has two functional vocabularies** within the classified 49 classes
2. **Base classes** operate with atomic primitives (direct execution)
3. **Compound classes** operate with derived forms (complex execution)
4. **The split is not random** - specific classes are locked to specific vocabulary types

## Tier

**Tier 2** - Empirically validated structural relationship

## Source

- Phase: COMPOUND_MIDDLE_ARCHITECTURE
- Test: T6 (t6_class_compound_profile.py)
- Data: 49 classes, 16,054 classified tokens
