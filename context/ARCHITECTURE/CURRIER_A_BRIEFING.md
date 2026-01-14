# What We Know About Currier A

**Version:** 1.0 | **Date:** 2026-01-12 | **Status:** CONSOLIDATED

This is the authoritative one-page summary of Currier A structural findings.

---

## The Bottom Line

Currier A is a **non-sequential categorical registry** that supports discrimination between comparable cases that the Currier B grammar deliberately collapses.

**Key structural fact:** The registry exhibits a strong discrimination gradient—entries requiring fine differentiation occupy 8.7x more vocabulary space than stable reference items.

---

## Frozen Facts (Tier 0-2)

| Finding | Constraint | Confidence |
|---------|------------|------------|
| A is DISJOINT from B grammar | C229 | FROZEN |
| A = non-sequential categorical registry | C240 | FROZEN |
| 8 PREFIX marker families | C240 | FROZEN |
| Tokens are compositional (PREFIX+MIDDLE+SUFFIX) | C267 | FROZEN |
| Sister pairs are equivalence classes | C408 | FROZEN |
| PREFIX encodes control-flow participation | C466/C467 | Tier 2 |
| No entry-level A↔B coupling | C384 | Tier 2 |

---

## Operational Domain Classification

Each PREFIX family maps to an operational domain based on B-grammar evidence:

| Domain | Prefixes | % of A | Structural Basis |
|--------|----------|--------|------------------|
| **ENERGY_OPERATOR** | ch, sh, qo | 59.4% | Dominates energy/escape roles in B |
| **CORE_CONTROL** | da, ol | 19.1% | Structural anchors; ol 5x B-enriched |
| **FREQUENT_OPERATOR** | ok, ot | 15.1% | FREQUENT role in canonical grammar |
| **REGISTRY_REFERENCE** | ct | 6.4% | 0% B terminals; 7x A-enriched |

**Coverage:** 63% of tokens classified. The 37% gap is expected (infrastructure, edge cases).

---

## The Discrimination Gradient

| Domain | Unique MIDDLEs | Ratio |
|--------|---------------|-------|
| ENERGY_OPERATOR | 564 | 8.7x |
| CORE_CONTROL | 176 | 2.7x |
| FREQUENT_OPERATOR | 164 | 2.5x |
| REGISTRY_REFERENCE | 65 | 1.0x |

**What this means:** Operations requiring fine discrimination need far more vocabulary than stable reference operations. This gradient:
- Survives section conditioning
- Correlates with HT vigilance pressure (C477)
- Is consistent with fractionation-type processes (Tier 3)

---

## Sister Pairs as Mode Selectors

| Pair | Primary | Alternate | Ratio |
|------|---------|-----------|-------|
| ch / sh | 7,181 | 3,303 | 2.17 |
| ok / ot | 1,905 | 1,640 | 1.16 |

Sister pairs encode **primary vs alternate handling mode** for the same operational role—not different materials. This fits:
- Conservative vs permissive handling
- Tight vs loose control
- Precision vs tolerance modes

---

## Section Distribution

| Section | ENERGY | CONTROL | FREQUENT | REGISTRY |
|---------|--------|---------|----------|----------|
| **H** | 61% | 18% | 13% | 8% |
| **P** | 56% | 22% | 20% | 3% |
| **T** | 55% | 20% | 20% | 5% |

**Key finding:** Section H (traditionally "herbal") accounts for **74% of all ENERGY_OPERATOR tokens**.

Safe interpretation: Section H structurally concentrates energy-intensive, highly discriminated operations.

---

## Why A Exists

From ECR-3 (Decision Archetypes):

> **Currier A exists because Currier B deliberately collapses distinctions.**

The B grammar handles execution decisions but intentionally ignores some distinctions that are decision-relevant. The A registry externalizes what grammar cannot track.

| Layer | What It Handles |
|-------|-----------------|
| B (Grammar) | Execution decisions: phase, energy, flow, recovery |
| A (Registry) | Discrimination decisions: "Is this case like that case?" |
| HT | Attention decisions: "Where should I be vigilant?" |
| AZC | Orientation decisions: "Where am I in the process?" |

---

## Confidence Summary

| Component | Confidence |
|-----------|------------|
| Structural facts (counts, distributions) | ~90-95% |
| PREFIX → operational domain | ~75-80% |
| Discrimination gradient interpretation | ~70% |
| Behavioral/chemistry framing | ~30-40% (illustrative) |

**Overall framework:** ~65-75%

---

## What This Does NOT Establish

- Specific substance identifications
- Entity-level naming
- Token-to-material mappings
- Recipe reconstruction
- That the domain is definitively thermal-chemical

---

## Key Files

| File | Content |
|------|---------|
| `results/currier_a_behavioral_registry.json` | Full classified registry (23,442 entries) |
| `results/currier_a_behavioral_stats.json` | Distribution statistics |
| `context/SPECULATIVE/a_behavioral_classification.md` | Detailed Tier-3 analysis |
| `context/CLAIMS/currier_a.md` | Frozen constraints |

---

## Navigation

- [CURRIER_B.md](CURRIER_B.md) - Grammar system
- [AZC_SYSTEM.md](AZC_SYSTEM.md) - Hybrid markers
- [CROSS_SYSTEM.md](CROSS_SYSTEM.md) - A/B/AZC coordination

---

*Consolidated 2026-01-12*
