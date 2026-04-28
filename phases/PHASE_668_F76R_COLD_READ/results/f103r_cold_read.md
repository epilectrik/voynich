# Cold Read: f103r ↔ III.16.0 Ferment Multiplication by Mixing

**Match tier:** Strong-supported
**Verdict:** Partially Coherent (revised from Coherent after expert review)

---

## The Recipe (III.16.0 — SISMEL Catalan, complete)

> Fill, si B metras aliter mets tu ab C, que son les dues cambres, mesclar s'[h]a tot en un per resolucio de liquefactio ab calor solament. Mas si tu ab l'aygua de la pedra vols fer ton mesclament, aquell serra millor, car es pres de unio de les coses miscibles que ja son alterades per les obres sobredites. Pren donques, fill, lo ferment de B e aquell de C; e cascu de aquels sia gitat en l'aygua roia. Puis ajusta les aygues e evapora aquells en lo bany de maria; e apres mit-ho sobre cenres e feu en la manera que t'havem dit en lo precedent capitol. E si veus que no flua, ajusta-li de l'ayre tant quant se pertendra, car de tant quant se minua en liquefacio, de tant se'n tira l'aygua per distillacio. E per aco te sia revelada la separacio de les quintes essencies. Restituit-li tot co qui ha perdut e mes, e hauras fet multiplicacio de composicio sobre altre compost...

*Cipher note: III.16 uses the Part III (Liber Mercuriorum) letter cipher: B = simple water, C = simple red sulphur, D = simple dissolved gold, E = compound red water, F = compound red sulphur, G = compound dissolved gold. This sub-recipe uses B and C explicitly — the "two chambers" — with later references to chamber combinations B F D H I in the philosophical discussion of multiplication.*

**Translation:** Son, if you put simple water (B) with simple red sulphur (C) — the two chambers — they will mix into one by liquefaction with heat alone. But if you use the stone's water for your mixing, it will be better, being closer to union of miscible things already altered by the preceding operations. Take then, son, the ferment of B and of C; throw each into the red water. Then combine the waters and evaporate them in the balneum mariae; then put it on ashes and fire in the manner described in the preceding chapter. If you see it doesn't flow, add air as needed — what diminishes in liquefaction is drawn as water by distillation. Through this the separation of the fifth essences is revealed to you. Restore all that was lost and more, and you will have made multiplication of composition upon another composite.

The recipe is a ferment multiplication procedure: combine two ferment substances through liquefaction, evaporate in balneum mariae, then process over ash-fire, test fluidity, and restore lost material by distillation. The key operational sequence is: **mix with heat** -> **balneum mariae evaporation** -> **ash-fire processing** -> **fluidity test** -> **distillation recovery** -> **quintessence separation**. The later philosophical discussion describes infinite multiplication by combining different chamber products.

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
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate x2, bind | Deep sustained cyclic heating — multiple iterations | PT-013 (15/15) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target — heat stage done | PT-013 (10/10) |
| qokeey | qo | k.e.e.y | fire: heat, stabilize x2, done | Establish gentle heat state | B Dict D1 |
| qokey | qo | k.e.y | fire: heat, stabilize, done | Brief heat application | B Dict D2 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qokar | qo | k.a.r | fire: heat, yield, respond | Apply heat and note the response | B Dict D1 |
| qotar | qo | t.a.r | fire: transfer, yield, respond | Transfer heat/material and note result | B Dict D1 |
| qotedy | qo | t.e.d.y | fire: transfer, stabilize, do, done | Execute a heat-driven transfer | B Dict D1 |
| qotal | qo | t.a.l | fire: transfer, yield, hold | Heat-driven transfer reached completion | B Dict D2 |
| qotain | qo | t.a.i.n | fire: transfer, yield, iterate, bind | Iterative heat-driven transfer | B Dict D2 |
| qoty | qo | t.y | fire: transfer, done | Heat transfer complete | B Dict D2 |
| qokechy | qo | k.e.c.h.y | fire: heat, stabilize, adjust, watch, done | Gentle-fire with active monitoring | Compositional |
| qokchey | qo | k.c.h.e.y | fire: heat, adjust, watch, stabilize, done | Monitored heat with adjustment | Compositional |
| qokechchy | qo | k.e.c.h.c.h.y | fire: heat, stabilize, adjust, watch x2, done | Double-monitored gentle fire | Compositional |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dain | da | i.n | material: iterate, bind | Bind material into the cycle | B Dict D1 |
| daiin | da | i.i.n | material: iterate x2, bind | Start a new cycle — initiate next loop | B Dict D0 |
| dal | da | l | material: hold/state | Carefully collect or place material | B Dict D0 |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state — verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| cheey | ch | e.e.y | test: stabilize x2, done | Extended active verification | B Dict D2 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chcthy | ch | c.t.h.y | test: adjust, transfer, watch, done | Watch the transfer (active) | B Dict D2 |
| checthy | ch | e.c.t.h.y | test: stabilize, adjust, transfer, watch, done | Watch a cooled transfer (active) | Obs. MIDDLE |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly — quick passive check | B Dict D1 |
| sheey | sh | e.e.y | watch: stabilize x2, done | Extended passive observation | B Dict D2 |
| shckhy | sh | c.k.h.y | watch: adjust, heat, watch, done | Passively observe the heat level | B Dict D2 |
| shcthy | sh | c.t.h.y | watch: adjust, transfer, watch, done | Watch the transfer (passive) | B Dict D2 |
| okeey | ok | e.e.y | vessel: stabilize x2, done | Vessel gently stabilized | B Dict D2 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal vessel for a processing cycle | B Dict D1 |
| okaiin | ok | a.i.i.n | vessel: yield, iterate x2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okeedy | ok | e.e.d.y | vessel: stabilize x2, do, done | Maintain vessel at gentle balneum temperature | B Dict D1 |
| okedy | ok | e.d.y | vessel: stabilize, do, done | Check vessel during cooling | B Dict D1 |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| otedy | ot | e.d.y | drip-rate: stabilize, do, done | Check drip/flow rate during cooling | B Dict D1 |
| oteey | ot | e.e.y | drip-rate: stabilize x2, done | Gentle transfer monitoring | B Dict D2 |
| otain | ot | a.i.n | drip-rate: yield, iterate, bind | Iterative transfer monitoring | B Dict D2 |
| otam | ot | a.m | drip-rate: yield, final | Transfer monitoring finalized | Compositional |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| saiin | sa | i.i.n | scaffold: iterate x2, bind | Begin extended binding iteration cycle | B Dict D1 |
| lchedy | lch | e.d.y | equipment: stabilize, do, done | Check equipment state during cooling | B Dict D1 |
| keedy | ke | e.d.y | steady-heat: stabilize, do, done | Steady-state thermal check | B Dict D2 |
| dy | -- | d.y | mark, done | Cycle close — action complete | B Dict D1 |
| am | -- | a.m | yield, final | Phase done — yield result and close | B Dict D0 |
| ol | -- | o.l | arrange, hold | Hold steady | B Dict D0 |
| lol | -- | l.o.l | state, arrange, state | Hold in arrangement | B Dict D2 |

