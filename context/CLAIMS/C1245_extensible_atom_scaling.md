# C1245: Extensible Atom Scaling — Two Independent Control Dimensions

**Tier:** 3 (INTERPRETIVE)
**Scope:** B
**Phase:** EN_LANE_CROSS_PREDICTION (Phase 443)
**Extends:** C1197 (atom extensibility partition), C1204 (i-extension inverted gradient), C1205 (i/k/e orthogonality), C901 (e stability gradient)
**Relates to:** C1195 (atom glosses), C1207 (atom correlation clusters), C1242 (cross-lane prediction)

---

## Statement

The two extensible atoms (e, i) encode two independent scaling dimensions of the control program. e-extension modulates **energy intensity**: k = full heat, ke = modulated heat, kee = gentle heat. i-extension modulates **iteration duration**: i = single pass, ii = sustained cycling. These dimensions are structurally independent (C1205: i anti-correlates with both k and e) and map cleanly to REGIME variation: bare k dominates REGIME_2 at 92.6% (highest intensity), while ke mixing reaches 18.6% in REGIME_1 (modulated regime).

This interpretation reframes the -aiin/-ain suffix gloss from "check/verification" (C561 context) to "settle/intake" (C1195 atom decomposition): aiin = a(yield) + ii(sustained cycling) + n(halt) = "sustained cycling until halt"; ain = a(yield) + i(single pass) + n(halt) = "one more pass then halt." The monitoring/checking function is carried by the CHSH lane (C929, C1243), not by the i-atom suffix.

---

## Evidence

### E-Extension as Intensity Gradient

QO tokens with heat MIDDLEs by REGIME:

| REGIME | k (pure) | ke (modulated) | kee (gentle) | k-ratio |
|--------|----------|----------------|--------------|---------|
| REGIME_2 | 112 | 7 | 2 | 92.6% |
| REGIME_3 | 276 | 44 | 8 | 84.1% |
| REGIME_1 | 1,261 | 291 | 12 | 80.6% |
| REGIME_4 | 67 | 14 | 1 | 81.7% |

REGIME_2 (highest k_ratio, iteration-heavy) uses almost exclusively pure k — no cooling modulation. REGIME_1 (highest thermo_ke feature) has the most ke mixing. This is consistent with e-count encoding cooling/modulation depth.

### I-Extension as Duration

From C1204: ii is the default form (53.7% vs single-i 45.9%). From C1244: aiin precedes ain 64.9% when both co-occur, representing wind-down from sustained to single-pass. From C1205: i anti-clusters within lines (z = -6.14) and displaces energy content rather than modulating k/e ratio.

### Independence of Axes

From C1207: i anti-correlates with e (r = -0.513) and with y (r = -0.599) at the folio level. From C1205: i-containing MIDDLEs have near-zero k (0.009) and near-zero e (0.005). The two extensible atoms occupy different operational axes — intensity (e) and duration/iteration (i) — consistent with two independent control parameters.

### Suffix Gloss Refinement

C561 established aiin's role in the or→aiin bigram (87.5% directional). C1236 labeled -aiin/-ain as "checkpoint suffixes" (mode-independent loop controllers). C1195 decomposed the atoms: aiin = a(yield) + ii(iterate) + n(halt) = "settle." The "check" reading arose from the or→aiin bigram context, not from the suffix's own atom semantics. In the EN energy-token context (qokaiin, okaiin), monitoring is CHSH's job (C929, C1243); the i-suffix specifies how long the energy operation runs.

---

## Functional Summary

```
e-extension: INTENSITY dial
  k     = full heat (rolling boil)
  ke    = modulated heat (controlled simmer)
  kee   = gentle heat (low fire)

i-extension: DURATION dial
  i     = single pass (one iteration)
  ii    = sustained cycling (keep going)
  iii   = extended run (rare, 0.3%)

Combined example:
  qokaiin  = energy + full-heat + sustained-cycling
  qokeain  = energy + modulated-heat + one-more-pass
```

---

## Falsification

Would be falsified if:
1. Bare k and ke show identical REGIME distributions (intensity interpretation fails)
2. i/ii show no directional ordering within lines (duration interpretation fails)
3. An alternative explanation accounts for both e-extension and i-extension gradients simultaneously

---

## Source

- Exploratory: `_tmp_regime_clean.py`, `_tmp_iin_ain_order.py`
- Prior: C1197, C1204, C1205, C1207 (atom characterization phases)
