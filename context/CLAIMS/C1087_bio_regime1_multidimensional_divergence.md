# C1087: Bio-REGIME_1 Multidimensional Divergence

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** BIO_DOMAIN_DISTINCTIVENESS (Phase 385)
**Extends:** C553 (BIO-REGIME energy independence), C1048 (Bio LOO R2=0.754)
**Strengthens:** C1084 (section-AXM ordering), C1029 (section-parameterized grammar weights)
**Relates to:** C609 (LINK density), C190 (LINK-CEI inverse), C876 (LINK checkpoint function), C458 (design asymmetry)

---

## Statement

Bio REGIME_1 folios (n=20) diverge from non-Bio REGIME_1 folios (n=12) on 6 of 8 tested dimensions: k%, h%, e%, LINK%, hazard density, and AXM self-transition rate. Lane balance (QO%, CHSH%) is NOT significantly different. Bio is a distinct operational mode within REGIME_1, not a subset of it. This explains C1048's finding that Bio is dynamically coherent (LOO R2=0.754) — it occupies a distinct, tight region of the REGIME_1 parameter space.

---

## Evidence

### Dimensional Comparison (Mann-Whitney U)

| Dimension | Bio-R1 | Non-Bio-R1 | U | p | Sig |
|-----------|--------|------------|---|---|-----|
| k kernel% | 34.25% | 28.82% | 174 | 0.037 | * |
| h kernel% | 8.91% | 6.79% | 191 | 0.006 | ** |
| e kernel% | 56.84% | 64.39% | 49 | 0.006 | ** |
| QO lane% | 34.34% | 33.89% | 124 | 0.892 | NS |
| CHSH lane% | 25.67% | 27.28% | 95 | 0.340 | NS |
| LINK lane% | 0.63% | 2.81% | 43 | 0.003 | ** |
| Hazard density | 11.69% | 9.42% | 178 | 0.025 | * |
| AXM self-rate | 0.754 | 0.677 | 187 | 0.010 | ** |

6/8 significant. The non-significant dimensions (QO%, CHSH%) indicate that Bio's distinctiveness is NOT about which lanes it uses, but how it enters them (CC trigger routing, per T4) and what it does within them (kernel balance, per C1085).

### LINK Depletion

The most structurally striking dimension: Bio LINK% = 0.63% vs non-Bio REGIME_1 = 2.81% (4.5x depletion). The corpus-wide LINK density is 13.2% (C609). Bio is approximately 20x below corpus average.

Connections:
- C190: LINK inversely correlates with control engagement intensity. Bio's near-zero LINK means near-maximum engagement — these programs almost never pause for monitoring.
- C876: If LINK functions as a checkpoint, Bio's checkpoint depletion means the process does not need periodic assessment pauses.
- C458: Clamped hazard with depleted LINK is consistent with a process that is continuously active but thermally protected — thermal inertia (water bath) prevents apparatus failure, eliminating the need for monitoring pauses.

### AXM Self-Transition Elevation

Bio AXM self-rate = 0.754 vs non-Bio R1 = 0.677. Higher self-transition means Bio programs are more repetitive — they stay in the same macro-state longer. Combined with C1084's section-AXM ordering (B=0.754 highest), this establishes Bio as the most dynamically stable section.

---

## Interpretation

Bio REGIME_1 is a distinct operational mode characterized by: (1) elevated kernel operations (k-enrichment), (2) near-zero monitoring (LINK depletion), (3) elevated hazard awareness (higher hazard density), (4) high dynamic stability (elevated AXM self-rate). This profile describes a continuously-engaged, energy-dominant process that doesn't need monitoring checkpoints. At Tier 3, this is consistent with balneum mariae (water bath): the thermal inertia of the water bath eliminates the need for frequent monitoring (depleted LINK) while requiring continuous energy modulation (k-enriched kernel) and high hazard awareness (the bath must be maintained at temperature).

---

## Method

- 20 Bio REGIME_1 folios vs 12 non-Bio REGIME_1 folios
- 8 dimensions computed per folio: k%, h%, e%, QO%, CHSH%, LINK%, hazard density, AXM self-transition rate
- Mann-Whitney U tests (non-parametric, appropriate for small samples)
- Pre-registered test with falsification criteria

**Script:** `phases/BIO_DOMAIN_DISTINCTIVENESS/scripts/bio_domain_tests.py`
**Results:** `phases/BIO_DOMAIN_DISTINCTIVENESS/results/bio_domain_results.json`

---

## Verdict

**BIO_R1_DIVERGENT**: Bio REGIME_1 diverges from non-Bio REGIME_1 on 6/8 dimensions, establishing it as a distinct operational mode within REGIME_1 — not a generic subset. The LINK depletion (0.63% vs 2.81%) and AXM elevation (0.754 vs 0.677) are the most interpretively productive dimensions, pointing to a continuously-engaged, checkpoint-free, dynamically stable process.
