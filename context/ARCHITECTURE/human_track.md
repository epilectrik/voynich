# Human Track Layer

> **Structural Contract:** [../STRUCTURAL_CONTRACTS/humanTrack.htsc.yaml](../STRUCTURAL_CONTRACTS/humanTrack.htsc.yaml) (AUTHORITATIVE — 17 guarantees, 10 invariants, 68 owned constraints)
>
> **Context Summary:** [../CLAIMS/HT_CONTEXT_SUMMARY.md](../CLAIMS/HT_CONTEXT_SUMMARY.md) (context-sufficient)
>
> **Explainer:** [HT_EXPLAINER.md](HT_EXPLAINER.md) - What HT is (and is not)

**Status:** CLOSED | **Tier:** 2 (structure), 3-4 (interpretation)

> **Status note (v7.25, 2026-09-28):** `SYSTEM/STATUS_BRIEF.md` and the generated `CONSTRAINT_TABLE.txt` win on
> conflict. Every "hazard" statement here is measured against the 17 forbidden transitions, a layer now withdrawn
> (C2081; C783 demoted; C2060; STATUS_BRIEF §3). "Waiting" profiles and LINK rest on LINK, now a morphological artifact of
> "ol" (C1174; true density 13.2%, C609). Sections resting on these are annotated. The later compound-specification
> reading (C935) is summarised in [HT_EXPLAINER.md](HT_EXPLAINER.md).

---

## Definition

The **Human Track (HT)** consists of tokens NOT in the 479-type canonical Currier B grammar vocabulary. This is a **token list definition**—the grammar has exactly 479 specific token types; everything else is "uncategorized" or "residue."

| Metric | Value |
|--------|-------|
| Occurrences | ~40,000 (33.4% of corpus) — legacy figure from before the H-track filter; in Currier B, HT = UN = 7,042 occurrences, 4,421 types (C740, C566) |
| Unique types | ~11,000 (legacy figure) |
| Section-exclusive | 80.7% |
| Line-initial enrichment | 2.16x |

---

## Structural Properties (Tier 2)

### Hazard Avoidance

**[Withdrawn v7.24/7.25 — historical; see SYSTEM/STATUS_BRIEF.md §3]** "Hazard positions" are the 17 forbidden
transitions, withdrawn as a prohibition layer (C2081, superseding C957; C783 demoted; C2060 taxonomy imposed). C166,
C169 and C217 remain Tier 2 in the registry as measurements relative to those positions; the reading that writing
"stops when attention is demanded" rests on the withdrawn layer.

| Metric | Value | Constraint |
|--------|-------|------------|
| Hazard proximity | 4.84 vs 2.5 expected | C169 |
| Forbidden seam presence | 0/35 | C166 |
| True HT near hazards | 0 (vs 4,510 near random) | C217 |

HT tokens **completely avoid** hazard positions. When attention is demanded, writing **stops entirely**.

### Section Exclusivity

| Metric | Value | Constraint |
|--------|-------|------------|
| Section-exclusive | 80.7% | C167 |
| Single unified layer | YES | C168 |

HT forms a single layer with strong section-local patterns.

### Morphologically Distinct

HT tokens form a **third compositional notation system** with disjoint prefix vocabulary (C347):

| Component | HT System | A/B System | Overlap |
|-----------|-----------|------------|---------|
| Prefixes | yk-, op-, yt-, sa-, so-, ka-, dc-, pc- | ch-, qo-, sh-, da-, ok-, ot-, ct-, ol- | **ZERO** |
| Suffixes | -dy, -in, -ey, -ar, -hy | -aiin, -dy, -ey, -or | Partial |
| Coverage | 71.3% decomposable | 100% grammar (of its own vocabulary = 69.5% of B tokens, C124 as corrected) | — |

This is NOT scribal noise—it is a **formally distinct layer**.

---

## Non-Operational Status (Tier 2)

HT is **confirmed NON-OPERATIONAL** by three independent tests (C404-406):

| Test | Finding | Constraint |
|------|---------|------------|
| Terminal independence | HT doesn't predict outcome (p=0.92) | C404 |
| Causal decoupling | HT doesn't alter grammar flow (V=0.10) | C405 |
| Generative structure | Zipf distribution (0.89), 67.5% hapax | C406 |

