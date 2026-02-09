# Human Communication Model

**Tier:** 4 (Exploratory)
**Status:** SPECULATIVE - subject to falsification
**Created:** 2026-01-22
**Depends on:** C103-C105, C121, C366, C382, C397, C458, C466-C467

---

## 0. Framing Principle

> **"Currier B never encodes preparation steps. It encodes control envelopes. Externally, we can observe that these envelopes are compatible with materials which, in practice, require preparation before entering the loop."**
>
> *— Validated 2026-01-22, see `phases/INTEGRATED_PROCESS_TEST/FRAMING_CORRECTION.md`*

### What This Document Describes

This model describes how a **trained human operator** could interpret B's structural features as operational guidance. B does not encode instructions in natural language. Rather, B's grammar creates patterns that a knowledgeable operator can map to actions.

**Analogy:** A musical score doesn't tell you "press this key" - it encodes pitch, duration, and dynamics. A trained musician interprets these into physical actions. Similarly, B encodes control structure; a trained operator interprets this into procedural actions.

---

## 1. Communication Hierarchy

B communicates at four levels, from most specific to most general:

| Level | What B Encodes | Human Interprets As | Grounding |
|-------|---------------|---------------------|-----------|
| **Kernel** | Control primitives | Direct action verbs | C103-C105 |
| **Role** | Instruction classes | Action type families | C121, C382 |
| **Mode** | Participation style | Intensity/caution | C466-C467, C408 |
| **Envelope** | Overall regime | Strategic stance | C179-C185, C458 |

---

## 2. Kernel Operators (Direct Control)

The kernel operators are B's most direct control primitives. Human mapping is well-grounded.

### 2.1 k - ENERGY_MODULATOR (C103)

**Structural function:** Energy level modulation
**Human interpretation:** "Adjust heat/energy input"

| Pattern | Human Guidance |
|---------|---------------|
| k appears | Energy adjustment point |
| k density high | Active energy management phase |
| k near hazard | Energy-sensitive transition |

**Constraint basis:** C103 defines k as ENERGY_MODULATOR. C089 establishes kernel set {k, h, e}.

### 2.2 h - PHASE_MANAGER (C104)

**Structural function:** Phase transition management
**Human interpretation:** "Watch for phase change / critical transition"

| Pattern | Human Guidance |
|---------|---------------|
| h appears | Phase boundary - observe carefully |
| h clusters | Multiple transition points |
| h → LINK | "Check status after phase change" |

**Constraint basis:** C104 defines h as PHASE_MANAGER. C107 establishes kernel operators are hazard-adjacent.

### 2.3 e - STABILITY_ANCHOR (C105)

**Structural function:** Recovery and stability reference
**Human interpretation:** "This is your safe state / fallback position"

| Pattern | Human Guidance |
|---------|---------------|
| e appears | Safe reference point available |
| e density high | Rich recovery options |
| e after hazard | "Return here if trouble" |

**Constraint basis:** C105 defines e as STABILITY_ANCHOR. C105 shows 54.7% of recovery paths pass through e.

---

## 3. Role Categories (Action Types)

The 49 instruction classes (C121) compress into 7 role categories. Human mappings are inferred from structural function.

### 3.1 ENERGY_OPERATOR (6 classes)

**Structural function:** Energy-related operations
**Human interpretation:** "Actions affecting heat/energy state"

**Constraint basis:** C121, C394 (Aggressive regimes show 1.34x ENERGY_OPERATOR)

### 3.2 AUXILIARY (8 classes)

**Structural function:** Infrastructure support, kernel access mediation
**Human interpretation:** "Setup, support, or preparatory action within the loop"

| Pattern | Human Guidance |
|---------|---------------|
| High AUXILIARY | Operation requires setup/support |
| AUXILIARY → LINK | "Prepare, then verify" |

**Constraint basis:** C396 (AUXILIARY Invariance at 8.5-9.0%), C396.a (execution-critical infrastructure)

**Important:** AUXILIARY refers to support operations WITHIN the control loop, not material preparation BEFORE entering the loop (per C171).

### 3.3 FLOW_OPERATOR (7 classes)

**Structural function:** Flow and transfer control
**Human interpretation:** "Manage material/vapor movement"

| Pattern | Human Guidance |
|---------|---------------|
| High FLOW | Active transfer/movement phase |
| FLOW density | Attention to flow dynamics |

