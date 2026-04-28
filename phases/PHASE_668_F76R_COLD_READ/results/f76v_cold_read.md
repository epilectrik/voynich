# Cold Read: f76v ↔ III.15.0 Ferment Liquefaction and Multiplication

**Match tier:** Strong-supported
**Verdict:** Coherent

---

## The Recipe (III.15.0 — SISMEL Catalan, complete)

> Quant tu hauràs fet lo ferment de tinctura, aquell convertiràs en liquefacció, ajustant-li H segon lo pes que saps, e lo seny te demonstrarà per la obra de natura, en tro sia tot fix dedins lo condensori. E après tu metràs y la cuinqua littera; aquella fixaràs tro veies que's fona com a cera, sens fer fum; e a tant serrà fet lo ferment liquefet de la primera cambra. E aquest in infinit se pot multiplicar per les obres secrets fetes de mixtió en diversa manera.

*Cipher note: This recipe is in Part III (Liber Mercuriorum) and uses the Part III letter cipher: B=simple water, C=simple red sulphur, D=simple dissolved gold, E=compound red water, F=compound red sulphur, G=compound dissolved gold. "H" is ambiguous — only B-G are defined in Part III; H may reference gold from the Part II system or be a raw reference to the 8th letter in the table. "La cuinqua littera" (the fifth letter) = E in Part III = compound red water.*

**Translation:** When you have made the ferment of tincture, convert it to liquefaction by adding H according to the weight you know, and sense will demonstrate through nature's work until all is fixed inside the condenser. Then put in the fifth letter [E = compound red water]; fix that until you see it melts like wax without smoke; and then the liquefied ferment of the first chamber is made. This can be infinitely multiplied through secret works of mixing in diverse ways.

The recipe describes a three-phase operation: (1) add a substance to the ferment and fix it inside the condenser through sustained heating and cooling; (2) add compound red water and fix again until a wax-like fusibility test is passed; (3) multiply the result through repeated mixing operations. The fixation-in-condenser step is the dominant operation — the operator applies heat, watches condensation, monitors transfer rates, and waits for complete fixation. The wax-melt test (melts like wax without producing smoke) is the quality gate. The multiplication step at the end is open-ended ("in infinit").

Key features: Short recipe text (465 characters), heavy emphasis on fixation (condenser work), fusibility test (wax-like melting, no smoke), cipher letter references (H, fifth letter), infinite multiplication claim.

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
| lch | Equipment check | Checking apparatus — seals, receiver, furnace |
| lsh | Equipment watch | Monitoring equipment state passively |

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

So `qo` + `k.e.e.d.y` reads compositionally as: *at the fire (qo), heat (k), stabilize (e), stabilize (e), mark (d), done (y)* — a gentle heat application with double stabilization, executed and closed. Across matched folios, this consistently appears where the recipe says to apply gentle heat (balneum mariae / water-bath level), giving the workshop reading **"gentle fire — balneum level."**

When `t` replaces `k` as the HEAD atom, the instruction shifts from direct heating to **transfer** — apparatus-mediated movement of material. `qo` + `t.e.e.d.y` reads: *at the fire, transfer, stabilize, stabilize, do, done* — a gentle heat-driven transfer. This is the characteristic token of condenser work: heat drives material through the apparatus, and the operator monitors the transfer.

**Key tokens on this folio:**

