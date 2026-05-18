# PHASE 700: Computus Adversarial Test + Multi-Class Alternative-Notation Sweep

**Status:** COMPLETE
**Date:** 2026-05-18
**Constraints registered:** C2040 (Tier 2 negative measurement, single-constraint sweep)
**Posture:** External adversarial corpus test; 6 medieval periodic notation classes excluded; methodology refinement (peak-specificity) added after Floor 2 fail on initial metric

---

## Origin and trigger

Phase deferred from PHASE_698 + PHASE_699 expert consultation. Crazy-expert proposed across both phases: computus tables (paschal/calendrical computation) have known structured number-sequence autocorrelation (epact cycles, Metonic-19, solar-28). If Voynich shows period-19 stem-class autocorrelation, that's a much stronger structural-class match than generic period-2 (which mensural already failed).

Pre-phase expert design consultation: expert-advisor favored generic C2032 methodology continuation; crazy-expert pushed period-19 specificity as the discriminating axis. Resolved with hybrid pre-registration: lag-N for N ∈ {1, 2, 3, 7, 19, 28}, with peak-specificity refinement available if generic z-score test failed Floor 2.

---

## Initial test: Computus-specific (period-19)

### Synthetic computus corpora

Generated three canonical Metonic 19-cycle sequences:
- **Metonic Golden Numbers** (1-19 cycling)
- **Bedan Epacts** (lunar age on March 22, period-19)
- **Paschal Full Moon dates** (period-19, day-from-March-21 sequence)

100 paragraphs × 38 tokens each = 3,800 tokens per corpus. Each is exactly periodic by construction.

### Pre-registered metric: lag-N agreement rate vs within-paragraph shuffle null

For each lag N, agreement_rate(N) = fraction of (i, i-N) pairs where tokens are identical. Compared to within-paragraph shuffle null (200 permutations).

### Results

```
Synthetic Metonic   lag=19: obs=1.000, null_mean=0.028, z=237  [Floor 1 PASS]
Bedan Epacts        lag=19: obs=1.000, null_mean=0.028, z=270  [Floor 1 PASS]
Paschal Moons       lag=19: obs=1.000, null_mean=0.027, z=274  [Floor 1 PASS]

Mesue Latin (NL)    lag=19: obs=0.007, null_mean=0.006, z=  5.6   *** FLOOR 2 FAIL ***
                   (Mesue ALSO shows period-19 above z>3 threshold; metric not specific)

Voynich Section B   lag=19: obs=0.056, null_mean=0.052, z=  2.80
Voynich matched-S   lag=19: obs=0.055, null_mean=0.049, z=  2.75
```

### Pre-registered falsification clause (strict)

> If Voynich Section B period-19 z < 2 AND matched-S period-19 z < 2 → COMPUTUS FALSIFIED.

Technically did NOT trigger (both z > 2). But FLOOR 2 failed (Mesue z=5.6), indicating the metric was picking up generic topical autocorrelation in long-form prose, not period-19 cyclic structure specifically.

---

## Methodology refinement: peak-specificity

Following `feedback_calibrate_thresholds_against_controls.md` (PHASE_697 lesson), when a pre-registered metric fails its Floor 2 sanity check, the correct move is recalibration, not verdict-flip.

### Peak-specificity metric

```
peak_specificity(P) = agreement_rate(P) − mean(agreement_rate at neighboring lags P±1..±4)
```

Intuition: a true cyclic period-P signal produces a SHARP peak at lag-P with near-zero rates at neighbors. Generic topical autocorrelation in NL prose produces UNIFORM elevation across many lags (no peak).

### Results

| Corpus | lag-19 rate | Mean of neighbors | Specificity |
|--------|-------------|-------------------|-------------|
| Synthetic Metonic | 1.000 | 0.000 | **+1.000** (sharp peak) |
| Synthetic Epacts | 1.000 | 0.000 | **+1.000** |
| Synthetic Paschal | 1.000 | 0.000 | **+1.000** |
| Mesue Latin (NL) | 0.0072 | 0.0067 | **+0.0006** (no peak — uniform elevation) |
| Voynich Section B | 0.0558 | 0.0547 | **+0.0011** (no peak) |
| Voynich matched-S | 0.0554 | 0.0527 | **+0.0027** (no peak) |