**Removing all 40,000 HT tokens would not affect grammar coverage or hazard topology.** [hazard topology withdrawn — C2081; the token count is a legacy figure]

---

## Program Stratification (Tier 2)

HT density varies by program type (C341) [in the old model "waiting" meant LINK ("when to wait — LINK tokens", CORE/model_boundary.md); LINK is now read as a morphological artifact, not a waiting operator (C1174), so "waiting" is a gloss — the density gradient is the measurement]:

| Waiting Profile | HT Density |
|-----------------|------------|
| EXTREME | 15.9% |
| HIGH | 10.4% |
| MODERATE | 8.5% |
| LOW | 5.7% |

Kruskal-Wallis p < 0.0001. HT is a **program-level characteristic**, not a token-level response.

### HT-LINK Decoupling (C342)

HT density is **independent** of LINK density at folio level:
- Spearman ρ = 0.010, p = 0.93
- "More LINK = more random mark-making" hypothesis is **falsified**
- HT is not synchronized with LINK token positions

---

## Global Threading (Tier 2) - NEW

> **C450-C453 jointly establish HT as a manuscript-wide, codicologically clustered orientation layer with unified vocabulary and session-level continuity.**

HT threads through the entire manuscript as a **single unified notation layer**:

| Property | Finding | Constraint |
|----------|---------|------------|
| Quire clustering | H=47.20, p<0.0001, eta-sq=0.150 | C450 |
| System stratification | A (0.170) > AZC (0.162) > B (0.149) | C451 |
| Unified vocabulary | Jaccard >= 0.947 across all systems | C452 |
| Adjacency clustering | 1.69x enrichment (stronger than C424's 1.31x) | C453 |

**Key insight:** HT uses the SAME prefix vocabulary across all systems but varies in DENSITY. It is modulated by:
1. **Codicological structure** (quire-level clustering)
2. **System context** (A > AZC > B density gradient)
3. **Production continuity** (strong adjacency clustering)

This makes HT the **glue that makes silence usable** - it keeps operators oriented across time and pages without carrying semantic content.

---

## Phase Synchrony (Tier 2)

Despite being non-operational, HT prefixes are **synchronized** to procedural phase (C348):

| Test | Finding |
|------|---------|
| Position gradient | EARLY: op-, pc-, do-; LATE: ta- |
| Grammar synchrony | V=0.136, p<0.0001 |
| Regime association | EXTREME: al-, yk-, ke-, ka-, op-; LOW: yt- only |

HT tracks **human-relevant procedural phase** while remaining decoupled from execution.

---

## Interpretation (Tier 3-4)

### Dual-Purpose Attention Mechanism (Tier 3)

HT serves **two complementary functions**:

1. **Attention maintenance** during waiting phases
2. **Guild training** in the art of the written form

This is NOT "doodling" or "scribbling" - the evidence shows highly structured, intentional practice.

HT achieved 4/8 tests for **attentional pacing** function (C209 - UNDERDETERMINED):
- NOT sensory checkpoints (avoid hazards, don't cluster near them) [hazard layer withdrawn — C2081]
- NOT quantitative markers (no counting behavior)
- NOT scribal errors (too systematic, section-specific)
- Serve human-facing navigation at SECTION level

### Deliberate Skill Acquisition (Tier 3)

4/5 tests confirm **intentional training** rather than random mark-making (C221):

| Evidence | Finding | Implication |
|----------|---------|-------------|
| Rare grapheme over-representation | 7.81x (p=0.0001) | Practicing difficult forms |
| Run structure | CV=0.35 matches fixed-block rehearsal | Deliberate practice blocks |
| Boundary-pushing forms | 24.5% | Exploring morphological limits |
| Section-level family rotation | Change rate 0.71 | Systematic curriculum |

### Unified Interpretation (Tier 3)

> "While at station and not acting → practice the written form."

Operators maintained attention AND trained their craft through **deliberate skill practice** during waiting phases. This explains:
- Silent activity (can't monitor apparatus while talking)
- ~11,000 unique types (combinatorial practice variety)
- 71.3% compositional (trained practice follows rules)
- Disjoint prefixes (avoid confusion with operational text)
- 80.7% section-exclusive (different scribes/sessions)
- Complete hazard avoidance (stop writing when attention demanded) [historical — rests on the withdrawn hazard layer]
- Rare grapheme engagement (practicing difficult forms, not avoiding them)

Historical parallel: Medieval apprentice work-study combination - productive waiting.

---

## Speculative Vocabulary (Tier 4)

| Label | Structural Function | Speculative Meaning |
|-------|---------------------|---------------------|
| ESTABLISHING | Section entry | System warming |
| RUNNING | Wait marker | Steady reflux |
| HOLDING | Persistence marker | Maintain state |
| APPROACHING | Constraint rise | Watch closely |
| RELAXING | Constraint fall | Ease vigilance |
| EXHAUSTING | Section exit | Run winding down |

---

## What HT Is NOT

- **NOT machine-state tracking** (avoids hazards, removal doesn't affect execution)
- **NOT material annotation** (no referential tokens)
- **NOT control-plane logic** (downstream only, never upstream)
- **NOT scribal errors** (33% error rate implausible, too structured)
- **NOT interleaved document** (why would it correlate with B's grammar/hazards?)

*[The "hazards" in these reasons refer to the withdrawn forbidden-transition layer (C2081; STATUS_BRIEF §3); the non-operational tests C404–C406 do not depend on it.]*

---

## What HT IS

- A **dual-purpose attention mechanism**: maintains alertness AND trains the written form
- A **parallel human-facing notation** synchronized to procedural phase
- **Deliberate skill practice** that maintains operator readiness during waiting
- **Structurally integrated** but **functionally independent** of execution
- **NON-EXECUTABLE** infrastructure for human operators
- **Guild training artifact**: rare grapheme engagement, boundary exploration, systematic curriculum

---

## HT-AZC Placement Affinity (Tier 2) - NEW

HT shows **significant preference for boundary positions** within Zodiac AZC (C457):

| Family | HT Rate | Interpretation |
|--------|---------|----------------|
| R (radial/interior) | 29.5% | Stable phase monitoring |
| S (sector/boundary) | **39.7%** | Transition attention |

**Difference:** 10.3% (p < 0.0001, Cramer's V = 0.105)

*[C457 survives the PHASE_742 audit at corrected H-only N (R 29.1%, S 41.7%; within-folio null p=0.0001), with the R = radial / S = sector gloss kept. The "interior/boundary" reading is the S/R division C435, retracted in PHASE_742 as a locus-length tautology; "monitoring" and "attention" are Tier-3 glosses.]*

This connects C456 (AZC interleaved spiral) with HT behavior: [v7.26 status: C456 demoted to Tier 3 (transcription-order statistic, like retracted C433-C435)]
- R-S alternation isn't just structural
- HT tracks the interior/boundary rhythm [interior/boundary reading retracted with C435]
- Supports "attention at phase boundaries" interpretation

**Key insight:**
> AZC defines the boundary structure of experience; HT marks when human attention should increase inside that structure.

---

## Key Constraints

| # | Constraint |
|---|------------|
| 166 | 0/35 forbidden seam presence (relative to the withdrawn forbidden-transition layer) |
| 167 | 80.7% section-exclusive |
| 169 | Hazard avoidance 4.84 vs 2.5 (relative to the withdrawn hazard layer) |
| 341 | HT-program stratification |
| 342 | HT-LINK decoupling (ρ=0.01) |
| 347 | Disjoint prefix vocabulary |
| 348 | Phase synchrony (V=0.136) |
| 404 | Terminal independence |
| 405 | Causal decoupling |
| 406 | Generative structure |
| **450** | **Quire clustering (eta-sq=0.150)** |
| **451** | **System stratification (A > AZC > B)** |
| **452** | **Unified prefix vocabulary (Jaccard >= 0.947)** |
| **453** | **Adjacency clustering (1.69x enrichment)** |
| **457** | **HT boundary preference in Zodiac AZC (S=39.7% > R=29.5%)** |

---

## Navigation

← [cross_system.md](cross_system.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