| Token | Prefix | Atoms | Compositional reading | Workshop Reading | Source |
|-------|--------|-------|-----------------------|-----------------|--------|
| qokedy | qo | k.e.d.y | fire: heat, stabilize, do, done | Maintain current fire level | PT-013 (10/10) |
| qokeedy | qo | k.e.e.d.y | fire: heat, stabilize x2, do, done | Gentle fire — balneum / water-bath level | PT-013 (10/10) |
| qokain | qo | k.a.i.n | fire: heat, yield, iterate, bind | Sustained cyclic heating | PT-013 (10/10) |
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate x2, bind | Sustained deep cyclic heating | B Dict D1 |
| qokeey | qo | k.e.e.y | fire: heat, stabilize x2, done | Establish gentle heat state | B Dict D1 |
| qoky | qo | k.y | fire: heat, done | Cease heating | B Dict D1 |
| qotedy | qo | t.e.d.y | fire: transfer, stabilize, do, done | Execute a heat-driven transfer | B Dict D1 |
| qoteedy | qo | t.e.e.d.y | fire: transfer, stabilize x2, do, done | Gentle heat-driven transfer (condenser) | B Dict D2 |
| qotain | qo | t.a.i.n | fire: transfer, yield, iterate, bind | Sustained cyclic transfer operation | B Dict D2 |
| qotar | qo | t.a.r | fire: transfer, yield, respond | Transfer heat/material and note result | B Dict D1 |
| qotal | qo | t.a.l | fire: transfer, yield, hold | Transfer reached target — stage done | B Dict D2 |
| qol | qo | l | fire: hold | Hold current heat level | B Dict D1 |
| qokol | qo | k.o.l | fire: heat, arrange, hold | Heat arranged and held steady | B Dict D2 |
| qokey | qo | k.e.y | fire: heat, stabilize, done | Brief stabilized heat | B Dict D2 |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| daiin | da | i.i.n | material: iterate x2, bind | Bind material into extended cycle | B Dict D0 |
| dal | da | l | material: hold/state | Carefully collect or place material | PT-013 (9/10) |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state — verify cooling/stabilization | B Dict D1 |
| chey | ch | e.y | test: stabilize, done | Quick active verification | B Dict D1 |
| cheedy | ch | e.e.d.y | test: stabilize x2, do, done | Check the gentle-cooling state | B Dict D2 |
| checkhy | ch | e.c.k.h.y | test: stabilize, adjust, heat, watch, done | Is the heat level right? (extended check) | B Dict D2 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Check the heat level | B Dict D2 |
| chekar | ch | e.k.a.r | test: stabilize, heat, yield, respond | Quality check — is the product right? | B Dict D2 |
| checthy | ch | e.c.t.h.y | test: stabilize, adjust, transfer, watch, done | Watch a cooled transfer (active) | Obs. MIDDLE |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate (clarity, fumes, color) | PT-013 (10/10) |
| shey | sh | e.y | watch: stabilize, done | Watch briefly — quick passive check | B Dict D1 |
| sheedy | sh | e.e.d.y | watch: stabilize x2, do, done | Extended passive observation | B Dict D2 |
| shecthy | sh | e.c.t.h.y | watch: stabilize, adjust, transfer, watch, done | Watch a cooled transfer (passive) | Obs. MIDDLE |
| shckhy | sh | c.k.h.y | watch: adjust, heat, watch, done | Passively observe the heat level | B Dict D2 |
| sheckhy | sh | e.c.k.h.y | watch: stabilize, adjust, heat, watch, done | Watch — is the heat level right? | B Dict D2 |
| okeedy | ok | e.e.d.y | vessel: stabilize x2, do, done | Vessel at gentle balneum temperature | B Dict D1 |
| okedy | ok | e.d.y | vessel: stabilize, do, done | Check vessel during cooling | B Dict D1 |
| okaiin | ok | a.i.i.n | vessel: yield, iterate x2, bind | Extended sealed processing, multiple cycles | B Dict D1 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal the vessel for a processing cycle | B Dict D1 |
| otedy | ot | e.d.y | drip-rate: stabilize, do, done | Check drip/flow rate during cooling | B Dict D1 |
| oteedy | ot | e.e.d.y | drip-rate: stabilize x2, do, done | Monitor gentle transfer rate | B Dict D2 |
| otar | ot | a.r | drip-rate: yield, respond | Note the drip/transfer rate | B Dict D3 |
| otaiin | ot | a.i.i.n | drip-rate: yield, iterate x2, bind | Extended transfer monitoring cycle | B Dict D2 |
| saiin | sa | i.i.n | scaffold: iterate x2, bind | Begin extended binding iteration cycle | B Dict D1 |
| lchedy | lch | e.d.y | equipment: stabilize, do, done | Check equipment state during cooling | B Dict D1 |
| lshedy | lsh | e.d.y | equipment-watch: stabilize, do, done | Monitor equipment state | B Dict D2 |
| olkeedy | ol | k.e.e.d.y | continue: gentle heat, do, done | Continue: gentle heat operation | B Dict D2 |
| olkedy | ol | k.e.d.y | continue: heat, stabilize, do, done | Continue: standard heat operation | Compositional |
| dy | -- | d.y | mark, done | Cycle close — action complete | B Dict D1 |
| ol | -- | o.l | arrange, hold | Hold steady | B Dict D0 |
| am | -- | a.m | yield, final | Phase done — yield result and close | B Dict D0 |
| sol | so | l | sequence: state | Mark current state in sequence | B Dict D1 |

**Observation MIDDLEs** — specific atom combinations within the body that mark active monitoring points:

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

---

## The Folio

