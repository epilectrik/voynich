# Cold Read: f107r — Token Analysis (SISMEL Match Unavailable)

**Match tier:** Supported (token-level only)
**Verdict:** Structurally coherent folio with distinctive two-phase thermal architecture

---

## Recipe Match Status

**Original match:** 1566 Cologne Chapter 44 (Mercuriorum) — "Quicksilver coagulation / correcting errors."

**SISMEL remap failure:** The 1566-to-SISMEL chapter remap failed for this folio. All SISMEL similarity scores returned 0.0. The 1566 Ch44 content does not correspond to SISMEL III.44.0, which is a different recipe entirely.

**Best available approximation:** SISMEL III.44.0 ("Ara direm com se devem corrigir les coses errades") discusses the impossibility of obtaining quintessences without material color changes, the danger of stimulative fire against dry matter, extraction by inhumation to preserve tinctures from burning, and the restoration of lost moisture. This is a **theoretical/cautionary passage**, not a step-by-step procedural recipe — it teaches principles of quintessence extraction with emphasis on avoiding thermal damage.

Because the recipe match is uncertain, this cold read analyzes f107r's token structure independently. Where the SISMEL III.44.0 text is suggestive of alignment, this is noted, but no paragraph-to-recipe mapping is asserted.

---

## Best-Available Recipe Text (SISMEL Catalan, III.44.0 — may not be correct match)

> Fill, impossibilitat regna en esta sciencia que tu pusques haver los espirits quintes sens alguna mutació materiall de color en color aliter de calor en calor. A les quals prech-te que haies sollicitació en tal manera que tots colors te sien agradables, exceptat roior, qui en la materia ve aprés les separacions de les quintes substancies per foch estimulatiu contra la materia secca. Ffill, adonchs les quintes substancies qui estan en sech e's cremen e's consumen lur tinctura... Si tu no saps traure de les aygues l'ayre, prega a natura... E guarda't de fer molt foch en la distillació dels ayres, car lo cors se rubificaria e soffocaria sa virtut attractiva... Trau-lo donchs per inhumacions, car aquells guarden les tinctures de tota adustió e restauran la humiditat perduda e revivifiquen la virtut attractiva.

**Translation:** Son, it is impossible in this science to obtain quintessences without material color changes (from color to color, that is, from heat to heat). Be attentive that all colors please you except redness, which comes from stimulative fire against dry matter. Quintessences in dry form burn and consume their tincture — they can only be extracted when joined artificially with the airs of their waters. Don't make too much fire distilling the airs — the body would rubify and suffocate its attractive virtue. Extract by inhumations, which guard tinctures from burning, restore lost moisture, and revivify attractive virtue.

*Cipher note: III.44.0 is in Part III (Liber Mercuriorum). The Part III letter cipher applies (B=simple water, C=simple red sulphur, D=simple dissolved gold, E=compound red water, F=compound red sulphur, G=compound dissolved gold). No cipher letters appear in this particular passage.*

**Key operational themes (if this recipe is correct):**
- Quintessence extraction requiring careful thermal control
- Avoid excessive fire (redness = thermal damage)
- Inhumation (gentle buried heat) to preserve tinctures
- Restoration of moisture lost through over-heating
- Color changes as process indicators

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
| ka | Heat-to-yield | Direct heat management toward a target state |
| lk | Equipment/furnace | Sustained equipment-level operation |
| ta | Transfer-to-yield | Transfer operations toward a target |
| te | Transfer-execute | Executing a transfer step |
| yk | Pre-heat | Preliminary heat operation |
| po | Stage-open | Opening a new procedural stage |
| al | Product-at-rest | Product has reached stable state |
| ar | Note-yield | Observe what was produced |
| or | Note-response | Acknowledge result and route to next action |
| lch | Equipment-check | Check equipment state (seals, receiver, furnace) |
| kch | Precision-heat | Precision heating with verification |
| pch | Stage-test | Stage verification (paragraph-level check) |
| lsh | Equipment-watch | Monitor equipment passively |

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

**Key tokens on this folio:**

