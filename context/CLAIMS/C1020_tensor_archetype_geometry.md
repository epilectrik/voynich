# C1020: Tensor Archetype Geometry — Tensor Factors Encode Dynamics Through Graded Curvature, Not Macro-State Clustering

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** TENSOR_ARCHETYPE_GEOMETRY (Phase 343)
**Extends:** C1019 (tensor-automaton orthogonality confirmed at archetype and HUB levels)
**Strengthens:** C1010 (macro-automaton not a variance artifact), C1016 (bridge degeneracy confirmed: 100% B MIDDLEs are bridges)
**Relates to:** C1000 (HUB sub-roles), C1013 (bridge = frequency selection), C1017 (dynamical variance decomposition)

---

## Statement

The rank-8 CP tensor factors (C1019) encode folio dynamics through **graded curvature** — continuous correlations with AXM attractor strength (rho up to 0.738) — rather than through discrete macro-state or archetype clustering. Three findings:

**A. Tensor factors are deeply correlated with dynamics but don't cluster by archetype.** 7/8 CP factors correlate with AXM self-transition at |rho| > 0.40 (best: Factor 2, rho=-0.738, p<0.0001). Archetypes explain 32.8% of CP factor variance (eta²), but silhouette is negative (-0.040) and k-means ARI is only 0.124. The tensor encodes dynamics as a continuous gradient, not as 6 discrete clusters.

**B. All B corpus MIDDLEs are bridge MIDDLEs (100% coverage).** The bridge/non-bridge partition is completely degenerate in Currier B, confirming C1016 (bridge density ~1.0) and C1013 (bridge selection by frequency, AUC=0.978). The bridge concept distinguishes A→B crossover vocabulary, not a B-internal partition.

**C. HUB MIDDLEs carry simpler transition structure (effective rank 3 vs full rank 8).** HUB-restricted factorization achieves 91.5% variance at rank 3, while the full tensor requires rank 8 for 97%. Neither HUB nor non-HUB restriction recovers macro-state structure (ARI=0.072 and 0.025 respectively). HUB PREFIX factors are LESS channeled than average (entropy 1.024 vs 0.851) — consistent with HUB MIDDLEs being universal connectors (C1000) that appear with diverse PREFIXes.

---

## Evidence

### Sub-A: Factor Trajectory Geometry

**A1: Silhouette score (FAIL but informative)**
- Silhouette: -0.040 (below 0.15 threshold)
- Null (1000 permutations): mean=-0.170, std=0.034
- z=3.81, p<0.0001 — significantly above random
- Archetypes impose non-random structure on CP space, but not compact clusters

**A2: MANOVA variance comparison (FAIL)**
- Archetype mean eta²: 0.328
- REGIME mean eta²: 0.224
- Ratio: 1.47x (below 2x threshold)
- Archetypes explain ~33% of CP variance — substantial but not dominant

**A3: AXM correlation (PASS — strongest finding)**

| Factor | Spearman rho | p-value |
|--------|-------------|---------|
| 0 | +0.498 | <0.0001 |
| 1 | -0.565 | <0.0001 |
| **2** | **-0.738** | **<0.0001** |
| 3 | -0.011 | 0.925 |
| 4 | +0.545 | <0.0001 |
| 5 | +0.611 | <0.0001 |
| 6 | -0.649 | <0.0001 |
| 7 | +0.544 | <0.0001 |

7/8 factors have |rho| > 0.40. Factor 2 alone explains ~54% of AXM variance (rho²=0.545). This confirms and explains C1019's ΔR²=0.465 — the tensor factors encode the AXM attractor basin shape as a continuous multidimensional gradient.

**A4: k-means recovery (FAIL)**
- ARI (k=6 k-means vs archetype labels): 0.124 (below 0.15)
- Near threshold; archetypes are partially but not cleanly recoverable

### Sub-B: HUB vs Non-HUB Factorization

**Bridge degeneracy finding:**
- B corpus unique MIDDLEs: 85
- Bridge MIDDLEs in corpus: 85 (100%)
- Non-bridge MIDDLEs in corpus: 0
- Bridge/non-bridge partition replaced with HUB (23 MIDDLEs) vs non-HUB (62 MIDDLEs)

**B1: HUB class ARI (FAIL)**
- HUB ARI vs C1010: 0.072 (below 0.15)
- Neither HUB nor full tensor recovers macro-states

**B2: Non-HUB class ARI (PASS)**
- Non-HUB ARI: 0.025 < 0.10
- Non-HUB MIDDLEs carry even less macro-state information

**B3: HUB effective rank (PASS)**

| Rank | Variance Explained |
|------|--------------------|
| 3 | 91.5% |
| 4 | 95.2% |
| 5 | 96.9% |
| 6 | 97.5% |

HUB transition structure is rank-3 sufficient (vs rank-8 for full tensor). The 23 HUB MIDDLEs mediate a simpler interaction space — consistent with their role as universal high-frequency connectors (C1000).

