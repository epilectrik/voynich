# EXT-3 Survivor Summary

**Phase:** EXT-3 (Failure & Hazard Alignment)
**Date:** 2026-01-05
**Purpose:** Documentation of processes surviving hazard/restart alignment

---

## Overview

EXT-3 tested whether EXT-2 historical processes fail in ways matching OPS hazard topology. Four processes survive with demonstrated alignment.

---

## Full Survivors (Tier 2)

### 1. CIRCULATIO (Pelican Circulation)

#### Why It Survives

| Criterion | Assessment | Evidence |
|-----------|------------|----------|
| OPS Hazard Match | **5/5 STRONG** | All hazard classes present |
| Restart Tolerance | **NOT TOLERATED** | Weeks of work lost |
| Operator Burden | **HIGH** | Continuous expert vigilance |
| Doctrine Alignment | **5/5 PASS** | All principles satisfied |

#### Hazard Alignment Detail

| OPS Hazard Class | Circulatio Failure | Match Strength |
|------------------|-------------------|----------------|
| PHASE_ORDERING (41%) | Vapor lock, premature condensation | ✅ STRONG |
| COMPOSITION_JUMP (24%) | Contamination from improper separation | ✅ STRONG |
| CONTAINMENT_TIMING (24%) | Seal failure, product escape | ✅ STRONG |
| RATE_MISMATCH (6%) | Circulation stall, flow disruption | ✅ STRONG |
| ENERGY_OVERSHOOT (6%) | Thermal runaway, bumping | ✅ STRONG |

**Phase Ordering Dominance:** The 41% dominance of PHASE_ORDERING in OPS hazards matches exactly the primary failure mode of circulatio: vapor and liquid must be in correct locations within the closed loop. Vapor lock (vapor trapped in arm) and premature condensation (condensate forming before proper separation) are phase-positioning failures.

#### Restart Intolerance Detail

| Factor | Circulatio | OPS Alignment |
|--------|------------|---------------|
| Restart requires | Full apparatus reset: cool, disassemble, clean, recharge | P3 PASS |
| Time investment lost | Days to weeks | EXTREME |
| Product recovery | None - batch contaminated | P2 PASS |
| Historical emphasis | "Forty weeks" operations; patience valued | P1 PASS |

#### Operator Burden Detail

| Factor | Circulatio | OPS Alignment |
|--------|------------|---------------|
| Monitoring | Continuous (glass vessels allow observation) | EXPERT_REFERENCE |
| Judgment type | Experiential (circulation "rightness") | EXPERT_REFERENCE |
| Waiting with vigilance | Extended waiting with periodic assessment | P1 PASS |

#### Confidence: **TIER 2 (Strong)**

Circulatio shows complete structural alignment with OPS. All five hazard classes are present, restart is catastrophic, and operator burden matches the EXPERT_REFERENCE archetype.

---

### 2. COHOBATIO (Repeated Reflux Distillation)

#### Why It Survives

| Criterion | Assessment | Evidence |
|-----------|------------|----------|
| OPS Hazard Match | **5/5 STRONG** | All hazard classes present |
| Restart Tolerance | **NOT TOLERATED** | Multi-pass investment lost |
| Operator Burden | **HIGH** | Continuous expert vigilance |
| Doctrine Alignment | **5/5 PASS** | All principles satisfied |

#### Hazard Alignment Detail

| OPS Hazard Class | Cohobatio Failure | Match Strength |
|------------------|-------------------|----------------|
| PHASE_ORDERING (41%) | Flooding (liquid where vapor should be) | ✅ STRONG |
| COMPOSITION_JUMP (24%) | Fraction contamination | ✅ STRONG |
| CONTAINMENT_TIMING (24%) | Overflow, vessel breakage, spillage | ✅ STRONG |
| RATE_MISMATCH (6%) | Flooding/channeling from rate imbalance | ✅ STRONG |
| ENERGY_OVERSHOOT (6%) | Bumping, scorching | ✅ STRONG |

**Phase Ordering Dominance:** Flooding—the primary cohobatio failure—is exactly phase ordering: liquid accumulates where vapor should flow. This matches the 41% dominance of PHASE_ORDERING in OPS.

**Rate Mismatch Precision:** The 6% RATE_MISMATCH frequency matches the real but relatively rare flooding/channeling failure mode in cohobatio.

#### Restart Intolerance Detail

| Factor | Cohobatio | OPS Alignment |
|--------|-----------|---------------|
| Restart requires | Drain and restart from beginning | P3 PASS |
| Investment structure | Accumulating (7-fold distillation) | EXTREME |
| Late failure cost | Destroys hours/days of work | P2 PASS |
| Historical emphasis | Purity over speed; multiple careful passes | P5 PASS |

#### Operator Burden Detail

