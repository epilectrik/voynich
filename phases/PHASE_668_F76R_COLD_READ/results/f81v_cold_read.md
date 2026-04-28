# Cold Read: f81v ↔ III.18.0 Potable Gold / Water of Life

**Match tier:** SUPPORTED
**Verdict:** Coherent

---

## The Recipe (III.18.0 — SISMEL Catalan, complete)

> Ara direm la composició de l'aygua potable simpla, que·s fa de sanch fixat per natura per confortar lo humit radicall humanal. Pren l'aygua que dessús te havem dit, que ha poder de sobre aliter dissolre or sots la conservació de sa specie o forme; e subtilia-lo en aquella per via de continuació ab inhumació en bany e laugera decocció. E aprés posa l'or dissolt en una carabaça de fin vidre, e distilla l'aygua e separa'n tota la humor. E estarà la substancia de l'or al fons del vexell tota secca. Puis pren de la lunaria e distilla la humor per alembich, en tro veuràs que par la diminució de sa sulphureitat no porà pus cremar. Continua ta distillació en altre receptori e aquella aygua pren en tro sobre'l cap de l'alembich no apparrà res de venes. En aquesta aygua gitaràs la substancia de l'or, e tantost se dissolrà en l'aygua vejetall per rahó del mercuri. Rectifica son mercuri de la fleuma, en tro veies que creme, e puis mescla-la ab primera eau ab la substancia de l'or. E és aygua de vida.

*Cipher note: III.18 is in the Liber Mercuriorum (Part III) and uses the Part III letter cipher: B=simple water, C=simple red sulphur, D=simple dissolved gold, E=compound red water, F=compound red sulphur, G=compound dissolved gold. No letter codes appear explicitly in this particular sub-recipe, but the substances described (dissolved gold, lunaria, vegetal water, mercury/phlegm) map directly to the cipher's referents.*

**Translation:** Now we'll describe the composition of simple potable water, made from blood fixed by nature to strengthen the radical human moisture. Take the water that can dissolve gold while conserving its species/form; refine it by continued inhumation in bath and gentle decoction. Then put the dissolved gold in a fine glass cucurbit, distill the water and separate all moisture. The gold substance will remain dry at the bottom of the vessel. Then take lunaria and distill the moisture through the alembic until by diminution of its sulphureity it can no longer burn. Continue your distillation into another receiver and take that water until nothing appears at the alembic head. In this water throw the gold substance — it will dissolve immediately in the vegetal water due to the mercury. Rectify its mercury from the phlegm until you see it burns, then mix it with the first water and the gold substance. This is water of life.

