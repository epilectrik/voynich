# Phase 599: APPARATUS_BUNDLE_ALIGNMENT

**Status:** COMPLETE
**Verdict:** APPARATUS_ALIGNMENT_NOT_CONFIRMED
**Constraints:** C1737–C1738
**Script:** `scripts/bundle_alignment_test.py` (45s)
**Results:** `results/bundle_alignment_results.json`
**Pre-registration:** `PREDICTIONS.md` (SHA-256: `5dded97c42e8af61bdaab5fb20f8a1a7e8f04d3ffd29d9524d8e550358230314`)

## Motivation

Phase 598 established thermal intensity alignment (C1735, C1736) but FAILED on 5-axis apparatus profile matching (598d Block 1). External expert review: we compressed a multi-axis apparatus system into a binary intensity split. The discriminating signal should be in **secondary apparatus profile shape** — the non-DISTILLATION axes (SEALED_VESSEL, SUSTAINED_HEAT, PRECISION, DIRECT_FIRE).

This phase tested whether Brunschwig's method-bundle taxonomy predicts the shape of the Voynich's 5D apparatus profile across section×REGIME cells, using geometry-concordance (Mantel), dominant-profile matching, direction concordance, and an open-cycle signature test. All tests used a **bridge family** (48 variants) for robustness.

## Design

- **Bridge family**: 4 method-bundle classes (GENTLE_SUSTAINED, OPEN_CYCLE_ELEVATED, SEALED_RECIRCULATION, PRECISION_CONTROLLED) × admissible profile mappings × weight family [0.55-0.80] = 48 bridge variants
- **Prototype comparison**: Cells mapped to prototypes via frozen constraints (C494, C1247, C1248), not fire-degree equivalence
- **5 viable cells**: H:R2(13), H:R3(5), H:R4(12), S:R1(10), S:R3(12)
- **Recipe bundles**: GENTLE_SUSTAINED=230, OPEN_CYCLE_ELEVATED=56, SEALED_RECIRCULATION=29, PRECISION_CONTROLLED=14 (102 unclassified — no methods listed)

## Results

| Test | Metric | Result | Verdict |
|------|--------|--------|---------|
| P1 | Mantel geometry concordance | median r=-0.279, median p=0.794, 0% significant | **FAIL** |
| P2 | Dominant match with margin | median match=0.25, p=0.164 | **FAIL** |
| P3 | Stars R1-R3 direction (3 axes) | 1/3 concordant, p=0.913 | **FAIL** |
| P4 | Open-cycle cosine similarity | cos=-0.606, p=0.806 | **FAIL** |
| S1 | DISTILLATION contamination | p=0.624 | **CLEAN** |
| S2 | Section diversity | H>S (p=0.000), H>B>S ordering | Partial C1249 |
| S3 | H:R3 sensitivity | r=0.000 without, r=-0.279 with | ROBUST |

**Final verdict: APPARATUS_ALIGNMENT_NOT_CONFIRMED (0/4, BRIDGE_SENSITIVE)**

## Key Findings

### 1. SEALED_VESSEL Universal Dominance
ALL 5 viable cells show SEALED_VESSEL as the dominant secondary profile:
- S:R1 = 0.609 (highest)
- S:R3 = 0.516
- H:R2 = 0.488
- H:R4 = 0.374
- H:R3 = 0.328

The bridge predicted different dominants (SUSTAINED_HEAT for S:R1, DIRECT_FIRE for S:R3, PRECISION for H:R4). The secondary profile space does not differentiate by apparatus identity — SEALED_VESSEL is the universal secondary mode.

### 2. Anti-Concordant Directional Predictions
Stars R1 vs R3:
- SUSTAINED_HEAT: predicted R1 > R3, observed R1 < R3 (MISS)
- DIRECT_FIRE: predicted R1 < R3, observed R1 > R3 (MISS)
- SEALED_VESSEL: predicted R1 > R3, observed R1 > R3 (MATCH)

R1 (gentle) has MORE DIRECT_FIRE than R3 (elevated). R3 has MORE SUSTAINED_HEAT than R1. This is the opposite of what the Brunschwig method taxonomy predicts.

### 3. Open-Cycle Cosine Anti-Correlation
Open-cycle recipes (207 with distill_references ≥ 2) predict a direction vector that is anti-correlated (cos=-0.606) with the observed R3-R1 direction. Multi-distillation recipes concentrate methods (balneum+horse_dung+circulation) that the bridge maps to SUSTAINED_HEAT and SEALED_VESSEL — but R3 relative to R1 shows the opposite pattern.

### 4. S1 Clean — Not a Thermal Intensity Problem
The DISTILLATION diagnostic is clean (p=0.624 for Herbal R2 vs R4). The failure is not due to thermal intensity confounding the secondary space. The secondary profiles are genuinely independent of DISTILLATION level.

## What This Means

The alignment between the 1512 Brunschwig and the Voynich manuscript is **limited to thermal intensity** (C1735/C1736). The method-bundle taxonomy (balneum_mariae, circulation, open_fire, sand_bath) does NOT predict apparatus profile shape. The 5 apparatus profiles (C1248) are real internal Voynich structure, but they represent a vocabulary differentiation axis that does not correspond to Brunschwig's method categories via any of 48 tested bridge variants.

Possible explanations:
1. The apparatus profiles represent **internal grammatical variation** (different control program templates) that is orthogonal to historical method categories
2. The SEALED_VESSEL vocabulary (ok, aii, ee, eey, eeol) may encode **general-purpose containment/waiting operations** rather than specific apparatus types
3. The Brunschwig-Voynich alignment may be real but operate at a different granularity than method categories (e.g., procedural complexity, safety requirements, duration — as already confirmed by C1735/C1736)
