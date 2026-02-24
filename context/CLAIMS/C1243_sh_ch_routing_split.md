# C1243: sh/ch Cross-Lane Routing Split

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** EN_LANE_CROSS_PREDICTION (Phase 443)
**Extends:** C929 (ch/sh sensory modality discrimination), C1203 (ch/sh MIDDLE atom differentiation)
**Relates to:** C1242 (cross-lane content prediction), C408 (ch/sh as prefix sisters)

---

## Statement

The ch and sh prefixes route differently to subsequent QO tokens, extending C929's positional/suffix evidence to cross-lane routing behavior. sh (monitor) routes to QO(k=heat) at 32.0% vs ch (test) at 24.0% (1.34x ratio). sh→QO has lower entropy (4.763 bits) than ch→QO (5.068 bits), indicating sh is a more formulaic, predictable pivot back to heating while ch is a decision gate that branches to varied operations based on test results.

---

## Evidence

### CHSH→QO Routing by Prefix

| Metric | sh (monitor) | ch (test) |
|--------|-------------|-----------|
| Total pairs | 1,402 | 1,549 |
| Unique QO MIDDLEs after | 157 | 166 |
| Route to QO(k=heat) | 32.0% | 24.0% |
| Route to QO(k-containing) | 47.2% | 35.6% |
| Entropy (→QO MIDDLE) | 4.763 bits | 5.068 bits |

### Top QO MIDDLEs After Each Prefix

**After sh (monitor):** k (32.0%), t (7.7%), ke (6.7%), edy (3.9%), l (3.5%)
**After ch (test):** k (24.0%), t (7.4%), aiin (4.8%), e (4.1%), ke (3.9%)

Key difference: sh concentrates on heat (k and ke together = 38.7%), ch distributes across more diverse operations including verification (aiin 4.8%) and cooling (e 4.1%).

### Atom-Level Handoffs

**sh→QO:** y→k at 23.3% dominant (watched → heat)
**ch→QO:** y→k at 16.2% (lower), more distributed to y→a (4.6%), y→e (6.2%), y→t (4.6%)

### QO→CHSH Direction

- QO routes to ch 1.69:1 over sh (testing more common than monitoring)
- QO(k) → sh at 32.2% vs QO(k) → ch at 28.0% (after heating, slightly more likely to monitor than test)

---

## Functional Model

```
QO(heat) → sh(monitor) → QO(heat)     ← tight loop, predictable pivot
QO(heat) → ch(test)    → QO(varied)   ← decision gate, branches based on result
```

sh is the **steady-state pivot**: "looked fine, keep heating." It keeps the process in the same operational mode. ch is the **checkpoint gate**: "tested it, now do something different based on the result." It enables mode changes and operational branching.

---

## Relation to C929

C929 established the ch/sh distinction through 5 signals: within-line position (ch later), suffix pairing (checkpoint suffixes 1.87x enriched with ch), and operational neighbor context (sh followed by heat 18.3%). C1243 adds a 6th independent signal: **cross-lane routing behavior** (sh routes to heat 1.34x more, with lower entropy). The routing evidence directly validates C929's functional model from a completely different methodological angle.

---

## Source

- Exploratory: `_tmp_ch_sh_pivot.py`
