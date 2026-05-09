# Phase 691.1: Pre-Registered Predictions

**Locked:** 2026-05-09
**Status:** REGISTERED. No additions or modifications after first training run begins.

These predictions are committed BEFORE training. Each is testable against the trained LM with specified null distributions. PASS/FAIL is determined by criteria stated below — no post-hoc threshold adjustment.

---

## Universal requirements (apply to ALL predictions)

1. **Folio-shuffle null required.** For any embedding-based test, shuffle folio assignments and re-run. The effect must survive folio-shuffle (i.e., not be explainable by C531: 98.8% folios have unique MIDDLEs).
2. **Falsification framing.** Results phrased as "consistent/inconsistent with constraint Y," NEVER "the model learned X."
3. **Without-tag variant is primary.** Predictions evaluated on the without-tag model unless explicitly noted otherwise. The with-tag model is for sanity-check only.
4. **N=10 random seeds minimum** for any aggregate effect-size claim. Report mean ± std.
5. **Pre-registered baseline:** Random initial weights (untrained model) constitute the baseline for all probes. Effect must be significant *relative to this baseline*, not just non-zero.

---

## P1: Same-MIDDLE clustering tighter than same-PREFIX
**Source:** C508 (token-level Jaccard 0.700, 27.5% mutual exclusion), C121, C267

**Test statistic:** For each token pair (x, y), compute embedding cosine similarity. Define:
- `sim_middle` = mean cosine sim across all token pairs sharing the same MIDDLE
- `sim_prefix` = mean cosine sim across all token pairs sharing the same PREFIX (but not the same MIDDLE)

**Prediction:** `sim_middle > sim_prefix + 0.10` (effect size ≥ 0.10 in cosine space)

**Null:** Permute MIDDLE labels across tokens (preserving frequency distribution). Re-compute. Pass requires p < 0.01 (10K permutations).

**PASS criterion:** Effect size ≥ 0.10 AND p < 0.01.
**FAIL interpretation:** MIDDLE compositional structure (C267) is not visible in raw co-occurrence — the constraint's strength may be weaker than claimed, OR PREFIX is doing more work than C508 suggests.

---

## P2: Sister-pair near-mirror in embedding space
**Source:** C408 (ch↔sh), C409, C1539 (ok↔ot)

**Test statistic:** For each sister pair (e.g., `chedy` / `shedy`):
- `d_sister` = mean Euclidean distance between sister embeddings
- `d_random` = mean distance between same-frequency random pairs

**Prediction:** `d_sister < 0.5 × d_random` (sisters at least 2x closer than chance)

**Null:** Permute sister labels among matched-frequency token pairs. Compute null distribution.

**PASS criterion:** Ratio < 0.5 AND p < 0.01.
**FAIL interpretation:** Sister-pair claim (C408/C409/C1539) may be a phonetic/visual classification not reflected in distributional behavior. Would require revisiting whether ch/sh and ok/ot are functionally distinct or just orthographic variants.

---

## P3: PREFIX three-tier separation in embedding space
**Source:** C1218, C1534 (MODIFIER chars: q,d,f,p,y,s vs BASE chars: h,e)

**Test statistic:** Train a linear probe on character embeddings to predict {MODIFIER, BASE, OTHER}. Report 3-class accuracy.

**Prediction:** Linear probe accuracy ≥ 85% on held-out chars (well above 33% chance baseline).

**Null:** Same probe trained on character embeddings from random-init model.

**PASS criterion:** Trained model accuracy ≥ 85% AND ≥ 30 pp above random-init baseline.
**FAIL interpretation:** PREFIX three-tier grammar (C1218/C1534) is positional/syntactic, not represented in distributional character embeddings. Probe failure does NOT falsify C1218 directly — the constraint is about positional grammar, not embedding geometry.

---

## P4: A/B linear separability without orthogonality
**Source:** C239 (folio-disjoint), C335 (69.8% vocabulary integration), C272

**Test statistic:** Linear probe on token embeddings to predict {A, B}. Report accuracy. Also report cosine similarity between A-centroid and B-centroid.

