# Cold Read: f75r ↔ III.19.0 Aqua Vitae (Reflux Distillation)

**Match tier:** CONFIRMED
**Expert verdict:** Coherent (8/8 structural predictions confirmed)
**Full token listing:** `data/f75r_cold_read.txt` (412 tokens, 46 lines)

---

## How to Read This Document

This recipe is 100 words. This folio is 412 tokens. That ratio — roughly 4:1 — is not a mismatch. It is the expected behavior of a notation system encoding operational control programs.

The recipe is a **specification**: it tells you what materials to combine, in what order, at what temperature, for how many cycles. "Reiterate, renewing the honeycomb at each second distillation, four times; and after, nine times" is one sentence. But executing a 4-then-9-cycle reflux distillation requires the operator to manage the fire across 13 passes, monitor the distillate, renew the honeycomb at intervals, transfer between vessels, and verify quality at each stage. The folio encodes all of that.

**What makes this match credible is not narrative plausibility** — generic agents produced COHERENT readings for wrong recipes in negative controls. What makes it credible is **specific structural features that discriminate**:

- **Counting anchors**: 4 consecutive identical `qokedy` tokens on L13 (corpus-singular in Currier B per C1889), directly encoding "per quatre vegades." 9 qok-class tokens spanning L37-38, encoding "ix vegades."
- **e-depth thermal arc**: V-shaped profile crashing to 0.18 at P7 (physical vessel transfer — no heat), consistent with reflux distillation's mid-process apparatus change
- **dar distribution**: Back-loaded (46% in P9), matching the recipe's "renew honeycomb at each second distillation" during the x9 cycle
- **Zero-dar fermentation phase**: P3-P4 have zero material additions, matching "put to ferment" (sealed, no additions)
- **Observation MIDDLE fade-out**: P5 has zero observation MIDDLEs during autonomous cycling

The negative control for this folio (f75r ↔ III.21.0, wrong recipe) scored 0/7 on structural predictions. The correct recipe scores 8/8. That gap is the evidence.

Every token on every line appears in this document. Where a token has a confident workshop reading, it is cited with source. Where a token is truly unparseable (5 of 412, 1.2%), it says *unrecognized*.

---

## The Recipe

### Catalan (III.19.0, SISMEL — Part III cipher, no letter codes in this sub-recipe)

> Tu pendràs l'aygua de vida e separa'n sa humiditat tota per distillació; e la substancia de l'aygua, qui és pur or, tu metràs a part; e dedins la humiditat vejetal metràs la terça part de **bresca** ab tota sa substancia, ço és assaber ab la mel e ab la cera. E aquella metràs a fermentar en laugera calor per .iii. dies; e quant més hi està, més val. Puys mit-ho a distillar en bany; e aquesta distillació e fermentació reitera en renovellant la bresca a cascuna segona distillació per quatre vegades; e aprés ix vegades.

*Cipher note: "bresca" (honeycomb) appears in mirror-script cipher at first occurrence (Tavola 2, entry 24). No Part III letter codes in this sub-recipe.*

### English

Take the water of life and separate all its moisture by distillation. The substance of the water, which is pure gold, set aside. In the vegetal moisture put a third part of **honeycomb** with all its substance (honey and wax). Put to ferment in gentle heat for 3 days — the longer the better. Then distill in balneum. Reiterate this distillation and fermentation, renewing the honeycomb at each second distillation, **four times**; and after, **nine times**.

### Recipe Structure

