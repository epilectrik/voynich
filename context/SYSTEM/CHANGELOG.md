# Context System Changelog

**Purpose:** Track changes to the context system structure and content.

---

## Version 2.20 (2026-01-12) - MIDDLE Atomic Incompatibility (C475)

### Summary

**MIDDLE-level compatibility is extremely sparse (4.3% legal), forming a hard incompatibility lattice.** This is the atomic discrimination layer - everything above it (A entries, AZC folios, families, HT) is an aggregation of this graph.

### Core Finding

> **95.7% of MIDDLE pairs are illegal. Only 4.3% can co-occur on the same specification line. This sparsity is robust to context definition (97.3% overlap with 2-line sensitivity check).**

### Probe Results (middle_incompatibility.py)

| Metric | Value |
|--------|-------|
| Total MIDDLEs | 1,187 |
| Total possible pairs | 703,891 |
| **Legal pairs** | **30,394 (4.3%)** |
| **Illegal pairs** | **673,342 (95.7%)** |
| Trivially absent | 155 |
| Connected components | 30 |
| Largest component | 1,141 (96% of MIDDLEs) |
| Isolated MIDDLEs | 20 |

### PREFIX Clustering (H1 - SUPPORTED)

| Type | Legal % | Interpretation |
|------|---------|----------------|
| Within-PREFIX | 17.39% | Soft prior for compatibility |
| Cross-PREFIX | 5.44% | Hard exclusion boundary |
| **Ratio** | **3.2x** | PREFIX is first partition |

### Key Structural Objects Identified

1. **Universal Connector MIDDLEs** ('a', 'o', 'e', 'ee', 'eo')
   - Compatibility basis elements
   - Bridge otherwise incompatible regimes
   - "Legal transition anchors"

2. **Isolated MIDDLEs** (20 total)
   - Hard decision points
   - "If you specify this, you cannot specify anything else"
   - Pure regime commitment

3. **PREFIX = soft prior, MIDDLE = hard constraint**
   - PREFIX increases odds of legality ~3x
   - MIDDLE applies near-binary exclusions

### Reconciliation with Prior Constraints

| Constraint | Previous | Now Resolved |
|------------|----------|--------------|
| C293 | MIDDLE is primary discriminator | Quantified: 95.7% exclusion rate |
| C423 | PREFIX-bound vocabulary | PREFIX is first partition, MIDDLE is sharper |
| C437-C442 | Why so many AZC folios? | AZC = projections of sparse graph |
| C459, C461 | HT anticipatory function | HT ≈ incompatibility density (testable) |

### f116v Correction

f116v folio-level isolation (from v2.19) is explained by **data sparsity** (only 2 words in AZC corpus), NOT by MIDDLE-level incompatibility. The f116v MIDDLEs ('ee', 'or') are actually universal connectors.

### New Constraint

**C475 - MIDDLE ATOMIC INCOMPATIBILITY** (Tier 2, CLOSED)
- Added to `context/CLAIMS/currier_a.md`

### Interpretation

> **The MIDDLE vocabulary forms a globally navigable but locally forbidden discrimination space. This is the strongest internal explanation yet of why the Voynich Manuscript looks the way it does without invoking semantics.**

### What This Enables (Bayesian Roadmap)

1. **Latent Discrimination Axes Inference** - How many latent axes explain the incompatibility graph?
2. **Probabilistic A Bundle Generator** - Can MIDDLE incompatibility + line length + PREFIX priors reproduce A entries?
3. **HT Variance Decomposition** - How much HT density is explained by local incompatibility degree?

### Updated Files

- `phases/MIDDLE_INCOMPATIBILITY/middle_incompatibility.py` - Main probe
- `results/middle_incompatibility.json` - Full results
- `context/CLAIMS/currier_a.md` - Added C475
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Updated

### Significance

This is a **regime change** in what kind of modeling is now possible. We've reached bedrock - the atomic discrimination layer. All higher-level structure (A, AZC, HT) can now be understood as aggregations of this sparse graph.

---

## Version 2.19 (2026-01-12) - AZC Compatibility at Specification Level

### Summary

**AZC compatibility filtering operates at the Currier A constraint-bundle level, not at execution level.** Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both. 10.3% of folio pairs are unbridged, with f116v being structurally isolated.

### Key Finding

> **Currier A entries define which AZC vocabularies can be jointly activated. Most folio pairs are compatible, but ~10% are not—with f116v being a structurally isolated discrimination regime. AZC compatibility is enforced at specification (A-bundle) level, not at execution or folio-presence level.**

### Probe Results

| Metric | Value |
|--------|-------|
| Total folio pairs | 435 |
| Bridged pairs | 390 (89.7%) |
| **Unbridged pairs** | **45 (10.3%)** |
| Graph connectivity | FULLY_CONNECTED |

### Family-Level Coherence

| Family Type | % Unbridged | Interpretation |
|-------------|-------------|----------------|
| Within-Zodiac | **0.0%** | Interchangeable discrimination contexts |
| Within-A/C | **14.7%** | True fine-grained alternatives |
| Cross-family | **11.3%** | Partial overlap, partial incompatibility |

### f116v Structural Isolation

f116v shares NO bridging tokens with most other folios:
- Vocabulary uniquely concentrated
- Cannot be jointly specified with most other constraint bundles
- Can still appear in B executions (C440 holds)
- Defines a discrimination profile incompatible at A-level

### C442 Refinement

Previous understanding: "94% unique vocabulary per folio"

Refined understanding:
> **AZC compatibility filtering operates at the level of Currier A constraint-bundle co-specification. Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both.**

Corollaries:
- Folios are NOT execution-exclusive
- Folios are NOT globally incompatible
- Incompatibility exists only at **specification time**
- Disallowed combinations leave no discrete trace—they simply never occur

### Why This Matters

This resolves family-level coherence:
- **Zodiac (0% unbridged)**: Supports sustained HT flow—interchangeable contexts
- **A/C (14.7% unbridged)**: Causes punctuated HT resets—true alternatives
- **Execution difficulty unchanged**: CEI, recovery, hazard models unaffected

### Updated Files

- `phases/AZC_COMPATIBILITY/azc_entry_bridges.py` - Correct probe
- `phases/AZC_COMPATIBILITY/azc_folio_compatibility.py` - First probe (coarse)
- `results/azc_entry_bridges.json` - Bridge analysis results
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.5
- `context/CLAIMS/azc_system.md` - C442 refined

### Significance

This is a **Tier-2 advance**:
- Pinpoints the mechanism of AZC compatibility (A-bundle level)
- Identifies f116v as structurally isolated
- Explains Zodiac coherence vs A/C alternatives
- Connects discrimination regimes to specification constraints

---

## Version 2.18 (2026-01-11) - AZC-Based Currier A Clustering

### Summary

**AZC folio co-occurrence can reverse-cluster Currier A entries, revealing sub-families within PREFIX classes.** The y- PREFIX shows a family split: some y- tokens cluster with Zodiac contexts, others with A/C contexts.

### Key Finding

> **PREFIX morphology does not fully determine AZC family affinity. Some PREFIX classes (notably y-) contain sub-families that differ in their discrimination-regime membership.**

### Probe Results

| Metric | Value |
|--------|-------|
| Currier A tokens in AZC | 778 (16% of vocabulary) |
| Tokens eligible for clustering | 367 (appear in 2+ AZC folios) |
| Sub-families detected | y- (FAMILY_SPLIT) |

