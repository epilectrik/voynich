# C781: FQ Phase Bypass

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

## Constraint

FQ (Frequency/escape role) has exactly 0% 'h' (phase) characters while maintaining 33.2% 'k' (energy) and 26.2% 'e' (stability). FQ escape routes completely bypass phase management.

## Evidence

From t7_role_kernel_taxonomy.py:

**FQ Kernel Profile:**
| Signature | Count | Percentage |
|-----------|-------|------------|
| none      | 1,561 | 54.0%      |
| k         | 571   | 19.8%      |
| e         | 370   | 12.8%      |
| k+e       | 388   | 13.4%      |

**FQ Kernel Character Rates:**
- k (energy): 33.2%
- h (phase): **0.0%**
- e (stability): 26.2%

**Comparison to EN:**
| Char | EN Rate | FQ Rate | Difference |
|------|---------|---------|------------|
| k    | 38.6%   | 33.2%   | -5.4pp     |
| h    | 59.4%   | 0.0%    | **-59.4pp** |
| e    | 58.3%   | 26.2%   | -32.1pp    |

FQ's zero 'h' rate is not due to low overall kernel - FQ has 46% kernel content. The absence of 'h' is selective.

## Interpretation

FQ's kernel profile reveals escape mechanism:

1. **Phase bypass:** FQ completely avoids 'h' (phase management). When the system escapes via FQ, it exits the phase-aligned pathway.

2. **Energy + Stability:** FQ uses k (energy, 33%) and e (stability, 26%) - enough to maintain stability without phase alignment.

3. **Escape model:**
```
Normal path:  FL[state] --[EN: h+e]--> FL[next_state]
                           (phase-managed)

Escape path:  FL[hazard] --[FQ: k+e]--> [exit]
                           (phase-bypassed)
```

4. **Why no phase?** Phase alignment (h) may be the computationally expensive or risky operation. Escape routes skip it entirely, using only energy injection (k) and stability anchoring (e).

Per C103-C105:
- k = ENERGY_MODULATOR (provides energy to escape)
- h = PHASE_MANAGER (skipped in escape)
- e = STABILITY_ANCHOR (maintains stability during escape)

## Provenance

- t7_role_kernel_taxonomy.json: role_kernel_sigs['FQ']
- Relates to: C775 (hazard FL escape driver), C778-C779 (EN profile)

## Status

CONFIRMED - FQ has exactly 0% 'h', escape bypasses phase management.
