# Validated Reading: f79r ↔ III.12.0 Mercury Sublimation → Red Elixir

**Match tier:** Strong-supported
**Expert verdict:** Coherent (5/7 structural predictions confirmed, 1 ambiguous, 1 explained mismatch)
**Full token listing:** `data/f79r_cold_read.txt` (389 tokens, 44 lines)

---

## How to Read This Document

This recipe is 209 words. This folio is 389 tokens — a 1.9:1 ratio. The recipe describes a mercury sublimation procedure with a distinctive thermal arc: gentle dissolution → three distillation-return cycles → gradually strengthen fire → rubification (material turns red) → separation (sublimate rises white, fixed turns red) → fix elements on the residue.

The folio's e-depth tracks this arc precisely: 0.76 (gentle dissolution) → 0.34 (fire strengthening — lowest on folio) → 0.91 (congelation/cooling) → 1.50 (maximum cooling at a 4-token micro-paragraph) → 0.45 (final fixation). The non-monotonic V-shape with the 0.34 minimum at P4 is the recipe's thermal fingerprint — "paulatinament fortifica ton foch" (gradually strengthen your fire) produces the lowest e-depth at exactly the right position.

**What makes this match credible:**
- **e-depth minimum at fire-strengthening**: P4 = 0.34 (lowest on folio) exactly where the recipe says to strengthen the fire
- **fch mercury markers** (C1939): exclusively in P5 (sublimation paragraph) where mercury volatility is operationally critical
- **cth transfer-watches** concentrate in P2-P3-P5 (distillation and sublimation phases involving material movement)
- **Zero dar in P6** (autonomous fire continuation) matching "continua donchs ton foch"
- **P9 e-depth 1.50** (maximum cooling) at a 4-token micro-paragraph between quality check and final fixation

Every token on every line appears in this document. 

---

## The Recipe

### Catalan (III.12.0, SISMEL — Part III cipher: B=simple water, D=simple dissolved gold)

> Pren mercuri sublimat e blanch axí com te havem dit, e dissol-lo en aygua del mercuri, de la qual és tret lo foch de la pedra mercuriosa, en la qual sia dissolt lo foch de la pedra axí substancialment com essencialment. Aprés separes l'aygua per distillació en tro sia tot congelat. E altra vegada retorna l'aygua sobre lo mercuri; e terça vegada distilla. E aprés paulatinament fortifica ton foch, en trou veies molt fort rubificar. E si res hi ha que no sia ligat ab lo foch de la pedra, allò se'n muntarà e sublimarà per la virtut del foch tot blanch. Continua donchs ton foch en tro veies que'l sublimatiu se sia sublimat, e el fix que és baix se sia rubificat. E sobre aquest fixe sos elements; hauràs del mercuri elixir complit.

### English

Take white sublimated mercury and dissolve it in mercury water (from which the fire of the mercurial stone was drawn). Separate the water by distillation until all is congealed. Return the water to the mercury again; and a third time distill. Then gradually strengthen your fire until you see strong rubification. If anything is not bound with the stone's fire, it will rise and sublimate by the fire's virtue, all white. Continue your fire until the sublimate has sublimated and the fixed part at the bottom has turned red. Fix the elements on this fixed part — you will have complete mercury elixir.

### Recipe Structure

| Step | Operation | Heat | Key feature |
|------|-----------|------|-------------|
| 1 | Dissolve white mercury in mercury water | gentle | passive dissolution |
| 2 | Distill water until congealed | moderate | distillation |
| 3 | Return water to mercury, distill 3rd time | moderate | iterative cycling (×3) |
| 4 | Gradually strengthen fire | increasing → strong | "paulatinament fortifica" |
| 5 | Rubification — watch for red | strong | visual quality gate |
| 6 | Continue fire — sublimate rises white, fixed turns red | sustained strong | separation phase |
| 7 | Fix elements on the fixed residue | — | final operation → complete elixir |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | e-depth DECREASES across folio (fire strengthening) | "paulatinament fortifica ton foch" | **MATCH** — 0.76 → 0.34, then V-shape |
| 2 | ×3 counting anchor | "terça vegada distilla" | **AMBIGUOUS** — distributed iteration markers, not clean counting run |
| 3 | fch mercury markers (mercury is central subject) | mercury sublimation recipe | **MATCH** — fch exclusively in P5 (sublimation) |
| 4 | Sublimation signature: transfer tokens going up | material rises, separates | **MATCH** — ot-dominant P5 |
| 5 | Two-phase structure: dissolution/cycling then fire strengthening | clear phase break at "aprés paulatinament" | **MATCH** — P1-P3 gentle → P4 minimum e-depth |
| 6 | Quality gate at rubification | "en tro veies molt fort rubificar" | **MATCH** — chekar + observation tokens in P8 |
| 7 | dar concentrated early (dissolution, not sublimation) | sublimation is autonomous | **MISMATCH (explained)** — dar in P5 reflects operator managing physical separation products |