| Factor | Cohobatio | OPS Alignment |
|--------|-----------|---------------|
| Monitoring | Continuous for fraction quality | EXPERT_REFERENCE |
| Judgment type | Experiential (purity assessment) | EXPERT_REFERENCE |
| Duration | Extended (multiple stages over hours/days) | EXPERT_REFERENCE |

#### Confidence: **TIER 2 (Strong)**

Cohobatio shows complete structural alignment with OPS. The multi-pass structure creates accumulating investment that makes late failure catastrophic, matching P3 exactly.

---

## Partial Survivors (Tier 3)

### 3. ATHANOR DIGESTION (Extended Operations)

#### Why It Survives (Despite Partial Hazard Match)

| Criterion | Assessment | Evidence |
|-----------|------------|----------|
| OPS Hazard Match | **3/5 STRONG, 2/5 PARTIAL** | Reduced but present |
| Restart Tolerance | **EXTREME INTOLERANCE** | Months of work lost |
| Operator Burden | **HIGH** (extended duration) | Patience is definitional |
| Doctrine Alignment | **4/5 PASS** | P1, P2, P3, P5 satisfied |

#### Hazard Alignment Detail

| OPS Hazard Class | Athanor Failure | Match Strength |
|------------------|-----------------|----------------|
| PHASE_ORDERING (41%) | Less applicable (slow process) | ⚠️ PARTIAL |
| COMPOSITION_JUMP (24%) | Contamination over extended period | ✅ STRONG |
| CONTAINMENT_TIMING (24%) | Seal failure over days/weeks | ✅ STRONG |
| RATE_MISMATCH (6%) | Heat rate variations | ⚠️ PARTIAL |
| ENERGY_OVERSHOOT (6%) | Overheating during extended operation | ✅ STRONG |

**Why Partial Match Is Acceptable:** The athanor's primary failure modes (contamination, seal failure, overheating) match 3/5 OPS hazard classes strongly. The partial matches (phase ordering, rate mismatch) reflect the inherently slow nature of digestion rather than structural incompatibility.

#### Restart Intolerance Detail — CRITICAL

| Factor | Athanor | OPS Alignment |
|--------|---------|---------------|
| Typical operation duration | "Forty weeks" documented | EXTREME |
| Investment structure | Linear accumulation over time | P3 EXTREME PASS |
| Restart cost | MONTHS of work lost | CATASTROPHIC |
| Historical emphasis | "Slow Henry" - patience is definitional | P1 EXTREME PASS |

**Why Extreme Duration Compensates for Partial Hazard Match:**

The athanor's restart intolerance is so extreme (months of operation lost) that it EXCEEDS the restart intolerance of circulatio and cohobatio. Even with partial hazard match (3/5), the P3 alignment is stronger than any other process.

Historical documentation explicitly names the athanor "Slow Henry" (piger Henricus) because patience is its defining characteristic. This matches OPS P1 (Waiting Is Default) at extreme levels.

#### Operator Burden Detail

| Factor | Athanor | OPS Alignment |
|--------|---------|---------------|
| Monitoring | Low-continuous (designed for unattended operation) | ACCEPTABLE |
| Judgment type | Setup and fuel management | EXPERT_REFERENCE |
| Duration commitment | EXTREME (weeks to months) | P5 PASS |

**Note on Monitoring:** The athanor is designed for unattended operation (self-feeding fuel mechanism), which might seem to contradict EXPERT_REFERENCE. However, this reflects the nature of digestion (slow, uniform heat) rather than lack of expertise. The operator must know when to start, how to set up, and when the process is complete—all expert judgments.

#### Confidence: **TIER 3 (Partial Hazard, Extreme Restart)**

Survives with reduced confidence due to partial hazard match. Extreme restart intolerance compensates for reduced hazard alignment.

---

### 4. QUINTESSENCE CIRCULATION (Multiple-Pass)

#### Why It Survives (Despite Being Apothecary Distillation Subset)

| Criterion | Assessment | Evidence |
|-----------|------------|----------|
| OPS Hazard Match | **4/5 STRONG, 1/5 PARTIAL** | Strong match |
| Restart Tolerance | **NOT TOLERATED** | Seven-fold investment lost |
| Operator Burden | **HIGH** | Purity across passes |
| Doctrine Alignment | **5/5 PASS** | All principles satisfied |

#### Hazard Alignment Detail

| OPS Hazard Class | Quintessence Failure | Match Strength |
|------------------|----------------------|----------------|
| PHASE_ORDERING (41%) | Critical for extreme purity | ✅ STRONG |
| COMPOSITION_JUMP (24%) | Impurity ruins multi-pass work | ✅ STRONG |
| CONTAINMENT_TIMING (24%) | Loss of precious product | ✅ STRONG |
| RATE_MISMATCH (6%) | More critical at high purity | ⚠️ PARTIAL |
| ENERGY_OVERSHOOT (6%) | Destroys concentrated product | ✅ STRONG |

#### Restart Intolerance Detail — Why This Subset Survives

