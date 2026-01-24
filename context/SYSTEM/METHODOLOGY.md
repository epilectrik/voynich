# Methodology

**Purpose:** Warnings, common bugs, and patterns for safe analysis.

---

## Critical Warning: Prefix Matching vs Token Matching

**RECURRENT BUG: This has caused false results multiple times.**

The 17 forbidden transitions are about **specific token pairs or token-class pairs**, NOT blanket prefix-to-prefix rules.

| WRONG | RIGHT |
|-------|-------|
| "Any `ol-` followed by any `qo-` is forbidden" | Specific transitions between grammar classes are forbidden |
| Testing `olsheol → qokchy` as forbidden | These are different tokens than the forbidden pair |
| Finding thousands of "violations" | Real violations are 0 in valid Currier B text |

**When writing new analysis scripts:**
1. Check if you're matching PREFIXES or specific TOKENS
2. Verify against the canonical grammar (479 types in Currier B)
3. Test on small samples before drawing conclusions
4. If results seem too good or too bad, check parsing logic first

---

## File Organization

| File Type | Location |
|-----------|----------|
| Phase analysis scripts | `archive/scripts/` |
| Utility scripts | `archive/scripts/` |
| Generated reports | `archive/reports/` |
| Phase documentation | `phases/<PHASE_NAME>/` |
| Canonical data | `data/transcriptions/` |
| Frozen outputs | `results/` |
| Curated knowledge | `context/` |

**Main directory should contain only:**
- `CLAUDE.md` (redirect to context/)
- `README.md`
- Configuration files
- Core library code in `lib/`

---

## Script Patterns

### Canonical Data Source

**PRIMARY DATA FILE:** `data/transcriptions/interlinear_full_words.txt`

This is the ONLY transcription file that should be used for quantitative analysis. It contains:
- Tab-separated values with headers
- Columns: word, complex_word, folio, section, quire, panel, language (A/B), hand, placement, line_number, transcriber, line_initial, line_final, etc.
- 122,160 tokens total
- Standard Voynich vocabulary (ch, sh, qo, da, ol, etc.)

**WARNING:** Other transcription files exist (e.g., `voynich_eva.txt`) but use different encoding schemes. EVA notation uses digits and different character mappings. Using the wrong transcription will produce invalid results.

**Quick verification:**
- Correct: tokens start with `ch-`, `sh-`, `qo-`, `da-`, `ol-`, etc.
- Wrong (EVA): tokens start with `4o`, `1c`, `9k`, etc.

### Loading Transcription Data

```python
from lib.transcription import load_transcription

# Default: original data, no patches
tokens = load_transcription()

# With recovery: apply high-confidence patches
tokens = load_transcription(apply_recovery=True, min_confidence='HIGH')
```

**Direct loading (when lib not available):**
```python
import pandas as pd
DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
```

### Filtering by Currier Language

```python
# Currier B only (most analysis)
if currier == 'B' and transcriber == 'H' and token and '*' not in token:
    # process token

# Currier A only
if currier == 'A' and transcriber == 'H' and token and '*' not in token:
    # process token
```

### Checking Against Grammar

```python
# Load canonical grammar
with open('results/canonical_grammar.json') as f:
    grammar = json.load(f)

# Check if token is in grammar
canonical_types = set(grammar['token_types'])  # 479 types
is_canonical = token in canonical_types
```

---

## PP (Pipeline-Participating) MIDDLE Analysis

**CRITICAL: PP analysis requires procedural grounding.**

### Valid Methodology (C505)

PP profile discrimination works when records are identified via **procedural trace**:

```
Known product type (B) → Required B folios → A records with high survival → RI MIDDLEs exclusive to those records → PP signature
```

This methodology:
- Starts from B-side procedural constraints
- Traces back to A records via vocabulary survival
- Identifies RI MIDDLEs that appear exclusively in those A records
- Then computes PP enrichment in those records

**Example (Animal/PRECISION):**
1. PRECISION product type requires specific B folios
2. 13 A records converge to those folios
3. RI MIDDLEs {eyd, tchyf, ofy, ...} are exclusive to those records
4. PP signature: 'te' (15.8x), 'ho' (8.7x), 'ke' (5.1x)

### Invalid Methodology (FALSIFIED)

**Do NOT use Bayesian class posteriors for PP discrimination.**

The material_class_priors.json approach:
- Assigns class probabilities based on folio co-occurrence
- Identifies taxonomically similar records
- Does NOT identify procedurally equivalent records

**Dilution test result:**
- C505 methodology (13 records): 15.8x enrichment
- Bayesian posteriors (40 records): 5.1x enrichment (diluted)
- Bayesian-only extra records (27): 0.9x enrichment (baseline noise)

The Bayesian approach adds false positives that dilute the PP signal.

