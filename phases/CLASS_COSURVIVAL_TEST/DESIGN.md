# CLASS_COSURVIVAL_TEST

> **CORRECTED (2026-01-22):** Scripts now use the **strict interpretation** (C502) - only A-record MIDDLEs are legal. Previous union-based results were WRONG.

## Objective

Test which of the 49 instruction classes co-survive together when B vocabulary is constrained by different Currier A records.

## Research Questions

1. Do certain classes always survive together?
2. Are certain class pairs never seen together under A constraints?
3. Do classes within the same role co-survive more than across roles?
4. Do the 49 classes partition into functional subgroups?

## Methodology

1. Build bidirectional token/class/MIDDLE mappings
2. For each A record, compute which classes survive under **strict** legality (only A-record MIDDLEs)
3. Compute pairwise co-survival matrix
4. Identify equivalence groups

## Key Finding (CORRECTED)

**Class-level filtering is meaningful under strict interpretation.**

| Metric | Union (WRONG) | Strict (CORRECT) |
|--------|---------------|------------------|
| Unique patterns | 5 | **1,203** |
| Always-survive classes | 49 | **6** |
| Mean classes per A record | 49 | **32.3** |
| Infrastructure survival | 98-100% | **13-27%** |

The union model made class-level filtering appear trivially coarse. The strict model reveals:
- 34% of classes filtered on average
- Only 6 classes always survive (unfilterable core)
- Infrastructure classes are heavily filtered

## Scripts

| Script | Purpose |
|--------|---------|
| `build_class_token_map.py` | Map 480 tokens to 49 classes |
| `compute_survivor_sets.py` | Compute survivors per A record (STRICT) |
| `analyze_cosurvival.py` | Pairwise analysis and equivalence groups |
| `analyze_patterns.py` | Pattern inspection utility |

## Results

See [results/FINDINGS.md](results/FINDINGS.md) for detailed analysis.

## Potential Constraints

Based on strict interpretation findings:

| Finding | Status |
|---------|--------|
| Unfilterable core: 6 classes (7, 9, 11, 21, 22, 41) | Document as pattern |
| Infrastructure vulnerability (13-27% survival) | Contradicts union assumption |
| 1,203 unique class patterns | Validates C481 at class level |
| 34% mean class filtering | Extends C411 to class level |
