# Cold Read: f84r ↔ II.12.0 Gold Dissolution (Corruptible Water / Nigredo)

**Match tier:** CONFIRMED
**Verdict:** Coherent

---

## The Recipe (II.12.0 — SISMEL Catalan, complete)

> Tu en virtut de A pren una unce de l'aygua del compost de la luna distillada per alembich, e en aquella gita una unce de G vejetal; puis met dedins ton ***** [20] segons lo pes de G, e aprés posa-lo en bany per .ii. dies o quatre, e dedins lo dit terme trobaràs tot negre axí com a carbó. Puis met dedins .xii. parties de E, e puis mit tot ho a podrir per un mes e mig.

*Cipher note: II.12 uses the Part II (Liber Practicus) letter cipher. A = God (Déu), G = philosophical mercury (mercuri), E = menstrual (menstruall). The five-asterisk cipher word ***** [20] resolves via Tavola 2 to "or" (gold). The cipher system is distinct from Part III — in Part II, B = quicksilver (argent viu), C = salt of stone, D = vitriol azoqueous, E = menstrual, F = fine silver, G = philosophical mercury, H = gold.*

**Translation:** In virtue of God (A), take one ounce of the water of the composite of the moon distilled through alembic, and in it throw one ounce of vegetal mercury (G); then put in your gold according to the weight of mercury, and after put in a bath for 2 or 4 days. Within the said term you will find it all black like charcoal. Then put in 12 parts of menstrual (E), and then put everything to putrefy for a month and a half.

The recipe is short (386 characters in Catalan) and describes a three-stage dissolution process: (1) combine three substances — moon-water, mercury, and gold — in measured proportions; (2) digest in balneum mariae for 2–4 days until the mixture blackens (nigredo); (3) add menstrual and putrefy the whole for 45 days. The operation is primarily a prolonged sealed digestion with two distinct time-scales: a short bath phase (days) and a long putrefaction phase (weeks).

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
| qokeedy | qo | k.e.e.d.y | fire: heat, stabilize×2, do, done | Gentle fire — balneum / water-bath level | PT-013 (10/10) |
| qokeey | qo | k.e.e.y | fire: heat, stabilize×2, done | Establish gentle heat state | B Dict D1 |
| qokain | qo | k.a.i.n | fire: heat, yield, iterate, bind | Sustained cyclic heating | PT-013 (10/10) |
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate×2, bind | Deep sustained cyclic heating — sealed | PT-013 (15/15) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target — heat stage done | PT-013 (10/10) |
| qokar | qo | k.a.r | fire: heat, yield, respond | Apply heat and note the response | B Dict D1 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qokey | qo | k.e.y | fire: heat, stabilize, done | Heat stabilized — done | B Dict D2 |
| qotedy | qo | t.e.d.y | fire: transfer, stabilize, do, done | Execute a heat-driven transfer | B Dict D1 |
| qotar | qo | t.a.r | fire: transfer, yield, respond | Transfer heat/material and note result | B Dict D1 |
| qoty | qo | t.y | fire: transfer, done | Transfer complete | B Dict D2 |
| qol | qo | l | fire: hold | Hold current heat level | B Dict D1 |
| qoteedy | qo | t.e.e.d.y | fire: transfer, stabilize×2, do, done | Gentle heat-driven transfer | B Dict D2 |
| qokchedy | qo | k.c.h.e.d.y | fire: heat, adjust, watch, stabilize, do, done | Adjust fire while watching, stabilized | B Dict D2 |
| qokchy | qo | k.c.h.y | fire: heat, adjust, watch, done | Adjust fire while watching | Compositional |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dain | da | i.n | material: iterate, bind | Bind material into the cycle | B Dict D1 |
| daiin | da | i.i.n | material: iterate×2, bind | Start a new cycle — deep binding | B Dict D0 |
| dal | da | l | material: hold/state | Carefully collect or place material | PT-013 (9/10) |
| dam | da | m | material: final | Material handling finalized | B Dict D0 |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state — verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chcthy | ch | c.t.h.y | test: adjust, transfer, watch, done | Watch the transfer (active) | B Dict D2 |
| checthy | ch | e.c.t.h.y | test: stabilize, adjust, transfer, watch, done | Watch a cooled transfer (active) | Obs. MIDDLE |
| chekar | ch | e.k.a.r | test: stabilize, heat, yield, respond | Quality check — is the product right? | B Dict D2 |
| checkhy | ch | e.c.k.h.y | test: stabilize, adjust, heat, watch, done | Check stabilized heat level | B Dict D2 |
| cheky | ch | e.k.y | test: stabilize, heat, done | Quick thermal check | B Dict D2 |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly — quick passive check | B Dict D1 |
| sheedy | sh | e.e.d.y | watch: stabilize×2, do, done | Extended passive observation | B Dict D2 |
| shckhy | sh | c.k.h.y | watch: adjust, heat, watch, done | Passively observe the heat level | B Dict D2 |
| shekar | sh | e.k.a.r | watch: stabilize, heat, yield, respond | Passive quality check — note the product | Compositional |
| shekam | sh | e.k.a.m | watch: stabilize, heat, yield, final | Passive quality check approaching finality | Compositional |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| otedy | ot | e.d.y | drip-rate: stabilize, do, done | Check drip/flow rate during cooling | B Dict D1 |
| oteey | ot | e.e.y | drip-rate: stabilize×2, done | Gentle drip-rate check | B Dict D2 |
| oteedy | ot | e.e.d.y | drip-rate: stabilize×2, do, done | Extended gentle drip-rate check | B Dict D2 |
| okey | ok | e.y | vessel: stabilize, done | Vessel temperature: settled | B Dict D2 |
| okedy | ok | e.d.y | vessel: stabilize, do, done | Check vessel during cooling | B Dict D1 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal the vessel for a processing cycle | B Dict D1 |
| okaiin | ok | a.i.i.n | vessel: yield, iterate×2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okal | ok | a.l | vessel: yield, hold | Vessel at target state | B Dict D2 |
| olky | ol | k.y | continue: heat, done | Continue heating, done | Compositional |
| saiin | sa | i.i.n | scaffold: iterate×2, bind | Begin extended binding iteration cycle | B Dict D1 |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| keedy | ke | e.d.y | steady-heat: stabilize, do, done | Steady-state thermal check | B Dict D2 |
| pchedy | pch | e.d.y | stage-test: stabilize, do, done | Stage-test: verify state (paragraph opener) | B Dict D2 |
| dy | — | d.y | mark, done | Cycle close — action complete | B Dict D1 |
| am | — | a.m | yield, final | Phase done — yield result and close | B Dict D0 |
| ol | — | o.l | arrange, hold | Hold steady | B Dict D0 |
| sol | so | l | sequence: state | Mark current state in sequence | B Dict D1 |

