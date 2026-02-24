# Currier B: Executable Grammar

**Status:** CLOSED | **Tier:** 0-2 | **Scope:** 61.9% of tokens, 83 folios

---

## Overview

Currier B is the primary executable content of the Voynich Manuscript. Each folio is a complete, self-contained control program governed by a single shared grammar.

| Metric | Value |
|--------|-------|
| Token coverage | 61.9% (~75,248 tokens) |
| Folios | 83 |
| Token types | 479 |
| Instruction classes | 49 (9.8x compression) |
| Grammar coverage | 100% |
| Forbidden transitions | 17 |
| LINK density | 38% |

---

## 49-Class Grammar (Tier 0)

All 479 token types reduce to 49 instruction classes with zero loss of predictive power.

### Functional Roles

| Role | Classes | Function |
|------|---------|----------|
| CORE_CONTROL | 2 | Execution boundaries (daiin, ol) |
| ENERGY_OPERATOR | 11 | Energy modulation |
| AUXILIARY | 8 | Support operations |
| FREQUENT_OPERATOR | 4 | Common instructions |
| HIGH_IMPACT | 3 | Major interventions |
| FLOW_OPERATOR | 2 | Flow control |
| Other roles | 19 | Specialized functions |

### Grammar Properties

- **100% coverage**: Every Currier B token parses
- **No exceptions**: Grammar is universal across all 83 folios
- **Compositional**: Tokens decompose into PREFIX + MIDDLE + SUFFIX
- **Deliberately over-specified**: 49 classes reducible to ~29 without structural loss (C411)

---

## Kernel Structure (Tier 0)

Three operators form the control core:

| Operator | Role | Evidence |
|----------|------|----------|
| **k** | ENERGY_MODULATOR | Adjusts energy input |
| **h** | PHASE_MANAGER | Manages phase transitions |
| **e** | STABILITY_ANCHOR | Maintains stable state (54.7% of recovery paths) |

### Kernel Properties

- All three are **BOUNDARY_ADJACENT** to forbidden transitions (C107)
- **e** dominates: 36% of Currier B tokens are e-class (C339)
- **h→k is SUPPRESSED** (0 observed) (C332)
- **e→e→e = 97.2%** of kernel trigrams (C333)

### 10 Single-Character Primitives

The kernel builds on 10 primitives: `s, e, t, d, l, o, h, c, k, r` (C85)

---

## Hazard Topology (Tier 0)

17 specific token transitions are **absolutely forbidden** (never occur in valid text).

### 5 Hazard Classes

| Class | Count | % | Description |
|-------|-------|---|-------------|
| PHASE_ORDERING | 7 | 41% | Material in wrong phase location |
| COMPOSITION_JUMP | 4 | 24% | Impure fractions passing |
| CONTAINMENT_TIMING | 4 | 24% | Overflow/pressure events |
| RATE_MISMATCH | 1 | 6% | Flow imbalance |
| ENERGY_OVERSHOOT | 1 | 6% | Thermal damage |

### Hazard Properties

- **65% asymmetric**: X→Y forbidden doesn't imply Y→X forbidden (C111)
- **59% distant from kernel**: Not clustered around k/h/e (C112)
- **8 additional suppressed** transitions (<0.5x expected) (C386)
- **qo-prefix = escape route**: 25-47% of post-hazard transitions (C397)

### Why Failures Are Irreversible

| Failure Type | Why No Recovery |
|--------------|-----------------|
| Phase disorder | Condensate in wrong location, needs disassembly |
| Contamination | Mixed impurities can't be separated |
| Spillage | Escaped material can't be recovered |
| Scorching | Burned character can't be removed |
| Flow chaos | Must rebuild from stable state |

---

## Program Structure (Tier 2)

### Folio = Program

Each folio is a **complete, self-contained program** (C178, Phase 22).

- 83 folios enumerated
- Each starts from known initial state
- Each terminates (57.8% in STATE-C, 42.2% in transitional states)
- No macro-chaining between folios (falsified in SEL-F)

### Line = Control Block

Lines are **formal control blocks**, not scribal wrapping (C357-360).

- 3.3x more regular than random breaks
- Specific boundary markers: `daiin, saiin, sain` (initial), `am, oly, dy` (final)
- LINK suppressed at boundaries (0.60x)
- Grammar is LINE-INVARIANT (0 forbidden violations across line breaks)