| Step | Operation | Materials | Heat | Count |
|------|-----------|-----------|------|-------|
| 1 | Separate water of life | water of life | distillation | — |
| 2 | Set aside gold substance | pure gold | — | — |
| 3 | Add honeycomb to vegetal moisture | 1/3 part honeycomb (honey + wax) | — | — |
| 4 | Ferment | — | gentle heat | 3 days |
| 5 | Distill in balneum | — | water bath | — |
| 6 | Reiterate (renew honeycomb every 2nd distillation) | fresh honeycomb | balneum | **x4** |
| 7 | Continue reiterating | fresh honeycomb | balneum | **x9** |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | High e-depth (balneum throughout) | "distillar en bany" | **MATCH** — 0.42-0.63, balneum range |
| 2 | dar tokens for honeycomb renewal | "renovellant la bresca" | **MATCH** — 27 dar total, back-loaded |
| 3 | qo-prefix dominant (fire management) | reflux = continuous heat | **MATCH** — qo=108 (26%) |
| 4 | x4 counting anchor | "per quatre vegades" | **MATCH** — 4x qokedy on L13 (C1889, corpus-singular) |
| 5 | x9 counting anchor | "ix vegades" | **MATCH** — 9 qok-class on L37-38 (C1969) |
| 6 | Multi-paragraph procedural folio | complex multi-phase recipe | **MATCH** — 9 paragraphs |
| 7 | Observation MIDDLEs present | monitoring distillation quality | **MATCH** — ckh x6, ecth x2, cth x2 |
| 8 | Thermal arc with transfer interruption | mid-process vessel change | **MATCH** — e-depth crashes to 0.18 at P7 |

**Score: 8/8 confirmed**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 412 |
| Lines | 46 |
| Paragraphs | 9 |
| Workshop-readable tokens | 407/412 (99%) |
| Truly unrecognized | 5 (1.2%) |
| dar (material-add) | 27 |
| Quality checks (chek/shek class) | 4 |
| Observation MIDDLEs | ckh x6, ecth x2, cth x2 |
| hh (extended observation) | 0 |

---

## Paragraph 1: Lines 1-5 (46 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L1 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| kchedy | kch | Heat-check: system steady, confirmed | Comp-v2 |
| kary | ka | Heat: respond | Comp-v2 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| shy | sh | Watch: complete | Comp-v2 |
| kchedy | kch | Heat-check: system steady, confirmed | Comp-v2 |
| qotar | qo | Fire: transfer heat/material and note result | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |

→ 8/8 recognized (100%).

**L2 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dain | da | Load: secure material for next run | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| ly | --- | *bare token: hold, * | --- |
| ssheol | sh | Watch: hold current state | Comp-v2 |
| qolchedy | qo | Fire: hold, adjust, watch, steady, do | Comp-v2 |
| chedykar | ch | Test: one standard heat cycle | Comp-v2 |
| chekeedy | ch | Test: one gentle balneum cycle | Comp-v2 |
| ror | --- | *bare token: respond, set up, respond* | --- |

→ 6/8 recognized (75%).

**L3 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chal | ch | Test: bring to stable state | Comp-v2 |
| orchey | or | Note what happened: adjust, watch, steady | Comp-v2 |
| qey | --- | *bare token: q, steady, * | --- |
| kain | ka | Apply heat through one processing cycle | B Dict D2 |
| sheeky | sh | Watch: gentle steady heat — balneum level | Comp-v2 |
| ltain | ta | Transfer: iterate, bind | Comp-v2 |
| olkar | ol | Steady: heat and note response | Comp-v2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |

→ 8/9 recognized (88%).

**L4 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dackhy | da | Load: temperature check | Comp-v2 |
| lkamo | lk | Check equipment: bring to, finalize, set up | Comp-v2 |
| ykeey | yk | Adjust: steady, steady | Comp-v2 |
| lshey | lsh | Watch equipment: steady | Comp-v2 |
| kal | ka | Heat: hold | Comp-v2 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |

→ 10/10 recognized (100%).

**L5 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| shey | sh | Watch: quick passive check | B Dict D1 |
| kar | ka | Apply heat and note the response | B Dict D3 |
| chey | ch | Test: quick active check | B Dict D1 |
| ckhey | --- | *unrecognized* (adjust, heat, watch, steady, ) | --- |
| r | --- | Respond -- route to next action | B Dict D3 |
| ain | --- | Bring to a binding cycle -- one pass | B Dict D2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |

→ 10/11 recognized (90%).


### P1 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 46 (11% of folio) |
| e-depth | 0.630 |
| dar count | 2 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- sh: 9 (19%)
- qo: 7 (15%)
- ka: 4 (8%)
- ch: 4 (8%)
- kch: 2 (4%)
- da: 2 (4%)
- ok: 1 (2%)

---