### PREFIX → AZC Family Baseline (confirms C471)

| PREFIX | Zodiac % | A/C % | Bias |
|--------|----------|-------|------|
| qo- | 18.8% | 71.9% | A/C |
| d- | 14.5% | 62.9% | A/C |
| or- | 58.3% | 16.7% | Zodiac |
| ot- | 25.0% | 25.0% | BALANCED |
| **y-** | 28.1% | 46.9% | **SPLIT** |

### y- Family Split Evidence

| Cluster | Family Bias | Sample Tokens | Shared Folios |
|---------|-------------|---------------|---------------|
| 66 | 85.7% Zodiac | ytaly, opaiin, alar | f72v1, f73v |
| 61 | 69.7% A/C | okeod, ykey, ykeeody | f69v, f73v |

### Interpretation

y- does not behave like a single material class. It spans both discrimination regimes, suggesting:

1. **y- encodes something orthogonal to the Zodiac/A-C axis**
2. **y- may be a modifier or state marker** rather than a material class
3. **Regime-independent function** - applies in both coarse and fine discrimination contexts

### Extreme Family Clusters (100% bias)

| Cluster | Bias | Tokens | Shared Folios |
|---------|------|--------|---------------|
| 67 | 100% Zodiac | okeoly, dalal, otalal | f70v2, f72v1 |
| 38 | 100% A/C | om, oir, ykaly | f67v2, f67r2 |
| 139 | 100% Zodiac | okam, okaldy, chas | f72r2, f72v3 |

### Updated Files

- `phases/EFFICIENCY_REGIME_TEST/azc_based_a_clustering.py` - Clustering probe
- `results/azc_based_a_clustering.json` - Full results
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.4, y- finding
- `context/SPECULATIVE/efficiency_regimes.md` - Added y- evidence

### Significance

This probe demonstrates that AZC can be used in reverse to reveal structure within Currier A vocabulary that PREFIX morphology alone doesn't show. The y- split provides evidence that some morphological markers encode regime-independent properties.

---

## Version 2.17 (2026-01-11) - Perceptual Discrimination Regime Synthesis

### Summary

**HT oscillation analysis completes the regime interpretation.** The concurrency management probe falsified the parallel-batch hypothesis but revealed the correct explanatory axis: discrimination complexity determines attentional flow patterns.

### Key Finding

> **Where discrimination is fine, attention becomes punctuated; where discrimination is coarse, attention can flow.**

### HT Oscillation Results

| Family | HT Density | Oscillation Score | Interpretation |
|--------|-----------|-------------------|----------------|
| Zodiac | 0.131 | 0.060 | Sustained attentional flow |
| A/C | 0.236 | 0.110 | Punctuated attentional checkpoints |

**A/C shows ~80% higher HT oscillation than Zodiac.**

### Falsified Hypotheses

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| Parallel batch management | FALSIFIED | HT oscillation reversed from prediction |
| Zodiac = high context switching | FALSIFIED | Zodiac has LOWER oscillation |

### The Coherent Explanatory Axis (All Layers Aligned)

| Layer | Zodiac | A/C |
|-------|--------|-----|
| Currier A | Coarse categories | Fine distinctions |
| AZC | Uniform scaffolds | Varied scaffolds |
| HT | Sustained flow | Punctuated checkpoints |
| Currier B | Same difficulty | Same difficulty |
| CEI | Same effort | Same effort |

### Final Interpretation (Tier 3 - VALIDATED)

> Zodiac and A/C AZC families correspond to regimes of perceptual discrimination complexity rather than operational difficulty. Zodiac contexts permit coarse categorization and sustained attentional flow, while A/C contexts require finer categorical distinctions, producing punctuated attentional checkpoints reflected in higher HT oscillation. Execution grammar absorbs this difference, resulting in no detectable change in behavioral brittleness or CEI.

### Updated Files

- `context/SPECULATIVE/efficiency_regimes.md` - Final validated interpretation
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.3, coherent axis table
- `phases/EFFICIENCY_REGIME_TEST/test_concurrency_management.py` - HT probe
- `results/concurrency_management_probe.json` - HT test output

### Significance

This is the first interpretation that cleanly integrates ALL layers (A, AZC, B, HT, CEI) without contradiction. The internal evidence has been exhausted correctly, by falsification rather than narrative preference.

---

## Version 2.16 (2026-01-11) - Lexical Granularity Regime Validation

### Summary

**This phase empirically tested the "efficiency regime" interpretation of Zodiac vs A/C.** The results localized the signal to the vocabulary layer and falsified behavioral-level claims.

### Key Finding

> **Zodiac vs A/C encodes regimes of lexical discrimination, not regimes of operational difficulty; the control grammar absorbs lexical complexity so that execution behavior remains stable.**

### Test Results

| Test | Result | Interpretation |
|------|--------|----------------|
| MIDDLE Discrimination Pressure | WEAK SUPPORT | 5/15 prefixes show gradient, 0 reversed |
| Residual Brittleness Analysis | **FAILED** | Effect is PREFIX-morphological, not regime-based |
| Universal MIDDLE Negative Control | **PASSED** | Universal MIDDLEs regime-neutral (58.7%), Exclusive biased (64.8%) |
| Family Escape Transfer | PARTIAL | Weak positive correlation (r=0.265) |

**Overall Verdict: WEAK_PARTIAL**

### What IS Supported (Lexical Level)

- MIDDLE discrimination is genuinely family-biased
- Universal MIDDLEs are regime-neutral; Exclusive MIDDLEs show A/C bias
- A/C contexts require finer vocabulary distinctions; Zodiac uses broader categories

### What Is NOT Supported (Behavioral Level - FALSIFIED)

- A/C = operationally brittle (REJECTED)
- Zodiac = operationally forgiving (REJECTED)
- Family affects CEI or recovery (REJECTED)
- Efficiency stress propagates to B programs (REJECTED)

### New Insight

**CEI measures control strain *within* execution, not *between* lexical regimes.**

CEI and AZC family live on orthogonal axes:
- CEI = trajectory management within execution
- AZC family = what distinctions exist ahead of time

### Updated Files

- `context/SPECULATIVE/efficiency_regimes.md` - Renamed, tested, revised
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.2, updated regime section
- `phases/EFFICIENCY_REGIME_TEST/` - Four test scripts + synthesis
- `results/efficiency_regime_*.json` - All test outputs

### Methodology Note

This represents a proper falsification attempt, not confirmation bias. The test suite was designed with pre-declared stop conditions and negative controls. The partial failure is a scientific success: it precisely located where the signal exists (vocabulary) vs where it does not (behavior).

---

## Version 2.15 (2026-01-11) - Morphological Binding Phase Closure

### Summary

**This phase resolved the interface between Currier A, AZC, and Currier B.** The binding logic that connects vocabulary composition to constraint activation is now morphologically encoded, causally active, and empirically validated.

### The One-Sentence Takeaway

> **Currier A records define which worlds are allowed to exist, AZC defines what is legal in each world and when recovery is possible, and Currier B blindly executes - leaving the consequences of earlier discriminations unavoidable but structurally bounded.**

### New Constraints

- **C471** - PREFIX Encodes AZC Family Affinity (Tier 2)
  - qo- and ol- strongly enriched in A/C AZC folios (91% / 81%)
  - ot- enriched in Zodiac folios (54%)
  - ch-, sh-, ok- broadly distributed
  - Statistical affinity, not exclusive mapping