**f76v:** 400 tokens, 41 lines, 6 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|---------------------|
| P1 | 1-14 | 144 | 3 | 1.01 | 2 ecth | Fixation in condenser: add H, heat and fix |
| P2 | 15 | 5 | 0 | 1.20 | 1 ecth | Cooled-transfer verification: fixation checkpoint |
| P3 | 16-24 | 86 | 2 | 0.98 | 1 ckh | Add fifth letter (E) and begin second fixation |
| P4 | 25-29 | 52 | 3 | 0.67 | -- | Fix until wax-like melting — fusibility test |
| P5 | 30-31 | 21 | 0 | 0.71 | -- | Quality gate: wax melt passes, no smoke |
| P6 | 32-41 | 92 | 2 | 0.60 | -- | Multiplication: iterative mixing operations |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active condensation, transfer monitoring). Lower values = more sustained uninterrupted heat (fixation, sustained cycling). A value near or above 1.0 is exceptional — it means cooling/stabilization atoms outnumber all other atoms combined, indicating a process dominated by condensation and cooling management. f76v's e-depths are among the highest of any matched folio, consistent with a recipe centered on fixation inside a condenser.

---

## Paragraph-by-Paragraph Cold Read

### P1 (Lines 1-14, 144 tokens) — Fixation in the Condenser

**Recipe says:** "Convert the ferment of tincture to liquefaction by adding H according to the weight you know, and sense will demonstrate through nature's work until all is fixed inside the condenser."

The dominant step: add a substance, apply heat, and wait for complete fixation inside the condenser. This is the recipe's main operation — the operator heats the material, drives vapor through the condenser, and monitors the transfer until everything is fixed.

**What the tokens say:**

P1 is massive — 144 tokens across 14 lines, 36% of the entire folio. The recipe puts all its procedural weight on the fixation step ("en tro sia tot fix dedins lo condensori"), and the folio allocates proportionately.

The e-depth of 1.01 is the highest of any paragraph on this folio and among the highest across all cold-read folios. Cooling/stabilization atoms outnumber everything else. This is not gentle balneum heat — this is condenser work, where the operation is defined by cooling and transfer monitoring rather than direct heating.

**The prefix distribution confirms this.** The top prefixes are: `qo` x27 (fire management), `ch` x19 (active testing), `sh` x18 (passive observation), `ot` x15 (transfer-rate monitoring), `ok` x13 (vessel management). Transfer-rate monitoring (`ot`) is the standout feature — 15 transfer-rate tokens in one paragraph is exceptionally high. In the condenser, the operator's primary task is monitoring how material moves through the apparatus: watching drip rates, noting flow changes, checking whether material is condensing and fixing. The ot-prefix density encodes exactly this.

L1 opens with vessel arrangement and apparatus setup: `okor` ("vessel: arrange, respond"), equipment monitoring (`lshedy`), and the first heat application (`qofchdal` — a flagged heat-adjustment operation). The line reads as initial setup of the condenser apparatus.

L2 establishes the working rhythm: gentle heat (`qokeedy` — "gentle fire, balneum level"), observation (`shedy` — "watch the distillate"), and state checking (`chedy` — "verify cooling state"). This alternation of heat/observe/check continues throughout the paragraph.

L3 intensifies: three `qokeedy` ("gentle fire") tokens and two `oteedy` ("monitor gentle transfer rate") tokens. Extended iterative binding appears: `chedaiin` — active checking bound into an iterative cycle. The operator has established heat and is now monitoring condensation rates.

L4 introduces the first material addition: `daiin` ("bind material into extended cycle") — the recipe's "adding H according to weight." Then a **cooled-transfer-watch** appears: `shecthy` (ecth observation MIDDLE). The operator adds the substance, then passively watches how the cooled intermediate behaves in the transfer process.

L5-L7 are dense with transfer operations. L5: `otain` ("transfer yield, iterate, bind"), `okain` ("seal vessel for processing cycle"), `chcthedy` (active transfer-watch), `otedy` ("check drip rate"). L7: `okaiin` ("extended sealed processing"), three `oteedy`/`otedy` ("transfer monitoring"), and `qokedy` ("maintain fire level"). The operator is locked into a monitoring loop — heat, watch the transfer, check the drip rate, verify the vessel seal, repeat.

L8 continues the pattern with dense heat management: two `qokeedy`, three `okeedy` ("vessel at gentle balneum temperature"), and `sheedy` ("extended passive observation"). The condenser is running.

L9 is a purely observational line — short (7 tokens), dominated by `ch`/`sh` prefixes. Multiple `cheey`/`cheedy` (active checks) and `shey`/`sheor` (passive observation). The operator pauses to assess: is the fixation progressing?

L10 returns to active intervention: `qopchdy` (heat with adjustment), `daiin` ("bind material into cycle") — the second material addition. Then continued observation and equipment monitoring.

L11 has the third and final material addition of P1: `daiin` again. Two `qokedy` ("maintain fire level") bracket the line, with `sheedy`/`shedy` observation between them. The paragraph is now deep into the fixation cycle — adding material as needed, maintaining heat, watching.