**Observation MIDDLEs** — specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

---

## The Folio

**f103r:** 522 tokens, 54 lines, 12 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|---------------------|
| P1 | 1--4 | 49 | 4 | 0.49 | 1 ckh | Initial mixing: combine ferments with heat |
| P2 | 5--12 | 94 | 5 | 0.67 | 1 cth, 1 ckh | Balneum mariae evaporation |
| P3 | 13--17 | 51 | 1 | 0.63 | 1 cth, 1 ckh | Transfer and sustained heating |
| P4 | 18--20 | 29 | 0 | 0.48 | 1 ecth, 1 ckh | Sealed iterative cycling |
| P5 | 21--23 | 28 | 3 | 0.46 | 1 cth, 1 ckh | Ash-fire step: material addition under direct heat |
| P6 | 24--29 | 59 | 3 | 0.92 | 1 cth | Balneum mariae recovery: intense cooling/evaporation |
| P7 | 30--36 | 59 | 0 | 0.76 | 2 ckh, 1 cth | Sustained autonomous processing |
| P8 | 37--41 | 46 | 1 | 1.02 | 1 cth, 2 ckh | Distillation recovery — maximum cooling |
| P9 | 42 | 4 | 0 | 0.75 | -- | Observational pause |
| P10 | 43--47 | 42 | 0 | 1.05 | -- | Extended gentle distillation |
| P11 | 48--51 | 36 | 0 | 0.97 | -- | Autonomous separation — quintessence |
| P12 | 52--54 | 25 | 1 | 0.96 | -- | Final restitution and closure |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation, evaporation). Lower values = more sustained uninterrupted heat (liquefaction, direct fire). A value near zero means no thermal operation at all (vessel handling).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1--4, 49 tokens) — Initial Mixing

**Recipe says:** "If you put simple water (B) with simple red sulphur (C) — the two chambers — they will mix into one by liquefaction with heat alone."

The opening step: combine two ferment substances using heat. Liquefaction, not distillation — simple melting and mixing.

**What the tokens say:**

The paragraph opens with `pchedal` (stage-test: verify state) then moves into a sequence dominated by active monitoring (`ch` prefix appears 12 times — the highest active-test density on the entire folio). This is the most monitoring-intensive paragraph, consistent with a first step where the operator must carefully watch two substances combine.

L1 establishes the transfer apparatus: `qoteey` ("heat-driven transfer with gentle cooling") and `qotal` ("heat-driven transfer reached completion"). Two heat-transfer tokens on the opening line set up the physical arrangement. Then `shedy` ("watch the distillate") and observation tokens — watching as substances begin to merge.

L1--L2 contain four material additions: `dain` on L1 ("bind material into the cycle"), `dal` on L1 ("carefully place material"), and a second `dain` on L2, plus `daloky` ("material: careful placement with vessel heat management"). These four dar tokens in four lines map directly to the recipe's instruction to combine the ferments of B and C: two substances, each handled and introduced into the mixture.

L2 introduces monitoring: `chcphhdy` — an extended pause-watch token — and `chep` ("quick active check"). The recipe says "they will mix by liquefaction with heat alone," meaning the operator watches the substances dissolve into one another.

