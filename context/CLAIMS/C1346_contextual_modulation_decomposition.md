# C1346: Contextual Suffix Modulation Is PREFIX-Dominated

**Tier:** 2
**Scope:** B
**Phase:** SUFFIX_MODE_CONTEXT (470)

## Constraint

The ~20% contextual residual in suffix mode prediction (C1341) decomposes into four factors ranked by conditional MI: PREFIX (0.097 bits), line category environment (0.057 bits), within-line position (0.024 bits), and paragraph opener mode (0.016 bits). PREFIX dominates, carrying 50% of the total conditional information. The factors are largely non-redundant: MI(PREFIX; opener_mode) = 0.003 bits, MI(PREFIX; thermal_bin) = 0.006 bits. However, variance decomposition shows combined factors explain only 5.2% of binary deviation variance, indicating the modulation is probabilistic rather than deterministic.

## Evidence

From suffix_mode_context.py test T5 (5,611 flexible MIDDLE tokens, 28 MIDDLEs):

**Conditional MI hierarchy:**

| Factor | Conditional MI (bits) | Share |
|--------|-----------------------|-------|
| PREFIX (C1342) | 0.097 | 49.8% |
| Category environment (C1343) | 0.057 | 29.3% |
| Position (C1344) | 0.024 | 12.4% |
| Opener mode (C1345) | 0.016 | 8.2% |

Note: MI values are not strictly additive due to partial overlap; shares are approximate.

**Redundancy check:**

| Pair | MI (bits) | Interpretation |
|------|-----------|----------------|
| PREFIX ↔ opener_mode | 0.003 | Near-independent |
| PREFIX ↔ thermal_bin | 0.006 | Near-independent |

**Variance decomposition (binary deviation):**

| Factor | Variance explained |
|--------|--------------------|
| PREFIX | 0.42% |
| Position | 0.02% |
| Opener mode | 0.01% |
| Thermal bin | 0.00% |
| Combined (PREFIX × position × opener) | 5.19% |

The low R-squared reflects the probabilistic nature of suffix modulation: PREFIX shifts the *probability* of suffix deviation from 6.3% (da) to 57.3% (BARE), but cannot deterministically predict any individual token's suffix.

**Overall deviation rate:** 46.1% of flexible MIDDLE tokens deviate from their modal suffix.

## Interpretation

The contextual modulation of suffix mode has a clear hierarchical structure:

1. **PREFIX** is the dominant channel (50% of information). It operates through the category pathway: PREFIX→category→suffix (C1297→C1309→suffix). Different PREFIXes route the same MIDDLE into different operational contexts, each with its own suffix requirement.

2. **Category environment** contributes independently (29%). THERMAL-rich lines push toward terminal suffix regardless of the token's own PREFIX. This represents line-level coherence: if a line is executing thermal-mode operations, even flexible tokens align.

3. **Position** is a genuine but weaker effect (12%). The MID-line terminal peak suggests specification concentrates at mid-line, with continuation signals at boundaries.

4. **Opener mode** is the weakest (8%) and section-heterogeneous. The paragraph-level context that C1256 detected at the line level barely reaches individual token suffix choice.

The factors are largely non-redundant (low pairwise MI), meaning they capture different aspects of context. The total conditional MI (sum ~0.194 bits, partial overlap aside) compared to the raw MI from C1338 (I(MIDDLE; suffix) = 0.697 bits) confirms that MIDDLE identity still dominates, but the contextual factors together provide meaningful additional prediction.

## Provenance

- suffix_mode_context.json: test T5
- Synthesizes: C1342 (PREFIX), C1343 (environment), C1344 (position), C1345 (opener)
- Extends: C1341 (mode emergent property — the ~20% residual is now decomposed)
- Extends: C1338 (MIDDLE suffix selectivity — flexible MIDDLEs' suffix is primarily PREFIX-determined)

## Status

CONFIRMED — contextual suffix modulation is PREFIX-dominated (50% of conditional MI), with category environment (29%), position (12%), and opener mode (8%) contributing. Factors are largely non-redundant.
