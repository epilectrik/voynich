# Cold Read: f76r ↔ II.16.0 Element Separation / Washing Operation (Sevenfold Distillation)

**Match tier:** CONFIRMED
**Verdict:** Coherent

---

## The Recipe (II.16.0 — SISMEL Catalan, complete)

> Fill, quant hauràs divisida la pedra per les .iiii. elements, és-te mester que les purgues per aquest regiment. Mais primerament has a saber la substancia des .iiii. elemens. Per que't diem que la terra e lo foch són resemblats en la substancia pedrenca o de pedra, e per ço han mester preparació del foch calcinant. E los altres dos, ço és lux l'ayre e l'aygua, són de natura aquaticha; per ço t'és ops que sapies la preparació deguda que han mester a la exigencia de lur natura, car l'aygua e l'aere han mester preparació que's fa ab septena distillació en tro són buyts de tota adustió qui vinga del part del menstruall, e estan plens de vera [tinctura] sens gens de cremament. Ffill, l'aygua e l'ayre distillaràs a·ppart en lur rectificació cascú per si; e les [feces] de l'aygua posaràs ab la terra, les quals faràs en cascuna distillació. E aprés la .vi. distillació, posa'n un gota o dues sobre una lamina de pur argent: e si lo negrifica, en res del món no és buyda de tota adustió. D'on met-lo a la setena distillació, en tro lex l'argent sens nulla corrupció. Adonchs hauràs aygua de vida, ab la qual lavaràs la terra, e lo mercuri philosophal confortatiu e lo mijà qui fa lo matrimoni de les tinctures. E así com fas de l'aygua de luna, semblant faràs de l'aygua del sol. E así com has oït de l'aygua, tot así deus entendre de l'ayre. E ço que estarà aprés les distilacions serrà foch que és ple de tinctura, lo qual metràs a part. E l'air que distilla és oli e tinctura, e és aur e ànima e enguent de philosoff, sens lo qual lo magisterii no's pot acaber...

*Cipher note: II.16 is Part II (Liber Practicus). The Part II letter cipher applies: A=God, B=quicksilver, C=salt of stone, D=vitriol azoqueous, E=menstrual, F=fine silver, G=philosophical mercury, H=gold. The recipe refers to "menstruall" (E) and "argent" / "argent fi" (F) in plaintext. No cipher letters appear explicitly in this sub-recipe.*

**Translation:** Son, once you have divided the stone into the 4 elements, you must purge them by this regiment. First know the substance of the 4 elements. Earth and fire resemble stony substance and need preparation by calcining fire. The other two — air and water — are aquatic in nature and need preparation through sevenfold distillation until empty of all burning that comes from the menstrual, and full of true tincture without any scorching. Son, distill water and air separately in their rectification, each by itself; and the feces of the water place with the earth, which you will do at each distillation. After the 6th distillation, put a drop or two on a plate of pure silver: if it blackens it, it is not yet empty of all burning. So put it to the 7th distillation, until it leaves the silver without corruption. Then you will have water of life, with which you will wash the earth, and the philosophical mercury — the comforting agent and the medium that makes the marriage of the tinctures. And as you do with the water of the moon, so you will do with the water of the sun. And as you have heard of the water, so you must understand of the air. And what remains after the distillations will be fire, full of tincture, which you will set aside. And the air that distills is oil and tincture, and is gold and soul and philosopher's ointment, without which the magisterium cannot be completed.

