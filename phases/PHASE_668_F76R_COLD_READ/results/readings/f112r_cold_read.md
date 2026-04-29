# Validated Reading: f112r ↔ III.11.0 Red Mercury Tincture (Cohobation)

**Match tier:** Supported
**Expert verdict:** Partially Coherent (P14 e-depth contradicts calcination endpoint; no ×3 counting anchor)
**Full token listing:** `data/f112r_cold_read.txt` (394 tokens, 49 lines)

---

## How to Read This Document

This recipe is 213 words. This folio is 394 tokens — a 1.8:1 ratio. The recipe describes creating red mercury tincture through cohobation: alternating balneum and ash distillation, returning water to viscous earth each time, extracting the fire/soul from the earth, and finally washing the fire by distillation and calcination until "red as burning fire."

The folio has 14 paragraphs — a high fragmentation count that encodes the recipe's multi-phase iterative structure with micro-gates at transition points.

**What works:**
- **e-depth oscillation** encodes alternating balneum/ash distillation
- **dar distribution** concentrates in P2-P5 (extraction phases), zero in P6-P14 (process management)
- **Observation MIDDLEs** at the 4 highest-risk moments
- **ok-prefix shift** from transfer monitoring (first half) to vessel management (second half)

**What doesn't work (expert-identified):**
- **P14 e-depth = 0.923** directly contradicts the recipe's calcination endpoint — "lavalo ab distillació et calcinació en tro que sia bé roig" (wash by calcination until red as fire). Per C1225/C1970, calcination should produce near-zero e-depth. This is the strongest negative signal.
- **No ×3 counting anchor** for ".iii. vegades" (three times balneum). Per C1965 standard, the counting shorthand is absent.

Every token on every line appears in this document.

---

## The Recipe

### Catalan (III.11.0, SISMEL — Part III cipher)

> Fill, tu prendràs la liquor derrera que pus greu és separada per distillació sobre cendres; e aquella distillaràs en bany per .iii. vegades. E aprés cascuna distillació, metràs l'aygua sobre la terra viscosa. Separa altra vegada aquella aygua per cendres; açò's fa per entenció que l'aygua traga lo foch qui és en la terra e sia guardat per tinctura. Distilla aquella liquor altra vegada per bany, a fi que's dissoulle del foch, e mit lo foch tot temps a part. Distillada que sia, tira més de la ànima de la terra ab foch sech. E guarda emperò que la terra no's rubifich, car tantost cremaria la tinctura del sofre blanch. E açò reitera en tro que veies la terra comminuida, defallent de tota humiditat. Puis pren lo foch e lavalo ab la distillació et calcinació en tro que sia bé roig así com a foch ardent.

### English

Son, take the last liquor (hardest to separate) by distillation on ashes; distill it in balneum 3 times. After each distillation, put the water on the viscous earth (it dissolves quickly). Separate that water again by ashes — this is to extract the fire from the earth for tincture. Distill the liquor again by balneum to strip the fire; set fire aside. After distillation, extract more soul from the earth with dry fire. But BEWARE: don't let the earth turn red — it would burn the white sulfur tincture. Repeat until the earth is depleted of all moisture. Then take the fire and wash it by distillation and calcination until red as burning fire.

### Recipe Structure

| Step | Operation | Heat | Key feature |
|------|-----------|------|-------------|
| 1 | Distill last liquor on ashes | ashes | initial separation |
| 2 | ×3 balneum distillation + earth return | balneum | cohobation cycle |
| 3 | Ash distillation to extract fire from earth | ashes | alternating regime |
| 4 | Balneum to strip fire from water | balneum | alternating regime |
| 5 | Dry fire extraction of earth's soul | dry fire | strongest heat |
| 6 | BEWARE: don't let earth redden | — | **critical quality gate** |
| 7 | Repeat until earth depleted | gentle | iterative |
| 8 | Wash fire to red via distillation + calcination | calcination | **endpoint: "red as fire"** |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | Alternating e-depth (balneum/ashes cycling) | cohobation = repeated regime switches | **MATCH** — oscillating profile |
| 2 | ×3 counting anchor | ".iii. vegades" | **NOT DETECTED** — no 3-token counting run |
| 3 | dar at earth-return positions | "metràs l'aygua sobre la terra" | **MATCH** — dar in P2-P5 |
| 4 | Quality gate observation MIDDLE | "guarda que la terra no's rubifich" | **MATCH** — observation tokens in P6 area |
| 5 | Final paragraphs = calcination (low e-depth) | "lavalo ab calcinació" | **FAIL** — P14 e-depth 0.923, should be near-zero |
| 6 | Iterative structure | "açò reitera" | **MATCH** — 14 paragraphs with micro-gates |
| 7 | fch mercury markers | creating mercury tincture | **PARTIAL** — low fch presence |

