# Speculative Interpretation Summary

**Status:** SPECULATIVE | **Tier:** 3-4 | **Version:** 4.29

---

## Purpose

This document consolidates all Tier 3-4 interpretations into a single reference. It is designed for external AI context loading.

**Critical:** Everything in this document is NON-BINDING speculation. It is consistent with the structural evidence but NOT proven by it. Treat as discardable if contradicted by new evidence.

---

## Frozen Conclusion (Tier 0 - Context Only)

> The Voynich Manuscript's Currier B text encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

This structural finding is FROZEN. The interpretations below attempt to explain what this structure might have been FOR.

---

## 0. APPARATUS-CENTRIC SEMANTICS (CCM Phase)

### Tier 3: Core Finding

> **The manuscript encodes the operational worldview of a controlled apparatus, not the descriptive worldview of a human observer.**

All recoverable semantics are those available to the apparatus and its control logic: states, transitions, risks, recoveries. All referential meaning (materials, plants, devices) is supplied externally by trained human operators.

### Token Decomposition (Complete)

Every Currier A/B token decomposes into four functional components:

```
TOKEN = PREFIX   → material-behavior class (what kind of thing)
      + SISTER   → operational mode (how carefully)
      + MIDDLE   → variant discriminator (which specific variant)
      + SUFFIX   → decision archetype (what decision is needed)
```

### Component-to-Class Mapping

| Component | Encodes | Classes | Evidence |
|-----------|---------|---------|----------|
| **PREFIX** | Material-behavior | 4 classes (M-A/B/C/D) | Grammar roles, enrichment |
| **SISTER** | Operational mode | 2 modes (precision/tolerance) | C412 anticorrelation |
| **MIDDLE** | Variant identity | ~1,184 discriminators | 80% prefix-exclusive |
| **SUFFIX** | Decision archetype | 12 archetypes (D1-D12) | A/B enrichment patterns |

### Material-Behavior Classes

| Class | Phase | Composition | Prefixes | Example Role |
|-------|-------|-------------|----------|--------------|
| **M-A** | Mobile | Distinct | ch, sh, qo | Energy operations |
| **M-B** | Mobile | Homogeneous | ok, ot | Routine operations |
| **M-C** | Stable | Distinct | ct | Registry reference |
| **M-D** | Stable | Homogeneous | ol, da | Structural anchor |

### Operational Modes (Sister Pairs)

| Sister | Mode | Escape Density | Meaning |
|--------|------|----------------|---------|
| **ch** (vs sh) | Precision | 7.1% | Tight tolerances, fewer recovery options |
| **sh** (vs ch) | Tolerance | 24.7% | Loose tolerances, more escape routes |

Statistical validation: rho = -0.326, p = 0.002 (C412)

### MIDDLE Frequency Structure

| Tier | MIDDLEs | Usage | Properties |
|------|---------|-------|------------|
| **Core** (top 30) | 30 | 67.6% | Mode-flexible, section-stable, cross-class |
| **Tail** | 1,154 | 32.4% | Mode-specific, hazard-concentrated, class-exclusive |

Key findings:
- Rare MIDDLEs cluster in high-hazard contexts (rho=-0.339, p=0.0001)
- Core MIDDLEs are 15x more rank-stable across sections
- Distribution is Zipf-like (s=1.26) with cutoff — bounded expert vocabulary

### Semantic Ceiling

**Recoverable internally (role-level):**
- What material-behavior class is involved
- What operational mode applies
- Which variant within the class
- What decision archetype is needed

**Irrecoverable internally (entity-level):**
- Specific substances, plants, or minerals
- Specific apparatus or devices
- Specific procedures or recipes
- What any token "means" in natural language

This is the terminal internal semantic layer. The boundary is by design.

### Why This Matters

The apparatus-centric perspective explains:
- Why vocabulary is universal across sections (comparability over specificity)
- Why no quantities appear (apparatus tracks state, not magnitude)
- Why illustrations look botanical but grammar does not (images are human context; text is control logic)
- Why ~1,184 MIDDLEs exist (expert recognition vocabulary, not linguistic labels)

---

## 0.A. CURRIER A COGNITIVE INTERFACE (PCC Phase) - NEW in v4.24

### Tier 3: Core Finding

> **Currier A is designed for expert navigation without meaning - a human-facing complexity-frontier registry with cognitive affordances optimized for working memory.**

This extends the Complexity-Frontier Registry model with empirical characterization of how humans would interact with the system.

### Closure State Architecture

Boundary tokens are **closure states**, not delimiters:

| Property | Finding |
|----------|---------|
| Function | Return vocabulary to neutral, maximally compatible state |
| -y ending | 36.5% at final position |
| -n ending | 15.2% at final position |
| -m ending | 12.2% at final position |
| Uniformity | NOT adjusted to entry complexity (no complexity correlation) |

Closure markers signal that an entry has emitted all discriminating vocabulary, enabling cognitive bracketing without punctuation.

### Working-Memory Chunks

Adjacent entries form **working-memory-sized clusters**:

| Metric | Value |
|--------|-------|
| Within-cluster coherence | 2.14x vs cross-cluster |
| Median cluster size | 2 |
| Max cluster size | 7 (working memory limit) |
| Cohen's d | 1.44 (large effect) |

Clusters are INVARIANT under folio reordering - this is local structure, not global organization.

### Singleton Isolation

Entries not in clusters (singletons) show distinct properties:

| Property | Clustered | Singleton |
|----------|-----------|-----------|
| Hub overlap | 0.850 | 0.731 |
| Incompatibility density | 0.979 | 0.986 |

Singletons are **deliberate isolation points**, not noise - entries with unique discrimination profiles that cannot cluster.

### A-AZC Breadth Interface

Entry vocabulary composition predicts downstream AZC compatibility:

| Factor | Effect on Breadth | p-value |
|--------|-------------------|---------|
| Hub-dominant | Broader | - |
| Tail-dominant | Narrower | <0.0001 |
| Closure present | Slightly broader | 0.003 |
| Non-prefix opener | Narrower | <0.0001 |

**Strong asymmetry:** Universal-dominant entries have 0.58 breadth; Tail-dominant entries have 0.31 breadth.

### The Navigation Model (Tier 3)

An expert using Currier A would:
1. Recognize entry boundaries via closure morphology
2. Process clusters as working-memory chunks
3. Use adjacency similarity for local orientation
4. Treat singletons as special/isolated items
5. Navigate via marker class organization

This is interface characterization, not semantic mapping. The system supports expert navigation without encoding meaning.

### What This Does NOT Claim

- ❌ Entries have semantic content
- ❌ Closure markers are adaptive signals
- ❌ Working-memory structure implies temporal ordering
- ❌ A-AZC breadth enables material identification

### Cross-References

| Constraint | Finding |
|------------|---------|
| C233 | LINE_ATOMIC (base for closure model) |
| C346 | Sequential coherence 1.20x |
| C424 | Clustered adjacency |
| C422 | DA articulation |

**Source:** phases/POST_CLOSURE_CHARACTERIZATION/PCC_SUMMARY_REPORT.md

---

## I. Human Track (HT) Interpretation

### Tier 2: Core Finding (v2.13)

> **HT is a scalar signal of required human vigilance that varies with content characteristics, not with codicology, singular hazards, or execution failure modes.**

HT functions as **anticipatory vigilance** - preparing the human operator for upcoming demands rather than reacting to past events (C459).

### What HT Is (Structural, Confirmed)

- HT **anticipates B stress** at quire level (r=0.343, p=0.0015)
- HT is **content-driven**, not production-driven (no quire boundary alignment)
- HT is **front-loaded** in the manuscript (decreasing trend)
- HT is **coarse**, distributed, and probabilistic

### What HT Is NOT

- HT does **not** say *why* attention is needed
- HT does **not** isolate catastrophic cases
- HT does **not** encode "danger zones"
- HT does **not** react to error or failure

### Tier 3: Dual-Purpose Attention Mechanism

HT may serve **two complementary functions**:

1. **Anticipatory vigilance** during high-demand phases
2. **Guild training** in the art of the written form

This is NOT "doodling" or "scribbling" - the evidence shows deliberate skill acquisition.

### Supporting Evidence (Tier 2 facts)

| Evidence | Finding | Implication |
|----------|---------|-------------|
| Rare grapheme engagement | 7.81x over-representation | Practicing difficult forms |
| Run structure | CV=0.35 (fixed-block range) | Deliberate practice blocks |
| Boundary-pushing forms | 24.5% | Exploring morphological limits |
| Family rotation | Change rate 0.71 | Systematic curriculum |
| Hazard avoidance | 0/35 at forbidden seams | Stop writing when attention demanded |
| Phase synchronization | V=0.136 | Writing tracks procedural phase |
| Anticipatory correlation | r=0.236 (HT before B) | HT precedes stress, not follows |

### System-Specific Anchoring

| System | Anchoring Pressure | Pattern |
|--------|-------------------|---------|
| Currier A | Registry layout | Entry-boundary aligned |
| Currier B | Temporal/attentional context | Waiting-profile correlated |
| AZC | Diagram geometry | Label-position synchronized |

### Historical Parallel

Medieval apprentice work-study combination. Productive use of operational waiting periods for skill development. Silent activity appropriate for apparatus monitoring.

---

## I.B. Four-Layer Responsibility Model (v2.13)

### Tier 2: Structural Finding

The manuscript distributes responsibility between system and human across four layers:

| Layer | Role | What It Handles |
|-------|------|-----------------|
| **Currier B** | Constrains you | Execution grammar, safety envelope |
| **Currier A** | Discriminates for you | Fine distinctions at complexity frontier |
| **AZC** | Gates you | Phase-indexed decision legality, compatibility filtering |
| **HT** | Prepares you | Anticipatory vigilance signal |

### Design Freedom vs Constraint (C458)

B programs exhibit **asymmetric design freedom**:

| Dimension | Allowed to Vary? | Evidence |
|-----------|-----------------|----------|
| Hazard exposure | NO | CV = 0.11 (clamped) |
| Intervention diversity | NO | CV = 0.04 (clamped) |
| Recovery operations | YES | CV = 0.82 (free) |
| Near-miss handling | YES | CV = 0.72 (free) |

### Tier 3: Interpretive Framing

The right mental model is not "What does this page tell me to do?" but:

> **"How much of the problem is the system handling for me here, and how much vigilance am I responsible for?"**

This suggests the manuscript is a **manual of responsibility allocation** rather than a manual of actions. The grammar guarantees safety by construction; the system guarantees risk will not exceed bounds; HT signals when human attention is required.

---

## I.C. AZC as Decision-Point Grammar (C437-C444)

### Tier 2: Structural Findings

AZC serves as a **decision-point grammar** that transforms static A-registry entries into phase-gated choice nodes:

| Finding | Evidence | Constraint |
|---------|----------|------------|
| Folios maximally orthogonal | Jaccard = 0.056 | C437 |
| Practically complete basis | 83% per-folio coverage | C438 |
| Folio-specific HT profiles | 18pp escape variance | C439 |
| Uniform B sourcing | 34-36 folios per B | C440 |
| Vocabulary-activated constraints | 49% A-types in 1 folio | C441 |
| Compatibility filter | 94% unique vocabulary | C442 |

### Tier 3: Operational Interpretation

**Core insight:** AZC converts static Currier A entries into phase-gated decision points.

| System | Function | Type |
|--------|----------|------|
| Currier A | WHAT exists | Static registry |
| Currier B | HOW to proceed | Procedural sequence |
| AZC | WHEN to decide | Decision grammar |

### Phase-to-Workflow Mapping

AZC positional grammar maps to operational workflow:

| Position | Workflow Phase | Escape Rate | Meaning |
|----------|----------------|-------------|---------|
| C | Setup/Loading | 1.4% | Entry constrained, errors fixable |
| P | Active work | 11.6% | Recovery permitted, intervention legal |
| R1→R2→R3 | Progression | 2.0%→1.2%→0% | Options narrowing, committing |
| S | Collection/Exit | 0-3.8% | Locked, must accept outcome |

In reflux distillation: early phases are reversible, late phases are committed. AZC encodes this grammatically.

### Compatibility Filter Mechanism (v4.5 - REFINED)

AZC compatibility operates at the **Currier A constraint-bundle level**, not at execution level.

**Precise Definition (C442 refined):**
> Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both.

**Empirical Test (2026-01-12):**

| Metric | Value |
|--------|-------|
| Total folio pairs | 435 |
| Bridged pairs | 390 (89.7%) |
| **Unbridged pairs** | **45 (10.3%)** |
| Graph connectivity | FULLY_CONNECTED |

**Family-Level Coherence:**

| Family Type | % Unbridged | Interpretation |
|-------------|-------------|----------------|
| Within-Zodiac | **0.0%** | Interchangeable discrimination contexts |
| Within-A/C | **14.7%** | True fine-grained alternatives |
| Cross-family | **11.3%** | Partial overlap |

**Key Corollaries:**
- Folios are NOT execution-exclusive (C440 still holds)
- Folios are NOT globally incompatible
- Incompatibility exists only at **specification time**
- Disallowed combinations leave no trace—they simply never occur

**f116v Structural Isolation:**
f116v shares NO bridging tokens with most other folios—it defines a discrimination profile that cannot be jointly specified with most other constraint bundles.

**Why AZC is large:** It enumerates all compatibility classes. Each folio = a different set of legal A-bundle combinations.

### Ambient Constraint Activation

