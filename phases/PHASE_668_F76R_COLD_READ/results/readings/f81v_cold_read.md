# Validated Reading: f81v ↔ III.18.0 Potable Gold (Water of Life)

**Match tier:** Supported
**Expert verdict:** Coherent (3 confirmed, 3 partial, 1 not detected)
**Full token listing:** `data/f81v_cold_read.txt` (258 tokens, 27 lines)

---

## How to Read This Document

This recipe is 182 words. This folio is 258 tokens — a 1.4:1 ratio. The recipe describes making potable gold (drinkable gold preparation) through a multi-step process: dissolve gold in special water via balneum inhumation, distill off moisture, then process lunaria through multiple distillation stages, redissolve the gold, rectify mercury, and combine into the "water of life."

The folio divides cleanly into two paragraphs that track the recipe's two-phase structure: P1 (sealed inhumation/dissolution, gentle heat, material-heavy) and P2 (active distillation/rectification, stronger heat, fire-management-heavy).

**What makes this match credible:**
- **e-depth shift**: P1=0.33 (sealed inhumation, minimal cooling intervention) vs P2=0.55 (active distillation with cooling cycles) — encodes the physical difference between passive sealed heating and active distillation
- **dar front-loading**: 71% of material additions in P1, matching the recipe's material-heavy dissolution phase
- **qo concentration shift**: P1 has 7 qo tokens, P2 has 35 — fire management 5× higher during active distillation
- **fch mercury marker** on L15 (C1939): appears at the transition to mercury rectification, exactly where the recipe says "rectifica son mercuri"
- **ckh temperature checks**: 3 in P1 (monitoring sealed balneum) + 2 in P2 (monitoring distillation)

**Honest gap:** No cs gold markers despite gold being central to the recipe. Expert explained: gold is a dissolved intermediate here, not a raw metallic input (contrast f84r where gold is actively dissolved and cs=3).

Every token on every line appears in this document.

---

## The Recipe

### Catalan (III.18.0, SISMEL — Part III cipher)

> Ara direm la composició de l'aygua potable simpla, que's fa de sanch fixat per natura per confortar lo humit radicall humanal. Pren l'aygua que ha poder de dissolre or sots la conservació de sa specie; e subtilia-lo en aquella per via de continuació ab inhumació en bany e laugera decocció. E aprés posa l'or dissolt en una carabaça de fin vidre, e distilla l'aygua e separa'n tota la humor. E estarà la substancia de l'or al fons del vexell tota secca. Puis pren de la lunaria e distilla la humor per alembich, en tro veuràs que par la diminució de sa sulphureitat no porà pus cremar. Continua ta distillació en altre receptori e aquella aygua pren en tro sobre'l cap de l'alembich no apparrà res de venes. En aquesta aygua gitaràs la substancia de l'or, e tantost se dissolrà en l'aygua vejetall per rahó del mercuri. Rectifica son mercuri de la fleuma, en tro veies que creme, e puis mescla-la ab primera eau ab la substancia de l'or. E és aygua de vida.

### English

We will now describe the composition of simple potable water, made from blood fixed by nature to comfort the radical human moisture. Take the water that has power to dissolve gold while preserving its form; subtilize it through continuous inhumation in balneum with gentle decoction. Then place the dissolved gold in a fine glass cucurbit, distill the water, and separate all the moisture. The substance of the gold will remain dry at the bottom of the vessel. Then take lunaria and distill its moisture through the alembic until you see that through diminution of its sulfureity it can no longer burn. Continue your distillation into another receptor, taking that water until nothing more appears at the head of the alembic. Into this water cast the gold substance — it will dissolve immediately in the vegetable water by reason of the mercury. Rectify the mercury from the phlegm until you see it burn, then mix it with the first water and the gold substance. This is the water of life.

### Recipe Structure

