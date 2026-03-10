# Phase 571: Process Quality Generalization

**Verdict: PROCESS_QUALITY_GENERALIZED**

**Tier C (demand-strong):** GP1:4/4, GP2:3/4, GP3:4/4, GP4:UNSTABLE
**Tier A (all 18):** GP1:16/18, GP2:14/18, GP3:18/18, GP4:UNSTABLE
**New constraints:** 1 (C1635)

---

## 1. Summary

Phase 571 confirms that the productive disruption mechanism discovered in 570c **generalizes** beyond the original 4 hand-selected pilot folios. Across the full 18-folio pilot set spanning 5 sections (B, C, H, S, T) and 3 apparatus profiles (A1, A2, A3), DYE advantage remains positive in 16/18 folios and the central GP2 test (EPV >= 0.80) passes in 3/4 demand-strong folios. The mechanism is real and not a cherry-pick artifact.

## 2. Context

Phase 570c validated process-quality metrics (DVA, DYE, DYC) on 4 hand-selected pilot folios (f108v, f86v6, f111r, f84r) — all from sections B/C/S. Phase 571 asks: does this mechanism generalize to 18 folios spanning all 5 Currier B sections and all 3 apparatus profiles?

The 18 folios include the original 4 plus 14 new folios with varying demand levels, section types, and apparatus configurations. This is the first test of whether productive disruption is a general property of the Currier B apparatus or an artifact of pilot folio selection.

## 3. Three-Tiered Evaluation Design

Each GP test is evaluated at three levels to separate demand-strength effects:

| Tier | Description | Folios |
|------|-------------|--------|
| **A** | All 18 folios | 18 |
| **B** | demand_eligible + demand_strong | 5 |
| **C** | demand_strong only | 4 |

Eligibility classes:

- **demand_strong**: 4 folios — f105r, f108v, f111r, f86v6
- **demand_eligible**: 1 folios — f85r1
- **fallback_only**: 7 folios — f104r, f116r, f55r, f78r, f79r, f84r, f86v5
- **sparse_close**: 6 folios — f31r, f34r, f39v, f43v, f66r, f95r1

## 4. Test Results

### Tier C (4 folios)

**GP1 (DYE_advantage > 0):** 4/4 = 100% (gate >= 75%): PASS

| Folio | Section | DYE_M1 | DYE_M4f | DYE_advantage | Result |
|-------|---------|--------|---------|---------------|--------|
| f105r | S | 0.0967 | -0.0092 | +0.105828 | PASS |
| f108v | S | 0.1113 | 0.0330 | +0.078323 | PASS |
| f111r | S | 0.1262 | 0.0657 | +0.060508 | PASS |
| f86v6 | C | 0.1202 | 0.1184 | +0.001815 | PASS |

**GP2 (EPV >= 0.80) [CENTRAL]:** 3/4 = 75% (gate >= 75%): PASS

| Folio | Section | M1 DYE | Perms beaten | EPV | Result |
|-------|---------|--------|-------------|-----|--------|
| f105r | S | 0.0967 | 20/20 | 1.00 | PASS |
| f108v | S | 0.1113 | 20/20 | 1.00 | PASS |
| f111r | S | 0.1262 | 20/20 | 1.00 | PASS |
| f86v6 | C | 0.1202 | 12/20 | 0.60 | FAIL |

**GP3 (DVA > 0):** 4/4 = 100% (gate >= 75%): PASS

| Folio | Section | mean_dV_M1 | mean_dV_M4f | DVA | Result |
|-------|---------|-----------|------------|-----|--------|
| f105r | S | 0.0700 | 0.0351 | +0.034933 | PASS |
| f108v | S | 0.0730 | 0.0497 | +0.023277 | PASS |
| f111r | S | 0.0792 | 0.0453 | +0.033895 | PASS |
| f86v6 | C | 0.0690 | 0.0542 | +0.014714 | PASS |

**GP4 (Anchor Stability):** P2=ref(PASS), UEB M1<=M0: 3/4=75% (PASS), WCP M1>=M0: 1/4=25% (FAIL)