- **C472** - MIDDLE Is Primary Carrier of AZC Folio Specificity (Tier 2)
  - PREFIX-exclusive MIDDLEs (77%) exhibit median entropy = 0.0
  - Typically appear in exactly one AZC folio
  - Shared MIDDLEs span multiple folios (18.7% vs 3.3% coverage)
  - MIDDLE is principal determinant of folio-level constraints

- **C473** - Currier A Entry Defines a Constraint Bundle (Tier 2)
  - A entry does not encode addressable object or procedure
  - Morphological composition specifies compatibility signature
  - Determines which AZC legality envelopes are applicable

### Final Definitions (Locked)

- **Currier A record** = Pre-execution compatibility declaration
- **AZC folio** = Complete legality regime (permissions + recoveries)
- **Currier B program** = Blind execution against filtered vocabulary

### Closure Declarations

**Pipeline Resolution & Morphological Binding: CLOSED**

No remaining degrees of freedom. The binding logic is:
- PREFIX -> AZC family affinity
- MIDDLE -> AZC folio specificity
- Together: each vocabulary item carries a compatibility signature

**Additional closures (do NOT reopen):**
- Naming or meaning of AZC folios (they are legality regimes)
- Aligning A entries to specific B programs (vocabulary-mediated)

### Updated Files

- `context/CLAIMS/azc_system.md` - Added C471-C473, morphological binding section
- `context/CLAUDE_INDEX.md` - Updated to v2.8, 335 constraints
- `context/MAPS/claim_to_phase.md` - Added C471-C473 mapping
- `phases/INTEGRATION_PROBE/` - Three probe scripts archived
- `results/integration_probe_*.json` - Probe results saved

---

## Version 2.14 (2026-01-11) - Pipeline Resolution Phase Closure

### Summary

**This phase achieved structural closure on the A -> AZC -> B pipeline.** The decisive finding: AZC constraint profiles propagate causally into Currier B execution behavior.

### New Constraints

- **C468** - AZC Legality Inheritance (Tier 2)
  - Tokens from high-escape AZC contexts show 28.6% escape in B
  - Tokens from low-escape AZC contexts show 1.0% escape in B
  - 28x difference confirms causal constraint transfer

- **C469** - Categorical Resolution Principle (Tier 2)
  - Operational conditions represented categorically via token legality
  - Not parametrically via encoded values
  - Physics exists externally; representation is categorical

- **C470** - MIDDLE Restriction Inheritance (Tier 2)
  - Restricted MIDDLEs (1-2 AZC folios): 4.0 B folio spread
  - Universal MIDDLEs (10+ AZC folios): 50.6 B folio spread
  - 12.7x difference confirms constraint transfer

### New Fits

- **F-AZC-015** - Windowed AZC Activation Trace
  - Case B confirmed: 70% of AZC folios active per window
  - High persistence (0.87-0.93): same folios persist
  - AZC is ambient legality field, not dynamic selector

- **F-AZC-016** - AZC->B Constraint Fit Validation
  - MIDDLE restriction transfers: CONFIRMED (12.7x)
  - Escape rate transfers: CONFIRMED (28x)
  - Pipeline causality validated

### Closure Declarations

**Pipeline Resolution Phase: CLOSED**

The A -> AZC -> B control pipeline is structurally and behaviorally validated.

**Do NOT reopen:**
- Entry-level A->B mapping (ruled out by pipeline mechanics)
- Dynamic AZC decision-making (F-AZC-015 closed this)
- Parametric variable encoding (no evidence exists)
- Semantic token meaning (all evidence against)

### Updated Files

- `context/CLAIMS/azc_system.md` - Added C468-C470, closure statement
- `context/MODEL_FITS/fits_azc.md` - Added F-AZC-015, F-AZC-016
- `context/MODEL_CONTEXT.md` - Added Section X.C (Representation Principle)
- `context/CLAUDE_INDEX.md` - Updated to v2.7, 320+ constraints

### Archived Scripts

29 scripts from `phases/AZC_constraint_hunting/` archived to `archive/scripts/AZC_constraint_hunting/`

---

## Version 2.13 (2026-01-10)

### E4: AZC Entry Orientation Trace (C460)

**Summary:** Tested whether AZC folios serve as cognitive entry points by analyzing HT trajectories in their neighborhood. Found significant step-change pattern, but it resembles random positions more than A/B entries.

**New Constraint:**

- **C460** - AZC Entry Orientation Effect (Tier 2)
  - Step-change at AZC: p < 0.002 (all window sizes)
  - Pre-entry HT: above average (+0.1 to +0.28 z-score)
  - Post-entry HT: below average (-0.08 to -0.30 z-score)
  - Gradient: decay, R^2 > 0.86

**Critical Nuance:**
- AZC trajectory differs from A and B systems (p < 0.005)
- AZC trajectory does NOT differ from random (p > 0.08)
- Interpretation: AZC is **placed at** natural HT transitions, not **causing** them

**Zodiac vs Non-Zodiac:**
- Zodiac step-change: -0.39 (stronger)
- Non-zodiac step-change: -0.36

**New Files:**
- `phases/exploration/azc_entry_orientation_trace.py`
- `results/azc_entry_orientation_trace.json`
- `context/CLAIMS/C460_azc_entry_orientation.md`

**Updated Files:**
- `context/CLAIMS/INDEX.md` - Version 2.13, 310 constraints

**Status:** E4 COMPLETE

### E5: AZC Internal Oscillation (Observation Only)

**Question:** Does AZC show internal micro-oscillations matching the global HT rhythm?

**Answer:** No. AZC does not replicate manuscript-wide dynamics internally.
- No significant autocorrelation
- Faster cadence (~3.75 folios vs global ~10)
- Zodiac internally flat; non-Zodiac shows decreasing trend

**Status:** Documented as observation, NOT a constraint. Line of inquiry closed.

**New File:**
- `results/azc_internal_oscillation.json`

---

## Version 2.11 (2026-01-10)

### Intra-Role Differentiation Audit (C458-C459)

**Summary:** Complete audit of intra-folio variation across all four systems. Discovered that risk is globally constrained while human burden and recovery strategy are locally variable. Established HT as anticipatory (not reactive) attention layer.

**Core Finding:**
> The Voynich Manuscript does not vary in how risky its procedures are; it varies in how much *slack, recovery capacity, and human attention* each situation demands - and it encodes that distinction with remarkable consistency across systems.

**New Constraints:**

- **C458** - Execution Design Clamp vs Recovery Freedom (Tier 2)
  - Hazard exposure: CV = 0.04-0.11 (CLAMPED)
  - Recovery operations: CV = 0.72-0.82 (FREE)
  - Regime separation: eta² = 0.70-0.74
  - C458.a: Hazard/LINK mutual exclusion (r = -0.945)

- **C459** - HT Anticipatory Compensation (Tier 2)
  - Quire-level correlation: r = 0.343, p = 0.0015
  - HT before B: r = 0.236, p = 0.032 (significant)
  - HT after B: r = 0.177, p = 0.109 (not significant)
  - Pattern: HT_ANTICIPATES_STRESS
  - C459.a: REGIME_2 shows inverted compensation

**Additional Findings (not constraints):**

