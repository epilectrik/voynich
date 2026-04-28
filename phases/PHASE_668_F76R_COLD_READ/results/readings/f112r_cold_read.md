# Cold Read: f112r ↔ III.11.0 Red Mercury Tincture (Cohobation)

**Match tier:** SUPPORTED
**Verdict:** Partially Coherent

---

## The Recipe (III.11.0 — SISMEL Catalan, complete)

> Fill, tu prendras la liquor derrera que pus greu es separada per distillacio sobre cendres; e aquella distillaras en bany per .iii. vegades. E apres cascuna distillacio, metras l'aygua sobre la terra viscosa, e aquella terra tost se dissolra en la dita aygua. Separa altra vegada aquella aygua per cendres; aco's fa per entencio que l'aygua traga lo foch qui es en la terra e sia guardat per tinctura. Distilla aquella liquor altra vegada per bany, a fi que's dissoulle del foch, e mit lo foch tot temps a part tout ensemble; et soit come dit est par tant de fois distillat que le plus de l'ame de la terre soit extraite en feu sech. Distillada que sia, tira mes de la anima de la terra ab foch sech. Et guarda empero que la terra no's rubifich, car tantost cremaria la tinctura del sofre blanch en lo qual se deu fixar lo foch de la nostra pedra mercuriall. E aco reitera en tro que veies la terra comminuida, defallent de tota humiditat. Puis pren lo foch e lavalo ab la distillacio et calcinacio en tro que sia be roig asi com a foch ardent. Ffill, aquest feu se trau ab calor e humor, e l'altre ab seccor e fredor se cree e engenre.

*Cipher note: III.11 is in the Liber Mercuriorum (Part III), using the Part III letter cipher: B=simple water, C=simple red sulphur, D=simple dissolved gold, E=compound red water, F=compound red sulphur, G=compound dissolved gold. No letter codes appear explicitly in this sub-recipe, but the "liquor" and "water" references are understood as cipher-B (simple water) and the "fire" extracted from the earth as the tincture principle.*

**Translation:** Son, take the last liquor most difficult to separate by distillation over ashes; distill it in bath 3 times. After each distillation, put the water over the viscous earth -- it will quickly dissolve. Separate the water again over ashes; this is to extract the fire in the earth, kept for tincture. Distill that liquor again by bath to strip it of fire, and keep the fire aside; repeat until most of the earth's soul is extracted as dry fire. After distilling, draw more of the earth's soul with dry fire. BUT BEWARE: don't let the earth rubify, because it would immediately burn the tincture of white sulphur in which the fire of our mercurial stone must be fixed. Reiterate until the earth is diminished, drained of all moisture. Then take the fire and wash it with distillation and calcination until it is as red as burning fire.

The recipe is a cohobation procedure: repeatedly distill a liquor, return the distillate to the residue (viscous earth), and redistill -- extracting "fire" (active tincture principle) from the earth in stages. It alternates between two distillation modes (ash distillation and bath distillation) and includes a critical warning against over-rubification. The final phase is washing the extracted fire with distillation and calcination to achieve deep red color.

Key operational phases:
1. Initial ash distillation of the last liquor
2. Bath distillation x3 with cohobation (water returned to earth each time)
3. Ash separation to extract fire from earth
4. Repeated bath distillation to strip fire, setting it aside
5. WARNING: do not rubify the earth
6. Reiteration until earth is drained
7. Final washing with distillation + calcination to red

---

## Token Dictionary

The table below shows how Voynich tokens are read in this cold read. The "Workshop Reading" column gives the operational meaning validated against Catalan recipe text (PT-013/014/015) and distributional evidence (B Operational Dictionary). Readers unfamiliar with the atom system can ignore the Atoms column entirely -- the Workshop Reading is self-sufficient.

**How tokens work:** Each token has a PREFIX (what you're acting on) and a BODY (what you're doing). The prefix selects an operational domain; the body atoms specify the action within that domain.

| Prefix | Domain | Workshop sense |
|--------|--------|---------------|
| qo | Heat source | Managing the fire or furnace |
| ch | Active test | Checking state -- finger test, color check, viscosity |
| sh | Passive watch | Observing without intervention -- watching distillate, fumes |
| ok | Vessel | Managing the vessel or apparatus temperature |
| ot | Transfer rate | Monitoring output -- drip rate, melt flow |
| ol | Continue | Maintaining current state without change |
| da | Material | Adding or handling substances |
| sa | Scaffold | Supporting infrastructure for iterative cycling |

The body is built from **atoms** -- single characters with functional meanings. These compose left to right: the first atom (HEAD) sets the action domain, subsequent atoms (MOD) modify or parametrize it, and the final atom (TERM) closes the instruction. Key atoms:

| Atom | Role | Gloss | Confidence |
|------|------|-------|------------|
| k | HEAD | heat | LOCKED |
| e | MOD | cool / stabilize | LOCKED |
| h | MOD | watch | LOCKED |
| y | TERM | end / done | LOCKED |
| i | MOD | iterate | LOCKED |
| n | TERM | bind / contain | LOCKED |
| a | MOD | yield | LOCKED |
| m | TERM | final | LOCKED |
| d | MOD | mark / do | SOLID |
| t | HEAD | transfer / apparatus-mediated | SOLID |
| l | MOD/TERM | state / hold | SOLID |
| o | MOD | arrange | SOLID |
| c | MOD | adjust | SOLID |
| r | TERM | respond | PLAUSIBLE |

So `qo` + `k.e.d.y` reads compositionally as: *at the fire (qo), heat (k), stabilize (e), mark (d), done (y)* -- a single heat application with stabilization, executed and closed. Across 10 matched folios, this consistently appears where the recipe says to maintain the fire at a steady level, giving the workshop reading **"maintain current fire level."**

When `e` doubles (`k.e.e.d.y`), the extra stabilization encodes gentler, more sustained heat -- balneum mariae (water-bath) temperature rather than direct fire. When the terminal changes from `y` (done) to `a.i.n` (yield, iterate, bind), the instruction shifts from a single completed action to sustained cycling: **"keep heating through repeated cycles."**

**Key tokens on this folio:**