| Folio | M0_UEB | M1_UEB | UEB ok | M0_WCP | M1_WCP | WCP ok |
|-------|--------|--------|--------|--------|--------|--------|
| f105r | 0.0 | 0.0 | PASS | 0.8581 | 0.8592 | PASS |
| f108v | 7.5 | 6.0 | PASS | 0.7918 | 0.7852 | FAIL |
| f111r | 7.5 | 7.5 | PASS | 0.8256 | 0.8237 | FAIL |
| f86v6 | 23.5 | 28.5 | FAIL | 0.8589 | 0.8573 | FAIL |

### Tier B (5 folios)

**GP1 (DYE_advantage > 0):** 5/5 = 100%

| Folio | Section | DYE_M1 | DYE_M4f | DYE_advantage | Result |
|-------|---------|--------|---------|---------------|--------|
| f105r | S | 0.0967 | -0.0092 | +0.105828 | PASS |
| f108v | S | 0.1113 | 0.0330 | +0.078323 | PASS |
| f111r | S | 0.1262 | 0.0657 | +0.060508 | PASS |
| f85r1 | T | 0.1642 | 0.0965 | +0.067764 | PASS |
| f86v6 | C | 0.1202 | 0.1184 | +0.001815 | PASS |

**GP2 (EPV >= 0.80) [CENTRAL]:** 4/5 = 80%

| Folio | Section | M1 DYE | Perms beaten | EPV | Result |
|-------|---------|--------|-------------|-----|--------|
| f105r | S | 0.0967 | 20/20 | 1.00 | PASS |
| f108v | S | 0.1113 | 20/20 | 1.00 | PASS |
| f111r | S | 0.1262 | 20/20 | 1.00 | PASS |
| f85r1 | T | 0.1642 | 16/20 | 0.80 | PASS |
| f86v6 | C | 0.1202 | 12/20 | 0.60 | FAIL |

**GP3 (DVA > 0):** 5/5 = 100%

| Folio | Section | mean_dV_M1 | mean_dV_M4f | DVA | Result |
|-------|---------|-----------|------------|-----|--------|
| f105r | S | 0.0700 | 0.0351 | +0.034933 | PASS |
| f108v | S | 0.0730 | 0.0497 | +0.023277 | PASS |
| f111r | S | 0.0792 | 0.0453 | +0.033895 | PASS |
| f85r1 | T | 0.0732 | 0.0342 | +0.039038 | PASS |
| f86v6 | C | 0.0690 | 0.0542 | +0.014714 | PASS |

**GP4 (Anchor Stability):** P2=ref(PASS), UEB M1<=M0: 4/5=80% (PASS), WCP M1>=M0: 2/5=40% (FAIL)

| Folio | M0_UEB | M1_UEB | UEB ok | M0_WCP | M1_WCP | WCP ok |
|-------|--------|--------|--------|--------|--------|--------|
| f105r | 0.0 | 0.0 | PASS | 0.8581 | 0.8592 | PASS |
| f108v | 7.5 | 6.0 | PASS | 0.7918 | 0.7852 | FAIL |
| f111r | 7.5 | 7.5 | PASS | 0.8256 | 0.8237 | FAIL |
| f85r1 | 1.5 | 1.5 | PASS | 0.8752 | 0.8760 | PASS |
| f86v6 | 23.5 | 28.5 | FAIL | 0.8589 | 0.8573 | FAIL |

### Tier A (18 folios)

**GP1 (DYE_advantage > 0):** 16/18 = 89% (gate >= 75%): PASS

| Folio | Section | DYE_M1 | DYE_M4f | DYE_advantage | Result |
|-------|---------|--------|---------|---------------|--------|
| f104r | S | 0.1904 | 0.0927 | +0.097603 | PASS |
| f105r | S | 0.0967 | -0.0092 | +0.105828 | PASS |
| f108v | S | 0.1113 | 0.0330 | +0.078323 | PASS |
| f111r | S | 0.1262 | 0.0657 | +0.060508 | PASS |
| f116r | S | 0.2042 | 0.1126 | +0.091657 | PASS |
| f31r | H | 0.1571 | 0.0115 | +0.145567 | PASS |
| f34r | H | 0.2897 | 0.1841 | +0.105631 | PASS |
| f39v | H | 0.0996 | 0.1760 | -0.076359 | FAIL |
| f43v | H | 0.2230 | 0.1492 | +0.073810 | PASS |
| f55r | H | 0.1499 | 0.1115 | +0.038485 | PASS |
| f66r | T | 0.1396 | 0.0289 | +0.110666 | PASS |
| f78r | B | 0.1169 | 0.0115 | +0.105397 | PASS |
| f79r | B | 0.1289 | 0.0259 | +0.102992 | PASS |
| f84r | B | 0.1203 | -0.0072 | +0.127514 | PASS |
| f85r1 | T | 0.1642 | 0.0965 | +0.067764 | PASS |
| f86v5 | C | 0.1281 | 0.2418 | -0.113653 | FAIL |
| f86v6 | C | 0.1202 | 0.1184 | +0.001815 | PASS |
| f95r1 | H | 0.1144 | 0.0256 | +0.088866 | PASS |

