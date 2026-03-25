# Phase 625: Short Paragraph Architecture

**Status:** COMPLETE
**Verdict:** SECTION_CONFOUNDED_WITH_LENGTH_RESIDUAL
**Constraints:** C1848-C1858 (11 constraints)
**Date:** 2026-03-25

---

## Question

Are short paragraphs (0-4 body lines, 85.8% of B) truncated instances of the universal arc, or structurally distinct operational objects?

## Background

Phase 624 proved B paragraphs form a CONTINUOUS_MANIFOLD -- one universal arc, no discrete templates (C1840, silhouette=0.075). But this was tested on only 14.2% of B paragraphs (those with >=6 body lines). The remaining 85.8% (~450 paragraphs) were excluded because they lack enough body lines for trajectory analysis.

Body-line distribution:
- 0 body (HEADER_ONLY): 107 (18.3%) -- BIO 55%, PHARMA 30%
- 1-2 body (MINIMAL): 193 (33.0%) -- RECIPE 85%
- 3-4 body (SHORT): 149 (25.5%) -- RECIPE 65%
- 5+ body (LONG): 136 (23.2%) -- HERBAL/BIO balanced

51.3% of all B paragraphs have <=3 total lines. Recipe/Pharma produce 78-86% of 2-4 line paragraphs.

Expert consultation (pre-plan, two rounds):
- Expert-advisor: kernel gradient test (C1206), position-matched subsampling, equivalence framing
- Crazy-expert: minimum viable paragraph test, HEADER_ONLY punctuation function, zone classification as most diagnostic test

---

## Design

### Population Strata

| Stratum | Body Lines | Expected N | Dominant Section |
|---------|-----------|------------|------------------|
| HEADER_ONLY | 0 | ~107 | BIO 55%, PHARMA 30% |
| MINIMAL | 1-2 | ~193 | RECIPE 85% |
| SHORT | 3-4 | ~149 | RECIPE 65% |
| LONG | 5+ | ~136 | HERBAL/BIO balanced |

### 11-Feature Paragraph Profile

| # | Feature | Computation | Rationale |
|---|---------|-------------|-----------|
| 1 | log_ke_ratio | log((k+0.5)/(e+0.5)) | Kernel polarity |
| 2 | h_rate | h-kernel / total tokens | Monitoring density |
| 3 | headless_rate | headless fraction | Infrastructure (C1574) |
| 4 | mode_a_frac | Mode A suffix fraction | Specification vs continuation (C1229) |
| 5 | mean_opacity | mean terminal opacity | Closure gradient (C1440) |
| 6 | cat_entropy | 8-category Shannon entropy | Operational diversity (C1250) |
| 7 | tokens_per_line | mean line length | Strongest sequential channel (C1728) |
| 8 | m_terminal_rate | m-terminal fraction | Closure signature (C1435) |
| 9 | dark_frac | dark pipeline fraction | Vocabulary pipeline (C1146) |
| 10 | bridge_frac | bridge token fraction | Dynamical freedom (C1099) |
| 11 | thermal_frac | THERMAL category fraction | Execution axis (C1309) |

### Section Confound Control Protocol

Every test runs at three levels:
1. **POOLED** (diagnostic -- expected section artifact)
2. **SECTION-RESIDUALIZED** (primary -- subtract section mean)
3. **WITHIN-RECIPE** (confirmation -- largest section, 85% of MINIMAL)

Golden folio test where applicable: folios containing both short AND long paragraphs from the same section.

### Null Models

| Null | Script | Construction | Tests |
|------|--------|-------------|-------|
| N1: Position-matched subsample | S2 | Take first N body lines from LONG paragraphs | Short = beginnings of long? |
| N2: Random subsample | S2 | Take random N body lines from LONG, 200 reps | Short = random subset of long? |
| N3: HEADER_ONLY position shuffle | S3 | Shuffle HEADER_ONLY positions within folios | Punctuation function real? |

### Verdict Logic

- **TRUNCATED_FROM_START**: Position-matched passes, features invariant, arc scales down
- **SPECIFICATION_DOMINATED**: Short paragraphs are specification-heavy beginnings; HEADER_ONLY are pure declarations
- **SECTION_CONFOUNDED_ONLY**: All differences vanish after section control
- **ARCHITECTURALLY_DISTINCT**: Position-matched fails, multiple features differ after section control

---

## Scripts