| Factor | Quintessence | OPS Alignment |
|--------|--------------|---------------|
| Pass structure | Seven-fold distillation (Rupescissa) | ACCUMULATING |
| Investment type | Each pass adds value | P3 PASS |
| Late failure cost | Destroys multiple passes of work | CATASTROPHIC |
| Historical emphasis | Purity paramount; no shortcuts | P5 PASS |

**Distinction from Aqua Vitae Simplex (Eliminated):**

| Factor | Aqua Vitae Simplex | Quintessence |
|--------|-------------------|--------------|
| Passes | Single | Seven |
| Investment | Single batch | Accumulated |
| Restart cost | One batch of wine | Hours/days of refinement |
| Economic barrier | LOW (wine is cheap) | HIGH (time investment) |

The key structural difference is **accumulating investment**. Simple aqua vitae is a single-pass process where restart means losing one batch of wine (cheap). Quintessence is a seven-pass process where restart means losing the accumulated refinement of multiple distillations.

#### Operator Burden Detail

| Factor | Quintessence | OPS Alignment |
|--------|--------------|---------------|
| Monitoring | HIGH - purity must be maintained across passes | EXPERT_REFERENCE |
| Judgment type | Experiential (quintessence quality) | EXPERT_REFERENCE |
| Duration | Extended (multiple stages) | EXPERT_REFERENCE |

#### Confidence: **TIER 3 (Subset of Class I)**

Survives as a specific subset of apothecary distillation. The multiple-pass structure creates accumulating investment that distinguishes it from eliminated aqua vitae simplex.

---

## Survivor Comparison

| Process | Hazard Match | Restart Intolerance | Duration | Confidence |
|---------|--------------|---------------------|----------|------------|
| Circulatio | 5/5 STRONG | HIGH (weeks) | Days-weeks | **Tier 2** |
| Cohobatio | 5/5 STRONG | HIGH (multi-pass) | Hours-days | **Tier 2** |
| Athanor | 3/5 STRONG | EXTREME (months) | Weeks-months | **Tier 3** |
| Quintessence | 4/5 STRONG | HIGH (multi-pass) | Hours-days | **Tier 3** |

---

## Common Survivor Features

### What All Survivors Share

1. **Irreversible Failure Modes**
   - All survivors have failures that cannot be undone
   - Once contaminated, scorched, or phase-disordered, the batch is lost

2. **Accumulating Investment**
   - All survivors have investment that grows over operation time
   - Restart means losing accumulated work, not just materials

3. **Expert Judgment Required**
   - All survivors require experiential judgment for quality assessment
   - No simple procedural checklist can substitute for expertise

4. **Waiting Is Structural**
   - All survivors have extended waiting built into the process
   - Not optional patience, but structural necessity

5. **Catastrophic Restart**
   - All survivors make restart economically or temporally catastrophic
   - Restart requires returning to baseline (not just fresh materials)

### Why These Features Match OPS

| Survivor Feature | OPS Doctrine Principle |
|------------------|----------------------|
| Irreversible failure | P2: Escalation Is Irreversible |
| Accumulating investment | P3: Restart Requires Low Engagement |
| Expert judgment | OPS-6.A: EXPERT_REFERENCE archetype |
| Waiting structural | P1: Waiting Is Default |
| Catastrophic restart | P3, P2 combined |

---

## What Survivors Do NOT Establish

- **No Products Identified:** Survivors describe process types, not specific products
- **No Materials Identified:** What was circulated, cohobated, or digested is not specified
- **No Illustrations Interpreted:** Visual content not used
- **No OPS Modification:** OPS constraints remain locked; this is external comparison

---

## Survivor Space Reduction

### EXT-2 → EXT-3 Reduction

| EXT-2 Processes | EXT-3 Survivors | Reduction |
|-----------------|-----------------|-----------|
| Circulatio | Circulatio | 1:1 |
| Cohobatio | Cohobatio | 1:1 |
| Digestio (3 variants) | Athanor only | 3:1 |
| Hydrodistillation | None | ELIMINATED |
| Apothecary (2 variants) | Quintessence only | 2:1 |
| **Total: 8** | **Total: 4** | **50% reduction** |

### Survivor Process Space

The surviving process space is:

1. **Closed-loop circulation** (Circulatio)
2. **Multi-pass redistillation** (Cohobatio)
3. **Extended thermal conditioning** (Athanor)
4. **Multi-pass refinement** (Quintessence)

All survivors share: **circulatory or accumulating operation with catastrophic restart**.

---

## Confidence Summary

| Process | Tier | Confidence | Key Strength |
|---------|------|------------|--------------|
| Circulatio | 2 | HIGH | 5/5 hazard match, complete doctrine alignment |
| Cohobatio | 2 | HIGH | 5/5 hazard match, accumulating investment |
| Athanor | 3 | MODERATE | Extreme restart intolerance compensates partial hazard |
| Quintessence | 3 | MODERATE | Multi-pass subset of eliminated class |

---

*Generated: 2026-01-05*