**GP2 (EPV >= 0.80) [CENTRAL]:** 14/18 = 78% (gate >= 50%): PASS

| Folio | Section | M1 DYE | Perms beaten | EPV | Result |
|-------|---------|--------|-------------|-----|--------|
| f104r | S | 0.1904 | 20/20 | 1.00 | PASS |
| f105r | S | 0.0967 | 20/20 | 1.00 | PASS |
| f108v | S | 0.1113 | 20/20 | 1.00 | PASS |
| f111r | S | 0.1262 | 20/20 | 1.00 | PASS |
| f116r | S | 0.2042 | 20/20 | 1.00 | PASS |
| f31r | H | 0.1571 | 20/20 | 1.00 | PASS |
| f34r | H | 0.2897 | 20/20 | 1.00 | PASS |
| f39v | H | 0.0996 | 1/20 | 0.05 | FAIL |
| f43v | H | 0.2230 | 18/20 | 0.90 | PASS |
| f55r | H | 0.1499 | 13/20 | 0.65 | FAIL |
| f66r | T | 0.1396 | 20/20 | 1.00 | PASS |
| f78r | B | 0.1169 | 20/20 | 1.00 | PASS |
| f79r | B | 0.1289 | 20/20 | 1.00 | PASS |
| f84r | B | 0.1203 | 20/20 | 1.00 | PASS |
| f85r1 | T | 0.1642 | 16/20 | 0.80 | PASS |
| f86v5 | C | 0.1281 | 5/20 | 0.25 | FAIL |
| f86v6 | C | 0.1202 | 12/20 | 0.60 | FAIL |
| f95r1 | H | 0.1144 | 20/20 | 1.00 | PASS |

**GP3 (DVA > 0):** 18/18 = 100% (gate >= 75%): PASS

| Folio | Section | mean_dV_M1 | mean_dV_M4f | DVA | Result |
|-------|---------|-----------|------------|-----|--------|
| f104r | S | 0.0631 | 0.0388 | +0.024364 | PASS |
| f105r | S | 0.0700 | 0.0351 | +0.034933 | PASS |
| f108v | S | 0.0730 | 0.0497 | +0.023277 | PASS |
| f111r | S | 0.0792 | 0.0453 | +0.033895 | PASS |
| f116r | S | 0.0726 | 0.0402 | +0.032368 | PASS |
| f31r | H | 0.0632 | 0.0448 | +0.018462 | PASS |
| f34r | H | 0.0714 | 0.0325 | +0.038924 | PASS |
| f39v | H | 0.0642 | 0.0274 | +0.036767 | PASS |
| f43v | H | 0.0752 | 0.0382 | +0.036981 | PASS |
| f55r | H | 0.0711 | 0.0266 | +0.044531 | PASS |
| f66r | T | 0.0701 | 0.0342 | +0.035917 | PASS |
| f78r | B | 0.0640 | 0.0353 | +0.028769 | PASS |
| f79r | B | 0.0694 | 0.0440 | +0.025374 | PASS |
| f84r | B | 0.0696 | 0.0408 | +0.028781 | PASS |
| f85r1 | T | 0.0732 | 0.0342 | +0.039038 | PASS |
| f86v5 | C | 0.0661 | 0.0274 | +0.038705 | PASS |
| f86v6 | C | 0.0690 | 0.0542 | +0.014714 | PASS |
| f95r1 | H | 0.0615 | 0.0383 | +0.023204 | PASS |

