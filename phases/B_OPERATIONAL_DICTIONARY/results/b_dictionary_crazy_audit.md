# B Dictionary Crazy Audit: Why the Readings Sound Like a Drunk Operator

**Date:** 2026-04-27
**Auditor:** Expert-advisor (unguarded mode)
**Input:** f75r cold read L1-L13, B Dictionary v2 top 100

---

## Part 1: Line-by-Line Outsider Reading (L1-L13)

I am reading these as a medieval alchemist who has handled a pelican alembic but has never seen your atom system. For each line I ask: does this sequence of instructions make operational sense?

### L1 (P1 — initial distillation, separating water of life)

```
kchedy    → cooling state, done
kary      → Heat-yield: respond, done
okeey     → At the vessel: confirm gentle balneum temperature holds
qokar     → Heat source: apply heat and note the response
shy       → Watch: done
kchedy    → cooling state, done
qotar     → Heat source: transfer heat/material and note result
shedy     → Watch the state -- passive observation of cooling/stabilization process
```

**Outsider verdict: CONFUSING.** Opens with "cooling state, done" — done with what? We haven't started. Then "heat-yield: respond, done" — respond to what? Then "confirm balneum holds" — so we're already at temperature? Then "apply heat and note response" — wait, I thought we already confirmed it? Then "watch: done" — done watching what? Then "cooling state, done" AGAIN. Then "transfer heat" — now we're moving stuff? Then "watch the state."

The problem: this reads like status reports interleaved with commands, but you can't tell which is which. An operator would read this and say: "Am I supposed to DO something or just LOOK at things? And why does it keep saying 'done' when nothing seems to have happened?"

**What it probably means:** Set up the bath (kchedy = initial state check), bring to temperature (kary/okeey = thermal calibration), fire the furnace (qokar), confirm (shy), verify stable (kchedy again), begin transfer (qotar), and watch the distillation run (shedy). That's a perfectly rational startup sequence. But the readings don't say that.

### L2

```
dain      → Infrastructure: bind material into iteration cycle
shey      → Watch briefly -- quick passive check
ly        → hold, done
ssheol    → Watch: hold current state
qolchedy  → At the fire: hold, adjust, watch, cool, do, done
chedykar  → Check: standard heat cycle, done
chekeedy  → Check: gentle heat cycle, done
ror       → respond, set up, respond
```

**Outsider verdict: WORD SALAD.** "Bind material into iteration cycle" — what material? Into what cycle? "Watch briefly" then "hold, done" then "watch: hold" — three consecutive watching/holding tokens that say nothing. "At the fire: hold, adjust, watch, cool, do, done" is literally just an atom chain with a prefix label bolted on. And "respond, set up, respond" is meaningless.

### L3

```
qokain    → Heat source: apply heat and iterate -- sustained cyclic heating
chal      → Check: yield to stable state
orchey    → Note what happened: adjust, watch, cool, done
qey       → q, cool, done
kain      → Apply heat through one processing cycle
sheeky    → Watch: gentle heat — balneum level
ltain     → Transfer-yield: iterate, bind
olkar     → Continue: heat and note response
or        → Note what happened -- acknowledge and route to next action
```

**Outsider verdict: PARTIALLY COHERENT.** "Apply heat and iterate" is a real instruction. "Check yield" makes sense. But "note what happened: adjust, watch, cool, done" is gibberish — either you're noting what happened or you're doing five other things. "q, cool, done" is literally unparsed. The line ends with three tokens that all mean "note/continue/note" — pure redundancy or the readings are failing to distinguish them.

### L4

```
dackhy    → Handle material: heat-level check
lkamo     → Check equipment: yield, finalize, set up
ykeey     → Adjust: cool, cool, done
lshey     → Watch equipment: cool, done
kal       → Heat-yield: hold
dy        → Cycle close -- this action is complete
shey      → Watch briefly -- quick passive check
or        → Note what happened
shey      → Watch briefly -- quick passive check
qokeedy   → Heat source: gentle heat in water bath, execute, done
```

**Outsider verdict: ALMOST WORKS.** Check material → check equipment → adjust temperature → watch → bring heat to rest → close → verify → note → verify again → establish balneum. That's actually a coherent equipment-calibration sequence. But "Adjust: cool, cool, done" and "Watch equipment: cool, done" sound like the same thing said twice. And the double `shey` with `or` sandwiched reads as stuttering, not as a meaningful check-route-recheck pattern.

