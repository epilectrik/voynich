# Dark Pipeline Dictionary (Exploratory)

**Status:** EXPLORATORY (Tier 4) | **Date:** 2026-04-02
**Method:** Cross-folio co-occurrence of dark pipeline MIDDLEs against known recipe ingredients from 19 matched folio-recipe pairs.

> **Caveat:** These are candidate identifications based on distribution patterns. None are confirmed. The dark pipeline encodes identification vocabulary that is PREFIX-locked (C1901) and section-modulated (C1148). These tokens label things; the labels are readable as atom-composed property descriptions but not as substance names without external reference.

---

## Tier 1: Equipment/Process Identifiers (appear on 10+ folios)

These dark MIDDLEs appear on nearly every matched folio regardless of recipe. They encode shared apparatus or universal process elements.

| Dark MIDDLE | Folios | Atom reading | Candidate identification |
|------------|--------|-------------|------------------------|
| **lch** | 16/19 | state.adjust.watch | **Distillation apparatus** (alembic+cucurbit assembly). Present wherever distillation occurs. The l(state) + c(adjust) + h(watch) composition reads "maintain adjusted observation" — the operator monitors the apparatus. |
| **lk** | 15/19 | state.heat | **Fire/furnace** (heat source infrastructure). Present wherever sustained heating occurs. l(state) + k(heat) = "heat state" = the thermal infrastructure. |
| **eed** | 10/19 | cool.cool.do | **Cooling step** (vessel cooling between operations). Concentrated on Section S folios (f108r=4x, f112v=6x). The ee(extended cool) + d(do) = "execute extended cooling." |

## Tier 2: Material Class Candidates (appear on 4-8 folios with interpretable patterns)

| Dark MIDDLE | Folios | NOT on | Atom reading | Candidate identification |
|------------|--------|--------|-------------|------------------------|
| **cth** | 9/19 | f77v, f82v (specifications), f107r (minerals), f108r | adjust.transfer.watch | **Organic/biological material** — present on folios with honey, wax, flesh, lunaria, ferment. Absent from mineral-only and specification folios. c(adjust) + t(transfer) + h(watch) = "adjust transfer under observation" — careful handling of delicate biological material. |
| **eet** | 6/19 | f77v, f82v, f107r, f66r, f79r | cool.cool.transfer | **Balneum-processed material** — concentrated on folios where material undergoes gentle bath processing. ee(extended cool) + t(transfer) = "extended cooling transfer" — material collected after gentle processing. |
| **fch** | 6/19 | f75r, f82r, f83r, f84r | flag.adjust.watch | **Mercury/mercury-water** — appears on f107r (quicksilver coagulation), f79r (mercury sublimation), f81v (mercury-water+gold), f78v (mercury-water+sulfur), f108r (separation using mercury). Absent from non-mercury recipes. f(flag) + c(adjust) + h(watch) = "flagged adjusted observation" — special cautionary monitoring for mercury (a volatile, hazardous material). |
| **eckh** | 6/19 | f75r, f77v, f83r, f84r, f107r | cool.adjust.heat.watch | **Lunaria/plant-derived liquid** — strongest concentration on f112v (lunaria→quicksilver, x3). Also on f82r (lunaria maceration), f78v (mercury-water), f76r, f76v, f81v. The e(cool) + ck(adjust.heat) + h(watch) = "cool, carefully heat, watch" — the careful thermal handling required for plant-derived volatile liquids. |
| **lsh** | 7/19 | f79r, f81v, f83r, f84r, f107r, f112r, f112v, f116r | state.sequence.watch | **Ash/fire medium** — concentrated on folios with ash distillation (f76r, f77v, f80r). Also on f78v, f82r, f82v. l(state) + sh(sequence.watch) = "state under sequential observation" — monitoring the fire medium's condition. |
| **p** (standalone) | 8/19 | f75r, f76r, f76v, f77v, f78v, f103r, f108r | pause | **Waiting/resting period** — appears on folios with extended passive processes (putrefaction on f84r, maceration on f82r, sun-curing candidate f107r). p=pause as a standalone MIDDLE may encode a timed waiting step rather than a material. |
| **cs** | Only f84r (x3) | All others | adjust.sequence | **Gold** — exclusive to f84r (gold dissolution) among matched folios. 3 occurrences. c(adjust) + s(sequence) = "sequential adjustment" — the sequential stages of gold treatment. Needs testing: do other gold-working folios in the corpus also show cs? |

## Tier 3: Folio-Exclusive Candidates (appear on 1 matched folio only)

These dark MIDDLEs appear on a single matched folio. They likely encode materials or conditions specific to that recipe. Listed by recipe to show how many "unique labels" each recipe requires.

