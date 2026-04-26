# Phase 654: Dark Pipeline Folio-Resolution Typology Test

## PRE-REGISTRATION

**Date locked:** 2026-04-26
**Status:** PRE-REGISTERED — predictions and classifications locked BEFORE atom analysis

This document is committed to the repository as pre-registration evidence. All classifications and statistical criteria are locked. Subsequent test scripts may not retroactively modify the categorization or pass/fail thresholds.

---

## Background

Phase 653 attempted to test whether dark-pipeline material atoms align with material-introduction events at paragraph resolution. The test was underpowered (eet had only ~5 occurrences in matched-folio token streams; paragraph-level alignment couldn't detect a folio-resolution signal). Result: null at p=1.0, but the null was on a test that couldn't have detected a real effect of the magnitude C1939 predicts.

C1939 (fch=mercury) and C1940 (cs=gold) operate at folio resolution — "∞ enrichment on 6/6 mercury-recipe folios" — which is the resolution where these material-atom claims can actually be tested.

Phase 654 re-runs the materials-as-identifiers thesis at the correct resolution: **folio-presence test, pre-registered, Bonferroni-corrected.**

---

## Locked classifications

### Eight substrate categories (mutually exclusive, exhaustive)

1. **MINERAL_MERCURY** — primary substrate is Hg / argent viu (cinnabar work, mercurial sublimation, congelation, fixation)
2. **GOLD** — primary substrate is gold / or (gold dissolution, projection, potable gold)
3. **SILVER** — primary substrate is silver (lunar work, silver-plate operations)
4. **ANIMAL_SUBSTRATE** — primary substrate is animal-derived (capon, blood, urine, animal ash, sal ammoniac)
5. **VEGETABLE_SUBSTRATE** — primary substrate is plant-derived (lunaria, herbs, alcoholic spirits, aqua vitae, ferments-of-vegetable)
6. **FERMENT_GENERIC** — ferment work where substrate origin (vegetable vs animal) is unclear or symbolically encoded (H, fifth letter)
7. **MIXED_MINERAL** — multi-mineral recipes (element separation, multi-metal work)
8. **THEORETICAL** — recipe discusses concepts without specific substrate work (vessel specifications, furnace theory, principle discussions)

**Classification rule:** Primary substrate = the material being PROCESSED in the recipe, prioritizing the input substrate over solvent or product. For ambiguous cases, default to the most prominent substance in the recipe text.

### Per-folio classifications (LOCKED)

Based on existing matched_recipes_status.json + C1959 extensions:

| Folio | Recipe | Locked Category | Rationale |
|---|---|---|---|
| f75r | Aqua vitae 4x/9x reflux | **VEGETABLE_SUBSTRATE** | Wine + honey/wax = vegetable origin |
| f76r | Element separation silver-plate | **MIXED_MINERAL** | M/O/L symbolic, silver test |
| f84r | Gold dissolution balneum+putrefaction | **GOLD** | Gold is primary substrate |
| f79r | Mercury sublimation → elixir | **MINERAL_MERCURY** | Hg sublimation work |
| f82r | Lunaria maceration 3-day sealed | **VEGETABLE_SUBSTRATE** | Lunaria primary |
| f103r | Ferment multiplication multi-chamber | **FERMENT_GENERIC** | Ferment work, B+C chambers symbolic |
| f76v | Ferment conversion (join H + bind) | **FERMENT_GENERIC** | Adds H letter, fifth letter — symbolic ferment |
| f77v | Furnace specification | **THEORETICAL** | Discusses subjects/leon vert as concepts |
| f81v | Potable gold / water of life | **GOLD** | Gold is target substrate (vegetable solvent secondary) |
| f82v | Vessel specification | **THEORETICAL** | Stone-in-elements theory |
| f112r | Red mercury tincture (cohobation) | **MINERAL_MERCURY** | Hg cohobation |
| f112v | Lunaria → quicksilver | **VEGETABLE_SUBSTRATE** | Lunaria input, quicksilver product (substrate is input) |
| f116r | Fixation / fusibility test | **MINERAL_MERCURY** | Hg fixation work |
| f107r | Quicksilver coagulation | **MINERAL_MERCURY** | Hg coagulation |
| f80r | Animal ash chain Ch21 multi | **ANIMAL_SUBSTRATE** | Animal ash primary substrate (Ch21-25) |
| f83r | Drip-counted mercurial solvent | **MINERAL_MERCURY** | Hg-solvent work |

C1959 extensions (per memory note + Phase 644):
| f108v | Mercury sublimation (III.29) | **MINERAL_MERCURY** | Hg sublimation chapter |
| f79v | First liquefaction (II.8) | **VEGETABLE_SUBSTRATE** | Liquefaction of F (= vegetable per cipher) |
| f78r | Mercury congelation (III.36) | **MINERAL_MERCURY** | Hg congelation |
| f86v3 | 3-day coniuncció (II.10) | **MIXED_MINERAL** | Conjunction work |
| f77r | 4-element temperament (III.28) | **THEORETICAL** | Element temperament theoretical |

**Total folio set: 21 matched folios.**

### Category counts

| Category | n folios |
|---|:---:|
| MINERAL_MERCURY | 7 (f79r, f112r, f116r, f107r, f83r, f108v, f78r) |
| GOLD | 2 (f84r, f81v) |
| SILVER | 0 |
| ANIMAL_SUBSTRATE | 1 (f80r) |
| VEGETABLE_SUBSTRATE | 4 (f75r, f82r, f112v, f79v) |
| FERMENT_GENERIC | 2 (f103r, f76v) |
| MIXED_MINERAL | 2 (f76r, f86v3) |
| THEORETICAL | 3 (f77v, f82v, f77r) |

**Pre-registration acknowledgment:** Several categories have low n (0-2), limiting statistical power. The pass criteria below are calibrated accordingly.

---

## Statistical protocol

### Atoms tested (9 named in C1941)

Equipment: lch, lk, eed
Process: cth, eke, ksh
Material: fch, cs, eckh

### Test

For each (atom, category) pair, compute:
- Folio-presence rate of atom on category folios = (folios in category with ≥1 occurrence of atom) / (n folios in category)
- Folio-presence rate of atom on non-category folios = same calculation on the remaining matched folios
- **Enrichment ratio** = category rate / non-category rate
- **Fisher exact test** for the 2×2 contingency (folio-with-atom × in-category)
- **Bonferroni correction:** alpha = 0.05 / 9 atoms = 0.0056

### Pass criteria (LOCKED)

**Phase 654 PASSES** if ≥3 atoms show:
- Enrichment ratio ≥4× (folio-presence rate at least 4× higher in target category)
- AND Fisher exact p < 0.0056 (Bonferroni-corrected)

**Phase 654 NULL** if ≤1 atom passes both criteria.

**Phase 654 INCONCLUSIVE** if 2 atoms pass — register as Tier 3 with documented underpowered status.

### Expected pre-registered predictions

Based on existing C1939, C1940 and crazy-expert framework:

| Atom | Predicted category | Reason |
|---|---|---|
| fch | MINERAL_MERCURY | C1939 (already at Tier 3) |
| cs | GOLD | C1940 (already at Tier 3) |
| eckh | VEGETABLE_SUBSTRATE | Phase 653 directional finding (38% organic vs 23% mineral, n=26, p>0.10) |
| eet | ANIMAL_SUBSTRATE (or fails) | Phase 653 atom-decomposition reading + 4:1:0 corpus ratio (post-hoc, weak) |
| Other 5 atoms (lch, lk, eed, cth, eke, ksh) | No prediction | Equipment/process atoms not predicted to be category-specific |

NOTE: eet not in the 9-atom test set per C1941. It was identified as a candidate post-hoc in Phase 653 and is not part of the locked typology test. Including eet in the test would constitute peeking after pre-registration.

---

## Outcome registration plan

**If Phase 654 PASSES (≥3 atoms confirmed):**
- Register C1968 (Tier 2): "Folio-resolution atom-substrate typology — N atoms map to substrate categories with Bonferroni-corrected p<0.0056 and ≥4× enrichment."
- The materials-as-identifiers thesis upgrades from "C1939+C1940 isolated findings" to "structural typology with N atom-substrate associations."

**If Phase 654 NULL (≤1 atom):**
- Document the null result; no new constraint registered.
- C1939 and C1940 stand as isolated material-identification findings (already Tier 3).
- Update INTERPRETATION_SUMMARY.md to reflect that the broader material-atom typology is empirically refuted.

**If Phase 654 INCONCLUSIVE (2 atoms):**
- Register Tier 3 candidate "atom-substrate typology partially supported" with documented underpowering.
- Future work: expand the test as more matched folios become available.

---

## Pre-registration commitment

This document is committed to the repository at the time of locking. The test script (s1 or future) will:

1. Read the locked classifications from this file
2. Apply the locked statistical protocol exactly
3. Report results without retroactively adjusting thresholds or categories
4. Register outcome per the locked outcome plan

Any deviation from the locked protocol must be flagged as an explicit deviation in the test result, not silently incorporated.

**Locked by:** project methodology
**Test execution:** deferred to subsequent session (forces independence between prediction and test)
