# Dark Pipeline Dictionary

**Status:** COMPREHENSIVE (Tier 3-4) | **Date:** 2026-04-02
**Method:** Manual reading of every dark pipeline token on 19 recipe-matched folios against Latin/English recipe text, position by position. Corpus-wide validation on all 82 Currier B folios for high-frequency candidates.

> **Caveat:** Dark pipeline MIDDLEs encode identification vocabulary — they label things by operational properties, not by name. The readings below describe HANDLING PROFILES, not chemical identities. "fch = mercury" means "fch appears wherever mercury is handled" and "fch's atoms read as flag.adjust.watch = hazardous material requiring cautious monitoring." The practitioner maps behavior to substance through domain knowledge.

---

## Three Functional Classes (C1941)

Dark pipeline MIDDLEs divide into three classes based on folio distribution and recipe correspondence:

### Class 1: Equipment Identifiers (universal — appear on 10+ folios)

| MIDDLE | Atoms | Reading | Corpus |
|--------|-------|---------|--------|
| lch | state.adjust.watch | Distillation apparatus | 65/82 |
| lk | state.heat | Fire/furnace state | 60/82 |
| eed | cool.cool.do | Extended cooling execution | 35/82 |

### Class 2: Process Identifiers (technique-specific — appear on 3-9 folios)

| MIDDLE | Atoms | Reading | Folios |
|--------|-------|---------|--------|
| cth | adjust.transfer.watch | State-transition monitoring | 9/19 |
| lsh | state.sequence.watch | Phase-boundary observation regime | 7/19 |
| eet | cool.cool.transfer | Cooling transfer operation | 6/19 |
| ksh | heat.sequence.watch | Sequential thermal observation | 4/19 |
| ir | iterate.respond | Iteration scaffold | 4/19 |
| eke | cool.heat.cool | Precision quality assessment | 3/19 |
| tsh | transfer.sequence.watch | Cohobation / return-distillation | 3/19 |
| ro | respond.arrange | Fermentation response | 3/19 |
| ep | cool.pause | Cooling pause test | 3/19 |
| cfh | adjust.flag.watch | Flagged quality assessment | 3/19 |
| dyt | do.end.transfer | Complete material transfer | 3/19 |
| es | cool.sequence | Cooling sequence check | 3/19 |
| ta | transfer.yield | Thermal transfer yield at transitions | 3/19 |
| octh | arrange.adjust.transfer.watch | Careful material transfer arrangement | 3/19 |
| ockh | arrange.adjust.heat.watch | Ash bed / heated arrangement | 3/19 |
| eok | cool.arrange.heat | Gentle fire / thermal arrangement test | 3/19 |

### Class 3: Material Identifiers (substance-specific — enriched on specific recipe types)

**Corpus-validated:**

| MIDDLE | Atoms | Reading | Corpus | Enrichment |
|--------|-------|---------|--------|-----------|
| fch | flag.adjust.watch | Mercury / mercury-water | 19/82 | ∞ |
| eckh | cool.adjust.heat.watch | Volatile liquid (plant or mineral) | 18/82 | ∞ |
| rai | respond.yield.iterate | Metallic product/fraction | 11/82 | 2.59x |
| cs | adjust.sequence | Gold | 9/82 | 17.5x |

**Folio-exclusive (selected — see Tier 4 section below for full list):**

| MIDDLE | Folio | Reading |
|--------|-------|---------|
| loch | f82r | Lunaria moisture |
| rol | f76v | Tincture ferment |
| ea | f112r | Ruby liquor |
| fsh | f83r | Lute compound (linen+flour+egg) |
| alod | f108r | Aludel (ash-phase vessel) |
| olyd | f81v | Gold solution |

---

## Detailed Entries

## Tier 1: Universal Equipment/Process Identifiers

These appear on 10+ matched folios. They encode shared apparatus or universal operations.

| Dark MIDDLE | Atoms | Folios | Corpus | Reading | Evidence |
|------------|-------|--------|--------|---------|---------|
| **lch** | state.adjust.watch | 16/19 | 65/82 | **Distillation apparatus** (alembic+cucurbit assembly). Appears wherever distillation occurs. Different PREFIXes encode different operational states: qo+lch = apparatus under heat, so+lch = apparatus in sequential mode, po+lch = apparatus paused, da+lch = apparatus being set up. | 6x on f76r (distillation-intensive), 5x on f83r, 4x on f82v (vessel spec). Always at apparatus-related positions. |
| **lk** | state.heat | 15/19 | 60/82 | **Fire/furnace state**. The current thermal condition of the heat source. Different PREFIXes: qo+lk = operational fire, so+lk = sequential fire management, da+lk = fire setup, po+lk = paused fire. | 4x on f80r, 3x on f83r (triple on furnace-shutdown line L41), 3x on f82v, 3x on f108r. |
| **eed** | cool.cool.do | 10/19 | 35/82 | **Extended cooling execution**. Execute a double-cooled operation — condensation, vessel cooling between phases, balneum-depth cooling action. | 6x on f112v (iterative balneum recipe), 4x on f108r (two-phase cooling-intensive), 3x on f116r (sublimation condensation), 3x on f76r. Tracks balneum proportion in recipes. |