AZC is not selected explicitly. Constraints activate automatically:
- **Core vocabulary** (20+ folios) → broadly legal
- **Specialized vocabulary** (1-3 folios) → activates specific profile
- **Position (C→P→R→S)** → determines phase-specific rules

The vocabulary you use determines which constraints apply.

### Zodiac vs A/C as Perceptual Discrimination Regimes (v4.3 - VALIDATED)

| Family | Scaffold | HT Oscillation | Interpretation |
|--------|----------|----------------|----------------|
| Zodiac (15 folios) | Uniform (same 12x) | 0.060 (low) | Coarse discrimination, sustained flow |
| A/C (21 folios) | Varied (unique each) | 0.110 (high) | Fine discrimination, punctuated checkpoints |

**Final Interpretation (Tier 3 - VALIDATED):**

> Zodiac and A/C AZC families correspond to regimes of perceptual discrimination complexity rather than operational difficulty. Zodiac contexts permit coarse categorization and sustained attentional flow, while A/C contexts require finer categorical distinctions, producing punctuated attentional checkpoints reflected in higher HT oscillation. Execution grammar absorbs this difference, resulting in no detectable change in behavioral brittleness or CEI.

**Empirically Tested (2026-01-11):**

| Test | Result |
|------|--------|
| MIDDLE Discrimination Gradient | WEAK SUPPORT (5/15 prefixes) |
| Residual Brittleness | FAILED (effect is PREFIX, not regime) |
| Universal MIDDLE Control | **PASSED** (58.7% vs 64.8%) |
| Family Escape Transfer | PARTIAL (r=0.265) |
| **HT Oscillation Density** | **PASSED** (A/C 80% higher) |

**The Coherent Explanatory Axis:**

| Layer | Zodiac | A/C |
|-------|--------|-----|
| Currier A | Coarse categories | Fine distinctions |
| AZC | Uniform scaffolds | Varied scaffolds |
| HT | Sustained flow | Punctuated checkpoints |
| Currier B | Same difficulty | Same difficulty |
| CEI | Same effort | Same effort |

> **Where discrimination is fine, attention becomes punctuated; where discrimination is coarse, attention can flow.**

**Falsified Variants:**
- Calendar/seasonal encoding ❌
- Parallel batch management ❌ (HT reversed)
- Regime-dependent execution difficulty ❌
- Family affects CEI or recovery ❌

See [efficiency_regimes.md](efficiency_regimes.md) for full test results.

### PREFIX Sub-Families via AZC Clustering (v4.4)

AZC folio co-occurrence can reveal sub-families within PREFIX classes that morphology alone doesn't show.

**Key Finding:** The y- PREFIX exhibits a **FAMILY_SPLIT**:

| Cluster | Family Bias | Sample Tokens | Shared Folios |
|---------|-------------|---------------|---------------|
| 66 | 85.7% Zodiac | ytaly, opaiin, alar | f72v1, f73v |
| 61 | 69.7% A/C | okeod, ykey, ykeeody | f69v, f73v |

**Interpretation:** y- does not behave like a single material class. It spans both discrimination regimes, suggesting:

1. **y- encodes something orthogonal to the Zodiac/A-C axis**
2. **y- may be a modifier or state marker** rather than a material class
3. **Regime-independent function** - applies in both coarse and fine discrimination contexts

**Contrast with regime-committed prefixes:**
- qo- (71.9% A/C) → tied to fine discrimination
- or- (58.3% Zodiac) → tied to coarse discrimination
- y- (split) → **regime-independent**

This strengthens the interpretation that PREFIX encodes more than material class - some prefixes encode functional roles that apply across discrimination regimes.

### Summary

> **AZC is a decision-point grammar that transforms static material references into phase-gated choice nodes, enforces compatibility between materials and operations, and encodes when intervention is legal versus when outcomes must be accepted.**

---

## I.D. MIDDLE Atomic Incompatibility Layer (C475) - NEW in v4.6

### Tier 2: Core Finding

> **MIDDLE-level compatibility is extremely sparse (4.3% legal), forming a hard incompatibility lattice. This is the atomic discrimination layer—everything above it (A entries, AZC folios, families, HT) is an aggregation of this graph.**

### Evidence (middle_incompatibility.py, 2026-01-12)

| Metric | Value |
|--------|-------|
| Total MIDDLEs | 1,187 |
| Total possible pairs | 703,891 |
| **Legal pairs** | **30,394 (4.3%)** |
| **Illegal pairs** | **673,342 (95.7%)** |
| Connected components | 30 |
| Largest component | 1,141 (96% of vocabulary) |
| Isolated MIDDLEs | 20 |
| Robustness (2-line check) | 97.3% overlap |

### Key Structural Objects

**1. Universal Connector MIDDLEs** ('a', 'o', 'e', 'ee', 'eo')
- Compatibility basis elements
- Bridge otherwise incompatible regimes
- "Legal transition anchors"
- Dominate strongest bridges (71, 50, 49 co-occurrences)

**2. Isolated MIDDLEs** (20 total)
- Hard decision points
- "If you specify this, you cannot specify anything else"
- Pure regime commitment
- Likely tail MIDDLEs, highly prefix-exclusive

**3. PREFIX = soft prior, MIDDLE = hard constraint**
- Within-PREFIX legal: 17.39%
- Cross-PREFIX legal: 5.44%
- Ratio: 3.2x (PREFIX increases odds, MIDDLE applies near-binary exclusions)

### Graph Structure

The incompatibility graph has:
- **30 connected components** (discrimination regimes)
- **One giant component** (1,141 MIDDLEs, 96%)
- Giant component ≠ free mixing — most pairs within it are still forbidden
- **Navigation requires changing regime step-by-step**

> The space is globally navigable, but only by changing discrimination regime step-by-step.

### Reconciliation with Prior Structure

| Prior Finding | Resolution |
|---------------|------------|
| C293 (MIDDLE is primary discriminator) | **Quantified**: 95.7% exclusion rate |
| C423 (PREFIX-bound vocabulary) | PREFIX is first partition, MIDDLE is sharper second |
| Why so many AZC folios? (C437-C442) | AZC = projections of sparse graph onto positional scaffolds |
| HT anticipatory function (C459, C461) | HT ≈ local incompatibility density (now testable) |
| f116v folio isolation | **Explained by data sparsity** (2 words), not MIDDLE incompatibility |

### Tier 3: Interpretive Implications

**Why This Matters:**

This explains several long-standing puzzles at once:
- Why AZC folios had to be so numerous (enumerating compatibility classes)
- Why Currier A appears both flat AND highly constrained
- Why HT tracks discrimination pressure rather than execution danger
- Why vocabulary sharing ≠ combinability

**What Kind of System This Is:**

> A globally navigable but locally forbidden discrimination space — the strongest internal explanation yet of why the Voynich Manuscript looks the way it does without invoking semantics.

**Bayesian Modeling Progress:**

1. ~~**Latent Discrimination Axes**~~ — **DONE: K=128 for 97% AUC** (see I.E below)
2. ~~**Probabilistic A Bundle Generator**~~ — **DONE: 9/14 metrics FAIL** (see I.F below)
3. ~~**Coverage Optimality**~~ — **DONE: 100% coverage, 22.3% hub savings** (see I.G below)
4. ~~**HT Variance Decomposition**~~ — **DONE: R²=0.28, TAIL PRESSURE dominant** (see I.H below)
5. ~~**Temporal Coverage Trajectories**~~ — **DONE: STRONG SCHEDULING with pedagogical pacing** (see I.I below)

### I.E. Latent Discrimination Dimensionality (v4.7) - NEW

**Question:** How many latent "axes of distinction" are needed to explain the MIDDLE incompatibility graph?

**Answer:** ~128 dimensions for 97% AUC. The discrimination space is HIGH-DIMENSIONAL.

| K | Cross-Validation AUC |
|---|----------------------|
| 2 | 0.869 |
| 4 | 0.870 |
| 8 | 0.869 |
| 16 | 0.886 |
| 32 | 0.900 |
| 64 | 0.923 |
| 128 | **0.972** |

**Key Findings:**

1. **Not low-rank** — The expert hypothesis of "2-4 binary switches" is rejected
2. **Axes don't align with PREFIX** — Max separation 0.011 (very weak)
3. **Axes don't align with characters** — Max correlation 0.138 (weak)
4. **Axes don't align with length** — Max correlation 0.160 (weak)

**Interpretation (Tier 3):**

The 128 latent axes represent:
- NOT simple features (prefix, characters, length)
- Emergent compatibility structure learned from co-occurrence
- Each MIDDLE carries ~128 bits of discriminatory information

> **The MIDDLE vocabulary is not a categorization system with a few dimensions. It is a rich feature space where each variant has a unique 128-dimensional fingerprint.**

**What This Means for Generative Modeling:**

Any generator that reproduces Currier A must implicitly encode these ~128 dimensions. This rules out:
- Simple rule-based generators
- Low-parameter Markov models
- "Random but constrained" generation

**Hub Confirmation:**

The top-5 MIDDLEs by degree (weighted co-occurrence) match prior finding:
| MIDDLE | Degree |
|--------|--------|
| 'a' | 2047 |
| 'o' | 1870 |
| 'e' | 1800 |
| 'ee' | 1625 |
| 'eo' | 1579 |

These universal connectors remain valid; they simply have high compatibility across all 128 dimensions.

### I.F. Bundle Generator Diagnostic (v4.8) - NEW

**Question:** Can a generator constrained only by MIDDLE incompatibility + line length + PREFIX priors reproduce Currier A entries?

**Answer:** NO. 9/14 diagnostic metrics fail. Residuals reveal additional structure.

**Generator Configuration:**
- Included: MIDDLE incompatibility, line length, PREFIX priors
- Excluded: marker exclusivity, section conditioning, AZC info, adjacency coherence

**Diagnostic Results:**

| Metric | Real | Synthetic | Verdict |
|--------|------|-----------|---------|
| lines_zero_mixing | 61.5% | 2.7% | **FAIL** |
| pure_block_frac | 46.9% | 2.7% | **FAIL** |
| universal_middle_frac | 31.6% | 56.7% | **FAIL** |
| unique_middles | 1187 | 330 | **FAIL** |
| lines_with_repetition | 96.4% | 63.9% | **FAIL** |
| prefixes_per_line | 1.78 | 4.64 | **FAIL** |
| line_length (mean/median) | 19.2/8.0 | 20.0/8.0 | OK |

**Residual Interpretation (New Structure):**

1. **PREFIX COHERENCE** — Lines prefer single PREFIX family (not just compatibility)
2. **TAIL FORCING** — Real A systematically uses rare MIDDLEs
3. **REPETITION IS STRUCTURAL** — 96.4% of lines have repetition (deliberate)
4. **HUB RATIONING** — Universal MIDDLEs used sparingly (31.6% vs 56.7%)

**Interpretation (Tier 3):**

> **Incompatibility + priors are NECESSARY but NOT SUFFICIENT.** The generator reveals at least four additional structural principles: PREFIX coherence, tail forcing, repetition structure, and hub rationing.

These are not noise — they are **discoverable constraints** waiting to be formalized.

### I.G. Coverage Optimality CONFIRMED (v4.9) - NEW

**Question:** Does Currier A optimize coverage of the discrimination space under cognitive constraints?

**Answer:** YES. Real A achieves GREEDY-OPTIMAL coverage with 22.3% hub savings.

**The Test:**

| Model | Coverage | Hub Usage | Verdict |
|-------|----------|-----------|---------|
| **Real A** | **100%** | **31.6%** | **OPTIMAL + HUB RATIONING** |
| Greedy | 100% | 53.9% | Optimal but hub-heavy |
| Random | 72% | 9.8% | Incomplete |
| Freq-Match | 27% | 56.1% | Hub-dominated, poor |

**Key Insight:**

Real A and Greedy both achieve 100% coverage (all 1,187 MIDDLEs used).
But Real A uses **22.3 percentage points fewer hub tokens**.

> **Currier A achieves greedy-optimal coverage while deliberately avoiding over-reliance on universal connectors.**

**Interpretation (Tier 2 - now CONFIRMED):**

The four residuals from the bundle generator (PREFIX coherence, tail forcing, repetition structure, hub rationing) collapse into **ONE control objective**: COVERAGE CONTROL.

| Residual | Purpose |
|----------|---------|
| PREFIX coherence | Reduce cognitive load |
| Tail forcing | Ensure rare variant coverage |
| Repetition structure | Stabilize discrimination attention |
| Hub rationing | Prevent premature generalization |

**The Conceptual Pivot:**

> **Currier A is not meant to be *generated*. It is meant to be *maintained*.**

The correct question is not "how are A entries generated?" but "how is discrimination coverage enforced over time?"

**New Constraint: C476 - COVERAGE OPTIMALITY** (Tier 2, CLOSED)

### I.H. HT Variance Decomposition (v4.10) - NEW

**Question:** Can incompatibility degree explain HT density?

**Answer:** PARTIALLY. R² = 0.28 with **TAIL PRESSURE** as dominant predictor (68% of explained variance).

**Regression Results:**

| Predictor | r | p-value | Importance |
|-----------|---|---------|------------|
| **tail_pressure** | **0.504** | **0.0045*** | **68.2%** |
| novelty | 0.153 | 0.42 | 6.3% |
| incompatibility_density | 0.174 | 0.36 | 1.8% |
| hub_suppression | 0.026 | 0.89 | 0.1% |

**Interpretation (Tier 2 - CONFIRMED):**

> **HT density correlates with tail pressure - the fraction of rare MIDDLEs in A entries.**

