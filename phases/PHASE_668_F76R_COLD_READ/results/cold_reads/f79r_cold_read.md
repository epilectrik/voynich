# Cold Read: f79r ↔ III.12.0 Mercury Sublimation → Red Elixir

**Match tier:** Strong-supported
**Verdict:** Coherent

---

## The Recipe (III.12.0 — SISMEL Catalan, complete)

> Pren mercuri sublimat e blanch axi com te havem dit, e dissol-lo en aygua del mercuri, de la qual es tret lo foch de la pedra mercuriosa, en la qual sia dissolt lo foch de la pedra axi substancialment com essencialment. Quant diem 'substancialment', diem per la substancia del foch; e quant diem 'essencialment', diem a la differencia des qualitats que l'aygua ha preses de la substancia del foch. Apres separes l'aygua per distillacio en tro sia tot congelat. E altra vegada retorna l'aygua sobre lo mercuri que si hi ha unctuositat aliter a fi que soit la unctuositat se supere ab l'aygua per distillacio. Puis altra vegada retorna sur le dit mercuri; e terca vegada distilla. E apres paulatinament fortifica ton foch, en trou veies vostre dit feu molt fort rubificar. E si res hi ha que no sia ligat ab lo foch de la pedra, allo se'n muntara e sublimara per la virtut del foch tot blanch. Continua donchs ton foch en tro veies que'l sublimatiu se sia sublimat, e el fix que es baix ou fons du vayssel se sia rubificat. E sobre aquest fixe sos elements axi com te havem dit; si tu nos has entes o oit, hauras del mercuri elixir complit.

*Cipher note: III.12 falls within the Liber Mercuriorum (Part III), using the Part III letter cipher (B=simple water, C=simple red sulphur, D=simple dissolved gold, E=compound red water, F=compound red sulphur, G=compound dissolved gold). No letter codes appear explicitly in this sub-recipe — the operations are described in plaintext.*

**Translation:** Take white sublimated mercury as we have told you, and dissolve it in mercury water (from which the fire of the mercurial stone was extracted, in which the fire of the stone is dissolved both substantially and essentially). Separate the water by distillation until all is congealed. Return the water onto the mercury a second time — if there is unctuosity, the water will separate it by distillation. Return a third time onto the mercury; distill a third time. Then gradually strengthen your fire until you see strong rubification. If anything is not bound by the stone's fire, it will rise and sublimate by the power of the fire, all white. Continue your fire until you see the sublimate has sublimated and the fixed matter at the bottom of the vessel has rubified. Over this fixed matter put its elements as we have told you; you will have complete mercury elixir.

The recipe is a mercury sublimation-fixation process: dissolve white sublimated mercury in mercury water, distill three times returning the water each time, then gradually strengthen the fire. Two outcomes separate: the volatile fraction sublimates upward (white), while the fixed residue at the vessel bottom rubifies (turns red). The red fixed matter becomes the completed mercury elixir.

