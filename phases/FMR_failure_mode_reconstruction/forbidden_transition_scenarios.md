# Forbidden Transition Scenarios

> **PURPOSE**: For each of the 17 forbidden transitions, propose a plausible real-world failure scenario.
> **METHOD**: Phenomenological reconstruction from state-pair incompatibility.

---

## Understanding Forbidden Transitions

Each forbidden transition represents a pair of system states that **cannot be entered in sequence**. The grammar forbids A→B AND B→A, indicating **mutual exclusions** — these states are fundamentally incompatible neighbors.

---

## PHASE_ORDERING Failures (7 Transitions)

*"Material in the wrong form at the wrong time."*

---

### 1. shey → aiin (and reverse)

#### Scenario
**"Vapor trapped in liquid pathway"**

The operator allows vapor-phase material to enter a section designed for liquid handling. The vapor condenses unpredictably, forming droplets in locations where drainage is impossible. The liquid accumulates, blocks normal flow, and creates a "vapor lock" — the system cannot clear itself.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Insufficient cooling before routing to liquid section |
| **Why irreversible** | Condensate in wrong location cannot be drained without disassembly |
| **Recovery** | Stop, cool completely, drain accumulated liquid, restart |
| **Severity** | HIGH |
| **Likelihood** | MODERATE — common mistake for impatient operators |
| **Economic impact** | Batch loss + time to clear apparatus |

**Confidence**: STRUCTURALLY SUPPORTED

---

### 2. shey → al (and reverse)

#### Scenario
**"Hot vapor meets cold surface too suddenly"**

Material transitioning between vapor and liquid phases meets an incompatible temperature gradient. Instead of orderly condensation, the material "flashes" — some condensing, some remaining vapor — creating an unstable two-phase mixture in a section designed for single-phase handling.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Failure to equilibrate temperatures before transition |
| **Why irreversible** | Two-phase mixture cannot separate in confined space |
| **Recovery** | Flush section, re-establish temperature gradient, restart |
| **Severity** | MEDIUM-HIGH |
| **Likelihood** | MODERATE — especially during startup |
| **Economic impact** | Partial batch loss, significant time delay |

**Confidence**: STRUCTURALLY SUPPORTED

---

### 3. shey → c (and reverse)

#### Scenario
**"Premature condensation before collection ready"**

Vapor begins condensing before the receiving vessel is properly prepared — perhaps still holding residue from previous operation, or at wrong temperature. The fresh condensate mixes with inappropriate material, compromising purity.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Rushing the sequence, not verifying vessel state |
| **Why irreversible** | Fresh product contaminated with residue |
| **Recovery** | Cannot recover this fraction; must segregate as lower grade |
| **Severity** | MEDIUM |
| **Likelihood** | HIGH — very common mistake |
| **Economic impact** | Product downgraded, not lost |

**Confidence**: STRUCTURALLY SUPPORTED

---

### 4. dy → aiin (and reverse)

#### Scenario
**"Dense material driven into light-material pathway"**

A heavier fraction (dy-state) is pushed into a section designed for lighter fractions. The dense material cannot rise or circulate properly, settling where it shouldn't, blocking pathways, and corrupting the separation gradient.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Excessive pressure or improper timing |
| **Why irreversible** | Heavy material deposited in inaccessible locations |
| **Recovery** | Complete flush and restart required |
| **Severity** | HIGH |
| **Likelihood** | LOW — requires significant operator error |
| **Economic impact** | Full batch loss, extensive cleaning |

**Confidence**: HISTORICALLY PLAUSIBLE

---

### 5. dy → chey (and reverse)

#### Scenario
**"Wrong phase sequence for volatile capture"**

The operator attempts to transition directly between states that require an intermediate step. The volatile components escape before capture, lost to the atmosphere. What remains is depleted of the most valuable fraction.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Skipping required equilibration step |
| **Why irreversible** | Volatiles lost cannot be recovered |
| **Recovery** | Batch depleted; may continue with degraded quality |
| **Severity** | MEDIUM-HIGH |
| **Likelihood** | MODERATE — impatience-driven mistake |
| **Economic impact** | Reduced yield, quality diminished |

**Confidence**: STRUCTURALLY SUPPORTED

---

### 6. chey → chedy (and reverse)

#### Scenario
**"Vapor pathway collapse"**

The vapor channel becomes flooded with condensate before the system is ready for liquid-phase operation. The return path for reflux becomes blocked. Circulation halts.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Cooling applied before heating stabilized |
| **Why irreversible** | Flooded pathway requires physical clearing |
| **Recovery** | Stop, drain, re-establish vapor-liquid equilibrium |
| **Severity** | HIGH |
| **Likelihood** | MODERATE — startup and shutdown vulnerable |
| **Economic impact** | Time loss, potential batch contamination |