L3 is dominated by active checking: `cheoty`, `chokal`, `chedy`, `chckhy` — four consecutive `ch`-prefix tokens. The heat-level check (`chckhy`) on L3 asks: is the fire right for liquefaction? Then `okain` ("seal vessel for a processing cycle") — the mixture is enclosed for continued heating.

L4 shifts to fire management: `qokedy` ("maintain fire level"), `qokeey` ("establish gentle heat"). The mixing is proceeding, heat is stabilized. The paragraph closes with `chedar` — an active check noting the result of the mixing.

**Match assessment:** Coherent. Four material additions concentrated in the first two lines (combining two substances), heavy active monitoring (12 ch-prefix tokens), moderate e-depth (0.49) consistent with liquefaction rather than distillation, and fire management settling in by L4. Maps directly to "mix B with C by liquefaction with heat alone."

---

### P2 (Lines 5--12, 94 tokens) — Balneum Mariae Evaporation

**Recipe says:** "Take the ferment of B and of C; throw each into the red water. Then combine the waters and evaporate them in the balneum mariae."

The largest paragraph on the folio — 94 tokens across 8 lines. The balneum mariae evaporation is the recipe's core operation: combine the waters and evaporate.

**What the tokens say:**

The e-depth rises to 0.67 — a significant jump from P1's 0.49. More cooling intervention means more active evaporation control. The recipe says "evaporate in the balneum mariae," and higher e-depth encodes more thermal regulation, exactly what a water-bath evaporation requires.

L5 opens with vessel and observation work: `okedar` ("vessel: verify and note"), `shedy` ("watch the distillate"), `oteey` ("gentle transfer monitoring"). The apparatus is being set up for evaporation. Transfer-rate monitoring (`ot`-prefix tokens: 12 total in P2) is the highest of any paragraph — consistent with active evaporation where the operator watches liquid levels change.

L6 introduces the first material addition in P2: `dain` ("bind material into the cycle"). Then a **transfer-watch** (`shcthy`): passively observing the transfer happening inside the balneum. This is the paragraph's key observation MIDDLE — watching the evaporation process.

L7 establishes the balneum rhythm: `qokeey` ("establish gentle heat"), `olshedy` ("continue: watch the distillate") appearing twice. The operator maintains gentle water-bath heat and watches. `qoeedy` ("gentle cooling operation") — actively managing the bath temperature.

L8--L9: Dense vessel management with repeated `okey` ("vessel temperature settled"), transfer monitoring (`otar`, `otain`, `otey`), and iteration scaffolding (`rain`, `lkaiin`). The evaporation is running in cycles — condense, collect, repeat. `qoisol` on L8 ("heat: iterate in sequence and hold") and `qotar` ("transfer and note result") describe iterative heat-driven transfers.

L10 shows iteration machinery: `daiin` ("start a new cycle"), `otaiin` ("iterative transfer monitoring"), `sarain` ("scaffold: respond and iterate bind"). The process is running through multiple evaporation passes. Five material additions across P2 (the most of any paragraph) match the recipe's instruction to combine multiple ferment waters.

L11: `dar` ("add a new substance") — the last explicit material addition. Then heavy observation and iteration: `okain` ("seal vessel"), `qorain` ("heat: respond and iterate"), `qokeol` ("heat: stabilize in arrangement"). The balneum is running.

L12 closes with a **heat-level check** (`shckhy`): is the bath at the right temperature? Then `qokeol`, `keedy` — maintaining gentle heat. The paragraph ends with `otedy` ("check drip rate") — one final transfer-rate check as evaporation completes.

**Match assessment:** Coherent. The largest paragraph (94 tokens, 18% of folio) maps to the recipe's core operation. Elevated e-depth (0.67) encodes balneum mariae control. Heavy transfer-rate monitoring (12 ot-prefix tokens), five material additions (combining waters), one transfer-watch, and one heat-level check. The iteration tokens (`otaiin`, `sarain`, `lkaiin`) encode repeated evaporation cycles.

---

### P3 (Lines 13--17, 51 tokens) — Transfer and Sustained Heating

**Recipe says:** "Then put it on ashes and fire in the manner described in the preceding chapter."

Transition from balneum mariae to ash-fire processing — a different heat regime.

**What the tokens say:**

The e-depth remains moderate at 0.63, but the prefix distribution changes dramatically: `qo`-prefix tokens jump to 12 (fire management dominates), up from 10 in P2 despite half the token count. Heat source management is now the primary activity.

L13 opens with `podar` ("begin: material note") and immediately shifts to heat operations: `qotedy` ("heat-driven transfer"), `qokar` ("apply heat and note the response"), `qokain` ("sustained cyclic heating"). Three heat-source tokens in rapid succession — establishing the ash-fire. `checkhy` ("check heat level with cooling") on L13 includes the folio's only `eckh` compound — a precision heat verification before committing to sustained fire.