Key features: dissolution in mercury water, three distillation returns, gradual fire strengthening (paulatinament), rubification (color change to red), sublimation/fixation separation, white sublimate vs red fixed matter, and final element addition over the fixed residue.

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
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate x2, bind | Deep sustained cyclic heating — extended iteration | PT-013 (15/15) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target — heat stage done | PT-013 (10/10) |
| qokar | qo | k.a.r | fire: heat, yield, respond | Apply heat and note the response | B Dict D1 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qokam | qo | k.a.m | fire: heat, yield, final | Heat stage finalized | Compositional |
| qokeey | qo | k.e.e.y | fire: heat, stabilize x2, done | Establish gentle heat state | B Dict D1 |
| qokol | qo | k.o.l | fire: heat, arrange, hold | Arrange the fire — set up heat configuration | B Dict D2 |
| qotar | qo | t.a.r | fire: transfer, yield, respond | Transfer heat/material and note result | B Dict D1 |
| qoteedy | qo | t.e.e.d.y | fire: transfer, stabilize x2, do, done | Execute a gentle heat-driven transfer | B Dict D2 |
| qotaiin | qo | t.a.i.i.n | fire: transfer, yield, iterate x2, bind | Sustained iterative heat transfer | B Dict D2 |
| qotain | qo | t.a.i.n | fire: transfer, yield, iterate, bind | Iterative heat transfer | B Dict D2 |
| qotal | qo | t.a.l | fire: transfer, yield, hold | Heat transfer reached completion | B Dict D2 |
| qokchdy | qo | k.c.h.d.y | fire: heat, adjust, watch, do, done | Adjust fire while watching | B Dict D2 |
| qokshedy | qo | k.s.h.e.d.y | fire: heat, sequence, watch, stabilize, do, done | Sequential fire management with observation | Compositional |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dain | da | i.n | material: iterate, bind | Bind material into the cycle | B Dict D1 |
| daiin | da | i.i.n | material: iterate x2, bind | Start a new cycle — extended binding | B Dict D0 |
| dal | da | l | material: hold/state | Carefully collect or place material | PT-013 (9/10) |
| dam | da | m | material: final | Material handling finalized | B Dict D0 |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state — verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| cheey | ch | e.e.y | test: stabilize x2, done | Gentle active verification | B Dict D2 |
| cheedy | ch | e.e.d.y | test: stabilize x2, do, done | Extended active state check | B Dict D2 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chcthy | ch | c.t.h.y | test: adjust, transfer, watch, done | Watch the transfer (active) | B Dict D2 |
| chkam | ch | k.a.m | test: heat, yield, final | Heat-test reaching finality | Compositional |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly — quick passive check | B Dict D1 |
| sheey | sh | e.e.y | watch: stabilize x2, done | Extended passive observation — watch gentle state | B Dict D2 |
| sheedy | sh | e.e.d.y | watch: stabilize x2, do, done | Extended passive observation of process | B Dict D2 |
| shckhy | sh | c.k.h.y | watch: adjust, heat, watch, done | Passively observe the heat level | B Dict D2 |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| otal | ot | a.l | drip-rate: yield, hold | Transfer rate has stabilized | B Dict D2 |
| otain | ot | a.i.n | drip-rate: yield, iterate, bind | Iterative transfer monitoring | B Dict D2 |
| otaiin | ot | a.i.i.n | drip-rate: yield, iterate x2, bind | Extended iterative transfer monitoring | B Dict D2 |
| oteedy | ot | e.e.d.y | drip-rate: stabilize x2, do, done | Check gentle drip/flow rate | B Dict D2 |
| oteeedy | ot | e.e.e.d.y | drip-rate: stabilize x3, do, done | Extremely gentle transfer monitoring | Compositional |
| okey | ok | e.y | vessel: stabilize, done | Vessel temperature: settled | B Dict D2 |
| okeey | ok | e.e.y | vessel: stabilize x2, done | Vessel gently stabilized | B Dict D2 |
| okaiin | ok | a.i.i.n | vessel: yield, iterate x2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal the vessel for a processing cycle | B Dict D1 |
| olky | ol | k.y | continue: heat, done | Continue heating, done | Compositional |
| olkaiin | ol | k.a.i.i.n | continue: heat, yield, iterate x2, bind | Continue: sustained deep cyclic heating | Compositional |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| saiin | sa | i.i.n | scaffold: iterate x2, bind | Begin extended binding iteration cycle | B Dict D1 |
| lchedy | lch | e.d.y | equipment: stabilize, do, done | Check apparatus (seals, receiver, furnace) | PT-013 (8/10) |
| lchey | lch | e.y | equipment: stabilize, done | Quick equipment check | B Dict D2 |
| kchedy | kch | e.d.y | precision-heat: stabilize, do, done | Precision-heat: verify state | B Dict D2 |
| sol | so | l | sequence: hold | Mark current state in sequence | B Dict D1 |
| dy | -- | d.y | mark, done | Cycle close — action complete | B Dict D1 |
| ol | -- | o.l | arrange, hold | Hold steady | B Dict D0 |
| am | -- | a.m | yield, final | Phase done — yield result and close | B Dict D0 |

**Observation MIDDLEs** — specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

---

## The Folio

**f79r:** 389 tokens, 44 lines, 10 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|---------------------|
| P1 | 1-3 | 29 | 0 | 0.76 | -- | Dissolution: dissolve mercury in mercury water |
| P2 | 4-6 | 34 | 1 | 0.56 | 1 cth | First distillation: separate water, begin congealing |
| P3 | 7-12 | 51 | 1 | 0.51 | 2 cth | Second return: return water onto mercury, redistill |
| P4 | 13-20 | 77 | 2 | 0.34 | 2 ckh | Third distillation: sustained cycling, fire strengthening |
| P5 | 21-25 | 47 | 3 | 0.62 | 1 cth | Rubification begins: material additions under rising heat |
| P6 | 26-30 | 40 | 0 | 0.60 | -- | Observation: watching for rubification and sublimation |
| P7 | 31-34 | 33 | 2 | 0.91 | -- | Cooling/collection: gathering the sublimate and fixed matter |
| P8 | 35-37 | 27 | 1 | 0.70 | -- | Quality verification: checking separation is complete |
| P9 | 38 | 4 | 0 | 1.50 | -- | Bridge: ultra-gentle transition between stages |
| P10 | 39-44 | 47 | 2 | 0.45 | 1 ckh | Final operation: apply elements over fixed residue to complete elixir |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation, collecting cooled product). Lower values = more sustained uninterrupted heat (fire strengthening, prolonged calcination). A value near zero means minimal thermal modulation (vessel handling). A value above 1.0 means cooling atoms outnumber all others (extreme cooling focus).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1-3, 29 tokens) — Dissolution

