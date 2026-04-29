# Validated Reading: f76v ↔ III.15.0 Ferment Conversion (Liquefaction → Multiplication)

**Match tier:** Strong-supported
**Expert verdict:** Coherent (5/7 structural predictions confirmed)
**Full token listing:** `data/f76v_cold_read.txt` (400 tokens, 41 lines)

---

## How to Read This Document

This recipe is 86 words. This folio is 400 tokens — a 4.7:1 ratio. The recipe describes converting a tincture ferment into a liquefied, fusible form through progressive fixation, then multiplying it infinitely. The key operation is fixation: binding materials under increasing heat until the product melts like wax without smoke.

The folio's e-depth tracks this precisely: descending from 1.01 (P1, gentle initial fixation) through 0.67 (P4, intense fixation) to 0.60 (P6, strongest heat for infinite multiplication). This monotonic descent encodes progressive heat strengthening — each phase requires more fire than the last.

**What makes this match credible:**
- **Descending e-depth** (1.01 → 0.60): monotonic across 6 paragraphs, encoding progressive fixation
- **chekar concentration in P5** (9.5% density): fusibility test tokens cluster at exactly the paragraph where the recipe says "veies que's fona com a cera" (see it melt like wax)
- **sa-prefix concentration in P6** (8 tokens): scaffold/iterate tokens for "in infinit se pot multiplicar"
- **n-atom pervasiveness** (~50+ tokens): bind/contain atoms throughout — fixation is fundamentally binding
- **Zero dar in P5** (the test paragraph): you don't add material during a quality test

**Honest gaps:** No cs gold markers despite gold being added (H = gold in Part III cipher). dar=10 rather than the predicted low/zero — the recipe involves more material handling than the brief text suggests.

Every token on every line appears in this document.

---

## The Recipe

### Catalan (III.15.0, SISMEL — Part III cipher: H = gold)

> Quant tu hauràs fet lo ferment de tinctura, aquell convertiràs en liquefacció, ajustant-li H segon lo pes que saps, e lo seny te demonstrarà per la obra de natura, en tro sia tot fix dedins lo condensori. E après tu metràs y la cuinqua littera; aquella fixaràs tro veies que's fona com a cera, sens fer fum; e a tant serrà fet lo ferment liquefet de la primera cambra. E aquest in infinit se pot multiplicar per les obres secrets fetes de mixtió en diversa manera.

### English

When you have made the tincture ferment, convert it to liquefaction by adding gold (H) according to the weight you know — your senses will demonstrate through nature's work — until all is fixed in the condenser. Then add the fifth letter; fix it until you see it melt like wax without smoke. Then the liquefied ferment of the first chamber is made. This can be multiplied infinitely by secret mixing operations in diverse manner.

### Recipe Structure

| Step | Operation | Heat | Key feature |
|------|-----------|------|-------------|
| 1 | Start with tincture ferment | — | precursor ready |
| 2 | Add gold (H) by weight | moderate | fixation begins |
| 3 | Fix in condenser until done | increasing | progressive binding |
| 4 | Add fifth letter | — | second material |
| 5 | Fix until melts like wax without smoke | strong | **fusibility test** |
| 6 | Result: liquefied ferment | — | first chamber done |
| 7 | Multiply infinitely | strongest | secret mixing |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | Low/zero dar | recipe uses "ajustant" (joining), not "gita" (casting) | **FAIL** — dar=10 (recipe has more handling than text suggests) |
| 2 | High n-atom (bind) count | "fix", "ligat" — fixation = binding | **MATCH** — ~50+ n-terminal tokens |
| 3 | Fusibility test: chekar in P5 | "veies que's fona com a cera" | **MATCH** — chekar×2 in P5 (9.5% density) |
| 4 | Descending e-depth (increasing heat) | fixation requires progressive strengthening | **MATCH** — 1.01 → 0.60 monotonic |
| 5 | cs gold markers (gold added as H) | recipe explicitly adds gold | **FAIL** — no cs detected |
| 6 | sa-prefix for multiplication | "in infinit se pot multiplicar" | **MATCH** — 8 sa-prefix in P6 |
| 7 | 6 paragraphs fits structure | prep, fix, fix-more, test, multiply | **MATCH** — coherent mapping |

