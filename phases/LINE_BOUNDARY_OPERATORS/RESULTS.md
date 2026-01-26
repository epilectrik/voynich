# LINE_BOUNDARY_OPERATORS Results

**Phase:** LINE_BOUNDARY_OPERATORS
**Date:** 2026-01-25
**Status:** CLOSED

---

## Hypothesis

L-compound operators (line-initial) and LATE prefixes (line-final) form **symmetric boundary markers** that bracket B control cycles.

---

## Findings

### Primary Result: SYMMETRIC BRACKETING FALSIFIED

L-compound and LATE prefixes are **NOT symmetric brackets**:

| Test | Result | Interpretation |
|------|--------|----------------|
| Co-occurrence ratio | 0.95x | Independent (not enriched) |
| Bracket order [L...LATE] | 67.4% | Inconsistent |
| MIDDLE overlap | 1.4% (2/144) | Different vocabulary pools |

**Conclusion:** These are parallel grammatical systems, not sequential brackets.

---

### Secondary Result: L-compound Compositional Structure (C298.a)

L-compound = `l` + energy operator root:

| Pattern | Count | Root |
|---------|-------|------|
| lch | 74 | ch (ENERGY) |
| lk | 58 | k (kernel) |
| lsh | 24 | sh (ENERGY) |

**75.9%** of L-compound MIDDLEs contain energy operator roots (ch/sh/k).

---

### Tertiary Result: `l` Positional Modifier

The `l` modifier shifts energy operations **earlier** in line:

| MIDDLE | Mean Position | Difference |
|--------|---------------|------------|
| ch | 0.483 | baseline |
| lch | 0.344 | **-0.139** |

The `l` is a grammatical modifier, not semantic content.

---

### Quaternary Result: Provenance Contrast

| Class | B-Exclusive Tokens | B-Exclusive MIDDLEs | Interpretation |
|-------|-------------------|---------------------|----------------|
| L-compound | 97.0% | 85.9% | Fully B-internal infrastructure |
| LATE (C539) | 85.4% | 23.8% (76.2% PP) | B-prefix on pipeline vocabulary |

L-compound uses B's own vocabulary; LATE marks PP content at boundaries.

---

### Quinary Result: Folio Type Differentiation (Tier 3)

L-compound rate and LATE rate are **negatively correlated** (r = -0.305):

| Folio Type | Example | L-compound | LATE |
|------------|---------|------------|------|
| Control-heavy | f83v | 4.94% | 0.00% |
| Output-heavy | f40r | 0.00% | 6.19% |

**REGIME mapping:**
- REGIME_1/3: Higher L-compound, higher ENERGY, lower LATE
- REGIME_2/4: Lower L-compound, lower ENERGY, higher LATE

---

### Negative Result: LINK Connection

Tested whether L-compound appears after LINK tokens:

| Test | Result |
|------|--------|
| L-compound after potential LINK | 0.65x (depleted) |
| Position ordering | Mixed (56%/44%) |

**LINK connection not confirmed.** Hypothesis that `l` = LINK marker is interesting but unproven.

---

## Constraints Produced/Extended

| Constraint | Tier | Action |
|------------|------|--------|
| C298.a | 2 | Extended C298 with compositional structure and positional shift |

---

## Tier 3 Characterizations Added

- L-compound as modified energy operators
- Folio program type differentiation (L-compound vs LATE)
- REGIME correlation with grammar type

---

## Falsified Hypotheses

1. **Symmetric bracketing** - L-compound and LATE do not form line brackets
2. **LINK connection** - L-compound is not systematically related to LINK

---

## Scripts

- `l_compound_analysis.py` - Initial L-compound characterization
- `boundary_deep_dive.py` - MIDDLE comparison and three-part structure test
- `folio_type_analysis.py` - Folio differentiation and REGIME correlation
- `link_connection_test.py` - LINK hypothesis testing

---

## Key Insight

L-compound and LATE represent **different grammatical strategies**:

```
L-COMPOUND (Control Infrastructure)
- B's own vocabulary (86% exclusive MIDDLEs)
- Modified energy operators (l + ch/k/sh)
- Earlier line position (0.34)
- Used in control-intensive folios

LATE PREFIX (Output Marking)
- B-prefix on PP vocabulary (76% PP MIDDLEs)
- V+L morphology (al/ar/or)
- Later line position (0.70)
- Used in output-intensive folios
```

These are parallel systems that characterize different **program types**, not sequential phases within lines.