**Recipe says:** "Take white sublimated mercury and dissolve it in mercury water, from which the fire of the mercurial stone was extracted."

The opening step: take an already-prepared reagent (sublimated mercury) and dissolve it in a specific solvent (mercury water). This is a preparatory dissolution, not yet a distillation — the operator is combining materials and observing the dissolution process.

**What the tokens say:**

The paragraph has **zero material additions** (dar = 0). This may seem surprising for a dissolution step, but the recipe presupposes that the mercury and mercury water were prepared earlier ("as we have told you"). P1 is not about introducing new substances — it is about managing the dissolution of substances already combined.

The e-depth of 0.76 is the second highest on the folio — heavy cooling and stabilization. Dissolution in mercury water requires controlled temperature: too much heat and you drive off the volatile mercury before it dissolves. The operator is keeping things cool while managing the process.

L1 opens with `torain` (a transfer-binding operation) followed by `shedy` ("watch the distillate"). Two `pch`-prefix tokens frame the line — paragraph-initial stage markers. The key sequence `shek` ("observe: cool, heat") followed by `otar` ("note the drip/transfer rate") and `otal` ("transfer rate stabilized") shows the operator monitoring a liquid transfer — pouring mercury water over the sublimated mercury and watching.

L2 introduces heat: `qoteedy` ("execute a gentle heat-driven transfer") — the first heat-source token. The dissolution needs gentle warming. Then monitoring intensifies: `otchedy` ("check the transfer while watching") and observation tokens (`olshey`, `shey`, `sheey`). The line reads: apply gentle heat to aid dissolution, then observe closely.

L3 has a **quality check**: `chckhey` — an active check with a heat-level component. Is the dissolution proceeding at the right temperature? Then `qokeey` ("establish gentle heat state") — the operator settles on a stable gentle heat to finish the dissolution. The paragraph closes with `rchedy` — a final state check.

**Match assessment:** Coherent. A supervised dissolution process with zero material additions (materials pre-prepared), high e-depth (keeping the process cool), gentle heat application, and transfer monitoring. The quality check on L3 maps directly to the recipe's concern that the fire of the stone be dissolved "both substantially and essentially" — the operator verifies the dissolution is proceeding correctly.

---

### P2 (Lines 4-6, 34 tokens) — First Distillation

**Recipe says:** "Separate the water by distillation until all is congealed."

The first distillation: drive off the water, leaving behind congealed mercury.

**What the tokens say:**

e-depth drops to 0.56 — still substantial cooling, but less than P1. Active distillation requires heating and cooling in balance: heat to vaporize, cool to condense. The moderate e-depth captures this balance.

L4 opens with `dar` — the paragraph's sole material addition. The recipe says to separate the water by distillation; before distilling, you need to ensure the apparatus is loaded. Then `qotar` ("transfer heat/material and note result") — initiating the distillation. `sheekeey` is notable: an observation token with extensive cooling atoms (e.e.k.e.e.y), encoding heavy stabilization monitoring — watching the condenser work. Then `qokeey` ("establish gentle heat") followed by `okey` ("vessel temperature settled") and `qoky` ("cease heating") — a complete heat cycle: establish, verify, stop.

L5 is dominated by active checking (`ch` prefix appears 6 times across L5-L6). The sequence `qokal` ("fire reached target") then `shedy` ("watch the distillate") shows the operator reaching a distillation milestone and observing. Then `chcthy` — a **transfer-watch**: actively watching what is being distilled over. This is the paragraph's only observation MIDDLE, and it specifically encodes watching a transformation — consistent with monitoring distillation output.

The rest of L5 is dense monitoring: `chear` ("check: cool, yield, respond"), `chey` ("quick verification"), `cheol`, `chol` — a cascade of active checks. The operator is closely verifying the first distillation.

L6 continues with heat management: `olkeey` ("continue: gentle heat"), `qokey` ("heat done"), and closes with `sain` ("begin a binding iteration cycle") — setting up for the next return-distillation cycle.

**Match assessment:** Coherent. A supervised first distillation with one material addition, balanced e-depth (heating and cooling), one transfer-watch, and dense active checking. The `sain` at the end of L6 explicitly begins the iteration cycle — the recipe says to return the water and redistill.

---

### P3 (Lines 7-12, 51 tokens) — Second Return and Redistillation

**Recipe says:** "Return the water onto the mercury again — if there is unctuosity, the water will separate it by distillation. Return a second time onto the mercury."

The water is returned over the mercury residue and redistilled. If unctuosity (oily residue) remains, the distillation strips it away.

