# C1414: Cross-Slot Atom Co-occurrence Exclusion Rules

**Tier:** 2 (ESTABLISHED)
**Scope:** B, MIDDLE, suffix, atom, co-occurrence, exclusion
**Phase:** CROSS_SLOT_INTERACTION (Phase 516)
**Extends:** C1190 (MIDDLE behavioral atomicity), C1409 (suffix atoms diverge from MIDDLE-terminal)
**Relates to:** C1393 (MIDDLE composition grammar), C1408 (suffix compositional structure), C475 (MIDDLE atomic incompatibility)

---

## Statement

Atoms appearing in both MIDDLE and SUFFIX of the same token show strong co-occurrence biases: d REPELS (O/E=0.203, p=7.1e-81), a REPELS (O/E=0.465, p=1.9e-29), h REPELS (O/E=0.509, p=6.6e-9), while e ATTRACTS (O/E=1.310, p=3.8e-50). Additionally, two absolute MIDDLE TERM x SUFFIX HEAD prohibitions exist: l-terminal MIDDLEs never take e-headed suffixes (0 observed, 37 expected) and r-terminal MIDDLEs never take e-headed suffixes (0 observed, 46 expected).

### MIDDLE x SUFFIX Same-Atom Co-occurrence

| Atom | O/E ratio | Direction | chi2 | p | mid_rate | suf_rate |
|------|-----------|-----------|------|---|----------|----------|
| d | 0.203 | STRONG REPEL | 362.7 | 7.1e-81 | 12.4% | 26.7% |
| a | 0.465 | REPEL | 126.9 | 1.9e-29 | 8.3% | 30.8% |
| h | 0.509 | REPEL | 33.7 | 6.6e-9 | 13.3% | 7.7% |
| o | 0.634 | REPEL | 28.4 | 1.0e-7 | 19.5% | 7.4% |
| e | 1.310 | ATTRACT | 221.7 | 3.8e-50 | 34.5% | 28.2% |
| m | 10.156 | ATTRACT | 33.6 | 6.8e-9 | 0.2% | 2.7% |
| i | 1.024 | NEUTRAL | 0.1 | 0.804 | 6.6% | 16.7% |
| y | 1.052 | NEUTRAL | 0.6 | 0.455 | 2.0% | 51.8% |

### Absolute MIDDLE TERM x SUFFIX HEAD Prohibitions

| MIDDLE TERM | SUFFIX HEAD | Expected | Observed | Interpretation |
|-------------|-------------|----------|----------|----------------|
| l | e | 36.9 | 0 | State-marking MIDDLEs never take stability suffixes |
| r | e | 46.3 | 0 | Response-marking MIDDLEs never take stability suffixes |

### Interpretation

**Repulsion (d, a, h, o):** When MIDDLE already encodes an operation using atom X, the suffix avoids X to carry DIFFERENT information. This is a complementary-information principle at the atom level — MIDDLE and suffix each contribute distinct parameters.

**Attraction (e):** Stability (e) accumulates across both MIDDLE and suffix, consistent with e-depth as a scaling parameter (C1197, C1225). Stability is the one operational dimension where MIDDLE and suffix REINFORCE rather than complement.

**Absolute prohibitions (l-TERM and r-TERM x e-SUFFIX):** MIDDLEs ending in state-marker l (C1385) or response-marker r (C1387) categorically refuse stability-headed suffixes. These MIDDLEs already encode exit conditions; their suffixes must carry non-stability information (mode B atoms: a, i, o).

---

## Falsification Criteria

1. If d co-occurrence O/E exceeds 0.50 with corrected morphological parsing, the strong repulsion weakens
2. If l-TERM x e-SUFFIX or r-TERM x e-SUFFIX tokens are found at non-negligible frequency, the absolute prohibition fails
3. If e attraction disappears when controlling for specific MIDDLE types (e.g., only edy driving it), the effect is MIDDLE-specific not atom-level

---

## Method

- 11,151 suffixed Currier B tokens with both MIDDLE and suffix decomposed into atoms
- For each of 12 atoms present in both MIDDLE and suffix: 2x2 contingency table (mid_has_atom x suf_has_atom)
- Expected count under independence: P(mid_has) * P(suf_has) * N
- Chi-squared test for each atom
- Separate analysis for MIDDLE TERM x SUFFIX HEAD junction pairs (N=995 tokens with compound MIDDLE + multi-atom suffix)

**Script:** `phases/CROSS_SLOT_INTERACTION/scripts/cross_slot_interaction.py`
**Results:** `phases/CROSS_SLOT_INTERACTION/results/cross_slot_interaction.json` (T6, T9)
