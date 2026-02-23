# C1228 - PREFIX Channel Switching Within Paragraphs

**Tier:** 2 | **Scope:** B | **Phase:** APPARATUS_TRANSITION_DETECTION (Phase 438)

## Statement

73.2% of B paragraphs (202/276 with 3+ body lines) have at least one interior body line pair where PREFIX distribution divergence (JSD) matches or exceeds the header-to-body opening divergence. Interior JSD mean (0.470) is nearly as high as opening JSD mean (0.504). PREFIX operational channels routinely reset mid-paragraph, indicating the operational mode changes between processing cycles.

## Evidence

### PREFIX JSD statistics

| Metric | Value |
|--------|-------|
| Paragraphs tested | 276 |
| Opening JSD (header->body) mean | 0.504 |
| Interior JSD mean | 0.470 |
| Paragraphs with interior switch | 202 (73.2%) |

### Section rates

| Section | n | Switch rate |
|---------|---|-------------|
| B (BIO) | 82 | 75.6% |
| H (HERBAL) | 56 | 69.6% |
| S (STARS) | 119 | 71.4% |
| C | 15 | 93.3% |

### Key observations

1. **Switching is pervasive**: Nearly 3 in 4 paragraphs have at least one interior channel reset as large as the header-body transition
2. **Section-consistent**: All sections show >69% switch rate
3. **Interior ≈ Opening**: The operational channel divergence between body lines (0.470) approaches the header-body divergence (0.504), meaning body lines can be as operationally distinct from each other as the header is from the body

## Interpretation

Lines within a paragraph routinely change operational mode. This does not indicate apparatus switching (kernel gradient is smooth, Test A: 2.4% breakpoints) but rather reflects different cycles of the same process operating through different PREFIX channels. Combined with C1227 (FL partial reset), this supports a model where each line is one cycle of an iterative process, and the operational channel shifts between cycles as the process evolves.

## Related constraints

- C1001: PREFIX dual encoding (content channel + line position)
- C1044: Section-dependent phase interleaving
- C556: Line SETUP->WORK->CHECK->CLOSE positional grammar
- C1227: FL cross-line reset clustering (companion finding)

## Provenance

- `phases/APPARATUS_TRANSITION_DETECTION/scripts/apparatus_transition_detection.py` (Test C)
- `phases/APPARATUS_TRANSITION_DETECTION/results/apparatus_transition_results.json`
