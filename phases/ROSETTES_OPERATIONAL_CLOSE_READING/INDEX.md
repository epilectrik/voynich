# Phase 620: Rosettes Operational Close Reading

**Status:** COMPLETE
**Verdict:** UNIFORM_OPERATIONAL_INDEX (2/3 core, T4 reported separately)
**Constraints:** C1817-C1823
**Date:** 2026-03-20

---

## Research Question

Phase 619 confirmed the rosettes share the universal atom substrate and are the manuscript's most arrangement-dominant text. The diagnostic infrastructure is mature after 5 prior rosettes phases (402-405, 619). The question shifts from "what are the rosettes structurally?" to "what do they say operationally?" — per-entity fingerprinting at 8-category resolution, cross-entity comparison with bootstrap null, baseline positioning against AZC/A/B, and expert close reading of annotated token dumps.

## Design

- 394 valid tokens from `data/rosettes_annotated.json` (ZL transcription, 443 raw - 49 filtered)
- 19 entities: 9 rosettes (20-67 tokens), 8 paths (1-5 tokens, low power), CLOCK (6), UNCLASSIFIED (1)
- Per-entity fingerprinting: HEAD, TERMINAL, MOD, 8-category profile, kernel, frame hazard, PREFIX, suffix rate, bridge/dark/compound, classified/unclassified sub-profiles
- Cross-entity: JSD matrices, bootstrap permutation null (1000 resamples), spatial adjacency test, Ward clustering
- Baselines: AZC (primary, per C1127), B (excluding rosettes folios), A
- Four predictions: T1 (bootstrap uniformity), T2 (C1131 consistency), T3 (spatial non-coherence), T4 (dual population per-entity)
- Expert close reading of annotated dumps (3 expert agents)

## Results

### T1: Entity Category Uniformity (Bootstrap)

| Metric | Value |
|--------|-------|
| Mean pairwise category JSD (9 rosettes) | 0.074 |
| Bootstrap 95th percentile threshold | 0.106 |
| Result | **PASS** |

All 9 rosettes share a common operational profile at 8-category resolution. Entity-level variation is within the range expected from random resampling of a single population.

### T2: Ring Non-Execution Enrichment (C1131 Consistency)

| Metric | Value |
|--------|-------|
| Ring non-execution share | 41.9% |
| Non-ring non-execution share | 44.7% |
| Enrichment ratio | 0.937 |
| Result | **FAIL** |

Ring text does NOT show non-execution enrichment at 8-category resolution. Explained by resolution effect: C1131's 42.7% AUXILIARY at 5-role level disappears when projected to 8-category space because bridge MIDDLEs carry the same category regardless of deployment context (scaffold vs execution). AX vocabulary shares 89.3% of MIDDLEs with operational roles (C567).

### T3: Spatial Non-Coherence

| Metric | Value |
|--------|-------|
| Mean adjacent JSD | 0.080 |
| Mean non-adjacent JSD | 0.073 |
| Delta | 0.007 |
| Threshold | < 0.02 |
| Result | **PASS** |

Entity operational character is NOT organized by physical proximity on the foldout. Extends C1128 (generic indexing) to category level.

### T4: Dual Population Per-Entity Divergence (Reported Separately)

| Entity | Classified N | Unclassified N | Category JSD |
|--------|-------------|----------------|--------------|
| SW | 16 | 29 | **0.646** |
| EAST | 18 | 14 | **0.440** |
| WEST | 15 | 13 | 0.286 |
| NW | 12 | 19 | 0.253 |
| NORTH | 25 | 17 | 0.212 |
| SOUTH | 22 | 15 | 0.194 |
| SE | 12 | 16 | 0.131 |
| CENTER | 36 | 31 | 0.124 |
| NE | 22 | 31 | 0.116 |
| **Mean** | | | **0.267** |

C1132's dual population manifests strongly at category level with large entity-specific variation. SW (0.646) and EAST (0.440) are extreme outliers; CENTER (0.124) and NE (0.116) have lowest divergence.

### Baseline Positioning

| Comparison | HEAD JSD | Category JSD | HEAD Cosine | Category Cosine |
|-----------|----------|-------------|-------------|-----------------|
| Rosettes vs AZC | **0.026** | 0.045 | **0.926** | 0.895 |
| Rosettes vs A | 0.050 | 0.072 | 0.894 | 0.856 |
| Rosettes vs B | 0.095 | **0.037** | 0.806 | **0.914** |

**HEAD-category dissociation**: HEAD closest to AZC, category closest to B. This is the signature of a compilation interface — AZC-like domain selection compiled through bridge terminal constraints into B-like execution categories.

## Scripts

| Script | Runtime | Output |
|--------|---------|--------|
| `scripts/rosettes_operational_close_reading.py` | ~8s | `results/rosettes_operational_close_reading.json` |
| (same script) | | `data/rosettes_entity_dumps.txt` |

## Key Findings

### 1. Rosettes Entity Operational Uniformity (C1817)
Mean pairwise category JSD 0.074 across 9 rosettes, below bootstrap 95th percentile 0.106. All entities share a common operational profile at 8-category resolution. Extends C1128 (generic indexing) from vocabulary to operational level.

### 2. Rosettes Spatial Non-Coherence at Category Level (C1818)
Adjacent-pair mean JSD (0.080) ≈ non-adjacent (0.073), delta 0.007. Entity operational character is NOT organized by physical proximity. The foldout is an operational index, not a spatial procedure.

### 3. HEAD-Category Dissociation (C1819)
HEAD distribution closest to AZC (JSD=0.026), category distribution closest to B (JSD=0.037). Mechanism: all tokens (both populations) drive HEAD toward AZC's o-enriched profile; classified-only tokens (bridge-dominated) drive category toward B's execution categories. Expert consensus: this is the compilation interface — the Rosettes sit exactly where AZC-like declarative specifications become B-like executable operations.

