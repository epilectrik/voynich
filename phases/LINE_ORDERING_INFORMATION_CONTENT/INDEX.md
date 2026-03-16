# Phase 595: LINE_ORDERING_INFORMATION_CONTENT

**Status:** COMPLETE
**Date:** 2026-03-15
**Constraints:** C1727, C1728, C1729

## Objective

Measure the total information content of line ordering within paragraphs across all channels simultaneously. Prior tests examined one channel at a time (vocabulary, category, suffix mode, hazard) and each found "no sequential signal" or "only folio-mediated." But many weak signals might sum to a meaningful total. Mode A/B persistence (C1423: 60.6% same-mode rate, CMI=0.029 bits) breaks pure independence — the question is whether mode persistence is the only sequential channel, or just one of several.

## Method

- **Data:** 82 qualifying paragraphs (>=6 body lines), 824 body lines from Currier B
- **Paragraph detection:** Using `par_initial` field from transcript; gallows-initial filter
- **Feature vector:** 15 dimensions per line: HEAD profile (6: a,e,o,k,t,headless), TERM profile (7: y,l,r,h,m,n,bare), suffix mode (1: binary A/B), line length (1)
- **Centering:** Subtract paragraph mean from each feature (no z-scoring with only 6-10 lines per paragraph)
- **Sequential structure score:** Sum of squared consecutive-line feature distances: Sigma ||f_{i+1} - f_i||^2
- **T2:** Total ordering information via 1000 within-paragraph shuffles + Stouffer's method
- **T3:** Full mode residualization — regress ALL features against mode label, recompute on residuals
- **T4:** Positional information — fractional quintile positions, permutation test per quintile
- **T5:** Per-channel lag-1 MI (suffix mode, dominant HEAD, dominant TERM, line length quartile)
- **T6:** Per-folio trajectory-based effect sizes

## Key Results

| Test | Metric | Value | Significance |
|------|--------|-------|-------------|
| T2 | Stouffer z | -6.048 | p < 0.001 |
| T2 | Mean effect size | -0.668 | Real ordering smoother than random |
| T2 | Paragraphs p<0.05 | 7/82 (8.5%) | Weak per-paragraph, strong aggregate |
| T3 | Stouffer z (mode-residualized) | -5.864 | p < 0.001 |
| T3 | Mean effect size | -0.648 | Barely changed from T2 (-0.668) |
| T3 | Mode contribution | ~3% | (T2 effect - T3 effect) / T2 effect |
| T4 | Q0 obs norm | 0.548 | p < 0.001 (4.5x null mean) |
| T4 | Q4 obs norm | 0.946 | p < 0.001 (7.9x null mean) |
| T4 | Q1 obs norm | 0.042 | p = 0.948 (indistinct) |
| T4 | Q2 obs norm | 0.355 | p = 0.033 (borderline) |
| T4 | Q3 obs norm | 0.325 | p = 0.058 (not significant) |
| T5 | suffix_mode MI | 0.044 bits | p = 0.001 (4.4% of H) |
| T5 | line_length MI | 0.178 bits | p < 0.001 (9.3% of H) |
| T5 | dominant_HEAD MI | 0.097 bits | p = 0.069 (not significant) |
| T5 | dominant_TERM MI | 0.050 bits | p = 0.473 (not significant) |
| T5 | Total significant MI | 0.222 bits | mode + length |
| T6 | Mean folio effect | -0.730 | 4/26 folios |effect|>2 |
| T6 | Strongest folio | f84v: -4.18 | score 92 vs null 348 |

## Interpretation

**Verdict: BOUNDARY_ENRICHED.** Line ordering carries substantial sequential information (T2: z=-6.05, p<0.001), and this information is almost entirely NOT explained by Mode A/B persistence (T3: z=-5.86 after full mode residualization, ~3% mode contribution). The sequential structure concentrates at paragraph boundaries: first body lines (Q0) and last body lines (Q4) carry distinctive content (T4: p<0.001 for both), while interior positions (Q1-Q3) are indistinct (p>0.03).

**Mode A/B is a minor channel.** The T3 mode-residualized test barely budges from T2 (effect: -0.648 vs -0.668, z: -5.86 vs -6.05). Mode persistence accounts for roughly 3% of sequential structure. This doesn't contradict C1423 (mode persistence is real at CMI=0.029 bits), but reveals it's a small fraction of the total ordering information.

**Line length is the dominant sequential channel.** T5 shows line_length MI = 0.178 bits (9.3% of H(length)), far exceeding suffix_mode MI = 0.044 bits (4.4% of H(mode)). Adjacent lines within paragraphs tend to have similar lengths. This is a physical/structural property — possibly reflecting layout constraints or scribal practice — rather than a linguistic one. HEAD and TERM routing show no significant lag-1 MI, confirming per-channel independence of compositional features.

