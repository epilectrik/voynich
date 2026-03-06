# Phase 539: Bridge MIDDLE Atom-Role Stability Across A and B

**Phase:** BRIDGE_ATOM_STABILITY
**Date:** 2026-03-06
**Constraints added:** C1506-C1509
**Verdict:** PARTIAL_STABILITY

---

## Research Question

Do bridge MIDDLEs preserve atom-role behavior across Currier A and Currier B? The bridge backbone (85 MIDDLEs) carries the dynamical structure shared between A's registry and B's execution grammar. C1499 proved the atom ontology is manuscript-wide, but does the same MIDDLE behave the same way in both systems?

## Context

- C1499: Atom ontology is manuscript-wide shared substrate (Jaccard 0.895)
- C1503: Bridge atoms redistribute across A/B (-edy ~50x B-enriched)
- C1500: Bridge-dark HEAD differentiation (bridge e/k/t dominant)
- C1395: Cross-system instruction encoding (HEAD+MOD*+TERM)
- C1504: Modifier grammar universal (MOD JSD < 0.007)

## Method

11 tests (T1-T11) plus a 10-prediction scorecard. Each bridge MIDDLE decomposed via `decompose_middle_hmt()` into HEAD, MOD, TERM slots. Token collections from A and B compared at each slot dimension plus PREFIX/SUFFIX ecology, category profiles, and per-atom behavioral correlations. 85 bridge MIDDLEs, 9,391 A tokens, 19,998 B tokens.

## Key Findings

### Internal Slot Stability (mean JSD = 0.046)

| Dimension | JSD | Cosine | Stability |
|-----------|-----|--------|-----------|
| TERMINAL | 0.014 | 0.977 | PRESERVED |
| CATEGORY | 0.037 | 0.913 | PRESERVED |
| MODIFIER | 0.048 | 0.967 | SHIFTED |
| HEAD | 0.077 | 0.837 | SHIFTED |

**TERMINAL is the most stable dimension** -- the atom carrying suffix gating and category specificity functions identically in both systems (C1506). HEAD is the least stable -- A uses o-HEAD/HEADLESS (arrangement), B uses e/k-HEAD (execution) (C1507).

### External Ecology (mean JSD = 0.113)

| Dimension | JSD | Cosine |
|-----------|-----|--------|
| PREFIX ecology | 0.072 | 0.919 |
| SUFFIX ecology | 0.153 | N/A |

PREFIX ecology is moderately different (JSD=0.072) -- all PREFIXes shared except one B-only (pe, 1 token). SUFFIX ecology is truly divergent (JSD=0.153), driven by -edy 50x B-enrichment.

### Frequency Redistribution (T1)

All 85 bridge MIDDLEs present in both A and B. 30 are A-enriched, 3 balanced, 52 B-enriched. Extreme examples: hy (0.077x in B, A-dominant), edy (277x in B, B-dominant), k (6.2x in B).

### Category Redistribution (C1508)

Categories are INTRINSIC -- 100% match rate (same category for same MIDDLE in both systems). But token-weighted distribution shifts: THERMAL +10.1pp in B (largest gain), STAGING -11.1pp in B (largest loss). A amplifies arrangement/observation categories; B amplifies execution categories.

### HEAD Redistribution (C1507)

A-enriched bridges: o-HEAD 55.0%, HEADLESS 42.5% (arrangement/identification).
B-enriched bridges: e-HEAD 37.4%, k-HEAD 15.5% (thermal execution).
HEAD JSD between A-enriched and B-enriched populations = 0.591 (massive).

### Atom Behavioral Stability (C1509)

Three-tier distribution of cross-system atom stability:
- **Stable** (8 atoms, r/s/t/l/a/m/o/g): correlation > 0.90, same behavior in A and B
- **Moderate** (6 atoms, k/c/p/i/e/n): correlation 0.70-0.90, shifted emphasis
- **Unstable** (3 atoms, y/h/d): correlation < 0.70, changed dominant category

d is the extreme outlier (correlation 0.062) -- its role changes from CONTAINMENT in A to OPERATION in B, driven by the edy MIDDLE's 277x B-enrichment.

### Terminal Tier Distribution (T10)

Terminal tier JSD = 0.005 (near-identical across systems). The three-tier terminal taxonomy (LOCKED/CHANNELED/DIFFUSE from C1487) is preserved with remarkable fidelity:

