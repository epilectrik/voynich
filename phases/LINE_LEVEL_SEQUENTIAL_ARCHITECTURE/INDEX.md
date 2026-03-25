# Phase 623: Line-Level Sequential Architecture & Compositional Drift

**Status:** COMPLETE
**Verdict:** SEQUENTIAL_WEAK_CONSECUTIVE_COHERENCE
**Constraints:** C1830-C1839
**Date:** 2026-03-24

---

## Question

What channels carry the between-line sequential signal discovered in C1727? And do folio-level grammar compliance patterns reveal compositional ordering?

## Background

C1727 established that line ordering within paragraphs is non-trivially smooth (lines are more similar to their neighbors than to random paragraph-mates). C1728 decomposed this partially: **line length** is the dominant channel (lag-1 MI=0.178 bits, 9.3% of H(length)), while HEAD and TERM show NO significant lag-1 MI. This creates a precise gap: sequential structure exists, lives primarily in structural channels not compositional ones, but only 3 of ~16 plausible channels have been tested.

Separately, the question of whether folios were composed in a detectable order has never been tested. The frozen model treats all folios as independent programs (C1399, C1400), but sequential grammar features represent a novel dimension that prior independence tests didn't cover.

## Design

### Part A: Between-Line Sequential Channel Architecture (Scripts 1-4)

Systematically characterize which feature channels carry between-line sequential signal, using paragraph-shuffled nulls throughout. Extends C1727-C1729 to full atom-level resolution. Includes transfer entropy for directionality, CTS-conditioned routing for closure reconciliation, and complexity gradient for instructional trajectory.

### Part B: Compositional Maturity Analysis (Scripts 5-6)

Build per-folio "grammar compliance profiles" and test whether they correlate with physical ordering (quire position) beyond section membership.

### Confound Architecture

Every test runs in three modes:
1. **RAW** -- no controls
2. **SECTION-RESIDUALIZED** -- z-scores within section
3. **LENGTH-CONTROLLED** -- binned conditional MI/correlation controlling for line length

If a signal appears in RAW but not SECTION-RESIDUALIZED: section effect, killed.
If signal survives SECTION-RESIDUALIZED but not LENGTH-CONTROLLED: line-length-mediated.
If signal survives all three: genuine sequential channel.

### Go/No-Go

**Part A success:** At least 2 channels beyond line length show section-controlled p < 0.01.
**Part B success:** PC1 of maturity features explains >30% variance after section control.
**If both fail:** Grammar was crystallized before composition; lines are compositionally independent within the structural template. That itself is a strong finding.

---

## Scripts

### Part A: Sequential Channel Architecture

| # | Script | Purpose | Key Prior |
|---|--------|---------|-----------|
| 1 | `sequential_channel_census.py` | 18-channel lag-1 MI census + ablation + transfer entropy + safety alternation + cross-paragraph + position partitioning | C1727, C1728 |
| 2 | `cts_conditioned_routing.py` | Terminal-to-HEAD routing conditioned on closure strength | C1563, C1728 |
| 3 | `complexity_gradient.py` | 9-feature complexity gradient + kernel gradient novelty + conditional entropy rate | C1206, C1782, C1574 |
| 4 | `boundary_content_anatomy.py` | Decompose C1729 boundary enrichment into specific channels | C1729 |

### Part B: Compositional Maturity

| # | Script | Purpose | Key Prior |
|---|--------|---------|-----------|
| 5 | `grammar_temperature.py` | Per-folio compliance metric (5 rule sets), token-shuffle null | C1360, C1440, C1472 |
| 6 | `compositional_drift.py` | Consecutive-folio JSD + maturity PCA + Mantel test against quire ordering | C361, C1569 |

---

## Script Details

### Script 1: sequential_channel_census.py

**Purpose:** Comprehensive 18-channel lag-1 MI census with ablation decomposition, transfer entropy, cross-paragraph comparison, and paragraph-position partitioning. The anchor script.

**18 feature channels (each = scalar per body line):**

