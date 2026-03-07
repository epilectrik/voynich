# C1566: Line Position Q3-Q4 Step Discontinuity

**Tier:** 2
**Scope:** B, line, position, gradient, quintile, closure, step, discontinuity, specification, work-zone, C1425, C1426, C1427, C1428, C1429, C1430, C1434, C1463
**Phase:** ATOM_ARCHITECTURE_CLEANUP (Phase 549)
**Date:** 2026-03-06

## Claim

Line interior (Q1-Q2-Q3) is compositionally homogeneous at atom resolution (adjacent quintile JSD < 0.003). Closure at Q3->Q4 is a discrete step: HEAD JSD jumps 26x (from 0.0007 at Q2->Q3 to 0.0185 at Q3->Q4) and TERMINAL JSD jumps 20x (from 0.0010 to 0.0200). Specification at Q0->Q1 is milder (HEAD JSD=0.0097). Refines C1425-C1430's three-zone model: at atom resolution, the line is a TWO-STEP architecture (specification shift + closure break) with a uniform work zone spanning Q1-Q3. The closure boundary is sharper than the specification boundary -- closure is a discrete event while specification is a gentler transition.

## Evidence

### Adjacent-quintile JSD

| Transition | HEAD JSD | TERM JSD |
|---|---|---|
| Q0->Q1 | 0.0097 | 0.0023 |
| Q1->Q2 | 0.0027 | 0.0013 |
| Q2->Q3 | **0.0007** | **0.0010** |
| Q3->Q4 | **0.0185** | **0.0200** |

### Step discontinuity ratios

| Ratio | Value |
|---|---|
| HEAD: (Q3->Q4) / (Q2->Q3) | **26.4x** |
| TERM: (Q3->Q4) / (Q2->Q3) | **20.0x** |
| HEAD: (Q0->Q1) / (Q1->Q2) | 3.6x |

### Full Q0-Q4 JSD

| Slot | Q0-Q4 JSD |
|---|---|
| HEAD | 0.0347 |
| TERMINAL | 0.0285 |

### What drives Q3->Q4

| HEAD | Q3 | Q4 | Shift |
|---|---|---|---|
| e | 29.8% | 19.5% | -10.3pp |
| HEADLESS | 25.5% | 36.1% | +10.6pp |
| a | 15.2% | 19.2% | +4.0pp |

| Terminal | Q3 | Q4 | Shift |
|---|---|---|---|
| m | 0.63% | 6.03% | +5.4pp (9.6x jump) |
| bare | 43.0% | 39.1% | -3.9pp |

The Q4 shift is dominated by: e-HEAD collapsing, headless/a-HEAD surging, and m-terminal appearing as closure valve (C1434).

## Interpretation

The three-zone model (SPECIFICATION / THERMAL_WORK / CLOSURE) from C1425-C1430 is better described at atom resolution as a TWO-STEP model:

1. **Mild specification shift** (Q0->Q1): e-HEAD starts high, k-HEAD rises to Q1 peak
2. **Uniform work zone** (Q1-Q2-Q3): stable composition, JSD < 0.003 between adjacent quintiles
3. **Sharp closure break** (Q3->Q4): discrete compositional event, JSD 20-26x larger than interior transitions

The asymmetry (closure sharper than specification) aligns with:
- C1434-C1439: m-terminal as active closure valve (not gradual decline)
- C1463-C1466: line safety architecture routing hazard to line-final
- C1427: line-final transition profile (TRANSITION enriched at Q4)

Opening a line is a soft transition (gradually shifting from specification to thermal work). Closing a line is a hard transition (abruptly shifting from work to closure).

## Falsification Criteria

1. If the step discontinuity disappears under line-length normalization
2. If the Q1-Q3 homogeneity breaks down in specific sections or REGIMEs
3. If the 26x HEAD JSD ratio is a binning artifact (e.g., quintile boundary placement effects)

## Source

`phases/ATOM_ARCHITECTURE_CLEANUP/results/atom_cleanup.json`