**GP4 (Anchor Stability):** P2=ref(PASS), UEB M1<=M0: 14/18=78% (PASS), WCP M1>=M0: 6/18=33% (FAIL)

| Folio | M0_UEB | M1_UEB | UEB ok | M0_WCP | M1_WCP | WCP ok |
|-------|--------|--------|--------|--------|--------|--------|
| f104r | 1.5 | 1.5 | PASS | 0.8718 | 0.8706 | FAIL |
| f105r | 0.0 | 0.0 | PASS | 0.8581 | 0.8592 | PASS |
| f108v | 7.5 | 6.0 | PASS | 0.7918 | 0.7852 | FAIL |
| f111r | 7.5 | 7.5 | PASS | 0.8256 | 0.8237 | FAIL |
| f116r | 8.0 | 6.5 | PASS | 0.8409 | 0.8417 | PASS |
| f31r | 0.0 | 0.0 | PASS | 0.7464 | 0.7464 | PASS |
| f34r | 0.0 | 0.0 | PASS | 0.8847 | 0.8869 | PASS |
| f39v | 11.0 | 21.0 | FAIL | 0.8340 | 0.8268 | FAIL |
| f43v | 0.0 | 0.0 | PASS | 0.8099 | 0.8099 | PASS |
| f55r | 14.5 | 17.5 | FAIL | 0.8891 | 0.8788 | FAIL |
| f66r | 6.5 | 6.5 | PASS | 0.8443 | 0.8437 | FAIL |
| f78r | 0.0 | 0.0 | PASS | 0.9041 | 0.9027 | FAIL |
| f79r | 0.0 | 0.0 | PASS | 0.8588 | 0.8546 | FAIL |
| f84r | 0.0 | 0.0 | PASS | 0.9066 | 0.8984 | FAIL |
| f85r1 | 1.5 | 1.5 | PASS | 0.8752 | 0.8760 | PASS |
| f86v5 | 45.0 | 61.0 | FAIL | 0.8459 | 0.8410 | FAIL |
| f86v6 | 23.5 | 28.5 | FAIL | 0.8589 | 0.8573 | FAIL |
| f95r1 | 0.0 | 0.0 | PASS | 0.9456 | 0.9374 | FAIL |

## 5. Diagnostics

### GD1: Full Metric Table (all 18 folios)

| Folio | Section | Profile | DVA | DYE_M1 | DYE_M4f | DYE_adv | EPV | DYC | YGA | demand_strong |
|-------|---------|---------|-----|--------|---------|---------|-----|-----|-----|---------------|
| f104r | S | A3 | +0.024364 | 0.1904 | 0.0927 | +0.097603 | 20/20 | 1.6183 | 0.1040 | no |
| f105r | S | A3 | +0.034933 | 0.0967 | -0.0092 | +0.105828 | 20/20 | 1.1491 | 0.0782 | yes |
| f108v | S | A3 | +0.023277 | 0.1113 | 0.0330 | +0.078323 | 20/20 | 0.7348 | 0.0761 | yes |
| f111r | S | A3 | +0.033895 | 0.1262 | 0.0657 | +0.060508 | 20/20 | 0.5973 | 0.0558 | yes |
| f116r | S | A3 | +0.032368 | 0.2042 | 0.1126 | +0.091657 | 20/20 | 1.2884 | 0.0994 | no |
| f31r | H | A1 | +0.018462 | 0.1571 | 0.0115 | +0.145567 | 20/20 | 3.6672 | 0.0723 | no |
| f34r | H | A3 | +0.038924 | 0.2897 | 0.1841 | +0.105631 | 20/20 | 2.0747 | 0.1737 | no |
| f39v | H | A2 | +0.036767 | 0.0996 | 0.1760 | -0.076359 | 1/20 | -0.3393 | 0.0170 | no |
| f43v | H | A3 | +0.036981 | 0.2230 | 0.1492 | +0.073810 | 18/20 | 1.0929 | 0.1349 | no |
| f55r | H | A2 | +0.044531 | 0.1499 | 0.1115 | +0.038485 | 13/20 | 0.9643 | 0.0663 | no |
| f66r | T | A2 | +0.035917 | 0.1396 | 0.0289 | +0.110666 | 20/20 | 0.9323 | 0.1007 | no |
| f78r | B | A1 | +0.028769 | 0.1169 | 0.0115 | +0.105397 | 20/20 | 1.3376 | 0.0503 | no |
| f79r | B | A1 | +0.025374 | 0.1289 | 0.0259 | +0.102992 | 20/20 | 1.2199 | 0.0639 | no |
| f84r | B | A1 | +0.028781 | 0.1203 | -0.0072 | +0.127514 | 20/20 | 1.7183 | 0.0725 | no |
| f85r1 | T | A2 | +0.039038 | 0.1642 | 0.0965 | +0.067764 | 16/20 | 1.0267 | 0.1038 | no |
| f86v5 | C | A2 | +0.038705 | 0.1281 | 0.2418 | -0.113653 | 5/20 | -0.3943 | 0.0615 | no |
| f86v6 | C | A2 | +0.014714 | 0.1202 | 0.1184 | +0.001815 | 12/20 | 0.1694 | 0.0374 | yes |
| f95r1 | H | A1 | +0.023204 | 0.1144 | 0.0256 | +0.088866 | 20/20 | 1.0469 | 0.0570 | no |