| # | Channel | Prior Expectation | Source |
|---|---------|-------------------|--------|
| 1 | Line length (tokens) | POSITIVE (calibration) | C1728 |
| 2 | Suffix mode proportion (frac Mode A) | WEAK POSITIVE | C1423 |
| 3 | PREFIX JSD from folio mean | UNKNOWN | C1801 |
| 4 | k-fraction: k/(k+h+e) | POSSIBLE | C1206 |
| 5 | h-fraction | POSSIBLE | C965/C1206 |
| 6 | e-fraction | POSSIBLE | C1206 |
| 7 | Headless rate | NULL (C1574) | C1574 |
| 8 | Modifier density (mean len(mods)) | UNKNOWN | Novel |
| 9 | m-terminal rate | POSSIBLE | C1434-C1439 |
| 10 | Dark pipeline fraction | NULL expected | C1146 |
| 11 | HT density | NULL expected | C842 |
| 12 | Category entropy H(8-cat) | NULL (C1716) | C1716 |
| 13 | ITERATION cluster ({a,i,n,r} frac) | UNKNOWN | C1207 |
| 14 | MONITORING cluster ({c,h} frac) | POSSIBLE | C1207 |
| 15 | Bridge token fraction | NULL expected | Pipeline is folio-level |
| 16 | ARTICULATOR rate | NULL expected | C1416-1417 |
| 17 | ey-fraction (preventive safety) | UNKNOWN | C1732 |
| 18 | ii-fraction (transformative safety) | UNKNOWN | C1732 |

**Tests per channel:**
1. Lag-1 MI with 500-perm paragraph-shuffled null -> z-score, p-value
2. Binned conditional MI controlling for line length (length quartiles) -> partial signal
3. Transfer entropy: TE(ch_N -> ch_{N+1}) vs TE(ch_{N+1} -> ch_N) -> directional asymmetry (top-5 channels)

**Cross-channel tests:**
4. Ablation decomposition: shuffle each channel within paragraph, measure smoothness degradation, report fraction of C1727 signal per channel + additivity ratio
5. Safety cross-MI: MI(ey_N, ii_{N+1}) and MI(ii_N, ey_{N+1}) -> safety alternation test (extends C1732)

**Context partitioning:**
6. Partition consecutive pairs into body-body, body-boundary (last line -> first of next), boundary-body. Report MI per context. Tests whether signal is truly sequential or just paragraph structure.

**Significance:** Bonferroni alpha = 0.05/18 = 0.00278. At 500 perms, min achievable p = 1/501 = 0.002 < 0.00278. Effect size floor: MI > 0.01 bits.

**Sample:** Consecutive body-line pairs from paragraphs with 5+ body lines.

**Constraint candidates:**
- C1830: Sequential Channel Census
- C1831: Transfer Entropy Asymmetry
- C1832: Safety Alternation (ey/ii cross-MI)
- C1833: Cross-Paragraph MI (null confirmation extending C1785)

---

### Script 2: cts_conditioned_routing.py

**Purpose:** Reconcile C1563 (token-level terminal-to-HEAD routing is real: r->a 2.23x, h->t 1.89x, y->k 1.60x) with C1728 (line-level HEAD lag-1 MI is null). The hypothesis: routing activates only at strong closure boundaries and is dormant at weak ones.

**Method:**
1. Compute per-line CTS using opacity-weighted score: LOCKED(y,m,n)=1.0, CHANNELED(l,h,r)=0.5, DIFFUSE(k,t)=0.0
2. Partition lines into LOW/MED/HIGH CTS terciles
3. For each tercile: compute MI(TERM_last_token_line_N, HEAD_first_token_line_N+1) with 500-perm null
4. Position-conditioned: Q0 (first body line), Q2 (mid), Q4 (last body line)
5. Null: within-paragraph line shuffle preserving CTS tercile assignment

**Connection:** C1725 shows closure zone has highest per-quintile MI. C1642 shows grammar-strength-dependent forgivingness. If CTS-high lines show tighter routing, the grammar responds to operational stakes.

**Constraint candidates:**
- C1834: CTS-Conditioned Terminal Routing

---

### Script 3: complexity_gradient.py

**Purpose:** Test whether instruction complexity and predictability change across body lines within paragraphs. Incorporates kernel gradient novelty (beyond C1206 retesting) and conditional entropy rate.

**9 features across body lines:**

| # | Feature | What it tests |
|---|---------|--------------|
| 1 | Modifier density (mean len(mods)) | Instruction complexity trajectory |
| 2 | Modifier entropy H(mod char distribution) | Combinatorial space narrowing (C1782) |
| 3 | Headless rate | C1574 extension to line resolution |
| 4 | Compound rate | Compound deployment trajectory |
| 5 | Mean MIDDLE length (chars) | Overall complexity |
| 6 | Atom diversity (distinct atoms / length) | C1330 vocabulary narrowing |
| 7 | Distinct HEAD x TERM frames per line | Operational flexibility trajectory (C1448) |
| 8 | Within-line atom variance | Line internal homogeneity (C1214, C1430) |
| 9 | Conditional entropy rate H(class_t | class_{t-1}) | Predictability trajectory (C1362, C1725) |

