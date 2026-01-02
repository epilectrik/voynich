# Program-Plant Correlation Table

> **PURPOSE**: Cross-tabulate program behavior with plant morphology.
> **METHOD**: Contingency tables with observed vs expected counts.

---

## Combined Data Table

| Folio | Primary Morphology | Aggressiveness | LINK Class | Hazard | Duration |
|-------|-------------------|----------------|------------|--------|----------|
| f26r | ROOT_HEAVY | MODERATE | MODERATE | MEDIUM | REGULAR |
| f26v | ROOT_HEAVY | CONSERVATIVE | HEAVY | LOW | REGULAR |
| f31r | ROOT_HEAVY | **AGGRESSIVE** | SPARSE | HIGH | REGULAR |
| f31v | COMPOSITE | CONSERVATIVE | HEAVY | MEDIUM | REGULAR |
| f33r | FLOWER_DOMINANT | **AGGRESSIVE** | MODERATE | MEDIUM | REGULAR |
| f33v | LEAFY_HERB | **AGGRESSIVE** | MODERATE | MEDIUM | REGULAR |
| f34r | ROOT_HEAVY | MODERATE | MODERATE | MEDIUM | REGULAR |
| f34v | WOODY_SHRUB | MODERATE | MODERATE | MEDIUM | REGULAR |
| f39r | ROOT_HEAVY | **AGGRESSIVE** | MODERATE | MEDIUM | EXTENDED |
| f39v | FLOWER_DOMINANT | MODERATE | MODERATE | MEDIUM | EXTENDED |
| f40r | FLOWER_DOMINANT | MODERATE | MODERATE | MEDIUM | REGULAR |
| f40v | FLOWER_DOMINANT | CONSERVATIVE | MODERATE | MEDIUM | REGULAR |
| f41r | LEAFY_HERB | MODERATE | MODERATE | MEDIUM | REGULAR |
| f41v | ROOT_HEAVY | CONSERVATIVE | HEAVY | LOW | REGULAR |
| f43r | ROOT_HEAVY | MODERATE | MODERATE | MEDIUM | EXTENDED |
| f43v | COMPOSITE | CONSERVATIVE | MODERATE | MEDIUM | EXTENDED |
| f46r | LEAFY_HERB | **AGGRESSIVE** | MODERATE | MEDIUM | EXTENDED |
| f46v | FLOWER_DOMINANT | MODERATE | MODERATE | MEDIUM | EXTENDED |
| f48r | LEAFY_HERB | CONSERVATIVE | HEAVY | LOW | REGULAR |
| f48v | LEAFY_HERB | CONSERVATIVE | HEAVY | LOW | REGULAR |
| f50r | FLOWER_DOMINANT | CONSERVATIVE | HEAVY | MEDIUM | REGULAR |
| f50v | FLOWER_DOMINANT | CONSERVATIVE | MODERATE | MEDIUM | REGULAR |
| f55r | LEAFY_HERB | **AGGRESSIVE** | MODERATE | MEDIUM | REGULAR |
| f55v | ROOT_HEAVY | MODERATE | MODERATE | LOW | REGULAR |

---

## Contingency Table 1: Aggressiveness × Primary Morphology

|                    | AGGRESSIVE | MODERATE | CONSERVATIVE | Total |
|--------------------|------------|----------|--------------|-------|
| **ROOT_HEAVY**     | 2          | 4        | 2            | 8     |
| **FLOWER_DOMINANT**| 1          | 3        | 3            | 7     |
| **LEAFY_HERB**     | 3          | 1        | 2            | 6     |
| **OTHER**          | 0          | 2        | 1            | 3     |
| **Total**          | 6          | 10       | 8            | 24    |

### Expected Values (if no association)

|                    | AGGRESSIVE | MODERATE | CONSERVATIVE |
|--------------------|------------|----------|--------------|
| **ROOT_HEAVY**     | 2.00       | 3.33     | 2.67         |
| **FLOWER_DOMINANT**| 1.75       | 2.92     | 2.33         |
| **LEAFY_HERB**     | 1.50       | 2.50     | 2.00         |
| **OTHER**          | 0.75       | 1.25     | 1.00         |

