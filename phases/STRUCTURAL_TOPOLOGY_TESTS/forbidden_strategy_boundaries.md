# Test 2: Forbidden Strategy Boundaries

**Question:** Are there programs where certain strategies are STRUCTURALLY IMPOSSIBLE, not just disfavored?

**Verdict:** CATEGORICAL_BOUNDARY - AGGRESSIVE strategy is completely forbidden for 17 programs (20.5%)

---

## Background

### Correlation vs Prohibition

C488 shows correlations between HT density and strategy viability:
- CAUTIOUS: r=+0.46 (p < 0.0001)
- AGGRESSIVE: r=-0.43 (p < 0.0001)
- OPPORTUNISTIC: r=-0.48 (p < 0.0001)

But correlation ≠ prohibition. Historical sources (Brunschwig, Geber) documented that 4th degree fire was explicitly **FORBIDDEN**, not just inadvisable.

**Test Question:** Is there a categorical boundary where AGGRESSIVE becomes impossible?

---

## Findings

### 1. CONSERVATIVE_WAITING Archetype: AGGRESSIVE = 0%

From operator_strategies.json:

| Archetype | Count | CAUTIOUS | AGGRESSIVE | OPPORTUNISTIC |
|-----------|-------|----------|------------|---------------|
| MIXED | 50 | 0.39 | 0.36 | 0.29 |
| CONSERVATIVE_WAITING | **17** | 0.45 | **0.00** | 0.21 |
| ENERGY_INTENSIVE | 10 | 0.03 | 0.63 | 0.80 |
| AGGRESSIVE_INTERVENTION | 6 | 0.17 | 0.67 | 0.67 |

**Key Finding:** 17 programs (20.5% of 83 B folios) have AGGRESSIVE compatibility = 0.000

This is not a low score - it is **categorical exclusion**.

### 2. What Defines the Boundary?

The classification thresholds from operator_strategies.json:

| Metric | Low Threshold | High Threshold |
|--------|---------------|----------------|
| link_density | 0.342 | **0.404** |
| intervention_frequency | 4.85 | 6.50 |
| hazard_density | 0.561 | 0.609 |

**Pattern Identified:** Programs with `link_density > 0.404` are categorically AGGRESSIVE-forbidden.

### 3. Characterization of Forbidden Programs

From OPS-1 signature data, CONSERVATIVE_WAITING programs share:

| Property | Value | Interpretation |
|----------|-------|----------------|
| link_density | > 0.404 | High monitoring/waiting |
| waiting_profile | HIGH/EXTREME | Extended waiting phases |
| intervention_style | CONSERVATIVE | Minimal active intervention |
| hazard_density | Lower end | Fewer hazard events |

**Sample Programs (CONSERVATIVE_WAITING archetype):**

| Folio | link_density | waiting_profile | intervention_style |
|-------|--------------|-----------------|-------------------|
| f105r | 0.516 | EXTREME | CONSERVATIVE |
| f105v | 0.531 | EXTREME | CONSERVATIVE |
| f48r | 0.557 | EXTREME | CONSERVATIVE |
| f48v | 0.490 | HIGH | CONSERVATIVE |
| f26v | 0.490 | HIGH | CONSERVATIVE |
| f113v | 0.456 | HIGH | CONSERVATIVE |
| f115v | 0.480 | HIGH | CONSERVATIVE |

### 4. The Boundary is Categorical, Not Gradient

**Evidence for categorical boundary:**

1. **Zero compatibility:** Not 0.01 or 0.05 - literally 0.000
2. **Sharp threshold:** link_density > 0.404 is the cutoff
3. **Consistent archetype:** All 17 folios share the same profile
4. **No intermediate values:** No "almost forbidden" state

**This matches the historical "4th degree" pattern:**
- 1st-3rd degrees: varying levels of appropriateness
- 4th degree: **FORBIDDEN** (not just inadvisable)

### 5. Why is AGGRESSIVE Forbidden for These Programs?

**Structural interpretation:**

CONSERVATIVE_WAITING programs have:
- High link_density → Extended monitoring/waiting phases
- Low hazard_density → Fewer hazard events to manage
- Conservative intervention → Minimal active manipulation

AGGRESSIVE strategy requires:
- Minimal waiting (low link_density)
- Fast throughput (high intervention)
- Risk tolerance (accepting hazard exposure)

**These are structurally incompatible.**

Attempting AGGRESSIVE operation on a CONSERVATIVE_WAITING program would:
- Skip required monitoring phases
- Rush through waiting-dependent processes
- Cause phase-ordering violations

The grammar itself encodes the prohibition.

---

## Statistical Verification

### Chi-Square Test: Archetype × AGGRESSIVE Viability

| Group | AGGRESSIVE > 0 | AGGRESSIVE = 0 | Total |
|-------|----------------|----------------|-------|
| Non-CONSERVATIVE_WAITING | 66 | 0 | 66 |
| CONSERVATIVE_WAITING | 0 | 17 | 17 |
| Total | 66 | 17 | 83 |

Chi-square = 83.0, p < 0.0001

**Perfect separation:** Zero overlap between groups.

### Correlation vs Prohibition

| Relationship | Nature | Evidence |
|--------------|--------|----------|
| HT vs AGGRESSIVE | Continuous correlation | r=-0.43 |
| Archetype vs AGGRESSIVE | **Categorical prohibition** | 17/17 = 0% |

The gradient (correlation) and the boundary (prohibition) are **independent findings**.

---

## Connection to Historical Sources

### Brunschwig's 4th Degree Fire

| Degree | Description | Voynich Parallel |
|--------|-------------|------------------|
| 1st | Gentle (balneum Mariae) | CAUTIOUS strategy |
| 2nd | Moderate direct heat | Balanced operation |
| 3rd | Strong heat | AGGRESSIVE strategy |
| 4th | "Coercion" - **FORBIDDEN** | CONSERVATIVE_WAITING exclusion |

### Geber's Irreversibility Warning

> "For your repentance will never be of avail."

The categorical boundary ensures that operators cannot attempt AGGRESSIVE strategy on programs that structurally forbid it. The prohibition is **grammatically encoded**, not just advisable.

---

## Conclusion

**Test 2 Verdict: CATEGORICAL_BOUNDARY**

1. **17 programs (20.5%) have AGGRESSIVE = 0%** - categorical exclusion
2. **link_density > 0.404 defines the boundary** - sharp threshold
3. **Perfect separation** - no intermediate states
4. **Matches historical "4th degree" pattern** - forbidden, not just inadvisable

**Tier 3 Hypothesis Generated:**
> Programs with high link_density (>0.404) represent processes where aggressive intervention is structurally impossible, not merely inadvisable. The grammar encodes operational prohibitions directly.

---

## Potential New Constraint

**C490: Categorical Strategy Prohibition (Proposed)**

- **Scope:** B
- **Tier:** 3
- **Statement:** 20.5% of B programs (CONSERVATIVE_WAITING archetype) categorically exclude AGGRESSIVE strategy (compatibility = 0.000). The boundary is defined by link_density > 0.404.
- **Evidence:** 17/17 folios with perfect exclusion; chi-square p < 0.0001
- **Related:** C488 (HT strategy prediction), C458 (design clamp)

---

## Data Sources

- `results/operator_strategies.json` - Archetype classification and viability matrix
- `phases/OPS1_folio_control_signatures/ops1_folio_signature_table.csv` - Per-folio metrics
- Historical: Brunschwig, Geber on degrees of fire and prohibition
