# Cold Read: f116r ↔ III.4.0 Fixation and Perfection (Fusibility Test)

**Match tier:** SUPPORTED
**Verdict:** Partially Coherent (revised from Coherent after expert review — zero fch mercury markers on a mercury fixation recipe, per C1939)

---

## The Recipe (III.4.0 — SISMEL Catalan, complete)

> Quant hauràs sublimat e presa la dita pura substancia del mercuri, adonchs fixaràs la una part de aquell; e nós te havem dat la manera de la fixació en la pedra maior. E quant aquella part serrà fixada, fixarà aprés l'altra. Donchs, reitera la sublimació de la partida no fixa sobra la cosa fixa, en tro que aquella semblantment sia fixa. La qual cosa temptaràs assaiant si bona fusió prestarà sobre lo foch. E si ho [fa], fet és; e si non fa, ajusta-li de l'argent viu exuberat en reiterant sa sublimació en tro que sia fusible. E la manera de la exuberació de tot argent viu te havem dat, si nos has entès, en la pratica de la pedra maior, com en aquesta «Pratica», en lo capitol segon que comença «Tu pendràs». Mas aquell se fa de son matex argent viu, e per ço és ella simpla. Mas si la vols més composta e la vols de mercuri, dissol altre mercuri en l'aygua primera que és exuberada de la ànima del dit mercuri del qual és feta la tinctura; e puys separa l'aygua per distilació, e así reitera en distillant e redistillant sobre ses feces en tro haya beguda l'aygua e tirada a ella tota la humiditat de les feces mercurials. Ffill, aquesta és la humiditat encerativa que sobre totes les altres està contra la batalla del foch. Per que ací, per la sola substancia del mercuri, fem excellent medicina de blanchor. E así com te sembla que nós diem de un, así entén que nós diem de tots...

*Cipher note: III.4.0 belongs to Part III (Liber Mercuriorum) and uses the Part III letter cipher: B=simple water, C=simple red sulphur, D=simple dissolved gold, E=compound red water, F=compound red sulphur, G=compound dissolved gold. No letter codes appear in this particular sub-recipe.*

**Translation:** When you have sublimated and taken the pure mercury substance, fix one part of it (we gave you the method in the greater stone). When that part is fixed, fix the other. Reiterate sublimation of the unfixed part over the fixed, until it too is fixed. **Test this** by trying if it gives good fusion over fire. If it does -- it's done. If not, add exuberated quicksilver and reiterate sublimation until fusible. To make it more composite: dissolve another mercury in the first water exuberated from the soul of the mercury; separate the water by distillation, reiterate distilling and redistilling over its feces until it has drunk the water and drawn all moisture from the mercurial feces. This is the wax-like moisture that resists fire above all others.

The recipe has a distinctive structure: (1) fix one part, then the other, via iterated sublimation; (2) apply the **fusibility test** -- does the product melt well over fire?; (3) conditional branching: if it passes, you're done; if not, add exuberated mercury and reiterate; (4) optional composite path: dissolve more mercury, distill and redistill over feces (cohobation) until the water is absorbed; (5) endpoint: the wax-like moisture that withstands fire.

Key features for matching: heavy sublimation cycling, a critical test-point (fusibility over fire), conditional addition of more material, feces cohobation (distilling and redistilling over residue), and the wax-like endpoint.

---

## Token Dictionary

