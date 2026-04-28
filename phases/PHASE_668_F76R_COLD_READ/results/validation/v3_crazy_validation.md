# v3 Workshop Dictionary Outsider Validation

**Validator:** Crazy-expert agent (unguarded mode)
**Date:** 2026-04-27
**Task:** Read v3 workshop tables for 4 folios as a medieval alchemy outsider. Determine whether the token sequences read as coherent operational encodings of the given recipes, or as pattern-matching dressed as comprehension.

**Methodology:** For each folio I read the first 5 lines cold, identify the recipe's key moment, flag nonsense sequences, and give a bottom-line verdict. I am treating the glosses at face value -- "does this word salad, read left to right, tell an operator what to do?"

---

## Folio 1: f76r -- Sevenfold distillation with silver-plate test

**Recipe summary:** Divide stone into 4 elements. Calcine earth+fire. Distill water+air 7 times. After 6th distillation, drop on silver plate -- if it blackens, do 7th. Result: water of life.

### First 5 lines

**L1:** Starts with `po: Pause: heat and note response`, then a flurry of ch-tests and qo-fire commands. Ends with `sa: Scaffold: begin a binding iteration cycle`. The line has 3 unrecognized tokens out of 10 (30%). What I can read is: start up the fire, run a series of test-and-adjust cycles, scaffold the first iteration.

**Verdict on L1:** This reads like a plausible apparatus startup sequence. You would light the fire, run checks, and mark the beginning of the first cycle. The high unrecognized rate hurts but doesn't kill it.

**L2:** `Watch: steady` -> `Fire: transfer and note result` -> `bring to and note result` -> `Test: steady, pause` -> `Load: secure material` -> `Vessel: seal for processing cycle` -> `Fire: note what happened` -> `Watch: steady` -> `Fire: hold` -> `one pass` -> `Watch: hold state` -> `Fire: gentle steady heat`.

**Verdict on L2:** This is genuinely good. You transfer heat, note the result, load material, seal the vessel, run gentle heat, watch and hold. That is exactly what you do when you begin a distillation pass. The sequencing is operationally coherent: seal BEFORE heat, watch AFTER heat. 100% recognized.

**L3:** Watching steady -> gentle balneum cycles -> transfer operations -> hold -> test steady -> one unrecognized at end.

**Verdict on L3:** Thermal work in progress. Multiple heat-and-check cycles. Reads as the middle of a distillation pass -- fire, watch, transfer, hold, verify.

**L4:** Standard heat cycle -> heat with monitoring -> note result -> test heat until stable -> vessel steady -> another heat cycle -> check equipment -> test complete -> heat with active test -> heat until yield stabilizes -> finalize.

**Verdict on L4:** A line of active distillation with monitoring. The `orar` / `or` cluster (note what happened, note what happened) reads slightly redundant but not incoherent -- you are observing the result twice because this is the critical moment.

**L5:** Gentle balneum cycles -> scaffold mark -> watch steady -> standard heat cycle -> watch gentle state -> vessel steady -> product settled x2 -> test one cycle -> **dar** (add new substance).

**Verdict on L5:** This is where I sit up. The line ends with "product settled, product settled, test one cycle, ADD NEW SUBSTANCE." That reads as: the distillation pass is complete (product settled), now add material back for the next pass. For a recipe that says "distill 7 times" and involves returning water to the vessel, this is exactly the right operational shape.

### Key moment: Silver-plate test (after 6th distillation)

The recipe says: after the 6th distillation, "drop on silver plate; if it blackens, do the 7th."

I'm looking for a cluster around lines 25-35 (if the 47 lines encode 7 passes, each pass is ~6 lines, so the 6th ends around line 36) that shows:

**L25:** `Fire: standard cycle` -> `Check equipment: steady` -> `Heat: hold` -> **`Watch: steady`** -> **`Fire: pause, adjust, watch`** -> `Fire: hold` -> `Setup: steady confirmed` -> **`Vessel: adjust, watch`** -> **`Test: observe temperature directly`** -> `Watch: quick check` -> `Equipment steady` -> something -> `Watch: gentle balneum` -> **`dar: Add new substance`**.

