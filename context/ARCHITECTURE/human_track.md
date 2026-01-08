# Human Track Layer

> **For most questions, see:** [../CLAIMS/HT_CONTEXT_SUMMARY.md](../CLAIMS/HT_CONTEXT_SUMMARY.md) (PRIMARY, context-sufficient)

**Status:** CLOSED | **Tier:** 2 (structure), 3-4 (interpretation)

---

## Definition

The **Human Track (HT)** consists of tokens NOT in the 479-type canonical Currier B grammar vocabulary. This is a **token list definition**—the grammar has exactly 479 specific token types; everything else is "uncategorized" or "residue."

| Metric | Value |
|--------|-------|
| Occurrences | ~40,000 (33.4% of corpus) |
| Unique types | ~11,000 |
| Section-exclusive | 80.7% |
| Line-initial enrichment | 2.16x |

---

## Structural Properties (Tier 2)

### Hazard Avoidance

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
| Coverage | 71.3% decomposable | 100% grammar | — |

This is NOT scribal noise—it is a **formally distinct layer**.

---

## Non-Operational Status (Tier 2)

HT is **confirmed NON-OPERATIONAL** by three independent tests (C404-406):

| Test | Finding | Constraint |
|------|---------|------------|
| Terminal independence | HT doesn't predict outcome (p=0.92) | C404 |
| Causal decoupling | HT doesn't alter grammar flow (V=0.10) | C405 |
| Generative structure | Zipf distribution (0.89), 67.5% hapax | C406 |

**Removing all 40,000 HT tokens would not affect grammar coverage or hazard topology.**

---

## Program Stratification (Tier 2)

HT density varies by program type (C341):

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
- "More LINK = more doodling" hypothesis is **falsified**
- HT is not synchronized with LINK token positions

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

### Attentional Pacing (Tier 3)

HT won 6/8 tests for **attentional pacing** function (C209):

- NOT sensory checkpoints (avoid hazards, don't cluster near them)
- NOT quantitative markers (no counting behavior)
- NOT scribal errors (too systematic, section-specific)
- Serve human-facing navigation at SECTION level

### Calligraphy Practice Hypothesis (Tier 4)

4/5 tests favor **handwriting practice** over random doodling (C221):

| Evidence | Finding |
|----------|---------|
| Rare grapheme over-representation | 3.29x (p=0.0001) |
| Run structure | CV=0.43 matches fixed-block rehearsal |
| Boundary-pushing forms | 28.5% |
| Section-level family rotation | Change rate 0.71 |

### Unified Interpretation (Tier 4)

> "While at station and not acting → practice calligraphy."

Operators kept themselves alert through **deliberate mark-making** during waiting phases. This explains:
- Silent activity (can't monitor apparatus while talking)
- ~11,000 unique types (combinatorial practice variety)
- 71.3% compositional (trained practice follows rules)
- Disjoint prefixes (avoid confusion with operational text)
- 80.7% section-exclusive (different scribes/sessions)
- Complete hazard avoidance (stop writing when attention demanded)

Historical parallel: Medieval apprentice work-study combination.

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

---

## What HT IS

- A **parallel human-facing notation** synchronized to procedural phase
- **Phase-aware calligraphic practice** that maintains operator readiness
- **Structurally integrated** but **functionally independent** of execution
- **NON-EXECUTABLE** infrastructure for human operators

---

## Key Constraints

| # | Constraint |
|---|------------|
| 166 | 0/35 forbidden seam presence |
| 167 | 80.7% section-exclusive |
| 169 | Hazard avoidance 4.84 vs 2.5 |
| 341 | HT-program stratification |
| 342 | HT-LINK decoupling (ρ=0.01) |
| 347 | Disjoint prefix vocabulary |
| 348 | Phase synchrony (V=0.136) |
| 404 | Terminal independence |
| 405 | Causal decoupling |
| 406 | Generative structure |

---

## Navigation

← [cross_system.md](cross_system.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
