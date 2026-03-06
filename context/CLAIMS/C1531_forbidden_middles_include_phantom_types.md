# C1531: Forbidden MIDDLEs Include Phantom Types Absent from Corpus

**Tier:** 2
**Scope:** B, MIDDLE, hazard, forbidden, phantom, construction, grammar, C109, C1178, C1394, C1528, C1529
**Phase:** HAZARD_CLASS_ATOMIZATION (Phase 543)
**Date:** 2026-03-06

## Claim

Five MIDDLEs participating in the 17 forbidden transitions have ZERO occurrences in the Currier B corpus: shey, chey, chedy, shedy, chol. These are not "disfavored" — they are ABSENT. Their constituent atoms appear freely in other combinations, but these specific constructions never occur. 11 of the 17 forbidden transitions involve at least one phantom MIDDLE. The forbidden transition list partially encodes CONSTRUCTION-LEVEL prohibitions (preventing certain atom combinations from being built), not just SEQUENCE-LEVEL prohibitions (preventing adjacent placement of existing tokens).

## Evidence

### Phantom MIDDLE census

| Phantom MIDDLE | Hazard Class | Role | Decomposition | Occurrences |
|---|---|---|---|---|
| shey | PHASE_ORDERING | Source | sh(PREFIX) + e(HEAD) + y(TERM) | 0 |
| chey | PHASE_ORDERING | Source | ch(PREFIX) + e(HEAD) + y(TERM) | 0 |
| chedy | COMPOSITION_JUMP | Source | ch(PREFIX) + e(HEAD) + d(MOD) + y(TERM) | 0 |
| shedy | COMPOSITION_JUMP | Source | sh(PREFIX) + e(HEAD) + d(MOD) + y(TERM) | 0 |
| chol | CONTAINMENT_TIMING | Source/Target | ch(PREFIX) + o(HEAD) + l(TERM) | 0 |

### Impact on forbidden transition census

- 17 total forbidden transitions (C109)
- 11 transitions involve at least one phantom MIDDLE (64.7%)
- 6 transitions involve only corpus-present MIDDLEs
- All 11 corpus violations come from non-phantom transitions

### Relationship to C1178

C1178 identified ch/sh-initial phantom MIDDLEs as a "dead naming pattern" in the dark pipeline context. The hazard phantoms are a distinct but parallel phenomenon: 4/5 hazard phantoms are also ch/sh-initial (shey, chey, chedy, shedy), while chol is ch-initial with o-HEAD. The forbidden list may partially preserve a construction grammar from an earlier stage of the system.

## Interpretation

The forbidden transition list serves a dual function: (1) preventing dangerous sequences of existing tokens (6 transitions with corpus-present MIDDLEs), and (2) recording construction-level prohibitions that prevent certain atom combinations from ever being assembled (11 transitions involving phantom MIDDLEs). The second function may be vestigial — these constructions are already prevented by the construction grammar itself — or it may serve as a redundant safety layer documenting WHY certain combinations are forbidden even though they never appear.

## Falsification Criteria

1. If any of the 5 phantom MIDDLEs are found in an expanded corpus or alternative transcription
2. If the phantom count drops below 3/5 with revised morphological analysis
3. If phantom-containing forbidden transitions are shown to be transcription errors

## Source

`phases/HAZARD_CLASS_ATOMIZATION/results/hazard_class_atomization.json`