**Confidence**: HISTORICALLY PLAUSIBLE

---

### 7. chey → shedy (and reverse)

#### Scenario
**"Phase inversion in reflux zone"**

What should be returning as controlled condensate instead remains as vapor, or vice versa. The reflux ratio — the balance of material returning versus proceeding — is destroyed. Separation efficiency collapses.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Temperature gradient disrupted |
| **Why irreversible** | Separation gradient must be rebuilt from scratch |
| **Recovery** | Extended stabilization period or restart |
| **Severity** | MEDIUM |
| **Likelihood** | HIGH — sensitive to environmental changes |
| **Economic impact** | Time loss, reduced separation quality |

**Confidence**: STRUCTURALLY SUPPORTED

---

## COMPOSITION_JUMP Failures (4 Transitions)

*"Contamination from skipping steps."*

---

### 8. chedy → ee (and reverse)

#### Scenario
**"Unfinished fraction passed as complete"**

Material that hasn't finished its purification cycle is allowed to proceed as if it were clean. Impurities that should have been separated are carried forward, permanently contaminating the output.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Impatience, misreading system state |
| **Why irreversible** | Impurities now mixed with product cannot be separated |
| **Recovery** | Batch permanently downgraded |
| **Severity** | MEDIUM |
| **Likelihood** | HIGH — temptation to rush |
| **Economic impact** | Quality loss, not quantity loss |

**Confidence**: STRUCTURALLY SUPPORTED

---

### 9. c → ee (and reverse)

#### Scenario
**"Vessel contamination carried forward"**

Material from one operational state is introduced to another without proper transition procedures. Residue from previous state contaminates new material.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Inadequate clearing between operations |
| **Why irreversible** | Cross-contamination cannot be undone |
| **Recovery** | Segregate contaminated fraction |
| **Severity** | MEDIUM |
| **Likelihood** | MODERATE — procedural error |
| **Economic impact** | Fraction loss, cleaning required |

**Confidence**: STRUCTURALLY SUPPORTED

---

### 10. shedy → aiin (and reverse)

#### Scenario
**"Late-stage material routed to early-stage pathway"**

Material that has undergone partial processing is accidentally returned to the beginning of the process. The "recycled" material is incompatible with fresh feed, corrupting both.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Valve/routing error |
| **Why irreversible** | Mixed streams cannot be separated |
| **Recovery** | Full system flush, restart with fresh feed |
| **Severity** | HIGH |
| **Likelihood** | LOW — requires significant routing error |
| **Economic impact** | Major batch loss |

**Confidence**: HISTORICALLY PLAUSIBLE

---

### 11. shedy → o (and reverse)

#### Scenario
**"Impure fraction reaches output"**

Material carrying impurities reaches a point where it cannot be recalled. The output is contaminated. If the output is a collected product, it's now degraded.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Monitoring failure, rushing collection |
| **Why irreversible** | Collected product cannot be uncollected |
| **Recovery** | Must discard or downgrade collected fraction |
| **Severity** | HIGH |
| **Likelihood** | MODERATE — especially near end of run |
| **Economic impact** | Product loss or severe quality reduction |

**Confidence**: STRUCTURALLY SUPPORTED

---

## CONTAINMENT_TIMING Failures (4 Transitions)

*"Apparatus in wrong state for the operation."*

---

### 12. chol → r (and reverse)

#### Scenario
**"Vessel opened while pressurized"**

The operator attempts to access or vent a vessel that still contains pressure. Material escapes violently — possibly causing injury, certainly causing product loss.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Impatience, failure to verify pressure state |
| **Why irreversible** | Escaped material cannot be recovered |
| **Recovery** | Clean up, restart if material remains |
| **Severity** | HIGH (safety hazard) |
| **Likelihood** | LOW — usually obvious danger |
| **Economic impact** | Product loss, potential apparatus damage |

**Confidence**: STRUCTURALLY SUPPORTED

---

### 13. l → chol (and reverse)

#### Scenario
**"Liquid routed into vapor-only section"**

Liquid material enters a section designed only for vapor handling. The liquid cannot drain properly, accumulates, and eventually blocks the vapor pathway. The "wrong material in wrong place" pattern.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Valve error, timing mistake |
| **Why irreversible** | Liquid pooled in vapor sections requires disassembly |
| **Recovery** | Stop, drain, possibly disassemble for cleaning |
| **Severity** | MEDIUM-HIGH |
| **Likelihood** | MODERATE — common with complex apparatus |
| **Economic impact** | Time loss, potential batch contamination |

