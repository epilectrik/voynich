# Cold Read: f112v ↔ III.1.0 Lunaria (Making Mercuries — Quicksilver Preparation)

**Match tier:** Supported
**Verdict:** Coherent

---

## The Recipe (III.1.0 — SISMEL Catalan, complete)

> Fill, t'es ops que entenes les operacions per les quals se creen los nostres argents vius. Apres, si saps ho, has scientia de conexer lo nostre argent viu; hauras l'art integrament, car les operacions de tots no es sino una cosa qui's fa per la manera que ara't direm. Tu pendras de la liquor mercuriall aliter o lunaria quant en volras, e de aquella per distillacio departiras les elements. Mas primerament separaras l'aygua fleumatica en la qual esta mortificat lo esperit. E continua en bany ta distillacio en tro que veies distillar per l'aygua animada que comenca a cremar. E aquella distilla a part; e quant tot co qui's pora distillar per aquella calor hauras reebut, la fleuma ne serra fora, axi com manifesta lo senyall de son cremament. E aquella partiras en dues parts: e la una part guardaras per crear los mercuries; e de la segona trauras los elements sens tota combustio desus la conservacio de la proprietat del sofre e de l'argent viu. En aquesta manera tu mettras la dita part de l'aygua animada sobre les feces... E tantost mit lo alembich dessus ab ton receptor, e encen lo foch de serradura composta... E aquell se continue en tro tot co que pora distillar sia distillat per equalitat del dit foch. E soit fet ceste distillacion en bany marie. Apres mit-ho en foch sech cinerench ab aquell continuitat de serradura; distilla lo oli, e a la fi de la distillacio lexa refradar la materia ab tot lo vexell. Puys retorna la primera liquor que es entre l'aygua primera e l'oli sobre les feces e reitera ta distillacio axi com ja es dit, en tro que les feces esteguen totes seques e arses; e que l'humit unctuous sia tot sublevat axi com a anima en la substancia de l'esperit.

*Cipher note: III.1.0 belongs to Part III (Liber Mercuriorum). The Part III letter cipher applies: B=simple water, C=simple red sulphur, D=simple dissolved gold, E=compound red water, F=compound red sulphur, G=compound dissolved gold. No letter codes appear explicitly in this particular sub-recipe.*

**Translation:** Son, you must understand the operations to create our quicksilvers. Take mercurial liquor (lunaria) as much as you want, and separate the elements by distillation. First separate the phlegmatic water where the spirit lies mortified. Continue bath distillation until you see the animated water begin to burn — that is the sign the phlegm is out. Divide that into two parts: one to create the mercuries, from the other extract elements without combustion preserving the properties of sulphur and quicksilver. Put the animated water over the feces, mount the alembic with receptor, light the composed sawdust fire. Continue until everything distillable is distilled by equal fire — do this in balneum mariae. Then put on dry ash-fire with continued sawdust; distill the oil. At the end let the material cool with the vessel. Return the first liquor over the feces and reiterate distillation until the feces are dry and burned, and the unctuous moisture is all raised like a soul in the substance of the spirit.

The recipe is a multi-phase pipeline: phlegm separation (water bath), animated-water collection (burning sign), two-way split, feces cohobation with animated water (balneum then ash-fire), oil distillation on ash-fire, cooling period, reiteration until dry. This is the master procedure for making mercuries — all subsequent III.x recipes reference it.

---

## Token Dictionary

The table below shows how Voynich tokens are read in this cold read. The "Workshop Reading" column gives the operational meaning validated against Catalan recipe text (PT-013/014/015) and distributional evidence (B Operational Dictionary). The "Atoms" column shows the underlying structural decomposition (C1394 HEAD+MOD+TERM model). Readers unfamiliar with the atom system can ignore the Atoms column entirely — the Workshop Reading is self-sufficient.

**How tokens work:** Each token has a PREFIX (what you're acting on) and a BODY (what you're doing). The prefix selects an operational domain; the body atoms specify the action within that domain.

| Prefix | Domain | Workshop sense |
|--------|--------|---------------|
| qo | Heat source | Managing the fire or furnace |
| ch | Active test | Checking state — finger test, color check, viscosity |
| sh | Passive watch | Observing without intervention — watching distillate, fumes |
| ok | Vessel | Managing the vessel or apparatus temperature |
| ot | Transfer rate | Monitoring output — drip rate, melt flow |
| ol | Continue | Maintaining current state without change |
| da | Material | Adding or handling substances |
| sa | Scaffold | Supporting infrastructure for iterative cycling |
| lk | Equipment | Furnace or equipment management |
| lch | Equipment check | Verify apparatus — seals, receiver, furnace |
| ke | Steady-state | Thermal equilibrium check |
| pch | Stage-test | Stage opening test — paragraph header |
| te | Transfer | Transfer operation |
| al | At-rest | Product has reached stable state |
| ka | Heat-yield | Heat until yield point |

The body is built from **atoms** — single characters with functional meanings. These compose left to right: the first atom (HEAD) sets the action domain, subsequent atoms (MOD) modify or parametrize it, and the final atom (TERM) closes the instruction. Key atoms:

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

So `qo` + `k.e.d.y` reads compositionally as: *at the fire (qo), heat (k), stabilize (e), mark (d), done (y)* — a single heat application with stabilization, executed and closed. Across 10 matched folios, this consistently appears where the recipe says to maintain the fire at a steady level, giving the workshop reading **"maintain current fire level."**

When `e` doubles (`k.e.e.d.y`), the extra stabilization encodes gentler, more sustained heat — balneum mariae (water-bath) temperature rather than direct fire. When the terminal changes from `y` (done) to `a.i.n` (yield, iterate, bind), the instruction shifts from a single completed action to sustained cycling: **"keep heating through repeated cycles."**

**Key tokens on this folio:**