The table below shows how Voynich tokens are read in this cold read. The "Workshop Reading" column gives the operational meaning validated against Catalan recipe text (PT-013/014/015) and distributional evidence (B Operational Dictionary). The "Atoms" column shows the underlying structural decomposition (C1394 HEAD+MOD+TERM model). Readers unfamiliar with the atom system can ignore the Atoms column entirely -- the Workshop Reading is self-sufficient.

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
| qokain | qo | k.a.i.n | fire: heat, yield, iterate, bind | Sustained cyclic heating | PT-013 (10/10) |
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate x2, bind | Deep sustained cyclic heating | PT-013 (15/15) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target -- heat stage done | PT-013 (10/10) |
| qokar | qo | k.a.r | fire: heat, yield, respond | Apply heat and note the response | B Dict D1 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qokeey | qo | k.e.e.y | fire: heat, stabilize x2, done | Establish gentle heat state | B Dict D1 |
| qokey | qo | k.e.y | fire: heat, stabilize, done | Standard heat -- done | B Dict D2 |
| qotain | qo | t.a.i.n | fire: transfer, yield, iterate, bind | Sustained heat-driven transfer | B Dict D2 |
| qoteedy | qo | t.e.e.d.y | fire: transfer, stabilize x2, do, done | Gentle heat-driven transfer | B Dict D2 |
| qotar | qo | t.a.r | fire: transfer, yield, respond | Transfer heat/material and note result | B Dict D1 |
| qotam | qo | t.a.m | fire: transfer, yield, final | Transfer operation finalized | Compositional |
| qokam | qo | k.a.m | fire: heat, yield, final | Heat stage finalized | Compositional |
| qokchdy | qo | k.c.h.d.y | fire: heat, adjust, watch, do, done | Adjust fire while watching | B Dict D2 |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dain | da | i.n | material: iterate, bind | Bind material into the cycle | B Dict D1 |
| daiin | da | i.i.n | material: iterate x2, bind | Start a new cycle | B Dict D0 |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state -- verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| cheey | ch | e.e.y | test: stabilize x2, done | Gently verify stabilization | B Dict D2 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chcthy | ch | c.t.h.y | test: adjust, transfer, watch, done | Watch the transfer (active) | B Dict D2 |
| chkar | ch | k.a.r | test: heat, yield, respond | Quality check -- is the heat product right? | Compositional |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly -- quick passive check | B Dict D1 |
| sheedy | sh | e.e.d.y | watch: stabilize x2, do, done | Extended passive observation | B Dict D2 |
| shckhy | sh | c.k.h.y | watch: adjust, heat, watch, done | Passively observe the heat level | B Dict D2 |
| shcthy | sh | c.t.h.y | watch: adjust, transfer, watch, done | Watch the transfer (passive) | Compositional |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| otedy | ot | e.d.y | drip-rate: stabilize, do, done | Check drip/flow rate during cooling | B Dict D1 |
| oteedy | ot | e.e.d.y | drip-rate: stabilize x2, do, done | Note gentle transfer rate | B Dict D2 |
| otal | ot | a.l | drip-rate: yield, hold | Note the output rate | B Dict D2 |
| otain | ot | a.i.n | drip-rate: yield, iterate, bind | Sustained transfer monitoring | B Dict D2 |
| okeey | ok | e.e.y | vessel: stabilize x2, done | Vessel temperature: gently settled | B Dict D2 |
| okeedy | ok | e.e.d.y | vessel: stabilize x2, do, done | Vessel at gentle balneum temperature | B Dict D1 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal vessel for processing cycle | B Dict D1 |
| okal | ok | a.l | vessel: yield, hold | Vessel reached target state | B Dict D2 |
| okar | ok | a.r | vessel: yield, respond | Note the vessel state | B Dict D3 |
| lchedy | lch | e.d.y | equipment-check: stabilize, do, done | Check apparatus (seals, receiver, furnace) | PT-013 (8/10) |
| lchey | lch | e.y | equipment-check: stabilize, done | Quick equipment check | B Dict D2 |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| keedy | ke | e.d.y | steady-heat: stabilize, do, done | Steady-state thermal check | B Dict D2 |
| dy | -- | d.y | mark, done | Cycle close -- action complete | B Dict D1 |
| am | -- | a.m | yield, final | Phase done -- yield result and close | B Dict D0 |
| ol | -- | o.l | arrange, hold | Hold steady | B Dict D0 |

**Observation MIDDLEs** -- specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

---

## The Folio

**f116r:** 537 tokens, 49 lines, 8 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|---------------------|
| P1 | 1-3 | 33 | 1 | 0.42 | -- | Sublimate and take pure mercury substance |
| P2 | 4-6 | 33 | 1 | 0.55 | 1 ckh | Fix first part |
| P3 | 7-14 | 80 | 4 | 0.64 | -- | Reiterate sublimation (unfixed over fixed) |
| P4 | 15-17 | 32 | 5 | 0.62 | 1 cth | Fusibility test + conditional addition |
| P5 | 18 | 12 | 0 | 0.50 | -- | Branch decision: pass/fail |
| P6 | 19-30 | 140 | 4 | 0.50 | 4 cth, 4 ckh | Exuberation cycle + reiteration to fusibility |
| P7 | 31-36 | 65 | 1 | 0.57 | 2 ckh | Composite dissolution -- dissolve mercury in first water |
| P8 | 37-49 | 142 | 3 | 0.48 | 4 ckh, 1 cth | Feces cohobation -- redistill until wax-like moisture |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation). Lower values = more sustained uninterrupted heat (sublimation, fixation). A value near zero means no thermal operation at all (vessel handling).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1-3, 33 tokens) -- Sublimation of Pure Mercury

**Recipe says:** "When you have sublimated and taken the pure substance of mercury..."

The recipe's opening premise: sublimation has already been performed and you are now collecting the purified mercury substance. This is a setup step -- handle the sublimate.

**What the tokens say:**

The paragraph opens with `kchdpy` ("precision-heat: do, done") -- a brief framing action. Then `shey` ("watch briefly") and `qokain` ("sustained cyclic heating") -- observe, then apply sustained heat. This opening triplet establishes supervised thermal operation.

L1 continues with `otalshedy` -- a compound vessel-monitoring token (transfer-rate: yield, state, watch, done) -- and two `shear` ("observe: yield, respond") tokens. Heavy observation with transfer monitoring: the operator is watching the sublimation yield.

L2 shifts to vessel management. Two consecutive `okeey` ("vessel temperature: gently settled") tokens confirm the vessel is at the correct temperature. Then `okain` ("seal vessel for processing cycle") -- the vessel is closed for a cycle. The line also carries iterative binding tokens (`ain`, `aiiin`) consistent with setting up repeated sublimation passes.