| Token | Prefix | Atoms | Compositional reading | Workshop Reading | Source |
|-------|--------|-------|-----------------------|-----------------|--------|
| qokedy | qo | k.e.d.y | fire: heat, stabilize, do, done | Maintain current fire level | PT-013 (10/10) |
| qokeedy | qo | k.e.e.d.y | fire: heat, stabilize x2, do, done | Gentle fire — balneum / water-bath level | PT-013 (10/10) |
| qokain | qo | k.a.i.n | fire: heat, yield, iterate, bind | Sustained cyclic heating | PT-013 (10/10) |
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate x2, bind | Sustained deep cyclic heating — multiple iterations | PT-013 (15/15) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target — heat stage done | PT-013 (10/10) |
| qokeey | qo | k.e.e.y | fire: heat, stabilize x2, done | Establish gentle heat state | B Dict D1 |
| qokeeey | qo | k.e.e.e.y | fire: heat, stabilize x3, done | Extremely gentle heat — minimal thermal contact | Compositional |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qokchdy | qo | k.c.h.d.y | fire: heat, adjust, watch, do, done | Adjust fire while watching | B Dict D2 |
| qokchey | qo | k.c.h.e.y | fire: heat, adjust, watch, stabilize, done | Adjust fire, watch cooling result | B Dict D2 |
| qotal | qo | t.a.l | fire: transfer, yield, hold | Heat-driven transfer reached target state | B Dict D2 |
| qotaiin | qo | t.a.i.i.n | fire: transfer, yield, iterate x2, bind | Heat-driven transfer cycling through iterations | B Dict D2 |
| qotain | qo | t.a.i.n | fire: transfer, yield, iterate, bind | Iterated heat-transfer cycle | B Dict D2 |
| qockhedy | qo | c.k.h.e.d.y | fire: adjust, heat, watch, stabilize, do, done | Heat-level check with stabilization | Compositional |
| qocthy | qo | c.t.h.y | fire: adjust, transfer, watch, done | Transfer-watch at the fire | Compositional |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| daiin | da | i.i.n | material: iterate, iterate, bind | Start a new cycle — initiate next heating-monitoring loop | B Dict D0 |
| dal | da | l | material: hold/state | Carefully collect or place material | PT-013 (9/10) |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state — verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| cheey | ch | e.e.y | test: stabilize x2, done | Active check — gentle stabilization verified | B Dict D2 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chol | ch | o.l | test: arrange, hold | Check arrangement state | B Dict D2 |
| chody | ch | o.d.y | test: arrange, do, done | Check arrangement, execute, done | B Dict D2 |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly — quick passive check | B Dict D1 |
| sheey | sh | e.e.y | watch: stabilize x2, done | Extended passive observation | B Dict D2 |
| sheeey | sh | e.e.e.y | watch: stabilize x3, done | Very extended passive observation — deep cooling watch | Compositional |
| okaiin | ok | a.i.i.n | vessel: yield, iterate x2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okeey | ok | e.e.y | vessel: stabilize x2, done | Vessel temperature: gentle settling | B Dict D2 |
| okal | ok | a.l | vessel: yield, hold | Vessel at target state | B Dict D2 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal the vessel for a processing cycle | B Dict D1 |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| otaiin | ot | a.i.i.n | drip-rate: yield, iterate x2, bind | Extended transfer monitoring through cycles | B Dict D2 |
| otal | ot | a.l | drip-rate: yield, hold | Transfer rate has reached target state | B Dict D2 |
| otam | ot | a.m | drip-rate: yield, final | Transfer monitoring finalized | Compositional |
| lkaiin | lk | a.i.i.n | equipment: yield, iterate x2, bind | Equipment cycling through iterations | B Dict D2 |
| lchedy | lch | e.d.y | equipment-check: stabilize, do, done | Check apparatus (seals, receiver, furnace) | PT-013 (8/10) |
| kaiin | ka | i.i.n | heat-yield: iterate x2, bind | Iterated heat-to-yield cycle | B Dict D2 |
| kain | ka | i.n | heat-yield: iterate, bind | Single heat-to-yield iteration | B Dict D2 |
| sain | sa | i.n | scaffold: iterate, bind | Begin a binding iteration cycle | B Dict D1 |
| saiin | sa | i.i.n | scaffold: iterate x2, bind | Begin extended binding iteration cycle | B Dict D1 |
| sar | sa | r | scaffold: respond | Iterative cycle channel: respond | B Dict D3 |
| aiin | -- | a.i.i.n | yield, iterate x2, bind | Yield product into the next processing cycle | B Dict D0 |
| am | -- | a.m | yield, final | Phase done — yield result and close | B Dict D0 |
| ol | -- | o.l | arrange, hold | Hold steady | B Dict D0 |
| or | -- | o.r | arrange, respond | Note what happened — route to next action | B Dict D0 |
| ar | -- | a.r | yield, respond | Note the yield — observe what was produced | B Dict D1 |
| al | -- | a.l | yield, hold | Product at rest — yield has reached stable state | B Dict D1 |
| dy | -- | d.y | do, done | Cycle close — action complete | B Dict D1 |
| kcheedy | kch | e.e.d.y | precision-heat: stabilize x2, do, done | Precision-heat: gentle verification | B Dict D2 |
| lolkaiin | lol | k.a.i.i.n | continue-arrange: heat, yield, iterate x2, bind | Load vessel for extended iterative run | Compositional |

**Observation MIDDLEs** — specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

---

## The Folio

**f107r:** 488 tokens, 51 lines, 18 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Structural character |
|------|-------|--------|-----|---------|-------------|----------------------|
| P1 | 1-3 | 31 | 0 | 0.94 | -- | Heavy cooling / initial stabilization |
| P2 | 4-7 | 39 | 1 | 0.82 | 1 ckh | Thermal management with heat-level check |
| P3 | 8-12 | 49 | 0 | 0.69 | -- | Sustained sealed processing, deep iteration |
| P4 | 13-15 | 32 | 0 | 0.44 | -- | Sustained heat with quality checks (2 chekar) |
| P5 | 16-17 | 14 | 0 | 0.57 | -- | Brief transition — transfer and iteration |
| P6 | 18-19 | 23 | 0 | 0.57 | -- | High unprefixed count — structural/arrangement |
| P7 | 20 | 2 | 0 | 1.50 | -- | Flash check (pure cooling verification) |
| P8 | 21-23 | 25 | 1 | 0.20 | -- | Vessel loading — low cooling, high iteration |
| P9 | 24-26 | 31 | 1 | 0.35 | -- | Active heat with material and monitoring |
| P10 | 27 | 10 | 0 | 0.20 | -- | Flagged heat iteration — unusual `f` atoms |
| P11 | 28-29 | 16 | 0 | 0.56 | -- | Equipment cycling and observation |
| P12 | 30-33 | 43 | 1 | 0.21 | -- | Heavy iteration with quality check (1 chekar) |
| P13 | 34-37 | 39 | 4 | 0.28 | 1 ckh | Material-loading phase — heaviest dar |
| P14 | 38 | 9 | 0 | 0.56 | -- | Transfer and flagged operations |
| P15 | 39-41 | 28 | 0 | 0.36 | -- | Sustained heat-to-yield cycling |
| P16 | 42-44 | 25 | 1 | 0.64 | -- | Re-cooling with material addition |
| P17 | 45-47 | 28 | 0 | 0.43 | -- | Deep cyclic heating, transfer finalization |
| P18 | 48-51 | 44 | 0 | 0.09 | -- | Terminal: pure transfer/vessel closure |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation, stabilization). Lower values = more sustained uninterrupted heat (fermentation, inhumation, vessel operations). A value near zero means no thermal operation at all (vessel handling, sealing, final closure).

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1-3, 31 tokens) — Initial Stabilization

**What the tokens say:**

P1 has the highest e-depth on the folio (0.94) — nearly one cooling atom per total atom. This is not gentle heat; this is aggressive cooling/stabilization. Something is being brought under control.