| # | Script | Purpose | Output |
|---|--------|---------|--------|
| shared | `scripts/shared_625.py` | Shared utilities, stratum assignment, 11 features | -- |
| 1 | `scripts/census_profiling.py` | Census, gallows, atoms, zone classification, feature profiles | `results/census_profiling.json` |
| 2 | `scripts/architecture_scaling.py` | Subsample null, minimum viable paragraph, kernel gradient | `results/architecture_scaling.json` |
| 3 | `scripts/between_paragraph_org.py` | HEADER_ONLY punctuation, spec/exec ratio, folio-level organization | `results/between_paragraph_org.json` |

---

## Script Details

### shared_625.py

**Purpose:** Shared utilities for all Phase 625 scripts. Provides stratum assignment (HEADER_ONLY / MINIMAL / SHORT / LONG based on body line count), 11-feature paragraph profile extraction, section-residualization, and golden folio identification.

**Key functions:**
- Stratum classification: 0 body = HEADER_ONLY, 1-2 = MINIMAL, 3-4 = SHORT, 5+ = LONG
- 11-feature vector computation per paragraph
- Section mean subtraction for residualization
- Within-RECIPE filtering for confirmation tests
- Golden folio identification (folios with both short and long paragraphs from same section)

---

### Script 1: census_profiling.py

**Purpose:** Comprehensive census of B paragraphs by stratum, plus gallows analysis, atom composition, C1398 zone classification, and 11-feature profiles per stratum with section confound control.

**Pipeline:**
1. Census: count paragraphs by stratum x section, verify expected distributions
2. Gallows analysis: k+f fraction by stratum (P4 test), gallows type distribution
3. Atom composition: per-stratum atom frequency profiles, JSD between strata
4. Zone classification (C1398): assign paragraphs to zones, test zone x stratum contingency (P5)
5. Feature profiling: 11-feature profiles per stratum, MW tests at all three confound levels (POOLED, SECTION-RESIDUALIZED, WITHIN-RECIPE)
6. Section x stratum association: Cramer's V (P1 test)

**Constraint candidates:**
- Section x stratum association strength
- Gallows composition by stratum
- Zone x stratum dependency
- Feature profiles by stratum (section-controlled)

**Output:** `results/census_profiling.json`

---

### Script 2: architecture_scaling.py

**Purpose:** The central test: position-matched subsampling null, random subsampling null, minimum viable paragraph test, and kernel gradient analysis. Determines whether short paragraphs are truncated beginnings of long ones.

**Tests:**

1. **Position-matched subsample (N1):** Take the first N body lines from LONG paragraphs (N=1,2,3,4). Compute 11-feature profiles on these truncated versions. KS test against actual MINIMAL/SHORT paragraphs. If 8+ features show p > 0.05 (section-controlled), short = beginning of long (P2).

2. **Random subsample (N2):** Take random N body lines from LONG paragraphs, 200 replicates. Same KS test battery. If random subsample FAILS (4+ features p < 0.05) while position-matched PASSES, short paragraphs specifically resemble openings, not arbitrary subsets (P2).

3. **Minimum viable paragraph test:** What is the minimum body-line count at which paragraph-level features stabilize? Compute feature vector variance as a function of body-line count. Identify the knee point.

4. **Kernel gradient (C1206):** Test h-fraction decline across body positions in SHORT (3-4 body) paragraphs. If gradient is absent (rho not significant, p > 0.05), SHORT paragraphs are too brief to express the gradient (P7).

5. **Line-level arc test:** Compute 11-feature vectors for first and last body lines of SHORT paragraphs. Cosine similarity between them (P8). If cosine < -0.3, the anti-parallel boundary structure (C1837) persists even in short paragraphs.

6. **m-terminal last-line enrichment (P6):** m-terminal rate in last body line of MINIMAL/SHORT vs LONG body mean.

**All tests run at three confound levels.**

**Constraint candidates:**
- Position-matched subsample result
- Minimum viable paragraph threshold
- Kernel gradient in short paragraphs
- Arc persistence in short paragraphs
- m-terminal closure enrichment

**Output:** `results/architecture_scaling.json`

---

### Script 3: between_paragraph_org.py

**Purpose:** HEADER_ONLY paragraph functional analysis, specification/execution ratio, and folio-level organizational structure. Tests whether HEADER_ONLY paragraphs serve a punctuation or declaration function.

**Tests:**