### Invalid Axis (FALSIFIED)

**Do NOT use fire degree as a PP axis.**

Fire degree (1=gentle, 2=standard, 3=moderate) reflects thermal tolerance, not handling complexity:
- Fire 1 includes animals AND flowers (both "gentle")
- This conflation destroys PP discrimination signal
- Material class (animal vs herb vs flower) is the valid axis

### Summary

| Approach | Status | Result |
|----------|--------|--------|
| Procedural trace (B→A) | VALID | 15.8x enrichment |
| Bayesian class posteriors | FALSIFIED | Diluted signal |
| Fire degree grouping | FALSIFIED | Conflated categories |

---

## Common Analytical Errors

### 1. Sample Size Issues

- Currier A has ~37,000 tokens, B has ~75,000
- Some folios have <100 tokens
- Statistical tests need sufficient data

### 2. Section Confusion

- "Currier" = language classification (A or B)
- "Section" = manuscript section (H, B, C, S, T, P, etc.)
- These are NOT the same thing

### 3. AZC Folio Grouping

**RECURRENT BUG: AZC analyses have used inconsistent folio counts.**

AZC folios have TWO independent classification systems:

| System | Criterion | Result |
|--------|-----------|--------|
| Visual (section codes) | Illustration type | Z=12, A=8, C=7, H=2, S=1 (30 total) |
| Textual grammar | Placement patterns | Zodiac=13 (incl f57v), A/C=17 |

**Key facts:**
- Total AZC in transcript: 30 folios
- Actual diagram folios: 27 (H and S are NOT diagrams)
- f57v is C by section code but Zodiac by placement grammar

**Every AZC analysis MUST document:**
1. Which folios were included (list them or describe filter)
2. Which classification system was used (visual vs grammar)
3. Whether H/S non-diagram folios were included
4. Why that grouping was chosen

**See:** `context/ARCHITECTURE/currier_AZC.md` for full classification details.

### 4. Transition Direction

- `X → Y` is the transition FROM X TO Y
- Forbidden transitions are asymmetric (65%)
- Don't assume bidirectional rules

### 5. Tier Promotion

- Don't treat Tier 3 findings as structural
- Always cite the tier when referencing claims
- Keep speculative content quarantined

---

## Constraint-First Reasoning

**RULE: Check constraints BEFORE speculating.**

When reasoning about relationships, interpretations, or implications:

1. **Search constraints first:**
   - Grep `context/CLAIMS/` for relevant keywords
   - Check INDEX.md for related constraint numbers
   - Read the actual constraint files, not just summaries

2. **Distinguish what is constrained vs. undocumented:**
   - Constrained = tested claim with evidence and tier
   - Undocumented = no constraint exists (gap, not confirmation)
   - Never treat absence of constraint as permission to speculate freely

3. **Cite or flag:**
   - If constrained: cite the constraint number
   - If undocumented: explicitly state "this is not constrained" and flag as potential research gap

**Example of error (actually occurred):**
> "Currier A entries might reference the same categories that B executes"
>
> This seemed plausible but **C384 explicitly falsifies entry-level A-B coupling.**
> Checking constraints first would have caught this.

---

## Questioning Constraints

**Constraints are conclusions, not dogma.** It is acceptable to:

1. **Question a constraint** when new evidence or reasoning suggests it may be:
   - Overstated (evidence weaker than tier implies)
   - Incomplete (missing edge cases)
   - In tension with another constraint

2. **Propose re-examination** if you find:
   - Internal contradictions between constraints
   - Gaps where expected constraints are missing
   - Evidence that contradicts a Tier 2 claim

3. **Never silently override** — if you think a constraint is wrong:
   - State the constraint explicitly
   - Present the conflicting evidence
   - Propose revision or flag for investigation

**Tier determines revisability:**
| Tier | Revisability |
|------|--------------|
| 0 | Frozen — do not question without extraordinary evidence |
| 1 | Falsified — do not retry, but can note if new approach differs |
| 2 | Closed — can propose reopening with new evidence |
| 3-4 | Open — expected to evolve |

---

## Research Workflow (Automated)

When Claude analyzes this project, follow this workflow:

### Phase Analysis Protocol

When analyzing a completed phase:

1. **Load context first:**
   - Read `context/CORE/frozen_conclusion.md` for Tier 0 facts
   - Read `context/CLAIMS/INDEX.md` for constraint reference

2. **Examine phase output:**
   - Read `phases/<PHASE_NAME>/` directory
   - Extract key metrics and findings
   - Identify claims being made

3. **Validate against existing constraints:**
   - Search CLAIMS/ for related constraints
   - Check for contradictions with Tier 0/1
   - Note supporting evidence from Tier 2

