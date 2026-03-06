# Phase 541: AZC Zone-Level Atomization

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1516-C1522 (7 new)

## Research Question

Do AZC internal zones differ at the atom level? Is o-HEAD uniformly enriched or zone-specific? What does zone-level atomization tell us about AZC's classification function?

## Context

Prior work established that AZC zones have distinct category profiles (C1269, V=0.084) but do NOT differentiate at raw atom level (C1271, 0/8 AXIS clusters significant). C1502 reported overall o-HEAD enrichment of 2.70x. The HEAD+MOD*+TERM instruction encoding grammar (C1393-C1395) provides a theoretically grounded decomposition that was established AFTER C1271.

**Key question:** Does the HEAD slot decomposition (C1394) reveal zone differentiation that raw character counting (C1271) missed?

## Method

12 tests on 3,227 AZC tokens (after cleaning: H-transcriber, non-empty, non-uncertain), decomposed using `decompose_middle_hmt()` into HEAD + MOD* + TERM slots. Major zones: R (1,326), C (629), S (501), P (397), L (68), OTHER (306). B baseline: 23,096 tokens. A baseline: 11,174 tokens.

Tests:
1. Zone population census
2. HEAD domain profile by zone
3. TERMINAL profile by zone
4. Modifier profile by zone
5. Headless abundance by zone
6. Zodiac vs A/C family comparison
7. R-series progression (R1-R4)
8. Zone differentiation: HEAD vs TERMINAL vs initial-atom
9. Pipeline classification (bridge/dark/exclusive) by zone
10. Zone distance to B and A profiles (JSD)
11. Label vs P-text comparison
12. o-domain deep dive

## Key Results

### 1. HEAD Domain Differentiation Is Significant (C1516)

chi2=112.3, V=0.115, p=5.81e-17 across 4 major zones. This REFINES C1271's null: the differentiation exists at HEAD slot level, not raw character level. HEAD slot decomposition captures domain selection that raw character counting misses because it mixes HEAD, MOD, and TERM positions.

### 2. o-HEAD Is Zone-Graded (C1517)

| Zone | o-HEAD | vs B (11.8%) |
|------|--------|-------------|
| R | 17.7% | 1.51x |
| P | 19.1% | 1.63x |
| C | 26.2% | 2.23x |
| S | 29.3% | 2.49x |
| L | 30.9% | 2.63x |
| AZC overall | 22.4% | 1.90x |

Overall AZC o-HEAD at HEAD-slot decomposition is 1.90x B, not 2.70x as in C1502. The difference is methodological: C1502 measured at MIDDLE initial-atom level (includes headless tokens where o may appear as modifier at position 0), while HEAD decomposition only counts o when it IS the HEAD atom. Both measurements are valid; they measure different things.

### 3. HEAD Dominates TERMINAL Across Zones (C1518)

Mean pairwise HEAD JSD=0.0254, TERMINAL JSD=0.0049 -- HEAD is 5.2x more discriminating. Zones specify WHAT DOMAIN (through HEAD) while sharing HOW instructions close (through TERMINAL). Most divergent pair S-P has 7.2x HEAD/TERMINAL JSD ratio.

### 4. Zodiac Uniform, A/C Diverse (C1519)

Between-family HEAD JSD=0.0158 (similar overall). Internal diversity: Zodiac=0.0617, A/C=0.1265 (2.0x ratio). Extends C436 (dual rigidity) to atom level.

### 5. R-Series No Gradient (C1520)

All Spearman correlations p=0.600 (N=4). R1-R3 are HEAD-stable (JSD 0.001-0.009). R4 anomalous (N=39, 51.3% headless) but underpowered for conclusions.

### 6. Pipeline Varies by Zone (C1521)

S-zone has most dark/exclusive (16.8%/21.4%), P-zone most bridge-dominated (80.4%). Dark MIDDLEs concentrate o-HEAD at 34.5% vs bridge 18.7% (1.84x). Zone o-HEAD variation is partially pipeline-mediated.

### 7. B-Proximate vs A-Proximate Partition (C1522)

| Zone | JSD to B | JSD to A | Closer to |
|------|----------|----------|-----------|
| R | 0.042 | 0.063 | B |
| P | 0.029 | 0.034 | B |
| C | 0.065 | 0.042 | A |
| S | 0.103 | 0.084 | A |
| L | 0.100 | 0.036 | A |

AZC hybridity (C301) is zone-graded: R/P are B-proximate (execution vocabulary), C/S/L are A-proximate (arrangement vocabulary).

## Additional Findings (not elevated to constraints)

- **Modifiers:** AZC has higher s-modifier (6.1% vs B 2.5%, 2.44x) and lower d-modifier (11.6% vs B 19.2%, 0.60x). S-zone has highest modifier load (138.7% total vs B 91.4%), suggesting S-zone vocabulary is more heavily modified.
- **Headless rates:** Mostly zone-uniform (21-33%), close to B (27.2%). P-zone has highest headless (33.0%), S-zone lowest (21.2%).
- **Labels vs P-text:** HEAD JSD=0.029 (modest). Labels have more o-HEAD (30.9% vs 19.1%) and less k-HEAD (1.5% vs 6.0%). Labels are more arrangement-focused.
- **o as TERM:** o-TERM = 0.0% in AZC, consistent with C1388 (o is never a terminal atom).

## Relationship to C1271

C1271 found 0/8 AXIS clusters significant at Bonferroni when testing AZC zone atom-level uniformity. Phase 541 finds significant HEAD differentiation (V=0.115). These are NOT contradictory:

- C1271 used C1207's AXIS clusters (coarse groupings of correlated atoms like {a,i,n,r}) tested at folio level using Kruskal-Wallis
- Phase 541 uses C1394's HEAD+MOD*+TERM decomposition tested at token level using chi-squared

The AXIS cluster approach lumps atoms across slot positions. The HEAD slot approach isolates the domain-selecting atom. The correct framing: **AZC zones share raw atom proportions (C1271 stands) but differ in how atoms are DEPLOYED across functional slots (C1516 new finding).** The differentiation is in HEAD domain selection, not in raw character inventory.

## Constraints Produced

| ID | Claim | Tier |
|----|-------|------|
| C1516 | AZC HEAD domain differentiation across zones (V=0.115) | 2 |
| C1517 | o-HEAD enrichment is zone-graded not uniform (17.7-29.3%) | 2 |
| C1518 | HEAD differentiation dominates TERMINAL across zones (5.2x) | 2 |
| C1519 | Zodiac HEAD uniformity vs A/C internal diversity (2.0x) | 2 |
| C1520 | R-series no HEAD gradient (all p=0.600) | 2 |
| C1521 | AZC zone pipeline composition varies (S dark-enriched) | 2 |
| C1522 | AZC zones partition between B-proximate and A-proximate | 2 |

## Files

- Script: `phases/AZC_ZONE_ATOMIZATION/scripts/azc_zone_atomization.py`
- Results: `phases/AZC_ZONE_ATOMIZATION/results/azc_zone_atomization.json`
