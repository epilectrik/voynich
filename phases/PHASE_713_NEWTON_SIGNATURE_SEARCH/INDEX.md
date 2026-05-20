# PHASE_713: Hypothesis-Free Newton's Signature Search

**Status:** PRE-REGISTERED, READY TO RUN
**Date:** 2026-05-20
**Posture:** PHASE_712 made the mistake of pre-assigning "excitation = k/h in MIDDLE" which was confounded by qo-PREFIX class. User's correction: don't assume what marks excitation — search for ANY token signature whose post-event dynamics fit Newton's cooling. Find the signature data-first if it exists, with null control.

---

## The actual question

PHASE_712 fail-pattern: I pre-assumed "k/h in MIDDLE marks operational excitation events" without checking whether that labeling was contaminated by PREFIX-class composition. Result: qo-PREFIX dominated the "excited" set, and the test measured qo-distributional habits, not thermal kinetics.

Better question: **Does ANY definable token-signature S have the property that post-S tokens show clean exponential approach to baseline e-density?**

If yes — we've discovered which subset of Voynich's vocabulary marks operational excitations data-first, without assuming.
If no — no token signature shows Newton's-cooling kinetics in this corpus.

Key insight (user): only SOME tokens participate as operational events. Most are scaffolding, structure, or content. The kinetics-bearing subset has to be identified, not assumed.

---

## Design (LOCKED)

### Signature space

Candidate excitation signatures to test:

**Single-property (~25 candidates):**
- Each PREFIX class: qo, ch, sh, ok, ot, ol, ct, da, [extended], NONE
- Each HEAD atom: a-HEAD, e-HEAD, o-HEAD, k-HEAD, t-HEAD, PSEUDO_HEAD
- Each TERM atom: y, n, m, h, l, r, k-term, t-term, NONE
- Each e-depth value: 0, 1, 2, 3+

**Two-way combinations (~40 candidates):**
- PREFIX × HEAD: qo+k, ch+e, sh+e, ok+e, ot+a, etc. (selectively only viable combinations)
- PREFIX × TERM: qo+y, qo+dy, ch+y, sh+y, etc.

**Special patterns (~10 candidates):**
- Tokens containing specific bigrams in MIDDLE (kh, ke, ch, ok, cth)
- Tokens with specific opcode-shape signatures from C1394

Total: ~70-80 candidate signatures. With Bonferroni: p < 0.0006 needed; with FDR-BH: more lenient.

### Stability metric

Track **e-density of next token's MIDDLE** as continuous stability signal:
- e_density(t) = (count of 'e' in MIDDLE of token at position t) / max(len(MIDDLE), 1)
- Range: [0, 1] roughly
- Baseline = mean(e_density) across all tokens

### Cooling curve per signature

For each candidate signature S:
1. Find all tokens matching S → "event tokens"
2. For each event token at position i, look forward at positions i+1, i+2, ..., i+8
3. Average e_density at each lag across all events of signature S
4. Result: cooling curve for S

### Newton's fit

Fit: e_density(lag) = e_∞ + (e_0 − e_∞) · exp(−lag/τ)

Parameters: e_∞ (asymptotic baseline), e_0 (initial post-event value), τ (recovery time constant)

Compute:
- SSE for Newton's
- SSE for constant (just predict mean)
- ΔAIC = AIC(constant) − AIC(Newton's) — positive means Newton's wins
- e_∞ should be close to corpus baseline; τ should be 1-5 (physically interpretable)

### Null distribution

For each signature S of size N_S (number of event tokens):
1. Generate K=500 random subsets of N_S random tokens
2. Compute cooling curve for each random subset
3. Fit Newton's to each
4. Record distribution of ΔAIC across random subsets

For signature S's real ΔAIC to be informative:
- ΔAIC(S) > 99th percentile of null distribution
- AND clean physical interpretation (τ in [1, 5], e_∞ near baseline, e_0 substantially different from baseline)

### Cross-validation

Split lines into two halves randomly:
1. Find top-5 signatures by ΔAIC on half A
2. Test if same signatures show Newton's fit on half B (with pre-registered tau from half A)
3. Survivors of both halves are robust candidates

---

## Pre-registered verdict criteria (LOCKED)

| Outcome | Verdict |
|---|---|
| ≥1 signature passes null (>99th percentile) AND cross-validates AND has physical-interpretable τ AND replicates on Voynich-shuffle null below threshold | **OPERATIONAL EXCITATION SIGNATURE DISCOVERED** — Tier 2 candidate; identifies specific token-class as kinetic excitation event |
| ≥1 signature passes null AND cross-validates BUT mensural ALSO shows Newton's-fit signatures | **FLOOR** — exponential recovery isn't thermal-specific; any structured-symbolic system produces some Newton's-like signatures by chance |
| Best signature ΔAIC fails null OR fails cross-validation | **NO DISCOVERED KINETIC SIGNATURE** — Voynich substrate doesn't have a token-class subset with thermal-kinetic dynamics; thermal interpretation loses kinetic support |
| Multiple signatures pass but they're correlated (same underlying class viewed differently) | **CONVERGENT SIGNATURE** — narrow to the parsimonious one |

---

## Why this is better than PHASE_712

PHASE_712 forced a specific labeling (k/h in MIDDLE) and the labeling happened to be confounded by PREFIX. This phase:
- Doesn't pre-assume which property marks excitation
- Tests against null distribution explicitly (was my key omission)
- Cross-validates discovered signatures
- Includes mensural floor check

If kinetic structure exists, it'll find it under SOME signature. If no signature shows it, that's a real negative — not a methodology gap.

---

## Caveats baked in

- Multiple-comparison correction is honest (Bonferroni or FDR-BH explicit)
- Cross-validation prevents single-fold overfit
- Mensural floor check per `feedback_floor_vs_discriminator_metric_test.md`
- Per `feedback_framework_as_null.md`: even if we find a Newton's-fit signature, this doesn't validate thermal MECHANISM — it identifies a token-class with exponential post-event recovery dynamics. The interpretation step ("therefore this token-class = thermal excitation") remains separate.
- Per `feedback_mechanism_cycle_procedural_ceiling.md`: this can give us a structural measurement (specific signature has kinetic-fit) but cannot establish operational mechanism without external grounding.

---

## Implementation

| Script | Purpose |
|---|---|
| `_signature_search.py` | Build all candidate signatures, compute cooling curves, fit Newton's, run null distribution, cross-validate |

---

## Effort estimate

~3-4 hours implementation, ~10-15 min runtime (signature × null bootstrap × cross-validation).
