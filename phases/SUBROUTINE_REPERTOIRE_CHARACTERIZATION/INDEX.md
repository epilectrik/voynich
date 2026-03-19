# Phase 608: SUBROUTINE_REPERTOIRE_CHARACTERIZATION

**Status:** COMPLETE
**Verdict:** REPERTOIRE_STRUCTURED_PREFIX_MEDIATED
**Constraints:** C1761-C1763
**Script:** `scripts/subroutine_repertoire.py` (runtime ~45s)
**PREDICTIONS.md SHA-256:** `670b31d3ca5ee562f00f94a59c9e09683240d5da318aa902a2db8c3113a984e9`

## Motivation

The pre-phase null test established that folio zone repertoire breadth is significantly narrower than chance (observed 1.675 vs expected 2.153, z=-0.781, t=-7.112, p<0.0001). Folios actively select specific paragraph subroutine types and exclude others. This phase characterizes the structure of that selection.

**Interpretive caveat:** C1398 zone assignments have low silhouette (0.113). Zones are gradient regions, not crisp types. Repertoire should be interpreted as co-occurrence of dominant paragraph emphases, not hard ontological paragraph species.

## Results Summary

### T1: Pairwise Zone Co-Occurrence (Section-Stratified Null, Multi-Paragraph)

| Pair | Observed | Expected | O/E | p | Sig |
|------|----------|----------|-----|---|-----|
| TQ-MP | 5 | 13.2 | 0.378 | 0.0000 | YES |
| CS-MP | 6 | 12.6 | 0.477 | 0.0034 | YES |
| TQ-CS | 13 | 20.6 | 0.632 | 0.0022 | YES |
| TQ-OI | 16 | 22.7 | 0.705 | 0.0042 | YES |
| CS-OI | 14 | 17.7 | 0.789 | 0.1170 | no |
| OI-MP | 14 | 18.4 | 0.762 | 0.0612 | no |

4/6 pairs significantly depleted under section-stratified null (Bonferroni alpha=0.0083). ALL pairs show depletion, none enriched. Folios strongly prefer mono-zone or narrow repertoires even after section ecology is controlled.

**Strongest signal:** THERMAL-MONITORING mutual exclusion (O/E=0.378) extends C1399's transition-level avoidance to the folio repertoire level. CONTAINMENT-MONITORING also strongly depleted (O/E=0.477).

**Pattern:** MONITORING-Phase is the most exclusionary zone — it avoids both THERMAL and CONTAINMENT at the repertoire level. OPERATION-Iteration is the most permissive — its pairs (CS-OI, OI-MP) are the weakest depletions.

### T2: Repertoire Typology

| Signature | Zones | Count |
|-----------|-------|-------|
| 0100 | CS only | 22 |
| 0010 | OI only | 8 |
| 1000 | TQ only | 8 |
| 1100 | TQ+CS | 7 |
| 1010 | TQ+OI | 7 |
| 1110 | TQ+CS+OI | 6 |
| 0011 | OI+MP | 6 |
| 0111 | CS+OI+MP | 5 |
| 1011 | TQ+OI+MP | 3 |
| 0110 | CS+OI | 3 |
| 1001 | TQ+MP | 2 |
| 0001 | MP only | 2 |
| 0101 | CS+MP | 1 |

13 of 15 possible signatures observed. Only "TQ+MP only" (1001 minus others) and "all four" (1111) are absent.

- Entropy: 3.303 bits (84.5% of max)
- Below section-stratified null (3.463): p=0.012
- CONTAINMENT-Sealing mono-type dominates (22/80 = 27.5% of all folios)

### T3: Nested Model Comparison

| Feature | dR2 | F | F_p | perm_p | KW_p (raw) | Sig |
|---------|-----|---|-----|--------|-------------|-----|
| **h_ratio** | **0.319** | **4.806** | **0.0001** | **0.001** | 0.0000 | **YES** |
| thermo_ke | 0.086 | 1.451 | 0.196 | 0.171 | 0.0002 | no |
| strong_close_frac | 0.085 | 0.839 | 0.573 | 0.445 | 0.275 | no |
| cei_total | 0.075 | 1.221 | 0.304 | 0.418 | 0.647 | no |
| link_density | 0.064 | 1.294 | 0.265 | 0.366 | 0.002 | no |

Model: rank(feature) ~ qo_frac + chsh_frac + bare_frac + section + paragraph_count [+repertoire_type]

**Key finding:** h_ratio shows 31.9% additional explained variance from repertoire type beyond PREFIX + section + paragraph_count (F=4.806, p=0.0001; permutation p=0.001). This means repertoire type carries independent information about monitoring balance that PREFIX composition alone does not capture.

thermo_ke and link_density show strong raw KW effects but are fully absorbed by PREFIX + section controls (not significant after nesting). This is the PREFIX confound the crazy-expert predicted.

Only 1/5 features reaches the INDEPENDENTLY_INFORMATIVE threshold (needed >=2), so the verdict remains PREFIX_MEDIATED. But the h_ratio signal is genuine and notable.

### T4: Section x Repertoire (Descriptive)

- Chi2=140.06, p<0.0001, Cramer's V=0.662
- Section strongly predicts repertoire (expected per C1569)
- Per-section entropy: Stars 2.94 > Biologicals 2.24 > Herbal 1.73 > Cosmological 1.52
- Stars has the most diverse repertoire (surprise — predicted Herbal)

### T5: Mono-Type Characterization