| Token | Prefix | Atoms | Compositional reading | Workshop Reading | Source |
|-------|--------|-------|-----------------------|-----------------|--------|
| qokedy | qo | k.e.d.y | fire: heat, stabilize, do, done | Maintain current fire level | PT-013 (10/10) |
| qokeedy | qo | k.e.e.d.y | fire: heat, stabilize x2, do, done | Gentle fire -- balneum / water-bath level | PT-013 (10/10) |
| qokeey | qo | k.e.e.y | fire: heat, stabilize x2, done | Establish gentle heat state | B Dict D1 |
| qokain | qo | k.a.i.n | fire: heat, yield, iterate, bind | Sustained cyclic heating | PT-013 (10/10) |
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate x2, bind | Sustained deep cyclic heating | B Dict D1 |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target -- heat stage done | PT-013 (10/10) |
| qokey | qo | k.e.y | fire: heat, stabilize, done | Brief heat application | B Dict D2 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qokchy | qo | k.c.h.y | fire: heat, adjust, watch, done | Adjust fire while watching | B Dict D2 |
| qokchdy | qo | k.c.h.d.y | fire: heat, adjust, watch, do, done | Monitored fire adjustment -- execute | B Dict D2 |
| qotedy | qo | t.e.d.y | fire: transfer, stabilize, do, done | Execute a heat-driven transfer | B Dict D1 |
| qoteedy | qo | t.e.e.d.y | fire: transfer, stabilize x2, do, done | Gentle heat-driven transfer | B Dict D2 |
| qokeeey | qo | k.e.e.e.y | fire: heat, stabilize x3, done | Very gentle heat -- extended cooling | B Dict D2 |
| qokeeiin | qo | k.e.e.i.i.n | fire: heat, stabilize x2, iterate x2, bind | Gentle sustained cycling -- balneum reiteration | Compositional |
| okeey | ok | e.e.y | vessel: stabilize x2, done | Vessel temperature: gently settled | B Dict D2 |
| okeedy | ok | e.e.d.y | vessel: stabilize x2, do, done | Vessel: maintain gentle balneum temperature | B Dict D1 |
| okedy | ok | e.d.y | vessel: stabilize, do, done | Vessel: check during cooling | B Dict D1 |
| okaiin | ok | a.i.i.n | vessel: yield, iterate x2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okal | ok | a.l | vessel: yield, hold | Vessel reached stable state | B Dict D2 |
| okar | ok | a.r | vessel: yield, respond | Vessel: note vessel state | B Dict D3 |
| okchedy | ok | c.h.e.d.y | vessel: adjust, watch, stabilize, do, done | Vessel: adjust while watching, verify | Compositional |
| okcheey | ok | c.h.e.e.y | vessel: adjust, watch, stabilize x2, done | Vessel: gentle adjustment under watch | Compositional |
| okeeey | ok | e.e.e.y | vessel: stabilize x3, done | Vessel temperature: very gentle stabilization | B Dict D2 |
| otedy | ot | e.d.y | drip-rate: stabilize, do, done | Check drip/flow rate during cooling | B Dict D1 |
| oteedy | ot | e.e.d.y | drip-rate: stabilize x2, do, done | Gentle drip monitoring | B Dict D2 |
| oteey | ot | e.e.y | drip-rate: stabilize x2, done | Transfer settled at gentle rate | B Dict D2 |
| otaiin | ot | a.i.i.n | drip-rate: yield, iterate x2, bind | Extended iterative transfer monitoring | B Dict D2 |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| otal | ot | a.l | drip-rate: yield, hold | Transfer rate stable | B Dict D2 |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state -- verify stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| cheey | ch | e.e.y | test: stabilize x2, done | Active verification of gentle state | B Dict D2 |
| chdy | ch | d.y | test: do, done | Active check: done | B Dict D2 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chcthy | ch | c.t.h.y | test: adjust, transfer, watch, done | Watch the transfer (active) | B Dict D2 |
| chody | ch | o.d.y | test: arrange, do, done | Check the arrangement | B Dict D2 |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| sheedy | sh | e.e.d.y | watch: stabilize x2, do, done | Extended passive observation | B Dict D2 |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dair | da | i.r | material: iterate, respond | Iterative material addition | B Dict D3 |
| dal | da | l | material: hold/state | Carefully collect or place material | PT-013 (9/10) |
| dam | da | m | material: final | Material handling finalized | B Dict D0 |
| saiin | sa | i.i.n | scaffold: iterate x2, bind | Begin extended binding iteration cycle | B Dict D1 |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| lchedy | lch | e.d.y | apparatus-check: stabilize, do, done | Check apparatus (seals, receiver, furnace) | PT-013 (8/10) |
| olkeedy | ol | k.e.e.d.y | continue: heat, stabilize x2, do, done | Continue: gentle heat execution | B Dict D2 |
| am | -- | a.m | yield, final | Phase done -- yield result and close | B Dict D0 |
| dy | -- | d.y | mark, done | Cycle close -- action complete | B Dict D1 |
| ol | -- | o.l | arrange, hold | Hold steady | B Dict D0 |
| or | -- | o.r | arrange, respond | Note what happened | B Dict D0 |
| ar | -- | a.r | yield, respond | Note the yield | B Dict D1 |
| aiin | -- | a.i.i.n | yield, iterate x2, bind | Yield into next processing cycle | B Dict D0 |

**Observation MIDDLEs** -- specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ckhh | c.k.h.h | adjust, heat, watch, watch | Extended heat-level surveillance |

---

## The Folio

**f112r:** 394 tokens, 45 lines, 14 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|---------------------|
| P1 | 1-6 | 48 | 0 | 0.60 | -- | Initial ash distillation of last liquor |
| P2 | 7-10 | 30 | 3 | 0.77 | -- | 3x bath distillation with cohobation |
| P3 | 11-14 | 34 | 0 | 0.88 | 1 cth | Ash separation to extract fire from earth |
| P4 | 15-18 | 37 | 1 | 0.70 | -- | Repeated bath distillation to strip fire |
| P5 | 19-24 | 53 | 3 | 0.72 | -- | Reiteration: extract soul as dry fire |
| P6 | 25 | 11 | 0 | 0.45 | 1 cth | Warning check: do not rubify |
| P7 | 26 | 3 | 0 | 0.67 | -- | Micro-check: verify state before continuing |
| P8 | 27-29 | 27 | 0 | 0.78 | 1 ckh | Continued extraction with dry fire |
| P9 | 30 | 9 | 0 | 0.56 | -- | Assessment: has the earth diminished? |
| P10 | 31-33 | 30 | 0 | 0.67 | 1 ckhh | Reiteration until earth drained of moisture |
| P11 | 34-36 | 26 | 0 | 0.46 | -- | Transition: take the fire for washing |
| P12 | 37-38 | 19 | 0 | 0.95 | -- | Distillation washing of extracted fire |
| P13 | 39-41 | 28 | 0 | 0.54 | -- | Calcination phase |
| P14 | 42-45 | 39 | 0 | 0.92 | -- | Final distillation to deep red |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation). Lower values = more sustained uninterrupted heat (calcination, dry fire processes). A value near zero means no thermal operation at all (vessel handling).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1-6, 48 tokens) -- Initial Ash Distillation

