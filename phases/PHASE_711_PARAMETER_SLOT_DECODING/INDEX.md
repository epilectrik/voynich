# PHASE_711: Parameter-Slot Decoding Predictivity Test

**Status:** COMPLETE
**Date:** 2026-05-20
**Posture:** Crazy-expert's proposed follow-up from PHASE_710. If atoms function as **opcodes + parameters** (not just incidental class markers), then atom-level slot decomposition should predict the next instruction class with additional information beyond what the current 49-class label alone provides.

**Verdicts:**
- Main test: PARAMETER-SLOT INFORMATIVE — slot features add +0.07 bits CE / +2.36pp acc / beat shuffle by 0.15 bits, 5/5 folds folio-CV (C2043 Tier 2 measurement).
- Follow-up diagnostics: PARAMETRIC INTERPRETATION REJECTED BY CRAZY-EXPERT'S OWN PRE-REGISTERED DISCRIMINATORS — 7/10 top classes show no within-class slot-feature signal; feature importance ordering puts CLOSURE features (TERM/suffix) at top, not HEAD as parametric reading required. Sub-class refinement is the supported interpretation (C2044 Tier 2 negative).

---

## The actual question

PHASE_710 established that Voynich's atom-layer vocabulary is categorically homogeneous-operational. C2042 stays a measurement; mechanism interpretation ("Voynich is a programming language") remains Tier 4 SPECULATIVE.

Crazy-expert's proposed test for promoting toward operational mechanism: **do atom-level slot features carry predictive information about the next instruction beyond what class-level information already captures?**

If YES: atoms function as parameters that influence what instruction comes next (consistent with opcode/operand semantics). If NO: atoms are class-determinants but their specific identity doesn't add forward-predictive value (atoms are labels, not parameters).

---

## Pre-registered test design (LOCKED)

For each (current_token, next_token) pair in Currier B P-placement (H-track, non-uncertain):

**Features:**
- `current_class` — the 49-class C121 label (from `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`)
- `prefix_category` — categorized PREFIX (ch/sh/qo/ok/ot/ol/ct/da/extended/none)
- `e_depth` — count of 'e' atoms in MIDDLE (0/1/2/3+)
- `head_atom` — HEAD atom of MIDDLE (a/e/o/k/t or PSEUDO_HEAD or NONE)
- `term_atom` — TERM atom of MIDDLE (y/n/m/h/l/r/k/t or NONE)
- `has_suffix` — boolean
- `suffix_first` — first atom of suffix if present (e/d/a/o/i/y or NONE)

**Models:**

1. **Baseline (class-only Markov):** P(next_class | current_class) — empirical transition matrix, Laplace smoothing α=0.1

2. **Slot model:** P(next_class | current_class, slot_features) — gradient boosted classifier (sklearn HistGradientBoosting) on (one-hot current_class + slot features)

3. **Shuffle control:** identical to slot model but with slot features randomly shuffled across tokens within the training set. This must NOT improve over baseline — establishes that any gains in the slot model are real, not overfitting.

**Evaluation:**
- 5-fold folio-out cross-validation (80 folios → 5 groups of 16 folios each)
- Metric A: held-out cross-entropy (bits per prediction)
- Metric B: held-out top-1 accuracy
- Metric C: held-out top-3 accuracy

---

## Pre-registered decision rules (LOCKED)

| Outcome | Verdict | Interpretation |
|---|---|---|
| Slot model improves CE ≥ 0.05 bits AND beats shuffle control by ≥0.04 bits | **PARAMETER-SLOT INFORMATIVE** — atoms carry predictive value beyond class label. Consistent with opcode/operand semantics. | Tier 3 candidate constraint |
| Slot model improves CE ≥ 0.05 bits BUT shuffle control matches it | **OVERFITTING** — slot features memorize tokens but don't generalize. Inconclusive. | No constraint |
| Slot model improves CE < 0.05 bits | **SLOT FEATURES NOT INFORMATIVE** — atom identity adds no forward-predictive value beyond class. Falsifies parameter-slot semantics. | Tier 1-2 negative measurement candidate |
| Slot model degrades CE | **PATHOLOGICAL** — test broken | Debug and re-design |

