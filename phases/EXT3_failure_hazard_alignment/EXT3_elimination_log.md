# EXT-3 Elimination Log

**Phase:** EXT-3 (Failure & Hazard Alignment)
**Date:** 2026-01-05
**Purpose:** Explicit documentation of processes eliminated for failing OPS hazard/restart criteria

---

## Elimination Criteria (Applied Strictly)

A process is **ELIMINATED** if any of the following are true:

1. **Hazard Mismatch:** Fewer than 3/5 STRONG OPS hazard class matches
2. **Restart Tolerance:** Historical practice tolerated restart (economically, mechanically, or psychologically)
3. **Operator Burden Mismatch:** Process can be operated without continuous expert vigilance
4. **Doctrine Violation:** Fails ≥2 OPS doctrine principles (P1-P5)

---

## Eliminated Processes

### 1. BALNEUM MARIAE (Water Bath Digestion)

| Attribute | Assessment |
|-----------|------------|
| EXT-2 Parent | Digestio (Class D) |
| OPS Hazard Match | 1/5 STRONG (WEAK) |
| Restart Tolerance | TOLERATED |
| Status | **ELIMINATED** |

#### Elimination Rationale

**Primary Reason: Hazard Mismatch**

The water bath fails to produce OPS-compatible failure modes:

| OPS Hazard | Balneum Mariae | Why Mismatch |
|------------|----------------|--------------|
| PHASE_ORDERING | ❌ NO MATCH | No vapor/liquid phase positioning |
| COMPOSITION_JUMP | ⚠️ PARTIAL | Contamination possible but recoverable |
| CONTAINMENT_TIMING | ✅ STRONG | Seal failure matters |
| RATE_MISMATCH | ❌ NO MATCH | Inherently slow process, rate irrelevant |
| ENERGY_OVERSHOOT | ⚠️ PARTIAL | **Water limits temperature to 100°C** |

**Critical Structural Incompatibility:** The water bath self-limits temperature. Energy overshoot—a core OPS hazard class—is physically impossible. Water cannot exceed 100°C at atmospheric pressure. This removes the primary failure mode that defines expert operation.

**Secondary Reason: Restart Tolerance**

| Factor | Assessment |
|--------|------------|
| Recovery possible | YES - can add water if bath boils down |
| Temperature adjustment | YES - remove from heat source |
| Restart with fresh materials | EASY |
| Historical emphasis | Gentle, forgiving method |

**Doctrine Failures:**

| Principle | Balneum Mariae | Verdict |
|-----------|----------------|---------|
| P2: Escalation irreversible | NO - temperature can be reduced | ❌ FAIL |
| P3: Restart requires low engagement | NO - restart easy | ❌ FAIL |

**Verdict:** ELIMINATED for hazard mismatch (1/5 STRONG), restart tolerance, and P2/P3 doctrine failures.

---

### 2. FIMUS EQUINUS (Horse Dung Digestion)

| Attribute | Assessment |
|-----------|------------|
| EXT-2 Parent | Digestio (Class D) |
| OPS Hazard Match | 0/5 STRONG (NO MATCH) |
| Restart Tolerance | FULLY TOLERATED |
| Status | **ELIMINATED** |

#### Elimination Rationale

**Primary Reason: Complete Hazard Failure**

Horse dung digestion produces ZERO OPS-compatible failure modes:

| OPS Hazard | Fimus Equinus | Why Mismatch |
|------------|---------------|--------------|
| PHASE_ORDERING | ❌ NO MATCH | No vapor/liquid dynamics |
| COMPOSITION_JUMP | ⚠️ PARTIAL | Environmental contamination possible |
| CONTAINMENT_TIMING | ⚠️ PARTIAL | Seal matters but not critical |
| RATE_MISMATCH | ❌ NO MATCH | Inherently slow, rate irrelevant |
| ENERGY_OVERSHOOT | ❌ **IMPOSSIBLE** | Dung cannot exceed 40-50°C |

**Critical Structural Incompatibility:** Horse dung cannot overheat. The primary energy overshoot hazard is physically impossible. The temperature range (40-50°C) is determined by microbial fermentation, not operator control. The operator cannot cause thermal damage regardless of action.

**Secondary Reason: Trivial Restart**