The recipe is an extended purification protocol: separate the stone's 4 elements, then purge water and air through 7 distillation cycles with a silver-plate purity test at cycle 6. Earth and fire receive calcination instead. The product is aqua vitae for washing the earth, plus philosophical mercury. The same procedure applies to both lunar and solar waters, and to air as well as water — the recipe explicitly instructs repeating the protocol across element pairs.

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
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate x2, bind | Sustained deep cyclic heating — multiple iterations | PT-013 (15/15) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target — heat stage done | PT-013 (10/10) |
| qokar | qo | k.a.r | fire: heat, yield, respond | Apply heat and note the response | B Dict D1 |
| qokeey | qo | k.e.e.y | fire: heat, stabilize x2, done | Establish gentle heat state | B Dict D1 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qotedy | qo | t.e.d.y | fire: transfer, stabilize, do, done | Execute a heat-driven transfer | B Dict D1 |
| qotain | qo | t.a.i.n | fire: transfer, yield, iterate, bind | Heat-transfer: sustained iterative cycle | B Dict D2 |
| qolchedy | qo | l.c.h.e.d.y | fire: hold, adjust, watch, stabilize, do, done | Check equipment state at the fire | Compositional |
| qolchey | qo | l.c.h.e.y | fire: hold, adjust, watch, stabilize, done | Apparatus check at the fire | Compositional |
| qokchdy | qo | k.c.h.d.y | fire: heat, adjust, watch, do, done | Adjust fire while watching | B Dict D2 |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dain | da | i.n | material: iterate, bind | Bind material into the cycle | B Dict D1 |
| dal | da | l | material: hold/state | Carefully collect or place material | PT-013 (9/10) |
| dalaiin | da | l.a.i.i.n | material: hold, yield, iterate x2, bind | Measured material addition into extended cycle | Compositional |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state — verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| checkhy | ch | e.c.k.h.y | test: stabilize, adjust, heat, watch, done | Gentle heat-level check | B Dict D2 |
| chcthy | ch | c.t.h.y | test: adjust, transfer, watch, done | Watch the transfer (active) | B Dict D2 |
| checthy | ch | e.c.t.h.y | test: stabilize, adjust, transfer, watch, done | Watch a cooled transfer (active) | B Dict D2 |
| chekain | ch | e.k.a.i.n | test: stabilize, heat, yield, iterate, bind | Quality check into iterative cycle | Compositional |
| chekear | ch | e.k.e.a.r | test: stabilize, heat, stabilize, yield, respond | Quality check — is the product right? | B Dict D2 |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly — quick passive check | B Dict D1 |
| sheedy | sh | e.e.d.y | watch: stabilize x2, do, done | Extended passive observation | B Dict D2 |
| shckhy | sh | c.k.h.y | watch: adjust, heat, watch, done | Passively observe the heat level | B Dict D2 |
| shecthy | sh | e.c.t.h.y | watch: stabilize, adjust, transfer, watch, done | Watch a cooled transfer (passive) | Compositional |
| shcthy | sh | c.t.h.y | watch: adjust, transfer, watch, done | Watch the transfer (passive) | Compositional |
| okaiin | ok | a.i.i.n | vessel: yield, iterate x2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal the vessel for a processing cycle | B Dict D1 |
| okedy | ok | e.d.y | vessel: stabilize, do, done | Check vessel during cooling | B Dict D1 |
| okeedy | ok | e.e.d.y | vessel: stabilize x2, do, done | Maintain vessel at gentle balneum temperature | B Dict D1 |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| otedy | ot | e.d.y | drip-rate: stabilize, do, done | Check drip/flow rate during cooling | B Dict D1 |
| otain | ot | a.i.n | drip-rate: yield, iterate, bind | Monitor transfer rate through iterative cycle | B Dict D2 |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| saiin | sa | i.i.n | scaffold: iterate x2, bind | Begin extended binding iteration cycle | B Dict D1 |
| lchedy | lch | e.d.y | apparatus: stabilize, do, done | Check apparatus (seals, receiver, furnace) | PT-013 (8/10) |
| lkeedy | lk | e.e.d.y | furnace: stabilize x2, do, done | Check furnace at gentle temperature | B Dict D2 |
| olain | ol | a.i.n | continue: yield, iterate, bind | Continue iterating | Compositional |
| dy | -- | d.y | mark, done | Cycle close — action complete | B Dict D1 |
| sol | so | l | sequence: hold | Mark current state in sequence | B Dict D1 |

