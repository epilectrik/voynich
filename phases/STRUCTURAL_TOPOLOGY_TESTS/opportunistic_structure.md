# Test 4: OPPORTUNISTIC Program Structure

**Question:** What structurally distinguishes programs that are OPPORTUNISTIC-viable ("skillful operator" programs)?

**Verdict:** JUDGMENT_AXIS_IDENTIFIED - OPPORTUNISTIC programs show high qo_density and recovery infrastructure

---

## Background

### Historical Parallel

Libavius documented three operator types:
- **Patient** - Waits for natural separation
- **Impatient** - Forces separation
- **Skillful** - "Knows WHEN to intervene"

OPPORTUNISTIC strategy (r=-0.48 with HT) may map to the "skillful" operator - adaptive, timing-sensitive, judgment-critical.

### Expert Hypothesis

> "Some programs are not tolerant or brittle - they are *judgment-critical*. That's a compelling new axis."

---

## Findings

### 1. OPPORTUNISTIC Viability by Archetype

| Archetype | Count | OPPORTUNISTIC Compatibility | Characterization |
|-----------|-------|------------------------------|------------------|
| ENERGY_INTENSIVE | 10 | **0.80** | Highest OPPORTUNISTIC |
| AGGRESSIVE_INTERVENTION | 6 | **0.67** | High OPPORTUNISTIC |
| MIXED | 50 | 0.29 | Moderate |
| CONSERVATIVE_WAITING | 17 | 0.21 | Lowest OPPORTUNISTIC |

**Pattern:** OPPORTUNISTIC viability inversely correlates with conservatism and directly correlates with energy-intensity.

### 2. Structural Signatures of OPPORTUNISTIC Programs

**From operator_strategies.json thresholds:**

| Metric | Low Threshold | High Threshold | OPPORTUNISTIC Association |
|--------|---------------|----------------|---------------------------|
| qo_density | 0.123 | **0.181** | High qo_density → OPPORTUNISTIC |
| recovery_ops_count | 8 | **19** | High recovery → OPPORTUNISTIC |
| hazard_density | 0.561 | 0.609 | Higher hazard → OPPORTUNISTIC |
| link_density | 0.342 | 0.404 | **Low** link → OPPORTUNISTIC |

**OPPORTUNISTIC programs have:**
- **High qo_density** (recovery/escape operators)
- **High recovery_ops_count** (escape infrastructure)
- **Lower link_density** (less waiting/monitoring)
- **Higher hazard tolerance** (operates in riskier regime)

### 3. ENERGY_INTENSIVE Archetype Profile

The highest-OPPORTUNISTIC archetype (ENERGY_INTENSIVE, 10 folios) has:

| Property | Value | Interpretation |
|----------|-------|----------------|
| CAUTIOUS compatibility | 0.03 | Almost zero |
| AGGRESSIVE compatibility | 0.63 | High |
| **OPPORTUNISTIC compatibility** | **0.80** | Highest |
| qo_density | High | Strong escape infrastructure |
| recovery_ops_count | High | Multiple recovery paths |
| intervention_style | Variable | Adaptive |

**Interpretation:** ENERGY_INTENSIVE programs are judgment-critical because:
1. They cannot use CAUTIOUS (0.03) - waiting doesn't work
2. They have AGGRESSIVE option (0.63) - can push hard
3. They excel at OPPORTUNISTIC (0.80) - best at adaptive timing

### 4. OPPORTUNISTIC vs CAUTIOUS: Structural Tradeoff

| Feature | CAUTIOUS-Optimal | OPPORTUNISTIC-Optimal |
|---------|------------------|----------------------|
| link_density | HIGH (>0.404) | LOW (<0.342) |
| qo_density | LOW | HIGH (>0.181) |
| recovery_ops | Fewer | Many (>19) |
| HT density | HIGH | LOW |
| Intervention style | Frequent stabilizing | Adaptive timing |

**The structural tradeoff:**
- CAUTIOUS programs need monitoring infrastructure (high LINK)
- OPPORTUNISTIC programs need escape infrastructure (high qo, recovery)

These are architecturally incompatible - you cannot have both maximal monitoring AND maximal escape infrastructure.

