# C892: Post-FQ h-Dominance

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Following FREQUENT_OPERATOR (escape) tokens, h-containing tokens dominate (24-36%) over e-containing (3-8%) and k-containing (17-25%) tokens across all REGIMEs. Recovery enters through phase-alignment (h) rather than equilibration (e).

---

## Evidence

**Test:** `phases/REVERSE_BRUNSCHWIG_TEST/scripts/09_recovery_orthogonality.py`

### Post-FQ First Kernel Distribution

| REGIME | Post-FQ h% | Post-FQ k% | Post-FQ e% | Dominant |
|--------|------------|------------|------------|----------|
| R3 | 36.4% | 17.3% | 5.0% | h |
| R1 | 31.1% | 25.3% | 6.6% | h |
| R4 | 25.0% | 22.1% | 2.8% | h |
| R2 | 24.2% | 19.1% | 8.1% | h |

**h dominates in ALL 4 REGIMEs.**

### Ordering Consistency

Across all REGIMEs, post-FQ kernel ordering is: h > k > e

This ordering holds regardless of REGIME (intense, gentle, precision, standard).

---

## Interpretation

### Refines C105 (e = STABILITY_ANCHOR)

C105 states that 54.7% of recovery paths pass through e. This constraint clarifies the pathway:

1. **FQ (escape)** → **h (phase alignment)** → **e (stabilization)**

The 54.7% figure in C105 refers to paths **containing** e, not the immediate successor of FQ. Recovery enters via h first, then reaches e.

### Closed-loop vs Linear

**Brunschwig (linear):** "Cooling" (equilibration) is primary recovery - let things settle down
**Voynich (closed-loop):** "Phase checking" (h) is primary recovery - verify state before proceeding

This makes sense for state-responsive control:
- After an escape event, you first CHECK where you are (h = phase alignment)
- Only then do you STABILIZE (e = equilibration)
- Jumping directly to equilibration without phase-checking risks compounding errors

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C105 | Refined - e is anchor, but h is entry point |
| C873 | Compatible - positional ordering (e < h < k) differs from recovery pathway |
| C890 | Related - recovery pathway is independent of recovery rate |

---

## Provenance

- **Phase:** REVERSE_BRUNSCHWIG_TEST
- **Date:** 2026-01-30
- **Script:** 09_recovery_orthogonality.py

---

## Navigation

<- [C891_energy_frequent_inverse.md](C891_energy_frequent_inverse.md) | [INDEX.md](INDEX.md) ->