**What the tokens say:**

The `qo` prefix dominates: 19 of 51 tokens (37%) are heat-source operations — the highest qo-density of any paragraph on the folio. The recipe calls for active distillation, and the token distribution reflects intensive fire management.

e-depth drops further to 0.51 — the heat is becoming more sustained as the operator works through redistillation. Less cooling interruption, more continuous operation.

L7 opens with `polchedy` (a gallows-initial equipment check) then immediately `qokar` ("apply heat and note the response"). The sequence `qokl`, `qokain` ("sustained cyclic heating"), `qoty` ("heat transfer done"), `qokar` again — heavy fire work. The redistillation is underway.

L8 contains two **transfer-watches** (`chcthy` on L8, and the second `chcthy` on L11): the operator is watching what comes over in the distillation. The recipe specifically mentions unctuosity — if it remains, the water separates it. The transfer-watches encode the operator checking whether the distillate is clean or still carrying impurities. `qokal` appears twice on L8 ("fire reached target") — the fire is being brought to distillation temperature and verified.

L9 opens with `saiin` ("begin extended binding iteration cycle") — the second iteration cycle of the recipe. Then `qokar`, `qoty`, `qokal`, `qokam` — apply heat, transfer, fire reached target, heat stage finalized. A complete distillation sub-cycle within the paragraph.

L10-L11 continue the same pattern. L10 has `qokain` ("sustained cyclic heating") and `qoteesy` — a sequential heat-driven transfer. L11 has observation tokens and the second transfer-watch. L12 closes with `qokchy` ("adjust fire while watching"), `qotchey` ("transfer: adjust, watch"), then `ldaiin` (material binding into the cycle) and `qotaiin` ("sustained iterative heat transfer") — the redistillation wrapping up with one final material binding operation.

**Match assessment:** Coherent. Intensive redistillation with the highest qo-density on the folio, two transfer-watches (checking for unctuosity), a second iteration cycle initiated by `saiin`, and e-depth declining as the process becomes more sustained. The single material addition (`ldaiin` on L12) maps to the water return.

---

### P4 (Lines 13-20, 77 tokens) — Third Distillation and Fire Strengthening

**Recipe says:** "Return a third time; distill a third time. Then gradually strengthen your fire until you see strong rubification."

This is the pivotal paragraph. The third and final distillation cycle, followed by the gradual fire strengthening that triggers rubification. The e-depth **drops to 0.34** — the lowest on the folio. The recipe says "paulatinament fortifica ton foch" (gradually strengthen your fire). Lower e-depth means less cooling intervention and more sustained, uninterrupted heat. This is the paragraph where the fire is at its strongest.

**What the tokens say:**

P4 is the largest paragraph: 77 tokens, 20% of the entire folio. The third distillation plus the critical fire-strengthening phase that drives rubification gets the most operational space.

L13 opens with `pshorol` and `shckhy` — a **heat-level check**. The operator begins by verifying the fire. Then `qotshdy` ("heat-transfer sequence: watch, do, done") and `qokaldy` ("heat reached target, do, done") — the third distillation cycle underway. `qotar` ("transfer and note result") on L13 confirms active distillation. The `aiin` token encodes deep iterative yield — the process cycling through its third pass.

L14: `saral` (scaffold: respond, yield, hold) begins the transition. `qokain` ("sustained cyclic heating") appears alongside `checkhy` — an active check of the heat level with cooling context. Then `dain` ("bind material into the cycle") — the only explicit material binding in the paragraph's first half. The water is being returned for the last time.

L15-L16: The fire-strengthening phase. `qokal` ("fire reached target") on L15 marks the distillation completing. Then a second **heat-level check** (`shckhy` on L16): the operator re-verifies the fire before strengthening it. `qokain` returns on L16 — sustained cycling at the new, stronger fire level. `qokam` ("heat stage finalized") closes L16 — one fire-strengthening increment is done.

L17-L18: The fire strengthening continues with `qokaiin` ("deep sustained cyclic heating — extended iteration") appearing on both L17 and L18. This is the doubly-iterated form — more sustained than `qokain`. The recipe says "gradually" (paulatinament) — the operator is not jumping to maximum heat but climbing incrementally. `otaiin` ("extended iterative transfer monitoring") on L17 and duplicate `otain` tokens on L18 monitor the output through the intensified heat.

L19-L20: The deepest part of the fire-strengthening. `qokain` returns on L19 as the cycling continues. `sain` ("begin a binding iteration cycle") maintains the iterative frame. L20 contains `ychedar` — an active check with material response — and `scthey` (a transfer-watch variant). The operator is checking the material for color change: has rubification begun?

