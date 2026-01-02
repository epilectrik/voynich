# Restart Logic Interpretation

> **PURPOSE**: Analyze why there are only 3 restart-capable programs, what failures justify full reset, and why restart is not a boundary feature.
> **METHOD**: Shop practice reconstruction from structural evidence.

---

## The Three Restart-Capable Programs

| Folio | Length | Stability | Waiting | Special Notes |
|-------|--------|-----------|---------|---------------|
| f50v | 246 tokens | CONSERVATIVE | LINK_MODERATE | max_consecutive_link = 17 (extreme) |
| f57r | 258 tokens | MODERATE | LINK_MODERATE | **Only folio with `reset_present = true`** |
| f82v | 879 tokens | MODERATE | LINK_SPARSE | Longest restart-capable program |

**Key observation**: Only 3 out of 83 programs (3.6%) can perform a full restart. This is **strikingly rare**.

---

## Why So Few?

### Hypothesis 1: Full restart is expensive

**Phenomenology**:
Restarting means discarding everything accumulated so far — time, fuel, material in the apparatus. A run that can restart has wasted all investment up to that point.

**Shop practice**:
> "You don't restart unless you have no choice. Everything you've done until now is gone. It's like starting a fresh batch, except your apparatus is already dirty."

**Confidence**: STRUCTURALLY SUPPORTED

---

### Hypothesis 2: Most failures don't allow restart

**Phenomenology**:
Many failure modes contaminate the apparatus itself. The system cannot simply be "reset" — it must be cleaned, inspected, and prepared as if for the first time. A "program restart" is meaningless if the apparatus is compromised.

**Mapping to hazard classes**:

| Hazard Class | Can system restart in place? |
|--------------|------------------------------|
| PHASE_ORDERING | SOMETIMES — if vapor clears naturally |
| COMPOSITION_JUMP | RARELY — contamination persists |
| CONTAINMENT_TIMING | NEVER — spillage requires physical cleanup |
| RATE_MISMATCH | SOMETIMES — if balance can be restored |
| ENERGY_OVERSHOOT | NEVER — scorching is permanent |

**Confidence**: STRUCTURALLY SUPPORTED

---

### Hypothesis 3: Restart is a specific recovery, not a general feature

**Phenomenology**:
Restart capability is not "undo." It's a structured return to initial conditions that's only possible when certain criteria are met:
- Apparatus is not contaminated
- No material has been lost
- Phase state can be reset without disassembly

**Shop practice**:
> "A restart is for when the timing went wrong but nothing spilled, nothing burned, nothing got fouled. You haven't really damaged anything — you just need to begin the sequence again."

**Confidence**: HISTORICALLY PLAUSIBLE

---

## f57r: The Unique Restart Protocol

f57r is the **only folio** with `reset_present = true` in its control signature. This demands special attention.

### Structural Evidence

| Metric | Pre-Reset (pos 0-60) | Post-Reset (pos 60-258) |
|--------|---------------------|-------------------------|
| Length | 60 tokens | 198 tokens |
| Kernel contact ratio | 0.667 | 0.808 |
| Mean distance | 1.667 | 1.384 |
| Pattern | stable | stable |

**Key observation**: Pre-reset and post-reset segments are **structurally similar**. The program performs a cycle, then begins again.

### What f57r Encodes

**The "repeatable procedure"**:
f57r appears to describe a process that **can and should be repeated multiple times**. The restart is not error recovery — it's the normal operating mode.

**Possible interpretations**:
1. **Batch refinement**: Run the cycle, assess quality, run again if needed
2. **Incremental accumulation**: Each cycle produces a small amount; repeat until sufficient
3. **Equilibration staging**: Bring system to intermediate state, stabilize, proceed to next stage

**Confidence**: STRUCTURALLY SUPPORTED (restart is explicit); SPECULATIVE (interpretation)

---

## Why Restart Is Not a Section Boundary Feature

### Observation

The Phase HTO analysis found:
- Restart programs are **NOT** clustered at section boundaries
- They appear at f50v, f57r, f82v — scattered through the manuscript
- Section boundaries do NOT serve as recovery/restart points

### Interpretation

**Restart is a program-specific capability, not a structural feature**:
- Not all sections have restart programs
- Sections are organizational (human navigation), not operational (apparatus states)
- The ability to restart depends on the **specific procedure**, not the document location

