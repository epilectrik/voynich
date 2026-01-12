# Fit Methodology

**Purpose:** Governance rules for the explanatory fit system.

**Core Principle:** Fits explain. Constraints bind. Never confuse adequacy with necessity.

---

## What is a Fit?

A **fit** is a statistical or generative model that adequately explains an observed pattern. Fits demonstrate that a simpler explanation is *sufficient* for the data.

**Key distinction:**
- **Constraint:** "Pattern X must hold" (structural claim, restricts behavior)
- **Fit:** "Pattern X can be explained by model Y" (explanatory claim, no restriction)

---

## Language Rules

### Fit-Safe Vocabulary (USE THESE)

| Verb | Meaning |
|------|---------|
| explains | Model accounts for observed variance |
| accounts for | Model sufficient for pattern |
| is sufficient to generate | Model can produce observed distribution |
| collapses the need for | Simpler model replaces complex hypothesis |
| supports existing constraints | Evidence aligns with constraint claims |
| fails exactly where expected | Negative result confirms boundary |

**Example:**
> "The factored token model **explains** 98% of token frequency."

### Forbidden Vocabulary (NEVER USE)

| Verb | Why Forbidden |
|------|---------------|
| governs | Implies constraint-like authority |
| determines | Implies causation, not adequacy |
| rules | Implies structural necessity |
| encodes | Implies intentional design |
| necessitates | Implies logical requirement |
| defines legality | This is constraint language |
| is required for | Implies necessity |

**Example of error:**
> ~~"The factored model **governs** token generation."~~
> This incorrectly promotes an explanatory fit to structural constraint.

---

## Fit Tier Definitions

| Tier | Label | Meaning | Constraint Effect |
|------|-------|---------|-------------------|
| **F0** | TRIVIAL | Definitional or tautological fit | None |
| **F1** | FAILED | Negative knowledge - model did not explain | None |
| **F2** | ADEQUATE | Simple model sufficient for observed pattern | None |
| **F3** | COMPELLING | Strong but non-necessary explanation | None |
| **F4** | EXPLORATORY | Provisional modeling attempt | None |

**All tiers have Constraint Effect = None.** This is by design.

---

## Tier Promotion Rules

### F4 → F3: Exploratory to Compelling

Requires:
- Multiple independent tests show consistency
- Cross-validation on held-out data
- Theoretical motivation beyond curve-fitting
- **Human authorization**

### F3 → F2: Compelling to Adequate

Requires:
- Success criteria defined BEFORE testing
- Statistical significance at p < 0.01
- No overfitting (model simpler than data structure)
- **Human authorization**

### F2 → Constraint: NEVER AUTOMATIC

**A fit CANNOT become a constraint without explicit human instruction.**

Even a perfect F2 fit remains in the fit registry. The claim "model explains pattern" never implies "pattern must follow model."

Promotion to constraint requires:
1. Human expert explicitly requests promotion
2. Independent structural evidence beyond the fit
3. Constraint language properly formulated
4. New C-number assigned through constraint workflow

---

## Failure Protocol (F1 Handling)

Null results are valuable. An F1 fit documents what does NOT work.

### Recording Failed Fits

```markdown
## F-X-###: [Name]

**Fit Tier:** F1 | **Status:** ACTIVE | **Date:** YYYY-MM-DD

### Question Tested
[What model was attempted]

### Result
**NULL** - [Specific failure metrics]

### Value of Failure
- Rules out [hypothesis]
- Suggests [alternative direction]
- Supports constraints [C###] by exclusion
```

### What F1 Results Tell Us

| Failure Pattern | Interpretation |
|-----------------|----------------|
| Random baseline = best | Feature set inadequate |
| Combined model < baseline | Features interfering |
| >75% but <90% accuracy | Partial structure exists |
| Perfect on subset, fails on rest | Subset boundary matters |

---

## Interaction with Constraint System

### Fits MAY:

- **Support** existing constraints by providing explanatory mechanism
- **Refine understanding** of why constraints hold
- **Falsify alternatives** to existing explanations
- **Identify gaps** where new constraints might be needed

### Fits NEVER:

- **Become** constraints without human instruction
- **Override** constraint claims
- **Define legality** or structural requirements
- **Restrict** what is considered valid

### Cross-Reference Protocol

When logging a fit, document:

```markdown
### Relation to Constraints
- **Supports:** C### (constraint receives explanatory support)
- **Refines:** C### (fit clarifies mechanism)
- **Falsifies alternatives to:** C### (competing hypothesis ruled out)
- **Introduces NEW constraints:** NO ✓
```

