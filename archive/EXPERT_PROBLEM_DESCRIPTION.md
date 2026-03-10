# Problem Description: Line-Level Interpretation for the Voynich B Folio Reader

## For External Expert Consultation

---

## What This Project Is

We have built a structural analysis system for the Voynich Manuscript's Currier B text (23,243 tokens across 83 folios). The core finding (Tier 0, proven) is:

> The Voynich Manuscript's Currier B text encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

This means:
- 479 distinct token types reduce to **49 instruction classes** with 100% grammar coverage
- Each folio is a complete **program** (83 programs total, 75,248 instructions cataloged)
- Programs are organized into **paragraphs** (independent parallel sub-programs)
- Lines within paragraphs are **assessment-intervention cycles** in a control loop
- Three kernel operators (k=energy, h=phase management, e=stability) form the control core
- 17 specific transitions are absolutely forbidden (hazard topology)
- The Brunschwig alignment (Tier 3, conditional) maps this structure onto 15th-century distillation process control

We have a CLI tool (`show_b_folio.py`) that can display folios in several modes.

---

## What We've Built So Far

### 1. Program Card (`--profile`) -- WORKING WELL

A folio-level summary card showing deviation from the B-wide baseline (82 folios). Example:

```
======================================================================
PROGRAM CARD: f79r                                              [Tier 2]
======================================================================
  Section: B - "Bathing/Biology" | BIO
  Kernel: k=29.7% [~avg]  h=9.9% [-7pp z=1.2]  e=60.3% [+8pp z=0.9]
  Roles: EN +3pp z=0.6 | AX -4pp z=0.7 | CC 1.8x z=0.5
  REGIME: REGIME_1 (99%) (C494)
  Archetype: 2 - MODERATE_ATTRACTOR (C1016)

  STRUCTURAL PROFILE
  ----------------------------------------
  QO-lane:      30.1% [~avg]
  Sister ch:    44.2% [-17pp z=1.2]
  ol-morph:     24.9% [+12pp* z=2.0] (C1174)
  Forgiveness:  0.72 [+6pp z=0.5] (C1016)
  Haz density:  16.7% [-7pp z=1.0] (C622)

  VOCABULARY
  ----------------------------------------
  Bridge: 91.3% [+5pp z=1.0] | Dark: 6.2% [~avg]
  Unique MIDDLEs: 72 | Compound: 25.4% [-8pp z=1.2]
  AXM vocab: 38 | AXM residual: -3.1
======================================================================

  PARAGRAPH SUMMARY (C855: independent parallel programs)
  ============================================================
  PARA | G | KERNEL k/h/e%  | ROLE | SIZE      | T%
  ------------------------------------------------------------
  P1   | T | k25/h17/e58    | EN   | 3L/ 29T | 52%
  P2   | T | k42/h 8/e50    | EN   | 3L/ 34T | 23%
  P3   | P | k45/h16/e39    | EN   | 6L/ 51T | 26%
  ...
```

This works well. It characterizes the folio at the aggregate level with clear tier discipline.

### 2. Token-Level Glosses (default view) -- WORD SALAD

The default view shows each token with a "calculated" gloss:

```
TOKEN          | CALCULATED                          | MANUAL GLOSS
--------------------------------------------------------------------------------
[Line 1]
torain         | transfer mid[k]  [check]            | -
shedy          | monitor batch[e]                    | -
pchor          | chop portion                        | -
or             | portion                             | -
shek           | monitor exact[k]                    | -
otar           | scaffold release                    | -
pchdy          | chop seal[k]                        | -
opcholor       | [hold-heavy] [-or]                  | -
otal           | scaffold gather[k]                  | -
shedy          | monitor batch[e]                    | -
```

**The problem:** These glosses don't compose into anything coherent. "transfer mid, monitor batch, chop portion, portion, monitor exact, scaffold release, chop seal" reads as word salad. Each token gloss is a morphological decomposition dressed up as a procedure description, but strung together they don't form an understandable procedure.

### 3. Structural Mode (`--structural-mode`) -- PURE PARSE, NO INTERPRETATION

```
TOKEN          | STRUCTURAL
--------------------------------------------------------------------------------
[Line 1]
torain         | transfer r[k] (ain)
shedy          | monitor edy[e]
pchor          | chop or
or             | or
shek           | monitor ek[k]
otar           | scaffold ar
pchdy          | chop dy[k]
```

This is defensible but uninformative -- it just shows the morphological parse without interpretation.

### 4. Narrative View (`--narrative`) -- JUST SCRAPPED

We built and immediately scrapped a "narrative" mode that composed line-level descriptions from aggregate structural metrics:

```
  L1 [HEADER]  10T  mixed  e-dom  HT:1  FL>TERM
     Header line. Mixed-lane balance. Stability-kernel (e) heavy (60%).
     Reaches terminal FL state.
     > torain shedy pchor or shek otar pchdy opcholor otal shedy
```

**Why we scrapped it:** This was intellectually dishonest. It just reformatted the same aggregate statistics (role composition, kernel balance, lane distribution) into English sentences. The metrics tag line already said everything the narrative said. No actual decoding was happening -- it was painting pre-computed descriptions over the lines.

---

## The Problem

We need a line-level interpretation that:

