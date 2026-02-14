# C1034: Symmetric Forbidden Suppression Fixes B5

**Tier:** 2 | **Scope:** B | **Phase:** PREFIX_FACTORED_DESIGN

## Statement

Bidirectional (symmetric) forbidden suppression resolves M2's B5 failure while preserving B1 and B3. M5-SF (for each forbidden pair A->B, also suppress B->A) achieves B5 pass rate 80% (B5=0.132 vs real 0.090), B1 pass rate 100% (spectral gap 0.873 vs real 0.894), and B3=0 forbidden violations. This is the ONLY tested model that passes all three criteria simultaneously under the C1025 reference forbidden mapping (684 class pairs). M2.5 (15% blending) fails B5 under the same mapping (0%, B5=0.169). PREFIX-factored generation through conditional routing is distributionally equivalent to M2 and does not improve B5.

## Evidence

### Approach Comparison

| Model | Mechanism | B5 | B5 pass | B1 | B1 pass | B3 |
|-------|-----------|-----|---------|-----|---------|-----|
| M2 | Asymmetric forbidden | 0.321 | 0% | 0.880 | 100% | 0.0 |
| **M5-SF** | **Symmetric forbidden** | **0.132** | **80%** | **0.873** | **100%** | **0.0** |
| M2.5 | 15% blending | 0.169 | 0% | 0.877 | 100% | 2.5 |
| M5-PFX | PREFIX-factored | 0.141 | 15% | 0.899 | 100% | 18.1 |
| M5-2 | Second-order chain | 0.149 | 0% | 0.899 | 100% | 19.4 |
| Real | — | 0.090 | — | 0.894 | — | 13 |

### Why Each Approach Fails or Succeeds

**M5-SF (symmetric forbidden) succeeds** because it targets the ROOT CAUSE: 16/17 forbidden pairs are one-directional (C1032), making the transition matrix asymmetric. Making all pairs bidirectional restores symmetry without flattening the spectral structure. Only 204 additional cells are zeroed (from 541 to 745).

**M2.5 (blending) fails** because generic detailed-balance blending is too blunt. Under heavy forbidden suppression (684 class pairs), 15% blending is insufficient to overcome the asymmetry (B5=0.169, outside 50% tolerance). Under lighter mapping (10 pairs), blending works — confirming the issue is forbidden-mapping-dependent.

**PREFIX-factored generation fails** because it is DISTRIBUTIONALLY EQUIVALENT to M2 for class bigrams. Marginalizing PREFIX-conditional transitions exactly recovers the unconditional class transition matrix (reconstruction error: 0.000000). Factoring through PREFIX changes the intermediate representation but not the generative distribution.

**Second-order chain fails** because additional context INCREASES asymmetry (B5=0.149, worse than M2's 0.142 under light mapping). Higher-order dependencies amplify directional patterns.

### PREFIX Transition Symmetry (Background)

| Level | Forward-Backward JSD |
|-------|---------------------|
| PREFIX transitions | 0.051 |
| Class transitions | 0.090 |
| Ratio (class/prefix) | 1.78x |

PREFIX transitions are 1.8x more symmetric than class transitions (C1024), but this symmetry cannot be "injected" through generation factoring — it must be applied directly to the transition matrix via symmetric forbidden suppression.

### Forbidden Mapping Sensitivity

| Mapping | Class Pairs | M2 B5 | M5-SF B5 | M5-SF B5 pass |
|---------|-------------|-------|----------|---------------|
| Token-direct | 10 | 0.142 | 0.129 | 95% |
| C1025-MIDDLE | 684 | 0.321 | 0.132 | 80% |

M5-SF robustly fixes B5 across both mapping strategies. The fix is insensitive to forbidden mapping aggressiveness.

### Projected M2 Pass Rate with M5-SF

| Test | M2 (C1025) | M5-SF | Status |
|------|-----------|-------|--------|
| B4 | FAIL (misspecified) | PASS | C1030 |
| B5 | FAIL (asymmetric) | PASS (80%) | **This phase** |
| C2 | FAIL (misspecified) | PASS | C1033 |
| All other 12 tests | PASS | PASS | C1025 |

**Projected M5-SF pass rate: 15/15 = 100%** (with B4 and C2 corrections from C1030, C1033).

## Interpretation

The B5 forward-backward asymmetry has a single root cause: asymmetric forbidden transition suppression. The fix requires no new generation architecture — just making forbidden suppression bidirectional. This is the "targeted correction" that C1032 identified as needed.

The failure of PREFIX-factored generation (distributionally equivalent to M2) is a significant negative result: PREFIX routing operates through SELECTIVE inclusion (C1012: positive channeling, not cross-state prohibition), which means its symmetry properties cannot be accessed by generation-level factoring. The symmetry must be enforced at the constraint level (forbidden pair structure), not the routing level.

## Open Question

The 684-pair C1025-MIDDLE forbidden mapping is more aggressive than the original C1025 implementation (which produced only 75 extra zero cells due to treating token names as MIDDLEs). The correct forbidden mapping for M2 remains under-specified — the Phase 18A inventory is token-level, and the token-to-class expansion method significantly affects the model. M5-SF's robustness across mapping strategies (80-95% B5 pass) suggests the symmetric fix is valid regardless.

## Related Constraints

- **C1032:** B5 asymmetry mechanism (diagnosed root cause)
- **C1025:** Generative sufficiency (original M2 definition)
- **C1030:** M2 gap decomposition (B4 correction)
- **C1033:** C2 misspecification
- **C1024:** PREFIX symmetric router, MIDDLE directional executor
- **C1012:** PREFIX positive macro-state channeling
- **C111:** 65% of forbidden transitions are asymmetric

## Provenance

- Scripts: `phases/PREFIX_FACTORED_DESIGN/scripts/prefix_factored_design.py`, `symmetric_forbidden.py`, `m5_comprehensive.py`
- Results: `phases/PREFIX_FACTORED_DESIGN/results/prefix_factored_design.json`, `symmetric_forbidden.json`, `m5_comprehensive.json`
- Date: 2026-02-14