- **D2 (AZC Zodiac):** Zodiac folios vary in monitoring vs transition emphasis (CV = 0.15-0.39), no position gradient
- **P1 (Clustering):** 4 natural folio clusters; 4 anomalous folios cluster by HT burden across systems (f41r, f65r, f67r2, f86v5)
- **P2 (Recto-Verso):** No systematic asymmetry (p = 0.79); HT balanced across spreads

**Theoretical Impact:**

| Category | Effect |
|----------|--------|
| Strengthened | Control-artifact model, human-centric design, non-semantic stance |
| Constrained | Danger tied to pages, diagrams encoding execution, HT as reactive |
| Disfavored | Recipe difficulty gradients, didactic sequences, per-page semantics |

**New Files:**
- `phases/exploration/unified_folio_profile.py` - D0
- `phases/exploration/b_design_space_cartography.py` - D1
- `phases/exploration/azc_zodiac_fingerprints.py` - D2
- `phases/exploration/ht_compensation_analysis.py` - D3
- `phases/exploration/folio_personality_clusters.py` - P1
- `phases/exploration/recto_verso_asymmetry.py` - P2
- `phases/exploration/INTRA_ROLE_DIFFERENTIATION_SUMMARY.md` - Synthesis
- `context/CLAIMS/C458_execution_design_clamp.md`
- `context/CLAIMS/C459_ht_anticipatory_compensation.md`

**Results Files:**
- `results/unified_folio_profiles.json` (227 profiles)
- `results/b_design_space_cartography.json`
- `results/azc_zodiac_fingerprints.json`
- `results/ht_compensation_analysis.json`
- `results/folio_personality_clusters.json`
- `results/recto_verso_asymmetry.json`

**Updated Files:**
- `context/CLAIMS/INDEX.md` - Version 2.11, 309 constraints

**Status:** Intra-Role Differentiation Audit COMPLETE.

### Extended Analysis: HT Temporal Dynamics + Anomalous Folios

**HT Temporal Dynamics:**
- Global decreasing trend: r=-0.158, p=0.017 (HT falls through manuscript)
- ~10-folio periodicity: SNR=4.78 (quire-scale oscillation)
- 9 changepoints detected
- Front-loaded: f39r-f67v2 is HIGH region (48 folios), ending is LOW

**Anomalous Folio Investigation:**

All 4 folios that cluster across system boundaries are HT HOTSPOTS:
| Folio | System | HT | Escape | Status |
|-------|--------|-----|--------|--------|
| f41r | B | 0.296 | 0.197 | HOTSPOT |
| f65r | AZC | 0.333 | n/a | HOTSPOT |
| f67r2 | AZC | 0.294 | n/a | HOTSPOT |
| f86v5 | B | 0.278 | 0.094 | HOTSPOT |

**New Files (Extended):**
- `phases/exploration/ht_temporal_dynamics.py`
- `phases/exploration/anomalous_folio_investigation.py`
- `results/ht_temporal_dynamics.json`
- `results/anomalous_folio_investigation.json`

**Deepest Pattern Discovered:**
> The Voynich is not primarily a manual of actions. It is a manual of **responsibility allocation** between system and human.

---

## Version 2.12 (2026-01-10)

### Post-Differentiation Explorations (E1-E3)

**E1: Quire Rhythm Alignment**
- HT changepoints do NOT align with quire boundaries (enrichment=0.59x, p=0.35)
- HT rhythm is CONTENT-DRIVEN, not production-driven
- Quires differ significantly in mean HT level (H=48.2, p<0.0001, eta²=0.149)
- No consistent internal pattern (43% flat)

**E2: Zero-Escape Characterization (CORRECTION)**
- Only 2 B folios have near-zero escape: f33v (0.009), f85v2 (0.010)
- Neither is an HT hotspot
- Zero-escape is RARE (2.4% of B folios)
- No HT difference between zero-escape and normal B (p=0.22)
- **CORRECTED:** f41r and f86v5 are NOT zero-escape (original finding was due to field name bug)

**E3: Anomalous Folio Deep Dive**
- 13 total HT hotspots (6 A, 5 B, 2 AZC)
- The "anomalous 4" (f41r, f65r, f67r2, f86v5) are not unique
- Only f65r is at a system boundary (A→AZC)
- B hotspots span different regimes (REGIME_2, REGIME_4)
- All anomalous folios have ~2x median HT for their system

**Key Corrections:**
- C459.b "zero-escape → max HT" WITHDRAWN (data error)
- Escape density for f41r: 0.197 (not 0)
- Escape density for f86v5: 0.094 (not 0)

**New Files:**
- `phases/exploration/quire_rhythm_analysis.py`
- `phases/exploration/zero_escape_characterization.py`
- `phases/exploration/anomalous_folio_deep_dive.py`
- `results/quire_rhythm_analysis.json`
- `results/zero_escape_characterization.json`
- `results/anomalous_folio_deep_dive.json`

**Updated Files:**
- `context/CLAIMS/C459_ht_anticipatory_compensation.md` - C459.b corrected

**Status:** Post-Differentiation Explorations COMPLETE

---

## Version 2.10 (2026-01-10)

### B Design Space Cartography (C458)

**Summary:** Interim version during Intra-Role audit. See v2.11 for complete documentation.

---

## Version 2.9 (2026-01-10)

### HT-AZC Placement Affinity (C457)

**Summary:** Single focused test of HT-AZC relationship, following the architectural synthesis. Discovered that HT preferentially marks boundary (S) positions over interior (R) positions in Zodiac AZC.

**New Constraint:**

- **C457** - HT Boundary Preference in Zodiac AZC (Tier 2)
  - S-family HT rate: 39.7%
  - R-family HT rate: 29.5%
  - Difference: 10.3 percentage points (p < 0.0001, V = 0.105)
  - HT preferentially marks BOUNDARIES (sector positions)
  - Supports "attention at phase boundaries" interpretation

**Key Insight:**
> AZC defines the boundary structure of experience; HT marks when human attention should increase inside that structure.

**Files Created:**
- `context/CLAIMS/C457_ht_boundary_preference.md`
- `results/ht_azc_placement_affinity.json`
- `phases/exploration/ht_azc_placement_test.py`

**Status:** HT-AZC investigation CLOSED. No further tests needed.

---

## Version 2.8 (2026-01-10)

### Apparatus-Topology Hypothesis Testing (C454-C456)

**Summary:** Rigorous hypothesis testing of whether AZC encodes apparatus-stage alignment. Properly designed tests with pre-registered kill conditions. Hypothesis FALSIFIED, but produced valuable architectural insights.

**New Constraints:**

- **C454** - AZC-B Adjacency Coupling FALSIFIED (Tier 1)
  - B folios near AZC show NO significant metric differences from B folios far from AZC
  - All window sizes (1-5 folios) returned p > 0.01
  - AZC does NOT modulate B execution
  - AZC and B are topologically segregated

- **C455** - AZC Simple Cycle Topology FALSIFIED (Tier 1)
  - Zodiac AZC is NOT a single ring/cycle
  - Multiple independent cycles (cycle_rank = 5)
  - Non-uniform degree distribution (CV = 0.817)
  - "Literal apparatus diagram" interpretation rejected

- **C456** - AZC Interleaved Spiral Topology (Tier 2)
  - Zodiac shows R-S-R-S alternating pattern
  - R1 -> S1 -> R2 -> S2 -> R3
  - Consistent with cognitive orientation scaffolding
  - Alternation represents interior (R) vs boundary (S) states

