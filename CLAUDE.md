# Voynich Manuscript Analysis - Reference Summary

> **Document Version:** 1.8 (Post-SITD Exploratory Phase, 2026-01-08)
> **See also:** `REVISION_LOG.md` for change history, `MODEL_SCOPE.md` for scope boundaries

> **Full documentation archive:** See `archive/CLAUDE_full_2026-01-06.md` for verbose version with extended guardrails and methodology explanations.

## Epistemic Tiers

| Tier | Label | Meaning |
|------|-------|---------|
| 0 | FROZEN FACT | Proven by internal structural analysis |
| 1 | FALSIFICATION | Hypothesis tested and rejected |
| 2 | STRUCTURAL INFERENCE | High-confidence bounded conclusion |
| 3 | SPECULATIVE ALIGNMENT | Non-binding interpretive layer |
| 4 | EXPLORATORY | Idea-generation only |

---

## Frozen Conclusion (Tier 0)

**Scope:** Currier B only (61.9% of tokens, 83 folios)

> The Voynich Manuscript's Currier B text encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

| Metric | Value |
|--------|-------|
| Instruction classes | 49 (9.8x compression) |
| Grammar coverage | 100% |
| Folios enumerated | 83 (75,248 instructions) |
| Translation-eligible zones | 0 |

**Purpose class:** Continuous closed-loop process control (all others eliminated)

**Viable process classes:** Circulatory reflux distillation, volatile aromatic extraction, circulatory thermal conditioning

**Product-class status:** Both extraction-type and conditioning-type survive; no internal analysis can distinguish

---

## Model Boundary (LOCKED) — Tier 0

### What the Manuscript DOES Encode (Currier B)

| Layer | Content | Evidence |
|-------|---------|----------|
| Executable Grammar | 49 instruction classes, 100% coverage | Phase 20: 9.8x compression |
| Kernel Control | 3 fixed operators (k, h, e) with mandatory STATE-C | Phase 15: 0/100 surrogates reproduced |
| Hazard Topology | 17 forbidden transitions in 5 failure classes | Phase 18 |
| Convergence | Dominant convergence to STATE-C (57.8% terminal; see SEL-F) | Phase 13-14, SEL-F revision |
| LINK Operator | Deliberate non-intervention (38% of text) | Phase 16: external termination |
| Folio = Program | Each folio is complete, self-contained | Phase 22: 83 folios enumerated |
| Line = Micro-stage | Lines are formal control blocks (3.3x more regular than random) | Phase LINE: boundary markers, grammar-invariant |

### What the Manuscript DOES NOT Encode (Proven)

| Claim | Status | Evidence |
|-------|--------|----------|
| Language | FALSIFIED | Phase X.5: 0.19% reference rate |
| Cipher | FALSIFIED | Phase G: cipher transforms DECREASE MI |
| Glyph Semantics | FALSIFIED | Phase 19: 0 identifier tokens |
| Illustration-Dependent Logic | FALSIFIED | Phase ILL: swap invariance p=1.0 |
| Step-by-Step Recipe | FALSIFIED | Phase FSS: families are emergent |

### Purpose Class Elimination

**Eliminated by structural incompatibility:**
- Cipher/hoax, Encoded language, Recipe/pharmacology, Herbarium/taxonomy
- Medical procedure, Astronomical calculation, Ritual/symbolic practice
- Educational text, Discrete batch operations, Fermentation
- Glassmaking/metallurgy, Dyeing/mordanting

**What the operator provides (not encoded):**
- Sensory completion judgment (when to stop)
- Material selection (what to process)
- Hazard recognition (physical signs of failure)

**What the text provides:**
- WHERE in the sequence (navigation)
- WHAT to do at each step (instruction)
- What NOT to do (forbidden transitions)

---

## Currier A: Non-Sequential Categorical Registry (Tier 2)

Currier A (31.8%, 114 folios) is **DISJOINT** from B in grammar but **UNIFIED** in type system.

| Property | Evidence |
|----------|----------|
| LINE_ATOMIC | Median 3 tokens/line, MI=0 across lines |
| POSITION_FREE | Zero JS divergence between positions |
| CATEGORICAL TAGGING | 8+ mutually exclusive marker prefixes (ch, qo, sh, da, ok, ot, ct, ol) |
| FLAT (not hierarchical) | Zero vocabulary overlap between markers |
| DATABASE_LIKE | TTR=0.137, 70.7% bigram reuse |
| DESIGNED SEPARATION | 25/112,733 cross-transitions (0.0%) |
| **SHARED TYPE SYSTEM** | Same kernel dichotomy (ch/sh/ok=100%, da/sa<5%), same LINK affinities |

**Architecture:** A uses the same morphological type system as B (Constraint 383) but instantiates it in a non-sequential registry rather than sequential programs. This is like a parts catalog (A) vs assembly instructions (B) — same part types, different formal systems.

### Structural Primitives

| Token | B Role | A Role | Affinity |
|-------|--------|--------|----------|
| `daiin` | CORE_CONTROL (execution boundary) | Record articulation | A-enriched (1.55x) |
| `ol` | CORE_CONTROL (pairs with daiin) | Marginal presence | B-enriched (0.21x) |

`daiin` = "portable articulator" (adapts to ANY context)
`ol` = "execution anchor" (functional only in sequential grammar)

### Multiplicity Encoding (Phases CAS-MULT, CAS-DEEP)

64.1% of entries exhibit **repeating block structure**: `[BLOCK] × N`

| Metric | Value |
|--------|-------|
| Entries with repetition | 64.1% (1013/1580) |
| Average repetition | 2.79x |
| Distribution | 2x: 416, 3x: 424, 4x: 148, 5x: 20, 6x: 5 |
| Block uniqueness | 100% (no cross-entry reuse) |
| Section isolation | **100%** (no cross-section reuse) |
| Marker exclusivity | 72.6% of tokens marker-specific |
| Section vocabulary overlap | 9.7% (Jaccard) |

**Key distinction:** This is **literal enumeration**, NOT abstract quantity.
- NOT: `ITEM = 5` (abstract quantity with arithmetic)
- BUT: `ITEM, ITEM, ITEM, ITEM, ITEM` (discrete instances without comparison)

**CAS-DEEP findings:**
- Markers at block END 60.3% (vs 44% start) - marker is trailing classification tag
- 3x dominance (55%) reflects human counting bias, bounded for usability
- INVERSE complexity: higher counts have MORE diverse blocks (rho=0.248)
- No cross-entry arithmetic, no reference frame for comparison

**Refined characterization:** `SECTION_ISOLATED_MARKER_STRATIFIED_ENUMERATION_REGISTRY`

### Compositional Morphology (Phase CAS-MORPH)

Marker tokens are **compositional, not atomic**:

```
marker_token = [ARTICULATOR] + PREFIX + [MIDDLE] + SUFFIX
```

| Component | Count | Role | Required? |
|-----------|-------|------|-----------|
| ARTICULATOR | ~9 forms | Optional refinement (yk-, yt-, kch-, etc.) | No |
| PREFIX | 8 | Primary classifier family | Yes |
| MIDDLE | 42 common | Modifier subcode | No |
| SUFFIX | 7 universal | Terminal variant code | Yes |

**Key finding:** 897 observed PREFIX × MIDDLE × SUFFIX combinations. The identity space scales combinatorially from a small formal codebook.

### Optional Articulator Layer (Phase EXT-9B)

~20% of Currier A tokens have **extended articulator forms** (yk-, yt-, kch-, ks-, ko-, yd-, ysh-, ych-).

| Test | Result |
|------|--------|
| Section exclusivity | **PASS** — MORE concentrated than core prefixes (kch: 95% in H) |
| Mutual exclusivity | **FAIL** — Co-occur with core prefixes (24.6%) |
| Identity necessity | **FAIL** — 100% removable without identity loss |
| Distribution entropy | Lower than core — more systematic than noise |

**Conclusion:** These are an **optional articulator layer** — systematic enough to have patterns, optional enough to not affect core identity. They refine expression without altering classification.

This explains:
- Low TTR (0.137) — component reuse
- High bigram reuse (70.7%) — predictable combination
- Learnability — small codebook, compositional rules

**Critical constraint:** These are FORMAL roles, not semantic meanings. What the components "mean" in the real world is external to the artifact and not recoverable.

**Final characterization:**

> Currier A is a compositional, non-semantic classification registry built from orthogonal code components, allowing hundreds of fine-grained distinctions while remaining formally stable, enumerable, and isolated from execution.

### Sister Pair Architecture (Phase SISTER)

Prefix families partition into structural categories:

| Category | Prefixes | Characteristics |
|----------|----------|-----------------|
| Sister Pair A | ch, sh | Equivalence class (J=0.23), mutually exclusive, section-conditioned |
| Sister Pair B | ok, ot | Equivalence class (J=0.24), mutually exclusive, section-conditioned |
| Infrastructure | da | Record articulation, not material classification |
| Isolate | ct | Section H specialist (85.9%), minimal cross-family similarity |
| Bridging | qo, ol | Moderate cross-family similarity, connect to both pairs |

**Sister pair behavior in Currier B:**
- AVOID direct sequence (0.6x suppression)
- SHARE predecessor contexts (336 shared)
- ACCEPT same suffixes (195 minimal pairs)
- SUBSTITUTE in trigram frames (119 contexts)

**Section conditioning:**
- Section H prefers ch-forms (78-92%)
- Section B is balanced (42-57% ch)
- Conditioning at section/quire level, not folio level

**Key insight:** Sister pairs occupy the same grammatical slot but are alternative choices, not companions. The choice is constrained by organizational context (section/quire), not individual program.

---

## Currier AZC: Astronomical/Zodiac/Cosmological Hybrid (Tier 2)

**7.7% of tokens (9,401) in 30 folios** were never classified by Currier as A or B.

| Metric | AZC | Currier A | Currier B |
|--------|-----|-----------|-----------|
| Token percentage | 7.7% | 30.5% | 61.9% |
| Folios | 30 | 114 | 83 |
| TTR | 0.285 | 0.137 | 0.096 |
| Tokens/line (median) | 8 | 22 | 31 |
| LINK density | 7.6% | 3.0% | 6.6% |

**Classification: HYBRID**
- B vocabulary coverage: 69.7% (just below 70% threshold)
- A vocabulary coverage: 65.4%
- Shared vocabulary (A∩B): 60.5%
- Unique vocabulary: 25.4% (1,529 types)

**Key findings:**
- AZC is a genuine **third mode** that bridges A and B
- Uses **shared core vocabulary** (60.5% from A∩B intersection)
- **Shortest lines** in manuscript (median 8 tokens)
- **Highest LINK density** (7.6%) — most wait-heavy text
- **Highest vocabulary diversity** (TTR 0.285)

**AZC-unique vocabulary (25.4%, 1,529 types):**
- 98% section-exclusive (Z, A, C have separate vocabularies)
- 37% line-initial, 37% line-final (boundary concentration)
- 65.9% hapax (most appear only once)
- Structural signature: LABELING (not executing, not indexing)

**Placement-coding axis (Constraint 306):**
- Finite placement classes: C (17.1%), P (11.0%), R1-R3, S-S2, Y
- Participates in repetition-based multiplicity
- Integrates into surrounding hybrid grammar

**Axis Connectivity (Constraints 307-312):**
- Placement x Morphology: WEAK dependency (V=0.18)
- R1/R2/R3 subscripts: ORDERED (monotonic middle length decrease)
- Placement transitions: GRAMMAR-LIKE (99 forbidden, self-transitions 5-26x enriched)
- Placement x Repetition: CONSTRAINED (P/S high, R low)
- Placement x Boundary: POSITIONAL GRAMMAR (S1/S2/X=edge 85-90%, R1/R2=interior 3-9%)
- Section x Placement: STRONG (V=0.631)

**Verdict:** MULTI-AXIS INTERDEPENDENT SYSTEM — all axes connected.

**Sections:** C (Cosmological), Z (Zodiac), A (Astronomical)

**Positional Legality (Constraints 313-320):**
- Position constrains LEGALITY not PREDICTION (z=13 forbidden pairs, but only 14% prediction gain)
- Global illegality + local exceptions (default-deny with explicit permits)
- 9/18 restricted operators are PLACEMENT-LOCKED (only appear in one placement)
- PHASE-LOCKED binding (32.3pp drop under rotation)
- HYBRID architecture: C is topological (9.8% drop), P/R/S are positional (40-78% drop)
- Folio-specific profiles (V=0.507): different diagrams have different layouts
- Zodiac template reuse: f71-f73 share identical placement profile
- S2 < S1 ordering (p < 0.0001): S-series marks ordered positions

**Diagram Alignment Status:** CONFIRMED — placement codes are diagram-anchored, not abstract.