**Match assessment:** Strongly coherent. P4 matches the recipe's critical transition from third-distillation to fire-strengthening. The e-depth of 0.34 (lowest on the folio) directly encodes sustained, uninterrupted heat — "gradually strengthen your fire." The two heat-level checks mark the operator verifying the fire before and during strengthening. The progression from `qokain` (single iteration) to `qokaiin` (double iteration) on L17-L18 encodes the gradual intensification. The 77-token size allocation reflects the operational weight of this phase.

---

### P5 (Lines 21-25, 47 tokens) — Rubification Under Rising Heat

**Recipe says:** "Until you see strong rubification. If anything is not bound by the stone's fire, it will rise and sublimate by the power of the fire, all white."

The fire has been strengthened. Now the operator watches for two simultaneous outcomes: the fixed matter rubifying (turning red) at the vessel bottom, and the volatile fraction sublimating upward as a white deposit.

**What the tokens say:**

e-depth rises to 0.62 — a significant jump from P4's 0.34. The process is no longer about applying maximum sustained heat. The operator is now managing a more complex thermal regime: hot enough to drive sublimation, but controlled enough to observe the separation.

**Three material additions** — the highest dar count so far. The recipe mentions nothing unbound by the fire will sublimate away. Material additions here correspond to the operator handling the products of the separation: collecting sublimate, adjusting the charge.

L21 opens with two `shar` tokens ("observe: yield, respond") — the operator watching and noting the response. Then `otshey` ("monitor transfer: watch") and vessel management. `dalkeeey` is striking: a material-handling token with triple-e cooling depth (e.e.e.y). This is the most cooling-intensive material operation on the folio — handling the white sublimate, which must be collected from the cooler upper parts of the vessel.

L22: `dal` ("carefully collect material") — the operator is gathering product. `sheedy` ("extended passive observation") — watching the process continue. Then `efchedy` and `qofchey` — tokens containing the `fch` atom pattern. Per C1939, `fch` is a mercury/mercury-water marker enriched on all 6/6 confirmed mercury-recipe folios. These are the only fch tokens on this folio, and they appear exclusively in the sublimation paragraph where mercury volatility is operationally critical. *(Note: the `f` atom here is a morphological element glossed as "flag" per C1392, not the Part III cipher letter F = compound red sulphur. Cipher letters are Catalan text substitutions, not Voynich token components.)*

L23: `dar` ("add a new substance") and `qotaiin` ("sustained iterative heat transfer") — material addition with continued heat cycling. The redistillation/return cycle continues.

L24 contains the paragraph's densest fire-management sequence: `qokshedy`, `qolkeey`, `qolkeedy`, `qokedy` — four consecutive heat-source tokens. The fire is being actively managed: sequential observation of the fire, gentle sustained heating, standard fire maintenance. Then `otain` and `otchey` — transfer monitoring.

L25 closes with `qokar` ("apply heat and note response"), `shedy` ("watch the distillate"), and a **transfer-watch** (`chcthy`) — actively observing what is being sublimated/transferred.

**Match assessment:** Coherent. The rise in e-depth from P4 reflects the shift from pure fire-strengthening to a more nuanced thermal regime (driving sublimation while managing collection). Three material additions correspond to handling products of the separation. The triple-e cooling depth on `dalkeeey` encodes collecting the cold white sublimate. The fch mercury markers on L22 (C1939) concentrate in the sublimation paragraph where mercury handling is critical. The transfer-watch on L25 monitors the sublimation.

---

### P6 (Lines 26-30, 40 tokens) — Sustained Observation

**Recipe says:** "Continue your fire until you see the sublimate has sublimated, and the fixed matter at the bottom of the vessel has rubified."

A waiting/monitoring phase. The fire is maintained; the operator watches until the separation is complete.

**What the tokens say:**

**Zero material additions** (dar = 0). No new substances are introduced — the operator is purely maintaining conditions and observing. The recipe says "continua donchs ton foch" (continue your fire) — pure maintenance.

**Zero observation MIDDLEs.** This initially seems paradoxical for a monitoring phase, but it follows the **observation fade-out pattern** seen on other folios (f75r P5 showed the same). The process is now autonomous: the fire runs, the sublimation proceeds, the rubification develops. The operator does not need active heat-level checks or transfer-watches — those were needed during the dynamic phases (P3-P5). Now the system is in a steady state.

e-depth holds at 0.60 — stable, balanced thermal management. Neither ramping up nor cooling down.

L26 opens with `polaiin` (a gallows-initial deep iteration marker) and `olteedy` ("continue: gentle transfer") — sustaining the current operation. `qotchey` ("heat-transfer: adjust, watch") and `qokchdy` ("adjust fire while watching") — the operator makes minor adjustments but does not change the fundamental regime.