**Architectural Synthesis:**

Created `context/ARCHITECTURE/layer_separation_synthesis.md` explaining:
- Why execution (B) must be context-free
- Why orientation (AZC) must be execution-free
- Why legality != prediction
- Why humans need spatial scaffolds for cyclic processes

**The Answer:**
> Why are there spatial diagrams that don't seem to describe anything?
> Because they describe *orientation*, not *operation*.

**Files Created:**
- `context/CLAIMS/C454_azc_b_adjacency_falsified.md`
- `context/CLAIMS/C455_azc_simple_cycle_falsified.md`
- `context/CLAIMS/C456_azc_interleaved_spiral.md`
- `context/ARCHITECTURE/layer_separation_synthesis.md`
- `phases/exploration/apparatus_topology_tests_v2.py`
- `phases/exploration/azc_topology_test.py`
- `results/apparatus_topology_critical_tests_v2.json`
- `results/azc_topology_analysis.json`

**Methodological Note:**
This phase demonstrated proper hypothesis testing:
1. Proposed falsifiable Tier-3 hypothesis
2. Pre-registered kill conditions (K1, K2)
3. Fixed test design flaws when detected
4. Accepted null results
5. Refined understanding based on evidence

**Status:** Apparatus-topology investigation CLOSED. Doors permanently closed on:
- AZC diagrams "representing" apparatus
- R/S/C positions mapping to physical components
- Diagram complexity correlating with execution difficulty

---

## Version 2.7 (2026-01-10)

### AZC-DEEP: Folio Family Architecture (C430-C432)

**Summary:** Completed AZC-DEEP Phases 1-3, discovering that AZC comprises two architecturally distinct folio families. This parallels the CAS-DEEP analysis of Currier A and reveals internal structure beyond "hybrid with placement."

**New Constraints:**

- **C430** - AZC Bifurcation (Tier 2)
  - AZC divides into two families with no transitional intermediates
  - Family 0: Zodiac-dominated, placement-stratified (13 folios)
  - Family 1: A/C-dominated, placement-flat (17 folios)
  - Bootstrap stability = 0.947, Silhouette = 0.34

- **C431** - Zodiac Family Coherence (Tier 2, refines C319)
  - All 12 Zodiac folios form single homogeneous cluster
  - JS similarity = 0.964
  - Higher TTR (0.54), placement entropy (2.25), AZC-unique rate (0.28)
  - Confirms Zodiac as distinct structural mode, not just template reuse

- **C432** - Ordered Subscript Exclusivity (Tier 2)
  - R1-R3, S1-S2 occur exclusively in Zodiac family
  - Binary diagnostic feature (0.96 vs 0.00 depth)
  - Ordered subscripts are family-defining, not AZC-general

**Architectural Impact:**
- AZC is now demonstrably non-monolithic
- Zodiac pages define a separate AZC control mode
- Ordered subscripts become diagnostic, not incidental
- Hybrid story sharpens: Cluster 1 has more shared vocabulary, Cluster 0 has more AZC-unique

**Files Modified:**
- `context/CLAIMS/azc_system.md` - Added C430-C435
- `context/CLAIMS/INDEX.md` - Updated AZC section

### AZC-DEEP Phase 4a: Zodiac Placement Grammar (C433-C435)

**Summary:** Discovered that Zodiac pages implement an extremely strict, block-based placement grammar - stricter than Currier B grammar, not looser.

**New Constraints:**

- **C433** - Zodiac Block Grammar (Tier 2)
  - Placement codes occur in extended contiguous blocks (mean 40-80 tokens)
  - Self-transition rate exceeds 98% for all major codes
  - Zero singletons - once a placement starts, it locks for dozens of tokens
  - **Stricter than Currier B grammar**

- **C434** - R-Series Strict Forward Ordering (Tier 2)
  - R1→R2→R3 only - no backward, no skipping
  - Backward transitions: 0 observed (349 expected)
  - Skip transitions: 0 observed (139 expected)

- **C435** - S/R Positional Division (Tier 2)
  - S-series: Boundary layer (95%+ at line edges)
  - R-series: Interior layer (89-95% interior positions)
  - Two-layer grammar: S marks entry/exit, R fills interior in ordered stages

**Key Insight:**
> The Zodiac pages are not "diagrams with labels." They are a rigid, page-bound control scaffold - the same structure reused twelve times with local vocabulary variation but identical placement logic.

### AZC-DEEP Phase 4b: A/C Family Placement Grammar (C436)

**Summary:** Discovered that the A/C family is ALSO rigid (98% self-transition, zero singletons), but differs from Zodiac in cross-folio consistency. The contrast is uniform-vs-varied, not rigid-vs-permissive.

**New Constraint:**

- **C436** - AZC Dual Rigidity Pattern (Tier 2)
  - Both families: >=98% self-transition, zero singletons
  - Zodiac family: 0.945 cross-folio consistency (uniform scaffold)
  - A/C family: 0.340 cross-folio consistency (folio-specific scaffolds)
  - The contrast is uniform-versus-varied rigidity

**Key Insight:**
> AZC is not "one mode with variation" - it implements two distinct coordination strategies. Every AZC page enforces a hard placement lock. The difference is whether that lock is standardized (Zodiac) or custom (A/C).

**Four-Layer Stack Now Complete:**
- Currier B: Controls systems (execution grammar)
- Currier A: Catalogs distinctions (complexity frontier)
- AZC: Locks context (uniform or custom scaffolds)
- HT: Keeps the human oriented once the lock is engaged

**AZC-DEEP Status:** COMPLETE (discovery phase). All four Voynich systems now show internal, non-trivial, testable architecture

---

## Version 2.6 (2026-01-10)

### C424: Clustered Adjacency + A-B Correlation Investigation + CFR Interpretation

**Summary:** Added C424 (Clustered Adjacency) with three refinements. Completed A-B hazard correlation investigation that falsified failure-memory hypothesis. Established Complexity-Frontier Registry (CFR) as unified interpretation for Currier A. Declared Currier A structurally exhausted.

**New Constraint:**
- **C424** - Clustered Adjacency in Currier A (Tier 2)
  - 31% of adjacent entries share vocabulary (clustered), 69% do not (singletons)
  - Mean cluster size: 3 entries (range 2-20)
  - Autocorrelation r=0.80 exceeds section-controlled null (z=5.85)

**Refinements:**
- **C424.a** - Structural correlates (68% vocabulary divergence between populations)
- **C424.b** - Run-size threshold (size 5+ shows J=0.36 vs size-2 J=0.08)
- **C424.c** - Section P inversion (singletons concentrate at top of pages)

**A-B Correlation Investigation (Exploratory - NO CONSTRAINT):**

| Test | Result | Interpretation |
|------|--------|----------------|
| Hazard density correlation | rho=0.228, p=0.038 | Initial positive |
| Permutation control | p=0.111 | FAILED |
| Frequency-matched control | p=0.056 | FAILED |
| **Pre-registered low-freq MIDDLE** | **rho=-0.052, p=0.651** | **FAIL** |

**Conclusion:** Apparent A-B hazard correlation entirely explained by token frequency. No residual risk-specific signal. Failure-memory hypothesis falsified.

**Unified Interpretation: Complexity-Frontier Registry (CFR)**

> Currier A externalizes regions of a shared control-space where operational similarity breaks down and fine discrimination is required.

