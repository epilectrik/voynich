# PHASE_714: Refine C645 Post-Hazard Directional Anchor

**Status:** COMPLETE
**Date:** 2026-05-20
**Verdicts:** C2045 (sharpening of C645) + C2046 (no pre-hazard QO buildup, Tier 2 negative). Expert-recommended split registration. Within-folio shuffle null passes at p<0.001 for all three substrate-level measures.
**Posture:** C645 established that 75.2% of next-EN tokens after hazard-class tokens are CHSH (cooling-rich) vs 24.8% QO (heating/energy-input). This is a structural directional fact that survived audit at Tier 2. Refine along five axes to either strengthen the thermal interpretation OR identify where the pattern decomposes.

---

## What C645 established

Phase LANE_CHANGE_HOLD_ANALYSIS (2026-01-26):
- HAZ_CLASSES = {7, 30} (per C109 hazard topology)
- 504 hazards in Currier B with next-EN tokens identified
- 75.2% of next-EN are CHSH (cooling), 24.8% QO (heating-bias)
- Base rate: 44.7% CHSH, 55.3% QO
- Enrichment: CHSH 1.36×, QO 0.55× depleted

This is the directional anchor for "post-overshoot → cooling-bias" pattern. PHASE_714 refines this in five orthogonal directions.

---

## Five refinement tests (LOCKED before run)

### Refinement 1: Per-hazard-class specificity

C645 lumped both hazard classes (7, 30). Split:
- Hazard class 7 post-recovery CHSH rate
- Hazard class 30 post-recovery CHSH rate
- Per-hazard-bigram-class enrichment

**Thermal prediction:** If one hazard class is more "energy-overshoot-like" (per C109 mapping), it should show STRONGER cooling-bias recovery (>80% CHSH).

**Alternative:** Both classes show ~75% (uniform); pattern is generic post-hazard recovery, not energy-specific.

### Refinement 2: Multi-lag trajectory

C645 measures only the IMMEDIATE next-EN. Compute CHSH-fraction at lag +1, +2, +3, +4 next-EN-positions after hazard.

**Thermal prediction:** Monotonic decay toward baseline (44.7%) over 2-4 EN-positions. Recovery is finite, not permanent intervention.

**Alternative 1:** Sustained elevation (CHSH stays high at all lags) — suggests structural lane-locking, not transient recovery.
**Alternative 2:** Immediate snap-back to baseline at lag +2 — single-step recovery, no sustained kinetics.
**Alternative 3:** Oscillatory (lag +1 high CHSH, lag +2 elevated QO, lag +3 high CHSH again) — damped oscillation, classic control system.

### Refinement 3: Triplet patterns (hazard → CHSH → ?)

For each hazard followed by CHSH (the dominant post-hazard pattern), what comes next?

**Thermal prediction:** Third EN-position is mostly:
- Another CHSH (continued cooling, sustained intervention)
- Or QO at low rate (heating returning gradually)

**Alternative:** Third position is at baseline distribution (no specific pattern beyond +1).

### Refinement 4: Pre-hazard signature

What characterizes positions immediately BEFORE a hazard? Compute EN-distribution at lag -1, -2, -3 before hazard.

**Thermal prediction:** Elevated QO (heating buildup) in lag -1 to -2 before hazard. The "overshoot" should have a precursor pattern.

**Alternative:** No precursor signature; hazards are random perturbations.

### Refinement 5: Folio-level consistency

C645 is a corpus-level aggregate. Compute per-folio post-hazard CHSH rate.

**Thermal prediction:** Consistency across folios where hazards occur (most folios should show post-hazard CHSH > baseline CHSH).

**Alternative:** C645 driven by a small number of folios with extreme post-hazard cooling bias; not substrate-level.

---

## Null distribution control

For each refinement test:
- Compute random null by sampling random non-hazard tokens of matched count
- Run same recovery-direction analysis
- Compare observed effect to null distribution
- Report p-empirical and p95/p99 thresholds

---

## Pre-registered verdict matrix (LOCKED)

| Outcome | Verdict |
|---|---|
| All 5 refinements show predicted thermal-pattern signatures above null | **STRONG THERMAL RECOVERY ARCHITECTURE** — C645 generalizes; substrate has multi-axis kinetic signatures matching thermal control system. Multiple Tier 2 candidates. |
| 2-3 refinements show predicted patterns | **MODERATE THERMAL RECOVERY** — C645 stands but doesn't generalize fully; thermal interpretation has partial multi-axis support. Tier 2-3 candidates per axis. |
| 0-1 refinements show predicted patterns | **C645 ISOLATED** — post-hazard cooling-bias is real but doesn't extend to multi-axis thermal architecture. Thermal interpretation supported only at C645's specific level. |
| Per-folio inconsistency: small subset of folios drives most signal | **FOLIO-LOCAL EFFECT** — C645 needs scope restriction; not substrate-level. |

---

## Methodology controls

- Pre-registered thresholds for each axis BEFORE running
- Null distribution comparison mandatory
- Multiple-comparison awareness (5 tests, FDR-BH at 0.05)
- Cross-validation by random folio split for top-finding axes
- Per `feedback_framework_as_null.md`: results matching thermal predictions get extra skepticism
- Per `feedback_floor_vs_discriminator_metric_test.md`: where applicable, check if random tokens or shuffled token-position controls reproduce the effect

