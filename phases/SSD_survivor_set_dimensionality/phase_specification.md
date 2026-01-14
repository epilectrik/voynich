# Phase SSD: Survivor-Set Dimensionality

**Status:** OPEN | **Date:** 2026-01-12 | **Tier Target:** 2

---

## Background

A structural gap has been identified in the A→AZC→B pipeline:

> **We do not yet have a fully specified account of what it means—mechanistically—for many Currier A tokens to remain admissible after AZC filtering, given that A multiplicity does not interact with B (C254).**

### What We Know (Firm Ground)

| Constraint | Finding |
|------------|---------|
| C233 | A lines are LINE_ATOMIC (median 3 tokens) |
| C254 | A multiplicity does NOT interact with B grammar |
| C422 | DA articulates sub-records within complex A entries |
| C458 | B execution complexity is clamped |
| C475 | Only 4.3% of MIDDLE pairs can legally co-occur |
| F-AZC-016 | AZC→B causal transfer is real and measurable |

### The Gap

When a Currier A line (potentially 40+ tokens with DA-articulated sub-cases) is filtered through AZC, some subset survives as "admissible." Example: 18/42 tokens pass.

**Unresolved question:**
> What is the representational role of a large surviving admissible A-set if it neither selects a specific B program nor scales B's grammatical complexity?

### Three Competing Hypotheses

| Hypothesis | Description | Prediction |
|------------|-------------|------------|
| **H-A: Equivalence-Class Refinement** | Large survivor set refines what B treats as equivalent | HT morphological diversity scales with survivor size |
| **H-B: Constraint Envelope Narrowing** | Survivor set defines convex envelope; more tokens = tighter envelope | Survivor size uncorrelated with HT; B variability unchanged |
| **H-C: Deferred Resolution** | Distinctions not immediately resolved, collapse later | B shows time-varying survivor effects (weakest) |

---

## Phase Objective

**Disambiguate the three hypotheses through targeted measurement.**

---

## Test 1: Survivor-Set Size vs HT Morphology

### Question
Does HT morphological diversity (not density) scale with survivor-set size?

### Rationale
- If H-A (equivalence-class refinement) is correct, more survivors = more discrimination responsibility = more HT diversity to support it
- If H-B (envelope narrowing), HT diversity should be independent of survivor count

### Method

1. **Build survivor-set calculator:**
   - For each AZC folio, extract scaffold MIDDLEs by position zone (C/P/R/S)
   - For each Currier A line, compute AZC-admissible survivor count
   - Survivor = A token whose MIDDLE appears in scaffold for its position zone

2. **Compute HT morphology metrics:**
   - For each A line (or adjacent context window), measure:
     - HT PREFIX entropy (not count)
     - HT MIDDLE diversity
     - HT type count / token count ratio

3. **Correlate:**
   - Spearman correlation: survivor_count vs HT_entropy
   - Control for A line length (partial correlation)
   - Control for section (stratified analysis)

### Data Requirements

| Data | Source |
|------|--------|
| Currier A lines | `data/transcriptions/interlinear_full_words.txt` (language='A') |
| AZC scaffold | `data/transcriptions/interlinear_full_words.txt` (language not A/B, placement codes) |
| HT tokens | Tokens with prefix in {HT_PREFIX_SET} - requires definition |
| MIDDLE extraction | Morphological decomposition from C267 |

### Success Criteria

| Result | Interpretation |
|--------|----------------|
| rho > 0.2, p < 0.05 | **Supports H-A** (equivalence-class refinement) |
| rho ≈ 0, p > 0.1 | **Supports H-B** (envelope narrowing) |
| rho < -0.2, p < 0.05 | Unexpected - needs investigation |

### Output
- `results/ssd_test1_survivor_ht_correlation.json`
- Scatter plot with regression line
- Stratified results by section

---

## Test 2: Survivor-Set Size vs B Micro-Variability

### Question
Do larger survivor sets correlate with internal B execution variability?

### Rationale
- C254 says multiplicity doesn't interact with B grammar
- But does survivor SIZE affect B micro-variability (within-grammar variance)?
- If yes, C254 needs refinement: multiplicity leaks into execution in constrained ways

### Method

1. **Identify B folios with paired A-line contexts:**
   - Find B execution windows preceded by:
     - Small survivor sets (bottom quartile)
     - Large survivor sets (top quartile)
   - Match on other confounds (section, position)

2. **Measure B micro-variability within each window:**
   - Recovery path variance (how many distinct recovery routes used)
   - LINK distribution entropy
   - Convergence volatility (state-change rate)
   - Kernel contact rate variance