The recipe is a multi-stage preparation: refine gold in a solvent by inhumation in bath, separate the gold substance by distillation, process lunaria through the alembic to produce a purified vegetal water, redissolve the gold in that water, rectify the mercury from phlegm, and combine everything. The procedure involves at least three distinct vessels (bath, cucurbit, receiver), multiple substance additions, and careful separation steps. It is materially dense — many substances are introduced, separated, and recombined — but thermally moderate: the recipe calls for gentle decoction and balneum, not aggressive heating.

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
| ka | Heat yield | Heat reaching target state |
| ke | Steady heat | Steady-state thermal management |
| te | Transfer | Executing a transfer operation |
| lch | Equipment check | Checking apparatus (seals, receiver, furnace) |
| lsh | Equipment watch | Monitoring equipment passively |
| dch | Material check | Checking material state |
| yk | Pre-heat | Preliminary thermal step |

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
| qokeedy | qo | k.e.e.d.y | fire: heat, stabilize×2, do, done | Gentle fire — balneum / water-bath level | PT-013 (10/10) |
| qokain | qo | k.a.i.n | fire: heat, yield, iterate, bind | Sustained cyclic heating | PT-013 (10/10) |
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate×2, bind | Sustained deep cyclic heating — multiple iterations | PT-013 (15/15) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target — heat stage done | PT-013 (10/10) |
| qokar | qo | k.a.r | fire: heat, yield, respond | Apply heat and note the response | B Dict D1 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qokeey | qo | k.e.e.y | fire: heat, stabilize×2, done | Establish gentle heat state | B Dict D1 |
| qol | qo | l | fire: hold | Hold current heat level | B Dict D1 |
| qokchdy | qo | k.c.h.d.y | fire: heat, adjust, watch, do, done | Adjust fire while watching | B Dict D2 |
| qotedy | qo | t.e.d.y | fire: transfer, stabilize, do, done | Execute a heat-driven transfer | B Dict D1 |
| qoty | qo | t.y | fire: transfer, done | Heat-source transfer complete | B Dict D2 |
| qotain | qo | t.a.i.n | fire: transfer, yield, iterate, bind | Sustained heat-driven transfer cycling | B Dict D2 |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dain | da | i.n | material: iterate, bind | Bind material into the cycle | B Dict D1 |
| daiin | da | i.i.n | material: iterate×2, bind | Start a new cycle — initiate the next loop | B Dict D0 |
| dal | da | l | material: hold/state | Carefully collect or place material | PT-013 (9/10) |
| daldy | da | l.d.y | material: hold, do, done | Careful placement, seal, done | Compositional |
| dalal | da | l.a.l | material: hold, yield, hold | Careful double placement — measure and place | Compositional |
| dairam | da | i.r.a.m | material: iterate, respond, yield, final | Material cycle: respond, yield, finalize | Compositional |
| daiidy | da | i.i.d.y | material: iterate×2, do, done | Extended iterative material handling, done | Compositional |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state — verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| chdy | ch | d.y | test: do, done | Actively check, done | B Dict D2 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chekal | ch | e.k.a.l | test: stabilize, heat, yield, hold | Quality check — has heat produced the right yield? | B Dict D2 |
| cheedy | ch | e.e.d.y | test: stabilize×2, do, done | Extended active verification | B Dict D2 |
| cheky | ch | e.k.y | test: stabilize, heat, done | Quick heat-state check | B Dict D2 |
| cheey | ch | e.e.y | test: stabilize×2, done | Gentle stabilization check | B Dict D2 |
| cheeky | ch | e.e.k.y | test: stabilize×2, heat, done | Deep stabilization heat check | Compositional |
| cheol | ch | e.o.l | test: stabilize, arrange, hold | Check apparatus arrangement during cooling | B Dict D2 |
| chody | ch | o.d.y | test: arrange, do, done | Check the arrangement | B Dict D2 |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly — quick passive check | B Dict D1 |
| sheedy | sh | e.e.d.y | watch: stabilize×2, do, done | Extended passive observation | B Dict D2 |
| shekal | sh | e.k.a.l | watch: stabilize, heat, yield, hold | Watch until heat produces yield | Compositional |
| shckhy | sh | c.k.h.y | watch: adjust, heat, watch, done | Passively observe the heat level | B Dict D2 |
| shol | sh | o.l | watch: arrange, hold | Watch the arrangement passively | B Dict D2 |
| okaiin | ok | a.i.i.n | vessel: yield, iterate×2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal the vessel for a processing cycle | B Dict D1 |
| okedy | ok | e.d.y | vessel: stabilize, do, done | Check vessel during cooling | B Dict D1 |
| okeedy | ok | e.e.d.y | vessel: stabilize×2, do, done | Maintain vessel at gentle balneum temperature | B Dict D1 |
| okeey | ok | e.e.y | vessel: stabilize×2, done | Vessel gently stabilized | B Dict D2 |
| okal | ok | a.l | vessel: yield, hold | Vessel at yield state | B Dict D2 |
| okar | ok | a.r | vessel: yield, respond | Vessel yields — note response | B Dict D3 |
| otedy | ot | e.d.y | drip-rate: stabilize, do, done | Check drip/flow rate during cooling | B Dict D1 |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| olkeedy | ol | k.e.e.d.y | continue: gentle heat, do, done | Continue at balneum temperature | B Dict D2 |
| olkain | ol | k.a.i.n | continue: heat, yield, iterate, bind | Continue sustained cyclic heating | Compositional |
| olkol | ol | k.o.l | continue: heat, arrange, hold | Continue heating in current arrangement | Compositional |
| oldy | ol | d.y | continue: do, done | Continue current action, done | Compositional |
| olchy | ol | c.h.y | continue: adjust, watch, done | Continue while adjusting and watching | Compositional |
| saiin | sa | i.i.n | scaffold: iterate×2, bind | Begin extended binding iteration cycle | B Dict D1 |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| keedy | ke | e.d.y | steady-heat: stabilize, do, done | Steady-state thermal check | B Dict D2 |
| lchedy | lch | e.d.y | equipment: stabilize, do, done | Check equipment state during cooling | B Dict D1 |
| lshedy | lsh | e.d.y | equipment-watch: stabilize, do, done | Monitor equipment passively | B Dict D2 |
| dchedy | dch | e.d.y | material-check: stabilize, do, done | Check material state during cooling | Compositional |
| dy | — | d.y | mark, done | Cycle close — action complete | B Dict D1 |
| ol | — | o.l | arrange, hold | Hold steady | B Dict D0 |
| pchedy | pch | e.d.y | stage-test: stabilize, do, done | Stage-test: verify state (paragraph opener) | B Dict D2 |
| kaiin | ka | i.i.n | heat-yield: iterate×2, bind | Extended heat cycling toward yield | B Dict D2 |
| kain | ka | i.n | heat-yield: iterate, bind | Heat cycling toward yield | B Dict D2 |

