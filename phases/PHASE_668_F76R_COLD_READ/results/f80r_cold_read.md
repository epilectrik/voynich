# Cold Read: f80r — Animal Ash Chain (Calcination, Multi-Chapter)

**Match tier:** Supported
**Verdict:** Coherent (token-analysis only)

---

## Recipe Status: SISMEL Match Unavailable

This folio was originally matched to 1566 Cologne Chapters 21-25 (Liber Mercuriorum), described as "Animal ash chain (multi-chapter)." However, the 1566-to-SISMEL chapter remap failed for f80r: all SISMEL similarity scores returned 0.0. The cold_read.txt file contains SISMEL III.21.0 text ("De les vexells" -- about vessels), but this is the wrong recipe. SISMEL III.21.0 corresponds to f82v (vessel specification), not f80r. The 1566 Chapters 21-25 about animal-derived calcination materials do not map to SISMEL III.21 due to the chapter-numbering offset between the two editions.

Since the correct recipe text is not available in the SISMEL corpus, this cold read is a **token-analysis only** reading. The original 1566 match description -- "Animal ash chain" -- suggests chapters about preparing animal-derived materials (bones, blood, tissue) through calcination: a multi-step process spanning several related chapters, each treating a different starting material but sharing a common procedure of burning, collecting ash, and processing the calcined residue.