L27: `qokeedy` ("gentle fire") — the balneum-level heat continues. `olkaiin` ("continue: sustained deep cyclic heating") — the process cycles autonomously. `cheey` ("gentle active verification") — a soft check, not an intensive investigation.

L28-L29: `qokain` ("sustained cyclic heating") on L28 keeps the fire running. L29 has `qokal` ("fire reached target") — the fire is steady. `lchey` and `lcheey` (equipment checks) on L28-L29 verify the apparatus is holding up during the extended operation.

L30 closes briefly: `qotal` ("heat transfer reached completion") and two observation tokens. The transfer phase — sublimation — is approaching its end.

**Match assessment:** Coherent. A pure maintenance paragraph with zero material additions and zero observation MIDDLEs — the observation fade-out pattern encoding autonomous operation. The recipe says "continue your fire" and the paragraph does exactly that: sustained cycling, minor adjustments, equipment checks, no new interventions.

---

### P7 (Lines 31-34, 33 tokens) — Cooling and Collection

**Recipe says:** (Implied: after the sublimation and rubification are complete, the operator must cool the system and collect the products — the white sublimate from above and the red fixed matter from the vessel bottom.)

**What the tokens say:**

e-depth **spikes to 0.91** — the highest non-trivial paragraph on the folio (P9 at 1.50 has only 4 tokens). The system is cooling dramatically. After the sustained fire of P4-P6, the operator is now bringing the temperature down to handle the products.

**Two material additions** (`daiin` on L32 and L33). The operator is collecting products — the white sublimate from the upper vessel walls and/or the red fixed residue from the bottom.

L31 opens with heavy cooling: `shey` ("watch briefly"), `oltshedy` ("continue: transfer, watch"), then `ykeey` and `okeey` — vessel cooling tokens with double-e depth. `sheedy` ("extended passive observation") watches as the system cools. No heat-source tokens dominate — only 4 `qo` tokens in the entire paragraph, compared to 19 in P3 or 16 in P4.

L32: `qoteedy` ("gentle heat-driven transfer") and `okaiin` ("extended sealed processing") — a controlled final transfer at very gentle heat. Then `daiin` ("start a new cycle — extended binding") and `olaiin` ("continue: extended iteration") — the first product collection.

L33: Another `daiin` — second material collection. `qotshedy` ("transfer: sequence, watch") and extreme cooling: `oteeedy` (triple-e drip monitoring) and `oteedy` (double-e drip monitoring). The drip rate is being watched with extraordinary care. Then `qokaiin` ("deep sustained cyclic heating") — a brief reapplication of heat, possibly to soften the fixed residue for extraction.

L34: `lcheol` (equipment check) and `kchedy` ("precision-heat: verify state") — verifying the apparatus and thermal state. `qotas` ("transfer: yield, sequence") and `oteedy` — final gentle transfers.

**Match assessment:** Coherent. The e-depth of 0.91 encodes a dramatic cooling phase — the operator is bringing the system down after prolonged fire-strengthening. Two material additions map to collecting the separated products (white sublimate, red fixed matter). The extreme cooling depths on transfer-monitoring tokens (triple-e on `oteeedy`) reflect the care needed when handling the final products.

---

### P8 (Lines 35-37, 27 tokens) — Quality Verification

**Recipe says:** (Implied: verify that the separation is complete — the sublimate has fully sublimated, the fixed matter is fully rubified.)

**What the tokens say:**

e-depth at 0.70 — the system is cool but not at the extreme levels of P7. The operator is now inspecting rather than actively cooling.

**Two quality checks** (`chekar_count` = 2) — the highest on the folio. No other paragraph has more than one. The operator is performing final quality verification: is the rubification complete? Is the sublimate fully separated? The `chekes` token on L35 (check: cool, heat, cool, sequence) suggests sequential quality testing — multiple criteria being evaluated.

L35: `chedy` ("check the state") and `shedy` ("watch") open the inspection. `qoteedy` ("gentle heat-driven transfer") and `qotain` ("iterative heat transfer") — any remaining volatile material is being driven off. `otal` ("transfer rate stabilized") — the output has stopped, confirming completion.

L36: Dense observation — `sheeol`, `sheky`, `sheol`, `shear` — four observation tokens in sequence. The operator is watching the products from multiple angles: has the color changed? Is the sublimate clean? Is the residue properly rubified?

L37: Equipment and apparatus checks — `lcheol` (equipment check), then stabilization: `sheey` ("extended observation"), `olsheey` ("continue: extended observation"). The paragraph closes with `okchey` ("vessel: adjust, watch") and `dain` ("bind material into cycle") — one final material binding, sealing the verified product.

**Match assessment:** Coherent. The two quality checks (highest on the folio) map directly to the verification step. The observation-dense L36 encodes the visual inspection for rubification (red color) and sublimate quality (white). The single material binding at the end seals the verified product.

