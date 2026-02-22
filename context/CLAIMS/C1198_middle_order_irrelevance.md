# C1198: MIDDLE Order — Distributional Equivalence

**Tier:** 2
**Scope:** B
**Phase:** ATOM_EXTENSIBILITY (Phase 425)
**Depends on:** C1190 (MIDDLE behavioral atomicity), C1192-C1194 (position-specific profiles)

## Constraint

MIDDLEs with identical character composition but different ordering show near-identical **distributional** profiles (section, position, prefix/suffix context). Order does not affect where in the text a MIDDLE appears or how it combines with other morphological slots.

21 order-equivalent groups tested (same character counts, different sequence, >=10 tokens each):

| Pair | Correlation | Counts |
|------|------------|--------|
| ke / ek | 0.999 | 421 / 169 |
| kch / ckh | 0.995 | 148 / 127 |
| ck / kc | 0.995 | 197 / 33 |
| eek / kee | 0.997 | 54 / 34 |
| te / et | 0.990 | 87 / 58 |
| ct / tc | 0.979 | 95 / 16 |
| ol / lo | 0.972 | 762 / 33 |
| pch / cph | 0.976 | 79 / 36 |
| tch / cth | 0.998 | 65 / 49 |

Mean within-group (same composition, different order): r=0.967
Mean between-group (different composition): r=0.957
Separation: +0.011, permutation p=0.116 (not significant)

## Interpretation

Character composition determines MIDDLE distributional behavior — where it appears in the text, which sections, which positions, which morphological context.

**Important scope limitation:** This does NOT establish that ke and ek are functionally identical to the operator. Order may encode procedural sequence (e.g., "cool then heat" vs "heat then cool") that is invisible to distributional statistics because both variants occupy the same grammatical slot. The constraint is narrowly scoped: **order does not affect textual distribution**. Whether order encodes operational sequence remains open.

## Relationship to C483

C483 established that TOKEN-level repetition (same token appearing multiple times on a line) is ordinal. This constraint addresses a different phenomenon: CHARACTER-level ordering within a single MIDDLE. Both converge on the same principle — the manuscript's textual grammar is driven by composition, though operational sequence may still be encoded within the MIDDLE for the human reader.

## Falsification

Would be falsified if a reordered pair is shown to have significantly different behavioral profiles (r < 0.8) using the same methodology on a sufficiently large sample (>50 tokens each).

## Provenance

- `phases/ATOM_EXTENSIBILITY/scripts/atom_extensibility_test.py` (T3)
- `phases/ATOM_EXTENSIBILITY/results/atom_extensibility_results.json`