**Observation MIDDLEs** — specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

---

## The Folio

**f76r:** 546 tokens, 47 lines, 4 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|---------------------|
| P1 | 1-29 | 357 | 19 | 0.60 | 10 ckh, 4 cth, 2 ecth, 1 cfh | Sevenfold distillation of water and air — the main purification protocol |
| P2 | 30-34 | 58 | 4 | 0.50 | 2 ckh, 1 ecth | Repeat for water of the sun — parallel rectification |
| P3 | 35-40 | 65 | 1 | 0.46 | 4 ckh | Vessel cycling and sealed processing — air rectification |
| P4 | 41-47 | 66 | 3 | 0.58 | 1 ecth | Collection and final separation — fire/tincture set aside |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation). Lower values = more sustained uninterrupted heat (calcination, autonomous cycling). A value near zero means no thermal operation at all (vessel handling).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1-29, 357 tokens) — Sevenfold Distillation

**Recipe says:** "Water and air need preparation through sevenfold distillation until empty of all burning from the menstrual. Distill water and air separately in their rectification, each by itself; and the feces of the water place with the earth. After the 6th distillation, put a drop or two on a plate of pure silver: if it blackens it, it is not yet empty of all burning. So put it to the 7th distillation, until it leaves the silver without corruption."

This is the core of II.16.0: a sustained, multi-cycle distillation program with a quality test near the end. The recipe describes 7 distillation passes on the aquatic elements (water and air), collecting feces at each pass, with a silver-plate purity check after the 6th pass and a final 7th pass to achieve complete purification.

**What the tokens say:**

P1 dominates the folio — 357 of 546 tokens (65%), spanning 29 lines. This is by far the largest paragraph on f76r, and the recipe explains why: the sevenfold distillation of two elements (water and air, each rectified separately) is the central operation, demanding the most procedural space.

**The monitoring density is exceptional.** P1 contains 17 observation MIDDLEs — 10 heat-level checks (ckh), 4 transfer-watches (cth), 2 cooled-transfer-watches (ecth), and 1 flag-heat check (cfh). No other paragraph on this folio approaches this density. The recipe describes repeated distillation requiring careful purging of "burning from the menstrual" — the operator must constantly monitor whether the product is still contaminated. This monitoring-intensive distillation is exactly what 17 observation MIDDLEs encode.

**Lines 1-5: Setup and first distillation pass.**

L1 opens with `potchokar` — a complex gallows-initial token combining transfer, adjustment, and heat response. The line contains monitoring tokens (`chcfhdy`, `chcphy`, `chcphdy`) establishing the initial quality baseline. One `sain` ("begin a binding iteration cycle") signals the start of the iterative process.

L2 introduces the first material addition: `dain` ("bind material into the cycle"), followed by vessel sealing (`okain` — "seal the vessel for a processing cycle"). Then gentle heat establishment: `qokeey` ("establish gentle heat state"). Watch tokens (`shedy`) track the distillate. The line reads: load material, seal the vessel, bring up gentle heat, and watch.

L3 intensifies the thermal program: `qokeey`, `qokey`, `qokeed` — a sequence of gentle-heat tokens. Then a transfer operation: `qotedy` ("execute a heat-driven transfer") followed by `otedy` ("check drip/flow rate during cooling"). The distillate is coming through.

L4 introduces standard fire management: two `qokedy` ("maintain current fire level") tokens bracketing `qokchy` ("adjust fire while watching"). Then `qokal` ("fire reached target — heat stage done"). One distillation pass is completing.

L5 has apparatus checking: `solchedy` ("check apparatus in sequence") and `qopchedy` (pause to check at the fire). A `dar` ("add a new substance") appears at the end — the feces being separated and placed with the earth, as the recipe instructs for each distillation.

**Lines 6-9: Cycling through distillation passes.**