The final line must always be present and must always be "NO" unless human authorization changes this.

---

## Fit Numbering Convention

| Scope | Prefix | Example |
|-------|--------|---------|
| Currier A | F-A-### | F-A-001, F-A-002 |
| Currier B | F-B-### | F-B-001 |
| AZC System | F-AZC-### | F-AZC-001 |
| Human Track | F-HT-### | F-HT-001 |
| Global/Cross-System | F-G-### | F-G-001 |

Numbers are assigned sequentially within each scope.

---

## Fit Documentation Standard

Fits use a **two-layer format** (like constraints):
- **Header line:** Standardized for programmatic parsing
- **Body sections:** Detailed methodology for human reference

### Header Format (Required - Parser Reads This)

```markdown
### F-X-### - Title

**Tier:** F# | **Result:** SUCCESS/PARTIAL/NULL | **Supports:** C###, C###
```

The parser extracts: ID, Title, Tier, Result, Supports from these two lines only.

### Body Format (Required - Human Reference)

```markdown
#### Question
What hypothesis or model was tested.

#### Method
Statistical approach, data used, success criteria.

#### Result Details
- Criterion 1: value (PASS/FAIL)
- Criterion 2: value (PASS/FAIL)

#### Interpretation
What this result means for the model.

#### Limitations
What this fit does NOT establish.
```

### Required Fields

| Field | Format | Location |
|-------|--------|----------|
| **ID** | `F-X-###` | Header line 1 |
| **Title** | Free text | Header line 1 |
| **Tier** | `F#` | Header line 2 |
| **Result** | SUCCESS/PARTIAL/NULL | Header line 2 |
| **Supports** | C###, C###-C### | Header line 2 |
| **Question** | Free text | Body |
| **Method** | Free text | Body |
| **Interpretation** | Free text | Body |

### Result Definitions

| Result | Meaning |
|--------|---------|
| **SUCCESS** | Model explains observed pattern |
| **PARTIAL** | Model explains some but not all variance |
| **NULL** | Model failed to explain pattern (negative knowledge) |

### Complete Example

```markdown
### F-A-001 - Compositional Token Generator

**Tier:** F2 | **Result:** PARTIAL | **Supports:** C267-C282

#### Question
Can observed PREFIX+MIDDLE+SUFFIX combinations be generated from a factored probability model?

#### Method
P(token) = P(PREFIX) × P(MIDDLE|PREFIX) × P(SUFFIX|PREFIX,MIDDLE)

Data: 37,214 Currier A tokens, lowercase normalized, all hands.

Success criteria (defined before testing):
- Type coverage >90%
- Token coverage >85%
- Perplexity <30% of uniform baseline

#### Result Details
- Type coverage: 84.5% (FAIL - below 90%)
- Token coverage: 98.0% (PASS)
- Perplexity ratio: 13.8% (PASS)
- Novel generation rate: 0% (no over-generation)

#### Interpretation
The factored model accounts for 98% of token frequency, demonstrating compositional morphology is sufficient for productive vocabulary. The 15.5% missing types are sparse combinations—structural gaps, not productive forms.

#### Limitations
This fit does NOT establish that tokens "must" follow this factorization—only that observed frequency is explained by it. The model is sufficient, not necessary.
```

### Programmatic Access

`FIT_TABLE.txt` is generated from fit registry files by `generate_fit_table.py`.

Format: `ID	FIT	TIER	SCOPE	RESULT	SUPPORTS	FILE`

The generator parses ONLY the header lines. Body content is preserved for human reference but not extracted.

Run `python context/MODEL_FITS/generate_fit_table.py` to regenerate.

---

## Operational Summary

**For Claude when working with fits:**

1. **Before logging a fit:**
   - Ensure language uses fit-safe vocabulary
   - Assign appropriate tier (F0-F4)
   - Define success criteria before testing
   - Document relation to constraints

2. **When interpreting fits:**
   - Never say "this means pattern X must hold"
   - Always say "this model explains pattern X"
   - Acknowledge remaining variance

3. **When asked to promote fit to constraint:**
   - Flag as requiring human authorization
   - Document what additional evidence would be needed
   - Never auto-promote

4. **When a fit fails (F1):**
   - Log it as valuable negative knowledge
   - Document what alternatives it rules out
   - Do not delete or hide failures

---

## Navigation

← [METHODOLOGY.md](METHODOLOGY.md) | [STOP_CONDITIONS.md](STOP_CONDITIONS.md) →
