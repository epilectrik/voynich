# A-B Paragraph Correspondence Test - Summary

## Question

Do specific Currier A paragraphs correspond to specific Currier B paragraphs?

Context:
- A paragraphs: 306, gallows-initial, RI header + PP body, ~20 PP MIDDLEs each
- B paragraphs: 585, gallows-initial, HT header + classified body, ~22 MIDDLEs each
- Both systems use paragraphs as operational units (C827, C840)

## Results

### Coverage Metrics by Granularity

| Level | Coverage | Baseline | Lift |
|-------|----------|----------|------|
| Line->Line | 56.2% | 10.3% | 5.44x |
| **Para->Para** | **64.2%** | **26.6%** | **2.41x** |
| Folio->Para | 73.0% | 42.7% | 1.71x |

### Key Findings

1. **Lift follows aggregation pattern**: As units get larger, coverage increases but lift decreases. This is expected - larger pools have more baseline overlap.

2. **Pool-size dominance confirmed**: Spearman rho=0.694 between A pool size and coverage. Larger A paragraphs achieve higher coverage.

3. **Many tied matches**: Mean 24.5 A paragraphs within 1% of best coverage (median 2). Only 47.7% of B paragraphs have a unique best match.

4. **Hub concentration**: Top 10 A paragraphs account for 85.9% of best matches. f101v2, f1r, f99v dominate.

5. **Pool-size-matched baseline**: When controlling for pool size, lift drops to 1.20x.

### Union Ceiling

- B paragraphs: 88.2% of MIDDLEs are in PP vocabulary
- Best-match achieves 72.8% of ceiling (75% of maximum possible)

## Interpretation

### What the lift means

The 2.41x lift at paragraph level is real but does NOT indicate specific A->B paragraph mapping. Instead:

1. **Selection effect**: Best-match always picks the A paragraph with the largest overlapping PP pool
2. **Hub dominance**: A few large A paragraphs serve as universal providers
3. **Vocabulary clustering**: PP MIDDLEs cluster in specific A paragraphs

### Why this isn't specific correspondence

If specific A->B paragraph pairing existed, we would expect:
- Unique best matches (found: only 47.7%)
- Rare MIDDLEs to show higher specificity (found: 60% vs 85% for common)
- Pool-size control to preserve lift (found: drops to 1.20x)
- B paragraphs to have unique vocabulary needs (found: 14.3% Jaccard overlap)

### Relationship to existing constraints

This finding is **consistent with** the existing architecture:

- **C384**: No A-B token coupling (confirmed at paragraph level)
- **C502**: Morphological filtering is vocabulary-based, not address-based
- **C735**: Pool size coverage dominance (confirmed at paragraph level)
- **C739**: Best-match specificity exists but is pool-size driven
- **C827**: Paragraphs are aggregation units for vocabulary pools

## Constraint Produced

| # | Name | Finding |
|---|------|---------|
| C846 | A-B Paragraph Pool Relationship | No specific A→B pairing; 39 A paragraphs serve 568 B; pool-size rho=0.694; raw lift 2.49x → 1.20x controlled |

## Conclusion

**NO SPECIFIC PARAGRAPH-TO-PARAGRAPH CORRESPONDENCE**

The A->B relationship is **POOL-BASED**, not **ADDRESS-BASED**:
- A paragraphs provide vocabulary pools (PP MIDDLEs)
- B paragraphs draw from these pools without specific A->B pairing
- Larger A paragraphs provide larger pools, hence higher coverage
- "Best match" is just "largest overlapping pool"

The paragraph structure in both systems serves **operational aggregation** (C827) - making larger pools available - not **referential addressing**.

## Files

- `paragraph_correspondence_test.py` - Initial test
- `investigate_hub_effect.py` - Hub analysis
- `rigorous_baseline_test.py` - Pool-size-controlled baseline
- `final_verdict.py` - Multi-granularity comparison
- `paragraph_correspondence.json` - Raw results
- `final_verdict.json` - Summary metrics