**Score: 5/7 confirmed, 2 failures**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 400 |
| Lines | 41 |
| Paragraphs | 6 |
| dar (material-add) | 10 |
| Quality checks (chek/shek class) | 4 |
| Observation MIDDLEs | ecth×2, ecthe×1, ckh×1 |
| hh (extended observation) | 0 |

---

## Paragraph 1: Lines 1-14 (144 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L1 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polarar | po | Pause: bring to and note result | Comp-v2 |
| okor | ok | Vessel: note what happened | Comp-v2 |
| opcheey | --- | *unrecognized* (set up, pause, adjust, watch, steady, steady, ) | --- |
| yteey | te | Transfer step: steady | Comp-v2 |
| opchaly | --- | *unrecognized* (set up, pause, adjust, watch, bring to, hold, ) | --- |
| lshedy | lsh | Watch equipment: confirm apparatus is steady | B Dict D2 |
| qofchdal | qo | Fire: bring to stable state | Comp-v2 |
| lkodol | lk | Check equipment: hold current state | Comp-v2 |
| opa | --- | *bare token: set up, pause, bring to* | --- |
| korols | ko | Heat: hold current state | Comp-v2 |

→ 7/10 recognized (70%).

**L2 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| scsedy | --- | *unrecognized* (sequence, adjust, sequence, steady, do, ) | --- |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| cholkeeey | ch | Test: gentle steady heat — balneum level | Comp-v2 |
| otedor | ot | Output: note what happened | Comp-v2 |
| okor | ok | Vessel: note what happened | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| oly | ol | Steady: current state confirmed | B Dict D2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qoyky | qo | Fire: set — stop adjusting | Comp-v2 |

→ 10/11 recognized (90%).

**L3 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dchedy | dch | Setup-check: system steady, confirmed | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| chedaiin | ch | Test: extended iteration cycles | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| olkedy | ol | Steady: one standard heat cycle | Comp-v2 |
| ror | --- | *bare token: respond, set up, respond* | --- |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| okal | ok | Vessel: contents settling -- let them stabilize | B Dict D2 |

→ 9/10 recognized (90%).

**L4 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| solkeey | so | Sequence: gentle steady heat — balneum level | Comp-v2 |
| sor | so | Sequence: respond | Comp-v2 |
| shecthy | sh | Watch: cooled-transfer-watch **«ecth»** | Comp-v2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| okar | ok | Vessel: note how the contents respond | B Dict D3 |
| chpchedy | ch | Test: pause, adjust, watch, steady, do | Comp-v2 |
| cpchy | --- | *unrecognized* (adjust, pause, adjust, watch, ) | --- |
| oty | ot | Output: transfer complete -- drip/flow has ceased | B Dict D2 |
| olor | ol | Steady: note what happened | Comp-v2 |
| otchy | ot | Output: adjust, watch | Comp-v2 |
| ralchl | al | Product settled: adjust, watch, hold | Comp-v2 |

→ 10/11 recognized (90%).

**L5 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| s | --- | Sequence marker -- positional step indicator | B Dict D3 |
| otain | ot | Output: monitor drip rate through one processing cycle | B Dict D2 |
| okain | ok | Vessel: seal for a processing cycle | B Dict D1 |
| chcthedy | ch | Test: observe material moving | Comp-v2 |
| qoteed | qo | Fire: gentle steady transfer | Comp-v2 |
| ykedy | yk | Adjust: system steady, confirmed | Comp-v2 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| teyteg | te | Transfer step: transfer, steady | Comp-v2 |

→ 10/10 recognized (100%).

**L6 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qotees | qo | Fire: gentle steady transfer | Comp-v2 |
| olkeey | ol | Steady: hold gentle heat -- balneum level steady | B Dict D2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qoeeedy | qo | Fire: steady, steady, steady, do | Comp-v2 |
| chckhey | ch | Test: temperature check | Comp-v2 |
| sheor | sh | Watch: note what happened | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |

→ 10/10 recognized (100%).

**L7 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| doteey | do | Execute: gentle steady transfer | Comp-v2 |
| qo | --- | *bare token: q, set up* | --- |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| cheolchdy | ch | Test: holding, confirmed | Comp-v2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| okedar | ok | Vessel: bring to and note result | Comp-v2 |
| da | --- | *bare token: do, bring to* | --- |

→ 9/11 recognized (81%).

