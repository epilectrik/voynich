# PHASE_706: Burstiness β + DFA Hurst Exponent

**Status:** COMPLETE — INDEX-only (no new constraints registered)
**Date:** 2026-05-19
**Verdict:** Both metrics are FLOORS for structured-symbolic systems, not NL discriminators. Mensural notation counter-example passed both NL thresholds. No new Tier 2 constraints registered. 6th methodology memory saved.

---

## Quick result summary

### Primary tests (sanity floors passed)

| Test | Voynich B | Codicillus | Mesue | Brunschwig | Random Null |
|------|----------:|-----------:|------:|-----------:|------------:|
| Burstiness β | **0.769** | 0.686 | 0.772 | 0.764 | 1.003 |
| DFA Hurst H | **0.652** | 0.704 | 0.597 | 0.696 | 0.510 |

Voynich Currier B looked NL-like on both axes.

### Follow-up controls (LOAD-BEARING)

**Within-folio shuffle null** (does the signal survive when within-folio token order is randomized?):
- β: 0.769 → 0.807 (Δ = +0.038, small)
- H: 0.652 → 0.644 (Δ = +0.008, tiny)
- Signal is ~95% folio-composition-driven (consistent with folio = program framework)

**Mensural notation floor test** (does a confirmed non-NL system pass the NL thresholds?):
- Mensural β = 0.653 (PASSES NL threshold of <0.85 with room)
- Mensural H = 0.823 (PASSES NL threshold of >0.55, higher than NL range)

**Mensural notation — a confirmed non-NL system — passes both NL-thresholds.** Therefore β and H are FLOORS for any structured-symbolic system with topical organization, not DISCRIMINATORS for NL.

---

## Why no constraints registered

The Voynich measurements (β=0.769, H=0.652) are real but **uninformative for the NL-vs-non-NL question** because the metrics don't actually discriminate:
- Any structured-symbolic system with topical organization passes both
- Voynich passing = "Voynich is structured-symbolic with topical organization" (already known)
- This adds no new information to the framework

Registering as Tier 2 would over-claim "NL-like Voynich" when the metrics actually say "structured-symbolic." Registering as Tier 3 descriptive would create epistemic clutter — a constraint whose primary content is "this metric isn't useful" is the kind of "noise-floor metric preserved as if informative" pattern that the C131 audit lesson warned against.

The substantive contribution is the **methodology lesson** (floor vs discriminator), saved to memory.

---

## What this confirms about the existing framework

1. **Substrate quintet's "non-NL" framing survives intact.** Only C2032 (lag2/lag1) actually discriminates NL — mensural fails C2032 cleanly (mensural +0.18 vs NL ±0.17, Voynich Section B -0.66). Other substrate axes (C2015 compression, C2022 Markov plateau) are also floors per prior calibration lesson.

2. **Content-driven folio clustering is real.** Within-folio shuffle preserves ~95% of β/H signal → most of the structure is at folio-composition level, which is exactly what the "folio = program" framework predicts.

3. **C2032 is now confirmed as the project's only-known-true NL discriminator.** Both β and H join C2015/C2022 as exclusion-gate floors. C2032 alone separates Voynich from mensural and NL.

---

## Methodology memory saved

`feedback_floor_vs_discriminator_metric_test.md` — 6th distinct failure-mode pattern in the audit taxonomy: floor metric mistaken for discriminator. Diagnostic: before treating any new literature-borrowed NL-detection metric as informative, ALWAYS run mensural (or equivalent non-NL structured benchmark) and check if it passes the metric's NL threshold. If yes, metric is floor only.

Generalizes prior `feedback_registration_calibration_lesson.md` (which established C2032 alone discriminates within the substrate triad) to ALL imported literature metrics.

---

## Posture (original — preserved for record)

Two classical NL-detection signatures from the literature that the project has not yet applied. Designed to complement the existing engineered-substrate quintet (C2015, C2022, C2032, C2035, C2036, C2039) by adding orthogonal language-detection axes.

---

## Why these two tests

After web research (see CHANGELOG v6.79 entry), six new statistical tests from the literature were identified. The two highest-EV picks:

1. **Burstiness β** — Weibull shape parameter for inter-arrival times of frequent tokens. From Altmann et al. 2009 ([Beyond Word Frequency: Bursts, Lulls, and Scaling](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0007678)). NL has β < 1 (semantic clustering); Poisson has β = 1. **Semantic class predicts β at 48% variance vs log-frequency at only 9%** — burstiness is semantically driven, not just frequency artifact.

2. **DFA Hurst exponent** — Detrended Fluctuation Analysis on token-length time series. From the long-range correlation literature ([PLOS ONE A Story of the Stone study](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0162423)). NL has H ≈ 0.6 (weak persistence); random has H = 0.5; anti-persistent has H < 0.5.

Both have known NL baselines and we have NL Latin corpora loaded (Codicillus, Mesue, Brunschwig) for direct comparison.

---

## Pre-registered design (LOCKED before any data inspection)

### Test 1: Burstiness β

