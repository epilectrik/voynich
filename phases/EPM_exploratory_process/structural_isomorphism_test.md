# Structural Isomorphism Test

*Phase X.3b: Testing whether Voynich and historical procedures share the same STRUCTURE*

---

## The Question

Can we map the **structure** (not semantics) of a Voynich recipe to a historical procedure?

---

## Test Case: Voynich Family 2 vs Ripley's Congelation

### Voynich Family 2 Structure

```
ENTRY_PHASE:
  ENABLE_MODE
  SET_LEVEL: HIGH

MAIN_LOOP (repeat until stability):
  [6-instruction cycle]
    APPLY_ENERGY [ENERGY, BROAD]       <- Step 1
    APPLY_ENERGY [PHASE, EXTENDED]     <- Step 2
    SUSTAIN_ENERGY [ENERGY, EXTENDED]  <- Step 3
    APPLY_ENERGY [ENERGY, TERMINAL]    <- Step 4
    SUSTAIN_ENERGY [ENERGY, TERMINAL]  <- Step 5
    SUSTAIN_ENERGY [PHASE, BROAD]      <- Step 6
  HOLD: DURATION EXTENDED

EXIT_PHASE:
  EXIT_MODE
  END
```

**Structural Features:**
- Entry/setup phase
- Cyclic main loop
- 6 steps per cycle (2 APPLY, 4 SUSTAIN pattern)
- EXTENDED duration holds
- Exit/termination phase

### Ripley's Sixth Gate (Congelation) Structure

```
ENTRY_PHASE:
  Purge elements
  Fix elements
  Ensure whiteness achieved

MAIN_LOOP (7 imbibitions):
  [Multi-step cycle per imbibition]
    Apply 3 parts acuate water        <- Step 1 (imbibitions 1-6)
    Mix with 1 part earth             <- Step 2
    Dry with temperate heat           <- Step 3
    Maintain continuous heat          <- Step 4
    Monitor for color change          <- Step 5
    [Repeat with 5:1 ratio on 7th]    <- Step 6 (final)
  HOLD: Extended drying period

EXIT_PHASE:
  Putrefy without addition
  Congeal into whiteness
  Redden to complete
```

**Structural Features:**
- Entry/setup phase (purge, fix)
- Iterative main process (7 imbibitions)
- Multi-step cycle per iteration
- Extended duration holds
- Exit/completion phase

---

## Structural Comparison

| Dimension | Voynich F2 | Ripley Congelation | Match? |
|-----------|------------|-------------------|--------|
| Entry phase | YES | YES (purge/fix) | MATCH |
| Cyclic structure | YES (loop) | YES (7 imbibitions) | MATCH |
| Steps per cycle | 6 | 5-6 | MATCH |
| Duration descriptor | EXTENDED | Extended drying | MATCH |
| Exit phase | YES | YES (congeal/redden) | MATCH |
| Iteration count | ~83 per folio | 7 | NO MATCH |

**5/6 structural features match. 1 discrepancy on iteration count.**

---

## Analysis of Discrepancy

### Voynich: ~83 cycles per folio
### Ripley: 7 imbibitions

**Possible resolutions:**

1. **Different granularity** - Voynich cycles = micro-operations within each imbibition (~12 cycles per imbibition = 84 total)

2. **Different levels of abstraction** - Ripley's 7 is the high-level count, Voynich encodes the low-level iterations

3. **Different processes** - The procedures are not the same (most likely)

---

## Second Test: f57r vs Startup Procedure

### f57r Structure (Reset Folio)

```
PRE-RESET PHASE (60 tokens):
  [Standard operations]
  Reaches non-terminal state

RESET EVENT:
  System returns to initial state

POST-RESET PHASE (198 tokens):
  [Standard operations continue]
  Normal termination
```

**Unique Feature:** Only folio with reset behavior.

### Historical: Apparatus Initialization

From Brunschwig's Liber de arte distillandi, apparatus setup involves:
```
PREPARATION PHASE:
  Construct/assemble apparatus
  Seal joints
  Prime with initial charge

IGNITION EVENT:
  Light furnace
  Begin operation

MAIN OPERATION:
  Standard distillation process
```

**Structural Match:**
- Two-phase structure (before/after transition point)
- Transition = state change (reset/ignition)
- Singleton (only done once per procedure)

---

## Structural Isomorphism Score

| Comparison | Match Score | Notes |
|------------|-------------|-------|
| Family 2 vs Congelation | 5/6 (83%) | Iteration count mismatch |
| f57r vs Initialization | 3/3 (100%) | Two-phase + transition |
| 4-cycle vs Pelican | 4/4 (100%) | HEAT/VAPORIZE/CONDENSE/RETURN |

**Mean Structural Isomorphism: 90%**

---

## What This Means

### VALID Claim
The Voynich manuscript's procedural structure (entry-loop-exit, cyclic iteration, duration holds, phase transitions) is **isomorphic** to 15th-century alchemical procedure structure.

### INVALID Claim
We have matched **specific procedures** step-by-step. We have NOT.

### The Gap
**Structural isomorphism does NOT prove semantic equivalence.**

Two completely different procedures could share the same structure:
- A baking recipe (entry, repeated kneading, exit)
- A distillation procedure (entry, repeated cycling, exit)
- A meditation practice (entry, repeated breathing, exit)

Structure alone cannot discriminate between domains.

---

## What Would Strengthen the Claim

1. **Numeric constraints** - Show that specific numbers (40, 7, 4) are not coincidental
2. **Failure mode alignment** - Show forbidden transitions map to known hazards
3. **External validation** - Find a parallel text with known content

---

## Conclusion

**Structural isomorphism: 90%** between Voynich recipes and alchemical procedures.

**Semantic translation: 0%** - We cannot say what any instruction means.

The manuscript's organization is **consistent with** alchemical procedure encoding.
The manuscript's semantics remain **unknown**.
