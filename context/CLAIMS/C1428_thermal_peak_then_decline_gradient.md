# C1428: THERMAL-Peak-Then-Decline Positional Gradient

**Tier:** 2 (ESTABLISHED)
**Scope:** B, line, position, gradient, category, THERMAL
**Phase:** LINE_LEVEL_ARCHITECTURE (Phase 519)
**Extends:** C556 (SETUP->WORK->CHECK->CLOSE), C1358 (class positional specialization), C1372 (thermodynamic arc)
**Relates to:** C932 (body vocabulary gradient), C965 (body kernel composition shift), C1302 (BARE anti-thermal)

---

## Statement

Within-line positional gradient: THERMAL category peaks at Q1 (29.4%), not Q0 (24.3%), because Q0 contains specification/prep vocabulary (articulators, staging PREFIXes). THERMAL then declines to 17.6% at Q4. FLOW rises monotonically Q0->Q4 (17.6%->22.6%). TRANSITION flat through Q0-Q3 then jumps at Q4 (14.1%->19.1%). BARE PREFIX rises Q0->Q4 (14.3%->21.9%). The gradient is SPECIFICATION -> THERMAL_WORK -> FLOW/TRANSITION.

### Category by Quintile

| Category | Q0 | Q1 | Q2 | Q3 | Q4 | Gradient Shape |
|----------|-----|-----|-----|-----|-----|----------------|
| THERMAL | 24.3% | **29.4%** | 24.8% | 24.6% | 17.6% | Peak Q1, decline |
| FLOW | 17.6% | 16.5% | 19.6% | 20.2% | **22.6%** | Monotonic rise |
| TRANSITION | 14.1% | 14.0% | 12.5% | 14.2% | **19.1%** | Flat then Q4 jump |
| STAGING | **15.6%** | 12.1% | 12.4% | 10.9% | 13.5% | Peaks Q0 |
| OPERATION | **14.7%** | 15.4% | 15.5% | 14.6% | 12.3% | Mild decline |
| MARKING | 8.4% | 6.5% | 7.7% | 8.3% | 7.9% | Flat |
| ARTICULATOR | **9.7%** | 2.8% | 2.8% | 2.5% | 3.5% | Sharp Q0 drop |

### BARE PREFIX Gradient

| Q0 | Q1 | Q2 | Q3 | Q4 |
|-----|-----|-----|-----|-----|
| 14.3% | 14.5% | 15.3% | 16.3% | **21.9%** |

BARE rises monotonically, anti-correlating with THERMAL. Validates C1302 (BARE is THERMAL-depleted, associated with closing operations).

### Implication

The delayed THERMAL peak (Q1 not Q0) resolves an apparent contradiction: C556 claims lines start with "SETUP" but THERMAL is the dominant operation. The resolution is that the SPECIFICATION zone (Q0) is structurally distinct from the THERMAL WORK zone (Q1-Q3). Lines specify first, then execute thermally, then close with state transitions.

---

## Falsification Criteria

1. If THERMAL peaks at Q0 instead of Q1 in all sections
2. If FLOW does not rise toward Q4
3. If BARE PREFIX does not increase toward line-final

---

## Method

- 23,096 tokens with normalized positions (0-1) binned into quintiles
- Category by CategoryClassifier atom plurality vote
- Per-quintile category distributions

**Script:** `phases/LINE_LEVEL_ARCHITECTURE/scripts/line_architecture.py` (T4)
**Results:** `phases/LINE_LEVEL_ARCHITECTURE/results/line_architecture.json`