**Score: 4/7 confirmed, 1 partial, 1 not detected, 1 fail**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 394 |
| Lines | 49 |
| Paragraphs | 14 |
| dar (material-add) | 7 |
| Quality checks (chek/shek class) | 1 |
| Observation MIDDLEs | ckh×1, cth×2, ckhh×1 |
| hh (extended observation) | 0 |

---

## Paragraph 1: Lines 1-6 (48 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L1 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| folchey | ol | Steady: adjust, watch, steady | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| ykair | yk | Adjust: bring to and note result | Comp-v2 |
| xar | --- | *bare token: x, bring to, respond* | --- |
| ally | al | Product settled: hold | Comp-v2 |
| oteedal | ot | Output: bring to stable state | Comp-v2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| chcphy | ch | Test: adjust, pause, watch | Comp-v2 |

→ 8/9 recognized (88%).

**L2 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| oar | --- | *bare token: set up, bring to, respond* | --- |
| qolkaiin | qo | Fire: sustained deep heating cycles | Comp-v2 |
| otail | ot | Output: bring to stable state | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| olaiin | ol | Steady: extended iteration cycles | Comp-v2 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |

→ 7/8 recognized (87%).

**L3 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| chedar | ch | Test: bring to and note result | Comp-v2 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| oty | ot | Output: transfer complete -- drip/flow has ceased | B Dict D2 |
| odys | --- | *unrecognized* (set up, do, , sequence) | --- |

→ 7/8 recognized (87%).

**L4 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| chokain | ch | Test: heat through one cycle | Comp-v2 |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| taim | ta | Transfer: iterate, finalize | Comp-v2 |
| oram | or | Note what happened: bring to, finalize | Comp-v2 |

→ 7/7 recognized (100%).

**L5 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| otair | ot | Output: bring to and note result | Comp-v2 |
| okody | ok | Vessel: set up, do | Comp-v2 |
| otody | ot | Output: set up, do | Comp-v2 |
| otal | ot | Output: monitor transfer rate until output stabilizes | B Dict D2 |
| okeeey | ok | Vessel: steady, steady, steady | Comp-v2 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |
| oain | --- | *unrecognized* (set up, bring to, iterate, bind) | --- |
| oy | --- | *bare token: set up, * | --- |

→ 7/9 recognized (77%).

**L6 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| chedal | ch | Test: bring to stable state | Comp-v2 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| olkeedy | ol | Steady: hold gentle heat -- maintain balneum level | B Dict D2 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| oram | or | Note what happened: bring to, finalize | Comp-v2 |

→ 7/7 recognized (100%).


### P1 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 48 (12% of folio) |
| e-depth | 0.604 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ot: 15 (31%)
- ch: 7 (14%)
- qo: 4 (8%)
- ol: 3 (6%)
- ok: 3 (6%)
- or: 2 (4%)
- yk: 1 (2%)

---

## Paragraph 2: Lines 7-10 (30 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L7 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| taiin | ta | Transfer: iterate, iterate, bind | Comp-v2 |
| olkeedy | ol | Steady: hold gentle heat -- maintain balneum level | B Dict D2 |
| qoteo | qo | Fire: transfer and hold | Comp-v2 |
| loeey | --- | *unrecognized* (hold, set up, steady, steady, ) | --- |
| keey | ke | Balneum: steady | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| ram | --- | *bare token: respond, bring to, finalize* | --- |

→ 6/8 recognized (75%).

**L8 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sairor | sa | Scaffold: note what happened | Comp-v2 |
| eteedy | --- | *unrecognized* (steady, transfer, steady, steady, do, ) | --- |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| qotchedy | qo | Fire: transfer, system steady | Comp-v2 |
| dody | do | Execute: cycle close | Comp-v2 |
| qokeeey | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| dair | da | Load: add material and note the response | B Dict D3 |
| ag | --- | *bare token: bring to, g* | --- |

