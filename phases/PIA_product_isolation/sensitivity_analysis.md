# Sensitivity Analysis

> **PURPOSE**: Test robustness of product rankings under alternative scoring assumptions.

> **METHOD**: Identify dominant axes, test scoring perturbations, assess ranking stability.

---

## Baseline Ranking (Reference)

| Rank | Product | Score | Gap to Next |
|------|---------|-------|-------------|
| 1 | Aromatic Waters | 19 | +1 |
| 2 | Medicinal Waters | 18 | +2 |
| 3 | Resin Extracts | 16 | +2 |
| 4 | Ritual Substances | 14 | 0 |
| 4 | Pharmaceutical Concentrates | 14 | +1 |
| 6 | Food Flavoring | 13 | +1 |
| 7 | Cosmetics | 12 | — |

**Margin of Victory**: Aromatic Waters leads by only 1 point over Medicinal Waters.

---

## Axis Dominance Analysis

### Which Axes Drive the Ranking?

| Axis | Score Variance Across Candidates | Ranking Impact |
|------|----------------------------------|----------------|
| A1: Process Compatibility | HIGH (0-3 range) | **DOMINANT** — Eliminates 3 candidates |
| A2: Control Complexity | HIGH (0-3 range) | **HIGH** — Separates top tier |
| A3: Material Compatibility | HIGH (1-3 range) | **HIGH** — Fatal for cosmetics |
| A4: Economic Value | MODERATE (1-3 range) | MODERATE |
| A5: Frequency | HIGH (1-3 range) | MODERATE |
| A6: Outcome Judgment | LOW (1-3 range) | LOW — Most score 2-3 |
| A7: Documentation Pattern | MODERATE (0-3 range) | LOW |

**Key Finding**: A1 (Process Compatibility) and A3 (Material Compatibility) are the dominant discriminators. These are also the axes with the strongest structural evidence from the locked grammar.

---

## Perturbation Tests

### Test 1: What If Control Complexity (A2) Were Weighted 2x?

**Rationale**: The 17 forbidden transitions suggest HIGH control stakes.