This cold read lets the token patterns speak for themselves. Where the patterns are consistent with calcination processes, this is noted. Where they suggest specific operational regimes independently of any assumed recipe, the evidence is presented directly.

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
| qokain | qo | k.a.i.n | fire: heat, yield, iterate, bind | Sustained cyclic heating | PT-013 (10/10) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target -- heat stage done | PT-013 (10/10) |
| qokar | qo | k.a.r | fire: heat, yield, respond | Apply heat and note the response | B Dict D1 |
| qokeedy | qo | k.e.e.d.y | fire: heat, stabilize x2, do, done | Gentle fire -- balneum / water-bath level | PT-013 (10/10) |
| qokedy | qo | k.e.d.y | fire: heat, stabilize, do, done | Maintain current fire level | PT-013 (10/10) |
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate x2, bind | Sustained deep cyclic heating -- multiple iterations | B Dict D1 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qokeey | qo | k.e.e.y | fire: heat, stabilize x2, done | Establish gentle heat state | B Dict D1 |
| qokam | qo | k.a.m | fire: heat, yield, final | Heat stage finalized | Compositional |
| qotain | qo | t.a.i.n | fire: transfer, yield, iterate, bind | Sustained iterative transfer at the fire | B Dict D2 |
| qotar | qo | t.a.r | fire: transfer, yield, respond | Transfer heat/material and note result | B Dict D1 |
| qotal | qo | t.a.l | fire: transfer, yield, hold | Transfer operation reached target | B Dict D2 |
| qotedy | qo | t.e.d.y | fire: transfer, stabilize, do, done | Execute a heat-driven transfer | B Dict D1 |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dain | da | i.n | material: iterate, bind | Bind material into the cycle | B Dict D1 |
| daiin | da | i.i.n | material: iterate x2, bind | Start a new cycle -- deeper iteration | B Dict D0 |
| dal | da | l | material: hold/state | Carefully collect or place material | PT-013 (9/10) |
| daly | da | l.y | material: hold, done | Careful placement, done | Compositional |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state -- verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| cheey | ch | e.e.y | test: stabilize x2, done | Gentle active verification | B Dict D2 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chcthy | ch | c.t.h.y | test: adjust, transfer, watch, done | Watch the transfer (active) | B Dict D2 |
| checthy | ch | e.c.t.h.y | test: stabilize, adjust, transfer, watch, done | Watch a cooled transfer (active) | Obs. MIDDLE |
| checkhy | ch | e.c.k.h.y | test: stabilize, adjust, heat, watch, done | Active stabilized heat-level check | B Dict D2 |
| chekar | ch | e.k.a.r | test: stabilize, heat, yield, respond | Quality check -- is the product right? | B Dict D2 |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly -- quick passive check | B Dict D1 |
| sheky | sh | e.k.y | watch: stabilize, heat, done | Observe the heat state passively | Compositional |
| shecthy | sh | e.c.t.h.y | watch: stabilize, adjust, transfer, watch, done | Watch a cooled transfer (passive) | Obs. MIDDLE |
| shcthy | sh | c.t.h.y | watch: adjust, transfer, watch, done | Watch what is being transferred (passive) | Obs. MIDDLE |
| shckhy | sh | c.k.h.y | watch: adjust, heat, watch, done | Passively observe the heat level | B Dict D2 |
| sheckhy | sh | e.c.k.h.y | watch: stabilize, adjust, heat, watch, done | Passively observe a stabilized heat level | Compositional |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal the vessel for a processing cycle | B Dict D1 |
| okaiin | ok | a.i.i.n | vessel: yield, iterate x2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okal | ok | a.l | vessel: yield, hold | Vessel reached target state | B Dict D2 |
| okedy | ok | e.d.y | vessel: stabilize, do, done | Check vessel during cooling | B Dict D1 |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| otedy | ot | e.d.y | drip-rate: stabilize, do, done | Check drip/flow rate during cooling | B Dict D1 |
| otal | ot | a.l | drip-rate: yield, hold | Note the output rate | PT-013 (8/10) |
| otain | ot | a.i.n | drip-rate: yield, iterate, bind | Iterative transfer monitoring | B Dict D2 |
| otaiin | ot | a.i.i.n | drip-rate: yield, iterate x2, bind | Extended transfer monitoring | B Dict D2 |
| olkain | ol | k.a.i.n | continue: heat, yield, iterate, bind | Continue sustained cyclic heating | Compositional |
| olkaiin | ol | k.a.i.i.n | continue: heat, yield, iterate x2, bind | Continue extended cyclic heating | Compositional |
| olky | ol | k.y | continue: heat, done | Continue heating, done | Compositional |
| olkeey | ol | k.e.e.y | continue: heat, stabilize x2, done | Continue at gentle heat | B Dict D2 |
| sal | sa | l | scaffold: hold | Mark scaffold state | Compositional |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| saiin | sa | i.i.n | scaffold: iterate x2, bind | Begin extended binding iteration cycle | B Dict D1 |
| lchedy | lch | e.d.y | apparatus-check: stabilize, do, done | Check apparatus (seals, receiver, furnace) | PT-013 (8/10) |
| lchey | lch | e.y | apparatus-check: stabilize, done | Quick apparatus check | B Dict D2 |
| sol | so | l | sequence: hold | Mark current state in sequence | B Dict D1 |
| dy | -- | d.y | mark, done | Cycle close -- action complete | B Dict D1 |
| am | -- | a.m | yield, final | Phase done -- yield result and close | B Dict D0 |
| ol | -- | o.l | arrange, hold | Hold steady | B Dict D0 |
| ram | -- | r.a.m | respond, yield, final | Stage done -- note result | PT-013 (4/4) |
| keedy | ke | e.d.y | steady-heat: stabilize, do, done | Steady-state thermal check | B Dict D2 |
| lol | -- | l.o.l | state, arrange, state | Structural hold | B Dict D2 |

**Observation MIDDLEs** -- specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

---

## The Folio

**f80r:** 441 tokens, 43 lines, 7 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Token profile |
|------|-------|--------|-----|---------|-------------|---------------|
| P1 | 1-17 | 204 | 7 | 0.40 | 4 ckh, 5 cth, 6 ecth | Main processing -- heavy fire + transfers + cooled-ash observation |
| P2 | 18-29 | 117 | 3 | 0.56 | 1 cth, 2 ecth | Continued processing at gentler heat |
| P3 | 30 | 7 | 1 | 0.43 | 1 cth | Micro-transition with transfer-watch |
| P4 | 31-36 | 45 | 0 | 0.47 | 1 ckh, 3 ecth | Cooled-ash processing -- no new material |
| P5 | 37-38 | 19 | 0 | 0.58 | -- | Brief: vessel cycling at gentle heat |
| P6 | 39-40 | 20 | 0 | 0.40 | -- | Brief: vessel iteration, low heat |
| P7 | 41-43 | 29 | 2 | 0.34 | -- | Final: material binding + closure at strong heat |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation, gentle handling). Lower values = more sustained uninterrupted heat (calcination, strong fire). A value near zero means no thermal operation at all (vessel handling).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1-17, 204 tokens) -- Main Calcination Operation