| Factor | Assessment |
|--------|------------|
| Restart materials | FREE (horse dung is waste) |
| Restart difficulty | TRIVIAL |
| Economic cost | NONE |
| Historical purpose | Convenience method |

**Doctrine Failures:**

| Principle | Fimus Equinus | Verdict |
|-----------|---------------|---------|
| P2: Escalation irreversible | NO - cannot overheat | ❌ FAIL |
| P3: Restart requires low engagement | NO - restart trivial | ❌ FAIL |
| P5: Throughput transient | N/A - no throughput concept | ❌ FAIL |

**Verdict:** ELIMINATED for complete hazard failure (0/5 STRONG), trivial restart, and multiple doctrine failures. This is a convenience method, not a precision process requiring expert control.

---

### 3. HYDRODISTILLATION (Commercial Aromatic Water Extraction)

| Attribute | Assessment |
|-----------|------------|
| EXT-2 Parent | Hydrodistillation (Class C) |
| OPS Hazard Match | 4/5 STRONG |
| Restart Tolerance | TOLERATED (commercial context) |
| Status | **ELIMINATED** |

#### Elimination Rationale

**Primary Reason: Restart Tolerance at Commercial Scale**

While process-level failures are irreversible (thermal degradation, volatile loss), the dominant historical practice tolerated restart:

| Historical Evidence | Assessment |
|---------------------|------------|
| Damascus rose water production | Commercial scale, batch failures expected |
| Brunschwig's methods | Production-oriented, systematic |
| Material availability | Rose petals harvested seasonally in quantity |
| Economic model | Throughput-valued production |

**Evidence of Commercial Production:**

> "By the ninth century the Arabs had discovered how to distil rose water." Damascus manuscripts from the 13th century show multi-unit production plants.

> Brunschwig's *Liber de arte distillandi* (1500) describes systematic production methods suitable for commercial application.

At production scale, individual batch failures were economically tolerable. Fresh materials were abundant during harvest season.

**Secondary Reason: Doctrine Failures (P3, P5)**

| Principle | Hydrodistillation (Commercial) | Verdict |
|-----------|-------------------------------|---------|
| P3: Restart requires low engagement | NO - restart easy with fresh materials | ❌ FAIL |
| P5: Throughput transient | **NO - commercial production values throughput** | ❌ FAIL |

**P5 Failure (Critical):** The OPS doctrine states "Throughput Is Transient" (speed is borrowed, not owned). Commercial aromatic water production explicitly valued throughput—maximizing yield during the harvest window was economically essential.

**Hazard Match (Strong, but Insufficient):**

The process-level hazard match is strong (4/5):
- Thermal degradation ↔ ENERGY_OVERSHOOT ✅
- Volatile loss ↔ PHASE_ORDERING ✅
- Contamination ↔ COMPOSITION_JUMP ✅
- Overflow ↔ CONTAINMENT_TIMING ✅

However, hazard match alone is insufficient. The restart and throughput criteria are eliminative.

**Note on Precious-Material Context:**

Non-commercial aromatic extraction with precious/scarce materials might survive (restart costly, quality-focused). However, this context is less well-documented historically than commercial production. The elimination applies to the dominant documented practice.

**Verdict:** ELIMINATED for P3 (restart tolerated), P5 (throughput valued). Hazard match is strong but insufficient to override restart/doctrine failures.

---

### 4. AQUA VITAE SIMPLEX (Simple Distilled Spirits)

| Attribute | Assessment |
|-----------|------------|
| EXT-2 Parent | Apothecary Distillation (Class I) |
| OPS Hazard Match | 4/5 STRONG |
| Restart Tolerance | TOLERATED |
| Status | **ELIMINATED** |

#### Elimination Rationale

**Primary Reason: Cheap Base Material**

| Factor | Assessment |
|--------|------------|
| Base material | Wine (abundant, relatively cheap) |
| Restart cost | LOW - fresh wine readily available |
| Historical availability | Wine production widespread in medieval Europe |
| Economic barrier | MINIMAL |

Unlike quintessence (requiring multiple passes), simple aqua vitae can be produced in a single distillation. Batch failure means losing one batch of wine, not accumulated refinement work.