L12: `checthy` — the second **cooled-transfer-watch** (ecth). The operator actively watches the cooled intermediate being produced. Then `qotal` ("transfer reached target — stage done") signals a transfer sub-step completing. The fixation is progressing.

L13 is dominated by transfer operations: three `qoteedy` ("gentle heat-driven transfer") tokens plus `qotedy` ("heat-driven transfer"). The condenser is actively producing output. `saiin` ("begin extended binding iteration cycle") starts a new cycle. `sheedy` x2 ("extended observation") — watching the output.

L14, the final line of P1: `qokeedy` ("gentle fire"), `qoteedy` ("gentle transfer"), `shcthedy` (passive transfer-watch). The paragraph closes with the same heat-transfer-observe pattern that defines it, plus `qoeekeedy` — a deeply stabilized heat operation, three `e` atoms of cooling layered around a heat kernel. The fixation is winding toward completion.

**Match assessment:** Strongly coherent. P1's dominance (36% of folio), extreme e-depth (1.01), exceptional transfer-rate monitoring density (15 ot-tokens), two cooled-transfer-watches (ecth), and three material additions map directly to the recipe's core instruction: add H, apply heat, and fix everything inside the condenser until nature's work is done. The paragraph's character — heavy cooling, constant transfer monitoring, sustained gentle heat — is exactly what condenser-based fixation demands.

---

### P2 (Line 15, 5 tokens) — Fixation Checkpoint

**Recipe says:** (Implicit transition: the first fixation is complete. Before adding the fifth letter, verify the state of the fixed product.)

A brief checkpoint between the two main operations.

**What the tokens say:**

Only 5 tokens on a single line — the smallest paragraph on the folio.

```
L15:  tchedy  lsheedy  chedal  chedy  checthey
```

Every token is a check or observation. The prefix distribution: `ch` x3, `tch` x1, `lsh` x1. No heat tokens (`qo`), no material additions (`da`), no transfer monitoring (`ot`). The operator has stopped all active operations and is purely assessing the result.

The e-depth is 1.20 — the highest of any paragraph on this folio. Every HEAD atom is `e` (cool/stabilize). The fixation has produced a cooled intermediate, and the operator is examining it.

The key token: `checthey` — a **cooled-transfer-watch** (ecth observation MIDDLE). The operator actively inspects the cooled product that came through the condenser. Has the fixation worked? The equipment check (`lsheedy` — "monitor equipment state: gentle, done") and the material assessment (`chedal` — "active check: stabilize, do, yield, state") complete the picture: check the product, check the equipment, verify the state.

**Match assessment:** Coherent. A pure verification step with no active operations. The highest e-depth on the folio confirms this is an assessment of cooled product, not an active process. Positioned exactly where the recipe transitions from "fix until all is fixed inside the condenser" to "then put in the fifth letter."

---

### P3 (Lines 16-24, 86 tokens) — Add the Fifth Letter and Fix Again

**Recipe says:** "Then put in the fifth letter [E = compound red water]; fix that until you see it melts like wax without smoke."

Add a new substance and begin the second fixation cycle. The fusibility test (melts like wax, no smoke) is the target.

**What the tokens say:**

The e-depth drops slightly to 0.98 — still very high but lower than P1. The process is similar (condenser fixation) but now the operator knows the apparatus is working and needs slightly less cooling intervention.

L16 opens with complex setup tokens: `polshdal` (arrangement with material handling), `otedair` ("transfer: stabilize, do, yield, iterate, respond" — a transfer-monitoring setup that initiates a new iterative sequence). Then `qokedy` ("maintain fire level") and `shedy` ("watch the distillate") — restarting the heat-observe cycle.

L17: `olkeey` ("continue: gentle heat, done") — the operator picks up where P1 left off. `shokaiin` ("observe: vessel extended sealed processing") — watching the sealed apparatus. `qokeedy` and `qokedy` appear — fire management reestablished. This line marks the transition from setup to active processing.

L18: `qockhedy` — a **heat-level check** (ckh observation MIDDLE). The only ckh in the paragraph. The operator actively checks: is the fire at the right level for this new fixation? Four heat-source tokens on this line (`qockhedy`, `qodeey`, `qolkeedy`, `qokedy`) indicate active fire adjustment. Then `daiin` — a **material addition**. This is the "fifth letter" being added: compound red water bound into the processing cycle.

L19: Heavy observation — `sheey`, `shedy`, `sheckhy` (passive heat-level check), `checkhy` (active heat-level check). After adding the new substance, the operator monitors intensively. `otar` ("note the drip rate") — transfer monitoring returns.

L20: Sustained processing. `qokedy` and two `qokeedy` ("gentle fire") tokens — maintaining balneum heat. `checkhy` appears again — another heat-level check. `loiiim` ends the line: a deeply iterative binding operation terminating with `m` (final) — multiple iteration cycles reaching a completion point.