L3 has the paragraph's only material addition: `dain` ("bind material into the cycle"). Then equipment checks (`lshey`, `lshedy`) and observation (`shey`) close the paragraph. The final token `saly` (scaffold: state, done) frames the infrastructure.

**Match assessment:** Coherent. A supervised sublimation setup with sustained cycling, vessel temperature verification, one material binding, and heavy observation. The low e-depth (0.42) indicates sustained heat with minimal cooling intervention -- consistent with sublimation, which requires steady upward heat rather than the cyclic cooling of distillation. The recipe says sublimation has been performed and the product collected; the tokens encode precisely that: sustained heat, vessel handling, observation of the yield.

---

### P2 (Lines 4-6, 33 tokens) -- Fix the First Part

**Recipe says:** "Fix one part of it; we gave you the method of fixation in the greater stone."

Fix the first portion of the sublimated mercury. Fixation requires prolonged heating to make a volatile substance non-volatile.

**What the tokens say:**

L4 opens with heavy transfer-rate monitoring: `oteedy` ("note gentle transfer rate"), `qotar` ("transfer heat/material and note result"). In fixation, you are driving off volatile components -- monitoring what comes off tells you whether the material is still volatile. The key observation: `chckhy` -- the paragraph's only **heat-level check** (ckh). Is the fire at the right level? Fixation requires sustained heat at a specific temperature; checking the heat is exactly what the recipe demands.

`chedy` ("check the state") appears three times across L5-L6 -- active verification that the fixation is proceeding. This is the operator repeatedly confirming: is it fixed yet?

L5 has `qokchdy` ("adjust fire while watching") -- fine-tune the fire during fixation. Then transfer monitoring intensifies: `otal` ("note the output rate"), `oteedy`, `otor`, `oty` -- a dense cluster of transfer-rate tokens. The operator is watching what leaves the vessel. When the transfer stops (nothing more volatile escapes), fixation is complete.

L6: `sain` ("begin a binding iteration cycle") -- the iterative frame for fixation. Then `lchedy` ("check apparatus") and three `chedy` ("check the state") tokens close the paragraph with continuous verification.

**Match assessment:** Coherent. One heat-level check, heavy transfer-rate monitoring (8 ot-prefix tokens -- the densest ot-concentration per token of any paragraph on this folio), three state checks, and one iteration binding. The e-depth rises to 0.55 -- more cooling intervention than sublimation, consistent with fixation requiring careful temperature management rather than pure sustained heat. The recipe says "fix one part"; the tokens encode: check the fire, watch what comes off, verify the state repeatedly.

---

### P3 (Lines 7-14, 80 tokens) -- Reiterate Sublimation (Unfixed over Fixed)

**Recipe says:** "Reiterate sublimation of the unfixed part over the fixed, until that likewise is fixed."

The core operation: take the part that is not yet fixed, sublimate it again over the already-fixed material, and repeat until both parts are fixed.

**What the tokens say:**

P3 is the largest paragraph so far -- 80 tokens across 8 lines. The recipe says to **reiterate** sublimation, and the folio allocates proportional space.

The e-depth is the highest on the folio at 0.64. This is active distillation/sublimation territory: each sublimation cycle involves heating (to sublimate), then cooling (to condense the sublimate back onto the fixed material). The high e-depth captures this oscillation between heat and cool.

**14 qo-prefix tokens** (heat-source operations) dominate the paragraph. Key sequences:

L7: `qokain` ("sustained cyclic heating") followed by `qoteey` ("gentle heat-driven transfer") and `tokain` (heat, iterate, bind). A sublimation cycle: apply sustained heat, transfer the sublimate, bind into the next iteration.

L8: `dar` ("add a new substance") opens the line -- the unfixed part being loaded over the fixed. Then `qokeey` ("establish gentle heat"), `qokain` ("sustained cyclic heating"), `qotody` (heat-driven transfer) -- another sublimation cycle. `oteedar` is a compound token joining transfer monitoring with material addition: the sublimate deposits on the fixed material.

L9: Three heat-source tokens in sequence: `qokeey`, `qokeedy` ("gentle fire -- balneum level"), `qokain`. The heat profile shifts to gentler application -- as sublimation iterates, the operator eases the fire to control deposition.

L10-L11: `dar` on L10 (another material loading), followed by heavy observation: `shedy`, `sheedy`, `shdy` -- three distinct passive-watch tokens. The operator watches the sublimate condense. `qoteedy` ("gentle heat-driven transfer") and `qotain` ("sustained heat-driven transfer") on L11 keep the sublimation cycling.

L12: Two `dain` ("bind material into cycle") and one `dain` -- material binding intensifies as the reiteration continues. `okain` ("seal vessel for processing cycle"), `otain` ("sustained transfer monitoring"), `olam` ("vessel load: yield, final") -- the cycle nears completion. The `am` terminal (final) signals approaching closure.

