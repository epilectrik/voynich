# Phase 669: Recto/Verso Operational Pairing

**Status:** COMPLETE
**Started:** 2026-04-30
**Goal:** Test whether recto/verso pairs on the same physical leaf share operational profiles.

## Findings

Both sides of a physical leaf encode operationally similar recipes. This is not an artifact of section membership, sequential proximity, or thermal channel dominance — it survives all four controlled tests.

### C1977: Recto/verso thermal pairing

Recto and verso folios on the same leaf have significantly similar mean e-depth (thermal intensity).

| Metric | Value |
|--------|-------|
| Pairs tested | 35 |
| Pearson r (recto vs verso e-depth) | 0.665 |
| Mean |recto - verso| difference | 0.124 (actual) vs 0.213 (random) |
| p-value (permutation, 10,000 shuffles) | 0.0001 |
| Tier | 2 |

### C1978: Recto/verso operational profile pairing

Recto and verso folios share full PREFIX distribution profiles (not just thermal) significantly beyond what section membership or sequential proximity can explain.

| Metric | Value |
|--------|-------|
| Pairs tested | 35 |
| Mean cosine similarity (actual) | 0.931 |
| Mean cosine (within-section random) | 0.896 |
| p-value (section-stratified permutation) | < 0.0001 |
| R/V advantage over adjacent-different-leaf | +0.038 (0.931 vs 0.894) |
| Without qo channel: p-value | < 0.0001 (multi-channel confirmed) |
| Broader baseline (all 83 folios): p-value | < 0.0001 |
| Per-prefix correlations | qo r=0.811, lk r=0.649, sa r=0.544, sh r=0.531, ok r=0.486, ot r=0.486, da r=0.437, ch r=0.399, ol r=0.384 |
| Tier | 2 |

## Controls Passed

| Control | Purpose | Result |
|---------|---------|--------|
| Section-stratified permutation | Section homogeneity confound | p < 0.0001 — not a section artifact |
| Adjacent-folio comparison | Sequential proximity confound | R/V 0.931 vs adjacent 0.894 — leaf-specific |
| Without-qo cosine | Thermal channel dominance | p < 0.0001 — multi-channel effect |
| Broader baseline (83 folios) | Restricted null confound | p < 0.0001 — robust |

## Interpretation

The scribe organized recipes by operational type on the same physical leaf. Both sides of a leaf encode similar fire management intensity (qo), observation patterns (sh), vessel handling (ok), material density (da), and equipment checking (lk). This is physical workshop organization — sequential operations requiring the same furnace setup are placed on the same sheet.

This extends C1936 (recto/verso sequential operations) from a semantic claim about matched recipe pairs to a structural claim about ALL recto/verso pairs corpus-wide.

## Scripts

| Script | Purpose |
|--------|---------|
| s1_rv_operational_pairing.py | All 4 controlled tests (section-stratified, adjacent-folio, without-qo, broader baseline) |

## Relationship to Existing Constraints

- **C1936** (recto/verso sequential pairing): Tier 3 semantic claim about matched folios. C1977/C1978 extend to all 35 r/v pairs with quantitative evidence.
- **C1325** (folio REGIME homogeneity): Internal folio consistency. C1977/C1978 extend to cross-side-of-leaf consistency.
- **C361** (adjacent folio vocabulary sharing, 1.30x): C1978 shows r/v pairing is STRONGER than adjacent-different-leaf pairing.
