# C1554: Phantom MIDDLEs Are Atom-Legal but Construction-Dead

**Tier:** 2
**Scope:** B, MIDDLE, phantom, atom, slot, construction, defense-in-depth, hazard, forbidden, C1552, C1553, C1178, C1209, C1210, C1546
**Phase:** PHANTOM_MIDDLE_MECHANISM (Phase 547)
**Date:** 2026-03-06

## Claim

All 5 hazard phantom MIDDLEs (chey, shey, chedy, shedy, chol) pass atom-level slot legality: every atom in every phantom occupies a slot (INITIAL/MEDIAL/TERMINAL) that is attested in the corpus. They also pass PREFIX compatibility (22-27 compatible PREFIXes each) and suffix compatibility (all terminal atoms have established opacity classes). Yet they have exactly 0 corpus tokens. The prohibition operates at the BIGRAM level (ch/sh at MIDDLE-initial, C1553), not at the atom or selectional level. This confirms defense-in-depth architecture: the forbidden transition topology (C109) covers MIDDLEs that the vocabulary system (C1553) already makes impossible, providing a second safety layer against their potential revival.

## Evidence

### Atom slot legality (all 5 phantoms)

| Phantom | Slot assignments | All slots attested? |
|---|---|---|
| shey | s(MOD) h(DUAL) e(HEAD) y(TERM) | Yes -- all 4 atoms appear in these slots in corpus |
| chey | c(MOD) h(DUAL) e(HEAD) y(TERM) | Yes |
| chedy | c(MOD) h(DUAL) e(HEAD) d(MOD) y(TERM) | Yes |
| shedy | s(MOD) h(DUAL) e(HEAD) d(MOD) y(TERM) | Yes |
| chol | c(MOD) h(DUAL) o(HEAD) l(TERM) | Yes |

Per C1209 and C1210, atoms have strong positional preferences (e.g., c=MEDIAL, h=TERMINAL, e=INITIAL, y=TERMINAL). Every phantom respects these slot assignments.

### Mechanism rejection cascade

| Hypothesis | Test | Result | Verdict |
|---|---|---|---|
| A: Atom slots illegal | Slot legality check | All 5 pass all slots | REJECTED |
| B: No compatible PREFIX | PREFIX compatibility | 22-27 PREFIXes each | REJECTED |
| B: Suffix impossible | Terminal opacity | y=OPAQUE, l=SEMI_TRANSPARENT | REJECTED |
| C: Hazard pruning | Forbidden pair check | All 5 are hazard sources (2-3 pairs each) | CONTRIBUTING |
| D: ch/sh bigram partition | Compound census | 0 ch/sh-initial 3+ char MIDDLEs | CONFIRMED PRIMARY |

### Defense-in-depth confirmation

The forbidden transition topology (17 pairs, C109) includes 7 pairs involving phantom source MIDDLEs. These transitions cannot occur because the source MIDDLEs do not exist. The safety system operates at two independent levels:

1. **Vocabulary level (C1553):** ch/sh-initial compound MIDDLEs are never instantiated
2. **Transition level (C109):** Even if instantiated, forbidden transitions would prevent dangerous sequences

Neither level requires the other, but both are present. This is the hallmark of defense-in-depth engineering.

## Interpretation

The grammar's forbidden transition topology was designed at a level of generality that exceeds the actual vocabulary. This is consistent with the grammar being defined first (or at a higher level of abstraction) and the vocabulary being curated within it. The phantom MIDDLEs represent structurally conceivable but lexically excluded constructions that the safety system nonetheless guards against. This pattern is characteristic of robust engineered systems that protect against not only current failure modes but also potential ones.

## Falsification Criteria

1. If any phantom MIDDLE is shown to violate an atom-level construction rule not tested here
2. If the defense-in-depth pattern is shown to be accidental (e.g., the forbidden pairs involving phantoms serve a different structural purpose)
3. If phantom MIDDLEs are discovered in uncounted corpus sections, falsifying their absence

## Source

`phases/PHANTOM_MIDDLE_MECHANISM/results/phantom_middle_mechanism.json`
