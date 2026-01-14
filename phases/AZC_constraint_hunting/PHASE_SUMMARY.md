# AZC Constraint Hunting Phase

**Status:** COMPLETE
**Date:** 2026-01-11
**Type:** Internal Exploration - Constraint Hunting

---

## Executive Summary

This phase probed AZC using Currier A and HT as controls. AZC is now boxed in from all sides:
- Currier A: understood (complexity-frontier registry)
- Currier B: closed (execution layer)
- HT: closed (anticipatory vigilance)

**Key Finding:** AZC is not a degenerate system. It implements **deliberate filtering and scaffolding** that differs structurally between the Zodiac and A/C families.

---

## Test Results Summary

| Test | Finding | Significance | Constraint Candidate |
|------|---------|--------------|---------------------|
| 1.1 MIDDLE universality | ENRICHED (48.1% vs 43.7%) | p < 0.0001 | AZC enriches universal MIDDLEs |
| 1.2 Suffix entropy | R-series > S-series | p < 0.00001 | Interior placements permit wider decision space |
| 1.3 Sister balance | Zodiac more balanced (68.8% vs 73.5%) | p = 0.038 | Family-specific mode preferences |
| 1.4 Prefix distribution | qo depleted (4.7% vs 14.7%) | p < 0.0001 | AZC filters high-hazard prefixes |
| 2.3 Bundle survival | 90% survival rate | N/A | AZC preserves A recognition bundles |
| 3.1 Vocabulary overlap | Jaccard = 0.120 | N/A | Families are vocabulary-distinct |
| 3.2 Placement grammar | Completely different | p < 0.0001 | Families use distinct placement systems |

**Tests with insufficient data:** 2.1 (adjacency), 2.2 (HT slope)

---

## Stage 1: AZC Audit

### Test 1.1: MIDDLE Universality in AZC

**Question:** Are universal MIDDLEs preserved, suppressed, or enriched in AZC?

**Result:** ENRICHED
- AZC: 48.08% universal MIDDLE tokens
- A baseline: 43.74%
- Chi-squared = 40.91, p < 0.000001

**Interpretation:** AZC preferentially admits material-independent recognition points. This suggests AZC gates legality based on universality.

---

### Test 1.2: Suffix Entropy by AZC Placement

**Question:** Does placement constrain decision archetypes?

**Result:** SIGNIFICANT DIFFERENCE
- R-series mean entropy: 1.120 bits
- S-series mean entropy: 0.612 bits
- Kruskal-Wallis H = 26.23, p < 0.00001

**Interpretation:** Interior placements (R-series) permit wider decision space than boundary placements (S-series). Placement gates decision archetype availability.

---

### Test 1.3: Sister Balance by AZC Family

**Question:** Do families show different sister-pair preferences?

**Result:** SIGNIFICANT DIFFERENCE
- Zodiac: 68.8% precision mode
- A/C: 73.5% precision mode
- Chi-squared = 4.29, p = 0.038

Both families are biased toward precision relative to A baseline (51%), but Zodiac is relatively more balanced.

**Interpretation:** Zodiac family maintains more mode flexibility than A/C family.

---

### Test 1.4: Prefix Distribution Compatibility

**Question:** Does AZC filter prefix classes?

**Result:** STRONG FILTERING
- qo-prefix: 4.7% in AZC vs 14.7% in A (0.32x, p < 0.0001)
- ct-prefix: 0.9% vs 6.4% (0.14x)
- ot-prefix: 24.6% vs 7.0% (3.51x ENRICHED)
- ok-prefix: 20.1% vs 8.1% (2.47x ENRICHED)

**Interpretation:** AZC filters high-hazard qo/ct prefixes and enriches ot/ok prefixes. AZC may preferentially admit low-hazard material classes.

---

## Stage 2: Cross-Layer Geometry

### Test 2.1: AZC Adjacency × A Recognition Density

**Result:** Insufficient data (only 2 A folios adjacent to AZC in sequence)

---

### Test 2.2: HT Slope at AZC Boundaries

**Result:** Insufficient data (HT per-folio structure not fully available)

---

### Test 2.3: Recognition Bundle Disruption

**Question:** Does AZC interrupt MIDDLE co-occurrence patterns from A?

**Result:** 90% SURVIVAL RATE
- 9/10 top A attraction pairs survive in AZC
- AZC preserves recognition bundles, does not disrupt them

**Interpretation:** AZC acts as a passthrough for recognition patterns, not a reset.

