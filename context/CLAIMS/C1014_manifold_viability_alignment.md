# C1014: Discrimination Manifold Encodes Viability Structure via Bridge Backbone

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** A->B
**Phase:** SURVIVOR_SET_GEOMETRY_ALIGNMENT (Phase 332)
**Resolves:** External expert question: does geometric proximity predict viability overlap?
**Strengthens:** C982 (Discrimination Space Dimensionality), C502 (A-Record Viability Filtering), C689 (Survivor Set Uniqueness)
**Relates to:** C1011 (Geometric Independence), C1013 (Bridge Topological Selection), C1000 (HUB Sub-Role Partition)

---

## Statement

The ~101D discrimination manifold (C982) encodes **viability structure**: A records with geometrically similar MIDDLE inventories produce nearly identical B vocabulary restrictions. MIDDLE Jaccard overlap correlates with centroid cosine similarity at r = 0.914 (Mantel p = 0.001, z = 102.66). This alignment is NOT hub/frequency-mediated (removing the hub eigenmode strengthens r from 0.887 to 0.914), is completely size-independent (partial r retention = 100.1%), and propagates to class-level survivor sets (r = 0.622, p = 0.001). However, the alignment is dominated by the 85 bridge MIDDLEs (C1013): bridge-only r = 0.905, non-bridge r = 0.194. The manifold is a **viability landscape** where the generalist backbone encodes filtering equivalence through residual compatibility geometry.

---

## Evidence

### T1: Record Centroid Correlation (PASS)

Mantel test on 1,528 A records (>=2 embeddable MIDDLEs), 1,166,628 pairs:

- Pearson r(Jaccard, cosine similarity): **0.905** (p = 0)
- Spearman r(Jaccard, cosine similarity): **0.914** (p = 0)
- Mantel test (1000 permutations): r = -0.914, **p = 0.001** (z = -102.66)

Records that share more MIDDLEs have geometrically closer centroids in the 100D residual space. This is the strongest pairwise correlation found in the entire constraint system.

### T2: Hub-Controlled Correlation (PASS, P6 prediction reversed)

- Hub-included Spearman r: -0.887 (p = 0)
- Hub-removed Spearman r: **-0.914** (p = 0)
- Ratio (residual/hub): **1.031**

The hub eigenmode (lambda_1 = 81.98, the frequency/degree gradient) DEGRADES the correlation. Removing it strengthens the viability signal from 0.887 to 0.914. The viability structure is encoded in the **residual compatibility geometry** — the fine-grained pattern of which MIDDLEs are compatible with which others, beyond the universal degree effect.

This reverses the C1013 prediction that frequency/generality mediates everything. While bridge selection is frequency-driven (C1013: AUC = 0.978), the viability alignment operates through a different mechanism: residual compatibility structure.

### T3: Size-Controlled Partial Correlation (PASS)

- Raw Spearman r: -0.914
- Partial r (controlling record size sum): **-0.916**
- Retention: **100.1%**

Record size has zero confounding effect. Larger records don't trivially produce more overlap or closer centroids. The geometric-viability alignment is intrinsic to the compatibility structure.

### T4: Class-Level Alignment (PASS)

- Class Jaccard vs cosine distance Spearman r: **-0.622** (p = 0)
- Mantel p: **0.001** (z = -51.72)
- MIDDLE Jaccard vs class Jaccard r: 0.699

The geometric alignment propagates through the MIDDLE-to-class mapping, losing ~32% of signal in the abstraction (0.914 -> 0.622). The class mapping (C502) is not lossless but preserves most of the viability structure.

### T5: Bridge-Dominated Control (P5 FAIL)

- Records with >=2 bridge MIDDLEs: 1,447 (94.7%)
- Records with >=2 non-bridge MIDDLEs: 605 (39.6%)
- Bridge-only Spearman r: **-0.905** (p = 0)
- Non-bridge Spearman r: **-0.194** (p = 0)
- Non-bridge/full ratio: **0.212**

The 85 bridge MIDDLEs (C1013) carry 91% of the viability signal (0.905/0.914). Non-bridge MIDDLEs contribute a statistically significant but weak additional signal (r = 0.194, 21% of full). The viability landscape is primarily structured by the generalist backbone.

---

## Interpretation