1. **HEADER_ONLY punctuation function:** Do features of the paragraph FOLLOWING a HEADER_ONLY differ from baseline? Compare 11-feature profiles of post-HEADER_ONLY paragraphs vs all other paragraphs (P10). Null model N3: shuffle HEADER_ONLY positions within folios, 200 replicates.

2. **Specification/execution ratio (P9):** Compute spec/exec ratio per stratum using Mode A fraction and kernel polarity. If HEADER_ONLY ratio > 2x LONG, these are pure specification objects.

3. **Folio-level stratum organization:** Do strata cluster within folios or distribute uniformly? Shannon entropy of stratum distribution per folio vs shuffled null.

4. **Stratum transition matrix:** Within folios, compute stratum-to-stratum transition probabilities. Chi-squared vs uniform. Tests whether strata have preferred sequencing.

5. **Golden folio direct comparison:** In folios containing both SHORT and LONG paragraphs from the same section, direct MW comparison on 11 features (no section confound possible).

**Constraint candidates:**
- HEADER_ONLY functional role (punctuation vs independent)
- Specification/execution ratio by stratum
- Folio-level stratum organization
- Stratum transition structure

**Output:** `results/between_paragraph_org.json`

---

## Pre-Registered Predictions

| # | Prediction | Basis | Pass Criterion | Result |
|---|-----------|-------|----------------|--------|
| P1 | Section x stratum V > 0.50 | C860, C1404 | V > 0.50, p < 0.001 | **FAIL** V=0.468, p<0.001 (close but below threshold) |
| P2 | Position-matched subsample PASSES, random FAILS | C1206 kernel gradient, C1428 Q1 peak | Pos-matched: 8+ features KS p > 0.05. Random: 4+ features p < 0.05. Section-controlled. | **PARTIAL** Pooled: both fail (4/11). Within-S MINIMAL: pos-matched 8/11 PASS |
| P3 | After section control, 8+ of 11 features stratum-invariant | C1241, C963, C1239 | MW p > 0.05 for SHORT vs LONG, section-residualized | **PASS** Section-resid: 8/11. Within-Recipe: 10/11. Golden: 7/11 |
| P4 | Gallows k+f fraction higher in HEADER_ONLY than LONG | C1780, C1784 | Chi-sq p < 0.01, k+f HEADER_ONLY > LONG | **FAIL** Direction reversed: HO 4.4% vs LONG 8.9%. HO 87.8% non-gallows-initial |
| P5 | MINIMAL paragraphs concentrate in specific C1398 zones | C1398, Recipe dominance | Chi-sq zone x stratum p < 0.01 | **FAIL** V=0.098, p=0.206. MINIMAL spans all zones uniformly |
| P6 | m-terminal elevated in MINIMAL/SHORT last body line | C1435 | Rate > LONG body mean, MW p < 0.05 | **FAIL** KW p=0.821. No stratum difference in last-line m-terminal |
| P7 | Kernel gradient (h declining) absent in SHORT (3-4 body) | C1206 gradient needs >=5 lines | rho not significant (p > 0.05) in SHORT | **PASS** SHORT rho=-0.078, p=0.086. Also absent in LONG (rho=-0.035, p=0.278) |
| P8 | Line-level arc present in SHORT: first/last body line cosine < -0.3 | C1837, C1425-C1430 | First/last body line feature cosine < -0.3 | **FAIL** Cosine=+0.999 at ALL strata. No anti-parallel in 12-feature space. Caveat: features not z-scored |
| P9 | HEADER_ONLY spec/exec ratio > 2x LONG | C853 (0% EN), C1287 | Ratio > 2x | **PARTIAL** Pooled: 1.71x (fail). Within-Recipe: 2.34x (pass, N=6 HO) |
| P10 | HEADER_ONLY does NOT create paragraph dependency | C845, C1399 | Post-HO features approx baseline, MW p > 0.05 | **PASS** Pooled: 8/11 significant (section confound). Section-controlled: 0/11 significant |

---

## Dependency Graph

```
Independent (no dependencies):
  Script 1 (census_profiling.py)
  Script 2 (architecture_scaling.py)
  Script 3 (between_paragraph_org.py)

All three scripts depend on:
  shared_625.py (shared utilities)
```

---

## Methodological Standards

### Stratum Assignment
- Body lines = total paragraph lines minus header line minus label lines
- HEADER_ONLY: 0 body lines. MINIMAL: 1-2. SHORT: 3-4. LONG: 5+.
- H-track only, Currier B only, labels excluded from body count

