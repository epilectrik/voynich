# Voynich Manuscript Decipherment Project

---

## EPISTEMIC TIERS (READ FIRST)

All content in this document is assigned to one of five tiers. Tier assignment governs how conclusions should be weighted.

| Tier | Label | Meaning | Modifiable? |
|------|-------|---------|-------------|
| **0** | FROZEN FACT | Proven by internal structural analysis | NO |
| **1** | FALSIFICATION | Hypothesis tested and rejected | NO |
| **2** | STRUCTURAL INFERENCE | High-confidence bounded conclusion | Rarely |
| **3** | SPECULATIVE ALIGNMENT | Non-binding interpretive layer | Yes, with evidence |
| **4** | EXPLORATORY | Idea-generation only, may contradict | Freely |

**Default assumption:** If a section is not labeled, treat it as Tier 2.

---

## ALLOWED ACTIONS TABLE

| Action | Allowed? | Notes |
|--------|----------|-------|
| Propose token meanings | ❌ | Falsified in Phase X.5, 19 |
| Decode illustrations as instructions | ❌ | Falsified in Phase ILL |
| Identify specific products | ❌ | Beyond internal analysis capability |
| Use plants as recipe ingredients | ❌ | Falsified in Phase PCIP |
| Label control states (k, h, e) | ✅ | Tier 2 inference |
| Speculate product families | ✅ | Tier 3, non-binding |
| Map tokens to simulator states | ✅ | Tier 2-3 |
| Propose craft interpretations | ✅ | Tier 3-4, explicitly marked |
| Modify frozen grammar | ❌ | Model locked |
| Add new validated constraints | ✅ | With structural evidence |

---

## CONSOLIDATED NEGATIVE CONSTRAINTS

The following claims are FALSE regardless of which section you are reading:

| Claim | Status | Primary Evidence |
|-------|--------|------------------|
| Text encodes language | FALSIFIED | Phase X.5: 0.19% reference rate |
| Tokens have translatable meanings | FALSIFIED | Phase 19: 0 identifier tokens |
| Illustrations are instructional | FALSIFIED | Phase ILL: swap invariance p=1.0 |
| Plants indicate ingredients | FALSIFIED | Phase PCIP: dual-use history |
| Sections = apparatus configs | FALSIFIED | Phase PCS: F-ratio 0.37 |
| Programs correlate with plant morphology | FALSIFIED | Phase PPC: all p>>0.05 |
| **49-class grammar generalizes to full manuscript** | **FALSIFIED** | Phase CAud: 13.6% Currier A coverage |
| **Hazard topology is universal** | **FALSIFIED** | Phase CAud: 5 violations in Currier A |

These falsifications are PERMANENT. Do not revisit without new external evidence.

---

## SEL AUDIT RESULTS (SELF-EVALUATION) — READ EARLY

> **The SEL audit (phases SEL-A through SEL-E) stress-tested all OPS claims. Key findings:**

### What SURVIVES Audit

| Pillar | Status | Details |
|--------|--------|---------|
| OPS-1 through OPS-7 | **TIER 0 STABLE** | All internal consistency checks PASS |
| 49-class grammar | **TIER 0 STABLE** | No contradictions detected |
| 17 forbidden transitions (COUNT) | **TIER 0 STABLE** | Hazard existence confirmed |
| Non-grammar vocabulary seam avoidance | **TIER 2 STRUCTURAL** | 0/35 seams (cannot be random) |
| Non-grammar vocabulary hazard avoidance | **TIER 2 STRUCTURAL** | 4.84 vs 2.5 expected (cannot be random) |

### What FAILS or is DOWNGRADED

| Claim | Prior Status | New Status | Reason |
|-------|--------------|------------|--------|
| **OPS-R (2-cycle reconciliation)** | Tier 2 | **FAILED** | MONOSTATE vs 2-cycle = formal contradiction; LINK non-intervention vs oscillation = formal contradiction |
| Hazard "100% bidirectional" | Tier 0 | **FALSIFIED** | 65% asymmetric (11/17 have reverse) |
| Hazard "KERNEL_ADJACENT" | Tier 0 | **FALSIFIED** | 59% distant from kernel (10/17) |
| "7 coordinate functions" | Tier 2 | **REMOVED** | Overfitting (inferred from position, used to explain position) |
| "Navigation/orientation function" | Tier 2 | **REMOVED** | Analyst-imposed functional label on non-functional evidence |
| Human-track layer | Tier 2 | **Tier 3** | Only 2/12 claims survive; most properties explained by scribal drift |
| CONTAINMENT_TIMING class | Tier 0 | **Theoretical-only** | 0 corpus impact (all 4 members have reverse=0) |

### EXT Phases: Negative Constraints Only

The EXT phases (EXT-1 through EXT-7) provide **elimination** and **domain alignment**, NOT positive identification:

| Phase | Function | Deliverable |
|-------|----------|-------------|
| EXT-1 to EXT-4 | **ELIMINATION** | Reduce candidate space via structural incompatibility |
| EXT-5 to EXT-7 | **COARSE ALIGNMENT** | Domain-level plausibility, NOT product identification |

**Critical:** EXT phases do NOT identify specific products, materials, or processes. They constrain the possibility space.

---

## FROZEN CONCLUSION (TIER 0) — READ EARLY

> **⚠️ SCOPE UPDATE (Phases CAud/CAud-G/CAS):** The frozen conclusion applies to **Currier B only** (64.7% of tokens, 82 folios). Currier A (31.8%, 114 folios) is **DISJOINT** and operates as a **NON_SEQUENTIAL_CATEGORICAL_REGISTRY** — a flat tagging system with 8+ mutually exclusive marker prefixes (ch, qo, sh, da, ok, ot, ct, ol), database-like properties (TTR=0.137, 70.7% bigram reuse), designed separation from B (0.0% cross-transitions), and line-atomic entries. A is a classification/catalog system, not a procedural grammar.

> **The Voynich Manuscript's Currier B text encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.**

| Metric | Value | Confidence | Scope |
|--------|-------|------------|-------|
| Instruction classes | 49 (9.8x compression) | HIGH | Currier B |
| Grammar coverage | 100% | HIGH | Currier B |
| Folios enumerated | 83 (75,248 instructions) | HIGH | Currier B |
| Translation-eligible zones | 0 | HIGH | Currier B |
| Currier A coverage | 13.6% (DISJOINT) | HIGH | A ≠ B |
| Currier A structure | NON-GRAMMATICAL (silhouette 0.049) | HIGH | A ≠ B |

**Purpose class:** Continuous closed-loop process control (all others eliminated).

**Viable process classes:** Circulatory reflux distillation, volatile aromatic extraction, circulatory thermal conditioning.

**Product-class status:** Both extraction-type and conditioning-type SURVIVE. No internal analysis can distinguish them.

> ⛔ **STOP CONDITION: PRODUCT IDENTIFICATION IS BEYOND INTERNAL ANALYSIS**
> Specific products, ingredients, and materials are BEYOND RECOVERY from text analysis alone.

