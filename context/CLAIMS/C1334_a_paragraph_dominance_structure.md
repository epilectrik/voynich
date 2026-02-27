# C1334: A Paragraph Category Dominance Structure

**Tier:** 2
**Scope:** A (all sections)
**Phase:** A_PARAGRAPH_CATEGORY_ARCHITECTURE (468)

## Constraint

A paragraphs have measurable category specialization with a highly skewed dominance distribution. STAGING dominates 43.6% of all paragraphs (1.89x its base rate of 23.1%), while three categories — CONTAINMENT, MONITORING, and MARKING — essentially never dominate a paragraph (0/241, 0/241, and 1/241 respectively), despite collectively comprising 17.4% of tokens.

## Evidence

From a_paragraph_category_architecture.py test A1:

**Overall (241 paragraphs with 3+ categorized PP MIDDLEs):**

| Category | Dominant in | % | Base rate | Lift |
|----------|------------|---|-----------|------|
| STAGING | 105 | 43.6% | 23.1% | **1.89x** |
| FLOW | 48 | 19.9% | 17.3% | 1.15x |
| TRANSITION | 42 | 17.4% | 17.9% | 0.97x |
| THERMAL | 33 | 13.7% | 14.4% | 0.95x |
| OPERATION | 12 | 5.0% | 9.9% | 0.50x |
| MARKING | 1 | 0.4% | 7.5% | 0.05x |
| CONTAINMENT | 0 | 0.0% | 4.8% | 0.00x |
| MONITORING | 0 | 0.0% | 5.1% | 0.00x |

- Mean dominance fraction: 0.299 vs null 0.281 (perm p<0.001, 1000 permutations)
- Holds in all 3 sections: H (n=183, mean_dom=0.294), P (n=47, mean_dom=0.315), T (n=11, mean_dom=0.317)

**Section specialization of dominant types:**

| Section | Top dominants |
|---------|---------------|
| H | STAGING 88/183 (48%), FLOW 38, TRANSITION 34 |
| P | THERMAL 21/47 (45%), STAGING 16, TRANSITION 7 |
| T | FLOW 7/11 (64%), diverse remainder |

## Interpretation

The A registry has a clear "backbone" category: STAGING (step, iterate, sequence, continue, repeat, cycle, loop, path). Nearly half of all paragraphs are organized around procedural sequencing. The three non-dominating categories (CONTAINMENT, MONITORING, MARKING) appear within paragraphs as supporting vocabulary but never define a paragraph's primary theme. This creates a two-tier architecture: 5 "dominating" categories that structure paragraphs, and 3 "supporting" categories that appear within but don't organize paragraphs.

The section specialization (H→STAGING, P→THERMAL, T→FLOW) extends C1266 (section atom-level differentiation) into the paragraph organization level.

## Provenance

- a_paragraph_category_architecture.json: test A1
- Extends: C1263 (paragraph specialization d=12.5, proved existence), C1266 (section atom differentiation)
- Relates to: C850 (5 structural paragraph types), C1039 (cluster selectivity)

## Status

CONFIRMED — paragraph dominance structure is highly skewed with strong section conditioning.