**Observation MIDDLEs** — specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

---

## The Folio

**f84r:** 361 tokens, 34 lines, 3 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|---------------------|
| P1 | 1–12 | 158 | 9 | 0.58 | 6 ckh, 2 ecth, 1 cth | Combine reagents + balneum digestion (2–4 days to nigredo) |
| P2 | 13–14 | 21 | 1 | 0.48 | 2 cth, 1 cthh | Transfer product + add menstrual |
| P3 | 15–34 | 182 | 15 | 0.50 | 5 ckh, 2 cth | Putrefaction (1.5 months, long sealed digestion) |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation). Lower values = more sustained uninterrupted heat (fermentation, autonomous cycling). A value near zero means no thermal operation at all (vessel handling).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1–12, 158 tokens) — Combine Reagents + Balneum Digestion

**Recipe says:** "Take one ounce of the water of the composite of the moon distilled through alembic, and in it throw one ounce of vegetal mercury; then put in your gold according to the weight of mercury, and after put in a bath for 2 or 4 days. Within the said term you will find it all black like charcoal."

This is the bulk of the recipe's procedural content: combine three substances in measured proportions, seal them in a water bath, and maintain heat until blackening occurs. P1, the folio's largest paragraph by token density per line (158 tokens / 12 lines = 13.2 tokens/line), encodes the most operationally demanding phase — both the careful preparation of reagents and the multi-day supervised digestion.

**What the tokens say:**

