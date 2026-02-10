# FL_DUAL_STATE_INVESTIGATION Phase

**Date:** 2026-02-09
**Status:** IN PROGRESS (Phase 3: Attractor Model)
**Tier:** 2-3 (Structural Refinement + Interpretation)
**Scripts:** 42 (01-42)

---

## Objective

Investigate whether the FL positional gradient (C777) masks a dual-state system,
and if so, characterize the full architecture of FL-based state indexing in
Currier B text.

## Motivating Evidence

- 12/15 FL MIDDLEs show negative kurtosis (-0.6 to -1.4) -- bimodal
- Line-level concordance only 56.2% (barely above chance)
- Section T shows NO gradient (rho=0.188, p=0.60)
- Context-dependent positions (~10pp shift by preceding token role)
- C773 hazard/safe split: 0.546 vs 0.811

---

## Phase Arc (3 stages)

### Stage 1: Bimodality Investigation (Scripts 01-11)

**Question:** Is the FL bimodality real or artifact?

**Verdict: DUAL_STATE (HIGH confidence)**

| # | Script | Verdict | Key Finding |
|---|--------|---------|-------------|
| 01 | line_length_artifact | REAL | Bimodality persists in all length bins (11/12 bimodal) |
| 02 | context_stratified_kurtosis | INTRINSIC | 12/12 MIDDLEs bimodal after context stratification |
| 03 | positional_anchoring_taxonomy | WEAK_PARTITION | 1 RIGID, 11 FLEXIBLE, 3 MODERATE |
| 04 | section_t_anomaly | SAMPLE_SIZE | T's gradient failure = small sample (50.6% random fail at n=188) |
| 05 | multi_fl_subsequences | WEAK_PATTERNS | Within-line forward:backward = 1.3:1 (vs 5:1 global) |
| 06 | residual_regression | PARTIAL | R2=0.337, 9/15 MIDDLEs remain bimodal after regression |
| 07 | gaussian_mixture | DUAL_STATE | 12/12 (100%) prefer 2-component GMM, all well-separated |
| 08 | forward_bias_decomposition | SUBTYPE_DRIVEN | Forward bias varies >3x across hazard classes |
| 09 | hazard_safe_bimodality | INDEPENDENT | 11/12 bimodal within hazard/safe classes |
| 10 | prefix_fl_mode_interaction | PREFIX_SELECTS | PREFIX shifts FL position for 82% of MIDDLEs |
| 11 | integrated_verdict | **DUAL_STATE** | Dual score=4, Artifact=0, Context=1 |

**Conclusion:** FL bimodality is real and intrinsic. Each FL token occupies one of
two modes (LOW or HIGH) determined by line position and PREFIX. The two modes
correspond to the inner vs outer layers of a nested line architecture.

### Stage 2: Nesting Architecture (Scripts 12-30)

**Question:** What IS the dual-state structure? How does it organize the line?

| # | Script | Verdict | Key Finding |
|---|--------|---------|-------------|
| 12 | mode_clustering | (Data) | 3 prefix clusters; TERMINAL/FINAL peak at 1.0 |
| 13 | mode_separated_transitions | PARTIALLY_COHERENT | Forward bias within modes (LOW=1.9:1, HIGH=2.0:1) |
| 14 | cross_line_mode_dynamics | LINE_LEVEL_RESET | HIGH->LOW reset rate = 77% at line boundaries |
| 15 | prefix_mode_selection | PREFIX_DETERMINES_MODE | LOW-biased: sh, qo, so, do, po, to; HIGH-biased: ol, ka, ar, or, ko |
| 16 | kernel_gap_analysis | NO_CORRELATION | Gap kernel composition does not vary with stage |
| 18 | paragraph_synchronization | NO_SYNC | No paragraph-level FL synchronization |
| 19 | stage_operator_profiles | VOCABULARY_DIVERGENCE | Stage vocabularies differ (Jaccard 0.16-0.59) but role distribution uniform |
| 20 | mode_pair_semantics | PAIR_CARRIES_MEANING | LOW+HIGH pair encodes info beyond either alone (MI=0.144, p=0.001) |
| 21 | pair_coherence | NO_PAIR_COHERENCE | Same-pair lines no more similar than random (Jaccard lift=1.36, p=0.086) |
| 22 | near_fl_morphology | (Data) | Layer structure: 582 outer left, 1589 center, 582 outer right |
| 23 | layer_class_mapping | CLASS_STRATIFIED | Classes preferentially occupy specific layers (V=0.228, p<0.001) |
| 24 | hierarchical_readthrough | COMPLETE | 20 lines manually annotated through full nesting model |
| 25 | frame_predicts_center | WEAK | Some frame->center association but not strong (NMI=0.305) |
| 26 | bimodality_is_nesting | **CONFIRMED** | Bimodality = nesting roles (3/4 checks pass) |
| 27 | pre_post_fl_analysis | FOURTH_LAYER | Pre/post FL tokens distinct from center (V=0.521) |
| 28 | paragraph_nesting_structure | WEAKLY_STRUCTURED | Some organization but not strong (2/6 signals) |
| 29 | pair_grid_vocabulary | **MATERIAL_STATE_GRID** | FL pair grid carves vocabulary along gradient (3/4 checks) |
| 30 | operator_navigation | **DISTRIBUTED** | FL tags are in-page navigation; each folio covers many states |

