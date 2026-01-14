# Test 3: Experience vs Instruction Boundary

**Question:** When does experience trump written instruction?

**Verdict:** Four knowledge types identified that CANNOT be transmitted through written instruction alone.

---

## Methodology

Surveyed historical sources and tacit knowledge literature to identify what the controller DELIBERATELY OMITS — knowledge that must come from experience, not documentation.

**Key concept:** Polanyi's Tacit Dimension
> "We can know more than we can tell."

This establishes that some knowledge is structurally non-codifiable.

---

## Tacit Knowledge Types Identified

### Type 1: SENSORY CALIBRATION

**What it is:**
Knowing what "right" looks, feels, smells, tastes like.

**Historical evidence:**
> "Diligent practice and use of the handwork" and knowledge "seen with eyes and heard with ears"
> "The feel of proper furnace construction, the sight of correctly flowing distillates, and the taste that confirms potency cannot be fully captured in print."

**Why it cannot be written:**
- "Right" is comparative to learned baseline
- No absolute reference exists
- Each apparatus/material has its own "right"
- Calibration is personal (my baseline ≠ your baseline)

**Structural property:**
This is **IDENTITY-DEPENDENT** knowledge — it depends on which specific apparatus, materials, and operator are involved.

---

### Type 2: EQUIPMENT FEEL

**What it is:**
Knowing the specific quirks and behaviors of YOUR apparatus.

**Historical evidence:**
> "Assessing equipment quality from different regional suppliers"
> "Visual inspections of the column internals"

**Modern parallel:**
> "The equipment works as part of a process, and both must be understood for effective troubleshooting."

**Why it cannot be written:**
- Each piece of equipment is unique
- Behavior varies with age, use, repairs
- "Normal for THIS apparatus" is learned, not specified
- Transfer to new equipment requires re-learning

**Structural property:**
This is **INSTANCE-DEPENDENT** knowledge — general instructions can't capture specific equipment behavior.

---

### Type 3: TIMING INTUITION

**What it is:**
Knowing when the process is "ready" without explicit indicators.

**Historical evidence:**
> "Knowing-how or 'embodied knowledge' is characteristic of the expert, who acts, makes judgments, and so forth without explicitly reflecting on the principles or rules involved."

**Modern parallel:**
> "Regular monitoring of key performance indicators... can help identify potential issues early on."

But the KEY is: experienced operators often know BEFORE KPIs trigger.

**Why it cannot be written:**
- Timing depends on integration of many subtle signals
- No single indicator is sufficient
- "Ready" is pattern recognition, not threshold
- Experts often can't explain HOW they know

**Structural property:**
This is **HOLISTIC** knowledge — emerges from integration, not from any single component.

---

### Type 4: TROUBLE RECOGNITION

**What it is:**
Early warning sense that something is going wrong.

**Historical evidence:**
> "Operators should be vigilant for unusual noises or vibrations, as these can indicate mechanical issues."
> "Heritage crafts embody... expertise that cannot be fully captured in written instructions."

**Modern parallel:**
> "Providing comprehensive training for operators on proper operation, troubleshooting techniques, and safety procedures."

But: training provides CATEGORIES of trouble; recognition requires EXPERIENCE.

**Why it cannot be written:**
- "Unusual" requires knowing "usual"
- Each installation has its own baseline
- Early signals are subtle and ambiguous
- False alarms must be filtered from real warnings

**Structural property:**
This is **DEVIATION-DETECTION** knowledge — requires implicit model of normal operation.

---

## The Transmission Problem

### Why Apprenticeship Is Required

From tacit knowledge research:
> "By watching the master and emulating his efforts in the presence of his example, the apprentice unconsciously picks up the rules of the art."

**Key insight:** The transfer mechanism is IMITATION, not INSTRUCTION.

| Knowledge Type | What Written Instruction Can Provide | What Must Be Learned by Doing |
|----------------|--------------------------------------|-------------------------------|
| Sensory calibration | Categories to attend to | What "right" feels like |
| Equipment feel | General maintenance | Your specific apparatus |
| Timing intuition | Checkpoints | When between checkpoints |
| Trouble recognition | Trouble categories | Subtle early warnings |

### What the Controller Deliberately Omits

The Voynich controller (per C469) uses CATEGORICAL resolution, not parametric.

**This means:**
- It can say WHICH class applies
- It CANNOT say WHERE in that class you are
- It can gate WHAT is legal
- It CANNOT supply the judgment to execute

**This is not a bug — it's a feature.**

The controller is designed to REQUIRE operator judgment because:
- That judgment cannot be encoded
- Encoding it would create false precision
- The system acknowledges its own limits

---

## The Irrecoverability Connection

From PWRE-1, the Voynich has **irrecoverability architecture**:
- HT correlates with tail pressure (attention)
- Hazards are asymmetric (65%)
- Recovery routes are constrained

**Why irrecoverability requires tacit knowledge:**

| Feature | Why Tacit Knowledge Required |
|---------|------------------------------|
| Asymmetric hazards | Must recognize WHICH asymmetry applies |
| Constrained recovery | Must judge WHEN recovery is possible |
| Attention spikes | Must know WHAT to attend to |

The system doesn't encode "be careful here" — it encodes "THIS is where attention matters" and trusts the operator to HAVE the relevant tacit knowledge.

---

## Experience vs Instruction Boundary Map

| Domain | Instruction Can Provide | Experience Must Provide |
|--------|------------------------|------------------------|
| Temperature | "Check by touch" | What "too hot" feels like |
| Phase | "Watch for branching" | Recognizing actual branching |
| Quality | "Taste to confirm" | What "confirmed" tastes like |
| Timing | "Wait until done" | Knowing "done" |
| Trouble | "Watch for problems" | Recognizing early signals |
| Equipment | "Maintain regularly" | Knowing YOUR equipment |

**The boundary is structural:**
> Instructions can specify WHAT to do and WHEN to check.
> Experience must supply HOW to judge and WHAT counts.

---

## Connection to HT (C477)

HT rises when tail MIDDLEs appear.

**Interpretation:**
- Common situations → routine judgment → low cognitive load
- Rare situations → require deeper tacit knowledge → high cognitive load
- HT signals "this requires experience, not just following instructions"

---

## Conclusion

**Test 3 Result: 4 TACIT KNOWLEDGE TYPES IDENTIFIED**

| Type | What Must Be Learned | Why Non-Codifiable |
|------|----------------------|-------------------|
| 1 | SENSORY_CALIBRATION | Identity-dependent baseline |
| 2 | EQUIPMENT_FEEL | Instance-specific behavior |
| 3 | TIMING_INTUITION | Holistic integration |
| 4 | TROUBLE_RECOGNITION | Deviation from implicit model |

All four are:
- Structurally non-codifiable (cannot be written)
- Transmission requires apprenticeship (imitation, not instruction)
- Aligned with irrecoverability architecture

**The controller DELIBERATELY OMITS what cannot be encoded.**

This is not a limitation — it's design integrity.

---

## Constraints Cited

- C469 - Categorical Resolution Principle
- C477 - HT Tail Correlation
- Irrecoverability architecture (PWRE-1)

---

## Sources

- [Tacit Knowledge - Wikipedia](https://en.wikipedia.org/wiki/Tacit_knowledge)
- [PMC: Brunschwig's Liber de arte distillandi](https://pmc.ncbi.nlm.nih.gov/articles/PMC5268093/)
- [Stripe Press: Tacit](https://www.stripe.press/tacit)

---

> *This analysis identifies structural classes of tacit knowledge without interpreting their semantic content. No substances, materials, or specific conditions are named.*