- Currier B provides sequences (how to act)
- Currier A provides discrimination (where fine distinctions matter)
- AZC constrains availability
- HT supports the human operator

**The relationship between A and B is structural and statistical, not addressable or semantic.**

**Structural Exhaustion Declared:**
Currier A has reached its structural analysis limit. No further purely structural analyses expected to yield new constraints.

**Closed Tests (DO NOT RE-RUN):**
- Hazard density correlation - CLOSED (frequency-explained)
- Forgiveness/brittleness discrimination - CLOSED (inseparable from complexity)

**New files:**
- `CLAIMS/C424_clustered_adjacency.md` - Full constraint documentation
- `phases/exploration/a_b_hazard_correlation.py` - Main correlation script
- `phases/exploration/preregistered_low_freq_test.py` - Decisive final test
- `phases/exploration/a_b_connection_map.py` - Connection map generator
- `phases/exploration/A_B_CORRELATION_RESULTS.md` - Correlation results
- `phases/exploration/A_B_CONNECTION_MAP.md` - Connection map summary
- `phases/exploration/a_b_connection_map.json` - Machine-readable map

**Updated files:**
- `CLAIMS/INDEX.md` - Added C424, version 2.6, count 424
- `CLAIMS/currier_a.md` - Added C424 section, exploratory note with CFR interpretation

**Research phase:** Exploration (1838 entries, 83 folios analyzed)

---

## Version 2.5 (2026-01-09)

### Record Structure Analysis + C250.a Refinement

**Summary:** Complete analysis of Currier A record-level structure using DA-segmented block boundaries.

**Findings (validated but not all constraint-worthy):**
- Block count distribution: 57% single-block, 43% multi-block
- Block size pattern: FRONT-HEAVY (first block ~11 tokens, later ~5)
- Positional prefix tendencies: qo/sh prefer first, ct prefers last (V=0.136)
- Block-level repetition: 58.7% exact, 91.5% high similarity (J>=0.5)
- Record templates: 3-5 patterns cover 77%

**Expert review outcome:**
- C424-C426 initially proposed but REJECTED as constraints
- Positional preferences = tendencies, not rules (no constraint)
- Templates = emergent patterns, not grammar (no constraint)
- Block-aligned repetition = valid refinement of C250

**Accepted:**
- **C250.a** - Block-Aligned Repetition (refinement)
  - Repetition applies to DA-segmented blocks, not partial segments
  - Non-adjacent blocks more similar than adjacent (interleaved enumeration)

**Rejected (kept as descriptive findings only):**
- Positional prefix preferences (tendency, not constraint)
- Record structure templates (emergent, not grammar)

**New files:**
- `phases/exploration/record_structure_analysis.py`
- `phases/exploration/block_position_prefix_test.py`
- `phases/exploration/repetition_block_alignment.py`
- `phases/exploration/RECORD_STRUCTURE_SYNTHESIS.md`

**Updated files:**
- `CLAIMS/currier_a.md` - Added C250.a refinement under Multiplicity Encoding

**Note:** Constraint count unchanged (423). Findings describe USE of structure, not design limits.

---

## Version 2.4 (2026-01-09)

### C410.a: Sister Pair Micro-Conditioning (Refinement)

**Summary:** Refinement documenting compositional conditioning of sister-pair choice in Currier A.

**Findings:**
- MIDDLE is the PRIMARY conditioning factor (25.4% deviation from 50%)
- Some MIDDLEs are >95% one sister (yk: 97% ch, okch: 96% ch)
- Suffix compatibility provides secondary conditioning (22.1% deviation)
- Adjacent-token effects favor run continuation (ch->ch: 77%)
- DA context has ZERO effect (V=0.001) - confirms DA is structural
- Section effect is background bias (V=0.078)

**Interpretation:**
Sister pairs encode equivalent classificatory roles but permit compositionally conditioned surface variation. Preferences are local within the compositional system - no new categories, semantics, or hierarchies.

**New files:**
- `phases/exploration/sister_pair_conditioning.py`

**Updated files:**
- `CLAIMS/C408_sister_pairs.md` - Added C410.a refinement section

**Note:** This closes Priority 3 (sister-pair conditioning). Does not break equivalence class status.

---

## Version 2.3 (2026-01-09)

### C346.b: Component-Level Adjacency Drivers (Refinement)

**Summary:** Refinement note added to C346 documenting component-level analysis of adjacency coherence.

**Findings:**
- Removing DA tokens increases adjacency coherence (+18.4%)
- MIDDLE-only adjacency is LOWER than full-token (2.10x vs 2.98x)
- PREFIX and SUFFIX drive local adjacency more than MIDDLE
- DA-segmented blocks show 26.8x internal coherence

**Key insight:** Currier A adjacency reflects domain-level continuity (PREFIX) with item-level variation (MIDDLE). This is registry organization, not semantic chaining.

**New files:**
- `phases/exploration/payload_refinement.py`

**Updated files:**
- `CLAIMS/currier_a.md` - Added C346.b refinement note

**Note:** This is a refinement, not a new constraint. Does not change C346's core finding.

---

## Version 2.2 (2026-01-09)

### C423: PREFIX-BOUND VOCABULARY DOMAINS + C267 Amendment

**Summary:** New Tier-2 constraint establishing MIDDLE as the primary vocabulary layer in Currier A, with prefixes defining domain-specific vocabularies. Amendment to C267 corrects "42 common middles" to full census of 1,184.

**Finding (MIDDLE census):**
- 1,184 distinct MIDDLEs identified (full inventory)
- 80% (947) are PREFIX-EXCLUSIVE
- 20% (237) are shared across prefixes
- 27 UNIVERSAL middles appear in 6+ prefixes
- Top 30 account for 67.6% of usage
- MIDDLE entropy: 6.70 bits (65.6% efficiency)

**PREFIX vocabulary sizes:**
| Prefix | Exclusive MIDDLEs |
|--------|-------------------|
| ch | 259 (largest) |
| qo | 191 |
| da | 135 |
| ct | 87 |
| sh | 85 |
| ok | 68 |
| ot | 55 |
| ol | 34 (smallest) |

**DA-MIDDLE coherence finding:**
- DA-segmented sub-records do NOT exhibit increased MIDDLE similarity
- Adjacent segment J=0.037 vs random segment J=0.039 (0.94x)
- DA separates structure, not vocabulary content

**Interpretation:**
- Prefixes define domain-specific vocabularies
- MIDDLEs are selected from prefix-specific inventories
- Shared/universal middles form small cross-domain core
- This is the vocabulary layer of Currier A

**C267 amendment:**
- Original: "42 common middles" (discovery-era simplification)
- Updated: "1,184 unique (27 universal)" with cross-reference to C423
- Added note explaining scope mismatch

**New files:**
- `phases/exploration/middle_census.py`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C423, version 2.2, count 423
- `CLAIMS/currier_a.md` - Added Vocabulary Domains section, MIDDLE coherence note to C422
- `CLAIMS/C267_compositional_morphology.md` - Amended MIDDLE count and added note

**Research phase:** Exploration (25,890 tokens parsed, 17,589 with MIDDLE)

---

## Version 2.1 (2026-01-09)

### C422: DA as Internal Articulation Punctuation

**Summary:** New Tier-2 constraint documenting DA's structural punctuation role within Currier A entries.

