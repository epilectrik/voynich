# C1106: Stars Section e-Stability Kernel Enrichment

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** STARS_RECIPE_CHARACTERIZATION (Phase 392)
**Extends:** C1084 (section AXM ordering), C494 (REGIME dimensions)

---

## Statement

The Stars/Recipe section (S, n=23 folios) has a significantly different kernel balance from the rest of the manuscript: e-enriched at 66.2% vs 57.4% non-Stars, k-depleted at 23.9% vs 32.5% (chi2=145.0, p=3.3e-32, Cramer's V=0.099). This pattern survives REGIME_1 control (chi2=89.0, p=4.7e-20 within REGIME_1 alone).

Within REGIME_1, Stars diverges from non-Stars on 5/8 operational dimensions (Mann-Whitney p<0.05): k_pct, h_pct, e_pct, LINK density, and AXM self-rate. Stars is NOT just another REGIME_1 section.

---

## Evidence

### S1: Kernel Balance
| Kernel | Stars | Stars% | Non-Stars | NS% | Ratio |
|--------|-------|--------|-----------|-----|-------|
| k | 1,901 | 23.9% | 2,244 | 32.5% | 0.73x |
| h | 787 | 9.9% | 695 | 10.1% | 0.98x |
| e | 5,270 | 66.2% | 3,962 | 57.4% | 1.15x |

- Chi-square: 145.0, dof=2, p=3.3e-32
- REGIME_1 controlled: Stars_R1 e=66.8%, non-Stars_R1 e=57.1%, chi2=89.0, p=4.7e-20

### S3: REGIME_1 Homogeneity (Stars-R1 n=10 vs non-Stars-R1 n=22)
| Dimension | Stars-R1 | NS-R1 | p |
|-----------|----------|-------|---|
| k kernel% | 0.275 | 0.344 | 0.022 |
| h kernel% | 0.066 | 0.088 | 0.005 |
| e kernel% | 0.659 | 0.568 | 0.003 |
| LINK lane% | 0.034 | 0.006 | <0.001 |
| AXM self-rate | 0.674 | 0.748 | 0.014 |

5/8 dimensions significant. Stars is structurally distinct beyond REGIME membership.

---

## Interpretation

Stars programs are e-stability enriched: they spend proportionally more vocabulary on stability/completion operations and less on core heating operations. This is the kernel-level signature of the Stars section, distinct from Bio's k-enrichment (C1085: balneum mariae sustained heating). The pattern is independent of REGIME assignment — it persists when comparing Stars-R1 to non-Stars-R1, confirming this is a section property.

Combined with the 7.4x LINK elevation (C1107), Stars appears to operate a monitoring-intensive process with strong stability emphasis — consistent with the lk prefix concentration documented in C930 (fire-method monitoring).

---

## Provenance

- Phase: 392 (STARS_RECIPE_CHARACTERIZATION), Tests S1, S3
- Script: `phases/STARS_RECIPE_CHARACTERIZATION/scripts/stars_recipe_characterization.py`
- Results: `phases/STARS_RECIPE_CHARACTERIZATION/results/stars_recipe_characterization.json`
- Related: C494, C930, C1084, C1085, C1107