**B4: PREFIX factor entropy (FAIL)**
- Full entropy: 0.851
- HUB entropy: 1.024 (higher, not lower)
- HUB MIDDLEs are LESS PREFIX-channeled — they appear with diverse PREFIXes because they're universal connectors

---

## Interpretation

This phase establishes that the tensor-automaton orthogonality (C1019) holds at every tested resolution:

1. **At the archetype level:** Tensor factors don't cluster into 6 archetypes, even though they explain 33% of archetype variance and correlate deeply with dynamics (rho up to 0.738).

2. **At the bridge level:** 100% bridge coverage makes bridge/non-bridge meaningless in B. The bridge concept is an A→B crossover marker, not a B-internal partition.

3. **At the HUB level:** HUB restriction reveals simpler structure (rank 3 vs 8) but doesn't recover macro-states. HUB MIDDLEs are PREFIX-diverse, not PREFIX-channeled.

The conceptual picture:
- **Tensor (C1019)** = continuous dynamical curvature landscape (rank 8, graded)
- **Macro-automaton (C1010)** = discrete topological constraint skeleton (6 states, binary)
- **Archetypes (C1016)** = folio-level dynamical personalities (6 types, categorical)

These three compressions capture different aspects of the same system. The tensor is the most dynamically informative (Factor 2 alone: rho=-0.738) but organized as a continuous gradient, not as discrete categories.

---

## Relationship to existing constraints

| Constraint | Relationship |
|-----------|-------------|
| C1019 | **Extended** — tensor-automaton orthogonality confirmed at archetype level (sil=-0.040) and HUB level (ARI=0.072) |
| C1010 | **Strengthened** — not a variance artifact; macro-states are topological, not spectral |
| C1016 | **Confirmed** — bridge degeneracy: 100% B MIDDLEs are bridges; archetype labels partially structure CP space (eta²=0.328) |
| C1013 | **Confirmed** — bridge = B vocabulary (0% non-bridge in corpus) |
| C1000 | **Extended** — HUB MIDDLEs mediate simpler transition structure (rank 3 vs 8) and are PREFIX-diverse (entropy 1.024 > 0.851) |
| C1017 | **Explained** — ΔR²=0.465 arises from continuous factor-dynamics correlations (7/8 factors at |rho|>0.40), not discrete macro-state recovery |

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| A1 | Archetypes cluster in CP space (silhouette > 0.15) | Sil=-0.040 (z=3.81 vs null) | FAIL |
| A2 | Archetypes > 2x REGIME in CP variance | 1.47x | FAIL |
| A3 | AXM attractor loads on specific CP factors (|rho| > 0.40) | rho=-0.738 | PASS |
| A4 | CP space independently recovers archetypes (ARI > 0.15) | ARI=0.124 | FAIL |
| B1 | HUB class ARI > 0.15 vs C1010 | ARI=0.072 | FAIL |
| B2 | Non-HUB ARI < 0.10 | ARI=0.025 | PASS |
| B3 | HUB tensor lower effective rank | Rank 3 (vs 8) | PASS |
| B4 | HUB PREFIX factors more channeled | Entropy 1.024 > 0.851 | FAIL |

3/8 passed → TENSOR_GEOMETRY_ORTHOGONAL

---

## Method

- 16,054 Currier B tokens mapped to 49 classes, 85 unique MIDDLEs (all bridges)
- Full tensor T[20, 10, 5, 49] with 13,315 bigrams from C1019
- Rank-8 non-negative CP via tensorly (300 iterations, tol=1e-6)
- Per-folio 8D tensor personality: token-weighted centroid of PREFIX×BIN×SUFFIX factor loadings
- 72 folios aligned with C1016 archetype labels (6 archetypes) and REGIME labels (4 REGIMEs)
- Silhouette score with 1000-permutation null model
- Per-dimension ANOVA eta² for archetype and REGIME groups
- Spearman correlation: 8 CP factor scores vs AXM self-transition
- k-means (k=6, 20 initializations) with ARI vs archetype labels
- HUB/non-HUB partition: 23 HUB MIDDLEs (C1000) vs 62 non-HUB MIDDLEs
- HUB rank sweep: NTF at ranks 3-9

**Script:** `phases/TENSOR_ARCHETYPE_GEOMETRY/scripts/tensor_archetype_geometry.py`
**Results:** `phases/TENSOR_ARCHETYPE_GEOMETRY/results/tensor_archetype_geometry.json`

---

## Verdict

**TENSOR_GEOMETRY_ORTHOGONAL**: Tensor factors encode folio dynamics through continuous graded curvature (Factor 2 rho=-0.738 with AXM), not through macro-state clustering (ARI=0.053) or archetype separation (silhouette=-0.040). 100% bridge degeneracy confirmed. HUB MIDDLEs carry simpler structure (rank 3 vs 8) but are PREFIX-diverse (universal connectors). The macro-automaton, tensor factors, and archetypes are three orthogonal compressions of the same system: topological (constraint), spectral (variance), and categorical (dynamics) respectively.