3. **Compare:**
   - Mann-Whitney U: large_survivor_B_variability vs small_survivor_B_variability
   - Effect size (Cohen's d)

### Data Requirements

| Data | Source |
|------|--------|
| A→B pairing | Requires definition of "A-line precedes B-window" |
| B execution metrics | Computed from transition sequences |
| Grammar classes | `results/canonical_grammar.json` |

### Success Criteria

| Result | Interpretation |
|--------|----------------|
| p < 0.05, d > 0.3 | **Refines C254** - multiplicity DOES leak into B variability |
| p > 0.1 | **Confirms C254** - survivor size acts purely at discrimination level |

### Output
- `results/ssd_test2_survivor_b_variability.json`
- Distribution comparison plots
- Effect size table

---

## Test 3: Intersection Stability

### Question
Is elimination or survival doing the work?

### Rationale
- If two A lines produce the SAME survivor set but differ in eliminated tokens:
  - Same downstream behavior → survivor identity is sufficient
  - Different downstream behavior → bundling effects exist beyond survivor identity

### Method

1. **Find survivor-set collisions:**
   - Across all A lines, compute survivor sets
   - Find pairs where survivor_set(A_line_i) == survivor_set(A_line_j)
   - But eliminated tokens differ: eliminated(A_line_i) ≠ eliminated(A_line_j)

2. **Compare downstream behavior:**
   - HT density in adjacent window
   - B execution signature (if applicable)
   - Section-matched comparison

3. **Statistical test:**
   - Paired comparison of downstream metrics
   - Null hypothesis: identical survivor sets → identical downstream behavior

### Data Requirements

| Data | Source |
|------|--------|
| All A lines with survivor sets | From Test 1 computation |
| Downstream metrics | HT density, B signatures |

### Success Criteria

| Result | Interpretation |
|--------|----------------|
| Downstream behavior indistinguishable (p > 0.1) | **Elimination does all work** - survivor set identity is sufficient |
| Downstream behavior differs (p < 0.05) | **Bundling effects exist** - eliminated tokens matter |

### Output
- `results/ssd_test3_intersection_stability.json`
- Collision pair catalog
- Downstream comparison table

---

## Dependencies

### Required Definitions (Before Tests Can Run)

1. **HT prefix set:** Which prefixes constitute Human Track?
   - Source: `context/CLAIMS/human_track.md` or C404-C406

2. **A→B pairing logic:** How to associate A lines with B execution windows?
   - Option A: Folio adjacency (A folio followed by B folio)
   - Option B: Section membership
   - Option C: Vocabulary overlap window

3. **Survivor computation:** Exact algorithm for determining admissibility
   - Position zone mapping (C/P/R/S from line position)
   - MIDDLE extraction (canonical decomposition)
   - Match criteria (exact vs substring vs prefix)

### External Data

- AZC folio features: `results/azc_folio_features.json`
- Position zone definitions: From F-AZC-005 (fits_azc.md)

---

## Constraints Addressed

| Constraint | How Addressed |
|------------|---------------|
| C254 | Test 2 either confirms or refines |
| C475 | Survivor computation uses MIDDLE incompatibility |
| C477 (HT tail correlation) | Test 1 extends to survivor-set dimension |
| F-AZC-016 | Tests whether causal transfer varies by survivor size |

---

## Expected Outcomes

### If H-A (Equivalence-Class Refinement) Wins
- Test 1: Positive correlation (rho > 0.2)
- Test 2: Null (no B variability effect)
- Test 3: Elimination matters (bundling effects exist)

**New constraint:** "Survivor-set size scales discrimination responsibility without inflating B complexity"

### If H-B (Envelope Narrowing) Wins
- Test 1: Null (no HT diversity effect)
- Test 2: Null (no B variability effect)
- Test 3: Survivor identity sufficient

**New constraint:** "Survivor-set defines constraint envelope; dimensionality is structural, not operational"

### If Mixed Results
- Document which aspects of each hypothesis are supported
- May indicate survivor-set has multiple functional roles

---

## Script Locations

| Script | Purpose |
|--------|---------|
| `archive/scripts/ssd_survivor_calculator.py` | Compute survivor sets for all A lines |
| `archive/scripts/ssd_test1_ht_correlation.py` | Test 1 implementation |
| `archive/scripts/ssd_test2_b_variability.py` | Test 2 implementation |
| `archive/scripts/ssd_test3_intersection.py` | Test 3 implementation |

---

## Execution Order

1. **Resolve dependencies** (HT prefix set, A→B pairing, survivor algorithm)
2. **Build survivor calculator** and validate on known cases
3. **Run Test 1** (HT morphology) - feasible with existing data
4. **Run Test 2** (B variability) - requires A→B pairing definition
5. **Run Test 3** (intersection stability) - requires sufficient collision pairs
6. **Synthesize results** and propose new constraints

---

## Stop Conditions

- **SUCCESS:** At least 2/3 tests produce significant results in consistent direction
- **PARTIAL:** Tests produce mixed results requiring refined hypothesis
- **FAILURE:** All tests null - survivor-set dimensionality has no measurable effect (unlikely given HT correlation structure)

---

## Navigation

↑ [../../context/CLAUDE_INDEX.md](../../context/CLAUDE_INDEX.md)
