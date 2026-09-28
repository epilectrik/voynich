# Currier B: Executable Grammar

**Status:** CLOSED | **Tier:** 0-2 | **Scope:** 61.9% of tokens, 83 folios

> **Status note (v7.25, 2026-09-28).** This overview predates the September 2026 review. Where it conflicts with
> `SYSTEM/STATUS_BRIEF.md` and the generated `CONSTRAINT_TABLE.txt`, those win. Tier 0 was restated on 2026-09-28
> (human sign-off) to its measured core:
>
> > Currier B is written in a single, compact token grammar: 49 classes covering 69.5% of its tokens, organised by line
> > with positional zones and word-boundary glyph coupling, and applied in folio units that share the grammar while
> > carrying their own vocabulary. This structure is not reproduced by copy-and-modify generation or by the Naibbe cipher
> > as published.
>
> Basis: C121, C124 (as corrected); C956, C357; C1212, C1563 (with PHASE_761); C531, C1790; C2077, C2080. The earlier
> Tier-0 sentence ("closed-loop, kernel-centric control programs ... narrow viability regime") is now a Tier-3 working
> interpretation with its supports withdrawn. Sections below that rest on the kernel, hazard topology, LINK monitoring
> or convergence are bannered as historical and kept for traceability.
>
> **Measurements that stand (STATUS_BRIEF §2):** the 49-class grammar (C121, C124); positional zones (C956); line
> regularity (C357); boundary glyph coupling (C1212, C1563); word-ending routing — a token's two-glyph ending predicts
> the next token's class beyond that coupling (C2082); common-token zero bigrams reduce to composition, zones and
> coupling, so no prohibition layer remains (C2081); family preference (C1313, C549, C2056 with its other legs demoted —
> qok→ok/oke only); folio units (C531, C1790);
> occupancy only — 57.8% of folios end in their dominant macro-state (C074).

---

## Overview

Currier B is the primary executable content of the Voynich Manuscript. Each folio is a complete, self-contained control program governed by a single shared grammar. **[Status: the measured claim is that folios are units sharing one grammar while carrying their own vocabulary (C531, C1790); "executable control program" is the Tier-3 working interpretation (C120, C171 demoted to Tier 3).]**

| Metric | Value |
|--------|-------|
| Token coverage | 61.9% (~75,248 tokens — legacy all-transcriber count; H-track Currier B = 23,243 tokens) |
| Folios | 83 |
| Token types | 479 (grammar vocabulary; C124 as corrected gives 480) |
| Instruction classes | 49 (9.8x compression) |
| Grammar coverage | 100% of the grammar's own vocabulary = 69.5% of Currier B tokens; HT/UN defined by exclusion (C124 as corrected; C566, C740) |
| Forbidden transitions | ~~17~~ withdrawn — zero bigrams reduce to composition, zones and boundary coupling (C2081; C957 superseded) |
| LINK density | ~~38%~~ 13.2% true density; 38% not reproducible (C609) |

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

*Role names are the project's labels for class groupings; the "Function" glosses (energy, intervention, flow) belong to the Tier-3 working interpretation.*

### Grammar Properties

- **100% coverage** of the grammar's own 480-type vocabulary, which is 69.5% of Currier B tokens; the remainder (HT/UN) is defined by exclusion (C124 as corrected; C566, C740). The older wording "every Currier B token parses" is not accurate.
- **No exceptions**: Grammar is universal across all 83 folios
- **Compositional**: Tokens decompose into PREFIX + MIDDLE + SUFFIX
- **Deliberately over-specified**: 49 classes reducible to ~29 without structural loss (C411)

---

## Kernel Structure (historical — formerly labelled Tier 0)

