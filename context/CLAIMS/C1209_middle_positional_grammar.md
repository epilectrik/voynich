# C1209: MIDDLE Positional Grammar -- Ordered [INITIAL-MEDIAL-TERMINAL] Atom Slots

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** ATOM_BEHAVIORAL_CENSUS (Phase 428)
**Extends:** C1060 (compound atom position grammar V=0.333), C1067 (terminal character positional bias)
**Relates to:** C1190 (behavioral atomicity), C1065 (bigram ordering grammar), C510 (sub-component position classes)

---

## Statement

Individual characters within multi-character MIDDLEs occupy strongly non-random positions, classifying into four position classes. All 18 testable atoms show FDR-significant positional preferences (alpha=0.05). 16,153 tokens with MIDDLE length >= 2 analyzed.

### INITIAL Atoms (mean position 0.07-0.33)

| Atom | N | Mean pos | Initial% | Terminal% |
|------|---|----------|----------|-----------|
| q | 122 | 0.071 | 85.2% | 2.5% |
| a | 3,492 | 0.087 | 86.3% | 3.6% |
| e | 9,085 | 0.214 | 67.5% | 10.2% |
| o | 4,072 | 0.326 | 57.2% | 22.1% |

a and q are near-obligatory INITIAL (>85%). e is strongly initial (67.5%). o is preferentially initial but more flexible (57.2%).

### MEDIAL Atoms (mean position 0.38-0.64)

| Atom | N | Mean pos | Initial% | Terminal% |
|------|---|----------|----------|-----------|
| p | 593 | 0.381 | 26.5% | 17.7% |
| c | 2,114 | 0.408 | 28.9% | 10.3% |
| i | 4,304 | 0.444 | 21.3% | 9.9% |
| f | 199 | 0.507 | 22.1% | 32.2% |
| d | 4,086 | 0.540 | 19.7% | 28.0% |
| s | 424 | 0.640 | 7.5% | 34.4% |

i is core-medial (mean 0.444, 68.7% medial). c and p are early-medial. d and s are late-medial, leaning toward terminal.

### TERMINAL Atoms (mean position 0.77-1.00)

| Atom | N | Mean pos | Initial% | Terminal% |
|------|---|----------|----------|-----------|
| l | 2,399 | 0.768 | 17.8% | 71.4% |
| r | 1,420 | 0.886 | 8.6% | 85.4% |
| h | 1,604 | 0.902 | 1.0% | 77.1% |
| m | 223 | 0.975 | 0.4% | 95.5% |
| y | 4,440 | 0.971 | 1.6% | 96.1% |
| n | 2,152 | 0.998 | 0.0% | 99.4% |

n is effectively fixed-terminal (99.4%). y and m are near-fixed (>95%). h and r are strongly terminal (>77%). l is preferentially terminal but allows initial position (17.8%).

### FREE Atoms (no strong preference)

| Atom | N | Mean pos | Initial% | Terminal% |
|------|---|----------|----------|-----------|
| k | 2,355 | 0.478 | 43.2% | 38.6% |
| t | 922 | 0.524 | 37.4% | 41.8% |

k and t are the only position-free atoms. Both are kernel operators (C520-C521) and can appear at any position within a MIDDLE. This is consistent with their role as energy-state operators that can be deployed at any point in a compound instruction.

---

## Ordered Slot Grammar

MIDDLEs follow an approximate slot structure:

```
[a/q/e/o] + [c/i/p/d/f/s] + [y/n/m/r/h/l]
 INITIAL      MEDIAL          TERMINAL
```

With k and t insertable at any position. This is consistent with C1065 (atom bigram ordering grammar) and C1070 (ordering independent of kernel bias), but operates at the individual character level rather than the multi-character atom level of those constraints.

---

## Relation to C1060 and C1067

C1060 tested multi-character atoms (sub-components like 'opch', 'ai', 'kc') for position within compounds. C1067 showed terminal character drives compound position. This constraint operates at a finer granularity: individual characters within individual MIDDLEs. The results are consistent: C1067's terminal-biased characters (d, i, c) map to our MEDIAL/TERMINAL classes, and C1067's initial-biased characters (p, l, k) align with our INITIAL/FREE/TERMINAL patterns.

---

## Method

- 16,153 Currier B tokens with MIDDLE length >= 2
- Normalized position: 0.0 = first character, 1.0 = last character
- Chi-squared per atom: observed {initial, medial, terminal} vs global proportion
- Benjamini-Hochberg FDR correction at alpha=0.05
- Bias classification: >1.5x global rate in a position class

**Script:** `phases/ATOM_BEHAVIORAL_CENSUS/scripts/atom_census_test.py` (T3)
**Results:** `phases/ATOM_BEHAVIORAL_CENSUS/results/atom_census_results.json`