**Boundary lines are compositionally distinctive.** T4 shows that Q0 (first body line after header) deviates from the paragraph mean by 4.5x the null expectation, and Q4 (last body line) by 7.9x. The last body line has the strongest positional signature. This connects to the within-line arc (C1425-C1430): if last body lines tend toward closure-heavy composition and first body lines toward specification-heavy composition, paragraph-internal ordering reflects a macro-arc from specification to closure across lines — not just within them.

**The signal is universal but section-graded.** All four sections show negative z (smoother than random): B (-3.70), C (-3.00), ? (-2.92), H (-1.75). All paragraph-length strata are significant: long (-4.83), medium (-3.27), short (-3.02). The effect is strongest in long paragraphs, which have more line-pairs for the sequential structure to manifest.

**Per-folio extremes.** f84v shows an extraordinary effect size of -4.18 (real score 92 vs null mean 348), indicating its line ordering is maximally smooth. f75r (-2.51), f83r (-2.08), and f116r (-2.10) also show strong effects. All are negative (smoother than random).

**Relationship to prior independence findings.** C670 (no vocabulary coupling), C1233 (cross-line MI < 1%), C1312 (sequential coupling tests fail), C1429 (adjacent lines categorically independent) all tested individual channels and found null results. This phase shows that when ALL channels are measured simultaneously, a coherent sequential signal emerges. The signal is driven primarily by line-length autocorrelation and boundary-position effects rather than by the compositional channels (HEAD, TERM, category) that the prior tests examined. The prior findings were correct: compositional channels carry no sequential signal. The ordering information lives in structural channels (length, position) that were never tested.

## Constraints

### C1727: Line ordering carries non-trivial sequential information
**Tier:** 2 (ESTABLISHED) | **Scope:** B

Within-paragraph body-line ordering carries substantial sequential structure: consecutive lines in real order are significantly smoother (more similar) than shuffled (Stouffer z=-6.048, p<0.001, mean effect=-0.668 across 82 paragraphs with 824 body lines). Only 8.5% of paragraphs are individually significant at p<0.05 — the signal is weak per-paragraph but highly consistent in direction (negative = smoother). Universal across all four sections (B: z=-3.70, C: z=-3.00, ?: z=-2.92, H: z=-1.75) and all paragraph-length strata (short: z=-3.02, medium: z=-3.27, long: z=-4.83). This revises the strong form of C670/C1233/C1429 (line independence): compositional channels are independent, but structural channels (length, boundary position) carry ordering information. The per-folio effect is consistently negative (mean=-0.73), with f84v showing the strongest effect (-4.18).

### C1728: Sequential information is NOT primarily Mode A/B persistence
**Tier:** 2 (ESTABLISHED) | **Scope:** B

Full mode residualization (regressing mode label out of ALL 15 features, not just removing the mode variable) barely changes the sequential signal: T3 z=-5.864 vs T2 z=-6.048, effect -0.648 vs -0.668. Mode A/B persistence accounts for approximately 3% of total sequential structure. The dominant sequential channel is line length (lag-1 MI=0.178 bits, 9.3% of H(length), p<0.001), which is 4x stronger than suffix mode (MI=0.044 bits, 4.4% of H(mode), p=0.001). Dominant HEAD and dominant TERM show no significant lag-1 MI (p=0.069 and p=0.473 respectively). This does not contradict C1423 (mode persistence CMI=0.029 bits is real) but reveals mode is a minor contributor to the ordering information budget. The compositional channels (HEAD, TERM, category) that prior independence tests examined carry no sequential signal; the ordering information lives in structural channels that were never tested individually.

### C1729: Paragraph boundary lines carry distinctive content (BOUNDARY_ENRICHED)
**Tier:** 2 (ESTABLISHED) | **Scope:** B

First body lines (Q0) and last body lines (Q4) deviate significantly from paragraph mean feature vectors: Q0 obs_norm=0.548 (4.5x null mean, p<0.001, n=181 lines), Q4 obs_norm=0.946 (7.9x null mean, p<0.001, n=206 lines). Interior positions are indistinct: Q1 p=0.948, Q2 p=0.033, Q3 p=0.058 (none significant at 0.01). The last body line (Q4) has the strongest positional signature, suggesting a paragraph-level macro-arc: first body lines carry one compositional signature (post-header specification?) and last body lines carry another (pre-close/closure?). This connects to the within-line specification-work-closure arc (C1425-C1430): position-dependent composition operates at both the within-line and within-paragraph scales. The boundary enrichment is the primary driver of the sequential smoothness detected in C1727 — lines at specific positions differ from the paragraph mean in consistent ways, making real ordering smoother than random.

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/line_ordering_information.py` | ~23 sec |

## Results

| File | Content |
|------|---------|
| `results/line_ordering_information_results.json` | Full results: T2-T6, per-paragraph detail, per-folio detail, controls, verdict |