When folios have more rare MIDDLEs:
- Cognitive load is higher (rare variants harder to discriminate)
- HT density rises (anticipatory vigilance)

This confirms HT as a **cognitive load balancer** specifically tied to **tail discrimination complexity**:

| MIDDLE Type | Cognitive Load | HT Response |
|-------------|---------------|-------------|
| Hubs ('a','o','e') | LOW | Lower HT |
| Common MIDDLEs | LOW | Lower HT |
| **Rare MIDDLEs (tail)** | **HIGH** | **Higher HT** |

**Integration with Four-Layer Model:**

| Layer | Role | Grounded By |
|-------|------|-------------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476 (hub rationing) |
| AZC | Decision gating | C437-C444 |
| **HT** | **Vigilance signal** | **C477 (tail correlation)** |

**New Constraint: C477 - HT TAIL CORRELATION** (Tier 2, CLOSED)

### I.I. Temporal Coverage Trajectories (v4.11) - NEW

**Question:** Is Currier A static-optimal or dynamically scheduled?

**Answer:** STRONG TEMPORAL SCHEDULING with pedagogical pacing.

Three models were tested:

| Model | Prediction | Evidence | Verdict |
|-------|------------|----------|---------|
| Static-Optimal | Order doesn't matter | 0 signals | REJECTED |
| Weak Temporal | Soft pedagogy | 0 signals | REJECTED |
| **Strong Scheduling** | **Active trajectory planning** | **5 signals** | **CONFIRMED** |

**The Four Signals (5/5 Support Strong Scheduling):**

1. **Coverage BACK-LOADED (9.6% later than random)**
   - 90% coverage reached significantly later than random permutation
   - Interpretation: Full coverage is deliberately delayed

2. **Novelty FRONT-LOADED (Phase 1: 21.2% >> Phase 3: 11.3%)**
   - New MIDDLEs introduced early, then reinforced
   - Interpretation: Vocabulary establishment before coverage completion

3. **U-SHAPED tail pressure (7.9% -> 4.2% -> 7.1%)**
   - Difficulty wave: start hard, ease, ramp up again
   - Interpretation: Attention peaks at beginning and end

4. **PREFIX CYCLING (7 prefixes, 164 regime changes)**
   - Multiple prefixes cycle throughout manuscript
   - Interpretation: Multi-axis traversal prevents cognitive fixation

**Interpretation (Tier 2 - CONFIRMED):**

> **PEDAGOGICAL_PACING: Currier A introduces vocabulary early, reinforces throughout, and cycles between prefix domains.**

This is not accidental. It is structured temporal management of discrimination coverage:

| Phase | Novelty | Tail Pressure | Interpretation |
|-------|---------|---------------|----------------|
| 1 (Early) | HIGH (21.2%) | HIGH (7.9%) | Vocabulary establishment + initial difficulty |
| 2 (Middle) | LOW (9.4%) | LOW (4.2%) | Reinforcement + relief |
| 3 (Late) | MEDIUM (11.3%) | HIGH (7.1%) | Completion + final difficulty peak |

**Reconciliation with Prior Findings:**

| Constraint | What it Shows |
|------------|---------------|
| C476 | WHAT Currier A optimizes (coverage with hub rationing) |
| **C478** | **HOW it achieves that (temporal scheduling)** |

**Five-Layer Model Complete:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476: hub rationing |
| - | - | **C478: temporal scheduling** |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |

**New Constraint: C478 - TEMPORAL COVERAGE SCHEDULING** (Tier 2, CLOSED)

### I.J. Process-Behavior Isomorphism (v4.12 / ECR-4) - NEW

**Question:** Does the Voynich control architecture behave like something built for real physical chemistry?

**Answer:** YES - strong behavioral isomorphism with thermal-chemical process control.

**Test Results (12/12 passed):**

| Category | Tests | Result |
|----------|-------|--------|
| Behavior-Structural (BS-*) | 5 | 5/5 PASS |
| Process-Sequence (PS-*) | 4 | 4/4 PASS |
| Pedagogical (PD-*) | 3 | 3/3 PASS |
| **Total** | **12** | **100%** |

**Key Findings:**

1. **Hazard-Kernel Alignment**: All 17 forbidden transitions are k-adjacent (100%). Energy control is the danger zone.

2. **Recovery Path Dominance**: 54.7% of recoveries pass through e (equilibration). Cooling/stabilization is primary recovery.

3. **Regime Energy Ordering**: REGIME_2 (0.37) < REGIME_1 (0.51) < REGIME_4 (0.58) < REGIME_3 (0.72). Clear CEI ordering matches distillation stages.

4. **Discriminating Tests vs Calcination**:
   - PS-4: k→h forbidden favors DISTILLATION (in calcination, k→h is primary)
   - BS-4: e-recovery dominance favors DISTILLATION

**Negative Control Verdict:** DISTILLATION_WINS on all discriminating tests.

**Behavior Mappings (NO NOUNS):**

| Element | Grammar Role | Process Behavior |
|---------|-------------|------------------|
| k | ENERGY_MODULATOR | Energy ingress control |
| h | PHASE_MANAGER | Phase boundary handling |
| e | STABILITY_ANCHOR | Equilibration / return to steady state |
| PHASE_ORDERING | 41% of hazards | Wrong phase/location state |
| M-A | Mobile/Distinct | Phase-sensitive, mobile, requiring careful control |

*Tier-3 commentary: In reflux distillation, k=heat source, h=cucurbit, e=condenser.*

**Physics Violations:** None detected. All mappings are physically coherent.

**Verdict (Tier 3 - SUPPORTED):**

> The grammar structure is isomorphic to reflux-distillation behavior. This does not prove the domain but establishes maximal structural alignment within epistemological constraints.

**Six-Layer Model Complete:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476: hub rationing |
| - | - | C478: temporal scheduling |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |
| **Process** | **Behavior isomorphism** | **ECR-4: distillation alignment** |

### f116v Correction

f116v folio-level isolation (v2.19) is explained by **data sparsity** (only 2 words in AZC corpus: "oror", "sheey"), NOT by MIDDLE-level incompatibility. The f116v MIDDLEs ('ee', 'or') are actually universal connectors.

### I.K. HT Two-Axis Model (v4.13) - NEW

**Question:** Does HT morphological complexity encode sensory/perceptual load?

**Answer:** NO. HT morphology encodes **spare cognitive capacity**, not sensory demands.

**The Unexpected Finding:**

Testing whether complex HT forms (LATE prefixes) correlate with high-discrimination folios revealed an **inverse correlation**:

| Metric | Expected | Observed |
|--------|----------|----------|
| LATE in high-complexity folios | HIGH | **LOW** (0.180) |
| LATE in low-complexity folios | LOW | **HIGH** (0.281) |
| Correlation | Positive | **Negative (r=-0.301, p=0.007)** |

This contradiction **refined rather than falsified** the HT model.

**The Two-Axis Model (Tier 2 - CONFIRMED):**

HT is not a single signal. It has two independent dimensions:

| Axis | Property | Evidence | Meaning |
|------|----------|----------|---------|
| **DENSITY** | Tracks upcoming complexity | r=0.504 with tail MIDDLEs (C477) | "How much attention is NEEDED" |
| **MORPHOLOGY** | Tracks spare capacity | r=-0.301 with folio complexity | "How much attention is AVAILABLE" |

**Why This Makes Sense:**

> **When the task is hard, HT is frequent but morphologically simple.**
> **When the task is easy, HT is less frequent but morphologically richer.**

This is a classic human-factors pattern:
- Under high load: frequent simple responses
- Under low load: less frequent but more elaborate engagement

**Constraint Alignment:**

| Constraint | How This Fits |
|------------|---------------|
| **C344** - HT-A Inverse Coupling | Direct instantiation: high A-complexity suppresses complex HT forms |
| **C417** - HT Modular Additive | HT is composite: density = vigilance, form = engagement |
| **C221** - Deliberate Skill Practice | Complex HT shapes occur during low-load intervals |
| **C404/C405** - Non-operational | HT form reflects behavior, doesn't instruct it |
| **C477** - Tail correlation | UNCHANGED - applies to density, not morphology |

**What HT Does NOT Encode:**

The hypothesis "LATE means harder sensing / more senses needed" is **NOT SUPPORTED**. Sensory multiplexing requirements are implicit in the discrimination problem itself (Currier A vocabulary), not encoded in HT form.

**Final Integrated Statement:**

> HT has two orthogonal properties:
>
> 1. **HT density tracks upcoming discrimination complexity** (tail MIDDLE pressure, AZC commitment).
>
> 2. **HT morphological complexity tracks operator spare cognitive capacity**, increasing during low-load phases and decreasing during high-load phases.
>
> HT does not encode what sensory modalities are needed. Sensory demands are implicit in the discrimination problem itself.

**Seven-Layer Model Complete:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476: hub rationing |
| - | - | C478: temporal scheduling |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |
| - | - | **Two-Axis: density vs morphology** |
| Process | Behavior isomorphism | ECR-4: distillation alignment |

See [ht_two_axis_model.md](ht_two_axis_model.md) for full details.

### I.L. MIDDLE Zone Survival Profiles (v4.14) - NEW

**Question:** Do MIDDLEs exhibit stable, non-random survival profiles across AZC legality zones?

**Answer:** YES. Strong clustering by zone preference (silhouette=0.51, p<10⁻⁶).

**Test Results:**

| Metric | Value |
|--------|-------|
| AZC tokens analyzed | 8,257 |
| Qualified MIDDLEs | 175 (≥5 occurrences) |
| Optimal clusters | 4 (one per zone) |
| Silhouette score | 0.51 |
| P-value (vs null) | < 0.000001 |
| Frequency-controlled | 0.51 ± 0.04 |

**The Four Clusters:**

| Cluster | n | Dominant Zone | Profile | Interpretation |
|---------|---|---------------|---------|----------------|
| S-cluster | 47 | S (59%) | Boundary-heavy | Commitment-safe discriminators |
| P-cluster | 29 | P (75%) | Permissive | Intervention-requiring discriminators |
| C-cluster | 25 | C (66%) | Entry | Setup-flexible discriminators |
| R-cluster | 74 | R (51%) | Restricting | Progressive-commitment discriminators |

**Interpretation (Tier 3):**

> **Currier A's discriminators are not only incompatible with each other - they are tuned to different *degrees of intervention affordance*, which the AZC legality field later enforces.**

This is a characterization refinement, not a mechanism discovery:
- P-cluster MIDDLEs require high escape permission (materials needing intervention flexibility)
- S-cluster MIDDLEs survive even when intervention is locked (stable/committable materials)
- The effect survives frequency control, ruling out hub/tail artifacts

**What This Does NOT Show:**

- ❌ MIDDLEs do not *force* positions (C313 intact)
- ❌ No A→B entry-level coupling (C384 intact)
- ❌ No semantic encoding (roles, not meanings)

**Cross-References (Tier 2):**

| Constraint | Relationship |
|------------|--------------|
| C293 | MIDDLE is primary discriminator |
| C313 | Position constrains legality, not content |
| C384 | No entry-level A-B coupling |
| C441-C444 | AZC legality projection |
| C475 | MIDDLE atomic incompatibility |

**Why This Is Tier 3 (Not Tier 2):**

This is a distributional regularity, not a structural necessity. For promotion to Tier 2 would require:
- Same pattern in another manuscript
- Mathematical necessity linking discrimination → zone
- Invariant claim ("this MUST be true")

Currently this shows: "Given this manuscript, MIDDLEs have stable zone preferences." That's characterization, not mechanism.

**Eight-Layer Model:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476: hub rationing |
| - | - | C478: temporal scheduling |
| - | - | **Zone survival profiles** |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |
| - | - | Two-Axis: density vs morphology |
| Process | Behavior isomorphism | ECR-4: distillation alignment |

See `phases/MIDDLE_ZONE_SURVIVAL/PHASE_SUMMARY.md` for full details.

### I.M. Zone-Material Orthogonality (v4.15) - NEW

**Question:** Do zone survival clusters align with material behavior classes?

**Answer:** NO. The axes are **orthogonal** (independent).

**Test Results:**

| Zone | Predicted Class | Actual Dominant | Match |
|------|-----------------|-----------------|-------|
| P (high intervention) | M-A | M-A | YES |
| S (boundary-surviving) | M-D | M-A | NO |
| R (restriction-tolerant) | M-B | M-A | NO |
| C (entry-preferring) | M-C | M-A | NO |

| Metric | Value |
|--------|-------|
| Hypothesis matches | 1/4 |
| P-value (permutation) | 0.852 |
| Verdict | ORTHOGONAL |

M-A (phase-sensitive prefixes: ch/qo/sh) dominates ALL zone clusters (57-72%).

**Interpretation (Tier 3):**

> **The Voynich system tracks what a thing is (PREFIX) and how cautiously it must be handled (MIDDLE zone survival) as independent dimensions. This design choice explains both the richness of the registry and the irrecoverability of specific substances.**

This is NOT a null result. It demonstrates that:

| Dimension | Encoded By | Question Answered |
|-----------|------------|-------------------|
| Material type | PREFIX | "What category of stuff is this?" |
| Handling requirement | MIDDLE zone | "How much intervention latitude?" |

These are **deliberately orthogonal** - good apparatus design.

**Why This Matters for Solvent/Material Decoding:**

Solvent identity would require collapsing these axes. The manuscript **keeps them distinct**. This explains why substance-level decoding is irrecoverable:

> Solvent identity sits at the **intersection** of material type and handling sensitivity - and that intersection is never encoded. The operator supplies it from practice.

