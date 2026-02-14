# C1028 — Vocabulary Curation Rule: Pairwise Co-occurrence Is Necessary and Dominant

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** VOCABULARY_CURATION_RULE (Phase 351)
**Depends on:** C1003, C1025, C267, C911

---

## Statement

The Currier B productive vocabulary (468 token types) occupies only 0.9% of the PREFIX × MIDDLE × SUFFIX product space (48,640 combinations from 32 PREFIXes × 76 MIDDLEs × 20 SUFFIXes). Token existence is governed by a single dominant rule: **both the PREFIX×MIDDLE pair AND the MIDDLE×SUFFIX pair must have been independently observed**. This pairwise co-occurrence gate has 100% recall (every existing token passes) and 58.4% precision (419 of 718 pairwise-compatible combinations exist). No higher-order "compiler rule" beyond pairwise compatibility is detectable: a depth-3 decision tree whose only effective features are `pm_cooc_exists` and `ms_cooc_exists` achieves 99.4% CV accuracy, matching the pairwise baseline. Additional curation within pairwise-compatible space (299 combinations that pass pairwise gate but don't exist) is consistent with finite-sample sparsity, not a structural constraint.

**Interpretation:** The vocabulary is determined by two independent pairwise filters (PREFIX selects MIDDLE families, MIDDLE selects SUFFIX options), confirming C1003 (no three-way synergy) and C911 (PREFIX×MIDDLE selectivity) from a generative/vocabulary perspective. There is no hidden compilation rule — the "compiler" is simply the conjunction of two pairwise compatibility filters.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Productive product space | 48,640 combinations |
| Existing tokens | 419 (0.9% occupancy) |
| Missing combinations | 48,221 (99.1%) |
| Pairwise-compatible combinations | 718 |
| Pairwise-compatible that exist | 419 (58.4%) |
| Tokens without pairwise support | 0 (0%) |

### Classifier Performance (5-fold CV)

| Classifier | CV Accuracy | Key |
|------------|-------------|-----|
| Decision tree depth 3 | 99.38% | Learns pairwise rule only |
| Decision tree depth 5 | 99.51% | Marginal improvement |
| Decision tree full | 99.81% | Overfits to 95 leaves |
| Logistic regression | 99.58% | pm_cooc (+8.42) and ms_cooc (+7.06) dominate |
| Baseline (PM+MS cooc) | 99.39% | Nearly matches best simple tree |

### Decision Tree (depth 3) Structure

The tree's only effective splits:
1. `ms_cooc_exists` (82.5% importance) — MIDDLE×SUFFIX pair ever observed?
2. `pm_cooc_exists` (17.5% importance) — PREFIX×MIDDLE pair ever observed?
3. All other features < 0.01% importance

### Logistic Regression Top Coefficients

| Feature | Coefficient | Direction |
|---------|-------------|-----------|
| pm_cooc_exists | +8.42 | Strongly predicts existence |
| ms_cooc_exists | +7.06 | Strongly predicts existence |
| middle_role_FL | -2.19 | FL MIDDLEs slightly less likely |
| log_middle_freq | -2.06 | High-frequency MIDDLEs slightly less likely (more selective) |

### Bare Component Effects

| Component | Existence Rate |
|-----------|---------------|
| Bare prefix (no prefix) | 3.9% |
| Non-bare prefix | 0.8% |
| Bare suffix (no suffix) | 8.7% |
| Non-bare suffix | 0.5% |

Bare components have higher existence rates because they represent simpler, more frequent forms.

---

## Implications

1. **No hidden compiler rule** — Vocabulary is determined by pairwise compatibility, not a higher-order constraint. C1003's "no three-way synergy" extends from information content to vocabulary membership.

2. **The vocabulary is a curated subset of pairwise-compatible space** — 58.4% of pairwise-compatible combinations actually exist. The 42% gap is consistent with finite-sample effects: less frequent pairwise-compatible combinations simply haven't appeared in 83 folios.

3. **PREFIX×MIDDLE is the primary filter** — This is the C911 forbidden pair system (102 forbidden combinations). MIDDLE×SUFFIX is the secondary filter. Together they gate vocabulary membership with zero false negatives.

4. **Phase 348's 4.2% M4 hallucination rate** was from conditional sampling (P(middle|prefix) × P(suffix|middle)), which already respects pairwise distributions. The residual 4.2% represents the gap between sampling from conditional distributions and the actual vocabulary — consistent with the 58.4% pairwise-compatible existence rate.

---

## Evidence

Results file: `phases/VOCABULARY_CURATION_RULE/results/vocabulary_curation_rule.json`
Script: `phases/VOCABULARY_CURATION_RULE/scripts/vocabulary_curation_rule.py`