**Confidence**: HISTORICALLY PLAUSIBLE

---

### 14. or → dal (and reverse)

#### Scenario
**"Overflow from improper drainage timing"**

Material accumulates in a vessel faster than it can drain. The vessel overflows, losing product and potentially contaminating surrounding areas.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Flow rate mismatch, blocked drain |
| **Why irreversible** | Spilled material cannot be recovered |
| **Recovery** | Clean, verify drainage, restart |
| **Severity** | MEDIUM |
| **Likelihood** | HIGH — common operational failure |
| **Economic impact** | Product loss, cleanup time |

**Confidence**: STRUCTURALLY SUPPORTED

---

### 15. he → or (and reverse)

#### Scenario
**"Heat applied to full vessel"**

The operator applies heat to a vessel that hasn't been properly drained or is still receiving material. Thermal expansion causes overflow or, worse, pressure buildup with no escape path.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Sequence error, vessel not verified empty |
| **Why irreversible** | Thermal expansion damage, spillage |
| **Recovery** | Stop heat, allow cooling, drain, restart |
| **Severity** | HIGH (safety hazard) |
| **Likelihood** | MODERATE — especially during complex operations |
| **Economic impact** | Product loss, potential apparatus damage |

**Confidence**: STRUCTURALLY SUPPORTED

---

## RATE_MISMATCH Failure (1 Transition)

*"Flow balance destroyed."*

---

### 16. ar → dal (and reverse)

#### Scenario
**"Surge overwhelms drainage capacity"**

A sudden increase in flow rate from one section exceeds the drainage capacity of the receiving section. Material backs up, potentially reversing flow, creating chaotic circulation patterns.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Abrupt change in heating, blocking downstream |
| **Why irreversible** | Flow distribution chaotic, separation destroyed |
| **Recovery** | Allow system to stabilize, restart separation |
| **Severity** | MEDIUM |
| **Likelihood** | MODERATE — especially with variable heat sources |
| **Economic impact** | Time loss, reduced separation efficiency |

**Confidence**: STRUCTURALLY SUPPORTED

---

## ENERGY_OVERSHOOT Failure (1 Transition)

*"Heat applied carelessly."*

---

### 17. he → t (and reverse)

#### Scenario
**"Bumping from excessive heat"**

Heat is applied too rapidly. The liquid superheats, then releases energy violently — "bumping." Material is thrown upward, contaminating vapor pathways, potentially escaping the apparatus entirely.

| Attribute | Assessment |
|-----------|------------|
| **Cause** | Too much fire, too fast |
| **Why irreversible** | Splattered material contaminates entire apparatus |
| **Recovery** | Complete apparatus cleaning, restart |
| **Severity** | VERY HIGH (safety + quality) |
| **Likelihood** | LOW — obvious mistake, but catastrophic |
| **Economic impact** | Full batch loss, extensive cleaning |

**Confidence**: STRUCTURALLY SUPPORTED

---

## Summary Statistics

| Severity | Count | Transitions |
|----------|-------|-------------|
| VERY HIGH | 1 | he→t |
| HIGH | 7 | shey→aiin, dy→aiin, chey→chedy, shedy→aiin, shedy→o, chol→r, he→or |
| MEDIUM-HIGH | 3 | shey→al, dy→chey, l→chol |
| MEDIUM | 6 | shey→c, chey→shedy, chedy→ee, c→ee, or→dal, ar→dal |

---

## Pattern Summary

### The Dominant Fear Patterns

1. **Phase state errors** dominate — material in wrong physical form at wrong time
2. **Contamination from impatience** — rushing past incomplete separation
3. **Apparatus physical limits** — overflow, pressure, thermal events
4. **All failures are bidirectional** — the incompatibility works in both directions

### The Operator's Constant Vigilance

| Must Watch For | Associated Failures |
|----------------|---------------------|
| Unexpected droplets, condensation | PHASE_ORDERING (7 transitions) |
| Color changes, cloudiness, off-smells | COMPOSITION_JUMP (4 transitions) |
| Overflow sounds, hissing, gurgling | CONTAINMENT_TIMING (4 transitions) |
| Surging, flooding, dry sections | RATE_MISMATCH (1 transition) |
| Bumping, scorching smell, temperature spikes | ENERGY_OVERSHOOT (1 transition) |

---

*All scenarios: STRUCTURALLY SUPPORTED from grammar structure; HISTORICALLY PLAUSIBLE for 15th-century circulation apparatus.*
