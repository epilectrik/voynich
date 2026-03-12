# Phase 584: ZODIAC_ASSIGNMENT_INFERENCE — Zodiac Sign Assignment by Category Coherence

**Status:** COMPLETE
**Verdict:** UNKNOWNS_ADD_NOISE
**Constraints:** C1685-C1688
**Runtime:** 5.47s

## Summary

Brute-force enumeration of all 12 valid zodiac sign assignments for 5 unidentified nymph folios. Uses the confirmed seasonal category signal (C1681, Phase 583) as the optimization target. The 7 confident visual-evidence anchors are fixed; 2 goat pages are constrained to {Aries, Taurus} (both Spring, per C1684) and 3 generic-animal pages to {Cancer, Capricorn, Aquarius}.

**Key finding:** The 12 assignments collapse to only **3 distinct seasonal groupings** because swapping signs within the same season produces identical chi-squared statistics. The only variable that matters is which of the 3 unknown folios gets assigned to Summer (Cancer). Even the best full-map assignment (V=0.113, perm_p=0.112) fails to beat the confident-only 7-folio baseline (V=0.157, perm_p=0.018). The unknown folios add noise, not signal.

## Results

### Assignment Ranking (3 distinct seasonal groupings)

| Group | Ranks | f72r3 | f71v/f72r1 | V | chi2 | p |
|-------|-------|-------|------------|---|------|---|
| **Best** | 1-4 | Cancer (Summer) | Capricorn/Aquarius (Winter) | 0.113 | 44.06 | 0.002 |
| Mid | 5-8 | Winter | One=Cancer, one=Winter | 0.098 | 32.72 | 0.049 |
| Worst | 9-12 | Winter | f71v=Cancer (Summer) | 0.092 | 28.78 | 0.119 |

### Permutation Validation (best assignment)

| Metric | Value |
|--------|-------|
| Observed chi2 | 44.06 |
| Permutation p | 0.112 |
| Valid perms | 10,000 |
| Verdict | NOT CONFIRMED |

### Comparison vs Confident-Only Baseline (Phase 583)

| Map | Folios | V | perm_p |
|-----|--------|---|--------|
| Confident-only (Phase 583) | 7 | 0.157 | 0.018 |
| Best full map (this phase) | 12 | 0.113 | 0.112 |

## Constraint Verdicts

| ID | Claim | Status |
|----|-------|--------|
| C1685 | ZODIAC_MAP_NOT_INFERRED | Full-map permutation p=0.112, does not reach significance. 12-folio seasonal signal too dilute for inference |
| C1686 | WITHIN_SEASON_DEGENERATE | Swapping signs within the same season produces identical chi2/V. The 12 nominal assignments collapse to 3 distinct seasonal groupings |
| C1687 | UNKNOWNS_DEGRADE_SIGNAL | Best 12-folio V=0.113 < confident-only V=0.157. Adding the 5 unknown folios weakens the seasonal signal regardless of assignment |
| C1688 | F72R3_SEASONAL_ASSIGNMENT | f72r3=Cancer (Summer) is the only resolved seasonal placement. Top 4/12 assignments all share f72r3=Summer. f71v and f72r1 both assigned to Winter in all top assignments |

## Key Findings

1. **Within-season sign swaps are invisible.** Goat ordering (Aries/Taurus) doesn't matter because both are Spring. The f71v/f72r1 Capricorn/Aquarius swap doesn't matter because both are Winter. This is structural: a season-level test cannot resolve within-season ordering.

2. **f72r3 is the diagnostic folio.** It's the only unknown whose seasonal assignment affects the chi-squared statistic. When f72r3=Cancer (Summer), V=0.113. When f72r3=Winter, V drops to 0.092-0.098. This is because f72r3 has the most tokens (163) and its category profile fits Summer better than Winter.

3. **Unknowns add noise at every assignment.** The confident-only baseline (V=0.157) beats the best 12-folio result (V=0.113). This means the 5 unknown folios have category profiles that don't cleanly fit any seasonal pattern — their "generic animal" centers correlate with ambiguous category distributions.

4. **The confident-only subset remains canonical.** Phase 583's 7-folio map (C1681) is not improved by adding the unknowns. Future zodiac-category work should use the confident-only subset unless new visual identifications become available.

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/zodiac_assignment_inference.py` | 5.47s |

## Files

- `results/zodiac_assignment_inference.json` — Full results with all 12 assignments