**What the tokens say:**

P1 dominates the folio: 204 of 441 tokens (46%), spanning 17 lines. This is the largest opening paragraph across all 15 cold-read folios. Whatever f80r encodes, nearly half of it happens in the first operation.

The e-depth of 0.40 is low -- this is sustained fire work with relatively little cooling intervention. On the 15-folio scale, only f107r P18 (0.09, final coagulation), f107r P8/P10 (0.20, strong fire), and f75r P7 (0.18, flash transfer) are lower for their respective paragraphs. A low e-depth in a paragraph this long indicates a prolonged high-heat operation, not a brief intense burst.

**Observation MIDDLEs (15 total, densest on any paragraph in the cold-read corpus):**

P1 has 4 heat-level checks (ckh), 5 transfer-watches (cth), and 6 cooled-transfer-watches (ecth). The 6 ecth tokens make this paragraph alone the ecth champion of the entire 15-folio cold-read set. The ecth MIDDLE encodes observing a cooled intermediate product -- watching ash or residue as it cools, checking cooled transferred material. In calcination, the operator repeatedly burns material, lets it cool, examines the ash, and decides whether to continue burning.

**Line-by-line:**

L1 opens with vessel and heat setup: `qokeedy` ("gentle fire -- balneum level") alongside vessel loading (`oltoiin` -- "transfer into vessel for extended iteration") and a material addition (`darshey`). The first substance enters the vessel under gentle heat.

L2 alternates sustained cyclic heating (`qokain` x2) with sustained iterative transfer (`qotain` x2) and includes the first heat-level check (`chckhy`). The pattern is: heat, transfer, check heat, heat again, transfer again. This rapid heat-transfer alternation is distinctive -- the operator is simultaneously managing fire and moving material.

L3 is heat-dense: `qokal` x2 ("fire reached target"), `qokain` x2 ("sustained cyclic heating"), `qokar` ("apply heat and note response"), and `qokam` ("heat stage finalized"). Six heat-source tokens on one line with two reaching-target and one finalization. A sustained calcination sub-step reaches completion.

L4 introduces the first transfer-watch (`chcthy`) and a heat-level check (`chckhy`). The line also includes `qotchy` ("transfer with adjustment while watching") and `qotar` ("transfer and note result"). Transfer operations are being actively monitored -- material is being moved under observation.

L5 mixes standard and gentle fire: `qokedy` ("maintain fire") and `qokeedy` ("gentle fire") side by side. The line's notable token is `qokechckhy` -- a long compound encoding heat with stabilization, adjustment, watching, and a heat-level check all in one instruction. This is a careful, monitored fire adjustment, not a routine maintenance step.

L6 introduces the first cooled-transfer-watch: `shecthy` ("passively watch a cooled transfer"). Something hot has been removed and is being observed as it cools. This is followed by `qokeedy` x2 and scaffold (`saltar`). The cooled-transfer-watch is the ecth signature of calcination: burn, remove, watch the cooled ash.

L7 is observation-heavy: three `sheky` ("observe the heat state passively") and `sheckhy` ("passively observe stabilized heat level"), with only one fire token (`qokar`). The operator is watching more than acting -- a passive observation phase between active calcination steps.

L8 pairs a transfer-watch (`shcthy`) with a cooled-transfer-watch (`shecthy`) on the same line, sandwiching fire tokens (`qokain` x2, `qokar`, `qokeedy`). The line closes with `olkam` ("continue: heat finalized"). This reads as: watch the active transfer, watch the cooled transfer, verify, finalize the heat stage.

