# B Dictionary Workshop Reading Audit

**Date:** 2026-04-27
**Source:** v2 dictionary (`b_dictionary_top100_v2.md`) cross-checked against f75r cold read
**Problem:** The `e` atom (LOCKED gloss: cool/stabilize) is rendered as "cooling" in many workshop readings where "stabilizing" or "settled" is the operationally correct sense. This produces contradictory or nonsensical sequences when tokens appear on lines adjacent to active heating operations.

**Scope:** The atom glosses are LOCKED. This audit revises only how the compound workshop reading phrases the combination for human comprehension. No structural claims are changed.

---

## Core Diagnosis

The `e` atom has two valid senses within its LOCKED gloss:

| Sense | When it applies | Example context |
|-------|----------------|-----------------|
| **Cooling** | Active temperature reduction, receiving condensate | `oteedy` (receiver collecting cooled distillate) |
| **Stabilizing** | System reaching or maintaining steady state | `chedy` (verifying system is in steady state) |

The v2 dictionary defaults to "cooling" in nearly every compound. This is wrong roughly half the time. When `e` follows `k` (heat), it almost always means "stabilize the heat" not "cool after heating." When `e` appears in a check/watch context (`ch-`, `sh-`), it means "verify stability" not "verify cooling."

The same problem affects `l` (hold/late). "At rest" implies OFF. Equipment maintaining gentle heat is not "at rest" -- it is "settled" or "holding steady."

And `-y` (done/end) compounds: "cease heating" (`qoky`) implies turning off the fire entirely, when the operational sense is "stop adjusting the fire" (the fire continues at its current level).

---

## Entries Requiring Revision

### Category 1: "cooling" should be "stabilizing" or "steady state"

| # | Token | Current Reading | Proposed Reading | Reasoning |
|---|-------|----------------|------------------|-----------|
| 1 | chedy | Check the state -- active verification that cooling/stabilization is proceeding | Verify stable -- active check that the system is in steady state | On heat-management lines (f75r L7, L15, L22, L28-L33), nobody is checking for cooling. They are checking that the system has settled. The slash "cooling/stabilization" hedges but readers see "cooling" first. |
| 3 | shedy | Watch the state -- passive observation of cooling/stabilization process | Watch for steady -- passive observation that conditions are holding | Same problem as chedy. On f75r L12, L32-L35, this token sits between `qokar` (apply heat) and `qokain` (sustained heating). "Watching cooling" between two heating tokens is contradictory. "Watching for steady" is not. |
| 8 | qokedy | Heat source: apply standard heat, cool, execute, done | At the fire: one standard heat cycle, done | "apply standard heat, cool, execute, done" is word salad -- 5 concepts in 8 words. A heat cycle inherently includes stabilization. The x4 counting anchor (L13) reads as "one cycle, one cycle, one cycle, one cycle" which is exactly what the recipe says. |
| 19 | otedy | Transfer rate: check the drip/flow rate during cooling | Transfer check: verify the drip rate is steady | The drip rate is being checked for stability, not checked "during cooling." On f75r L44-L45, this appears between active heat management tokens. |
| 25 | cheey | Active test: verify gentle cooling is proceeding | Verify gentle steady state -- confirm balneum holds | On f75r L12, this sits between `ol` (hold steady) tokens. The operator is confirming the water bath is stable, not that it is cooling down. |
| 28 | lchedy | Check equipment state during cooling | Check equipment: confirm apparatus is stable | Equipment checks happen during operation, not just during cooling. On f75r L10, L25, L33, this appears mid-operation. |
| 29 | okedy | Vessel management: check vessel during cooling | At the vessel: confirm contents are stable | Same pattern -- vessel checks during active operation, not specifically during cooling. |
| 37 | sheey | Watch for gentle cooling -- passive balneum observation | Watch for gentle steady -- passive balneum observation | The balneum is being observed for stability, not for cooling. |
| 42 | oteey | Monitor output: confirm gentle cooling at the receiver | Monitor output: confirm gentle steady flow at receiver | At the receiver end, you want steady flow, not cooling per se. |
| 45 | oteedy | Monitor output: gentle cooling at the receiver, done | Monitor output: gentle steady state at receiver, done | Same as oteey. |
| 46 | cheol | Active test: check cooling and hold steady | Verify and hold -- confirm state, maintain it | "Check cooling and hold steady" contradicts itself (cooling is change, holding steady is not). Should be: verify the state, then maintain it. |
| 48 | sheedy | Watch the gentle cooling process through to completion | Watch the gentle process through to completion | "Gentle cooling process" implies deliberate cooling. In balneum context (f75r L16, L40), the operator watches the gentle HEAT process. Removing "cooling" fixes it. |
| 65 | cheedy | Active test: verify gentle cooling proceeds correctly | Verify gentle steady state proceeds correctly | Same pattern as cheey, with -dy completion marker. |
| 70 | cheody | Active test: check what was set up during cooling | Verify what was arranged, done | "During cooling" is an assumption. The -o- means arrangement (C1388). |
| 72 | opchedy | Operate: run the active check procedure during cooling | Operate: run the active check procedure | "During cooling" is unnecessary qualifier that creates contradictions. |
| 86 | lchey | Quick equipment check during cooling | Quick equipment check -- confirm apparatus state | "During cooling" again assumes cooling is happening. |
| 91 | lshedy | Watch equipment state during cooling | Watch equipment: confirm apparatus is steady | Equipment observation during operation, not specifically during cooling. |
| 98 | qokchedy | At the fire: heat with active test during cooling, done | At the fire: heat with active check, done | "Heat during cooling" is a direct contradiction. The operator heats, then checks the system is stable. |

