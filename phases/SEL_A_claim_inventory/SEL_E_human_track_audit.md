# SEL-E: Human-Track Minimality & Necessity Audit

**Phase:** SEL-E (Self-Evaluation - Human-Track Audit)
**Date:** 2026-01-05
**Authority Scope:** OPS ONLY
**Status:** DESTRUCTIVE AUDIT (no repairs)

---

## SECTION A — HUMAN-TRACK CLAIM INVENTORY

### Claims from OPS Documentation

| ID | Claim | Original Tier | Source |
|----|-------|---------------|--------|
| HT-01 | ~40,000 occurrences (33.4% of corpus), ~11,000 types | Tier 2 | UTC |
| HT-02 | Zero forbidden seam presence (0/35 seams) | Tier 2 | NESS |
| HT-03 | 80.7% section-exclusive vocabulary | Tier 2 | MCS |
| HT-04 | 9.1% vocabulary overlap first/last third | Tier 2 | UTC |
| HT-05 | Mean hazard distance 4.84 (vs 2.5 expected) | Tier 2 | NESS |
| HT-06 | Morphologically distinct from operational grammar | Tier 2 | MCS |
| HT-07 | 99.6% LINK-proximal | Tier 2 | HTCS |
| HT-08 | Single unified layer (not multiple systems) | Tier 2 | NESS |
| HT-09 | 2.16x line-initial enrichment | Tier 2 | UTC |
| HT-10 | 1.48x folio-start enrichment | Tier 2 | UTC |
| HT-11 | 7 coordinate functions identified | Tier 2 | HTCS |
| HT-12 | Function: navigation/orientation/position encoding | Tier 3 | MCS/HTCS |

---

## SECTION B — EXECUTION TEST RESULTS

### TEST 1: Execution Invariance

| Metric | With Human-Track | Without Human-Track | Difference |
|--------|------------------|---------------------|------------|
| Total tokens | 121,531 | ~80,891 (66.6%) | -33.4% |
| Grammar recognition | 100% | 100% | **NONE** |
| Forbidden violations | 0 | 0 | **NONE** |
| Execution blocking | 0 seams | 0 seams | **NONE** |
| Convergence detection | 100% | 100% | **NONE** |

**VERDICT:** Grammar, hazards, and execution are **INVARIANT** to human-track removal.

This confirms the OPS claim that human-track is non-executive. However, this alone does not establish that human-track has ANY function—it only establishes that it has NO executive function.

---

### TEST 2: Boundary Necessity

| Location | Human-Track Presence | Expected (Random) |
|----------|---------------------|-------------------|
| Forbidden seams (35 total) | **0 (0%)** | ~12 (33%) |
| Adjacent to seams (±3 tokens) | ~12 | ~420 |
| High-constraint zones | **Avoids** (4.84 vs 2.5) | Random (2.5) |

**VERDICT:** Human-track tokens are **ABSENT** from grammar-critical seams.

This is the strongest structural finding. The question is: does absence indicate active avoidance (intentional design) or simply non-overlap of independent vocabularies?

---

## SECTION C — NECESSITY FINDINGS

### Per-Claim Assessment

| ID | Claim | Necessity | Rationale |
|----|-------|-----------|-----------|
| HT-01 | 33.4% of corpus | **STRUCTURALLY NEUTRAL** | Count is observable but doesn't imply function |
| HT-02 | Zero seam presence | **STRUCTURALLY NECESSARY** | Cannot be explained by random vocabulary |
| HT-03 | 80.7% section-exclusive | **STRUCTURALLY NEUTRAL** | Consistent with scribal drift |
| HT-04 | 9.1% vocabulary overlap | **STRUCTURALLY NEUTRAL** | Consistent with scribal drift |
| HT-05 | Hazard avoidance (4.84 vs 2.5) | **STRUCTURALLY NECESSARY** | Cannot be explained by random vocabulary |
| HT-06 | Morphologically distinct | **STRUCTURALLY NEUTRAL** | Could be independent vocabulary |
| HT-07 | 99.6% LINK-proximal | **DEPENDS ON LINK DEFINITION** | LINK itself is under audit |
| HT-08 | Single unified layer | **STRUCTURALLY NEUTRAL** | Absence of subdivision ≠ presence of unity |
| HT-09 | 2.16x line-initial | **ELIMINABLE** | Explained by spacing/filler model |
| HT-10 | 1.48x folio-start | **ELIMINABLE** | Explained by spacing/filler model |
| HT-11 | 7 coordinate functions | **OVERFITTING** | Inferred from position, used to explain position |
| HT-12 | Navigation function | **ANALYST-IMPOSED** | Inference layer, not observation |

