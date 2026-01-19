# JAR_WORKING_SET_INTERFACE

**Phase ID:** JAR-WORKING-SET-INTERFACE
**Status:** CLOSED
**Tier:** 3 (Interface Characterization)
**Date:** 2026-01-17

---

## Summary

Jars in the Voynich Manuscript function as **visual, apparatus-level anchors for complementary working sets** of materials—showing an expert what belongs together in a single operational context, without encoding procedure, order, or meaning.

---

## Investigation Trajectory

This phase tested four mutually exclusive hypotheses about jar function:

| Hypothesis | Prediction | Result | Status |
|------------|------------|--------|--------|
| Storage/inventory | Neutral or homogeneous grouping | Falsified | Closed |
| Contamination avoidance | Strong negative exclusion | Falsified (inverse signal) | Closed |
| Material taxonomy | Class homogeneity | Falsified | Closed |
| **Complementary working sets** | Positive cross-class enrichment | **Confirmed** | Survives |

The surviving hypothesis is the **only one consistent with all frozen constraints**.

---

## Key Findings

### 1. Jar Labels Are Unique Apparatus Identifiers

- 16 unique jar labels across 7 folios
- **No jar label repeats** across folios
- Jar prefixes avoid M-A (energy) class entirely

### 2. Contamination Avoidance: FALSIFIED

| Metric | Value |
|--------|-------|
| Observed exclusions | 5 pairs |
| Expected exclusions | 10.1 pairs |
| Ratio | 0.49x (FEWER than random) |
| P-value | 0.978 |

Jars show **fewer** exclusions than random—the opposite of contamination avoidance.

### 3. Class Homogeneity: FALSIFIED

| Metric | Value |
|--------|-------|
| Observed homogeneity | 24.5% |
| Expected homogeneity | 33.5% |
| Ratio | 0.73x (LESS than random) |
| P-value | 0.965 |

Jars are **more diverse** than random—the opposite of taxonomic grouping.

### 4. Cross-Class Pair Enrichment: CONFIRMED

| Class Pair | Observed | Expected | Ratio |
|------------|----------|----------|-------|
| M-B + M-D | 8 | 4.34 | **1.84x** |
| M-A + M-B | 4 | 2.38 | **1.68x** |
| M-A + M-D | 3 | 1.88 | **1.59x** |

All cross-class pairs are **enriched**. Jars deliberately combine materials from different classes.

### 5. Triplet Stability: CONFIRMED

| Triplet | Observed | Expected | Ratio | P-value |
|---------|----------|----------|-------|---------|
| M-B + M-D + OTHER | 7 | 4.11 | **1.70x** | **0.022** |
| M-A + M-B + M-D | 3 | 1.41 | **2.13x** | 0.107 |
| M-A + M-B + OTHER | 4 | 2.28 | 1.75x | 0.093 |
| M-A + M-D + OTHER | 3 | 1.78 | 1.68x | 0.203 |

**Overall: 17 triplet occurrences vs 9.6 expected = 1.77x enriched**

The "complete working set" (M-A + M-B + M-D) is the most enriched triplet.

---

## Constraint Compliance

| Constraint | Status |
|------------|--------|
| C171 (no material encoding) | Compliant - roles identified, not substances |
| C384 (no A↔B coupling) | Compliant - nothing propagates to execution |
| C233 (LINE_ATOMIC) | Compliant - no scope or inheritance |
| C475/C476 (incompatibility) | Compliant - positive complementarity, not new rules |
| Apparatus-centric semantics | Perfect fit |

---

## Final Interpretation

> **Jars are visual, apparatus-level anchors that identify complementary working sets of materials intended to participate together in a single operational context. They externalize "what goes together" to the human operator while deliberately refusing to encode procedure, order, quantity, or meaning.**

This:
- Completes the apparatus-centric interpretation
- Explains jar uniqueness (physical apparatus instances)
- Explains prefix restrictions (container posture, not content)
- Explains positive diversity (complementary roles, not similar materials)
- Explains why nothing propagates downstream (interface layer only)

---

## Material Class Definitions

From CCM prefix mapping:

| Class | Prefixes | Role |
|-------|----------|------|
| M-A | ch, sh, qo | Energy operations (phase-sensitive) |
| M-B | ok, ot | Routine operations (mobile homogeneous) |
| M-D | da, ol | Stable anchor (structural) |
| M-C | ct | Registry reference |
| OTHER | Various | Unclassified |

---

## Files

| File | Description |
|------|-------------|
| `jar_exclusion_test.py` | Contamination avoidance test |
| `jar_homogeneity_test.py` | Class grouping test |
| `jar_complementarity_test.py` | Pair enrichment test |
| `jar_triplet_test.py` | Triplet stability test |
| `results.json` | Full statistical results |

---

## What This Does NOT Claim

- Jars do NOT encode specific substances
- Jars do NOT map to Brunschwig methods
- Jars do NOT select processing regimes
- Jars do NOT propagate to execution grammar
- This is NOT Tier 2 (structural) - it is Tier 3 (interface characterization)

---

## Governance

**Status:** CLOSED with explanatory saturation

Every alternative interpretation either:
- Contradicted the data, or
- Violated Tier 0-2 constraints

Further testing would either rediscover the same pattern or push toward semantic overreach.

---

## Cross-References

- `phases/PHARMA_LABEL_DECODING/README.md` - Source data
- `context/SPECULATIVE/apparatus_centric_semantics.md` - Theoretical framework
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Section X.18