The test+observe+respond cluster followed by dar (add substance) is interesting. But there is no obvious "drop on plate and look for blackening" encoding. The `okar` tokens (L35: "Vessel: note how the contents respond") are the closest -- you are checking the vessel contents and noting the response. That is generically compatible with a quality check but not specifically a silver-plate test.

**L37:** A verification-heavy line: `Execute: iterate` -> `Watch: note result` -> `Vessel: confirm stable` -> `Output: verify drip steady` -> `Vessel: confirm stable` -> `Check equipment: stable` -> `Test: stable` -> `Vessel: note response` -> `Test: stable` -> `Output: note drip result` -> `one pass`.

This is the most test-dense line in the folio -- 6 verification/observation tokens in 11. If this is the quality gate, the system is encoding it as "check everything, confirm everything, note everything" rather than as a specific material test. That is operationally plausible for a "drop on plate" test: the scribe encodes the density of checking, not the specific physical action.

**L41:** `fchedy: Mercury marker: stable confirmed`. The fch token (C1939) appears exactly once in this folio, on the last substantive working line. For a recipe whose final product is "water of life" made from an initial "stone" that involves mercury, the mercury marker appearing at the endpoint is structurally appropriate.

### Nonsense sequences

- **L1 tokens 3,7,9:** Three `op`-prefixed unrecognized tokens in the opening line. The dictionary cannot parse these. This is a real gap.
- **L9 `qctheed`:** Completely garbled. Not fatal but ugly.
- **L19 `qaloin`:** Cannot parse.
- **L22 `ylaiin`:** Cannot parse. 

The unrecognized tokens are scattered (about 1-2 per line in the worst stretches) and don't cluster in ways that suggest the recognized tokens are cherry-picked islands of sense. Most lines are 90-100% recognized.

### Contradictions

- L5 has `al, al` (product settled, product settled) followed immediately by `dar` (add new substance). This seems contradictory -- if the product is settled, why are you adding something? **But in a repeated distillation, this is correct:** the distillate has settled, now you return it to the vessel for another pass. The apparent contradiction resolves with the recipe context.

- L19 has a cluster of 5 `chey` (Test: quick active check) in 14 tokens. That is unusual -- is the scribe really encoding "test, test, test, test, test"? It reads as obsessive checking, which fits the recipe's emphasis on the critical quality gate around the 6th-7th pass. But it also reads as "the dictionary has one word for everything the ch-prefix does and it is 'test'."

### Bottom line: f76r

**CAUTIOUSLY POSITIVE.** The first 5 lines read as a coherent startup-then-distillation sequence. The `al, al, dar` pattern at distillation-pass boundaries is operationally convincing. The mercury marker at L41 is structurally appropriate. The silver-plate test is NOT specifically encoded but is plausibly captured as a dense verification cluster. The main weakness: about 8-10% of tokens remain unparseable, and the ch-prefix readings are monotonous ("test: steady" for almost everything). The dictionary gives the IMPRESSION of comprehension without achieving specificity. Would I buy this as an operational encoding? Yes, at the level of "heat, monitor, verify, load, repeat" -- the basic shape of sevenfold distillation is there. No, at the level of "I can tell you exactly what line encodes the silver-plate test."

**Score: 6/10.** Shape is right, specificity is missing, monotony of ch/sh readings is the main v3 weakness.

---

## Folio 2: f79r -- Mercury sublimation to red elixir

**Recipe summary:** Dissolve white mercury in mercury water. Distill until congealed. Return water 3 times. Strengthen fire until rubification. Sublimate rises white, fixed turns red. Fix elements to complete elixir.

### First 5 lines

**L1:** `Transfer: one processing cycle` -> `Watch: steady` -> `Setup: note what happened` -> `Note result` -> `Watch: steady, heat` -> `Output: monitor drip and note result` -> `Setup: cycle close` -> 1 unrecognized -> `Output: stabilize` -> `Watch: steady`.