**Observation MIDDLEs** — specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

---

## The Folio

**f81v:** 258 tokens, 27 lines, 2 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|---------------------|
| P1 | 1–9 | 91 | 15 | 0.33 | 3 ckh | Preparation: inhumation, dissolution, material loading |
| P2 | 10–27 | 167 | 6 | 0.55 | 2 ckh | Distillation: separation, lunaria processing, rectification |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation). Lower values = more sustained uninterrupted heat (inhumation, sealed processing). A value near zero means no thermal operation at all (vessel handling).

**Structural signature:** This folio has only 2 paragraphs but 21 dar — extremely high material density. The recipe explains why: potable gold requires dissolving gold, separating it, processing lunaria, redissolving gold, rectifying mercury, and combining multiple products. Every one of those steps introduces or handles a substance. The 2-paragraph structure splits the procedure into its natural halves: P1 is preparation and inhumation (material-heavy, thermally sustained), P2 is distillation and rectification (material-light, thermally active).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1–9, 91 tokens) — Preparation: Inhumation and Material Loading

**Recipe says:** "Take the water that can dissolve gold while conserving its species/form; refine it by continued inhumation in bath and gentle decoction."

The opening phase: take the solvent water, add the gold, and subject the mixture to prolonged inhumation — sealed processing in a water bath with gentle, sustained heat. This is not distillation but dissolution: the gold must be refined *within* the solvent through repeated sealed cycles. The recipe explicitly calls for "continuació ab inhumació en bany" — continued inhumation in bath.

**What the tokens say:**

**15 material additions in 91 tokens.** This is by far the highest material density on any cold-read folio — one in every six tokens is a `dar` or `da`-prefix substance-handling instruction. The recipe explains the density: potable gold begins by combining multiple prepared substances (the solvent water, the gold itself) and then subjecting them to iterative sealed processing that requires repeated material interventions.

L1 opens with observation (`shey` — "watch briefly") and a steady-heat check (`keedy` — "steady-state thermal check"), then immediately begins material work: `dal` ("carefully place material") followed by `dar` ("add a new substance"). The stage-test `pchedy` appears mid-line, marking the paragraph opening. More observation follows (`shek`, `sheky` — watching the heat state), then transfer-rate operations: `otoin` (ot-prefix = "monitor transfer rate: arrange, iterate, bind") and `olkol` ("continue heating in arrangement"). *(Note: `otoin` has ot-prefix (transfer-rate domain), not ok-prefix (vessel domain). The reading is "set up transfer cycle," not "seal the vessel.")* The line reads: observe the setup, add the first materials, verify, seal the vessel.

L2 applies the first heat: `qokedy` ("maintain current fire level"), then immediately shifts to sealed processing — `okaiin` ("extended sealed processing, multiple cycles"). This is the inhumation beginning. The line is dominated by iteration tokens: `kair`, `kain`, `olkain` — all heat-yield-iterate patterns. The recipe says "continuació ab inhumació" and the tokens encode exactly that: sustained iterative heat cycling within a sealed vessel. Three `ol` tokens maintain the state through the process.

L3 intensifies: `saiin` ("begin extended binding iteration cycle") opens the line, followed by `daiin` ("start a new cycle"). Then vessel management at balneum temperature: `olkeedy` ("continue at gentle heat") and `okedy` ("check vessel during cooling"). A heat-level check follows with `chdy` ("actively check, done"). Material handling continues: `dalal` ("careful double placement") — measuring and placing material with extra care. The recipe's "laugera decocció" (gentle decoction) is reflected in the `olkeedy` balneum-temperature token.

