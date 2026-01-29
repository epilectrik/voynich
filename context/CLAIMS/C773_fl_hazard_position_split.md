# C773: FL Hazard-Safe Position Split

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

## Constraint

FL classes exhibit a sharp hazard/safe split with distinct positional profiles:
- Hazard FL (classes 7, 30): 88.7% of FL tokens, mean position 0.546 (medial)
- Safe FL (classes 38, 40): 11.3% of FL tokens, mean position 0.811 (line-final)

Safe FL is positioned 0.265 later in lines than hazard FL.

## Evidence

From t2_fl_behavior.py:

**FL Class Hazard Split:**
| Category | Classes | Tokens | Percentage | Mean Position |
|----------|---------|--------|------------|---------------|
| Hazard   | 7, 30   | 956    | 88.7%      | 0.546         |
| Safe     | 38, 40  | 122    | 11.3%      | 0.811         |

**Position Difference:**
- Safe FL mean position: 0.811
- Hazard FL mean position: 0.546
- Difference: +0.265 (safe is 26.5% of line length later)

**FL Overall Position Distribution:**
| Zone     | Count | Percentage |
|----------|-------|------------|
| Initial  | 115   | 10.7%      |
| Early    | 157   | 14.6%      |
| Medial   | 326   | 30.2%      |
| Late     | 228   | 21.1%      |
| Final    | 252   | 23.4%      |

**FL Behavioral Findings:**
- FL mean position: 0.576 (slightly medial)
- Line-final rate: 65.3% (of line-final position tokens)
- FL -> FQ transition: 16.0%
- FL -> FL chaining: 88 instances (9.9%)

## Interpretation

FL's hazard/safe split correlates with positional function:
1. **Hazard FL (medial):** Appears mid-line where material flow is active
2. **Safe FL (line-final):** Appears at line endings as flow termination

The safe FL classes (38, 40) may function as "flow closers" that safely terminate material movement at line boundaries. Hazard FL (7, 30) drives active flow transitions.

## Provenance

- t2_fl_behavior.json: hazard_split, position distribution
- Relates to: C109 (hazard classes), C768 (role-compound correlation)

## Status

CONFIRMED - FL hazard/safe split shows distinct positional profiles.