L14: `qokeechy` ("gentle fire with adjustment and monitoring") — the gentlest monitored heat token — followed by `qoky` ("cease heating"). The operator brings up heat, watches, adjusts, pauses. A **transfer-watch** (`chcthy`) on L14 observes what is being transformed under the new heat regime. This is the transition point: watching the product change from balneum-processed to ash-fire-processed.

L15: Three consecutive `qo`-prefix tokens: `qotedy` ("heat-driven transfer"), `qokeey` ("establish gentle heat"), `qotey` ("transfer and cool"). Heat-driven transfers are the primary activity — moving material through the ash-fire apparatus.

L16--L17 continue the heat-management cycle. `shckhy` on L16 — passively checking the heat level. L17 closes with `qokal` ("fire reached target") and `oty` ("transfer done") — the ash-fire step is wrapping up.

Only 1 dar token in this paragraph (`dal` on L13 — "carefully place material"). The recipe says "put it on ashes" — a single transfer of the already-mixed product onto the ash-fire setup.

**Match assessment:** Coherent. Fire management dominates (12 qo-prefix tokens in 51 total), one material placement (transferring product to ashes), one transfer-watch (observing transformation under new heat), and the e-depth of 0.63 encodes moderate cooling — ash-fire is hotter than balneum but the operator still intervenes.

---

### P4 (Lines 18--20, 29 tokens) — Sealed Iterative Cycling

**Recipe says:** (Continuation of the ash-fire process — "in the manner described in the preceding chapter" implies sustained iterative heating)

**What the tokens say:**

**Zero material additions.** The product is sealed and processing. The recipe describes a continuation of established procedure, and P4 encodes exactly that: pure operation with no new inputs.

The e-depth drops to 0.48 — the second-lowest on the folio. Less cooling means more sustained, uninterrupted heat. The ash-fire is running steadily.

L18 opens with a **cooled-transfer-watch** (`checthy` — ecth observation MIDDLE): the operator handles a cooled intermediate product. This is the only ecth on the entire folio — P4 marks the moment when the balneum-processed product is being moved into the ash-fire phase. Then heavy iteration: `okain` ("seal vessel"), `qokain` ("sustained cyclic heating"), `qokalshedy` — a compound token encoding heat reaching yield state followed by watching the distillate.

L19 is dense with iteration tokens: `okaiin` ("extended sealed processing"), `qokaiin` ("deep sustained cyclic heating"), `qokain` ("sustained cycling"). Three vessel-sealing iteration tokens on one line — the process is locked in and cycling.

L20 closes with a **heat-level check** (`shckhy`) and more cycling: `qokaiin`, `qokain`. The paragraph ends with `shedy` ("watch the distillate") — passive monitoring as the cycle runs.

**Match assessment:** Coherent. Zero material additions, low e-depth (sustained heat), dense iteration tokens, one cooled-transfer-watch (handling intermediate product), one heat-level check. This encodes sealed autonomous processing — the "manner described in the preceding chapter" running without intervention.

---

### P5 (Lines 21--23, 28 tokens) — Ash-Fire Step with Material Addition

**Recipe says:** "If you see it doesn't flow, add air as needed — what diminishes in liquefaction is drawn as water by distillation."

The fluidity test and corrective action: check the product, and if it has lost material, add more.

**What the tokens say:**

e-depth drops to 0.46 — the lowest on the folio. This is the most sustained heat, consistent with direct ash-fire work where the operator actively manages the flame rather than a water bath.

L21 opens with `pcheam` ("stage-test: yield and finalize") — a stage boundary. Then `sokedy` ("sequence: maintain fire level") and `dalkar` ("material: careful placement with heat and respond") — a material addition under heat with active response. `qokal` ("fire reached target") and `qoky` ("cease heating") follow: the fire is at the right level, then paused.

L22 introduces a **transfer-watch** (`chcthy`) — watching the transfer or transformation happening. This is the fluidity test: the operator actively watches whether the product flows. Three material additions appear in P5: `dalkar` on L21, `dalshy` on L22 ("material: careful placement while watching"), and `daiin` on L23 ("start a new cycle"). The recipe says "add air as needed" — these material additions are the corrective additions in response to the fluidity test.

L22 also has `qokeedy` ("gentle fire — balneum level") — a shift back toward gentler heat after the ash-fire intensity. The recipe is transitioning from direct fire toward recovery distillation.

L23 closes with a **heat-level check** (`chckhy`) and `lchedy` ("check equipment") — verifying the apparatus is ready for the next phase.

**Match assessment:** Coherent. The lowest e-depth (0.46) marks peak direct-fire work. Three material additions encode corrective additions ("add air as needed"). One transfer-watch captures the fluidity test. The transition to gentler heat at the end of P5 prepares for the recovery distillation that follows.

---

### P6 (Lines 24--29, 59 tokens) — Balneum Mariae Recovery

**Recipe says:** "What diminishes in liquefaction is drawn as water by distillation."

Recovery distillation: what was lost during the heat process is now recaptured by distilling.

**What the tokens say:**

The e-depth jumps dramatically to 0.92 — nearly double P5's 0.46. This is the sharpest e-depth transition on the folio: from the lowest (direct ash-fire) to one of the highest (intensive cooling and evaporation). The recipe describes transitioning from fire processing to distillation recovery, and the e-depth captures this precisely.