**[Withdrawn v7.24/7.25 — historical; see SYSTEM/STATUS_BRIEF.md §3]** "Kernel k/h/e as the core of the grammar" is
superseded: C089 → C2082 (PHASE_763, MIXED). At glyph level k shows no routing beyond matched control glyphs; the
e/bench signal is word-ending routing, not a kernel role. The role glosses C103–C105 and primitive list C085 are demoted
to Tier 3. What remains as measurement is a family preference (qo tokens rich in k, ok tokens in e; qo/ch-sh alternation:
C1313, C549, C2056 as revised, other legs demoted) and word-ending routing (C2082). The text below is kept for traceability.

Three operators form the control core:

| Operator | Role | Evidence |
|----------|------|----------|
| **k** | ENERGY_MODULATOR | Adjusts energy input |
| **h** | PHASE_MANAGER | Manages phase transitions |
| **e** | STABILITY_ANCHOR | Maintains stable state (54.7% of recovery paths) |

### Kernel Properties

- All three are **BOUNDARY_ADJACENT** to forbidden transitions (C107) [the forbidden-transition layer is withdrawn — C2081]
- **e** dominates: 36% of Currier B tokens are e-class (C339)
- **h→k is SUPPRESSED** (0 observed) (C332)
- **e→e→e = 97.2%** of kernel trigrams (C333)

*[C332, C333, C339 remain Tier 2 in the registry as EVA-letter counts (C107 was demoted to Tier 3 in the v7.26 cascade). "h" sits inside a bench or benched-gallows glyph 98.9% of the time (C1440, PHASE_754), so letter statistics involving h are partly spelling (STATUS_BRIEF §3, EVA-letter row).]* [v7.26 status: C107 demoted to Tier 3 (kernel/forbidden-pair framing withdrawn)]

### 10 Single-Character Primitives

The kernel builds on 10 primitives: `s, e, t, d, l, o, h, c, k, r` (C85) [C085 demoted to Tier 3: an EVA letter inventory — c and h are the two halves of the bench glyph]

---

## Hazard Topology (historical — formerly labelled Tier 0)

**[Withdrawn v7.24/7.25 — historical; see SYSTEM/STATUS_BRIEF.md §3]** The hazard layer is withdrawn: the class level
is demoted (C783, Tier 3), the 5-class taxonomy was imposed by keyword matching (C2060), the battery's forbidden-suppression
test is idealization conformance (C2063), and common-token zero bigrams reduce to line composition, positional zones
and boundary glyph coupling (C2081, superseding C957). C109 is scoped to zero patterns; C216 is Tier 3. No prohibition
layer remains. The text below is kept for traceability.

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

*[Status: the Tier-0 measurement is folio units that share the grammar while carrying their own vocabulary (C531) with no duplicate lines or paragraphs (C1790). "Program" is the Tier-3 working interpretation.]*

- 83 folios enumerated
- Each starts from known initial state
- Each terminates (57.8% in STATE-C, 42.2% in transitional states) [C074 kept as occupancy only: 57.8% of folios end in their dominant macro-state; no sequential convergence (C1401–C1403)]
- No macro-chaining between folios (falsified in SEL-F)

### Line = Control Block

Lines are **formal control blocks**, not scribal wrapping (C357-360). [Measured: line regularity and boundary tokens (C357, C358); "control block" is the Tier-3 reading.]

- 3.3x more regular than random breaks
- Specific boundary markers: `daiin, saiin, sain` (initial), `am, oly, dy` (final)
- LINK suppressed at boundaries (0.60x)
- Grammar is LINE-INVARIANT (0 forbidden violations across line breaks) [the forbidden-transition layer is withdrawn — C2081]
- Positional zones: 192/334 tokens zone-exclusive, 2.72x shuffle (C956); the last glyph of a token predicts the first glyph of the next (C1212, C1563), robust to spacing uncertainty and replicated on ZL (PHASE_761)

### Program Taxonomy

*[The category labels ("waiting", "caution") are control-reading glosses (Tier 3). "Waiting" was read from LINK, which is a morphological artifact, not a waiting or monitoring operator (C1174, C609).]*

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
| Spatial distribution | Boundary-enriched (C805; C365 uniformity refuted) |
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

## Convergence (historical)

