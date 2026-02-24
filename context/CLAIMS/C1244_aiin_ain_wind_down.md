# C1244: aiin-ain Sequential Wind-Down

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** EN_LANE_CROSS_PREDICTION (Phase 443)
**Extends:** C1234 (iteration two-track system), C1204 (i-extension inverted gradient)
**Relates to:** C1195 (atom gloss: aiin=settle, ain=intake), C561 (or→aiin bigram), C1236 (suffix scope markers)

---

## Statement

When -aiin and -ain suffixes co-occur on the same line, aiin precedes ain 64.9% of the time (98/151 lines). Adjacent suffix pairs show the same directionality: aiin→ain (19) vs ain→aiin (11). The QO→CHSH→QO triplet analysis shows 84.5% advance to a different MIDDLE (not literal loop-back), with only 15.5% repeating the same MIDDLE (2.05x above the 7.6% random baseline). The cycle progresses through different operations, with aiin marking the sustained cycling phase and ain marking the finishing pass.

---

## Evidence

### T1: Co-Occurrence Ordering
- Lines containing both suffixes: 151
- aiin before ain: 98 (64.9%)
- ain before aiin: 53 (35.1%)

### T2: Adjacent Suffix Pairs
| Pair | Count |
|------|-------|
| aiin → ain | 19 |
| ain → aiin | 11 |
| aiin → aiin | 52 |
| ain → ain | 30 |

aiin→aiin (sustained cycling) is the most common pair. aiin→ain (wind-down) is directionally preferred over ain→aiin (1.73:1).

### T3: Positional Means
- -aiin: mean position 0.465
- -ain: mean position 0.478
- Consistent with aiin earlier in line, ain later

### T4: QO→CHSH→QO Triplet Analysis (Loop-Back Test)

For QO → sh → QO triplets:
- Same MIDDLE before/after sh: 15.5% (2.05x baseline)
- Different MIDDLE: 84.5%

For QO → ch → QO triplets:
- Same MIDDLE before/after ch: 14.9% (1.96x baseline)
- Different MIDDLE: 85.1%

Both prefixes advance more than they loop. The above-baseline loop-back rate concentrates heavily on `k` MIDDLE (heat → monitor → heat), where the MIDDLE stays `k` but the suffix changes (e.g., qokaiin → sh → qokain).

### T5: aiin→ain Same-MIDDLE Co-Occurrence
- When aiin precedes ain on a line: same MIDDLE 15.6%, different 84.4%
- The wind-down typically changes the operation, not just the suffix

---

## Interpretation

The aiin→ain pattern represents a **wind-down sequence** within the iteration system. aiin (a+ii+n = yield-iterate-iterate-halt = "sustained cycling") appears during the main processing phase, while ain (a+i+n = yield-iterate-halt = "final pass") appears as the process concludes. This is consistent with C1234's two-track model (iin=cycle setup, aiin=bounded loop control) and extends it with directional evidence: the system winds down from sustained cycling to single-pass finishing.

The 15.5% loop-back rate for heat operations (k → monitor → k) with suffix change (aiin→ain) represents the specific case where the operation type stays constant but the iteration specification decreases — literally "keep heating, keep heating... one more heat, done."

---

## Source

- Exploratory: `_tmp_sh_loop_or_advance.py`, `_tmp_iin_ain_order.py`