**Conclusion:** FL bimodality = nesting. Each line has a 7-layer architecture:

```
[PREAMBLE] [FL-LOW] [OL] ... CENTER ... [OR] [FL-HIGH] [CODA]
```

The FL pair (LOW, HIGH) functions as a 2D coordinate on a state grid.
Nearby OL/OR tokens add continuous addressing. Together they predict 52.1%
of center content. The FL pair grid represents MATERIAL_STATE indexing.

### Stage 3: State Machine Architecture (Scripts 31-42)

**Question:** How does the state grid organize folios, paragraphs, and lines?

| # | Script | Verdict | Key Finding |
|---|--------|---------|-------------|
| 31 | coordinate_space_mapping | (Profiles) | LOW=ACTION_INTENSITY (qo rho=+0.738), HIGH=OVERSIGHT_LEVEL (ok rho=+0.569, sh rho=-0.463) |
| 32 | fl_middle_partition | (Profiles) | 3 HIGH-dominant (i, in, am), 1 LOW-dominant (y), 8 DUAL; all FLOATERS |
| 33 | coordinate_determinants | MIXED | Folio primary (V=0.302), line order irrelevant (rho~0), adjacent lift=1.35x |
| 34 | four_coordinate_test | PARTIAL_COORDINATES | FL pair + OL/OR predict 52.1% of center (3/5 checks) |
| 35 | azc_nesting_correspondence | WEAK_SIGNAL | AZC organizes coordinate vocabulary, not line structure (2/5) |
| 36 | azc_venn_test | NO_VENN | Two-wheel model rejected; weak S1/S2 L/R asymmetry (p=0.027) |
| 37 | full_line_readthrough | (Narrative) | 15 lines annotated; OL=monitor 40%, OR=action 27%; center heterogeneous |
| 38 | folio_progression | **GRID_PATCH** | 97% of folios fill grid patches, not diagonals; universal arc MEDI->TERM |
| 39 | paragraph_state_coherence | **STRUCTURAL_ONLY** | Paragraphs orthogonal to state grid (within=between distance, d=-0.012) |
| 40 | paragraph_zone_fl_test | **ZONE_SPECIFIC_FL** | FL system specific to body lines (5/5); header 45% vs body 56% coordination |
| 41 | tail_reset_test | PARTIAL_RESET | Tail centers state toward LATE/MEDIAL (rho=+0.390); not full zero-reset |
| 42 | attractor_state_test | **ATTRACTOR_MODEL** | (LATE,LATE) is attractor; 100% convergent flow; rho=+0.881 distance vs correction |

---

## Integrated Model

### The Line = State-Indexed Instruction

```
[PREAMBLE] [FL-LOW] [OL] ... CENTER ... [OR] [FL-HIGH] [CODA]
```

- **FL-LOW**: Discrete ACTION_INTENSITY coordinate (INITIAL -> TERMINAL)
- **FL-HIGH**: Discrete OVERSIGHT_LEVEL coordinate (INITIAL -> TERMINAL)
- **OL/OR**: Continuous semi-coordinate dimensions
- **CENTER**: Operational content (qo/sh/ch/ok control loop)
- 4 coordinates together predict **52.1%** of center content

The FL coordinate tells you WHERE on the state grid this instruction applies.
The center content tells you WHAT to do there (sense, act, check).

### The Paragraph = Self-Contained Operation Type