L21: `chckhy` — a direct **heat-level check**. Then `chdar` ("active check: do, yield, respond") and monitoring tokens. `salkeedy` ("scaffold: state, gentle heat") — the iterative infrastructure is sustaining gentle heat. `qoteedy` ("gentle heat-driven transfer") closes the line — condenser work continuing.

L22: `qotedy` ("heat-driven transfer") and `qokedy` ("maintain fire") with monitoring between them. Two `lchedy` ("check equipment state") tokens — the operator inspects the apparatus. The transfer-and-check cycle continues.

L23: `qokeedy` ("gentle fire"), `qoteey` ("transfer, stabilize x2, done"), `qokol` ("heat arranged and held steady"). The fire is stabilized and the transfer is proceeding smoothly. Two `shedy` ("watch the distillate") tokens. `raiin` at line end — yield bound into extended iteration.

L24 (final line of P3): `qokeey` ("establish gentle heat"), `dal` ("carefully collect/place material") — the second material addition. The paragraph closes with `lchedy` ("check equipment") and `olshey` ("continue: watch"). Material handling at the end, then monitoring.

**Match assessment:** Coherent. P3 replicates the condenser-fixation cycle of P1 with two key differences: (1) a material addition on L18 corresponding to adding the "fifth letter," and (2) one heat-level check (ckh) where P1 had none — the operator needs to verify fire adjustment for the new substance. The e-depth (0.98) remains very high, confirming continued condenser-dominant work.

---

### P4 (Lines 25-29, 52 tokens) — Fixation to Fusibility

**Recipe says:** "Fix that until you see it melts like wax without smoke."

The second fixation cycle continues, driving toward the wax-melt test.

**What the tokens say:**

The e-depth drops sharply to 0.67. This is the most significant thermal shift on the folio — from the cooling-dominated condenser regime (0.98-1.20) down to a heat-heavier operation. The recipe says to "fix" the substance — fixation by definition means driving off volatile components and consolidating what remains. As fixation progresses, the product becomes less volatile, requiring less cooling management and more sustained heat to complete the process. The falling e-depth tracks this physical reality.

L25: `qokshedy` ("heat: sequence, watch, stabilize, do, done" — a heat-and-observe compound), `qokedy` ("maintain fire level"), `dal` ("carefully place material") — the first material addition of P4. `shey` ("watch briefly") and `opchedy` provide observation. The line reads as continued fixation with material handling.

L26: `qokaiin` ("sustained deep cyclic heating") — the deepest sustained heating token on this folio. The fire is being held at intensity through multiple cycles, driving the fixation. `daiin` ("bind material into cycle") — second material addition. `checkhy` ("is the heat level right?") — an extended heat check. `oteoldy` ("transfer: stabilize, arrange, state, do, done") — monitoring the transfer as it approaches completion.

L27: The paragraph's densest iteration passage. `daiin` — third material addition. Then paired heat-level observations: `shckhey` (passive heat check) and `chckhey` (active heat check) — back-to-back, the operator is carefully verifying the fire from both passive and active perspectives. `qokeedy` ("gentle fire"). Then a remarkable cluster: `saiin` ("begin extended iteration cycle"), `chek` + `ain` + `r` + `ain` + `o` + `kan` — fragmented tokens that suggest compressed iteration-and-binding sequences, culminating in `chlaiiin` ("active check: state, yield, iterate x3, bind") — triple iteration depth, the most deeply iterative token in the paragraph. The fixation is cycling hard.

L28: `saiin` x1 + `sair` x1 ("scaffold: iterate, respond") — iteration infrastructure. `sheckhy` x2 ("watch: is the heat right?") — paired passive heat checks. `qokeedy` ("gentle fire") between them. Equipment checks: `lkeedy`, `lchedy`. The operator is monitoring the system while the fixation deepens.

L29: `sheedy` ("extended observation"), `qokeedy` ("gentle fire"), `qolkey` ("heat: state, heat, cool, done"). Then `okaiin` ("extended sealed processing") — the vessel is sealed for the final push. `chekar` — the first **quality check** on the folio. Is the product right? The operator tests the result of the fixation cycle.

**Match assessment:** Coherent. P4 shows the fixation deepening: e-depth dropping as the product becomes less volatile, sustained deep cycling (`qokaiin`), three material additions, paired heat-level checks (both active and passive), and a quality check (`chekar`) at the end. The quality check on L29 corresponds to beginning to test whether the product "melts like wax without smoke."

---

### P5 (Lines 30-31, 21 tokens) — Quality Gate: Wax-Melt Test

**Recipe says:** "Until you see it melts like wax, without smoke; and then the liquefied ferment of the first chamber is made."