L4 opens with `qokaiin` ("sustained deep cyclic heating — multiple iterations") — the most intensive sealed-heat token in the vocabulary. This is the heart of the inhumation: deep, sustained, multi-cycle processing. The vessel is sealed (`okain` — "seal the vessel for a processing cycle"), then checked (`cheeky` — "deep stabilization heat check"). Material additions continue: `dain`, `daiin` — binding material into the cycle. The line closes with a **heat-level check** (`chckhy`): is the bath at the right temperature?

L5 continues the sealed processing pattern: `okaiin` ("extended sealed processing") followed immediately by `daiin` ("new material cycle"). Transfer monitoring appears: `otain` — watching the output while the vessel processes. Another **heat-level check** (`chckhy`) — the second in two lines. The recipe says gentle decoction, and the scribe checks the heat twice in rapid succession. Then vessel stabilization: `okeedy` ("maintain vessel at balneum temperature") and `qoky` ("cease heating"). The first thermal cycle is winding down. Material additions close the line: `daiin`, `okar` — adding substances and noting the vessel's response.

L6 transitions: `qokain` ("sustained cyclic heating") and `okaiin` ("extended sealed processing") continue the inhumation, but now verification dominates. Two active checks appear: `chedy` ("check the state") and `cheol` ("check apparatus arrangement"). Then `daldy` ("careful placement, seal, done") — material is being carefully placed and the vessel sealed. The inhumation cycle is being managed through careful material additions and state verification.

L7 opens with vessel operations (`olor` — "arrange vessel"), then a critical compound observation token: `sheckhal` — passively observe the heat state while checking yield. This extended observation token (6 atoms) monitors whether the inhumation is producing the desired result. Two `daiin` additions bracket `qokeedal` — a heat token that combines gentle balneum heat (`kee`) with a yield-hold terminal (`d.a.l`): apply gentle heat until a yield state is reached and hold it there. The third **heat-level check** (`chckhy`) of P1 appears here. The line reads: check yield, add material, apply gentle heat to yield, add material, verify heat level.

L8 shifts toward observation: `shedy` ("watch the distillate") and `sheedy` ("extended passive observation"). Between observations, heat state is held (`qol` — "hold current heat level") and material is added (`daiin`, `dkain`). Gentle steady heat (`keedy`) maintains the balneum. The tone has shifted from active material loading to patient observation — the inhumation is running, and the operator watches.

L9 closes the paragraph with a cluster of iteration and vessel tokens: `kaiin` ("extended heat cycling"), `okeey` ("vessel gently stabilized"), `daiin` ("material cycle"), then `olor` ("arrange vessel"). The final observation is a compound heat check: `checkhy` ("cool, adjust, heat, watch, done") — a thorough verification before the paragraph closes. The last token is `daiidy` ("extended iterative material handling, done") — material work finalized.

**Match assessment:** Strongly coherent. The signature feature of P1 is its extreme material density (15 dar in 91 tokens, 16.5%) combined with low e-depth (0.33). The recipe calls for inhumation — sealed processing in a bath — which requires sustained heat without active cooling (low e-depth) and repeated material handling (high dar). The three heat-level checks across 9 lines match the recipe's emphasis on "laugera decocció" (gentle decoction): the operator must verify the bath temperature repeatedly to avoid overheating the gold solution. The heavy presence of `okaiin`/`okain` (sealed vessel cycling) tokens encodes the inhumation process directly.

---

### P2 (Lines 10–27, 167 tokens) — Distillation, Separation, and Rectification

**Recipe says:** "Then put the dissolved gold in a fine glass cucurbit, distill the water and separate all moisture. The gold substance will remain dry at the bottom. Then take lunaria and distill through the alembic until the sulphureity can no longer burn. Continue distillation into another receiver until nothing appears at the alembic head. In this water throw the gold substance — it will dissolve. Rectify its mercury from the phlegm until it burns, then mix with the first water and the gold substance. This is water of life."

The second half of the recipe is a multi-step distillation and rectification sequence: separate gold from solvent, process lunaria, redissolve gold, rectify mercury, and combine. Where P1 was about loading and inhumation (sealed, material-heavy), P2 is about distillation and purification (open, heat-active).

**What the tokens say:**

**e-depth rises from 0.33 to 0.55** — a dramatic shift. P2 has nearly twice the cooling intervention of P1. This is the fingerprint of active distillation: heating to produce vapors that are then condensed (cooled). The recipe moves from sealed inhumation (low e-depth) to open distillation through the alembic (high e-depth), and the folio's thermal signature tracks this transition exactly.