## Tier 2: Material/Process Identifiers (Corpus-Validated)

| Dark MIDDLE | Atoms | Folios | Corpus | Enrichment | Reading | Evidence |
|------------|-------|--------|--------|-----------|---------|---------|
| **fch** | flag.adjust.watch | 6/19 | 19/82 | **∞** (mercury vs non-mercury) | **Mercury / mercury-water**. Flagged for cautious monitored handling — mercury is volatile, toxic, requires constant vigilance. | Present on ALL mercury-recipe folios (f79r, f81v, f82v, f78v, f107r, f108r). Absent from ALL non-mercury matched folios. f107r L27: double fch flanking mercury coagulation step. |
| **cs** | adjust.sequence | 1/19 (3x) | 9/82 | **17.5x** (gold vs non-gold) | **Gold**. Sequential staged treatment. Gold requires multi-step processing (dissolve, putrefy, wash, separate). | 3x on f84r (gold dissolution) at L1 (introduction), L28 (mid-putrefaction), L30 (near completion) — maps the arc of gold treatment. f84v (same leaf) has 2x. 9/82 corpus folios, concentrated in Section B Mercuriorum neighborhood. |
| **eckh** | cool.adjust.heat.watch | 6/19 | 18/82 | **∞** (lunaria vs mineral-only) | **Volatile liquid requiring careful thermal management**. Applies to both plant extracts (lunaria) AND volatile mineral distillates. | 3x on f112v (lunaria→quicksilver), 2x on f78v (mercury-water dissolution), 1x on f76r (mineral distillate), f82r (lunaria maceration), f76v, f81v. Zero on mineral-only folios without liquid handling. |
| **cth** | adjust.transfer.watch | 9/19 | 35/82 | N/A (process, not material) | **State-transition monitoring**. Watching material change from one state to another — color change, phase change, dissolution, coagulation. NOT a material identifier. | 5 folios confirmed: f75r (distillate quality), f84r (nigredo/blackening), f82r (maceration completion), f76v (ferment readiness), f112r (cohobation state). Always at transition-watching positions. |
| **eke** | cool.heat.cool | 3/19 | 12/82 | N/A (process) | **Precision quality assessment**. Thermal precision check of material quality — testing purity, readiness, composition. | f75r L2 (honey quality), f76r L12 (distillate purity near silver-plate test), f79r L35 (final sublimation check). Always at quality-testing positions. |
| **eet** | cool.cool.transfer | 6/19 | 16/82 | **3.07x** (balneum) | **Cooling transfer operation**. Applying external cooling to the vessel (cold cloths, condenser cooling) or collecting cooled distillate. | f75r L35,37 (cold cloths around cucurbit during fermentation), f76v L10,20 (balneum cooling transfer), f112r L24,25 (cohobation distillate cooling), f78v L30 (final moisture transfer). |
| **ksh** | heat.sequence.watch | 4/19 | 14/82 | N/A (process) | **Sequential thermal observation**. Watching a heating process step by step — boil-and-skim, drop-counting, monitoring sublimate rise, watching distillation progress. | f75r L7,19 (boil-and-skim), f79r L10,24 (distillation monitoring), f83r L4,14 (sawdust fire + graduated fire), f76v L25 (binding monitoring). |
| **lsh** | state.sequence.watch | 7/19 | 14/82 | **3.46x** (ash folios) | **Establish observation regime at phase boundary**. Marks transitions between operational phases — setting up sequential monitoring for a new processing mode. | f75r L27 (balneum start), f76r L18,33,46 (phase transitions), f82r L7 (pre-sealing), f78v L3,12, f82v L5(x2),16 (vessel naming sequence). Also enriched on ash-distillation folios. |
| **rai** | respond.yield.iterate | 4/19 | 11/82 | **2.59x** (metallic) | **Metallic product/fraction**. The iteratively-yielded responsive product from metal-working processes. | f76r L8 (mineral distillate), f107r L1 (lead earth), f112r L21 (red mercury tincture), f66r L2 (fixation yield cycle). Concentrated on Section S (metallic processing). |

## Tier 3: Confirmed Process/Operation Identifiers

