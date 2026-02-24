# C1251: Atom Gloss Compositional Validation

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** GLOSS_SCALE_VALIDATION (Phase 446)
**Extends:** C1190 (atomicity r=0.754), C1195 (atom confidence tiers), C1191 (position-dependent composition)
**Relates to:** C1250 (category structural coherence), C1209 (MIDDLE positional grammar), C1207 (atom correlation clusters)

---

## Statement

Atom character-to-gloss assignments (k=heat, e=cool, h=watch, y=end, i=iterate, etc.) validate through **composition**, not positional prediction. A 6-test battery on 14 non-kernel atoms (kernel atoms k/e/h excluded as quasi-definitional) produces 2/6 PASS:

| Test | Null Model | Statistic | Result | Key Value |
|------|-----------|-----------|--------|-----------|
| T1: Line-position prediction | Shuffle predictions | Spearman rho | FAIL | rho=0.534, p=0.033 |
| T2: Suffix mode alignment | Shuffle predictions | Spearman rho | FAIL | rho=-0.056, p=0.555 |
| T3: Kernel co-occurrence | Shuffle predictions | Correct/12 | FAIL | 5/12, p=0.244 |
| T4: REGIME differentiation | B (random token labels) | Chi-square | **PASS** | chi2=1473, 37.4x, p=0.000 |
| T5: Compositional consistency | Shuffle atom glosses | Match count | **PASS** | 20/67 (30%) vs 13.9 (21%), p=0.008 |
| T6: Paragraph position | Shuffle predictions | Spearman rho | FAIL | rho=0.165, p=0.286 |

### Key Finding: Composition Pathway

Atom glosses are validated through a three-link compositional chain, each link independently tested:

1. **Atom -> MIDDLE composition** (C1190: r=0.754, p<0.001)
2. **Composed glosses -> MIDDLE category** (T5: 30% match vs 21% shuffled, p=0.008)
3. **MIDDLE category -> structural behavior** (C1250: 5/7 COHERENT)

### Why Directional Predictions Fail

Four tests predicted structural positions from semantic glosses. All fail because **morphological grammar governs position independently of semantic content** (C1191):

- **T2 (suffix mode):** c(adjust) is 92% Mode A, s(sequence) is 78% Mode A — driven by morphological compatibility (ch/sh compounds), not operational semantics
- **T3 (kernel affinity):** d(mark) is 90% E-affiliated because "ed/edy/oed" are common morphological compounds, not because marking is semantically related to cooling
- **T1 (line position):** y(end) appears at position 0.506 (mid-line), not late — "ending" operations can occur at any point in a control sequence

### Structural Reality Confirmed

T4 shows non-kernel atoms differentiate REGIMEs 37.4x more than random token labeling (p=0.000). This confirms atoms carry genuine structural information — the issue is that this information manifests through the compositional chain, not through direct position/co-occurrence prediction from glosses.

### Informative Kernel Affinity Data (T3)

Though the prediction test fails, the actual affinities are structurally informative:

| Atom | Gloss | Actual Dominant | K | E | H |
|------|-------|----------------|---|---|---|
| y | end | E (0.967) | 0.017 | 0.967 | 0.016 |
| d | mark | E (0.896) | 0.050 | 0.896 | 0.054 |
| o | work | E (0.618) | 0.195 | 0.618 | 0.188 |
| t | transfer | E (0.611) | 0.013 | 0.611 | 0.376 |
| l | frame | E (0.526) | 0.244 | 0.526 | 0.230 |
| i | iterate | K (0.513) | 0.513 | 0.263 | 0.224 |
| p | pause | H (0.711) | 0.034 | 0.256 | 0.711 |
| f | flag | H (0.602) | 0.047 | 0.351 | 0.602 |
| c | adjust | H (0.483) | 0.308 | 0.209 | 0.483 |
| s | sequence | H (0.492) | 0.190 | 0.317 | 0.492 |
| r | input | H (0.437) | 0.207 | 0.356 | 0.437 |

**Three affinity groups emerge:** E-affiliated (y, d, o, t, l), K-affiliated (i), H-affiliated (p, f, c, s, r). These reflect morphological composition patterns, not semantic relatedness.

---

## Interpretation

Atom glosses are valid at the compositional level — they correctly predict how atoms combine to produce MIDDLE-level meanings. But atom position within lines, suffix co-occurrence, and kernel co-occurrence are governed by the morphological grammar (C1191, C1209), not by operational semantics. Meaning and position are two independent constraint layers in the Voynich system, analogous to how English word meaning does not predict word position in a sentence.

---

## Method

- 14 non-kernel atoms with >=50 occurrences (g excluded: only 8 standalone occurrences)
- Kernel atoms (k, e, h) excluded: quasi-definitional, not independent validation targets
- Pre-registered directional predictions for all tests, derived from gloss meanings before examining structural data
- Null model: shuffle gloss assignments among non-kernel atoms, keeping kernel atom glosses fixed
- T5 restricted to 67 human-glossed MIDDLEs with 2+ atoms including >=1 non-kernel (avoids circularity with autogloss system)

**Script:** `phases/GLOSS_SCALE_VALIDATION/scripts/atom_gloss_validation.py`
**Results:** `phases/GLOSS_SCALE_VALIDATION/results/atom_gloss_validation.json`