1. **Actually decodes the line** -- derives meaning from the token sequence, not just aggregate statistics
2. **Is understandable** -- a reader can follow what the procedure is doing
3. **Is honest about its tier** -- doesn't pretend certainty it doesn't have

### What We Know About Lines

Each line is one **assessment-intervention cycle** in a control loop. But the interior of the line is **unordered** (C961: Kendall tau ~ 0). Tokens within a line are concurrent interventions, not sequential steps. You cannot read left-to-right as "do X, then Y, then Z."

There IS a positional template at the line level:
- **SETUP** zone: infrastructure tokens (da/sa prefixes), control loop markers
- **WORK** zone: operational tokens (qo, ch, sh, ok, ot, ol prefixes) -- this interior is unordered
- **CHECK/CLOSE** zone: late-position tokens (al, ar, or prefixes), FL state markers

### What Each Token Encodes (proven)

Every token decomposes into:

```
TOKEN = [ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX]

PREFIX  -> operation domain selector (WHAT you're acting on)
SISTER  -> operational mode (HOW carefully: precision vs tolerance)
MIDDLE  -> operation type (heating/cooling/monitoring)
SUFFIX  -> flow control marker (what happens AFTER)
```

PREFIX-MIDDLE combinations are grammatically constrained (102 forbidden combinations):

| PREFIX Class | Domain Target | Selects MIDDLE Family |
|--------------|---------------|----------------------|
| **qo-** | Energy source | k-family (heating, energy input) |
| **ch-/sh-** | The process itself | e-family (cooling, stabilization) |
| **da-/sa-** | Setup/configuration | infrastructure (iin, in, r, l) |
| **ot-/ol-** | Adjustment/continuation | h-family (phase monitoring) |
| **ok-** | Vessel/apparatus | e-family + infrastructure |

Sister pairs encode operational mode:
- **ch** = precision mode (tight tolerances, fewer escape routes)
- **sh** = tolerance mode (loose tolerances, more recovery options)

### What We Have for MIDDLE Glosses (Tier 3)

We have a dictionary of 340 glossed MIDDLEs (out of 1,339 total). These come from kernel correlation, section distribution, and REGIME clustering -- the Brunschwig alignment. Examples:

- **k** = "heat" (k-kernel, energy input)
- **e/ed/eed** = "cool/deep-cool" (e-kernel, stability)
- **ch/sh** = "monitor/check" (h-kernel, phase management)
- **t** = "transfer"
- **ol** = "store" (LINK operator, monitoring boundary)

### The FL (Flow-Level) State System

FL MIDDLEs genuinely track sequential state progression within each line:
- i/ii -> in -> r/ar -> al/l/ol -> o/ly/am -> m/dy/ry/y
- This gives "where are we in the process" information
- 5:1 forward:backward ratio; full state reset is forbidden

### Paragraph Context

Lines exist within paragraphs that have a proven spec-to-exec gradient (C932):
- Early body lines: rare vocabulary (specification -- setting up parameters)
- Late body lines: universal vocabulary (execution loop -- running the process)
- Header line: enriched compound tokens (identification/specification)

---

## What We Think Might Work (But Need Expert Input)

Our internal expert suggested a **channel-grouped control cycle view** that:

1. Groups tokens by PREFIX channel (not left-to-right order), respecting the unordered interior
2. Uses MIDDLE glosses from the dictionary (Tier 3, clearly marked)
3. Reports FL state as the one genuinely sequential progress marker
4. Characterizes control posture (precision/tolerance, heating/cooling)
5. Uses paragraph position to frame the cycle's role (spec vs exec)

Example of what this might look like:

```
LINE 5 [Body Q1 -- Specification zone]
  State: MEDIAL (FL: ar, r)
  Posture: PRECISION heating (ch dominant, k=0.45)

  Channels active:
    ENERGY:    sustained heat (qo:ke), transfer (qo:t)
    TESTING:   active check (ch:e.dy), precision cool (ch:eey)
    INFRA:     control loop (da:iin)

  Control: Loop active, no escape routes, precision mode
```

### Our Concern

We're worried this is still just another way of reformatting structural metadata into English rather than truly decoding what the line says. The question is: **is there a way to derive readable, meaningful procedure descriptions from the token-level information we have, or is the semantic ceiling genuinely impassable at the line level?**

---

## What We're Asking For

1. Is the channel-grouped approach the right direction, or is there a better way to compose token-level information into line-level meaning?
2. How do we avoid the trap of dressing up structural metrics as interpretation?
3. What would a genuinely decoded line look like, given our tier constraints?
4. Is there information in the token sequence we're not using that could bridge the gap to readability?
5. Should we accept that readable line-level interpretation requires commitment to the Brunschwig alignment (Tier 3), and if so, how do we frame that honestly?

---

## Technical References

- Token morphology: `scripts/voynich.py` (Morphology class, BTokenAnalysis)
- MIDDLE dictionary: `data/middle_dictionary.json` (340 glossed MIDDLEs)
- 49 instruction classes: proven grammar with 100% coverage
- Constraint system: 1,034 validated constraints (context/CLAIMS/)
- Structural contracts: context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml
- Speculative interpretations: context/SPECULATIVE/INTERPRETATION_SUMMARY.md