| Token | Prefix | Atoms | Compositional reading | Workshop Reading | Source |
|-------|--------|-------|-----------------------|-----------------|--------|
| qokedy | qo | k.e.d.y | fire: heat, stabilize, do, done | Maintain current fire level | PT-013 (10/10) |
| qokeedy | qo | k.e.e.d.y | fire: heat, stabilize x2, do, done | Gentle fire — balneum / water-bath level | PT-013 (10/10) |
| qokain | qo | k.a.i.n | fire: heat, yield, iterate, bind | Sustained cyclic heating | PT-013 (10/10) |
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate x2, bind | Deep sustained cyclic heating — sealed apparatus | PT-013 (15/15) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target — heat stage done | PT-013 (10/10) |
| qokeey | qo | k.e.e.y | fire: heat, stabilize x2, done | Establish gentle heat state | B Dict D1 |
| qokey | qo | k.e.y | fire: heat, stabilize, done | Brief heat application | B Dict D2 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qokeeey | qo | k.e.e.e.y | fire: heat, stabilize x3, done | Extremely gentle heat — lightest thermal touch | Compositional |
| qokchdy | qo | k.c.h.d.y | fire: heat, adjust, watch, do, done | Adjust fire while watching | B Dict D2 |
| qotedy | qo | t.e.d.y | fire: transfer, stabilize, do, done | Execute a heat-driven transfer | B Dict D1 |
| qoteedy | qo | t.e.e.d.y | fire: transfer, stabilize x2, do, done | Gentle heat-driven transfer | B Dict D2 |
| qotam | qo | t.a.m | fire: transfer, yield, final | Transfer finalized | Compositional |
| qotaiin | qo | t.a.i.i.n | fire: transfer, yield, iterate x2, bind | Sustained iterative heat transfer | B Dict D2 |
| qokam | qo | k.a.m | fire: heat, yield, final | Heat stage finalized | Compositional |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dain | da | i.n | material: iterate, bind | Bind material into the cycle | B Dict D1 |
| daiin | da | i.i.n | material: iterate x2, bind | Start a new cycle — initiate next loop | B Dict D0 |
| dal | da | l | material: hold/state | Carefully collect or place material | B Dict D0 |
| daldy | da | l.d.y | material: hold, do, done | Careful placement, seal, done | Compositional |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state — verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| cheedy | ch | e.e.d.y | test: stabilize x2, do, done | Check gentle cooling | B Dict D2 |
| cheol | ch | e.o.l | test: stabilize, arrange, state | Check arrangement is stable | B Dict D2 |
| chol | ch | o.l | test: arrange, state | Check arrangement | B Dict D2 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chcthy | ch | c.t.h.y | test: adjust, transfer, watch, done | Watch the transfer (active) | B Dict D2 |
| checkhy | ch | e.c.k.h.y | test: stabilize, adjust, heat, watch, done | Check heat level during cooling | B Dict D2 |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly — quick passive check | B Dict D1 |
| sheey | sh | e.e.y | watch: stabilize x2, done | Extended gentle observation | B Dict D2 |
| sheedy | sh | e.e.d.y | watch: stabilize x2, do, done | Extended passive observation of gentle process | B Dict D2 |
| okeey | ok | e.e.y | vessel: stabilize x2, done | Vessel temperature settled | B Dict D2 |
| okeedy | ok | e.e.d.y | vessel: stabilize x2, do, done | Vessel at gentle balneum temperature | B Dict D1 |
| okedy | ok | e.d.y | vessel: stabilize, do, done | Check vessel during cooling | B Dict D1 |
| okaiin | ok | a.i.i.n | vessel: yield, iterate x2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal vessel for a processing cycle | B Dict D1 |
| okar | ok | a.r | vessel: yield, respond | Vessel: note the yield | B Dict D3 |
| okal | ok | a.l | vessel: yield, state | Vessel reached target state | B Dict D2 |
| otaiin | ot | a.i.i.n | drip-rate: yield, iterate x2, bind | Monitor drip rate through extended cycles | B Dict D2 |
| oteey | ot | e.e.y | drip-rate: stabilize x2, done | Drip rate settled at gentle level | B Dict D2 |
| otam | ot | a.m | drip-rate: yield, final | Transfer monitoring finalized | Compositional |
| olkeedy | ol | k.e.e.d.y | continue: heat, stabilize x2, do, done | Continue gentle heating | B Dict D2 |
| saiin | sa | i.i.n | scaffold: iterate x2, bind | Begin extended binding iteration cycle | B Dict D1 |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| keedy | ke | e.d.y | steady-heat: stabilize, do, done | Steady-state thermal check | B Dict D2 |
| lchedy | lch | e.d.y | equipment-check: stabilize, do, done | Check apparatus (seals, receiver, furnace) | PT-013 (8/10) |
| lkeeedy | lk | e.e.e.d.y | equipment: stabilize x3, do, done | Very gentle equipment cooldown | Compositional |
| lkeedy | lk | e.e.d.y | equipment: stabilize x2, do, done | Equipment at gentle operating temperature | B Dict D2 |
| am | -- | a.m | yield, final | Phase done — yield result and close | B Dict D0 |
| ol | -- | o.l | arrange, hold | Hold steady | B Dict D0 |
| aiin | -- | a.i.i.n | yield, iterate x2, bind | Yield into the next processing cycle | B Dict D0 |
| pchedy | pch | e.d.y | stage-test: stabilize, do, done | Stage-test: verify state (paragraph opener) | B Dict D2 |

**Observation MIDDLEs** — specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| cfh | c.f.h | adjust, flag, watch | Flag-check: is a critical threshold being met? |

---

## The Folio

**f112v:** 415 tokens, 47 lines, 15 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|---------------------|
| P1 | 1-6 | 52 | 1 | 0.81 | -- | Phlegm separation: bath distillation to remove phlegmatic water |
| P2 | 7-10 | 28 | 1 | 0.64 | -- | Animated water emerges: watch for the burning sign |
| P3 | 11-14 | 35 | 2 | 0.74 | 1 cfh | Distill animated water apart: collect the spirit fraction |
| P4 | 15-19 | 45 | 1 | 0.91 | -- | Two-way split: divide and prepare elements without combustion |
| P5 | 20-24 | 42 | 0 | 0.93 | -- | Balneum phase: sustained water-bath distillation over feces |
| P6 | 25-26 | 17 | 0 | 1.41 | -- | Deep cooling: let the material cool with the vessel |
| P7 | 27-29 | 28 | 0 | 1.14 | -- | Transition to ash-fire: equipment and heat regime change |
| P8 | 30 | 10 | 1 | 0.90 | -- | Mount alembic: apparatus setup with material load |
| P9 | 31 | 5 | 0 | 0.60 | -- | Light the fire: brief ignition step |
| P10 | 32-34 | 28 | 0 | 1.11 | -- | Sawdust fire: equal-fire distillation begins |
| P11 | 35 | 6 | 0 | 0.67 | -- | Dry ash-fire: switch to stronger direct heat |
| P12 | 36 | 10 | 0 | 0.90 | -- | Oil distillation: distill the oil on ash-fire |
| P13 | 37-38 | 23 | 1 | 0.30 | -- | Cool and return: let material cool, return liquor over feces |
| P14 | 39-41 | 24 | 2 | 0.58 | 1 ckh | Reiteration: repeat distillation with heat-level check |
| P15 | 42-47 | 62 | 1 | 0.42 | 1 cth | Final reiteration: continue until feces are dry and burned |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation, deliberate cooling). Lower values = more sustained uninterrupted heat (sustained fire, autonomous cycling). A value near zero means almost no cooling operation at all (vessel handling, material movement, or intense dry fire).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1-6, 52 tokens) — Phlegm Separation

