# FOLIO_LEVEL_FILTERING

**Status:** COMPLETE | **Constraints:** C704-C709 | **Scope:** A-B

## Objective

Test whether the **full A folio** is the functional filtering unit for B vocabulary. CONSTRAINT_BUNDLE_SEGMENTATION showed PP MIDDLEs distribute homogeneously within A folios (C703), making the folio-level PP union the natural candidate. A_RECORD_B_FILTERING (C682-C693) showed individual records are too restrictive (11/49 classes, 78% unusable).

## Key Findings

**The A folio IS the functional filtering unit.** All 6 tests passed. Folio-level pooling produces viable B programs with dramatic improvement over record-level filtering.

| Metric | Record-Level (C682-C693) | Folio-Level | Improvement |
|--------|--------------------------|-------------|-------------|
| PP MIDDLEs | 5.0 per record | 35.3 per folio | **7.0x** |
| Class survival | 11.08/49 (22.6%) | 39.8/49 (81.2%) | **3.6x** |
| Empty B lines | 78% | 13.7% | **5.7x better** |
| Best usability | 0.107 | 0.343 | **3.2x** |
| Dynamic range | 266x | 14.3x | **18.6x tighter** |
| Inter-folio discrimination | Jaccard 0.199 | Jaccard 0.274 | Still discriminative |

## Interpretation

Each A folio specifies a PP vocabulary pool. Individual lines are partial samples of this pool; pooling across all lines recovers the complete specification. The folio-level PP union (mean 35.3 MIDDLEs) provides sufficient vocabulary for B programs with 81.2% class survival and 86.3% line viability.

**Critical observation:** B CLASS-level Jaccard = 0.83 across A folios. Different folios select different tokens but converge on similar class compositions. This is consistent with the Tier 0 frozen conclusion: B programs maintain a narrow viability regime by design.

FL remains the most fragile role (32.5% depletion at folio level), confirming the vulnerability gradient (C686). All other roles have near-zero depletion.

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `folio_level_filtering.py` | T3.1-T3.6 (C704-C709) | `folio_level_filtering.json` |

## Constraints

| # | Name | Key Result |
|---|------|------------|
| C704 | Folio PP Pool Size | Mean 35.3 MIDDLEs (7x record-level) |
| C705 | Folio-Level Class Survival | Mean 39.8/49 (81.2%), 3.6x improvement |
| C706 | B Line Viability Under Folio Filtering | 13.7% empty (vs 78% record-level) |
| C707 | Folio Usability Dynamic Range | 14.3x range, best=0.343 |
| C708 | Inter-Folio PP Discrimination | PP Jaccard 0.274, CLASS Jaccard 0.83 |
| C709 | Section Invariance | All sections 100% viable (H=0.085, P=0.182, T=0.293) |

## Gate

**Core gate PASSED:** T3.2 (39.8 >= 25 classes) AND T3.3 (13.7% < 30% empty) AND T3.5 (0.274 < 0.6 Jaccard).

## Data Dependencies

- `scripts/voynich.py` (canonical transcript library)
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (token -> class)
- `phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json` (forbidden transitions)
- `phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json` (REGIME map)

## Cross-References

- C682-C693: A record B filtering (baseline to beat)
- C703: PP folio-level homogeneity (motivating finding)
- C502.a: Full morphological filtering (algorithm used)
- C686: Role vulnerability gradient (FL fragility confirmed at folio level)
- C437: AZC folio orthogonality (Jaccard 0.056 — PP pools are less orthogonal)