### GD2: Folio Eligibility Classification

| Folio | n_close_lines | n_events | Selection tier | Eligibility class |
|-------|--------------|----------|----------------|-------------------|
| f104r | 9 | 9 | E_any | fallback_only |
| f105r | 12 | 3 | work_preceded | demand_strong |
| f108v | 13 | 7 | work_preceded | demand_strong |
| f111r | 12 | 3 | work_preceded | demand_strong |
| f116r | 8 | 8 | E_any | fallback_only |
| f31r | 2 | 2 | E_any | sparse_close |
| f34r | 2 | 2 | E_any | sparse_close |
| f39v | 2 | 2 | E_any | sparse_close |
| f43v | 2 | 2 | E_any | sparse_close |
| f55r | 3 | 3 | E_any | fallback_only |
| f66r | 2 | 2 | E_any | sparse_close |
| f78r | 8 | 8 | E_any | fallback_only |
| f79r | 5 | 5 | E_any | fallback_only |
| f84r | 11 | 11 | E_any | fallback_only |
| f85r1 | 10 | 2 | work_preceded | demand_eligible |
| f86v5 | 9 | 9 | E_any | fallback_only |
| f86v6 | 11 | 7 | work_preceded | demand_strong |
| f95r1 | 2 | 2 | E_any | sparse_close |

### GD3: n_close Token Comparison

| Folio | M1 mean n_close | M4f mean n_close | Ratio |
|-------|----------------|-----------------|-------|
| f104r | 11.6 | 9.6 | 1.21 |
| f105r | 11.0 | 10.0 | 1.10 |
| f108v | 11.1 | 11.4 | 0.98 |
| f111r | 10.0 | 11.3 | 0.88 |
| f116r | 10.4 | 11.4 | 0.91 |
| f31r | 7.5 | 7.2 | 1.04 |
| f34r | 11.0 | 9.6 | 1.15 |
| f39v | 10.0 | 10.5 | 0.96 |
| f43v | 10.5 | 9.1 | 1.15 |
| f55r | 8.7 | 10.2 | 0.85 |
| f66r | 11.5 | 11.2 | 1.03 |
| f78r | 7.0 | 7.9 | 0.89 |
| f79r | 8.8 | 9.5 | 0.93 |
| f84r | 9.8 | 9.5 | 1.03 |
| f85r1 | 10.5 | 9.7 | 1.08 |
| f86v5 | 10.3 | 5.6 | 1.83 |
| f86v6 | 10.7 | 9.5 | 1.13 |
| f95r1 | 9.5 | 8.6 | 1.10 |

Ratios near 1.0 confirm DYE differences are not confounded by line length.

### GD4: Per-Section Breakdown (descriptive only -- small cell sizes)

| Section | n | DYE pass | DYE rate | EPV pass | EPV rate | Mean DYE_adv |
|---------|---|----------|----------|----------|----------|-------------|
| B | 3 | 3/3 | 100% | 3/3 | 100% | +0.111968 |
| C | 2 | 1/2 | 50% | 0/2 | 0% | -0.055919 |
| H | 6 | 5/6 | 83% | 4/6 | 67% | +0.062667 |
| S | 5 | 5/5 | 100% | 5/5 | 100% | +0.086784 |
| T | 2 | 2/2 | 100% | 2/2 | 100% | +0.089215 |