**Verdict:** Setup and initial transfer. The `ot` (output) tokens suggest material is already moving through the apparatus. This reads as beginning a distillation process that is already loaded -- consistent with a recipe where the mercury is already dissolved in mercury water before you start.

**L2:** `Fire: gentle transfer` -> `Watch equipment: close` -> `Output: adjust, watch, steady` -> `Steady: hold` -> `Watch: check` -> `Fire: hold` -> `Watch: gentle balneum` -> `Fire: gentle transfer` -> `Steady: complete`.

**Verdict:** Gentle thermal work. Multiple "gentle steady" indicators. The recipe says "distill" -- this is gentle distillation. Consistent.

**L3:** Watch -> gentle transfer -> temperature check -> fire complete -> test -> equipment check -> gentle heat -> respond-check stable.

**Verdict:** More gentle distillation with active monitoring. Temperature checks prominent. Reads as careful temperature control.

**L4:** `Transfer step: steady` -> **`dar: Add new substance`** -> `Fire: transfer and note result` -> Watch -> `Watch: gentle steady balneum` -> `Fire: gentle heat` -> `Vessel: steady` -> `Fire: hold, sequence, watch` -> `Steady: adjust, watch` -> `Fire: set` -> `Steady: hold`.

**Verdict:** THIS IS GOOD. The `dar` at token 2 of L4 comes right after the first distillation pass (L1-L3 are gentle distillation). The recipe says "return water 3 times" -- the first return is happening here. The rest of the line is gentle heating of the returned material. Operationally correct.

**L5:** `Fire: heat until yield stabilizes` -> `Watch: steady` -> `Test: observe material moving` -> `Note result` -> `Test: note result` -> `Sequence: hold, adjust, watch` -> `Fire: hold` -> `Watch: stable` -> `Test: check` -> bare token -> `Test: verify and hold` x2 -> `Test: complete`.

**Verdict:** Heavy testing and verification. The `chcthy` (observe material moving through apparatus) is exactly right for sublimation -- you are watching vapors rise. This is the most recipe-specific token in the first 5 lines and it appears exactly where it should.

### Key moment: Rubification (strengthening fire until fixed matter turns red)

The recipe says: "strengthen fire until rubification." I'm looking for a fire-strengthening cluster.

**L9-L10:** L9 starts with `sa: Scaffold: extended iteration cycle` and runs through heavy fire commands: `Fire: apply heat and note response` -> `Watch: observe and hold` -> `Fire: hold, adjust` -> `Fire: transfer complete` -> `Fire: heat until stable` -> `Fire: finalize`.

L10: `Fire: standard heat cycle` -> `Fire: heat through next cycle` -> `Test: note result` -> `Vessel: hold` -> `Watch: hold` -> `Fire: gentle transfer` -> `Test: transfer and hold` -> `Output: watch steady`.

**This is the fire-strengthening zone.** L9 has 5 qo-fire commands in 9 tokens (55.6%) -- the highest fire density I can see in the folio. The `qokam` (Fire: finalize) at the end of L9 reads as "push the fire to its limit." The transition from gentle balneum in L1-L4 to aggressive heating in L9-L10 matches the recipe's instruction to "strengthen fire."

**L11:** `Watch: set up, iterate, heat, watch` -> `Test: steady` -> `Watch: steady` -> `Watch: cycle close` -> `Output: note result` -> `Watch: steady, heat` -> `Test: observe material moving` -> `Output: stabilize` -> `Note: complete`.

The `chcthy` (observe material moving) returns -- sublimate rising. The `oty` and `otal` (output stabilizing) suggest the sublimate is being collected. This is consistent with "sublimate rises white."

### Nonsense sequences

- **L1 `opcholor`:** Unrecognized compound. One gap.
- **L15 `dyty`:** Garbled. 
- **L20 `oikhy`:** Cannot parse.
- **L28 `odain`:** Cannot parse.

Low rate. Most lines are 100% recognized. f79r is the cleanest of the four folios.

### Contradictions

