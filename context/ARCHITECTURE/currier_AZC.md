# Currier AZC: Astronomical/Zodiac/Cosmological Hybrid

**Status:** CLOSED | **Tier:** 2 | **Scope:** 7.7% of tokens, 30 folios

---

## Overview

AZC refers to text in the Astronomical (A), Zodiac (Z), and Cosmological (C) sections that was **never classified** by Currier as either A or B. It is a genuine **third mode** that bridges both systems.

| Metric | AZC | Currier A | Currier B |
|--------|-----|-----------|-----------|
| Token percentage | 7.7% | 30.5% | 61.9% |
| Folios | 30 | 114 | 83 |
| TTR | 0.285 | 0.137 | 0.096 |
| Tokens/line (median) | 8 | 22 | 31 |
| LINK density | 7.6% | 3.0% | 6.6% |

---

## Classification: HYBRID (Tier 2)

AZC straddles the A/B boundary:

| Metric | Value | Threshold |
|--------|-------|-----------|
| B vocabulary coverage | 69.7% | (just below 70%) |
| A vocabulary coverage | 65.4% | |
| Shared vocabulary (A∩B) | 60.5% | |
| Unique vocabulary | 25.4% (1,529 types) | |

**Verdict:** AZC uses the **shared core vocabulary** while adding unique diagram-specific terms.

---

## Distinctive Properties (Tier 2)

| Property | Value | Significance |
|----------|-------|--------------|
| Shortest lines | Median 8 tokens | Diagram annotation style |
| Highest LINK density | 7.6% | Most wait-heavy text |
| Highest vocabulary diversity | TTR 0.285 | Most varied per token |
| Section exclusivity | 98% | Z, A, C have separate vocabularies |

---

## Placement Coding System (Tier 2)

AZC-unique tokens exhibit a **finite, repeatable set of placement-dependent classes**:

### Placement Classes

| Class | Distribution | Function |
|-------|--------------|----------|
| C | 17.1% | Central/core position |
| P | 11.0% | Peripheral position |
| R1, R2, R3 | Variable | Radial positions (ordered) |
| S, S1, S2 | Variable | Edge/boundary markers |
| Y | Variable | Other positions |

### Axis Properties (C307-312)

| Property | Finding |
|----------|---------|
| Placement × Morphology | WEAK dependency (V=0.18) |
| R1/R2/R3 subscripts | ORDERED (monotonic middle length decrease) |
| Placement transitions | GRAMMAR-LIKE (99 forbidden, self-transitions 5-26x enriched) |
| Placement × Repetition | CONSTRAINED (P/S high, R low) |
| Placement × Boundary | POSITIONAL (S1/S2/X edge 85-90%, R1/R2 interior 3-9%) |
| Section × Placement | STRONG (V=0.631) |

---

## Positional Legality (Tier 2)

Position constrains **LEGALITY not PREDICTION** (C313-320):

| Finding | Evidence |
|---------|----------|
| Grammar collapse in 7 placements | (A1) |
| 219 forbidden token-placement pairs | z=13 (A2) |
| Prediction gain only 14% | Position defines what's ALLOWED, not LIKELY (A4) |
| Global illegality + local exceptions | Default-deny with explicit permits (C314) |
| 9/18 restricted operators placement-locked | Only appear in one placement (C315) |
| Phase-locked binding | 32.3pp drop under rotation (C316) |

### Architecture

- **C placement** is rotation-tolerant (9.8% drop) — topological
- **P/R/S placements** are phase-locked (40-78% drop) — positional
- System has **topological core with positional frame** (C317)

---

## Diagram Anchoring (Tier 2)

Placement codes are **diagram-anchored**, not abstract:

| Finding | Evidence | Constraint |
|---------|----------|------------|
| Folio-specific profiles | V=0.507 for folio × placement | C318 |
| Zodiac template reuse | f71-f73 share identical profile | C319 |
| S2 < S1 ordering | p < 0.0001 Mann-Whitney | C320 |
| Zodiac vocabulary isolated | J=0.076 between consecutive folios | C321 |

Different diagrams have different placement distributions, but zodiac folios reuse templates.

---

## Cycle Discriminator (Tier 2)

AZC was tested for calendar vs workflow organization:

| Test | Result |
|------|--------|
| Calendar vs Workflow | HYBRID (V difference = 0.013) |
| Placement × A-Material | V = 0.152 |
| Placement × B-Procedure | V = 0.139 |
| Zodiac vocabulary isolation | J = 0.076 |
| Seasonal clustering | 5/25 placements have full coverage |

**Verdict: SEASON-GATED WORKFLOW** — AZC encodes workflow states whose availability is seasonally constrained. Both material timing AND procedural state matter.

---

## AZC-Unique Vocabulary (Tier 2)

25.4% of AZC vocabulary (1,529 types) appears in neither A nor B:

| Property | Value | Significance |
|----------|-------|--------------|
| Section-exclusive | 98% | Z, A, C have separate vocabularies |
| Line-initial | 37% | Boundary concentration |
| Line-final | 37% | Boundary concentration |
| Hapax rate | 65.9% | Most appear only once |

**Structural signature:** LABELING (not executing, not indexing)

---

## Three Sections

| Section | Content | Characteristics |
|---------|---------|-----------------|
| **Z (Zodiac)** | Zodiac diagrams | Template reuse, isolated vocabulary |
| **A (Astronomical)** | Astronomical diagrams | Variable placement profiles |
| **C (Cosmological)** | Cosmological diagrams | Topological placement (rotation-tolerant) |

---

## Tier Boundary

**Inside Tier 2 (structural):**
- Placement classes exist and are formally distinct
- Placement constrains legality
- Diagram anchoring is confirmed

**Outside (Tier 3+):**
- Mapping placements to physical geometry
- Identifying celestial objects
- Correlating with apparatus components

---

## Key Constraints

| # | Constraint |
|---|------------|
| 300 | 9,401 tokens (7.7%) unclassified by Currier |
| 301 | AZC is HYBRID (B=69.7%, A=65.4%) |
| 302 | Distinct line structure (median 8 tokens) |
| 306 | Placement-coding axis established |
| 313 | Position constrains LEGALITY not PREDICTION |
| 317 | Hybrid architecture (topological + positional) |
| 322 | SEASON-GATED WORKFLOW interpretation |

---

## Navigation

← [currier_A.md](currier_A.md) | [cross_system.md](cross_system.md) →