L13-L14: Two `sain`/`sar` scaffold tokens frame the iterative infrastructure. `qoteedy` and `qokain` on L13 continue the heat-transfer cycling. L14 closes with `chey` ("quick verification"), `chear` ("verify: yield, respond") -- final checks before the paragraph ends.

**Four material additions** (dar: 4) distributed across the paragraph -- each represents loading unfixed material onto the fixed for another sublimation pass. "Reiterate the sublimation" manifests as repeated dar + heat-cycle sequences.

**Match assessment:** Coherent. The paragraph's dominant structure -- cycling between heat application, transfer, observation, and material re-loading -- directly encodes iterated sublimation. The highest e-depth on the folio (0.64) captures active sublimation's heat-cool oscillation. Four material additions distributed across 8 lines encode the repeated loading of unfixed material. The paragraph size (80 tokens, 15% of the folio) reflects the recipe's emphasis on reiteration.

---

### P4 (Lines 15-17, 32 tokens) -- The Fusibility Test

**Recipe says:** "Test this by trying if it gives good fusion over fire. If it does, it's done; if not, add exuberated quicksilver..."

The critical test-point: apply the product to fire and see if it melts well. If yes -- the process is complete. If no -- add more material and continue.

**What the tokens say:**

P4 has **5 dar** (material additions) -- the highest material density of any paragraph on this folio (5 dar in 32 tokens = one addition per 6.4 tokens). The recipe says: if the test fails, "add exuberated quicksilver." The heavy material loading encodes the contingency: the test found the product not yet fusible, so additional mercury is being incorporated.

L15 opens with `pchoetal` (stage-test: arrange, stabilize, transfer, yield, state) -- a complex opening token that reads as staging the test: arrange the product, transfer it to the test position, note the state. Then `otedal` and `otal` (transfer monitoring) -- watch what happens when the material meets the fire. `oteedy` ("note gentle transfer rate") continues the observation.

Then: `daiin` ("start a new cycle") and `dar` ("add a new substance") -- the first material additions. The test has been performed and more material is needed. `okeedy` ("vessel at balneum temperature"), `qoky` ("cease heating") -- the vessel is managed between additions.

L16: Another `dar` opens the line -- continued material addition. `chedy` ("check the state"), `sheedy` ("extended observation"), `otal` ("note output rate"). Then the paragraph's only **transfer-watch**: `shcthy` (cth) -- passively watch the transfer. This is the fusibility observation: the operator watches how the material behaves when heat is applied. Does it flow? Does it melt cleanly? The transfer-watch encodes the visual assessment of fusion quality.

`qotey` ("transfer: stabilize, done"), `dain` ("bind material"), `otar` ("note drip rate") -- continuing the test-and-add cycle.

L17: `dain` ("bind material") -- another material binding. `chey` ("quick verification"), `qokeey` ("establish gentle heat"), two `okeey` ("vessel gently settled") -- verifying the state after additions. `qol` ("hold current heat level"), `chedy` ("check the state") close the paragraph with a final verification.

**Match assessment:** Coherent. The paragraph encodes the recipe's test-and-branch structure: heavy transfer monitoring (fusibility observation), one transfer-watch (watching the melt behavior), and five material additions (adding exuberated quicksilver when the test fails). The e-depth remains high at 0.62 -- the test requires active heating with careful temperature control.

---

### P5 (Line 18, 12 tokens) -- Branch Decision

**Recipe says:** "If it does, it's done; if not..."

A brief decision point between the test and the continuation.

**What the tokens say:**

Only 12 tokens on a single line. **Zero material additions.** This is not an operational paragraph -- it is a decision boundary.

L18: `pcharalor` -- a complex stage-test opener (yield, respond, yield, state, arrange, respond). Then `qokey` ("standard heat, done") -- one brief heat application. Four `ot`-prefix tokens: `otedy` ("check drip rate"), `otain` ("sustained transfer monitoring"), `otar` ("note drip rate"), `oteeedy` (triple-stabilization drip check). The paragraph is dominated by transfer-rate monitoring: the operator is watching whether the product flows.

`ches` ("check: cool, sequence") and `ary` close the paragraph. The product's fusion behavior has been assessed.

**Match assessment:** Coherent. A brief assessment paragraph with zero material additions and heavy transfer monitoring. The recipe describes a decision: is it fusible? The tokens encode watching the melt behavior. The paragraph's brevity (12 tokens, single line) matches the recipe's conditional -- this is a gate, not an operation.

---

### P6 (Lines 19-30, 140 tokens) -- Exuberation Cycle and Reiteration to Fusibility

**Recipe says:** "Add exuberated quicksilver, reiterating its sublimation until it is fusible."

If the test failed, the remedy is to add exuberated mercury and resume sublimation cycles until fusibility is achieved. This is the longest operational stretch in the recipe.

**What the tokens say:**

P6 is the largest paragraph on the folio -- 140 tokens across 12 lines (26% of the folio). The recipe dedicates most of its procedural text to this reiteration, and the folio allocates proportional space.