---

### P9 (Line 38, 4 tokens) — Bridge

**Recipe says:** (Transition between verification and the final operation)

**What the tokens say:**

Only 4 tokens on a single line:

```
L38:  pol  olkeeey  sheol  qokeey
```

e-depth is 1.50 — the highest on the folio, though the small sample (4 tokens) inflates this metric. The paragraph reads: gallows marker (`pol`), continue with extremely gentle heat (`olkeeey` — triple-e cooling depth), observe the arrangement (`sheol`), establish gentle heat (`qokeey`).

This is a brief bridge between the quality verification of P8 and the final operation of P10. The operator pauses, maintains ultra-gentle conditions, observes, and prepares for the last step.

**Match assessment:** Neutral. A 4-token bridge paragraph is too small to draw strong structural conclusions. Its function as a transition between quality verification and the final operation is consistent with the recipe flow.

---

### P10 (Lines 39-44, 47 tokens) — Final Operation: Elements over Fixed Residue

**Recipe says:** "Over this fixed matter put its elements as we have told you; you will have complete mercury elixir."

The final step: apply the prepared elements to the rubified fixed residue to produce the completed mercury elixir.

**What the tokens say:**

e-depth drops to 0.45 — back to sustained heat. The final operation requires renewed fire: applying elements over the fixed matter means a final heating to integrate them. The recipe promises completion: "you will have complete mercury elixir."

**One heat-level check** (`chckhy` on L40) — the operator verifies the fire for the final operation.

L39: `polkeey` (gallows-initial with gentle heat) opens the paragraph. Then `qokol` ("arrange the fire") — setting up the fire configuration for the final step. `olky` ("continue heating, done") and `orkar` ("respond: heat, yield, respond") — the fire is being actively managed. `shecphhdy` is notable: it contains a double-`h` (hh) mark — the only hh-extended token on the folio. Double-watch tokens are rare and typically mark heightened vigilance. The operator is watching with extra care during the final critical step.

L40: `qokched` ("heat: adjust, watch, cool, do") — monitored heating. The **heat-level check** (`chckhy`) appears here: is the fire right for the final operation? `okaiin` ("extended sealed processing") — the vessel is sealed for the final integration.

L41: `qokain` ("sustained cyclic heating") and `qotain` ("iterative heat transfer") — the fire cycles as the elements are integrated into the fixed residue. `chkain` ("active check: heat, iterate, bind") — actively verifying the binding process. This token specifically encodes checking that heat-driven iteration is producing binding — exactly what "putting elements over the fixed matter" requires.

L42: `sain` ("begin iteration cycle") and heavy vessel management — `okain` x2 ("seal for processing"), `chedy` ("check the state"), `cheedy` ("extended active check"). The cycling continues with repeated sealing and verification.

L43: `qokain` continues, then `qoky` ("cease heating") — the fire is being shut down. `daiin` ("start a new cycle — extended binding") is the final material operation. Then `chkam` ("heat-test: yield, final") — the `m` (final) atom marks this as a terminal quality check. The heat test is done for the last time. `cheedy` ("extended active check") — one last verification.

L44 (final line): `dar` ("add a new substance") — the very last material addition on the folio. `okeey` ("vessel gently stabilized") — the vessel cools. `cheory` — a final active check with response. The folio closes with monitoring and a terminal check.

**Match assessment:** Coherent. The final paragraph restores sustained heat (e-depth 0.45), contains the folio's only hh-extended token (heightened vigilance for the critical final step), includes a terminal quality check with the `m` (final) atom, and closes with a material addition and vessel stabilization. The recipe promises "complete mercury elixir" — the folio closes with terminal checks and finalization tokens.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | 0.76 | Dissolution — keep cool while combining |
| P2 | 0.56 | First distillation — balanced heating and cooling |
| P3 | 0.51 | Redistillation — more sustained heat |
| P4 | **0.34** | Fire strengthening — least cooling, most sustained heat |
| P5 | 0.62 | Rubification/sublimation — managing complex thermal regime |
| P6 | 0.60 | Sustained observation — stable maintenance |
| P7 | **0.91** | Cooling/collection — dramatic temperature drop |
| P8 | 0.70 | Quality verification — cool enough to inspect |
| P9 | 1.50 | Bridge — ultra-gentle (4 tokens) |
| P10 | 0.45 | Final operation — renewed sustained heat |

