# C1063: PREFIX-SUFFIX Compatibility Constraints

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE (Phase 380)
**Extends:** C911 (102 forbidden PREFIX x MIDDLE), C278 (hierarchy), C539 (LATE prefix class)
**Relates to:** C1059 (suffix-role independence), C588 (role-suffix strata), C275 (pairwise interactions)

---

## Statement

The PREFIX x SUFFIX space contains **17 forbidden combinations** (expected >= 5, observed = 0), confirming C278's hierarchy prediction: PREFIX constrains SUFFIX less than MIDDLE (17 vs 102 forbidden pairs).

| Measure | Value |
|---------|-------|
| Common PREFIXes tested | 30 (>= 50 tokens) |
| Common SUFFIXes tested | 21 (>= 50 tokens) |
| Total tokens | 22,792 |
| Chi² | 8703.4 (p = 0.0) |
| Cramér's V | 0.138 |
| Forbidden pairs | **17** |
| Enriched pairs (z > 3.0) | 50 |
| Depleted pairs (z < -3.0) | 57 |

Role-composition decomposition (C588): 1/17 forbidden pairs are role-explained, **16/17 are genuinely novel** PREFIX-SUFFIX constraints — not mediated by role composition.

Top forbidden (by expected count):

| PREFIX | SUFFIX | Expected |
|--------|--------|----------|
| ta | edy | 20.4 |
| ar | edy | 11.7 |
| sa | y | 9.6 |
| lch | y | 9.2 |
| yk | al | 8.9 |

Top enriched: qo x edy (z=+32.5), qo x eey (z=+24.3), qo x ain (z=+22.4), ch x hy (z=+18.2).
Top depleted: qo x BARE (z=-37.3), ch x edy (z=-8.9), da x edy (z=-8.5).

LATE prefix prediction (C539) NOT confirmed: al has 0 forbidden suffixes, ar has 1, or has 1. Despite 68-70% suffix depletion, LATE prefixes have sufficient tokens in the remaining 30% to avoid zero cells.

ch/sh each have 0 forbidden suffixes — broadest SUFFIX compatibility confirmed.

---

## Interpretation

The 17:102 ratio (PREFIX x SUFFIX vs PREFIX x MIDDLE) quantifies C278's hierarchy: PREFIX's primary selectivity targets MIDDLE (family selection), with SUFFIX as a weaker secondary constraint. The V=0.138 (PREFIX x SUFFIX) vs V used in C911 for PREFIX x MIDDLE confirms SUFFIX is the less constrained axis.

The dominant pattern is qo's extreme suffix selectivity: qo x edy is enriched at z=+32.5 (nearly 3x expected), while qo x BARE is depleted at z=-37.3. This means qo-prefixed tokens are almost never bare — they require specific suffixes. Combined with C1059 (suffix carries independent role info), this shows qo uses suffix to specify sub-role within its family.

The 16 novel forbidden pairs (not role-explained) establish genuine PREFIX-SUFFIX incompatibility beyond what role composition predicts. These represent structural constraints in the morphological assembly system.

---

## Method

- 22,792 Currier B tokens with common PREFIXes (>= 50) and common SUFFIXes (>= 50)
- C911 methodology: expected from marginal products, forbidden = expected >= 5 AND observed = 0
- Role decomposition: per-PREFIX role distribution weighted by C588 per-role bare rates
- Forbidden pairs with expected non-bare rate < 0.05 classified as role-explained

**Script:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/scripts/morphological_joint_space.py`
**Results:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t1_prefix_suffix_forbidden.json`
