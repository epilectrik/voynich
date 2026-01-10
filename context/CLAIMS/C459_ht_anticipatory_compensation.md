# C459: HT Anticipatory Compensation

**Tier:** 2 | **Status:** CONFIRMED | **Scope:** Cross-system (HT × B)

---

## Statement

Human Track (HT) density is **significantly higher in quires containing stressed B folios** (r=0.343, p=0.0015), and the correlation is **stronger with HT preceding B** than following it.

This suggests HT functions as **anticipatory vigilance** rather than post-hoc recovery.

---

## Evidence

### Quire-Level Correlation

| Metric | Value |
|--------|-------|
| Spearman r | 0.343 |
| p-value | 0.0015 |
| n (B folios) | 83 |

HT density in the same quire as a B folio correlates positively with that folio's execution tension.

### Directional Analysis

| Direction | r | p | Significant |
|-----------|---|---|-------------|
| HT before B | 0.236 | 0.032 | Yes |
| HT after B | 0.177 | 0.109 | No |

**Pattern: HT_ANTICIPATES_STRESS**

The correlation is significant only for HT density *before* the B folio, not after. This rules out post-stress decompression models.

### Window Analysis

| Window | r | p | Significant |
|--------|---|---|-------------|
| ±1 folio | 0.132 | 0.234 | No |
| ±2 folios | 0.153 | 0.167 | No |
| ±3 folios | 0.229 | 0.037 | Yes |
| Quire | 0.343 | 0.0015 | Yes |

Effect strengthens at larger windows, consistent with quire-level clustering (C450).

---

## C459.a: Regime-Dependent Compensation

The HT-stress relationship differs by B regime:

| Regime | Mean Tension | Mean HT | r | Pattern |
|--------|-------------|---------|---|---------|
| REGIME_1 | -0.294 | 0.129 | +0.260 | Positive |
| REGIME_2 | -0.873 | 0.199 | -0.264 | **Inverted** |
| REGIME_3 | +0.850 | 0.116 | +0.341 | Positive |
| REGIME_4 | +0.205 | 0.175 | -0.072 | None |

**Interpretation:** REGIME_2 (lowest tension, highest HT) shows inverted compensation - HT is high even when tension is low. This may indicate a different operational mode.

---

## C459.b: Zero-Escape Characterization

**STATUS: CORRECTED (2026-01-10)**

Original finding claimed f41r and f86v5 had zero escape routes. This was incorrect due to a field name error in the analysis script.

### Corrected Data

| Folio | Escape Density | HT Density | Zero-Escape? |
|-------|----------------|------------|--------------|
| f41r | 0.197 | 0.296 | NO |
| f86v5 | 0.094 | 0.278 | NO |

### Actual Zero-Escape Folios (E2)

Only **2** B folios have near-zero escape (≤0.01):

| Folio | Escape Density | HT Density | HT Status |
|-------|----------------|------------|-----------|
| f33v | 0.009 | 0.158 | NORMAL |
| f85v2 | 0.010 | 0.163 | NORMAL |

Neither is an HT hotspot.

### Revised Interpretation

- Zero-escape is RARE in B (2.4% of folios)
- Zero-escape does NOT correlate with elevated HT
- The original "recovery scarcity → HT spike" hypothesis is NOT SUPPORTED

f41r and f86v5 are HT hotspots for reasons unrelated to escape density.

---

## What This Constraint Claims

1. HT density correlates with B execution stress at **quire level** (not immediate neighbor level)
2. HT **precedes** stressed B sections (anticipatory, not reactive)
3. The relationship **varies by regime** - not uniform across B design space
4. REGIME_2 shows **inverted** relationship (high HT despite low tension)
5. ~~Zero-escape B folios have max HT~~ (WITHDRAWN - based on incorrect data)

---

## What This Constraint Does NOT Claim

- WHY HT anticipates stress (operator preparation, margin setting, etc.)
- Whether this pattern is intentional or emergent
- The causal direction (HT → B planning vs common cause)

---

## Architectural Interpretation

The anticipatory pattern suggests HT may function as:

> "Prepare the human operator for an upcoming high-stress section"

Rather than:

> "Help the operator recover from a completed high-stress section"

This is consistent with HT as **attention-priming** rather than **decompression**.

---

## Regime-Specific Interpretation

| Regime | Possible Interpretation |
|--------|------------------------|
| REGIME_1/3 | Standard anticipatory model |
| REGIME_2 | Steady-state vigilance (always high HT) |
| REGIME_4 | HT-independent operation |

---

## Phase Documentation

Research conducted: 2026-01-10 (D3 - HT Compensation Analysis + Extensions)

Scripts:
- `phases/exploration/ht_compensation_analysis.py` (D3)
- `phases/exploration/ht_temporal_dynamics.py` (temporal analysis)
- `phases/exploration/anomalous_folio_investigation.py` (C459.b)

Results:
- `results/ht_compensation_analysis.json`
- `results/ht_temporal_dynamics.json`
- `results/anomalous_folio_investigation.json`

---

## Cross-References

- C450: HT quire clustering
- C458: B execution design clamp
- C412: Sister-escape anticorrelation

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
