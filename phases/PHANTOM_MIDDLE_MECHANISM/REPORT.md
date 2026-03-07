# Phase 547: Phantom MIDDLE Mechanism

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1553, C1554, C1555

---

## Research Question

WHY do the 5 phantom hazard source MIDDLEs (shey, chey, chedy, shedy, chol) have exactly zero corpus occurrences? C1552 established THAT they are absent and C1178 labeled them as a "dead naming pattern" -- but what MECHANISM prevents their existence? Four candidate hypotheses were tested:

| Hypothesis | Mechanism | Prediction |
|---|---|---|
| A: CONSTRUCTION_PROHIBITION | Atom slot rules forbid the phantom compositions | At least one atom in each phantom occupies a forbidden slot |
| B: SELECTIONAL_COLLAPSE | No PREFIX or suffix can combine with these MIDDLEs | Zero compatible PREFIXes or suffix attachment is impossible |
| C: SAFETY_PRUNING | Phantoms were deliberately excluded because they would be hazard sources | Phantom hazard involvement is non-accidental |
| D: LEXICAL_CURATION | ch/sh is a PREFIX-domain bigram that categorically does not serve as MIDDLE-initial | 0 ch/sh-initial compound MIDDLEs of length 3+ exist anywhere |

---

## Method

10 analytical tests were conducted using `phases/PHANTOM_MIDDLE_MECHANISM/scripts/phantom_middle_mechanism.py`:

1. **Atom slot legality** -- Do phantom atoms violate C1209/C1210 slot rules?
2. **Component existence** -- Do phantom substrings exist as standalone MIDDLEs?
3. **Near neighbors** -- How close are phantoms to existing MIDDLEs?
4. **Structural patterns** -- What is the ch/sh-initial compound MIDDLE census?
5. **PREFIX compatibility** -- Can any PREFIX combine with phantom MIDDLEs?
6. **Suffix compatibility** -- Are phantom terminals suffix-compatible?
7. **Cross-system presence** -- Do phantoms appear in Currier A or AZC?
8. **Counterfactual hazard** -- What forbidden transitions would phantoms create?
9. **Statistical absence** -- Is the ch/sh MIDDLE gap consistent with frequency expectations?
10. **Synthesis** -- Which mechanism best explains the evidence?

---

## Results

### Test 1: Atom Slot Legality -- ALL LEGAL

Every atom in every phantom occupies a slot that is attested in the corpus:

| Phantom | Atoms | All slots legal? |
|---|---|---|
| shey | s(MOD) h(TERM/DUAL) e(HEAD) y(TERM) | Yes |
| chey | c(MOD) h(TERM/DUAL) e(HEAD) y(TERM) | Yes |
| chedy | c(MOD) h(TERM/DUAL) e(HEAD) d(MOD) y(TERM) | Yes |
| shedy | s(MOD) h(TERM/DUAL) e(HEAD) d(MOD) y(TERM) | Yes |
| chol | c(MOD) h(TERM/DUAL) o(HEAD) l(TERM) | Yes |

**Verdict:** Hypothesis A (CONSTRUCTION_PROHIBITION) **REJECTED**. No atom placement rule prevents these compounds.

### Test 2: Component Existence -- KEY SUBSTRINGS MISSING

No single-atom reduction of any phantom exists as a corpus MIDDLE:

| Phantom | Reductions tested | Any exists? |
|---|---|---|
| shey | hey, sey, shy, she | No |
| chey | hey, cey, chy, che | No |
| chedy | hedy, cedy, chdy, chey, ched | No |
| shedy | hedy, sedy, shdy, shey, shed | No |
| chol | hol, col, chl, cho | hol (3 tokens, A only) |

Key missing 3-character substrings: she, hey, che, hed, hedy, cho. The phantoms lack a construction pathway -- there is no simpler MIDDLE to build from.

### Test 3: Near Neighbors -- EDIT DISTANCE 2 MINIMUM

All phantoms require at least 2 character edits to reach any existing MIDDLE:

| Phantom | Min edit distance | Frame (HEAD->TERM) | Same-frame MIDDLEs |
|---|---|---|---|
| shey | 2 | s->y | 0 |
| chey | 2 | c->y | 2 (cfhy, ckhy) |
| chedy | 2 | c->y | 2 (cfhy, ckhy) |
| shedy | 2 | s->y | 0 |
| chol | 2 | c->l | 0 |

The s->y and c->l frames are completely empty. The phantoms occupy isolated regions of MIDDLE space.

### Test 4: Structural Patterns -- THE KEY FINDING

**ch/sh as MIDDLE-initial bigram in compounds of length 3+: ZERO.**

| Pattern | Types | Tokens |
|---|---|---|
| ch-initial MIDDLEs (all lengths) | 1 ("ch") | 4 |
| sh-initial MIDDLEs (all lengths) | 1 ("sh") | 5 |
| c-initial compound MIDDLEs (3+ chars) | 55 | 291 |
| s-initial compound MIDDLEs (3+ chars) | 12 | 14 |
| **ch-initial compound MIDDLEs (3+ chars)** | **0** | **0** |
| **sh-initial compound MIDDLEs (3+ chars)** | **0** | **0** |

Meanwhile, ch/sh as PREFIX: 3,492 + 2,329 = **5,821 tokens**. The PREFIX:MIDDLE ratio is 5,821:0 -- a categorical positional partition.

c-initial compounds exist abundantly (55 types, 291 tokens), and s-initial compounds exist (12 types, 14 tokens). But the moment the second character is h (forming ch or sh), the compound MIDDLE category becomes empty. This is not a c-atom or s-atom prohibition -- it is specifically the ch and sh BIGRAMS that are excluded from MIDDLE position.