**Recipe says:** "First separate the phlegmatic water where the spirit lies mortified. Continue bath distillation until you see the animated water begin to burn."

The opening step: take lunaria and separate the phlegmatic (inert, watery) fraction by sustained water-bath distillation.

**What the tokens say:**

The e-depth is 0.81 — heavy cooling intervention, characteristic of active water-bath distillation where the operator is constantly managing vessel temperature and condensation.

The prefix distribution is dominated by vessel management: `ok` x9 (vessel operations), `qo` x8 (fire management), `ot` x5 (transfer-rate monitoring). This is an apparatus-heavy paragraph — the operator is setting up and running a distillation, managing every component simultaneously.

L1 opens with `keeoal` ("steady-state: establish arrangement") and vessel operations. The line has heavy `ok/ot` tokens — managing vessel temperature and transfer rate. The single fire token `qor` ("fire: respond") is brief; the emphasis is on the apparatus, not the heat source. This fits the opening of a water-bath distillation where the bath is already warming and the focus is on apparatus setup.

L2 shifts to active fire management: `qokeey` ("establish gentle heat"), `qokal` ("fire reached target"). Then vessel operations: `okain` ("seal vessel for a cycle"), `okeol` ("vessel arranged and cooling"). The bath is reaching operating temperature. The line closes with `oraiin` ("yield into extended iterative cycle") — the sustained distillation process is beginning.

L3 opens with `qokeeor` ("gentle heat: arrange and respond") — an unusually complex fire token with double stabilization. Then observation: `sheey` ("extended gentle observation"), `sheedy` ("extended passive observation"). The operator is watching the distillate. `qotam` ("transfer finalized") at line end — a transfer event completes.

L4: `shody` ("watch: arrange, do, done") and then `qokeedy` x2 ("gentle fire — balneum level") — two consecutive balneum-heat tokens. The bath distillation is running at steady gentle heat. `qoky` ("cease heating") at line end, then `am` ("phase done") — a sub-step concludes.

L5-L6 are scaffold-heavy: `sain`, `saiin` ("begin binding iteration cycles"), `okaiin` ("extended sealed processing"). The distillation is cycling through iterative passes. The paragraph's single `daiin` ("start a new cycle") on L5 is the initial material loading — the lunaria being charged into the apparatus.

**Match assessment:** Coherent. An apparatus-heavy water-bath distillation paragraph with high e-depth (0.81), dominated by vessel and transfer-rate operations, gentle balneum heat (double `qokeedy` on L4), and iterative scaffold tokens. Maps directly to "continue bath distillation" for phlegm separation.

---

### P2 (Lines 7-10, 28 tokens) — Animated Water Emerges

**Recipe says:** "Until you see the animated water begin to burn. And that distill apart; and when all that can be distilled by that heat you have received, the phlegm will be out, as the sign of its burning manifests."

The critical observation phase: watch for the burning sign that indicates the phlegm is exhausted and the animated water is coming through.

**What the tokens say:**

e-depth drops to 0.64 — less active cooling than P1. The distillation is now running and the operator's role shifts from managing apparatus to monitoring product.

The prefix distribution shifts dramatically: `ok` x6 (vessel monitoring, not setup) with heavy `ot` x4 (transfer-rate watching). The operator is watching what comes out of the alembic — drip rate, character, signs of burning.

L7 opens with `pcheokeey` (stage-test: complex arrangement and heat check) — the paragraph-opening test token. Then `qoteedy` ("gentle heat-driven transfer") — the distillate is being transferred at gentle heat. The line's `oteor` ("drip-rate: stabilize and arrange, respond") is monitoring the output.

L8 is almost entirely vessel and transfer monitoring: `okor` ("vessel: respond"), `otaiin` ("monitor drip rate through extended cycles"), `okal` ("vessel at target state"), `otal` ("transfer-rate: yield, state"). These are drip-watching tokens — the operator is monitoring the output stream, waiting for the burning sign. `chekaiiin` ("quality check: heat, yield, iterate x3, bind") closes the line — an extended quality verification. This is the moment of recognition: is the animated water starting to burn?

L9 continues the monitoring with `okaiin` ("extended sealed processing") and `otaiin` ("transfer monitoring through cycles"). Then `qokchdy` ("adjust fire while watching") — the operator adjusts the fire while watching the critical transition. A `cheekain` ("check: gentle heat, yield, iterate, bind") quality verification runs alongside.

L10: `dain` ("bind material into cycle") — the single material addition, followed by `sheey` ("extended gentle observation") and `okchedy` ("vessel: adjust, watch, cool, do, done"). The animated water fraction is being collected into a separate receiver while the operator watches.

One `chekar`-class quality check in this paragraph — consistent with the recipe's emphasis on recognizing "the sign of its burning."

**Match assessment:** Coherent. A monitoring-heavy paragraph with transfer-rate dominance and a quality check. The shift from apparatus-setup (P1) to product-watching (P2) matches the recipe's "until you see the animated water begin to burn."

---

### P3 (Lines 11-14, 35 tokens) — Distill Animated Water Apart

**Recipe says:** "And that distill apart. Divide into two parts: one to create the mercuries, from the other extract elements without combustion."

Collect the animated water and prepare for the two-way split.

**What the tokens say:**