| Dark MIDDLE | Atoms | Folios | Reading | Evidence |
|------------|-------|--------|---------|---------|
| **tsh** | transfer.sequence.watch | 3/19 | **Cohobation / sequential transfer observation**. Watching material transfer from one vessel/state to another, especially during cohobation (returning distillate over residue). | 4x on f79r (mercury cohobation), 1x on f82v (vessel transfer spec). Concentrated where recipes describe return-distillation. |
| **ro** | respond.arrange | 3/19 | **Fermentation response**. The material responding and rearranging itself during fermentation. Process identifier, not material. | f76v L25 (after H-joining), f103r L8 (paragraph-initial in ferment multiplication), f77v L16 (furnace for fermentation). All ferment-context folios. |
| **ep** | cool.pause | 3/19 (5x) | **Cooling pause test**. Testing whether material has cooled/settled sufficiently between operations. | f76r L2,18 (both ch-PREFIX = active test), f103r L2,21,22 (multiplication cycle cooling checks), f83r L1. |
| **cfh** | adjust.flag.watch | 3/19 | **Flagged quality assessment**. Periodic quality checks marked as noteworthy — flagging material state at critical junctures. | f76r L1 (initial material assessment), f84r L8 (balneum periodic check), f108r L2 (seal flagging). |
| **dyt** | do.end.transfer | 3/19 | **Complete material transfer**. The action of finishing a material movement — transferring a completed product. | f84r L1 (silver water transfer), f79r L15 (post-distillation transfer), f76v L22 (pre-joining transfer). |
| **es** | cool.sequence | 3/19 | **Cooling sequence check**. Verifying the cooling sequence is proceeding correctly during sustained processes. | f75r L14 (post-9x-cycle check), f82r L24 (maceration cooling check), f78v L23 (bath distillation check). |
| **ta** | transfer.yield | 3/19 | **Thermal transfer yield at transitions**. The heat source producing a yield at phase-transition points. | f76r L16 (before silver-plate test), f79r L34 (late sublimation), f77v L16 (furnace operation). |
| **ir** | iterate.respond | 4/19 | **Iteration scaffold**. The structural framework for repeat loops — setting up the iterative cycling architecture. | f77v L21, f81v L10, f116r L21, f107r L42. Always at positions where iterative cycles are being established. |
| **octh** | arrange.adjust.transfer.watch | 3/19 | **Careful material transfer arrangement**. Arranging material during a monitored, adjusted transfer operation. | f82r L4 (placing lunaria on flesh), f112v L20 (pouring animated water over dregs), f80r L1 (vessel arrangement). |
| **ockh** | arrange.adjust.heat.watch | 3/19 | **Ash bed / heated arrangement**. The arrangement of heated substrate (ash, sand) around vessels. | f83r L19 (ashes 5 fingers deep), f108r L9,47 (ash-phase distillation), f107r L41 (projection heating). |
| **eok** | cool.arrange.heat | 3/19 | **Gentle fire application / thermal arrangement test**. Testing the thermal arrangement after cooling — verifying the correct heat regime. | f108r L6,37 (balneum gentle fire), f80r L38 (final thermal test), f66r L28 (fixation thermal reversal). |

## Tier 4: Folio-Exclusive Material Candidates

Each appears on only one matched folio, likely encoding recipe-specific materials or conditions.

| Dark MIDDLE | Folio | Recipe | Atoms | Reading |
|------------|-------|--------|-------|---------|
| **loch** | f82r | Lunaria maceration | state.arrange.adjust.watch | **Lunaria moisture handling profile** — the material in its maceration vessel, arranged, adjusted, watched. |
| **rol** | f76v | Ferment conversion | respond.arrange.state | **Tincture ferment** — the prepared ferment in its responsive arranged state. |
| **olyd** | f81v | Potable gold | arrange.state.end.do | **Gold solution completion** — the gold dissolving to its terminal state. |
| **ea** | f112r | Red tincture | cool.yield | **Ruby liquor** — the cooled yielded product specific to this recipe. |
| **rain** | f112r | Red tincture | respond.yield.iterate.bind | **Cohobation tincture product** — the iteratively bound product of repeated cohobation. |
| **alo** | f77v | Furnace spec | yield.state.arrange | **Specific furnace type** — a particular furnace arrangement. |
| **fsh** | f83r | First distillation | flag.sequence.watch | **Lute compound** — the sealing material (linen+flour+egg) applied in flagged, sequenced layers. |
| **ocph** | f83r | First distillation | arrange.adjust.pause.watch | **Cucurbit spacing arrangement** — the 2-3 cucurbits spaced 5-6 fingers apart. |
| **odee** | f108r | Element separation | arrange.do.cool.cool | **Uncovering the vessel** — removing the cover (exposing to ambient cooling). First token on folio. |
| **alod** | f108r | Element separation | yield.state.arrange.do | **Aludel** — the specific vessel for ash-phase distillation. f108r-exclusive. |
| **dii** | f108r | Element separation | do.iterate.iterate | **Gradually strengthen fire** — double iteration = gradual incremental increase. f108r-exclusive. |
| **eock** | f107r | Quicksilver coagulation | cool.arrange.adjust.heat | **Lead earth thermal preparation** — cool first, arrange, adjust, then heat. Mineral-specific. |
| **otch/eotch** | f107r | Quicksilver coagulation | arrange.transfer.adjust.watch | **Sulfur vapor collection apparatus** — the transfer arrangement for collecting volatile sulfur. eotch adds e(cool) = the condensation side. |
| **kii** | f107r | Quicksilver coagulation | heat.iterate.iterate | **Intensified iterative heating** — the most intense heating mode. Double iteration under heat. |
| **eee** | f107r, f112r, f112v | Various | cool.cool.cool | **Maximum cooling depth** — the deepest possible thermal modulation. Triple-cool = extreme balneum or deep condensation. |
| **ara** | f112v, f82v | Lunaria separation; Vessel spec | yield.respond.yield | **Mutual embrace / bidirectional yield** — two materials yielding to each other. f112v: "elements embrace." f82v: vessel's two-way function. |