**[Withdrawn v7.24/7.25 — historical; see SYSTEM/STATUS_BRIEF.md §3]** Convergence to STATE-C / MONOSTATE as a
target is withdrawn. C074 is kept as an occupancy measurement only (57.8% of folios end in the macro-state that dominates
them); there is no sequential convergence at any scale (C1402); MONOSTATE is thematic dominance (C1403); the completion
gradient C325 is a section confound (C1401). C079 and C084 are demoted to Tier 3. The table is kept for traceability.

Programs converge toward stable states.

| Metric | Value |
|--------|-------|
| STATE-C terminal | 57.8% of folios |
| Transitional terminal | 42.2% of folios |
| Section dependency | H/S ~50% STATE-C, B/C 70-100% (C324) |
| Completion gradient | STATE-C increases with position (rho=+0.24) (C325) [v7.26 status: C325 demoted to Tier 3 (section confound (C1401))] |

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

This dichotomy encodes **MONITORING vs INTERVENTION** phases (C382). [v7.26 status: C382 demoted to Tier 3 (kernel contact is a spelling identity; monitoring reading withdrawn)]

*[Status: C382 remains Tier 2 as registered, but its MONITORING/INTERVENTION reading rests on constructs now withdrawn — LINK as a monitoring operator (C609, C1174) and the k/h/e kernel (C089 superseded by C2082). "Kernel contact" counts EVA letters k, h, e, and h is half the bench glyph (C1440). Read the labels as historical.]*

### Cross-Lane Content Prediction (C1242-C1244)

The QO and CHSH EN lanes carry paired information within each line. Adjacent cross-lane tokens show genuine MIDDLE co-occurrence (MI=1.0632, z=13.42) but null sequential ordering (z=0.05). Kernel routing at lane boundaries is massive (z=49.12), with CHSH→QO asymmetry (2.2x): monitoring constrains subsequent energy operations more than the reverse. sh functions as a monitor-pivot (routes to heat 32%), ch as a checkpoint-gate (24%, more varied outcomes). The -aiin/-ain suffix pair shows directional wind-down (64.9% aiin-first). The cycle is strictly line-scoped (cross-line null). The two extensible atoms encode independent control dimensions: e=intensity (k/ke/kee), i=duration (i/ii) (F-B-007, interpretive fit).

*[C1242–C1244 are Tier 2 measurements (MI, routing z, ordering rates). The glosses "monitoring", "monitor-pivot", "checkpoint-gate", "heat" and "control dimensions" are Tier-3 working-interpretation vocabulary; LINK/monitoring and the kernel reading are withdrawn (STATUS_BRIEF §3).]*

---

## Key Constraints

| # | Constraint |
|---|------------|
| 121 | 49 instruction classes (9.8x compression) — Tier 0 |
| 124 | 100% grammar coverage — Tier 0, as corrected: of its own vocabulary, 69.5% of B tokens |
| 109 | ~~5 failure classes~~ scoped: zero patterns only; 5-class taxonomy imposed (C2060); screen reduces (C2081) |
| 110 | PHASE_ORDERING 7/17 — per its row, a count of the one gloss-coherent grouping; the 5-class taxonomy is imposed (C2060) and the hazard layer withdrawn (historical) |
| 332 | h→k SUPPRESSED (EVA-letter count; see C1440) |
| 357 | Lines 3.3x more regular than random — Tier-0 basis |
| 382 | Morphology encodes control phase (Tier 2; labels rest on withdrawn LINK/kernel readings — see above) |
| 411 | Grammar deliberately over-specified |
| 956 | Positional token exclusivity (zones) — Tier-0 basis |
| 1212, 1563 | Boundary glyph coupling — Tier-0 basis (PHASE_761) |
| 531, 1790 | Folio-unique vocabulary; no duplicate lines/paragraphs — Tier-0 basis |
| 2081 | Common-token zero bigrams reduce (supersedes C957) |
| 2082 | Word-ending routing (supersedes C089) |

---

## Navigation

↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md) | [currier_A.md](currier_A.md) →
