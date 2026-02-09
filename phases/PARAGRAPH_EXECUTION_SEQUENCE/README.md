# PARAGRAPH_EXECUTION_SEQUENCE Phase

**Date:** 2026-01-31
**Status:** PLANNING
**Tier:** 2-3 (Structural / Semantic Interpretation)
**Prerequisites:** C840 (paragraph structure), C893 (kernel-operation mapping), C855-C862 (folio-paragraph architecture)

---

## Objective

Determine whether paragraphs within a Currier B folio follow a predictable execution sequence corresponding to procedural phases, or whether they operate as independent parallel programs.

**Core Question:** Is there a "program flow" at the paragraph level - e.g., setup paragraphs → processing paragraphs → completion paragraphs?

---

## Background

### Current Model: PARALLEL_PROGRAMS (C855, C862)

The folio-paragraph architecture phase established:
- Each paragraph introduces 63-85% new vocabulary
- Template model correlation only 0.23
- Verdict: Paragraphs are "independent mini-programs"

**BUT:** This tested vocabulary uniqueness, not operational SEQUENCE. Paragraphs can have unique vocabulary AND follow a predictable phase sequence (like functions in a program that each do different things but execute in order).

### Relevant Constraints

| Constraint | Finding | Relevance |
|------------|---------|-----------|
| C827 | Paragraphs are operational units | Defines analysis granularity |
| C840 | Header-body structure (44.9% HT line 1) | Paragraph internal structure |
| C893 | Kernel signature predicts operation type | Maps k/h/e to operation categories |
| C894 | REGIME_4 recovery concentration | Precision processing signature |
| C556 | Line syntax: SETUP→WORK→CHECK→CLOSE | Line-level precedent for phase structure |

### Brunschwig Alignment Hypothesis

Brunschwig distillation procedures have explicit phases:
1. **Preparation** - Equipment setup, material loading
2. **Heating** - Fire application, temperature management
3. **Processing** - Distillation, phase transitions
4. **Collection** - Product capture, quality verification

If Voynich folios encode procedures, paragraph ordinals may map to these phases.

---

## Research Questions

### Q1: Do kernel signatures vary by paragraph ordinal?

**Hypothesis:** If procedural sequence exists:
- Early paragraphs: Higher k (energy initialization)
- Middle paragraphs: Higher h (phase management)
- Late paragraphs: Higher e (stabilization)

### Q2: Do role compositions vary by paragraph ordinal?

**Hypothesis:** If procedural sequence exists:
- Early: Higher CC (control setup), higher AX (scaffolding)
- Middle: Higher EN (energy operations)
- Late: Higher FL (flow/completion), higher FQ (error handling)

### Q3: Is there a paragraph-position specialization?

**Question:** Do certain paragraph ordinals specialize in specific operations?
- "First paragraphs always do X"
- "Final paragraphs always do Y"
- "Middle paragraphs vary freely"

### Q4: Do sections show different paragraph sequences?

**Hypothesis:** Given section REGIME concentrations:
- BIO (70% REGIME_1, control-heavy): Steeper gradient, more differentiation
- HERBAL_B: Flatter gradient, more parallel
- PHARMA: Output-oriented sequence

### Q5: Does paragraph count predict sequence structure?

**Question:** Do folios with more paragraphs show clearer phase differentiation?
- Many paragraphs (7+): Clear setup/process/cleanup phases
- Few paragraphs (2-3): Compressed or merged phases

---

## Test Design

### Test 1: Kernel Profile Gradient

**Method:**
1. For each B folio, extract paragraphs by ordinal (1, 2, 3, ...)
2. Compute kernel signature per paragraph:
   - k_rate = tokens containing 'k' / total tokens
   - h_rate = tokens containing 'h' / total tokens
   - e_rate = tokens containing 'e' / total tokens
3. Normalize ordinal position (0 = first paragraph, 1 = last paragraph)
4. Test correlation: ordinal vs kernel rates
5. Test gradient: ANOVA or Kruskal-Wallis across ordinal bins

**Expected Results:**

| Outcome | Interpretation |
|---------|----------------|
| k decreasing with ordinal | Energy initialization early, dissipation late |
| h peak at middle ordinals | Phase transitions concentrated in processing |
| e increasing with ordinal | Stabilization concentrates at completion |
| No correlation | Paragraphs are kernel-independent (parallel) |

**Output:** `kernel_gradient.json`

---

### Test 2: Role Composition Gradient

**Method:**
1. For each paragraph, compute role distribution:
   - CC_rate, EN_rate, FL_rate, FQ_rate, AX_rate (using C583 taxonomy)
