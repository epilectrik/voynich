# C492: PREFIX Phase-Exclusive Legality

**Tier:** 2
**Scope:** A→AZC
**Status:** CLOSED
**Source:** STRUCTURAL_TOPOLOGY_TESTS

---

## Statement

One PREFIX class (control-flow category `ct`) exhibits a *phase-exclusive legality profile*: its tokens are grammatically admissible only in P-zone AZC contexts and are categorically absent from C- and S-zones. This exclusion is invariant under frequency control.

---

## Evidence

### Zone Distribution

| Zone | PREFIX `ct` | Baseline | Status |
|------|-------------|----------|--------|
| C (initial) | **0.0%** | 13.7% | CATEGORICALLY ABSENT |
| P (early-mid) | **26.3%** | 13.7% | 2× ENRICHED |
| R (committed) | 7.2% | 13.7% | Reduced |
| S (late) | **0.2%** | 13.7% | NEAR-ABSENT |

### Statistical Tests

- Chi-square for zone × PREFIX presence: p < 0.0001
- C-zone: 0/706 tokens (complete exclusion)
- S-zone: 1/500 tokens (near-complete exclusion)
- Effect is independent of:
  - Overall token frequency
  - Section/quire
  - HT density

### Enrichment Ratios

| Zone | Observed/Expected Ratio |
|------|------------------------|
| C | 0.00 (complete exclusion) |
| P | 1.92 (2× enrichment) |
| R | 0.53 (50% depletion) |
| S | 0.01 (near-complete exclusion) |

---

## Structural Interpretation

This constraint establishes that:

1. **PREFIX classes have zone-specific legality** - not all prefixes are valid in all AZC positions
2. **The exclusion is categorical** - 0% in C-zone is not a low frequency, it's a prohibition
3. **Phase specificity is grammatical** - the PREFIX is legal only during a specific phase window

---

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C443 | Extends: position-conditioned constraints apply to PREFIX |
| C371 | Complements: line-level positional grammar now has zone-level parallel |
| Zone-Material Orthogonality | Compatible: orthogonality is statistical, this exclusion is categorical |

---

## What This Constraint Does NOT Say

- Does NOT claim semantic meaning for the PREFIX
- Does NOT interpret what the phase-specific role "is"
- Does NOT assume material identity

The constraint is purely about legality profiles in grammar space.

---

## Tier 3 Speculation (Not Part of Constraint)

*Interpretive Note:* This PREFIX class may represent "phase-specific invariants" - control-flow roles that are introduced during active phases but are not present at initialization or final output. This interpretation remains Tier 3 speculative.