**L1 — Apparatus setup.** The line opens with structural framing (`lmyl`) and a heat-source prefix (`kal`), then moves through state verification (`chedy` — "check the state"), gentle heat establishment (`qokeey` — "establish gentle heat state"), and vessel management (`okeedy` — "maintain vessel at gentle temperature", `olshed` — "load the vessel while watching"). Two transfer-rate checks (`otedy`, `qotedy`) indicate the apparatus is being warmed and flow paths are being verified. This reads as the initial setup: bring the equipment to temperature, load it, observe.

**L2 — First material loading under observation.** `shekar` ("passive quality check — note the product") on L2 opens with a quality observation — the moon-water is being evaluated. A material addition appears mid-line: `dal` ("carefully place material"). Then a dense cluster of heat-level checks: `chckhdy` and `schckhy` — both encoding **ckh** (is the fire right?). The recipe says to distill the moon-water through alembic; these heat-level checks monitor the initial distillation temperature. The line ends with `qokeey` ("establish gentle heat") — the bath is coming up.

**L3 — Material addition + sustained heating.** Two `dar` ("add a new substance") tokens appear — the first line with two material additions on the folio. Between them: `shedy` ("watch the distillate"), `qokedy` and `qokeedy` ("maintain fire" and "gentle fire — balneum level"), `chedy` ("check the state"). The recipe specifies adding mercury and then gold "according to the weight" — two distinct material additions requiring weighing and observation. The line closes with `okain` ("seal the vessel for a processing cycle") — after both reagents are in, the vessel is sealed.

**L4 — Observation intensifies.** `okedy` ("check vessel during cooling") opens the line. Two `shedy` tokens frame the middle — passive observation. `shckhy` ("passively observe the heat level") is another **ckh** observation MIDDLE: is the balneum at the right temperature? `qokal` ("fire reached target") confirms the heat has stabilized. The recipe says "put in a bath for 2 or 4 days" — the operator has loaded the vessel, sealed it, brought the bath to temperature, and is now monitoring.

**L5–L6 — Sustained bath monitoring.** L5 has dense heat-source activity: `qotedy` ("heat-driven transfer"), `qokeedy` ("gentle fire — balneum"), `qokeey` ("establish gentle heat"), `qokedy` ("maintain fire level"). The balneum is running. L6 intensifies observation: `shedy` appears twice, framing `qokedy`. Then a critical pair: `shckhy` + `chckhy` — a passive heat-level check immediately followed by an active heat-level check. Two consecutive ckh observations: the operator is verifying the bath temperature both by looking (passive) and by testing (active). Another `chckhy` follows after a material handling operation (`dal`). Three heat-level checks on one line — the most on any line in this paragraph. The recipe says 2–4 days in a bath; during extended balneum operations, temperature stability is the primary concern.

**L7 — Cyclic heating begins.** Two `qokain` ("sustained cyclic heating") tokens plus `qotedy` ("heat-driven transfer") and `qolkeey` (hold at gentle heat). The digestion has moved from setup to autonomous cycling. `salchedy` ("check apparatus in scaffold cycle") closes the line — equipment verification during the long run.

**L8 — The turning point (cooled-transfer-watch pair).** `qokeedy` ("gentle fire — balneum") and `qokedy` ("maintain fire") maintain the bath. But mid-line, two `checthy` tokens appear — **cooled-transfer-watches** (ecth). These are the only ecth observations in P1, and they appear consecutively on the same line, flanking a `dar` ("add a new substance"):

```
L8:  ... qokeedy  dy  qokedy  daiin  shckhedy  qokaiin  checthy  dar  checthy  am
```

Two cooled-transfer-watches around a material addition. The recipe says "you will find it all black like charcoal" — the blackening (nigredo) is the diagnostic moment. The operator is handling the product as a cooled intermediate, observing its transformation, adding material, observing again. The ecth observation MIDDLE specifically encodes watching a cooled product being handled. The line closes with `am` ("phase done — yield result and close") — the digestion phase is reaching its conclusion.

**L9 — Quality verification.** Dense monitoring: `qokaiin` ("deep sustained cyclic heating"), then four ch-prefix tokens in quick succession — `chol` ("check arrangement"), `cheky` ("quick thermal check"), `chey` ("quick active verification"), `chedy` ("check the state"). The operator is testing the product: has the blackening progressed? Is the temperature stable? `okal` ("vessel at target state") and `okaly` ("vessel at target — done") confirm the vessel state is satisfactory.