**Observation MIDDLE explosion.** P6 has **8 observation MIDDLEs** -- 4 transfer-watches (cth) and 4 heat-level checks (ckh). No other paragraph on this folio comes close. The recipe says to keep sublimating "until fusible" -- the operator must repeatedly check both the fire level and the transfer behavior to assess whether fusibility has been achieved. The dense monitoring encodes this iterative testing regime.

**Two quality checks** (`chekar`-class tokens) appear in P6. These are the first quality checks on the folio. The recipe says the endpoint is a quality assessment (good fusion over fire), and these tokens encode exactly that: is the product satisfactory?

L19: `qotain` ("sustained heat-driven transfer"), `qotar` ("transfer and note result") -- the sublimation cycling resumes. `chcthy` -- a **transfer-watch**: actively observe the transfer. `dain` ("bind material") -- load material for the cycle. The line reads: sublimate, watch the transfer, add material, iterate.

L20-L21: Heavy monitoring. `chedy`, `cheey`, `chol` (active verification), mixed with `otar`, `otedy` (transfer monitoring). `qokain` ("sustained cyclic heating") appears on L21 and L22. `shckhy` on L21 -- a **heat-level check**: is the fire right? `orchcthdy` on L21 -- a compound token containing both a transfer-watch and execution markers.

L22: `shcthy` -- a **transfer-watch** (passive): watch the transfer without intervening. `dar` ("add substance") -- another material addition. The operator adds mercury, watches the sublimate, checks: is it flowing better now?

L23: `dain` ("bind material"), then `qokal` ("fire reached target"), `qoteedy` ("gentle heat-driven transfer") -- the fire is at the right level; proceed with gentle sublimation. Two `shedy` ("watch the distillate") frame the transfer.

L24: `qokedy` ("maintain fire level") -- the single instance of this canonical fire-management token on the folio. `chcthy` -- another **transfer-watch**. `qokeey` ("establish gentle heat") -- maintain the balneum.

L25: `qokeey`, `qokeedy` ("gentle fire -- balneum level"), `shckhy` (**heat-level check**), `qokain` ("sustained cyclic heating"). The fire management intensifies: the operator adjusts, checks, sustains. This is deep into the reiteration -- precise control matters.

L26: `qokaiin` ("deep sustained cyclic heating") -- the only double-iterate heat token on the folio. This encodes the deepest level of sustained cycling: many iterations stacked. `chckhol` -- a **heat-level check** extended with arrangement and state markers. `qotey` ("transfer: stabilize, done"), `qotam` ("transfer operation finalized") -- a sublimation cycle completes.

L27-L28: `daiin` ("start a new cycle") on L27, `chckhy` (**heat-level check**) -- another fire check. `qoky` ("cease heating") -- a pause in the cycling. L28 shifts to equipment monitoring: `lchey`, `lkeey`, `lshalshy` -- checking seals and apparatus integrity. After many sublimation cycles, the equipment needs verification.

L29: `cheey`, `chear` ("verify: yield, respond"), `lkain` -- iterative binding continues. The observation density drops as the reiteration becomes more autonomous.

L30: `saraiin` (scaffold: extended iterative binding) -- deep iterative infrastructure. `qokain` ("sustained cyclic heating"), `chcthy` -- the final **transfer-watch** of the paragraph. `okaly` ("vessel: yield, state, done") closes the paragraph.

**Match assessment:** Coherent. The paragraph's scale (26% of the folio), observation density (8 obs MIDDLEs), quality checks (2), and material additions (4) all match the recipe's longest operational section. The 4 transfer-watches encode repeated fusibility assessment. The 4 heat-level checks encode the precise fire management needed for controlled sublimation. The `qokaiin` (deep sustained cycling) encodes the recipe's emphasis on reiteration "until fusible."

---

### P7 (Lines 31-36, 65 tokens) -- Composite Dissolution

**Recipe says:** "If you want it more composite and want it from mercury, dissolve another mercury in the first water exuberated from the soul of the mercury..."

The recipe offers an optional enhancement: dissolve additional mercury in the exuberated water to make the product more powerful. This is a dissolution operation, not sublimation.

**What the tokens say:**

P7 shifts the paragraph's character significantly. The `sh`-prefix (passive observation) count jumps to 12 -- the highest observer-density per token on the folio. The recipe says to dissolve mercury in the first water: dissolution is a *watching* process. You add the mercury to the liquid and observe whether it dissolves. Passive observation dominates because the operator is waiting for dissolution to complete rather than actively managing fire.

`qo`-prefix tokens (13) remain substantial -- heat is still needed to drive dissolution. But the ratio changes: P3 had 14 qo and 6 sh (heat-dominant); P7 has 13 qo and 12 sh (nearly balanced). The shift from heat-dominant to observation-heavy encodes the shift from sublimation to dissolution.

L31: `pchallarar` -- a complex stage-test opener. Then `ckhal` (adjust, heat, watch, yield, state) -- heat monitoring. `alolfchy` -- a compound token with "flag" atoms (f), which are rare in the corpus. This folio-specific token may encode a conditional operation specific to the composite path.

