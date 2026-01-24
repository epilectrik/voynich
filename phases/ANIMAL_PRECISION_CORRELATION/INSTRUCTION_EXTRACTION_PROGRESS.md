# Instruction Sequence Extraction Progress

**Task**: Re-curate all 203 Brunschwig recipes with correct instruction sequences
**Started**: 2026-01-21
**Status**: BATCH 1 COMPLETE (automated scan + 16 corrections applied)
**Last Updated**: 2026-01-21

---

## Summary

| Before | After |
|--------|-------|
| 185 generic [AUX, e_ESCAPE] | 170 generic |
| 5 unique sequences | 12 unique sequences |

**Sequence distribution after corrections:**
- [AUX, e_ESCAPE]: 170
- [AUX, k_ENERGY, e_ESCAPE]: 8
- [AUX, FLOW, e_ESCAPE]: 5
- [AUX, h_HAZARD, e_ESCAPE]: 2
- [AUX, h_HAZARD, LINK, e_ESCAPE]: 2
- [AUX, e_ESCAPE, FLOW, k_ENERGY]: 2 (chicken/capon)
- [AUX, FLOW, LINK, e_ESCAPE]: 1
- [AUX, FLOW, h_HAZARD, k_ENERGY, e_ESCAPE]: 1
- [AUX, FLOW, h_HAZARD, LINK, e_ESCAPE]: 1
- [AUX, e_ESCAPE, k_ENERGY]: 1

---

## Instruction Classification Rules

### Instruction Types and Keywords

| Type | Meaning | German Keywords | English Keywords |
|------|---------|-----------------|------------------|
| **AUX** | Preparation | hack, schneid, stoß, wasch, schel, zerklein, zerstampf, bereit | chop, cut, pound, wash, peel, crush, prepare |
| **e_ESCAPE** | Distillation/Recovery | distillier, brenn, alembic, kühl, kalt, rectific | distill, burn, alembic, cool, cold, rectify |
| **k_ENERGY** | Heat Application | balneum, balneo, feuer, warm, hitz, sied, koch, glut | water bath, fire, warm, heat, boil, cook, embers |
| **FLOW** | Pour/Collect/Transfer | gieß, schütt, nimm, samm, setz, filter, seih | pour, collect, take, gather, place, filter, strain |
| **h_HAZARD** | Hazardous/Fermentation | dung, mist, pferd, vergrab, ferment, faul, gift | dung, manure, horse, bury, ferment, rot, poison |
| **LINK** | Timing/Waiting | tag, stund, woch, nacht, wart, zeit, zwischen | day, hour, week, night, wait, time, between |
| **RECOVERY** | Safety/Caution | hüt, acht, gefahr, vorsicht, vermeide | beware, caution, danger, careful, avoid |

### Sequence Order Rules

1. **AUX** typically comes first (preparation)
2. **FLOW** for collection/transfer operations
3. **h_HAZARD** for fermentation/burial steps
4. **LINK** for waiting periods
5. **k_ENERGY** for heating steps
6. **e_ESCAPE** for distillation (often near end)
7. Multiple of same type = list once unless distinct phases

### Special Cases

- "balneum mariae" / "balneo" = k_ENERGY (water bath heating)
- "per alembicum" alone = e_ESCAPE (standard distillation)
- "per alembicum in balneo" = k_ENERGY + e_ESCAPE
- "redistill" or "rectify" = k_ENERGY + e_ESCAPE (second distillation with heat)
- Collection from nature (sap, dew, collected water) = FLOW

### CRITICAL: Harvest Timing vs Procedural Waiting

**NOT LINK (harvest timing):**
- "at end of May" = when to harvest, not a procedural step
- "during dog days" = when to collect
- "between Mary days" = harvest window
- "when flowering" = harvest condition

**IS LINK (procedural waiting):**
- "let stand 8 days" = waiting step during procedure
- "bury for 14 days" = time-based procedure step
- "soak overnight" = procedural waiting
- "place in sun 40 days" = extended procedural step

**Rule**: Only classify as LINK if there's an explicit waiting/timing step DURING the procedure, not harvest timing.

---

## Progress Tracking