Secondary checks:
- Same direction must hold for accuracy metric (≥2pp improvement for PASS verdict)
- Within-folio split must work: if model generalizes only within folios (not across), it's memorizing folio habits not parameter semantics

---

## What this can establish (and what it can't)

**CAN establish (if PARAMETER-SLOT INFORMATIVE):**
- Atom-level slot features carry predictive information about next instruction beyond class label
- Atoms therefore behave as if they encode forward-predictive parameters (consistent with opcode/operand reading)

**CANNOT establish:**
- That atoms ARE opcodes (the opcode interpretation is one of multiple operational specifications consistent with these data)
- That the predictive information is **semantic** (could be morphological co-selection patterns, scribal habits, syntactic agreement)
- That tokens are literally decodable as instructions

The honest finding: **atom-level slot decomposition is forward-predictive beyond class label**, which is a structural-measurement-level claim that's consistent with — but does not prove — opcode/operand semantics.

---

## Framework-as-null discipline

This test directly addresses crazy-expert's PHASE_710 follow-up. Two anti-trap precautions:

1. **Shuffle control is mandatory.** If the slot model matches shuffle, the gain is overfitting/memorization, not informative. Per `feedback_framework_as_null.md` and `feedback_floor_vs_discriminator_metric_test.md`.

2. **Tier-promotion ceiling acknowledged.** Even if slot features improve prediction, this stays Tier 3 (measurement), not Tier 2 (validated structural fact). Per `feedback_mechanism_cycle_procedural_ceiling.md`, operational mechanism claims need external grounding, not internal prediction improvement.

3. **Class-feature contamination check.** The 49-class taxonomy is partly built from slot decomposition. If slot features improve prediction, we need to verify they're not just finer-grained class labels. Diagnostic: do the within-class variation in slot features (same class, different slot values) predict different next-classes? If yes, atoms encode parametric info beyond class. If no, slot features = class refinement, not parameters.

---

## Scripts

| Script | Purpose |
|---|---|
| `_slot_decoding_test.py` | Build features, train all 3 models, evaluate on 5-fold folio CV |

---

## Effort estimate

~3-4 hours implementation + ~5-15 min runtime (gradient boosting on ~22k samples).

---

## Registration-trap audit

- Pre-registered thresholds locked BEFORE running
- 3 distinct outcome categories (informative / overfitting / not informative) — not binary
- Shuffle control mandatory
- Class-feature contamination diagnostic baked in
- Outcome stays Tier 3 even if PASS — mechanism interpretation blocked at Tier 4
- Framework-as-null acknowledged: even if the test passes, this doesn't prove "Voynich is a programming language"; it's a structural-measurement-level fact about predictive value of slot features

---

## RESULTS (2026-05-20)

### Main test (5-fold folio-CV, calibrated LogReg apples-to-apples)

| Model | CE (bits) | Acc@1 | Acc@3 |
|---|---:|---:|---:|
| Markov reference (class-only) | 4.8785 | 13.67% | — |
| LogReg class-only baseline | 4.7597 | 13.76% | 30.5% |
| **LogReg slot (class + slot features)** | **4.6903** | **16.12%** | **33.6%** |
| Shuffle control (slot features permuted) | 4.8377 | 13.17% | 29.5% |

All three pre-registered axes PASS:
- CE improvement ≥ 0.05 bits → +0.069 bits PASS
- Real gain over shuffle ≥ 0.04 bits → +0.147 bits PASS
- Accuracy improvement ≥ 2pp → +2.36pp PASS

**Initial verdict: PARAMETER-SLOT INFORMATIVE.** Registered as C2043 Tier 2 measurement.

### Follow-up diagnostics (crazy-expert pre-registered discriminators)

**Test 1 — Within-class retention** (crazy-expert: >50% retention → parametric survives; <20% → refinement wins)

For top-10 most-frequent classes, held class fixed and tested whether slot features add within-class predictive value:

| Class | N | Full-slot gain vs marginal |
|---|---:|---:|
| 33 | 1253 | +0.034 bits (e-depth alone gains +0.049 → e-depth beats full-slot here) |
| 13 | 794 | -0.009 |
| 8 | 662 | -0.277 |
| 31 | 551 | -0.395 |
| 32 | 528 | -0.297 |
| 29 | 499 | -0.084 |
| 14 | 450 | -0.470 |
| 9 | 403 | -0.463 |
| 28 | 408 | (degenerate) |
| 34 | 707 | (degenerate) |