L9 continues with another transfer-watch (`chcthy`) and sustained heat (`qokal` x2, `qokain`). The pattern of heat-then-observe-transfer persists.

L10 marks a material-handling cluster: `dalched` ("place material carefully while checking"), `dalom` ("material handling finalized"), alongside sustained heat (`qokain`), a heat-level check (`chckhy`), and observation (`shedy`, `shey`). New material is being added and processed under heat with monitoring.

L11 has the fourth heat-level check (`chckhy`), more transfer monitoring (`chcthy`), and `qotar` ("transfer and note result"). Transfer and heat monitoring continue.

L12 carries the third cooled-transfer-watch (`shecthy`), gentle heat (`qokeedy`), two `qokal` ("fire reached target"), and `qoky` ("cease heating"). The heat cycle reaches target and backs off.

L13-L14 shift toward structural tokens: multiple `ol` (hold), `kaiin` ("deep iteration"), `aiiin` ("yield iterate x3 bind" -- the only triple-i token in this paragraph, signaling exceptionally deep cycling), and `shcthy` (transfer-watch). L14 introduces `dain` ("bind material into cycle") -- a material addition mid-paragraph.

L15-L16 carry the final material additions: two `dar` ("add new substance") and `checthy`/`shecthy` (cooled-transfer-watches). `qokaiin` on L16 ("sustained deep cyclic heating") indicates extended iterative processing. The material is being burned through repeated cycles.

L17 closes P1 with heavy vessel/continuation tokens: `otaiin`, `olkaiin`, `olkain`, `oraiin` -- all deeply iterative. The final token sequence is `checthy` then `olor` -- one last cooled-transfer-watch before the paragraph ends.

**Profile:** P1 is a massive, sustained calcination operation. The token profile is dominated by fire management (55 qo-prefix tokens, 27% of the paragraph), with heavy observation (27 sh-prefix, 23 ch-prefix) and significant vessel management (11 ok, 18 ol, 12 ot). The 15 observation MIDDLEs -- particularly the 6 cooled-transfer-watches -- encode an operator who repeatedly burns material, removes it, watches it cool, checks the ash, and returns it to the fire. Seven material additions are distributed across the 17 lines, consistent with a multi-material or multi-batch process.

---

### P2 (Lines 18-29, 117 tokens) -- Continued Processing at Gentler Heat

**What the tokens say:**

P2 is the second-largest paragraph, with 117 tokens across 12 lines. The e-depth rises to 0.56 -- a significant shift from P1's 0.40. The operator has moved from sustained strong fire to a regime with more cooling intervention. This could indicate a shift from direct calcination to processing the calcined product: dissolution, gentle distillation, or extraction from the ash.

The fire-source tokens (`qo`) still dominate (35 tokens, 30%) but the character shifts: `qokaiin` ("sustained deep cyclic heating") appears 3 times, and `qokeey` ("establish gentle heat") appears 4 times. The heat profile is gentler and deeper -- longer cycles at lower temperature.

**Observation MIDDLEs (3 total: 1 cth, 2 ecth):**

Only 3 observation MIDDLEs across 117 tokens (1 per 39 tokens) versus P1's 15 across 204 tokens (1 per 14 tokens). The monitoring intensity drops by nearly 3x. If P1 was the active burning phase requiring constant observation, P2 is a more autonomous process that needs less intervention.

The two ecth tokens (`shecthy` on L23, `checthy` on L21) continue the cooled-transfer-watch pattern, but at much lower density. Cooled products are still being observed, but less frequently.

L18 opens with a paragraph gallows (`pcheolkal`) and `dal` ("carefully place material"), then fire and observation. Material is being loaded for a new processing phase.

L19-L20 alternate fire management and observation. `qokain` x2 and `qokal` x3 across these lines show sustained heating reaching target states. L20 has the only transfer-watch in P2 (`chcthy`) alongside a material addition (`daiin` -- "start a new cycle") and sealed vessel processing (`okaiin`).

