# C1417: ARTICULATOR Line-Initial Concentration

**Tier:** 2
**Scope:** B, line, position
**Phase:** 517 (ARTICULATOR_DEEP_DIVE)
**Date:** 2026-03-05

## Claim

Articulators concentrate at line-initial position: 17.3% at initial vs 2.7% medial (6.48x enrichment). Paragraph headers are 4.11x enriched (16.8% vs 4.1%). Two positional sub-groups: INITIAL articulators (d,k,p,s,t,y concentrated at Q0 2.4-4.2x) and FINAL articulators (l,r concentrated at Q4 2.4-2.6x). Cramer's V(position quintile, ARTICULATOR) = 0.092, p < 1e-115, N = 23,096.

## Evidence

- Script: `phases/ARTICULATOR_DEEP_DIVE/scripts/articulator_deep_dive.py` (T7, T8)
- Results: `phases/ARTICULATOR_DEEP_DIVE/results/articulator_deep_dive.json`

## Relationship to Existing Constraints

- Extends C1001 (PREFIX dual encoding -- content and positional grammar) to ARTICULATOR
- Consistent with C747/C748 (line-1 HT enrichment step function) -- articulators show similar opening-position concentration
- Extends C1287 (paragraph headers MARKING-enriched) -- articulators add to header specification
- INITIAL sub-group (d,k,p,s,t,y) parallels SETUP phase of C556 execution syntax
- FINAL sub-group (l,r) parallels LATE PREFIX family C539 (line-final enrichment)