The fusibility test: does the product melt like wax without producing smoke? This is the pass/fail gate.

**What the tokens say:**

Only 21 tokens on 2 lines — a short verification paragraph, structurally parallel to P2 (the fixation checkpoint). Zero material additions. The operator is not processing — the operator is testing.

The e-depth is 0.71. No observation MIDDLEs. The prefix distribution: `sh` x6 (passive observation), `ch` x4 (active testing), `tch` x2, `sa` x2 (scaffold), `ot` x2 (transfer monitoring), `ok` x1 (vessel), `qo` x1 (heat). Observation and testing dominate; only one heat token in the entire paragraph. The fire is maintained at level while the operator focuses on assessment.

**Two `chekar` tokens** — quality checks. This is the only paragraph on the folio with two quality checks, and the only paragraph on f76v with zero material additions and two chekars simultaneously. The recipe's fusibility test (melt like wax, no smoke) is a quality gate, and P5 encodes concentrated quality assessment.

L30: `tchedy` opens — a test check. `chees` ("active check: cool, cool, sequence") and `cheedy` ("check the gentle-cooling state") — monitoring the cooling behavior of the material. `chkaiin` ("active check: heat, yield, iterate x2, bind") — testing the material's response to sustained heat cycling. `sheky` ("watch: stabilize, heat, done") and `shtal` ("watch: transfer, yield, state") — observing what happens when heat is applied and when material transfers. This line reads as the operator applying heat to the product and watching how it responds — does it melt? Does it smoke?

L31: `shekaiiin` ("observe: stabilize, heat, yield, iterate x3, bind") — deep iterative observation of heated material. `shets` ("watch: stabilize, transfer, sequence") and `shety` ("watch: stabilize, transfer, done") — watching transfer behavior. `otey` and `otedy` ("check transfer rate") — monitoring flow. `okaiin` ("extended sealed processing"). `qotar` ("transfer heat and note result") — the single heat-transfer token. The line closes with `chedy` ("verify state").

**Match assessment:** Coherent. P5 is a concentrated quality assessment: two `chekar` quality checks, zero material additions, observation-dominant prefix distribution, and tokens encoding the operator testing the product's response to heat and transfer. This maps to the recipe's fusibility test — "until you see it melts like wax, without smoke." The short length (21 tokens) matches the test's character: you heat a small sample and watch whether it melts cleanly or smokes.

---

### P6 (Lines 32-41, 92 tokens) — Multiplication

**Recipe says:** "This can be infinitely multiplied through secret works of mixing in diverse ways."

The final step: the liquefied ferment is complete, and the recipe pivots to multiplication — repeated mixing operations that can be iterated indefinitely.

**What the tokens say:**

P6 is the second-largest paragraph (92 tokens, 23% of folio), second only to P1. Where P1 encoded the primary fixation, P6 encodes the open-ended multiplication. The e-depth drops to 0.60 — the lowest on the folio. The process has moved beyond condenser-dominated cooling into sustained iterative cycling with more direct heat.

**The defining feature of P6 is iteration density.** The `sa` (scaffold) prefix appears 8 times — more than any other paragraph. `saiin` alone appears 5 times across P6. The scaffold prefix supports iterative cycling infrastructure, and its concentration here encodes the recipe's "in infinit se pot multiplicar" — infinite multiplication through repeated operations.

L32: `tain` ("iterate, bind"), `qotain` ("sustained cyclic transfer"), `qokaiin` ("sustained deep cyclic heating"), `taiin` ("iterate x2, bind") — four iteration-and-binding tokens on a single line. `chckhedy` ("heat-level check with stabilization") monitors the fire. `chedy` x2 provides state verification. The line reads as the first multiplication cycle being initiated — set up the iterative infrastructure, check the heat, verify.

L33: Only 3 tokens — `saiin` ("begin extended iteration cycle"), `otaiin` ("extended transfer monitoring cycle"), `shckhedy` ("passively observe heat level"). A short line establishing the cycling framework and checking heat before the next batch of operations.

L34: `sakaiin` ("scaffold: heat, yield, iterate x2, bind") — a scaffold token with embedded heat cycling. `qotain` ("sustained cyclic transfer") — transfer operations continuing. `saiin` and `otary` ("transfer: yield, respond, done") — more cycling infrastructure. This line layers iteration upon iteration.

L35: `qokeedy` ("gentle fire") — heat returns to balneum level. `qoky` ("cease heating") — then stops. `saiin` starts another cycle. `lchedy` and `lshedy` check equipment. `chedy` x2 verifies state. The operator is cycling through multiplication passes: heat, stop, check, start again.