L24 opens with `tchoky` ("transfer check: arrange heat done") and establishes the distillation apparatus. `qokal` ("fire reached target"), then `qotain` ("iterative heat-driven transfer") — the recovery distillation begins. A **transfer-watch** (`shcthy`) appears on L24: passively watching the recovery distillate collect.

L24 also has `dain` ("bind material into the cycle") — material going into the recovery setup.

L25: `dar` ("add a new substance") plus `qokain` ("sustained cyclic heating"). The recovery distillation is running with material being processed. `chckhey` — a heat-level check with cooling — monitors the fire carefully. `okeeey` ("vessel: triple stabilization done") — an unusually deep cooling token, consistent with balneum mariae where extensive temperature regulation is essential.

L26--L27: Intensive cooling operation. L27 is particularly striking: `qokechy` ("gentle fire with active monitoring"), then three `qokeey`/`okeey` pairs — gentle heat operations alternating with vessel stabilization. The e-depth on these lines drives the paragraph's 0.92 average. The balneum is running at full evaporation capacity.

L28: `dalkain` ("material: careful placement with heat and iteration") — the third material addition. The recovery process draws material back through iterative distillation cycles.

L29 closes with `qokechchy` — a **double-monitored** gentle fire token (the only one on this folio). The operator is watching with extreme care as the recovery distillation reaches its peak. Then `qokeey` ("gentle heat") and `chedy` ("check the state") — final verification.

**Match assessment:** Coherent. The dramatic e-depth jump from 0.46 to 0.92 directly encodes the recipe's transition from ash-fire to recovery distillation. Heavy fire management with intensive cooling (qo-prefix: 15, the most of any paragraph), three material additions, and one transfer-watch. The double-monitored gentle fire token on L29 marks the operational peak.

---

### P7 (Lines 30--36, 59 tokens) — Sustained Autonomous Processing

**Recipe says:** "Through this the separation of the fifth essences is revealed to you."

The quintessence separation: a sustained process requiring patience and passive observation.

**What the tokens say:**

**Zero material additions.** The product is sealed inside the apparatus and the process runs itself. The recipe's philosophical statement — "the separation is revealed to you" — implies observation rather than action.

The e-depth moderates to 0.76 — still high but less extreme than P6. The recovery distillation is settling into a steady rhythm.

Passive observation dominates: `sh`-prefix appears 14 times (the most of any paragraph on this folio). The operator watches rather than acts. L30 opens with apparatus checking (`pcholkchdy` — "stage: arrange, hold, heat, adjust, watch, do, done"), then `sheckhy` ("observe: heat level check") — a compound observation token that embeds a heat-level assessment within passive watching.

L31 is dense with iteration: `soiin` ("sequence: iterate deeply"), `kaiin` ("heat to yield: iterate deeply"), three `okaiin` ("extended sealed processing") tokens across L31. The system is cycling autonomously.

Two **heat-level checks** (`shckhy` on L31, `shckhy` on L33) — both using the `sh` (passive) prefix rather than `ch` (active). The operator watches the fire level rather than testing it. This passive monitoring is consistent with autonomous processing where intervention is minimal.

L32: `qokedy` ("maintain fire level"), `qokal` ("fire reached target"), then a **transfer-watch** (`shcthy`) — watching the distillate transfer passively. The process is producing output that the operator simply observes.

L34--L35: `qokeedy` appears twice on L35--L36, `qokeey` appears three times on L36--L33. The gentle-fire tokens cluster in the later lines — the system is settling into steady balneum-level operation. L35 also has `shedain` ("observe: material binding in iteration") — watching material being drawn through the distillation cycle without intervening.

L36 closes with heavy gentle-heat management: `okeedy`, `qokeedy`, `qokeey` x2 — four gentle-temperature tokens on one line. The balneum is at a stable, sustained level.

**Match assessment:** Coherent. Zero material additions, passive observation dominant (14 sh-prefix), two heat-level checks (both passive), one transfer-watch, and dense iteration tokens. The e-depth of 0.76 encodes steady balneum processing. Maps to "the separation of the fifth essences is revealed" — the operator watches the quintessence emerge.

---

### P8 (Lines 37--41, 46 tokens) — Distillation Recovery (Maximum Cooling)

**Recipe says:** "Restore all that was lost and more."

The restitution phase: distillation recovers everything lost during the preceding heat steps.

**What the tokens say:**

The e-depth reaches 1.02 — the first paragraph above 1.0 on this folio. This is maximum cooling intervention: more stabilization atoms than any other paragraph. Intensive distillation recovery is exactly what "restore all that was lost" demands — aggressive evaporation-condensation to recapture material.

L37 opens with `pchedy` ("stage-test: verify state") followed by five consecutive `qo`-prefix tokens: `qokeey`, `qokeodair`, `qokshy`, `qokeedy`, `qokeedy`. Fire management at maximum intensity. The two `qokeedy` tokens in sequence ("gentle fire — balneum level" x2) emphasize sustained water-bath operation.