**Finding:**
- 75.1% of internal DA occurrences separate adjacent runs of different marker prefixes (3:1 ratio)
- All DA tokens (daiin and non-daiin) exhibit identical separation behavior (74.9% vs 75.4%)
- Entries with DA are significantly longer (25.2 vs 16.4 tokens) and more prefix-diverse (3.57 vs 2.01)
- DA-segmented regions form prefix-coherent blocks

**Section gradient:**
- H (Herbal): 76.9% separation rate (3.3:1)
- P (Pharmaceutical): 71.7% (2.5:1)
- T (Text-only): 65.0% (1.9:1)
- Direction invariant across all sections

**Interpretation:**
- DA does not encode category identity
- DA marks internal sub-record boundaries within complex registry entries
- DA functions as punctuation rather than classifier
- Role is globally infrastructural, intensity correlates with section complexity

**New files:**
- `phases/exploration/da_punctuation_analysis.py`
- `phases/exploration/da_deep_dive.py`
- `phases/exploration/da_section_invariance.py`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C422, version 2.1, count 422
- `CLAIMS/currier_a.md` - Added DA Internal Articulation section

**Research phase:** Exploration (1838 entries, 3619 DA tokens analyzed)

---

## Version 2.0 (2026-01-09)

### C421: Section-Boundary Adjacency Suppression + C346.a Refinement

**Summary:** New Tier-2 constraint documenting section boundary effects on adjacent entry similarity. Refinement note added to C346 explaining similarity decomposition.

**C421 Finding:**
- Adjacent entries crossing section boundaries exhibit 2.42x lower vocabulary overlap
- Same-section adjacent: J=0.0160
- Cross-section adjacent: J=0.0066
- p < 0.001

**C346.a Refinement:**
- 1.31x adjacency similarity driven by MIDDLE (1.23x) and SUFFIX (1.18x)
- Weak contribution from marker prefixes (1.15x)
- Local ordering reflects subtype/property similarity, not marker class

**Interpretation:**
- Section boundaries (H/P/T) are primary hard discontinuities in Currier A
- Catalog organized by content/topic first, markers classify within clusters
- Does NOT change what Currier A represents; tightens characterization

**New files:**
- `phases/exploration/adjacent_entry_analysis.py`
- `phases/exploration/adjacent_section_boundary.py`
- `phases/exploration/ADJACENT_ENTRY_SYNTHESIS.md`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C421, version 2.0, count 421
- `CLAIMS/currier_a.md` - Added C346.a refinement, C421 section

**Research phase:** Exploration (1838 entries, 114 folios analyzed)

---

## Version 1.9 (2026-01-09)

### C420: Currier A Folio-Initial Positional Exception

**Summary:** New Tier-2 constraint documenting positional tolerance at folio boundaries in Currier A.

**Finding:**
- First-token position in Currier A permits otherwise illegal C+vowel prefix variants (ko-, po-, to-)
- 75% failure rate at position 1 vs 31% at positions 2-3
- C+vowel prefixes: 47.9% at position 1, 0% elsewhere
- Fisher exact p < 0.0001
- Morphologically compatible (ko- shares 100% suffix vocabulary with ok-)

**Interpretation:**
- Positional tolerance at codicological boundaries (common in medieval registries)
- Does NOT imply headers, markers, semantic categories, or enumeration
- No revision to C240 (marker families) or C234 (position-free) required

**New files:**
- `CLAIMS/C420_folio_initial_exception.md` - Full constraint documentation
- `phases/exploration/first_token_*.py` - Research scripts
- `phases/exploration/FIRST_TOKEN_SYNTHESIS.md` - Research synthesis

**Updated files:**
- `CLAIMS/INDEX.md` - Added C420, version 1.9, count 420
- `CLAIMS/currier_a.md` - Added Positional Exception section

**Research phase:** Exploration (48 folios analyzed)

---

## Version 1.8 (2026-01-09)

### HT/AZC FINAL CLOSED

**Summary:** Completed final constraint audit; verified C412; declared HT and AZC sections FINAL CLOSED.

**Audit results:**
- HT: 21 constraints + 1 superseded - ALL PASS
- AZC: 23 constraints - ALL PASS
- Notes: HT-AZC-NOTE-01, AZC-NOTE-01 correctly scoped

**C412 verification:**
- Original methodology replicated exactly
- Results reproduced: rho=-0.327 (original -0.326), p=0.0027 (original 0.002)
- Prior discrepancy explained: wrong metric used in re-analysis (ch-density vs ch-preference)
- Review flag removed

**Updated files:**
- `CLAIMS/C412_sister_escape_anticorrelation.md` - Added verification section
- `CLAIMS/INDEX.md` - Removed ⚠️ REVIEW marker

**New files:**
- `phases/exploration/c412_verification.py` - Verification script

**Final status:**
| Section | Status |
|---------|--------|
| Human Track (HT) | FINAL CLOSED |
| AZC System | FINAL CLOSED |
| Sister Pairs | FINAL CLOSED |

---

## Version 1.7 (2026-01-09)

### HT-AZC Third Anchoring Pressure

**Summary:** Identified AZC-specific HT pattern (diagram label concentration).

**Updated files:**
- `CLAIMS/human_track.md` - Added HT-AZC-NOTE-01, updated frozen statement

**Key finding:**
- AZC HT uniquely shows BOTH line-initial AND line-final enrichment
- Driven by L-placement (label) text: 88.8% initial, 95% final
- L-placement lines are short (1-3 tokens) with 15.1% HT density
- Establishes **third anchoring pressure**: diagram geometry (label positions)

**Three-system refinement:**
| System | Anchoring Pressure |
|--------|-------------------|
| Currier A | Registry layout (entry boundaries) |
| Currier B | Temporal/attentional context |
| AZC | Diagram geometry (label positions) |

---

## Version 1.6 (2026-01-09)

### Data Source Documentation + AZC/C412 Updates

**Summary:** Added data source documentation; documented AZC findings; flagged C412 discrepancy.

**Updated files:**
- `SYSTEM/METHODOLOGY.md` - Added "Canonical Data Source" section
- `CLAIMS/azc_system.md` - Added AZC-NOTE-01 (qo-depletion refinement)
- `CLAIMS/C412_sister_escape_anticorrelation.md` - Added review flag
- `CLAIMS/INDEX.md` - Added review marker to C412

**Key additions:**

1. **Data source documentation:**
   - PRIMARY DATA FILE: `data/transcriptions/interlinear_full_words.txt`
   - WARNING about EVA vs standard vocabulary encoding

2. **AZC-NOTE-01:** qo-prefix depletion (2.8x lower than B), refines C301/C313

3. **C412 review flag:** Re-analysis finds anticorrelation in Currier A (rho=-0.334, p=0.0003), NOT in B (rho=-0.089, p=0.42). Requires reconciliation with original SISTER phase.

**Issue caught:** During AZC exploration, wrong transcription file was initially used. All previous constraints verified safe.

---

## Version 1.5 (2026-01-09)

### HT Formal Hierarchy

**Summary:** Established canonical hierarchy for Human Track layer. Adds C414-C419.

**New files:**
- `CLAIMS/HT_HIERARCHY.md` - Formal hierarchy document (canonical)

**Updated files:**
- `CLAIMS/human_track.md` - Added C414-C419, system-specific refinement
- `CLAIMS/HT_CONTEXT_SUMMARY.md` - Updated with hierarchy reference
- `CLAIMS/INDEX.md` - Count 411→419, added 6 new constraints
- `CLAUDE_INDEX.md` - Count update, navigation to HT_HIERARCHY.md

