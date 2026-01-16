# Phase OPS-4: Pressure Envelope Report

**Date:** 2026-01-15

---

## 1. Regime Pressure Profiles

### REGIME_1

**N Folios:** 31

| Pressure | Mean | Std | Min | Max |
|----------|------|-----|-----|-----|
| Time | 0.678 | 0.151 | 0.411 | 0.984 |
| Risk | 0.608 | 0.096 | 0.415 | 0.873 |
| Stability | 0.601 | 0.094 | 0.292 | 0.812 |

**Stable Region (+/-1 std from mean):**
- Time: [0.527, 0.829]
- Risk: [0.512, 0.704]
- Stability: [0.506, 0.695]

**Instability Thresholds (+/-2 std):**
- Time: [0.375, 0.980]
- Risk: [0.416, 0.801]
- Stability: [0.412, 0.789]

**Dominant Exit Pressures:**
- high time -> gradient toward REGIME_2
- high time -> gradient toward REGIME_3
- high time -> gradient toward REGIME_4
- high risk -> gradient toward REGIME_2
- high risk -> gradient toward REGIME_4

---

### REGIME_2

**N Folios:** 11

| Pressure | Mean | Std | Min | Max |
|----------|------|-----|-----|-----|
| Time | 0.433 | 0.282 | 0.114 | 1.000 |
| Risk | 0.189 | 0.120 | 0.000 | 0.366 |
| Stability | 0.345 | 0.129 | 0.176 | 0.545 |

**Stable Region (+/-1 std from mean):**
- Time: [0.151, 0.715]
- Risk: [0.069, 0.309]
- Stability: [0.215, 0.474]

**Instability Thresholds (+/-2 std):**
- Time: [0.000, 0.997]
- Risk: [0.000, 0.428]
- Stability: [0.086, 0.604]

---

### REGIME_3

**N Folios:** 16

| Pressure | Mean | Std | Min | Max |
|----------|------|-----|-----|-----|
| Time | 0.278 | 0.238 | 0.025 | 0.980 |
| Risk | 0.692 | 0.116 | 0.557 | 1.000 |
| Stability | 0.736 | 0.097 | 0.609 | 1.000 |

**Stable Region (+/-1 std from mean):**
- Time: [0.040, 0.516]
- Risk: [0.576, 0.808]
- Stability: [0.640, 0.833]

**Instability Thresholds (+/-2 std):**
- Time: [0.000, 0.753]
- Risk: [0.460, 0.924]
- Stability: [0.543, 0.929]

**Dominant Exit Pressures:**
- high risk -> gradient toward REGIME_2
- high risk -> gradient toward REGIME_4
- high stability (instability) -> gradient toward REGIME_1
- high stability (instability) -> gradient toward REGIME_2
- high stability (instability) -> gradient toward REGIME_4

---

### REGIME_4

**N Folios:** 25

| Pressure | Mean | Std | Min | Max |
|----------|------|-----|-----|-----|
| Time | 0.140 | 0.094 | 0.000 | 0.328 |
| Risk | 0.409 | 0.088 | 0.248 | 0.561 |
| Stability | 0.483 | 0.160 | 0.000 | 0.641 |

**Stable Region (+/-1 std from mean):**
- Time: [0.046, 0.234]
- Risk: [0.320, 0.497]
- Stability: [0.322, 0.643]

**Instability Thresholds (+/-2 std):**
- Time: [0.000, 0.328]
- Risk: [0.232, 0.585]
- Stability: [0.162, 0.803]

---

## 2. Transition Pressure Gradients

| From | To | Weight | Inducing Conditions | Type |
|------|-----|--------|---------------------|------|
| REGIME_1 | REGIME_2 | 0.919 | time pressure relief (gradient=0.245); risk pressure relief (gradient=0.419) | pareto_tradeoff |
| REGIME_3 | REGIME_2 | 0.895 | risk pressure relief (gradient=0.503); stability pressure relief (gradient=0.392) | exit_dominated |
| REGIME_1 | REGIME_4 | 0.855 | time pressure relief (gradient=0.537); risk pressure relief (gradient=0.200) | pareto_tradeoff |
| REGIME_3 | REGIME_4 | 0.675 | time pressure relief (gradient=0.137); risk pressure relief (gradient=0.284) | exit_dominated |
| REGIME_1 | REGIME_3 | 0.400 | time pressure relief (gradient=0.400) | enter_dominated_transient |
| REGIME_4 | REGIME_2 | 0.357 | risk pressure relief (gradient=0.219); stability pressure relief (gradient=0.138) | pareto_tradeoff |
| REGIME_2 | REGIME_4 | 0.293 | time pressure relief (gradient=0.293) | pareto_tradeoff |
| REGIME_3 | REGIME_1 | 0.220 | risk pressure relief (gradient=0.084); stability pressure relief (gradient=0.136) | exit_dominated |
| REGIME_2 | REGIME_3 | 0.155 | time pressure relief (gradient=0.155) | enter_dominated_transient |

---

## 3. Prohibited Transitions

| From | To | Reason |
|------|-----|--------|
| REGIME_2 | REGIME_1 | worsens all three pressure axes |
| REGIME_4 | REGIME_1 | worsens all three pressure axes |
| REGIME_4 | REGIME_3 | worsens all three pressure axes |

---

*Generated: 2026-01-15T23:47:28.137936*