### Summary

| Status | Count | Claims |
|--------|-------|--------|
| Structurally necessary | 2 | HT-02, HT-05 |
| Depends on other claims | 1 | HT-07 |
| Structurally neutral | 5 | HT-01, HT-03, HT-04, HT-06, HT-08 |
| Eliminable | 2 | HT-09, HT-10 |
| Overfitting/analyst-imposed | 2 | HT-11, HT-12 |

---

## SECTION D — PARSIMONY COMPARISON

### Model 1: Human-Track Navigation Model (OPS)

**Assumptions:**
1. Tokens form a coherent human-facing layer
2. Layer serves navigation/orientation function
3. Section-exclusivity encodes position
4. 7 distinct coordinate functions exist
5. LINK-proximity indicates "waiting phase" marking
6. Hazard avoidance is intentional

**Explains:**
- Zero seam presence (intentional avoidance)
- Hazard distance (intentional avoidance)
- Section exclusivity (position encoding)
- LINK proximity (waiting phase marking)
- Line-initial enrichment (section entry marking)

**Does not explain:**
- Why 33% of corpus needed for navigation
- Why 11,000 distinct types needed
- Why vocabulary drift occurs within "unified layer"

---

### Model 2: Minimal Noise/Artifact Model

**Assumptions:**
1. Tokens are scribal filler/spacing artifacts
2. Vocabulary varies by scribe/section (drift)
3. No intentional function assigned
4. Grammar and hazards are independent vocabulary

**Explains:**
- Section exclusivity (scribal habit drift)
- Vocabulary overlap pattern (temporal drift)
- Line-initial enrichment (spacing after breaks)
- Folio-start enrichment (section markers)
- Length distribution (filler tends similar length)

**Does not explain:**
- Zero seam presence (expected ~33% by chance)
- Hazard avoidance (expected random proximity)

---

### Comparison Table

| Property | Human-Track Model | Noise/Artifact Model |
|----------|-------------------|----------------------|
| Zero seam presence | **EXPLAINS** (intentional) | FAILS (predicts ~33%) |
| Hazard avoidance | **EXPLAINS** (intentional) | FAILS (predicts random) |
| Section exclusivity | EXPLAINS (encoding) | **EXPLAINS** (drift) |
| Vocabulary overlap | EXPLAINS (local codes) | **EXPLAINS** (drift) |
| Line-initial enrichment | EXPLAINS (entry markers) | **EXPLAINS** (spacing) |
| Folio-start enrichment | EXPLAINS (section markers) | **EXPLAINS** (section breaks) |
| 7 coordinate functions | CLAIMS (circular) | **REJECTS** (overfitting) |
| 33% corpus share | CLAIMS (necessary) | **SIMPLER** (no claim) |

### Verdict

**Noise/Artifact Model explains 4/6 core properties.**

**Human-Track Model is required ONLY for:**
1. Zero seam presence
2. Hazard avoidance

These two properties constitute the **minimal structural residue** that cannot be explained by scribal noise.

---

## SECTION E — FAILURE MODES & OVERFITTING

### Circular Assumptions Detected

| Claim | Circularity |
|-------|-------------|
| HT-07: LINK-proximal | "Near LINK" depends on LINK meaning "waiting"; LINK meaning depends on token distribution |
| HT-11: 7 coordinate functions | Inferred from positional patterns; used to explain positional patterns |
| HT-12: Navigation function | Inferred from structural absence (non-executive); used to explain structural presence |

### Analyst Impositions

| Claim | Issue |
|-------|-------|
| "Human-track" terminology | Presupposes human-facing purpose before testing |
| "Navigation scaffolding" | Functional label applied to non-functional evidence |
| "Wait-phase marker" | Assigns meaning to proximity correlation |
| "Coordinate system" | Assigns structure to vocabulary distribution |

### Unfalsifiable Claims

| Claim | Issue |
|-------|-------|
| "Function: position encoding" | Any distribution can be called "position encoding" |
| "Serves operator during waiting" | Cannot be falsified without operator testimony |
| "Expert reference manual design" | Post-hoc rationalization of structural features |