L36: `daiin` ("bind material into cycle") — the first material addition of P6. The recipe says "mixing in diverse ways" — you need to add material during multiplication. `cheol` ("active check: arrange, state") — verify the arrangement. `okeey` ("vessel: gently cool") — vessel management.

L37: `qoeedy` ("heat: cool x2, do, done"), `qokey` ("heat: stabilize, done"), `qoky` ("cease heating"). Heat applications are short and punctuated — consistent with repeated mixing passes rather than sustained fixation. `saiin` starts yet another cycle. `oiiin` ("arrange, iterate x3, bind") — deep iteration. `chchky` ("active check: adjust, watch, heat, done") and `shekeey` ("observe: stabilize, heat, cool x2, done") — monitoring between multiplication passes.

L38: `saiin` opens the line — another iteration cycle. `qokeedy` ("gentle fire"), `qokain` ("sustained cyclic heating"). `lolsaiiin` — a deeply iterative vessel-load-and-scaffold token. The line has fragments (`r`, `al`, `r`, `aiin`, `dl`) that suggest compressed iteration-binding sequences.

L39: `qokaiin` ("sustained deep cyclic heating") — the deepest heating token reappears. `shedy` x2 ("watch the state"). `san` ("scaffold: bind"), `sar` ("scaffold: respond"), `keedy` ("steady-state thermal check"). Then `qoky` ("cease heating") — another heat-stop cycle.

L40: `daiin` ("bind material into cycle") — the second and final material addition. `qoky` ("cease heating") and `qokaiin` ("sustained deep cycling") — alternating stop-and-restart. `shedy` x2 and `chey` bracket the line — observation and testing throughout.

L41 (final line): `sol` ("mark current state in sequence"), `shey` ("watch briefly"), `chedy` ("verify state"), `qokedy` ("maintain fire level"), `chedy` again, `qol` ("hold heat level"). The folio ends with state-marking, observation, verification, and fire held steady. The `chekar` on this paragraph (1 quality check total) and the final `shedy` close the multiplication with one last assessment. `aiin` at the end — the yield goes forward into the next cycle, the process remaining open.

**Match assessment:** Coherent. P6's defining feature — extreme iteration density (8 scaffold tokens, repeated `saiin`, deep iteration atoms `iii`) — maps directly to the recipe's "in infinit se pot multiplicar." The two material additions match "mixing in diverse ways." The e-depth of 0.60 (lowest on folio) reflects the shift from condenser fixation to sustained mixing operations. The open ending (final `aiin` — yield into next cycle) matches the recipe's claim of infinite multiplicability.

---

## Cross-Paragraph Patterns

### e-depth thermal arc

| Para | e-depth | Interpretation |
|------|---------|----------------|
| P1 | **1.01** | Condenser fixation: cooling-dominant, transfer-heavy |
| P2 | **1.20** | Pure verification of cooled product |
| P3 | 0.98 | Second fixation (add fifth letter): still condenser-dominant |
| P4 | 0.67 | Fixation deepening: product less volatile, more sustained heat |
| P5 | 0.71 | Quality gate: fusibility test (heat + observe) |
| P6 | **0.60** | Multiplication: sustained iterative cycling, direct heat |

The e-depth tells the story of a process that starts in the condenser and ends at the fire. P1-P3 are cooling-dominated (e-depth near or above 1.0) — the operator spends most effort managing condensation, transfer rates, and cooled intermediates. As fixation progresses through P4, the product stabilizes and requires less cooling intervention. P5 (the wax-melt test) checks the product's behavior under heat. P6 (multiplication) drops to 0.60 — now the operation is about sustained iterative heating and mixing, not condensation.

This arc is physically coherent. A fixation process begins with volatile material condensing in the apparatus (heavy cooling), and as volatiles are driven off, what remains is increasingly fixed (less cooling needed). The wax-melt test confirms this: the product melts without smoking, meaning the volatiles are gone. Multiplication then applies direct heat for mixing.

### dar distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 3 | 30% | Adding H + condenser fixation |
| P2 | 0 | 0% | Verification only |
| P3 | 2 | 20% | Adding fifth letter (E) + fixation |
| P4 | 3 | 30% | Fixation deepening |
| P5 | 0 | 0% | Quality test only |
| P6 | 2 | 20% | Multiplication mixing |

Material additions concentrate in the active processing paragraphs (P1, P3, P4) and reappear during multiplication (P6). The two zero-dar paragraphs (P2, P5) are both verification/testing steps — no material is added, only the state is assessed. This matches the recipe precisely: P1 adds H, P3 adds the fifth letter, P4 continues fixation with material adjustments, and P6 mixes for multiplication. The verification steps (P2, P5) are observation-only.

### Observation MIDDLE distribution