The paragraph opens with `pchdlar` (stage-test: do, hold, yield, respond) — a diagnostic opening. Then an observation sequence: `sheolor` (watch arrangement), and two heat-source operations: `qokchy` ("adjust fire while watching") on L1, followed by vessel operations (`otor`, `okeesodar`).

L2 shifts to transfer monitoring: `qoteos` (heat-driven transfer with arrangement), then `shedy` ("watch the distillate") — passive observation. The line features two `aiin` ("yield into next cycle") tokens flanking the observation, and closes with monitoring: `cheockhy` (a complex monitor combining arrangement, adjustment, heat, and watching) and `qotain` (iterated heat-transfer).

L3 continues with `olcheey` (equipment check with gentle stabilization), `sheos` (observe with arrangement), and `qokeeey` — an **extremely gentle heat** token with triple stabilization. Triple-e heat tokens are rare in Currier B. This encodes minimal thermal contact: barely warming. The line closes with `qotain` (iterated heat-transfer), `ykain` (pre-heat iteration), and `okeey` (vessel at gentle temperature).

**Zero material additions.** P1 is pure process: cool, stabilize, transfer, observe. No substances are introduced — the paragraph manages something already present.

**Structural assessment:** A stabilization-heavy opening paragraph with the highest e-depth on the folio. The triple-e heat token (`qokeeey`) and absence of material additions suggest the folio begins by establishing extremely careful thermal control over existing material. If III.44.0 is correct, this would align with the passage's emphasis on avoiding excessive fire and the principle that quintessences "don't want to be anything but humid simple airs."

---

### P2 (Lines 4-7, 39 tokens) — Thermal Management with Monitoring

**What the tokens say:**

e-depth drops to 0.82 — still heavily cooling-dominated, but heat is increasing. The paragraph introduces the folio's first observation MIDDLE: `chckhy` ("check the heat level") on L7.

L4 opens with `teeody` (transfer-execute: cool, arrange, do, done) — a transfer operation under cooling. Then `chedain` (active check: cool, do, yield, iterate, bind) — the check produces output that feeds into the next cycle. `qoteey` (heat-driven transfer, gently cooled) and `qokar` ("apply heat and note the response") introduce active heating for the first time.

The middle of L4 has `otokcho` — a vessel-seal token with an unusual atom string including heat, adjustment, and watching (o.k.c.h.o). This suggests apparatus management during a monitored thermal operation. `qoked` and `okchedy` close the line: fire management and vessel adjustment-watch.

L5 is heavy on vessel correction: two `okchedy` tokens (adjust, watch, cool, do, done) bracket the line. Three heat-source tokens in sequence (`qokeed`, `qokear`, then `qokain`) show escalating heat: first gentle application, then heat-yield-respond, then sustained cycling. The escalation reads as gradually bringing the system up to operating temperature.

L6 introduces the first material addition: `daiin` ("start a new cycle"). The line also contains `chotchedy` — a monitoring token with a transfer-watch atom combination (o.t.c.h). This is the only transfer-watch observation in the first quarter of the folio. Then `chedaiin` (active check feeding into extended iteration) and the closure `am` ("phase done").

L7 has the heat-level check: `chckhy`. After six lines of gradual thermal buildup, the operator explicitly checks: is the fire at the right level? The line closes with vessel operations at gentle temperature.

**Structural assessment:** P2 transitions from the heavy cooling of P1 to active thermal management. The heat-level check on L7 confirms the operator is now managing a real fire. One material addition and one observation MIDDLE. The paragraph reads as establishing the operating regime.

---

### P3 (Lines 8-12, 49 tokens) — Deep Sealed Processing

**What the tokens say:**

e-depth drops further to 0.69. The paragraph is the largest so far (49 tokens) and is dominated by vessel management (7 `ok`-prefix tokens) and monitoring (9 `ch`-prefix tokens). Zero material additions.

L8 opens with `torshor` (an arrangement-sequence token) then `sheeey` — **triple-e passive observation**, watching very gently. `qokeey` ("establish gentle heat") and `qokedy` ("maintain current fire level") manage the fire. Then `lkaiin` and `qokaiin` — equipment and heat-source tokens both entering deep iteration (double-i).

L9-L10 are dense with vessel correction (`okoiin`, `okeey`, `okeedy`) and monitoring (`chedy`, `chey`, `cheedaiin`). The `cheedaiin` on L10 is significant: an active check with double stabilization feeding into extended iteration — checking the state deeply and routing the result into continued cycling.

L10 also has `qokal` ("fire reached target") and `lchedy` ("check apparatus") — the fire is at the right level, equipment is verified.

L11-L12 shift toward deep iteration: three `okaiin` (vessel: extended sealed processing), two `aiin` (yield into next cycle), and `otaram` (transfer-rate: yield, respond, yield, final) — a compound terminal that reads as "transfer monitoring reaching finality." L12 closes with `chal` (check: yield, hold) and iteration tokens.

**Structural assessment:** P3 is a sealed autonomous processing phase. High vessel management, zero material additions, deep iteration (`i.i.n` and `i.i.i.n` forms prominent). The fire was established in P1-P2 and now runs in sustained fashion while the operator monitors the sealed vessel through many cycles. The drop in e-depth from P1-P2 reflects less active cooling intervention — the process is thermally stable and running.

---

### P4 (Lines 13-15, 32 tokens) — Quality Assessment

**What the tokens say:**

e-depth drops to 0.44 — the folio's inflection point toward sustained heat. The paragraph's most distinctive feature: **two quality checks (chekar-class)**. These are the first on the folio.

L13 opens with `polchls` (stage-open with arrangement) then heavy observation: `sheky` (watch: cool, heat, done), two `shedy` ("watch the distillate"), and `pshedaiin` (observation feeding into extended iteration). Vessel operations `otodal` and `otaral` appear — transfer-rate tokens with yield-respond patterns.

L14 has `cthedy` — a transfer-watch observation. Then `cheol` and `chear` — active checks. `chtaiin` (monitor: transfer, yield, iterate, bind) — checking a transfer that feeds into cycling. `qokaiin` at the end of L14: sustained deep cycling continues.

