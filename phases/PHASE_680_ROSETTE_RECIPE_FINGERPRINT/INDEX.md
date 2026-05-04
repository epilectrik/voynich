# Phase 680: Rosette ↔ Matched-Recipe Operational Fingerprint

**Status:** COMPLETE
**Started:** 2026-05-04
**Goal:** Test whether specific rosettes resemble specific operational classes from the 11 matched-recipe folios. Phase 402 (C1124-C1130) had concluded "generic indexing"; this phase asked whether finer-grained recipe-class structure exists with our updated matching catalog.

## Findings

### Real structural finding: Path/node fingerprint differentiation

| Metric | Paths (n=25) | Nodes (n=409) | Diff |
|--------|--------------|---------------|------|
| BARE prefix | 40% | 34.5% | +5.5 |
| da-prefix | **16%** | **1.7%** | **+14.3 (9.4x)** |
| ok-prefix | 4% | **17.1%** | **-13.1 (4.3x)** |
| TERM-y | 48% | 28.9% | +19.1 |
| HEAD-a | 4% | 17.4% | -13.4 |
| HEAD-e | 8% | 19.6% | -11.6 |
| Bridge MIDDLE | 36% | 54% | -18 |

The path/node distinction survives same-folio baseline (Phase 678): f85+f86 body has 6% da-prefix (intermediate), so paths are 2.7x folio rate and nodes are 3.5x lower than folio rate. Both populations are intentionally structured.

### Recipe-class operational map: FALSIFIED

Initial spatial pattern (closest matched recipe per rosette):
- Bottom row (S/SE/SW) → fixation (f116r)
- Top + Center → potable gold (f81v)
- Cardinal axes → transformations

Falsifiers run:
- **F1 permutation null:** combined coherence p=0.024 — bottom-row pattern statistically real
- **F2 sub-region prediction:** 5/9 rosettes show whole-fingerprint differing from dominant-sub-region — within-rosette incoherence
- **F3 whitelist sensitivity (THE KILLER):** 45/100 random non-matched 11-folio pools produce same or higher spatial coherence

The recipe-class interpretation FAILS F3. Pattern is fingerprint-similarity arithmetic (rosettes' AZC-like grammar pulls them toward low-thermal folios generally), not specific recipe mapping.

### CENTER vs outer-8 structural difference

CENTER has higher BARE (40% vs 33%), higher qo (2.8% vs 1.5%), higher sh (4.2% vs 2.1%). Lower ok (-7.3), lower ch (-5.4), lower head_a/head_e. Consistent with CENTER as focal/integrative node distinct from outer-8 apparatus stations.

## Constraint Registered

### C1989 (Tier 3): Rosette path/node structural differentiation

Within the f85-86 rosettes foldout (per data/rosettes_annotated.json), path tokens between rosettes (n=25, 8 paths in octagonal cycle) differ structurally from rosette node tokens (n=409, 9 rosettes). Paths show 9.4x enrichment in da-prefix (16% vs 1.7%) and 4.3x depletion in ok-prefix (4% vs 17.1%). Survives same-folio baseline control (f85+f86 body has 6% da-prefix, intermediate). Recipe-class operational map interpretation FALSIFIED by whitelist-sensitivity test (45/100 random non-matched 11-folio pools reproduce same spatial coherence). Path/node distinction is intentional structural property of the foldout, not arithmetic artifact. Mechanism not adjudicated; consistent with workshop-apparatus-diagram interpretation in SPECULATIVE/rosettes_workshop_diagram.md.

**Tier:** 3 (Rosettes structural property)

## Scripts

- `s1_rosette_fingerprint.py` — Operational fingerprint comparison
- `s2_falsifiers.py` — Three falsifier tests (permutation null, sub-region prediction, whitelist sensitivity)
- `s3_paths_peek.py` — Per-token inspection of path content
- `s4_same_folio_baseline.py` — f85+f86 body comparison

## Relationship to Existing Constraints

- **C1124-C1130** (rosettes metalayer, AZC-like, generic indexing): C1989 refines — the metalayer has internal path/node differentiation that wasn't characterized before
- **C1128** (generic indexing across all 82 B folios): NOT contradicted; C1989 operates at a different granularity (within-rosette structure)
- **C1925** (dar = material introduction): Path da-enrichment is consistent
- **C1487** (HEAD×TERM affinity): Path/node profiles align with different head×term combinations
