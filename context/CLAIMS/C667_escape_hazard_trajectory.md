# C667: Escape/Hazard Density Trajectory

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

Hazard-class token density and escape event density are **stationary within folios**. Neither concentrates early or late. Forbidden token-pair transitions (the 17 forbidden pairs) produced zero events in the corpus.

However, escape efficiency (escape/hazard ratio) declines in Q4 (0.579 vs 0.636 in Q1-Q3), suggesting late-program escape routes are slightly constrained.

## Evidence

### Hazard-Class Token Density (2420 lines)

| Quartile | Density |
|----------|---------|
| Q1 | 0.1543 |
| Q2 | 0.1651 |
| Q3 | 0.1545 |
| Q4 | 0.1631 |

Spearman rho = +0.009, p = 0.650. KW H = 2.43, p = 0.488. **FLAT.**

### Forbidden Transition Events

Total forbidden events: **0** across 23,096 tokens. The 17 token-level forbidden pairs are never observed in the H-track filtered corpus. This means hazard detection must use class-level proximity, not literal forbidden-pair occurrence.

### Escape Density

| Quartile | Density |
|----------|---------|
| Q1 | 0.0955 |
| Q2 | 0.1012 |
| Q3 | 0.0946 |
| Q4 | 0.0894 |

Spearman rho = -0.029, p = 0.149. KW H = 5.28, p = 0.152. **FLAT.**

### Escape/Hazard Ratio by Quartile

| Q | Hazard Tokens | Escapes | Ratio |
|---|--------------|---------|-------|
| Q1 | 1018 | 647 | 0.636 |
| Q2 | 938 | 597 | 0.637 |
| Q3 | 923 | 583 | 0.632 |
| Q4 | 944 | 547 | **0.579** |

Q4 escape efficiency drops to 0.579 (Q1-Q3 mean: 0.635).

### Escape Subfamily Stability

QO fraction among escapes: Q1=41.6%, Q2=42.7%, Q3=38.3%, Q4=41.9%. No significant drift. CHSH dominance (~58%) is stable across all quartiles, consistent with C645.

### Regime Stratification

| Regime | Hazard Q1 | Hazard Q4 | Slope |
|--------|-----------|-----------|-------|
| REGIME_1 | 0.168 | 0.151 | -0.017 |
| REGIME_2 | 0.151 | 0.191 | +0.040 |
| REGIME_3 | 0.131 | 0.183 | +0.053 |
| REGIME_4 | 0.148 | 0.148 | +0.000 |

Regimes diverge: REGIME_2/3 show late hazard increase; REGIME_1 shows decline; REGIME_4 is flat.

## Interpretation

Hazard exposure is deployed at constant density throughout programs. This extends C458 (hazard density clamped between folios, CV=0.114) to within-folio stationarity: the controller maintains a fixed risk surface at all temporal scales.

The zero forbidden-pair events confirm these pairs are extremely rare or absent in the H-track corpus at the token level. The hazard topology operates at the class level (instruction class transitions), not at the specific token-pair level.

The Q4 escape efficiency decline (0.579 vs ~0.635) hints that late-program lines may have slightly fewer escape opportunities — consistent with convergence behavior where the control loop narrows its operating range.

## Cross-References

- C548: Gateway front-loading (rho=-0.368) operates at manuscript level, NOT within folios
- C458: Hazard density CV=0.114 (clamped between folios) — C667 shows it's also clamped within folios
- C645: CHSH post-hazard dominance (75.2%) — escape subfamily ratio is stable across quartiles
- C109: 17 forbidden transitions — zero literal events in H-track corpus

## Provenance

B_FOLIO_TEMPORAL_PROFILE, Script 2 (folio_temporal_dynamics.py), Test 4