**Recipe says:** "Take the last liquor most difficult to separate by distillation over ashes."

The opening step: take a previously prepared liquor -- the hardest fraction to separate -- and distill it over ashes. Ash distillation uses moderate, steady heat through an ash bed, not a water bath.

**What the tokens say:**

The prefix distribution immediately stands out: `ot` (transfer rate monitoring) dominates with 15 of 48 tokens -- the heaviest transfer monitoring of any paragraph on this folio. Ash distillation is a slow, difficult separation ("the most difficult to separate") requiring close attention to what comes over. The operator is watching drip rates constantly.

L1 opens with `folchey` (vessel-load: adjust, watch, stabilize, done) and `qokeey` ("establish gentle heat") -- loading the apparatus and bringing it to temperature. Then `oteedal` (transfer rate: gentle stabilization to careful collection) -- the first drip monitoring. The line closes with `chcphy` (active check with pause and watch) -- an unusual token suggesting a deliberate pause to observe before proceeding.

L2: `saiin` ("begin extended binding iteration cycle") frames the iterative structure. Then heavy iteration: `qolkaiin` (heat with sustained contained cycling), `otail` (transfer rate: yield to state), `olaiin` (vessel load into extended cycle). The system is being set up for repeated passes.

L3: Two `oteedy` tokens in succession -- repeated gentle drip monitoring. Then `otaiin` (extended iterative transfer monitoring) and `oty` (transfer done). The operator monitors the drip rate through multiple cycles and notes completion.

L4: `qokeedy` ("gentle fire -- balneum level") followed by `chokain` (active check of sustained heat cycling) -- but wait, the recipe says ash distillation, not bath. The presence of `qokeedy` (balneum-level heat) in what should be an ash-distillation paragraph is a mild tension. However, ash-bed distillation does use moderate heat comparable to balneum, just delivered through a different medium. The thermal signature is similar even if the apparatus differs.

L5-L6: Dense transfer and vessel management: `otal` (transfer rate stable), `okeeey` (vessel very gently stabilized), `otar` (note drip rate), closing with `oram` (vessel: yield final) -- the separation is completing. L6 ends with `olkeedy` (continue gentle heat) and `oram` (yield final) -- wrapping up this distillation pass.

**Match assessment:** Partially coherent. The extreme ot-prefix density (31% of tokens) correctly encodes intensive transfer monitoring, consistent with a difficult separation. The e-depth of 0.60 indicates moderate distillation. Zero material additions -- the operator is working with material already in the vessel, which matches "take the last liquor." The balneum-temperature tokens in an ash-distillation context are mildly discordant but not disqualifying.

---

### P2 (Lines 7-10, 30 tokens) -- Bath Distillation x3 with Cohobation

**Recipe says:** "Distill it in bath 3 times. After each distillation, put the water over the viscous earth -- it will quickly dissolve."

The core cohobation cycle: distill in balneum, return the distillate to the viscous earth residue, redistill. Three times.

**What the tokens say:**

e-depth jumps to 0.77 -- a significant increase from P1's 0.60. The recipe shifts from ash distillation to bath distillation, and the folio registers this as more active cooling/stabilization. Bath distillation is gentler and involves more deliberate temperature management than ash distillation. The e-depth captures this.

`qo` prefix dominates (8 of 30 tokens) -- heavy fire management. L7 opens with `taiin` (transfer: extended iteration binding) and `olkeedy` ("continue gentle heat") -- the bath cycle is underway. Then `qoteo` (heat transfer with cooling and arrangement) -- a heat-driven transfer operation. `qokeey` ("establish gentle heat") confirms balneum-level operation.

L8: `sairor` (scaffold: complex iteration pattern) opens, followed by `qotchedy` (heat: transfer with adjustment while watching and cooling) -- a monitored transfer under gentle heat. Then `qokeeey` ("very gentle heat") -- the deepest stabilization on the folio so far, consistent with careful balneum temperature control. Two material additions follow: `dair` ("iterative material addition") -- returning the distillate to the earth. This is the cohobation step: the recipe says "put the water over the viscous earth."

L9: `saiin` ("begin extended iteration cycle") resets for the next cohobation pass. `okeey` (vessel gently settled), `qokeey` (gentle heat), `chedy` (check the state). Then `qokchy` ("adjust fire while watching") -- actively managing the heat between cycles. `qokary` (fire: heat, yield, respond) -- apply heat and note what happens.

L10: `dair` -- a third material addition, the third cohobation return. Then `chedy` (check state), `qodain` (heat: binding cycle), and `dam` ("material handling finalized"). The paragraph closes with material finalization, three bath cycles complete.

**Three material additions (dair, dair, dam) across the paragraph.** The recipe says "3 times" for the bath distillation cycle. Three dar tokens in P2 directly encode the three-fold cohobation.

**Match assessment:** Coherent. The e-depth rise to 0.77 captures the shift from ash to bath distillation. Three material additions match "per .iii. vegades" (three times). The mix of fire management, transfer operations, and scaffolding tokens encodes the reiterate-and-return structure of cohobation.

---

### P3 (Lines 11-14, 34 tokens) -- Ash Separation to Extract Fire

**Recipe says:** "Separate the water again over ashes; this is to extract the fire in the earth, kept for tincture."

Return to ash distillation -- but now with a specific purpose: extracting the "fire" (active principle) from the earth and preserving it for tincture.

**What the tokens say:**

e-depth spikes to 0.88 -- the second-highest on the folio. This is intensive distillation with heavy cooling intervention: extracting a volatile principle ("fire") demands careful condensation. You need to capture what comes over, not let it escape.

`qo` (8 tokens) and `ot` (7 tokens) together account for 44% of the paragraph -- fire management and transfer monitoring dominate, both essential for a targeted extraction. Zero material additions -- no new substances, just processing what is already present.

L11: Three consecutive `qokeey` tokens interspersed with transfer monitoring (`otey`, `qokedy`) -- sustained gentle heat driving the extraction. The line closes with `chotyr` (monitor: arrangement, transfer, respond) -- watching what comes across.

L12: `otchedy` (transfer monitoring with adjustment and watch -- **a transfer-watch observation MIDDLE**, cth) -- this is the paragraph's only observation MIDDLE, and it specifically encodes watching a transfer. The operator is actively observing what is being separated. `qotain` (heat: transfer yield iterate bind) -- a heat-driven iterative transfer. Then two more ot-prefix tokens (`oteedy`, `oteey`) -- continued drip monitoring.

