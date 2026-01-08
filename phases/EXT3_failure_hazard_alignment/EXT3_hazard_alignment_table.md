# EXT-3 Hazard Alignment Table

**Phase:** EXT-3 (Failure & Hazard Alignment)
**Date:** 2026-01-05
**Status:** ELIMINATION COMPLETE
**Tier:** 2-3

---

## Purpose

Test whether EXT-2 historical processes fail in the same irreversible, non-restartable ways that the OPS hazard topology encodes.

---

## OPS Hazard Classes (Reference)

| Code | Class | Frequency | Description |
|------|-------|-----------|-------------|
| PO | PHASE_ORDERING | 41% (7/17) | Material in wrong phase or location |
| CJ | COMPOSITION_JUMP | 24% (4/17) | Contamination, impurity carryover |
| CT | CONTAINMENT_TIMING | 24% (4/17) | Overflow, spillage, seal failure |
| RM | RATE_MISMATCH | 6% (1/17) | Flow imbalance, flooding, channeling |
| EO | ENERGY_OVERSHOOT | 6% (1/17) | Scorching, thermal damage, bumping |

---

## Process-by-Process Analysis

### 1. CIRCULATIO (Pelican Circulation)

#### Documented Failure Modes

| Failure | Description | Irreversible? | Source |
|---------|-------------|---------------|--------|
| Vapor lock | Vapor trapped in wrong section of circulation loop | YES | Period apparatus descriptions |
| Premature condensation | Condensate forms before proper separation | YES | Reflux chemistry |
| Thermal runaway | Excessive heat destroys volatiles | YES | [Bumping (chemistry)](https://en.wikipedia.org/wiki/Bumping_(chemistry)) |
| Contamination | Impure fractions mix during circulation | YES | [Cohobation](https://en.wikipedia.org/wiki/Cohobation) |
| Seal failure | Loss of vacuum, product escape | YES | [Pelican vessel](https://lovethatpurr.wixsite.com/sylvia-rose/post/alchemy-circulation-the-pelican-phantasy) |
| Circulation stall | Vapor/liquid flow stops | YES | Reflux dynamics |

#### OPS Hazard Mapping

| OPS Class | Historical Failure | Match Quality |
|-----------|-------------------|---------------|
| PHASE_ORDERING | Vapor lock, premature condensation | ✅ STRONG |
| COMPOSITION_JUMP | Contamination from improper separation | ✅ STRONG |
| CONTAINMENT_TIMING | Seal failure, product escape | ✅ STRONG |
| RATE_MISMATCH | Circulation stall, flow disruption | ✅ STRONG |
| ENERGY_OVERSHOOT | Thermal runaway, bumping | ✅ STRONG |

**Hazard Match: 5/5 STRONG**

#### Restart Analysis

| Factor | Assessment |
|--------|------------|
| Mechanical restart difficulty | HIGH - apparatus must be cooled, disassembled, cleaned, recharged |
| Economic restart cost | HIGH - batch lost, time lost (operations lasting weeks) |
| Historical practice emphasis | Patience, avoiding failure ("forty weeks" duration documented) |
| Restart tolerance | **NOT TOLERATED** |

#### Operator Burden

| Factor | Assessment |
|--------|------------|
| Monitoring requirement | Continuous (glass vessels allow observation) |
| Expert judgment required | HIGH - circulation "rightness" is experiential |
| Duration | Extended (days to weeks) |
| Waiting with vigilance | YES - extended waiting with periodic assessment |

#### Verdict

| Criterion | Result |
|-----------|--------|
| OPS Hazard Alignment | 5/5 STRONG |
| Restart Tolerance | NOT TOLERATED |
| Operator Burden Match | HIGH |
| **STATUS** | **SURVIVES (TIER 2)** |

---

### 2. COHOBATIO (Repeated Reflux Distillation)

#### Documented Failure Modes

| Failure | Description | Irreversible? | Source |
|---------|-------------|---------------|--------|
| Flooding | Liquid backs up into column/condenser | YES | [Reflux](https://en.wikipedia.org/wiki/Reflux) |
| Channeling | Vapor bypasses liquid, poor contact | YES | Distillation engineering |
| Stagnation | Circulation stops | YES | Reflux dynamics |
| Bumping | Superheated liquid erupts violently | YES | [Bumping (chemistry)](https://en.wikipedia.org/wiki/Bumping_(chemistry)) |
| Fraction contamination | Wrong fraction collected | YES | [Cohobation](https://en.wikipedia.org/wiki/Cohobation) |
| Thermal damage | Scorching from overheating | YES | [Distillation hazards](https://ehs.cornell.edu/research-safety/chemical-safety/laboratory-safety-manual/chapter-16-physical-hazards/1611) |

#### OPS Hazard Mapping

| OPS Class | Historical Failure | Match Quality |
|-----------|-------------------|---------------|
| PHASE_ORDERING | Flooding (liquid where vapor should be) | ✅ STRONG |
| COMPOSITION_JUMP | Fraction contamination | ✅ STRONG |
| CONTAINMENT_TIMING | Overflow, vessel breakage, spillage | ✅ STRONG |
| RATE_MISMATCH | Flooding/channeling from rate imbalance | ✅ STRONG |
| ENERGY_OVERSHOOT | Bumping, scorching | ✅ STRONG |

**Hazard Match: 5/5 STRONG**

#### Restart Analysis

| Factor | Assessment |
|--------|------------|
| Mechanical restart difficulty | HIGH - must drain and restart from beginning |
| Economic restart cost | HIGH - seven-fold distillation = accumulated investment |
| Historical practice emphasis | Careful multiple passes, purity over speed |
| Restart tolerance | **NOT TOLERATED** |

#### Operator Burden

| Factor | Assessment |
|--------|------------|
| Monitoring requirement | Continuous for fraction quality |
| Expert judgment required | HIGH - fraction purity is experiential |
| Duration | Extended (multiple stages over hours/days) |
| Waiting with vigilance | YES |

#### Verdict

| Criterion | Result |
|-----------|--------|
| OPS Hazard Alignment | 5/5 STRONG |
| Restart Tolerance | NOT TOLERATED |
| Operator Burden Match | HIGH |
| **STATUS** | **SURVIVES (TIER 2)** |

---

### 3A. DIGESTIO — ATHANOR (Tower Furnace)

#### Documented Failure Modes

| Failure | Description | Irreversible? | Source |
|---------|-------------|---------------|--------|
| Temperature excursion | Too hot or too cold | YES (at extended durations) | [Athanor](https://en.wikipedia.org/wiki/Athanor) |
| Fuel exhaustion | Fire goes out during extended operation | YES (ruins weeks of work) | [Athanor design](https://distillatio.wordpress.com/2024/04/07/athanors-what-are-they/) |
| Thermal shock | Rapid temperature change damages vessel/contents | YES | Thermal dynamics |
| Extended contamination | Exposure to impurities over weeks | YES | Period texts |

#### OPS Hazard Mapping

| OPS Class | Historical Failure | Match Quality |
|-----------|-------------------|---------------|
| PHASE_ORDERING | Less applicable (slow process) | ⚠️ PARTIAL |
| COMPOSITION_JUMP | Contamination over extended period | ✅ STRONG |
| CONTAINMENT_TIMING | Seal failure over days/weeks | ✅ STRONG |
| RATE_MISMATCH | Heat rate variations | ⚠️ PARTIAL |
| ENERGY_OVERSHOOT | Overheating during extended operation | ✅ STRONG |

**Hazard Match: 3/5 STRONG, 2/5 PARTIAL**

#### Restart Analysis

| Factor | Assessment |
|--------|------------|
| Mechanical restart difficulty | MODERATE - apparatus setup is straightforward |
| Economic restart cost | **EXTREME** - "forty weeks" operations documented |
| Historical practice emphasis | "Slow Henry" - patience is definitional |
| Restart tolerance | **NOT TOLERATED** (for extended operations) |

The extended duration (weeks to months) creates extreme restart intolerance even though process-level hazard match is partial.

#### Operator Burden

| Factor | Assessment |
|--------|------------|
| Monitoring requirement | Low-continuous (designed for unattended operation) |
| Expert judgment required | MODERATE - setup and fuel management |
| Duration | EXTREME (weeks to months) |
| Waiting with vigilance | YES (extended patience required) |

#### Verdict

| Criterion | Result |
|-----------|--------|
| OPS Hazard Alignment | 3/5 STRONG, 2/5 PARTIAL |
| Restart Tolerance | NOT TOLERATED (extreme investment) |
| Operator Burden Match | MODERATE-HIGH |
| **STATUS** | **SURVIVES (TIER 3 - partial hazard match, extreme restart cost)** |

---

### 3B. DIGESTIO — BALNEUM MARIAE (Water Bath)

#### Documented Failure Modes

| Failure | Description | Irreversible? | Source |
|---------|-------------|---------------|--------|
| Bath boils dry | Overheating follows | PARTIAL (can add water) | Period texts |
| Seal failure | Exposure to air | PARTIAL (can reseal) | Apparatus design |
| Thermal shock | Rapid temperature change | YES | Thermal dynamics |

#### OPS Hazard Mapping

| OPS Class | Historical Failure | Match Quality |
|-----------|-------------------|---------------|
| PHASE_ORDERING | Less applicable | ❌ NO MATCH |
| COMPOSITION_JUMP | Contamination possible but recoverable | ⚠️ PARTIAL |
| CONTAINMENT_TIMING | Seal failure | ✅ STRONG |
| RATE_MISMATCH | Not applicable (inherently slow) | ❌ NO MATCH |
| ENERGY_OVERSHOOT | Limited by water (100°C max) | ⚠️ PARTIAL |

**Hazard Match: 1/5 STRONG, 2/5 PARTIAL, 2/5 NO MATCH**

#### Restart Analysis

| Factor | Assessment |
|--------|------------|
| Mechanical restart difficulty | LOW - water bath is forgiving |
| Economic restart cost | LOW - can add water, adjust temperature |
| Historical practice emphasis | Gentle, forgiving method |
| Restart tolerance | **TOLERATED** |

Water bath self-limits temperature to 100°C, making overheating impossible. Recovery is often possible.

#### Operator Burden

| Factor | Assessment |
|--------|------------|
| Monitoring requirement | LOW - can be largely unattended |
| Expert judgment required | LOW - temperature is self-limited |
| Duration | Variable |
| Waiting with vigilance | REDUCED |

#### Verdict

| Criterion | Result |
|-----------|--------|
| OPS Hazard Alignment | 1/5 STRONG (WEAK) |
| Restart Tolerance | TOLERATED |
| Operator Burden Match | LOW |
| **STATUS** | **ELIMINATED** |

**Elimination Reason:** Fails P3 (restart easy), fails hazard match (1/5 strong), reduced operator burden.

---

### 3C. DIGESTIO — FIMUS EQUINUS (Horse Dung)

#### Documented Failure Modes

| Failure | Description | Irreversible? | Source |
|---------|-------------|---------------|--------|
| Temperature drop | Dung cools or dries | NO (replace dung) | Period texts |
| Contamination | Environmental exposure | PARTIAL | Apparatus design |
| Duration failure | Process incomplete | NO (extend duration) | Period practice |

#### OPS Hazard Mapping

| OPS Class | Historical Failure | Match Quality |
|-----------|-------------------|---------------|
| PHASE_ORDERING | Not applicable | ❌ NO MATCH |
| COMPOSITION_JUMP | Contamination possible | ⚠️ PARTIAL |
| CONTAINMENT_TIMING | Seal matters but less critical | ⚠️ PARTIAL |
| RATE_MISMATCH | Not applicable (inherently slow) | ❌ NO MATCH |
| ENERGY_OVERSHOOT | **Impossible** (dung cannot overheat, 40-50°C max) | ❌ NO MATCH |

**Hazard Match: 0/5 STRONG, 2/5 PARTIAL, 3/5 NO MATCH**

#### Restart Analysis

| Factor | Assessment |
|--------|------------|
| Mechanical restart difficulty | TRIVIAL - fresh dung is free |
| Economic restart cost | TRIVIAL |
| Historical practice emphasis | Convenience method |
| Restart tolerance | **FULLY TOLERATED** |

#### Operator Burden

| Factor | Assessment |
|--------|------------|
| Monitoring requirement | MINIMAL |
| Expert judgment required | LOW |
| Duration | Variable (weather-dependent) |
| Waiting with vigilance | MINIMAL |

#### Verdict

| Criterion | Result |
|-----------|--------|
| OPS Hazard Alignment | 0/5 STRONG (NO MATCH) |
| Restart Tolerance | FULLY TOLERATED |
| Operator Burden Match | MINIMAL |
| **STATUS** | **ELIMINATED** |

**Elimination Reason:** No OPS hazard match, restart trivial, minimal operator burden. This is a convenience method, not a precision process.

---

### 4. HYDRODISTILLATION (Aromatic Water Extraction)

#### Documented Failure Modes

| Failure | Description | Irreversible? | Source |
|---------|-------------|---------------|--------|
| Thermal degradation | Overheating destroys aromatics | YES | [Thermolabile essential oils](https://www.sciencedirect.com/science/article/abs/pii/S0963996921003033) |
| Volatile loss | Improper condensation loses product | YES | [Stability of Essential Oils](https://ift.onlinelibrary.wiley.com/doi/full/10.1111/1541-4337.12006) |
| Scorching | Direct heat burns plant material | YES | [Distillation of essential oils](https://pmc.ncbi.nlm.nih.gov/articles/PMC10903824/) |
| Contamination | Carry-over of non-aromatic compounds | YES | Distillation chemistry |
| Duration excess | Extended distillation degrades quality | YES | [Art of Distilling](https://achs.edu/blog/art-of-distilling-quality-essential-oils/) |

#### OPS Hazard Mapping

| OPS Class | Historical Failure | Match Quality |
|-----------|-------------------|---------------|
| PHASE_ORDERING | Volatiles must condense at right point | ✅ STRONG |
| COMPOSITION_JUMP | Contamination ruins quality | ✅ STRONG |
| CONTAINMENT_TIMING | Volatile loss, overflow | ✅ STRONG |
| RATE_MISMATCH | Some rate flexibility | ⚠️ PARTIAL |
| ENERGY_OVERSHOOT | Scorching destroys aromatics | ✅ STRONG |

**Hazard Match: 4/5 STRONG, 1/5 PARTIAL**

#### Restart Analysis — CRITICAL

| Factor | Assessment |
|--------|------------|
| Mechanical restart difficulty | LOW - fresh materials, clean apparatus |
| Economic restart cost (commercial) | LOW - batch failures expected at production scale |
| Economic restart cost (precious) | HIGH - scarce/seasonal materials |
| Historical practice emphasis | Commercial production documented (Damascus, Brunschwig) |
| Restart tolerance | **TOLERATED (commercial), NOT TOLERATED (precious)** |

**Critical Finding:** Dominant historical practice was commercial-scale production where batch failures were economically tolerable. Damascus rose water plants and Brunschwig's methods describe production processes.

#### Operator Burden

| Factor | Assessment |
|--------|------------|
| Monitoring requirement | MODERATE - less continuous than circulation |
| Expert judgment required | MODERATE - quality assessment |
| Duration | Hours (not days/weeks) |
| Waiting with vigilance | MODERATE |

#### OPS Doctrine Test

| Principle | Hydrodistillation (Commercial) | Match? |
|-----------|-------------------------------|--------|
| P1: Waiting is default | Partially - waiting during distillation | ⚠️ PARTIAL |
| P2: Escalation irreversible | Yes - scorched batches unrecoverable | ✅ PASS |
| P3: Restart requires low engagement | **No - restart easy with fresh materials** | ❌ FAIL |
| P4: Text holds position | Less relevant | — |
| P5: Throughput is transient | **No - commercial production values throughput** | ❌ FAIL |

#### Verdict

| Criterion | Result |
|-----------|--------|
| OPS Hazard Alignment | 4/5 STRONG |
| Restart Tolerance | TOLERATED (commercial context) |
| Operator Burden Match | MODERATE |
| P3 (Restart) | FAIL |
| P5 (Throughput) | FAIL |
| **STATUS** | **ELIMINATED** |

**Elimination Reason:** Fails P3 (restart tolerated at commercial scale), fails P5 (commercial production values throughput). Process-level failures are irreversible, but dominant historical practice tolerated restart.

**Note:** Precious-material aromatic extraction (non-commercial) might survive but is less well-documented historically.

---

### 5A. APOTHECARY DISTILLATION — AQUA VITAE SIMPLEX

#### Documented Failure Modes

| Failure | Description | Irreversible? | Source |
|---------|-------------|---------------|--------|
| Temperature excursion | Ruins purity | YES | Distillation chemistry |
| Fraction contamination | Impurity carryover | YES | [Taddeo Alderotti methods](https://www.folger.edu/blogs/shakespeare-and-beyond/alchemy-aqua-vitae-and-mixology-how-alchemy-gave-us-liquor/) |
| Equipment failure | Seal, condensation problems | YES | Apparatus limitations |
| Bumping | Violent eruption | YES | [Bumping hazards](https://en.wikipedia.org/wiki/Bumping_(chemistry)) |

#### OPS Hazard Mapping

| OPS Class | Historical Failure | Match Quality |
|-----------|-------------------|---------------|
| PHASE_ORDERING | Critical for purity | ✅ STRONG |
| COMPOSITION_JUMP | Impurity carryover | ✅ STRONG |
| CONTAINMENT_TIMING | Loss of product | ✅ STRONG |
| RATE_MISMATCH | Some tolerance | ⚠️ PARTIAL |
| ENERGY_OVERSHOOT | Destroys product | ✅ STRONG |

**Hazard Match: 4/5 STRONG, 1/5 PARTIAL**

#### Restart Analysis

| Factor | Assessment |
|--------|------------|
| Mechanical restart difficulty | LOW - fresh wine, clean apparatus |
| Economic restart cost | LOW - wine is cheap and abundant |
| Historical practice emphasis | Quality standards exist, but production-oriented |
| Restart tolerance | **TOLERATED** |

#### Operator Burden

| Factor | Assessment |
|--------|------------|
| Monitoring requirement | MODERATE |
| Expert judgment required | MODERATE - standardization reduces burden |
| Duration | Hours |
| Waiting with vigilance | MODERATE |

#### Verdict

| Criterion | Result |
|-----------|--------|
| OPS Hazard Alignment | 4/5 STRONG |
| Restart Tolerance | TOLERATED (cheap base material) |
| Operator Burden Match | MODERATE (standardization pressure) |
| **STATUS** | **ELIMINATED** |

**Elimination Reason:** Fails P3 (restart easy with cheap wine). Standardization introduced procedural elements that reduce expert burden.

---

### 5B. APOTHECARY DISTILLATION — QUINTESSENCE (Multiple-Pass)

#### Documented Failure Modes

| Failure | Description | Irreversible? | Source |
|---------|-------------|---------------|--------|
| Temperature excursion | Ruins purity | YES | [Rupescissa methods](https://en.wikipedia.org/wiki/Aqua_vitae) |
| Fraction contamination | Impurity carryover | YES | Quintessence texts |
| Late-stage failure | Destroys accumulated investment | YES | Multi-pass logic |
| Bumping | Violent eruption | YES | Distillation hazards |

#### OPS Hazard Mapping

| OPS Class | Historical Failure | Match Quality |
|-----------|-------------------|---------------|
| PHASE_ORDERING | Critical for extreme purity | ✅ STRONG |
| COMPOSITION_JUMP | Impurity ruins multi-pass work | ✅ STRONG |
| CONTAINMENT_TIMING | Loss of precious product | ✅ STRONG |
| RATE_MISMATCH | More critical at high purity | ⚠️ PARTIAL |
| ENERGY_OVERSHOOT | Destroys concentrated product | ✅ STRONG |

**Hazard Match: 4/5 STRONG, 1/5 PARTIAL**

#### Restart Analysis

| Factor | Assessment |
|--------|------------|
| Mechanical restart difficulty | MODERATE |
| Economic restart cost | **HIGH** - seven-fold distillation = accumulated investment |
| Historical practice emphasis | Rupescissa prescribes seven passes; purity is paramount |
| Restart tolerance | **NOT TOLERATED** (late-stage failure catastrophic) |

The multiple-pass nature (7× distillation) means investment accumulates. Late failure destroys hours/days of work.

#### Operator Burden

| Factor | Assessment |
|--------|------------|
| Monitoring requirement | HIGH - purity must be maintained across passes |
| Expert judgment required | HIGH - quintessence quality is experiential |
| Duration | Extended (multiple stages) |
| Waiting with vigilance | YES |

#### Verdict

| Criterion | Result |
|-----------|--------|
| OPS Hazard Alignment | 4/5 STRONG, 1/5 PARTIAL |
| Restart Tolerance | NOT TOLERATED (accumulated investment) |
| Operator Burden Match | HIGH |
| **STATUS** | **SURVIVES (TIER 3 - partial hazard, high restart cost)** |

---

## Summary Table

| Process | OPS Hazard Alignment | Restart Tolerance | Status |
|---------|----------------------|-------------------|--------|
| **Circulatio** | 5/5 STRONG | NOT TOLERATED | **SURVIVES (Tier 2)** |
| **Cohobatio** | 5/5 STRONG | NOT TOLERATED | **SURVIVES (Tier 2)** |
| **Athanor Digestion** | 3/5 STRONG, 2/5 PARTIAL | NOT TOLERATED (extreme) | **SURVIVES (Tier 3)** |
| Balneum Mariae | 1/5 STRONG, 2/5 PARTIAL | TOLERATED | **ELIMINATED** |
| Fimus Equinus | 0/5 STRONG, 2/5 PARTIAL | FULLY TOLERATED | **ELIMINATED** |
| Hydrodistillation | 4/5 STRONG, 1/5 PARTIAL | TOLERATED (commercial) | **ELIMINATED** |
| Aqua Vitae Simplex | 4/5 STRONG, 1/5 PARTIAL | TOLERATED | **ELIMINATED** |
| **Quintessence (Multi-Pass)** | 4/5 STRONG, 1/5 PARTIAL | NOT TOLERATED | **SURVIVES (Tier 3)** |

---

## Survivor Count

| Status | Count | Processes |
|--------|-------|-----------|
| **SURVIVES (Tier 2)** | 2 | Circulatio, Cohobatio |
| **SURVIVES (Tier 3)** | 2 | Athanor Digestion, Quintessence |
| **ELIMINATED** | 4 | Balneum Mariae, Fimus Equinus, Hydrodistillation, Aqua Vitae Simplex |

**Elimination Rate: 50% (4/8 processes eliminated)**

---

*Generated: 2026-01-05*