e-depth is 0.74 — intermediate between P1's heavy distillation and P2's monitoring. Active distillation is happening but at a controlled pace.

This paragraph has the folio's only **cfh** (flag-check) observation MIDDLE, on L11: `chcfhy` ("check: adjust, flag, watch, done"). The flag-check encodes a threshold test — is a critical condition being met? In the recipe, this is the moment of division: the operator must determine when the animated water fraction is complete before splitting the product. The cfh marks that critical decision point.

L11 opens with `tchor` ("transfer: arrange, respond") and cycles through `oteeey` ("drip-rate: very gentle stabilization") and `qokey` ("brief heat application"). The gentleness of the thermal tokens — triple-e on the transfer and brief single-e on the heat — encodes careful, conservative distillation. The recipe says "without combustion" for the second fraction; the operator is being cautious.

L12: Two `daiin` ("start a new cycle") — two material additions. The recipe says to divide into two parts; two material-handling events on L12 match a physical division operation. Between them: `sheeol` ("observe arrangement at gentle state"), `qokeedy` ("gentle balneum heat"), `qochaiin` ("heat: adjust, watch, yield into iterative cycle"). Gentle heat with continuous monitoring as the split happens.

L13 opens with `dcheoty` (material-transfer operation) and has two `chedy` ("check the state") active verifications. The checks verify the quality of each fraction. Then `qokaiin` ("deep sustained cyclic heating") — a sealed-apparatus heating pass to finalize the separation. `otam` ("transfer monitoring finalized") closes the line.

L14 is scaffold and iteration: `sain` ("begin iteration cycle"), `ain`/`am` ("yield and close"). The paragraph wraps up with `qokeedy` ("gentle balneum heat") — the distillation of the animated water is complete.

**Match assessment:** Coherent. The cfh flag-check marks the critical division point. Two material additions on L12 match the two-way split. Conservative thermal profile (gentle tokens, cautious heat) matches "without combustion." The paragraph transitions from active collection to closure.

---

### P4 (Lines 15-19, 45 tokens) — Preparing the Feces Cohobation

**Recipe says:** "Put the animated water over the feces... Mount the alembic with receptor, light the composed sawdust fire... Continue until everything distillable is distilled by equal fire — do this in balneum mariae."

Setup for the main distillation phase: animated water goes back onto the feces for balneum distillation.

**What the tokens say:**

e-depth jumps to 0.91 — the highest yet. This is intense distillation with heavy cooling management, consistent with balneum mariae where the operator must constantly manage the water-bath temperature.

The prefix distribution is dominated by `qo` x14 (fire management) and `ch` x9 (active testing). This is the most fire-intensive paragraph so far — the operator is running a sustained balneum distillation with continuous quality checking.

L15 opens with `pchodain` (stage-test with material arrangement and iterative binding) — material is being loaded. Then `okeedy` ("vessel at gentle balneum temperature"), `qokeedy` ("gentle fire"), `olkeedy` ("continue gentle heating"), `qokain` ("sustained cyclic heating"). Four consecutive gentle-heat tokens followed by sustained cycling. The balneum is running at full capacity.

L16: `saiin` ("begin extended iteration cycle") opens, followed by observation: `sheey` ("gentle observation"). Then `qoteedy` ("gentle heat-driven transfer"), `qokey`, `qokeey` x2 — a dense cluster of fire management. The distillate is being collected under gentle balneum heat.

L17 shifts to monitoring: `daiin` ("start a new cycle") opens with material handling, then five consecutive `ch`-prefix tokens: `cheeir`, `cheedy`, `chykeedy`, `chdaiin`, `cheedy`. Five active checks in succession on a single line — the operator is verifying, re-verifying, and re-checking. The recipe says "by equal fire" — this dense checking cluster encodes the operator's vigilance in maintaining constant heat.

L18: `qokeedy` ("gentle balneum heat"), `qokeeey` ("extremely gentle heat"), `qokeeody` ("gentle heat arranged and executed"). The heat tokens increase in gentleness — triple-e on `qokeeey`. Then `qotam` ("transfer finalized") — a distillation pass completes.

L19: `sarain`, scaffold tokens, `qoeeey` ("fire: extremely gentle cooling"), `qoteo` ("fire: transfer, cool, arrange"). The paragraph winds down with extremely gentle operations and scaffold management.

**Match assessment:** Coherent. The highest e-depth on the folio (0.91) encodes intense balneum-mariae distillation. The fire-dominance (14 qo-prefix tokens) and dense checking (5 consecutive ch-tokens on L17) match "continue until everything distillable is distilled by equal fire."

---

### P5 (Lines 20-24, 42 tokens) — Sustained Balneum Distillation

**Recipe says:** "Continue until everything distillable is distilled by equal fire — do this in balneum mariae."

The sustained running of the water-bath distillation over the feces.

**What the tokens say:**

e-depth peaks at 0.93 — the second-highest on the folio. Even more cooling intervention than P4. The balneum is at full operation.

**Zero material additions.** Once the animated water is loaded onto the feces, the process runs without new material — exactly as the recipe describes. The operator's job is to maintain conditions, not add anything.

The prefix distribution is dominated by `ch` x12 (active testing) and `qo` x9 (fire management). This is a checking-and-heating paragraph — pure process management.

L20: `qokedy` ("maintain fire level"), `qotaiin` ("sustained iterative heat transfer"), `chocthedy` ("check: arrange, transfer, watch, cool, do, done"). An active transfer is happening under continuous monitoring.

L21: `chekain` ("quality check: heat, yield, iterate, bind") — a quality verification. Then `qoeedy` ("fire: gentle cooling"), `qokaiin` ("deep sustained cyclic heating"), `shedy` ("watch the distillate"). The push-pull between gentle cooling and sustained heating encodes the balneum's operating characteristic: heat the bath, let it stabilize, watch the output.

L22-L23: More checking tokens (`cheol`, `chedy`, `chedain`, `cheedaiin`) interspersed with gentle fire management (`qokeey`, `qokeedy`). The checking intensifies as the paragraph proceeds.

L24 closes with `qokeedy` ("gentle balneum heat") followed by a sequence of deeply cooling tokens. The paragraph ends with the balneum at full gentle operation.

One `chekar`-class quality check — the ongoing verification that distillation is proceeding correctly.