## Summary Statistics

| Metric | Value |
|--------|-------|
| Dark tokens analyzed | 466 |
| Unique dark MIDDLEs on matched folios | 152 |
| MIDDLEs with candidate readings | 152 (100%) |
| Tier 1 (universal, HIGH confidence) | 3 |
| Tier 2 (corpus-validated, HIGH confidence) | 8 |
| Tier 3 (multi-folio process, MEDIUM confidence) | 11 |
| Tier 4 (folio-exclusive, LOW-MEDIUM confidence) | 16+ |
| Corpus-wide validation performed | 7 candidates tested, 6 supported |
| Material identifiers with ∞ enrichment | 2 (fch=mercury, eckh=volatile liquid) |

## Key Findings

### 1. The dark pipeline encodes three functional classes

**Equipment identifiers** (lch, lk, olo, ockh): Name apparatus components and fire states. Appear universally across recipes because equipment is shared.

**Process identifiers** (cth, eke, ksh, tsh, ro, ep, eok, lsh): Name specific operational techniques — state-transition monitoring, precision testing, sequential observation, cohobation, fermentation. Appear wherever that technique is used, regardless of material.

**Material identifiers** (fch, cs, eckh, rai, + folio-exclusives): Name specific materials by their handling profiles. fch=mercury (hazardous flagged handling), cs=gold (sequential staged treatment), eckh=volatile liquid (careful thermal management), rai=metallic product (iterative yield response).

### 2. Exclusive count correlates with recipe complexity

| Recipe complexity | Mean exclusive dark MIDDLEs |
|------------------|---------------------------|
| 3+ distinct materials | 8.0 |
| 1-2 materials | 3.0 |
| 0 materials (specifications) | 2.0 |

### 3. Atom compositions produce operationally coherent readings

Every dark MIDDLE decomposes into atoms that describe the HANDLING PROFILE of the identified thing:
- fch (mercury) = flag.adjust.watch = "flagged for cautious monitoring" — mercury IS hazardous
- cs (gold) = adjust.sequence = "sequential adjustment" — gold IS processed in stages
- lch (apparatus) = state.adjust.watch = "maintained adjusted observation" — apparatus IS constantly monitored
- eet (cooling transfer) = cool.cool.transfer = "extended cooling transfer" — condenser cooling IS a double-cool transfer

The dark pipeline doesn't NAME things — it describes how they BEHAVE operationally.

### 4. PREFIX variation encodes operational mode

The same dark MIDDLE takes different PREFIXes to encode different operational contexts:
- qo+lch = apparatus under active heating
- so+lch = apparatus in sequential processing mode
- po+lch = apparatus paused between operations
- da+lch = apparatus being set up

This is consistent with the PREFIX domain-selector model (C570, C936) — the PREFIX says WHAT CONTEXT the identified thing is in.

---

## Predictions

### fch = mercury: 13 unmatched folios have fch
f31r, f39r, f40v, f50r, f66v, f85r1, f86v3, f103v, f106v, f111r, f113r, f113v, f115r

If fch=mercury holds, these folios should involve mercury processing. f103v and f85r1 are already confirmed reverse-blind matches that DO involve mercury — supporting the prediction.

### cs = gold: 7 unmatched folios have cs
f75v, f78r, f80r, f84v, f85r2, f86v3, f95v2, f103v

f84v is the VERSO of f84r (gold dissolution) — gold on both sides of the same leaf.

---

*This document is Tier 3-4 exploratory work. Material identifications (fch, cs, eckh) with corpus-validated enrichment are approaching Tier 2. Universal equipment identifiers (lch, lk, eed) are Tier 2. For the constraint system, see `context/CLAIMS/INDEX.md`.*
