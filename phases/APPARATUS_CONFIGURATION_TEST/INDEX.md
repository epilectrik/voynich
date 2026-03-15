# Phase 589: APPARATUS_CONFIGURATION_TEST

**Status:** COMPLETE
**Date:** 2026-03-14
**Version:** 5.62
**Constraints:** C1709-C1711

## Purpose

Test whether A folio PP MIDDLE content predicts B-side operational manifold position — i.e., whether different PP pools map to different regions of the B-side operational space. Uses coverage-weighted centroids to bridge A→B through PP MIDDLE overlap, with bridge/dark decomposition (C1139) to identify which pipeline carries the signal.

## Scripts

| Script | Runtime | Purpose |
|--------|---------|---------|
| `scripts/apparatus_configuration_test.py` | ~20s | 3 tests: Mantel (PP dist vs manifold dist), 10-axis prediction (F-params + profiles), section mediation |

## Results

### T1: PP Similarity Predicts B-Side Manifold Distance (Mantel Test)

| Metric | Value |
|--------|-------|
| A folios | 114 |
| B folios (with apparatus data) | 76 |
| **Full PP Mantel r** | **0.4226** |
| Full PP Mantel p | <0.0001 |
| Null distribution | mean=0.0001, std=0.044 |
| Partial Mantel (size + section) | r=0.4062, p<0.0001 |
| **Bridge PP Mantel r** | **0.4278** |
| Bridge PP partial Mantel | r=0.4148, p<0.0001 |
| Dark PP Mantel r | 0.2047 |
| Dark PP partial Mantel | r=0.2057, p<0.0001 |

**PASS.** PP MIDDLE similarity strongly predicts B-side manifold distance. Bridge MIDDLEs (77% of pool, r=0.43) dominate over dark MIDDLEs (22%, r=0.20). Controls (pool size, section) barely diminish the signal. Pipeline verdict: **BRIDGE_DOMINANT**.

### T2: PP Content Predicts Manifold Axes (10-axis, Bonferroni-corrected)

| Axis | Full rho | Bridge rho | Dark rho | Significant? |
|------|----------|------------|----------|--------------|
| F4_raw | -0.340 | -0.272 | -0.181 | YES |
| SUSTAINED_HEAT | -0.227 | -0.210 | -0.168 | YES |
| DIRECT_FIRE | -0.224 | -0.215 | -0.173 | YES |
| F5 | -0.174 | -0.175 | -0.216 | no |
| PRECISION | -0.179 | -0.184 | -0.215 | no |
| DISTILLATION | -0.163 | -0.160 | -0.163 | no |
| SEALED_VESSEL | -0.151 | -0.166 | -0.213 | no |
| F3 | -0.118 | -0.134 | -0.169 | no |
| F1 | -0.117 | -0.144 | -0.195 | no |
| F2 | -0.077 | -0.137 | -0.176 | no |

**PASS.** 3/10 axes significant (full, bridge, and dark each pass 3/10). F4_raw is the strongest predicted axis. All correlations negative (similar PPs → similar axis values, as expected).

### T3: Section Mediation

| Metric | Value |
|--------|-------|
| Within-section pairs | 1,265 |
| Within-section rho (full) | 0.381 |
| Within-section p | 4.8e-45 |
| Within-section rho (bridge) | 0.440 |
| Within-section rho (dark) | 0.343 |
| Between-section pairs | 5,176 |
| Between-section rho | 0.390 |
| Max per-axis change after section control | 0.019 |

**PASS (INDEPENDENT).** Signal persists fully within sections (rho=0.38 vs between-section rho=0.39). Section membership does not mediate the PP→manifold connection. Per-axis partial correlations barely change when controlling section.

### Bridge/Dark Decomposition

| Metric | Value |
|--------|-------|
| Bridge PPs per folio (mean) | 28.8 |
| Dark PPs per folio (mean) | 8.3 |
| Other PPs per folio (mean) | 0.1 |
| Bridge+dark coverage | 99.6% |
| Full coverage (A→B mean) | 0.303 |
| Bridge coverage (A→B mean) | 0.293 |
| Dark coverage (A→B mean) | 0.010 |

Bridge MIDDLEs account for 77% of PP pools and carry the dominant manifold signal (r=0.43 vs dark r=0.20). Bridge+dark account for 99.6% of all PP MIDDLEs.

## Constraint Verdicts

| C# | Verdict | Description |
|----|---------|-------------|
| C1709 | PP_MANIFOLD_CORRELATION | PP MIDDLE distance predicts B-side manifold position (Mantel r=0.4226, partial r=0.4062); bridge-dominant (r=0.4278 > dark r=0.2047) |
| C1710 | PP_AXIS_PREDICTION | PP composition predicts 3/10 B-side manifold axes (F4_raw rho=-0.340, SUSTAINED_HEAT rho=-0.227, DIRECT_FIRE rho=-0.224); prediction partial not comprehensive |
| C1711 | PP_MANIFOLD_SECTION_INDEPENDENT | PP-manifold correlation is section-independent (within-section rho=0.381, between-section rho=0.390; max per-axis change after section control = 0.019) |

## Verdict

**APPARATUS_CONFIGURATION_SUPPORTED.** A folio PP MIDDLE content genuinely predicts B-side operational manifold position, through a bridge-dominant pipeline, independent of section membership. Three specific manifold axes respond to PP composition. The structural evidence (Tier 2) supports the interpretive claim (Tier 3) that A folios parameterize apparatus configuration.