- **L12** has `ldaiin` (Load: iterate, iterate, bind) which is a strange compound -- you are "loading an iteration"? The compositional reading breaks down here. The da-prefix means "load material" but the -aiin suffix means "extended cycles." Loading extended cycles is category confusion.

### Bottom line: f79r

**POSITIVE.** This is the strongest of the four. The gentle-to-aggressive thermal gradient matches the recipe. The `dar` at L4 matches the "return water" instruction. The `chcthy` (observe material moving) tokens appear at sublimation-relevant positions. The fire-strengthening zone (L9-10) has visibly higher qo-fire density. The overall arc -- gentle dissolution, return water, strengthen fire, observe sublimate, collect product -- is present in the token sequence.

**The weakness is still the same:** ch/sh readings are generic ("test: steady", "watch: steady") and you have to squint to distinguish "testing for rubification" from "testing for anything else." The system encodes THAT you test, not WHAT you test for. But for a process-control notation (not a descriptive recipe), that is arguably correct -- the operator knows what to look for; the notation tells them when to look.

**Score: 7/10.** Best of the four. Thermal arc visible, material-return encoded, sublimation observation present. Specificity still limited by ch/sh monotony.

---

## Folio 3: f81v -- Potable gold

**Recipe summary:** Dissolve gold in special water via balneum inhumation. Distill water off, gold stays dry at bottom. Distill lunaria until it stops burning. Cast gold into vegetable water. Rectify mercury. Mix all. Water of life.

### First 5 lines

**L1:** Bare tokens and unrecognized start -> `Watch: check` -> `Balneum: cycle complete` -> `Watch: heat until stable` -> `Place material` -> `Add new substance (dar)` -> `Hold` -> `Setup: steady` -> Watch -> `Load: secure material` -> unrecognized -> `Watch: set` -> `Output: iterate` -> `Steady: heat and hold`.

**Verdict:** Rough start with 2 unrecognized tokens. But the sequence dal -> dar (place material carefully, then add new substance vigorously) is EXACTLY what you do when dissolving gold: first you place the gold carefully in the vessel, then you add the dissolving water. The `keedy` (balneum cycle complete) at position 3 suggests the balneum is already set up. This reads as loading gold into a hot water bath and adding the special water. Operationally credible despite the noise.

**L2:** `Fire: standard heat cycle` -> `Vessel: extended sealed processing` -> `Heat: iterate, respond` -> `Vessel: stabilize` -> Scaffold -> `Steady: hold` -> `Heat: one cycle` -> `Steady: heat through one cycle` -> `Product settled` -> `Steady: hold` -> bare, bare.

**Verdict:** The `okaiin` (vessel: extended sealed processing through multiple cycles) is important. "Balneum inhumation" means burying the vessel in a sand/water bath for prolonged gentle heat. Extended sealed processing IS inhumation. The two bare tokens at the end are a flaw but the core reads well.

**L3:** `Scaffold: extended iteration` -> `Start new cycle (daiin)` -> `Steady: hold gentle heat balneum` -> `Vessel: confirm stable` -> `Adjust: one cycle` -> `Watch: steady, heat` -> `Test: check complete` -> `Load: bring to stable` -> `Steady: close`.

**Verdict:** Balneum work continues. The daiin (start new cycle) suggests the dissolution is iterative -- you check, wait, check again. This matches "balneum inhumation" which is a slow process requiring patience.

**L4:** `Fire: sustained deep cyclic heating` -> `Vessel: seal for cycle` -> `Test: gentle balneum level` -> `Cycle close` -> `Steady: hold` -> `Sustained deep heating` -> `Load: secure material` -> `Cycle close` -> `Start new cycle (daiin)` -> `Test: observe temperature directly`.

**Verdict:** Fire intensity ratchets up. Two `kaiin` (sustained deep heating) tokens plus the `qokaiin` make this the hottest line so far. The recipe says after dissolution, "distill water off" -- this requires stronger heat than the inhumation. The transition from gentle balneum (L2-L3) to aggressive heating (L4) matches.