**Match assessment:** Coherent. Zero material additions, peak e-depth (0.93), check-dominated prefix distribution, and sustained cycling tokens encode an autonomous balneum distillation running until completion.

---

### P6 (Lines 25-26, 17 tokens) — Cooling Period

**Recipe says:** "At the end of the distillation let the material cool with the vessel."

A deliberate cooling step between the balneum phase and the ash-fire phase.

**What the tokens say:**

e-depth explodes to **1.41** — by far the highest on the folio and among the highest seen on any cold-read folio. This is extreme cooling. The `e` atoms outnumber all other atoms combined.

**Zero material additions, zero dar.** Nothing is being added — the operator is simply letting everything cool.

The prefix distribution: `ch` x7 (active testing), `qo` x4 (fire management). But look at the heat tokens: `qokeeey` ("extremely gentle heat — lightest thermal touch"), `qokeey` ("establish gentle heat"), `qokeedy` ("gentle balneum heat"). Even the fire tokens encode gentleness and cooling. And `lkeeedy` ("equipment: very gentle cooldown") — triple-e on the equipment, the furnace itself cooling down.

L25: `pchdaiin` (stage-test: material arrangement, iterative binding), `shedy` ("watch the state"), `otaiin` ("monitor drip rate through cycles"), `cheedy` ("check gentle cooling"), `qokeeey` ("extremely gentle heat"), `lkeeedy` ("very gentle equipment cooldown"). The sequence is: watch, monitor output, check cooling, barely heat, let equipment cool. The apparatus is being deliberately brought down to ambient temperature.

L26: `checkhey` and `checkhy` — two heat-level checks in succession. "Is the fire still too hot? Check again." Then `cheeol` ("check: gentle stabilization of arrangement"), `qokeedy` ("gentle balneum heat"), `qoteosam` ("transfer: cool, arrange, sequence, yield, final"). The final heat-related operation on L26 is a sequenced transfer finalization — the last distillate is being collected as the system cools.

**Match assessment:** Strongly coherent. The e-depth of 1.41 directly encodes the recipe's "let the material cool with the vessel." Dual heat-level checks on L26 match the operator verifying that cooling is complete. The absence of material additions confirms this is a passive cooling phase.

---

### P7 (Lines 27-29, 28 tokens) — Transition to Ash-Fire

**Recipe says:** "Then put on dry ash-fire with continued sawdust."

Transition from balneum mariae to the stronger ash-fire regime.

**What the tokens say:**

e-depth remains high at 1.14 — still heavily cooling, but dropping from P6's 1.41. The system is transitioning from deep cooling back toward active operation.

**Zero material additions.** This is a regime change, not a material-handling step.

The prefix distribution: `qo` x8 (fire management is now dominant), `sh` x3 (passive watching), `ok` x2 (vessel), `ke` x2 (steady-state checks). The fire prefix returns to dominance — the operator is re-establishing heat, but differently.

L27: `pchodain` (stage-test: material arrangement), then `teeedy` ("transfer: gentle cooling done"), `qoeey` ("fire: gentle cooling"), `okeedy` ("vessel at balneum temperature"), `qokeear` ("fire: gentle heat, yield, respond"). The heat tokens are exploring a new regime — note the variety. Instead of the repetitive `qokeedy` of balneum operation, we see `qokeear`, `qotedy` — the operator is testing different heat levels as ash-fire conditions are established.

L28: `shey` ("watch briefly"), then `qoiin` ("fire: iterate, iterate, bind") — a pure iterative fire token without any heat atom, unusual. The fire is being cycled, not temperature-managed. `qokeeey` ("extremely gentle heat") appears — but alongside `ykeey` x2 and `qoeey`, all deeply cooling. The transition from balneum to ash-fire involves carefully warming a cooled system.

L29: `sheey` ("extended gentle observation"), `qoeekain` ("fire: gentle cooling, heat, yield, iterate, bind") — a complex ramp-up token. The observation and progressive fire management encode the gradual transition to ash-fire operation.

**Match assessment:** Coherent. A fire-regime transition paragraph with zero material additions, high-but-declining e-depth, and progressive fire exploration. Maps to the recipe's shift from balneum mariae to "dry ash-fire with continued sawdust."

---

### P8 (Line 30, 10 tokens) — Mount the Alembic

**Recipe says:** "Mount the alembic with receptor."

A brief apparatus setup step.

**What the tokens say:**

Only 10 tokens on a single line. The paragraph opens with `polor` ("stage-opening: state, arrange, respond") — a positional/arrangement opener.

Key sequence: `sheedy` ("extended passive observation") and `okeedey` ("vessel: gentle cooling, do, done") — observe the apparatus, verify vessel temperature. Then `sal` ("scaffold: hold state"), `aiin` ("yield into cycle"), `sheedar` ("observe: gentle cooling, material, respond") — observe a material response during cooling.

The single material addition: `dalkedy` ("material: careful placement, heat, stabilize, done") — carefully placing something with heat management. Mounting the alembic involves physical apparatus work, and the careful-placement token captures that.

`qopchedy` ("fire: pause, adjust, watch, cool, done") — the fire is paused while apparatus is being handled. You do not run the fire while mounting the alembic.

**Match assessment:** Coherent. A brief apparatus-setup paragraph with paused fire, careful material placement, and observation. Maps to "mount the alembic with receptor."

---

### P9 (Line 31, 5 tokens) — Light the Fire

**Recipe says:** "Light the composed sawdust fire."

The briefest paragraph: ignition.

**What the tokens say:**

Only 5 tokens on a single line — the shortest paragraph on the folio. e-depth drops to 0.60 — significantly less cooling than the preceding paragraphs. Heat is returning.

```
L31:  tar  aiin  okeear  oteody  arar
```

`tar` ("transfer: respond") — a transfer initiation. `aiin` ("yield into cycle") — the process enters its next phase. `okeear` ("vessel: gentle cooling, yield, respond") — the vessel responds as heat is applied. `oteody` ("drip-rate: cool, arrange, do, done") — transfer monitoring as the fire lights. `arar` ("yield, respond") — note the result.

The entire sequence reads: initiate transfer, yield into cycle, vessel responds, monitor transfer, note result. Five tokens for a single physical action: lighting the fire and watching the system respond.

