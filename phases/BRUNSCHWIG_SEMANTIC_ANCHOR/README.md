# BRUNSCHWIG_SEMANTIC_ANCHOR Phase

## Goal

Close the semantic anchoring chain from Brunschwig recipes → Product types → A entry MIDDLEs.

Establish whether MIDDLEs encode **material-processing compatibility** (not identity).

## The Unclosed Chain

```
Brunschwig: "Lavender water uses first degree balneum" ─────────── KNOWN
     ↓
Voynich: REGIME = Brunschwig degree = Product type ─────────────── PROVEN (F-BRU-001/002)
     ↓
Voynich: Product types have exclusive MIDDLE vocabularies ──────── PROVEN (78.2% exclusive)
     ↓
??? A entries with those MIDDLEs = material-compatible contexts
     ↓
ANCHOR: MIDDLEs encode processing compatibility, not material identity
```

## Product Type ↔ REGIME Mapping

From existing validation:

| REGIME | Fire Degree | Product Type | Brunschwig Examples |
|--------|-------------|--------------|---------------------|
| REGIME_2 | 1st (balneum) | WATER_GENTLE | Lavender, rose, violet |
| REGIME_1 | 2nd (warm) | WATER_STANDARD | Sage, mint, rue |
| REGIME_3 | 3rd (seething) | OIL_RESIN | Juniper, turpentine, pine |
| REGIME_4 | 4th (intense) | PRECISION | Precise timing operations |

## Key Constraint

**C171:** Zero material encoding. Cannot claim "MIDDLE X = substance Y".

We CAN claim: "MIDDLEs in cluster X occur only in contexts compatible with gentle-extraction materials."

## Phase Structure

| Phase | Script | Question |
|-------|--------|----------|
| 1 | `phase1_ab_flow_validation.py` | Do A folios classified as WATER_GENTLE feed B folios in REGIME_2? |
| 2 | `phase2_discriminating_middles.py` | Which MIDDLEs are most diagnostic of each product type? |
| 3 | `phase3_material_incompatibility.py` | Do MIDDLE incompatibilities align with material processing incompatibilities? |
| 4 | `phase4_entry_prediction.py` | Can we predict an A entry's product affinity from its structure? |

## Success Criteria

- Phase 1: A→B flow validates >70%
- Phase 2: Discriminating MIDDLEs are disjoint across product types
- Phase 3: Cross-product incompatibility >95%
- Phase 4: Entry prediction >60% accuracy (vs 25% baseline)

## Falsification

If phases fail: MIDDLEs encode operational state only, not material compatibility.
F-BRU-003 (property rejection) would extend to entry level.

## Dependencies

- `results/exclusive_middle_backprop.json` - Product-exclusive MIDDLEs, A folio classifications
- `results/regime_folio_mapping.json` - B folio REGIME assignments
- `results/middle_incompatibility.json` - MIDDLE incompatibility data
- `data/transcriptions/interlinear_full_words.txt` - Full transcript