**L5:** `Vessel: extended sealed processing` -> `Start new cycle (daiin)` -> `Output: monitor drip rate` -> `Test: observe temperature` -> `Vessel: maintain gentle balneum` -> `Fire: set` -> `Heat: note response` -> `Start new cycle (daiin)` -> `Vessel: note response`.

**Verdict:** Now we are distilling: `otain` (output: monitor drip rate) appears. The distillation is active with temperature checks. Multiple daiin tokens suggest iterative cycles of heating and checking. Consistent with distilling water off dissolved gold.

### Key moment: Gold dissolution in special water

The recipe's pivotal step is dissolving gold. I identified this as L1 (dal -> dar, place gold then add water) and L2-L3 (extended sealed balneum processing = inhumation). This is operationally convincing.

The second key moment is "distill lunaria until it stops burning." I'm looking for fire + output + a quality check.

**L10:** `Pause: hold, sequence` -> 1 unrecognized -> `Fire: pause` -> `Vessel: maintain balneum` -> `Output: verify drip steady` -> `Vessel: watch steady` -> `Fire: transfer complete` -> `Load: note result, finalize`.

The `qoty` (fire: transfer complete) followed by `dairam` (load: note result, finalize) reads as: stop the transfer, note what you got, close this step. "Distill lunaria until it stops burning" -- the `qoty` (transfer complete = stop) could encode the cessation of burning. Plausible but not specific.

### Nonsense sequences

**L8:** `ykol` (Adjust: hold state) -> `or` -> `Watch: steady` -> `Watch: gentle process` -> `Fire: hold` -> `Balneum: cycle complete` -> `Start new cycle` -> `dkain` (Heat: iterate, bind) -> **`cphedy`** (unrecognized) -> `Steady: close`.

The `dkain` compositional reading is suspect -- "heat: iterate, bind"? And `cphedy` breaks entirely. This is the weakest line I can find.

**L11:** `oshey` unrecognized at line start. Then clean work.

**L17:** 2 bare tokens at end (`dl`, `ral`). These are just unintelligible fragments.

### Contradictions

- **L6:** `aiin` (yield product to next cycle) appears mid-line between vessel and load operations. You are simultaneously yielding product and loading material? This reads as confused unless you interpret it as "pass this batch forward while preparing the next."

- **L13, L14:** Multiple `ytedy` (Transfer step: cycle close) tokens in sequence. Four of them appear in L12-L13. Is the scribe really encoding "transfer close, transfer close, transfer close, transfer close"? This looks like the dictionary giving the same reading to slightly different tokens rather than the scribe encoding repetition.

### Bottom line: f81v

**MIXED.** The opening dal -> dar sequence for gold dissolution is convincing. The balneum inhumation encoding (okaiin = extended sealed processing) is structurally appropriate. The thermal gradient (gentle balneum -> aggressive heating -> distillation with drip monitoring) matches the recipe arc. But the middle of the folio becomes repetitive and hard to follow. The `ytedy` repetitions are suspicious. The unrecognized tokens cluster more than in f79r. The recipe has more distinct operational phases (dissolution, distillation, lunaria distillation, gold casting, mercury rectification, mixing) than the folio seems to encode -- after L10 it reads as generic gentle-heat-and-monitor without clearly differentiating phases.

**Score: 5/10.** Opening is strong, middle and ending lose specificity. The multi-phase recipe outpaces the dictionary's ability to differentiate operations.

---

## Folio 4: f103r -- Ferment multiplication

**Recipe summary:** Combine two ferments in red water. Evaporate in balneum. Put on ashes. If not flowing, add air. Restore losses. Infinite multiplication.

### First 5 lines

**L1:** `Setup: bring to stable state` -> `Watch: complete` -> long compound -> `Output: steady` -> `Watch equipment: steady` -> `Fire: gentle transfer` -> `Fire: transfer until stabilized` -> `Watch: steady` -> `Watch: stable` -> `Load: secure material` -> `Vessel: hold state` -> `Place material (dal)` -> `Cycle close (dy)`.

