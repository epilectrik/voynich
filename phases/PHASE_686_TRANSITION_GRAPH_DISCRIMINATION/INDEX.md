# Phase 686: Transition-Graph Structural Discrimination

**Status:** COMPLETE — 4 constraints drafted (C1996-C1999), 3 pass / 1 directional negative
**Started:** 2026-05-06
**Completed:** 2026-05-06
**Goal:** Import two structural metrics from Earnhart (2026) — circuit rank μ on the token-transition graph, and per-token successor entropy H_succ — and test whether they (a) replicate Earnhart's order-constraint result on our filtered H-track, (b) discriminate among our existing classifications (sections, REGIMEs, RI/PP/INFRA token classes) beyond vocabulary-size confounds.

## Results summary

| Test | Verdict | Headline |
|------|---------|----------|
| T1 (C1996) | **PASS** | Earnhart's μ-vs-shuffle result replicates: gap = −1782 (their −1831), z = −38.3 |
| T2 (C1997) | **PASS** | Mean per-folio z_μ = −1.27, 87/115 folios negative, 0/115 above +2 |
| T3 (C1998) | **DIRECTIONAL NEGATIVE** | INFRA H_succ HIGHER than RI in Currier B (reversed from prediction) |
| T4 (C1999) | **PASS** | Sections differ in z_μ: S/C/B ≈ −2.0 most constrained, H = −0.30 weakest |

## Background

Earnhart's "Harmonic-Topological Analysis" (April 2026) reports that the actual Voynich manuscript has lower circuit rank than frequency-shuffled controls (μ_actual=22,675 vs μ_shuffle=24,506) on the full IVTFF/Takahashi extraction (37,967 tokens). Their analysis stops at corpus level. We have a richer taxonomy (sections, REGIMEs, RI/PP/INFRA token classes, atom system) that lets us test whether these new metrics discriminate at finer granularity — and crucially, whether they add information beyond what vocabulary size already explains.

The pre-registration discipline: predictions and thresholds locked before computing. Each outcome (pass or fail) registers as a constraint.

## Definitions (locked)

**Token transition graph G:**
- Nodes V = unique token types
- Edges E = unordered pairs (s_i, s_j) where s_j follows s_i somewhere in the sequence
- **Self-loops excluded** (Earnhart Remark 4.2 — required for well-defined incidence matrix; consistent with our practice of treating same-token repetition separately per C1789)
- c = number of connected components

**Circuit rank** μ = |E| − |V| + c