| Range | Status | Last Processed | Notes |
|-------|--------|----------------|-------|
| #1-50 | COMPLETE | #45 | 7 corrections |
| #51-100 | COMPLETE | #98 | 4 corrections |
| #101-150 | COMPLETE | #149 | 3 corrections |
| #151-203 | COMPLETE | #170 | 2 corrections |

---

## Correction Log (16 total)

Format: `#ID: OLD_SEQ -> NEW_SEQ (reason)`

### Batch 1 (#1-50) - 7 corrections
- #17 Burretsch Blumen: [AUX, e_ESCAPE] -> [AUX, k_ENERGY, e_ESCAPE] (balneum mariae)
- #21 Blow Gilgen Blümlin: [AUX, e_ESCAPE] -> [AUX, k_ENERGY, e_ESCAPE] (balneum mariae)
- #31 Bonen Blügot: [AUX, e_ESCAPE] -> [AUX, k_ENERGY, e_ESCAPE] (balneum mariae)
- #32 Bonen: [AUX, e_ESCAPE] -> [AUX, k_ENERGY, e_ESCAPE] (ventre equino/warm sand bath)
- #36 Kruſe Basillen: [AUX, e_ESCAPE] -> [AUX, k_ENERGY, e_ESCAPE] (balneum mariae)
- #38 Bocks Blut: [AUX, e_ESCAPE] -> [AUX, FLOW, e_ESCAPE] (blood collected)
- #45 Blow Violen: [AUX, e_ESCAPE] -> [AUX, k_ENERGY, e_ESCAPE] (balneum mariae)

### Batch 2 (#51-100) - 4 corrections
- #68 Ertber: [AUX, e_ESCAPE] -> [AUX, h_HAZARD, LINK, e_ESCAPE] (bury in ant hill 8 days)
- #89 Holder Rinde: [AUX, e_ESCAPE] -> [AUX, k_ENERGY, e_ESCAPE] (balneum mariae)
- #94 Hunig: [AUX, h_HAZARD, e_ESCAPE] -> [AUX, h_HAZARD, LINK, e_ESCAPE] (bury 14 days)
- #98 Huner Magen: [AUX, e_ESCAPE] -> [AUX, k_ENERGY, e_ESCAPE] (balneum mariae)

### Batch 3 (#101-150) - 3 corrections
- #110 Karten waſſer: [AUX, e_ESCAPE] -> [AUX, FLOW, LINK, e_ESCAPE] (collect, 40 days in sun)
- #119 Küetreck: [AUX, e_ESCAPE] -> [AUX, FLOW, h_HAZARD, k_ENERGY, e_ESCAPE] (dung, collect, redistill)
- #149 Reben: [AUX, e_ESCAPE] -> [AUX, FLOW, e_ESCAPE] (sap collected)

### Batch 4 (#151-203) - 2 corrections
- #159 Regen würm: [AUX, e_ESCAPE] -> [AUX, FLOW, h_HAZARD, LINK, e_ESCAPE] (soak overnight, manure, pour)
- #170 Stern geſchütz: [AUX, e_ESCAPE] -> [AUX, h_HAZARD, e_ESCAPE] (rotting wood)

---

## Spot Check Verification (2026-01-22)

Verified 4 random recipes against OCR source text:

| ID | Recipe | Dimensions Verified |
|----|--------|---------------------|
| #89 | Holder Rinde | class=tree_bark, fire=2, seq correct (balneum mariae confirmed) |
| #98 | Huner Magen | class=animal, fire=4, seq correct (stripped + balneum marie) |
| #119 | Küetreck | class=animal_product, fire=4, all 5 steps confirmed in OCR |
| #159 | Regen würm | class=animal, fire=4, all 5 steps confirmed (overnight soak, manured earth, collection, cleaning, distillation) |

**Result:** All dimensions verified correct against source text.

---

## Resume Instructions

If context is compacted, read this file to resume:
1. Check "Progress Tracking" table for last completed batch
2. Read the Correction Log for what's been done
3. Continue from the next unprocessed recipe
4. Update this file as you go

---

## Files

- **Source OCR**: `sources/brunschwig_1500_text.txt`
- **Current JSON**: `data/brunschwig_complete.json`
- **This tracking file**: `phases/ANIMAL_PRECISION_CORRELATION/INSTRUCTION_EXTRACTION_PROGRESS.md`
