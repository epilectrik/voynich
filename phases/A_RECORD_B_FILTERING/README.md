# A_RECORD_B_FILTERING

**Status:** COMPLETE | **Constraints:** C682-C693 | **Scope:** A-B

## Objective

Characterize how **individual Currier A records filter the Currier B vocabulary** through full morphological filtering (C502.a). Prior work established population-level means (C503.a). This phase asks: **what does a filtered B folio actually look like? Which lines survive? Does the program remain coherent? What fails?**

## Key Findings

**A single A record renders most B folios inoperative.** The median A record (PP=6, 8 surviving classes) makes 74-100% of B folio lines entirely empty. Only the most permissive records (~14 PP MIDDLEs) produce marginally coherent residual programs. The filtering hierarchy is clear:

| Dimension | Result |
|-----------|--------|
| Mean class survival | 11.08 / 49 (22.6%) |
| Most fragile role | FL (60.9% depletion rate) |
| Most resilient role | FQ (12.5% depletion, 43.2% survival) |
| Hazard elimination | 83.9% of records eliminate all 17 forbidden transitions |
| Kernel access | 97.4% retain k/h/e (h=95.5%, k=81.0%, e=60.7%) |
| Filter fingerprint uniqueness | 97.6% (1,525 unique sets from 1,562 records) |
| Dominant failure mode | MIDDLE mismatch (94.7% of failures) |
| Unusable pairings | 25/32 representative (record, folio) pairs have >50% empty lines |
| Usability dynamic range | 266x (best to worst non-zero) |

## Interpretation

A records function as **individual configuration tokens** that each specify a narrow morphological vocabulary slice. No single A record produces a usable B program — the filtering is structurally too severe. This implies B programs operate under aggregate constraint from multiple A records (a full A folio or section), not single-record filtering. The MIDDLE component provides ~95% of the selectivity; PREFIX and SUFFIX contribute marginal edge refinement.

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `survivor_population_profile.py` | T1-T4: Class distribution, role composition, hazard pruning, LINK/kernel | `survivor_population_profile.json` |
| `structural_reshape_analysis.py` | T5-T8: Vulnerability gradient, composition interaction, REGIME robustness, uniqueness | `structural_reshape_analysis.json` |
| `instance_trace_analysis.py` | T9-T12: Line legality, coherence, failure modes, usability gradient | `instance_trace_analysis.json` |

## Constraints

| # | Name | Key Result |
|---|------|------------|
| C682 | Survivor Distribution Profile | Mean 11.08/49 classes, 1.2% zero-class |
| C683 | Role Composition Under Filtering | FL 60.9% depleted, FQ 12.5% depleted |
| C684 | Hazard Pruning Under Filtering | 83.9% full elimination (0/17 active) |
| C685 | LINK and Kernel Survival Rates | 97.4% kernel union, 36.5% lose all LINK |
| C686 | Role Vulnerability Gradient | FL > EN > AX > CC > FQ (most to least fragile) |
| C687 | Composition-Filtering Interaction | PURE_RI: 0.44 classes; MIXED = PURE_PP (p=0.997) |
| C688 | REGIME Filtering Robustness | REGIME_2 most robust (0.222), REGIME_3 least (0.167) |
| C689 | Survivor Set Uniqueness | 97.6% unique (1,525/1,562), Jaccard mean=0.199 |
| C690 | Line-Level Legality Distribution | 78% of pairings >50% empty, no positional effect |
| C691 | Program Coherence Under Filtering | 0-20% operational completeness, work > setup > close |
| C692 | Filtering Failure Mode Distribution | 94.7% MIDDLE, 3.6% PREFIX, 1.7% SUFFIX |
| C693 | Usability Gradient | 266x dynamic range, best=0.107 (Max-classes) |

## Data Dependencies

- `scripts/voynich.py` (canonical transcript library)
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (token -> 49 classes)
- `phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json` (folio -> REGIME)
- `phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json` (17 forbidden transitions)

## Cross-References

- C502.a: Full morphological filtering algorithm (verified)
- C503.a: Prior population mean (6.8 classes — discrepancy documented in C682)
- C503.c: Kernel union access (97.6% — confirmed at 97.4%)
- C509.d: Three filtering dimensions independent (confirmed via C692 failure decomposition)
- C498: RI/PP bifurcation (confirmed: PURE_RI = near-zero survival, C687)
- C384: No A->B token lookup (respected: filtering via morphological components only)
- C609: LINK operator definition (36.5% records lose LINK capacity, C685)