**Prediction:**
- Probe accuracy ≥ 85% on held-out tokens (folio-stratified split)
- AB centroid cosine ≥ 0.6 (NOT orthogonal — 69.8% vocab integration)

**Null:** Folio-shuffle baseline. Probe on shuffled-folio model.

**PASS criterion:** Both conditions satisfied; folio-shuffle accuracy ≤ 65%.
**FAIL interpretation:**
- If accuracy LOW: A/B distinction is not in embedding space (challenges C239 separability via distributional means)
- If centroids ORTHOGONAL: 69.8% integration (C335) doesn't manifest geometrically — A/B might be more separable than the integration metric suggests

---

## P5: AZC forms third cluster, o-HEAD enriched
**Source:** C300-C311, C1502, C1559

**Test statistic:**
- 3-class linear probe (A/B/AZC), accuracy on held-out
- Among AZC tokens: frequency of o-HEAD MIDDLEs vs same in B

**Prediction:**
- 3-class accuracy ≥ 75% (lower bar — AZC has fewer tokens)
- o-HEAD enrichment in AZC ≥ 1.5x B baseline

**PASS criterion:** Both satisfied AND folio-shuffle accuracy ≤ 50%.
**FAIL interpretation:** AZC may not be structurally distinct from A/B at the token level (challenges C1502/C1559). Worth investigating whether AZC distinctiveness is purely positional rather than distributional.

---

## P6: Hub-MIDDLE peripherality (frequency vs structure orthogonality)
**Source:** C1011 (geometric independence of frequency manifold and macro-state automaton)

**Test statistic:**
- Compute token-frequency rank
- Compute embedding centrality (mean distance from corpus centroid)
- Pearson correlation between rank and centrality

**Prediction:** |corr| < 0.3 (weak correlation — frequency hubs ARE NOT structural hubs)

**PASS criterion:** |corr| < 0.3 AND folio-shuffle |corr| > 0.5 (i.e., effect persists only in real model).
**FAIL interpretation:** Frequency and structure are not orthogonal — C1011's geometric-independence claim fails. Hub MIDDLEs (C1011) would then be both frequent AND structural, simplifying the macro-state model.

---

## P7: Forbidden-bigram perplexity cliff
**Source:** C109, C783, C1118 (17 forbidden MIDDLE-MIDDLE transitions)

**Test statistic:** For each held-out forbidden bigram, compute LM perplexity at the second token's first character given context. Compare to:
- Random legal bigrams (matched frequency)

**Prediction:** Mean PPL on forbidden bigrams ≥ 5x mean PPL on random legal bigrams.

**PASS criterion:** Ratio ≥ 5.0 AND Mann-Whitney U test p < 0.001.
**FAIL interpretation:** The 17 forbidden transitions (C109/C783/C1118) are corpus statistics that the LM doesn't learn → suggests they're surface-level frequency facts, not deep grammatical constraints. Would require reframing C997 (safety buffer) as descriptive rather than enforced.

---

## P8: Cross-system MIDDLE invariance
**Source:** C1499, C1509 (Jaccard substrate identity across A and B)

**Test statistic:** For each MIDDLE that appears in both A and B (frequency ≥ 5 in each):
- `d_within_AB` = embedding distance between A-context and B-context occurrences
- `d_random_pair` = embedding distance for random folio pairs

**Prediction:** `d_within_AB < d_random_pair` AND ratio < 0.7.

**PASS criterion:** Ratio < 0.7 AND p < 0.01 (folio-shuffle null).
**FAIL interpretation:** Same MIDDLE in A vs B has divergent contextual usage — challenges substrate-identity claim (C1499/C1509). Would suggest A and B share orthography but not function for shared MIDDLEs.

---

## P9: Atom-level prediction from char embeddings
**Source:** C1394 (HEAD/MOD/TERM atom encoding, 18 atoms)

**Test statistic:** Linear probe to predict atom-class (HEAD, MOD, TERM) from character embeddings within a token. Report 3-class accuracy.

**Prediction:** Accuracy ≥ 80% (well above 33% chance).

**PASS criterion:** Accuracy ≥ 80% AND ≥ 40 pp above random-init baseline.
**FAIL interpretation:** Atom system (C1394) is a hand-built model not present in distributional structure. Direct falsification of compositional decomposition claim.

