# Phase 691.4 — Anomaly Detection Results

**Date:** 2026-05-09
**Method:** Per-token pseudo-likelihood (mask each char, predict, mean log-prob)

## Pre-registration outcome

The pre-reg's auxiliary criterion (≥30% of top-1% surprise tokens have ≥3 transcribers disagreeing) was NOT met — but for a different reason than expected:

- Top-1% surprise overlap rate with ≥3-transcriber-disagree: **6.3%**
- Eligible baseline rate: **4.1%**
- Enrichment: **1.55x**
- Permutation p-value: **0.035**

The signal is **statistically significant but modest**: LM surprise IS correlated with transcriber disagreement, but not strongly enough to dominate. The 30% target was unrealistic given the baseline disagreement rate is only 4.1%.

| Top % | n | Overlap | Baseline | Enrichment | p-value |
|---|---|---|---|---|---|
| 0.5 | 158 | 7.6% | 4.1% | 1.86x | 0.032 |
| 1.0 | 316 | 6.3% | 4.1% | 1.55x | 0.035 |
| 2.0 | 633 | 7.6% | 4.1% | 1.85x | <0.001 |
| 5.0 | 1584 | 8.0% | 4.1% | 1.96x | <0.001 |

Effect strengthens at top-2% and top-5% (lower variance with more samples). LM surprise is a weak-but-real signal for transcriber disagreement.

## The more interesting finding: anomaly type

Looking at WHICH tokens the LM flags:

**Top-30 highest-surprise tokens (top 1%):**

| Token | Folio | Line | Surprise | n_disagree |
|---|---|---|---|---|
| `c` | f66r | 22 | 7.99 | 1 |
| `c` | f57v | 1 | 7.56 | 2 |
| `x` | f66r | 32 | 7.28 | 0 |
| `x` | f57v | 1 | 7.26 | 2 |
| `x` | f66r | 24 | 7.21 | 0 |
| `e` | f49v | 20 | 7.12 | 2 |
| `t` | f113v | 5 | 7.11 | 2 |
| `x` | f66r | 10 | 6.66 | 0 |
| `c` | f75r | 42 | 6.50 | 3 |
| `a` | f68r3 | 7 | 6.37 | 0 |
| `e` | f49v | 13 | 6.36 | 3 |
| `f` | f66r | 15 | 6.32 | 0 |
| `e` | f49v | 5 | 5.83 | 2 |
| `g` | f67r1 | 3 | 5.82 | 4 |
| `f` | f57v | 1 | 5.76 | 2 |
| `oy` | f112v | 13 | 5.50 | 0 |
| `k` | f49v | 7 | 5.41 | 2 |
| `r` | f66r | 20 | 5.38 | 1 |
| `x` | f57v | 1 | 5.36 | 2 |
| `k` | f49v | 25 | 5.29 | 2 |

**Pattern: 26 of top 30 are single-character or two-character tokens from known-anomalous folios.**

### Folio breakdown

- **f66r** (7 tokens): the "character key / glossary" page identified in Phase 684 — known to contain isolated single chars
- **f57v** (5 tokens): numerology page with the unusual AZC single-char ring (C763/C764)
- **f49v** (5 tokens): zodiac/special folio with unusual short tokens
- **f67r1, f68r3, f113v, f75r, f112v, f105r, f106v, f23v, f27v, f40r, f76r**: scattered single-char anomalies

### What this means

**The LM independently rediscovered the same anomalous folios that structural research has already noted.** This is corroboration of Phase 684 (f66r as character key) and prior identification of f57v, f49v as structurally distinct from the main corpus.

The LM treats single-char tokens as highly surprising because the H-track corpus is ~99% multi-char tokens. So the surprise metric essentially classifies tokens by length anomaly. In itself this is not a NEW discovery — but it does demonstrate the LM is capturing real distributional structure.

## Useful follow-up: stratified anomaly detection

The current top-1% list is dominated by length anomalies. To find more interesting anomalies (semantic/structural rather than length-based), the next analysis should:

1. **Stratify by token length** — compute surprise rank within each length bucket (3-char, 4-char, 5-char, etc.)
2. **Within each length, look at top 1-2%** — these are anomalies given their length
3. **Cross-reference against transcriber disagreement** at this stratified level

This would surface tokens like `qokeey` that are unusually surprising for a 6-char token, rather than `x` which is just an unusual length.

## Constraint candidates

- **C2006** (Tier 2): LM-surprise correlates with 18-transcriber disagreement (1.55-1.96x enrichment, p<0.05). Modest external validation of transcriber-disagreement as anomaly signal.
- **C2007** (Tier 2): LM independently identifies known-anomalous folios (f66r, f57v, f49v) as outlier-rich via length-anomaly surprise. Corroborates Phase 684 character-key identification.

## Next analyses

- **691.4b** — Stratified anomaly detection (within-length surprise ranking)
- **691.5** — Token-level reformulation of forbidden-bigram test (P7 redo)
- **691.6** — Three-LM comparison

## Files

- [`overlap_report_without_tag.json`](overlap_report_without_tag.json) — full numerical results
- [`lm_surprise_per_token_without_tag.jsonl`](lm_surprise_per_token_without_tag.jsonl) — raw per-token surprise (37,091 records)
- [`transcriber_disagreement.jsonl`](transcriber_disagreement.jsonl) — per-position disagreement records