### 5. HT-OPPORTUNISTIC Anti-Correlation Explained

**HT vs OPPORTUNISTIC: r=-0.48 (p < 0.00001)**

Why negative correlation?

| Factor | HT Effect | OPPORTUNISTIC Effect |
|--------|-----------|---------------------|
| Monitoring | HT tracks attention | Low LINK needed |
| Escape | HT stops at hazards | High qo needed |
| Risk tolerance | HT avoids risk | Higher hazard tolerance |

**Interpretation:** HT density tracks attention/monitoring needs. OPPORTUNISTIC programs need less monitoring and more escape infrastructure. The negative correlation reflects structural incompatibility between "track everything" and "escape when needed."

### 6. The Judgment-Critical Axis

The expert's hypothesis is confirmed: OPPORTUNISTIC represents a distinct axis of program behavior.

| Axis | Low End | High End |
|------|---------|----------|
| **Caution** | AGGRESSIVE_INTERVENTION | CONSERVATIVE_WAITING |
| **Judgment** | CONSERVATIVE_WAITING | ENERGY_INTENSIVE |

ENERGY_INTENSIVE programs are:
- Not the most aggressive (AGGRESSIVE_INTERVENTION is more aggressive)
- Not the most cautious (CONSERVATIVE_WAITING is most cautious)
- **The most judgment-critical** (highest OPPORTUNISTIC)

This suggests a third operational mode beyond cautious/aggressive: **adaptive judgment**.

---

## Structural Definition of OPPORTUNISTIC-Viable Programs

Programs are OPPORTUNISTIC-viable when they have:

1. **High qo_density (>0.181)** - Strong escape operator presence
2. **High recovery_ops_count (>19)** - Multiple recovery pathways
3. **Low link_density (<0.342)** - Less monitoring infrastructure
4. **Higher hazard tolerance** - Can operate in riskier regime

This combination creates programs where:
- Constant monitoring is not required
- Escape/recovery is readily available
- Timing of intervention matters more than constant attention

---

## Connection to Historical Parallel

### Libavius's "Skillful Operator"

| Historical Concept | Voynich Structural Parallel |
|-------------------|----------------------------|
| "Knows WHEN to intervene" | High qo_density enables timed escapes |
| Neither patient nor impatient | Not CAUTIOUS, not purely AGGRESSIVE |
| Optimal balance | ENERGY_INTENSIVE archetype |
| Judgment required | Low HT (less tracking), more decision points |

The "skillful operator" is not simply in the middle of the caution spectrum - they operate in a structurally distinct mode characterized by escape infrastructure and adaptive timing.

---

## Conclusion

**Test 4 Verdict: JUDGMENT_AXIS_IDENTIFIED**

OPPORTUNISTIC programs are structurally distinguished by:

1. **High escape infrastructure** (qo_density, recovery_ops)
2. **Low monitoring infrastructure** (link_density)
3. **Higher hazard tolerance**
4. **Negative HT correlation** (less tracking, more decision)

This represents a third operational mode beyond cautious/aggressive: **adaptive judgment**.

**Tier 3 Hypothesis:**
> OPPORTUNISTIC viability tracks "judgment-critical" programs where timing matters more than constant monitoring. These programs have escape infrastructure (qo, recovery) instead of monitoring infrastructure (LINK, HT).

---

## Potential New Constraint

**C491: Judgment-Critical Program Axis (Proposed)**

- **Scope:** B
- **Tier:** 3
- **Statement:** OPPORTUNISTIC viability defines a structural axis independent of caution/aggression. High-OPPORTUNISTIC programs (ENERGY_INTENSIVE archetype) have high qo_density (>0.181), high recovery_ops (>19), and low link_density (<0.342).
- **Evidence:** ENERGY_INTENSIVE has 80% OPPORTUNISTIC compatibility vs 3% CAUTIOUS
- **Related:** C488 (HT strategy prediction), C490 (categorical prohibition)

---

## Data Sources

- `results/operator_strategies.json` - Archetype-strategy matrix
- `phases/OPS1_folio_control_signatures/ops1_folio_signature_table.csv` - Per-folio metrics
- Historical: Libavius on "skillful" operators