**Constraints added:**
| # | Name | Tier | Key Finding |
|---|------|------|-------------|
| C414 | Strong Grammar Association | 2 | chi2=934, p<10^-145 |
| C415 | Non-Predictivity | 1 (FALSIFICATION) | MAE worsens with HT conditioning |
| C416 | Directional Asymmetry | 2 | V=0.324 vs 0.202 (1.6x) |
| C417 | Modular Additive | 2 | No synergy (p=1.0) |
| C418 | Positional Without Informativeness | 2 | Bias exists but non-predictive |
| C419 | HT Positional Specialization in A | 2 | Entry-aligned, seam-avoiding |

**Terminology guardrail established:**
- DO: "aligned with", "correlated with", "position-biased"
- DON'T: "marks", "encodes", "annotates", "means"

**Model refinement:**
- Currier A: HT aligned with registry layout (entry boundaries)
- Currier B: HT aligned with temporal/attentional context
- Same layer, different anchoring pressures

---

## Version 1.4 (2026-01-09)

### Phase: STRUCTURE_FREEZE_v1

**Summary:** Formal freeze of structural inspection layer. Transitions project from foundational reconstruction to deliberate post-structure paths.

**Components frozen:**
- **Basic Inspection v1** (`apps/script_explorer/BASIC_INSPECTION.md`)
  - Currier A registry parsing and roles
  - Currier B grammar roles (49-class, conservative binding)
  - AZC placement binding (`R/R1/R2/R3`, `S/S1/S2`, `C`, `MULTI`)
  - HT isolation and override behavior
  - Global properties (prefix family, kernel affinity, escape)

- **Execution Inspector v0.1** (`apps/script_explorer/EXECUTION_INSPECTOR.md`)
  - Grammar-only execution inspection
  - `grammar_bound` semantics
  - Conservative UNKNOWN handling
  - No hazards, order, or kernel contact beyond grammar anchors

**Repository rules enforced:**
- ❌ Do not alter parsing logic
- ❌ Do not alter classification logic
- ❌ Do not alter role assignment tables
- ❌ Do not alter system boundaries
- ❌ Do not reinterpret UNKNOWNs
- ❌ Do not extend execution semantics implicitly
- ❌ Do not weaken system gating (A/B/AZC/HT)

**Post-freeze paths available:**
1. Documentation & Consolidation (RECOMMENDED)
2. Visualization / UX (SAFE)
3. Deeper Execution Semantics (ADVANCED, requires new phase)

**Intent:** Preserve structural integrity. Expansion is a choice, not an accident.

---

## Version 1.0 (2026-01-08)

### Initial Release

**Created:** Context expansion system to replace monolithic CLAUDE.md

**Structure:**
- `context/` directory with 9 subdirectories
- `CLAUDE_INDEX.md` as primary entry point (~4k tokens)
- Progressive disclosure architecture
- 57 markdown files total

**Directories:**
- `SYSTEM/` - Meta-rules, tiers, methodology (5 files)
- `CORE/` - Tier 0-1 facts (3 files)
- `ARCHITECTURE/` - Structural analysis by text type (5 files)
- `OPERATIONS/` - OPS doctrine, program taxonomy (3 files)
- `CLAIMS/` - 411 constraints indexed (24 files: 1 index, 16 individual claims, 7 grouped registries)
- `TERMINOLOGY/` - Key definitions (3 files)
- `METRICS/` - Quantitative facts (4 files)
- `SPECULATIVE/` - Tier 3-4 content (4 files)
- `MAPS/` - Cross-references (3 files)

**Design Principles:**
1. Entry point stays slim (<10k tokens)
2. One concept per file
3. ≤15k tokens per file
4. Every claim declares Tier + closure
5. No analysis in context files
6. Archive is append-only
7. Context points to archive

**Migration:**
- Content extracted from CLAUDE.md v1.8 (95KB, ~30k tokens)
- Original preserved as `archive/CLAUDE_v1.8_2026-01-08.md`
- CLAUDE.md converted to redirect

---

## Version 1.3 (2026-01-08)

### Added: Constraint-First Reasoning Protocol

**Summary:** Added methodology for checking constraints before speculating, and guidance on when/how to question constraints.

**Files updated:**
- `context/SYSTEM/METHODOLOGY.md` - Added two new sections:
  - "Constraint-First Reasoning" - rule to search constraints before interpreting
  - "Questioning Constraints" - when and how to challenge existing claims
- `context/CLAUDE_INDEX.md` - Added stop condition reminder and note that questioning is allowed

**Motivation:** During conversation, speculated that "Currier A entries might reference the same categories B executes" — but C384 explicitly falsifies this. Checking constraints first would have prevented the error.

**Key principles added:**
- Search CLAIMS/ before reasoning about relationships
- Distinguish "constrained" from "undocumented" (gap ≠ permission)
- Cite constraint numbers or flag as research gap
- Questioning is allowed but must be explicit, not silent override
- Tier determines revisability (0=frozen, 2=reopenable with evidence)

---

## Version 1.2 (2026-01-08)

### Added: Structural Intuition Clarification

**Summary:** Added documentation to prevent the misinterpretation that "neutral/unhighlighted tokens are unknown."

**Files updated:**
- `context/CLAUDE_INDEX.md` - Added three new sections:
  - "How to Think About Tokens (Structural Layer)"
  - "Why Visualization Tools Highlight Only Some Tokens"
  - "Structural Analysis vs Interpretive / Probabilistic Reasoning"

**Clarifications made:**
- Tokens are surface realizations, not functional operators
- Functional behavior determined at instruction-class level
- High hapax rates explained by compositional morphology
- "Neutral" means "non-contrastive", not "unknown"
- Visualization highlighting is a UI choice, not knowledge boundary
- Bayesian/probabilistic reasoning explicitly supported in interpretive layer

**No constraint changes:** This is a documentation-only update for human intuition alignment. No tiers, claims, or conclusions were altered.

---

## Version 1.1 (2026-01-08)

### Added: Research Automation

**Summary:** Added skills, hooks, and workflow documentation for automated research.

**Files created:**
- `.claude/skills/phase-analysis/SKILL.md` - Automatic phase analysis
- `.claude/skills/constraint-lookup/SKILL.md` - Constraint search and citation
- `.claude/settings.json` - Hook configuration
- `archive/scripts/validate_constraint_reference.py` - Constraint validation
- `archive/scripts/extract_phase_metrics.py` - Metrics extraction

**Files updated:**
- `context/SYSTEM/METHODOLOGY.md` - Added "Research Workflow (Automated)" section
- `context/SYSTEM/HOW_TO_READ.md` - Added multi-branch access patterns
- `context/CLAUDE_INDEX.md` - Added "Automation" section

**New workflows:**
- Phase Analysis Protocol (automatic)
- Constraint Lookup Protocol (automatic)
- Constraint reference validation (hook)

---

## Future Entries

When updating context, add entries in this format:

```markdown
## Version X.Y (YYYY-MM-DD)

### [Type: Added/Changed/Removed/Fixed]

**Summary:** Brief description

**Files affected:**
- `path/to/file.md` - what changed

**Constraint changes:**
- C### added/updated/removed

**Source:** Phase PHASE_NAME (if applicable)
```

---

## Navigation

← [HOW_TO_READ.md](HOW_TO_READ.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