L15 introduces `qockhal` — a heat-source token with adjustment-heat-watch-yield: check the fire level and bring it to target. Two `sheky` tokens (cool, heat, done) — watching the interplay between cooling and heating. `okeeey` (triple-e vessel cooling) appears — very gentle vessel management. The paragraph closes with iteration tokens.

**Structural assessment:** P4 is an assessment point. After the autonomous processing of P3, the operator checks quality twice and examines the thermal state. The observation tokens are heavy (6 `sh`-prefix) and the quality checks suggest a decision point: is the product satisfactory? Should processing continue?

If III.44.0 is relevant, this could correspond to the passage's emphasis on watching color changes: "all colors should please you except redness."

---

### P5 (Lines 16-17, 14 tokens) — Brief Transition

**What the tokens say:**

Only 14 tokens over 2 lines — a short connecting paragraph. e-depth 0.57 (moderate).

L16 opens with `tolshosor` (a complex arrangement-sequence token) and `olkeedy` ("sustain gentle heat"). Then `qotaiin` (heat-driven transfer cycling) and `otalar` (transfer-rate yielding). An `am` ("phase done") closes the main action.

L17: `sair` ("scaffold: iterate, respond") — an iterative scaffold. Two `chey` ("quick verification") tokens bracket an unusual token `losaiin`.

**Structural assessment:** A transitional paragraph connecting P4's assessment to whatever follows. The scaffold token and phase-close suggest one operational stage is ending and another is beginning.

---

### P6 (Lines 18-19, 23 tokens) — Structural Arrangement

**What the tokens say:**

e-depth 0.57 (moderate). The most striking feature: **11 unprefixed tokens out of 23** (48%) — the highest unprefixed ratio on the folio. Unprefixed tokens are structural/arrangement operations rather than specific heat/vessel/material actions.

L18 opens with `poalosy` (stage-open: yield, hold, arrange, sequence, done) — a new stage with sequential arrangement. Passive observation: `shey`, `sheey` (twice). Unusual tokens appear: `aiphy` (yield, iterate, pause, watch — a deliberate hold), `farsheey` (flagged arrangement with observation), `fol` (flag, arrange, hold), and `opalkaiin` (a long compound: arrange, pause, yield, hold, heat, yield, iterate, iterate, bind).

L19 continues with arrangement and iteration: `oaiin`, `ol`, `rar`, then passive observation (`sheey`) and monitoring (`cholal`, `cheeody`, `cheodaiin`). Terminal: `aldy` (product at rest: do, done).

**Structural assessment:** P6 reads as a procedural rearrangement — the operator is reorganizing apparatus, adjusting setup, pausing between phases. The high proportion of unprefixed structural tokens and the `pause` atoms (`p`) support this reading. No material additions, no heat-level checks. The process is between active phases.

---

### P7 (Line 20, 2 tokens) — Flash Verification

**What the tokens say:**

The smallest paragraph on the folio: only 2 tokens.

```
L20:  tcheol  kcheedy
```

`tcheol` (transfer-check: cool, arrange, hold) — verify the transfer arrangement.
`kcheedy` (precision-heat: stabilize x2, do, done) — precision heat verification at gentle level.

e-depth 1.50 — the highest of any paragraph, but based on only 2 tokens. Both tokens are pure cooling/stabilization checks.

**Structural assessment:** A flash verification point. The operator quickly confirms the arrangement (tcheol) and thermal state (kcheedy) before proceeding. This 2-token paragraph is a quality gate between phases — similar to flash-check paragraphs seen on other folios.

---

### P8 (Lines 21-23, 25 tokens) — Vessel Loading

**What the tokens say:**

e-depth crashes to 0.20 — a sharp drop from P7's 1.50. This is sustained heat with minimal cooling intervention. Vessel management dominates: 5 `ok`-prefix tokens, plus 2 `lk`-prefix (equipment).

L21 opens with `taror` (transfer: respond, arrange, respond) and `olal` (continue: yield, hold). Then dense vessel operations: `okain` (seal vessel for cycle), `okaiin` (extended sealed processing), `qotal` (heat-transfer reached target). Two `lkaiin` (equipment: extended iteration) and an `okeeo` (vessel: cooling arranged). The line is five token pairs of vessel + iteration.