L32: `olkeey` ("continue: gently heat") -- maintain gentle heat during dissolution. Three `shey` ("watch briefly") tokens across the line -- repeated brief observations: is the mercury dissolving? `lchedy` ("check apparatus") -- verify the setup. `qokeedy` ("gentle fire -- balneum level") -- dissolution proceeds at balneum temperature.

L33: `qokain` ("sustained cyclic heating"), `sheey` ("extended observation"), `sheeky` (observe: cool, heat, done). The operator cycles between heating and watching. `cheds` and structural tokens close the line.

L34: Two `qokain` tokens, two `okain` ("seal vessel for cycle") -- sustained cycling with the vessel sealed. `shckhy` -- a **heat-level check**: is the fire right for dissolution? `qokam` ("heat stage finalized") -- a dissolution cycle ends.

L35: Three `qokeey` ("establish gentle heat") / `qokain` ("sustained cycling") tokens. `lchey` ("quick equipment check"), `cthar` (apparatus-watch: yield, respond). Two **heat-level checks** (`shckhy`) frame the heating -- careful thermal management as dissolution nears completion.

L36: One `dain` ("bind material") -- the paragraph's single material addition, loading the mercury to be dissolved. Then `chey` ("quick verification"), `sheckhy` (observe: cool, adjust, heat, watch). The paragraph closes with `qoklain` ("heat: state, yield, iterate, bind") -- sustained heat for the dissolution endgame.

**One quality check** (chekar: 1) -- the operator verifies: has the dissolution been adequate?

**Match assessment:** Coherent. The shift to observation-dominant operation (12 sh-prefix tokens) encodes the move from sublimation to dissolution. Two heat-level checks maintain careful temperature control. The single material addition on L36 corresponds to dissolving "another mercury" in the prepared water. The paragraph's moderate size (65 tokens) reflects the recipe's briefer treatment of this optional enhancement compared to the main sublimation reiteration.

---

### P8 (Lines 37-49, 142 tokens) -- Feces Cohobation

**Recipe says:** "Separate the water by distillation, reiterate distilling and redistilling over its feces until it has drunk the water and drawn all moisture from the mercurial feces. This is the wax-like moisture that resists fire above all others."

The final and most demanding operation: repeated distillation-and-redistillation over the feces (residue), cycling the water back onto the solid residue until all the moisture is absorbed. The endpoint is the "wax-like moisture" (humiditat encerativa) -- a product with extraordinary fire resistance.

**What the tokens say:**

P8 is the largest paragraph on the folio at 142 tokens (26% of the folio, effectively tied with P6). The recipe's two main operational blocks -- exuberation reiteration (P6) and feces cohobation (P8) -- receive nearly equal folio allocation. Both are iterative cycling processes; both get the most space.

**26 sh-prefix tokens** (passive observation) -- the highest count of any paragraph, even exceeding P7. Cohobation is an extended watching process: you distill the water off the feces, pour it back, redistill, and repeat. Most of the time is spent watching the distillate.

**24 qo-prefix tokens** (heat management) -- also the highest count, tied with the sheer volume of heat operations needed for repeated distillation cycles.

**4 heat-level checks** (ckh) plus 1 transfer-watch (cth) -- continued dense monitoring. The fire must be precisely managed through many distillation passes.

L37: `cheey` ("gently verify"), `lkeey` (equipment: gently settled), `olkeey` ("continue: gently heat"), `lchey` ("quick equipment check") -- establishing the setup for cohobation. `qoky` ("cease heating") -- a pause before beginning. `lshedy` ("monitor equipment") -- apparatus ready.

L38: `daiin` ("start a new cycle") -- the cohobation begins. `qokeey` ("establish gentle heat"), `qokain` ("sustained cyclic heating"), `qokeedy` ("gentle fire -- balneum level") -- heat ramps up through the balneum range. `chkar` -- a quality test (heat, yield, respond): is the distillate right?

L39: Two `qokain` tokens frame the line -- sustained cycling. `olkeey` ("continue: gently heat"), `keeey` (triple stabilization) -- extended gentle heating. The repeated `e` atoms encode the extremely gentle, sustained heat of cohobation: you are not trying to drive material up fast; you are slowly cycling water back onto residue.

L40: Observation intensifies. `dsheey`, `shey`, `shey` -- three passive observations in sequence. `qokain` ("sustained cycling"), `shckhy` (**heat-level check**) -- sustained heat with fire monitoring. `chedy` ("check state") -- active verification of progress.

L41: `shar`, `shar` -- two identical "observe: yield, respond" tokens in sequence. `sheain` ("observe: cool, yield, iterate, bind") -- observation tied to the iterative framework. `qokchy` ("heat: adjust, watch") -- fine-tune the fire. `chckhy` (**heat-level check**) -- is the fire right?

L42: The densest heat-cycling line on the folio. `qokain` appears three times, plus `sheckhy` (observe: heat-level check), `shekain` (observe: heat, iterate, bind), `shkain` (observe: heat, yield, iterate, bind). Heat management and observation are fully interleaved -- the operator cycles between firing and watching, firing and watching. The recipe says "reiterate distilling and redistilling" -- this line encodes the iterative core.