L21-L23 are dominated by gentle heat tokens: `qokeedy`, `qokeey` x4, `olkeey` x2. The fire regime has clearly shifted to balneum-level. L21 and L23 each carry a cooled-transfer-watch, but otherwise monitoring is light.

L24-L26 represent the middle of P2 with `qokain` x3 and `qokaiin` x3 -- the deepest iterative cycling on the folio. The process is running through extended repeated passes. Two `sheckhy` ("passively observe stabilized heat level") appear on L24 and L26, but these are not counted as observation MIDDLEs (they lack the canonical ckh/cth/ecth structure).

L27 has `olkeeey` -- a triple-e continuation token, the deepest cooling/stabilization on the folio. This is extremely gentle heat.

L28-L29 close with sustained cycling (`qokain` x2), gentle heat (`qokeedy`), and transfer monitoring (`oteey`, `otain`). L29's `rar` and `alshees` are unusual structural tokens that do not appear frequently in the corpus.

**Profile:** P2 continues the calcination-derived processing but at gentler heat. The shift from e-depth 0.40 to 0.56, the 3x reduction in observation MIDDLEs, and the appearance of deep-iteration and gentle-heat tokens all indicate a different operational regime -- likely processing what P1 calcined. Three material additions (dar count: 3) and 2 quality checks (chekar count: 2) confirm active handling of product.

---

### P3 (Line 30, 7 tokens) -- Micro-Transition

**What the tokens say:**

Only 7 tokens on a single line. P3 is the smallest paragraph on the folio and one of the smallest in the cold-read corpus.

```
L30:  torolshsdy  opchey  shepchy  qotain  shcthy  qokedy  daly
```

The sequence reads: a complex structural token, an observation pause, passive watching with adjustment, a sustained iterative transfer (`qotain`), a transfer-watch (`shcthy`), standard fire maintenance (`qokedy`), and a careful material placement completed (`daly`).

The single transfer-watch (`shcthy`) is the only observation MIDDLE. The e-depth of 0.43 is moderate. One material addition (`daly` -- "careful placement, done").

**Profile:** This is a brief bridge between P2 and P4 -- a physical transition step where material is moved with one transfer-watch. Similar in function to the micro-paragraphs seen on other folios (f75r P7 at 11 tokens, f84r P2 at 12 tokens), these encode brief physical handling between longer processing phases.

---

### P4 (Lines 31-36, 45 tokens) -- Cooled-Ash Processing

**What the tokens say:**

P4 has zero material additions (dar = 0) but the highest ecth density on the folio: 3 cooled-transfer-watches across 45 tokens (1 per 15 tokens). Combined with 1 heat-level check, there are 4 observation MIDDLEs total -- denser than P2 (3 per 117 tokens) though less than P1.

The zero-dar profile is significant. No new material enters the process. P4 is working with what P1-P3 already produced. Combined with the ecth dominance, this reads as: the operator is handling previously calcined, cooled material -- examining it, processing it further, but not adding anything new.

L31 opens with a transfer operation (`tolkain`), sealing (`otal`), state checks (`chedy`, `shedy`), a stabilized heat-level check (`checkhy`), and heat application (`qokar`). The apparatus is prepared and heat applied.

L32 is the observation-MIDDLE core: two `checthy` (cooled-transfer-watches) bracketing `qokain` x3 (sustained cyclic heating). The pattern is: observe cooled product, apply sustained heat, observe cooled product again. This is a processing cycle that alternates between heating and examining the cooled result -- consistent with repeated calcination or ash refining.

L33 is monitoring-dense: `sheckhy` x2 and `checkhy` -- three heat-observation tokens. The operator is watching the fire level carefully. `qokar` ("apply heat and note response") and `qokeey` ("establish gentle heat") frame the observations. There is an active calibration happening: is the fire right?

L34 continues with `qokain` x3 (sustained cycling), `shckhy` (the only canonical heat-level check in P4), and another cooled-transfer-watch (`checthy`). The cycle of heat-then-observe-cooled-product continues.