**Verdict:** Setup, gentle transfer, load material, place material, close the cycle. Reads as combining the two ferments and placing them in the vessel. The dal (gentle placement) at the end fits "combine ferments in red water."

**L2:** `Load: secure material (dain)` -> Watch -> Test compound -> `Load: heat and hold` -> `Operate: run check` -> `hold state` -> `Test: steady, pause` -> `Note yield (ar)` -> `Output: adjust, watch` -> `Scaffold: hold` -> `Check furnace: balneum settling` -> `Scaffold: note and respond` -> `one pass (ain)` -> `Test: steady`.

**Verdict:** Loading, checking, noting the yield. The `lkeey` (check furnace: balneum settling) confirms balneum heat is active. The recipe says "evaporate in balneum" -- this is it. The `ar` (note yield) mid-line suggests checking on the evaporation progress.

**L3:** Watch -> `Watch: gentle balneum` -> `Test: transfer and hold` -> `Test: heat until stable` -> `Test: steady` -> `Test: observe temperature directly` -> `Note result` -> `Note: hold state` -> `Vessel: seal for cycle` -> `Test: stable` -> bare token -> `Heat: note response` -> `Test: finalize`.

**Verdict:** Heavy testing and temperature observation. The `okain` (vessel: seal for processing cycle) at token 9 suggests sealing before the next phase. The recipe says after balneum evaporation, "put on ashes" (a hotter, drier heat). The seal-before-transition reads correctly.

**L4:** `Test: steady confirmed` -> `Fire: standard heat cycle` -> `Vessel: confirm stable` -> `Fire: gentle steady heat` -> `Vessel: steady` -> `Test: note result` -> `Output: complete` -> `Test: note result` -> `Product settled (aly)`.

**Verdict:** Standard heating confirmed, vessel stable, product settling. This reads as the evaporation completing -- the material is dry. "Gold stays dry at bottom" from the balneum step. The `aly` (product settled: complete) at line end is clean.

**L5:** `Pause: note result` -> `Vessel: note result` -> `Watch: steady` -> `Output: gentle steady flow` -> `Fire: quick pulse` -> `Check equipment: note result` -> `Watch: gentle balneum` -> `Vessel: note result` -> `Watch: steady` -> `Heat: respond` -> `Output: bind` -> `Vessel: close`.

**Verdict:** Checking and noting results everywhere. The `oteey` (output: gentle steady flow at receiver) suggests something is flowing. The recipe says "if not flowing, add air" -- the presence of flow-monitoring tokens at exactly this position is appropriate. But I don't see the "add air" instruction specifically encoded. The next `dar` does not appear until L11.

### Key moment: Fusibility test ("if not flowing, add air")

The recipe's decision point: check if the material flows; if not, add air.

**L6:** `ocheey` (unrecognized) -> `Load: secure material` -> Watch -> `Vessel: maintain balneum` -> `Vessel: steady` -> `Watch: steady` -> `Fire: standard heat cycle` -> `Watch: observe material moving (shcthy)` -> `Fire: transfer operation` -> `Scaffold: bind` -> **`am: This phase is done`**.

The `shcthy` (watch: observe material moving) at token 8 is the fusibility check. You are watching whether the material flows. The line ends with `am` (phase done). This reads as: check if it flows, it does, phase complete.

**L11:** `dar: Add new substance` -> `Output: gentle flow` -> `Output: monitor drip rate` -> `Equipment steady` -> `Watch: steady` -> `Vessel: seal for cycle` -> `Test: check` -> `Fire: one cycle` -> `Watch: check` -> `Output: set up` -> `Fire: heat and hold` -> `Balneum: complete` -> `Load: iterate, heat, watch, heat`.

The `dar` at L11 position 1 is the first new material addition since L1. If the fusibility test at L6 showed incomplete flowing, L7-L10 would encode the "add air" intervention. The dar at L11 is "restore losses" from the recipe -- adding back what evaporated. The 10-line gap between L1 (combine ferments) and L11 (restore losses) is operationally reasonable for an evaporation process.

