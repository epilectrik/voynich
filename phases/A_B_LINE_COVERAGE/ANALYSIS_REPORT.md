# A-B Line MIDDLE Coverage Analysis

## Research Question

Do specific Currier A lines have unexpectedly strong vocabulary coverage of specific Currier B lines? If a single A line can cover >50% of a B line's MIDDLEs, this would suggest line-level correspondence.

## Methodology

1. **A Line Vocabulary**: For each A line, extract the set of token MIDDLEs (1,549 lines with 2+ MIDDLEs)

2. **B Line Vocabulary**: For each B line, extract the set of token MIDDLEs using only classified tokens from `class_token_map.json` (2,241 lines with 3+ classified MIDDLEs)

3. **Coverage Metric**: For each B line, find the A line with maximum coverage:
   ```
   coverage = |B_line_middles ∩ A_line_middles| / |B_line_middles|
   ```

4. **Random Baseline**: Shuffle A line assignments to establish chance-level coverage

## Key Findings

### 1. High Apparent Coverage

| Threshold | B Lines Meeting Threshold |
|-----------|---------------------------|
| >= 30%    | 100.0% |
| >= 50%    | 97.8%  |
| >= 70%    | 50.3%  |
| >= 100%   | 11.5%  |

Mean best-match coverage: **71.4%**

### 2. BUT: Coverage Equals Random Baseline

- Random mean best coverage: 67.4%
- Observed mean: 68.6%
- **Lift over random: 1.02x** (essentially none)

### 3. Coverage Driven by Shared Core Vocabulary

The classified B vocabulary consists of only **88 unique MIDDLEs**. ALL 88 appear in the A vocabulary.

Top MIDDLEs driving coverage:
| MIDDLE | A Count | B Count |
|--------|---------|---------|
| k      | 337     | 1,924   |
| edy    | 6       | 1,670   |
| aiin   | 265     | 798     |
| ey     | 268     | 710     |
| ol     | 778     | 697     |

**53% of coverage overlap comes from the top 10 MIDDLEs alone.**

### 4. No Rare MIDDLE Correspondence

When testing for shared rare MIDDLEs (those appearing in <=5 A lines):
- **0 B lines** have 2+ rare MIDDLE matches with any A line
- Only 0.3% of coverage overlap comes from rare MIDDLEs

### 5. Low Match Specificity

- 415 unique A lines serve as best matches for 2,241 B lines
- Top A line (f7v line 3) is best match for 82 different B lines
- Concentration ratio: 0.19 (same A lines match many B lines)

If there were true line correspondence, we would expect unique pairings.

## Interpretation

### Why Coverage Appears High

1. **Small Shared Vocabulary**: The classified B tokens use only 88 unique MIDDLEs, all present in A

2. **High-Frequency MIDDLEs**: These 88 MIDDLEs are the operational core - they appear in many lines of both A and B

3. **Statistical Inevitability**: With such concentrated vocabulary, any A line containing common MIDDLEs (like `k`, `ol`, `ey`, `aiin`) will "cover" any B line using those same MIDDLEs

### What This Means

The high coverage rates reflect **shared vocabulary inheritance**, not direct line-level templating. A and B share:
- A common grammatical substrate (~400 MIDDLEs appear in both)
- A concentrated operational core (88 MIDDLEs in classified B tokens)
- Similar distributional patterns

But they do NOT show:
- One-to-one line correspondence
- Rare vocabulary sharing
- Specific A lines matching specific B lines beyond chance

## Conclusion

**High coverage rates are an artifact of shared core vocabulary, not evidence of line-level correspondence.**

A single A line can cover 70%+ of many B lines because:
1. B's classified vocabulary is small (88 MIDDLEs)
2. A and B share these MIDDLEs
3. Any A line with common MIDDLEs matches any B line with the same

This finding is **consistent with the constraint system**:
- A and B share a common operational vocabulary (PP class)
- But A contains registry-specific content (RI class) that B does not use
- The shared vocabulary enables communication, not copying

## Files

- `run_coverage_test.py` - Initial coverage analysis
- `run_coverage_deep_analysis.py` - Core/rare MIDDLE breakdown
- `run_final_report.py` - Complete coverage statistics
- `run_vocabulary_comparison.py` - A-B vocabulary comparison
- `results/coverage_summary.json` - Summary statistics
