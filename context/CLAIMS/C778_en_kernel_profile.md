# C778: EN Kernel Profile

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

## Constraint

EN (Energy role) is 91.9% kernel-containing with dominant signature h+e (35.8%). EN primarily uses phase (h=59.4%) and stability (e=58.3%) operators, with energy (k=38.6%) secondary. EN functions as the phase/stability operator, not energy injector.

## Evidence

From t6_en_kernel_profile.py:

**EN Kernel Signature Distribution:**
| Signature | Count | Percentage |
|-----------|-------|------------|
| h+e       | 2,585 | 35.8%      |
| k         | 1,053 | 14.6%      |
| k+e       | 1,034 | 14.3%      |
| h         | 1,004 | 13.9%      |
| none      | 582   | 8.1%       |
| k+h       | 370   | 5.1%       |
| k+h+e     | 324   | 4.5%       |
| e         | 259   | 3.6%       |

**Kernel Character Rates:**
- Any kernel: 91.9%
- h (phase): 59.4%
- e (stability): 58.3%
- k (energy): 38.6%

**EN Class Kernel Rates:**
- 10 EN classes are 100% kernel (classes 8, 31, 34, 35, 37, 42, 43, 44, 47, 48)
- Lowest: Class 36 at 38.3%, Class 45 at 42.4%

## Interpretation

Despite being named "EN" (Energy), this role primarily manages **phase and stability**, not energy:

1. **h+e dominance (35.8%):** The most common kernel combination is phase + stability
2. **h > k:** Phase management (59.4%) exceeds energy modulation (38.6%)
3. **h ≈ e:** Phase and stability are nearly equal, suggesting coupled operation

The kernel operators (per C103-C105):
- k = ENERGY_MODULATOR
- h = PHASE_MANAGER
- e = STABILITY_ANCHOR

EN's profile suggests it **aligns phase and anchors stability** during material transformation, rather than injecting energy.

## Provenance

- t6_en_kernel_profile.json: kernel_signatures, kernel_rates
- Relates to: C103-C105 (kernel operators), C772 (FL primitive substrate), C777 (FL state index)

## Status

CONFIRMED - EN is h+e dominant (phase + stability operator).