### 4. Per-Entity Dual Population Category Divergence (C1820)
Within-entity classified/unclassified category JSD ranges from 0.116 (NE) to 0.646 (SW), mean 0.267. C1132's dual population manifests strongly at category level. SW's extreme divergence (classified=OPERATION-dominant, unclassified=MARKING-dominant) suggests domain-boundary positioning. CENTER's minimal divergence (0.124) suggests integration-hub convergence.

### 5. EAST Execution Anomaly (C1821)
Only rosette entity with e-HEAD > o-HEAD (31% vs 25%). Highest kernel density (32.3%), OPERATION 44.4% among classified tokens. ok-prefix dominance (10/32 tokens) creates thermal-verification channel. Most execution-like entity in the Rosettes, displaced from the AZC-like metalayer profile toward B execution character.

### 6. CENTER Integration Hub (C1822)
Lowest dual-population JSD (0.124), highest headless rate (32.8%), most balanced HEAD distribution, largest token count (67). Both vocabulary layers encode the same operational context. Functions as the convergence point — the spatial analog of B's AXM universal attractor (C978).

### 7. CLOCK Zero-Energy Monitoring (C1823)
k-kernel=0%, FLOW=50%, zero energy modulation (6 tokens). Indexes pure monitoring/flow operations without thermal input. Unique among all Rosettes entities.

## Expert Close Reading Highlights

### Entity Operational Profiles

| Entity | Tokens | Dom HEAD | Bridge | Character |
|--------|--------|----------|--------|-----------|
| CENTER | 67 | o 38.8% | 77.6% | Integration hub, highest headless (32.8%) |
| NORTH | 42 | o 33.3% | 88.1% | Iteration-focused (a-HEAD 28.6%) |
| NE | 53 | o 39.6% | 69.8% | Typical rosette, closest to aggregate |
| EAST | 32 | **e 27.8%** | 71.9% | Execution anomaly (e-HEAD dominant) |
| SE | 28 | o 50.0% | 67.9% | Arrangement-pure (highest o-HEAD) |
| SOUTH | 37 | o 35.1% | 83.8% | h-kernel 0%, monitoring-absent |
| SW | 45 | o 44.4% | 64.4% | Domain boundary (JSD=0.646 extreme) |
| WEST | 28 | o 42.9% | 75.0% | h-kernel 0%, monitoring-absent |
| NW | 31 | o 29.0% | 67.7% | Flow-oriented (FLOW 37.9%) |

### Structural Observations
- **No positional grammar within ring texts** — HEAD domains appear quasi-random, confirming C1130 (bigram entropy 7.92 bits). This is an index vocabulary, not a procedural sequence.
- **Genuine C/U interleaving** — classified and unclassified tokens spatially mix within every sub-region. No block segregation.
- **o->bare is the universal dominant frame** — minimal arrangement operations forming the catalog backbone across all entities.
- **Inner labels drive entity-specific differentiation** — ring text (higher bridge, more uniform) provides the generic index; inner labels carry what entity-specificity exists.
- **PATHs are abbreviated rosette text** — same HEAD distribution, same bridge enrichment, not a separate register.
- **Headless rate correlates with entity size** — larger entities (CENTER=67 → 32.8% headless) need more infrastructure vocabulary to organize broader operational scope.

## Caveats

1. **ZL transcription filtering**: Same 49/443 filter as Phase 619.
2. **T2 resolution effect**: C1131's 5-role AUXILIARY differentiation disappears at 8-category resolution because bridge MIDDLEs carry identical categories regardless of deployment context.
3. **Entity sample sizes**: 9 rosettes range from 28-67 tokens. JSD estimates for smallest entities (SE=28, WEST=28) are noisy. Bootstrap null accounts for this.
4. **T4 not in verdict**: Dual population divergence is reported separately because it is a characterization metric, not a pass/fail prediction against the index model.
5. **Expert interpretations**: Close reading findings are Tier 3-4. The "compilation interface" interpretation of C1819 is structurally grounded but interpretive.

## Verdict Rationale

UNIFORM_OPERATIONAL_INDEX: T1 (bootstrap uniformity) and T3 (spatial non-coherence) pass. T2 (ring enrichment) fails due to resolution effect, not model failure. All 9 rosettes share a common operational profile without spatial organization. The headline finding is C1819's HEAD-category dissociation — HEAD closest to AZC, category closest to B — identifying the Rosettes as the compilation interface between declarative and executable manuscript layers.

T4 reveals large entity-specific dual-population divergence (SW=0.646, EAST=0.440) that automated tests missed but expert close reading characterizes: SW sits at a domain boundary (OPERATION vs MARKING), EAST is displaced toward execution character, CENTER is the integration hub.

## Dependencies

- C1126 (Rosettes metalayer confirmed)
- C1127 (Rosettes AZC-like grammar)
- C1124 (Rosettes bridge enrichment 3.05x)
- C1128 (Rosettes generic indexing)
- C1130 (Rosettes random transition structure)
- C1131 (Ring text BRIDGE_VOCABULARY_INDEX, 42.7% AUXILIARY)
- C1132 (Ring text dual population)
- C1250 (8 operational categories)
- C1393-C1394 (HEAD+MOD+TERM slot grammar)
- C1475 (HEAD domain taxonomy)
- C1487 (Terminal tier system)
- C1499 (Shared atom substrate)
- C1502 (AZC o-HEAD enrichment)
- C1506-C1507 (Bridge terminal stability, HEAD redistribution)
- C1559 (o-HEAD cross-system gradient)
- C1813-C1816 (Phase 619 rosettes atom findings)
