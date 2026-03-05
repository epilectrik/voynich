# C1409: Suffix Atoms Diverge from MIDDLE-Terminal Atoms

**Tier:** 2 (ESTABLISHED)
**Scope:** B, suffix, atom, MIDDLE, cross-position, divergence
**Phase:** SUFFIX_ATOM_DECOMPOSITION (Phase 515)
**Extends:** C1394 (same atom inventory, independent domain), C1190 (MIDDLE behavioral atomicity)
**Relates to:** C1393 (MIDDLE compound composition grammar), C906 (suffix saturation)

---

## Statement

Atoms that appear in both suffix and MIDDLE-terminal position carry **different operational information by position**. Of 12 shared atoms tested, none maintain identical category profiles across positions. JSD ranges from 0.004 (h — most stable) to 0.560 (m — most divergent). The same character encodes different operational emphasis depending on whether it appears in MIDDLE or suffix.

### Cross-Position Category Divergence (T6)

| Atom | Suffix dominant | MIDDLE-terminal dominant | JSD | Stable? |
|------|----------------|------------------------|-----|---------|
| h | MONITORING | MONITORING | 0.004 | Nearly |
| y | THERMAL | THERMAL | 0.042 | Nearly |
| d | THERMAL | THERMAL | 0.055 | Nearly |
| l | THERMAL | STAGING | 0.070 | NO |
| n | THERMAL | THERMAL | 0.084 | Moderate |
| e | THERMAL | THERMAL | 0.085 | Moderate |
| r | THERMAL | FLOW | 0.103 | NO |
| o | THERMAL | STAGING | 0.129 | NO |
| s | TRANSITION | THERMAL | 0.135 | NO |
| a | THERMAL | TRANSITION | 0.229 | NO |
| i | THERMAL | STAGING | 0.493 | NO |
| m | THERMAL | CONTAINMENT | 0.560 | NO |

### Three Stability Tiers

1. **Near-stable** (JSD < 0.06): h, y, d — these atoms have similar function regardless of position
2. **Moderate shift** (JSD 0.06-0.15): l, n, e, r, o, s — same general area but different emphasis
3. **Strong divergence** (JSD > 0.15): a, i, m — fundamentally different operational profiles

### Interpretation

The suffix domain is not simply "MIDDLE atoms in a different slot." It is a **parallel compositional system** using the same alphabet but with position-dependent semantics. Atoms h and y are the most positionally invariant — likely reflecting their fundamental character (h="watch", y="completion/scope"). Atoms like m and i are heavily context-dependent, taking on different operational roles in suffix vs MIDDLE.

This is consistent with C1394's statement that suffix is an "independent compositional domain" — independence means the same symbols are reinterpreted, not copied.

---

## Falsification Criteria

1. If better category assignment (from direct MIDDLE→category mapping rather than PREFIX proxy) shows all atoms with JSD < 0.05, the divergence is an artifact of proxy noise
2. If the divergence is driven entirely by sample size differences (suffix n >> MIDDLE-terminal n for some atoms), bootstrapped JSD may show overlap at CI boundaries

---

## Method

- 12 atoms present in both suffix and MIDDLE-terminal positions
- Category profiles computed via PREFIX proxy (8 categories)
- JSD (Jensen-Shannon divergence) between suffix and MIDDLE-terminal category distributions
- MIDDLE-terminal: last atom of the MIDDLE string (from Morphology extraction)
- Suffix: atom's position within the suffix decomposition

**Script:** `phases/SUFFIX_ATOM_DECOMPOSITION/scripts/suffix_atom_decomposition.py`
**Results:** `phases/SUFFIX_ATOM_DECOMPOSITION/results/suffix_atom_decomposition.json` (T6)
