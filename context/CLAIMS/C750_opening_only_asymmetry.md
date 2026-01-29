# C750: Opening-Only HT Asymmetry

**Tier:** 0 — FROZEN FACT
**Phase:** B_LINE_POSITION_HT
**Scope:** Currier B, all folios

## Statement

The HT enrichment at folio boundaries is opening-only. The last line of B folios has 30.8% HT density, indistinguishable from interior lines at 29.8% (Wilcoxon p = 0.497). Folios have an asymmetric structure: an HT-enriched header at line 1, followed by uniform operational density through the final line.

## Evidence

| Position | Mean HT% | vs Interior p |
|----------|----------|---------------|
| Line 1 (first) | 50.2% | < 10^-6 |
| Interior (2 to N-1) | 29.8% | baseline |
| Line N (last) | 30.8% | 0.497 (ns) |

## Interpretation

Programs begin with identification but end without closure marking. This is consistent with a control system that runs to completion — the "end" is simply the absence of further instructions, not a formal termination signal using non-operational vocabulary.

## Depends On

- C747 (line-1 HT enrichment)
- C748 (step function)
- C233 (LINE_ATOMIC)

## Source

`phases/B_LINE_POSITION_HT/results/ht_line_position.json` (T6)