**L10 — New material addition with heat management.** `qokal` ("fire reached target") anchors the line. Heavy heat management: `qokedy`, two `qokeedy` ("gentle fire — balneum"). A `dar` ("add a new substance") at line-end — the 9th and last material addition in P1. The recipe mentions adding gold "according to the weight of mercury"; the careful spacing of additions across the paragraph (9 dar over 12 lines, never more than 2 per line) reflects the measured, weight-conscious loading described in the recipe.

**L11 — Transfer observation.** `dar` opens the action, followed by `shcthy` — a **transfer-watch** (cth). The operator is observing the material being transformed. Then `qotedy` ("heat-driven transfer") and `qolchey` ("hold and check apparatus"). Heavy observation: four sh-prefix or ch-prefix tokens on the line. `daiin` ("start a new cycle") near line-end signals the process is cycling.

**L12 — Final heat management.** `qokedy` ("maintain fire"), `qokar` ("apply heat and note the response"), `chckhy` ("check the heat level") — the last ckh observation in P1. `qokchedy` ("adjust fire while watching, stabilized") and `qokaiin` ("deep sustained cyclic heating") close the paragraph. The balneum is settled into its long run, heat verified one last time.

**Match assessment:** Coherent. P1 encodes the recipe's combined preparation-and-digestion phase. Nine material additions across 12 lines match the recipe's three weighed substances (moon-water, mercury, gold) plus process-maintenance additions during the multi-day bath. The e-depth of 0.58 — moderate, with significant cooling/stabilization intervention — is consistent with a balneum mariae operation where temperature must be actively managed. Six ckh (heat-level check) observations reflect the 2–4 day bath duration: when you maintain a water bath for days, you check the fire frequently. The paired ecth (cooled-transfer-watch) observations on L8 mark the nigredo diagnostic — the moment the operator handles the product and sees the blackening.

---

### P2 (Lines 13–14, 21 tokens) — Transfer + Add Menstrual

**Recipe says:** "Then put in 12 parts of menstrual."

A brief transitional step: the blackened product from the bath is handled, and 12 parts of menstrual (E) are added.

**What the tokens say:**

P2 is strikingly small — only 21 tokens on 2 lines. The recipe step it maps to is equally brief: a single sentence about adding menstrual.

**L13 — Transfer-heavy.** The prefix distribution tells the story: `ot` (transfer-rate) appears 5 times on this 13-token line — more transfer-rate tokens than any other line on the folio. The line opens with `pchedy` ("stage-test: verify state") — the standard paragraph-opening verification. Then `qotchedy` ("transfer with adjustment while watching") — a heat-driven transfer under observation. `otaiiin` ("transfer-rate: yield through deep iteration cycles") — an extended transfer monitoring token with triple-i (iterate×3), the deepest iteration depth on the folio. `chcthy` ("watch the transfer") — a **transfer-watch** (cth).

The dominance of transfer-rate tokens (5 of 13) and the transfer-watch observation encode the product being physically moved from the bath vessel to a new one. After 2–4 days sealed in the balneum, the blackened mixture is being decanted or poured.

**L14 — Material addition + gentle heat.** `shcthhy` — a **transfer-watch with extended observation** (cthh — the doubled `h` encodes "watch, watch" — prolonged scrutiny of the transfer). The operator is watching the black product move, examining it carefully. Is it fully blackened? Is the consistency right? Then `dar` ("add a new substance") — the menstrual is being added. `shcthy` follows — another transfer-watch after the addition. The operator watches the menstrual mix with the blackened product.

The line closes with `qokeedy` ("gentle fire — balneum level") and `olkey` ("continue: heat, done") — establishing the gentle heat regime that will carry into P3's putrefaction.

**Match assessment:** Coherent. A brief transitional paragraph dominated by transfer operations (4 ot-prefix tokens on L13, 1 on L14) and transfer-watches (3 cth/cthh observations across 2 lines). One material addition (`dar`) maps directly to "put in 12 parts of menstrual." The e-depth drops to 0.48 from P1's 0.58 — the product is being handled at a cooler state between the active bath phase and the coming putrefaction. The extended transfer-watch (`shcthhy` with doubled h) encodes the careful inspection of the nigredo product: the operator needs to verify that the blackening is complete before committing to 45 days of putrefaction.

---

### P3 (Lines 15–34, 182 tokens) — Putrefaction