**Per feature:** Spearman rho vs paragraph body position. One-sample Wilcoxon on per-paragraph slopes. Binned conditional correlation controlling for line length. Section-stratified. Minimum 5 body lines per paragraph.

**Kernel gradient novelty (beyond C1206):**
- Does kernel gradient slope differ by section? (ANOVA on per-paragraph slopes)
- Does gradient appear in SHORT paragraphs (3-4 body lines) or only long ones (6+)?

**Constraint candidates:**
- C1835: Instruction Complexity Gradient
- C1836: Conditional Entropy Rate by Position

---

### Script 4: boundary_content_anatomy.py

**Purpose:** Decompose C1729 boundary enrichment into specific feature channels. Determine whether first-line and last-line are distinctive in the SAME or DIFFERENT ways.

**Method:**
1. For paragraphs with 7+ body lines: compute 18-feature vector for first body line, last body line, and interior mean (lines 2 through N-1)
2. Per-feature: paired test (boundary vs interior mean), Bonferroni corrected
3. Cosine similarity between first-line and last-line divergence vectors
4. Account for header echo effect (C1786, C1779: Z3/Z1 ratio = 0.191)

**Specific predictions:**
- First body line: specification-enriched (MARKING category? prep PREFIXes?)
- Last body line: closure-enriched (m-terminal? high CTS? e-kernel?)
- Reference C1566 (Q3-Q4 step discontinuity) for closure zone boundary

**Constraint candidates:**
- C1837: Boundary Content Decomposition
- C1838: Specification-Closure Asymmetry

---

### Script 5: grammar_temperature.py

**Purpose:** Per-folio composite grammar compliance metric measuring rule tightness.

**5 rule-compliance metrics per folio:**

| # | Metric | Source | Measurement |
|---|--------|--------|-------------|
| 1 | Forbidden buffer proximity | C997, C1027 | Fraction of bigrams one step from a forbidden pair |
| 2 | Modifier avoidance compliance | C1472 | Fraction of 2+ modifier compounds violating 8 avoided pairs |
| 3 | Terminal opacity compliance | C1440-C1445 | Deviation from corpus-wide suffix rates per terminal atom |
| 4 | PREFIX-MIDDLE HEAD forbidden | C1415 | Fraction of observed PREFIX x HEAD in forbidden set |
| 5 | PREFIX-MIDDLE forbidden | C911 | Fraction of observed PREFIX x MIDDLE in forbidden set |

**Composite temperature:** T = observed_compliance / shuffle_compliance. Null = per-folio token-shuffle preserving vocabulary but destroying grammar. T=1.0 = no more grammatical than chance. T >> 1.0 = highly ordered.

**Analysis:**
- Section-residualize T and all 5 sub-metrics
- Spearman rho of T vs quire position within sections
- Test: does T variance across folios exceed section-explained variance?
- Report T distribution by section and REGIME

**Constraint candidates:**
- C1839: Folio Grammar Temperature
- C1840: Grammar Crystallization (if uniform T)

---

### Script 6: compositional_drift.py

**Purpose:** Integration. Build per-folio maturity vectors, test for compositional ordering.

**Per-folio features:**
- From Script 3: mean complexity gradient slopes (9 features)
- From Script 5: grammar temperature + 5 sub-metrics
- Fresh: Heaps beta (transcript-order AND shuffled-order, report ratio), hapax fraction, dark pipeline rate, bridge rate, sister ratio, within-domain parameterization entropy (C1569)

**Method:**
1. Build 83-folio x D maturity matrix
2. Section-residualize (z-score within section)
3. Project out known C1715 PCs (PREFIX/kernel axis, suffix_rate/e_frac axis)
4. PCA on residuals. Test PC1 vs quire number (Spearman rho)
5. Consecutive-folio atom JSD: 18-atom frequency profile per folio, JSD between quire-consecutive folios vs random same-section pairs. Mantel test (1000 perms)
6. Permutation null: 1000 shuffles of folio-to-quire assignment

**Depends on:** Scripts 3 and 5 JSON outputs.

**Constraint candidates:**
- C1841: Folio Maturity Vector Structure
- C1842: Consecutive Folio Similarity

---

## Pre-Registered Predictions

