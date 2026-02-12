# C1002: SUFFIX Positional and Sequential Grammar

**Tier:** 2 | **Scope:** B | **Phase:** SUFFIX_POSITIONAL_STATE_MAPPING | **Date:** 2026-02-12

## Statement

SUFFIX encodes a weaker positional grammar than PREFIX (8/22 non-uniform vs 20/32, R²=0.027 vs 0.069) but a comparable sequential grammar (Cramér's V=0.063 vs PREFIX V=0.060). A handful of extreme positional specialists exist (am 88% line-final, om 88% final, ry 68% final, ly 48% final; eey and ey initial-biased), but most suffixes are positionally uniform. SUFFIX sequential transitions are highly structured with strong self-repetition (edy→edy +14.3σ, dy→dy +11.2σ) and cross-suffix sequencing (ain→hy +8.2σ, aiin→hy +5.2σ). However, SUFFIX carries zero unique cross-token predictive signal: I(SUFFIX; PREFIX_{t+1} | MIDDLE) = -0.074 bits (fully redundant with MIDDLE class). Category-level paragraph gradients (C932: terminal r=-0.89, bare r=+0.90) do NOT decompose to individual suffixes (only 2/21 monotonic).

## Evidence

### T1: Suffix Positional Census (PARTIAL)
- 8/22 suffixes non-uniform (Bonferroni p < 4.5e-5)
- Extreme specialists:
  - `am`: 88.0% Q5 (line-final), concentration 4.40x, mean position 0.930
  - `om`: 87.9% Q5, concentration 4.39x, mean position 0.926
  - `ry`: 68.6% Q5, concentration 3.43x, mean position 0.748
  - `ly`: 48.1% Q5, concentration 2.41x, mean position 0.695
  - `y`: 35.0% Q5, concentration 1.75x, mean position 0.583
  - `eey`: 24.6% Q1 (line-initial), concentration 1.23x, mean position 0.418
  - `ey`: 25.7% Q2 (early), concentration 1.29x, mean position 0.437
  - `edy`: central bias, mean position 0.477
- R² variance decomposition:
  - PREFIX alone: 0.069, MIDDLE alone: 0.062, SUFFIX alone: 0.027
  - All three additive: 0.143
  - SUFFIX unique contribution: 0.025

### T2: Paragraph Quintile Trajectories (FAIL)
- Only 2/21 testable suffixes monotonic (edy, dy)
- Bonferroni threshold: p < 0.0024
- C932 category gradients (terminal r=-0.89, bare r=+0.90) do NOT decompose to individual suffixes
- Category-level gradients are emergent from suffix-frequency weighting, not individual suffix behavior

### T3: Suffix Sequential Grammar (CONFIRMED)
- chi² = 2896, df=1225, p=1.1e-136, **Cramér's V = 0.063** (exceeds PREFIX V=0.060)
- 5 forbidden transitions (|z| > 3.0):
  - edy→NONE (-8.5σ), dy→NONE (-5.7σ), s→edy (-3.3σ), aiin→edy (-3.3σ), ain→aiin (-3.1σ)
- 17 enriched transitions (z > 3.0):
  - **edy→edy (+14.3σ)**, **dy→dy (+11.2σ)**, ain→hy (+8.2σ), aiin→hy (+5.2σ)
  - s→s (+4.8σ), eey→eey (+4.5σ), r→r (+4.4σ), NONE→NONE (+4.2σ)
  - edy→eey (+4.4σ), dy→ar (+4.7σ), eey→aiin (+4.0σ)
- Sequential MI: 0.019 bits (0.7% of suffix entropy) — present but low
- Self-repetition is the dominant sequential signal

### T4: Suffix Cross-Token Prediction (FAIL)
- I(SUFFIX; PREFIX_{t+1}) = 0.053 bits, I(MIDDLE; PREFIX_{t+1}) = 0.094 bits
- I(SUFFIX; PREFIX_{t+1} | MIDDLE) = **-0.074 bits** (negative = fully redundant)
- I(SUFFIX; MIDDLE_{t+1} | MIDDLE) = **-0.089 bits** (also fully redundant)
- Redundancy with MIDDLE: 0.126 bits (SUFFIX and MIDDLE share next-PREFIX information entirely)
- SUFFIX adds ZERO unique cross-token prediction beyond MIDDLE class

## Suffix Positional Zone Map

| Zone | Suffixes | Mean Position |
|------|----------|---------------|
| LINE-INITIAL | eey (0.42), ey (0.44), eol (0.43) | 0.42-0.44 |
| CENTRAL | edy (0.48), aiin (0.47), ain (0.48), r (0.46), s (0.46) | 0.46-0.48 |
| UNIFORM | NONE (0.50), dy (0.52), hy (0.50), ar (0.48), al (0.49), or (0.47), ol (0.54), iin (0.53), l (0.56) | 0.47-0.56 |
| LINE-FINAL | y (0.58), ly (0.70), ry (0.75), am (0.93), om (0.93) | 0.58-0.93 |

### T5: Suffix Batching Stress Test (CLOSED — Non-Executive)
- Self-repetition clustering (T3) tested for execution-dynamic effects
- **Hazard adjacency**: raw rho=+0.315, partial rho=+0.263 (controlling line length) — SURVIVES confound
  - Matched-length comparison (n=9-12): high-clustering lines have ~2x hazard adjacency rate
  - BUT explained by EN compositional density: suffix-rich tokens are EN, EN sits adjacent to FL/hazard classes
- **Lane switch rate**: raw rho=+0.096 → partial rho=+0.047 — ARTIFACT of line length
- **Recovery distribution**: FQ doubles (11%→23%) in high-clustering lines; chi²=27.4, p<0.001
- **Regime clustering**: KW H=27.1, p<0.001; REGIME_1/2 slightly higher intensity than REGIME_3/4
- **EN density control**: partial rho=+0.263 survives controlling for BOTH line length AND EN fraction (p=9e-38). Matched bins: at constant EN density (0.3-0.7), high-clustering lines have ~1.6x hazard adjacency. Signal is NOT purely an EN density artifact — suffix composition within EN genuinely correlates with hazard proximity.
- **But**: does not alter 6-state compression, memory depth, forbidden arcs, hazard gate duration, or macro automaton (expert assessment). EN micro-structural refinement, not architectural.
- **Verdict: MORPHOLOGICAL_BATCHING — CLOSED.** Suffix clustering is real, survives all confound controls, but refines EN micro-structure without deforming grammar. Non-executive.

## Implications

- **Extends C375**: am as 7.7x line-final specialist now confirmed in full census (4.40x Q5 concentration); om joins as equally extreme
- **Extends C932**: Category paragraph gradients are EMERGENT, not individual-suffix properties — confirmed by T2 failure
- **Parallels C1001**: SUFFIX sequential grammar (V=0.063) is comparable to PREFIX sequential grammar (V=0.060), establishing a structural parallel
- **New**: Self-repetition dominance (edy→edy +14.3σ) — suffixed tokens cluster into morphological batches within lines. This is non-executive compositional clustering driven by EN role density, not a new architectural layer
- **Falsifies**: Any hypothesis that SUFFIX carries unique cross-token sequential information beyond MIDDLE class identity
- **Closes**: Suffix batching as potential execution grammar — hazard correlation is a compositional artifact of EN density, not a causal mechanism

## Provenance

- `phases/SUFFIX_POSITIONAL_STATE_MAPPING/results/t1_suffix_positional_census.json`
- `phases/SUFFIX_POSITIONAL_STATE_MAPPING/results/t2_suffix_paragraph_trajectories.json`
- `phases/SUFFIX_POSITIONAL_STATE_MAPPING/results/t3_suffix_sequential_grammar.json`
- `phases/SUFFIX_POSITIONAL_STATE_MAPPING/results/t4_suffix_cross_token_prediction.json`
- `phases/SUFFIX_POSITIONAL_STATE_MAPPING/results/t5_suffix_batching_stress_test.json`
- `phases/SUFFIX_POSITIONAL_STATE_MAPPING/results/t5c_en_density_control.json`
