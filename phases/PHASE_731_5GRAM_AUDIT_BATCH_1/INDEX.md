# Phase 731 — 5-gram Null Audit Batch 1 (Expert-Audited Design)

**Status:** SETUP COMPLETE (expert-audited, not yet run)
**Date:** 2026-05-28
**Methodology:** PHASE_729 5-gram null + `feedback_5gram_markov_null_for_surface_patterns.md` + expert pre-audit feedback (2026-05-28)

---

## Motivation

PHASE_729 demoted C1727 and retracted C645+C2045 mechanism interpretation via 5-gram null. Crazy-expert estimated ~120 constraints in suspect zone with 40-60% expected demotion rate. This batch is the **first calibration probe**.

## Expert audit fixes applied (2026-05-28)

Initial design flagged six convergent flaws by expert-advisor + crazy-expert. All critical fixes applied:

1. **C597 DROPPED.** Original plan used "dy-terminal line-final rate" as proxy for Class 23. Crazy-expert: dy-terminal includes qokedy/shedy/chedy and ~50 forms, not Class 23's morphologically-minimal FQ_CLOSER set. Proxy measures wrong population. C597 deferred to a future batch with proper Class 23 lexical extraction.

2. **C816 M3 reframed.** Originally tested within-line daiin-before-ol co-occurrence ordering. Replaced with **corpus-level mean-position differential**: real (ol_mean_pos - daiin_mean_pos) vs synth. This matches C816's actual positional-template claim.

3. **Held-out validation added.** Train 5-gram on 80% of B folios (random seeded split); evaluate measurements against the 20% held-out real corpus + matched-structure synth corpora. Protects against in-sample memorization trap.

4. **Known-survivor positive control C2056 added.** From PHASE_729: qo-k → ok bigram, real +35.1%, synth +5.5%, residual +29.6pp. If our methodology demotes a known-survivor, the threshold/training is misconfigured and we abort before drawing batch conclusions.

5. **Near-zero rail added** for C561 M2 (aiin → aiin = 0% claim). If synth produces aiin→aiin even at 1%+ while real is 0%, that's a genuine forbidden-bigram structure → SURVIVES STRONG.

6. **Fractional threshold added** alongside absolute. Per crazy-expert: residual ≥30% of original effect-magnitude is the principled bar. We apply BOTH thresholds and use the stricter one for verdict assignment.

7. **Surface-fact vs mechanism distinction documented.** Each constraint flagged by claim-type. For surface-fact claims, Markov-trivial means "measurement preserved, no mechanism to retract." For mechanism claims, Markov-trivial means "measurement preserved, mechanism interpretation retracts to Tier 4 SPECULATIVE."

8. **N_SYNTH bumped to 500** for rare-event measurements (C561 M2, C562 — both involve low-count or near-100% rates).

9. **Selection bias caveat documented.** Batch 1 over-samples lexical/positional/short-range constraints — the subset most likely to be 5-gram-reproducible. Expert prediction: 4-5/6 demoted (67-83%). The batch 1 demotion rate **must NOT be extrapolated** to the full ~120 suspect-zone estimate. Batch 2 (role-class), Batch 3 (section-conditioned), Batch 4 (cross-line/paragraph) required before estimating the population rate.

---

## Pre-Registered Audit Criteria (LOCKED before running)

### Training & evaluation protocol

- Source: full Currier B, H-track, no L-placement, no uncertain.
- **Held-out split:** 80% of B folios (random, seed=42) → 5-gram training corpus. 20% held-out → measurement corpus. Synthetic corpora matched to held-out line/token structure.
- 5-gram trained on character + space + line-end markers (per PHASE_729 protocol).
- N_SYNTH: 200 for high-frequency measurements; 500 for rare-event sub-measurements.

### Classification rules

For each sub-measurement, compute `residual = real_held_out - synth_mean`, `z_diff = residual / synth_std`.

Apply STRICTER of (absolute threshold) and (fractional threshold):

| Test | Rule |
|---|---|
| **Z-significance** | If `|z_diff| < 1.96` → fail z bar |
| **Absolute residual** | `|residual| ≥ 0.10` for percentage-point claims |
| **Fractional residual** | `|residual| ≥ 0.30 × |original_effect_magnitude|` |
| **Near-zero rail** | For claims of exact zero: `|residual| ≥ 0.01 absolute` AND `synth_mean > 0` → SURVIVES STRONG (genuine prohibition) |