L6: `qoaiin` ("sustained contained heat") opens the line — deep iterative heating. Two `dar` tokens on this stretch signal material handling mid-cycle. `chekain` ("quality check into iterative cycle") — the operator checks quality and feeds the result back into the next pass. The cycle-within-cycle structure is evident.

L7 has a heat-level check (`shckhy`) and a material addition: `dar` followed by `daly` ("material: hold, done"). The feces are again being separated and set aside. Two `ain` ("yield into cycle") tokens maintain the iterative frame.

L8 opens with `qotedshedy` — a compound token combining heat-driven transfer with observation. Then `chckhy` ("check the heat level") — the second heat-level check. `raiiin` is notable: a triple-iterate token, encoding deep cycling within the iterative frame.

L9: Three `shedy` tokens interspersed with heat management. `dain` and `saiin` signal another material binding and a new extended iteration scaffold. The distillation cycling continues.

**Lines 10-15: Mid-protocol monitoring intensifies.**

L10 is the densest monitoring line on the folio. It contains:
- `checthy` — a **cooled-transfer-watch** (ecth): observing a cooled intermediate product
- `chckhey` — a heat-level check with gentle stabilization
- `sheckhey` — a passive heat observation with the same pattern
- `okaiin` — extended sealed processing

Three different observation types on one line. The recipe requires the operator to watch for signs of remaining "burning" — here the monitoring is at maximum intensity. This maps to the critical assessment phase between distillation passes.

L12 introduces a **quality check** sequence: `checkhy` ("gentle heat-level check"), then `chekear` ("quality check — is the product right?"). This is the first response-type quality assessment (two earlier `chekain` tokens on L6 and L8 feed back into iteration rather than producing a verdict) — the operator is testing whether the distillate has been sufficiently purged. Two `qotain` tokens ("heat-transfer: sustained iterative cycle") maintain the cycling frame.

L15 packs two consecutive heat-level checks: `chckhy` and `shckhy` — one active, one passive. Both are asking: is the fire at the right level? The doubled check (active verification followed by passive confirmation) suggests heightened attention at this point in the protocol.

**Lines 16-22: Sustained cycling with material operations.**

L16-L18 show a shift toward material handling. `dar` on L16, `dain` on L18, and `dalshedy` on L18 ("add material while watching the distillate"). The recipe says to "place the feces of the water with the earth at each distillation" — these material operations track repeated feces collection across passes.

L18 also contains a **cooled-transfer-watch** (`shecthy`): the operator is handling a cooled intermediate product. This is consistent with collecting distilled fractions between passes and setting them aside.

L19-L20 are monitoring-dense: five `chey` ("quick active verification") tokens on L19 plus one `ky`. The operator is performing rapid quality checks between heat applications. L20-L21 have `qokaiin` ("sustained deep cyclic heating") — the deepest iteration tokens, encoding multi-pass cycling. The iterative frame is at maximum depth.

L21: Two `dal` ("carefully collect or place material") tokens — measured material handling. One `qokaiin` — sustained deep cycling continues. The recipe's "at each distillation, place the feces with the earth" maps to these paired collect-and-cycle operations.

L22 shows a characteristic heat-watch pattern: `qokar`-`shedy`-`shedy`-`qokar`-`shedy` — apply heat, watch, watch, apply heat, watch. This alternating rhythm is supervised distillation. Then `dar` ("add a new substance") and `shcthy` — a **transfer-watch**: watch what is being transferred. The operator applies heat, watches the result, adds material, and monitors the transfer.

**Lines 23-27: Late-protocol transitions and quality assessment.**

L23: `darchey` ("add material while checking") and two transfer-watches (`shcthy` on L23 and L26). `dalaiin` ("measured material addition into extended cycle") — the operator is loading material for continued cycling.

L25-L26: Heavy observation. L25 has `chckhy` ("heat-level check") and `dar` — checking and adding. L26 is dominated by passive observation: four `shedy` / `shey` tokens in sequence, then a `shcthy` (transfer-watch). The operator is watching intensively — consistent with the approach to the 6th-distillation quality test described in the recipe.