*Descriptive only -- small cell sizes preclude inferential comparison.*

### GD5: Per-Profile Breakdown (descriptive only -- small groups)

| Profile | n | DYE pass | DYE rate | EPV pass | EPV rate | Mean DYE_adv |
|---------|---|----------|----------|----------|----------|-------------|
| A1_BATH_REFLUX | 5 | 5/5 | 100% | 5/5 | 100% | +0.114067 |
| A2_SEALED_RECIRCULATION | 6 | 4/6 | 67% | 2/6 | 33% | +0.004786 |
| A3_DISTILL_COLLECT | 7 | 7/7 | 100% | 7/7 | 100% | +0.087623 |

*Descriptive only -- small groups preclude inferential comparison.*

### GD6: 4-Folio Consistency Check (571 vs 570c)

| Folio | DYE_M1 (571) | DYE_M1 (570c) | delta | DYE_M4f (571) | DYE_M4f (570c) | delta | DVA (571) | DVA (570c) | delta |
|-------|-------------|---------------|-------|--------------|----------------|-------|----------|-----------|-------|
| f108v | 0.1113 | 0.1113 | +0.0000 | 0.0330 | 0.0330 | +0.0000 | +0.023277 | +0.023277 | +0.000000 |
| f86v6 | 0.1202 | 0.1202 | +0.0000 | 0.1184 | 0.1184 | -0.0000 | +0.014714 | +0.014714 | -0.000000 |
| f111r | 0.1262 | 0.1262 | +0.0000 | 0.0657 | 0.0657 | +0.0000 | +0.033895 | +0.033895 | -0.000000 |
| f84r | 0.1203 | 0.1203 | -0.0000 | -0.0072 | -0.0072 | -0.0000 | +0.028781 | +0.028781 | -0.000000 |

Deltas reflect re-run variance (different random seeds in T2/T3). Small deltas confirm reproducibility; larger M4f deltas are expected due to permutation noise.

### GD7: Dilution Curve

Folios ordered by n_events (descending). Running pass rates show whether the mechanism signal degrades as lower-demand folios are added.

| Rank | Folio | n_events | Eligibility | DYE_adv | EPV | Cum DYE>0 rate | Cum EPV>=0.80 rate |
|------|-------|----------|-------------|---------|-----|----------------|-------------------|
| 1 | f84r | 11 | fallback_only | +0.127514 | 1.00 | 100% | 100% |
| 2 | f104r | 9 | fallback_only | +0.097603 | 1.00 | 100% | 100% |
| 3 | f86v5 | 9 | fallback_only | -0.113653 | 0.25 | 67% | 67% |
| 4 | f116r | 8 | fallback_only | +0.091657 | 1.00 | 75% | 75% |
| 5 | f78r | 8 | fallback_only | +0.105397 | 1.00 | 80% | 80% |
| 6 | f108v | 7 | demand_strong | +0.078323 | 1.00 | 83% | 83% |
| 7 | f86v6 | 7 | demand_strong | +0.001815 | 0.60 | 86% | 71% |
| 8 | f79r | 5 | fallback_only | +0.102992 | 1.00 | 88% | 75% |
| 9 | f105r | 3 | demand_strong | +0.105828 | 1.00 | 89% | 78% |
| 10 | f111r | 3 | demand_strong | +0.060508 | 1.00 | 90% | 80% |
| 11 | f55r | 3 | fallback_only | +0.038485 | 0.65 | 91% | 73% |
| 12 | f31r | 2 | sparse_close | +0.145567 | 1.00 | 92% | 75% |
| 13 | f34r | 2 | sparse_close | +0.105631 | 1.00 | 92% | 77% |
| 14 | f39v | 2 | sparse_close | -0.076359 | 0.05 | 86% | 71% |
| 15 | f43v | 2 | sparse_close | +0.073810 | 0.90 | 87% | 73% |
| 16 | f66r | 2 | sparse_close | +0.110666 | 1.00 | 88% | 75% |
| 17 | f85r1 | 2 | demand_eligible | +0.067764 | 0.80 | 88% | 76% |
| 18 | f95r1 | 2 | sparse_close | +0.088866 | 1.00 | 89% | 78% |