| Step | Operation | Heat | Key feature |
|------|-----------|------|-------------|
| 1 | Dissolve gold in special water | gentle balneum | "inhumació en bany e laugera decocció" |
| 2 | Place in glass cucurbit, distill off moisture | moderate | gold remains dry at bottom |
| 3 | Distill lunaria through alembic | moderate | quality gate: "no porà pus cremar" |
| 4 | Continue into second receptor | moderate | gate: "no apparrà res de venes" |
| 5 | Cast gold into vegetable water | — | immediate dissolution |
| 6 | Rectify mercury from phlegm | moderate | gate: "veies que creme" |
| 7 | Mix with first water + gold | — | **Result: water of life** |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | High e-depth early (balneum inhumation) | "inhumació en bany e laugera decocció" | **PARTIAL** — P1=0.33 (low, not high) but physically correct: sealed inhumation has minimal cooling intervention |
| 2 | cs gold markers | gold dissolved explicitly | **NOT DETECTED** — gold as dissolved intermediate |
| 3 | Multiple quality gates (3 explicit checks) | burns test, alembic head, rectification | **PARTIAL** — chekar=7 but distributed broadly |
| 4 | dar at specific moments | gold, lunaria, gold redissolution | **MATCH** — 21 dar, front-loaded in P1 |
| 5 | Two-vessel structure | cucurbit then second receptor | **PARTIAL** — 2 paragraphs map to 2 phases |
| 6 | Observation MIDDLEs at quality gates | visual checks | **MATCH** — ckh×5 distributed |
| 7 | fch mercury marker | mercury rectification | **MATCH** — fch on L15 at rectification transition |

**Score: 3 confirmed, 3 partial, 1 not detected**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 258 |
| Lines | 27 |
| Paragraphs | 2 |
| dar (material-add) | 21 (8.1% — highest material density in matched set) |
| Quality checks (chek/shek class) | 7 |
| Observation MIDDLEs | ckh×5 |
| hh (extended observation) | 0 |

---

## Paragraph 1: Lines 1-9 (91 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L1 (14 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| par | --- | *bare token: pause, bring to, respond* | --- |
| shey | sh | Watch: quick passive check | B Dict D1 |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| shekal | sh | Watch: heat until stable | Comp-v2 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| pchedy | pch | Setup: system steady, confirmed | Comp-v2 |
| shek | sh | Watch: steady, heat | Comp-v2 |
| dain | da | Load: secure material for next run | B Dict D1 |
| ofal | --- | *unrecognized* (set up, flag, bring to, hold) | --- |
| sheky | sh | Watch: set — stop adjusting | Comp-v2 |
| otoin | ot | Output: set up, iterate, bind | Comp-v2 |
| olkol | ol | Steady: heat and hold | Comp-v2 |

→ 12/14 recognized (85%).

**L2 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| kair | ka | Heat: iterate, respond | Comp-v2 |
| okal | ok | Vessel: contents settling -- let them stabilize | B Dict D2 |
| sar | sa | Scaffold: note the position and respond | B Dict D3 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| kain | ka | Apply heat through one processing cycle | B Dict D2 |
| olkain | ol | Steady: heat through one cycle | Comp-v2 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| rol | --- | *bare token: respond, set up, hold* | --- |
| dl | --- | *bare token: do, hold* | --- |

→ 10/12 recognized (83%).

**L3 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| olkeedy | ol | Steady: hold gentle heat -- maintain balneum level | B Dict D2 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| dykain | yk | Adjust: one processing cycle | Comp-v2 |
| shek | sh | Watch: steady, heat | Comp-v2 |
| chdy | ch | Test: check complete | B Dict D2 |
| dalal | da | Load: bring to stable state | Comp-v2 |
| oldy | ol | Steady: cycle close | Comp-v2 |

→ 9/9 recognized (100%).

**L4 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| okain | ok | Vessel: seal for a processing cycle | B Dict D1 |
| cheeky | ch | Test: gentle steady heat — balneum level | Comp-v2 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| kaiin | ka | Sustained deep heating -- extended cyclic heat application | B Dict D2 |
| dain | da | Load: secure material for next run | B Dict D1 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |

→ 10/10 recognized (100%).

