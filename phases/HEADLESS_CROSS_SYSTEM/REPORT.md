# Phase 542: Headless Compound Cross-System Distribution

**Phase:** HEADLESS_CROSS_SYSTEM
**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1523-C1527

---

## Research Questions

1. What is the headless rate in each system (A, B, AZC)?
2. Do headless compounds show the same pseudo-HEAD differentiation across systems?
3. Is da-PREFIX exclusivity universal or B-specific?
4. Does suffix bifurcation hold cross-system?
5. Do headless tokens cluster in specific AZC zones?
6. Are headless compounds bridge-enriched or dark-enriched?

---

## Method

All tokens from Currier A (11,174), Currier B (23,096), and AZC (3,227) decomposed via `decompose_middle_hmt()` into HEAD/MOD/TERM slots. Headless = MIDDLE whose first character is not in HEAD_ATOMS = {a, e, o, k, t}. 10 tests (T1-T10) covering headless rates, pseudo-HEAD profiles, PREFIX exclusivity, suffix rates, AZC zone distribution, pipeline composition, terminal profiles, category profiles, MIDDLE length, and cross-system type overlap.

---

## Results Summary

### T1: Headless Rate by System (C1523)

| System | N tokens | Headless N | Headless Rate |
|--------|----------|------------|---------------|
| **A** | 11,174 | 4,353 | **39.0%** |
| **B** | 23,096 | 6,277 | **27.2%** |
| **AZC** | 3,227 | 899 | **27.9%** |

- Omnibus chi2=504.49, p=2.82e-110
- A vs B: chi2=487.73, p=4.44e-108, ratio=1.43x
- B vs AZC: chi2=0.63, p=0.428 (NOT significant)

**Finding:** A has significantly more headless compounds (1.43x B). B and AZC are statistically indistinguishable. A's declarative register (C1395, C1507) preferentially uses headless infrastructure vocabulary.

### T2: Pseudo-HEAD Profile by System

| Rank | A | B | AZC |
|------|---|---|-----|
| 1 | i (21.3%) | l (20.4%) | y (22.1%) |
| 2 | y (16.4%) | d (18.2%) | l (16.4%) |
| 3 | c (11.1%) | i (16.8%) | r (13.6%) |
| 4 | l (10.5%) | r (13.9%) | d (13.1%) |
| 5 | h (10.0%) | c (9.8%) | i (12.6%) |

**Finding:** Each system has a different pseudo-HEAD emphasis: A=i-dominant (TRANSITION), B=l/d-dominant (STAGING/OPERATION), AZC=y-dominant (OPERATION). i is common to all three top-5s. Category profiles are near-identical cross-system (JSD=0.023-0.035) despite different pseudo-HEAD distributions.

### T3: da/sa/ta PREFIX Exclusivity (C1524)

| PREFIX | A headless% | B headless% | AZC headless% |
|--------|-------------|-------------|---------------|
| da | 99.8% (1078/1080) | 99.8% (1081/1083) | 98.1% (205/209) |
| sa | 99.2% (125/126) | 99.7% (328/329) | 98.2% (56/57) |
| ta | 98.6% (70/71) | 100.0% (237/237) | 94.4% (17/18) |

- da enrichment: A=844.6x, B=1,448.3x, AZC=132.7x

**Finding:** da/sa/ta headless exclusivity is UNIVERSAL across all three systems. This is a manuscript-wide grammar rule, not a B-specific phenomenon.

### T4: Suffix Rate (C1525)

| System | Headless suffix% | Headed suffix% | Ratio | chi2 | p |
|--------|-------------------|-----------------|-------|------|---|
| A | 35.2% | 48.0% | 0.73x | 177.0 | 2.2e-40 |
| B | 43.1% | 50.2% | 0.86x | 92.6 | 6.4e-22 |
| AZC | 35.9% | 59.0% | 0.61x | 137.3 | 1.1e-31 |

**Finding:** Headless compounds have LOWER suffix rates than headed in all three systems. AZC shows the strongest effect (0.61x). Mechanistically explained by terminal opacity (C1440): headless h-enrichment is insufficient to compensate for massive bare-terminal depletion.

### T5: AZC Zone Distribution

| Zone | Headless Rate | Ratio to B |
|------|---------------|------------|
| R | 27.3% | 1.00x |
| C | 27.8% | 1.02x |
| S | 21.2% | 0.78x |
| P | 33.0% | 1.21x |
| L | 33.8% | 1.24x |

- chi2=16.12, p=0.001, V=0.075 (modest)

**Finding:** AZC zone variation in headless rate is modest (V=0.075). S-zone is lowest (21.2%), P/L zones highest (~33%). Not a strong differentiator.

### T6: Pipeline Composition (C1527 partial)

| System | Bridge headless% | Dark headless% | Dark/Bridge ratio | chi2 |
|--------|-------------------|----------------|-------------------|------|
| A | 38.6% | 34.8% | 0.90x | 5.45 |
| B | 25.6% | 37.6% | **1.47x** | 114.5 |
| AZC | 29.4% | 21.6% | 0.73x | 9.10 |

**Finding:** B-specific dark headless enrichment (1.47x, p=1.0e-26). A and AZC show the opposite pattern. Dark pipeline's identification function in B specifically uses headless infrastructure vocabulary.

### T7: Terminal Atom Profiles

Cross-system headless terminal JSD: A vs B = 0.012, A vs AZC = 0.038, B vs AZC = 0.017.

Universal headless terminal shifts vs headed:
- **Bare-terminal depleted:** 0.56-0.58x across all systems
- **n-terminal enriched:** 1.55-3.15x across all systems
- **h-terminal enriched:** 1.36-2.66x across all systems

