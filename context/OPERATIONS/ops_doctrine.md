# OPS Doctrine (OPS-1 through OPS-7)

**Status:** CLOSED | **Tier:** 2

---

## The 5 Core Principles

1. **Waiting is Default** (38% LINK)
2. **Escalation is Irreversible**
3. **Restart Requires Low-CEI**
4. **Text Holds Position, Not Escape Route**
5. **Throughput (REGIME_3) is Transient**

---

## OPS-1: Program Characterization

83 folios yield 33 operational metrics:

| Category | Metrics |
|----------|---------|
| Stability | MODERATE (55%), CONSERVATIVE (22%), AGGRESSIVE (18%), ULTRA_CONSERVATIVE (5%) |
| Waiting | LINK_MODERATE (47%), LINK_HEAVY (29%), LINK_SPARSE (17%) |
| Special | 3 RESTART_CAPABLE (f50v, f57r, f82v) |

---

## OPS-2: Regime Discovery

4 stable regimes identified (K-Means, Silhouette=0.23):

| Regime | Characteristics |
|--------|-----------------|
| REGIME_1 | Baseline operation |
| REGIME_2 | Lowest CEI |
| REGIME_3 | High throughput (all aggressive folios) |
| REGIME_4 | Elevated engagement |

**Ordering:** R2 < R1 < R4 < R3

---

## OPS-3: Pareto Efficiency

| Regime | Status |
|--------|--------|
| REGIME_1 | Pareto-efficient |
| REGIME_2 | Pareto-efficient |
| REGIME_3 | DOMINATED |
| REGIME_4 | Pareto-efficient |

REGIME_3 is transient throughput state, not sustainable.

---

## OPS-4: Restart Mechanics

- 3 restart-capable folios: f50v, f57r, f82v
- Restart folios have higher stability (0.589 vs 0.393)
- Restart positioned at low-CEI (d=2.24)

---

## OPS-5: Control Engagement Intensity

CEI manifold formalized:
- LINK-CEI correlation: r = -0.7057 (strong negative)
- More waiting = less active engagement
- 4 CEI bands correspond to 4 regimes

---

## OPS-6: Codex Organization

| Finding | Value |
|---------|-------|
| CEI smoothing | d=1.89 (reduces jumps) |
| Restart at low-CEI | d=2.24 |
| Navigation efficiency | WORSE than random (d=-7.33) |
| Codex organization | PARTIAL (2/5 tests pass) |

---

## OPS-7: Operator Model

**100% match:** EXPERT_REFERENCE archetype

| Property | Evidence |
|----------|----------|
| No definitions | Experts assumed |
| No remedial instruction | Knowledge prerequisite |
| Discrete procedures | Not continuous tuning |
| Positional markers | For interruption recovery |

---

## Why Conservatism Dominates (77%)

**Failures are irreversible:**

| Failure Type | Why No Recovery |
|--------------|-----------------|
| Phase disorder | Condensate mislocated |
| Contamination | Mixed impurities |
| Spillage | Material escaped |
| Scorching | Burned character |
| Flow chaos | Balance destroyed |

Cost of batch loss exceeds any time saved.

---

## Navigation

← [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md) | [program_taxonomy.md](program_taxonomy.md) →