L38 is the monitoring peak: a **transfer-watch** (`shcthy`), two **heat-level checks** (`chckhy`, `checkhy`), plus `qokain` ("sustained cyclic heating"). Three observation MIDDLEs on a single line — the highest density on the folio. The operator is watching the recovery distillation with extreme attention: is the fire right? Is the transfer proceeding? Is the heat stable?

L39: `qokeey` ("gentle heat"), `qotal` ("transfer reached completion"), `shedy` ("watch the distillate"). The recovery is producing visible output.

L40: Heavy observation — five `sh`-prefix tokens including `shckhy` ("passively observe heat level") and `sheeol` ("extended observation"). Then `otam` ("transfer monitoring finalized") — the `m` (final) atom marks a terminal operation. The distillation recovery is nearing completion.

L41 closes with `qokeedy` ("gentle fire"), `qokal` ("fire reached target"), and `dal` ("carefully place material") — the paragraph's only material addition. The recovered distillate is being carefully collected.

**Match assessment:** Coherent. Maximum e-depth (1.02) encodes intensive distillation recovery. Three observation MIDDLEs on L38 mark the monitoring peak. The `otam` terminal on L40 signals approaching completion. One material addition at the end (collecting the recovered product). Maps to "restore all that was lost and more."

---

### P9 (Line 42, 4 tokens) — Observational Pause

**Recipe says:** (Implicit: pause between recovery and continued processing)

**What the tokens say:**

Only 4 tokens on a single line — the smallest paragraph on the folio:

```
L42:  tshey  sheol  cheolshy  chalal
```

Pure observation and checking: `tshey` ("observe: cool done"), `sheol` ("observe: arrangement state"), `cheolshy` ("check: arrangement, state, watch"), `chalal` ("check: yield state, yield state"). No fire management, no material, no transfer monitoring. Two `sh`-prefix (passive observation) and two `ch`-prefix (active checking) tokens.

The doubled `al.al` at the end of `chalal` is striking — a yield-state/yield-state construction that reads as "the product has reached stable state, confirmed stable." This is a verification that the distillation recovery produced a satisfactory product.

**Match assessment:** Coherent. A brief observational pause between intensive distillation recovery (P8) and the extended processing that follows (P10--P12). Zero dar, zero fire management — the operator pauses to verify the state of the product before continuing.

---

### P10 (Lines 43--47, 42 tokens) — Extended Gentle Distillation

**Recipe says:** "And you will have made multiplication of composition upon another composite."

The multiplication phase: the recovered product is processed further through extended gentle distillation to achieve multiplication.

**What the tokens say:**

The e-depth reaches the folio maximum at 1.05. Zero material additions, zero observation MIDDLEs. The process is running entirely through thermal cycling without intervention — the purest distillation paragraph on the folio.

L43 opens with `tar` ("transfer: respond") and `qotal` ("transfer reached completion"), `qokal` ("fire reached target") — the apparatus is functioning and producing results. Then `qokaiin` ("deep sustained cyclic heating") — multiple-iteration deep cycling.

L44: `qokeey` ("gentle heat") — balneum-level operation continuing.

L45 contains two identical `qokeedy` tokens in sequence — gentle balneum fire maintained through two consecutive passes. Then `qoteedy` ("gentle heat-driven transfer") and `oteedy` ("gentle transfer monitoring") — the distillation is producing output at a gentle, controlled rate.

L46: Four `qokeey` tokens appear on this line (three explicit, one `keey`). This is the highest concentration of gentle-heat tokens on the folio — sustained, steady balneum mariae operation for the multiplication process.

L47 closes with `qokaly` ("fire: heat, yield, state, done") and two `lch`-prefix equipment checks — verifying the apparatus as the process winds down.

**Match assessment:** Coherent. Maximum e-depth (1.05), zero material additions, zero observation MIDDLEs — pure autonomous distillation. The gentle-heat token concentration on L46 encodes sustained balneum processing. Maps to the multiplication phase where composition is built upon composition through extended processing.

---

### P11 (Lines 48--51, 36 tokens) — Autonomous Separation

**Recipe says:** (Continuation of the multiplication — the philosophical principle that "what diminishes is restored" operates through iterative processing)

**What the tokens say:**

The e-depth remains high at 0.97. Zero material additions, zero observation MIDDLEs. Like P10, this is pure autonomous processing.

L48 opens with `polarar` ("begin: respond, yield, respond") — a stage marker. Then `qotolaiin` ("heat: transfer in arrangement through deep iteration") — a compound transfer-iteration token encoding sustained heat-driven cycling. Two consecutive `qokeey` ("gentle heat") tokens follow — balneum maintained.

L49 includes `qokeedy` ("balneum fire"), `qoky` ("cease heating"), and the paragraph's quality check: `chekeey` on L51 ("check: stabilize, heat, stabilize deeply") — testing the product's quality after extended processing. This is the only `chekar`-class token in P11, providing a single verification point.

L50 shows the sustained cycling: `qokain` ("sustained cyclic heating"), `qotain` ("iterative heat-driven transfer"), `qokeey` ("gentle heat"). The balneum continues.

L51 closes with `saiin` ("extended binding iteration cycle") — scaffolding infrastructure for the iterative process.