**Successor entropy** H_succ(s) = −Σ_s' p(s'|s) log_2 p(s'|s)
- p(s'|s) = empirical conditional next-token probability
- Computed per token type with frequency n ≥ 3 (sparse-conditional control)

**Frequency-shuffle null:** random permutation of the token sequence preserving exact unigram counts. 1000 permutations per corpus-level test, 200 per folio-level test.

**Per-folio z-score:** z_μ(f) = (μ_f − mean(μ_shuffle_f)) / std(μ_shuffle_f) where shuffles are within-folio.

## Locked methodology

| ID | Spec |
|----|------|
| M1 | Transcribers: H-track only (`transcriber == 'H'`) |
| M2 | Placement: TEXT only (exclude `placement.startswith('L')`) |
| M3 | Tokens: exclude empty, exclude `'*' in word` |
| M4 | Token = exact word string (no morphological normalization) |
| M5 | Self-loops excluded from incidence graph |
| M6 | Section labels from Transcript metadata (H/B/S/C/A — A=Currier_A) |
| M7 | REGIME assignment from external REGIME map (C494, RecordAnalyzer) |
| M8 | Token class from RecordAnalyzer (RI / PP / INFRA / UNKNOWN) |
| M9 | H_succ computed only for tokens with n≥3 occurrences |
| M10 | Per-folio analysis: each folio is one observation |
| M11 | RNG seed = 42 throughout |
| M12 | Number of shuffles: 1000 corpus-level, 200 per-folio |

## Pre-registered tests

### T1 — Corpus-level replication of Earnhart

**Hypothesis:** Full-corpus μ_actual < mean(μ_shuffle) at one-sided p<0.001 over 1000 frequency-shuffles.

**Statistic:** Compute μ on full filtered H-track (≈37,957 tokens). Compute mean and std of μ over 1000 shuffles preserving unigram counts. Report z = (μ_actual − mean_shuffle) / std_shuffle.

**Pass:** z < −3.09 (one-sided p<0.001) AND replication direction matches Earnhart.

**Fail:** z ≥ −3.09 → flag filtering or implementation discrepancy with Earnhart, investigate before T2-T4.

**Constraint registered (regardless of outcome):** C1996.

### T2 — Per-folio order constraint

**Hypothesis:** Per-folio z_μ averaged across all folios is significantly negative (one-sample t-test p<0.001), confirming order constraints persist at folio level not just corpus aggregate.

**Statistic:** For each folio with n≥100 tokens: compute z_μ(f) over 200 within-folio shuffles. Take mean across folios; one-sample t-test against 0.

**Pass:** mean z_μ < 0 AND one-sample t-test p<0.001.

**Fail:** Order-constraint signal is corpus-aggregate only, individual folios don't reliably show it. Useful negative result.

**Constraint registered:** C1997.

### T3 — Token class predicts successor entropy

**Hypothesis (one-sided):** E[H_succ | INFRA] < E[H_succ | RI] at Mann-Whitney U test p<0.01, with mean difference > 0.3 bits.

**Reasoning:** INFRA tokens are infrastructure/glue. If they function as formulaic position markers, their successors should be more constrained than RI (recipe-internal/content) tokens.

**Statistic:** Per-token H_succ for all token types in Currier B with n≥3. Group by RecordAnalyzer class. MWU one-sided test (INFRA < RI).

**Pass:** MWU one-sided p<0.01 AND |E[INFRA] − E[RI]| > 0.3 bits AND direction is INFRA < RI.

**Fail (multiple modes):**
- p ≥ 0.01 → no detectable difference, classification orthogonal to predictability
- Direction reversed (INFRA > RI) → INFRA tokens have *more* varied successors, contradicting the formulaic-glue interpretation

**Constraint registered:** C1998.

### T4 — Section × order-constraint magnitude

**Hypothesis:** Per-folio z_μ from T2 differs across sections (H/B/S/C). Specifically, predict B has more negative mean z_μ than H (B more order-constrained even after vocabulary-size normalization).

**Statistic:** Kruskal-Wallis across all four sections; post-hoc Mann-Whitney B vs H.

**Pass:** Kruskal-Wallis p<0.05 AND post-hoc B vs H p<0.05 AND mean(z_μ_B) < mean(z_μ_H).

**Fail:** Sections differ in raw μ (driven by vocabulary size) but not in *order-constraint magnitude* once normalized. Would suggest the structural complexity differences are content-driven, not order-driven.

**Constraint registered:** C1999.

## Constraint registration plan

Four constraints will register regardless of pass/fail outcomes. Tiers determined by results:

| ID | Topic | Tier if pass | Tier if fail |
|----|-------|--------------|--------------|
| C1996 | Corpus μ-vs-shuffle gap | 2 (structural fact) | flag-only (replication failure) |
| C1997 | Per-folio order constraint | 2 (structural fact) | 2 (negative result, also informative) |
| C1998 | Token class × H_succ | 2 (structural fact) | 2 (orthogonality is also a structural fact) |
| C1999 | Section × order-constraint magnitude | 2 (structural fact) | 2 (negative result) |

All four register at minimum at Tier 2 because the metric definitions are precise and the methodology is locked.

## Anti-HARK commitments

- Test order is fixed: T1 first; if it fails, T2-T4 still run but with discrepancy flag attached.
- No threshold adjustment after seeing results.
- No re-binning of tokens, REGIMEs, or sections after seeing results.
- Token classes (RI/PP/INFRA) frozen at whatever RecordAnalyzer returns at execution time.
- If T3's predicted direction is wrong, that registers as a directional negative — not a "revision" to two-sided.

## Computational plan

**Script s1: full corpus T1**
- Build full-corpus transition graph
- Compute μ_actual, μ_shuffle distribution
- Output: `results/t1_corpus_replication.json`

**Script s2: per-folio T2**
- For each folio: build folio graph, compute z_μ
- One-sample t-test on z_μ across folios
- Output: `results/t2_per_folio_zscores.json` + summary

**Script s3: token H_succ + T3**
- Compute H_succ per token type (n≥3) on full corpus
- Tag each token with RecordAnalyzer class
- MWU INFRA vs RI
- Output: `results/t3_hsucc_by_class.json`

**Script s4: T4 section comparison**
- Use folio z_μ from s2, grouped by section
- Kruskal-Wallis + post-hoc
- Output: `results/t4_section_zmu.json`

**Script s5: register**
- Aggregate all four results
- Generate constraint text for C1996-C1999
- Output: `results/constraint_drafts.md`

## Expected runtime

Transition graphs are small (≤8K nodes for full corpus, ≤1K per folio). All four tests should complete within 30 minutes total on standard hardware. The 1000-shuffle corpus null is the longest single operation (~5-10 min).

## Detailed results

### T1: Corpus replication — PASS

| Quantity | Value |
|----------|-------|
| Tokens (filtered H-track) | 37,429 |
| Unique types | 7,904 |
| μ_actual | 22,380 |
| mean(μ_shuffle) | 24,162 |
| std(μ_shuffle) | 46.49 |
| z | −38.33 |
| Gap | −1,782 |
| Earnhart gap (reference) | −1,831 |
| Empirical p | 0.001 (Monte Carlo floor at 1/1000) |

Pre-reg threshold `z < -3.09 AND replication direction matches Earnhart` met overwhelmingly. Empirical p hit Monte Carlo floor — all 1000 shuffles strictly exceeded μ_actual, so p ≤ 1/1000 = 0.001. The parenthetical "(one-sided p<0.001)" in the pre-reg was the parametric interpretation of z<-3.09 under normality, not a separate empirical p threshold; z = −38.3 corresponds to a parametric one-sided p < 1e−300. **Verdict: PASS.**

### T2: Per-folio order constraint — PASS

| Quantity | Value |
|----------|-------|
| N folios analyzed (n_tokens ≥ 100) | 115 |
| Mean z_μ | −1.266 |
| One-sample t (df=114) | −8.66 |
| One-sided p | < 1e−13 |
| Folios with z_μ < 0 | 87/115 (76%) |
| Folios with z_μ < −2 | 33/115 (29%) |
| Folios with z_μ > +2 | 0/115 |

Order constraints are not a corpus-aggregate artifact — they manifest at individual-folio scale on the great majority of pages. **Verdict: PASS.**

### T3: Token class predicts H_succ — DIRECTIONAL NEGATIVE

| Class | N types | mean H_succ | example tokens |
|-------|---------|-------------|----------------|
| INFRA | 54 | 2.890 bits | daiin (n=314, H=7.30), dar (n=188, H=6.80), saiin (n=99, H=6.07) |
| RI | 6 | 2.295 bits | qotcheedy (n=4, H=2.0), chcthhy (n=5, H=2.32), qokshedy (n=11, H=3.28) |
| PP | 897 | 2.979 bits | chedy (n=491, H=7.47), ain (n=79, H=5.87) |
| UNKNOWN | 75 | 1.986 bits | — |

Predicted direction: E[H_succ | INFRA] < E[H_succ | RI]. Observed: E[INFRA] > E[RI] by 0.60 bits. MWU one-sided p (in predicted direction) = 0.539. **Direction reversed.**

**Mechanism note:** INFRA tokens in Currier B are high-frequency function elements (daiin, dar, saiin) with many opportunities for distinct successors. RI tokens in Currier B are rare (n=3-11 in observed sample) with H_succ mechanically bounded by log₂(n_with_successor). The pre-registered prediction conflated "formulaic role" with "predictable next-token" — they are not equivalent at our sample sizes.

**Pre-reg discipline preserved:** Prediction failed in registered direction. Result registers as directional negative (C1998), no revision to two-sided form.

### T4: Section × order-constraint magnitude — PASS

Per-folio z_μ by section (sorted by mean):

| Section | n folios | mean z_μ |
|---------|----------|----------|
| S (Pharmaceutical/Stars) | 23 | −2.041 |
| C (Cosmological) | 11 | −1.959 |
| B (Biological/Balneological) | 20 | −1.950 |
| Z (Zodiac) | 6 | −1.196 |
| T (Text/Recipe-like) | 5 | −1.122 |
| P (Pharmaceutical) | 14 | −0.930 |
| A (Astronomical) | 3 | −0.744 |
| H (Herbal) | 33 | −0.304 |

By Currier language:

| Language | n | mean z_μ |
|----------|---|----------|
| Currier A | 31 | −0.816 |
| Currier B | 69 | −1.397 |
| AZC (NA) | 15 | −1.594 |

| Test | Result |
|------|--------|
| Kruskal-Wallis H (df=6) | 27.73, p = 0.0001 |
| Post-hoc B vs H MWU two-sided | z = −3.60, p = 0.0003 |
| Direction (B < H) | Confirmed |

**Verdict: PASS.**

## Constraint Drafts (revised post expert validation)

### C1996 (Tier 2, Scope: GLOBAL): Token-transition order constraints exceed unigram-frequency expectations (full corpus)

On the H-track filtered corpus (n=37,429 tokens, |V|=7,904 types, no labels, no asterisks, self-loops excluded), the token-transition graph circuit rank μ_actual = 22,380 is dramatically lower than mean(μ_shuffle) = 24,162 over 1000 frequency-preserving shuffles (z = −38.3, gap = −1,782). Replicates Earnhart 2026 result (gap −1,831 on his 37,967-token extraction). Empirical p hit Monte Carlo floor (1/1000) — all 1000 shuffles strictly exceeded μ_actual. Token-graph circuit rank deficit is a graph-theoretic measurement of the same constraint phenomenon captured at class level by **C389 (low bigram conditional entropy, H=0.41 bits)** and **C1025 (49-class Markov + symmetric forbidden suppression sufficiency)**. Convergent evidence via a metric that does not reference instruction-class taxonomy. Compatible with C109 (forbidden transitions), C361 (adjacent-folio vocab sharing), C1808 (section qo-rate baselines). External replication of Earnhart 2026.

### C1997 (Tier 2, Scope: GLOBAL): Per-folio token-transition order constraint is widespread but heterogeneous

Of 115 folios with ≥100 tokens, mean per-folio z_μ (computed against 200 within-folio frequency-shuffles) is −1.266 (one-sample t = −8.66, df = 114, one-sided p << 1e−13). 87/115 folios (76%) show negative z_μ; 33/115 (29%) below −2; 0/115 above +2. Order constraint is not a corpus-aggregate artifact — it manifests at individual-folio scale on the great majority of pages, but with substantial section heterogeneity (per C1999). **Length-confound caveat:** regression z_μ ~ log(n_tokens) yields slope = −1.14 (t=−4.95, p<0.0001, R²=0.18). The effect is partly size-amplified: small folios (n=100) project to z_μ ≈ −0.40 (weakly constrained), large folios (n=613) project to z_μ ≈ −2.47 (strongly constrained). The order constraint is genuine even at small sizes but is amplified at larger token counts. Cross-section heterogeneity per C1999 dominates the size effect within sections.

### C1998 (Tier 2, Scope: B): INFRA token successor entropy exceeds RI in Currier B (predicted direction REVERSED)

Pre-registered prediction (Phase 686): E[H_succ | INFRA] < E[H_succ | RI] in Currier B, MWU one-sided p<0.01, gap > 0.3 bits. **Result: REVERSED.** INFRA tokens (n=54 types in B with n≥3, includes daiin n=314 H=7.30, dar n=188 H=6.80, saiin n=99 H=6.07) have mean H_succ = 2.89 bits, which is 0.60 bits HIGHER than RI tokens (n=6 types, mean H_succ = 2.29). MWU one-sided p in predicted direction = 0.539. Directional negative result. **Mechanism (per C498.b/C498.d):** RI tokens in B are predominantly rare singletons or near-singletons by definition (~977 RI singletons per C498.b; mean ~4.82 chars per C498.b; length-frequency correlation per C498.d). Their H_succ is mechanically bounded by log₂(n_with_observed_successors). The pre-registered test as designed cannot distinguish predicted formulaic-glue effect from rarity-driven H bound. Falsification preserved as registered. The RI/PP/INFRA classification axis does NOT predict transition predictability in the direction we expected. **Forecloses retest of this hypothesis without explicit frequency-matched controls** — any future test must match INFRA and RI samples on token count before computing H_succ. Methodologically equivalent to C415, C946, C947 directional negatives.

### C1999 (Tier 2, Scope: GLOBAL): Section-level order-constraint magnitude varies systematically

Per-folio z_μ (transition-graph circuit rank vs within-folio frequency-shuffle null) differs across sections at Kruskal-Wallis H = 27.7, df = 6, p = 0.0001. Pre-registered post-hoc Currier B vs Herbal: mean z_μ_B = −1.95 (n=20), mean z_μ_H = −0.30 (n=33), MWU two-sided p = 0.0003. Direction matches prediction (B more order-constrained than H). Section ordering: S (−2.04, n=23), C (−1.96, n=11), B (−1.95, n=20) most order-constrained; Z (−1.20), T (−1.12), P (−0.93), A (−0.74) intermediate; H (−0.30, n=33) weakest. By Currier language: AZC (−1.59) > Currier B (−1.40) > Currier A (−0.82). z_μ controls for vocabulary size via folio-specific shuffles, so section effect is not a raw vocabulary-size artifact. **REGIME mediation caveat (per C1404):** Section S in particular is dominated by REGIME_3/REGIME_4 folios; the strong S z_μ may be partly a REGIME-composition effect rather than a pure section property. REGIME-stratified analysis not performed in this phase to preserve pre-reg discipline. **Length-confound caveat:** per C1997, z_μ has size dependence; section effect could be partly mediated by section-typical folio length. **A weakest ranking is consistent with C233 (LINE_ATOMIC) and C234 (POSITION_FREE)** — A genuinely has less sequential structure between tokens. **AZC strongest is consistent with C302 (distinct line structure), C311 (positional grammar), C313 (position constrains legality)** — AZC has tighter positional grammar than running-text systems. Complements C1404 (section structural differentiation) and C1808 (section qo-rate baselines). Section-level z_μ is descriptive measurement; functional interpretation reserved as Tier 3 follow-up.

## Methodological notes from execution

**T1 verdict adjudication:** My script's `pass_p` check (p<0.001 strict) was unreachable at 1000 shuffles where the minimum achievable empirical p = 1/1000 = 0.001. The actual pre-reg threshold was `z < -3.09 AND direction matches Earnhart`; the parenthetical "(one-sided p<0.001)" was the parametric interpretation of z<-3.09 under normality. Adjudicated PASS based on the literal pre-reg criterion. The script's "FAIL" output is preserved as recorded for transparency, but the adjudicated verdict is PASS. For future phases: separate empirical-p thresholds need shuffle counts ≥ 10,000.

**T3 directional discipline:** The prediction failed in the registered direction. Per Phase 686 anti-HARK commitments and our project standard (memory: Earnhart's "revised BEH" example), the failure is registered as directional negative. The constraint is NOT revised to a two-sided form. The mechanism analysis (frequency confound) is documented but does not retroactively change the verdict.

## Scripts

- `s1_t1_corpus_replication.py` — full-corpus μ vs 1000 freq-shuffles
- `s2_t2_per_folio.py` — per-folio z_μ via 200 within-folio shuffles, t-test
- `s2b_length_confound.py` — supplementary length-confound regression on T2 (post-expert revision)
- `s3_t3_hsucc_by_class.py` — H_succ per token type, MWU INFRA vs RI
- `s4_t4_section_zmu.py` — Kruskal-Wallis across sections, post-hoc B vs H
- `s5_aggregate_register.py` — adjudicate verdicts, draft constraints

## What this phase confirms / refutes from Earnhart 2026

| Earnhart claim | Our finding |
|----------------|-------------|
| μ_actual < mean(μ_shuffle) on full corpus | **Confirmed** (our gap −1,782 vs his −1,831) |
| Currier B more complex than A | **Confirmed at section level** (B z_μ −1.40 vs A −0.82) |
| Order constraints beyond unigram | **Extended to per-folio level** (76% of folios show negative z_μ) |
| BEH (one-sided A>B entropy) | Not directly tested; consistent with Earnhart's null |

What we add beyond Earnhart:

- Per-folio z_μ as a normalized (vocabulary-controlled) order-constraint metric
- Section-level stratification of z_μ (his analysis stops at Currier-language level)
- AZC-section z_μ measurement (Earnhart did not isolate AZC)
- Test of RI/PP/INFRA classification against successor entropy (failed in predicted direction)

## Limits

- T3 negative result is partly mechanism-driven (RI tokens rare in B yields capped H_succ). A future test could match-on-frequency before comparing classes. **Not done in this phase per pre-reg discipline** — re-running with new methodology would be HARK.
- Per-folio z_μ for very small folios (n_tokens < 100) was excluded; some short folios may have signal we don't capture.
- Earnhart's exact extraction filtering differs slightly (37,967 vs our 37,429) — gap-magnitude difference (−1,831 vs −1,782) is consistent with this filtering delta plus shuffle Monte Carlo noise.

## Relationship to existing constraints

- **C109** (forbidden transitions) — provides specific transition prohibitions; T1 tests aggregate order-constraint magnitude
- **C361** (adjacent-folio vocab sharing) — folio-level effects must control for this
- **C494** (REGIME assignment) — provides REGIME labels for testing
- **C1106** (e-depth marginal preservation) — frequency-shuffle is the analogous null at unigram level
- **C1404** (section structural differentiation) — T4 directly tests this on new metrics
- **C1789** (local repetition) — self-loop exclusion controls for this
- **C1808** (section qo-rate baselines) — analog of section-level structural baselines
- **C1994** (S vs B token-level e-depth coupling) — distinct mechanism, complementary

## External reference

Earnhart, D. (2026). "Harmonic-Topological Analysis of the Voynich Manuscript as Generator-Class Discrimination." Self-published, voynichframework.com. Used for: μ definition, frequency-shuffle null methodology, full-corpus reference values for replication check (μ=22,675, shuffle μ=24,506).

Independent verification: their token count (37,967) matches our filtered H-track count (37,957) within ±10 (editorial-marker handling difference). Provides external sanity check on our pipeline.

## Methodological notes

- **Why μ at folio level needs per-folio normalization:** raw μ scales with effective vocabulary, so cross-folio comparison requires the within-folio z-score to control for that. Earnhart did not do this; we add it.
- **Why H_succ requires n≥3:** for tokens with n=1 or n=2, H_succ is degenerate (n=1 has no successor; n=2 has at most 2 distinct successors). Threshold n=3 is the minimum for meaningful conditional distribution.
- **Why one-sided directional tests:** specific predictions stake direction in advance. Earnhart's BEH "revision" example illustrates the cost of two-sided testing after directional failure.
