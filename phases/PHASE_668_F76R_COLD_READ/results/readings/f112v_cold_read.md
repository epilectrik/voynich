# Validated Reading: f112v ↔ III.1.0 Lunaria → Quicksilver Pipeline

**Match tier:** Supported
**Expert verdict:** Coherent (6/8 structural predictions confirmed, 2 partial)
**Full token listing:** `data/f112v_cold_read.txt` (415 tokens, 54 lines)

---

## How to Read This Document

This recipe is 528 words. This folio is 415 tokens — a 0.8:1 ratio, the only folio with FEWER tokens than recipe words. III.1.0 is the opening chapter of the Liber Mercuriorum, describing the complete pipeline for creating quicksilver from lunaria. It is one of the longest and most operationally complex recipes in the Testamentum, with 13+ distinct steps involving multiple thermal regimes (balneum → ash fire → cooling → gentle fire → desiccation).

The folio's e-depth traces a distinctive three-regime profile: balneum peak (1.41 at P6, where the recipe says "en bany marie"), cooling valley (0.30-0.60 at P9-P11), and dry-fire decline (0.30-0.42 at P13-P15, where the recipe specifies gentle fire for desiccation). The zero-qo paragraph (P9, 5 tokens) maps to "lexa refradar la materia" (let the material cool).

**What makes this match credible:**
- **e-depth peak at P6** (1.41) exactly where recipe says "en bany marie"
- **Zero-qo cooling paragraph** (P9, 5 tokens) at "let the material cool"
- **e-depth crash to 0.30** at P13 — autonomous balneum distillation signature
- **fch mercury marker** in P1 (C1939) where recipe introduces "liquor mercuriall"
- **dar distributed across 8 paragraphs** matching material-intensive multi-step recipe
- **15 paragraphs appropriate** for a 13+ step recipe

**Honest gaps:** The verification table for this folio shows Phase 641 atom-decode rated it WEAK (DOES NOT SUPPORT). The expert positive control's COHERENT verdict is based on structural pattern matching, which is a different evidence type than atom-level operational scoring.

Every token on every line appears in this document.

---

## The Recipe

### Catalan (III.1.0, SISMEL — Part III cipher: B=simple water, D=simple dissolved gold, E=compound red water)

> Fill, t'és ops que entenes les operacions per les quals se creen los nostres argents vius. Tu pendràs de la liquor mercuriall o lunaria quant en volràs, e de aquella per distillació departiràs les elements. Mas primerament separaràs l'aygua fleumatica en la qual està mortificat lo esperit. E continua en bany ta distillació en tro que veies distillar per l'aygua animada que comença a cremar. E aquella distilla a part. E aquella partiràs en dues parts: e la una part guardaràs per crear los mercuries; e de la segona trauràs los elements sens tota combustió. En aquesta manera tu mettràs la dita part de l'aygua animada sobre les feces. E tantost mit lo alembich dessús ab ton receptor, e encén lo foch de serradura composta. E aquell se continue en tro tot ço que porà distillar sia distillat per equalitat del dit foch. E soit fet ceste distillacion en bany marie. Aprés mit-ho en foch sech cinerench ab aquell continuitat de serradura; distilla lo oli, e a la fi de la distillació lexa refradar la materia ab tot lo vexell. Puys retorna la primera liquor sobre les feces e reitera ta distillació, en tro que les feces esteguen totes seques e arses.

### English

Son, you must understand the operations for creating quicksilvers. Take mercurial liquor (lunaria) and separate the elements by distillation. First separate the phlegmatic water where the spirit is mortified. Continue balneum distillation until you see animated water begin to burn. Distill that aside; divide into two parts (one for creating mercuries, from the other extract elements without combustion). Put the animated water on the dregs (like melted pitch at vessel bottom). Set up alembic with receptor, light composed sawdust fire. Continue until all distills by equality of fire — do this in balneum mariae. Then put in dry ash fire with sawdust; distill the oil. At end of distillation, let the material cool with the vessel. Return first liquor to dregs, repeat distillation until dregs are dry and burnt.

### Recipe Structure

