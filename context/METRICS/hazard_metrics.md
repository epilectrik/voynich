# Hazard Metrics

**Status:** CLOSED | **Tier:** 0-2

---

## Forbidden Transitions

| Metric | Value | Tier | Constraint |
|--------|-------|------|------------|
| Total forbidden | 17 | 0 | C109 |
| Failure classes | 5 | 0 | C109 |
| Asymmetric | 65% | 2 | C111 |
| Distant from kernel | 59% | 2 | C112 |

---

## 5 Failure Classes

| Class | Count | % | Constraint |
|-------|-------|---|------------|
| PHASE_ORDERING | 7 | 41% | C110 |
| COMPOSITION_JUMP | 4 | 24% | C109 |
| CONTAINMENT_TIMING | 4 | 24% | C109 |
| RATE_MISMATCH | 1 | 6% | C109 |
| ENERGY_OVERSHOOT | 1 | 6% | C109 |

Note: CONTAINMENT_TIMING has 0 corpus impact (theoretical-only).

---

## Hybrid Hazard Model (C216)

| Type | % | LINK Nearby | Severity |
|------|---|-------------|----------|
| Batch-focused | 71% | 1.229 | 0.733 |
| Apparatus-focused | 29% | 0 | 0.800 |

Apparatus hazards require faster response (no waiting allowed).

---

## Hazard Avoidance

| Metric | Value | Constraint |
|--------|-------|------------|
| HT hazard proximity | 4.84 (vs 2.5 expected) | C169 |
| HT at forbidden seams | 0/35 | C166 |
| True HT near hazards | 0 (vs 4,510 at random) | C217 |
| Hazards at line-initial | 0.20x (5x depleted) | C400 |
| Hazards at folio-initial | 0/82 | C400 |

---

## Escape Routes

| Metric | Value | Constraint |
|--------|-------|------------|
| qo-prefix escape rate | 25-47% | C397 |
| ENERGY_OPERATOR as escape | 40-67% | C398 |
| CORE_CONTROL as escape | 22-32% | C398 |
| Safe precedence (ENERGY_OP) | 33-67% | C399 |

---

## Suppressed Transitions

| Metric | Value | Constraint |
|--------|-------|------------|
| Beyond forbidden | 8 suppressed (<0.5x) | C386 |
| All in KERNEL-HEAVY cluster | YES | C386 |
| h→k observed | 0 | C332 |
| Self-transition enrichment | 3.76x average | C388 |

---

## Navigation

← [grammar_metrics.md](grammar_metrics.md) | [link_metrics.md](link_metrics.md) →