L35 introduces `qotain` ("sustained iterative transfer") -- material is being moved repeatedly. `chedy` x1 and `shedy` x1 provide state verification.

L36 closes with `qokain` x3 (sustained cycling) and `shedy` -- observation during the final heat cycle. `lolom` on L35 and `orol` on L36 are structural closures.

**Profile:** P4 is a self-contained processing step: no new material, heavy cooled-transfer observation (3 ecth), and sustained cyclic heating (8 qokain-class tokens). The e-depth of 0.47 is moderate -- more cooling than P1 (0.40) but less than P2 (0.56). This is still fire-intensive work, but with more cooling intervention than the initial calcination. One quality check (chekar = 1) indicates product assessment.

---

### P5 (Lines 37-38, 19 tokens) -- Vessel Cycling at Gentle Heat

**What the tokens say:**

P5 has 19 tokens over 2 lines, zero dar, zero observation MIDDLEs, and the highest e-depth of any paragraph on f80r (0.58). The monitoring has disappeared entirely and the heat is the gentlest on the folio.

```
L37:  polchy  efaloir  okain  okaiin  cheey  kain  ylor  olkeey  qokal
L38:  sal  shy  loiin  cheey  qotl  shety  cheoky  qokain  cheey  ram
```

Vessel management tokens dominate: `okain` ("seal for a cycle"), `okaiin` ("extended sealed processing"), and `olkeey` ("continue at gentle heat"). Three `cheey` ("gentle active verification") appear -- a token that checks without intense intervention.

L38 closes with `ram` ("stage done -- note result"). This is a terminal marker: a phase of work is complete and the result is recorded.

**Profile:** P5 is a brief autonomous step. The vessel is sealed, gentle heat applied, and the process left to run. Zero observation MIDDLEs confirm the process does not need watching. The `ram` closure suggests this step produces a finished intermediate that the remaining paragraphs will handle differently.

---

### P6 (Lines 39-40, 20 tokens) -- Vessel Iteration

**What the tokens say:**

P6 has 20 tokens, zero dar, zero observation MIDDLEs, and e-depth 0.40 -- back to P1's level. The heat is intensifying again after P5's gentle interlude.

```
L39:  tain  chey  ral  kas  chey  lkl  ol  shees  okaiin  olky  oklor
L40:  lol  chey  saiin  shety  okaiiin  sheor  tchey  lkaiin  okainy
```

Vessel iteration tokens dominate: `okaiin` ("extended sealed processing"), `okaiiin` ("yield iterate x3 bind" -- a triple-iteration token, the deepest vessel cycling on the folio), and `lkaiin` x1. The `saiin` ("begin extended binding iteration cycle") on L40 provides iterative scaffolding.

Three `chey` ("quick active verification") spread across both lines provide light-touch monitoring. Zero heat-source (`qo`) tokens in P6 -- the only paragraph on f80r with no fire management at all. Heat is not being managed because the vessel is sealed and the fire was set during an earlier step.

**Profile:** P6 is pure vessel cycling. The operator has sealed the vessel and is running extended iterative passes without touching the fire. The triple-iteration `okaiiin` is notable -- it signals the deepest vessel-cycling commitment on this folio. No material additions, no fire management, no observation MIDDLEs. The process is autonomous.

---

### P7 (Lines 41-43, 29 tokens) -- Final Binding and Closure

**What the tokens say:**

P7 is the closing paragraph: 29 tokens over 3 lines, 2 dar tokens, zero observation MIDDLEs, and the lowest e-depth on the folio (0.34). This is the most sustained heat on f80r -- a strong final fire.

```
L41:  talkl  ol  s  al  cheoly  daiin  otaly  otain  chey  lkain  olom
L42:  sol  tl  shey  qoklcheey  lkaiin  ol  olor  aiin  ydaiin  cheol  kain
L43:  lol  eey  lchey  qokal  cheol  lchor  otlol
```

L41 introduces the two material additions: `daiin` ("start a new cycle") is a material-iteration token. Two transfer monitors (`otaly`, `otain`) and `lkain` (equipment cycling) follow. The line closes with `olom` ("continue: arrange, finalize") -- a structural closure.

