# Epistemic Layers: Constraint vs Fit vs Speculation

**Purpose:** Define the three knowledge layers in this project and how to correctly categorize new findings.

---

## The Core Distinction

| Layer | Question Answered | Changeability |
|-------|-------------------|---------------|
| **Constraint** | What MUST be true for the system to exist? | Requires model reopening |
| **Fit** | What HAPPENS to be true given this manuscript? | Can change with new data |
| **Speculation** | What MIGHT this mean for human interpretation? | Fully discardable |

---

## Layer 1: Constraints (Tier 0-2)

### Definition

A constraint is an **architectural necessity** — something that must be true for the reconstructed system to function as observed.

### Characteristics

- Derived from **internal structure**, not external comparison
- Would break the model if falsified
- Independent of any specific historical corpus
- Expressed as rules, not observations

### Examples

| Constraint | Why It's Necessary |
|------------|-------------------|
| C332: h→k forbidden | Grammar collapses if violated |
| C475: 95.7% MIDDLE incompatibility | Registry structure requires mutual exclusion |
| C458: Execution clamped, recovery free | Explains asymmetric design freedom |

### Test

> "If this were false, would the system still work?"
>
> If YES → Not a constraint
> If NO → Constraint

---

## Layer 2: Fits (F-series)

### Definition

A fit is a **demonstration of explanatory power** — something that happens to be true given this manuscript and the external world, but is not architecturally required.

### Characteristics

- May depend on external corpora (Brunschwig, Puff)
- Could fail in another historical context without breaking the model
- Expressed as observations, correlations, or predictions
- Answers "Does the model explain reality?" not "What must the model contain?"

### Sub-Types

| Type | Description | Example |
|------|-------------|---------|
| **External Alignment (F3)** | Model predicts external corpus structure | F-BRU-001: Brunschwig product types |
| **Characterization (F2)** | Quantifies model properties | F-BRU-005: Hierarchical MIDDLE structure |
| **Negative Knowledge (F2)** | Permanently kills alternative interpretations | F-BRU-003: Property model fails |
| **Robustness (F2)** | Shows stability under perturbation | F-BRU-004: Cluster stability |

### Test

> "If this were false, would the architecture still function?"
>
> If YES → Fit (not constraint)
> If NO → Promote to constraint

---

## Layer 3: Speculation (Tier 3-4)

### Definition

Speculation is **interpretive framing** — human-readable meaning that helps communication but carries no structural weight.

### Characteristics

- Can be discarded without affecting any constraint or fit
- May use semantic language ("aromatic", "medicinal")
- Useful for pedagogy, not for model definition
- Explicitly marked as speculative

### Examples

| Speculation | Why It's Discardable |
|-------------|---------------------|
| "MIDDLEs might encode processing requirements" | Model works regardless of what MIDDLEs "mean" |
| "WATER_GENTLE corresponds to delicate flowers" | External labeling, not internal necessity |
| "The manuscript is a distillation manual" | Domain hypothesis, not structural claim |

### Test

> "If we removed all semantic labels, would the constraints still hold?"
>
> If YES → Speculation is properly separated
> If NO → Semantic drift has contaminated constraints

---

## Decision Flowchart

```
New Finding
    │
    ▼
Does it define what MUST exist?
    │
    ├── YES → Is it internally derived?
    │           │
    │           ├── YES → CONSTRAINT (Tier 0-2)
    │           │
    │           └── NO → Reconsider: may be fit
    │
    └── NO → Does it demonstrate explanatory power?
              │
              ├── YES → FIT (F-series)
              │          │
              │          ├── External corpus? → F3
              │          ├── Kills alternatives? → F2 (Negative)
              │          └── Quantifies property? → F2
              │
              └── NO → Is it interpretive framing?
                        │
                        ├── YES → SPECULATION (Tier 3-4)
                        │
                        └── NO → Not a finding (noise)
```

---

## Common Mistakes

### 1. Promoting Fits to Constraints

**Wrong:** "Brunschwig predicts A signatures, so add C495."

**Right:** "Brunschwig alignment is F-BRU-001 (F3). It supports C475/C476 but doesn't define new architecture."

**Why:** External alignment could fail with a different corpus without breaking the Voynich model.

---

### 2. Treating Negative Knowledge as Positive Constraints

**Wrong:** "Property models fail, so add C498: MIDDLEs don't encode properties."

**Right:** "F-BRU-003 permanently kills property interpretations. Link to C475/C476 as evidentiary support."

**Why:** Negative knowledge tells us what the system IS NOT, but the constraint system should define what it IS.

---

### 3. Semantic Drift in Constraint Language

**Wrong:** "C500: MIDDLEs encode material properties hierarchically."

**Right:** "F-BRU-005: MIDDLE vocabulary shows hierarchical structure (supports C383)."

**Why:** "Material properties" is interpretive. "Hierarchical structure" is geometric/observational.

---

### 4. Redundant Constraints

**Wrong:** "Add C500 for hierarchical MIDDLE structure."

**Right:** "This is already implied by C383 (global type system) and C475 (incompatibility). Fold into existing documentation."

**Why:** If a new finding is predicted by existing constraints, it's a fit (confirmation), not a new constraint.

---

## The Saturation Principle

When new tests keep landing exactly where they should without forcing upstream changes:

> **The model is saturated, not brittle.**

This is the **best possible outcome**. It means:
- The architecture is complete
- New findings confirm rather than extend
- Discovery phase is over; consolidation phase begins

---

## File Locations

| Layer | Primary Location | Format |
|-------|-----------------|--------|
| Constraints | `context/CONSTRAINT_TABLE.txt` | C### entries |
| Fits | `context/MODEL_FITS/FIT_TABLE.txt` | F-XXX-### entries |
| Speculation | `context/SPECULATIVE/` | Markdown narratives |

---

## For Future Sessions

When proposing new additions:

1. **Ask:** "Is this architecturally necessary or observationally true?"
2. **Check:** Does it follow from existing constraints?
3. **Categorize:** Constraint / Fit / Speculation
4. **Document:** In the correct location with correct tier

If uncertain, default to **Fit**. Constraints should be rare and carefully justified.

---

*This legend exists to prevent epistemic category errors. The distinction matters for long-term model stability.*
