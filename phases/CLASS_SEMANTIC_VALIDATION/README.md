# CLASS_SEMANTIC_VALIDATION Phase

## Purpose

Test Tier 4 speculative role assignments from INSTRUCTION_CLASS_CHARACTERIZATION against corpus structure.

## Status: CLOSED

Phase complete. 16 constraints documented (C547-C562). Expert validated 2026-01-25: all findings consistent with existing constraint system, no conflicts identified. Role taxonomy (CC, EN, FL, FQ, AX) confirmed as capturing real structural distinctions.

## Research Questions

| Question | Status | Finding | Constraint |
|----------|--------|---------|------------|
| Q1a: Gateway line-level | Resolved | No line-level ordering (40.4%) | - |
| Q1b: Gateway folio-level | **DOCUMENTED** | 90.2% co-occur, manuscript arc | C548 |
| Q2: qo-Chain thermal | **DOCUMENTED** | 1.53x REGIME_1 enrichment | C547 |
| Q3: CORE_CONTROL syntax | Resolved | NOT a trigger (baseline-level) | - |
| Q4: Interleaving | **DOCUMENTED** | z=10.27, 56.3% vs 50.6% expected | C549 |
| Q5: Role transitions | **DOCUMENTED** | Self-chaining hierarchy, ENERGY avoidance | C550 |
| Q6: AUXILIARY characterization | Resolved | Heterogeneous residual, not functional role | - |
| Q7: Class universality | **DOCUMENTED** | 67% universal, FLOW depleted in REGIME_1 | C551 |
| Q8: Line length by REGIME | Resolved | No significant difference (p=0.089) | - |
| Q9: Section specialists | **DOCUMENTED** | Distinct section role profiles | C552 |
| Q10: BIO-REGIME correlation | **DOCUMENTED** | Independent additive effects | C553 |
| Q11: Hazard co-occurrence | **DOCUMENTED** | Cluster (1.29x dispersion), 93% lines | C554 |
| Q12: REGIME boundary effects | Resolved | No discontinuity at boundaries (p=0.457) | - |
| Q13: Class 33 anomaly | **DOCUMENTED** | Class 33/34 substitution in PHARMA | C555 |
| Q14: Line-initial patterns | **DOCUMENTED** | ENERGY medial-concentrated | C556 |
| Q15: REGIME_3 homogeneity | Resolved | Partially size artifact, n=8 too small | - |
| Q16: Class 34 token analysis | Resolved | Prefix partition (qo- vs ch-/sh-) | - |
| Q17: daiin opener function | **DOCUMENTED** | 27.7% initial, ENERGY trigger | C557 |
| Q18: REGIME_3 daiin anomaly | Resolved | BIO section composition effect | - |
| Q19: Singleton class analysis | **DOCUMENTED** | 3 singletons, CC dominated | C558 |
| Q20: ol function analysis | Resolved | Confirms C558 complementary pattern | - |
| Q21: FREQUENT role function | **DOCUMENTED** | Morphologically minimal, final-biased | C559 |
| Q22: Class 17 analysis | **DOCUMENTED** | ol-derived control operators | C560 |
| Q23: Class 9 aiin-chaining | **DOCUMENTED** | or->aiin directional bigram | C561 |
| Q24: FLOW role analysis | **DOCUMENTED** | Final-biased hierarchy, PHARMA enriched | C562 |

## Documented Findings

### C547: qo-Chain REGIME_1 Enrichment (Tier 3)
- 313 qo-chains (2+ consecutive Class 32/33/36)
- REGIME_1: 1.53x enrichment (51.4% of chains)
- REGIME_2/3: Depleted (0.42x, 0.55x)

### C548: Manuscript-Level Gateway/Terminal Envelope (Tier 2)
- 90.2% of folios have BOTH gateway and terminal
- rho=0.499 count correlation
- Gateways front-loaded (rho=-0.368)
- Terminal-dominant overall (2.7x more folios)

### C549: qo/ch-sh Interleaving Significance (Tier 2)
- 56.3% interleaving vs 50.6% expected
- z=10.27, p<0.001
- REGIME_3 highest (59.0%), REGIME_4 lowest (52.2%)

### C550: Role Transition Grammar (Tier 2)
- Self-chaining hierarchy: FREQUENT 2.38x > FLOW 2.11x > ENERGY 1.35x
- FLOW-FREQUENT bidirectional affinity: 1.54-1.73x
- ENERGY avoids FLOW (0.75x), FREQUENT (0.71x), UNCLASSIFIED (0.80x)
- REGIME_1 has elevated EN->EN chaining (1.20x vs baseline)

### C551: Grammar Universality and REGIME Specialization (Tier 2)
- 67% of classes (32/48) are universal across all REGIMEs
- CORE_CONTROL most universal (0.836 evenness)
- ENERGY enriched in REGIME_1 (1.26-1.48x)
- FLOW depleted in REGIME_1 (0.40-0.63x)
- Thermal/flow anticorrelation by REGIME