**Recipe says:** "And then put everything to putrefy for a month and a half."

The final phase: 45 days of sealed, sustained digestion. This is the longest duration in the recipe by far — 2–4 days for the bath versus 45 days for putrefaction. P3, at 182 tokens (50% of the folio), is correspondingly the largest paragraph. The folio allocates its space in proportion to the duration of each phase.

**What the tokens say:**

**L15 — Initial loading.** `shcthy` — a **transfer-watch** (cth) — the product from P2 is being observed as it enters the putrefaction vessel. `olky` ("continue: heat, done") and `dar` ("add a new substance") — loading materials. `oraiiin` ("vessel response: deep iteration") — the vessel is being prepared for a long run with triple-i iteration depth. The deep iteration atoms (i.i.i.n) recur on this folio specifically at moments of preparation for extended processing.

**L16 — Vessel sealing for long cycle.** `olaiin` ("load vessel: extended iteration binding"), `okain` ("seal vessel for a processing cycle"), `olain` ("load for iteration binding"). Three vessel-management tokens with iteration atoms on one line — the apparatus is being loaded and sealed for the long putrefaction. `shedy` ("watch the state") and `qokolchedy` ("hold heat at arrangement while checking") maintain observation.

**L17 — Gentle heat established.** `qokeedy` ("gentle fire — balneum level") opens the line — the putrefaction heat is being set. `dar` ("add a new substance") — a material addition. `checkhy` ("check stabilized heat level") — a ckh observation verifying the heat. `otar` ("note the transfer rate"). `olchcthy` — continue while watching the transfer. The heat regime for putrefaction is being established and verified.

**L18 — Heat-level check + scaffold iteration.** `qokedy` ("maintain fire level"), then `chckhy` — a **heat-level check** (ckh). `sain` ("begin a binding iteration cycle") — the scaffold is being set up for the long autonomous process. `shekam` ("passive quality check approaching finality") — the `m` (final) atom marks a terminal observation. The quality of the product is being assessed as a baseline before the long run.

**L19 — Material additions with heat management.** `qokal` ("fire reached target") and `qokedy` ("maintain fire level") anchor the heat. Two `daiin` ("start a new cycle — deep binding") — material additions being locked into the process. `qoky` ("cease heating") appears mid-line, followed by `chedy` ("check the state") — a brief cooling check before resuming. The operator is establishing the cycle that will carry the putrefaction.

**L20 — Transfer and material operations.** `qotar` ("transfer heat/material and note result") opens the line. Two `dar` ("add a new substance") tokens — the highest single-line material density in P3. `shckhy` — a **heat-level check** (ckh). `qotedy` ("heat-driven transfer"). The line reads: transfer material, add substances, check heat, transfer again. Active material management within the putrefaction.

**L21–L22 — Extended observation phase.** L21 has dense observation: `shey` ("watch briefly"), `cheol` ("check arrangement"), scattered te-prefix tokens. L22 opens with observation (`dshey`, `shedy`) then a `dar` material addition followed by `otedaiin` ("transfer-rate: extended iteration binding") — monitoring the output during the long sealed process. Two ckh observations close L22: `shckhchy` (passive heat check with extended monitoring) and `chckhy` (active heat-level check). The putrefaction needs periodic temperature verification across its 45-day duration.

**L23 — Material loading + heat check.** `qokal` ("fire reached target"), two material-binding tokens (`daiin`, `dain`), and `shckhy` — a **heat-level check** (ckh). The operator is adding material and checking that the heat is holding. The putrefaction is an autonomous process, but materials may need periodic replenishment.

**L24 — Material and vessel management.** Two observation tokens (`shey` × 2) frame `dar` and `dain` — material additions under observation. `qoky` ("cease heating") appears — periodic heat interruption during the long process. `okedar` ("vessel: check vessel and respond") — vessel management.

**L25 — Gentle transfer operations.** `qoteedy` ("gentle heat-driven transfer") — the first qoteedy on the folio. During putrefaction, any transfers are done gently. `qokeedy` ("gentle fire — balneum") maintains the bath temperature. `dam` ("material handling finalized") — a material phase closes.

**L26 — Heat adjustment.** `qokchy` ("adjust fire while watching") — the operator tweaks the fire. `olky` ("continue: heat, done"), `otedy` ("check drip rate"). Routine maintenance of the long process.