### Program Taxonomy

| Category | Count | Characteristics |
|----------|-------|-----------------|
| CONSERVATIVE | 18 (22%) | High waiting, careful |
| MODERATE | 46 (55%) | Balanced approach |
| AGGRESSIVE | 15 (18%) | Fast, less waiting |
| ULTRA_CONSERVATIVE | 4 (5%) | Maximum caution |

---

## LINK Population (Tier 2)

LINK tokens (containing `ol` substring) are a **morphological artifact**, not a unified functional layer (C1174). The `ol` substring is recruited differently by each grammatical role.

| Metric | Value |
|--------|-------|
| Density | 13.2% of B tokens (3,047 tokens, C609) |
| Section conditioning | B=19.6%, H=9.1%, C=10.1% (C334) |
| Spatial distribution | Boundary-enriched (C805; refutes C365 uniform) |
| Vocabulary | Strongly role-stratified (V=0.404, C1170) |
| Behavior | Role-dominant, no cross-role substrate (C1171) |

### Role-Specific `ol` Usage (C1174)

| Role | How `ol` participates | Position |
|------|-----------------------|----------|
| CC | Standalone operator `ol` | MIDDLE |
| AX | Prefix component (ol+keedy, ol+chedy) | PREFIX (59%) |
| EN | Within energy operator morphology | MIDDLE/SPAN/SUFFIX |

### Positional Properties

- Boundary-enriched: first-token 17.2%, last-token 15.3%, middle 12.4% (C805)
- Mean position: 0.476 (earlier than baseline 0.504)
- Predecessor bias: NOT SIGNIFICANT (p=0.41, C804)
- Successor bias: WEAK (p<0.001, enrichments ~1.1x, C804)
- LINK-escalation complementarity: 0.605x baseline near escalation (C340)

---

## Convergence (Tier 2)

Programs converge toward stable states.

| Metric | Value |
|--------|-------|
| STATE-C terminal | 57.8% of folios |
| Transitional terminal | 42.2% of folios |
| Section dependency | H/S ~50% STATE-C, B/C 70-100% (C324) |
| Completion gradient | STATE-C increases with position (rho=+0.24) (C325) |

---

## Morphological Structure (Tier 2)

Tokens decompose compositionally:

```
token = [ARTICULATOR] + PREFIX + [MIDDLE] + SUFFIX
```

### Prefix-Suffix Dichotomy

| Type | Prefixes | Suffixes | Behavior |
|------|----------|----------|----------|
| KERNEL-HEAVY | ch, sh, ok, lk, lch, yk, ke | -edy, -ey, -dy | 100% kernel contact, LINK-avoiding |
| KERNEL-LIGHT | da, sa | -in, -l, -r | <5% kernel contact, LINK-attracted |

This dichotomy encodes **MONITORING vs INTERVENTION** phases (C382).

### Cross-Lane Content Prediction (C1242-C1244)

The QO and CHSH EN lanes carry paired information within each line. Adjacent cross-lane tokens show genuine MIDDLE co-occurrence (MI=1.0632, z=13.42) but null sequential ordering (z=0.05). Kernel routing at lane boundaries is massive (z=49.12), with CHSH→QO asymmetry (2.2x): monitoring constrains subsequent energy operations more than the reverse. sh functions as a monitor-pivot (routes to heat 32%), ch as a checkpoint-gate (24%, more varied outcomes). The -aiin/-ain suffix pair shows directional wind-down (64.9% aiin-first). The cycle is strictly line-scoped (cross-line null). The two extensible atoms encode independent control dimensions: e=intensity (k/ke/kee), i=duration (i/ii) (F-B-007, interpretive fit).

---

## Key Constraints

| # | Constraint |
|---|------------|
| 121 | 49 instruction classes (9.8x compression) |
| 124 | 100% grammar coverage |
| 109 | 5 failure classes |
| 110 | PHASE_ORDERING dominant (41%) |
| 332 | h→k SUPPRESSED |
| 357 | Lines 3.3x more regular than random |
| 382 | Morphology encodes control phase |
| 411 | Grammar deliberately over-specified |

---

## Navigation

↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md) | [currier_A.md](currier_A.md) →