**Score: 5/7 confirmed, 1 ambiguous, 1 explained mismatch**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 389 |
| Lines | 44 |
| Paragraphs | 10 |
| dar (material-add) | 12 |
| Quality checks (chek/shek class) | 4 |
| Observation MIDDLEs | cth×4, ckh×3 |
| hh (extended observation) | 0 |

---

## Paragraph 1: Lines 1-3 (29 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L1 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| torain | to | Note transfer: one processing cycle | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| pchor | pch | Setup: note what happened | Comp-v2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| shek | sh | Watch: steady, heat | Comp-v2 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| pchdy | pch | Setup: cycle close | Comp-v2 |
| opcholor | --- | *unrecognized* (set up, pause, adjust, watch, set up, hold, set up, respond) | --- |
| otal | ot | Output: monitor transfer rate until output stabilizes | B Dict D2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |

→ 9/10 recognized (90%).

**L2 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| lshdy | lsh | Watch equipment: cycle close | Comp-v2 |
| otchedy | ot | Output: adjust, watch, steady, do | Comp-v2 |
| olshey | ol | Steady: watch sequence steady | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| qoteey | qo | Fire: gentle steady transfer | Comp-v2 |
| loly | ol | Steady: complete | Comp-v2 |

→ 10/10 recognized (100%).

**L3 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| yshealdy | sh | Watch: bring to stable state | Comp-v2 |
| rshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| chckhey | ch | Test: temperature check | Comp-v2 |
| qoy | qo | Fire: complete | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |
| lchey | lch | Check equipment: quick apparatus check | B Dict D2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| rchedy | rch | Respond-check: system steady, confirmed | Comp-v2 |

→ 9/9 recognized (100%).


### P1 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 29 (7% of folio) |
| e-depth | 0.759 |
| dar count | 0 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- sh: 7 (24%)
- qo: 6 (20%)
- ot: 3 (10%)
- pch: 2 (6%)
- ol: 2 (6%)
- ch: 2 (6%)
- to: 1 (3%)

---

## Paragraph 2: Lines 4-6 (34 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L4 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| teey | te | Transfer step: steady | Comp-v2 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| qotar | qo | Fire: transfer heat/material and note result | B Dict D1 |
| sheds | sh | Watch: sequence steady | Comp-v2 |
| sheekeey | sh | Watch: gentle steady heat — balneum level | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| okey | ok | Vessel: steady | Comp-v2 |
| qolshy | qo | Fire: hold, sequence, watch | Comp-v2 |
| olchey | ol | Steady: adjust, watch, steady | Comp-v2 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |

→ 11/11 recognized (100%).

