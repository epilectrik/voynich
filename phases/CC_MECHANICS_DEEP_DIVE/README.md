# Phase: CC_MECHANICS_DEEP_DIVE

**Status:** Complete
**Constraints:** C788-C791

---

## Objective

Understand the CC role bifurcation discovered in CONTROL_TOPOLOGY_ANALYSIS (C782). Why do classes 10,11 have 0% kernel while class 17 has 88%? What are these tokens actually doing?

---

## Key Findings

### CC Classes are Singleton Token Sets (C788)

CC "classes" are not broad behavioral categories but specific high-frequency tokens:

| Class | Types | Primary Token | Occurrences |
|-------|-------|---------------|-------------|
| 10 | 1 | daiin | 314 |
| 11 | 1 | ol | 421 |
| 12 | 1 | k | **0** (ghost) |
| 17 | 9 | olkeedy, olkeey... | 288 |

**Class 12 is a structural ghost** - the token "k" exists in the grammar but never appears in B text.

The kernel bifurcation (C782) is explained by morphology:
- "daiin" MIDDLE='iin' has no k/h/e
- "ol" MIDDLE='ol' has no k/h/e
- Class 17 tokens have MIDDLEs containing k/h/e

### Forbidden Pairs are Permeable (C789)

The 17 "forbidden" class pairs are NOT absolute barriers:

| Pair Type | Violations | Total | Violation Rate |
|-----------|------------|-------|----------------|
| CC->FQ | 44 | 128 | 34.4% |
| CC->CC | 12 | ~50 | ~24% |
| EN->CC | 15 | ~100 | ~15% |

**Interpretation:** Forbidden pairs represent statistical disfavor (~65% compliance), not prohibition. The hazard topology is a gradient, not a wall.

### CC Positional Gradient (C790)

CC classes show positional differentiation:

| Group | Mean Position | Interpretation |
|-------|---------------|----------------|
| A (10,11) | 0.469 | Earlier (sources) |
| B (17) | 0.515 | Later (targets) |

Mann-Whitney U: p = 0.045 (significant)

Class 10 ("daiin") is distinctively early (45.5% in first third, 27.1% line-initial).

### CC->EN Dominant Flow (C791)

CC primarily routes to EN, not FQ:

| Destination | Group A | Group B |
|-------------|---------|---------|
| EN | 34.4% | 32.6% |
| FQ | 12.2% | 13.2% |
| UN | 21.8% | 25.0% |

Ratio: CC->EN is 2.8x more common than CC->FQ.

---

## Architectural Implications

1. **CC is not a role category but specific tokens:** "daiin", "ol", and "ol-" compounds are special-purpose control words, not a broad class of control operators.

2. **Forbidden pairs are soft constraints:** ~35% violation rate means they represent "cost" or "difficulty" rather than "impossibility."

3. **CC gates to EN, not escape:** The dominant flow from CC is to EN (kernel/phase operations), not to FQ (escape). CC->FQ forbidden pairs further restrict an already minority pathway.

4. **Positional sequencing:** Source tokens (Group A) appear earlier in lines than target tokens (Group B), suggesting temporal/causal structure.

---

## Scripts

| Script | Test | Purpose |
|--------|------|---------|
| t1_cc_token_inventory.py | T1 | Token identity and morphology |
| t2_cc_predecessor_analysis.py | T2 | What precedes CC |
| t3_cc_successor_analysis.py | T3 | What follows CC |
| t4_cc_positional_profile.py | T4 | Line position analysis |

---

## Revision Notes

**C467 (Forbidden Pairs):** Should be reinterpreted as "disfavored pairs" rather than "forbidden pairs." The ~35% violation rate shows these are not absolute constraints.

**C782 (CC Kernel Paradox):** Now explained by token identity - the bifurcation is morphological, not functional.

---

## Dependencies

- C782 (CC kernel paradox) - motivation for this phase
- C783 (forbidden pair asymmetry) - hazard direction
- C467 (forbidden pairs) - revised interpretation