2. Test correlation: ordinal vs role rates
3. Test gradient: Kruskal-Wallis across ordinal positions

**Expected Results:**

| Outcome | Interpretation |
|---------|----------------|
| CC front-loaded | Control initialization at start |
| EN middle-concentrated | Energy operations in processing phase |
| FL back-loaded | Flow/completion at end |
| FQ back-loaded | Error handling before termination |
| Uniform distributions | Roles are position-independent (parallel) |

**Output:** `role_gradient.json`

---

### Test 3: First vs Last Paragraph Contrast

**Method:**
1. Extract all "first paragraphs" (ordinal = 1) and "last paragraphs" (ordinal = max)
2. Compare distributions:
   - Kernel signatures (k, h, e)
   - Role compositions (CC, EN, FL, FQ, AX)
   - HT density (header signature)
   - LINK density (monitoring intensity)
   - Mean token count (paragraph size)
3. Statistical tests: Mann-Whitney U, chi-square

**Expected Results:**

| Outcome | Interpretation |
|---------|----------------|
| Significant differences | First/last have distinct functions |
| No differences | Paragraph position doesn't determine function |

**Output:** `first_last_contrast.json`

---

### Test 4: FQ Recovery Distribution

**Method:**
1. Compute FQ density per paragraph (FQ tokens / total tokens)
2. Map FQ to ordinal position
3. Test: Do certain ordinals concentrate error handling?
4. Cross-reference with C894 (REGIME_4 recovery specialization)

**Expected Results:**

| Outcome | Interpretation |
|---------|----------------|
| FQ concentrated late | Error handling before termination |
| FQ concentrated early | Verification before processing |
| FQ uniform | Recovery distributed throughout |
| FQ peaks at middle | Error handling during risky processing |

**Output:** `fq_distribution.json`

---

### Test 5: Section-Specific Sequence Patterns

**Method:**
1. Segment folios by section (BIO, HERBAL_B, PHARMA, COSMO)
2. Repeat Tests 1-4 within each section
3. Test section × ordinal interaction (2-way ANOVA)

**Expected Results:**

| Section | Expected Pattern | Rationale |
|---------|------------------|-----------|
| BIO | Strong gradient (control-heavy) | 70% REGIME_1, needs setup |
| HERBAL_B | Moderate gradient | Mixed REGIME, diverse procedures |
| PHARMA | Completion-focused gradient | Output-oriented, collection emphasis |
| COSMO | Weak/no gradient | Different domain, may not follow procedure model |

**Output:** `section_patterns.json`

---

### Test 6: Brunschwig Phase Mapping

**Method:**
1. Define Brunschwig phase signatures from BRSC:
   - SETUP: Low energy operations, high scaffolding
   - HEATING: High k, elevated hazard exposure
   - PROCESSING: High h, phase transitions
   - COLLECTION: High e, stabilization, output marking
2. Classify each paragraph by best-fit phase
3. Test: Does phase assignment follow ordinal order?
4. Compute sequence adherence rate

**Expected Results:**

| Outcome | Interpretation |
|---------|----------------|
| >70% adherence to SETUP→HEATING→PROCESSING→COLLECTION | Strong procedural correspondence |
| 50-70% adherence | Partial correspondence, some flexibility |
| <50% adherence | No fixed sequence, parallel programs confirmed |

**Output:** `brunschwig_phase_mapping.json`

---

### Test 7: Paragraph Transition Grammar

**Method:**
1. For consecutive paragraph pairs (P_n, P_n+1), compute:
   - Kernel signature transition (e.g., HIGH_K → HIGH_E)
   - Role composition transition (e.g., EN-heavy → FL-heavy)
   - Operation type transition (from C893 mapping)
2. Build transition matrix
3. Test for structure: chi-square, mutual information
4. Identify preferred and disfavored transitions

**Expected Results:**

| Outcome | Interpretation |
|---------|----------------|
| Structured transitions | Grammar governs paragraph order |
| Random transitions | Paragraphs are independent |
| Disfavored transitions exist | "Forbidden sequences" at paragraph level |

**Output:** `paragraph_transitions.json`

---

### Test 8: Paragraph Count Effect

**Method:**
1. Bin folios by paragraph count: Low (2-4), Medium (5-7), High (8+)
2. Within each bin, compute gradient strength (correlation magnitude)
3. Test: Does higher paragraph count enable clearer phase separation?

**Expected Results:**

| Outcome | Interpretation |
|---------|----------------|
| High count = stronger gradient | More paragraphs = more phase differentiation |
| No effect | Phase structure independent of paragraph count |
| Low count = stronger gradient | Fewer paragraphs = more concentrated phases |