- **HEADER** (line 1): Specification/setup. Less FL-dependent (21.2% FL, 45% coordinated).
- **BODY** (middle lines): State-indexed instructions. FL most active (26.2% FL, 56.2% coordinated).
- **TAIL** (last line): State centering. Pulls toward LATE/MEDIAL for handoff (rho=+0.390).

Paragraphs are **orthogonal to the state grid** (within-para distance = between-para distance).
They organize by OPERATION TYPE, not by state. Each paragraph's body spans multiple states.

Established: PARALLEL_PROGRAMS (C855), not sequential. Spec->exec gradient (C932) governs
vocabulary complexity within a paragraph, not state coordinates.

### The Folio = State Coverage Table (Control Program)

- Covers a contiguous **GRID_PATCH** of the (action, oversight) space (97%)
- Contains ~7 paragraphs (independent mini-programs)
- Lines unordered by state (rho~0) -- it's a **lookup table**, not a narrative
- Folio identity is the primary state determinant (V=0.302)

### The Attractor = (LATE, LATE)

- **Most frequent state**: 16.2% of all coordinated lines
- **100% convergent flow**: Every state's mean transition vector points toward (LATE, LATE)
- **Distance predicts correction**: rho=+0.881 (farther states shift more toward center)
- **Stability gradient**: 22.3% self-transition at attractor vs 0% at INITIAL/EARLY
- **Universal operating envelope**: MEDI->TERM band (9 states in >40% of folios)

Lines at (LATE, LATE) = maintenance mode (stay put).
Lines away from (LATE, LATE) = error correction (pull back toward center).
The farther from the attractor, the stronger the correction.

### The Control Loop

Within each line, the qo/sh/ch/ok prefix system implements the feedback mechanism:

| Distance from attractor | Character |
|------------------------|-----------|
| NEAR (0-1) | Maintenance: qo=25.4%, balanced sensing/checking |
| FAR (2-3) | Correction: slightly more corrective, less monitoring |
| EXTREME (3+) | Full correction: ok rises to 9.0%, sh drops to 12.7% |

The control loop MIX is similar everywhere (content gradient is weak, rho=-0.058),
but the FL INTENSITY SETTING changes -- the same loop runs harder or softer
depending on distance from the setpoint.

---

## Key Constraints This Phase Builds On

- C777: FL state index (global gradient) -- REFINED to 2D coordinate
- C773: FL hazard-safe position split -- shown INDEPENDENT of bimodality
- C786: Forward bias (5:1) -- shown SUBTYPE_DRIVEN (hazard=4.81, safe=0.44, other=1.03)
- C787: State reset prohibition
- C770-C776: FL primitive architecture
- C855: Paragraphs are PARALLEL_PROGRAMS
- C932: Paragraph spec->exec gradient
- C357: Lines are deliberately chunked

## Potential New Constraints (pending registration)

| Finding | Proposed Tier | Key Evidence |
|---------|--------------|--------------|
| FL bimodality = nesting (LOW/HIGH modes) | Tier 2 | 100% GMM dual, PREFIX selects mode |
| 7-layer line architecture | Tier 2 | PREAMBLE/FL-LOW/OL/CENTER/OR/FL-HIGH/CODA |
| FL pair = 2D state coordinate (ACTION x OVERSIGHT) | Tier 2 | rho=+0.738 (qo), rho=-0.463 (sh) |
| 4-coordinate addressing (FL + OL/OR) predicts 52.1% | Tier 2 | Conditional entropy reduction |
| Folio = GRID_PATCH (state coverage table) | Tier 2 | 97% GRID_PATCH, rho~0 line order |
| Paragraph orthogonal to state grid | Tier 2 | within=between distance, d=-0.012 |
| HEADER/BODY/TAIL FL specialization | Tier 2 | 5/5 checks, body 56.2% vs header 45.0% |
| Tail centering toward LATE/MEDIAL | Tier 2 | rho=+0.390 proportional reset |
| (LATE,LATE) attractor with convergent flow | Tier 2 | 100% convergent, rho=+0.881 |
| AZC organizes coordinate vocabulary, not line structure | Tier 2 | S-series 3.06x at FL bookends |

---

## Files

- `scripts/01-42`: Python test scripts (each produces JSON)
- `results/01-42`: JSON results (one per script)
- Script 17 (line_inspector) has no JSON output (interactive/visual tool)

## Dependencies

- `scripts/voynich.py` (Transcript, Morphology)
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (token roles)
- `sklearn.mixture.GaussianMixture` (GMM fitting)
- `scipy.stats` (statistical tests throughout)