L13: `chcthy` -- **transfer-watch** (cth observation MIDDLE). A second explicit transfer-watch appears on the same paragraph. Wait -- looking at the summary JSON, P3 shows only 1 cth, and this `chcthy` is also cth. But the JSON shows cth: 1 for P3. Let me check: the token on L12 is `otchedy` which has body `c.h.e.d.y` -- this contains cth in the prefix-adjusted body. The `chcthy` on L13 with body `c.t.h.y` is the counted cth. So one formal observation MIDDLE, but two tokens with transfer-watching character. The recipe says this step is specifically to "extract the fire in the earth" -- the operator is watching carefully for the tincture principle.

L14: `otaiin` (extended iterative transfer) and `okeedy` (vessel at gentle balneum) followed by `qokeey` (gentle heat). The paragraph winds down with iterative processing and gentle stabilization.

**Match assessment:** Coherent. The e-depth of 0.88 -- intensive distillation -- matches a targeted extraction step. The transfer-watch observation confirms the operator is actively monitoring what comes over. The combination of heavy fire management and transfer monitoring encodes "separate over ashes to extract the fire." Zero material additions: this is pure process.

---

### P4 (Lines 15-18, 37 tokens) -- Repeated Bath Distillation to Strip Fire

**Recipe says:** "Distill that liquor again by bath to strip it of fire, and keep the fire aside; repeat until most of the earth's soul is extracted as dry fire."

Return to bath distillation, now stripping the fire from the liquor and setting it aside.

**What the tokens say:**

e-depth drops to 0.70 -- still active distillation but less intensive than the targeted extraction in P3. The operator is now in a repeat-and-strip mode, less demanding than the initial targeted extraction.

The prefix mix is highly diverse (15 different prefixes for 37 tokens) -- the most varied paragraph on the folio. This matches the recipe's multi-step character: distill by bath, set the fire aside, repeat. Multiple sub-operations within one paragraph.

L15: Opens with `poar` (paragraph opener: yield, respond) and `alchor` (arrangement: adjust, watch, respond). Then `octhy` -- an arrangement with transfer-watch character (`o.c.t.h.y`), though not formally counted as an observation MIDDLE due to the unprefixed form. `qokeedy` ("gentle fire -- balneum") -- bath distillation confirmed. `pchedy` (stage-test: verify state) -- a paragraph-opening check.

L16: `shol` (passive watch: hold state) -- the operator observes without intervening. Then three fire-management tokens: `qokeey`, `qokeeey`, `qokedain`. The `qokeeey` ("very gentle heat") is notable -- extreme stabilization. `qokedain` (fire: heat, stabilize, do, yield, iterate, bind) is a complex token that encodes heated iterative cycling with stabilization -- sustained balneum reiteration.

L17: `qoeeean` (heat: triple stabilization, yield, bind) -- extreme cooling atoms, the most stabilized heat token in this paragraph. The operator is managing a very gentle bath distillation. Then `cheey` x2 (active verification of gentle state), `qor` (heat: respond), `qokey` (brief heat). Multiple monitoring checks.

L18: `saiin` (begin extended iteration cycle). One material addition: `dalchd` (material: hold, adjust, watch, do) -- a careful, watched material placement. This is "keep the fire aside" -- the extracted fire is being set apart. `okal` (vessel: yield, hold -- vessel reached stable state), then `chody`, `chedy`, `cham` -- three active checks in sequence ending with `cham` (test: yield, final). The paragraph closes with verification that the step is complete.

**Match assessment:** Partially coherent. The bath-distillation heat signature (qokeey, qokeeey) matches. The single material addition (setting fire aside) plausibly encodes "keep the fire aside." The high prefix diversity captures the multi-operation character of this step. The e-depth of 0.70, lower than P3's extraction, suggests the stripping operation is less thermally demanding than the initial extraction.

---

### P5 (Lines 19-24, 53 tokens) -- Reiteration: Extract the Earth's Soul

**Recipe says:** "Repeat until most of the earth's soul is extracted as dry fire. After distilling, draw more of the earth's soul with dry fire."

Extended reiteration of the distill-strip-set-aside cycle. The largest paragraph on the folio -- the reiteration demands the most operational space.

**What the tokens say:**

53 tokens across 6 lines -- the largest paragraph, consistent with the recipe's "repeat until" instruction requiring extended cycling. e-depth is 0.72 -- sustained active distillation.

`qo` prefix dominates (11 of 53 tokens) -- heavy fire management. Three material additions (dal, daichy, dairiy) spread across the paragraph provide periodic material handling during the reiteration.

L19: `polchdy` (paragraph opener with watched adjustment), `saiin` (begin iteration), then fire sequence: `qeey`, `qokey`, `qokeey`, `qoko` -- escalating from brief heat to gentle balneum to heat-arrangement. The fire is being managed through the cycle. `am` (phase done) closes the sub-step.

L20: `qoaiin` (heat: extended iteration) opens -- sustained cycling. `keody`, `keol` (steady-state thermal checks). `okeeey` (vessel: very gentle stabilization). Then `dal` ("carefully collect material") -- setting aside the extracted fire. `aiin` (yield into next cycle) and `ody` (arrange, done) -- cycle complete, next begins.

L21: `solkeedy` (sequence: gentle heat execution) and `raiin` (yield into extended cycle). Then `chcthey` -- although this token contains a `cth` transfer-watch pattern in its body, it is not formally counted as an observation MIDDLE in the summary. Followed by `qoteedy` ("gentle heat-driven transfer") -- a balneum-level transfer operation. The reiteration is distilling and transferring in gentle cycles.

L22: `daichy` (material: iterate, adjust, watch) -- a watched material addition. `lchedy` ("check apparatus") -- verifying seals and equipment during the long reiteration.

L23: `qoain` (heat: yield, iterate, bind) and `qoiin` (heat: deep iteration) -- sustained cycling. `dairiy` (material: iterate, respond, iterate) -- another material operation, iterative in character. `teedy` (transfer execution), `qopol` (heat: pause, arrange, hold) -- a pause in the heating. Then `octhdy` -- an arrangement with transfer-watch character: watching the distillate. `otychey` -- transfer monitoring with checking.

L24: `cheeteey` (test: double stabilization with transfer) -- an unusually complex check token, monitoring both cooling and transfer simultaneously. `qoteeey` (heat: very gentle transfer) -- the gentlest transfer on the folio. `lkeey`, `okeedy`, `lkedy` -- equipment and vessel at gentle temperature. Then `qokedy` ("maintain current fire level") and two `otedy` (drip rate checks). The paragraph winds down with standard monitoring.