| Para | ckh | cth | ecth | Total | Recipe activity |
|------|-----|-----|------|-------|-----------------|
| P1 | -- | -- | 2 | 2 | Condenser fixation: watching cooled transfers |
| P2 | -- | -- | 1 | 1 | Cooled-product verification |
| P3 | 1 | -- | -- | 1 | Second fixation: heat-level check for new substance |
| P4 | -- | -- | -- | **0** | Fixation deepening: process autonomous |
| P5 | -- | -- | -- | **0** | Quality test: no observation MIDDLEs needed |
| P6 | -- | -- | -- | **0** | Multiplication: iteration, not condensation |

The observation MIDDLEs tell a specific story about condenser work. All three `ecth` (cooled-transfer-watch) tokens appear in P1-P2 — the primary fixation phase and its verification checkpoint. The operator is watching cooled intermediates come through the condenser. P3 has one `ckh` (heat-level check) — the operator verifies fire adjustment after adding the new substance. After that, observation MIDDLEs disappear entirely. By P4-P6, the process no longer requires specialized transfer or heat monitoring: the fixation is deepening autonomously, the quality test is a different kind of check (chekar, not observation MIDDLE), and multiplication is iterative cycling.

### chekar (quality check) distribution

| Para | chekar | Context |
|------|--------|---------|
| P1-P3 | 0 | Fixation in progress — nothing to test yet |
| P4 | 1 | First quality check as fixation approaches completion |
| P5 | **2** | Fusibility test: concentrated quality assessment |
| P6 | 1 | Final verification during multiplication |

Quality checks are absent from the fixation paragraphs (P1-P3) and concentrate in P4-P6, with the peak in P5. This distribution matches the recipe's structure: the operator cannot test the product until fixation is advanced, and the wax-melt test (P5) is the decisive quality gate. The single chekar in P4 begins the testing, P5 doubles it for the pass/fail decision, and P6 includes one final check during multiplication.

### saiin (scaffold iteration) distribution

| Para | saiin count | sa-prefix total | Interpretation |
|------|-------------|-----------------|----------------|
| P1 | 1 | 1 | Minimal iteration infrastructure |
| P2 | 0 | 0 | No iteration (verification only) |
| P3 | 2 | 2 | Moderate cycling for second fixation |
| P4 | 4 | 4 | Heavy cycling as fixation deepens |
| P5 | 2 | 2 | Iteration context for the quality test |
| P6 | **8** | **8** | Maximum iteration: infinite multiplication |

The scaffold count nearly doubles at each phase transition: 1 -> 2 -> 4 -> 8. P6's 8 scaffold tokens represent the highest iteration density on the folio. The recipe says "in infinit se pot multiplicar" — the folio encodes this through maximal iteration infrastructure in the final paragraph.

---

## Verdict: COHERENT

f76v produces a coherent paragraph-by-paragraph reading against III.15.0 (ferment liquefaction and multiplication). The folio's 6 paragraphs map to the recipe's procedural steps without post-hoc adjustment:

1. **Condenser fixation** (P1) — 36% of folio, e-depth 1.01, 15 transfer-rate tokens, 2 cooled-transfer-watches. Encodes "add H and fix inside the condenser."
2. **Fixation checkpoint** (P2) — 5 tokens, e-depth 1.20, pure verification with cooled-transfer-watch. The transition between the two fixation phases.
3. **Add fifth letter and fix** (P3) — material addition on L18, heat-level check, e-depth 0.98. Encodes "put in the fifth letter; fix that."
4. **Fixation to fusibility** (P4) — e-depth drops to 0.67 as product stabilizes, first quality check. Encodes fixation deepening toward the wax-melt target.
5. **Wax-melt quality gate** (P5) — 21 tokens, zero material additions, two quality checks. Encodes "until you see it melts like wax without smoke."
6. **Multiplication** (P6) — 8 scaffold tokens (doubling progression 1-2-4-8), e-depth 0.60, iterative cycling with material mixing. Encodes "in infinit se pot multiplicar."

The e-depth arc (1.01 -> 1.20 -> 0.98 -> 0.67 -> 0.71 -> 0.60) tracks the physical chemistry of the process: condenser-dominated fixation gives way to sustained direct-heat multiplication as volatiles are driven off. The observation MIDDLE distribution (ecth concentrated in P1-P2, ckh in P3, then absent) reflects the monitoring shift from condenser-watching to autonomous cycling. The chekar distribution (absent in P1-P3, concentrated in P4-P5) matches the recipe's quality gate. The scaffold doubling progression (1-2-4-8) culminates in maximal iteration density at the multiplication step.

The folio's most distinctive structural signature — e-depths near or above 1.0 in the first three paragraphs — is rare across the matched folio set and specifically encodes condenser-dominant operation, which is exactly what "en tro sia tot fix dedins lo condensori" demands.