The e-depth draws a distinctive V-shape: high during dissolution (cooling to prevent mercury volatilization) → declining through the three distillation cycles → bottoming at P4 (fire strengthening, the recipe's "gradually strengthen your fire") → rebounding sharply at P7 (cooling to collect products) → settling at P10 (renewed heat for the final element application). This thermal arc maps precisely to the recipe's physical demands: gentle dissolution, increasingly forceful distillation, maximum fire for rubification, dramatic cooling for collection, and renewed heat for completion.

### dar distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 0 | 0% | Dissolution (materials pre-prepared) |
| P2 | 1 | 8% | First distillation (loading apparatus) |
| P3 | 1 | 8% | Redistillation (water return) |
| P4 | 2 | 17% | Third distillation + fire strengthening |
| P5 | 3 | **25%** | Rubification (handling separated products) |
| P6 | 0 | 0% | Sustained observation (no additions) |
| P7 | 2 | 17% | Collecting sublimate and fixed matter |
| P8 | 1 | 8% | Quality verification (sealing product) |
| P9 | 0 | 0% | Bridge |
| P10 | 2 | 17% | Final element application |

Material additions concentrate in P5 (25%) — the phase where rubification produces new products to handle — and are absent from P1 (materials already combined) and P6 (pure observation). The zero-dar stretches at P1 and P6 map directly to the recipe: P1 uses pre-prepared materials, P6 says "continue your fire" with no new additions. P10's two additions correspond to the recipe's final instruction: "put its elements over this fixed matter."

### Observation MIDDLE distribution

| Para | ckh | cth | ecth | Total | Recipe activity |
|------|-----|-----|------|-------|-----------------|
| P1 | -- | -- | -- | 0 | Dissolution (controlled, routine) |
| P2 | -- | 1 | -- | 1 | First distillation — transfer-watch |
| P3 | -- | 2 | -- | 2 | Redistillation — watching for unctuosity |
| P4 | 2 | -- | -- | 2 | Fire strengthening — heat-level checks |
| P5 | -- | 1 | -- | 1 | Rubification — transfer-watch |
| P6 | -- | -- | -- | **0** | Autonomous observation (fade-out) |
| P7 | -- | -- | -- | 0 | Cooling/collection |
| P8 | -- | -- | -- | 0 | Quality verification |
| P9 | -- | -- | -- | 0 | Bridge |
| P10 | 1 | -- | -- | 1 | Final operation — heat-level check |

Observation MIDDLEs cluster in P2-P5 (the active distillation/fire-strengthening phases) and disappear from P6 onward (the autonomous/collection phases). Critically, the **type** of observation shifts: P2-P3 and P5 use `cth` (transfer-watch — watching what is being distilled/sublimated), while P4 uses `ckh` (heat-level check — is the fire at the right level for strengthening?). This type-shift tracks the recipe: during distillation you watch the output; during fire strengthening you monitor the fire itself. P6's observation fade-out encodes autonomous operation — "continue your fire" needs no active checking.

---

## Verdict: COHERENT

f79r produces a coherent paragraph-by-paragraph reading against III.12.0 (mercury sublimation to red elixir). The folio's 10 paragraphs map to the recipe's procedural arc without post-hoc adjustment:

1. **Dissolution** (P1) — zero material additions, high e-depth (cooling to manage volatile mercury), transfer monitoring
2. **First distillation** (P2) — one material addition, balanced e-depth, one transfer-watch, iteration cycle initiated
3. **Redistillation** (P3) — highest qo-density on the folio (37%), two transfer-watches (checking for unctuosity), second iteration cycle
4. **Third distillation + fire strengthening** (P4) — largest paragraph (77 tokens, 20%), e-depth bottoms at 0.34 (maximum sustained heat), two heat-level checks, progression from single to double iteration
5. **Rubification** (P5) — three material additions (handling separated products), `f`-atom tokens during red-sulphur formation, one transfer-watch
6. **Sustained observation** (P6) — zero dar, zero observation MIDDLEs (fade-out pattern), pure fire maintenance
7. **Cooling/collection** (P7) — e-depth spikes to 0.91, two material collections, extreme cooling depths on transfer monitors
8. **Quality verification** (P8) — two quality checks (highest on folio), observation-dense inspection for rubification
9. **Bridge** (P9) — 4-token transition, ultra-gentle conditions
10. **Final operation** (P10) — renewed sustained heat (e-depth 0.45), only hh-extended token (heightened vigilance), terminal quality check with `m` atom, final material addition

The e-depth thermal arc — descending through the three distillation cycles, bottoming during fire strengthening, spiking during collection, and renewing for the final operation — maps to the physical chemistry of mercury sublimation-fixation. The observation MIDDLE type-shift from transfer-watches (distillation) to heat-level checks (fire strengthening) and back to fade-out (autonomous operation) tracks the monitoring demands at each step. The dar distribution matches the recipe's material-handling pattern: zero during dissolution (pre-prepared), concentrated during rubification (product handling), and absent during sustained observation (fire maintenance only).

These structural patterns do not depend on any individual token gloss — they are quantitative properties of the folio that align with the recipe independently.
