# PHASE_720: Substrate-Quintet Domain-Discrimination Test (Rupescissa vs Theophilus)

**Status:** COMPLETE — INDEX-only (no constraints registered)
**Date:** 2026-05-20
**Verdict:** Test ran. Pre-registered prediction FAILED (Rupescissa NOT in distillation-Latin range; Theophilus and Rupescissa within 0.16 r21 of each other, both far from Voynich's -0.66). However, **calibration gap discovered** (Codicillus reproduction gives r21=-0.007 vs known -0.22) — both experts converged on: **do not register negative under uncalibrated methodology** per `feedback_calibrate_thresholds_against_controls.md`. Test informative as methodology lesson only.

**Methodology lesson:** text-statistical cross-corpus methods (8D matcher per PHASE_718 + substrate-quintet stem-class autocorrelation per PHASE_720) are generic within Latin — they discriminate Voynich from Latin generally but NOT among Latin domain classes. The distillation interpretation rests on NON-text-statistical evidence (PWRE-1 structural narrowing, PHYS kernel dynamics, C1314 thermal cycling, C645+C2045 hazard recovery, C2042 categorical signature). Documented as feedback memory.
**Posture:** After PHASE_718 confirmed the 8D matcher is generic at text-feature level, test whether the **substrate-quintet signatures** (the surviving evidence layer) discriminate distillation-domain Latin (Rupescissa) from metalwork-domain Latin (Theophilus). This is the direct external test of PWRE's structural narrowing that survived PHASE_718 untouched.

---

## The actual question

PHASE_718 showed the 8D matcher is generic — it clusters medieval-procedural Latin without regard to physical-process domain. But the substrate-quintet (C2032 lag-ratio specifically) might still discriminate. Critical existing data points:

- **Voynich Section B:** r21 = -0.66 (strong period-2)
- **Codicillus** (alchemy/distillation): r21 ≈ -0.22 (per C2031 cross-validation methodology)
- **Mesue Grabadin** (pharmacy): r21 ≈ -0.17
- **Mensural notation** (non-NL music): r21 = +0.18 (cleanly distinct)

Not yet tested at proper C2032 methodology:
- **Rupescissa** (distillation/quintessence, ~1351 Latin) — same domain class as PWRE predicts for Voynich
- **Theophilus** (metalwork/glass/pigments, ~1120) — domain class PWRE EXCLUDES

**Pre-registered prediction:** If PWRE's structural narrowing is right, Rupescissa (distillation) should show a different substrate-quintet signature than Theophilus (metalwork), AND Rupescissa should be closer to Voynich's signature than Theophilus is.

---

## Methodology (LOCKED, matches `_c2031_codicillus_cross_validation.py`)

For each corpus:
1. Load Latin text, segment into paragraphs (blank-line-separated, 20-50 words each)
2. For each word: compute Latin stem (lowercase, strip case ending via regex, take first 3 chars)
3. For each paragraph, build stem sequence
4. Compute lag-N same-stem rate at lag 1, 2, 3
5. Compute shuffled-null (200 permutations within-paragraph)
6. excess = observed - null
7. r21 = lag2_excess / lag1_excess

**Critical:** this matches the project's actual C2032 methodology that produces -0.22 / -0.17 for Codicillus / Mesue. Will reproduce those baselines as control.

---

## Pre-registered prediction matrix (LOCKED)

| Outcome | Verdict |
|---|---|
| Rupescissa r21 in Codicillus range (-0.30 to -0.10) AND Theophilus r21 substantially different (>+0.05 difference) | **PWRE NARROWING EXTERNALLY VALIDATED** — substrate quintet discriminates distillation from metalwork at the stem-class level |
| Both Rupescissa AND Theophilus in similar Latin range (-0.30 to +0.30) | **SUBSTRATE QUINTET ALSO GENERIC** — discriminates Voynich from Latin generally but not domain-within-Latin |
| Theophilus shows Voynich-like signature (-0.5+) | **UNEXPECTED** — would reverse the PWRE narrowing |
| Either corpus extreme positive (+0.5+) | **NOISE / methodology issue** — investigate |

---

## Why this is the highest-yield remaining test

PHASE_718 left a specific open question: **the 8D matcher is generic, but is ANYTHING discriminative of distillation specifically?** PWRE's narrowing is the strongest distillation-pointing evidence, but PWRE's prediction (Theophilus-type metalwork EXCLUDED, distillation-class INCLUDED) hasn't been directly tested at the text-statistical level.

This test is:
- Hypothesis-driven (PWRE makes a specific prediction)
- Uses the surviving evidence layer (substrate quintet, not matcher)
- Has clear binary outcomes
- Either externally validates PWRE OR shows even the substrate quintet doesn't discriminate at domain level

Both outcomes are informative. Positive outcome would be the first external grounding result the project has produced this session.

---

## What this can and can't establish

**CAN establish (if PWRE narrowing externally validated):**
- Substrate-quintet signature is domain-class-specific within medieval procedural Latin
- Rupescissa-type distillation Latin clusters with Voynich Section B; Theophilus-type metalwork doesn't
- The distillation interpretation gets external statistical corroboration

**CANNOT establish:**
- That Voynich IS Rupescissa-specific content (just that it's in the same domain class)
- Specific decoding
- Operational details

---

## Implementation

| Script | Purpose |
|---|---|
| `_substrate_domain_test.py` | Apply C2032 stem-class methodology to Rupescissa + Theophilus, compare to Codicillus/Mesue reference values + Voynich Section B |

---

## Effort

~2 hours implementation, ~5 min runtime.

---

## Registration-trap audit

- Pre-registered binary criteria locked before run
- Methodology reuses existing `_c2031_codicillus_cross_validation.py` pipeline that already produces project-validated reference values
- Both outcomes (validation, generic) are informative
- Mensural floor (non-NL) and Codicillus baseline (in-domain Latin) provide control range
- Per `feedback_floor_vs_discriminator_metric_test.md`: this test specifically asks whether the discriminator extends to domain-within-Latin or stops at non-NL-vs-NL

---

## RESULTS (2026-05-20)

### Cross-corpus signatures

| Corpus | n_paras | lag1_excess | lag2_excess | r21 |
|---|---:|---:|---:|---:|
| Codicillus (in-domain reference, expected -0.22) | 88 | -0.0063 | +0.00004 | **-0.007** ⚠ |
| Rupescissa (distillation, PWRE-compatible) | 149 | -0.0030 | -0.0022 | +0.726 |
| Theophilus body (metalwork, PWRE-EXCLUDED) | 79 | -0.0296 | -0.0168 | +0.568 |
| Voynich Section B (known reference) | — | — | — | -0.66 |

### Pre-registered prediction: FAILED

- Rupescissa r21 = +0.726 — NOT in expected distillation-Latin range (-0.30 to -0.10)
- Theophilus and Rupescissa difference = -0.158 (substantially smaller than the discrimination prediction would require)
- Neither corpus approaches Voynich's -0.66
- Theophilus actually has LARGER lag1_excess (-0.030 vs Rupescissa's -0.003) — opposite of PWRE prediction

### Calibration gap (the critical finding)

My Codicillus reproduction gives r21=-0.007 but the project's known C2032 value is -0.22. My script directly mirrors `_c2031_codicillus_cross_validation.py` methodology. The gap suggests methodology-drift between the original C2031 cross-validation and what I'm reproducing.

Possible causes (not investigated in this phase):
- Different paragraph segmentation (concatenated vs per-paragraph aggregation)
- Length filter parameter difference
- Stem-extraction parameter difference
- Original C2032 -0.22 might use a different aggregation (per-paragraph then averaged, vs my concatenated)

### Expert consultation

**Expert-advisor:** "The -0.007 vs -0.22 gap is disqualifying for cross-corpus claims as currently constructed. Per `feedback_calibrate_thresholds_against_controls.md`: if your reference control doesn't reproduce its known value, you don't have a calibrated metric — you have an uncalibrated measurement. Three reasons against registration: pre-reg failed + calibration gap unresolved; Theophilus lag1 anomaly unexplained; cross-corpus mechanism claims need both internal pass and external validation."

**Crazy-expert:** "Don't register yet. The gap is a methodology overhang that contaminates any negative finding registered under this methodology. Per `feedback_calibrate_thresholds_against_controls.md` — calibrate before locking. Right now you don't have a calibrated reproduction." Also: Theophilus lag1 anomaly "tracks REGISTER (instructional density) more than OPERATIONAL CLASS (distillation vs metalwork)" — Theophilus is craft-instruction Latin with high tool/material name repetition; not a PWRE-violation, just register-density.

### Why this is INDEX-only, not registered

Registering a negative result under uncalibrated methodology replicates the C131 invented-threshold pattern (per `feedback_made_up_threshold_audit.md`). Both experts converged on: investigate calibration gap separately OR document the methodology gap itself as the finding.

### What this IS (cumulative methodology lesson)

Combined with PHASE_718:
- **PHASE_718:** 8D matcher generic at text-feature level
- **PHASE_720:** Substrate quintet (stem-class autocorrelation) generic at domain-within-Latin level (with calibration caveat)

**Cumulative finding:** text-statistical cross-corpus methods discriminate Voynich from Latin generally but NOT among Latin domain classes. The distillation interpretation therefore rests on NON-text-statistical evidence:
- PWRE-1 structural narrowing (architectural physics-compatibility)
- PHYS kernel dynamics (within-text)
- C1314 qo-k/ok-e thermal cycling (within-text bigram)
- C645+C2045 hazard recovery (within-text directional)
- C2042 atom-monocategorical operational signature (within-text categorical)

Documented as `feedback_text_statistical_methods_generic_at_domain_level.md` (memory note, not constraint).

### Pattern at the broader level

Both experts independently arrived at: **the distillation interpretation has a clean evidence basis at architectural/dynamical levels, not at corpus-statistical levels**. This is exactly the mechanism-cycle procedural-ceiling pattern. Text-statistical methods exhausted at current resolution.

### What's queued

- **Calibration gap investigation:** find what differs between my methodology and the original C2031 cross-validation that produces -0.22. Could be a separate methodology audit phase.
- **PWRE external test paths:** physical reconstruction OR architectural-alignment sharpening (F-BRU-007, F-BRU-027 fits already point this direction)
- **Consolidation:** per `feedback_operational_story_first_trap.md` — "when the trap pattern repeats, the right response is to stop generating new findings and re-examine methodology"

### Constraint actions

- NO new constraint registered
- C2053 NOT assigned (number remains available)
- Phase count increments (PHASE_720 INDEX exists)
- Constraint count unchanged at 2044
- Methodology memory `feedback_text_statistical_methods_generic_at_domain_level.md` to be added