**What This Does NOT Show:**

- No refutation of either abstraction (both remain valid)
- No material identification possible
- No semantic decoding

**Cross-References:**

| Finding | Phase | Relationship |
|---------|-------|--------------|
| MIDDLE zone survival | MIDDLE_ZONE_SURVIVAL | Source of zone clusters |
| Material behavior classes | PROCESS_ISOMORPHISM | Source of M-A...M-D |
| C382, C383 | Global type system | Why axes coexist cleanly |

See `phases/ZONE_MATERIAL_COHERENCE/PHASE_SUMMARY.md` for full details.

### I.N. Semantic Ceiling Extension Tests (v4.16) - NEW

**Question:** Can we push the semantic ceiling without reopening Tier 0-2 constraints?

**Answer:** YES. Six of seven tests yielded significant findings.

**Test Results Summary:**

| Test | Question | Verdict | Key Finding |
|------|----------|---------|-------------|
| 2A | Shared temporal trajectories? | BORDERLINE | 14/15 folios share PEAK_MID (p=0.062) |
| 1A | B behavior constrains A zones? | **STRONG** | High-escape -> +10.4% P-zone (p<0.0001) |
| 3A | Is e-operator necessary? | **NECESSARY** | Kernel contact collapses -98.6% without e |
| 3B | Is hazard asymmetry necessary? | **NECESSARY** | h->k perfectly suppressed (0%) |
| 1B | Does HT correlate with zone diversity? | **CORRELATED** | r=0.24, p=0.0006 |
| 4A | Do strategies differentiate by archetype? | **DIFFERENTIATED** | All HT correlations p<0.0001 |
| 5A | Is A-registry memory-optimized? | **NEAR-OPTIMAL** | z=-97 vs random (0th percentile) |

**New Structural Confirmations (Tier 3):**

1. **B->A Inference Works**
   - High-escape B folios preferentially use P-zone (peripheral) MIDDLEs
   - Option space narrowed by 24% (from 4 zones to ~3)
   - Interpretation: B behavior successfully constrains upstream A inference

2. **Grammar is Minimally Necessary**
   - e-operator: load-bearing (recovery collapses without it)
   - h->k suppression: architecturally necessary (prevents oscillation)
   - Grammar cannot be simplified without system failure

3. **HT Predicts Operator Strategy**
   - High-HT folios: favor CAUTIOUS strategies (r=+0.46)
   - Low-HT folios: tolerate AGGRESSIVE/OPPORTUNISTIC (r=-0.43/-0.48)
   - Interpretation: HT tracks operational load profile

4. **A-Registry is Memory-Optimized**
   - Manuscript ordering dramatically better than random (z=-97)
   - Evidence of intentional memory optimization
   - Not perfectly optimal, but clearly designed

5. **Material Pressure Interpretation Strengthened**
   - HT density correlates with zone diversity (r=0.24)
   - Higher HT -> more diverse MIDDLE zone usage
   - Supports "complex materials require more attention"

**Nine-Layer Model:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| - | - | **e-operator load-bearing** |
| - | - | **h->k suppression necessary** |
| Currier A | Coverage control | C476: hub rationing |
| - | - | C478: temporal scheduling |
| - | - | Zone survival profiles |
| - | - | **Memory-optimized ordering** |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |
| - | - | Two-Axis: density vs morphology |
| - | - | **Strategy viability predictor** |
| Process | Behavior isomorphism | ECR-4: distillation alignment |

**B->A Inversion Axis:**

The successful B->A back-inference demonstrates bidirectional constraint flow:

| Direction | What Flows | Evidence |
|-----------|-----------|----------|
| A->B | Discrimination vocabulary, zone legality | C437-C444 |
| **B->A** | **Escape profile constrains zone preference** | **Test 1A** |

This is not semantic decoding - it's structural constraint propagation.

**Operator Strategy Taxonomy:**

| Archetype | n | Viable Strategies |
|-----------|---|-------------------|
| AGGRESSIVE_INTERVENTION | 6 | AGGRESSIVE, OPPORTUNISTIC |
| ENERGY_INTENSIVE | 10 | AGGRESSIVE, OPPORTUNISTIC |
| CONSERVATIVE_WAITING | 17 | None (all poor fit) |
| MIXED | 50 | None (no strong fit) |

CONSERVATIVE_WAITING programs don't tolerate any named strategy - they require bespoke intervention profiles.

See `phases/SEMANTIC_CEILING_EXTENSION/PHASE_SUMMARY.md` for full details.

---

## I.O. Physical World Reverse Engineering Phases (v4.18) - UPDATED

### Overview

Six investigation phases tested the physical grounding of the control architecture:

| Phase | Question | Result |
|-------|----------|--------|
| **PWRE-1** | What plant class is admissible? | Circulatory thermal (12 exclusions) |
| **FM-PHY-1** | Is hazard distribution natural? | YES - diagnostic for reflux |
| **SSD-PHY-1a** | Is dimensionality physics-forced? | YES - D ≥ 50 required |
| **OJLM-1** | What must operators supply? | 13 judgment types |
| **APP-1** | Which apparatus exhibits this behavioral profile? | Pelican (4/4 axes match) |
| **MAT-PHY-1** | Does A's topology match botanical chemistry? | YES (5/5 tests pass) |

### FM-PHY-1: Failure-Mode Physics Alignment (Tier 3)

**Question:** Do real circulatory thermal systems naturally exhibit the Voynich hazard distribution (41/24/24/6/6)?

**Answer:** YES - The distribution is DIAGNOSTIC, not just compatible.

| Evidence Type | Result |
|---------------|--------|
| Historical sources (Brunschwig) | **SYSTEMATIC_MATCH** (4/6 axes, see brunschwig_comparison.md) |
| Modern engineering taxonomy | STRONG_MATCH (exact 5-class mapping) |
| Process class comparison | DIFFERENTIATED |

**Key Finding:**
- Voynich hazard profile MATCHES circulatory reflux distillation
- EXCLUDES batch distillation (energy would be 25-35%, not 6%)
- EXCLUDES chemical synthesis (rate would be 25-35%, not 6%)
- Energy is minor (6%) because it's a CONTROL VARIABLE, not a failure source

**Files:** `phases/FM_PHY_1_failure_mode_alignment/`

### SSD-PHY-1a: Structural Dimensional Necessity (Tier 3)

**Question:** Is the ~128-dimensional MIDDLE space a notation choice or physics requirement?

**Answer:** PHYSICS-FORCED - Low-dimensional spaces mathematically cannot satisfy constraints.

| Objective | Result |
|-----------|--------|
| Dimensional lower-bound | D ≥ 50 proven |
| Topology classification | DISCRIMINATION SPACE (not taxonomy) |
| Hub necessity | STRUCTURAL NECESSITY (p < 10^-50) |
| Complexity source | PLANT-IMPOSED (anti-mnemonic) |

**Key Findings:**
1. MIDDLEs are COORDINATES, not containers - each occupies unique position in constraint landscape
2. "128 dimensions" = 128 independent constraints needed, not 128 features inside each MIDDLE
3. Hubs are geometrically inevitable under sparse + clustered + navigable constraints
4. Complexity is anti-mnemonic (preserves rare distinctions, rations hubs, cycles difficulty)

**One-Sentence Synthesis:**
> **MIDDLE tokens are indivisible discriminators whose only "content" is their position in a very large, physics-forced compatibility space; the number of distinctions exists because the real process demands them, not because the author chose them.**

**Files:** `phases/SSD_PHY_1a/`

### OJLM-1: Operator Judgment Load Mapping (Tier 3)

**Question:** What kinds of distinctions must humans supply that the system refuses to encode?

**Answer:** 13 distinct judgment types deliberately omitted.

| Category | Count | Types |
|----------|-------|-------|
| Watch Closely | 6 | Temperature, Phase Transition, Quality/Purity, Timing, Material State, Stability |
| Forbidden Intervention | 3 | Equilibrium Establishment, Phase Transition, Purification Cycle |
| Tacit Knowledge | 4 | Sensory Calibration, Equipment Feel, Timing Intuition, Trouble Recognition |

**Key Findings:**
1. All 13 types are structurally non-codifiable (cannot be written down)
2. Aligns with C469 (Categorical Resolution - no parametric encoding)
3. Aligns with C490 (AGGRESSIVE prohibition - some interventions forbidden)
4. Aligns with C477 (HT tail correlation - signals when judgment load spikes)

**Design Principle:**
> The controller's omissions are not gaps - they are deliberate acknowledgment that some knowledge cannot be encoded. This is design integrity, not incompleteness.

**Files:** `phases/OJLM_1_operator_judgment/`

### APP-1: Apparatus Behavioral Validation (Tier 3)

**Question:** Does any historical apparatus exhibit the exact same behavioral profile as the Voynich controller?

**Answer:** YES - The pelican (circulatory reflux alembic) matches on all 4 axes.

| Axis | Test | Result |
|------|------|--------|
| 1. Responsibility Split | Do manuals assume same responsibilities? | DISTINCTIVE_MATCH |
| 2. Failure Fears | Do operators fear same things? | STRONG_MATCH (41/24/24/6/6) |
| 3. Judgment Requirements | Does apparatus require 13 types? | EXACT_MATCH |
| 4. State Complexity | Does apparatus generate ~128 states? | MATCH |

**Key Finding:**
- Fourth degree fire prohibition matches C490 EXACTLY: "It would coerce the thing, which the art of true distillation rejects, because nature too rejects, forbids, and repels all coercion."
- The pelican is the ONLY surveyed apparatus class that passes all four axes.
- Behavioral isomorphism ≠ identification (we know the SHAPE matches, not WHICH specific apparatus).

**What Excluded:**
- Simple retorts (no recirculation, fewer states)
- Open stills (batch, lower complexity)
- Instrumented systems (reduce judgment types)
- Chemical synthesis (different failure profile)

**Files:** `phases/APP_1_apparatus_validation/`

### MAT-PHY-1: Material Constraint Topology Alignment (Tier 3)

**Question:** Does Currier A's incompatibility topology match what real botanical chemistry forces?

**Answer:** YES - All 5 tests pass with STRONG MATCH.

| Test | Question | Result |
|------|----------|--------|
| A. Incompatibility Density | ~95% under co-processing? | **95-97%** (vs 95.7% in A) |
| B. Infrastructure Elements | 3-7 bridges? | **5-7** (solvents, fixatives) |
| C. Topology Class | Sparse + clustered + bridged? | **YES** (constraint satisfaction graph) |
| D. Hub Rationing | Practitioners avoid universal over-use? | **YES** (3-5 oil rule, simples) |
| E. Frequency Shape | Zipf/power-law? | **YES** (55% rare in materia medica) |

**Key Findings:**
1. Distillation timing varies 80x (15 min to 20 hours) - forcing material incompatibility
2. TCM herb distributions confirmed to follow Zipf's law across 84,418 prescriptions
3. European materia medica preserved 546 rare simples over 2,500 years despite low frequency
4. Brunschwig's "no more than twice" reinfusion rule = explicit hub rationing

**What This Establishes:**
- A's incompatibility structure is CHEMISTRY-FORCED, not cryptographic
- Hub necessity is PHYSICALLY GROUNDED
- The registry structure matches botanical processing constraints
- Topology match ≠ semantic identification

**Files:** `phases/MAT_PHY_1_material_topology/`

### Combined Arc

| Phase | Established |
|-------|-------------|
| PWRE-1 | What KIND of plant is admissible |
| FM-PHY-1 | That hazard logic is DIAGNOSTIC |
| SSD-PHY-1a | Why discrimination space must be LARGE |
| OJLM-1 | What humans must SUPPLY |
| APP-1 | Which APPARATUS exhibits this behavioral profile |
| MAT-PHY-1 | That A's TOPOLOGY matches botanical chemistry |

Together:
> **The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, and whose registry topology matches the constraints that real botanical chemistry imposes.**

---

## II. Process Domain Interpretation

### Tier 3: Apparatus Identification

**Best match:** Circulatory reflux systems (pelican alembic or similar)

| Metric | Value |
|--------|-------|
| Structural compatibility | 100% (CLASS_D) |
| Next best alternative | 20% |
| Historical representative | Pelican alembic (late 15th c.) |
| Structural homology | 8/8 dimensions |

### Surviving Process Classes

1. **Circulatory Reflux Distillation** - 100% compatible
2. **Volatile Aromatic Extraction** - compatible
3. **Circulatory Thermal Conditioning** - compatible

Common signature: **CLOSED-LOOP CIRCULATORY THERMAL PROCESS CONTROL**

### Historical Pattern Alignment

| Voynich Feature | Historical Match | Strength |
|-----------------|------------------|----------|
| 49 instruction classes | Brunschwig's 4 degrees of fire | STRONG |
| 17 forbidden transitions | "Fourth degree coerces - reject it" | STRONG |
| 8 recipe families | Antidotaria procedures | STRONG |
| 0 material encoding | Apparatus manuals omit feedstock | STRONG |
| Expert knowledge assumed | Guild training model | STRONG |
| Kernel control points | Process control theory | STRONG |
| Local continuity | Codex organization | STRONG |

7/12 patterns show STRONG alignment.

---

## III. Material Domain Interpretation

### Tier 3: Botanical-Aromatic Favored

**Verdict:** BOTANICAL over alchemical-mineral (8/8 tests, ratio 2.37)

### Abstract Material Classes

