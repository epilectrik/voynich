# CLASS_COSURVIVAL_TEST

> **PARTIAL SUPERSESSION NOTE (2026-01-22):**
> The legality computation in `compute_survivor_sets.py` used a **union-based model** (aggregating MIDDLEs from matched AZC folios). This model was later discovered to be WRONG - see MEMBER_COSURVIVAL_TEST for the correct **strict interpretation** (only A-record MIDDLEs are legal).
>
> **What remains valid:** Class-level findings (98.4% identical patterns, all 49 classes survive) are unaffected because classes survive under BOTH models. The class-level coarseness is real.
>
> **What is superseded:** Token-level survivor counts from this phase. Use MEMBER_COSURVIVAL_TEST results for token-level analysis.

## Objective

Test which of the 49 instruction classes co-survive together when B vocabulary is constrained by different Currier A records.

## Research Questions

1. Do certain classes always survive together?
2. Are certain class pairs never seen together under A constraints?
3. Do classes within the same role co-survive more than across roles?
4. Do the 49 classes partition into functional subgroups?

## Methodology

1. Build bidirectional token/class/MIDDLE mappings
2. For each A record, compute which classes survive AZC filtering
3. Compute pairwise co-survival matrix
4. Identify equivalence groups

## Key Finding

**Class-level filtering is extremely coarse.** 98.4% of A records produce identical survivor sets (all 49 classes). Only 5 unique patterns exist despite 1,575+ unique MIDDLE-level patterns (C481).

## Scripts

| Script | Purpose |
|--------|---------|
| `build_class_token_map.py` | Map 480 tokens to 49 classes |
| `compute_survivor_sets.py` | Compute survivors per A record |
| `analyze_cosurvival.py` | Pairwise analysis and equivalence groups |
| `analyze_patterns.py` | Pattern inspection utility |

## Results

See [results/FINDINGS.md](results/FINDINGS.md) for detailed analysis.

## Proposed Constraints (NOT YET ADDED)

> **Note:** These were proposed but not formally added. C502 was later used for a different constraint (A-Record Viability Filtering). If adding these, use C503+.

- Class-level filtering coarseness (5 patterns from 1,579 A records)
- Unfilterable core classes [7, 9, 11, 21, 22, 41]
- Infrastructure class vulnerability (98.4-98.8% survival, not 100%)