**L27 — Gentle observation.** Only 6 tokens. `sheedy` ("extended passive observation") and `qokeedy` ("gentle fire — balneum") — sustained gentle heat with passive watching. The process is well-established; intervention is minimal.

**L28 — Heat target + heat check.** `qokeedy` ("gentle fire — balneum"), `qokal` ("fire reached target"), `shckhy` — a **heat-level check** (ckh). Periodic verification that the putrefaction bath is holding temperature.

**L29 — Quality check.** `chekar` ("quality check — is the product right?") — one of 3 chekar tokens on the folio, and one of only 2 in P3. This is a quality inspection during the long putrefaction. `qotar` ("transfer heat/material and note result"), `saiin` ("begin extended binding iteration cycle") — the process continues cycling.

**L30 — Deep sealed cycling.** `okaiin` ("extended sealed processing, multiple cycles"), `qokain` ("sustained cyclic heating"), `qokeey` ("establish gentle heat"), `qotedy` ("heat-driven transfer"). The putrefaction is in its deep autonomous phase: sealed, cycling, transfers occurring within the vessel.

**L31 — Sustained cycling continues.** `qokain` ("sustained cyclic heating") — the iterative frame continues. Vessel management tokens dominate the rest of the line.

**L32 — Transfer-watch + material.** `chcthy` — a **transfer-watch** (cth). `olchcthy` — continue while watching the transfer. `dar` ("add a new substance"). Late in the putrefaction, the operator checks the product's transformation and adds material.

**L33 — Quality assessment.** `chekar`-like observation: `shekedy` ("observe the heat-cool cycle"). `dam` ("material handling finalized") — the last material operation in the paragraph. `ithhy` — an extended-watch token with doubled h (prolonged scrutiny). The quality of the putrefying product is being carefully assessed.

**L34 — Closing.** `qokedy` ("maintain fire level") — the last heat management token on the folio. Three `okedy` ("check vessel during cooling") tokens — vessel verification. `ar` tokens note the yield. The folio closes with vessel checks, confirming the process is winding down.