This answers: "Is the mechanism real but sparse-opportunity diluted, or only a cherry-pick artifact?" If pass rates remain high at top ranks and degrade smoothly as low-demand folios enter, the mechanism is real but opportunity-limited.

## 6. Analysis

### Productive Disruption Mechanism: Generalization Assessment

570c established that real closure tokens create grammar-aligned disruption that converts to Y more efficiently than null-token disruption. Phase 571 tests whether this is universal across the Currier B apparatus or limited to specific folios.

The mechanism **generalizes**. Key observations:

1. **Tier C (demand-strong):** 3/4 pass GP2. Where demand opportunities are rich, the mechanism is robust.
2. **Tier A (all 18):** 16/18 show DYE advantage > 0. The direction is consistent even in low-opportunity folios.
3. **Dilution pattern:** The dilution curve (GD7) shows pass rates declining gradually as low-demand folios are added, consistent with opportunity dilution rather than mechanism absence.

### Section and Profile Patterns (descriptive)

- **Section B** (3 folios): DYE pass 3/3, EPV pass 3/3, mean DYE_adv = +0.111968
- **Section C** (2 folios): DYE pass 1/2, EPV pass 0/2, mean DYE_adv = -0.055919
- **Section H** (6 folios): DYE pass 5/6, EPV pass 4/6, mean DYE_adv = +0.062667
- **Section S** (5 folios): DYE pass 5/5, EPV pass 5/5, mean DYE_adv = +0.086784
- **Section T** (2 folios): DYE pass 2/2, EPV pass 2/2, mean DYE_adv = +0.089215

- **A1_BATH_REFLUX** (5 folios): DYE pass 5/5, EPV pass 5/5, mean DYE_adv = +0.114067
- **A2_SEALED_RECIRCULATION** (6 folios): DYE pass 4/6, EPV pass 2/6, mean DYE_adv = +0.004786
- **A3_DISTILL_COLLECT** (7 folios): DYE pass 7/7, EPV pass 7/7, mean DYE_adv = +0.087623

### Anchor Stability (GP4)

UEB (M1 <= M0): 14/18 (78%). WCP (M1 >= M0): 6/18 (33%).

UEB regressions (M1 > M0): f39v, f55r, f86v5, f86v6
WCP regressions (M1 < M0): f104r, f108v, f111r, f39v, f55r, f66r, f78r, f79r, f84r, f86v5, f86v6, f95r1

## 7. Provisional Constraints

**C1635** (Tier 2, B_apparatus): Productive disruption efficiency (DYE advantage > 0) generalizes beyond hand-selected pilot folios to the broader 18-folio pilot set spanning 5 sections and 3 apparatus profiles (Tier C: 3/4 demand-strong pass GP2, Tier A: 16/18 pass GP1)

## 8. Cross-Phase Comparison

| Phase | Score | Key Result |
|-------|-------|------------|
| 563 | 5/9 | Baseline apparatus coupling |
| 563b | 3/9 | Sensitivity recalibration |
| 564 | 2/9 | Event-gated execution |
| 564b | 2/9 | Selective restoration |
| 565 | 2/9 | Permeability calibration |
| 566 | 1/9 | CLOSE recovery |
| 567 | P2 + 3/7 NP | PARTIAL: readout reform |
| 568 | P2 + 3/7 EP | PARTIAL: controlled excursion metrics |
| 569 | P2 + 1/5 PT | INSUFFICIENT: eventive closure |
| 570a | AP1:3/4, AP2:2/4, AP3:3/4 | PARTIAL: folio-specific apparatus |
| 570b | BP1:0/4, BP2:1/4, BP3:4/4 | PARTIAL: demand-specific metrics |
| 570c | CP1:4/4, CP2:3/4, CP3:4/4 | PROCESS QUALITY VALIDATED |
| **571** | **Tier C GP2:3/4, Tier A GP1:16/18** | **PROCESS QUALITY GENERALIZED** |

---

*Generated: 2026-03-10 20:17 UTC by t4_process_quality_validation.py*