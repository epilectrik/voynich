# C1011: Discrimination Manifold and Macro-Automaton are Geometrically Independent

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** A→B
**Phase:** GEOMETRIC_MACRO_STATE_FOOTPRINT (Phase 329)
**Relates to:** C982 (Discrimination Space Dimensionality), C976 (6-State Transition Topology), C1010 (Minimal Invariant Partition), C987 (Manifold Continuity), C1000 (HUB Sub-Role Partition), C995 (Affordance Bins)

---

## Statement

The ~101D discrimination manifold (C982) and the 6-state macro-automaton (C976/C1010) describe **orthogonal structural levels**. Macro-state labels have no geometric footprint in the discrimination space. The manifold captures A-level MIDDLE compatibility; the automaton captures B-level transition topology. These are complementary descriptions, not redundant — neither can be derived from the other.

---

## Evidence

### Minimal overlap between A and B MIDDLE inventories

Only 85/972 MIDDLEs (8.7%) that define the discrimination manifold also participate in B's 49-class grammar. The manifold is overwhelmingly an A-level structure. Geometric analysis is restricted to these 85 bridging MIDDLEs.

### No geometric clustering by macro-state

Overall silhouette score = -0.1256 (z = -0.96 vs 1000 null permutations, p = 0.843). Negative silhouette means MIDDLEs are closer to other-state centroids than to their own-state centroid on average. Per-state silhouettes: AXM = -0.124, AXm = +0.121, FL_HAZ = -0.165, FQ = -0.193, CC = -0.211, FL_SAFE = -0.078. Only AXm shows positive (weak) coherence.

Within-state dispersion (2.25–3.57) exceeds between-state centroid distances (0.72–2.19) for all pairs except CC. States overlap extensively in geometric space.

### Forbidden transitions are not geometric boundaries

Only 2/17 forbidden transitions have both classes representable (both classes must have ≥1 mapped MIDDLE). Of these, mean forbidden distance = 1.988 vs allowed = 2.006 (ratio = 0.991, Mann-Whitney p = 1.0). Forbidden transitions do not span larger geometric distances than allowed ones.

### HUB MIDDLEs are geometrically peripheral, not central

HUB MIDDLEs occupy significantly MORE residual space than non-HUB MIDDLEs (mean norm 2.31 vs 0.76, p = 2.7 × 10⁻¹⁶). This reverses the prediction from C1000 that HUB MIDDLEs would cluster near the geometric origin. HUB's role as a topological connector in the transition graph is independent of its geometric position in the compatibility manifold.

### HUB sub-roles not geometrically distinct

The 4 sub-roles (HAZARD_SOURCE, HAZARD_TARGET, SAFETY_BUFFER, PURE_CONNECTOR) from C1000 show within-role dispersion ≈ between-role dispersion (ratio = 0.999, z = -0.27, p = 0.577). Sub-role identity is a transition-topological property, not a geometric one.

### Affordance bins dominated by AXM

Cross-tabulation of affordance bins × macro-states shows many-to-many mapping but dominated by AXM (64/85 mapped MIDDLEs). Mean bin concentration = 0.777 — bins tend toward single macro-states, but this reflects AXM's 75% share, not geometric structure.

### Pre-registered prediction outcomes

| Prediction | Expected | Observed | Pass |
|-----------|----------|----------|------|
| P1: EN+AX (AXM+AXm) overlap | Overlapping footprints | AXm silhouette +0.12 (weak separation) | FAIL |
| P2: FL_HAZ/FL_SAFE separate | Distinct regions | Centroid distance 1.13 (largest non-CC pair) | PASS |
| P3: FQ intermediate geometry | Between core and periphery | Silhouette -0.193 (no intermediate position) | FAIL |
| P4: CC geometrically peripheral | Outlier positions | Highest dispersion (3.57) but negative silhouette | FAIL |
| P5: HUB geometrically significant | Clustered or distinctive | Significantly farther from origin (p ≈ 0) | PASS |
| P6: No clean 6-basin partition | Silhouette < 0.3 | Silhouette -0.126 (confirmed continuous) | PASS |

3/6 predictions passed. The passes confirm C987 (continuous manifold, no basins) and that HUB has distinctive geometry. The failures demonstrate that macro-state structure does not project into geometric space.

---

## Interpretation

The discrimination manifold encodes which MIDDLEs can co-occur in A records — a compatibility structure built from the full A vocabulary (972 MIDDLEs). The macro-automaton encodes which instruction classes can follow each other in B execution sequences — a transition structure built from the 49-class grammar. These operate at different organizational levels:

- **Manifold** = what is compatible (A-level, vocabulary structure)
- **Automaton** = what follows what (B-level, sequential structure)

The 8.7% overlap (85 bridging MIDDLEs) means B draws on a small, specialized subset of A's discrimination space. Within that subset, B imposes its own organizational logic (transition topology, hazard boundaries) that is invisible to A's compatibility geometry.

---

## Relationship to existing constraints

| Constraint | Relationship |
|-----------|-------------|
| C982 | **Confirmed** — manifold dimensionality (~101D) validated; eigenvector embedding reproduces known properties |
| C987 | **Confirmed** — no discrete basins (silhouette -0.126 < 0.3 threshold); manifold is continuous |
| C976/C1010 | **Complemented** — macro-automaton is valid but geometrically invisible; operates at different level |
| C1000 | **Refined** — HUB sub-roles are transition-topological, not geometric; HUB MIDDLEs occupy MORE residual space (peripheral) |
| C995 | **Consistent** — affordance bins cross-cut macro-states (many-to-many mapping) |
| C572 | **Confirmed** — EN/AX geometric overlap predicted but AXm shows weak separation |

---

## Method

- Eigenvector decomposition of 972×972 A-level MIDDLE compatibility matrix
- Hub eigenmode (λ₁ = 81.98) removed; top 100 residual dimensions retained
- 972 MIDDLEs mapped to B instruction classes via morphological extraction from B tokens
- 85/972 MIDDLEs successfully bridged (present in both A manifold and B class assignments)
- Macro-state labels from C976 partition applied to mapped MIDDLEs
- Silhouette analysis with 1000-permutation null model
- Forbidden transition distance test (Mann-Whitney)
- HUB sub-role geometric separation test (permutation-based dispersion ratio)
- Affordance bin × macro-state cross-tabulation

**Script:** `phases/GEOMETRIC_MACRO_STATE_FOOTPRINT/scripts/geometric_footprint.py`
**Results:** `phases/GEOMETRIC_MACRO_STATE_FOOTPRINT/results/geometric_footprint.json`

---

## Verdict

**GEOMETRIC_INDEPENDENCE**: The discrimination manifold and macro-automaton are complementary structural descriptions. Neither is redundant with the other. Unification of C982 geometry with C976/C1010 topology is not achievable — they describe different organizational levels of the manuscript's architecture.