**L8 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| ochedy | --- | *unrecognized* (set up, adjust, watch, steady, do, ) | --- |
| roiin | --- | *unrecognized* (respond, set up, iterate, iterate, bind) | --- |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| olor | ol | Steady: note what happened | Comp-v2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| qolkeeey | qo | Fire: gentle steady heat — balneum level | Comp-v2 |
| r | --- | Respond -- route to next action | B Dict D3 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |

→ 9/11 recognized (81%).

**L9 (7 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sheor | sh | Watch: note what happened | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |
| ral | --- | *bare token: respond, bring to, hold* | --- |
| cheey | ch | Test: verify gentle steady state -- confirm balneum holds | B Dict D2 |
| r | --- | Respond -- route to next action | B Dict D3 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |

→ 6/7 recognized (85%).

**L10 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| cphdor | --- | *unrecognized* (adjust, pause, watch, do, set up, respond) | --- |
| shedal | sh | Watch: bring to stable state | Comp-v2 |
| qopchdy | qo | Fire: pause, adjust, watch, do | Comp-v2 |
| dshedy | sh | Watch: system steady, confirmed | Comp-v2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| tchedy | tch | Transfer-check: system steady, confirmed | Comp-v2 |
| lsheetal | lsh | Watch equipment: gentle steady transfer | Comp-v2 |
| shecphy | sh | Watch: steady, adjust, pause, watch | Comp-v2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| dy | --- | Cycle close -- this action is complete | B Dict D1 |

→ 9/10 recognized (90%).

**L11 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| cheor | ch | Test: note what happened | Comp-v2 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| oekeedy | --- | *unrecognized* (set up, steady, heat, steady, steady, do, ) | --- |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| oteedy | ot | Output: gentle steady state at receiver, confirmed | B Dict D2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| shedam | sh | Watch: steady, do, bring to, finalize | Comp-v2 |

→ 9/10 recognized (90%).

**L12 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| sheol | sh | Watch: observe and hold -- passive monitoring, maintain state | B Dict D2 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| lteedy | te | Transfer step: system steady, confirmed | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qotal | qo | Fire: transfer until output stabilizes | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| checthy | ch | Test: cooled-transfer-watch **«ecth»** | Comp-v2 |
| otedeey | ot | Output: steady, do, steady, steady | Comp-v2 |
| qokol | qo | Fire: heat and hold -- maintain current heat level | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| deey | de | steady | Comp-v2 |

→ 12/12 recognized (100%).

**L13 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| okeeedy | ok | Vessel: steady, steady, steady, do | Comp-v2 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qotedy | qo | Fire: execute a heat-driven transfer operation | B Dict D1 |
| oleeedy | ol | Steady: steady, steady, steady, do | Comp-v2 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| lo | --- | *bare token: hold, set up* | --- |

→ 10/11 recognized (90%).

**L14 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| cthedy | ct | system steady, confirmed | Comp-v2 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |
| shcthedy | sh | Watch: observe material moving | Comp-v2 |
| qoeekeedy | qo | Fire: one gentle balneum cycle | Comp-v2 |
| deedy | de | system steady, confirmed | Comp-v2 |

→ 10/10 recognized (100%).


### P1 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 144 (36% of folio) |
| e-depth | 1.007 |
| dar count | 3 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ecthx2 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 27 (18%)
- ch: 19 (13%)
- sh: 18 (12%)
- ot: 15 (10%)
- ok: 13 (9%)
- ol: 6 (4%)
- te: 3 (2%)

---

## Paragraph 2: Lines 15-15 (5 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L15 (5 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tchedy | tch | Transfer-check: system steady, confirmed | Comp-v2 |
| lsheedy | lsh | Watch equipment: system steady, confirmed | Comp-v2 |
| chedal | ch | Test: bring to stable state | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| checthey | ch | Test: cooled-transfer-watch **«ecth»** | Comp-v2 |

→ 5/5 recognized (100%).


### P2 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 5 (1% of folio) |
| e-depth | 1.200 |
| dar count | 0 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ecthex1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 3 (60%)
- tch: 1 (20%)
- lsh: 1 (20%)

---

## Paragraph 3: Lines 16-24 (86 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L16 (8 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| polshdal | po | Pause: bring to stable state | Comp-v2 |
| otedair | ot | Output: bring to and note result | Comp-v2 |
| opshedal | --- | *unrecognized* (set up, pause, sequence, watch, steady, do, bring to, hold) | --- |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| pschedal | sch | Quick check: bring to stable state | Comp-v2 |
| tsheokeedy | sh | Watch: one gentle balneum cycle | Comp-v2 |
| oshepols | --- | *unrecognized* (set up, sequence, watch, steady, pause, set up, hold, sequence) | --- |

→ 6/8 recognized (75%).

**L17 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sar | sa | Scaffold: note the position and respond | B Dict D3 |
| olkeey | ol | Steady: hold gentle heat -- balneum level steady | B Dict D2 |
| shokaiin | sh | Watch: sustained deep heating cycles | Comp-v2 |
| sheolol | sh | Watch: hold current state | Comp-v2 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| qekchdy | --- | *unrecognized* (q, steady, heat, adjust, watch, do, ) | --- |
| qoeeedy | qo | Fire: steady, steady, steady, do | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| lkedy | lk | Check equipment: system steady, confirmed | Comp-v2 |
| chdy | ch | Test: check complete | B Dict D2 |

→ 9/10 recognized (90%).

**L18 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| lshey | lsh | Watch equipment: steady | Comp-v2 |
| qockhedy | qo | Fire: temperature check | Comp-v2 |
| qodeey | qo | Fire: system steady, confirmed | Comp-v2 |
| qolkeedy | qo | Fire: one gentle balneum cycle | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| chol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| chedchey | ch | Test: steady, do, adjust, watch, steady | Comp-v2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| olkedy | ol | Steady: one standard heat cycle | Comp-v2 |

→ 9/9 recognized (100%).

**L19 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| or | --- | Note what happened -- acknowledge and route to next action | B Dict D0 |
| ar | --- | Note the yield -- observe what was produced | B Dict D1 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| otar | ot | Output: monitor the drip rate and note the result | B Dict D3 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| otchedy | ot | Output: adjust, watch, steady, do | Comp-v2 |
| checkhey | ch | Test: temperature check (gentle level) | Comp-v2 |
| olchedy | ol | Steady: adjust, watch, steady, do | Comp-v2 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |
| sheckhy | sh | Watch: temperature check | Comp-v2 |
| lky | lk | Check equipment: complete | Comp-v2 |

→ 11/11 recognized (100%).

**L20 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dol | do | Load: place material and hold -- position substance, keep it there | B Dict D2 |
| sheetey | sh | Watch: gentle steady transfer | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |
| lshedy | lsh | Watch equipment: confirm apparatus is steady | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| shl | sh | Watch: hold | Comp-v2 |
| loiiim | --- | *unrecognized* (hold, set up, iterate, iterate, iterate, finalize) | --- |

→ 10/11 recognized (90%).

**L21 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| cthedy | ct | system steady, confirmed | Comp-v2 |
| oteol | ot | Output: hold current state | Comp-v2 |
| chdar | ch | Test: bring to and note result | Comp-v2 |
| chckhy | ch | Test: observe temperature directly **«ckh»** | B Dict D2 |
| chees | ch | Test: sequence steady | Comp-v2 |
| salkeedy | sa | Scaffold: one gentle balneum cycle | Comp-v2 |
| chey | ch | Test: quick active check | B Dict D1 |
| lcheedy | lch | Check equipment: system steady, confirmed | Comp-v2 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |
| qoteedy | qo | Fire: transfer under gentle steady heat, confirmed | B Dict D2 |

→ 10/10 recognized (100%).

**L22 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| qotedy | qo | Fire: execute a heat-driven transfer operation | B Dict D1 |
| chey | ch | Test: quick active check | B Dict D1 |
| dytey | --- | *unrecognized* (do, , transfer, steady, ) | --- |
| teedy | te | Transfer step: system steady, confirmed | Comp-v2 |
| lchey | lch | Check equipment: quick apparatus check | B Dict D2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| lal | --- | *bare token: hold, bring to, hold* | --- |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |

→ 10/12 recognized (83%).

**L23 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dchedy | dch | Setup-check: system steady, confirmed | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qoteey | qo | Fire: gentle steady transfer | Comp-v2 |
| qokol | qo | Fire: heat and hold -- maintain current heat level | B Dict D2 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| olchedr | ol | Steady: adjust, watch, steady, do, respond | Comp-v2 |
| shetey | sh | Watch: gentle steady transfer | Comp-v2 |
| raiin | --- | Respond through extended iteration cycles | B Dict D3 |

→ 10/10 recognized (100%).

**L24 (5 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| lsheey | lsh | Watch equipment: steady, steady | Comp-v2 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |
| olshey | ol | Steady: watch sequence steady | Comp-v2 |

→ 5/5 recognized (100%).


### P3 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 86 (21% of folio) |
| e-depth | 0.977 |
| dar count | 2 |
| Quality checks (chek/shek) | 0 |
| Observation MIDDLEs | ckhx1 |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 17 (19%)
- ch: 15 (17%)
- sh: 13 (15%)
- ot: 5 (5%)
- ol: 5 (5%)
- lch: 5 (5%)
- lsh: 3 (3%)

---

## Paragraph 4: Lines 25-29 (52 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L25 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| psheoldy | sh | Watch: holding, confirmed | Comp-v2 |
| opalshedy | --- | *unrecognized* (set up, pause, bring to, hold, sequence, watch, steady, do, ) | --- |
| qokshedy | qo | Fire: one standard heat cycle | Comp-v2 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| dor | do | Execute: respond | Comp-v2 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| opchedy | --- | Operate: run the active check procedure | B Dict D2 |
| dal | da | Place material carefully -- gentle/measured transfer or output | B Dict D0 |
| ro | --- | *bare token: respond, set up* | --- |
| fcham | fch | Mercury marker (C1939): bring to, finalize | Comp-v2 |

→ 8/10 recognized (80%).

**L26 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| dshol | sh | Watch: hold current state | Comp-v2 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| ches | ch | Test: sequence steady | Comp-v2 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| checkhy | ch | Test: heat-level check with close observation | B Dict D2 |
| oteoldy | ot | Output: holding, confirmed | Comp-v2 |
| qokeey | qo | Fire: gentle steady heat holding | B Dict D1 |
| chckhyd | ch | Test: temperature check | Comp-v2 |
| lar | --- | *bare token: hold, bring to, respond* | --- |
| aly | al | Product settled: complete | Comp-v2 |

→ 9/10 recognized (90%).

**L27 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| shckhey | sh | Watch: temperature check | Comp-v2 |
| chckhey | ch | Test: temperature check | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| chek | ch | Test: steady, heat | Comp-v2 |
| ain | --- | Bring to a binding cycle -- one pass | B Dict D2 |
| r | --- | Respond -- route to next action | B Dict D3 |
| ain | --- | Bring to a binding cycle -- one pass | B Dict D2 |
| o | --- | *bare token: set up* | --- |
| kan | ka | Heat: bind | Comp-v2 |
| chlaiiin | ch | Test: extended iteration cycles | Comp-v2 |

→ 11/12 recognized (91%).

**L28 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| sheckhy | sh | Watch: temperature check | Comp-v2 |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| chey | ch | Test: quick active check | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| sair | sa | Scaffold: iterate, respond | Comp-v2 |
| sheckhy | sh | Watch: temperature check | Comp-v2 |
| lkeedy | lk | Check furnace: gentle balneum level holds | B Dict D2 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |

→ 9/9 recognized (100%).

**L29 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sar | sa | Scaffold: note the position and respond | B Dict D3 |
| sheedy | sh | Watch: gentle process through to completion | B Dict D2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| qolkey | qo | Fire: hold, heat, steady | Comp-v2 |
| lchdy | lch | Check equipment: cycle close | Comp-v2 |
| scheer | sch | Quick check: steady, steady, respond | Comp-v2 |
| shees | sh | Watch: sequence steady | Comp-v2 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| ches | ch | Test: sequence steady | Comp-v2 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| alaldy | al | Product settled: bring to stable state | Comp-v2 |

→ 11/11 recognized (100%).


### P4 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 52 (13% of folio) |
| e-depth | 0.673 |
| dar count | 3 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- ch: 9 (17%)
- sh: 8 (15%)
- qo: 8 (15%)
- sa: 4 (7%)
- da: 3 (5%)
- al: 2 (3%)
- lch: 2 (3%)

---

## Paragraph 5: Lines 30-31 (21 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L30 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tchedy | tch | Transfer-check: system steady, confirmed | Comp-v2 |
| lshees | lsh | Watch equipment: sequence steady | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| chees | ch | Test: sequence steady | Comp-v2 |
| tchy | tch | Transfer-check: complete | Comp-v2 |
| rshed | sh | Watch: steady, do | Comp-v2 |
| chkaiin | ch | Test: sustained deep heating cycles | Comp-v2 |
| sheky | sh | Watch: set — stop adjusting | Comp-v2 |
| shtal | sh | Watch: bring to stable state | Comp-v2 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| lsan | sa | Scaffold: bind | Comp-v2 |

→ 11/11 recognized (100%).

**L31 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sair | sa | Scaffold: iterate, respond | Comp-v2 |
| shekaiiin | sh | Watch: sustained deep heating cycles | Comp-v2 |
| shets | sh | Watch: sequence steady | Comp-v2 |
| aiiin | --- | *unrecognized* (bring to, iterate, iterate, iterate, bind) | --- |
| shety | sh | Watch: steady, transfer | Comp-v2 |
| otey | ot | Output: steady | Comp-v2 |
| okaiin | ok | Vessel: extended sealed processing through multiple cycles | B Dict D1 |
| otedy | ot | Output: verify the drip rate is steady | B Dict D1 |
| qotar | qo | Fire: transfer heat/material and note result | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |

→ 9/10 recognized (90%).


### P5 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 21 (5% of folio) |
| e-depth | 0.714 |
| dar count | 0 |
| Quality checks (chek/shek) | 2 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- sh: 6 (28%)
- ch: 4 (19%)
- tch: 2 (9%)
- sa: 2 (9%)
- ot: 2 (9%)
- lsh: 1 (4%)
- ok: 1 (4%)

---

## Paragraph 6: Lines 32-41 (92 tokens)

### Token Reading (v2 workshop readings)

Every token on every line. **B Dict** = B Operational Dictionary, **Comp-v2** = composed from atoms, **---** = truly unrecognized.

**L32 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| tain | ta | Transfer: iterate, bind | Comp-v2 |
| sheey | sh | Watch: gentle steady state -- passive balneum observation | B Dict D2 |
| qotain | qo | Fire: transfer through one processing cycle | B Dict D2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| taiin | ta | Transfer: iterate, iterate, bind | Comp-v2 |
| chckhedy | ch | Test: temperature check | Comp-v2 |
| otol | ot | Output: hold current state | Comp-v2 |
| oty | ot | Output: transfer complete -- drip/flow has ceased | B Dict D2 |

→ 10/10 recognized (100%).

**L33 (3 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| otaiin | ot | Output: monitor through extended iteration cycles | B Dict D2 |
| shckhedy | sh | Watch: temperature check | Comp-v2 |

→ 3/3 recognized (100%).

**L34 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sakaiin | sa | Scaffold: sustained deep heating cycles | Comp-v2 |
| okeedy | ok | Vessel: maintain gentle balneum level | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qotain | qo | Fire: transfer through one processing cycle | B Dict D2 |
| cphey | --- | *unrecognized* (adjust, pause, watch, steady, ) | --- |
| opcheey | --- | *unrecognized* (set up, pause, adjust, watch, steady, steady, ) | --- |
| oty | ot | Output: transfer complete -- drip/flow has ceased | B Dict D2 |
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| otary | ot | Output: bring to and note result | Comp-v2 |

→ 7/9 recognized (77%).

**L35 (10 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| ychees | ch | Test: sequence steady | Comp-v2 |
| alchedy | al | Product settled: adjust, watch, steady, do | Comp-v2 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| lshedy | lsh | Watch equipment: confirm apparatus is steady | B Dict D2 |
| tol | to | Note transfer: hold | Comp-v2 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| olor | ol | Steady: note what happened | Comp-v2 |

→ 10/10 recognized (100%).

**L36 (6 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| cheol | ch | Test: verify and hold -- confirm state, maintain it | B Dict D2 |
| teey | te | Transfer step: steady | Comp-v2 |
| lshety | lsh | Watch equipment: steady, transfer | Comp-v2 |
| okeey | ok | Vessel: confirm gentle balneum temperature holds | B Dict D2 |
| qeedy | --- | *unrecognized* (q, steady, steady, do, ) | --- |

→ 5/6 recognized (83%).

**L37 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| qoeedy | qo | Fire: system steady, confirmed | Comp-v2 |
| lchedy | lch | Check equipment: confirm apparatus is stable | B Dict D1 |
| chees | ch | Test: sequence steady | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| oiiin | --- | *unrecognized* (set up, iterate, iterate, iterate, bind) | --- |
| chchky | ch | Test: heat with active monitoring | Comp-v2 |
| shekeey | sh | Watch: gentle steady heat — balneum level | Comp-v2 |
| qokey | qo | Fire: one quick heat-and-settle pulse | B Dict D2 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| sy | --- | *bare token: sequence, * | --- |

→ 9/11 recognized (81%).

**L38 (12 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| saiin | sa | Scaffold: begin an extended iteration cycle | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qokeedy | qo | Fire: one gentle balneum cycle, confirmed | B Dict D1 |
| lolsaiiin | ol | Steady: extended iteration cycles | Comp-v2 |
| qokain | qo | Fire: heat through next cycle -- sustained cyclic heating | B Dict D1 |
| chey | ch | Test: quick active check | B Dict D1 |
| r | --- | Respond -- route to next action | B Dict D3 |
| al | --- | Product settled -- yield has reached stable state | B Dict D1 |
| r | --- | Respond -- route to next action | B Dict D3 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| dl | --- | *bare token: do, hold* | --- |

→ 11/12 recognized (91%).

**L39 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sshey | sh | Watch: steady | Comp-v2 |
| lshedy | lsh | Watch equipment: confirm apparatus is steady | B Dict D2 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| okedy | ok | Vessel: confirm contents are stable | B Dict D1 |
| san | sa | Scaffold: bind | Comp-v2 |
| ol | --- | Steady: hold as-is -- maintain current state without change | B Dict D0 |
| keedy | ke | Gentle steady heat -- balneum cycle complete | B Dict D2 |
| sar | sa | Scaffold: note the position and respond | B Dict D3 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| dedy | de | cycle close | Comp-v2 |

→ 11/11 recognized (100%).

**L40 (11 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| qoky | qo | Fire: set -- stop adjusting, fire stays at current level | B Dict D1 |
| daiin | da | Start a new cycle -- initiate the next heating-monitoring loop | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |
| chey | ch | Test: quick active check | B Dict D1 |
| qokaiin | qo | Fire: sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| cheedy | ch | Test: verify gentle steady state proceeds correctly | B Dict D2 |
| qo | --- | *bare token: q, set up* | --- |
| char | ch | Test: bring to and note result | Comp-v2 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |

→ 10/11 recognized (90%).

**L41 (9 tokens)**
| Token | Prefix | Reading | Source |
|-------|--------|---------|--------|
| sol | so | Scaffold: mark current state in sequence | B Dict D1 |
| shey | sh | Watch: quick passive check | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qokedy | qo | Fire: one standard heat cycle | B Dict D1 |
| chedy | ch | Test: system steady -- active verification that the current state is stable | B Dict D1 |
| qol | qo | Fire: hold current heat level | B Dict D1 |
| r | --- | Respond -- route to next action | B Dict D3 |
| aiin | --- | Yield product into the next processing cycle | B Dict D0 |
| shedy | sh | Watch: system steady -- passive confirmation that conditions are holding | B Dict D1 |

→ 9/9 recognized (100%).



### P6 Structural Profile

| Feature | Value |
|---------|-------|
| Tokens | 92 (23% of folio) |
| e-depth | 0.598 |
| dar count | 2 |
| Quality checks (chek/shek) | 1 |
| Observation MIDDLEs | none |
| hh (extended obs) | 0 |

**Top prefixes:**
- qo: 16 (17%)
- ch: 16 (17%)
- sh: 10 (10%)
- sa: 8 (8%)
- ot: 5 (5%)
- ok: 3 (3%)
- lsh: 3 (3%)

---

## Cross-Paragraph Patterns

### e-depth Thermal Arc

| Para | Lines | Tokens | e-depth | Recipe phase |
|------|-------|--------|---------|-------------|
| P1 | 1-14 | 144 | 1.007 | Initial fixation — gentle, balneum-level |
| P2 | 15 | 5 | 1.200 | Brief transition (micro-paragraph) |
| P3 | 16-24 | 86 | 0.977 | Second fixation — slightly more heat |
| P4 | 25-29 | 52 | 0.673 | Intense fixation — heat increasing |
| P5 | 30-31 | 21 | 0.714 | Fusibility test — "melt like wax" |
| P6 | 32-41 | 92 | **0.598** | Multiplication — strongest sustained heat |

The e-depth descends monotonically from 1.01 to 0.60 (setting aside the P2 micro-transition). This encodes the recipe's core logic: fixation requires progressively stronger fire. The operator starts gentle and increases heat through each phase until the material is fixed enough to melt like wax. P6 (infinite multiplication) requires the strongest sustained heat — and has the lowest e-depth.

### dar Distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 3 | 30% | Initial fixation — loading gold + ferment |
| P2 | 0 | 0% | Transition (no material action) |
| P3 | 2 | 20% | Second fixation — adding fifth letter |
| P4 | 3 | 30% | Intense fixation — process adjustments |
| P5 | 0 | 0% | Fusibility test (no additions during test) |
| P6 | 2 | 20% | Multiplication — mixing operations |

P5 zero dar is structurally significant: during the fusibility test ("see it melt like wax without smoke"), the operator observes the product on the fire. No material is added during a quality test. This zero is a negative prediction that holds.

### chekar Distribution

| Para | chekar | Density | Recipe phase |
|------|--------|---------|-------------|
| P1 | 0 | 0% | Fixation in progress (not testing yet) |
| P2 | 0 | 0% | Transition |
| P3 | 0 | 0% | Second fixation (not testing yet) |
| P4 | 1 | 1.9% | Late fixation — first test |
| P5 | **2** | **9.5%** | **Fusibility test — peak density** |
| P6 | 1 | 1.1% | Multiplication — end-check |

The chekar tokens concentrate in P5 at 9.5% density — the highest on the folio. The recipe's fusibility test ("temptaràs assaiant si bona fusió prestarà sobre lo foch") maps to exactly this paragraph. P4's single chekar is a preliminary check; P6's is a final verification.

### sa-prefix (Scaffold/Iterate) Distribution

| Para | sa-prefix | % of para | Note |
|------|-----------|-----------|------|
| P1 | 1 | 0.7% | — |
| P2 | 0 | 0% | — |
| P3 | 3 | 3.5% | — |
| P4 | 3 | 5.8% | Iterative cycling increasing |
| P5 | 1 | 4.8% | — |
| P6 | **8** | **8.7%** | **"in infinit se pot multiplicar"** |

sa-prefix tokens concentrate in P6 — the multiplication paragraph. The recipe says this ferment "can be multiplied infinitely by secret mixing operations." The folio encodes this with the highest scaffold/iterate density on the folio, including extreme iteration markers (`oiiin`, `lolsaiiin` with triple-i).

---

## Verdict: COHERENT

f76v produces a coherent structural reading against III.15.0 (ferment conversion / liquefaction → multiplication). The folio's 6 paragraphs map to the recipe's progressive fixation sequence:

1. **Initial fixation** (P1, 144 tokens) — e-depth 1.01 (gentlest heat), ecth×2 (handling cooled intermediates), 3 dar (loading gold + ferment)
2. **Transition** (P2, 5 tokens) — micro-paragraph, highest e-depth (1.20)
3. **Second fixation** (P3, 86 tokens) — e-depth 0.98, ckh×1 (temperature check), 2 dar (adding fifth letter)
4. **Intense fixation** (P4, 52 tokens) — e-depth drops to 0.67, first chekar
5. **Fusibility test** (P5, 21 tokens) — chekar×2 (9.5% density), zero dar, "melt like wax without smoke"
6. **Infinite multiplication** (P6, 92 tokens) — lowest e-depth (0.60), 8 sa-prefix tokens, extreme iteration markers

The descending e-depth arc (1.01 → 0.60) is the primary structural signal — it directly encodes progressive fire strengthening through fixation. The chekar concentration in P5 independently confirms the fusibility test position. The sa-prefix surge in P6 independently confirms the multiplication phase.

**Honest gaps:** dar=10 exceeds the predicted low/zero (the recipe says "ajustant" = joining, which we predicted would use n-atoms rather than dar, but the folio uses both). No cs gold markers despite the recipe adding gold — the expert positive control explained this as consistent with gold as a dissolved intermediate, not a primary metallic input.