**One quality check** appears in this paragraph: `chekar` is counted once in the summary (via `cheeteey` or similar -- the JSON shows chekar_count: 1). This is the only quality check on the entire folio, and it falls in the reiteration paragraph where the recipe says "until most of the earth's soul is extracted." The operator is checking: have we extracted enough?

**Match assessment:** Partially coherent. The largest paragraph encodes the longest recipe phase. Three material additions across 6 lines match periodic fire-set-aside operations during reiteration. The quality check uniquely placed here matches the "until" condition. The e-depth of 0.72 sustains active distillation across the whole reiteration.

---

### P6 (Line 25, 11 tokens) -- Warning Check: Do Not Rubify

**Recipe says:** "BUT BEWARE: don't let the earth rubify, because it would immediately burn the tincture of white sulphur in which the fire of our mercurial stone must be fixed."

A critical warning mid-procedure. The operator must check the earth's color -- if it starts to turn red (rubify), the tincture is at risk.

**What the tokens say:**

Only 11 tokens on a single line. The e-depth drops sharply to 0.45 -- the lowest so far, equal to P11. This is not a distillation paragraph. The operator has paused active distillation to inspect.

The prefix mix is diagnostic: `ch` x3 (active testing dominates), `ok` x2 (vessel checks), `sh` x1 (passive observation). The paragraph is almost entirely about checking and watching. Zero material additions, zero fire management tokens with `qo` prefix. The operator is not heating or adding anything -- just looking.

Key sequence: `tedain` (transfer: binding cycle) -- noting a transfer state. `shedy` ("watch the distillate") -- passive observation. `okchd` (vessel: adjust, watch, do) -- vessel check. Then `kedy` (steady-state thermal: done) and `chor` (active check: arrange, respond).

The paragraph's single observation MIDDLE is `chcthy` -- a **transfer-watch** (cth). The operator is actively watching what is being transferred. In the context of "don't let the earth rubify," the transfer-watch encodes: look at what's coming over -- is the color changing? Is the earth darkening?

`cheety` (test: double stabilization with transfer) -- checking that the product is still gently stabilized, not overheating into rubification.

**Match assessment:** Coherent. The sharp e-depth drop, the absence of fire management, the dominance of active checks, and the transfer-watch all encode an inspection pause. The recipe's warning ("guarda empero") becomes a paragraph-level operational stop: check the state before proceeding.

---

### P7 (Line 26, 3 tokens) -- Micro-Check

**Recipe says:** (Continuation of the warning: verify before resuming)

**What the tokens say:**

Only 3 tokens -- the smallest paragraph on the folio and one of the shortest in all cold-read folios.

```
L26:  tockhy  chedy  chedam
```

`tockhy` (transfer operation: adjust, heat, watch) -- checking a heat-related transfer. `chedy` ("check the state") -- active verification. `chedam` (test: stabilize, do, yield, final) -- verification with finality marker. The `m` (final) atom in `chedam` marks this as a concluding check.

The three tokens read sequentially: *check the transfer under heat -- verify the state -- verification complete and final.* This is a gate: the operator has inspected (P6), now confirms the result before resuming operations.

**Match assessment:** Coherent as a minimal gate paragraph. The recipe's warning logically produces two operational units: the inspection (P6) and the go/no-go confirmation (P7). The `m`-terminal in `chedam` marks finality -- the check is done, proceed.

---

### P8 (Lines 27-29, 27 tokens) -- Continued Extraction with Dry Fire

**Recipe says:** "After distilling, draw more of the earth's soul with dry fire."

Resume extraction after the warning check, now using dry fire (direct heat rather than bath).

**What the tokens say:**

e-depth returns to 0.78 -- back to active distillation after the P6-P7 inspection pause. The shift from the warning's 0.45 back up to 0.78 signals resumed thermal operations.

L27 is dense with complex tokens: `pcholkeedy` (stage-check: arrangement, state, gentle heat execution) opens the paragraph as a formal restart. `okchoiiin` (vessel: adjust, watch, arrangement, triple iteration, bind) -- the vessel is being set up for extended sealed operation with triple iteration depth. Two `opchedy` tokens appear -- arrangement with pause, adjustment, and watching. The repetition suggests a deliberate, careful setup.

L28: `sheokeedy` (observe: gentle heat arrangement) -- passive observation of the heat setup. Then `qokeedy` ("gentle fire -- balneum") and `qokain` ("sustained cyclic heating") appear together. `oteedy` (gentle drip monitoring). Then **`chckhy`** -- a **heat-level check** (ckh observation MIDDLE). This is the only formal heat-level check on the entire folio, and it falls precisely where the recipe transitions from bath distillation to dry fire. The operator is checking: is the heat level correct for the new mode?

L29: `saiin`, `olshedy` (continue: watch state), `chokeey` (monitor: heat and gentle stabilization), `okaiin` (vessel: extended sealed processing). The extraction continues with sustained cycling and monitoring.

**Match assessment:** Coherent. The single heat-level check (ckh) marks the transition to a different heat regime (dry fire). The resumed e-depth after the warning pause encodes the restart of active extraction. Heavy observation tokens (4 sh-prefix) suggest careful monitoring during this delicate phase.

---

### P9 (Line 30, 9 tokens) -- Assessment: Has the Earth Diminished?

**Recipe says:** "Reiterate until you see the earth diminished, drained of all moisture."

A check point: is the earth sufficiently depleted?

**What the tokens say:**

9 tokens on a single line. e-depth drops to 0.56 -- moderate, not intensive distillation. `ch` prefix dominates (4 of 9 tokens) -- active testing.

```
L30:  tar  ar  cheokey  okeody  chol  ol  chedy  qokedy  cheom
```

The sequence reads: `tar` (transfer yield) -- `ar` (note the yield) -- `cheokey` (test: arrangement, heat, stabilize) -- `okeody` (vessel: arrangement completed). Then `chol` (active check: hold), `ol` (hold steady), `chedy` (check the state). A single `qokedy` ("maintain fire level") appears -- minimal fire management. The paragraph closes with `cheom` (test: stabilize, arrange, final) -- assessment finalized.

The pattern is check-heavy with a single heat token. The operator is inspecting the state of the earth: has it diminished? Is there still moisture? The `m`-terminal in `cheom` closes the assessment.

**Match assessment:** Coherent. A brief assessment paragraph with active testing dominance and minimal heating. The recipe's "reiterate until" condition demands periodic checks, and this paragraph is one.