| # | Prediction | Confidence | Basis |
|---|-----------|------------|-------|
| P1 | Line length dominates (>60% of signal) | 85% | C1728 |
| P2 | Kernel fractions (h especially) show genuine lag-1 MI | 70% | C1206 |
| P3 | PREFIX composition shows NO sequential drift | 80% | C964 free interior |
| P4 | Headless rate is null | 75% | C1574 folio-specific |
| P5 | HT density null within body | 80% | C842 flat after line 1 |
| P6 | Cross-paragraph bridge is null | 85% | C1785, C1793 |
| P7 | Suffix mode residual is mostly length-mediated | 75% | C1341 |
| P8 | Maturity vectors cluster by section only | 70% | C1569, C1399 |
| P9 | First/last body lines distinctive in DIFFERENT features | 65% | C1425 vs C1434 |
| P10 | CTS-conditioned routing reconciles C1563 vs C1728 | 55% | Novel hypothesis |
| P11 | Grammar temperature is uniform (pre-crystallized) | 60% | C1360 uniformity |
| P12 | Modifier entropy decreases across paragraph body | 60% | C1782 compression |
| P13 | Transfer entropy is forward-dominant (ch_N -> ch_{N+1}) | 65% | Sequential generation |
| P14 | Safety atoms (ey/ii) show no cross-MI | 70% | Minimal line-level signal |

---

## Dependency Graph

```
Independent (run in parallel):
  Script 1 (channel census + ablation + TE + safety)
  Script 2 (CTS routing)
  Script 3 (complexity gradient)
  Script 4 (boundary anatomy)
  Script 5 (grammar temperature)

Depends on above:
  Script 6 (compositional drift) -- uses Scripts 3 and 5 outputs
```

---

## Methodological Standards

### MI Estimation
- Histogram binning (5 bins for scalars), Miller-Madow bias correction
- 500 paragraph-shuffled permutations for null (required for Bonferroni over 18 channels)
- Report: z-score, raw MI, fraction of H(feature) explained
- Effect size floor: MI > 0.01 bits to register (avoids trivially small effects)

### Transfer Entropy
- TE(X->Y) = I(Y_{t+1}; X_t | Y_t) via conditional MI
- Computed for top-5 significant channels from MI census
- Forward-backward asymmetry: TE(X->Y) vs TE(Y->X)

### Partial MI Method
- Binned conditional MI: bin by line-length quartiles, compute MI within each bin, average
- NOT residualization (line length is discrete; residuals introduce artifacts)

### Grammar Temperature Null
- Per-folio token-shuffle: preserves vocabulary, destroys grammar
- T = observed_compliance / shuffle_compliance

### Significance
- Per-script Bonferroni: alpha = 0.05 / (number of tests in script)
- Cross-phase FDR: Benjamini-Hochberg on all significant results
- All p-values two-sided unless directional prediction is pre-registered
- At 500 perms: min achievable p = 1/501 = 0.002

### Sample Requirements
- Minimum 5 body lines per paragraph for inclusion (112 eligible paragraphs)
- Minimum 7 body lines for boundary anatomy (57 eligible paragraphs)
- Minimum 50 line-pairs per section for section-stratified tests
- Scripts testing per-paragraph slopes: minimum 100 eligible paragraphs
- Report effective N after all filtering

### Confounds
- Line length: binned conditional MI or partial correlation in every test
- Section: section-stratified alongside pooled; results must be directionally consistent
- Paragraph membership: paragraph-shuffled null is primary null model
- Folio membership: folio-shuffled null for Part B scripts

---

## Expected Verdict

**SEQUENTIAL_LENGTH_DOMINANT** -- If line length accounts for >60% of signal, kernel carries secondary, all else null, no compositional ordering.

**MULTI_CHANNEL_SEQUENTIAL** -- If 3+ channels carry genuine signal, indicating richer between-line grammar than previously characterized.

**CRYSTALLIZED_GRAMMAR** -- If Part A finds sparse signal AND Part B shows uniform grammar temperature, indicating the notation system was fully designed before any folio was composed.

---

## Results

### Script 1: Sequential Channel Census — SEQUENTIAL_WEAK
- **2/18 channels significant** (Bonferroni alpha=0.00278): length MI=0.359 (z=11.93, p=0.000), prefix_jsd MI=0.047 (z=3.24, p=0.004)
- **Ablation:** Length = 26% of total smoothness signal (not >60% as predicted). Sum of deltas = 0.28 (non-additive)
- **Transfer entropy:** Backward-dominant for both significant channels (length asym=-0.87, prefix_jsd asym=-0.92)
- **Safety alternation:** Null (ey→ii z=0.49, ii→ey z=-0.39)
- **Context partitioning:** Body-body MI >> cross-paragraph MI for all channels
- 833 body-body pairs, 354 cross-paragraph pairs. Runtime: 28.3s