**Cycle Discriminator (Tests 4-5):**
- Calendar vs Workflow: HYBRID (Cramer's V difference = 0.013)
- Placement x A-Material: V = 0.152
- Placement x B-Procedure: V = 0.139
- Zodiac vocabulary isolation: Jaccard = 0.076 (structural templates)
- Seasonal clustering: 5/25 placements have full coverage

**Verdict: SEASON-GATED WORKFLOW** — AZC encodes workflow states whose availability is seasonally constrained. Both material timing AND procedural state matter.

**Tier Boundary:** Any attempt to map placements to physical geometry, celestial objects, or apparatus components exceeds internal structural evidence and belongs to Tier 3+.

---

## Consolidated Falsifications (Tier 1)

| Claim | Evidence |
|-------|----------|
| Text encodes language | Phase X.5: 0.19% reference rate |
| Tokens have translatable meanings | Phase 19: 0 identifier tokens |
| Illustrations are instructional | Phase ILL: swap invariance p=1.0 |
| Plants indicate ingredients | Phase PCIP: dual-use history |
| Sections = apparatus configs | Phase PCS: F-ratio 0.37 |
| Programs correlate with plant morphology | Phase PPC: all p>>0.05 |
| 49-class grammar generalizes to full manuscript | Phase CAud: 13.6% Currier A coverage |
| Hazard topology is universal | Phase CAud: 5 violations in Currier A |
| OPS-R 2-cycle reconciliation | SEL-F: RESOLVED (definitional ambiguity; 2-cycle=periodicity, MONOSTATE=convergence) |
| "100% convergence to STATE-C" | SEL-F: only 57.8% terminate in STATE-C |
| Procedural chaining (folios form macro-sequences) | SEL-F: Tests 1-6 falsified; no sequential state matching |
| STATE-C marks material-family boundaries | SEL-F: TEST 11 p=1.0; no association |
| Sharp material-family clustering | SEL-F: TEST 9 silhouette=0.018; highly overlapping |
| Hazard "100% bidirectional" | SEL-D: 65% asymmetric |
| Hazard "KERNEL_ADJACENT clustering" | SEL-D: 59% distant from kernel |
| Human-track "7 coordinate functions" | SEL-E: overfitting |
| HT 99.6% LINK-proximal | HTD: ρ=0.010, p=0.93 (decoupled) |
| Repetition encodes ratios/proportions | EXT-9B: no cross-entry comparison, no reference frame, violates no-arithmetic constraint |

---

## SEL Audit Results

### Survives
- OPS-1 through OPS-7: TIER 0 STABLE
- 49-class grammar: TIER 0 STABLE
- 17 forbidden transitions (COUNT): TIER 0 STABLE
- Non-grammar seam avoidance (0/35): TIER 2 STRUCTURAL
- Non-grammar hazard avoidance (4.84 vs 2.5): TIER 2 STRUCTURAL

### Failed/Downgraded
- OPS-R: RESOLVED by SEL-F (definitional, not formal contradiction; convergence claim revised)
- Human-track layer: Tier 2 → Tier 3
- CONTAINMENT_TIMING class: Theoretical-only (0 corpus impact)

---

## Key Structural Findings

### Currier B Grammar
- 49 instruction classes, 100% coverage
- 3 kernel operators: k (ENERGY_MODULATOR), h (PHASE_MANAGER), e (STABILITY_ANCHOR)
- 17 forbidden transitions in 5 failure classes
- Dominant convergence to STATE-C (57.8% terminal; 42.2% end in transitional states — see SEL-F)
- 38% LINK density (deliberate waiting)

### 5 Hazard Classes
| Class | Count | % | Notes |
|-------|-------|---|-------|
| PHASE_ORDERING | 7 | 41% | Primary |
| COMPOSITION_JUMP | 4 | 24% | Primary |
| CONTAINMENT_TIMING | 4 | 24% | *Theoretical-only (0 corpus impact; see SEL-D)* |
| RATE_MISMATCH | 1 | 6% | Primary |
| ENERGY_OVERSHOOT | 1 | 6% | Primary |

**Hybrid Hazard Model (EXT-ECO-02):**
- 71% **batch-focused hazards** (opportunity-loss): Mistimed action loses value
- 29% **apparatus-focused hazards** (equipment protection): CONTAINMENT_TIMING + ENERGY_OVERSHOOT

Key distinction: Apparatus hazard tokens have ZERO LINK nearby (vs 1.229 for batch) — faster response needed, no waiting allowed. Apparatus hazards have higher severity (0.8 vs 0.733) and rarer occurrence (5% vs 11.3%).

### Author Intent (via Failures) — Tier 3

> "The book encodes my fears, so that you do not have to learn them through loss."

**What the author feared most:**
1. **Phase disorder** (41%) — material changing state in wrong location (vapor where liquid should be)
2. **Contamination** (24%) — impure fractions passing before separation complete
3. **Apparatus failure** (24%) — overflow, pressure events, physical damage
4. **Flow chaos** (6%) — rate imbalance destroying circulation rhythm
5. **Thermal damage** (6%) — scorching from excessive heat

**Why failures are irreversible:**
| Failure Type | Why No Recovery |
|--------------|-----------------|
| Phase disorder | Condensate in wrong location cannot drain without disassembly |
| Contamination | Mixed impurities cannot be separated once combined |
| Spillage | Escaped material cannot be recovered |
| Scorching | Burned character cannot be removed from product |
| Flow chaos | Balance must be rebuilt from stable initial state |

**Why conservatism dominates (77% = MODERATE + CONSERVATIVE):** Failures are irreversible. Cost of batch loss exceeds any time saved. Aggressive programs (18%) exist for time-sensitive materials with experienced operators. ULTRA_CONSERVATIVE (5%) reserved for highest-value materials.

### Program Taxonomy (83 folios)
- Stability: MODERATE 55%, CONSERVATIVE 22%, AGGRESSIVE 18%, ULTRA_CONSERVATIVE 5%
- Waiting: LINK_MODERATE 47%, LINK_HEAVY 29%, LINK_SPARSE 17%
- 3 RESTART_CAPABLE (f50v, f57r, f82v)

### Control Engagement Intensity (CEI)
- 4 regimes ordered: REGIME_2 < REGIME_1 < REGIME_4 < REGIME_3
- LINK-CEI correlation = -0.7057 (strong negative)
- Manuscript ordering reduces CEI jumps (d=1.89)
- Restart folios at low-CEI positions (d=2.24)

### Operator Doctrine (OPS-7)
1. Waiting is default (38% LINK)
2. Escalation is irreversible
3. Restart requires low-CEI
4. Text holds position, not escape route
5. Throughput (REGIME_3) is transient

---

## Organizational Layer (Tier 2)

### Prefix/Suffix Coordinate System
- PIECEWISE_SEQUENTIAL geometry (PC1 rho=-0.624)
- 15 punctuated transitions, align with quire changes
- Local continuity d=17.5 vs random

### Human Track Layer (= "Uncategorized" = "Residue")

> **Status:** HTC phase confirmed HT is NON-OPERATIONAL with 3 independent tests (constraints 404-406). Interpretation permanently Tier 3-4.

**Definition:** Tokens NOT in the 479-type canonical grammar vocabulary. This is a TOKEN LIST definition - the grammar has exactly 479 specific token types; everything else is "uncategorized."

| Metric | Value |
|--------|-------|
| Occurrences | ~40,000 (33.4% of corpus) |
| Unique types | ~11,000 |
| Section-exclusive | 80.7% |
| Line-initial enrichment | 2.16x |
| Hazard proximity | 4.84 vs 2.5 expected (avoidance) |
| Forbidden seam presence | 0/35 (zero) |

**What these tokens ARE:** HT tokens form a **third compositional notation system** with its own morphology:

| Component | HT System | A/B System | Overlap |
|-----------|-----------|------------|---------|
| Prefixes | yk-, op-, yt-, sa-, so-, ka-, dc-, pc-, ... | ch-, qo-, sh-, da-, ok-, ot-, ct-, ol- | **ZERO** |
| Suffixes | -dy, -in, -ey, -ar, -hy, ... | -aiin, -dy, -ey, -or, ... | Partial |
| Coverage | 71.3% decomposable | 100% grammar | — |

This is NOT "alternative prefixes" or "scribal variants" — it is a disjoint formal layer.

**Function (SID-04/05):** ATTENTIONAL PACING (won 6/8 tests)
- NOT sensory checkpoints (avoid hazards, don't cluster near them)
- NOT quantitative markers (no counting behavior)
- NOT scribal errors (too systematic, section-specific)
- Serve human-facing navigation at SECTION level

**The Attentional Pacing Interpretation:**
The residue layer represents marks made by operators to **maintain attention during waiting phases**. Writing keeps hands busy so ears can work — monitoring for bubbles, hissing, changes in reflux rhythm. When attention is demanded (near hazards), writing **stops entirely** — not simpler marks, but ZERO marks.

**Key discovery (EXT-ECO-02):** 0 true HT tokens found near 17,984 hazard positions vs 4,510 near 1,000 random positions. Earlier "sparse HT near hazards" findings were artifacts. Operators don't write simpler marks near hazards — they write NOTHING.

**External validation:** Doodling improves attention by 29% (Andrade 2009). Medieval scribes made marginal marks during boring copying work. The practice is underdocumented but plausible.

**Practice Hypothesis (Tier 4):** 4/5 tests favor handwriting practice over random doodling:
- Rare grapheme over-representation 3.29x (p=0.0001)
- Run CV=0.43 matches fixed-block rehearsal (not memoryless)
- 28.5% boundary-pushing forms (exploring glyph limits)
- Section-level family rotation (change rate 0.71)

This suggests **purposeful calligraphy practice during waiting phases** — operators kept themselves alert through deliberate mark-making, not automatic scribbling.

**Unified Interpretation (Tier 4, HTD synthesis):**

> "While at station and not acting → practice calligraphy."

This collapses competing framings (attention maintenance vs diligent availability vs skill practice) into a single medieval work behavior. The structural evidence shows HT scales with program waiting intensity (Constraint 341) but isn't synchronized with specific LINK tokens (Constraint 342). The distinction between "staying alert" and "being available" is a modern psychological framing — the operator would simply say: *"I'm here, I'm not doing anything, I'm writing."*

Historical parallel: Medieval apprentice work-study combination (literacy training during physical labor) is documented but under-studied.

**Why Calligraphy Practice Fits (Tier 4):**

The theory survives because it explains more features with fewer assumptions than any alternative:

| Feature | Explanation |
|---------|-------------|
| Silent activity needed | Can't monitor apparatus (bubbles, hissing) while talking |
| B grammar insufficient | ~500 repeating tokens don't develop fine motor skills |
| ~11,000 unique HT types | Combinatorial stringing creates practice variety |
| 71.3% compositional | Trained practice follows learned combination rules |
| Disjoint prefix vocabulary | Avoids confusion with operational text |
| 80.7% section-exclusive | Different scribes/sessions have different habits |
| Modest position correlation | Habitual practice patterns become implicit position cues |
| Modest grammar correlation | Local copying/variation from nearby operational text |
| Complete hazard avoidance | Stop writing when attention demanded |

**Alternatives tested and rejected:**
- Material lists → 85.6% isolated (not list-like runs)
- Marginal glosses → Too systematic, doesn't explain hazard avoidance
- Cipher layer → Section isolation makes no sense
- Scribal errors → 33% error rate implausible, too structured
- Interleaved document → Why would it correlate with B's grammar/hazards?

This is the best-fitting interpretation. No alternative explains the combination of compositional structure, section exclusivity, grammar correlation, and hazard avoidance.

**HT-STATE Synthesis (Tier 2, HT-MORPH/HT-STATE):**

HT prefixes are **phase- and context-synchronized** to the operational grammar:

| Test | Finding | Effect |
|------|---------|--------|
| HT-STATE-1 | Position gradient | EARLY: op-, pc-, do- (effect -0.25); LATE: ta- (+0.06) |
| HT-STATE-2 | Grammar synchrony | V=0.136, p<0.0001 (2.5x null) |
| HT-STATE-3 | Regime association | EXTREME: al-, yk-, ke-, ka-, op-; LOW: yt- only |

> **HT is a formal, learned, non-executing annotation system that tracks human-relevant procedural phase and readiness while remaining synchronized to the operational grammar.**

This upgrades the attention/calligraphy model from plausible interpretation to **structurally supported architectural layer**. The coupling is real; the semantics remain unrecoverable.

**What HT is NOT:**
- NOT machine-state tracking (avoids hazards, removal doesn't affect execution)
- NOT material annotation (no referential tokens, no identifiers)
- NOT control-plane logic (downstream only, never upstream)

**What HT IS:**
- A parallel human-facing notation synchronized to procedural phase
- Phase-aware calligraphic practice that maintains operator readiness
- Structurally integrated but functionally independent of execution

**Speculative Waiting-Phase Vocabulary (Tier 4):**

| Label | Structural Function | Speculative Meaning |
|-------|---------------------|---------------------|
| ESTABLISHING | Section entry | System warming, circulation starting |
| RUNNING | Wait marker | Steady reflux, all normal |
| HOLDING | Persistence marker | Maintain state, extended patience |
| APPROACHING | Constraint rise | Watch closely, risk increasing |
| RELAXING | Constraint fall | Critical passed, ease vigilance |
| EXHAUSTING | Section exit | Run winding down |
| SECTION_n | Section-exclusive | "You are in section H/S/B/etc." |

Why written down: Vocabulary is private (80.7% section-exclusive), states are finer than oral tradition names (1,158 tokens), operator distrusted memory during long runs, interruption recovery needed.

**Key insight:** These tokens are NON-EXECUTABLE. Removing all 40,000 occurrences would not affect grammar coverage or hazard topology. They are infrastructure for human operators, not apparatus logic.

---

## Apparatus Layer (External, Non-Binding) — Tier 2

### Best Match: Circulatory Reflux Systems

- **Compatibility:** CLASS_D = 100% match; alternatives ≤20%
- **Historical Representative:** Pelican alembic (late 15th-century)
- **Structural Homology:** 8/8 dimensions match Brunschwig (1500) and pseudo-Geber (~1300)
- **Surviving Candidates:** Reflux Distillation (1.000), Distillation Column (0.875), Steam Boiler (0.833)
- **Eliminated:** Biological homeostasis systems (failed TEST_3: no external operator)

**What This DOES NOT Mean:**
- No specific products or feedstocks identified
- No materials or substances encoded
- Apparatus identification is SPECULATIVE and DISCARDABLE

---

## External Comparative Research (Non-Binding) — Tier 2

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

**7 STRONG alignments, 4 MODERATE** across 12 documented patterns.

### Human Factors Rationale

The design is optimized for:
- **Cognitive load reduction:** 9.8x vocabulary compression
- **Error prevention:** Discrete approved procedures, not continuous tuning
- **Interruption recovery:** Positional markers, physical pause points at quire boundaries
- **Expert operation:** No definitions, no remedial instruction

---

## Physics Plausibility Audit (Phase PPA) — Tier 2

### Verdict: PHYSICALLY PLAUSIBLE (7/7 tracks pass)

| Track | Question | Result |
|-------|----------|--------|
| P-1 | Irreversibility respected? | **PASS** — 17 forbidden = mutual exclusions |
| P-2 | Energy conservation consistent? | **PASS** — 62% kernel contact |
| P-3 | Latency tolerated? | **PASS** — 38% LINK, max 7 consecutive |
| P-4 | Noise tolerated? | **PASS** — 9.8x compression, 41% margin |
| P-5 | Control dimensions realistic? | **PASS** — 3 axes collapse to 1-D |
| P-6 | Extended stability achieved? | **PASS** — Grammar supports convergence (57.8% terminal STATE-C) |
| P-7 | Failure modes legible? | **PASS** — All 5 classes map to real failures |

A competent operator could use this grammar to control a real continuous physical system without violating thermodynamics, conservation laws, or causality.

---

## Speculative Findings (Tier 3-4)

### Process-Class Isomorphism (PCISO)
Survivors: Circulatory Reflux, Volatile Aromatic Extraction, Circulatory Conditioning
Common signature: CLOSED-LOOP CIRCULATORY THERMAL PROCESS CONTROL

### Material Class Compatibility — Tier 3

| Abstract Class | Real Medieval Materials | Grammar Fit |
|----------------|------------------------|-------------|
| CLASS_A (porous, swelling) | Dried leaves, flowers, roots, bark | COMPATIBLE |
| CLASS_B (dense, hydrophobic) | Resins, seeds, citrus peel | COMPATIBLE |
| CLASS_C (phase-unstable) | Fresh plant material, fats, emulsions | **INCOMPATIBLE** |
| CLASS_D (stable, rapid diffusion) | Alcohol/water mixtures, clear extracts | COMPATIBLE |
| CLASS_E (homogeneous fluid) | Distilled water, pure alcohol | COMPATIBLE |

Phase-unstable materials (CLASS_C) show 19.8% failure rate — grammar designed to AVOID phase transitions.

### Craft Interpretation (Phase OLF) — Tier 3

Five craft-meaning tests using perfumery as interpretive lens — all PLAUSIBLE:

| Test | Verdict |
|------|---------|
| Token clusters align with smell-change windows? | PLAUSIBLE |
| Tokens encode warning memories? | ALL CRAFT-PLAUSIBLE |
| Tokens support resumption after breaks? | STRONGLY PLAUSIBLE |
| Same roles, different vocabulary across sections? | YES — CRAFT NAMING |
| Absences match perfumery tacit knowledge? | EXACTLY ALIGNED |

**Coherent narrative:** Human-track tokens make *perfect craft sense* as perfumer's working marks — navigation and warning for experienced operators, not instruction for novices.

> *"If this were a perfumery manual, these marks would almost certainly be there for this reason — and it would be strange if they weren't."*

### Product-Space Plausibility (PSP)
Plausible families: Aromatic Waters, Essential Oils, Resin Extracts, Digested Preparations, Stabilized Compounds

### Product Isolation Analysis (PIA)
Primary candidate: **Aromatic Waters** (90.5% convergence)
Multi-product workshop likely

**83-Program Interpretation:**
Programs likely represent **substrate × intensity combinations**, not 83 distinct products. An operator might make 5-10 things using many programs depending on material source, condition, and batch.

| Product | Programs Used | Frequency |
|---------|---------------|-----------|
| Aromatic waters | CONSERVATIVE, MODERATE | Primary |
| Medicinal waters | MODERATE | Secondary |
| Resin extracts | AGGRESSIVE | Occasional |
| Stabilization | ULTRA_CONSERVATIVE | As needed |

### Plant Illustration Alignment (PIAA)
- 86.7% perfumery-aligned (p<0.001)
- 73% root emphasis
- No program-morphology correlation

### Material Domain (EXT-MAT-01)
BOTANICAL_FAVORED (HIGH confidence): 8/8 tests favor aromatic-botanical over alchemical-mineral (ratio 2.37)

### Institutional Compatibility (EXT-6)
Survivors: Goldsmith/assayer workshops (Central Europe 1400-1550, N. Italy 1400-1470)

### Historical Scale (Tier 4)
~1,800 catalog entries is plausible but exceptional for 15th c. — larger than typical recipe books (300-400) but consistent with major institutional operations (Santa Maria Novella, Venetian muschieri guild). See `phases/CAS_POST/historical_scale_comparison.md`.

### Program Forgiveness Gradient (Tier 4, Phase SITD)

Programs vary along a **forgiving ↔ brittle** axis (5σ spread) that is partially independent of aggressive/conservative:

| Quartile | Hazard Density | Escape Density | Safe Run |
|----------|----------------|----------------|----------|
| Q1 (Brittle) | 11.1% | 7.5% | 27.6 |
| Q4 (Forgiving) | 7.8% | 23.8% | 45.0 |

- Hazard-Escape correlation: -0.184 (relatively independent dimensions)
- Effect size vs aggressive/conservative: 0.509 (moderate, not identical)
- Most brittle: f33v, f48v, f39v (concentrated hazards, few escapes)
- Most forgiving: f77r, f82r, f83v (many escape routes, spread-out hazards)

**Interpretation:** The grammar provides different amounts of "slack" for operator error. Forgiving programs offer more recovery paths, potentially serving less experienced operators. This is consistent with a **competency-graded reference** model but remains interpretive (Tier 4).

---

## Validated Constraints (411 Total)

### Executability (72-84, 115-125)
| # | Constraint |
|---|------------|
| 74 | Dominant convergence to stable states (57.8% STATE-C terminal; SEL-F revision) |
| 79 | Only STATE-C essential |
| 84 | System targets MONOSTATE (STATE-C); 42.2% of folios end in transitional states (SEL-F revision) |
| 115 | 0 non-executable tokens |
| 119 | 0 translation-eligible zones |
| 120 | PURE_OPERATIONAL verdict |
| 121 | 49 instruction equivalence classes (9.8x compression) |
| 124 | 100% grammar coverage |

### Kernel Structure (85-95, 103-108)
| # | Constraint |
|---|------------|
| 85 | 10 single-character primitives (s, e, t, d, l, o, h, c, k, r) |
| 89 | Core within core: k, h, e |
| 90 | 500+ 4-cycles, 56 3-cycles (topological; Phase CYCLE found NO distinct semantics — 100% token overlap) |
| 103 | k = ENERGY_MODULATOR |
| 104 | h = PHASE_MANAGER |
| 105 | e = STABILITY_ANCHOR (54.7% recovery paths) |
| 107 | All kernel nodes BOUNDARY_ADJACENT to forbidden transitions |

### Hazard Topology (109-114)
| # | Constraint |
|---|------------|
| 109 | 5 failure classes (PHASE_ORDERING dominant 41%) |
| 110 | PHASE_ORDERING 7/17 = 41% |
| 111 | 65% asymmetric (SEL-D revision) |
| 112 | 59% distant from kernel (SEL-D revision) |

### Language Rejection (130-132)
| # | Constraint |
|---|------------|
| 130 | DSL hypothesis rejected (0.19% reference rate) |
| 131 | Role consistency LOW (23.8%) |
| 132 | Language encoding CLOSED |

### Organizational Structure (153-177)
| # | Constraint |
|---|------------|
| 153 | Prefix/suffix axes partially independent (MI=0.075) |
| 154 | Extreme local continuity (d=17.5) |
| 155 | Piecewise-sequential geometry (PC1 rho=-0.624) |
| 156 | Detected sections match codicology (quantified by QLA: 4.3x quire-section alignment) |
| 157 | Circulatory reflux uniquely compatible (100%) |
| 158 | Extended runs necessary (12.6% envelope gap) |
| 159 | Section boundaries organizational (F-ratio 0.37) |
| 160 | Variants are discrete alternatives (43%) |
| 161 | Folio ordering shows risk gradient (rho=0.39) |
| 162 | Aggressive programs buffered (88% vs 49% null) |
| 163 | 7 domains ruled incompatible |
| 164 | Botanical illustrations 86.7% perfumery-aligned |
| 165 | No program-morphology correlation |
| 166 | Uncategorized: zero forbidden seam presence (0/35) |
| 167 | Uncategorized: 80.7% section-exclusive |
| 168 | Uncategorized: single unified layer |
| 169 | Uncategorized: hazard avoidance 4.84 vs 2.5 |
| 170 | Uncategorized: morphologically distinct (p<0.001) |
| 171 | Only continuous closed-loop process control survives |
| 172 | ~~Human-track 99.6% LINK-proximal~~ **SUPERSEDED by Constraint 342** (HTD: ρ=0.010, decoupled) |
| 173 | Linguistic hypothesis EXHAUSTED |
| 174 | Intra-role outcome divergence (CF-1=0.62, CF-2=0.34) |
| 175 | 3 process classes survive (reflux, extraction, conditioning) |
| 176 | 5 product families survive |
| 177 | Both extraction/conditioning survive; extraction favored |

### OPS Findings (178-198)
| # | Constraint |
|---|------------|
| 178 | 83 folios yield 33 operational metrics |
| 179 | 4 stable regimes (K-Means k=4, Silhouette=0.23) |
| 180 | All 6 aggressive folios in REGIME_3 |
| 181 | 3/4 regimes Pareto-efficient; REGIME_3 dominated |
| 182 | Restart-capable = higher stability (0.589 vs 0.393) |
| 183 | No regime dominates all axes |
| 184 | 9 pressure-induced transitions; 3 prohibited |
| 185 | REGIME_3 = transient throughput state |
| 186 | No pressure-free cycles |
| 187 | CEI manifold formalized |
| 188 | CEI bands: R2 < R1 < R4 < R3 |
| 189 | CEI bidirectional; down-CEI easier (1.44x) |
| 190 | LINK-CEI r=-0.7057 |
| 191 | CEI smoothing (d=1.89) |
| 192 | Restart at low-CEI (d=2.24) |
| 193 | Navigation WORSE than random (d=-7.33) |
| 194 | PARTIAL codex organization (2/5) |
| 195 | Human-track compensation NOT detected |
| 196 | 100% match EXPERT_REFERENCE archetype |
| 197 | Designed for experts, not novices |
| 198 | OPS CLOSED; 5 core principles |

### EXT Findings (199-223)
| # | Constraint |
|---|------------|
| 199 | Both mineral AND botanical now survive (EXT-4 revised) |
| 200 | 6 survivors: 2 Final Products, 3 Platform Reagents, 1 Intermediate |
| 201 | Guild-restricted, court-sponsored ecosystem |
| 202 | Goldsmith/assayer workshops survive |
| 203 | Voynich structurally exceptional |
| 204 | OPS-R RESOLVED by SEL-F (definitional ambiguity, not formal contradiction) |
| 205 | Residue 82% section-exclusive |
| 206 | Sections not compressible to regimes |
| 207 | 0/18 micro-cipher tests passed |
| 208 | Residue compatible with non-encoding dynamics |
| 209 | Attentional pacing wins (6/8) |
| 210 | External alignments robust to HT removal |
| 211 | Seasonal ordering underpowered |
| 212 | 93% plants peak May-August |
| 213 | Opportunity-loss model supported (64.7% premature hazards) |
| 214 | EXT-4 duration criterion INVALIDATED |
| 215 | BOTANICAL_FAVORED (8/8 tests, ratio 2.37) |
| 216 | Hybrid hazard model (71% batch, 29% apparatus) |
| 217 | 0 true HT near hazards |
| 218-220 | Hygiene audits: all findings ROBUST |
| 221 | Practice-leaning (4/5) |
| 222 | No intentional layout function |
| 223 | Procedural fluency MIXED |

### Currier A Disjunction (224-232)
| # | Constraint |
|---|------------|
| 224 | A coverage = 13.6% (threshold 70%); 66.8% novel vocabulary |
| 225 | A transition validity = 2.1% |
| 226 | A has 5 forbidden violations (B has 0) |
| 227 | A LINK density = 3.0% (B = 6.6%) |
| 228 | A density = 0.35x B |
| 229 | A = DISJOINT |
| 230 | A silhouette = 0.049 (no grammatical structure) |
| 231 | A is REGULAR but NOT GRAMMATICAL |
| 232 | A section-conditioned but class-uniform |

### Currier A Schema (233-240)
| # | Constraint |
|---|------------|
| 233 | A = LINE_ATOMIC |
| 234 | A = POSITION_FREE |
| 235 | 8+ mutually exclusive markers |
| 236 | A = FLAT (not hierarchical) |
| 237 | A = DATABASE_LIKE |
| 238 | Global schema, local instantiation |
| 239 | A/B separation = DESIGNED (0.0% cross-transitions) |
| 240 | A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY |

### Structural Primitives (241-249)
| # | Constraint |
|---|------------|
| 241 | daiin A-enriched (1.55x), ol B-enriched (0.21x) |
| 242 | daiin neighborhood flip (content in A, grammar in B) |
| 243 | daiin-ol adjacent: 54 in B, 27 in A |
| 244 | Infrastructure reuse without semantic transfer |
| 245 | MINIMAL vocabulary: exactly 2 tokens (daiin, ol) |
| 246 | 4 mandatory criteria for structural primitives |
| 247 | SP-01 (daiin): affects 30.2% A, 16.5% B |
| 248 | SP-02 (ol): affects 7.4% A, 17.7% B |
| 249 | Scan COMPLETE: 11 candidates tested |

### Multiplicity Encoding (250-260)
| # | Constraint |
|---|------------|
| 250 | A encodes multiplicity via literal repetition; 64.1% show `[BLOCK] × N` |
| 251 | Repetition is intra-record only; no aggregation or arithmetic |
| 252 | Repetition bounded 2-6x; distribution peaks at 2x (416), 3x (424) |
| 253 | All blocks unique (0% cross-entry reuse) |
| 254 | Multiplicity does NOT interact with B; isolated from operational grammar |
| 255 | Blocks 100% SECTION-EXCLUSIVE; zero cross-section reuse (CAS-DEEP) |
| 256 | Markers at block END 60.3% (vs 44% start); marker is trailing tag (CAS-DEEP) |
| 257 | 72.6% of tokens MARKER-EXCLUSIVE; markers define distinct vocabulary domains (CAS-DEEP) |
| 258 | 2x/3x ratio = 0.981 (near-equal); suggests deliberate design, not random (CAS-DEEP) |
| 259 | INVERSE COMPLEXITY: higher repetitions have MORE diverse blocks (rho=0.248) (CAS-DEEP) |
| 260 | Section vocabulary overlap 9.7% (Jaccard); sections are isolated domains (CAS-DEEP) |
| 261 | Token order NON-RANDOM: shuffling destroys blocks (4.2% survive); original order meaningful (CAS-DEEP-V) |
| 262 | LOW MUTATION across repetitions: 7.7% variation; blocks similar but not identical (CAS-DEEP-V) |
| 263 | Section-specific ceilings: H max=5x, P max=5x, T max=6x (CAS-DEEP-V) |
| 264 | Inverse-complexity is BETWEEN-MARKER effect (Simpson's paradox); within-marker rho<0 for all 8 markers (CAS-DEEP-V) |
| 265 | 1,123 unique marker tokens across 8 classes; 85 core tokens (freq>=10); `daiin` dominates DA (51.7%), `ol` dominates OL (32.3%) (CAS-CAT) |
| 266 | Currier A has TWO content types: block entries (64.1%) have ONE marker class (exclusive); non-block entries (35.9%) mix MULTIPLE classes (90.5% have 2-8 classes) (CAS-SCAN) |

### Compositional Morphology (267-271)
| # | Constraint |
|---|------------|
| 267 | Marker tokens are COMPOSITIONAL: decompose into PREFIX + [MIDDLE] + SUFFIX with orthogonal reuse (CAS-MORPH) |
| 268 | 897 observed PREFIX × MIDDLE × SUFFIX combinations; identity space scales combinatorially from small codebook (CAS-MORPH) |
| 269 | 7 UNIVERSAL suffixes across 6+ prefixes; 3 UNIVERSAL middles across 6+ prefixes (CAS-MORPH) |
| 270 | Some middles are PREFIX-EXCLUSIVE (CT:-h-, DA:-i-, QO:-kch-); internal structure within classifier families (CAS-MORPH) |
| 271 | Compositional structure explains low TTR (0.137) and high bigram reuse (70.7%); components combine predictably (CAS-MORPH) |
| 272 | A and B are on COMPLETELY DIFFERENT folios: 0 shared folios (A=114, B=83); physical manuscript separation, not just vocabulary (CAS-PHYS) |

### Prefix Taxonomy Compatibility (273-280)
| # | Constraint |
|---|------------|
| 273 | Section specialization NON-UNIFORM: CT is 85.9% Section H vs OK/OL at 53-55%; at least one prefix is specialized to one product line (EXT-8) |
| 274 | Co-occurrence UNIFORM: no prefix pair shows strong association (>1.5x) or avoidance (<0.5x) in compounds; prefixes can combine freely (EXT-8) |
| 275 | Suffix-prefix interaction SIGNIFICANT (Chi2 p=2.69e-05): different prefixes have different suffix preferences; EXCLUDES prefixes being processing states (EXT-8) |
| 276 | MIDDLE is PREFIX-BOUND: 28 middles EXCLUSIVE to single prefix (Cramer's V=0.674); MIDDLE is TYPE-SPECIFIC refinement, not universal property (EXT-8) |
| 277 | SUFFIX is UNIVERSAL: 22 of 25 significant suffixes appear in 6+ prefix classes; SUFFIX = universal output form applicable to all types (EXT-8) |
| 278 | Three-axis HIERARCHY: PREFIX (family) → MIDDLE (type-specific) → SUFFIX (universal form); signature of MATERIAL CLASSIFICATION SYSTEM (EXT-8) |
| 279 | STRONG cross-axis dependencies: all three pairwise interactions p < 10⁻³⁰⁰; axes are HIERARCHICALLY RELATED, not independent dimensions (EXT-8) |
| 280 | Section P ANOMALY: suffix -eol is 59.7% Section P (only axis value favoring P); suggests P involves specific output form (EXT-8) |
| 281 | Components SHARED: all 8 prefixes, all 27 suffixes appear in BOTH A and B; only 9 middles are A-exclusive (mostly CT-family); SAME ALPHABET, DIFFERENT GRAMMAR (EXT-8) |
| 282 | Component ENRICHMENT: CT is A-enriched (0.14x), OL/QO are B-enriched (5x/4x); -dy suffix 27x B-enriched, -or 0.45x A-enriched; usage patterns differ dramatically (EXT-8) |

### Cross-System Mapping (283-286)
| # | Constraint |
|---|------------|
| 283 | Suffixes show CONTEXT PREFERENCE: -or (0.67x), -chy (0.61x), -chor (0.18x) A-enriched; -edy (191x!), -dy (4.6x), -ar (3.2x) B-enriched; -ol, -aiin BALANCED (EXT-9) |
| 284 | CT in B is CONCENTRATED in specific folios (48 folios); when CT appears in B it uses B-suffixes (-edy, -dy); registry materials take operational form in procedures (EXT-9) |
| 285 | 161 BALANCED tokens (0.5x-2x ratio) serve as shared vocabulary; DA-family dominates; cross-reference points between A and B (EXT-9) |
| 286 | Modal preference is PREFIX x SUFFIX dependent; CT consistently A-enriched across suffixes, OL consistently B-enriched; not simple suffix-determines-context (EXT-9) |

### Ratio Hypothesis FALSIFIED (287-290)
| # | Constraint |
|---|------------|
| 287 | Repetition does NOT encode abstract quantity, proportion, or scale; remains LITERAL ENUMERATION without arithmetic semantics (EXT-9B RETRACTION) |
| 288 | 3x dominance (55%) reflects human counting bias and registry ergonomics, NOT proportional tiers; no cross-entry comparison mechanism exists (EXT-9B RETRACTION) |
| 289 | Folio-level uniformity reflects ENUMERATION DEPTH PREFERENCE (scribal convention, category density), NOT batch scale; no reference frame for ratios (EXT-9B RETRACTION) |
| 290 | Same composition with different counts confirms count is INSTANCE MULTIPLICITY, not magnitude; "3x here" is not comparable to "3x there" due to section isolation (EXT-9B RETRACTION) |

### Optional Articulator Layer (291)
| # | Constraint |
|---|------------|
| 291 | ~20% of Currier A tokens have OPTIONAL ARTICULATOR forms (yk-, yt-, kch-, etc.); MORE section-concentrated than core prefixes; 100% removable without identity loss; systematic refinement layer, not noise (EXT-9B) |

### CAS-POST Findings (292-297)
| # | Constraint |
|---|------------|
| 292 | Articulators contribute ZERO unique identity distinctions; ablation creates 0 collisions; purely EXPRESSIVE, not discriminative (CAS-POST) |
| 293 | Component essentiality hierarchy: MIDDLE (402 distinctions) > SUFFIX (13) > ARTICULATOR (0); PREFIX provides foundation (1387 base); MIDDLE is primary discriminator (CAS-POST) |
| 294 | Articulator density INVERSELY correlates with prefix count (15% at 0-1 prefix to 4% at 6 prefixes); articulators COMPENSATE for low complexity (CAS-POST) |
| 295 | Sections exhibit DISTINCT configurations: H=dense mixed (87% mixed, 8.2% art), P=balanced (48% exclusive, 5.1% art), T=uniform sparse (81% uniform, 2.57x mean rep) (CAS-POST) |
| 296 | CH appears in nearly all common prefix pairs (CH+DA, CH+QO, CH+SH); functions as UNIVERSAL MIXING ANCHOR (CAS-POST) |
| 297 | -eol is ONLY suffix concentrated in section P (55.9% vs 41.3% H); all other suffixes favor H; P has distinct suffix profile (CAS-POST) |

### B-Specific Operators (298)
| # | Constraint |
|---|------------|
| 298 | L-compound middle patterns (lch-, lk-, lsh-) function as B-specific grammatical operators; 30-135x more common in B, largely absent from A; grammar-level specialization not covered by shared component inventory (B-MORPH) |

### A↔B Cross-Reference (299)
| # | Constraint |
|---|------------|
| 299 | Section H vocabulary dominates B procedures (76/83 = 91.6%); Section P rare (7/83 = 8.4%); Section T absent (0/83 = 0%); chi² = 127.54, p < 0.0001; A sections have NON-UNIFORM mapping to B procedure applicability (CAS-XREF) |

### Astronomical/Zodiac/Cosmological Hybrid (300-305)
| # | Constraint |
|---|------------|
| 300 | 9,401 tokens (7.7%) in A/Z/C sections are UNCLASSIFIED by Currier A/B; concentrated in 30 folios across Astronomical, Zodiac, Cosmological sections; prior binary A/B model was incomplete (AZC) |
| 301 | AZC text is HYBRID: B vocabulary coverage 69.7%, A vocabulary coverage 65.4%, shared vocabulary 60.5%; straddles classification thresholds (AZC) |
| 302 | AZC has DISTINCT line structure: median 8 tokens/line (vs A=22, B=31); TTR 0.285 (vs A=0.137, B=0.096); consistent with diagrammatic annotation (AZC) |
| 303 | AZC has ELEVATED LINK density (7.6%) — higher than both A (3.0%) and B (6.6%); most wait-heavy text in manuscript (AZC) |
| 304 | AZC has 25.4% UNIQUE vocabulary (1,529 types) absent from both A and B; section-specific terminology (AZC) |
| 305 | AZC-unique vocabulary is 98% SECTION-EXCLUSIVE, 37% line-initial, 37% line-final, 65.9% hapax; structural signature of LABELING function distinct from execution (B) or indexing (A) (AZC-PROBE) |
| 306 | AZC-unique tokens exhibit a finite, repeatable set of placement-dependent classes (C, P, R1-R3, S-S2, Y) with non-uniform distribution; orthogonal to morphological identity, recur across folios, participate in repetition-based multiplicity, integrate into surrounding hybrid grammar; establishes formal PLACEMENT-CODING axis within AZC inscriptional mode (AZC-PLACEMENT) |
| 307 | Placement x Morphology dependency: Cramer's V = 0.18 (PREFIX), 0.17 (SUFFIX); placement class weakly influences morphological form; axes NOT fully orthogonal (AZC-AXIS) |
| 308 | Numeric placement subscripts are ORDERED: R1>R2>R3 and S>S1>S2 in middle component length (monotonic decrease); subscripts encode ordinal position, not arbitrary labels (AZC-AXIS) |
| 309 | Placement transitions show grammar-like constraints: 99 forbidden bigrams (<20% expected), all self-transitions enriched 5-26x; labels cluster by placement class; cross-placement transitions systematically avoided (AZC-AXIS) |
| 310 | Placement constrains repetition depth: P, S-series allow higher repetition (mean 2.7-3.0); R-series allows lower (mean 2.1-2.4); multiplicity is placement-gated (AZC-AXIS) |
| 311 | Positional grammar detected: S1, S2, X, L are BOUNDARY specialists (85-90% line-edge); R1, R2, R3 are INTERIOR specialists (3-9% boundary); placement encodes line position (AZC-AXIS) |
| 312 | Section x Placement strong dependency: Cramer's V = 0.631; Z, A, C sections have distinct placement profiles; section identity constrains placement vocabulary (AZC-AXIS) |

### Positional Legality and Diagram Anchoring (313-320)
| # | Constraint |
|---|------------|
| 313 | Position constrains LEGALITY not PREDICTION: Grammar collapse in 7 placements (A1), 219 forbidden token-placement pairs at z=13 (A2), but kernel sensitivity weak (A3) and prediction gain only 14% (A4); position defines what's ALLOWED, not what's LIKELY (AZC-AXIS) |
| 314 | Global illegality + local exceptions: 100% of forbidden tokens are forbidden across multiple placements; 0 placement-specific forbidden tokens; default-deny with explicit permits, not role-based permissions (AZC-AXIS) |
| 315 | Placement-locked operators: 9/18 restricted operators (frequent AZC-only tokens) appear in exactly ONE placement; examples: otaldar only in S2, okesoe only in P, cpheeody only in C (AZC-AXIS) |
| 316 | Phase-locked binding: Rotation invariance test shows 32.3 percentage point binding drop; token-placement mapping is anchored to absolute position, not relative topology (AZC-AXIS) |
| 317 | Hybrid architecture: C placement is rotation-tolerant (9.8% drop), P/R/S are phase-locked (40-78% drop); system has topological core with positional frame (AZC-AXIS) |
| 318 | Folio-specific placement profiles: Cramer's V = 0.507 for folio x placement; different folios have distinctly different placement distributions; diagram layout varies by folio (AZC-AXIS) |
| 319 | Template reuse in zodiac folios: f71r through f73v share identical placement profile (R1 dominant 25-40%, R2/S1 secondary); diagrams use reusable positional templates (AZC-AXIS) |
| 320 | S2 < S1 ordered sequence: S2 appears earlier than S1 (p < 0.0001, Mann-Whitney U); S-series marks ordered positions, not arbitrary boundaries (AZC-AXIS) |
| 321 | Zodiac vocabulary is FOLIO-ISOLATED: mean consecutive Jaccard = 0.076 (std 0.015); each zodiac diagram has largely independent vocabulary; structural template, not gradual drift (AZC-AXIS) |
| 322 | Placement coverage is SEASONALLY CLUSTERED: only 5/25 placements have full zodiac coverage; 8 partial, 12 absent; confirms SEASON-GATED WORKFLOW interpretation (AZC-AXIS) |
| 323 | Terminal state distribution: 57.8% STATE-C, 38.6% "other" (transitional), 3.6% "initial" (reset); 42% non-STATE-C concentrated in sections H/S and earlier positions (SEL-F, Tier 2) |
| 324 | Terminal state is SECTION-DEPENDENT: Sections H/S ~50% STATE-C, Sections B/C 70-100% STATE-C (SEL-F, Tier 2) |
| 325 | COMPLETION GRADIENT exists: STATE-C increases with position (rho=+0.24, p=0.03); vocabulary DECREASES (-0.44); A-ref density INCREASES (+0.31); later folios do LESS with HIGHER completion (SEL-F, Tier 2) |
| 326 | A-reference sharing within clusters: 1.31x enrichment (p<0.000001); material conditioning is real but SOFT and OVERLAPPING (silhouette=0.018); NOT a clean taxonomy (SEL-F, Tier 2) |
| 327 | Cluster 3 (f75-f84) is locally anomalous: only contiguous cluster, 70% STATE-C, highest A-ref coherence (0.294); LOCAL observation, not organizational law (SEL-F, Tier 2) |
| 328 | Grammar noise robustness: 10% token corruption produces only 3.3% entropy increase; structure degrades GRACEFULLY (ROBUST, Tier 2) |
| 329 | Grammar ablation robustness: Removing top 10 tokens (15% of corpus) produces only 0.8% entropy change; no single token dominates (ROBUST, Tier 2) |
| 330 | Grammar cross-validation: Leave-one-folio-out shows max 0.25% entropy change, std 0.06%; no single folio dominates (ROBUST, Tier 2) |
| 331 | 49-class minimality: Number is functional classification (morphological), not optimal clustering; silhouette near zero for all k; prior audit WEAKENED finding CONFIRMED (ROBUST, Tier 2) |
| 332 | Kernel bigram ordering: h->k is SUPPRESSED (0 observed); k->k and h->h are ENRICHED (self-transitions); chi-square p < 0.000001; formal ordering constraint exists (KERNEL, Tier 2) |
| 333 | Kernel trigram dominance: e->e->e = 97.2% of kernel trigrams; entropy = 0.27 bits (vs 4.75 max); system dominated by 'e' state with rare k/h interruptions (KERNEL, Tier 2) |
| 334 | LINK section conditioning: LINK density varies by section (B=19.6%, H=9.1%, C=10.1%, S=9.8%); Section B requires 45% more waiting; kernel state does NOT condition LINK (z=0.05 vs null); waiting is section-driven (LINK, Tier 2) |
| 335 | A-B vocabulary integration: 69.8% of B tokens appear in A vocabulary; A and B are FOLIO-disjoint and GRAMMAR-disjoint but VOCABULARY-integrated; 1,532 shared types across 83 B folios (AB_INTEGRATION, Tier 2) |
| 336 | Hybrid A-access pattern: Adjacent B folios share more A-vocabulary (0.548 vs 0.404, p < 0.000001) AND similar B-programs share more A-vocabulary (0.427 vs 0.256, p = 0.009); operators use BOTH sequential reading and semantic lookup (AB_INTEGRATION, Tier 2) |
| 337 | Mixed-marker dominance: 89.2% of A lines contain 2+ marker classes; exclusive lines (8.7%) are shorter (14.5 vs 24.8 tokens), appear later in folios (10.5 vs 8.2), and have less B-vocabulary (65.6% vs 76.1%); mixing is NORM, exclusivity is SPECIALIZED (MIXED, Tier 2) |
| 338 | Marker co-occurrence independence: All marker pair ratios 0.9-1.0 (observed/expected); no enriched (>1.5x) or avoided (<0.5x) pairs; markers mix FREELY without grammatical constraints (MIXED, Tier 2) |
| 339 | E-class dominance: 36% of Currier B tokens are e-class (stability markers); k+h combined = 0.3%; grammar is structurally stability-dominated, consistent with equilibrium-seeking control (PHYS, Tier 2) |
| 340 | LINK-escalation complementarity: LINK density near escalation is 0.605x baseline (p < 0.001); waiting (LINK) and intervention (k/h) are functionally segregated; grammar separates monitoring from action (PHYS, Tier 2) |
| 341 | HT-program stratification: HT density varies monotonically by waiting profile (EXTREME 15.9% > HIGH 10.4% > MODERATE 8.5% > LOW 5.7%; Kruskal-Wallis p < 0.0001); HT is a program-level characteristic, not a token-level response (HTD, Tier 2) |
| 342 | HT-LINK decoupling: HT density is independent of LINK density at folio level (Spearman ρ = 0.010, p = 0.93); the "more LINK = more doodling" hypothesis is falsified; HT is not synchronized with LINK token positions (HTD, Tier 2) |
| 343 | A-AZC persistence independence: A-vocabulary tokens appear in 2.2x more AZC placements than AZC-only tokens (p < 0.0001); high-multiplicity A-tokens have 43% broader coverage (p = 0.001); A-registry assets persist independently of AZC legality windows; supports managed stewardship model (AAZ, Tier 2) |
| 344 | HT-A inverse coupling: HT density is negatively correlated with A-vocabulary reference density within B programs (rho = -0.367, p < 0.001); high-HT programs use LESS registry vocabulary; HT tracks cognitive spare capacity, not just temporal opportunity; operators write more when procedures are simpler (AAZ, Tier 2) |

### Currier A Folio Organization (345-346)
| # | Constraint |
|---|------------|
| 345 | Currier A folios lack thematic coherence: within-folio vocabulary similarity (J=0.018) equals between-folio similarity (J=0.017); folio boundaries are physical containers, not organizational units (CAS-FOLIO, Tier 2) |
| 346 | Currier A exhibits SEQUENTIAL COHERENCE: adjacent entries share 1.31x more vocabulary than non-adjacent entries (p<0.000001); local clustering exists without folio-level structure (CAS-FOLIO, Tier 2) |

### HT Morphology and Synchrony (347-348)
| # | Constraint |
|---|------------|
| 347 | HT tokens form a compositional notation system with disjoint prefix vocabulary: HT prefixes (yk-, op-, yt-, sa-, etc.) have ZERO overlap with A/B prefixes (ch-, qo-, sh-, etc.); 71.3% of HT types decompose into HT_PREFIX + MIDDLE + SUFFIX; this is a third formal layer, not scribal noise (HT-MORPH, Tier 2) |
| 348 | HT prefixes are phase- and context-synchronized: position effect sizes up to -0.25 (EARLY: op-, pc-, do-; LATE: ta-); grammar synchrony V=0.136 (p<0.0001); regime association V=0.123 (EXTREME-associated: al-, yk-, ke-, ka-, op-; LOW-associated: yt-); HT tracks human-relevant procedural phase while remaining coupled to operational grammar (HT-STATE, Tier 2) |

### Morphology Closure (349-352)
| # | Constraint |
|---|------------|
| 349 | Extended cluster prefix inventory: pch, tch, kch, dch, fch, rch, sch added to original clusters (ck, ckh, ds, dsh, cp, cph, ks, ksh, ts, tsh, ps, psh); all follow C+C+h pattern; combine with multiple B-suffixes (MORPH-CLOSE, Tier 2) |
| 350 | HT+B hybrids (HT prefix + B suffix) = 12.47% of corpus; formally explained as cross-layer morphological reuse, not mysterious tokens (MORPH-CLOSE, Tier 2) |
| 351 | Final morphology classification: 92.66% explained, 3.90% ambiguous (known components in unclear position), 2.82% noise (single chars + damaged), 0.62% TRUE ORPHAN (MORPH-CLOSE, Tier 2) |
| 352 | TRUE ORPHAN residue (0.62%) consists of consonant ligatures (dl, lr, ld), vowel-initial fragments, and scribal artifacts; no evidence for unaccounted formal system (MORPH-CLOSE, Tier 2) |

### Folio Gap Analysis (353-356)
| # | Constraint |
|---|------------|
| 353 | State continuity between adjacent Currier B folios is BETTER than random (d=-0.20); no extreme discontinuities (>3 sigma) detected; largest transitions explicable by restart mechanisms (FG, Tier 2) |
| 354 | EARLY-phase HT prefixes (op-, pc-, do-) are 2.69x enriched at folio starts; orientation pattern intact; no evidence of mid-procedure folio starts (FG, Tier 2) |
| 355 | 75.9% of Currier B folios start with known morphological prefixes; 18.1% are EVA-valid compositional forms; 6.0% (5 folios) are transcription artifacts (damaged tokens, rare 'm' glyph, truncated entries); no structurally anomalous starts detected (FG, Tier 2) |
| 356 | Section variance asymmetry is negligible (max 0.0027, mean 0.0014); no truncation signal in any section; internal symmetry preserved (FG, Tier 2) |

### Line-Level Control Architecture (357-360)
| # | Constraint |
|---|------------|
| 357 | Line lengths in Currier B are 3.3x more regular than random breaks (CV 0.263 vs 0.881, z=-3.60); lines are DELIBERATELY CHUNKED, not scribal wrapping (LINE, Tier 2) |
| 358 | Specific tokens mark line boundaries: `daiin`, `saiin`, `sain` at line-initial (3-11x enrichment); `am`, `oly`, `dy` at line-final (4-31x enrichment); chi-square p=1.3e-15 (LINE, Tier 2) |
| 359 | LINK tokens are SUPPRESSED at line boundaries (0.60x vs mid-line); lines are NOT pause/wait points but formal structural units (LINE, Tier 2) |
| 360 | Grammar forbidden transitions are respected across line breaks: 0 violations in 2,338 cross-line bigrams; grammar is LINE-INVARIANT (LINE, Tier 2) |

### B-Folio Vocabulary Patterns (361-364)
| # | Constraint |
|---|------------|
| 361 | Adjacent B folios share 1.30x more vocabulary than non-adjacent (p<0.000001, d=0.76); supports sequential composition/reading (BVP, Tier 2) |
| 362 | Control regimes (REGIME_1-4) have distinct vocabulary fingerprints: within-regime 1.29x more similar than between-regime (p=0.002); regimes are categorical not just parametric (BVP, Tier 2) |
| 363 | Vocabulary is INDEPENDENT of stability and LINK profiles (ratio ~1.05); operational intensity emerges from token patterns, not vocabulary selection (BVP, Tier 2) |
| 364 | B vocabulary is hub-peripheral: 41 core tokens (in >=50% of folios), 3,368 unique tokens (68%, in only 1 folio); 3 vocabulary outliers (f113r, f66v, f105v) (BVP, Tier 2) |

### LINK Distribution (365-366)
| # | Constraint |
|---|------------|
| 365 | LINK tokens are SPATIALLY UNIFORM within folios and lines: no positional clustering (p=0.005), run lengths match random (z=0.14), line-position uniform (p=0.80); LINK has no positional marking function (LDF, Tier 2) |
| 366 | LINK marks GRAMMAR STATE TRANSITIONS: preceded by AUXILIARY (1.50x), FLOW_OPERATOR (1.30x); followed by HIGH_IMPACT (2.70x), ENERGY_OPERATOR (1.15x); p<10^-18; LINK is boundary between monitoring and intervention phases (LDF, Tier 2) |

### Quire-Level Organization (367-370)
| # | Constraint |
|---|------------|
| 367 | Manuscript sections are QUIRE-ALIGNED: 12/18 quires are single-section, mean homogeneity 0.923 (4.3x random); physical binding reflects logical organization (QLA, Tier 2) |
| 368 | Control regimes CLUSTER within quires: within-quire same-regime rate 2.20x between-quire rate; quires organized by operational profile (QLA, Tier 2) |
| 369 | Vocabulary shows QUIRE CONTINUITY: within-quire Jaccard 1.69x between-quire (p<10^-243); folios in same quire share vocabulary (QLA, Tier 2) |
| 370 | Quire boundaries are STRUCTURAL DISCONTINUITIES: 1.67x vocabulary drop, 41% section/language changes at boundaries (QLA, Tier 2) |

### B-Prefix Functional Grammar (371-374)
| # | Constraint |
|---|------------|
| 371 | Prefixes have POSITIONAL GRAMMAR: line-initial specialists (so 6.3x, ych 7.0x, pch 5.2x), line-final specialists (lo 3.7x, al 2.7x, da 1.8x), mid-line preference (ch 0.15x, op 0.07x initial); enrichment range 0.07x-7.0x (BPF, Tier 2) |
| 372 | Prefixes split by KERNEL CONTACT: KERNEL-HEAVY (ch, sh, ok, lk, lch, yk, ke = 100% contain k/h/e), KERNEL-LIGHT (da 4.9%, sa 3.4%); dichotomy indicates two operational modes (BPF, Tier 2) |
| 373 | Prefixes have LINK AFFINITY patterns: LINK-ATTRACTED (al 2.48x, ol 1.82x, da 1.66x near LINK), LINK-AVOIDING (qo 0.65x, lch 0.67x, op 0.59x); prefixes participate in waiting/intervention split (BPF, Tier 2) |
| 374 | Prefixes have SECTION PREFERENCES: chi2=2369 (p=0); lk is 81% Section S; yk is 36% Section H; prefixes constrain which sections they appear in (BPF, Tier 2) |

### B-Suffix Functional Grammar (375-378)
| # | Constraint |
|---|------------|
| 375 | Suffixes have POSITIONAL GRAMMAR: extreme line-final specialists (-am 7.7x, -om 8.7x, -oly 4.6x, -y 2.3x); line-initial (-or 1.8x, -ol 1.6x); -am/-om are 80-90% line-final (BSF, Tier 2) |
| 376 | Suffixes split by KERNEL CONTACT: KERNEL-HEAVY (-edy 91%, -ey 95%, -dy 83%), KERNEL-LIGHT (-in 6%, -l 12%, -r 17%); mirrors prefix dichotomy (BSF, Tier 2) |
| 377 | KERNEL-LIGHT suffixes are LINK-ATTRACTED: -l (2.78x), -in (2.30x), -r (2.16x) near LINK; KERNEL-HEAVY suffixes avoid LINK (-edy 0.59x); waiting-phase markers (BSF, Tier 2) |
| 378 | Prefix-suffix combinations are CONSTRAINED: chi2=7053 (p=0); da+-aiin=30%, da+-edy=1%; sh+-edy=28%; prefixes select compatible suffixes (BSF, Tier 2) |

### Morphological Stability (379-381)
| # | Constraint |
|---|------------|
| 379 | PREFIX/SUFFIX VOCABULARY varies by folio/section: prefix CV=0.50, suffix CV=0.62; section chi2=876 (p≈0); different programs use different instruction mixes (MSTAB, Tier 2) |
| 380 | PREFIX/SUFFIX FUNCTION is INVARIANT: ch/sh are 100% kernel-heavy in ALL folios; functional roles are grammar-level constants even when vocabulary selection varies (MSTAB, Tier 2) |
| 381 | INSTRUCTION CONCENTRATION: 28 prefix+suffix combinations cover 50% of tokens, 87 cover 80%, from 394 total; compositional system with concentrated core and long tail (MSTAB, Tier 2) |
| 382 | MORPHOLOGY ENCODES CONTROL PHASE: kernel-light prefix+suffix (da, -in/-l/-r) = MONITORING phase (LINK-adjacent); kernel-heavy prefix+suffix (ch/sh, -edy/-ey) = INTERVENTION phase (LINK-distant); prefix-suffix constraints enforce phase coherence; each line follows ENTRY→MONITORING→LINK→INTERVENTION→EXIT structure; **extends to AZC** (same dichotomies, same LINK affinities) (MSTAB, Tier 2) |
| 383 | GLOBAL MORPHOLOGICAL TYPE SYSTEM: Prefixes encode functional type (INTERVENTION vs MONITORING) globally across A, B, and AZC; ch/sh/ok=100% kernel contact in ALL systems, da/sa<5% in ALL systems; LINK affinity patterns identical (da/al attracted, qo/ok avoiding); type system is grammar-independent (A has no sequential grammar but same types); B instantiates types in sequential programs, A instantiates types in non-sequential registry; explains vocabulary sharing without semantic transfer (A-ARCH, Tier 2) |
| 383a | SYSTEM-SPECIFIC REALIZATION OF GLOBAL TYPES: While the global type system (including substitution classes ch/sh and ok/ot) is shared across A, B, and AZC, positional and organizational realization is system-specific. In B: substitution is strongly section-conditioned and mutually exclusive (0.65x), DA functions as infrastructural boundary marker. In AZC: substitution valid but less symmetric, boundary/infrastructure roles shift to ok/ot (38%/27% line-initial vs DA 15%); consistent with AZC's distinct positional grammar. Infrastructure is role-based, not token-fixed. (SISTER, Tier 2) |
| 384 | NO ENTRY-LEVEL A-B COUPLING: Although A and B share global vocabulary and type system, there is NO entry-level or folio-level cross-reference; all B programs draw from identical A-derived vocabulary pool (Jaccard 0.998 between all B folios); 215 one-to-one tokens scatter across 207 unique A-B pairs (no repeated pairings beyond noise); rare tokens are rare globally, not relationally; A does NOT function as lookup catalog for B programs; coupling occurs ONLY at global type-system level (A-ARCH, Tier 2) |
| 385 | STRUCTURAL GRADIENT IN CURRIER A: Currier A exhibits measurable internal ordering; higher-frequency tokens appear earlier in sequence (rho=-0.44); later folios contain longer tokens with fewer recognizable morphological components (length rho=+0.35, components rho=-0.29); section-level diversity increases H (0.311) -> P (0.440) -> T (0.623); gradient reflects systematic structural change within registry, independent of execution grammar or semantic interpretation (A-ARCH, Tier 2) |

### Transition Enrichment and Higher-Order Sequences (386-390)
| # | Constraint |
|---|------------|
| 386 | TRANSITION SUPPRESSION: Beyond 17 forbidden transitions, 8 transitions significantly suppressed (<0.5x expected); all 8 involve KERNEL-HEAVY tokens (chedy, shedy, aiin, ar); suppression within INTERVENTION cluster, not cross-phase; supports phase-internal hazard avoidance (TRANS, Tier 2) |
| 387 | PREFIX TRANSITION ASYMMETRY: sh->qo enriched (2.04x), da/sa/al->qo suppressed (0.23-0.43x); INTERVENTION prefixes feed into qo; MONITORING prefixes avoid qo; establishes qo as phase-transition hub (TRANS, Tier 2) |
| 388 | SELF-TRANSITION ENRICHMENT: Self-transitions 3.76x enriched on average; qokeedy->qokeedy (4.7x), qokedy->qokedy (4.4x); self-repetition is preferred control strategy indicating stabilization or continuation (TRANS, Tier 2) |
| 389 | BIGRAM-DOMINANT LOCAL DETERMINISM: Grammar almost fully determined by 2-token context; H(X\|prev 2)=0.41 bits (95.9% reduction from unconditioned); once 2 prior tokens known, next token nearly predetermined; extreme for any known notation system (HOS, Tier 2) |
| 390 | NO RECURRING N-GRAMS: 99.6% of trigrams are hapax; 100% of 5-grams+ unique; zero universal trigrams across >=30% of folios; grammar generates sequences locally, not from memorized templates (HOS, Tier 2) |

### Grammar Architecture (391-393)
| # | Constraint |
|---|------------|
| 391 | TIME-REVERSAL SYMMETRY: Role-level transitions in Currier B are statistically time-reversal invariant; H(X\|past k) = H(X\|future k) for k=1,2,3 (ratio 1.00); grammar encodes bidirectional adjacency constraints rather than intrinsic causal direction; procedural direction is supplied by operator, not grammar (SYM, Tier 2) |
| 392 | ROLE-LEVEL CAPACITY CLOSURE: At role abstraction level (6 classes), 35/36 possible transitions observed (97.2%); only HIGH_IMPACT->HIGH_IMPACT is zero-count; no hidden role-level prohibitions beyond documented hazards; structural control imposed through preference and local determinism, not expanded illegality (CAP, Tier 2) |
| 393 | FLAT ROLE-LEVEL TOPOLOGY: Role-transition graph is single strongly-connected component with diameter 1, transitivity 1.0, zero articulation points; no global chokepoints or hierarchical role gating; global structure arises from fine-grain local constraints, not role-level architecture (TOPO, Tier 2) |

### Regime-Role Differentiation (394-396)
| # | Constraint |
|---|------------|
| 394 | INTENSITY-ROLE DIFFERENTIATION: Aggressive programs use 1.34x more ENERGY_OPERATOR (41.4% vs 31.0%, p=0.012) and 1.24x more CORE_CONTROL (24.3% vs 19.7%, p=0.033); conservative programs use 2.0x more HIGH_IMPACT (14.9% vs 7.5%, p=0.0004); role composition varies systematically by operational intensity (RRD, Tier 2) |
| 395 | DUAL CONTROL STRATEGY: Aggressive = rapid small adjustments (kernel-heavy, less waiting); Conservative = bigger moves with more waiting (HIGH_IMPACT heavy, more LINK); confirms intensity regimes are categorical operational modes, not just parametric variation (RRD, Tier 2) |
| 396 | AUXILIARY INVARIANCE: AUXILIARY role is invariant across intensity regimes (8.5-9.0%, p=0.99); infrastructure tokens remain constant while intervention tokens vary; grammar skeleton is fixed, intervention strategy is variable (RRD, Tier 2) |

### Hazard Avoidance Microstructure (397-399)
| # | Constraint |
|---|------------|
| 397 | QO-PREFIX ESCAPE ROUTE: qo- prefixed tokens are the universal escape from hazard source positions; after hazard sources, qo- tokens appear 25-47% of the time (qokeey, qokain, qokedy, qol most frequent); qo- serves as the primary "safe transition" prefix for redirecting away from forbidden targets (HAV, Tier 2) |
| 398 | ESCAPE ROLE STRATIFICATION: After hazard source tokens, ENERGY_OPERATOR is primary escape destination (40-67% depending on source), CORE_CONTROL is secondary (22-32%); grammar redirects hazard sources toward stability-maintaining roles; HIGH_IMPACT is 61.8% escape after 'or' only (HAV, Tier 2) |
| 399 | SAFE PRECEDENCE PATTERN: ENERGY_OPERATOR and CORE_CONTROL safely precede hazard targets (33-67%); hazard targets are approached from stable states, not from other hazardous positions; grammar creates "safe approach corridors" to dangerous tokens (HAV, Tier 2) |

### Boundary Sensitivity (400)
| # | Constraint |
|---|------------|
| 400 | BOUNDARY HAZARD DEPLETION: Hazard tokens (sources and targets of forbidden transitions) are 5-7x depleted at line-initial positions (0.20x sources, 0.15x targets, both p=0.0000) and completely absent at folio-initial positions (0/82 folios); line-final positions show moderate depletion (0.65x); grammar creates "safe zones" at structural boundaries for operator resumption (BSA, Tier 2) |

### Role Motifs (401-402)
| # | Constraint |
|---|------------|
| 401 | SELF-TRANSITION DOMINANCE: ENERGY_OPERATOR has 45.6% self-transition rate (nearly half stay in same role); CORE_CONTROL has 25.0%; grammar skeleton is dominated by role persistence rather than role switching; consistent with stability-maintaining control where small adjustments cluster (LRM, Tier 2) |
| 402 | HIGH_IMPACT CLUSTERING: HIGH_IMPACT → HIGH_IMPACT is the only enriched role bigram (1.73x expected); big interventions cluster together rather than being evenly distributed; no depleted role bigrams exist (role topology is flat with selective clustering) (LRM, Tier 2) |

### Program Archetypes (403)
| # | Constraint |
|---|------------|
| 403 | PROGRAM ARCHETYPE CONTINUUM: 83 B programs form a continuum (silhouette 0.14-0.19) with 5 interpretable archetypes: (1) Conservative Waiting (10 folios, LINK 0.50, HIGH_IMPACT 21.7%), (2) Aggressive Intervention (10 folios, CORE_CONTROL 26.3%), (3) Balanced Standard (20 folios), (4) FREQUENT_OPERATOR-Dominated (16 folios, 26.7%), (5) Energy-Intensive (26 folios, ENERGY_OPERATOR 47.2%); programs are not discrete categories but positions on a multidimensional operational manifold (PAS, Tier 2) |

### HT Closure Tests (404-406)
| # | Constraint |
|---|------------|
| 404 | HT TERMINAL INDEPENDENCE: HT density does not predict terminal grammar state (chi2=1.41, p=0.92; rho=0.013, p=0.90); high-HT and low-HT folios have statistically indistinguishable outcome distributions; HT has no influence on program completion (HTC, Tier 2) |
| 405 | HT CAUSAL DECOUPLING: HT presence does not alter subsequent grammar token probabilities beyond phase correlation; chi2 significant (p=0.0000) but effect size negligible (Cramer's V=0.10); HT has no advisory or predictive role in grammar execution (HTC, Tier 2) |
| 406 | HT GENERATIVE STRUCTURE: HT types follow Zipf distribution (exponent 0.892, R²=0.92) with 67.5% hapax rate; consistent with productive compositional system, not random noise or memorized templates; supports practice/exploration interpretation (HTC, Tier 2) |

### Sister Pair Analysis (407-410)
| # | Constraint |
|---|------------|
| 407 | DA INFRASTRUCTURE CLASSIFICATION: DA prefix class is INFRASTRUCTURE, not a material family; extreme suffix bias (-in at 34.4% vs 1.1% for others), extreme line-boundary enrichment (20.9% line-initial vs 2-8% for others), low internal diversity (top 3 tokens = 42.6% of class), alignment with infrastructure token `daiin`; DA functions as record articulation, not material classification (SISTER, Tier 2) |
| 408 | SISTER PAIR EQUIVALENCE CLASSES: Prefix families ch-sh and ok-ot form EQUIVALENCE CLASSES; Jaccard similarity of MIDDLE vocabulary shows ch-sh (J=0.23) and ok-ot (J=0.24) are 3-4x more similar than cross-pair baselines (J=0.05-0.08); CT and DA isolated (J<0.04); prefix space partitions into 2 sister pairs, 2 isolates (da, ct), 2 bridging families (qo, ol) (SISTER, Tier 2) |
| 409 | SISTER PAIR MUTUAL EXCLUSION: Sister pairs are SUBSTITUTABLE but MUTUALLY EXCLUSIVE in Currier B; ch-sh bigrams suppressed 0.62-0.65x; ok-ot bigrams suppressed 0.53-0.64x; despite avoiding sequence, sister pairs share predecessor contexts (336 shared), accept identical suffixes (195 minimal pairs), substitute in trigram frames (119 contexts); same grammatical slot, alternative choices (SISTER, Tier 2) |
| 410 | SISTER PAIR SECTION CONDITIONING: Sister pair choice is SECTION-CONDITIONED; Section H strongly prefers ch-forms (cheky 85%, chckhy 92%, checkhy 78%); Section B balanced or sh-leaning (42-57% ch); earlier quires (E, F, G) prefer ch-forms; Quire M balanced; conditioning at section/quire level, not folio level (71% mixed folios) (SISTER, Tier 2) |
| 411 | DELIBERATE OVER-SPECIFICATION: The Currier B grammar contains substantially more instruction classes (49) than minimally required to preserve transition entropy and hazard topology; using loss-bounded reduction (<=1% entropy increase per merge), grammar compresses from 49 to 29 classes (~40% reduction) without structural loss; ENERGY_OPERATOR classes collapse (11->2), AUXILIARY classes collapse (8->1), but CORE_CONTROL tokens (daiin, ol) refuse to merge; indicates intentional vocabulary diversification for human-facing mnemonic, ergonomic, or readability considerations rather than minimal encoding (SITD, Tier 2) |

### Illustration Independence (137-140)
| # | Constraint |
|---|------------|
| 137 | Swap invariance confirmed (p=1.0) |
| 138 | Illustrations do not constrain execution |
| 139 | Grammar recovered from text-only |
| 140 | Illustrations are epiphenomenal |

### Family Structure (126-129, 141-144)
| # | Constraint |
|---|------------|
| 126 | 0 contradictions across 8 families |
| 129 | Family differences = coverage artifacts |
| 141 | Cross-family transplant = ZERO degradation |
| 144 | Families are emergent regularities |

---

## Historical Phase Summary

| Phase | Finding | Status |
|-------|---------|--------|
| 7 | Formal semantic model | 95.1% parse coverage |
| 9-11 | Domain discrimination | Pharmacology 0/3, Alchemy 2/3 |
| 12 | Tradition fingerprinting | T3 PRIVATE SCHOOL |
| 13-14 | Executability | MONOSTATE (57.8% terminal STATE-C; revised by SEL-F) |
| 15 | Hub core structure | 10 primitives, k/h/e core |
| 16 | Process alignment | REFLUX DISTILLATION (86%) |
| 17 | Kernel semantics | Three-point control |
| 18 | Hazard topology | 5 failure classes |
| 19 | Identifier detection | PURE_OPERATIONAL |
| 20 | Normalization | 49 classes, ASYMPTOTE |
| 21-22 | Enumeration | 83 folios, 75,248 instructions |
| 23 | Regime boundaries | f57r = RESTART_PROTOCOL |
| X | Adversarial audit | 6/8 survived |
| X.5 | DSL discriminator | Language REJECTED |
| CCF | Circular folios | VISUAL_BUNDLING |
| ILL | Illustration independence | EPIPHENOMENAL |
| FSS | Family syntax | EMERGENT |
| PMS | Prefix material selection | FALSIFIED |
| PPA | Physics plausibility | 7/7 PASS |
| L1-L4 | Process dynamics | COHERENT |
| EPM | Process mapping | 2 STRONG, 4 MODERATE |
| APF | Process comparison | PF-C better (0.81 vs 0.47) |
| HTO | Ordering analysis | 2/5 PASS |
| CDCE | Engineering comparison | HIGH: reflux/conditioning |
| PIA | Product isolation | Aromatic Waters 90.5% |
| PIAA | Plant alignment | 86.7% perfumery |
| PPC | Program-plant correlation | NO correlation |
| FMR | Failure modes | 5 classes mapped |
| UTC | Uncategorized tokens | Section-local, non-executable |
| MCS | Coordinate system | 80.7% section-exclusive |
| NESS | Non-executable systems | Single unified layer |
| PCI | Purpose inference | Closed-loop control only |
| HOT | Ordinal hierarchy | FALSIFIED (2/5) |
| HLL-2 | Language-likeness | FALSIFIED (2/5) |
| OLF | Olfactory craft | 5/5 plausible |
| IMD | Micro-differentiation | CF-1/CF-2 STRONG_SIGNAL |
| PCISO | Process isomorphism | 3 survive |
| PSP | Product plausibility | 5 families |
| PCC | Product convergence | Both survive |
| PCIP | Plant intersection | No new constraint |
| OPS-1 to OPS-7 | Operator doctrine | CLOSED |
| EXT-1 to EXT-7 | External comparison | Goldsmith workshops survive |
| SEL-A to SEL-E | Self-evaluation | See below |
| SEL-F | Contradiction resolution | OPS-R RESOLVED; 57.8% STATE-C (not 100%); COMPLETION GRADIENT confirmed; 5 new constraints (323-327) |
| SID-01 to SID-05 | Residue investigation | CLOSED |
| CAud | Currier A audit | DISJOINT |
| CAud-G | A grammar derivation | NO GRAMMAR |
| CAS | A schema | CATEGORICAL REGISTRY |
| CAS-DS | A deep structure | INFRASTRUCTURE_REUSE |
| SP | Structural primitives | MINIMAL (2 tokens) |
| CAS-MULT | Multiplicity encoding | 64.1% repeating blocks |
| CAS-DEEP | Deep structure analysis | 100% section-isolated, marker-stratified |
| CAS-DEEP-V | Validation tests | Token order non-random, low mutation, Simpson's paradox |
| CAS-CAT | Marker token catalog | 1,123 tokens, 85 core, 8 classes documented |
| CAS-SCAN | Non-block entry scan | TWO content types: block=exclusive, non-block=mixed (90.5% multi-class) |
| CAS-MORPH | Compositional morphology | 897 PREFIX×MIDDLE×SUFFIX combinations; identity space from small codebook |
| CAS-PHYS | Physical folio separation | 0 shared folios between A and B; manuscript-level designed separation |
| EXT-8 | Full morphology analysis | MATERIAL_CLASSIFICATION_SIGNATURE; 3-axis hierarchy (family->type-specific->universal form) |
| EXT-9 | Cross-system mapping | CO-DESIGNED_COMPLEMENTARY_MODE-PREFERRING; shared alphabet, different grammar |
| EXT-9B | Ratio hypothesis + Articulator layer | RATIO FALSIFIED; ARTICULATOR LAYER confirmed (~20% optional, 100% removable, systematic) |
| CAS-POST | Post-closure comparative analysis | COMPLETE; Section archetypes identified; MIDDLE=primary discriminator; Articulators=ZERO identity contribution |
| B-MORPH | B compositional morphology | L-compounds (lch-, lk-, lsh-) identified as B-specific grammatical operators |
| CAS-XREF | Cross-reference structure | H-section dominates B (91.6%); P rare (8.4%); T absent (0%); sections map to procedure applicability |
| AZC | Astronomical/Zodiac/Cosmological | HYBRID (7.7% of corpus); bridges A and B with 60.5% shared vocabulary; distinct line structure |
| AZC-PROBE | AZC unique vocabulary probe | LABELING signature (98% section-exclusive, 37% line-boundary, 65.9% hapax); NOT executing/indexing |
| AZC-PLACEMENT | Placement code analysis | Finite placement classes (C, P, R1-R3, S-S2, Y); orthogonal to morphology; formal placement-coding axis |
| AZC-AXIS | Axis connectivity tests | MULTI-AXIS INTERDEPENDENT SYSTEM; 7/7 tests show signal; placement constrains morphology, repetition, boundary, section |
| AZC-AXIS-A | Phase A: Axis interaction | Position constrains LEGALITY not PREDICTION; z=13 forbidden pairs; grammar collapse in 7 placements |
| AZC-AXIS-A2 | A2-DEEP: Forbidden structure | Global illegality + local exceptions; 9/18 placement-locked operators |
| AZC-AXIS-ROT | Rotation invariance | 32.3pp binding drop = PHASE-LOCKED; hybrid architecture (C topological, P/R/S positional) |
| AZC-AXIS-B | Phase B-MIN: Diagram alignment | CONFIRMED; V=0.507 folio-specific; zodiac template reuse; S2<S1 ordering |
| AZC-AXIS-CD | Cycle Discriminator (Tests 4-5) | HYBRID: V_A=0.152, V_B=0.139; SEASON-GATED WORKFLOW; vocabulary isolated, placements clustered |
| ROBUST | Grammar Robustness | 4/4 tests PASS: noise injection (graceful), ablation (distributed), cross-validation (stable), minimality (confirmed weakened) |
| KERNEL | Kernel Ordering Constraints | 2 Tier 2 constraints: h->k SUPPRESSED, e->e->e dominates (97.2%); CLOSED (3 tests, bounded scope) |
| LINK | LINK Temporal State-Space | 1 Tier 2 constraint: LINK is section-conditioned (B=1.45x), NOT kernel-conditioned (z=0.05); CLOSED |
| AB_INTEGRATION | A-B Integration Mechanics | 2 Tier 2 constraints: 69.8% vocabulary integration; HYBRID access (sequential + semantic); CLOSED |
| MIXED | Mixed-Marker Entry Analysis | 2 Tier 2 constraints: 89.2% mixed-marker lines; markers mix independently; exclusive lines are SPECIALIZED; CLOSED |
| CYCLE | Cycle Semantics Analysis | 0 constraints (HARD STOP): 3-cycles and 4-cycles NOT DISTINCT (100% token overlap, same kernel composition); CLOSED |
| PHYS | Physics Plausibility Stress Test | 2 Tier 2 constraints: e-class dominance (36%), LINK-escalation complementarity (0.605x); stability-dominated system; CLOSED |
| HTD | Human-Track Domain Analysis | 2 Tier 2 constraints: HT-program stratification (p < 0.0001), HT-LINK decoupling (ρ = 0.01); single-domain with behavioral stratification; CLOSED |
| AAZ | A-AZC Coordination Stress Test | 2 Tier 2 constraints: A-vocab 2.2x broader than AZC-only (persistence); HT-A inverse coupling (rho=-0.367); A-registry persists independently of legality; HT tracks cognitive spare capacity; STEWARDSHIP model supported; CLOSED |
| CAS-FOLIO | Currier A Folio Coherence | 2 Tier 2 constraints: No folio-level thematic coherence (within=between, p=0.997); SEQUENTIAL COHERENCE exists (adjacent 1.31x more similar, p<0.000001); CLOSED |
| MORPH-CLOSE | Final Morphology Closure | 4 Tier 2 constraints: Extended cluster prefixes (pch, tch, kch, dch, fch, rch, sch); HT+B hybrids explained (12.47%); 92.66% explained, 0.62% TRUE ORPHAN; CLOSED |
| FG | Folio Gap Analysis | 4 Tier 2 constraints: State continuity BETTER than random (d=-0.20); HT orientation intact (2.69x enrichment); 75.9% known prefixes; section symmetry preserved; NO STRUCTURAL EVIDENCE of post-composition removal; CLOSED |
| LINE | Line-Level Control Architecture | 4 Tier 2 constraints: Lines 3.3x more regular than random (z=-3.60); boundary tokens identified (3-31x enrichment); LINK suppressed at boundaries; grammar LINE-INVARIANT; LINES ARE FORMAL CONTROL BLOCKS; CLOSED |
| BVP | B-Folio Vocabulary Patterns | 4 Tier 2 constraints: Adjacent sharing 1.30x (d=0.76); regime fingerprints 1.29x; vocabulary independent of stability/LINK; hub-peripheral structure (41 core, 3368 unique); B FOLIOS VOCABULARILY STRUCTURED; CLOSED |
| BPF | B-Prefix Functional Grammar | 4 Tier 2 constraints: Positional grammar (0.07x-7.0x enrichment); kernel dichotomy (100% vs <5%); LINK affinity patterns; section preferences (chi2=2369); PREFIX FUNCTION CHARACTERIZED; CLOSED |
| BSF | B-Suffix Functional Grammar | 4 Tier 2 constraints: Positional grammar (-am/-om 80-90% line-final); kernel dichotomy mirrors prefix; KERNEL-LIGHT suffixes LINK-attracted (2.2-2.8x); prefix-suffix constrained (chi2=7053); SUFFIX FUNCTION CHARACTERIZED; CLOSED |
| MSTAB | Morphological Stability | 2 Tier 2 constraints: Vocabulary varies by folio/section (CV=0.50-0.62); Function is INVARIANT (ch/sh 100% kernel-heavy in ALL folios); VOCABULARY VARIES, FUNCTION STABLE; CLOSED |
| LDF | LINK Distribution within Folios | 2 Tier 2 constraints: LINK spatially uniform (3 NULL tests); LINK marks grammar state transitions (HIGH_IMPACT 2.70x after LINK); LINK IS BOUNDARY BETWEEN MONITORING AND INTERVENTION; CLOSED |
| QLA | Quire-Level Analysis | 4 Tier 2 constraints: Section-quire alignment 4.3x; regime clustering 2.20x; vocabulary continuity 1.69x; boundary discontinuities 1.67x; QUIRES ARE ORGANIZATIONAL UNITS; CLOSED |
| A-ARCH | A-B-AZC Architecture | 3 Tier 2 constraints: (383) GLOBAL TYPE SYSTEM across A/B/AZC; (384) NO ENTRY-LEVEL COUPLING (Jaccard 0.998); (385) STRUCTURAL GRADIENT in A (freq vs first-occurrence rho=-0.44, diversity H->P->T); A=organized registry, B=programs using global pool; CLOSED |
| TRANS | Transition Enrichment & Higher-Order Sequences | 5 Tier 2 constraints: (386) 8 suppressed transitions in KERNEL-HEAVY cluster; (387) qo as phase-transition hub; (388) self-transitions 3.76x enriched; (389) BIGRAM-DOMINANT (H=0.41 bits with 2-token context); (390) 99.6% trigrams hapax; CLOSED |
| SYM/CAP/TOPO | Grammar Architecture Probes | 3 Tier 2 constraints: (391) TIME-REVERSAL SYMMETRY (H ratio=1.00); (392) ROLE-LEVEL CAPACITY (97.2% observed); (393) FLAT TOPOLOGY (diameter=1, no bottlenecks); grammar encodes adjacency constraints, operator supplies direction; CLOSED |
| RRD | Regime-Role Differentiation | 3 Tier 2 constraints: (394) Intensity-role differentiation (AGGRESSIVE 1.34x ENERGY_OP, CONSERVATIVE 2.0x HIGH_IMPACT); (395) Dual control strategy (rapid small vs big+wait); (396) AUXILIARY invariant (p=0.99); intensity regimes are CATEGORICAL operational modes; CLOSED |
| HAV | Hazard Avoidance Microstructure | 3 Tier 2 constraints: (397) qo-prefix universal escape route (25-47%); (398) escape role stratification (ENERGY_OPERATOR 40-67% primary); (399) safe precedence pattern (stable→hazard approach); grammar has POSITIVE avoidance guidance, not just prohibitions; CLOSED |
| BSA | Boundary Sensitivity Audit | 1 Tier 2 constraint: (400) hazard tokens 5-7x depleted at line-initial (0.20x/0.15x), ZERO at folio-initial (0/82); grammar creates "safe zones" at structural boundaries for operator resumption; CLOSED |
| LRM | Local Role Motifs | 2 Tier 2 constraints: (401) self-transition dominance (ENERGY_OP 45.6%, CORE 25.0%); (402) HIGH_IMPACT clustering only (1.73x); role topology flat with selective clustering; CLOSED |
| PAS | Program Archetype Synthesis | 1 Tier 2 constraint: (403) programs form continuum (silhouette 0.14-0.19) with 5 archetypes; not discrete categories but positions on multidimensional operational manifold; CLOSED |
| HTC | HT Closure Tests | 3 Tier 2 constraints: (404) terminal independence (p=0.92); (405) causal decoupling (V=0.10); (406) generative structure (Zipf=0.89, 67.5% hapax); HT is CONFIRMED NON-OPERATIONAL; interpretation permanently Tier 3-4; CLOSED |
| SISTER | Sister Pair Analysis | 5 Tier 2 constraints: (407) DA is infrastructure in A/B; (408) ch-sh/ok-ot form equivalence classes (J=0.23/0.24); (409) sister pairs mutually exclusive but substitutable; (410) choice is section-conditioned in B; (383a) system-specific realization — AZC shifts boundary roles to ok/ot; infrastructure is role-based, not token-fixed; CLOSED |
| SITD | Shot in the Dark Exploratory | 1 Tier 2 constraint: (411) Grammar is deliberately over-specified (~40% reducible to 29 classes with <1% entropy cost); CORE_CONTROL tokens refuse to merge; vocabulary diversity serves human ergonomics. Tier 4 finding: forgiving/brittle axis (5σ spread) partially orthogonal to aggressive/conservative; CLOSED |

---

## Adversarial Audit Summary

| Attack | Result |
|--------|--------|
| Kernel Collapse | SURVIVES |
| Cycle Illusion | WEAKENED |
| Grammar Minimality | WEAKENED |
| Random Baseline | SURVIVES |
| Folio Independence | SURVIVES |
| Grammar Collapse | SURVIVES |
| DSL Discriminator | SURVIVES |
| Family Syntax | SURVIVES |

**Overall: 6/8 attacks failed to falsify model**

---

## Key Files

### Data
- `data/transcriptions/interlinear_full_words.txt` — Canonical source (TSV, EVA tokens)
- `data/transcriptions/recovery_patches.tsv` — Damaged token recovery proposals (see below)

### Damaged Token Recovery

The canonical transcription contains ~1,400 tokens with `*` characters (EVA notation for uncertain/damaged glyphs). Using our structural knowledge, ~33% are recoverable with high confidence.

**Patch file format:**
```
folio | line | original | recovered | confidence | candidates
f1r   | 3    | d*       | dy        | CERTAIN    | dy
f2v   | 5    | ar*      | ary       | HIGH       | ary;arl;aro
```

**Confidence tiers:**
- `CERTAIN` — Unique match, 100% confidence
- `HIGH` — 2-5 candidates, top candidate >80% frequency share
- `AMBIGUOUS` — >5 candidates, documented but not recommended

**When to USE recovery patches:**
- Frequency analysis (reduces noise from damaged tokens)
- Grammar coverage testing (damaged tokens appear as false residue)
- Token classification (damaged tokens pollute category counts)

**When NOT to use recovery patches:**
- Paleographic analysis (need original glyph data)
- Transcription validation (comparing against manuscript images)
- Any analysis where the uncertainty itself is meaningful
- Publishing results (disclose whether patches were applied)

**Usage in scripts:**
```python
from lib.transcription import load_transcription

# Default: original data, no patches
tokens = load_transcription()

# With recovery: apply high-confidence patches
tokens = load_transcription(apply_recovery=True, min_confidence='HIGH')

# Maximum recovery: apply all patches including ambiguous
tokens = load_transcription(apply_recovery=True, min_confidence='AMBIGUOUS')
```

**Always document** which mode was used when reporting results.

### Results
- `results/canonical_grammar.json` — 49-class grammar
- `results/full_recipe_atlas.txt` — 75,248 instructions
- `results/control_signatures.json` — Kernel definitions

### Phase Reports
- `phases/OPS1-7_*/` — Operator doctrine
- `phases/EXT1-7_*/` — External comparisons
- `phases/SEL_A_claim_inventory/` — SEL audit suite
- `phases/SID01-05_*/` — Residue investigation
- `phases/CAud_currier_a_audit/` — Currier A disjunction
- `phases/CAS_*/` — A schema analysis
- `phases/CAS_XREF_cross_reference_structure/` — A-B cross-reference
- `phases/SP_structural_primitives/` — Structural primitives
- `phases/AZC_AXIS_axis_connectivity/` — AZC axis connectivity + diagram alignment (STRUCTURALLY COMPLETE)
- `phases/FG_folio_gap_analysis/` — Folio gap analysis (NO STRUCTURAL EVIDENCE of post-composition removal)
- `phases/LINE_line_level_analysis/` — Line-level control architecture (LINES ARE FORMAL CONTROL BLOCKS)
- `phases/BSA_boundary_sensitivity_audit/` — Boundary sensitivity (safe zones at boundaries)
- `phases/LRM_local_role_motifs/` — Local role motifs (self-transition dominance)
- `phases/PAS_program_archetype_synthesis/` — Program archetypes (5-archetype continuum)
- `phases/HTC_ht_closure_tests/` — HT closure tests (HT confirmed non-operational)

### Archive
- `archive/CLAUDE_full_2026-01-06.md` — Full verbose documentation backup
- `archive/scripts/` — Research scripts (phase analysis, utilities)
- `archive/reports/` — Generated reports and audit results

---

## File Organization

**Rule:** Keep the main directory clean. New research scripts and reports go to archive.

| File Type | Location |
|-----------|----------|
| Phase analysis scripts | `archive/scripts/` |
| Utility scripts | `archive/scripts/` |
| Generated reports (.txt, .json) | `archive/reports/` |
| Phase documentation (.md) | `phases/<PHASE_NAME>/` |
| Canonical data | `data/transcriptions/` |
| Frozen outputs | `results/` |

**Main directory should contain only:**
- `CLAUDE.md` (this file)
- `README.md`
- Configuration files (.gitignore, etc.)
- Core library code in `lib/`

---

## Methodological Warnings

**RECURRENT BUG: Prefix matching ≠ Token matching**

The 17 forbidden transitions are about **specific token pairs or token-class pairs**, NOT blanket prefix-to-prefix rules.

❌ WRONG: "Any token starting with `ol-` followed by any token starting with `qo-` is forbidden"
✅ RIGHT: "Specific transitions between grammar classes are forbidden in specific contexts"

This confusion has caused false results multiple times:
- Testing `olsheol → qokchy` as a "forbidden transition" (it's not — these are different tokens)
- Finding thousands of "violations" that aren't violations
- Misclassifying token categories based on prefix alone

**When writing new analysis scripts:**
1. Check if you're matching PREFIXES or specific TOKENS
2. Verify against known canonical grammar (479 types in B)
3. Test on small samples before drawing conclusions
4. If results seem too good or too bad, check parsing logic first

---

## What Cannot Be Recovered Internally

- Specific substances, materials, or products
- Natural language equivalents for any token
- Historical identity of author or school
- Precise dating or geographic origin
- Illustration meanings
- Physical apparatus construction details

---

*MODEL FROZEN. 411 constraints validated. ROBUST + KERNEL + LINK + AB_INTEGRATION + MIXED + CYCLE + PHYS + HTD + AAZ + CAS-FOLIO + HT-MORPH + HT-STATE + MORPH-CLOSE + FG + LINE + BVP + BPF + BSF + MSTAB + LDF + QLA + A-ARCH + TRANS + SYM/CAP/TOPO + RRD + HAV + BSA + LRM + PAS + HTC + SISTER + SITD phases COMPLETE.*

*Morphology closure (2026-01-07): 92.66% explained, 0.62% irreducible residue. No unaccounted formal systems remain.*

*v1.8 (2026-01-08): Added SITD phase (constraint 411). Grammar deliberately over-specified (~40% reducible); vocabulary diversity serves human ergonomics. Tier 4: forgiving/brittle program axis identified.*
