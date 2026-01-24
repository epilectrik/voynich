# Brunschwig Prep Action → Grammar Posture Divergence Test

**Phase:** PREP_POSTURE_DIVERGENCE
**Date:** 2026-01-22
**Status:** IN PROGRESS

## Objective

Test whether Brunschwig recipes with different prep verb profiles show systematically different **grammar posture metrics** - NOT whether prep actions map to specific instruction classes.

## The Critical Distinction

| WRONG Question | RIGHT Question |
|----------------|----------------|
| "Which AUXILIARY class corresponds to CHOP?" | "Do CHOP-heavy recipes show different grammar postures than GATHER-heavy recipes?" |

**Why the original was wrong:**
- C131 (23.8% role consistency) pre-falsifies action-to-class mapping
- C171 (closed-loop) forbids treating GATHER/CHOP/POUND as discrete batch actions
- C396 (AUXILIARY invariance) - some subclasses are REGIME-invariant, cannot encode regime-varying verbs

**Why posture metrics are allowed:**
- Continuous measurements, not categorical class assignment
- Aggregate behavioral signatures, not 1:1 mappings
- Consistent with control manifold interpretation in BCSC

## Theoretical Framework

From F-BRU-007 (Constraint Substitution Model):
> "When operations are dangerous, grammar restricts options. When forgiving, grammar permits many options."

**Predictions:**
- CHOP (high-risk, precise) → constrained grammar posture (lower escape, higher infrastructure)
- GATHER (low-risk, flexible) → permissive grammar posture (higher escape, broader zone affinity)
- WASH (contamination control) → lower hazard adjacency

**Key constraint:**
- C458: Hazard exposure is CLAMPED (CV=0.11), recovery is FREE (CV=0.82)
- Expect larger effects in recovery metrics than hazard metrics

## Metrics

| Metric | Description | Expected Effect Range |
|--------|-------------|----------------------|
| `prefix_entropy` | Diversity of PREFIX distribution | Recovery (high) |
| `kernel_proximity` | Mean distance to k/h/e operators | Hazard (low) |
| `infrastructure_density` | AUXILIARY class density | Recovery (high) |
| `link_density` | LINK operator frequency | Recovery (high) |
| `escape_frequency` | e_ESCAPE operator rate | Recovery (high) |
| `sli` | Sensory Load Index (hazard/(escape+link)) | Hazard (low) |
| `zone_affinity` | C/P/R/S distribution | Recovery (high) |

## Constraint Compliance

| Constraint | How This Test Complies |
|------------|------------------------|
| C171 | Posture metrics are continuous, not batch actions |
| C131 | No class-to-verb mapping attempted |
| C396 | Aggregate metrics, not individual class tracking |
| C458 | Interpret effect sizes against clamp/free baseline |
| C469 | Using continuous metrics, not categories |
