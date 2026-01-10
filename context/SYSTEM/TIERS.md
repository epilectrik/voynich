# Epistemic Tiers

**Purpose:** Define the evidential status of all claims in this project.

---

## Tier Definitions

| Tier | Label | Meaning | Evidence Required | Permanence |
|------|-------|---------|-------------------|------------|
| **0** | FROZEN FACT | Proven by internal structural analysis | Structural proof from text alone | Permanent, never reopen |
| **1** | FALSIFICATION | Hypothesis tested and rejected | Explicit test with falsifying evidence | Permanent, do not retry |
| **2** | STRUCTURAL INFERENCE | High-confidence bounded conclusion | Strong statistical evidence, bounded scope | Stable unless contradicted |
| **3** | SPECULATIVE ALIGNMENT | Non-binding interpretive layer | Plausible fit, no structural proof | May change freely |
| **4** | EXPLORATORY | Idea-generation only | None required | Ephemeral |

---

## Tier 0: FROZEN FACTS

These are **proven by the internal structure of the text alone**, independent of any external interpretation.

**Characteristics:**
- Derived from structural analysis of token sequences
- No external knowledge required
- Reproducible by any competent analyst
- Cannot be overturned by interpretation

**Examples:**
- The grammar has 49 instruction classes with 100% coverage
- 17 specific transitions are forbidden (never occur)
- 57.8% of folios terminate in STATE-C
- Currier A and B are folio-disjoint (0 shared folios)

**Rule:** Tier 0 facts must never be reopened, questioned, or "improved." They are the foundation.

---

## Tier 1: FALSIFICATIONS

These are hypotheses that have been **explicitly tested and rejected** with falsifying evidence.

**Characteristics:**
- Were plausible prior to testing
- Have specific, documented refutation
- Include citation to the phase that falsified them

**Examples:**
- Language encoding (0.19% reference rate)
- Cipher encoding (transforms decrease MI)
- Illustration-dependent logic (swap invariance p=1.0)
- Step-by-step recipe format (families are emergent)

**Rule:** Tier 1 claims must never be retried. The evidence for rejection is final.

---

## Tier 2: STRUCTURAL INFERENCES

These are **high-confidence conclusions with bounded scope**, supported by strong statistical evidence.

**Characteristics:**
- Derived from quantitative analysis
- Explicitly bounded (applies to X, not Y)
- Could be refined by new evidence (but unlikely to be overturned)

**Examples:**
- Human Track shows structured practice patterns (4/5 tests), NOT random mark-making
- Prefix families partition into sister pairs (ch/sh, ok/ot)
- Lines are formal control blocks, not scribal wrapping
- Quires are organizational units (4.3x alignment)

**Rule:** Tier 2 claims are stable references. New analysis may extend or refine, but should cite existing constraints.

---

## Tier 3: SPECULATIVE ALIGNMENTS

These are **interpretive claims that fit the structure** but cannot be proven internally.

**Characteristics:**
- Consistent with Tier 0-2 findings
- Require external knowledge to evaluate
- Useful for understanding, not for proof
- Explicitly marked as speculative

**Examples:**
- The apparatus is a pelican alembic
- The process is circulatory reflux distillation
- The craft is perfumery/distillation
- Material classes correspond to botanical families
- HT serves dual-purpose: attention maintenance + guild training in the written form

**Rule:** Tier 3 claims must never contaminate Tier 0-2. Keep in SPECULATIVE/ directory.

---

## Tier 4: EXPLORATORY

These are **ideas and questions** for future investigation.

**Characteristics:**
- No evidence required
- May be contradictory or incomplete
- Useful for brainstorming
- Should be pruned regularly

**Examples:**
- "What if the zodiac sections encode seasonal timing?"
- "Could the repetition patterns indicate batch sizes?"
- "Is there a skill-level gradient in program complexity?"

**Rule:** Tier 4 ideas should either be promoted (tested → Tier 2/1) or discarded. Do not accumulate.

---

## Tier Transitions

| From | To | Requires |
|------|----|----------|
| 4 → 2 | Exploratory → Structural | Successful test with positive evidence |
| 4 → 1 | Exploratory → Falsified | Failed test with negative evidence |
| 3 → 2 | Speculative → Structural | New internal evidence (rare) |
| 2 → 0 | Structural → Frozen | Universal proof without exceptions |

**Downward transitions (3→4, 2→3) are rare but possible if evidence weakens.**

---

## Navigation

← [CLAUDE_INDEX.md](../CLAUDE_INDEX.md) | [STOP_CONDITIONS.md](STOP_CONDITIONS.md) →