L43: `shear` ("observe: yield, respond"), `chcphy` (check: adjust, pause, watch) -- observation with deliberate pauses. `qokam` ("heat stage finalized") -- a distillation cycle completes.

L43a-L44: `qokain` ("sustained cycling"), `shckhy` (**heat-level check**), `lcheor` (equipment check), `okam` ("vessel: yield, final") -- another cycle completes. `shey` ("watch briefly"), `qokas` (heat: yield, sequence) -- monitoring sequence position within the iteration.

L45: `qokar` ("apply heat and note response"), `okey` ("vessel: stabilize, done"), `shcphhy` (observe: adjust, pause, watch -- extended) -- the first `hh` (double-watch) token. Extended observation encodes heightened attention: the operator is looking carefully for the endpoint. `oteey` ("note gentle transfer rate") -- is the water being absorbed?

L46: `chckhey` (check: heat-level plus cool, done), `qokey` ("heat, done"), `okeey` ("vessel gently settled"), `okal` ("vessel reached target") -- the process is converging. The vessel is stable; the fire is right; the product is settling.

L47: `dain` ("bind material") twice, `olkeey` ("continue: gently heat"), `qokar` ("apply heat and note response") -- final material bindings and heat. `otan` ("transfer: yield, bind"), `otain` ("sustained transfer monitoring") -- monitoring the last transfers.

L48: `sosar` (scaffold: sequence, yield, respond), `qokey` ("heat, done"), `cheey` ("gently verify"), `qor` ("heat: respond"), `aram` (yield: final) -- terminal tokens accumulate. The cohobation is ending.

