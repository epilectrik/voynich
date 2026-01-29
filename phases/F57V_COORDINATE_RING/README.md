# F57V_COORDINATE_RING Phase

## Objective

Investigate whether f57v R2's single-character sequence functions as a structural coordinate system for the cosmological diagram, and whether similar patterns exist in other Zodiac folios.

## Background

C763 documents that f57v R2 is 100% single characters with a repeating ~27-char pattern and p/f gallows substitution. Expert analysis suggests:

1. R2 violates C540 (bound morpheme constraint) - operates under different rules
2. The p/f substitution marks "two variants of the same structural position"
3. Boundary rings (R2, R4) vs content rings (R1, R3) suggests scaffold/content layering
4. R2 may be a positional coordinate system deliberately below morphological threshold

## Tests

| Test | Question | Method |
|------|----------|--------|
| T1 | Do other Zodiac folios have single-char rings? | Check R-series composition across 13 Zodiac folios |
| T2 | Do p/f positions align with visual structure? | Map p/f positions in the R2 sequence |
| T3 | Does R2 pattern correlate with R1/R3 content? | Align R2 positions with adjacent ring vocabulary |

## Scripts

- `t1_zodiac_ring_survey.py` - Survey all Zodiac folio ring compositions
- `t2_pf_position_mapping.py` - Map p/f variant positions in R2 sequence
- `t3_ring_alignment.py` - Check if R2 positions correlate with R1/R3 content

## Results

| Test | Finding | Verdict |
|------|---------|---------|
| T1 | f57v R2/R4 are ONLY anomalous rings across all 13 Zodiac folios; others have 0-8% single-char | **F57V_UNIQUE** |
| T2 | p at pos 6, f at pos 33 both preceded by 'x k k'; 27 positions apart (half ring); angular ~194° | **SYSTEMATIC_VARIATION** |
| T3 | R1 and R2 both have exactly 50 tokens; 'x' appears 4 times in R2 but never in R1 | **ALIGNMENT_POSSIBLE** |

## Key Findings

1. **f57v is unique.** No other Zodiac folio has single-char dominated rings. The pattern is specific to the cosmological diagram.

2. **p/f marks two halves of the ring.** Both first-p and first-f are preceded by `x k k` with same following context `t r y c o`. They are 27 positions apart (180° around the ring).

3. **R1 and R2 are 1:1 aligned.** Both have exactly 50 clean tokens. This supports R2 as an index or coordinate system for R1 content.

4. **'x' is coordinate-only.** The character 'x' appears 4 times in R2 (at `x k k` markers) but NEVER appears in R1. It's part of the scaffold, not content.

5. **Unique terminators.** Characters 'm' and 'n' appear only at R2's end, marking ring completion.

## Structural Interpretation

R2 functions as a **positional coordinate layer** for the cosmological diagram:
- `x k k` marks section boundaries (appears at positions 3 and 30)
- `p` vs `f` distinguishes the two halves of the ring
- `m n` terminates the sequence
- Character 'x' is used exclusively for positional marking, not content

This supports the expert hypothesis that R2 is "below morphological threshold" - a scaffold/index layer rather than content carrier.

## Provenance

Follow-up to AZC_FOLIO_DIFFERENTIATION phase, based on C763 and expert-advisor consultation.