L42 has deep iteration tokens: `lkaiin` ("equipment sustained cycling"), `aiin` ("yield into next cycle"), `ydaiin` ("start a new cycle"). The process is binding material through repeated passes. `qoklcheey` is a long compound token encoding heat with state-check and gentle stabilization -- the only `qo` token on L42, and a careful one.

L43 closes the folio: `qokal` ("fire reached target"), `cheol` x2 ("check arrangement state"), `lchey` ("quick apparatus check"), and `otlol` (transfer structural hold). The fire reaches target and the apparatus is verified. The final token is structural -- the folio ends on a hold.

**Profile:** P7 is the wrap-up. Two material additions bind material into the final cycles. The e-depth of 0.34 -- the lowest on the folio -- indicates the strongest sustained heat, consistent with a final calcination or fixation step. Zero observation MIDDLEs: by this point, the operator knows what to expect. Only 2 qo-prefix tokens across 3 lines confirm that the fire was set earlier and runs without further adjustment. Equipment checks (`lchey`, `lchor`) verify the apparatus one last time.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | 0.40 | Sustained fire -- main calcination |
| P2 | 0.56 | Gentler processing of calcined product |
| P3 | 0.43 | Moderate -- brief transition |
| P4 | 0.47 | Moderate -- cooled-ash processing |
| P5 | **0.58** | Gentlest heat -- autonomous vessel cycling |
| P6 | 0.40 | Fire intensity returns for vessel iteration |
| P7 | **0.34** | Strongest fire -- final binding/fixation |

The e-depth draws a characteristic arc: sustained fire (0.40) for the main operation, a rise to gentle heat (0.56-0.58) during intermediate processing, then a drop to the strongest fire on the folio (0.34) for the final step. This is the thermal signature of calcination: strong heat to burn, gentle heat to process, strong heat to finish. The range (0.34-0.58) is narrow compared to folios with distillation (f75r: 0.18-0.63, f107r: 0.09-1.50), consistent with a process that stays in the fire-intensive regime throughout and never needs the deep cooling of distillation or the cold handling of mercury work.

### dar distribution

| Para | dar | % | What it suggests |
|------|-----|---|-----------------|
| P1 | 7 | 54% | Main material loading |
| P2 | 3 | 23% | Continued additions during processing |
| P3 | 1 | 8% | One transition-step placement |
| P4 | 0 | 0% | Processing existing material only |
| P5 | 0 | 0% | Autonomous cycling |
| P6 | 0 | 0% | Autonomous cycling |
| P7 | 2 | 15% | Final material binding |

13 total dar across 441 tokens (3.0%). Material additions are heavily front-loaded: 77% occur in P1-P2. P4-P6 have zero additions -- a 3-paragraph stretch without any new material, covering 84 tokens and 8 lines. This is the profile of a process where all material is loaded early, processed through multiple phases, and only a small final addition completes the operation.

The 1566 match description "animal ash chain (multi-chapter)" implies multiple starting materials processed through a shared calcination procedure. The 7 dar in P1 (distributed across lines 1, 7, 10, 10, 14, 15, 16) are consistent with multiple material additions during the main burning phase -- either multiple batches of the same material or multiple different materials entering the same calcination vessel.

### Observation MIDDLE distribution

| Para | ckh | cth | ecth | Total | Density |
|------|-----|-----|------|-------|---------|
| P1 | 4 | 5 | **6** | **15** | 1 per 14 tokens |
| P2 | -- | 1 | 2 | 3 | 1 per 39 tokens |
| P3 | -- | 1 | -- | 1 | 1 per 7 tokens |
| P4 | 1 | -- | **3** | 4 | 1 per 11 tokens |
| P5 | -- | -- | -- | **0** | -- |
| P6 | -- | -- | -- | **0** | -- |
| P7 | -- | -- | -- | **0** | -- |

**Total: 5 ckh + 7 cth + 11 ecth = 23 observation MIDDLEs**

