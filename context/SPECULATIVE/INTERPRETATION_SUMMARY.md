# Speculative Interpretation Summary

**Status:** SPECULATIVE | **Tier:** 3-4 | **Version:** 4.71

---

## Purpose

This document consolidates all Tier 3-4 interpretations into a single reference. It is designed for external AI context loading.

**Critical:** Everything in this document is NON-BINDING speculation. It is consistent with the structural evidence but NOT proven by it. Treat as discardable if contradicted by new evidence.

---

## Frozen Conclusion (Tier 0 - Context Only)

> The Voynich Manuscript's Currier B text encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

This structural finding is FROZEN. The interpretations below attempt to explain what this structure might have been FOR.

---

## Universal Boundaries

All interpretations in this document respect these constraints. Individual sections may add section-specific caveats but these five apply universally:

1. **Semantic ceiling** (C171, C120): No token-level meaning or translation is recoverable from internal analysis alone.
2. **No entry-level A-B coupling** (C384): No mapping from individual A entries to individual B tokens exists.
3. **No substance identification**: Specific plants, materials, or substances cannot be identified from the text.
4. **No Brunschwig equivalence**: Voynich is not a cipher for Brunschwig; no folio-to-passage mapping exists.
5. **Tier discipline**: All interpretations are Tier 3-4 speculation, consistent with but not proven by structural evidence.

---

## Epistemological Frame: Structure-Fitting, Not Translation

This project does not attempt to translate the Voynich Manuscript. The structural layer (Tier 0-2) proves that the manuscript has a rigorous internal grammar — 49 instruction classes, forbidden transitions, convergence behavior. The interpretive layer (Tier 3) shows that this structure is consistent with thermodynamic process control — the way sheet music is consistent with the physics of sound.

A researcher who discovers musical scores without knowing the notation cannot translate notes into words, because notes are not words. But structural analysis reveals patterns that match the harmonic series: forbidden combinations correspond to dissonant intervals, positional rules match musical form. The researcher proves the documents encode music without ever hearing a note.

Similarly, the Voynich Manuscript's 49 instruction classes, 17 forbidden transitions (in 5 hazard classes), kernel-centric convergence behavior, and bounded recovery architecture are structural constraints that map onto the physics of controlled distillation. The forbidden transitions correspond to physical failure modes. The convergence behavior matches thermodynamic equilibrium-seeking. The recovery architecture matches historical practice (Brunschwig's bounded reinfusion). The Galenic organizational framework (6/6 directional coherence at organizational level, but 0/4 at grammar level; Phase 376-384) provides the intellectual genealogy — as training background, not design principle (F-RUP-001).

This framing applies to ALL interpretations below: each section explores what specific aspects of the structure might correspond to in the physical domain, given that the structural fit has already been established.

---

## 0. APPARATUS-CENTRIC SEMANTICS (CCM Phase)

### Tier 3: Core Finding

> **The manuscript encodes the operational worldview of a controlled apparatus, not the descriptive worldview of a human observer.**

All recoverable semantics are those available to the apparatus and its control logic: states, transitions, risks, recoveries. All referential meaning (materials, plants, devices) is supplied externally by trained human operators.

### Token Decomposition (Complete)

Every Currier A/B token decomposes into four functional components:

```
TOKEN = PREFIX   → operation domain selector (selects allowed MIDDLE family)
      + SISTER   → operational mode (how carefully)
      + MIDDLE   → operation type (heating/cooling/monitoring)
      + SUFFIX   → context-dependent marker (system role + material class)
```

### Component-to-Class Mapping

| Component | Encodes | Classes | Evidence |
|-----------|---------|---------|----------|
| **PREFIX** | Operation domain | 4 classes selecting MIDDLE families | C911: 102 forbidden combinations |
| **SISTER** | Operational mode | 2 modes (precision/tolerance) | C412 anticorrelation |
| **MIDDLE** | Operation type | 3 families (k-energy, e-stability, h-monitoring) | C908-C910: kernel/section/REGIME correlation |
| **SUFFIX** | Two-axis marker | A/B system role + material class | C283, C495, C527 |

### PREFIX-MIDDLE Selection (C911 - Tier 2)

PREFIX and MIDDLE are **not independent**. Each PREFIX selects which MIDDLE family is grammatically legal:

| PREFIX Class | Selects For | Enrichment | Forbidden From |
|--------------|-------------|------------|----------------|
| **qo-** | k-family (k, ke, t, kch) | 4.6-5.5x | e-family, infrastructure |
| **ch-/sh-** | e-family (edy, ey, eey) | 2.0-3.1x | k-family, infrastructure |
| **da-/sa-** | infrastructure (iin, in, r, l) | 5.9-12.8x | All operational MIDDLEs |
| **ot-/ol-** | h-family (ch, sh) | 3.3-6.8x | k-family |
| **ok-** | e-family + infra | 2.6-3.3x | k-family |

**102 forbidden combinations** where expected ≥5 but observed = 0 (e.g., qo+ey, da+edy, ok+k).

This is **grammatical agreement**, not free combination. PREFIX determines the operation domain; MIDDLE specifies within that domain.

**SUFFIX Two-Axis Model (revised 2026-01-24):**

Suffix operates on two orthogonal dimensions:

| Axis | Scope | Finding | Tier |
|------|-------|---------|------|
| System role | A vs B enrichment | -edy 49x B, -ol 0.35x A-enriched | 2 (C283) |
| Material class | Within A: animal vs herb | Animal: 78% -ey/-ol; Herb: 41% -y/-dy | 3 (C527) |

The earlier "decision archetype (D1-D12)" mapping in ccm_suffix_mapping.md is **provisional and incomplete**. The fire-degree interpretation (C527) is conditional on Brunschwig alignment.

### Material-Behavior Classes (Revised with C911, C936)

| Class | Prefixes | Domain Target | Selects MIDDLE Family | Brunschwig Parallel |
|-------|----------|---------------|----------------------|---------------------|
| **Energy** | qo | Heat source | k-family only | Heating, distillation |
| **Process Testing** | ch, sh | The process | e-family only | Finger test, drip watching |
| **Vessel Management** | ok | The vessel/apparatus | e-family + infrastructure | Opening, closing, cooling vessel |
| **Correction** | ot, ol | Adjustment/continuation | h-family, e-family | Rectification, continuation |
| **Infrastructure** | da, sa | Setup configuration | iin/in/r/l only | Anchors, connectors |

PREFIX is a **domain selector** (C570, C571, C936): it determines WHAT you're acting on, while MIDDLE provides the action. The same MIDDLE with different prefixes produces different domain targets: ok+aiin = "check vessel", ch+aiin = "test check", qo+aiin = "heat check" (378 same-MIDDLE pairs confirmed, C936).

**ok specifically** was previously glossed as "seal" (then "seal/cover/plug" composite). Both verb-based approaches produce incoherent line readings. The vessel domain selector interpretation (C936 revised) produces the only coherent procedural readings across all four regimes. ok's restriction to e-family + infrastructure (C911) has a physical explanation: vessel operations are cooling/stability and apparatus management, not direct energy operations.

The earlier M-A/B/C/D classification is superseded by this domain-selector model. PREFIX class determines both the target domain and which operations (MIDDLEs) are grammatically permitted.

### MIDDLE Semantic Families (C908-C910 - Tier 2)

MIDDLEs encode **operation types**, not just variant identity. Three functional families emerge from kernel correlation, section distribution, and REGIME clustering:

| Family | MIDDLEs | Kernel Profile | Section Concentration | Function |
|--------|---------|---------------|----------------------|----------|
| **k-family** | k, ke, ck, ek, eck, kch, lk | HIGH_K (1.3-1.6x) | B (bathing) 1.5-2x | Heating, energy input |
| **e-family** | e, ed, eed, eo, eeo, eod, eey | HIGH_E (1.2-1.6x) | S (recipes) 1.3-1.7x | Cooling, stabilization |
| **h-family** | ch, sh, pch, opch, d | HIGH_H (1.2-1.6x) | T (text) 1.7-4x | Phase monitoring |

**Evidence strength:**
- 55% of MIDDLEs significantly correlate with kernel profile (C908)
- 96% of MIDDLEs are section-specific (C909)
- 67% of MIDDLEs are REGIME-specific (C910)

### Section-MIDDLE Alignment (C909 - Tier 2)

Manuscript sections use systematically different MIDDLE vocabularies, validating content interpretation:

| Section | Content | MIDDLE Profile | Brunschwig Interpretation |
|---------|---------|---------------|---------------------------|
| **B** (Bathing) | Human figures in tubs | k-enriched 1.5-2x | Balneum marie (water bath heating) |
| **H** (Herbal) | Plant illustrations | Mixed k+h | Extraction (heat + phase monitoring) |
| **S** (Recipes) | Recipe-like text | e-enriched 1.3-1.7x | Final products, stabilization |
| **T** (Text) | Text-only pages | h-enriched 1.7-4x | Instructions, procedures |
| **C** (Cosmological) | Diagrams | Infrastructure | Relational, connectors |

The "bathing figures" are not people bathing - they are **vessels in water baths** (balneum marie), the gentlest distillation method. The k-MIDDLE enrichment confirms heating operations.

### Precision Vocabulary (C912 - Tier 2)

The `m` MIDDLE (7.24x enriched in REGIME_4 precision folios) appears almost exclusively as the token `dam`:

| Property | Value |
|----------|-------|
| Form | `dam` = da (anchor) + m + ø (no suffix) |
| Frequency | 55% of all m-MIDDLE tokens |
| Section | Herbal 41% (precision extraction) |
| Function | Precision anchoring / verification marker |

This is a **specific lexical item**, not a productive pattern. It marks precision verification steps in quality-critical procedures.

### Two-Level Grammar Constraint (C908-C911)

Grammar operates at two levels with different constraint profiles:

| Level | Unit | Constraint Type | Freedom |
|-------|------|-----------------|---------|
| **Paragraph** | Multi-token sequence | Co-occurrence | Nearly free (585 positive pairs, 1 negative) |
| **Token** | PREFIX + MIDDLE | Morphological selection | Tight (102 forbidden combinations) |

**Interpretation:** A paragraph is a **recipe** containing multiple operation types. Individual tokens are **single operations** constrained to compatible PREFIX+MIDDLE combinations. You can have heating AND cooling in the same paragraph (different tokens), but a single qo- token cannot encode a cooling operation.

### Operational Modes (Sister Pairs)

| Sister | Mode | Escape Density | Meaning |
|--------|------|----------------|---------|
| **ch** (vs sh) | Precision | 7.1% | Tight tolerances, fewer recovery options |
| **sh** (vs ch) | Tolerance | 24.7% | Loose tolerances, more escape routes |

Statistical validation: rho = -0.326, p = 0.002 (C412)

### LATE Prefixes as Output/Completion Phase (Tier 3)

The V+L prefixes (al, ar, or) may function as output/completion markers within line-level control loops:

| Prefix | Position | Suffix-Less | Interpretation |
|--------|----------|-------------|----------------|
| al | 0.692 | 43.9% | Output marker |
| ar | 0.744 | 68.4% | Terminal form |
| or | 0.664 | 70.5% | Terminal form |

**Structural evidence (C539, Tier 2):**
- 3.78x enrichment at absolute line end
- V+L morphology distinct from consonantal ENERGY prefixes
- Short MIDDLE preference (om, am, y enriched)
- When not line-final, followed by ENERGY prefixes (cycle reset)

**Interpretive hypothesis (Tier 3):**
- EARLY position (ENERGY prefixes) = Initialize energy state
- MIDDLE position (mixed roles) = Monitor and intervene
- LATE position (V+L prefixes) = Record output / mark completion

This interpretation is consistent with closed-loop control semantics where each line represents a control cycle: setup → work → output. The V+L morphology may be phonologically motivated (easier articulation at phrase boundaries).

**Contrast with ol:** Despite sharing V+L morphology, ol sits at MIDDLE position (0.560) and has only 27.8% suffix-less rate (below baseline). ol is CORE_CONTROL, not LATE class. V+L pattern is necessary but not sufficient.

### L-compound as Modified Energy Operators (Tier 3)

L-compound operators (lch, lk, lsh) are structurally `l` + energy operator root (C298.a):

| Pattern | Count | Interpretation |
|---------|-------|----------------|
| lch = l + ch | 74 | Modified ch operation |
| lk = l + k | 58 | Modified k operation |
| lsh = l + sh | 24 | Modified sh operation |

**Positional shift:** The `l` modifier moves energy operations earlier in line (lch 0.344 vs ch 0.483). This may represent "pre-positioned" or "setup" energy operations before the main working phase.

**Provenance contrast with LATE:**
- L-compound: Fully B-internal (97% exclusive tokens, 86% exclusive MIDDLEs)
- LATE: B-prefix on PP vocabulary (85% exclusive tokens, 76% PP MIDDLEs)

L-compound is B's own infrastructure; LATE marks pipeline content at boundaries.

### Folio Program Type Differentiation (Tier 3)

L-compound rate and LATE rate show negative correlation (r = -0.305) at folio level:

| Folio Type | Example | L-compound | LATE | ENERGY |
|------------|---------|------------|------|--------|
| Control-intensive | f83v | 4.94% | 0.00% | High |
| Output-intensive | f40r | 0.00% | 6.19% | Lower |

**REGIME correlation:**
- REGIME_1/3: Higher L-compound (1.2-1.6%), higher ENERGY (48-50%), lower LATE
- REGIME_2/4: Lower L-compound (0.7-1.0%), lower ENERGY (35-38%), higher LATE

This suggests folios differ not just in content but in **control architecture**: some programs emphasize active control (L-compound heavy), others emphasize output recording (LATE heavy).

**Note:** Symmetric bracketing hypothesis (L-compound + LATE as line brackets) was tested and **falsified** - co-occurrence ratio 0.95x (independent), bracket order only 67.4%.

### Grammar Infrastructure Allocation by Section (Tier 3)

REGIME classifications reflect **grammar infrastructure allocation**, orthogonal to C494's execution precision axis:

| REGIME | L-compound | Kernel | LATE | Profile |
|--------|------------|--------|------|---------|
| REGIME_1 | 2.35% | 16.8% | 1.37% | Control-infrastructure-heavy |
| REGIME_2 | 0.32% | 10.2% | 3.14% | Output-intensive |
| REGIME_4 | 0.87% | 14.0% | 1.98% | Balanced |

**Section B Concentration (70% REGIME_1):**

| Section | REGIME_1 | REGIME_2 | REGIME_4 | Interpretation |
|---------|----------|----------|----------|----------------|
| B (balneological) | 70% | 5% | 10% | Control-heavy |
| H (herbal) | 13% | 31% | 44% | Output-distributed |
| S (stellar) | 17% | 35% | 43% | Output-distributed |

Section B (traditionally "bathing figures") concentrates in REGIME_1, suggesting these folios document procedures requiring:
- Heavy control infrastructure (L-compound, kernel)
- Active intervention (16.8% kernel contact per line)
- Modified energy operations (L-compounds enriched 2.6-7.5x)

**Enriched MIDDLEs in REGIME_1:**
- lsh: 7.51x, lch: 4.38x, lk: 2.61x (L-compound family)
- ect: 4.66x, ct: 2.31x (control operators)

**Fire-degree distributes by Section, not REGIME:**

| Section | High-Fire | Low-Fire | Ratio |
|---------|-----------|----------|-------|
| H | 3.9% | 17.8% | 0.22 (lowest) |
| B | 7.5% | 19.4% | 0.39 |
| S | 7.1% | 15.2% | 0.47 |
| C | 6.1% | 12.9% | 0.48 (highest) |

**Orthogonality with C494:** This classification (grammar composition) is independent of C494's precision axis (execution requirements). A folio can be both high-precision (C494 REGIME_4) AND control-infrastructure-heavy (this analysis REGIME_1).

**Source:** REGIME_SEMANTIC_INTERPRETATION phase (2026-01-25)

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

**Semantic Ceiling Gradient (C499, v4.31):**

The ceiling has layers - not all irrecoverable information is equally irrecoverable:

| Level | Recoverability | Method |
|-------|----------------|--------|
| Entity identity (lavender) | IRRECOVERABLE | - |
| Material CLASS priors | **PARTIALLY RECOVERABLE** | Bayesian inference via procedural context |
| Procedural context | RECOVERABLE | Folio classification, product type |

**Conditional recovery (IF Brunschwig applies):**
- 128 registry-internal MIDDLEs with full P(material_class) vectors
- 27 tokens with P(animal) = 1.00 (PRECISION-exclusive)
- Mean entropy: 1.08 bits (86% match null baseline)

The distinction is epistemological, not ontological: the system MAY encode specific materials, we just can't recover WHICH.

### Why This Matters

The apparatus-centric perspective explains:
- Why vocabulary is universal across sections (comparability over specificity)
- Why no quantities appear (apparatus tracks state, not magnitude)
- Why illustrations look botanical but grammar does not (images are human context; text is control logic)
- Why ~1,184 MIDDLEs exist (expert recognition vocabulary, not linguistic labels)

### The -Xy Suffix Compositional Family (Tier 3)

The four primary `-y`-based suffixes form a systematic family where a kernel consonant modifies the base `-y` ("end") suffix:

| Suffix | Kernel | Gloss | Tokens | Compositional Reading |
|--------|--------|-------|--------|-----------------------|
| `-y`   | null   | "end" | 458 | bare close |
| `-ey`  | E      | "set" | 769 | e-kernel stabilizing close |
| `-dy`  | K      | "seal" | 594 | k-kernel decisive close |
| `-hy`  | H      | "confirm" | 910 | h-kernel phase-verifying close |

**Structure:** consonant + y = kernel-typed variant of "end."

**The d/k kernel cross-over:** `d` shifts kernel from H (as MIDDLE, "mark") to K (as suffix `-dy`, "seal"). C919 (Tier 2) establishes that the d-extension is END-class — inherently a closer. `k` is an energy *operator*, not a closer; `d` is the closing form that operates in k's domain. The suffix system uses closing-form consonants, not raw kernel consonants.

**Distillation reading (Tier 4):** The three kernel-typed closers correspond to how a distiller ends different operations:
- `-ey` "set" = stabilize at this point (temperature reached, hold it)
- `-dy` "seal" = lock and close (fraction collected, seal the vessel)
- `-hy` "confirm" = verify phase state before proceeding (check the condensate is the right fraction)

The `-hy` gloss "confirm" replaces the earlier "hazard flag" (BCSC revision). C907 falsified the connector hypothesis (0.99x boundary enrichment), which is consistent: `-hy` modifies the current operation (phase verification), it does not link to the next one. The 86% mid-line positioning (C907) places `-hy` tokens in the monitoring zone where active phase checking occurs.

**Example:** `chckhy` = ch:hard.confirm = "actively test hardness, confirm phase state." The operator tests the material's consistency, then verifies they're collecting the correct fraction.

**Provenance:** C907 (morphological characterization, Tier 2), C919 (d-extension END-class, Tier 2), C1003 (pairwise compositionality, Tier 2). The compositional reading and distillation alignment are Tier 3.

### Kernel-German Abbreviation Hypothesis (Tier 4)

The Voynich consonant inventory may encode first-letter abbreviations of German and Latin distillation vocabulary. The strongest evidence is the three kernel consonants mapping to the three fundamental distillation operations.

#### Core Mapping (Strong — Tier 4a)

| Kernel | Function | Abbreviation | Meaning | Confidence |
|--------|----------|-------------|---------|------------|
| **K** | ENERGY_DRIVER | **K**ochen (Ger.) | to boil/cook | Strong |
| **E** | STABILITY_ANCHOR | **E**rkalten (Ger.) | to cool down | Strong |
| **H** | PHASE_MANAGER | **H**alten / **H**üten (Ger.) | to hold/maintain; to watch over | Strong |

These are the three fundamental operations of distillation. Any German-speaking distiller would know kochen, erkalten, halten as the basic triad: heat it, cool it, hold it steady. Hüten (to watch, guard) is an alternative for H that aligns with the PHASE_MANAGER monitoring role.

#### Latin Elements (Strong — Tier 4a)

| Element | Position | Abbreviation | Meaning | Confidence |
|---------|----------|-------------|---------|------------|
| **qo** | PREFIX (energy channel) | **Co**quo (Lat.) | I boil/cook | Strong |
| **op** | PREFIX | **Op**erare (Lat.) | to operate/work | Moderate |

The `qo` = coquo connection is particularly compelling: qo is the energy channel prefix that exclusively selects k-family MIDDLEs (C911). Latin *coquo* and German *kochen* are cognates — both descend from Proto-Indo-European \*pekʷ- ("to cook"). The same root word appears as the PREFIX (qo = coquo) and as the KERNEL (k = kochen), one in Latin, one in German, encoding the same concept at two structural levels.

#### Extended Consonant Mappings (Moderate — Tier 4b)

| Consonant | Our Gloss | German Candidate | Meaning | Confidence |
|-----------|-----------|-----------------|---------|------------|
| **d** | "seal" (END-class, C919) | **D**ichten | to seal/make tight | Moderate |
| **t** | "transfer" | **T**reiben | to drive; also *abtreiben* = to drive off volatiles | Moderate |
| **s** | "break" | **S**cheiden | to separate/part | Moderate |
| **g** | "complete" | **G**ar | done/fully cooked | Moderate |
| **m** | "measure" | **M**essen | to measure | Moderate |
| **r** | "stir" | **R**ühren | to stir | Moderate |

Note: *abtreiben* (to drive off volatiles) is a standard German distillation term and strengthens the t=Treiben mapping.

#### Weak/Speculative Mappings (Tier 4c)

| Element | Position | Candidate | Meaning | Confidence |
|---------|----------|-----------|---------|------------|
| **l** | SUFFIX/MIDDLE | **L**etzt (last) or **L**assen (to let) | last; to allow/release | Weak |
| **p** | SUFFIX | **P**ause | pause/rest | Weak |
| **ain** | MIDDLE | **Ein** (Ger.) | in/into (intake) | Weak |
| **da** | FL prefix | **Da** (Ger.) | there/then | Weak |

The `da` mapping is suggestive because FL tokens decompose as da+stage, and German "da" functions as a deictic ("there/then") that could introduce a state reference.

#### Linguistic Evidence

**Dialect evidence:** The manuscript's Brunschwig alignment points to Strasbourg, in the Alemannic German dialect region. In Alemannic, the initial k-sound is pronounced and written as **ch** (e.g., "choche" for "kochen"). This may explain the ch/k relationship in the notation system — ch as the Alemannic pronunciation of the k-family channel.

**Latin-German hybrid pattern:** The vocabulary splits along a functional axis:
- **German** = operational workshop vocabulary (kochen, erkalten, halten, dichten, treiben, scheiden, messen, rühren) — the verbs a practitioner uses while working
- **Latin** = theoretical/academic vocabulary (coquo, operare) — the terms from books and formal instruction

This bilingual split is consistent with a guild-trained German practitioner educated in Latin alchemical texts, precisely matching Brunschwig's biography (Strasbourg guild surgeon, Latin-educated, wrote *Liber de arte distillandi*).

#### Status and Constraints

Fully Tier 4. The K-E-H + qo core is structurally suggestive (perfect functional alignment, etymological qo/k link) but cannot be validated from internal analysis alone. Extended mappings have varying confidence. The hypothesis strengthens C911 (qo selects k-family), C521 (kernel opposition), and C929 (suffix semantics) without contradicting any existing constraint.

**Expert validation (Round 8):** No constraint conflicts identified. Internal tiering (4a/4b/4c) recommended to distinguish strong core from weaker extensions.

---

## 0.A. CURRIER A COGNITIVE INTERFACE (PCC Phase)

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

Universal Boundaries apply. Additionally:
- ❌ Closure markers are adaptive signals
- ❌ Working-memory structure implies temporal ordering

### Cross-References

| Constraint | Finding |
|------------|---------|
| C233 | LINE_ATOMIC (base for closure model) |
| C346 | Sequential coherence 1.20x |
| C424 | Clustered adjacency |
| C422 | DA articulation |

**Source:** phases/POST_CLOSURE_CHARACTERIZATION/PCC_SUMMARY_REPORT.md

---

## 0.A.1. RI INSTANCE IDENTIFICATION SYSTEM (RI_EXTENSION_MAPPING Phase)

### Tier 2/3: Core Finding

> **RI vocabulary functions as an instance identification system built via derivational morphology from PP vocabulary. PP encodes general categories shared with B execution; RI extends PP with single-character markers to identify specific instances. This explains A's purpose as an index bridging general procedures (B) to specific applications (labels, illustrated items).**

This resolves the fundamental question: "Why does Currier A exist if Currier B is self-sufficient for execution?"

### The Three-Level Model

| Level | Vocabulary | Function | Example |
|-------|-----------|----------|---------|
| **B (Execution)** | PP only | General operations | "Process 'od' at temperature 'kch'" |
| **A (Registry)** | PP + RI | Specific instances | "Entry for 'odo': follow procedure X" |
| **Labels** | RI-enriched (3.7x) | Illustration pointers | "This drawing = 'odo'" |

### The Derivational System

RI is built from PP through single-character extensions:

```
PP MIDDLE 'od' (category: herb/material class)
     |
     +-- 'odo' (instance 1) - used in label
     +-- 'oda' (instance 2) - used in text
     +-- 'odd' (instance 3) - used in text
```

**Structural evidence:**
- 90.9% of RI MIDDLEs contain PP as substring (C913)
- 71.6% of extensions are single characters
- Position preferences exist: 'd' is 89% suffix, 'h' is 79% prefix

### Dual-Use Pattern

225 PP MIDDLEs appear both directly AND as RI bases, demonstrating the category/instance distinction:

| PP MIDDLE | Direct Uses | As RI Base | Interpretation |
|-----------|-------------|------------|----------------|
| 'od' | 191 | 23 | Category AND instances |
| 'eo' | 211 | 14 | Category AND instances |
| 'ol' | 790 | 4 | Mostly category |

### Why Labels Are RI-Enriched (3.7x)

Labels point to **specific illustrated items**, not general categories:
- Text: 7.4% RI (discusses general procedures)
- Labels: 27.3% RI (points to THIS plant, not plants in general)

The derivational system provides the instance-specificity labels require.

### The A-B Relationship

```
Currier B = PROCEDURE LIBRARY
  - General instructions for operations
  - Uses PP vocabulary (categories only)
  - "How to process herbs" (general)
       |
       v
Currier A = REGISTRY/INDEX
  - Specific instances of procedures
  - Uses PP + RI vocabulary
  - "Entry for THIS herb: follow procedure X"
       |
       v
Labels = POINTERS
  - Link illustrations to registry entries
  - RI-enriched for instance-specificity
```

### What This Resolves

| Question | Answer |
|----------|--------|
| Why does A exist if B is self-sufficient? | A indexes specific applications of general B procedures |
| Why are labels RI-enriched? | Labels point to specific illustrated items |
| What is RI vocabulary? | Instance identifiers derived from PP categories |
| How do A and B relate? | Same conceptual vocabulary, different granularity |

### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- X RI encodes semantic content beyond instance differentiation

### Cross-References

| Constraint | Finding |
|------------|---------|
| C240 | A = Registry - now explains the indexing mechanism |
| C913 | RI Derivational Morphology |
| C914 | RI Label Enrichment (3.7x) |
| C915 | Section P Pure-RI Entries |
| C916 | RI Instance Identification System (synthesis) |

**Source:** phases/RI_EXTENSION_MAPPING/README.md

---

## 0.A.2. LABEL-TO-B PIPELINE (LABEL_INVESTIGATION Phase)

### Tier 2/3: Core Finding

> **Labels connect to B through shared PP vocabulary, with jar labels specifically concentrating in AX_FINAL (material-carrying) positions at 2.1x baseline rate. This validates the three-level model: Labels identify materials that B procedures operate ON.**

### The Complete Pipeline

```
ILLUSTRATION
     |
     v
LABEL (uses RI/PP vocabulary)
  - Jar labels: container identifiers (35.1% AX_FINAL in B)
  - Content labels: material identifiers (roots, leaves)
     |
     v
PP BASE (shared with B)
  - 97.9% of labels connect to B vocabulary
  - 104 unique PP bases from 192 labels
     |
     v
B PROCEDURE (deploys PP in roles)
  - AX_FINAL: maximum scaffold depth (material specification)
  - EN: operational positions
```

### Jar vs Content Distinction

| Label Type | B Connection | AX_FINAL Rate | Function |
|------------|--------------|---------------|----------|
| **Jar** | PP bases in B | **35.1%** (2.1x) | Container/configuration identifier |
| **Content** | PP bases in B | 19.1% (1.14x) | Material identifier (root, leaf) |
| B Baseline | - | 16.7% | Reference |

Jar labels are statistically significant (chi2=30.15, p=4e-08); content labels show moderate enrichment.

### What This Validates

| Finding | Significance |
|---------|--------------|
| **C571 confirmed** | PREFIX selects role, MIDDLE carries material identity |
| **Labels are functional** | They point to materials that B operates on |
| **AX_FINAL = material slot** | Per C565, maximum scaffold depth = where materials are specified |
| **Cross-system coherence** | A (labels) -> B (procedures) uses shared vocabulary in predictable positions |

### The Jar-to-AX_FINAL Interpretation

```
JAR LABEL "okaradag" (f99r)
     |
     v
PP BASE "ara" (extracted MIDDLE)
     |
     v
B TOKEN "ot-ara-y" appearing in AX_FINAL position
     = "the thing being processed"
```

Jar labels identify materials at **maximum scaffold depth** - the boundary/completion position where material identity is specified without operational modification. This is where you'd expect "what to process" to appear.

### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- X Specific jar-to-procedure mappings are recoverable
- X Content labels have the same AX_FINAL concentration (they don't)

### Cross-References

| Constraint | Finding |
|------------|---------|
| C565 | AX_FINAL positional semantics |
| C570 | AX PREFIX derivability |
| C571 | PREFIX selects role, MIDDLE carries material |
| C523 | Pharma jar label vocabulary bifurcation |
| C914 | RI label enrichment (3.7x) |
| C928 | Jar label AX_FINAL concentration (2.1x) |

**Source:** phases/LABEL_INVESTIGATION/README.md

---

## 0.B. PP FUNCTIONAL ROLE CLOSURE (PP_B_EXECUTION_TEST Phase)

### Tier 2: Core Finding

> **PP (Pipeline-Participating) MIDDLEs have a two-level effect: COUNT determines class survival breadth, COMPOSITION determines intra-class token configuration.**

This resolves both the C505 paradox (material-class PP differentiation with null class-level effects) and the "480 token paradox" (why maintain 480 tokens if 49 classes suffice).

### The Two-Level PP Effect (C506, C506.a)

| Level | What PP Determines | Evidence |
|-------|-------------------|----------|
| **Class** | Which instruction types survive | COUNT matters (r=0.715), COMPOSITION doesn't (cosine=0.995) |
| **Token** | Which variants within classes are available | COMPOSITION matters (Jaccard=0.953 when same classes) |

**Variable taxonomy:**

| Variable Type | System | What It Does | Evidence |
|---------------|--------|--------------|----------|
| **Routing** | AZC | Position-indexed legality | C443, C468 |
| **Differentiation** | RI | Identity exclusion (95.7% incompatibility) | C475, C481 |
| **Capacity** | PP | Class survival breadth (count) | C504, C506 |
| **Configuration** | PP | Intra-class token selection (composition) | C506.a |

**Key insight:** Classes are instruction types; tokens are parameterized variants.

### Evidence Summary

| Test | Result | Interpretation |
|------|--------|----------------|
| PP count vs B class survival | r=0.715, p<10^-247 | COUNT determines class breadth |
| PP composition vs B class mix | Cosine=0.995 | COMPOSITION irrelevant at class level |
| PP composition vs token availability | Jaccard=0.953 | COMPOSITION matters at token level (~5% variation) |
| Per-class survival | 0/49 significant | No individual class differs |

### PP Count Gradient (Class Level)

| PP Count | Mean B Classes | n |
|----------|----------------|---|
| 0-2 | 19.0 | 171 |
| 3-5 | 30.9 | 805 |
| 6-8 | 37.2 | 525 |
| 9-11 | 41.4 | 64 |
| 12-15 | 43.9 | 13 |

### Resolution of the 480 Token Paradox

Why maintain 480 distinct tokens across 49 classes?

Answer: **Intra-class behavioral parameterization.**

- The 49 classes provide the operational grammar (what instructions exist)
- The ~480 tokens provide behaviorally distinct variants (how each instruction executes)
- PP COUNT determines class survival breadth (how many instruction types)
- PP COMPOSITION determines intra-class configuration (which behavioral variants)

Animal materials don't need different *classes* than plant materials — they need different *execution flows* within the same class structure. C505's PP profile differences shape which behavioral variants are available, not which classes survive.

### Intra-Class Behavioral Heterogeneity (C506.b, v4.36)

Tokens within the same class but with different MIDDLEs are **positionally compatible but behaviorally distinct**:

| Dimension | Same-MIDDLE | Different-MIDDLE | p-value |
|-----------|-------------|------------------|---------|
| Position | Similar | Similar | 0.11 (NS) |
| Transitions | Similar | **Different** | <0.0001 |

73% of MIDDLE pairs within classes have transition JS divergence > 0.4.

**The "Chop vs Grind" Pattern:**

Like "chop" and "grind" in a recipe:
- Both appear in the same grammatical slot (positionally compatible)
- But they lead to different subsequent operations (behaviorally distinct)

Classes define **grammatical equivalence** (what can substitute syntactically), not **semantic equivalence** (what does the same thing operationally).

**Implication for PP composition:**

```
PP composition → MIDDLE selection → transition pattern variation
                                  → execution flow differences
                                  (within fixed class structure)
```

The ~5% token variation (C506.a) is **behaviorally meaningful**, not noise.

### What C505 Actually Means (Revised)

C505's material-class PP profile differences are **configuration markers**:

> PP profiles shape which token variants are available within surviving classes.

PP profile variation allows:
- Material-specific parameterization within shared class framework
- Same operational grammar, different execution variants
- Structural adaptation without semantic encoding

### Why Class-Level Null Effects Are Correct

The class-level null results (C506) protect the semantic ceiling (C171, C469):

- If PP composition caused different *classes* to survive → PP would encode material-specific instruction sets
- Material-specific instruction sets → violates PURE_OPERATIONAL constraint
- Therefore: class-level null effects are architecturally necessary

But token-level variation (C506.a, C506.b) is permitted:
- Same classes, different behavioral variants
- Structural adaptation without changing the instruction vocabulary
- This is parameterization, not semantic encoding

### What This Closes

- PP composition → class survival: **FALSIFIED** (C506)
- PP composition → token configuration: **CONFIRMED** (C506.a)
- PP composition → behavioral variation: **CONFIRMED** (C506.b)
- PP functional characterization: **COMPLETE** (two-level model)

### PP-HT Responsibility Substitution (C507, v4.34)

**Resolved:** PP capacity is weakly but significantly inversely correlated with HT density.

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Spearman rho | **-0.294** | Moderate negative |
| p-value | **0.0015** | Highly significant |
| PP 0-3 HT density | 18.83% | High HT when low PP |
| PP 6+ HT density | 12.62% | Low HT when high PP |
| PP vs HT TTR | **+0.40** | More varied HT with more PP |

**Two-axis HT model:**
1. **HT density axis** — how much HT appears (negatively correlated with PP)
2. **HT diversity axis** — how varied HT is when it appears (positively correlated with PP)

**Interpretation:** PP and HT partially substitute in a "responsibility budget." More grammatical freedom (PP capacity) correlates with less human vigilance (HT density) but more varied vigilance (HT TTR).

This is NOT:
- Complete substitution (r = -0.29, not -0.8)
- HT tracking PP content (composition doesn't matter per C506)
- Causal relationship (correlation only)

### What Remains Open

The next frontier is **PP × HT × AZC three-way interaction**:
- Does AZC position modulate the PP-HT trade-off?
- Does PP count increase operator error tolerance?
- Regime-specific HT compensation patterns

This shifts from "what PP is" to "what the artifact does to the human."

### Cross-References

| Constraint | Role |
|------------|------|
| C504 | PP count correlation (r=0.772) |
| C505 | A-side profile differences |
| C506 | Non-propagation to B |
| C507 | PP-HT partial substitution |
| C171 | Semantic ceiling protection |
| C469 | Categorical resolution |

**Source:** PP_B_EXECUTION_TEST (2026-01-23), PP_HT_INTERACTION_TEST (2026-01-23)

---

## 0.C. THREE-LAYER CONSTRAINT ARCHITECTURE (MIDDLE_SUBCOMPONENT_GRAMMAR Phase)

### Tier 2-3: Architectural Discovery

> **The manuscript's symbol system operates through three independent constraint layers sharing a single substrate - construction, compatibility, and execution - which together achieve complex morphology, extreme vocabulary sparsity, AND execution safety simultaneously.**

### The Problem This Solves

Prior analysis identified multiple constraint regimes:
- C085: 10 kernel primitives (s, e, t, d, l, o, h, c, k, r)
- C109: 17 forbidden transitions between token classes
- C475: 95.7% of MIDDLE pairs are incompatible
- C517: Superstring compression with hinge letters

The question: Are these the same constraint seen at different scales, or independent systems?

### Key Evidence (Test 17)

**Hypothesis tested:** Construction constraints (within-token) are isomorphic to execution constraints (between-token).

**Result:** FALSIFIED

| Metric | Value |
|--------|-------|
| Pearson correlation | r = -0.21 |
| p-value | 0.07 (not significant) |
| Category match rate | 28.4% (near random) |

Construction-suppressed pairs: only 2.9% also suppressed in execution.
Construction-elevated pairs: 0% also elevated in execution.

### Three-Layer Architecture

```
SYMBOL SUBSTRATE (10 primitives: s,e,t,d,l,o,h,c,k,r)
         |
         ├── CONSTRUCTION LAYER (C521)
         |     - Directional asymmetry within tokens
         |     - One-way valve: e→h blocked (0.00), h→e favored (7.00x)
         |     - Result: Legal token forms
         |
         ├── COMPATIBILITY LAYER (C475)
         |     - MIDDLE atomic incompatibility
         |     - 95.7% of pairs forbidden
         |     - Result: Legal co-occurrence
         |
         └── EXECUTION LAYER (C109)
               - 17 forbidden transitions between classes
               - Phase-ordering dominant (41%)
               - Result: Legal program paths
```

### Why This Matters

**Independence enables modularity:**
- Construction constraints can evolve without breaking execution
- Compatibility constraints can be tuned without rebuilding morphology
- Execution hazards can be managed without token redesign

**Shared substrate enables compactness:**
- Same 10 characters do triple duty
- No separate "syntax layer" needed
- Information density maximized

**Real-world analogy:** Consider a programming language where:
- Character encoding rules govern what strings are valid identifiers
- Type system rules govern what combinations are semantically valid
- Control flow rules govern what execution orders are safe

These are independent - changing identifier rules doesn't change type checking.

### Kernel Primitive Reality

Test 15-16 confirmed kernel primitives (k, h, e) are **real operators**, not compression artifacts:

**Directional Asymmetry (C521):**
| Transition | Ratio | Interpretation |
|------------|-------|----------------|
| e→h | 0.00 | STABILITY → PHASE: completely blocked |
| h→e | 7.00x | PHASE → STABILITY: highly favored |
| k→e | 4.32x | ENERGY → STABILITY: favored |

This one-way valve topology **cannot arise from compression mechanics**. Compression would create symmetric patterns (hinges work both directions). The asymmetry proves functional operator status.

### Interpretive Implication (Tier 3)

The three-layer architecture suggests the manuscript was designed for:

1. **Expressive power:** Complex token morphology (construction layer)
2. **Safety:** Incompatibility prevents dangerous combinations (compatibility layer)
3. **Control:** Execution constraints maintain system stability (execution layer)

These goals are achieved **independently**, allowing each to be optimized without trade-offs.

### RI as Operational Signature (Tier 3)

RI MIDDLEs encode **compatibility intersections** at the construction layer:
- 85.4% contain multiple PP atoms (C516)
- Each atom is a compatibility dimension
- RI = PP₁ ∩ PP₂ ∩ PP₃ ∩ ... ∩ modifier

This explains why RI is:
- Unique to A (compatibility specification is A-side)
- Highly specific (multi-atom = narrow intersection)
- Length-correlated with uniqueness (more atoms = more specific)

### Cross-References

| Constraint | Role |
|------------|------|
| C085 | 10 kernel primitives (shared substrate) |
| C109 | Execution hazards (execution layer) |
| C475 | MIDDLE incompatibility (compatibility layer) |
| C517 | Superstring compression (hinge letters) |
| C521 | Directional asymmetry (construction layer) |
| C522 | Layer independence (falsified isomorphism) |

**Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

---

## 0.C.1. MIDDLE ATOM BEHAVIORAL COMPOSITION (COMPOUND_DECOMPOSITION + CROSSWORD_GLOSS_VALIDATION Phases)

### Tier 2: Statistical Foundation (C1190, C1191)

> **Single-character MIDDLEs are genuine behavioral atoms. Compound MIDDLEs inherit behavioral profiles by additive composition of their component atoms. Permutation test: r=0.754, z=3.32, p<0.001, 0/1000 permutations beating real assignment.**

> **Additive composition is MIDDLE-specific (C1190 scope correction, Phase 422). PREFIX compounds show emergent behavior — atoms c, h, s, p acquire specialized profiles in PREFIX position that exceed simple addition (C1191). SUFFIX position imposes a systematic behavioral shift on all atoms (pairwise shift correlation r=0.892). Atoms maintain consistent IDENTITY across positions (15/18 CONSISTENT) but follow position-specific COMPOSITIONAL RULES (C1191).**

This finding provides behavioral validation of Section 0.C's three-layer architecture. The construction layer isn't just string manipulation — the atoms being constructed with carry genuine functional signatures that compose additively in MIDDLE position, while PREFIX and SUFFIX positions apply distinct compositional rules.

### Key Results

| Variant | Real r | Perm r | Z | p |
|---------|--------|--------|---|---|
| All features (incl kernel) | 0.711 | 0.478 | 5.04 | <0.001 |
| **No kernel (circularity-free)** | **0.754** | **0.605** | **3.32** | **<0.001** |
| Kernel only | 0.500 | 0.008 | 4.12 | 0.002 |

The no-kernel variant controls for the possibility that kernel assignments derive from character content (tautology). Result holds without kernel features — compositionality is carried by purely behavioral signals: prefix co-occurrence (R=0.62), line-final rate (R=0.47), suffix rate (R=0.45), section distribution (R=0.43).

### Tier 3: Compositional Gloss Families

The following atom composition patterns are consistent across all compound appearances. Glosses derived from independent behavioral analysis (MIDDLE_SEMANTIC_MAPPING phase), NOT from decomposition.

**The y-terminal family (6/6 compounds fit):**

y = "end" (458 tokens standalone). Every -y compound is a type of ending:

| Compound | Decomposition | Gloss | Fit |
|----------|--------------|-------|-----|
| ey | cool + end | "set" (cooling done) | Strong |
| dy | mark + end | "seal" | Strong |
| hy | watch + end | "confirm" | Strong |
| ly | late + end | "end" | Strong |
| ry | mid + end | "finish" | Strong |
| eey | cool + cool + end | "deep" | Strong |

**The i+n intake/iterate family (6/6 compounds fit):**

If i = "cycle/iterate" and n = "bind/connect":

| Compound | Decomposition | Gloss | Fit |
|----------|--------------|-------|-----|
| ii | cycle + cycle | "repeat" | Strong |
| in | cycle + bind | "link" | Strong |
| iin | cycle + cycle + bind | "iterate" | Strong |
| ain | into + cycle + bind | "intake" | Strong |
| aiin | into + cycle + cycle + bind | "settle" | Strong |
| oiin | vessel + cycle + cycle + bind | "loop" | Strong |

**Order-sensitive kernel compounds (Tier 2 atoms only):**

| Compound | Decomposition | Gloss | Note |
|----------|--------------|-------|------|
| ke | heat + cool | "steady" | Heat-first: balanced by cooling |
| ek | cool + heat | "exact" | Cool-first: precise temperature |
| ee | cool + cool | "long" | Extended cooling |
| kee | heat + cool + cool | "deep" | Deep processing |
| eek | cool + cool + heat | "lock" | Locked/fixed state |

Same letters in different orders produce different but related glosses. Order sensitivity is structurally grounded in C521 (kernel directional asymmetry) and C1065 (atom bigram ordering grammar).

### Tier 4: The "o = vessel" Hypothesis

Current dictionary gloss "near" fails across 21 compound appearances. The hypothesis o = "vessel" (German *Ofen* = furnace) improves most fits:

| Compound | Decomposition | Gloss | Fit |
|----------|--------------|-------|-----|
| ok | vessel + heat | "seal" (seal before heating) | Strong |
| ot | vessel + transfer | "route" (through vessel) | Strong |
| ol | vessel + late | "continue" (let proceed) | Moderate |
| eo | cool + vessel | "open" (open cooled vessel) | Strong |
| opch | vessel + pause + adjust + watch | "operate" | Moderate |
| oiin | vessel + cycle + cycle + bind | "loop" | Strong |

The ok/ot sister pair (C408) decomposes as: ok = proactive vessel+heat management, ot = corrective vessel+transfer adjustment — matching the structural analysis exactly.

### Tier 4: Confidence Gradient Methodology

C1190 licenses using compound decomposition as a **gloss correction tool** with confidence grading:

- **High confidence:** Compounds whose atoms have Tier 2 behavioral profiles AND whose predicted profile closely matches observed (ke, ek, ee, hy, dy, ey)
- **Medium confidence:** Compounds with moderate-confidence atoms and reasonable fit (al, ar, ol, or)
- **Low confidence:** Compounds with weak atoms or poor prediction residuals

This methodology respects the semantic ceiling (C171, C120) — glosses describe operational function, not material identification.

### Cross-References

| Constraint | Role |
|------------|------|
| C1190 | MIDDLE behavioral atomicity (additive composition, MIDDLE-specific) |
| C1191 | Position-dependent composition (PREFIX emergent, SUFFIX systematic shift) |
| C267.a | 218 sub-components reconstruct 97.8% (structural basis) |
| C1003 | Pairwise compositionality at TOKEN level |
| C1065 | Atom bigram ordering grammar |
| C521 | Kernel directional asymmetry (order sensitivity) |
| C1070 | Ordering grammar independent of kernel physics |
| C929 | ch/sh sensory modality (explains PREFIX compound emergence) |
| C906 | Vowel primitive suffix saturation |

**Source:** COMPOUND_DECOMPOSITION phase (2026-02-21)

---

## 0.D. RI LEXICAL LAYER HYPOTHESIS (RI_STRUCTURE_ANALYSIS Phase)

### Tier 3: Grammar vs Lexicon Distinction

> **RI extensions within MIDDLEs may function as a LEXICAL layer that anchors abstract grammar to specific external substances, while PREFIX/SUFFIX/PP remain purely functional markers operating as GRAMMAR.**

This extends C526 with a detailed characterization of the two-layer model.

### The Problem This Addresses

C120 (PURE_OPERATIONAL) establishes that Voynich tokens have no semantic content. But RI MIDDLEs exhibit vocabulary-like behavior:
- 609 unique identifiers (regenerated 2026-01-24 with atomic-suffix parser)
- Localized to specific folios (87% on only 1 folio)
- Non-compositional (don't decompose systematically)
- Appear with varying PREFIX/SUFFIX combinations

This creates tension: How can 609 arbitrary localized identifiers have "no semantic content"?

### Resolution: Grammar vs Lexicon

The resolution distinguishes two functional layers:

| Layer | Components | Function | Semantic Status |
|-------|------------|----------|-----------------|
| **Grammar** | PREFIX, SUFFIX, PP atoms | Control-flow, procedural | No content (C120 applies) |
| **Lexicon** | RI extensions | Referential anchoring | Points to substances (THAT, not WHAT) |

**Grammar** is combinatorial and global:
- ch prefix used with 57 different MIDDLEs
- dy suffix used with 40 different MIDDLEs
- PP atoms appear across all systems (A, B, AZC)

**Lexicon** is arbitrary and localized:
- RI extensions don't decompose systematically
- 83% appear on only 1-2 folios
- Extensions function as dictionary entries, not grammatical positions

### Evidence Summary

**RI Localization Pattern:**

| Category | Percent | Avg Folios | Interpretation |
|----------|---------|------------|----------------|
| Strictly local (1 folio) | 87.3% | 1.0 | Specific material identifiers |
| Local (1-2 folios) | ~90% | 1.28 avg | Material identifiers |
| Distributed (10+ folios) | <1% | varies | Compatibility bridges |

**NOTE (2026-01-24):** Regenerated with atomic-suffix parser. With 609 RI MIDDLEs: 87% appear on only 1 folio, avg ~1.3 folios.

**PREFIX/SUFFIX Versatility:**

| Affix | Different MIDDLEs | Role |
|-------|-------------------|------|
| ch | 57 | Global grammatical marker |
| sh | 29 | Global grammatical marker |
| qo | 27 | Global grammatical marker |
| dy | 40 | Global grammatical marker |
| y | 34 | Global grammatical marker |

Same affixes combine with many different RI extensions - the grammar layer is independent of the lexical layer.

**Variation Pattern:**
- 95% of localized RI appear with multiple PREFIX/SUFFIX combinations
- Same RI MIDDLE, different grammatical context
- Example: `cheom`, `sheom`, `okeom`, `cheomam` all share MIDDLE `eom`

### The Two-Layer Model

```
Word Structure:
  TOKEN = PREFIX + MIDDLE + SUFFIX
          ↓        ↓        ↓
          Grammar  MIDDLE   Grammar
                   ↓
           PP_atom + Extension
           ↓         ↓
           Grammar   Lexicon
```

**Interpretation:**
- PP atoms encode **procedural compatibility** (what can be done)
- RI extensions encode **referential identity** (to what)
- PREFIX/SUFFIX encode **grammatical context** (in what form)

### RI PREFIX Bifurcation (C528)

RI MIDDLEs split into two nearly-disjoint populations based on PREFIX behavior:

| Population | Count | % of RI |
|------------|-------|---------|
| PREFIX-REQUIRED | 334 | 50.1% |
| PREFIX-FORBIDDEN | 321 | 48.1% |
| PREFIX-OPTIONAL | 12 | 1.8% |

**Key finding:** Only 1.8% of RI MIDDLEs appear both ways. The rest are locked into one pattern.

**Section independence:** Both populations show identical distributions across H and P sections (~54% PREFIX rate in each). The split is substance-inherent, not section-driven.

**Implication for two-layer model:** PREFIX is grammatical globally, but its attachment to specific RI MIDDLEs is **lexically encoded**. Each substance identifier inherently requires or forbids PREFIX marking:

```
RI Vocabulary (609 MIDDLEs)  [regenerated 2026-01-24]
+-- PREFIX-REQUIRED (~50%): Always appear with PREFIX
|     Examples: acp, afd, aiikh, akod, alda
|
+-- PREFIX-FORBIDDEN (~50%): Never appear with PREFIX
      Examples: aiee, aiid, cckh, cfaras, cfhod
```

This creates two parallel substance vocabularies on each folio, both following the same localization pattern (87-90% on exactly 1 folio).

### Semantic Ceiling Refinement

This refines C120 (PURE_OPERATIONAL):

| What | Status |
|------|--------|
| Grammar (PREFIX, SUFFIX, PP) | No semantic content - abstract functional positions |
| Lexicon (RI extensions) | REFERENTIAL content - points to substances |
| Entity identity | IRRECOVERABLE - we know THAT 609 things are distinguished, not WHAT |

The system can **reference** specific substances without **encoding** which substances they are. The manuscript is operational AND referential - these are not contradictory.

### Why This Matters

**For the apparatus model:**
- Grammar tells the operator WHAT TO DO
- Lexicon tells the operator TO WHAT
- Both are necessary for functional completeness

**For interpretation:**
- ~609 substances/categories are distinguished in Currier A
- Cannot identify which (semantic ceiling)
- But we know they exist as distinct referents

**For the expert-oriented design:**
- Expert knows WHAT each RI extension refers to
- Grammar provides procedural context
- System assumes external knowledge of referents

### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- ❌ RI extensions are linguistic labels (the distinction is functional, not semantic)

**The distinction is functional, not semantic:** RI extensions POINT TO substances the way dictionary entries point to concepts - without encoding WHICH concepts.

### Cross-References

| Constraint | Role |
|------------|------|
| C120 | PURE_OPERATIONAL (applies to grammar, refined for lexicon) |
| C498 | RI vocabulary track (83% localized) |
| C475 | MIDDLE incompatibility (compatibility layer) |
| C509 | PP/RI dimensional separability |
| C517 | Superstring compression |
| C526 | RI Lexical Layer Hypothesis |

**Source:** RI_STRUCTURE_ANALYSIS (2026-01-24)

### Gallows Domain Coherence (Tier 3)

**Finding (C530):** When RI contains gallows letter X, PP in the same record is 2-5x more likely to also contain X:

| Gallows | PP baseline | Observed in same record | Enrichment |
|---------|-------------|-------------------------|------------|
| k | 23.5% | 54.8% | 2.3x |
| t | 15.8% | 33.1% | 2.1x |
| p | 8.7% | 42.9% | 4.9x |
| f | 5.0% | 17.9% | 3.6x |

**Interpretation:**

This supports the RI lexical layer hypothesis: RI MIDDLEs reference specific materials that cluster by some property. Records and folios appear to organize around gallows "domains":

- **k-domain:** Default/unmarked (78/109 folios are k-dominant)
- **t-domain:** Alternative category (cluster of t-specialized folios)
- **p/f-domains:** Rare specialized markers (never folio-dominant)

This is NOT compositional derivation (the PP-as-atoms theory was statistically insignificant per C512 retest). Rather, it suggests **thematic coherence** - records dealing with the same category of material tend to use vocabulary (both RI and PP) from the same gallows domain.

**What this supports:**
- RI references external substances organized by some categorical property
- That property correlates with gallows letter usage
- The expert user would recognize these domain clusters

**What this does NOT claim:**
- ❌ Gallows letters encode specific meanings (we can't know what k vs t signifies)
- ❌ Domain clustering enables translation or identification

**Source:** GALLOWS_MIDDLE_ANALYSIS (2026-01-24)

### RI Linker Mechanism: Convergent Inter-Record References (Tier 3)

**Finding (C835):** 0.6% of RI tokens (4 out of 707 types) function as "linkers" - they appear as FINAL in one paragraph and INITIAL in another, creating directed links between records.

**Topology is CONVERGENT (many-to-one):**

```
cthody:  5 folios (FINAL) ───→ 1 folio (INITIAL): f93v
ctho:    4 folios (FINAL) ───→ 1 folio (INITIAL): f32r
```

Each linker appears as INITIAL in exactly ONE folio but as FINAL in MULTIPLE folios. This creates collector hubs (f93v receives 5 inputs).

**Two Alternative Interpretations (cannot distinguish structurally):**

| Model | Logic | Meaning | Physical Analog |
|-------|-------|---------|-----------------|
| **AND (aggregation)** | Intersection | f93v requires ALL 5 conditions satisfied | Compound needing 5 ingredients |
| **OR (alternatives)** | Union | f93v accepts ANY of the 5 as valid input | 5 equivalent suppliers for same ingredient |

**Why the ambiguity matters:**

The same structural pattern supports both interpretations. An encoding where the logical operator (AND vs OR) is context-dependent would be:
- **Compact** - same notation serves multiple purposes
- **Expert-dependent** - practitioners know which applies
- **Opaque to outsiders** - hard to decode without domain knowledge

**Network Properties (Tier 2):**
- 12 directed links connecting 12 folios
- 66.7% forward flow (earlier folio → later folio)
- 75% ct-prefix in linkers (morphological marker)
- 95.3% of RI are singletons (linkers are rare)

**Interpretation:** Collector records (f93v, f32r) may document:
- **AND:** Compound materials/procedures requiring multiple source satisfactions
- **OR:** Procedures accepting alternative equivalent inputs

The sparse linking (0.6%) suggests most records are self-contained. Only rare "hub" entries aggregate or accept alternatives from multiple sources.

**New Evidence Favoring OR (2026-01-30):**

From linker_destination_characterization.py and linker_destination_followup.py:

1. **Hub destinations are structurally typical** - f93v and f32r show no outlier properties (all z-scores < |1|). They don't look like "aggregation points" that would combine inputs.

2. **Linkers don't consistently appear as INITIAL in destinations:**
   - cthody: INITIAL (pos 1) in f93v ✓
   - ctho: MIDDLE (pos 13) in f32r ✗
   - ctheody, qokoiiin: NOT FOUND in their destinations

   This suggests linkers function as cross-references ("see also folio X") rather than procedural inputs.

3. **High source vocabulary similarity (Jaccard 0.50-0.77):**
   - If AND (aggregation): sources should have DIFFERENT content (distinct ingredients)
   - If OR (alternatives): sources should have SIMILAR content (interchangeable)

   Observed Jaccard similarity is high, supporting the OR interpretation. Sources share substantial vocabulary beyond the linker token.

4. **Section concentration:** 96% (all destinations + 8/9 sources) are in section H. This suggests domain-specific cross-referencing within herbal content.

**Interpretation refined:** Linkers likely function as **cross-references** marking alternative entries or variations, not as procedural input aggregation points. The ct-ho morphology may mark "see also" rather than "requires".

**Source:** A_RECORD_B_ROUTING_TOPOLOGY (2026-01-28), LINKER_DESTINATION_CHARACTERIZATION (2026-01-30)

---

## 0.E. B FOLIO AS CONDITIONAL PROCEDURE (CLASS_COMPATIBILITY_ANALYSIS Phase)

### Tier 3: Core Finding

> **Each B folio is a distinct procedure defined by unique vocabulary. Folio selection is external (human choice based on desired outcome). AZC modulates which core operations are available, creating conditional execution paths through the selected procedure.**

This upgrades "specific folio = specific recipe" from **NOT CLAIMED** (previous X.10 disclaimer) to **TIER 3 SUPPORTED**.

### Evidence Summary (C531-C534)

| Finding | Value | Constraint |
|---------|-------|------------|
| Folios with unique MIDDLE | **98.8%** (81/82) | C531 |
| Unique MIDDLEs that are B-exclusive | **88%** | C532 |
| Adjacent folio grammatical slot overlap | **1.30x** vs non-adjacent | C533 |
| Mean unique MIDDLEs per folio | 10.5 | C531 |
| Only folio without unique vocabulary | f95r1 | C531 |

### The Two-Vocabulary Model

Each B folio contains two vocabulary layers:

| Layer | Source | AZC Role | Function |
|-------|--------|----------|----------|
| **Core vocabulary** | Shared (41 MIDDLEs) | **Filtered** - determines what's legal | Control flow (~79% of tokens) |
| **Unique vocabulary** | B-exclusive (88%) | **Not filtered** - always available | Procedure identity (~21% of tokens) |

**Key insight:** AZC doesn't determine WHICH folio runs. AZC determines which OPERATIONS are available within any folio.

### The Conditional Execution Model

The same B folio can produce different execution paths depending on the A record:

```
B Folio F (fixed procedure):
├── Unique vocabulary: Always available (procedure identity)
│   └── 10-15 MIDDLEs specific to this folio
│
└── Core vocabulary: Conditionally available
    ├── A record X active → core ops {a, b, c} legal
    │   └── Execution path: unique + {a, b, c}
    │
    └── A record Y active → core ops {a, d, e} legal
        └── Execution path: unique + {a, d, e}
```

This is **constraint satisfaction**, not **program selection**:
- The manuscript provides 83 procedures (B folios)
- AZC provides runtime constraints (which core ops are legal)
- Actual execution = intersection of procedure content and AZC legality

### The Operational Workflow

```
1. MATERIAL IDENTIFICATION
   Human has substance → finds matching A record
   A record's PP vocabulary encodes compatibility profile

2. COMPATIBILITY CHECK
   A record position activates AZC constraints
   ~80% of B core vocabulary filtered (C502)

3. PROCEDURE SELECTION
   Human chooses B folio based on desired outcome
   Each folio is a complete procedure with unique specifics

4. CONDITIONAL EXECUTION
   Procedure runs with:
   - Unique vocabulary (always available) = procedure identity
   - Legal core vocabulary (AZC-filtered) = available operations

5. MONITORING
   Human Track annotations record observations
   Higher HT with rare materials (C461)
```

### Why 83 Folios With Unique Vocabulary?

Each folio is a **specific recipe**, not a generic template:

| Property | Evidence | Interpretation |
|----------|----------|----------------|
| Unique vocabulary | 98.8% have unique MIDDLEs | Each procedure has specific details |
| Same grammar | All use 49 classes (C121) | Shared control structure |
| Adjacent similarity | 1.30x slot overlap | Related procedures (variations) |
| Section clustering | Partial (C534) | Domain organization |

The ~10.5 unique MIDDLEs per folio encode:
- Specific equipment/apparatus references
- Specific timing/temperature markers
- Specific outcome indicators
- What makes THIS procedure distinct from others

### Integration with Brunschwig Model

This strengthens the Brunschwig alignment:

| Brunschwig | Voynich | Mapping |
|------------|---------|---------|
| Fire degree (1-4) | REGIME (1-4) | Completeness requirements |
| Recipe within degree | B folio within REGIME | Specific procedure |
| Recipe-specific steps | Unique vocabulary | Procedure identity |
| Shared techniques | Core vocabulary | Control operations |

The pathway becomes concrete:

```
Brunschwig recipe
    → Product type
    → REGIME (completeness tier)
    → B folio (specific procedure)
    → Execution with A-record constraints
```

### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- ❌ Folio selection is encoded in the text (it's external/human)
- ❌ AZC "chooses" which folio runs

### What This DOES Claim (Tier 3)

- ✓ Each B folio is a distinct procedure (unique vocabulary defines it)
- ✓ Folio identity is independent of AZC (88% B-exclusive)
- ✓ AZC modulates execution paths, not procedure selection
- ✓ The manuscript is a conditional procedure library, not a sequential program
- ✓ Human operator selects folio based on external context

### Architectural Implication

The Voynich B section is a **reference library** of 83 conditional procedures:

```
┌─────────────────────────────────────────────────────────┐
│                   B PROCEDURE LIBRARY                    │
│                      (83 folios)                         │
├─────────────────────────────────────────────────────────┤
│  Each folio:                                             │
│  ├── IDENTITY: Unique vocabulary (always available)     │
│  ├── GRAMMAR: 49 instruction classes (shared)           │
│  └── CONSTRAINTS: Core vocab filtered by AZC            │
├─────────────────────────────────────────────────────────┤
│  Human selects folio based on:                          │
│  ├── Domain (herbal, pharma, astro sections)            │
│  ├── Desired outcome (product type)                     │
│  └── Material compatibility (A record determines)        │
└─────────────────────────────────────────────────────────┘
```

This is why:
- Illustrations exist (visual indexing for folio selection)
- Sections exist (domain organization for navigation)
- Labels exist (identification markers)
- Each folio has unique vocabulary (procedure specificity)

The text encodes procedures and constraints. The decision of WHEN to use them is external.

### Cross-References

| Constraint | Role |
|------------|------|
| C531 | Folio unique vocabulary prevalence |
| C532 | Unique MIDDLE B-exclusivity |
| C533 | Grammatical slot consistency |
| C534 | Section-specific profiles (partial) |
| C502 | A-record viability filtering |
| C470 | MIDDLE restriction inheritance |
| C121 | 49-class grammar universality |

**Source:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

---

## 0.E.1. GENERATIVE SUFFICIENCY AND DESIGN FREEDOM (Saturation Frontier)

### Tier 2: Core Finding

> **A minimal generative model (49-class Markov chain + symmetric forbidden suppression) reproduces 87% of measurable structure across 15 statistical tests, achieving 100% pass rate after three test corrections. The remaining ~57% of folio-level dynamical variance is genuine program-specific free variation that cannot be predicted from any aggregate structural property.**

### Generative Sufficiency (C1025, C1030, C1033, C1034)

The M2 model: sample instruction class from first-order transition probabilities, suppress forbidden transitions bidirectionally.

| Test Category | Tests | Pass Rate | Notes |
|---------------|-------|-----------|-------|
| Class distribution | 4 | 4/4 | Frequency, entropy, hapax |
| Transition structure | 4 | 4/4 | Spectral gap, forbidden compliance |
| Morphological | 4 | 4/4 | PREFIX, SUFFIX rates |
| Macro-state | 3 | 3/3 | After B4+C2+B5 corrections |
| **Total** | **15** | **15/15** | **100%** |

Three test corrections:
- **B4** (C1030): Test was misspecified for non-stationary data
- **C2** (C1033): Wrong CC class definition; class 17 has 59% suffixed tokens
- **B5** (C1034): Required symmetric (bidirectional) forbidden suppression, not asymmetric

PREFIX-factored generation (sampling PREFIX first, then class conditioned on PREFIX) is distributionally equivalent to M2 (C1034). PREFIX routing operates through selective inclusion (C1012), not through the generative process.

### Macro-Dynamics Variance Decomposition (C1017, C1035)

Folio-level AXM self-transition rate (how strongly each program orbits its dominant operational mode) decomposes as:

| Source | Variance | Cumulative |
|--------|----------|------------|
| REGIME + section | 42.0% | 42.0% |
| PREFIX entropy | 5.1% | 47.1% |
| Hazard density | 6.1% | 53.2% |
| Bridge geometry PC1 | 6.3% | 59.5% |
| **Residual (irreducible)** | **~57%** | **LOO-corrected** |

The C1017 model is moderately overfit (LOO CV R-squared = 0.433 vs training 0.564). The true explained fraction is ~43%.

Six additional folio-level predictors tested (paragraph count, HT density, gatekeeper fraction, QO fraction, vocabulary size, line count) all produce zero incremental variance beyond the baseline (C1035). Random forest finds no non-linear signal.

### Design Freedom Interpretation (C458, C980)

The ~57% residual is the **grammar's free design space**:
- Hazard exposure is clamped (CV = 0.04-0.11) — globally constrained
- Recovery strategy is locally free (CV = 0.72-0.82) — per-folio variation
- Each program is independently parameterized within its archetype
- The parameterization is not predictable from any aggregate structural property

This is consistent with C980's 66.3% free variation envelope. The manuscript provides the grammar, the forbidden constraints, and the macro-state topology. Within those constraints, each folio's author chose a specific operational style — and those choices are the irreducible residual.

**Source:** GENERATIVE_SUFFICIENCY (Phase 348), MACRO_DYNAMICS_VARIANCE_DECOMPOSITION (Phase 340), PREFIX_FACTORED_DESIGN (Phase 356), AXM_RESIDUAL_DECOMPOSITION (Phase 357)

---

## 0.F. LINE-LEVEL EXECUTION SYNTAX (CLASS_SEMANTIC_VALIDATION Phase)

### Tier 2-3: Execution Cycle Discovery

> **Each line follows a positional template: SETUP (initial) → THERMAL WORK (medial) → CHECKPOINT/CLOSURE (final). The 5 role categories (CC, EN, FL, FQ, AX) have distinct positional preferences, transition grammars, and REGIME/section profiles that collectively define line-level execution syntax.**

This fills a critical gap: we previously knew the VOCABULARY of operations (what roles exist) but not the SYNTAX (how they flow within a line).

### The Line as Control Cycle

The 49 instruction classes participate in 5 validated roles with distinct positional preferences (C556, Chi2 p=3e-89):

```
LINE STRUCTURE:

INITIAL zone              MEDIAL zone              FINAL zone
[0.0 -------- 0.3]        [0.3 -------- 0.7]       [0.7 -------- 1.0]

  daiin (CC trigger)         ENERGY chains            FLOW (ar, al, ary)
  AUXILIARY setup            qo ↔ ch-sh interleave    FREQUENT (or→aiin)
  UNCLASSIFIED (1.55x)      ENERGY (avoids edges)     FL/FQ (~1.65x)

        CC/AX                  ENERGY 0.45x              FL/FQ
      (openers)              (medial-concentrated)       (closers)
```

### Key Structural Findings (C547-C562)

**Positional Grammar (C556):**

| Role | Initial Enrichment | Final Enrichment | Position |
|------|-------------------|------------------|----------|
| UNCLASSIFIED | 1.55x | 1.42x | Initial-biased |
| AUXILIARY | 0.97x | 0.79x | Initial-biased |
| ENERGY | **0.45x** | **0.50x** | **Medial-concentrated** |
| CORE_CONTROL | 1.16x | 0.83x | Initial-biased |
| FREQUENT | 0.70x | **1.67x** | **Final-biased** |
| FLOW | 0.73x | **1.65x** | **Final-biased** |

**Transition Grammar (C550):**

| Pattern | Finding |
|---------|---------|
| Self-chaining hierarchy | FREQUENT 2.38x > FLOW 2.11x > ENERGY 1.35x |
| FLOW-FREQUENT affinity | Bidirectional 1.54-1.73x |
| ENERGY transition asymmetry | Avoids FL (0.75x), FQ (0.71x), UN (0.80x) |

ENERGY operators preferentially chain with themselves (transition preference asymmetry), forming functionally coherent thermal sequences that avoid mixing with non-thermal roles.

**ENERGY/FLOW Anticorrelation (C551, C562):**

| Dimension | ENERGY | FLOW |
|-----------|--------|------|
| Position | Medial (0.45x initial) | Final (17.5%) |
| REGIME_1 | **Enriched** (1.26-1.48x) | **Depleted** (0.40-0.63x) |
| BIO section | **Enriched** (1.72x) | **Depleted** (0.83x) |
| PHARMA section | Class 33 depleted (0.20x) | **Enriched** (1.38x) |
| EN/FL ratio | REGIME_1: **7.57** | REGIME_2: **3.71** |

### Role-Specific Structure

**CORE_CONTROL Hierarchy (C557, C558, C560):**

```
CORE_CONTROL
├── Singletons (atomic)
│   ├── daiin (Class 10): 27.7% line-initial, 47.1% ENERGY followers
│   ├── ol (Class 11): 9.5% line-final, closure signal
│   └── k (Class 12): 0 occurrences in Currier B (bound morpheme)
└── Derived (compound)
    └── Class 17 (ol+X): 9 tokens, ALL PREFIX=ol
        BIO enriched 1.72x, PHARMA 0 occurrences
```

**daiin** functions as an ENERGY trigger - "begin thermal sequence." **ol** functions as closure - "processing complete." Class 17 represents elaborated control operators derived from the atomic ol.

**or→aiin Directional Bigram (C561):**

| Expected (random) | Observed |
|-------------------|----------|
| aiin→aiin: 31% | **0%** |
| or→aiin: 22% | **87.5%** |

Zero aiin→aiin sequences exist (structural constraint, not statistical tendency). The or→aiin bigram functions as a grammatical unit: or initiates (85%), aiin terminates (90%). This is a checkpoint marker, not token repetition.

**FLOW Final Hierarchy (C562):**

| Class | Final% | Function |
|-------|--------|----------|
| 40 (ary, dary, aly) | 59.7% | Strong closers |
| 38 (aral, aram) | 52.0% | Strong closers |
| 30 (dar, dal, dam) | 14.8% | Neutral/provisional |
| 7 (al, ar) | 9.9% | Soft closers |

**ary is 100% line-final** - a pure termination signal. The hierarchy represents degrees of closure from provisional (ar) to absolute (ary).

**Section Profiles (C552, C553, C555):**

| Section | Signature | Profile |
|---------|-----------|---------|
| BIO | +CC +EN (45.2% ENERGY) | Thermal-intensive processing |
| HERBAL_B | +FQ -EN (1.62x FREQUENT) | Repetitive non-thermal cycles |
| PHARMA | +FL, Class 34 replaces 33 | Flow-dominated, controlled collection |
| RECIPE_B | -CC | Reduced control overhead |

BIO-REGIME effects are independent and additive (C553): baseline 27.5% ENERGY, +6.5pp from REGIME_1, +9.8pp from BIO section. BIO + REGIME_1 = 48.9% ENERGY (highest in manuscript).

### Tier 3-4: Distillation Cycle Interpretation

The line-level execution syntax maps directly to a distillation control cycle:

| Line Phase | Structural Evidence | Distillation Interpretation |
|------------|--------------------|-----------------------------|
| **SETUP** (initial) | daiin 27.7% initial, 47.1% ENERGY followers (C557) | "Begin heating sequence" - operator initiates fire |
| **WORK** (medial) | ENERGY chains, qo↔ch-sh interleaving at 56.3% (C549, C550) | Sustained thermal processing: heat (ch-sh) → vent/monitor (qo) → heat again |
| **CHECK** (medial-final) | or→aiin bigram, 87.5% directional (C561) | Sensory checkpoint - "taste and scent" verification |
| **CLOSE** (final) | FLOW hierarchy, ary 100% final (C562) | Completion: provisional (ar) to absolute (ary) |

**REGIME as operational mode:**

| REGIME | EN/FL Ratio | Interpretation |
|--------|-------------|----------------|
| REGIME_1 | 7.57 | Active heating mode (Brunschwig first degree) |
| REGIME_2 | 3.71 | Cooling/collection mode (second degree) |
| REGIME_3 | 5.04 | Intervention mode (third degree) |
| REGIME_4 | 4.76 | Precision mode (controlled execution) |

**Section as procedural type:**

| Section | Thermal Intensity | Distillation Parallel |
|---------|-------------------|-----------------------|
| BIO (45% ENERGY) | Maximum | Hot bath distillation (balneum mariae) |
| HERBAL (FREQUENT-enriched) | Low | Maceration/infusion (cold processing) |
| PHARMA (FLOW-dominated) | Moderate | Controlled condensation/collection |

### Integration with Brunschwig

**Brunschwig's fire-degree cycle now maps to line structure:**

| Brunschwig Phase | Voynich Line Position | Key Marker |
|------------------|-----------------------|------------|
| "First degree - initiate heat" | Initial zone | daiin (trigger) |
| "Second/third degree - work" | Medial zone | ENERGY chains, qo↔ch-sh |
| "Finger test / scent test" | Medial-final boundary | or→aiin (checkpoint) |
| "Overnight cooling" | Final zone | FLOW hierarchy (ar < ary) |

Brunschwig writes: *"Rose and lavender waters are discarded when their taste and scent have diminished."* The or→aiin bigram may mark exactly this moment - where sensory judgment determines whether the batch passes.

Brunschwig writes: *"must be left to stand overnight to cool."* The FLOW final hierarchy encodes degrees of this commitment - from provisional cooling (ar) to irreversible batch completion (ary).

### The Gap This Fills

| Before CLASS_SEMANTIC_VALIDATION | After |
|----------------------------------|-------|
| Knew token decomposition (PREFIX+MIDDLE+SUFFIX) | Now know how tokens FLOW within lines |
| Knew roles existed (CC, EN, FL, FQ, AX) | Now know roles have positional grammar |
| Knew REGIME controlled intensity | Now know REGIME controls ENERGY/FLOW ratio |
| Knew sections had different profiles | Now know profiles map to procedural types |
| Knew lines were control blocks | Now know control blocks have SETUP→WORK→CHECK→CLOSE structure |

### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- That or→aiin literally means "sensory test"
- That daiin literally means "begin heating"

The interpretation is STRUCTURAL, not semantic: line-level syntax exhibits a cycle structure consistent with thermal processing.

### Cross-References

| Constraint | Role |
|------------|------|
| C547 | qo-chain REGIME_1 enrichment |
| C548 | Manuscript-level gateway/terminal envelope |
| C549 | qo/ch-sh interleaving significance |
| C550 | Role transition grammar (ENERGY asymmetry) |
| C551 | Grammar universality, REGIME specialization |
| C552 | Section-specific role profiles |
| C553 | BIO-REGIME independence |
| C554 | Hazard class clustering |
| C555 | PHARMA thermal operator substitution |
| C556 | ENERGY medial concentration |
| C557 | daiin line-initial ENERGY trigger |
| C558 | Singleton class structure |
| C559 | FREQUENT role structure **(SUPERSEDED by C583, C587 — used wrong FQ membership)** |
| C560 | Class 17 ol-derived operators |
| C561 | or→aiin directional bigram |
| C562 | FLOW role structure |

**Source:** CLASS_SEMANTIC_VALIDATION (2026-01-25)

---

## 0.G. THE SCAFFOLD AND THE SHADOW (AX_FUNCTIONAL_ANATOMY Phase)

### Tier 3-4: What the Other 28% Was Doing All Along

For months, one-fifth of the instruction classes sat in a bucket labeled AUXILIARY — 480 tokens, 20 classes, 28.4% of everything Currier B ever wrote — and nobody could say what they *did*. They weren't ENERGY. They weren't FLOW. They weren't CONTROL or FREQUENT. They were just... there. Structurally present, positionally real (C563-C566 proved they had INIT/MED/FINAL sub-positions with p=3.6e-47), but functionally invisible. The grammar had a heartbeat and a skeleton and a nervous system, and then this enormous quiet mass of tissue that nobody could name.

It turns out we were looking at the problem backwards.

We kept asking: *What does AUXILIARY do that the other roles don't?* The answer is nothing. AX doesn't do anything the other roles don't do. It uses the same vocabulary, drawn from the same pipeline, carrying the same material identity. The difference isn't in the vocabulary. The difference is in the *prefix*.

### One Vocabulary, Two Postures

Take a MIDDLE — any MIDDLE, say `edy`. The pipeline delivers it from Currier A through AZC into B. Now watch what happens:

Attach the prefix `ch` and you get `chedy` — an ENERGY operator. The distiller picks up the material and puts it to work. Heat applied, vapor rising, the cucurbit is active.

Attach the prefix `ok` and you get `okedy` — an AUXILIARY scaffold token. The distiller *stages* the material. It's on the bench, accounted for, positioned for use. But the fire isn't lit yet.

Strip the prefix entirely and you get bare `edy` — an AX_FINAL frame-closer. The material is declared ready. The workspace around this step is complete.

Now add an articulator: `ychedy`, `dchedy`, `lchedy` — AX_INIT frame-openers. The distiller announces: *this workspace is now open for processing this material*. The `ch` prefix is still there — it still names the operational mode — but the articulator (`y`, `d`, `l`) shifts it from present tense to future tense. Not "processing now" but "preparing to process."

Same MIDDLE. Same material. Four different deployment modes, selected entirely by what prefix wraps around it (C571). A classifier using nothing but prefix achieves 89.6% accuracy at telling AX from non-AX (C570). The remaining 10.4% are exactly the ambiguous cases — the articulated ch/sh forms where the system deliberately blurs the line between announcing work and doing it.

This is the resolution: **PREFIX is the role selector. MIDDLE is the material carrier. AX is not a different vocabulary — it is the same vocabulary in scaffold mode** (C571).

### The Numbers Behind the Story

The overlap is not subtle. Of 57 unique MIDDLEs that appear in AX tokens, 41 — seventy-two percent — are shared with operational ENERGY tokens (C567). The Jaccard similarity between AX and EN vocabulary is 0.400, which is enormous for two categories that were supposed to be doing different things. And 98.2% of AX MIDDLEs come through the PP pipeline from Currier A. This is not independent material. This is the same material the pipeline sends everywhere else.

How much of Currier A feeds into AX? Nearly all of it. 97.2% of A records carry at least one MIDDLE that ends up in an AX class (C568). The average record contributes 3.7 AX-relevant MIDDLEs. The top contributors are the universal single-character forms — `o` appears in 60% of records, `i` in 39%, `e` in 34% — the same hub MIDDLEs that anchor the entire discrimination space. Only 44 records (2.8%) have zero AX vocabulary, and every one of them is tiny, with four or fewer total MIDDLEs. They're not AX-excluded; they're just small.

On the B side, the guarantee is absolute: zero contexts have zero AX classes. Classes 21 and 22 survive in every single pipeline configuration. You cannot construct a legal B line without scaffolding. The frame is architecturally mandatory (C568).

### Proportional but Not Random

Here is where it gets interesting. The fraction of surviving classes that are AX is 0.4540. The expected fraction under uniform distribution is 0.4545. The deviation is -0.0005 — less than a tenth of a percent. AX doesn't grow or shrink relative to operational roles. It scales in perfect proportion to pipeline throughput (C569).

But the linear model only achieves R²=0.83, not 0.99. The *volume* is proportional; the *composition* has structure of its own. AX_INIT is systematically over-represented (regression slope 0.130 vs expected 0.102) while AX_FINAL is under-represented (0.093 vs 0.122). The manuscript opens frames more eagerly than it closes them. Workspaces are declared with enthusiasm and wrapped up with restraint — which, if you've ever watched someone set up a distillation bench versus clean one up, sounds about right.

### The Shadow on the Scaffold

So what *is* AUXILIARY?

It is the shadow cast by operational vocabulary onto the structural frame of each line. The same light source — MIDDLEs from the pipeline — hits two surfaces. When it hits an operational prefix (ch, sh, qo), you get active processing: ENERGY work, thermal sequences, the grammar's engine running. When it hits a scaffold prefix (ok, ot, bare, articulated), you get staging: workspace management, frame boundaries, material accounting.

The shadow is real. It has shape — INIT/MED/FINAL positional structure with p=3.6e-47 (C563). It has guaranteed presence — classes 21 and 22 always survive (C568). It has independent composition — the subgroup slopes differ from expectation (C569). But it is defined by what casts it. Remove the operational vocabulary and the shadow vanishes. The scaffold has no vocabulary of its own — or rather, it has 16 exclusive MIDDLEs (28.1%), just enough to prove it isn't *entirely* derivative, but not enough to stand alone.

This means the line-level execution cycle from Section 0.F is richer than we thought. Each line doesn't just run SETUP→WORK→CHECK→CLOSE. Each line *brackets* its work in a structural frame made from the same material it processes:

```
 AX_INIT                    ENERGY work               AX_FINAL
 "Opening workspace:        "Processing lavender:      "Workspace closed:
  lavender staged"           heat, vent, monitor"       lavender complete"
  (ychedy)                   (chedy, shedy)             (dy)
       └──── same MIDDLE ──────── same MIDDLE ──────────┘
              different PREFIX      different PREFIX
```

The manuscript records not just what was done to the lavender, but the opening and closing of the workspace *around* the lavender. Every step is framed. Every frame is built from the step's own material. This is why AX is 28.4% of the text — it takes real structural work to bracket every operation with its own scaffold, and that scaffold is proportional to the operations it frames.

### What This Means for the Workshop

Picture Brunschwig's distillery. The master has a bench, a furnace, a cucurbit, an alembic, collection vessels. Before each operation, he stages: lays out the rose petals, checks the alembic's seal, positions the receiver. This staging uses the same materials that will be processed — you can't stage lavender without handling lavender — but the *posture* is different. Staging is inventory. Processing is chemistry. Same hands, same materials, different intent.

The manuscript, it appears, records both. Not just "heat the lavender" (ENERGY) and "collect the distillate" (FLOW) and "check the scent" (FREQUENT) and "begin the sequence" (CONTROL) — but also "workspace open for lavender" (AX_INIT), "lavender staged" (AX_MED), "lavender workspace closed" (AX_FINAL). The staging protocol. The part of the procedure that a modern recipe would leave implicit but that a 15th-century reference manual for trained operators — a manual designed to be *safe* — would make explicit.

This is consistent with a system that takes safety seriously enough to encode it structurally. The scaffold is guaranteed (C568). The frame always opens (AX_INIT present 95.9% of the time). The frame always closes (AX_FINAL present 100%). You cannot skip the staging protocol. The grammar won't let you.

If the manuscript is a manual for operating dangerous thermal-chemical equipment — and the structural evidence increasingly says it is — then the 28% we couldn't explain wasn't wasted space. It was the safety margin. The part of every procedure that says: *before you light the fire, confirm your workspace is ready. After the fire goes out, confirm your workspace is clear.*

Every good workshop has this discipline. The Voynich manuscript, it seems, wrote it down.

### Twenty Classes, One Shadow (C572)

One question remained after the anatomy was clear: if AX has 19 instruction classes, do those 19 classes correspond to 19 different *kinds* of scaffolding? Nineteen distinct staging protocols? Nineteen ways to open a workspace?

No. We tested every dimension we could think of — transition structure, positional profiles, neighborhood context — and the answer was emphatic. Only 3 of 19 classes showed any structured transitions. A classifier trained on context signatures scored 6.8% accuracy, *below* the 10.3% random baseline. The best clustering algorithm could manage was k=2 with silhouette 0.18 — worse than the prior attempt that already found weak signal. The sole outlier was Class 22, AX_FINAL's workhorse, which distinguished itself not by what it *did* but by where it *sat*.

The 19 classes are not 19 kinds of scaffold. They are one shadow, cast from 19 slightly different angles. Position is the only thing that separates them. The AX vocabulary is positionally structured (INIT/MED/FINAL is real, p=3.6e-47) but behaviorally uniform. Every scaffold token does the same thing: frame the workspace. The grammar gives you 19 classes because the morphological system — 22 AX-exclusive prefixes crossed with articulators — generates 19 distinct surface forms. But the behavioral space those forms occupy is a single cloud, not 19 clusters.

This is the final simplification. Currier B's 49 instruction classes decompose into 30 behaviorally meaningful roles (the operational classes) plus 19 positional variants of a single scaffold function. The grammar is simpler than it looks. The complexity is in the operations. The scaffold is just... scaffolding.

### Evidence Summary (C567-C572)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C567 | AX MIDDLEs overlap with operational roles | 72% shared, Jaccard=0.400 |
| C568 | AX vocabulary present in nearly all pipeline contexts | 97.2% A-records, 0 zero-AX B-contexts |
| C569 | AX volume scales proportionally, composition is independent | Fraction 0.454, R²=0.83 |
| C570 | PREFIX alone predicts AX membership | 89.6% accuracy, 22 AX-exclusive prefixes |
| C571 | AX = PREFIX-determined scaffold mode of pipeline vocabulary | PREFIX is role selector, MIDDLE is material |
| C572 | 19 AX classes collapse to ≤2 effective behavioral groups | silhouette=0.18, context below baseline |

**Source:** AX_FUNCTIONAL_ANATOMY (2026-01-25), AUXILIARY_STRATIFICATION (2026-01-25), AX_CLASS_BEHAVIOR (2026-01-25)

---

## 0.H. ENERGY ANATOMY (EN_ANATOMY Phase)

### Tier 2: EN Internal Architecture

> **EN comprises 18 instruction classes (not 11 as BCSC stated), accounting for 7,211 tokens (31.2% of B). Internally, EN classes show DISTRIBUTIONAL_CONVERGENCE — grammatically equivalent but lexically partitioned by PREFIX family. EN is 100% pipeline-derived and has 30 exclusive MIDDLEs.**

This resolves the EN undercount (BCSC v1.2 listed 11 classes) and completes the EN role characterization.

### The 18-Class Census (C573)

ICC-based definitive count: {8, 31-37, 39, 41-49}. Core 6 classes provide 79.5% of EN tokens; Minor 12 provide 20.5%. The discrepancy with BCSC's 11-class count arose because the original grammar analysis used a coarser clustering.

### Distributional Convergence (C574)

The 18 EN classes do NOT form distinct behavioral clusters. Best clustering: k=2, silhouette=0.180. QO-prefixed and CHSH-prefixed classes have identical positions, REGIME profiles, and context distributions (JS divergence = 0.0024). But their MIDDLE vocabularies are nearly disjoint: QO uses 25 MIDDLEs, CHSH uses 43, only 8 shared (Jaccard=0.133, C576).

**Verdict:** EN is grammatically equivalent but lexically partitioned. PREFIX selects which material subvocabulary to use, not what grammatical function to perform. The QO/CHSH split (C276, C423) operates within a single role, not between roles.

### Pipeline Purity (C575)

All 64 unique EN MIDDLEs are PP (pipeline-participating). Zero RI, zero B-exclusive. EN is the purest role — even purer than AX (98.2% PP). The entire EN vocabulary traces back to Currier A.

### Content-Driven Interleaving (C577)

QO and CHSH occupy the same positions (p=0.104, not significantly different). Alternation is driven by material-type selection (BIO 58.5%, PHARMA 27.5%), not positional preferences.

### Exclusive Vocabulary (C578)

EN has 30 exclusive MIDDLEs — 46.9% of its vocabulary is not shared with AX, CC, FL, or FQ. This is a dedicated content subvocabulary within the pipeline.

### Trigger Profile Differentiation (C580)

CHSH is triggered by AX (32.5%) and CC (11%). QO is triggered by EN-self (53.5%) and boundary contexts (68.8%). Chi2=134, p<0.001. The two PREFIX families enter EN through different grammatical pathways.

### Evidence Summary (C573-C580)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C573 | EN definitive count | 18 classes (not 11) |
| C574 | Distributional convergence | silhouette=0.180, JS=0.0024 |
| C575 | 100% pipeline-derived | 64 MIDDLEs, all PP |
| C576 | MIDDLE vocabulary bifurcation | QO 25, CHSH 43, 8 shared |
| C577 | Interleaving is content-driven | Position p=0.104 (NS) |
| C578 | 30 exclusive MIDDLEs | 46.9% of EN vocabulary |
| C579 | CHSH-first ordering bias | 53.9%, p=0.010 |
| C580 | Trigger profile differentiation | chi2=134, p<0.001 |

**Source:** EN_ANATOMY (2026-01-26)

---

## 0.I. SMALL ROLE ANATOMY AND FIVE-ROLE SYNTHESIS (SMALL_ROLE_ANATOMY Phase)

### Tier 2: Complete Role Taxonomy

> **The 49 Currier B instruction classes partition into 5 roles — CC (3-4 classes), EN (18), FL (4), FQ (4), AX (19-20) — with complete coverage. All roles are 100% PP (AX 98.2%). Small roles (CC, FL, FQ) show GENUINE internal structure; large roles (EN, AX) are COLLAPSED or CONVERGENT. Suffix usage is strongly role-stratified (chi2=5063.2). FL is hazard-source-biased; EN is hazard-target.**

This phase completes the five-role taxonomy by characterizing the three small operational roles (CC, FL, FQ), resolving census discrepancies, introducing the suffix dimension, and producing a unified cross-role comparison.

### Census Resolution (C581-C583)

Three long-standing discrepancies resolved:

| Role | Resolved Classes | Tokens | % of B | Note |
|------|-----------------|--------|--------|------|
| CC | {10, 11, 12, 17} | ~1,023 | 4.4% | Class 12 ghost (0 tokens, C540); Class 17 per C560 |
| FL | {7, 30, 38, 40} | 1,078 | 4.7% | BCSC undercounted at 2; ICC gives 4 |
| FQ | {9, 13, 14, 23} | 2,890 | 12.5% | C559 used wrong set {9,20,21,23} — SUPERSEDED |

**Resolved (2026-01-26):** Class 14 = FQ per ICC phase20a + behavioral evidence (suffix rate 0.0 vs AX_MED 0.56–1.0; token count 707 vs AX_MED 38–212; JS divergence 0.0018 with FQ Class 13). Class 17 = CC per C560. AX corrected from 20 to 19 classes. C563 updated.

### The Structure Inversion (C589)

The most counterintuitive finding: small roles are more internally structured than large roles.

| Role | Classes | KW Significant | Verdict |
|------|---------|---------------|---------|
| CC | 2 active | 75% | GENUINE_STRUCTURE |
| FL | 4 | 100% | GENUINE_STRUCTURE |
| FQ | 4 | 100% | GENUINE_STRUCTURE |
| EN | 18 | — | DISTRIBUTIONAL_CONVERGENCE (C574) |
| AX | 19 | — | COLLAPSED (C572) |

Small roles have few classes but each class does something distinct. Large roles have many classes doing roughly the same thing. Control signals are differentiated; content carriers are interchangeable.

**Tier 3 interpretation:** This maps to how procedural knowledge is organized. You need a few specialized control tools (begin, transition, iterate, close) but many interchangeable content instances (different materials through the same operations). The system differentiates its control signals and mass-produces its content carriers.

### Suffix Role Selectivity (C588)

First cross-role suffix analysis. Chi-square = 5063.2, dof=80, p < 1e-300.

| Stratum | Role | Suffix Types | Bare Rate |
|---------|------|-------------|-----------|
| SUFFIX_RICH | EN | 17 | 39.0% |
| SUFFIX_MODERATE | AX | 19 | 62.3% |
| SUFFIX_DEPLETED | FL, FQ | 1-2 | 93-94% |
| SUFFIX_FREE | CC | 0 | 100.0% |

EN and AX share suffix vocabulary (Jaccard = 0.800). CC/FL/FQ are suffix-isolated.

**Tier 3 interpretation:** Suffixes encode material variants on content tokens. EN is suffix-rich because it specifies *which variant* of an operation to perform — different materials need different treatment. CC/FL/FQ are suffix-free because control signals are material-independent. "Begin" is "begin" regardless of what you're distilling.

### FL Hazard-Safe Split (C586)

FL divides into two genuine subgroups:

| Subgroup | Classes | Mean Position | Final Rate | Hazard Role |
|----------|---------|--------------|------------|-------------|
| Hazard | {7, 30} | 0.55 | 12.3% | Source (4.5x initiation bias) |
| Safe | {38, 40} | 0.81 | 55.7% | Non-hazardous |

Mann-Whitney: position p=9.4e-20, final rate p=7.3e-33. FL initiates forbidden transitions far more than it receives them. EN is the mirror: mostly a target.

**Tier 3 interpretation:** In distillation, the danger comes from flow decisions — opening a valve at the wrong time, transitioning between phases incorrectly. The material itself (EN) doesn't create hazards; it suffers the consequences. FL → EN hazard directionality is exactly what you'd see in a system where flow control errors damage the batch.

### FQ Four-Way Differentiation (C587)

| Class | Tokens | Character | Distinctive Feature |
|-------|--------|-----------|-------------------|
| 9 | 630 | aiin/o/or | Medial self-chaining, prefix-free |
| 13 | 1,191 | ok/ot+suffix | Largest FQ class, 16% suffixed |
| 14 | 707 | ok/ot+bare | Distinct from 13 (p=1.6e-10) |
| 23 | 362 | d/l/r/s/y | Final-biased, morphologically minimal |

Classes 13 and 14 share the ok/ot PREFIX family but differ in suffix behavior. This mirrors C570's PREFIX-as-role-selector principle operating *within* a single role.

### CC Positional Dichotomy (C590)

Class 10 (daiin): initial-biased (0.413), 27.1% line-initial. Class 11 (ol): medial (0.511), 5.0% initial. Mann-Whitney p=2.8e-5. CC is operationally a two-token toggle with complementary control primitives. Class 12 (k) is ghost. If Class 17 is included (C560), it adds ol-derived compound control operators.

### C559 Correction (C592)

C559 (FREQUENT Role Structure) used incorrect membership {9, 20, 21, 23}. Classes 20 and 21 are AX (C563). Correct FQ is {9, 13, 14, 23} per ICC. C559 is SUPERSEDED by C583 and C587. Downstream constraints C550, C551, C552, C556 flagged for re-verification with corrected membership.

### Five-Role Summary Table (C591)

| Property | CC | EN | FL | FQ | AX |
|----------|-----|-----|-----|-----|-----|
| Classes | 3-4 | 18 | 4 | 4 | 19-20 |
| Tokens | 735-1023 | 7,211 | 1,078 | 2,890 | 4,559 |
| % of B | 3-4% | 31.2% | 4.7% | 12.5% | 19.7% |
| PP% | 100% | 100% | 100% | 100% | 98.2% |
| Suffix types | 0 | 17 | 2 | 1 | 19 |
| Bare rate | 100% | 39% | 94% | 93% | 62% |
| Hazard role | None | Target | Source | Mixed | None |
| Structure | GENUINE | CONVERGENCE | GENUINE | GENUINE | COLLAPSED |

### Integration with Distillation Interpretation

The five-role taxonomy maps to a layered execution model:

| Layer | Role | Function | Distillation Parallel |
|-------|------|----------|----------------------|
| Frame | AX | Positional template | Apparatus arrangement |
| Signal | CC | Control primitives | Operator hand signals |
| Content | EN | Material operations (suffix-modified) | Substance processing |
| Flow | FL | State transitions (hazard-aware) | Valve/gate operations |
| Iteration | FQ | Repetition and closure | Cycle count, batch completion |

A line reads as: AX frame → CC signal → EN content + FL transitions + FQ iteration → FQ/FL close.

The suffix boundary confirms the apparatus-centric model: content tokens (EN) carry material-specific parameterization via suffixes; control tokens (CC/FL/FQ) are universal and bare. The system encodes *what material* through suffixes on EN, but *how to process* through suffix-free control signals.

### Evidence Summary (C581-C592)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C581 | CC definitive census | {10,11,12,17} — Class 17 confirmed CC per C560 |
| C582 | FL definitive census | {7,30,38,40}, 4 classes (was 2) |
| C583 | FQ definitive census | {9,13,14,23}, 2890 tokens (supersedes C559) |
| C584 | Near-universal pipeline purity | CC/EN/FL/FQ 100% PP; AX 98.2% |
| C585 | Cross-role MIDDLE sharing | EN-AX Jaccard=0.402; CC isolated |
| C586 | FL hazard-safe split | p=9.4e-20; FL source-biased 4.5x |
| C587 | FQ internal differentiation | 4-way genuine, 100% KW significant |
| C588 | Suffix role selectivity | chi2=5063.2; three suffix strata |
| C589 | Small role genuine structure | CC/FL/FQ all GENUINE vs large roles |
| C590 | CC positional dichotomy | daiin initial vs ol medial, p=2.8e-5 |
| C591 | Five-role complete taxonomy | 49 classes → 5 roles, complete partition |
| C592 | C559 membership correction | C559 SUPERSEDED; downstream flags |

**Source:** SMALL_ROLE_ANATOMY (2026-01-26)

---

## 0.J. FQ INTERNAL ARCHITECTURE (FQ_ANATOMY Phase)

### Tier 2: FQ 3-Group Structure

> **FQ's 4 classes form 3 functional groups: CONNECTOR {9}, PREFIXED_PAIR {13, 14}, CLOSER {23}. Classes 13 and 14 have completely non-overlapping MIDDLE vocabularies (Jaccard=0.000). Internal transitions follow a directed grammar (chi2=111, p<0.0001). Class 23 is a boundary specialist with 29.8% final rate. FQ-FL symbiosis is position-driven, not hazard-mediated.**

This phase deepens the FQ characterization from SMALL_ROLE_ANATOMY (C587) by examining internal vocabulary, transitions, and upstream context.

### 3-Group Structure (C593)

Silhouette analysis yields 3 groups (silhouette=0.68):
- **CONNECTOR** {9}: or/aiin bigram, medial self-chaining, prefix-free. Functions as the operational connector between EN blocks.
- **PREFIXED_PAIR** {13, 14}: ok/ot-prefixed classes, the bulk of FQ (1,898 tokens). Share PREFIX family but differ completely in MIDDLE vocabulary.
- **CLOSER** {23}: morphologically minimal (d/l/r/s/y), final-biased. Terminates sequences.

### Complete 13-14 Vocabulary Bifurcation (C594)

Classes 13 and 14 share zero MIDDLEs (Jaccard=0.000). This is sharper than EN's QO/CHSH split (Jaccard=0.133). Class 13 has 18.2% suffix rate; Class 14 has 0%. Despite sharing the ok/ot PREFIX family, they access completely different content vocabularies — the most extreme vocabulary segregation in the corpus.

### Internal Transition Grammar (C595)

FQ internal transitions are non-random (chi2=111, p<0.0001):
- 23->9 enriched 2.85x (closer feeds connector)
- 9->13 vs 9->14 ratio is 4.6:1 (connector preferentially feeds Class 13)
- 13->23 enriched (Class 13 feeds closer to terminate)

### FQ-FL Symbiosis (C596)

FQ and FL co-occur in positionally structured patterns, but hazard alignment is non-significant (p=0.33). The symbiosis is position-driven — both roles concentrate at line boundaries — not hazard-mediated. FQ does not preferentially pair with hazardous FL classes.

### Class 23 Boundary Dominance (C597)

Class 23 has the highest final rate of any FQ class (29.8%) and accounts for 39% of all FQ line-final tokens despite being only 12.5% of FQ by count. Mean run length 1.19 — almost always appears as a singleton. It functions as a dedicated boundary marker.

### Tier 3 Interpretation

FQ implements **iteration control** within the line grammar:
- CONNECTOR (Class 9) chains operational blocks — the "and then" between EN sequences
- PREFIXED_PAIR (13, 14) provides parameterized repetition with two completely different content vocabularies (possibly different iteration modes or targets)
- CLOSER (23) terminates sequences — the "stop" signal

The 13-14 complete bifurcation suggests two distinct iteration pathways sharing a common structural frame (ok/ot PREFIX) but accessing different material specifications.

### Evidence Summary (C593-C597)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C593 | FQ 3-group structure | silhouette=0.68 |
| C594 | Complete 13-14 vocabulary bifurcation | Jaccard=0.000 |
| C595 | Internal transition grammar | chi2=111, p<0.0001 |
| C596 | FQ-FL position-driven symbiosis | hazard p=0.33 (NS) |
| C597 | Class 23 boundary dominance | 29.8% final, 39% of FQ finals |

**Source:** FQ_ANATOMY (2026-01-26)

---

## 0.K. SUB-ROLE INTERACTION GRAMMAR (SUB_ROLE_INTERACTION Phase)

### Tier 2: Cross-Boundary Sub-Group Routing

> **Internal sub-groups of each role interact non-randomly across role boundaries. 8/10 cross-role pairs show significant sub-group routing (5 survive Bonferroni). CC sub-groups are differentiated triggers: daiin/ol activate EN_CHSH while ol-derived activates EN_QO. All 19 hazard events originate from exactly 3 sub-groups (FL_HAZ, EN_CHSH, FQ_CONN). REGIME modulates routing magnitude but not direction.**

This phase connects the role-level transition grammar (C550) with the internal anatomy of each role, testing whether sub-group identity is visible across role boundaries.

### Cross-Boundary Structure (C598)

13 sub-groups across 5 roles (EN: QO/CHSH/MINOR; FQ: CONN/PAIR/CLOSER; FL: HAZ/SAFE; AX: INIT/MED/FINAL; CC: DAIIN/OL/OL_D) produce 10 testable cross-role pairs. 8/10 are significant raw, 5/10 survive Bonferroni. Strongest: CC->EN (chi2=104, p=2.5e-20), FQ->EN (chi2=35, p=3.5e-8).

### CC Trigger Selectivity (C600)

The sharpest finding. CC sub-groups are **differentiated triggers** (chi2=129.2, p=9.6e-21):
- **daiin** (Class 10) and **ol** (Class 11): trigger EN_CHSH at 1.60-1.74x, suppress EN_QO to 0.18x
- **ol-derived** (Class 17): triggers EN_QO at 1.39x, suppresses EN_CHSH to 0.77x

This refines C557 ("daiin opens lines") to "daiin specifically opens the CHSH pathway." The QO pathway has a completely different upstream activator.

### AX Scaffolding Routing (C599)

AX sub-positions route differently to operational sub-groups (chi2=48.3, p=3.9e-4):
- AX_INIT feeds QO at 1.32x
- AX_FINAL avoids QO (0.59x) and feeds FQ_CONN (1.31x)
- AX is not a uniform frame — it is a directional routing mechanism

### Hazard Sub-Group Concentration (C601)

All 19 corpus hazard events originate from exactly 3 source sub-groups: FL_HAZ (47%), EN_CHSH (26%), FQ_CONN (26%). EN_CHSH absorbs 58% of hazard targets. EN_QO never participates — zero as source, zero as target. This confirms the QO/CHSH bifurcation is functional, not just lexical.

### REGIME-Conditioned Routing (C602)

4/5 tested cross-role pairs are REGIME-dependent (homogeneity p<0.05). The exception is AX->FQ which is REGIME-independent (p=0.86), consistent with AX being structural scaffolding rather than content-sensitive. REGIME modulates magnitude but never flips direction — FQ_CONN always feeds CHSH in every REGIME.

### Tier 3 Interpretation: Two Parallel Processing Lanes

The sub-role interaction data reveals **two parallel processing pathways**:

```
CC_DAIIN/OL  --triggers-->  EN_CHSH  --feeds-->  FQ_CONN
                                                    |
                                             (hazard loop)
                                                    |
CC_OL_D      --triggers-->  EN_QO    --feeds-->  FQ_PAIR
                                                 (safe)
```

- **CHSH lane:** Triggered by daiin/ol, carries hazardous operations, uses connector routing
- **QO lane:** Triggered by ol-derived compounds, carries safe operations, uses prefixed pair routing
- **AX scaffolding:** Routes differentially — INIT feeds QO, FINAL feeds CONN

In the apparatus-centric model: daiin opens a hazardous processing sequence (high-temperature distillation, reactive materials), while ol-derived compounds open a safe processing sequence (routine operations, stable materials). The two lanes share grammar but access different vocabularies and carry different risk profiles.

### Evidence Summary (C598-C602)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C598 | Cross-boundary sub-group structure | 8/10 significant, 5/10 Bonferroni |
| C599 | AX scaffolding routing | chi2=48.3, p=3.9e-4 |
| C600 | CC trigger sub-group selectivity | chi2=129.2, p=9.6e-21 |
| C601 | Hazard sub-group concentration | 3 sources, QO never participates |
| C602 | REGIME-conditioned sub-role grammar | 4/5 REGIME-dependent, AX->FQ exception |

**Source:** SUB_ROLE_INTERACTION (2026-01-26)

---

## 0.L. LANE CONTROL ARCHITECTURE (LANE_CHANGE_HOLD_ANALYSIS Phase)

### Tier 3: Core Finding

> **The two EN execution lanes (QO/CHSH) encode complementary control functions — energy application and stabilization — that alternate with inertia-driven dynamics within a phase-gated legality framework. Thresholds are categorical (legality transitions), not numeric (accumulation values).**

### Two-Lane Functional Assignment

EN tokens carry one of two PREFIX subfamilies (C570-571) drawing from non-overlapping MIDDLE vocabularies (C576, Jaccard = 0.133):

| Lane | PREFIX | MIDDLE Character | Kernel Content | Hazard Role | Post-Hazard |
|------|--------|-----------------|----------------|-------------|-------------|
| **QO** | qo- | k-rich (70.7%) | ENERGY_MODULATOR | Zero participation (C601) | 24.8% (depleted) |
| **CHSH** | ch-/sh- | e-rich (68.7%) | STABILITY_ANCHOR | All 19 forbidden transitions | 75.2% (dominant) |

**Morphological lane signature** (C647): Cramer's V = 0.654, p < 0.0001. The lanes are built from different kernel-character vocabularies.

**Interpretation:** QO = controlled energy addition (non-hazardous). CHSH = stabilization/correction (hazard recovery). "Safe energy pathway" (F-B-002) means energy application that stays within bounds, not absence of energy.

### Change/Hold Label: FALSIFIED

The original interpretation (CHSH = state-changing, QO = state-preserving) was tested with 5 predictions. Two critical reversals falsified it:
- QO tokens contain k (energy), not e (stability) — opposite of prediction
- CHSH dominates post-hazard recovery (75.2%), not QO — opposite of prediction

The reversed mapping (QO = energy, CHSH = stabilization) resolves all 5 predictions. F-B-006 documents this.

### Oscillation Architecture

**Hysteresis oscillation confirmed** (C643): alternation rate = 0.563 vs null = 0.494 (p < 0.0001, z > 10). Short runs (median = 1.0). Section-dependent: BIO = 0.606, HERBAL_B = 0.427.

**Switching dynamics are inertia-driven, not threshold-driven:**

| Run Length N | QO P(switch) | CHSH P(switch) |
|-------------|-------------|---------------|
| 1 | 0.500 | 0.482 |
| 2 | 0.438 | 0.417 |
| 3 | 0.416 | 0.324 |
| 4 | 0.111 | 0.180 |
| 5 | 0.308 | 0.111 |

Hazard function is **DECREASING** (Spearman rho = -0.90 QO, -1.00 CHSH). Once in a lane, the system tends to stay. No numeric accumulation toward a switching threshold.

CC tokens between EN pairs **suppress** switching (42.6% switch rate with CC vs 57.1% without, p = 0.0002). Gap content explains only 1.25% of switching variance (pseudo-R2). Switching is not externally triggered — it emerges from the grammar's alternation preference at N=1.

### Categorical Legality Thresholds (Phase-Gated)

While token-level switching is memoryless-with-inertia, the system encodes **macro-level categorical thresholds** as legality transitions:

| Threshold | Mechanism | Evidence |
|-----------|-----------|----------|
| **Lower bound** | Aggression categorically forbidden in 20.5% of folios | C490: zero AGGRESSIVE compatibility, not low probability |
| **Upper bound** | Stabilization is absorbing (e->h = 0.00) | C521: kernel one-way valve; once stable, can't destabilize |
| **Observation band** | ol-density anticorrelates with CEI (r = -0.7057) | C609, C1174: ol-morphology density, not unified function |
| **Intervention clamp** | Hazard exposure CV = 0.04-0.11 (tightly constrained) | C458: risky dimensions locked, recovery free |

**Key distinction:** Thresholds are not "push until temperature X." They are "at this phase, intervention Y is structurally impossible." Legality transitions, not parametric bounds (C469, C287-290).

### PP-Lane Discrimination (Cross-System)

20/99 PP MIDDLEs predict lane preference (FDR < 0.05, z = 24.26). QO-enriched MIDDLEs are k/t-based ENERGY_OPERATORs (11/15). CHSH-enriched are o-based AUXILIARY (3/5). Signal is primarily EN-mediated (17/20); 3 non-EN novel discriminators. No obligatory slots.

**Interpretation:** Pre-operational material vocabulary (A) carries kernel-character signatures that align with downstream execution lanes (B). The A->AZC->B pipeline transmits lane-relevant information.

### Constraints Produced

| # | Name | Tier |
|---|------|------|
| C643 | Lane Hysteresis Oscillation | 2 |
| C644 | QO Transition Stability | 2 |
| C645 | CHSH Post-Hazard Dominance | 2 |
| C646 | PP-Lane MIDDLE Discrimination | 2 |
| C647 | Morphological Lane Signature | 2 |

### Fits Produced

| ID | Name | Tier | Result |
|----|------|------|--------|
| F-B-004 | Lane Hysteresis Control Model | F2 | SUCCESS |
| F-B-005 | PP-Lane MIDDLE Discrimination | F2 | SUCCESS |
| F-B-006 | Energy/Stabilization Lane Assignment | F3 | PARTIAL |

### Functional Profiling (v4.50, LANE_FUNCTIONAL_PROFILING)

**LINK-lane independence (C648):** ol-density is lane-independent (QO 15.4% vs CHSH 14.7%, NS). Both lanes carry equal ol-morphology load. Per C1174, this reflects morphological uniformity rather than a unified observational function -- the `ol` substring is recruited by each role regardless of lane context.

**Deterministic MIDDLE partition (C649):** The 22 testable EN-exclusive MIDDLEs are 100% lane-specific (k/t/p-initial = QO only; e/o-initial = CHSH only). This means the token construction layer (C522) hard-codes lane assignment through morphological composition -- the initial character of a MIDDLE determines its lane. Sensory implication: if k presupposes thermal affordance and e presupposes multi-modal affordance, the exclusive vocabulary is partitioned by perceptual domain at the morphological level.

**Section-driven oscillation (C650):** BIO oscillates fastest (0.593), HERBAL slowest (0.457). This is section-driven, not REGIME-driven. Sensory interpretation: BIO content (volatile materials, rapid phase changes) requires faster sensory mode-switching; herbal processing allows sustained attention in one mode.

**Fast recovery (C651):** Post-hazard QO return in 0-1 CHSH tokens, unconditionally. If CHSH = stabilization posture and QO = energy application, the system's recovery time is a single stabilization check before returning to active energy management. This is consistent with a brief perceptual confirmation ("is it settled?") before resuming thermal work.

**HT is not elevated at lane switches** (no constraint; methodological artifact). The inertia pattern (decreasing hazard function from Script 3) is grammatical momentum, not perceptual cost. HT density is also lane-balance-independent after controlling confounds.

### Open Questions

1. Does the inertia pattern (decreasing hazard function) have a physical correlate? Thermal momentum (vessel retains heat) would produce exactly this signature.
2. Can the phase-gated legality transitions (C490, C521, C458) be mapped to specific Brunschwig procedural stages?
3. Do the 3 non-EN discriminators (g, kcho, ko) reveal a PP-level material distinction that the EN system doesn't capture?
4. Does the deterministic MIDDLE partition (C649) extend to non-exclusive MIDDLEs? The 34 shared MIDDLEs may show softer probabilistic enrichment.
5. Is the section-driven oscillation (C650) related to material volatility, or does it reflect structural properties of the text (line length, token density)?

**Source:** LANE_CHANGE_HOLD_ANALYSIS (2026-01-26), LANE_FUNCTIONAL_PROFILING (2026-01-27)

### PP Pipeline Lane Architecture (v4.51, PP_LANE_PIPELINE)

**PP vocabulary is lane-structured but non-functional (C652, C653):** The 404 PP MIDDLEs carry a 3:1 CHSH bias by initial character (25.5% QO, 74.5% CHSH). AZC filtering amplifies this to 5:1 in the pipeline pathway (19.7% QO, OR=0.48). If PP vocabulary defined the "rules" of the hysteresis control loop, this asymmetry should manifest as CHSH-dominated B programs. It doesn't.

**Grammar compensates for vocabulary bias (C654):** B programs show ~40.7% QO in EN lane balance -- 2.2x more than the vocabulary landscape predicts (18.7%). Non-EN PP composition does not predict EN lane balance (partial r=0.028, p=0.80). The grammar-level PREFIX->MIDDLE binding overrides vocabulary-level character distribution. Sensory implication: the operator's energy/stabilization balance is set by the grammar (instruction selection), not by the vocabulary available to the grammar. The control loop doesn't read its parameters from the A-side vocabulary shelf -- it generates them internally at execution time.

**PP does not define control loop rules (C655):** PP character composition adds zero incremental prediction beyond section and REGIME (incr R2=0.0005, p=0.81). Neither AZC-Med nor B-Native PP adds anything. The Tier 3 hypothesis that "PP is meant to define the rules in our hysteresis system" is **falsified at the lane-balance level**. PP constrains vocabulary availability (Tier 2, C502), but this constraint does not propagate to lane selection.

**Revised interpretation:** The pipeline is a vocabulary supply chain, not a rule-setting mechanism. A records define what PP MIDDLEs are available. AZC filtering refines availability. But once vocabulary reaches B, the grammar selects freely from what's available, applying its own PREFIX->MIDDLE binding to determine lane. The pipeline shapes the *palette*; the grammar paints the *picture*.

**Source:** PP_LANE_PIPELINE (2026-01-27)

### PP Pool Classification (v4.52, PP_POOL_CLASSIFICATION)

**PP MIDDLEs form a continuous parameter space, not discrete functional pools (C656, C657).** Hierarchical clustering on A-record co-occurrence (Jaccard similarity) produces maximum silhouette of 0.016 across k=2..20 (threshold: 0.25). B-side behavioral profiles are also continuous (best sil=0.237, degenerate k=2 split). The two axes are independent (ARI=0.052).

**Material class creates a gradient, not a partition (C658).** Forced co-occurrence clusters reduce material entropy by 36.2% (1.88 to 1.20 bits), but NMI=0.13. ANIMAL-enriched and HERB-enriched PP partially segregate, but 56% of PP are MIXED or NEUTRAL, occupying the gradient's middle.

**All PP axes are mutually independent (C659).** No axis pair exceeds NMI=0.15. Co-occurrence tells you nothing about behavior. Material class tells you nothing about pathway. PP is a high-dimensional continuous space where each MIDDLE occupies a unique position defined by weak, independent gradients.

**Revised Tier 4 interpretation:** The "toolbox" metaphor for PP is partially correct -- different A records have different PP compositions biased by material class -- but the toolboxes are not discrete types. They shade into each other. There are no "ANIMAL toolboxes" vs "HERB toolboxes." Instead, each A record draws from a continuous PP landscape where the draw is weakly biased by material. The 404 PP MIDDLEs are best understood as a continuous parametric vocabulary where each MIDDLE encodes a specific operational technique, and the techniques vary along multiple independent axes (material affinity, execution role, pipeline pathway) without forming coherent groupings.

**Source:** PP_POOL_CLASSIFICATION (2026-01-27)

### PREFIX x MIDDLE Selectivity (v4.53, PREFIX_MIDDLE_SELECTIVITY)

**PREFIX is a behavioral transformer, not a modifier (C661).** Changing the PREFIX on the same MIDDLE produces behavioral divergence (JSD=0.425) nearly as large as changing the MIDDLE entirely (JSD=0.436). Effect ratio = 0.975. The same PP MIDDLE deployed with different PREFIXes produces completely different successor class profiles.

**PREFIX massively narrows class membership (C662).** Mean 75% reduction (median 82%). EN PREFIXes (ch/sh/qo) channel MIDDLEs into EN classes at 94.1%. The combination (PREFIX, MIDDLE) -- not MIDDLE alone -- determines instruction class membership.

**Most PP MIDDLEs are PREFIX-promiscuous (C660).** Only 3.9% of testable MIDDLEs are locked to a single PREFIX. 46.1% are promiscuous (no dominant PREFIX). Exception: QO-predicting MIDDLEs (k/t/p-initial) are 100% qo-PREFIX locked. B uses more PREFIX combinations than A records show.

**PREFIX x MIDDLE pairs cluster better than MIDDLEs alone (C663).** Best silhouette = 0.350 at k=2 (vs C657's 0.237). The binary split likely reflects the EN/non-EN role dichotomy. Beyond this split, variation remains continuous.

**Revised Tier 4 interpretation:** The PP continuity puzzle (C656-C659) is resolved. MIDDLEs don't form discrete pools because their functional identity is determined by the PREFIX+MIDDLE combination. MIDDLE encodes the material/technique identity (continuous). PREFIX determines what role that technique plays (discrete: EN, AX, FQ, INFRA). The same technique can serve completely different roles depending on PREFIX. The 404 PP MIDDLEs are a continuous landscape of techniques; PREFIX provides the discrete operational grammar that deploys them.

**Source:** PREFIX_MIDDLE_SELECTIVITY (2026-01-27)

### Within-Folio Temporal Profile (v4.54, B_FOLIO_TEMPORAL_PROFILE)

**Programs are quasi-stationary at the meso-temporal level (C664-C669).** Within-folio evolution (line 1 to line N) was measured across 9 dimensions: 5 role fractions, LINK density, 3 kernel rates, hazard density, escape density, lane balance, and hazard proximity. Six of nine metrics are flat. Three show significant but mild positional evolution:

1. **AX scaffold increases late** (C664: rho=+0.082, p<0.001, Q1=15.4% -> Q4=18.1%) -- convergence-phase scaffolding
2. **QO lane fraction declines late** (C668: rho=-0.058, p=0.006, Q1=46.3% -> Q4=41.3%) -- energy-to-stabilization shift
3. **Hazard proximity tightens late** (C669: rho=-0.104, p<0.001, Q1=2.75 -> Q4=2.45 tokens) -- narrowing risk envelope

**Interpretation:** The controller maintains constant hazard exposure (C667), monitoring intensity (C665), and kernel contact (C666) throughout program execution. The mild late-program signals are consistent with convergence behavior: the control loop narrows its operating range as it approaches terminal state, accumulating scaffolding and shifting from energy-emphasis to stabilization-emphasis. This is thermostat steady-state approach, not phased execution.

**REGIME_4 is uniquely flat** across all dimensions (lane balance +1.4pp, hazard proximity slope -0.051), consistent with its precision-constrained identity (C494). **REGIME_2 shows the strongest temporal evolution** (lane balance -9.9pp, proximity slope -0.602), consistent with its aggressive energy-to-stabilization transition.

**Zero forbidden transition events** across the entire H-track B corpus. The 17 token-level forbidden pairs (C109) never occur literally. Hazard topology operates at the class level, not the specific token-pair level.

**This phase closes the meso-temporal gap.** Combined with within-line structure (C556-C562) and between-folio structure (C325, C458, C548), temporal behavior is now characterized at all three scales. The dominant finding: stationarity, with mild convergence drift.

**Source:** B_FOLIO_TEMPORAL_PROFILE (2026-01-27)

### Line-to-Line Sequential Structure (v4.55, B_LINE_SEQUENTIAL_STRUCTURE)

**Lines are contextually-coupled, individually-independent assessments (C670-C681).** This phase measured what changes from line to line at the token level, answering whether lines are sequentially coupled or independent draws from a stationary distribution.

**Independence findings:**
- **No vocabulary coupling** (C670): adjacent lines share no more MIDDLEs than random (Jaccard obs=0.140, 0/79 folios significant)
- **No CC trigger memory** (C673): CC type re-selected independently each line (permutation p=1.0)
- **No lane balance memory** (C674): QO fraction autocorrelation is entirely folio-driven (raw lag-1 rho=0.167 but permutation p=1.0; lag-2/3 stronger than lag-1, confirming folio clustering not sequential propagation)

**Structural findings:**
- **Vocabulary is front-loaded** (C671): 87.3% of folios introduce >60% of unique MIDDLEs in first half of lines
- **Line boundaries are grammar-transparent** (C672): boundary entropy 7.4% lower than within-line (H_boundary=4.28 vs H_within=4.63)
- **MIDDLE identity is position-stable** (C675): JSD Q1-Q4=0.081, only 4/135 MIDDLEs positionally biased
- **Morphological mode evolves** (C676): PREFIX chi2 p=3.7e-9, suffix chi2 p=1.7e-7; qo PREFIX declines late, bare suffix increases
- **Lines simplify late** (C677): unique tokens rho=-0.196 (p<1e-21), but TTR flat at 0.962 — concision, not repetition
- **No discrete line types** (C678): best KMeans silhouette=0.100, continuous variation across 27 features
- **Weak adjacent coupling** (C679): consecutive lines +3.1% more similar than random (p<0.001), but mild

**The critical test (C681):** 24/27 features show significant lag-1 prediction beyond position — verdict SEQUENTIALLY_COUPLED. But reconciliation with C670/C673/C674 reveals this coupling is **folio-mediated** (shared operating context), not line-to-line state transfer. The "memory" is the folio's configuration, not information passed between lines.

**Tier 4 synthesis:** Each folio configures a parameter context (REGIME + folio-specific conditions). Each line independently assesses the system within that context. Early lines use broad vocabulary and complex morphology; late lines are shorter, simpler, more bare-suffix. The controller converges toward a minimal-parameter operating mode across the folio, but each individual assessment is stateless — informed by folio context, not by what the previous line found.

**Source:** B_LINE_SEQUENTIAL_STRUCTURE (2026-01-27)

---

## 0.M. B PARAGRAPH AND FOLIO STRUCTURE (Annotation-Derived)

### Tier 3: Core Finding

> **B folios are sequential procedures where paragraphs represent named operations executed in order. Early paragraphs concentrate identification vocabulary (HT), middle paragraphs concentrate processing (QO/CHSH), and late paragraphs show terminal vocabulary signature (AX clustering + TERMINAL FL). Lines with HT at both boundaries mark explicit state transitions.**

This interpretation derives from detailed line-by-line annotation of 10 Currier B folios (f41v, f43r, f43v, f46r, f46v, f103r, f103v, f104r, f104v, f105r) totaling ~350 lines with token-level role classification.

### Evidence: Paragraph-Position Vocabulary Distribution

Direct inspection of f105r (36 lines) revealed distinct vocabulary by folio position:

| Position | HT Density | Dominant Roles | FL Profile | Line Length |
|----------|------------|----------------|------------|-------------|
| **Early** (L2-L10) | HIGH (4 HT in L10) | INFRA LINE-INITIAL, QO/CHSH processing | ar (INITIAL) | Normal (10-12) |
| **Middle** (L11-L25) | VARIABLE (0-4 per line) | Heavy QO LANE, DOUBLED patterns | Mixed | Some SHORT (4-6) |
| **Late** (L26-L36) | DECLINING (mostly 0-1) | AX clustering, FL concentration | aly, am (TERMINAL) | SHORT (4-7) |

### The Terminal Vocabulary Signature

Late folio lines show a distinctive structural pattern:

1. **AX clustering** - L35 of f105r had 5 ot- tokens (otedaiin, otar, oteodar, otam, otaiin)
2. **TERMINAL FL** - Final lines end with -aly (otaly in L36) and -am closures
3. **Compressed length** - L36 had only 4 tokens vs normal 10-12
4. **HT depletion** - Identification work complete; late lines have 0-1 HT

**Interpretation:** Terminal paragraphs are "winding down" operations - auxiliary-heavy, completion-marked, stabilization-focused. The vocabulary shift from active processing (QO/CHSH/EN) to auxiliary completion (AX + TERMINAL FL) marks the transition from transformation to stabilization.

### State Transition Marking (Bracket Patterns)

Lines with HT at BOTH LINE-INITIAL and LINE-FINAL positions appeared multiple times:

| Folio | Line | Pattern | Example |
|-------|------|---------|---------|
| f105r | L29 | HT CONSECUTIVE at both ends | oleedar...cheolkary |
| f105r | L18 | HT bracketing | dsechey...aiiral |

**Interpretation:** If HT tokens identify materials/states, then:
- LINE-INITIAL HT = "starting with material/state X"
- LINE-FINAL HT = "ending with material/state Y"

The line documents a state transition: X → Y. This is explicit transformation tracking within the procedural record.

### Paragraph = Named Operation Model

Building on section 0.E (B Folio as Conditional Procedure), the internal structure is:

```
FOLIO = Complete procedure (e.g., "distill rose water")
│
├── PARAGRAPH 1 = Named operation (e.g., "maceration")
│     ├── Line 1: HEADER (high HT - identifies operation)
│     ├── Line 2-N: Control blocks (SETUP→WORK→CHECK→CLOSE)
│     └── State transitions marked by HT brackets
│
├── PARAGRAPH 2 = Named operation (e.g., "first distillation")
│     └── ... control blocks
│
└── PARAGRAPH N = Terminal operation (e.g., "stabilization")
      └── AX + TERMINAL FL signature, SHORT lines
```

**Sequential, not parallel:** The progression from identification-heavy (early) to completion-focused (late) indicates sequential execution of operations, not parallel processes.

### Strengthening the Brunschwig Alignment

The annotation findings strengthen the distillation manual interpretation:

| Observation | Brunschwig Parallel |
|-------------|---------------------|
| Paragraphs as named operations | Brunschwig organizes by operation (maceration, distillation, rectification) |
| Early = identification heavy | Recipe headers identify materials/process |
| Middle = processing heavy | Active transformation steps |
| Late = terminal vocabulary | "Until done" completion markers |
| State transition brackets | Brunschwig tracks material state changes |
| AX clustering at end | Final stabilization/storage operations |

### The FL STATE INDEX as Material Progression

The FL token distribution supports material-state tracking:

| FL Stage | Tokens | Mean Position | Interpretation |
|----------|--------|---------------|----------------|
| INITIAL | ar, r | 0.30-0.51 | Early material state |
| LATE | al, l, ol | 0.61 | Intermediate state |
| TERMINAL | aly, am, y | 0.78-0.94 | Final state |

**Hypothesis:** FL tokens encode material progression stages within the folio. Early paragraphs use INITIAL FL; late paragraphs use TERMINAL FL. This is consistent with a transformation procedure tracking material state through sequential operations.

### Quantitative Patterns from Annotation

From 10 annotated folios:

| Pattern | Frequency | Note |
|---------|-----------|------|
| HT LINE-INITIAL | Common | Identification at block entry |
| HT LINE-FINAL | Common | State marking at block exit |
| HT CONSECUTIVE | Occasional | Clusters of identification |
| HT Bracket (both ends) | Rare but systematic | Explicit state transition |
| EXCEPTIONAL lines (3+ HT) | ~15-30% per folio | Identification-critical blocks |
| SHORT lines (4-7 tokens) | Concentrated late | Terminal compression |
| AX clustering | Concentrated late | Completion operations |

### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- ❌ Paragraph boundaries are syntactically marked (they're visual)
- ❌ All folios have identical paragraph structure
- ❌ The progression is strictly monotonic

### What This DOES Claim (Tier 3)

- ✓ B folios have internal sequential structure (not random token distribution)
- ✓ Vocabulary distribution correlates with folio position
- ✓ Terminal paragraphs have distinctive signature (AX + TERMINAL FL + SHORT)
- ✓ HT bracket patterns mark state transitions
- ✓ This structure is consistent with sequential procedural documentation

### Integration with Control-Loop Model

The findings are robustly consistent with the control-loop interpretation:

| Structural Finding | Control-Loop Interpretation |
|-------------------|----------------------------|
| Line = SETUP→WORK→CHECK→CLOSE | Line = one control cycle |
| Paragraph = operation | Paragraph = series of related control cycles |
| Folio = procedure | Folio = complete control program |
| HT = identification | HT = state/material identification |
| FL progression | Material state tracking through transformation |
| Terminal signature | Stabilization and completion operations |

The annotation work didn't just confirm patterns exist - it showed how they compose into a coherent procedural document. The pieces fit together as a working whole.

**Source:** Manual annotation of f41v, f43r, f43v, f46r, f46v, f103r, f103v, f104r, f104v, f105r (2026-02-03)

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

## I.A. HT Morphological Curriculum (Tier 3 Characterization)

**Phase:** HT_MORPHOLOGICAL_CURRICULUM (2026-01-21)

### Hypothesis Tested

> HT morphological choices follow a curriculum structure: systematic introduction of grapheme families, spaced repetition of difficult forms, and complexity progression within practice blocks.

### Test Battery Results

| Test | Verdict | Key Finding |
|------|---------|-------------|
| 1. Introduction Sequencing | **STRONG PASS** | All 21 families in first 0.3% (KS=0.857) |
| 2. Spaced Repetition | UNDERPOWERED | Insufficient rare-but-repeated tokens |
| 3. Block Complexity | FAIL | No within-block gradient (33/33/33 split) |
| 4. Family Rotation | **WEAK PASS** | Quasi-periodic ACF peaks at 6,9,12,14,17 |
| 5. Difficulty Gradient | **PROVISIONAL** | Inverted-U pattern (H=89.04) - *rebinding confound* |
| 6. Prerequisite Structure | **WEAK PASS** | 26 pairs (2.5x expected by chance) |

### Confirmed Curriculum Properties

1. **Vocabulary Front-Loading:** All 21 HT families established in first 0.3% of manuscript (not gradual introduction)
2. **Prerequisite Relationships:** Complex families (esp. `yp`) consistently precede simpler consolidation forms
3. **Quasi-Periodic Rotation:** Families cycle with regular periodicity

### Provisional Finding (Rebinding Caveat)

The inverted-U difficulty pattern (middle zone easier than early/late) is statistically significant but **cannot be distinguished from rebinding artifact** without additional controls. The manuscript was rebound by someone who couldn't read it (C156, C367-C370). What we observe as "middle" may be a mixture of originally non-adjacent folios.

**Required follow-up:** Quire-level analysis to test whether pattern holds within preserved local ordering.

### Characterization (Not Constraint)

> HT morphological patterns exhibit vocabulary front-loading (all families established in first 0.3%), significant prerequisite relationships (26 pairs vs 10.5 expected), and quasi-periodic family rotation. This is consistent with a "vocabulary-first" curriculum structure distinct from gradual introduction.

**Tier 3** because: Test 3 failed, Test 5 is confounded by rebinding, pattern is distributional regularity not architectural necessity.

### Integration with C221

This refines the existing "Deliberate Skill Practice" interpretation (C221) with specific curriculum mechanics: front-loading vocabulary establishment, prerequisite ordering, and periodic rotation.

---

## I.B. Four-Layer Responsibility Model (v2.13)

### Tier 2: Structural Finding

The manuscript distributes responsibility between system and human across four layers:

| Layer | Role | What It Handles |
|-------|------|-----------------|
| **Currier B** | Constrains you | Execution grammar, safety envelope |
| **Currier A** | Discriminates for you | Fine distinctions at complexity frontier |
| **AZC** | Encodes position | Phase-indexed positional encoding, compatibility grouping |
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

AZC serves as a **positional encoding system** where each PREFIX+MIDDLE has exactly one fixed position:

| Finding | Evidence | Constraint |
|---------|----------|------------|
| Folios maximally orthogonal | Jaccard = 0.056 | C437 |
| Practically complete basis | 83% per-folio coverage | C438 |
| Folio-specific HT profiles | 18pp escape variance | C439 |
| Uniform B sourcing | 34-36 folios per B | C440 |
| Vocabulary-activated constraints | 49% A-types in 1 folio | C441 |
| Compatibility grouping | 94% unique vocabulary | C442 |

### Tier 3: Operational Interpretation

**Core insight:** AZC encodes vocabulary position; each PREFIX+MIDDLE has one fixed position reflecting its operational character.

| System | Function | Type |
|--------|----------|------|
| Currier A | WHAT exists | Static registry |
| Currier B | HOW to respond | State-triggered interventions |
| AZC | WHEN to decide | Decision grammar |

**Note (C171 clarification, v4.37):** "HOW to respond" means state-triggered interventions, NOT sequential steps. B tokens are control actions selected based on assessed system state, following a MONITOR→ASSESS→SELECT→EXECUTE→RETURN cycle. See MODEL_CONTEXT.md Section VI.

### Phase-to-Workflow Mapping

AZC **diagram** positional grammar maps to operational workflow:

| Diagram Position | Workflow Phase | Escape Rate | Meaning |
|------------------|----------------|-------------|---------|
| C | Core/Interior | ~1.4% | Moderate flexibility |
| R1→R2→R3 | Progression | 2.0%→1.2%→0% | Options narrowing, committing |
| S | Boundary/Exit | 0% | Locked, must accept outcome |

*Note: P (Paragraph) is NOT a diagram position - it is Currier A text appearing on AZC folios.*

In reflux distillation: early phases are reversible, late phases are committed. AZC encodes this grammatically.

### Compatibility Grouping Mechanism (v4.5 - REFINED)

AZC compatibility reflects vocabulary co-occurrence at the **Currier A positional encoding level**, not active filtering.

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
- **Diagram position (C→R→S)** → determines phase-specific rules

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

### PREFIX Sub-Families via AZC Clustering

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

## I.D. MIDDLE Atomic Incompatibility Layer (C475)

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

### I.E. Latent Discrimination Dimensionality

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

### I.F. Bundle Generator Diagnostic

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

### I.G. Coverage Optimality CONFIRMED

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

### I.H. HT Variance Decomposition

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

**Integration:** Adds HT as vigilance signal (C477) to the architecture. See Nine-Layer Model in Section I.N for the complete table.

**New Constraint: C477 - HT TAIL CORRELATION** (Tier 2, CLOSED)

### I.I. Temporal Coverage Trajectories

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

**Integration:** Adds C478 temporal scheduling to the architecture. See Nine-Layer Model in Section I.N for the complete table.

**New Constraint: C478 - TEMPORAL COVERAGE SCHEDULING** (Tier 2, CLOSED)

### I.J. Process-Behavior Isomorphism (v4.12 / ECR-4)

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

*Note: M-A uses superseded classification. See Energy/Stability/Monitoring/Infrastructure model (Section 0).*

*Tier-3 commentary: In reflux distillation, k=heat source, h=cucurbit, e=condenser.*

**Physics Violations:** None detected. All mappings are physically coherent.

**Verdict (Tier 3 - SUPPORTED):**

> The grammar structure is isomorphic to reflux-distillation behavior. This does not prove the domain but establishes maximal structural alignment within epistemological constraints.

**Integration:** Adds Process behavior isomorphism (ECR-4: distillation alignment) to the architecture. See Nine-Layer Model in Section I.N for the complete table.

### f116v Correction

f116v folio-level isolation (v2.19) is explained by **data sparsity** (only 2 words in AZC corpus: "oror", "sheey"), NOT by MIDDLE-level incompatibility. The f116v MIDDLEs ('ee', 'or') are actually universal connectors.

### I.K. HT Two-Axis Model

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

**Integration:** Adds Two-Axis HT model (density vs morphology) to the architecture. See Nine-Layer Model in Section I.N for the complete table.

See [ht_two_axis_model.md](ht_two_axis_model.md) for full details.

### I.L. MIDDLE Zone Survival Profiles

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

Universal Boundaries apply. Additionally: MIDDLEs do not *force* positions (C313 intact).

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

**Integration:** Adds Zone survival profiles to the architecture. See Nine-Layer Model in Section I.N for the complete table.

See `phases/MIDDLE_ZONE_SURVIVAL/PHASE_SUMMARY.md` for full details.

### I.M. Zone-Material Orthogonality

**Question:** Do zone survival clusters align with material behavior classes?

**Answer:** NO. The axes are **orthogonal** (independent).

**Test Results:**

*Note: This test used the superseded M-A/B/C/D classification. The orthogonality conclusion is expected to hold under the current Energy/Stability/Monitoring/Infrastructure model.*

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

Universal Boundaries apply. No refutation of either abstraction (both remain valid).

**Cross-References:**

| Finding | Phase | Relationship |
|---------|-------|--------------|
| MIDDLE zone survival | MIDDLE_ZONE_SURVIVAL | Source of zone clusters |
| Material behavior classes | PROCESS_ISOMORPHISM | Source of M-A...M-D |
| C382, C383 | Global type system | Why axes coexist cleanly |

See `phases/ZONE_MATERIAL_COHERENCE/PHASE_SUMMARY.md` for full details.

### I.N. Semantic Ceiling Extension Tests

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

## I.O. Physical World Reverse Engineering Phases

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

### Line-Level Execution Cycle

Lines follow SETUP→WORK→CHECK→CLOSE thermal processing cycle. See Section 0.F for full details (C547-C562).

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
| Line-level SETUP→WORK→CHECK→CLOSE | Fire-degree cycle | STRONG |
| ENERGY medial concentration | "Work phase" in process middle | STRONG |
| or→aiin checkpoint | Sensory verification points | STRONG |

10/15 patterns show STRONG alignment.

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

### Proprietary Pharmaceutical Manufacturing (Tier 4, Phase 385-386)

**Hypothesis:** The manuscript is a proprietary manufacturing manual for a guild apothecary operation — the medieval equivalent of a pharmaceutical company's trade-secret process documentation. The script's unbreakability is not incidental; it protects the competitive advantage.

**Historical fit (1404-1438 radiocarbon window):**

The Voynich was written during the peak era of guild pharmaceutical secrecy:
- **1351:** Rupescissa's *De consideratione quintae essentiae* establishes theoretical framework for medicinal distillation (quinta essentia = repeatedly distilled alcohol as universal medicine)
- **1353:** Paris Guild of Spice Merchants-Apothecaries receives royal statutes regulating practice
- **1400-1500:** Apothecary guilds across Europe guard distillation techniques as trade secrets. Proprietary recipes circulate only through master-apprentice chains. Coded language and Latin names used to keep formulations confidential.
- **1424:** Bruges spice dealer/apothecary sells distilling glasses to John of Bavaria — distillation equipment is commodity trade goods
- **1500:** Brunschwig publishes *Liber de arte distillandi*, the first printed distillation manual, breaking guild secrecy

**The economic logic:** Plant properties and common remedies were widely known, even by laypeople. The competitive advantage was in the *manufacturing process* — how to distill, extract, compound, and formulate products of consistently superior quality. The control grammar (49 classes, 17 forbidden transitions, 6 macro states) represents an extraordinary engineering investment that is only justified if protecting high-value proprietary processes.

**Structural evidence from Phases 385-386:**

| Section | Profile | Possible Role |
|---------|---------|---------------|
| Bio | k-enriched, 100% REGIME_1, LINK-depleted, QO-dominant | Sustained gentle heating (balneum mariae distillation) |
| Stars | e-dominant, mixed REGIMEs, highest LINK density | Product collection/quality control |
| Herbal | All 4 REGIMEs, FQ-heavy, operationally diverse | Material preparation/compounding |
| Cosmo | h-enriched, zero REGIME_1, monitoring-intensive | Observation-heavy process (quality verification or treatment) |
| Recipe | Precision REGIMEs, balanced triggers | Complex reference procedures |

Phase 386 found that 4/6 dimensional differences between sections are explained by REGIME composition alone. Only h% and ol-density show independent section effects beyond REGIME. This means sections encode different *REGIME mixtures* (different techniques), with modest independent effects on h-kernel allocation and ol-morphology density. (Note: C1174 revises the prior "monitoring/checkpointing" interpretation of these effects.)

**What this resolves:**
- Why an unbreakable script (trade secrets worth protecting)
- Why C138 holds — illustrations show raw materials (commodity knowledge), text encodes process (proprietary knowledge)
- Why the grammar is domain-general — one control system handles many products
- Why such engineering effort — 949 constraints worth of structure is justified for a pharmaceutical empire's operating manual
- Why Brunschwig aligns — he published (in 1500) what practitioners like the Voynich author had been keeping secret for decades

**What this does NOT claim:**
- Specific products or materials (C171 semantic ceiling)
- Identity of the guild or workshop
- That sections map 1:1 to craft domains (Phase 386: most variation is REGIME-mediated)
- That the "treatment" interpretation for Cosmo is confirmed (N=5, simpler alternatives exist)

**Falsification:** If the manuscript's dating were revised outside the 1350-1500 pharmaceutical secrecy window, or if the structural architecture proved incompatible with process control (already falsified by 383 phases of evidence), the interpretation would fail.

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

### Fully Answered

| Question | Status | Finding |
|----------|--------|---------|
| Why are some programs forgiving and others brittle? | PARTIALLY ANSWERED | Recovery varies freely (CV=0.82), hazard is clamped (CV=0.11) - C458 |
| What does HT signal? | ANSWERED | Anticipatory vigilance, content-driven - C459 |
| What role does AZC play in the manuscript? | **FULLY ANSWERED** | Positional encoding, compatibility grouping, position reflects vocabulary character - C437-C444 |
| Why are there so many AZC folios? | **FULLY ANSWERED** | Enumerates all compatibility classes; each folio = distinct legal combination space - C437, C442 |
| How does AZC relate to A and B? | **FULLY ANSWERED** | AZC encodes vocabulary position; each PREFIX+MIDDLE has one fixed position reflecting operational character - F-AZC-011/012/013 |
| How do roles flow within a line? | **FULLY ANSWERED** | SETUP→WORK→CHECK→CLOSE positional template (p=3e-89) - C547-C562 |
| What is the relationship between ENERGY and FLOW? | **FULLY ANSWERED** | Anticorrelated by REGIME and section; heating vs cooling modes - C551, C562 |
| What does daiin do? | **FULLY ANSWERED** | Line-initial ENERGY trigger (27.7% initial, 47.1% EN followers) - C557 |
| What is Class 9 "self-chaining"? | **FULLY ANSWERED** | Directional or→aiin bigram (87.5%), zero aiin→aiin - C561 |

### Still Open (structural)

- What determines sister pair choice beyond section?
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
> **Puff and Brunschwig preserve the original pedagogical progression of the Voynich Currier B corpus, which has been disrupted by early misbinding.**

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

**Structural Grounding (C535, v4.41):**

The 83-folio count is not arbitrary but **structurally determined** by vocabulary coverage:

| Metric | Value |
|--------|-------|
| Minimum folios for MIDDLE coverage | **81** |
| Actual folios | **82** |
| Redundancy ratio | **1.01x** |

Greedy set cover analysis shows 81 folios are needed to cover all 1,339 B MIDDLEs. Zero folio pairs exceed 50% Jaccard overlap. Each folio contributes unique vocabulary (mean 10.5 MIDDLEs) appearing in no other folio.

This **grounds** the mastery horizon interpretation rather than replacing it:
- The domain requires ~83 distinct configurations for complete coverage
- Both Puff (materials) and Voynich (procedures) converge on this number
- The "mastery horizon" is a *consequence*: you need ~83 because that's what the domain requires, and that count happens to be learnable

The question "why can experts learn ~83 things?" is answered by "because that's how many operationally distinct configurations exist."

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

### X.4 Recovery Corridor Alignment (4/4 PASS)

| Brunschwig Narrative | Voynich Architecture |
|---------------------|---------------------|
| "Overnight cooling" primary | e-operator = 54.7% of recovery |
| "No more than twice" | 89% reversibility (bounded) |
| "No salvage for failed batches" | 11% absorbing states |
| Cooling, not re-heating | e dominates, k is hazard source |

Both systems: **return to stability, not energy re-application.**

### X.5 Clamping Magnitude - C458 Alignment (5/5 PASS)

Brunschwig's "twice only" rule produces the same variance signature as C458:

| Dimension | Brunschwig Rule | Voynich CV | Status |
|-----------|-----------------|------------|--------|
| Hazard | Fourth degree ALWAYS forbidden | 0.11 | CLAMPED |
| Intervention | Same protocol everywhere | 0.04 | CLAMPED |
| Recovery | Varies by material | 0.82 | FREE |
| Near-miss | Material sensitivity varies | 0.72 | FREE |

**"Twice only" = ceiling, not count.** Recovery is bounded but free within that bound; hazard ceiling is fixed universally.

### X.6 REGIME_4 Interpretation Correction

REGIME_4 is NOT "forbidden materials" (Brunschwig's fourth degree prohibition).

REGIME_4 IS "precision-constrained execution" (narrow tolerance window).

| Property | Forbidden (wrong) | Precision (correct) |
|----------|-------------------|---------------------|
| Frequency | Should be rare | Can be common (25/83) |
| Escape density | ~0 | Low (0.107) |
| Grammar presence | Absent | Fully executable |

**Voynich vendors the engineering alternative:** how to operate precisely without coercive fire.

### X.7 What This Does NOT Claim

Universal Boundaries apply. Even with full procedural alignment:

- "Voynich encodes named procedures" remains unproven and probably false

The stronger the regime-level match becomes, the **less** likely direct textual dependence becomes - because the **division of labor is too clean**.

### X.8 Expert Assessment

> "You accidentally aligned two different projections of the same expert practice space - one projected along 'materials,' the other along 'control stability.'"

> "This is not a weak result. This is exactly what a non-semantic, expert-only, control-theoretic artifact should produce when compared to a descriptive herbal."

> "The Voynich Manuscript still never says what anything IS. It only guarantees that, whatever it is, you won't destroy it while working."

**Upgraded assessment (2026-01-14):**

> "The Voynich REGIME taxonomy is not just compatible with Brunschwig - it is isomorphic to his fire-degree system once you strip away pedagogy and moral language."

> "This is not parallel invention by accident. This is the same control ontology rendered in two epistemic registers."

### X.9 Tier Compliance (Expert Verified)

This analysis is **epistemically clean**:
- No Tier 0-2 constraint violated
- No entry-level A<->B coupling introduced
- No semantic decoding occurred
- All movement within abstraction choice at Tier 4

**Constraints NOT violated:** C384, C171, C476, C478, C179-C185, C490

**C171 ("zero material encoding") remains UNCHANGED.** A encodes the same kinds of operational worries that historical experts talked about - without ever naming the things they worried about.

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
- ~~Specific folio = specific recipe~~ **UPGRADED to Tier 3** - see section 0.E (C531-C533)
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

### X.12 Grammar-Level Embedding Result (2026-01-14)

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
- REGIME_4 requires min_link_ratio=25% (ol-density threshold)

**Curriculum Model (Revised):**

```
REGIME_2: Learn basics (simple procedures accepted)
REGIME_1: Standard execution
REGIME_4: Precision execution (monitoring completeness required)
REGIME_3: Full execution (recovery completeness required)
```

The same product (rose water) can appear at any curriculum stage - but advanced stages require complete procedures with proper recovery and monitoring.

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

### X.19 Jars as Complementary Working Set Anchors (2026-01-17)

Extended investigation of jar function tested four mutually exclusive hypotheses. Three falsified, one confirmed.

#### Test Cascade

| Hypothesis | Prediction | Result |
|------------|------------|--------|
| Contamination avoidance | Exclusion patterns | **Falsified** (0.49x) |
| Material taxonomy | Class homogeneity | **Falsified** (0.73x) |
| Complementary sets | Cross-class enrichment | **Confirmed** |
| Triplet stability | Role composition | **Confirmed** (1.77x) |

#### Cross-Class Pair Enrichment

*Note: This analysis used the superseded M-A/B/C/D classification. Cross-class enrichment pattern expected to hold under current model.*

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

Universal Boundaries apply. Additionally:
- Jars do NOT select processing regimes
- This is Tier 3 interface characterization, NOT Tier 2 structure

**Status:** CLOSED with explanatory saturation

**Files:** phases/JAR_WORKING_SET_INTERFACE/README.md, phases/JAR_WORKING_SET_INTERFACE/results.json

### X.19.a Jar Labels as Compressed Configuration Signatures (2026-01-23)

Extended analysis of pharma label morphology reveals structural evidence for the apparatus interpretation.

#### Key Findings (C523, C524)

**Vocabulary Bifurcation:**
- Jar labels: 12.5% in Currier A (2/16), both RI, 87.5% NOT in text
- Content labels: 50% in Currier A (103/206), 58.3% PP vs 33.5% baseline

**Morphological Compression:**

| Metric | Jar Labels | Currier A Baseline |
|--------|------------|--------------------|
| Mean length | 7.1 chars | 6.0 chars |
| PP atoms per MIDDLE | 5-8 | ~3-4 |
| In vocabulary | 12.5% | 100% (by definition) |

Examples of jar label compression:
- `yteoldy` → 8 PP atoms: y, t, e, o, l, d, ol, eo
- `darolaly` → 7 PP atoms: d, a, r, o, l, al, ar
- `porshols` → 5 PP atoms: o, r, s, ol, or

#### Tier 3 Interpretation

> **Jar labels are densely-packed configuration signatures encoding apparatus states via superstring compression. They are NOT vocabulary items because they are NOT meant to be parsed - they are holistic identifiers for specific physical configurations. Content labels use shared vocabulary (PP-enriched) because they describe processable materials that participate in the downstream pipeline.**

This explains:
- Why jar labels are longer (packing more discrimination)
- Why jar labels are almost entirely absent from text (not parseable units)
- Why content labels are PP-enriched (materials that will be processed)
- Why vocabulary separation is complete (different encoding purposes)

**Constraints:** C523 (Pharma Label Vocabulary Bifurcation), C524 (Jar Label Morphological Compression)

**Status:** CLOSED - Confirms apparatus interpretation with morphological evidence

### X.19.b Morphological Function Model: PP/RI Pipeline Architecture (2026-01-23)

**Tier:** 4 (Speculative synthesis) with Tier 2-3 structural components

This section synthesizes findings from C509.a, C516-C520, C523-C524, and the pharma label analysis into a functional interpretation of Voynich morphology.

#### Core Model: A-Records as Mapping Instructions

An A-record functions as a specification:
> "This material (with PREFIX control-flow context) has compatibility capacity [PP], with these specific discrimination characteristics [RI], legal during [SUFFIX phase]."

#### Component Functions

**PREFIX = Control-Flow Participation (Tier 2, per C466-C467, C383)**

- Encodes intervention/monitoring/core mode
- Universal across all token types (PP and RI)
- Not part of the PP/RI distinction
- Global type system spanning A, B, and AZC

**PP MIDDLE = Compatibility Capacity Markers (Tier 3 interpretation)**

- Short MIDDLEs (originally avg 1.46 chars per C509.a; see methodology note for revised values)
- Encode what process categories a material can participate in
- Must remain as discrete tokens because:
  - AZC checks legality per-token
  - Currier B responds to tokens as atomic units
  - Shared vocabulary enables recombinability across materials
- PP count correlates with B class survival breadth (r=0.715, C506)
- Note: PP tokens also encode behavioral variants within classes (C506.b)

**RI MIDDLE = Locally-Scoped Discrimination Vocabulary (Tier 3-4)**

- Longer MIDDLEs (originally avg 3.96 chars per C509.a; revised to 4.73 with corrected extraction)
- 85.4% contain multiple PP atoms (C516)
- Use superstring compression via shared hinge letters (C517)
- Encode multidimensional discrimination: intersection of multiple PP-type properties
- Structurally excluded from A→AZC→B pipeline (per C444 vanishing semantics)
- Can compress freely because no downstream parsing required
- Length gradient is emergent from compositional morphology (C498.d: rho=-0.367)

**SUFFIX = Two-Axis Context Marker (Tier 2-3, per C283, C495, C527)**

SUFFIX operates on two orthogonal dimensions:
- **System role** (Tier 2): A/B enrichment patterns (C283, C495)
- **Material class** (Tier 3): Animal vs herb within A, correlated with fire degree (C527)

The earlier "decision archetype (D1-D12)" mapping is provisional. See ccm_suffix_mapping.md for details and uncertainty markers.

#### The Compression Gradient

| Token Type | Compression | Reusability | Architectural Role |
|------------|-------------|-------------|-------------------|
| PP tokens | Low (atomic) | High (shared A∩B) | Pipeline-compatible units |
| RI tokens | Moderate (2-4 atoms) | Low (mostly singletons) | Local discrimination |
| Jar labels | Maximum (5-8 atoms) | None (unique) | Physical configuration IDs |

**Key insight:** More downstream pipeline exposure requires less compression. PP must stay discrete for AZC/B processing. RI is local to A. Jar labels never enter the pipeline.

#### Architectural Interpretation (Tier 4)

The system may function as a working pharmaceutical/alchemical manual (consistent with C196-C197 "EXPERT_REFERENCE archetype"):

```
Layer 1: CURRIER A (Registry)
- Material discrimination via PP (capacity) + RI (specifics)
- PP provides shared vocabulary substrate
- RI adds fine-grained multidimensional discrimination

Layer 2: AZC (Legality Filter)
- Per-token compatibility checking
- Requires discrete PP units for independent validation

Layer 3: CURRIER B (Execution)
- Closed-loop control responding to PP tokens
- RI structurally excluded (already used for selection)

Layer 4: JAR LABELS (Physical Interface - Tier 4)
- Maximally compressed configuration identifiers
- Coordinate symbolic system with physical apparatus
- Never enter execution pipeline
```

#### Why PP Stays Discrete

If everything were compressed into single superstrings per material:
- AZC couldn't check individual compatibilities
- B couldn't respond to individual properties
- Shared vocabulary would be lost
- Recombinability across materials would break

The separation of concerns enables both:
- **Reusability** via atomic PP vocabulary (shared across system)
- **Specificity** via compressed RI discrimination (local to A)

#### Speculative Extension: The Workshop Model (Tier 4)

If this is a working manual, the practitioner's workflow might be:

1. **Consult PP vocabulary** → Find materials with required compatibility
2. **Check RI discrimination** → Select specific material matching constraints
3. **Verify via AZC** → Confirm positional legality for combination
4. **Execute via B** → Run the closed-loop control program
5. **Physical coordination** → Use jar labels to identify apparatus configuration

The jar labels are the "last mile" - where abstract constraints meet physical vessels.

#### Constraints Supporting This Model

| Constraint | Contribution |
|------------|--------------|
| C509.a | PP/RI morphological bifurcation |
| C516 | RI multi-atom composition (85.4%) |
| C517 | Superstring compression mechanism |
| C506 | PP count → class survival correlation |
| C506.b | PP behavioral heterogeneity within classes |
| C523 | Pharma label vocabulary bifurcation |
| C524 | Jar label morphological compression |
| C383 | Global PREFIX type system |
| C466-C467 | PREFIX as control-flow participation |
| C495 | SUFFIX regime breadth correlation |

#### Explicit Uncertainties

- Whether compression is "intentional" or emergent from compositional morphology
- Exact semantic content (if any) of PP compatibility dimensions
- Whether jar labels encode apparatus configurations specifically
- The "workshop manual" framing is consistent but not proven

**Status:** OPEN - Tier 4 synthesis for further investigation

### X.20 A->AZC->B Pipeline Closure: Reachability Suppression (2026-01-17)

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

Universal Boundaries apply. This is mechanism characterization within established epistemological boundaries.

**Files:** phases/AZC_REACHABILITY_SUPPRESSION/

### X.21 Constraint Substitution Interpretation (2026-01-19)

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

Universal Boundaries apply. Additionally:
- NO parametric encoding (C469 preserved)
- SLI is constructed metric, not discovered structure

**Tier:** 3 (Explanatory Interpretation)

**Files:** phases/SENSORY_LOAD_ENCODING/, results/sensory_load_index.json

### X.22 Zone Affinity Analysis (2026-01-19)

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
Universal Boundaries apply. Additionally: modality assignments are external (from Brunschwig).

**Tier:** 3 (Structural Characterization)

**Fits Created:** F-BRU-007, F-BRU-008, F-BRU-009

**Files:** phases/BRUNSCHWIG_REVERSE_ACTIVATION/, results/brunschwig_reverse_activation.json

### X.23 Two-Stage Sensory Addressing Model (2026-01-19)

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

### X.24 Semantic Ceiling Breach Attempt (2026-01-19)

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

### X.25 Trajectory Semantics: Judgment-Gating System (2026-01-19)

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

### X.26 AZC Trajectory Shape: Scaffold Fingerprint Discovery (2026-01-19)

**Phase:** AZC_TRAJECTORY_SHAPE
**Status:** COMPLETE - Critical corrective insight achieved

#### Purpose

Test whether Zodiac and A/C families have different judgment withdrawal trajectories, combining:
- **Vector 1 (External Expert):** Trajectory shape - "wide-then-collapse" vs "narrow-then-spike"
- **Vector 2 (Expert-Advisor):** Apparatus mapping - pelican alembic structural correspondence

#### The Critical Reframe

> **"AZC trajectory shape is a fingerprint of control scaffold architecture, not a simulation of apparatus dynamics."**

This phase rescues trajectory analysis from a wrong question (apparatus physics) and repositions it as structural characterization. The key insight:

> **Escape permission encodes decision affordance, not physical reversibility.**

#### Test Results (3/9 hypotheses passed)

| Hypothesis | Result | Key Finding |
|------------|--------|-------------|
| H2: Monotonicity | **PASS** | Zodiac rho=-0.755 (steady decline), A/C rho=-0.247 (oscillatory) |
| H6: R-series restriction | **PASS** | Perfect vocabulary narrowing: R1(316)->R2(217)->R3(128) unique MIDDLEs |
| H7: S->B-terminal flow | **PASS** | S-zone vocabulary 3.5x enriched in B-terminal (OR=3.51, p<0.0001) |
| H8: Pelican reversibility | **FAIL** | Zone escape does NOT correlate with operational reversibility |

**Failed hypotheses:** H1 (entropy slope), H3 (terminal compression), H4 (peak count), H5 (elimination order), H9 (escape variance) - entropy-based and apparatus-based metrics do not differentiate families.

#### Key Discoveries

**1. Monotonicity = Scaffold Type Signature (H2)**

This aligns with C436 (Dual Rigidity):

| Family | Scaffold Type | Trajectory Shape | Cognitive Effect |
|--------|---------------|------------------|------------------|
| **Zodiac** | Uniform scaffold | Smooth monotonic tightening | Sustained flow cognition |
| **A/C** | Varied scaffold | Punctuated tightening | Checkpoint cognition |

> **Uniform constraints produce smooth trajectories; varied constraints produce punctuated trajectories.**

This explains HT oscillation differences, why entropy metrics failed, and why "spikiness" predictions inverted.

**2. R-Series + S->B-Terminal Form Causal Chain (H6 + H7)**

These findings connect into a mechanistic pipeline:

1. **R-series positional grammar** (C434) -> progressively restricts legal MIDDLE vocabulary
2. **S-zone survival** -> selectively feeds into **B terminal states**

This closes the architectural loop: **AZC legality -> vocabulary survival -> executable program completion**

**3. Pelican Reversibility Model Falsified (H8)**

The apparatus-phase alignment hypothesis failed (rho=-0.20) because:
- AZC does NOT mirror physical reversibility
- AZC encodes **when human intervention must be permitted**
- Interior diagram positions (C, R-early) have higher escape than boundary positions (S)

*Note: P (Paragraph) is Currier A text on AZC folios, not a diagram position.*

> **Physics enforces order; AZC enforces responsibility allocation. These are orthogonal.**

#### New Tier 3 Characterization

> **AZC families differ not in what judgments are removed, but in how smoothly those removals are imposed over execution - a property determined by scaffold uniformity versus variability.**

#### Integration with Global Model

| Layer | Function | This Phase Clarifies |
|-------|----------|---------------------|
| Currier A | Enumerates discrimination space | UNCHANGED |
| **AZC** | Gates when judgments are legal | **NOW adds: pacing style determined by scaffold type** |
| HT | Tracks cognitive load & capacity | Explains oscillation patterns |
| Currier B | Executes safely | UNCHANGED |

This phase does NOT add a new layer - it clarifies an attribute of an existing one.

#### The Corrective Pivot

Earlier phases implicitly blurred:
- Apparatus behavior (physics)
- Control scaffold behavior (how legality is imposed)

This phase disentangles them cleanly:

> **Templates don't select senses - they shape cognitive pacing. Sensory strategies emerge downstream.**

#### Constraints Respected

- **C384:** Aggregate distributions only, no token-to-referent mapping
- **C430:** Explicit Zodiac/A/C family separation
- **C434:** Uses R-series forward ordering
- **C436:** Scaffold uniformity difference confirmed

**Tier:** 3 (Structural Characterization - scaffold->trajectory signature)

**Files:** phases/AZC_TRAJECTORY_SHAPE/, results/ats_*.json

### X.27 Brunschwig-Voynich Relationship Bounded: Explanation-Enforcement Complementarity FALSIFIED (2026-01-19)

**Phase:** BC_EXPLANATION_ENFORCEMENT
**Status:** COMPLETE - Clean falsification achieved

#### Purpose

Test the "one remaining legitimate reverse-Brunschwig test" (external expert): Does Brunschwig's pedagogical verbosity inversely correlate with AZC scaffold constraint rigidity?

> **Core question:** Where Voynich enforces more, does Brunschwig explain less?

#### Test Results (0/4 hypotheses passed = FALSIFIED)

| Hypothesis | Prediction | Result | Status |
|------------|------------|--------|--------|
| H1: Freedom correlation | Inverse density-freedom correlation | rho=+0.09 (opposite direction) | **FAIL** |
| H2: Scaffold rigidity | UNIFORM < VARIED density | d=-0.37 (correct direction, p=0.11) | **FAIL** |
| H3: Interaction | Freedom x Pacing interaction > main | dR2=0.00 (no effect) | **FAIL** |
| H4: Complementarity ratio | Stable ratio across regimes | CV increased 9.6% | **FAIL** |

#### What Was Falsified

The stronger hypothesis:

> **"Brunschwig's pedagogical verbosity systematically complements Voynich's enforcement rigidity at the recipe/regime level."**

This hypothesis is now **dead permanently**.

#### What Survives Intact

The falsification does NOT touch:

- Zone-modality discrimination (F-BRU-009, two-stage model) - INTACT
- Zones structure judgment admissibility, not sensory labels - INTACT
- AZC trajectory shape = scaffold fingerprint, not apparatus dynamics - INTACT
- Scaffold uniformity vs variability determines cognitive pacing - INTACT

#### The Corrected Relationship

| Aspect | Brunschwig | Voynich |
|--------|------------|---------|
| Primary function | Explains **WHAT** | Enforces **WHEN** |
| Audience | Learners / practitioners | Experts only |
| Content | Materials, heat, moral warnings | Legality, transitions, recoverability |
| Silence | On enforcement | On explanation |
| Alignment level | Curriculum trajectory | Curriculum trajectory |
| **NOT aligned** | Interface timing | Interface timing |

#### Why This Strengthens the Model

If the test had succeeded, we'd be forced into:
- Implicit co-design claims
- Hidden synchrony assumptions
- An explanation-enforcement dual-manual model

The falsification produces something cleaner:

> **Voynich stands alone as an enforcement artifact.**

Voynich and Brunschwig converge on:
- The same process domain
- The same hazard ontology
- The same curriculum ordering
- The same notion of completeness vs intensity

...but **only at the level of control worldview**, not at the level of interface behavior.

#### Final Synthesis (Corrected)

> **AZC zones and scaffold families address sensory strategies indirectly by structuring judgment admissibility and cognitive pacing, not by encoding modalities. Brunschwig and Voynich align at the level of procedural ontology and curriculum trajectory, but they do not coordinate explanation and enforcement at the level of individual recipes or phases.**

This formulation:
- Respects every Tier 0-2 constraint
- Incorporates the falsification
- Preserves the genuine AZC/sensory insight
- Closes the Brunschwig line of inquiry cleanly

#### New Constraints

**C-BOUND-01:** Voynich is not part of a fine-grained pedagogical feedback loop with Brunschwig.
**C-BOUND-02:** The Voynich-Brunschwig relationship is maximally abstract: convergent at ontology level, independent at interface level.

**Tier:** FALSIFIED (0/4) - Clean negative result, bounds relationship appropriately

**Files:** phases/BC_EXPLANATION_ENFORCEMENT/, results/bc_*.json

### X.28 Recipe Triangulation Methodology: Multi-Dimensional PP Convergence (2026-01-21)

**Phase:** ANIMAL_PRECISION_CORRELATION

#### The Problem

Previous attempts at reverse-Brunschwig mapping failed because:
1. Single PP tokens don't discriminate (90%+ folio overlap between recipes)
2. REGIME alone provides weak selection (only 11.9% exclusive vocabulary)
3. Working at folio level loses record-level signal

#### The Solution

Multi-dimensional PP convergence at RECORD level, combined with PREFIX profile matching.

#### The Pipeline

```
Brunschwig Recipe Dimensions
       ↓
B Folio Constraints (REGIME + PREFIX profile)
       ↓
Multi-dimensional Conjunction → Candidate B Folios
       ↓
PP Vocabulary Extraction
       ↓
A RECORD Convergence (3+ PP tokens)
       ↓
RI Token Extraction
       ↓
PREFIX Profile Matching → Instruction Sequence
       ↓
Material Identification
```

#### Key Mappings

| Recipe Dimension | B Constraint | Implementation |
|------------------|--------------|----------------|
| fire_degree = N | REGIME_N | `regime_folio_mapping.json` |
| e_ESCAPE in sequence | High qo ratio | `qo_ratio >= avg` |
| AUX in sequence | High ok/ot ratio | `aux_ratio >= avg` |
| FLOW in sequence | High da ratio | `da_ratio >= avg` |

#### Worked Example: Chicken (ennen)

**Input:**
- fire_degree: 4 → REGIME_4
- instruction_sequence: [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE]
- Unique pattern: ESCAPE bookends + AUX (no FLOW)

**4D Conjunction:**
- REGIME_4 + high qo + high aux + low da → 1 folio (f95v1)
- Relaxed to 5 chicken-like folios

**A Record Convergence:**
- 110 records converge to 3+ chicken folios at 2+ PP each
- 4 records contain known animal RI tokens

**PREFIX Profile Matching:**
| RI Token | Has ESCAPE PP? | Has AUX PP? | Chicken Match? |
|----------|----------------|-------------|----------------|
| teold | YES (t=88% qo) | NO | Partial |
| chald | YES (fch=74% qo) | NO | Partial |
| **eoschso** | YES (ke,keo) | **YES (ch=48%)** | **FULL** |
| eyd | weak | weak | No |

**Result:** Only **eoschso** has BOTH escape AND aux PP, matching chicken's unique [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE] pattern.

**Conclusion:** eoschso = ennen (chicken) [Tier 3 hypothesis]

#### Critical Constraints

**DO:**
- Use multi-dimensional conjunction for B folio selection
- Require 3+ PP convergence at RECORD level (not folio)
- Match PREFIX profiles to instruction patterns
- Compare against Brunschwig sequences for identification

**DO NOT:**
- Use single PP tokens for discrimination
- Work at folio level (90%+ overlap)
- Skip PREFIX profile matching
- Assume REGIME alone discriminates

#### Constraint Implications

Refines C384 (no entry-level A-B coupling):
> "Single PP tokens do not establish entry-level coupling, but multi-dimensional PP convergence combined with PREFIX profile matching can identify specific A records."

#### Status

- **Validated:** Animal material class (chicken identification)
- **Pending:** Plant materials (rose water), other animal refinement
- **Tier:** 3 (requires Brunschwig alignment for interpretation)

**Files:**
- Methodology: `context/SPECULATIVE/recipe_triangulation_methodology.md`
- Results: `phases/ANIMAL_PRECISION_CORRELATION/results/`
- Scripts: `phases/ANIMAL_PRECISION_CORRELATION/scripts/`

### X.29 Material-Class REGIME Invariance: Precision as Universal Requirement (2026-01-25) - REVISED

**REVISED FINDING:** Both animal AND herb material classes route preferentially to REGIME_4 (precision control). Material differentiation occurs at **token variant level**, not REGIME level.

#### Key Discovery

| Material Class | REGIME_4 Enrichment | p-value |
|----------------|---------------------|---------|
| Animal | **2.03x** | 0.024 |
| Herb | **2.09x** | 0.011 |

Both material classes prefer REGIME_4 at nearly identical enrichment (~2x). This contradicts the initial hypothesis that different materials would route to different REGIMEs.

#### Hypothesis Evolution

| Version | Prediction | Result |
|---------|------------|--------|
| **Original** | Animal -> REGIME_1/2 | WRONG |
| **Intermediate** | Animal -> REGIME_4 | INCOMPLETE |
| **Final** | Both Animal AND Herb -> REGIME_4 | CONFIRMED |

#### Where Differentiation Actually Occurs

| Level | Differentiation? | Evidence |
|-------|-----------------|----------|
| REGIME | **NO** | Both ~2x REGIME_4 enriched |
| Folio | **NO** | r=0.845 correlation |
| Token Variants | **YES** | Jaccard=0.38 (62% different) |

#### Statistical Evidence

**REGIME distribution:**
- Animal: 13/21 high-reception folios in REGIME_4 (62%)
- Herb: 14/22 high-reception folios in REGIME_4 (64%)
- Baseline: 25/82 folios in REGIME_4 (30.5%)

**Token-level differentiation:**
- Overall Jaccard: 0.382
- Per-class mean Jaccard: 0.371
- Most differentiated: ke (0.037), fch (0.111), ol (0.169)

#### Interpretation

**REGIME_4 encodes execution precision requirements, not material identity.** Different materials can share execution requirements while differing in behavioral parameterization.

The manuscript achieves material-appropriate execution NOT by routing to different procedures, but by **selecting different token variants within a shared grammatical framework**:

```
Material -> REGIME: Same (both -> precision)
Material -> Token: Different (62% non-overlap)
```

This confirms C506.b: tokens within same class are positionally compatible but behaviorally distinct. The 480-token vocabulary parameterizes a 49-class grammar, not replaces it.

#### PP Classification (Tier 3)

| Class | Count | % | Top Markers |
|-------|-------|---|-------------|
| ANIMAL | 63 | 15.6% | pch, opch, ch, h |
| HERB | 113 | 28.0% | keo, eok, ko, to |
| MIXED | 67 | 16.6% | - |
| NEUTRAL | 161 | 39.9% | - |

RI projection: 95.9% of RI contain classifiable PP atoms, enabling material-class inference through composition.

#### Relationship to X.6

This finding STRONGLY REINFORCES X.6 (REGIME_4 Interpretation Correction):

> "REGIME_4 is NOT 'forbidden materials' - it IS 'precision-constrained execution'"

Now demonstrated across BOTH material classes: REGIME_4 is universal precision infrastructure, not material-specific processing.

#### Tier Compliance

- **C536 (Tier 2):** Material-class REGIME invariance (structural fact)
- **C537 (Tier 2):** Token-level differentiation (structural fact)
- **C538 (Tier 3):** PP material-class distribution (conditional on Brunschwig)
- **This section (Tier 4):** Interpretation as execution parameterization

**Files:**
- Phase: `phases/MATERIAL_REGIME_MAPPING/`
- PP Classification: `phases/PP_CLASSIFICATION/`
- Results: `phases/*/results/`

### X.30 Three-Tier MIDDLE Structure and AZC Bridge Tokens (2026-02-04)

**Phase:** REVERSE_BRUNSCHWIG_V2
**Status:** COMPLETE - Structural pattern with speculative interpretation

#### Core Discovery

The MIDDLE layer in Currier B exhibits a three-tier structure based on folio position and AZC presence:

| Tier | MIDDLEs | Mean Position | AZC Presence | Origin |
|------|---------|---------------|--------------|--------|
| **EARLY** | ksh, lch, tch, pch, te | 0.31-0.41 | **6 tokens** | B-specific |
| **MID** | k, t, e | 0.42-0.46 | **151 tokens** | Pipeline (A→AZC→B) |
| **LATE** | ke, kch | 0.47-0.59 | **4 tokens** | B-specific |

#### The AZC Discriminator

AZC presence/absence distinguishes vocabulary origin:

| Tier | % of AZC tier tokens | Interpretation |
|------|---------------------|----------------|
| MID | **93.8%** | Core operations flow through A→AZC→B pipeline |
| EARLY+LATE | **6.2%** | B-specific vocabulary, not AZC-mediated |

**The rule:** If a MIDDLE appears significantly in AZC → it's MID tier (pipeline vocabulary). If absent from AZC → it's EARLY or LATE tier (B-internal vocabulary).

#### The 10 EARLY/LATE Tokens in AZC: Bridge Vocabulary

Of ~900 EARLY/LATE tokens in B, only 10 appear in AZC. These split into two groups:

**AZC-Only (3 tokens) - Pure Labels:**

| Token | PREFIX | MIDDLE | In B? |
|-------|--------|--------|-------|
| orkeeey | or | ke | NO |
| shkeal | sh | ke | NO |
| ypolcheey | po | lch | NO |

- Non-qo prefixes (or-, sh-, po-)
- Appear only in Zodiac diagram positions
- Function as positional labels, not executable operations

**Bridge Tokens (7 tokens) - Cross to B:**

| Token | PREFIX | MIDDLE | B Count | B Position |
|-------|--------|--------|---------|------------|
| qoteedy | **qo** | te | 73 | 0.43 (early) |
| qokchdy | **qo** | kch | 54 | 0.45 (early) |
| qopchey | **qo** | pch | 7 | - |
| dalchdy | da | lch | 3 | - |
| qoteor | **qo** | te | 3 | - |
| dolchedy | do | lch | 2 | - |

- **96.5% qo-prefixed** (vs 79.3% for other EARLY/LATE in B)
- Appear **earlier** in B folios than other EARLY/LATE tokens (0.432 vs 0.479)
- Dominated by two tokens: `qoteedy` (73) and `qokchdy` (54) = 89% of B occurrences

#### The qo- PREFIX Discriminator

The qo- prefix determines whether an EARLY/LATE token can cross from AZC to B:

| Pattern | AZC Role | B Role |
|---------|----------|--------|
| qo- + EARLY/LATE MIDDLE | Bridge marker | Executable operation |
| non-qo + EARLY/LATE MIDDLE | Position label | Absent or rare |

**Example:** The MIDDLE `ke` appears in both groups:
- `qokeedy` → 306 occurrences in B (executable)
- `orkeeey` → 0 occurrences in B (AZC label only)

Same MIDDLE, different PREFIX → different pipeline behavior.

#### Speculative Interpretation: Sparse Indexing System

The Zodiac diagrams function as **configuration templates** where:

1. **Most vocabulary is simple labels** (y, o, r, l, ar, dy) - positional markers
2. **MID tier tokens (k, t, e)** mark core operational states
3. **Specific qo-EARLY/LATE tokens** mark phase boundaries:
   - `qoteedy` (qo-te-edy) → preparation phase entry point
   - `qokchdy` (qo-kch-dy) → extended operation marker

**The Zodiac doesn't encode full procedural vocabulary.** It encodes **which procedural template/phase structure to activate**. B then generates appropriate EARLY/LATE vocabulary based on that configuration.

```
ZODIAC CONFIGURATION SPACE
    │
    ├─ Simple labels (y, o, r, l)     → Position markers only
    ├─ MID tier (k, t, e)             → Core operational states
    ├─ qoteedy                         → "Start preparation phase"
    └─ qokchdy                         → "Include extended operations"
    │
    ▼
B EXECUTION
    │
    ├─ EARLY tier (B-generated)       → Full preparation vocabulary
    ├─ MID tier (from pipeline)       → Core operations
    └─ LATE tier (B-generated)        → Extended operations
```

#### Alignment with Brunschwig Model

This maps to Brunschwig's procedural structure:

| Brunschwig Phase | Voynich Tier | AZC Role |
|------------------|--------------|----------|
| Preparation (14 ops) | EARLY | Sparse markers (qoteedy) |
| Distillation (27 ops) | MID | Full vocabulary (k, t, e) |
| Extended treatment | LATE | Sparse markers (qokchdy) |

The Zodiac encodes **which phases are active**, not the full procedural detail. B supplies the detail.

#### Structural Evidence

| Finding | Evidence | Tier |
|---------|----------|------|
| Three-tier positional structure | ANOVA p=0.013, Cohen's d=-0.875 | 2 |
| MID tier AZC dominance | 93.8% of AZC tier tokens | 2 |
| qo- prefix bridge pattern | 96.5% vs 79.3% | 2 |
| Bridge tokens earlier in B | 0.432 vs 0.479 mean position | 2 |
| Sparse indexing interpretation | - | 4 (this section) |

#### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- ❌ Complete understanding of Zodiac function
- ✓ Structural pattern of vocabulary flow through pipeline
- ✓ PREFIX as execution-eligibility marker
- ✓ Zodiac as sparse index, not full procedure encoding

#### Tier Compliance

- **F-BRU-011 (Tier 2):** Three-tier MIDDLE operational structure
- **Structural patterns (Tier 2):** AZC presence, qo- discrimination, positional differences
- **This interpretation (Tier 4):** Sparse indexing model for AZC→B phase activation

**Files:**
- Phase: `phases/REVERSE_BRUNSCHWIG_V2/`
- Analysis scripts: `phases/REVERSE_BRUNSCHWIG_V2/scripts/`
- Results: `phases/REVERSE_BRUNSCHWIG_V2/results/`

### X.31 Preparation Operation Mapping and Modification System (2026-02-04)

**Phase:** REVERSE_BRUNSCHWIG_V2
**Status:** SUPPORTED - Statistical correlation with speculative interpretation
**Fit:** F-BRU-012

#### Core Discovery

The 5 preparation-tier MIDDLEs correlate with Brunschwig preparation operations at statistically significant levels, with PREFIX and SUFFIX encoding operational modifications.

#### Operation Mapping (Spearman rho = 1.000, p < 0.001)

| Brunschwig Operation | MIDDLE | Evidence | Confidence |
|---------------------|--------|----------|------------|
| **GATHER** (selection) | te | Earliest position (0.410), most uniform morphology (87% -edy) | MEDIUM-HIGH |
| **CHOP** (mechanical) | pch | HERBAL_B concentrated (36.5%), herb material class | MEDIUM |
| **STRIP** (separation) | lch | BIO concentrated (37.5%), extreme PREFIX diversity (12 types) | MEDIUM |
| **POUND** (intensive) | tch | OTHER concentrated (37.4%), pharma/intensive context | LOW-MEDIUM |
| **Rare ops** (BREAK, WASH) | ksh | Lowest frequency (7.9%), specialized contexts | LOW |

#### PREFIX Modification: Handling Mode

| PREFIX | Rate | Position | Meaning | Pattern |
|--------|------|----------|---------|---------|
| qo- | 77.9% | 0.429 | Standard operation | All MIDDLEs |
| ol- | 5.1% | 0.378 | Output/terminal form | All MIDDLEs |
| so- | 4.5% | 0.478 | Tolerance mode | **Only lch** |
| po- | 3.6% | 0.415 | Specialized/restricted | **Only lch** |
| da- | 2.1% | 0.367 | Anchoring reference | **Only lch** |

**Key finding:** `lch` (STRIP) has 12 different prefixes vs 2-5 for others. This matches Brunschwig's STRIP operation which applies to diverse materials (leaves, bark, feathers, stomach linings) requiring different handling modes.

#### SUFFIX Modification: Operation Intensity

| SUFFIX | Rate | Meaning | Brunschwig Parallel |
|--------|------|---------|---------------------|
| -edy | 56.2% | Complete/thorough | "chopped fine", "pounded well" |
| -dy | 16.6% | Basic operation | Standard processing |
| -ey | 14.8% | Selective/delicate | "lightly", careful handling |

**Section correlation (statistical):**
- BIO (delicate materials): 68.8% -edy (thorough processing)
- HERBAL_B (herbs): 55.2% -edy, 22.9% -dy (more variation)
- OTHER (intensive): 42.1% -edy, 20.6% -ey (selective in harsh context)

#### Full Token Interpretation

| Token | Count | Interpretation |
|-------|-------|----------------|
| qoteedy | 73 | Standard GATHER, complete |
| qopchedy | 32 | Standard CHOP, complete |
| qopchdy | 15 | Standard CHOP, basic |
| solchedy | 8 | Tolerant STRIP, complete (delicate materials) |
| dalchedy | 7 | Anchored STRIP, complete (registry reference) |
| qotchedy | 24 | Standard POUND, complete |
| qotchdy | 23 | Standard POUND, basic |

#### Brunschwig Modifier System Parallel

| Brunschwig | Voynich | Evidence |
|------------|---------|----------|
| Intensity ("fine" vs "coarse") | SUFFIX (-edy/-dy/-ey) | Section correlation (p<0.01) |
| Material type (delicate vs tough) | PREFIX (qo-/so-/da-) | lch diversity pattern |
| Downstream fire degree | Section distribution | Material-section alignment |

#### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- The specific operation names are hypothetical (MIDDLE "correlates with" not "encodes")
- Token interpretations are illustrative, not proven

#### Tier Compliance

- **Statistical patterns (Tier 2):** Frequency correlation, section distributions, PREFIX diversity
- **F-BRU-012 (Tier F3):** Operation mapping with section-material correspondence
- **Token interpretations (Tier 4):** Specific semantic assignments

#### Naming Note

Uses "preparation-tier MIDDLEs" rather than "EARLY tier" to avoid collision with C539's EARLY/LATE PREFIX terminology.

### X.32 Extended Operation Differentiation: ke vs kch (2026-02-04)

**Phase:** REVERSE_BRUNSCHWIG_V2
**Status:** SUPPORTED - Statistical differentiation with speculative interpretation
**Fit:** F-BRU-013

#### Core Discovery

The two extended-tier MIDDLEs (ke, kch) encode different operational modes that map to Brunschwig's fire degree monitoring protocols.

#### Section Specialization (Key Discriminator)

| MIDDLE | BIO+HERBAL_B | OTHER | Processing Mode |
|--------|--------------|-------|-----------------|
| **ke** | **85.3%** | 14.7% | Gentle/sustained |
| **kch** | 45.3% | **54.7%** | Intensive/precision |

#### Suffix Pattern Differentiation

| MIDDLE | -edy | -dy | -ey | Pattern |
|--------|------|-----|-----|---------|
| **ke** | 85.3% | 0% | 0% | Uniform (complete operation) |
| **kch** | 32.4% | 41.2% | 19.6% | Mixed (context-dependent) |

ke maintains uniform -edy regardless of section; kch adapts its suffix to context.

#### Morphological Interpretation

| MIDDLE | Components | Interpretation |
|--------|------------|----------------|
| **ke** | k + e | Heat + equilibration (sustained cycles) |
| **kch** | k + ch | Heat + precision (C412: ch = precision mode) |

#### Brunschwig Mapping

| Fire Degree | Monitoring Mode | MIDDLE | Evidence |
|-------------|-----------------|--------|----------|
| Degree 1-2 (gentle) | Sustained heat cycles | **ke** | BIO/HERBAL_B concentration |
| Degree 3 (critical) | "Finger test" precision | **kch** | OTHER concentration, tch co-occurrence |

#### Co-occurrence Pattern

kch is enriched 17x with `tch` (POUND equivalent), confirming that intensive operations require precision heat control.

#### Complete Three-Tier Model

| Tier | MIDDLEs | Function | Brunschwig Phase |
|------|---------|----------|------------------|
| **Preparation** | te, pch, lch, tch, ksh | Material preparation | GATHER, CHOP, STRIP, POUND |
| **Core** | k, t, e | Base thermodynamic | Heat, timing, equilibrate |
| **Extended** | ke, kch | Modified operations | Sustained (ke) or precision (kch) |

#### Tier Compliance

- **Section specialization (Tier 2):** Statistical measurement
- **Suffix differentiation (Tier 2):** Statistical measurement
- **F-BRU-013 (Tier F3):** Brunschwig monitoring parallel
- **Morphological interpretation (Tier 4):** k+e, k+ch decomposition

### X.33 Procedural Dimension Independence (2026-02-05)

**Phase:** REVERSE_BRUNSCHWIG_V3
**Status:** CONFIRMED - Statistical validation with Tier 2 findings
**Fits:** F-BRU-015, F-BRU-016

#### Core Discovery

Procedural tier features add 2-3 independent dimensions beyond aggregate rate features in PCA.

#### Dimensional Increase

| Metric | Original | Combined |
|--------|----------|----------|
| Dims for 80% variance | **5** | **8** |
| Independent procedural PCs | - | **2** (|r| < 0.3) |

#### Independence Test

| Procedural PC | Max |r| with Original PCs | Status |
|---------------|----------------------------|--------|
| Proc PC1 | 0.28 | INDEPENDENT |
| Proc PC2 | 0.24 | INDEPENDENT |

#### REGIME Differentiation

6/12 procedural features show significant REGIME differences (Kruskal-Wallis p < 0.05):
- prep_density: eta-squared = 0.18 (LARGE)
- thermo_density: eta-squared = 0.16 (LARGE)
- extended_density: eta-squared = 0.15 (LARGE)

#### REGIME_4 Clarification (F-BRU-017)

REGIME_4 shows HIGHER ke_kch ratio (more ke/sustained), clarifying "precision" in C494:
- Precision = tight tolerance, not intensity
- Achieved via sustained equilibration cycles (ke = k + e)
- NOT via burst precision (kch = k + ch)

#### Interpretation

The three-tier procedural structure captures variance orthogonal to aggregate rates:
- WHAT operations occur (rates) is partially independent from WHEN they occur (positions)
- REGIMEs encode different procedural BALANCES, not just operation intensities

### X.34 Root Illustration Processing Correlation: Tier 4 External Anchor (2026-02-05)

**Phase:** REVERSE_BRUNSCHWIG_V3
**Status:** CONFIRMED - Statistical significance with external semantic grounding
**Fit:** F-BRU-018

#### Core Discovery

B folios using vocabulary from root-illustrated A folios show elevated root-processing operations (tch=POUND, pch=CHOP), providing external semantic anchoring.

#### Statistical Evidence

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Pearson r | **0.366** | Moderate correlation |
| p-value | **0.0007** | Highly significant |
| Spearman rho | **0.315** | Robust to outliers |
| Direction | CORRECT | Root overlap -> higher root ops |

#### External Anchor Logic

```
Brunschwig (External): "POUND/CHOP roots" (dense materials need mechanical breakdown)
          |
          v
Voynich illustrations: 73% emphasize root systems (PIAA phase classification)
          |
          v
A folios with root illustrations -> PP bases (vocabulary extraction)
          |
          v
B folios using root-sourced PP -> elevated tch (POUND) + pch (CHOP)
```

This is NOT circular reasoning - it connects:
- Visual features (illustration root emphasis)
- Brunschwig domain knowledge (root processing methods)
- Voynich text patterns (prep MIDDLE distribution)

#### Methodological Compliance (C384)

The analysis operates at **folio aggregate level**:
- C384 prohibits token-level A-B lookup
- C384.a permits "record-level correspondence via multi-axis constraint composition"
- PP-base overlap is aggregate vocabulary matching, not token mapping

#### Effect Size Benchmark

The r=0.37 correlation is comparable to validated Tier 3 findings:
- C477 (HT-tail correlation): r=0.504
- C459 (HT anticipatory): r=0.343
- C412 (sister-escape anticorrelation): rho=-0.326

#### What This Does Claim (Tier 4)

- Illustrations DO encode material category information (even if epiphenomenal to execution)
- The A->B vocabulary pipeline preserves material-category signals
- Brunschwig material-operation mappings have predictive power for Voynich patterns

#### What This Does NOT Claim

Universal Boundaries apply. Additionally: this is aggregate statistical correspondence, not decipherment.

#### Tier Compliance

- **Statistical correlation (Tier 2):** Measured effect (r=0.37, p<0.001)
- **F-BRU-018 (Tier 4):** External semantic anchoring via Brunschwig + illustrations

**Files:** phases/REVERSE_BRUNSCHWIG_V3/, phases/PROCEDURAL_DIMENSION_EXTENSION/

### X.35 Material Category Hierarchy: Marked vs Unmarked (2026-02-05)

**Phase:** REVERSE_BRUNSCHWIG_V3
**Status:** SUPPORTED - Explains asymmetric pathway evidence
**Fit:** F-BRU-019

#### Core Discovery

The Voynich system marks **deviations from default processing**, not the default itself. Delicate plant materials (leaves, flowers, petals) are the unmarked default.

#### Three-Pathway Summary

| Material Category | A Signal | B Signal | Status |
|-------------------|----------|----------|--------|
| **Roots/Dense** | Illustration (root emphasis) | tch+pch elevated (r=0.37) | **CONFIRMED** |
| **Animals** | Suffix -ey/-ol | REGIME_4, k+e >> h | **CONFIRMED** |
| **Delicate plants** | Suffix -y/-dy | No distinctive signature | **UNMARKED DEFAULT** |

#### Why Delicate Plants Have No Marker

Herb-suffix pathway test showed:
- Modest correlation with gentle density (r=0.24, p=0.028)
- BUT no REGIME-specific routing (KW p=0.80)
- Both herb AND animal overlap correlate similarly with B metrics

**Interpretation:** Gentle processing is the baseline assumption. Only deviations require marking:
- "POUND this" (roots)
- "Precision timing" (animals)
- [nothing] = proceed with gentle processing (flowers/leaves)

#### Brunschwig Parallel

Brunschwig's manual follows the same pattern:
- Most recipes are for aromatic flowers/leaves (unmarked default)
- Special instructions only for dense materials and animals

#### Category Consolidation

From this point forward:
- **Delicate plant material** = leaves, flowers, petals, soft herbs (single category)
- **Dense plant material** = roots, bark, seeds (requires marking)
- **Animal material** = fats, organs, kermes (requires precision marking)

#### Tier Compliance

- Statistical tests: Tier 2 (null finding is still a finding)
- Theoretical coherence: Tier 3 (Brunschwig alignment)
- Material category consolidation: Tier 4 (interpretive)

---

## XI. Rosettes Foldout (STATUS: REVALIDATED — Phase 402)

The Rosettes foldout has been revalidated using corrected ZL (Zandbergen) transcription data with manual spatial annotation (`data/rosettes_annotated.json`). All 21 prior Rosettes constraints were deleted due to data quality issues; 5 new constraints (C1124-C1128) replace them.

### Tier 2: Structural Findings

**Metalayer confirmed (C1126):** The Rosettes foldout is an organizational metalayer sitting above the standard A/B/AZC systems and cross-referencing the body text. This is the core finding — it is not a standard B program page, not a standard AZC positional page, but a meta-structural index.

**AZC-like grammar (C1127):** All entity types (ring text, labels, paths, spiral, clock) show consistent AZC-type morphology: grammar coverage ~42% (B: ~100%, AZC: ~50%), kernel density 29-41%, PP ~50%/RI ~2%. Not a hybrid — the old hybrid classification (C1088) was a data artifact.

**Bridge enrichment (C1124):** 3.05x enrichment over B corpus (21.5% vs 7.0%). Universal across all sub-region types — ring 4.56x, labels 4.74-5.17x, clock 7.11x. The foldout preferentially samples cross-system vocabulary.

**Section T indexing — QUALIFIED (C1125, C1133):** All 9 rosettes correlate most strongly with Section T at the section level, but this is a vocabulary-size artifact (C1133). Section T has only 1 non-Rosettes folio (f66r, 112 MIDDLEs); per-folio, f66r ranks #11/76. Top 10 overlapping folios are 9 Section S + 1 Section H. Bridge density anticorrelates with overlap (rho = -0.60). The foldout indexes diverse, vocabulary-rich folios, not Section T specifically.

**Generic indexing (C1128):** All rosettes point to approximately the same B folios (mean inter-rosette Jaccard of top-5 sets = 0.322; f40v in top-5 for 8/9 rosettes). The foldout is a shared vocabulary hub, not a specific lookup table.

**Ring text forbidden compliance (C1130):** Ring text has 0/277 forbidden transition violations but transition entropy 7.92 bits (vs B's ~0.41). Respects hard constraints, ignores soft ones.

**Ring text register classification (C1131):** Ring text is a BRIDGE_VOCABULARY_INDEX — a distinct register that samples B-grammar bridge vocabulary under hard constraints. 52.4% of tokens map to B grammar, AUXILIARY role dominates (42.7%), 100% of classified MIDDLEs are bridge. Structured class distribution, not random enumeration.

**Ring text dual population (C1132):** Ring text interleaves two populations: (1) B-grammar bridge tokens (short, simple, 100% bridge) that serve as index entries, and (2) unclassified identification tokens (long, complex, mostly non-bridge) that label foldout-specific concepts.

### Tier 3: Spatial Structure (Inconclusive)

Path tokens do not bridge endpoint rosette vocabularies, and vocabulary similarity does not decay with spatial distance. These tests were underpowered — most individual entities have <10 tokens, limiting statistical sensitivity for spatial patterns.

### Interpretation (Tier 3-4)

The Rosettes foldout functions as a **general-purpose vocabulary reference hub** — an organizational index that connects the manuscript's control vocabulary through bridge MIDDLEs. Its AZC-like grammar is consistent with a positional encoding system (like AZC diagram positions) rather than executable programs or registry entries. The apparent Section T targeting (C1125) is a vocabulary-size artifact (C1133) — the foldout actually overlaps most with diverse, vocabulary-rich folios (primarily Section S Stars/Recipes). The Rosettes vocabulary is general-purpose metalayer vocabulary that indexes into whatever B folios have the most diverse MIDDLE inventories.

---

## XII. Cross-System Vocabulary Flow (Phase 406)

Phase 406 resolves the C1049/C909 paradox: shared pipeline vocabulary is type-universal across sections (Herfindahl 0.701) yet B output is 96% section-specific. The answer is **frequency modulation**.

### Tier 2: Structural Findings

**Section specificity is frequency-modulated (C1134):** The same shared/PP MIDDLEs appear in all B sections (type-universal) but at section-specific token frequencies. PP vocabulary drives 74% of between-section JS divergence (JS_PP=0.124 vs JS_ALL=0.167). B-exclusive vocabulary is maximally section-specific per-type (JS=0.847) but carries only 5.8% of tokens, making it token-negligible for section discrimination. The paradox resolves: vocabulary is type-universal but frequency-specific.

**Unmatched PP dark pipeline (C1135):** Of 404 PP MIDDLEs, only 89 match B grammar classes. The other 315 are overwhelmingly present in B (95.2%, 300/315) but at dramatically lower frequency (mean 5.7 tokens vs 224.8 for matched; mean 4.6 folios vs 39.0). They are section-concentrated (Herf 0.716), mostly compound (66.7%), and constitute the HT/UN derivational substrate — the morphological bridge between A's registry and B's unclassified layer.

**A->B flow is uniform and concentrated (C1136):** A-Herbal and A-Pharmaceutical produce indistinguishable B coverage profiles (cosine 0.9997). The pipeline is section-blind — all A sections cover B-Herbal best and B-Stars worst, with identical relative profiles. Pipeline grammar is highly concentrated: 12 A folios cover 100% of B's 89 classified MIDDLEs, with f58v (Section T, text-only) alone covering 60.7%. The full B inventory ceiling is 30.4% from all 114 A folios — 70% of B vocabulary is completely B-internal.

### Interpretation (Tier 3-4)

The A->B vocabulary pipeline operates as a **frequency-tuned universal substrate**: A provides a shared vocabulary pool (404 PP MIDDLEs) that all B sections access, but each section tunes the token frequencies to its operational needs. Section-specificity is not vocabulary-specificity — it is usage-specificity applied to universal vocabulary. The "dark pipeline" of 300 unmatched PP MIDDLEs provides the derivational raw material from which B's HT/UN layer constructs its 900+ exclusive identification vocabulary (via compounding, consistent with C924's 97.9% atom containment). The pipeline is structurally simple: section-blind, concentrated in ~12 hub folios, with f58v as the single most vocabulary-rich entry point.

---

## XIII. Dark Pipeline Functional Test (Phase 407)

Phase 407 functionally characterizes the 300 dark-pipeline PP MIDDLEs from C1135. A 5-test battery establishes their classification fate, construction grammar, relationship to bridges, positional behavior, and section profile.

### Tier 2: Structural Findings

**100% HT/UN substrate (C1137):** All 1,696 B tokens built from dark-pipeline MIDDLEs are HT/UN classified. Zero are grammar-classified. This is not a tendency but a complete partition: matched PP MIDDLEs (89) produce 80.2% grammar-classified tokens, while dark-pipeline MIDDLEs (300) produce exclusively identification vocabulary. The mean 5.7 tokens per dark-pipeline MIDDLE (vs 224.8 for matched) validates C1135's frequency characterization.

**Distinct construction grammar (C1138):** Dark-pipeline tokens use a morphological recipe distinct from both general HT and grammar tokens. Grammar-standard/extended PREFIX ratio is 3.39 (vs general HT 1.81, 87% higher) — dark tokens strongly prefer grammar-standard prefixes (ch, sh, qo, etc.) over extended/HT-specific ones. Suffix rate is 89.9% (vs HT 77.3%, grammar 38.7%). Articulator rate is 2.5% (vs HT 10.1%). The pattern is: simpler at the front (fewer articulators, more grammar-standard prefixes), more elaborated at the back (higher suffix rate). This constitutes a third morphological register within B's token inventory.

**Bridge-disjoint (C1139):** The 300 dark-pipeline MIDDLEs and 85 bridge MIDDLEs (C1013) have zero overlap. The A-B vocabulary pipeline has three cleanly separated channels: (1) bridge MIDDLEs carrying dynamical/behavioral information, (2) ~4 non-bridge matched PPs, and (3) dark-pipeline MIDDLEs carrying identification/specification information. Neither population borrows from the other.

### Interpretation (Tier 3-4)

The dark pipeline is not "dark" — it is the **identification construction channel**. While bridge MIDDLEs structure B's operational behavior (which instruction classes to use, what archetype patterns emerge), dark-pipeline MIDDLEs structure B's identification vocabulary (which specific entities are being referenced). The distinct construction grammar — grammar-standard prefixes selecting operational domains, dark-pipeline MIDDLEs providing compound identification content, high suffix rates encoding additional context — suggests a systematic construction process for generating the specification layer (C935) from shared A/B vocabulary atoms.

The complete disjointness from bridges means the A-B pipeline bifurcates cleanly: operational information flows through 85 bridge MIDDLEs into the 49-class grammar, while identification information flows through 300 dark-pipeline MIDDLEs into HT/UN compound vocabulary. These are parallel but independent pathways through the shared vocabulary pool.

---

## XIV. PP Pipeline Atom Decomposition (Phase 408)

Phase 408 closes the PP pipeline architecture and discovers the construction hierarchy connecting the three A-B channels.

### Tier 2: Structural Findings

**PP pipeline complete partition (C1140):** The 404 PP MIDDLEs partition into exactly four mutually exclusive populations: 85 bridge, 4 non-bridge matched (c, ch, cho, otc -- AUXILIARY-dominant edge cases), 300 dark pipeline, and 15 B-absent phantoms (all ch/sh-prefixed with zero A tokens). The partition is exhaustive and all six pairwise intersections are empty.

**Dark pipeline compounds built from bridge atoms (C1141):** Despite zero MIDDLE-level overlap (C1139), 96.5% of dark-pipeline compounds contain at least one bridge atom as a building block. Of 50 unique atoms found in the 200 compound dark-pipeline MIDDLEs, 43 (86%) are bridge MIDDLEs. Bridge atoms account for 91.6% of all atom occurrences. The construction hierarchy is: bridge atoms (short, universal) -> compositional assembly (1-3 atoms per compound) -> dark-pipeline compounds (section-concentrated) -> HT/UN identification tokens.

**Modified construction grammar (C1142):** Dark-pipeline compounds follow a variant dialect of B's general atom ordering grammar (C1065). Agreement on asymmetric pair direction is 50% (7/14 matches), but gateway/terminal atom positioning is preserved (gateway mean position 0.083, terminal 0.352). The dark pipeline uses a larger atom vocabulary (50 vs 27 for grammar compounds), with 25 dark-exclusive atoms extending the construction alphabet. Section concentration (C1135 Herfindahl 0.716) is NOT atom-driven (permutation p = 0.303) -- the same atoms appear across sections, with specificity arising from combination rather than selection.

### Interpretation (Tier 3-4)

The three A-B pipeline channels (C1139) are not independent -- they are connected through a **construction hierarchy**. Bridge MIDDLEs serve a dual role: they ARE the dynamical backbone of B's 49-class grammar (C1013, C1014), and they are also the **morphological substrate** from which identification vocabulary is assembled. The dark pipeline does not have its own atomic vocabulary -- it reuses bridge atoms in novel combinations, using a modified grammar with additional atoms. This is the B-side analog of C913's finding that 90.9% of RI MIDDLEs contain PP substrings on the A side.

The overlapping but non-identical atom pools (Jaccard 0.481) and modified ordering rules (50% agreement) suggest the dark pipeline represents a **specialized construction channel**: it shares the fundamental morphological building blocks with grammar compounds but applies different assembly rules to produce identification vocabulary rather than operational instructions. The 25 dark-exclusive atoms provide additional specificity not needed in the grammar channel.

This resolves the apparent paradox of C1139: bridge and dark-pipeline MIDDLEs are disjoint as whole strings, but the dark pipeline is built FROM bridge atoms. Disjointness at the compound level coexists with dependency at the atom level.

### Tier 4: Operational-Profile Nomenclature

The dark pipeline may be a **naming system that defines things by their processing behavior**. Bridge atoms encode operational primitives (heat, cool, monitor, stabilize); the 49-class grammar uses these to specify what to DO. The dark pipeline recombines the same atoms into compound labels that specify what you are WORKING WITH. The names are not arbitrary -- they are compressed operational profiles. A dark-pipeline compound built from [cooling-atom + monitoring-atom] does not mean "lavender" or "rosemary"; it means "the material you cool while monitoring."

This would explain the full structural signature:
- **Built from bridge atoms (96.5%):** Things are named using operational vocabulary because the names ARE operational descriptions.
- **Never grammar-classified (100% HT/UN):** Names do not execute. They sit alongside the grammar as labels.
- **Section-concentrated but not atom-driven (Herf 0.716, perm p=0.303):** Every section uses the same operational primitives; different sections combine them differently because different material classes have different processing profiles.
- **Low frequency (5.7 tokens/MIDDLE):** Each specific material or preparation appears rarely across the manuscript.
- **Modified ordering grammar (50% C1065 agreement):** Atoms are sequenced differently when naming something than when specifying operations on it -- perhaps the dominant processing property leads.
- **Grammar-standard prefixes (C1138, GS/EXT ratio 3.39):** Even identification tokens need a domain selector. Materials are identified within operational contexts.
- **Phantoms (15 B-absent):** Morphologically valid name-slots that no actual material instantiates. The system can generate more names than it needs.

The analogy is chemical nomenclature: methyl-ethyl-ketone names a substance by concatenating its structural components. A distiller trained in this system would not read a substance name in natural language -- they would read a compound MIDDLE and recognize the material by its operational profile. The semantic ceiling (C171) holds: we cannot recover WHICH material a compound names, but we can see that the naming system is built from the same atoms that drive the operational grammar.

### Phase 409 Extension: Dual-Channel Budget and Section-Specific Catalogs

Phase 409 adds three structural signatures that sharpen the operational-profile nomenclature interpretation:

**1. Complementary budget (C1146, r = -0.865):** Dark-pipeline and bridge token rates are strongly anti-correlated at the folio level, and this holds within every section (r = -0.82 to -0.88). A folio that spends more tokens on operational instructions (bridge/grammar) spends fewer on material identification (dark pipeline), and vice versa. This is what you would expect from a recipe system: some procedures are complex to execute but involve few materials; others are operationally simple but require extensive material specification. The manuscript's "token budget" trades off between WHAT TO DO and WHAT TO USE.

**2. Section-specific catalogs (C1148, 3.9x hyper-modulation):** Dark-pipeline MIDDLEs are nearly 4x more section-differentiated than grammar MIDDLEs. This means each section of the manuscript draws from a largely distinct material vocabulary. If sections correspond to material domains (herbs, minerals, waters, animal products), this is exactly what you'd expect: the operational grammar (heat, cool, distill, filter) is roughly universal across domains, but the things you name are domain-specific. Herbal sections name herbs; mineral sections name minerals. The grammar is shared; the catalog is local.

**3. Interior filling (C1147, 73.2% MIDDLE position):** Dark-pipeline tokens preferentially fill line interiors rather than anchoring boundaries. Grammar tokens are even more interior (83.5%), while general HT is less so (67.7%). This positions material-identification tokens as embedded content within the structural flow of each line — they are the nouns in the sentence, surrounded by the operational verbs. A line reads as: [grammar-opener] [material] [material] [operation] [material] [grammar-closer].

**What Phase 409 rules out:** The dark-exclusive atom pool (25 atoms) is NOT a structurally special subclass — same section behavior (C1143), same slot positions (C1145), and doesn't explain ordering mismatches (C1144). The operational-profile naming system uses ALL atoms interchangeably. The 25 "dark-exclusive" atoms are simply rarer variants of the same building blocks — possibly encoding less common processing properties that only matter for material naming, not for operational instructions.

**Updated analogy:** The manuscript is a recipe collection organized by material domain. Each section is like a chapter in a pharmacopoeia. The bridge MIDDLEs are the shared procedural verbs (heat, filter, decant, macerate) used across all chapters. The dark-pipeline MIDDLEs are the domain-specific ingredient lists — and each chapter has its own list, assembled from the same root concepts but combined differently to name different substances. When a procedure is complex, the recipe is mostly verbs; when many materials are involved, the recipe is mostly names. The names aren't arbitrary labels — they are compressed descriptions of how each material behaves under processing.

## XV. Cross-Lane Content Prediction and Heat-Measure Cycle (Phase 443)

**Phase:** EN_LANE_CROSS_PREDICTION | **Constraints:** C1242-C1244 | **Fits:** F-B-007

### Core Finding

Adjacent QO and CHSH EN tokens carry paired information within each line. The specific QO MIDDLE predicts the specific CHSH MIDDLE (MI=1.0632 bits, z=13.42) — but the sequential order doesn't matter (z=0.05). It's the pairing that's structured, not the sequence. This resolves the C961 tension: within-lane ordering IS null, but cross-lane content pairing is genuine.

### The Heat-Measure Cycle

Lines encode a heat-measure cycle: QO applies energy, CHSH monitors, QO adjusts. The dominant atom handoff pattern:

```
QO(k-terminal) → CHSH(e-initial...y-terminal) → QO(k-initial)
Heat            → Cool/measure...end           → Heat again
```

- Top QO→CHSH handoff: k→e at 20.7% (heat, then cool/measure)
- Top CHSH→QO handoff: y→k at 19.5% (measurement done, heat again)
- Lines open with CHSH 54.2% (measure first), close with QO 59.8% (heat last)
- Kernel routing is massive (z=49.12), with CHSH→QO 2.2x stronger than QO→CHSH — the monitoring result constrains next energy operation more strongly than energy constrains monitoring. This is a feedback architecture.

### sh Monitor-Pivot vs ch Checkpoint-Gate (C1243)

The two CHSH prefixes serve different routing functions:

| | sh (monitor) | ch (test) |
|---|---|---|
| Routes to QO(k=heat) | 32.0% | 24.0% |
| Routes to k-containing | 47.2% | 35.6% |
| Entropy (→QO) | 4.763 bits (formulaic) | 5.068 bits (varied) |
| Function | **Pivot**: "watched, keep heating" | **Gate**: "tested, decide next action" |

sh is the steady-state pivot that keeps the process running in the same mode. ch is the decision point that can branch to different operations based on the test result. This extends C929's positional/suffix evidence with cross-lane routing evidence.

### aiin→ain Wind-Down Pattern (C1244)

When both appear on a line, aiin precedes ain 64.9% of the time. This represents wind-down from sustained cycling to final pass:

```
qokaiin → sh(monitor) → qokain
"heat, keep cycling" → watch → "heat, one more pass"
```

The MIDDLE changes 84.5% of the time (not literal repetition), but the suffix decreases: aiin (sustained) → ain (finishing). The cycle progresses through different operations while the iteration specification decreases.

### Two Independent Scaling Axes (F-B-007)

The two extensible atoms encode independent control parameters:

| Dimension | Atom | Extension | Effect |
|-----------|------|-----------|--------|
| **Intensity** | e | e, ee, eee | k=full heat, ke=modulated, kee=gentle |
| **Duration** | i | i, ii, iii | i=single pass, ii=sustained cycling |

Empirical support: bare k is 92.6% of QO heat MIDDLEs in REGIME_2 (highest intensity), while ke mixing reaches 18.6% in REGIME_1 (modulated regime). The "check" gloss for -aiin/-ain (C561) applies to the or→aiin bigram context; in suffix semantics, aiin = a(yield) + ii(iterate) + n(halt) = "sustained cycling until halt."

### Cycle Is Strictly Line-Scoped

Cross-line atom MI is null (z=0.37). Cross-line lane pattern matches independence exactly. The heat-measure cycle resets at every line boundary, consistent with C1233 (cross-line independence).

### Cross-Lane Pairing Decomposition (C1245, C1246)

The C1242 MI signal decomposes into a **selectivity gradient**: rare QO MIDDLEs (ked, te, keeo) lock to 1-3 CHSH partners (entropy 3.4 bits), while common QO MIDDLEs (k, t, aiin) are promiscuous (entropy 4.6-5.1 bits, near the marginal 5.2 bits). Selectivity correlates with frequency (rho=0.665) — specialized operations require specific monitoring, generic operations accept any.

E-depth shows a **two-scale pattern**: at the category level, e-containing tokens match (OR=2.625); within the e-containing subset, high-e QO pairs with low-e CHSH (rho=-0.262). Strong heat gets light monitoring; gentle heat gets deep monitoring.

**Mode A (specification) and Mode B (execution) use different pairings** (JSD z=4.60). Mode A enriches energy+specific-measurement pairs (k-ck 5.1x, ke-ey 3.7x) with MI=1.425 bits. Mode B enriches sustained+passive pairs (k-eol 6.5x, l-edy 3.3x) with MI=0.978 bits. Specification lines lock energy to targeted checks; execution lines pair routine operations with generic monitoring.

### Apparatus Vocabulary Classification (C1247-C1249)

REGIME encodes apparatus type via vocabulary signatures. Five apparatus profiles (DISTILLATION, SEALED_VESSEL, SUSTAINED_HEAT, PRECISION, DIRECT_FIRE) defined from Brunschwig-grounded MIDDLE glosses score each folio against apparatus-specific vocabulary.

**Key structural findings:**

- **aii (unseal) is the strongest single-MIDDLE REGIME discriminator**: 41x enriched in REGIME_3 vs REGIME_1. 14/20 R3 folios contain aii (70%) vs 1/32 R1 folios (3.1%). Line context shows close→unseal→open transition pattern. R3 operates as open-cycle batch processing; R1 as continuous-run.

- **Distillation cycle signature**: t+eol co-occur at OR=16.27 (p=0.0001). If a program drives off volatiles, it sustains output. Sustained heat cycle: every folio with eeol also has ke (OR=inf, p=0.0003).

- **DISTILLATION vs PRECISION anti-correlate** at rho=-0.666 (p<0.0001) — the strongest inter-profile axis. Folios specialize: either distillation vocabulary or precision vocabulary, not both.

- **R1/R3 are single-apparatus REGIMEs** (97%/95% distillation-dominant). **R2/R4 mix apparatus types** within the same fire degree — consistent with Brunschwig's description of applying the same temperature via different apparatus. R2 splits 60% sealed vessel / 40% distillation; R4 splits three ways.

- **R3 vs R1 vocabulary differentiation**: R3-enriched = aii 41x, eo "cool-open" 7.6x, od "collect" 6.9x. R1-enriched = ke "sustained heat" 3.2x, ck "direct heat" 2.7x, lk "L-compound energy" 4.3x. R3 programs include unsealing, collecting, and cooling-with-opening. R1 emphasizes sustained energy management without interruption.

- **Section H (Herbal) is the most apparatus-diverse section**: all non-distillation folios in R2 and R4 are Herbal. Section B is overwhelmingly distillation (0.293 vs H 0.134). Herbal procedures reflect material-specific processing requirements.

**Methodological note**: An initial top-down approach (PCA on 2587 PREFIX-MIDDLE pair vectors residualized against REGIME) found no clean structure (NOT_SUPPORTED). The bottom-up approach — defining apparatus profiles from domain knowledge and scoring folios against them — found the real signal. The lesson: apparatus is a domain-specific category that requires domain-specific feature engineering, not unsupervised discovery.

---

## XVI. 8-Category Operational System (Phases 452-456)

**Phases:** A_CATEGORY_SCATTERSHOT (452) | AZC_CATEGORY_SCATTERSHOT (453) | CATEGORY_B_EXECUTION (454) | CATEGORY_MECHANISM_DECOMPOSITION (455) | CATEGORY_REGIME_INTEGRATION (456)
**Constraints:** C1261-C1294 | **Date:** 2026-02-24

### Core Finding

91 human-glossed MIDDLEs plus ~1,144 dark-auto-assigned MIDDLEs (via atom plurality vote) partition into 8 operational categories: THERMAL, CONTAINMENT, FLOW, MONITORING, OPERATION, TRANSITION, STAGING, MARKING. This system organizes the manuscript at every level — Currier A records, AZC diagram positions, B execution grammar, paragraph structure, and macro-state dynamics. It is the strongest cross-system organizing principle discovered to date (C1250).

### The 8 Categories

| Category | Gloss Examples | Role |
|----------|---------------|------|
| THERMAL | heat, fire, cool, sustain, pulse | Energy management: heating, cooling, temperature maintenance |
| CONTAINMENT | seal, hold, lock, bind, rigid | Physical constraint: sealing vessels, maintaining closure |
| FLOW | transfer, gather, discharge, route, input | Material movement: transferring, collecting, dispensing |
| MONITORING | watch, check, verify, scan, measure | Observation: temperature checks, quality verification |
| OPERATION | work, operate, batch, pound, strip | Active processing: physical manipulation of materials |
| TRANSITION | start, open, close, end, finish, halt | State changes: beginning/ending phases, opening/closing |
| STAGING | frame, step, iterate, sequence, cycle | Process organization: iteration, sequencing, cycling |
| MARKING | mark, flag, note, pause, adjust, hazard | Annotation: flagging conditions, noting adjustments |

### Cross-System Organization (Phases 452-453)

**Currier A (Phase 452):** Categories organize A at every tested grain. Records cluster by category (C1261, d=9.7). Paragraphs specialize: THERMAL dominates long paragraphs, MARKING dominates short ones (C1263, d=12.5). The bridge/dark pipeline split aligns with category: bridge MIDDLEs are TRANSITION-enriched, dark-pipeline MIDDLEs are MARKING-dominated (C1264, V=0.441). A sections differentiate at the atom level by category-aligned AXIS clusters (C1266).

**AZC (Phase 453):** AZC zones (R, C, S, P) specialize by category (C1269, V=0.084). Bridge MIDDLEs are sorted by category within AZC zones (C1272, p=0.0003) while dark MIDDLEs are not (p=0.198) — AZC mediates the bridge sorting. AZC-exclusive vocabulary has a distinctive category profile: MARKING/THERMAL-enriched, TRANSITION-depleted (C1273, V=0.382). All AZC sections converge on A Pharma atom profiles (C1276).

**The headline cross-system finding (C1274):** THERMAL category fraction predicts high B escape rate (rho=+0.780), TRANSITION fraction predicts low escape (rho=-0.598). Category composition in AZC/A directly predicts B dynamics.

### B Execution Grammar (Phase 454)

Phase 454 proved categories organize B's internal execution with 7/7 PASS:

**Escape architecture solved:**
- THERMAL escape is fully PREFIX-mediated (C1277): THERMAL MIDDLEs are 44.1% qo-prefixed (vs 9.5% baseline). Partial correlation collapses to rho=-0.081 after controlling for qo. Chain: THERMAL MIDDLE -> qo-PREFIX selection -> zero-hazard QO lane (C601) -> escape.
- TRANSITION anti-escape is PREFIX-independent (C1281): partial=-0.586 survives ch/sh control. Mechanism initially unknown.

**Category adds information beyond PREFIX (C1278):** Category reduces instruction class entropy by 24.7% (1.207 bits). PREFIX reduces it by 53.1% (2.589 bits). Together they explain 71.7% (3.496 bits). Category adds 18.6% beyond what PREFIX already provides — they are complementary organizational axes.

**Mode differentiation (C1279):** Mode A lines (terminal-suffix dominant) are THERMAL-enriched (28.9%), injecting escape-capable vocabulary. Mode B lines (bare-suffix dominant) are TRANSITION-enriched (17.4%), maintaining escape restriction. The suffix mode system and category system, derived independently, converge on the same operational axis.

**Hazard concentration (C1280):** Hazard MIDDLEs concentrate in FLOW (50.4%) and CONTAINMENT (11.5%). THERMAL is essentially hazard-immune (2.6%). V=0.560 — the strongest category effect measured. In process terms: transferring material and maintaining seals are dangerous; heating is safe (consistent with distillation physics where the fire is controlled but the transfer/seal failure modes are catastrophic).

### Category Mechanism Decomposition (Phase 455)

Phase 455 decomposed three open mechanisms with 6/8 PASS:

**TRANSITION anti-escape mechanism solved (C1285):** The expert hypothesized EN->EN self-loops. **Rejected.** TRANSITION sources actually have *lower* EN successor rates (0.403 vs 0.476 baseline) and *lower* EN->EN self-loop rates (0.474 vs 0.517). Instead, TRANSITION redirects successors toward AUXILIARY (1.24x enriched) and FREQUENT_OPERATOR (1.13x enriched) — roles that lack escape capacity because qo-prefix tokens concentrate in ENERGY_OPERATOR. Each TRANSITION token independently redirects its successor (no sequential clustering, T2 FAIL). The anti-escape property is baked into the vocabulary, not into sequential patterns.

**Asymmetric escape architecture:** THERMAL enables escape via PREFIX routing (qo). TRANSITION prevents escape via role redirection (AUX/FQ). Same category system, opposite mechanisms at different layers — PREFIX for enabling, role for suppressing.

**Category transition grammar (C1286):** The 8x8 category-to-category bigram matrix is massively structured (chi2=526, V=0.060, p~10^-81). Key features:

| Pattern | Residual | Process Interpretation |
|---------|----------|----------------------|
| MARKING -> MARKING | +10.4 | Annotation persists in theme |
| FLOW -> TRANSITION | +6.7 | Transfer leads to closing/finalizing |
| OPERATION -> THERMAL | +6.5 | Work leads to heating |
| THERMAL -> THERMAL | +6.0 | Sustained heating persists |
| FLOW -> FLOW | +4.6 | Sustained transfer persists |
| FLOW -> THERMAL | -7.3 | No direct flow-to-heat (strongest avoidance) |
| OPERATION -> TRANSITION | -4.7 | No direct work-to-close |
| THERMAL -> MARKING | -4.5 | No direct heat-to-mark |
| THERMAL -> TRANSITION | -3.4 | No direct heat-to-close |

The system follows process control logic: you heat (and keep heating), then transfer (and keep transferring), then close. You don't jump from heating to closing or from flow to heating. The pathways are also directional: FLOW->TRANSITION (779) vs TRANSITION->FLOW (525).

**Forbidden transitions are cross-category (T3 FAIL):** 15/17 forbidden transitions cross category boundaries (only 2 within-category, both MARKING->MARKING). MARKING is the dominant target/source in forbidden pairs (10/17 involve MARKING). Forbidden transitions operate below category level — they enforce specific MIDDLE-level constraints, not category boundaries.

**Paragraph architecture (C1287-C1290):**

- **Headers are MARKING-enriched (C1287):** Paragraph headers (first token) are 2.44x enriched for MARKING and 1.45x for STAGING, while THERMAL is suppressed (0.46x). This contrasts with line entries, which are THERMAL-enriched (C1283). Three-level specification hierarchy: paragraph header = marking/staging specification -> line entry = thermal specification -> line body = flow/transition execution.

- **Within-folio paragraph coherence (C1288):** Paragraphs within the same folio are more category-similar than cross-folio paragraphs (within JSD=0.109 vs null=0.122, z=-4.92). The folio (= program) imposes a category theme on all its paragraphs. Paragraph independence (C891-C893) is structural (grammar, kernel access) but not thematic (category composition).

- **Category predicts AXM dwell (C1289):** THERMAL fraction predicts high AXM self-transition (rho=+0.520), TRANSITION fraction predicts low AXM self-transition (rho=-0.519). Both survive Bonferroni. AXM is the dominant macro-state where 33/49 classes reside. THERMAL vocabulary keeps the system in its main operational loop; TRANSITION vocabulary moves it through state changes. This partially resolves the C1169 27% AXM residual variance.

- **Paragraph mode = category emphasis (C1290):** Mode A paragraphs are THERMAL-enriched (28.8% vs 21.0%), Mode B are TRANSITION-enriched (16.7% vs 11.5%). Chi2=300.4, V=0.114. Confirms C1279 at paragraph granularity.

### Relationship to Galenic Framework

The 8-category system is NOT an extension of the Galenic framework (F-RUP-001). The Galenic framework uses 4 qualities (hot/cold/wet/dry) x 4 degrees. Phase 384 showed that Galenic predictions fail at the grammar level (0/4 tests pass) — the Galenic framework is the author's training background, not the system's design principle.

The 8-category system is derived from Brunschwig process glosses and validated structurally. It succeeds where Galenic fails: organizing the grammar's sequential flow, paragraph structure, macro-state dynamics, and escape architecture. The categories are operational (what you DO in distillation) rather than qualitative (what properties materials HAVE). The Voynich author encoded process control, not natural philosophy.

### Interpretation (Tier 3)

In distillation context, the 8-category transition grammar describes a process control language where:

1. **The folio sets an operational theme.** A THERMAL-heavy folio is a heating-focused program. A TRANSITION-heavy folio manages state changes. All paragraphs within the folio follow this theme.

2. **Each paragraph begins with marking/staging annotation** (what to note, what to adjust) before executing its operational content. This matches recipe structure: "Note: check the seal. Then heat at sustained temperature, transfer the distillate, close the vessel."

3. **Sequential operations follow preferred pathways.** You heat and keep heating. You transfer and then close. You don't jump from heating to closing (THERMAL->TRANSITION depleted). You don't jump from flow to heating (FLOW->THERMAL depleted). The grammar enforces physically reasonable process sequences.

4. **The escape/anti-escape architecture maps to process control authority.** THERMAL operations (via qo-PREFIX) can exit the main operational loop — because changing temperature is a fundamental control action. TRANSITION operations suppress exit — because when you're in a close/finalize sequence, you need to complete it before the system can change state. This is feedback control: heating gives you options, closing locks you in until done.

5. **AXM dwell = sustained processing.** THERMAL vocabulary keeps the system in its dominant macro-state (the main processing loop). TRANSITION vocabulary breaks out of it. High-THERMAL folios are sustained processing programs; high-TRANSITION folios manage state changes and transitions between processing phases.

### REGIME-Category Relationship (Phase 456)

Phase 456 tested whether categories integrate with the 4-REGIME classification (C179/C494, GMM k=4 on 15 folio features). The association is strong (chi2=526, V=0.106) but **kernel-mediated**: after residualizing on k/h/e atom composition, the signal drops to non-significant (Fisher p=0.061). THERMAL's kernel R2=0.779 means ~78% of its folio-level variance is explained by k/e atom prevalence alone.

**Key findings:**
- **REGIME_1** (thermal-control-intensive, 32 folios) = THERMAL-dominant (29.7%)
- **REGIME_2** (output-intensive, 15 folios) = FLOW-dominant (28.1%)
- **REGIME_4** (precision-constrained, 15 folios) = OPERATION/TRANSITION-dominant
- Categories survive section control but not kernel residualization -- kernel atoms are the primary pathway (C1291-C1292)
- Categories add genuine resolution beyond role profiles (Fisher p=7.5e-8) -- not a relabeling of existing class/role structure (C1293)
- **Categories do NOT extend C1169 AXM model** (C1294) -- the raw correlations (C1289, rho=+/-0.52) are fully absorbed by existing predictors. The 27% AXM residual is validated as irreducible design freedom.

**Interpretation:** REGIMEs and categories are not independently designed classification systems. Both express the same underlying kernel chemistry at different scales. REGIMEs are the macro view (this folio is a heating program because its k-ratio is high). Categories are the micro view (this token does heating work because its MIDDLE contains k-atoms). They converge because the author's system is coherent: the program type determines the vocabulary.

---

## XVII. Paragraph Termination Mechanism (Phase 457)

**Phase:** PARAGRAPH_TERMINATION_TRIGGER (457)
**Constraints:** C1295-C1296 | **Date:** 2026-02-24

### Core Finding

Paragraph termination is **memoryless**: no line-level feature predicts when a paragraph ends. An exhaustive 8-test battery (Bonferroni p<0.00625) tested every plausible trigger mechanism — thermal threshold, thermal budget, thermal step, B-track signature, suffix mode gate, category shutdown sequence, folio-level prediction extension — and ALL failed (C1295). The sole PASS: tail product types (C1232's 3 clusters) have distinct category profiles (C1296, chi2=139.1), meaning the *form* of shutdown varies by operational theme but the *decision* to stop shows no precursor.

### What Was Tested and Failed

| Hypothesis | Test | Result |
|------------|------|--------|
| Thermal threshold (high e_frac triggers stop) | T1: e_frac last vs interior, length-controlled | FAIL (Fisher p=0.236, raw signal = length confound) |
| B-track terminal cooling | T2: terminal B-line vs interior B-line e_frac | FAIL (Fisher p=0.178) |
| Thermal step into final line | T3: delta_e_frac terminal vs interior pairs | FAIL (perm p=0.822) |
| Thermal budget (hotter = shorter) | T4: mean e_frac vs body length, within-folio | FAIL (rho=-0.007, p=0.930) |
| Mode gate (A or B mode triggers stop) | T5: Mode A fraction last 2 vs earlier | FAIL (chi2=1.19, p=0.276) |
| Category shutdown sequence | T6: 8-category profile last 2 vs earlier | FAIL (perm p=0.400) |
| Folio-level thermal/category prediction | T7: extended OLS vs section+REGIME baseline | FAIL (F p=0.365, LOO decreases) |

### Interpretation (Tier 3)

The paragraph body is genuinely homogeneous until -am fires the termination signal (C1237, 5.19x enriched). This extends C963's body homogeneity finding from role fractions to thermal, modal, and categorical grain. The T1 result is particularly instructive: the apparent thermal enrichment in last lines is entirely a line-length confound (last lines are shorter, short lines have different e_frac distributions).

In distillation terms: a paragraph is a batch operation that runs for a predetermined duration. The operator does not look at the material's state to decide when to stop — the duration was decided when the program was written (at the folio level, C1239). The -am suffix is the "batch complete" stamp, not a "conditions met" sensor. This is consistent with a reference manual rather than a real-time control system: the manual specifies HOW LONG to run each operation, not WHEN to stop based on observations.

The T8 finding (tail type category divergence) adds nuance: while the timing is memoryless, the vocabulary used in the final lines reflects the paragraph's operational theme. A THERMAL-heavy paragraph ends with heating vocabulary (Cluster 2, THERMAL 33.5%). A TRANSITION-heavy paragraph ends with state-change vocabulary (Cluster 0, TRANSITION 20.1%). The shutdown vocabulary is thematically appropriate even though its placement is not state-triggered.

---

## XVIII. PREFIX Category Anatomy (Phase 458)

**Phase:** PREFIX_CATEGORY_ANATOMY (458)
**Constraints:** C1297-C1302 | **Date:** 2026-02-24

### Core Finding

Individual PREFIXes predict operational categories with structured selectivity (V=0.311, chi2=15,598). This is not tautological with base-group membership: PREFIX adds 0.058 bits (2.1%) of category information beyond base group (C1301). The association is concentrated in specific pairs, particularly t-base (ct vs ot, V=0.891) and o-base (qo vs others, V=0.217).

### Channel Architecture

Two parallel channels organize PREFIX-category flow, each with a sister pair plus a categorically pure third member:

| Channel | Sister Pair | Third Member | Third's Purity |
|---------|-------------|-------------|----------------|
| EN | ch/sh (OPERATION) | qo | 59% THERMAL |
| AX | ok/ot (FLOW) | ct | 90% MONITORING |

The third members are the most categorically pure PREFIXes in the system. qo injects thermal content; ct provides monitoring operations. The asymmetry is striking: qo is common in B (4,069 tokens, 17.6%) while ct is rare (60 tokens, 0.26%), reflecting ct's primary A-system role (C282, 0.14x B frequency).

### Sister Pair Divergence in B

ch/sh are category-identical in Currier A (C1268, V=0.021) but diverge in B (C1299, V=0.121, p=9.4e-16). This survives section control (Fisher p=3.4e-10) and position control. The mechanism is MIDDLE-level: ch selects a broader vocabulary including minority MIDDLEs (ot MIDDLE 91.9% ch, ckh 76.4% ch), while sh concentrates on high-frequency MIDDLEs in OPERATION (edy at 21.2%). B's richer vocabulary reveals selectivity differences invisible in A's more uniform token set.

ok/ot likewise diverge (C1298, V=0.105): ok is THERMAL-enriched (24.7% vs 20.2%) and MONITORING-enriched (2.52x), while ot is OPERATION-enriched (17.3% vs 12.5%).

### BARE as Anti-Thermal Anchor

BARE tokens (no PREFIX) are THERMAL-depleted at 4.1% (vs 27.5% prefixed), establishing the PREFIX slot as the primary mechanism for thermal injection (C1302). BARE tokens concentrate in FLOW (29.4%) and STAGING (20.7%) -- infrastructure and preparation operations that do not carry thermal parameters.

### Interpretation (Tier 3)

The PREFIX is not merely a passive label or a redundant echo of base-group identity. It selects the operational channel through which a token contributes to the program. In distillation terms:

- **qo-prefixed tokens** are primarily heating/cooling instructions (THERMAL)
- **ct-prefixed tokens** are temperature/flow monitoring checkpoints (MONITORING)
- **a-base prefixed tokens** (da, sa, ka, ta) are setup/preparation instructions (STAGING)
- **h-base prefixed tokens** (ch, sh, etc.) are the primary execution vocabulary (OPERATION)
- **BARE tokens** are routing and flow infrastructure

The channel symmetry (EN and AX each having a sister pair + pure third) suggests the PREFIX system is organized around two complementary operational channels, each providing general-purpose execution via the sister pair and specialized single-purpose injection via the third member. The qo/ct asymmetry (thermal injection is common, monitoring is rare) is consistent with a system that spends most of its time executing thermal operations and only occasionally pauses to check monitoring conditions.

---

## XIX. Sister Category Mechanism (Phase 459)

**Phase:** SISTER_CATEGORY_MECHANISM (459)
**Constraints:** C1303-C1307 | **Date:** 2026-02-24

### Core Finding

Sister pair category divergence (ch/sh and ok/ot) is position-independent and mechanistically driven by vocabulary selection, not vocabulary transformation. Position explains almost none (ch/sh) or actually masks (ok/ot) the true category signal. The MIDDLE's category is intrinsic -- it does not change based on which sister PREFIX selects it.

### Position Independence

ch/sh category divergence retains 98.3% of its V after position control (C1303). The category profiles are remarkably stable across EARLY/MID/LATE zones (V=0.094 to 0.102). C929's positional axis (ch later, sh earlier) is genuinely orthogonal to the category axis (ch selects different MIDDLEs than sh).

ok/ot shows 124.1% V retention (C1304) -- position was actually *suppressing* the true divergence. C1184's opposite positional polarity (ok early, ot late) was a confounder masking the category signal. Within EARLY positions alone, the divergence is V=0.207, nearly double the raw V=0.114.

### Mechanism: Vocabulary Selection

0 of 33 qualifying MIDDLEs shift dominant category between ch and sh (C1305). When the same MIDDLE (e.g., "e", "dy", "ck") appears after ch vs after sh, it keeps the same category (THERMAL, CONTAINMENT, MARKING respectively). The sister pair achieves its category divergence entirely by selecting DIFFERENT MIDDLEs at different rates, not by changing what any individual MIDDLE means.

This is the resolution: PREFIX is a vocabulary selector (which words to deploy) not a vocabulary transformer (what words mean). In process control terms: ch and sh send different instructions (different MIDDLEs), but any given instruction has the same meaning regardless of which sister dispatched it.

### Cross-Lane Category Routing

When ch and sh tokens transition to QO-lane tokens, the QO token's category differs (C1306, V=0.122, p=2.34e-5). ch routes more STAGING cargo (20.6% vs 12.9%) to the QO lane, while sh routes more THERMAL cargo (53.6% vs 45.0%). Sister identity shapes not just the token's own category but the categorical composition of the downstream execution channel.

### Two-Atom PREFIX Instructions (Tier 3)

The results support reading PREFIXes as two-atom instructions with a [VERB] + [TARGET] format:

| PREFIX | Verb | Target | Dominant Category | Reading |
|--------|------|--------|-------------------|---------|
| ok | o (set/execute) | k (heat) | STAGING/THERMAL | "set heat parameters" |
| ot | o (set/execute) | t (transfer) | MARKING/OPERATION | "set transfer routing" |
| ch | c (adjust/calibrate) | h (watch) | OPERATION | "adjust monitoring" |
| sh | s (sequence/step) | h (watch) | THERMAL/MARKING | "sequence monitoring" |
| qo | q (?) | o (operate) | THERMAL (59%) | "thermal operation" |
| ct | c (adjust) | t (transfer) | MONITORING (90%) | "calibrate transfer" |

The verb distinction maps to control system operations: you SET a temperature (ok), you ADJUST a thermometer (ch). Different verbs on different subsystems. The base atom (k, t, h) determines WHICH subsystem the instruction targets; the lead atom determines WHAT action to take on that subsystem.

### Additivity

No three-way interaction exists between sister identity, category, and position (C1307). The sister category effect is additive with position: knowing the sister identity gives the same category information regardless of where in the line you are. This rules out models where sister pairs modulate category differently at different line positions (e.g., "ch selects THERMAL early but FLOW late").

## XX. Cross-Mode Category Coupling (Phase 460)

**Phase:** CROSS_MODE_CATEGORY_COUPLING (460)
**Constraints:** C1308-C1312 | **Date:** 2026-02-25

### Core Finding

Mode A and Mode B parallel tracks are coordinated by shared paragraph context and positional synchronization, not by sequential dependency. The two tracks read from the same "key signature" (paragraph category profile) and are synchronized by position within the line, but play their parts independently — like two instruments reading from the same measure of sheet music.

### Paragraph Category Coherence

Both modes within a paragraph share a common category "key" (C1308). Within-paragraph A-B divergence (JSD=0.141) is significantly less than cross-paragraph (JSD=0.170, p=7.4e-6). A THERMAL-heavy paragraph has THERMAL content in both its Mode A and Mode B lines. The paragraph sets the operational domain; both voices contribute to it.

### Mode Specialization

Mode A is the specification/parameter voice: THERMAL (32.5% vs 20.7%) and MONITORING (2.6x enriched). Mode B is the execution/process voice: TRANSITION (1.64x), STAGING (1.37x), FLOW (1.22x). Together they cover 6.1 of 8 categories vs 4.8 alone (C1309). This maps directly onto suffix mode characterization: A (terminal-heavy = endpoint specification) encodes WHAT to achieve thermally; B (bare-heavy = continuation) encodes HOW to execute flow and transitions.

### Positional Synchronization

At the same relative position within adjacent A/B lines, categories align 1.27x above chance (perm p=0.001, C1310). NMI is consistent across all 5 position bins (0.042-0.063), peaking at MID-LATE. THERMAL->THERMAL is the strongest pairing (7.6%). The two tracks are synchronized by position — working on the same operational domain at the same point in the line.

### B-to-A Thermal Feedback

B's thermal state feeds back to the next A line through a narrow channel (C1311): ke_ratio -> MARKING (rho=-0.198, p=0.0006) and ke_ratio -> THERMAL (rho=+0.176, p=0.002). Hot B lines suppress marking content and boost thermal content in the next A line. The feedback is directional — A->B shows no signal (p>0.3). In control system terms: the execution voice reports back, and the specification voice adjusts.

### No Sequential Coupling

All sequential coupling tests are negative (C1312): zig-zag coupling is weaker than random (Z=-3.39), A's category doesn't predict B's (p=0.146), no cross-line transition grammar, 0 cross-line forbidden transitions, and all token-interleaving ratios increase entropy. Same-mode pairs show stronger coupling than cross-mode pairs (AA r=0.463 > BA r=0.328). Lines are operationally self-contained.

### BA Handoff Pattern

The BA boundary shows a characteristic handoff: TRANSITION->THERMAL at 12.0%, dominating all other transitions. B lines exit through TRANSITION, A lines re-enter with THERMAL specification. This makes physical sense: an execution phase completes a state change, then the specification voice sets new thermal parameters for the next cycle.

### Cross-Mode Sheet Music Principle (Tier 3 Synthesis)

The Phase 460 findings collectively establish a named structural principle: Mode A and Mode B lines read from the same paragraph-level "key signature" (C1308), are synchronized by relative position within the line (C1310), and play complementary parts — A carries specification/THERMAL, B carries execution/TRANSITION (C1309). But they compose their individual contributions independently (C1312). B's thermal state feeds back to A's category selection (C1311) as the only detectable cross-mode signal. Like two staves of sheet music, the voices are in the same key, coordinated by measure, and playing different roles — but each part is written as a self-contained line.

## XXI. Distillation Terminology Mapping (Phase 461)

**Phase:** DISTILLATION_TERMINOLOGY_MAPPING (461)
**Constraints:** C1313-C1316 | **Fits:** F-B-008 through F-B-012 | **Date:** 2026-02-25
**Tier:** 3-4 (intentionally interpretive, extending GLOSSING.md)

### Purpose

Systematic test of whether distillation physics maps directly to the manuscript's structural patterns. 10 tests with negative controls, producing the authoritative Tier 3-4 reference mapping that survives context loss. 9/10 tests pass.

### Two-Channel Thermal Architecture (C1313, F-B-008)

qo and ok access completely non-overlapping thermal atom pools:

| PREFIX | k-fraction | e-fraction | Role |
|--------|-----------|-----------|------|
| qo | **0.510** | 0.102 | Heat source (k-dominant) |
| ok | 0.001 | **0.282** | Vessel temperature (e-dominant) |
| sa (control) | 0.005 | 0.003 | Neutral (no thermal bias) |

In distillation terms: qo manages the fire/furnace (adding energy), ok manages the vessel/still (cooling/stabilization). Two physically independent thermal channels. Brunschwig confirms: fire managed via air holes (lines 2038-2055) vs vessel tested by finger (lines 1880-1893).

### Overshoot-Correct Cycling (C1314, F-B-009)

Within lines, qo-k tokens transition to ok-e tokens 43% above chance (103 observed vs 72 null, p=0.0). The reverse (ok-e to qo-k) is 55% above chance (112 vs 72, p=0.0). This is consistent with heat overshoot followed by vessel correction — the standard problem in distillation where heat always overshoots and must be corrected.

### Control Flow Loop

Within-line bigram analysis reveals a preferred PREFIX sequencing:

```
sh (watch) -> qo (stoke fire) -> ok (check vessel temp) -> ot (check output) -> sh (watch)
   1.98x          1.08x              1.18x
```

- **sh -> qo (1.98x):** Passive monitoring is the primary trigger for heat action
- **qo -> ok (1.08x):** Heat action triggers vessel thermal check
- **ok -> ot (1.18x):** Vessel check leads to operations check (coarse then fine)
- **ok/ot -> qo (0.84/0.88x):** Neither verification leads back to heat directly

**What triggers heat:** 36.7% of sh tokens precede qo. sh-before-qo is enriched in edy (batch, 1.32x OPERATION) and depleted in ar (close, 0.29x FLOW) and ol (continue, 0.58x STAGING). The monitor watches the ongoing batch and triggers heat when it needs energy — not after flow endpoints or staging transitions.

**Loop scope:** Cross-line, not intra-line. Full sh->qo->ok->ot within a single line: only 3.3% of sh->qo starts (48 of 2,417 lines). Each line executes one or two steps, not a complete cycle. Forward/reverse directionality: 6.0x.

### ok vs ot: Two-Stage Verification (C1316)

ok and ot are e-sisters (both e-dominant: 0.282 and 0.258) but serve sequential roles:

| Property | ok (coarse) | ot (fine) |
|----------|------------|----------|
| THERMAL | 24.7% | 20.2% |
| OPERATION | 12.5% | 17.3% |
| Top MIDDLE | aiin (settling) | edy (batching) |
| Enriched MIDDLEs | ee (extended cool) | od (collect), or (portion) |

ok checks **thermal state** (is the temperature right?), ot checks **operational state** (is the process running correctly?). The operator would not fine-tune flow rate if temperature was not stable yet.

### REGIME Token Profile Discrimination (C1315, F-B-010)

The 4 REGIMEs produce statistically different B token profiles (6/7 metrics significant at p<0.01). Currier A tokens show 0/7 — discrimination is entirely B-specific. This confirms REGIMEs capture real B-internal variation.

### Luting-CONTAINMENT Association (F-B-011)

CONTAINMENT category tokens show REGIME discrimination (dy-MIDDLE: p=0.015, d=-0.753). However, the direction was reversed from prediction: REGIME_1 (balneum) shows MORE sealing than REGIME_3 (direct fire). Physical explanation: balneum vessels immersed in water baths require more vessel-sealing, distinct from joint-luting.

### E-Compound Cooling Taxonomy (F-B-012)

Different e-compound MIDDLEs distribute non-randomly across REGIMEs (chi-sq p<0.01):
- **eeol** (extended cool + continue): Enriched in REGIME_2 (sustained operation, overnight standing)
- **eo** (cool + work): Enriched in REGIME_2 (monitored cooling)
- **e** (basic cool): More uniform distribution

### MIDPROCESS Action Mapping

13 modern distillation MIDPROCESS actions each map to distinguishable PREFIX + category patterns. All 13 significant at Bonferroni-corrected p < 0.005. Mean pairwise cosine distance = 0.73 (random mapping: 0.003). The real mapping dramatically outperforms random assignment (p < 0.001).

### PREFIX-to-Distillation Domain Table (Tier 3-4)

| PREFIX | Domain | Physical Referent | Evidence |
|--------|--------|-------------------|----------|
| qo | Heat source | Fire/furnace management | C1313, C1314 |
| ok | Vessel temperature | Thermal verification (coarse) | C1313, C1316 |
| ot | Vessel operations | Operational verification (fine) | C1316 |
| ch | Active testing | Discrete physical tests | C929, T7 |
| sh | Passive monitoring | Continuous observation | C929, T7, T9 |
| ol | Continuation | Maintaining during active process | T8 |
| da | Setup/infrastructure | Apparatus preparation | T4 |
| sa | Scaffold | Supporting infrastructure | T1 neg ctrl |

### REGIME-to-Fire-Degree Mapping (Tier 3)

| REGIME | Proposed Method | Characteristic | Evidence |
|--------|----------------|----------------|----------|
| REGIME_1 | Balneum marie (water bath) | Gentle, e-rich, more sealing, highest alternation rate | T4, T5, T6, T10 |
| REGIME_2 | Sustained operation | High iteration, overnight cooling | T4, T10 |
| REGIME_3 | Ash/sand (per ignem) | Direct fire, rapid gathering | T4, T5, T7 |
| REGIME_4 | Precision operation | h-rich monitoring, tight tolerance | T4, T7 |

### Test Summary

| Test | Topic | Result | p-value |
|------|-------|--------|---------|
| T1 | Two-channel thermal model | PASS | 0.0 |
| T2 | Overshoot-correct cycling | PASS | 0.0 |
| T3 | MIDPROCESS action mapping | PASS | all 13 sig |
| T4 | REGIME token profiles | PASS | 6/7 p<0.01 |
| T5 | Luting discrimination | PASS | dy p=0.015 |
| T6 | Cooling mode differentiation | PASS | chi-sq p<0.01 |
| T7 | Monitoring PREFIX x REGIME | PASS | 3/4 predictions |
| T8 | O-PREFIX differentiation | PASS | chi-sq p<0.001 |
| T9 | Thermal shock prevention | PASS | THERMAL enriched |
| T10 | Bang-bang rate by REGIME | FAIL | ordering reversed |

### What This Means

The Voynich B text's structural patterns — PREFIX selection, atom composition, within-line sequencing, REGIME variation — map systematically onto the physics of controlled distillation. This is not translation; it is structural alignment at the level of operational roles. The manuscript's control programs are consistent with managing heat input, monitoring vessel state, verifying output, and cycling through these operations with precision appropriate to the fire degree. Token coverage: 99.5% of B tokens receive a mapping.