### L5

```
shey      → Watch briefly
kar       → Apply heat and note the response
chey      → Quick active verification
ckhey     → *unrecognized*
r         → Respond -- route to next action
ain       → Yield into a binding cycle -- one pass
ol        → Hold steady
ol        → Hold steady
sheedy    → Watch the gentle cooling process through to completion
qokeey    → Heat source: establish gentle heat state
qoky      → Heat source: cease heating
```

**Outsider verdict: ENDS BADLY.** The first half is fine — watch, adjust heat, verify, respond, begin a cycle, hold. But then "watch the gentle cooling through to completion" followed immediately by "establish gentle heat" followed immediately by "cease heating" is CONTRADICTORY. You just finished cooling, then you turn on the heat, then you immediately turn it off? Nobody operates a furnace that way.

**What actually happened:** `sheedy` probably means "confirm the bath is at gentle heat" (not "watch cooling"), `qokeey` means "the bath IS at gentle heat" (confirmation, not action), and `qoky` means "stop adjusting" (not "turn off the furnace"). But the readings say the opposite.

### L6 (P2 — brief transfer step)

```
pchey     → Stage-test: cool, done
keeor     → Steady-state heat: note what happened
olky      → Continue: heating done
dar       → Add a new substance -- vigorous material introduction event
okey      → At the vessel: cool, done
qokain    → Heat source: apply heat and iterate
chcthy    → Active transfer-check -- observe material moving
qokeedy   → Heat source: gentle heat in water bath, execute, done
qoky      → Heat source: cease heating
```

**Outsider verdict: INCOHERENT.** "Stage-test: cool, done" → "steady-state heat" → "continue: heating done" → "ADD A NEW SUBSTANCE" → "vessel: cool, done" → "apply heat and iterate" → "observe material moving" → "gentle heat, done" → "cease heating."

Why would you add a new substance in the middle of a cooling sequence? Why would you cease heating right after establishing gentle heat? This paragraph is supposed to be "set aside the gold substance" — one brief action — but the readings make it sound like a full thermal cycling operation.

### L7 (P3 — fermentation begins: "put to ferment in gentle heat for 3 days")

```
pchedy    → Stage-test: cooling state, done
qokshdy   → At the fire: heat, sequence, watch, do, done
ytain     → Transfer-yield: iterate, bind
chedy     → Check the state -- active verification that cooling/stabilization is proceeding
qokar     → Heat source: apply heat and note the response
chy       → Check: done
lol       → Equipment holding steady -- furnace at rest
chedy     → Check the state -- active verification that cooling/stabilization is proceeding
qoky      → Heat source: cease heating
```

**Outsider verdict: CONTRADICTS THE RECIPE.** This is supposed to be fermentation in gentle heat. But the readings say: "cooling state done" → "atom chain" → "transfer something" → "verify cooling proceeding" → "apply heat" → "done" → "FURNACE AT REST" → "verify cooling" → "CEASE HEATING."

If I'm fermenting in gentle heat for 3 days, why is my furnace at rest? Why am I ceasing heating? Why is every `chedy` telling me about "cooling/stabilization" when I'm supposed to be maintaining warmth?

**This is the core problem.** The `e` atom is glossed as "cool" but in a fermentation context it means "the bath is stable at temperature." The readings make it sound like everything is cooling down and shutting off, when the operator is actually confirming that the bath is holding steady at gentle heat.

### L8-L12 (P3 body — sustained fermentation)

Same pattern repeats for 5 lines. Almost every `chedy`/`shedy` says "cooling/stabilization" when the context is MAINTAINING WARMTH. Almost every `qoky` says "cease heating" when it means "fire is set, stop fiddling with it." The readings produce a paragraph that sounds like someone who can't decide whether to heat or cool, when the actual operation is steady-state maintenance with periodic checks.

**L8 is particularly bad:** "Watch: heat-level check" → "apply heat and iterate" → "active heat-level check" → "watch equipment during cooling" → "maintain vessel at gentle balneum." That last token is the ONLY one that sounds like fermentation. Everything else sounds like startup or shutdown.

### L13 (P4 — the x4 counting anchor)