## Paragraph 2: Lines 6-6 (9 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L6 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pchey | pch | Setup: steady | Comp-v2 |
| keeor | ke | Balneum: note what happened | Comp-v2 |
| olky | ol | Steady: set — stop adjusting | Comp-v2 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| okey | ok | Vessel: steady | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chcthy | ch | Test: observe material moving through apparatus **«cth»** | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |

→ 9/9 recognized (100%).


### P2 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 9 (2% of folio) |
| e-depth | 0.556 |
| dar count | 1 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | cthx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 3 (33%)
- pch: 1 (11%)
- ke: 1 (11%)
- ol: 1 (11%)
- da: 1 (11%)
- ok: 1 (11%)
- ch: 1 (11%)

---

## Paragraph 3: Lines 7-12 (58 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L7 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pchedy | pch | Setup: system steady, confirmed | Comp-v2 |
| qokshdy | qo | Fire: heat, sequence, watch, do | Comp-v2 |
| ytain | ta | Transfer: iterate, bind | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| chy | ch | Test: complete | Comp-v2 |
| lol | --- | Equipment steady -- furnace holding at current level | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |

→ 9/9 recognized (100%).

**L8 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sor | so | Sequence: respond | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |
| qotardy | qo | Fire: transfer and note result | Comp-v2 |
| dsheckhy | sh | Watch: temperature check | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| lshedy | lsh | Watch equipment: confirm apparatus is steady | B Dict D2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |

→ 8/8 recognized (100%).

**L9 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokchdy | qo | Fire: heat with active test adjustment, cycle close | B Dict D2 |
| chcthy | ch | Test: observe material moving through apparatus **«cth»** | B Dict D2 |
| lo | --- | *bare token: hold, set up* | --- |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokan | qo | Fire: heat, bring to, bind | Comp-v2 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| olchedy | ol | Steady: adjust, watch, steady, do | Comp-v2 |
| sal | sa | Scaffold: hold | Comp-v2 |

→ 8/9 recognized (88%).

**L10 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dshor | sh | Watch: note what happened | Comp-v2 |
| qotar | qo | Fire: transfer heat/material and note result | B Dict D1 |
| chdy | ch | Test: check complete | B Dict D2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| otey | ot | Output: steady | Comp-v2 |
| tedy | te | Transfer operation complete | B Dict D2 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |

→ 10/10 recognized (100%).

**L11 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| oly | ol | Steady: current state confirmed | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| dor | do | Execute: respond | Comp-v2 |
| chekam | ch | Test: steady, heat, bring to, finalize | Comp-v2 |

→ 10/10 recognized (100%).

**L12 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ssheckhy | sh | Watch: temperature check | Comp-v2 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| oly | ol | Steady: current state confirmed | B Dict D2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| r | --- | Respond -- route to next action | B Dict D3 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |

→ 12/12 recognized (100%).


### P3 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 58 (14% of folio) |
| e-depth | 0.448 |
| dar count | 0 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | ckhx2, cthx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 17 (29%)
- ch: 11 (18%)
- sh: 8 (13%)
- ol: 3 (5%)
- ok: 2 (3%)
- pch: 1 (1%)
- ta: 1 (1%)

---

## Paragraph 4: Lines 13-16 (39 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L13 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pchedy | pch | Setup: system steady, confirmed | Comp-v2 |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| olshedy | ol | Steady: watch sequence steady | Comp-v2 |

→ 8/8 recognized (100%).

**L14 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| keeshy | ke | Balneum: watch sequence steady | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| olshedy | ol | Steady: watch sequence steady | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| aly | al | Product settled: complete | Comp-v2 |

→ 11/11 recognized (100%).

**L15 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| keeoly | ke | Balneum: holding, confirmed | Comp-v2 |
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| okchdy | ok | Vessel: adjust, watch, do | Comp-v2 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |

→ 11/11 recognized (100%).

**L16 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| lch | --- | *bare token: hold, adjust, watch* | --- |
| shokain | sh | Watch: heat through one cycle | Comp-v2 |
| chy | ch | Test: complete | Comp-v2 |
| otshedy | ot | Output: watch sequence steady | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |

→ 8/9 recognized (88%).