### C552: Section-Specific Role Profiles (Tier 2)
- Sections have distinct role distributions (Chi2=565.8, p<0.001)
- BIO: +CC +EN (thermal-intensive processing, 45.2% ENERGY)
- HERBAL_B: +FQ -EN (repetitive non-thermal)
- PHARMA: +FL (flow-dominated procedures)
- RECIPE_B: -CC (reduced control overhead)

### C553: BIO-REGIME Energy Independence (Tier 2)
- BIO is 70% REGIME_1, but effects are independent
- Additive model: baseline 27.5%, +6.5pp REGIME, +9.8pp section
- Both effects significant (p<0.001) when controlled
- BIO + REGIME_1 = 48.9% ENERGY (highest in manuscript)

### C554: Hazard Class Clustering (Tier 2)
- Hazard classes cluster, not disperse (dispersion index 1.29, p<0.001)
- 93% of lines contain hazard-adjacent classes (mean 3.1/line)
- Gateway-terminal: 1.06x (confirms C548 manuscript-level envelope)
- Hazard management is zone-concentrated

### C555: PHARMA Thermal Operator Substitution (Tier 2)
- Class 33 depleted 0.20x in PHARMA, Class 34 enriched 1.90x
- ~10x divergence between related ENERGY classes
- Section-specific, not REGIME-driven (PHARMA is 84% REGIME_1)
- ENERGY operators are not interchangeable

### C556: ENERGY Medial Concentration (Tier 2)
- ENERGY avoids line boundaries: 0.45x initial, 0.50x final
- FLOW/FREQUENT prefer final: 1.65x, 1.67x
- UNCLASSIFIED prefer initial: 1.55x
- Lines have positional template (Chi2 p=3e-89)

### C557: daiin Line-Initial ENERGY Trigger (Tier 2)
- daiin: 27.7% line-initial (2.2x CC average of 12.5%)
- Class 10 is a singleton (only daiin)
- 47.1% ENERGY followers (1.9x enriched)
- RECIPE: 36.3% initial, highest section
- REGIME_3 anomaly: highest rate but lowest initial

### C558: Singleton Class Structure (Tier 2)
- Only 3 singleton classes: 10 (daiin), 11 (ol), 12 (k)
- 2/3 CORE_CONTROL classes are singletons
- Complementary positions: daiin initial-biased, ol final-biased
- Class 12 (k) has 0 occurrences in Currier B

### C559: FREQUENT Role Structure (Tier 2)
- 35 token types, 1301 occurrences (5.6% of corpus)
- Morphologically minimal (Class 23: d, l, r, s, y, am, dy)
- Final-biased: 19.6% final (3.6x ENERGY)
- HERBAL enriched (1.62x), BIO depleted (0.85x)
- Class 9 exception: self-chains (16.2%), NOT final-biased

### C560: Class 17 ol-Derived Control Operators (Tier 2)
- 9 tokens, ALL have PREFIX=ol (morphologically derived from ol singleton)
- Tokens: olaiin, olchedy, olchey, olkaiin, olkain, olkedy, olkeedy, olkeey, olshedy
- BIO: 1.72x enriched, PHARMA: 0 occurrences (complete avoidance)
- REGIME_3: 1.90x enriched
- Non-singleton CC class is structurally derived from singleton ol

### C561: Class 9 or->aiin Directional Bigram (Tier 2)
- 87.5% of Class 9 chains are or->aiin (42/48)
- Zero aiin->aiin sequences exist
- Bigram functions as grammatical unit, not same-token repetition
- HERBAL: 21.7% chain rate (highest), BIO: 8.8% (lowest)
- Refines C559 "self-chaining" characterization

### C562: FLOW Role Structure (Tier 2)
- 19 tokens, 1078 occurrences (4.7% of corpus)
- Final-biased hierarchy: Class 40 (59.7%) > Class 38 (52.0%) > Class 30 (14.8%) > Class 7 (9.9%)
- Token "ary" is 100% line-final (pure closure signal)
- PHARMA enriched (1.38x), BIO depleted (0.83x)
- ENERGY/FLOW anticorrelation: REGIME_1 has 2x higher EN/FL ratio
- Morphologically unified by ar/al/da elements

## Resolved Questions (No Constraint Needed)

### Q1a: Line-Level Gateway Ordering
- Within-line gateway->terminal order only 40.4%
- Resolved by C548: envelope is manuscript-level, not line-level

### Q3: CORE_CONTROL as Trigger
- 40.6% ENERGY follow-on vs 37.0% baseline
- Only 1.10x enrichment, not significant as trigger
- CORE_CONTROL is NOT positional trigger

### Q6: AUXILIARY Characterization
- AUXILIARY is heterogeneous residual, not coherent functional role
- 2.5x higher token diversity than semantic roles
- 2.4x smaller class size than semantic roles
- Strong ENERGY co-occurrence (62-70%)
- Definitional, not constraint-worthy

