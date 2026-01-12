# External Corroboration Protocol

**Tier:** 3 | **Status:** READY FOR DEPLOYMENT | **Date:** 2026-01-10

> **Purpose:** Test ECR findings against external practitioner knowledge without corrupting the frozen model.

---

## Core Principles

1. **No manuscript exposure** — Experts never see tokens, glyphs, or transcriptions
2. **No leading** — Questions describe patterns, not conclusions
3. **Falsifiable** — Wrong answers are possible and informative
4. **Bounded** — Answers cannot backflow into token semantics

---

## Administration Requirements

- Questions should be asked by someone unfamiliar with VMS research
- Respondents should have no prior exposure to Voynich hypotheses
- Responses must be recorded verbatim before scoring
- Ideal respondents:
  - Historical perfumers
  - Traditional distillers
  - Pharmaceutical historians
  - Alchemical recreationists
  - Material scientists with historical craft experience

---

## Question Set A: Hazard Topology

*For practitioners of historical distillation, aromatic extraction, or pharmaceutical compounding*

### A-1: Hazard Distribution

> "In your experience with [craft], what causes batches to fail? Roughly, what percentage of failures come from:
> - Wrong sequence of operations
> - Unwanted separation or recombination of components
> - Timing of containment (opening/closing vessels)
> - Rate mismatches (too fast/slow)
> - Energy overshoot (overheating)
>
> Does one or two of these dominate?"

**Testing:** Does real-world hazard topology match PHASE_ORDERING (41%) + COMPOSITION_JUMP (24%) dominance?

| Response | Score |
|----------|-------|
| Phase/sequence and composition errors dominate | PASS |
| Mixed distribution | PARTIAL |
| Energy overshoot dominates, or evenly distributed | FAIL |

---

### A-2: Reversibility Profile

> "When something goes wrong, how often can you recover the batch versus having to discard and restart?"

**Testing:** The 89% reversibility signature in the frozen model.

| Response | Score |
|----------|-------|
| High reversibility (>70%) | PASS |
| Medium reversibility (40-70%) | PARTIAL |
| Low reversibility (<40%) | FAIL |

---

## Question Set B: Decision Archetypes

*For practitioners with hands-on experience*

### B-1: Judgment Moments

> "Walk me through a typical operation. At what points do you have to make a judgment call that can't be written down as a fixed rule? What are you looking at when you decide?"

**Testing:** Do real decision points map to our 12 archetypes (D1-D12)?

| Response | Score |
|----------|-------|
| Clusters around phase transitions, composition assessment, timing calls, recovery decisions | PASS |
| Mixed types | PARTIAL |
| Primarily about quantities, temperatures, or named ingredients | FAIL |

---

### B-2: Attention vs. Execution

> "Is there a difference between 'paying attention to something' and 'doing something about it'? Can you give an example where you're watching but not acting?"

**Testing:** The HT/B-layer distinction (attention vs. execution).

| Response | Score |
|----------|-------|
| Clear separation — monitoring without intervention is a recognized mode | PASS |
| Some distinction acknowledged | PARTIAL |
| All attention leads immediately to action; no watching-without-acting | FAIL |

---

### B-3: Context Shifts

> "Does the same operation feel different at the beginning versus the middle versus near the end? Do you watch for different things?"

**Testing:** AZC-layer context encoding; section conditioning (C232).

| Response | Score |
|----------|-------|
| Same actions require different discrimination depending on phase of overall process | PASS |
| Some context-dependence | PARTIAL |
| Operations are context-independent; same rules throughout | FAIL |

---

## Question Set C: Material Behavior

*For material scientists or experienced practitioners*

### C-1: Classification Axes

> "If you had to sort the materials you work with into categories based on how they *behave* during processing — not what they are — what dimensions would you use?"

**Testing:** Does phase-mobility x composition-distinctness emerge naturally?

| Response | Score |
|----------|-------|
| Mentions volatility/stability AND purity/mixture as primary axes | PASS |
| Mentions one axis | PARTIAL |
| Classification by source, color, cost, or other non-behavioral axes | FAIL |

---

### C-2: Class Count

> "How many fundamentally different *types* of behavior do you deal with? Not specific materials — behavior types."

**Testing:** The 3-5 class range from ECR-1.

| Response | Score |
|----------|-------|
| 3-6 range; reluctance to give exact number | PASS |
| 2 or 7-9 | PARTIAL |
| Confident exact answer (especially 1-2 or 10+) | FAIL |

---

## Question Set D: Apparatus Roles

*For historians of technology or instrument makers*

### D-1: Functional Roles

> "In a complete [distillation/extraction] setup, what distinct *functions* do the different pieces serve? Not the parts themselves — the jobs they do."

**Testing:** ECR-2 apparatus roles (4-7 functional categories).

| Response | Score |
|----------|-------|
| Maps to energy-source, phase-container, separator, circulation, collector, anchor | PASS |
| 2-3 or 8+ functional categories | PARTIAL |
| Purely anatomical (names of vessels) without functional abstraction | FAIL |

---

### D-2: Interchangeability

> "Can different physical apparatus serve the same function? Can the same apparatus serve different functions in different setups?"

**Testing:** Role abstraction — apparatus roles are functional, not physical.

| Response | Score |
|----------|-------|
| Yes to both — function and form are separable | PASS |
| Yes to one | PARTIAL |
| Both no — rigid one-to-one mapping | FAIL |

---

## Scoring Matrix

| Question | Tests | Pass Condition | Fail Condition |
|----------|-------|----------------|----------------|
| A-1 | Hazard topology | Phase/composition dominant | Energy/rate dominant |
| A-2 | Reversibility | High (>70%) | Low (<40%) |
| B-1 | Decision archetypes | Phase/composition/timing | Quantities/names |
| B-2 | HT/B distinction | Clear separation | No distinction |
| B-3 | Section conditioning | Strong context effects | Context-independent |
| C-1 | Classification axes | Mobility x composition | Non-behavioral |
| C-2 | Class count | 3-6, uncertain | 1 or 10+ |
| D-1 | Apparatus roles | 4-7 abstract roles | Names only |
| D-2 | Role abstraction | Both yes | Both no |

---

## Interpretation Thresholds

| Score | Interpretation |
|-------|----------------|
| 7-9 PASS | Strong corroboration — ECR findings align with practitioner knowledge |
| 5-6 PASS | Moderate corroboration — general alignment with some gaps |
| 4 PASS | Weak corroboration — requires model review |
| <4 PASS | Model revision needed — ECR findings may not reflect actual craft |

---

## What This Protocol Does NOT Do

- **Does not prove** the manuscript is about distillation
- **Does not identify** specific substances or apparatus
- **Does not decode** any tokens
- **Does not contaminate** the frozen constraint system

It tests whether the **structural patterns** we've identified are consistent with real-world craft knowledge.

---

## Expert Validation

Expert review (2026-01-10) confirmed:

> "This is one of the best-designed external corroboration protocols I've seen. [...] You are not asking 'Does this remind you of medieval perfumery?' You are asking 'Does your lived knowledge satisfy these structural constraints?' That's the correct reversal of authority."

---

## Navigation

← [TIERS.md](TIERS.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