**Constraint basis:** C121, C366 (FLOW_OPERATOR precedes LINK at 1.30x)

**Brunschwig correlation:** FLOW maps to da-prefix at r=0.9757, p=0.0243

### 3.4 HIGH_IMPACT (5 classes)

**Structural function:** Significant state changes
**Human interpretation:** "Major intervention required"

| Pattern | Human Guidance |
|---------|---------------|
| HIGH_IMPACT appears | Significant action point |
| HIGH_IMPACT clusters | Critical operation sequence |

**Constraint basis:** C394 (Conservative regimes show 2.0x HIGH_IMPACT), C402 (HIGH_IMPACT Clustering)

### 3.5 CORE_CONTROL (4 classes)

**Structural function:** Central control operations
**Human interpretation:** "Primary control action"

**Constraint basis:** C121

### 3.6 LINK (1 class, special status)

**Structural function:** Monitoring/intervention boundary marker
**Human interpretation:** "Check status now / observation point"

| Pattern | Human Guidance |
|---------|---------------|
| LINK appears | Mandatory observation point |
| LINK after h | "Verify phase transition completed" |
| LINK before HIGH_IMPACT | "Confirm before major action" |

**Constraint basis:** C366 (LINK marks grammar state transitions, p<10^-18)

**Statistical profile:** LINK is followed by HIGH_IMPACT at 2.70x and ENERGY_OPERATOR at 1.15x.

---

## 4. Participation Mode (PREFIX)

PREFIX does NOT encode action type. PREFIX encodes **how** to participate in control flow.

### 4.1 What PREFIX Communicates

| PREFIX Pattern | Human Interprets As | NOT This |
|----------------|---------------------|----------|
| High precision (ch vs sh) | "Execute carefully" | "Do energy action" |
| High tolerance (sh vs ch) | "Allow variation" | "Different action" |
| qo-prefix present | "Escape route available" | "Run away" |

**Constraint basis:**
- C466-C467: PREFIX encodes control-flow participation
- C408: Sister pairs (ch/sh, ok/ot) are equivalent slots - same action, different mode
- C397: qo-prefix correlates with escape routes at 25-47%

### 4.2 Sister Pair Equivalence (C408-C409)

**Critical:** ch/sh and ok/ot are NOT different actions. They are the SAME action in different modes:

| Sister Pair | Same Action, Different Mode |
|-------------|---------------------------|
| ch / sh | Precision mode vs Tolerance mode |
| ok / ot | Precision mode vs Tolerance mode |

Human interpretation: "Do this action carefully (ch/ok)" vs "Do this action with allowance for variation (sh/ot)"

### 4.3 Escape Permission (qo-prefix)

**Structural function:** Marks escape route availability
**Human interpretation:** "Recovery path exists here"

**Constraint basis:** C397 (qo-prefix = escape route, 25-47% of lines)

---

## 5. Envelope Level (REGIME)

REGIME provides folio-level context that modifies all instruction interpretation.

### 5.1 REGIME as Strategic Stance

| REGIME | Control Strategy (C395) | Human Stance |
|--------|------------------------|--------------|
| REGIME_1 | Gentle, conservative | "Proceed cautiously" |
| REGIME_2 | Moderate | "Standard operation" |
| REGIME_3 | Active | "Active management needed" |
| REGIME_4 | Aggressive | "Rapid small adjustments" |

**Constraint basis:** C179-C185 (REGIME definitions), C395 (Dual Control Strategy)

### 5.2 Hazard Envelope (C458)

**Grammar clamps danger, frees recovery.**

| Structural Pattern | Human Interpretation |
|-------------------|---------------------|
| Near hazard topology | "Danger zone - follow exactly" |
| High escape density | "Multiple safe options" |
| REGIME + hazard context | "This envelope defines your freedom" |

**Constraint basis:** C458, C109 (17 forbidden transitions)

---

## 6. What B Does NOT Communicate

Per validated constraints, B **cannot** encode:

| Cannot Encode | Constraint | Why |
|--------------|------------|-----|
| Preparation steps | C171 | Batch processing forbidden |
| Material identity | C120 | Pure operational, no materials |
| Ingredient lists | C384 | No entry-level coupling |
| Sequential workflow | C391 | Time-reversal symmetric |
| Quantities/amounts | C469 | Categorical, not parametric |
| Timing/duration | C171 | Continuous control, not timed steps |

