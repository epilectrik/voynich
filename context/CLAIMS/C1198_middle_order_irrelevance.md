# C1198: MIDDLE Order Irrelevance

**Tier:** 2
**Scope:** B
**Phase:** ATOM_EXTENSIBILITY (Phase 425)
**Depends on:** C1190 (MIDDLE behavioral atomicity), C1192-C1194 (position-specific profiles)

## Constraint

MIDDLEs with identical character composition but different ordering show near-identical behavioral profiles. Order does not significantly alter distributional behavior.

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

Character composition determines MIDDLE behavior; the ordering of atoms within a MIDDLE is secondary. This supports a compositional reading where MIDDLEs encode **what atoms participate** rather than **in what sequence they execute**.

Note: order may still carry information below the resolution of behavioral profiles (e.g., procedural sequence visible only to the human operator, not detectable from distributional statistics). The constraint is that order does not affect *distributional behavior* in the text.

## Relationship to C483

C483 established that TOKEN-level repetition (same token appearing multiple times on a line) is ordinal. This constraint addresses a different phenomenon: CHARACTER-level ordering within a single MIDDLE. Both converge on the same principle — the manuscript encodes composition, not sequence.

## Falsification

Would be falsified if a reordered pair is shown to have significantly different behavioral profiles (r < 0.8) using the same methodology on a sufficiently large sample (>50 tokens each).

## Provenance

- `phases/ATOM_EXTENSIBILITY/scripts/atom_extensibility_test.py` (T3)
- `phases/ATOM_EXTENSIBILITY/results/atom_extensibility_results.json`