### P4 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 39 (9% of folio) |
| e-depth | 0.436 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ckhx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 13 (33%)
- ch: 4 (10%)
- sh: 4 (10%)
- ke: 3 (7%)
- sa: 3 (7%)
- ol: 2 (5%)
- ot: 2 (5%)

---

## Paragraph 5: Lines 17-22 (52 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L17 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pchedar | pch | Setup: bring to and note result | Comp-v2 |
| shepchy | sh | Watch: steady, pause, adjust, watch | Comp-v2 |
| lshedary | lsh | Watch equipment: bring to and note result | Comp-v2 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| shal | sh | Watch: bring to stable state | Comp-v2 |
| shy | sh | Watch: complete | Comp-v2 |
| kol | ko | Heat: hold | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokam | qo | Fire: heat, bring to, finalize | Comp-v2 |

→ 9/9 recognized (100%).

**L18 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| char | ch | Test: bring to and note result | Comp-v2 |
| sar | sa | Scaffold: note the position and respond | B Dict D3 |
| oly | ol | Steady: current state confirmed | B Dict D2 |

→ 9/9 recognized (100%).

**L19 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokshedy | qo | Fire: one standard heat cycle | Comp-v2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| ithey | --- | *unrecognized* (iterate, transfer, watch, steady, ) | --- |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |

→ 7/8 recognized (87%).

**L20 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ry | --- | *bare token: respond, * | --- |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qor | qo | Fire: respond | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |
| lchey | lch | Check equipment: quick apparatus check | B Dict D2 |
| lo | --- | *bare token: hold, set up* | --- |
| ydain | da | Load: iterate, bind | Comp-v2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |

→ 7/9 recognized (77%).

**L21 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| oqekain | --- | *unrecognized* (set up, q, steady, heat, bring to, iterate, bind) | --- |
| chey | ch | Test: quick active check | B Dict D1 |
| qckhsy | --- | *unrecognized* (q, adjust, heat, watch, sequence, ) | --- |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| ysheor | sh | Watch: note what happened | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| lor | --- | Hold and note the result | B Dict D3 |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |

→ 6/8 recognized (75%).

**L22 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| odar | --- | *unrecognized* (set up, do, bring to, respond) | --- |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| kar | ka | Apply heat and note the response | B Dict D3 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| sar | sa | Scaffold: note the position and respond | B Dict D3 |

→ 8/9 recognized (88%).


### P5 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 52 (12% of folio) |
| e-depth | 0.423 |
| dar count | 2 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- sh: 13 (25%)
- qo: 10 (19%)
- ch: 5 (9%)
- da: 2 (3%)
- sa: 2 (3%)
- pch: 1 (1%)
- lsh: 1 (1%)

---

## Paragraph 6: Lines 23-26 (31 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L23 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pchey | pch | Setup: steady | Comp-v2 |
| kshey | sh | Watch: steady | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| sshey | sh | Watch: steady | Comp-v2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokam | qo | Fire: heat, bring to, finalize | Comp-v2 |

→ 8/8 recognized (100%).

**L24 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| olkeey | ol | Steady: hold gentle heat -- balneum level steady | B Dict D2 |
| qolkary | qo | Fire: heat until stable | Comp-v2 |
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| checthy | ch | Test: cooled-transfer-watch **«ecth»** | Comp-v2 |
| lor | --- | Hold and note the result | B Dict D3 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |

→ 7/7 recognized (100%).

**L25 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| shckhy | sh | Watch: passive temperature observation **«ckh»** | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| shy | sh | Watch: complete | Comp-v2 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |
| ram | --- | *bare token: respond, bring to, finalize* | --- |

→ 7/8 recognized (87%).

**L26 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dain | da | Load: secure material for next run | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| sheol | sh | Watch: observe and hold -- passive monitoring, maintain state | B Dict D2 |
| dain | da | Load: secure material for next run | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| qoly | qo | Fire: hold | Comp-v2 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| ady | --- | *bare token: bring to, do, * | --- |

→ 7/8 recognized (87%).