**Finding:** Terminal profile shifts are consistent cross-system. Headless compounds universally avoid bare terminals and enrich n/h terminals.

### T8: Category Profiles (C1526)

| Category | A headless | B headless | AZC headless |
|----------|-----------|-----------|-------------|
| THERMAL | **0.8%** | **1.1%** | **0.6%** |
| STAGING | 35.2% | 30.9% | 32.4% |
| MARKING | 12.8% | 19.5% | 13.5% |
| TRANSITION | 19.7% | 12.1% | 25.4% |

- Cross-system headless category JSD: 0.023-0.035
- Within-system headless-vs-headed JSD: 0.226-0.317

**Finding:** Headless category profile is UNIVERSAL: near-zero THERMAL (0.6-1.1%), high STAGING/MARKING. Cross-system JSD is 6.7-13.8x smaller than within-system headless-vs-headed JSD. Headless compounds perform the same structural function in all systems: infrastructure/identification, never thermal execution.

### T9: MIDDLE Length

| System | Headless mean | Headed mean | p |
|--------|--------------|-------------|---|
| A | 1.93 | 2.30 | 3.2e-92 |
| B | 1.87 | 2.33 | 6.2e-234 |
| AZC | 1.71 | 2.60 | 3.2e-100 |

**Finding:** Headless MIDDLEs are shorter in all systems. AZC shows the largest gap (0.89 chars).

### T10: Type Overlap (C1527)

| Metric | Value |
|--------|-------|
| Unique headless types: A | 395 |
| Unique headless types: B | 484 |
| Unique headless types: AZC | 160 |
| Triple-shared types | 69 |
| A-exclusive types | 250 (63.3%) |
| B-exclusive types | 329 (68.0%) |
| AZC-exclusive types | 63 (39.4%) |
| Triple-shared token coverage: A | 88.0% |
| Triple-shared token coverage: B | 89.0% |
| Triple-shared token coverage: AZC | 88.1% |
| Pairwise Jaccard: A&B | 0.183 |
| Pairwise Jaccard: A&AZC | 0.164 |
| Pairwise Jaccard: B&AZC | 0.158 |

**Finding:** Despite high type-level exclusivity (63-68%), 69 shared types cover 88-89% of tokens. The SHARED_SUBSTRATE_GRADED_SLOTS architecture (C1499) holds for headless compounds: a small shared functional core does the work while system-exclusive types provide low-frequency specialization.

---

## Constraints Produced

| # | Name | Tier | Key Finding |
|---|------|------|-------------|
| C1523 | Currier A headless rate 1.43x higher than B/AZC | 2 | A=39.0% vs B=27.2%/AZC=27.9%; B and AZC indistinguishable |
| C1524 | da/sa/ta PREFIX exclusivity universal across systems | 2 | da enrichment: A=844.6x, B=1448.3x, AZC=132.7x; manuscript-wide grammar rule |
| C1525 | Headless suffix depletion universal across systems | 2 | Headless lower: A=0.73x, B=0.86x, AZC=0.61x; terminal opacity mechanism |
| C1526 | Headless category profile universal across systems | 2 | Near-zero THERMAL (0.6-1.1%), high STAGING/MARKING; cross-system JSD=0.023-0.035 |
| C1527 | Headless functional core shared: 69 types cover 88-89% | 2 | Type exclusivity 63-68% but token mass converges; B-specific dark headless enrichment (1.47x) |

---

## Architectural Implications

1. **Headless is a manuscript-wide structural domain.** The category profile, terminal shifts, suffix depletion, and PREFIX exclusivity rules are identical across A, B, and AZC. This extends C1488 (headless as coherent domain in B) to the entire manuscript.

2. **A's declarative register is headless-heavy.** A's 1.43x headless enrichment (C1523) is the headless side of C1507's HEAD redistribution: A selects arrangement/infrastructure (o-HEAD + headless), B selects execution (e/k-HEAD).

3. **AZC tracks B, not A, for headless rate.** Despite AZC's otherwise A-proximate vocabulary profile (C1522), its headless rate (27.9%) matches B (27.2%), not A (39.0%). AZC is a positional classification system, not a vocabulary register.

4. **Dark-headless affinity is B-specific.** The 1.47x dark headless enrichment in B (C1527) does not hold in A or AZC, confirming that dark pipeline's identification function (C1505) specifically recruits headless infrastructure in the execution grammar.

5. **SHARED_SUBSTRATE_GRADED_SLOTS confirmed for headless.** The same architecture documented in C1499 for the overall atom ontology applies within the headless subdomain: shared core tokens (69 types, 88-89% coverage), system-specific type tails, graded deployment.

---

## Scripts and Data

- Script: `phases/HEADLESS_CROSS_SYSTEM/scripts/headless_cross_system.py`
- Results: `phases/HEADLESS_CROSS_SYSTEM/results/headless_cross_system.json`

---

## Navigation

- Prior phase: [Phase 541: AZC Zone-Level Atomization](../../phases/AZC_ZONE_ATOMIZATION/REPORT.md)
- Constraints: [C1523](../../context/CLAIMS/C1523_currier_a_headless_enrichment.md), [C1524](../../context/CLAIMS/C1524_headless_prefix_exclusivity_universal.md), [C1525](../../context/CLAIMS/C1525_headless_suffix_depletion_universal.md), [C1526](../../context/CLAIMS/C1526_headless_category_profile_universal.md), [C1527](../../context/CLAIMS/C1527_headless_functional_core_shared.md)