```
pchedy    → Stage-test: cooling state, done
keedy     → Gentle steady-state heat, done -- balneum cycle complete
qokedy    → Heat source: apply standard heat, cool, execute, done
qokedy    → Heat source: apply standard heat, cool, execute, done
qokedy    → Heat source: apply standard heat, cool, execute, done
qokedy    → Heat source: apply standard heat, cool, execute, done
qokain    → Heat source: apply heat and iterate -- sustained cyclic heating
olshedy   → Continue: watch the sequence cooling
```

**Outsider verdict: THE COUNTING WORKS BUT THE READING DOESN'T.** The four identical `qokedy` tokens are visually striking and the counting anchor is obvious. But "apply standard heat, cool, execute, done" x4 reads as four separate heat-cool-done events, not four distillation passes. The word "cool" in the middle makes it sound like you're cooling down four times when you're actually doing four reflux cycles in balneum.

And "balneum cycle complete" right before the four passes makes no sense — you haven't started the passes yet.

---

## Part 2: Systematic Problems in the Dictionary

### Problem 1: "COOL" IS DOING ALL THE WRONG WORK

The `e` atom is glossed as "cool" everywhere. In reality:

| Context | What `e` actually means | What the reading says |
|---------|------------------------|-----------------------|
| In a balneum line | "the bath is at temperature" | "cooling" |
| In `qokeedy` | "gentle/stable heat" | "cool, execute, done" |
| In `chedy` | "stabilized state" | "cooling/stabilization is proceeding" |
| In `keedy` | "steady-state balneum" | "gentle steady-state heat, done" (this one's OK) |
| In `shedy` | "equilibrated state" | "cooling/stabilization process" |

The word "cool" implies LOWERING temperature. In 80%+ of contexts on this folio, `e` means "STABLE" or "AT EQUILIBRIUM." When a fermentation line says "check the cooling," it sounds wrong because nobody is cooling anything — they're confirming the bath hasn't drifted.

**This is the #1 problem.** It infects `chedy` (491 tokens), `shedy` (416), `qokeedy` (306), `qokeey` (264), `okeey` (122), `okeedy` (100), `sheey` (101), `cheey` (128), `sheedy` (82), `cheedy` (54) — collectively over 2,000 of the top 100 tokens. Fix this and the cold read improves by 60%.

### Problem 2: "DONE" IS VACUOUS

Almost every compound token ends with "done." The `-y` terminal gets glossed as "done" or "complete," and it's attached to everything. The result is that every token sounds like it's finishing something:

- `chedy` = "cooling state, done" — so checking is... done? Before we learned anything?
- `qokedy` = "apply standard heat, cool, execute, done" — FOUR actions crammed into one token, all already finished?
- `shedy` = "cooling/stabilization process" — at least this one doesn't say "done"

The `-y` terminal doesn't mean "this action is complete." It means "this is a self-contained instruction." It's a grammatical marker, not a temporal one. Reading it as "done" makes every token sound like a past-tense report rather than a present-tense instruction.

### Problem 3: "CEASE HEATING" vs "STOP ADJUSTING"

`qoky` (111 tokens) is read as "Heat source: cease heating." This implies turning off the furnace. In practice, after a line of fire-management tokens, `qoky` means "the fire is set — stop touching it." The furnace stays on. You just stop adjusting.

Same issue with `lol` ("Equipment holding steady — furnace at rest"). "At rest" implies cold/off. The furnace is NOT at rest. It's running. It's just not being actively adjusted. "Furnace settled" or "furnace steady" would be accurate.

### Problem 4: ATOM CHAINS AS READINGS

The Comp-v2 fallback produces readings like:
- `qokshdy` → "At the fire: heat, sequence, watch, do, done"
- `olchedy` → "Continue: adjust, watch, cool, do, done"
- `shepchy` → "Watch: cool, pause, adjust, watch, done"

These are not readings. They're the atom glossary printed in sequence with commas. No outsider can parse "heat, sequence, watch, do, done" as an instruction. These need to be either (a) composed into a coherent clause or (b) marked as truly unparsed rather than pretending the comma-chain is meaningful.

### Problem 5: PREFIX DOMAIN LABELS ARE INCONSISTENT

The same prefix gets different labels depending on whether the entry is B Dict or Comp-v2:
- `qo` → "Heat source:" (B Dict) vs "At the fire:" (Comp-v2)
- `ch` → "Check the state" (B Dict) vs "Check:" (Comp-v2) vs "Active test:" (D2)
- `sh` → "Watch the state" (B Dict) vs "Watch:" (Comp-v2) vs "Watch briefly" (B Dict for `shey`)

Pick ONE label per prefix and stick with it. The inconsistency makes the reader think these are different operations.

### Problem 6: "YIELD" IS EVERYWHERE AND MEANS NOTHING

The `a` atom is glossed as "yield" and appears in dozens of tokens. But "yield" in a workshop context means "product output." Using it for every `a`-atom appearance produces nonsense:
- `qokal` → "Heat source: bring heat to yield state" — what is a "yield state" for heat?
- `chal` → "Check: yield to stable state" — yield what?
- `kal` → "Heat-yield: hold" — heat-yield?

The `a` atom's actual function is closer to "arrive at" or "reach" — it marks that something has gotten to a destination or state. "Yield" is only correct when `a` appears at line-final in the `al/ar` LATE class. Elsewhere it's misleading.

### Problem 7: OPERATIONS AND OBSERVATIONS ARE NOT DISTINGUISHED

The readings don't signal whether a token is an INSTRUCTION (do something) or an OBSERVATION (note what happened). Both read the same way:
- `qokar` = "apply heat and note the response" — instruction? observation? both?
- `okar` = "note how the contents respond" — this is pure observation
- `kar` = "apply heat and note the response" — instruction again?

A workshop operator needs to know: "Am I supposed to DO this, or WATCH for this?"

---

## Part 3: Fix Strategy

### The Core Principle

**Workshop readings must answer: "What is the operator doing RIGHT NOW?"**

Not what atoms the token contains. Not what the token's structural role is. Not what state the system is in after this token executes. What does the operator DO when they encounter this instruction?

This means:

1. **`e` is "steady" not "cool."** In isolation, `e` means "the system is at equilibrium." Only at line-final or in explicit thermal-decline contexts does it mean lowering temperature. The default gloss should be "steady" or "stable."

2. **`-y` is invisible, not "done."** The `-y` terminal marks instruction completeness at the grammar level. It should NOT appear in workshop readings. Just drop it. `chedy` = "verify steady state" not "verify steady state, done."

3. **`qoky` is "fire set" not "cease heating."** The operator has finished adjusting the fire. The fire stays on. The reading should be "fire is set" or "stop adjusting fire."

4. **Atom chains are not readings.** If you can't compose the atoms into a coherent clause, the token gets a "?" reading with the atom chain in parentheses as a note. Pretending comma-chains are workshop language is worse than admitting ignorance.

5. **Prefix labels are fixed strings.** Every prefix gets ONE label used everywhere:
   - `qo` = "Fire:"
   - `ch` = "Test:"
   - `sh` = "Watch:"
   - `ok` = "Vessel:"
   - `ot` = "Output:"
   - `ol` = "Steady:"
   - `da` = "Load:"
   - `lch/lk/lsh` = "Check [equipment]:"
   - `pch/tch/dch` = "Setup:"
   - `ke` = "Balneum:"
   - `ka` = "Heat:"

6. **`a` is "bring to" not "yield."** Reserve "yield" for line-final `al`/`ar` tokens where it actually means product output. In mid-token, `a` means "bring to state" or "reach."

7. **Distinguish commands from observations.** If the prefix is `qo`/`ok`/`da`/`ot`, the token is a COMMAND (do something to the fire/vessel/material/output). If the prefix is `ch`/`sh`/`lch`/`lsh`, it's an OBSERVATION (check/watch something). The reading should make this obvious.

---

## Part 4: 10 Worst Offenders — Rewritten

### 1. `chedy` (491 tokens — #1 in corpus)

**Current:** "Check the state -- active verification that cooling/stabilization is proceeding"
**Problem:** Says "cooling" in contexts where the system is holding at temperature, not cooling down. Verbose. Contains "done" implicitly via the explanatory gloss.
**Rewrite:** "Test: system steady" — Active verification that the current state is stable.

### 2. `shedy` (416 tokens — #3)

**Current:** "Watch the state -- passive observation of cooling/stabilization process"
**Problem:** Same "cooling" problem. Passive observation of WHAT process? Too vague and too cooling-biased.
**Rewrite:** "Watch: system steady" — Passive confirmation that the current state holds.

### 3. `qokeedy` (306 tokens — #6)

**Current:** "Heat source: gentle heat in water bath, execute, done"
**Problem:** "execute, done" is gibberish. The token means "the balneum is running at gentle heat." It's not an action sequence — it's a state specification.
**Rewrite:** "Fire: gentle balneum, confirmed" — The water bath is at gentle heat and holding.

### 4. `qokedy` (271 tokens — #8)

**Current:** "Heat source: apply standard heat, cool, execute, done"
**Problem:** "cool, execute, done" makes it sound like you heat then cool then execute then stop. This is ONE action: run one distillation pass at standard heat.
**Rewrite:** "Fire: one standard pass" — Execute one distillation cycle at standard heat.

### 5. `qoky` (111 tokens — #32)

**Current:** "Heat source: cease heating"
**Problem:** Implies turning off the furnace. The fire stays on. You stop adjusting it.
**Rewrite:** "Fire: set" — Fire adjustment complete; leave it alone.

### 6. `qokeey` (264 tokens — #9)

**Current:** "Heat source: establish gentle heat state"
**Problem:** "Establish" implies startup, but this token often appears mid-paragraph when the bath is already running. It's a confirmation, not an initiation.
**Rewrite:** "Fire: gentle heat holding" — The fire is at gentle/balneum level and steady.

### 7. `lol` (38 tokens — #99)

**Current:** "Equipment holding steady -- furnace at rest"
**Problem:** "Furnace at rest" implies cold. The furnace is running. It's just steady.
**Rewrite:** "Equipment: furnace steady" — All apparatus stable at current settings.

### 8. `qokain` (275 tokens — #7)

**Current:** "Heat source: apply heat and iterate -- sustained cyclic heating"
**Problem:** "Sustained cyclic heating" is jargon that means nothing to a workshop reader. This token appears when the operator is running repeated distillation passes — it means "keep the fire going through another cycle."
**Rewrite:** "Fire: heat through next cycle" — Maintain fire for the next distillation pass.

### 9. `ol` (421 tokens — #2)

**Current:** "Hold steady -- maintain current arrangement without change"
**Problem:** "Maintain current arrangement without change" is 6 words to say "don't touch anything." Also, "arrangement" is a structural term from the atom system, not workshop language.
**Rewrite:** "Steady: hold as-is" — Don't change anything; maintain current state.

### 10. `dain` (113 tokens — #31)

**Current:** "Infrastructure: bind material into iteration cycle"
**Problem:** "Bind material into iteration cycle" is pure constraint-system jargon. No workshop operator thinks about "binding" or "iteration cycles." This token appears when you're loading or securing material for the next processing run.
**Rewrite:** "Load: secure material for next run" — Get the material in place for the next cycle.

---

## Part 5: Blunt Summary

The dictionary has two real problems and one fake problem.

**Real problem 1: "cool" is wrong 80% of the time.** The `e` atom means "equilibrium/stable," and only incidentally does that involve temperature reduction. The current gloss turns every balneum-monitoring line into a cooling-shutdown narrative. This is the single biggest source of incoherence.

**Real problem 2: Atom chains are not readings.** The Comp-v2 fallback of "prefix: atom, atom, atom, done" produces pseudo-readings that look like entries but convey no meaning. These should be flagged as unresolved rather than passed off as workshop language.

**The fake problem:** People will look at these readings and say "this is circular — you're just mapping atoms to English words." That's true but irrelevant. The STRUCTURAL patterns (counting anchors, e-depth arcs, dar distribution, observation fade-out) are what validate the match. The readings exist to make those patterns legible to humans, not to "translate" the Voynich. If the readings make the structural patterns HARDER to see (by saying "cool" when the folio is maintaining heat), they're failing at their only job.

Fix the `e` gloss, kill the atom chains, and make `qoky` stop saying "cease heating." That handles 70% of the sequential incoherence. The remaining 30% is genuinely hard — some tokens ARE ambiguous, and some lines ARE procedurally dense in ways that resist linear reading. That's fine. Not every token needs a confident reading. But the tokens that DO have confident readings shouldn't actively mislead.