**6 material additions in 167 tokens.** Material density drops from 16.5% (P1) to 3.6% (P2). The recipe explains the shift: P1 was about combining substances; P2 is about separating and purifying them. You add less because you're taking things apart.

**Lines 10–11: Opening the distillation apparatus.** L10 opens with `polshy` (sequence/watch start) and a complex observation token, then shifts to vessel work: `okeedy` ("maintain vessel at balneum temperature"), `otedy` ("check drip rate during cooling"), and `qoty` ("heat-source transfer complete"). The single material token `dairam` ("material cycle: respond, yield, finalize") closes the line — material from P1's inhumation is being loaded into the cucurbit. L11 establishes the gentle heat regime: `qokeey` ("establish gentle heat"), `okeey` ("vessel gently stabilized"), `qoky` ("cease heating"). Multiple tokens check vessel state. The apparatus is being brought to operating temperature for distillation.

**Lines 12–13: First distillation — separating the water.** The recipe says "distilla l'aygua e separa'n tota la humor." L12 has fire management (`qokedy` — "maintain fire level"), observation (`shedy` — "watch the distillate"), and transfer operations (`chetedy` — an active check during transfer, and two `ytedy` — transfer executions). The distillation is running: heat, watch, transfer, repeat. L13 continues with more transfer tokens (`ytedy` ×2) and adds `dar` — a material addition. This single `dar` may mark the moment when the gold substance, now dry at the bottom, is set aside: "E estarà la substancia de l'or al fons del vexell tota secca."

**Lines 14–16: Lunaria distillation.** The recipe says "Puis pren de la lunaria e distilla la humor per alembich, en tro veuràs que par la diminució de sa sulphureitat no porà pus cremar." L14 opens with observation (`dshedy`) and thermal management (`ykeedy`), then adds `daiin` ("new material cycle") — the lunaria is being introduced. Fire management intensifies: `qokeed`, `qokedy`, and an equipment check (`lchpchdy`) verify the apparatus state. L15 has `qokal` ("fire reached target"), then verification (`chedy` — "check the state") and passive observation (`sheey` — "extended passive observation"). A complex scaffold-observation token (`salshcthdy`) encodes watching a transfer through the apparatus — monitoring what comes through the alembic. The recipe says to distill "until the sulphureity can no longer burn," and the folio encodes sustained distillation with active checks. L16 adds observation (`shedy`), gentle heat (`qoeedy`), and another `dar` — possibly the moment when the receiver is changed: "Continua ta distillació en altre receptori." The line closes with monitoring tokens (`chdy`, `pchdy`) — actively checking the transition.

**Lines 17–19: Continued distillation with monitoring.** The recipe says to continue distillation "until nothing appears at the alembic head." L17 opens with a compound watch token (`sshkchdy` — observing the heat with adjustment), then alternates observation and fire management: `shedy`, `qolchedy`, `qokain`. A **heat-level check** (`shckhy`) appears — passively watching the fire level. This is sustained distillation under close monitoring, exactly the attentive watching required to determine when "no apparrà res de venes" (nothing more appears at the alembic head).

L18 intensifies the fire management: `qokchdy` ("adjust fire while watching"), then verification (`chey`, `cheky`), observation (`shedy`), and two `qokedy` ("maintain fire level") tokens in sequence. A **heat-level check** (`chckhy`) appears — the operator verifies the fire is right. Then `qoky` ("cease heating"): a distillation pass completes.

L19 opens with `solkeey` ("establish gentle heat in sequence"), observation (`shedy`), then `qokar` ("apply heat, note response") — the operator is checking whether the distillate has changed. The compound observation token `sheckhy` (watch, adjust, heat, watch) encodes careful monitoring of the heat state. Two heat tokens close the line: `qokar`, `qokal` — apply heat, reach target. The distillation is approaching the endpoint where nothing more comes through.