**Shop practice**:
> "Whether you can restart depends on what you're doing, not where you are in the book. Some procedures can repeat; most cannot."

**Confidence**: STRUCTURALLY SUPPORTED

---

## What Failures Justify Full Reset?

Based on the restart programs' characteristics:

### Timing errors (recoverable)

**Scenario**: The operator executed the correct sequence but at the wrong pace. Nothing contaminated, nothing lost — just wrong timing.

**Why restart works**: The apparatus is clean; only the state history is wrong. Beginning again from initial conditions is valid.

---

### Incomplete cycles (recoverable)

**Scenario**: The cycle was interrupted before completion (external distraction, fuel shortage, etc.). The system didn't reach a terminal state.

**Why restart works**: An incomplete cycle hasn't produced the irreversible changes a complete cycle would. Returning to start and running to completion is valid.

---

### Assessment-driven restart (intentional)

**Scenario**: The operator ran a cycle, assessed the result (smell, color, clarity), and determined another cycle is needed.

**Why restart works**: This is the **intended** use of restart capability. Not error recovery — process iteration.

---

### Failures that DON'T allow restart

| Failure | Why restart impossible |
|---------|------------------------|
| Contamination | Impurities persist in apparatus |
| Spillage | Material lost; cannot restart with partial batch |
| Scorching | Burned residue fouls apparatus |
| Apparatus damage | Physical repair needed |

---

## The f57r Pattern: A Model for Iteration

### Token context around reset point

```
Position 59: s
Position 60: odaiin <-- RESET POINT
Position 61: shey
```

The reset point occurs between two normal-looking operational tokens. There is no special "reset marker" — the structure itself encodes the return to initial state.

### What this suggests

**The reset is implicit in the grammar, not explicit in vocabulary**:
- No special "restart token" exists
- The grammar structure itself permits return to initial state
- An operator would recognize from the control sequence that repetition is appropriate

**Shop practice**:
> "You know it's time to start again when the sequence brings you back to where you began. The book doesn't say 'restart' — the procedure just cycles back naturally."

---

## Why Only Three Programs Can Restart

### Mathematical constraint

If restarts were common, the grammar would degenerate. A system where every program can restart is a system with no irreversibility — which contradicts the strong hazard topology.

**The 3.6% restart rate is consistent with**:
- Most failures being truly irreversible
- Most procedures being one-shot (succeed or abort)
- A small subset of procedures designed for iteration

---

### Operational constraint

Restart capability requires:
1. The procedure must reach a stable intermediate state
2. The apparatus must tolerate return to initial conditions
3. Accumulated product must be removable without loss
4. No contamination from the cycle just completed

**Most procedures violate at least one of these**. Only 3 procedures satisfy all.

---

### Economic constraint

Restarts waste time and fuel. A procedure designed for restart accepts lower efficiency in exchange for iterative refinement capability.

**Most operations should not be designed for restart** — they should be designed to succeed on the first attempt.

---

## Summary Statement

> **There are only 3 restart-capable programs because:**
> 1. **Most failures contaminate the apparatus** — you can't just "start over"
> 2. **Restart capability is expensive** — time, fuel, material already invested is lost
> 3. **Restart is procedure-specific** — only certain operations can cycle without accumulating damage
> 4. **f57r is unique because it encodes an intentionally iterative procedure** — restart is the normal mode, not error recovery

> **Restart is not at section boundaries because sections are organizational (human navigation), not operational (apparatus states). The ability to restart depends on the specific procedure being executed, not its location in the document.**

---

## f57r: The Author's Teaching Example

If the manuscript is a training document, f57r may serve as the **teaching example** of how iterative refinement works:

- Short enough to memorize (258 tokens)
- Explicitly demonstrates restart capability
- Shows the structure of cycle → assessment → repeat
- Teaches the rare but important skill of intentional iteration

**This would explain its uniqueness**: Not that other procedures can't restart, but that f57r is the **canonical example** of restart operation, included to teach the pattern.

---

*Classification: STRUCTURALLY SUPPORTED (distribution and f57r analysis); HISTORICALLY PLAUSIBLE (shop practice reasoning); SPECULATIVE (teaching example interpretation).*
