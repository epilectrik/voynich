# C1403: MONOSTATE is Thematic Dominance Not Sequential Convergence

**Tier:** 2 (ESTABLISHED)
**Scope:** B, convergence, MONOSTATE, AXM, reframe
**Phase:** STATE_C_CONVERGENCE_REVISIT (Phase 513)
**Reframes:** C074 (dominant convergence), C079 (only STATE-C essential), C084 (system targets MONOSTATE)
**Extends:** C1401 (section confound), C1402 (no sequential convergence)
**Relates to:** C976 (6-state automaton), C1010 (6-state invariant partition), C324 (section-dependent terminals)

---

## Statement

C084's "system targets MONOSTATE" describes AXM's role as the **dominant operational mode** within each folio program (59-75% AXM by section), not convergence toward a terminal state. Programs do not navigate toward STATE-C; they operate within AXM from the start at a section-determined rate. The three Tier 0 facts (C074, C079, C084) remain factually correct but their "convergence" framing is reinterpreted.

### Reframing of Early Findings

| Constraint | Original Framing | Reframed Understanding |
|-----------|------------------|----------------------|
| C074 (57.8% STATE-C) | Folios "converge to" STATE-C | 57.8% is the corpus-wide average of section-level AXM thematic profiles |
| C079 (only STATE-C essential) | Programs "reach completion" through STATE-C | AXM is the universally present dominant mode in every section |
| C084 (MONOSTATE) | Grammar targets a single stable endpoint | AXM is the default operational mode; programs orbit it with section-determined rates |
| C325 (completion gradient) | Later folios are "more complete" | Section B (highest AXM) is positioned later in the manuscript (C1401) |

### Section-Level AXM Thematic Profiles

| Section | Mean AXM Rate | Interpretation |
|---------|--------------|----------------|
| B | 74.5% | Highest AXM dominance |
| S | 66.8% | Moderate |
| H | 58.9% | Lower but still majority AXM |
| C | 58.2% | Similar to H |

### What "MONOSTATE" Now Means

The grammar has a single dominant attractor (AXM, self-transition 0.697). Every program spends most of its time there. But the mechanism is not sequential convergence — it is **thematic dominance from the outset**:

1. The folio's section determines its AXM rate (C324)
2. Paragraphs within the folio independently sample from this rate (C1400, C1402)
3. No paragraph position or terminal state predicts any other paragraph's behavior (C1399, C1400)
4. Kernel contact rates are flat throughout programs (C666) — no ramp-up or wind-down
5. C1038's within-AXM entropy narrowing is grammar-level, not program-specific

The 42.2% non-STATE-C folios are not "incomplete programs that didn't converge" — they are programs whose section-level thematic envelope has a lower AXM rate, producing terminal lines that happen to land in non-AXM states.

---

## Relationship to Tier 0 Constraints

This constraint **reframes but does not contradict** the Tier 0 facts:
- The statistical facts (57.8%, MONOSTATE, only STATE-C essential) remain true
- The dynamical interpretation (sequential convergence) is replaced by a static one (thematic dominance)
- No Tier 0 constraint needs to be reopened or modified — only the narrative around them changes

---

## Falsification Criteria

1. If a conditioning variable (REGIME, section, paragraph type) reveals hidden sequential convergence in a subpopulation, the thematic-dominance interpretation is incomplete
2. If C1038's entropy convergence is shown to operate between macro-states (not just within AXM), sequential convergence toward AXM exists at the token level
3. If the folio ICC for AXM rate increases substantially (above 0.50) with better state classification, folio theme may be more deterministic than suggested

---

## Method

Synthesis of T1-T7 from Phase 513. All tests confirm: no sequential convergence at any scale, section determines AXM rate, paragraph position adds nothing.

- T1: Section confound (C325 collapses within sections)
- T2: Paragraph terminal AXM (folio ICC=0.286, 71% paragraph-level variation)
- T3: No cross-paragraph convergence (rho=-0.019, p=0.78)
- T4: Full paragraph independence (rho=0.001, perm p=0.983)
- T5: Folio theme sufficient (position -29.6% worse)
- T6: No within-paragraph convergence (rho=-0.016, p=0.535)

**Script:** `phases/STATE_C_CONVERGENCE_REVISIT/scripts/state_c_revisit.py`
**Results:** `phases/STATE_C_CONVERGENCE_REVISIT/results/state_c_revisit.json` (all tests)
