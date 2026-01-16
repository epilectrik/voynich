# OPS-6.A: Human-Navigation Compensation Analysis

**Generated:** 2026-01-15T23:48:11.227683

---

## T1: Human-Track Density vs Navigation Difficulty

### Hypothesis
> When retreat paths are long, human-track markers become more dense.

### Results

| Metric | Value |
|--------|-------|
| Spearman rho (density) | -0.1992 |
| p-value (density) | 0.0728 |
| Spearman rho (diversity) | 0.4122 |
| Effect size | -1.696 |
| N folios | 82 |

**Status:** NOT_SUPPORTED

**Interpretation:** Correlation rho=-0.1992 (p=0.0728); negative relationship

---

## T2: Human-Track Role Shift in Trap Regions

### Hypothesis
> Trap regions show different human-track profiles than safe regions.

### Partition

| Region | Count | Mean Density | Mean Diversity |
|--------|-------|--------------|----------------|
| Safe | 73 | 0.8518 | 0.7361 |
| Trap | 9 | 0.8255 | 0.8423 |

**Density Effect Size:** -0.661

**Status:** DETECTED

**Interpretation:** Trap regions (n=9): density effect=-0.661, diversity effect=0.878

---

## T3: LINK-Phase Cognitive Load Proxy

### Hypothesis
> Long waits in trap regions are more heavily annotated.

### Results

| Metric | Safe | Trap |
|--------|------|------|
| N folios | 73 | 9 |
| Mean max run | 26.96 | 18.67 |
| Mean avg run | 7.11 | 6.0 |

**Effect Size:** -0.785

**Status:** NOT_SUPPORTED

**Interpretation:** Trap regions show shorter wait annotations (d=-0.785)