| Folio | Recipe | Exclusive dark MIDDLEs | Likely encoding |
|-------|--------|----------------------|-----------------|
| **f107r** | Quicksilver coagulation (lead+Hg+sulfur) | aip, air, dk, eock, eotch, kii, oe, okch, okcho, tal, yp (11) | 3 materials + reaction products + apparatus. Highest exclusive count — most specialized vocabulary. |
| **f66r** | Fixation (amalgam) | alch, ctho, eeod, eka, eoct, er, iro, oda, odai, ofar, yd (11) | Amalgam-specific vocabulary. Ring format may require additional positional labels. |
| **f108r** | Element separation (putrefied composite) | alod, dii, eodc, eyt, it, odee, oke, oko, old (9) | Composite material fractions. The recipe produces 4 separate elements — each may get its own label. |
| **f112v** | Lunaria→quicksilver | ald, cf, ocho, oee, oeeeo, yke (6) | Lunaria-specific vocabulary. oeeeo (4 atoms with triple-e) is the most thermally extreme dark MIDDLE in the set. |
| **f80r** | Animal ash chain (flesh+lunaria+bones) | eeyt, eolt, epch, la, rc (5) | Multi-material: capon flesh, lunaria moisture, bones. 5 exclusive labels for a 5-chapter multi-material folio. |
| **f112r** | Red mercury tincture | ea, ete, ody, rain (4) | Ruby liquor + calcination products. rain = respond.into.iterate.bind — could encode the iterative calcination process. |
| **f116r** | Fixation/fusibility test | ala, at, oet, to (4) | Sublimated substance + quicksilver additives. |
| **f81v** | Potable gold | ip, oin, olyd (3) | Gold + mercury-water. Fewer exclusives because materials are shared with other Mercuriorum folios. |
| **f76v** | Ferment conversion | ckhyd, rol, tee (3) | Tincture ferment + substance H. |
| **f82v** | Vessel specification | eecth, eold, yckh (3) | Equipment-specific labels. No materials — these may encode vessel types or operational modes. |
| **f83r** | First distillation (D+C) | fsh, ocph, ty (3) | Substances D and C (cipher-named). Only 3 exclusives — D and C are shared with other Practica recipes. |
| **f79r** | Mercury sublimation | eal, olch (2) | Mercury-water + stone-water. Few exclusives because mercury vocabulary is shared across the pipeline. |
| **f82r** | Lunaria maceration | loch (1) | Single exclusive — lunaria-specific. Most lunaria vocabulary shared with f80r and f112v. |
| **f76r** | Element separation | qk (1) | Single exclusive — the silver plate test. qk may encode silver or the testing plate itself. |
| **f77v** | Furnace specification | alo (1) | Single exclusive — equipment label. |
| **f78v** | Composite ferments | kesh (1) | Single exclusive — sulfur/sweetness. |

## Observations

### 1. Exclusive count correlates with recipe material complexity

| Materials in recipe | Mean exclusive dark MIDDLEs |
|--------------------|---------------------------|
| 3+ distinct materials | 8.0 (f107r=11, f66r=11, f108r=9, f80r=5) |
| 1-2 materials | 3.0 (f112r=4, f116r=4, f81v=3, f76v=3, f82r=1) |
| 0 materials (specs) | 2.0 (f82v=3, f77v=1) |

Recipes with more materials need more identification labels. This is consistent with dark MIDDLEs encoding material identity.

### 2. Mercury vocabulary is shared, not exclusive

fch (mercury candidate) appears on 6 folios — all involving mercury or mercury-water. Mercury is a PIPELINE material that flows through multiple recipes. Its identifier appears wherever it's used, not just where it's first introduced. This is consistent with C1901 (dark MIDDLEs are PREFIX-locked identification vocabulary deployed across multiple contexts).

### 3. Specification folios have few exclusives

f77v (furnace spec) and f82v (vessel spec) have only 1 and 3 exclusive dark MIDDLEs respectively. Specifications describe EQUIPMENT that is shared across all recipes — most of their dark vocabulary is shared, not exclusive. Their few exclusives may encode specific equipment configurations rather than materials.

### 4. The atom compositions are interpretable

Dark MIDDLEs are NOT random character sequences. Their atom compositions produce readable operational-property descriptions:
- fch = flag.adjust.watch = "flagged for cautious monitored handling" → volatile mercury
- cth = adjust.transfer.watch = "careful transfer under observation" → delicate organic material
- eet = cool.cool.transfer = "extended-cooling transfer" → balneum product
- lch = state.adjust.watch = "maintained adjusted observation" → apparatus requiring constant attention

The labels describe HOW the named thing behaves operationally, not WHAT it is chemically. This is consistent with C171 (semantic ceiling) and C120 (PURE_OPERATIONAL).

---

## Next Steps

1. **Test cs = gold:** Check whether cs appears on other gold-working folios outside the matched set
2. **Test fch = mercury:** Check fch concentration across ALL 83 B folios, not just the 19 matched ones
3. **Test eet = organic:** Verify that eet is absent from mineral-only folios corpus-wide
4. **Cross-reference with Currier A:** Dark MIDDLEs derive from A's registry (C1903: 78% spawn RI). Do the A-system records for these dark MIDDLEs support the material identifications?
5. **Test the exclusive-count correlation** on the remaining matched folios (reverse-blind set)

---

*This document is Tier 4 exploratory work. No findings are registered as constraints. For the constraint system, see `context/CLAIMS/INDEX.md`.*