**Match assessment:** Coherent. A minimal paragraph encoding a single decisive action. The sharp e-depth drop from P8 (0.90) to P9 (0.60) marks the return of active heating.

---

### P10 (Lines 32-34, 28 tokens) — Equal-Fire Distillation

**Recipe says:** "Continue until everything distillable is distilled by equal fire."

The sawdust fire runs at constant intensity while distillation proceeds.

**What the tokens say:**

e-depth rises to 1.11 — back to heavy cooling management. The distillation is running actively.

The prefix distribution: `ch` x10 (active testing dominates), `qo` x5 (fire management), `ok` x2, `ot` x2. Testing is the primary activity — the operator is continuously verifying.

L32 features two unusual tokens: `qopchedy` and `qopcheey` — both contain the `pch` (pause-check) atom within the fire prefix. These encode paused fire adjustment with checking — the operator pauses to verify the fire is equal (constant) before letting it continue. The recipe explicitly requires "equal fire" — these pause-and-check tokens encode that vigilance.

L33: `qokedy` ("maintain fire level") and `qokeedy` ("gentle balneum heat") side by side — standard and gentle heat management. Then `chedaiin` ("check: cool, do, yield into iterative cycle") — verification during the sustained cycling. `okeeedy` ("vessel: very gentle cooling") — triple-e on the vessel, indicating extensive cooling management.

L34: `checkhy` ("check heat level during cooling") — a heat-level check. Then `chkaiin` ("test: heat, yield into deep cycle") and `checkhol` ("check heat: arrange, hold") — persistent heat monitoring. The paragraph closes with `chdam` ("test: do, yield, final") — the testing phase finalizes.

**Zero material additions.** The distillation runs without intervention — equal fire, equal output, autonomous cycling.

**Match assessment:** Coherent. Check-dominated (10 ch-prefix tokens in 28), zero material additions, pause-and-verify fire tokens. The operator's sole job is maintaining equal fire — and the token distribution reflects exactly that.

---

### P11 (Line 35, 6 tokens) — Switch to Dry Ash-Fire

**Recipe says:** "Then put on dry ash-fire with continued sawdust; distill the oil."

A brief regime change: from equal balneum-style fire to stronger direct ash-fire.

**What the tokens say:**

Only 6 tokens on a single line. e-depth drops to 0.67 — a notable decline from P10's 1.11. Less cooling means more sustained heat. The operator is increasing the thermal intensity.

```
L35:  pched  shedain  qokaiin  okar  chedy  checkhy
```

`pched` (stage-test: cool, do) — the stage opener. `shedain` ("observe: cool, do, yield, iterate, bind") — watch the material respond to the new heat level. `qokaiin` ("deep sustained cyclic heating") — the first deep-cycle heating token since P5. After paragraphs of gentle/equal fire, the system shifts to aggressive sustained heat.

`okar` ("vessel: yield, respond") — the vessel responds to the new regime. `chedy` ("check the state") and `checkhy` ("check heat level during cooling") — state verification and a heat-level check. The operator verifies the fire is at the correct (higher) level.

**Match assessment:** Coherent. A brief regime-change paragraph. The e-depth drop from 1.11 to 0.67 and the appearance of `qokaiin` (deep sustained heating) mark the transition to ash-fire. The heat-level check confirms the operator is verifying the new fire intensity.

---

### P12 (Line 36, 10 tokens) — Oil Distillation

**Recipe says:** "Distill the oil."

A specific product collection: the oil fraction, distilled under ash-fire conditions.

**What the tokens say:**

10 tokens on a single line. e-depth is 0.90 — a rise from P11's 0.67. Active distillation is happening again, with the cooling management characteristic of collecting a distillate.

```
L36:  tchede  okeey  lky  shedaiiin  chdy  qokeedy  cheky  lkedy  qotedy  raram
```

`tchede` ("transfer-test: cool, do, cool") — a transfer initiation with cooling management. `okeey` ("vessel temperature settled") — the vessel is at operating temperature. `lky` ("equipment: done") — equipment is ready.

`shedaiiin` ("observe: cool, do, yield, iterate x3, bind") — extended observation through multiple iterative passes. The oil distills slowly through repeated cycles — this is the patient observation of a slow distillation.

`qokeedy` ("gentle balneum heat") and `qotedy` ("execute heat-driven transfer") — the fire is operating and driving the transfer. `cheky` ("check: cool, heat, done") — a thermal verification.

The paragraph closes with `raram` ("yield, final") — the oil fraction is collected and the step concludes.

One `chekar`-class quality check — verifying the oil product.

**Match assessment:** Coherent. A product-collection paragraph with active distillation (e-depth 0.90), extended observation (`shedaiiin` with triple iteration), heat-driven transfer, and quality verification. Maps to "distill the oil" under ash-fire conditions.

---

### P13 (Lines 37-38, 23 tokens) — Cool and Return Liquor

**Recipe says:** "At the end of the distillation let the material cool with the vessel. Then return the first liquor over the feces."

The pivotal step: cool everything down, then begin the cohobation reiteration.

**What the tokens say:**

e-depth crashes to **0.30** — by far the lowest on the folio. After P6's extreme cooling (1.41), this is the thermal opposite: almost no cooling atoms because the operation is primarily material handling and process arrangement, not thermal management. The operator is moving material, not managing heat.

The prefix distribution: `ch` x5 (testing), `qo` x3 (fire), but also `ot` x2 (transfer monitoring), `sa` x1 (scaffold), `sh` x1, `da` x1. Material handling and transfer monitoring are prominent.

L37: `teedal` ("transfer: cool, do, yield, state") — a cooled transfer. `sain` ("begin iteration cycle") — the reiteration scaffold is set up. `ar` ("note the yield") x2 — noting what was produced. `otaiin` ("monitor drip rate through extended cycles"), `shedy` ("watch the state") — monitoring the apparatus.

The critical fire sequence on L37: `qokedaiin` ("fire: heat, cool, do, yield into deep cycle"), `qokaiin` ("deep sustained cyclic heating"), `qokam` ("heat stage finalized"). This three-token fire sequence tells the story: start the heat, sustain the cycle, finalize. The reiteration is being initiated.

