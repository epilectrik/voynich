# C779: EN-FL State Coupling

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

## Constraint

EN kernel profile varies systematically with FL state: 'h' (phase) rate drops from 95.1% after FL-EARLY to 76.9% after FL-LATE. Early FL states require heavy phase management; late FL states require less.

## Evidence

From t6_en_kernel_profile.py:

**EN Kernel Profile After FL (by FL state):**

| FL State | n | Any Kernel | k rate | h rate | e rate |
|----------|---|------------|--------|--------|--------|
| EARLY    | 61 | 98.4% | 26.2% | **95.1%** | 68.9% |
| MEDIAL   | 150 | 97.3% | 12.7% | **89.3%** | 70.0% |
| LATE     | 13 | 92.3% | 15.4% | **76.9%** | 53.8% |

**Key Pattern:**
- h (phase) drops: 95.1% → 89.3% → 76.9%
- e (stability) relatively stable: 68.9% → 70.0% → 53.8%
- k (energy) low throughout: 26.2% → 12.7% → 15.4%

**EN Kernel Profile Before FL (by FL state):**

| FL State | n | k rate | h rate | e rate |
|----------|---|--------|--------|--------|
| EARLY    | 41 | 31.7% | 63.4% | 65.9% |
| MEDIAL   | 181 | **45.3%** | 55.2% | 50.3% |
| LATE     | 34 | 38.2% | 61.8% | 55.9% |

Before FL-MEDIAL, k (energy) peaks at 45.3% - energy injection precedes intermediate states.

## Interpretation

The EN-FL coupling reveals the transformation mechanism:

```
FL[EARLY] --[EN: h=95%, phase-heavy]--> FL[MEDIAL]
     |                                      |
     |         [EN: k=45% before]           |
     |                                      v
FL[MEDIAL] --[EN: h=89%, stabilizing]--> FL[LATE]
                                            |
                                            v
                              [EN: h=77%, minimal phase]
```

1. **Early states need phase alignment:** Material entering the process requires heavy phase management (h=95%)
2. **Medial states receive energy:** k peaks (45%) before medial states - energy injection at mid-process
3. **Late states are stable:** Reduced phase management (h=77%) indicates material approaching terminal state

EN guides material through FL-indexed states by progressively reducing phase management as material stabilizes.

## Provenance

- t6_en_kernel_profile.json: en_after_fl profiles
- Relates to: C777 (FL state index), C778 (EN kernel profile)

## Status

CONFIRMED - EN kernel profile couples to FL state progression.