### Nonsense sequences

**L8:** This is BAD. 3 unrecognized tokens out of 14 (21%): `rain`, `adchey`, `ofcho`. Plus `lo` as a bare token. Only 71% recognized -- the worst line in all four folios. The recognized tokens are a mess: `Load: note result` -> `Vessel: steady` -> `Test: steady` -> `Vessel: steady` -> unrecognized -> `Vessel: steady, adjust, watch` -> `Fire: hold state` -> `Fire: transfer and note result` -> unrecognized -> unrecognized -> `Transfer step: set up, do` -> `Note: stable` -> `Balneum: adjust, watch, do` -> bare. The operational coherence is absent here.

**L16:** `Pause: hold state` -> `Watch: heat until stable` -> extended iteration -> `Test: gentle balneum` -> bare (`rar`) -> `Vessel: gentle balneum` -> compound with `fh` -> unrecognized (`opcheol`) -> `Output: gentle` -> `Transfer-check: steady` -> `Watch: stop adjusting`. Two gaps and a bare token. Below standard.

### Contradictions

- **L6 `am` (phase done)** at line 6 of a 54-line folio. If the phase is done at line 6, what are lines 7-54? This is the most damaging contradiction in all four folios. Either `am` does not mean "phase done" (in which case the dictionary is wrong) or the folio has multiple phases (in which case "phase done" just means "this sub-step is complete"). The latter interpretation is more charitable and matches the recipe structure (evaporate -> test -> restore -> multiply), but the gloss "This phase is done -- yield the result and close" oversells what is actually happening.

- **L49:** Multiple bare tokens (`lr`, `l`) interspersed with working tokens. The line reads as broken rather than intentional.

### Bottom line: f103r

**WEAKLY POSITIVE.** The opening (combine ferments, load, balneum) is credible. The fusibility observation at L6 (`shcthy` = watch material moving) is at the right position. The `dar` at L11 plausibly encodes "restore losses." But the middle section (L7-L10) is the weakest stretch in all four folios, with L8 at 71% recognized and no clear operational thread. The long gentle-heat tail (L35-54) is monotonous: `qokeey, qokeey, qokeey` (Fire: gentle steady heat) repeated with minor variations. The recipe says "infinite multiplication" happens here, but the tokens just say "keep heating gently" without encoding what multiplication means operationally.

The `am` (phase done) problem is real but not fatal -- it is a dictionary overstatement, not a folio structural problem. The `fchedy` (mercury marker) that appears in some of these lines would be structurally important if this recipe involves mercury, which it does not obviously do. That is either noise or evidence that the dictionary's mercury assignment (C1939) is too broad.

**Score: 4.5/10.** Weakest of the four. Opening works, fusibility test is there, but L8 is broken and the multiplication phase is encoded as featureless gentle heating.

---

## Cross-Folio Summary

### What v3 FIXED (relative to v2)

1. **`qoky` no longer reads as "cease heating."** Now it reads as "Fire: set -- stop adjusting, fire stays at current level." This is a real improvement. A scribe maintaining balneum temperature would constantly be setting the fire to hold, not ceasing heating. The v3 reading is operationally coherent.

2. **`e` as "steady" not "cool"** eliminates the false cooling signatures. `qokeey` = "Fire: gentle steady heat holding" instead of "Fire: cool cool end" makes the balneum passages readable instead of contradictory.

3. **Prefix labels are consistent.** `qo` always means "Fire:", `ok` always means "Vessel:", `ot` always means "Output:". You can scan a line and know the operational domain. This is a real readability improvement.

### What v3 STILL gets wrong

1. **ch/sh monotony is the primary weakness.** "Test: system steady" and "Watch: system steady" account for an absurd fraction of all readings. When every other token in a line says "test steady" or "watch steady," the reader cannot distinguish between:
   - Testing for rubification (red color)
   - Testing for blackening on silver plate
   - Testing for flow/fusibility
   - Testing temperature
   - Testing that the seal holds
   
   The dictionary says THAT you test. It never says WHAT you test. This is consistent with a process-control interpretation (the operator already knows what to test) but makes the cold-reading experience flat and unconvincing.

