# C1012: PREFIX is a Macro-State Selector via Positive Channeling, Not Negative Prohibition

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** PREFIX_MACRO_STATE_ENFORCEMENT (Phase 330)
**Strengthens:** C662 (PREFIX Role Reclassification), C976 (6-State Transition Topology)
**Relates to:** C911 (102 Forbidden PREFIX × MIDDLE Pairs), C1001 (PREFIX Dual Encoding), C1010 (Minimal Partition), C1011 (Geometric Independence)

---

## Statement

PREFIX is an **extremely powerful macro-state selector** — it reduces macro-state entropy by 76.7% (chi-square = 31,500, p ≈ 0). Many PREFIXes channel 100% of their tokens into a single macro-state. However, the 102 forbidden PREFIX × MIDDLE combinations (C911) are **not the enforcement mechanism**. Prohibitions do not disproportionately target cross-state combinations (23.2% vs 27.8% null), and forbidden CLASS transitions are not preferentially backed by morphological prohibitions (38.9% vs 46.2% null). PREFIX enforces the macro-automaton through **positive selectivity** — which MIDDLEs it includes — not through negative prohibitions.

---

## Evidence

### T1: PREFIX Macro-State Selectivity (PASS)

Contingency table of 16,054 classified B tokens × 27 observed PREFIXes × 6 macro-states:

- Weighted mean macro-state entropy per PREFIX: **0.603 bits** (max possible: 2.585 bits)
- Entropy reduction: **76.7%** (z = 1139 vs 1000 permutations, p = 0)
- Chi-square of independence: 31,500 (p ≈ 0)
- I(PREFIX; macro-state) = 0.876 bits

Multiple PREFIXes show 100% concentration on a single macro-state:
- al, ar → FL_SAFE (100%)
- ct, dch, do, fch, ka, kch, ko, lch → AXM (100%)
- ch, sh → AXM+AXm (100%, confirming C662's 94.1% EN class rate)

### T2: Prohibitions Are NOT Cross-State Targeted (FAIL)

Of 102 forbidden pairs, 56 were classifiable (46 had MIDDLEs absent from the class assignment system). Among the 56:

- CROSS_STATE: 13 (23.2%)
- WITHIN_STATE: 14 (25.0%)
- MIXED: 29 (51.8%)

Null expectation (random MIDDLE reassignment): 27.8% ± 2.9%. Observed cross-state fraction is BELOW null (z = -1.58, p = 0.958). Prohibitions do not target cross-state boundaries.

### T3: Forbidden Transitions Not Backed by Prohibitions (FAIL)

7/18 depleted pairs (38.9%) have at least one morphological prohibition backing. Null (random allowed transitions): 46.2% ± 12.0%. Forbidden transitions are LESS backed than random (z = -0.61, p = 0.786).

Backed transitions: (13,40) FQ→FL_SAFE, (5,34) AXm→AXM, (19,33) AXm→AXM, (3,33) AXm→AXM, (33,38) AXM→FL_SAFE, (13,5) FQ→AXm, (10,28) CC→AXM. Notable: AXm↔AXM and FQ↔FL_SAFE boundaries are backed; FL_HAZ and core CC boundaries are not.

### T4: Position Predicts Macro-State But Mediation is Partial (FAIL threshold, significant signal)

- I(position; macro-state) = 0.0113 bits (z = 44.78, p = 0)
- I(position; macro-state | PREFIX) = 0.0068 bits
- Mediation fraction: 39.9% (below 50% threshold)
- AXM dominance declines from Q1 (71.5%) to Q4 (62.3%)

Position does significantly predict macro-state, and PREFIX mediates 40% of this — but the majority of positional variation in macro-state is not PREFIX-mediated.

### T5: EN PREFIX Channeling (PASS)

ch and sh PREFIXes: 100% of tokens in AXM + AXm. Exceeds the 90% prediction threshold. This extends C662's finding from class-level to macro-state level.

### T6: FL_HAZ+CC Prohibition Enrichment (PASS)

FL_HAZ+CC tokens: 10.5% of corpus. FL_HAZ+CC-targeting prohibitions: 22.5% of total. Enrichment: 2.14x (above 2.0 threshold). Small-state prohibitions are over-represented, consistent with boundary enforcement of rare states.

---

## Interpretation

PREFIX operates as a **positive selector** for macro-states. When a token carries PREFIX "ch", it is channeled into AXM+AXm with 100% certainty — not because "ch" forbids FL_HAZ or CC MIDDLEs, but because the MIDDLEs that co-occur with "ch" are exclusively AXM/AXm-class MIDDLEs.

The 102 negative prohibitions (C911) serve a different function — they prevent specific intra-state and cross-state MIDDLE combinations that would violate finer-grained distributional constraints (C661: PREFIX transforms successor-class profiles, JSD = 0.425). The prohibitions are about behavioral incompatibility within the MIDDLE selection system, not about macro-state boundary enforcement.

This produces a clean architectural picture:
- **PREFIX positive selectivity** → macro-state channeling (this constraint)
- **PREFIX negative prohibitions** → fine-grained behavioral incompatibility (C911, C661)
- **Macro-automaton topology** → 49-class transition structure (C976, C1010)
- **Discrimination manifold** → A-level MIDDLE compatibility (C982, C1011)

Four independent constraint mechanisms, sharing vocabulary but serving distinct structural roles.

---

## Relationship to existing constraints

| Constraint | Relationship |
|-----------|-------------|
| C662 | **Confirmed and extended** — PREFIX role reclassification propagates to macro-state level with 76.7% entropy reduction |
| C911 | **Reframed** — the 102 prohibitions are NOT macro-state enforcement; they serve finer-grained behavioral selectivity |
| C976/C1010 | **Consistent** — macro-automaton topology is enforced by PREFIX positive channeling, not by prohibitions |
| C1001 | **Extended** — PREFIX's positional encoding accounts for 39.9% of position→macro-state link; the rest is independent |
| C1011 | **Strengthened** — another axis of independence: morphological prohibitions and macro-state topology serve different functions |

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| P1 | PREFIX selectivity > 10% | 76.7% | PASS |
| P2 | >60% prohibitions cross-state | 23.2% | FAIL |
| P3 | Forbidden coverage ratio > 1.5 | 0.84 | FAIL |
| P4 | Positional mediation > 50% | 39.9% | FAIL |
| P5 | EN PREFIXes → AXM+AXm > 90% | 100% | PASS |
| P6 | FL_HAZ+CC enrichment > 2x | 2.14x | PASS |

3/6 passed → PARTIAL_ENFORCEMENT

---

## Method

- Single pass over 23,243 B tokens (16,054 mapped to 49-class grammar, 7,042 HT tokens unmapped)
- Morphological extraction via `scripts/voynich.py` Morphology class
- 1000-permutation null models for all statistical tests
- Cross-tabulation of 27 PREFIXes × 6 macro-states
- Classification of 102 prohibitions as CROSS_STATE / WITHIN_STATE / MIXED
- Forbidden transition coverage: 18 depleted pairs tested for morphological backing

**Script:** `phases/PREFIX_MACRO_STATE_ENFORCEMENT/scripts/prefix_enforcement.py`
**Results:** `phases/PREFIX_MACRO_STATE_ENFORCEMENT/results/prefix_enforcement.json`

---

## Verdict

**PARTIAL_ENFORCEMENT**: PREFIX is a powerful macro-state selector through positive channeling, but the 102 specific prohibitions do not enforce macro-state boundaries. The enforcement mechanism is inclusion-based, not exclusion-based.