**Output:** `paragraph_count_effect.json`

---

## Success Criteria

| Level | Criteria | Implication |
|-------|----------|-------------|
| **STRONG** | 5+ tests show significant ordinal effects | Procedural sequence confirmed |
| **MODERATE** | 3-4 tests show significant effects | Partial sequence, some parallel structure |
| **WEAK** | 1-2 tests show effects | Minimal sequence, predominantly parallel |
| **NULL** | 0 tests show effects | PARALLEL_PROGRAMS model confirmed absolutely |

**Statistical thresholds:**
- Correlation: |r| >= 0.25, p < 0.05
- ANOVA/Kruskal-Wallis: p < 0.05, effect size >= 0.1
- Chi-square: p < 0.05
- Adherence rates: vs null model baseline

---

## Potential Constraints

Depending on results, this phase could establish:

| Finding | Constraint |
|---------|------------|
| Kernel gradient exists | **C9XX:** Paragraph ordinal predicts kernel signature (k decreasing, e increasing) |
| Role gradient exists | **C9XX:** Paragraph ordinal predicts role composition |
| First/last distinct | **C9XX:** First and final paragraphs have distinct operational signatures |
| Section patterns differ | **C9XX:** Section-specific paragraph sequence profiles |
| Brunschwig phases map | **C9XX:** Paragraph ordinals correspond to Brunschwig procedural phases |
| Transitions structured | **C9XX:** Paragraph transition grammar (preferred/disfavored sequences) |

---

## Data Dependencies

| Source | Use |
|--------|-----|
| data/voynich_transcript.csv | B tokens with folio/paragraph/line info |
| scripts/voynich.py | Morphology extraction, role classification |
| context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml | Role taxonomy (C583) |
| phases/B_CONTROL_FLOW_SEMANTICS/results/ | Kernel semantics, operation mapping |
| data/brunschwig_curated_v3.json | Phase definitions (if Test 6) |

---

## Scripts

| Script | Test | Output |
|--------|------|--------|
| 01_kernel_gradient.py | Test 1 | kernel_gradient.json |
| 02_role_gradient.py | Test 2 | role_gradient.json |
| 03_first_last_contrast.py | Test 3 | first_last_contrast.json |
| 04_fq_distribution.py | Test 4 | fq_distribution.json |
| 05_section_patterns.py | Test 5 | section_patterns.json |
| 06_brunschwig_mapping.py | Test 6 | brunschwig_phase_mapping.json |
| 07_paragraph_transitions.py | Test 7 | paragraph_transitions.json |
| 08_paragraph_count_effect.py | Test 8 | paragraph_count_effect.json |
| 09_integrated_verdict.py | Synthesis | paragraph_sequence_verdict.json |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Sparse data (few paragraphs per folio) | Use normalized ordinals, pool across folios |
| Section confound | Test within-section and control for section |
| Overlap with C855-C862 | Focus on OPERATIONAL sequence, not vocabulary |
| Re-deriving "paragraphs are units" | Test SEQUENCE specifically, not unit-hood |

---

## Relationship to Existing Work

| Prior Phase | Relationship |
|-------------|--------------|
| FOLIO_PARAGRAPH_ARCHITECTURE | Tests vocabulary independence; this tests operational sequence |
| B_CONTROL_FLOW_SEMANTICS | Provides kernel semantics; this applies to paragraph level |
| REVERSE_BRUNSCHWIG_TEST | Tests domain correspondence; this tests format at paragraph scale |
| PARAGRAPH_INTERNAL_PROFILING | Tests within-paragraph structure; this tests between-paragraph order |

---

## Expected Timeline

1. **Data preparation:** Extract paragraph-level features (kernel, role, position)
2. **Core tests (1-4):** Gradient and contrast analyses
3. **Extended tests (5-8):** Section patterns, Brunschwig mapping, transitions
4. **Synthesis:** Integrated verdict and constraint documentation

---

## Files

```
phases/PARAGRAPH_EXECUTION_SEQUENCE/
├── README.md (this file)
├── scripts/
│   ├── 01_kernel_gradient.py
│   ├── 02_role_gradient.py
│   ├── 03_first_last_contrast.py
│   ├── 04_fq_distribution.py
│   ├── 05_section_patterns.py
│   ├── 06_brunschwig_mapping.py
│   ├── 07_paragraph_transitions.py
│   ├── 08_paragraph_count_effect.py
│   └── 09_integrated_verdict.py
└── results/
    └── (generated outputs)
```