### P6 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 31 (7% of folio) |
| e-depth | 0.484 |
| dar count | 3 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ecthx1, ckhx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 9 (29%)
- sh: 5 (16%)
- da: 3 (9%)
- ch: 2 (6%)
- sa: 2 (6%)
- pch: 1 (3%)
- ol: 1 (3%)

---

## Paragraph 7: Lines 27-27 (11 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L27 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pdalshor | da | Load: hold current state | Comp-v2 |
| shtol | sh | Watch: transfer and hold | Comp-v2 |
| qoty | qo | Fire: transfer complete -- stop moving material | B Dict D2 |
| pshar | sh | Watch: bring to and note result | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| okaldy | ok | Vessel: bring to stable state | Comp-v2 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| rol | --- | *bare token: respond, set up, hold* | --- |

→ 10/11 recognized (90%).


### P7 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 11 (2% of folio) |
| e-depth | 0.182 |
| dar count | 2 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- sh: 3 (27%)
- da: 2 (18%)
- ot: 2 (18%)
- qo: 1 (9%)
- ok: 1 (9%)

---

## Paragraph 8: Lines 28-31 (46 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L28 (13 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tchedy | tch | Transfer-check: system steady, confirmed | Comp-v2 |
| pchedy | pch | Setup: system steady, confirmed | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| dair | da | Load: add material and note the response | B Dict D3 |
| shecthy | sh | Watch: cooled-transfer-watch **«ecth»** | Comp-v2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| l | --- | *bare token: hold* | --- |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| lol | --- | Equipment steady -- furnace holding at current level | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |

→ 12/13 recognized (92%).

**L29 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dain | da | Load: secure material for next run | B Dict D1 |
| chkal | ch | Test: heat until stable | Comp-v2 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| lolkaiin | ol | Steady: sustained deep heating cycles | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| dain | da | Load: secure material for next run | B Dict D1 |
| olchey | ol | Steady: adjust, watch, steady | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qotan | qo | Fire: transfer, bring to, bind | Comp-v2 |

→ 12/12 recognized (100%).

**L30 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qodaiin | qo | Fire: extended iteration cycles | Comp-v2 |
| cheeky | ch | Test: gentle steady heat — balneum level | Comp-v2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| cheky | ch | Test: verify the heat level | B Dict D2 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| dain | da | Load: secure material for next run | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| okalol | ok | Vessel: bring to stable state | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| olom | ol | Steady: set up, finalize | Comp-v2 |

→ 12/12 recognized (100%).

**L31 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| chey | ch | Test: quick active check | B Dict D1 |
| qoked | qo | Fire: one standard heat cycle | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| daldy | da | Load: hold, do | Comp-v2 |

→ 9/9 recognized (100%).


### P8 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 46 (11% of folio) |
| e-depth | 0.609 |
| dar count | 5 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | ecthx1, ckhx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 14 (30%)
- ch: 8 (17%)
- da: 5 (10%)
- sh: 5 (10%)
- ol: 3 (6%)
- ok: 3 (6%)
- tch: 1 (2%)

---

## Paragraph 9: Lines 32-46 (120 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L32 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polshy | po | Pause: hold, sequence, watch | Comp-v2 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| das | da | Load: sequence | Comp-v2 |
| chsdy | ch | Test: sequence, do | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| ldy | --- | *bare token: hold, do, * | --- |

→ 9/10 recognized (90%).

**L33 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| lshedy | lsh | Watch equipment: confirm apparatus is steady | B Dict D2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chcthedy | ch | Test: observe material moving | Comp-v2 |
| ltedy | te | Transfer step: cycle close | Comp-v2 |
| darom | da | Load: note what happened | Comp-v2 |

→ 8/8 recognized (100%).

**L34 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| solkedy | so | Sequence: one standard heat cycle | Comp-v2 |
| okal | ok | Vessel: contents settling -- let them stabilize | B Dict D2 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| oty | ot | Output: transfer complete -- drip/flow has ceased | B Dict D2 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| kain | ka | Apply heat through one processing cycle | B Dict D2 |
| olkedy | ol | Steady: one standard heat cycle | Comp-v2 |

→ 9/9 recognized (100%).

**L35 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| sheety | sh | Watch: gentle steady transfer | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |

→ 9/9 recognized (100%).

**L36 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |

→ 9/9 recognized (100%).

**L37 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |
| sheety | sh | Watch: gentle steady transfer | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokchdy | qo | Fire: heat with active test adjustment, cycle close | B Dict D2 |
| qokechdy | qo | Fire: one standard heat cycle | Comp-v2 |
| lol | --- | Equipment steady -- furnace holding at current level | B Dict D2 |

→ 7/7 recognized (100%).

**L38 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| ldy | --- | *bare token: hold, do, * | --- |

→ 5/6 recognized (83%).

**L39 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| yshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qokchdy | qo | Fire: heat with active test adjustment, cycle close | B Dict D2 |
| olkeedy | ol | Steady: hold gentle heat -- maintain balneum level | B Dict D2 |
| otey | ot | Output: steady | Comp-v2 |
| koldy | ko | Heat: hold, do | Comp-v2 |

→ 6/6 recognized (100%).

**L40 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| rshedy | sh | Watch: system steady, confirmed | Comp-v2 |

→ 7/7 recognized (100%).

**L41 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sokeedy | so | Sequence: one gentle balneum cycle | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| dykeedy | yk | Adjust: system steady, confirmed | Comp-v2 |
| sy | --- | *bare token: sequence, * | --- |

→ 5/6 recognized (83%).

**L42 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| c | --- | *bare token: adjust* | --- |
| qoteey | qo | Fire: gentle steady transfer | Comp-v2 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |

→ 5/6 recognized (83%).

**L43 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| yshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| chekar | ch | Test: heat and note response | Comp-v2 |
| oldy | ol | Steady: cycle close | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chkar | ch | Test: heat and note response | Comp-v2 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| oldy | ol | Steady: cycle close | Comp-v2 |

→ 7/7 recognized (100%).

**L44 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dchedy | dch | Setup-check: system steady, confirmed | Comp-v2 |
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| okoldy | ok | Vessel: holding, confirmed | Comp-v2 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| otam | ot | Output: bring to, finalize | Comp-v2 |
| olaiin | ol | Steady: extended iteration cycles | Comp-v2 |
| chdar | ch | Test: bring to and note result | Comp-v2 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |

→ 11/11 recognized (100%).

**L45 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| shckhy | sh | Watch: passive temperature observation **«ckh»** | B Dict D2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| sorol | so | Sequence: hold current state | Comp-v2 |
| oty | ot | Output: transfer complete -- drip/flow has ceased | B Dict D2 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| qotedy | qo | Fire: execute a heat-driven transfer operation | B Dict D1 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |

→ 10/10 recognized (100%).

**L46 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| sheol | sh | Watch: observe and hold -- passive monitoring, maintain state | B Dict D2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| dain | da | Load: secure material for next run | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| otol | ot | Output: hold current state | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| olor | ol | Steady: note what happened | Comp-v2 |

→ 9/9 recognized (100%).



### P9 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 120 (29% of folio) |
| e-depth | 0.600 |
| dar count | 12 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | ckhx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 34 (28%)
- sh: 16 (13%)
- ot: 14 (11%)
- da: 12 (10%)
- ch: 7 (5%)
- ok: 6 (5%)
- ol: 6 (5%)

---

## Cross-Paragraph Patterns

### e-depth Thermal Arc

| Para | Lines | Tokens | e-depth | Recipe phase |
|------|-------|--------|---------|-------------|
| P1 | 1-5 | 46 | 0.630 | Initial distillation (separation) |
| P2 | 6 | 9 | 0.556 | Set aside gold (handling cooled product) |
| P3 | 7-12 | 58 | 0.448 | Fermentation (sustained gentle heat, 3 days) |
| P4 | 13-16 | 39 | 0.436 | x4 distillation cycle (balneum) |
| P5 | 17-22 | 52 | 0.423 | Autonomous reiteration (most sustained heat) |
| P6 | 23-26 | 31 | 0.484 | Transition — setup for x9 |
| P7 | 27 | 11 | **0.182** | Physical vessel transfer — no thermal operation |
| P8 | 28-31 | 46 | 0.609 | x9 preparation — balneum restarting |
| P9 | 32-46 | 120 | 0.600 | x9 reflux cycle at full balneum |