L38: `ar` ("note the yield") opens, then `okchey` ("vessel: adjust, watch, cool, done") — the vessel is being adjusted. `chedy` ("check the state"), `chol` ("check arrangement") — state verification. `otaiin` ("monitor drip rate") and `chedar` ("check: cool, do, yield, respond") — transfer monitoring continues. The paragraph closes with `dain` ("bind material into cycle") — the single material addition. The "first liquor" is being returned over the feces.

**Match assessment:** Coherent. The e-depth crash to 0.30 encodes the shift from thermal operation to material handling — "let the material cool" followed by "return the first liquor over the feces." The single dar at paragraph end matches the cohobation: returning one fraction over the residue. The reiteration scaffold (`sain`) marks the start of the cycling process.

---

### P14 (Lines 39-41, 24 tokens) — Reiteration

**Recipe says:** "Reiterate your distillation as already described, until the feces are completely dry and burned."

Repeat the entire distillation sequence over the returned feces.

**What the tokens say:**

e-depth rises to 0.58 — moderate, indicating active but not intense distillation. The reiteration runs at a measured pace.

This paragraph has the folio's only **ckh** (heat-level check) observation MIDDLE, on L40: `chckhy` ("check: adjust, heat, watch, done"). The operator is actively checking the fire level — making sure the reiterated distillation runs at the correct intensity. This is the only explicit heat-level check on the entire folio, and it falls exactly where the recipe says to reiterate carefully.

The prefix distribution: `ch` x9 (active testing dominates), `da` x2 (two material additions), `qo` x2, `ok` x2, `ot` x2. Testing dominates because the reiteration requires constant verification.

L39: `teodarody` ("transfer: material, respond, arrange, do, done") — a material-involving transfer. `okaiin` ("extended sealed processing"), `otam` ("transfer monitoring finalized"), then `qoteey` ("gentle heat-driven transfer") and `qotain` ("heat-driven transfer: yield, iterate, bind") — the transfer sequence for the reiteration.

L40: `lchedy` ("check apparatus: seals, receiver, furnace") — an equipment check. This is the PT-013 validated token for verifying apparatus integrity before a critical step. Then the `chckhy` heat-level check. After verification: `daiin` x2 ("start a new cycle") — two material additions. Material is being loaded for the reiteration.

L41: `ykeedain` — a deeply cooling material-binding token. Then `checkhey` ("check heat level during cooling") — another heat verification. The paragraph closes with `chol` ("check arrangement") — final state check.

**Match assessment:** Coherent. The equipment check (`lchedy`) and heat-level check (`chckhy`) on L40 encode the operator verifying everything before reiteration. Two material additions match the return of liquor over feces. The check-dominated prefix distribution (9 ch-tokens in 24) reflects the careful verification required for reiterated distillation.

---

### P15 (Lines 42-47, 62 tokens) — Final Reiteration and Completion

**Recipe says:** "Continue until the feces are completely dry and burned, and the unctuous moisture is all raised like a soul in the substance of the spirit."

The extended final phase: sustained reiteration until the process is complete.

**What the tokens say:**

P15 is the largest paragraph — 62 tokens, 15% of the entire folio. The final reiteration is the most operationally demanding part: run until complete, with no predetermined endpoint.

e-depth drops to 0.42 — among the lowest on the folio. Low cooling means sustained, uninterrupted heat. The feces must be dried and burned — this requires persistent strong heat, not gentle balneum cooling.

The prefix distribution is broad: `ch` x14 (testing), `none` x15 (unprefixed structural tokens), `ot` x6 (transfer monitoring), `qo` x4 (fire), `al` x4 (at-rest), `ok` x3 (vessel), `ka` x3 (heat-yield). The breadth reflects a complex extended operation touching every part of the system.

L42: `qokchdy` ("adjust fire while watching") — active fire management. `otechy` ("drip-rate: cool, adjust, watch, done") — monitoring the output with transfer-watch. `qokedy` ("maintain fire level") — standard heat maintenance. `shain` ("watch: yield, iterate, bind") — observation tied to cycling.

L43: Dense arrangement and state tokens: `olkeol` ("continue: heat, cool, arrange, state"), `chol` x2 ("check arrangement"), `alchedy` ("at-rest: adjust, watch, cool, done"). The operator is managing a complex multi-component arrangement during the extended reiteration. `chtal` ("check: transfer, yield, state") — monitoring the transfer product.

L44: `qokchal` ("fire: heat, adjust, watch, yield, state") — a complex fire management token that includes watching and yield assessment. `okal` ("vessel at target state"), `otedar` ("drip-rate: cool, do, yield, respond") — vessel and transfer monitoring.

L44a: A **transfer-watch** (`chcthy` — "watch what's being transferred"). This is P15's observation MIDDLE — the operator is actively watching what comes out of the alembic during the final reiteration. "Is the unctuous moisture fully raised?"

L45: `chokain` ("test: arrange, heat, yield, iterate, bind") — heat cycling with arrangement. `charam` ("test: yield, respond, yield, final") — a terminal quality verification. `daldy` ("material: careful placement, seal, done") — the final material handling. `okaiin` ("extended sealed processing") — the last sealed processing pass.

L47 (final line): `olkaiin` ("continue: heat, yield into deep cycle") — the last sustained heating token. Then `oty` ("transfer: done") and `ary` ("yield: done") — the process closes. The final two tokens both terminate with `y` (done) — the folio's operations are complete.

**Match assessment:** Coherent. P15 dominates the folio's late section with 62 tokens and the lowest e-depth (0.42), encoding sustained dry heat for drying and burning the feces. The transfer-watch on L44a monitors the final product. The broad prefix distribution reflects the operational complexity of the final reiteration. Terminal `y`-atoms on the last line close the folio.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | 0.81 | Active balneum distillation — phlegm separation |
| P2 | 0.64 | Monitoring transition — watching for burning sign |
| P3 | 0.74 | Controlled distillation — collecting animated water |
| P4 | 0.91 | Intense balneum — feces cohobation begins |
| P5 | **0.93** | Peak balneum — sustained autonomous distillation |
| P6 | **1.41** | Deep cooling — let material cool with vessel |
| P7 | 1.14 | Transition — warming from cool toward ash-fire |
| P8 | 0.90 | Apparatus setup — moderate thermal management |
| P9 | 0.60 | Fire ignition — heat returns sharply |
| P10 | 1.11 | Equal-fire distillation — heavy check-and-cool |
| P11 | 0.67 | Regime change to ash-fire — less cooling, more heat |
| P12 | 0.90 | Oil distillation — active product collection |
| P13 | **0.30** | Material handling — cool, return liquor over feces |
| P14 | 0.58 | Reiteration — moderate distillation resumes |
| P15 | 0.42 | Final dry reiteration — sustained heat to burn feces |