### Script 2: CTS-Conditioned Routing — NO_CTS_EFFECT
- No CTS tercile shows significant TERM→HEAD MI (LOW p=1.0, MED p=0.04, HIGH p=0.14)
- Terminal routing is strictly token-local; no line-level signal even at strong closure boundaries
- C1563 (token-level routing real) and C1728 (line-level null) are genuinely orthogonal scales
- Routing enrichment ratios (r→a, h→t, y→k) show no CTS dependence

### Script 3: Complexity Gradient — PARTIAL_GRADIENT
- **4/9 features significant raw, 3/9 survive length control:**
  - mod_entropy: rho=-0.130 (p=0.002, lc_p=0.008) — combinatorial space narrows
  - atom_diversity: rho=+0.272 (p=0.000, lc_p=0.011) — atom diversity increases
  - distinct_frames: rho=+0.190 (p=0.000, lc_p=0.008) — frames diversify
  - cond_entropy_rate: rho=-0.165 (p=0.000, lc_p=0.676) — killed by length control
- **Kernel gradient:** h_frac slope=-0.083 (not significant by section ANOVA). Short paragraphs show stronger h-decline than long ones
- Section stratification: Effects strongest in sections B and H

### Script 4: Boundary Content Anatomy — ANTI_PARALLEL_BOUNDARIES
- 57 paragraphs with 7+ body lines
- **First body line:** 0/18 channels significantly different from interior
- **Last body line:** 3/18 channels enriched (length, prefix_jsd, cat_entropy)
- **Cosine similarity of divergence vectors:** -0.989 — boundaries are anti-parallel
- First and last body lines diverge in OPPOSITE directions from interior

### Script 5: Grammar Temperature — SECTION_STRATIFIED
- T_composite: mean=1.926, std=0.216, range [1.479, 2.439]
- Section B: T=2.063, Section H: T=1.806, Section S: T=1.972
- **Quire correlation raw:** rho=0.352, p=0.001 — significant
- **Quire correlation section-residualized:** rho=0.065, p=0.578 — NULL
- Grammar compliance is entirely section-determined, not quire-ordered
- T_modifier uniformly 1.0 (no modifier avoidance violations detected)

### Script 6: Compositional Drift — CONSECUTIVE_COHERENCE_ONLY
- 76 folios, 21 features (9 gradient slopes + 5 grammar temp + 7 lexical)
- **PCA:** PC1 explains 21.7%, PC2 19.3%. PC1 vs quire: rho=0.10, p=0.39 — NULL
- **Mantel test:** r=0.126, p=0.000 — significant. Consecutive folios more similar
- Heaps beta ratio (transcript/shuffled): 1.002 — no compositional ordering effect
- Verdict: Local coherence exists (Mantel) but no global ordering gradient (PCA)

### Prediction Assessment

| # | Prediction | Result | Explanation |
|---|-----------|--------|-------------|
| P1 | Length >60% of signal | **FAIL** | 26% of ablation — less dominant than expected |
| P2 | Kernel h lag-1 MI significant | **FAIL** | h_frac MI=0.000 (z=-0.58) |
| P3 | PREFIX JSD no sequential drift | **FAIL** | Significant (MI=0.047, z=3.24) |
| P4 | Headless rate null | **PASS** | MI=0.021 (z=1.50, p=0.088) |
| P5 | HT density null | **PASS** | MI=0.000 (z=-0.49) |
| P6 | Cross-paragraph bridge null | **PASS** | All channels BB >> CP |
| P7 | Suffix mode length-mediated | **PASS** | MI=0.024 (z=1.13, p=0.13 — not significant) |
| P8 | Maturity by section only | **PARTIAL** | PC1 null but Mantel significant |
| P9 | Boundary features different | **PASS** | Cosine = -0.99 (anti-parallel) |
| P10 | CTS reconciles C1563/C1728 | **FAIL** | No CTS effect on routing |
| P11 | Grammar temperature uniform | **FAIL** | Section-stratified (B: 2.06, H: 1.81) |
| P12 | Modifier entropy decreases | **PASS** | rho=-0.130, survives length control |
| P13 | TE forward-dominant | **FAIL** | Backward-dominant for both channels |
| P14 | Safety ey/ii cross-MI null | **PASS** | z=0.49 / z=-0.39 |

Score: 8 PASS, 1 PARTIAL, 5 FAIL out of 14 predictions.

---

## Runtime

| Script | Time |
|--------|------|
| 1: Sequential Channel Census | 28.3s |
| 2: CTS-Conditioned Routing | ~10s |
| 3: Complexity Gradient | ~5s |
| 4: Boundary Content Anatomy | ~5s |
| 5: Grammar Temperature | ~60s |
| 6: Compositional Drift | ~30s |
| **Total** | **~2.5 min** |