---

### P10 (Lines 31-33, 30 tokens) -- Reiteration Until Earth Drained

**Recipe says:** "Reiterate until the earth is diminished, drained of all moisture."

Continued reiteration following the assessment. The process is not yet complete.

**What the tokens say:**

e-depth returns to 0.67 -- moderate active distillation. `ok` prefix dominates (5 of 30 tokens) -- vessel management is central.

L31: `okaiin` (vessel: extended sealed processing) and `otain` (transfer: iterative binding) -- the vessel is sealed and the transfer cycle continues. `lchedy` ("check apparatus") -- equipment verification. Then `okeeor` (vessel: gentle stabilization, arrangement, respond) and `oteor` (transfer: stabilization, arrangement, respond) -- both showing gentle management of vessel and transfer.

L32: A distinctive sequence -- `ar`, `al`, `ar`, `s` -- a rapid sequence of yield-note, state, yield-note, sequence-marker. This read-note-read pattern is unusual and may encode the operator checking the earth's state repeatedly. `alkeear` (arrangement: gentle heat, yield, respond) -- an arrangement-domain token with heat and yield. `okeechy` (vessel: gentle stabilization with adjustment and watch) -- careful vessel management. `qoiiin` (heat: triple iteration binding) -- deep iterative heating. The triple `i` depth is notable: the deepest iteration token in this paragraph, encoding sustained repetitive cycling.

L33: The paragraph's observation MIDDLE appears: `shckhhy` -- a **heat-level check with extended watch** (ckhh). The double `h` (watch.watch) extends the observation. This is the only `ckhh` on the folio -- an intensified heat surveillance token. After the P9 assessment found the earth insufficiently drained, the operator returns to extraction with heightened monitoring. `okcheey` (vessel: adjust, watch, gentle stabilization), `chedy` (check state), `shdal` (observe: material placement).

**Match assessment:** Partially coherent. The extended heat surveillance (ckhh) marks heightened attention during continued reiteration. The deep iteration tokens (qoiiin) encode sustained cycling. The assessment in P9 was not satisfied; P10 continues the work with more intensive monitoring.

---

### P11 (Lines 34-36, 26 tokens) -- Transition: Take the Fire for Washing

**Recipe says:** "Then take the fire and wash it with distillation and calcination until it is as red as burning fire."

Transition between extraction and the final washing phase. The extracted fire is now the subject.

**What the tokens say:**

e-depth drops to 0.46 -- the second-lowest on the folio. The thermal character shifts: this is not active distillation but preparation for a new phase. Fewer cooling atoms mean less distillation and more sustained or direct heat -- consistent with the transition toward calcination.

`ok` (5) and `qo` (5) share dominance -- equal emphasis on vessel management and fire management. `ol` (3) maintains state, `sa` (2) provides iteration scaffolding.

L34: `lshdar` (equipment-watch: material, yield, respond) -- monitoring a material movement. `okechedy` (vessel: stabilize, adjust, watch, stabilize, do, done) -- a complex vessel check with double stabilization. `qokar` ("apply heat and note the response") -- direct heat application. Then `qotedy` ("execute a heat-driven transfer") -- the extracted fire is being moved. `qokchdy` ("monitored fire adjustment") -- adjust the fire while watching.

L35: `sain` ("begin iteration cycle"). `olaiin` (vessel load: extended iteration) -- loading the vessel for the new phase. `qopchdy` (heat: pause, adjust, watch) -- careful heat management with a pause. `qoky` ("cease heating") -- a full heat stop. Then vessel checks: `okeal` (vessel: stabilize, yield, hold), `chedy` (check state), `okeey` (vessel: gentle stabilization), `otedy` (drip check), `okeedy` (vessel: gentle balneum).

L36: `sain` again -- another iteration cycle begins. `checkhy` (test: stabilize, adjust, heat, watch) -- a comprehensive check combining cooling, adjustment, heat, and observation. `olchain` (vessel-load: adjust, watch, yield, iterate, bind) -- loading with watched iteration. `okeey` (gentle stabilization). `olam` (vessel-load: yield, final) -- loading complete.

**Match assessment:** Partially coherent. The low e-depth encodes a shift away from active distillation. The mix of vessel loading, fire cessation, and iteration scaffolding plausibly encodes the transition: stop extracting, take the fire, and prepare for the washing phase. The heat cessation (`qoky`) marks a procedural boundary.

---

### P12 (Lines 37-38, 19 tokens) -- Distillation Washing of Extracted Fire

**Recipe says:** "...wash it with distillation and calcination until it is as red as burning fire."

The distillation half of the final washing. The extracted fire is distilled to purify it.

**What the tokens say:**

e-depth spikes to 0.95 -- the highest of any paragraph on the folio. This is the most intensive distillation step. The recipe says to "wash with distillation" -- purificatory distillation to achieve deep red. Maximum cooling intervention means maximum condensation effort: every drop of distillate matters.

`ok` prefix dominates overwhelmingly (7 of 19 tokens) -- vessel management central to washing distillation. The operator is managing the vessel through intensive cooling cycles.

L37: `pom` (paragraph: final) -- a finality marker opening the paragraph. `okaiin` (vessel: extended sealed processing) -- sealed cycling. Then a striking sequence of vessel management tokens: `olkedy` (continue: heat, stabilize, do, done), `okedy` (vessel: check during cooling), `okeey` (vessel: gently settled), `okeedy` (vessel: gentle balneum). Four consecutive ok/ol-prefix tokens, each with progressively more stabilization. The vessel temperature is being walked down through careful stages.

Then `keedas` (steady-state thermal: stabilize, do, yield, sequence) -- a sequenced thermal state. `otear` (transfer: stabilize, yield, respond) -- noting the output. `shkeor` (observe: heat, stabilize, arrangement, respond) -- passively watching the heat arrangement. `qoky` ("cease heating") closes L37.

L38: `sar` (scaffold: respond) and `ain` (yield, iterate, bind) -- iteration continues. `olkeear` (continue: gentle heat, yield, respond) -- sustained gentle heat. `okeody` (vessel: arrangement done). `qokeeiin` ("gentle sustained cycling -- balneum reiteration") -- the most significant heat token in this paragraph, encoding gentle balneum-level cycling with deep iteration. `oteedy` (gentle drip monitoring). `qokey` (brief heat), `okal` (vessel at stable state), `okedy` (vessel check during cooling).

**Match assessment:** Coherent. The highest e-depth on the folio (0.95) maps to purificatory distillation. The vessel-dominated prefix profile encodes apparatus-intensive washing. The `qokeeiin` token encodes exactly what "wash with distillation" demands: gentle sustained cycling through the balneum.