| Zone | All mono (n=40) | Genuine mono (2+ par, n=17) |
|------|-----------------|----------------------------|
| THERMAL-QO | 8 | 8 |
| CONTAINMENT-Sealing | 22 | 6 |
| OPERATION-Iteration | 8 | 2 |
| MONITORING-Phase | 2 | 1 |

CONTAINMENT-Sealing dominates overall mono-type (22/40) because 16 of its 22 are single-paragraph folios (forced mono). Among genuine 2+-paragraph mono-types, THERMAL-QO leads (8/17).

Mono vs multi-type differences (MW):
- thermo_ke: mono=0.018, multi=0.025, p=0.008 (mono lower)
- cei_total: mono=0.592, multi=0.527, p=0.042 (mono higher)
- h_ratio, strong_close_frac, link_density: not significant

Within mono-type KW (across zone identities):
- thermo_ke: H=15.98, p=0.001 (zones differ)
- h_ratio: H=13.85, p=0.003 (zones differ)
- link_density: H=13.81, p=0.003 (zones differ)

## Prediction Outcomes

| # | Prediction | Outcome |
|---|-----------|---------|
| P1 | TQ-MP depleted (section-strat, p<0.0083) | **PASS** (O/E=0.378, p<0.001) |
| P2 | Entropy below section null + <8 sigs with n>=3 | **FAIL** (below null=yes, but 10 sigs with n>=3) |
| P3 | Repertoire null after controls (0/5 sig) | **FAIL** (1/5 sig — h_ratio surprise) |
| P4 | Section assoc + Herbal max entropy | **FAIL** (assoc=yes, but Stars has max entropy) |
| P5 | TQ most common genuine mono-type | **PASS** (8/17) |
| P6 | Mono vs multi differ on >=2 features | **PASS** (2/5: thermo_ke, cei_total) |

3/6 predictions pass. Two failures are in the "interesting surprise" direction (P3: h_ratio independently informative; P4: Stars most diverse, not Herbal).

## Findings

### F1: Universal zone-pair depletion at folio level
All 6 zone pairs show depletion (O/E < 1.0), 4/6 significant under section-stratified null. Folios prefer narrow subroutine repertoires. This is not a section artifact — it survives within-section permutation. Strongest: THERMAL-MONITORING (O/E=0.378) and CONTAINMENT-MONITORING (O/E=0.477). MONITORING is the most exclusionary zone.

### F2: h_ratio independently predicted by repertoire type
After controlling PREFIX + section + paragraph_count, repertoire type explains 31.9% additional variance in h_ratio (p=0.001 permutation). This is the only feature surviving full controls. Interpretation: the monitoring-execution balance (h-kernel ratio) is not fully determined by token-level PREFIX composition or section membership — the specific combination of paragraph emphasis zones within a folio carries additional information about what monitoring regime the folio operates under.

### F3: PREFIX absorbs most repertoire-feature correlations
4/5 features (thermo_ke, strong_close_fraction, cei_total, link_density) that show raw KW significance are fully explained by PREFIX + section + paragraph_count. The PREFIX confound predicted by the crazy-expert is confirmed for these features.

### F4: CONTAINMENT-Sealing is the default mono-type
55% of all mono-type folios (22/40) are CS. Most are single-paragraph (Herbal) folios, explaining Herbal's low repertoire entropy (1.73 bits). Among genuine 2+-paragraph mono-types, THERMAL-QO leads.

### F5: Stars has highest repertoire diversity
Stars section entropy = 2.94 bits (highest of all sections), contradicting the prediction of Herbal. Stars folios use more diverse subroutine combinations despite being operationally specialized (thermo-monitoring axis per C1752, C1755).

## Constraints

### C1761: Folio-Level Zone Co-Occurrence Universal Depletion
**Tier 2 | Scope: B**

All 6 zone-type pairs show depletion at the folio repertoire level (O/E 0.378-0.789). 4/6 survive Bonferroni-corrected section-stratified null (alpha=0.0083). THERMAL-MONITORING (O/E=0.378) and CONTAINMENT-MONITORING (O/E=0.477) are most depleted. MONITORING-Phase is the most exclusionary zone type. No zone pair shows enrichment. Folios actively restrict their paragraph zone repertoire beyond what section ecology predicts.

### C1762: Repertoire Typology and Mono-Type Prevalence
**Tier 2 | Scope: B**

13 of 15 possible binary zone signatures observed (absent: TQ+MP only, all-four). Entropy 3.303 bits (84.5% max), significantly below section-stratified null (p=0.012). 50% of folios are mono-type. CONTAINMENT-Sealing dominates overall mono-type (22/40) due to Herbal single-paragraph folios. Among genuine 2+-paragraph mono-types, THERMAL-QO leads (8/17). Stars has highest repertoire entropy (2.94 bits), Herbal lowest (1.73 bits). Mono-type folios have lower thermo_ke (p=0.008) and higher CEI (p=0.042) than multi-type.

### C1763: Repertoire Independently Predicts h_ratio
**Tier 2 | Scope: B**

Repertoire type explains 31.9% additional variance in h_ratio beyond PREFIX fractions + section + paragraph_count (nested F=4.806, p=0.0001; permutation p=0.001). This is the only feature (of 5 tested) surviving full controls. Interpretation: the monitoring-execution balance is not fully captured by token-level PREFIX composition — paragraph-level zone combination carries independent information. For 4/5 other features (thermo_ke, strong_close_fraction, cei_total, link_density), PREFIX + section fully absorbs repertoire effects, confirming the PREFIX confound predicted by the constraint system (C1405-C1431).