The e-depth draws a distinctive three-phase arc:

**Phase I (P1-P5):** Balneum mariae. e-depth ranges 0.64-0.93, peaking at P5. This is the water-bath distillation regime — gentle, sustained, heavily cooled. The recipe's "continue in balneum until everything distillable is distilled."

**Phase II (P6-P12):** Transition and ash-fire. P6 crashes to the maximum (1.41 — deep cooling), then the system gradually transitions to ash-fire through P7-P12. The recipe's "let the material cool" then "put on dry ash-fire."

**Phase III (P13-P15):** Reiteration. e-depth crashes to 0.30 (material handling), then settles low (0.42-0.58). The final paragraphs encode the dry, sustained heat needed to "burn the feces dry." The recipe's "reiterate until the feces are completely dry and burned."

### dar distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 1 | 10% | Initial lunaria loading |
| P2 | 1 | 10% | Animated water collection |
| P3 | 2 | 20% | Two-way split |
| P4 | 1 | 10% | Feces cohobation loading |
| P5 | 0 | 0% | Autonomous balneum cycling |
| P6 | 0 | 0% | Pure cooling (no material) |
| P7 | 0 | 0% | Regime transition (no material) |
| P8 | 1 | 10% | Alembic mounting — apparatus setup |
| P9 | 0 | 0% | Fire ignition (no material) |
| P10 | 0 | 0% | Equal-fire distillation (autonomous) |
| P11 | 0 | 0% | Ash-fire regime change (no material) |
| P12 | 0 | 0% | Oil collection (product out, not in) |
| P13 | 1 | 10% | Return liquor over feces |
| P14 | 2 | 20% | Reiteration material loading |
| P15 | 1 | 10% | Final material handling |

10 total dar, distributed in two clusters:

**Early cluster (P1-P4):** 5 dar (50%) — the setup phase. Load lunaria, collect fractions, split, reload onto feces. The recipe's initial preparation steps.

**Late cluster (P13-P15):** 4 dar (40%) — the reiteration phase. Return liquor over feces, reload for reiteration. The recipe's "return the first liquor over the feces and reiterate."

**Zero-dar gap (P5-P12):** 8 paragraphs with only 1 dar (P8, apparatus mounting). This 8-paragraph stretch is pure autonomous process — distillation, cooling, regime change, and oil collection happen without new material being added. The recipe describes this as continuous operation: "continue until everything distillable is distilled," "let it cool," "distill the oil." No new material enters the system during this stretch.

### Observation MIDDLE distribution

| Para | ckh | cth | cfh | Total | Recipe activity |
|------|-----|-----|-----|-------|-----------------|
| P1-P2 | -- | -- | -- | 0 | Initial distillation and monitoring |
| P3 | -- | -- | 1 | **1** | Flag-check at the critical division point |
| P4-P12 | -- | -- | -- | 0 | Autonomous distillation phases |
| P13 | -- | -- | -- | 0 | Material handling |
| P14 | 1 | -- | -- | **1** | Heat-level check before reiteration |
| P15 | -- | 1 | -- | **1** | Transfer-watch during final collection |

Only 3 observation MIDDLEs across 415 tokens — extremely sparse. This folio uses observation MIDDLEs surgically:

1. **P3 cfh** (flag-check): At the two-way split — the most critical decision point in the recipe. The operator must identify when the animated water fraction is complete.
2. **P14 ckh** (heat-level check): At the start of reiteration — verifying fire intensity before committing to the final cycling.
3. **P15 cth** (transfer-watch): During the final reiteration — watching for the endpoint, "the unctuous moisture all raised."

Each observation MIDDLE marks a point where the recipe demands active operator judgment, not routine monitoring.

---

## Verdict: COHERENT

f112v produces a coherent paragraph-by-paragraph reading against III.1.0 (Lunaria — making mercuries). The folio's 15 paragraphs map to the recipe's multi-phase pipeline without post-hoc adjustment:

1. **Phlegm separation** (P1) — active balneum distillation, apparatus-heavy setup. *Expert note:* `fcheol` on L1 contains the fch atom pattern (C1939: mercury marker), consistent with the recipe opening "take mercurial liquor."
2. **Burning sign** (P2) — monitoring-heavy, transfer-rate watching, quality check
3. **Animated water collection** (P3) — flag-check at the division point, two material additions for the split
4. **Feces cohobation setup** (P4) — peak fire intensity (14 qo-tokens), 5 consecutive checks on L17
5. **Sustained balneum** (P5) — peak e-depth (0.93), zero material additions, autonomous cycling
6. **Cooling** (P6) — extreme e-depth (1.41), zero material additions, dual heat-level checks
7. **Ash-fire transition** (P7) — fire-regime exploration, progressive warming
8. **Alembic mounting** (P8) — brief apparatus setup with paused fire
9. **Fire ignition** (P9) — minimal 5-token paragraph, sharp e-depth drop
10. **Equal-fire distillation** (P10) — check-dominated, pause-and-verify fire tokens
11. **Ash-fire switch** (P11) — regime change, deep sustained heating appears
12. **Oil distillation** (P12) — product collection with extended observation
13. **Cool and return** (P13) — e-depth crash to 0.30, material handling dominant
14. **Reiteration** (P14) — equipment check, heat-level check, material reload
15. **Final reiteration** (P15) — largest paragraph, low e-depth (0.42), transfer-watch, terminal closure

The recipe describes a ~15-operation pipeline and the folio has 15 paragraphs — a near-exact structural correspondence. The e-depth arc captures the recipe's three thermal regimes (balneum, cooling, ash-fire/reiteration) without reference to any individual token gloss. The dar distribution's two clusters (early loading, late reiteration) with a zero-dar autonomous gap match the recipe's process structure. The three observation MIDDLEs fall at exactly the three decision points the recipe demands operator judgment.