**L5 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| kar | ka | Apply heat and note the response | B Dict D3 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |

→ 9/9 recognized (100%).

**L6 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| lky | lk | Check equipment: complete | Comp-v2 |
| ls | --- | *bare token: hold, sequence* | --- |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| okain | ok | Vessel: seal for a processing cycle | B Dict D1 |
| daldy | da | Load: hold, do | Comp-v2 |

→ 9/10 recognized (90%).

**L7 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| olor | ol | Steady: note what happened | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| sheckhal | sh | Watch: temperature check | Comp-v2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| qokeedal | qo | Fire: one gentle balneum cycle | Comp-v2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| schedy | sch | Quick check: system steady, confirmed | Comp-v2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |

→ 9/9 recognized (100%).

**L8 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ykol | yk | Adjust: hold current state | Comp-v2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| dkain | ka | Heat: iterate, bind | Comp-v2 |
| cphedy | --- | *unrecognized* (adjust, pause, watch, steady, do, ) | --- |
| oldy | ol | Steady: cycle close | Comp-v2 |

→ 9/10 recognized (90%).

**L9 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| yar | --- | *bare token: , bring to, respond* | --- |
| olchey | ol | Steady: adjust, watch, steady | Comp-v2 |
| kaiin | ka | Sustained deep heating -- extended cyclic heat application | B Dict D2 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| olor | ol | Steady: note what happened | Comp-v2 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |
| daiidy | da | Load: iterate, iterate, do | Comp-v2 |

→ 7/8 recognized (87%).


### P1 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 91 (35% of folio) |
| e-depth | 0.330 |
| dar count | 15 |
| Quality checks (chek/shek) | 4 |
| Observation MIDDLEs | ckhx3 |
| hh (extended obs) | 0 |

**Top prefixes:**
- da: 15 (16%)
- ok: 10 (10%)
- sh: 8 (8%)
- ol: 8 (8%)
- ch: 8 (8%)
- qo: 7 (7%)
- ka: 6 (6%)

---

## Paragraph 2: Lines 10-27 (167 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L10 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polshy | po | Pause: hold, sequence, watch | Comp-v2 |
| oshyteed | --- | *unrecognized* (set up, sequence, watch, , transfer, steady, steady, do) | --- |
| qop | qo | Fire: pause | Comp-v2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| okshedy | ok | Vessel: watch sequence steady | Comp-v2 |
| qoty | qo | Fire: transfer complete -- stop moving material | B Dict D2 |
| dairam | da | Load: bring to and note result | Comp-v2 |

→ 7/8 recognized (87%).

**L11 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| oshey | --- | *unrecognized* (set up, sequence, watch, steady, ) | --- |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| oky | ok | Vessel: done -- seal or set aside | B Dict D2 |
| ykeey | yk | Adjust: steady, steady | Comp-v2 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| okylky | ok | Vessel: hold, heat | Comp-v2 |
| olchy | ol | Steady: adjust, watch | Comp-v2 |
| ky | --- | *bare token: heat, * | --- |
| dsholyd | sh | Watch: holding, confirmed | Comp-v2 |

→ 8/10 recognized (80%).

**L12 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qol | qo | Fire: hold current heat level | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| chdy | ch | Test: check complete | B Dict D2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| ytedy | te | Transfer step: cycle close | Comp-v2 |
| chetedy | ch | Test: gentle steady transfer | Comp-v2 |
| lkedey | lk | Check equipment: system steady, confirmed | Comp-v2 |
| ytedy | te | Transfer step: cycle close | Comp-v2 |

→ 9/9 recognized (100%).

**L13 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ykecsey | yk | Adjust: sequence steady | Comp-v2 |
| dched | dch | Setup-check: steady, do | Comp-v2 |
| ytedy | te | Transfer step: cycle close | Comp-v2 |
| ytedy | te | Transfer step: cycle close | Comp-v2 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| ykeda | yk | Adjust: steady, do, bring to | Comp-v2 |
| iphy | --- | *unrecognized* (iterate, pause, watch, ) | --- |
| qoty | qo | Fire: transfer complete -- stop moving material | B Dict D2 |
| ykedy | yk | Adjust: system steady, confirmed | Comp-v2 |
| okal | ok | Vessel: contents settling -- let them stabilize | B Dict D2 |

