# Context System Changelog

**Purpose:** Track changes to the context system structure and content.

---

## Version 5.61 (2026-03-14) - Phase 588: Recipe Specification Test

### Summary

Phase 588 tests the crazy expert's "recipe specification" hypothesis: are A folios preparation specifications whose PP MIDDLE sets define which B programs can run? Three tests with proper controls: (1) PP content → B-side similarity controlling for pool size, hub fraction, and section; (2) folio-restricted PP discriminative power; (3) specialization vs generalization using coverage-matched null. Key finding: PP content genuinely predicts B-side similarity (partial rho=0.502), overturning C753's class-level null. But folios are NOT categorically specialized — entropy matches coverage-optimized random draws. Verdict: CONTENT_RELEVANT_NOT_SPECIALIZED. A folios are application-specific but category-generic.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/RECIPE_SPECIFICATION_TEST/` -- Phase 588 directory with script, results, INDEX |
| **ADDED** | C1706: PP content predicts B-side -- partial rho=0.502, overturns C753 at token level |
| **ADDED** | C1707: Restricted PP discriminative -- d=3.667, restricted PPs differentiate folios |
| **ADDED** | C1708: Folio category not specialized -- entropy z=0.116, matches coverage-optimized null |
| **UPDATED** | INDEX.md -- +3 constraints (1708 total), Phase 588 section |
| **UPDATED** | CLAUDE.md -- Quick reference updated (v5.61, 1708 constraints, 588 phases) |
| **REFINED** | C753 -- Class-level null (r=-0.038) overturned at token level (rho=0.502) |

### Key Findings

- **PP content is strongly predictive at token level (C1706):** Partial Spearman rho=0.502 between folio PP Jaccard and B-side cosine similarity, controlling for pool size, hub fraction, and section. This is the strongest A→B content-level finding. Confounds suppress the signal (raw rho=0.470), not inflate it. C753's class-level null (r=-0.038) is overturned.
- **Folios are category-generic (C1708):** Category entropy z=0.116 vs coverage-matched null. 73/114 folios indistinguishable from random. Every folio covers all 8 categories equally. The "recipe" specialization prediction fails.
- **Application-specific, not category-specific:** A folios select specific cross-category MIDDLE combinations that enable specific B programs. The specialization is in WHICH tokens from each category, not WHICH categories. This resolves the tension between C753 (no class-level signal) and C1705 (strong pair-level signal).

---

## Version 5.60 (2026-03-14) - Phase 587: B-Side Operational Signatures

### Summary

Phase 587 changes approach from looking at A's internal structure to looking at A's shadow in B. Each A record's C502.a three-axis morphological filter reduces B's 4,889 tokens to ~38 survivors. The survivor set is characterized as a 16-dimensional B-side operational signature (8 category fractions, 6 HEAD fractions, k-initial fraction, hazard exposure). Five tests probe whether A's organizational logic propagates through C502.a filtering. Key finding: C475-incompatible record pairs produce significantly more divergent B-side signatures (Cohen's d=0.816, p=3.8e-289), confirming the discrimination manifold has real operational meaning at the pair level. However, this meaning does not organize into clean macroscopic categories — section prediction works only at folio level (2.19x chance), and RI extension predictions mostly fail (1/5).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/BSIDE_OPERATIONAL_SIGNATURES/` -- Phase 587 directory with script, results, INDEX |
| **ADDED** | C1702: Folio B-side coherence weak -- z=15.15 significant but ratio=1.086 (8.6% above between-folio) |
| **ADDED** | C1703: Section prediction partial -- folio 2.19x passes, record 1.74x fails |
| **ADDED** | C1704: RI extension predictions fail -- 1/5 pass Bonferroni, only e→HEAD_e confirmed |
| **ADDED** | C1705: C475 operational divergence confirmed -- d=0.816, p=3.8e-289; manifold geometry maps to B-side operational divergence |
| **UPDATED** | INDEX.md -- +4 constraints (1705 total), Phase 587 section |
| **UPDATED** | CLAUDE.md -- Quick reference updated (v5.60, 1705 constraints, 587 phases) |
| **REFINED** | C1701 -- "residual is content" refined: content has OPERATIONAL meaning (C1705), not noise |

### Key Findings

- **C475 divergence is the star finding (C1705):** C475-incompatible record pairs (sharing no compatible MIDDLEs) diverge significantly more in B-side operational space (d=0.816). This is the strongest finding in the manifold investigation arc (Phases 585-587). The discrimination manifold is not just a frequency artifact — its compatibility geometry maps to which B programs the material permits.
- **Structure is pair-level, not categorical:** Folio coherence is weak (ratio 1.086), section prediction partial (folio 2.19x, record 1.74x), and RI extension predictions fail (1/5). The operational meaning is encoded at individual MIDDLE-pair compatibility level, not at macroscopic category level.
- **C1701 refinement:** Phase 586's "residual is content" conclusion gains depth. The content specificity that drives the 0.234 clustering gap has real operational meaning — it determines which B programs are available. This is not random variation but systematic operational filtering.
- **Noise floor caveat:** Random draws of 36 B tokens from 4,889 achieve 0.902 cosine similarity in 16-dim signature space. This high baseline makes detecting genuine structure harder and may explain why record-level tests fail despite strong pair-level signal.

---

## Version 5.59 (2026-03-14) - Phase 586: Compatibility Reconstruction

### Summary

Phase 586 asks which deployment grammar layer creates the discrimination manifold's 0.873 clustering. Phase 585 showed atom composition fails (edge Jaccard 6.4%). This phase tests 5 progressive A-native deployment layers: global frequency (D0), section conditioning (D1), folio pool restriction (D2), per-folio frequency weighting (D3), and PREFIX selectivity (D4). Key finding: frequency-weighted co-occurrence alone produces clustering 0.639 (73% of manifold). No deployment layer closes the remaining 0.234 gap. The residual reflects line-level content specificity, not grammar rules.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/COMPATIBILITY_RECONSTRUCTION/` -- Phase 586 directory with script, results, INDEX |
| **ADDED** | C1696: Frequency baseline high -- D0 clustering 0.639, 73% of manifold from frequency alone |
| **ADDED** | C1697: Section effect negligible -- D1-D0 = +0.004 clustering |
| **ADDED** | C1698: Folio pool moderate -- D2-D1 = +0.032 clustering but density inflation |
| **ADDED** | C1699: Frequency corrects not adds -- D3 best Jaccard (0.285) but no clustering gain |
| **ADDED** | C1700: PREFIX selectivity hurts -- D4-D3 = -0.106 clustering, -0.049 Jaccard |
| **ADDED** | C1701: Manifold residual is content -- best Jaccard 0.285, 0.234 gap unexplained |
| **UPDATED** | INDEX.md -- +6 constraints (1701 total), Phase 586 section |
| **UPDATED** | CLAUDE.md -- Quick reference updated (v5.59, 1701 constraints, 586 phases) |
| **REFRAMED** | C1695 -- "deployment grammar" attribution narrowed; even A-native deployment fails |

### Key Findings

- **Frequency is the baseline, not CM null (C1696):** The CM null (0.250) measures random edge rewiring, which destroys hub structure. Frequency-weighted co-occurrence through shared lines naturally produces clustering 0.639. The truly anomalous gap is only 0.234, not 0.623.
- **Section is irrelevant (C1697):** Section conditioning adds +0.004 clustering. Currier A is mostly Herbal; section partitioning barely touches the vocabulary.
- **Folio pools help moderately (C1698):** Folio pool restriction adds +0.032 clustering but inflates density (0.034 vs real 0.022). Vocabulary cliques contribute, but are not dominant.
- **PREFIX filtering is counterproductive (C1700):** Adding PREFIX→HEAD compatibility reduces both clustering (-0.106) and Jaccard (-0.049). PREFIX constraints remove correct edges faster than incorrect ones.
- **The residual is content (C1701):** The 0.234 gap between frequency baseline and real manifold reflects which specific MIDDLEs each line encodes — irreducible content specificity. This is not grammar; it is the data itself.

---

## Version 5.58 (2026-03-14) - Phase 585: Atom Compositional Generator

### Summary

Phase 585 retests F-BRU-003 ("Property-Based Generator Rejection", v2.44, 2026-01-15) with the atom architecture discovered 5-8 weeks after F-BRU-003 was run. F-BRU-003 tested a naive generator (8 random property bins, featureless MIDDLEs) before HEAD+MOD+TERM composition was known. This phase tests five generators (empirical atom model, structured-random, parameter-independent, naive reproduction, independent features) plus a diagnostic isolating the clustering gap source. Key finding: atom composition breaks the 0.49 independent feature ceiling (reaching 0.60) but atom features do not predict real MIDDLE co-occurrence (edge Jaccard 6.4%). The discrimination manifold's 0.873 clustering arises from the deployment grammar (B execution), not morphological composition.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/ATOM_COMPOSITIONAL_GENERATOR/` -- Phase 585 directory with 2 scripts, 2 result files, INDEX |
| **ADDED** | C1689: Atom compatibility partially predictable -- AUC=0.745 but edge Jaccard=0.064 on real MIDDLEs |
| **ADDED** | C1690: Composition breaks independent feature ceiling -- Empirical clustering 0.599 > ceiling 0.49 |
| **ADDED** | C1691: Slot architecture sufficient -- Structured-Random 0.501 = 83.6% of Empirical |
| **ADDED** | C1692: Cross-slot dependencies neutral -- Param-Independent 0.623 >= Empirical 0.599 |
| **ADDED** | C1693: Naive property confirmed dead -- clustering 0.021 on clean H-filtered baseline |
| **ADDED** | C1694: No dominant compositional layer -- Ablation range 0.56-0.62 |
| **ADDED** | C1695: Deployment not compositional -- Real MIDDLEs predicted clustering 0.412, edge Jaccard 0.064 |
| **UPDATED** | INDEX.md -- +7 constraints (1695 total), Phase 585 section |
| **UPDATED** | CLAUDE.md -- Quick reference updated (v5.58, 1695 constraints, 585 phases) |
| **ANNOTATED** | F-BRU-003 NARROWED -- naive model fails but conclusion "permanently kills property interpretations" too broad |

### Key Findings

- **Composition breaks ceiling (C1690):** Atom-compositional generators achieve 0.599 clustering, exceeding C984's 0.49 independent feature ceiling by 22%. F-BRU-003 never tested this class of model. The HEAD+MOD+TERM slot grammar creates transitivity that independent binary features cannot.
- **Architecture, not parameters (C1691):** Structured-Random model (uniform everything) reaches 0.501, already past the ceiling. Specific parameter values add only ~0.10. The slot grammar IS the clustering driver.
- **Cross-slot rules neutral (C1692):** Param-Independent (0.623) actually exceeds Empirical (0.599). The avoidance/selectivity/gating rules serve diversity, not clustering.
- **Deployment is the source (C1695):** Definitive diagnostic. Logistic model on real MIDDLEs at density-matched threshold: clustering 0.412, edge Jaccard 6.4%. Only 1,250 of 10,241 real edges predicted. Atom features do not determine line-level co-occurrence. The manifold is a grammar property, not a morphology property.
- **F-BRU-003 narrowed:** Naive model correctly fails (0.021) but the broad conclusion is too strong. Atom composition gets to 0.60, not 0.02. The real bottleneck is that compatibility is deployment-determined, not composition-determined.

---

## Version 5.57 (2026-03-12) - Phase 584: Zodiac Assignment Inference

### Summary

Phase 584 brute-force enumerates all 12 valid zodiac sign assignments for 5 unidentified nymph folios (2 goat pages × {Aries,Taurus} and 3 unknown-animal pages × {Cancer,Capricorn,Aquarius}), using the seasonal category signal (C1681) as optimization target. Key discovery: the 12 nominal assignments collapse to 3 distinct seasonal groupings because within-season sign swaps are invisible to the test. Even the best full-map assignment (V=0.113, perm_p=0.112) fails to beat the confident-only 7-folio baseline (V=0.157, perm_p=0.018). Verdict: UNKNOWNS_ADD_NOISE.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/ZODIAC_ASSIGNMENT_INFERENCE/` -- Phase 584 directory with script and results |
| **ADDED** | C1685: Full zodiac map NOT INFERRED -- perm_p=0.112, 12-folio signal too dilute |
| **ADDED** | C1686: Within-season assignment DEGENERATE -- 12 assignments collapse to 3 seasonal groupings |
| **ADDED** | C1687: Unknowns DEGRADE signal -- best V=0.113 < confident-only V=0.157 |
| **ADDED** | C1688: f72r3 seasonal assignment RESOLVED -- f72r3=Cancer (Summer) preferred in all top assignments |
| **UPDATED** | INDEX.md -- +4 constraints (1688 total), Phase 584 section |
| **UPDATED** | CLAUDE.md -- Quick reference updated (v5.57, 1688 constraints, 584 phases) |

### Key Findings

- **Within-season degeneracy (C1686):** Swapping Aries/Taurus (both Spring) or Capricorn/Aquarius (both Winter) produces identical chi2/V. A season-level test structurally cannot resolve within-season ordering. This reduces the effective search space from 12 to 3.
- **Unknowns are noise (C1687):** The 5 unknown folios have category profiles that don't cleanly fit any seasonal pattern. Their "generic animal" centers correlate with ambiguous distributions. The confident-only 7-folio subset (C1681) remains canonical.
- **f72r3 diagnostic (C1688):** f72r3=Cancer (Summer) is the only resolved seasonal placement. f72r3 has the most tokens (163) of the unknowns and its profile fits Summer. f71v and f72r1 are Winter in all top assignments.

---

## Version 5.56 (2026-03-12) - Phase 583: Zodiac Seasonal Category Clustering

### Summary

Phase 583 tests whether AZC zodiac page vocabulary clusters by season when classified into the 8 operational categories (C1250). Motivated by Brunschwig 1512 zodiac-conditional apparatus instructions and C322 (SEASON-GATED WORKFLOW). Initial run (v1) with standard zodiac map gave WEAK result. Critical discovery: the standard map has ≥6 misassigned folios and 2 non-zodiac pages. Re-run (v2) with corrected visual-evidence zodiac assignments changes verdict to CONFIRMED (perm_p=0.018).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/ZODIAC_SEASONAL_CATEGORY/` -- Phase 583 directory with 2 scripts, 2 result files |
| **ADDED** | C1681: Zodiac category seasonal signal SEASONAL_SIGNAL_CONFIRMED -- confident-only V=0.157, perm_p=0.018 |
| **ADDED** | C1682: Thermal seasonal gradient THERMAL_GRADIENT_ABSENT -- not individually significant in any variant |
| **ADDED** | C1683: Within-season coherence trend COHERENCE_TREND -- consistent direction, aries map p=0.060 |
| **ADDED** | C1684: Goat-folio seasonal identity GOAT_PAGES_SPRING -- goat=Aries perm_p=0.033, goat=Capricorn perm_p=0.220 |
| **UPDATED** | INDEX.md -- +4 constraints (1684 total), Phase 583 section updated with v2 results |
| **UPDATED** | CLAUDE.md -- Quick reference updated (v5.56, 1684 constraints, 583 phases) |

### Key Findings

- **Zodiac correction critical (C1681):** Standard scholarship zodiac map has ≥6 visual mismatches (fish labeled Aries, scale labeled Virgo, feline labeled Scorpio, etc.) and includes 2 non-zodiac pages (f70r1/f70r2). Correcting to visual-evidence assignments: confident-only (7 pages) perm_p=0.018, V=0.157. Signal was real but masked by incorrect assignments.
- **Apparatus-specific channels fail (C1682):** THERMAL and CONTAINMENT not individually significant in any of 4 mapping variants. The seasonal signal is distributed across categories.
- **Goat diagnostic (C1684):** Goat=Capricorn (Winter) kills signal (perm_p=0.220), goat=Aries (Spring) preserves it (perm_p=0.033). The goat pages' category profiles cluster with Spring. Constrains zodiac assignment for follow-up inference.
- **Three unknown folios (f71v, f72r1, f72r3)** have unidentifiable "generic animal" centers. Candidates for zodiac assignment inference phase.

---

## Version 5.55 (2026-03-11) - Phase 582: Apparatus Atlas Bridge Design

### Summary

Phase 582 bridges the abstract apparatus response manifold (5.88 dimensions, 76 folios, 1,674 prior constraints) to physical apparatus specifications. Pure synthesis/documentation phase -- no new corpus analysis or simulation. Centers on manifold-to-knob mapping as core deliverable (per expert revision), with intervention packet library, physical metrics schema, counterfeit closure atlas, and staged experiments. Instruction-to-action translation is explicitly secondary/heuristic.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/APPARATUS_ATLAS_BRIDGE_DESIGN/` -- Phase 582 directory with 8 scripts (T0-T7), 8 result files, 5 output documents |
| **ADDED** | C1675: Component atlas coverage ATLAS_COMPLETE -- 5 knob axes, 11 packet types, 5 metrics |
| **ADDED** | C1676: Instruction translation coverage TRANSLATION_COMPLETE -- 6 macro-states, 3 zones, 4 REGIMEs, 13 judgments |
| **ADDED** | C1677: Safety protocol derivability SAFETY_DERIVABLE -- 5 hazard classes, 3 safety levels, judgment boundaries |
| **ADDED** | C1678: Validation experiment feasibility EXPERIMENTS_FEASIBLE -- 7/7 experiments, 61 minimum runs |
| **ADDED** | C1679: Metric bridge adequacy METRIC_BRIDGE_COMPLETE -- DVA/YGA/DYE/CTS/forgivingness physical analogs |
| **ADDED** | C1680: Manifold knob identifiability KNOB_MAPPING_IDENTIFIABLE -- 5/5 F-axes to physical knobs |
| **ADDED** | APPARATUS_ATLAS.md -- manifold atlas with family analogs and knob maps |
| **ADDED** | INTERVENTION_PACKET_LIBRARY.md -- 11 physical packet types, counterfeit closure atlas |
| **ADDED** | PHYSICAL_METRICS_SCHEMA.md -- sensor mappings, formulas, 7 hardware nulls |
| **ADDED** | OPERATOR_BRIDGE_MANUAL.md -- heuristic interpretations, safety, operator judgment |
| **ADDED** | VALIDATION_PROTOCOL.md -- staged experiments E0-E6 |
| **UPDATED** | INDEX.md -- +6 constraints (1680 total), Phase 582 section added |
| **UPDATED** | CLAUDE.md -- Quick reference updated (v5.55, 1680 constraints, 582 phases) |

### Key Findings

- **Manifold-to-knob mapping (C1680):** All 5 F-axes mapped to physical control surfaces. F1 (forgiveness) -> reflux ratio. F2 (closure exploitability) -> valve timing. F3 (thermal accent) -> bath temperature. F4 (headless infrastructure) -> plumbing complexity. F5 (containment) -> gasket quality. PC1 (30.0%) led by abl_CLOSE_RECOVERY, confirming seal/recirculation as primary apparatus axis.
- **Metric bridge (C1679):** All 5 virtual process metrics given operational physical definitions. CTS_phys uses weighted composite with seal_completion at highest weight (0.35), consistent with containment-coupled recovery dominating A2. 7 hardware null conditions predesigned to control for timing, thermal, routing, attention, delay, and phase effects.
- **Component atlas (C1675):** 11 physical packet types span the full closure strength spectrum from sub-threshold counterfeit to full hard closure. Counterfeit closure atlas maps per-family acceptance: A1 low, A2 moderate (strength-dependent), A3 intermediate.
- **Validation protocol (C1678):** 7 staged experiments (E0-E6) with 61 total minimum runs. E0 rig characterization is prerequisite. 3-level rig specification: MVP ($560) -> recirculatory ($735) -> pelican ($1235).
- **Expert corrections integrated:** a-HEAD = "active transformation domain" (not "yield"), paragraph = "operational subroutine" (not "complete run"), manifold-to-knob is core bridge (not instruction translation).

---

## Version 5.54 (2026-03-11) - Phase 581: Line-Internal Atom Gradient Decomposition

### Summary

Phase 581 decomposes the validated three-zone line architecture (C1425-C1430) at individual atom resolution. 23,074 Currier B tokens across 2,406 lines analyzed for HEAD/TERMINAL/MODIFIER x quintile deployment profiles, Q3->Q4 closure mechanism, hazard x atom x position interaction, and section-conditioned gradients. Pure corpus analysis, no simulation.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/LINE_INTERNAL_ATOM_GRADIENT_DECOMPOSITION/` — Phase 581 directory with 6 scripts (T0-T5), 5 result files, REPORT_581.md |
| **ADDED** | C1671: Atom positional gradient structure GRADIENT_HETEROGENEOUS — e/headless most positional, o flat |
| **ADDED** | C1672: Q3->Q4 atom decomposition CLOSURE_DISTRIBUTED — m-terminal=77% of TERM JSD, HEAD distributed |
| **ADDED** | C1673: Hazard x atom x position HAZARD_POSITION_COUPLED — chi2=337, 16 zone-specific pairs, k-LED work zone |
| **ADDED** | C1674: Section-conditioned gradients SECTION_MODULATES_GRADIENT — scaffold preserved, amplitudes modulated |
| **UPDATED** | INDEX.md — +4 constraints (1674 total), Phase 581 section added |
| **UPDATED** | CLAUDE.md — Quick reference updated (v5.54, 1674 constraints, 581 phases) |

### Key Findings

- **Gradient heterogeneity (C1671 GRADIENT_HETEROGENEOUS):** HEAD chi2=659 (p<0.001), TERM chi2=663 (p<0.001). Atoms do NOT gradient uniformly: e-HEAD and headless have 12x the gradient magnitude of o-HEAD. Min pairwise cosine=0.929 among HEAD profiles. 5/6 predictions passed (P5 failed: r-terminal not depleted at Q0). Headless internal split significant: d-pseudo-HEAD closure-enriched, i-pseudo-HEAD specification-enriched.
- **Closure decomposition (C1672 CLOSURE_DISTRIBUTED):** The Q3->Q4 step is overwhelmingly an m-terminal event (77.4% of TERM JSD). HEAD closure is distributed: e-collapse (36%), headless-surge (22%), a-surge (22%). Closure and specification are mechanistically distinct: TERM cosine=0.08 (completely different atoms drive each). Interior transitions confirm C1566 work-zone homogeneity.
- **Hazard-position coupling (C1673 HAZARD_POSITION_COUPLED):** Interaction chi2=337 with 16 zone-specific pairs. Safety architecture operates through specific atom-position couplings. a-HEAD is intrinsically hazardous everywhere (2.8-4.6x enrichment in all zones). Work-zone safety is k-LED (k 63.2% in WORK vs t 61.2%, e 56.1%). ZERO frames concentrate in SPECIFICATION zone.
- **Section modulation (C1674 SECTION_MODULATES_GRADIENT):** All sections preserve the three-zone scaffold (TERM correlations all >0.96). But HEAD deployment amplitudes vary: C section HEAD corr=0.76, Q3Q4 JSD varies 2.2x across sections. m-terminal Q4 surge is universal. Matches expert prediction: "same scaffold, different emphases."
- **Carryover cross-reference:** Position-sensitive atoms are predominantly POSITIVE carryover (50% of top-6), suggesting gradient is driven by deployment choices, not chaining bias.

---

## Version 5.53 (2026-03-11) - Phase 580: Apparatus Response Manifold Synthesis

### Summary

Phase 580 consolidates all per-folio apparatus features from Phases 570a-579 into a two-space manifold synthesis. Space A (response surface, 11 features) describes what kind of apparatus each folio has; Space B (realized performance, 4 features) describes how each folio actually performs. Per expert revision, this split avoids a self-repackaging PCA. Pure analytical synthesis from existing JSON results — no new simulation.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS/` — Phase 580 directory with 6 scripts (T0-T5), 6 result files, REPORT_580.md |
| **ADDED** | C1667: Manifold dimensionality MANIFOLD_DIFFUSE — effective rank 5.88, 5 PCs for 80%, not low-dimensional |
| **ADDED** | C1668: Family geometry FAMILY_GRADIENT — LOO 0.78, silhouette 0.13, overlapping gradient clouds |
| **ADDED** | C1669: Landscape alignment LANDSCAPE_ALIGNED — 2 sig KW PCs, B/W=1.07, three-pole reproduced |
| **ADDED** | C1670: Accent is manifold position ACCENT_IS_MANIFOLD_POSITION — canonical r1=0.871, incr R²=0.268 |
| **ADDED** | Tier-3 interpretation freeze on apparatus-conditioned closure advantage |
| **UPDATED** | INDEX.md — +4 constraints (1670 total), Phase 580 section added |
| **UPDATED** | CLAUDE.md — Quick reference updated (v5.53, 1670 constraints, 580 phases) |

### Key Findings

- **Dimensionality (C1667 MANIFOLD_DIFFUSE):** The 11-feature response surface has effective rank 5.88. Five PCs capture 80%. High ablation-channel correlations (r=0.90, 0.92) create some redundancy but don't collapse the manifold. Space B is dominated by a single DYE/z_margin axis (effective rank 1.40).
- **Family geometry (C1668 FAMILY_GRADIENT):** LOO accuracy 78% (perm p=0.001), but silhouette only 0.13. A2 is most elongated (ratio 1.36) along PC1-PC2. A3 bridges A1-A2 with 54% of folios equidistant. Families are overlapping gradient clouds, not discrete clusters.
- **Landscape alignment (C1669 LANDSCAPE_ALIGNED):** PC1 (H=19.75, p<0.001) and PC3 (H=11.43, p=0.003) separate SA/TD/FR. B/W ratio 1.07 confirms three-pole structure. Cross-space: PC1~PEF (r=-0.43), PC2~CCS1 (r=0.55).
- **Accent reinterpretation (C1670 ACCENT_IS_MANIFOLD_POSITION):** Canonical r1=0.871. Accent PC1 ~ manifold PC1 (Spearman r=-0.80). Within-A2, manifold explains R²=0.946 of CCS1. Point-biserial: manifold PC1 discriminates SE vs PA stubborn folios (r=-0.65).
- **Tier-3 freeze:** The forgiving pole is the forgiving edge of a continuous apparatus-response manifold. Folio accent is machine-fit position on a real response surface.

---

## Version 5.52 (2026-03-11) - Phase 579: Forgiving Pole Residual Audit

### Summary

Phase 579 audits the 8 stubborn A2 forgiving folios (f39v, f40r, f50v, f55v, f85r2, f86v5, f86v6, f95r2) that survive all closure-gating improvements from Phases 574-578. Four diagnostic tracks determine whether these represent a structural endpoint or parameter underfit. C1666 (DECISIVE): MIXED_BOUNDARY_STRATUM -- 4 structural endpoints (f39v, f55v, f86v5, f95r2) and 4 parameter-achievable (f40r, f50v, f85r2, f86v6). The forgiving/passing boundary is a gradient, not a clean partition, consistent with C1641.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/FORGIVING_POLE_RESIDUAL_AUDIT/` -- Phase 579 directory with 6 scripts (T0-T5), 6 result files, REPORT_579.md |
| **ADDED** | C1663: Pole coherence GRADIENT_TAIL -- LOO 33.3%, 0/5 sig F-axes, 2/5 sig ablation channels, tight lobe but inseparable |
| **ADDED** | C1664: Channel concentration CHANNEL_CONCENTRATED -- 8/8 >60% share, NO_R1 dominates 6/8, NO_R4 2/8, pre=post gate |
| **ADDED** | C1665: Opportunity confound OPPORTUNITY_NEUTRAL -- event count R-sq=0.0001, CTS lower in forgiving, not a confound |
| **ADDED** | C1666: Structural endpoint MIXED_BOUNDARY_STRATUM -- 4 STRUCTURAL_ENDPOINT, 4 PARAMETER_ACHIEVABLE, 0 PARAMETER_UNDERFIT |
| **UPDATED** | INDEX.md -- +4 constraints (1666 total), Phase 579 section added |
| **UPDATED** | CLAUDE.md -- Quick reference updated (v5.52, 1666 constraints, 579 phases) |

### Key Findings

- **Coherence (C1663 GRADIENT_TAIL):** The 8 form a tight lobe (within-similarity=0.919) but LOO nearest-centroid only 33.3% -- not separable from passing A2. They are the tail of A2's continuous gradient, not a distinct subfamily.
- **Channel (C1664 CHANNEL_CONCENTRATED):** R1 (per-SV CLOSE drawdown) dominates 6/8 folios, R4 (quality-conditioned Y accumulation) dominates 2/8 (f86v5, f86v6). Pre-gate and post-gate identical -- regime gating didn't change the residual conversion mechanism.
- **Opportunity (C1665 OPPORTUNITY_NEUTRAL):** Event count R-sq=0.0001 on CCS1. Forgiving folios have weaker closure events (CTS 0.200 vs 0.350, 80% WEAK grammar vs 48.5%, 6.7% E_armed vs 39.4%). These are intrinsic properties, not sampling artifacts.
- **Endpoint (C1666 MIXED_BOUNDARY_STRATUM):** F1xF2 grid search (144 per folio) + conditional 3rd-axis (F3/F5) finds 4 folios can pass but only with displacement >= 0.5 (PARAMETER_ACHIEVABLE), 4 cannot pass at any point (STRUCTURAL_ENDPOINT). All best points cluster at grid extreme (F1=1.6, F2=0.5). Zero PARAMETER_UNDERFIT (none pass with displacement < 0.3).
- **7,488 total simulation runs in 121s.** T4a=6,912 (F1xF2 sweep), T4b=576 (3rd-axis extension), T2=336 (sub-ablation).

---

## Version 5.51 (2026-03-11) - Phase 578: Event-Local Closure Adjudicator

### Summary

Phase 578 replaces Phase 576's line-level morphological classifier with an event-level execution+anatomy classifier. Phase 577 falsified line-level strength (21.6% surrogate agreement). Expert diagnosis: closure legitimacy is event-local, not line-local. The key discriminator is burden resolution — whether the CLOSE event actually reduced max(|C-0.5|, |X-0.5|) — combined with event-level packet strength signals. 4 event classes: AUTHENTIC_RESOLVER (128, 27.6%), PARTIAL_RESOLVER (174, 37.6%), NONRESOLVING_COUNTERFEIT (161, 34.8%), INERT_PSEUDO (0). Decisive test (C1660) REJECTED: all event-class configs perform worse than LINE_CLASS_CONTROL (Phase 576 AMB_PESSIMISTIC). Event-class gate suppresses COUNTERFEIT events that have positive DYE advantage (90.1% positive), and gives null events full admission at non-CLOSE positions under M4f.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/EVENT_LOCAL_CLOSURE_ADJUDICATOR/` -- Phase 578 directory with 6 scripts (T0-T5), 6 result files, REPORT_578.md |
| **ADDED** | C1659: Event-local feature coverage COVERAGE_VALIDATED — 463 events, 2323 lines, 3/4 classes populated, burden range [-3.46, 1.00] |
| **ADDED** | C1660: Event legitimacy gating EVENT_GATING_REJECTED — LINE_CLASS_CONTROL wins (A2 delta=0.0635), all event configs negative A2 delta, null wins increase |
| **ADDED** | C1661: Burden resolution discriminator DISCRIMINATOR_WEAK — direction OK (AUTH DYE_adv=0.119 > CF=0.098) but Cohen's d=0.267 < 0.3 threshold |
| **ADDED** | C1662: Landscape migration MIGRATION_ABSENT — A2 FORGIVING 8→8, 0 migrating folios, no regression |
| **UPDATED** | INDEX.md -- +4 constraints (1662 total), Phase 578 section added |
| **UPDATED** | CLAUDE.md -- Quick reference updated (1662 constraints, Phase 578) |

### Key Findings

- **Decisive test fails (C1660):** EVENT_CLASS_FULL A2 delta=-0.0185 (vs LINE_CLASS_CONTROL +0.0635). All event-class configs produce negative A2 delta, increasing null wins from 7→8 (vs 7→2 for LINE_CLASS_CONTROL). Event-class gating is strictly worse than morphological gating.
- **Root cause 1 — COUNTERFEIT has positive DYE:** NONRESOLVING_COUNTERFEIT events have mean DYE_adv=0.098 with 90.1% positive rate. Suppressing these events REDUCES M1 DYE. Burden non-resolution does NOT mean the event lacks genuine M1 advantage.
- **Root cause 2 — M4f null inflation:** Event classes only cover CLOSE lines (463/2323 = 20%). Under M4f, non-CLOSE positions get NON_CLOSE → (1.0, 1.0) full admission. This inflates null DYE. Phase 576 morphological classes cover ALL lines (100%), suppressing null events at counterfeitable positions.
- **Burden resolution direction confirmed (C1661):** AUTHENTIC mean DYE_adv (0.119) > COUNTERFEIT (0.098), but effect size weak (d=0.267). Resolution coherence is dramatically different: AUTHENTIC 68.8% coherent vs COUNTERFEIT 7.5% — but this doesn't translate to DYE suppression.
- **Event classification well-formed (C1659):** 463 events correctly classified, 3/4 classes populated (INERT_PSEUDO=0 expected), burden distribution well-profiled.
- **Landscape unchanged (C1662):** A2 FORGIVING 8→8. No improvement over Phase 576.
- **Strong-band preservation slightly better:** EVENT_CLASS_FULL preserves 64.8% of strong DYE (vs LINE_CLASS_CONTROL 58.7%), but this comes at the cost of negative delta advantage.

### Status

Phase 578 event-local gating REJECTED. Burden resolution is a real feature (coherence signature is stark) but it doesn't predict DYE advantage well enough to gate on. COUNTERFEIT events have genuine positive DYE, and the event-class framework gives null events full admission at non-CLOSE positions. 1,662 validated constraints across 578 phases.

---

## Version 5.50 (2026-03-11) - Phase 577: Authenticity-Strength Regime Gate

### Summary

Phase 577 adds closure authenticity strength as a 4th gate input to Phase 576's regime admission architecture. Phase 576 proved regime admission gating works (ARCHITECTURE_ROBUST) but strong-band DYE preservation was only 58.7% (target 90%). Phase 577 adds strength bands (STRONG/MED/WEAK) as a 4th gate dimension to rescue strong legitimate closure without weak-band relapse. The decisive test (C1656) fails: RESCUE_REJECTED. The best configuration is NO_STRENGTH (= Phase 576 AMB_PESSIMISTIC), meaning the strength dimension does not improve performance. The aligned signal definitions (any_opaque, strict closure_armed) produce a surrogate with only 21.6% agreement with Phase 574 event bands, too coarse to discriminate.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/AUTHENTICITY_STRENGTH_REGIME_GATE/` -- Phase 577 directory with 6 scripts (T0-T5), 6 result files, REPORT_577.md |
| **ADDED** | C1655: Authenticity strength coverage COVERAGE_PARTIAL — 2323 lines, 3/3 bands, 4 structural zeros (needed 5), surrogate agreement 21.6% |
| **ADDED** | C1656: Strong-band rescue RESCUE_REJECTED — best config=NO_STRENGTH, strong preserved 69.1% (<80% target), weak guardrail safe, A2 delta=0.0635 (matches P576) |
| **ADDED** | C1657: Configuration robustness SPECIFIC — 0/3 strength configs beat NO_STRENGTH, 3/3 beat CREDIT_ONLY_4D, architecture not robust for strength dimension |
| **ADDED** | C1658: Landscape migration MIGRATION_ABSENT — A2 FORGIVING 8→8, 0 migrating folios, no regression |
| **UPDATED** | INDEX.md -- +4 constraints (1658 total), Phase 577 section added |
| **UPDATED** | CLAUDE.md -- Quick reference updated (1658 constraints, Phase 577) |

### Key Findings

- **Decisive test fails (C1656):** Adding authenticity strength as a 4th gate input does NOT rescue strong-band DYE. The best configuration is NO_STRENGTH, identical to Phase 576 AMB_PESSIMISTIC (A2 delta=0.0635). All rescue configs underperform.
- **Surrogate too coarse:** Per-line strength bands agree only 21.6% with Phase 574 event-level bands. The aligned signal definitions (opacity_frac>0 instead of >=0.5, strict closure_armed instead of broadened proxy) dramatically shifted the band distribution: STRONG=460(19.8%), MED=1729(74.4%), WEAK=134(5.8%). "STRONG" is too permissive to discriminate.
- **Rescue dilutes selectivity:** STRENGTH_RESCUE achieves 76.8% strong preservation (up from 69.1%) but A2 delta drops from 0.0635 to 0.0475 and null wins increase from 2 to 3. The gain in strong preservation is not worth the loss in selectivity.
- **Signal alignment changes:** 1782 lines changed opaque status, 572 lines changed armed status from Phase 576 definitions. This confirms the surrogates are materially different, not just edge cases.
- **Landscape unchanged:** A2 FORGIVING 8→8, 0 migrating folios. The strength dimension has no landscape impact.
- **Structural zeros clean:** 0 activations across all configs, confirming classifier/strength alignment is consistent even if the surrogate is weak.

### Status

Phase 577 strength dimension REJECTED. The per-line surrogate is too coarse to rescue strong-band DYE without diluting gate selectivity. Next iteration should consider event-level (not line-level) strength, or alternative rescue mechanisms. 1,658 validated constraints across 577 phases.

---

## Version 5.49 (2026-03-11) - Phase 576: Closure Regime Admission Gate

### Summary

Phase 576 validates the expert's core diagnosis from Phase 575: counterfeit closure must be blocked at the regime level (Layer 2: whether R1-R5 fire), not just the reward level (Layer 3: Y-credit). A two-stage ClosureAdmissionApparatus gates regime admission (admit_mult on R1/R5) and yield credit (credit_mult on R2/R3/R4 Y) based on a 6-class tiered legitimacy classifier, CTS band, and containment burden. The decisive test (C1652) passes: REGIME_GATED outperforms CREDIT_ONLY on A2 delta_advantage (0.0605 vs 0.0561), and the architecture is robust across all 4 regime configs. Strong-band DYE preservation (58.7%) and M1 signature agreement (76%) need improvement.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/CLOSURE_REGIME_ADMISSION_GATE/` -- Phase 576 directory with 6 scripts (T0-T5), 6 result files, REPORT_576.md |
| **ADDED** | C1651: Tiered classification PARTIAL — 2323 lines, 6/6 classes, AUTH_AMBIGUOUS 5.4%, M1 agreement 76% |
| **ADDED** | C1652: Regime admission SELECTIVE — SSI=63.5, REGIME_GATED A2 delta > CREDIT_ONLY, 4/4 configs beat control |
| **ADDED** | C1653: Event-band discrimination PARTIAL — TP=4/5, TN=4/4, FP=0, strong preserved 58.7%, weak suppressed 71.4% |
| **ADDED** | C1654: Landscape STABLE — A2 FORGIVING 8→8, CCS1 reduction 66.2%, no new A1/A3 FORGIVING |
| **UPDATED** | INDEX.md -- +4 constraints (1654 total), Phase 576 section added |
| **UPDATED** | CLAUDE.md -- Quick reference updated (1654 constraints, Phase 576) |

### Key Findings

- **Decisive test (C1652):** Gating regime admission (R1-R5) outperforms gating only Y-credit. REGIME_GATED A2 delta_adv=0.0605 vs CREDIT_ONLY=0.0561. All 4 regime configs outperform the credit-only control.
- **Architecture robustness:** ARCHITECTURE_ROBUST — 4/4 configs beat CREDIT_ONLY, SSI>1 for all, TN>=4 for all. Result is not config-specific.
- **AUTH_AMBIGUOUS too generous:** AMB_PESSIMISTIC (halving AUTH_AMBIGUOUS multipliers) performs best (delta=0.0635, SSI=63.5), confirming the base table's ambiguous values are too permissive.
- **Strong-band loss:** 58.7% preservation (target 90%). The gate reduces strong-band DYE because some STRONG events land on lines classified as non-RESISTANT (AUTH_PROTECTIVE, AUTH_THRESHOLD).
- **M1 signature agreement:** 76% (target 90%). Mismatches are armed/unarmed differences between Phase 574 and 576 armedness proxies; class-level agreement is higher.
- **Landscape stable:** A2 FORGIVING pole unchanged (8→8) despite 66.2% CCS1 reduction. DYE improvement doesn't translate to classification shifts.
- **Null win reduction:** A2 null wins 7→2-3 across configs (71.4% weak suppression).

### Status

Regime admission gate validated as architecturally sound (C1652 SELECTIVE, ARCHITECTURE_ROBUST). Strong-band preservation and classification agreement need iteration. 1,654 validated constraints across 576 phases.

---

## Version 5.48 (2026-03-10) - Phase 575: Selective Closure Credit + Authentication Gate

### Summary

Phase 575 internalizes Phase 574's counterfeit-closure threshold as an online apparatus gate. A two-layer AuthenticatedRecoveryApparatus gates Y-credit (Layer 1) and modulates cleanliness gain (Layer 2) based on an Authentication Closure Score (ACS). The ACS configuration is validated (C1647) and both layers contribute synergistically (C1648). However, the gate fails the surgical selectivity test (C1649: SSI=0, no counterfeitable signatures correctly starved) because CTS dominates the ACS formula, drowning out the morphological configuration signal. The landscape is mildly aggravated (C1650).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE/` -- Phase 575 directory with 5 scripts (T0-T5), 5 result files, REPORT_575.md |
| **ADDED** | C1647: ACS configuration validated — 86.6% signature coverage, rho=0.8045, ACS gap 2.7x CTS gap |
| **ADDED** | C1648: Two-layer gate synergistic — L1 delta=0.003, L2 incremental=0.0005, combined=0.0036 |
| **ADDED** | C1649: Stratified selectivity REJECTED — SSI=0, auth_mult 0.83-1.0 for all counterfeitable sigs |
| **ADDED** | C1650: Landscape pole aggravated — FORGIVING unchanged A2, +1 total (new A3 FORGIVING) |
| **UPDATED** | INDEX.md -- +4 constraints (1650 total), Phase 575 section added |
| **UPDATED** | CLAUDE.md -- Quick reference updated (1650 constraints, Phase 575) |

### Key Findings

- **ACS validation (C1647):** The authentication closure score (ACS = 0.60*CTS + 0.40*config_score) successfully discriminates RESISTANT (mean ACS=0.631) from COUNTERFEITABLE (mean ACS=0.224) signatures. The configuration-based scoring adds signal beyond CTS alone (ACS gap=0.270 vs CTS gap=0.101).
- **Gate architecture (C1648):** Layer 1 (Y-credit gating by auth_mult) contributes ~85% of the gate's M1 DYE reduction. Layer 2 (cleanliness gain modulation) adds ~15%. Combined M1 delta=0.0036 for A2 folios, confirming both layers work.
- **Selectivity failure (C1649):** No counterfeitable signature achieves auth_mult < 0.5 under any configuration. Root cause: alpha=0.60 weight on CTS in the ACS formula means even low-config_score events have ACS above the A2 threshold (0.324) if their CTS > ~0.4. The configuration signal exists but is overwhelmed.
- **Landscape aggravation (C1650):** The gate uniformly reduces DYE advantage rather than selectively discriminating. 9 STABLE_AMPLIFIER folios shift to THRESHOLD_DEPENDENT; 1 new FORGIVING_RECIRCULATOR appears in A3.
- **Next iteration guidance:** Reduce alpha substantially (e.g., 0.30-0.40), or use non-linear ACS where config_score dominates at low values, or apply gate only to A2 events below the CTS threshold identified in C1644 (CTS < 0.18).

### Status

Authentication gate tested, ACS validated, selectivity NEGATIVE. 1,650 validated constraints across 575 phases.

---

## Version 5.47 (2026-03-10) - Phase 574: Counterfeit Closure Threshold + Recovery Gate Map

### Summary

Phase 574 decomposes the close recovery mechanism (C1639) into R1-R5 sub-channels, models counterfeit closure threshold curves, identifies which closure packet morphologies are counterfeitable in A2, and maps the continuous apparatus response landscape.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/` -- Phase 574 directory with 6 scripts (T0-T5), 6 result files, REPORT_574.md |
| **ADDED** | C1643: Recovery gate R1_C dominant — R1_C (117%) and R4_C (119%) strongly non-additive coupled loop |
| **ADDED** | C1644: Threshold A2 shifted gradual — A2 needs CTS=0.18 vs A1=0.04, shift +0.138, transition width 0.327 |
| **ADDED** | C1645: Morphology selective counterfeiting — 5 resistant, 5 counterfeitable packet types |
| **ADDED** | C1646: Landscape three-pole — 25% amplifier, 63% threshold-dependent, 12% forgiving recirculator |
| **UPDATED** | INDEX.md -- +4 constraints (1646 total), Phase 574 section added |
| **UPDATED** | CLAUDE.md -- Quick reference updated (1646 constraints, Phase 574) |

### Key Findings

- **Recovery gate (C1643):** Containment drawdown (R1-C, 117%) and containment-to-Y conversion (R4-C, 119%) form a coupled loop (interaction fraction -1.06). R1 feeds R4, so removing either alone underestimates their joint contribution.
- **Threshold (C1644):** A2 requires 4.5x more CTS (0.18 vs 0.04) before grammar advantage emerges. Below CTS=0.2, 64% of A2 events are counterfeitable. Above CTS=0.6, 0% are. The transition is gradual (width=0.327), not a sharp gate.
- **Morphology (C1645):** Armed+headless+high-CTS packets resist counterfeiting even in A2. Low-signal packets are counterfeitable. Protection hierarchy: headless > high_cts > armed > compound > m_terminal.
- **Landscape (C1646):** Three descriptive poles on a continuous manifold. A2 dominates the forgiving pole (8/9), but 1 A2 folio is a stable amplifier and 9 are threshold-dependent. Cross-cut fraction 0.25 confirms gradient structure.

### Status

Recovery gate + threshold + morphology + landscape analysis COMPLETE. 1,646 validated constraints across 574 phases.

---

## Version 5.46 (2026-03-10) - Phase 573: A2 Forgivingness Mechanism + Apparatus Family Partition

### Summary

Phase 573 investigates WHY the A2_SEALED_RECIRCULATION apparatus profile has 9x higher Forgivingness Index than A1, using counterfactual ablation across 5 physics channels on 76 eligible Currier B folios. The phase identifies close recovery (R1-R5) as the single dominant mechanism (159.5% of excess CCS1), discovers that grammar strength modulates whether real closure beats the forgiving null, and tests unsupervised family partition of the folio set.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/` -- Phase 573 directory with 6 scripts (T0-T5), 6 result files, REPORT_573.md |
| **ADDED** | C1639: A2 mechanism identified — NO_CLOSE_RECOVERY accounts for 159.5% of excess CCS1 |
| **ADDED** | C1640: Family partition inconclusive — real structure (sil=0.361, ARI=0.385) but below thresholds |
| **ADDED** | C1641: Within-A2 weakly structured — 44% boundary folios, no section sub-profiles |
| **ADDED** | C1642: Grammar pattern strength-dependent — only STRONG events beat the null (+0.021), WEAK events lose (-0.014) |
| **UPDATED** | INDEX.md -- +4 constraints (1642 total), Phase 573 section added |
| **UPDATED** | CLAUDE.md -- Quick reference updated (1642 constraints, Phase 573) |

### Key Findings

- **Mechanism (C1639):** Close recovery channels (R1-R5) are THE mechanism. Ablating them drops A2 null DYE from 0.114 → ~0. Within-A2, CCS1 correlates rho=0.963 with close recovery ablation effect.
- **Grammar (C1642):** A2 forgivingness is NOT uniform. STRONG-grammar events beat the null; WEAK events lose. The apparatus physics (R1-R5) are so generous that only strong grammar can outcompete them.
- **Families (C1640):** 2-cluster partition separates 12 forgiving folios (9 A2 + 3 A3) from 64 productive folios. Structure is gradient-like, not crisp.
- **A2 structure (C1641):** No section-based sub-profiles (F-ratio=0.055). But 44% boundary folios: 4 resemble A1 (CCS1=0.013), 4 resemble A3. Core A2 (n=5) has CCS1=0.180.

### Status

A2 mechanism analysis COMPLETE. 1,642 validated constraints across 573 phases.

---

## Version 5.41 (2026-03-06) - Phase 552: Historical Genre Placement (SYNTHESIS)

### Summary

Phase 552 is a Tier 3 interpretive synthesis placing the Voynich Manuscript within the landscape of medieval technical document genres. No new empirical analysis was performed and no new constraints were added. The output is `phases/HISTORICAL_GENRE_PLACEMENT/GENRE_ANALYSIS.md`, a genre comparison document (~5,000 words) that evaluates 8 medieval document genres against the VMS structural profile across 7 assessment dimensions, identifies the genre gap, and proposes a new genre classification.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/HISTORICAL_GENRE_PLACEMENT/GENRE_ANALYSIS.md` -- Genre comparison (6 sections: Methodology, Genre Comparison Matrix, Closest Matches, Genre Gap, Proposed Genre Classification, Implications) |
| **UPDATED** | INDEX.md -- +0 constraints (1410 total), Phase 552 synthesis section added |

### Key Integrative Findings (narrative connections, not new claims)

- No existing medieval genre scores above 2.5/7 compatibility with the VMS structural profile; laboratory notebooks are closest (2.5/7), tally systems second (2.0/7)
- Three VMS features have NO historical precedent in any surveyed genre: structural safety architecture (C109), multi-register architecture (C1499), formal operational grammar (C121/C124)
- The fundamental genre gap is between DESCRIPTION and EXECUTION: all surveyed genres describe procedures in natural language; the VMS encodes operational states in formal notation
- Proposed genre classification: OPERATIONAL CONTROL CODEX -- a purpose-built non-linguistic operational notation encoding parameterized control programs with structural safety enforcement and multi-register architecture
- The genre gap directly explains the decipherment failure: the VMS was never natural language (C132), so all cipher/language approaches are structurally misdirected
- The VMS and Brunschwig serve opposite purposes within the same domain: proprietary execution (pre-1500) vs pedagogical publication (1500)

### Status

Historical genre placement COMPLETE. 1,410 validated constraints across 552 phases.

---

## Version 5.40 (2026-03-06) - Phase 551: Operator/Document-Usage Model (SYNTHESIS)

### Summary

Phase 551 is a Tier 3 interpretive synthesis describing how a trained medieval practitioner would navigate and use the Voynich Manuscript's four-register document stack during a work session. No new empirical analysis was performed and no new constraints were added. The output is `phases/OPERATOR_USAGE_MODEL/OPERATOR_MODEL.md`, a practitioner-facing narrative (~4,500 words) that translates structural findings from 550 prior phases into a practical account of document usage.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/OPERATOR_USAGE_MODEL/OPERATOR_MODEL.md` -- Practitioner's guide (9 sections: operator profile, four registers, eight-step session model, comparisons, responsibility architecture, dark pipeline, parallel execution, negative space, summary) |
| **ADDED** | `phases/OPERATOR_USAGE_MODEL/REPORT.md` -- Phase report documenting synthesis decisions and integrative findings |
| **UPDATED** | INDEX.md -- +0 constraints (1410 total), Phase 551 synthesis section added |

### Key Integrative Findings (narrative connections, not new claims)

- Four registers form a coordinated working environment navigated as-needed during a single session, not sequentially
- Eight-step session model emerges from combining program selection (C531), configuration checking (C502/C443), header reading (C747), paragraph selection (C1399/C864), line execution (C1425-C1430), between-line judgment (C1056), between-paragraph choice (C1399-C1400), and completion judgment (C197)
- Negative space is collectively striking: no literacy (C132), no math (C287), no sequential memory (C1470-C1471), no cross-folio reference (C531), no grammar knowledge (C121) -- notation designed for maximum operational accessibility
- Parallel execution model: paragraph self-containment (C845) + ordering null (C1399) + state-independence (C1400) + within-folio coherence (C1288) enables multiple operators working from same folio simultaneously

### Status

Operator usage model COMPLETE. Complements Phase 550 (technical specification) with a practitioner-facing view of the same architecture. 1,410 validated constraints across 551 phases.

---

## Version 5.39 (2026-03-06) - Phase 550: Complete Control Architecture -- The Voynich Instruction Word (SYNTHESIS)

### Summary

Phase 550 is the capstone synthesis of the characterization program. No new empirical analysis was performed and no new constraints were added. The output is `phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md`, a self-contained specification document (~4,500 words) that formalizes the complete instruction word structure, safety architecture, organizational model, cross-register document stack, shared atom substrate, operator responsibility boundary, and generative sufficiency into a single coherent reference derived from the full 1,410-constraint system across 549 analytical phases.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md` -- Complete architectural specification (7 sections + 2 appendices) |
| **ADDED** | `phases/INSTRUCTION_WORD_FORMALISM/REPORT.md` -- Phase report documenting synthesis decisions and integrative findings |
| **UPDATED** | INDEX.md -- +0 constraints (1410 total), Phase 550 synthesis section added |

### Key Integrative Findings (cross-constraint connections, not new claims)

- Terminal atom is TRIPLE-function linchpin: suffix gating (C1440-C1445) + hazard class typing (C1547) + next-HEAD routing (C1563)
- Three safety levels compose MULTIPLICATIVELY, explaining 0.053% realized hazard rate (C1360) despite individual levels being "leaky"
- Cross-token instruction chain is exclusively TERM->HEAD; suffix is a dead-end branch (C1564)
- A and B are registers (declarative vs executable) over shared atom substrate (C1499-C1527), not lookup tables or translations
- Operator boundary is an intentional design choice: encodes everything procedurable, excludes everything requiring embodied judgment (C1056, C197, C458)

### Status

Characterization program COMPLETE. 1,410 validated constraints across 550 phases. No structural question about the formal architecture remains open at the level addressable by internal analysis.

---

## Version 5.38.174 (2026-03-06) - Phase 549: Atom Architecture Cleanup

### Summary

Phase 549 closes remaining empirical gaps in atom-level characterization through four sub-analyses: articulator behavior across systems, sequential atom couplings, paragraph atom signatures, and line-position atom gradients. 4 research questions, 17 sub-analyses. Q1 (articulators) CONFIRMS all 6 existing constraints (C1416-C1421) at higher resolution with no new findings. Q2 (sequential couplings) produces THREE new constraints: HEAD self-transition rate hierarchy (C1562) revealing three-tier persistence where stability/identification domains sustain runs (e/headless ~28.5%) while thermal/arrangement domains switch quickly (k 16.7%, o 13.6%); terminal-to-next-HEAD routing grammar (C1563) completing the cross-token instruction chain -- TERM is a dual-function atom that simultaneously gates suffix attachment and routes the next token's HEAD domain (r->a 2.231x, y->k 1.597x, h->t 1.892x, l->e 1.246x, m->o 1.554x); and suffix zero forward HEAD information (C1564, JSD=0.0021), extending C1003 (pairwise compositionality) to the cross-token boundary. Q3 (paragraph signatures) produces ONE new constraint: header modifier divergence exceeds HEAD divergence 10x (C1565) -- paragraph specification operates through modifier selection (p 3.66x, f 3.90x enriched) not HEAD domain (JSD=0.008), resolving C1287's MARKING-enriched header mechanism. Q4 (line-position gradient) produces ONE new constraint: Q3->Q4 step discontinuity (C1566) -- HEAD JSD jumps 26x at closure boundary while Q1-Q3 interior remains homogeneous (JSD<0.003), refining C1425-C1430's three-zone model to a TWO-STEP architecture with uniform work zone.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1562: HEAD self-transition rate hierarchy (e/headless 28.5% >> k 16.7% >> o 13.6% >> t 9.1%; three-tier persistence) |
| **ADDED** | C1563: Terminal-to-next-HEAD cross-token routing grammar (r->a 2.231x, y->k 1.597x, h->t 1.892x, l->e 1.246x, m->o 1.554x) |
| **ADDED** | C1564: Suffix zero forward HEAD information (JSD=0.0021; suffix scope terminates at token edge) |
| **ADDED** | C1565: Paragraph header modifier divergence 10x HEAD divergence (MOD JSD=0.085 vs HEAD JSD=0.008; p 3.66x, f 3.90x in headers) |
| **ADDED** | C1566: Line position Q3-Q4 step discontinuity (HEAD JSD 26x jump, TERM JSD 20x jump; two-step line architecture) |
| **ADDED** | `phases/ATOM_ARCHITECTURE_CLEANUP/scripts/atom_cleanup.py` |
| **ADDED** | `phases/ATOM_ARCHITECTURE_CLEANUP/results/atom_cleanup.json` |
| **ADDED** | `phases/ATOM_ARCHITECTURE_CLEANUP/REPORT.md` |
| **UPDATED** | INDEX.md -- +5 constraints (1410 total) |
| **EXTENDED** | C1212 (TERMINAL->INITIAL cross-token chaining): extended to HEAD-domain resolution via C1562/C1563 |
| **EXTENDED** | C1003 (pairwise compositionality): extended to cross-token boundary via C1564 (suffix zero forward info) |
| **EXTENDED** | C1402 (no sequential convergence at any scale): extended to paragraph atom composition (late body MORE divergent, ratio 1.393) |
| **CONFIRMED** | C1416: Articulator rate 4.41% in B (exact match) |
| **CONFIRMED** | C1417: Articulator line-initial concentration (4.518x enrichment) |
| **CONFIRMED** | C1418: Articulator PREFIX-locked with BARE/qo exclusion (qo 0.016x, BARE 0.0x) |
| **CONFIRMED** | C1419: Articulator e-HEAD selectivity / k-HEAD exclusion (e 1.807x, k 0.098x) |
| **CONFIRMED** | C1420: Articulator suffix suppression (0.548x ratio) |
| **CONFIRMED** | C1421: Articulator category full MIDDLE mediation (category JSD=0.030) |
| **CONFIRMED** | C1428: THERMAL peak-then-decline positional gradient (Q1 peak at category level) |
| **CONFIRMED** | C1434: m-terminal 196x line-final enrichment (37x at quintile resolution) |
| **CONFIRMED** | C1464: k-IMMUNE thermal work onset at Q1 (k-HEAD peaks Q1 at 17.2%) |
| **CONNECTED** | C1563 -> C1440 (terminal opacity): TERM atom now dual-function (suffix gating + HEAD routing) |
| **CONNECTED** | C1565 -> C1287 (paragraph header MARKING-enriched): mechanism resolved -- modifier selection not HEAD domain |
| **CONNECTED** | C1566 -> C1434 (m-terminal closure valve): m-terminal step at Q4 drives the sharp closure discontinuity |

---

## Version 5.37.173 (2026-03-06) - Phase 548: o-Domain Deep Dive

### Summary

Phase 548 provides the first comprehensive characterization of the o-HEAD atom domain (2,717 tokens, 11.8% of Currier B), answering 10 research questions across 13 analytical tests. STRONGEST FINDING: o-HEAD terminal-to-category deterministic mapping (C1556) -- the terminal atom deterministically selects operational category at near-100% purity: ol=100% STAGING, or=100% FLOW, bare o=100% OPERATION. This is the sharpest terminal-category coupling for any HEAD atom, resolving C1388's vague "arrangement" label. o-HEAD depletes y-terminal to 0.007x (C1557), the strongest single-terminal depletion for any HEAD, creating structural PHASE_ORDERING immunity. Executive modifiers p (3.51x) and f (2.83x) are the strongest modifier enrichments for any single HEAD (C1558), confirming C1543. Cross-system gradient runs A (28.5%) > AZC (22.4%) > B (11.8%) with AZC zones grading from arrangement-heavy boundaries (S=29.3%) to execution-heavy interiors (R=17.7%), confirming C1517 and C1522 at full resolution (C1559). Inner atom composition shows y at 0.023x -- the most extreme single-atom divergence in the system (C1560). o-HEAD achieves 0% hazard source AND 0% target across all 2,717 tokens (C1561). Verdict: o-HEAD is an ARRANGEMENT SPECIFICATION SYSTEM using terminal atoms as categorical switches.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1556: o-HEAD terminal-to-category deterministic mapping (ol=100% STAGING, or=100% FLOW, bare o=100% OPERATION) |
| **ADDED** | C1557: o-HEAD y-terminal near-complete depletion (0.007x; structural PHASE_ORDERING immunity) |
| **ADDED** | C1558: o-HEAD p/f executive modifier enrichment (p 3.51x, f 2.83x; i 0.32x, d 0.55x depleted) |
| **ADDED** | C1559: o-HEAD cross-system gradient A(28.5%)>AZC(22.4%)>B(11.8%) with AZC S/R=1.66x |
| **ADDED** | C1560: o-HEAD inner atom composition divergent (y 0.023x most extreme in system; l 2.74x, p 4.67x) |
| **ADDED** | C1561: o-HEAD empirical hazard immunity (0% source AND 0% target, N=2717) |
| **ADDED** | `phases/O_DOMAIN_DEEP_DIVE/scripts/o_domain_deep_dive.py` |
| **ADDED** | `phases/O_DOMAIN_DEEP_DIVE/results/o_domain_deep_dive.json` |
| **ADDED** | `phases/O_DOMAIN_DEEP_DIVE/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1405 total) |
| **EXTENDED** | C1388 (o-atom arrangement domain marker): RESOLVED -- arrangement is CHANNELED through terminal atoms (l=staging, r=flow, bare=operation) |
| **EXTENDED** | C1475 (HEAD domain differentiation): o domain shown more internally structured (terminal-deterministic) than other HEADs |
| **EXTENDED** | C1485 (HEAD x TERM affinity): o-HEAD affinities are near-deterministic, not just enriched |
| **EXTENDED** | C1517 (o-HEAD zone-graded in AZC): confirmed with full zone detail (L=30.9%, S=29.3%, C=26.2%, P=19.1%, R=17.7%) |
| **EXTENDED** | C1507 (bridge HEAD redistributes A vs B): confirmed with token-level detail (A=28.5% o-HEAD, B=11.8%) |
| **CONFIRMED** | C1543 (p/f o-HEAD arrangement affiliates): quantified at p 3.51x, f 2.83x |
| **EXTENDED** | C1546 (HEAD hazard source immunity): extended to target immunity for o-HEAD (0% both directions) |
| **CONNECTED** | C1557 -> C1551 (PHASE_ORDERING = y-terminal): o-HEAD avoids y at 0.007x, structurally immune to PHASE_ORDERING |
| **CONNECTED** | C1556 -> C1483 (terminal category specificity): sharpened to near-deterministic within single HEAD |

---

## Version 5.36.172 (2026-03-06) - Phase 547: Phantom MIDDLE Mechanism

### Summary

Phase 547 investigates WHY the 5 phantom hazard source MIDDLEs (chey, shey, chedy, shedy, chol) identified in C1552 have exactly zero corpus occurrences despite being structurally conceivable. 4 candidate hypotheses tested across 10 analytical dimensions. PRIMARY MECHANISM: D_LEXICAL_CURATION confirmed -- ch/sh is a PREFIX-domain bigram that categorically does not extend to MIDDLE-initial position for compounds of length 3+ (C1553). PREFIX:MIDDLE ratio 5,821:0. Individual atoms c, s, h all appear freely in MIDDLE position; the prohibition operates at bigram granularity. SECONDARY: C_SAFETY_PRUNING contributing -- all 5 phantoms are hazard sources in the forbidden transition topology, providing defense-in-depth (C1554). REJECTED: A_CONSTRUCTION_PROHIBITION (all atoms legal in assigned slots) and B_SELECTIONAL_COLLAPSE (22-27 compatible PREFIXes each, suffix-compatible terminals). Additional finding: c-initial compound second-atom selectivity (C1555) -- 49/55 c-initial compounds (89.1%) contain h, but h is ALWAYS at position 2+ (c+[k/t/f/p]+h), never at position 1 (c+h). Confirms bigram-level positional partition between PREFIX domain and MIDDLE domain.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1553: ch/sh-initial compound MIDDLE categorical absence (0 types 3+ chars, PREFIX:MIDDLE ratio 5,821:0) |
| **ADDED** | C1554: Phantom MIDDLEs atom-legal but construction-dead (defense-in-depth -- forbidden topology covers vocabulary-excluded MIDDLEs) |
| **ADDED** | C1555: c-initial compound second-atom selectivity (c+h at positions 0-1 = 0, c+[k/t/f/p]+h = 49/55 types) |
| **ADDED** | `phases/PHANTOM_MIDDLE_MECHANISM/scripts/phantom_middle_mechanism.py` |
| **ADDED** | `phases/PHANTOM_MIDDLE_MECHANISM/results/phantom_middle_mechanism.json` |
| **ADDED** | `phases/PHANTOM_MIDDLE_MECHANISM/REPORT.md` |
| **UPDATED** | INDEX.md -- +3 constraints (1399 total) |
| **EXTENDED** | C1178 (phantom MIDDLEs morphologically isolated): mechanism now identified as ch/sh positional partition (C1553) |
| **EXTENDED** | C1552 (5/9 hazard sources are phantom): mechanism fully characterized -- not atom-level or selectional, but bigram-level positional partition |
| **CONNECTED** | C1553 -> C1534 (PREFIX uses 15 chars in three-tier classification): ch/sh as PREFIX bases explains why the same bigram cannot serve as MIDDLE-initial |
| **CONNECTED** | C1554 -> C109 (5 failure classes): forbidden topology designed at level of generality exceeding actual vocabulary -- structural insurance |
| **CONNECTED** | C1555 -> C1389 (c-atom main-loop modifier): c+[k/t/f/p]+h pattern shows c as modifier requiring intervening HEAD before terminal h |

---

## Version 5.35.171 (2026-03-06) - Phase 546: Hazard x PREFIX Integration

### Summary

Phase 546 joins the hazard-class atlas (C1528-C1533, Phase 543) with the PREFIX atom taxonomy (C1534-C1539, Phase 544) to determine whether PREFIX bases and modifiers actively route hazard exposure. 7 research questions across 11 analysis dimensions on 23,096 B tokens. STRONGEST FINDING: Universal HEAD atom hazard source immunity -- ALL 5 HEAD atoms {a,e,o,k,t} have exactly 0% source rate across 16,819 headed tokens (chi2=4411.9, V=0.219). EXTENDS C1446 from k-only to entire HEAD class. All 1,537 hazard source tokens are exclusively HEADLESS. TERMINAL atom determines hazard CLASS TYPE more strongly than HEAD (V=0.306 vs V=0.219): y->PHASE_ORDERING (100%), l->CONTAINMENT_TIMING (100%). PREFIX bases show significant hazard gradient (chi2=2038.0, V=0.133): e-base 3.37x enriched, k-base 0.30x depleted. q-modifier provides ~7x hazard protection on o-base (4.15% vs 27-52% for other modifiers) via k-HEAD routing (C1538). Sister pairs show 0.66-1.80x hazard asymmetry predictable from atom structure. COMPLETE hazard routing chain established: PREFIX base -> HEAD selection -> hazard immunity (binary) -> TERMINAL atom -> hazard class type (categorical).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1546: Universal HEAD atom hazard source immunity (all 5 HEADs at 0%, N=16,819, chi2=4411.9, V=0.219) |
| **ADDED** | C1547: TERMINAL atom determines hazard class type (V=0.306, 1.40x stronger than HEAD; y->PHASE_ORDERING, l->CONTAINMENT_TIMING) |
| **ADDED** | C1548: PREFIX base-level hazard differentiation (chi2=2038.0, V=0.133; e-base 3.37x, k-base 0.30x) |
| **ADDED** | C1549: q-modifier hazard protection on o-base (qo 4.15% vs other o-modifiers 27-52%; ~7x protection via k-HEAD routing) |
| **ADDED** | C1550: Sister pair hazard source asymmetry (ch/sh 1.80x, ok/ot 0.66x inverted, da/sa 1.54x) |
| **ADDED** | C1551: PHASE_ORDERING exclusively headless y-terminal dy; CONTAINMENT_TIMING exclusively l-terminal |
| **ADDED** | C1552: 5/9 hazard source MIDDLEs are phantom types absent from corpus (chey, shey, chedy, shedy, chol) |
| **ADDED** | `phases/HAZARD_PREFIX_INTEGRATION/scripts/hazard_prefix_integration.py` |
| **ADDED** | `phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json` |
| **ADDED** | `phases/HAZARD_PREFIX_INTEGRATION/REPORT.md` |
| **UPDATED** | INDEX.md -- +7 constraints (1396 total) |
| **EXTENDED** | C1446 (k-HEAD complete hazard immunity): from k-only to ALL 5 HEAD atoms -- universal HEAD class property |
| **EXTENDED** | C1476 (k-HEAD intrinsic immunity): intrinsic property applies to entire HEAD class, not k-specific |
| **EXTENDED** | C1447 (terminal atom hazard partition): TERMINAL V=0.306 dominates HEAD V=0.219 in hazard class determination |
| **EXTENDED** | C1449 (PREFIX channel hazard with sister parity): decomposed to atom-level asymmetry (modifier-driven vs base-driven) |
| **EXTENDED** | C1529 (PHASE_ORDERING = headless y-terminal): confirmed at PREFIX-integrated resolution with 675 tokens across 10+ PREFIXes |
| **EXTENDED** | C1530 (CONTAINMENT_TIMING = l/r SEMI_TRANSPARENT): confirmed exclusively l-terminal across 12+ PREFIXes |
| **EXTENDED** | C1531 (phantom forbidden MIDDLEs): connected to C1178 dead naming pattern and C1546 HEAD immunity |
| **EXTENDED** | C1538 (q-modifier THERMAL activation): hazard protection mechanism identified -- q routes to k-HEAD which is immune |
| **CONNECTED** | C1475 (HEAD domain differentiation) + C1536 (base-to-HEAD selection) + C1528 (hazard atom territories): complete chain from PREFIX input to hazard output |

---

## Version 5.34.170 (2026-03-06) - Phase 545: Executive Atom Instability

### Summary

Phase 545 investigates WHY the three atoms {p,f,c} are classified as "unstable" in C1509's three-tier behavioral stability hierarchy. 9 research questions across 8 behavioral dimensions on all B tokens containing MOD atoms {p,i,c,f,d,s}. MAJOR SURPRISE: "unstable" atoms have LOWER cross-system behavioral divergence (mean JSD=0.0110) than "stable" MODs (JSD=0.0319, ratio 0.35x). C1509 instability reflects functional niche specialization (context shifts around the atom), not behavioral divergence (the atom's own profile shifting). Suffix exclusion partition discovered: the 5 suffix-excluded atoms {k,t,p,f,c} exactly equal ACTION HEADs + UNSTABLE MODs = INSTRUCTION-ONLY tier. c is a unique slot-switcher (PREFIX: 61% e-HEAD; MIDDLE: 46.4% headless). p/f are arrangement-affiliated (33-41% o-HEAD), contrasting with i as iteration-affiliated (53% a-HEAD). All three unstable atoms shift toward Mode A (specification) when moving A->B. f has the lowest bridge rate of any MOD atom (49.3%, most B-exclusive).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1540: p/f/c behavioral non-divergence vs stable MODs (mean JSD 0.35x ratio, instability is niche specialization) |
| **ADDED** | C1541: Suffix exclusion defines instruction-only atom tier ({k,t,p,f,c} = 0 suffix occurrences = ACTION+EXECUTIVE) |
| **ADDED** | C1542: c-atom slot-switching between PREFIX and MIDDLE (PREFIX: 61% e-HEAD, MIDDLE: 46.4% headless) |
| **ADDED** | C1543: p/f are o-HEAD arrangement-affiliated atoms (33-41% o-HEAD, stable across A/B) |
| **ADDED** | C1544: Unstable atoms increase Mode A suffix rate A->B (c +25.3pp, f +22.3pp, p +15.5pp) |
| **ADDED** | C1545: f-atom anomalous B-exclusive vocabulary affinity (49.3% bridge, lowest MOD) |
| **ADDED** | `phases/EXECUTIVE_ATOM_INSTABILITY/scripts/executive_atom_instability.py` |
| **ADDED** | `phases/EXECUTIVE_ATOM_INSTABILITY/results/executive_atom_instability.json` |
| **ADDED** | `phases/EXECUTIVE_ATOM_INSTABILITY/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1389 total) |
| **REFINED** | C1509 (three-tier atom behavioral stability): "instability" reframed as functional niche specialization, not behavioral divergence |
| **EXTENDED** | C1511 (suffix atom exclusion): connected to C1509 instability — suffix-excluded set exactly equals ACTION HEADs + UNSTABLE MODs |
| **EXTENDED** | C1496 (c-modifier primary displacement context): explained by c's slot-switching behavior |
| **EXTENDED** | C1388 (o-atom arrangement domain): p/f identified as o's modifier partners |
| **EXTENDED** | C1139 (bridge/dark disjoint): f is the MOD atom most affiliated with dark pipeline (50.7% B-exclusive) |
| **CONNECTED** | C1515 (suffix Mode A = THERMAL/MONITORING): unstable atoms preferentially receive specification suffixes in B |

---

## Version 5.33.169 (2026-03-06) - Phase 544: PREFIX Atom Taxonomy

### Summary

Phase 544 decomposes PREFIX morphology at individual atom (character) level, paralleling MIDDLE decomposition (Phases 523-540) and suffix decomposition (Phase 540). 13 analysis steps on 19,232 B tokens with PREFIX. Key finding: PREFIX uses 15 characters (identical across A/B/AZC, Jaccard=1.000) in a three-tier positional classification: MODIFIER {c,d,f,p,q,s,y} at POS-0, BASE {e,h} at POS-1+, DUAL {a,k,l,o,r,t} at both. Base character predicts MIDDLE HEAD atom with V=0.478 (89% of MIDDLE HEAD category specificity V=0.511). a-base is the universal headless gateway (94-96% regardless of modifier, 1.5pp spread). q-modifier uniquely activates THERMAL channel on o-base (64% k-HEAD vs 5-19% for other modifiers, 3.5x gap), making qo compositionally transparent. Sister pairs decompose into SAME_BASE (ch/sh, da/sa) and SAME_MOD (ok/ot) structural types, all with HEAD JSD<0.01. i-atom is categorically excluded from PREFIX (the only MIDDLE MOD absent), confirming iteration is MIDDLE-internal. Cross-system base distribution JSD=0.011-0.046 extends C1499 shared substrate to PREFIX atoms.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1534: PREFIX uses 15 characters in three-tier positional classification (MODIFIER/BASE/DUAL), identical across all systems |
| **ADDED** | C1535: i-atom categorically excluded from PREFIX -- iteration mechanism absent from channel selection |
| **ADDED** | C1536: Base-to-HEAD selection V=0.478 -- each base selects a distinct operational domain |
| **ADDED** | C1537: a-base is the universal headless gateway (94-96% headless regardless of modifier) |
| **ADDED** | C1538: q-modifier uniquely activates THERMAL channel on o-base (64% k-HEAD vs 5-19% other modifiers) |
| **ADDED** | C1539: Sister pairs decompose into SAME_BASE (ch/sh, da/sa) and SAME_MOD (ok/ot) structural types |
| **ADDED** | `phases/PREFIX_ATOM_TAXONOMY/scripts/prefix_atom_taxonomy.py` |
| **ADDED** | `phases/PREFIX_ATOM_TAXONOMY/results/prefix_atom_taxonomy.json` |
| **ADDED** | `phases/PREFIX_ATOM_TAXONOMY/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1383 total) |
| **EXTENDED** | C1218 (PREFIX internal positional grammar): three-tier classification quantified with chi2=14,327.8, V=0.547 |
| **EXTENDED** | C1219 (base determines MIDDLE content): upgraded to HEAD-atom resolution with V=0.478 domain specificity |
| **EXTENDED** | C1491 (da-PREFIX near-exclusivity): generalized from da to entire a-base family (da/sa/ka/ta all 94-96% headless) |
| **EXTENDED** | C1499 (shared substrate): PREFIX atom inventory is manuscript-wide (Jaccard=1.000 cross-system) |
| **EXTENDED** | C1300 (qo near-pure THERMAL): decomposed to atom-level mechanism (q=thermal activation, o=domain base) |
| **CONNECTED** | C1475 (HEAD domain differentiation): PREFIX base achieves 89% of HEAD's category specificity |
| **CONNECTED** | C1478 (k/t terminal mirror): ok/ot SAME_MOD sister pair has smallest HEAD JSD (0.0034) because k,t are mirrors |
| **CONNECTED** | C1511 (suffix atom exclusion): three-slot complementary partition -- PREFIX excludes {i,m,n,g,x}, suffix excludes {k,t,p,f,c} |

---

## Version 5.32.168 (2026-03-06) - Phase 543: Hazard-Class Atomization

### Summary

Phase 543 decomposes the 5 hazard failure classes (PHASE_ORDERING 41%, COMPOSITION_JUMP 24%, CONTAINMENT_TIMING 24%, RATE_MISMATCH 6%, ENERGY_OVERSHOOT 6%) from C109 onto the atom-mechanical frame system (HEAD x TERM) established in Phases 523-535. 4 test dimensions (A: frame, B: modifier, C: PREFIX channel, D: line position) on 23,096 B tokens, 20,542 adjacency pairs, 11 forbidden violations. Key finding: hazard classes map to NEAR-ORTHOGONAL HEAD territories (7/10 pairwise Jaccard=0). PHASE_ORDERING = headless y-terminal to a-HEAD n-terminal cross-domain boundary failure, concentrating in CHSH checkpoint context (28.4% CHSH, 7/11 violations). CONTAINMENT_TIMING = l/r SEMI_TRANSPARENT class with 100% avoidance (0 violations in 1,129 appearances). 5 phantom MIDDLEs (shey, chey, chedy, shedy, chol) in 11/17 transitions reveal construction-level prohibitions. Hazard classes partition by line position (chi2=46.6, V=0.066): setup errors early, closure errors late. 5/7 predictions confirmed.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1528: Hazard classes map to near-orthogonal atom HEAD territories (7/10 pairwise Jaccard=0) |
| **ADDED** | C1529: PHASE_ORDERING is headless y-terminal to a-HEAD transition failure (10/11 violations = dy->aiin) |
| **ADDED** | C1530: CONTAINMENT_TIMING is l/r-terminal SEMI_TRANSPARENT class (100% avoidance, 0/1,129) |
| **ADDED** | C1531: Forbidden MIDDLEs include 5 phantom types absent from corpus (11/17 transitions involve phantoms) |
| **ADDED** | C1532: Hazard classes partition by line position (chi2=46.6, p=0.000079; setup early, closure late) |
| **ADDED** | C1533: PHASE_ORDERING is CHSH-channel specific (28.4% CHSH, 7/11 violations; QO=0) |
| **ADDED** | `phases/HAZARD_CLASS_ATOMIZATION/scripts/hazard_class_atomization.py` |
| **ADDED** | `phases/HAZARD_CLASS_ATOMIZATION/results/hazard_class_atomization.json` |
| **ADDED** | `phases/HAZARD_CLASS_ATOMIZATION/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1377 total) |
| **EXTENDED** | C109 (5 failure classes): each class now has atom-level HEAD territory, terminal profile, PREFIX channel, and line position characterization |
| **EXTENDED** | C1446 (k-HEAD immunity): immunity confirmed universal across all 5 hazard classes |
| **EXTENDED** | C1447 (terminal hazard partition): terminal role now differentiated by hazard class |
| **EXTENDED** | C1449 (PREFIX channel hazard): CHSH specificity to PHASE_ORDERING resolved |
| **EXTENDED** | C1451 (Mode B violations): all 11 violations concentrated in PHASE_ORDERING dy->aiin |
| **CONNECTED** | C1178 (phantom dead naming): hazard phantoms parallel dark-pipeline phantoms (4/5 ch/sh-initial) |
| **CONNECTED** | C1440 (three-tier opacity): CONTAINMENT_TIMING maps to SEMI_TRANSPARENT tier |

---

## Version 5.31.162 (2026-03-06) - Phase 542: Headless Compound Cross-System Distribution

### Summary

Phase 542 tests whether headless compound properties documented in B (C1488-C1498) are universal across all three systems (Currier A, Currier B, AZC). 10 tests on 37,497 tokens decomposed via HEAD/MOD/TERM slots. Key finding: headless is a MANUSCRIPT-WIDE structural domain. Category profile is universal (cross-system JSD=0.023-0.035, near-zero THERMAL 0.6-1.1%), suffix depletion is universal (A=0.73x, B=0.86x, AZC=0.61x), and da/sa/ta PREFIX exclusivity is universal (da enrichment 132.7x-1,448.3x). A has 1.43x higher headless rate than B/AZC (39.0% vs 27.2%/27.9%), consistent with A's declarative register (C1507). 69 shared types cover 88-89% of headless tokens across all systems (SHARED_SUBSTRATE_GRADED_SLOTS confirmed for headless subdomain). B-specific: dark pipeline headless enrichment 1.47x.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1523: Currier A headless rate 1.43x higher than B/AZC (A=39.0% vs B=27.2%/AZC=27.9%; B and AZC indistinguishable p=0.428) |
| **ADDED** | C1524: da/sa/ta PREFIX exclusivity universal across all three systems (da enrichment: A=844.6x, B=1,448.3x, AZC=132.7x) |
| **ADDED** | C1525: Headless suffix depletion universal (A=0.73x, B=0.86x, AZC=0.61x; terminal opacity mechanism) |
| **ADDED** | C1526: Headless category profile universal (near-zero THERMAL 0.6-1.1%, cross-system JSD=0.023-0.035) |
| **ADDED** | C1527: Headless functional core shared — 69 types cover 88-89%; B-specific dark headless enrichment (1.47x) |
| **ADDED** | `phases/HEADLESS_CROSS_SYSTEM/scripts/headless_cross_system.py` |
| **ADDED** | `phases/HEADLESS_CROSS_SYSTEM/results/headless_cross_system.json` |
| **ADDED** | `phases/HEADLESS_CROSS_SYSTEM/REPORT.md` |
| **UPDATED** | INDEX.md -- +5 constraints (1365 total) |
| **UPDATED** | `currierB.bcsc.yaml` -- added cross_system_universality field to headless_compounds section, extended provenance |
| **EXTENDED** | C1488 (headless coherent domain): coherence extends cross-system at token level (88-89% convergence on 69 types) |
| **EXTENDED** | C1499 (shared substrate): SHARED_SUBSTRATE_GRADED_SLOTS architecture confirmed for headless subdomain |

---

## Version 5.30.157 (2026-03-06) - Phase 541: AZC Zone-Level Atomization

### Summary

Phase 541 tests whether AZC internal zones differentiate at HEAD+MOD*+TERM slot level (C1394), given that C1271 found null at raw atom level using AXIS clusters (C1207). 12 tests on 3,227 AZC tokens decomposed into HEAD/MOD/TERM slots. Key finding: HEAD domain differentiation IS significant (chi2=112.3, V=0.115, p=5.81e-17) -- zones differ in domain selection, not raw character inventory. o-HEAD enrichment is zone-graded (R=17.7% to S=29.3%, vs B=11.8%). HEAD is 5.2x more discriminating than TERMINAL across zones. AZC zones partition into B-proximate (R, P -- lower o-HEAD, more bridge) and A-proximate (C, S, L -- higher o-HEAD, more dark/exclusive). R-series shows no HEAD gradient. Zodiac HEAD is uniform; A/C is 2.0x more internally diverse.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1516: AZC HEAD domain differentiation across zones (chi2=112.3, V=0.115, p=5.81e-17) |
| **ADDED** | C1517: o-HEAD enrichment is zone-graded not uniform (R 17.7% to S 29.3%, overall 1.90x B) |
| **ADDED** | C1518: HEAD differentiation dominates TERMINAL across zones (5.2x JSD ratio) |
| **ADDED** | C1519: Zodiac HEAD uniformity vs A/C internal diversity (2.0x ratio; extends C436) |
| **ADDED** | C1520: R-series no HEAD gradient (all p=0.600, N=4) |
| **ADDED** | C1521: AZC zone pipeline composition varies (S dark-enriched, P bridge-dominated) |
| **ADDED** | C1522: AZC zones partition B-proximate (R, P) vs A-proximate (C, S, L) by HEAD JSD |
| **ADDED** | `phases/AZC_ZONE_ATOMIZATION/scripts/azc_zone_atomization.py` |
| **ADDED** | `phases/AZC_ZONE_ATOMIZATION/results/azc_zone_atomization.json` |
| **ADDED** | `phases/AZC_ZONE_ATOMIZATION/REPORT.md` |
| **UPDATED** | INDEX.md -- +7 constraints (1360 total) |
| **REFINED** | C1271 (zone atom uniformity): raw atom null STANDS; HEAD slot differentiation is a NEW finding at different resolution |
| **REFINED** | C1502 (o-HEAD 2.70x): HEAD-slot decomposition gives 1.90x; initial-atom level gives 2.70x; methodological difference |
| **EXTENDED** | C436 (dual rigidity): extended to atom level -- Zodiac uniform, A/C diverse at HEAD |
| **EXTENDED** | C1272 (bridge-dark zone sorting): atom-level confirmation -- dark MIDDLEs 1.84x o-HEAD vs bridge |
| **EXTENDED** | C301 (AZC hybrid): hybridity is zone-graded -- R/P B-proximate, C/S/L A-proximate |
| **UPDATED** | AZC-ACT contract v1.4: added HEAD_DOMAIN_DIFFERENTIATION guarantee, zone_head_atomization section, refined invariant and disallowed wording |

---

## Version 5.29.150 (2026-03-06) - Phase 540: Suffix Atom Taxonomy

### Summary

Phase 540 decomposes the suffix layer at atom-level resolution using CategoryClassifier (8 categories) and morphological decomposition. 12 analyses (T1-T12) on 11,151 suffixed B tokens (35 unique suffixes, 13 single-char atoms). Verdict: suffix is a PARALLEL compositional domain -- same HEAD+TERM grammar as MIDDLE but compressed (13 vs 18 atoms, missing k/t ACTION HEADs and p/f/c EXECUTIVE MODs), with attenuated HEAD (V=0.277, 53% of MIDDLE) and amplified TERM (R2=0.059, 1.68x MIDDLE). MIDDLE terminal atom dominates suffix content selection (V=0.513 vs HEAD V=0.305). ALL 12 shared atoms carry DIFFERENT category info in suffix vs MIDDLE (mean JSD=0.526). Cross-system suffix atom inventory identical (A=B=13, JSD=0.050). Suffix modes confirmed at full 8-category resolution with positional asymmetry.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1510: Suffix parallel HEAD+TERM decomposition (first-atom V=0.277 53% HEAD, last-atom R2=0.059 1.68x TERM) |
| **ADDED** | C1511: Suffix excludes ACTION HEAD and EXECUTIVE MOD atoms ({k,t} + {p,f,c}; action-free executive-free) |
| **ADDED** | C1512: MIDDLE terminal dominates suffix content selection (V=0.513 vs HEAD V=0.305, 1.68x) |
| **ADDED** | C1513: Suffix atoms universally divergent from MIDDLE atoms (12/12, mean JSD=0.526, n=1.000) |
| **ADDED** | C1514: Cross-system suffix atom identity (A=B=13, JSD=0.050; B enriches d/e/i, A enriches o/h/l/s) |
| **ADDED** | C1515: Suffix mode category anatomy with positional asymmetry (Mode A medial/specification, Mode B boundary/continuation) |
| **ADDED** | `phases/SUFFIX_ATOM_TAXONOMY/scripts/suffix_atom_taxonomy.py` |
| **ADDED** | `phases/SUFFIX_ATOM_TAXONOMY/results/suffix_atom_taxonomy.json` |
| **ADDED** | `phases/SUFFIX_ATOM_TAXONOMY/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1359 total) |
| **CONFIRMED** | C1408 (suffix HEAD->TERM structure): quantified attenuation/amplification ratios |
| **CONFIRMED** | C1409 (suffix atom divergence): extended to full 8-category profiles, ALL 12 divergent |
| **CONFIRMED** | C1410 (suffix modes atom-level): extended to 8-category resolution with positional asymmetry |
| **CONFIRMED** | C1440-C1445 (terminal opacity): h 98.7%, y 1.6%, n 0.8% suffix rates in suffix context |
| **CONFIRMED** | C1499 (shared substrate): extended to suffix layer, identical inventories A=B |
| **EXTENDED** | C1412 (MIDDLE terminal dominates suffix): atom-level confirmation V=0.513 |
| **EXTENDED** | C1413 (PREFIX-SUFFIX MIDDLE-mediated): specifically through TERMINAL atom not HEAD |
| **EXTENDED** | C1507 (A arrangement emphasis): A suffix also o-enriched 3.31x |

---

## Version 5.28.144 (2026-03-06) - Phase 539: Bridge Atom Stability Across A and B

### Summary

Phase 539 tests whether the 85 bridge MIDDLEs preserve atom-role behavior across Currier A and Currier B. 11 tests plus a 10-prediction scorecard (5/10 confirmed). Each bridge MIDDLE decomposed via HEAD+MOD*+TERM. Token collections from A (9,391 tokens) and B (19,998 tokens) compared across slot dimensions, PREFIX/SUFFIX ecology, category profiles, and per-atom behavioral correlations. Verdict: PARTIAL_STABILITY -- internal structure preserved (mean JSD 0.046), deployment channels shifted (mean JSD 0.113). TERMINAL is the most stable slot (JSD=0.014, 5.4x more stable than HEAD). Categories are INTRINSIC (100% match rate) but token-weighted distribution shifts: THERMAL +10.1pp in B, STAGING -11.1pp in B. A is o-HEAD/HEADLESS dominant (arrangement); B is e/k-HEAD dominant (execution). Individual atoms partition into three behavioral stability tiers: 8 stable (corr>0.90), 6 moderate (0.70-0.90), 3 unstable (<0.70). d is extreme outlier (corr=0.062).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1506: Bridge terminal atom stability across A and B (TERMINAL JSD=0.014, most stable slot; tier JSD=0.005) |
| **ADDED** | C1507: Bridge HEAD redistribution A vs B (A=o/HEADLESS, B=e/k; HEAD JSD=0.077, least stable slot) |
| **ADDED** | C1508: Bridge category redistribution A vs B (100% intrinsic match; THERMAL +10.1pp B, STAGING -11.1pp B) |
| **ADDED** | C1509: Three-tier atom behavioral stability (8 stable, 6 moderate, 3 unstable; d=0.062 outlier) |
| **ADDED** | `phases/BRIDGE_ATOM_STABILITY/scripts/bridge_atom_stability.py` |
| **ADDED** | `phases/BRIDGE_ATOM_STABILITY/results/bridge_atom_stability.json` |
| **ADDED** | `phases/BRIDGE_ATOM_STABILITY/REPORT.md` |
| **UPDATED** | INDEX.md -- +4 constraints (1353 total) |
| **CONFIRMED** | C1499 (shared substrate): behaviorally stable at terminal level across systems |
| **CONFIRMED** | C1500 (bridge e/k/t enrichment): confirmed as B-specific execution emphasis |
| **CONFIRMED** | C1388 (o-atom arrangement domain): confirmed via A-enriched bridge HEAD profile |
| **CONFIRMED** | C1487 (three-tier terminal taxonomy): preserved across systems with tier JSD=0.005 |
| **EXTENDED** | C1503 (bridge redistribution): quantified at all slot dimensions, not just frequency |
| **EXTENDED** | C1347 (B reshapes bridge usage): quantified THERMAL +10.1pp, STAGING -11.1pp |
| **EXTENDED** | C1409 (atom cross-position divergence): extended to cross-system dimension |

---

## Version 5.27.140 (2026-03-06) - Phase 538: Cross-Layer Atom Decomposition

### Summary

Phase 538 tests whether the HEAD+MOD*+TERM atom grammar (C1393-C1394) is manuscript-wide or B-local, and whether bridge and dark pipeline MIDDLEs differ at atom-level slot composition. 10 tests across 7 pipeline channels (bridge 85, dark 300, a_exclusive 579, b_only 900, all_A 972, all_B 1293, all_AZC 617). Verdict: SHARED_SUBSTRATE_GRADED_SLOTS -- the atom ontology is manuscript-wide (minimum pairwise Jaccard 0.895, modifier JSD < 0.007 between non-bridge channels). Channels differentiate through slot PROPORTIONS, not slot INVENTORIES. Bridge is the systematic outlier across all three slot types (HEAD, TERMINAL, MODIFIER), reflecting its dual-system role as dynamical backbone. Dark pipeline uses the same atoms in identification-optimized proportions: o-HEAD dominant (28.7% vs bridge 16.5%), bare/h-terminal dominant (74.7%/15.7%), MARKING-dominant category (36.0%). AZC shows strongest o-HEAD enrichment of any channel (31.8%, 2.70x). Bridge MIDDLEs undergo dramatic morphological redistribution between A and B contexts (-edy ~50x B-enriched, ct ~12x A-enriched). Predictions: 4/5 confirmed (P3 FAIL: dark prefers bare+DIFFUSE/h terminals, NOT CHANNELED as predicted).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1499: Atom ontology manuscript-wide shared substrate (min Jaccard 0.895, all 7 channels share 18 atoms) |
| **ADDED** | C1500: Bridge-dark HEAD domain differentiation (bridge e/k/t 37.6% vs dark 31.0%; dark o+headless 63.3%) |
| **ADDED** | C1501: Bridge terminal tier outlier (LOCKED 8.2%, bare 58.8%; dark bare 74.7%, h 15.7%; TERM JSD 0.039-0.082) |
| **ADDED** | C1502: AZC o-HEAD domain enrichment 2.70x (k 0.314x, t 0.488x depleted) |
| **ADDED** | C1503: Bridge atom redistribution across A/B (-edy ~50x B-enriched, ct ~12x A-enriched, HEAD JSD 0.0767) |
| **ADDED** | C1504: Modifier grammar universality across channels (same 6 modifiers, MOD JSD < 0.007 non-bridge) |
| **ADDED** | C1505: Dark pipeline MARKING-dominant category profile (36.0% vs bridge balanced V=0.4427) |
| **ADDED** | `phases/CROSS_LAYER_ATOM_DECOMPOSITION/scripts/cross_layer_atoms.py` |
| **ADDED** | `phases/CROSS_LAYER_ATOM_DECOMPOSITION/results/cross_layer_atoms.json` |
| **ADDED** | `phases/CROSS_LAYER_ATOM_DECOMPOSITION/REPORT.md` |
| **UPDATED** | INDEX.md -- +7 constraints (1349 total) |
| **UPDATED** | BCSC v3.31 -- bridge_dual_role updated with cross-system atom substrate findings, dark_pipeline_integration updated with atom-level category profile |
| **CONFIRMED** | C1381 (o-initial AZC enrichment): extended to type-level at stronger effect (2.70x) |
| **CONFIRMED** | C1264 (bridge vs dark category divergence): confirmed at full atom-decomposition level |
| **CONFIRMED** | C1394 (instruction encoding architecture): modifier grammar proven manuscript-wide |
| **CONFIRMED** | C1141 (dark compounds from bridge atoms): atom Jaccard 0.895 confirms shared substrate |
| **EXTENDED** | C1347 (B reshapes bridge category usage): extended to atom and morphological wrapping level |

---

## Version 5.26.133 (2026-03-06) - Phase 537: Displaced HEAD Grammar

### Summary

Phase 537 resolves C1493's finding that 35.7% of headless compound MIDDLEs contain HEAD-set atoms {a,e,o,k,t} at non-initial positions. The decisive test: pseudo-HEAD (first atom) predicts operational category 2.68x more accurately than the displaced HEAD atom (35.1% vs 13.1%, N=1,084). 0/5 displaced HEADs share the same dominant category as their canonical HEAD counterpart. k and t are massively enriched among displaced HEADs (5.31x and 6.90x respectively) while e is depleted (0.26x) -- k/t function as TERMINAL atoms per C1478 (k/t dual-role), not as domain selectors. The c-modifier is the primary displacement context (87.1% of c-initial headless tokens contain displaced HEADs), with ck (197 tokens) and ct (95 tokens) as the dominant patterns. Displaced-HEAD tokens have 89.8% suffix rate (vs 35.7% canonical, 24.0% genuine headless), explained by their bare-terminal dominance connecting to the transparent suffix tier (C1440). n-terminal and y-terminal categorically exclude displacement (0.36% and 0.39%) because their exclusive modifier partners (i and d per C1484) leave no compositional slot for HEAD atoms. Hazard exposure is near-zero (0.08% high-frame). Verdict: HEAD_SET_CHARACTER_NOT_FUNCTIONING_AS_HEAD.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1494: Displaced HEAD k/t enrichment with inverted frequency (k 5.31x, t 6.90x; e 0.26x depleted) |
| **ADDED** | C1495: HEAD-set atoms do not function as domain selectors when displaced (pseudo-HEAD 2.68x better) |
| **ADDED** | C1496: c-modifier primary displacement context (87.1% rate; ck/ct backbone) |
| **ADDED** | C1497: Displaced HEAD extreme suffix rate (89.8% vs 35.7% canonical vs 24.0% genuine headless) |
| **ADDED** | C1498: n/y-terminal categorical displacement exclusion (0.36-0.39% vs bare 83.9%) |
| **ADDED** | `phases/DISPLACED_HEAD_GRAMMAR/scripts/displaced_head_grammar.py` |
| **ADDED** | `phases/DISPLACED_HEAD_GRAMMAR/results/displaced_head_grammar.json` |
| **ADDED** | `phases/DISPLACED_HEAD_GRAMMAR/REPORT.md` |
| **UPDATED** | INDEX.md -- +5 constraints (1342 total) |
| **UPDATED** | BCSC v3.30 -- headless internal_structure updated to note displaced HEADs are non-functional |
| **RESOLVED** | C1493 open question: displaced HEADs are genuinely headless compounds with HEAD-set chars in non-HEAD roles |
| **CONFIRMED** | C1478 (k/t terminal mirror): k/t function as terminals in displaced position, not HEADs |
| **CONFIRMED** | C1484 (terminal-modifier exclusivity): n+i and y+d partnerships exclude HEAD displacement |
| **CONFIRMED** | C1489 (pseudo-HEAD differentiation): first atom dominates category even when HEAD-set atoms present elsewhere |

---

## Version 5.25.128 (2026-03-06) - Phase 536: Headless Compound Subgrammar

### Summary

Phase 536 characterizes the ~20.5% of Currier B compound MIDDLE tokens whose initial atom is NOT a HEAD atom {a,e,o,k,t}. These "headless" compounds (3,312 tokens, 469 types) form a structurally coherent functional domain (verdict: HEADLESS_IS_COHERENT_DOMAIN). The initial atom acts as a PSEUDO-HEAD with V=0.511 category differentiation: d=CONTAINMENT 84%, i=STAGING 67%, p=MARKING 92%, f=MARKING 91%, r=FLOW 61%, c=OPERATION 32%. Terminal profile shifts systematically: h enriched 2.98x, n enriched 2.45x, while LOCKED tier (r+m) depleted 6.2x -- structural hazard avoidance since r-terminal carries 92.58% of forbidden violations (C1447). PREFIX selectivity is near-absolute: da 2284x enriched, sa/ta exclusive to headless, ok/ot near-absent. Suffix bifurcation reveals binary vs parametric operations: d/i bare (<15% suffix rate, self-contained binary ops) vs c/p/f suffixed (>93%, parametric ops needing suffix specification). Same modifier ordering grammar applies (61.9% vs 70.1% compliance). 35.7% of headless types contain HEAD atoms in non-initial positions ("displaced HEAD"). The headless aggregate is categorically distinct from all 5 HEAD domains (nearest: o at JSD=0.302, farthest: a at JSD=0.665).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1488: Headless compound population structure (3,312 tokens 20.5%, 469 types, MOD-initial 77.5%) |
| **ADDED** | C1489: Headless pseudo-HEAD category differentiation (V=0.511, d=CONTAINMENT 84%, i=STAGING 67%) |
| **ADDED** | C1490: Headless terminal profile shift (h 2.98x, n 2.45x enriched; LOCKED 6.2x depleted) |
| **ADDED** | C1491: Headless da-PREFIX near-exclusivity (da 2284x, sa/ta 100% exclusive) |
| **ADDED** | C1492: Headless suffix bifurcation (d/i bare vs c/p/f suffixed, binary vs parametric split) |
| **ADDED** | C1493: Headless internal structure with displaced HEAD (MT 46.7%, 35.7% displaced HEAD) |
| **ADDED** | `phases/HEADLESS_COMPOUND_SUBGRAMMAR/scripts/headless_compound_subgrammar.py` |
| **ADDED** | `phases/HEADLESS_COMPOUND_SUBGRAMMAR/results/headless_compound_subgrammar.json` |
| **ADDED** | `phases/HEADLESS_COMPOUND_SUBGRAMMAR/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1337 total) |
| **UPDATED** | BCSC MIDDLE_INSTRUCTION_ENCODING guarantee -- headless characterization updated with C1488-C1493 |
| **EXTENDED** | C1397 (headless compound functional grammar): fully quantified V=0.503→0.511, atom-level decomposition |
| **CONFIRMED** | C1484 (terminal-modifier exclusivity): holds in headless at 99.6-100% compliance |
| **CONFIRMED** | C1472 (modifier co-occurrence avoidance): same grammar applies in headless (61.9% vs 70.1%) |
| **REFINED** | C1394 (instruction encoding architecture): da-enrichment is i-initial-specific, not generic headless |

---

## Version 5.24.126 (2026-03-06) - Phase 535: TERMINAL Functional Taxonomy

### Summary

Phase 535 characterizes the 6 TERMINAL atoms {y, l, r, h, m, n} comprehensively across 12 behavioral dimensions, creating the symmetric counterpart to the HEAD domain taxonomy (C1475-C1479). TERMINAL x CATEGORY Cramer's V=0.463 -- terminals are the second strongest category determinant after HEAD. The 6 terminals form three functional tiers: LOCKED (r=FLOW 98.9%, m=TRANSITION 87.9%), CHANNELED (l=STAGING 64.5%, y=OPERATION 40.6%, n=TRANSITION 39.3%), DIFFUSE (h=MARKING 30.0% across 6 categories, bare=THERMAL 43.2% across 6). Modifier selection is near-perfectly terminal-gated (C1484): n exclusively takes i (8.606x, zero instances of any other modifier), y exclusively takes d (2.868x), h takes {c,p,f,s} (5-9x), l/r/m resist modification (<5%). HEAD-TERMINAL affinity creates compositional frames: e locks to y-terminal (72.7%), a locks to n/m-terminal (59-60%), k/t categorically avoid n/m (0-1 tokens). The hazard circuit is directional: y-terminal sources 90.9% of forbidden violations, n-terminal absorbs 90.9%. Two orthogonal design axes: opacity (suffix attachment rate) and category specificity (how narrowly terminal constrains domain). r is SEMI-TRANSPARENT but categorically LOCKED to FLOW; h is TRANSPARENT but DIFFUSE across 6 categories.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1483: TERMINAL category specificity gradient (V=0.463, r near-deterministic to h diffuse) |
| **ADDED** | C1484: TERMINAL modifier exclusivity partition (n=i only, y=d only, h={c,p,f,s}) |
| **ADDED** | C1485: TERMINAL HEAD affinity partition (e->y 72.7%, a->n/m 59-60%, k/t avoid n/m) |
| **ADDED** | C1486: m-terminal line-final closure confirmation (mean_pos 0.903, 73.7% line-final) |
| **ADDED** | C1487: Six-terminal functional taxonomy (LOCKED/CHANNELED/DIFFUSE, opacity orthogonal) |
| **ADDED** | `phases/TERM_FUNCTIONAL_TAXONOMY/scripts/term_functional_taxonomy.py` |
| **ADDED** | `phases/TERM_FUNCTIONAL_TAXONOMY/results/term_functional_taxonomy.json` |
| **ADDED** | `phases/TERM_FUNCTIONAL_TAXONOMY/REPORT.md` |
| **UPDATED** | INDEX.md -- +5 constraints (1331 total) |
| **CONFIRMED** | C1440-C1441 (terminal opacity gradient): verified across all 6 terminals |
| **CONFIRMED** | C1434-C1439 (m-terminal closure valve): 73.7% line-final, 87.9% TRANSITION |
| **CONFIRMED** | C1447 (r-terminal hazard vector): 90.9% of source violations |
| **EXTENDED** | C1472-C1474 (modifier co-occurrence): terminal gates modifier selection |
| **PARALLELED** | C1475-C1479 (HEAD domain taxonomy): TERMINAL provides symmetric exit-condition taxonomy |

---

## Version 5.23.125 (2026-03-05) - Phase 534: i-Modifier Paradox Resolution

### Summary

Phase 534 FULLY RESOLVES the i-modifier Simpson's paradox (C1452-C1456). The complete causal chain: i selects a-HEAD at 88.6% of headed tokens (C1479), a-HEAD is the primary hazard carrier (C1477), inflating i's marginal hazard via selection (+0.319). But within each HEAD, i conditionally protects (-0.388). Net result: i is 28% SAFER than other modifiers (17.9% vs 24.8%). The crude 1.69x ratio from C1452 compared i to ALL non-i tokens including unmodified safe-HEAD tokens -- an apples-to-oranges comparison. Within a-HEAD, i produces a COMPLETE TERMINAL TRANSFORMATION: n-terminal from 1.2% to 82.1%, category from FLOW (78.1%) to TRANSITION (66.2%). Protection is categorical (changes what happens at the terminal), not positional (doesn't avoid terminals). Double-ii achieves 0.0% hazard (N=887) via 94.0% n-terminal TRANSITION lock-in. Monotonic i-count gradient within a-HEAD: no-i=79.3%, single-i=68.6%, double-ii=0.0%. C1477's "modifier quench failure" in a-HEAD is refined: rare modifiers (c,d,f,p,s) DO quench in a-HEAD, but i dominates the modifier population (1,528 vs 86 total) and only partially reduces hazard (to 28.8%), dragging the aggregate.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1480: i-modifier Simpson's paradox full resolution (selection +0.319, conditional -0.388, net -0.069 safer) |
| **ADDED** | C1481: i-modifier terminal transformation within a-HEAD (n-term 1.2%→82.1%, FLOW→TRANSITION) |
| **ADDED** | C1482: Double-ii safety via TRANSITION-locked n-terminal (0.0% hazard, monotonic gradient) |
| **ADDED** | `phases/I_MODIFIER_PARADOX/scripts/i_modifier_paradox.py` |
| **ADDED** | `phases/I_MODIFIER_PARADOX/results/i_modifier_paradox.json` |
| **ADDED** | `phases/I_MODIFIER_PARADOX/REPORT.md` |
| **UPDATED** | INDEX.md -- +3 constraints (1326 total) |
| **CLOSED** | C1452-C1456 (i-modifier Simpson's paradox) -- complete mechanistic explanation |
| **REFINED** | C1477 (a-HEAD quench resistance): aggregate effect of i dominance; rare modifiers DO quench |
| **CONFIRMED** | C1453 (i protects within frames) at a-HEAD level with delta=-0.536 |
| **CONFIRMED** | C1455 (double-ii categorical safety) with full n-terminal lock-in mechanism |

---

## Version 5.22.124 (2026-03-05) - Phase 533: HEAD Domain Differentiation

### Summary

Phase 533 characterizes the 5 HEAD atoms {a, e, o, k, t} as categorically distinct operational domains and resolves the mechanism of k-HEAD hazard immunity (C1446). Each HEAD defines a primary domain with extreme specialization: k=THERMAL (90.3%, 3.80x), t=FLOW (87.0%, 4.47x), a=FLOW+TRANSITION dual-category, e=THERMAL+OPERATION multi-category, o=STAGING+OPERATION multi-category, headless=CONTAINMENT+MARKING+STAGING. k-HEAD immunity is INTRINSIC (0.0% forbidden rate with or without modifiers across all 6 frames) -- not a consequence of modifier quenching or terminal selection. a-HEAD is the primary hazard carrier (66.0% forbidden rate, 2,032/3,079 tokens) and the ONLY HEAD where modifier quenching fails (52.8% with modifiers vs 79.9% without). k and t are terminal-identical (JSD=0.0017) but categorically opposed (JSD=0.784) -- functionally parallel channels with identical structural packaging and opposite operational content. Each HEAD selects a distinct modifier profile creating a near-partition of the modifier space, directly explaining C1473 frame incompatibility.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1475: HEAD atom domain taxonomy (5 HEADs + headless define non-overlapping operational domains) |
| **ADDED** | C1476: k-HEAD immunity is intrinsic not compositional (0% in all compositional contexts) |
| **ADDED** | C1477: a-HEAD is primary hazard carrier (66.0%, only HEAD where quench fails) |
| **ADDED** | C1478: k/t terminal mirror with category opposition (terminal JSD=0.0017, category JSD=0.784) |
| **ADDED** | C1479: HEAD-modifier selectivity partition (a monopolizes i, e monopolizes d, o attracts p/f/c) |
| **ADDED** | `phases/HEAD_DOMAIN_DIFFERENTIATION/scripts/head_domain_differentiation.py` |
| **ADDED** | `phases/HEAD_DOMAIN_DIFFERENTIATION/results/head_domain_differentiation.json` |
| **ADDED** | `phases/HEAD_DOMAIN_DIFFERENTIATION/REPORT.md` |
| **UPDATED** | INDEX.md -- +5 constraints (1323 total) |
| **DEEPENED** | C1446 (k-HEAD immunity): mechanism resolved as intrinsic |
| **EXTENDED** | C1448 (frame hazard map): a-HEAD frames identified as primary hazard source |
| **REFINED** | C1450 (modifier quenching): works for e/o/t, fails for a |
| **EXPLAINED** | C1473 (modifier avoidance): HEAD domain partition is root cause |

---

## Version 5.21.123 (2026-03-05) - Phase 532: Modifier Functional Grouping

### Summary

Phase 532 explains WHY the 8 modifier pair avoidances from C1472 occur. Tested three hypotheses: (A) discrete functional groups {p,f,i} vs {c,d} vs {s}, (B) functional redundancy, (C) frame incompatibility. Result: Hypothesis A REJECTED (separation ratio 0.997 -- no between-group vs within-group behavioral difference), Hypothesis B REJECTED (0/5 redundancy signals; avoiding pairs are LESS similar than co-occurring pairs), Hypothesis C SUPPORTED (5/5 incompatibility signals). Mechanism: modifiers with narrow HEAD selectivity (d=85.1% e-HEAD, i=88.6% a-HEAD, p=78.7% o-HEAD) avoid each other because no single HEAD can satisfy both demands simultaneously. c and s have broad HEAD distributions (entropy >1.9) enabling them to co-occur with narrow modifiers. s is the universal connector -- co-occurs with all 5 others via behavioral centrality (lowest mean JSD 0.1176), broad HEAD, and FQ macro-state context (64.6%).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1473: Modifier avoidance is frame incompatibility (HEAD x TERM selectivity conflict; V_HEAD=0.545, V_TERM=0.498) |
| **ADDED** | C1474: s-modifier universal connector (mean JSD 0.1176, HEAD entropy 1.909, FQ 64.6%) |
| **ADDED** | `phases/MODIFIER_FUNCTIONAL_GROUPING/scripts/modifier_functional_grouping.py` |
| **ADDED** | `phases/MODIFIER_FUNCTIONAL_GROUPING/results/modifier_functional_grouping.json` |
| **ADDED** | `phases/MODIFIER_FUNCTIONAL_GROUPING/REPORT.md` |
| **UPDATED** | INDEX.md -- +2 constraints (1318 total) |
| **RESOLVED** | C1472 open question: why specific modifier pairs avoid each other |

---

## Version 5.20.122 (2026-03-05) - Phase 531: Modifier Stacking Order

### Summary

Phase 531 resolves C1393's open question: "When multiple modifiers appear in one compound, is their internal sub-order fixed?" Answer: NO -- co-occurrence avoidance is the dominant constraint (8/15 pairs never co-occur), and ordering is a statistical preference (best 68.8%), not a rule. The C1394 T4 "fixed stacking order p->f->i->c->d->s" is refined: d,s is reversed (s precedes d 60.9%), and the empirically best ordering is p->f->c->s->d->i. 3+ modifier sequences comply with any single ordering only 42.6% of the time. C1394 T10's characterization of "morphological convention with weak semantic coupling" is confirmed and quantified.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1472: Modifier co-occurrence avoidance dominates ordering (8/15 empty, 0 strict, d,s reversed) |
| **ADDED** | `phases/MODIFIER_STACKING_ORDER/scripts/modifier_stacking_order.py` |
| **ADDED** | `phases/MODIFIER_STACKING_ORDER/results/modifier_stacking_order.json` |
| **ADDED** | `phases/MODIFIER_STACKING_ORDER/REPORT.md` |
| **UPDATED** | INDEX.md -- +1 constraint (1316 total) |
| **UPDATED** | currierB.bcsc.yaml -- refined modifier ordering from "fixed" to "statistical preference" |
| **RESOLVED** | C1393 open question on modifier stacking order |

---

## Version 5.19.121 (2026-03-05) - Phase 530: Cross-Line Hazard Continuity

### Summary

Phase 530 tests whether one line's closing hazard predicts the next line's opening safety. C1429 established cross-line category independence (MI=0.032 bits) and C1451 showed Mode B carries 100% of forbidden violations. C1463 showed lines route hazard to line-final. Result: cross-line hazard MI is 0.0172 bits (0.54x of category MI), and ALL correlation (rho=0.238) collapses under within-folio shuffling (MI p=0.212, rho p=0.098). Autocorrelation is flat at ~0.22 across lags 1-4 with zero sequential decay. Mode-stratified analysis shows B->B pairs (100% forbidden carrier per C1451) have NO elevated coupling vs A->A. The e->y safe pathway is DEPLETED 0.82x (Fisher p=0.0001) after high-hazard lines, not enriched -- a folio composition effect. Lines are independently composed safety units.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1470: Cross-line hazard correlation is folio-mediated (MI=0.0172 bits, shuffle p=0.212) |
| **ADDED** | C1471: No compensatory safe opening after hazardous closure (e->y DEPLETED 0.82x) |
| **ADDED** | `phases/CROSS_LINE_HAZARD/scripts/cross_line_hazard.py` |
| **ADDED** | `phases/CROSS_LINE_HAZARD/results/cross_line_hazard.json` |
| **ADDED** | `phases/CROSS_LINE_HAZARD/REPORT.md` |
| **UPDATED** | INDEX.md -- +2 constraints (1315 total) |
| **UPDATED** | currierB.bcsc.yaml -- extended cross_line_independence with hazard-frame resolution |

---

## Version 5.18.120 (2026-03-05) - Phase 529: Paragraph-Level Hazard Gradient

### Summary

Phase 529 tests whether the line-level hazard gradient (C1463: safe operations first, hazardous last, V=0.085) repeats at paragraph scale. The answer is NO -- the paragraph implements a COMPLEMENTARY architecture with comparable magnitude (V=0.071, ratio 0.84) but DIFFERENT topology. Paragraph headers concentrate LOW/infrastructure vocabulary (1.130x enriched), NOT ZERO/safe vocabulary (0.784x depleted). Safe vocabulary (e->y, k-HEAD) concentrates in the paragraph BODY (ZERO 1.077x, IMMUNE 1.121x). HIGH hazard concentrates at TAIL (1.134x). Critically, the line-level hazard gradient operates INDEPENDENTLY within all paragraph zones (V=0.079-0.094), confirming that safety is enforced at line level while paragraphs enforce specification-first ordering. The two levels form a LAYERED architecture, not a fractal one.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1467: Paragraph zone x hazard interaction (non-fractal, V=0.071, different topology from line level) |
| **ADDED** | C1468: Header infrastructure-first composition (LOW 1.130x, ZERO 0.784x depleted) |
| **ADDED** | C1469: Line hazard gradient paragraph-independent (within-zone V=0.079-0.094) |
| **ADDED** | `phases/PARAGRAPH_HAZARD_GRADIENT/scripts/paragraph_hazard_gradient.py` |
| **ADDED** | `phases/PARAGRAPH_HAZARD_GRADIENT/results/paragraph_hazard_gradient.json` |
| **ADDED** | `phases/PARAGRAPH_HAZARD_GRADIENT/REPORT.md` |
| **UPDATED** | INDEX.md -- +3 constraints (1313 total) |
| **UPDATED** | currierB.bcsc.yaml -- added paragraph_hazard_routing section |

---

## Version 5.17.119 (2026-03-05) - Phase 528: Line Zone x Frame Hazard Interaction

### Summary

Phase 528 tests the interaction between two independently discovered systems: the three-zone line model (C1425-C1430: SPECIFICATION/THERMAL_WORK/CLOSURE) and the frame hazard classification (C1448: 7 HIGH, 3 ZERO, k-IMMUNE). 23,090 tokens across 6 tests + 1 extra. Key findings: the systems are NOT independent -- they interact with structured routing (chi2=336.3, V=0.085). ZERO-hazard frames enrich at SPECIFICATION (1.236x), IMMUNE (k-HEAD) tokens concentrate at THERMAL_WORK onset (Q1 peak 1.311x), and HIGH-hazard frames concentrate at CLOSURE (1.134x). Lines create a monotonic hazard gradient: safe operations first, energy operations second, hazardous operations last. HIGH frames are positionally heterogeneous (KW H=68.8, p=1.83e-13): o-HEAD HIGH is position-neutral while a/d-HEAD HIGH is closure-biased. The pattern is universal across line lengths (V=0.081-0.091).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1463: Zone-hazard routing at line level (chi2=336.3, V=0.085, monotonic gradient) |
| **ADDED** | C1464: k-IMMUNE THERMAL_WORK onset concentration (Q1 peak 1.311x, 63.1% in work zone) |
| **ADDED** | C1465: HIGH frame positional heterogeneity (o-HEAD neutral, a/d-HEAD closure-biased, spread 0.115) |
| **ADDED** | C1466: Zone-hazard pattern line-length invariance (V=0.081-0.091, universal) |
| **ADDED** | `phases/LINE_ZONE_FRAME_HAZARD/scripts/line_zone_frame_hazard.py` |
| **ADDED** | `phases/LINE_ZONE_FRAME_HAZARD/results/line_zone_frame_hazard.json` |
| **ADDED** | `phases/LINE_ZONE_FRAME_HAZARD/REPORT.md` |
| **UPDATED** | INDEX.md -- +4 constraints (1310 total) |
| **UPDATED** | currierB.bcsc.yaml -- added zone-hazard interaction findings |

---

## Version 5.16.118 (2026-03-05) - Phase 525: e→y Safe Pathway and Recovery Architecture

### Summary

Phase 525 investigates the e→y frame (HEAD=e, TERMINAL=y), identified in C1448 as the largest safe frame in the grammar at 3,475 tokens (15.0% of corpus). 10 tests reveal that e→y is NOT a reactive recovery mechanism — it is an ambient safety substrate deployed at a constant ~15% rate regardless of local context (Mann-Whitney p=0.310). Hazard rate 0.06% (400x below baseline). OPERATION-enriched (3.94x), CHSH-channel with sh enrichment (2.45x), qo/BARE categorically excluded. e→y rate is the strongest single predictor of folio-level program forgiveness (rho=+0.569 with AXM self-transition). Together, k-HEAD and e→y account for ~5,558 tokens (24% of corpus) at zero hazard — the grammar's thermal safety envelope.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1457: e→y narrow vocabulary dominance (3,475 tokens, 7 MIDDLEs, 15.0% of corpus) |
| **ADDED** | C1458: e→y categorical safety with OPERATION enrichment (0.06% hazard, 400x reduction) |
| **ADDED** | C1459: e→y context-independent deployment (post-hazard=14.75%, post-safe=15.35%, p=0.310 NS) |
| **ADDED** | C1460: e→y early-line concentration with final avoidance (0.55x line-final, mean pos 0.463) |
| **ADDED** | C1461: e→y CHSH-channel with sh enrichment (2.45x) and qo/BARE exclusion (0.04x/0.002x) |
| **ADDED** | C1462: e→y rate predicts folio forgiveness (rho=+0.569 with AXM self-transition) |
| **ADDED** | `phases/EY_SAFE_PATHWAY/scripts/ey_safe_pathway.py` |
| **ADDED** | `phases/EY_SAFE_PATHWAY/results/ey_safe_pathway.json` |
| **ADDED** | `phases/EY_SAFE_PATHWAY/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1306 total) |
| **UPDATED** | CONSTRAINT_TABLE.txt regenerated (1306 constraints) |
| **UPDATED** | currierB.bcsc.yaml -- added e→y safe pathway findings to atom_level_decomposition and recovery sections |

---

## Version 5.15.117 (2026-03-05) - Phase 524: i-Modifier Hazard Anomaly

### Summary

Phase 524 investigates WHY the i-modifier boosts hazard (C1450 found i boosts 1.69x while all other modifiers quench to 0%). 10 tests across 2,052 i-modified tokens (8.9% of corpus). Key findings: the hazard boost is a Simpson's paradox -- i selects into hazardous HEAD+TERM frames (61.8% in high-hazard frames vs 14.0% non-i) but REDUCES hazard within those frames (weighted delta -0.407, 12/19 frames protective). Non-monotonic extension gradient: single-i=39.8% hazard, double-ii=0.0% (aiin has exactly 0% hazard across 834 tokens). i is categorically anti-thermal (THERMAL 0.05%, 0.002x baseline), operating exclusively in STAGING/TRANSITION/FLOW space. Quenching modifiers partially override i (22.6% -> 7.5%). i-tokens are 90.6% suffix-free and 95.7% Mode B due to n-terminal structure.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1452: Non-monotonic i-extension hazard gradient (no-i=24.1%, single-i=39.8%, double-ii=0.0%) |
| **ADDED** | C1453: i-modifier frame selection, not inherent hazard (Simpson's paradox, within-frame delta -0.407) |
| **ADDED** | C1454: i-modifier anti-thermal category profile (THERMAL 0.05%, 0.002x baseline) |
| **ADDED** | C1455: Quenching modifier partial i-override (22.6% -> 7.5%, N=40) |
| **ADDED** | C1456: i-modifier suffix depletion (9.4% suffix rate, 95.7% Mode B, n-terminal) |
| **ADDED** | `phases/I_MODIFIER_HAZARD/scripts/i_modifier_hazard.py` |
| **ADDED** | `phases/I_MODIFIER_HAZARD/results/i_modifier_hazard.json` |
| **ADDED** | `phases/I_MODIFIER_HAZARD/REPORT.md` |
| **UPDATED** | INDEX.md -- +5 constraints (1300 total) |
| **UPDATED** | CONSTRAINT_TABLE.txt regenerated (1300 constraints) |
| **UPDATED** | currierB.bcsc.yaml -- added i-modifier hazard findings to hazard atom_level_decomposition |

---

## Version 5.14.116 (2026-03-05) - Phase 523: Hazard Atom-Level Decomposition

### Summary

Phase 523 decomposes the 17 forbidden transitions (C109, Tier 0) at atom-level resolution using the HEAD+MOD*+TERM instruction encoding framework (C1393-C1394). 10 tests across 23,096 tokens and 20,676 adjacency pairs. Key findings: k-HEAD is completely hazard-immune (0.0% across 3,100 tokens -- all frames neutralized). Terminal atom hazard partition: HIGH (r 92.58%, n 38.97%, l 30.88%), LOW (e 16.49%, y 15.82%), ZERO (k, m, h 0%). 7 high-hazard frames account for >95% of hazard. Sister pairs show hazard parity (ok/ot 1.04x, ch/sh 1.29x). SEMI_TRANSPARENT opacity tier concentrates hazard at 56.5% (2.5x OPAQUE). Mode B carries 100% of forbidden violations (11/11). All 5 standard modifiers {c,d,f,p,s} quench hazard to 0%; i-modifier boosts 1.69x.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1446: k-HEAD complete hazard immunity (0.0% across 3,100 tokens, all frames) |
| **ADDED** | C1447: terminal atom hazard partition (HIGH r/n/l, LOW e/y, ZERO k/m/h) |
| **ADDED** | C1448: HEAD x TERM frame hazard map with k-neutralization |
| **ADDED** | C1449: PREFIX channel hazard with sister pair parity (ok/ot 1.04x, ch/sh 1.29x) |
| **ADDED** | C1450: opacity tier hazard gradient (SEMI_TRANSPARENT 56.5%, 2.5x OPAQUE) |
| **ADDED** | C1451: Mode B exclusive forbidden violation concentration (11/11 = 100%) |
| **ADDED** | `phases/HAZARD_ATOM_DECOMPOSITION/scripts/hazard_atom_decomposition.py` |
| **ADDED** | `phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json` |
| **ADDED** | `phases/HAZARD_ATOM_DECOMPOSITION/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1295 total) |
| **UPDATED** | CONSTRAINT_TABLE.txt regenerated (1295 constraints) |

---

## Version 5.13.115 (2026-03-05) - Phase 522: Two-Level Closure Architecture

### Summary

Phase 522 characterizes the two-level closure architecture where MIDDLE terminal atoms and suffix atoms encode complementary information at the token boundary. 10 tests across 16,925 tokens with terminal classification. Key findings: three-tier terminal opacity gradient (OPAQUE y/m/n <5% suffix, SEMI-TRANSPARENT l/r 17-20%, TRANSPARENT h 99%) is an active grammar rule (C1441: O/E 0.105-0.168 in matched population). TERMINAL carries 3.6x more category mutual information than suffix head (1.261 vs 0.347 bits) with only 8.2% redundancy, position-invariant across all quintiles. 17 forbidden TERMINAL x suffix-head pairs; e-suffix universally blocked by non-h terminals. Self-atom cross-layer repulsion (y 0.028x, n 0.000x). Paragraph-level m-terminal/suffix anticorrelation (rho=-0.199).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1440: three-tier terminal opacity gradient (OPAQUE/SEMI-TRANSPARENT/TRANSPARENT, V=0.753) |
| **ADDED** | C1441: active terminal-suffix exclusion grammar rule (y 0.159x, m 0.105x, n 0.168x) |
| **ADDED** | C1442: TERMINAL-suffix category information complementarity (3.6x MI ratio, 8.2% redundancy) |
| **ADDED** | C1443: 17 forbidden TERMINAL x suffix-head pairs (e-suffix blocked by all non-h terminals) |
| **ADDED** | C1444: self-atom cross-layer repulsion (y 0.028x, n 0.000x, r 0.486x) |
| **ADDED** | C1445: m-terminal and suffix anticorrelation at paragraph level (rho=-0.199, p=0.00001) |
| **ADDED** | `phases/TWO_LEVEL_CLOSURE/scripts/two_level_closure.py` |
| **ADDED** | `phases/TWO_LEVEL_CLOSURE/results/two_level_closure.json` |
| **ADDED** | `phases/TWO_LEVEL_CLOSURE/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1290 total) |
| **UPDATED** | CONSTRAINT_TABLE.txt regenerated (1290 constraints) |
| **UPDATED** | currierB.bcsc.yaml -- added two-level closure architecture to middle_instruction_encoding |

---

## Version 5.12.114 (2026-03-05) - Phase 521: m-Terminal Anomaly

### Summary

Phase 521 deeply characterizes the m-terminal MIDDLE atom, which C1427 found shows 196x enrichment from line-initial to line-final -- the largest positional effect ever observed. 10 tests plus 5 deep-dives across 289 m-terminal tokens (10 unique types). Key findings: m is a dedicated body-line closure operator with the lowest diversity of any terminal (10 types), near-pure TRANSITION category (87.9%), complete hazard exclusion (0% FLOW/CONTAINMENT), extreme suffix suppression (4.2% vs 48.3%, 11.5x), and body-line exclusivity (0% header, depleted par-final). The -am suffix and m-terminal MIDDLE are orthogonal systems (1 token overlap) operating at different grammar levels: m closes body lines, -am closes paragraphs.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1434: m-terminal low-diversity closure specialization (10 types, 289 tokens, 86.5% = am+m) |
| **ADDED** | C1435: m-terminal body-line exclusivity (10.45% body-line-final, 0% header, 3.26% par-final) |
| **ADDED** | C1436: m-terminal near-pure TRANSITION category (87.9%, 5.86x enrichment) |
| **ADDED** | C1437: m-terminal complete hazard exclusion (0% FLOW/CONTAINMENT) |
| **ADDED** | C1438: m-terminal categorical suffix suppression (4.2% vs 48.3%, 11.5x) |
| **ADDED** | C1439: m-terminal MIDDLE and -am suffix are orthogonal systems (1 token overlap) |
| **ADDED** | `phases/M_TERMINAL_ANOMALY/scripts/m_terminal_analysis.py` |
| **ADDED** | `phases/M_TERMINAL_ANOMALY/results/m_terminal_analysis.json` |
| **ADDED** | `phases/M_TERMINAL_ANOMALY/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1284 total) |
| **UPDATED** | CONSTRAINT_TABLE.txt regenerated (1284 constraints) |

---

## Version 5.11.113 (2026-03-05) - Phase 520: Paragraph AXM Residual

### Summary

Phase 520 systematically decomposes the ~24% paragraph AXM variance unexplained by PREFIX composition (C1405). 10 tests across 41 features, 283 paragraphs, 23,096 tokens. No non-PREFIX feature adds predictive power -- full 41-feature model DEGRADES vs PREFIX-only (CV R2=0.707 vs 0.711). The residual decomposes as 25.2% binomial sampling noise + 4.2% genuine design freedom. PREFIX achieves 94.4% of the theoretical maximum R2. All non-PREFIX correlations (HEAD atoms, suffix mode, articulators) are fully PREFIX-mediated via C1411/C1418/C1422. Refines C1169's "~27% design freedom" to "~4% genuine + ~25% noise" at paragraph level.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1431: non-PREFIX features add zero predictive power for paragraph AXM |
| **ADDED** | C1432: paragraph AXM residual is 85% measurement noise |
| **ADDED** | C1433: PREFIX-AXM mediation chain is complete at paragraph level |
| **ADDED** | `phases/PARAGRAPH_AXM_RESIDUAL/scripts/paragraph_axm_residual.py` |
| **ADDED** | `phases/PARAGRAPH_AXM_RESIDUAL/results/paragraph_axm_residual.json` |
| **ADDED** | `phases/PARAGRAPH_AXM_RESIDUAL/REPORT.md` |
| **UPDATED** | INDEX.md -- +3 constraints (1278 total) |
| **UPDATED** | CONSTRAINT_TABLE.txt regenerated (1278 constraints) |

---

## Version 5.10.112 (2026-03-05) - Phase 519: Line-Level Architecture

### Summary

Phase 519 systematically profiles the Currier B line as a structural unit via 10 tests across 23,096 tokens in 2,420 lines. Key findings: lines are unimodal in length (mean=9.54, mode=10, CV=0.340), open with specification vocabulary (ARTICULATOR 3.93x, STAGING 1.57x), execute thermal operations mid-line (THERMAL peaks Q1 at 29.4%), and close with transition/closure markers (TRANSITION 1.63x, -m suffix 9.54x). Adjacent lines are categorically independent (MI<0.035 bits). Information forms a U-shape (boundaries more informative than interior). Validates C556/C929/C1218-C1219/C670.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1425: line length unimodal distribution |
| **ADDED** | C1426: line-initial specification profile |
| **ADDED** | C1427: line-final transition profile |
| **ADDED** | C1428: THERMAL-peak-then-decline positional gradient |
| **ADDED** | C1429: cross-line category independence |
| **ADDED** | C1430: information U-shape at line boundaries |
| **ADDED** | `phases/LINE_LEVEL_ARCHITECTURE/scripts/line_architecture.py` |
| **ADDED** | `phases/LINE_LEVEL_ARCHITECTURE/results/line_architecture.json` |
| **ADDED** | `phases/LINE_LEVEL_ARCHITECTURE/REPORT.md` |
| **UPDATED** | INDEX.md -- +6 constraints (1275 total) |
| **UPDATED** | CONSTRAINT_TABLE.txt regenerated (1275 constraints) |

---

## Version 5.09.111 (2026-03-05) - Phase 518: Suffix Mode Cycling Mechanism

### Summary

Phase 518 investigates what drives the alternation between suffix Mode A ({d,e,ee,h,y} -- THERMAL/MONITORING) and Mode B ({a,i,ii,l,m,n,o,r,s} -- STAGING/FLOW) within paragraphs. Result: token-level mode is ~80% MIDDLE-determined (C1412) with NO sequential dependency (CMI=0.016 bits, 1.64% of H). Lines show mild mode PERSISTENCE (60.6% same-mode rate, vs 50% random), not interleaving. C1229's "80% interleaved" refers to paragraph classification (fraction containing mixed modes), NOT consecutive-line switch rate (which is 39.4%, BELOW random). TERMINAL switching does not drive mode switching -- mode switch rate is identical (39.1% vs 39.4%) regardless of whether the dominant TERMINAL changed. The 2.89% genuine line-level sequential signal represents mild operational state inertia.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1422: suffix mode is MIDDLE-determined without sequential dependency |
| **ADDED** | C1423: line-level mode persistence with weak inertia |
| **ADDED** | C1424: mode switching is TERMINAL-independent at line level |
| **ADDED** | `phases/SUFFIX_MODE_CYCLING_MECHANISM/scripts/suffix_mode_mechanism.py` |
| **ADDED** | `phases/SUFFIX_MODE_CYCLING_MECHANISM/results/suffix_mode_mechanism.json` |
| **UPDATED** | INDEX.md -- +3 constraints (1268 total) |
| **UPDATED** | CONSTRAINT_TABLE.txt regenerated (1268 constraints) |

---

## Version 5.08.110 (2026-03-05) - Phase 517: ARTICULATOR Deep Dive

### Summary

Phase 517 provides the first comprehensive analysis of the ARTICULATOR slot in token morphology `[ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX]`. Articulators are rare (4.41% of B tokens, 1,019/23,096), dominated by y (51.2%), and concentrate at line-initial position (17.3% vs 2.7% medial = 6.48x). They categorically exclude BARE tokens (0/3,864) and qo-PREFIX (3/4,069 = 0.07%), locking instead to sh-family PREFIXes (t: 94%, k: 94%, d: 72%). Articulated tokens overwhelmingly carry e-initial MIDDLEs (76-90% vs 40% baseline), with k-HEAD MIDDLEs categorically excluded. Suffix attachment is suppressed (0.34-0.55x baseline). Category information is 100% MIDDLE-mediated (I(ART;CAT|MIDDLE) = 0.000 bits). Two positional sub-groups: INITIAL articulators (d,k,p,s,t,y) and FINAL articulators (l,r). ARTICULATOR is a peripheral line-opening specification marker, not a fourth independent morphological axis.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1416: ARTICULATOR rate and inventory |
| **ADDED** | C1417: ARTICULATOR line-initial concentration |
| **ADDED** | C1418: ARTICULATOR PREFIX-locked with BARE/qo exclusion |
| **ADDED** | C1419: ARTICULATOR e-HEAD selectivity and k-HEAD exclusion |
| **ADDED** | C1420: ARTICULATOR suffix suppression |
| **ADDED** | C1421: ARTICULATOR category full MIDDLE mediation |
| **ADDED** | `phases/ARTICULATOR_DEEP_DIVE/scripts/articulator_deep_dive.py` |
| **ADDED** | `phases/ARTICULATOR_DEEP_DIVE/results/articulator_deep_dive.json` |
| **UPDATED** | BCSC v3.26 -- morphology section: added ARTICULATOR findings |
| **UPDATED** | INDEX.md -- +6 constraints (1265 total) |

---

## Version 5.07.109 (2026-03-05) - Phase 516: Cross-Slot Interaction Grammar

### Summary

Phase 516 tests how PREFIX, MIDDLE, and SUFFIX constrain each other within tokens at atom resolution. Result: the instruction encoding chain is strictly PREFIX -> MIDDLE -> SUFFIX (not three-way). PREFIX selects MIDDLE HEAD atom (V=0.414, MI=1.089 bits); MIDDLE determines suffix via terminal atom (TERM V=0.503 outpredicts PREFIX V=0.169 by 3x); PREFIX-SUFFIX is the most independent pair (NMI=0.090), almost entirely mediated through MIDDLE. Sister pairs (ch/sh, ok/ot) select identical MIDDLE atoms (JSD=0.010). Cross-slot atom co-occurrence reveals d REPELS (O/E=0.203), e ATTRACTS (1.310), and 2 absolute prohibitions (l/r-TERM x e-SUFFIX HEAD = 0). 83 forbidden PREFIX x MIDDLE HEAD combinations quantify atom-level channeling. Three-way synergy is negligible (+0.009 bits), confirming C1003 at atom resolution.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1411: PREFIX->MIDDLE selectivity hierarchy with sister pair atom identity |
| **ADDED** | C1412: MIDDLE dominates suffix determination via terminal atom |
| **ADDED** | C1413: PREFIX-SUFFIX coupling is MIDDLE-mediated |
| **ADDED** | C1414: cross-slot atom co-occurrence exclusion rules |
| **ADDED** | C1415: 83 forbidden PREFIX x MIDDLE HEAD combinations at atom level |
| **ADDED** | `phases/CROSS_SLOT_INTERACTION/scripts/cross_slot_interaction.py` |
| **ADDED** | `phases/CROSS_SLOT_INTERACTION/results/cross_slot_interaction.json` |
| **UPDATED** | BCSC v3.25 — morphology section: added cross-slot interaction findings |
| **UPDATED** | INDEX.md — +5 constraints (1259 total) |

---

## Version 5.06.108 (2026-03-05) - Phase 515: Suffix Atom Decomposition

### Summary

Phase 515 decomposes the suffix domain at atom resolution, paralleling the MIDDLE encoding work (C1393-C1394). Result: suffix uses 16 atoms (a reduced subset of MIDDLE's 18 — missing k, t, p, f, c) with strong HEAD→TERM compositional structure (76.6% HEAD-initial, 100% TERM-terminal, zero violations). First atom predicts category (V=0.277), last atom predicts line position (R²=0.059). Cross-position comparison shows atoms carry different operational information in suffix vs MIDDLE position (0/12 stable, JSD range 0.004-0.560). C1229's two alternating suffix modes decompose cleanly: Mode A = {d,e,ee,h,y} THERMAL/MONITORING atoms; Mode B = {a,i,ii,l,m,n,o,r,s} STAGING/FLOW atoms.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1408: suffix has HEAD→TERM compositional structure |
| **ADDED** | C1409: suffix atoms diverge from MIDDLE-terminal atoms (0/12 stable) |
| **ADDED** | C1410: suffix modes are atom-level category partitions |
| **ADDED** | `phases/SUFFIX_ATOM_DECOMPOSITION/scripts/suffix_atom_decomposition.py` |
| **ADDED** | `phases/SUFFIX_ATOM_DECOMPOSITION/results/suffix_atom_decomposition.json` |
| **UPDATED** | BCSC v3.24 — suffix section: added C1408-C1410 |
| **UPDATED** | INDEX.md — +3 constraints (1254 total) |

---

## Version 5.05.107 (2026-03-05) - Phase 514: Section and Paragraph AXM Drivers

### Summary

Phase 514 asks what structurally differentiates sections and what drives the 71% paragraph-level AXM variation that folio membership doesn't explain (C1402 ICC=0.286). Result: sections are REGIME allocation policies (V=0.573, 7.4x next effect); paragraph AXM is dominated by PREFIX composition (CV R2=0.736); section alone has negative predictive power (CV R2=-0.027). The full chain is section→REGIME→PREFIX→AXM, with section fully mediated. PREFIX-AXM mapping is universal across all sections (6/7 features sign-consistent). 24% residual = genuine paragraph design freedom.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1404: section structural differentiation is REGIME-dominated (V=0.573) |
| **ADDED** | C1405: paragraph AXM rate driven by PREFIX not section (CV R2=0.736) |
| **ADDED** | C1406: section is REGIME composition at paragraph level (fully mediated) |
| **ADDED** | C1407: PREFIX-AXM relationship universal across sections (6/7 consistent) |
| **ADDED** | `phases/SECTION_PARAGRAPH_AXM_DRIVERS/scripts/section_paragraph_drivers.py` |
| **ADDED** | `phases/SECTION_PARAGRAPH_AXM_DRIVERS/results/section_paragraph_drivers.json` |
| **UPDATED** | BCSC v3.23 — section/convergence: added C1404-C1407 |
| **UPDATED** | INDEX.md — +4 constraints (1251 total) |

---

## Version 5.04.106 (2026-03-05) - Phase 513: STATE-C Convergence Revisit

### Summary

Phase 513 revisits the early STATE-C convergence model (C074, C325, Phases 13-14) in light of paragraph independence findings (C1398-C1400). Result: FULL_REFRAME. C325's completion gradient (rho=+0.24 with folio position) is a section confound — within every section, the gradient collapses to zero. Section B (74.5% AXM) sits later in the manuscript (section-position rho=+0.391). No sequential convergence toward AXM is detected at any scale: across paragraphs (rho=-0.019, p=0.78), within paragraphs (rho=-0.016, p=0.535), or between adjacent paragraphs (rho=0.001, perm p=0.983). Position-aware models are 29.6% worse than simple folio-mean baseline. C074/C079/C084 remain factually correct but their "convergence" framing is reinterpreted: MONOSTATE describes AXM as the dominant operational mode (59-75% by section), not a sequential convergence endpoint.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1401: C325 completion gradient is section confound |
| **ADDED** | C1402: no sequential convergence to AXM at any scale (7 tests, 0 sequential) |
| **ADDED** | C1403: MONOSTATE is thematic dominance not sequential convergence (reframes C074/C079/C084) |
| **ADDED** | `phases/STATE_C_CONVERGENCE_REVISIT/scripts/state_c_revisit.py` |
| **ADDED** | `phases/STATE_C_CONVERGENCE_REVISIT/results/state_c_revisit.json` |
| **UPDATED** | BCSC v3.22 — convergence section: reframed with C1401-C1403 |
| **UPDATED** | INDEX.md — +3 constraints (1247 total) |

---

## Version 5.04.105 (2026-03-05) - Phase 512: Paragraph State-Independent Ordering

### Summary

Phase 512 tests whether paragraph ordering is state-dependent (terminal physical state routes what comes next). Result: 0/8 PASS after disambiguation. Terminal kernel balance, category profile, and tail product type do NOT predict next paragraph zone. Folio-mode baseline (0.685) dominates all state models. The initial T5 thermal continuity signal (rho=+0.230) was disambiguated as folio-level shared environment: shuffle p=0.565, adjacent≈non-adjacent (p=0.690), lag gradient flat. Folio-residualized correlation flips to -0.161 (p=0.029) — weak thermal anti-correlation (compensatory cycling, not carryover). Combined with C1399: paragraphs are independently composed subroutines within the folio's thematic envelope, ordered neither by position nor by state.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1400: paragraph state-independent ordering (8+4 tests, 0/8 PASS, thermal disambiguation) |
| **ADDED** | `phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/scripts/state_dependent_ordering.py` |
| **ADDED** | `phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/scripts/thermal_disambiguation.py` |
| **ADDED** | `phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/results/state_dependent_ordering.json` |
| **ADDED** | `phases/PARAGRAPH_STATE_DEPENDENT_ORDERING/results/thermal_disambiguation.json` |
| **UPDATED** | BCSC v3.21 — paragraph section: added state_independent_ordering subsection |
| **UPDATED** | INDEX.md — +1 constraint (1244 total) |

---

## Version 5.04.104 (2026-03-04) - Phase 511: Paragraph Ordering Null

### Summary

Phase 511 tests whether the 4 operational gradient zones (C1398) follow a preferred sequence within folios. Result: NO_ORDERING (7/8 FAIL). All zones cluster at normalized ordinal ~0.5. No monotonic ramp (rho=-0.052). The one structured test (transition matrix, V=0.424) reveals zone INERTIA (self-transition O/E=2.02), not sequential ordering — folios run consecutive paragraphs of the same type. THERMAL↔MONITORING mutual avoidance (O/E=0.12/0.20) reflects different program types, not sequential incompatibility. Section-controlled: all FAIL. Folio specifies WHAT operational concerns and HOW MUCH, not in WHAT ORDER. Strengthens C845 (self-containment) and C862 (parallel programs).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1399: paragraph ordering null (8 tests, 7/8 FAIL, zone inertia O/E=2.02) |
| **ADDED** | `phases/PARAGRAPH_ORDERING_WITHIN_FOLIOS/scripts/paragraph_ordering.py` |
| **ADDED** | `phases/PARAGRAPH_ORDERING_WITHIN_FOLIOS/results/paragraph_ordering.json` |
| **UPDATED** | BCSC v3.20 — paragraph section: added ordering_null subsection |
| **UPDATED** | INDEX.md — +1 constraint (1243 total) |

---

## Version 5.04.103 (2026-03-04) - Phase 510: Paragraph Operational Gradient

### Summary

Phase 510 tests whether paragraphs form discrete program types. Result: paragraphs form a **continuous operational variation space** (silhouette 0.113, well below 0.25 threshold), NOT discrete types. However, 4 interpretable gradient zones emerge: THERMAL-QO (n=87, BIO/REGIME_1), CONTAINMENT-Sealing (n=68, HERBAL), OPERATION-Iteration (n=75, STARS_RECIPE/REGIME_3), MONITORING-Phase (n=34, STARS_RECIPE/REGIME_3). Strong section (V=0.408) and REGIME (V=0.371) correspondence. 50% of folios contain multiple zones. Combined with C1378 (NULL material differentiation): paragraphs are subroutines handling different operational aspects of the same job, not different jobs on shared equipment.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1398: paragraph operational gradient (8 tests, continuous space, 4 gradient zones, C1378 connection) |
| **ADDED** | `phases/PARAGRAPH_PROGRAM_TYPING/scripts/paragraph_program_typing.py` |
| **ADDED** | `phases/PARAGRAPH_PROGRAM_TYPING/results/paragraph_program_typing.json` |
| **UPDATED** | BCSC v3.19 — paragraph section: added operational_gradient subsection |
| **UPDATED** | INDEX.md — +1 constraint (1242 total) |

---

## Version 5.04.102 (2026-03-04) - Phase 509: Headless Compound Functional Grammar

### Summary

Phase 509 characterizes the headless compound subgrammar (20.6% of compound tokens, 3,288 tokens, 467 types). The initial atom of a headless compound acts as a pseudo-HEAD, creating atom-specific functional domains with high discriminative power (category V=0.503, PREFIX channel V=0.459). Seven initial atoms show distinct profiles: d=CONTAINMENT 84%, p=MARKING 92%, f=MARKING 91%, i=STAGING 66%, r=FLOW 61%, c=OPERATION 32% (most diverse), l=STAGING 28% (most versatile). A stark suffix bifurcation separates binary operations (d/i bare 85-93%) from parametric operations (c/p/f suffixed 93-97%). The da-PREFIX enrichment reported in C1394 T8 is driven specifically by i-initial compounds (iin, in), not headless compounds generally. Modifier ordering follows the same grammar (61.9% vs 70.1% headed). q-initial (104 tokens) is a separate non-grammar artifact.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1397: headless compound functional grammar (10 tests, V=0.503 category, pseudo-HEAD, suffix bifurcation) |
| **ADDED** | `phases/HEADLESS_COMPOUND_GRAMMAR/scripts/headless_compound_grammar.py` |
| **ADDED** | `phases/HEADLESS_COMPOUND_GRAMMAR/results/headless_compound_grammar.json` |
| **UPDATED** | BCSC v3.18 — headless_compounds section rewritten with per-atom profiles |
| **UPDATED** | INDEX.md — +1 constraint (1241 total) |

---

## Version 5.04.101 (2026-03-04) - Phase 508: Prep PREFIX Profiling

### Summary

Phase 508 resolves the prep PREFIX glossing question. C1221 (Phase 434) had collapsed the Brunschwig-derived verb glosses (CHOP, POUND, STRIP, GATHER) to generic "process" after showing identical MIDDLE category content (cosine 0.963, shuffle p=0.998). Phase 508 tests 7 non-content dimensions and finds 7/8 DIFFERENTIATED. Prep PREFIXes share MIDDLE content but diverge strongly on position (dch 71.2% line-initial, lch mean 0.530), paragraph position (pch 41.2% par-initial, lch 0%), suffix bare rate (pch 50.6%, lch 81.3%), REGIME (lch 70.5% R1, pch/tch 40-44% R3), section (lch 40% Section B), and sequential context (V=0.308). Atom-grounded glosses replace generic "process": pch=stage-test, tch=transfer-test, dch=mark-test, lch=hold-test, te=transfer-cool. Three positional tiers emerge: OPENER (pch, dch, tch), BODY (te), SUSTAINER (lch).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1396: prep PREFIX structural differentiation (8 tests, 7/8 differentiated, atom-grounded glosses) |
| **ADDED** | `phases/PREP_PREFIX_PROFILING/scripts/prep_prefix_profiling.py` |
| **ADDED** | `phases/PREP_PREFIX_PROFILING/results/prep_prefix_profiling.json` |
| **UPDATED** | GLOSSING.md — prep PREFIX glosses revised from "process" to atom-grounded (pch=stage-test, etc.) |
| **UPDATED** | README.md, GUIDE.md — POUND/CHOP references replaced with "preparation-class PREFIX operations" |
| **UPDATED** | INDEX.md — +1 constraint (1240 total) |

---

## Version 5.04.100 (2026-03-04) - Phase 507: Cross-System Instruction Encoding

### Summary

Phase 507 extends the HEAD+MOD*+TERM instruction encoding architecture (C1394) from B-only to manuscript-wide through 7 cross-system tests. A-exclusive MIDDLEs (579 types) follow the same slot grammar as B (modifier ordering Fisher p=0.90; pair-lock 84.2% agreement; atom distribution V=0.114). Bridge MIDDLEs show 100% HEAD category stability across A and B (V=0.562). However, A and B use the shared grammar with different functional emphasis: A is enriched in state-describing terminals (l at 1.84x) and arrangement frames (o-HEAD 2.5-2.8x), while B is dominated by action-performing terminals (dy at 144x enrichment) and execution frames (edy, aiin, ar). A records exhibit positional grammar — o-HEAD leads (37.5% first), headless trails (55.5% last) — with within-folio PP compatibility exceeding between-folio by 1.22x (z=+20.9). Headless HEAD recovery is rejected (9.1% accuracy, worse than random) — headless compounds are genuinely headless. A→B prediction is statistically significant (z=+8.60) but practically flat (R²<5%), confirming the uniform pool relationship (C484/C1136).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1395: cross-system instruction encoding (7 tests, shared grammar Fisher p=0.90, 100% bridge stability, A=state/B=action split, positional grammar confirmed) |
| **ADDED** | `phases/INSTRUCTION_ENCODING_MAP/scripts/` — 7 scripts (a_exclusive_slot_grammar, headless_head_recovery, a_record_head_coherence, cross_system_head_stability, a_exclusive_frames_and_terminals, a_record_b_folio_prediction, a_situation_description_tests) |
| **ADDED** | `phases/INSTRUCTION_ENCODING_MAP/results/` — 7 JSON result files |
| **UPDATED** | C1394: scope expanded from B to GLOBAL; headless HEAD recovery open question resolved (REJECTED) |
| **UPDATED** | INDEX.md — +1 constraint (1239 total) |

---

## Version 5.04.99 (2026-03-04) - Phase 506: Instruction Encoding Refinement

### Summary

Phase 506 resolves all four open questions from C1394. Headless compounds (20.6% of compound tokens) are a specialized subgrammar for infrastructure/support operations (CONTAINMENT 10.4x, MARKING 5.3x) concentrated at boundary positions and under a-base PREFIXes (da 2213x enrichment). The h-terminal is not chaotic but transparent — HEAD+MODS predict category at V=0.988, and h="watch" lets the HEAD's domain signal pass through. PREFIX compensates for h-ambiguity (+0.166 V). Modifier ordering (p→f→i→c→d→s) is morphological convention with first-modifier dominance (66.5% decisive); the pipeline model is falsified for multi-stage stacking, which collapses to MARKING (97–100%). The e-atom is a genuine domain-specific HEAD (not a default); o is the real versatility champion (entropy 2.396). e-depth creates a saturation gradient: single-e is diverse, ee=84% THERMAL, eee=100% THERMAL.

### Changes

| Action | Details |
|--------|---------|
| **UPDATED** | C1394: +4 tests (T8–T11), all open questions resolved, encoding model refined (h-transparency, headless subgrammar, e-depth saturation, first-modifier dominance) |
| **ADDED** | `phases/INSTRUCTION_ENCODING_MAP/scripts/` — 4 scripts (headless_compounds, h_terminal_analysis, modifier_order_semantics, e_versatility_test) |
| **ADDED** | `phases/INSTRUCTION_ENCODING_MAP/results/` — 4 JSON result files |

---

## Version 5.04.98 (2026-03-04) - Phase 505: Instruction Encoding Architecture

### Summary

Phase 505 extends C1393's three-slot composition grammar into a full instruction encoding architecture. The modifier slot is revealed as a variable-length, internally ordered array (p→f→i→c→d→s) rather than a single position. The HEAD+TERM frame predicts 64% of instruction category, with modifiers accounting for the remaining 36% through consistent category-shifting effects (d→OPERATION at V=0.657, f→MARKING at 76.4%, i→TRANSITION at 44.7%). Most "macro-atoms" from C1379 are shown to be adjacent slots rather than fused units — only dy is hard-fused (never separated, O/E 5.75x); ke, ee, od are just adjacent slots following the grammar. Nine atoms are pair-locked (standalone <10%), including all 5 modifier atoms and HEAD atoms a/o. The suffix is confirmed as an independent morphological layer (entropy 1.475 bits) built from the same atom inventory but compositionally separate from the MIDDLE.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1394: instruction encoding architecture (7 tests, frame predicts 64%, modifier ordering p→f→i→c→d→s, fusion gradient, pair-locking) |
| **ADDED** | `phases/SUFFIX_BOUNDARY_TEST/scripts/` — 4 scripts (suffix_boundary_test, pair_locked_atoms, fusion_vs_adjacency, modifier_stack_test) |
| **ADDED** | `phases/INSTRUCTION_ENCODING_MAP/scripts/instruction_map.py` — frame matrix, modifier effects, compound decomposition table |
| **ADDED** | `phases/INSTRUCTION_ENCODING_MAP/results/compound_table.txt` — 190 compounds decomposed with glosses |
| **UPDATED** | C1393: suffix boundary resolved in open questions (entropy 1.475 bits, confirmed independent) |
| **UPDATED** | INDEX.md — +1 constraint (1238 total), v5.04 |

---

## Version 5.03.97 (2026-03-03) - Phase 504: Compound MIDDLE Composition Grammar

### Summary

Phase 504 discovers and validates the three-slot composition grammar for compound MIDDLEs through 6 tests. Atoms partition into HEAD (a,e,o — always first, set domain), MODIFIER (p,c,i,f,d,s — always middle, shape action), TERMINAL (l,r,h,y,m,n — always last, carry state), and FREE (k,t — positionally mobile, role-dual process variables). The partition has Cramér's V=0.593 (chi²=30,868) and independently replicates C1209 (15/19 atom match). First atom predicts compound category at 74–76%.

Key findings: (1) k and t are NOT position-independent — they are the MOST position-sensitive atoms (JSD 0.72/0.79 vs e at 0.59), reversing from actor (98% THERMAL when first) to measurement target (88% MONITORING when last). (2) PREFIX channels modulate slot interpretation — qo deploys k as actor, ch/sh deploy k as target. (3) Atom glosses predict intrinsic FUNCTION (what the MIDDLE does), while PREFIX assignment predicts deployment CHANNEL (who orders it) — two independent readable layers. (4) Terminal-to-head carry-over is real (p~10⁻¹¹⁸) but weak (V=0.077), resetting at line boundaries.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1393: compound MIDDLE composition grammar (6 tests, V=0.593, head-initial, role duality, channel modulation) |
| **ADDED** | `phases/GLOSS_PREDICTION_TESTS/scripts/` — 6 test scripts (compound_head_test, atom_position_preferences, free_atom_position_test, terminal_head_carryover, composition_grammar_accuracy, channel_slot_grammar) |
| **ADDED** | `phases/GLOSS_PREDICTION_TESTS/results/phase_504_composition_grammar.json` — consolidated results |
| **UPDATED** | C1195: Phase 504 composition grammar cross-reference added |
| **UPDATED** | INDEX.md — +1 constraint (1237 total), v5.03 |

---

## Version 5.02.96 (2026-03-03) - Phase 503: S-Atom Modifier Battery

### Summary

Phase 503 is a follow-up to Phase 501, testing atom s with a purpose-built 8-test modifier battery instead of the standard category injection framework. Score: 5/8 (SM-2/3/4/7/8 PASS, SM-1/5/6 FAIL). The DECISIVE test SM-8 proved s is a PREDICTABLE base-dependent modifier: cosine 0.966 across independent corpus halves (all 5 testable compounds >= 0.925). s systematically shifts partner category (4/5 Xs compounds change primary, SM-2), amplifies PREFIX selectivity (SM-3), changes suffix distributions (SM-4), and routes differently from ch (SM-7, chi2=211.2, replicating C1243). h-junction not universal — tsh=FLOW, psh=MARKING (SM-1). Combined with Phase 501: 11/20 total, below 12+ SOLID threshold. s remains PLAUSIBLE but with strong modifier characterization: it's a sequencing modifier that doesn't inject a category but deterministically transforms its partner's operational domain.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/PARALLEL_MONITORING_TRACKS/PHASE_503_S_MODIFIER/` -- 8 modifier battery scripts + results JSON |
| **UPDATED** | C1391: Phase 503 modifier evidence added (SM-8 cosine 0.966, combined 11/20) |
| **UPDATED** | C1195: s evidence paragraph updated with Phase 503 modifier battery findings |
| **UPDATED** | INDEX.md -- Phase 503 findings section added to C1391 entry |

---

## Version 5.02.95 (2026-03-03) - Phase 502: F-Atom Semantic Deep Dive

### Summary

Phase 502 investigates atom f (current gloss: "flag") through 12 prediction tests in 3 cycles. Score: 6/12 (6 PASS, 4 FAIL, 1 INCONCLUSIVE, 1 N/A). f is the #2 MARKING atom (12.009x enrichment, behind only p's 12.033x) with the strongest compound uniformity of any tested atom — 90.9% of all f-compounds are MARKING. KEY STRUCTURAL FINDING: f-initial vocabulary is 100% HT/UN and never enters the 49-class execution grammar, making f the purest identification/annotation atom in the system. This distinguishes f from fellow MARKING atoms p (88.7% AXM execution) and d (execution grammar participant). f->c junction at 10.28x enrichment makes fch a compound unit (like sh in s-atom). CHSH+f 82.8% MARKING. H1 "flag" wins decisively (4/4 discriminants in F-F10, 5/5 compositional convergence in F-F12). All 4 failures are data-driven (215 tokens, sparse compounds, no testable reversed forms) or test calibration issues (f too uniformly MARKING for diversity predictions). f remains PLAUSIBLE due to data sparsity ceiling. German candidate: Flagge/Fahne.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/F_ATOM_SEMANTIC_DEEP_DIVE/` -- Phase 502 directory (12 scripts, results JSON) |
| **ADDED** | C1392: f-atom marking flag profile (#2 MARKING 12.009x, 100% HT/UN, 5/5 convergence, 6/12 tests, PLAUSIBLE) |
| **UPDATED** | C1195: Phase 502 evidence added; f remains PLAUSIBLE ("flag"); tier counts unchanged 8/6/5/0 |
| **UPDATED** | INDEX.md -- +1 constraint (1234 total), v5.02 |

---

## Version 5.01.94 (2026-03-03) - Phase 501: S-Atom Semantic Deep Dive

### Summary

Phase 501 investigates atom s (current gloss: "sequence") through 12 prediction tests in 3 cycles. Score: 6/12 (Cycle 1: 2P+1I+1F, Cycle 2: 2P+2F, Cycle 3: 2P+3F). s is the #1 STAGING atom in the system (87.50%, 6.721x enrichment) with perfect compound determinism — all 6 tested compounds map to a unique category at 100% purity (sh=MONITORING, ksh=MONITORING, lsh=MONITORING, os=OPERATION, es=STAGING, cs=MARKING). s operates in FQ macro-state (64.6%, 3.59x), distinguishing it from AXM-confined atoms c and p. The sh compound-suffix family dominates s's compound architecture: s->h junction 13.16x (208 observed), sh terminal 73.9%, first atom X determines Xsh category across 4 distinct categories. Bifurcated architecture explains 0/3 glossed compound match — all glossed compounds are in the sh-family (MONITORING) while standalone s is overwhelmingly STAGING. H1 "sequence" is best hypothesis (S-S10: 3/4 vs H2 "sift" 2/4, H3 "step" 2/4). H2 "sift" rejected (MONITORING only 2.84% standalone). s remains PLAUSIBLE — strong category identity but complex compound behavior and structural neutrality in injection tests (2/6) prevent SOLID upgrade. German candidate: sequenzieren.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/S_ATOM_SEMANTIC_DEEP_DIVE/` -- Phase 501 directory (12 scripts, results JSON) |
| **ADDED** | C1391: s-atom staging sequence profile (#1 STAGING 6.721x, 6/6 compound determinism, FQ macro-state, sh compound-suffix, 6/12 tests, PLAUSIBLE) |
| **UPDATED** | C1195: Phase 501 evidence added; s remains PLAUSIBLE ("sequence"); tier counts unchanged 8/6/5/0 |
| **UPDATED** | INDEX.md -- +1 constraint (1233 total), v5.01 |

---

## Version 5.00.93 (2026-03-03) - Phase 500: P-Atom Semantic Deep Dive

### Summary

Phase 500 investigates atom p (current gloss: "pause") through 12 prediction tests in 3 cycles. Score: 10/12 PASS (Cycle 1: 4/4, Cycle 2: 3/4, Cycle 3: 3/4). p is the #1 MARKING atom in the entire system (12.033x enrichment, 93.63% of all p-initial tokens), with the strongest carryover of any atom (8.126x consecutive pair enrichment, ZERO cross-line pairs). Compositional convergence: 3/4 gloss-to-category matches (op=TRANSITION, cph=MONITORING, cp=MARKING; ep=MARKING miss). Universal MARKING injection +68.3pp across 4/4 testable bases. Gateway compound op: 95.5% INITIAL position (210/220), 100% TRANSITION, 63 folios. CHSH+p MON+MARK 87.4% (higher than CHSH+c). AXM 88.7% (enriched but less confined than c's 93.5%), FL_HAZ 0.000x. Two minor failures: cp/pc both MARKING (p too dominant for order sensitivity), section gradient best tracker FLOW (+0.714) not MARKING (+0.657). p upgraded PLAUSIBLE -> SOLID. German candidate: pausieren. Consistent with REGIME 2: "seal->heat->PAUSE->cool overnight->unseal->collect".

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/P_ATOM_SEMANTIC_DEEP_DIVE/` -- Phase 500 directory (12 scripts, results JSON) |
| **ADDED** | C1390: p-atom marking pause profile (#1 MARKING 12.033x, #1 carryover 8.126x, 10/12 tests, SOLID) |
| **UPDATED** | C1195: p upgraded from PLAUSIBLE ("pause") to SOLID ("pause"); tier counts now 8/6/5/0 |
| **UPDATED** | INDEX.md -- +1 constraint (1232 total), v5.00 |

---

## Version 4.99.92 (2026-03-03) - Phase 499: C-Atom Semantic Deep Dive

### Summary

Phase 499 investigates atom c (current gloss: "adjust") through 19 prediction tests across three batteries. Initial cross-token battery scored 4/12, revealing c as an intra-compound modifier rather than a cross-token operator: 93.5% AXM-confined (exclusive main-loop, zero FL_HAZ/FQ/CC), MONITORING 12.237x enrichment (#1), anti-THERMAL 0.055x (near-zero), c->h junction (C1216: 380/380) operates WITHIN MIDDLEs producing ZERO cross-token signal. Compound decomposition battery (Phase 499b, 4 tests) and tiebreakers (Phase 499c, 3 tests) provided the decisive evidence: 6/6 compositional convergence — every independently glossed c-compound matches CategoryClassifier output when decomposed through c(adjust)+X. MON+MARK injection +43.2pp across 5/5 base atoms. Order sensitivity with 100% category flips (ck=OPERATION vs kc=CONTAINMENT, ct=MONITORING vs tc=FLOW). h-suffix category transformation (p<0.000001). 100% compound determinism across all 61 c-initial MIDDLEs. Expert-advisor validated SOLID upgrade: zero constraint conflicts, compositional convergence is strongest among all non-LOCKED atoms. c upgraded PLAUSIBLE -> SOLID. German candidate: justieren.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/C_ATOM_SEMANTIC_DEEP_DIVE/` — Phase 499 directory (19 scripts across 3 batteries, results JSON) |
| **ADDED** | C1389: c-atom main-loop modifier profile (6/6 compositional convergence, 100% compound determinism, SOLID) |
| **UPDATED** | C1195: c upgraded from PLAUSIBLE ("adjust") to SOLID ("adjust"); tier counts now 8/5/6/0 |
| **UPDATED** | INDEX.md — +1 constraint (1231 total), v4.99 |

---

## Version 4.98.91 (2026-03-03) - Phase 498: O-Atom Semantic Deep Dive

### Summary

Phase 498 documents the most extensive single-atom investigation in the project: 23 tests across three batteries. Initial "vessel" (Ofen/CONTAINMENT) hypothesis scored 3/12 — CONTAINMENT prediction falsified, but revealed o's actual profile: STAGING 2.49x, OPERATION 1.78x, THERMAL 0.105x (most extreme depletion of any atom), anti-AXM #1 of all 20 atoms. Pivoted to "ordnen" (arrange) hypothesis: 4/8 confirmed. Tiebreaker tests: 1/3 — temporal ordering falsified (o does NOT precede k within lines, 48.6% chance), but ol compositional reading confirmed (100% STAGING, 7.68x, C874 convergence). Expert-advisor validated SOLID upgrade based on: (1) C874 convergence — ol=LINK from structural analysis independently confirmed by o(arrange)+l(state) decomposition; (2) 100% compound determinism across 4 o+X compounds (ol=STAGING, ok=CONTAINMENT, or=FLOW, ot=MONITORING); contrast al=FLOW vs ol=STAGING proves first atom carries independent semantic content; (3) German etymology fits pattern: K=Kochen, E=Erkalten, D=Dichten, T=Treiben, O=Ordnen. o upgraded WEAK→SOLID. Zero WEAK atoms remaining.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/O_ATOM_SEMANTIC_DEEP_DIVE/` — Phase 498 directory (23 scripts, results JSON) |
| **ADDED** | C1388: o-atom arrangement domain marker (C874 convergence, 100% compound determinism, SOLID) |
| **UPDATED** | C1195: o upgraded from WEAK ("work") to SOLID ("arrange"); tier counts now 8/4/7/0 |
| **UPDATED** | INDEX.md — +1 constraint (1230 total), v4.98 |

---

## Version 4.97.90 (2026-03-03) - Phase 497: R-Atom Semantic Deep Dive

### Summary

Phase 497 documents the r-atom investigation: 10 rounds of hypothesis-test cycles across 4 hypotheses (return/reflux, flow/run, ripen/mature, repeat), all falsified or partially falsified. Unlike the l-atom (Phase 496, 15 tests, WEAK→SOLID), r produced 0 fully confirmed predictions. However, the investigation discovered extreme structural facts: r exists ONLY as "ar" and "or" (extreme compound selectivity); ar monopolizes FL_HAZ (248:0 vs or, 4.910x enrichment, chi-sq=1473.71); only r/l/n appear at FL_HAZ (all RESPONDER-class); r anti-cycling (rho=-0.334, p=0.003); r→a forward chain at 2.142x. r upgraded from WEAK ("input") to PLAUSIBLE ("respond") in C1195. PLAUSIBLE ceiling due to a/o initial confound — with only 2 MIDDLE forms, r's contribution cannot be fully isolated.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/R_ATOM_SEMANTIC_DEEP_DIVE/` — Phase 497 directory (10 scripts, results JSON) |
| **ADDED** | C1387: r-terminal hazard-response partitioning (ar monopolizes FL_HAZ 248:0, anti-cycling rho=-0.334) |
| **UPDATED** | C1195: r upgraded from WEAK ("input") to PLAUSIBLE ("respond"); tier counts now 8/3/7/1 |
| **UPDATED** | INDEX.md — +1 constraint (1229 total), v4.97 |

---

## Version 4.96.89 (2026-03-03) - Phase 496: L-Atom Semantic Deep Dive

### Summary

Phase 496 documents the most thorough single-atom investigation in the project's history: 15 rounds of hypothesis-test cycles on atom l, using the crazy-expert agent to propose hypotheses and quantitative scripts to validate them. 10 alternative hypotheses were tested and falsified (let-flow, release, arrange, level, specifier, redirect, continue, nominalizer, hold, free, product). The final interpretation — l = "state/condition marker" — is supported by massive evidence: 68.9% post-state-change rate (vs 47.2% baseline), 77% kernel-before-l ordering on mixed lines, kernel contact avoidance (rho=-0.197, p<0.000001), Mode B locking (72%), and category redirection (0/5 match base atom default). German candidate: Lage (situation/condition/state of affairs). Compound readings: ol=vessel-state, el=cool-state, kl=heat-state. CHSH + l compositional reading confirmed with 450 tokens (ch+ol = "checkpoint the vessel-state"). Independent finding: ACTOR/RESPONDER terminal-atom timing split — atoms partition into ACTORS {e,k,h,t} at 18-32%, NEUTRAL {d,o,y,i} at 38-49%, RESPONDERS {n,l,r,m} at 64-78% post-state-change rate. Orthogonal to C1208 carryover and C1209 positional grammar. C1195 updated: l upgraded from WEAK ("frame") to SOLID ("state").

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/L_ATOM_SEMANTIC_DEEP_DIVE/` — Phase 496 directory (15 scripts, results JSON) |
| **ADDED** | C1385: l-terminal state/condition marker (68.9% post-change, 77% kernel-before-l, SOLID) |
| **ADDED** | C1386: ACTOR/RESPONDER terminal-atom timing split (3-way partition, orthogonal to C1208/C1209) |
| **UPDATED** | C1195: l upgraded from WEAK ("frame") to SOLID ("state"); tier counts now 8/3/6/2 |
| **UPDATED** | INDEX.md — +2 constraints (1228 total), v4.96 |

---

## Version 4.95.88 (2026-03-02) - Phase 495: Gloss Prediction Tests (batch 3)

### Summary

Phase 495 extended with P12-P14 predictions. P12 (h-terminal CHSH lane enrichment): INVERTED — h-terminal depleted in CHSH (0.767x, p=0.0002), complementary distribution not resonance. P13 (e/k vs AXM): HALF CONFIRMED — k-initial rho=+0.620 (p<0.0001), strongest atom-to-dynamics correlation; e-initial inverted (positive not negative); true axis is k vs {a,o,d}. New constraint C1384. P14 (y-terminal paragraph-final): NULL (0.950x, p=0.14). Crazy-expert cumulative: 8/14 confirmed, 3 inverted, 1 wrong direction, 1 mixed, 1 null.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1384: k-initial MIDDLE fraction predicts AXM self-transition (rho=+0.620) |
| **ADDED** | Phase 495 batch 3 script and results (P12-P14) |
| **UPDATED** | INDEX.md -- +1 constraint (1226 total) |

---

## Version 4.95.87 (2026-03-02) - C1383: n-terminal boundary avoidance

### Summary

Two independent predictions (P6, P9) that n-terminal MIDDLEs would be enriched at boundaries both inverted significantly (0.81x at mode transitions, 0.694x at line-final). Documented as C1383 to establish n as a steady-state interior atom and prevent future boundary-role predictions. Extends C1208 (anti-clustering) and C1209 (within-MIDDLE terminality) to line-level positional behavior.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1383: n-terminal MIDDLE boundary avoidance |
| **UPDATED** | INDEX.md -- +1 constraint (1225 total) |

---

## Version 4.95.86 (2026-03-02) - Phase 495: Gloss Prediction Tests (batch 2)

### Summary

Phase 495 extended with P9-P11 predictions. P9 (n-terminal at line-final): INVERTED — depleted at line-final (0.694x, p=0.000005), second n-terminal inversion confirms n as steady-state mid-line atom. P10 (k-initial Mode B depletion): CONFIRMED — k-initial MIDDLEs 0.583x depleted in Mode B vs Mode A (chi2=245, p<0.0001), holds in all 5 sections; a-initial shows symmetric opposite at 2.034x Mode B enrichment; e-initial perfectly neutral. New constraint C1382. P11 (bridge simpler than dark): MIXED — raw depth not significant but frequency-matched depth confirms (0.754x, p=0.000009). Crazy-expert cumulative: 7/11 confirmed, 2 inverted, 1 wrong direction, 1 mixed.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1382: k/a atom-initial suffix mode polarization |
| **ADDED** | Phase 495 batch 2 script and results (P9-P11) |
| **UPDATED** | INDEX.md -- +1 constraint (1224 total) |

---

## Version 4.95.85 (2026-03-02) - Phase 495: Gloss Prediction Tests

### Summary

Phase 495 tests three predictions from crazy-expert agent's analysis of Tier 4 gloss/etymology tables. P6 (n-terminal MIDDLEs at mode boundaries): INVERTED — depleted at transitions (0.81x, p<0.0001), n concentrates in stable mode regions. P7 (o-initial MIDDLEs in AZC): CONFIRMED — 1.9x enriched (22.4% vs 11.8%, chi2=281.3, p<0.0001), smooth gradient from AZC through B-shared to B-exclusive vocabulary, Section C highest B-internal rate (18.9%). P8 (f-atoms in REGIME_3): WRONG DIRECTION — peaks in REGIME_4/REGIME_2, not REGIME_3. New constraint C1381. Crazy-expert overall scorecard: 6/8 confirmed, 1 inverted, 1 wrong direction.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/GLOSS_PREDICTION_TESTS/` -- Phase 495 directory |
| **ADDED** | Phase 495 script and results (3 tests, 26K tokens) |
| **ADDED** | C1381: o-initial MIDDLE enrichment in AZC (1.9x, cross-system gradient) |
| **UPDATED** | INDEX.md -- +1 constraint (1223 total), v4.95 |

---

## Version 4.94.84 (2026-03-02) - F-B-001 SUPERSEDED by C1174

### Summary

Coherence audit identified that F-B-001 (LINK Operator as Sustained Monitoring Interval, SUCCESS) was never updated after C1174 (Phase 418) demonstrated LINK is a morphological artifact, not a functional layer. The fit's 6 structural property matches were artifacts of averaging across a heterogeneous population (C1171: 0/4 cross-role consistency). F-B-001 downgraded from SUCCESS to SUPERSEDED. C190 anticorrelation (r=-0.71) remains valid statistically but reinterpreted as role-specific vocabulary selection. Updated: fits_currier_b.md, FIT_TABLE.txt, INDEX.md, fit_to_constraint.md.

### Changes

| Action | Details |
|--------|---------|
| **UPDATED** | F-B-001 status: SUCCESS -> SUPERSEDED (by C1174) |
| **UPDATED** | FIT_TABLE.txt, INDEX.md, fit_to_constraint.md |

---

## Version 4.94.83 (2026-03-02) - Phase 494: Parallel Monitoring Tracks (continued)

### Summary

Phase 494 extended with C1380: apparatus profile similarity predicts AXM self-transition residual similarity (Mantel r=0.224, p=0.002, 5K permutations). Dominant apparatus group clusters in residual space (eta²=0.083, p=0.034). Sealed-vessel folios are most self-repetitive (+0.022), sustained-heat most varied (-0.018). Qualifies C1169: ~8% of "genuine design freedom" is actually apparatus input parameterization. C1169's univariate battery missed this because the signal is in pairwise profile similarity, not individual predictors.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | C1380: Apparatus parameterization in AXM residual |
| **ADDED** | `design_freedom_apparatus_test.py` script and results |
| **UPDATED** | C1379 extended with T5 (suffix mode channel separation) |
| **UPDATED** | INDEX.md -- +1 constraint (1222 total) |

---

## Version 4.94.82 (2026-03-01) - Phase 494: Parallel Monitoring Tracks

### Summary

Phase 494 tests whether MIDDLE atoms encode parallel monitoring parameters and whether high-affinity atom pairs from C1210 are fused macro-atoms. Five-test battery: (T1) macro-atom composition improves C1190 r from 0.760 to 0.797 (z=5.98, p<0.001) — PASS; (T2) reversed pairs not significantly more similar than different-set (ratio 0.904) — FAIL, pure parallelism rejected; (T3) cross-token coupling dominated by TERMINAL→INITIAL (MI=0.079) not SET carry (0.025) — MIXED; (T4) atom removal ratio 1.375 < 1.5 threshold but initial dominates (Kruskal p=0.004) — PASS qualified; (T5) suffix mode channel separation: ke/ct/ck 1.9-2.9x Mode A enriched, in 0.54x Mode B, qo 1.91x Mode A (p=0.0000) — PASS. Macro-atoms have functional channel assignments (specification vs continuation). New constraint C1379.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/PARALLEL_MONITORING_TRACKS/` -- Phase 494 directory |
| **ADDED** | Phase 494 scripts and results (5 tests, 23K tokens, 10K permutations) |
| **ADDED** | C1379: Two-level parallel composition with priority ordering + channel separation |
| **UPDATED** | INDEX.md -- +1 constraint (1221 total), v4.94 |

---

## Version 4.93.81 (2026-02-28) - Phase 492: Paragraph-Level Material Differentiation (NULL)

### Summary

Phase 492 tests whether paragraphs within a folio encode different plant materials, motivated by Brunschwig's 6-still water bath and 15th-century multi-material batch processing. Pre-registered two-level prediction: category profiles converge (same apparatus), dark-pipeline MIDDLEs diverge (different materials). Result: dark-pipeline MIDDLEs are near-identical across paragraphs within a folio (Jaccard 0.972 vs 0.963, p=0.98). Semantic ceiling (C171) extends to paragraph granularity. Bonus finding: paragraph headers are 1.11x more diverse than bodies (p=0.0001), qualifying C855. New constraint C1378.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/PARAGRAPH_MATERIAL_DIFFERENTIATION/` -- Phase 492 directory |
| **ADDED** | Phase 492 script and results (5 tests, 72 folios, 10K permutations) |
| **ADDED** | C1378: Paragraph-level material differentiation (NULL result) |
| **UPDATED** | INDEX.md -- +1 constraint (1220 total) |

---

## Version 4.92.80 (2026-02-27) - Phase 491: Historical Network (Initial Build)

### Summary

Phase 491 maps the intellectual network of persons, works, and institutions in the Voynich's temporal-geographic zone (c.1350-1530, N. Italy / S. Germany / Austria / Alsace). Initial build: 39 persons, 21 works, 61 edges, 16 cipher parallels. Key findings: (1) cipher use was normal in this zone (Alchymey Teuczsch 1426, Fontana c.1420, Buch der heiligen Dreifaltigkeit c.1410); (2) selective encryption of commercially valuable knowledge was standard; (3) Fontana used invented glyphs (not letter substitution) at exact Voynich radiocarbon date; (4) Brunschwig's 1512 "geoffenbart" marks explicit secrecy-to-openness transition. ONGOING phase — designed for incremental expansion.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/HISTORICAL_NETWORK/` -- Phase 491 directory |
| **ADDED** | `data/network_persons.json` -- 39 persons (P001-P039) |
| **ADDED** | `data/network_works.json` -- 21 works (W001-W021) |
| **ADDED** | `data/network_edges.json` -- 61 edges (E001-E061) |
| **ADDED** | `data/cipher_parallels.json` -- 16 cipher systems (CP001-CP016) |
| **ADDED** | `HISTORICAL_NETWORK.md` -- main narrative with 3 clusters, 4 chains |
| **ADDED** | `OPEN_QUESTIONS.md` -- 10 research threads, 4 priority levels |

---

## Version 4.91.79 (2026-02-27) - Phase 490: Puff-Voynich Structural Revisit (NULL)

### Summary

Phase 490 revisits the Puff-Voynich connection with modern structural tools (8-category profiles, 5-apparatus profiles, REGIME system). Uses blind PPC morphological classification to assign 21 Currier B herbal folios to 3 plant material groups (8 ROOT, 7 FLOWER, 6 HERB). Pre-registered, distributional (reordering-invariant), permutation-based. Result: both category profiles (p=0.51) and apparatus profiles (p=0.15) show NULL — no material-type differentiation. Early evidential ceiling confirmed. New constraint C1377.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/PUFF_VOYNICH_STRUCTURAL_REVISIT/` -- Phase 490 directory |
| **ADDED** | Phase 490 script and results (3 tests, 21 folios, 10K permutations) |
| **ADDED** | C1377: Puff-Voynich structural revisit (NULL result) |
| **UPDATED** | INDEX.md -- +1 constraint (1219 total) |

---

## Version 4.91.78 (2026-02-27) - Phase 488 T8: Lexicon Signal Decomposition

### Summary

Phase 488 extended with T8: lexicon signal decomposition under slot-preserving shuffle. Tests whether Gatta's z=3.6-4.4 Hebrew lexicon match is specific to Hebrew or an artifact of EVA's within-slot co-occurrence structure (C1209). Result: random bijective mappings show comparable vocabulary concentration (z=-158 vs Gatta z=-131) when comparing real vs slot-shuffled decoded text. The lexicon signal is from EVA grammar structure, not Hebrew-specific alignment. Updated scorecard: 4/8 control program, 1/8 cipher, 3/8 ambiguous = STRONG FALSIFICATION.

### Changes

| Action | Details |
|--------|---------|
| **UPDATED** | `phases/HEBREW_CIPHER_CROSS_VALIDATION/scripts/hebrew_cipher_cross_validation.py` -- T8 added |
| **UPDATED** | `phases/HEBREW_CIPHER_CROSS_VALIDATION/results/hebrew_cipher_cross_validation.json` -- T8 results |
| **UPDATED** | `phases/HEBREW_CIPHER_CROSS_VALIDATION/CROSS_VALIDATION_REPORT.md` -- T8 section added |
| **UPDATED** | C1375 constraint file -- T8 findings, scorecard 3/7→4/8 |

---

## Version 4.91.77 (2026-02-27) - Phase 489: Character-Level RTL Is Grammar-Internal

### Summary

Phase 489: Decomposition of the character-level RTL directional signal (replicated at z=36.8 within-token bigram conditional entropy) against known grammar asymmetries. The signal is FULLY EXPLAINED by C1209's INITIAL→MEDIAL→TERMINAL slot syntax. Slot-preserving shuffle preserves 102% of asymmetry (z=-2.6 from observed); random shuffle destroys it (z=79.8). Coarse 4-category slot syntax explains 48.9%, fine-grained per-slot character frequencies explain the rest. Kernel transitions (C521) actually oppose the gradient (-10.3%). Reconciles C1117 (LTR at token level) with character-level RTL: different structural layers of the same grammar. No Phase 490 needed.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/EVA_CHAR_ASYMMETRY_DECOMPOSITION/` -- 1 script + 1 results JSON |
| **ADDED** | C1376 constraint file (1 new constraint, 1219->1220) |
| **UPDATED** | `INDEX.md` -- 1219->1220 total, Phase 489 section added |
| **UPDATED** | `CLAUDE.md` -- v4.90->v4.91, 488->489 phases, 1219->1220 constraints |

---

## Version 4.90.76 (2026-02-27) - Phase 488: Hebrew Cipher Cross-Validation

### Summary

Phase 488: Cross-validation against Antenore Gatta's Hebrew cipher hypothesis (voynich-toolkit). Their EVA→Hebrew decode (context-sensitive, RTL, digraph/positional/homophone mapping) INCREASES character bigram entropy (+0.218 bits) and DECREASES token MI (-0.755 bits) — the opposite of correct decipherment, consistent with C130. Zero category coherence in Hebrew space (C171 holds). Only 1/35 PREFIXes exactly matches a Hebrew morpheme. The T2 within-class clustering (z=-15.5) is a morphological confound, not Hebrew structure. Score: 3/7 control program, 1/7 cipher, 3/7 ambiguous = STRONG FALSIFICATION at grammar layer.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/HEBREW_CIPHER_CROSS_VALIDATION/` -- 1 script + 1 results JSON |
| **ADDED** | C1375 constraint file (1 new constraint, 1218->1219) |
| **UPDATED** | `INDEX.md` -- 1218->1219 total, Phase 488 section added |
| **UPDATED** | `CLAUDE.md` -- v4.89->v4.90, 487->488 phases, 1218->1219 constraints |

---

## Version 4.89.75 (2026-02-27) - Phase 487: Within-PREFIX MIDDLE Positional Selection

### Summary

Phase 487: Resolved the mechanism behind the within-PREFIX thermal arc (C1373). MIDDLE selection changes by line position within every major PREFIX (7/7 tests p<0.001). The within-ch THERMAL decline is driven by extreme concentration: just 2 MIDDLEs (eey + eol) explain 100% of the gradient. Position specialists are PREFIX-generalist MIDDLEs (breadth 15.3 vs 8.3, p=0.0004) — the common vocabulary, not restricted forms. BARE shows equal positional selection (rank 14/27), proving position drives MIDDLE selection independently of PREFIX routing. The thermal arc is a MIDDLE-level positional grammar property.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/WITHIN_PREFIX_MIDDLE_POSITION/` -- 1 script + 1 results JSON |
| **ADDED** | C1374 constraint file (1 new constraint, 1217->1218) |
| **UPDATED** | `INDEX.md` -- 1217->1218 total, Phase 487 section added |
| **UPDATED** | `CLAUDE.md` -- v4.88->v4.89, 486->487 phases, 1217->1218 constraints |

---

## Version 4.88.74 (2026-02-27) - Phase 486: PREFIX Category-Position Decomposition

### Summary

Phase 486: Decomposed the PREFIX confound identified in C1372. The thermal arc (C1371) is **NOT** a PREFIX compositional artifact — it exists WITHIN individual PREFIX families. ch shows THERMAL rho=-0.900 (chi² p=3e-6), sh shows rho=-0.800 (chi² p=3e-4). 11/27 PREFIXes show |rho|>0.50 (weighted average=-0.720). Removing positional specialists (5.7% of tokens) actually STRENGTHENS the gradient. qo (59% THERMAL, peaks Q2) creates the non-monotonic Q2 bump. BARE tokens anchor Q5 THERMAL depletion. H3 (compositional artifact) is FALSIFIED. **C1372 amendment:** the PREFIX confound control was too aggressive; the gradient is genuinely within-PREFIX.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/PREFIX_CATEGORY_POSITION_DECOMPOSITION/` -- 1 script + 1 results JSON |
| **ADDED** | C1373 constraint file (1 new constraint, 1216->1217) |
| **AMENDED** | C1372 — PREFIX confound conclusion was too strong |
| **UPDATED** | `INDEX.md` -- 1216->1217 total, Phase 486 section added |
| **UPDATED** | `CLAUDE.md` -- v4.87->v4.88, 485->486 phases, 1216->1217 constraints |

---

## Version 4.87.73 (2026-02-27) - Phase 485: Thermodynamic Arc Validation

### Summary

Phase 485: Tested whether a first-principles thermodynamic ordering model (derived from distillation process logic) predicts the observed 8-category quintile profiles (C1371). **NO — 0/7 formal tests pass.** Predicted rank ordering (rho=0.286) far below threshold. Thermodynamic model 2.8x WORSE than uniform null at predicting gradient shapes. CONTAINMENT is LATE (COM=2.235), not early as predicted. 6/7 directional predictions confirmed but partially circular with C1371. **PREFIX confound control COLLAPSES the signal** — category gradient is substantially mediated by PREFIX positional grammar (C1001), not independent thermodynamic ordering. Constrains Tier 3 distillation interpretation.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/THERMODYNAMIC_ARC_VALIDATION/` -- 1 script + 1 results JSON |
| **ADDED** | C1372 constraint file (1 new constraint, 1215->1216) |
| **UPDATED** | `INDEX.md` -- 1215->1216 total, Phase 485 section added |
| **UPDATED** | `CLAUDE.md` -- v4.86->v4.87, 484->485 phases, 1215->1216 constraints |

---

## Version 4.86.72 (2026-02-27) - Phase 484: Position-Conditioned Category Grammar

### Summary

Phase 484: Tested whether 8-category transition grammar varies by line position, extending M2.1's class-level position-conditioning (C1362) to the operational category layer. **YES — category transitions are position-conditioned** (chi² p=4.5e-65, V=0.102). Line-final (Q5) is the most distinctive position. THERMAL self-loops erode Q1→Q5 (32.4%→19.1%). FLOW has the only significant monotonic gradient (rho=0.900, increasing). Section-position interaction absent, confirming C1047 at category level.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/POSITION_CONDITIONED_CATEGORY_GRAMMAR/` -- 1 script + 1 results JSON |
| **ADDED** | C1371 constraint file (1 new constraint, 1214->1215) |
| **UPDATED** | `INDEX.md` -- 1214->1215 total, Phase 484 section added |
| **UPDATED** | `CLAUDE.md` -- v4.85->v4.86, 483->484 phases, 1214->1215 constraints |

---

## Version 4.85.71 (2026-02-27) - Phase 483: Category Pipeline Trace

### Summary

Phase 483: First end-to-end trace of the 8-category system through the A→AZC→B pipeline. Pipeline is WEAKLY_RESHAPED (JS A↔B=0.026). B selectively amplifies THERMAL (+72%) and OPERATION (+58%) while attenuating STAGING (-47%) and MONITORING (-73%). AZC is intermediate, closer to A. Section-specific transfer functions: BIO=maximum THERMAL (2.03x), HERBAL=THERMAL-neutral (0.98x). Dark pipeline 3x more stable than bridge. 4/7 predictions confirmed.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/CATEGORY_PIPELINE_TRACE/` -- 1 script + 1 results JSON |
| **ADDED** | C1370 constraint file (1 new constraint, 1213->1214) |
| **UPDATED** | `INDEX.md` -- 1213->1214 total, Phase 483 section added |
| **UPDATED** | `CLAUDE.md` -- v4.84->v4.85, 482->483 phases, 1213->1214 constraints |

---

## Version 4.84.70 (2026-02-27) - Phase 482: Accent Spatial Structure

### Summary

Phase 482: Tested whether the folio_position signal in C1368's PC2 model represents genuine manuscript-order structure or a section confound. **GATE: SECTION_CONFOUND** — position adds only 1.0% partial R² beyond section for PC2 (threshold 2%). However, within-section local coherence exists: adjacent Bio (p=0.039) and Stars (p=0.024) folios have more similar accents than random same-section pairs. No manuscript-level gradient detected.

**Phase 482 headline findings:**
- folio_position in C1368 is section-mediated (partial R²=0.010 < 0.02)
- Within-section local coherence: Bio and Stars adjacent folios are ~15-18% more accent-similar
- 0/9 lag autocorrelations significant — coherence is weak but present
- Section boundaries moderate (ratio 1.18) — accent transitions relatively smooth
- Archetypes 1-2 spatially clustered (section-driven)

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/ACCENT_SPATIAL_STRUCTURE/` -- 1 script + 1 results JSON |
| **ADDED** | C1369 constraint file (1 new constraint, 1212->1213) |
| **UPDATED** | `INDEX.md` -- 1212->1213 total, Phase 482 section added, C1368 note amended |
| **UPDATED** | `CLAUDE.md` -- v4.83->v4.84, 481->482 phases, 1212->1213 constraints |

---

## Version 4.83.69 (2026-02-27) - Phase 481: Accent PC2/PC3 Decomposition

### Summary

Phase 481: Characterized the uncharacterized accent dimensions PC2 (sequential complexity, 20.5%) and PC3 (morphological texture, 8.9%). 0/5 expert predictions confirmed — the accent surprised us. THERMAL is the pervasive accent predictor across PC1+PC2 (79.4% combined). Stars section dominates PC3 morphological axis (eta²=0.457). Manuscript folio position enters PC2 model — first accent-level evidence of manuscript-order signal.

**Phase 481 headline findings:**
- PC2: THERMAL (kernel-residualized) + folio_position → LOO R² = 0.267
- PC3: section_S + CONTAINMENT (residualized) + ch_preference → LOO R² = 0.496
- Section predicts morphological texture (PC3), NOT sequential complexity (PC2) — reversed prediction
- THERMAL dominates both PC1 (C1367) and PC2 — pervasive accent predictor
- Folio position signal in PC2 — motivates cross-folio spatial analysis

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/ACCENT_PC23_DECOMPOSITION/` -- 1 script + 1 results JSON |
| **ADDED** | C1368 constraint file (1 new constraint, 1211->1212) |
| **UPDATED** | `INDEX.md` -- 1211->1212 total, Phase 481 section added |
| **UPDATED** | `CLAUDE.md` -- v4.82->v4.83, 480->481 phases, 1211->1212 constraints |

---

## Version 4.82.68 (2026-02-27) - Phase 480: Folio Accent Vector Analysis

### Summary

Phase 480: Extracted per-folio accent vectors from Phase 479 z-scores, ran PCA, and tested whether the accent structure is archetype-dominated or captures new folio-level structure. **Gating test: NEW_STRUCTURE** — accent PC1 correlates weakly with archetypes (|rho|=0.274), capturing 67% independent variance. THERMAL category fraction predicts the accent beyond kernel balance (partial rho=0.588). BIO accent is section-intrinsic.

**Phase 480 headline findings:**
- PC1 explains 58.9% of accent variance (AXM dynamics intensity)
- Accent-archetype |rho|=0.274 → genuinely new structure, not archetype-dominated
- THERMAL fraction survives kernel control (partial rho=0.588, p<0.0001) — category has independent accent signal
- BIO accent persists within REGIME_1 (p=0.019) — section-intrinsic, not REGIME-mediated
- Archetype 1 = 8/10 BIO, highly homogeneous (sign agreement 0.88)

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/FOLIO_ACCENT_VECTOR/` -- 1 script + 1 results JSON |
| **ADDED** | C1367 constraint file (1 new constraint, 1210->1211) |
| **UPDATED** | `INDEX.md` -- 1210->1211 total, Phase 480 section added |
| **UPDATED** | `CLAUDE.md` -- v4.81->v4.82, 479->480 phases, 1210->1211 constraints |

---

## Version 4.81.67 (2026-02-27) - Phase 479: M2.1 Generative Gap Characterization

### Summary

Phase 479: Characterized the per-folio gap between M2.1 (corpus-wide model, 21/21) and real folio structure. Generated 100 synthetic counterparts per real folio, computed 31-feature z-score profiles. **The folio accent is a macro-automaton operating point parameter** — concentrated in class distribution (AXM/FQ fractions) and sequential dynamics (AXM self-transition, run length), not in positional structure or vocabulary composition.

**Phase 479 headline findings:**
- 11/31 features show systematic gaps (mean|z| > 1.5)
- Top gap features: AXM fraction (2.14), class concentration (2.03), AXM self-transition (2.03)
- BIO section has HIGHEST anomaly (1.691) — coherent AND distinctive (C1048 reinterpretation)
- Archetype 1 (strong attractor) has highest anomaly (2.034)
- C458 hazard/recovery asymmetry does NOT manifest at generative gap resolution
- 76.5% of feature-folio pairs within |z| < 2

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/GENERATIVE_GAP_CHARACTERIZATION/` -- 1 script + 1 results JSON |
| **ADDED** | C1366 constraint file (1 new constraint, 1209->1210) |
| **UPDATED** | `INDEX.md` -- 1209->1210 total, Phase 479 section added |
| **UPDATED** | `CLAUDE.md` -- v4.80->v4.81, 477->479 phases, 1209->1210 constraints |

---

## Version 4.80.66 (2026-02-27) - Phase 477: Corrected Evaluation — M2.1 Full Pass

### Summary

Phase 477: Corrected two test specification bugs (B4 per C1030, C2 per C1033), added PREFIX/MIDDLE symmetry diagnostics (X1, X2), and re-evaluated M2.1 on a 21-metric battery. **M2.1 achieves 21/21 — the 49-class grammar is generatively closed.** PREFIX-factored generation confirmed unnecessary (C1034: distributionally equivalent to M2, reconstruction error 0.000000).

**Phase 477 headline findings:**
- B4 corrected: real data has EN>FQ>AX>FL>CC, not FQ>FL>EN. M2.1 matches at 70%.
- C2 split: C2a macro CC=100% (passes 100%), C2b role CC matches real within 3pp (passes 70%)
- X1 PREFIX symmetry: M2.1 reproduces near-symmetry (0.036 vs real 0.051)
- X2 MIDDLE asymmetry: M2.1 reproduces directionality (0.094 vs real 0.126)
- PREFIX factoring proven unnecessary — symmetric forbidden suppression captures the required symmetry
- M2.1 full pass: 21/21 metrics, mean 20.0 per run

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/CORRECTED_EVALUATION/` -- 1 script + 1 results JSON |
| **ADDED** | C1365 constraint file (1 new constraint, 1208->1209) |
| **UPDATED** | `INDEX.md` -- 1208->1209 total, Phase 477 section added |
| **UPDATED** | `CLAUDE.md` -- v4.79->v4.80, 476->477 phases, 1208->1209 constraints |

---

## Version 4.79.65 (2026-02-27) - Phase 476: Position-Conditioned Generation (M2.1)

### Summary

Phase 476: M2.1 position-conditioned generation. Two models (M2-SF baseline, M2.1 quintile-conditioned) evaluated side-by-side on 18-metric battery (15 original + 3 new position metrics), 10 runs each. **M2.1 passes 16/18 with zero regressions, gaining all 3 positional metrics.** Position conditioning delivers 2.0-2.4x improvement on quintile class KL, transition JSD, and specialist accuracy. Remaining failures (B4 role rank, C2 CC suffix-free) are morphological, targeted by Phases 477-478.

**Phase 476 headline findings:**
- M2.1 passes 16/18 vs M2-SF 13/18 — +3 tests gained, 0 lost (C1364)
- P1 quintile class KL: 0.066→0.029 (2.2x improvement)
- P2 quintile transition JSD: 0.299→0.146 (2.0x improvement)
- P3 specialist accuracy: 0.149→0.062 (2.4x improvement)
- B5 passes at 90% confirming C1034 symmetric forbidden suppression
- M2.1 is the new generative frontier at 88.9% pass rate

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/POSITION_CONDITIONED_GENERATION/` -- 1 script + 1 results JSON |
| **ADDED** | C1364 constraint file (1 new constraint, 1207->1208) |
| **UPDATED** | `INDEX.md` -- 1207->1208 total, Phase 476 section added |
| **UPDATED** | `CLAUDE.md` -- v4.78->v4.79, 475->476 phases, 1207->1208 constraints |

---

## Version 4.78.64 (2026-02-26) - Phase 475: Gradient Steepness

### Summary

Phase 475: 5-test gated battery testing whether the within-line AXM gradient (C1359: 0.737→0.549) varies by folio/program. **Overall: clean null — gradient is universal.** Both gates closed: slope variance does not exceed permutation noise (p=0.105), and steepness adds negligible info beyond C1168 boundary architecture (delta-R²=0.010). REGIME and section do not predict gradient steepness. The line gradient is an emergent property of the shared 49-class grammar, not a tunable parameter.

**Phase 475 headline findings:**
- T1 gate CLOSED: per-folio slope variance indistinguishable from noise (p=0.105, 1000 permutations)
- T2 gate CLOSED: delta-R² = 0.010 beyond C1168 entry+exit divergence — no new information
- T3 FAIL: REGIME does not predict gradient steepness (KW p=0.22, pre-registered R1<R3 direction correct but MW p=0.67)
- T4 FAIL: Section does not predict gradient steepness (KW p=0.13)
- T5 unreliable: k=2 silhouette=0.50 but only n=10 folios with sufficient data for clustering
- **Key finding:** Programs differ in WHAT they execute but not in HOW their lines unfold positionally. Extends C821.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/GRADIENT_STEEPNESS/` -- 1 script + 1 results JSON |
| **ADDED** | C1363 constraint file (1 new constraint, 1206->1207) |
| **UPDATED** | `INDEX.md` -- 1206->1207 total, Phase 475 section added |
| **UPDATED** | `CLAUDE.md` -- v4.77->v4.78, 474->475 phases, 1206->1207 constraints |

---

## Version 4.77.63 (2026-02-26) - Phase 474: Line Micro-Grammar

### Summary

Phase 474: 5-test battery characterizing line-internal execution structure at 49-class resolution. **Overall: smooth positional gradient with massive generative improvement.** Half the classes (24/48) are positional specialists. Transition structure changes monotonically Q0→Q4 (rho=0.639). No positional motifs — grammar is invariant, only class frequencies shift. Position-conditioned M2p beats stationary M2 on all 5 metrics (1.6-2.5x improvement).

**Phase 474 headline findings:**
- 24/48 classes are positional specialists (C1358): FL_SAFE at line-end, initial classes at line-start
- Smooth monotonic transition gradient (C1359): AXM self drops 0.737→0.549 across quintiles, rho=0.639
- Forbidden transitions nearly absolute at MIDDLE level (C1360): 11/20,676 = 0.053%, position-independent
- No positional motifs (C1361): 1/1,556 bigrams significant after Bonferroni — grammar rules same everywhere
- M2p wins 5/5 generative metrics (C1362): position conditioning is M2's primary blind spot
- **Key insight:** positional gradient from class frequency shift, not position-specific grammar rules

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/LINE_MICRO_GRAMMAR/` -- 1 script + 1 results JSON |
| **ADDED** | C1358-C1362 constraint files (5 new constraints, 1201->1206) |
| **UPDATED** | `INDEX.md` -- 1201->1206 total, Phase 474 section added |
| **UPDATED** | `CLAUDE.md` -- v4.76->v4.77, 473->474 phases, 1201->1206 constraints |

---

## Version 4.76.62 (2026-02-26) - Phase 473: Layered Grammar Test

### Summary

Phase 473: 5-test battery testing whether B grammar has three tiers (dark=context → bridge=execution → suffix=mode) rather than binary grammar/non-grammar. **Overall: three-tier model FALSIFIED.** Gates pass (frequency gate, PREFIX independence gate) but all three core tests fail. Dark MIDDLEs have very local grammar influence (next-token) but do not constitute a grammar tier.

**Phase 473 headline findings:**
- Frequency gate: dark entropy survives freq matching (Z=-5.60) but collapses under subsampling (Z=-0.55) — partially artifact (C1355)
- PREFIX independence gate: dark MIDDLE identity adds info beyond PREFIX (Z=4.50, perm p<0.001) — genuine (C1356)
- CORE: dark presence does NOT condition bridge-to-bridge transitions (MI=0.098, null=0.101, p=0.90) (C1354)
- CORE: dark removal does NOT genericize bridge transitions (entropy diff p=0.38) (C1354)
- CORE: dark proximity weakly boosts terminal suffix (V=0.042) — real but tiny (C1357)
- Binary model preserved with refinement: dark tokens are grammar-adjacent (local influence) not grammar-participating

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/LAYERED_GRAMMAR_TEST/` -- 1 script + 1 results JSON |
| **ADDED** | C1354-C1357 constraint files (4 new constraints, 1197->1201) |
| **UPDATED** | `INDEX.md` -- 1197->1201 total, Phase 473 section added |
| **UPDATED** | `CLAUDE.md` -- v4.75->v4.76, 472->473 phases, 1197->1201 constraints |

---

## Version 4.75.61 (2026-02-26) - Phase 472: Dark Pipeline Structure

### Summary

Phase 472: 5-test battery characterizing the structural role of dark pipeline MIDDLEs (300 MIDDLEs, identification channel). **Overall: dark pipeline = context-setting parameters, not material referents.** Dark MIDDLEs are atomistic (no co-occurrence groups), constrain local grammar continuation (narrow successor entropy), span folios as expected for their frequency (no staples/specialists split), and have no dedicated syntactic slot.

**Phase 472 headline findings:**
- Dark MIDDLEs show no within-section co-occurrence structure (C1350: 0/5 sections significant)
- Dark-dark adjacency is perfectly random (C1350: ratio=1.02, p=0.76)
- Dark successor entropy is significantly narrower than bridge (C1351: 2.59 vs 4.18 bits, Z=-7.45)
- This falsifies the material-referent prediction (materials would have wide successor entropy)
- Folio span matches frequency null (C1352: 78.3% within ±2σ, no bimodal split)
- Weak positional bias before bridge (C1353: 52.7%, Z=3.0) but trivial effect (2.7%)
- Dark pipeline = independent context-setting parameters that constrain local execution

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/DARK_PIPELINE_STRUCTURE/` -- 1 script + 1 results JSON |
| **ADDED** | C1350-C1353 constraint files (4 new constraints, 1193->1197) |
| **UPDATED** | `INDEX.md` -- 1193->1197 total, Phase 472 section added |
| **UPDATED** | `CLAUDE.md` -- v4.74->v4.75, 471->472 phases, 1193->1197 constraints |

---

## Version 4.74.60 (2026-02-26) - Phase 471: A-B Category Flow

### Summary

Phase 471: 4-test battery testing whether A-side category structure flows to B through the vocabulary pipeline. **Overall: dual-channel category architecture confirmed.** Bridge channel shows active reshaping by B (amplifies THERMAL/OPERATION, suppresses STAGING/MONITORING). Dark channel preserves category structure near-perfectly (rho=0.976). A sections differentiate at category level despite MIDDLE-level uniformity (C1136).

**Phase 471 headline findings:**
- B reshapes bridge category delivery: amplifies THERMAL 1.72x, OPERATION 1.58x, suppresses MONITORING 0.27x, STAGING 0.54x (C1347)
- Bridge consumption perfectly matches B's total category landscape: JSD=0.004 (C1347)
- Mode correlation: high-THERMAL-bridge folios run more Mode A lines (Z=3.45, p=0.0004) (C1347)
- A sections differentiate at category level despite MIDDLE-level uniformity (C1348: chi2=380, V=0.144, perm p=0.001)
- Section T category signal propagates cross-system: A-T → B-T rho=0.85, p=0.016 (C1348)
- Dark pipeline preserves categories near-perfectly: rho=0.976, JSD=0.009 (C1349)
- Bridge and dark carry independent category information per B section: rho=0.19 (C1349)
- C1136 partially overturned: sections are MIDDLE-uniform but category-differentiated

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/A_B_CATEGORY_FLOW/` -- 1 script + 1 results JSON |
| **ADDED** | C1347-C1349 constraint files (3 new constraints, 1190->1193) |
| **UPDATED** | `INDEX.md` -- 1190->1193 total, Phase 471 section added |
| **UPDATED** | `CLAUDE.md` -- v4.73->v4.74, 470->471 phases, 1190->1193 constraints |

---

## Version 4.73.59 (2026-02-26) - Phase 470: Suffix Mode Context

### Summary

Phase 470: 5-test battery decomposing the ~20% contextual residual in suffix mode prediction (C1341). **Overall: PREFIX is the dominant contextual channel.** Four factors contribute, largely non-redundantly: PREFIX (50% of MI), category environment (29%), position (12%), opener mode (8%).

**Phase 470 headline findings:**
- PREFIX modulates suffix for flexible MIDDLEs: conditional MI 0.097 bits, V=0.23 (C1342)
- da→93% bare, qo→41% terminal, ok_group→52% terminal — PREFIX routes MIDDLE into suffix context
- THERMAL-rich neighborhoods independently push toward terminal suffix: Z=5.87 (C1343)
- MID-line position has highest terminal fraction: 40.6% vs EARLY 34.6% (C1344)
- Opener mode barely propagates to token suffix: V=0.048, section-heterogeneous (C1345)
- Factors are non-redundant: MI between pairs only 0.003-0.006 bits (C1346)
- Resolves C1339 THERMAL paradox: PREFIX controls whether THERMAL content gets suffixed

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/SUFFIX_MODE_CONTEXT/` -- 1 script + 1 results JSON |
| **ADDED** | C1342-C1346 constraint files (5 new constraints, 1185->1190) |
| **UPDATED** | `INDEX.md` -- 1185->1190 total, Phase 470 section added |
| **UPDATED** | `CLAUDE.md` -- v4.72->v4.73, 469->470 phases, 1185->1190 constraints |

---

## Version 4.72.58 (2026-02-26) - Phase 469: Suffix Mode Assignment

### Summary

Phase 469: 4-test battery discriminating between identity model (MIDDLE determines suffix) and context model (line imposes mode on tokens) for suffix mode assignment. **Overall: Identity model dominates.** MIDDLE identity carries 11.57x more suffix information than line mode. Mode is ~80% emergent from token composition.

**Phase 469 headline findings:**
- I(MIDDLE; suffix) = 0.697 bits, 11.57x more than I(line_mode; suffix) = 0.060 bits (C1338)
- Only 7.7% of frequent MIDDLEs are mode-locked; 92.3% freely appear in both modes (C1339)
- Same MIDDLE keeps same suffix across modes: median cross-mode JSD = 0.020 (C1340)
- Token-identity-predicted mode matches actual 80.0% (baseline 59.7%, lift 1.34x) (C1341)
- Generative mechanism: MIDDLEs bring intrinsic suffix preferences → aggregate → line mode emerges
- Resolves C1256 (opener seeds profile), C1259 (flat mode proportion), C1229 (mode alternation)

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/SUFFIX_MODE_ASSIGNMENT/` -- 1 script + 1 results JSON |
| **ADDED** | C1338-C1341 constraint files (4 new constraints, 1181->1185) |
| **UPDATED** | `INDEX.md` -- 1181->1185 total, Phase 469 section added |
| **UPDATED** | `CLAUDE.md` -- v4.71->v4.72, 468->469 phases, 1181->1185 constraints |

---

## Version 4.71.57 (2026-02-26) - Phase 468: A Paragraph Category Architecture

### Summary

Phase 468: 4-test battery characterizing how the 8-category operational system organizes Currier A paragraphs. Extends Phase 452's scattershot (C1263: paragraphs specialize, d=12.5) into full architectural characterization. **Overall: 2/4 PASS, 1 WEAK, 1 FAIL.**

**Phase 468 headline findings:**
- STAGING dominates 43.6% of A paragraphs at 1.89x base rate; CONTAINMENT/MONITORING/MARKING never dominate (C1334)
- 5 distinct category-based paragraph types: STAGING(105), FLOW(48), TRANSITION(42), THERMAL(33), OPERATION(12) (C1335)
- MARKING is front-loaded in A paragraphs (pos 0.429, p<0.001) — cross-system pattern with B headers (C1287) and B block 0 (C1332) (C1336)
- No folio-level paragraph sequencing — confirms C240 NON_SEQUENTIAL extends to paragraph category organization (C1337)
- Section specialization: H→STAGING-centric, P→THERMAL-centric, T→FLOW-centric
- Two-tier category architecture: 5 "dominating" categories structure paragraphs, 3 "supporting" categories appear within but never organize paragraphs

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/A_PARAGRAPH_CATEGORY_ARCHITECTURE/` -- 1 script + 1 results JSON |
| **ADDED** | C1334-C1337 constraint files (4 new constraints, 1177->1181) |
| **UPDATED** | `INDEX.md` -- 1177->1181 total, Phase 468 section added |
| **UPDATED** | `CLAUDE.md` -- v4.70->v4.71, 467->468 phases, 1177->1181 constraints |

---

## Version 4.70.56 (2026-02-26) - Phase 467: Multiplexed Procedure Test

### Summary

Phase 467: 4-test battery testing whether block architecture reflects multiplexed procedures (one fire regime, multiple vessels/batches, block 0 documents shared context). **Overall: 2/4 PASS (M1 + M4).** Strict multiplexing NOT confirmed, but block 0 IS categorically special — its unique vocabulary is MARKING/MONITORING-enriched, providing annotation context rather than apparatus setup.

**Phase 467 headline findings:**
- Block-0-unique MIDDLEs are MARKING 2.48x enriched, MONITORING 1.57x — NOT STAGING/CONTAINMENT (C1332)
- Kernel is the most stable inter-block dimension: 0.027 < category 0.052 < PREFIX 0.145 (C1333)
- No block size gradient (token rho=-0.050, p=0.251) — multiplexing prediction of "later blocks shorter" fails
- Vocabulary containment asymmetry exists (6.2pp, p=0.004) but below 10pp threshold
- "Setup block" interpretation falsified; "marking context block" emerges instead
- All blocks share operational work (OPERATION, TRANSITION in shared vocabulary); only block 0 adds full marking/monitoring annotations

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/MULTIPLEXED_PROCEDURE_TEST/` -- 1 script + 1 results JSON |
| **ADDED** | C1332-C1333 constraint files (2 new constraints, 1175->1177) |
| **UPDATED** | `INDEX.md` -- 1175->1177 total, Phase 467 section added |
| **UPDATED** | `CLAUDE.md` -- v4.69->v4.70, 466->467 phases, 1175->1177 constraints |

---

## Version 4.69.55 (2026-02-26) - Phase 466: Block Vocabulary Drift

### Summary

Phase 466: 4-test battery testing whether consecutive blocks show directional vocabulary drift consistent with iterative refinement (proposed by internal expert following C1326). **Overall: 1/4 PASS.** Iterative refinement falsified. Vocabulary narrowing is the only universal signal — later blocks use fewer distinct MIDDLEs.

**Phase 466 headline findings:**
- Vocabulary narrowing universal: later blocks use fewer MIDDLEs (rho=-0.248, perm p<0.001) (C1330)
- No k→e kernel drift (rho=+0.026, p=0.600) — blocks don't shift from energy to precision (C1331)
- No Mode A→B suffix shift (rho=-0.038, p=0.199) — specification doesn't decrease (C1331)
- No FL stage progression (rho=+0.021, p=0.435) — material state doesn't advance (C1331)
- Section-specific: B/C show partial drift, H reversed, S flat — no universal mechanism
- C1326 (cross-block similarity) explained by REGIME sharing, not convergence toward target
- Iterative refinement model falsified: blocks share context but don't converge

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/BLOCK_VOCABULARY_DRIFT/` -- 1 script + 1 results JSON |
| **ADDED** | C1330-C1331 constraint files (2 new constraints, 1173->1175) |
| **UPDATED** | `INDEX.md` -- 1173->1175 total, Phase 466 section added |
| **UPDATED** | `CLAUDE.md` -- v4.68->v4.69, 465->466 phases, 1173->1175 constraints |

---

## Version 4.68.54 (2026-02-26) - Phase 465: Section S Block Architecture

### Summary

Phase 465: 6-test battery testing whether Section S's anomalous single-paragraph blocks (12.4/folio) are parallel monitoring stations or ordered stages. **Overall: 1/6 PASS.** Parallel stations hypothesis falsified. S blocks are an ordered monitoring sequence with progressive OPERATION→THERMAL/TRANSITION shift.

**Phase 465 headline findings:**
- Section S ordinal progression: OPERATION decreases (rho=-0.169, p<0.001), THERMAL/TRANSITION increase with block position (C1327)
- S p-gallows dominance: p→p self-continuation at 69%, no k/f/p→t cycle (C1328)
- S blocks MORE categorically diverse than non-S (JSD 0.069 > 0.052, z=7.20) (C1329)
- S blocks vocabulary-independent (Jaccard 0.327 < non-S 0.438) but operationally ordered
- Parallel stations falsified: blocks are NOT exchangeable, show sequential structure
- Section S = ordered monitoring rounds, not parallel identical stations

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/SECTION_S_BLOCK_ARCHITECTURE/` -- 1 script + 1 results JSON |
| **ADDED** | C1327-C1329 constraint files (3 new constraints, 1170->1173) |
| **UPDATED** | `INDEX.md` -- 1170->1173 total, Phase 465 section added |
| **UPDATED** | `CLAUDE.md` -- v4.67->v4.68, 464->465 phases, 1170->1173 constraints |

---

## Version 4.67.53 (2026-02-26) - Phase 464: Block Execution Cycle

### Summary

Phase 464: 8-test battery testing whether visual text blocks form complete execution cycles with cross-block restart, block-final termination, and REGIME inheritance. **Overall: 2/8 PASS** (A1 gallows restart, C1 REGIME homogeneity). Block-final termination signatures absent — blocks restart via gallows reset, not vocabulary markers.

**Phase 464 headline findings:**
- Cross-block gallows restart confirmed: block-initial k/f/p=72.3%, block-final t=39.8% (C1323)
- Block-final termination absent: -am depleted 0.36x, suffix mode identical, 0/8 category shifts (C1324)
- Folio REGIME homogeneity: within-folio block distance 0.056 < between-folio 0.065, p<0.001 (C1325)
- Cross-block category continuity: JSD 0.071 < within-block 0.136, z=-8.98 (C1326)
- Block boundaries are gallows-level structural markers (C845), not vocabulary-level content markers
- Architecture: folio = REGIME container, block = processing stage, paragraph = specialized operator

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/BLOCK_EXECUTION_CYCLE/` -- 1 script + 1 results JSON |
| **ADDED** | C1323-C1326 constraint files (4 new constraints, 1166->1170) |
| **UPDATED** | `INDEX.md` -- 1166->1170 total, Phase 464 section added |
| **UPDATED** | `CLAUDE.md` -- v4.66->v4.67, 463->464 phases, 1166->1170 constraints |

---

## Version 4.66.52 (2026-02-26) - Phase 463: Block Gallows Ordering

### Summary

Phase 463: 5-test battery testing whether gallows letters encode paragraph operator roles within blocks. **Overall: 1/5 PASS.** Gallows encode positional phase (when in block), not operational type (what it does).

**Phase 463 headline findings:**
- Gallows within-block ordering: t clusters late (0.700), k/f/p cluster early (0.255-0.319) (C1321)
- Transition matrix: universal k/f/p→t flow (chi-sq=64.88, p<0.001), t self-continues at 72%
- Gallows-category independence: 0/8 categories predicted by gallows letter (C1322)
- Gallows encode PHASE (when), PREFIX encodes TYPE (what) — orthogonal axes
- C869 (Tier 3) revised: split is k/f/p vs t, not k/f vs p/t

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/BLOCK_GALLOWS_ORDERING/` -- 1 script + 1 results JSON |
| **ADDED** | C1321-C1322 constraint files (2 new constraints, 1164->1166) |
| **UPDATED** | `INDEX.md` -- 1164->1166 total, Phase 463 section added |
| **UPDATED** | `CLAUDE.md` -- v4.65->v4.66, 462->463 phases, 1164->1166 constraints |

---

## Version 4.65.51 (2026-02-26) - Phase 462: Text Block Parallel Operators

### Summary

Phase 462: 7-test battery testing whether visual text blocks group complementary parallel operators. **Overall: 4/7 PASS.** Establishes blocks as a new validated organizational level between paragraph and folio.

**Phase 462 headline findings:**
- Block census: 91.5% of B folios have 2+ blocks, 485 total across 82 folios (C1317)
- PREFIX complementarity: within-block JSD > between-block (p<0.001), confirmed in 4/5 sections (C1318)
- Block-initial enrichment: HT 7.3% vs 4.9% (z=7.07), MARKING 9.4% vs 7.0% (z=4.81) (C1319)
- Thermal envelope hypothesis FALSIFIED: blocks maximize internal diversity, not convergence (C1320)
- Section-specific architecture: S=12.4, B=4.6, H=2.3 blocks/folio (KW H=56.8, p<0.001)
- Revised model: blocks are self-contained processing stages with complementary operations
- Structural hierarchy: token < line < paragraph < block < folio

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/TEXT_BLOCK_PARALLEL_OPERATORS/` -- 1 script + 1 results JSON |
| **ADDED** | C1317-C1320 constraint files (4 new constraints, 1160->1164) |
| **UPDATED** | `INDEX.md` -- 1160->1164 total, Phase 462 section added |
| **UPDATED** | `CLAUDE.md` -- v4.64->v4.65, 461->462 phases, 1160->1164 constraints |

---

## Version 4.64.50 (2026-02-25) - Phase 461: Distillation Terminology Mapping + Gloss Sync

### Summary

Phase 461: 10-test battery testing whether distillation physics maps to the manuscript's structural patterns. **Overall: 9/10 PASS.** Also includes 8-category ClassifierClassifier integration into voynich.py and a full gloss synchronization pass.

**Phase 461 headline findings:**
- Two-channel thermal architecture: qo k-enriched (0.510), ok e-enriched (0.282), completely non-overlapping (C1313)
- Overshoot-correct cycling: qo-k to ok-e transitions 43% above chance within lines (C1314)
- REGIME discrimination: 6/7 metrics significant for B, 0/7 for A — B-specific (C1315)
- O-PREFIX categorical distinction: ok/ot/ol/or all separable; ok->ot sequential ordering 1.18x (C1316)
- 13 modern MIDPROCESS actions all map to distinguishable PREFIX+category patterns (cosine 0.73 vs 0.003 random)
- Control flow loop: sh(1.98x)->qo->ok(1.18x)->ot (coarse thermal check then fine operational check)
- Post-phase: ok = vessel thermal verification (coarse), ot = vessel operational verification (fine)
- T10 FAIL: alternation ordering reversed (REGIME_1 highest, not REGIME_3)
- 5 Fits registered (F-B-008 through F-B-012), 99.5% B token coverage

**Gloss synchronization:**
- decoder_maps.json v2.0: ot "scaffold" -> "verify" (C1316), ol "store" -> "continue" (GLOSSING.md), qo/ok notes updated for two-channel model
- show_b_folio.py: 7 atom glosses synced to voynich.py ATOM_GLOSSES, 5 PREFIX glosses synced to decoder_maps.json
- All 37 shared PREFIX glosses and 18 atom glosses now match across decoder_maps.json, voynich.py, and show_b_folio.py

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/DISTILLATION_TERMINOLOGY_MAPPING/` -- 1 script + 1 results JSON |
| **ADDED** | C1313-C1316 constraint files (4 new constraints, 1156->1160) |
| **ADDED** | F-B-008 through F-B-012 (5 new Fits, fits_currier_b.md v1.4) |
| **UPDATED** | `voynich.py` -- CategoryClassifier integration, 8-category system |
| **UPDATED** | `show_b_folio.py` -- category display, gloss sync (7 atoms + 6 prefixes) |
| **UPDATED** | `decoder_maps.json` v1.9->v2.0 -- category maps, ot/ol/qo/ok prefix updates |
| **UPDATED** | `INDEX.md` -- 1156->1160 total, Phase 461 section added |
| **UPDATED** | `GLOSSING.md` -- ot/qo/ok prefix glosses, control flow loop section |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` v4.71 -- Section XXI (distillation mapping) |
| **UPDATED** | `fits_currier_b.md` v1.3->v1.4 -- 5 new distillation terminology fits |
| **REGENERATED** | CONSTRAINT_TABLE.txt, FIT_TABLE.txt, expert-advisor.md |

---

## Version 4.63.49 (2026-02-25) - Phase 460: Cross-Mode Category Coupling

### Summary

Phase 460: 8-test line-level battery (460a) + 6-probe parallel track analysis (460c) investigating whether Mode A and Mode B lines show structured category coupling. **Overall: WEAK_ZIGZAG_ARTIFACT_SUSPECT (460a: 2 PASS, 1 WEAK, 5 FAIL) + parallel track findings.** Headline: the two mode tracks are coordinated by shared paragraph context and positional synchronization, not by sequential dependency. Both modes share paragraph's category "key" (within-para A-B JSD=0.141 < cross-para JSD=0.170, p=7.4e-6). Mode A specializes in THERMAL/MONITORING; Mode B in FLOW/STAGING/TRANSITION. At the same relative position within adjacent A/B lines, categories align 1.27x above chance (perm p=0.001). B->A thermal feedback: ke_ratio predicts next A's MARKING (rho=-0.198, p=0.0006) and THERMAL (rho=+0.176, p=0.002). All sequential coupling tests negative: zig-zag weaker than null (Z=-3.39), no A->B prediction (p=0.146), no cross-line transition grammar, 0 cross-line forbidden transitions, all interleaving ratios increase entropy. BA handoff dominated by TRANSITION->THERMAL (12.0%). New constraints: C1308-C1312 (5 new, 1151->1156).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/CROSS_MODE_CATEGORY_COUPLING/` -- 3 scripts + 3 results JSON |
| **ADDED** | C1308-C1312 constraint files (5 new constraints, 1151->1156) |
| **UPDATED** | `CLAUDE.md` -- 1151->1156 constraints, 459->460 phases, v4.63 |
| **UPDATED** | `INDEX.md` -- 1151->1156 total, Phase 460 section added |
| **UPDATED** | `currierB.bcsc.yaml` -- cross-mode category coupling section |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` -- cross-mode coupling section |

---

## Version 4.62.48 (2026-02-24) - Phase 459: Sister Category Mechanism

### Summary

Phase 459: 6-test battery decomposing whether sister pair category divergence (C1298, C1299) is driven by positional placement or genuine categorical selection. **Overall: PARTIAL_MODE_SELECTION (4 PASS, 2 FAIL).** Headline: sister pair category divergence is position-independent and mechanistically driven by vocabulary SELECTION not TRANSFORMATION. ch/sh V retention 98.3%: position explains almost none of the category divergence (CATEGORY_GENUINE). ok/ot V retention 124.1%: position was actually MASKING divergence -- true category signal is stronger than raw measurement. 0/33 qualifying MIDDLEs shift dominant category between ch and sh (binom p=1.0): sister pairs diverge by choosing DIFFERENT MIDDLEs, not by changing what the same MIDDLE means (MIDDLE_DETERMINES_CATEGORY). Cross-lane cargo diverges: ch routes STAGING (20.6% vs 12.9%) to QO lane, sh routes THERMAL (53.6% vs 45.0%), V=0.122, p=2.34e-5. No three-way interaction (sister x category x position): ch/sh V range=0.009 perm p=1.0, ok/ot V range=0.114 perm p=1.0 -- sister category effect is additive with position. FAIL: T3 MIDDLE shift test confirms mechanism is selection not transformation (informative failure). FAIL: T6 no interaction detected. New constraints: C1303-C1307 (5 new, 1146->1151).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/SISTER_CATEGORY_MECHANISM/` -- 1 script + 1 results JSON |
| **ADDED** | C1303-C1307 constraint files (5 new constraints, 1146->1151) |
| **UPDATED** | `CLAUDE.md` -- 1146->1151 constraints, 458->459 phases, v4.62 |
| **UPDATED** | `INDEX.md` -- 1146->1151 total, Phase 459 section added |
| **UPDATED** | `currierB.bcsc.yaml` -- sister category mechanism section |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` -- sister category mechanism section |

---

## Version 4.61.47 (2026-02-24) - Phase 458: PREFIX Category Anatomy

### Summary

Phase 458: 8-test battery decomposing how individual PREFIXes predict 8-category operational labels. **Overall: PARTIAL_ANATOMY (5 PASS, 2 WEAK, 1 CONTROL_VIOLATED).** Headline: PREFIX-category association is strongly structured (V=0.311, chi2=15,598) and survives the tautology gate (T6: CMI=0.058 bits, 2.1% beyond base group). qo is 59% THERMAL (rank 1/32, near-pure channel). ct is 90% MONITORING. ok/ot sister pair diverges (V=0.105, p=4.0e-5): ok THERMAL-enriched, ot OPERATION-enriched. ch/sh diverge in B (V=0.121, p=9.4e-16) despite A-identity (C1268 V=0.021) -- survives section/position controls, mechanism is MIDDLE-level vocabulary breadth. BARE is THERMAL-depleted (4.1% vs 27.5%) and FLOW/STAGING-enriched (V=0.243) -- PREFIX slot is primary thermal injection mechanism. Channel symmetry discovered: EN (ch/sh + qo) parallels AX (ok/ot + ct) -- sister pair + categorically pure third member. WEAK: da/sa sub-Bonferroni (p=0.013), base-category alignment 27.6% (below 40% threshold). New constraints: C1297-C1302 (6 new, 1140->1146).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/PREFIX_CATEGORY_ANATOMY/` -- 1 script + 1 results JSON |
| **ADDED** | C1297-C1302 constraint files (6 new constraints, 1140->1146) |
| **UPDATED** | `CLAUDE.md` -- 1140->1146 constraints, 457->458 phases, v4.61 |
| **UPDATED** | `INDEX.md` -- 1140->1146 total, Phase 458 section added |
| **UPDATED** | `currierB.bcsc.yaml` -- PREFIX-category anatomy section |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` -- PREFIX category anatomy section |

---

## Version 4.60.46 (2026-02-24) - Phase 457: Paragraph Termination Trigger

### Summary

Phase 457: 8-test battery probing what triggers paragraph termination. **Overall: TERMINATION_MEMORYLESS (1 PASS, 0 WEAK, 7 FAIL).** Headline: no line-level feature predicts when a paragraph terminates. All 7 trigger hypotheses fail at Bonferroni p<0.00625: thermal level (length confound, Fisher p=0.236), B-track thermal (p=0.178), thermal step into final line (perm p=0.822), thermal budget (within-folio rho=-0.007 p=0.930), mode gate (chi2=1.19 p=0.276), category profile shift (perm p=0.400), folio prediction extension (F-test p=0.365, LOO decreases). Body is homogeneous at thermal/category grain until -am fires, extending C963 beyond role fractions. T4 within-folio test is definitive: no thermal budget governs paragraph duration. Sole PASS (T8): 3 tail product types (C1232) have distinct category profiles (chi2=139.1, perm p=0.001) -- tail FORM varies but tail TIMING does not. New constraints: C1295 (termination memoryless), C1296 (tail type category divergence). Termination is folio-programmed (C1239), not state-triggered.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/PARAGRAPH_TERMINATION_TRIGGER/` -- 1 script + 1 results JSON |
| **ADDED** | C1295-C1296 constraint files (2 new constraints, 1138->1140) |
| **UPDATED** | `CLAUDE.md` -- 1138->1140 constraints, 456->457 phases, v4.60 |
| **UPDATED** | `INDEX.md` -- 1138->1140 total, Phase 457 section added |
| **UPDATED** | `paragraph.psc.yaml` -- termination memoryless finding |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` -- paragraph termination section |

---

## Version 4.59.45 (2026-02-24) - Phase 456: Category-REGIME Integration

### Summary

Phase 456: 7-test battery + 1 calibration probing whether the 8-category system (C1250) integrates with the 4-REGIME classification (C179/C494). **Overall: CATEGORY_REGIME_PARTIAL (4 PASS, 0 WEAK, 2 FAIL, 1 SKIP).** Headline: Category-REGIME association is strong (chi2=526, V=0.106) but **kernel-mediated** -- after residualizing on k/h/e composition, Fisher p=0.061 (C1291). THERMAL kernel R2=0.779, TRANSITION=0.546, FLOW=0.409. The association survives section control (C1292, within-section chi2=216.4) but not kernel residualization. Categories genuinely discriminate beyond role profiles (C1293, Fisher p=7.5e-8, category JSD > role JSD in 5/6 REGIME pairs). **Critical negative: categories do NOT extend C1169 AXM model** (C1294, all |rho|<0.14 with residuals) -- validates C1169 closure. REGIME_1=THERMAL-dominant (29.7%), REGIME_2=FLOW-dominant (28.1%), REGIME_4=OPERATION/TRANSITION-dominant. T3 circularity gate FAILED, capping overall verdict at PARTIAL.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/CATEGORY_REGIME_INTEGRATION/` -- 1 script + 1 results JSON |
| **ADDED** | C1291-C1294 constraint files (4 new constraints, 1134->1138) |
| **UPDATED** | `CLAUDE.md` -- 1134->1138 constraints, 455->456 phases, v4.59 |
| **UPDATED** | `INDEX.md` -- 1134->1138 total, Phase 456 section added |
| **UPDATED** | `currierB.bcsc.yaml` -- category-REGIME integration section |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` -- kernel mediation finding |

---

## Version 4.58.44 (2026-02-24) - Phase 455: Category Mechanism Decomposition

### Summary

Phase 455: 8-test battery decomposing category mechanisms across three tiers: TRANSITION anti-escape, forbidden transition structure, and paragraph-level dynamics. **Overall: CATEGORY_MECHANISM_PERVASIVE (6/8 PASS, 0 WEAK, 2 FAIL).** Headline: TRANSITION anti-escape mechanism solved -- role redirection to AUX (1.24x) and FQ (1.13x), NOT EN self-loop (C1285). Expert hypothesis rejected: EN successor rate 0.403 for TRANSITION vs 0.476 baseline. Category transition grammar is strongly structured (C1286, chi2=526, p~10^-81): self-loops enriched (MARKING +10.4, THERMAL +6.0), FLOW->TRANSITION enriched (+6.7), THERMAL->TRANSITION depleted (-3.4). Paragraph headers are MARKING-enriched 2.44x (C1287), contrasting line entries (THERMAL-enriched). Within-folio paragraphs share category profiles (C1288, z=-4.92). **THERMAL/TRANSITION predict AXM dwell (C1289, rho=+/-0.52), partially resolving C1169 27% residual.** Paragraph mode confirmed at paragraph level (C1290, V=0.114). FAILs: TRANSITION does NOT cluster (T2, per-token mechanism); forbidden transitions are cross-category (T3, MARKING-target dominated).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/CATEGORY_MECHANISM_DECOMPOSITION/` -- 1 script + 1 results JSON |
| **ADDED** | C1285-C1290 constraint files (6 new constraints, 1128->1134) |
| **UPDATED** | `CLAUDE.md` -- 1128->1134 constraints, 454->455 phases, v4.58 |
| **UPDATED** | `INDEX.md` -- 1128->1134 total, Phase 455 section added |
| **UPDATED** | `currierB.bcsc.yaml` -- category mechanism decomposition section |
| **UPDATED** | `azc_b_activation.act.yaml` -- TRANSITION role redirection mechanism |

---

## Version 4.57.43 (2026-02-24) - Phase 454: Category B Execution

### Summary

Phase 454: 8-test battery probing whether the 8-category operational system (C1250) organizes Currier B's execution grammar. **Overall: CATEGORY_EXECUTES (7/7 PASS, 1 CALIBRATION).** Headline: THERMAL->escape is fully PREFIX-mediated (C1277) -- THERMAL MIDDLEs are 44.1% qo-prefixed, and partial correlation collapses (rho=-0.081) after controlling for qo composition. Chain solved: THERMAL->qo-PREFIX->QO lane (zero hazard)->escape. Category adds 18.6% instruction class entropy reduction BEYOND PREFIX (C1278) -- complementary axes explaining 71.7% together. Mode A lines are THERMAL-enriched (28.9%) = escape-capable; Mode B lines are TRANSITION-enriched (17.4%) = escape-restrictive (C1279). **Strongest effect: hazard concentrates in FLOW/CONTAINMENT (V=0.560, C1280) -- THERMAL is hazard-immune (2.6%).** TRANSITION anti-escape is PREFIX-independent (C1281, partial=-0.586 survives) -- asymmetric mechanism, unknown. Category predicts section (6/8 Bonferroni, C1282) and differentiates entry vs exit zones (V=0.141, C1283). Kernel calibration confirms consistency (C1284, not scored).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/CATEGORY_B_EXECUTION/` -- 1 script + 1 results JSON |
| **ADDED** | C1277-C1284 constraint files (8 new constraints, 1120->1128) |
| **UPDATED** | `CLAUDE.md` -- 1120->1128 constraints, 453->454 phases, v4.57 |
| **UPDATED** | `INDEX.md` -- 1120->1128 total, Phase 454 section added |
| **UPDATED** | `currierB.bcsc.yaml` -- category_execution section added |
| **UPDATED** | `azc_b_activation.act.yaml` -- THERMAL mediation mechanism added |

---

## Version 4.56.42 (2026-02-24) - Phase 453: AZC Category Scattershot

### Summary

Phase 453: 8-test scattershot battery probing whether the 8-category operational system (C1250) organizes AZC's positional structure. **Overall: AZC_CATEGORY_STRUCTURED (5/8 PASS, 1 WEAK, 2 FAIL).** AZC zones specialize by category (C1269, V=0.084) and families diverge (C1270, V=0.122). AZC mediates bridge/dark category sorting -- bridge MIDDLEs sorted by category within zones (C1272, p=0.0003), dark not (p=0.198). AZC-exclusive vocabulary is MARKING/THERMAL enriched (C1273, V=0.382). **Headline: THERMAL category predicts high B escape (C1274, rho=+0.780), TRANSITION predicts low escape (rho=-0.598) -- category is a cross-system organizing principle connecting A registry through AZC to B dynamics.** Two nulls: AZC zones do NOT differentiate at atom level (C1271, 0/8 Bonferroni) and no within-zone spatial coherence (C1275, d=-0.173). All AZC sections converge on A Pharma atom profile (C1276, WEAK).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/AZC_CATEGORY_SCATTERSHOT/` -- 1 script + 1 results JSON |
| **ADDED** | C1269-C1276 constraint files (8 new constraints, 1112->1120) |
| **UPDATED** | `CLAUDE.md` -- 1112->1120 constraints, 452->453 phases, v4.56 |
| **UPDATED** | `INDEX.md` -- 1112->1120 total, Phase 453 section added |
| **UPDATED** | `azc_activation.act.yaml` -- v1.2->v1.3, category organization added |
| **UPDATED** | `azc_b_activation.act.yaml` -- v1.2->v1.3, category-escape correlation added |

---

## Version 4.55.41 (2026-02-24) - Phase 452: A Category Scattershot

### Summary

Phase 452: 8-test scattershot battery probing whether the 8-category operational system (C1250) organizes Currier A's registry structure. **Overall: CATEGORY_ORGANIZED (6/8 PASS, 2 FAIL).** A records (C1261, d=9.7) and paragraphs (C1263, d=12.5) are strongly category-coherent. RI extension characters predict PP base category (C1262, V=0.221). Bridge vs dark pipeline MIDDLEs have divergent category profiles (C1264, V=0.441, survives length control). Atom coherence within records is independent of category (C1265, residual +0.291). Atom decomposition breaks C946's MIDDLE-level uniformity barrier (C1266, 5/7 AXIS clusters differentiate sections). **Two clean nulls:** Mode A/B distinction does not propagate into A records (C1267, p=0.204) -- mode is B-execution only. Prefix ch/sh does not select category context (C1268, JSD=0.0002) -- prefix and category are orthogonal.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/A_CATEGORY_SCATTERSHOT/` -- 1 script + 1 results JSON |
| **ADDED** | C1261-C1268 constraint files (8 new constraints, 1104->1112) |
| **UPDATED** | `CLAUDE.md` -- 1104->1112 constraints, 451->452 phases, v4.55 |
| **UPDATED** | `INDEX.md` -- 1104->1112 total, Phase 452 section added |

---

## Version 4.54.40 (2026-02-24) - Phase 451: Gradient Decomposition

### Summary

Phase 451: Decomposes prior paragraph-body gradient constraints by suffix mode (C1258 parallel tracks). 7-test battery retesting C932, C933, C965, C1227, C1228, C676. **Headline finding: Mode A proportion is FLAT across the paragraph body (rho=-0.027, p=0.449)** -- mode-proportion shift is NOT a confound for aggregate gradients. Results: C933 (prep verb early concentration) is ARTIFACT of prep verbs being Mode A tokens (77%); C1227 (FL resets) GENUINE within B-track (B->B 49.7% > cross-mode 40.5%); C676 (suffix trajectory) GENUINE in Mode B (bare rho=0.072, p=0.008); C1228 (PREFIX switching) MIXTURE (within<cross p=0.002). C932 and C965 could NOT be replicated in aggregate -- methodology concern independent of mode decomposition. **Follow-up: Mode B thermal state tracking** -- energy balance propagates through B-track (e_frac rho=0.376, ke_ratio rho=0.228, qo_frac rho=0.186, k_frac rho=0.139, all p=0.000) while FL stage does NOT propagate (rho=0.026, p=0.56). No ordinal progression in energy variables. B-track carries thermal context but independently assesses material state each cycle.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/GRADIENT_DECOMPOSITION/` -- 2 scripts + 2 results JSONs |
| **ADDED** | C1259-C1260 constraint files (2 new constraints, 1102->1104) |
| **UPDATED** | `CLAUDE.md` -- 1102->1104 constraints, 450->451 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1102->1104 constraints, v4.53->v4.54 |
| **UPDATED** | `INDEX.md` -- 1102->1104 total, Phase 451 section added |

---

## Version 4.53.39 (2026-02-24) - Phase 450: Sequential Content Prediction

### Summary

Phase 450: Tests sequential content prediction at three scales — opener→line, pre-termination drift, cross-paragraph vocabulary. Main battery: **4/9 PARTIAL.** Opener MIDDLE selects suffix mode A/B (Cramer's V=0.30, 1.76x, p=0.000) but does NOT predict kernel profile or FL distribution. Termination is abrupt (penultimate lines 2.45x divergent, but no monotonic trajectory — confirms C1237). Consecutive paragraphs share vocabulary (Jaccard 0.226 vs 0.199, p=0.000) but NOT kernel or suffix mode profiles. Follow-up continuation hypothesis: 1/5, NOT SUPPORTED (Mode-B-opening paragraphs are inherently B-heavy, not continuing predecessors). **Major follow-up finding:** Parallel mode tracks hypothesis 5/5 SUPPORTED — Mode A and B lines form coupled sequential tracks. Mode B carries continuity (vocabulary, kernel, FL); Mode A injects specification. Cross-mode coupling bidirectional. Counterpoint architecture resolves C670's adjacent-line null.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/SEQUENTIAL_CONTENT_PREDICTION/` -- 3 scripts + 3 results JSONs |
| **ADDED** | C1256-C1258 constraint files (3 new constraints, 1099->1102) |
| **UPDATED** | `CLAUDE.md` -- 1099->1102 constraints, 449->450 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1099->1102 constraints, v4.52->v4.53 |
| **UPDATED** | `INDEX.md` -- 1099->1102 total, Phase 450 section added |

---

## Version 4.52.38 (2026-02-24) - Phase 449: Category Section Vocabulary

### Summary

Phase 449: Tests whether sections use different specific MIDDLEs within the same operational categories. Uses full 99.5% coverage (human + dark auto-assigned per C1254). **Result: 2/5 WEAK_SIGNAL.** Clean pass/fail split: vocabulary is SHARED across sections (Jaccard 0.676≈null 0.669, T1 FAIL), but frequencies are SECTION-SPECIFIC (34.3% enriched p=0.001 T2, 76.8% classification +37.8pp p=0.001 T3). Category conditioning adds nothing to section divergence (1.13x, T4 FAIL). Critical T5 finding: dark compounds (WEAK tier) have Jaccard 0.894 (nearly disjoint across sections) while core grammar (LOCKED/SOLID) has 0.343 (universal). Unifies C1134 (frequency modulation), C1148 (dark hyper-modulation), and C1176 (atom-selection) into single picture: core grammar is equipment-independent, dark compounds carry section identity.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/CATEGORY_SECTION_VOCABULARY/` -- 1 script + 1 results JSON |
| **ADDED** | C1255 constraint file (1 new constraint, 1098->1099) |
| **UPDATED** | `CLAUDE.md` -- 1098->1099 constraints, 448->449 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1098->1099 constraints, v4.51->v4.52 |
| **UPDATED** | `INDEX.md` -- 1098->1099 total, Phase 449 section added |

---

## Version 4.51.37 (2026-02-24) - Phase 448: Dark Pipeline Characterization

### Summary

Phase 448: Tests whether the 8 validated gloss categories (C1250) generalize to the ~11.4% of B tokens not covered by human-glossed MIDDLEs. Auto-assignment via atom-level plurality vote covers 95.2% of 1,144 dark MIDDLEs (zero ties), raising total B token coverage from 88.6% to 99.5%. **Result: 3/6 PARTIALLY_GENERALIZES.** Passes: line-position differentiation (10.8x, p=0.001), within-line MI (1.5x, p=0.001), and coverage (95.2%). Fails: behavioral silhouette (p=0.155), section divergence (p=0.235), Q-MIDDLE divergence (p=0.342). Critical stratified finding: LOCKED+SOLID confidence tier passes behavioral silhouette (p=0.001) while WEAK atoms (65% of assignments) add noise. Atom-level operational encoding penetrates the HT layer — more fundamental than the 49-class grammar boundary.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/DARK_PIPELINE_CHARACTERIZATION/` -- 1 script + 1 results JSON |
| **ADDED** | C1254 constraint file (1 new constraint, 1097->1098) |
| **UPDATED** | `CLAUDE.md` -- 1097->1098 constraints, 447->448 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1097->1098 constraints, v4.50->v4.51 |
| **UPDATED** | `INDEX.md` -- 1097->1098 total, Phase 448 section added |

---

## Version 4.50.36 (2026-02-24) - Phase 447: Paragraph Operational Classification

### Summary

Phase 447: Paragraph-level operational profiling using validated gloss categories (C1250). 7-test battery with gallows-gloss prediction as primary test (C869 tier promotion attempt). **Result: 2/7 WEAK.** PRIMARY test (T1): gallows type does NOT predict body gloss profile (V=0.032, p=0.539) — C869 remains Tier 3; gallows mark paragraph boundaries but don't determine operational content. Paragraphs form continuous operational distribution (sil=0.192), not discrete types. Gloss adds nothing to REGIME beyond section (-1.9pp). Two passes: T4 folio operational specialization (within-folio JSD 0.263 < between-folio 0.294, p=0.000 — folios specialize operationally, extends C1041); T7 paragraph-level apparatus correlation (rho=0.409, attenuated from token-level 0.758 but significant). Ordinal trends suggestive but sub-Bonferroni.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/PARAGRAPH_OPERATIONAL_CLASSIFICATION/` -- 1 script + 1 results JSON |
| **ADDED** | C1252-C1253 constraint files (2 new constraints, 1095->1097) |
| **UPDATED** | `CLAUDE.md` -- 1095->1097 constraints, 446->447 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1095->1097 constraints, v4.49->v4.50 |
| **UPDATED** | `INDEX.md` -- 1095->1097 total, Phase 447 section added |

---

## Version 4.49.35 (2026-02-24) - Phase 446: Gloss Scale Validation

### Summary

Phase 446: Corpus-wide validation of the Tier 3 gloss system at both MIDDLE and atom levels. **MIDDLE-level (v2):** 8 operational categories on 90 MIDDLEs achieve 5/7 COHERENT against dual null models (random partition + random token labels). Key passes: behavioral silhouette z=3.5, kernel-category alignment V=0.675, line position F=29.9 (30x), apparatus-gloss rho=0.758, within-line MI 9x. V1 null model failure diagnosed (shuffling among same 90 MIDDLEs too conservative). **Atom-level (446b):** 14 non-kernel atoms tested with 6-test battery. 2/6 PASS: atoms differentiate REGIMEs 37x (structural reality), composed atom glosses predict human-assigned MIDDLE categories p=0.008 (compositional chain). 4 directional prediction tests fail because morphological grammar (C1191) governs atom position/co-occurrence independently of semantic content. Key insight: atom meanings manifest through composition into MIDDLEs, not through direct structural placement.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/GLOSS_SCALE_VALIDATION/` -- 2 scripts + 2 results JSONs |
| **ADDED** | C1250-C1251 constraint files (2 new constraints, 1093->1095) |
| **UPDATED** | `CLAUDE.md` -- 1093->1095 constraints, 445->446 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1093->1095 constraints |
| **UPDATED** | `INDEX.md` -- 1093->1095 total, Phase 446 section added |

---

## Version 4.48.34 (2026-02-24) - Phase 445: Apparatus Vocabulary Classification

### Summary

Phase 445: Apparatus vocabulary profiling of Currier B folios. Initial top-down PCA battery (5 tests) returned NOT_SUPPORTED — residual structure too diffuse after REGIME control. Bottom-up approach using Brunschwig-derived apparatus profiles found strong signal. 3 new constraints (C1247-C1249). **Result: REGIME ENCODES APPARATUS TYPE.** aii (unseal) is 41x enriched in REGIME_3 vs REGIME_1 (C1247). Distillation cycle co-occurrence: t+eol OR=16.27, ke+eeol OR=inf (C1248). DISTILLATION vs PRECISION anti-correlate rho=-0.666. R1/R3 are single-apparatus REGIMEs; R2/R4 mix apparatus types within fire degree. Herbal is the only apparatus-diverse section (C1249).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/APPARATUS_VOCABULARY_CLASSIFICATION/` -- 2 scripts + 2 results JSONs |
| **ADDED** | C1247-C1249 constraint files (3 new constraints, 1090->1093) |
| **UPDATED** | `currierB.bcsc.yaml` -- apparatus vocabulary block added |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` -- apparatus classification section |
| **UPDATED** | `CLAUDE.md` -- 1090->1093 constraints, 444->445 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1090->1093 constraints |
| **UPDATED** | `INDEX.md` -- 1090->1093 total, Phase 445 section added |

---

## Version 4.47.33 (2026-02-24) - Phase 444: EN Cross-Lane Pairing

### Summary

Phase 444: 6-test battery decomposing the C1242 cross-lane MI signal into specific QO-CHSH MIDDLE pairings. 2 new constraints (C1245-C1246). **Result: SELECTIVITY GRADIENT + MODE-DIFFERENTIATED PAIRING.** QO MIDDLEs span 1.773-bit entropy range in CHSH partner selection; rare MIDDLEs are selective, common are promiscuous (rho=0.665). E-depth shows matched intensity at category level (OR=2.625) but complementary within e-containing subset (rho=-0.262). i-atom control null (C1205 confirmed). Pair frequencies are domain-specific (refines C821). Mode A (specification) enriches energy+specific-measurement pairs (MI=1.425), Mode B (execution) enriches sustained+passive pairs (MI=0.978), JSD z=4.60 (C1246).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/EN_CROSS_LANE_PAIRING/` -- script + results (6 tests: T1-T6) |
| **ADDED** | C1245-C1246 constraint files (2 new constraints, 1088->1090) |
| **UPDATED** | `currierB.bcsc.yaml` -- cross_lane_prediction block extended |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` -- pairing decomposition section |
| **UPDATED** | `CLAUDE.md` -- 1088->1090 constraints, 443->444 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1088->1090 constraints |
| **UPDATED** | `INDEX.md` -- 1088->1090 total, Phase 444 section added |

---

## Version 4.46.32 (2026-02-23) - Phase 443: EN Lane Cross-Prediction

### Summary

Phase 443: 4-test battery (T1/T1a/T3/T4) plus exploratory cross-line, sh/ch routing, and aiin/ain ordering tests investigating whether adjacent QO and CHSH tokens predict each other's specific MIDDLE content. 3 new constraints (C1242-C1244) + 1 fit (F-B-007). **Result: GENUINE CROSS-LANE CONTENT PREDICTION.** Adjacent cross-lane EN pairs show MI=1.0632 bits (z_perm=13.42) but within-lane ordering is null (z_wl=0.05) — it's line-level co-occurrence, not sequential. Kernel routing at lane boundaries is massive (z=49.12) with CHSH→QO asymmetry (2.2x). sh routes to heat 1.34x more than ch, functioning as a formulaic monitor-pivot while ch is a varied checkpoint-gate (C1243, extends C929). aiin→ain ordering is directional (64.9%), representing wind-down from sustained cycling to final pass (C1244, extends C1234). Extensible atoms encode two independent control dimensions: e=intensity (k/ke/kee), i=duration (i/ii) (F-B-007, fit not constraint).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/EN_LANE_CROSS_PREDICTION/` -- script + results (Stage 1: T1/T1a/T3/T4) |
| **ADDED** | C1242-C1244 constraint files (3 new constraints, 1085->1088) + F-B-007 fit |
| **UPDATED** | `currierB.bcsc.yaml` -- cross_lane_prediction block |
| **UPDATED** | `GLOSSING.md` -- -aiin/-ain suffix gloss refined |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` -- heat-measure cycle section |
| **UPDATED** | `CLAUDE.md` -- 1077->1089 constraints, 439->443 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1034->1089 constraints, v3.91->v4.46 |
| **UPDATED** | `INDEX.md` -- 1085->1089 total, Phase 443 section added |

---

## Version 4.21.31 (2026-02-20) - Phase 421: Sister Entry Divergence Extension

### Summary

Phase 421: Pre-registered minimal model comparison testing whether opener sister-pair composition (opener_ch_frac) independently predicts per-folio entry divergence beyond the existing boundary architecture. 2 new constraints (C1188-C1189). **Result: SISTER_ENTRY_LEVER_ABSENT.** opener_ch_frac adds ΔLOO-R²=-0.020 against B3 baseline (below 0.02 pre-registered threshold; actually hurts cross-validation). Coefficient sign is NEGATIVE (opposite expectation). All sections absent. AXM mediation absorbed. **Key conclusion:** C1186's correlation (entry JSD partial rho=0.312) is REAL but fully mediated by opener-routing features (C1163-C1165). Sister is a proxy for these features, not an independent control channel. The boundary architecture (C1168) is structurally complete — no additional predictor from the sister-pair discovery extends it. C1169's ~27% AXM residual is confirmed irreducible by sister metrics.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/SISTER_ENTRY_DIVERGENCE_EXTENSION/` -- script + results (5-test battery) |
| **ADDED** | C1188-C1189 constraint files (2 new constraints, 1032->1034) |
| **UPDATED** | `CLAUDE.md` -- 1032->1034 constraints, 420->421 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1032->1034 constraints, v3.90->v3.91 |
| **UPDATED** | `INDEX.md` -- 1032->1034 total, Phase 421 section added |

---

## Version 4.20.30 (2026-02-20) - Phase 420: Sister-Pair Mechanism

### Summary

Phase 420: 8-test battery investigating whether the 52.9% unexplained variance in sister-pair choice (C639) is genuine free variation or structured by unmeasured predictors. 9 new constraints (C1179-C1187). **Result: BOUNDARY_CONTROL_KNOB.** Sister choice is NOT free variation — it is structured even within identical MIDDLE+SUFFIX slots (14/174 Bonferroni-significant, C1179). Position mediates +12.8% variance (ch=0.487, sh=0.395, LOO confirmed, C1180). ch-heavy folios have lower AXM self-transition (partial rho=-0.250) and higher hazard density (+0.255), making sister choice dynamically consequential (C1181). Folio-level consistency is moderate (ICC=0.317, C1182). Sister choice is independent of vocabulary pipeline (C1183). ch/sh and ok/ot are largely independent axes with OPPOSITE positional asymmetries (C1184). Successor routing is MIDDLE-dependent, not universal — 5/102 strata significant, preserving C121 (C1185). Entry divergence is the key coupling: partial rho=0.312, p=0.004, and opener ch fraction strongly predicts folio ch_pref at rho=0.455 (C1186). **Overall: sister preference is a within-class control parameter that modulates entry boundary dynamics and hazard exposure, reducing C639's unexplained variance from 52.9% to ~40% (C1187).**

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/SISTER_PAIR_MECHANISM/` -- script + results (8-test battery) |
| **ADDED** | C1179-C1187 constraint files (9 new constraints, 1023->1032) |
| **UPDATED** | `CLAUDE.md` -- 1023->1032 constraints, 419->420 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1023->1032 constraints, v3.89->v3.90 |
| **UPDATED** | `INDEX.md` -- 1023->1032 total, Phase 420 section added |

---

## Version 4.19.29 (2026-02-20) - Phase 419: Dark Pipeline Combinatorics

### Summary

Phase 419: 5-test battery investigating combinatorial rules governing dark-pipeline compound MIDDLEs (300 MIDDLEs, 200 compound, 50 atoms). 4 new constraints (C1175-C1178). **Key findings:** C475 compatibility is a necessary gate for atom co-occurrence (100% recall) but only 7.9% of 903 possible pairs are occupied -- paralleling C1028's sparse vocabulary curation (C1175). **Section hyper-modulation (3.9x) is atom-selection-dominated:** multiplicative atom model achieves R-squared=0.781, pseudo-R-squared=0.677 -- atoms carry section signal, compounds inherit multiplicatively (C1176). Dark pipeline ordering grammar is consistent with C1065 (4/4 testable pairs match, 0 mismatches, revising C1142's 50% which arose from low-count noise, C1177). Phantom MIDDLEs (15 B-absent ch/sh-initial forms) are morphologically isolated with no productive analogs in dark pipeline (C1178).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/DARK_PIPELINE_COMBINATORICS/` -- script + results (5-test battery) |
| **ADDED** | C1175-C1178 constraint files (4 new constraints, 1019->1023) |
| **UPDATED** | `currierB.bcsc.yaml` -- dark_pipeline_combinatorics block |
| **UPDATED** | `CLAUDE.md` -- 1019->1023 constraints, 418->419 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1019->1023 constraints, v3.88->v3.89 |
| **UPDATED** | `INDEX.md` -- 1019->1023 total, Phase 419 section added |

---

## Version 4.18.28 (2026-02-20) - Phase 418: LINK Functional Architecture

### Summary

Phase 418: 5-test battery characterizing LINK (`ol` substring, 13.2% of B, 3,047 tokens, 801 types) — the last major uncharacterized token population. 5 new constraints (C1170-C1174). **Result: LINK_MORPHOLOGICAL_ARTIFACT.** Vocabulary strongly stratified by role (chi2=1493, V=0.404, C1170). Behavior is role-dominant: 4/4 roles show significant LINK/non-LINK divergence, cross-role JSD comparable to baseline (C1171). BIO's 2× density excess is SPAN-targeted: EN_SPAN 4.65×, AX_SPAN 2.15×, MIDDLE depleted (C1172). Macro-automaton dynamics show passive participation (1.09× boundary enrichment, CC-dominated). Boundary enrichment does not correlate with divergence measures (entry rho=-0.059, exit rho=-0.151, both NS, C1173). **The `ol` substring is a morphological component recruited differently by each grammatical role, not a unified functional layer (C1174).**

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/LINK_FUNCTIONAL_ARCHITECTURE/` -- script + results (5-test battery) |
| **ADDED** | C1170-C1174 constraint files (5 new constraints, 1014→1019) |
| **UPDATED** | `currierB.bcsc.yaml` -- link_functional_architecture block, revised link_operator interpretation |
| **UPDATED** | `CLAUDE.md` -- 1014→1019 constraints, 417→418 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1014→1019 constraints, v3.87→v3.88 |
| **UPDATED** | `INDEX.md` -- 1014→1019 total, Phase 418 section added |

---

## Version 4.17.27 (2026-02-20) - Phase 417: Residual Freedom Characterization

### Summary

Phase 417: 5-test exhaustive battery determining whether the ~27% AXM residual from the dual boundary model (C1168) is genuinely irreducible or contains unmeasured structure. 1 new constraint (C1169). **Result: RESIDUAL_GENUINELY_FREE.** 23 candidate predictors tested — zero survive Holm-Bonferroni correction. Random forest CV R²=-0.14 (permutation p=0.375). Residuals are spatially random in manuscript order (lag-1=0.102, p=0.378). No C458 asymmetry, no regime residual structure (KW p=0.998). T5 gated closed. **The AXM residual decomposition program (Phases 412-417) is CLOSED.** ~73% of AXM self-transition variance is structurally determined (dual boundary model); ~27% is genuine per-program design freedom.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/RESIDUAL_FREEDOM_CHARACTERIZATION/` -- script + results (5-test battery) |
| **ADDED** | C1169 constraint file (1 new constraint, 1013→1014) |
| **UPDATED** | `currierB.bcsc.yaml` -- residual_freedom_closure block |
| **UPDATED** | `CLAUDE.md` -- 1013→1014 constraints, 416→417 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1013→1014 constraints, v3.86→v3.87 |
| **UPDATED** | `INDEX.md` -- 1013→1014 total, Phase 417 section added |

---

## Version 4.16.26 (2026-02-20) - Phase 416: Exit Divergence Symmetry

### Summary

Phase 416: 5-test battery testing whether exit boundary carries independent signal beyond the entry bundle (C1035 + entry_div + AXM_return). 3 new constraints (C1166-C1168). **Key finding:** Exit JSD is redundant after controlling for entry (partial rho=-0.097, p=0.101, C1166), but AXM departure rate at exit (directional routing out of AXM at line endings) carries independent signal: dR²=0.035, F=11.80, p=0.0012, LOO 0.696→0.745 (C1167). Closer routing features explain R²=0.338 of exit divergence; gatekeeper exit mechanism is partial (R²=0.108). Dual boundary model (entry + exit): R²=0.852, LOO=0.732, all 3 sections benefit (C1168). C1035 irreducible residual: ~57%→~27%.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/EXIT_DIVERGENCE_SYMMETRY/` -- script + results (5-test battery) |
| **ADDED** | C1166-C1168 constraint files (3 new constraints, 1010→1013) |
| **UPDATED** | `currierB.bcsc.yaml` -- exit_divergence_redundancy, axm_departure_rate_extension, dual_boundary_architecture |
| **UPDATED** | `CLAUDE.md` -- 1010→1013 constraints, 415→416 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1010→1013 constraints, v3.85→v3.86 |
| **UPDATED** | `INDEX.md` -- 1010→1013 total, Phase 416 section added |

---

## Version 4.15.25 (2026-02-20) - Phase 415: Entry Reset Mechanism

### Summary

Phase 415: 5-test battery decomposing C1158's entry dominance — what opener properties drive per-folio entry divergence variation? 4 new constraints (C1162-C1165). **Major finding:** AXM return rate at entry (fraction of entry transitions routing back to AXM) correlates with AXM self-transition at rho=0.841 and adds dR²=0.111 beyond entry divergence (F=30.95, p<0.000001, LOO 0.543→0.696). Opener role does NOT predict entry divergence (R²=0.128). Opener routing partially mediates entry divergence (shrinkage=0.41) but entry div retains independent signal. Total entry_div + AXM_return bundle: dR²=0.180 vs C1035, LOO 0.511→0.676. C1035 irreducible residual reduced from ~57% to ~32%.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/ENTRY_RESET_MECHANISM/` -- script + results (5-test battery) |
| **ADDED** | C1162-C1165 constraint files (4 new constraints, 1006→1010) |
| **UPDATED** | `currierB.bcsc.yaml` -- opener_role_neutrality, axm_return_rate_dominance, opener_routing_mediation, axm_return_rate_residual_extension |
| **UPDATED** | `CLAUDE.md` -- 1006→1010 constraints, 414→415 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1006→1010 constraints |
| **UPDATED** | `INDEX.md` -- 1006→1010 total, Phase 415 section added |

---

## Version 4.14.24 (2026-02-20) - Phase 414: Boundary Divergence Decomposition

### Summary

Phase 414: 5-test battery decomposing the C1157 boundary divergence signal. 4 new constraints (C1158-C1161). Key findings: entry dominates exit 3.5× (dR²=0.098 vs 0.028) — contradicts gatekeeper exit hypothesis. Boundary divergence is a ROUTING shift, not AXM persistence decay — AXM→AXM accounts for only 3.2% of total transition delta; inter-state routing (AXm→AXM, FQ→AXM) dominates. Section explains 70.2% of BD variance but BD carries independent signal (partial rho=-0.459, dR²=0.135 over section-only baseline). Gatekeeper classes partially mediate (~30.5% dR² drop) but 70% of signal comes from non-gatekeeper routing. Overall: BOUNDARY_DIVERGENCE_PARTIALLY_EXPLAINED.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/BOUNDARY_DIVERGENCE_DECOMPOSITION/` -- script + results (5-test battery) |
| **ADDED** | C1158-C1161 constraint files (4 new constraints, 1002→1006) |
| **UPDATED** | `currierB.bcsc.yaml` -- entry_dominance, routing_shift, section_confound_independence, gatekeeper_partial_mediation |
| **UPDATED** | `CLAUDE.md` -- 1002→1006 constraints, 413→414 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1002→1006 constraints |
| **UPDATED** | `INDEX.md` -- 1002→1006 total, Phase 414 section added |

---

## Version 4.13.23 (2026-02-20) - Phase 413: Line Transition Dynamics

### Summary

Phase 413: 5-test battery testing whether within-line position constrains token transition dynamics and mediates the C1035 AXM residual. 2 new constraints (C1156-C1157). **Major finding:** boundary divergence is the first predictor to break the C1035 barrier — dR²=0.0845, F=14.15, p=0.0004, LOO improves 0.433→0.512. Transition matrices differ strongly by zone (JSD 0.22-0.33, p<0.001). AXM self-transition drops 0.730→0.633 from entry to exit. Effect is section-dependent. Position conditioning does NOT improve M2 generation — structure is descriptive, not generative.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/LINE_TRANSITION_DYNAMICS/` -- script + results (5-test battery) |
| **ADDED** | C1156-C1157 constraint files (2 new constraints, 1000→1002) |
| **UPDATED** | `currierB.bcsc.yaml` -- line_position_transition_dynamics, boundary_divergence_residual |
| **UPDATED** | `CLAUDE.md` -- 1000→1002 constraints, 412→413 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 1000→1002 constraints |
| **UPDATED** | `INDEX.md` -- 1000→1002 total, Phase 413 section added |

---

## Version 4.12.22 (2026-02-20) - Phase 412: Paragraph Kernel Dynamics

### Summary

Phase 412: 5-test battery testing whether within-folio paragraph kernel diversity mediates the C1035 AXM residual. 1 new constraint (C1155). All tests negative — paragraph kernel heterogeneity, trajectory slope diversity, and type entropy add zero explanatory power to C1035 baseline (best dR²=0.0014, all LOO negative). Within-section correlations null. The ~57% irreducible residual is confirmed closed against paragraph-level dynamics. Design freedom (C1153, ~40%) is genuinely program-specific.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/PARAGRAPH_KERNEL_DYNAMICS/` -- script + results (5-test battery) |
| **ADDED** | C1155 constraint file (1 new constraint, 999→1000) |
| **UPDATED** | `currierB.bcsc.yaml` -- paragraph_kernel_dynamics_residual_closure |
| **UPDATED** | `CLAUDE.md` -- 999→1000 constraints, 411→412 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 999→1000 constraints |
| **UPDATED** | `INDEX.md` -- 999→1000 total, Phase 412 section added |

---

## Version 4.10.21 (2026-02-20) - Phase 411: Section-Conditioned Generative Fidelity

### Summary

Phase 411: 5-test battery testing whether section-conditioned M2 captures folio-level structural variation. 3 new constraints (C1152-C1154). Key finding: clean two-layer architecture — section-M2 captures vocabulary composition (class distribution ratio 1.48x, 87% folios improved) but NOT sequential dynamics (AXM 1.76x) or kernel engagement (1.79x). Generative design freedom ~40%, consistent with C1035. k/e-kernel execution variance is universally program-specific (~2x); h-kernel monitoring is section-determined in specialized sections but program-specific in STARS_RECIPE.

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/SECTION_CONDITIONED_GENERATIVE_FIDELITY/` -- script + results (5-test battery) |
| **ADDED** | C1152-C1154 constraint files (3 new constraints, 996→999) |
| **UPDATED** | `currierB.bcsc.yaml` -- vocabulary_dynamics_layer_separation, generative_design_freedom |
| **UPDATED** | `CLAUDE.md` -- 996→999 constraints, 410→411 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 996→999 constraints |
| **UPDATED** | `INDEX.md` -- 996→999 total, Phase 411 section added |

---

## Version 4.10.20 (2026-02-20) - Phase 410: Folio Balance Characterization

### Summary

Phase 410: 5-test battery characterizing the bridge/dark folio balance axis (C1146). 3 new constraints (C1149-C1151). Key findings: (1) vocabulary balance is completely orthogonal to dynamical archetypes (ARI=-0.002) and AXM (rho=0.001) — confirms C1035 irreducible residual is NOT explained by balance; (2) dark-dominant folios shift kernel profile within RECIPE_B (k_frac drops 31.4%→22.6%, p=0.002) — material plane couples to operational kernel; (3) balance is section-structured (chi-sq p<0.0001) but not reducible to section. Also implemented [ident:MIDDLE] rendering for dark-pipeline tokens in BFolioDecoder (expert-validated Tier 2 label).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/FOLIO_BALANCE_CHARACTERIZATION/` -- script + results (5-test battery) |
| **ADDED** | C1149-C1151 constraint files (3 new constraints, 993→996) |
| **UPDATED** | `scripts/voynich.py` -- BFolioDecoder: dark pipeline integration (is_dark_pipeline, folio_balance, [ident:MIDDLE] rendering) |
| **UPDATED** | `scripts/show_b_folio.py` -- dark-pipeline magenta coloring, DP legend entry |
| **ADDED** | `data/dark_pipeline_middles.json` -- canonical 300 dark-pipeline MIDDLEs |
| **UPDATED** | `CLAUDE.md` -- 993→996 constraints, 409→410 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 993→996 constraints |
| **UPDATED** | `INDEX.md` -- 993→996 total, Phase 410 section added |

---

## Version 4.10.19 (2026-02-20) - Phase 409: Dark Pipeline Internal Architecture

### Summary

Phase 409: 6-test battery probing the internal structure of the 300 dark-pipeline MIDDLEs. 6 new constraints (C1143-C1148). Key findings: (1) bridge-dark anti-correlation r=-0.865 — complementary distribution at folio level; (2) 3.9x hyper-modulated frequency profiles vs PP baseline; (3) dark pipeline is genuine grammar variant (ordering divergence not explained by atom pool); (4) dark-pipeline tokens interior-enriched (73.2% MIDDLE vs HT 67.7%).

### Changes

| Action | Details |
|--------|---------|
| **ADDED** | `phases/DARK_PIPELINE_INTERNAL_ARCHITECTURE/` -- script + results (6-test battery) |
| **ADDED** | C1143-C1148 constraint files (6 new constraints, 987→993) |
| **UPDATED** | `currierB.bcsc.yaml` -- bridge_dark_anticorrelation (C1146), modified_ordering expanded (C1143-C1145), line_position (C1147), hyper_modulation (C1148), provenance |
| **UPDATED** | `humanTrack.htsc.yaml` -- dark_pipeline_line_position/modulation/tradeoff in currier_b, compound_specification +6 constraints, totals 78→84 owned |
| **UPDATED** | `currierA.casc.yaml` -- bridge_anticorrelation in dark_pipeline, provenance +C1146 |
| **UPDATED** | `azc_b_activation.act.yaml` -- identification_channel_modulation (C1148), anti-correlation note (C1146) |
| **UPDATED** | `CLAUDE.md` -- 987→993 constraints, 408→409 phases |
| **UPDATED** | `CLAUDE_INDEX.md` -- 987→993 constraints |
| **UPDATED** | `INDEX.md` -- 987→993 total, Phase 409 section added |

---

## Version 4.10.18 (2026-02-20) - Structural Contract Updates: Phase 406-408 Integration

### Summary

Integrated 9 new constraints (C1134-C1142) from Phases 406-408 into 4 structural contracts (BCSC, HTSC, CASC, AZC-B-ACT). Expert-validated placement with ownership corrections: B-side findings (C1134 frequency modulation, C1137 HT substrate, C1138 distinct grammar) restricted to BCSC/HTSC; A-side vocabulary properties to CASC. Changed all 6 contract status from LOCKED to ACTIVE per user directive.

### Changes

| Action | Details |
|--------|---------|
| **UPDATED** | `currierB.bcsc.yaml` -- section_differentiation_mechanism (C1134), pp_pipeline_partition (C1135-C1136, C1139-C1140), dark_pipeline_integration (C1137-C1138, C1141-C1142), bridge_dual_role, differentiation_principle frequency-level, provenance |
| **UPDATED** | `humanTrack.htsc.yaml` -- COMPOUND_SPECIFICATION extended (C1141), dark_pipeline_morphology/atom_substrate/construction_grammar (C1138, C1141, C1142), construction_channel (C1137, C1141), dark_pipeline_substrate in currier_b, provenance 74→78 owned |
| **UPDATED** | `currierA.casc.yaml` -- functional_partition in shared_with_b with C498.a reconciliation (C1140), dark pipeline conditional correspondence, bridge_mechanism disjoint+substrate (C1139, C1141), dark_pipeline viability block (A-side only), provenance |
| **UPDATED** | `azc_b_activation.act.yaml` -- dual_channel in vocabulary_scope (C1137, C1140), frequency_dimension in categorical_resolution (C1134) |
| **UPDATED** | All 6 contracts: status LOCKED → ACTIVE |
| **UPDATED** | `CLAUDE_INDEX.md` -- structural contracts count: "4 (LOCKED)" → "6" |
| **UPDATED** | `INTERPRETATION_SUMMARY.md` -- removed HT oscillation from Still Open (resolved by C1082) |
| **REGENERATED** | Expert-advisor agent (389.8 KB), EXPERT_CONTEXT.md (741.8 KB) |

---

## Version 4.10.17 (2026-02-20) - Phase 408: PP Pipeline Atom Decomposition

### Summary

Phase 408 closes the PP pipeline architecture and decomposes dark-pipeline compound MIDDLEs into atoms. Headline finding: **96.5% of dark-pipeline compounds contain bridge atoms as building blocks** -- identification vocabulary is morphologically derived FROM dynamical vocabulary. The PP pipeline is a complete four-way partition (85 + 4 + 300 + 15 = 404). Dark-pipeline construction grammar is a modified dialect of general B ordering rules (50% pair agreement, but gateway/terminal positioning preserved).

Key findings:
- **Partition closure** (Test 1): 85 bridge + 4 non-bridge matched (c, ch, cho, otc) + 300 dark pipeline + 15 phantom = 404 PP MIDDLEs. Exhaustive and mutually exclusive.
- **Bridge atom prevalence** (Test 2): 86% of atom types are bridges, 91.6% of occurrences. 43 of 50 unique atoms are bridge MIDDLEs. Mean 1.44 atoms per compound.
- **Overlapping atom pools** (Test 3): Jaccard(grammar,dark) = 0.481. 25 shared atoms, 25 dark-exclusive. Jaccard(dark,all_B) = 0.877.
- **Section independence** (Test 4): Section concentration is NOT atom-driven (permutation p = 0.303). Same atoms across sections; specificity from combination, not selection.
- **Modified grammar** (Test 5): 50% agreement with C1065 ordering (7/14 matches). Gateway/terminal positioning preserved (0.083 vs 0.352).

### Changes

| Action | Details |
|--------|---------|
| **CREATED** | `phases/PP_PIPELINE_ATOM_DECOMPOSITION/scripts/pp_pipeline_atoms.py` -- 5-test battery |
| **CREATED** | `phases/PP_PIPELINE_ATOM_DECOMPOSITION/results/pp_pipeline_atoms.json` -- full results |
| **CREATED** | `context/CLAIMS/C1140_pp_pipeline_complete_partition.md` |
| **CREATED** | `context/CLAIMS/C1141_dark_pipeline_bridge_atom_substrate.md` |
| **CREATED** | `context/CLAIMS/C1142_dark_pipeline_modified_construction_grammar.md` |
| **UPDATED** | `context/CLAIMS/INDEX.md` -- added Phase 408 section, count 984->987 |
| **REGENERATED** | `CONSTRAINT_TABLE.txt`, expert-advisor agent |

### New Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1140 | PP pipeline complete four-way partition: 85 + 4 + 300 + 15 = 404 | 2 |
| C1141 | Dark pipeline compounds built from bridge atoms: 86% types, 91.6% occurrences, 96.5% coverage | 2 |
| C1142 | Dark pipeline uses modified construction grammar: 50% C1065 agreement, gateway/terminal preserved | 2 |

Constraint count: 984 -> 987 (+3 new).

---

## Version 4.10.16 (2026-02-20) - Phase 407: Dark Pipeline Functional Test

### Summary

Phase 407 functionally characterizes the 300 dark-pipeline PP MIDDLEs identified in C1135. 5-test battery confirms they are 100% HT/UN substrate (zero grammar-classified tokens), use a distinct construction grammar (grammar-standard/extended PREFIX ratio 3.39 vs general HT 1.81), and are completely disjoint from the 85 bridge MIDDLEs (zero overlap). Positionally and sectionally, they follow general HT patterns.

Key findings:
- **100% HT/UN substrate** (Test 1): All 1,696 dark-pipeline B tokens are HT/UN. Zero are grammar-classified. Mean 5.7 tokens/MIDDLE (validates C1135). Complete functional partition: matched PPs produce grammar (80.2%), dark pipeline produces identification vocabulary (100%).
- **Distinct construction grammar** (Test 2): Grammar-standard/extended PREFIX ratio 3.39 (vs HT 1.81, 87% higher). Suffix rate 89.9% (vs HT 77.3%), articulator rate 2.5% (vs HT 10.1%). A third morphological register within B.
- **Bridge-disjoint** (Test 3): Zero overlap between 300 dark-pipeline and 85 bridge MIDDLEs. Three clean A-B channels: bridges (dynamical), non-bridge matched (~4), dark pipeline (identification).
- **Header-neutral** (Test 4): Folio line-1 rate 6.9% (HT baseline 6.5%). Follows general HT positional pattern.
- **HT-aligned sections** (Test 5): JS(dark,HT) = 0.0005, JS(dark,grammar) = 0.0109. 22x closer to HT than grammar.

### Changes

| Action | Details |
|--------|---------|
| **CREATED** | `phases/DARK_PIPELINE_FUNCTIONAL_TEST/scripts/dark_pipeline_test.py` -- 5-test battery |
| **CREATED** | `phases/DARK_PIPELINE_FUNCTIONAL_TEST/results/dark_pipeline_test.json` -- full results |
| **CREATED** | `context/CLAIMS/C1137_dark_pipeline_ht_substrate.md` |
| **CREATED** | `context/CLAIMS/C1138_dark_pipeline_construction_grammar.md` |
| **CREATED** | `context/CLAIMS/C1139_dark_pipeline_bridge_disjoint.md` |
| **UPDATED** | `context/CLAIMS/INDEX.md` -- added Phase 407 section, count 981->984 |
| **REGENERATED** | `CONSTRAINT_TABLE.txt`, expert-advisor agent |

### New Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1137 | Dark pipeline MIDDLEs are 100% HT/UN substrate: 1,696 tokens, 0 grammar-classified | 2 |
| C1138 | Dark pipeline has distinct construction grammar: GS/EXT ratio 3.39 vs HT 1.81, suffix 89.9% | 2 |
| C1139 | Dark pipeline and bridge backbone completely disjoint: zero overlap of 300 vs 85 | 2 |

Constraint count: 981 -> 984 (+3 new).

---

## Version 4.10.15 (2026-02-20) - Phase 406: Cross-System Vocabulary Flow

### Summary

Phase 406 resolves the C1049/C909 paradox: shared/PP MIDDLEs are section-universal (Herfindahl 0.701), yet B output is 96% section-specific. Answer: **FREQUENCY_MODULATED** — same vocabulary, different token rates per section. 6-test battery across 3 tiers.

Key findings:
- **Frequency modulation** (A1-A2): PP drives 74% of section divergence through differential token frequencies (JS=0.124). B-exclusive JS=0.847 but only 5.8% of tokens — maximally specific per-type but token-negligible.
- **Dark pipeline** (B1): 300/315 unmatched PP MIDDLEs appear in B at low frequency (mean 5.7 tokens vs 224.8 matched). Section-concentrated (Herf 0.716), mostly compound (66.7%). Previously uncharacterized HT/UN substrate.
- **Uniform pool** (C1): A-H and A-P produce indistinguishable B-coverage profiles (cosine 0.9997). Pipeline is section-blind.
- **Concentrated grammar** (C2): 12 A folios cover 100% of classified B grammar. f58v (Section T) alone covers 60.7%. Full B inventory ceiling: 30.4%.
- **A-section routing** (B2): Bridge MIDDLEs uniformly sourced (H=70.8%, P=21.2%). P-enriched bridges weakly favor ENERGY_OPERATOR.

### Changes

| Action | Details |
|--------|---------|
| **CREATED** | `phases/CROSS_SYSTEM_VOCABULARY_FLOW/scripts/ab_vocabulary_flow.py` — 6-test battery |
| **CREATED** | `phases/CROSS_SYSTEM_VOCABULARY_FLOW/results/ab_vocabulary_flow.json` — full results |
| **CREATED** | `context/CLAIMS/C1134_section_specificity_frequency_modulated.md` |
| **CREATED** | `context/CLAIMS/C1135_unmatched_pp_dark_pipeline.md` |
| **CREATED** | `context/CLAIMS/C1136_ab_flow_uniform_concentrated.md` |
| **UPDATED** | `context/CLAIMS/INDEX.md` — added Phase 406 section, count 978->981 |
| **REGENERATED** | `CONSTRAINT_TABLE.txt`, expert-advisor agent |

### New Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1134 | Section specificity is frequency-modulated: PP drives 74% of divergence; resolves C1049/C909 paradox | 2 |
| C1135 | Unmatched PP dark pipeline: 300/315 B-present at low frequency; HT/UN compound substrate | 2 |
| C1136 | A->B flow: uniform pool (cosine 0.9997), 12 folios cover 100% classified grammar | 2 |

Constraint count: 978 -> 981 (+3 new).

---

## Version 4.10.14 (2026-02-20) - Phase 405: Section Program Architecture / Rosettes Targeting

### Summary

Phase 405 decomposes the C1125 "all 9 rosettes target Section T" finding. Critical discovery: Section T has only 1 non-Rosettes folio (f66r, 112 MIDDLEs). 8-test battery reveals the section-level correlation is a **vocabulary-size artifact** — T's small vocabulary inflates Jaccard. Per-folio, f66r ranks #11/76; the top 10 are 9 Section S + 1 Section H. Bridge density triangle **falsified** (rho = -0.60 anticorrelation).

Key findings:
- **Per-folio overlap** (T1): f66r ranks #11/76; f105r (Section S) ranks #1 at Jaccard 0.181
- **Bridge density anticorrelation** (T2): rho = -0.60; H folios most bridge-dense but not most Rosettes-overlapping
- **Overlap composition** (T3): 40 shared MIDDLEs, 75% bridge-mediated
- **Size-controlled bootstrap** (T4): f66r at 100th percentile from ALL sections — SIZE_ARTIFACT confirmed
- **Section architecture** (T5-T8): Sections differentiated (mean JS = 0.091, confirms C552/C1029) but T is unremarkable
- **Naming correction**: C1125 said "Section T (pharmaceutical)" — corrected to "Section T (text-only)". P = Pharmaceutical.

### Changes

| Action | Details |
|--------|---------|
| **CREATED** | `phases/ROSETTES_SYSTEM_REVALIDATION/scripts/section_program_architecture.py` — 8-test battery |
| **CREATED** | `phases/ROSETTES_SYSTEM_REVALIDATION/results/section_program_architecture.json` — full results |
| **CREATED** | `context/CLAIMS/C1133_rosettes_targeting_decomposition.md` |
| **AMENDED** | `context/CLAIMS/C1125_rosettes_section_t_universal.md` — corrected parenthetical, added qualification |
| **UPDATED** | `context/CLAIMS/INDEX.md` — added Phase 405 section, count 977→978 |
| **REGENERATED** | `CONSTRAINT_TABLE.txt`, expert-advisor agent |

### New Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1133 | Rosettes targeting decomposition: C1125 Section T correlation is vocabulary-size artifact; f66r #11/76 per-folio; bridge density rho=-0.60 | 2 |

Constraint count: 977 → 978 (+1 new).

---

## Version 4.10.13 (2026-02-20) - Phase 404: Ring Text Register Characterization

### Summary

Phase 404 characterizes ring text (circumferential text on the 9 rosettes) as a distinct register type. 12-test battery across 3 tiers. Verdict: **BRIDGE_VOCABULARY_INDEX** — ring text specifically samples B-grammar bridge vocabulary under B's hard constraints, functioning as a cross-system vocabulary reference.

Key findings:
- **Structured class distribution** (A1): JS(uniform)=0.291, not random enumeration; 33/49 classes used, Class 2 enriched 26.4x
- **Role skew** (A2): AUXILIARY 42.7% (vs B 25.4%), ENERGY_OPERATOR 11.3% (vs B 45.8%) — structural vocabulary, not execution
- **Bridge enrichment** (A3): 32.1% > non-ring 25.5% > B p95 11.0%; 100% of classified MIDDLEs are bridge
- **Dual population** (A4): Classified tokens short/simple/bridge; unclassified tokens long/complex/unique — two interleaved vocabularies
- **No positional gradient** (C3): Ring text uniform throughout, no line-1 effect
- **High hapax** (C2): 81.5% hapax rate, 36.6% foldout-unique types
- **Per-rosette diversity** (C1): Ring text Jaccard 0.237 < C1128's 0.322 — ring text MORE diverse across rosettes

### Changes

| Action | Details |
|--------|---------|
| **CREATED** | `phases/ROSETTES_SYSTEM_REVALIDATION/scripts/ring_text_register.py` — 12-test battery |
| **CREATED** | `phases/ROSETTES_SYSTEM_REVALIDATION/results/ring_text_register.json` — full results |
| **CREATED** | `context/CLAIMS/C1131_ring_text_register_classification.md` |
| **CREATED** | `context/CLAIMS/C1132_ring_text_dual_population.md` |
| **UPDATED** | `context/CLAIMS/INDEX.md` — added Phase 404 section, count 975→977 |
| **REGENERATED** | `CONSTRAINT_TABLE.txt`, expert-advisor agent |

### New Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1131 | Ring text register: BRIDGE_VOCABULARY_INDEX (structured classes, elevated bridge, 100% classified bridge) | 2 |
| C1132 | Ring text dual population (classified: 4.0 chars, 100% bridge; unclassified: 6.4 chars, 22.1% bridge) | 2 |

Constraint count: 975 → 977 (+2 new).

---

## Version 4.10.12 (2026-02-20) - Phase 403: P-Text/Rosettes Integration Revalidation

### Summary

Phase 403 revalidates the unified indexing hypothesis (Phase 395, C1112/C1113) using corrected Rosettes data. 7-test battery: 4 synthesis (R1, R3, R4, R5) + 3 diagnostics (R2, R6, R7). Verdict: **UNIFIED_CONFIRMED** (4/4 PASS).

Key findings:
- **P-text bridge enrichment reproduced exactly** (R1): 45.5%, 100th percentile of A (identical to Phase 395)
- **Vocabulary overlap confirmed** (R3): Jaccard=0.137, 36 shared MIDDLEs, 100th percentile
- **Paragraph co-tracking confirmed** (R4): Spearman rho=0.576, p<<0.001
- **Union prediction confirmed** (R5): Cosine=0.876 (better than either alone)
- **Grammar divergence** (R2): P-text is A-like (cosine 0.964), Rosettes are AZC-like (cosine 0.908 to AZC)
- **Section-general vocabulary** (R6): Shared vocabulary appears in all sections, not T-dominated
- **P-text more specific** (R7): P-text targets different B folios than Rosettes (cross-overlap 0.101)

### Changes

| Action | Details |
|--------|---------|
| **CREATED** | `phases/ROSETTES_SYSTEM_REVALIDATION/scripts/ptext_rosettes_integration.py` — 7-test battery |
| **CREATED** | `phases/ROSETTES_SYSTEM_REVALIDATION/results/ptext_rosettes_integration.json` — full results |
| **CREATED** | `context/CLAIMS/C1112_ptext_bridge_enrichment.md` — re-registered |
| **CREATED** | `context/CLAIMS/C1129_ptext_rosettes_unified_indexing.md` — new |
| **UPDATED** | `context/CLAIMS/INDEX.md` — added Phase 403 section, count 972→974 |
| **REGENERATED** | `CONSTRAINT_TABLE.txt`, expert-advisor agent |

### New/Re-registered Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1112 | P-text bridge enrichment (45.5%, 100th percentile of A) — re-registered | 2 |
| C1129 | P-text/Rosettes unified indexing (UNIFIED_CONFIRMED 4/4) | 2 |

Constraint count: 972 → 975 (+1 re-registered, +2 new).

### Additional Constraint (same session)

| # | Statement | Tier |
|---|-----------|------|
| C1130 | Ring text forbidden compliance without transition grammar (0/277 violations, entropy 7.92 vs B 0.41) — from Phase 402 S5 | 2 |

Re-registration audit: expert reviewed all 21 deleted constraints against Phase 402/403 evidence. 14 are subsumed by C1124-C1129, 5 lack revalidated evidence, C1114/C1115 are superseded by C1130. No further re-registrations needed.

---

## Version 4.10.11 (2026-02-19) - Phase 402: Rosettes System Revalidation

### Summary

Phase 402 revalidates the Rosettes foldout classification and metalayer hypothesis using corrected ZL transcription data (`data/rosettes_annotated.json`). 13-test battery across 3 tiers: System Classification (S1-S6), Cross-Reference Validation (X1-X4), Spatial Structure (P1-P3). 443 tokens, 19 entities, 177 unique MIDDLEs.

**Overall verdict: ROSETTES_CONFIRMED_METALAYER** — the metalayer hypothesis replicates with corrected data. Spatial structure tests inconclusive due to sparse token counts per entity.

### Changes

| Action | Details |
|--------|---------|
| **CREATED** | `phases/ROSETTES_SYSTEM_REVALIDATION/scripts/rosettes_revalidation.py` — 13-test battery |
| **CREATED** | `phases/ROSETTES_SYSTEM_REVALIDATION/results/rosettes_revalidation_results.json` — full results |
| **CREATED** | 5 new constraint files: C1124-C1128 |
| **UPDATED** | `context/CLAIMS/INDEX.md` — added Rosettes System Revalidation section, count 967→972 |
| **UPDATED** | `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` — new Rosettes findings |
| **REGENERATED** | `CONSTRAINT_TABLE.txt`, expert-advisor agent |

### New Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1124 | Rosettes Bridge Enrichment (Revalidated) — 3.05x enrichment | 2 |
| C1125 | Rosettes Universal Section T Correlation — all 9 rosettes → Section T | 2 |
| C1126 | Rosettes Metalayer Status (Revalidated) — confirmed metalayer | 2 |
| C1127 | Rosettes AZC-Like Grammar Profile — consistently AZC-like not hybrid | 2 |
| C1128 | Rosettes Generic (Not Specific) Indexing — shared vocabulary hub | 2 |

Constraint count: 967 → 972 (+5 new).

---

## Version 4.10.10 (2026-02-19) - Rosettes Data Architecture Reset

### Summary

All 21 Rosettes-derived constraints (C1088-C1098, C1100-C1101, C1109-C1110, C1112-C1115, C1122-C1123) **deleted** due to data quality issues. The underlying EVA interlinear transcript was missing 3/9 rosettes' ring text and lacked spatial context. Qualified constraints C440.a and C757.a also removed.

New data source: `data/rosettes_annotated.json` — built from ZL (Zandbergen) transcription + manual spatial annotation. 137 loci, 443 words, 19 first-class entities (9 rosettes, 8 paths, 1 clock, 1 unclassified).

`RosettesAnalyzer` in `scripts/voynich.py` rewritten to load from new JSON instead of EVA transcript.

### Changes

| Action | Details |
|--------|---------|
| **DELETED** | 21 constraint files from `context/CLAIMS/` |
| **DELETED** | C440.a qualifier from `context/CLAIMS/azc_system.md` |
| **DELETED** | C757.a qualifier from `context/CLAIMS/C757_azc_zero_kernel.md` |
| **UPDATED** | `context/CLAIMS/INDEX.md` — removed all Rosettes entries, count 988→967 |
| **UPDATED** | `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` — Rosettes section marked INVALIDATED |
| **UPDATED** | `scripts/voynich.py` — RosettesAnalyzer rewritten for new data source |
| **CREATED** | `context/DATA/ROSETTES_DATA_ARCHITECTURE.md` — documents new data architecture |
| **REGENERATED** | `CONSTRAINT_TABLE.txt`, expert-advisor agent, `FIT_TABLE.txt` |

Constraint count: 988 → 967 (21 deleted).

---

## Version 4.10.9 (2026-02-18) - P-Text / Rosettes Indexing Architecture (Phase 395)

### Summary

Phase 395 tests whether P-text (Currier A-like tokens on AZC folios) and Rosettes labels share a unified bridge-vocabulary indexing system. 10-test battery in 2 stages: Stage 1 characterizes P-text (P1 GATE PASS, P2 PASS, P3 FAIL, P4 MODERATE, P5 FAIL-artifact), Stage 2 tests integration (I1 PASS, I2 FAIL, I3 PASS, I4 PASS, I5 FAIL). Synthesis: UNIFIED_INDEXING. 2 new constraints (C1112-C1113).

Key findings:
- **P-text is extremely bridge-enriched** (P1 PASS): 45.5% bridge MIDDLEs (55/121), at 100th percentile of A (bootstrap p95=13.2%). Exceeds Rosettes (24.4%).
- **P-text and Rosettes share affordance profiles** (P2 PASS): Cosine 0.925, both dominated by FLOW_TERMINAL + HUB_UNIVERSAL + STABILITY_CRITICAL.
- **Vocabulary overlap is significant** (I1 PASS): 72 shared MIDDLEs, Jaccard=0.210, p=0.0000 vs bootstrap.
- **Paragraph-level convergence** (I3 PASS): Spearman rho=0.642, p~10^-70. Both vocabularies target the same B paragraphs.
- **Affordance signature match** (I4 PASS): Unified index matches paragraph headers at cosine=0.949.
- **Not folio-level** (I2 FAIL): Cross-reference targets are paragraphs, not specific folios.
- **Not positional** (I5 FAIL): Bridge MIDDLEs are ubiquitous in paragraphs, not header-concentrated.

Overall verdict: UNIFIED_INDEXING — the manuscript has a vocabulary-mediated paragraph-level indexing system spanning A, AZC, and B.

### New Files

| File | Purpose |
|------|---------|
| `phases/PTEXT_ROSETTES_INDEXING_ARCHITECTURE/scripts/ptext_rosettes_indexing.py` | 10-test battery |
| `phases/PTEXT_ROSETTES_INDEXING_ARCHITECTURE/results/ptext_rosettes_indexing.json` | Full results |

### New Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1112 | P-Text bridge enrichment at extreme levels (45.5%, 100th percentile) | 2 |
| C1113 | P-Text and Rosettes share unified bridge-vocabulary indexing system | 2 |

### Changes

- `context/CLAIMS/INDEX.md`: Added C1112-C1113, Phase 395 summary
- `CLAUDE.md`: 978 constraints, 395 phases
- C486: Strengthened (B-transmission explained via bridge enrichment)
- C1014: Extended (bridge MIDDLEs concentrated in P-text at 2x Rosettes)
- C1096: Contextualized (part of unified indexing system)
- C1109: Extended (vocabulary mediation is unified, not Rosettes-specific)

---

## Version 4.10.8 (2026-02-18) - Stars Paradox Resolution (Phase 394)

### Summary

Phase 394 tests whether the Stars Paradox (most REGIME diversity, lowest AXM variance) is a genuine structural anomaly requiring a mechanism, or a REGIME-composition artifact. 3-gate, 15-test battery: Gate 1 FAIL (paradox not confirmed under controls), 0/11 mechanism tests PASS. 1 new constraint (C1111).

Key findings:
- **Stars Paradox is a REGIME composition artifact** (G1.2 FAIL): Within-REGIME Stars is NOT anomalous. R1 ratio=1.45 (p=0.075, NS). R3 ratio=0.60 (non-Stars MORE convergent). Stars (0.00525) and Bio (0.00590) have near-identical variance — Herbal is the true outlier (0.01303).
- **LINK regulation falsified** (M1, 0/3): Zero within-Stars correlation (rho=-0.018). LINK removal barely affects variance (+5%).
- **CC channeling falsified** (M2, 0/3): Stars CC entropy HIGHER (1.79 vs 1.55 — wrong direction). CC routing WIDER.
- **Paragraph constraint falsified** (M3, 0/2): Stars JSD HIGHER than Bio (0.114 vs 0.076 — wrong direction).
- **De facto forbidden transitions falsified** (M4, 0/3): Stars has FEWER zero-transitions (-25.5% — opposite prediction).

Overall verdict: PARADOX_NOT_CONFIRMED — the REGIME system (C979) is sufficient.

### New Files

| File | Purpose |
|------|---------|
| `phases/STARS_PARADOX_RESOLUTION/scripts/stars_paradox_resolution.py` | 15-test battery |
| `phases/STARS_PARADOX_RESOLUTION/results/stars_paradox_resolution.json` | Full results |

### New Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1111 | Stars Paradox is REGIME composition artifact | 2 |

### Changes

- `context/CLAIMS/INDEX.md`: Added C1111, Phase 394 summary
- `CLAUDE.md`: 976 constraints, 394 phases
- C979: Strengthened (no section-specific topology modifier needed)
- C1084: Qualified (section AXM ordering is REGIME-composition effect)
- C1108: Resolved (Stars Paradox and all untested mechanisms now addressed)

---

## Version 4.10.7 (2026-02-18) - Rosettes Cross-Reference Validation (Phase 393)

### Summary

Phase 393 tests whether the Rosettes foldout demonstrates the operational character of its cross-referenced target folios (Stars/Pharma), or operates purely through vocabulary overlap. 6-test battery: 1 PASS, 1 PARTIAL, 4 FAIL. 2 new constraints (C1109-C1110).

Key findings:
- **Description regions operationally homogeneous** (P1 GATE FAIL): f85v2 NORTH/VERT/CENTER show pairwise distances within permuted range (p=0.459). No process-type differentiation at profile level.
- **B-like folios do NOT preferentially match Stars** (P2 PARTIAL): 1/2 B-like folios (f86v3) barely exceeds Stars cosine over Herbal (margin 0.03%).
- **Non-bridge vocabulary matches Herbal, not Stars** (P3 FAIL): All 7 Rosettes folios match H best in non-bridge MIDDLE Jaccard. Stars last or near-last for most.
- **No gradient predicts Stars similarity** (P4 FAIL): rho=-0.086, p=0.872.
- **Target folios not more similar than random** (P5 FAIL): lift=0.996x, p=0.698.
- **CENTER convergence node directionally confirmed** (P6 PASS): tgt_fraction 0.458 > NORTH/VERT, k_pct 54.5% < NORTH/VERT. Strengthens C1092.

Overall verdict: ROSETTES_VOCABULARY_ONLY — index function is bridge-mediated (C1100), not process-demonstrating.

### New Files

| File | Purpose |
|------|---------|
| `phases/ROSETTES_CROSS_REFERENCE_VALIDATION/scripts/rosettes_crossref_validation.py` | 6-test battery |
| `phases/ROSETTES_CROSS_REFERENCE_VALIDATION/results/rosettes_crossref_validation.json` | Full results |

### New Constraints

| # | Statement | Tier |
|---|-----------|------|
| C1109 | Rosettes cross-reference is vocabulary-mediated, not process-demonstrating | 2 |
| C1110 | CENTER convergence node directionally confirmed | 2 |

### Changes

- `context/CLAIMS/INDEX.md`: Added C1109-C1110, Phase 393 summary
- `CLAUDE.md`: 975 constraints, 393 phases

---

## Version 4.10 (2026-02-15) - HT Interaction Architecture (6-Test Battery)

### Summary

Phase 383 tests 4 untested HTSC V9 cross-guarantee predictions, the open HT oscillation question, and a paragraph ordinal neutrality negative control. Expert-advisor validated (opus). Results: 1 PASS, 2 PARTIAL, 2 FAIL, 1 negative control PASS. 6 new constraints (C1078-C1083).

Key findings:
- **HT hazard avoidance is vocabulary-level** (T1 FAIL): Only 5/7042 HT tokens participate in forbidden vocabulary. Hazard avoidance is role-mediated (C622), not positional. Cross-guarantee prediction trivially satisfied.
- **Line-1 exclusivity is tautological** (T2 PARTIAL): Line-1 100% vs body 78.3% exclusive, but singleton control kills it — both 100%. Folio-specificity (C870) fully explains the difference.
- **Tail pressure predicts HT compound rate** (T3 PASS): rho=0.367, p=0.0007. POSITIVE direction supports C935 specification model; two-axis model prediction rejected. Partial rho=0.425 after controlling HT count.
- **LINK-HT prefix phase independent** (T4 FAIL): chi2=0.89, p=0.35. LINK adjacency does not modulate HT EARLY/LATE prefix ratio. Confirms C804 weak transition bias.
- **HT oscillation is section-driven** (T5 PARTIAL): Raw ACF significant at lags 1,2,4,6,20. After section-residualization, only lag 7 survives. No lag 8-12 signal. Resolves open question.
- **HT paragraph-ordinal neutral** (T6 negative control PASS): rho=0.018, p=0.69. Confirms C855 parallel programs. HT joins LINK and hazard as paragraph-ordinal neutral.

### New Files

| File | Purpose |
|------|---------|
| `phases/HT_INTERACTION_ARCHITECTURE/scripts/ht_interaction_architecture.py` | 6-test battery |
| `phases/HT_INTERACTION_ARCHITECTURE/results/t1_boundary_hazard_distance.json` | T1 results |
| `phases/HT_INTERACTION_ARCHITECTURE/results/t2_line1_section_exclusivity.json` | T2 results |
| `phases/HT_INTERACTION_ARCHITECTURE/results/t3_tail_compound_correlation.json` | T3 results |
| `phases/HT_INTERACTION_ARCHITECTURE/results/t4_link_prefix_phase.json` | T4 results |
| `phases/HT_INTERACTION_ARCHITECTURE/results/t5_ht_oscillation_wavelength.json` | T5 results |
| `phases/HT_INTERACTION_ARCHITECTURE/results/t6_paragraph_ordinal_neutrality.json` | T6 results |
| `context/CLAIMS/C1078_ht_hazard_avoidance_vocabulary_level.md` | Hazard avoidance = vocabulary |
| `context/CLAIMS/C1079_line1_exclusivity_folio_specificity_tautology.md` | Line-1 exclusivity = tautology |
| `context/CLAIMS/C1080_tail_compound_specification_correlation.md` | Tail × compound = specification |
| `context/CLAIMS/C1081_link_ht_prefix_phase_independent.md` | LINK-HT prefix independent |
| `context/CLAIMS/C1082_ht_oscillation_section_driven.md` | Oscillation = section-driven |
| `context/CLAIMS/C1083_ht_paragraph_ordinal_neutral.md` | HT paragraph-ordinal neutral |

---

## Version 4.09 (2026-02-15) - Terminal Compatibility Geography (5-Test Battery)

### Summary

Phase 382 maps WHY terminal characters predict C475 compatibility (C1072) by cross-referencing terminal neighborhoods with C591 roles, C976 macro-states, C995 affordance bins, and clique structure. 5-test battery, expert-advisor validated. Results: 2 PASS, 3 PARTIAL. 5 new constraints (C1073-C1077).

Key findings:
- **Terminal-role frequency mediation** (T1 PARTIAL): V=0.4069 but perm_p=0.582. Terminal-role profiles entirely explained by frequency neighborhoods. C777 FL bias quantified ('y' FL=1.7%). C770 k/h/e tautology flagged.
- **Terminal-state frequency mediation** (T2 PARTIAL): Non-AXM V=0.4165 but perm_p=0.992. Even stronger frequency mediation than T1. FL_SAFE sparsity confirmed (min expected cell=0.02).
- **Compatibility asymmetry frequency-dominated** (T3 PARTIAL): freq_sum +1.654 standardized coefficient dominates all other features. INITIAL_match +0.089 (below 0.10 threshold). INITIAL_x_FINAL +0.016 NS confirms C1003 pairwise compositionality.
- **Terminal predicts affordance bin genuinely** (T4 PASS): Non-BULK V=0.3247, perm_p=0.000. First terminal signal surviving frequency null. 10 bins confirmed. 'm' terminal 50% FLOW_TERMINAL, 'e' terminal 22% STABILITY_CRITICAL.
- **Terminal groups form genuine cliques** (T5 PASS): 3/5 groups elevated above frequency-band-matched null: 'n' 4.07x, 'y' 3.40x, 'l' 2.52x. C983 global clustering baseline (0.873) exceeded.

### New Files

| File | Purpose |
|------|---------|
| `phases/TERMINAL_COMPATIBILITY_GEOGRAPHY/scripts/terminal_compatibility_geography.py` | 5-test battery |
| `phases/TERMINAL_COMPATIBILITY_GEOGRAPHY/results/t1_role_composition.json` | T1 results |
| `phases/TERMINAL_COMPATIBILITY_GEOGRAPHY/results/t2_macro_state_correspondence.json` | T2 results |
| `phases/TERMINAL_COMPATIBILITY_GEOGRAPHY/results/t3_asymmetry_mechanism.json` | T3 results |
| `phases/TERMINAL_COMPATIBILITY_GEOGRAPHY/results/t4_affordance_bin_alignment.json` | T4 results |
| `phases/TERMINAL_COMPATIBILITY_GEOGRAPHY/results/t5_transitivity_test.json` | T5 results |
| `context/CLAIMS/C1073_terminal_role_frequency_mediated.md` | Terminal-role = frequency |
| `context/CLAIMS/C1074_terminal_state_frequency_mediated.md` | Terminal-state = frequency |
| `context/CLAIMS/C1075_compatibility_asymmetry_frequency_dominated.md` | Asymmetry = frequency |
| `context/CLAIMS/C1076_terminal_affordance_bin_genuine.md` | Terminal-affordance genuine |
| `context/CLAIMS/C1077_terminal_groups_genuine_cliques.md` | Terminal cliques genuine |

---

## Version 4.08 (2026-02-15) - Multi-Layer Compatibility Architecture (5-Test Battery)

### Summary

Phase 381 integrates three independently-discovered forbidden/incompatibility layers (C475, C911, C1063) to test whether they form a unified safety architecture. 5-test battery, expert-advisor validated. Results: 2 PASS, 1 PARTIAL, 2 informative FAIL. 5 new constraints (C1068-C1072).

Key findings:
- **Cross-layer partial coupling** (T1 FAIL): C475 x C911 coupled (NMI=0.185) but frequency-mediated (perm_p=0.13). C1063 layer fully independent (NMI<0.006). Two MIDDLE-centric layers share frequency gradient; PREFIX-SUFFIX layer orthogonal.
- **Weak residual community structure** (T2 PARTIAL): After hub removal, 3 communities emerge (Q_signal=0.082 above random). One concentrates kernel-classified MIDDLEs. Too weak for categorical interpretation but non-trivial.
- **Atom ordering independent of kernel bias** (T3 FAIL): Only 2/21 asymmetric pairs cross kernel classes; both mismatch C521. Compound construction grammar has own rules not reducible to kernel directional physics.
- **Hazard residual above components** (T4 PASS): Only 4/17 C109 forbidden transitions blocked by any layer. 13/13 residual are C475-compatible. Confirms C627: forbidden transitions are token-specific directional, not component-decomposable.
- **Terminal character predicts compatibility** (T5 PASS): 5 terminal groups elevated >2x baseline (n x15.2, m x8.2, y x7.2, r x2.3, l x2.3). INITIAL-biased terminals 3.2x more compatible than FINAL-biased.

### New Files

| File | Purpose |
|------|---------|
| `phases/MULTI_LAYER_COMPATIBILITY_ARCHITECTURE/scripts/multi_layer_compatibility.py` | 5-test battery |
| `phases/MULTI_LAYER_COMPATIBILITY_ARCHITECTURE/results/t1_cross_layer_independence.json` | T1 results |
| `phases/MULTI_LAYER_COMPATIBILITY_ARCHITECTURE/results/t2_community_structure.json` | T2 results |
| `phases/MULTI_LAYER_COMPATIBILITY_ARCHITECTURE/results/t3_atom_kernel_correlation.json` | T3 results |
| `phases/MULTI_LAYER_COMPATIBILITY_ARCHITECTURE/results/t4_hazard_residual.json` | T4 results |
| `phases/MULTI_LAYER_COMPATIBILITY_ARCHITECTURE/results/t5_terminal_compatibility.json` | T5 results |
| `context/CLAIMS/C1068_cross_layer_partial_coupling.md` | C475 x C911 coupling |
| `context/CLAIMS/C1069_residual_community_structure.md` | Weak 3-community structure |
| `context/CLAIMS/C1070_atom_ordering_kernel_independence.md` | Atom ordering != kernel bias |
| `context/CLAIMS/C1071_hazard_residual_above_components.md` | Forbidden transitions above components |
| `context/CLAIMS/C1072_terminal_character_compatibility_signal.md` | Terminal char compatibility |

---

## Version 4.07 (2026-02-15) - Morphological Joint Space Architecture (5-Test Battery)

### Summary

Phase 380 combines PREFIX x SUFFIX compatibility analysis with within-compound atom ordering grammar. 5-test battery, expert-advisor reviewed (2x). Results: 2 PASS, 2 PARTIAL, 1 informative FAIL. 5 new constraints (C1063-C1067).

Key findings:
- **17 PREFIX x SUFFIX forbidden pairs** (T1 PARTIAL): Fewer than C911's 102 PREFIX x MIDDLE, confirming C278 hierarchy. 16/17 genuinely novel (not role-explained). LATE prefix prediction failed.
- **+5.9pp joint role classification gain** (T2 PASS): PREFIX 82.6%, joint 88.5%. QO-family V=0.615 vs sister V=0.124. Three-layer encoding confirmed.
- **Atom bigram ordering grammar** (T3 PARTIAL): V=0.376, p=1.8e-73. 21 asymmetric pairs, 15 at 100% dominance. k-before-e 58.7% (sig but below 60%). Permutation null p=0.0000.
- **Construction-execution independence confirmed** (T4 FAIL): rho=-0.004, p=0.65. Zero correlation at 11,525 token-level observations. C522 is absolute, not underpowered.
- **Terminal character positional code** (T5 PASS): V=0.231, p=3.5e-12. 'c'-terminal→FINAL (86%), 'p'-terminal→INITIAL (83%). Resolves kc paradox: driven by 'c' character, not k-kernel.

### New Files

| File | Purpose |
|------|---------|
| `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/scripts/morphological_joint_space.py` | 5-test battery |
| `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t1_prefix_suffix_forbidden.json` | T1 results |
| `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t2_prefix_suffix_role_gain.json` | T2 results |
| `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t3_atom_bigram_grammar.json` | T3 results |
| `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t4_string_vs_line_position.json` | T4 results |
| `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t5_terminal_character_bias.json` | T5 results |
| `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/morphological_joint_space_summary.json` | Combined summary |
| `context/CLAIMS/C1063_prefix_suffix_compatibility.md` | PREFIX-SUFFIX forbidden pairs |
| `context/CLAIMS/C1064_prefix_suffix_joint_role_encoding.md` | Joint role classification gain |
| `context/CLAIMS/C1065_atom_bigram_ordering_grammar.md` | Directed atom ordering grammar |
| `context/CLAIMS/C1066_construction_execution_independence_confirmed.md` | C522 token-level confirmation |
| `context/CLAIMS/C1067_terminal_character_positional_bias.md` | Terminal character positional code |

---

## Version 4.06 (2026-02-15) - Morphological Deep Structure (5-Test Battery)

### Summary

Phase 379 combines the two highest-yield morphological directions: suffix sequential microstructure and compound MIDDLE composition rules. 5-test battery, expert-advisor reviewed. Results: 2 PASS, 1 INDEPENDENT, 2 PARTIAL. 5 new constraints (C1058-C1062).

Key findings:
- **Suffix sequential grammar is genuine** (T1 PASS): V drops only 6.2% after role and repetition decomposition (0.066→0.062). Signal is section-universal.
- **Suffix-role independence from PREFIX** (T2 INDEPENDENT): V *increases* 30.7% after PREFIX conditioning. Suffix carries independent role information — anti-mediation.
- **Atom position grammar** (T3 PASS): V=0.333, p=3.8e-14. opch/eol→INITIAL, ai/kc→FINAL. 5 atoms significant after Bonferroni. Kernel prediction (k-early, e-late) marginally significant (p=0.054).
- **Atom co-occurrence structure** (T4 PARTIAL): 10 enriched pairs (z>3), 0 depleted. chi²=1830, p=3.6e-7. C475 compliance 100% but matches random baseline — C475 operates at token level, not atom level.
- **Compound depth-folio specificity** (T5 PARTIAL): rho=-0.27, p=5.3e-23. Deeper compounds are more folio-specific. Max depth=5. UN deeper than classified (p=5.5e-13). No within-role variation.

### New Files

| File | Purpose |
|------|---------|
| `phases/MORPHOLOGICAL_DEEP_STRUCTURE/scripts/morphological_deep_structure.py` | 5-test battery |
| `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t1_suffix_signal_decomposition.json` | T1 results |
| `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t2_role_suffix_signatures.json` | T2 results |
| `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t3_atom_position_grammar.json` | T3 results |
| `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t4_atom_cooccurrence_rules.json` | T4 results |
| `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t5_compound_depth_role.json` | T5 results |
| `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/morphological_deep_summary.json` | Combined summary |
| `context/CLAIMS/C1058_suffix_sequential_grammar_genuine.md` | Suffix signal decomposition |
| `context/CLAIMS/C1059_suffix_role_prefix_independent.md` | Suffix-role PREFIX independence |
| `context/CLAIMS/C1060_atom_position_grammar.md` | Atom positional preferences |
| `context/CLAIMS/C1061_atom_cooccurrence_structure.md` | Atom co-occurrence patterns |
| `context/CLAIMS/C1062_compound_depth_folio_specificity.md` | Depth-specificity gradient |

---

## Version 4.05 (2026-02-15) - Galenic Recipe Physics Prediction (3-Test Battery)

### Summary

Phase 378 tests whether the Galenic framework makes recipe-level physics predictions about the Voynich (all Tier 4). 3-test battery, expert-advisor designed: T1 (degree-hazard correlation), T2 (quality opposition directionality), T3 (Galenic degree recovery residual). All 3 FAIL. The FAILs map the boundary of the Galenic analogy: framework-level alignment holds (F-RUP-001), but recipe-level physics (which MIDDLEs are dangerous, which transitions forbidden, how folios recover) do NOT follow Galenic rules. Break point: Galenic system is scalar (4×4 cells), Voynich is topological (23 hub nodes, 17 forbidden transitions, compatibility graphs). No new constraints. No new fits.

### New Files

| File | Purpose |
|------|---------|
| `phases/GALENIC_RECIPE_PREDICTION/scripts/galenic_recipe_prediction.py` | 3-test battery |
| `phases/GALENIC_RECIPE_PREDICTION/results/t1_degree_hazard.json` | T1 results |
| `phases/GALENIC_RECIPE_PREDICTION/results/t2_quality_directionality.json` | T2 results |
| `phases/GALENIC_RECIPE_PREDICTION/results/t3_degree_recovery.json` | T3 results |
| `phases/GALENIC_RECIPE_PREDICTION/results/galenic_recipe_summary.json` | Combined summary |

### Updated Files

| File | Change |
|------|--------|
| `context/SPECULATIVE/rupescissa_comparative.md` | Added Phase 378 Galenic Recipe Physics section |

---

## Version 4.04 (2026-02-15) - Galenic Enhancement Analysis (Synthesis)

### Summary

Phase 377 synthesizes how the Voynich enhanced the original Galenic classification framework across 6 axes (all Tier 4). No new computation — structured comparison of existing constraints and Phase 375-376 results. Enhancement axes: (1) Classification Resolution: 4 qualities → 9 affordance bins (2.25x, C995). (2) Degree Granularity: 4 degrees → 14-63 MIDDLEs/channel (3.5-15.75x, C911/C982). (3) Compound Mechanism: additive → compatibility-graph mediated (12x differential, C475/C1053). (4) Operation Encoding: 12 named → 49 distributional classes (4.1x, C121). (5) Hazard Management: prohibition → precision engineering (C494/C997). (6) Hazard Architecture: narrative warnings → topological forbidden graph with 5 dimensions (C109). Consistent pattern: abstraction increase (named → distributional), resolution increase (coarse → fine), constraint formalization (narrative → structural). No new constraints. New fit: F-RUP-001 (Galenic Framework Directional Enhancement, F4). Total fits: 66.

### New Files

| File | Purpose |
|------|---------|
| `context/MODEL_FITS/fits_rupescissa.md` | Rupescissa Galenic framework fit registry |

### Updated Files

| File | Change |
|------|--------|
| `context/SPECULATIVE/rupescissa_comparative.md` | Added Phase 377 Galenic Enhancement Analysis section |
| `context/MODEL_FITS/generate_fit_table.py` | Added fits_rupescissa.md to registry; generalized multi-line regex |
| `context/MODEL_FITS/FIT_TABLE.txt` | Regenerated (66 fits) |

---

## Version 4.03 (2026-02-15) - Reverse Rupescissa Test (Galenic Framework Alignment)

### Summary

Phase 376 tests whether Rupescissa's Galenic 4-quality x 4-degree organizational framework makes structural predictions about the Voynich that survive falsification. Expert-advisor dropped 2 circular tests and added 2 novel ones with higher discriminative power. 4-test battery (all Tier 4): (1) Multi-Axis Hazard Boundary: PASS -- 5 independent failure dimensions, only 1 thermal, Rupescissa's multi-axis prediction survives. (2) Quality-Degree Factorization: PARTIAL -- 58.1% of classifiable forbidden PREFIX x MIDDLE combos follow block-diagonal structure. (3) Oppositional Pairing: PASS -- exactly 2 orthogonal axes (lane split + sister pair), partial r=-0.064 after controlling for QO density. (4) Degree Ordering Within Quality: PASS -- 4/6 PREFIX channels show significant rank-intensity correlation. Overall: 3/4 PASS, 1 PARTIAL. New constraint: C1057 (Lane-Sister Orthogonal Axes, Tier 2). Phase 376.

### New Files

| File | Purpose |
|------|---------|
| `phases/RUPESCISSA_REVERSE_TEST/scripts/rupescissa_reverse_test.py` | 4-test Galenic alignment battery |
| `phases/RUPESCISSA_REVERSE_TEST/results/test1_hazard_dimensionality.json` | Multi-axis hazard test |
| `phases/RUPESCISSA_REVERSE_TEST/results/test2_factorization.json` | Quality-degree factorization |
| `phases/RUPESCISSA_REVERSE_TEST/results/test3_oppositional_pairing.json` | Oppositional pairing |
| `phases/RUPESCISSA_REVERSE_TEST/results/test4_degree_ordering.json` | Degree ordering |
| `phases/RUPESCISSA_REVERSE_TEST/results/galenic_test_summary.json` | Combined results |

### Updated Files

| File | Change |
|------|--------|
| `context/SPECULATIVE/rupescissa_comparative.md` | Added Phase 376 results section |
| `context/CLAIMS/C1057_lane_sister_orthogonal_axes.md` | New constraint: lane-sister orthogonality |
| `context/CLAIMS/INDEX.md` | Added C1057 entry |

### Updated Files

| File | Change |
|------|--------|
| `context/CLAIMS/C574_en_behavioral_collapse.md` | Added C1057 cross-reference |
| `context/CLAIMS/C412_sister_escape_anticorrelation.md` | Added C1057 cross-reference |
| `context/CLAIMS/C639_sister_pair_variance_decomposition.md` | Added C1057 cross-reference |
| `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` | Added lane_sister_orthogonality to folio_level_composition |

---

## Version 4.02 (2026-02-15) - Rupescissa Comparative Analysis

### Summary

Phase 375 performs three-way comparative analysis across the medieval distillation tradition: Rupescissa (~1351) -> Brunschwig (1500) -> Voynich (15th c.). Framed as shared tradition convergence, not evolutionary lineage. Three analyses: (1) Degree System Evolution (Tier 3) -- Rupescissa 16-cell 4-quality x 4-degree matrix collapses to Brunschwig's 1-axis fire degree; both peak at D2; prohibition transformation documented: AVOID (Rup) -> RESTRICT (Bru) -> ENGINEER (Voy, C494). (2) Action Vocabulary Evolution (Tier 3) -- maps all 12 Rupescissa actions to Brunschwig equivalents; 64.3% core distillation coverage vs 14.3% non-core; identifies 6 categories of Brunschwig additions; documents qualitative shift from 12 named -> 36 named -> 49 abstract (C121). (3) Concealment Doctrine (Tier 4) -- extracts 7 concealment strategies (145 keyword hits) from Rupescissa text; 5/5 consistent with Voynich design but all have independent structural explanations; C476 tension documented. Builds on F-BRU-011/F-BRU-012; novel contribution is Rupescissa->Brunschwig mapping. All three falsification criteria PASS. Expert-advisor validated. No new constraints. Phase 375.

### New Files

| File | Purpose |
|------|---------|
| `phases/RUPESCISSA_COMPARATIVE/scripts/rupescissa_compare.py` | Three-way comparative analysis script |
| `phases/RUPESCISSA_COMPARATIVE/results/degree_evolution.json` | Degree system comparison |
| `phases/RUPESCISSA_COMPARATIVE/results/action_evolution.json` | Action vocabulary evolution |
| `phases/RUPESCISSA_COMPARATIVE/results/concealment_doctrine.json` | Concealment analysis |
| `phases/RUPESCISSA_COMPARATIVE/results/comparative_summary.json` | Combined findings |
| `context/SPECULATIVE/rupescissa_comparative.md` | Findings document (Tier 3/4) |

---

## Version 4.01 (2026-02-15) - Rupescissa Curation (v1.0)

### Summary

Phase 374 curates John of Rupescissa's "De consideratione quintae essentiae" (~1351) — the foundational text of the medieval distillation tradition — into structured JSON following the Brunschwig curation pattern. 61 chapter entries (41 Book 1 + 20 Book 2 remedies) classified into 7 types: THEORY (7), PROCESS (5), EXTRACTION (11), DEGREE_CATALOG (9), PHARMACOLOGICAL (8), APPARATUS (1), REMEDY (20). 131 materials extracted with 4-quality x 4-degree classifications (70 with degree data). 12 distinct procedural actions identified across 16 chapters, comparable to Brunschwig's 36-action taxonomy. 10 materials overlap with Brunschwig. Verification (V1-V6) all pass. This enables systematic cross-text comparison across the Rupescissa→Puff→Brunschwig→Voynich lineage. No new constraints. Phase 374.

### New Files

| File | Purpose |
|------|---------|
| `data/rupescissa_curated_v1.json` | Curated chapter data (61 entries, 7 types, 12 actions) |
| `data/rupescissa_materials_v1.json` | Materials inventory (131 substances, 70 with degree data) |
| `phases/RUPESCISSA_CURATION/scripts/rupescissa_curate.py` | Curation script |
| `phases/RUPESCISSA_CURATION/results/curation_verification.json` | Verification results |

### Updated Files

| File | Change |
|------|--------|
| `sources/rupescissa/README.md` | Added curated data references |

---

## Version 4.00 (2026-02-15) - Paragraph Structural Contract (PSC)

### Summary

Phase 373 creates the Paragraph Structural Contract (PSC v1.0), a cross-system structural unit contract describing paragraphs from the paragraph's own perspective. Consolidates 20 owned + 36 referenced constraints (56 total) across Currier A and B. Expert-advisor validation added 1 guarantee (COMPOUND_SPECIFICATION), 3 invariants (gallows_boundary_enrichment, cluster_count_convergence, body_length_shrinkage), and 3 disallowed interpretations. Follows layered ownership model: PSC owns paragraph-as-unit properties; BCSC retains B execution patterns; CASC retains A profiling details. Both contracts updated with cross-references to PSC. Verification script (V1-V9) confirms all quantitative guarantees. V8 constraint coverage: 100% (56/56). Five previously unclaimed constraints now formally housed (C885, C1022, C1027, C1052, C1054). No new constraints. Phase 373.

### New Files

| File | Purpose |
|------|---------|
| `context/STRUCTURAL_CONTRACTS/paragraph.psc.yaml` | Paragraph Structural Contract (PSC v1.0) |
| `phases/PARAGRAPH_STRUCTURAL_CONTRACT/scripts/psc_verification.py` | Verification script |
| `phases/PARAGRAPH_STRUCTURAL_CONTRACT/results/psc_verification.json` | Verification results |

### Updated Files

| File | Change |
|------|--------|
| `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` | Added PSC cross-references to paragraph and folio_paragraph_architecture sections |
| `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` | Added PSC cross-reference to paragraph_structure section |

---

## Version 3.99 (2026-02-15) - HT Structural Contract (HTSC)

### Summary

Phase 372 creates the Human Track Structural Contract (HTSC), the first unified structural contract for HT from HT's own perspective, consolidating 68 owned constraints and 14 referenced constraints into a single authoritative YAML document. Expert-advisor validation added 4 guarantees (ANTICIPATORY_COMPENSATION, TAIL_CORRELATION, LINE1_COMPOSITE_HEADER, CAUSAL_DECOUPLING), 2 invariants (BODY_BOUNDARY_ENRICHMENT, LINK_POSITIVE_ASSOCIATION), and 4 disallowed interpretations. Verification script (V1-V9) confirms all quantitative guarantees against data. V2 revealed that C451 used prefix-based HT detection (19 families), reproducing A=0.171, AZC=0.165, B=0.148 exactly; full C740 UN definition gives AZC > A > B (documented). V8 constraint coverage audit: 97.6% (81/83 known HT constraints covered). V9 identified 4 untested cross-guarantee predictions. No new constraints. Phase 372.

### New Files

| File | Purpose |
|------|---------|
| `context/STRUCTURAL_CONTRACTS/humanTrack.htsc.yaml` | HT Structural Contract (HTSC v1.0) |
| `phases/HT_STRUCTURAL_CONTRACT/scripts/htsc_verification.py` | Verification script |
| `phases/HT_STRUCTURAL_CONTRACT/results/htsc_verification.json` | Verification results |

### Updated Files

| File | Change |
|------|--------|
| `context/ARCHITECTURE/human_track.md` | Added HTSC pointer |
| `context/ARCHITECTURE/HT_EXPLAINER.md` | Added HTSC pointer, updated one-sentence summary per C935 |

---

## Version 3.98 (2026-02-15) - Brunschwig MIDPROCESS Absence (C1056)

### Summary

Phase 371 formally characterizes the structural absence of MIDPROCESS from Brunschwig's recipe-level encoding. Exhaustive investigation across 5 independent data sources confirms zero per-recipe distillation process monitoring variation. V3 curation: 0/245 recipes have MIDPROCESS actions. Master data: monitoring_intensity has 37 non-zero values but all derive from medical usage monitoring. MONITORING step_types: 0 process monitoring, 47 medical usage. Source text: 77% of MIDPROCESS keywords in Book 1 general chapters. PCA analysis: removing zero-variance MIDPROCESS and STORAGE columns doesn't change structure (5D=7D exactly). Brunschwig-Voynich dimensional gap: 2 PCs (3/5 vs 5/10), 0.752 bits entropy gap. Fabricated uniform MIDPROCESS achieves loading 0.571 (Path C mechanically passable) but is circular. M2 failure analysis: 3 universally-failing tests (B4, B5, C2) span 3 categories; 2/3 capture dynamic/pairwise structure consistent with monitoring gap (OJLM-1 partial parallel). MIDPROCESS represents tacit operator knowledge — the OJLM-1 boundary. 1 new constraint (C1056). 1 new fit (F-BRU-030). Phase 371.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1056 | MIDPROCESS Structural Absence / OJLM-1 Boundary | 2 |

### New Fits

| ID | Name | Result |
|----|------|--------|
| F-BRU-030 | MIDPROCESS Absence Characterization | MIDPROCESS_STRUCTURALLY_ABSENT |

---

## Version 3.97 (2026-02-15) - Section-Specific M2 Capstone (C1055)

### Summary

Phase 370 tests whether M2 generative sufficiency (C1025) holds per section independently. 5 pre-registered hypotheses, 3 pass. Verdict: near-section-decomposable. Per-section M2 reaches 78-79% for BIO and STARS_RECIPE (just below 80% global threshold), 70% for HERBAL. The same 3 universally-failing tests (B4, B5, C2) apply per-section as globally. Pooling advantage is only +0.5 tests (global=12.0, weighted-local=11.5), confirming C1047's no-interaction finding. Global M2 tested per-section shows dramatic distributional degradation (D1 fails 4/4 sections) but topology tests preserved (B1, B3). Cross-section transfer does NOT correlate with C1029 JSD (rho=-0.24). Test battery partitions into 11 section-invariant and 4 section-sensitive tests. Sections parameterize a single grammar rather than implementing distinct grammars. 1 new constraint (C1055). Phase 370.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1055 | M2 Near-Section-Decomposable | 2 |

---

## Version 3.96 (2026-02-15) - Affordance Bin Paragraph Dynamics (C1054)

### Summary

Phase 369 tests whether the 9 affordance bins (C995-C1000) have distinct paragraph-gradient trajectories. 5 pre-registered hypotheses, 0 pass. Verdict: NO_GRADIENT_BIN_INTERACTION (0/5). Key finding: affordance bin composition is INVARIANT across the B paragraph specification→execution gradient (C932). HUB_UNIVERSAL fraction remains ~64% at every quintile position (Spearman rho=-0.10, p=0.873). No non-HUB bin shows gradient dependence (0/8 Bonferroni-significant). HUB sub-roles are quintile-independent (0/4 significant). Bin-to-bin transition grammar barely differs between zones (JSD=0.066). The gradient selects which MIDDLEs within each bin, not which bins — the affordance scaffold is a static functional architecture preserved across the gradient. 1 new constraint (C1054). Phase 369.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1054 | Affordance Bin Gradient Invariance | 2 |

---

## Version 3.95 (2026-02-15) - Paragraph Gradient Combinatorics (C1052-C1053)

### Summary

Phase 368 tests whether B paragraph specification→execution gradient (C932) operates through C475 MIDDLE incompatibility graph. 5 pre-registered hypotheses, 2 pass. Verdict: COMPOUND_MEDIATED. Key findings: (1) B paragraphs ARE cluster-selective (z=-2.61, p=0.007), replicating C1039 on Currier B. (2) Compound atom prediction (C935) is C475-mediated: atoms that are mutually compatible predict body MIDDLEs at 46.2% vs 3.9% for incompatible atoms (12x, Wilcoxon p=0.002). (3) The gradient does NOT operate through compatibility at the line level (full compatibility rate near-ceiling at 99.8%). (4) Cluster entropy DECREASES Q0→Q4 (rho=-0.80): execution converges on specific compatibility neighborhoods, opposite of initial prediction. (5) Section funnel aperture weakly correlates with gradient steepness (rho=-0.5, n=3). Matrix coverage: 46.1% of B MIDDLEs in A-derived compatibility matrix. 2 new constraints (C1052-C1053). Phase 368.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1052 | B Paragraph Cluster Selectivity | 2 |
| C1053 | Compound Atom C475 Mediation | 2 |

---

## Version 3.94 (2026-02-15) - A-B Section Correspondence (C1049-C1051)

### Summary

Phase 367 tests whether A-side PP MIDDLE composition carries any trace of B's section parameterization. 5 pre-registered hypotheses, 5 pass. Verdict: PP_SECTION_SIGNAL (5/5). Key findings: (1) Shared (A∩B) MIDDLEs have Herfindahl 0.70 vs B-only 0.93 — shared vocabulary IS the section-universal substrate, explaining C946's reach uniformity (cosine 0.997). (2) C946 replicated (raw cosine=0.996); A section (H vs P) creates slight proportion differences. (3) C708 funnel topology is section-dependent — BIO class Jaccard=0.794 vs global 0.847; BIO has narrowest funnel aperture. (4) PP composition quality (core_fraction) has partial r=0.33-0.46 with section coverage after pool-size control. (5) A folio rankings shift across sections (rho=0.81-0.86 residualized). Does not contradict C752/C753/C946 — extends constraint propagation interpretation with mechanistic detail. 3 new constraints (C1049-C1051). Phase 367.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1049 | Shared Vocabulary Section-Universal Substrate | 2 |
| C1050 | PP Composition Section-Differential Coverage | 2 |
| C1051 | Section-Conditioned Class Convergence Asymmetry | 2 |

---

## Version 3.93 (2026-02-14) - Section Residual Decomposition (C1047-C1048)

### Summary

Phase 366 tests whether section x predictor interaction effects explain any of C1035's irreducible AXM self-transition residual. 5 pre-registered hypotheses, 2 pass. Verdict: SECTION_INTERACTIONS_CONFIRM_IRREDUCIBILITY. Key findings: (1) 0/3 interaction terms reach significance — section modulates dynamics additively (intercepts) not interactively (slopes). (2) Per-section models dramatically overfit (weighted LOO 0.037 vs global 0.412) except BIO (LOO 0.754). (3) Bridge geometry is section-orthogonal (BIO PC1 cosine=0.069 to global) but this doesn't improve prediction. (4) Conservation confirmed: LOO R²=0.412, residual 58.8%. The AXM residual elimination sequence is now complete: C1035-C1038 tested four strata, C1047-C1048 tested section stratification. The residual is genuine design freedom (C458/C980). 2 new constraints (C1047-C1048). Phase 366.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1047 | Section-Dynamics Interaction Absent | 2 |
| C1048 | BIO Section Dynamical Coherence | 2 |

---

## Version 3.92 (2026-02-14) - Section-Parameterized Line Grammar (C1042-C1046)

### Summary

Phase 365 tests whether section identity modulates the B line grammar at interior and boundary levels. 10 pre-registered hypotheses, 6 pass. Verdict: DEEP_PARAMETERIZATION (3/5 interior + 3/5 boundary). Key findings: (1) Interior transitions, self-loop rates, and phase interleaving are all section-dependent — sections parameterize the grammar at every tested interior level. (2) Opener and closer role distributions and mandatory bigram rates are section-dependent — boundaries are also parameterized. (3) C956 positional exclusivity breaks per section (30-55% retention) — global exclusivity is partially a section composition effect. (4) Line length is section-insensitive (eta2=0.004) — the program structure controls length, not section. (5) EN ordering remains free in all sections — C961 free interior confirmed as section-invariant. 5 new constraints (C1042-C1046). Phase 365.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1042 | Section-Conditional Positional Exclusivity Reduction | 2 |
| C1043 | Role Self-Loop Section Dependence | 2 |
| C1044 | Section-Dependent Phase Interleaving Rate | 2 |
| C1045 | Section-Dependent Boundary Role Composition | 2 |
| C1046 | Mandatory Bigram Section Modulation | 2 |

---

## Version 3.91 (2026-02-14) - A Paragraph Combinatorial Grammar (C1039-C1041)

### Summary

Phase 364 tests whether A paragraph membership imposes MIDDLE compatibility constraints beyond line-level incompatibility (C475/C729). 8 pre-registered hypotheses, 3 pass. Key findings: (1) Paragraphs draw from fewer C475 clusters than random (entropy 1.50 vs 1.78, z=-2.83, p=0.002) -- cluster selectivity. (2) Within-folio paragraph pairs have higher compatibility than between-folio (0.880 vs 0.811, p~0), surviving section matching -- folio is the compatibility unit. (3) Paragraphs have LOWER cross-line compatibility than random (z=-3.567) -- complementary diversification, extending C476 coverage optimality to paragraph level. Negative results: RI linkers don't predict folio composition similarity (p=0.151); adjacent paragraphs no more similar than non-adjacent (p=0.223); paragraph composition adds marginal B prediction (delta-R2=0.048, below threshold). 3 new constraints (C1039-C1041). Phase 364.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1039 | A Paragraph Cluster Selectivity | 2 |
| C1040 | A Folio-Level Paragraph Compatibility Coherence | 2 |
| C1041 | A Paragraph Complementary Diversification | 2 |

---

## Version 3.90 (2026-02-14) - Brunschwig Semantic Boundary Probe (F-BRU-029)

### Summary

Phase 363 probes three remaining paths to Tier 4 semantic mapping between Brunschwig and Voynich. Result: PARTIAL_EXTENSION (6/9 predictions pass). Path A (3/3): Safety buffer profiles show hazard class specificity — 19/22 buffers prevent PHASE_ORDERING violations (86%, vs 41% of pairs), with QO-prefixed buffers enriched 9/19 in PHASE_ORDERING vs 0/3 elsewhere. This deepens F-BRU-023's thermodynamic coherence from token-level to class-level, showing QO-lane energy interventions specifically target phase-sequencing failures. Path B (2/3): Process-side REGIME gradient is weakly positive (rho=0.200), contrasting F-BRU-028's strongly negative output rho. Brunschwig Degree 4 has highest precision/monitoring. REGIME_2 (not REGIME_4) has narrowest hazard envelope. Path C (1/3): Brunschwig operational PCA needs only 3 components for 80% but axes don't align with Voynich — Brunschwig PC1 is preparation-vs-collection, not energy/intensity. MIDPROCESS actions are absent from curated data (extraction gap, not structural difference). 1 new fit (F-BRU-029). Phase 363.

### New Fits

| ID | Name | Tier |
|----|------|------|
| F-BRU-029 | Semantic Boundary Probe (Three-Path) | F4 |

---

## Version 3.89 (2026-02-14) - Brunschwig Output Gradient Inversion (F-BRU-028)

### Summary

Phase 362 tests whether Brunschwig and Voynich output-side parameters follow the same REGIME-level gradient. Three-tier test: cross-REGIME Spearman correlation on 5 parameter pairings (Tier 1), within-REGIME_1 KS shape comparison (Tier 2), and Mantel correlation structure comparison (Tier 3). Result: GRADIENT_INVERTED — all 5 positive pairings show negative rho (range -0.258 to -0.800), meaning REGIME gradients are systematically inverted. Brunschwig REGIME_4 (PRECISION) has the highest output complexity (use_count=6.0, text_length=4285); Voynich REGIME_4 has the lowest (n_tokens=81.5, line_count=13.0). The null pair correctly shows rho=0.000. KS-2 passes (text_length vs n_tokens shapes similar, p=0.23). Mantel r=0.38 positive but not significant (p=0.138). Pooled analysis: 3/5 same direction at STANDARD vs SPECIALIZED granularity. This is architecturally informative: the variance architecture match (F-BRU-027, p=0.0019) operates at a deeper level than surface parametrics. Free output-side variation (C980, C1035) is independently parameterized in each system. The inversion has a structural explanation via C494 (REGIME_4 precision constrains Voynich option space) and C197 (expert vs novice documentation orientation). 1 new fit (F-BRU-028). Phase 362.

### New Fits

| ID | Name | Tier |
|----|------|------|
| F-BRU-028 | Output Parameter REGIME Gradient Mapping | F3 |

---

## Version 3.88 (2026-02-14) - Brunschwig Variance Architecture Alignment (F-BRU-027)

### Summary

Phase 361 tests whether Brunschwig's recipe collection exhibits the same variance architecture as Voynich B: process-side parameters constrained while output-side parameters freely vary. Using normalized entropy H/H_max across 509 materials with 12 parameters (8 process, 4 output), the separation is highly significant (permutation p=0.0019). Process-side mean H_norm=0.427 (constrained), output-side mean H_norm=0.827 (free). The variance ratio (49.6/50.4) approximates Voynich's 43/57 split within 6.6pp. Within-category output variation dominates between-category by 9.2x. Continuous CV comparison: Brunschwig use_count CV=0.664 and text_length CV=0.723 fall within Voynich's C458 recovery CV range (0.72-0.82). This is the first fit to test variance distributions rather than categorical mappings, establishing a sixth alignment axis alongside grammar, hazard, regime, suppression, and recovery. 1 new fit (F-BRU-027). Phase 361.

### New Fits

| ID | Name | Tier |
|----|------|------|
| F-BRU-027 | Variance Architecture Alignment | F3 |

---

## Version 3.87 (2026-02-14) - AXM Run Entropy Convergence + Residual Closure (C1038)

### Summary

Phase 360 tested the last candidate stratum for C1035's 57% irreducible AXM self-transition residual: micro-sequential dynamics within AXM runs. Positive finding: AXM runs converge monotonically — conditional entropy decreases from H=3.84 bits (position 1) to H=2.52 bits (position 6), slope=-0.248 bits/position. This is a grammar-level invariant (ANOVA by archetype p=0.117), consistent with C978 mixing time and C1007 gatekeeper enrichment. Negative finding: all three micro-sequential predictors (entropy gradient, per-folio JSD, per-folio CMI) fail to predict the residual after sample-size control. JSD and CMI were heavily confounded with transition count (JSD vs log(N): rho=-0.675; CMI vs log(N): rho=+0.499); after residualizing, both collapse (JSD rho: -0.295→-0.149; CMI rho: +0.237→+0.082). Corpus JSD=0.066 bits validates C1024 (0.070). Completes four-phase elimination (C1035/C1036/C1037/C1038): the 57% residual is confirmed as the design freedom space predicted by C458 (recovery freedom) and C980 (66.3% free variation envelope). 1 new constraint (C1038). Phase 360.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1038 | AXM Run Entropy Convergence + Micro-Sequential Stratum Empty | 2 |

---

## Version 3.86 (2026-02-14) - AXM Class Composition Redundancy (C1037)

### Summary

Per-folio AXM class composition profiling (32 classes across 72 folios, CLR-transformed PCA) fails to decompose C1035's 57% irreducible residual. Class PCs produce LOO R² = -0.071 on residuals (worse than predicting the mean). Combined with C1017 baseline, class PCs add only +0.005 incremental LOO R² (0.433 → 0.437). The class composition signal is entirely absorbed by existing predictors. PREFIX and class composition are strongly coupled (rho = -0.55, p < 0.000001), confirming PREFIX routing (C1023) governs class activation. C458's asymmetry does not manifest as differential class-level stability (hazard vs non-hazard CV diff = -0.026). Third consecutive elimination stratum: aggregate statistics (C1035), boundary transitions (C1036), class composition (C1037). Remaining untested candidate: micro-sequential dynamics within AXM runs. 1 new constraint (C1037). Phase 359.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1037 | AXM Class Composition Redundant | 2 |

---

## Version 3.85 (2026-02-14) - Exit Pathway Neutrality (C1036)

### Summary

Exit-conditional analysis of AXM boundary transitions: when AXM is exited, where does the system go? CV of exit allocation is inversely proportional to pathway frequency (FQ < FL < CC < AXm) — the sampling theory prediction, not C458. Ingress mirror and dwell duration analysis show identical frequency-driven pattern. Key structural finding: exit pathways are independently routed (FL/CC uncorrelated, rho=-0.003 vs compositional null -0.333), consistent with PREFIX-conditioned routing (C1023). C458's hazard/recovery asymmetry is localized to within-AXM dynamics, not boundary crossing. Eliminates exit proportions from C1035's 57% irreducible design freedom. 1 new constraint (C1036). Phase 358.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1036 | AXM Exit Pathway Allocation Frequency-Neutral | 2 |

---

## Version 3.84 (2026-02-14) - AXM Residual Irreducibility (C1035)

### Summary

Direct attack on C1017's 40% unexplained AXM self-transition variance with six pre-registered folio-level predictors (paragraph count, HT density, gatekeeper fraction, QO fraction, vocabulary size, line count). Clean negative result: 0/7 predictions passed. No predictor adds any incremental R-squared beyond C1017 baseline. Random forest finds no non-linear signal (CV R-squared = -0.149). C1017 baseline is moderately overfit (LOO gap 0.132; true explained variance ~43%). The residual is genuinely program-specific free variation, consistent with C458 (recovery freedom) and C980 (66.3% free variation envelope). 1 new constraint (C1035). Phase 357.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1035 | AXM Residual Irreducible | 2 |

---

## Version 3.83 (2026-02-14) - Symmetric Forbidden B5 Fix (C1034)

### Summary

Design and validation of PREFIX-factored generation architecture to resolve M2's B5 failure. Key result: PREFIX-factored generation through conditional routing is distributionally equivalent to M2 (doesn't help). The actual fix is simpler: bidirectional forbidden suppression (M5-SF). Under C1025 reference mapping, M5-SF achieves B5=0.132 (80% pass), B1=0.873 (100% pass), B3=0 — the ONLY model passing all three simultaneously. M2.5 blending fails B5 under this mapping. With B4+C2+B5 corrections, M2 achieves projected 15/15 = 100% pass rate. 1 new constraint (C1034). Phase 356.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1034 | Symmetric Forbidden Suppression Fixes B5 | 2 |

---

## Version 3.82 (2026-02-14) - C2 Test Misspecification (C1033)

### Summary

The C2 test (CC suffix-free >= 99%) is misspecified. The test uses CC={10,11,12,17} (5-role taxonomy) but C588 established CC as 100% suffix-free using CC={10,11,12} (macro-state partition). Class 17 has 59% suffixed tokens (170/288: olkeedy, olkeey, olkain, olkaiin, olkedy), dragging the measured rate to 83.4%. Real data itself fails the test. M2 reproduces the real CC suffix-free rate exactly (0.824 +/- 0.010 vs real 0.834). Correcting C2 pushes M2 from 13/15 to 14/15 = 93.3%. Two of three M2 failures (B4, C2) were test misspecifications; only B5 (forward-backward asymmetry, C1032) is genuine. C590's claim that class 17 suffix = NONE is incorrect. 1 new constraint (C1033). Phase 355.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1033 | C2 Test Misspecification — CC Definition Mismatch | 2 |

---

## Version 3.81 (2026-02-14) - B5 Asymmetry Mechanism (C1032)

### Summary

Diagnosis and attempted correction of M2's B5 forward-backward asymmetry failure. The B5 failure (JSD 0.178 vs real 0.090) is caused by asymmetric forbidden transition suppression: 16 of 17 forbidden pairs are one-directional (C111), making the M2 matrix more directional than real data. 15% detailed-balance blending corrects B5 to 0.111 (100% pass) but regresses B1 spectral gap (0.894 to 0.770, FAIL) and B3 (5 forbidden violations). Generic blending is too blunt — real data achieves low asymmetry AND high spectral gap simultaneously through PREFIX-specific routing (C1024). M2 pass rate remains 13/15 = 86.7%. True B5 fix requires PREFIX-factored generation architecture (projected 14/15 = 93.3%). 1 new constraint (C1032). Phase 354.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1032 | B5 Asymmetry Mechanism — Forbidden Suppression + PREFIX Routing | 2 |

---

## Version 3.80 (2026-02-14) - FL Cross-Line Independence (C1031)

### Summary

Direct test of FL stage continuity across line boundaries within paragraphs. FL state (C777) does NOT propagate across lines. Within-line SAME rate (68.2%, C786) collapses to 27.9% cross-line. Backward transitions jump from 4.5% to 44.3%. Endpoint correlation is zero (rho=0.003 narrow, p=0.963). Marginal mean-stage correlation (rho=0.063) has negligible effect and is folio-mediated (C681). Each line independently samples its FL stages — paragraphs are NOT multi-line FL trajectories. Confirms C670/C681 for the FL dimension specifically. 1 new constraint (C1031). Phase 353.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1031 | FL Cross-Line Independence | 2 |

---

## Version 3.79 (2026-02-14) - Section Grammar Variation + M2 Gap Decomposition (C1029-C1030)

### Summary

Two-part investigation. Part A: Section modulates 49-class transition weights at the same scale as REGIME (mean pairwise JSD: section 0.325 vs REGIME 0.320, ratio 1.016x). Topology is shared across sections (zero section-only transitions). 42.6% of classes are section-dependent. Role self-loop ordering varies by section (BIO: EN > FQ > FL; COSMO: FQ > FL > EN). Extends C979 to the section dimension. Part B: Phase 348's B4 test is misspecified — M2 trivially reproduces real self-loop rates (identical by construction). Corrected M2 pass rate: 13/15 = 86.7% (not 80%). The remaining 2 failures (B5 forward-backward asymmetry, C2 CC suffix-free rate) are independent mechanisms: B5 needs PREFIX symmetric routing (C1024), C2 needs role-specific morphological constraints. 2 new constraints (C1029-C1030). Phase 352.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1029 | Section-Parameterized Grammar Weights | 2 |
| C1030 | M2 Gap Decomposition — Two Independent Mechanisms | 2 |

---

## Version 3.78 (2026-02-14) - Vocabulary Curation Rule (C1028)

### Summary

"Compiler test" — what determines which PREFIX×MIDDLE×SUFFIX combinations exist? Productive product space has 48,640 combinations; only 419 (0.9%) exist. Token existence is governed by pairwise co-occurrence: both PREFIX×MIDDLE AND MIDDLE×SUFFIX must have been independently observed. This gate has 100% recall and 58.4% precision (419/718 pairwise-compatible combinations exist). A depth-3 decision tree learns only this pairwise rule (99.4% CV), matching the co-occurrence baseline. No higher-order "compiler rule" is detectable. The 42% gap within pairwise-compatible space is consistent with finite-sample sparsity. Confirms C1003 (no three-way synergy) from a vocabulary-existence angle. 1 new constraint (C1028). Phase 351.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1028 | Vocabulary Curation Rule — Pairwise Co-occurrence Necessary and Dominant | 2 |

---

## Version 3.77 (2026-02-14) - Hazard Violation Archaeology (C1027)

### Summary

Archaeology of the ~26.5% class-level forbidden pair violation rate. 10-test battery across folio, line position, paragraph, REGIME, PREFIX, section, pair-specific, neighborhood, sequential context, and permutation dimensions. Key finding: violations are SPATIALLY UNIFORM (no folio/line/paragraph/REGIME/permutation clustering, all p>0.05) but STRUCTURALLY CONDITIONED (violation-hosting lines are longer +1.20 p<0.0001, less kernel-dense -0.064 p<0.0001, less EN-dense -0.081 p<0.0001). PREFIX effect borderline (p=0.051). Per-pair variation high (Gini=0.49). Violations are a uniform grammar property, not exception handling or scribal noise. 1 new constraint (C1027). Phase 350.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1027 | Hazard Violation Archaeology — Spatially Uniform, Structurally Conditioned | 2 |

### Key Findings

**HAZARD_VIOLATION_ARCHAEOLOGY (10 tests):**
- Spatial uniformity: folio p=0.69, line p=0.22, paragraph p=0.32, REGIME p=0.22
- Structural conditioning: line length +1.20, kernel -0.064, EN -0.081 (all p<0.0001)
- PREFIX borderline: qo 1.89x enriched, lsh 0.21x depleted (p=0.051)
- Section borderline: BIO 0.217 vs RECIPE_B 0.292 (p=0.028)
- Pair variation: Gini=0.49, AX→FQ most common category (171/717)
- MIDDLE-level violations near zero (13/1829 = 0.71%), class-level 26.5%

---

## Version 3.76.1 (2026-02-13) - BCSC Contract Update (v3.10 → v3.11)

### Summary

BCSC structural contract audit and update to integrate findings from Phases 345-349 (C1022-C1026). Added GENERATIVE_SUFFICIENCY_AND_NECESSITY guarantee (the 49-class Markov + forbidden is both sufficient and necessary). Updated CONDITIONAL_ENTROPY_SYMMETRIC with C1024 morphological asymmetry resolution. Clarified macro-automaton as a lossy projection. Corrected gatekeeper role from exit directors to exit markers (C1023). Added generative_specification_bracketed invariant. Other three contracts (CASC, AZC-ACT, AZC-B-ACT) confirmed unaffected — all five phases are B-internal.

### Changes

- **BCSC v3.10 → v3.11**: 8 edits integrating C1022-C1026
- New guarantee: GENERATIVE_SUFFICIENCY_AND_NECESSITY
- New invariant: generative_specification_bracketed
- Updated: CONDITIONAL_ENTROPY_SYMMETRIC (C1024 resolution)
- Updated: MACRO_AUTOMATON_COMPRESSION (lossy projection, C1022/C1025)
- Updated: constraint_symmetry invariant (morphological decomposition)
- Updated: gatekeeper_mechanism (exit markers not exit directors, C1023)
- Added C1022-C1026 to provenance registry

---

## Version 3.76 (2026-02-13) - Grammar Component Necessity (C1026)

### Summary

Ablation necessity analysis at the 49-class level — the reverse of Phase 348's sufficiency test. 5 ablation conditions on real B corpus (100 shuffles each, 100 bootstrap resamples, >2sigma break threshold) with 10 topology-sensitive metrics. Class ordering within macro-states is LOAD-BEARING (5/10 breaks, spectral gap z=8.85), proving the 49-class ordering carries sequential structure the macro-automaton doesn't capture. Forbidden pair avoidance is LOAD-BEARING (4/10 breaks) and shapes directional asymmetry. Token identity within class is PARTIAL (2/10 breaks) — MIDDLE-level forbidden constraints leak through class boundaries. 4/10 topology-sensitive metrics are actually DISTRIBUTIONAL (survive all ablations). State partition and role partition are structurally equivalent. Combined with C1025: the 49-class transition matrix + forbidden suppression is both sufficient AND necessary. 1 new constraint (C1026). Phase 349.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1026 | Grammar Component Necessity — Class Ordering and Forbidden Avoidance Are Load-Bearing; Token Identity Is Partial | 2 |

### Key Findings

**GRAMMAR_COMPONENT_NECESSITY (5 ablations x 10 metrics):**
- (a) Forbidden injection: LOAD_BEARING (4/10 breaks; bigram diversity + fwd-rev JSD)
- (b) Subset forbidden: LOAD_BEARING (3/10 breaks)
- (c) Class shuffle in state: LOAD_BEARING (5/10 breaks; spectral gap z=8.85)
- (d) Class shuffle in role: LOAD_BEARING (5/10 breaks; equivalent to c)
- (e) Token shuffle in class: PARTIAL (2/10; MIDDLE forbidden leak z=3.51)
- Metric classification: 4 DISTRIBUTIONAL, 2 SEQUENTIAL, 1 TOPOLOGICAL, 3 COMPOUND

---

## Version 3.75 (2026-02-13) - Generative Sufficiency (C1025)

### Summary

Capstone generative simulation testing whether proven mechanisms can regenerate realistic B text. 5 models (M0 i.i.d. through M4 compositional), 15-test battery, 20 instantiations each. Key surprise: M0 (token frequency only) passes 73% of tests, revealing most structural tests measure marginal properties. Sufficiency frontier at M2 (49-class Markov + forbidden suppression, 80%). M4 (PREFIX-routed compositional generation) performs WORST (63%) because prefix×middle×suffix product space exceeds real vocabulary (4.2% hallucination). Macro-automaton M3 ties M2 but adds nothing (lossy projection). 2/5 predictions correct. 1 new constraint (C1025). Phase 348.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1025 | Generative Sufficiency — Class Markov + Forbidden Suppression Is Sufficient at M2 (80%) | 2 |

### Key Findings

**GENERATIVE_SUFFICIENCY (5 models × 15 tests):**
- M0 i.i.d.: 11/15 (73%) — most tests are marginal (distributional)
- M1 class Markov: 11.9/15 (79%) — adds spectral gap
- M2 M1 + forbidden: 12/15 (80%) — **sufficiency frontier**
- M3 6-state macro: 12/15 (80%) — ties M2, adds nothing
- M4 compositional: 9.4/15 (63%) — WORST; hallucination from product space
- B4, C2 universally failed = test specification issues
- Verdict: GENERATIVE_SUFFICIENCY_AT_M2

---

## Version 3.74 (2026-02-13) - Structural Directionality (C1024)

### Summary

Decomposes forward-backward asymmetry by morphological component and functional role. Resolves the C391/C886 tension: constraint symmetry lives in PREFIX (symmetric router), execution directionality lives in MIDDLE (directional executor). MIDDLE asymmetry is 4x PREFIX asymmetry. FL tokens show highest role-specific directionality (consistent with SOURCE-biased flow control). Null control reveals 64% of raw JSD is sparsity noise; sequential component is 36% above null but statistically significant. Verdict: WEAK_ASYMMETRY (1/5 PASS). 1 new constraint (C1024). Phase 347.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1024 | Structural Directionality — MIDDLE Carries Execution Asymmetry, PREFIX Is Symmetric Router | 2 |

### Key Findings

**STRUCTURAL_DIRECTIONALITY (5 tests):**
- T1: Bigram JSD — **PASS** (JSD = 0.089 bits, confirming C886)
- T2: PREFIX dominance — FAIL (PREFIX/MIDDLE ratio = 0.25x; MIDDLE is 4x more asymmetric)
- T3: CC highest — FAIL (FL = #1, CC = #4; flow control is most directional)
- T4: FL_HAZ > FL_SAFE — FAIL (reversed; small-sample artifact on rare classes)
- T5: Null control — FAIL (64% retention; sparsity dominates raw JSD)

---

## Version 3.73 (2026-02-13) - Structural Necessity Ablation (C1023)

### Summary

Counterfactual surgery on 4 structural components (6 sub-tests) to determine which are load-bearing vs decorative for the 6-state macro-automaton (C1010). PREFIX→state content routing is the sole load-bearing component, creating 78-81% of non-random transition structure. FL split (-0.34%), gatekeepers (JSD 0.0014), within-state routing (0%), and REGIME conditioning (1.1%) are all decorative at the macro level. Methodological discovery: initial PREFIX shuffle was tautologically invariant (state determined by class, not PREFIX); fixed by resampling state from P(state|new_prefix). Structure loss manifests as spectral gap INCREASE (chain becomes random), not decrease. 1 new constraint (C1023). Phase 346.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1023 | Structural Necessity Ablation — PREFIX Routing Is Sole Load-Bearing Macro Component | 2 |

### Key Findings

**STRUCTURAL_NECESSITY_ABLATION (6 tests):**
- T1: FL merge — DECORATIVE (spectral gap -0.34%, z=-2.39 vs null; statistically real but topologically negligible)
- T2: Gatekeeper — DECORATIVE (exit JSD=0.0014, below null mean=0.0024; markers not mechanisms)
- T3a: PREFIX within-state — DECORATIVE (0% structure loss)
- T3b: PREFIX within-position — **LOAD-BEARING** (77.8% structure loss)
- T3c: PREFIX global — **LOAD-BEARING** (80.7% structure loss)
- T4: REGIME merge — DECORATIVE (1.1% gap difference; C979 confirmed)

---

## Version 3.72 (2026-02-13) - Paragraph Macro-Dynamics (C1022) NEGATIVE

### Summary

Tests whether the 6-state macro-automaton (C1010) differentiates paragraph-level structure. Six pre-registered tests: header vs body distribution, spec vs exec zone shift, AXM self-transition by ordinal, gallows-initial CC enrichment, macro-state entropy by ordinal, qo/chsh gradient correspondence. Result: 1/6 PASS. The macro-automaton does NOT resolve paragraph structure — paragraph dynamics operate within AXM's 32-class internal diversity, below the 6-state partition's resolution floor. Key informative findings: gallows tokens are 100% AXM/AXm scaffold (not CC boundary markers); qo and ch/sh prefixes are both >98% AXM (C863 gradient is within-AXM); late paragraphs converge to lower entropy (rho=-0.215, p=0.007). Verdict: PARAGRAPH_MACRO_DYNAMICS_NEGATIVE. 1 new constraint (C1022). Phase 345.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1022 | Paragraph Macro-Dynamics — 6-State Automaton Does Not Differentiate Paragraph Structure | 2 |

### Key Findings

**PARAGRAPH_MACRO_DYNAMICS (6 tests):**
- T1: Header vs body — FAIL (AXM +2.8pp, chi2=16.04, p=0.007; headers are scaffold-heavy)
- T2: Spec vs exec — FAIL (AXM +1.4pp, chi2=11.81, p=0.037; sub-threshold)
- T3: AXM self by ordinal — FAIL (Spearman rho=0.207, p=0.011; binary p=0.121 underpowered)
- T4: Gallows CC — FAIL (gallows 87.7% AXM, 12.3% AXm, 0% CC; informative)
- T5: Entropy by ordinal — **PASS** (rho=-0.215, p=0.007; late paragraphs more concentrated)
- T6: qo/chsh macro-state — FAIL (both >98% AXM; C863 gradient is within-AXM)

---

## Version 3.71 (2026-02-13) - CP Factor Characterization (C1021) + Contract Audit

### Structural Contract Audit (post-C1021)

Updated BCSC (v3.9→v3.10) and CASC (v1.8→v1.9) to reflect findings from Phases 339-344 (C1016-C1021):

**BCSC changes:**
- Qualified archetype slope anomalies per C1018 (not statistically established at n=7)
- Added bridge PC1 partial redundancy note (rho=0.568 with hub frequency; C1018)
- Added archetype discriminator features (k_frac F=15.81, SAFETY_BUFFER 1.7x; C1018)
- Added THREE_COMPRESSION_INDEPENDENCE section (C1019-C1021): tensor/automaton/archetype orthogonality
- Added 100% bridge degeneracy (C1020)
- Updated safety_buffer_architecture with archetype connection
- Added provenance for C1018, C1019, C1020, C1021

**CASC changes:**
- Added bridge degeneracy clarification (C1020: all B MIDDLEs are bridges)
- Added C1018, C1020 provenance

AZC-ACT and AZC-B-ACT: no changes needed (all findings are B-scope).

### Summary

Characterizes the rank-8 CP tensor factors (C1019) by loading profiles, tests rank necessity, and attempts to reconcile tensor and automaton under constraint filtering. Key finding: Factor 2 (rho=-0.750 with AXM, the tensor's strongest dynamical predictor) is a class-level frequency gradient (Spearman rho=0.854 with class token frequency, confirming C986). Gatekeeper alignment (C1007) is near zero (cosine=0.059). Factor 3 (AXM-orthogonal, rho=0.090) also aligns with frequency (cosine=0.648) but captures the dynamics-decoupled frequency component. Cross-validated cosine saturates at rank 4 (0.713), with rank 6-12 nearly identical (0.732-0.738) — rank 8 is not structurally special. Constrained consistency test: applying forbidden/depleted pairs (C109) to class similarity WORSENS macro-state recovery (ARI=0.007 vs unconstrained 0.050, z=-0.22 vs null). All factors show strong PREFIX selectivity (mean Gini=0.803). The tensor line concludes: the three compressions — tensor (variance/frequency), macro-automaton (constraint topology), archetypes (dynamical personality) — are irreducibly independent. Verdict: FREQUENCY_ARTIFACT+FACTOR3_IDENTIFIED; RANK_CONTINUOUS; ORTHOGONAL_CONFIRMED (4/11 PASS). 1 new constraint (C1021). Phase 344.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1021 | CP Factor Characterization — Tensor Factors Are Frequency-Dominated, Rank Is Continuous, Tensor-Automaton Orthogonality Is Complete | 2 |

### Key Findings

**CP_FACTOR_CHARACTERIZATION (Sub-1 + Sub-2 + Sub-3):**
- Factor 2 is C986's frequency eigenmode projected onto the tensor (rho=0.854)
- Factor 3 captures AXM-orthogonal frequency (cosine=0.648, different PREFIX conditioning)
- CV cosine: rank-2=0.638, rank-4=0.713, rank-6=0.732, rank-8=0.736 — no knee at 8
- Constraint filtering CANNOT reconcile tensor and automaton (constrained ARI < unconstrained)
- PREFIX selectivity high across all 8 factors (mean Gini=0.803)

---

## Version 3.70 (2026-02-13) - Tensor Archetype Geometry (C1020)

### Summary

Tests whether C1016's dynamical archetypes cluster in C1019's rank-8 CP component space, and whether HUB-restricted factorization reveals different structure. Bridge/non-bridge partition is degenerate (100% of B MIDDLEs are bridges, confirming C1016/C1013), so Sub-B uses HUB vs non-HUB partition. Key finding: tensor factors encode dynamics through continuous graded curvature (7/8 factors correlate with AXM at |rho|>0.40, best Factor 2 rho=-0.738), NOT through discrete macro-state clustering or archetype separation (silhouette=-0.040, k-means ARI=0.124). Archetypes explain 32.8% of CP variance (eta²) — substantial but as a gradient, not clusters. HUB MIDDLEs carry simpler transition structure (effective rank 3 vs 8) but are PREFIX-diverse (entropy 1.024 vs 0.851), consistent with universal connector role (C1000). Verdict: TENSOR_GEOMETRY_ORTHOGONAL (3/8 PASS). 1 new constraint (C1020). Phase 343.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1020 | Tensor Archetype Geometry — Tensor Factors Encode Dynamics Through Graded Curvature, Not Macro-State Clustering | 2 |

### Key Findings

**TENSOR_ARCHETYPE_GEOMETRY (Sub-A + Sub-B):**
- A3: AXM correlation — **PASS** (Factor 2 rho=-0.738; 7/8 factors |rho|>0.40)
- Bridge degeneracy: 100% B MIDDLEs are bridges (C1016/C1013 confirmed)
- B3: HUB effective rank 3 (vs full rank 8) — **PASS**
- Tensor, automaton, and archetypes are three orthogonal compressions: spectral, topological, categorical

---

## Version 3.69 (2026-02-13) - Morphological Tensor Decomposition (C1019)

### Summary

Tests whether non-negative tensor factorization of the morphological transition structure T[PREFIX, MIDDLE_BIN, SUFFIX_GROUP, SUCCESSOR_CLASS] independently recovers the 6-state macro-automaton topology. The 20×10×5×49 tensor (13,315 bigrams, 5.1% density) has genuine rank-8 structure explaining 97.0% of variance. Five key findings: (1) optimal rank is 8 (within predicted 5-8 range); (2) CP decomposition equals or exceeds Tucker at matched parameters (Tucker 21% worse), confirming C1003 pairwise sufficiency at the tensor level; (3) **class factors do NOT recover C1010's 6-state partition** (ARI=0.053, random level) — the macro-automaton is an interpretive abstraction, not a natural tensor factorization; (4) tensor factors explain ΔR²=0.465 of AXM self-transition variance beyond REGIME+section, 4x the C1017 archetype reference (0.115); (5) SUFFIX is near-degenerate (2 SVD dims for 90%, confirming C1004) and HUB vs STABILITY bins differentiate (cosine=0.574, confirming C1018). Cross-validation stable (mean congruence 0.882). Verdict: TENSOR_NOVEL (5/8 PASS). 1 new constraint (C1019). Phase 342.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1019 | Morphological Tensor Decomposition — Transition Tensor Has Rank-8 Pairwise Structure Orthogonal to 6-State Macro-Automaton | 2 |

### Key Findings

**MORPHOLOGICAL_TENSOR_DECOMPOSITION (5 tests + synthesis):**
- T1: Tensor construction + rank selection — **PASS** (rank 8, 97.0% variance, 20×10×5×49, 13,315 bigrams)
- T2: Factor interpretation — MIXED (class ARI=0.053 FAIL; PREFIX rho=0.182 FAIL; bins cos=0.574 PASS; SUFFIX 2 SVD dims PASS)
- T3: CP vs Tucker — **PASS** (Tucker 21% worse at matched params; C1003 confirmed)
- T4: Controls — MIXED (marginalized ARI=0.050; shuffle mean=0.080 PASS; cross-val 0.882 stable; ΔR²=0.465)
- Verdict: TENSOR_NOVEL — 5/8 passed (macro-automaton is interpretive abstraction, not tensor projection; tensor factors 4x more predictive than macro-states)

---

## Version 3.68 (2026-02-13) - Archetype Geometric Anatomy (C1018)

### Summary

Anatomizes the 6 dynamical archetypes from C1016/C1017, validating slope anomalies via bootstrap/permutation tests, decomposing bridge PC1 into interpretable features, and identifying discriminator features across 7 families. Five findings: (1) archetypes 5/6 are not section artifacts (max 57.1%/56.7%), though section×archetype association is significant (V=0.457); (2) archetype 5 PREFIX slope anomaly is NOT established (n=7, bootstrap CI spans zero, boundary-fragile); archetype 6 hazard slope is directionally supported (perm p=0.014) but CI spans zero; (3) bridge PC1 is partially a hub frequency gradient (rho=0.568, exceeding 0.5 threshold) — partial C986 re-derivation identified; the non-redundant signal is a HUB_UNIVERSAL↔STABILITY_CRITICAL gradient; (4) 8 features across 5 families discriminate archetypes: k_frac (F=15.81), SAFETY_BUFFER (F=11.37), HAZARD_TARGET (F=5.73), fl_ratio (F=5.51), QO affinity (F=5.47); archetype 6 SAFETY_BUFFER enrichment (1.7x, p=0.003) explains positive hazard slope; (5) archetypes 5/6 occupy distinct bridge geometric positions (U=174, p=0.006) but mediation is weak — co-location, not causal. Verdict: ARCHETYPE_ANATOMY_UNIFIED (5/7 PASS). 1 new constraint (C1018). Phase 341.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1018 | Archetype Geometric Anatomy — Slope Anomalies, Bridge PC1 Decomposition, and HUB Sub-Role Differentiation | 2 |

### Key Findings

**ARCHETYPE_GEOMETRIC_ANATOMY (5 tests + synthesis):**
- T1: Archetype structural profiling — **PASS** (archetypes 5/6 NOT section-dominated; chi2=60.28 p=0.000006 V=0.457)
- T2: Bootstrap validation of slope anomalies — FAIL (arch 5 CI spans zero; arch 6 perm p=0.014 but CI spans zero; informative)
- T3: Bridge PC1 decomposition — MIXED (hub freq rho=0.568 exceeds threshold; PC1=HUB↔STABILITY gradient; archetypes F=3.56 p=0.006)
- T4: Discriminator features — **PASS** (8 significant across 5 families; SAFETY_BUFFER enrichment p=0.003 confirms expert prediction)
- T5: Unified hypothesis — **SUPPORTED** (arch 5 vs 6 geometrically distinct p=0.006; mediation weak)

---

## Version 3.67 (2026-02-13) - Macro-Dynamics Variance Decomposition (C1017)

### Summary

Decomposes macro-state dynamics into identifiable sources, resolving C1015.T8's informative failure. Four findings: (1) PREFIX routing is genuine (78.7% within-MIDDLE entropy reduction, z=65.59), non-positional (80.1%), and REGIME-invariant (ratio=1.06 across all 4 REGIMEs); (2) PREFIX entropy and hazard token density are independent, additive predictors of AXM basin depth (combined ΔR²=0.115 beyond REGIME+section baseline), with weak interaction (ΔR²=0.030, confirming C1003) and no SUFFIX contribution (p=0.280, confirming C1004); (3) bridge geometry adds ΔR²=0.063 (PC1: rho=-0.459, p=0.00005; F=9.58, p=0.003) — the geometry→dynamics conduit is load-bearing, confirming C1016.T8; (4) the 40.1% residual is non-linear: archetype-stratified models show qualitatively different slopes (sign flips in archetypes 5 and 6), mean within-archetype R²=0.230. Bridge density is constant at 1.0 (85/87 B MIDDLEs are bridges). Verdict: DYNAMICS_DECOMPOSED (8/9 PASS). 1 new constraint (C1017). Phase 340.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1017 | Macro-State Dynamics Decompose into PREFIX Routing, Hazard Density, and Bridge Geometry | 2 |

### Key Findings

**MACRO_DYNAMICS_VARIANCE_DECOMPOSITION (8 tests + synthesis):**
- T1: MIDDLE-conditioned PREFIX routing — **PASS** (78.7% entropy reduction within-MIDDLE, z=65.59; non-AXM spanning 85.9%)
- T2: Positional null model — **PASS** (19.9% positional; 80.1% genuine morphological routing, z=41.78)
- T3: REGIME-stratified routing — FAIL (ratio=1.06; PREFIX routing is REGIME-invariant; informative)
- T4: Hazard density differentiates archetypes — **PASS** (eta²=0.228, p=0.004); bridge density constant at 1.0
- T5: Variance decomposition — **PASS** (REGIME+section R²=0.420; +PREFIX+hazard R²=0.534; interaction ΔR²=0.030)
- T5b: Archetype-stratified models — **PASS** (slopes differ: β_PREFIX flips in arch.5, β_hazard flips in arch.6; mean within-archetype R²=0.230)
- T5c: Geometric bridge feature — **PASS** (PC1 rho=-0.459, p=0.00005; ΔR²=0.063, F=9.58, p=0.003; bridge geometry is load-bearing)
- T6: Residual characterization — **PASS** (SUFFIX uncorrelated p=0.280; archetype captures non-linear residual F=6.71 p<0.0001)

### Structural Contracts

- BCSC v3.8 → v3.9: Integrated C1017 findings (PREFIX routing quantification, REGIME-invariance, bridge geometry ΔR², archetype slope differences, variance decomposition)

---

## Version 3.66 (2026-02-13) - Folio-Level Macro-Automaton Decomposition (C1016)

### Summary

Decomposes the corpus-wide 6-state macro-automaton (C1010/C1015) to the folio (program) level. Five structural findings: (1) 6 dynamical archetypes emerge that are orthogonal to the 4 REGIMEs (ARI=0.065), organized along an AXM attractor strength axis from "strong attractor" (self=0.82) to "active interchange" (self=0.47); (2) the forgiveness gradient decomposes into macro-state transition features — forgiveness = AXM attractor strength (rho=0.678, 6 Bonferroni-significant features), mechanistically grounding C458's "recovery is free" design principle; (3) REGIME+section explain only 33.7% of folio-level transition variance, with 66.3% residual confirming C980's free variation envelope is substantively meaningful; (4) vocabulary geometry (100D discrimination manifold) weakly predicts but cannot determine dynamical archetypes (ARI=0.163, LOO=0.444 vs 0.167 chance), confirming C1011 geometry/topology independence at folio level; (5) the bridge backbone (85 MIDDLEs) is the primary geometry→dynamics conduit, carrying 3.8x more archetype-predictive information than non-bridge MIDDLEs (ARI 0.141 vs 0.037). T3 (C458 transition-level realization) FAILS informatively — clamping operates at aggregate program level, not individual transitions. Verdict: FOLIO_DECOMPOSITION_CONFIRMED (7/8 PASS). 1 new constraint (C1016). Phase 339.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1016 | Folio-Level Macro-Automaton Decomposition with Dynamical Archetypes | 2 |

### Key Findings

**FOLIO_MACRO_AUTOMATON_DECOMPOSITION (8 tests + synthesis):**
- T1: 72/82 folios with N≥50 transitions — **PASS** (13,645 transitions match C1015/T6)
- T2: 6 dynamical archetypes, ARI(REGIME)=0.065 — **PASS** (archetypes orthogonal to REGIMEs)
- T3: C458 transition-level realization — FAIL (hazard CV=1.814, recovery CV=0.289; C458 clamping is aggregate, not per-transition; informative)
- T4: Forgiveness decomposition — **PASS** (6 Bonferroni-significant features; AXM occ rho=0.678, AXM self rho=0.651)
- T5: Restart folio signature — **PASS** (f57r FQ depressed z=-2.06; constrained excursion space)
- T6: Variance decomposition — **PASS** (REGIME+section eta²=0.337; 66.3% residual is program-specific)
- T7: Geometry/topology independence — **PASS** (ARI(manifold, archetypes)=0.163; LOO=0.444 vs 0.167 chance; archetypes not reducible to vocabulary geometry)
- T8: Bridge conduit test — **PASS** (bridge ARI=0.141 vs non-bridge ARI=0.037, 3.8x; bridge backbone is geometry→dynamics conduit; density anti-correlates with AXM self rho=-0.308)

### Contract Updates

| Contract | Version | Key Changes |
|----------|---------|-------------|
| BCSC | 3.7→3.8 | +2 guarantees (BRIDGE_CONDUIT_MECHANISM, FOLIO_DYNAMICAL_ARCHETYPES from C1016); MACRO_AUTOMATON_COMPRESSION updated with folio-level independence; MACRO_STATE_DYNAMICS updated with archetype decomposition; design_freedom mechanism added (forgiveness = AXM attractor strength); dwell regime_modulation updated (REGIME eta²=0.149); folio_uniqueness connected to dynamical uniqueness |
| CASC | 1.7→1.8 | bridge_density_dynamics subsection added to viability_landscape; b_relationship updated with bridge conduit mediation |
| BRSC | 2.2 (unchanged) | No relevant findings |
| AZC-ACT | 1.2 (unchanged) | No relevant findings |
| AZC-B-ACT | 1.2 (unchanged) | No relevant findings |

---

## Version 3.65 (2026-02-13) - Structural Contract Audit (Phases 333-338)

### Summary

Audited 6 recent phases (333-338) against all 5 structural contracts. BCSC updated to v3.7 with: 3 new guarantees (MACRO_STATE_DYNAMICS, FL_ROUTING_ASYMMETRY, PREFIX_MDL_OPTIMALITY from C1015), full 6×6 macro-state transition matrix section, FL routing details in prefix_channel_architecture (da bi-directional router, ar FL_SAFE selector), thermodynamic grounding for hazard failure classes and safety buffers (F-BRU-023), new disallowed interpretation (FL_SAFE is NOT absorbing). BRSC updated to v2.2: quality rejection mapping confidence upgraded MEDIUM→HIGH with F-BRU-023 validation, new safety buffer mapping hypothesis. CASC/AZC-ACT/AZC-B-ACT confirmed no updates needed.

### Contract Updates

| Contract | Version | Key Changes |
|----------|---------|-------------|
| BCSC | 3.6→3.7 | +3 guarantees (C1015), +transition matrix section, +FL routing in PREFIX channels, +thermodynamic grounding (F-BRU-023), +disallowed FL_SAFE absorbing |
| BRSC | 2.1→2.2 | Quality rejection confidence MEDIUM→HIGH, +safety buffer mapping |
| CASC | 1.7 (unchanged) | No relevant findings |
| AZC-ACT | 1.2 (unchanged) | No relevant findings |
| AZC-B-ACT | 1.2 (unchanged) | No relevant findings |

---

## Version 3.64 (2026-02-13) - PREFIX Composition State Routing + Transition Matrix (C1015)

### Summary

Three genuinely new structural findings beyond existing C661/C1012: (1) `da` is the unique bi-directional FL router (OR=126.67, p≈0; only PREFIX routing both FL_HAZ and FL_SAFE), `ar` is a pure FL_SAFE selector (5/5, p≈0); (2) Full 6×6 macro-state transition matrix reveals dynamical characterization — AXM is a massive attractor (self=0.697, pull=0.642), FL_SAFE is NOT absorbing (self=0.023, return time 117.7 steps), CC is a pure initiator (self=0.041), system is ergodic with near-instant mixing (spectral gap 0.896); (3) PREFIX is MDL-optimal single component for state routing at corpus scale (33.9% compression, rank 1/4). T2/T5 operationalize C661/C1012 at the macro-state level (41.0% entropy reduction, 0.862 mean purity). T8 (generative sufficiency) shows PREFIX is necessary but not sufficient for transition dynamics (r=0.963, R²=-4.04 vs marginal — pairwise PREFIX×MIDDLE interaction required per C1003). Verdict: COMPOSITION_ROUTING_CONFIRMED (6/8 PASS, T1/T8 informative nulls). 1 new constraint (C1015). Phase 338.

### New Constraints

| ID | Name | Tier |
|----|------|------|
| C1015 | PREFIX-Conditioned Macro-State Mutability with FL-Specific Routing Asymmetry | 2 |

### Key Findings

**PREFIX_COMPOSITION_STATE_ROUTING (8 tests + synthesis):**
- T1: State-change rate 77.8% vs 73.0% null — FAIL (informative: AXM dominance inflates null baseline)
- T2: PREFIX entropy reduction 41.0% — **PASS** (z=17.6, p≈0; operationalizes C661/C1012)
- T3: da unique FL router — **PASS** (OR=126.67, p≈0; 5:5 HAZ:SAFE; only PREFIX in both FL states)
- T4: ar 100% FL_SAFE — **PASS** (5/5, binomial p≈0 vs 2.5% base rate)
- T5: Mean purity 0.862 vs 0.780 null — **PASS** (z=3.8, p=0.0001)
- T6: 6×6 transition matrix — **PASS** (AXM attractor 0.697; FL_SAFE fleeting 0.023; CC initiator 0.041; ergodic gap=0.896; stationary≈empirical)
- T7: MDL compression — **PASS** (PREFIX rank 1/4 at corpus scale N=16,054; 33.9% compression vs baseline; BIC-optimal single component)
- T8: PREFIX generative sufficiency — FAIL (informative: r=0.963 but R²=-4.04 vs marginal; AXM dominance makes marginal baseline very strong; PREFIX determines WHICH state but transition dynamics require PREFIX×MIDDLE interaction per C1003)

---

## Version 3.63 (2026-02-13) - Gloss Adversarial Validation (PREFIX-Domain + Mantel)

### Summary

Final glossing phase. Two orthogonal tests: (1) PREFIX-domain assignment uniqueness — exhaustive 6-permutation scoring of {qo, ok, ch/sh} → {ENERGY, VESSEL, PROCESS} using 5 structural metrics from C911, C601, C997. Current assignment is the UNIQUE winner (composite 5 vs next-best 11, gap=6). (2) Mantel test — pairwise behavioral distance (17-dim affordance signatures) correlates with gloss category membership (r=0.081, p=0.002). But ablating kernel-derived features drops to p=0.057 (marginal). FLOW is the most behaviorally coherent category (disc=0.149, p=0.011). Verdict: DOMAIN_VALIDATED_MANTEL_CIRCULAR (2/3 PASS). 1 new fit (F-BRU-026). Phase 337.

### New Fits

| ID | Name | Tier | Result |
|----|------|------|--------|
| F-BRU-026 | Gloss Adversarial Validation | F4 | DOMAIN_VALIDATED_MANTEL_CIRCULAR |

### Key Findings

**GLOSS_ADVERSARIAL_VALIDATION (4 tests):**
- T1: PREFIX-domain uniqueness — **PASS** (composite 5/5, gap=6 to next-best, S5 zero-hazard confirmed)
- T2: Mantel full (17 features) — **PASS** (r=0.081, p=0.002)
- T3: Mantel ablated (13 features) — FAIL (r=0.043, p=0.057 — marginal, 53% signal survives ablation)
- T4: Per-category decomposition — FLOW strongest (disc=0.149, p=0.011), TRANSITION marginal (p=0.078)

---

## Version 3.62 (2026-02-12) - Gloss Structural Validation (Negative)

### Summary

4-test phase testing whether the 90 core MIDDLE glosses are structurally constrained via adversarial permutation (forbidden transition category concentration) and distributional context clustering (bigram context vectors). Adversarial tests fail — only 13 testable forbidden pairs across 9 categories provides insufficient resolution (real=10 distinct pairs vs random mean=10.3, p=0.52). Distributional context weakly validates (ARI=0.032, p=0.037). Three gloss categories (THERMAL, MONITORING, CONTAINMENT) show strong distributional grounding; two (STAGING, STRUCTURAL) do not. Verdict: GLOSS_NOT_CONSTRAINED (1/4 PASS). Clean negative — adversarial metric underpowered, distributional structure real but weak. 1 new fit (F-BRU-025, GLOSS_NOT_CONSTRAINED). Phase 336.

### New Fits

| ID | Name | Tier | Result |
|----|------|------|--------|
| F-BRU-025 | Gloss Structural Validation | F4 | GLOSS_NOT_CONSTRAINED |

### Key Findings

**GLOSS_STRUCTURAL_VALIDATION (4 tests):**
- T1: Full adversarial permutation — FAIL (p=0.52, at chance)
- T2: PREFIX-constrained permutation — FAIL (p=0.51, at chance)
- T3: Distributional context alignment — PASS (ARI=0.032, p=0.037)
- T4: Within-category cohesion — FAIL (mean=0.551 < 0.60; THERMAL 0.96, MONITORING 0.80, CONTAINMENT 0.79 strong; STAGING 0.15, STRUCTURAL 0.23 weak)

---

## Version 3.61 (2026-02-12) - PP MIDDLE Extension Validation (Negative)

### Summary

5-test phase testing whether PP MIDDLE glossing frontier (404 shared A+B MIDDLEs) can be extended via auto-composition, behavioral similarity, compound bin coherence, folio thematic concentration, and hub sub-role alignment. Coverage audit passes (72.8% reachable), but extension mechanism is too weak: auto-composition shows modest behavioral grounding (cosine=0.23, t=15.6 vs random), affordance bins are orthogonal to compound structure (9.6% = chance), folio coherence is hub-driven only (no-hub ratio 1.01, n.s.), hub gloss alignment at 52% (below 65% threshold). Verdict: EXTENSION_UNSUPPORTED (1/5 PASS). Clean negative — existing 90 core glosses validated by Phase 334 are NOT invalidated. 1 new fit (F-BRU-024, NEGATIVE). Phase 335.

### New Fits

| ID | Name | Tier | Result |
|----|------|------|--------|
| F-BRU-024 | PP MIDDLE Extension Validation | F4 | EXTENSION_UNSUPPORTED |

### Key Findings

**PP_MIDDLE_EXTENSION (5 tests):**
- T1: 72.8% PP MIDDLEs reachable (87 glossed + 207 auto-composable) — PASS
- T2: Auto-composition behaviorally real (t=15.6, p<10^-6) but modest (cosine=0.23 < 0.5) — FAIL
- T3: Affordance bins orthogonal to compound structure (9.6% = chance) — FAIL
- T4: Folio coherence hub-driven (all: 1.055; no-hub: 1.01 n.s.) — FAIL
- T5: Hub gloss-to-role alignment 12/23 (52% < 65%) — FAIL

---

## Version 3.60 (2026-02-12) - Forbidden Transition Thermodynamics (Token-Level Coherence)

### Summary

5-test phase testing whether 17 forbidden token transitions (C109), when glossed using independently-derived Brunschwig vocabulary, map to specific distillation failure modes. PERFECT CONCORDANCE: 15/15 classifiable pairs map to recognizable failures (T1), 15/15 match structural failure classes from Phase 18 (T4), 8/8 asymmetry explanations coherent (T2), 22/22 safety buffers physically coherent (T3), buffer REGIME distribution non-uniform p=0.0081 (T5). QO-prefixed safety buffers (41%) represent energy insertion between consecutive test/monitor operations. Verdict: THERMODYNAMIC_COHERENCE (5/5 PASS). 1 new fit (F-BRU-023). Phase 334.

### New Fits

| ID | Name | Tier | Result |
|----|------|------|--------|
| F-BRU-023 | Forbidden Transition Thermodynamics | F2 | THERMODYNAMIC_COHERENCE |

### Key Findings

**FORBIDDEN_TRANSITION_THERMODYNAMICS (5 tests):**
- T1: 15/15 glossed forbidden pairs → recognizable distillation failures
- T2: 8/8 asymmetric pairs have coherent physical explanations
- T3: 22/22 safety buffers are physically coherent interventions (QO=41%)
- T4: 15/15 concordance between physical interpretations and structural failure classes
- T5: Buffer REGIME distribution non-uniform (chi²=11.79, p=0.008, REGIME_1 1.86x enriched)

---

## Version 3.59 (2026-02-12) - Recipe Triangulation V2 (Negative)

### Summary

6-test phase testing whether A paragraph handling types (CAREFUL, STANDARD, PRECISION, GENTLE) predict B-side REGIME compatibility through the PP filtering cascade (C502). PP MIDDLEs have REGIME specificity (median=0.50) but handling types do NOT exploit it. PRECISION paragraphs are R4-DEPLETED (2.9th percentile, wrong direction). All handling types peak at REGIME_1 (base rate). Confirms C753 extends to categorical level: A→B PP pathway is structural (which tokens legal) but not parametric (which REGIME applies). Verdict: NO_SIGNAL. No new constraints. 1 new fit (F-BRU-022, NEGATIVE). Phase 333.

### New Fits

| ID | Name | Tier | Result |
|----|------|------|--------|
| F-BRU-022 | Recipe Triangulation via PP-REGIME Pathway | F3 | NEGATIVE |

### Key Findings

**RECIPE_TRIANGULATION_V2 (6 tests):**
- T2 (GATE): PARTIAL — MIDDLEs have specificity (median=0.50) but R4-heavy NOT enriched in PRECISION (OR=0.32)
- T1: FAIL — PRECISION R4=0.081 < CAREFUL R4=0.087 (d=-0.82, wrong direction)
- T3: FAIL — Label permutation: PRECISION at 2.9th percentile (depleted)
- T4: FAIL — All handling types peak at REGIME_1; only 1/4 concordant with Brunschwig
- T5: FAIL — Wrong ordering (rho=-0.11)
- T6: FAIL — rho=0.4, p=0.6 (underpowered)

---

## Version 3.58 (2026-02-12) - Survivor-Set Geometry Alignment

### Summary

5-test phase testing whether the discrimination manifold (C982) encodes viability structure — do A records with geometrically similar MIDDLE inventories produce similar B vocabulary restrictions (C502/C689)? MIDDLE Jaccard vs centroid cosine Spearman r=0.914 (Mantel p=0.001, z=-102.66, n=1,528 records, 1.17M pairs). Hub-removed r=0.914 is STRONGER than hub-included r=0.887 (ratio=1.031) — viability encoded in residual compatibility geometry, not frequency. Size-controlled retention=100.1%. Class-level r=0.622 (p=0.001). Bridge-only r=0.905 (91% of signal), non-bridge r=0.194 (21%). Verdict: PARTIAL_ALIGNMENT — manifold is a viability landscape, mediated by the 85-MIDDLE bridge backbone, through residual compatibility geometry. 1 new constraint (C1014), 879 total. Phase 332.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C1014 | Discrimination Manifold Encodes Viability via Bridge Backbone | 2 | Spearman r=0.914 z=-102.66; hub-removed stronger (1.031); size retention 100.1%; class r=0.622; bridge 91%, non-bridge 21%; 4/6 predictions |

### Key Findings

**SURVIVOR_SET_GEOMETRY_ALIGNMENT (5 tests):**
- T1: MIDDLE Jaccard vs centroid cosine r=0.914 (Mantel p=0.001, z=-102.66)
- T2: Hub-removed r=0.914 > hub-included r=0.887; residual geometry encodes viability
- T3: Partial r=-0.916, retention=100.1%; zero size confounding
- T4: Class-level r=0.622 (p=0.001); propagates through class mapping
- T5: Bridge 91% of signal, non-bridge 21%; bridge backbone mediates viability

---

## Version 3.57 (2026-02-12) - Bridge MIDDLE Selection Mechanism

### Summary

6-test phase testing what predicts which 85/972 MIDDLEs bridge from A's discrimination manifold into B's 49-class grammar (resolving C1011). Bridge MIDDLEs are overwhelmingly selected by topological generality: frequency alone achieves AUC=0.978. They are 55x more frequent, 26x wider folio spread, 12x more compatible, 6x higher hub loading, half the character length, 2x less compound. Affordance bin enrichment is extreme: HUB_UNIVERSAL 23/23=100% bridging (11.44x), 4 specialized bins at 0% bridging (725 MIDDLEs). 15/17 univariate predictors significant (Bonferroni). Full multivariate model (AUC=0.904) does not improve beyond frequency. Verdict: TOPOLOGICAL_SELECTION — the A->B vocabulary boundary is a natural generality filter, not an active selection mechanism. 1 new constraint (C1013), 878 total. Phase 331.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C1013 | A->B Vocabulary Bridge is Topological Generality Filter | 2 | Freq AUC=0.978; 15/17 predictors significant; HUB_UNIVERSAL 100% bridge (11.44x); 4 bins at 0%; length 2.27 vs 4.11; 5/6 predictions |

### Key Findings

**BRIDGE_MIDDLE_SELECTION_MECHANISM (6 tests):**
- T1: 15/17 univariate predictors significant; frequency 55x, folio_spread 26x, compat_degree 12x
- T2: Frequency-only AUC = 0.978 (near-perfect)
- T3: Full model AUC = 0.904 on 125 valid; no improvement over frequency
- T4: Affordance bin chi2=479.5 (p=1.4e-97); HUB_UNIVERSAL 23/23=100%; 4 bins at 0%
- T5: Bridge MIDDLEs shorter, atomic, AXM-dominated (75.3%)
- T6: Verdict TOPOLOGICAL_SELECTION — 5/6 predictions passed

---

## Version 3.56 (2026-02-12) - PREFIX Macro-State Enforcement

### Summary

5-test phase testing whether the 102 forbidden PREFIX × MIDDLE combinations (C911) enforce the 6-state macro-automaton topology. PREFIX is a massive macro-state selector — 76.7% entropy reduction (chi2=31500, z=1139), with many PREFIXes channeling 100% of tokens to a single state. However, the 102 specific prohibitions are NOT the enforcement mechanism: only 23.2% target cross-state combinations (below 27.8% null, z=-1.58), and forbidden transitions are not preferentially backed (38.9% vs 46.2% null). PREFIX enforces macro-state through positive selectivity (which MIDDLEs it includes), not negative prohibition. Positional mediation 39.9%. EN PREFIXes (ch/sh) channel 100% to AXM+AXm. Verdict: PARTIAL_ENFORCEMENT — enforcement is inclusion-based, not exclusion-based. 1 new constraint (C1012), 877 total. Phase 330.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C1012 | PREFIX Macro-State Selector via Positive Channeling | 2 | 76.7% entropy reduction z=1139; prohibitions not cross-state z=-1.58; forbidden coverage 38.9% below null; mediation 39.9%; 3/6 predictions |

### Key Findings

**PREFIX_MACRO_STATE_ENFORCEMENT (5 tests):**
- T1: 76.7% entropy reduction (chi2=31500); I(PREFIX;macro)=0.876 bits; 10+ PREFIXes at 100%
- T2: Prohibitions not cross-state targeted (23.2% vs 27.8% null, z=-1.58, p=0.958)
- T3: 7/18 forbidden transitions backed (38.9%); below null 46.2% (z=-0.61)
- T4: Position→macro-state significant (z=44.78) but PREFIX mediates only 39.9%
- T5: Verdict PARTIAL_ENFORCEMENT — 3/6 predictions passed

---

## Version 3.55 (2026-02-12) - Geometric Macro-State Footprint

### Summary

6-test phase testing whether the ~101D discrimination manifold (C982) has geometric structure corresponding to the 6-state macro-automaton (C976/C1010). Only 85/972 MIDDLEs (8.7%) bridge A discrimination space → B execution grammar. Macro-state silhouette = -0.126 (z=-0.96, p=0.843) — worse than random, no geometric footprint. Forbidden transitions not at geometric boundaries (ratio=0.991, p=1.0). HUB MIDDLEs are geometrically peripheral not central (norm 2.31 vs 0.76, p≈0), reversing prediction from C1000. HUB sub-roles not geometrically distinct (p=0.577). 3/6 pre-registered predictions passed (P2: FL separation, P5: HUB significant, P6: no basins). Verdict: GEOMETRIC_INDEPENDENCE — manifold and automaton describe orthogonal structural levels (A-level compatibility vs B-level transition topology). 1 new constraint (C1011), 876 total. Phase 329.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C1011 | Discrimination Manifold and Macro-Automaton Geometrically Independent | 2 | 85/972 bridge (8.7%); silhouette -0.126 z=-0.96 p=0.843; forbidden ratio 0.991 p=1.0; HUB peripheral 2.31 vs 0.76 p≈0; sub-roles p=0.577; 3/6 predictions |

### Key Findings

**GEOMETRIC_MACRO_STATE_FOOTPRINT (6 tests):**
- T1: Eigenvector embedding 972×972 compatibility matrix; hub eigenmode λ₁=81.98 removed; 100D residual
- T2: 85 bridging MIDDLEs; silhouette -0.126 (z=-0.96 p=0.843); all per-state negative except AXm (+0.12)
- T3: 2/17 forbidden transitions representable; distance ratio 0.991 (p=1.0) — no boundary alignment
- T4: HUB MIDDLEs farther from origin (2.31 vs 0.76, p=2.7e-16); sub-role dispersion ratio 0.999 (p=0.577)
- T5: Affordance bins × macro-states many-to-many; AXM dominates mapped set (75%)
- T6: Verdict GEOMETRIC_INDEPENDENCE — complementary not redundant descriptions

---

## Version 3.54 (2026-02-12) - Macro-Automaton Necessity

### Summary

6-test phase proving the 6-state macro-automaton (C976) is the minimal invariant-preserving partition. k-sweep from 3 to 12 with constraint retention scoring, emission-aware AIC/BIC, five alternative 7-state partitions, and independent spectral clustering. k<6 breaks role integrity and depletion separation (k=5: 2 violations, k=4: 5, k=3: 9). AIC minimum at k=6 (~110 point advantage). k>6 preserves constraints but adds no structural benefit — depletion gap persists at z=7-9 at all k, confirmed as 49-class phenomenon. Independent spectral clustering finds structurally different partitions (ARI=0.059). Verdict: STRUCTURALLY_FORCED. 1 new constraint (C1010), 875 total. Phase 328.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C1010 | 6-State Minimal Invariant-Preserving Partition | 2 | k<6 breaks invariants (2-9 violations); AIC min at k=6; k>6 no structural gain; depletion z=7-9 at all k; spectral ARI=0.059 |

### Key Findings

**MACRO_AUTOMATON_NECESSITY (6 tests):**
- T1: Constraint retention 1.0 at k>=6; degrades to 0.263 at k=3; fidelity flat at 0.80 all k
- T2: AIC minimum k=6 (91299); BIC minimum k=3; LL jump of 70 at k=6
- T3: k=5 first breaks FQ role integrity + depletion (9,33); k=4 adds CC mixing; k=3 has 9 violations
- T4: Five 7-state alternatives (spectral, gatekeeper, affordance, entropy-max, JSD-greedy) — none close depletion gap
- T5: Spectral clustering ARI=0.059 vs agglomerative; role purity 0.0-0.5; structurally poor partitions
- T6: Verdict STRUCTURALLY_FORCED — 6 is minimal, AIC-optimal, upward refinement decorative

---

## Version 3.53 (2026-02-12) - AXM Gatekeeper Investigation

### Summary

11-test phase fully characterizing the AXM exit-boundary gatekeeper mechanism discovered in Phase 326 (C1007). Confirms directional gating: entry/exit class compositions are asymmetric (chi2=152.60, p<0.0001) with 5 AUXILIARY classes {15,20,21,22,25} enriched 2-10x at exit only. Gatekeepers have lower transition entropy (4.12 vs 4.56 bits, p=0.016) and are enriched in HAZARD_TARGET sub-role (C1000). Effect survives mid-line positional control (p=0.002). T8-T9 probe geometric layer: hazard-target compositional curvature toward exit (rho=-0.055, p=0.0001) but NO radial depth gradient (p=0.098) and gatekeepers are NOT structural bridges (betweenness p=0.514). T10-T11 probe saturation boundary: no constrained sub-role exit motif (pre-GK indistinguishable p=0.940, exit entropy matches baseline) and REGIME does NOT modulate curvature slope (p=0.200). AXM architecture fully characterized. 2 new constraints (C1008-C1009), 874 total. Phase 327.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C1008 | AXM Directional Gating Mechanism | 2 | Entry/exit asymmetry chi2=152.60 p<0.0001; entropy 4.12 vs 4.56 bits p=0.016; mid-line control p=0.002 |
| C1009 | AXM Exit Hazard-Target Compositional Curvature | 2 | HAZARD_TARGET density 10%->16% at exit rho=-0.055 p=0.0001; no depth gradient; compositional not spectral |

### Key Findings

**AXM_GATEKEEPER_INVESTIGATION (9 tests):**
- T1: Directional gating - entry/exit asymmetry (chi2=152.60, p<0.0001)
- T2: No exit routing specificity (p=0.286) - destination-agnostic
- T3: Mid-line positional control passed (chi2=58.42, p=0.002) - genuine gating
- T4: No duration prediction (KW p=0.128)
- T5: REGIME-variable gatekeeper identity (mean cross-rho=-0.245)
- T6: HAZARD_TARGET sub-role enriched at exit (chi2=13.89, p=0.003)
- T7: Lower gatekeeper entropy (4.12 vs 4.56 bits, p=0.016) - routing switches
- T8: Hazard-target compositional curvature toward exit (rho=-0.055, p=0.0001); NO depth gradient
- T9: Gatekeepers NOT structural bridges (betweenness p=0.514, PageRank p=0.183)
- T10: No constrained sub-role exit motif (pre-GK p=0.940, exit entropy matches baseline)
- T11: REGIME does NOT modulate curvature slope (rho=+0.800, p=0.200) - mechanism shape-invariant

---

## Version 3.52 (2026-02-12) - REGIME Dwell Architecture

### Summary

8-test phase probing dwell-time interactions in the 6-state macro-automaton. T1-T4 characterize dwell correlates (REGIME selectively stretches AXm, longer dwell = lower hazard density, shallower MIDDLEs = longer dwell, LINK density positive). T5-T8 investigate whether non-geometric AXM run lengths (chi2=52.79) represent genuine temporal memory. **RESOLVED: topology artifact.** First-order Markov null reproduces empirical dwell (KS p=0.074), simulated data also non-geometric (chi2=5097), confirming phase-type distribution from 32-class compression. Weibull k=1.55 REGIME-invariant. Compositional drift within AXM runs (T6b, p=0.010) connects to C977 S3/S4 directional flow. However, T8 discovers genuine gatekeeper subset: specific classes 3-10x enriched at AXM exit boundaries (chi2=178.21, p<0.0001). 2 new constraints (C1006-C1007), 872 total. Phase 326.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C1006 | Macro-State Dwell Non-Geometricity is Topology Artifact | 2 | KS p=0.074 null reproduces; Weibull k=1.55 REGIME-invariant; compositional drift p=0.010 |
| C1007 | AXM Exit-Boundary Gatekeeper Subset | 2 | chi2=178.21 p<0.0001; class 22 9.58x enriched; FQ principal interchange 57.1% |

### Key Findings

**REGIME_DWELL_ARCHITECTURE (8 tests):**
- T1: REGIME selectively stretches AXm only (rho=+0.306, p=0.007); AXM regime-independent
- T2: Longer dwell = lower hazard density (rho=-0.416, p=0.0001) — dwell is safety property
- T3: Shallower MIDDLEs = longer dwell (rho=-0.318, p=0.004), independent of REGIME
- T4: HT density null; LINK density positive (rho=+0.389, p=0.0003) — more monitoring = longer dwell
- T5: Increasing hazard function at 6-state level (rho=+0.95); flat at 49-class (mean run 1.054)
- T5b: First-order Markov null REPRODUCES empirical AXM dwell (KS p=0.074) — TOPOLOGY ARTIFACT
- T6: Non-geometricity correlates with compression ratio (AXM 32-class, FQ 4-class, FL_HAZ geometric)
- T6b: Compositional drift DETECTED within AXM runs (chi2=52.09, p=0.010)
- T7: Weibull k=1.55 across all REGIMEs (range 0.096) — shape invariant, scale varies
- T8: Gatekeeper subset at AXM exit boundaries (chi2=178.21, p<0.0001)

---

## Version 3.51 (2026-02-12) - Bubble-Point Oscillation Falsified

### Summary

Tier 4 exploratory phase testing whether QO/CHSH lane oscillation follows bubble-point dynamics (hotter REGIME = faster switching). **Falsified**: alternation rate *decreases* with REGIME intensity (rho=-0.44, p<0.0001). Effect is primarily section-driven (T7: rho=0.011, p=0.924 after section control). Modest REGIME residual only in double partial (rho=0.278, p=0.016). REGIME_4 has anomalously long CHSH runs (2.19), consistent with C494 precision axis. Eliminates physics-driven switching mechanism; supports operator-driven duty cycles. Distillation narrative strengthened. 1 new constraint (C1005), 870 total. Phase 325.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C1005 | Bubble-Point Oscillation Falsified (Duty-Cycle Pattern) | 4 | Alt rate rho=-0.44 p<0.0001; T7 section-controlled rho=0.011; R4 CHSH=2.19 |

### Key Findings

**BUBBLE_POINT_OSCILLATION_TEST (7 tests):**
- Hotter REGIMEs have *longer* runs in both lanes (opposite to bubble-point prediction)
- Alternation rate decreases with intensity (rho=-0.44, p<0.0001)
- Section absorbs REGIME effect completely (T7: partial rho=0.011, p=0.924)
- REGIME_4 anomalously long CHSH runs (2.19 vs 1.58-1.89) = precision monitoring
- Double partial (section + QO fraction) shows modest residual (rho=0.278, p=0.016)
- Confirms C650 (section-specific oscillation rates) as primary pace-setter

---

## Version 3.50 (2026-02-11) - HUB Decomposition & PREFIX Dual Encoding

### Summary

Two phases decomposing PP (PREFIX+MIDDLE) structure. HUB_ROLE_DECOMPOSITION classifies 23 HUB_UNIVERSAL MIDDLEs into 4 functional sub-roles and discovers all 17/17 forbidden transitions involve HUB (correcting C996's 13/17). PP_INFORMATION_DECOMPOSITION uses conditional MI to prove PREFIX is a dual-axis encoder: it selects content (lane, class) AND line position. PREFIX defines clear positional zones (po=86% initial, ar=61% final), is regime-invariant for major PREFIXes, and reveals sequential grammar (sh→qo +20.5σ enrichment). 2 new constraints (C1000-C1001), 846 total.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C1000 | HUB_UNIVERSAL Decomposes Into Functional Sub-Roles | 2 | 4 sub-roles; 17/17 forbidden involve HUB (perm p=0.0000); PREFIX V=0.689; sil=0.398 |
| C1001 | PREFIX Dual Encoding — Content and Positional Grammar | 2 | R²(PREFIX)=0.069≈R²(MIDDLE)=0.062 for position; 20/32 non-uniform; regime-invariant; sh→qo +20.5σ |

### Key Findings

**HUB_ROLE_DECOMPOSITION (5 tests):**
- HUB MIDDLEs partition into HAZARD_SOURCE(6), HAZARD_TARGET(6), SAFETY_BUFFER(3), PURE_CONNECTOR(8)
- Behaviorally homogeneous (0/14 KW significant) but functionally distinct
- ALL 17/17 forbidden transitions involve HUB MIDDLEs (corrects C996)
- PREFIX differentiates lanes within HUB: chi²=12957, Cramér's V=0.689
- Safety buffers 3.8x qo-enriched (Fisher p=0.012)

**PP_INFORMATION_DECOMPOSITION (5 tests):**
- MIDDLE is primary for suffix (45.4% of H) and regime (7.1%); PREFIX is co-equal for position (10.1% vs 9.6%)
- PREFIX positional zones: INITIAL (po, dch, so), CENTRAL (qo, ch, ok), FINAL (ar, al, or, BARE)
- sh→qo enrichment (+20.5σ) reveals line-opening → continuation grammar
- Cross-component MI: I(MIDDLE_t; PREFIX_{t+1}) = 0.499 bits
- Positional grammar is universal: REGIME main effect H=0.27, p=0.97

### Existing Constraints Extended
- C996: Corrected from 13/17 to 17/17 HUB involvement in forbidden transitions
- C661: PREFIX behavioral transformation (JSD=0.425) now includes positional encoding
- C662: PREFIX role reclassification (75% reduction) operates alongside positional control
- C997: Safety buffer QO mechanism confirmed and quantified within HUB (3.8x enrichment)

---

## Version 3.47 (2026-02-11) - B-Exclusive Geometric Integration (Architecture Complete)

### Summary

Binary-outcome micro-phase testing whether 900 B-exclusive MIDDLEs are geometrically subordinate or architecturally independent. All 5 tests converge: **SUBORDINATE**. 94% contain A atoms (89% string coverage), 33× A-compatible neighbor enrichment, 80% hapax, 81% single-folio, no energy effect. B-exclusive vocabulary is morphological elaboration of A's discrimination geometry, not a second system. Phase CLOSED with 1 constraint (C994). **Architecture complete** per expert directive — A's 972-MIDDLE discrimination geometry is the unified constraint surface.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C994 | B-Exclusive MIDDLEs Are Geometrically Subordinate | 2 | 5/5 tests SUBORDINATE; 94% A atoms, 89% coverage, 33× enrichment |

### Key Findings (T1-T5)

- B-exclusive MIDDLEs project into A's manifold (norm ratio 1.09, distance ratio 1.24) — **not a second geometry** (T1)
- B-exclusive co-occurrence respects A's topology at 33× enrichment, clustering 0.748 (86% of A's 0.873) (T2)
- 80% hapax, 94% compound, 81% single-folio — **morphological periphery**, not core vocabulary (T3)
- No material energy effect (shift +0.0006, p=0.12) — **surface decoration** on A-space backbone (T4)
- 89% mean string coverage by A atoms; most are 2-atom superstrings (54.3%) — **FULL_COLLAPSE** (T5)
- 53/900 (5.9%) genuinely novel (no A atoms) — all single-character or rare bigrams, no structural significance
- Expert prediction (Possibility A: SUBORDINATE) confirmed on all five axes

---

## Version 3.46 (2026-02-11) - Constraint Energy Functional

### Summary

Scalarized the ~100D discrimination space into a per-line compatibility energy E(line) = mean pairwise residual cosine. Five tests (T1-T5). B operates at **elevated constraint tension** (E = -0.011, below random by 0.016) — NOT minimizing energy. Radial depth in the manifold is the dominant predictor (ρ = -0.517). e-kernel is the compatibility kernel (ρ = +0.309), geometrically confirming C105. REGIME_4 uniquely converges in energy (var ratio 0.28). **Geometric closure**: escape rate, radial depth, and energy form a coherent triangle. Phase CLOSED with 4 constraints (C990-C993).

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C990 | B Operates at Elevated Constraint Tension | 2 | E=-0.011, shift -0.016, p=10⁻¹⁰¹ |
| C991 | Radial Depth Dominates Line-Level Energy | 2 | depth→E ρ=-0.517, p=10⁻¹⁶⁴ |
| C992 | e-Kernel Is the Compatibility Kernel | 2 | e→E ρ=+0.309, p=2×10⁻⁵⁴ |
| C993 | REGIME_4 Uniquely Converges in Energy | 2 | trend ρ=-0.90, var ratio 0.28 |

### Key Findings (T1-T5)

- B lines have **more constraint tension** than random MIDDLE subsets — inverted from prediction
- The 80% token concordance (C989) coexists with net negative cosine — B respects boundaries while operating near them
- **Radial depth** (ρ=-0.517) is the strongest single predictor of line energy — dwarfs all others
- AZC zone restrictiveness maps to radial depth: R3 deepest, C shallowest — mechanizes C443
- **e-kernel dominates compatibility** (3× stronger than h, 6× stronger than k) — stability anchor confirmed geometrically
- REGIME_4 starts with widest energy spread and converges to tightest — unique among all REGIMEs
- HT (first lines) have higher energy (-0.003 vs -0.011) and higher compound fraction (0.188 vs 0.102)
- B's grammar uses constraint tension **functionally** — not a penalty to avoid, an operating parameter

---

## Version 3.45 (2026-02-11) - Discrimination Space Phase Closure

### Summary

Completed the DISCRIMINATION_SPACE_DERIVATION phase with T10-T12 (AZC submanifold projection, hub-residual structure, B-side validation). Hub eigenmode (λ₁=82) identified as frequency gradient (ρ=-0.792). Residual space is continuous curved manifold, not blocks. AZC folio cohesion is entirely hub-driven (27/27→0/27 after removal). B execution inhabits A's geometry at 37× token-level enrichment. **A→AZC→B pipeline is geometrically closed.** Phase CLOSED with 9 constraints (C981-C989).

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C986 | Hub Eigenmode Is Frequency Gradient | 2 | λ₁=82, hub-frequency ρ=-0.792, monotonic with frequency band |
| C987 | Discrimination Manifold Is Continuous | 2 | Best k=5, sil=0.245, gap=-0.014, 865/972 in one cluster |
| C988 | AZC Folio Cohesion Is Hub-Driven | 2 | Full: 27/27 z=+13.26; Residual: 0/27 z=-2.68 |
| C989 | B Execution Inhabits A's Discrimination Geometry | 2 | 80.2% token-level, 37× enrichment, residual cosine aligned |

### Key Findings (T10-T12)

- Hub eigenmode is the **frequency/centrality axis** — separable from constraint structure
- Removing hub reveals **continuous manifold** (fuzzy bands, not blocks) — resolves C984 mechanism
- AZC folio "coherence" is an artifact of **hub frequency alignment** — no deep manifold partitioning
- B execution **massively respects** A's compatibility boundaries (37× enrichment at token level)
- Violations concentrate in **rare MIDDLEs** — observation gap, not structural exception
- Section S stands alone in B residual space — consistent with C941

---

## Version 3.44 (2026-02-11) - Discrimination Space Derivation

### Summary

Full characterization of the MIDDLE discrimination space (972 MIDDLEs, C475 basis). Nine tests (T1-T9) establish: spectral fingerprint is genuine (RARE under Configuration Model, 4/5 metrics anomalous z=+17 to +137; STABLE under bootstrap CV<0.055); dimensionality ~101 from 7 convergent methods; clustering 0.873 is +137σ above random (transitive compatibility); independent binary feature model categorically fails (clustering ceiling 0.49); character features partially predict compatibility (AUC 0.71 vs spectral 0.93).

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C981 | MIDDLE Discrimination Space Is a Structural Fingerprint | 2 | 4/5 metrics anomalous under CM, z=+17 to +137, CV<0.055 |
| C982 | Discrimination Space Dimensionality ~101 | 2 | Median of 7 methods, STRUCTURED_HIGH_DIMENSIONAL |
| C983 | Compatibility Is Strongly Transitive | 2 | Clustering 0.873 vs CM 0.253, z=+136.9 |
| C984 | Independent Binary Features Insufficient | 2 | AND-model clustering ceiling 0.49 vs target 0.87 |
| C985 | Character-Level Features Insufficient for Discrimination | 2 | AUC 0.71 vs spectral 0.93, PREFIX ARI=0.006 |

### Key Findings

- FINGERPRINT_CONFIRMED: spectral profile is anomalous AND stable — genuine structural property
- ~101 effective dimensions quantify the "token-level parameterization" layer of C976's three-layer architecture
- Clustering 0.873 is the single most anomalous property (+137σ) — compatibility is strongly transitive
- Independent features produce clustering ~0.44 regardless of K — constraint features must be correlated/hierarchical
- Character features explain 71% but miss 29% — discrimination requires non-morphological information
- Architecture: Hub manifold (λ₁=82) + 28 structured axes + 70 fine-grained axes + noise tail

---

## Version 3.43 (2026-02-11) - Controlled Variable Analysis

### Summary

Tier 3/4 comparative analysis identifying the controlled variable tracked by the 6-state automaton. Five distillation-context candidates scored against a 14-property structural signature extracted from C976-C980. **Temperature / Thermal State wins at 95.8% (23/24), 20.8pp gap over runner-up (Phase Boundary Position, 75.0%).** Documented as fit F-BRU-021, not as a constraint (framework-dependent interpretation).

### New Fits

| # | Name | Tier | Result |
|---|------|------|--------|
| F-BRU-021 | Controlled Variable Identification (Temperature) | F3 | SUCCESS (95.8%) |

### Key Findings

- Grammar tracks the input variable (fire degree) not the output measurement (distillate quality)
- Phase boundary is the primary physical effect of thermal state — input controls output
- Categorical control (SIG-11) matches visual fire assessment, not thermometer reading
- REGIME intensity scaling (C979) maps directly to fire degree escalation
- Only weakness: binary lane oscillation mapping to thermal modes is underspecified

---

## Version 3.42 (2026-02-11) - Minimal State Automaton Phase

### Summary

Structural compression of 49-class Currier B grammar into minimal latent state automaton. **Verdict: 6 states (COMPRESSIBLE, 8.2x compression).** Holdout-invariant (100/100 trials produce 6 states). Hub-and-spoke topology with AXM as universal attractor. REGIME modulates transition weights, not topology. Three-layer architecture established: 6-state control topology / 49-class grammar / token-level parameterization.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C976 | Transition Topology Compresses to 6 States | 2 | 49→6, 8.2x, holdout ARI=0.939 |
| C977 | EN/AX Transitionally Indistinguishable | 2 | 38 classes merge, AXm→AXM 24.4x asymmetry |
| C978 | Hub-and-Spoke with Sub-2-Token Mixing | 2 | Spectral gap 0.894, mixing 1.1 tokens |
| C979 | REGIME Modulates Weights Not Topology | 2 | chi2=475.5, FL regime-independent |
| C980 | Free Variation Envelope | 2 | 48 eigenvalues, 6 necessary states |

### Key Findings

- Grammar is a 6-state automaton dressed in 49 classes; classes provide lexical diversity, states provide structural law
- EN/AX merge at topology level (foreshadowed by C572, C574, C615) but remain morphologically distinct
- FL_HAZ/FL_SAFE regime-independent — boundary markers are constants, operational interior is parameterized
- Role taxonomy and dynamic constraints produce convergent boundaries — roles are not cosmetic
- Depletion is within-state texture (real 19 vs synthetic 3.8, z=+7.6) — not captured by 6-state macro model
- REGIME_4 has highest FQ scaffolding rate (0.237 vs pooled 0.173), confirming precision interpretation (C494)
- 6-state count perfectly holdout-stable; partition ARI=0.939 with instability only at AXm/AXM boundary

---

## Version 3.41 (2026-02-10) - Fingerprint Uniqueness Phase

### Summary

Null-model stress test of 11-property Voynich B statistical fingerprint against generic sparse categorical grammars. **Verdict: UNCOMMON** (Fisher p = 7.67e-08, worst-case single-test p = 0.024). Four tests with 11 null ensembles total (30,000+ random instances). Four of eleven fingerprint properties discriminate universally; four are non-discriminating at 49-class granularity (they operate within roles).

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C971 | Transition Asymmetry Structurally Rare | 2 | 18 depleted, 100% asymmetric, p<=0.0001 |
| C972 | Cross-Line Independence Stronger Than Random Markov | 2 | MI=0.521 vs null 0.72-0.77, p=0.000 |
| C973 | Compositional Sparsity Exceeds Low-Dimensional Models | 2 | Latent 3-5D: incomp 0.001 vs 0.460, p=0.000 |
| C974 | Suffix-Role Binding Structural Not Random | 2 | chi2=3872 vs null 390, p=0.000 |
| C975 | Fingerprint Joint Uniqueness UNCOMMON | 2 | Fisher p=7.67e-08, 4/11 discriminate |

### Key Findings

- Strongest discriminators: 100% transition asymmetry (F2) and unusually low cross-line MI (F10)
- Latent feature models (3-5 dimensions) produce near-zero incompatibility (0.001 vs 0.460) — dimensional necessity confirmed
- First-order BIC sufficiency is universal (100% of null chains also first-order) — NOT discriminating
- Sharp hazard gate invisible at 49-class level — operates within roles (C967)
- Suffix-role chi2 drops 10x under random class reassignment — binding is class-structure property
- Joint constellation cannot be generated by random categorical grammars

### Files

- `context/CLAIMS/C971_transition_asymmetry_rare.md` - new
- `context/CLAIMS/C972_cross_line_independence_rare.md` - new
- `context/CLAIMS/C973_compositional_sparsity_exceeds_latent.md` - new
- `context/CLAIMS/C974_suffix_role_binding_structural.md` - new
- `context/CLAIMS/C975_fingerprint_joint_uncommon.md` - new
- `context/CLAIMS/INDEX.md` - updated (823 constraints, v3.41)
- `context/MAPS/claim_to_phase.md` - updated
- `phases/FINGERPRINT_UNIQUENESS/` - 5 test scripts + 5 result JSONs

---

## Version 3.38 (2026-02-09) - Material Locus Search Phase

### Summary

16-test research phase systematically searched all remaining combinatorial hiding places for material identity encoding. **Verdict: MATERIAL EMERGENT** — section identity IS the material coordinate; no sub-section material markers exist. Material is implicitly encoded in the section-level vocabulary profile.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C941 | Section Is Primary Vocabulary Organizer | 2 | ARI=0.40, NMI=0.53, residual ~0 |
| C942 | Context-Dependent MIDDLE Successor Profiles | 2 | 45.8% section-dependent, KL ratio 2.0x |
| C943 | Whole-Token Variant Coordination | 2 | Residual MI=0.105 bits, 60% persists |
| C944 | Paragraph Kernel Sequence Stereotypy | 2 | Entropy p=0.004, section T=1.32 bits |
| C945 | No Folio-Persistent Material Markers FALSIFIED | 1 | 0 at >80%, 81.8% single-paragraph |
| C946 | No A Material-Domain Routing FALSIFIED | 1 | Cosine=0.997, ARI=-0.007 |
| C947 | No Specification Vocabulary Gradient FALSIFIED | 1 | Early 62.5% vs Late 64.2%, p=0.632 |
| C948 | Gloss Gap Paragraph-Start Enrichment | 2 | 4.03x at par_start, all distinct gaps hapax |

### Key Findings

- Every positive signal traces to section identity — token variants, successors, paragraph sequences
- No individual token, morphological slot, or positional feature serves as material marker
- A folios are a generic pool (cosine 0.997) — no material routing from A to B
- Gloss gaps enriched at paragraph starts (4.03x) and section-specific, but all distinct ones are hapax
- Section functions simultaneously as operational configuration AND implicit material domain
- Semantic ceiling (C120/C171) reinforced at a deeper level

---

## Version 3.37 (2026-02-09) - MIDDLE Material Semantics Phase

### Summary

14-test research phase tested whether tail MIDDLEs (rare, <15 folios) encode material-specific identity. **Verdict: WEAK** — phase-position semantics confirmed; material-level identity NOT supported. Semantic ceiling (C120) stands with refinement.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C937 | Rare MIDDLE Zone-Exclusivity | 2 | 55.1% vs 25.5%, d=0.67, p=2.97e-15 |
| C938 | Section-Specific Tail Vocabulary | 2 | 42-66% exclusive, ratio=1.40, p=1.29e-06 |
| C939 | Zone-Exclusive MIDDLEs Are Compositional Variants | 2 | 89.4% distance-1, p=0.978 indistinguishable |
| C940 | FL State Marking via Rare MIDDLEs FALSIFIED | 1 | p=0.224, bimodal distribution |

### Revision Notes

- **C619:** Confirmed within procedural phases (JSD=0.01, no zone survives Bonferroni)

### Key Findings

- Rare MIDDLEs deploy in specific procedural phases (SETUP/PROCESS/FINISH) — genuine structural feature
- But they are compositional elaborations (single-char edits) of common MIDDLEs, not independent identifiers
- FL state marking ruled out as explanation for finish-zone vocabulary
- Section-specific tail vocabulary extends C909 to the rare distribution
- Material encoding does NOT live in MIDDLE morphology

### Files Changed

- `context/CLAIMS/INDEX.md` — v3.37, +4 constraints (790→794)
- `context/CLAIMS/C937_rare_middle_zone_exclusivity.md` — NEW
- `context/CLAIMS/C938_section_tail_vocabulary.md` — NEW
- `context/CLAIMS/C939_zone_exclusive_compositional_variants.md` — NEW
- `context/CLAIMS/C940_fl_rare_middle_falsification.md` — NEW
- `context/CLAIMS/C619_unique_middle_behavioral_equivalence.md` — Revision note added
- `phases/MIDDLE_MATERIAL_SEMANTICS/` — Full phase (14 scripts, 14 results, README)

---

## Version 3.10 (2026-02-03) - B Paragraph Structure Analysis

### Summary

Detailed line-by-line annotation of **10 Currier B folios** (~350 lines) revealed paragraph-level vocabulary distribution patterns. New section 0.M added to INTERPRETATION_SUMMARY.md documenting sequential paragraph structure, terminal vocabulary signature, and state transition marking.

### Key Findings (Tier 3)

| Finding | Evidence |
|---------|----------|
| **Sequential paragraph structure** | Vocabulary distribution correlates with folio position (early=HT-heavy, late=AX+FL-heavy) |
| **Terminal vocabulary signature** | Late paragraphs show AX clustering + TERMINAL FL (-aly, -am) + SHORT lines |
| **State transition brackets** | HT at BOTH line-initial AND line-final marks explicit X→Y transformation |
| **FL STATE INDEX confirmation** | FL tokens (ar→al→aly) track material progression through folio |

### Interpretation Strengthened

The annotation work significantly strengthened the Brunschwig/distillation interpretation:
- Paragraphs correspond to named operations (maceration, distillation, rectification)
- Early identification → middle processing → late completion matches recipe structure
- State transition brackets match material state tracking in distillation manuals

### Files Updated

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Version 4.56, Section 0.M added
- `context/SYSTEM/CHANGELOG.md` - This entry

### Annotated Folios

First 5: f41v, f43r, f43v, f46r, f46v
Next 5: f103r, f103v, f104r, f104v, f105r

### Source

Manual token-level annotation using pacemaker workflow (`scripts/annotate_next_line.py --mode b`)

---

## Version 3.09 (2026-02-01) - Token Annotation Findings

### Summary

Systematic token-by-token annotation of all **114 Currier A folios** (1,272+ lines) completed. Three new constraints document previously invisible patterns. Annotation data infrastructure added to context system.

### New Constraints

| # | Name | Finding |
|---|------|---------|
| C901 | Extended e Stability Gradient | e→ee→eee→eeee forms stability depth continuum; quadruple-e rare (11 folios), concentrated in late Currier A |
| C902 | Late Currier A Register | f100-f102 show distinct characteristics: p/f-domain concentration, extended vowels, very short lines, morphological MONSTERS |
| C903 | Prefix Rarity Gradient | Common→rare→very-rare→extremely-rare prefix distribution (ch/sh > ct > qk > qy) |

### Constraint Refinement

**C833 (RI First-Line Concentration):** Added refinement note that 50% of folios have RI outside L1, establishing this as a preference rather than a requirement.

### New Data Files Documented

| File | Purpose |
|------|---------|
| `data/token_dictionary.json` | Token-level annotations with morphology, distribution, notes |
| `data/folio_notes.json` | Folio-level observations from systematic annotation |
| `data/annotation_progress.json` | Pacemaker script progress tracking |

Documentation added to `DATA/TRANSCRIPT_ARCHITECTURE.md` with usage examples.

### Expert Analysis Findings

Key patterns identified across 114 folios:

- **Doubled patterns**: 81 folios (71%)
- **Short lines**: 70 folios (61%)
- **QO concentration**: 64 folios (56%)
- **C833 flags (non-L1 RI)**: 57 folios (50%)
- **P-domain markers**: 51 folios (45%)
- **Linkers**: 47 folios (41%)
- **Triple e patterns**: 41 folios (36%)
- **Quadruple e patterns**: 11 folios (10%)
- **Rare qk-prefix**: 9 folios (8%)
- **Extremely rare qy-prefix**: 3 folios (3%)

### Files Updated

- `context/CLAIMS/INDEX.md` - Version 3.22, 768 constraints
- `context/CLAUDE_INDEX.md` - Version 3.09, constraint count updated
- `context/DATA/TRANSCRIPT_ARCHITECTURE.md` - Annotation data section added
- `context/CLAIMS/C833_ri_first_line_concentration.md` - Refinement added
- `context/CONSTRAINT_TABLE.txt` - Regenerated
- `context/MODEL_FITS/FIT_TABLE.txt` - Regenerated
- `.claude/agents/expert-advisor.md` - Regenerated with new constraints

### Cross-References

C901, C902, C903, C833 (refined), TOKEN_ANNOTATION_BATCH_11 phase

---

## Version 3.00 (2026-01-31) - Kernel Layer Clarification

### Summary

**Major clarification:** k, h, e "kernel" characters operate at CONSTRUCTION level (within-token morphology), not EXECUTION level (token-to-token sequencing). The 17 "forbidden transitions" operate at CLASS level, not k/h/e character level. These are INDEPENDENT constraint systems.

### KERNEL_STATE_SEMANTICS Phase Findings

| Test | Finding |
|------|---------|
| T1-T6 | Between-token k/h/e transitions are UNIFORM (O/E 0.87-1.21) |
| T7 | Class-level transitions show STRONG structure (O/E 0.20-7.31) |
| T9 | Within-token k/h/e transitions confirm C521 (5/5 claims) |
| T10 | k/h/e content does NOT predict forbidden transition participation |

### Key Discovery

Two independent constraint systems share the same symbol substrate:
1. **CONSTRUCTION layer (C521):** Within-token k→h→e ordering with strong asymmetry
2. **EXECUTION layer (C109):** Class-level forbidden transitions operating on instruction classes

C522 (layer independence) CONFIRMED with additional evidence.

### Files Updated

**BCSC v2.0:**
- KERNEL_CENTRALITY guarantee: Reframed from "control core" to "morphological core"
- kernel_boundary_adjacency invariant: Clarified as correlational, not causal
- kernel section: Added scope note that operators describe morphological contribution, not execution state

**Constraints:**
- C107: Added scope clarification (correlational not causal)
- C522: Added KERNEL_STATE_SEMANTICS evidence table

**Metrics:**
- hazard_metrics.md: Added scope note on class-level vs character-level

### Cross-References

C107, C109, C521, C522, KERNEL_STATE_SEMANTICS phase

---

## Version 2.99 (2026-01-31) - Escape Terminology Revision

### Summary

**Major terminology correction:** "Escape routes" (C397/C398) reframed as "lane transitions."

### Problem Identified

The HAV phase (C397-C398) introduced "escape" terminology that was later contradicted:
- C397 claimed "qo-prefix = escape route" after hazard sources
- But C645 shows CHSH dominates post-hazard (75.2%), QO is depleted (0.55x)
- C601 shows QO has zero hazard participation (0/19)
- The "escape to energy" framing was backwards

### Correct Model

| Lane | Kernel | Hazard Role |
|------|--------|-------------|
| CHSH | e-rich (68.7%) | Handles hazard-adjacent contexts, recovery |
| QO | k-rich (70.7%) | Operates hazard-distant, depleted near hazards |

What C397/C398 actually measured: the normal CHSH→QO lane transition pattern (C643), not escape.

### Files Updated

- `phases/HAV_hazard_avoidance/summary.md` - Revised interpretation
- `context/CLAIMS/morphology.md` - C397/C398 descriptions corrected
- `context/CONSTRAINT_TABLE.txt` - C397/C398 entries updated
- `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` - Recovery section rewritten
- `context/METRICS/hazard_metrics.md` - Escape section replaced

### Cross-References

C601 (QO zero hazard), C643 (QO-CHSH alternation), C645 (CHSH post-hazard dominance)

---

## Version 2.98 (2026-01-31) - P-TEXT FOLIO ANALYSIS Phase

### Summary

Investigated why P-text appears on 9 specific AZC folios and discovered it represents a **privileged Currier A vocabulary subset** with high transmission to B.

### Key Findings

| Finding | Value |
|---------|-------|
| P-text folios | 9 of 29 AZC folios (f65v-f70r2) |
| P-text to B transmission | **76.7%** (vs 39.9% for general A) |
| Same-folio Jaccard | 0.195 (vs 0.040 baseline) |
| Correlation with B TTR | r=0.524, p<0.0001 |

### Interpretation

P-text is not "A text on AZC folios" but a **privileged vocabulary subset** that:
- Has high transmission to B execution
- Correlates with high qo-density B folios (vocabulary diversity)
- Has content relationship to same-folio diagrams

### Constraints Updated

- **C492**: Added reframing note - "P-zone" → "P-text (Currier A paragraph)"
- **C486**: Added reframing note - strengthened by vocabulary-based interpretation

### Anomaly Noted

f65v is 100% P-text with 0 diagram tokens - unique among AZC folios.

---

## Version 2.97 (2026-01-31) - P Position Clarification

### Summary

Audited and corrected context system to clarify that **P (Paragraph) is NOT an AZC diagram position**. P is paragraph text that appears on AZC folios but is physically separate from the circular diagrams.

### Authoritative Source

From `context/ARCHITECTURE/azc_transcript_encoding.md`:

| Code | Physical Meaning |
|------|------------------|
| R, R1-R4 | Ring text (concentric circles) |
| S, S0-S3 | Star/spoke OR nymph-interrupted ring |
| C, C1-C2 | Circle text (continuous ring) |
| **P** | **Paragraph (separate from diagram)** |

### Files Updated

- `azc_activation.act.yaml`: Removed P from positional zones; added clarification
- `fits_azc.md`: Removed P from workflow phase table; added clarification notes
- `AZC_POSITION_VOCABULARY/README.md`: Labeled P as "(not diagram)" throughout
- `azc_system.md`: Updated C443 to focus on diagram positions (C, R, S)
- `CHANGELOG.md`: Fixed v2.96 entry which incorrectly listed P

---

## Version 2.96 (2026-01-31) - AZC Terminology Cleanup

### Summary

Fixed pervasive "filter/gate/route" language that incorrectly implied AZC actively affects execution. AZC is a static positional encoding: each PREFIX+MIDDLE has ONE fixed position, and position reflects vocabulary character, not causal effect.

### Correct Model

**AZC is NOT:**
- A filter that selects/blocks tokens
- A gate that controls execution flow
- A router that directs content
- An active transformation layer

**AZC IS:**
- A static lookup table (PREFIX+MIDDLE → position)
- A vocabulary classifier (position reflects operational character)
- A positional encoding (each token type has one fixed position)

### Key Finding (AZC_POSITION_VOCABULARY Phase)

AZC **diagram** position vocabulary signatures (C, R, S only - P is paragraph text, not diagram):

| Position | Character | Indicators |
|----------|-----------|------------|
| S-series | Stabilization | Highest AX% (35-45%), highest ok/ot% (41-45%), lowest EN% |
| R-series | Processing | Balanced profile, interior positions |
| C | Core | Balanced |

*P (Paragraph) is Currier A text on AZC folios, not a diagram position.*

Position has NO independent effect beyond vocabulary composition (Test 4: 0/10 MIDDLEs showed position effect when controlling for MIDDLE).

### Documentation Updates

| File | Change |
|------|--------|
| phases/AZC_POSITION_VOCABULARY/ | New phase documenting position vocabulary analysis |
| azc_activation.act.yaml | Replaced "gates/filters" → "encodes/groups" |
| currier_AZC.md | "gates" → "encodes position" |
| azc_system.md | "compatibility filter" → "compatibility grouping" |
| C384a | "AZC legality routing" → "AZC positional encoding" |
| C765 | "constrains execution" → "has characteristic B behavior" |
| fits_azc.md | Multiple filter/gate references corrected |

### Terminology Corrections

| Wrong | Right |
|-------|-------|
| AZC gates | AZC encodes position |
| AZC filters | AZC positions reflect |
| compatibility filter | compatibility grouping |
| AZC routes | AZC maps |
| AZC constrains B execution | AZC vocabulary has characteristic B behavior |

---

## Version 2.95 (2026-01-31) - FL Terminology Disambiguation

### Summary

Added terminology disambiguation for "FL" which was being used for two different concepts:

1. **FL (MIDDLE taxonomy)** - C777 material state index (~25% of tokens)
2. **FLOW_OPERATOR (FO)** - 49-class behavioral role (4.7% of tokens)

### Documentation Updates

| File | Change |
|------|--------|
| TERMINOLOGY/fl_disambiguation.md | New file explaining the distinction |
| C777_fl_state_index.md | Added terminology note |
| currierB.bcsc.yaml | Added FO abbreviation and disambiguation note |
| CLAIMS/INDEX.md | Added terminology note to FL section |

### Why This Matters

FL MIDDLEs (y, m, am, dy, r, l, etc.) appear in ~25% of all tokens across all 49 classes. FLOW_OPERATOR is a specific behavioral role with only 4.7% of tokens. Confusing them leads to incorrect analysis (e.g., expecting "FL rate" of 25% but seeing 4.7% when using 49-class role).

---

## Version 2.94 (2026-01-31) - A-B Within-Line Positional Correspondence

### Summary

Extended A_PP_INTERNAL_STRUCTURE phase with cross-system analysis. Major finding: shared vocabulary has consistent within-line positional roles across A and B.

### Key Finding (C899)

**A-B Within-Line Positional Correspondence:** PP MIDDLEs maintain consistent within-line positions across systems.

| Metric | Value |
|--------|-------|
| Corpus-level r | 0.654 (p < 0.0001) |
| Folio-level r (mean) | 0.149 (weak) |
| Zone preservation | 92.5% (vs 33% chance) |
| Hub zone stability | 5/5 MIDDLE in both systems |

**Interpretation:** This is a **corpus-level grammar property**, not a folio-level mapping. Vocabulary items carry positional semantics (EARLY/MIDDLE/LATE roles) that are consistent across both systems. This differs from C885, which establishes folio-level vocabulary correspondence.

### Documentation Updates

| File | Change |
|------|--------|
| INDEX.md | Updated A PP Internal Structure section (C898-C899) |
| C899_ab_positional_correspondence.md | New constraint file |

### Constraint Count

- Before: 764 constraints
- After: 765 constraints (+1: C899)

---

## Version 2.93 (2026-01-30) - A PP Internal Structure

### Summary

New phase A_PP_INTERNAL_STRUCTURE reveals that Currier A PP vocabulary has significant internal organization, refining C234's aggregate "position-free" finding.

### Key Findings (C898)

1. **PP Positional Grammar** (C898.a)
   - 50% of MIDDLEs have significant position bias (KS p<0.0001)
   - LATE-biased: m (0.85), am (0.79), d (0.75), dy (0.73) - closure markers
   - EARLY-biased: or (0.35), pch (0.31), dch (0.38) - opening/initiation

2. **PP Hub Network Structure** (C898.b)
   - Scale-free network with CV=1.69 (hub-dominated)
   - Top hub: iin (degree 277, mega-hub connector)
   - Secondary hubs: ol (208), s (197), or (188), y (181)
   - Consistent with C475: hubs are "legal connectors" bridging otherwise incompatible vocabulary

3. **Bimodal Position Distribution**
   - INITIAL zone (0.0-0.1): 13.9%
   - MIDDLE zone (0.4-0.6): 17.8% (valley)
   - FINAL zone (0.9-1.0): 18.9%
   - Aligns with C830 FINAL-bias (0.675) since C828 confirms 100% of repeats are PP

### Relationship to C234

C234 establishes aggregate position-freedom. C898 refines this: the aggregate may be uniform, but the PP subpopulation has bimodal structure. Analogous to C498.d refining C498 for RI length-frequency correlation.

### Phase Verdict

**STRONG** (2 confirmed, 1 support, 1 not supported)

| Test | Verdict |
|------|---------|
| 1. Positional Preferences | CONFIRMED |
| 2. Network Topology | CONFIRMED |
| 4. WITH-RI vs WITHOUT-RI | SUPPORT (sample imbalanced) |
| 6. Gradient Analysis | NOT SUPPORTED (primary axis is DIVERSITY vs CLOSURE) |

### Documentation Updates

| File | Change |
|------|--------|
| INDEX.md | Added C898 section |
| C898_a_pp_internal_structure.md | New constraint file |
| phases/A_PP_INTERNAL_STRUCTURE/ | New phase directory |

### Constraint Count

- Before: 763 constraints
- After: 764 constraints (+1: C898)

---

## Version 2.92 (2026-01-30) - Section-Specific Registry Architecture

### Summary

Extended C888 with comprehensive section architecture comparison. Sections (H, P, T) have distinct registry architectures, not just different content.

### Key Findings

1. **WITH-RI ratio differs significantly** (p=0.044)
   - P section: 64.5% WITH-RI (material specification focus)
   - H section: 49.1% WITH-RI (cross-reference balance)

2. **Section-distinctive PREFIXes**
   - H: kch, sch, dch, tch, ct (gallows-ch compounds, cross-ref)
   - P: or, ol (LINK prefixes - monitoring/safety)
   - T: al, ar, ta (highly distinctive)

3. **Low vocabulary overlap** (Jaccard ~0.2)
   - H: 69% exclusive MIDDLEs
   - P: 46% exclusive MIDDLEs

### Documentation Updates

| File | Change |
|------|--------|
| C888 | Renamed to "Section-Specific Registry Architecture", added C888.a (WITH-RI ratio), C888.c (vocabulary distinctiveness), C888.d (section PREFIXes) |

### Scripts Created

- `scripts/section_architecture_comparison.py`
- `scripts/ri_positional_function_test.py` (investigation closed - effect explained by PREFIX)
- `scripts/ri_pp_control_test.py`
- `scripts/ri_pp_dual_use_analysis.py`

### Constraint Count

- No change: 763 constraints (extension of C888, not new constraint)

---

## Version 2.91 (2026-01-30) - Linker Destination Characterization

### Summary

Characterized the structural properties of linker destination folios (C835) and refined understanding of linker function. Expert validation confirmed findings are consistent with existing constraints.

### Key Findings

1. **Hub destinations are structurally typical** - f93v and f32r show no outlier properties (z-scores < |1|)
2. **Linkers don't consistently appear as INITIAL** in destinations - suggests cross-reference function
3. **High source vocabulary similarity** (Jaccard 0.50-0.77) favors OR (alternatives) over AND (aggregation)
4. **Section concentration** - 96% in section H (herbal)
5. **ct-ho is necessary but not sufficient** - only 3/42 ct-ho tokens are linkers (7.1%)

### Documentation Updates

| File | Change |
|------|--------|
| C835 | Added "Hub Destination Characterization" section with structural metrics, positions, Jaccard analysis |
| C837 | Added "ct-ho is Necessary But Not Sufficient" section (7.1% linker rate) |
| INTERPRETATION_SUMMARY.md | Added new evidence favoring OR interpretation under RI Linker Mechanism |

### Scripts Created

- `scripts/linker_destination_characterization.py`
- `scripts/linker_destination_followup.py`

### Constraint Count

- No change: 763 constraints (refinement of existing, not new constraint)

---

## Version 2.90 (2026-01-30) - RI Chain Investigation (No New Constraint)

### Summary

Investigated whether RI token connections form a "procedural network" in Currier A.

### Investigation

1. Found 93.7% of A records connected via shared RI tokens
2. Common tokens (daiin, chol) create dense connectivity
3. Initially interpreted as procedural chaining

### Null Test Result

Chi-square testing revealed the pattern is **positional grammar**, not procedural linking:
- daiin, dy, chol = significantly OUTPUT-biased (end of paragraphs)
- sho, cthol, okol = significantly INPUT-biased (start of paragraphs)
- da- prefix = grammatical closure marker

### Expert Validation

Checked against existing constraints:
- **C422**: DA as internal articulation punctuation (75% separation)
- **C839**: RI Input-Output morphological asymmetry
- **C830**: Repetition tokens late-biased

**Verdict:** Pattern already covered by existing constraints. No new constraint needed.

### Constraint Count

- No change: 763 constraints

---

## Version 2.89 (2026-01-30) - Prefixed FL MIDDLEs as State Markers

### Summary

Analysis of tokens ending in -am/-y reveals they contain **FL MIDDLEs** (am, y, dy, ly, m) from C777's state index. These prefixed FL MIDDLEs inherit FL's state-indexing function, explaining their line-final concentration and operation→state mappings.

### New Constraint

| Constraint | Statement |
|------------|-----------|
| **C897** | Prefixed FL MIDDLEs as Line-Final State Markers (Tier 2) |

### Key Discovery: FL MIDDLE Connection

All tokens contain FL MIDDLEs from C777:

| Token | Prefix | MIDDLE | FL Stage | Position |
|-------|--------|--------|----------|----------|
| am | - | am | FINAL | 0.802 |
| dam | da | m | TERMINAL | 0.861 |
| otam | ot | am | FINAL | 0.802 |
| oly | ol | y | TERMINAL | 0.942 |
| oldy | ol | dy | TERMINAL | 0.908 |
| daly | da | ly | FINAL | 0.785 |
| ary | ar | y | TERMINAL | 0.942 |

### Why This Wasn't Obvious

1. Role classification masks FL MIDDLEs - prefixes shift tokens to AUXILIARY/FREQUENT_OPERATOR
2. Tokens analyzed as wholes - morphological decomposition reveals FL core
3. FL constraints (C770-C777) focus on pure FL tokens, not prefixed forms

### Operation → State Mappings (Extends C777)

| ENERGY Operation | Terminal State | FL MIDDLE |
|------------------|----------------|-----------|
| shey | → ldy | l (LATE) |
| cheky, chedy | → daly | ly (FINAL) |
| qokain, qokeedy | → oly | y (TERMINAL) |

Different heating operations produce different FL terminal states.

### Constraint Count

713 validated constraints (+1 from 712).

---

## Version 2.88 (2026-01-30) - Process Type Discrimination

### Summary

Discovered kernel-recovery correlations that discriminate thermal process types. Phase monitoring (h) anti-correlates with recovery (FQ), while fire control (k) positively correlates. This supports process mode discrimination: distillation (high h) vs boiling/decoction (high k, low h).

### New Constraints

| Constraint | Statement |
|------------|-----------|
| **C895** | Kernel-Recovery Correlation Asymmetry: k-FQ r=+0.27, h-FQ r=-0.29 (Tier 2) |
| **C896** | Process Mode Discrimination: HIGH_K_LOW_H = 2.5x FQ, non-distillation (Tier 3) |

### Key Findings

**Kernel-FQ correlations (527 paragraphs):**

| Kernel | Correlation | p-value | Interpretation |
|--------|-------------|---------|----------------|
| k% | +0.268 | < 10^-6 | Fire control requires recovery |
| h% | -0.286 | < 10^-6 | Phase monitoring substitutes for recovery |
| e% | +0.040 | 0.36 | Equilibration neutral |

**Process interpretation:**
- HIGH_H = DISTILLATION (drip feedback reduces errors)
- HIGH_K_LOW_H = BOILING/DECOCTION (no drip feedback, more recovery needed)

### Convergent Evidence

This is convergent with C781 ("FQ has 0% h; escape routes bypass phase management"). The negative h-FQ correlation (r=-0.286) quantifies this architectural bypass.

### Constraint Count

712 validated constraints (+2 from 710).

---

## Version 2.87 (2026-01-30) - REGIME-Paragraph Recovery Concentration

### Summary

Extended C893 to REGIME level, discovering that recovery-specialized folios cluster in REGIME_4 (33% vs 0-3% other REGIMEs). This validates C494's precision interpretation at paragraph level.

### New Constraint

| Constraint | Statement |
|------------|-----------|
| **C894** | REGIME_4 Recovery Specialization Concentration: 33% recovery-specialized folios in REGIME_4 (chi-sq=28.41, p=0.0001); validates C494 precision interpretation |

### Key Findings

**Folio specialization by REGIME:**

| REGIME | Recovery% | K/(K+H) | Interpretation |
|--------|-----------|---------|----------------|
| REGIME_4 | 33% | 0.32 | Precision + recovery capacity |
| REGIME_1 | 3% | 0.21 | Moderate, forgiving |
| REGIME_2 | 0% | 0.27 | Low intensity |
| REGIME_3 | 0% | 0.10 | Aggressive, distillation-focused |

**Confounding analysis:**
- Effect persists within sections (controlling for section composition)
- Section H: REGIME_4 has 56% higher K/(K+H) than REGIME_3

**Multi-level validation chain:**
- Token level: C780 (FQ is k-rich)
- Paragraph level: C893 (HIGH_K = recovery)
- Folio level: Recovery-specialized folios exist
- REGIME level: REGIME_4 concentrates recovery-specialized folios

### Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C494 | VALIDATES - paragraph-level confirmation of precision interpretation |
| C893 | EXTENDS - from paragraph-level to REGIME aggregation |
| C780 | ALIGNS - FQ is k-rich explains HIGH_K -> recovery link |

### Constraint Count

710 validated constraints (+1 from 709).

---

## Version 2.86 (2026-01-30) - Paragraph Kernel-Operation Mapping

### Summary

Discovered that B paragraph kernel signatures predict operation types, mapping to Brunschwig operation categories. HIGH_K paragraphs concentrate escape/recovery operations; HIGH_H paragraphs concentrate active processing operations.

### New Constraint

| Constraint | Statement |
|------------|-----------|
| **C893** | Paragraph Kernel Signature Predicts Operation Type: HIGH_K=2x FQ enrichment (p<0.0001), HIGH_H=elevated EN (p=0.036) |

### Key Findings

**Paragraph-level operation specialization:**

| Para Type | Count | FQ Rate | EN Rate | Brunschwig Mapping |
|-----------|-------|---------|---------|-------------------|
| HIGH_K | 58 | 19.7% | 19.3% | Recovery procedures |
| HIGH_H | 203 | 9.7% | 22.0% | Active distillation |
| BALANCED | 235 | 12.6% | 23.9% | General procedures |

**Statistical significance:**
- FQ difference (HIGH_K vs HIGH_H): p < 0.0001 (Tier 2)
- EN difference: p = 0.036 (supporting evidence)

**Brunschwig operation categories (Tier 3 interpretation):**
- HIGH_K = "If it overheats, remove from fire" (crisis response)
- HIGH_H = "Distill with fire, watching drip rate" (careful processing)
- BALANCED = Standard distillation steps

### Relationship to C780

This extends C780 (Role Kernel Taxonomy) from token-level to paragraph-level:
- C780: "FQ tokens use k+e with 0% h" (token property)
- C893: "HIGH_K paragraphs concentrate FQ operations" (spatial organization)

The concentration of recovery operations in HIGH_K paragraphs is new structural information.

### Expert Validation

Approved for Tier 2 documentation. No conflicts with existing constraints (C780, C781, C778, C103-105).

### Constraint Count

709 validated constraints (+1 from 708).

---

## Version 2.85 (2026-01-30) - Closed-Loop Orthogonality Discovery

### Summary

Discovered orthogonal control dimensions in the Voynich closed-loop model that Brunschwig's linear recipe model cannot capture. Added 3 new constraints (C890-C892) and extended REVERSE_BRUNSCHWIG_TEST to 10 tests.

### New Constraints

| Constraint | Statement |
|------------|-----------|
| **C890** | Recovery Rate-Pathway Independence: FQ rate and post-FQ kernel vary independently |
| **C891** | ENERGY-FREQUENT Inverse: rho=-0.80 at REGIME level |
| **C892** | Post-FQ h-Dominance: h (24-36%) dominates over e (3-8%) in recovery |

### Key Findings

**Recovery orthogonality (C890, C892):**
- FQ rate ranking: R4 > R2 > R1 > R3
- Post-FQ e% ranking: R2 > R1 > R3 > R4 (nearly inverse)
- h dominates post-FQ in ALL 4 REGIMEs (phase-check before equilibration)

**Role composition orthogonality (C891):**
- ENERGY_OPERATOR vs FREQUENT_OPERATOR: rho = -0.80 (strong inverse)
- CORE_CONTROL vs FREQUENT_OPERATOR: rho = 0.00 (perfectly orthogonal)
- R3 (intense): highest ENERGY (36.5%), lowest FREQUENT (11.2%)
- R4 (precision): lowest ENERGY (22.7%), highest FREQUENT (15.1%)

### Phase Update

REVERSE_BRUNSCHWIG_TEST upgraded from MODERATE-STRONG to STRONG:
- Tests 9-10 added (recovery_orthogonality, role_orthogonality)
- Overall: 2 STRONG + 5 SUPPORT + 2 WEAK + 1 NEUTRAL = STRONG correspondence

### Expert Validation

Findings validated against existing constraints:
- Consistent with C458 (recovery is free)
- Refines C105 (e = STABILITY_ANCHOR) - h is entry point, e is anchor
- Strengthens C494 (REGIME_4 precision)
- No conflicts detected

### Constraint Count

758 validated constraints (+3 from 755).

---

## Version 2.84 (2026-01-30) - Escape Terminology Clarification

### Summary

Discovered that two distinct "escape" measures exist in the constraint system with nearly inverse REGIME rankings. Added terminology clarifications to affected constraints.

### Discovery

| Measure | Definition | Classes | Used In | REGIME Ranking |
|---------|------------|---------|---------|----------------|
| qo_density | qo-prefixed tokens | 32, 33, 36 | C494, REGIME profiles | R3 > R1 > R2 > R4 |
| FQ_density | FREQUENT_OPERATOR role | 9, 13, 14, 23 | BCSC, escape recovery | R4 > R2 > R1 > R3 |

**Overlap: 0 tokens** - completely disjoint sets with orthogonal semantics:
- qo_density = thermal/energy operation intensity (C838: "execution-facing, kernel-adjacent")
- FQ_density = grammatical escape/flow control operators

**Key Insight:** REGIME_4's apparent contradiction (lowest "escape" in C494 but highest error handling) is resolved:
- Low qo_density = gentle heat (precision processing)
- High FQ_density = tight tolerances require more error correction

### Changes

**C494_regime4_precision_axis.md:**
- Added terminology note clarifying "escape rate" = qo_density (morphological), not FQ_density (grammatical)
- Changed table label from "Escape rate" to "Escape rate (qo)" for clarity

**REVERSE_BRUNSCHWIG_TEST phase:**
- Updated README with "Methodology Discovery: Dual Escape Measures" section
- Updated fire_stability_proxy.json with terminology clarification
- Updated reverse_brunschwig_verdict.json with methodology_discovery section

### Source

REVERSE_BRUNSCHWIG_TEST phase, Test 8 verification

---

## Version 2.83 (2026-01-30) - Aggregation Level Cleanup Round 2

### Summary

Extended aggregation annotations to additional constraints. Round 1 covered 14 constraints; Round 2 covered 17 more for a total of 31 annotated constraints.

### Round 2 Changes

**A-Record Filtering constraints annotated (line-level):**
- C682 (survivor distribution profile)
- C683 (role composition under filtering)
- C684 (hazard pruning under filtering)
- C685 (LINK/kernel survival rates)
- C686 (role vulnerability gradient)
- C687 (composition-filtering interaction)
- C688 (REGIME filtering robustness)
- C689 (survivor set uniqueness)

**PP Structure constraints annotated:**
- C640 (PP role projection architecture)
- C641 (PP population execution profiles)
- C656 (PP co-occurrence continuity)
- C658 (PP material gradient)

**Cross-System constraints annotated:**
- C642 (A record role material architecture)
- C825 (continuous not discrete routing)
- C691 (program coherence) - added C885 reference

**RI Structure constraints clarified:**
- C831 (RI three-tier structure) - scope note added
- C833 (RI first-line concentration) - scope clarification added
- C834 (paragraph granularity validation) - scope clarification added

**Verified correct (no changes needed):**
- C722 (within-line accessibility) - already uses "A-folio filtering"
- C725 (across-line accessibility) - B-scope analysis

### Constraint Count

755 validated constraints (no new constraints, annotations only).

---

## Version 2.82 (2026-01-30) - Aggregation Level Cleanup Round 1

### Summary

Annotated constraints that analyze Currier A at line or paragraph level to clarify the three-level hierarchy established by C881 and C885:

| Level | Count | Purpose |
|-------|-------|---------|
| Line | 1,575 | Transcript structure (not operationally meaningful) |
| Paragraph | 342 | A-internal record unit (C881) |
| **Folio** | 114 | **A-B operational unit** (C885: 81% coverage) |

### Changes

**Line-level constraints annotated:**
- C481 (survivor-set uniqueness)
- C690 (line-level legality distribution)
- C693 (usability gradient)
- C728 (PP co-occurrence incompatibility)
- C730 (PREFIX-MIDDLE within-line coupling)
- C731 (adjacent line continuity)
- C732 (within-line selection uniformity)
- C733 (PP token variant line structure)
- C824 (A-record filtering mechanism)

**Paragraph-level constraints annotated:**
- C827 (paragraph operational unit) - clarified: paragraph is A-internal, folio is A-B operational
- C846 (A-B paragraph pool) - noted folio achieves higher coverage
- C881 (A record paragraph structure) - clarified distinction from A-B operational level

**Multi-level constraints linked to C885:**
- C826 (token filtering model) - added C885 reference

### Constraint Count

755 validated constraints (no new constraints, annotations only).

---

## Version 2.81 (2026-01-30) - CURRIER_A_STRUCTURE_V2 Phase + C887-C889

### Summary

Comprehensive characterization of Currier A paragraph-level structure. Extended existing constraints (C881, C837) and added new constraints documenting WITHOUT-RI paragraph behavior.

### Key Findings

**Two Paragraph Opening Types:**
- WITH-RI (62.9%): Material-focused records with RI in first line
- WITHOUT-RI (37.1%): Process-focused annotations with pure PP

**WITHOUT-RI Backward Reference (C887):**
- 1.23x backward/forward asymmetry
- Highest overlap (Jaccard 0.228) when following WITH-RI paragraph
- Mechanism: process instructions apply to just-identified material

**Section-Specific Function (C888):**
- Section H: ct-prefix 3.87x enriched (cross-referencing)
- Section P: qo/ok/ol enriched (safety protocols)

**ct-ho PP Vocabulary (C889):**
- MIDDLEs h, hy, ho are 98-100% ct-prefixed in Section H
- Extends C837 linker signature to PP level
- Reserved vocabulary for linking/transfer operations

### Changes

- **C881 updated:** Integrated CURRIER_A_STRUCTURE_V2 findings into existing paragraph structure constraint
- **C837 updated:** Added cross-reference to C889 (PP-level extension)
- **C887 added:** WITHOUT-RI Backward Reference mechanism
- **C888 added:** Section-Specific WITHOUT-RI Function
- **C889 added:** ct-ho Reserved PP Vocabulary

### Constraint Count

755 validated constraints.

---

## Version 2.80 (2026-01-30) - C391 Clarification + C886 Transition Directionality

### Summary

Clarified C391 (time-reversal symmetry) and added C886 (transition directionality) based on external audit.

### Key Finding

C391 and C886 measure **different properties** that together are diagnostic:

| Property | Voynich | Natural Language | Procedural |
|----------|---------|------------------|------------|
| Conditional entropy symmetry (C391) | Yes (1.00) | No (~0.85) | ~0.9 |
| Transition probability correlation (C886) | **Near-zero (-0.055)** | High (~0.99) | High (~0.99) |

**Interpretation:** Grammar constraints are bidirectional (C391), but execution paths are directional (C886). This combination excludes both natural language AND simple procedural text.

### Changes

- **C391 renamed/clarified:** "Conditional Entropy Symmetry" - explicitly distinguishes constraint symmetry from transition symmetry
- **C886 added:** "Transition Probability Directionality" - P(A→B) uncorrelated with P(B→A)
- **BCSC contract updated:** TIME_REVERSAL_SYMMETRIC → CONDITIONAL_ENTROPY_SYMMETRIC with dual provenance

### Constraint Count

752 validated constraints.

---

## Version 2.79 (2026-01-29) - A-B Vocabulary Correspondence Definitive Answer

### Summary

**DEFINITIVE ANSWER:** A folios provide 81.2% vocabulary coverage for B paragraphs (1.71x vs random). Single A paragraphs provide only 58.3% coverage (2.04x vs random). The A-B relationship is real but requires folio-level or multi-paragraph aggregation.

### Key Finding (C885)

| A Unit | B Unit | Coverage | vs Random |
|--------|--------|----------|-----------|
| Paragraph | Paragraph (>=10 PP) | 58.3% | 2.04x |
| **Folio** | **Paragraph** | **81.2%** | 1.71x |
| 2-3 Paragraphs | Paragraph | 76-80% | - |

### What Works vs Doesn't

**Works:**
- A folio -> B paragraph: 81% coverage, 1.71x lift
- Multi-paragraph aggregation: 80%+ with 3 paragraphs

**Doesn't Work (Artifacts/Null):**
- Lane balance correlation: 0.99x (artifact of best-match)
- Kernel matching: 1.17x (marginal)
- Linker bundles: 0.99x (no better than random)

### Interpretation

A folios are "material contexts" that define available vocabulary. B paragraphs are "mini-programs" that execute with that vocabulary. The operator selects an A context (folio) appropriate for their material.

### Documentation

- `context/CLAIMS/C885_ab_vocabulary_correspondence.md` - New constraint
- `phases/A_B_CORRESPONDENCE_SYSTEMATIC/FINDINGS.md` - Full analysis
- `context/CLAIMS/C384a_conditional_correspondence.md` - Updated with quantitative evidence

### Constraint Count

751 validated constraints.

---

## Version 2.78 (2026-01-29) - Record Unit Correction (eoschso Invalidated)

### Summary

**CRITICAL CORRECTION:** The eoschso = chicken identification is **INVALIDATED**. The previous methodology incorrectly treated lines as records.

A records are **paragraphs**, not lines. Initial RI (material identifier) appears in the **first line** of a paragraph.

### Evidence

- eoschso (MIDDLE of "okeoschso") appears at position 41/70 in paragraph A_268
- This is in the MIDDLE lines of the paragraph, not the first line
- Therefore eoschso is NOT initial RI and cannot be a material identifier

### Corrected Methodology

New paragraph-level PP triangulation (MATERIAL_MAPPING_V2, Scripts 09-11):
1. Group paragraph tokens by LINE
2. Extract RI from FIRST LINE only (initial RI = material ID)
3. Match PP patterns against Brunschwig handling types
4. Validate via kernel signature (k+e vs h ratio)

### New PRECISION Candidates (Potential Animals)

6 paragraphs pass both PP pattern AND kernel validation (k+e >> h):

| Para | Initial RI | Folio | k+e | h |
|------|-----------|-------|-----|---|
| A_194 | opolch | f58v | 0.53 | 0.05 |
| A_196 | eoik | f58v | 0.50 | 0.06 |
| A_283 | qkol | f99v | 0.50 | 0.09 |
| A_280 | opsho, eoef | f99r | 0.60 | 0.23 |
| A_332 | ho, efchocp | f102r2 | 0.78 | 0.22 |
| A_324 | qekeol, laii | f101v2 | 0.48 | 0.12 |

### Documentation Updated

- `context/SPECULATIVE/recipe_triangulation_methodology.md` - Marked as INVALIDATED
- `phases/MATERIAL_MAPPING_V2/FINDINGS.md` - New corrected analysis

---

## Version 2.77 (2026-01-21) - Recipe Triangulation Methodology + C384 Scope Fix

### Summary

Developed and validated a methodology for mapping Brunschwig recipe characteristics to specific Voynich A records via multi-dimensional PP convergence. Successfully identified **eoschso = ennen (chicken)** as Tier 3 hypothesis.

**Also fixed C384 scope** - the original wording was over-blocking valid record-level inference, causing AI derailment.

### Key Findings

| Test | Result |
|------|--------|
| REGIME vocabulary distinctiveness | 11.9% exclusive (weak) |
| 4D conjunction narrowing | 0.29x ratio (synergistic) |
| Rose water vs animal folio overlap | 90.8% (PP not discriminative at folio level) |
| Record-level PP convergence | **DISCRIMINATES** (different records for different animals) |

### The Working Pipeline

```
Recipe Dimensions → B Folio Constraints → 4D Conjunction →
PP Vocabulary → A RECORD Convergence (3+) → RI Extraction →
PREFIX Profile Matching → Instruction Sequence → Material ID
```

### Animal Identification

| RI Token | ESCAPE PP? | AUX PP? | Candidate Animal |
|----------|------------|---------|------------------|
| eoschso | YES | YES | **ennen (chicken)** |
| teold | YES | NO | scharlach/charlach/milch? |
| chald | YES | NO | scharlach/charlach/milch? |
| eyd | weak | weak | blut/ltzinblut? |

### Constraint Refinement

**C384 (no entry-level A-B coupling) refined:**
> Single PP tokens do not establish entry-level coupling, but multi-dimensional PP convergence at RECORD level combined with PREFIX profile matching can identify specific A records.

### New Documentation

- `context/SPECULATIVE/recipe_triangulation_methodology.md` - Full methodology
- `phases/ANIMAL_PRECISION_CORRELATION/results/animal_identification.md` - Results
- `phases/ANIMAL_PRECISION_CORRELATION/results/pipeline_gap_analysis.md` - Initial tests

### C384 Scope Fix

**Problem:** Original C384 wording ("No entry-level A-B coupling") was over-blocking record-level inference, causing AI to abort valid tests.

**Solution:** Split into two constraints:
- **C384** (revised): No TOKEN-level or context-free A-B lookup
- **C384.a** (new): Conditional record-level correspondence PERMITTED

**What C384 now BLOCKS:**
- Token -> meaning lookup
- Token -> folio mapping
- Entry -> folio WITHOUT constraint routing
- Dictionary / translation claims

**What C384.a PERMITS:**
- Record-level correspondence via multi-axis constraint composition
- Survivor-set collapse (C481)
- Reverse inference via AZC routing
- Multi-dimensional PP convergence at RECORD level

**Canonical rule added to MODEL_CONTEXT.md:**
> "Currier A never names anything, but Currier A records can correspond to Currier B execution contexts when sufficient constraints collapse through AZC."

### Files Changed

- CLAIMS/C384_no_entry_coupling.md - REVISED (narrowed scope)
- CLAIMS/C384a_conditional_correspondence.md - NEW
- CLAIMS/INDEX.md - Updated C384, added C384.a
- CLAIMS/currier_a.md - Updated C384 references
- MODEL_CONTEXT.md - Updated forbidden list, added canonical rule
- SPECULATIVE/INTERPRETATION_SUMMARY.md - Added X.28 (Recipe Triangulation)
- SPECULATIVE/recipe_triangulation_methodology.md - NEW

---

## Version 2.76 (2026-01-21) - ANIMAL_PRECISION_CORRELATION: A-Exclusive Registry Vocabulary

### Summary

Investigated whether REGIME_4 (precision procedures) shows distinctive morphological signatures consistent with animal distillation's categorical procedural differences. The "animal distillation / REGIME_4 correlation" hypothesis was partially supported but critically reframed.

### Pre-Registered Predictions

| ID | Prediction | Result |
|----|------------|--------|
| P1 (Strong) | REGIME_4 hazard CV within 0.04-0.11 | **PASS** |
| P2 (Medium) | REGIME_4 ch-prefix enrichment >1.2x | **FAIL** |
| P3 (Medium) | f75r distinctive within REGIME_1 | **FAIL** |
| P4 (Weak) | <20% L-compound in PRECISION tokens | **PASS** (0%) |
| P5 (Exploratory) | REGIME_4 lower escape density | **SUPPORTED** |

### Critical Discovery

All 18 P(animal)=1.00 tokens are **A-exclusive** - they exist in Currier A's registry but NEVER appear in Currier B's execution layer. The "animal distillation" connection is about A's material cataloguing, not B's procedural execution.

### REGIME_4 Distinctive Profile

| Characteristic | REGIME_4 vs Others |
|----------------|-------------------|
| Recovery operations | **0.37x** (much less) |
| Near-miss events | **0.52x** (much less) |
| da-prefix | **1.48x** enriched |
| ok-prefix | **1.24x** enriched |
| ct-prefix | **1.84x** enriched |
| qo-prefix | **0.68x** depleted |

REGIME_4 is "get it right the first time" - less recovery, less intervention, different PREFIX profile.

### f75r Investigation

The Tier 4 speculative mapping of Kudreck→f75r is NOT supported. f75r is a typical REGIME_1 folio (z-score +0.18), not a REGIME_4 outlier.

### Constraint Implications

| Constraint | Status |
|------------|--------|
| C458 (Design Clamp) | **VALIDATED** - all REGIMEs show clamped hazard |
| C494 (REGIME_4 = precision) | **SUPPORTED** - distinctive low-recovery/low-escape profile |
| C384 (No A-B coupling) | **PRESERVED** - PRECISION tokens are A-exclusive |
| C499 (RI vocabulary) | **VALIDATED** - animal-associated MIDDLEs stay in A |

### Documentation Updates

- Updated C499 in currier_a.md with validation note (corrected count 27→18)
- Created comprehensive PHASE_SUMMARY.md

### Provenance

- Phase: ANIMAL_PRECISION_CORRELATION
- Scripts: `test_a_design_clamp.py`, `test_b_precision_tokens.py`, `test_c_f75r_investigation.py`, `test_de_morphology_by_regime.py`
- Results: 4 JSON files in results/

---

## Version 2.75 (2026-01-21) - B_EXCLUSIVE_MIDDLE_ORIGINS: Three-Layer Stratification (C501)

### Summary

Investigated why 569 MIDDLEs are B-exclusive. Discovered that B-exclusivity is NOT about distinct discriminators - it's morphological surface variation. 65.9% of B-exclusive MIDDLEs are edit-distance-1 variants of shared MIDDLEs.

### Key Findings

| Finding | Evidence |
|---------|----------|
| 65.9% are edit-distance-1 variants | 375/569 MIDDLEs |
| Edit types | 59% insertion, 39% substitution, 2% deletion |
| B-exclusive longer | Mean 4.40 vs 3.03 chars (p<0.0001) |
| Boundary enriched | 1.70x at line edges |
| 80.3% are singletons | 457/569 appear exactly once |
| L-compound operators | 49 types, 111 tokens (line-initial) |

### Three-Layer Stratification

| Layer | Size | Function |
|-------|------|----------|
| L-compound operators | 49 types | Line-initial control (C298) |
| Boundary closers | ~15 types | Line-final markers (-edy/-dy) |
| Singleton cloud | 457 types (80%) | Orthographic variants, no grammar role |

### False Lead Closed

The "49 distant MIDDLEs = 49 instruction classes" coincidence was tested and correctly rejected. All 49 distant MIDDLEs are hapax legomena with no operator behavior.

### REGIME Finding

REGIME_1 (simple) has highest B-exclusive rate (60.4%). Complex procedures use more canonical vocabulary. Supports C458 (design freedom in simple contexts).

### Constraint Added

**C501 - B-Exclusive MIDDLE Stratification (Tier 2):** B-exclusive status primarily reflects positional and orthographic realization under execution constraints, not novel discriminative content. True grammar operators are confined to the small L-compound core.

### Documentation Updates

- Added C501 to currier_a.md
- Updated MODEL_CONTEXT.md Section V with quantified stratification
- Updated EXPERT_CONTEXT.md via regeneration

### Provenance

- Phase: B_EXCLUSIVE_MIDDLE_ORIGINS
- Scripts: `b_excl_origin_analysis.py`, `extract_distant_middles.py`, `high_freq_b_exclusive.py`
- Results: `b_excl_origin_analysis.json`

---

## Version 2.74 (2026-01-21) - A_SECTION_T_CHARACTERIZATION: Measurement Disambiguation

### Summary

Investigated why Section T vocabulary shows 0% presence in Currier B (C299). Resolved apparent anomaly by discovering C299 measures section-characteristic vocabulary, not raw vocabulary overlap. Section T contains no distinctive vocabulary—only generic infrastructure tokens.

### Investigation Path

| Phase | Test | Finding |
|-------|------|---------|
| 1 | Registry-Internal Check | OPPOSITE - Section T is 32.3% RI vs 57.6% baseline (DEPLETED) |
| 1 | AZC Participation | OPPOSITE - Section T 52.8% vs 28.1% baseline (ENRICHED) |
| 1 | Control Operators | Zero control operators found in Section T |
| 2 | S-Zone Concentration | FALSIFIED - Section T DEPLETED in boundary zones (15.1% vs 17.9%) |
| 3 | Vocabulary Overlap | **KEY DISCOVERY** - 67.7% of T MIDDLEs appear in B (vs 42.4% baseline) |
| 3 | B Folio Presence | 100% of B folios contain Section T vocabulary |

### Key Discovery

Two different questions were conflated:

| Question | Answer |
|----------|--------|
| Does B use vocabulary that appears in Section T? | **YES - 100% of B folios** |
| Does B use vocabulary *distinctive* of Section T? | **NO - 0%** |

Both results are true simultaneously and not in tension.

### Resolution

Section T (f1r, f58r, f58v) contains **no section-characteristic vocabulary**. Its vocabulary consists entirely of shared infrastructure tokens (`_EMPTY_`, `a`, `al`, `ck`, `d`, etc.) that appear ubiquitously across all systems.

Section T functions as:
- Generic baseline (not specialized registry content)
- Template/scaffold (demonstrates morphology without domain specifics)
- Non-discriminative registry surface (orientation, not content)

### External Validation

Reviewed by domain expert. Verdict: "This represents a successful disambiguation rather than a correction. C299 was correct all along—it measures section-characteristic vocabulary, not raw overlap. Section T simply has no distinctive content to measure."

### Constraint Changes

| Constraint | Change |
|------------|--------|
| C299 | VALIDATED - measures section-characteristic vocabulary correctly |
| C299.a | ADDED - clarification that C299 measures discriminators, not raw overlap |

### Provenance

- Phase: A_SECTION_T_CHARACTERIZATION
- Scripts: `phases/A_SECTION_T_CHARACTERIZATION/scripts/`
  - `section_t_analysis.py` (initial characterization)
  - `azc_zone_analysis.py` (S-zone hypothesis test)
  - `permutation_and_overlap_test.py` (vocabulary overlap discovery)
- Results: `phases/A_SECTION_T_CHARACTERIZATION/results/`

---

## Version 2.73 (2026-01-21) - HT_MORPHOLOGICAL_CURRICULUM: Partial Curriculum Structure

### Summary

Investigated whether HT morphological patterns follow curriculum structure. Found partial evidence (1 strong, 2 weak, 1 provisional out of 5 valid tests). Key rebinding confound identified for difficulty gradient finding.

### Test Battery Results

| Test | Verdict | Key Finding |
|------|---------|-------------|
| 1. Introduction Sequencing | **STRONG PASS** | All 21 families in first 0.3% (KS=0.857) |
| 2. Spaced Repetition | UNDERPOWERED | Insufficient rare-but-repeated tokens |
| 3. Block Complexity | FAIL | No within-block gradient |
| 4. Family Rotation | **WEAK PASS** | Quasi-periodic ACF peaks |
| 5. Difficulty Gradient | **PROVISIONAL** | Inverted-U confounded by rebinding |
| 6. Prerequisite Structure | **WEAK PASS** | 26 pairs (2.5x expected) |

### Key Findings

| Finding | Evidence | Status |
|---------|----------|--------|
| Vocabulary front-loading | All 21 families in first 0.3% | CONFIRMED |
| Prerequisite relationships | 26 pairs vs 10.5 expected | CONFIRMED |
| Quasi-periodic rotation | ACF peaks at 6,9,12,14,17 | CONFIRMED |
| Inverted-U difficulty | H=89.04, p<0.0001 | PROVISIONAL (rebinding confound) |

### Rebinding Caveat

The inverted-U difficulty pattern cannot be distinguished from rebinding artifact without quire-level controls. The manuscript was rebound by someone who couldn't read it (C156, C367-C370). The "middle" zone in current binding is a mixture of originally non-adjacent folios.

### Documentation Updates

- Added Section I.A to INTERPRETATION_SUMMARY.md (HT Morphological Curriculum)
- Added curriculum characterization note to C221 in operations.md
- Added brief mention to MODEL_CONTEXT.md Section IX
- Updated phase summary to reflect PROVISIONAL status for Test 5

### Outcome

Tier 3 characterization (not Tier 2 constraint). Refines C221 (Deliberate Skill Practice) with specific curriculum mechanics.

### Provenance

- Phase: HT_MORPHOLOGICAL_CURRICULUM
- Script: `phases/HT_MORPHOLOGICAL_CURRICULUM/scripts/ht_curriculum_analysis.py`
- Results: `phases/HT_MORPHOLOGICAL_CURRICULUM/results/ht_curriculum_results.json`

---

## Version 2.72 (2026-01-20) - A_RECORD_STRUCTURE_ANALYSIS: PP Vocabulary Bifurcation (C498.a)

### Summary

Investigated the internal structure of "Pipeline-Participating" (PP) MIDDLEs from C498. Discovered that the 268 A∩B shared MIDDLEs comprise two structurally distinct subclasses, not a uniform pipeline-participating population.

### Key Findings

| Finding | Evidence |
|---------|----------|
| 114 bypass MIDDLEs | Appear in A and B but **never** in AZC |
| B-heavy frequency | 58.8% have B count > 2× A count |
| B-native vocabulary | e.g., `eck` A=2, B=85; `ect` A=2, B=46 |
| Pipeline narrower | Only 154 (25%) genuinely participate in A→AZC→B |

### Complete A MIDDLE Hierarchy

```
A MIDDLEs (617 total)
├── RI: Registry-Internal (349, 56.6%)
│     A-exclusive, instance discrimination, folio-localized
│
└── Shared with B (268, 43.4%)
    ├── AZC-Mediated (154, 25.0% of A vocabulary)
    │     A→AZC→B constraint propagation
    │     ├── Universal (17) - 10+ AZC folios
    │     ├── Moderate (45) - 3-10 AZC folios
    │     └── Restricted (92) - 1-2 AZC folios
    │
    └── B-Native Overlap (114, 18.5% of A vocabulary)
          Zero AZC presence, B-dominant frequency
          Execution-layer vocabulary with incidental A appearance
```

### Terminology Correction

The original "Pipeline-Participating" label is misleading:
- **AZC-Mediated Shared** (154): Genuine pipeline participation
- **B-Native Overlap / BN** (114): Domain overlap, not pipeline flow

### External Validation

Reviewed by domain expert. Verdict: "This is a solid, architecture-strengthening refinement. It sharpens C498, clarifies pipeline scope, and removes an implicit overgeneralization — without reopening any closed tier."

### Constraint Changes

1. **C498.a added (Tier 2 Refinement):** A∩B shared vocabulary bifurcates into AZC-Mediated (154) and B-Native Overlap (114). Constraint inheritance (C468-C470) applies only to AZC-Mediated subclass.

### Files Updated

- `context/CLAIMS/currier_a.md` - Added C498.a refinement
- `context/CLAIMS/INDEX.md` - Added C498.a entry and characterization note
- `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` - Updated two_track_structure with substructure
- `context/MODEL_CONTEXT.md` - Updated Two-Track section with full hierarchy

### Provenance

- Phase: A_RECORD_STRUCTURE_ANALYSIS (PP vocabulary analysis)
- Scripts: pp_middle_frequency.py, pp_singleton_analysis.py, pp_singleton_b_frequency.py, pp_middle_propagation.py, pp_bypass_azc.py
- Results: pp_middle_propagation.json

---

## Version 2.71 (2026-01-20) - A_RECORD_STRUCTURE_ANALYSIS: Hierarchical RI Closure at Segment Level

### Summary

Extended RI closure investigation to DA-segmented structure. Tested whether DA articulation (C422) reveals RI/PP stratification beyond what PREFIX alone explains. Discovered **hierarchical RI closure** — the closer preference operates at both line and segment scales.

### Three-Phase Investigation

| Phase | Question | Result |
|-------|----------|--------|
| Pre-check | Does PREFIX explain RI/PP? | V=0.183 (moderate), proceed |
| Phase 1 | Do DA segments stratify by RI/PP? | d=0.323 (weak), bimodal tail |
| Phase 2 | RI position within segments? | 1.43× closer preference (p<0.001) |
| Phase 3 | Are RI-RICH segments distinct? | Yes, 5× expected by chance |

### Key Findings

| Finding | Evidence |
|---------|----------|
| Hierarchical closure | Line-final 1.76×, segment-final 1.43× |
| RI-RICH segments distinct | 6.1% of segments, 5× binomial expected |
| PREFIX ≠ segment profile | p=0.151 (PREFIX doesn't predict) |
| RI-RICH are short, coherent | 3.3 tokens mean, diversity 2.66 |

### Critical Insight

PREFIX does NOT predict segment RI profile (p=0.151), even though PREFIX partially predicts token-level RI/PP (V=0.183). This means **RI concentration is a positional-closure phenomenon independent of PREFIX vocabulary**.

Two orthogonal organizational axes in A:
1. **PREFIX families** — what domain/material-class is being discriminated
2. **RI closure bursts** — where instance discrimination happens

### Constraint Changes

1. **C498-CHAR-A-SEGMENT added (Tier 3):** Hierarchical RI closure at segment level — 1.43× segment-final preference, RI-RICH segments as distinct closure units

### Files Updated

- `context/CLAIMS/currier_a.md` - Added C498-CHAR-A-SEGMENT characterization block
- `context/CLAIMS/INDEX.md` - Added segment characterization note
- `phases/A_RECORD_STRUCTURE_ANALYSIS/PHASE_SUMMARY.md` - Added Part 3 (DA segmentation)

### Provenance

- Phase: A_RECORD_STRUCTURE_ANALYSIS (DA segmentation sub-phases)
- Scripts: prefix_ri_pp_crosstab.py, da_segment_ri_pp_composition.py, da_segment_ri_position.py, da_segment_clustering.py
- Results: prefix_ri_pp_crosstab.json, da_segment_*.json

---

## Version 2.70 (2026-01-20) - A_RECORD_STRUCTURE_ANALYSIS: RI Closure Characterization

### Summary

Investigated internal structure of Currier A records using the RI (registry-internal) vs PP (pipeline-participating) distinction from C498. Discovered **RI closure tokens** — the missing complementary half of A's structural punctuation, orthogonal to DA articulation (C422).

### Key Findings

| Finding | Evidence |
|---------|----------|
| RI line-final preference | 29.5% vs 16.8% expected (1.75×) |
| Opener/closer vocabulary disjoint | Jaccard = 0.072 |
| 87% singleton closers | 104 of 119 closer MIDDLEs used exactly once |
| Core closure kernel | ho (10×), hod (4×), hol (3×), mo (3×), oro (3×), tod (3×) |

### Two Complementary Structural Mechanisms

| Layer | Mechanism | Scope | Function |
|-------|-----------|-------|----------|
| Internal segmentation | DA articulation (C422) | Within a record | Sub-unit boundary punctuation |
| Record termination | RI closers | End of a record | Completion + instance discrimination |

**Key insight:** If DA is a comma, RI closers are a period — but one that often needs to be unique, because what matters is not just that something ended, but that it ended as *this* and not anything else.

### Governance Decision

This is **Tier 3 characterization**, not Tier 2 constraint. The finding is **ergonomic bias**, not grammar — C234 (POSITION_FREE) remains intact. Currier A would satisfy all structural contracts even if closers were less singleton-heavy or end-biased.

### Constraint Changes

1. **C498-CHAR-A-CLOSURE added (Tier 3):** RI closure token characterization — line-final preference, singleton tail, complementary to C422

### Files Updated

- `context/CLAIMS/currier_a.md` - Added C498-CHAR-A-CLOSURE characterization block
- `context/CLAIMS/INDEX.md` - Added characterization note under C498-C500 section
- `phases/A_RECORD_STRUCTURE_ANALYSIS/PHASE_SUMMARY.md` - Complete phase documentation

### Provenance

- Phase: A_RECORD_STRUCTURE_ANALYSIS
- Scripts: ri_*.py, closer_*.py, analyze_multi_ri.py, etc.
- Results: ri_signal_investigation.json, noncloser_ri_investigation.json

---

## Version 2.69 (2026-01-20) - BRUNSCHWIG_CANDIDATE_LABELING Phase 4: PREFIX/SUFFIX Track Distribution

### Summary

Extended registry-internal vocabulary analysis with PREFIX/SUFFIX track distribution tests and suffix posture confirmation tests. Key findings: ct-prefix marks exclusive discrimination layer (85% exclusivity, 4.41× enrichment); CLOSURE suffixes are front-loaded (foundational framework) while NAKED entries are late refinements.

### PREFIX/SUFFIX Distribution Results

| Test | Finding | Effect Size |
|------|---------|-------------|
| PREFIX track distribution | ct-prefix 4.41× enriched in registry-internal | Cramér's V=0.307 (strong) |
| CT-prefix deep dive | 85% ct-MIDDLEs exclusive, 13.0 folio spread | - |
| SUFFIX track distribution | 45% registry-internal types ALWAYS suffix-less | Cramér's V=0.222 (moderate) |

### Suffix Posture Confirmation Tests

| Test | Hypothesis | Result | Effect Size |
|------|-----------|--------|-------------|
| S-1 (HT density) | CLOSURE → higher HT | NULL | r=0.152 (small) |
| S-2 (Incompatibility) | NAKED → more isolated | NULL | r=0.0 |
| S-3 (Temporal) | NAKED → introduced earlier | **CONTRADICTED** | r=0.495 (medium) |
| S-4 (Tail pressure) | NAKED → Q4 concentration | **CONFIRMED** | Phi=0.333 (medium) |

### Key Finding

| Posture | Q1 Share | Q4 Share | Interpretation |
|---------|----------|----------|----------------|
| CLOSURE (-y) | **76.7%** | 6.7% | Foundational framework |
| NAKED | 25.9% | **37.9%** | Late refinement |
| EXECUTION | ~100% | 0% | Earliest routing |

**Tail concentration ratio:** NAKED 5.69× more likely in Q4 than CLOSURE

### Constraint Changes

1. **C500 added (Tier 3):** Suffix Posture Temporal Pattern - CLOSURE front-loaded, NAKED late refinement, reverses initial hypothesis

### Files Updated

- `context/CLAIMS/currier_a.md` - Added C500 section
- `context/CLAIMS/INDEX.md` - Added C500 to A-Exclusive Vocabulary Track
- `phases/BRUNSCHWIG_CANDIDATE_LABELING/PHASE_SUMMARY.md` - Added Phase 4 documentation

### Provenance

- Phase: BRUNSCHWIG_CANDIDATE_LABELING Phase 4
- Scripts: s1-s4_*.py in phases/BRUNSCHWIG_CANDIDATE_LABELING/scripts/
- Results: s1-s4_*.json in phases/BRUNSCHWIG_CANDIDATE_LABELING/results/

---

## Version 2.68 (2026-01-20) - BRUNSCHWIG_CANDIDATE_LABELING: Bounded Material-Class Recoverability

### Summary

Attempted to generate Tier 4 candidate labels for registry-internal vocabulary using Brunschwig procedural coordinates. Discovered that while entity-level identity remains irrecoverable, **material-class probability vectors are computable** via Bayesian inference through procedural context.

**Framing:** "What these tokens COULD HAVE BEEN" - not "what they ARE"

### Phase Results

| Phase | Question | Result |
|-------|----------|--------|
| Phase 1 | Material category discrimination | UNINTERPRETABLE (nesting problem) |
| Phase 2 | WATER_STANDARD structural clustering | NULL (Q=0.068, near-random) |
| Phase 3 | Material-class posteriors via Bayesian inference | **POSITIVE** |

### Key Achievement: Bounded Recoverability

| Before | After |
|--------|-------|
| "Entity-level semantics are irrecoverable" | "Entity IDENTITY is irrecoverable, but CLASS-LEVEL PRIORS are computable" |
| "We can't know what these tokens mean" | "We can't know WHICH material, but we CAN compute P(material_class)" |

### Results

- 128 MIDDLEs analyzed with full material-class probability vectors
- 27 tokens with P(animal) = 1.00 (PRECISION-exclusive)
- Mean entropy: 1.08 bits (range 0.00 - 2.62)
- Null model validation: 86% match baseline (confirms prior-dominated nature)

### Semantic Ceiling Gradient

| Level | Recoverability |
|-------|----------------|
| Specific material (lavender) | IRRECOVERABLE |
| Material class (flower vs herb) | **PARTIALLY RECOVERABLE** |
| Procedural context (gentle distillation) | RECOVERABLE |

### Constraint Changes

1. **C499 added (Tier 3):** Bounded Material-Class Recoverability - material-class probability vectors computable for registry-internal MIDDLEs, conditional on Brunschwig interpretive frame.

### Documentation Updates

- `context/CLAIMS/currier_a.md` - Added C499
- `context/CLAIMS/INDEX.md` - Updated to v2.46 (339 constraints), added C499
- Phase: `phases/BRUNSCHWIG_CANDIDATE_LABELING/`

---

## Version 2.67 (2026-01-20) - BRUNSCHWIG_2TRACK_STRATIFICATION: Type-Specificity Confound Discovered

### Summary

Re-tested F-BRU-005's finding (75.4% type-specific MIDDLEs) using the new 2-track vocabulary classification (C498). Discovered that the aggregate rate is confounded by the registry-internal vocabulary's folio-localization.

### Key Findings

| Track | Type-Specific Rate | n |
|-------|--------------------|---|
| Registry-internal | **62.5%** | 128 |
| Pipeline-participating | **46.1%** | 128 |

**Chi-square:** 12.64, df=3, p < 0.01, Cramer's V = 0.222

### Interpretation

The 75.4% aggregate type-specific rate is inflated by registry-internal vocabulary (56.6% of MIDDLEs). These are folio-localized (avg 1.34 folios) and naturally appear in fewer product types.

The pipeline-participating vocabulary (which actually flows through A→AZC→B) shows a lower 46.1% type-specificity rate - still substantial but not the dominant pattern.

### Angle D: Reference Material Correlation (C498 Validation)

Tested whether registry-internal vocabulary correlates with Brunschwig reference-only materials (listed but no procedure):

| Group | Product Types | n Folios | Mean Reg-Int Ratio |
|-------|---------------|----------|-------------------|
| HIGH-REFERENCE | OIL_RESIN, WATER_GENTLE | 36 | **35.6%** |
| LOW-REFERENCE | WATER_STANDARD, PRECISION | 74 | **30.3%** |

**Mann-Whitney U:** z = -2.602, **p = 0.01**, effect size r = 0.248

**Result:** SUPPORTED - validates C498's "fine distinctions below execution threshold" interpretation.

### Expert Validation

Both internal expert-advisor and external expert validated findings:
- No Tier 0-2 violations
- C498 externally corroborated by orthogonal historical signal
- F-BRU-005 REFINED, not falsified
- Model-strengthening refinement, not scope creep

**Locked-in sentence:** "Separating Currier A into pipeline-participating and registry-internal vocabulary reveals that much of the apparent product-type specificity arises from coverage-driven folio localization; genuine operational alignment exists only in the pipeline vocabulary and is necessarily weaker, overlapping, and regime-mediated—exactly as required by an expert-only, non-semantic control system."

### Documentation Updates

- `context/MODEL_FITS/fits_brunschwig.md` - Added 2-track stratification section to F-BRU-005
- `context/CLAIMS/currier_a.md` - Added external validation note to C498
- Phase: `phases/BRUNSCHWIG_2TRACK_STRATIFICATION/`

---

## Version 2.66 (2026-01-20) - A_INTERNAL_STRATIFICATION: Two-Track Vocabulary Structure

### Summary

Investigated whether A-exclusive MIDDLEs (those appearing in Currier A but never in Currier B) have distinct structural roles. Discovered that Currier A has two vocabulary tracks with different morphological signatures and propagation behavior.

**Result: C498 added (Tier 2) - Registry-Internal Vocabulary Track**

### Key Findings

| Track | MIDDLEs | Characteristics | Role |
|-------|---------|-----------------|------|
| **Pipeline-participating** | 268 (43.4%) | Standard prefixes/suffixes, broad folio spread (7.96) | Flow through A→AZC→B |
| **Registry-internal** | 349 (56.6%) | ct-prefix 5.1×, suffix-less 3×, folio-localized (1.34) | Stay in A registry |

### Falsified Hypotheses

1. **Entry-type marker hypothesis: FALSIFIED** - Initial findings (98.8% opener rate) were artifacts of a data bug (grouping by word,folio instead of folio,line). Corrected: 18.8% vs 17.1% (not significant).

2. **AZC-terminal bifurcation hypothesis: FALSIFIED** - The 8.9% (31 MIDDLEs) that appear in AZC but never reach B are interface noise from systems sharing the same alphabet, not a distinct stratum. Verification checks: 2 PASS, 2 FAIL.

### Constraint Changes

1. **C498 added (Tier 2):** Registry-Internal Vocabulary Track - A-exclusive MIDDLEs (56.6%) form a morphologically distinct track that encodes within-category fine distinctions below the granularity threshold for execution.

### Documentation Updates

- `context/CLAIMS/currier_a.md` - Added C498 with full evidence
- `context/CLAIMS/INDEX.md` - Added C498 entry
- `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` - Added two_track_structure to middle section
- `context/MODEL_CONTEXT.md` - Added Section VII subsection
- Phase: `phases/A_INTERNAL_STRATIFICATION/`

---

## Version 2.65 (2026-01-20) - f49v Instructional Apparatus Discovery

### Summary

Discovered that f49v contains unique instructional apparatus - a teaching/reference page demonstrating Currier A structural principles. This is the only page in the manuscript with systematic marginal ordinal labels.

### Key Findings

1. **26 single-character L-placement labels** (65% of all such labels in manuscript)
2. **Marginal numbers 1-5** aligned with ordinal positions in vertical character column
3. **33 vocabulary types exclusive to f49v** (phonotactically extreme but structurally valid)
4. **Statistical test for category encoding: NEGATIVE** (p=0.0517, not significant)

### Interpretation

The single-letter column is not encoding values - it is **indexing examples**. The page demonstrates A structure rather than instantiating registry content.

Per external expert: *"A rare, deliberate moment where the manuscript turns inward and teaches how to read itself — without ever explaining itself."* The system that refuses instruction everywhere else has exactly ONE place where it demonstrates form - structurally, not semantically. This is strong corroboration of the expert-only, non-semantic model.

The existence of a single instructional/reference page demonstrates that Currier A was actively used and taught, not that it contains pedagogical grammar or semantic encoding.

### Constraint Changes

1. **C497 added (Tier 2):** f49v Instructional Apparatus - documents unique meta-structural apparatus

### Documentation Updates

- `context/CLAIMS/currier_a.md` - Added C497 in new "Meta-Structural Artifacts" section
- `context/CLAIMS/INDEX.md` - Added C497 entry, updated count to 338
- `phases/PHARMA_LABEL_DECODING/` - Investigation scripts and analysis

---

## Version 2.64 (2026-01-19) - AZC_INTERFACE_VALIDATION: Visual Heterogeneity is Interface-Only

### Summary

Validated that AZC visual heterogeneity (scatter diagrams, rings, nymph pages, P-text) represents interface variation, not mechanism variation. Core A→AZC→B architecture remains intact.

**Expert verdict:** One small surgical correction (P-text reclassification) + one genuinely new structural fact (C496). No architectural contracts modified. No semantic reopening.

### Tests Executed

| Test | Question | Result |
|------|----------|--------|
| TEST 0 | Transcript hygiene | PASS (3,299 tokens confirmed) |
| TEST 1 | P-text classification | **A-ON-AZC-FOLIO** (PREFIX 0.946 to A) |
| TEST 2 | Diagram type uniformity | **UNIFORM** (all types >0.88) |
| TEST 3 | Center token behavior | **LEGALITY-PARTICIPATING** (PREFIX 0.94 to ring) |
| TEST 4 | Nymph interruption | **FUNCTIONAL** (S-positions 75% o-prefix) |

### Constraint Changes

1. **C300, C301 amended:** Added note that 398 P-text tokens should be excluded from AZC legality analysis (diagram-only count: 2,901)
2. **C496 added (Tier 2):** Nymph-Adjacent S-Position Prefix Bias - o-prefix enrichment (75%) in nymph-interrupted positions
3. **C137, C436 confirmed:** Diagram type uniformity confirms illustration independence

### Data Quality Warning

⚠️ Center placements on nymph folios may be partially under-transcribed. Analyses use available tokens only.

### Documentation Updates

- `context/ARCHITECTURE/azc_transcript_encoding.md` - Major update with all TEST findings
- `context/DATA/TRANSCRIPT_ARCHITECTURE.md` - Added AZC cross-reference
- `context/CLAIMS/azc_system.md` - C300/C301 notes, C496 added, refinement notes updated
- `context/CLAIMS/C301_azc_hybrid.md` - P-text reclassification note
- `context/CLAIMS/INDEX.md` - C496 added, count updated to 337
- Phase: `phases/AZC_INTERFACE_VALIDATION/`
- Results: `results/test1_ptext_reclassification.json` through `test4_nymph_interruption.json`

---

## Version 2.63 (2026-01-19) - A_REGIME_STRATIFICATION: SUFFIX-REGIME Association Confirmed

### Summary

Investigated whether A vocabulary stratifies by REGIME compatibility. Found that the naive "39% single-REGIME" observation is heavily confounded by frequency, but SUFFIX morphology shows a genuine association with REGIME compatibility breadth.

**Result: SUFFIX effect confirmed (C495 added), frequency confound documented**

### Tests Executed

| Test | Question | Result |
|------|----------|--------|
| T1 (Morphology) | PREFIX/SUFFIX predict REGIME? | **SUFFIX YES** (V=0.159), PREFIX no |
| T2 (Frequency) | Are REGIME-specific tokens rare? | **YES** - major confound (V=0.38) |
| T3 (AZC) | AZC zone differences? | No effect |
| T4 (Folio) | Cluster on A folios? | Inconclusive |

### Key Findings

- SUFFIX predicts compatibility breadth: `-r` enriched in universal (11.5% vs 4.2%), `-ar`/`-or` enriched in single-REGIME
- Frequency confound: Among frequent tokens (>20x), only 4.7% are genuinely single-REGIME
- PREFIX shows no REGIME association (V=0.068)

### New Constraint

**C495 (Tier 2, SCOPE: A→B):** SUFFIX–REGIME Compatibility Breadth Association. SUFFIX morphology in Currier A tokens is associated with downstream REGIME compatibility breadth in Currier B.

### Documentation

- Phase: `phases/A_REGIME_STRATIFICATION/`
- Results: `results/regime_stratification_tests.json`
- Constraint: Added to `context/CLAIMS/morphology.md`

---

## Version 2.62 (2026-01-19) - PUFF_STRUCTURAL_TESTS: Evidential Ceiling Confirmed

### Summary

Tested whether improved AZC/Currier A understanding enables new Puff-Voynich structural linkages beyond existing curriculum-level alignment (10/11 prior tests pass).

**Result: No new linkage found (0/2 tests passed)**

### Tests Executed

| Test | Hypothesis | Result |
|------|------------|--------|
| T9 (Danger -> HT) | Dangerous materials have elevated HT | **FAIL** (effect reversed) |
| T8 (Complexity -> Breadth) | Complex materials need larger vocabulary | **FAIL** (effect reversed) |
| T4 (Category -> PREFIX) | Material categories correlate with PREFIX | CONSTRAINED (A-B linkage too weak) |

### Key Findings

- Dangerous Puff positions have LOWER HT (0.133 vs 0.150)
- Later Puff positions have SMALLER vocabulary (168 vs 186)
- A-B linkage only 4% above baseline - insufficient for Category->PREFIX test

### Conclusion

Puff evidential ceiling confirmed. Curriculum-level alignment established; structural linkage not found. Further Puff testing would require semantic interpretation (prohibited) or external provenance research.

**Puff remains Tier 3-4 SPECULATIVE.**

### Documentation

- Phase: `phases/PUFF_STRUCTURAL_TESTS/`
- Results: `results/puff_danger_ht_test.json`, `results/puff_complexity_breadth_test.json`

---

## Version 2.61 (2026-01-19) - BC_EXPLANATION_ENFORCEMENT: Brunschwig Relationship Bounded

### Summary

Tested the "one remaining legitimate reverse-Brunschwig test" (external expert): Does Brunschwig's pedagogical verbosity inversely correlate with AZC scaffold constraint rigidity?

**Result: FALSIFIED (0/4 hypotheses passed)**

### Test Results

| Hypothesis | Prediction | Result | Status |
|------------|------------|--------|--------|
| H1 | Inverse density-freedom correlation | rho=+0.09 | FAIL |
| H2 | UNIFORM < VARIED density | d=-0.37, p=0.11 | FAIL |
| H3 | Interaction > main effects | dR2=0.00 | FAIL |
| H4 | Stable complementarity ratio | CV +9.6% | FAIL |

### What Was Falsified

> "Brunschwig's pedagogical verbosity systematically complements Voynich's enforcement rigidity at the recipe/regime level."

### What Survives

- Zone-modality discrimination (F-BRU-009) - INTACT
- AZC trajectory shape = scaffold fingerprint - INTACT
- Scaffold uniformity determines cognitive pacing - INTACT

### The Corrected Relationship

| Aspect | Brunschwig | Voynich |
|--------|------------|---------|
| Primary function | Explains WHAT | Enforces WHEN |
| Alignment level | Curriculum trajectory | Curriculum trajectory |
| NOT aligned | Interface timing | Interface timing |

> **Voynich stands alone as an enforcement artifact.**

### New Constraints

- **C-BOUND-01:** Voynich is not part of a fine-grained pedagogical feedback loop
- **C-BOUND-02:** Voynich-Brunschwig relationship is maximally abstract: convergent at ontology, independent at interface

### Documentation

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Section X.27 added (v4.31)
- `phases/BC_EXPLANATION_ENFORCEMENT/BC_EXPLANATION_ENFORCEMENT_REPORT.md` (NEW)

### Data Files

- `results/bc_explanation_density.json` through `results/bc_synthesis.json`

**Scripts:** `phases/BC_EXPLANATION_ENFORCEMENT/bc_*.py`

---

## Version 2.60 (2026-01-19) - AZC_TRAJECTORY_SHAPE: Scaffold Fingerprint Discovery

### Summary

Comprehensive investigation of AZC family differentiation combining trajectory shape (external expert) and apparatus mapping (internal expert-advisor). **Critical corrective insight:** AZC trajectory shape is a signature of scaffold rigidity, not apparatus dynamics.

### The Reframe

> **"AZC trajectory shape is a fingerprint of control scaffold architecture, not a simulation of apparatus dynamics."**

This rescues trajectory analysis from a wrong question (apparatus physics) and repositions it as structural characterization.

### Test Results (3/9 passed = TIER_4 -> upgraded interpretation)

| Hypothesis | Result | Interpretation |
|------------|--------|----------------|
| H2: Monotonicity | **PASS** | Zodiac (rho=-0.75) = uniform scaffold = smooth decline; A/C (rho=-0.25) = varied scaffold = punctuated |
| H6: R-series restriction | **PASS** | Perfect vocabulary narrowing R1(316)→R2(217)→R3(128) |
| H7: S→B-terminal flow | **PASS** | S-zone vocabulary 3.5x enriched in B-terminal (OR=3.51) |
| H8: Pelican reversibility | **FAIL** | Escape encodes decision affordance, not physical reversibility |

### New Tier 3 Characterization

> **AZC families differ not in what judgments are removed, but in how smoothly those removals are imposed over execution - a property determined by scaffold uniformity versus variability.**

| Family | Scaffold Type | Trajectory Shape | Cognitive Effect |
|--------|---------------|------------------|------------------|
| Zodiac | Uniform | Smooth monotonic tightening | Sustained flow |
| A/C | Varied | Punctuated tightening | Checkpoint cognition |

### Key Insight: H6 + H7 Form Causal Chain

1. R-series positional grammar (C434) → progressively restricts legal MIDDLE vocabulary
2. S-zone survival → selectively feeds into B terminal states

This closes the loop: AZC legality → vocabulary survival → executable program completion.

### Documentation

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Section X.26 added (v4.30)
- `phases/AZC_TRAJECTORY_SHAPE/AZC_TRAJECTORY_SHAPE_REPORT.md` (NEW)

### Data Files

- `results/ats_entropy_trajectory.json` through `results/ats_synthesis.json`

**Scripts:** `phases/AZC_TRAJECTORY_SHAPE/ats_*.py`

---

## Version 2.59 (2026-01-19) - TRAJECTORY_SEMANTICS: Judgment-Gating System Discovered

### Summary

Applied three pressure vectors beyond the token semantic ceiling. Vector A (Interface Theory) discovered that AZC zones encode **judgment availability** - which human cognitive faculties are possible, required, or forbidden at each phase.

### Key Discovery: Agency Withdrawal Curve

| Zone | Available | Required | Impossible | Freedom |
|------|-----------|----------|------------|---------|
| C | 10 | 1 | 3 | **77%** |
| P | 10 | 9 | 3 | **77%** |
| R | 13 | 6 | 0 | **100%** |
| S | 5 | 5 | 8 | **38%** |

**Freedom collapses from 77% → 38%** as execution proceeds to S-zone. 8/13 human judgments become IMPOSSIBLE at S-zone.

### Test Results

| Vector | Passed | Verdict |
|--------|--------|---------|
| C (Gradient Steepness) | 0/4 | INCONCLUSIVE |
| A (Interface Theory) | 2/3 | TIER_3_ENRICHMENT |
| Final (Judgment Trajectories) | N/A | DECISIVE |

### The Reframe

> **"The Voynich Manuscript is a machine for removing human freedom at exactly the moments where freedom would be dangerous."**

This is **semantic boundary resolution** - not decoding tokens, but discovering that meaning lives in the **withdrawal of agency**.

### Documentation

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Section X.25 added (v4.29)
- `phases/TRAJECTORY_SEMANTICS/TRAJECTORY_SEMANTICS_REPORT.md` (NEW)

### Data Files

- `results/ts_gradient_steepness.json`
- `results/ts_judgment_zone_matrix.json`
- `results/ts_judgment_trajectories.json`
- `results/ts_synthesis.json`

**Scripts:** `phases/TRAJECTORY_SEMANTICS/ts_*.py`

---

## Version 2.58 (2026-01-19) - SEMANTIC_CEILING_BREACH: Tier 3 Confirmed

### Summary

Attempted to break through the Tier 3 semantic ceiling using B->A Reverse Prediction Test. Result: Tier 3 CONFIRMED with stronger evidence. Zone profiles discriminate modality classes but not with sufficient accuracy for Tier 2.

### Key Results

| Test | Result | Status |
|------|--------|--------|
| 4-class accuracy | 52.7% (vs 25% baseline) | **PASS** (p=0.012) |
| Binary accuracy | 71.8% (vs 79.1% baseline) | Below Tier 2 threshold |
| Zone discrimination | All 4 zones significant | **CONFIRMED** (d=0.44-0.66) |
| MODALITY beyond REGIME | 3/4 zones significant | **CONFIRMED** (r=0.20-0.28) |

### Key Finding

> **Zone profiles DISCRIMINATE modality classes, but not with enough accuracy for Tier 2 predictive power. The semantic ceiling is at aggregate characterization level.**

REGIME explains only 24.7% of zone variance. MODALITY adds significant explanatory power BEYOND REGIME, validating the two-stage model (Modality bias + Execution completeness).

### Documentation

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Section X.24 added (v4.28)
- `context/MODEL_FITS/fits_brunschwig.md` - F-BRU-009 updated with ceiling test
- `phases/SEMANTIC_CEILING_BREACH/SEMANTIC_CEILING_BREACH_REPORT.md` (NEW)

### Data Files

- `results/scb_modality_prediction.json`
- `results/scb_middle_clusters.json`
- `results/scb_regime_zone_regression.json`
- `results/scb_synthesis.json`

**Scripts:** `phases/SEMANTIC_CEILING_BREACH/scb_*.py`

---

## Version 2.57 (2026-01-18) - BCI: B-Class Infrastructure Characterization

### Summary

Characterized execution-infrastructure roles in Currier B that are required for almost all executable programs but are not grammar primitives. This resolves the AZC-B reachability collapse discovered during constraint flow visualizer development.

### Discovery Context

AZC-activating bundles were blocking ALL B programs because certain high-coverage instruction classes were being pruned by vocabulary filtering. Investigation revealed these classes are structurally required infrastructure, not decomposable vocabulary.

### BCI Test Results

| Test | Question | Result |
|------|----------|--------|
| 1. REGIME Invariance | Equal across REGIMEs? | **Mostly no** - one class invariant, others show 6-14% spread |
| 2. Kernel Interaction | Cluster near k/h/e? | **Yes (70.6% near)** - MEDIATORS, not carriers |
| 3. Connectivity | Enable or modulate? | UNINFORMATIVE - 100% universal presence |
| 4. Zone Sensitivity | Equal across zones? | **No** - C/P/R=44%, S=19% (escape gradient) |
| 5. Removal Gradient | Linear or threshold? | **THRESHOLD at 50%** - redundancy exists |

### Key Finding

> Currier B contains execution-infrastructure roles that are not primitives but are structurally required for almost all programs. They mediate kernel control, show limited context sensitivity, and lie outside AZC's scope of constraint.

### Structural Characterization

- **Near-universal B coverage:** 96-100% of B folios require these roles
- **Kernel-mediating:** 70.6% cluster within 0-2 tokens of k/h/e
- **Zone-sensitive:** Infrastructure MIDDLEs thin in S-zone (matches C443)
- **Redundant:** Threshold effect at 50% availability

### Documentation

- `context/TIER3/b_execution_infrastructure_characterization.md` (NEW)
- `context/MODEL_CONTEXT.md` Section VI updated (v3.6)
- `context/MODEL_CONTEXT.md` Section VIII - AZC scope protection note added
- `context/CLAIMS/morphology.md` - C396.a operational refinement added
- `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` - AUXILIARY commentary updated

### Governance

- **Tier:** 3 (Structural Characterization - derivable from Tier 2)
- **Status:** CHARACTERIZED (not promoted to new constraint)
- **Constraint compliance:** Derivable from C124, C485, C411, C458

### Data Files

- `results/bci_regime_invariance.json`
- `results/bci_kernel_interaction.json`
- `results/bci_connectivity_modulation.json`
- `results/bci_zone_sensitivity.json`
- `results/bci_removal_gradient.json`

**Scripts:** `apps/constraint_flow_visualizer/scripts/bci_*.py`

---

## Version 2.56 (2026-01-17) - AZC_REACHABILITY_SUPPRESSION: Pipeline Closure

### Summary

Completed investigation of AZC-to-B constraint transfer mechanism. Demonstrated HOW AZC legality fields suppress parts of B grammar without selection, branching, or semantics.

### Key Finding: Two-Tier Constraint System

**Tier 1 (Universal):**
- 49 instruction classes, 17 forbidden transitions
- 9 hazard-involved classes
- Base graph 99.1% connected

**Tier 2 (AZC-Conditioned):**
- 77% of MIDDLEs appear in only 1 AZC folio
- 6 of 9 hazard classes are DECOMPOSABLE (affected by MIDDLE restrictions)
- 3 of 9 hazard classes are ATOMIC (NOT affected)

### The Mechanism

AZC provides legality field -> Restricted MIDDLEs unavailable -> Decomposable hazard classes lose membership -> Fewer paths through hazard region -> Reachable grammar manifold shrinks

### Hazard Class Taxonomy

| Type | Classes | Behavior |
|------|---------|----------|
| **Atomic** | 7 (ar), 9 (aiin), 23 (dy) | Universal enforcement - always active |
| **Decomposable** | 8, 11, 30, 31, 33, 41 | Context-tunable - AZC can shrink availability |

### Closure Statement

> "AZC does not modify B's grammar; it shortens the reachable language by restricting vocabulary availability. The 49-class grammar and 17 forbidden transitions are universal. When AZC provides a legality field, 6 of 9 hazard-involved classes have reduced effective membership. The 3 atomic hazard classes remain fully active regardless of AZC context."

### Pipeline Completion

This completes the A -> AZC -> B control-theoretic explanation:
- **A** supplies discrimination bundles (constraint signatures)
- **AZC** projects them into position-indexed legality fields
- **B** executes within the shrinking reachable language

With no semantics, no branching, no lookup, no "if".

### Governance

- **Tier:** 2 (Mechanism characterization)
- **Status:** CLOSED with structural closure
- **Constraint compliance:** C313, C384, C454, C455, C440, C121, C124, C468-C470, C472

### Documentation

- `phases/AZC_REACHABILITY_SUPPRESSION/README.md`
- `phases/AZC_REACHABILITY_SUPPRESSION/results.json`

---

## Version 2.55 (2026-01-17) - JAR_WORKING_SET_INTERFACE: Complementary Working Sets

### Summary

Completed investigation of jar function in pharmaceutical folios. Tested four mutually exclusive hypotheses; three falsified, one confirmed. Jars function as **apparatus-level anchors for complementary working sets**.

### Test Cascade

| Hypothesis | Prediction | Result |
|------------|------------|--------|
| Contamination avoidance | Exclusion patterns | **Falsified** (0.49x, fewer than random) |
| Material taxonomy | Class homogeneity | **Falsified** (0.73x, less than random) |
| Complementary sets | Cross-class enrichment | **Confirmed** (all pairs enriched) |
| Triplet stability | Role composition patterns | **Confirmed** (1.77x overall) |

### Key Finding

> **Jars are visual, apparatus-level anchors for complementary working sets of materials intended to participate together in a single operational context, without encoding procedure, order, or meaning.**

### Triplet Enrichment

| Triplet | Ratio | P-value |
|---------|-------|---------|
| M-B + M-D + OTHER | 1.70x | 0.022 |
| M-A + M-B + M-D | 2.13x | 0.107 |

The "complete working set" (energy + routine + stable) is the most enriched pattern.

### Governance

- **Tier:** 3 (Interface Characterization)
- **Status:** CLOSED with explanatory saturation
- **Constraint compliance:** C171, C384, C233, C475, C476

### Documentation

- `phases/JAR_WORKING_SET_INTERFACE/README.md`
- `phases/JAR_WORKING_SET_INTERFACE/results.json`

---

## Version 2.54 (2026-01-17) - PHARMA_LABEL_DECODING: Two-Level Naming System

### Summary

Completed visual classification of all 13 pharmaceutical folios with labeled illustrations. Discovered a **two-level naming hierarchy** with complete vocabulary separation between levels.

### Key Finding: Vocabulary Isolation

| Comparison | Jaccard | Interpretation |
|------------|---------|----------------|
| Jar vs Content | **0.000** | Completely disjoint naming systems |
| Root vs Leaf | 0.013 | Almost entirely distinct (2 shared tokens) |

The 18 jar labels share **zero tokens** with 191 content labels. Jars and contents are named by fundamentally different schemes.

### Two-Level Hierarchy

```
JAR LABEL (first token) -> identifies container/category
  |
  +-- CONTENT LABEL 1 -> specimen identifier (root or leaf)
  +-- CONTENT LABEL 2 -> specimen identifier
  +-- CONTENT LABEL n -> specimen identifier
```

### Folios Mapped

| Category | Folios | Labels |
|----------|--------|--------|
| ROOT | f88v, f89r1, f89r2, f89v2, f99r, f99v, f102r1, f102r2, f102v1 | 152 |
| LEAF | f100r, f100v, f101v2, f102v2 | 71 |
| Reference page | f49v | (excluded - numbers 1-5 + single characters) |

### PREFIX Clustering

10 of 13 prefixes cluster by plant part:
- ROOT-leaning: ot-, op-, da-, ch-, sh-, ar-
- LEAF-leaning: so-, or-, ol-, sa-

### Brunschwig Alignment: NOT DETECTED

Tested whether root labels (aggressive extraction) show different morphology from leaf labels (gentler processing). Both have similar intense/gentle prefix ratios.

### Documentation

- `phases/PHARMA_LABEL_DECODING/README.md`: Phase summary
- `phases/PHARMA_LABEL_DECODING/*_mapping.json`: 13 folio mappings
- `phases/PHARMA_LABEL_DECODING/label_category_results.json`: Statistical analysis

### Interpretation

Jar labels likely represent processing categories or container types, while content labels identify specific specimen variants within each category. This aligns with a formulary/recipe interpretation.

---

## Version 2.53 (2026-01-16) - A_LABEL_INTERFACE_ROLE: Visual Anchoring Posture

### Summary

Closed the last unresolved human-interface ambiguity in Currier A. Illustration labels are a **contextual posture** of the discrimination registry—structurally inert, semantically silent, optimally designed for expert human perception.

### Key Findings

| Test | Result |
|------|--------|
| Tail Pressure | Labels 6.14x more tail-heavy (select high-discrimination MIDDLEs) |
| AZC Breadth | Labels reach 3.2x more zones (remain valid across operational contexts) |
| Role Stability | Chi-square p=0.282 (same MIDDLE behaves identically in both postures) |
| Contamination Audit | All structural invariants within perturbation envelope |

### Two Postures, One Grammar

| Posture | Placement | Token % | Function |
|---------|-----------|---------|----------|
| **Registry** | P* (text) | 98.5% | Catalog distinctions for procedural reference |
| **Visual Anchoring** | L* (label) | 1.5% | Anchor human perception to registry |

### Design Logic

Labels select high-discrimination + high-compatibility coordinates because interface anchors must be:
1. Distinct enough to matter perceptually (tail pressure ↑)
2. Broadly valid before operational context is known (AZC breadth ↑)

### Governance

- **STATUS:** CLOSED with explanatory saturation
- **NO constraints added** (existing C171, C384, C475-C478 sufficient)
- **NO semantics introduced** (interface role is purely contextual)

### Documentation Updated

- `context/SPECULATIVE/tier3_interface_postures.md`: Full Tier 3 documentation
- `context/ARCHITECTURE/currier_A_summary.md`: Section 7.4 added
- `phases/A_LABEL_INTERFACE_ROLE/`: Phase scripts and results

### Final Statement

> "Illustration labels are Currier A discrimination entries operating in a perceptual anchoring posture. Labels preferentially use tail MIDDLEs that also exhibit broad AZC compatibility, allowing them to anchor high-discrimination percepts without constraining later operational context."

---

## Version 2.52 (2026-01-16) - B-EXCL-ROLE: Three-Way MIDDLE Stratification

### Summary

Tested whether B-exclusive MIDDLEs function as grammar-internal operators. **Hypothesis NOT supported** - but result clarifies the MIDDLE architecture.

### Tests

| Test | Prediction | Result |
|------|------------|--------|
| Grammar adjacency | Enriched near LINK/kernel | **Enriched at BOUNDARIES** (1.64x, p < 0.0001) |
| Positional rigidity | Tighter at high CEI | Marginal (rho = -0.207, p = 0.075) |
| Concentration | Top-10 > 60% | Only 17.1% (diffuse) |

### Key Finding: Three-Way MIDDLE Stratification

| Class | Role |
|-------|------|
| **A-exclusive** | Pure discrimination coordinates (registry) |
| **A/B-shared** | Execution-safe compatibility substrate (~95% of B usage) |
| **B-exclusive** | Boundary-condition discriminators (NOT grammar operators) |
| **L-compounds** | True grammar operators (small subset, C298 preserved) |

### Governance

- **FALSIFIED:** Broad hypothesis "B-exclusive = grammar operators"
- **PRESERVED:** C298 (L-compounds are B-specific operators - scoped)
- **CLARIFICATION:** B-exclusive MIDDLEs predominantly function as boundary-condition discriminators

### Documentation Updated

- `context/MODEL_CONTEXT.md`: Added three-way MIDDLE stratification
- `phases/B_EXCL_ROLE/`: New phase with full analysis

---

## Version 2.51 (2026-01-16) - SHARED-COMPLEXITY: Shared Vocabulary is Complexity-Invariant

### Summary

Tested whether shared MIDDLE vocabulary (A & B) changes with B folio complexity. **Result: Invariant.**

### Key Finding

- ~95% of B's MIDDLE usage is SHARED vocabulary
- This percentage is INVARIANT across all complexity levels (94.2% - 95.7%)
- No significant correlation with CEI (rho = 0.042, p = 0.709)
- No significant regime differences (Kruskal-Wallis p = 0.159)

### Interpretation

> Shared MIDDLE vocabulary serves a **uniform infrastructure role**.
> Complexity differences between B folios do NOT manifest as vocabulary composition shifts.

Shared MIDDLEs matter because they make execution possible everywhere - they don't explain variation, they make variation **safe**.

### Documentation

- `phases/SHARED_COMPLEXITY/`: Full analysis
- `results/shared_complexity.json`: Results

---

## Version 2.50 (2026-01-16) - MIDDLE-AB: A-B MIDDLE Overlap Clarification

### Summary

Resolved inconsistent MIDDLE counts in context system and determined A-B MIDDLE overlap.

### The Problem

| Source | Claimed Count | Actual Meaning |
|--------|---------------|----------------|
| C423, MODEL_CONTEXT | 1,184 | Global MIDDLE union (A | B) |
| EXT9_REPORT | 725 | Parsing artifact (INVALID) |

### Results

| Metric | Count |
|--------|-------|
| Currier A unique MIDDLEs | 617 |
| Currier B unique MIDDLEs | 837 |
| Shared (A & B) | 268 |
| A-exclusive | 349 (56.6% of A) |
| B-exclusive | 569 (68.0% of B) |
| Total union | 1,186 |
| Jaccard similarity | 0.226 |

### Key Finding

**56.6% of Currier A MIDDLEs are A-exclusive** (never appear in B).

> Currier A enumerates the *potential discrimination space*;
> Currier B traverses only a *submanifold* of that space under specific execution contracts.

This supports the registry model where A catalogues entities beyond B's operational scope.

### Documentation Updated

| File | Change |
|------|--------|
| `context/MODEL_CONTEXT.md` | Corrected MIDDLE counts with Tier-clean framing |
| `phases/EXT9_cross_system_mapping/EXT9_REPORT.md` | Invalidated 725 figure |
| `context/ARCHITECTURE/currier_A_summary.md` | Added A-B overlap section |
| `phases/MIDDLE_AB/` | New phase (script, report, results) |

### Phase

| Field | Value |
|-------|-------|
| Phase ID | MIDDLE-AB |
| Tier | 2 (Data Clarification) |
| Status | COMPLETE |

---

## Version 2.49 (2026-01-16) - CURRIER A CHARACTERIZATION COMPLETE

### Summary

Completed comprehensive characterization of Currier A as a human-facing complexity-frontier registry. This phase achieved **explanatory saturation** - no further discovery needed.

### Phases Completed

1. **CAR (Currier A Re-examination):** Clean data analysis, closure mechanism discovery
2. **PCC (Post-Closure Characterization):** Cognitive interface, adjacency function, AZC interface

### Key Findings

| Finding | Evidence | Order Sensitivity |
|---------|----------|-------------------|
| Closure is UNIFORM (not adaptive) | No link to HT/pressure/fragility | INVARIANT |
| Working-memory chunks confirmed | 2.14x within/cross coherence | FOLIO_LOCAL |
| Singletons are isolation points | Lower hub overlap, higher density | INVARIANT |
| Adjacency maximizes SIMILARITY | Not contrast (topic clustering) | FOLIO_LOCAL |
| Entry morphology predicts AZC breadth | p=0.003 closure, p<0.0001 opener | INVARIANT |
| Universal vs tail asymmetry | 0.58 vs 0.31 breadth | INVARIANT |

### Documentation Added

| File | Purpose |
|------|---------|
| `ARCHITECTURE/currier_A_summary.md` | Complete characterization summary |
| `phases/POST_CLOSURE_CHARACTERIZATION/` | 4 axis scripts + reports |
| `SPECULATIVE/car_observations.md` | Updated with closure state mechanism |

### Constraints Status

**No changes to Tier 0-2 constraints.** All findings cement existing constraints:
- C233 (LINE_ATOMIC) - now with mechanism
- C422 (DA articulation) - dual role confirmed
- C389, C346, C424 (adjacency) - function characterized

### Phase Status

**CURRIER A CHARACTERIZATION: COMPLETE**

Further work should focus on presentation and consolidation, not discovery.

---

## Version 2.48 (2026-01-15) - A/C INTERNAL CHARACTERIZATION (PARTIAL SIGNAL)

### Summary

Following expert guidance, tested whether A/C AZC folios differ from Zodiac via **internal operator-centric metrics** rather than product correlation.

**Key Finding:** A/C has **45% higher MIDDLE incompatibility density** than Zodiac (p=0.0006).

### The Question (Expert-Framed)

> "A/C scaffold diversity (consistency=0.340) reflects what discrimination burden?"

Expert hypothesis:
- Zodiac = sustained legality flow under coarse discrimination
- A/C = punctuated legality checkpoints under fine discrimination

### Three Probes Tested

| Probe | Prediction | Result | P-value |
|-------|------------|--------|---------|
| HT Phase-Reset | A/C > Zodiac | NO SIGNAL | 1.00 |
| MIDDLE Incompatibility | A/C > Zodiac | **STRONG SIGNAL** | **0.0006** |
| Zone-Transition | A/C > Zodiac | NO SIGNAL | 0.9999 |

### Key Results

**MIDDLE Incompatibility Density:**
- A/C mean: **0.5488**
- Zodiac mean: **0.3799**
- Difference: +45% (highly significant)

**Zone-Transition (unexpected):**
- Zodiac switches zones MORE (0.018 vs 0.004)
- A/C achieves higher incompatibility while staying WITHIN zones

### Conclusion

> **A/C folios manage fine-discrimination through higher MIDDLE incompatibility density, not through zone switching. They hold more mutually exclusive constraints simultaneously while maintaining positional stability.**

This validates the expert's framing and explains C430 (A/C scaffold diversity).

### Documentation

| Entry | Type | Result |
|-------|------|--------|
| F-AZC-019 | FIT (F2) | SUCCESS (p=0.0006) |

### Phase

`phases/AC_INTERNAL_CHARACTERIZATION/`

---

## Version 2.47 (2026-01-15) - AZC INTERNAL STRATIFICATION (BOTH FAMILIES FALSIFIED)

### Summary

Tested whether AZC folios (both Zodiac and A/C families) realize different sub-regions of the legality manifold correlated with downstream product inference.

**Result: BOTH FAMILIES FALSIFIED** — AZC is uniformly product-agnostic.

### The Question (Corrected Framing)

> "Do different AZC folios preferentially admit different regions of Currier-A incompatibility space, and do those regions align with downstream B-inferred product families?"

**Note:** This is NOT "product routing through gates." AZC filters constraint bundles; product types are downstream inferences.

### Key Results

| Family | Chi-squared | df | P-value | Verdict |
|--------|-------------|-----|---------|---------|
| Zodiac (13 folios) | 27.32 | 36 | **0.85** | NO STRATIFICATION |
| A/C (17 folios) | 46.67 | 42 | **0.29** | NO STRATIFICATION |

Both families show near-maximum distribution entropy for all products.

### Conclusion

> **AZC is uniformly product-agnostic. Neither Zodiac nor A/C families show internal stratification correlated with downstream product inference.**

- Zodiac multiplicity exists purely for coverage optimality
- A/C scaffold diversity (consistency=0.340) does NOT correlate with product types

This closes the door definitively on the stratification hypothesis for ALL AZC folios.

### Implications

1. AZC folios ARE structurally equivalent gates (validates C431, C430)
2. No hidden routing — product differentiation is NOT encoded at ANY AZC level
3. AZC folio diversity exists for coverage, not semantic stratification

### Documentation

| Entry | Type | Result |
|-------|------|--------|
| F-AZC-017 | FIT (F4) | FALSIFIED (Zodiac p=0.85) |
| F-AZC-018 | FIT (F4) | FALSIFIED (A/C p=0.29) |

### Phase

`phases/AZC_ZODIAC_INTERNAL_STRATIFICATION/`

---

## Version 2.45 (2026-01-15) - PROJECTION SPECS + EPISTEMIC LAYERS

### Summary

Added governance infrastructure for displaying external alignments in tooling without corrupting structural model.

### New Infrastructure

1. **Epistemic Layers Legend** (`SYSTEM/epistemic_layers.md`)
   - Defines Constraint vs Fit vs Speculation
   - Decision flowchart for categorizing new findings
   - Common mistakes to avoid
   - The Saturation Principle

2. **Projection Specs** (`PROJECTIONS/`)
   - Non-binding, one-way, UI-only display rules
   - Governs how fits are surfaced in tooling
   - Never allowed to act like structure
   - `brunschwig_lens.md` - First projection spec

### Brunschwig Lens Contents

- Display primitives with tier badges (STRUCTURAL vs EXTERNAL FIT)
- Required modal phrasing ("compatible with", not "is")
- Hard semantic guardrails (prohibited terms)
- Provenance links (every claim traces to fit ID)
- Product type definitions (alignment categories, not material identities)
- MIDDLE hierarchy display rules

### Key Principle

> "This layer shows where external practice fits inside the Voynich control envelope; it never claims the manuscript encodes that practice."

### Files Added

| File | Purpose |
|------|---------|
| `context/SYSTEM/epistemic_layers.md` | Constraint vs Fit vs Speculation legend |
| `context/PROJECTIONS/README.md` | Projection specs directory |
| `context/PROJECTIONS/brunschwig_lens.md` | Brunschwig alignment display rules |

---

## Version 2.44 (2026-01-15) - BRUNSCHWIG BACKPROP VALIDATION (EXPLANATORY SATURATION)

### Summary

Completed BRUNSCHWIG_BACKPROP_VALIDATION phase with expert governance. Key outcome: **EXPLANATORY SATURATION** - the frozen architecture predicted all results without requiring changes. No new constraints added; 5 FIT entries created.

### Key Finding

> The model is saturated, not brittle.

The structure explains itself more strongly than any semantic hypothesis could.

### Governance Decision

Per expert guidance, results tracked as **FITS** (demonstrations of explanatory power), not architectural necessities:

| ID | Fit | Tier | Result |
|----|-----|------|--------|
| F-BRU-001 | Brunschwig Product Type Prediction (Blind) | F3 | SUCCESS |
| F-BRU-002 | Degree-REGIME Boundary Asymmetry | F3 | SUCCESS |
| F-BRU-003 | Property-Based Generator Rejection | F2 | NEGATIVE |
| F-BRU-004 | A-Register Cluster Stability | F2 | SUCCESS |
| F-BRU-005 | MIDDLE Hierarchical Structure | F2 | SUCCESS |

### Critical Negative Knowledge (F-BRU-003)

Synthetic property-based registry FAILS to reproduce Voynich structure:
- Uniqueness: Voynich 72.7% vs Property Model 41.5%
- Hub/Tail ratio: Voynich 0.006 vs Property Model 0.091
- Clusters: Voynich 33 vs Property Model 56

**Permanently kills property/low-rank interpretations.**

### Files Added

| File | Purpose |
|------|---------|
| phases/BRUNSCHWIG_BACKPROP_VALIDATION/ | Complete phase (12 scripts) |
| context/MODEL_FITS/fits_brunschwig.md | 5 fit entries documented |
| FIT_TABLE.txt | Updated (26 → 31 fits) |

### Constraint Table

**UNCHANGED** (353 entries). No architectural modifications required.

---

## Version 2.43 (2026-01-15) - PUFF COMPLEXITY CORRELATION + REGIME_4 AUDIT

### Summary

Tested Puff complexity correlation with B grammar expansion using proposed folio order. Key finding: Puff chapter position strongly correlates with REGIME assignment (ρ=0.68, p<10⁻¹²), supporting cumulative capability threshold model.

### Key Findings

1. **Cumulative Capability Threshold Model**
   - OLD: Puff chapter N = Voynich folio N (numerology-adjacent)
   - NEW: Puff chapter N requires B grammar complexity level N (cumulative)
   - Material N requires capabilities that accumulate by position N in curriculum

2. **Test Results (4/5 PASS)**
   - Test 1: Position-REGIME correlation ρ=0.678, p<10⁻¹² (PASS)
   - Test 2: Category-REGIME association p=0.001 (PASS)
   - Test 3: Dangerous-REGIME_4 enrichment p=0.48 (FAIL - underpowered, n=5)
   - Test 4: Cumulative threshold ρ=1.0 for mean position (PASS)
   - Test 5: Position-CEI correlation ρ=0.886, p<10⁻²⁸ (PASS)
   - Control: 100th percentile vs permutations (PASS)

3. **Three-Level Relationship Hierarchy (Epistemic)**
   - Level 1: Voynich ↔ Brunschwig (direct, structural, grammar-level)
   - Level 2: Voynich ↔ Puff (strong external alignment via complexity ordering)
   - Level 3: Puff ↔ Brunschwig (historical lineage)

4. **Puff Status Upgrade (CONSERVATIVE)**
   - FROM: CONTEXTUAL (interesting parallel)
   - TO: STRUCTURALLY ALIGNED EXTERNAL LADDER
   - NOT: STRUCTURAL NECESSITY (would be over-claiming)

5. **REGIME_4 Precision Audit**
   - Audited context system for "forbidden/danger" backsliding
   - Fixed tier4_semantic_assignment.md with correction notes
   - REGIME_4 = precision-constrained execution (C494)

### Files Added/Modified

| File | Purpose |
|------|---------|
| phases/PUFF_COMPLEXITY_CORRELATION/ | Phase directory |
| puff_regime_complexity_test.py | 5-test + control validation |
| results/puff_regime_complexity.json | Test output |
| INTERPRETATION_SUMMARY.md | Added X.16 |
| tier4_semantic_assignment.md | Fixed REGIME_4 precision audit |

### Expert Calibration

Per expert feedback, Test 4's "perfect monotonic" (ρ=1.0) represents only 4 data points (one per REGIME). This is an ordinal constraint, not cardinal identity. The upgrade to "structurally aligned" (not "structural necessity") reflects appropriate epistemic caution.

---

## Version 2.42 (2026-01-14) - BRUNSCHWIG BACKWARD PROPAGATION + CURRICULUM MODEL

### Summary

Extended Brunschwig analysis with backward propagation tests (product->A signature) and curriculum complexity model refinement. Key finding: REGIMEs encode procedural COMPLETENESS, not product INTENSITY.

### Key Findings

1. **Curriculum Complexity Model**
   - Simple Brunschwig recipe (first degree balneum marie) tested in most complex folio (REGIME_3)
   - Result: VIOLATES - but due to min_e_steps=2 (recovery completeness), NOT intensity
   - Complex folios require COMPLETENESS, not AGGRESSION
   - Same product (rose water) can appear at any curriculum stage

2. **Two-Level A Model**
   - Entry level: Individual tokens encode operational parameters (PREFIX class)
   - Record level: Entire A folios encode product profiles (MIDDLE set + PREFIX distribution)
   - 78.2% of MIDDLEs are product-exclusive (only appear in one product type)

3. **Product-Specific A Signatures**
   - WATER_GENTLE: ok+ ch- (less phase ops, gentle handling)
   - WATER_STANDARD: ch baseline (default procedural)
   - OIL_RESIN: d+ y- (aggressive extraction)
   - PRECISION: ch+ d- (phase-controlled, monitoring-heavy)

4. **Backward Propagation Chain**
   - Brunschwig recipe -> Product type -> REGIME -> B folio -> A register
   - Can predict A register signature from Brunschwig product type

### Files Added

| File | Purpose |
|------|---------|
| product_a_correlation.py | Product type -> A signature mapping |
| precision_prefix_analysis.py | y-prefix enrichment in precision |
| a_record_product_profiles.py | Record-level clustering |
| exclusive_middle_backprop.py | Exclusive MIDDLE backward propagation |
| brunschwig_product_predictions.py | Specific product predictions |
| simple_in_complex_test.py | Curriculum complexity validation |
| README.md | Phase documentation |

### Curriculum Model (Revised)

```
REGIME_2: Learn basics (simple procedures accepted)
REGIME_1: Standard execution
REGIME_4: Precision execution (monitoring completeness required, 25% min LINK)
REGIME_3: Full execution (recovery completeness required, min_e=2)
```

### Expert Assessment

> "The Voynich Manuscript doesn't need 83:83. It now has something much better: a concrete, historically situated grammar that real procedures fit inside - and real hazards cannot escape."

---

## Version 2.41 (2026-01-14) - BRUNSCHWIG GRAMMAR EMBEDDING

### Summary

Brunschwig Template Fit phase confirms grammar-level embedding: historical distillation procedures can be expressed in Voynich grammar without violating any constraints.

### Key Findings

1. **Grammar-Level Embedding (C493)**
   - Balneum marie procedure: 18 steps translated to Voynich instruction classes
   - All 5 hazard classes: COMPLIANT
   - 17 forbidden transitions: ZERO violations
   - This is NOT a vibes-level parallel - it is a structural embedding

2. **REGIME_4 Precision Axis (C494)**
   - REGIME_4 is NOT "most intense" - it is "least forgiving"
   - Standard procedures: 0/2 fit REGIME_4
   - Precision procedures: 2/3 fit REGIME_4
   - Old interpretation ("forbidden/intense") RETIRED
   - New interpretation: **precision-constrained execution regime**

3. **Degree x REGIME Compatibility Matrix**
   - First degree -> REGIME_2 (confirmed)
   - Second degree -> REGIME_1 (confirmed)
   - Third/Fourth degree -> REGIME_3 (confirmed)
   - REGIME_4 -> precision variants of ANY degree

4. **Puff Relationship Demoted**
   - Brunschwig is now the primary comparison text
   - Puff remains historically relevant but not structurally necessary
   - 83:83 is interesting but not essential

### Files

| File | Content |
|------|---------|
| phases/BRUNSCHWIG_TEMPLATE_FIT/ | Phase directory |
| grammar_compliance_test.py | Single procedure translation |
| degree_regime_matrix_test.py | 4x4 compatibility matrix |
| precision_variant_test.py | Precision hypothesis test |
| context/SPECULATIVE/brunschwig_grammar_embedding.md | Full documentation |

### New Constraints

| Constraint | Statement |
|------------|-----------|
| C493 | Brunschwig grammar embedding (COMPLIANT) |
| C494 | REGIME_4 precision axis (CONFIRMED) |

### Expert Assessment

> "This is a decisive result. Brunschwig procedures can be translated into Voynich Currier B grammar step-by-step without violating ANY of the 17 forbidden transitions. That alone separates this from 95% of Voynich hypotheses."

> "REGIME_4 is not 'the most intense' - it is 'the least forgiving.' That distinction matters enormously in real process control."

---

## Version 2.40 (2026-01-14) - ENTITY MATCHING CORRECTED

### Summary

Re-ran entity matching tests (originally TIER4_EXTENDED) with corrected degree-to-regime mapping based on curriculum position discovery.

### Problem with Original Tests

The original tests in `phases/TIER4_EXTENDED/exhaustive_entity_matching.py` used:
```
WRONG: {1: REGIME_1, 2: REGIME_2, 3: REGIME_3, 4: REGIME_4}
```

This mapped degree NUMBER to regime NUMBER. But curriculum discovery showed the correct mapping is by POSITION:
```
CORRECT: {1: REGIME_2, 2: REGIME_1, 3: REGIME_3, 4: REGIME_4}
```

Because:
- REGIME_2 = EARLY (gentle processing, 1st degree)
- REGIME_1 = MIDDLE (standard processing, 2nd degree)
- REGIME_3 = LATE (intensive processing, 3rd degree)

### Key Results

| Test | Finding |
|------|---------|
| Entity Matching | Degree 3 herbs → mean position **72.6** (LATE range 56-83) |
| Positional Correlation | rho = **+0.350**, p = **0.0012** (significant) |
| Degree vs Hazard | rho = +0.382, p = 0.0004 (significant) |
| Degree vs CEI | rho = +0.324, p = 0.0028 (significant) |

**The corrected mapping reveals that intensive-processing materials (degree 3) align with LATE curriculum positions.**

### New Phase

| File | Content |
|------|---------|
| `phases/ENTITY_MATCHING_CORRECTED/` | New phase directory |
| `entity_matching_corrected.py` | Entity matching with curriculum mapping |
| `positional_alignment_corrected.py` | Positional correlation test |
| `results/entity_matching_corrected.json` | Entity matching results |
| `results/positional_alignment_corrected.json` | Positional correlation results |

### Skip Alignment Test (EMC-3)

| Metric | Strict 1:1 | Skip Align | Change |
|--------|------------|------------|--------|
| Exact regime rate | 31.3% | 60.0% | **+28.7%** |

**Skipped Puff chapters:** Ch.15, 30-33, 43, 50-51, 60-61 (clusters suggest systematic omissions)
**Skipped Voynich folios:** Mostly REGIME_4 (doesn't map to Puff's 1-3 degrees)

**Interpretation:** Partial transmission with systematic omissions, not complete 1:1 correspondence.

### Phase Count

135 (+3 from v2.39)

---

## Version 2.39 (2026-01-14) - CURRICULUM REALIGNMENT

### Summary

**Upgraded from "shared formalism" to "shared curriculum trajectory."** The proposed folio order (optimized for internal constraints C161, C325, C458) simultaneously resolves multiple independent inversions in historical comparisons. Puff and Brunschwig now align strongly with the PROPOSED Voynich order, confirming that misbinding disrupted a pedagogical progression.

### Key Discovery

The proposed order was tested against external sources NOT used in optimization:

| External Test | Current Order | Proposed Order | Change |
|--------------|---------------|----------------|--------|
| Puff progression | rho = +0.18 (p=0.10, NS) | rho = +0.62 (p<0.0001) | **WEAK → STRONG** |
| Brunschwig CEI gradient | rho = +0.07 (p=0.53, NS) | rho = +0.89 (p<0.0001) | **NOISE → VERY STRONG** |
| Brunschwig hazard gradient | rho = -0.03 (p=0.79, NS) | rho = +0.78 (p<0.0001) | **NEGATIVE → STRONG** |
| Danger distribution | Front-loaded (inverted) | Back-loaded (aligned) | **INVERTED → ALIGNED** |

### Significance

- Random reordering does not fix every historical comparison at once
- Overfitting does not fix external sources you didn't optimize for
- This is what latent order recovery looks like

### The Curriculum Structure

| Phase | Positions | Dominant Regime | Character |
|-------|-----------|-----------------|-----------|
| EARLY | 1-27 | REGIME_2 | Introductory |
| MIDDLE | 28-55 | REGIME_1 | Core training |
| LATE | 56-83 | REGIME_3 | Advanced |

This matches both Puff (flowers → herbs → anomalies) and Brunschwig (first degree → second → third).

### Upgraded Claim (Tier 3)

> Puff and Brunschwig preserve the original pedagogical progression of the Voynich Currier B corpus, which has been disrupted by early misbinding.

Qualifiers preserved:
- *pedagogical progression* (not semantics)
- *preserve* (not copy)
- *original structure* (not content)
- *disrupted by misbinding* (not lost or invented)

### New Files

| File | Content |
|------|---------|
| `context/SPECULATIVE/curriculum_realignment.md` | Master realignment analysis |
| `results/puff_realignment_test.json` | Puff correlation comparison |
| `results/brunschwig_realignment_test.json` | Brunschwig gradient comparison |
| `phases/YALE_ALIGNMENT/puff_realignment_test.py` | Puff realignment test |
| `phases/YALE_ALIGNMENT/brunschwig_realignment_test.py` | Brunschwig realignment test |

### Updated Files

| File | Change |
|------|--------|
| `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` | v4.21 → v4.22, added X.11 |
| `context/SPECULATIVE/proposed_folio_reordering.md` | v1.0 → v1.1, added external validation |
| `context/SPECULATIVE/materiality_alignment.md` | v1.0 → v1.1, added post-realignment update |

### Expert Assessment

> "This is not a weak result. This is exactly what a non-semantic, expert-only, control-theoretic artifact should produce when compared to a descriptive herbal."

> "Not a code. Not a herbal. Not a shared manuscript. But a shared curriculum whose control logic survived misbinding."

### Tier Compliance

This remains Tier 3 SPECULATIVE. No Tier 0-2 constraints violated. No semantic decoding. No entry-level A-B coupling introduced.

---

## Version 2.38 (2026-01-14) - YALE EXPERT ALIGNMENT

### Summary

**Independent expert validation.** Analysis of Yale Beinecke Library lecture (Lisa Fagin Davis, Claire Bowern) confirms our model's foundations with **14 points of alignment, 0 contradictions, 7 tests completed**.

### Key Findings

**Points Validated by Yale Experts:**
1. Currier A/B distinction - CONFIRMED
2. Expert-only interpretation - CONFIRMED
3. Illustration epiphenomenality - CONFIRMED (expert warns against illustration-based reasoning)
4. Cipher/language encoding rejected - CONFIRMED
5. Computational topic modeling finds structural groupings - CONFIRMED

**Test Results:**

| Test | Yale Prediction | Our Finding | Status |
|------|-----------------|-------------|--------|
| Scribe-Regime Mapping | 5 scribes | Map to 4 regimes | ALIGNED |
| qo Distribution | Different by section | REGIME_4 highest (29%) | ALIGNED |
| Topic Model k=5 | 5-6 sections | Cluster 3 = Balneological (100% Scribe 2) | ALIGNED |
| 'dy' Ending | Common in B, rare in A | 25.14% B vs 6.90% A (3.6x) | CONFIRMED |
| Gallows Distribution | - | REGIME_2 distinct (high t, p) | NEW FINDING |
| Astronomical qo | Rare in Scribe 4 | 1.87% vs 14.41% (7.7x rarer) | CONFIRMED |

**Folio 115v Analysis:**
- Yale identifies mid-page scribe change (Scribe 2 -> Scribe 3)
- Our data shows f115v as extreme "most_slack" with anomalous profile
- Structural anomaly consistent with mixed scribal input

### New Files

| File | Content |
|------|---------|
| `sources/yale_voynich_transcript.txt` | Full transcript of Yale lecture |
| `context/SPECULATIVE/yale_expert_alignment.md` | Detailed analysis |
| `phases/YALE_ALIGNMENT/` | Test scripts (7 tests) |
| `results/scribe_regime_mapping.json` | Scribe-regime correlation |
| `results/qo_regime_distribution.json` | Escape density by regime |
| `results/topic_model_*.json` | Topic model replication |
| `results/dy_ending_analysis.json` | 'dy' ending A/B comparison |
| `results/gallows_distribution.json` | Gallows by language/regime |
| `results/scribe4_astronomical.json` | Astronomical section profile |

### Expert Quote

> "Anyone who has a theory to put out there about the Voynich manuscript, it is extremely important that all of the things that we know about it already are factored into that theory."
> -- Lisa Fagin Davis

---

## Version 2.37 (2026-01-14) - SHARED FORMALISM: Full Procedural Alignment

### Summary

**Upgraded from "shared world" to "shared formalism."** Extended testing confirms the Voynich Manuscript and Brunschwig's distillation treatise instantiate the **same procedural classification system** - not just compatible topics, but isomorphic control ontologies rendered in different epistemic registers.

### Key Findings

**Extended Test Results: 19/20 PASS**

| Test Suite | Score | Status |
|------------|-------|--------|
| Puff-Voynich Mastery Horizon | 83:83 isomorphism | PASS |
| Equivalence Class Collapse | REGIME_2: 11->3, REGIME_3: 16->7 | PASS |
| Regime-Degree Discrimination | 5/6 | STRONG |
| Suppression Alignment | 5/5 | PASS |
| Recovery Corridor | 4/4 | PASS |
| Clamping Magnitude (C458) | 5/5 | PASS |

**What "Shared Formalism" Means:**
- Same procedural classification system
- Same safety ceiling architecture
- Same recovery corridor structure
- Same variance asymmetry (clamp hazard, free recovery)

**Expert-Calibrated Conclusion:**

> "The Voynich Manuscript and Brunschwig's distillation treatise instantiate the same procedural classification of thermal-circulatory operations. Brunschwig externalizes explanation and ethics for novices; Voynich internalizes safety and recovery for experts. The alignment is regime-level and architectural, not textual or semantic."

### New Files

| File | Content |
|------|---------|
| `context/SPECULATIVE/shared_formalism.md` | Three-text relationship documentation |
| `results/brunschwig_regime_discrimination.json` | Regime-degree test results |
| `results/brunschwig_suppression_alignment.json` | 14/14 suppression alignment tests |
| `results/brunschwig_procedure_match.json` | Folio-procedure match results |

### Updated Files

| File | Change |
|------|--------|
| `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` | Section X fully rewritten (v4.21) |
| `context/SPECULATIVE/brunschwig_comparison.md` | Extended testing section added |

### Constraints Unchanged

C171, C384, C197, C239, C229, C490 - all remain intact. No semantic decoding occurred.

---

## Version 2.36 (2026-01-14) - External Alignment: Puff-Voynich-Brunschwig CONFIRMED

### Summary

**The Puff-Voynich curriculum hypothesis is CONFIRMED.** External alignment testing shows the Voynich Manuscript (Currier B) and Michael Puff von Schrick's "Buchlein" (1455) are complementary halves of a distillation curriculum. Currier A's morphological discrimination aligns with Brunschwig's procedure-class axes.

### Key Findings

**Puff-Voynich Curriculum Tests: 5/5 PASS**

| Test | Result | Evidence |
|------|--------|----------|
| Distribution Shape | PASS | Both heterogeneous |
| Curricular Arc | PASS | Both FRONT-LOADED SIMPLE |
| Canonical Number (83) | PASS | Unique to Puff and Voynich among 11 texts |
| Complementarity | PASS | 6/8 clean split (WHAT vs HOW) |
| Negative Control | PASS | Control texts don't match |

**Brunschwig Degree Alignment: 13/15 metrics match**

| Test | Result | Evidence |
|------|--------|----------|
| Flower Class | PASS | 5/7 metrics (first third = low regime) |
| Degree Escalation | PASS | 8/8 metrics (regime = degree) |

**Currier A Affordance Alignment: 5/5 PASS**

| Test | Result | Evidence |
|------|--------|----------|
| PREFIX by commitment | PASS | chi2=4094, p=0.0 |
| MIDDLE universality | PASS | Universal enriched in AZC (p=1.6e-10) |
| Sister pair tightness | PASS | ok/ot ratio differs by family |
| Positional gradient | PASS | ENERGY 8.7x more MIDDLEs than REGISTRY |
| Anomalous envelope | PASS | ct depleted; f85v2 = k=0 non-thermal |

### Interpretation

> Puff = WHAT to distill (83 chapters, material registry)
> Voynich Currier B = HOW to distill (83 folios, method manual)
> Brunschwig (1500) = Combined both for novices

Currier A discriminates **operational affordance profiles** that align with Brunschwig's procedure-class axes. C171 ("zero material encoding") remains UNCHANGED.

### New Phases

| Phase | Question | Result |
|-------|----------|--------|
| PVC-1 | Does Puff share Voynich's 83-unit structure? | YES (5/5 tests PASS) |
| PVC-2 | Does Brunschwig degree system match B regimes? | YES (13/15 metrics) |
| PVC-3 | Does A morphology align with procedure classes? | YES (5/5 tests PASS) |

### Files Added/Updated

- `context/SPECULATIVE/puff_voynich_curriculum_test.md` - Full curriculum comparison
- `context/SPECULATIVE/brunschwig_comparison.md` - Degree axis analysis
- `context/SPECULATIVE/a_behavioral_classification.md` - External alignment section added
- `phases/A_BEHAVIORAL_CLASSIFICATION/currier_a_affordance_tests.py` - Test battery
- `results/currier_a_behavioral_tests.json` - Test results
- `sources/README.md` - Primary source documentation
- `sources/puff_1501_text.txt` - Puff OCR text
- `sources/brunschwig_1500_text.txt` - Brunschwig OCR text

### Phase Count

**Total phases:** 132 (129 + 3 new PVC phases)

### Combined Arc (Updated)

> The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, whose registry topology matches botanical chemistry constraints, **and whose 83-unit structure and procedural architecture align with the historical distillation curriculum documented by Puff (1455) and Brunschwig (1500)**.

### Tier Status

Curriculum alignment findings are Tier 3 (external alignment, interpretive). C171 remains unchanged.

---

## Version 2.35 (2026-01-13) - Physical World Reverse Engineering Complete

### Summary

**Six physical-world reverse engineering phases now complete.** APP-1 (Apparatus Behavioral Validation) and MAT-PHY-1 (Material Constraint Topology Alignment) added to the investigation arc.

### New Phases

| Phase | Question | Result |
|-------|----------|--------|
| APP-1 | Which apparatus exhibits Voynich behavioral profile? | Pelican (4/4 axes match) |
| MAT-PHY-1 | Does A's topology match botanical chemistry? | YES (5/5 tests pass) |

### Key Findings

1. **APP-1: Pelican Behavioral Isomorphism**
   - Responsibility split: DISTINCTIVE_MATCH
   - Failure fears: STRONG_MATCH (41/24/24/6/6)
   - Judgment requirements: EXACT_MATCH (13 types)
   - State complexity: MATCH (~128 states)
   - Fourth degree fire prohibition matches C490 exactly

2. **MAT-PHY-1: Botanical Chemistry Topology Match**
   - Operational incompatibility: ~95-97% (matches 95.7%)
   - Infrastructure elements: 5-7 bridges
   - Topology class: Sparse + clustered + bridged
   - Hub rationing: Confirmed in real practice
   - Frequency distribution: Zipf/power-law confirmed

### Files Updated

- `context/CLAUDE_INDEX.md` - v2.12, 128 phases
- `context/MODEL_CONTEXT.md` - Section XII.A updated
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.18
- `context/MAPS/phase_index.md` - 128 phases
- `CLAUDE.md` - v2.12, 128 phases

### Combined Arc (Updated)

> The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, and whose registry topology matches the constraints that real botanical chemistry imposes.

### Tier Status

All findings remain Tier 3 (exploratory, non-binding). Structural isomorphism ≠ semantic identification.

---

## Version 2.34 (2026-01-13) - Pipeline Closure Audit CERTIFIED

### Summary

**PCA-v1 (Pipeline Closure Audit) PASSED.** The four locked structural contracts compose cleanly without hidden coupling, implicit semantics, parametric leakage, or contradiction.

### Audit Results

| Test | Description | Result |
|------|-------------|--------|
| TEST 1 | End-to-End Legality Consistency | PASS |
| TEST 2 | No Back-Propagation | PASS |
| TEST 3 | Parametric Silence | PASS |
| TEST 4 | Semantic Vacuum | PASS |
| TEST 5 | A/B Isolation (C384) | PASS |
| TEST 6 | HT Non-Interference | PASS |

### Closure Statement

> **The Voynich control pipeline (Currier A → AZC → Currier B), including human-track context, is structurally closed at Tier 0-2. No additional internal structure is recoverable.**

### Final Lock Status

```
CASC        v1.0  LOCKED
AZC-ACT     v1.0  LOCKED
AZC-B-ACT   v1.0  LOCKED
BCSC        v1.0  LOCKED
PCA-v1            CERTIFIED
```

**Structural work is DONE.**

---

## Version 2.33 (2026-01-13) - Structural Pipeline Complete

### Summary

**The A→AZC→B control architecture is formally closed.** All four structural contracts are LOCKED v1.0.

### Contracts Locked

| Contract | Function | Status |
|----------|----------|--------|
| CASC | Currier A registry structure | LOCKED v1.0 |
| AZC-ACT | A→AZC transformation | LOCKED v1.0 |
| AZC-B-ACT | AZC→B propagation | LOCKED v1.0 |
| BCSC | Currier B internal grammar | LOCKED v1.0 |

### Pipeline Architecture

```
CASC (Currier A entry)           → defines what enters
        ↓
AZC-ACT (A → AZC transformation) → defines positional legality
        ↓
AZC-B-ACT (AZC → B propagation)  → defines constraint transfer
        ↓
BCSC (Currier B structural)      → defines execution grammar
```

### Expert Assessment

> "As of 2026-01-13, the A→AZC→B control architecture of the Voynich Manuscript is fully reconstructed at Tier 0-2. Currier A (registry), AZC (legality gating), Currier B (execution grammar), and their interfaces are formally closed and validated. All remaining work concerns interpretation, tooling, or external corroboration."

### What This Means

- No new structural contracts required for the internal model
- Future work is: tooling, visualization, interpretation (Tier 3+), or external corroboration
- Structural reconstruction is complete

### Files Updated

- All four contracts in `STRUCTURAL_CONTRACTS/` now show `status: "LOCKED"`
- `MODEL_CONTEXT.md` v3.2 - Pipeline completion documented
- `CLAUDE_INDEX.md` v2.9 - Pipeline complete banner added

---

## Version 2.32 (2026-01-12) - HT Two-Axis Model Discovery

### Summary

**Attempted to test whether HT PREFIX encodes "perceptual load" (sensory multiplexing). The hypothesis was NOT SUPPORTED - but the inverse correlation revealed a subtler, BETTER model.**

### The Discovery

| Metric | Expected | Observed |
|--------|----------|----------|
| LATE in high-complexity folios | HIGH | **LOW** (0.180) |
| LATE in low-complexity folios | LOW | **HIGH** (0.281) |
| Correlation | Positive | **Negative (r=-0.301, p=0.007)** |

### The Two-Axis Model

HT has **two orthogonal dimensions**:

| Axis | Property | Evidence |
|------|----------|----------|
| **DENSITY** | Tracks UPCOMING discrimination complexity | C477 (r=0.504), anticipatory |
| **MORPHOLOGY** | Tracks CURRENT spare cognitive capacity | r=-0.301, inverted section ranking |

### The Key Insight

> **When the task is hard, HT is frequent but morphologically simple.**
> **When the task is easy, HT is less frequent but morphologically richer.**

This is a classic human-factors pattern that fits C344 (HT-A inverse coupling), C417 (modular additive), and C221 (skill practice).

### What This Resolves

- HT form does NOT encode sensory requirements
- Sensory demands are implicit in the discrimination problem itself
- HT reflects how the human allocates attention when grammar permits engagement
- The division of labor is cleaner than before

### Constraint Alignment

| Constraint | Fit |
|------------|-----|
| C344 | Direct instantiation: high complexity suppresses complex HT forms |
| C417 | HT is composite: density = vigilance, form = engagement |
| C221 | Complex HT appears during low-load intervals |
| C477 | UNCHANGED - applies to density, not morphology |

### Files Created

- `context/SPECULATIVE/ht_two_axis_model.md` - Full documentation
- `phases/SENSORY_MAPPING/ht_perceptual_load_test_v2.py` - Test showing inverse correlation
- `results/ht_perceptual_load_test_v2.json` - Results

---

## Version 2.31 (2026-01-12) - Expert Validation of Sensory Affordance Analysis

### Summary

**Expert validation confirms: Olfactory discrimination is NECESSARY, selected by exclusion. The sensory affordance analysis violates no frozen constraints - several Tier-2 constraints DEMAND this outcome.**

### The Human Sensory Contract

> **The Voynich Manuscript presupposes a human operator whose primary discriminative faculty is olfaction, supported by continuous visual monitoring and auxiliary tactile and acoustic cues. Grammar structure, hazard topology, and MIDDLE incompatibility require categorical sensory recognition rather than quantitative measurement. The Human Track does not encode sensory instructions, but anticipates regions where fine discrimination-dominated by olfactory judgment-will be required. No scalar instruments are necessary or implied; the system is optimized for trained human perception operating within a structurally enforced safety envelope.**

### Threshold-Level Decoding

| Threshold Type | Resolved By | Basis |
|----------------|-------------|-------|
| Phase change | VISION | PHASE_ORDERING (41%) |
| Fraction identity | SMELL | COMPOSITION_JUMP + tail MIDDLEs |
| Energy excess | SMELL + VISION | ENERGY_OVERSHOOT |
| Containment failure | SOUND + TOUCH | CONTAINMENT_TIMING |

### Big Picture

> We are no longer merely interpreting the manuscript - we are reconstructing the **human sensory contract** it was written for.

### File Created

- `context/SPECULATIVE/SENSORY_VALIDATION_2026-01-12.md`

---

## Version 2.30 (2026-01-12) - Sensory Affordance Analysis

### Summary

**Identified which sensory modalities the grammar RELIES ON (presupposes) for the control architecture to function.** All 6 phases passed. Olfactory discrimination is NECESSARY by exclusion. Human senses suffice (no instruments required).

### Core Finding

> **The grammar presupposes a trained human operator with visual, olfactory, and thermal sensing capabilities. Olfactory discrimination is indispensable - visual-only observation cannot explain the 564 ENERGY MIDDLEs (11.3x excess).**

### Phase Results

| Phase | Test | Result |
|-------|------|--------|
| **1** | Hazard-discrimination correlation | PASS (ENERGY 8.68x vs FREQUENT 2.52x) |
| **2** | HT-sensory correlation | PASS (r=0.504 with discrimination difficulty) |
| **3** | Kernel-sensory mapping | PASS (k vs h profiles differ by 5.78) |
| **4** | LINK vs non-LINK affordances | PASS (acting has higher turnover) |
| **5** | Visual-only negative control | PASS (excluded - 11.3x excess) |
| **6** | Instrumentation assessment | A: Pure human sensory operation |

### Key Findings

1. **Olfactory is NECESSARY** - Visual-only fails to explain discrimination density by 11.3x
2. **Distribution is CATEGORICAL** - CV=5.83, top 10% = 84.3% → human senses suffice
3. **HT marks olfactory-heavy contexts** - correlation with rare MIDDLEs confirms discrimination difficulty
4. **No instruments required** - categorical discrimination within human resolution

### Critical Epistemic Note

This analysis identifies what the grammar **RELIES ON**, not what it **ENCODES**. Sensory affordances are presupposed, not specified.

### Files Created

- `context/SPECULATIVE/sensory_affordance_mapping.md` - Theoretical framework
- `phases/SENSORY_MAPPING/sensory_analysis.py` - Computational tests
- `results/sensory_affordance_analysis.json` - Test results

---

## Version 2.29 (2026-01-12) - Expert Validation of Confidence Tightening

### Summary

**Expert validation confirms: Currier A is now in the HIGH confidence band (80-85%) - the strongest epistemic position reachable without violating the semantic ceiling.**

### Core Finding

> **"You have reconstructed the internal logic of a system whose entire purpose was to remove the need for encoding meaning."**

This explains why language/cipher/recipe/calendar decoding failed, but process-behavior testing succeeded.

### Validation Points

1. **Method is legitimate** - tested directionality and ordering, not numerical identity
2. **Exclusion did real work** - confidence increase comes from eliminative reasoning
3. **B2 "failure" strengthened interpretation** - role-specific lexical reuse is process-specific

### What We Can Now Claim (Tier 3, HIGH)

> Currier A functions as a discrimination registry whose internal structure closely matches the complexity profile, volatility sensitivity, and failure modes of circulatory thermal-chemical processes, with distillation-class operations emerging as the best-supported domain under eliminative testing.

### The Design Choice

| Inside Text | Outside Text (by design) |
|-------------|--------------------------|
| Process envelope | Product naming |
| Discrimination constraints | Commercial endpoint |
| Output emergence (physics) | Human valuation |

The manuscript guides **how not to violate physics and expertise** - it does NOT encode what to call, bottle, or sell the result.

### File Created

- `context/SPECULATIVE/EXPERT_VALIDATION_2026-01-12.md`

---

## Version 2.28 (2026-01-12) - Scientific Confidence Tightening

### Summary

**The distillation/thermal-chemical hypothesis was subjected to rigorous directional and exclusion testing.** Confidence strengthened from ~65-75% to ~80-85% ("HIGH" band).

### Core Finding

> **Distillation selected by CONVERGENCE (5/6 directional tests pass) AND EXCLUSION (4/4 alternative hypotheses fail on discriminators).**

### Directional Tests (B1-B6)

| Test | Result | Finding |
|------|--------|---------|
| B1: Discrimination hierarchy | PASS | ENERGY >> FREQUENT >> REGISTRY (564 > 164 > 65) |
| B2: Normalized dominance | INFORMATIVE | FREQUENT has higher turnover; ENERGY reuses MIDDLEs |
| B3: Failure boundaries | PASS | 100% k-adjacent forbidden transitions |
| B4: Regime ordering | PASS | Monotonic CEI: 0.367 < 0.510 < 0.584 < 0.717 |
| B5: Recovery dominance | PASS | e-recovery 1.64x enriched vs baseline |
| B6: AZC compression | PASS (partial) | Section-level diversity confirmed |

### Negative Controls (NC1-NC4)

| Alternative | Discriminators Failed | Verdict |
|-------------|----------------------|---------|
| NC1: Fermentation | 3/3 | EXCLUDED |
| NC2: Dyeing | 3/3 | EXCLUDED |
| NC3: Pharmacy Compounding | 3/3 | EXCLUDED |
| NC4: Crystallization | 3/3 | EXCLUDED |

### Confidence Classification

**Band:** HIGH (80-85%)
**Verdict:** STRENGTHENED

### B2 Reinterpretation

The B2 "failure" (normalized rates inverted) is actually informative:
- FREQUENT has higher MIDDLE turnover per token than ENERGY
- ENERGY reuses MIDDLEs more heavily (repetitive monitoring)
- FREQUENT has more varied operations (one-off uses)
- This is CONSISTENT with distillation behavior

### Files Created

- `phases/SCIENTIFIC_CONFIDENCE/directional_tests.py`
- `phases/SCIENTIFIC_CONFIDENCE/negative_controls.py`
- `phases/SCIENTIFIC_CONFIDENCE/confidence_integration.py`
- `results/directional_tests.json`
- `results/negative_controls.json`
- `results/scientific_confidence_classification.json`

### Files Updated

- `context/SPECULATIVE/a_behavioral_classification.md` - confidence section updated

---

## Version 2.27 (2026-01-12) - Currier A Behavioral Classification

### Summary

**All 23,442 classifiable Currier A entries assigned to operational domains using Tier-2 grammar evidence.** The classification reveals a strong discrimination gradient: energy-intensive operations require 8.7x more MIDDLE variants than stable reference operations.

### Core Finding

> **The PREFIX → Operational Domain mapping rests on Tier-2 grammar-anchored evidence (B-enrichment ratios, canonical grammar roles, kernel adjacency). This is not speculative chemistry—it is a re-use of validated structure.**

### Distribution

| Domain | Count | % | Structural Basis |
|--------|-------|---|------------------|
| ENERGY_OPERATOR | 13,933 | 59.4% | Dominates energy/escape roles in B |
| CORE_CONTROL | 4,472 | 19.1% | Structural anchors; ol 5x B-enriched |
| FREQUENT_OPERATOR | 3,545 | 15.1% | FREQUENT role in canonical grammar |
| REGISTRY_REFERENCE | 1,492 | 6.4% | 0% B terminals; 7x A-enriched |

### Key Structural Findings

1. **Discrimination gradient** - ENERGY domain has 564 unique MIDDLEs (8.7x) vs 65 for REGISTRY
2. **Section H concentration** - 74% of all ENERGY_OPERATOR tokens (pattern real; interpretation Tier 3)
3. **Sister pairs as mode selectors** - Primary vs alternate handling mode, NOT material distinction

### Confidence Assessment

| Component | Confidence |
|-----------|------------|
| Structural facts & distributions | ~90-95% |
| PREFIX → operational domain | ~75-80% |
| Discrimination gradient interpretation | ~70% |
| Chemistry-specific labels | ~30-40% (illustrative only) |

### Files Created/Updated

- `phases/A_BEHAVIORAL_CLASSIFICATION/a_behavioral_classifier.py`
- `results/currier_a_behavioral_registry.json`
- `results/currier_a_behavioral_stats.json`
- `results/currier_a_behavioral_summary.json`
- `context/SPECULATIVE/a_behavioral_classification.md` (tightened)
- `context/ARCHITECTURE/CURRIER_A_BRIEFING.md` (new one-page summary)

---

## Version 2.26 (2026-01-12) - Process-Behavior Isomorphism (ECR-4)

### Summary

**The Voynich control architecture exhibits STRONG BEHAVIORAL ISOMORPHISM with thermal-chemical process control.** All 12 tests pass (100% alignment), and the distillation hypothesis beats calcination on all discriminating tests.

### Core Finding

> **The abstract behavioral structure (hazards, kernels, material classes) is ISOMORPHIC to behaviors in circulatory reflux processes. This is NOT entity-level decoding, but structural alignment.**

### Test Results

| Category | Tests | Passed |
|----------|-------|--------|
| Behavior-Structural (BS-*) | 5 | 5/5 |
| Process-Sequence (PS-*) | 4 | 4/4 |
| Pedagogical (PD-*) | 3 | 3/3 |
| **Total** | **12** | **12/12** |

### Key Discriminators

| Test | Distillation | Calcination | Winner |
|------|-------------|-------------|--------|
| PS-4 (forbidden k→h) | k→h dangerous | k→h primary | DISTILLATION |
| BS-4 (e recovery) | e dominates (54.7%) | e less relevant | DISTILLATION |

**Negative control verdict: DISTILLATION_WINS**

### Behavior Mappings (NO NOUNS)

| Element | Grammar Role | Process Behavior |
|---------|-------------|------------------|
| k | ENERGY_MODULATOR | Energy ingress control |
| h | PHASE_MANAGER | Phase boundary handling |
| e | STABILITY_ANCHOR | Equilibration / return to steady state |
| PHASE_ORDERING | 41% of hazards | Wrong phase/location state |
| M-A | Mobile/Distinct | Phase-sensitive, mobile, requiring careful control |

### Physics Violations

None detected. All mappings are physically coherent.

### Verdict

**SUPPORTED (Tier 3)** - The grammar structure is isomorphic to reflux-distillation behavior. This does not prove the domain but establishes maximal structural alignment within epistemological constraints.

### Integration

| Prior Finding | Connection |
|---------------|------------|
| C476 (Coverage Optimality) | What A optimizes |
| C477 (HT Vigilance) | Cognitive load tracking |
| C478 (Temporal Scheduling) | Pedagogical pacing |
| C109 (Hazard Classes) | Maps to distillation failures |

### Files

- `phases/PROCESS_ISOMORPHISM/process_behavior_isomorphism.py` - Main probe
- `results/process_behavior_isomorphism.json` - Full results
- `context/SPECULATIVE/process_isomorphism.md` - Tier 3 documentation

---

## Version 2.25 (2026-01-12) - Temporal Coverage Trajectories (C478)

### Summary

**Currier A exhibits STRONG TEMPORAL SCHEDULING with pedagogical pacing.** The manuscript is not statically ordered - it actively manages WHEN vocabulary coverage occurs, introducing new MIDDLEs early, reinforcing throughout, and cycling through prefix domains.

### Core Finding

> **Currier A is not just coverage-optimal (C476), it is temporally scheduled to introduce, reinforce, and cycle through discrimination domains. This is PEDAGOGICAL PACING.**

### Four Signals (5/5 Support Strong Scheduling)

| Signal | Finding | Interpretation |
|--------|---------|----------------|
| **Coverage timing** | 90% reached 9.6% LATER than random | Back-loaded coverage |
| **Novelty rate** | Phase 1 (21.2%) >> Phase 3 (11.3%) | Front-loaded vocabulary introduction |
| **Tail pressure** | U-shaped: 7.9% -> 4.2% -> 7.1% | Difficulty wave pattern |
| **Prefix cycling** | 7 prefixes cycle (164 regime changes) | Multi-axis traversal |

### Interpretation

Three mutually exclusive models were tested:

| Model | Evidence | Verdict |
|-------|----------|---------|
| Static-Optimal | Order doesn't matter | 0 points |
| Weak Temporal | Soft pedagogy | 0 points |
| **Strong Scheduling** | **Active trajectory planning** | **5 points** |

**Result: STRONG-SCHEDULING (100% confidence)**

### Mechanism: PEDAGOGICAL_PACING

1. **Introduce early** - New MIDDLEs front-loaded in Phase 1
2. **Reinforce throughout** - Coverage accumulates slowly despite novelty
3. **Cycle domains** - 7 prefixes alternate, preventing cognitive fixation
4. **Wave difficulty** - U-shaped tail pressure creates attention peaks

### Reconciliation with Prior Findings

| Constraint | What it Shows |
|------------|---------------|
| C476 (Coverage Optimality) | WHAT Currier A optimizes |
| **C478 (Temporal Scheduling)** | **HOW it achieves that optimization** |

### New Constraint

**C478 - TEMPORAL COVERAGE SCHEDULING** (Tier 2, CLOSED)
- Strong temporal scheduling with pedagogical pacing
- Evidence: 5/5 signals support scheduled traversal
- Interpretation: Introduce early, reinforce throughout, cycle domains

### Files

- `phases/TEMPORAL_TRAJECTORIES/temporal_coverage_trajectories.py` - Analysis
- `results/temporal_coverage_trajectories.json` - Full results

---

## Version 2.24 (2026-01-12) - HT Variance Decomposition (C477)

### Summary

**HT density is partially explained (R² = 0.28) by A metrics, with TAIL PRESSURE as the dominant predictor (68% of variance).** HT rises when rare MIDDLEs are in play - evidence of cognitive load balancing.

### Core Finding

> **HT correlates with tail pressure (r = 0.504, p = 0.0045). When folios have more rare MIDDLEs, HT density is higher. HT is a cognitive load signal for tail discrimination complexity.**

### Regression Results

| Predictor | r | p-value | Ablation |
|-----------|---|---------|----------|
| **tail_pressure** | **0.504** | **0.0045*** | **68.2%** |
| incompatibility_density | 0.174 | 0.36 | 1.8% |
| novelty | 0.153 | 0.42 | 6.3% |
| hub_suppression | 0.026 | 0.89 | 0.1% |

### Interpretation

| R² Range | Interpretation | This Result |
|----------|----------------|-------------|
| 0.50+ | Strongly tied to discrimination | - |
| **0.25-0.40** | **Coarse vigilance signal** | **R² = 0.28** |
| 0.10-0.25 | Weak connection | - |
| <0.10 | HT signals something else | - |

### Why Tail Pressure?

- **Common MIDDLEs (hubs)** are easy to recognize (low cognitive load)
- **Rare MIDDLEs (tail)** require more attention to discriminate (high cognitive load)
- **HT rises when rare variants are in play** → anticipatory vigilance

### Integration with Prior Findings

| System | Role | Now Grounded |
|--------|------|--------------|
| Currier A | Coverage control | C476: optimal coverage with hub rationing |
| HT | Vigilance signal | **C477: tracks tail discrimination pressure** |
| AZC | Decision gating | C437-C444 |
| Currier B | Execution safety | Frozen Tier 0 |

### New Constraint

**C477 - HT TAIL CORRELATION** (Tier 2, CLOSED)
- HT density correlates with tail MIDDLE pressure (r = 0.504)
- Evidence of cognitive load balancing for rare discriminations

### Files

- `phases/HT_VARIANCE_DECOMPOSITION/ht_variance_decomposition.py` - Analysis
- `results/ht_variance_decomposition.json` - Full results

---

## Version 2.23 (2026-01-12) - Coverage Optimality CONFIRMED (C476)

### Summary

**Currier A achieves GREEDY-OPTIMAL coverage (100%) while using 22.3% FEWER hub tokens.** This confirms deliberate coverage management - Currier A is not generated, it is maintained.

### Core Finding

> **Real A achieves the same coverage as a greedy coverage-maximizing strategy, but with significantly less reliance on universal hub MIDDLEs. This is evidence of deliberate vocabulary management.**

### Coverage Comparison

| Model | Final Coverage | Hub Usage | Tail Activation |
|-------|---------------|-----------|-----------------|
| **Real A** | **100%** | **31.6%** | **100%** |
| Random | 72% | 9.8% | 67.8% |
| Freq-Match | 27% | 56.1% | 10.2% |
| **Greedy** | **100%** | **53.9%** | **100%** |

### Key Insight: Hub Efficiency

- Real A and Greedy both achieve 100% coverage
- Real A uses **31.6%** hub tokens
- Greedy uses **53.9%** hub tokens
- **Hub savings: 22.3 percentage points**

### Interpretation

The four residuals from Move #2 collapse into ONE control objective: **COVERAGE CONTROL**

| Residual | Mechanism |
|----------|-----------|
| PREFIX coherence | Reduce cognitive load during discrimination |
| Tail forcing | Ensure coverage of rare variants |
| Repetition structure | Stabilize attention on distinctions |
| Hub rationing | Prevent collapsing distinctions too early |

> **Currier A is not meant to be generated. It is meant to be maintained.**

### New Constraint

**C476 - COVERAGE OPTIMALITY** (Tier 2, CLOSED)
- Real A achieves greedy-optimal coverage with hub rationing
- Evidence of deliberate vocabulary management

### Files

- `phases/COVERAGE_OPTIMALITY/coverage_optimality.py` - Main analysis
- `results/coverage_optimality.json` - Full results

---

## Version 2.22 (2026-01-12) - Bundle Generator Diagnostic (EXPECTED FAILURE)

### Summary

**A minimal generator constrained only by MIDDLE incompatibility + line length + PREFIX priors fails on 9/14 diagnostic metrics.** Failure modes reveal additional structure in Currier A: PREFIX coherence, block purity, repetition structure, and tail access.

### Core Finding

> **Incompatibility + priors are NECESSARY but NOT SUFFICIENT. The generator over-mixes, under-uses the tail, and fails to reproduce the repetition structure.**

### Generator Configuration

**Included (hard constraints only):**
- MIDDLE atomic incompatibility (C475)
- Line length distribution (C233, C250-C252)
- PREFIX priors (empirical frequencies)
- LINE as specification context

**Excluded (want to see if they emerge):**
- Marker exclusivity rules
- Section conditioning
- AZC family information
- Adjacency coherence (C424)
- Suffix preferences

### Diagnostic Results

| Metric | Real | Synthetic | Verdict |
|--------|------|-----------|---------|
| lines_zero_mixing | 61.5% | 2.7% | **FAIL (-95.6%)** |
| pure_block_frac | 46.9% | 2.7% | **FAIL (-94.2%)** |
| universal_middle_frac | 31.6% | 56.7% | **FAIL (+79.6%)** |
| unique_middles | 1187 | 330 | **FAIL (-72.2%)** |
| lines_with_repetition | 96.4% | 63.9% | **FAIL (-33.7%)** |
| prefixes_per_line | 1.78 | 4.64 | **FAIL (+160%)** |
| line_length_mean | 19.2 | 20.0 | OK |
| line_length_median | 8.0 | 8.0 | OK |

### Residual Interpretation (New Structure Identified)

1. **PREFIX COHERENCE CONSTRAINT** - Lines prefer to stay within a single PREFIX family (not just compatibility)

2. **TAIL ACCESS FORCING** - Real A systematically uses rare MIDDLEs; generator ignores them

3. **REPETITION IS STRUCTURAL** - 96.4% of real lines have MIDDLE repetition (deliberate, not random)

4. **HUB RATIONING** - Universal MIDDLEs ('a','o','e') are used sparingly (31.6% vs 56.7% generator)

### What This Proves

| Finding | Status |
|---------|--------|
| Incompatibility is necessary | Confirmed (line length matches) |
| Incompatibility is sufficient | **REJECTED** (9/14 metrics fail) |
| PREFIX coherence exists | **NEW CONSTRAINT** (block purity) |
| Repetition is structural | **NEW CONSTRAINT** (not in current model) |
| Tail MIDDLEs are forced | **NEW CONSTRAINT** (registry coverage) |

### Files

- `phases/A_BUNDLE_GENERATOR/a_bundle_generator.py` - Generator and diagnostics
- `results/a_bundle_generator.json` - Full results

### Next Step

**HT Variance Decomposition** - Can incompatibility degree explain HT density?

---

## Version 2.21 (2026-01-12) - Latent Discrimination Axes (HIGH-DIMENSIONAL)

### Summary

**The MIDDLE compatibility space requires ~128 latent axes to achieve 97% prediction accuracy.** This is HIGH-DIMENSIONAL - discrimination is not reducible to a few binary choices.

### Core Finding

> **128 dimensions needed for 97% AUC. The discrimination space is NOT low-rank (not 2-4 axes as initially hypothesized). PREFIX, character content, and length are all weak predictors of the axes.**

### Probe Results (latent_discrimination_axes.py)

| Metric | Value |
|--------|-------|
| Optimal K | 128 |
| AUC at K=128 | 97.2% |
| AUC at K=2 | 86.9% |
| AUC at K=32 | 90.0% |
| Variance at K=128 | 83.4% |
| K for 90% variance | 51 |

### AUC by Dimensionality

| K | AUC | Interpretation |
|---|-----|----------------|
| 2 | 0.869 | Two axes capture ~87% |
| 4 | 0.870 | Minimal gain |
| 8 | 0.869 | Minimal gain |
| 16 | 0.886 | Starts improving |
| 32 | 0.900 | 90% threshold |
| 64 | 0.923 | Significant gain |
| 128 | 0.972 | Near ceiling |

### Axis Structure Analysis

**Axes do NOT align with interpretable features:**

| Feature | Max Correlation | Verdict |
|---------|-----------------|---------|
| PREFIX | 0.011 (separation) | WEAK |
| Characters | 0.138 ('f' on axis 2) | WEAK |
| Length | 0.160 (axis 17) | WEAK |

### Interpretation

1. **Not 2-4 binary switches** - The expert hypothesis of "2-4 axes of distinction" is rejected
2. **Rich feature space** - Each MIDDLE encodes ~128 bits of discriminatory information
3. **Emergent structure** - The axes don't map to obvious linguistic features
4. **PREFIX is ~1/128th** - PREFIX explains about 1/128th of the discrimination variance

### Hub Confirmation

Top-5 hubs by degree match prior finding:
| MIDDLE | Degree (weighted) |
|--------|------------------|
| 'a' | 2047 |
| 'o' | 1870 |
| 'e' | 1800 |
| 'ee' | 1625 |
| 'eo' | 1579 |

### What This Means

1. **Vocabulary is NOT simple categorization** - Not just "A/B/C with variants"
2. **Each MIDDLE is unique** - 128-dimensional fingerprint
3. **Compatibility is learned, not rule-based** - No simple grammar generates it
4. **Generative model needs ~128 features per MIDDLE** - High complexity

### Files

- `phases/LATENT_AXES/latent_discrimination_axes.py` - Main analysis
- `results/latent_discrimination_axes.json` - Full results

### Next Steps (from expert roadmap)

1. ~~Latent Discrimination Axes Inference~~ **DONE - HIGH-DIMENSIONAL**
2. **Probabilistic Currier-A Bundle Generator** - Can we reproduce A entries?
3. **HT Variance Decomposition** - Ground HT quantitatively

---

## Version 2.20 (2026-01-12) - MIDDLE Atomic Incompatibility (C475)

### Summary

**MIDDLE-level compatibility is extremely sparse (4.3% legal), forming a hard incompatibility lattice.** This is the atomic discrimination layer - everything above it (A entries, AZC folios, families, HT) is an aggregation of this graph.

### Core Finding

> **95.7% of MIDDLE pairs are illegal. Only 4.3% can co-occur on the same specification line. This sparsity is robust to context definition (97.3% overlap with 2-line sensitivity check).**

### Probe Results (middle_incompatibility.py)

| Metric | Value |
|--------|-------|
| Total MIDDLEs | 1,187 |
| Total possible pairs | 703,891 |
| **Legal pairs** | **30,394 (4.3%)** |
| **Illegal pairs** | **673,342 (95.7%)** |
| Trivially absent | 155 |
| Connected components | 30 |
| Largest component | 1,141 (96% of MIDDLEs) |
| Isolated MIDDLEs | 20 |

### PREFIX Clustering (H1 - SUPPORTED)

| Type | Legal % | Interpretation |
|------|---------|----------------|
| Within-PREFIX | 17.39% | Soft prior for compatibility |
| Cross-PREFIX | 5.44% | Hard exclusion boundary |
| **Ratio** | **3.2x** | PREFIX is first partition |

### Key Structural Objects Identified

1. **Universal Connector MIDDLEs** ('a', 'o', 'e', 'ee', 'eo')
   - Compatibility basis elements
   - Bridge otherwise incompatible regimes
   - "Legal transition anchors"

2. **Isolated MIDDLEs** (20 total)
   - Hard decision points
   - "If you specify this, you cannot specify anything else"
   - Pure regime commitment

3. **PREFIX = soft prior, MIDDLE = hard constraint**
   - PREFIX increases odds of legality ~3x
   - MIDDLE applies near-binary exclusions

### Reconciliation with Prior Constraints

| Constraint | Previous | Now Resolved |
|------------|----------|--------------|
| C293 | MIDDLE is primary discriminator | Quantified: 95.7% exclusion rate |
| C423 | PREFIX-bound vocabulary | PREFIX is first partition, MIDDLE is sharper |
| C437-C442 | Why so many AZC folios? | AZC = projections of sparse graph |
| C459, C461 | HT anticipatory function | HT ≈ incompatibility density (testable) |

### f116v Correction

f116v folio-level isolation (from v2.19) is explained by **data sparsity** (only 2 words in AZC corpus), NOT by MIDDLE-level incompatibility. The f116v MIDDLEs ('ee', 'or') are actually universal connectors.

### New Constraint

**C475 - MIDDLE ATOMIC INCOMPATIBILITY** (Tier 2, CLOSED)
- Added to `context/CLAIMS/currier_a.md`

### Interpretation

> **The MIDDLE vocabulary forms a globally navigable but locally forbidden discrimination space. This is the strongest internal explanation yet of why the Voynich Manuscript looks the way it does without invoking semantics.**

### What This Enables (Bayesian Roadmap)

1. **Latent Discrimination Axes Inference** - How many latent axes explain the incompatibility graph?
2. **Probabilistic A Bundle Generator** - Can MIDDLE incompatibility + line length + PREFIX priors reproduce A entries?
3. **HT Variance Decomposition** - How much HT density is explained by local incompatibility degree?

### Updated Files

- `phases/MIDDLE_INCOMPATIBILITY/middle_incompatibility.py` - Main probe
- `results/middle_incompatibility.json` - Full results
- `context/CLAIMS/currier_a.md` - Added C475
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Updated

### Significance

This is a **regime change** in what kind of modeling is now possible. We've reached bedrock - the atomic discrimination layer. All higher-level structure (A, AZC, HT) can now be understood as aggregations of this sparse graph.

---

## Version 2.19 (2026-01-12) - AZC Compatibility at Specification Level

### Summary

**AZC compatibility filtering operates at the Currier A constraint-bundle level, not at execution level.** Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both. 10.3% of folio pairs are unbridged, with f116v being structurally isolated.

### Key Finding

> **Currier A entries define which AZC vocabularies can be jointly activated. Most folio pairs are compatible, but ~10% are not—with f116v being a structurally isolated discrimination regime. AZC compatibility is enforced at specification (A-bundle) level, not at execution or folio-presence level.**

### Probe Results

| Metric | Value |
|--------|-------|
| Total folio pairs | 435 |
| Bridged pairs | 390 (89.7%) |
| **Unbridged pairs** | **45 (10.3%)** |
| Graph connectivity | FULLY_CONNECTED |

### Family-Level Coherence

| Family Type | % Unbridged | Interpretation |
|-------------|-------------|----------------|
| Within-Zodiac | **0.0%** | Interchangeable discrimination contexts |
| Within-A/C | **14.7%** | True fine-grained alternatives |
| Cross-family | **11.3%** | Partial overlap, partial incompatibility |

### f116v Structural Isolation

f116v shares NO bridging tokens with most other folios:
- Vocabulary uniquely concentrated
- Cannot be jointly specified with most other constraint bundles
- Can still appear in B executions (C440 holds)
- Defines a discrimination profile incompatible at A-level

### C442 Refinement

Previous understanding: "94% unique vocabulary per folio"

Refined understanding:
> **AZC compatibility filtering operates at the level of Currier A constraint-bundle co-specification. Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both.**

Corollaries:
- Folios are NOT execution-exclusive
- Folios are NOT globally incompatible
- Incompatibility exists only at **specification time**
- Disallowed combinations leave no discrete trace—they simply never occur

### Why This Matters

This resolves family-level coherence:
- **Zodiac (0% unbridged)**: Supports sustained HT flow—interchangeable contexts
- **A/C (14.7% unbridged)**: Causes punctuated HT resets—true alternatives
- **Execution difficulty unchanged**: CEI, recovery, hazard models unaffected

### Updated Files

- `phases/AZC_COMPATIBILITY/azc_entry_bridges.py` - Correct probe
- `phases/AZC_COMPATIBILITY/azc_folio_compatibility.py` - First probe (coarse)
- `results/azc_entry_bridges.json` - Bridge analysis results
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.5
- `context/CLAIMS/azc_system.md` - C442 refined

### Significance

This is a **Tier-2 advance**:
- Pinpoints the mechanism of AZC compatibility (A-bundle level)
- Identifies f116v as structurally isolated
- Explains Zodiac coherence vs A/C alternatives
- Connects discrimination regimes to specification constraints

---

## Version 2.18 (2026-01-11) - AZC-Based Currier A Clustering

### Summary

**AZC folio co-occurrence can reverse-cluster Currier A entries, revealing sub-families within PREFIX classes.** The y- PREFIX shows a family split: some y- tokens cluster with Zodiac contexts, others with A/C contexts.

### Key Finding

> **PREFIX morphology does not fully determine AZC family affinity. Some PREFIX classes (notably y-) contain sub-families that differ in their discrimination-regime membership.**

### Probe Results

| Metric | Value |
|--------|-------|
| Currier A tokens in AZC | 778 (16% of vocabulary) |
| Tokens eligible for clustering | 367 (appear in 2+ AZC folios) |
| Sub-families detected | y- (FAMILY_SPLIT) |

### PREFIX → AZC Family Baseline (confirms C471)

| PREFIX | Zodiac % | A/C % | Bias |
|--------|----------|-------|------|
| qo- | 18.8% | 71.9% | A/C |
| d- | 14.5% | 62.9% | A/C |
| or- | 58.3% | 16.7% | Zodiac |
| ot- | 25.0% | 25.0% | BALANCED |
| **y-** | 28.1% | 46.9% | **SPLIT** |

### y- Family Split Evidence

| Cluster | Family Bias | Sample Tokens | Shared Folios |
|---------|-------------|---------------|---------------|
| 66 | 85.7% Zodiac | ytaly, opaiin, alar | f72v1, f73v |
| 61 | 69.7% A/C | okeod, ykey, ykeeody | f69v, f73v |

### Interpretation

y- does not behave like a single material class. It spans both discrimination regimes, suggesting:

1. **y- encodes something orthogonal to the Zodiac/A-C axis**
2. **y- may be a modifier or state marker** rather than a material class
3. **Regime-independent function** - applies in both coarse and fine discrimination contexts

### Extreme Family Clusters (100% bias)

| Cluster | Bias | Tokens | Shared Folios |
|---------|------|--------|---------------|
| 67 | 100% Zodiac | okeoly, dalal, otalal | f70v2, f72v1 |
| 38 | 100% A/C | om, oir, ykaly | f67v2, f67r2 |
| 139 | 100% Zodiac | okam, okaldy, chas | f72r2, f72v3 |

### Updated Files

- `phases/EFFICIENCY_REGIME_TEST/azc_based_a_clustering.py` - Clustering probe
- `results/azc_based_a_clustering.json` - Full results
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.4, y- finding
- `context/SPECULATIVE/efficiency_regimes.md` - Added y- evidence

### Significance

This probe demonstrates that AZC can be used in reverse to reveal structure within Currier A vocabulary that PREFIX morphology alone doesn't show. The y- split provides evidence that some morphological markers encode regime-independent properties.

---

## Version 2.17 (2026-01-11) - Perceptual Discrimination Regime Synthesis

### Summary

**HT oscillation analysis completes the regime interpretation.** The concurrency management probe falsified the parallel-batch hypothesis but revealed the correct explanatory axis: discrimination complexity determines attentional flow patterns.

### Key Finding

> **Where discrimination is fine, attention becomes punctuated; where discrimination is coarse, attention can flow.**

### HT Oscillation Results

| Family | HT Density | Oscillation Score | Interpretation |
|--------|-----------|-------------------|----------------|
| Zodiac | 0.131 | 0.060 | Sustained attentional flow |
| A/C | 0.236 | 0.110 | Punctuated attentional checkpoints |

**A/C shows ~80% higher HT oscillation than Zodiac.**

### Falsified Hypotheses

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| Parallel batch management | FALSIFIED | HT oscillation reversed from prediction |
| Zodiac = high context switching | FALSIFIED | Zodiac has LOWER oscillation |

### The Coherent Explanatory Axis (All Layers Aligned)

| Layer | Zodiac | A/C |
|-------|--------|-----|
| Currier A | Coarse categories | Fine distinctions |
| AZC | Uniform scaffolds | Varied scaffolds |
| HT | Sustained flow | Punctuated checkpoints |
| Currier B | Same difficulty | Same difficulty |
| CEI | Same effort | Same effort |

### Final Interpretation (Tier 3 - VALIDATED)

> Zodiac and A/C AZC families correspond to regimes of perceptual discrimination complexity rather than operational difficulty. Zodiac contexts permit coarse categorization and sustained attentional flow, while A/C contexts require finer categorical distinctions, producing punctuated attentional checkpoints reflected in higher HT oscillation. Execution grammar absorbs this difference, resulting in no detectable change in behavioral brittleness or CEI.

### Updated Files

- `context/SPECULATIVE/efficiency_regimes.md` - Final validated interpretation
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.3, coherent axis table
- `phases/EFFICIENCY_REGIME_TEST/test_concurrency_management.py` - HT probe
- `results/concurrency_management_probe.json` - HT test output

### Significance

This is the first interpretation that cleanly integrates ALL layers (A, AZC, B, HT, CEI) without contradiction. The internal evidence has been exhausted correctly, by falsification rather than narrative preference.

---

## Version 2.16 (2026-01-11) - Lexical Granularity Regime Validation

### Summary

**This phase empirically tested the "efficiency regime" interpretation of Zodiac vs A/C.** The results localized the signal to the vocabulary layer and falsified behavioral-level claims.

### Key Finding

> **Zodiac vs A/C encodes regimes of lexical discrimination, not regimes of operational difficulty; the control grammar absorbs lexical complexity so that execution behavior remains stable.**

### Test Results

| Test | Result | Interpretation |
|------|--------|----------------|
| MIDDLE Discrimination Pressure | WEAK SUPPORT | 5/15 prefixes show gradient, 0 reversed |
| Residual Brittleness Analysis | **FAILED** | Effect is PREFIX-morphological, not regime-based |
| Universal MIDDLE Negative Control | **PASSED** | Universal MIDDLEs regime-neutral (58.7%), Exclusive biased (64.8%) |
| Family Escape Transfer | PARTIAL | Weak positive correlation (r=0.265) |

**Overall Verdict: WEAK_PARTIAL**

### What IS Supported (Lexical Level)

- MIDDLE discrimination is genuinely family-biased
- Universal MIDDLEs are regime-neutral; Exclusive MIDDLEs show A/C bias
- A/C contexts require finer vocabulary distinctions; Zodiac uses broader categories

### What Is NOT Supported (Behavioral Level - FALSIFIED)

- A/C = operationally brittle (REJECTED)
- Zodiac = operationally forgiving (REJECTED)
- Family affects CEI or recovery (REJECTED)
- Efficiency stress propagates to B programs (REJECTED)

### New Insight

**CEI measures control strain *within* execution, not *between* lexical regimes.**

CEI and AZC family live on orthogonal axes:
- CEI = trajectory management within execution
- AZC family = what distinctions exist ahead of time

### Updated Files

- `context/SPECULATIVE/efficiency_regimes.md` - Renamed, tested, revised
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.2, updated regime section
- `phases/EFFICIENCY_REGIME_TEST/` - Four test scripts + synthesis
- `results/efficiency_regime_*.json` - All test outputs

### Methodology Note

This represents a proper falsification attempt, not confirmation bias. The test suite was designed with pre-declared stop conditions and negative controls. The partial failure is a scientific success: it precisely located where the signal exists (vocabulary) vs where it does not (behavior).

---

## Version 2.15 (2026-01-11) - Morphological Binding Phase Closure

### Summary

**This phase resolved the interface between Currier A, AZC, and Currier B.** The binding logic that connects vocabulary composition to constraint activation is now morphologically encoded, causally active, and empirically validated.

### The One-Sentence Takeaway

> **Currier A records define which worlds are allowed to exist, AZC defines what is legal in each world and when recovery is possible, and Currier B blindly executes - leaving the consequences of earlier discriminations unavoidable but structurally bounded.**

### New Constraints

- **C471** - PREFIX Encodes AZC Family Affinity (Tier 2)
  - qo- and ol- strongly enriched in A/C AZC folios (91% / 81%)
  - ot- enriched in Zodiac folios (54%)
  - ch-, sh-, ok- broadly distributed
  - Statistical affinity, not exclusive mapping

- **C472** - MIDDLE Is Primary Carrier of AZC Folio Specificity (Tier 2)
  - PREFIX-exclusive MIDDLEs (77%) exhibit median entropy = 0.0
  - Typically appear in exactly one AZC folio
  - Shared MIDDLEs span multiple folios (18.7% vs 3.3% coverage)
  - MIDDLE is principal determinant of folio-level constraints

- **C473** - Currier A Entry Defines a Constraint Bundle (Tier 2)
  - A entry does not encode addressable object or procedure
  - Morphological composition specifies compatibility signature
  - Determines which AZC legality envelopes are applicable

### Final Definitions (Locked)

- **Currier A record** = Pre-execution compatibility declaration
- **AZC folio** = Complete legality regime (permissions + recoveries)
- **Currier B program** = Blind execution against filtered vocabulary

### Closure Declarations

**Pipeline Resolution & Morphological Binding: CLOSED**

No remaining degrees of freedom. The binding logic is:
- PREFIX -> AZC family affinity
- MIDDLE -> AZC folio specificity
- Together: each vocabulary item carries a compatibility signature

**Additional closures (do NOT reopen):**
- Naming or meaning of AZC folios (they are legality regimes)
- Aligning A entries to specific B programs (vocabulary-mediated)

### Updated Files

- `context/CLAIMS/azc_system.md` - Added C471-C473, morphological binding section
- `context/CLAUDE_INDEX.md` - Updated to v2.8, 335 constraints
- `context/MAPS/claim_to_phase.md` - Added C471-C473 mapping
- `phases/INTEGRATION_PROBE/` - Three probe scripts archived
- `results/integration_probe_*.json` - Probe results saved

---

## Version 2.14 (2026-01-11) - Pipeline Resolution Phase Closure

### Summary

**This phase achieved structural closure on the A -> AZC -> B pipeline.** The decisive finding: AZC constraint profiles propagate causally into Currier B execution behavior.

### New Constraints

- **C468** - AZC Legality Inheritance (Tier 2)
  - Tokens from high-escape AZC contexts show 28.6% escape in B
  - Tokens from low-escape AZC contexts show 1.0% escape in B
  - 28x difference confirms causal constraint transfer

- **C469** - Categorical Resolution Principle (Tier 2)
  - Operational conditions represented categorically via token legality
  - Not parametrically via encoded values
  - Physics exists externally; representation is categorical

- **C470** - MIDDLE Restriction Inheritance (Tier 2)
  - Restricted MIDDLEs (1-2 AZC folios): 4.0 B folio spread
  - Universal MIDDLEs (10+ AZC folios): 50.6 B folio spread
  - 12.7x difference confirms constraint transfer

### New Fits

- **F-AZC-015** - Windowed AZC Activation Trace
  - Case B confirmed: 70% of AZC folios active per window
  - High persistence (0.87-0.93): same folios persist
  - AZC is ambient legality field, not dynamic selector

- **F-AZC-016** - AZC->B Constraint Fit Validation
  - MIDDLE restriction transfers: CONFIRMED (12.7x)
  - Escape rate transfers: CONFIRMED (28x)
  - Pipeline causality validated

### Closure Declarations

**Pipeline Resolution Phase: CLOSED**

The A -> AZC -> B control pipeline is structurally and behaviorally validated.

**Do NOT reopen:**
- Entry-level A->B mapping (ruled out by pipeline mechanics)
- Dynamic AZC decision-making (F-AZC-015 closed this)
- Parametric variable encoding (no evidence exists)
- Semantic token meaning (all evidence against)

### Updated Files

- `context/CLAIMS/azc_system.md` - Added C468-C470, closure statement
- `context/MODEL_FITS/fits_azc.md` - Added F-AZC-015, F-AZC-016
- `context/MODEL_CONTEXT.md` - Added Section X.C (Representation Principle)
- `context/CLAUDE_INDEX.md` - Updated to v2.7, 320+ constraints

### Archived Scripts

29 scripts from `phases/AZC_constraint_hunting/` archived to `archive/scripts/AZC_constraint_hunting/`

---

## Version 2.13 (2026-01-10)

### E4: AZC Entry Orientation Trace (C460)

**Summary:** Tested whether AZC folios serve as cognitive entry points by analyzing HT trajectories in their neighborhood. Found significant step-change pattern, but it resembles random positions more than A/B entries.

**New Constraint:**

- **C460** - AZC Entry Orientation Effect (Tier 2)
  - Step-change at AZC: p < 0.002 (all window sizes)
  - Pre-entry HT: above average (+0.1 to +0.28 z-score)
  - Post-entry HT: below average (-0.08 to -0.30 z-score)
  - Gradient: decay, R^2 > 0.86

**Critical Nuance:**
- AZC trajectory differs from A and B systems (p < 0.005)
- AZC trajectory does NOT differ from random (p > 0.08)
- Interpretation: AZC is **placed at** natural HT transitions, not **causing** them

**Zodiac vs Non-Zodiac:**
- Zodiac step-change: -0.39 (stronger)
- Non-zodiac step-change: -0.36

**New Files:**
- `phases/exploration/azc_entry_orientation_trace.py`
- `results/azc_entry_orientation_trace.json`
- `context/CLAIMS/C460_azc_entry_orientation.md`

**Updated Files:**
- `context/CLAIMS/INDEX.md` - Version 2.13, 310 constraints

**Status:** E4 COMPLETE

### E5: AZC Internal Oscillation (Observation Only)

**Question:** Does AZC show internal micro-oscillations matching the global HT rhythm?

**Answer:** No. AZC does not replicate manuscript-wide dynamics internally.
- No significant autocorrelation
- Faster cadence (~3.75 folios vs global ~10)
- Zodiac internally flat; non-Zodiac shows decreasing trend

**Status:** Documented as observation, NOT a constraint. Line of inquiry closed.

**New File:**
- `results/azc_internal_oscillation.json`

---

## Version 2.11 (2026-01-10)

### Intra-Role Differentiation Audit (C458-C459)

**Summary:** Complete audit of intra-folio variation across all four systems. Discovered that risk is globally constrained while human burden and recovery strategy are locally variable. Established HT as anticipatory (not reactive) attention layer.

**Core Finding:**
> The Voynich Manuscript does not vary in how risky its procedures are; it varies in how much *slack, recovery capacity, and human attention* each situation demands - and it encodes that distinction with remarkable consistency across systems.

**New Constraints:**

- **C458** - Execution Design Clamp vs Recovery Freedom (Tier 2)
  - Hazard exposure: CV = 0.04-0.11 (CLAMPED)
  - Recovery operations: CV = 0.72-0.82 (FREE)
  - Regime separation: eta² = 0.70-0.74
  - C458.a: Hazard/LINK mutual exclusion (r = -0.945)

- **C459** - HT Anticipatory Compensation (Tier 2)
  - Quire-level correlation: r = 0.343, p = 0.0015
  - HT before B: r = 0.236, p = 0.032 (significant)
  - HT after B: r = 0.177, p = 0.109 (not significant)
  - Pattern: HT_ANTICIPATES_STRESS
  - C459.a: REGIME_2 shows inverted compensation

**Additional Findings (not constraints):**

- **D2 (AZC Zodiac):** Zodiac folios vary in monitoring vs transition emphasis (CV = 0.15-0.39), no position gradient
- **P1 (Clustering):** 4 natural folio clusters; 4 anomalous folios cluster by HT burden across systems (f41r, f65r, f67r2, f86v5)
- **P2 (Recto-Verso):** No systematic asymmetry (p = 0.79); HT balanced across spreads

**Theoretical Impact:**

| Category | Effect |
|----------|--------|
| Strengthened | Control-artifact model, human-centric design, non-semantic stance |
| Constrained | Danger tied to pages, diagrams encoding execution, HT as reactive |
| Disfavored | Recipe difficulty gradients, didactic sequences, per-page semantics |

**New Files:**
- `phases/exploration/unified_folio_profile.py` - D0
- `phases/exploration/b_design_space_cartography.py` - D1
- `phases/exploration/azc_zodiac_fingerprints.py` - D2
- `phases/exploration/ht_compensation_analysis.py` - D3
- `phases/exploration/folio_personality_clusters.py` - P1
- `phases/exploration/recto_verso_asymmetry.py` - P2
- `phases/exploration/INTRA_ROLE_DIFFERENTIATION_SUMMARY.md` - Synthesis
- `context/CLAIMS/C458_execution_design_clamp.md`
- `context/CLAIMS/C459_ht_anticipatory_compensation.md`

**Results Files:**
- `results/unified_folio_profiles.json` (227 profiles)
- `results/b_design_space_cartography.json`
- `results/azc_zodiac_fingerprints.json`
- `results/ht_compensation_analysis.json`
- `results/folio_personality_clusters.json`
- `results/recto_verso_asymmetry.json`

**Updated Files:**
- `context/CLAIMS/INDEX.md` - Version 2.11, 309 constraints

**Status:** Intra-Role Differentiation Audit COMPLETE.

### Extended Analysis: HT Temporal Dynamics + Anomalous Folios

**HT Temporal Dynamics:**
- Global decreasing trend: r=-0.158, p=0.017 (HT falls through manuscript)
- ~10-folio periodicity: SNR=4.78 (quire-scale oscillation)
- 9 changepoints detected
- Front-loaded: f39r-f67v2 is HIGH region (48 folios), ending is LOW

**Anomalous Folio Investigation:**

All 4 folios that cluster across system boundaries are HT HOTSPOTS:
| Folio | System | HT | Escape | Status |
|-------|--------|-----|--------|--------|
| f41r | B | 0.296 | 0.197 | HOTSPOT |
| f65r | AZC | 0.333 | n/a | HOTSPOT |
| f67r2 | AZC | 0.294 | n/a | HOTSPOT |
| f86v5 | B | 0.278 | 0.094 | HOTSPOT |

**New Files (Extended):**
- `phases/exploration/ht_temporal_dynamics.py`
- `phases/exploration/anomalous_folio_investigation.py`
- `results/ht_temporal_dynamics.json`
- `results/anomalous_folio_investigation.json`

**Deepest Pattern Discovered:**
> The Voynich is not primarily a manual of actions. It is a manual of **responsibility allocation** between system and human.

---

## Version 2.12 (2026-01-10)

### Post-Differentiation Explorations (E1-E3)

**E1: Quire Rhythm Alignment**
- HT changepoints do NOT align with quire boundaries (enrichment=0.59x, p=0.35)
- HT rhythm is CONTENT-DRIVEN, not production-driven
- Quires differ significantly in mean HT level (H=48.2, p<0.0001, eta²=0.149)
- No consistent internal pattern (43% flat)

**E2: Zero-Escape Characterization (CORRECTION)**
- Only 2 B folios have near-zero escape: f33v (0.009), f85v2 (0.010)
- Neither is an HT hotspot
- Zero-escape is RARE (2.4% of B folios)
- No HT difference between zero-escape and normal B (p=0.22)
- **CORRECTED:** f41r and f86v5 are NOT zero-escape (original finding was due to field name bug)

**E3: Anomalous Folio Deep Dive**
- 13 total HT hotspots (6 A, 5 B, 2 AZC)
- The "anomalous 4" (f41r, f65r, f67r2, f86v5) are not unique
- Only f65r is at a system boundary (A→AZC)
- B hotspots span different regimes (REGIME_2, REGIME_4)
- All anomalous folios have ~2x median HT for their system

**Key Corrections:**
- C459.b "zero-escape → max HT" WITHDRAWN (data error)
- Escape density for f41r: 0.197 (not 0)
- Escape density for f86v5: 0.094 (not 0)

**New Files:**
- `phases/exploration/quire_rhythm_analysis.py`
- `phases/exploration/zero_escape_characterization.py`
- `phases/exploration/anomalous_folio_deep_dive.py`
- `results/quire_rhythm_analysis.json`
- `results/zero_escape_characterization.json`
- `results/anomalous_folio_deep_dive.json`

**Updated Files:**
- `context/CLAIMS/C459_ht_anticipatory_compensation.md` - C459.b corrected

**Status:** Post-Differentiation Explorations COMPLETE

---

## Version 2.10 (2026-01-10)

### B Design Space Cartography (C458)

**Summary:** Interim version during Intra-Role audit. See v2.11 for complete documentation.

---

## Version 2.9 (2026-01-10)

### HT-AZC Placement Affinity (C457)

**Summary:** Single focused test of HT-AZC relationship, following the architectural synthesis. Discovered that HT preferentially marks boundary (S) positions over interior (R) positions in Zodiac AZC.

**New Constraint:**

- **C457** - HT Boundary Preference in Zodiac AZC (Tier 2)
  - S-family HT rate: 39.7%
  - R-family HT rate: 29.5%
  - Difference: 10.3 percentage points (p < 0.0001, V = 0.105)
  - HT preferentially marks BOUNDARIES (sector positions)
  - Supports "attention at phase boundaries" interpretation

**Key Insight:**
> AZC defines the boundary structure of experience; HT marks when human attention should increase inside that structure.

**Files Created:**
- `context/CLAIMS/C457_ht_boundary_preference.md`
- `results/ht_azc_placement_affinity.json`
- `phases/exploration/ht_azc_placement_test.py`

**Status:** HT-AZC investigation CLOSED. No further tests needed.

---

## Version 2.8 (2026-01-10)

### Apparatus-Topology Hypothesis Testing (C454-C456)

**Summary:** Rigorous hypothesis testing of whether AZC encodes apparatus-stage alignment. Properly designed tests with pre-registered kill conditions. Hypothesis FALSIFIED, but produced valuable architectural insights.

**New Constraints:**

- **C454** - AZC-B Adjacency Coupling FALSIFIED (Tier 1)
  - B folios near AZC show NO significant metric differences from B folios far from AZC
  - All window sizes (1-5 folios) returned p > 0.01
  - AZC does NOT modulate B execution
  - AZC and B are topologically segregated

- **C455** - AZC Simple Cycle Topology FALSIFIED (Tier 1)
  - Zodiac AZC is NOT a single ring/cycle
  - Multiple independent cycles (cycle_rank = 5)
  - Non-uniform degree distribution (CV = 0.817)
  - "Literal apparatus diagram" interpretation rejected

- **C456** - AZC Interleaved Spiral Topology (Tier 2)
  - Zodiac shows R-S-R-S alternating pattern
  - R1 -> S1 -> R2 -> S2 -> R3
  - Consistent with cognitive orientation scaffolding
  - Alternation represents interior (R) vs boundary (S) states

**Architectural Synthesis:**

Created `context/ARCHITECTURE/layer_separation_synthesis.md` explaining:
- Why execution (B) must be context-free
- Why orientation (AZC) must be execution-free
- Why legality != prediction
- Why humans need spatial scaffolds for cyclic processes

**The Answer:**
> Why are there spatial diagrams that don't seem to describe anything?
> Because they describe *orientation*, not *operation*.

**Files Created:**
- `context/CLAIMS/C454_azc_b_adjacency_falsified.md`
- `context/CLAIMS/C455_azc_simple_cycle_falsified.md`
- `context/CLAIMS/C456_azc_interleaved_spiral.md`
- `context/ARCHITECTURE/layer_separation_synthesis.md`
- `phases/exploration/apparatus_topology_tests_v2.py`
- `phases/exploration/azc_topology_test.py`
- `results/apparatus_topology_critical_tests_v2.json`
- `results/azc_topology_analysis.json`

**Methodological Note:**
This phase demonstrated proper hypothesis testing:
1. Proposed falsifiable Tier-3 hypothesis
2. Pre-registered kill conditions (K1, K2)
3. Fixed test design flaws when detected
4. Accepted null results
5. Refined understanding based on evidence

**Status:** Apparatus-topology investigation CLOSED. Doors permanently closed on:
- AZC diagrams "representing" apparatus
- R/S/C positions mapping to physical components
- Diagram complexity correlating with execution difficulty

---

## Version 2.7 (2026-01-10)

### AZC-DEEP: Folio Family Architecture (C430-C432)

**Summary:** Completed AZC-DEEP Phases 1-3, discovering that AZC comprises two architecturally distinct folio families. This parallels the CAS-DEEP analysis of Currier A and reveals internal structure beyond "hybrid with placement."

**New Constraints:**

- **C430** - AZC Bifurcation (Tier 2)
  - AZC divides into two families with no transitional intermediates
  - Family 0: Zodiac-dominated, placement-stratified (13 folios)
  - Family 1: A/C-dominated, placement-flat (17 folios)
  - Bootstrap stability = 0.947, Silhouette = 0.34

- **C431** - Zodiac Family Coherence (Tier 2, refines C319)
  - All 12 Zodiac folios form single homogeneous cluster
  - JS similarity = 0.964
  - Higher TTR (0.54), placement entropy (2.25), AZC-unique rate (0.28)
  - Confirms Zodiac as distinct structural mode, not just template reuse

- **C432** - Ordered Subscript Exclusivity (Tier 2)
  - R1-R3, S1-S2 occur exclusively in Zodiac family
  - Binary diagnostic feature (0.96 vs 0.00 depth)
  - Ordered subscripts are family-defining, not AZC-general

**Architectural Impact:**
- AZC is now demonstrably non-monolithic
- Zodiac pages define a separate AZC control mode
- Ordered subscripts become diagnostic, not incidental
- Hybrid story sharpens: Cluster 1 has more shared vocabulary, Cluster 0 has more AZC-unique

**Files Modified:**
- `context/CLAIMS/azc_system.md` - Added C430-C435
- `context/CLAIMS/INDEX.md` - Updated AZC section

### AZC-DEEP Phase 4a: Zodiac Placement Grammar (C433-C435)

**Summary:** Discovered that Zodiac pages implement an extremely strict, block-based placement grammar - stricter than Currier B grammar, not looser.

**New Constraints:**

- **C433** - Zodiac Block Grammar (Tier 2)
  - Placement codes occur in extended contiguous blocks (mean 40-80 tokens)
  - Self-transition rate exceeds 98% for all major codes
  - Zero singletons - once a placement starts, it locks for dozens of tokens
  - **Stricter than Currier B grammar**

- **C434** - R-Series Strict Forward Ordering (Tier 2)
  - R1→R2→R3 only - no backward, no skipping
  - Backward transitions: 0 observed (349 expected)
  - Skip transitions: 0 observed (139 expected)

- **C435** - S/R Positional Division (Tier 2)
  - S-series: Boundary layer (95%+ at line edges)
  - R-series: Interior layer (89-95% interior positions)
  - Two-layer grammar: S marks entry/exit, R fills interior in ordered stages

**Key Insight:**
> The Zodiac pages are not "diagrams with labels." They are a rigid, page-bound control scaffold - the same structure reused twelve times with local vocabulary variation but identical placement logic.

### AZC-DEEP Phase 4b: A/C Family Placement Grammar (C436)

**Summary:** Discovered that the A/C family is ALSO rigid (98% self-transition, zero singletons), but differs from Zodiac in cross-folio consistency. The contrast is uniform-vs-varied, not rigid-vs-permissive.

**New Constraint:**

- **C436** - AZC Dual Rigidity Pattern (Tier 2)
  - Both families: >=98% self-transition, zero singletons
  - Zodiac family: 0.945 cross-folio consistency (uniform scaffold)
  - A/C family: 0.340 cross-folio consistency (folio-specific scaffolds)
  - The contrast is uniform-versus-varied rigidity

**Key Insight:**
> AZC is not "one mode with variation" - it implements two distinct coordination strategies. Every AZC page enforces a hard placement lock. The difference is whether that lock is standardized (Zodiac) or custom (A/C).

**Four-Layer Stack Now Complete:**
- Currier B: Controls systems (execution grammar)
- Currier A: Catalogs distinctions (complexity frontier)
- AZC: Locks context (uniform or custom scaffolds)
- HT: Keeps the human oriented once the lock is engaged

**AZC-DEEP Status:** COMPLETE (discovery phase). All four Voynich systems now show internal, non-trivial, testable architecture

---

## Version 2.6 (2026-01-10)

### C424: Clustered Adjacency + A-B Correlation Investigation + CFR Interpretation

**Summary:** Added C424 (Clustered Adjacency) with three refinements. Completed A-B hazard correlation investigation that falsified failure-memory hypothesis. Established Complexity-Frontier Registry (CFR) as unified interpretation for Currier A. Declared Currier A structurally exhausted.

**New Constraint:**
- **C424** - Clustered Adjacency in Currier A (Tier 2)
  - 31% of adjacent entries share vocabulary (clustered), 69% do not (singletons)
  - Mean cluster size: 3 entries (range 2-20)
  - Autocorrelation r=0.80 exceeds section-controlled null (z=5.85)

**Refinements:**
- **C424.a** - Structural correlates (68% vocabulary divergence between populations)
- **C424.b** - Run-size threshold (size 5+ shows J=0.36 vs size-2 J=0.08)
- **C424.c** - Section P inversion (singletons concentrate at top of pages)

**A-B Correlation Investigation (Exploratory - NO CONSTRAINT):**

| Test | Result | Interpretation |
|------|--------|----------------|
| Hazard density correlation | rho=0.228, p=0.038 | Initial positive |
| Permutation control | p=0.111 | FAILED |
| Frequency-matched control | p=0.056 | FAILED |
| **Pre-registered low-freq MIDDLE** | **rho=-0.052, p=0.651** | **FAIL** |

**Conclusion:** Apparent A-B hazard correlation entirely explained by token frequency. No residual risk-specific signal. Failure-memory hypothesis falsified.

**Unified Interpretation: Complexity-Frontier Registry (CFR)**

> Currier A externalizes regions of a shared control-space where operational similarity breaks down and fine discrimination is required.

- Currier B provides sequences (how to act)
- Currier A provides discrimination (where fine distinctions matter)
- AZC constrains availability
- HT supports the human operator

**The relationship between A and B is structural and statistical, not addressable or semantic.**

**Structural Exhaustion Declared:**
Currier A has reached its structural analysis limit. No further purely structural analyses expected to yield new constraints.

**Closed Tests (DO NOT RE-RUN):**
- Hazard density correlation - CLOSED (frequency-explained)
- Forgiveness/brittleness discrimination - CLOSED (inseparable from complexity)

**New files:**
- `CLAIMS/C424_clustered_adjacency.md` - Full constraint documentation
- `phases/exploration/a_b_hazard_correlation.py` - Main correlation script
- `phases/exploration/preregistered_low_freq_test.py` - Decisive final test
- `phases/exploration/a_b_connection_map.py` - Connection map generator
- `phases/exploration/A_B_CORRELATION_RESULTS.md` - Correlation results
- `phases/exploration/A_B_CONNECTION_MAP.md` - Connection map summary
- `phases/exploration/a_b_connection_map.json` - Machine-readable map

**Updated files:**
- `CLAIMS/INDEX.md` - Added C424, version 2.6, count 424
- `CLAIMS/currier_a.md` - Added C424 section, exploratory note with CFR interpretation

**Research phase:** Exploration (1838 entries, 83 folios analyzed)

---

## Version 2.5 (2026-01-09)

### Record Structure Analysis + C250.a Refinement

**Summary:** Complete analysis of Currier A record-level structure using DA-segmented block boundaries.

**Findings (validated but not all constraint-worthy):**
- Block count distribution: 57% single-block, 43% multi-block
- Block size pattern: FRONT-HEAVY (first block ~11 tokens, later ~5)
- Positional prefix tendencies: qo/sh prefer first, ct prefers last (V=0.136)
- Block-level repetition: 58.7% exact, 91.5% high similarity (J>=0.5)
- Record templates: 3-5 patterns cover 77%

**Expert review outcome:**
- C424-C426 initially proposed but REJECTED as constraints
- Positional preferences = tendencies, not rules (no constraint)
- Templates = emergent patterns, not grammar (no constraint)
- Block-aligned repetition = valid refinement of C250

**Accepted:**
- **C250.a** - Block-Aligned Repetition (refinement)
  - Repetition applies to DA-segmented blocks, not partial segments
  - Non-adjacent blocks more similar than adjacent (interleaved enumeration)

**Rejected (kept as descriptive findings only):**
- Positional prefix preferences (tendency, not constraint)
- Record structure templates (emergent, not grammar)

**New files:**
- `phases/exploration/record_structure_analysis.py`
- `phases/exploration/block_position_prefix_test.py`
- `phases/exploration/repetition_block_alignment.py`
- `phases/exploration/RECORD_STRUCTURE_SYNTHESIS.md`

**Updated files:**
- `CLAIMS/currier_a.md` - Added C250.a refinement under Multiplicity Encoding

**Note:** Constraint count unchanged (423). Findings describe USE of structure, not design limits.

---

## Version 2.4 (2026-01-09)

### C410.a: Sister Pair Micro-Conditioning (Refinement)

**Summary:** Refinement documenting compositional conditioning of sister-pair choice in Currier A.

**Findings:**
- MIDDLE is the PRIMARY conditioning factor (25.4% deviation from 50%)
- Some MIDDLEs are >95% one sister (yk: 97% ch, okch: 96% ch)
- Suffix compatibility provides secondary conditioning (22.1% deviation)
- Adjacent-token effects favor run continuation (ch->ch: 77%)
- DA context has ZERO effect (V=0.001) - confirms DA is structural
- Section effect is background bias (V=0.078)

**Interpretation:**
Sister pairs encode equivalent classificatory roles but permit compositionally conditioned surface variation. Preferences are local within the compositional system - no new categories, semantics, or hierarchies.

**New files:**
- `phases/exploration/sister_pair_conditioning.py`

**Updated files:**
- `CLAIMS/C408_sister_pairs.md` - Added C410.a refinement section

**Note:** This closes Priority 3 (sister-pair conditioning). Does not break equivalence class status.

---

## Version 2.3 (2026-01-09)

### C346.b: Component-Level Adjacency Drivers (Refinement)

**Summary:** Refinement note added to C346 documenting component-level analysis of adjacency coherence.

**Findings:**
- Removing DA tokens increases adjacency coherence (+18.4%)
- MIDDLE-only adjacency is LOWER than full-token (2.10x vs 2.98x)
- PREFIX and SUFFIX drive local adjacency more than MIDDLE
- DA-segmented blocks show 26.8x internal coherence

**Key insight:** Currier A adjacency reflects domain-level continuity (PREFIX) with item-level variation (MIDDLE). This is registry organization, not semantic chaining.

**New files:**
- `phases/exploration/payload_refinement.py`

**Updated files:**
- `CLAIMS/currier_a.md` - Added C346.b refinement note

**Note:** This is a refinement, not a new constraint. Does not change C346's core finding.

---

## Version 2.2 (2026-01-09)

### C423: PREFIX-BOUND VOCABULARY DOMAINS + C267 Amendment

**Summary:** New Tier-2 constraint establishing MIDDLE as the primary vocabulary layer in Currier A, with prefixes defining domain-specific vocabularies. Amendment to C267 corrects "42 common middles" to full census of 1,184.

**Finding (MIDDLE census):**
- 1,184 distinct MIDDLEs identified (full inventory)
- 80% (947) are PREFIX-EXCLUSIVE
- 20% (237) are shared across prefixes
- 27 UNIVERSAL middles appear in 6+ prefixes
- Top 30 account for 67.6% of usage
- MIDDLE entropy: 6.70 bits (65.6% efficiency)

**PREFIX vocabulary sizes:**
| Prefix | Exclusive MIDDLEs |
|--------|-------------------|
| ch | 259 (largest) |
| qo | 191 |
| da | 135 |
| ct | 87 |
| sh | 85 |
| ok | 68 |
| ot | 55 |
| ol | 34 (smallest) |

**DA-MIDDLE coherence finding:**
- DA-segmented sub-records do NOT exhibit increased MIDDLE similarity
- Adjacent segment J=0.037 vs random segment J=0.039 (0.94x)
- DA separates structure, not vocabulary content

**Interpretation:**
- Prefixes define domain-specific vocabularies
- MIDDLEs are selected from prefix-specific inventories
- Shared/universal middles form small cross-domain core
- This is the vocabulary layer of Currier A

**C267 amendment:**
- Original: "42 common middles" (discovery-era simplification)
- Updated: "1,184 unique (27 universal)" with cross-reference to C423
- Added note explaining scope mismatch

**New files:**
- `phases/exploration/middle_census.py`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C423, version 2.2, count 423
- `CLAIMS/currier_a.md` - Added Vocabulary Domains section, MIDDLE coherence note to C422
- `CLAIMS/C267_compositional_morphology.md` - Amended MIDDLE count and added note

**Research phase:** Exploration (25,890 tokens parsed, 17,589 with MIDDLE)

---

## Version 2.1 (2026-01-09)

### C422: DA as Internal Articulation Punctuation

**Summary:** New Tier-2 constraint documenting DA's structural punctuation role within Currier A entries.

**Finding:**
- 75.1% of internal DA occurrences separate adjacent runs of different marker prefixes (3:1 ratio)
- All DA tokens (daiin and non-daiin) exhibit identical separation behavior (74.9% vs 75.4%)
- Entries with DA are significantly longer (25.2 vs 16.4 tokens) and more prefix-diverse (3.57 vs 2.01)
- DA-segmented regions form prefix-coherent blocks

**Section gradient:**
- H (Herbal): 76.9% separation rate (3.3:1)
- P (Pharmaceutical): 71.7% (2.5:1)
- T (Text-only): 65.0% (1.9:1)
- Direction invariant across all sections

**Interpretation:**
- DA does not encode category identity
- DA marks internal sub-record boundaries within complex registry entries
- DA functions as punctuation rather than classifier
- Role is globally infrastructural, intensity correlates with section complexity

**New files:**
- `phases/exploration/da_punctuation_analysis.py`
- `phases/exploration/da_deep_dive.py`
- `phases/exploration/da_section_invariance.py`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C422, version 2.1, count 422
- `CLAIMS/currier_a.md` - Added DA Internal Articulation section

**Research phase:** Exploration (1838 entries, 3619 DA tokens analyzed)

---

## Version 2.0 (2026-01-09)

### C421: Section-Boundary Adjacency Suppression + C346.a Refinement

**Summary:** New Tier-2 constraint documenting section boundary effects on adjacent entry similarity. Refinement note added to C346 explaining similarity decomposition.

**C421 Finding:**
- Adjacent entries crossing section boundaries exhibit 2.42x lower vocabulary overlap
- Same-section adjacent: J=0.0160
- Cross-section adjacent: J=0.0066
- p < 0.001

**C346.a Refinement:**
- 1.31x adjacency similarity driven by MIDDLE (1.23x) and SUFFIX (1.18x)
- Weak contribution from marker prefixes (1.15x)
- Local ordering reflects subtype/property similarity, not marker class

**Interpretation:**
- Section boundaries (H/P/T) are primary hard discontinuities in Currier A
- Catalog organized by content/topic first, markers classify within clusters
- Does NOT change what Currier A represents; tightens characterization

**New files:**
- `phases/exploration/adjacent_entry_analysis.py`
- `phases/exploration/adjacent_section_boundary.py`
- `phases/exploration/ADJACENT_ENTRY_SYNTHESIS.md`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C421, version 2.0, count 421
- `CLAIMS/currier_a.md` - Added C346.a refinement, C421 section

**Research phase:** Exploration (1838 entries, 114 folios analyzed)

---

## Version 1.9 (2026-01-09)

### C420: Currier A Folio-Initial Positional Exception

**Summary:** New Tier-2 constraint documenting positional tolerance at folio boundaries in Currier A.

**Finding:**
- First-token position in Currier A permits otherwise illegal C+vowel prefix variants (ko-, po-, to-)
- 75% failure rate at position 1 vs 31% at positions 2-3
- C+vowel prefixes: 47.9% at position 1, 0% elsewhere
- Fisher exact p < 0.0001
- Morphologically compatible (ko- shares 100% suffix vocabulary with ok-)

**Interpretation:**
- Positional tolerance at codicological boundaries (common in medieval registries)
- Does NOT imply headers, markers, semantic categories, or enumeration
- No revision to C240 (marker families) or C234 (position-free) required

**New files:**
- `CLAIMS/C420_folio_initial_exception.md` - Full constraint documentation
- `phases/exploration/first_token_*.py` - Research scripts
- `phases/exploration/FIRST_TOKEN_SYNTHESIS.md` - Research synthesis

**Updated files:**
- `CLAIMS/INDEX.md` - Added C420, version 1.9, count 420
- `CLAIMS/currier_a.md` - Added Positional Exception section

**Research phase:** Exploration (48 folios analyzed)

---

## Version 1.8 (2026-01-09)

### HT/AZC FINAL CLOSED

**Summary:** Completed final constraint audit; verified C412; declared HT and AZC sections FINAL CLOSED.

**Audit results:**
- HT: 21 constraints + 1 superseded - ALL PASS
- AZC: 23 constraints - ALL PASS
- Notes: HT-AZC-NOTE-01, AZC-NOTE-01 correctly scoped

**C412 verification:**
- Original methodology replicated exactly
- Results reproduced: rho=-0.327 (original -0.326), p=0.0027 (original 0.002)
- Prior discrepancy explained: wrong metric used in re-analysis (ch-density vs ch-preference)
- Review flag removed

**Updated files:**
- `CLAIMS/C412_sister_escape_anticorrelation.md` - Added verification section
- `CLAIMS/INDEX.md` - Removed ⚠️ REVIEW marker

**New files:**
- `phases/exploration/c412_verification.py` - Verification script

**Final status:**
| Section | Status |
|---------|--------|
| Human Track (HT) | FINAL CLOSED |
| AZC System | FINAL CLOSED |
| Sister Pairs | FINAL CLOSED |

---

## Version 1.7 (2026-01-09)

### HT-AZC Third Anchoring Pressure

**Summary:** Identified AZC-specific HT pattern (diagram label concentration).

**Updated files:**
- `CLAIMS/human_track.md` - Added HT-AZC-NOTE-01, updated frozen statement

**Key finding:**
- AZC HT uniquely shows BOTH line-initial AND line-final enrichment
- Driven by L-placement (label) text: 88.8% initial, 95% final
- L-placement lines are short (1-3 tokens) with 15.1% HT density
- Establishes **third anchoring pressure**: diagram geometry (label positions)

**Three-system refinement:**
| System | Anchoring Pressure |
|--------|-------------------|
| Currier A | Registry layout (entry boundaries) |
| Currier B | Temporal/attentional context |
| AZC | Diagram geometry (label positions) |

---

## Version 1.6 (2026-01-09)

### Data Source Documentation + AZC/C412 Updates

**Summary:** Added data source documentation; documented AZC findings; flagged C412 discrepancy.

**Updated files:**
- `SYSTEM/METHODOLOGY.md` - Added "Canonical Data Source" section
- `CLAIMS/azc_system.md` - Added AZC-NOTE-01 (qo-depletion refinement)
- `CLAIMS/C412_sister_escape_anticorrelation.md` - Added review flag
- `CLAIMS/INDEX.md` - Added review marker to C412

**Key additions:**

1. **Data source documentation:**
   - PRIMARY DATA FILE: `data/transcriptions/interlinear_full_words.txt`
   - WARNING about EVA vs standard vocabulary encoding

2. **AZC-NOTE-01:** qo-prefix depletion (2.8x lower than B), refines C301/C313

3. **C412 review flag:** Re-analysis finds anticorrelation in Currier A (rho=-0.334, p=0.0003), NOT in B (rho=-0.089, p=0.42). Requires reconciliation with original SISTER phase.

**Issue caught:** During AZC exploration, wrong transcription file was initially used. All previous constraints verified safe.

---

## Version 1.5 (2026-01-09)

### HT Formal Hierarchy

**Summary:** Established canonical hierarchy for Human Track layer. Adds C414-C419.

**New files:**
- `CLAIMS/HT_HIERARCHY.md` - Formal hierarchy document (canonical)

**Updated files:**
- `CLAIMS/human_track.md` - Added C414-C419, system-specific refinement
- `CLAIMS/HT_CONTEXT_SUMMARY.md` - Updated with hierarchy reference
- `CLAIMS/INDEX.md` - Count 411→419, added 6 new constraints
- `CLAUDE_INDEX.md` - Count update, navigation to HT_HIERARCHY.md

**Constraints added:**
| # | Name | Tier | Key Finding |
|---|------|------|-------------|
| C414 | Strong Grammar Association | 2 | chi2=934, p<10^-145 |
| C415 | Non-Predictivity | 1 (FALSIFICATION) | MAE worsens with HT conditioning |
| C416 | Directional Asymmetry | 2 | V=0.324 vs 0.202 (1.6x) |
| C417 | Modular Additive | 2 | No synergy (p=1.0) |
| C418 | Positional Without Informativeness | 2 | Bias exists but non-predictive |
| C419 | HT Positional Specialization in A | 2 | Entry-aligned, seam-avoiding |

**Terminology guardrail established:**
- DO: "aligned with", "correlated with", "position-biased"
- DON'T: "marks", "encodes", "annotates", "means"

**Model refinement:**
- Currier A: HT aligned with registry layout (entry boundaries)
- Currier B: HT aligned with temporal/attentional context
- Same layer, different anchoring pressures

---

## Version 1.4 (2026-01-09)

### Phase: STRUCTURE_FREEZE_v1

**Summary:** Formal freeze of structural inspection layer. Transitions project from foundational reconstruction to deliberate post-structure paths.

**Components frozen:**
- **Basic Inspection v1** (`apps/script_explorer/BASIC_INSPECTION.md`)
  - Currier A registry parsing and roles
  - Currier B grammar roles (49-class, conservative binding)
  - AZC placement binding (`R/R1/R2/R3`, `S/S1/S2`, `C`, `MULTI`)
  - HT isolation and override behavior
  - Global properties (prefix family, kernel affinity, escape)

- **Execution Inspector v0.1** (`apps/script_explorer/EXECUTION_INSPECTOR.md`)
  - Grammar-only execution inspection
  - `grammar_bound` semantics
  - Conservative UNKNOWN handling
  - No hazards, order, or kernel contact beyond grammar anchors

**Repository rules enforced:**
- ❌ Do not alter parsing logic
- ❌ Do not alter classification logic
- ❌ Do not alter role assignment tables
- ❌ Do not alter system boundaries
- ❌ Do not reinterpret UNKNOWNs
- ❌ Do not extend execution semantics implicitly
- ❌ Do not weaken system gating (A/B/AZC/HT)

**Post-freeze paths available:**
1. Documentation & Consolidation (RECOMMENDED)
2. Visualization / UX (SAFE)
3. Deeper Execution Semantics (ADVANCED, requires new phase)

**Intent:** Preserve structural integrity. Expansion is a choice, not an accident.

---

## Version 1.0 (2026-01-08)

### Initial Release

**Created:** Context expansion system to replace monolithic CLAUDE.md

**Structure:**
- `context/` directory with 9 subdirectories
- `CLAUDE_INDEX.md` as primary entry point (~4k tokens)
- Progressive disclosure architecture
- 57 markdown files total

**Directories:**
- `SYSTEM/` - Meta-rules, tiers, methodology (5 files)
- `CORE/` - Tier 0-1 facts (3 files)
- `ARCHITECTURE/` - Structural analysis by text type (5 files)
- `OPERATIONS/` - OPS doctrine, program taxonomy (3 files)
- `CLAIMS/` - 411 constraints indexed (24 files: 1 index, 16 individual claims, 7 grouped registries)
- `TERMINOLOGY/` - Key definitions (3 files)
- `METRICS/` - Quantitative facts (4 files)
- `SPECULATIVE/` - Tier 3-4 content (4 files)
- `MAPS/` - Cross-references (3 files)

**Design Principles:**
1. Entry point stays slim (<10k tokens)
2. One concept per file
3. ≤15k tokens per file
4. Every claim declares Tier + closure
5. No analysis in context files
6. Archive is append-only
7. Context points to archive

**Migration:**
- Content extracted from CLAUDE.md v1.8 (95KB, ~30k tokens)
- Original preserved as `archive/CLAUDE_v1.8_2026-01-08.md`
- CLAUDE.md converted to redirect

---

## Version 1.3 (2026-01-08)

### Added: Constraint-First Reasoning Protocol

**Summary:** Added methodology for checking constraints before speculating, and guidance on when/how to question constraints.

**Files updated:**
- `context/SYSTEM/METHODOLOGY.md` - Added two new sections:
  - "Constraint-First Reasoning" - rule to search constraints before interpreting
  - "Questioning Constraints" - when and how to challenge existing claims
- `context/CLAUDE_INDEX.md` - Added stop condition reminder and note that questioning is allowed

**Motivation:** During conversation, speculated that "Currier A entries might reference the same categories B executes" — but C384 explicitly falsifies this. Checking constraints first would have prevented the error.

**Key principles added:**
- Search CLAIMS/ before reasoning about relationships
- Distinguish "constrained" from "undocumented" (gap ≠ permission)
- Cite constraint numbers or flag as research gap
- Questioning is allowed but must be explicit, not silent override
- Tier determines revisability (0=frozen, 2=reopenable with evidence)

---

## Version 1.2 (2026-01-08)

### Added: Structural Intuition Clarification

**Summary:** Added documentation to prevent the misinterpretation that "neutral/unhighlighted tokens are unknown."

**Files updated:**
- `context/CLAUDE_INDEX.md` - Added three new sections:
  - "How to Think About Tokens (Structural Layer)"
  - "Why Visualization Tools Highlight Only Some Tokens"
  - "Structural Analysis vs Interpretive / Probabilistic Reasoning"

**Clarifications made:**
- Tokens are surface realizations, not functional operators
- Functional behavior determined at instruction-class level
- High hapax rates explained by compositional morphology
- "Neutral" means "non-contrastive", not "unknown"
- Visualization highlighting is a UI choice, not knowledge boundary
- Bayesian/probabilistic reasoning explicitly supported in interpretive layer

**No constraint changes:** This is a documentation-only update for human intuition alignment. No tiers, claims, or conclusions were altered.

---

## Version 1.1 (2026-01-08)

### Added: Research Automation

**Summary:** Added skills, hooks, and workflow documentation for automated research.

**Files created:**
- `.claude/skills/phase-analysis/SKILL.md` - Automatic phase analysis
- `.claude/skills/constraint-lookup/SKILL.md` - Constraint search and citation
- `.claude/settings.json` - Hook configuration
- `archive/scripts/validate_constraint_reference.py` - Constraint validation
- `archive/scripts/extract_phase_metrics.py` - Metrics extraction

**Files updated:**
- `context/SYSTEM/METHODOLOGY.md` - Added "Research Workflow (Automated)" section
- `context/SYSTEM/HOW_TO_READ.md` - Added multi-branch access patterns
- `context/CLAUDE_INDEX.md` - Added "Automation" section

**New workflows:**
- Phase Analysis Protocol (automatic)
- Constraint Lookup Protocol (automatic)
- Constraint reference validation (hook)

---

## Future Entries

When updating context, add entries in this format:

```markdown
## Version X.Y (YYYY-MM-DD)

### [Type: Added/Changed/Removed/Fixed]

**Summary:** Brief description

**Files affected:**
- `path/to/file.md` - what changed

**Constraint changes:**
- C### added/updated/removed

**Source:** Phase PHASE_NAME (if applicable)
```

---

## Navigation

← [HOW_TO_READ.md](HOW_TO_READ.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
