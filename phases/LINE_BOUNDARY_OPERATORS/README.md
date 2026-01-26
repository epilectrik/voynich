# LINE_BOUNDARY_OPERATORS Phase

**Status:** ACTIVE
**Started:** 2026-01-25
**Predecessor:** ACTION_SEQUENCE_TEST

---

## Hypothesis

L-compound operators (line-initial) and LATE prefixes (line-final) form **symmetric boundary markers** that bracket B control cycles.

---

## Background

From ACTION_SEQUENCE_TEST:
- LATE prefixes (al, ar, or) cluster at line-end (3.78x enrichment)
- LATE prefixes are B-internal grammar applied to PP vocabulary
- Lines show phase structure: EARLY → MIDDLE → LATE

From existing constraints:
- C298: L-compound MIDDLEs (lk, lch, etc.) are B-specific operators
- C501: L-compounds are line-initial control operators (49 types, 111 tokens)
- C539: LATE prefixes are line-final markers

---

## Questions

1. **Symmetry**: Do L-compounds show the same B-exclusive + PP-MIDDLE pattern as LATE prefixes?

2. **Positional**: What is the mean line position of L-compound tokens? (Expect < 0.3)

3. **Co-occurrence**: Do L-compounds and LATE prefixes co-occur in the same lines? Or are they alternatives?

4. **Bracketing**: Does the pattern [L-compound ... LATE] define a complete control cycle?

5. **Function**: If symmetric, what does each boundary mark?
   - L-compound = cycle initialization?
   - LATE = cycle completion/output?

---

## Test Plan

1. **L-compound position analysis**
   - Extract all L-compound tokens
   - Compute mean line position
   - Compare to LATE prefix position (0.70)

2. **L-compound provenance check**
   - Token-level: B-exclusive rate
   - MIDDLE-level: PP vs B-exclusive
   - Compare to LATE pattern (85% B-exclusive tokens, 76% PP MIDDLEs)

3. **Co-occurrence analysis**
   - Count lines with both L-compound AND LATE tokens
   - Test if co-occurrence is above/below random expectation

4. **Bracket structure test**
   - In lines with both, is L-compound before LATE?
   - What's between them? (Should be MIDDLE-phase tokens)

---

## Success Criteria

**CONFIRMED** if:
- L-compounds show line-initial clustering (position < 0.3)
- L-compounds show same provenance pattern (B-exclusive tokens, PP MIDDLEs)
- L-compound and LATE co-occur above chance
- [L-compound ... LATE] pattern is consistent

**REJECTED** if:
- L-compounds are not positionally constrained
- L-compounds and LATE are mutually exclusive
- No systematic bracketing pattern

---

## Scripts

- `l_compound_position.py` - Position analysis
- `l_compound_provenance.py` - B-exclusive vs PP check
- `boundary_cooccurrence.py` - Co-occurrence analysis
- `bracket_structure.py` - Full bracket pattern test

---

## Dependencies

- C298 (L-compound MIDDLEs)
- C501 (B-exclusive MIDDLE stratification)
- C539 (LATE prefix class)
