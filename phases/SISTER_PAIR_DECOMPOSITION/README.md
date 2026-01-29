# SISTER_PAIR_DECOMPOSITION

**Status:** COMPLETE | **Date:** 2026-01-26 | **Constraints:** C603-C605

## Purpose

Decompose C412 (sister-escape anticorrelation, rho=-0.326, p=0.002) using sub-group machinery from EN_ANATOMY and SUB_ROLE_INTERACTION phases. The old question was "why does ch-preference anticorrelate with escape density?" This phase answers it.

## Scripts

| Script | Purpose |
|--------|---------|
| `en_subfamily_selection.py` | What determines EN QO vs CHSH selection? |
| `sister_pair_decomposition.py` | Decompose C412 through sub-group variables |

## Key Findings

### 1. CC Composition Drives EN Subfamily Selection (C603)

CC trigger composition is the strongest predictor of folio-level EN subfamily balance:
- CC_OL_D fraction -> QO proportion: rho=0.355, p=0.001
- CC_DAIIN fraction -> CHSH proportion: rho=0.345, p=0.002

Exceeds section (V=0.092), REGIME (V=0.047), and position (V=0.045).

### 2. C412 is Partially a REGIME Artifact (C604)

The anticorrelation vanishes within individual REGIMEs:
- REGIME_1: rho=-0.075 (n=23, not significant)
- REGIME_2: rho=-0.051 (n=24, not significant)
- REGIME_3: rho=-0.690 (n=8, marginal p=0.058)
- REGIME_4: rho=-0.231 (n=27, not significant)

Controlling for REGIME reduces C412 by 27.6%. The correlation is driven by between-REGIME variation in both ch_preference and escape_density.

EN subfamily and CC composition do NOT mediate C412 (8.2% and 11.7% reduction).

### 3. Two-Lane Model Validated at Folio Level (C605)

Lane balance = (en_chsh_proportion * cc_daiin_fraction) / total lane intensity:
- Predicts escape_density: rho=-0.506 (vs ch_preference rho=-0.301)
- Adds independent information: partial rho=-0.452, p<0.0001
- 68% stronger predictor than ch_preference alone

## Constraints Produced

| # | Name | Key Evidence |
|---|------|-------------|
| C603 | CC Folio-Level Subfamily Prediction | CC_OL_D->QO rho=0.355, CC_DAIIN->CHSH rho=0.345 |
| C604 | C412 REGIME Decomposition | 27.6% REGIME mediation; vanishes within REGIME_1/2 |
| C605 | Two-Lane Folio-Level Validation | Lane balance rho=-0.506, independent of ch_preference |

## Data Dependencies

| File | Source |
|------|--------|
| class_token_map.json | CLASS_COSURVIVAL_TEST |
| regime_folio_mapping.json | REGIME_SEMANTIC_INTERPRETATION |
| voynich.py | scripts/ |

## Verification

- EN total = 7,211 (matches C573)
- C412 replication: rho=-0.304 (expected ~-0.326, within tolerance)
- QO + CHSH + MINOR = 3,170 + 3,970 + 71 = 7,211 (exact)