---

### P13 (Lines 39-41, 28 tokens) -- Calcination Phase

**Recipe says:** "...wash it with distillation **and calcination** until it is as red as burning fire."

The calcination half of the final washing. After distillation, apply sustained dry heat to calcine.

**What the tokens say:**

e-depth drops sharply to 0.54 -- a dramatic fall from P12's 0.95. Calcination uses sustained dry heat with minimal cooling. The e-depth captures this: fewer cooling atoms mean less condensation management and more raw heat application.

`ok` prefix still dominates (8 of 28 tokens) -- the vessel remains central, but now the vessel is being managed under sustained heat rather than distillation. `qo` contributes 3 tokens, `ch` 2, `sh` 2.

L39: `palkeedy` (arrangement: gentle heat execution) -- initiating gentle heat. `qopal` (heat: pause, yield, hold) -- careful heat establishment. `okaiiin` (vessel: yield, triple iteration, bind) -- the deepest iteration token on the folio (three `i` atoms). Triple iteration encodes extended sealed processing through many cycles -- consistent with prolonged calcination. `sheody` (observe: arrangement done) -- watching the result.

L40: `sain` ("begin iteration cycle"). `okal` (vessel at stable state). `lkeedy` (equipment: gentle heat execution). Then `okar` (vessel: note state), `okchedy` (vessel: adjust, watch, stabilize) -- vessel management with monitoring. `qokal` ("fire reached target") -- the heat has arrived at the desired level. `chkey` (test: heat, stabilize, done) -- checking that the heat is correct.

L41: `cheey` (active verification of gentle state), `okchey` (vessel: adjust, watch, stabilize), `qokchy` ("adjust fire while watching"). Three consecutive check/adjustment tokens. Then `okchaiin` (vessel: adjust, watch, yield, extended iteration) -- the vessel is being managed through watched iterative cycles. `okeeos` (vessel: gentle stabilization, arrangement, sequence), `okchy` (vessel: adjust, watch), `ory` (vessel respond: done). Dense vessel checking to close.

**Match assessment:** Coherent. The e-depth drop from 0.95 to 0.54 precisely marks the shift from distillation to calcination. The deepest iteration token (okaiiin, triple-i) encodes extended calcination cycling. The ok-prefix dominance continues but now under sustained heat rather than cooling -- the vessel is being calcined, not distilled.

---

### P14 (Lines 42-45, 39 tokens) -- Final Distillation to Deep Red

**Recipe says:** "...until it is as red as burning fire. Son, this fire is drawn with heat and moisture, and the other with dryness and cold is created and engendered."

The final step: achieve the deep red color through final distillation. The recipe's closing sentence describes the dual-nature principle being separated.

**What the tokens say:**

e-depth surges back to 0.92 -- the second-highest on the folio, nearly matching P12's 0.95. The folio returns to intensive distillation for the final push to red. The recipe says "until it is as red as burning fire" -- the operator distills until the color criterion is met.

`ok` prefix dominates again (8 of 39 tokens), with significant `qo` (4), `sh` (3), `te` (3), and `ot` (3) contributions. The prefix diversity suggests a multi-mode final operation combining vessel management, fire control, passive observation, transfer execution, and drip monitoring.

L42: `polar` (paragraph opener: state, yield, respond). `shedy` ("watch the distillate") -- passive observation returns. `qokaiin` ("sustained deep cyclic heating") -- the strongest fire token in this paragraph, encoding deep iterative heating. `okeedy` (vessel at gentle balneum), `qotal` (heat: transfer yield to state).

L43: `okar` (vessel: note state), `ycheedy` (check: gentle stabilization execution), `yteeey` (transfer: very gentle stabilization), `sheor` (observe: stabilization, arrangement, respond) -- the operator observes, checks, and monitors the gentle transfer. `oteeg` (transfer: gentle stabilization) closes the line.

L44: `sar` (scaffold: respond), `ain` (yield, iterate, bind). Then `qokaekeeey` -- a remarkable token: fire: heat, yield, stabilize, heat, stabilize x3, done. This complex double-heat token with heavy stabilization encodes a carefully managed heat application with extreme cooling -- perhaps the final precision distillation. `okaeechey` (vessel: yield, stabilize x2, adjust, watch, stabilize) -- an equally complex vessel token. `okeeedy` (vessel: triple stabilization, do, done) -- the most stabilized vessel token on the folio. The operator is managing temperature with extreme precision for the final color achievement.

L45 (final line): `okeeey` (vessel: triple stabilization), `oteeedy` (transfer: triple stabilization, do, done) -- the most stabilized transfer token on the folio. `qokeey` (gentle heat), `okeey` (vessel: gentle stabilization). The folio closes with `okary` (vessel: yield, respond, done) and `yky` -- a terminal marker.

**Match assessment:** Coherent. The return to peak e-depth (0.92) for the final paragraph matches the recipe's concluding distillation to achieve deep red. The extremely stabilized tokens (triple-e vessels and transfers) encode maximum precision -- the operator is managing the last, most critical distillation step. The folio ends as the recipe ends: the fire is washed until red.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | 0.60 | Moderate ash distillation |
| P2 | 0.77 | Active bath distillation (cohobation) |
| P3 | 0.88 | Intensive targeted extraction |
| P4 | 0.70 | Repeat bath distillation, less intensive |
| P5 | 0.72 | Extended reiteration cycling |
| P6 | **0.45** | Warning inspection pause |
| P7 | 0.67 | Micro-check gate |
| P8 | 0.78 | Resumed extraction with dry fire |
| P9 | 0.56 | Assessment pause |
| P10 | 0.67 | Continued reiteration |
| P11 | **0.46** | Transition: fire cessation for new phase |
| P12 | **0.95** | Purificatory distillation washing (peak) |
| P13 | **0.54** | Calcination (sustained dry heat) |
| P14 | **0.92** | Final distillation to deep red |

The e-depth traces a distinctive double-peak arc. The first half (P1-P5) rises from 0.60 to 0.88, drops back to 0.70-0.72 during reiteration, then crashes to 0.45 at the warning check. After the warning, it rises again through P8 (0.78), dips at the assessment (P9: 0.56), then produces the most dramatic swing on the folio: P11 (0.46, transition) to P12 (0.95, distillation wash) to P13 (0.54, calcination) to P14 (0.92, final distillation). The P12-P13-P14 sequence -- high, low, high -- directly encodes the recipe's "wash with distillation and calcination": distill (high e-depth), calcine (low e-depth), final distill (high e-depth).