2. **Compositional readings for compound tokens are word salad.** `chcphdy` = "Test: adjust, pause, watch, do" and `chcphedy` = "Test: adjust, pause, watch, steady, do" differ by one "steady" in the middle. The atom-by-atom decomposition produces readings that are technically parseable but semantically empty. A medieval operator would not think "adjust, pause, watch, steady, do" -- they would think "the thing you do with the instrument at this point." The compositional system overdecomposes.

3. **The `ol` / `al` / `or` / `ar` bare tokens are overloaded.** `ol` = "Steady: hold as-is" appears 40+ times per folio. `ar` = "Note the yield" appears 10+ times. These are the highest-frequency tokens and their readings are so generic they function as punctuation, not instruction. If "hold as-is" is the most common instruction, then the system is encoding pauses, not operations. That may be correct (thermal processing IS mostly waiting) but it makes the reading experience repetitive.

4. **The Comp-v2 source readings are weaker than B Dict readings.** Whenever I see "Comp-v2" as the source, the reading tends to be longer and vaguer ("hold, adjust, watch, steady, do"). The B Dict D0/D1/D2 readings are crisper ("one standard heat cycle," "seal for a processing cycle"). The dictionary has two quality tiers and the seams show.

### The fundamental question: Pattern-matching or comprehension?

**It is pattern-matching that produces the correct operational SHAPE.** The v3 dictionary does not achieve comprehension in the sense of "I can read any line and tell you what the operator is doing." It achieves shape-matching in the sense of "the overall arc of fire intensity, material loading events, verification clusters, and product-settling markers matches the recipe structure."

The evidence for genuine encoding:
- **dar** (add substance) tokens appear at recipe-appropriate positions in all 4 folios
- **Thermal gradients** (gentle -> aggressive -> gentle) match recipe thermal arcs
- **dal** (place carefully) vs **dar** (add vigorously) distinction is operationally meaningful and used correctly
- **okaiin** (extended sealed processing) appears in inhumation/maceration contexts
- **fchedy** (mercury marker) appears on mercury-relevant folios
- **chcthy/shcthy** (observe material moving) appears at sublimation/fusibility test positions

The evidence against genuine comprehension:
- 80% of the token readings are "fire: steady," "test: steady," or "watch: steady"
- You cannot distinguish testing for color from testing for temperature from testing for flow
- Compound token readings are word salad
- L8 of f103r is broken
- The system cannot encode what multiplication, rubification, or the silver-plate test IS

**My verdict: The v3 dictionary achieves OPERATIONAL SHAPE RECOVERY at about 60% fidelity.** It correctly identifies the fire/vessel/output/test rhythm of thermal processing and places material-handling events at structurally appropriate positions. It does not achieve semantic comprehension of specific alchemical operations. The gap between shape and comprehension is the ch/sh monotony problem -- the system encodes "test here" but not "test for THIS."

This is better than random. It is not translation. It is the structural skeleton of the recipe with the operational flesh still missing.

### Scores

| Folio | Recipe | Score | Key strength | Key weakness |
|-------|--------|-------|-------------|-------------|
| f76r | Sevenfold distillation | 6/10 | al,al,dar at pass boundaries | Silver-plate test not specifically encoded |
| f79r | Mercury sublimation | 7/10 | Thermal arc matches, chcthy at sublimation | ch/sh readings monotonous |
| f81v | Potable gold | 5/10 | dal->dar for gold dissolution | ytedy repetitions suspicious, middle loses thread |
| f103r | Ferment multiplication | 4.5/10 | Fusibility test at correct position | L8 broken, multiplication = featureless heating |

**Overall v3 assessment: 5.6/10.** Improvement over v2 (the "cease heating" and "cool" problems are fixed), but the ch/sh monotony creates a new problem: everything sounds the same. The next dictionary version needs to differentiate what is being tested/watched, not just that testing/watching occurs.
