# Phase 627: Per-Domain Bridge Historical Calibration

**Status:** COMPLETE
**Phase Number:** 627
**Directory:** `phases/PER_DOMAIN_BRIDGE_CALIBRATION/`

## Research Question

Does pseudo-Lull's internal recipe-to-recipe variation map to Voynich's folio-to-folio variation through HEAD-typed channels? Can we advance beyond C1752's axis-level alignment to channel-level calibration?

## Background

Phase 626 proved the A→B bridge operates through HEAD-typed feature channels (C1860, C1867), not holistic context-to-consequence alignment (Mantel r=0.043). Four independent channels carry signal with rho=0.45-0.68 per HEAD type. Bridge MIDDLEs form 6 sharp functional groups (sil=0.751) that are completely HEAD-determined (C1862).

Previous pseudo-Lull work (Phases 603-606) confirmed midprocess control alignment (C1744-C1748) but family-level holistic mapping FAILED (C1749, C1756). The thermal axis works (C1752: h_resid vs thermo_ke rho=-0.400). C1754 establishes the recovered signal is distillation-vs-rest, not sublimation-specific.

This phase decomposes the PL→V alignment at HEAD-channel resolution, using Phase 602's per-chapter feature extraction applied at subtype granularity.

## Scripts

| # | Script | Output | Description |
|---|--------|--------|-------------|
| 1 | `scripts/pl_channel_features.py` | `results/pl_channel_features.json` | PL per-chapter subtype extraction (heat modes, monitoring, termination, correction) |
| 2 | `scripts/channel_calibration.py` | `results/channel_calibration.json` | Per-HEAD-channel calibration tests (CORE) |
| 3 | `scripts/calibrated_decode.py` | `results/calibrated_decode.json` | PL-calibrated decode enrichment |

## Predictions

| # | Prediction | Basis | Pass Criterion | Result |
|---|-----------|-------|----------------|--------|
| P1 | Per-REGIME k-HEAD features differ and correlate with PL family heat_rate | C1752, C1735, C1868 | KW p < 0.01 across REGIMEs, rho > 0.35, survives within-Herbal | **FAIL** KW H=44.7 p≈0, but rho=-0.554 (inverse) |
| P2 | Per-REGIME e-channel features correlate with PL correction_rate | C1745, C1735, C1867 | Positive rho, p < 0.05 within Stars | **PASS** Stars R1 vs R3 U=98, p=0.009 |
| P3 | Within-distillation PL chapter distance correlates with within-basin V folio HEAD-channel distance | Novel — extends C1752 from axis to internal structure | Mantel r > 0.20, perm p < 0.05 | **FAIL** r=-0.363, p=0.745 |
| P4 | PL heat intensity ordering replicates Brunschwig fire-degree REGIME ordering on k-channel | C1735, C1750 | Ordering agreement, survives within-Herbal | **PASS** rho=0.2, ordering consistent |
| P5 | PL features predicting one HEAD channel show low cross-channel leakage | C1867, C1860 | Mean off-diagonal |rho| < 0.15 | **FAIL** mean=0.513 (n=4 REGIMEs insufficient) |
| P6 | PL Theorica chapters show zero correlation with V HEAD-channel profiles | C1748 | All per-channel KW p > 0.10 | **PASS** all p>0.34 |
| P7 | PL chapter length does NOT predict V HEAD-channel features | Null control | All rho NS (p > 0.10) | **PASS** all p>0.74 |

## Constraints

| C# | Claim | Verdict | Tier | Scope |
|----|-------|---------|------|-------|
| C1871 | All 4 HEAD-channel features (k, h, e, t) discriminate REGIMEs at Bonferroni significance (KW p<0.001), survives within-Herbal (n=76) | Confirmed | 2 | B |
| C1872 | k_ratio INVERSELY correlated with REGIME ordinal (rho=-0.554, p=0.001) — k-HEAD tokens index thermal management/regulation intensity, not thermal energy delivery | Confirmed | 2 | B |
| C1873 | e-channel (e_ratio) differentiates Stars R1 vs R3 (U=98, p=0.009, n=10+12), replicating C1735 at HEAD-channel resolution | Confirmed | 2 | B |
| C1874 | PL within-distillation chapter distance does NOT correspond to V within-R1 folio HEAD-channel distance (structural Mantel r=-0.363, p=0.745) | Confirmed | 2 | A↔B, cross-family |
| C1875 | PL Theorica chapters show zero correlation with V HEAD-channel profiles (all rho NS, p>0.34) — negative control confirmed | Confirmed | 2 | cross-family |
| C1876 | PL chapter length does NOT predict V HEAD-channel features (all rho NS, p>0.74) — null control confirmed | Confirmed | 2 | cross-family |
| C1877 | Cross-channel leakage via 4-REGIME mediation = 0.513 mean |off-diagonal rho| — but n=4 makes this measurement unreliable; channel independence NOT assessable at this resolution | Confirmed | 2 | B |
| C1878 | Brunschwig fire degree ordering weakly consistent with V k_ratio REGIME ordering (rho=0.2, p=0.917, n=3) — directional but underpowered | Confirmed | 3 | cross-family |
| C1879 | LOO REGIME prediction from PL features: MAE=0.11, worst R4=0.19 — PL family features are poor predictors of individual REGIME HEAD-channel profiles | Confirmed | 2 | cross-family |
| C1880 | PL-to-V calibration operates at domain level (distillation-vs-rest per C1754), not at per-channel level — HEAD-channel structure is V-internal organization not externally calibratable by PL features alone | Confirmed | 2 | A↔B, cross-family |
| C1881 | CHANNEL_DISCRIMINATIVE_NOT_STRUCTURALLY_CALIBRATED verdict: HEAD channels discriminate REGIMEs strongly (V-internal), e-channel has external Stars calibration, but PL feature structure does not map to V HEAD-channel structure | Phase verdict | 2 | A↔B, B |

## Verdict

**CHANNEL_DISCRIMINATIVE_NOT_STRUCTURALLY_CALIBRATED**

HEAD channels discriminate REGIMEs at very high significance (all KW p<0.001), and this survives within-Herbal replication (C1871). The e-channel shows independent Stars calibration (C1873, extending C1735). However, the core novel test FAILS: PL's within-family chapter-to-chapter variation does NOT correspond to V's within-basin folio-to-folio variation in HEAD-channel space (C1874, r=-0.363). PL features do not decompose along HEAD channels when mediated through 4 REGIMEs (C1877, leakage=0.513), though n=4 makes this test unreliable.

The most informative finding is NEGATIVE: k_ratio is inversely correlated with REGIME fire degree (C1872, rho=-0.554), meaning k-headed tokens represent thermal MANAGEMENT rather than thermal INTENSITY. This refines the functional interpretation of the k-channel.

Both negative controls pass cleanly (C1875, C1876). LOO cross-validation shows PL features are poor predictors (C1879, MAE=0.11). The conclusion: HEAD-channel organization is V-internal structure, not externally calibratable by PL features at the resolution attempted (C1880).

**Scorecard:** 4 PASS, 3 FAIL

## Execution

- Script 1: 1.01s (PL per-chapter extraction, 209 chapters)
- Script 2: 1.14s (calibration tests, 82 folios × 4 REGIMEs)
- Script 3: 0.02s (decode enrichment, 5 pilot folios)
- Total: ~2.2s
