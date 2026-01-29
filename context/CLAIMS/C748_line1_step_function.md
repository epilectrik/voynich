# C748: Line-1 Step Function

**Tier:** 0 — FROZEN FACT
**Phase:** B_LINE_POSITION_HT
**Scope:** Currier B, all folios

## Statement

HT enrichment at folio opening is a sharp step function, not a gradient. Line position 1 has 50.2% HT density; position 2 drops immediately to 31.7%, and positions 3-10 remain flat at 27-33%. The enrichment is confined to a single line.

## Evidence

| Position | n folios | Mean HT% | SE |
|----------|----------|---------|----|
| 1 | 82 | 50.2% | 2.3% |
| 2 | 82 | 31.7% | 1.8% |
| 3 | 82 | 29.5% | 1.9% |
| 4 | 82 | 28.2% | 1.7% |
| 5 | 82 | 29.7% | 2.0% |
| 6 | 81 | 26.7% | 2.0% |
| 7 | 81 | 30.4% | 1.7% |
| 8 | 79 | 32.8% | 2.0% |
| 9 | 78 | 30.7% | 2.2% |
| 10 | 74 | 32.8% | 2.6% |

Mann-Whitney position 1 vs positions 2-5: U=20,852, p < 10^-6.

## Interpretation

The folio "header" is exactly one line. The transition from header to operational content is abrupt and complete. This matches the visual impression from manual folio inspection where opening lines appeared morphologically distinct from the working body.

## Depends On

- C747 (line-1 HT enrichment)
- C233 (LINE_ATOMIC — line is the control block unit)

## Source

`phases/B_LINE_POSITION_HT/results/ht_line_position.json` (T2)