| Step | Operation | Heat | Key feature |
|------|-----------|------|-------------|
| 1 | Take lunaria liquor | — | mercury introduction |
| 2 | Separate phlegmatic water | balneum | first distillation |
| 3 | Continue until animated water burns | balneum | quality gate: burning |
| 4 | Distill animated water aside | balneum | separation |
| 5 | Divide into two parts | — | split |
| 6 | Put animated water on dregs | — | material combination |
| 7 | Set up alembic + receptor | — | apparatus |
| 8 | Sawdust fire distillation | sawdust fire | "en bany marie" |
| 9 | Switch to dry ash fire — distill oil | ash fire | regime change |
| 10 | Let material cool with vessel | **no heat** | "lexa refradar" |
| 11 | Return liquor to dregs | — | cohobation return |
| 12 | Repeat until dregs dry + burnt | gentle fire | iterative desiccation |
| 13 | Continue gentle fire until elements bind | gentle fire | final desiccation |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | 15 paragraphs appropriate | 13+ operational steps | **MATCH** — 15 paragraphs |
| 2 | Multiple thermal regimes | balneum → ash → cooling → gentle | **MATCH** — 3 distinct regimes visible |
| 3 | e-depth arc with variation | balneum high, ash lower, cooling zero, gentle moderate | **MATCH** — peak 1.41, valley 0.30 |
| 4 | Significant dar count | multiple material additions/returns | **MATCH** — 10 dar across 8 paragraphs |
| 5 | Quality gate at animated water | "en tro que veies" (until you see) | **PARTIAL** — observation tokens present but not strongly localized |
| 6 | Cooling phase with near-zero heat | "lexa refradar la materia" | **MATCH** — P9 zero qo, 5 tokens |
| 7 | Iterative structure (return + repeat) | "reitera ta distillació" | **PARTIAL** — iteration tokens distributed |
| 8 | fch mercury marker | mercury is central subject | **MATCH** — fch in P1 |

**Score: 6/8 confirmed, 2 partial**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 415 |
| Lines | 54 |
| Paragraphs | 15 |
| dar (material-add) | 10 |
| Quality checks (chek/shek class) | 4 |
| Observation MIDDLEs | cfh×1, ckh×1, cth×1 |
| hh (extended observation) | 0 |

---

## Paragraph 1: Lines 1-6 (52 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L1 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| keeoal | ke | Balneum: bring to stable state | Comp-v2 |
| chool | ch | Test: hold current state | Comp-v2 |
| opal | --- | *unrecognized* (set up, pause, bring to, hold) | --- |
| otalair | ot | Output: bring to and note result | Comp-v2 |
| y | --- | Done -- bare completion marker | B Dict D2 |
| fcheol | fch | Mercury marker (C1939): hold current state | Comp-v2 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| qor | qo | Fire: respond | Comp-v2 |
| eees | --- | *unrecognized* (steady, steady, steady, sequence) | --- |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |

→ 8/10 recognized (80%).

**L2 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| oar | --- | *bare token: set up, bring to, respond* | --- |
| osal | --- | *unrecognized* (set up, sequence, bring to, hold) | --- |
| okeeshy | ok | Vessel: watch sequence steady | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| okain | ok | Vessel: seal for a processing cycle | B Dict D1 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| okeol | ok | Vessel: hold current state | Comp-v2 |
| oty | ot | Output: transfer complete -- drip/flow has ceased | B Dict D2 |
| oraiin | or | Note what happened: extended iteration cycles | Comp-v2 |

→ 7/9 recognized (77%).

**L3 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokeeor | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| aiiin | --- | *unrecognized* (bring to, iterate, iterate, iterate, bind) | --- |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| lkeeody | lk | Check equipment: steady, steady, set up, do | Comp-v2 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| qotam | qo | Fire: transfer, bring to, finalize | Comp-v2 |

→ 9/10 recognized (90%).

**L4 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| shody | sh | Watch: set up, do | Comp-v2 |
| qo | --- | *bare token: q, set up* | --- |
| oeeeody | --- | *unrecognized* (set up, steady, steady, steady, set up, do, ) | --- |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |

→ 7/9 recognized (77%).

**L5 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| aiiin | --- | *unrecognized* (bring to, iterate, iterate, iterate, bind) | --- |
| okey | ok | Vessel: steady | Comp-v2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| otal | ot | Output: monitor transfer rate until output stabilizes | B Dict D2 |
| chear | ch | Test: bring to and note result | Comp-v2 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| cheeoldy | ch | Test: holding, confirmed | Comp-v2 |

→ 8/9 recognized (88%).

