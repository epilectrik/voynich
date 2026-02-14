# FL vs FLOW_OPERATOR Disambiguation

**Status:** Reference | **Created:** 2026-01-31

---

## The Problem

"FL" is used for two different concepts that overlap but measure different things:

1. **FL (MIDDLE taxonomy)** - Material state index based on MIDDLE morphemes
2. **FLOW_OPERATOR (49-class role)** - Behavioral role in the 49-class grammar

This document clarifies the distinction.

---

## FL: Material State Index (C777)

**Abbreviation:** FL (preferred)

**Definition:** MIDDLEs that index material progression through a process. ~25% of all B tokens contain FL MIDDLEs.

**MIDDLEs (17 total):**

| Stage | MIDDLEs | Position Range |
|-------|---------|----------------|
| INITIAL | ii, i | 0.30-0.35 |
| EARLY | in | 0.42 |
| MEDIAL | r, ar | 0.51-0.55 |
| LATE | al, l, ol | 0.61-0.64 |
| FINAL | o, ly, am | 0.75-0.80 |
| TERMINAL | m, dy, ry, y | 0.86-0.94 |

**Key Properties:**
- Within-line positional gradient (C777)
- Tracks "where material IS" in state space
- Present in ~25% of tokens across all 49 classes
- Does not progress across lines (each line samples independently; C1031)

**Provenance:** C777, C770-C776, C785-C787

---

## FLOW_OPERATOR: 49-Class Behavioral Role

**Abbreviation:** FO (to avoid confusion with FL)

**Definition:** One of 5 behavioral roles in the 49-class grammar. Specific tokens with specific grammatical behavior.

**Classes:** {7, 30, 38, 40}

**Token Share:** 4.7% of B (1,078 tokens)

**Key Properties:**
- Primitive substrate layer (no kernel chars k/h/e)
- Hazard-source role (initiates 4.5x more hazard than receives)
- Split into hazard pair {7, 30} and safe pair {38, 40}
- Specific tokens: dar, dal, daly, ary, dain, etc.

**Provenance:** C121, C562, C582, C586

---

## Relationship

| Aspect | FL (MIDDLE) | FO (49-class) |
|--------|-------------|---------------|
| Scope | Any token with FL MIDDLE | Specific tokens in 4 classes |
| Coverage | ~25% of B tokens | 4.7% of B tokens |
| Measures | Material state position | Grammatical behavior |
| Within-line | Positional gradient | Role in control cycle |

**Overlap:** FLOW_OPERATOR tokens contain FL MIDDLEs, but FL MIDDLEs appear across many classes (EN, AX, FQ, etc.).

**Example:**
- Token `chedy` has FL MIDDLE `y` (TERMINAL) but is class 14 (FQ), not FLOW_OPERATOR
- Token `daly` has FL MIDDLE `y` and IS class 40 (FLOW_OPERATOR)

---

## Usage Guidelines

| When discussing... | Use... |
|--------------------|--------|
| Material state tracking | **FL** |
| Within-line positional gradient | **FL** |
| MIDDLE taxonomy (C777) | **FL** |
| 49-class behavioral role | **FLOW_OPERATOR** or **FO** |
| Hazard-source/safe split | **FLOW_OPERATOR** or **FO** |
| Classes 7, 30, 38, 40 | **FLOW_OPERATOR** or **FO** |

---

## Related Constraints

- C777: FL State Index (defines FL MIDDLE taxonomy)
- C770-C776: FL primitive architecture
- C785-C787: FL transitions and forward bias
- C562: FLOW_OPERATOR role structure
- C586: FLOW_OPERATOR internal structure (hazard/safe split)