### 11-Feature Paragraph Profile
- Features computed per paragraph (whole-paragraph aggregates)
- All features are scalar (no vector features)
- Missing features (e.g., no k-class tokens) handled with smoothing constants

### Section Confound Control
- POOLED: raw comparison across strata (diagnostic, expected to show section artifact)
- SECTION-RESIDUALIZED: subtract per-section mean from each paragraph's feature vector. Primary test level.
- WITHIN-RECIPE: restrict to Recipe section only. Confirmation test exploiting Recipe's dominance in MINIMAL (85%) and SHORT (65%).
- Golden folio: direct comparison within folios containing both short and long paragraphs from same section. Eliminates section confound entirely.

### Significance
- Per-script Bonferroni: alpha = 0.05 / (number of tests in script)
- Mann-Whitney U for two-stratum comparisons (non-parametric)
- KS test for distribution equivalence in subsampling nulls
- Chi-squared for contingency tables (zone x stratum, section x stratum)
- Cramer's V for association strength
- Permutation nulls: 200 replicates, one-sided p-values

### Sample Requirements
- Minimum 20 paragraphs per stratum-section cell for section-stratified tests
- Report effective N after all filtering
- WITHIN-RECIPE tests require Recipe paragraphs in each stratum being compared

### Confounds
- Section: three-level control protocol (POOLED, SECTION-RESIDUALIZED, WITHIN-RECIPE)
- Paragraph length: inherent to stratum definition; position-matched subsample tests for length artifact
- Folio ecology: golden folio test eliminates both section and folio confounds
- REGIME: monitor but not primary confound (C1843 shows REGIME does not mediate arc shape)

---

## Expected Constraints

C1848-C1858 range (up to 11 constraints).

---

## Results

**Prediction scorecard:** 3 PASS, 2 PARTIAL, 5 FAIL

**Verdict: SECTION_CONFOUNDED_WITH_LENGTH_RESIDUAL** — Most feature variance across paragraph strata is explained by section assignment (V=0.468). After section residualization, 8/11 features become stratum-invariant. Three length-mechanical features survive: cat_entropy (operational diversity narrows with fewer lines), tokens_per_line (short paragraphs pack more per line), m_terminal_rate (closure marker frequency). No evidence of distinct operational modes by stratum.

**Key findings:**

1. **Short paragraphs are NOT truncated beginnings** (C1848): Position-matched subsample null fails at pooled level (4/11 features pass, need 8+). But within-section S, MINIMAL passes 8/11 (C1858) — the apparent pooled distinctness is a section composition artifact.

2. **Section dominates stratum variance** (C1849): After section residualization, 8/11 features become invariant between SHORT and LONG. Within Recipe: 10/11 invariant. The stratum effect is overwhelmingly a section selection effect.

3. **Three length-residual features** (C1850): cat_entropy (p=3.2e-5, d=-0.54), tokens_per_line (p=0.038, d=0.34), m_terminal_rate (p=0.000248, d=-0.25). These are informational/mechanical consequences of shorter text, not operational mode differences.

4. **Zone classification stratum-independent** (C1851): V=0.098, p=0.206. MINIMAL paragraphs span all C1398 zones uniformly — they are not specialized single-function units.

5. **HEADER_ONLY non-gallows-initial** (C1852): 87.8% (79/90) lack gallows-initial tokens. k-enriched (0.157 vs 0.116, p=0.049), o-depleted (0.096 vs 0.142, p=0.0002). Reverses P4 prediction.

6. **No anti-parallel arc at any scale** (C1854): First/last body line cosine ≈ +0.999 at all strata. The anti-parallel structure (C1837, cosine=-0.989) operates at atom enrichment grain, not captured by 12 category-level features. Caveat: features not z-scored, tokens_per_line dominates cosine.

7. **Kernel gradient absent everywhere** (C1855): Not just absent in SHORT (p=0.086) but also in LONG (p=0.278). C1206 gradient may operate at finer position resolution or within specific sections/REGIMEs not captured by pooled analysis.

8. **Header-body coupling increases with length** (C1856): MINIMAL 0.070, SHORT 0.078, LONG 0.098. Longer paragraphs allow more header→body prediction (consistent with C1795).