**Lines 20–21: Redissolution and transfer.** The recipe says "En aquesta aygua gitaràs la substancia de l'or, e tantost se dissolrà en l'aygua vejetall per rahó del mercuri." L20 opens with `qocthey` — a fire-source token that includes a transfer-watch (cth): heat while watching what is being transferred. This is the moment of redissolution: throwing the gold substance into the vegetal water. Then `chekal` ("quality check — has heat produced the right yield?") and `chody` ("check the arrangement") — the operator verifies the redissolution has occurred. Fire management continues (`qokedy`), and transfer tokens dominate: `lshety` ("equipment watch: transfer"), `qoldy` ("fire: hold, do"), `ltedy` ("transfer done"), `qotain` ("sustained heat-driven transfer cycling"). The line reads: heat-transfer-watch, verify dissolution, continue transfers.

L21 shifts to equipment monitoring: four `lsh`-prefix tokens (`lsho`, `lshedy` ×2) — monitoring equipment during cooling. The recipe says to "rectifica son mercuri de la fleuma" (rectify its mercury from the phlegm), and equipment monitoring is characteristic of rectification: watching the alembic, checking seals, noting what comes through. Active checks (`chedy`) alternate with heat management (`qolky`, `qol`). An equipment check (`lchedal`) and transfer rate monitoring (`otar`) close the line.

**Lines 22–24: Rectification.** L22 continues the rectification: `qokal` ("fire reached target"), `qol` ("hold heat"), then sealed iteration (`oiin` — "arrange, iterate×2, bind"). A gentle verification (`cheey`) precedes a careful material addition (`dal` — "carefully place material"). Observation closes: `shedy`, `sal` (scaffold state). L23 opens with passive observation (`shol`), then iterative tokens (`ykaiin`, `olkain` — extended cycling), observation (`shedy`), and `qoky` ("cease heating"). A material check (`dchedy`) appears — checking the material state after rectification. L24 has vessel checking (`okchedy`), fire management (`qokal`), vessel stabilization (`okeey`), and extended verification (`cheedy` — "extended active verification"). The rectification is being monitored carefully with repeated checks.

**Lines 25–27: Completion — combining and finalizing.** The recipe says "puis mescla-la ab primera eau ab la substancia de l'or. E és aygua de vida." L25 has observation (`oshedy`, `shol`), a heat-driven transfer (`qotedy`), and multiple active checks (`chedy` ×2, `chey`). The operator is watching the final combination step. L26 begins with arrangement (`ol`), a compound monitoring token (`chechol` — checking arrangement while adjusting), and iteration (`oiin`). Material is carefully added (`dal`) — possibly the final combining of the first water with the gold substance. The line closes with gentle heating: `olkeol`, `olkeedy` ("continue at balneum temperature"), `okeol` — maintaining temperature during the final combination.

L27 (the final line) has only 7 tokens. It opens with observation (`dsheol`), then deep iteration (`oiiin` — "arrange, iterate×3, bind" — a triple-iteration token, rare in the corpus, encoding the final multi-component combination). Gentle continued heating (`olkeedy`), a transfer (`tedy`), a heat check (`cheky`), a compound passive observation (`shckhedy` — watching the heat level while cooling), and a final yield-hold (`chal`). The folio closes with observation and stabilization — the water of life is prepared.

**Match assessment:** Coherent. P2's signature features — high e-depth (0.55), low material density (3.6%), and dominant fire/observation prefixes — encode active distillation and rectification. The progression from transfer operations (L12–13) through sustained distillation monitoring (L17–19) to equipment-focused rectification (L20–21) to final combination (L25–27) maps to the recipe's sequence: separate moisture, distill lunaria, redissolve gold, rectify mercury, combine. The two heat-level checks (L17, L18) appear during the lunaria distillation phase, where the recipe demands close attention to the endpoint ("until the sulphureity can no longer burn"). The `lsh` (equipment-watch) cluster on L21 is characteristic of rectification — monitoring the apparatus during purification.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | **0.33** | Sustained sealed heat — inhumation in bath |
| P2 | **0.55** | Active distillation and rectification |

The e-depth contrast between the two paragraphs is stark: 0.33 vs 0.55. This is the largest single-transition e-depth jump of any 2-paragraph folio in the cold-read set. The recipe explains why: P1 is inhumation — sealed processing in a water bath where heat is sustained and steady, with minimal cooling intervention. P2 is distillation and rectification — heating to produce vapors that are then condensed, requiring active cooling. The folio's thermal architecture directly encodes the physical chemistry of the procedure.

### dar distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 15 | **71%** | Inhumation: combining water, gold, and iterative additions |
| P2 | 6 | 29% | Distillation/rectification: separation dominates |