**Human implication:** A human operator must bring external knowledge of:
- What material they are processing
- What preparation was done before entering the loop
- Specific quantities and timing from training/experience

B provides the **control structure**. The human provides the **domain context**.

---

## 7. Inference Model for Trained Operators

### 7.1 The Communication Flow

```
B Grammar Structure
       ↓
┌──────────────────────────────────┐
│  Kernel: k, h, e                 │  → Direct control verbs
│  Role: 49 classes → 7 categories │  → Action type families
│  PREFIX: Participation mode      │  → How carefully
│  REGIME: Envelope context        │  → Overall stance
└──────────────────────────────────┘
       ↓
Trained Operator Interprets
       ↓
Procedural Actions (including inferred prep)
```

### 7.2 Example Interpretation Chain

**B says (structurally):**
- REGIME_2 context
- High AUXILIARY, FLOW_OPERATOR density
- h (PHASE_MANAGER) at key points
- LINK markers after h
- e (STABILITY_ANCHOR) available
- qo-prefix escape routes present

**Trained operator infers:**
- "Standard operation envelope"
- "Requires careful handling and flow management"
- "Watch for phase transitions, verify after each"
- "Safe fallback state available"
- "Recovery options exist if needed"

**Domain knowledge adds:**
- "For this material type, that means grinding finely first"
- "Phase transition = vapor formation, watch for condensation"
- "Fallback = reduce heat to baseline"

---

## 8. Relationship to RI Material Identification

| Dimension | RI Tokens (Currier A) | Instruction Mappings (Currier B) |
|-----------|----------------------|--------------------------------|
| **References** | Material classes (WHAT) | Control actions (HOW) |
| **System** | Static registry | Executable grammar |
| **Basis** | C498 (Registry vocabulary) | C121 (49 instruction classes) |
| **Granularity** | MIDDLE-level discrimination | Role-level categories |
| **Recoverability** | Partial (P(class) vectors) | Role-level only (C382) |

**Parallel systems, orthogonal dimensions:**
- RI tells the human WHAT material class
- B tells the human HOW to control the process

Together: "This is [material class from A]. Process it [this way from B]."

---

## 9. Falsification Criteria

This Tier 4 model would be INVALIDATED if:

### 9.1 Grammar Violation
A proposed interpretation implies a forbidden transition (C109, 17 transitions). If "do X then Y" requires X→Y and that transition is forbidden, the interpretation is wrong.

### 9.2 Time-Reversal Asymmetry
Per C391, valid interpretations should work in both directions. Interpretations that only make sense forward violate time-reversal symmetry.

### 9.3 Predictivity Failure
Per C415 (HT NON-PREDICTIVITY), if adding HT worsens interpretation accuracy, the model is wrong.

### 9.4 Cross-Folio Inconsistency
Per C124 (100% coverage), interpretations must apply universally. Folio-specific meanings violate universality.

### 9.5 Role Combination Contradiction
Per C392 (97.2% role-level capacity), nearly all role combinations exist. Claims that certain combinations are "impossible" need strong justification.

### 9.6 Sister Pair Violation
Per C408-C409, ch/sh and ok/ot are equivalent slots. Any interpretation assigning different ACTION TYPES to sisters is wrong.

---

## 10. Grounding Summary

| Mapping | Constraint Basis | Grounding Strength |
|---------|-----------------|-------------------|
| k = "Adjust energy" | C103 | **STRONG** |
| h = "Watch phase transition" | C104 | **STRONG** |
| e = "Safe fallback" | C105 | **STRONG** |
| LINK = "Check status" | C366 | **STRONG** |
| qo = "Escape available" | C397 | **STRONG** |
| AUXILIARY = "Support action" | C396 | **MODERATE** |
| HIGH_IMPACT = "Major intervention" | C394 | **MODERATE** |
| FLOW_OPERATOR = "Flow management" | C121, correlation | **MODERATE** |
| Sister pairs = "Same action, different mode" | C408-C409 | **STRONG** |
| REGIME = "Strategic stance" | C179-C185, C395 | **MODERATE** |

---

## Navigation

← [INTERPRETATION_SUMMARY.md](INTERPRETATION_SUMMARY.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