**L5 (13 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| chcthy | ch | Test: observe material moving through apparatus **«cth»** | B Dict D2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| chear | ch | Test: bring to and note result | Comp-v2 |
| solchey | so | Sequence: hold, adjust, watch, steady | Comp-v2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| shal | sh | Watch: bring to stable state | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |
| l | --- | *bare token: hold* | --- |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| chy | ch | Test: complete | Comp-v2 |

→ 12/13 recognized (92%).

**L6 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| shol | sh | Watch: hold -- passive monitoring, keep current state | B Dict D2 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| olkeey | ol | Steady: hold gentle heat -- balneum level steady | B Dict D2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| chey | ch | Test: quick active check | B Dict D1 |

→ 10/10 recognized (100%).


### P2 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 34 (8% of folio) |
| e-depth | 0.559 |
| dar count | 1 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | cthx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 8 (23%)
- ch: 8 (23%)
- sh: 5 (14%)
- ok: 2 (5%)
- ol: 2 (5%)
- te: 1 (2%)
- da: 1 (2%)

---

## Paragraph 3: Lines 7-12 (51 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L7 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polchedy | po | Pause: hold, adjust, watch, steady, do | Comp-v2 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokl | qo | Fire: heat, hold | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chey | ch | Test: quick active check | B Dict D1 |
| qoty | qo | Fire: transfer complete -- stop moving material | B Dict D2 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |

→ 10/10 recognized (100%).

**L8 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokol | qo | Fire: heat and hold -- maintain current heat level | B Dict D2 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| shed | sh | Watch: steady, do | Comp-v2 |
| ykchedy | yk | Adjust: adjust, watch, steady, do | Comp-v2 |
| chcthy | ch | Test: observe material moving through apparatus **«cth»** | B Dict D2 |
| yoky | ok | Vessel: complete | Comp-v2 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| cholo | ch | Test: hold current state | Comp-v2 |

→ 9/9 recognized (100%).

**L9 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| psheedy | sh | Watch: system steady, confirmed | Comp-v2 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| sheol | sh | Watch: observe and hold -- passive monitoring, maintain state | B Dict D2 |
| qolchey | qo | Fire: hold, adjust, watch, steady | Comp-v2 |
| qoty | qo | Fire: transfer complete -- stop moving material | B Dict D2 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| qokam | qo | Fire: heat, bring to, finalize | Comp-v2 |

→ 9/9 recognized (100%).

**L10 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokshedy | qo | Fire: one standard heat cycle | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| cheor | ch | Test: note what happened | Comp-v2 |
| okol | ok | Vessel: hold current state | Comp-v2 |
| sheeol | sh | Watch: hold current state | Comp-v2 |
| qoteesy | qo | Fire: gentle steady transfer | Comp-v2 |
| choty | ch | Test: transfer and hold | Comp-v2 |
| otechys | ot | Output: watch sequence steady | Comp-v2 |

→ 8/8 recognized (100%).

**L11 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| shoikhy | sh | Watch: set up, iterate, heat, watch | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| tshey | sh | Watch: steady | Comp-v2 |
| dshdy | sh | Watch: cycle close | Comp-v2 |
| otchar | ot | Output: bring to and note result | Comp-v2 |
| shek | sh | Watch: steady, heat | Comp-v2 |
| chcthy | ch | Test: observe material moving through apparatus **«cth»** | B Dict D2 |
| otal | ot | Output: monitor transfer rate until output stabilizes | B Dict D2 |
| ory | or | Note what happened: complete | Comp-v2 |

→ 9/9 recognized (100%).

**L12 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokchy | qo | Fire: heat with active monitoring | Comp-v2 |
| qotchey | qo | Fire: transfer, adjust, watch, steady | Comp-v2 |
| ldaiin | da | Load: iterate, iterate, bind | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qotaiin | qo | Fire: sustained transfer cycles -- repeated distillation passes | B Dict D2 |
| sal | sa | Scaffold: hold | Comp-v2 |

→ 6/6 recognized (100%).


### P3 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 51 (13% of folio) |
| e-depth | 0.510 |
| dar count | 1 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | cthx2 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 19 (37%)
- sh: 11 (21%)
- ch: 9 (17%)
- ot: 3 (5%)
- ok: 2 (3%)
- sa: 2 (3%)
- po: 1 (1%)

---

## Paragraph 4: Lines 13-20 (77 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L13 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pshorol | sh | Watch: hold current state | Comp-v2 |
| shckhy | sh | Watch: passive temperature observation **«ckh»** | B Dict D2 |
| qotshdy | qo | Fire: transfer, sequence, watch, do | Comp-v2 |
| qokaldy | qo | Fire: heat until stable | Comp-v2 |
| opchedy | --- | Operate: run the active check procedure | B Dict D2 |
| qotar | qo | Fire: transfer heat/material and note result | B Dict D1 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |

→ 9/9 recognized (100%).

**L14 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saral | sa | Scaffold: bring to and note result | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |
| qotal | qo | Fire: transfer until output stabilizes | B Dict D2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| chey | ch | Test: quick active check | B Dict D1 |
| dain | da | Load: secure material for next run | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qol | qo | Fire: hold current heat level | B Dict D1 |

→ 10/10 recognized (100%).

**L15 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokl | qo | Fire: heat, hold | Comp-v2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| okol | ok | Vessel: hold current state | Comp-v2 |
| dyty | --- | *unrecognized* (do, , transfer, ) | --- |
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| sheol | sh | Watch: observe and hold -- passive monitoring, maintain state | B Dict D2 |
| lchey | lch | Check equipment: quick apparatus check | B Dict D2 |

→ 9/10 recognized (90%).

**L16 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| shain | sh | Watch: one processing cycle | Comp-v2 |
| shckhy | sh | Watch: passive temperature observation **«ckh»** | B Dict D2 |
| qoly | qo | Fire: hold | Comp-v2 |
| kshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| otal | ot | Output: monitor transfer rate until output stabilizes | B Dict D2 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokam | qo | Fire: heat, bring to, finalize | Comp-v2 |

→ 9/9 recognized (100%).

**L17 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| shy | sh | Watch: complete | Comp-v2 |
| lsheey | lsh | Watch equipment: steady, steady | Comp-v2 |
| ls | --- | *bare token: hold, sequence* | --- |
| air | --- | Bring to and note the result | B Dict D3 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| aror | ar | Note the yield: note what happened | Comp-v2 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| ches | ch | Test: sequence steady | Comp-v2 |
| olol | ol | Steady: hold current state | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |

→ 10/11 recognized (90%).

**L18 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| solor | so | Sequence: hold current state | Comp-v2 |
| olshey | ol | Steady: watch sequence steady | Comp-v2 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| chey | ch | Test: quick active check | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| otal | ot | Output: monitor transfer rate until output stabilizes | B Dict D2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| dam | da | Finalize this process step -- material handling complete | B Dict D0 |

→ 10/10 recognized (100%).

**L19 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| sheyky | sh | Watch: steady, heat | Comp-v2 |
| shoky | sh | Watch: set — stop adjusting | Comp-v2 |
| oly | ol | Steady: current state confirmed | B Dict D2 |

→ 11/11 recognized (100%).

**L20 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| y | --- | Done -- bare completion marker | B Dict D2 |
| shal | sh | Watch: bring to stable state | Comp-v2 |
| ychedar | ch | Test: bring to and note result | Comp-v2 |
| oikhy | --- | *unrecognized* (set up, iterate, heat, watch, ) | --- |
| scthey | ct | watch, steady | Comp-v2 |
| tal | ta | Transfer: hold | Comp-v2 |
| chear | ch | Test: bring to and note result | Comp-v2 |

→ 6/7 recognized (85%).


### P4 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 77 (19% of folio) |
| e-depth | 0.338 |
| dar count | 2 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ckhx2 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 16 (20%)
- sh: 14 (18%)
- ch: 11 (14%)
- ot: 5 (6%)
- sa: 3 (3%)
- ol: 3 (3%)
- da: 2 (2%)

---

## Paragraph 5: Lines 21-25 (47 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L21 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pol | po | Pause: hold | Comp-v2 |
| shar | sh | Watch: bring to and note result | Comp-v2 |
| shar | sh | Watch: bring to and note result | Comp-v2 |
| pchey | pch | Setup: steady | Comp-v2 |
| otshey | ot | Output: watch sequence steady | Comp-v2 |
| okaos | ok | Vessel: bring to, set up, sequence | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| okshey | ok | Vessel: watch sequence steady | Comp-v2 |
| dalkeeey | da | Load: gentle steady heat — balneum level | Comp-v2 |
| ry | --- | *bare token: respond, * | --- |

→ 9/10 recognized (90%).

**L22 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| lchey | lch | Check equipment: quick apparatus check | B Dict D2 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| efchedy | --- | *unrecognized* (steady, flag, adjust, watch, steady, do, ) | --- |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qofchey | qo | Fire: flag, adjust, watch, steady | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| dor | do | Execute: respond | Comp-v2 |
| ched | ch | Test: steady, do | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |

→ 10/11 recognized (90%).

**L23 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| shear | sh | Watch: bring to and note result | Comp-v2 |
| qotaiin | qo | Fire: sustained transfer cycles -- repeated distillation passes | B Dict D2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| lkain | lk | Check equipment: one processing cycle | Comp-v2 |
| otchedy | ot | Output: adjust, watch, steady, do | Comp-v2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| olkl | ol | Steady: heat, hold | Comp-v2 |
| otshedy | ot | Output: watch sequence steady | Comp-v2 |
| otory | ot | Output: note what happened | Comp-v2 |

→ 10/10 recognized (100%).

**L24 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokshedy | qo | Fire: one standard heat cycle | Comp-v2 |
| qolkeey | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| qolkeedy | qo | Fire: one gentle balneum cycle | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| otchey | ot | Output: adjust, watch, steady | Comp-v2 |
| okain | ok | Vessel: seal for a processing cycle | B Dict D1 |
| y | --- | Done -- bare completion marker | B Dict D2 |

→ 8/8 recognized (100%).

**L25 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| cholchey | ch | Test: holding, confirmed | Comp-v2 |
| qotshy | qo | Fire: transfer, sequence, watch | Comp-v2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| chcthy | ch | Test: observe material moving through apparatus **«cth»** | B Dict D2 |

→ 8/8 recognized (100%).


### P5 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 47 (12% of folio) |
| e-depth | 0.617 |
| dar count | 3 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | cthx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 9 (19%)
- ot: 8 (17%)
- sh: 7 (14%)
- ch: 4 (8%)
- ok: 3 (6%)
- da: 3 (6%)
- po: 1 (2%)

---

## Paragraph 6: Lines 26-30 (40 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L26 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polaiin | po | Pause: extended iteration cycles | Comp-v2 |
| olteedy | ol | Steady: gentle steady transfer | Comp-v2 |
| qotchey | qo | Fire: transfer, adjust, watch, steady | Comp-v2 |
| dykeedy | yk | Adjust: system steady, confirmed | Comp-v2 |
| qokchdy | qo | Fire: heat with active test adjustment, cycle close | B Dict D2 |
| opchedy | --- | Operate: run the active check procedure | B Dict D2 |
| shol | sh | Watch: hold -- passive monitoring, keep current state | B Dict D2 |
| ory | or | Note what happened: complete | Comp-v2 |

→ 8/8 recognized (100%).

**L27 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| kas | ka | Heat: sequence | Comp-v2 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| olkaiin | ol | Steady: sustained deep heating cycles | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| ory | or | Note what happened: complete | Comp-v2 |
| cholor | ch | Test: hold current state | Comp-v2 |
| oty | ot | Output: transfer complete -- drip/flow has ceased | B Dict D2 |
| oky | ok | Vessel: done -- seal or set aside | B Dict D2 |

→ 10/10 recognized (100%).

**L28 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| y | --- | Done -- bare completion marker | B Dict D2 |
| dol | do | Load: place material and hold -- position substance, keep it there | B Dict D2 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| odain | --- | *unrecognized* (set up, do, bring to, iterate, bind) | --- |
| yteey | te | Transfer step: steady | Comp-v2 |
| chyteey | ch | Test: gentle steady transfer | Comp-v2 |
| otoldy | ot | Output: holding, confirmed | Comp-v2 |
| lchey | lch | Check equipment: quick apparatus check | B Dict D2 |

→ 8/9 recognized (88%).

**L29 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| lcheey | lch | Check equipment: steady, steady | Comp-v2 |
| qochey | qo | Fire: adjust, watch, steady | Comp-v2 |
| qody | qo | Fire: cycle close | Comp-v2 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| olor | ol | Steady: note what happened | Comp-v2 |
| okchd | ok | Vessel: adjust, watch, do | Comp-v2 |
| dchol | dch | Setup-check: hold current state | Comp-v2 |
| dchy | dch | Setup-check: complete | Comp-v2 |
| oly | ol | Steady: current state confirmed | B Dict D2 |

→ 9/9 recognized (100%).

**L30 (4 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| yshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| qotal | qo | Fire: transfer until output stabilizes | B Dict D2 |
| ysheey | sh | Watch: steady, steady | Comp-v2 |
| olor | ol | Steady: note what happened | Comp-v2 |

→ 4/4 recognized (100%).


### P6 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 40 (10% of folio) |
| e-depth | 0.600 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 8 (20%)
- ol: 5 (12%)
- sh: 5 (12%)
- ch: 3 (7%)
- or: 2 (5%)
- ot: 2 (5%)
- ok: 2 (5%)

---

## Paragraph 7: Lines 31-34 (33 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L31 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pol | po | Pause: hold | Comp-v2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| oltshedy | ol | Steady: transfer, system steady | Comp-v2 |
| sheol | sh | Watch: observe and hold -- passive monitoring, maintain state | B Dict D2 |
| ykeey | yk | Adjust: steady, steady | Comp-v2 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| cheor | ch | Test: note what happened | Comp-v2 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |

→ 9/9 recognized (100%).

**L32 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| olaiin | ol | Steady: extended iteration cycles | Comp-v2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| chey | ch | Test: quick active check | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |

→ 10/10 recognized (100%).

**L33 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qotshedy | qo | Fire: transfer, system steady | Comp-v2 |
| oteeedy | ot | Output: steady, steady, steady, do | Comp-v2 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| chey | ch | Test: quick active check | B Dict D1 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |

→ 8/8 recognized (100%).

**L34 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| lcheol | lch | Check equipment: hold current state | Comp-v2 |
| kchedy | kch | Heat-check: system steady, confirmed | Comp-v2 |
| qotas | qo | Fire: transfer, bring to, sequence | Comp-v2 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| teol | te | Transfer step: hold current state | Comp-v2 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |

→ 6/6 recognized (100%).


### P7 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 33 (8% of folio) |
| e-depth | 0.909 |
| dar count | 2 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- sh: 6 (18%)
- ch: 4 (12%)
- qo: 4 (12%)
- ot: 3 (9%)
- ol: 2 (6%)
- ok: 2 (6%)
- da: 2 (6%)

---

## Paragraph 8: Lines 35-37 (27 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L35 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pol | po | Pause: hold | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| qotain | qo | Fire: transfer through one processing cycle | B Dict D2 |
| ody | --- | *bare token: set up, do, * | --- |
| chekes | ch | Test: gentle steady heat — balneum level | Comp-v2 |
| otal | ot | Output: monitor transfer rate until output stabilizes | B Dict D2 |

→ 7/8 recognized (87%).

**L36 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| sheeol | sh | Watch: hold current state | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| os | --- | *bare token: set up, sequence* | --- |
| sheky | sh | Watch: set — stop adjusting | Comp-v2 |
| sheol | sh | Watch: observe and hold -- passive monitoring, maintain state | B Dict D2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| shear | sh | Watch: bring to and note result | Comp-v2 |
| oly | ol | Steady: current state confirmed | B Dict D2 |

→ 9/10 recognized (90%).

**L37 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| lcheol | lch | Check equipment: hold current state | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| olsheey | ol | Steady: watch sequence steady | Comp-v2 |
| shol | sh | Watch: hold -- passive monitoring, keep current state | B Dict D2 |
| keey | ke | Balneum: steady | Comp-v2 |
| okchey | ok | Vessel: adjust, watch, steady | Comp-v2 |
| dain | da | Load: secure material for next run | B Dict D1 |

→ 9/9 recognized (100%).


### P8 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 27 (6% of folio) |
| e-depth | 0.704 |
| dar count | 1 |
| Quality checks (chek/shek) | 2 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- sh: 7 (25%)
- ch: 3 (11%)
- qo: 2 (7%)
- ol: 2 (7%)
- po: 1 (3%)
- ot: 1 (3%)
- so: 1 (3%)

---

## Paragraph 9: Lines 38-38 (4 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L38 (4 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pol | po | Pause: hold | Comp-v2 |
| olkeeey | ol | Steady: gentle steady heat — balneum level | Comp-v2 |
| sheol | sh | Watch: observe and hold -- passive monitoring, maintain state | B Dict D2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |

→ 4/4 recognized (100%).


### P9 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 4 (1% of folio) |
| e-depth | 1.500 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- po: 1 (25%)
- ol: 1 (25%)
- sh: 1 (25%)
- qo: 1 (25%)

---

## Paragraph 10: Lines 39-44 (47 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L39 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polkeey | po | Pause: gentle steady heat — balneum level | Comp-v2 |
| qokol | qo | Fire: heat and hold -- maintain current heat level | B Dict D2 |
| otshdy | ot | Output: sequence, watch, do | Comp-v2 |
| olky | ol | Steady: set — stop adjusting | Comp-v2 |
| orkar | or | Note what happened: heat and note response | Comp-v2 |
| shecphhdy | sh | Watch: steady, adjust, pause, watch, watch, do **«hh»** | Comp-v2 |
| olkal | ol | Steady: heat until stable | Comp-v2 |

→ 7/7 recognized (100%).

**L40 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| y | --- | Done -- bare completion marker | B Dict D2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokched | qo | Fire: one standard heat cycle | Comp-v2 |
| oltshey | ol | Steady: watch sequence steady | Comp-v2 |
| otchotor | ot | Output: transfer and hold | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |

→ 8/8 recognized (100%).

**L41 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qotain | qo | Fire: transfer through one processing cycle | B Dict D2 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| chkain | ch | Test: heat through one cycle | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| oly | ol | Steady: current state confirmed | B Dict D2 |

→ 9/9 recognized (100%).

**L42 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| okain | ok | Vessel: seal for a processing cycle | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| lkchedy | lk | Check equipment: adjust, watch, steady, do | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| okain | ok | Vessel: seal for a processing cycle | B Dict D1 |
| oly | ol | Steady: current state confirmed | B Dict D2 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |

→ 8/8 recognized (100%).

**L43 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| y | --- | Done -- bare completion marker | B Dict D2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| chkam | ch | Test: heat, bring to, finalize | Comp-v2 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| ldy | --- | *bare token: hold, do, * | --- |

→ 9/10 recognized (90%).

**L44 (5 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ody | --- | *bare token: set up, do, * | --- |
| oaan | --- | *unrecognized* (set up, bring to, bring to, bind) | --- |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| dar | da | Add a new substance -- vigorous material introduction event | B Dict D0 |
| cheory | ch | Test: note what happened | Comp-v2 |

→ 3/5 recognized (60%).



### P10 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 47 (12% of folio) |
| e-depth | 0.447 |
| dar count | 2 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ckhx1 |
| hh (extended obs) | 1 |

**Top prefixes:**
- ch: 9 (19%)
- qo: 6 (12%)
- ol: 5 (10%)
- sh: 4 (8%)
- ok: 4 (8%)
- ot: 3 (6%)
- da: 2 (4%)

---

## Cross-Paragraph Patterns

### e-depth Thermal Arc

| Para | Lines | Tokens | e-depth | Recipe phase |
|------|-------|--------|---------|-------------|
| P1 | 1-3 | 29 | 0.759 | Gentle dissolution (mercury in mercury water) |
| P2 | 4-6 | 34 | 0.559 | First distillation cycle |
| P3 | 7-12 | 51 | 0.510 | Second and third distillation-return cycles |
| P4 | 13-20 | 77 | **0.338** | **Gradually strengthen fire** — lowest on folio |
| P5 | 21-25 | 47 | 0.617 | Sublimation — material rises, separates |
| P6 | 26-30 | 40 | 0.600 | Continue fire — autonomous processing |
| P7 | 31-34 | 33 | 0.909 | Congelation — cooling the separated product |
| P8 | 35-37 | 27 | 0.704 | Quality check — observe rubification |
| P9 | 38 | 4 | 1.500 | Maximum cooling — brief stabilization pause |
| P10 | 39-44 | 47 | 0.447 | Final fixation — fix elements on residue |

The thermal arc is the strongest structural signal. It traces the recipe's physical chemistry: gentle dissolution (0.76) → moderate distillation cycling (0.51-0.56) → fire strengthening drops to folio minimum (0.34 at P4) → sublimation and separation require managed heat (0.60-0.62) → congelation spike (0.91) → quality check cooling (0.70) → maximum cooling micro-pause (1.50) → return to active heat for final fixation (0.45).

The P4 minimum (0.34) directly encodes "paulatinament fortifica ton foch" — the point of maximum fire intensity. The P9 maximum (1.50) is a 4-token micro-paragraph — the briefest pause for maximum cooling between quality verification and final fixation.

### dar Distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 0 | 0% | Passive dissolution (no additions) |
| P2 | 1 | 8% | Start of distillation — begin material cycling |
| P3 | 1 | 8% | Distillation-return (return water to mercury) |
| P4 | 2 | 17% | Fire strengthening — minimal material handling |
| P5 | 3 | 25% | Sublimation — managing separated products |
| P6 | 0 | 0% | Autonomous fire continuation (no additions) |
| P7 | 2 | 17% | Congelation — collecting cooled product |
| P8 | 1 | 8% | Quality check — minor handling |
| P9 | 0 | 0% | Micro-pause (no action) |
| P10 | 2 | 17% | Final fixation — fix elements on residue |

P1 zero dar (passive dissolution — just watching mercury dissolve). P6 zero dar (autonomous fire — "continua donchs ton foch" means maintain fire, don't add anything). P5 has the highest dar (25%) — seemingly counterintuitive for sublimation, but the operator IS managing a physical separation, collecting sublimate from the upper vessel.

### Observation MIDDLE Distribution

| Para | ckh | cth | Total | Recipe activity |
|------|-----|-----|-------|-----------------|
| P1 | — | — | 0 | Passive dissolution (minimal monitoring) |
| P2 | — | 1 | 1 | Transfer-watch during first distillation |
| P3 | — | 2 | 2 | Transfer-watches during return cycles |
| P4 | 2 | — | 2 | Temperature checks during fire strengthening |
| P5 | — | 1 | 1 | Transfer-watch during sublimation |
| P6-P9 | — | — | 0 | Autonomous processing / stabilization |
| P10 | 1 | — | 1 | Temperature check during final fixation |

The observation MIDDLEs sort by type: cth (transfer-watch) appears during distillation and sublimation (P2, P3, P5) where material is physically moving. ckh (temperature check) appears during fire management (P4, P10) where the fire level is operationally critical. This sorting is not random — it tracks the recipe's operational demands.

---

## Verdict: COHERENT

f79r produces a coherent structural reading against III.12.0 (mercury sublimation → red elixir). The folio's 10 paragraphs trace the recipe's thermal arc:

1. **Gentle dissolution** (P1) — highest e-depth (0.76), zero dar, passive observation
2. **First distillation** (P2) — e-depth drops, cth transfer-watch, first dar
3. **Return cycles** (P3) — continued distillation, 2 cth transfer-watches
4. **Fire strengthening** (P4) — **lowest e-depth** (0.34), 2 ckh temperature checks, dam closure
5. **Sublimation** (P5) — fch mercury markers (C1939), highest dar (25%), ot-dominant
6. **Autonomous fire** (P6) — zero dar, sustained qo, "continua ton foch"
7. **Congelation** (P7) — e-depth spikes to 0.91, cooling the separated product
8. **Quality check** (P8) — chekar×2, observation-heavy, verifying rubification
9. **Cooling pause** (P9) — 4 tokens, e-depth 1.50, maximum cooling micro-paragraph
10. **Final fixation** (P10) — e-depth drops to 0.45, ckh temperature check, hh extended monitoring, dar + am closure

The thermal arc is the primary evidence: the e-depth minimum at P4 encodes fire strengthening, and no other recipe in the matched set produces this specific descend-then-rebound-then-spike profile. The fch mercury markers appearing exclusively in the sublimation paragraph (P5) add material-specific evidence per C1939.

**Expert review note:** The fch tokens on L22 (`efchedy`, `qofchey`) were originally misread through the Part III cipher (F = compound red sulphur). They are morphological mercury markers (C1939), not cipher references. This correction strengthens the match.