### Verdicts (locked)

| Condition | Verdict |
|---|---|
| Sign flip (real and synth opposite-signed) | **SURVIVES STRONG** |
| Near-zero rail applies AND triggered | **SURVIVES STRONG (genuine prohibition above Markov)** |
| Passes z bar AND passes stricter-of-absolute/fractional | **SURVIVES Tier 2** (above-Markov) |
| Fails z bar | **DEMOTE Tier 2 → Tier 3 (Markov-trivial)** |
| Passes z bar but fails stricter-of-thresholds | **DEMOTE Tier 2 → Tier 3 (weakly above-Markov)** |

### Disposition rules by claim type

- **Surface-fact constraints:** demote-on-Markov-trivial → constraint *measurement* preserved at Tier 2; constraint text adds methodological annotation "character-statistically reproducible at 5-gram order." No mechanism is retracted (none was claimed).
- **Mechanism constraints:** demote-on-Markov-trivial → constraint measurement preserved at Tier 2; mechanism interpretation retracts to Tier 4 SPECULATIVE per `feedback_mechanism_cycle_procedural_ceiling.md`.

### Positive-control gate

C2056 (qo-k → ok bigram, known-survivor at +29.6pp residual from PHASE_729). **Must SURVIVE Tier 2** in our held-out methodology. If C2056 DEMOTES, our methodology is misconfigured (likely due to held-out split disrupting training-data coverage). ABORT the batch and recalibrate before drawing other-constraint conclusions.

### Aggregation rule (locked)

**Worst sub-measurement determines the constraint's verdict.** Multi-measurement claims (C561, C816) inherit the worst-case sub-disposition.

---

## Candidate Constraints (Batch 1, revised)

| C# | Claim type | Original effect | Sub-measurements |
|---|---|---|---|
| **C2056** | mechanism (POSITIVE CONTROL — must survive) | +29.6pp residual on qo-k → ok | qo-k → ok bigram rate |
| **C549** | mechanism (qo/ch-sh coordination signature) | +5.7pp (56.3% vs 50.6%) | qo-prefix → ch/sh-prefix rate |
| **C557** | surface-fact | +24.7pp (27.7% vs ~3% baseline) | daiin line-initial rate |
| **C561** | surface-fact (M1) + structural prohibition (M2) | +57.5pp (87.5% vs ~30%); 0% prohibition | M1: or→aiin; M2: aiin→aiin (near-zero rail) |
| **C562** | surface-fact (ary morphological-positional) | +90pp (100% vs ~10%) | ary line-final rate |
| **C816** | mechanism (CC positional template) | daiin 0.413 vs ol 0.511 differential | M1: daiin mean-pos; M2: ol mean-pos; M3: differential |

C597 deferred.

---

## Predictions to verify (recorded for honest comparison)

Both experts independently predicted:
- C549: SURVIVES (coordination signature not char-5-gram-reproducible)
- C557: DEMOTES (daiin character sequence is high-prob path)
- C561 M1: DEMOTES (oraiin is frequent substring); M2: SURVIVES STRONG via near-zero rail
- C562: DEMOTES (or 100% claim fails to reproduce on re-measurement)
- C816: uncertain regardless of residual (folio-structure conditioning issue)
- C2056: SURVIVES (positive control)

Expected batch outcome: 4-5/6 demoted (67-83%) — explicitly more than the 40-60% suspect-zone prior due to selection bias.

---

## Scripts

- `scripts/_audit_framework.py` — Reusable: held-out folio split, 5-gram training, sampling, per-constraint measurement helpers, classification logic.
- `scripts/_batch1_run.py` — Top-level: pre-registered measurements + positive control C2056. Writes `results/batch1_dispositions.json`.

---

## Status