L27: Two transfer-watches (`chcthy` on L27 itself) and a heat-level check (`chckhy`). Then `otar` ("note the drip/transfer rate") — monitoring the output. The protocol is reaching a critical assessment point.

**Lines 28-29: Winding down the main distillation.**

L28: `qokal` ("fire reached target") opens the line. Then mostly monitoring and arrangement tokens: `chol`, `chdy`, vessel loading. The heat phase is completing.

L29 (final line of P1): `qokal` again — heat stage done. `lchey` ("check equipment state") and `chey` ("quick verification"). The paragraph closes with apparatus checking and a final heat completion.

**Three quality checks (`chekear` / `chekain` type)** appear across P1. The recipe describes testing at the 6th distillation — these quality checks distributed through the long protocol mark the assessment points where the operator evaluates whether purification is sufficient.

**Match assessment:** Strongly coherent. P1's massive 29-line span encodes the full sevenfold distillation protocol. The 17 observation MIDDLEs (the highest monitoring density on this folio) match a recipe that demands constant vigilance for residual "burning." Material additions (19 dar) distributed across the paragraph track the repeated feces-collection step. The e-depth of 0.60 indicates active distillation with significant cooling intervention — standard for a multi-pass rectification. The three quality checks map to the recipe's purity-testing requirement.

---

### P2 (Lines 30-34, 58 tokens) — Parallel Rectification (Water of the Sun)

**Recipe says:** "And as you do with the water of the moon, so you will do with the water of the sun."

The recipe explicitly instructs repeating the full rectification protocol for a second element preparation. P1 encoded the first run (water of the moon); P2 encodes the parallel procedure (water of the sun) in compressed form.

**What the tokens say:**

P2 has 58 tokens — a dramatic compression from P1's 357. The recipe justifies this: "semblant faras" ("similarly you will do"). The scribe does not re-encode the full sevenfold distillation; instead, P2 captures the compressed operational signature of a repeated protocol.

L30 opens with a gallows-initial token and `qokeedy` ("gentle fire — balneum level") — restarting gentle heat for a new batch. `oty` ("transfer done") closes the initial setup.

L31 has a **heat-level check** (`shckhy`) — confirming the fire is at the right level for the repeated protocol. Then `dain` ("bind material into the cycle") — loading the new batch. `qokedar` (heat with yield response) and apparatus checking (`olchdy`, `lchedy`). The line reads: check heat, load material, begin distillation, check equipment.