**Match assessment:** Coherent. P3 dominates the folio (50% of tokens, 20 of 34 lines) just as putrefaction dominates the recipe (45 days vs. 2–4 days for the bath). Fifteen material additions (60% of the folio's total 25 dar) are distributed across the long paragraph. Five ckh (heat-level check) observations spaced across 20 lines encode periodic temperature verification during a 45-day sealed process. The e-depth of 0.50 — slightly lower than P1's 0.58 — reflects less active thermal intervention: putrefaction requires sustained, steady heat rather than the more actively managed balneum of P1. Three quality checks (chekar tokens) verify progress during the long run.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | 0.58 | Active balneum digestion — temperature actively managed |
| P2 | **0.48** | Transfer phase — cooler handling between active stages |
| P3 | 0.50 | Sustained putrefaction — steady gentle heat, less intervention |

The e-depth draws a modest but coherent arc: highest in P1 where the balneum requires active temperature management (the operator must keep the water bath at the right level for 2–4 days), dipping lowest in P2 where the product is being transferred and handled at a cooler state, and settling slightly below P1 in P3 where the putrefaction runs at sustained gentle heat for 45 days. The difference between P1 (0.58) and P3 (0.50) captures the physical distinction: a multi-day bath with frequent temperature checks versus a 45-day autonomous digestion that requires less active intervention once established.

### dar distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 9 | 36% | Combine moon-water + mercury + gold; process additions during digestion |
| P2 | 1 | 4% | Add menstrual |
| P3 | 15 | **60%** | Material management during 45-day putrefaction |

Material additions concentrate in P3 (60% of all dar). This is consistent with a long putrefaction: over 45 days, the operator periodically replenishes or adjusts the mixture. P1's 9 dar (36%) correspond to the initial loading of three weighed reagents plus process-maintenance additions during the multi-day bath. P2's single dar maps directly to "put in 12 parts of menstrual" — the one addition specified for the transition.

### Observation MIDDLE distribution

| Para | ckh | cth | ecth | Total | Recipe activity |
|------|-----|-----|------|-------|-----------------|
| P1 | 6 | 1 | 2 | 9 | Balneum digestion — active heat monitoring + nigredo diagnostic |
| P2 | — | 2 (+1 cthh) | — | 3 | Transfer handling — watching the product move |
| P3 | 5 | 2 | — | 7 | Putrefaction — periodic heat checks + transformation watches |

**P1 has the highest observation density** (9 obs MIDDLEs / 158 tokens = 5.7%). Six heat-level checks (ckh) encode the active temperature management required during the 2–4 day balneum. The two cooled-transfer-watches (ecth) on L8 mark the nigredo — the moment the operator inspects the blackened product.

**P2 concentrates on transfer-watches** (3 cth/cthh, zero ckh). The entire paragraph is about handling and observing the product as it moves between vessels. The extended transfer-watch (`shcthhy` with doubled h) encodes careful inspection of the blackened product before committing to putrefaction.

**P3 distributes observation evenly** across 20 lines: 5 ckh and 2 cth. Over a 45-day process, the operator periodically checks the heat and observes the transformation. The observation density (7 / 182 tokens = 3.8%) is lower than P1's — consistent with a more autonomous process requiring less frequent intervention.

---

## Structural Signatures

### Folio compactness matches recipe brevity

II.12.0 is one of the shortest recipes in the Testamentum (386 characters in Catalan). f84r is correspondingly compact: 3 paragraphs, 34 lines, 361 tokens. For comparison, f75r (matched to III.19.0 aqua vitae, a longer recipe with two counting phases) has 9 paragraphs, 46 lines, 412 tokens. The folio scales with the recipe.

### qokaiin (deep sealed cycling) marks long-duration phases

`qokaiin` appears 3 times on the folio — once in P1 (L8, L9, L12). This token, with its double-i ("iterate, iterate"), encodes deep sustained cycling in a sealed vessel. All three appearances fall in the second half of P1 (L8–L12), where the multi-day bath digestion is underway. None appear in P2 (a brief transfer) or P3 (where `qokain` with single-i handles the longer but less thermally intensive putrefaction). The distinction is precise: the balneum requires deeper thermal cycling than putrefaction.

### Transfer-rate dominance in P2

P2's prefix profile is unique on the folio: `ot` (transfer-rate) ties with `qo` (heat source) at 5 tokens each in a 21-token paragraph. No other paragraph comes close to this transfer-rate concentration. The recipe's transition step — moving the blackened product and adding menstrual — is a physical handling operation, and the folio encodes it as such.

---

## Verdict: COHERENT

f84r produces a coherent paragraph-by-paragraph reading against II.12.0 (gold dissolution with nigredo and putrefaction). The folio's 3 paragraphs map to the recipe's three procedural stages without post-hoc adjustment:

1. **Combine + Digest** (P1) — 9 material additions for three weighed reagents, active balneum with 6 heat-level checks, nigredo diagnostic via paired cooled-transfer-watches on L8
2. **Transfer + Add Menstrual** (P2) — transfer-rate dominated (5 ot tokens), 3 transfer-watches, single material addition for the menstrual

**Material markers (expert review note):** `fchedy` on L15 contains the fch atom pattern (C1939: mercury/mercury-water marker, enriched on all 6/6 confirmed mercury-recipe folios). This is consistent with a recipe using mercury water as the dissolution medium. The cs gold marker (C1940) was not systematically checked in the original cold read; the expert positive control confirmed cs=3 on this folio, consistent with gold being the dissolved subject material.
3. **Putrefaction** (P3) — 50% of folio tokens for the 45-day phase, 15 material additions, 5 heat-level checks distributed across 20 lines, 3 quality checks

The folio's compactness (3 paragraphs, 361 tokens) matches the recipe's brevity (386 characters). The e-depth arc (0.58 → 0.48 → 0.50) tracks the physical transition from actively managed balneum to cooler transfer handling to sustained gentle putrefaction. The observation MIDDLE distribution shifts from heat-monitoring (ckh-heavy P1) through transfer-watching (cth-only P2) to mixed periodic monitoring (P3) — reflecting the changing demands at each stage.

The paired ecth observations on L8 provide the most specific structural signal: two cooled-transfer-watches flanking a material addition mark the exact moment described by the recipe as "you will find it all black like charcoal." The nigredo is not a vague thematic correspondence — it is a locatable diagnostic event encoded in the observation MIDDLE pattern of a specific line.