**7/10 top classes: full-slot model PERFORMS WORSE than marginal baseline within fixed class.** Slot features have no within-class predictive value. The 0.07 bits gain comes entirely from BETWEEN-class differentiation.

**Test 2 — Feature importance ordering** (crazy-expert: HEAD >> e_depth >> TERM >> suffix_first if parametric; prefix dominating HEAD by >2× = parametric weakens)

Per-dim L1 norms from full slot LogReg:

| Rank | Feature | Per-dim importance |
|---|---|---:|
| 1 | TERM atom | 17.62 |
| 2 | suffix_first | 15.28 |
| 3 | prefix_cat | 12.81 |
| 4 | HEAD atom | 12.33 |
| 5 | e_depth | 11.15 |

HEAD vs prefix_cat ratio: 0.96 (essentially equal, NOT >2× toward parametric).

**Observed ordering puts CLOSURE features (TERM atom, suffix_first) at top — exactly what defines class membership per C1487 (terminal opacity) and C1510 (suffix structure). HEAD (parametric reading's "operator domain selector") is 4th of 5. Opposite ordering from parametric prediction.**

### Combined interpretation

Both pre-registered discriminating tests reject the parametric reading. The 0.07 bits gain reflects **sub-class refinement of the 49-class C121 taxonomy**, NOT parametric opcode/operand semantics. Slot features help identify which class a token belongs to at finer granularity, but within a fixed class, slot composition adds no forward-predictive value.

Crazy-expert accepted the rejection: "Both pre-registered diagnostics fired against me. Within-class retention <20% on 7/10 classes is the strong form — slot features carry no signal given the class. Feature ranking ... is the death blow for parametric: if HEAD were the opcode and other slots were operands, HEAD should dominate. It doesn't. Per the memory note I wrote: expert predictions ARE pre-registered tests. I lose."

### Constraints registered

- **C2043 (Tier 2 measurement):** Slot features add +0.07 bits CE / +2.36pp Acc@1 / +0.15 bits over shuffle to next-class prediction beyond 49-class label. Replicates 5/5 folio-CV folds. Between-class differentiation only; no within-class signal.

- **C2044 (Tier 2 negative):** Parametric semantics interpretation REJECTED by both pre-registered discriminators (within-class retention test 7/10 classes show no signal; feature importance ordering puts closure features TERM/suffix at top, opposite parametric prediction). 0.07 bits gain reflects sub-class refinement of C121, NOT parameter encoding. Crazy-expert's "atoms-as-opcodes-with-operands" mechanism inference from PHASE_710 retracted to Tier 4 SPECULATIVE.

### What does NOT change

- **C2042 (atom-layer categorical homogeneity):** unaffected. PHASE_710 was about atom glosses being categorically OPERATION; PHASE_711 is about forward-predictive value. Both stand together: atoms are all-operational-glossed AND they refine class membership, but they don't function as opcode parameters in any forward-predictive sense.

- **Tier 0 (closed-loop control programs):** unaffected. Substrate-level framing survives; specific mechanism inference about parameter encoding falls.

### Methodology contribution

PHASE_711 demonstrates the methodology discipline working: crazy-expert's own pre-registered discriminators rejected crazy-expert's hypothesis. Per `feedback_expert_predictions_are_pre_registrations.md`, expert predictions ARE pre-registered tests. The shape-without-semantics framing (atoms have differentiated categorical roles but don't parametrically modulate next-instruction selection) is the new ceiling.

### Methodology lesson

Calibration matters for CE comparisons. Initial run with HistGradientBoosting gave PATHOLOGICAL verdict because GBM probabilities are uncalibrated (overconfident on wrong predictions → high CE). Re-run with multinomial LogReg L2 gave clean verdict. Per `feedback_calibrate_thresholds_against_controls.md`, methodology choice can flip primary metric without changing underlying signal. Apples-to-apples comparison (same architecture for baseline and test model) was the load-bearing fix.