→ 6/8 recognized (75%).

**L9 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| o | --- | *bare token: set up* | --- |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| teedy | te | Transfer step: system steady, confirmed | Comp-v2 |
| qokchy | qo | Fire: heat with active monitoring | Comp-v2 |
| qokary | qo | Fire: heat and note response | Comp-v2 |

→ 8/9 recognized (88%).

**L10 (5 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dair | da | Load: add material and note the response | B Dict D3 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qodain | qo | Fire: one processing cycle | Comp-v2 |
| dam | da | Finalize this process step -- material handling complete | B Dict D0 |

→ 5/5 recognized (100%).


### P2 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 30 (7% of folio) |
| e-depth | 0.767 |
| dar count | 3 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 8 (26%)
- ch: 3 (10%)
- da: 3 (10%)
- sa: 2 (6%)
- ta: 1 (3%)
- ol: 1 (3%)
- ke: 1 (3%)

---

## Paragraph 3: Lines 11-14 (34 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L11 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tchedy | tch | Transfer-check: system steady, confirmed | Comp-v2 |
| qoteey | qo | Fire: gentle steady transfer | Comp-v2 |
| qeol | --- | *unrecognized* (q, steady, set up, hold) | --- |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| otey | ot | Output: steady | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| chotyr | ch | Test: transfer and hold | Comp-v2 |

→ 7/8 recognized (87%).

**L12 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dchedy | dch | Setup-check: system steady, confirmed | Comp-v2 |
| qo | --- | *bare token: q, set up* | --- |
| otchedy | ot | Output: adjust, watch, steady, do | Comp-v2 |
| chdy | ch | Test: check complete | B Dict D2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| qotain | qo | Fire: transfer through one processing cycle | B Dict D2 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| ror | --- | *bare token: respond, set up, respond* | --- |

→ 7/9 recognized (77%).

**L13 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sor | so | Sequence: respond | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| chdy | ch | Test: check complete | B Dict D2 |
| ches | ch | Test: sequence steady | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| chcthy | ch | Test: observe material moving through apparatus **«cth»** | B Dict D2 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |

→ 10/10 recognized (100%).

**L14 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| soar | so | Sequence: bring to and note result | Comp-v2 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| chey | ch | Test: quick active check | B Dict D1 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |

→ 7/7 recognized (100%).


### P3 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 34 (8% of folio) |
| e-depth | 0.882 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | cthx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 8 (23%)
- ot: 7 (20%)
- ch: 6 (17%)
- so: 2 (5%)
- ok: 2 (5%)
- tch: 1 (2%)
- dch: 1 (2%)

---

## Paragraph 4: Lines 15-18 (37 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L15 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| poar | po | Pause: bring to and note result | Comp-v2 |
| alchor | al | Product settled: note what happened | Comp-v2 |
| octhy | --- | *unrecognized* (set up, adjust, transfer, watch, ) | --- |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| pchedy | pch | Setup: system steady, confirmed | Comp-v2 |
| opomdy | --- | *unrecognized* (set up, pause, set up, finalize, do, ) | --- |

→ 6/8 recognized (75%).

**L16 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| solol | so | Sequence: hold current state | Comp-v2 |
| shol | sh | Watch: hold -- passive monitoring, keep current state | B Dict D2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| qokeeey | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| qokedain | qo | Fire: one standard heat cycle | Comp-v2 |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| amchd | --- | *unrecognized* (bring to, finalize, adjust, watch, do) | --- |

→ 7/8 recognized (87%).

**L17 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qoeeean | qo | Fire: steady, steady, steady, bring to, bind | Comp-v2 |
| she | sh | Watch: steady | Comp-v2 |
| olkeear | ol | Steady: gentle steady heat — balneum level | Comp-v2 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| qor | qo | Fire: respond | Comp-v2 |
| cheo | ch | Test: steady, set up | Comp-v2 |
| ral | --- | *bare token: respond, bring to, hold* | --- |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| teey | te | Transfer step: steady | Comp-v2 |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |

→ 10/11 recognized (90%).

**L18 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| key | ke | Balneum: complete | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |
| dalchd | da | Load: hold, adjust, watch, do | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| okal | ok | Vessel: contents settling -- let them stabilize | B Dict D2 |
| chody | ch | Test: check the arrangement | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| cham | ch | Test: bring to, finalize | Comp-v2 |

→ 10/10 recognized (100%).


### P4 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 37 (9% of folio) |
| e-depth | 0.703 |
| dar count | 1 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 7 (18%)
- ch: 7 (18%)
- ot: 2 (5%)
- ok: 2 (5%)
- sh: 2 (5%)
- po: 1 (2%)
- al: 1 (2%)

---

## Paragraph 5: Lines 19-24 (53 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L19 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polchdy | po | Pause: hold, adjust, watch, do | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| otaly | ot | Output: bring to stable state | Comp-v2 |
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| sheky | sh | Watch: set — stop adjusting | Comp-v2 |
| qeey | --- | *unrecognized* (q, steady, steady, ) | --- |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| qoko | qo | Fire: heat, set up | Comp-v2 |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |

→ 9/10 recognized (90%).

**L20 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qoaiin | qo | Fire: extended iteration cycles | Comp-v2 |
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| keody | ke | Balneum: set up, do | Comp-v2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| keol | ke | Balneum: hold current state | Comp-v2 |
| okeeey | ok | Vessel: steady, steady, steady | Comp-v2 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| ody | --- | *bare token: set up, do, * | --- |

→ 10/11 recognized (90%).

**L21 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| solkeedy | so | Sequence: one gentle balneum cycle | Comp-v2 |
| raiin | --- | Respond through extended iteration cycles | B Dict D3 |
| chcthey | ch | Test: observe material moving | Comp-v2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| qeey | --- | *unrecognized* (q, steady, steady, ) | --- |
| rair | --- | *unrecognized* (respond, bring to, iterate, respond) | --- |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| sy | --- | *bare token: sequence, * | --- |

→ 6/9 recognized (66%).

**L22 (3 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| daichy | da | Load: iterate, adjust, watch | Comp-v2 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |
| qairal | --- | *unrecognized* (q, bring to, iterate, respond, bring to, hold) | --- |

→ 2/3 recognized (66%).

**L23 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qoain | qo | Fire: one processing cycle | Comp-v2 |
| qoiin | qo | Fire: iterate, iterate, bind | Comp-v2 |
| olcheedy | ol | Steady: adjust, watch, steady, steady, do | Comp-v2 |
| dairiy | da | Load: iterate, respond, iterate | Comp-v2 |
| teedy | te | Transfer step: system steady, confirmed | Comp-v2 |
| qopol | qo | Fire: hold current state | Comp-v2 |
| chdy | ch | Test: check complete | B Dict D2 |
| oteor | ot | Output: note what happened | Comp-v2 |
| octhdy | --- | *unrecognized* (set up, adjust, transfer, watch, do, ) | --- |
| otychey | ot | Output: adjust, watch, steady | Comp-v2 |

→ 9/10 recognized (90%).

**L24 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| cheeteey | ch | Test: gentle steady transfer | Comp-v2 |
| qoteeey | qo | Fire: gentle steady transfer | Comp-v2 |
| lkeey | lk | Check furnace: balneum level settling | B Dict D2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| key | ke | Balneum: complete | Comp-v2 |
| lkedy | lk | Check equipment: system steady, confirmed | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| lo | --- | *bare token: hold, set up* | --- |

→ 9/10 recognized (90%).


### P5 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 53 (13% of folio) |
| e-depth | 0.717 |
| dar count | 3 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 11 (20%)
- ot: 5 (9%)
- ch: 4 (7%)
- ke: 3 (5%)
- ok: 3 (5%)
- da: 3 (5%)
- lk: 2 (3%)

---

## Paragraph 6: Lines 25-25 (11 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L25 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tedain | te | Transfer step: one processing cycle | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| ochor | --- | *unrecognized* (set up, adjust, watch, set up, respond) | --- |
| okchd | ok | Vessel: adjust, watch, do | Comp-v2 |
| ykedy | yk | Adjust: system steady, confirmed | Comp-v2 |
| kedy | ke | Standard heat cycle complete | B Dict D2 |
| chor | ch | Test: note what happened | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| cheety | ch | Test: gentle steady transfer | Comp-v2 |
| chcthy | ch | Test: observe material moving through apparatus **«cth»** | B Dict D2 |
| okey | ok | Vessel: steady | Comp-v2 |

→ 10/11 recognized (90%).


### P6 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 11 (2% of folio) |
| e-depth | 0.455 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | cthx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 3 (27%)
- ok: 2 (18%)
- te: 1 (9%)
- sh: 1 (9%)
- yk: 1 (9%)
- ke: 1 (9%)

---

## Paragraph 7: Lines 26-26 (3 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L26 (3 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tockhy | to | Note transfer: temperature check | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| chedam | ch | Test: steady, do, bring to, finalize | Comp-v2 |

→ 3/3 recognized (100%).


### P7 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 3 (0% of folio) |
| e-depth | 0.667 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 2 (66%)
- to: 1 (33%)

---

## Paragraph 8: Lines 27-29 (27 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L27 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pcholkeedy | pch | Setup: one gentle balneum cycle | Comp-v2 |
| okchoiiin | ok | Vessel: adjust, watch, set up, iterate, iterate, iterate, bind | Comp-v2 |
| aky | --- | *bare token: bring to, heat, * | --- |
| opchedy | --- | Operate: run the active check procedure | B Dict D2 |
| kolfchdy | ko | Heat: hold, flag, adjust, watch, do | Comp-v2 |
| opchedy | --- | Operate: run the active check procedure | B Dict D2 |
| lky | lk | Check equipment: complete | Comp-v2 |
| shty | sh | Watch: transfer | Comp-v2 |

→ 7/8 recognized (87%).

**L28 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ysheedy | sh | Watch: system steady, confirmed | Comp-v2 |
| sheokeedy | sh | Watch: one gentle balneum cycle | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| ytchedy | tch | Transfer-check: system steady, confirmed | Comp-v2 |
| sharam | sh | Watch: bring to and note result | Comp-v2 |

→ 8/8 recognized (100%).

**L29 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sar | sa | Scaffold: note the position and respond | B Dict D3 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| olshedy | ol | Steady: watch sequence steady | Comp-v2 |
| chokeey | ch | Test: gentle steady heat — balneum level | Comp-v2 |
| sal | sa | Scaffold: hold | Comp-v2 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| olor | ol | Steady: note what happened | Comp-v2 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| chealy | ch | Test: bring to stable state | Comp-v2 |

→ 11/11 recognized (100%).


### P8 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 27 (6% of folio) |
| e-depth | 0.778 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ckhx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- sh: 4 (14%)
- qo: 3 (11%)
- ch: 3 (11%)
- ok: 2 (7%)
- ot: 2 (7%)
- sa: 2 (7%)
- ol: 2 (7%)

---

## Paragraph 9: Lines 30-30 (9 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L30 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tar | ta | Transfer and note the yield | B Dict D3 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| cheokey | ch | Test: gentle steady heat — balneum level | Comp-v2 |
| okeody | ok | Vessel: system steady, confirmed | Comp-v2 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| cheom | ch | Test: steady, set up, finalize | Comp-v2 |

→ 9/9 recognized (100%).


### P9 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 9 (2% of folio) |
| e-depth | 0.556 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 4 (44%)
- ta: 1 (11%)
- ok: 1 (11%)
- qo: 1 (11%)

---

## Paragraph 10: Lines 31-33 (30 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L31 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| poir | po | Pause: iterate, respond | Comp-v2 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| keolor | ke | Balneum: hold current state | Comp-v2 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |
| okeeor | ok | Vessel: note what happened | Comp-v2 |
| oteor | ot | Output: note what happened | Comp-v2 |
| karainy | ka | Heat: one processing cycle | Comp-v2 |

→ 10/10 recognized (100%).

**L32 (13 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sor | so | Sequence: respond | Comp-v2 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| s | --- | Sequence marker -- positional step indicator | B Dict D3 |
| alkeear | al | Product settled: gentle steady heat — balneum level | Comp-v2 |
| alshedy | al | Product settled: watch sequence steady | Comp-v2 |
| okeechy | ok | Vessel: steady, steady, adjust, watch | Comp-v2 |
| qoiiin | qo | Fire: iterate, iterate, iterate, bind | Comp-v2 |
| oteey | ot | Output: confirm gentle steady flow at receiver | B Dict D2 |
| ched | ch | Test: steady, do | Comp-v2 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| am | --- | This phase is done -- yield the result and close | B Dict D0 |

→ 13/13 recognized (100%).

**L33 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sarol | sa | Scaffold: hold current state | Comp-v2 |
| okcheey | ok | Vessel: adjust, watch, steady, steady | Comp-v2 |
| cphedy | --- | *unrecognized* (adjust, pause, watch, steady, do, ) | --- |
| shckhhy | sh | Watch: temperature check with extended observation | Comp-v2 |
| okeeor | ok | Vessel: note what happened | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| shdal | sh | Watch: bring to stable state | Comp-v2 |

→ 6/7 recognized (85%).


### P10 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 30 (7% of folio) |
| e-depth | 0.667 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ckhhx1 |
| hh (extended obs) | 1 |

**Top prefixes:**
- ok: 5 (16%)
- ot: 4 (13%)
- al: 2 (6%)
- ch: 2 (6%)
- sh: 2 (6%)
- po: 1 (3%)
- ke: 1 (3%)

---

## Paragraph 11: Lines 34-36 (26 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L34 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pairar | --- | *unrecognized* (pause, bring to, iterate, respond, bring to, respond) | --- |
| lshdar | lsh | Watch equipment: bring to and note result | Comp-v2 |
| okechedy | ok | Vessel: steady, adjust, watch, steady, do | Comp-v2 |
| qokar | qo | Fire: apply heat and note the response | B Dict D1 |
| aram | ar | Note the yield: bring to, finalize | Comp-v2 |
| qotedy | qo | Fire: execute a heat-driven transfer operation | B Dict D1 |
| araiin | ar | Note the yield: extended iteration cycles | Comp-v2 |
| qokchdy | qo | Fire: heat with active test adjustment, cycle close | B Dict D2 |
| opary | --- | *unrecognized* (set up, pause, bring to, respond, ) | --- |

→ 7/9 recognized (77%).

**L35 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| olaiin | ol | Steady: extended iteration cycles | Comp-v2 |
| qopchdy | qo | Fire: pause, adjust, watch, do | Comp-v2 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| okeal | ok | Vessel: bring to stable state | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |

→ 11/11 recognized (100%).

**L36 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |
| olchain | ol | Steady: one processing cycle | Comp-v2 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| olam | ol | Steady: bring to, finalize | Comp-v2 |

→ 6/6 recognized (100%).


### P11 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 26 (6% of folio) |
| e-depth | 0.462 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ok: 5 (19%)
- qo: 5 (19%)
- ol: 3 (11%)
- ar: 2 (7%)
- sa: 2 (7%)
- ch: 2 (7%)
- lsh: 1 (3%)

---

## Paragraph 12: Lines 37-38 (19 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L37 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| pom | po | Pause: finalize | Comp-v2 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| olkedy | ol | Steady: one standard heat cycle | Comp-v2 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| keedas | ke | Balneum: sequence steady | Comp-v2 |
| otear | ot | Output: bring to and note result | Comp-v2 |
| shkeor | sh | Watch: note what happened | Comp-v2 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |

→ 10/10 recognized (100%).

**L38 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sar | sa | Scaffold: note the position and respond | B Dict D3 |
| ain | --- | Bring to a binding cycle -- one pass | B Dict D2 |
| olkeear | ol | Steady: gentle steady heat — balneum level | Comp-v2 |
| okeody | ok | Vessel: system steady, confirmed | Comp-v2 |
| qokeeiin | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| okal | ok | Vessel: contents settling -- let them stabilize | B Dict D2 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |

→ 9/9 recognized (100%).


### P12 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 19 (4% of folio) |
| e-depth | 0.947 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ok: 7 (36%)
- qo: 3 (15%)
- ol: 2 (10%)
- ot: 2 (10%)
- po: 1 (5%)
- ke: 1 (5%)
- sh: 1 (5%)
- sa: 1 (5%)

---

## Paragraph 13: Lines 39-41 (28 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L39 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| palkeedy | al | Product settled: one gentle balneum cycle | Comp-v2 |
| qopal | qo | Fire: bring to stable state | Comp-v2 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| opal | --- | *unrecognized* (set up, pause, bring to, hold) | --- |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| okaiiin | ok | Vessel: extended iteration cycles | Comp-v2 |
| sheody | sh | Watch: system steady, confirmed | Comp-v2 |
| yteokar | te | Transfer step: heat and note response | Comp-v2 |
| ogom | --- | *unrecognized* (set up, g, set up, finalize) | --- |

→ 7/9 recognized (77%).

**L40 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sain | sa | Scaffold: begin a binding iteration cycle | B Dict D1 |
| okal | ok | Vessel: contents settling -- let them stabilize | B Dict D2 |
| lkeedy | lk | Check furnace: gentle balneum level holds | B Dict D2 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| okchedy | ok | Vessel: adjust, watch, steady, do | Comp-v2 |
| qokal | qo | Fire: heat until the yield stabilizes | B Dict D1 |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| chkey | ch | Test: set — stop adjusting | Comp-v2 |
| oto | ot | Output: set up | Comp-v2 |
| aral | ar | Note the yield: bring to stable state | Comp-v2 |

→ 10/10 recognized (100%).

**L41 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| yshesy | sh | Watch: sequence steady | Comp-v2 |
| alain | al | Product settled: one processing cycle | Comp-v2 |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| okchey | ok | Vessel: adjust, watch, steady | Comp-v2 |
| qokchy | qo | Fire: heat with active monitoring | Comp-v2 |
| okchaiin | ok | Vessel: extended iteration cycles | Comp-v2 |
| okeeos | ok | Vessel: sequence steady | Comp-v2 |
| okchy | ok | Vessel: adjust, watch | Comp-v2 |
| ory | or | Note what happened: complete | Comp-v2 |

→ 9/9 recognized (100%).


### P13 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 28 (7% of folio) |
| e-depth | 0.536 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ok: 8 (28%)
- qo: 3 (10%)
- al: 2 (7%)
- ot: 2 (7%)
- sh: 2 (7%)
- ch: 2 (7%)
- te: 1 (3%)

---

## Paragraph 14: Lines 42-45 (39 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L42 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polar | po | Pause: bring to and note result | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| y | --- | Done -- bare completion marker | B Dict D2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qotal | qo | Fire: transfer until output stabilizes | B Dict D2 |
| chody | ch | Test: check the arrangement | B Dict D2 |
| oteody | ot | Output: system steady, confirmed | Comp-v2 |
| oraryteop | or | Note what happened: transfer and note result | Comp-v2 |

→ 9/9 recognized (100%).

**L43 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| yteeo | te | Transfer step: steady, set up | Comp-v2 |
| raiin | --- | Respond through extended iteration cycles | B Dict D3 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| opor | --- | *unrecognized* (set up, pause, set up, respond) | --- |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| ycheedy | ch | Test: system steady, confirmed | Comp-v2 |
| qeedar | --- | *unrecognized* (q, steady, steady, do, bring to, respond) | --- |
| yteeey | te | Transfer step: steady, steady | Comp-v2 |
| sheor | sh | Watch: note what happened | Comp-v2 |
| oteeg | ot | Output: steady, steady | Comp-v2 |

→ 8/10 recognized (80%).

**L44 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sar | sa | Scaffold: note the position and respond | B Dict D3 |
| ain | --- | Bring to a binding cycle -- one pass | B Dict D2 |
| qokaekeeey | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| yk | --- | *bare token: , heat* | --- |
| okaeechey | ok | Vessel: bring to, steady, steady, adjust, watch, steady | Comp-v2 |
| okeeedy | ok | Vessel: steady, steady, steady, do | Comp-v2 |
| alair | al | Product settled: bring to and note result | Comp-v2 |
| okcheey | ok | Vessel: adjust, watch, steady, steady | Comp-v2 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| arody | ar | Note the yield: set up, do | Comp-v2 |

→ 9/10 recognized (90%).

**L45 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| yar | --- | *bare token: , bring to, respond* | --- |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| okeeey | ok | Vessel: steady, steady, steady | Comp-v2 |
| teey | te | Transfer step: steady | Comp-v2 |
| shkar | sh | Watch: heat and note response | Comp-v2 |
| oteeedy | ot | Output: steady, steady, steady, do | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| okary | ok | Vessel: bring to and note result | Comp-v2 |
| yky | yk | Adjust: complete | Comp-v2 |

→ 9/10 recognized (90%).



### P14 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 39 (9% of folio) |
| e-depth | 0.923 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ok: 8 (20%)
- qo: 4 (10%)
- sh: 3 (7%)
- ot: 3 (7%)
- te: 3 (7%)
- ch: 2 (5%)
- po: 1 (2%)

---

## Cross-Paragraph Patterns

### e-depth Thermal Arc

| Para | Lines | Tokens | e-depth | Recipe phase |
|------|-------|--------|---------|-------------|
| P1 | 1-6 | 48 | 0.604 | Initial ash distillation |
| P2 | 7-10 | 30 | 0.767 | Balneum distillation (×3 cycle) |
| P3 | 11-14 | 34 | 0.882 | Continued balneum — peak gentle heat |
| P4 | 15-18 | 37 | 0.703 | Ash distillation (extract fire from earth) |
| P5 | 19-24 | 53 | 0.717 | Balneum to strip fire |
| P6 | 25 | 11 | 0.455 | Warning phase — "don't let earth redden" |
| P7 | 26 | 3 | 0.667 | Micro-gate |
| P8 | 27-29 | 27 | 0.778 | Heightened observation |
| P9 | 30 | 9 | 0.556 | Brief transition |
| P10 | 31-33 | 30 | 0.667 | Iterative reiteration |
| P11 | 34-36 | 26 | 0.462 | Dry fire extraction |
| P12 | 37-38 | 19 | 0.947 | Return to balneum |
| P13 | 39-41 | 28 | 0.536 | Continued processing |
| P14 | 42-45 | 39 | **0.923** | **Endpoint — should be calcination (low e-depth) but reads as balneum** |

The e-depth oscillates broadly (0.45-0.95) consistent with alternating balneum/ash distillation regimes. P6 (0.455) marks the warning phase — the lowest e-depth in the first half, consistent with the "beware" instruction requiring careful low-heat monitoring.

**Critical discordance:** P14 (0.923) should encode calcination ("wash by calcination until red as fire"). Calcination predicts near-zero e-depth (direct fire, no cooling stabilization). Instead P14 has the second-highest e-depth on the folio. This is the primary reason the match is PARTIALLY COHERENT rather than COHERENT.

### dar Distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 0 | 0% | Initial distillation |
| P2 | 3 | 43% | Earth-return in cohobation (3 dar ≈ 3 cycles) |
| P3-P4 | 2 | 29% | Continued extraction |
| P5 | 2 | 29% | Fire stripping |
| P6-P14 | 0 | 0% | Process management (no additions) |

All 7 dar concentrate in P2-P5 (extraction phases). P6-P14 (9 paragraphs, 237 tokens) have zero dar — consistent with a recipe that transitions from material handling (cohobation returns) to autonomous processing (reiteration until depleted, then washing).

### Observation MIDDLE Distribution

| Para | ckh | cth | ckhh | Total | Recipe activity |
|------|-----|-----|------|-------|-----------------|
| P2 | — | 1 | — | 1 | Transfer-watch during cohobation |
| P6 | 1 | — | — | 1 | Temperature check at warning phase |
| P8 | — | 1 | — | 1 | Transfer-watch during heightened observation |
| P10 | — | — | 1 | 1 | Extended temperature check (doubled h) during reiteration |

4 observation MIDDLEs at 4 structurally distinct positions. The ckhh (doubled-h extended observation) in P10 marks the most critical monitoring moment — the iterative reiteration where the operator must watch the earth's state without letting it redden.

---

## Verdict: PARTIALLY COHERENT

f112r produces a partially coherent structural reading against III.11.0 (red mercury tincture via cohobation). The match operates at the level of "compatible Section S distillation folio" rather than "this specific recipe encodes this specific folio."

**What works:**
1. **e-depth oscillation** tracks alternating balneum/ash distillation regimes
2. **dar concentration in P2-P5** with zero in P6-P14 matches extraction → autonomous processing transition
3. **14 paragraphs with micro-gates** encodes the recipe's multi-phase iterative structure
4. **Observation MIDDLEs** at 4 highest-risk moments

**What fails:**
1. **P14 e-depth = 0.923** contradicts calcination endpoint — the recipe's closing instruction ("wash by calcination until red as fire") predicts near-zero e-depth. This is the single strongest negative signal.
2. **No ×3 counting anchor** for the recipe's explicit "three times" balneum cycle.
3. **dar front-loading** — while consistent with the recipe's structure, the low total (7 dar) means less material-handling evidence to anchor the reading.