L49 (final line): `sodal` (scaffold: do, yield, state) -- placing the final product. Then `chcthy` -- a **transfer-watch** (the paragraph's sole cth) paired immediately with `chckhy` -- a **heat-level check**. Transfer-watch plus heat-check as the final observation pair: the operator watches the product's behavior over fire one last time. This is the ultimate fusibility verification -- does the wax-like moisture withstand fire? `qol` ("hold heat level"), `ain` (yield, iterate, bind), `ary` (close) end the folio.

**One quality check** (chekar: 1) -- the final quality assessment of the cohobated product.

**Match assessment:** Coherent. The paragraph encodes cohobation's defining features: repeated gentle distillation (qokeey/qokeedy tokens, high e-content), extended observation (26 sh-prefix), four heat-level checks, one transfer-watch at the very end (paired with a heat check -- the final fusibility verification). The `hh`-extended observation token on L45 encodes heightened attention at the endpoint search. The final line's transfer-watch + heat-check pair directly encodes "trying if it gives good fusion over fire" -- the recipe's concluding test. Material additions (3 dar) are low because cohobation cycles the same water, not new substances.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | 0.42 | Sublimation -- sustained upward heat, minimal cooling |
| P2 | 0.55 | Fixation -- careful temperature management |
| P3 | **0.64** | Iterated sublimation -- peak heat-cool oscillation |
| P4 | 0.62 | Fusibility test -- active heating with careful control |
| P5 | 0.50 | Branch decision -- neutral |
| P6 | 0.50 | Exuberation reiteration -- balanced heat and observation |
| P7 | 0.57 | Dissolution -- moderate thermal management |
| P8 | 0.48 | Feces cohobation -- sustained gentle heat |

The e-depth traces two arcs across the folio. The first arc (P1-P4) rises from 0.42 to 0.64 and back to 0.62: sublimation setup (sustained heat) to iterated sublimation (peak heat-cool cycling) to the fusibility test. The second arc (P5-P8) descends from 0.50 to 0.48: the exuberation and cohobation phases operate at progressively more sustained, gentler heat. This matches the recipe: the early sublimation cycles are aggressive; the later cohobation ("distilling and redistilling over its feces") is gentle, patient, extended -- the operator coaxes the water into the residue rather than driving it.

### dar distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 1 | 5% | Sublimation setup -- one material loading |
| P2 | 1 | 5% | Fixation -- one binding |
| P3 | 4 | 21% | Iterated sublimation -- repeated loading of unfixed material |
| P4 | **5** | **26%** | Fusibility test + conditional addition -- heaviest loading |
| P5 | 0 | 0% | Branch decision -- no material action |
| P6 | 4 | 21% | Exuberation reiteration -- adding mercury |
| P7 | 1 | 5% | Dissolution -- one mercury addition |
| P8 | 3 | 16% | Feces cohobation -- minimal addition (cycling same water) |
| **Total** | **19** | | |

Material additions peak at P4 (5 dar, 26% of total) -- the paragraph where the fusibility test fails and the recipe says "add exuberated quicksilver." The iterated sublimation (P3) and exuberation reiteration (P6) each have 4 dar, encoding their repeated material cycling. The feces cohobation (P8) has only 3 dar despite being the largest paragraph because cohobation recycles the same water rather than adding new material. The zero-dar P5 (branch decision) perfectly encodes a decision point with no operational action.

### Observation MIDDLE distribution

| Para | ckh | cth | Total | Recipe activity |
|------|-----|-----|-------|-----------------|
| P1 | -- | -- | 0 | Sublimation setup (routine) |
| P2 | 1 | -- | 1 | Fixation: one heat-level check |
| P3 | -- | -- | 0 | Iterated sublimation (established process) |
| P4 | -- | 1 | 1 | Fusibility test: one transfer-watch |
| P5 | -- | -- | 0 | Branch decision (no thermal observation) |
| P6 | 4 | 4 | **8** | Exuberation: intensive monitoring regime |
| P7 | 2 | -- | 2 | Dissolution: heat checks only |
| P8 | 4 | 1 | **5** | Cohobation: dense heat monitoring + final fusibility check |

The observation MIDDLE distribution tells a clear story. P1-P5 (sublimation, fixation, test) have only 2 observation MIDDLEs total -- these are well-understood processes where the operator knows what to do. P6 explodes to 8 (4 ckh + 4 cth) -- the exuberation reiteration requires constant checking of both fire level and transfer behavior because the operator is searching for the fusibility endpoint. P8 has 5 (4 ckh + 1 cth) -- cohobation needs dense heat monitoring, and the single transfer-watch on the final line encodes the concluding fusibility verification.

The quality-check distribution reinforces this: 0 quality checks in P1-P5, then 2 in P6 (endpoint search), 1 in P7 (dissolution verification), 1 in P8 (final product assessment). Quality checking appears only after the fusibility test reveals the product is not yet done.

### Folio-level structural signature

Three features distinguish f116r from other cold-read folios:

1. **Transfer-rate dominance in P2.** Eight ot-prefix tokens in 33 tokens (24%) is the densest transfer-monitoring concentration per token on this folio. Fixation is diagnosed by what leaves the vessel -- when nothing more transfers, the material is fixed. The token distribution captures this diagnostic.

2. **The observation MIDDLE explosion in P6.** Eight observation MIDDLEs in a single paragraph is among the highest concentrations on any cold-read folio. The recipe demands iterative testing for an uncertain endpoint ("until fusible"), and the tokens encode this with dense monitoring.

3. **The P49 cth+ckh terminal pair.** The folio's final line has a transfer-watch immediately followed by a heat-level check -- the two observations needed for a fusibility assessment (watch how the material flows over fire, check the fire is at the right level). This directly encodes the recipe's endpoint: "trying if it gives good fusion over fire."

---

## Verdict: PARTIALLY COHERENT

*Revised from COHERENT after expert review. The iterative structure, fusibility test positioning, and two-part structure all match. However, zero fch mercury markers (C1939) on a recipe explicitly about mercury fixation is a critical diagnostic failure that prevents a COHERENT verdict.*

f116r produces a partially coherent paragraph-by-paragraph reading against III.4.0 (fixation and perfection / fusibility test). The folio's 8 paragraphs map to the recipe's procedural steps:

1. **Sublimation setup** (P1) -- sustained heat (e-depth 0.42), vessel handling, observation
2. **Fix first part** (P2) -- transfer-rate monitoring, one heat-level check, state verification
3. **Iterated sublimation** (P3) -- highest e-depth (0.64), 4 material additions, 14 heat-source tokens
4. **Fusibility test + conditional addition** (P4) -- heaviest material loading (5 dar), one transfer-watch
5. **Branch decision** (P5) -- 12 tokens, zero material additions, transfer monitoring
6. **Exuberation reiteration** (P6) -- largest paragraph (140 tokens), 8 observation MIDDLEs, 2 quality checks
7. **Composite dissolution** (P7) -- observation-dominant (12 sh-prefix), 2 heat-level checks
8. **Feces cohobation** (P8) -- largest paragraph (142 tokens), sustained gentle heat, final fusibility pair (cth+ckh on L49)

The recipe's three distinctive features -- iterated sublimation, a conditional fusibility test, and feces cohobation -- each have plausible token-level signatures. The e-depth arc captures the shift from aggressive sublimation (high oscillation) to patient cohobation (sustained gentle heat). The observation MIDDLE distribution concentrates in P6 and P8, where the recipe demands iterative endpoint testing. The dar distribution peaks at the conditional addition (P4) and drops during cohobation (P8), matching the recipe's material-handling pattern. The folio's final line encodes the recipe's concluding test -- transfer-watch plus heat-check: does the wax-like moisture withstand fire?

**Critical gap (expert review):** The recipe is explicitly about mercury fixation ("sublimated mercury," "mercurial feces," "quicksilver"). C1939 established that the fch atom pattern (mercury/mercury-water marker) is enriched on all 6/6 confirmed mercury-recipe folios. f116r has zero fch tokens anywhere on the folio. This absence prevents upgrading beyond PARTIALLY COHERENT: the structural profile (iterative fixation, fusibility test, cohobation) is consistent with a generic fixation recipe, but lacks the mercury-specific vocabulary expected from C1939. The folio may encode a fixation procedure from a different material context, or the fch diagnostic may not generalize to all mercury-adjacent recipes.