**L6 (5 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| oaiin | --- | *unrecognized* (set up, bring to, iterate, iterate, bind) | --- |
| okeeedy | ok | Vessel: steady, steady, steady, do | Comp-v2 |
| cheaikhy | ch | Test: heat through one cycle | Comp-v2 |

→ 4/5 recognized (80%).


### P1 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 52 (12% of folio) |
| e-depth | 0.808 |
| dar count | 1 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ok: 9 (17%)
- qo: 8 (15%)
- ot: 5 (9%)
- ch: 4 (7%)
- sh: 3 (5%)
- sa: 2 (3%)
- ke: 1 (1%)

---

## Paragraph 2: Lines 7-10 (28 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L7 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pcheokeey | pch | Setup: gentle steady heat — balneum level | Comp-v2 |
| oeeeky | --- | *unrecognized* (set up, steady, steady, steady, heat, ) | --- |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| oeesaiin | --- | *unrecognized* (set up, steady, steady, sequence, bring to, iterate, iterate, bind) | --- |
| oteor | ot | Output: note what happened | Comp-v2 |
| opchdar | --- | *unrecognized* (set up, pause, adjust, watch, do, bring to, respond) | --- |
| opary | --- | *unrecognized* (set up, pause, bring to, respond, ) | --- |

→ 3/7 recognized (42%).

**L8 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ocheor | --- | *unrecognized* (set up, adjust, watch, steady, set up, respond) | --- |
| okor | ok | Vessel: note what happened | Comp-v2 |
| aiiin | --- | *unrecognized* (bring to, iterate, iterate, iterate, bind) | --- |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| okal | ok | Vessel: contents settling -- let them stabilize | B Dict D2 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| otal | ot | Output: monitor transfer rate until output stabilizes | B Dict D2 |
| kedy | ke | Standard heat cycle complete | B Dict D2 |
| chekaiiin | ch | Test: sustained deep heating cycles | Comp-v2 |

→ 7/9 recognized (77%).

**L9 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| soaiin | so | Sequence: extended iteration cycles | Comp-v2 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| iiin | --- | *unrecognized* (iterate, iterate, iterate, bind) | --- |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| cheekain | ch | Test: gentle steady heat — balneum level | Comp-v2 |
| okchedy | ok | Vessel: adjust, watch, steady, do | Comp-v2 |
| qokchdy | qo | Fire: heat with active test adjustment, cycle close | B Dict D2 |

→ 7/8 recognized (87%).

**L10 (4 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dain | da | Load: secure material for next run | B Dict D1 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| okchedy | ok | Vessel: adjust, watch, steady, do | Comp-v2 |
| oror | or | Note what happened: note what happened | Comp-v2 |

→ 4/4 recognized (100%).


### P2 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 28 (6% of folio) |
| e-depth | 0.643 |
| dar count | 1 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ok: 6 (21%)
- ot: 4 (14%)
- qo: 2 (7%)
- ch: 2 (7%)
- pch: 1 (3%)
- ke: 1 (3%)
- so: 1 (3%)

---

## Paragraph 3: Lines 11-14 (35 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L11 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tchor | tch | Transfer-check: note what happened | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| odeedy | --- | *unrecognized* (set up, do, steady, steady, do, ) | --- |
| oteeey | ot | Output: steady, steady, steady | Comp-v2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| lody | --- | *unrecognized* (hold, set up, do, ) | --- |
| chcfhy | ch | Test: adjust, flag, watch | Comp-v2 |
| ochos | --- | *unrecognized* (set up, adjust, watch, set up, sequence) | --- |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| olky | ol | Steady: set — stop adjusting | Comp-v2 |

→ 7/10 recognized (70%).

**L12 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| olkeedain | ol | Steady: one gentle balneum cycle | Comp-v2 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| sheeol | sh | Watch: hold current state | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qochaiin | qo | Fire: extended iteration cycles | Comp-v2 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| qoty | qo | Fire: transfer complete -- stop moving material | B Dict D2 |

→ 9/9 recognized (100%).

**L13 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dcheoty | dch | Setup-check: transfer and hold | Comp-v2 |
| oy | --- | *bare token: set up, * | --- |
| otchedy | ot | Output: adjust, watch, steady, do | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| chedal | ch | Test: bring to stable state | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| otam | ot | Output: bring to, finalize | Comp-v2 |

→ 8/9 recognized (88%).

**L14 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| ain | --- | Bring to a binding cycle -- one pass | B Dict D2 |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |
| ykeedain | yk | Adjust: one processing cycle | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| chedaiin | ch | Test: extended iteration cycles | Comp-v2 |
| alain | al | Product settled: one processing cycle | Comp-v2 |

→ 7/7 recognized (100%).


### P3 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 35 (8% of folio) |
| e-depth | 0.743 |
| dar count | 2 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | cfhx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 6 (17%)
- ot: 5 (14%)
- ch: 5 (14%)
- ol: 2 (5%)
- da: 2 (5%)
- tch: 1 (2%)
- sh: 1 (2%)

---

## Paragraph 4: Lines 15-19 (45 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L15 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pchodain | pch | Setup: one processing cycle | Comp-v2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| olkeedy | ol | Steady: hold gentle heat -- maintain balneum level | B Dict D2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| qokedar | qo | Fire: one standard heat cycle | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |

→ 9/9 recognized (100%).

**L16 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| chdaly | ch | Test: bring to stable state | Comp-v2 |

→ 9/9 recognized (100%).

**L17 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| cheeir | ch | Test: steady, steady, iterate, respond | Comp-v2 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| chykeedy | ch | Test: one gentle balneum cycle | Comp-v2 |
| chdaiin | ch | Test: extended iteration cycles | Comp-v2 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| otaldal | ot | Output: bring to stable state | Comp-v2 |

→ 8/8 recognized (100%).

**L18 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| chey | ch | Test: quick active check | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qokeeey | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| qokeeody | qo | Fire: one gentle balneum cycle | Comp-v2 |
| qotam | qo | Fire: transfer, bring to, finalize | Comp-v2 |
| olaiin | ol | Steady: extended iteration cycles | Comp-v2 |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |

→ 10/10 recognized (100%).

**L19 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sarain | sa | Scaffold: one processing cycle | Comp-v2 |
| ain | --- | Bring to a binding cycle -- one pass | B Dict D2 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| qoeeey | qo | Fire: steady, steady, steady | Comp-v2 |
| qoteo | qo | Fire: transfer and hold | Comp-v2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| aiiin | --- | *unrecognized* (bring to, iterate, iterate, iterate, bind) | --- |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| chalor | ch | Test: bring to and note result | Comp-v2 |

→ 8/9 recognized (88%).


### P4 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 45 (10% of folio) |
| e-depth | 0.911 |
| dar count | 1 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 14 (31%)
- ch: 9 (20%)
- sa: 3 (6%)
- ok: 2 (4%)
- ol: 2 (4%)
- sh: 2 (4%)
- pch: 1 (2%)

---

## Paragraph 5: Lines 20-24 (42 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L20 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pchoraiin | pch | Setup: extended iteration cycles | Comp-v2 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| alchedy | al | Product settled: adjust, watch, steady, do | Comp-v2 |
| olkeedy | ol | Steady: hold gentle heat -- maintain balneum level | B Dict D2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qotaiin | qo | Fire: sustained transfer cycles -- repeated distillation passes | B Dict D2 |
| chocthedy | ch | Test: observe material moving | Comp-v2 |
| sairal | sa | Scaffold: bring to and note result | Comp-v2 |

→ 8/8 recognized (100%).

**L21 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| chekain | ch | Test: heat through one cycle | Comp-v2 |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| qoeedy | qo | Fire: system steady, confirmed | Comp-v2 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokeol | qo | Fire: heat and hold | Comp-v2 |
| kain | ka | Apply heat through one processing cycle | B Dict D2 |

→ 10/10 recognized (100%).

**L22 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| soiin | so | Sequence: iterate, iterate, bind | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| chetain | ch | Test: one processing cycle | Comp-v2 |

→ 6/6 recognized (100%).

**L23 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ycheol | ch | Test: hold current state | Comp-v2 |
| keeor | ke | Balneum: note what happened | Comp-v2 |
| olkeeey | ol | Steady: gentle steady heat — balneum level | Comp-v2 |
| chedain | ch | Test: one processing cycle | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| cheedaiin | ch | Test: extended iteration cycles | Comp-v2 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qotain | qo | Fire: transfer through one processing cycle | B Dict D2 |

→ 9/9 recognized (100%).

**L24 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| soiin | so | Sequence: iterate, iterate, bind | Comp-v2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| okain | ok | Vessel: seal for a processing cycle | B Dict D1 |
| otchedy | ot | Output: adjust, watch, steady, do | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| eeedeed | --- | *unrecognized* (steady, steady, steady, do, steady, steady, do) | --- |
| ckhedy | --- | *unrecognized* (adjust, heat, watch, steady, do, ) | --- |
| cheedaiin | ch | Test: extended iteration cycles | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |

→ 7/9 recognized (77%).


### P5 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 42 (10% of folio) |
| e-depth | 0.929 |
| dar count | 0 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 12 (28%)
- qo: 9 (21%)
- ol: 2 (4%)
- sa: 2 (4%)
- ke: 2 (4%)
- sh: 2 (4%)
- so: 2 (4%)

---

## Paragraph 6: Lines 25-26 (17 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L25 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pchdaiin | pch | Setup: extended iteration cycles | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| qokeeey | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| lkeeedy | lk | Check equipment: steady, steady, steady, do | Comp-v2 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| lor | --- | Hold and note the result | B Dict D3 |
| eeedy | --- | *unrecognized* (steady, steady, steady, do, ) | --- |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |

→ 9/10 recognized (90%).

**L26 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ychedal | ch | Test: bring to stable state | Comp-v2 |
| checkhey | ch | Test: temperature check (gentle level) | Comp-v2 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |
| cheeol | ch | Test: hold current state | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qoteosam | qo | Fire: transfer and hold | Comp-v2 |
| chos | ch | Test: set up, sequence | Comp-v2 |

→ 7/7 recognized (100%).


### P6 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 17 (4% of folio) |
| e-depth | 1.412 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 7 (41%)
- qo: 4 (23%)
- pch: 1 (5%)
- sh: 1 (5%)
- ot: 1 (5%)
- lk: 1 (5%)

---

## Paragraph 7: Lines 27-29 (28 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L27 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pchodain | pch | Setup: one processing cycle | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| teeedy | te | Transfer step: system steady, confirmed | Comp-v2 |
| qoeey | qo | Fire: steady, steady | Comp-v2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qokeear | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| okedal | ok | Vessel: bring to stable state | Comp-v2 |
| olkeedy | ol | Steady: hold gentle heat -- maintain balneum level | B Dict D2 |
| qotedy | qo | Fire: execute a heat-driven transfer operation | B Dict D1 |

→ 10/10 recognized (100%).

**L28 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| shey | sh | Watch: quick passive check | B Dict D1 |
| keedal | ke | Balneum: bring to stable state | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| keeeody | ke | Balneum: steady, steady, set up, do | Comp-v2 |
| qoiin | qo | Fire: iterate, iterate, bind | Comp-v2 |
| ykeey | yk | Adjust: steady, steady | Comp-v2 |
| qokeeey | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| ykeey | yk | Adjust: steady, steady | Comp-v2 |
| qoeey | qo | Fire: steady, steady | Comp-v2 |
| qokaim | qo | Fire: heat through one cycle | Comp-v2 |

→ 11/11 recognized (100%).

**L29 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| qoeekain | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| kain | ka | Apply heat through one processing cycle | B Dict D2 |
| alor | al | Product settled: note what happened | Comp-v2 |
| chedol | ch | Test: hold current state | Comp-v2 |
| sheody | sh | Watch: system steady, confirmed | Comp-v2 |

→ 7/7 recognized (100%).


### P7 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 28 (6% of folio) |
| e-depth | 1.143 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 8 (28%)
- sh: 3 (10%)
- ok: 2 (7%)
- ke: 2 (7%)
- ch: 2 (7%)
- yk: 2 (7%)
- pch: 1 (3%)

---

## Paragraph 8: Lines 30-30 (10 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L30 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polor | po | Pause: hold current state | Comp-v2 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| okeedey | ok | Vessel: steady, steady, do, steady | Comp-v2 |
| sal | sa | Scaffold: hold | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| sheedar | sh | Watch: bring to and note result | Comp-v2 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| qopchedy | qo | Fire: pause, adjust, watch, steady, do | Comp-v2 |
| dalkedy | da | Load: one standard heat cycle | Comp-v2 |
| opchdy | --- | *unrecognized* (set up, pause, adjust, watch, do, ) | --- |

→ 9/10 recognized (90%).


### P8 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 10 (2% of folio) |
| e-depth | 0.900 |
| dar count | 1 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- sh: 2 (20%)
- ok: 2 (20%)
- po: 1 (10%)
- sa: 1 (10%)
- qo: 1 (10%)
- da: 1 (10%)

---

## Paragraph 9: Lines 31-31 (5 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L31 (5 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tar | ta | Transfer and note the yield | B Dict D3 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| okeear | ok | Vessel: bring to and note result | Comp-v2 |
| oteody | ot | Output: system steady, confirmed | Comp-v2 |
| arar | ar | Note the yield: bring to and note result | Comp-v2 |

→ 5/5 recognized (100%).


### P9 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 5 (1% of folio) |
| e-depth | 0.600 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ta: 1 (20%)
- ok: 1 (20%)
- ot: 1 (20%)
- ar: 1 (20%)

---

## Paragraph 10: Lines 32-34 (28 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L32 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tchedor | tch | Transfer-check: note what happened | Comp-v2 |
| shee | sh | Watch: steady, steady | Comp-v2 |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| otedar | ot | Output: bring to and note result | Comp-v2 |
| checphey | ch | Test: steady, adjust, pause, watch, steady | Comp-v2 |
| qopchedy | qo | Fire: pause, adjust, watch, steady, do | Comp-v2 |
| qopcheey | qo | Fire: pause, adjust, watch, steady, steady | Comp-v2 |
| kar | ka | Apply heat and note the response | B Dict D3 |
| opcheeo | --- | *unrecognized* (set up, pause, adjust, watch, steady, steady, set up) | --- |
| raify | --- | *unrecognized* (respond, bring to, iterate, flag, ) | --- |

→ 8/10 recognized (80%).

**L33 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| cheeor | ch | Test: note what happened | Comp-v2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| chedaiin | ch | Test: extended iteration cycles | Comp-v2 |
| okeeedy | ok | Vessel: steady, steady, steady, do | Comp-v2 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| cheekey | ch | Test: gentle steady heat — balneum level | Comp-v2 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |

→ 10/10 recognized (100%).

**L34 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| chedaiin | ch | Test: extended iteration cycles | Comp-v2 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |
| lkeedy | lk | Check furnace: gentle balneum level holds | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| chkaiin | ch | Test: sustained deep heating cycles | Comp-v2 |
| checkhol | ch | Test: temperature check | Comp-v2 |
| chdam | ch | Test: do, bring to, finalize | Comp-v2 |

→ 8/8 recognized (100%).


### P10 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 28 (6% of folio) |
| e-depth | 1.107 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 10 (35%)
- qo: 5 (17%)
- ot: 2 (7%)
- ok: 2 (7%)
- tch: 1 (3%)
- sh: 1 (3%)
- ke: 1 (3%)

---

## Paragraph 11: Lines 35-35 (6 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L35 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pched | pch | Setup: steady, do | Comp-v2 |
| shedain | sh | Watch: one processing cycle | Comp-v2 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |

→ 6/6 recognized (100%).


### P11 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 6 (1% of folio) |
| e-depth | 0.667 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 2 (33%)
- pch: 1 (16%)
- sh: 1 (16%)
- qo: 1 (16%)
- ok: 1 (16%)

---

## Paragraph 12: Lines 36-36 (10 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L36 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tchede | tch | Transfer-check: steady, do, steady | Comp-v2 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| lky | lk | Check equipment: complete | Comp-v2 |
| shedaiiin | sh | Watch: extended iteration cycles | Comp-v2 |
| chdy | ch | Test: check complete | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| cheky | ch | Test: verify the heat level | B Dict D2 |
| lkedy | lk | Check equipment: system steady, confirmed | Comp-v2 |
| qotedy | qo | Fire: execute a heat-driven transfer operation | B Dict D1 |
| raram | ar | Note the yield: bring to, finalize | Comp-v2 |

→ 10/10 recognized (100%).


### P12 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 10 (2% of folio) |
| e-depth | 0.900 |
| dar count | 0 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- lk: 2 (20%)
- ch: 2 (20%)
- qo: 2 (20%)
- tch: 1 (10%)
- ok: 1 (10%)
- sh: 1 (10%)
- ar: 1 (10%)

---

## Paragraph 13: Lines 37-38 (23 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L37 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| teedal | te | Transfer step: bring to stable state | Comp-v2 |
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokedaiin | qo | Fire: one standard heat cycle | Comp-v2 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| kedy | ke | Standard heat cycle complete | B Dict D2 |
| qokam | qo | Fire: heat, bring to, finalize | Comp-v2 |

→ 11/11 recognized (100%).

**L38 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sa | --- | *bare token: sequence, bring to* | --- |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| oiin | --- | *unrecognized* (set up, iterate, iterate, bind) | --- |
| okchey | ok | Vessel: adjust, watch, steady | Comp-v2 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| chedar | ch | Test: bring to and note result | Comp-v2 |
| lkain | lk | Check equipment: one processing cycle | Comp-v2 |
| cheo | ch | Test: steady, set up | Comp-v2 |
| dain | da | Load: secure material for next run | B Dict D1 |

→ 10/12 recognized (83%).


### P13 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 23 (5% of folio) |
| e-depth | 0.304 |
| dar count | 1 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 5 (21%)
- qo: 3 (13%)
- ot: 2 (8%)
- te: 1 (4%)
- sa: 1 (4%)
- sh: 1 (4%)
- ke: 1 (4%)

---

## Paragraph 14: Lines 39-41 (24 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L39 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| teodarody | te | Transfer step: bring to and note result | Comp-v2 |
| opcheed | --- | *unrecognized* (set up, pause, adjust, watch, steady, steady, do) | --- |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| chaiin | ch | Test: extended iteration cycles | Comp-v2 |
| otam | ot | Output: bring to, finalize | Comp-v2 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| qoteey | qo | Fire: gentle steady transfer | Comp-v2 |
| qotain | qo | Fire: transfer through one processing cycle | B Dict D2 |
| chcthd | ch | Test: observe material moving | Comp-v2 |

→ 8/9 recognized (88%).

**L40 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| y | --- | Done -- bare completion marker | B Dict D2 |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| cheolchal | ch | Test: bring to stable state | Comp-v2 |
| shchy | sh | Watch: adjust, watch | Comp-v2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| cheolor | ch | Test: hold current state | Comp-v2 |
| okain | ok | Vessel: seal for a processing cycle | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |

→ 11/11 recognized (100%).

**L41 (4 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ykeedain | yk | Adjust: one processing cycle | Comp-v2 |
| checkhey | ch | Test: temperature check (gentle level) | Comp-v2 |
| oain | --- | *unrecognized* (set up, bring to, iterate, bind) | --- |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |

→ 3/4 recognized (75%).


### P14 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 24 (5% of folio) |
| e-depth | 0.583 |
| dar count | 2 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ckhx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 9 (37%)
- ok: 2 (8%)
- ot: 2 (8%)
- qo: 2 (8%)
- da: 2 (8%)
- te: 1 (4%)
- lch: 1 (4%)

---

## Paragraph 15: Lines 42-47 (62 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L42 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| poly | po | Pause: hold | Comp-v2 |
| keedain | ke | Balneum: one processing cycle | Comp-v2 |
| she | sh | Watch: steady | Comp-v2 |
| kchdy | kch | Heat-check: cycle close | Comp-v2 |
| chotshe | ch | Test: transfer and hold | Comp-v2 |
| otechy | ot | Output: steady, adjust, watch | Comp-v2 |
| qokchdy | qo | Fire: heat with active test adjustment, cycle close | B Dict D2 |
| otaray | ot | Output: bring to and note result | Comp-v2 |
| shain | sh | Watch: one processing cycle | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |

→ 10/10 recognized (100%).

**L43 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ooeeor | --- | *unrecognized* (set up, set up, steady, steady, set up, respond) | --- |
| oeeal | --- | *unrecognized* (set up, steady, steady, bring to, hold) | --- |
| olkeol | ol | Steady: heat and hold | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| chl | ch | Test: hold | Comp-v2 |
| alchedy | al | Product settled: adjust, watch, steady, do | Comp-v2 |
| ykeedy | yk | Adjust: system steady, confirmed | Comp-v2 |
| chtal | ch | Test: bring to stable state | Comp-v2 |
| kar | ka | Apply heat and note the response | B Dict D3 |
| opchy | --- | *unrecognized* (set up, pause, adjust, watch, ) | --- |
| famom | --- | *unrecognized* (flag, bring to, finalize, set up, finalize) | --- |

→ 8/12 recognized (66%).

**L44 (20 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokchal | qo | Fire: heat until stable | Comp-v2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| qaiin | --- | *unrecognized* (q, bring to, iterate, iterate, bind) | --- |
| otol | ot | Output: hold current state | Comp-v2 |
| teol | te | Transfer step: hold current state | Comp-v2 |
| okal | ok | Vessel: contents settling -- let them stabilize | B Dict D2 |
| otedar | ot | Output: bring to and note result | Comp-v2 |
| opalchdy | --- | *unrecognized* (set up, pause, bring to, hold, adjust, watch, do, ) | --- |
| alpchdy | al | Product settled: pause, adjust, watch, do | Comp-v2 |
| ycheey | ch | Test: steady, steady | Comp-v2 |
| chokeey | ch | Test: gentle steady heat — balneum level | Comp-v2 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| tchedy | tch | Transfer-check: system steady, confirmed | Comp-v2 |
| oteol | ot | Output: hold current state | Comp-v2 |
| chcthy | ch | Test: observe material moving through apparatus **«cth»** | B Dict D2 |
| alaiin | al | Product settled: extended iteration cycles | Comp-v2 |
| char | ch | Test: bring to and note result | Comp-v2 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| kamdam | ka | Heat: finalize, do, bring to, finalize | Comp-v2 |

→ 18/20 recognized (90%).

**L45 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ykeey | yk | Adjust: steady, steady | Comp-v2 |
| lor | --- | Hold and note the result | B Dict D3 |
| chaiin | ch | Test: extended iteration cycles | Comp-v2 |
| cheky | ch | Test: verify the heat level | B Dict D2 |
| chokain | ch | Test: heat through one cycle | Comp-v2 |
| charam | ch | Test: bring to and note result | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |
| kain | ka | Apply heat through one processing cycle | B Dict D2 |
| chdal | ch | Test: bring to stable state | Comp-v2 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| daldy | da | Load: hold, do | Comp-v2 |

→ 11/11 recognized (100%).

**L47 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| eotar | --- | *unrecognized* (steady, set up, transfer, bring to, respond) | --- |
| aim | --- | *bare token: bring to, iterate, finalize* | --- |
| oar | --- | *bare token: set up, bring to, respond* | --- |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| alor | al | Product settled: note what happened | Comp-v2 |
| aiiin | --- | *unrecognized* (bring to, iterate, iterate, iterate, bind) | --- |
| olkaiin | ol | Steady: sustained deep heating cycles | Comp-v2 |
| oty | ot | Output: transfer complete -- drip/flow has ceased | B Dict D2 |
| ary | ar | Note the yield: complete | Comp-v2 |

→ 5/9 recognized (55%).



### P15 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 62 (14% of folio) |
| e-depth | 0.419 |
| dar count | 1 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | cthx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 14 (22%)
- ot: 6 (9%)
- qo: 4 (6%)
- al: 4 (6%)
- ka: 3 (4%)
- ok: 3 (4%)
- sh: 2 (3%)

---

## Cross-Paragraph Patterns

### e-depth Thermal Arc

| Para | Lines | Tokens | e-depth | Recipe phase |
|------|-------|--------|---------|-------------|
| P1 | 1-6 | 52 | 0.808 | Phlegm separation (balneum) |
| P2 | 7-10 | 28 | 0.643 | Animated water appears |
| P3 | 11-14 | 35 | 0.743 | Continued balneum distillation |
| P4 | 15-19 | 45 | 0.911 | Distill animated water aside |
| P5 | 20-24 | 42 | 0.929 | Division / animated water on dregs |
| P6 | 25-26 | 17 | **1.412** | **Balneum mariae** — peak e-depth |
| P7 | 27-29 | 28 | 1.143 | Continued balneum |
| P8 | 30 | 10 | 0.900 | Setup for ash fire |
| P9 | 31 | 5 | 0.600 | **Let material cool** — zero qo tokens |
| P10 | 32-34 | 28 | 1.107 | Return liquor to dregs |
| P11 | 35 | 6 | 0.667 | Brief transition |
| P12 | 36 | 10 | 0.900 | Continued processing |
| P13 | 37-38 | 23 | **0.304** | **Autonomous distillation** — lowest e-depth |
| P14 | 39-41 | 24 | 0.583 | Gentle fire for desiccation |
| P15 | 42-47 | 62 | 0.419 | Final desiccation — elements bind |

Three thermal regimes:
1. **Balneum peak** (P4-P7, e-depth 0.90-1.41): the recipe's "en bany marie" phase. P6 at 1.41 is the highest e-depth on any matched folio — maximum cooling stabilization for the water bath.
2. **Cooling valley** (P9, e-depth 0.60): "lexa refradar la materia" — zero qo tokens, the operator lets the material cool naturally. Only 5 tokens — a brief physical pause.
3. **Dry-fire decline** (P13-P15, e-depth 0.30-0.58): "en tro que les feces esteguen totes seques" — gentle sustained fire for desiccation. The lowest e-depth (0.30 at P13) reflects autonomous distillation where the fire runs with minimal cooling intervention.

### dar Distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 1 | 10% | Initial material loading |
| P2-P3 | 1 | 10% | Distillation outputs |
| P4-P5 | 2 | 20% | Separation and division |
| P6-P8 | 2 | 20% | Balneum setup |
| P9 | 0 | 0% | Cooling (no material action) |
| P10-P12 | 2 | 20% | Return liquor to dregs (cohobation) |
| P13-P15 | 2 | 20% | Final processing |

dar is distributed broadly (10 across 8 paragraphs) matching a recipe with material handling at every stage: loading lunaria, separating animated water, dividing into parts, returning liquor to dregs, and final processing.

### Material Marker

- **fch (mercury marker, C1939):** `fcheol` on L1 in P1. The recipe opens with "pendràs de la liquor mercuriall" (take mercurial liquor). The fch marker appears at the very first line, confirming the mercury-processing nature of the recipe.

---

## Verdict: COHERENT

f112v produces a coherent structural reading against III.1.0 (lunaria → quicksilver creation). The folio's 15 paragraphs trace the recipe's multi-step pipeline through three distinct thermal regimes:

1. **Phlegm separation** (P1-P3) — balneum distillation, fch mercury marker in P1
2. **Animated water** (P4-P5) — separation and division, rising e-depth
3. **Balneum mariae** (P6-P8) — peak e-depth (1.41), the recipe's explicit water-bath instruction
4. **Cooling** (P9) — 5 tokens, zero qo, "let the material cool"
5. **Cohobation return** (P10-P12) — return liquor to dregs, moderate heat
6. **Desiccation** (P13-P15) — lowest e-depth (0.30), gentle sustained fire until dregs are dry

The three-regime thermal profile (balneum peak → cooling valley → desiccation decline) is specific to this recipe's structure. The zero-qo cooling paragraph (P9) and the balneum peak at P6 (1.41) are both physically motivated and positionally correct.

**Expert review note:** `fcheol` on L1 contains the fch mercury marker (C1939), consistent with a recipe that opens by introducing mercurial liquor. The Phase 641 atom-decode rated this folio WEAK, but the expert structural assessment finds COHERENT — different evidence types can produce different verdicts.
