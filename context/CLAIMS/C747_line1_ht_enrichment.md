# C747: Line-1 HT Enrichment

**Tier:** 0 — FROZEN FACT
**Phase:** B_LINE_POSITION_HT
**Scope:** Currier B, all folios

## Statement

The opening line (position 1) of Currier B folios has dramatically elevated HT (unclassified token) density compared to all subsequent lines. Mean line-1 HT fraction is 50.2% vs 29.8% for lines 2+, a +20.3 percentage point enrichment.

## Evidence

| Metric | Value |
|--------|-------|
| Folios analyzed | 82 |
| Mean line-1 HT fraction | 50.2% |
| Mean lines-2+ HT fraction | 29.8% |
| Mean delta | +20.3pp |
| Direction | 69 positive / 0 zero / 13 negative |
| Wilcoxon signed-rank | W=3127, p < 10^-6 |
| Paired t-test (one-sided) | t=8.955, p < 10^-6 |
| Cohen's d | 0.989 |
| Permutation test (10,000x) | z=11.07, p=0.0000 |

The effect is present in all major sections:
- H (Herbal): +27.1pp, p=0.0000 (32 folios)
- B (Bio): +19.1pp, p=0.0004 (20 folios)
- S (Stars/Recipe): +14.7pp, p=0.0006 (23 folios)

## Interpretation

Opening lines of B folio-programs contain a disproportionate concentration of vocabulary outside the 49-class operational grammar. This is consistent with a "header" or "identification" zone that uses non-operational vocabulary before the executable control sequence begins.

## Depends On

- C166 (HT identification)
- C740 (HT = UN population identity)
- C404 (HT non-operational)

## Source

`phases/B_LINE_POSITION_HT/results/ht_line_position.json` (T1, T5)