### Deviation from Expected

|                    | AGGRESSIVE | MODERATE | CONSERVATIVE |
|--------------------|------------|----------|--------------|
| **ROOT_HEAVY**     | **0.00**   | +0.67    | -0.67        |
| **FLOWER_DOMINANT**| -0.75      | +0.08    | +0.67        |
| **LEAFY_HERB**     | +1.50      | -1.50    | 0.00         |
| **OTHER**          | -0.75      | +0.75    | 0.00         |

---

## Contingency Table 2: LINK Class × Primary Morphology

|                    | SPARSE | MODERATE | HEAVY | Total |
|--------------------|--------|----------|-------|-------|
| **ROOT_HEAVY**     | 1      | 5        | 2     | 8     |
| **FLOWER_DOMINANT**| 0      | 6        | 1     | 7     |
| **LEAFY_HERB**     | 0      | 4        | 2     | 6     |
| **OTHER**          | 0      | 2        | 1     | 3     |
| **Total**          | 1      | 17       | 6     | 24    |

---

## Specific Hypothesis Tests

### H1: AGGRESSIVE programs align with ROOT_HEAVY morphology

| Condition | Count |
|-----------|-------|
| AGGRESSIVE programs | 6/24 (25.0%) |
| ROOT_HEAVY primary | 8/24 (33.3%) |
| Both AGGRESSIVE + ROOT_HEAVY | **2** |
| Expected by chance | 2.00 |
| **Ratio (Obs/Exp)** | **1.00** |

**Verdict**: NO ENRICHMENT. Exactly as expected by chance.

---

### H2: CONSERVATIVE/LINK_HEAVY programs align with FLOWER_DOMINANT

| Condition | Count |
|-----------|-------|
| CONSERVATIVE programs | 8/24 (33.3%) |
| FLOWER_DOMINANT primary | 7/24 (29.2%) |
| Both CONSERVATIVE + FLOWER_DOMINANT | **3** |
| Expected by chance | 2.62 |
| **Ratio (Obs/Exp)** | **1.14** |

**Verdict**: SLIGHT enrichment but not significant (p=1.00 Fisher's exact).

---

### H3: LINK_HEAVY programs align with delicate (FLOWER) morphology

| Condition | Count |
|-----------|-------|
| LINK_HEAVY programs | 6/24 (25.0%) |
| FLOWER_DOMINANT primary | 7/24 (29.2%) |
| Both LINK_HEAVY + FLOWER_DOMINANT | **1** |
| Expected by chance | 1.75 |
| **Ratio (Obs/Exp)** | **0.57** |

**Verdict**: DEPLETION (fewer than expected). Opposite of hypothesis.

---

## Summary of All Tested Combinations

| Combination | Observed | Expected | Ratio | Direction |
|-------------|----------|----------|-------|-----------|
| AGGRESSIVE + ROOT_HEAVY | 2 | 2.00 | 1.00 | NEUTRAL |
| AGGRESSIVE + FLOWER_DOMINANT | 1 | 1.75 | 0.57 | DEPLETION |
| CONSERVATIVE + FLOWER_DOMINANT | 3 | 2.62 | 1.14 | SLIGHT ENRICHMENT |
| LINK_HEAVY + FLOWER_DOMINANT | 1 | 1.75 | 0.57 | DEPLETION |
| LINK_HEAVY + ROOT_HEAVY | 2 | 2.00 | 1.00 | NEUTRAL |
| EXTENDED + ROOT_HEAVY | 2 | 2.00 | 1.00 | NEUTRAL |

---

## Key Pattern Observations

1. **No systematic enrichment**: All ratios between 0.57 and 1.14
2. **Most combinations near 1.0**: Indicating independence
3. **LEAFY_HERB + AGGRESSIVE slightly elevated** (3 vs 1.5 expected)
4. **FLOWER_DOMINANT + AGGRESSIVE depleted** (1 vs 1.75 expected)
5. **But none reach statistical significance**

---

*Correlation table generated from independent morphology and program classifications.*