**Additional structural finding:** Of the 55 c-initial compound MIDDLEs, 49 (89.1%) contain h -- but h appears at position 2 or later, never at position 1. The pattern is c+[k/t/f/p]+h (e.g., ckh, cth, cfh, cph), where an intervening atom separates c from h. The ch bigram at positions 0-1 is categorically absent.

### Test 5: PREFIX Compatibility -- NO COLLAPSE

All phantoms are compatible with 22-27 PREFIXes:

| Phantom | Compatible PREFIXes |
|---|---|
| shey | 27 |
| chey | 22 |
| chedy | 22 |
| shedy | 27 |
| chol | 22 |

**Verdict:** Hypothesis B (SELECTIONAL_COLLAPSE) **REJECTED**. No PREFIX bottleneck prevents phantom usage.

### Test 6: Suffix Compatibility -- COMPATIBLE

| Phantom | Terminal | Opacity class | Expected suffix rate |
|---|---|---|---|
| shey | y | OPAQUE | <5% |
| chey | y | OPAQUE | <5% |
| chedy | y | OPAQUE | <5% |
| shedy | y | OPAQUE | <5% |
| chol | l | SEMI_TRANSPARENT | ~9.6% |

All phantoms have terminal atoms observed in the corpus with established suffix behaviors. No suffix incompatibility.

### Test 7: Cross-System Presence -- ABSENT EVERYWHERE

None of the 5 phantoms appear as MIDDLEs in Currier A or AZC. Some appear as substrings in longer compound MIDDLEs (e.g., "chol" appears inside opchol, tchol, ochol in B), but never as standalone MIDDLE types.

### Test 8: Counterfactual Hazard -- ALL WOULD BE DANGEROUS

Each phantom participates in 2-3 forbidden transition pairs:

| Phantom | Forbidden pairs | Hazard class |
|---|---|---|
| chey | 3 (chey->chedy, chey->shedy, shey->chey) | PHASE_ORDERING |
| shey | 2 (shey->chey, shey->shedy) | PHASE_ORDERING |
| chedy | 2 (chey->chedy, shedy->chedy) | PHASE_ORDERING |
| shedy | 3 (chey->shedy, shey->shedy, shedy->chedy) | PHASE_ORDERING |
| chol | 2 (involves CONTAINMENT_TIMING) | CONTAINMENT_TIMING |

All 5 phantoms are PHASE_ORDERING or CONTAINMENT_TIMING hazard sources. If they existed, they would create active forbidden transitions. Hypothesis C (SAFETY_PRUNING) is a **contributing** factor but cannot be primary because it does not explain the mechanism of exclusion.

### Test 9: Statistical Absence -- CONSISTENT WITH LEXICAL CURATION

- ch bigram as MIDDLE-initial: 0.025% of all MIDDLE bigram-initial positions
- sh bigram as MIDDLE-initial: 0.031% of all MIDDLE bigram-initial positions
- c-initial headless compounds with h: 49/62 types (79.0%), but h is NEVER at position 1

The c+h adjacency avoidance in MIDDLE position is categorical and cannot be explained by frequency effects.

### Test 10: Synthesis

| Hypothesis | Verdict | Evidence |
|---|---|---|
| A: CONSTRUCTION_PROHIBITION | **REJECTED** | All atoms legal in all slots (Test 1) |
| B: SELECTIONAL_COLLAPSE | **REJECTED** | 22-27 compatible PREFIXes each (Test 5), suffix-compatible (Test 6) |
| C: SAFETY_PRUNING | **CONTRIBUTING** | All phantoms are hazard sources (Test 8), but does not explain mechanism |
| D: LEXICAL_CURATION | **CONFIRMED PRIMARY** | 0 ch/sh-initial compound MIDDLEs of any length; 5,821:0 PREFIX:MIDDLE ratio (Test 4) |

---

## Mechanism

**Primary:** D_LEXICAL_CURATION -- ch and sh are PREFIX-domain bigrams that categorically do not extend to MIDDLE-initial position in compounds. This is a positional partition: the same character pair serves as PREFIX 5,821 times but as MIDDLE-initial bigram 0 times. The partition is not about individual atoms (c and s both appear as MIDDLE-initial; h appears freely in MIDDLEs) but about the specific bigrams ch and sh.

**Secondary:** C_SAFETY_PRUNING -- The forbidden transition topology includes phantom MIDDLEs as hazard sources, providing defense-in-depth. Even if the positional partition were breached, the safety topology would prevent dangerous transitions.

**Connection to C1178:** The 5 hazard phantoms are a subset of the 15 phantom MIDDLEs identified in C1178. All 15 follow the same dead ch/sh-initial naming pattern. The hazard topology was defined at a level of generality that includes this dead pattern, providing structural insurance.

**Connection to C1546:** Phantom MIDDLEs contain HEAD-set atoms (e, o) at non-initial positions. Per C1494, these are "displaced HEADs" functioning as TERMINALS, not HEADs. If phantoms existed, they would be headless compounds -- consistent with hazard being exclusively a headless phenomenon (C1546).

---

## Constraints Produced

| ID | Claim | Tier |
|---|---|---|
| C1553 | ch/sh-initial compound MIDDLE categorical absence -- 0 types of length 3+, PREFIX:MIDDLE ratio 5,821:0 | 2 |
| C1554 | Phantom MIDDLEs are atom-legal but construction-dead -- defense-in-depth via forbidden topology covering vocabulary-excluded MIDDLEs | 2 |
| C1555 | c-initial compound second-atom selectivity -- c+h at positions 0-1 categorically absent despite c+[k/t/f/p]+h being common (49/55 c-initial compounds contain h at position 2+) | 2 |

---

## Source

`phases/PHANTOM_MIDDLE_MECHANISM/results/phantom_middle_mechanism.json`