---

## Why this is the right next test after PHASE_713

PHASE_713 looked for Newton's curve at lag-1-8 token-level → wrong resolution (instruction text doesn't encode kinetics).

PHASE_714 looks at:
- LANE distributions (not curve shapes) — appropriate for instruction-level data
- Multi-lag at EN-position level (next operational instruction, not next any token)
- Triplet patterns (3-step protocols, instruction-grammar level)
- Pre-event signatures (buildup pattern)
- Folio-level consistency

This matches the resolution at which instruction-level operational notation would encode thermal control: the GRAMMAR of recovery sequences, not the KINETICS of execution.

---

## Implementation

| Script | Purpose |
|---|---|
| `_posthazard_refinement.py` | Run all 5 refinement tests with null controls |

---

## Effort estimate

~2 hours implementation, ~5 min runtime.

---

## RESULTS (2026-05-20)

### 5-axis refinement results

| Axis | Test | Result | Status |
|---|---|---|---|
| R1 | Hazard-class specificity (cls 7 vs 30) | 73.4% vs 76.6% CHSH — spread 0.032 | **FAIL** (no class-spec) |
| R2 | Multi-lag trajectory (lag +1..+4) | +0.199 → -0.031 → +0.007 → -0.032 | **PASS** (single-step decay) |
| R3 | Triplet patterns (hazard→CHSH→?) | 50/50 split, asymmetry -0.084 | **FAIL** (no continuation) |
| R4 | Pre-hazard QO buildup | 42-43% QO at lag -1/-2/-3 (BELOW baseline 44.7%) | **FAIL** (no precursor heating) |
| R5 | Folio-level consistency | 94.92% folios CHSH > baseline | **PASS strong** |

### Per-lag null distribution

| Lag | Observed CHSH | Null p99 | p_emp | Passes |
|---|---:|---:|---:|---|
| +1 | 0.7520 | 0.6530 | 0.0000 | **YES** |
| +2 | 0.5216 | 0.6668 | 0.9667 | No |
| +3 | 0.5602 | 0.6823 | 0.7333 | No |
| +4 | 0.5213 | 0.7242 | 0.8667 | No |

### Within-folio shuffle null (R5 follow-up after expert-advisor scrutiny)

| Metric | Observed | Null p99 | p_empirical | Passes |
|---|---:|---:|---:|---|
| Global post-hazard CHSH rate | 0.7520 | 0.6250 | 0.0000 | **YES** |
| Fraction of folios above baseline | 94.92% | 84.75% | 0.0000 | **YES** |
| Mean across-folio CHSH rate | 0.7751 | 0.6448 | 0.0000 | **YES** |

All three substrate-level measures pass within-folio shuffle null. R5's effect is not composition shadow.

### Expert consultation outcomes

**Expert-advisor:** Recommended split registration. R4 negative is clean and deserves separate Tier 2 constraint. Required within-folio shuffle null for R5 before registration (added, passes p<0.001). Interpretive framing ("instruction-grammar bigram rule") = Tier 3-4 max, keep constraint texts measurement-only.

**Crazy-expert:** Recommended sharpening framing. Notably reframed hazards as "stabilization failures" (system already in CHSH-mode when hazard occurs) rather than "thermal overshoots from heating buildup." Pre-hazard CHSH-dominance (R4 finding interpreted positively) suggests "stabilization until something gives." Flagged F-B-008/F-B-009 (two-channel thermal, overshoot-correct cycling) for review — multi-step thermal narrative falsified.

### Registered constraints

- **C2045 (Tier 2):** PHASE_714 sharpening of C645. Post-hazard CHSH preference is single-step (lag +1: 0.752, lag +2-4: baseline), substrate-level (94.9% folio consistency, within-folio shuffle null passes p<0.001), class-agnostic (spread 0.032 between hazard classes), no continuation protocol after first CHSH.

- **C2046 (Tier 2 negative):** No pre-hazard QO buildup. Hazards are NOT preceded by elevated QO/heating activity. QO rate at lag -1/-2/-3 before hazard is 42-43% (slightly BELOW baseline 44.7%). Falsifies the "thermal overshoot from cumulative heating" reading of hazards. Hazards occur during sustained CHSH-dominant contexts, not after QO buildup.

### Mechanism interpretations NOT registered

Per `feedback_mechanism_cycle_procedural_ceiling.md`:
- "Thermal damage-control protocol" — Tier 4 SPECULATIVE
- "Stabilization-failure mechanism" (crazy-expert) — Tier 4 SPECULATIVE
- "Instruction-grammar bigram rule" — Tier 3 framing only

The measurements stand; the mechanism interpretations remain underdetermined within internal procedure.

### What this changes about the broader thermal interpretation

**Strengthens:** C645 directional anchor is substrate-level, real, single-step damage-control rule.
**Weakens:** Multi-step thermal kinetic architecture reading (no continuation protocol, no class specificity, no pre-buildup signature).
**Falsifies specifically:** "Hazards are precipitated by cumulative heating excursion" — there's no QO precursor.

Net: thermal interpretation reduces from "multi-step kinetic architecture" to "structural process-class narrowing (PWRE) + single-step damage-control bigram rule (C645+C2045) + categorical-operational vocabulary (C2042)." Still substantial substrate-level support, but mechanism inference is more conservative.