**Secondary Reason: Standardization Pressure**

EXT-1 noted that Class I (Medical/pharmaceutical distillation) showed PARTIAL trap tolerance due to standardization:

> "Standardization introduced procedural elements for reproducibility"
> "Some rescue procedures exist for purity"

Taddeo Alderotti (1276) and Michele Savonarola (1440s) systematized aqua vitae production, introducing procedural elements that reduced expert burden.

**Doctrine Failures:**

| Principle | Aqua Vitae Simplex | Verdict |
|-----------|-------------------|---------|
| P3: Restart requires low engagement | NO - restart easy with cheap wine | ❌ FAIL |

**Hazard Match (Strong, but Insufficient):**

Process-level hazards are real (4/5 STRONG), but the economic context removes restart intolerance.

**Distinction from Quintessence:**

Quintessence (multiple-pass) SURVIVES because:
- Investment accumulates with each pass
- Seven-fold distillation means late failure is catastrophic
- Restart cost scales with completion percentage

Simple aqua vitae lacks this accumulating investment structure.

**Verdict:** ELIMINATED for P3 (restart tolerated with cheap base material). Standardization reduced expert burden.

---

## What Was NOT Eliminated

### EXT-2 Classes with Full Survivors

| EXT-1 Class | Surviving Processes | Eliminated Processes |
|-------------|---------------------|---------------------|
| A (Circulatio) | Circulatio (Tier 2) | None |
| B (Cohobatio) | Cohobatio (Tier 2) | None |
| D (Digestio) | Athanor (Tier 3) | Balneum Mariae, Fimus Equinus |
| I (Apothecary) | Quintessence (Tier 3) | Aqua Vitae Simplex |

### EXT-2 Classes Fully Eliminated

| EXT-1 Class | Eliminated Processes | Reason |
|-------------|---------------------|--------|
| C (Aromatic Extraction) | Hydrodistillation | P3, P5 fail at commercial scale |

**Note:** Class C elimination applies to the dominant documented practice (commercial production). The possibility of non-commercial aromatic extraction surviving is noted but undocumented.

---

## Elimination Summary

| Process | Primary Reason | Secondary Reason | Doctrine Failures |
|---------|----------------|------------------|-------------------|
| Balneum Mariae | Hazard mismatch (1/5) | Restart easy | P2, P3 |
| Fimus Equinus | No hazard match (0/5) | Restart trivial | P2, P3, P5 |
| Hydrodistillation | P3, P5 fail | Commercial scale | P3, P5 |
| Aqua Vitae Simplex | Cheap base material | Standardization | P3 |

---

## Statistical Summary

| Metric | Value |
|--------|-------|
| Processes analyzed | 8 |
| Processes eliminated | 4 |
| Elimination rate | **50%** |
| Surviving Tier 2 | 2 (Circulatio, Cohobatio) |
| Surviving Tier 3 | 2 (Athanor, Quintessence) |

---

## Key Discriminating Factors

### What Separates Survivors from Eliminated

1. **Energy Overshoot Capability:** Survivors can overheat; eliminated processes (balneum, fimus) cannot
2. **Accumulated Investment:** Survivors have investment that grows over time; eliminated processes have single-batch economics
3. **Restart Economics:** Survivors have costly restart (apparatus reset, multi-pass loss); eliminated have cheap restart (fresh materials available)
4. **Throughput Attitude:** Survivors devalue throughput; eliminated (hydrodistillation) value throughput

### The Critical Filter: Restart Tolerance

The strongest discriminator is **restart tolerance**. All eliminated processes share the property that historical practice tolerated starting over:

| Process | Restart Tolerance Mechanism |
|---------|----------------------------|
| Balneum Mariae | Water bath is forgiving |
| Fimus Equinus | Dung is free |
| Hydrodistillation | Materials seasonally abundant at commercial scale |
| Aqua Vitae Simplex | Wine is cheap |

All survivors share the property that restart is catastrophic:

| Process | Restart Catastrophe Mechanism |
|---------|------------------------------|
| Circulatio | Weeks of work lost |
| Cohobatio | Multi-pass investment destroyed |
| Athanor | Months of work lost |
| Quintessence | Seven-fold distillation investment lost |

---

*Generated: 2026-01-05*