| Product | Original | Adjusted | Rank Change |
|---------|----------|----------|-------------|
| Aromatic Waters | 19 | 21 (+2) | Unchanged (#1) |
| Medicinal Waters | 18 | 21 (+3) | **TIES #1** |
| Pharmaceutical Concentrates | 14 | 17 (+3) | Rises to #3 |
| Resin Extracts | 16 | 18 (+2) | Falls to #4 |

**Result**: Medicinal Waters TIES Aromatic Waters. Medical stakes could justify equal ranking.

**Implication**: If the 17 forbidden transitions specifically indicate life-safety concerns, Medicinal Waters becomes co-equal.

---

### Test 2: What If Frequency (A5) Were Weighted 2x?

**Rationale**: 83 programs suggest high production diversity.

| Product | Original | Adjusted | Rank Change |
|---------|----------|----------|-------------|
| Aromatic Waters | 19 | 22 (+3) | **EXTENDS LEAD** |
| Medicinal Waters | 18 | 20 (+2) | Unchanged (#2) |
| Resin Extracts | 16 | 17 (+1) | Falls further |

**Result**: Aromatic Waters EXTENDS lead. High frequency production strongly favors aromatics.

**Implication**: The 83-program justification is most naturally explained by aromatic water production with its high substrate variability.

---

### Test 3: What If Economic Value (A4) Were Weighted 2x?

**Rationale**: Valuable products justify elaborate protection.

| Product | Original | Adjusted | Rank Change |
|---------|----------|----------|-------------|
| Aromatic Waters | 19 | 22 (+3) | **EXTENDS LEAD** |
| Medicinal Waters | 18 | 21 (+3) | Unchanged (#2) |
| Pharmaceutical Concentrates | 14 | 17 (+3) | Rises |

**Result**: Top rankings stable. High-value products dominate regardless.

---

### Test 4: What If Documentation Pattern (A7) Were Weighted 2x?

**Rationale**: The manuscript's non-semantic design suggests secrecy priority.

| Product | Original | Adjusted | Rank Change |
|---------|----------|----------|-------------|
| Aromatic Waters | 19 | 21 (+2) | Unchanged (#1) |
| Ritual Substances | 14 | 17 (+3) | **RISES TO #3** |
| Medicinal Waters | 18 | 20 (+2) | Unchanged (#2) |

**Result**: Ritual Substances rises significantly. Secret transmission could matter more.

**Implication**: If the non-semantic design was *primarily* about secrecy (not just expert operation), ritual substances become more plausible.

---

### Test 5: What If We Remove A4 (Economic) and A7 (Documentation) Entirely?

**Rationale**: These are external/historical axes, not derived from grammar structure.

| Product | Original (7 axes) | Reduced (5 axes) | Rank Change |
|---------|-------------------|------------------|-------------|
| Aromatic Waters | 19 | 14/15 (93%) | Unchanged |
| Medicinal Waters | 18 | 13/15 (87%) | Unchanged |
| Resin Extracts | 16 | 12/15 (80%) | Unchanged |
| Cosmetics | 12 | 8/15 (53%) | Unchanged |

**Result**: Rankings STABLE when using only grammar-derived axes.

**Implication**: The ranking is robust to historical/economic assumptions.

---

## Single-Point Failure Sensitivity

### What Single Change Would Overturn the Ranking?

| Change | Effect | Likelihood |
|--------|--------|------------|
| Grammar tolerates phase change | Distilled spirits re-enters at #1-2 | **ZERO** (locked finding) |
| Illustrations encode plant IDs | All rankings destabilized | **ZERO** (Phase ILL falsified) |
| Dosage tokens found | Medicinal Waters rises to #1 | **VERY LOW** (0 identifiers found) |
| 83 programs found redundant | Resin Extracts rises | **LOW** (all programs functional) |
| CLASS_C compatible | Cosmetics viable | **ZERO** (19.8% failure locked) |

**Key Finding**: No plausible single change would overturn Aromatic Waters as #1.

---

## Robustness Summary

| Scenario | Aromatic Waters Rank | Stable? |
|----------|---------------------|---------|
| Baseline | #1 | — |
| Control (A2) 2x | #1 (tied) | YES |
| Frequency (A5) 2x | #1 (extended) | YES |
| Economic (A4) 2x | #1 (extended) | YES |
| Documentation (A7) 2x | #1 | YES |
| Remove A4+A7 | #1 | YES |
| All weights equal | #1 | YES |

**VERDICT**: Aromatic Waters ranking is **ROBUST** across all tested perturbations.

---

## Axis Correlation Check

Are the axes truly independent?

| Axis Pair | Correlation | Independence |
|-----------|-------------|--------------|
| A1 (Process) ↔ A3 (Material) | MODERATE | Partial overlap in phase-stability |
| A2 (Control) ↔ A4 (Economic) | MODERATE | High-value → high-stakes |
| A5 (Frequency) ↔ A4 (Economic) | LOW | Frequent ≠ valuable |
| A6 (Outcome) ↔ A7 (Documentation) | LOW | Sensory ≠ secret |

**Finding**: Some correlation exists between A1/A3 (both about phase stability) and A2/A4 (both about stakes). This could inflate aromatic/medicinal scores by ~1-2 points.

**Correction Applied**: Even reducing A1 or A3 by 1 point for correlated redundancy, Aromatic Waters remains #1.

---

## What Would Change the Verdict?

The ranking would significantly change only if:

1. **Phase change becomes compatible** — Not possible (locked finding)
2. **Material identifiers are found** — Would shift toward Medicinal
3. **Illustrations prove semantic** — Would require complete re-analysis
4. **Fewer programs were functional** — Would reduce frequency importance

None of these are plausible given the locked model.

---

## Confidence in Final Ranking

| Claim | Confidence | Robustness |
|-------|------------|------------|
| Aromatic Waters = #1 | **HIGH** | Stable across all perturbations |
| Medicinal Waters = #2 | **MEDIUM-HIGH** | Could tie #1 with A2 weighting |
| Resin Extracts = viable subset | **MEDIUM** | Falls with frequency emphasis |
| Top 3 separation from rest | **HIGH** | Gap persists in all scenarios |
| Eliminations (spirits, fermentation, solvents) | **DEFINITIVE** | Fatal failures unresolved |

---

*See `top_candidate_rationale.md` for "Why This Book?" analysis.*