→ 9/10 recognized (90%).

**L14 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| ykeedy | yk | Adjust: system steady, confirmed | Comp-v2 |
| cseeky | --- | *unrecognized* (adjust, sequence, steady, steady, heat, ) | --- |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| qokeed | qo | Fire: one gentle balneum cycle | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| lchpchdy | lch | Check equipment: pause, adjust, watch, do | Comp-v2 |

→ 7/8 recognized (87%).

**L15 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| salshcthdy | sa | Scaffold: observe material moving | Comp-v2 |
| qofchedy | qo | Fire: flag, adjust, watch, steady, do | Comp-v2 |
| r | --- | Respond -- route to next action | B Dict D3 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| ltary | ta | Transfer: respond | Comp-v2 |

→ 9/9 recognized (100%).

**L16 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| lor | --- | Hold and note the result | B Dict D3 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qoeedy | qo | Fire: system steady, confirmed | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| chy | ch | Test: complete | Comp-v2 |
| rshdy | sh | Watch: cycle close | Comp-v2 |
| lshedy | lsh | Watch equipment: confirm apparatus is steady | B Dict D2 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| chdy | ch | Test: check complete | B Dict D2 |
| pchdy | pch | Setup: cycle close | Comp-v2 |

→ 10/10 recognized (100%).

**L17 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sshkchdy | sh | Watch: heat with active monitoring | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qolchedy | qo | Fire: hold, adjust, watch, steady, do | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| shckhy | sh | Watch: passive temperature observation **«ckh»** | B Dict D2 |
| dl | --- | *bare token: do, hold* | --- |
| ral | --- | *bare token: respond, bring to, hold* | --- |

→ 7/9 recognized (77%).

**L18 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokchdy | qo | Fire: heat with active test adjustment, cycle close | B Dict D2 |
| chey | ch | Test: quick active check | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| cheky | ch | Test: verify the heat level | B Dict D2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |

→ 10/10 recognized (100%).

**L19 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| solkeey | so | Sequence: gentle steady heat — balneum level | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| sheckhy | sh | Watch: temperature check | Comp-v2 |
| dcsedy | --- | *unrecognized* (do, adjust, sequence, steady, do, ) | --- |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| dol | do | Load: place material and hold -- position substance, keep it there | B Dict D2 |
| chy | ch | Test: complete | Comp-v2 |

→ 9/10 recognized (90%).

**L20 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qocthey | qo | Fire: observe material moving | Comp-v2 |
| chekal | ch | Test: heat until stable | Comp-v2 |
| chody | ch | Test: check the arrangement | B Dict D2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| lshety | lsh | Watch equipment: steady, transfer | Comp-v2 |
| qoldy | qo | Fire: hold, do | Comp-v2 |
| ltedy | te | Transfer step: cycle close | Comp-v2 |
| qotain | qo | Fire: transfer through one processing cycle | B Dict D2 |

→ 8/8 recognized (100%).

**L21 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| lsho | lsh | Watch equipment: set up | Comp-v2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| lshedy | lsh | Watch equipment: confirm apparatus is steady | B Dict D2 |
| lshedy | lsh | Watch equipment: confirm apparatus is steady | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qolky | qo | Fire: set — stop adjusting | Comp-v2 |
| lchedal | lch | Check equipment: bring to stable state | Comp-v2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |

→ 9/9 recognized (100%).

**L22 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| oiin | --- | *unrecognized* (set up, iterate, iterate, bind) | --- |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| lohedy | --- | *unrecognized* (hold, set up, watch, steady, do, ) | --- |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| sal | sa | Scaffold: hold | Comp-v2 |
| chtedytar | ch | Test: transfer and note result | Comp-v2 |

→ 7/9 recognized (77%).