### Q8: Line Length by REGIME
- No significant difference (Kruskal-Wallis p=0.089)
- All REGIMEs: mean 9.3-9.8 words/line
- 75-82% of lines are "long" (8+ words)
- REGIMEs differ in WHAT operations, not HOW MANY

### Q12: REGIME Boundary Effects
- No discontinuity at REGIME transitions (p=0.457)
- Boundary mean absolute ENERGY jump: 8.2%
- Non-boundary jump: 8.2% (identical)
- REGIME is aggregate tendency, not hard mode switch

### Q15: REGIME_3 Homogeneity
- REGIME_3 has only 8 folios (vs 23-27 for others)
- Bootstrap-adjusted: still 1.8x more homogeneous
- But n=8 is too small for confident conclusion
- ENERGY range 16.7% vs 27-30% for others

### Q16: Class 34 Token Analysis
- Class 33 and 34 are perfectly partitioned by PREFIX
- Class 33: 100% qo- prefix (13 token types)
- Class 34: 100% ch-/sh- prefix (19 token types)
- PHARMA substitution from C555 is prefix-family selection
- No new constraint needed - elaborates existing C555

### Q18: REGIME_3 daiin Anomaly
- REGIME_3 daiin: 11.9% initial vs 29.4% other REGIMEs
- BIO section in REGIME_3: 0% initial (21 daiin, all non-initial)
- Composition effect: REGIME_3 is 50% BIO by daiin count
- Other sections in REGIME_3 have normal rates (16-27%)
- Small sample (n=42) limits confidence

### Q20: ol Function Analysis
- ol: 5.2% initial, 9.5% final (confirms C558)
- ol is pure MIDDLE (no prefix/suffix) vs daiin (PREFIX + MIDDLE)
- ENERGY follows ol: 31.8% (vs 47.1% for daiin)
- daiin-ol co-occurrence: only 42 lines (1.7%)
- When both appear: daiin before ol 57.1%
- Confirms complementary CC operator pair from C558

## Scripts

| Script | Status | Output |
|--------|--------|--------|
| hazard_gateway_localization.py | Complete | hazard_gateway_localization.json |
| qo_chain_thermal_test.py | **C547** | qo_chain_thermal.json |
| core_control_syntax.py | Complete | core_control_syntax.json |
| core_control_baseline.py | Complete | core_control_baseline.json |
| folio_envelope_test.py | **C548** | folio_envelope_test.json |
| interleaving_significance.py | **C549** | interleaving_significance.json |
| role_transition_matrix.py | **C550** | role_transition_matrix.json |
| auxiliary_characterization.py | Complete | auxiliary_characterization.json |
| class_regime_universality.py | **C551** | class_regime_universality.json |
| line_length_by_regime.py | Complete | line_length_by_regime.json |
| section_specialists.py | **C552** | section_specialists.json |
| bio_regime_correlation.py | **C553** | bio_regime_correlation.json |
| hazard_class_cooccurrence.py | **C554** | hazard_class_cooccurrence.json |
| regime_boundary_effects.py | Complete | regime_boundary_effects.json |
| class33_anomaly.py | **C555** | class33_anomaly.json |
| line_initial_patterns.py | **C556** | line_initial_patterns.json |
| regime3_homogeneity.py | Complete | regime3_homogeneity.json |
| class34_token_analysis.py | Complete | class34_token_analysis.json |
| daiin_opener_function.py | **C557** | daiin_opener_function.json |
| regime3_daiin_anomaly.py | Complete | regime3_daiin_anomaly.json |
| singleton_class_analysis.py | **C558** | singleton_class_analysis.json |
| ol_function_analysis.py | Complete | ol_function_analysis.json |
| frequent_role_analysis.py | **C559** | frequent_role_analysis.json |
| class17_analysis.py | **C560** | class17_analysis.json |
| class9_chaining_analysis.py | **C561** | class9_chaining_analysis.json |
| flow_role_analysis.py | **C562** | flow_role_analysis.json |

## Potential Next Tests

1. **Phase summary** - Consolidate findings into role taxonomy
2. **AUXILIARY deep-dive** - Further characterize residual category (if warranted)

## Role Taxonomy Summary

All 5 roles now characterized:

| Role | Classes | Findings | Key Constraint |
|------|---------|----------|----------------|
| CORE_CONTROL | 10, 11, 12, 17 | 3 singletons (daiin, ol, k), Class 17 ol-derived | C558, C560 |
| ENERGY | 32, 33, 34, 36, etc. | Medial-concentrated, REGIME_1 enriched, prefix-partitioned | C551, C555, C556 |
| FLOW | 7, 30, 38, 40 | Final-biased hierarchy, ary=100% final, PHARMA enriched | C562 |
| FREQUENT | 9, 20, 21, 23 | Morphologically minimal, final-biased, Class 9 or->aiin bigram | C559, C561 |
| AUXILIARY | Residual | Heterogeneous, high diversity, ENERGY co-occurrence | Q6 (no constraint) |
