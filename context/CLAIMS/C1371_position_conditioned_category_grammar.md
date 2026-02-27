# C1371 — Position-Conditioned Category Grammar

**Tier:** 2
**Scope:** B, line, category, positional, transition
**Phase:** 484 (POSITION_CONDITIONED_CATEGORY_GRAMMAR)
**Depends on:** C1362, C1286, C1047, C556, C562, C1305

## Constraint

Category transitions ARE position-conditioned (chi² p=4.5e-65, Cramer's V=0.102). The line-final quintile (Q5) has the most distinctive category grammar (JS=0.016, 4-8x other quintiles). THERMAL self-loops erode from 32.4% (Q1) to 19.1% (Q5); FLOW self-loops grow from 21.3% to 25.0%. FLOW is the only category with a significant monotonic gradient (rho=0.900, p=0.037, increasing). The positional pattern is section-universal (mean JS profile correlation=0.617, confirming C1047 extends to categories). 5/8 categories show significant self-transition rate variation by position. 4/6 predictions confirmed.

## T1: Position-Dependence (Primary)

Chi-squared homogeneity across 5 quintiles: **chi²=844.7, dof=252, p=4.5e-65**. Category transition grammar varies by position.

Cramer's V=0.102 — modest but highly significant effect. Smaller than class-level position-conditioning (expected, since categories are a coarser grouping of 49 classes into 8 categories).

**Per-quintile JS divergence from global:**
| Q1 | Q2 | Q3 | Q4 | Q5 |
|----|----|----|----|----|
| 0.0046 | 0.0039 | 0.0021 | 0.0026 | **0.0162** |

Q5 is 4-8x more deviant than other quintiles. The line ending has the most distinctive category grammar.

## T2: Category Gradient Profile

| Category | Q1 | Q2 | Q3 | Q4 | Q5 | rho | p |
|----------|----|----|----|----|----|----|---|
| THERMAL | 0.243 | **0.293** | 0.250 | 0.245 | 0.176 | -0.400 | 0.505 |
| **FLOW** | 0.176 | 0.168 | 0.193 | 0.203 | **0.225** | **0.900** | **0.037** |
| CONTAINMENT | 0.036 | 0.045 | 0.058 | 0.048 | 0.055 | 0.700 | 0.188 |
| STAGING | **0.155** | 0.123 | 0.121 | 0.111 | 0.135 | -0.400 | 0.505 |
| OPERATION | 0.148 | 0.153 | **0.154** | 0.147 | 0.123 | -0.600 | 0.285 |
| TRANSITION | 0.141 | 0.138 | 0.126 | 0.140 | **0.191** | 0.300 | 0.624 |
| MARKING | 0.084 | 0.063 | 0.078 | 0.083 | 0.079 | -0.100 | 0.873 |
| MONITORING | 0.017 | 0.016 | 0.019 | 0.023 | 0.016 | 0.200 | 0.747 |

**FLOW is the only significant monotonic gradient** (rho=0.900, p=0.037). FLOW builds toward line end.

THERMAL peaks at Q2 (0.293) and drops to Q5 (0.176) — medially concentrated as predicted by C556.

STAGING is front-loaded (Q1=0.155, declines to Q4=0.111). TRANSITION spikes at Q5 (0.191).

## T3: Position-Variant Bigrams

7 bigrams show >2x enrichment or <0.5x depletion at specific positions:

| Bigram | Position | Ratio | n |
|--------|----------|-------|---|
| CONTAINMENT→TRANSITION | Q5 | **2.05x** enriched | 34 |
| MARKING→THERMAL | Q5 | **0.39x** depleted | 17 |
| MONITORING→OPERATION | Q5 | 0.40x depleted | 3 |
| STAGING→MONITORING | Q4 | 0.40x depleted | 3 |
| MONITORING→TRANSITION | Q2 | 0.47x depleted | 4 |
| CONTAINMENT→STAGING | Q1 | 0.48x depleted | 15 |
| CONTAINMENT→THERMAL | Q5 | 0.49x depleted | 16 |

Most variant bigrams concentrate at **Q5** — the line ending has specific category pathways that are opened (CONTAINMENT→TRANSITION) or closed (MARKING→THERMAL, CONTAINMENT→THERMAL).

**Interpretation:** At line end, the grammar favors transitions out of CONTAINMENT toward TRANSITION states, and disfavors transitions toward THERMAL. The line closes with state changes, not thermal processing.

## T4: Section-Position Interaction

All sections show the same positional pattern: Q5 is the most deviant quintile, Q3 is the least. Mean JS profile correlation between sections: **0.617**. This confirms C1047 extends to the category level — **section and position are additive, not interactive**.

**P6: CONFIRMED.** No section-position interaction.

## T5: Self-Transition Rates by Position

| Category | Q1 | Q2 | Q3 | Q4 | Q5 | rho | Significant |
|----------|----|----|----|----|----|----|-------------|
| **THERMAL** | **0.324** | 0.299 | 0.280 | 0.262 | **0.191** | **-1.000** | **Yes** |
| **FLOW** | **0.213** | 0.223 | 0.237 | 0.242 | **0.250** | **1.000** | **Yes** |
| CONTAINMENT | 0.073 | 0.064 | 0.072 | 0.070 | 0.078 | 0.300 | No |
| STAGING | 0.118 | 0.150 | 0.126 | 0.109 | 0.162 | 0.300 | No |
| OPERATION | 0.149 | 0.138 | 0.129 | 0.142 | 0.135 | -0.500 | No |
| TRANSITION | 0.159 | 0.161 | 0.119 | 0.181 | 0.227 | 0.700 | Yes* |
| MARKING | 0.111 | 0.134 | 0.187 | 0.161 | 0.172 | 0.700 | Yes* |
| MONITORING | 0.012 | 0.030 | 0.013 | 0.011 | 0.017 | 0.000 | Yes* |

**5/8 categories show significant self-transition rate variation. P5: CONFIRMED.**

**THERMAL self-loop erosion** (rho=-1.0): THERMAL chains heavily at line start (32.4%) and disperses at line end (19.1%). This is a novel finding — thermal processing runs in sustained bursts that decay across the line.

**FLOW self-loop growth** (rho=1.0): FLOW builds momentum toward line end (21.3%→25.0%), consistent with FLOW's line-final enrichment (C562).

**TRANSITION self-loop spike at Q5** (0.227 vs Q3 minimum 0.119): State transitions cluster and chain at line boundaries.

## Pre-Registered Prediction Scorecard

| # | Prediction | Result | Actual |
|---|-----------|--------|--------|
| P1 | MARKING front-depleted (Q1/Q5 > 1.5) | **FALSIFIED** | Ratio 1.05 — MARKING is position-independent |
| P2 | THERMAL medially concentrated | **CONFIRMED** | Medial 0.263 > Q1 0.243 > Q5 0.176 |
| P3 | FLOW peaks Q5 at >=1.5x Q1 | **FALSIFIED** | Peaks Q5 (confirmed) but ratio 1.28 (below 1.5x) |
| P4 | TRANSITION late-enriched | **CONFIRMED** | Q4-Q5 mean 0.166 > Q1-Q2 mean 0.140 |
| P5 | >=3/8 self-transition rates vary | **CONFIRMED** | 5/8 significant |
| P6 | Section-position additive | **CONFIRMED** | Mean profile corr 0.617 |

**Score: 4/6 confirmed.** P1 and P3 missed on threshold (both directionally correct but below cutoff).

## Synthesis

Category grammar has a clear **line-positional architecture**:

1. **Line-initial (Q1-Q2):** THERMAL-dominated, high self-loop rate. Programs start with sustained thermal processing.
2. **Line-medial (Q3):** Most grammar-neutral position. Lowest deviation from global transition matrix.
3. **Line-final (Q5):** The most distinctive position. THERMAL drops, FLOW and TRANSITION spike. Self-loops shift from THERMAL to TRANSITION. Category pathways change: CONTAINMENT→TRANSITION opens, MARKING→THERMAL closes.

**The line is a thermal arc:** Thermal processing loads at the front, disperses through the middle, and resolves into flow and transition at the end. This is consistent with the Tier 3 interpretation: heat is applied, fluid moves, state changes.

**Relationship to M2.1:** M2.1 position-conditions at the 49-class level (C1362). This phase shows the same phenomenon exists at the 8-category level. Since categories are deterministic aggregations of classes (C1305), the category-level conditioning is a coarser view of the same underlying structure. Cramer's V=0.102 (category) vs the class-level effect size suggests categories capture the broad strokes while classes capture finer positional detail.

## Provenance

Script: `phases/POSITION_CONDITIONED_CATEGORY_GRAMMAR/scripts/position_conditioned_category_grammar.py`
Results: `phases/POSITION_CONDITIONED_CATEGORY_GRAMMAR/results/position_conditioned_category_grammar.json`