---

## Stage 3: Zodiac vs Non-Zodiac Family Comparison

### Test 3.1: Vocabulary Overlap by Family

**Result:** VOCABULARY-DISTINCT
- Zodiac types: 1,335
- A/C types: 1,667
- Shared: 321 types
- Jaccard similarity: 0.120 (very low)

Baseline: Within-A/C consistency is 0.340. The between-family Jaccard (0.120) is lower, indicating families are more distinct from each other than internal A/C variation.

**Interpretation:** Families share only minimal vocabulary.

---

### Test 3.2: Placement Grammar Differences

**Result:** COMPLETELY DIFFERENT GRAMMARS

| Placement | Zodiac | A/C |
|-----------|--------|-----|
| R1 | 28.2% | 0% |
| R2 | 23.6% | 0% |
| R3 | 14.0% | 0% |
| S1 | 16.6% | 0% |
| S2 | 14.4% | 0% |
| C | 0.2% | 31.2% |
| P | 0% | 27.5% |
| R | 0% | 11.6% |

Chi-squared = 38.82, p < 0.0000001

**Interpretation:** Zodiac uses subscripted placements (R1-R3, S1-S2); A/C uses unsubscripted placements (C, P, R, S). They implement completely distinct scaffolding strategies.

---

## Constraint Candidates

### Tier 3 Candidates (Require Expert Review)

| ID | Statement | Evidence |
|----|-----------|----------|
| C463 | AZC enriches universal MIDDLEs relative to A baseline | Chi² = 40.91, p < 0.0001 |
| C464 | Interior placements permit wider suffix entropy than boundary placements | KW H = 26.23, p < 0.00001 |
| C465 | qo-prefix is depleted in AZC (0.32x relative to A) | Binomial p < 0.0001 |
| C466 | Zodiac and A/C families use distinct vocabulary pools | Jaccard = 0.120 |
| C467 | Zodiac and A/C families use mutually exclusive placement codes | Chi² = 38.82, p < 0.0001 |

---

## Architectural Implications

### What AZC Does
1. **Filters recognition** - Enriches universal MIDDLEs, depletes qo/ct prefixes
2. **Gates decisions** - Interior placements allow wider suffix choice
3. **Preserves bundles** - A's recognition clusters survive into AZC
4. **Bifurcates scaffolds** - Two families with completely different placement grammars

### What AZC Does NOT Do
1. Does NOT disrupt recognition patterns
2. Does NOT treat A vocabulary as degenerate
3. Does NOT use a single uniform strategy

### Two-Family Model Deepened

| Property | Zodiac (13 folios) | A/C (17 folios) |
|----------|-------------------|-----------------|
| Cross-folio consistency | 0.964 | 0.340 |
| Placement codes | R1, R2, R3, S1, S2 | C, P, R, S |
| Between-family Jaccard | 0.120 | 0.120 |
| Sister preference | 68.8% precision | 73.5% precision |
| ot-prefix share | 36.0% | 17.3% |
| qo-prefix share | 1.6% | 6.7% |

---

## Files Created

| File | Contents |
|------|----------|
| `azc_middle_universality.py` | Test 1.1 |
| `azc_suffix_entropy.py` | Test 1.2 |
| `azc_sister_balance.py` | Test 1.3 |
| `azc_prefix_distribution.py` | Test 1.4 |
| `azc_recognition_geometry.py` | Tests 2.1-2.3 |
| `azc_family_comparison.py` | Tests 3.1-3.2 |
| `results/azc_middle_universality.json` | Test 1.1 results |
| `results/azc_suffix_entropy.json` | Test 1.2 results |
| `results/azc_sister_balance.json` | Test 1.3 results |
| `results/azc_prefix_distribution.json` | Test 1.4 results |
| `results/azc_recognition_geometry.json` | Tests 2.1-2.3 results |
| `results/azc_family_comparison.json` | Tests 3.1-3.2 results |

---

## Next Steps

1. Expert review of 5 constraint candidates (C463-C467)
2. Consider promoting significant findings to Tier 2
3. Update AZC architecture documentation with new structural insights
4. Cross-validate against existing C300-C460 constraints

---

## Semantic Ceiling

This phase measures **filtering, gating, and scaffolding** - not content.
- We know WHAT AZC filters (universal MIDDLEs, qo-prefixes)
- We know WHERE decisions narrow (S-placements)
- We do NOT know WHY (no entity-level semantics)

---

*Phase completed 2026-01-11*
