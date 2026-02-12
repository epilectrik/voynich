# C1000: HUB_UNIVERSAL Decomposes Into Functional Sub-Roles

**Tier:** 2 | **Scope:** B | **Phase:** HUB_ROLE_DECOMPOSITION | **Date:** 2026-02-11

## Statement

HUB_UNIVERSAL (Bin 6) is structurally decomposable into four functional sub-roles despite behavioral homogeneity on affordance signatures. The 23 HUB MIDDLEs partition into HAZARD_SOURCE (6), HAZARD_TARGET (6), SAFETY_BUFFER (3), and PURE_CONNECTOR (8) based on forbidden transition participation and safety buffer duty. Sub-roles are behaviorally homogeneous (0/14 dimensions significant on Kruskal-Wallis) but functionally distinct: PREFIX creates dramatic lane separation (chi²=12957, Cramér's V=0.689), safety buffers are 3.8x qo-enriched (Fisher p=0.012), and regime clustering reveals 4 sub-populations (silhouette=0.398 at k=4).

## Evidence

### T1: Sub-Role Partition
- 23 HUB MIDDLEs classified by forbidden pair participation + safety buffer duty
- Sub-roles: HAZARD_SOURCE [ar, dy, ey, l, ol, or], HAZARD_TARGET [aiin, al, ee, o, r, t], SAFETY_BUFFER [eol, k, od], PURE_CONNECTOR [d, e, eey, ek, eo, iin, s, y]
- Overlap: `l` and `ol` serve all three hazard roles simultaneously
- Behavioral signature comparison: 0/14 dimensions significant (HOMOGENEOUS on affordance profiles)
- Token-level lane distributions differ dramatically: SAFETY_BUFFER 81.6% QO, HAZARD_TARGET 65.4% NEUTRAL

### T2: PREFIX Differentiation Within HUB
- Lane chi²=12957 (p≈0), Cramér's V=0.689 (strong association)
- qo PREFIX → 86.5% QO lane; sh PREFIX → 81.2% CHSH lane
- JSD(qo vs sh) = 0.697; JSD(ch vs sh) = 0.011 (ch/sh form grammar pair)
- Safety buffers: 46.7% qo-prefix vs 18.6% baseline (Fisher OR=3.82, p=0.012)

### T3: Forbidden Concentration
- **17/17 forbidden transitions involve HUB MIDDLEs** (corrects C996's 13/17)
- Permutation test: null mean=0.78, observed=17, p=0.0000
- 12/23 HUB MIDDLEs (52.2%) participate in forbidden pairs
- Only 3 non-HUB MIDDLEs participate: c (FLOW_TERMINAL), he (ROUTINE_SPECIALIZED), edy (STABILITY_CRITICAL)

### T4: Internal Structure
- Regime clustering: 4 clusters at silhouette=0.398
  - Cluster 1 (R1-dominant): e, eey, eol, ey, k, l, ol, t
  - Cluster 2 (R3/R4-dominant): d, eo, od
  - Cluster 3 (R2/R4-dominant): dy, ek, o, s
  - Cluster 4 (balanced R2): aiin, al, ar, ee, iin, or, r, y

### T5: Integrated Verdict
- Score: 2.67/4.0 — HUB_DECOMPOSABLE
- 3/4 dimensions show significant sub-structure

## Implications

- **Corrects C996**: All 17/17 forbidden transitions involve HUB, not 13/17
- **Extends C997**: Safety buffer architecture is QO-PREFIX-driven within HUB
- **Confirms C995**: Bin behavioral coherence holds (homogeneous signatures) but functional diversity exists beneath
- HUB_UNIVERSAL is a compatibility carrier that tolerates hazard, provides buffers, and connects everything — its overloaded role reflects functional centrality, not classification error

## Provenance

- `phases/HUB_ROLE_DECOMPOSITION/results/t1_hub_sub_role_partition.json`
- `phases/HUB_ROLE_DECOMPOSITION/results/t2_prefix_bin_interaction.json`
- `phases/HUB_ROLE_DECOMPOSITION/results/t3_cross_bin_forbidden_anatomy.json`
- `phases/HUB_ROLE_DECOMPOSITION/results/t4_hub_compound_position_analysis.json`
- `phases/HUB_ROLE_DECOMPOSITION/results/t5_integrated_verdict.json`