**Methodology:**
1. For each corpus, extract token sequence in natural reading order
2. Identify top-50 most frequent tokens with ≥20 total occurrences
3. For each token: extract positions of all occurrences in the sequence
4. Compute inter-arrival times = differences between consecutive positions
5. Fit Weibull distribution (scipy.stats.weibull_min) to inter-arrival times
6. Record β (shape parameter)
7. Report median, mean, IQR of β across the 50 tokens

**Corpora to test:**
- **Target:** Voynich Currier B (H-track, P-placement, full token strings)
- **NL baselines:** Codicillus Mercuriorum Latin (alchemy), Mesue Grabadin Latin (pharmacy), Brunschwig 1512 (Early New High German distillation)
- **Random null:** Voynich Currier B with full token-sequence shuffle (should give β ≈ 1)

### Test 2: DFA Hurst exponent

**Methodology:**
1. For each corpus, extract token-length time series in reading order
2. Standard DFA-2 procedure:
   - Compute profile: cumulative sum of (x_t − mean)
   - For each scale w in log-spaced range [10, N/4]:
     - Divide profile into non-overlapping windows of size w
     - Fit quadratic polynomial within each window, subtract trend
     - Compute std of detrended residuals
     - F(w) = mean std across windows
   - Fit log F(w) ~ H · log(w) → Hurst exponent H
3. Compute Hurst on raw token-length sequence
4. Compute Hurst on shuffled sequence (random baseline)

**Corpora:** Same as burstiness test.

---

## Pre-registered decision rules (LOCKED)

### Per-test thresholds (from literature)

**Burstiness β:**
- β median < 0.85 → **NL-like burstiness** (semantic clustering present)
- β median > 0.95 → **Poisson-like / random**
- 0.85 ≤ β median ≤ 0.95 → ambiguous

**Hurst H:**
- H > 0.55 → **NL-like persistence** (long-range correlation)
- 0.45 < H < 0.55 → **random / uncorrelated**
- H < 0.45 → **anti-persistent** (unusual)

### Combined verdict

| Burstiness | Hurst | Verdict |
|------------|-------|---------|
| NL-like | NL-like | **NL-LIKE SIGNATURE** — would challenge engineered-substrate "non-language" framing |
| Poisson | Random | **RANDOM SIGNATURE** — would be surprising; Voynich isn't random by other measures |
| NL-like | Random | **MIXED-1** — semantic clustering without long-range; cipher-like? |
| Poisson | NL-like | **MIXED-2** — long-range structure without semantic clustering; very unusual |
| Outside either range | Either | **NOVEL SIGNATURE** — adds new axis to substrate-distinctness story |

### Sanity floor

Both tests must produce sensible values on NL baselines:
- Codicillus / Mesue must show β < 0.95 AND H > 0.55 (NL signatures expected)
- If NL baselines fail the test, methodology is broken — DO NOT interpret Voynich result
- Random shuffle of Voynich tokens must show β ≈ 1.0 AND H ≈ 0.5

---

## What this tests vs what we already have

| Existing measurement | What it captures | New test extends to |
|---------------------|------------------|---------------------|
| C2015 (char-LM compression bpc) | Symbol-level entropy | — |
| C2022 (Markov plateau order) | Local conditional structure | — |
| C2032 (lag2/lag1 chain excess) | Short-range autocorrelation in e-depth | DFA extends to LONG-range cross-scale |
| C2030 (within-line LATE clustering) | Adjacency clustering of specific class | Burstiness extends to GLOBAL temporal clustering for any token |
| Atom-system structural model | Token construction grammar | — |

Both new tests are **orthogonal to existing measurements**. Burstiness captures the SEMANTIC-clustering dimension that the substrate quintet doesn't measure. DFA captures long-range persistence that the Markov plateau doesn't capture.

---

## Registration-trap audit

- **Both tests use external NL baselines.** Codicillus / Mesue / Brunschwig comparisons are essential — without them we'd be measuring against arbitrary thresholds.
- **Both tests have random null built in.** Shuffled Voynich should give β=1, H=0.5. If it doesn't, methodology is broken.
- **Thresholds are taken from external literature** (not adjusted for this experiment). Lit values: NL β ~0.6-0.8, NL H ~0.6.
- **Both outcomes are publishable.** NL-like result challenges existing framing. Non-NL result strengthens substrate-distinctness story.
- **Pre-registered before any runs.** All decision criteria locked above.

---

## Expected effort

Burstiness: ~30 min implementation + ~5 min runtime per corpus
DFA Hurst: ~30 min implementation + ~5 min runtime per corpus
Combined: ~1.5 hours total

---

## Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `_burstiness_test.py` | Weibull β fit on top-50 token inter-arrival times | Ready to write |
| `_dfa_hurst_test.py` | DFA-2 Hurst exponent on token-length series | Ready to write |
| `_combined_verdict.py` | Apply decision rules across both tests | Optional — can be a manual step |

---

## Cross-references

- Engineered substrate quintet: C2015, C2022, C2032, C2035, C2036, C2039
- Methodology lessons: `feedback_calibrate_thresholds_against_controls.md` (calibrate against in-distribution baselines first), `feedback_specific_vs_tautological_predictions.md` (decompose criteria)
- Literature: Altmann et al. 2009 PLOS ONE (burstiness); A Story of the Stone PLOS ONE (DFA); Beit-Hallahmi PLOS ONE 2013 (Voynich statistical properties)