---

## P10: Currier-A folios more compressible than Currier-B (or equal)
**Source:** C124 (grammar universality), C229 (A/B disjoint vocabulary)

**Test statistic:** Per-folio average bits-per-char from trained LM.

**Prediction:** Currier A mean bits/char ≤ Currier B mean bits/char + 0.1 (allowing for size differences). NOT predicting strong inequality — predicting equality or A-slightly-easier (per C124's universality claim).

**PASS criterion:** A bits/char ≤ B bits/char + 0.1.
**FAIL interpretation:**
- If B << A in bits/char: A is harder to model, suggesting more diverse structure or more vocabulary spread
- If A << B by > 0.5: A is dramatically simpler, challenging "universal grammar" framing in C124

---

## Anomaly-detection auxiliary criterion (Phase 691.4)

**Not a primary prediction** — depends on transcript-error candidates from Phase 690 audit and 18-transcriber disagreement records.

**Auxiliary test:** Top 1% perplexity tokens (excluding hapax-only, controlling for token frequency). Cross-reference against:
- Phase 690 disputed-token candidates
- Tokens where 18-transcriber consensus diverges (≥ 3 transcribers disagree)

**Success metric:** Of top-1% perplexity tokens, ≥ 30% appear in transcriber-disagreement set.

This is exploratory, not pre-registered as PASS/FAIL.

---

## Summary table

| ID | Test | PASS criterion | FAIL implication |
|----|------|----------------|------------------|
| P1 | Same-MIDDLE > same-PREFIX clustering | effect ≥ 0.10, p < 0.01 | C267 weaker than claimed |
| P2 | Sister pairs near-mirror | ratio < 0.5, p < 0.01 | C408/C409 not distributional |
| P3 | PREFIX 3-tier linear probe | acc ≥ 85%, +30pp over baseline | C1218 positional only |
| P4 | A/B separable not orthogonal | acc ≥ 85%, cos ≥ 0.6 | C239 / C335 calibration |
| P5 | AZC distinct + o-HEAD enriched | acc ≥ 75%, o-ratio ≥ 1.5x | C1502 / C1559 |
| P6 | Frequency-structure independence | |corr| < 0.3 | C1011 geometric independence |
| P7 | Forbidden-bigram perplexity cliff | ratio ≥ 5.0, p < 0.001 | C109/C997 not learned |
| P8 | Cross-system MIDDLE invariance | ratio < 0.7, p < 0.01 | C1499/C1509 substrate |
| P9 | Atom-class linear probe | acc ≥ 80%, +40pp over baseline | C1394 not distributional |
| P10 | A/B bits-per-char comparable | A ≤ B + 0.1 | C124 grammar universality |

---

## Pre-registration commitment

**Author:** Joe DiPrima
**Date:** 2026-05-09
**Hash chain-of-custody:**
- SHA256 of file BEFORE registration line was added: `f9485cddb4cb146a548fc03f4bd5d791678f44454cc9a8e7329c05968aee2908`
- SHA256 of file AFTER registration line was added: `b52d991a2d11984544b3d11fe335c1fcb688b4c1f26534dce6208076b865516f`
- Final lock occurs when this file is committed to git. Any modifications after commit invalidate the registration.

I commit to:
- Reporting all 10 PASS/FAIL outcomes (no cherry-picking)
- NOT modifying thresholds based on observed results
- Using the without-tag model variant as primary
- Folio-shuffle nulls for all embedding-based tests
- Including N=10 seeds for any aggregate effect

**File hash will be committed to git BEFORE Phase 691.2 (training) begins.**

---

## Predicted aggregate outcome

If our structural model is broadly correct: 7-9 of 10 predictions PASS.

If our structural model is correct in framework but mis-calibrated: 5-7 PASS, 3-5 FAIL with informative directions (e.g., P6 fails → frequency-structure correlation revealed).

If our structural model is incorrect or radically over-fit: ≤4 PASS, multiple FAIL across compositional claims.

The most informative outcomes are **clean failures of P1/P3/P9** (compositional / atom claims), since these are the foundation of much of the structural work.