**Match assessment:** Coherent. High e-depth (0.97), zero material additions, and one quality check. The process is running autonomously through its final iterative cycles. The quality check on L51 is the only intervention — verifying the product before closure.

---

### P12 (Lines 52--54, 25 tokens) — Final Restitution and Closure

**Recipe says:** "Restore all that was lost and more, and you will have made multiplication."

The final step: the last distillation pass restores what was consumed, completing the multiplication.

**What the tokens say:**

The e-depth remains high at 0.96. Fire management dominates: 12 `qo`-prefix tokens in 25 total (48%) — the highest qo-density of any paragraph on the folio. The operator is managing the fire with intense focus for the final pass.

L52 opens with `pchedal` ("stage-test: verify and yield state") — the same opening token as P1, creating a structural frame around the entire folio. Then `qokeey` ("gentle heat"), `qoty` ("heat transfer done"), and apparatus checking (`chepchy`, `qopchey`) — monitoring the final transfer. `lkaiin` ("equipment: deep iteration") — the apparatus is completing its last cycles.

L53 is the fire-management climax: `qokedy` ("maintain fire level"), `qokaiin` ("deep sustained cycling"), `qokeey` x3 ("gentle heat" repeated three times). Five gentle-fire tokens on one line — the balneum is running at full steady-state for the last time.

`chedy` ("check the state") and `lchedy` ("check equipment") provide verification — is the product ready? Is the apparatus functioning?

L54 closes the folio: `qoteeey` ("transfer: triple stabilization, done") — a deeply cooled transfer token, the only triple-e transfer on the folio. Then `darchedy` — the folio's final material token — "material: respond, adjust, watch, stabilize, do, done." This compound token encodes the final restitution: add back ("restore what was lost"), with monitoring and verification built into the single instruction. The folio's last two tokens are `qokey` ("brief heat") and `qoty` ("transfer done") — heat ceases, the process is complete.

**Match assessment:** Coherent. Maximum fire-management density (48% qo-prefix), high e-depth (0.96), and one material addition at the very end. The deeply-cooled transfer token `qoteeey` on L54 encodes the final, most carefully controlled distillation pass. The folio closes with `qoty` — transfer done — as the multiplication is complete.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | 0.49 | Liquefaction — moderate heat for mixing |
| P2 | 0.67 | Balneum mariae evaporation |
| P3 | 0.63 | Transfer and sustained heating |
| P4 | 0.48 | Sealed cycling — sustained direct heat |
| P5 | **0.46** | Ash-fire — lowest e-depth (peak direct heat) |
| P6 | **0.92** | Recovery distillation — sharp jump to high cooling |
| P7 | 0.76 | Autonomous processing — steady balneum |
| P8 | **1.02** | Maximum cooling — intensive distillation recovery |
| P9 | 0.75 | Brief observational pause |
| P10 | **1.05** | Extended gentle distillation — folio maximum |
| P11 | 0.97 | Autonomous separation |
| P12 | 0.96 | Final restitution |

The e-depth draws a distinctive two-phase arc. The first half (P1--P5) stays moderate to low (0.46--0.67), encoding the recipe's progression from mixing through ash-fire processing. Then P6 marks a dramatic jump to 0.92 — the transition from direct fire to recovery distillation. The second half (P6--P12) stays high (0.75--1.05), encoding sustained distillation and separation. The arc directly mirrors the recipe's structure: first heat-dominated operations (liquefaction, ash-fire), then cooling-dominated operations (recovery distillation, quintessence separation, multiplication).

The contrast between P5 (0.46, ash-fire) and P6 (0.92, recovery) is the most abrupt e-depth transition on the folio, corresponding to the recipe's pivot from "put on ashes and fire" to "what diminishes in liquefaction is drawn as water by distillation."

### dar distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 4 | 22% | Combining ferments of B and C |
| P2 | 5 | 28% | Adding waters for balneum evaporation |
| P3 | 1 | 6% | Single transfer to ash-fire setup |
| P4 | 0 | 0% | Sealed cycling (no additions) |
| P5 | 3 | 17% | Corrective additions (fluidity test) |
| P6 | 3 | 17% | Material for recovery distillation |
| P7 | 0 | 0% | Autonomous processing (no additions) |
| P8 | 1 | 6% | Collecting recovered distillate |
| P9 | 0 | 0% | Observational pause |
| P10 | 0 | 0% | Pure distillation (no additions) |
| P11 | 0 | 0% | Autonomous separation (no additions) |
| P12 | 1 | 6% | Final restitution |

Material additions concentrate in the first half: P1--P6 account for 16 of 18 dar (89%). The recipe's physical work — combining substances, adding corrective material, loading the recovery apparatus — is front-loaded. The second half (P7--P12) has only 2 dar tokens across 208 tokens, encoding autonomous processing where the apparatus runs without intervention.

The zero-dar stretch in P4 and P7--P11 (five of twelve paragraphs) marks phases where the product is sealed inside the apparatus and cycling through distillation without external input. The recipe's philosophical point — that multiplication occurs through the process itself, not through adding more material — is structurally encoded by this distribution.