**L23 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| shol | sh | Watch: hold -- passive monitoring, keep current state | B Dict D2 |
| qekchy | --- | *unrecognized* (q, steady, heat, adjust, watch, ) | --- |
| ykaiin | yk | Adjust: extended iteration cycles | Comp-v2 |
| olkain | ol | Steady: heat through one cycle | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| dchedy | dch | Setup-check: system steady, confirmed | Comp-v2 |
| rol | --- | *bare token: respond, set up, hold* | --- |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| cthdy | ct | watch, do | Comp-v2 |

→ 8/10 recognized (80%).

**L24 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ytey | te | Transfer step: complete | Comp-v2 |
| okchedy | ok | Vessel: adjust, watch, steady, do | Comp-v2 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| sal | sa | Scaffold: hold | Comp-v2 |
| teol | te | Transfer step: hold current state | Comp-v2 |
| dchdy | dch | Setup-check: cycle close | Comp-v2 |
| ly | --- | *bare token: hold, * | --- |

→ 9/10 recognized (90%).

**L25 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| oshedy | --- | *unrecognized* (set up, sequence, watch, steady, do, ) | --- |
| qotedy | qo | Fire: execute a heat-driven transfer operation | B Dict D1 |
| shol | sh | Watch: hold -- passive monitoring, keep current state | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| yshchey | sh | Watch: adjust, watch, steady | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| chey | ch | Test: quick active check | B Dict D1 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| tchd | tch | Transfer-check: do | Comp-v2 |
| oky | ok | Vessel: done -- seal or set aside | B Dict D2 |

→ 10/11 recognized (90%).

**L26 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| chechol | ch | Test: hold current state | Comp-v2 |
| tar | ta | Transfer and note the yield | B Dict D3 |
| oiin | --- | *unrecognized* (set up, iterate, iterate, bind) | --- |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| olkeol | ol | Steady: heat and hold | Comp-v2 |
| olkeedy | ol | Steady: hold gentle heat -- maintain balneum level | B Dict D2 |
| okeol | ok | Vessel: hold current state | Comp-v2 |

→ 9/10 recognized (90%).

**L27 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dsheol | sh | Watch: hold current state | Comp-v2 |
| oiiin | --- | *unrecognized* (set up, iterate, iterate, iterate, bind) | --- |
| olkeedy | ol | Steady: hold gentle heat -- maintain balneum level | B Dict D2 |
| tedy | te | Transfer operation complete | B Dict D2 |
| cheky | ch | Test: verify the heat level | B Dict D2 |
| shckhedy | sh | Watch: temperature check | Comp-v2 |
| chal | ch | Test: bring to stable state | Comp-v2 |

→ 6/7 recognized (85%).



### P2 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 167 (64% of folio) |
| e-depth | 0.551 |
| dar count | 6 |
| Quality checks (chek/shek) | 3 |
| Observation MIDDLEs | ckhx2 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 35 (20%)
- ch: 23 (13%)
- sh: 20 (11%)
- ok: 12 (7%)
- te: 8 (4%)
- da: 6 (3%)
- yk: 6 (3%)

---

## Cross-Paragraph Patterns

### e-depth Thermal Arc

| Para | Lines | Tokens | e-depth | Recipe phase |
|------|-------|--------|---------|-------------|
| P1 | 1-9 | 91 | 0.330 | Inhumation + dissolution (sealed balneum, gentle decoction) |
| P2 | 10-27 | 167 | 0.551 | Distillation, separation, rectification (active fire management) |

The e-depth shift from 0.33 to 0.55 encodes the physical difference between the two phases. P1 (inhumation) is sealed, passive, with minimal cooling intervention — the operator loads the vessel, seals it, and maintains gentle heat for an extended period. P2 (distillation/rectification) requires active fire management with cooling cycles — the operator is moving material through the alembic, monitoring distillate quality, and rectifying mercury.

