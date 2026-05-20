# PHASE_712: Thermodynamic Kinetics Test for Kernel

**Status:** PRE-REGISTERED, READY TO RUN
**Date:** 2026-05-20
**Posture:** Test whether kernel dynamics (k/h excitation → e recovery) follow Newton's law of cooling — the specific exponential-decay-to-equilibrium signature of thermal heat transfer. If yes, this provides EXTERNAL grounding for the "k=heat / e=stability" interpretation at the dynamics level, going beyond PHYS's snapshot measurements (lag-2 e-return rate) to actual kinetic curve shapes.

---

## Why this matters

PHASE_711 confirmed: parametric semantics interpretation of slot features REJECTED. Atoms function as class-determinants (sub-class refinement), not as decodable operands.

But the KERNEL-LEVEL interpretation (k/h = excitation, e = stability) survived PHASE_711 untouched — that's at the dynamics level, not the parametric-coupling level. PHYS phase showed:
- e dominates (36% of tokens)
- k/h are rare excursion events (~0.3%)
- Rapid return to e after k/h (52.6% at lag-2 vs 36% baseline)
- LINK-heavy during stable, LINK-sparse during intervention

These ARE consistent with damped control system dynamics. But "damped control" is broad. **Newton's law of cooling is specific: exponential decay back to equilibrium with characteristic time constant τ**, independent of perturbation magnitude. This is a sharper signature.

If kernel dynamics fit Newton's cooling: **direct kinetic measurement of thermal-specific behavior**, providing external grounding to break the procedural ceiling (per `feedback_mechanism_cycle_procedural_ceiling.md`).

If they don't: kernel reading stays at "damped control" generic level; thermal interpretation loses its strongest empirical pillar.

---

## Three discriminating sub-tests (LOCKED before run)

### Test A: Cooling-curve shape

For each escalation event (token containing k or h in MIDDLE) in Currier B P-placement, measure e-density at lags 1, 2, 3, 4, 5, 6, 7, 8 tokens forward. Average across all escalation events to get the cooling curve.

Fit three candidate models:
- **Newton's cooling:** e(t) = e∞ − (e∞ − e₀) · exp(−t/τ)
- **Linear decay:** e(t) = e∞ − (e∞ − e₀) · max(1 − t/T, 0)
- **Power-law:** e(t) = e∞ − (e∞ − e₀) · t^(−α)

Compare via AIC. **Thermal prediction:** Newton's wins by ΔAIC ≥ 10 vs both alternatives.

### Test B: Excursion-magnitude → recovery-time scaling

Cluster consecutive escalation tokens into "excursion episodes." For each episode:
- magnitude = number of consecutive k/h tokens
- recovery_time = tokens until 3 consecutive stable (e-present, no k/h) tokens

Newton's law: τ independent of perturbation magnitude → logarithmic scaling of recovery time with excursion magnitude.

**Thermal prediction:** recovery_time = τ · log(magnitude + 1) + c, R² ≥ 0.3
**Linear prediction (rate-limited):** recovery_time = a · magnitude + c
**Noise prediction:** No relationship (R² < 0.1)

### Test C: Onset-vs-recovery asymmetry

For each excursion episode:
- onset_time = tokens since last stable e-region BEFORE the event
- recovery_time = tokens until next stable e-region AFTER the event

**Newton's pure prediction:** Symmetric (onset/recovery ratio ≈ 1.0)
**Thermal-with-insulation prediction:** Recovery > onset (cooling slower than heating)
**Non-thermal/symmetric-Markov prediction:** Onset/recovery ratio determined by symmetry of transition matrix

**Test passes** if asymmetry observed (ratio < 0.8 or > 1.2) AND consistent direction across events.

---

## Control corpora (mandatory per `feedback_floor_vs_discriminator_metric_test.md`)

| Corpus | Source | Expected on Test A |
|---|---|---|
| **Voynich Currier B** | H-track, P-placement | Target — fits Newton's if thermal |
| **Voynich shuffled** | Within-line random shuffle of token order | Null — no kinetic structure should emerge |
| **Mensural duration streams** | `phases/MENSURAL_NOTATION_HYPOTHESIS/results/mensural_streams.json` | Non-thermal structured-symbolic — should FAIL Newton's (no thermal kinetics in music notation) |
| **Synthetic Newton's cooling** | Generated stream with known τ=2.0 exponential recovery | Positive control — should PASS Newton's cleanly |

Mensural's role: if it ALSO passes Newton's, then the kinetic-shape test is a generic floor for structured-symbolic systems, not a thermal-specific discriminator. Per PHASE_706 lesson.

---

## Pre-registered verdict criteria (LOCKED)

| Outcome | Verdict |
|---|---|
| Voynich passes A+B+C; mensural FAILS A | **THERMAL SIGNATURE CONFIRMED** — external grounding for k=heat / e=stability at kinetic level. Tier 2 candidate constraint. |
| Voynich passes A only (cooling-curve fits but no magnitude scaling, no asymmetry); mensural FAILS A | **DAMPED CONTROL SIGNATURE** — generic exponential relaxation but not specifically thermal. Tier 3 candidate. |
| Voynich passes A; mensural ALSO passes A | **FLOOR** — Newton's-cooling-like recovery is a generic structured-symbolic signature. Inconclusive for thermal interpretation. |
| Voynich fails A (Newton's doesn't beat linear/power) | **NO KINETIC STRUCTURE** — PHYS findings should be reframed as statistical regression-to-mean, not thermal recovery. Thermal interpretation loses empirical pillar. |

---

## Why this could break the procedural ceiling

Per `feedback_mechanism_cycle_procedural_ceiling.md`: internal procedure establishes substrate facts; mechanism interpretations need external grounding.

Newton's cooling is **physics, not data**. The exponential form, the constant τ, the asymmetric onset/recovery — these are PREDICTIONS derived from heat equations, not patterns we'd expect to emerge from generic symbolic systems unless those systems are actually modeling thermal dynamics.

If Voynich kernel dynamics specifically match Newton's predictions:
- The k=excitation/heat reading gets KINETIC grounding (not just static structural narrowing per PWRE)
- The procedural-DSL framing strengthens significantly: not just "operational-shape vocabulary" but "operational-kinetics dynamics"
- This is the external grounding the methodology memory said was needed

If Voynich kernel dynamics DON'T match Newton's specifically:
- "k=heat" framing weakens — kernel may be damped-control but the specific thermal interpretation loses kinetic support
- We'd revise the substrate framing toward generic-control-system, not thermal-specifically

Both outcomes are informative. This is a discriminating test, not a confirmation test.

---

## Implementation plan

| Script | Purpose |
|---|---|
| `_thermo_kinetics_test.py` | Build kernel sequences, run all 3 tests, fit curves, compare AIC |

---

## Effort estimate

~2-3 hours implementation, ~5 min runtime.

---

## Registration-trap audit

- Pre-registered thresholds locked BEFORE running
- 4 outcome categories (CONFIRMED / DAMPED / FLOOR / NULL) — not binary
- Mensural floor check mandatory
- Synthetic positive control validates methodology
- Random shuffle null rules out generic ordering effects
- Verdict depends on RELATIVE performance vs mensural and synthetic — apples-to-apples
- Even if PASSES, mechanism interpretation stays Tier 3 (kinetic-fit ≠ proof of operational decode)
- Framework-as-null: the result fits the thermal narrative we've been building, so per `feedback_framework_as_null.md` extra skepticism warranted
- Crazy-expert's PHASE_711 falsification fresh in mind — predictions matching theory ≠ theory validated; we need the discriminators (mensural floor + synthetic positive) to work
