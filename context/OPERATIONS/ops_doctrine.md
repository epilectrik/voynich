# OPS Doctrine (OPS-1 through OPS-7)

**Status:** CLOSED | **Tier:** 2

> **[Withdrawn v7.24/7.25 — historical; see SYSTEM/STATUS_BRIEF.md §3]** This doctrine reads Currier B as a closed-loop control program operated by a human (waiting, escalation, restart, throughput, irreversible failure). That reading is now the Tier-3 working interpretation: closed-loop control is demoted (C171, Tier 3; all four legs withdrawn), LINK is a 13.2% morphological artifact of "ol" rather than a waiting/monitoring operator (C609, C1174), the hazard/failure layer is withdrawn (C783, C2060, C2081), and REGIME is a soft gradient rather than 4 crisp classes (C1712, C2070). The OPS rows C178–C198 remain Tier 2 in the generated table as folio-level metrics; read their operational vocabulary as the historical interpretation. Text kept for traceability.

---

## The 5 Core Principles

1. **Waiting is Default** (38% LINK) [withdrawn: the 38% figure is not reproducible — true LINK density is 13.2% (C609) — and LINK is a morphological artifact, not waiting (C1174)]
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

4 stable regimes identified (K-Means, Silhouette=0.23): [scoped by C1712/C2070 — silhouette selects k=2 (the Bio vs non-Bio section split); the k=4 excess over null is only +0.047; REGIME is a soft gradient, not 4 crisp classes, and REGIME effects need a within-section re-test]

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
- LINK-CEI correlation: r = -0.7057 (strong negative) — statistic stands (C190); the reading below is withdrawn (C1174)
- More waiting = less active engagement [historical interpretation: LINK is not waiting]
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

**[Withdrawn v7.24/7.25 — historical; see SYSTEM/STATUS_BRIEF.md §3]** The failure types below are the 5-class hazard taxonomy, which was imposed by keyword matching (C2060); the class-level forbidden transitions are demoted (C783) and the token-level zeros reduce to composition, zones and boundary coupling (C2081). No prohibition or failure layer remains (C2081).

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