### Anomaly Absorption

The "human-track" category absorbs:
- ALL tokens not in grammar (~40,000 occurrences)
- ALL vocabulary not in 49 instruction classes (~11,000 types)
- 33.4% of entire corpus

This is a **maximal absorption** pattern. Any unexplained token is classified as "human-track" by default.

---

## SECTION F — SEL-E VERDICT

### Test Results Summary

| Test | Result | Impact |
|------|--------|--------|
| T1: Execution Invariance | **INVARIANT** | Human-track is non-executive |
| T2: Boundary Necessity | **ZERO PRESENCE** | Structurally anomalous (cannot be random) |
| T3: Noise Baseline | **2 RESIDUES** | Zero-seam + hazard-avoidance unexplained |
| T4: Parsimony | **PARTIAL** | 4/6 properties explained by simpler model |
| T5: Overfitting | **DETECTED** | 3 circular assumptions, 4 analyst impositions |

---

### Claims That SURVIVE

| ID | Claim | Revised Status |
|----|-------|----------------|
| HT-02 | Zero forbidden seam presence (0/35) | **Tier 2 (STRUCTURAL)** |
| HT-05 | Hazard avoidance (4.84 vs 2.5) | **Tier 2 (STRUCTURAL)** |

These two properties are **structurally anomalous** and cannot be explained by random vocabulary or scribal drift. They require some form of avoidance mechanism.

---

### Claims DOWNGRADED

| ID | Claim | Revised Status | Reason |
|----|-------|----------------|--------|
| HT-03 | Section exclusivity | **Tier 3** | Explained by scribal drift |
| HT-04 | Vocabulary overlap | **Tier 3** | Explained by scribal drift |
| HT-06 | Morphologically distinct | **Tier 3** | Independent vocabulary, no function implied |
| HT-07 | LINK-proximal | **Tier 3** | Depends on LINK definition (under audit) |
| HT-08 | Single unified layer | **Tier 3** | Absence of subdivision ≠ presence of unity |
| HT-09 | Line-initial enrichment | **Tier 3** | Explained by spacing model |
| HT-10 | Folio-start enrichment | **Tier 3** | Explained by spacing model |

---

### Claims REMOVED

| ID | Claim | Reason |
|----|-------|--------|
| HT-11 | 7 coordinate functions | **OVERFITTING** — inferred from position, used to explain position |
| HT-12 | Navigation/orientation function | **ANALYST-IMPOSED** — functional label on non-functional evidence |

---

### Final Tier Status

**Prior:** Human-track layer = Tier 2 (Structural Inference)

**Revised:** Human-track layer = **Tier 3 (Speculative Alignment)**

**Rationale:**
- Only 2/12 claims survive as Tier 2
- Core functional claims (navigation, coordination) are analyst impositions
- 7 coordinate functions are overfitting artifacts
- Most properties explained by simpler model (scribal drift + spacing)

---

### Minimal Structural Description

The tokens outside the 49-class grammar:
1. **Never appear at forbidden seams** (0/35) — STRUCTURAL
2. **Avoid hazard-involved tokens** (4.84 vs 2.5) — STRUCTURAL
3. **Show scribal drift patterns** — NON-FUNCTIONAL

This is the **minimal necessary characterization**. No navigation, coordination, or human-facing function needs to be invoked.

---

### Alternative Label

Replace "Human-Track Coordinate System" with:

> **"Non-Grammar Vocabulary Layer"** — tokens outside the 49-class grammar that structurally avoid forbidden seams and hazard zones, showing scribal drift patterns.

This label:
- Makes no functional claims
- Preserves the two structural findings
- Eliminates analyst-imposed interpretation

---

## Summary Statement

> **The "human-track" layer as CHARACTERIZED (navigation, coordination, 7 functions) does not survive audit.**
>
> **The "human-track" layer as OBSERVED (seam avoidance, hazard avoidance) does survive as structural anomaly.**
>
> Required changes:
> - Downgrade human-track layer from Tier 2 to Tier 3
> - Remove "7 coordinate functions" claim (overfitting)
> - Remove "navigation/coordination" functional labels (analyst-imposed)
> - Rename to "Non-Grammar Vocabulary Layer"
> - Preserve only: zero-seam presence + hazard avoidance

---

*SEL-E complete. Functional claims collapsed. Structural residue preserved.*

*Generated: 2026-01-05*