L22: `yksheol` (pre-heat observation), `okaiiin` (triple-i vessel iteration — the deepest iteration form), `shoikhy` (passive observation of iterative heat), `daiin` (the paragraph's only material addition), `qotalal` (heat-transfer at double yield-hold), and `qokal` (fire reached target).

L23 closes with two identical `chodaiin` (monitor: arrange, do, yield, iterate, bind) tokens — monitoring feeding into deep iteration. Between them: `shar` (observe: yield, respond).

**Structural assessment:** P8 is a vessel-loading and sealing phase. The material addition (daiin) loads fresh substance, then the vessel is sealed for deep iterative processing. The triple-i `okaiiin` on L22 is notable — this encodes the deepest sealed processing on the folio. The low e-depth means heat is sustained without cooling interruption: the fire burns steadily while the sealed vessel processes.

---

### P9 (Lines 24-26, 31 tokens) — Active Heat with Material

**What the tokens say:**

e-depth 0.35 (low — sustained heat). Heavy monitoring: 8 `ch`-prefix tokens. One material addition.

L24 opens with `pal` (pause, yield, hold) and `alchky` (product-at-rest: adjust, watch, heat, done). Then vessel management: `okilcheol` (a complex vessel token with iteration, adjustment, watching, and cooling). Two `kair` (heat-yield: iterate, respond) tokens. `dar` — the material addition. Then `pchod` (stage-test: arrange, do) and `lkaiiin` (equipment: triple-i iteration).

L25 is monitoring-heavy: `ycheain`, `chal`, `chedy`, `chody`, `char`, `chdalal` — six monitors in eleven tokens. Interspersed: `qokaiin` (sustained deep heat), `qokchdy` (adjust fire while watching), `qokal` (fire at target). The monitoring density here is the highest on the folio.

L26: `olcheor` and `olcheol` (continue with adjustment, watching, cooling) — sustained monitored continuation. `kaiin` (heat-yield iteration), `otair` (transfer-rate iterate), and `okal` (vessel at target). Closes with `cheody` (active check: arrange, do, done).

**Structural assessment:** P9 is an actively monitored heat phase. The operator is watching closely while maintaining sustained fire and managing material. The monitoring density on L25 suggests this is a critical point where the process outcome depends on careful attention. If III.44.0 is relevant, this could be where the operator must watch for color changes ("all colors should please you except redness").

---

### P10 (Line 27, 10 tokens) — Flagged Heat Iteration

**What the tokens say:**

Single-line paragraph, 10 tokens. e-depth 0.20 (sustained heat). The paragraph's most distinctive feature: **three tokens containing the `f` (flag) atom** — `ofchedy`, `qofchedy`, and `qofchol`. The `f` atom is rare in Currier B; three occurrences in 10 tokens is exceptional.

```
L27:  podar  aiisod  qokiir  otiir  ofchedy  qofchedy  qofchol  chkaiin  chpaiin  orol
```

`podar` (stage-open: do, yield, respond) opens a new stage. `qokiir` (heat: iterate, iterate, respond) — deep iterative heating. `otiir` (transfer: iterate, iterate, respond) — deep iterative transfer. Then the three flagged tokens — these combine the flag marker with adjustment-watch sequences.

`chkaiin` (monitor: heat, yield, iterate, bind) and `chpaiin` (monitor: pause, yield, iterate, bind) close the paragraph — monitoring with both heat and pause orientations.

**Structural assessment:** P10 is a flagged procedural marker. The `f` atom cluster is corpus-unusual. This may encode a warning or special condition — a point where the operator must take particular notice. If III.44.0 is relevant, the flag atoms could correspond to the recipe's warnings about excessive fire ("don't make too much fire distilling the airs — the body would rubify").

---

### P11 (Lines 28-29, 16 tokens) — Equipment Cycling

**What the tokens say:**

e-depth 0.56 (moderate). Equipment prefixes dominate: 2 `lk`, 2 `yk`, 2 `ka`. Zero material additions.

L28: `kar` (heat-yield: respond), two `aiin` (yield into next cycle), monitoring (`chl`, `cholor`), observation (`sheees` — triple-e passive observation), then vessel and equipment operations: `otchy` (transfer: adjust, watch), `lkaiin`, `ykaiin`, `ykal`, `kal`. The line is dense with iteration bindings.

L29: `olkeeo` (continue: heat, cool, arrange) and `lkeeo` (equipment: cool, arrange) — a matched pair of continuation and equipment tokens. Then `ar` (note the yield) and `shol` (observe arrangement).

**Structural assessment:** P11 is equipment management between processing phases. The operator is cycling equipment — adjusting, watching, noting results. The moderate e-depth and absence of material suggest maintenance of the existing thermal state rather than any new action.

---

### P12 (Lines 30-33, 43 tokens) — Deep Iteration with Quality Check

**What the tokens say:**

e-depth 0.21 (very low — deep sustained heat). The second-largest paragraph in the second half. One material addition, one quality check (chekar-class).

L30 opens with `pair` (pause, yield, iterate, respond) and a remarkable token: `aiiikhedy` — a triple-i yield-iterate sequence followed by heat-watch-cool-do-done. This encodes the deepest iteration depth on the entire folio, combined with a full heat-watch-cool cycle. Then `shalkaiin` (observe: yield, hold, heat, yield, iterate, bind) — passive observation of a sustained process. `qokaiin` (sustained deep heat) and several arrangement tokens.

L31: `daiin` — the material addition. Then `sheol` (observe arrangement), `chdy` (actively check: done), `okaiin` (extended sealed processing), `sheykal` (observe: cool, done, then heat-yield-hold), and multiple state tokens. The material feeds into another round of processing.

L32: `salxar` — an unusual scaffold token with what appears to be a diagram marker (`x`). Then `qokaiin` (sustained deep heat), `okal` (vessel at target), `qockhedy` (heat-level check with stabilization), and `qocthy` (transfer-watch at the fire). The heat-level check and transfer-watch together mean the operator is verifying both fire level and what's being produced.

L33 has the quality check: `chekain` (active check: cool, heat, yield, iterate, bind) — a chekar-class quality assessment. Then monitoring (`cheo`, `chey`), heat management (`qol` — hold current heat), and deep iteration (`kaiiin` — triple-i heat-yield). `lcheel` (equipment check: cool, cool, hold) — checking the equipment at gentle temperature. The paragraph closes with `lkar` and `okal` — equipment yield and vessel at target.

**Structural assessment:** P12 is a major processing paragraph. Deep sustained heat (e-depth 0.21), heavy iteration (including the folio's deepest single token `aiiikhedy`), one quality check, and one material addition. The transfer-watch and heat-level check on L32 suggest active monitoring of production quality. This paragraph encodes extended high-temperature processing with careful attention to output.

---

### P13 (Lines 34-37, 39 tokens) — Material Loading Phase

**What the tokens say:**

e-depth 0.28 (low — sustained heat). **Four material additions** — the most of any paragraph, and 44% of the folio's total 9 dar tokens.

L34 opens with `pairar` (pause, yield, iterate, respond, yield, respond — a compound arrangement). Then `lkeey` (equipment at gentle temperature), `qotal` (heat-transfer at target), and `cheotain` — a monitoring token combining observation, transfer, and iteration. `dar` is the first material addition. Then `okaiin` and `otaiin` — vessel and transfer cycling.

L35: `daiin` — second material addition. Then equipment operations: `lkeeol` (equipment at gentle arrangement), `lchedy` (check apparatus), `qokor` (heat: arrange, respond). The line continues with `lkaiin` (equipment iteration), `chedy` (state check), `qotaiin` (heat-transfer cycling). The apparatus is being loaded and checked.

L36: Two more material additions — `dar` and `dal` ("add substance" and "carefully place material"). Between them: `alchor` (product-at-rest: adjust, watch, arrange, respond), `kcheo` (precision-heat: cool, arrange), `rkeey` (gentle cooling). Then `qokchey` (adjust fire while watching cooling) and iteration bindings. The heat-level observation MIDDLE appears: `chckhy` is in L37.

L37 closes the paragraph with the heat-level check: `chckhy` ("is the fire at the right level?"). Then `chol` and `alkain` — monitoring and product-binding.

**Structural assessment:** P13 is the material-loading hub of the folio. Four substances added across 4 lines, with equipment checks, apparatus verification, and one heat-level observation. The low e-depth means materials are being added into a hot, sustained process — not a cooled setup. This reads as replenishing or adjusting the material composition during active processing.

If III.44.0 is relevant, this could correspond to "joining artificially with the airs of their waters" — the materials needed to extract the quintessence from its dry state.

---

### P14 (Line 38, 9 tokens) — Transfer and Flagged Operation

**What the tokens say:**

Single-line paragraph, 9 tokens. e-depth 0.56 (moderate — midpoint cooling).

```
L38:  poaral  orar  ofchey  qoteedy  qotaiin  opchedy  qokchey  otlchdain  aly
```

`poaral` (stage-open: yield, respond, yield, hold) — opening a new stage with compound yield. `orar` (vessel-respond: yield, respond). `ofchey` — another flagged token (flag, adjust, watch, cool, done). `qoteedy` (gentle heat-transfer) and `qotaiin` (heat-transfer cycling). `opchedy` (arrange, pause, adjust, watch, cool, do, done — a complex arrangement check). `qokchey` (adjust fire while watching cooling). `otlchdain` (transfer-rate: hold, adjust, watch, do, yield, iterate, bind — a dense compound transfer operation). Terminal: `aly` (product at rest: done).

**Structural assessment:** P14 is a brief transition with another flagged token. The `ofchey` on L38 is the fourth `f`-bearing token on the folio (three were in P10). The combination of stage-opening, heat-transfer operations, and flagged monitoring suggests a controlled transition between processing phases. The moderate e-depth indicates active cooling is being applied during the transfer.

---

### P15 (Lines 39-41, 28 tokens) — Sustained Heat-to-Yield Cycling

**What the tokens say:**

e-depth 0.36 (low — sustained heat). Heavy on monitoring (7 `ch`-prefix) and vessel management (3 `ok`, 3 `ot`). Zero material additions.

L39 opens with `tair` (transfer: iterate, respond) and two identical `cheol` tokens (active check: cool, arrange, hold). `kchekain` (precision-heat with quality check feeding into iteration) — one of the most operationally dense single tokens, combining precision heat with a quality assessment that routes into the next cycle. Then monitoring and arrangement tokens.

L40 is dense with iteration: `lolkaiin` (load vessel for extended iterative run), `qokaiin` (sustained deep heat), `okaiin` (extended sealed processing), `olkar` (equipment: heat-yield-respond), `otair` (transfer-rate iterate), and two `okal` (vessel at target). Every domain — vessel, heat, transfer, equipment — is running in iterative mode simultaneously.

L41: `qokain` (sustained cyclic heating), `ockhey` (a ckh-class arrangement check), `qokal` (fire at target), `otal` (transfer at target), `otam` (transfer monitoring finalized). The `m` terminal in `otam` marks a finalization — this transfer sequence is complete.

**Structural assessment:** P15 is a full-intensity processing paragraph where all systems cycle simultaneously. The finalization on L41 (`otam`) closes a transfer sequence. Zero material additions mean P15 runs on what P13 loaded. The sustained low e-depth encodes continuous heat without cooling interruption.

---

### P16 (Lines 42-44, 25 tokens) — Re-cooling with Material

**What the tokens say:**

e-depth rises sharply to 0.64 — the first significant cooling increase since P2. One material addition.

L42 opens with `pcholky` (stage-test: arrange, hold, heat, done) and `sokeey` — a rare `so`-prefix token (gentle heat). `oteey` (transfer: gentle cooling), `ykchey` (pre-heat adjustment-watch), and `paichy` (pause, yield, iterate, adjust, watch). Multiple vessel tokens at gentle temperature: `okeey` appears twice across the paragraph. Terminal: `kairam` (heat-yield: iterate, respond, yield, final) — a compound finalization.

L43: `okeear` (vessel: gentle cool, yield, respond), `daiin` (the material addition — start new cycle), `sheody` (watch arrangement), `ykchedy` (pre-heat verification). Then `chykaiin` (monitoring: heat-yield, iterate, bind), `otal` (transfer at target), `taiin` (transfer iteration), `chotaiin` (monitoring transfer iteration), and `aram` (note yield: final).

L44: `ycheodain` (monitoring: cool, arrange, do, yield, iterate, bind) — a complex check. `okeey` (vessel at gentle temperature). Then `qokeeody` (fire: heat, cool x2, arrange, do, done — gentle heat with arrangement) and `qokaiin` (sustained deep heat).

**Structural assessment:** P16 re-introduces cooling after the sustained-heat stretch of P8-P15. The e-depth jump from 0.36 to 0.64 is the sharpest upward shift on the folio. One material addition mid-paragraph. The cooling and material together suggest a new phase is beginning: the operator adds substance and actively manages temperature downward.

If III.44.0 is relevant, this could correspond to "restoring lost moisture" — adding humid material while cooling the system.

---

### P17 (Lines 45-47, 28 tokens) — Deep Cyclic Heating and Transfer Finalization

**What the tokens say:**

e-depth 0.43 (moderate-low). Heavy on heat-source management: 6 `qo`-prefix tokens. Zero material additions.

L45 opens with `todky` (transfer: do, heat, done) and `chedy` (check state). Then two significant heat tokens back-to-back: `qockhy` (adjust fire while watching) and `qokeedy` (gentle balneum fire). `qokokil` (heat: arrange, heat, iterate, hold) — a compound token encoding heat-arrangement-iteration, suggesting a complex furnace adjustment. `chees` (check: cool, cool, sequence) and `opal` (arrange, pause, yield, hold) close L45. Two transfer bindings: `otaiin` and `otaram` (the latter with finalization).

L46: `sar` (scaffold: respond), `cheey` (active check, gentle), `qodaiin` (heat-source: do, yield, iterate, bind — an unusual `d`-headed heat operation). Two `qokaiin` (sustained deep heat). Two `otal` (transfer at target). `alkal` (product-at-rest: heat, yield, hold) — the product is at thermal equilibrium.

L47: `okain` (seal vessel for cycle), `cheey` (active check), `lol` (hold arrangement), `loeey` (state, arrange, cool, cool, done), and `oiinal` (arrange, iterate, bind, yield, hold).

**Structural assessment:** P17 is the last major heating paragraph before closure. Two finalization tokens (`otaram`, `alkal`) suggest the main thermal processing is completing. The compound heat tokens (`qokokil`, `qodaiin`) are unusual forms not common across Currier B — they may encode specialized furnace operations specific to this recipe.

---

### P18 (Lines 48-51, 44 tokens) — Terminal Closure

**What the tokens say:**

e-depth 0.09 — the lowest of any paragraph and among the lowest across all cold-read folios. This is zero thermal operation: pure vessel handling, transfer, and closure.

The paragraph is the second-largest on the folio (44 tokens) — a substantial closing sequence.

L48: `faiiral` — another flagged token (flag, yield, iterate, respond, yield, hold). `chkal` (monitor: heat, yield, hold — thermal finalization check). Two `lky` (equipment: done) — equipment shutdown. Dense transfer and binding: `otain`, `qotain`, `oty` (transfer: done), `otaiin`, `ytaiin`. Terminal: `om` (arrange, final).

L49: `alain` (product: yield, iterate, bind), `aifhy` (yield, iterate, flag, watch — flagged observation), `chkain` (monitor: heat, yield, iterate, bind). Then paired sequences: two `okair` (vessel: yield, iterate, respond) alternating with two `chtl` (monitor: transfer, hold). This pairing encodes alternating vessel-check and transfer-hold operations — systematically closing down.

L50: `chain` (monitor: yield, iterate, bind), `al` (product at rest). `lkeey` (equipment: gentle cooling). `chol` (check arrangement). `taidy` (transfer: iterate, do, done). Two transfer bindings: `qotaiin` and `ytaiin`. Equipment operations: `lkl`, `lfchal`. Then `pchdy` (stage-test: do, done) — a paragraph-level closure check. `pal` (pause, yield, hold) and `tar` (transfer: respond).

L51 (final line): `sar` (scaffold: respond), `ain` (yield, iterate, bind), `chol` (check arrangement). Then `olcheey` (continue: adjust, watch, gentle cooling). Two `otal` (transfer at target). `ol` (hold steady). `otchy` (transfer: adjust, watch). **`qoky` ("cease heating")** — the fire is shut down. Terminal: `otaily` (transfer: yield, iterate, hold, done) — the very last token closes the transfer sequence.

**Structural assessment:** P18 is a systematic shutdown. The e-depth of 0.09 means virtually no thermal operation — everything is vessel handling, transfer closure, equipment shutdown. The `qoky` ("cease heating") near the end of L51 explicitly marks fire shutdown. Multiple finalization markers (`om`, `pchdy`, `otal x2`) confirm procedural completion.

The 5 flagged tokens across the folio (3 in P10, 1 in P14, 1 in P18) bookend the second half, possibly marking cautionary checkpoints. The final `faiiral` on L48 may be a closing procedural flag.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | **0.94** | Heavy initial stabilization/cooling |
| P2 | 0.82 | Active thermal management, still cooling-heavy |
| P3 | 0.69 | Sealed processing, moderate cooling |
| P4 | 0.44 | Quality assessment — sustained heat established |
| P5 | 0.57 | Brief transition (slight cooling rebound) |
| P6 | 0.57 | Structural rearrangement |
| P7 | **1.50** | Flash verification (2 tokens, pure cooling check) |
| P8 | **0.20** | Vessel loading — sustained heat begins |
| P9 | 0.35 | Active monitored heating |
| P10 | **0.20** | Flagged heat iteration |
| P11 | 0.56 | Equipment cycling (moderate) |
| P12 | **0.21** | Deep iteration — sustained processing |
| P13 | 0.28 | Material loading under sustained heat |
| P14 | 0.56 | Transfer transition (moderate) |
| P15 | 0.36 | Full-intensity cycling |
| P16 | **0.64** | Re-cooling — new phase |
| P17 | 0.43 | Final deep heating |
| P18 | **0.09** | Terminal closure — fire shutdown |

**Two-phase architecture:** The folio divides into two distinct thermal regimes:

1. **Phase A (P1-P7):** High e-depth, cooling-dominated. The average e-depth across P1-P6 is 0.72. The operator is working with active cooling intervention — stabilizing, checking, managing temperature carefully. This phase starts with aggressive stabilization (0.94) and descends toward sustained heat (0.44) before a flash check (P7).

2. **Phase B (P8-P18):** Low e-depth, heat-dominated. The average e-depth across P8-P18 (excluding P7) is 0.33. Sustained heat with minimal cooling. The operator lets the fire burn while monitoring and loading materials. This phase climaxes in P12's deep iteration (0.21) and concludes with the terminal closure (0.09).

The transition occurs at P7-P8: the flash verification gate (e-depth 1.50) followed by vessel loading (e-depth 0.20). This is the sharpest thermal discontinuity on the folio — from pure cooling verification to sustained heat in a single paragraph boundary.

If III.44.0 is relevant, Phase A could encode the careful stabilization and separation that precedes quintessence extraction ("color to color, heat to heat"), while Phase B could encode the inhumation process ("extract by inhumations, which guard tinctures from burning").

### dar distribution

| Para | dar | % | Context |
|------|-----|---|---------|
| P1 | 0 | 0% | Pure stabilization |
| P2 | 1 | 11% | First material introduction |
| P3 | 0 | 0% | Sealed processing |
| P4 | 0 | 0% | Quality assessment |
| P5 | 0 | 0% | Transition |
| P6 | 0 | 0% | Arrangement |
| P7 | 0 | 0% | Flash check |
| P8 | 1 | 11% | Vessel loading |
| P9 | 1 | 11% | Active heating |
| P10 | 0 | 0% | Flagged iteration |
| P11 | 0 | 0% | Equipment cycling |
| P12 | 1 | 11% | Deep processing |
| P13 | **4** | **44%** | Material loading hub |
| P14 | 0 | 0% | Transfer transition |
| P15 | 0 | 0% | Sustained cycling |
| P16 | 1 | 11% | Re-cooling with material |
| P17 | 0 | 0% | Final heating |
| P18 | 0 | 0% | Terminal closure |

**Total: 9 dar across 488 tokens (1.8% material density)**

Material additions are sparse and concentrated: 44% occur in a single paragraph (P13). The folio's material density (1.8%) is notably lower than f75r's (6.3%, 26 dar / 412 tokens). This suggests f107r encodes a process where the primary work is thermal management and monitoring, with relatively few material handling events.

The distribution pattern: one early addition (P2), then nothing through the quality assessment (P3-P7), then gradual loading (P8-P9-P12: one each), then the concentrated loading hub (P13: four), then one final addition (P16) before shutdown. This reads as a process where materials are established early, processed through extended heat cycles, replenished at one critical point, and then run to completion.

### Observation MIDDLE distribution

| Para | ckh | cth | ecth | Total | Context |
|------|-----|-----|------|-------|---------|
| P1 | -- | -- | -- | 0 | Initial stabilization |
| P2 | 1 | -- | -- | 1 | First heat-level check |
| P3 | -- | -- | -- | 0 | Sealed autonomous processing |
| P4 | -- | -- | -- | 0 | Quality assessment (chekar instead) |
| P5-P12 | -- | -- | -- | 0 | Extended processing stretch |
| P13 | 1 | -- | -- | 1 | Material loading — heat-level check |
| P14-P18 | -- | -- | -- | 0 | Final processing and closure |

**Total: 2 observation MIDDLEs across 488 tokens**

This is the sparsest observation MIDDLE distribution of any cold-read folio. Only two heat-level checks (`ckh`), both positioned at operational transitions: P2 (establishing the regime) and P13 (the material-loading hub). Zero transfer-watches (`cth`) and zero cooled-transfer-watches (`ecth`).

The near-absence of observation MIDDLEs combined with the low material density paints a picture of an autonomous or quasi-autonomous process. Once established, the operator intervenes minimally — monitoring via standard prefix tokens (`ch`, `sh`) rather than embedding observation MIDDLEs into compound operations. This is consistent with a process like inhumation: bury the vessel in gentle heat and let it work.

### Quality check distribution

| Para | chekar | Context |
|------|--------|---------|
| P4 | 2 | Post-initial-processing assessment |
| P12 | 1 | Mid-deep-processing check |

Three quality checks total, concentrated at assessment points. P4 checks quality after the initial Phase A processing. P12 checks quality during the deep Phase B processing. This spacing suggests a process monitored at two key decision points rather than continuously assessed.

---

## Distinctive Features for Recipe Identification

The following structural patterns may help identify the correct 1566 recipe when the SISMEL remap is resolved:

1. **Two-phase thermal architecture.** The folio has a clear Phase A (cooling-heavy, e-depth ~0.72) and Phase B (heat-heavy, e-depth ~0.33) separated by a flash verification gate (P7). The correct recipe should describe an initial stabilization/separation phase followed by sustained heating.

2. **Very low material density.** Only 9 dar across 488 tokens (1.8%) — the process is primarily thermal, not material-handling. The correct recipe should not involve frequent material additions or complex preparation sequences.

3. **Material concentration in a single paragraph.** P13 contains 44% of all dar. The correct recipe should have one major material-loading event, not distributed additions.

4. **Flagged tokens (f-atoms).** Five tokens with `f` atoms cluster in P10 (3), P14 (1), and P18 (1). These are rare in Currier B and may encode warnings or special procedural markers. The correct recipe should contain cautionary instructions or flagged steps.

5. **Extremely low terminal e-depth (0.09).** P18's e-depth is among the lowest across all cold-read folios. The process ends with pure vessel/transfer closure, not gradual cooling. The correct recipe should end with a sealing or transfer operation rather than a distillation.

6. **18 paragraphs.** This is a high paragraph count, suggesting either a multi-step process or a recipe with many short procedural phases (typical of cautionary/corrective recipes that alternate between brief instructions and warnings).

7. **Sparse observation MIDDLEs.** Only 2 across the entire folio. The process is largely autonomous once established — consistent with inhumation, long-duration sealed processes, or theoretical/parameter-setting operations.

---

## Tentative Assessment Against III.44.0

While the SISMEL remap failed and III.44.0 may not be the correct match, several structural features of f107r are *consistent* with the passage's themes:

- **Phase A (aggressive stabilization)** aligns with the passage's emphasis on careful temperature control and avoiding redness from stimulative fire.
- **Phase B (sustained heat with low cooling)** aligns with inhumation — "extract by inhumations, which guard tinctures from burning."
- **Flagged tokens** could encode the passage's warnings ("don't make too much fire," "the body would rubify").
- **Low material density with concentrated loading** aligns with a process focused on thermal management rather than complex material preparation.
- **The two-phase architecture** could encode the passage's contrast between what goes wrong (stimulative fire, burning, color damage) and what goes right (inhumation, moisture restoration, revivification).

However, the 18-paragraph structure is unusually detailed for what reads as a relatively short theoretical passage. The correct match may be a longer procedural recipe that the 1566 Ch44 chapter number maps to via a different numbering scheme.

---

## Verdict: STRUCTURALLY COHERENT (Token Analysis Only)

f107r shows a well-organized internal structure with a clear two-phase thermal architecture, appropriate placement of quality checks, concentrated material loading, and a systematic terminal closure. The folio's token patterns are consistent with a quintessence extraction or preservation process emphasizing careful thermal control.

The SISMEL recipe match remains unresolved. The folio's distinctive features — two-phase thermal arc, flagged tokens, sparse observation MIDDLEs, concentrated material loading, and extremely low terminal e-depth — provide a structural fingerprint that should help identify the correct recipe when the 1566-to-SISMEL chapter remap is resolved for this folio.