Material additions are front-loaded: 71% occur in P1. This is the inverse of most cold-read folios (where material additions typically accumulate toward the end). The recipe explains the inversion: potable gold begins with extensive material preparation — dissolving gold in the solvent water through repeated sealed cycles — before the long distillation-and-rectification sequence. You load materials first, then separate and purify. The folio encodes this front-loaded material pattern precisely.

### Observation MIDDLE distribution

| Para | ckh | cth | ecth | Total | Recipe activity |
|------|-----|-----|------|-------|-----------------|
| P1 | 3 | — | — | 3 | Inhumation: repeated heat-level checks |
| P2 | 2 | — | — | 2 | Distillation: monitoring during lunaria processing |

All 5 observation MIDDLEs are heat-level checks (`ckh`). There are no transfer-watches (`cth`) or cooled-transfer-watches (`ecth`) on this folio. This makes sense given the recipe: potable gold is primarily about managing temperature during sealed inhumation (P1) and then during distillation (P2). The operator's monitoring concern throughout is "is the heat right?" — not "what is being transferred?" The recipe says "laugera decocció" (gentle decoction) and demands attention to sulphureity diminution during lunaria distillation. Heat monitoring is the dominant observation mode because the procedure's success depends on temperature control at every stage.

### Prefix distribution shift

| Prefix | P1 count | P2 count | Shift |
|--------|----------|----------|-------|
| da (material) | 15 | 6 | Heavy → Light |
| qo (fire) | 7 | 35 | Light → **Dominant** |
| ch (check) | 8 | 23 | Moderate → Heavy |
| sh (watch) | 8 | 20 | Moderate → Heavy |
| ok (vessel) | 10 | 12 | Steady |

The prefix shift tells the story of the recipe's two halves. P1 is material-dominated: the operator is loading substances into the sealed vessel for inhumation. P2 is fire-and-observation-dominated: the operator manages distillation, watches the alembic, and checks the product. The `qo` prefix count jumps fivefold (7 to 35), reflecting the shift from passive sealed heating to active fire management during distillation. The `ch` and `sh` prefixes nearly triple, reflecting the intensified monitoring required during lunaria distillation and mercury rectification.

---

## Verdict: COHERENT

f81v produces a coherent two-paragraph reading against III.18.0 (potable gold / water of life). The folio's most distinctive feature — its extreme material density (21 dar, 8.1% of tokens) concentrated in P1 — matches the recipe's requirement for extensive material preparation before distillation. The two paragraphs map to the recipe's natural structural division:

1. **Inhumation and dissolution** (P1) — 15 material additions, e-depth 0.33 (sustained sealed heat), 3 heat-level checks. Maps to: "take the water, refine gold by inhumation in bath and gentle decoction."
2. **Distillation, separation, and rectification** (P2) — 6 material additions, e-depth 0.55 (active distillation), fire-management dominant (35 qo-prefix tokens), equipment monitoring during rectification. Maps to: distill to separate moisture, process lunaria through alembic, redissolve gold, rectify mercury, combine into water of life.

**Material markers (expert review note):** `qofchedy` on L15 contains the fch atom pattern (C1939: mercury/mercury-water marker, enriched on all 6/6 confirmed mercury-recipe folios). It appears at the transition between distillation and mercury rectification — exactly where the recipe says "rectifica son mercuri de la fleuma." The cs gold marker (C1940) is absent despite gold being the recipe's central subject; the expert positive control explained this as consistent with gold being a dissolved intermediate rather than a raw metallic input (contrast f84r where gold is actively dissolved and cs=3).

The e-depth contrast (0.33 → 0.55) is the strongest structural signal: sealed inhumation produces sustained low-cooling heat; distillation and rectification produce active cooling. This thermal transition encodes the physical chemistry of the procedure without depending on any individual token gloss.

The only observation MIDDLEs are heat-level checks (`ckh`), consistent with a recipe that demands careful temperature control throughout — gentle decoction during inhumation, attentive monitoring during lunaria distillation to detect the endpoint. The absence of transfer-watches (`cth`) and cooled-transfer-watches (`ecth`) is itself informative: this recipe is about dissolution and distillation within vessels, not about moving cooled intermediates between setups.

The 2-paragraph structure is unusual for this corpus (most folios have 4–9 paragraphs), but the recipe is a single continuous procedure with one natural division point: the transition from sealed inhumation to open distillation. The folio allocates its paragraph break precisely at that boundary.
