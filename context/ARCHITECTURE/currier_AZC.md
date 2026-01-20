# Currier AZC: Context-Locking Scaffold System

**Status:** CLOSED | **Tier:** 2 | **Scope:** 7.7% of tokens, 30 folios

**See also:** [azc_transcript_encoding.md](azc_transcript_encoding.md) — Physical diagram encoding in transcript

---

## The Core Insight

> **AZC is not "diagrams with labels." It is a rigid, page-bound control scaffold that locks the system into constrained contexts.**

AZC does not execute procedures (that's Currier B).
AZC does not catalog distinctions (that's Currier A).
AZC controls **where things are allowed to appear**.

Every AZC page enforces a hard placement lock. The human enters AZC to commit to a context constraint.

---

## Two Families, Two Strategies (C430)

AZC comprises **two architecturally distinct folio families** with no transitional intermediates:

| Family | Folios | Strategy | Cross-Folio Consistency |
|--------|--------|----------|------------------------|
| **Zodiac (Family 0)** | 13 (all 12 Z + f57v) | Uniform scaffold | 0.945 |
| **A/C (Family 1)** | 17 (8 A + 6 C + 2 H + 1 S) | Folio-specific scaffolds | 0.340 |

**Both families are equally rigid** (≥98% self-transition, zero singletons). The difference is:

- **Zodiac:** The same rigid scaffold reused 12 times
- **A/C:** A different rigid scaffold each time

This is not "rigid vs permissive." This is **"rigid-and-uniform" vs "rigid-and-specific."**

---

## Classification Systems: Visual vs Textual Grammar

**IMPORTANT:** AZC folios have **two independent classification systems** that do not align:

### 1. Visual/Art-Historical Classification (Section Codes)

The transcript assigns section codes based on **visual content** (illustrations):

| Section | Count | Classification Criterion |
|---------|-------|-------------------------|
| Z (Zodiac) | 12 | Zodiac figures visible |
| A (Astronomical) | 8 | Astronomical diagrams |
| C (Cosmological) | 7 | Cosmological diagrams |
| H (Herbal) | 2 | Plant illustrations (NOT diagram pages) |
| S (Text) | 1 | Text-only page (NOT diagram page) |

**Note:** H and S are in the AZC JSON (30 total) but are NOT diagram folios. Analysis should use 27 (A+Z+C).

### 2. Textual Grammar Classification (Placement Patterns)

The structural analysis classifies by **placement grammar**:

| Family | Folios | Grammar Pattern |
|--------|--------|-----------------|
| Zodiac (Family 0) | 13 | Subscripted R/S codes (R1, R2, R3, S1, S2) |
| A/C (Family 1) | 17 | Non-subscripted codes (C, P, R, S) |

### The f57v Boundary Case

**f57v is the critical overlap:**
- **Section code:** C (Cosmological, by illustration)
- **Placement grammar:** Zodiac-like (uses subscripted R1, R2, R3 codes)

This means f57v is:
- In the **Zodiac family (Family 0)** by textual grammar (13 folios including f57v)
- In the **C section** by visual classification (7 folios including f57v)

The two classifications measure different properties. Visual classification captures what the diagram depicts. Textual grammar classification captures how the text is organized.

### Why This Matters

When analyzing AZC folios, explicitly state which classification you're using:

| Analysis Type | Use This Classification |
|---------------|------------------------|
| Diagram content | Visual (section codes: Z, A, C) |
| Placement patterns | Textual grammar (Family 0 vs Family 1) |
| Vocabulary compatibility | Either (document which) |
| Constraint validation | Must specify grouping method |

**Future tests MUST document:**
1. Which folios were included
2. Which classification system was used
3. Whether H/S non-diagram folios were included

---

## The Zodiac Control Scaffold (C431-C435)

The Zodiac pages implement an **extremely strict placement grammar** — stricter than Currier B:

### Block-Based Structure (C433)

Placement codes occur in massive contiguous blocks, never isolated:

| Code | Mean Run | Max Run | Self-Transition |
|------|----------|---------|-----------------|
| R1 | 79.6 | 156 | 99.9% |
| R2 | 64.3 | 106 | 99.9% |
| S1 | 51.2 | 73 | 100% |
| S2 | 40.3 | 141 | 100% |
| R3 | 40.9 | 132 | 98.8% |

Once a placement starts, it **locks for dozens of tokens**.

### Strict Forward Ordering (C434)

R-subscript transitions are strictly forward: **R1 → R2 → R3 only**.

| Transition Type | Observed | Expected | Status |
|----------------|----------|----------|--------|
| Backward (R2→R1, R3→R2) | 0 | 349 | **FORBIDDEN** |
| Skip (R1→R3) | 0 | 139 | **FORBIDDEN** |
| Forward (R1→R2, R2→R3) | 2 | 2 | Rare but legal |

No exceptions. The R-series implements a one-way progression through interior stages.

### Two-Layer Grammar (C435)

| Layer | Codes | Position | Function |
|-------|-------|----------|----------|
| **Boundary (S-series)** | S0, S1, S2 | 95%+ at line edges | Marks entry/exit |
| **Interior (R-series)** | R1, R2, R3, R4 | 89-95% interior | Fills stages in order |

S marks boundaries. R fills interiors. They never mix roles.

### Template Reuse (C431)

All 12 Zodiac folios form a single homogeneous cluster:
- Placement JS similarity: 0.964
- Bootstrap stability: 0.947

The twelve Zodiac pages are **structural clones** — the same control structure instantiated 12 times with local vocabulary variation.

---

## The A/C Variable Scaffold (C436)

The A/C family is **also rigid**, but each folio has its own scaffold:

| Metric | A/C Family | Zodiac Family |
|--------|------------|---------------|
| Self-transition rate | 98.0% | 98-100% |
| Singleton rate | 0% | 0% |
| Mean run length | 111.6 | 40-80 |
| Cross-folio consistency | **0.340** | **0.945** |

A/C runs are actually **longer** than Zodiac runs. The rigidity is comparable.

The difference: A/C folios don't share their scaffolds. Each diagram has custom placement constraints.

### Dominant Codes (A/C)

| Code | Frequency | Role |
|------|-----------|------|
| C | 32.3% | Interior (77.6%) |
| P | 26.6% | Interior (75.8%) |
| R | 11.2% | Mixed (55.2%) |
| S | 8.0% | Boundary (74.9%) |

No ordered subscripts (R1/R2/R3, S1/S2) appear in this family.

---

## What AZC Does (Functional Role)

AZC is **the human entry point** to the system. It is where the operator commits to a context lock:

| Family | Commitment |
|--------|------------|
| Zodiac | "Enter the standard cycle" |
| A/C | "Enter this specific configuration" |

AZC does not tell you what to do. It tells you **how narrowly constrained you are about to be**.

### Coordination by Constraint

AZC coordinates procedures by **forbidding wrong combinations**, not by choosing right ones:

- Which morphologies are legal in this context
- Where boundaries apply
- How long you stay inside one regime

This explains why:
- AZC has 219 forbidden token-placement pairs (C313)
- Placement constrains LEGALITY not PREDICTION (only 14% prediction gain)
- Position-locked operators exist (9/18 restricted to single placement)

---

## The Four-Layer Stack

AZC completes the Voynich control architecture:

| Layer | System | Function |
|-------|--------|----------|
| **Execution** | Currier B | Controls what you do over time |
| **Distinction** | Currier A | Catalogs where distinctions matter |
| **Context** | AZC | Locks which things may appear where |
| **Orientation** | HT | Keeps the human stable once locked |

AZC does not execute. It does not index. It **gates**.

---

## What AZC Rules Out

The extreme structural regularity definitively excludes:

- ❌ Calendars (semantic systems don't tolerate 99.9% self-transition)
- ❌ Astrology (no backward motion allowed)
- ❌ Month-by-month recipes (40-150 token lock-ins)
- ❌ Semantic labels attached to figures (zero flexibility)
- ❌ Educational diagrams (absolute prohibition of swaps)

Control scaffolds tolerate these patterns. Semantic systems do not.

---

## Classification Metrics

| Metric | AZC | Currier A | Currier B |
|--------|-----|-----------|-----------|
| Token percentage | 7.7% | 30.5% | 61.9% |
| Folios | 30 | 114 | 83 |
| TTR | 0.285 | 0.137 | 0.096 |
| Tokens/line (median) | 8 | 22 | 31 |
| LINK density | 7.6% | 3.0% | 6.6% |

### Vocabulary Overlap

| Metric | Value |
|--------|-------|
| B vocabulary coverage | 69.7% |
| A vocabulary coverage | 65.4% |
| Shared vocabulary (A∩B) | 60.5% |
| Unique vocabulary | 27.4% (903 types) |

AZC uses the shared core while adding diagram-specific terms.

---

## Key Constraints

### Core Architecture (C300-C322)

| # | Constraint |
|---|------------|
| C300 | 3,299 tokens (8.7%) unclassified by Currier |
| C301 | AZC is HYBRID (B=69.7%, A=65.4%) |
| C306 | Placement-coding axis established |
| C313 | Position constrains LEGALITY not PREDICTION |
| C317 | Hybrid architecture (topological + positional) |
| C322 | SEASON-GATED WORKFLOW interpretation |

### Folio Family Architecture (C430-C436)

| # | Constraint |
|---|------------|
| C430 | AZC Bifurcation: two architecturally distinct families |
| C431 | Zodiac Family Coherence (refines C319) |
| C432 | Ordered Subscript Exclusivity (Zodiac-only) |
| C433 | Zodiac Block Grammar (98%+ self-transition) |
| C434 | R-Series Strict Forward Ordering |
| C435 | S/R Positional Division (boundary/interior) |
| C436 | Dual Rigidity: uniform vs varied scaffolds |

---

## Tier Boundary

**Inside Tier 2 (structural):**
- Two folio families exist with distinct coordination strategies
- Placement grammar is extremely rigid in both families
- Zodiac implements uniform scaffold, A/C implements varied scaffolds
- Ordered subscripts are Zodiac-exclusive

**Outside (Tier 3+):**
- Mapping placements to physical diagram geometry
- Identifying celestial objects represented
- Interpreting what "entering a cycle" meant historically

---

## Summary

AZC is not decorative annotation. It is **bulk mechanical structure** that implements context-locking for an operational system.

The Zodiac pages are not "about" twelve things. They are the **same control structure reused twelve times**.

The A/C pages are not "loose." They are **equally rigid but diagram-specific**.

Together, they form a context-gating layer that constrains what Currier B procedures may legally execute and where Currier A distinctions apply.

---

## Navigation

← [currier_A.md](currier_A.md) | [cross_system_synthesis.md](cross_system_synthesis.md) →