### Category 2: "at rest" or "cease" should be "settled" or "stop adjusting"

| # | Token | Current Reading | Proposed Reading | Reasoning |
|---|-------|----------------|------------------|-----------|
| 32 | qoky | Heat source: cease heating | At the fire: done adjusting -- fire set at current level | "Cease heating" implies turning off the fire. In f75r L5, L12, L15, L19, this appears at the END of heat-management sequences. The fire continues; the operator stops fiddling with it. Same on f75r L41 mid-balneum -- you do not turn off the fire during reflux. |
| 41 | okal | At the vessel: bring contents to rest | At the vessel: contents settling -- let them stabilize | "Bring to rest" implies stopping all activity. "Settling" means the contents are reaching equilibrium. |
| 75 | oky | At the vessel: operation done -- close or remove from apparatus | At the vessel: done -- seal or set aside | "Close or remove from apparatus" is too specific. "Seal or set aside" covers the actual operational range. |
| 99 | lol | Equipment holding steady -- furnace at rest | Equipment settled -- furnace holding at current level | "Furnace at rest" implies no fire. On f75r L7 (fermentation paragraph), the furnace maintains gentle heat. On L28, same context. On L37 (mid-x9 cycle), the furnace is absolutely not at rest -- it is settled at balneum temperature. |

### Category 3: "cool, execute, done" word salad in qo-prefix compounds

| # | Token | Current Reading | Proposed Reading | Reasoning |
|---|-------|----------------|------------------|-----------|
| 6 | qokeedy | Heat source: gentle heat in water bath, execute, done | At the fire: one gentle balneum cycle, done | "Gentle heat in water bath, execute, done" is 9 words of word salad. This is the most common balneum token on f75r. "One gentle balneum cycle, done" is clear and under 12 words. |
| 9 | qokeey | Heat source: establish gentle heat state | At the fire: bring to gentle steady heat | "Establish gentle heat state" is bureaucratic. "Bring to gentle steady heat" is what the operator does. |
| 38 | okeedy | Vessel management: maintain vessel at gentle balneum temperature | At the vessel: maintain gentle balneum level | Cleaner. "Vessel management" is a category label, not a workshop instruction. |
| 47 | qokey | At the fire: apply heat with brief cooling -- one thermal pulse | At the fire: one quick heat-and-settle pulse | "Brief cooling" after "apply heat" sounds contradictory. A thermal pulse heats then lets the system settle. |

### Category 4: Miscellaneous readability problems