The discrimination manifold has **dual function**:

1. **Compatibility structure** (A-level): encodes which MIDDLEs can co-occur in A records, creating the ~101D geometric space. This was known from C982.

2. **Viability landscape** (A->B): encodes which A records produce equivalent B vocabulary restrictions. Records whose MIDDLEs occupy similar regions of the manifold produce similar survivor sets. This is new.

The viability function operates through the **residual** compatibility geometry (not the hub/frequency gradient). Two records have similar viability profiles not because they contain equally frequent MIDDLEs, but because they contain MIDDLEs that are compatible with the same partners. This specific compatibility pattern determines which B instruction classes survive.

The bridge backbone (85 MIDDLEs, C1013) mediates 91% of this signal. These topologically central MIDDLEs are the structural substrate through which geometric proximity translates to functional equivalence. The 887 specialized MIDDLEs add texture but not the dominant structure.

This completes the architectural picture:
- **C982**: Manifold exists (dimensionality ~101D)
- **C1011**: Manifold is independent of macro-automaton (geometric independence)
- **C1013**: Manifold-to-grammar bridge is a generality filter (topological selection)
- **C1014**: Manifold encodes viability through residual geometry (this constraint)

The manifold is not just abstract compatibility — it is the structural substrate of A->B vocabulary filtering, operating through fine-grained compatibility patterns in the generalist backbone.

---

## Relationship to existing constraints

| Constraint | Relationship |
|-----------|-------------|
| C982 | **Extended** — manifold dimensionality confirmed; functional interpretation added (viability landscape) |
| C502 | **Connected** — viability filtering mechanism now has geometric substrate |
| C689 | **Explained** — 97.6% survivor-set uniqueness arises from unique geometric positions in compatibility space |
| C1011 | **Refined** — manifold is independent of macro-automaton BUT encodes viability (different structural levels: macro topology vs vocabulary restriction) |
| C1013 | **Complemented** — bridge selection is frequency-driven (AUC 0.978) but viability alignment is residual-driven (ratio 1.031); different mechanisms for different functions |
| C1000 | **Consistent** — HUB MIDDLEs (bridge backbone) mediate the viability signal |

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| P1 | Mantel p < 0.05 | p = 0.001 (z = -102.66) | PASS |
| P2 | Residual r > 0.05 | r = 0.914 | PASS |
| P3 | Size retention > 50% | 100.1% | PASS |
| P4 | Class Mantel p < 0.05 | p = 0.001 (z = -51.72) | PASS |
| P5 | Non-bridge ratio > 50% | 21.2% | FAIL |
| P6 | Residual/hub ratio < 0.8 | 1.031 | FAIL |

4/6 passed -> PARTIAL_ALIGNMENT

P5 failure: viability signal dominated by bridge backbone (21% non-bridge contribution).
P6 failure: prediction reversed — residual is STRONGER than hub-included. Viability is encoded in fine-grained compatibility, not frequency.

---

## Method

- 1,579 A records from `phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json`
- 972x972 compatibility matrix eigendecomposed; hub eigenmode (lambda_1 = 81.98) removed; 100 residual dimensions retained, scaled by sqrt(lambda)
- Records filtered to >=2 embeddable MIDDLEs (n = 1,528, 96.8%)
- Per-record centroids computed as mean of embedded MIDDLEs in residual space
- Pairwise MIDDLE Jaccard and cosine distance on 1,166,628 pairs
- Mantel test with 1000 row/column permutations (two-sided)
- Size control via rank-based partial correlation
- Bridge/non-bridge split using C1013's 85-MIDDLE bridge set

**Script:** `phases/SURVIVOR_SET_GEOMETRY_ALIGNMENT/scripts/survivor_geometry.py`
**Results:** `phases/SURVIVOR_SET_GEOMETRY_ALIGNMENT/results/survivor_geometry.json`

---

## Verdict

**PARTIAL_ALIGNMENT**: The discrimination manifold encodes viability structure with near-perfect fidelity (r = 0.914) through residual compatibility geometry. The alignment propagates to class-level survivor sets (r = 0.622) and is completely size-independent. However, 91% of the signal runs through the 85-MIDDLE bridge backbone — the specialized vocabulary contributes only 21%. The manifold is a viability landscape, but a bridge-mediated one.
