# C1387: r-Terminal Hazard-Response Partitioning

**Tier:** 2
**Scope:** B
**Phase:** R_ATOM_SEMANTIC_DEEP_DIVE (Phase 497)
**Date:** 2026-03-03
**Depends on:** C1386 (ACTOR/RESPONDER timing split), C1207 (atom clusters), C1208 (carryover classes), C976 (macro-automaton states), C1195 (atom gloss tiers)

## Statement

r-terminal MIDDLEs partition into exactly two forms — **ar** and **or** — with radically different macro-state profiles despite identical suffix mode signatures:

| MIDDLE | n | FL_HAZ | FQ | AXM | AXm | FL_SAFE | CC |
|--------|---|--------|-----|-----|-----|---------|-----|
| ar | 594 | 41.8% | 36.5% | 19.2% | 2.5% | 0% | 0% |
| or | 387 | 0.0% | 70.5% | 25.1% | 4.4% | 0% | 0% |

ar monopolizes FL_HAZ (248 tokens, zero or); or concentrates in FQ (routine). Only three terminal atoms appear at FL_HAZ — r (45.3%), l (34.0%), n (20.7%) — all RESPONDER-class (C1386). r actively suppresses suffix-mode cycling (rho=-0.334, p=0.003).

The r atom's operational gloss upgrades from WEAK "input" to PLAUSIBLE "respond" (C1195). The PLAUSIBLE ceiling exists because only 2 MIDDLE forms (ar, or) make it impossible to fully isolate r's contribution from the initial atom (a vs o).

## Evidence

### E1: FL_HAZ monopoly by ar (P-R6)

r-terminal enrichment at FL_HAZ: 45.34% of all terminal atoms at FL_HAZ are r (4.910x enrichment, chi-sq=1473.71, p≈0). ALL 248 FL_HAZ r-terminal tokens are "ar" — zero "or" appear at FL_HAZ.

Only RESPONDER atoms appear at FL_HAZ:
- r: 45.3% (all ar)
- l: 34.0%
- n: 20.7%
- All others: 0%

### E2: Anti-cycling signal (P-R10)

Paragraph r-density anticorrelates with suffix-mode cycling rate: rho=-0.334, p=0.003 (n=77 paragraphs). r is the strongest anti-cycling terminal atom. More r = sustained response, less oscillation.

### E3: RESPONDER timing confirmation (P-R2, extends C1386)

r post-state-change rate = 72.6% (vs 47.2% baseline). Ranks 2nd among all atoms (after m=78.2%). Confirms RESPONDER class.

### E4: Iteration-axis chaining (P-R5)

r→a forward chain at 2.142x (strongest sequential dependency). n→r backward chain at 1.234x. r→r self-chain at 1.865x. r chains with iteration-axis atoms {a, i, n, r} (C1207), not kernel atoms.

### E5: Identical suffix mode profiles (P-R1, P-R7)

ar = 27.4% Mode A, or = 26.6% Mode A (delta: +0.8pp, negligible). Identical per-state mode profiles. The differentiator is macro-state distribution, not suffix mode.

### E6: Identical line position (P-R8)

ar mean line position: 0.4892, or: 0.4918 (delta: -0.0026). Both perfectly medial.

### E7: Identical kernel environment (P-R9)

k-kernel on ar-lines: 6.12%, or-lines: 5.64% (delta: +0.48pp). All kernel atom deltas < 1pp.

### E8: No paragraph gradient (P-R3)

r-terminal paragraph shape is FLAT (Q0-Q4 all within 0.97-1.03x enrichment). No positional gradient within paragraph bodies.

### E9: No category co-occurrence signal (P-R4)

All category co-occurrence lifts near 1.0x. r is category-neutral at line level.

### E10: Falsified hypotheses

| Hypothesis | Tests | Result | Key falsifying evidence |
|-----------|-------|--------|----------------------|
| Return/reflux (Rücklauf) | P-R1, P-R2, P-R3 | FALSIFIED | No mode split, no paragraph gradient, post-change is non-specific (all RESPONDERs) |
| Flow/run (rinnen) | P-R4, P-R5, P-R6 | PARTIALLY FALSIFIED | No FLOW co-occurrence, no kernel chaining; but FL_HAZ enrichment is extreme (this is ar, not r generally) |
| Ripen/mature (reifen) | P-R7, P-R8, P-R9 | FALSIFIED | No mode-by-state split, no position split, no kernel environment split |
| Repeat (repetieren) | P-R10 | FALSIFIED | Anti-cycling (rho=-0.334), opposite of prediction |

## Relationship to Existing Constraints

- **C1386** (Tier 2): r is a RESPONDER atom (72.6% post-change). This constraint adds the ar/or partitioning detail.
- **C1207** (Tier 2): {a, i, n, r} iteration axis. r→a chaining (2.142x) confirms sequential iteration dependency.
- **C1208** (Tier 2): r is POSITIVE carryover. The anti-cycling signal is consistent with sustained response (positive carryover dampens oscillation).
- **C976** (Tier 1): Macro-automaton states. ar's FL_HAZ monopoly and or's FQ concentration map cleanly onto the state topology.
- **C1195** (Tier 2): Upgrades r from WEAK ("input") to PLAUSIBLE ("respond").

## Falsification

Would be falsified if:
1. r-terminal MIDDLEs with forms other than ar/or were discovered (currently: zero)
2. or were shown to appear at FL_HAZ in a different transcript or track
3. The anti-cycling signal were shown to be a section artifact (currently holds within-section)
4. A third r-terminal form emerged that isolated r's contribution from the initial atom

## Provenance

- `phases/R_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_r06_flhaz_deep_dive.py` — FL_HAZ monopoly (P-R6)
- `phases/R_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_r10_cycling_correlation.py` — anti-cycling (P-R10)
- `phases/R_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_r05_bigram_chaining.py` — iteration-axis chaining (P-R5)
- `phases/R_ATOM_SEMANTIC_DEEP_DIVE/results/r_atom_prediction_results.json` — all 10 rounds structured
