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

## Post-Hoc Functional Reading (Informal)

Atom-level HEAD/TERMINAL profiles across the 7 confident zodiac pages reveal a coherent annual workflow gradient:

| Season | a(yield) HEAD | e(cool) HEAD | k(heat) HEAD | r(input) TERM | y(end) TERM |
|--------|---------------|--------------|--------------|---------------|-------------|
| Spring | **30.2%** | 25.9% | 0% | **12.9%** | 13.7% |
| Summer | 23.1% | 33.9% | 0.5% | 5.9% | 20.4% |
| Autumn | 17.4% | **40.9%** | 0.7% | 8.1% | 14.4% |
| Winter | **8.2%** | 40.2% | **5.2%** | **3.1%** | **25.8%** |

- **yield(a)** drops monotonically Spring→Winter (30%→8%): material extraction tapers off
- **heat(k)** appears only in Winter (5.2%): external heating when ambient temperature drops
- **input(r)** terminal declines Spring→Winter (13%→3%): new material stops coming in
- **end(y)** terminal rises toward Winter (14%→26%): processes reach completion

This gradient is consistent with a real annual workflow (not random grouping): Spring extracts fresh materials, Summer processes to defined endpoints, Autumn runs sustained cooling operations, Winter manages temperature and closes out processes.

The unknown folios show mixed profiles that straddle seasonal boundaries — f71v profiles as Spring-like (high yield + input), f72r3 profiles as Autumn-like (high cool + work) despite the category test preferring Summer. This mismatch between category-level and atom-level assignment may explain why they add noise.

Not formalized as constraints (n=1 per season for Spring/Winter, informal analysis).

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/zodiac_assignment_inference.py` | 5.47s |

## Files

- `results/zodiac_assignment_inference.json` — Full results with all 12 assignments