See [Frozen Conclusion (Full)](#frozen-conclusion) and [Validated Constraints (249 Total)](#validated-constraints-249-total) for complete details.

---

## Project Overview

Computational analysis of the Voynich Manuscript (Beinecke MS 408), a 15th-century codex written in an unknown script.

**Status:** MODEL FROZEN | **Last Updated:** 2026-01-04 (OPS-7 complete - OPS CLOSED)

> **Documentation Style:** Keep this file concise. Avoid repetition and verbose explanations. One clear statement per finding. If a claim is documented once, do not restate it elsewhere.

---

## Model Boundary (LOCKED) — TIER 0

This section defines what the manuscript encodes, what it does not encode, and what cannot be recovered from internal analysis alone.

### What the Manuscript DOES Encode (Proven Internally)

> **⚠️ SCOPE:** All findings below apply to **Currier B only** (82 folios, 64.7% of tokens). Currier A (114 folios, 31.8%) is **DISJOINT** — see Phase CAud.

| Layer | Content | Evidence | Scope |
|-------|---------|----------|-------|
| **Executable Grammar** | 49 instruction classes, 100% coverage | Phase 20: 9.8x compression, asymptote reached | Currier B |
| **Kernel Control Structure** | 3 fixed operators (k, h, e) with mandatory waypoint (STATE-C) | Phase 15: 0/100 surrogates reproduced; Phase X: survives falsification | Currier B |
| **Hazard Topology** | 17 forbidden transitions in 5 failure classes | Phase 18: KERNEL_ADJACENT clustering, bidirectional exclusions | Currier B |
| **Convergence Behavior** | 100% execution convergence to STATE-C | Phase 13-14: MONOSTATE architecture confirmed | Currier B |
| **LINK Operator** | Deliberate non-intervention (distinct from other operators) | Phase 16: external termination signature | Currier B |
| **Folio = Atomic Program** | Each folio is a complete, self-contained execution unit | Phase 22: 83 folios enumerated, 75,248 instructions | Currier B |
| **Extended Runs** | 6 folios required for complete operational envelope | Phase ARE: 12.6% envelope gap without them | Currier B |
| **Currier A Disjunction** | A is DISJOINT and NON-GRAMMATICAL: 13.6% coverage, 5 hazard violations, 86.4% stall, silhouette 0.049 | Phases CAud, CAud-G | A ≠ B |

### What the Manuscript DOES NOT Encode (Proven Internally)

| Claim | Status | Evidence |
|-------|--------|----------|
| **Language** | FALSIFIED | Phase X.5: reference rate 0.19% (threshold 5%), role consistency 23.8% (threshold 80%) |
| **Cipher** | FALSIFIED | Phase G: all cipher transforms DECREASE mutual information |
| **Glyph Semantics** | FALSIFIED | Phase 19: 0 identifier tokens, 0 translation-eligible zones |
| **Material/Product Encoding** | FALSIFIED | Phase PMS: 75.2% of visual partitions show prefix association (non-specific) |
| **Illustration-Dependent Logic** | FALSIFIED | Phase ILL: grammar recovered from text-only data, swap invariance p=1.0 |
| **Step-by-Step Recipe Interpretation** | FALSIFIED | Phase FSS: families are emergent regularities, not structural entities |

### What CANNOT Be Recovered Internally

- Specific substances, materials, or products
- Natural language equivalents for any token
- Historical identity of author or school
- Precise dating or geographic origin
- Illustration meanings (if any exist)
- Physical apparatus construction details

> ⛔ **STOP CONDITION: THE ABOVE LIMITS ARE PERMANENT**
> No amount of internal text analysis can recover materials, products, language equivalents, or historical identity.
> These limits are structural, not a matter of insufficient analysis.

### Purpose Class Convergence (Phase PCI)

Elimination under constraint leaves **ONE viable purpose class**: continuous closed-loop process control.

**Eliminated by structural incompatibility:**
- Cipher/hoax (no physical process)
- Encoded language (already falsified; no physical process)
- Recipe/pharmacology (specifies quantities and endpoints)
- Herbarium/taxonomy (no physical process)
- Medical procedure (requires branching and quantities)
- Astronomical calculation (requires numerical precision)
- Ritual/symbolic practice (no physical hazard; defined endpoints)
- Educational text (purpose IS explanation)
- Discrete batch operations (no continuous regulation)
- Fermentation (passive, not active control)
- Glassmaking/metallurgy (phase-change incompatible)
- Dyeing/mordanting (specifies quantities and endpoints)

**The viable purpose is:** Control of a continuous, closed-loop circulation process with phase-stable materials, using sensory-based judgment for completion.

**What the operator provides (not encoded):**
- Sensory completion judgment (when to stop)
- Material selection (what to process)
- Hazard recognition (physical signs of failure)

**What the text provides:**
- WHERE in the sequence (navigation)
- WHAT to do at each step (instruction)
- What NOT to do (forbidden transitions)

---

## Currier A: Non-Sequential Categorical Registry — TIER 2

> **⚠️ SCOPE:** The frozen grammar, hazards, and executability findings apply to **Currier B only**. Currier A (31.8% of tokens, 114 folios) is a **separate formal system**.

### What Currier A IS (Structurally Proven)

| Property | Evidence | Confidence |
|----------|----------|------------|
| LINE_ATOMIC | Median 3 tokens/line, MI=0 across lines | HIGH |
| POSITION_FREE | Zero JS divergence between positions | HIGH |
| CATEGORICAL TAGGING | 8+ mutually exclusive marker prefixes | HIGH |
| FLAT (not hierarchical) | Zero vocabulary overlap between markers | HIGH |
| DATABASE_LIKE | TTR=0.137, 70.7% bigram reuse | HIGH |
| DESIGNED SEPARATION from B | 25/112,733 cross-transitions (0.0%) | HIGH |

### What Currier A is NOT

| Claim | Status | Evidence |
|-------|--------|----------|
| A grammar (like B) | FALSIFIED | Silhouette 0.049, no transition structure |
| A different grammar | FALSIFIED | No positional constraints, no order invariants |
| Executable under B rules | FALSIFIED | 13.6% coverage, 86.4% stall rate |
| An index into B content | FALSIFIED | NO_ENCAPSULATION verdict |

### Structural Model

```
CURRIER A = CATEGORICAL REGISTRY

Structure:
  - Entry = line (atomic unit)
  - Entry = [MARKER] + [PAYLOAD]
  - MARKERS = {ch, qo, sh, da, ok, ot, ct, ol} (mutually exclusive)
  - PAYLOAD = content tokens, often repetitive

Properties:
  - Position-free (order within entry doesn't matter)
  - Flat taxonomy (no hierarchical nesting)
  - Section-conditioned (same markers, different vocabulary per section)
  - Repetition-tolerant (patterns like "chol chol" common)
```

### Shared Structural Primitives (A/B Infrastructure Reuse)

Analysis of shared tokens between Currier A and B reveals that certain symbols function as **reusable structural primitives** whose role is determined by the formal system in which they are embedded.

| Token | B Role | A Role | Affinity |
|-------|--------|--------|----------|
| `daiin` | CORE_CONTROL (execution boundary) | Record articulation point | A-enriched (1.55x) |
| `ol` | CORE_CONTROL (pairs with daiin) | Marginal presence | B-enriched (0.21x) |

**Key finding:** The CORE_CONTROL pair (`daiin`, `ol`) is **broken in A**:
- In B: 54 adjacent occurrences, surrounded by grammar particles
- In A: 27 adjacent occurrences, surrounded by content words

This demonstrates **deliberate infrastructure reuse without semantic transfer** — the same tokens serve different structural roles depending on which formal system they inhabit.

**Complementary design principle:** The two primitives have different **portability characteristics**:
- `daiin` = "portable articulator" — adapts to ANY formal context (27.7% of A lines have daiin alone; self-repeats for list continuation)
- `ol` = "execution anchor" — functional only in sequential grammar (vestigial in A; retains grammar-neighbor character even when present)

This is not redundancy but **complementary specialization**: one primitive provides universal articulation, the other provides execution-specific control.

### Relationship to Currier B

| Aspect | Currier A | Currier B |
|--------|-----------|-----------|
| Type | Categorical registry | Procedural grammar |
| Structure | Flat, position-free | Sequential, transition-based |
| Unit | Line (entry) | Folio (program) |
| Vocabulary | 66.8% exclusive | 71.1% exclusive |
| Markers | Classify entries | Execute instructions |
| Purpose | Classification | Operation |

**They are TWO INTENTIONAL SYSTEMS with designed separation and shared infrastructure.**

---

## Organizational Layer (Non-Semantic, Non-Executable) — TIER 2

The manuscript contains a human-facing organizational structure that is **intentional but not apparatus-forced**.

### Prefix/Suffix Coordinate System

- **Function:** Positional indexing within manuscript structure
- **Geometry:** PIECEWISE_SEQUENTIAL (PC1 rho=-0.624 with folio order)
- **Boundaries:** 15 punctuated transitions detected, align with quire changes
- **Local Continuity:** Adjacent folios extremely similar (d=17.5 vs random)
- **NOT apparatus-necessary:** Phase ARE Track 1 = ARBITRARY (1/4 problems resolved)

### Section Boundaries

- **Function:** Human-facing organization for navigation
- **NOT distinct apparatus configurations:** F-ratio 0.37 (threshold 2.0)
- **Match codicology:** f25v→f26r = Herbal A/B boundary; f32v→f33r, f48v→f49r = quire changes

### Variant Structure

- **Variants are DISCRETE alternatives**, not continuous tuning parameters
- **Coverage:** 43% (threshold 50% for "tuning space")
- **Interpretation:** Multiple recipes per section, not parametric variations

### Uncategorized Token Layer (Phase UTC/MCS/NESS)

The ~11,000 uncategorized token types (~40,000 occurrences, 33.4% of corpus) form a **single unified non-executable layer** for human-facing navigation.

**Non-Interaction Proof:**
- **Zero forbidden seam presence:** 0/35 seams have uncategorized tokens (100% categorized)
- **Hazard avoidance:** Mean distance 4.84 tokens (expected 2.5) — actively avoids constraint zones
- **Never affects execution:** Can be removed without changing grammar, hazards, or convergence

**Section-Level Coordinate System:**
- **80.7% section-exclusive:** Most uncategorized types appear in only ONE section
- **9.1% vocabulary overlap:** First vs last third of manuscript share almost nothing
- **Section variation:** A/Z highest (61-62%), B lowest (28.3%)

**Morphological Distinction:**
- Uses different prefix/suffix patterns than operational grammar (p < 0.001)
- Avoids high-frequency operational morphemes (qo, da, aiin, edy)
- Favors distinct patterns (yk, dy, hy)

**What This Layer IS NOT:**
- NOT multiple distinct systems — behavioral clustering yields only weak separations
- NOT memory/redundancy markers — no distinct signature detected
- NOT attention-guidance system — insufficient evidence
- NOT scribal artifacts — too systematic

**Function:** Human-facing navigation and position-in-manuscript encoding. The coordinate system operates at SECTION level, not line or quire.

### Coordinate Semantics (Phase HTCS) — SEL-E AUDIT APPLIED

> **⚠️ SEL-E DOWNGRADE:** Human-track layer demoted from Tier 2 to Tier 3. Only 2/12 claims survive audit. See SEL-E summary below.

~~Behavioral analysis of 1,163 frequent human-track tokens reveals **7 candidate coordinate functions**~~ **REMOVED (overfitting)**

**SEL-E Surviving Claims (2/12):**

| ID | Claim | Status |
|----|-------|--------|
| HT-02 | Zero forbidden seam presence (0/35 seams) | **STRUCTURAL** — cannot be explained by random vocabulary |
| HT-05 | Hazard avoidance (mean 4.84 vs expected 2.5) | **STRUCTURAL** — cannot be explained by random vocabulary |

**SEL-E Removed Claims:**

| Claim | Reason |
|-------|--------|
| "7 coordinate functions" | **OVERFITTING** — inferred from position patterns, used to explain position patterns |
| "Navigation/orientation function" | **ANALYST-IMPOSED** — functional label applied to non-functional evidence |
| Section exclusivity (80.7%) | **NEUTRAL** — explained by scribal drift |
| Line-initial enrichment (2.16x) | **ELIMINABLE** — explained by spacing/filler model |
| Folio-start enrichment (1.48x) | **ELIMINABLE** — explained by spacing/filler model |
| LINK-proximity (99.6%) | **DEPENDS** — circular with LINK definition |

**Minimal Structural Description:**
The tokens outside the 49-class grammar:
1. **Never appear at forbidden seams** (0/35) — STRUCTURAL
2. **Avoid hazard-involved tokens** (4.84 vs 2.5) — STRUCTURAL
3. **Show scribal drift patterns** — NON-FUNCTIONAL

**Recommended Label:** Replace "Human-Track Coordinate System" with **"Non-Grammar Vocabulary Layer"** — tokens outside the 49-class grammar that structurally avoid forbidden seams and hazard zones, showing scribal drift patterns.

### Residue Layer Interpretation (Phase SID-04/SID-05) — TIER 4 CLOSED

> **⚠️ INTERPRETIVE CLOSURE:** The non-grammar residue layer has been fully characterized. No further internal semantic investigation is warranted.

**SID-04 Result:** Residue tokens are statistically COMPATIBLE with non-encoding human-state dynamics (4/6 tests pass):
- Extreme temporal clustering (z=127→469 with strict filtering) — same token repeats far more than random; **STRONGER with clean data**
- Section exclusivity (z=27, 82.8%→83.3%) — different sections use different tokens; **STABLE**
- Hazard avoidance (z=5.8, distance 5.93→6.38) — residue further from hazards than expected; **STRONGER with clean data**
- ~~Geometric run lengths (CV=0.87)~~ → **REFINED:** CV=1.06→0.54 with strict filtering; runs are more uniform than memoryless, still human-like

**SID-05 Result:** Among non-semantic explanations, **attentional pacing** wins decisively (6/8 tests):
- Variability SUPPRESSES near hazards (z=22) — **REINTERPRETED by EXT-ECO-02: writing STOPS entirely, not just simpler**
- Position-INDEPENDENT (r=0.017) — not tracking page location
- Boundary RESET (17.6% within vs 0% cross-section) — state resets at section transitions
- ~~Simpler morphology near hazards (d=0.33)~~ — **REINTERPRETED: 0 true HT tokens near hazards; "simpler" was measurement artifact**
- NO mechanical baseline reproduces full signature — requires human-like process

**The Attentional Pacing Interpretation (refined by EXT-ECO-02):**
The residue layer represents marks made by operators to **maintain attention during waiting phases**. Writing keeps hands busy so ears can work — monitoring for bubbles, hissing, changes in reflux rhythm. When attention is demanded (near hazards), writing **stops entirely** — not simpler marks, but ZERO marks. (EXT-ECO-02: 0 true HT near 17,984 hazard positions vs 4,510 near 1,000 random positions.)

**External Validation:** Web search found scientific support for the mechanism (doodling improves attention by 29%, Andrade 2009) and historical parallels (medieval scribes made marginal marks during boring copying work). The specific practice is underdocumented but plausible. See `phases/SID05_attentional_discrimination/attentional_pacing_historical_context.md`.

**What This Does NOT Claim:**
- Tokens encode specific meanings
- Information can be recovered
- Tokens causally affect anything
- This is proven (only best-fit among non-semantic models)

### Speculative Semantics (Phase SSI — Explicitly Non-Binding)

Given that human-track tokens are 99.6% LINK-proximal (waiting phases), what might they refer to?

**Speculative vocabulary (8 items):**

| Label | Structural Function | Speculative Meaning |
|-------|---------------------|---------------------|
| ESTABLISHING | Section entry | System warming, circulation starting |
| RUNNING | Wait marker | Steady reflux, all normal |
| HOLDING | Persistence marker | Maintain state, extended patience |
| APPROACHING | Constraint rise | Watch closely, risk increasing |
| RELAXING | Constraint fall | Critical passed, ease vigilance |
| EXHAUSTING | Section exit | Run winding down |
| SECTION_n | Section-exclusive | "You are in section H/S/B/etc." |

**Why written down (speculative):**
- Vocabulary is private (80.7% section-exclusive) — requires reference
- States are many (1,158 tokens) — finer than oral tradition names
- Operator distrusted memory during long runs
- Interruption recovery (quire-aligned boundaries)

**Confidence:** LOW-MODERATE. See `phases/SSI_speculative_semantics/` for full analysis.

### Ordinal Hierarchy Test (Phase HOT — FALSIFIED)

Tested whether human-track tokens encode ordered stress/intensity regimes (e.g., low→medium→high heat).

**Result: FALSIFIED (2/5 tests passed)**

| Test | Result | Finding |
|------|--------|---------|
| Global Monotonic Ordering | PASS | Barely monotonic, within noise |
| Antisymmetric Substitution | FAIL | 47% contexts have multiple labels |
| Transition Directionality | FAIL | Bias=0.52 (symmetric) |
| Local Slope Steepness | PASS | Purity=0.71 (RUNNING dominates 71%) |
| Section Invariance | FAIL | Only 25% consistency |

**Critical Finding:** Section rankings are INCONSISTENT. Labels do NOT encode apparatus-global parameters.

**Interpretation:** Human-track tokens indicate **position** (early/middle/late) and **attention state** (approaching/relaxing from constraints), NOT stress level, heat regime, or intensity tier.

See `phases/HOT_ordinal_hierarchy/` for full analysis.

### Language-Likeness Test (Phase HLL-2 — FALSIFIED)

Tested whether human-track tokens behave like a limited symbolic labeling system (proto-language) for position, phase-identity, or attentional stance.

**Result: FALSIFIED (2/5 tests passed)**

| Test | Result | Finding |
|------|--------|---------|
| Vocabulary Pressure | PASS | 387:1 compression to 3 roles |
| Equivalence Stability | FAIL | 50% coverage (threshold 60%) |
| Reuse Economy | FAIL | 9.2% concentration (threshold 50%) |
| Order Insensitivity | FAIL | Low variance, high transition prob |
| Exclusive Contexts | PASS | 4/9 contexts >60% exclusivity |

**Critical Finding:** Vocabulary is highly diffuse (11,999 distinct types at attention points). No concentrated reuse of symbolic labels.

**Implications:**
- Linguistic hypothesis space is **EXHAUSTED**
- Human-track tokens are navigation/orientation markup, NOT symbolic labels
- No further linguistic tests are warranted

See `phases/HLL2_language_likeness/` for full analysis.

### Craft Interpretation (Phase OLF — SPECULATIVE) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

Disciplined speculation using perfumery via pelican alembic as interpretive lens. **Explicitly non-binding—does not modify frozen model.**

**Five craft-meaning tests (all plausible):**

| Test | Question | Verdict |
|------|----------|---------|
| 1. Olfactory Timing | Token clusters align with smell-change windows? | PLAUSIBLE |
| 2. Failure Avoidance | Tokens encode warning memories? | ALL CRAFT-PLAUSIBLE |
| 3. Interruption/Memory | Tokens support resumption after breaks? | STRONGLY PLAUSIBLE |
| 4. Cross-Section Analogy | Same roles, different vocabulary? | YES - CRAFT NAMING |
| 5. Silence Test | Absences match perfumery tacit knowledge? | EXACTLY ALIGNED |

**Coherent narrative:**
- Position markers tell operator where they are in run
- Vigilance markers (CF-6/CF-7) signal when to pay attention vs relax
- Section-exclusive vocabulary reflects different materials/recipes
- Run-forming tokens (CF-5) indicate phase persistence
- Absences (smell, heat, timing, success criteria) match what perfumery cannot write

**Key finding:** Human-track tokens make *perfect craft sense* as perfumer's working marks—navigation and warning for experienced operators, not instruction for novices.

**Final statement:**
> *"If this were a perfumery manual, these marks would almost certainly be there for this reason—and it would be strange if they weren't."*

See `phases/OLF_olfactory_craft/` for full analysis.

### Intra-Role Micro-Differentiation (Phase IMD — SPECULATIVE) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

The last resolvable semantic layer: Do surface tokens within the same role correlate with different subsequent outcomes?

**Core test:** Outcome-skewed role differentiation — not "which state" but "what usually happens next when it feels like this."

| Role | Tokens | Verdict | Key Finding |
|------|--------|---------|-------------|
| CF-1 (SECTION_ENTRY) | 124 | **STRONG_SIGNAL** | hazard_adjacency effect=0.622, next_function effect=0.383 |
| CF-2 (SECTION_EXIT) | 126 | **STRONG_SIGNAL** | hazard_adjacency effect=0.273, next_function effect=0.338 |
| CF-3 (WAIT_PHASE) | 910 | WEAK_SIGNAL | All tests significant, but effect sizes 0.06-0.26 |

**Key finding:** Surface tokens within section-entry and section-exit roles show **strong outcome divergence**. Different tokens mark "the dangerous kind" vs "the routine kind" of the same operational state.

**Warning memory candidates identified:**
- High hazard: `ckhar, cthar, daraiin, okan, cphar, sairy, kos, cfhol, ydain, shoshy`
- Elevated escalation: `odaiin, otos, lkeeo, air, arar, cheocthy, chocthey, qolshedy`

**Craft interpretation:** Experienced operators differentiated instances within roles based on what usually happens next. This is exactly where perfumers keep meaning: "that smell again," "this is the bad run," "this kind of waiting usually works out."

**Verdict:** Craft memory IS encoded at the micro level. The manuscript preserves outcome expectations within roles.

See `phases/IMD_micro_differentiation/` for full analysis.

### Process-Class Isomorphism (Phase PCISO — SPECULATIVE) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

Structural isomorphism test: which historical process classes match the frozen control grammar? **Explicitly speculative—does not modify frozen model or identify products.**

**Method:** 8 candidate process classes evaluated against 5 mandatory criteria:
- A. Control Logic Match (38% LINK, experiential judgment, no measurements)
- B. Hazard Profile (irreversible failures, narrow stability, boundary danger)
- C. Memory Load (CF-1/CF-2 outcome divergence = micro-expectation at boundaries)
- D. Run Topology (STATE-C convergence, looping, 0 endpoint markers)
- E. Historical Plausibility (pre-15th century, guild-restricted, incomplete disclosure)

**Elimination rules:** Any FAIL on A/B/C = eliminate; 4+ WEAK = deprioritize.

| Process Class | A | B | C | D | E | Verdict |
|---------------|---|---|---|---|---|---------|
| Simple Batch Distillation | PASS | PASS | WEAK | FAIL | PASS | ELIMINATE |
| Circulatory Reflux Distillation | PASS | PASS | PASS | PASS | PASS | **SURVIVE** |
| Volatile Aromatic Extraction | PASS | PASS | PASS | PASS | PASS | **SURVIVE** |
| Fermentation | PASS | WEAK | WEAK | FAIL | PASS | ELIMINATE |
| Metallurgical Heat | WEAK | PASS | WEAK | FAIL | PASS | ELIMINATE |
| Dye Vat Management | PASS | WEAK | WEAK | FAIL | PASS | ELIMINATE |
| Glassmaking | WEAK | PASS | WEAK | FAIL | PASS | ELIMINATE |
| Chemical Sublimation | PASS | PASS | WEAK | FAIL | PASS | ELIMINATE |
| Alkaline Leaching | WEAK | WEAK | WEAK | WEAK | PASS | DEPRIORITIZE |
| Circulatory Conditioning | PASS | PASS | PASS | PASS | PASS | **SURVIVE** |

**Key elimination factor (D = Run Topology):** 6 classes fail because they have defined endpoints, non-looping progression, or transformative state changes incompatible with 100% STATE-C convergence and 0 endpoint markers.

**Survivors (3 classes):**
1. **Circulatory Reflux Distillation** (pelican/cohobation)
2. **Volatile Aromatic Extraction** (continuous circulation)
3. **Circulatory Thermal Conditioning** (digestion/stabilization)

**Common structural signature:** All three reduce to one umbrella class:

> **CLOSED-LOOP CIRCULATORY THERMAL PROCESS CONTROL**

Two subspecies:
- Extraction-type (aromatic waters, essential oils, concentrated extracts)
- Conditioning-type (thermal stabilization, digestion, maturation)

**What this does NOT show:**
- Does not identify specific products
- Does not interpret illustrations
- Cannot distinguish extraction-type from conditioning-type internally

See `phases/PCI_process_class_isomorphism/` for full analysis.

### Product-Space Plausibility (Phase PSP — SPECULATIVE) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

Historical product-space reduction: which product families could practitioners produce using the surviving process classes? **Explicitly speculative—does not identify specific products or ingredients.**

**Method:** 11 candidate product families evaluated against 5 plausibility filters:
- A. Process Compatibility (circulation required, indefinite operation, no fixed measurements)
- B. Risk Profile (irreversible failure, boundary risk)
- C. Sensory Judgment (smell, taste, clarity, behavior as endpoints)
- D. Economic Logic (high value, justifies prolonged attention)
- E. Historical Attestation (pre-manuscript era, incomplete disclosure)

**Elimination rules:** Any FAIL on A/B/C = eliminate; ≥3 WEAK = deprioritize.

| Product Family | A | B | C | D | E | Verdict |
|----------------|---|---|---|---|---|---------|
| Aromatic Distillates (Waters) | PASS | PASS | PASS | PASS | PASS | **PLAUSIBLE** |
| Essential Oils | PASS | PASS | PASS | PASS | PASS | **PLAUSIBLE** |
| Concentrated Resin Extracts | PASS | PASS | PASS | PASS | PASS | **PLAUSIBLE** |
| Matured/Digested Preparations | PASS | PASS | PASS | PASS | PASS | **PLAUSIBLE** |
| Stabilized Aromatic Compounds | PASS | PASS | PASS | WEAK | WEAK | **PLAUSIBLE** (borderline) |
| Medicinal Plant Waters | WEAK | WEAK | WEAK | PASS | PASS | DEPRIORITIZE |
| Pharmaceutical Syrups | WEAK | WEAK | WEAK | PASS | PASS | DEPRIORITIZE |
| Distilled Alcoholic Spirits | FAIL | WEAK | PASS | PASS | PASS | ELIMINATE |
| Fermented Products | FAIL | — | — | — | — | ELIMINATE |
| Crystallized Products | FAIL | — | — | — | — | ELIMINATE |
| Separated Fractions | FAIL | — | — | — | — | ELIMINATE |

**Key elimination factors:**
- A=FAIL (4 families): Defined endpoints, batch collection, passive process, phase change required
- ≥3 WEAK (2 families): Batch-compatible, recoverable failures, recipe-driven

**Plausible product families (5):**
1. **Aromatic Distillates (Waters)** — rose water, lavender water, orange flower
2. **Essential Oils** — concentrated volatile oils via cohobation
3. **Concentrated Resin Extracts** — balsams, oleoresins (frankincense, myrrh)
4. **Matured/Digested Preparations** — tinctures, elixirs via thermal conditioning
5. **Stabilized Aromatic Compounds** — fixatives for perfumery (borderline)

**Mapping to PCI subspecies:**
- Extraction-type: Waters, oils, resin extracts
- Conditioning-type: Digested preparations, stabilized compounds

**What this does NOT show:**
- Does not identify a specific product
- Does not use plant illustrations
- Does not infer ingredients or recipes
- Cannot distinguish between extraction-type and conditioning-type

See `phases/PSP_product_space_plausibility/` for full analysis.

### Product-Class Convergence (Phase PCC — SPECULATIVE) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

Class-level convergence test: do structural constraints uniquely favor extraction-type or conditioning-type products? **Explicitly speculative—does not identify specific products.**

**Method:** Extraction-type vs conditioning-type evaluated against 5 convergence criteria:
- A. Endpoint Logic Compatibility (lacks declarative "done" state)
- B. Hazard Localization (risks at boundaries, not mid-run)
- C. Memory Utility (boundary micro-expectation improves outcomes)
- D. Loop Stability (circulation beneficial without degradation)
- E. Historical Practice Consistency (documented, under-specified)

**Scoring rules:** FAIL on A, B, or D = eliminate; ≥2 WEAK = underconstrained.

| Class Type | A | B | C | D | E | Verdict |
|------------|---|---|---|---|---|---------|
| Extraction-Type | PASS | PASS | PASS | PASS | PASS | **SURVIVES (strong)** |
| Conditioning-Type | PASS | WEAK | WEAK | PASS | PASS | **SURVIVES (underconstrained)** |

**Discriminating structural features:**
- Phase-ordering hazard dominance (41%): fits extraction (core challenge) better than conditioning (catastrophic failure)
- CF-1 effect=0.622: strong boundary variation favors extraction (material-dependent) over conditioning (uniform)
- CF-2 effect=0.338: moderate boundary variation favors extraction over conditioning

**Key finding:** Both classes survive (no FAILs), but extraction-type shows stronger structural alignment:
- 5/5 PASS for extraction vs 3/5 PASS + 2 WEAK for conditioning
- All discriminating features favor extraction; none favor conditioning

**Formal conclusion:**
> "Both extraction-type and conditioning-type products remain structurally compatible. Further class-level convergence is not justified."

**Product family prioritization (if forced):**
- **Favored:** Aromatic Distillates (Waters), Essential Oils, Concentrated Resin Extracts
- **Underconstrained:** Matured/Digested Preparations, Stabilized Aromatic Compounds

> ⛔ **STOP CONDITION: BOTH PRODUCT CLASSES SURVIVE**
> Extraction-type and conditioning-type are BOTH structurally compatible.
> No internal analysis can distinguish between them. Do not attempt to resolve this underdetermination.

See `phases/PCC_product_class_convergence/` for full analysis.

### Plant-Context Intersection (Phase PCIP — SPECULATIVE) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

Falsification-focused test: do reliably identifiable plant illustrations contradict either extraction-type or conditioning-type product classes? **Explicitly speculative—non-instructional evidence only.**

**Method:** High-confidence plant identifications evaluated against 4 inclusion criteria:
1. Morphology strongly aligns with known medieval illustrations
2. Identification agreed by multiple sources OR functionally unambiguous
3. Historical use does NOT vary across major craft domains
4. Classification can be reduced to a use-category, not species name

**Critical finding:** All identified plant use-categories fail criterion #3. Medieval aromatic plants were historically processed via BOTH extraction AND conditioning:

| Plant Type | Extraction Use | Conditioning Use |
|------------|----------------|------------------|
| Iris/Orris (f38r) | Essential oil, butter | Compound pomades, fixatives |
| Umbellifers (f9r, f19r) | Aromatic waters, oils | Cordials, digested preparations |
| Shrubby aromatics | Bay oil, myrtle water | Compound unguents |
| Blue flowers | Distilled waters | Preserved preparations |

**Key finding:** No plant use-category was historically exclusive to one processing method. Both extraction AND conditioning were applied to the same aromatic materials.

**Formal conclusion:**
> "Plant illustrations do not add decisive constraint beyond prior system-level compatibility analysis."

**Rationale:**
- Zero plants meet all 4 inclusion criteria
- Aromatic alignment already counted in Phase PIAA (86.7%)
- Dual-use is the historical norm (same materials, different methods)
- No plant-based contradiction of either class can be established

**Product space status (unchanged):**
- Extraction-Type: SURVIVES (strong)
- Conditioning-Type: SURVIVES (underconstrained)

> ⛔ **STOP CONDITION: PLANT EVIDENCE ADDS NO CONSTRAINT**
> All identifiable plant types were historically used in BOTH extraction AND conditioning.
> Plant-based analysis cannot distinguish product classes. This pathway is closed.

See `phases/PCIP_plant_context_intersection/` for full analysis.

---

## Apparatus Layer (External, Non-Binding) — TIER 2

Internal structural analysis identifies strong homology with a specific apparatus class. This is **inferential and non-binding**—it does not modify the frozen grammar model.

### Best Match: Circulatory Reflux Systems

- **Compatibility:** CLASS_D = 100% match; alternatives ≤20%
- **Historical Representative:** Pelican alembic (late 15th-century)
- **Structural Homology:** 8/8 dimensions match Brunschwig (1500) and pseudo-Geber (~1300)
- **Surviving Candidates:** Reflux Distillation (1.000), Distillation Column (0.875), Steam Boiler (0.833)
- **Eliminated:** Biological homeostasis systems (failed TEST_3: no external operator)

### What This DOES NOT Mean

- No specific products or feedstocks identified
- No materials or substances encoded
- No alchemical phases or symbols mapped
- Apparatus identification is SPECULATIVE and DISCARDABLE

---

## External Comparative Research (Non-Binding) — TIER 2

Historical manual design analysis (Phase HFM) compared Voynich structure against documented patterns in technical manuals, curricula, and human factors research.

### Pattern Alignment with Historical Manuals

| Voynich Feature | Historical Match | Alignment |
|-----------------|------------------|-----------|
| 49 discrete instruction classes | Brunschwig's 4 degrees of fire | STRONG |
| 17 forbidden transitions | "Fourth degree coerces—reject it" | STRONG |
| 8 recipe families | Antidotaria list multiple procedures | STRONG |
| 0 material encoding | Apparatus manuals omit feedstock | STRONG |
| Expert knowledge assumed | Guild training model | STRONG |
| Kernel control points (k, h, e) | Process control theory | STRONG |
| Local continuity (d=17.5) | Codex organization patterns | STRONG |
| Positional indexing | Medieval recipe organization | MODERATE |
| Quire-aligned sections | Interruption recovery support | MODERATE |

**7 STRONG alignments, 4 MODERATE, 1 SPECULATIVE** across 12 documented patterns.

### Human Factors Rationale

The design is optimized for:
- **Cognitive load reduction:** 9.8x vocabulary compression
- **Error prevention:** Discrete approved procedures, not continuous tuning
- **Interruption recovery:** Positional markers, physical pause points at quire boundaries
- **Expert operation:** No definitions, no remedial instruction

### What This Shows

The Voynich's structure matches **15th-century distillation manual design** (Brunschwig 1500) on 8/8 structural dimensions. The design is **rational and historically attested** for expert-facing apparatus operation manuals.

### What This Does NOT Show

- ❌ Does not identify specific purpose
- ❌ Does not assign token meanings
- ❌ Does not prove historical identity
- ❌ Does not modify frozen grammar model

**Pattern alignment ≠ identification.** See `limits_statement.md` for full epistemological boundaries.

---

## Physics Plausibility Audit (Phase PPA) — TIER 2

Formal audit of whether the operational grammar is dynamically consistent with controlling a real physical system.

### Verdict: PHYSICALLY PLAUSIBLE (7/7 tracks pass)

| Track | Question | Result |
|-------|----------|--------|
| P-1 | Irreversibility respected? | **PASS** — 17 forbidden transitions are mutual exclusions, no recovery implied |
| P-2 | Energy conservation consistent? | **PASS** — 62% kernel contact, state changes require sustained input |
| P-3 | Latency tolerated? | **PASS** — 38% LINK density, max 7 consecutive waiting tokens |
| P-4 | Noise tolerated? | **PASS** — 9.8x compression, 41% safe margin, low sensitivity |
| P-5 | Control dimensions realistic? | **PASS** — 3 kernel axes collapse to 1-D effective behavior |
| P-6 | Extended stability achieved? | **PASS** — 100% convergence, extended runs scale linearly |
| P-7 | Failure modes legible? | **PASS** — All 5 failure classes map to real system failures |

### What This Means

A competent operator could use this grammar to control a real continuous physical system without violating thermodynamics, conservation laws, or causality.

### What This Does NOT Mean

- ❌ Does not prove the grammar is correct or optimal
- ❌ Does not identify what physical system is controlled
- ❌ Does not validate any historical claims
- ❌ Does not assign meanings to tokens

See `assumption_boundary.md` for full epistemological limits.

---

## Forward Experimental Inference (Phase L1L2) — TIER 2

Pre-registered falsification tests of whether the grammar maps coherently onto continuous physical process dynamics.

### Lane 1: Control-Grammar ↔ Process Dynamics Matching

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| Unique best templates | 3 | ≤3 | **PASS** |
| F-ratio (between/within variance) | 3.702 | >0.5 | **PASS** |
| Mean match score | 0.636 | >0.35 | **PASS** |

**Cluster Mapping:** 83 programs cluster into 5 groups mapping to 3 abstract process templates:
- TEMPLATE_A: Diffusion-limited process (24 programs)
- TEMPLATE_B: Rate-limited continuous control (17 programs)
- TEMPLATE_C: Equilibrium-seeking circulation (42 programs)

**Verdict:** Programs cluster coherently around compatible process dynamics. No mutual incompatibility.

### Lane 2: LINK Operator Stress Test

| Metric | t-stat | p-value | Cohen's d | Result |
|--------|--------|---------|-----------|--------|
| Failure rate | 6.972 | <0.0001 | **1.60** | High-LINK is SAFER |
| Reconvergence | -2.669 | 0.015 | -0.61 | High-LINK slower (expected) |
| Overshoot | -0.277 | 0.785 | -0.06 | Negligible |

**Key Finding:** LINK-heavy programs show significantly reduced failure rate (p<0.0001, effect size d=1.60 = very large). Slower reconvergence is physically expected for damped systems.

**Verdict:** LINK encodes deliberate waiting that confers measurable stability advantage.

### Lane 3: Material-Class Compatibility Test

| Material Class | Physical Traits | Failure Rate | Status |
|----------------|-----------------|--------------|--------|
| CLASS_A | High porosity, slow diffusion, swelling | 0.0% | COMPATIBLE |
| CLASS_B | Low porosity, hydrophobic, minimal swelling | 0.0% | COMPATIBLE |
| CLASS_C | Phase-change prone, emulsion-forming | **19.8%** | INCOMPATIBLE |
| CLASS_D | Non-swelling, rapid diffusion, stable | 0.0% | COMPATIBLE |
| CLASS_E | Homogeneous fluid, no solid interactions | 0.0% | COMPATIBLE |

**Statistical Test:** Kruskal-Wallis H=106.3, p<10⁻²¹, η²=0.93 (very large effect)

**Key Finding:** Only CLASS_C (phase-unstable materials) fails. All 480 failures = PHASE_COLLAPSE.

**Verdict:** Grammar shows differential material compatibility. Phase-stable materials operable; phase-unstable materials destabilize.

### Lane 4: Geometry Compatibility Test (Option A)

| Geometry | Description | Conv Rate | Failure | LINK Eff | Status |
|----------|-------------|-----------|---------|----------|--------|
| G1 | Linear open flow | 6.5% | 93.5% | 0.20 | INCOMPATIBLE |
| G2 | Batch vessel | 99.3% | 0.7% | 0.20 | COMPATIBLE |
| G3 | Partial recirculation | 99.9% | 0.1% | 0.20 | COMPATIBLE |
| G4 | Fully closed loop | 100% | 0% | 0.80 | COMPATIBLE |
| G5 | Multi-loop nested | 100% | 0% | 1.35 | COMPATIBLE |

**Statistical Test:** Kruskal-Wallis H=359.3, p<10⁻⁷⁶, η²=0.87; LINK effectiveness d=4.50

**Key Finding:** G1 (open flow) fails completely. LINK maps to physical delay only in closed-loop geometries (G4, G5).

**Verdict:** Grammar selectively compatible with closed-loop recirculation geometries.

### Combined Verdict: COHERENT

All four lanes pass. The grammar is coherent with continuous physical process control.

---

## Exploratory Process Mapping (Phase EPM) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

Post-lock speculative analysis comparing programs to each other and to abstract process families. **Explicitly speculative and non-binding.**

### Program Role Taxonomy

83 programs classified across 6 dimensions based on control signatures:

| Dimension | Distribution |
|-----------|-------------|
| Stability | MODERATE 55%, CONSERVATIVE 22%, AGGRESSIVE 18%, ULTRA_CONSERVATIVE 5% |
| Waiting | LINK_MODERATE 47%, LINK_HEAVY 29%, LINK_SPARSE 17%, LINK_HEAVY_EXTENDED 7% |
| Convergence | REGULAR_STABLE 47%, REGULAR_OPEN 40%, IRREGULAR 10%, FAST_STABLE 4% |
| Recovery | HIGHLY_RECOVERABLE 42%, RECOVERABLE 34%, LOW_RECOVERY 24% |

**Special markers**: 3 RESTART_CAPABLE (f50v, f57r, f82v), 10 HIGH_INTERVENTION, 43 EXTENDED

### Speculative Process Family Alignment

| Process Family | Alignment | Key Support |
|----------------|-----------|-------------|
| CONTINUOUS_EXTRACTION | **STRONG** | LINK = waiting for mobility-limited transport |
| CIRCULATION_CONDITIONING | **STRONG** | STATE-C convergence = target state maintenance |
| REDISTRIBUTION_PROCESS | MODERATE | Hazard topology = preventing runaway concentration |
| SEPARATION_BY_MOBILITY | MODERATE | Template diversity = different mobility profiles |
| MAINTENANCE_HOLDING | MODERATE | Ultra-conservative programs = pure maintenance |
| BREAKDOWN_DIGESTION | WEAK | Bidirectional hazards contradict irreversibility |

**Key finding**: Grammar equally consistent with extraction-type and conditioning-type processes. Internal analysis cannot distinguish.

### Negative Process Matches (Ruled Out)

| Process Class | Incompatibility | Primary Reason |
|---------------|-----------------|----------------|
| PHASE_CHANGE_PROCESSES | STRONG | CLASS_C fails exclusively (PHASE_COLLAPSE) |
| ONE_PASS_EXTRACTION | STRONG | G1 open flow = 93.5% failure |
| ENDPOINT_DEFINED_RECIPES | STRONG | 0 termination signals in grammar |
| HIGH_YIELD_BATCH | STRONG | LINK maps to nothing in batch geometry |
| EMULSION_PROCESSES | STRONG | Phase instability defeats control logic |
| RAPID_THERMAL_RAMPING | MODERATE | ENERGY_OVERSHOOT hazard class |
| DISCRETE_PRODUCT_RECIPES | MODERATE | Grammar describes operation, not production |

### Process Space Constraint

The negative matches collectively constrain to:
- Closed-loop circulation processes
- Continuous indefinite operation
- Gradual cumulative change OR maintenance
- Phase-stable substrates only

### What This Does NOT Show

- ❌ Does not identify specific purpose or products
- ❌ Does not assign token meanings
- ❌ Does not distinguish extraction from conditioning
- ❌ Does not modify frozen grammar model

**Speculative alignment ≠ identification.** See `exploratory_program_roles.md` and `speculative_process_alignment.md` for full analysis.

---

## Adversarial Process Family Comparison (Phase APF) — TIER 2

Stress test comparing two abstract process archetypes against the locked grammar. **Goal: find where each fits POORLY.**

### Archetypes Tested

- **PF-E (Extraction-Like)**: Removal/transfer of mobile fractions, depletion gradients, endpoint-seeking, throughput-valued
- **PF-C (Conditioning-Like)**: State maintenance, no completion notion, cyclic redistribution, stability-valued

### Summary Results

| Metric | PF-E (Extraction) | PF-C (Conditioning) |
|--------|-------------------|---------------------|
| Structural Coherence | 0.470 | **0.810** |
| Total Tensions | 10 | 2 |
| Unexplained Features | 7 | 6 |
| Contrivance Required | HIGH | MODERATE |

### Feature-by-Feature Fit

| Grammar Feature | PF-E | PF-C | Notes |
|-----------------|------|------|-------|
| 0 endpoint markers | POOR | GOOD | Extraction expects completion signals |
| 38% LINK density | POOR | GOOD | High waiting fits conditioning |
| 100% bidirectional hazards | POOR | GOOD | Extraction is irreversible |
| 18% AGGRESSIVE programs | POOR | POOR | Risky for both |
| 16.9% LINK_SPARSE | MODERATE | POOR | Speed priority fits extraction |
| 12% HIGH_INTERVENTION | GOOD | POOR | Monitoring fits extraction |
| 83 distinct programs | MODERATE | POOR | Diversity fits extraction variety |
| All programs reach STATE-C | POOR | GOOD | Convergence fits maintenance |

### What PF-E Struggles to Explain (Critical)

- **0 endpoint markers** — Extraction is inherently finite
- **100% bidirectional hazards** — Extraction is irreversible
- **High-LINK = safer** — Contradicts speed-safety tradeoff
- **Conservative program dominance** — Extraction pushes limits

### What PF-C Struggles to Explain

- **83 distinct programs** — Pure maintenance should be uniform
- **16.9% LINK_SPARSE** — Maintenance should wait
- **12% HIGH_INTERVENTION** — Active change, not passive maintenance
- **f57r = RESTART_PROTOCOL** — Why reset if maintaining?

### Features NEITHER Explains Well

- 3 restart-capable programs (too few for extraction, too many for conditioning)
- 18% AGGRESSIVE programs (risky for both)
- 5 hazard classes equally present (each expects different dominance)

### Verdict

**PF-C (Conditioning) fits better**, but the difference is not decisive. Neither pure archetype is a clean fit. A hybrid interpretation (Continuous Circulation Maintenance) would require least contrivance.

**This supports the EPM finding**: Internal analysis cannot distinguish between extraction-type and conditioning-type processes.

---

## Human-Track Ordering Analysis (Phase HTO) — TIER 2

Tests whether manuscript ordering and sectioning are structured to manage operator risk, learning, and recovery. **All system-track structures locked.**

### Verdict: PARTIALLY_STRUCTURED (2/5 tests pass)

| Test | Verdict | Key Finding |
|------|---------|-------------|
| 1. Order vs Risk | **SIGNAL** | Monotonic increase (rho=0.39, p=0.0004) |
| 2. Boundary Clustering | NULL | Programs randomly distributed |
| 3. Currier A/B | N/A | Insufficient data (all Currier B in corpus) |
| 4. Local Neighborhood | **SIGNAL** | 88% buffering vs 49% null (p<0.0001) |
| 5. Restart Placement | NULL | Randomly placed |

### Key Findings

- **Risk increases through manuscript**: First third (1.69) → Middle (2.00) → Last (2.07)
- **Risky programs buffered**: 88% of aggressive programs surrounded by safer neighbors
- **Transitions smoothed**: Mean risk jump (0.31) significantly less than random (0.44)
- **Section boundaries NOT recovery points**: No clustering of special programs near boundaries
- **Restart programs NOT strategically placed**: f50v, f57r, f82v positions appear random

### What This Shows

- Folio ordering reflects **operator learning progression** (easier → harder)
- Local safety buffering is **intentional** (p<0.0001)
- Risk management encoded in **both grammar AND local ordering**

### What This Does NOT Show

- ❌ Section boundaries do not serve as recovery/restart points
- ❌ Macro-structure (sections, quires) not risk-aligned
- ❌ Restart program placement appears arbitrary

---

## Cross-Domain Comparative Engineering Analysis (Phase CDCE) — TIER 2

Situates the locked control grammar among real continuous processes by engineering comparison, not historical identification. **Question: What would a modern engineer conclude?**

### Domain Alignment Summary

| Domain | Control | Geometry | Library | Human | **OVERALL** |
|--------|---------|----------|---------|-------|-------------|
| Reflux Distillation | HIGH | HIGH | HIGH | HIGH | **HIGH** |
| Circulation Conditioning | HIGH | HIGH | MED | HIGH | **HIGH** |
| Continuous Extraction | MED | MED | MED | MED | **MED** |
| Long-Duration Equilibration | MED | MED | LOW | MED | **MED** |
| Batch Processes | LOW | LOW | LOW | LOW | **INCOMPATIBLE** |
| Open-Flow Processes | LOW | LOW | LOW | LOW | **INCOMPATIBLE** |
| Phase-Change Processes | LOW | LOW | LOW | LOW | **INCOMPATIBLE** |

### Hard Incompatibilities (7 domains ruled out)

| Domain | Primary Conflict |
|--------|------------------|
| Phase-change processes | CLASS_C fails exclusively (100% PHASE_COLLAPSE) |
| Open-flow systems | G1 geometry = 93.5% failure |
| Batch processes | LINK semantics void without circulation |
| Endpoint-defined recipes | 0 termination markers in grammar |
| High-throughput production | Priority inversion (stability >> speed) |
| Emulsion processes | Interface instability defeats control |
| Rapid thermal ramping | ENERGY_OVERSHOOT explicit hazard class |

### Engineer's Intuition Summary

What a modern process engineer would conclude without historical context:

- **"This is a control system, not a recipe book"** — Programs describe operation, not production
- **"The author was safety-conscious"** — 77% conservative programs, 17 bidirectional hazards
- **"This requires circulation"** — 38% wait instructions only work with recirculation
- **"Discrete programs, not continuous tuning"** — 83 fixed programs, pre-automation design
- **"Phase changes are catastrophic"** — System designed to avoid, not achieve, phase transitions

### Modern Facility Interpretation

> *"A circulation conditioning or reflux system with pre-automation control philosophy. Safety-conscious, expert-operated, no product specification. The grammar handles operation—outcome judgment is external."*

**What would surprise them:**
1. Complete absence of completion criteria
2. 38% wait instruction density
3. Bidirectional (not threshold) hazard structure
4. 83 distinct programs without continuous tuning
5. Zero process/product identification

### What This Shows

- Grammar is recognizable as **continuous process control** to modern engineers
- Closest matches: **reflux distillation, circulation conditioning**
- Design is **pre-automation but coherent**

### What This Does NOT Show

- ❌ Does not identify specific purpose or products
- ❌ Does not prove historical identity
- ❌ Does not distinguish between compatible domains
- ❌ Does not modify frozen grammar model

---

## Speculative Reconstruction Phase (Phase SRP) — TIER 4

> **⚠️ EXPLORATORY — Idea-generation only. May contradict other sections. Does not modify frozen model.**

Exploratory speculation about possible materials, products, and workshop context. **Explicitly non-binding—does not modify locked grammar.**

### Candidate Product Classes

| Product Class | Structural Fit | Historical Fit | Confidence |
|---------------|----------------|----------------|------------|
| **Aromatic waters** | STRONG | STRONG | **MEDIUM-HIGH** |
| Medicinal extracts | STRONG | STRONG | MEDIUM |
| Concentrated essences | MODERATE | MODERATE | LOW-MEDIUM |
| Stabilized preparations | STRONG (partial) | MODERATE | LOW-MEDIUM |

### Material Class → Real Materials (Speculative)

| Abstract Class | Real Medieval Materials | Grammar Fit |
|----------------|------------------------|-------------|
| CLASS_A (porous, swelling) | Dried leaves, flowers, roots, bark | COMPATIBLE |
| CLASS_B (dense, hydrophobic) | Resins, seeds, citrus peel | COMPATIBLE |
| CLASS_C (phase-unstable) | Fresh plant material, fats, emulsions | INCOMPATIBLE |
| CLASS_D (stable, rapid diffusion) | Alcohol/water mixtures, clear extracts | COMPATIBLE |
| CLASS_E (homogeneous fluid) | Distilled water, pure alcohol | COMPATIBLE |

### Illustrations as Memory Aids

- **Function:** Category markers, mnemonic anchors (NOT operational)
- **Plant prominence:** Root emphasis may indicate root-processing sections
- **Botanical abstraction:** Deliberately non-specific; category, not species
- **Navigation:** Visual bookmarks for expert users

### Calendar/Seasonality

- **Strong interpretation:** Harvesting windows (LOW confidence)
- **Weak interpretation:** Organizational mnemonic (MEDIUM confidence)
- **Environmental:** Winter processing may be optimal (indoor, stable temp)

### Practitioner's Summary

**Plausibly making:**
1. Aromatic waters (rose, lavender, orange flower)
2. Medicinal herbal extracts (dried plant infusions)
3. Stabilized/matured preparations

**Certainly NOT making:**
1. Distilled spirits (requires phase change)
2. Crystallized products (requires phase change)
3. Separated fractions (requires open flow)

### The 83-Program Interpretation

Programs likely represent **substrate × intensity combinations**, not 83 distinct products. An operator might make 5-10 things using many programs depending on material source, condition, and batch.

### What This Does NOT Claim

- ❌ Specific plants or species
- ❌ Specific products identified
- ❌ Commercial vs. personal use
- ❌ Geographic origin
- ❌ Token meanings

**Speculation ≠ identification.** See `candidate_products.md` for full analysis.

---

## Product Isolation Analysis (Phase PIA) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

Multi-axis structural convergence test to isolate the most plausible product class. **Explicitly speculative—does not modify locked grammar.**

### Method

10 candidate products scored against 7 independent axes (0-3 each, max 21):
- A1: Process Compatibility (closed-loop, phase stability)
- A2: Control Complexity Justification (stakes, degradation risk)
- A3: Material Class Compatibility (CLASS_A-E alignment)
- A4: Economic & Social Value (1400-1450)
- A5: Frequency of Production (justifies 83 programs)
- A6: Outcome Judgment Externality (sensory, subjective)
- A7: Historical Documentation Pattern (semi-secret, practice-based)

### Final Ranking

| Rank | Product | Score | Confidence | Status |
|------|---------|-------|------------|--------|
| **1** | Aromatic Waters | **19/21** (90.5%) | HIGH | Primary candidate |
| **2** | Medicinal Herb Waters | **18/21** (85.7%) | MEDIUM-HIGH | Strong alternative |
| **3** | Resin Extracts | **16/21** (76.2%) | MEDIUM | Viable subset |
| — | Distilled Spirits | ELIMINATED | — | Phase change fatal |
| — | Fermented Products | ELIMINATED | — | Batch + phase change |
| — | Cosmetics | 12/21 | VERY LOW | CLASS_C emulsion problem |

### Why Aromatic Waters Wins

| Grammar Feature | Aromatic Waters Fit |
|-----------------|---------------------|
| Non-semantic grammar | Operator smells what they're making—words don't help |
| Abstract illustrations | Category markers, not species IDs (roses vary by region) |
| No endpoints encoded | Fragrance quality is purely subjective |
| 83 programs | Substrate × intensity × source combinations |
| 77% conservative | Volatiles need gentle handling |
| 17 forbidden transitions | Quality destruction hazards |

### Multi-Product Workshop Interpretation

| Product | Programs Used | Frequency |
|---------|---------------|-----------|
| Aromatic waters | CONSERVATIVE, MODERATE | Primary |
| Medicinal waters | MODERATE | Secondary |
| Resin extracts | AGGRESSIVE | Occasional |
| Stabilization | ULTRA_CONSERVATIVE | As needed |

### Residual Concerns

| Concern | Severity |
|---------|----------|
| 17 forbidden transitions seems excessive for aromatics | MODERATE |
| 18% AGGRESSIVE programs higher than expected for florals | LOW-MODERATE |
| 3 RESTART programs unexplained | LOW |

### Sensitivity Analysis

Ranking is **ROBUST** across all tested perturbations:
- Doubling any single axis weight: Aromatic Waters remains #1
- Removing historical axes (A4, A7): Rankings stable
- No plausible single change overturns ranking

### Verdict

> **If only one product class were responsible for this manual: Aromatic Waters (90.5% convergence)**

The workshop likely produced multiple products—primarily aromatic waters, secondarily medicinal waters, occasionally resin extracts—explaining the full program library.

See `product_convergence_ranking.md`, `axis_by_axis_scoring_table.md`, `sensitivity_analysis.md`, `top_candidate_rationale.md`.

---

## Plant Illustration Alignment Analysis (Phase PIAA) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

Statistical class-level analysis testing whether Voynich botanical illustrations align with perfumery/aromatic water plant classes. **Explicitly speculative—does not modify locked grammar.**

### Method

30 botanical folios examined for class-level plant identification (NOT species-level). Each assigned to plant classes:
- AF: Aromatic Flower
- ALH: Aromatic Leaf Herb
- AS: Aromatic Shrub/Tree
- RT: Resinous Tree/Shrub
- MH: Medicinal Herb (non-aromatic)
- FP: Food Plant
- DP: Dye Plant
- TP: Toxic/Industrial Plant

### Key Results

| Metric | Value | Null Expectation | Deviation |
|--------|-------|------------------|-----------|
| Aromatic-aligned folios | **86.7%** (26/30) | ~35% | **+51.7%** |
| Food plant presence | 3.3% (1/30) | ~15-20% | **-12%** |
| Dye plant presence | 0% (0/30) | ~5-10% | **-5%** |
| Grain presence | 0% (0/30) | ~5-10% | **-5%** |
| Root emphasis | **73%** (22/30) | ~30% | **+43%** |
| Blue/purple flowers | **47%** (14/30) | ~20% | **+27%** |

### Plant Class Distribution

| Class | Frequency | Perfumery Relevance |
|-------|-----------|---------------------|
| Aromatic Flower | 56.7% | HIGH |
| Aromatic Leaf Herb | 53.3% | HIGH |
| Medicinal Herb | 46.7% | MEDIUM |
| Aromatic Shrub | 13.3% | HIGH |
| Resinous | 10.0% | HIGH |
| Food Plant | 3.3% | LOW |
| Dye/Industrial | 0% | NONE |

### Negative Control: Systematic Absences

| Absent Class | Expected (General Herbal) | Significance |
|--------------|---------------------------|--------------|
| Grains/Cereals | 5-10% | **SIGNIFICANT** |
| Vegetables | 5-10% | **SIGNIFICANT** |
| Dye Plants | 5-10% | **SIGNIFICANT** |
| Fiber Plants | 2-5% | MODERATE |

### Notable Perfumery Indicators

- **f38r**: Iris-type plants with connected rhizomes (orris root = major perfumery material)
- **f9r, f19r**: Feathery umbellifer-type (fennel, dill, angelica family)
- **f11r, f11v, f37v**: Shrubby forms (myrtle, bay, rosemary types)
- **73% root emphasis**: Unusual for general herbals; consistent with extraction-source awareness

### Statistical Summary

| Metric | Value |
|--------|-------|
| Perfumery Alignment Index | **80.1%** |
| Null hypothesis (general herbal) | **REJECTED** (p < 0.001) |
| Overall Confidence | **HIGH (85.6%)** |

### Verdict

> **If judged by plant class alone, this corpus IS CONSISTENT with a perfumery-oriented manuscript.**

This finding **reinforces** the Product Isolation Analysis conclusion that aromatic waters is the primary candidate product class.

### What This Does NOT Show

- ❌ Does not identify specific plant species
- ❌ Does not prove manuscript purpose
- ❌ Does not assign token meanings
- ❌ Does not modify frozen grammar model

See `plant_class_assignments.md`, `perfumery_alignment_statistics.md`, `negative_control_plant_classes.md`, `confidence_assessment.md`.

### Speculative Plant Identifications (Phase EXT-SEQ-01B) — TIER 4

> **⚠️ TIER 4 EXPLORATORY — Speculative identifications, NOT proven.**

Attempted species-level identification based on PIAA morphology + 15th-century European aromatic availability. Used to test finer-grained seasonal ordering.

**High-confidence identifications (17/30 = 57%):**

| Folio | Best Guess | Confidence | Peak Month |
|-------|------------|------------|------------|
| f38r | **Iris/Orris** | VERY HIGH | May |
| f9r | Fennel | HIGH | July |
| f11r | Lavender | HIGH | July |
| f11v | Bay Laurel | HIGH | May |
| f5r | Violet | HIGH | April |
| f37v | Myrtle | HIGH | June |
| f45v | Cardoon | HIGH | August |

**Seasonal distribution (speculative):**
- EARLY_SPRING (Mar-Apr): 1 (3%)
- LATE_SPRING (May-Jun): 12 (40%)
- SUMMER (Jul-Aug): 16 (53%)
- AUTUMN (Sep-Oct): 1 (3%)
- WINTER: 0 (0%)

**Key finding:** 93% of speculatively identified plants peak May-August (aromatic flowering season). No sequential ordering detected—plants are interleaved rather than clustered by season.

**Ordering test results (0/3 significant):**
- Adjacency: p = 1.00, d = -0.08
- Monotonic drift: p = 0.37, rho = 0.17
- Clustering: p = 0.36, d = -1.23 (LESS clustered than random)

**Interpretation:** The botanical section documents **peak-season aromatics** without calendar organization. This is consistent with **material selection** (what to process) rather than **temporal instruction** (when to process).

See `phases/EXT_SEQ_01_seasonal_ordering/speculative_plant_data.md` for complete identification table.

---

## Program-Plant Correlation Analysis (Phase PPC) — TIER 2

Statistical test of whether program behavior correlates with plant illustration morphology, suggesting intentional material-aware pairing. **Independence requirement: morphology classified BLIND before correlation.**

### Method

24 botanical folios with both program data and plant illustrations:
- Phase 1: Blind morphology classification (ROOT_HEAVY, FLOWER_DOMINANT, LEAFY_HERB, WOODY_SHRUB, COMPOSITE)
- Phase 2: Independent program metric extraction (Aggressiveness, LINK class, Hazard proximity, Duration)
- Phase 3: Statistical correlation tests (Chi-square, Fisher's exact, permutation)

### Key Results

| Test | Statistic | p-value | Result |
|------|-----------|---------|--------|
| Chi-square (Aggression × Morphology) | χ²=4.76 | **0.5747** | NOT SIGNIFICANT |
| Chi-square (LINK × Morphology) | χ²=2.89 | **0.8224** | NOT SIGNIFICANT |
| Fisher's exact (AGGRESSIVE ↔ ROOT_HEAVY) | OR=1.00 | **1.0000** | NO ASSOCIATION |
| Permutation test (10,000 shuffles) | — | **0.6762** | CONSISTENT WITH CHANCE |

### Specific Hypothesis Tests

| Hypothesis | Observed | Expected | Ratio | Verdict |
|------------|----------|----------|-------|---------|
| AGGRESSIVE → ROOT_HEAVY | 2 | 2.00 | 1.00 | NO ENRICHMENT |
| CONSERVATIVE → FLOWER_DOMINANT | 3 | 2.62 | 1.14 | NOT SIGNIFICANT |
| LINK_HEAVY → FLOWER_DOMINANT | 1 | 1.75 | 0.57 | DEPLETED (opposite) |
| EXTENDED → ROOT_HEAVY | 2 | 2.00 | 1.00 | NO ENRICHMENT |

### Morphology Distribution (Blind Classification)

| Primary Tag | Count | Percentage |
|-------------|-------|------------|
| ROOT_HEAVY | 10 | 41.7% |
| FLOWER_DOMINANT | 7 | 29.2% |
| LEAFY_HERB | 5 | 20.8% |
| COMPOSITE | 2 | 8.3% |
| WOODY_SHRUB | 1 | 4.2% |

### Verdict

> **"There IS NOT statistically meaningful alignment between procedural style and plant morphology."**

All p-values >> 0.05. Odds ratios near 1.0. Permutation test confirms consistency with random assignment.

### What This Shows

- Program assignment appears **random with respect to plant morphology**
- Aggressive programs NOT concentrated on root-heavy plants
- Conservative programs NOT concentrated on flower-dominant plants
- **Illustrations and programs are independent layers**

### What This Reinforces

- Phase ILL finding: Illustrations are **epiphenomenal**
- Programs describe **generic apparatus operation**, not material-specific handling
- Material knowledge is **external** (operator knows what to process)

### What This Does NOT Address

- Section-level correlation (untested)
- Symbolic/non-morphological plant meanings
- Sequential ordering correlation within sections
- Text-based material encoding

See `plant_morphology_classification.md`, `program_role_metrics.md`, `program_plant_correlation_table.md`, `statistical_significance_report.md`, `interpretive_summary.md`.

---

## Failure-Mode Reconstruction Analysis (Phase FMR) — TIER 3

> **⚠️ SPECULATIVE — Non-binding interpretive layer. Does not modify frozen model.**

Phenomenological reconstruction of what real-world failures the control grammar prevents. **Focus: craft risk, not product identification.**

### The Five Hazard Classes (17 Forbidden Transitions)

| Class | Count | % | Physical Mechanism | Dominant Fear |
|-------|-------|---|-------------------|---------------|
| PHASE_ORDERING | 7 | 41% | Vapor lock, premature condensation | **PRIMARY** |
| COMPOSITION_JUMP | 4 | 24% | Contamination, impurity carryover | Secondary |
| CONTAINMENT_TIMING | 4 | 24% | Overflow, pressure failure | Secondary |
| RATE_MISMATCH | 1 | 6% | Flooding, weeping, channeling | Tertiary |
| ENERGY_OVERSHOOT | 1 | 6% | Bumping, scorching, thermal shock | Tertiary |

### What the Author Feared Most

1. **Phase disorder** — material changing state in wrong location (vapor where liquid should be)
2. **Contamination** — impure fractions passing before separation complete
3. **Apparatus failure** — overflow, pressure events, physical damage
4. **Flow chaos** — rate imbalance destroying circulation rhythm
5. **Thermal damage** — scorching from excessive heat

### Why Failures Are Irreversible

| Failure Type | Why No Recovery Mid-Run |
|--------------|------------------------|
| Phase disorder | Condensate in wrong location cannot drain without disassembly |
| Contamination | Mixed impurities cannot be separated once combined |
| Spillage | Escaped material cannot be recovered |
| Scorching | Burned character cannot be removed from product |
| Flow chaos | Balance must be rebuilt from stable initial state |

### Aggressive vs Conservative Programs

| Aspect | Aggressive (18%) | Conservative (77%) |
|--------|------------------|-------------------|
| Link density | LOW (less waiting) | HIGH (more waiting) |
| Hazard proximity | HIGH (near forbidden zones) | LOW (safe margin) |
| Use case | Time-sensitive materials, experienced operators | Valuable materials, training, normal operation |
| Risk profile | Higher failure probability, faster completion | Lower failure probability, slower completion |

**Why conservatism dominates**: Failures are irreversible. Cost of batch loss exceeds any time saved.

### Restart Logic (3 Programs)

| Program | Interpretation |
|---------|----------------|
| f50v | Restart-capable, max_consecutive_link = 17 (extreme waiting) |
| f57r | **Only folio with explicit reset** — encodes intentional iteration |
| f82v | Longest restart-capable program (879 tokens) |

**Why so few**: Most failures contaminate apparatus; restart requires clean system. f57r encodes iterative refinement, not error recovery.

### Author Intent via Failures

**What the book prevents** (explicit encoding):
- Phase disorder from impatience
- Contamination from rushing separation
- Apparatus damage from improper sequencing
- Thermal damage from excessive heat

**What the book assumes** (not encoded):
- Basic fire management competence
- Physical safety awareness
- Sensory judgment for quality
- Material selection knowledge

**What the book deliberately omits**:
- Product identity (none of your business)
- Material specifications (external knowledge)
- Success criteria (your senses tell you)
- Completion signals (outcome judgment external)

### Author Psychology Summary

> "The book encodes my fears, so that you do not have to learn them through loss."

The author wrote this manual to **prevent irreversible failures** observed or feared in practice. The dominance of phase-ordering hazards (41%) suggests personal experience with vapor/liquid mishaps in circulation apparatus.

See `hazard_taxonomy.md`, `forbidden_transition_scenarios.md`, `aggressive_conservative_risk_analysis.md`, `restart_logic_interpretation.md`, `author_intent_via_failures.md`.

---

## Frozen Conclusion — TIER 0

> **The Voynich Manuscript encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.**

| Metric | Value | Confidence |
|--------|-------|------------|
| Instruction classes | 49 (9.8x compression) | HIGH |
| Recipe families | 8 canonical patterns | HIGH |
| Grammar coverage | 100% | HIGH |
| Folios enumerated | 83 (75,248 instructions) | HIGH |
| Translation-eligible zones | 0 | HIGH |
| Model existence | Structure is real, not artifactual | HIGH |
| Model parameters | 2 claims need clarification | MEDIUM |

### Weakened Claims (Require Methodological Clarification)

1. **"Universal 2-cycle structure"** — Dominant cycle is 5-6 at character level, varies with segmentation
2. **"17 forbidden transitions as active constraints"** — 100% legality with or without constraints (never violated in corpus)

---

## Validated Constraints (249 Total) — TIER 0

> **⚠️ SCOPE CAVEAT (Phases CAud/CAud-G/CAS):** All grammar, hazard, and executability claims below apply to **Currier B only** (64.7% of tokens, 82 folios). Currier A (31.8% of tokens, 114 folios) is **DISJOINT** and operates as a **NON_SEQUENTIAL_CATEGORICAL_REGISTRY** — a flat tagging system with mutually exclusive marker prefixes, designed separation from B, and database-like properties. See constraints 224-240.

Any valid interpretation must account for these findings. Organized by category.

### Executability (Constraints 72-84, 115-125)

| # | Constraint |
|---|------------|
| 74 | 100% execution convergence to stable states |
| 79 | Only STATE-C essential (system works without A, B, or D) |
| 84 | System is fundamentally MONOSTATE |
| 115 | 0 non-executable tokens (every token affects execution) |
| 119 | 0 translation-eligible zones |
| 120 | PURE_OPERATIONAL verdict |
| 121 | 49 instruction equivalence classes (9.8x compression) |
| 124 | 100% grammar coverage |

### Kernel Structure (Constraints 85-95, 103-108)

| # | Constraint |
|---|------------|
| 85 | 10 single-character primitives (s, e, t, d, l, o, h, c, k, r) |
| 89 | Core within core: k, h, e (centrality 4847, 2968, 2181) |
| 90 | 500+ 4-cycles, 56 3-cycles |
| 103 | k = ENERGY_MODULATOR (qo operator 3466x) |
| 104 | h = PHASE_MANAGER (ct operator) |
| 105 | e = STABILITY_ANCHOR (54.7% recovery paths) |
| 107 | All kernel nodes BOUNDARY_ADJACENT to forbidden transitions |

### Hazard Topology (Constraints 109-114) — SEL-D AUDIT APPLIED

| # | Constraint | SEL-D Status |
|---|------------|--------------|
| 109 | 5 failure classes: PHASE_ORDERING, COMPOSITION_JUMP, CONTAINMENT_TIMING, ENERGY_OVERSHOOT, RATE_MISMATCH | **WEAKENED**: RATE_MISMATCH + ENERGY_OVERSHOOT are single-member (mergeable); CONTAINMENT_TIMING is theoretical-only (0 corpus impact) |
| 110 | PHASE_ORDERING dominant (7/17 = 41%) | STABLE |
| 111 | ~~100% bidirectional (all failures are mutual exclusions)~~ | **FALSIFIED**: 65% asymmetric (11/17 show reverse exists while forward blocked) |
| 112 | ~~KERNEL_ADJACENT clustering~~ | **FALSIFIED**: 59% (10/17) are distant from kernel; no structural forcing |

**SEL-D Verdict:** Hazard COUNT (17 transitions) = Tier 0 STABLE. Hazard CHARACTERIZATION = downgraded to Tier 2.

### Language Rejection (Constraints 130-132)

| # | Constraint |
|---|------------|
| 130 | DSL hypothesis rejected (reference rate 0.19%, threshold 5%) |
| 131 | Role consistency LOW (23.8%, threshold >80%) |
| 132 | Language encoding CLOSED (pre-registered falsification test passed) |

### Organizational Structure (Constraints 153-160)

| # | Constraint |
|---|------------|
| 153 | Prefix/suffix axes partially independent (MI=0.075 bits) |
| 154 | Extreme local continuity (d=17.5 vs random) |
| 155 | Piecewise-sequential geometry (PC1 rho=-0.624) |
| 156 | Detected sections match codicology |
| 157 | Circulatory reflux uniquely compatible (100% match) |
| 158 | Extended runs structurally necessary (12.6% envelope gap) |
| 159 | Section boundaries are organizational (F-ratio 0.37) |
| 160 | Variants are discrete alternatives (coverage 43%) |
| 161 | Folio ordering shows risk gradient (rho=0.39, p=0.0004) |
| 162 | Aggressive programs buffered by safer neighbors (88% vs 49% null) |
| 163 | Grammar recognizable as continuous process control; 7 domains ruled incompatible |
| 164 | Botanical illustrations 86.7% perfumery-aligned (p<0.001 vs general herbal null) |
| 165 | No program-morphology correlation (all p>>0.05, OR=1.0); programs independent of plant illustrations |
| 166 | Uncategorized tokens: zero forbidden seam presence (0/35 seams) |
| 167 | Uncategorized tokens: 80.7% section-exclusive, 9.1% vocabulary overlap across manuscript |
| 168 | Uncategorized tokens: single unified layer, NOT multiple distinct systems |
| 169 | Uncategorized tokens: actively avoid hazard zones (mean 4.84 vs expected 2.5) |
| 170 | Uncategorized tokens: morphologically distinct from operational grammar (p<0.001) |
| 171 | Purpose class: only continuous closed-loop process control survives elimination under constraint |
| 172 | Human-track tokens: 99.6% LINK-proximal; navigation serves waiting phases, not active intervention |
| 173 | Human-track tokens: linguistic hypothesis EXHAUSTED; tokens are markup, NOT symbolic labels (HLL-2) |
| 174 | Human-track tokens: intra-role outcome divergence (CF-1 effect=0.62, CF-2 effect=0.34); craft memory encoded (IMD) |
| 175 | Process-class isomorphism: 3 classes survive (circulatory reflux, aromatic extraction, thermal conditioning); 7 eliminated by run topology (PCISO) |
| 176 | Product-space plausibility: 5 families survive (aromatic waters, essential oils, resin extracts, digested preparations, stabilized compounds); 4 eliminated by process incompatibility (PSP) |
| 177 | Product-class convergence: both extraction-type and conditioning-type survive; extraction-type shows stronger alignment (5/5 PASS vs 3/5 PASS); no decisive distinction (PCC) |
| 178 | Folio-level control signatures: 83 folios yield 33 operational metrics; all internally derived from frozen grammar (OPS-1) |
| 179 | Control strategy clustering: 4 stable regimes identified (K-Means k=4, Silhouette=0.23, ARI=0.88); methods agree within ±1 (OPS-2) |
| 180 | Aggressive folios cluster non-randomly: all 6 aggressive folios in REGIME_3 (Chi²=18.0, p<0.001) (OPS-2) |
| 181 | Regime tradeoffs: 3/4 regimes Pareto-efficient; REGIME_3 dominated (high risk, low stability, no compensating advantage) (OPS-3) |
| 182 | Restart-capable folios have significantly higher stability (0.589 vs 0.393); confirms recovery-stability link (OPS-3) |
| 183 | No regime dominates all axes: best time=REGIME_4, best risk=REGIME_2, best stability=REGIME_1; confirms structural tradeoff (OPS-3) |
| 184 | Operator decision model: 9 pressure-induced transition pathways; 3 prohibited transitions (worsen all pressures); all cross-checks PASS (OPS-4) |
| 185 | REGIME_3 (dominated) serves as transient throughput state: entered under acute time pressure, exited under accumulated risk/stability pressure (OPS-4) |
| 186 | Regime switching graph has no pressure-free cycles; conservative stabilization path always exists from any regime (OPS-4) |
| 187 | Control Engagement Intensity (CEI) manifold formalized: composite index integrating time, risk, and stability pressures; weights documented (OPS-5) |
| 188 | CEI bands: 4 regimes ordered REGIME_2 < REGIME_1 < REGIME_4 < REGIME_3 (low to high engagement intensity); all validation checks PASS (OPS-5) |
| 189 | CEI dynamics: bidirectional movement confirmed; asymmetric costs (down-CEI easier, ratio=1.44); dominated transient = brief high-CEI excursion (OPS-5) |
| 190 | LINK-CEI correlation = -0.7057 (strong negative); LINK density acts as CEI damping; internal investigation closed (OPS-5) |
| 191 | CEI smoothing: manuscript ordering reduces adjacent CEI jumps (2.8th percentile vs null, d=1.89); local smoothing is intentional (OPS-6) |
| 192 | Restart placement: restart-capable folios have significantly lower CEI (1.9th percentile, d=2.24); strategically placed at low-engagement positions (OPS-6) |
| 193 | Navigation topology: max retreat distance and trap positions WORSE than random (0th percentile, d=-7.33); global navigation not CEI-optimized (OPS-6) |
| 194 | Codex organization: PARTIAL structural support for CEI management (2/5 hypotheses supported); local smoothing present, global navigation suboptimal (OPS-6) |
| 195 | Human-track compensation NOT detected: trap regions show lower HT density (d=-0.60) and shorter wait runs (d=-0.54); human-track does not offset navigation difficulty (OPS-6.A) |
| 196 | Manual-design archetype: 100% match to EXPERT_REFERENCE; tolerates traps, uses local smoothing, LINK-anchored navigation, strategic restart placement (OPS-6.A) |
| 197 | Design rationale: manuscript tolerates poor global navigation because it is designed for experts who already know the process, not for novice training (OPS-6.A) |
| 198 | Operator doctrine consolidated: 5 core principles (waiting default, escalation irreversible, restart requires low-CEI, text holds position not escape, throughput transient); OPS-1 through OPS-6.A internally consistent; 0 contradictions; OPS CLOSED (OPS-7) |
| 199 | Material correlation: ~~ALL botanical materials eliminated~~ **REVISED** — EXT-4 duration criterion invalidated by SID-05 (attentional pacing implies hours, not weeks); botanical materials RECONSIDERED; both mineral AND botanical interpretations now survive (EXT-4 + EXT-4 REVISION) |
| 200 | Role classification: survivors split into Final Products (2: Aurum Potabile, Mercurial Elixirs - actually consumed with documented deaths), Platform Reagents (3: Philosophical Mercury, Sal Ammoniac, Oil of Vitriol), and Functional Intermediate (1: Antimony Preparations); product identification JUSTIFIED (EXT-5A) |
| 201 | Use-context mapping: all 6 survivors absorbed into single coherent ecosystem (guild-restricted, court-sponsored, expert-operated alchemical-medical practice); preparation and use structurally decoupled; Voynich encodes preparation, NOT downstream application; further historical narrowing (region, guild, lineage) JUSTIFIED (EXT-5B) |
| 202 | Institutional compatibility: goldsmith/assayer workshops (Central Europe 1400-1550, N. Italy 1400-1470) survive all constraints; university-adjacent and N. Italy apothecary-adjacent ELIMINATED; Tier 3-4 convergence achieved (EXT-6) |
| 203 | Structural parallel search: partial parallels exist (quintessence tradition 7.0/10, Pseudo-Geber 6.5/10), but Voynich structurally exceptional; exceeds all comparands on material abstraction, theoretical absence, endpoint absence, library scale, illustration independence; null comparison class (recipe books, cookbooks) fails on 5/10 features (EXT-7) |
| 204 | ~~Abstraction layer reconciliation~~ **OPS-R FAILED** (SEL-B): 2-cycle oscillation contradicts MONOSTATE; LINK oscillation contradicts non-intervention; claims NON-AUTHORITATIVE |
| 205 | Residue tokens: 82% section exclusivity NOT emergent from any single global generative process; section-conditioned models required; Markov/context-free/null all fail C3 constraint (SID-01) |
| 206 | Section regime clustering: 8 sections cluster weakly into 2 regimes (silhouette=0.292 < 0.4 threshold); section identity NOT compressible into reliable regime structure; sections remain irreducible conditioning variable (SID-01.1) |
| 207 | Micro-cipher stress test: 18 subsets tested via 5 sampling strategies; 0/18 passed all 4 formal tests (substitution invariance, information gain, compression advantage, global consistency); no hidden cipher layers, encoding schemes, or anomalous organization detected; residue FULLY EXPLAINED by documented structural models; internal investigation EXHAUSTED (SID-03) |
| 208 | Residue tokens statistically compatible with non-encoding human-state dynamics: extreme clustering (z=127), section-conditioned (z=27), hazard-avoidant (z=5.8), geometric run-lengths (CV=0.87); no encoding required; boundary asymmetry and synthetic model fit fail; interpretive closure justified (SID-04) |
| 209 | Non-executive residue best explained as attentional pacing (Model A wins 6/8 tests vs place-keeping and mechanical): variability suppression near hazards (z=22), position independence (r=0.017), boundary reset (17.6% vs 0%), morphological simplification (d=0.33), no mechanical baseline reproduces full signature; residue layer interpretively CLOSED (SID-05) |
| 210 | External alignment signals robust to human-track removal: filtering 14.2% tokens (human-track layer) changes 1/6 key metrics >25%; hazard density, LINK density, phase-ordering ratio, LINK-hazard proximity, safety margin all remain statistically similar; prior external alignments (EXT-1 to EXT-7) were grammar-driven, not human-behavior artifacts (EXT-FILTER-01) |
| 211 | Illustration seasonal ordering test UNDERPOWERED: 77% of botanical folios classify as SUMMER (aromatic flowers + leaf herbs); 0/3 ordering tests significant; seasonal organization hypothesis neither confirmed nor refuted; class imbalance from aromatic dominance (PIAA 86.7%) collapses seasonal variation (EXT-SEQ-01) |
| 212 | Speculative plant IDs (Tier 4): 30 plants identified based on morphology + historical availability; 93% peak May-August; 0/3 ordering tests significant even at monthly resolution; clustering LESS than random (d=-1.23); botanical section documents peak-season aromatics without calendar organization; f38r = Iris/Orris (VERY HIGH confidence) (EXT-SEQ-01B) |
| 213 | Hazard topology consistent with opportunity-loss model (Tier 3): premature action hazards dominate (64.7% vs 0% late); mean LINK 37.6% (wait dominance); restart rate 3.6% (binary penalty); aggressive programs show no speed advantage (margin -0.158, speed +0.003); hazards encode "mistimed action loses value" not "system becomes unstable"; 6 tests, OPPORTUNITY_LOSS_DOMINANT HIGH confidence (EXT-ECO-01) |
| 214 | EXT-4 duration criterion INVALIDATED: SID-05 attentional pacing (hours of active monitoring) + EXT-ECO-01 opportunity-loss (patience-based, not calendar-based) contradict weeks/months assumption; botanical materials (aromatic waters, essential oils, resins) RECONSIDERED; both mineral AND botanical interpretations now viable; internal analysis cannot distinguish (EXT-4 REVISION) |
| 215 | Material domain discrimination: BOTANICAL_FAVORED (HIGH confidence); 8/8 tests favor aromatic-botanical over alchemical-mineral (score 6.24 vs 2.63, ratio 2.37); HIGH-confidence tests: illustration 86.7% perfumery-aligned (alchemical expects apparatus/symbols), hazards encode opportunity-loss not mortal danger (mercury kills, rose water doesn't), duration=hours (SID-05); 83 programs = diverse product space (botanical); 80.7% section exclusivity = different materials; aromatic interpretation FAVORED; alchemical interpretation NOT excluded (EXT-MAT-01) |
| 216 | Hybrid hazard model SUPPORTED (MODERATE confidence): 3/5 tests distinguish apparatus-focused hazards (CONTAINMENT_TIMING + ENERGY_OVERSHOOT = 29%) from batch-focused hazards (71%); apparatus hazard tokens have ZERO LINK nearby (vs 1.229 for batch) = faster response, no waiting; apparatus hazards have higher severity (0.8 vs 0.733, d=0.71) and rarer occurrence (5% vs 11.3%); ~71% batch-focused (opportunity-loss), ~29% apparatus-focused (equipment protection); accounts for EXT-ECO-01 Test F ambiguity (EXT-ECO-02) |
| 217 | Human-track tokens COMPLETELY AVOID hazard zones: 0 true HT tokens found near 17,984 hazard positions vs 4,510 HT tokens near 1,000 random positions; SID-05 "variability suppression near hazards (z=22)" reinterpreted as ABSENCE not suppression; operators don't write simpler marks near hazards, they write NOTHING; strongly confirms attentional pacing model (attention demanded = scribbling stops entirely); earlier "sparse HT" findings were artifacts (hazard tokens near each other in forbidden pairs) (EXT-ECO-02) |
| 218 | Hygiene audit of SID-04: core findings ROBUST or STRONGER with strict token filtering; clustering z-score INCREASED (257→469, +82%); section exclusivity STABLE (82.8%→83.3%); hazard avoidance INCREASED (5.93→6.38 mean distance); run length CV CHANGED (1.06→0.54) - "geometric/memoryless" interpretation refined to "consistent run lengths"; noise was WEAKENING signals not creating false positives; ~3,200 artifacts removed (19% of residue); SID-04 conclusions validated (HYGIENE-01) |
| 219 | Hygiene audit of HTCS: coordinate semantics findings ROBUST with strict token filtering; max change 2.1%; HT token count 3360→3343 (-0.5%); section-early 282→276 (-2.1%); section-late 244→244 (0%); run-forming 79→73 (-7.6%); all coordinate function classifications stable; HTCS conclusions validated (HYGIENE-02) |
| 220 | Hygiene audit of MCS: section exclusivity finding STABLE with strict token filtering; KEY METRIC UNCHANGED (83.5%→83.3% = -0.2pp); uncategorized types reduced 3727→3352 (-10.1%) by filtering artifacts: 2617 single-char, 759 non-alpha, 1315 hazard tokens; core 80.7% section-exclusive claim VALIDATED; noise tokens were cross-section (less exclusive) so true exclusivity may be slightly higher (HYGIENE-03) |
| 221 | Human-track tokens show PRACTICE-LEANING patterns (Tier 4, LOW-MODERATE confidence): 4/5 tests favor handwriting practice over doodling; rare grapheme over-representation 3.29x (p=0.0001); run CV=0.43 matches fixed-block rehearsal (not memoryless); 28.5% boundary-pushing forms; section-level family rotation (change rate 0.71); compatible with SID-05 attentional pacing (purposeful practice during waiting phases); does NOT imply encoding, semantics, or execution relevance (EXT-HF-01) |
| 222 | Human-track tokens show NO intentional layout function (Tier 4): 5 layout tests yield mixed results; HT-present lines have HIGHER variance (CV 0.884 vs 0.482, p<0.0001) - HT tokens cluster in variable regions; HT-present folios have LESS uniform fill (r=+0.224, p=0.0007); BUT counterfactual removal INCREASES irregularity (+3% CV, 95% CI [0.01, 0.03]); interpretation: HT tokens appear in layout-variable regions and partially compensate but do not achieve uniformity; consistent with opportunity-based placement (EXT-HF-02) |
| 223 | Procedural fluency confirmatory tests return MIXED results (Tier 4, LOW confidence): 2/5 practice-leaning (coverage efficiency HT 0.124 vs Exec 0.052 per token = 2.38x; rare bigram 5.75x over-representation), 2/5 doodling-leaning (run diversity z=-86.2; adjacent repetition 17.1% vs 0.2% baseline), 1/5 confirmed (100% alphabet fidelity); neither confirms nor refutes practice hypothesis; apparent contradiction reconcilable as exploration+drilling behavior; 5.75x rare bigram over-representation is strongest discriminating signal for practice (EXT-HF-03) |

### Currier A Disjunction (Constraints 224-232) — Phases CAud, CAud-G

| # | Constraint |
|---|------------|
| 224 | Currier A grammar coverage = 13.6% (threshold 70%); 49-class grammar does NOT generalize to A; A vocabulary 66.8% novel (CAud) |
| 225 | Currier A transition validity = 2.1% (threshold 60%); 100% of A folios have <50% validity; A sequences are invalid under B grammar (CAud) |
| 226 | Currier A has 5 forbidden transition violations (B has 0); hazard topology is NOT universal; A operates under different rules (CAud) |
| 227 | Currier A LINK density = 3.0% (B = 6.6%); 0.45x ratio; A shows less waiting behavior (CAud) |
| 228 | Currier A structural density = 0.35x B; 100 vs 283 tokens/folio; A is sparse/label-like (CAud) |
| 229 | Currier A classification = DISJOINT; A is a separate system from B, not executable under frozen grammar (CAud) |
| 230 | Currier A grammar derivation: silhouette = 0.049 (threshold 0.15); A does NOT exhibit grammatical structure in B sense; only 3 weak classes vs B's strong clustering (CAud-G) |
| 231 | Currier A is REGULAR but NOT GRAMMATICAL: low TTR (0.137) indicates vocabulary regularity; low silhouette (0.049) indicates no transition-based structure; A is categorical/labeling system, not procedural grammar (CAud-G) |
| 232 | Currier A section-conditioned but class-uniform: Class 1 dominates all sections (85-87%); no section-specific grammatical variation; A vocabulary overlap with B = 28.9% (CAud-G) |

### Currier A Schema Architecture (Constraints 233-240) — Phase CAS

| # | Constraint |
|---|------------|
| 233 | Currier A atomicity = LINE_ATOMIC; each line is an atomic unit (record); median 3 tokens/line; cross-line MI = 0 (CAS-1) |
| 234 | Currier A positional structure = POSITION_FREE; JS divergence = 0.0 between positions; no slot/field constraints; tokens appear freely within entries (CAS-2) |
| 235 | Currier A marker taxonomy: 8+ mutually exclusive prefix categories (ch, qo, sh, da, ok, ot, ct, ol); co-occurrence matrix = ALL ZEROS; vocabulary overlap between markers = 0 (CAS-3) |
| 236 | Currier A marker structure = FLAT (not hierarchical); zero subsumption relationships; markers are classification peers (CAS-3) |
| 237 | Currier A is DATABASE_LIKE: TTR=0.137, 70.7% bigram reuse, 58.5% pattern concentration; top patterns are repetitions ("daiin daiin" 1651x) (CAS-5) |
| 238 | Currier A section binding: same 10 markers in all sections; 78.7% section-exclusive vocabulary; global classification schema with local instantiation (CAS-4) |
| 239 | Currier A/B separation = DESIGNED: 25/112,733 cross-transitions (0.0%); Jaccard vocabulary overlap 0.141; P=100% A, B/C/S=100% B; hard boundaries at section level (CAS-6) |
| 240 | Currier A formal type: NON_SEQUENTIAL_CATEGORICAL_REGISTRY; flat tagging system; classification/catalog structure; human-queryable, NOT executable (CAS) |

### Shared Structural Primitives (Constraints 241-244) — Phase CAS Deep Structure

| # | Constraint |
|---|------------|
| 241 | CORE_CONTROL tokens (`daiin`, `ol`) show opposite system affinities: `daiin` is A-enriched (1.55x), `ol` is B-enriched (0.21x); the control pair is broken in A (CAS-DS) |
| 242 | `daiin` neighborhood flip: in A surrounded by content words (`chol`, `shol`, `chor`); in B surrounded by grammar particles (`chedy`, `ol`, `qoky`); role determined by embedding system (CAS-DS) |
| 243 | `daiin` and `ol` form adjacent pair in B (54 occurrences) but rarely in A (27 occurrences); execution control pairing absent in A's flat schema (CAS-DS) |
| 244 | Structural primitive reuse: certain tokens function as reusable structural components whose role is determined by the formal system in which they are embedded; `daiin` serves as execution control boundary in B, record articulation point in A; demonstrates deliberate infrastructure reuse without semantic transfer (CAS-DS) |

### Structural Primitive Vocabulary (Constraints 245-249) — Phase SP

| # | Constraint |
|---|------------|
| 245 | Structural primitive vocabulary is MINIMAL: exactly 2 tokens (daiin, ol), both CORE_CONTROL class; no additional structural primitives exist (SP) |
| 246 | Structural primitive test suite: 4 mandatory criteria (cross-system appearance, role inversion, high frequency, constrained adjacency); all 4 required for classification (SP) |
| 247 | SP-01 (daiin): A-enriched (1.55x), execution boundary in B, record articulator in A; affects 30.2% of A entries, 16.5% of B lines (SP) |
| 248 | SP-02 (ol): B-enriched (0.21x), control counterpart in B, marginal in A; functionally tied to sequential execution; affects 7.4% of A entries, 17.7% of B lines (SP) |
| 249 | Structural primitive scan COMPLETE: 11 candidates tested (daiin, ol, aiin, saiin, dol, dy, or, dar, dal, chol, s); only CORE_CONTROL tokens qualify; scan closed (SP) |

### Illustration Independence (Constraints 137-140)

| # | Constraint |
|---|------------|
| 137 | Swap invariance confirmed (p=1.0) |
| 138 | Illustrations do not constrain execution |
| 139 | Grammar recovered from text-only data |
| 140 | Illustrations are epiphenomenal |

### Family Structure (Constraints 126-129, 141-144)

| # | Constraint |
|---|------------|
| 126 | 0 contradictions across 8 families |
| 129 | Family differences = coverage artifacts |
| 141 | Cross-family syntax transplant = ZERO degradation |
| 144 | Process families are emergent regularities (observer-imposed) |

---

## Explicitly Falsified Hypotheses — TIER 1

These claims have been tested and rejected. They should NOT be revisited without new external evidence.

| Hypothesis | Test | Result |
|------------|------|--------|
| PLANT-PROCESS-BODY patterns | Randomization | 0/4 passed = ARTIFACT |
| Zodiac pages have phonetic labels | Control comparison | Control scored equal/higher |
| Text matches medical recipe structure | Structure alignment | Best fit only 37-50% |
| Hub functional roles have visual meaning | Replication | p=0.43 (original was fluke) |
| Visual-text correlation at any offset | Exhaustive search | 0/58,075 tests significant |
| Prefixes encode plant-part material selection | BF-PFX-Omega | 75.2% partitions significant (non-specific) |
| Sections encode apparatus configurations | F-ratio test | F=0.37 (threshold 2.0) |
| Prefix/suffix resolve operational problems | Necessity test | 1/4 problems resolved |
| Program behavior correlates with plant morphology | Chi-square, Fisher's, permutation | All p>>0.05, OR=1.0 |
| **OPS-R 2-cycle reconciliation** | SEL-B consistency audit | **FAILED** — MONOSTATE vs 2-cycle = contradiction |
| Hazard "100% bidirectional" | SEL-D bidirectionality test | **FALSIFIED** — 65% asymmetric (11/17 have reverse) |
| Hazard "KERNEL_ADJACENT clustering" | SEL-D kernel-dependence test | **FALSIFIED** — 59% distant from kernel |
| Human-track "7 coordinate functions" | SEL-E parsimony test | **REMOVED** — overfitting (circular inference) |
| Human-track "navigation function" | SEL-E necessity test | **REMOVED** — analyst-imposed, no structural necessity |
| **49-class grammar generalizes to manuscript** | CAud 8-track audit | **FALSIFIED** — 13.6% coverage in Currier A (threshold 70%); A is DISJOINT |
| **Hazard topology is universal** | CAud Track 3 | **FALSIFIED** — 5 forbidden transitions occur in Currier A (B has 0) |

---

## Adversarial Audit Summary — TIER 1

| Attack | Target | Result |
|--------|--------|--------|
| Kernel Collapse | Frequency artifact? | **SURVIVES** |
| Cycle Illusion | Segmentation artifact? | **WEAKENED** |
| Grammar Minimality | Overfit? | **WEAKENED** |
| Random Baseline | Generic behavior? | **SURVIVES** |
| Folio Independence | Redundant samples? | **SURVIVES** |
| Grammar Collapse | Incompatible family grammars? | **SURVIVES** |
| DSL Discriminator | Language encoding possible? | **SURVIVES** |
| Family Syntax Significance | Families structurally necessary? | **SURVIVES** |

**Overall: 6/8 attacks failed to falsify model.**

---

## Historical Phase Summary — TIER 2

| Phase | Finding | Status |
|-------|---------|--------|
| 7 | Formal semantic model | 95.1% parse coverage |
| 9-11 | Domain discrimination | Pharmacology 0/3, Alchemy 2/3 |
| 12 | Tradition fingerprinting | T3 PRIVATE SCHOOL |
| 13-14 | Executability | MONOSTATE, 100% convergence |
| 15 | Hub core structure | 10 primitives, k/h/e core |
| 16 | Process alignment | REFLUX DISTILLATION (86%) |
| 17 | Kernel semantics | Three-point control |
| 18 | Hazard topology | 5 failure classes |
| 19 | Identifier detection | PURE_OPERATIONAL |
| 20 | Normalization | 49 classes, ASYMPTOTE REACHED |
| 21-22 | Enumeration | 83 folios, 75,248 instructions |
| 23 | Regime boundaries | f57r = RESTART_PROTOCOL |
| X | Adversarial audit | 3/5 survived, 2 weakened |
| X.2 | Grammar collapse | SURVIVES, MODEL FROZEN |
| X.5 | DSL discriminator | Language hypothesis REJECTED |
| CCF | Circular folios | VISUAL_BUNDLING |
| ILL | Illustration independence | EPIPHENOMENAL |
| FSS | Family syntax | EMERGENT (not structural) |
| CSM/CST | Control signature matching | Circulatory reflux confirmed |
| HCG | Historical comparison | 8/8 Brunschwig match |
| PMS | Prefix material selection | FALSIFIED |
| PCS/CGR | Coordinate system | PIECEWISE_SEQUENTIAL |
| ARE | Apparatus reverse engineering | INCONCLUSIVE (2/5) |
| HFM | Human factors & manual design | 8/8 Brunschwig pattern match |
| PPA | Physics plausibility audit | 7/7 PASS, PHYSICALLY PLAUSIBLE |
| L1L2 | Forward experimental inference | COHERENT (Lane 1 + Lane 2 PASS) |
| L3 | Material-class compatibility | PASS (4/5 compatible, 1 incompatible) |
| L4/OptA | Geometry compatibility | PASS (closed-loop selective, d=4.50) |
| EPM | Exploratory process mapping | SPECULATIVE (2 STRONG, 4 MODERATE, 1 WEAK alignment) |
| APF | Adversarial process family comparison | PF-C fits better (0.81 vs 0.47), neither decisive |
| HTO | Human-track ordering analysis | PARTIALLY_STRUCTURED (2/5), local buffering significant |
| CDCE | Cross-domain comparative engineering | HIGH alignment: reflux/conditioning; 7 domains INCOMPATIBLE |
| SRP | Speculative reconstruction | Aromatic waters MEDIUM-HIGH; 3 products plausible, 3 ruled out |
| PIA | Product isolation analysis | Aromatic Waters 90.5% convergence; multi-product workshop |
| PIAA | Plant illustration alignment | 86.7% perfumery-aligned; reinforces aromatic waters hypothesis |
| PPC | Program-plant correlation | NO correlation (all p>>0.05); programs independent of morphology |
| FMR | Failure-mode reconstruction | 5 hazard classes mapped to craft failures; author psychology inferred |
| UTC | Uncategorized token characterization | Human-track, section-local, 9.1% overlap, non-executable |
| MCS | Manuscript coordinate system | Section-level (80.7% exclusive); line/quire hypotheses FALSIFIED |
| NESS | Non-executable symbol systems | Single unified layer; no additional systems detected |
| PCI | Purpose class inference | Single viable class: continuous closed-loop process control |
| HTCS | Coordinate semantics | 7 functions identified; 99.6% LINK-proximal (waiting-phase navigation) |
| SSI | Speculative semantics | 8-item vocabulary proposed; LOW-MODERATE confidence (explicitly speculative) |
| HOT | Ordinal hierarchy test | FALSIFIED (2/5 tests); tokens are positional, NOT stress-level indicators |
| HLL-2 | Language-likeness test | FALSIFIED (2/5 tests); linguistic hypothesis space EXHAUSTED |
| OLF | Olfactory-craft meaning reconstruction | SPECULATIVE (5/5 tests plausible); perfumery interpretation coherent |
| IMD | Intra-role micro-differentiation | SPECULATIVE (CF-1/CF-2 STRONG_SIGNAL); craft memory encoded at micro level |
| PCISO | Process-class isomorphism | SPECULATIVE (3 survive: reflux, aromatic extraction, conditioning); 7 eliminated by D criterion |
| PSP | Product-space plausibility | SPECULATIVE (5 product families survive: waters, oils, resins, digested, stabilized); 4 eliminated by A criterion |
| PCC | Product-class convergence | SPECULATIVE (both classes survive; extraction favored 5/5 vs 3/5; no decisive elimination) |
| PCIP | Plant-context intersection | SPECULATIVE (no new constraint; all plant types historically dual-use; criterion #3 fails) |
| OPS-1 | Folio-level control signature extraction | 83 folios, 33 metrics extracted; purely operational |
| OPS-2 | Control strategy clustering | 4 stable regimes (K-Means k=4, ARI=0.881); aggressive folios cluster non-randomly |
| OPS-3 | Risk-time-stability tradeoff mapping | 3/4 regimes Pareto-efficient; REGIME_3 dominated; cross-checks PASS |
| OPS-4 | Operator decision & switching model | 9 transition pathways; 3 prohibited; REGIME_3 = transient throughput state; cross-checks PASS |
| OPS-5 | Control Engagement Intensity (CEI) manifold | CEI formalized; 4 bands (R2<R1<R4<R3); bidirectional dynamics; LINK-CEI r=-0.71; internal investigation closed |
| OPS-6 | Codex Structure Analysis | PARTIAL organization: CEI smoothing SUPPORTED (d=1.89), restart placement SUPPORTED (d=2.24), navigation REJECTED (d=-7.33); local smoothing present, global navigation suboptimal |
| OPS-6.A | Human-Track Navigation Compensation | Human-track compensation NOT detected (T1-T3 all negative effects); 100% match to EXPERT_REFERENCE archetype; design assumes experts who know the process |
| OPS-7 | Operator Doctrine Consolidation | OPS CLOSED; 5 principles (waiting default, escalation irreversible, restart low-CEI, position not escape, throughput transient); 0 contradictions across OPS-1 through OPS-6.A |
| EXT-1 | External Procedure Isomorphism | CANDIDATE HARVEST; 6 procedure classes survive (4 full trap-tolerance, 2 partial); 18 eliminated; common signature = closed-loop circulatory expert operation |
| EXT-2 | Historical Process Matching | PROCESS IDENTIFICATION; 28 named historical processes mapped (25 confirmed Tier 2, 2 marginal Tier 3, 1 textual Tier 4); all 6 EXT-1 classes have real historical instantiation |
| EXT-3 | Failure & Hazard Alignment | ELIMINATION; 4/8 processes eliminated (50%); survivors: Circulatio (Tier 2), Cohobatio (Tier 2), Athanor (Tier 3), Quintessence (Tier 3); eliminated: Balneum Mariae, Fimus Equinus, Hydrodistillation, Aqua Vitae Simplex |
| EXT-4 | Material & Botanical Correlation | **PARTIALLY REVISED**; original elimination (100% botanical) invalidated by SID-05 duration reinterpretation; botanical materials RECONSIDERED; both mineral (mercury, antimony, gold) AND botanical (aromatic waters, essential oils) now survive; see EXT4_REVISION_NOTICE.md |
| EXT-5A | Role Classification (Terminal Gate) | CONTINUE JUSTIFIED; 6 survivors classified: 2 Final Products (actually consumed), 3 Platform Reagents, 1 Functional Intermediate; heterogeneous role distribution; product identification phases remain justified |
| EXT-5B | Use-Context Mapping | CONTINUE JUSTIFIED; all 6 survivors absorbed into guild-restricted, court-sponsored, expert-operated alchemical-medical ecosystem; preparation/use decoupled; Voynich encodes preparation NOT application; historical narrowing (region, guild, lineage) justified |
| EXT-6 | Institutional Compatibility Audit | CONVERGENCE (Tier 3-4); goldsmith/assayer workshops (Central Europe 1400-1550, N. Italy 1400-1470) survive all constraints; university-adjacent ELIMINATED (C4 violation); N. Italy apothecary-adjacent ELIMINATED (C3, C4 violations); Iberia UNDERDETERMINED |
| EXT-7 | Structural Parallel Corpus Search | PARTIAL PARALLELS; quintessence tradition (Rupescissa) = closest match (7.0/10); Pseudo-Geber = 6.5/10; Voynich STRUCTURALLY EXCEPTIONAL (exceeds all comparands on abstraction); null class (recipe books, cookbooks) FAILS on 5/10 features; Voynich = extreme endpoint of operational alchemy continuum |
| OPS-R | Abstraction Layer Reconciliation | **FAILED** (SEL-B); MONOSTATE vs 2-cycle oscillation = CONTRADICTION; LINK non-intervention vs oscillation participation = CONTRADICTION; convergence pillar DESTABILIZED; NON-AUTHORITATIVE |
| SEL-A | Claim Inventory | 28 claims inventoried; OPS claims organized by pillar |
| SEL-B | Consistency Audit | OPS-R FAILED (2 formal contradictions); OPS-1 through OPS-7 PASS; convergence/LINK pillars DESTABILIZED |
| SEL-C | Circularity Audit | 3/28 claims circular; all non-critical; no foundational circularity detected |
| SEL-D | Hazard Topology Audit | Hazard COUNT survives (17 transitions); hazard CHARACTERIZATION downgraded (bidirectional 65%, kernel-adjacent 59%); CONTAINMENT_TIMING theoretical-only |
| SEL-E | Human-Track Audit | Only 2/12 claims survive (zero-seam, hazard-avoidance); "7 coordinate functions" REMOVED (overfitting); "navigation function" REMOVED (analyst-imposed); layer downgraded Tier 2→Tier 3 |
| SID-01 | Global Residue Convergence Test | PARTIAL CONVERGENCE; 82% section exclusivity NOT emergent from any global generative process; section-conditioned models required; residue is human-designed coordinate system |
| SID-01.1 | Section Regime Clustering Test | WEAK STRUCTURE ONLY; 8 sections cluster into k=2 regimes (silhouette=0.292); compression effective but not reliable; section identity remains irreducible conditioning variable |
| SID-03 | Micro-Cipher Stress Test | NO ADDITIONAL STRUCTURE; 18 subsets tested across 5 sampling strategies; 0/18 passed all 4 formal tests; Test A (equivalence classes) and Test C (compression) universally failed; no hidden cipher layers, no anomalous organization; internal investigation EXHAUSTED |
| SID-04 | Human-State Compatibility | COMPATIBLE (4/6 tests); residue tokens compatible with non-encoding human-state dynamics; extreme clustering (z=127), section exclusivity (z=27), hazard avoidance (z=5.8), geometric runs (CV=0.87); no encoding REQUIRED |
| SID-05 | Attentional Pacing Discrimination | MODEL A WINS (6/8 tests); attentional pacing beats place-keeping and mechanical noise; variability suppresses near hazards (z=22), position-independent, boundary reset, simpler morphology near hazards; RESIDUE LAYER CLOSED |
| EXT-FILTER-01 | External Alignment Conditioning | ALIGNMENT_UNCHANGED; 14.2% human-track tokens removed; 1/6 key metrics changed >25%; prior external alignments (EXT-1 to EXT-7) were grammar-driven, not human-behavior artifacts; hygiene pass complete |
| EXT-SEQ-01 | Illustration Seasonal Ordering | NO_ORDERING_SIGNAL; 0/3 tests significant; test underpowered due to class imbalance (77% SUMMER from aromatic dominance); seasonal ordering hypothesis neither confirmed nor refuted |
| EXT-SEQ-01B | Speculative Plant ID + Fine Seasonal | NO_ORDERING_SIGNAL (Tier 4 SPECULATIVE); 30 plants speculatively identified; 93% peak May-August; 0/3 tests significant even with monthly resolution; clustering LESS than random (d=-1.23); documents peak-season aromatics without calendar organization |
| EXT-ECO-01 | Opportunity-Loss Hazard Profile | OPPORTUNITY_LOSS_DOMINANT (HIGH confidence); premature action hazards 64.7% (vs 0% late); mean LINK 37.6%; restart rate 3.6% (binary penalty); aggressive programs show no speed advantage (margin -0.158, speed +0.003); hazards encode "mistimed action loses value" not "system becomes unstable" (Tier 3) |
| EXT-MAT-01 | Material Domain Discrimination | BOTANICAL_FAVORED (HIGH confidence); 8/8 tests favor botanical over alchemical-mineral (score ratio 2.37); HIGH-confidence tests: illustration 86.7% perfumery-aligned, hazards encode opportunity-loss not mortal danger, duration=hours (SID-05); EXT-4 botanical elimination INVALIDATED; aromatic interpretation RESTORED (Tier 3) |
| EXT-ECO-02 | Hazard Class Discrimination | HYBRID_SUPPORTED (MODERATE confidence); 3/5 tests distinguish apparatus-focused hazards (CONTAINMENT_TIMING, ENERGY_OVERSHOOT = 29%) from batch-focused (71%); KEY FINDINGS: (1) apparatus hazard tokens have ZERO LINK nearby (vs 1.229 for batch) = faster response needed; (2) human-track tokens COMPLETELY AVOID all hazard zones (0 true HT near 17,984 hazards vs 4,510 near random) - SID-05 "suppression" reinterpreted as ABSENCE; apparatus hazards have higher severity (0.8 vs 0.733) and rarer occurrence; hybrid model accounts for Test F ambiguity in EXT-ECO-01 (Tier 3) |
| HYGIENE-01 | SID-04 Token Filtering Audit | ROBUST; reran SID-04 with strict filtering (excluding <2 chars, non-alpha, hazard tokens); core findings STABLE or STRONGER: clustering +82%, exclusivity +0.6%, hazard distance +7.6%; run length CV changed -49% (1.06→0.54) - refined from "memoryless" to "consistent"; noise was WEAKENING signals not creating false positives; validates SID-04 methodology |
| HYGIENE-02 | HTCS Coordinate Semantics Audit | ROBUST; reran HTCS with strict filtering; max change 2.1%; all coordinate function counts stable: section-early 282→276 (-2.1%), section-late 244→244 (0%), run-forming 79→73 (-7.6%); HT token count 3360→3343 (-0.5%); validates HTCS methodology |
| HYGIENE-03 | MCS Section Exclusivity Audit | MOSTLY STABLE; reran MCS with strict filtering; KEY FINDING UNCHANGED: section exclusivity rate 83.5%→83.3% (-0.2pp); uncategorized types reduced 3727→3352 (-10.1%) by filtering short/non-alpha/hazard tokens; filtered: 2617 single-char, 759 non-alpha, 1315 hazard tokens; core 80.7% exclusivity claim VALIDATED |
| EXT-HF-01 | Attentional Doodling vs Practice | PRACTICE-LEANING (Tier 4, LOW-MODERATE confidence); 4/5 tests favor handwriting practice over doodling; rare grapheme over-representation 3.29x (p=0.0001); run CV=0.43 (fixed-block rehearsal); 28.5% boundary-pushing forms; family rotation 0.71; refines SID-05: writing during waiting phases was purposeful practice, not purely automatic; does NOT imply encoding/semantics/execution |
| EXT-HF-02 | Visual Layout Stabilization | NO_INTENTIONAL_LAYOUT_FUNCTION (Tier 4); 5 layout tests yield 1 support, 2 counter, 1 null, 1 exploratory; HT-present lines have HIGHER variance (CV 0.884 vs 0.482); HT removal INCREASES irregularity (+3% CV); HT tokens cluster in layout-variable regions and partially compensate; consistent with opportunity-based placement, not intentional design |
| EXT-HF-03 | Procedural Fluency Reinforcement | MIXED (Tier 4, LOW confidence); 5 confirmatory tests yield 2 practice-leaning (coverage efficiency 2.38x, rare bigram 5.75x), 2 doodling-leaning (run diversity z=-86.2, repetition 17.1%), 1 confirmed (alphabet fidelity 100%); apparent contradiction reconcilable as exploration+drilling; practice hypothesis neither confirmed nor refuted; strongest signal: 5.75x rare bigram over-representation |
| CAud | Currier A Executability Boundary | **DISJOINT** (Tier 0 STRUCTURAL); 8-track audit: grammar coverage 13.6% (FAIL), transition validity 2.1% (FAIL), 5 hazard violations (FAIL), 86.4% execution stall; 49-class grammar applies to Currier B ONLY; Currier A is a separate system; FALSIFIES generalization claim |
| CAud-G | Currier A Grammar Derivation | **A_LACKS_GRAMMAR** (Tier 0 STRUCTURAL); silhouette=0.049 (threshold 0.15); only 3 weak classes (one dominates 72.5%); A is REGULAR (TTR 0.137) but NOT GRAMMATICAL (no transition structure); categorical/labeling system, not procedural grammar; 28.9% vocabulary overlap with B |
| CAS | Currier A Schema Investigation | **NON_SEQUENTIAL_CATEGORICAL_REGISTRY** (Tier 2 STRUCTURAL); 6-phase schema analysis: LINE_ATOMIC entries, POSITION_FREE tokens, 8+ mutually exclusive marker categories (co-occurrence=0, vocabulary overlap=0), FLAT hierarchy, DATABASE_LIKE (TTR=0.137, 70.7% bigram reuse), DESIGNED_SEPARATION from B (0.0% cross-transitions); A is a flat tagging/classification system, not a grammar |
| CAS-DS | Currier A Deep Structure (Structural Primitives) | **INFRASTRUCTURE_REUSE** (Tier 2 STRUCTURAL); CORE_CONTROL tokens (`daiin`, `ol`) show opposite affinities (daiin A-enriched 1.55x, ol B-enriched 0.21x); neighborhood flip (daiin surrounded by content in A, grammar in B); control pairing broken in A (54→27 adjacent occurrences); tokens function as reusable structural components whose role is system-determined; demonstrates deliberate infrastructure reuse without semantic transfer |
| SP | Structural Primitive Discovery | **MINIMAL_VOCABULARY** (Tier 2 STRUCTURAL); 4-phase systematic scan (candidate extraction, role polarity, removal tests, minimal vocabulary); 11 candidates tested; only 2 tokens qualify (daiin, ol = CORE_CONTROL); structural primitive test suite: cross-system appearance, role inversion, high frequency, constrained adjacency; no additional structural primitives exist; scan CLOSED |

---

## Project Structure — TIER 2

```
voynich/
├── CLAUDE.md                              # This file (main documentation)
├── README.md                              # Public-facing project summary
├── ORGANIZATION.md                        # Directory structure guide
├── limits_statement.md                    # Epistemological boundaries
├── assumption_boundary.md                 # What physics audit does NOT prove
├── overall_verdict.md                     # Final judgment
├── validated_structural_findings.md       # 175 constraints list
│
├── phases/                                # All analysis phases
│   ├── 01-09_early_hypothesis/            # Initial model building
│   ├── 10-14_domain_characterization/     # Domain discrimination
│   ├── 15-20_kernel_grammar/              # Kernel and grammar discovery
│   ├── 21-23_enumeration/                 # Full enumeration
│   ├── X_adversarial_audit/               # Falsification tests
│   ├── CCF_circular_folios/               # Circular folio analysis
│   ├── ILL_illustration_independence/     # Illustration coupling
│   ├── FSS_family_syntax/                 # Family syntax
│   ├── [... additional specialized phases]
│   ├── FMR_failure_mode_reconstruction/   # Failure mode analysis
│   ├── NESS_non_executable_systems/       # Human-track symbol systems
│   ├── PCI_purpose_class_inference/       # Purpose class convergence
│   ├── HTCS_coordinate_semantics/         # Coordinate function inference
│   ├── SSI_speculative_semantics/         # Speculative waiting-phase meanings
│   ├── HOT_ordinal_hierarchy/             # Ordinal hierarchy stress test (FALSIFIED)
│   ├── HLL2_language_likeness/            # Language-likeness test (FALSIFIED)
│   ├── PCI_process_class_isomorphism/     # Process-class isomorphism (SPECULATIVE)
│   ├── PSP_product_space_plausibility/    # Product-space plausibility (SPECULATIVE)
│   ├── PCC_product_class_convergence/     # Product-class convergence (SPECULATIVE)
│   ├── PCIP_plant_context_intersection/   # Plant-context intersection (SPECULATIVE)
│   ├── OPS1_folio_control_signatures/     # Folio-level control signatures (TIER 2)
│   ├── OPS2_control_strategy_clustering/  # Control strategy clustering (TIER 2)
│   ├── OPS3_risk_time_stability_tradeoffs/ # Risk-time-stability tradeoffs (TIER 2)
│   ├── OPS4_operator_decision_model/      # Operator decision & switching model (TIER 2)
│   ├── OPS5_control_engagement_intensity/ # Control Engagement Intensity manifold (TIER 2)
│   ├── OPS6_codex_organization/           # Codex Structure Analysis (TIER 2)
│   ├── OPS6A_human_navigation/            # Human-Track Navigation Compensation (TIER 2)
│   ├── OPS7_operator_doctrine/            # Operator Doctrine Consolidation (TIER 2) - OPS CLOSED
│   ├── OPS_R_abstraction_reconciliation/  # Abstraction Layer Reconciliation (**FAILED** - SEL-B)
│   ├── EXT1_external_procedure_isomorphism/ # External Procedure Isomorphism (External Comparative)
│   ├── EXT2_historical_process_matching/ # Historical Process Matching (External Comparative)
│   ├── EXT3_failure_hazard_alignment/ # Failure & Hazard Alignment (External Comparative)
│   ├── EXT4_material_botanical_correlation/ # Material & Botanical Correlation (External Comparative)
│   ├── EXT5A_role_classification/ # Role Classification Terminal Gate (External Comparative)
│   ├── EXT5B_use_context_mapping/ # Bounded Use-Context Mapping (External Comparative)
│   ├── EXT6_institutional_compatibility/ # Institutional Compatibility Audit (External Comparative)
│   ├── EXT7_structural_parallel_search/ # Structural Parallel Corpus Search (External Comparative)
│   ├── SEL_A_claim_inventory/            # SEL Audit: Claim Inventory, Consistency, Hazard & Human-Track Tests
│   ├── SID01_global_residue_convergence/ # SID-01: Residue generative convergence test (PARTIAL CONVERGENCE)
│   ├── SID03_micro_cipher_stress_test/   # SID-03: Micro-cipher stress test (NO SIGNAL - INTERNAL EXHAUSTED)
│   ├── SID04_human_state_compatibility/  # SID-04: Human-state compatibility (COMPATIBLE 4/6)
│   ├── SID05_attentional_discrimination/ # SID-05: Attentional pacing discrimination (MODEL A WINS 6/8) - RESIDUE CLOSED
│   ├── EXT_FILTER_01_alignment_conditioning/ # EXT-FILTER-01: External alignment conditioning (ALIGNMENT_UNCHANGED)
│   ├── EXT_SEQ_01_seasonal_ordering/ # EXT-SEQ-01: Illustration seasonal ordering (NO_ORDERING_SIGNAL)
│   ├── EXT_ECO_01_opportunity_loss_profile/ # EXT-ECO-01: Opportunity-Loss Hazard Profile (OPPORTUNITY_LOSS_DOMINANT)
│   ├── EXT_MAT_01_material_discrimination/ # EXT-MAT-01: Material Domain Discrimination (BOTANICAL_FAVORED)
│   ├── EXT_ECO_02_hazard_class_discrimination/ # EXT-ECO-02: Hazard Class Discrimination (HYBRID_SUPPORTED)
│   ├── EXT_HF_01_attentional_doodling/       # EXT-HF-01: Attentional Doodling vs Practice (PRACTICE-LEANING, Tier 4)
│   ├── EXT_HF_02_visual_layout/              # EXT-HF-02: Visual Layout Stabilization (NO_INTENTIONAL_LAYOUT_FUNCTION, Tier 4)
│   ├── EXT_HF_03_procedural_fluency/         # EXT-HF-03: Procedural Fluency Reinforcement (MIXED, Tier 4)
│   ├── CAud_currier_a_audit/                 # CAud: Currier A Executability Boundary (DISJOINT - FALSIFIES GENERALIZATION)
│   └── SP_structural_primitives/             # SP: Structural Primitive Discovery (MINIMAL_VOCABULARY - scan CLOSED)
│
├── legacy/                                # Falsified hypotheses (preserved)
│   ├── translation_attempts/
│   ├── dictionary_building/
│   └── semantic_analysis/
│
├── lib/                                   # Reusable code libraries
│   ├── analysis/                          # Analysis modules
│   ├── tools/                             # Helper tools
│   └── utilities/                         # Standalone utilities
│
├── data/                                  # Input data
│   └── transcriptions/                    # EVA transcriptions
│
├── results/                               # Frozen canonical outputs
│   ├── canonical_grammar.json             # 49-class grammar
│   ├── full_recipe_atlas.txt              # 75,248 instructions
│   ├── control_signatures.json            # Kernel definitions
│   └── summary_reports/                   # High-level summaries
│
├── folio_analysis/                        # Per-folio deep dives
│   ├── hazard_maps/
│   ├── kernel_trajectories/
│   └── outlier_traces/
│
├── annotation_data/                       # Manual annotations
└── research/                              # External references
```

See `ORGANIZATION.md` for complete phase listing and file naming conventions.

Key outputs (in `results/` and phase directories):
- `results/canonical_grammar.json` — 100% coverage grammar (49 classes)
- `results/full_recipe_atlas.txt` — Complete recipe atlas (75,248 instructions)
- `results/control_signatures.json` — Kernel operator definitions
- `phases/ARE_apparatus_engineering/apparatus_reverse_engineering_report.md`
- `phases/HFM_human_factors/human_factors_summary.md`
- `phases/PPA_physics_plausibility/physics_plausibility_audit.md`
- `phases/FMR_failure_mode_reconstruction/` — Failure mode reconstruction (5 files)
- `phases/NESS_non_executable_systems/` — Non-executable symbol systems inventory
- `phases/PCI_purpose_class_inference/` — Purpose class convergence analysis
- `phases/HTCS_coordinate_semantics/` — Coordinate function inference
- `phases/SSI_speculative_semantics/` — Speculative waiting-phase meanings (non-binding)
- `phases/HOT_ordinal_hierarchy/` — Ordinal hierarchy stress test (FALSIFIED)
- `phases/HLL2_language_likeness/` — Language-likeness test (FALSIFIED)
- `phases/OLF_olfactory_craft/` — Olfactory-craft meaning reconstruction (SPECULATIVE)
- `phases/PCI_process_class_isomorphism/` — Process-class isomorphism (SPECULATIVE)
- `phases/PSP_product_space_plausibility/` — Product-space plausibility (SPECULATIVE)
- `phases/PCC_product_class_convergence/` — Product-class convergence (SPECULATIVE)
- `phases/PCIP_plant_context_intersection/` — Plant-context intersection (SPECULATIVE)
- `phases/OPS1_folio_control_signatures/` — Folio-level control signatures (TIER 2)
- `phases/OPS2_control_strategy_clustering/` — Control strategy clustering (TIER 2)
- `phases/OPS3_risk_time_stability_tradeoffs/` — Risk-time-stability tradeoffs (TIER 2)
- `phases/OPS4_operator_decision_model/` — Operator decision & switching model (TIER 2)
- `phases/OPS5_control_engagement_intensity/` — Control Engagement Intensity manifold (TIER 2)
- `phases/OPS6_codex_organization/` — Codex Structure Analysis (TIER 2)
- `phases/OPS6A_human_navigation/` — Human-Track Navigation Compensation (TIER 2)
- `phases/OPS7_operator_doctrine/` — Operator Doctrine Consolidation (TIER 2) - OPS CLOSED
- `phases/OPS_R_abstraction_reconciliation/` — Abstraction Layer Reconciliation (**FAILED** - SEL-B)
- `phases/EXT1_external_procedure_isomorphism/` — External Procedure Isomorphism (External Comparative)
- `phases/EXT2_historical_process_matching/` — Historical Process Matching (External Comparative)
- `phases/EXT3_failure_hazard_alignment/` — Failure & Hazard Alignment (External Comparative)
- `phases/EXT4_material_botanical_correlation/` — Material & Botanical Correlation (External Comparative)
- `phases/EXT5A_role_classification/` — Role Classification Terminal Gate (External Comparative)
- `phases/EXT5B_use_context_mapping/` — Bounded Use-Context Mapping (External Comparative)
- `phases/EXT6_institutional_compatibility/` — Institutional Compatibility Audit (External Comparative)
- `phases/EXT7_structural_parallel_search/` — Structural Parallel Corpus Search (External Comparative)
- `phases/SEL_A_claim_inventory/` — SEL Audit Suite (SEL-A through SEL-E: claim inventory, consistency, circularity, hazard, human-track)
- `phases/SID01_global_residue_convergence/` — Global Residue Convergence Test (PARTIAL CONVERGENCE: section exclusivity not emergent)
- `phases/SID03_micro_cipher_stress_test/` — Micro-Cipher Stress Test (NO SIGNAL: internal investigation EXHAUSTED)
- `phases/SID04_human_state_compatibility/` — Human-State Compatibility (COMPATIBLE 4/6: clustering z=127, hazard avoidance z=5.8)
- `phases/SID05_attentional_discrimination/` — Attentional Pacing Discrimination (MODEL A WINS 6/8: residue layer CLOSED)
- `phases/EXT_FILTER_01_alignment_conditioning/` — External Alignment Conditioning (ALIGNMENT_UNCHANGED: prior alignments grammar-driven)
- `phases/EXT_SEQ_01_seasonal_ordering/` — Illustration Seasonal Ordering (NO_ORDERING_SIGNAL: test underpowered by class imbalance)
- `phases/EXT_SEQ_01_seasonal_ordering/speculative_plant_data.md` — Speculative Plant IDs (Tier 4: 30 plants, 57% HIGH confidence, f38r=Iris VERY HIGH)
- `phases/EXT_ECO_01_opportunity_loss_profile/` — Opportunity-Loss Hazard Profile (OPPORTUNITY_LOSS_DOMINANT: premature hazards 64.7%, wait dominance 37.6%, binary penalty 3.6% restart)
- `phases/EXT4_material_botanical_correlation/EXT4_REVISION_NOTICE.md` — EXT-4 Revision (duration criterion invalidated; botanical materials RECONSIDERED)
- `phases/EXT_MAT_01_material_discrimination/` — Material Domain Discrimination (BOTANICAL_FAVORED: 8/8 tests, score ratio 2.37, HIGH confidence)
- `phases/EXT_ECO_02_hazard_class_discrimination/` — Hazard Class Discrimination (HYBRID_SUPPORTED: 3/5 tests, apparatus vs batch hazards distinguished)
- `phases/EXT_HF_01_attentional_doodling/` — Attentional Doodling vs Practice (PRACTICE-LEANING: 4/5 tests, Tier 4)
- `phases/EXT_HF_02_visual_layout/` — Visual Layout Stabilization (NO_INTENTIONAL_LAYOUT_FUNCTION: 1/5 support, 2/5 counter, Tier 4)
- `phases/EXT_HF_03_procedural_fluency/` — Procedural Fluency Reinforcement (MIXED: 2/5 practice, 2/5 doodling, 1/5 confirmed, Tier 4)

---

## Transcription Data Sources — TIER 2

### Canonical Source: `interlinear_full_words.txt`

- **Location:** `data/transcriptions/interlinear_full_words.txt`
- **Format:** TSV with standard EVA tokens (`shey`, `aiin`, `chol`, `qokaiin`, etc.)
- **Usage:** ALL analysis, VEE app, constraint visualization
- **Font compatibility:** Standard EVA maps directly to VoynichEVA font (a-z → glyphs)
- **Grammar match:** Tokens match `hazards.py` forbidden pairs exactly

### Reference Only: `voynich_eva.txt`

- **Location:** `data/transcriptions/voynich_eva.txt`
- **Format:** Proprietary encoding with digits (`fa19s`, `9`, `hae`, etc.)
- **Usage:** Reference only — **NOT for analysis or app**
- **Warning:** Requires font mapping; tokens do NOT match grammar

**IMPORTANT:** Always use `interlinear_full_words.txt` for any new code or analysis.

---

## Change Log (Final Documentation Freeze) — TIER 2

### What Was Removed
- Redundant explanations of executability (consolidated to Model Boundary)
- Redundant frozen conclusion statements (single canonical version retained)
- "Alchemical Interpretation" section (implied semantics removed)
- Outdated "Working Model" section with semantic layer labels
- "What Would Advance This Project" section (analysis complete)
- Detailed file listing (consolidated to structure overview)

### What Was Reclassified
- "Kernel Semantics" labels (k=ENERGY, etc.) → marked as **inferential overlays**, not proven identities
- Apparatus identification → explicitly marked as **external/non-binding**
- Prefix/suffix function → reclassified from "possibly operational" to **organizational/positional indexing**
- Section boundaries → reclassified from "possibly apparatus configurations" to **human-facing organization**

### What Was Clarified
- Added explicit "Model Boundary" section defining internal vs external vs unrecoverable
- Normalized terminology: "executable operational control grammar", "positional indexing", "piecewise-sequential"
- Preserved all falsifications in dedicated table
- Clarified that organizational layer is **intentional but not apparatus-forced**
- Clarified that variant structure is **discrete alternatives**, not continuous tuning

### What Was Preserved (Unchanged)
- All 160 validated constraints
- All explicit falsifications
- All adversarial audit results
- Historical phase summary
- Weakened claims with required clarifications

---

*MODEL FROZEN. No further structural claims. Documentation complete.*