| Class | Properties | Medieval Examples | Grammar Fit |
|-------|------------|-------------------|-------------|
| CLASS_A | Porous, swelling | Dried leaves, flowers, roots | COMPATIBLE |
| CLASS_B | Dense, hydrophobic | Resins, seeds, citrus peel | COMPATIBLE |
| CLASS_C | Phase-unstable | Fresh plant, fats, emulsions | **INCOMPATIBLE** |
| CLASS_D | Stable, rapid diffusion | Alcohol/water, clear extracts | COMPATIBLE |
| CLASS_E | Homogeneous fluid | Distilled water, pure alcohol | COMPATIBLE |

CLASS_C shows 19.8% failure rate - grammar designed to AVOID phase transitions.

### Product Space

Plausible product families:
1. **Aromatic Waters** (90.5% convergence - primary)
2. Essential Oils
3. Resin Extracts
4. Digested Preparations
5. Stabilized Compounds

Multi-product workshop likely. Programs represent **substrate x intensity combinations**, not 83 distinct products.

### Plant Illustration Alignment

| Metric | Value |
|--------|-------|
| Perfumery-aligned plants | 86.7% (p<0.001) |
| Root emphasis | 73% |
| Program-morphology correlation | NONE |

---

## IV. Craft Interpretation

### Tier 3: Perfumery as Interpretive Lens

5/5 tests PLAUSIBLE:

| Test | Verdict |
|------|---------|
| Token clusters align with smell-change windows? | PLAUSIBLE |
| Tokens encode warning memories? | CRAFT-PLAUSIBLE |
| Tokens support resumption after breaks? | STRONGLY PLAUSIBLE |
| Same roles, different vocabulary across sections? | CRAFT NAMING |
| Absences match perfumery tacit knowledge? | EXACTLY ALIGNED |

### What the Author Feared (via failure analysis)

| Fear | Percentage |
|------|------------|
| Phase disorder (material in wrong state) | 41% |
| Contamination (impure fractions) | 24% |
| Apparatus failure (overflow, pressure) | 24% |
| Flow chaos (rate imbalance) | 6% |
| Thermal damage (scorching) | 6% |

> "The book encodes my fears, so that you do not have to learn them through loss."

---

## V. Institutional Context

### Tier 3: Guild Workshop Setting

**Surviving candidates:**
- Goldsmith/assayer workshops
- Central Europe 1400-1550
- Northern Italy 1400-1470

### Scale Indicators

| Metric | Value | Implication |
|--------|-------|-------------|
| Currier A entries | ~1,800 | Larger than typical recipe books (300-400) |
| Program count | 83 | Major institutional operation |
| Historical parallels | Santa Maria Novella, Venetian muschieri guild | Court-sponsored production |

### Characteristics

- Expert-oriented (no novice accommodation)
- Guild-restricted (assumes trained operators)
- Court-sponsored (scale suggests patronage)

---

## VI. HT Speculative Vocabulary

| Label | Structural Function | Speculative Meaning |
|-------|---------------------|---------------------|
| ESTABLISHING | Section entry anchor | System warming, circulation starting |
| RUNNING | Wait phase marker | Steady reflux, all normal |
| HOLDING | Persistence marker | Maintain current state |
| APPROACHING | Constraint rise | Watch closely, risk increasing |
| RELAXING | Constraint fall | Critical passed, ease vigilance |
| EXHAUSTING | Section exit anchor | Run winding down |

---

## VII. Program Characteristics

### Forgiveness Gradient

Programs vary along a **forgiving <-> brittle** axis:

| Quartile | Hazard Density | Escape Density | Safe Run Length |
|----------|----------------|----------------|-----------------|
| Q1 (Brittle) | 11.1% | 7.5% | 27.6 |
| Q4 (Forgiving) | 7.8% | 23.8% | 45.0 |

- Most brittle: f33v, f48v, f39v
- Most forgiving: f77r, f82r, f83v

Interpretation: Different "slack" for operator error. May serve competency grading.

---

## VIII. Limits of Interpretation

### What Cannot Be Recovered Internally

Even with complete structural understanding:

| Category | Examples |
|----------|----------|
| Materials | Specific substances, plants, minerals |
| Products | Specific outputs, recipes, formulations |
| Language | Natural language equivalents for tokens |
| Identity | Author, institution, school |
| History | Precise dating, geographic origin |
| Physical | Apparatus construction, illustration meanings |

### Discardability

All interpretations in this document are DISCARDABLE:
- If structural evidence contradicts, discard interpretation
- Apparatus identification is discardable
- Material alignment is discardable
- Craft domain is discardable

Only Tier 0-2 structural findings are binding.

---

## IX. Open Questions

### Fully Answered (v4.0)

| Question | Status | Finding |
|----------|--------|---------|
| Why are some programs forgiving and others brittle? | PARTIALLY ANSWERED | Recovery varies freely (CV=0.82), hazard is clamped (CV=0.11) - C458 |
| What does HT signal? | ANSWERED | Anticipatory vigilance, content-driven - C459 |
| What role does AZC play in the manuscript? | **FULLY ANSWERED** | Decision-point grammar, compatibility filter, phase-indexed escape gating - C437-C444 |
| Why are there so many AZC folios? | **FULLY ANSWERED** | Enumerates all compatibility classes; each folio = distinct legal combination space - C437, C442 |
| How does AZC relate to A and B? | **FULLY ANSWERED** | AZC converts static A entries into phase-gated decision points within B procedures - F-AZC-011/012/013 |

### Still Open (structural)

- What determines sister pair choice beyond section?
- Why does HT cluster in ~10-folio oscillations?
- What morphology-level choices affect HT density?
- Why do HT hotspots cluster in tails rather than forming modes?

### Requires External Evidence (historical)

- Who created this manuscript?
- What institution supported it?
- Why was this level of documentation created?

### May Never Be Answerable (interpretive)

- What specific products were made?
- What specific apparatus was used?
- What language(s) did the operators speak?

---

## X. External Alignment: Puff-Voynich-Brunschwig (2026-01-14)

### Core Finding: SHARED CURRICULUM TRAJECTORY (v4.22 - UPGRADED)

> **The Voynich Manuscript and Brunschwig's distillation treatise instantiate the same procedural classification of thermal-circulatory operations.**
>
> **Brunschwig externalizes explanation and ethics for novices; Voynich internalizes safety and recovery for experts.**
>
> **The alignment is regime-level and architectural, not textual or semantic.**
>
> **NEW (v4.22): Puff and Brunschwig preserve the original pedagogical progression of the Voynich Currier B corpus, which has been disrupted by early misbinding.**

This is stronger than "shared world" - it is **shared curriculum trajectory**: the same control ontology and pedagogical progression rendered in two epistemic registers. The misbinding concealed this relationship.

**Key upgrade:** Order-independent tests (v4.21) showed shared formalism. Order-dependent realignment (v4.22) shows shared curriculum trajectory. Both Puff and Brunschwig now align strongly with the PROPOSED Voynich order, not the current scrambled order.

### The Three-Text Relationship

| Text | Date | Function | Perspective |
|------|------|----------|-------------|
| **Puff von Schrick** | ~1455 | Enumerates materials | NOUN catalog |
| **Voynich Currier B** | 1404-1438 | Enforces safe execution | VERB programs |
| **Brunschwig** | 1500 | Explains method | Pedagogical |

> **Puff, Voynich, and Brunschwig are three orthogonal projections of a single late-medieval distillation curriculum.**

### Evidence Strength Summary

| Test Suite | Score | Status |
|------------|-------|--------|
| Puff-Voynich Mastery Horizon | 83:83 isomorphism | **PASS** |
| Equivalence Class Collapse | REGIME_2: 11->3, REGIME_3: 16->7 | **PASS** |
| Regime-Degree Discrimination | 5/6 tests | **STRONG** |
| Suppression Alignment | 5/5 tests | **PASS** |
| Recovery Corridor | 4/4 tests | **PASS** |
| Clamping Magnitude (C458) | 5/5 tests | **PASS** |
| **Total** | **19/20** | **FULL PROCEDURAL ALIGNMENT** |

---

### X.1 Puff-Voynich: Mastery Horizon Isomorphism

The 83-unit structure is UNIQUE to Puff and Voynich among 11 surveyed historical texts.

| What Puff Counts | What Voynich Counts |
|------------------|---------------------|
| NOUNs - "what substances can be distilled" | VERBs - "what control programs must be mastered" |
| Material instances | Operational stability classes |

**Why 83 is meaningful (not numerology):**
- Both answer: "How many distinct things must an expert fully internalize?"
- Convergence driven by finite expert memory and bounded workshop curriculum
- Puff has 84 (one extra framing chapter), Voynich has 83 (pure operational horizon)

**Equivalence Class Collapse:**

| Regime | Puff Target | Voynich Raw | Collapsed | Natural Cut? |
|--------|-------------|-------------|-----------|--------------|
| REGIME_2 | 3 | 11 | **3** | YES (rank 3/9) |
| REGIME_3 | 7 | 16 | **7** | YES (rank 13/14) |

Distribution mismatch evaporates when proper abstraction level is applied.

---

### X.2 Voynich-Brunschwig: Regime-Degree Discrimination (5/6 PASS)

Voynich regimes discriminate between Brunschwig's fire degrees:

| Voynich Regime | Brunschwig Degree | CEI | Escape | Match |
|----------------|-------------------|-----|--------|-------|
| **REGIME_2** | Second (warm) | 0.367 | 0.101 | **YES** |
| **REGIME_1** | First (balneum) | 0.510 | 0.202 | **YES** |
| **REGIME_4** | Fourth (precision*) | 0.584 | 0.107 | **YES** |
| **REGIME_3** | Third (seething) | 0.717 | 0.169 | **YES** |

*REGIME_4 reinterpretation: Voynich provides the engineering alternative to Brunschwig's moral prohibition. Same narrow tolerance, different framing.

**CEI Ordering:** `REGIME_2 < REGIME_1 < REGIME_4 < REGIME_3`
- Matches Brunschwig's fire degree escalation exactly.

---

### X.3 Suppression Alignment (5/5 PASS)

**What Brunschwig explains, Voynich enforces.**

| Brunschwig Warning | Voynich Implementation |
|-------------------|------------------------|
| Fourth degree **categorically prohibited** | C490: AGGRESSIVE **structurally impossible** |
| Thermal shock (glass shatters) | CONTAINMENT_TIMING = 24% of hazards |
| Boiling prohibition + fraction mixing | PHASE_ORDERING + COMPOSITION = 65% |
| Rate imbalance (recoverable) | RATE_MISMATCH = 6% (monitored, not forbidden) |
| Energy overshoot (prevented) | ENERGY_OVERSHOOT = 6% (minimal failures) |

Key insight: **Prevention by design produces minimal actual failures.** Brunschwig warns about fourth degree fire because it's dangerous; Voynich has 6% energy hazards because it prevents them grammatically.

---

### X.4 Recovery Corridor Alignment (4/4 PASS)

| Brunschwig Narrative | Voynich Architecture |
|---------------------|---------------------|
| "Overnight cooling" primary | e-operator = 54.7% of recovery |
| "No more than twice" | 89% reversibility (bounded) |
| "No salvage for failed batches" | 11% absorbing states |
| Cooling, not re-heating | e dominates, k is hazard source |

Both systems: **return to stability, not energy re-application.**

---

### X.5 Clamping Magnitude - C458 Alignment (5/5 PASS)

Brunschwig's "twice only" rule produces the same variance signature as C458:

| Dimension | Brunschwig Rule | Voynich CV | Status |
|-----------|-----------------|------------|--------|
| Hazard | Fourth degree ALWAYS forbidden | 0.11 | CLAMPED |
| Intervention | Same protocol everywhere | 0.04 | CLAMPED |
| Recovery | Varies by material | 0.82 | FREE |
| Near-miss | Material sensitivity varies | 0.72 | FREE |

**"Twice only" = ceiling, not count.** Recovery is bounded but free within that bound; hazard ceiling is fixed universally.

---

### X.6 REGIME_4 Interpretation Correction