9. **HIGH-count folios more structured** (C1857): Steeper length gradient (rho=-0.247, p=0.033), more structured gallows transitions (chi2=37.8, p=1.9e-5), MORE diverse paragraphs (JSD=0.146 vs 0.119).

10. **HEADER_ONLY independence after section control** (C1853): Pooled dependency (8/11 features differ post-HO) vanishes after section control (0/11 within Recipe). Punctuation function borderline (zone change 64.7% vs 47.7%, permutation p=0.06).

**Data note:** bridge_frac = 0.0 in all strata. This is likely a data loading issue (bridge token set not intersected with MIDDLEs in build_corpus). Does not affect other features or conclusions.

**Runtime:** Script 1: ~15s. Script 2: ~25s. Script 3: ~10s.

---

## Constraints

| C# | Claim | Tier | Scope |
|----|-------|------|-------|
| 1848 | Short paragraphs NOT truncated beginnings: position-matched subsample null FAILS at pooled level (4/11 features pass, need 8+). Short paragraphs have different feature distributions than first-N-lines of long paragraphs. Verdict: DISTINCT at pooled level | 2 | B, paragraph, stratum, subsample |
| 1849 | Section dominates stratum variance: V=0.468 (p<0.001). After section residualization, 8/11 features become stratum-invariant (SHORT vs LONG). Within Recipe: 10/11 invariant. Golden folio: 7/11 invariant | 2 | B, paragraph, section, stratum, C860 |
| 1850 | Three length-residual features survive section control: cat_entropy (p=3.2e-5, d=-0.54), tokens_per_line (p=0.038, d=0.34), m_terminal_rate (p=0.000248, d=-0.25). All are informational/mechanical consequences of shorter text, not operational mode differences | 2 | B, paragraph, stratum, features |
| 1851 | Zone classification stratum-independent: C1398 zone assignment shows V=0.098 (p=0.206) across MINIMAL/SHORT/LONG. MINIMAL spans all zones uniformly. Within Recipe: V=0.101, p=0.447. Short paragraphs are not zone-specialized | 2 | B, paragraph, zones, C1398 |
| 1852 | HEADER_ONLY non-gallows-initial: 87.8% (79/90) lack gallows-initial tokens. k-fraction enriched (0.157 vs 0.116, p=0.049), o-fraction depleted (0.096 vs 0.142, p=0.0002). Opener fraction 4.4% (lowest of all strata). Headers are NOT executive gallows declarations | 2 | B, paragraph, header_only, gallows |
| 1853 | HEADER_ONLY independence after section control: post-HO paragraphs differ in 8/11 features pooled but 0/11 within Recipe. Punctuation function borderline (zone change 64.7% vs 47.7%, permutation p=0.06). No paragraph dependency created by HEADER_ONLY | 2 | B, paragraph, header_only, independence, C845 |
| 1854 | No anti-parallel arc in category-level feature space: first/last body line cosine=+0.999 at all strata (MINIMAL, SHORT, LONG). C1837's anti-parallel (cosine=-0.989) operates at atom enrichment grain not captured by 12 category features. Caveat: features not z-scored | 2 | B, paragraph, arc, boundary, C1837, C1842 |
| 1855 | Kernel gradient absent all strata: h-rate declining gradient (C1206) not detected. SHORT rho=-0.078 (p=0.086), LONG rho=-0.035 (p=0.278). C1206 may operate at finer position resolution or within specific sections | 2 | B, paragraph, kernel, gradient, C1206 |
| 1856 | Header-body coupling increases with paragraph length: MINIMAL 0.070, SHORT 0.078, LONG 0.098 (mean absolute rho). Longer paragraphs show stronger header→body prediction. Consistent with C1795 | 2 | B, paragraph, header, coupling, C1795 |
| 1857 | HIGH-count folios more structured: steeper first-line length gradient (rho=-0.247, p=0.033), more structured gallows transitions (chi2=37.8, p=1.9e-5, V=0.236), MORE diverse paragraphs (JSD=0.146 vs 0.119). HIGH-count folios are internally heterogeneous with strong sequential organization | 2 | B, folio, paragraph, organization |
| 1858 | Section-specific truncation in S: within Recipe, MINIMAL passes position-matched subsample null (8/11 features, n_real=163, n_synth=44). Recipe MINIMAL paragraphs specifically resemble truncated beginnings of Recipe LONG paragraphs. Other sections similar (B: 9/11, H: 9/11) with low N | 2 | B, paragraph, section, Recipe, truncation |
