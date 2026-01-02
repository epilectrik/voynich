# PF-C (Continuous Conditioning-Like) vs Voynich Grammar

> **ADVERSARIAL TEST**: Finding where conditioning archetype fits POORLY

---

## Summary Metrics

| Metric | Value |
|--------|-------|
| Structural Coherence | 0.810 |
| Total Tensions | 2 |
| Unexplained Features | 6 |
| Strained Assumptions | 0 |

---

## Test A: Program Role Distribution

**Coherence Score**: 0.650

### Tensions
- 18.1% AGGRESSIVE programs - risky for pure maintenance

### Unexplained Features
- LINK_SPARSE programs (16.9%) suggest speed priority inconsistent with conditioning
- HIGH_INTERVENTION programs (12.0%) suggest active change rather than maintenance

---

## Test B: LINK Utilization

**Coherence Score**: 1.000

- Mean LINK density: 0.383
- Mean max consecutive LINK: 8.5

### Tensions

### Unexplained Features
- (None)

---

## Test C: Hazard Encoding

**Coherence Score**: 0.800

- Hazard density mean: 0.582
- Near-miss mean: 23.7
- All hazards bidirectional: True

### Tensions
- (None)

### Unexplained Features
- ENERGY_OVERSHOOT hazard class - conditioning doesn't typically risk energy runaway
- RATE_MISMATCH hazard class - conditioning doesn't have inherent rate requirements

---

## Test D: Absence of Endpoints

**Coherence Score**: 0.900

- Endpoint markers present: 0
- Archetype predicts endpoints: False
- Fit quality: **GOOD**

### Tensions
- (None — this is a **GOOD FIT**)

### Unexplained Features
- Program length range 2059 - pure maintenance should be uniform

---

## Test E: Recovery & Restart Programs

**Coherence Score**: 0.700

- Restart-capable programs: 3 (f50v, f57r, f82v)
- Mean recovery ops: 16.1

### Tensions
- 35 programs with >15 recovery ops - excessive for stable maintenance

### Unexplained Features
- f57r = RESTART_PROTOCOL - why would maintenance need a dedicated reset program?

---

## What PF-C Struggles to Explain

### Critical Mismatches

1. **Program diversity** — Pure maintenance should be uniform; 83 distinct programs exist
2. **LINK_SPARSE programs** — 16.9% have low waiting; maintenance should wait
3. **HIGH_INTERVENTION programs** — 12% suggest active change, not passive maintenance
4. **AGGRESSIVE programs** — 18% operate near hazard limits; risky for pure maintenance

### Awkward Fits

1. ENERGY_OVERSHOOT hazard class — conditioning doesn't typically risk energy runaway
2. RATE_MISMATCH hazard class — conditioning has no inherent rate requirements
3. f57r = RESTART_PROTOCOL — why would maintenance need a dedicated reset program?
4. Extended runs with high recovery ops — suggests instability, not steady maintenance

### Degree of Contrivance Required

To fit PF-C to this grammar requires assuming:
- 83 different "conditions" need 83 different maintenance protocols
- LINK_SPARSE programs handle "fast-equilibrating" conditions (ad hoc)
- AGGRESSIVE programs are for "critical" conditions requiring active intervention
- Hazard diversity reflects "multiple failure modes" of a complex system

**Contrivance level: MODERATE**