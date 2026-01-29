# C775: Hazard FL Escape Driver

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

## Constraint

Hazard FL classes (7, 30) drive 98% of FL->FQ transitions. Safe FL classes (38, 40) account for only 2%. The FL->FQ rate is 22.5% of classified FL transitions.

## Evidence

From t4_fl_hazard_relationship.py:

**FL -> FQ by Class:**
| FL Class | Category | FL->FQ Count | Percentage |
|----------|----------|--------------|------------|
| 7        | HAZARD   | 71           | 49.7%      |
| 30       | HAZARD   | 69           | 48.3%      |
| 38       | SAFE     | 3            | 2.1%       |
| 40       | SAFE     | 0            | 0.0%       |

**Summary:**
- Hazard FL (7, 30): 140 transitions (97.9%)
- Safe FL (38, 40): 3 transitions (2.1%)

**FL -> FQ Target Distribution:**
| FQ Class | Count | Percentage |
|----------|-------|------------|
| 9        | 50    | 35.0%      |
| 13       | 35    | 24.5%      |
| 14       | 32    | 22.4%      |
| 23       | 26    | 18.2%      |

FQ class 9 is the dominant escape target.

## Interpretation

The hazard/escape relationship:

1. **Hazard FL feeds escape routes:** FL classes that are hazard-tagged (7, 30) preferentially transition to FQ
2. **Safe FL is terminal:** Safe FL (38, 40) rarely transitions to FQ because it already represents safe termination
3. **Escape mechanism:** Hazard FL -> FQ may be the grammar's way of routing hazardous flow to frequency/escape handling

Functional model:
```
Hazard FL (7, 30) --[22.5%]--> FQ (escape processing)
                  --[77.5%]--> EN/AX/CC/FL (continued flow)

Safe FL (38, 40) --[~0%]--> FQ (no need for escape)
                --[terminal]--> (line-final position)
```

## Provenance

- t4_fl_hazard_relationship.json: fl_to_fq_by_class
- Relates to: C773 (FL hazard-safe position split), C774 (FL outside forbidden)

## Status

CONFIRMED - Hazard FL drives escape transitions; safe FL is terminal.
