# OPS-6.A: Human-Navigation Compensation Analysis

**Generated:** 2026-01-04T22:49:33.717379

---

## T1: Human-Track Density vs Navigation Difficulty

### Hypothesis
> When retreat paths are long, human-track markers become more dense.

### Results

| Metric | Value |
|--------|-------|
| Spearman rho (density) | -0.1896 |
| p-value (density) | 0.0861 |
| Spearman rho (diversity) | 0.2771 |
| Effect size | -1.755 |
| N folios | 83 |

**Status:** NOT_SUPPORTED

**Interpretation:** Correlation rho=-0.1896 (p=0.0861); negative relationship

---

## T2: Human-Track Role Shift in Trap Regions

### Hypothesis
> Trap regions show different human-track profiles than safe regions.

### Partition

| Region | Count | Mean Density | Mean Diversity |
|--------|-------|--------------|----------------|
| Safe | 74 | 0.8484 | 0.3319 |
| Trap | 9 | 0.8246 | 0.3359 |

**Density Effect Size:** -0.597

**Status:** NOT_DETECTED

**Interpretation:** Trap regions (n=9): density effect=-0.597, diversity effect=0.036

---

## T3: LINK-Phase Cognitive Load Proxy

### Hypothesis
> Long waits in trap regions are more heavily annotated.

### Results

| Metric | Safe | Trap |
|--------|------|------|
| N folios | 74 | 9 |
| Mean max run | 60.36 | 45.33 |
| Mean avg run | 7.1 | 6.1 |

**Effect Size:** -0.539

**Status:** NOT_SUPPORTED

**Interpretation:** Trap regions show shorter wait annotations (d=-0.539)