4. **Classify findings:**
   | Finding Type | Action |
   |--------------|--------|
   | NEW structural claim | Propose new constraint (C412+) |
   | CONFIRMS existing | Add citation to existing constraint |
   | CONTRADICTS Tier 0-1 | Flag as potential error in analysis |
   | SPECULATIVE | Assign Tier 3-4, add to SPECULATIVE/ |

5. **Document:**
   - Update relevant files in context/
   - Add to CLAIMS/INDEX.md if new constraint
   - Update MAPS/ cross-references

### Constraint Lookup Protocol

When user references a constraint:

1. Check if number exists in `context/CLAIMS/INDEX.md`
2. Determine if individual file or grouped registry
3. Read the relevant file
4. Always cite: Tier, closure status, source phase

### New Analysis Protocol

Before running new analysis:

1. Check `context/CORE/falsifications.md` - don't retry rejected approaches
2. Check `context/SYSTEM/STOP_CONDITIONS.md` - respect boundaries
3. Define success criteria BEFORE running
4. Assign expected tier to potential findings

---

## Creating New Phases

1. **Create directory:** `phases/PHASE_NAME/`
2. **Include:**
   - `README.md` or `PHASE_SUMMARY.md`
   - Analysis scripts (copy to `archive/scripts/`)
   - Output data
3. **Document:**
   - Pre-defined success criteria
   - What tier the findings belong to
   - Which constraints are added/updated
4. **Update:**
   - `context/CLAIMS/INDEX.md` if new constraints
   - `context/MAPS/claim_to_phase.md`
   - `context/SYSTEM/CHANGELOG.md`

---

## Constraint Maintenance Workflow

**Source of truth:** The grouped registry files in `context/CLAIMS/`

**Workflow for adding constraints:**

1. **Add to appropriate registry file:**
   - `tier0_core.md` - Frozen Tier 0 facts
   - `grammar_system.md` - B grammar structure
   - `currier_a.md` - A registry properties
   - `morphology.md` - Compositional system
   - `operations.md` - OPS doctrine
   - `human_track.md` - HT layer
   - `azc_system.md` - AZC hybrid system
   - `organization.md` - Organizational structure

2. **Use consistent format:**
   ```markdown
   ### C### - Title
   **Tier:** # | **Status:** CLOSED
   Description text.
   **Source:** Phase/Source
   ```

3. **Regenerate the enumerated table:**
   ```bash
   python context/generate_constraint_table.py
   ```
   This parses all registry files and outputs `CONSTRAINT_TABLE.txt`.

4. **Update INDEX.md** if adding a representative constraint to a category table.

5. **Update counts** in CLAUDE_INDEX.md, INDEX.md, CLAUDE.md if total changes.

**Do NOT edit CONSTRAINT_TABLE.txt directly** — it is generated from registry files.

---

## Citing Constraints

Format: `Constraint ###` or `C###`

Example: "Currier A is folio-disjoint from B (C272)"

Always include the constraint number for traceability.

---

## Claude Code Session Behavior

### Plan Mode File Management

**RULE: Use Write, not Edit, for fresh plans.**

When entering plan mode for a **different task** than the existing plan file:
- Use `Write` tool to completely overwrite the plan file
- Do NOT use `Edit` to incrementally modify the old plan

**Why this matters:**
- Incremental edits waste context tokens
- Risk leaving remnants of old content
- Slower and more error-prone
- Pollutes context with irrelevant intermediate states

**Correct approach:**
```
# Different task → complete replacement
Write(file_path=plan_file, content=entire_new_plan)
```

**Incorrect approach:**
```
# Wasteful incremental modification
Edit(old_string=chunk1, new_string=new_chunk1)
Edit(old_string=chunk2, new_string=new_chunk2)
...
```

**When to use Edit on plan files:**
- Same task, refining existing plan
- Adding a section to current plan
- Fixing a typo or small correction

---

## What Cannot Be Recovered Internally

No amount of structural analysis can determine:

- Specific substances, materials, or products
- Natural language equivalents for any token
- Historical identity of author or school
- Precise dating or geographic origin
- Illustration meanings
- Physical apparatus construction details

These require external evidence and belong to Tier 3+.

---

## Related: Fit System

For logging explanatory models (fits), see [FIT_METHODOLOGY.md](FIT_METHODOLOGY.md).

Key distinction:
- **Constraints** (this document): Structural claims that bind behavior
- **Fits** (FIT_METHODOLOGY.md): Explanatory models that demonstrate sufficiency

Fits explain. Constraints bind. Never confuse the two.

---

## Navigation

← [STOP_CONDITIONS.md](STOP_CONDITIONS.md) | [FIT_METHODOLOGY.md](FIT_METHODOLOGY.md) | [HOW_TO_READ.md](HOW_TO_READ.md) →