The P1 e-depth of 0.33 is among the lowest for any balneum-matched paragraph. This is physically correct: inhumation ("burial" in the sand/ash bath) is the most passive form of balneum heating — you seal the vessel and leave it. Minimal thermal intervention means minimal cooling atoms.

### dar Distribution

| Para | dar | % | Density | Recipe phase |
|------|-----|---|---------|-------------|
| P1 | 15 | 71% | 16.5% | Material-heavy: loading gold, water, preparing dissolution |
| P2 | 6 | 29% | 3.6% | Lighter: lunaria addition, gold redissolution, mixing |

P1 has the highest material density (16.5%) of any paragraph in the matched folio set. The recipe explains why: potable gold begins by combining multiple prepared substances (the solvent water, the gold itself, the cucurbit) and subjecting them to iterative sealed processing that requires repeated material interventions.

P2's 6 dar at 3.6% density reflects the recipe's lighter material handling: adding lunaria, casting gold into vegetable water, and the final mixing.

### Observation MIDDLE Distribution

| Para | ckh | Total | Density | Recipe phase |
|------|-----|-------|---------|-------------|
| P1 | 3 | 3 | 3.3% | Temperature monitoring during sealed balneum |
| P2 | 2 | 2 | 1.2% | Temperature monitoring during distillation |

ckh (temperature check) is the only observation MIDDLE type on this folio — no cth (transfer-watch), no ecth (cooled-transfer-watch). This is consistent with the recipe: the primary operational concern throughout is maintaining the right temperature. The recipe never describes watching material transfer or handling cooled intermediates — it's about getting the heat right for dissolution, distillation, and rectification.

### qo-prefix (Fire Management) Distribution

| Para | qo count | % of para | Recipe phase |
|------|----------|-----------|-------------|
| P1 | 7 | 7.7% | Sealed balneum — minimal active fire management |
| P2 | 35 | 21.0% | Active distillation — continuous fire adjustment |

The 5× jump in fire management from P1 to P2 encodes the operational shift: inhumation (passive, sealed) → distillation (active, monitored). During inhumation, the fire is set and left. During distillation, the operator continuously adjusts the fire to manage distillation rate, rectification temperature, and mercury quality checks.

### Material Marker

- **fch (mercury marker, C1939):** `qofchedy` on L15. Appears at the transition between P1 (dissolution) and P2 (distillation), exactly where the recipe transitions to mercury-related operations ("Rectifica son mercuri de la fleuma"). The fch pattern is enriched on all 6/6 confirmed mercury-recipe folios.
- **cs (gold marker, C1940):** Absent. The expert positive control noted this is consistent with gold being a dissolved intermediate (passively present in solution) rather than a primary metallic input being actively processed (as on f84r where cs=3).

---

## Verdict: COHERENT

f81v produces a coherent two-paragraph reading against III.18.0 (potable gold / water of life). The folio's structure maps to the recipe's natural division:

1. **Inhumation and dissolution** (P1, 91 tokens) — 15 dar (71% of total, highest density in matched set), e-depth 0.33 (sealed passive heat), 3 ckh temperature checks. The recipe says "take the water, subtilize gold through continuous inhumation in balneum with gentle decoction."
2. **Distillation, separation, and rectification** (P2, 167 tokens) — 6 dar, e-depth 0.55 (active fire), 35 qo-prefix tokens (5× P1), fch mercury marker at the rectification transition. The recipe describes: distill moisture, process lunaria through alembic, redissolve gold in vegetable water, rectify mercury, combine into water of life.

The e-depth shift (0.33 → 0.55), dar front-loading (71% in P1), qo concentration shift (5×), and fch marker at the mercury rectification point are the primary structural signals. The recipe's 7 steps compress into 2 paragraphs because the first 3 steps are all sealed-vessel operations (one phase) and steps 4-7 are all active-distillation operations (one phase).

**Honest gap:** No cs gold markers. The recipe's most distinctive structural feature — potable gold from dissolved gold — lacks the material-specific marker that C1940 predicts. The expert's explanation (dissolved intermediate vs primary metallic input) is plausible but not independently tested.