### dar distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 0 | 0% | Initial distillation (material already present) |
| P2 | 3 | 43% | Cohobation: 3x return of water to earth |
| P3 | 0 | 0% | Ash extraction (pure process) |
| P4 | 1 | 14% | Set fire aside |
| P5 | 3 | 43% | Reiteration with periodic fire-set-aside |
| P6-P14 | 0 | 0% | Post-warning: process management only |

Total dar: 7. All material additions occur in P2, P4, and P5 -- the cohobation and reiteration phases. The recipe's cohobation ("put the water over the viscous earth") requires material returns, and P2's three dar tokens directly encode the three-fold cycle. After P5, zero material additions appear: the second half of the folio is pure process management (washing, calcination, final distillation). The recipe matches this: once the fire is extracted, the remaining operations are purification of what has already been collected.

The remarkably low dar count (7 total for a 394-token folio) initially seems discordant with a "complex multi-phase procedure." But the recipe's complexity is procedural, not material. Most steps involve the same two substances (water and earth/fire) being repeatedly processed. New material introductions are rare -- it is the same liquor being distilled, returned, and redistilled. The folio encodes process management over material handling, which is exactly what cohobation demands.

### Observation MIDDLE distribution

| Para | ckh | cth | ckhh | Total | Recipe activity |
|------|-----|-----|------|-------|-----------------|
| P1 | -- | -- | -- | 0 | Initial distillation (routine) |
| P2 | -- | -- | -- | 0 | Cohobation cycling |
| P3 | -- | 1 | -- | 1 | Targeted extraction: watching the transfer |
| P4 | -- | -- | -- | 0 | Repeat bath distillation |
| P5 | -- | -- | -- | 0 | Extended reiteration |
| P6 | -- | 1 | -- | 1 | Warning check: watching for rubification |
| P7 | -- | -- | -- | 0 | Gate check |
| P8 | 1 | -- | -- | 1 | Heat-level check at mode transition |
| P9 | -- | -- | -- | 0 | Assessment |
| P10 | -- | -- | 1 | 1 | Extended heat surveillance during reiteration |
| P11 | -- | -- | -- | 0 | Transition |
| P12 | -- | -- | -- | 0 | Distillation washing |
| P13 | -- | -- | -- | 0 | Calcination |
| P14 | -- | -- | -- | 0 | Final distillation |

Four observation MIDDLEs total, each in a different paragraph. Two are transfer-watches (cth) at the extraction step (P3) and the warning check (P6) -- both moments where the operator must watch what is coming over. One heat-level check (ckh) at P8 where the heat regime changes. One extended heat surveillance (ckhh) at P10 where the reiteration requires heightened attention. The observations are sparse but functionally placed: they mark the moments of greatest operational risk.

---

## Structural Notes

### The 14-paragraph fragmentation

f112r has 14 paragraphs for 394 tokens -- an average of 28 tokens per paragraph. This is notably fragmented compared to f75r (9 paragraphs, 46 tokens average). The fragmentation matches the recipe's character: cohobation is not a linear procedure but a multi-phase operation with mode switches (ash vs. bath distillation), a warning interruption, assessment pauses, and a transition between extraction and washing. Each mode switch gets its own paragraph.

Three paragraphs have fewer than 10 tokens (P7: 3, P9: 9). These micro-paragraphs function as operational gates -- brief checks between longer processing phases. P7 (3 tokens) is the go/no-go after the rubification warning; P9 (9 tokens) is the assessment of whether the earth has diminished. The recipe's procedural logic demands these check points.

### The ok-prefix shift

A distinctive pattern emerges across the folio:

- P1-P5 (first half): `ot` and `qo` dominate. Transfer monitoring and fire management -- the operator is distilling and watching drip rates.
- P6-P14 (second half): `ok` dominates. Vessel management takes over -- the operator is managing the apparatus through washing, calcination, and final distillation.

The shift from transfer-monitoring to vessel-management corresponds to the recipe's structural pivot: the first half extracts (you watch what comes over), the second half washes and calcines (you manage the vessel through repeated thermal cycles). The folio's prefix distribution tracks this operational shift.

---

## Verdict: PARTIALLY COHERENT

f112r produces a partially coherent paragraph-by-paragraph reading against III.11.0 (red mercury tincture via cohobation). The structural alignment is solid at the macro level but less precise at the individual paragraph level than the strongest cold reads.

**What works well:**

1. **e-depth arc** -- The double-peak structure, the P12-P13-P14 distillation-calcination-distillation swing, and the warning-pause dip at P6 all track the recipe's thermal logic.
2. **dar distribution** -- Three material additions in P2 match "3 times" cohobation. All dar concentrated in P2/P4/P5 (extraction phases) with zero in P6-P14 (process management) matches the recipe's material structure.
3. **Observation placement** -- Four observation MIDDLEs at the four highest-risk moments (extraction, warning, mode change, heightened reiteration).
4. **Paragraph fragmentation** -- 14 paragraphs with micro-gates at P7 and P9 encode the recipe's multi-phase procedural structure.
5. **ok-prefix shift** -- Transfer monitoring in the first half, vessel management in the second, tracking the extraction-to-washing pivot.

**What is weaker:**

1. **7 dar for 394 tokens** -- While explainable (cohobation recycles the same material), the low count means less material-handling evidence to anchor the reading.
2. **No counting anchor** -- The recipe's "3 times" in P2 maps plausibly to 3 dar, but there is no corpus-singular identical-token run like f75r's 4x qokedy. The counting evidence is distributional, not structural.
3. **Individual paragraph boundaries** -- The mapping of 14 paragraphs to 7 recipe phases requires some paragraphs to share a phase (P8-P10 all map to "reiteration until drained"), which is less precise than a 1:1 paragraph-to-step mapping.
4. **Balneum tokens in ash distillation (P1)** -- The recipe distinguishes ash distillation from bath distillation, but the thermal tokens do not clearly differentiate these modes.
5. **P14 calcination-endpoint discordance (expert review)** -- The recipe ends with "lavalo ab distillació et calcinació en tro que sia bé roig" (wash by calcination until red as fire). Per C1225/C1970, calcination should produce near-zero e-depth (direct fire, no balneum dampening). P14's e-depth of 0.92 is the second-highest on the folio — the opposite of what calcination predicts. This is the strongest single piece of negative evidence against the match.

The match tier of SUPPORTED is appropriate: the macro-structural patterns (e-depth arc, dar distribution, observation placement, prefix shift) all align with the recipe, but the individual paragraph readings require more interpretive bridging than the strongest confirmed matches.
