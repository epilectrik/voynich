# APP-1: Apparatus Behavioral Validation — Phase Specification

**Status:** IN PROGRESS
**Date:** 2026-01-13
**Tier:** 3 (Exploratory, Non-Binding)
**Prerequisites:** PWRE-1 ✅, FM-PHY-1 ✅, SSD-PHY-1a ✅, OJLM-1 ✅

---

## Core Question

> **Does any historical apparatus exhibit the exact same responsibility split, failure fears, judgment omissions, and control affordances we have reconstructed?**

This is **behavioral validation**, not apparatus identification or semantic decoding.

---

## Gating Conditions Met

This phase is appropriate ONLY because:

1. ✅ **Controller fully reconstructed** (Tier 0-2 closed)
2. ✅ **Plant class strongly constrained** (PWRE-1 + FM-PHY-1)
3. ✅ **Human-system boundary explicitly mapped** (OJLM-1)

---

## Critical Constraints

### MUST NOT (Tier 0-2 Protection)

- ❌ Map tokens → parts ("k = furnace", "h = alembic head")
- ❌ Read drawings as schematics
- ❌ Identify specific substances flowing through parts
- ❌ Claim "this diagram is a pelican"
- ❌ Violate C384, C383, or semantic ceiling

### MAY (Behavioral Ethnography)

- ✅ Compare responsibility partition against historical manuals
- ✅ Test failure-fear proportions against operator accounts
- ✅ Verify judgment-omission patterns against apparatus requirements
- ✅ Check state-space necessity against apparatus complexity

---

## Research Axes (Pre-Registered)

### Axis 1: Responsibility-Split Matching

**Question:** Do historical apparatus manuals assume exactly the same human responsibilities?

**What We Know (OJLM-1):**
- ENCODES: legality, compatibility, recovery, safety
- REFUSES TO ENCODE: sensory calibration, timing intuition, phase recognition

**Test:**
- Manuals that explain sensory cues → ❌ MISMATCH
- Manuals that omit them entirely → ✅ MATCH

---

### Axis 2: Failure-Fear Alignment

**Question:** Do operators fear the same things in the same proportions?

**What We Know (FM-PHY-1):**
- Phase ordering: DOMINANT (41%)
- Contamination + Containment: SECONDARY (24% each)
- Energy & Rate: MINOR (6% each)

**Test:** Compare operator failure accounts to 41/24/24/6/6 distribution.

---

### Axis 3: Judgment-Omission Test

**Question:** Does any apparatus require exactly 13 judgment types?

**What We Know (OJLM-1):**
13 types across 3 categories:
- Watch Closely (6): Temperature, Phase Transition, Quality/Purity, Timing, Material State, Stability
- Forbidden Intervention (3): Equilibrium Establishment, Phase Transition, Purification Cycle
- Tacit Knowledge (4): Sensory Calibration, Equipment Feel, Timing Intuition, Trouble Recognition

**Test:** Binary per apparatus - excess or deficit → mismatch.

---

### Axis 4: State-Space Necessity Match

**Question:** Does apparatus generate ~100+ categorical states?

**What We Know (SSD-PHY-1a):**
- ~128 categorical distinctions
- Forced by plant state-space
- Low-dimensional spaces insufficient

**Test:** Count distinct states, assess quantifiability.

---

## Target Apparatus Families

| Family | Status | Rationale |
|--------|--------|-----------|
| Circulatory reflux alembics (pelican) | ✅ PRIMARY | Matches all constraints |
| Multi-pass aromatic water distillation | ✅ SECONDARY | High state complexity |
| Closed-loop conditioning vessels | ✅ TERTIARY | Non-batch, circulatory |
| Simple retorts | ❌ EXCLUDED | No recirculation |
| Open stills | ❌ EXCLUDED | Batch, simple |
| Straight batch heating | ❌ EXCLUDED | No closed loop |
| Any with calibrated instrumentation | ❌ EXCLUDED | Reduces judgment load |

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Historical sources surveyed | ≥ 5 operator-centric texts |
| Responsibility-split test | At least 1 apparatus matches ALL omissions |
| Failure-fear proportion | Within 15% of 41/24/24/6/6 |
| Judgment requirement | All 13 types required (no excess, no deficit) |
| State complexity | ~100+ categorical distinctions |

**STRONG MATCH:** An apparatus that passes ALL FOUR axes.

---

## Correct Framing (REQUIRED)

> **"We are not identifying the apparatus depicted in the Voynich Manuscript. We are testing whether any historical apparatus requires the same control architecture, judgment partition, and failure logic."**

---

## Deliverables

- `phase_specification.md` - This document
- `responsibility_split_survey.md` - Axis 1 results
- `failure_fear_analysis.md` - Axis 2 results
- `judgment_requirement_test.md` - Axis 3 results
- `state_complexity_assessment.md` - Axis 4 results
- `APP_1_PHASE_SUMMARY.md` - Summary

---

## Epistemic Safety Clause

> *This phase does not decode the Voynich Manuscript. It tests whether any historical apparatus requires the same control architecture, judgment partition, and failure logic - without claiming token meanings, part identities, or diagram interpretations. All findings are Tier 3 unless they establish logical necessity.*

---

*Phase specification created 2026-01-13*