REGIME_4 is NOT "forbidden materials" (Brunschwig's fourth degree prohibition).

REGIME_4 IS "precision-constrained execution" (narrow tolerance window).

| Property | Forbidden (wrong) | Precision (correct) |
|----------|-------------------|---------------------|
| Frequency | Should be rare | Can be common (25/83) |
| Escape density | ~0 | Low (0.107) |
| Grammar presence | Absent | Fully executable |

**Voynich vendors the engineering alternative:** how to operate precisely without coercive fire.

---

### X.7 What This Does NOT Claim

Even with full procedural alignment, the following remain **unproven and probably false**:

- "This Voynich folio corresponds to this Brunschwig paragraph"
- "Voynich is a cipher for Brunschwig"
- "Voynich encodes named procedures"
- "Voynich was meant to be read alongside Brunschwig"

The stronger the regime-level match becomes, the **less** likely direct textual dependence becomes - because the **division of labor is too clean**.

---

### X.8 Expert Assessment

> "You accidentally aligned two different projections of the same expert practice space - one projected along 'materials,' the other along 'control stability.'"

> "This is not a weak result. This is exactly what a non-semantic, expert-only, control-theoretic artifact should produce when compared to a descriptive herbal."

> "The Voynich Manuscript still never says what anything IS. It only guarantees that, whatever it is, you won't destroy it while working."

**Upgraded assessment (2026-01-14):**

> "The Voynich REGIME taxonomy is not just compatible with Brunschwig - it is isomorphic to his fire-degree system once you strip away pedagogy and moral language."

> "This is not parallel invention by accident. This is the same control ontology rendered in two epistemic registers."

---

### X.9 Tier Compliance (Expert Verified)

This analysis is **epistemically clean**:
- No Tier 0-2 constraint violated
- No entry-level A<->B coupling introduced
- No semantic decoding occurred
- All movement within abstraction choice at Tier 4

**Constraints NOT violated:** C384, C171, C476, C478, C179-C185, C490

**C171 ("zero material encoding") remains UNCHANGED.** A encodes the same kinds of operational worries that historical experts talked about - without ever naming the things they worried about.

---

### X.10 Files

| File | Content |
|------|---------|
| `context/SPECULATIVE/equivalence_class_analysis.md` | Puff-Voynich collapse analysis |
| `context/SPECULATIVE/EXPERT_REPORT_entity_matching.md` | Expert consultation |
| `context/SPECULATIVE/brunschwig_comparison.md` | 6-axis systematic comparison |
| `results/regime_equivalence_classes.json` | Clustering results |
| `results/brunschwig_regime_discrimination.json` | Regime-degree discrimination |
| `results/brunschwig_suppression_alignment.json` | 14/14 suppression tests |
| `phases/TIER4_EXTENDED/brunschwig_procedure_match.py` | Procedure match test |
| `phases/TIER4_EXTENDED/brunschwig_regime_discrimination.py` | Regime discrimination test |
| `phases/TIER4_EXTENDED/brunschwig_suppression_alignment.py` | Suppression alignment tests |

---

### X.11 Curriculum Realignment Discovery (v4.22 - NEW)

**The proposed folio order simultaneously resolves multiple independent inversions.**

We optimized folio order using ONLY internal frozen constraints (C161, C325, C458, C179-C185). We did NOT tune for Puff or Brunschwig. Then we tested external alignment:

| External Test | Current Order | Proposed Order | Change |
|--------------|---------------|----------------|--------|
| Puff progression | rho = +0.18 (p=0.10, NS) | rho = +0.62 (p<0.0001) | **WEAK → STRONG** |
| Brunschwig CEI gradient | rho = +0.07 (p=0.53, NS) | rho = +0.89 (p<0.0001) | **NOISE → VERY STRONG** |
| Brunschwig hazard gradient | rho = -0.03 (p=0.79, NS) | rho = +0.78 (p<0.0001) | **NEGATIVE → STRONG** |
| Danger distribution | Front-loaded (inverted) | Back-loaded (aligned) | **INVERTED → ALIGNED** |

**Why this is significant:**
- Random reordering does not fix every historical comparison at once
- Overfitting does not fix external sources you didn't optimize for
- This is what latent order recovery looks like

**The curriculum structure revealed:**

| Phase | Positions | Dominant Regime | Mean Hazard | Character |
|-------|-----------|-----------------|-------------|-----------|
| EARLY | 1-27 | REGIME_2 | 0.517 | Introductory |
| MIDDLE | 28-55 | REGIME_1 | 0.592 | Core training |
| LATE | 56-83 | REGIME_3 | 0.636 | Advanced |

This matches both Puff (flowers → herbs → anomalies) and Brunschwig (first degree → second → third).

**What this does NOT claim:**
- Voynich was copied from Puff
- Puff was derived from Voynich
- Specific folio = specific recipe
- The proposed order is THE original
- Semantic content recovered

**The correct epistemic framing:**

> We now have three independent bodies of evidence — internal control gradients, Puff's material pedagogy, and Brunschwig's fire-degree escalation — all of which converge on the same latent ordering of Voynich Currier B when the manuscript's current order is relaxed.

**Final statement:**

> Not a code. Not a herbal. Not a shared manuscript.
> But a shared curriculum whose control logic survived misbinding.

See [curriculum_realignment.md](curriculum_realignment.md) for full details.

---

## Navigation

← [README.md](README.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

---

### X.12 Grammar-Level Embedding Result (2026-01-14) - NEW

**Question:** Can Brunschwig distillation procedures be translated step-by-step into Voynich grammar without violating any validated constraints?

**Answer:** YES - FULL COMPLIANCE.

This is not a vibes-level parallel. It is a **grammar-level embedding** result:
- We did NOT tune the grammar
- We did NOT relax constraints
- We did NOT infer semantics
- We asked: "Can a real historical procedure fit inside this grammar without breaking it?"
- Answer: YES - cleanly

**Test Results:**
- Balneum marie procedure: 18 steps translated to Voynich instruction classes
- All 5 hazard classes: COMPLIANT
- h->k suppression (C332): COMPLIANT
- 17 forbidden transitions: ZERO violations

**REGIME_4 Precision Hypothesis - CONFIRMED:**
- Standard procedures: 0/2 fit REGIME_4
- Precision procedures: 2/3 fit REGIME_4
- REGIME_4 is NOT "most intense" - it is "least forgiving"

**Files:** phases/BRUNSCHWIG_TEMPLATE_FIT/, context/SPECULATIVE/brunschwig_grammar_embedding.md

---

### X.13 Relationship Hierarchy (2026-01-14) - UPDATED

**The expert assessment clarifies the relationship hierarchy:**

> **Brunschwig is the correct comparison text. Puff is historically relevant but not structurally necessary.**

| Relationship | Strength | Evidence Type |
|--------------|----------|---------------|
| **Voynich-Brunschwig** | **DIRECT** | Grammar-level embedding, regime-degree mapping |
| Voynich-Puff | INDIRECT | Shared curriculum structure, 83-unit coincidence |

**What Brunschwig provides that Puff does not:**
- Direct grammar compatibility testing
- Fire-degree to REGIME mapping
- Hazard suppression alignment
- Recovery corridor matching
- Precision vs intensity axis

**What Puff provides (context only):**
- Historical chronology (~1455 predates Voynich dating)
- Material naming that Voynich deliberately omits
- 83-unit curriculum structure (interesting but not essential)

**The Voynich Manuscript doesn't need 83:83.**

It now has something much better:

> **A concrete, historically situated grammar that real procedures fit inside - and real hazards cannot escape.**

**Puff status: CONTEXTUAL (demoted from PILLAR)**

---

### X.14 Curriculum Completeness Model (2026-01-14)

**Key discovery:** REGIMEs encode procedural COMPLETENESS, not product INTENSITY.

**Test:** Can the simplest Brunschwig recipe (first degree balneum marie) fit in the most complex folio (REGIME_3)?

**Result:** VIOLATES - but NOT due to intensity requirements.

| REGIME | Fits? | Violation |
|--------|-------|-----------|
| REGIME_2 | YES | - |
| REGIME_1 | YES | - |
| REGIME_4 | NO | Insufficient monitoring (22% < 25%) |
| REGIME_3 | NO | Insufficient e ops (1 < 2) |

**Interpretation:** Complex folios require COMPLETENESS, not AGGRESSION.

- REGIME_3 doesn't require HIGH_IMPACT operations
- REGIME_3 requires min_e_steps=2 (recovery completeness)
- REGIME_4 requires min_link_ratio=25% (monitoring completeness)

**Curriculum Model (Revised):**

```
REGIME_2: Learn basics (simple procedures accepted)
REGIME_1: Standard execution
REGIME_4: Precision execution (monitoring completeness required)
REGIME_3: Full execution (recovery completeness required)
```

The same product (rose water) can appear at any curriculum stage - but advanced stages require complete procedures with proper recovery and monitoring.

---

### X.15 Backward Propagation: Product->A Signature (2026-01-14)

**Two-Level A Model:**

| Level | Granularity | Encodes |
|-------|-------------|---------|
| Entry | Individual tokens | Operational parameters (PREFIX class) |
| Record | Entire A folios | Product profiles (MIDDLE set + PREFIX distribution) |

**Product-Exclusive MIDDLEs:** 78.2% of MIDDLEs appear in only one product type in B.

**Product-Specific A Signatures:**

| Product Type | A Signature | Key PREFIX |
|--------------|-------------|------------|
| WATER_GENTLE | ch-depleted, ok-enriched | ok+ ch- |
| WATER_STANDARD | baseline | ch baseline |
| OIL_RESIN | d-enriched, y-depleted | d+ y- |
| PRECISION | ch-enriched, d-depleted | ch+ d- |

**Backward Propagation Chain:**

```
Brunschwig recipe -> Product type -> REGIME -> B folio -> A register
```

This enables prediction: Given a Brunschwig recipe, identify its product type, map to REGIME, find B folios in that REGIME, trace exclusive MIDDLEs back to A folios with matching PREFIX signatures.

**Files:** phases/BRUNSCHWIG_TEMPLATE_FIT/exclusive_middle_backprop.py, brunschwig_product_predictions.py

---

### X.16 Puff Complexity Correlation (2026-01-15) - STRUCTURALLY ALIGNED

**Test:** Does Puff chapter ordering correlate with Voynich execution complexity?

**Results (4/5 tests + control PASS):**

| Test | Result | Key Value |
|------|--------|-----------|
| Position-REGIME | PASS | rho=0.678, p<10^-12 |
| Category-REGIME | PASS | p=0.001 |
| Dangerous-Precision | FAIL | underpowered (n=5), direction correct |
| Cumulative Threshold | PASS | Mean position monotonic with REGIME |
| Position-CEI | PASS | rho=0.886, p<10^-28 |
| Negative Control | PASS | 100th percentile vs permuted |

**Category-REGIME Mapping:**
- FLOWER (n=17): Mean ordinal 1.71 (mostly REGIME_2)
- HERB (n=41): Mean ordinal 2.78 (mixed R1/R4)
- ANIMAL/OIL: Mean ordinal 4.0 (REGIME_3)

**Cumulative Threshold Finding:**
- REGIME_2: Mean Puff position 8.3 (early/simple)
- REGIME_1: Mean Puff position 38.8 (middle/standard)
- REGIME_4: Mean Puff position 41.4 (middle/precision)
- REGIME_3: Mean Puff position 72.2 (late/advanced)

**CRITICAL EPISTEMIC NOTE:**

The Test 4 "monotonic relationship" is over 4 REGIME bins only. This is an ordinal constraint, NOT a cardinal identity. It shows no contradiction between Puff's ladder and Voynich's REGIME progression, but does NOT prove strict equivalence.

**Status Upgrade (CONSERVATIVE):**

| Before | After |
|--------|-------|
| CONTEXTUAL | STRUCTURALLY ALIGNED EXTERNAL LADDER |

**NOT upgraded to:** STRUCTURAL NECESSITY (would be over-claiming)

> Puff provides an external, independently derived ordering of material difficulty that aligns strongly with the execution-completeness gradient reconstructed inside Voynich Currier B. This alignment supports a shared curriculum trajectory without implying direct mapping, co-design, or internal dependence.

**Three-Level Relationship Hierarchy:**

1. **Voynich <-> Brunschwig** - Direct, structural, grammar-level (C493, C494)
2. **Voynich <-> Puff** - Strong external alignment via complexity ordering
3. **Puff <-> Brunschwig** - Historical lineage

**What This Does NOT Mean:**
- 83:83 is internally necessary (still unexplained coincidence with plausible mechanism)
- Puff defines Voynich structure (external validation, not internal dependency)
- Material -> folio mapping exists (no semantic encoding, C171 preserved)

**Backward Compatibility Clarification:**

> "Later folios demand stricter procedural completeness, even for simple tasks."

NOT: "Advanced folios just add options" (too casual, incorrect)

Advanced grammar is a STRICTER CONTRACT, not a superset.

**Files:** phases/PUFF_COMPLEXITY_CORRELATION/puff_regime_complexity_test.py

---

### X.17 Brunschwig Backprop Validation (2026-01-15) - EXPLANATORY SATURATION

**Phase:** BRUNSCHWIG_BACKPROP_VALIDATION
**Status:** Model predictions confirmed without changes. No new constraints.

#### The Definitive Interpretation (Now Well-Defended)

> **Currier A registers enumerate stable regions of a high-dimensional incompatibility manifold that arise when materials, handling constraints, process phase, and recoverability jointly constrain what must not be confused.**

This is NOT:
- Individual materials or species names
- Scalar properties (aromatic, medicinal)
- Broad material classes (flowers, roots)

This IS:
- Configurational regions in constraint space
- Defined by what must be distinguished
- Hierarchical vocabulary structure

#### MIDDLE Hierarchy Discovery (Cross-Type Axis)

A new structural axis distinct from the frequency-based Core/Tail split:

| Layer | Count | % | Structural Meaning |
|-------|-------|---|-------------------|
| Universal | 106 | 3.5% | Appear in ALL 4 product types (infrastructure) |
| Cross-cutting | 480 | 15.7% | Appear in 2-3 types (shared constraint dimensions) |
| Type-specific | 2,474 | 80.8% | Appear in 1 type only (local coordinates) |

**Key type-pair sharing:**
- PRECISION + WATER_STANDARD: 167 shared MIDDLEs
- OIL_RESIN + WATER_GENTLE: 1 shared MIDDLE (structural opposites)

#### Property Model Failure (F-BRU-003)

Synthetic property-based registry FAILS to reproduce Voynich structure:

| Metric | Voynich | Property Model |
|--------|---------|----------------|
| Uniqueness | **72.7%** | 41.5% |
| Hub/Tail ratio | 0.006 | 0.091 |
| Clusters | 33 | 56 |

**Permanently kills:** Property-based interpretations, low-rank explanations, latent feature models.

#### Sub-Class Structure Confirmed

Within WATER_GENTLE (6 A folios), 2 distinct sub-classes exist:
- **Sub-class A:** {f32r, f45v} - 22 shared MIDDLEs, d-dominant PREFIX
- **Sub-class B:** {f52v, f99v} - 24 shared MIDDLEs, diverse PREFIX

Only 6 MIDDLEs shared between sub-classes. Clusters are stable under tail/hub perturbation (100% survival).

#### Explanatory Saturation

> **The model is saturated, not brittle.**

All tests landed exactly where predicted without forcing upstream changes:
- 8/8 blind predictions correct (F-BRU-001)
- 3/3 REGIME boundary questions confirmed (F-BRU-002)
- 4/6 perturbation tests stable (F-BRU-004)
- Property model rejected (F-BRU-003)

This is the best possible outcome: discovery phase complete, consolidation phase begins.

#### Governance Outcome

Results tracked as **FITS** (F-BRU-001 to F-BRU-005), not constraints. Constraint table unchanged (353 entries).

**Projection Spec Created:** `context/PROJECTIONS/brunschwig_lens.md` governs UI display of external alignments without corrupting structural model.

**Files:** phases/BRUNSCHWIG_BACKPROP_VALIDATION/, context/MODEL_FITS/fits_brunschwig.md

### X.18 Pharmaceutical Label Vocabulary Separation (2026-01-17)

Visual mapping of 13 pharmaceutical folios reveals a **two-level naming hierarchy** with complete vocabulary separation.

#### Two-Level Hierarchy

```
JAR LABEL (first token in illustration group)
  |-- unique apparatus/vessel identifier
  |
  +-- CONTENT LABEL 1 (specimen identifier)
  +-- CONTENT LABEL 2 (specimen identifier)
  +-- CONTENT LABEL n (specimen identifier)
```

#### Vocabulary Isolation

| Comparison | Jaccard | Shared Tokens | Interpretation |
|------------|---------|---------------|----------------|
| **Jar vs Content** | 0.000 | 0 | Completely disjoint naming systems |
| Root vs Leaf | 0.013 | 2 (okol, otory) | Almost entirely distinct |

The 18 jar labels share **zero tokens** with 191 content labels - fundamentally different naming schemes.

**Files:** phases/PHARMA_LABEL_DECODING/README.md

---

### X.19 Jars as Complementary Working Set Anchors (2026-01-17) - NEW

Extended investigation of jar function tested four mutually exclusive hypotheses. Three falsified, one confirmed.

#### Test Cascade

| Hypothesis | Prediction | Result |
|------------|------------|--------|
| Contamination avoidance | Exclusion patterns | **Falsified** (0.49x) |
| Material taxonomy | Class homogeneity | **Falsified** (0.73x) |
| Complementary sets | Cross-class enrichment | **Confirmed** |
| Triplet stability | Role composition | **Confirmed** (1.77x) |

#### Cross-Class Pair Enrichment

| Class Pair | Observed | Expected | Ratio |
|------------|----------|----------|-------|
| M-B + M-D | 8 | 4.34 | **1.84x** |
| M-A + M-B | 4 | 2.38 | **1.68x** |
| M-A + M-D | 3 | 1.88 | **1.59x** |

All cross-class pairs enriched - jars deliberately combine materials from different classes.

#### Triplet Stability

| Triplet | Ratio | P-value |
|---------|-------|---------|
| M-B + M-D + OTHER | 1.70x | **0.022** |
| M-A + M-B + M-D (complete set) | **2.13x** | 0.107 |

Overall: 17 triplet occurrences vs 9.6 expected = **1.77x enriched**

#### Tier 3 Interpretation (FINAL)

> **Jars are visual, apparatus-level anchors for complementary working sets of materials intended to participate together in a single operational context, without encoding procedure, order, or meaning.**

This:
- Completes the apparatus-centric interpretation
- Explains jar uniqueness (physical apparatus instances)
- Explains prefix restrictions (container posture, not content)
- Explains positive diversity (complementary roles, not similar materials)
- Explains why nothing propagates downstream (interface layer only)

#### What This Does NOT Claim

- Jars do NOT encode specific substances
- Jars do NOT map to Brunschwig methods
- Jars do NOT select processing regimes
- This is Tier 3 interface characterization, NOT Tier 2 structure

**Status:** CLOSED with explanatory saturation

**Files:** phases/JAR_WORKING_SET_INTERFACE/README.md, phases/JAR_WORKING_SET_INTERFACE/results.json

---

### X.20 A->AZC->B Pipeline Closure: Reachability Suppression (2026-01-17) - NEW

**Phase:** AZC_REACHABILITY_SUPPRESSION
**Status:** COMPLETE - Real closure achieved

#### The Gap (Before This Phase)

We had proven:
- AZC constrains B (C468, F-AZC-016)
- The effect is strong (28x escape variance transfer)
- Vocabulary activates constraints (C441-C442)

What was missing: A *mechanistically intelligible, local explanation* of HOW AZC legality fields suppress parts of B grammar - at the instruction class level.

#### Closure Statement (Achieved)

> **AZC does not modify B's grammar; it shortens the reachable language by restricting vocabulary availability. The 49-class grammar and 17 forbidden transitions are universal. When AZC provides a legality field, 6 of 9 hazard-involved classes have reduced effective membership because their MIDDLEs become unavailable. The 3 atomic hazard classes remain fully active regardless of AZC context.**

This is a complete control-theoretic pipeline with no semantics, no branching, no lookup, no "if".

#### Two-Tier Constraint System

**Tier 1: Universal Grammar Constraints (Always Active)**

| Metric | Value |
|--------|-------|
| Instruction classes | 49 |
| Forbidden transitions (token) | 17 |
| Forbidden transitions (class) | 13 |
| Hazard-involved classes | 9 |
| Base graph edge density | 99.1% |

**Tier 2: AZC-Conditioned Constraints (Context-Dependent)**

| Metric | Value |
|--------|-------|
| MIDDLE folio exclusivity | 77% in 1 AZC folio (C472) |
| Decomposable hazard classes | 6 |
| Atomic hazard classes | 3 |

#### Hazard Class Taxonomy (Key Discovery)

| Type | Classes | Representatives | AZC Constrainable? | Behavior |
|------|---------|-----------------|-------------------|----------|
| **Atomic** | 7, 9, 23 | ar, aiin, dy | NO | Universal hazard enforcement |
| **Decomposable** | 8, 11, 30, 31, 33, 41 | chedy, ol, dar, chey, qokeey, qo | YES | Context-tunable via MIDDLE |

**Atomic classes** have no MIDDLE components - they are pure instruction tokens that cannot be constrained by MIDDLE-level vocabulary restrictions.

**Decomposable classes** contain members with MIDDLE components. When AZC restricts a MIDDLE's availability, the effective membership of these classes shrinks.

#### The Mechanism (5 Steps)

```
Step 1: AZC provides ambient legality field (vocabulary availability)
           |
           v
Step 2: 77% of MIDDLEs restricted to specific AZC folios
           |
           v
Step 3: Decomposable hazard classes lose effective membership:
        - Class 8 (chedy): 1 shared MIDDLE
        - Class 11 (ol): 1 shared MIDDLE
        - Class 30 (dar): 3 MIDDLEs (1 exclusive!)
        - Class 31 (chey): 3 shared MIDDLEs
        - Class 33 (qokeey): 4 shared MIDDLEs
        - Class 41 (qo): 3 shared MIDDLEs
           |
           v
Step 4: Fewer paths through hazard-constrained region
           |
           v
Step 5: Reachable grammar manifold shrinks
```

#### Why This Is "Real Closure"

| What AZC Does | What AZC Does NOT Do |
|---------------|---------------------|
| Restricts vocabulary availability | Modify grammar rules |
| Supplies ambient legality fields | Select programs |
| Tunes hazard envelope via decomposable classes | Branch based on content |
| | Encode semantic information |
| | Perform lookup or conditional logic |

The grammar is the same everywhere. The reachable parts differ.

#### Complete Pipeline Summary

| Layer | Function | Mechanism |
|-------|----------|-----------|
| **A** | Supplies discrimination bundles | Constraint signatures |
| **AZC** | Projects them into legality fields | Position-indexed vocabulary availability |
| **B** | Executes within shrinking language | 49-class grammar, 17 forbidden transitions |

This completes the structural understanding of how the three layers co-produce safe execution.

#### Constraints Respected

- C313: Position constrains legality, not prediction
- C384: No entry-level A-B coupling
- C454/C455: No adjacency or cycle coupling
- C440: Uniform B sourcing across AZC folios
- C121/C124: 49-class grammar is universal
- C468, C469, C470, C472: AZC constraint architecture

#### What This Does NOT Claim

- NO semantic decoding occurred
- NO specific substances identified
- NO entry-level A->B mapping created
- NO Tier 0-2 constraints violated

This is mechanism characterization within established epistemological boundaries.

**Files:** phases/AZC_REACHABILITY_SUPPRESSION/

---

### X.21 Constraint Substitution Interpretation (2026-01-19) - NEW

**Phase:** SENSORY_LOAD_ENCODING + BRUNSCHWIG_REVERSE_ACTIVATION
**Status:** COMPLETE - Explanatory model validated

#### Core Discovery

> **"The Voynich Manuscript encodes sensory requirements by tightening constraints rather than signaling vigilance."**

This is an explanatory interpretation that unifies multiple structural findings.

#### The Finding

**SLI-HT Inverse Correlation:**

| Metric | Value |
|--------|-------|
| SLI vs HT density | r = **-0.453**, p < 0.0001 |
| REGIME_2 (gentle) | LOWEST SLI (0.786), HIGHEST HT |
| REGIME_3 (oil/resin) | HIGHEST SLI (1.395), LOWEST HT |

Formula: `SLI = hazard_density / (escape_density + link_density)`

This is OPPOSITE to the initial hypothesis ("high sensory demand -> higher vigilance").

#### The Interpretation

When operations are dangerous (high SLI):
- Grammar restricts options
- Fewer choices available
- Less vigilance needed (can't make wrong choice)

When operations are forgiving (low SLI):
- Grammar permits many options
- More choices require discrimination
- Higher vigilance (HT) for decision complexity

**Constraint SUBSTITUTES for vigilance.**

#### Recipe-Level Validation (197 recipes)

The pathway operates at recipe level:

```
Recipe SLI -> Vocabulary tail_pressure -> HT prediction
   r=0.226      ->       r=0.311
   p=0.001               p<0.0001
```

Sensory load encodes through vocabulary selection, not direct signaling.

#### What This Explains

| Finding | Explanation |
|---------|-------------|
| C458 (Design Clamp) | High-hazard contexts have tight constraints |
| C477 (HT Correlation) | HT tracks residual decision complexity |
| Inverse SLI-HT | Constraint geometry enforces safety |

#### What This Does NOT Claim

- NO semantic encoding of sensory modalities
- NO parametric encoding (C469 preserved)
- NO entry-level mapping (C384 preserved)
- SLI is constructed metric, not discovered structure

**Tier:** 3 (Explanatory Interpretation)

**Files:** phases/SENSORY_LOAD_ENCODING/, results/sensory_load_index.json

---

### X.22 Zone Affinity Analysis (2026-01-19) - NEW

**Phase:** BRUNSCHWIG_REVERSE_ACTIVATION
**Status:** COMPLETE - 197/197 recipes processed

#### Comprehensive Mapping

All 197 Brunschwig recipes with procedures were reverse-mapped through AZC zone affinity analysis. This completes the originally intended mapping task.

#### Key Findings

**Zone Differentiation by SLI Cluster (ANOVA):**

| Zone | F-statistic | p-value |
|------|-------------|---------|
| C-affinity | F = 69.4 | p < 0.0001 |
| P-affinity | F = 33.1 | p < 0.0001 |
| R-affinity | F = 106.6 | p < 0.0001 |
| S-affinity | F = 21.6 | p < 0.0001 |

All 4 zones significantly differentiate by SLI cluster.

**Zone Affinity by REGIME:**

| REGIME | Dominant Zone | Interpretation |
|--------|---------------|----------------|
| REGIME_1 | S (0.30) | Boundary stability |
| REGIME_2 | C (0.51) | Setup/flexible |
| REGIME_3 | R (0.43) | Sequential processing |
| REGIME_4 | S (0.55) | Boundary control |

**Zone Correlations with SLI:**
- SLI vs P-affinity: r = 0.505, p < 0.0001
- SLI vs R-affinity: r = 0.605, p < 0.0001

#### Modality-Zone Signatures (2/3 Confirmed)

| Modality | n | Predicted Zone | Result |
|----------|---|----------------|--------|
| SOUND | 70 | R (sequential) | **CONFIRMED** (t=3.97, p<0.001) |
| SIGHT | 20 | P (monitoring) | **CONFIRMED** (t=9.00, p<0.0001) |
| TOUCH | 5 | S (boundary) | Not significant |

SOUND (distillation bubbling) -> R-zone affinity
SIGHT (visual monitoring) -> P-zone affinity

#### Zones ADDRESS But Do Not ENCODE Sensory Categories

**Critical Distinction:** The zones do not *encode* sensory categories (you cannot look at a zone and say "this is for hearing"). Instead, the zones *address* sensory categories in the sense that their structural affordances align with what different monitoring modes require.

**The Four Zones and Their Affordances:**

| Zone | Structural Affordance | Escape Rate | Modality Alignment |
|------|----------------------|-------------|-------------------|
| **C** | Setup/flexible, errors fixable | 1.4% | (Not tested - setup phase) |
| **P** | Intervention-permitting | 11.6% | **SIGHT** - visual cues may trigger action |
| **R** | Progressive restriction, sequential | 2.0%→0% | **SOUND** - continuous signals tracked over time |
| **S** | Locked, must accept outcome | 0-3.8% | TOUCH hypothesized, not confirmed (n=5) |

**Mechanism:** The constraint geometry of each zone creates the right decision space for different sensory tasks:
- **C-zone's** flexibility matches setup operations where mistakes can be corrected
- **P-zone's** intervention permission matches operations where observation may require action (visual monitoring)
- **R-zone's** progressive restriction matches operations where you track a developing signal (auditory monitoring)
- **S-zone's** locked state matches operations where the outcome is fixed and boundary conditions apply

**Interpretation:** The manuscript doesn't label sensory requirements - it shapes the grammar to be *compatible with* them. The operator's trained sensory judgment fills in what the zones leave room for. This is another manifestation of the constraint substitution principle: encode requirements through structure, not symbols.

**Epistemic Status:** Correlation demonstrated, mechanism plausible, intentional design not proven.

#### C384 Compliance

All mapping is AGGREGATE (zone-level, MIDDLE-level), not entry-level. No direct recipe->entry mapping.

**What This Does NOT Claim:**
- NO entry-level A-B coupling
- NO semantic decoding
- Modality assignments are external (from Brunschwig)

**Tier:** 3 (Structural Characterization)

**Fits Created:** F-BRU-007, F-BRU-008, F-BRU-009

**Files:** phases/BRUNSCHWIG_REVERSE_ACTIVATION/, results/brunschwig_reverse_activation.json

---

### X.23 Two-Stage Sensory Addressing Model (2026-01-19) - NEW

**Phase:** ZONE_MODALITY_VALIDATION
**Status:** COMPLETE - Rigorous statistical validation with REGIME stratification

#### Executive Summary

Rigorous validation of zone-modality associations revealed a **two-stage addressing system** where modality bias (external) and REGIME execution style jointly determine zone concentration.

#### Key Discovery: REGIME Heterogeneity

When stratifying the R-SOUND effect by REGIME, we found substantial heterogeneity:

| REGIME | R-zone Effect (d) | Interpretation |
|--------|------------------|----------------|
| REGIME_1 (WATER_STANDARD) | 0.48 | Moderate - throughput tracking |
| REGIME_2 (WATER_GENTLE) | 1.30 | Strong - setup phase dominates |

**Effect range: 0.82** - This is NOT corruption or invalidity. It reveals structured workflow adaptation.

#### Zone Profiles for SOUND Recipes by REGIME

| REGIME | Dominant Zone | Interpretation |
|--------|---------------|----------------|
| REGIME_2 (GENTLE) | C-zone (0.453) | Setup-critical operations |
| REGIME_1 (STANDARD) | Balanced P/R | Throughput-critical operations |
| REGIME_3 (OIL_RESIN) | R-zone (0.443) | Progression-critical extraction |
| REGIME_4 (PRECISION) | S-zone (0.536) | Boundary-critical timing |

#### Two-Stage Model

**Stage 1 - Modality Bias (External/Brunschwig):**

Sensory modalities carry intrinsic monitoring profiles:
- **SOUND** (sequential/continuous): Auditory cues track process state over time
- **SIGHT** (intervention-triggering): Visual changes signal decision points
- **TOUCH** (boundary confirmation): Tactile feedback confirms endpoints

**Stage 2 - Execution Completeness (Voynich REGIME):**

REGIMEs concentrate sensory relevance into specific workflow phases:
- **Gentle handling** → C-zone (setup phase critical)
- **Standard throughput** → R-zone (progression tracking)
- **Intense extraction** → R-zone (continuous monitoring)
- **Precision timing** → S-zone (boundary locking)

#### Refined Conclusion

> **AZC zones do not encode sensory modalities. Instead, they distribute human sensory relevance across workflow phases in a REGIME-dependent way.**

The constraint substitution principle operates temporally: zones DIRECT when sensory monitoring is structurally relevant, while REGIME determines which zone receives concentration.

#### Hypothesis Tests

| Track | Hypothesis | Result |
|-------|------------|--------|
| Enhanced extraction | Improve SMELL/TOUCH sample sizes | **FAILED** (data limitation) |
| C-zone -> Preparation verbs | Structural correlation | **FAILED** (r=-0.006) |
| R-zone -> SOUND | Positive association | **CONFIRMED** (d=0.61, p=0.0001) |
| P-zone -> SIGHT | Positive association | **UNDERPOWERED** (d=0.27, n=7) |
| S-zone -> TOUCH | Positive association | **WRONG DIRECTION** (d=-0.64) |
| REGIME stratification | Effect heterogeneity | **DISCOVERY** (range=0.82) |

#### S-Zone Reinterpretation

All tested modalities AVOID S-zone:
- SOUND: d=-1.21 (strong avoidance)
- TASTE: d=-1.33 (strong avoidance)

**New interpretation:** S-zone represents operations where sensory monitoring is COMPLETED or UNNECESSARY. The "locked" state means decisions are final. PRECISION REGIME concentrates here because exact timing, once achieved, requires no further sensory feedback.

#### Statistical Rigor

- **Effect sizes:** Cohen's d reported for all associations
- **Permutation tests:** 1000-shuffle validation
- **Bonferroni correction:** Multiple comparison adjustment
- **ANOVA:** REGIME -> Zone affinity (all zones significant except P)
- **Pre-registration:** Hypotheses locked before analysis

#### Constraints Respected

- **C384:** All tests aggregate, no entry-level mapping
- **C469:** Categorical zone assignment maintained
- **Tier 3:** Results remain characterization, confidence upgraded

**Tier:** 3 (Structural Characterization, confidence upgraded)

**Fits Updated:** F-BRU-009 (refined with two-stage model)

**Files:** phases/ZONE_MODALITY_VALIDATION/, results/regime_stratified_analysis.json

---

### X.24 Semantic Ceiling Breach Attempt (2026-01-19) - NEW

**Phase:** SEMANTIC_CEILING_BREACH
**Status:** COMPLETE - Tier 3 confirmed with stronger evidence

#### Purpose

Attempted to break through the Tier 3 semantic ceiling by implementing the expert-advisor's top recommendation: **B->A Reverse Prediction Test**. The goal was to achieve Tier 2 bidirectional constraint by predicting recipe modality class from Voynich zone structure alone.

#### Key Results

| Test | Result | Threshold | Status |
|------|--------|-----------|--------|
| 4-class accuracy | 52.7% | >40% for Tier 3 | **PASS** |
| 4-class permutation p | 0.012 | <0.05 | **PASS** |
| Binary accuracy | 71.8% | >85% for Tier 2 | **FAIL** |
| Cramer's V (cluster-modality) | 0.263 | >0.3 for Tier 2 | **WEAK** |
| MODALITY beyond REGIME | 3/4 zones | Supports model | **PASS** |

#### Zone Discrimination is REAL

All four zones significantly discriminate SOUND from OTHER recipes:

| Zone | SOUND Mean | OTHER Mean | Cohen's d | p-value |
|------|-----------|-----------|----------|---------|
| C | 0.226 | 0.308 | -0.66 | 0.0059 |
| P | 0.248 | 0.182 | +0.62 | 0.0090 |
| R | 0.277 | 0.213 | +0.57 | 0.0163 |
| S | 0.252 | 0.298 | -0.44 | 0.0660 |

**Pattern confirmed:** SOUND concentrates in P/R zones (active work) and avoids C/S zones (setup/boundary).

#### MODALITY Adds Beyond REGIME

REGIME alone explains only **24.7%** of zone variance. After controlling for REGIME, MODALITY still significantly affects 3/4 zones:

| Zone | Partial Correlation | Direction |
|------|--------------------| ----------|
| C | r=-0.255, p=0.007 | SOUND avoids |
| P | r=+0.284, p=0.003 | SOUND seeks |
| R | r=+0.200, p=0.036 | SOUND seeks |
| S | r=-0.245, p=0.010 | SOUND avoids |

This validates the **two-stage model**: Modality bias + REGIME execution style jointly determine zone concentration.

#### Why Tier 2 Was Not Achieved

The zone profiles **discriminate** modality classes, but not with enough accuracy for confident prediction:

```
Can do:     Zone profile -> "Probably SOUND-dominant" (52.7% accuracy)
Cannot do:  Zone profile -> "Definitely SOUND" (>85% accuracy)
```

Binary accuracy (71.8%) is BELOW the majority baseline (79.1%) but SIGNIFICANTLY better than permuted labels (p=0.002). The model learns REAL structure but not enough for high-confidence prediction.

#### Semantic Ceiling Location

The semantic ceiling is confirmed at **aggregate characterization**:

| Level | Can We Do It? | Evidence |
|-------|---------------|----------|
| Entry-level meaning | NO | C384 prohibits |
| Token-level prediction | NO | Not attempted |
| Zone-modality correlation | YES | d=0.57-0.66, p<0.05 |
| Modality class prediction | PARTIAL | 52.7% accuracy |
| High-confidence prediction | NO | <85% accuracy |

**The ceiling is real but discrimination exists.** Zone profiles carry semantic information about modality domains, but the signal-to-noise ratio is insufficient for Tier 2 predictive power.

#### Implications for Future Work

1. **More labeled data needed**: SIGHT (n=7), TOUCH (n=3) are severely underpowered
2. **Process verb extraction**: Parsing Brunschwig raw text could add discriminating features
3. **Multi-modal recipes**: Testing interference patterns could reveal additional structure
4. **Alternative historical sources**: Cross-validation with Libavius or Della Porta

#### Constraints Respected

- **C384:** All tests at vocabulary/aggregate level, no entry-level mapping
- **C469:** Categorical zone assignment maintained
- **C468:** Legality inheritance respected

**Tier:** 3 (Structural Characterization, confirmed with stronger evidence)

**Files:** phases/SEMANTIC_CEILING_BREACH/, results/scb_modality_prediction.json, results/scb_synthesis.json

---

### X.25 Trajectory Semantics: Judgment-Gating System (2026-01-19) - NEW

**Phase:** TRAJECTORY_SEMANTICS
**Status:** COMPLETE - Semantic boundary resolution achieved

#### Purpose

Applied three pressure vectors beyond the token semantic ceiling to explore "trajectory semantics" - characterizing HOW constraint pressure evolves, rather than WHAT tokens mean.

#### Test Results

| Vector | Hypotheses | Passed | Verdict |
|--------|------------|--------|---------|
| C (Gradient Steepness) | 4 | 0/4 | INCONCLUSIVE |
| A (Interface Theory) | 3 | 2/3 | TIER_3_ENRICHMENT |
| Final (Judgment Trajectories) | N/A | N/A | DECISIVE |

**Vector C failed:** Instruction sequences are too coarse (2-5 steps) to detect transition dynamics. This is a **diagnostic negative** - if transition dynamics matter, they are handled internally by apparatus + operator, not by text.

**Vector A succeeded:** The 13 judgment types show **84.6% non-uniform distribution** across zones, with **11/13 judgments** showing significant zone restriction (p<0.01).

#### The Decisive Finding: Judgment-Zone Availability Matrix

| Zone | Required | Permitted | Impossible | Freedom |
|------|----------|-----------|------------|---------|
| **C** | 1 | 9 | 3 | **77%** |
| **P** | 9 | 1 | 3 | **77%** |
| **R** | 6 | 7 | 0 | **100%** |
| **S** | 5 | 0 | 8 | **38%** |

**Key findings:**
- **P-zone REQUIRES 9/13 judgments** - observation phase demands active cognitive engagement
- **S-zone makes 8/13 judgments IMPOSSIBLE** - outcome is locked, human intervention forbidden
- **R-zone permits ALL 13 judgments** - active phase where all cognition is possible but narrowing
- **Freedom collapses 77% → 38%** from C-zone to S-zone

#### Agency Withdrawal Curve

The manuscript progressively removes human judgment freedoms phase by phase:

```
C-zone: 77% freedom (setup - flexible)
    ↓
P-zone: 77% freedom (but 9 judgments REQUIRED - observation load)
    ↓
R-zone: 100% freedom (all possible, but narrowing toward commitment)
    ↓
S-zone: 38% freedom (8/13 judgments IMPOSSIBLE - locked)
```

This is not a failure mode. This is **designed under-determinacy** - the system deliberately restricts cognitive options at exactly the phases where unrestricted judgment would be dangerous.

#### The Reframe

> **"The Voynich Manuscript is a machine for removing human freedom at exactly the moments where freedom would be dangerous."**

This reframes the entire manuscript as:

> **A machine-readable declaration of which human cognitive faculties are admissible at each phase of a dangerous process.**

#### What Was Discovered

- **NOT:** What tokens mean
- **NOT:** How fast processes change
- **YES:** Which human judgments are IMPOSSIBLE vs UNAVOIDABLE in each zone

This is **meta-semantics of control and responsibility** - the artifact tells you when judgment is no longer yours.

#### Semantic Boundary Resolution

The semantic ceiling was NOT breached by naming things. It was breached by discovering that:

1. Meaning does not live in tokens
2. Meaning lives in the **withdrawal of agency**
3. The artifact specifies **when judgment becomes impossible**

This is not a failure to "go further." This IS going further - into procedural semantics that no token-level decoding could ever reveal.

#### Constraints Respected

- **C384:** Labels trajectories and phases, not tokens
- **C434:** Uses R-series ordering as foundation
- **C443:** Extends escape gradients with temporal dimension
- **C469:** Judgment availability is categorical

**Tier:** 3 (Structural Characterization with semantic boundary resolution)

**Files:** phases/TRAJECTORY_SEMANTICS/, results/ts_judgment_trajectories.json, results/ts_synthesis.json