L32: `sain` ("begin a binding iteration cycle") opens the iterative frame. Then `shckhy` (a second heat-level check), `otedy` ("check drip rate"), and `qokal` ("fire reached target"). The cycling is faster here — two heat-level checks in three lines (vs. P1's ten across 29 lines). The protocol is familiar now, so checks come at a faster cadence.

L33 introduces three material additions: `dain`, `daiin` ("start a new cycle"), and a **cooled-transfer-watch** (`shecthy`). Then `otalam` with a terminal `m` (final) atom — the transfer monitoring is reaching completion. Feces are being collected and handled; the protocol is the same.

L34: `qokar` ("apply heat and note the response") — the familiar heat-watch rhythm. The paragraph closes with `chdy` ("check: done").

**Match assessment:** Coherent. P2 compresses the sevenfold protocol into a 58-token paragraph. The same operational elements appear — heat-level checks (2 ckh), material additions (4 dar), a cooled-transfer-watch (1 ecth), and iterative cycling — but at a fraction of the length. The e-depth drops to 0.50, slightly lower than P1's 0.60, consistent with a parallel run where the operator is now experienced and the process requires less active cooling intervention. The compression ratio (6.2:1 vs P1) mirrors the recipe's "do likewise" instruction.

---

### P3 (Lines 35-40, 65 tokens) — Air Rectification (Sealed Processing)

**Recipe says:** "And as you have heard of the water, so you must understand of the air."

The recipe extends the protocol to the air element. Air rectification requires the same sevenfold distillation but produces a different product: "the air that distills is oil and tincture, and is gold and soul and philosopher's ointment."

**What the tokens say:**

P3 has a distinctive prefix distribution that separates it from P1 and P2. **Vessel-management tokens dominate:** `ok` (11 tokens) is the most common prefix, overtaking both `qo` (6) and `ch` (5). In P1, `qo` (75) and `ch` (73) led. The shift from fire-management to vessel-management encodes a process where the apparatus itself — seals, receivers, connections — demands more attention than the heat source.

This makes sense for air rectification. Air is volatile; the product is "oil and tincture." Collecting volatile fractions requires airtight apparatus, careful receiver management, and sealed processing — exactly the vessel-centric operation that P3's prefix distribution encodes.

L35: `shckhy` ("passively observe the heat level") — the first observation is a heat check. Then heavy vessel operations: `lkaiin` ("furnace: extended iteration cycle"), `olshedy` ("continue: watch the distillate"), `otain` ("monitor transfer rate through iterative cycle"), `okar` ("vessel: yield and respond"). Five vessel/transfer tokens on one line.

L36: `qokaiin` ("sustained deep cyclic heating") — the deepest iteration level appears. `okeedy` ("maintain vessel at gentle balneum temperature") — vessel management at balneum level. `chckhy` — a heat-level check. The combination of deep cycling with gentle vessel temperature is consistent with careful distillation of volatile fractions.

L37-L38 show the vessel-cycling pattern most clearly. L37 has three `okedy` ("check vessel during cooling") tokens and two `okar` ("vessel: yield and respond"), plus `otar` ("note the drip rate"). The operator is repeatedly checking the vessel, checking the output, checking the vessel again. One `dain` on L38 — the single material addition in P3 — corresponds to the minimal material handling needed for air rectification (the volatile product largely collects itself).

L39: `saiin` ("extended binding iteration cycle"), `shckhy` (heat-level check), `qoky` ("cease heating"), `qokal` ("fire reached target"). The iteration is winding down. The heat-level check followed by both "cease heating" and "fire reached target" marks a controlled shutdown.

L40: Three `saiin`/`sain` scaffold tokens — iterative cycling infrastructure. Three `oky` ("vessel: done") tokens — vessel operations closing out. The paragraph ends with apparatus response tokens (`lkar`, `chedy`, `lkar`). The cycling is complete; the vessels are closed.

**Four heat-level checks** (ckh) across 6 lines — the same monitoring density as P2 scaled to comparable length. Zero transfer-watches and zero cooled-transfer-watches: the operator is monitoring heat, not handling cooled intermediates. This is consistent with air rectification, where the product is captured as vapor/oil rather than handled as a cooled liquid.

**Match assessment:** Coherent. The prefix shift from fire-management (P1) to vessel-management (P3) encodes the physical difference between liquid and air rectification. The e-depth drops to 0.46 — the lowest on the folio — consistent with more sustained heat for volatile distillation. Minimal material additions (1 dar) match a process where the volatile product self-collects. The four heat-level checks maintain quality monitoring without the liquid-handling observation types (cth, ecth) that characterized P1.

---

### P4 (Lines 41-47, 66 tokens) — Collection and Final Separation

**Recipe says:** "And what remains after the distillations will be fire, full of tincture, which you will set aside. And the air that distills is oil and tincture, and is gold and soul and philosopher's ointment, without which the magisterium cannot be completed."

The final step: collect all products, set aside the fire (tincture-rich residue), and handle the distilled oil. The recipe describes product collection and classification, not a new distillation.

**What the tokens say:**

P4's e-depth rises to 0.58 — higher than P2 and P3 but slightly below P1. This is not a new distillation but a careful collection and handling step. The cooling atoms reflect the thermal management needed to handle hot products, not active distillation.

L41 opens with `fchedy` — a rare `fch` prefix (appears only here on this folio). The `f` prefix is uncommon in Currier B. Then `qokaiin` ("sustained deep cyclic heating") and `otal` ("note the output rate"). The line reads: special check, sustained heating, note the output. This is the final processing before collection.

L42: `keedy` ("steady-state thermal check"), `dar` ("add a new substance"), `qopchedy` ("pause to check at the fire"). A material addition during the collection phase — the fire-element residue being "set aside" (metras a part) as the recipe instructs.

L43 is the thermal center of P4. Three heat-management tokens in sequence: `qokedy`, `qokeedy`, `qokedy` — standard fire, gentle fire, standard fire. This bracketing pattern (standard-gentle-standard) encodes a careful collection step: bring heat up to release the product, go gentle to stabilize, bring heat back up to complete. Then `okar` ("vessel: yield and respond"), `shedy` ("watch the distillate"), `otain` ("monitor transfer rate through iteration"). The products are being extracted.

L44: `qoteedy` ("gentle heat-driven transfer") — a transfer at balneum temperature. This is the philosopher's ointment being carefully collected. The `m`-terminal atom in nearby tokens (absent from this paragraph but present in the compound tokens) signals approaching finality.

L45: `dal` ("carefully collect or place material") — material handling. `qolaiin` ("sustained iteration at the heat source"). Two `olchedy` ("check apparatus: adjust, watch") — checking the apparatus state during the final collection.

L46: `sain` ("begin a binding iteration cycle") followed by `sheey` ("extended passive observation"). A **cooled-transfer-watch** appears: `checthey` (ecth variant) — the single ecth observation in P4. The operator is handling a cooled product: the collected oil/tincture being observed as it cools. `ldaiin` ("material: extended iteration cycle") — the final material addition. `okedalor` — a complex vessel token incorporating yield, arrangement, and response. The products are being sorted and placed.

L47 (final line of the folio): `qokaiin` ("sustained deep cyclic heating") — the iteration continues to the very end. Then `shedy` ("watch the distillate"), `qokeey` ("establish gentle heat state"). The folio closes on gentle heat and observation — a controlled, quiet ending. The final products have been collected; the process is complete.

**Match assessment:** Coherent. P4 encodes product collection and separation rather than a new distillation. The e-depth of 0.58 reflects thermal management during collection, not active rectification. Three material additions match the recipe's instruction to "set aside" the fire and collect the oil separately. The single cooled-transfer-watch (ecth) on L46 marks the handling of a finished, cooled product. The folio ends quietly — gentle heat and observation — consistent with a process that has reached its conclusion.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | 0.60 | Active multi-pass distillation — high cooling intervention |
| P2 | 0.50 | Compressed parallel rectification — moderate cooling |
| P3 | 0.46 | Vessel-centric sealed processing — sustained heat for volatiles |
| P4 | 0.58 | Product collection — careful thermal handling |

The e-depth arc traces a physical trajectory: intensive distillation with high cooling (P1), a compressed repeat at moderate cooling (P2), sustained heat for volatile air rectification (P3), then a rise for careful product collection (P4). The lowest value (0.46) falls on P3 — air rectification — where volatile fractions require sustained, less-interrupted heat. The rise to 0.58 in P4 reflects the cooling and thermal management needed to handle hot products during final collection.

### dar distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 19 | 70% | Sevenfold distillation — feces collection at each pass |
| P2 | 4 | 15% | Parallel rectification — compressed material handling |
| P3 | 1 | 4% | Air rectification — volatile product self-collects |
| P4 | 3 | 11% | Product collection — setting aside fire and oil |

Material additions are front-loaded: 70% occur in P1. The recipe explains why — "the feces of the water place with the earth, which you will do at each distillation." Seven distillation passes, each producing feces to be collected and set aside, require extensive material handling. P2 compresses the same protocol into 4 additions. P3 (air rectification) has only 1 — volatile products collect themselves without manual intervention. P4's 3 additions correspond to the final product-sorting step.

### Observation MIDDLE distribution

| Para | ckh | cth | ecth | Total | Recipe activity |
|------|-----|-----|------|-------|-----------------|
| P1 | 10 | 4 | 2 | 17* | Sevenfold distillation — maximum monitoring |
| P2 | 2 | — | 1 | 3 | Compressed parallel rectification |
| P3 | 4 | — | — | 4 | Air rectification — heat checks only |
| P4 | — | — | 1 | 1 | Product collection — single cooled-transfer-watch |

*P1 also has 1 cfh (flag-heat-check), bringing its total observation MIDDLEs to 17.

Observation MIDDLEs concentrate overwhelmingly in P1 (17 of 25 total, 68%). The recipe's sevenfold distillation demands constant vigilance — the operator must detect residual "burning from the menstrual" at each pass. P1's monitoring density encodes this requirement.

P3 has 4 heat-level checks (ckh) but zero transfer-watches — consistent with air rectification, where the operator monitors the heat but does not handle liquid intermediates. P4 has just one observation (an ecth — cooled-transfer-watch), marking the moment when a finished product is handled for the final time.

The progressive decline from 17 (P1) to 3 (P2) to 4 (P3) to 1 (P4) tracks the recipe's movement from intensive purification toward product collection and completion.

### Structural signature: 4-paragraph asymmetric layout

f76r's most distinctive structural feature is its extreme asymmetry: P1 contains 65% of the folio's tokens. This is unusual — most folios distribute tokens more evenly across paragraphs. The recipe explains the asymmetry. II.16.0 describes one primary protocol (the sevenfold distillation) and then says to repeat it for other elements ("as you do with water of the moon, so with water of the sun"; "as you have heard of the water, so understand of the air"). The scribe encodes the full procedure once in P1, then compresses the repetitions into shorter paragraphs. The layout is not 7 equal sections for 7 distillation passes, nor 4 equal sections for 4 elements — it is one long section for the master protocol plus three compressed sections for the parallel applications. This matches II.16.0's rhetorical structure precisely.

---

## Verdict: COHERENT

f76r produces a coherent paragraph-by-paragraph reading against II.16.0 (element separation, sevenfold distillation). The folio's 4 paragraphs map to the recipe's procedural structure without post-hoc adjustment:

1. **Sevenfold distillation** (P1) — 357 tokens (65% of folio), 17 observation MIDDLEs, 19 material additions. Encodes the full multi-pass rectification protocol with quality checks, feces collection at each pass, and the highest monitoring density on the folio.
2. **Parallel rectification** (P2) — 58 tokens, compressed 6.2:1 from P1. Same operational elements (heat-level checks, material additions, cooled-transfer-watch) at a fraction of the length, matching "as you do with water of the moon, so with water of the sun."
3. **Air rectification** (P3) — 65 tokens, vessel-management dominant. The prefix shift from fire-centric (P1) to vessel-centric (P3) encodes the physical difference between liquid and volatile distillation. Lowest e-depth (0.46) = most sustained heat. Minimal material additions (1 dar) = volatile product self-collects. Heat-level checks but no transfer-watches = monitoring heat, not handling liquids.
4. **Product collection** (P4) — 66 tokens. Careful thermal management, 3 material additions for sorting products, single cooled-transfer-watch for handling the finished oil/tincture. The folio ends on gentle heat and observation.

The folio's extreme paragraph asymmetry (65% in P1) directly mirrors the recipe's rhetorical structure: full description first, compressed repetitions after. The e-depth arc (0.60 → 0.50 → 0.46 → 0.58) tracks the physical chemistry — from active distillation through sustained volatile processing to careful product collection. The dar distribution (70% in P1) matches the recipe's feces-at-each-pass instruction. The observation MIDDLE distribution (68% in P1) encodes the recipe's demand for constant vigilance during purification. These structural patterns are quantitative properties of the folio that align with the recipe independently of any individual token gloss.
