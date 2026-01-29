# C780: Role Kernel Taxonomy

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

## Constraint

The 5 functional roles partition kernel responsibilities distinctly:
- FL: 0% kernel (state index)
- EN: 92% kernel, h+e dominant (phase+stability operator)
- FQ: 46% kernel, k+e only, **0% h** (phase-bypass escape)
- CC: 25% kernel, but dominates forbidden pairs (control logic)
- AX: 57% kernel, balanced (auxiliary)

## Evidence

From t7_role_kernel_taxonomy.py:

**Role Kernel Summary:**

| Role | Tokens | Any Kernel | k% | h% | e% | Dominant Sig |
|------|--------|------------|-----|-----|-----|--------------|
| FL   | 1,078  | 0.0%       | 0.0% | 0.0% | 0.0% | none (100%) |
| CC   | 1,023  | 24.8%      | 16.6% | 8.2% | 18.6% | none (75.2%) |
| EN   | 7,211  | 91.9%      | 38.6% | 59.4% | 58.3% | h+e (35.8%) |
| FQ   | 2,890  | 46.0%      | 33.2% | 0.0% | 26.2% | none (54.0%) |
| AX   | 3,852  | 57.3%      | 29.5% | 26.4% | 37.7% | none (42.7%) |

**Kernel Character Dominance:**
- FL: NONE (kernel-free)
- EN: h (phase) at 59.4%
- FQ: k (energy) at 33.2%
- CC: e (stability) at 18.6%
- AX: e (stability) at 37.7%

**Forbidden Pair Participation:**
| Role | Appearances in 17 Forbidden Pairs |
|------|-----------------------------------|
| CC   | 20 (classes 10, 11, 12, 17)       |
| FQ   | 10 (classes 9, 23)                |
| EN   | 4 (classes 31, 32)                |
| FL   | 0                                 |
| AX   | 0                                 |

## Interpretation

Roles have distinct kernel strategies:

1. **FL (State Index):** Zero kernel - pure state labeling without modulation

2. **EN (Transformation):** Highest kernel (92%), h+e dominant - manages phase alignment and stability during state transitions

3. **FQ (Escape):** Moderate kernel (46%), k+e only with **0% h** - energy and stability without phase management. Escape routes bypass the phase system entirely.

4. **CC (Control):** Low kernel (25%) but dominates forbidden pairs (20 appearances) - control logic operates through class transitions, not kernel content

5. **AX (Auxiliary):** Balanced kernel (57%) - supporting role with no forbidden pair involvement

The partition suggests:
- Normal operation: FL → EN (phase-managed transformation)
- Escape: FL → FQ (phase-bypass via energy+stability)
- Control: CC mediates transitions (forbidden-pair gated)

## Provenance

- t7_role_kernel_taxonomy.json: role_stats, forbidden_pair_counts
- Relates to: C778-C779 (EN profile), C770-C777 (FL architecture)

## Status

CONFIRMED - Roles partition kernel responsibilities with distinct profiles.