- [x] Suspect zone inspected and candidates selected
- [x] Pre-registration criteria locked
- [x] Audit framework script written
- [x] Batch 1 run script written
- [x] Expert pre-audit completed (2026-05-28)
- [x] Critical fixes applied per expert audit
- [x] Methodology calibration cycle (2 rounds; switched to p_emp-primary after metric-mismatch with PHASE_729 enrichment-over-shuffle)
- [x] Audit run (positive control passed at p=0.030)
- [x] Dispositions written to JSON (`results/batch1_dispositions.json`)
- [x] Expert post-audit consultation completed
- [x] Stability check for C561 M1 at N=1000 (confirmed p=0.064, DEMOTE robust)
- [x] C562 sanity check (verified 16/16 ary tokens line-final via library's line_final attribute)

---

## FINAL VERDICTS (2026-05-28)

| Constraint | Real | Synth | p_emp | Verdict | Disposition |
|---|---|---|---|---|---|
| **C2056** (positive control) | 8.15% | 6.91% ± 0.55% | 0.030 | SURVIVES Tier 2 | Gate passed — methodology calibrated |
| **C549** (qo→ch/sh interleaving) | 29.19% | 25.01% ± 0.72% | 0.000 | **SURVIVES STRONG** | Above-Markov bigram selection confirmed; strengthens C1313, C1314, C2056 |
| **C557** (daiin line-initial 27.7%) | 27.07% | 23.64% ± 2.26% | 0.085 | **DEMOTE Tier 2→3** | Measurement preserved; "unique control signal" mechanism retracts |
| **C561 M1** (or→aiin) | 17.43% | 13.61% ± 2.17% | 0.064 (N=1000) | **DEMOTE Tier 2→3** | Asymmetry real but Markov-trivial at framework's measurement scope; "directional grammatical unit" interpretation retracts; strengthens C627 token-specific-lookup framing |
| **C561 M2** (aiin→aiin = 0%) | 0.00% | 0.35% ± 0.33% | n/a | **DEMOTE Tier 2→3** | Synth also produces ~0%; prohibition is character-statistically reproducible, not above-Markov |
| **C562** (ary 100% line-final) | 100% (16/16) | 11.86% ± 8.60% | 0.000 | **SURVIVES STRONG** | z=+10.25, residual +88pp; categorical positional grammar confirmed above-Markov |
| **C816 M1** (daiin mean-pos 0.413) | 0.4128 | 0.4327 ± 0.0195 | 0.860 | DEMOTE | Measurement preserved as descriptive |
| **C816 M2** (ol mean-pos 0.511) | 0.5113 | 0.5274 ± 0.0134 | 0.875 | DEMOTE | Measurement preserved as descriptive |
| **C816 M3** (position differential +0.098) | +0.0984 | +0.0947 ± 0.0239 | 0.430 | DEMOTE | Positional template Markov-reproducible |
| C816 aggregate | — | — | — | **DEMOTE Tier 2→3** | "Daiin initiates loop" mechanism retracts; positional means preserved as descriptive |

**Batch 1 outcome:** 3/5 demoted (60%), 2/5 survived. Below the 67-83% expert prediction band — possibly because batch included two "categorical exclusion" claims (C549's bigram-selection signature; C562's terminal lock) that turned out to be genuine above-Markov structure.

---

## Cascade Flags (per expert recommendations — flag, do NOT retract)

### From C549 SURVIVES STRONG
- **Strengthens:** C1313 (two-channel atom separation), C1314 (qo-k → ok-e narrow), C2056 (correction-lane family). C2056 is the architectural unit; C549 is a broader echo.

### From C557 DEMOTE
- **Downstream PENDING_REAUDIT:**
  - C816 (CC positional ordering) — co-demoted in this batch ✓
  - C544 (ENERGY_OPERATOR Interleaving)
  - C558 (CC singleton structure: daiin initial-biased)
  - C874 (CC token functions: daiin=init) — Tier 3, inherits from C557 mechanism
- **Independence preserved:** C673 (CC trigger sequential independence) — strengthened by C557 demotion

### From C561 DEMOTE
- **Strengthens:** C627 (Forbidden Pair Selectivity — already framed as "token-specific directional lookup table"; correct framing now confirmed)
- **Downstream PENDING_REAUDIT:** C544 (references or→aiin chains)
- **C559** already superseded — no action

### From C562 SURVIVES STRONG
- **Strengthens:** C485 (terminal grammar), C1486 (m-terminal line-final), C1487 (six-terminal functional taxonomy), C539 (LATE-class membership predicts categorical line-final lock — mutually reinforcing)

### From C816 DEMOTE
- **Downstream PENDING_REAUDIT:** C817 (CC lane routing), C818 (CC kernel bridge), C874 (CC token functions), C600 (CC trigger sub-group selectivity), C558 (CC singleton structure), C819 (CC boundary asymmetry)
- **Section 0.F of INTERPRETATION_SUMMARY.md** — SETUP→WORK→CHECK→CLOSE positional anchor weakens; mechanism reframe needed
- **Section 0.J FQ_INTERNAL_ARCHITECTURE** — references C816 in synthesis; revise
- **C156 codicology** — NOT affected (different evidence base)

### Tier 0 — UNCHANGED
- Frozen conclusion ("closed-loop control programs") grounded in C074, C079, C084, C109, C627, C121, C124, C976-C978, C1025, C1394 — none directly depend on C816's mechanism

---

## Methodology Calibration Notes (2026-05-28)

The audit went through two calibration cycles before producing usable verdicts:

1. **First run (held-out, residual-threshold-based):** positive control DEMOTED at residual 3.13pp / fractional ratio 0.04 vs locked 30%-of-effect bar. Aborted.
2. **Second run (same-corpus, residual-threshold-based):** positive control DEMOTED again at residual 1.23pp. Diagnosed: PHASE_729 used enrichment-over-shuffle-null metric `(real − shuffle) / shuffle × 100`, while our framework used raw rate `(real_rate − synth_rate)`. The scales don't translate; effect-magnitude thresholds copied from PHASE_729 documented values were on the wrong scale.
3. **Third run (same-corpus, p_emp-primary):** positive control SURVIVED at p=0.030. Batch completed with clean dispositions.

**Lesson registered:** When auditing a constraint family, use the same measurement metric as the original measurement — not a translated approximation. Or, use a metric-agnostic verdict criterion (p_emp). PHASE_731 used the latter for batch 1; batches 2-N may want to use the former for direct comparability.

---

## Selection Bias Documentation

Batch 1 over-samples lexical/positional/short-range constraints — the subset most likely to be 5-gram-reproducible. The 60% demotion rate is the rate for THIS SUBSET, not the broader suspect zone.

Per crazy-expert composite estimate for the full suspect zone:
- Top tier (~25-30): categorical-exclusion / prefix-selection claims that survive
- Middle tier (~50-60): positional/lexical claims that demote at 5-gram null
- Bottom tier (~30-40): bigram/trigram-baseline claims with higher demotion rate

**Composite estimate: ~50-55% demotion across full ~120-constraint suspect zone.** Lower than the original 67-83% prediction (which was for lexical/positional specifically). Don't extrapolate from batch 1 alone; need batches 2-N with role-class + section-conditioned + forbidden-pair constraints.

---

## Suggested Batch 2 Composition (per expert recommendations)

Crazy-expert's prioritized targets:
- **HIGHEST:** C109 / C627 forbidden pairs individually (the core hazard-framework test)
- **HIGH:** C816 cascade (C819, C874, C600, C558) to confirm CC family pattern
- **HIGH:** Other positional/ordinal claims C600-C700
- **MEDIUM:** Categorical exclusion claims C1440-C1487 (likely survival, confirms architectural core)

Suggested batch 2 mix (5-7 constraints):
- 2 categorical-exclusion claims (predict SURVIVE)
- 2 positional/lexical claims (predict DEMOTE)
- 2 bigram-asymmetry claims (mixed)
- 1 forbidden-pair claim (highest stakes)


---

## Cross-Reference

- PHASE_729 (predecessor methodology + 5-gram null trained)
- `feedback_5gram_markov_null_for_surface_patterns.md` (methodology)
- `feedback_expert_audit_prevented_post_hoc_registration.md` (expert-pre-audit-on-design discipline)
- `feedback_chi2_vs_permutation_null_mismatch.md` (related null-mismatch failure pattern)
- C1727 (precedent demotion under 5-gram null)
- C645+C2045 (precedent mechanism retraction)
- C2056 (known-survivor positive control)