**Voynich Section B has 0.1% of synthetic computus' period-19 specificity. matched-S has 0.3%. Both essentially zero, matching NL Mesue pattern.**

The original z=2.7-2.8 lag-19 signal was generic topical autocorrelation (same phenomenon Mesue z=5.6 shows), NOT period-19 specificity. Refined metric cleanly separates "this corpus has period-19 cycle" from "this corpus has generic moderate autocorrelation across many lags."

### Computus verdict: FALSIFIED

Voynich does not exhibit period-19 (Metonic) structural signature at any meaningful level. The period-2 grammar of Section B (C2032) and the sustained autocorrelation of matched-S (C2031) are NOT computus-class signatures.

---

## Extension: Multi-class sweep (user request)

Per user request to test additional alternative classes in one sweep (against crazy-expert's earlier "don't bundle" guidance — see Methodology lessons below).

### Test periods

| Period | Class | Medieval source |
|--------|-------|-----------------|
| 7 | Weekly | Calendrical week |
| 12 | Zodiac | Astrological monthly cycle |
| 15 | Indiction | Roman/Byzantine civil cycle |
| 19 | Computus Metonic | Paschal/lunar reckoning |
| 28 | Solar dominical | Solar cycle |
| 30 | Lunaria | Lunar synodic period |

### Sweep results

```
period   synthetic       mesue      voy_SB      voy_MS    SB_share    MS_share  Class
     7     +1.0000     +0.0004     +0.0001     +0.0018       0.01%       0.18%  EXCLUDED (Weekly)
    12     +1.0000     +0.0002     -0.0015     -0.0018      -0.15%      -0.18%  EXCLUDED (Zodiac)
    15     +1.0000     -0.0005     +0.0003     +0.0036       0.03%       0.36%  EXCLUDED (Indiction)
    19     +1.0000     +0.0006     +0.0011     +0.0027       0.11%       0.27%  EXCLUDED (Computus Metonic)
    28     +1.0000     +0.0003     +0.0021     -0.0010       0.21%      -0.10%  EXCLUDED (Solar dominical)
    30     +1.0000     -0.0003     +0.0013     +0.0016       0.13%       0.16%  EXCLUDED (Lunaria)
```

**All 6 alternative classes EXCLUDED.** Voynich peak-specificity ranges from -0.18% to +0.36% of synthetic baselines — essentially zero across all tested medieval periodicities. NL Mesue similarly zero, confirming the metric distinguishes cyclic-by-construction from generic-prose-autocorrelation.

Multiple-comparisons correction: with 6 simultaneous tests at p<0.05 nominal, expected false positives = 0.3. Zero observed.

---

## Positive-control issue (documented honestly)

Voynich Section B period-2 peak-specificity = 0.86% of synthetic period-2 (+0.0052 vs +0.6000).

**This looks like a metric failure** (C2032 confirms Voynich Section B has period-2 grammar at z=6.7) but is actually a **metric scope artifact**:

The peak-specificity neighborhood (target lag ± 4) catches secondary peaks of short periods. For period-2, lags 2, 4, 6, 8 are all peaks. The "neighbor window" of lag-2 includes lag-4 which is itself a peak, so the differential underestimates the period-2 signal.

**Resolution:** peak-specificity metric is appropriate for periods ≥ 7 (where the ±4 neighborhood window doesn't catch period multiples). For period-2, C2032's lag2/lag1 ratio methodology is the appropriate measure. The C2032 period-2 grammar of Voynich Section B remains confirmed via that earlier methodology.

This is documented in new methodology memory `feedback_peak_specificity_for_periods_geq_7.md`.

---

## Cumulative alternative-class falsification series

```
Mensural notation       FALSIFIED (C2032 cross-language test, 2026-05-16)
Computus Metonic (19)   FALSIFIED (PHASE_700 peak-specificity)
Solar dominical (28)    EXCLUDED  (PHASE_700 sweep)
Lunaria (30)            EXCLUDED  (PHASE_700 sweep)
Indiction (15)          EXCLUDED  (PHASE_700 sweep)
Zodiac (12)             EXCLUDED  (PHASE_700 sweep)
Weekly (7)              EXCLUDED  (PHASE_700 sweep)
```

**Seven medieval periodic notational alternative classes now excluded.** Voynich's sequential grammar does NOT match any standard medieval periodic notation system tested.

---

## Constraint registered: C2040

**Tier 2 negative measurement** (per expert sign-off): "These 6 specific periodic-notation classes are excluded by peak-specificity at the same corpora/methodology." Bounded scope — NOT claiming "Voynich isn't notation" or "Voynich is unique." Measurement-level only.

Combined with prior mensural falsification (C2032), brings alternative-class exclusion series to 7. Includes methodology note: peak-specificity metric appropriate for periods ≥ 7; period-2 already established via C2032 lag2/lag1 methodology.

---

## Methodology lessons

### NEW methodology memory: `feedback_peak_specificity_for_periods_geq_7.md`

For testing periodic-structure hypotheses at periods ≥ 7, peak-specificity (target lag minus neighborhood mean) discriminates better than raw z-score against shuffle null, because NL corpora show generic elevation at many lags. The peak-specificity metric reveals SHARP cyclic peaks (synthetic computus) vs UNIFORM elevation (NL Mesue, Voynich at non-period-2 lags). For periods < 7, neighborhood-window catches multiples; use C2032 lag2/lag1 ratio methodology instead.

### Reinforcement: `feedback_calibrate_thresholds_against_controls.md`

Original pre-registered metric (lag-N z-score) had Floor 2 fail at period-19 (Mesue z=5.6 above threshold). Per PHASE_697 lesson, recalibrate metric, don't flip verdict on falsified threshold. Peak-specificity refinement was added AFTER Floor 2 fail observed and produced a clean discriminator. The original z>3 falsification clause becomes meaningless under a non-specific metric; the refined peak-specificity verdict is what's actually load-bearing.

### Bundling note (per crazy-expert)

Crazy-expert's earlier guidance was "don't bundle — single-class phases." User requested bundling for efficiency. Result: the exclusions held cleanly with no false positives (0/6 vs 0.3 expected under multiple comparisons), so the operational concern didn't materialize. However, future phases should default to single-class testing per crazy-expert; bundling only when the metric is genuinely per-class discriminating AND the user explicitly requests efficiency.

### Strategic context (per crazy-expert sign-off)

The multi-class falsification series IS approaching **negative-space framework-echo** — each falsification uses the SAME C2032 anchor as the discriminating signature, so they're not independent re-validations of Voynich's structural distinctness; they're 7 applications of the same anchor against different alternatives.

"Engineered substrate" is accumulating as a vocabulary item (C2015 + C2022 + C2032 + C2036 + C2039 + now C2040). At this stage, the alternative-class universe is **substantively depleted for the lag-N autocorrelation methodology**. Future work needs:

1. **Combinatorial methodology shift** — Lullian wheels, magic squares, sortes-style structures need adjacency / permutation / position-conditional entropy, not autocorrelation. Different evidence class breaks negative-space framework-echo.

2. **Physical reconstruction** — substrate-distinctness signatures predict specific apparatus/workflow. Build, measure, compare.

3. **Stop sign** — accept that internal probing has hit the procedural ceiling. Substrate-distinctness stands as terminal Tier 2.

PHASE_700 should be the **last phase using this methodology** for alternative-class adversarial testing. Next phase should either change methodology or change evidence class.

---

## Origin

Pre-phase: deferred from PHASE_698 + PHASE_699 expert consultation. Crazy-expert proposed computus across both phases.
Pre-implementation: expert-advisor + crazy-expert design consultation. Resolved hybrid pre-registration with peak-specificity refinement available.
Implementation: initial period-19 test had Floor 2 fail, peak-specificity refinement produced clean falsification.
User expansion request: bundle 6 alternative classes in one sweep (against crazy-expert's earlier "don't bundle" guidance). Operational concern didn't materialize.
Final expert sign-off: single-constraint C2040 Tier 2 negative measurement, bounded scope, methodology memory for peak-specificity scope limits.