### Observation MIDDLE distribution

| Para | ckh | cth | ecth | Total | Recipe activity |
|------|-----|-----|------|-------|-----------------|
| P1 | 1 | -- | -- | 1 | Heat check during mixing |
| P2 | 1 | 1 | -- | 2 | Balneum: heat check + transfer-watch |
| P3 | 1 | 1 | -- | 2 | Ash-fire: heat check + transfer-watch |
| P4 | 1 | -- | 1 | 2 | Sealed cycling: heat check + cooled-transfer |
| P5 | 1 | 1 | -- | 2 | Fluidity test: heat check + transfer-watch |
| P6 | -- | 1 | -- | 1 | Recovery: transfer-watch only |
| P7 | 2 | 1 | -- | 3 | Autonomous: double heat check + transfer-watch |
| P8 | 2 | 1 | -- | 3 | Distillation peak: double heat check + transfer-watch |
| P9 | -- | -- | -- | **0** | Observational pause (no monitoring) |
| P10 | -- | -- | -- | **0** | Pure distillation (no monitoring) |
| P11 | -- | -- | -- | **0** | Autonomous separation (no monitoring) |
| P12 | -- | -- | -- | **0** | Final closure (no monitoring) |

Observation MIDDLEs show a clean structural pattern: present in P1--P8, then completely absent in P9--P12. This is the **observation fade-out**: as the process becomes fully autonomous in the final third, the operator stops actively monitoring specific parameters. The recipe's transition from procedural instruction ("take... throw... combine... evaporate...") to philosophical statement ("the separation of the fifth essences is revealed... you will have made multiplication") corresponds exactly to this fade-out.

The single ecth (cooled-transfer-watch) appears in P4 — the moment when the product transitions from balneum processing to sealed cycling. The double ckh tokens in P7 and P8 mark the peak monitoring intensity during autonomous processing and distillation recovery, where getting the fire level right is critical.

---

## Verdict: PARTIALLY COHERENT

*Revised from COHERENT after expert review. The e-depth two-phase structure and dar front-loading are genuine matches, but the predicted ash-fire regime is absent and sa-prefix tokens do not concentrate in the multiplication phase as expected.*

f103r produces a partially coherent paragraph-by-paragraph reading against III.16.0 (ferment multiplication by mixing). The folio's 12 paragraphs map to the recipe's procedural steps, but with two structural tensions:

1. **Initial mixing** (P1) -- four material additions, heavy active monitoring, moderate heat for liquefaction
2. **Balneum evaporation** (P2) -- the largest paragraph (94 tokens), elevated e-depth, five material additions, transfer-watch
3. **Transfer to ash-fire** (P3) -- fire management dominant, one material placement, transfer-watch
4. **Sealed cycling** (P4) -- zero material, low e-depth (sustained heat), cooled-transfer-watch
5. **Ash-fire with correction** (P5) -- lowest e-depth on folio, three corrective material additions (fluidity test)
6. **Recovery distillation** (P6) -- dramatic e-depth jump to 0.92, three material additions, transfer-watch
7. **Autonomous processing** (P7) -- zero material, passive observation dominant, quintessence separation
8. **Maximum distillation** (P8) -- peak e-depth (1.02), three observation MIDDLEs on L38, transfer finalization
9. **Observational pause** (P9) -- four tokens, pure verification
10. **Extended distillation** (P10) -- folio maximum e-depth (1.05), zero material, pure autonomous processing
11. **Autonomous separation** (P11) -- high e-depth, quality check, iterative cycling
12. **Final restitution** (P12) -- maximum fire-management density, one final material addition, folio closes with `qoty` (transfer done)

The e-depth thermal arc is the strongest structural signal: a two-phase pattern where moderate values (0.46--0.67) in the first half encode mixing and direct-fire work, then a sharp transition at P6 to high values (0.75--1.05) encodes recovery distillation and quintessence separation. The pivot between P5 (0.46) and P6 (0.92) directly mirrors the recipe's transition from "put on ashes and fire" to "what diminishes in liquefaction is drawn as water by distillation."

The dar distribution (89% in P1--P6, 11% in P7--P12) encodes the recipe's front-loaded material handling versus back-loaded autonomous processing. The observation MIDDLE fade-out (present in P1--P8, absent in P9--P12) captures the transition from procedural instruction to the autonomous multiplication process.

These structural patterns do not depend on any individual token gloss — they are quantitative properties of the folio that align with the recipe independently.

**Tensions identified by expert review:**
1. **Ash regime absent.** The recipe specifies "aprés mit-ho sobre cenres" (then put on ashes), predicting a distinct low-e-depth fire phase. The first-half e-depth dip (0.46–0.67) is too mild to constitute a categorically different fire regime — the folio is dominated by a sustained balneum regime in its second half, with moderate variation in the first half.
2. **sa-prefix mislocated.** 5 of 8 sa-prefix tokens appear in P1–P3 (combination setup), not in P7–P12 (multiplication). The recipe's "in infinit se pot multiplicar" predicts scaffold/iterate tokens in the multiplication phase, but sustained cycling is encoded through qo-prefix dominance instead.
