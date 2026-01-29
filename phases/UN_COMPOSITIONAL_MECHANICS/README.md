# UN_COMPOSITIONAL_MECHANICS

**Status:** COMPLETE | **Date:** 2026-01-26 | **Constraints:** C610-C613

## Purpose

Characterize the 7,042 UN (unclassified) tokens that comprise 30.5% of Currier B. C566 established they are "morphologically normal" — this phase asks: what ARE they? Can we predict their ICC roles? Do they form distinct sub-populations?

## Scripts

| Script | Purpose |
|--------|---------|
| `un_census.py` | Inventory, morphological profile, PREFIX->role probability, MIDDLE overlap, section/REGIME distribution |
| `un_role_prediction.py` | PREFIX-based, PREFIX+SUFFIX joint, MIDDLE-based, and consensus role prediction |
| `un_population_test.py` | K-means clustering, hapax/repeater analysis, AX-UN boundary test, folio-level predictors |

## Key Findings

### 1. UN = Morphologically Complex Tail (C610)

UN tokens have the same PREFIX distribution as classified tokens but are more complex:
- 2x suffix rate (77.3% vs 38.7%)
- 5.3x articulator rate (10.1% vs 1.9%)
- 79.4% PP MIDDLEs, 0% RI, 20.6% novel (90.7% of novel MIDDLEs contain PP atoms)

### 2. 99.9% Role Prediction (C611)

PREFIX alone assigns 99.2% of UN tokens. Consensus assigns 99.9%:
- EN: 37.1% (2,612 tokens)
- AX: 34.6% (2,439 tokens)
- FQ: 22.4% (1,574 tokens)
- FL: 5.9% (412 tokens)
- CC: **0.0%** — fully resolved, no unclassified variants

### 3. Genuine Bifurcation (C612)

UN splits into 2 clusters (silhouette=0.263 > EN anatomy 0.180):
- Cluster 0: high-suffix (94%), EN/AX dominated
- Cluster 1: lower-suffix (69%), FQ/AX dominated
- Hapax are significantly longer (6.65 vs 5.84, p<0.0001)
- UN proportion = lexical diversity index (rho=+0.631***)

### 4. AX-UN Boundary Is Continuous (C613)

AX-predicted UN tokens (2,150) behave like classified AX:
- Similar positions (p=0.084, not significantly different)
- Similar transition contexts
- If absorbed, AX grows from 17.9% to 27.2% of B

## Constraints Produced

| # | Name | Key Evidence |
|---|------|-------------|
| C610 | UN Morphological Profile | 2x suffix, 5.3x articulator, 79.4% PP MIDDLEs |
| C611 | UN Role Prediction | PREFIX assigns 99.2%; EN 37.1%, AX 34.6%, FQ 22.4%, CC 0% |
| C612 | UN Population Structure | k=2 silhouette=0.263; TTR rho=+0.631***; LINK rho=-0.524*** |
| C613 | AX-UN Boundary | positions p=0.084; continuous boundary; AX 17.9%->27.2% |

## Data Dependencies

| File | Source |
|------|--------|
| class_token_map.json | CLASS_COSURVIVAL_TEST |
| middle_classes.json | A_INTERNAL_STRATIFICATION |
| regime_folio_mapping.json | REGIME_SEMANTIC_INTERPRETATION |
| voynich.py | scripts/ |

## Verification

- UN tokens: 7,042 (exact match C566)
- UN types: 4,421 (exact match C566)
- UN hapax: 74.1% (exact match C566)
- Classified + UN = 16,054 + 7,042 = 23,096 (total B after label/uncertain exclusion)
- Role predictions sum to 7,042 (all assigned)
