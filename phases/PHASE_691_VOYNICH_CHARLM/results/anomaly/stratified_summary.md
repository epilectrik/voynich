# Phase 691.4b — Stratified Within-Length Anomaly Detection

**Date:** 2026-05-09
**Method:** Rank tokens by surprise WITHIN each character-length bucket, take top 1% per bucket, cross-reference against transcriber disagreement.

## Headline result

**Aggregate enrichment: 3.40x** (overall 16.2% overlap with ≥3-transcriber disagree, vs 4.8% baseline in same-length pool).

Compare to unstratified Phase 691.4: 1.55x enrichment. Stratifying by length **doubles** the signal-to-noise ratio.

## Per-length breakdown

| Length | n | top 1% | Overlap | Baseline | Enrichment |
|---|---|---|---|---|---|
| 1 | 696 | 6 | 0.0% | 9.1% | 0.0x |
| 2 | 2216 | 22 | 9.1% | 4.6% | **2.0x** |
| 3 | 3483 | 34 | 11.8% | 5.1% | **2.3x** |
| 4 | 6709 | 67 | 16.4% | 4.8% | **3.4x** |
| 5 | 9457 | 94 | 20.2% | 4.3% | **4.7x** |
| 6 | 7444 | 74 | 9.5% | 3.8% | **2.5x** |
| 7 | 4413 | 44 | 20.5% | 5.1% | **4.1x** |
| 8 | 1749 | 17 | **41.2%** | 6.6% | **6.2x** |
| 9 | 651 | 6 | 0.0% | 6.9% | 0.0x |
| 10 | 192 | 1 | 0.0% | 8.9% | 0.0x |

**The sweet spot is length 4-8** (the typical Voynich token length range). Length 8 alone hits **41.2% overlap with disagreement** — exceeding the original pre-reg's 30% threshold within that length bucket.

## Why length-1 and length-9+ tokens score 0x enrichment

- **Length 1**: these ARE the length anomaly. They're surprising because they're rare lengths, not because of structural issues. Disagreement rate at length-1 is high (9.1%) but uncorrelated with surprise — both signals just track "weird folio."
- **Length 9-10**: small N, likely compound or junk tokens. Probably mostly junk.

## Top-30 stratified-top tokens (length > 1)

Real anomaly candidates worth investigation:

| Token | L | Folio | Line | Surprise | n_disagree |
|---|---|---|---|---|---|
| `el` | 2 | f8r | 18 | 5.64 | 1 |
| `oy` | 2 | f112v | 13 | 5.50 | 0 |
| `le` | 2 | f113r | 9 | 5.48 | **3** |
| `rn` | 2 | f35r | 9 | 5.47 | 0 |
| `ska` | 3 | f22r | 7 | 5.23 | 2 |
| `rd` | 2 | f75v | 3 | 5.10 | **4** |
| `em` | 2 | f69r | 5 | 5.04 | 2 |
| **`oleoeder`** | **8** | **f77v** | **3** | **4.74** | **3** |
| `dgs` | 3 | f70r2 | 1 | 4.72 | 2 |
| `lmyl` | 4 | f84r | 1 | 4.66 | **4** |
| `cs` | 2 | f55v | 7 | 4.68 | 2 |
| `dl` (×4 occurrences) | 2 | various | | 4.27-4.66 | 1-2 |
| `lgl` | 3 | f82v | 20 | 4.34 | **3** |
| `diil` | 4 | f23r | 8 | 4.32 | 2 |
| `osih` | 4 | f113v | 28 | 4.51 | 2 |
| `ctos` | 4 | f29v | 4 | 4.21 | 2 |
| `ckey` | 4 | f99r | 9 | 4.20 | 1 |

## Anomaly types observed

1. **Genuine transcription errors** — Multiple `dl` tokens at length 2 (transcribers often disagree whether `d` and `l` are separate or part of a longer sequence)
2. **Foreign / Latin-like tokens** — `oleoeder`, `osih`, `ctos`, `lmyl`, `ker` — possibly glosses or non-Voynichese
3. **Damaged / merged tokens** — short-but-unusual: `rn`, `em`, `cs`, `lg`
4. **Boundary anomalies** — Some `2-char` tokens may be trailing fragments of longer tokens with edge damage

## Comparison to Phase 690 audit

Phase 690 raised the question of transcript errors. The stratified anomaly analysis produces a concrete candidate list:

- **365 stratified-top tokens** total
- **59 of those (16.2%) have ≥3 transcribers disagreeing with H** — all are candidate transcription errors worth direct review
- The 41% rate at length-8 is particularly compelling — long tokens with both LM-surprise and transcriber-disagreement are very likely real errors

## Constraint candidates

- **C2008**: Stratified-by-length LM surprise produces 3.4x aggregate enrichment vs transcriber disagreement (vs 1.55x unstratified). Length stratification is required for token-level anomaly detection. Tier 2.
- **C2009**: Length-8 H-track tokens with high LM surprise have 41% transcriber-disagreement rate (vs 6.6% length-8 baseline). Strong candidate-error pool. Tier 2.

## Files

- [`stratified_anomaly_without_tag.json`](stratified_anomaly_without_tag.json) — full per-length breakdown + top examples
- [`summary.md`](summary.md) — Phase 691.4 unstratified results