| # | Token | Current Reading | Proposed Reading | Reasoning |
|---|-------|----------------|------------------|-----------|
| 16 | al | The product is at rest -- yield has reached stable state | Product settled -- yield has reached stable state | "At rest" implies inert/finished. "Settled" means it has stabilized and can be assessed. |
| 18 | qokal | Heat source: bring heat to yield state -- heat until stable | At the fire: heat until the yield stabilizes | "Bring heat to yield state" is confusing -- does "yield state" mean "the state that yields product" or "the state of the yield"? Rephrased for clarity. |
| 68 | keedy | Gentle steady-state heat, done -- balneum cycle complete | Gentle steady heat, done -- balneum cycle complete | "Steady-state" is a technical compound adjective that reads awkwardly. "Steady heat" is simpler. |
| 87 | kedy | Standard heat cycle, done -- heating operation complete | Standard heat cycle, done | "Heating operation complete" is redundant after "done." |
| 92 | lkeedy | Check furnace at gentle balneum temperature | Check furnace: gentle balneum level holds | Adding "holds" conveys the check is for stability, not just temperature measurement. |
| 93 | olkeedy | Hold gentle heat steady -- maintain balneum level | Hold gentle heat -- maintain balneum level | "Hold steady" is redundant with "maintain." Pick one. |
| 94 | lkeey | Furnace at gentle heat -- confirm balneum level holds | Check furnace: balneum level settling | "Furnace at gentle heat" is a state description, not an instruction. Adding "check" makes it actionable. |
| 100 | olkeey | Hold gentle heat -- maintain balneum level | Hold gentle heat -- balneum level steady | Minor. "Maintain balneum level" sounds like an instruction to do something; "balneum level steady" confirms the state. |

---

## Entries Flagged by User but Fine As-Is

| # | Token | Current Reading | Verdict |
|---|-------|----------------|---------|
| 26 | okeey | At the vessel: confirm gentle balneum temperature holds | **GOOD** -- User noted this one works. The word "holds" conveys stability, not cooling. Keep. |
| 2 | ol | Hold steady -- maintain current arrangement without change | **GOOD** -- "Hold steady" is the right sense. No cooling implication. |
| 33 | dy | Cycle close -- this action is complete | **GOOD** -- Clean, no ambiguity. |
| 15 | dar | Add a new substance -- vigorous material introduction event | **GOOD** -- Clear operational action. |
| 5 | daiin | Start a new cycle -- initiate the next heating-monitoring loop | **GOOD** -- Clear, no cooling confusion. |
| 63 | am | This phase is done -- yield the result and close | **GOOD** -- Paragraph terminator, no ambiguity. |

---

## Summary Statistics

| Category | Count |
|----------|-------|
| "cooling" -> "stabilizing/steady" | 18 entries |
| "at rest/cease" -> "settled/done adjusting" | 4 entries |
| Word salad / clarity | 4 entries |
| Miscellaneous readability | 8 entries |
| **Total entries needing revision** | **34 of 100** |
| Entries confirmed fine | 6 flagged, all OK |

---

## Design Principle for Future Readings

When composing workshop readings for `e`-containing compounds:

1. **If the token is in a ch/sh (check/watch) context:** Use "stable" or "steady," not "cooling." The operator is verifying state, not verifying a temperature decrease.

2. **If `e` follows `k` within a MIDDLE:** Use "steady heat" or "settle," not "cool." `ke` = heat that has stabilized, not heat followed by cooling.

3. **If the token has `-dy` (done) suffix after `e`:** The system has reached steady state and the check/operation is complete. Do not say "cooling done" -- say "stable, done" or just "done."

4. **For `qoky` and similar `-y` completions at the fire:** "Done adjusting" not "cease." The fire continues; the operator stops intervening.

5. **For equipment tokens (`l-` prefix):** "Settled" or "holding at current level," never "at rest." Equipment maintains state; it does not stop.

6. **General rule:** If the proposed reading would sound contradictory when placed between two `qokain` (sustained heating) tokens on the same line, the reading is wrong. Revise until it reads naturally in a heat-management sequence.