| Tier | A % | B % |
|------|-----|-----|
| BARE_TERM | 35.6% | 39.3% |
| CHANNELED | 45.0% | 46.8% |
| LOCKED | 13.8% | 10.8% |
| DIFFUSE | 5.7% | 3.1% |

B slightly enriches y-terminal (1.54x) at the expense of h-terminal (0.54x).

## Prediction Scorecard

| # | Prediction | Result |
|---|-----------|--------|
| P1 | HEAD stable (JSD < 0.05) | FAIL (0.077) |
| P2 | TERMINAL stable (JSD < 0.05) | PASS (0.014) |
| P3 | MODIFIER universal (JSD < 0.01) | FAIL (0.048) |
| P4 | Category intrinsic (100% match) | PASS |
| P5 | PREFIX ecology divergent (JSD > 0.20) | FAIL (0.072) |
| P6 | A suffix rate < B suffix rate | PASS (35.9% vs 42.3%) |
| P7 | A/B-enriched have different HEADs | PASS (JSD = 0.591) |
| P8 | All atom correlations > 0.70 | FAIL (d=0.062, h=0.365, y=0.476) |
| P9 | A prefers l,h terminals | PASS |
| P10 | B prefers y,m,r terminals | FAIL (only y enriched) |

**Score: 5/10 (50%)**

P1 FAIL: HEAD is the LEAST stable slot, not stable. A's o-HEAD dominance vs B's e/k-HEAD dominance creates real divergence.

P3 FAIL: Modifiers shift substantially. d-modifier explodes in B (544 A vs 3,528 B tokens), driven by -edy.

P5 FAIL: PREFIX ecology is NOT divergent -- cosine 0.919, all PREFIXes shared. The wrapping is more similar than expected.

P8 FAIL: Three atoms (d, h, y) have radically different behavioral profiles across systems. These are the closure/boundary atoms, not the structural frame atoms.

P10 FAIL: B enriches y-terminal (1.54x) but NOT m-terminal (0.69x) or r-terminal (0.80x).

## Verdict: PARTIAL_STABILITY

Bridge MIDDLEs exhibit a clear stability hierarchy: **internal structure preserved, deployment channels shifted**. Terminal atoms are system-invariant (C1506). HEAD atoms are system-sensitive (C1507). Categories are intrinsic to the MIDDLE identity but their population emphasis shifts between arrangement (A) and execution (B) contexts (C1508). Individual atoms partition into three behavioral stability tiers (C1509).

The ratio of internal to external JSD (0.046 / 0.113 = 0.41) shows the MIDDLE itself is roughly 2.4x more stable than its wrapping context. The bridge backbone maintains its structural skeleton across systems while being deployed with different frequency emphasis and morphological wrapping.

## Constraints Produced

| # | Name | Tier | Key Finding |
|---|------|------|-------------|
| C1506 | Bridge terminal atom stability across A and B | 2 | TERMINAL JSD = 0.014, most stable slot |
| C1507 | Bridge HEAD redistribution A vs B | 2 | A = o/HEADLESS, B = e/k, JSD = 0.077 |
| C1508 | Bridge category redistribution A vs B | 2 | THERMAL +10.1pp B, STAGING -11.1pp B |
| C1509 | Three-tier atom behavioral stability | 2 | 8 stable, 6 moderate, 3 unstable atoms |

## Cross-References

| Constraint | Status | How |
|-----------|--------|-----|
| C1499 | CONFIRMED | Shared substrate proven behaviorally stable at terminal level |
| C1503 | EXTENDED | Redistribution quantified at all slot dimensions |
| C1500 | CONFIRMED | Bridge e/k/t enrichment confirmed as B-specific execution emphasis |
| C1347 | EXTENDED | B reshaping quantified: THERMAL +10.1pp, STAGING -11.1pp |
| C1388 | CONFIRMED | o-atom arrangement domain confirmed via A-enriched bridge HEAD profile |
| C1487 | CONFIRMED | Three-tier terminal taxonomy preserved across systems (tier JSD = 0.005) |
| C1409 | EXTENDED | Atom cross-position divergence now includes cross-system divergence |

## Files

- Script: `phases/BRIDGE_ATOM_STABILITY/scripts/bridge_atom_stability.py`
- Results: `phases/BRIDGE_ATOM_STABILITY/results/bridge_atom_stability.json`