This is the second-highest observation MIDDLE count of any folio in the cold-read corpus (tied with f116r's ~23). But the composition is entirely different: f116r is dominated by ckh and cth (a fusibility test requires watching heat levels and active transfers), while f80r is dominated by **ecth** (11 tokens -- the most of any folio by a wide margin).

The ecth (cooled-transfer-watch) dominance is the signature finding of this folio. Across all 15 cold-read folios, f80r has more ecth tokens than any other. The ecth MIDDLE encodes watching a cooled intermediate product. In calcination, this is the defining observation: you burn material, let the ash cool, examine the cooled residue (color, texture, completeness of combustion), and decide whether to continue. Each ecth token is a moment where the operator inspects the cooled calcination product.

The observation fade-out is sharp: 15 obs MIDDLEs in P1, declining through P2-P4, then complete silence in P5-P7. By the later paragraphs, the operator knows the product and no longer needs to inspect it. This pattern -- dense early observation fading to autonomous later processing -- appears across multiple matched folios (f75r P3-P5, f79r P6-P10, f107r P3-P18) and consistently marks the transition from active supervision to autonomous operation.

### Distinctive pattern: qo-prefix absence in P6

P6 is the only paragraph on f80r with zero heat-source (`qo`) tokens. Every other paragraph has between 2 and 55. This is a genuine anomaly: the fire is not being managed because the vessel was sealed and the fire set during an earlier step. P6 is pure vessel cycling with no fire intervention -- the operator has committed the process to the sealed vessel and the fire runs autonomously.

### Distinctive pattern: front-weighted structure

f80r allocates 46% of its tokens to P1 and 27% to P2 -- together, 73% of the folio's content is in the first two paragraphs. This is the most front-weighted distribution of any cold-read folio. By comparison, f75r distributes 29% to its largest paragraph (P9, the final cycle), and f107r spreads tokens across 18 paragraphs with no single paragraph exceeding 15%.

A front-weighted structure is consistent with a process where the main operation is a single extended procedure (calcination) that runs for a long time, followed by shorter post-processing steps. The "multi-chapter" description suggests that the 1566 chapters each describe a short variant of the same procedure, and the folio compresses these into one long paragraph encoding the shared calcination operation with multiple material additions.

---

## Verdict: COHERENT (Token-Analysis Only)

Without the matched recipe text, this cold read cannot validate paragraph-recipe correspondence directly. However, the token patterns produce a coherent and distinctive operational profile that is independently consistent with calcination:

1. **ecth dominance**: 11 cooled-transfer-watches, more than any other folio. Calcination requires repeatedly examining cooled ash -- the ecth signature matches this exactly.

2. **Narrow, low e-depth range (0.34-0.58)**: The folio stays in the fire-intensive regime throughout, never reaching the high e-depths of distillation or gentle handling. Calcination is sustained strong fire work.

3. **Front-loaded material additions**: 77% of dar in P1-P2, then a 3-paragraph zero-dar stretch. Materials are loaded early and burned; the later steps process what was already calcined.

4. **Observation fade-out**: 15 obs MIDDLEs in P1, declining to zero in P5-P7. The operator watches intensely during active burning, then the process becomes autonomous.

5. **23 total observation MIDDLEs**: Second-highest of any folio, reflecting the monitoring demands of calcination -- a process where the operator must constantly judge whether material is sufficiently burned.

6. **P6 zero qo-prefix**: One paragraph with no fire management at all -- the fire runs autonomously while the sealed vessel cycles.

7. **Strong final heat (P7 e-depth 0.34)**: The folio closes at its strongest fire, consistent with a final calcination or fixation step.

These patterns do not depend on knowing the specific recipe. They describe a sustained, fire-intensive process with repeated examination of cooled residues, front-loaded material handling, and a transition from active supervision to autonomous cycling. This is the operational profile of calcination. The "animal ash chain" description from the 1566 match is consistent with this profile, though the specific chapter content remains unverified pending SISMEL corpus resolution.