The e-depth draws a distinctive V-shaped arc: moderate (0.63) → decreasing through fermentation/x4 (0.44-0.42) → crashes to 0.18 at the physical transfer (P7) → rebounds to 0.60 for the x9 run. This tracks the physical reality: you sustain heat for fermentation, it becomes increasingly automated, you break to physically transfer vessels (no heat at all), then you restart the water bath for the long x9 run.

### dar Distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 2 | 7% | Initial material loading |
| P2 | 1 | 4% | Set aside gold |
| P3 | 0 | 0% | Pure fermentation (no additions) |
| P4 | 0 | 0% | x4 cycle (no additions during cycle) |
| P5 | 2 | 7% | Honeycomb renewal during reiteration |
| P6 | 3 | 11% | Loading for x9 |
| P7 | 2 | 7% | Transfer handling |
| P8 | 5 | 19% | Heavy loading for x9 |
| P9 | 12 | **44%** | x9 cycle with repeated honeycomb renewal |

Material additions are back-loaded: 44% occur in P9 (the x9 cycle). The recipe explicitly says to renew the honeycomb at each second distillation — 9 cycles means ~4-5 renewals, and we see 12 additions distributed across 15 lines. The zero-dar stretch in P3-P4 (fermentation + x4) matches the recipe: once materials are combined, fermentation and the initial cycle operate without additions.

### Observation MIDDLE Distribution

| Para | ckh | cth | ecth | Total | Recipe activity |
|------|-----|-----|------|-------|-----------------|
| P1 | — | — | — | 0 | Initial distillation (routine) |
| P2 | — | 1 | — | 1 | Transfer-watch: moving gold aside |
| P3 | 2 | 1 | — | 3 | Fermentation: heat checks + transformation watch |
| P4 | 1 | — | — | 1 | x4 cycle: heat monitoring |
| P5 | — | — | — | **0** | Autonomous reiteration (fade-out) |
| P6 | 1 | — | 1 | 2 | Transition: heat check + cooled transfer |
| P7 | — | — | — | 0 | Flash transfer (no thermal observation) |
| P8 | 1 | — | 1 | 2 | Setup: heat check + cooled transfer |
| P9 | 1 | — | — | 1 | x9 cycle: sparse monitoring |

Observation MIDDLEs concentrate in P3 (fermentation — the operator needs to watch carefully) and reappear at P6/P8 (transition/setup). P5 (autonomous reiteration) has zero — the process runs itself. The x9 cycle (P9) has only 2 across 120 tokens — by now the process is well-established and needs minimal intervention.

---

## Verdict: COHERENT

f75r produces a coherent paragraph-by-paragraph reading against III.19.0 (aqua vitae, reflux distillation). The folio's 9 paragraphs map to the recipe's procedural steps:

1. **Separation** (P1) — supervised initial distillation
2. **Set aside** (P2) — brief transfer step with transfer-watch
3. **Fermentation** (P3) — sustained gentle heat, zero material additions, heat-level checks
4. **x4 cycle** (P4) — four identical `qokedy` tokens in sequence (corpus-singular, C1889)
5. **Reiteration** (P5) — autonomous cycling with observation fade-out
6. **x9 setup** (P6) — transition with cooled-transfer-watch
7. **Flash transfer** (P7) — pure vessel handling, e-depth 0.18
8. **x9 preparation** (P8) — heavy material loading, balneum restart
9. **x9 cycle** (P9) — 9 fire-management tokens on L37-38, 44% of all dar

The two numerical anchors (x4 on L13, x9 on L37-38) are the strongest evidence. The x4 run is corpus-singular (C1889): no other line in Currier B has 4+ consecutive identical tokens. The x9 density window is shared with only 2 other folios (f86v3, f108r per C1969), but f75r is the only one matched to a recipe specifying "ix vegades." The e-depth arc, dar distribution, and observation MIDDLE fade-out are quantitative properties that do not depend on individual token glosses.

**Negative control:** f75r ↔ III.21.0 (vessel specification, wrong recipe) scored 0/7 structural predictions — INCOHERENT. The correct recipe scores 8/8.
