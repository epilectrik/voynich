# PHASE_722: Rupescissa Intra-Corpus Register Stratification

**Status:** COMPLETE — INDEX-only (no constraints registered)
**Date:** 2026-05-20
**Verdict:** Pre-registered criteria nominally PASS but controls flag noise-floor concerns. Both experts converge: DO NOT register. Random quartile control (seed 0) produced r21=-0.658 — Voynich's magnitude — purely by chance in a random subset. Recipe-dense lag1=-0.00162 is noise floor (6× smaller than Codicillus canonical -0.01013); r21=-1.44 is a ratio artifact from lag1≈0. The metric has no discriminating power at quartile-N (~70 paragraphs). Direction prediction (recipe→period-2, theory→monotonic) DID work as crazy-expert predicted, but magnitude failed silently. Registered as **7th distinct failure pattern** in the project's failure-mode taxonomy: bootstrap-ratio amplification of noise-floor numerator/denominator producing apparent large signatures.
**Posture:** Crazy-expert's PHASE_720 v2 follow-up. After C2053 established cross-corpus pattern (Codicillus + Voynich period-2, Rupescissa + Theophilus monotonic) admits a register-tracking interpretation (compact-formulaic-recipe Latin vs discursive Latin), but expert-advisor declined to register interpretation due to N=4 + post-hoc fit risk. This phase tests the register-tracking hypothesis at INTRA-CORPUS resolution.

---

## The actual question

Rupescissa is mixed-register text: contains both procedural recipe passages and theoretical/philosophical passages about quintessence. If the register-tracking interpretation is correct, recipe-dense passages within Rupescissa should show period-2 (negative r21, like Codicillus), and theory-dense passages should show monotonic (positive r21, matching overall Rupescissa +0.226).

If we observe this within-corpus pattern, register-tracking is confirmed at intra-corpus resolution — Rupescissa's overall +0.226 is the average of two distinct registers, not a single-corpus property.

If both registers show the same sign within Rupescissa, register-tracking fails and the C2053 cross-corpus pattern tracks something other than register (e.g., author, century, Latin variety).

---

## Methodology (LOCKED)

### Step 1: Load and segment Rupescissa
Per PHASE_720 v2 calibrated methodology: 15-80 word paragraphs after skip_lines=200.

### Step 2: Score each paragraph for register
**Recipe register markers** (Latin imperatives, measurement units, procedural sequence):
- Imperative verbs: `recipe`, `accipe`, `sume`, `da`, `mitte`, `pone`, `misce`, `tere`, `agita`, `coque`, `decoque`, `distilla`, `sublima`, `calcina`, `pone`, `serva`
- Measurement units: `uncia`, `libra`, `drachma`, `pondus`, `unc`, `lb`, `dr`
- Procedural sequence: `tunc`, `deinde`, `postea`, `donec`, `usquequo`
- Process verbs: `fiat`, `solvitur`, `coquitur`, `distillatur`, `subjugare`, `ablutio`

**Theory register markers** (abstract concepts, logical connectives):
- Abstract concepts: `natura`, `essentia`, `virtus`, `qualitas`, `substantia`, `materia`, `forma`, `principium`, `fundamentum`, `philosoph`, `secretum`, `mysterium`
- Logical connectives: `ergo`, `igitur`, `scilicet`, `sicut`, `quia`, `quoniam`, `propterea`, `nam`

### Step 3: Compute register-score per paragraph
`score = (n_recipe_markers - n_theory_markers) / n_words`

Positive score → recipe-dense; negative → theory-dense.

### Step 4: Stratify
Split paragraphs into:
- **Top quartile** (most recipe-dense): expected to show period-2 if register-tracking holds
- **Bottom quartile** (most theory-dense): expected to show monotonic
- **Middle 50%**: mixed-register control

### Step 5: Compute C2032 r21 for each stratum
Apply PHASE_720 v2 calibrated stem-class methodology to each subset of paragraphs separately.

### Step 6: Control comparisons
- **Random-quartile split control:** randomly assign paragraphs to two halves, compute r21 for each. Should give similar values (~+0.226 like overall Rupescissa) if register split is meaningful.
- **Length-quartile split control:** split by paragraph length instead of register score. Should NOT reproduce the register split's pattern if length isn't the confound.

---

## Pre-registered predictions (LOCKED)

| Outcome | Verdict |
|---|---|
| Recipe-dense r21 < -0.10 AND Theory-dense r21 > +0.10 (clean sign-reversal split) | **REGISTER-TRACKING CONFIRMED** — Rupescissa's +0.226 is bimodal average of two registers |
| Recipe-dense and Theory-dense both same sign (both negative OR both positive) | **REGISTER HYPOTHESIS FAILS** — within-corpus split doesn't reproduce cross-corpus pattern |
| Random-quartile control shows similar split to register-stratified split | **CONFOUND** — any split would show difference (small-N artifact) |
| Length-quartile reproduces the register pattern | **LENGTH CONFOUND** — register effect is just length effect |

---

## Why this matters

If register-tracking confirmed at intra-corpus level:
- The C2053 cross-corpus pattern (Codicillus+Voynich period-2 vs Rupescissa+Theophilus monotonic) is INTERPRETED as register-tracking, not domain-tracking
- Voynich aligns with compact-formulaic-recipe register specifically
- The Voynich-vs-Codicillus 3× magnitude gap (-0.66 vs -0.229) is the engineered-substrate-on-top-of-recipe-register signature
- Register-tracking interpretation moves from Tier 3-4 SPECULATIVE to Tier 2 measurement

If register-tracking fails:
- Cross-corpus pattern tracks something else (author, century, edition style, ...)
- Voynich's period-2 signature interpretation remains open
- C2053 stands as the measurement-only finding

---

## Implementation

| Script | Purpose |
|---|---|
| `_rupescissa_register_stratification.py` | Load Rupescissa, score paragraphs, stratify, compute r21 per stratum + controls |

---

## Effort

~2-3 hours implementation, ~5 min runtime (200-perm shuffles on smaller subsets).

---

## Registration-trap audit

- Pre-registered binary criteria locked before any data inspection
- Random-quartile and length-quartile controls explicitly required
- Methodology reuses calibrated PHASE_720 v2 pipeline (verified to reproduce canonical Codicillus -0.22)
- N per quartile will be ~70 paragraphs (Rupescissa total 279 → quartiles 70 each) — sufficient for stable r21 if effects are real
- Both outcomes (confirm, fail) are informative; the controls discriminate confound from signal
- Per `feedback_framework_as_null.md`: the register-tracking interpretation already fits framework cleanly; needs intra-corpus test to validate (not just N=4 cross-corpus pattern)

---

## RESULTS (2026-05-20)

### Stratified r21 by register score

| Stratum | n_paras | lag1 | lag2 | r21 |
|---|---:|---:|---:|---:|
| Recipe-dense (top quartile) | 69 | -0.00162 | +0.00233 | **-1.440** |
| Middle 50% (mixed) | 138 | -0.00468 | -0.00254 | +0.542 |
| Theory-dense (bottom quartile) | 72 | -0.00297 | -0.00136 | +0.457 |
| Codicillus reference | 148 | -0.01013 | +0.00232 | -0.229 |
| Voynich Section B | — | — | — | -0.66 |

**Pre-registered verdict per script:** REGISTER-TRACKING CONFIRMED ✓ (nominal pass: recipe-dense < -0.10, theory-dense > +0.10, register_diff 1.897 > 1.5× both controls).

**Crazy-expert's directional prediction CONFIRMED** in direction (recipe→period-2, theory→monotonic) — sign pattern matches register-tracking hypothesis.

### Controls flagged the noise-floor problem

**Control 1: Random quartile split (3 seeds):**
- Seed 0: top=+0.376, bottom=**-0.658**, diff=1.034
- Seed 1: top=+0.455, bottom=+0.334, diff=0.121
- Seed 2: top=+0.319, bottom=+0.581, diff=0.262

**LOAD-BEARING FAILURE:** Seed 0 random subset produced r21=-0.658 — Voynich's magnitude — purely by chance. If random N=70 chunks of Rupescissa can hit -0.658, the r21 metric at this N has no discriminating power.

**Control 2: Length quartile split:**
- Longest paragraphs: r21=-0.143
- Shortest paragraphs: r21=+0.549
- Difference: 0.692

Length confound substantial. Long paragraphs alone trend toward period-2.

### Noise-floor diagnostic

- Recipe-dense lag1 = -0.00162 (6× smaller than Codicillus canonical -0.01013)
- All Rupescissa subsets have lag1 in -0.001 to -0.005 range
- Codicillus canonical (calibrated PHASE_720 v2) has lag1 = -0.01013 — well above noise floor
- The r21=-1.44 for recipe-dense is a division-by-near-zero ratio artifact
- Voynich Section B canonical r21=-0.66 came from lag1≈-0.03 to -0.04 — well above noise floor

**At this N, r21 magnitudes are noise-floor amplified.** The metric requires lag1 > ~|0.005| to be interpretable as a true period-2 signature.

### Expert convergence

**Expert-advisor:** "Disqualifying on its own. If a random selection of ~70 Rupescissa paragraphs can produce Voynich-magnitude signature by chance, the metric has no discriminating power at this N. ... **Candidate 7th pattern in failure-mode taxonomy: bootstrap-ratio amplification of noise-floor numerator/denominator producing apparent large signatures.**"

**Crazy-expert (acknowledging his own prediction direction worked, magnitude failed silently):** "Direction-only passes are 1-bit evidence. Four control failures wipe that out. ... The framework now has enough operational vocabulary that ANY new stratification can be told as a clean operational story with surface-passing statistics. ... `feedback_mechanism_cycle_procedural_ceiling.md` pattern reaching saturation in a single session."

### Why this is INDEX-only, not registered

The pre-registered criteria nominally pass but they're inadequate for noise-floor magnitudes. The script's binary thresholds (register_diff > 1.5× control_diff) pass numerically but the underlying lag1 magnitudes are too small to support stable r21 interpretation. Registering a Tier 2 measurement here would inflate the constraint registry with non-informative measurement per `feedback_made_up_threshold_audit.md` and `feedback_bootstrap_ratio_at_noise_floor.md` (NEW).

### Strategic implication (cumulative)

Six interpretive findings this session passed nominal pre-reg but failed proper scrutiny:
1. PHASE_711 parametric atom-slot semantics (mechanism inference from MI measurement)
2. PHASE_716 line-spanning C1212 chaining (boundary tokens add noise not signal)
3. PHASE_716 mode coherence (within-mode pairs not larger than cross-mode)
4. PHASE_718 alchemy-specificity (matcher generic, NOT alchemy-discriminating)
5. PHASE_720 v1 calibration gap (length filter parameter drift)
6. PHASE_722 noise-floor (random subset produces Voynich-magnitude by chance)

Per crazy-expert: "the framework now has enough operational vocabulary that ANY new stratification can be told as a clean operational story with surface-passing statistics." The discrimination cycle is producing nominal passes faster than they can survive controls.

### New memory note created

`feedback_bootstrap_ratio_at_noise_floor.md` documents this as 7th distinct failure pattern in taxonomy.

### What's queued

Per expert convergence, three viable paths forward:
- **(a)** Aggregate larger recipe-dense corpora (Mercuriorum + Practica chapters across Rupescissa + Codicillus + Brunschwig) to escape lag1 noise floor; r21 stratification has statistical room with N≥300+ paragraphs per stratum
- **(b)** Abandon r21 ratio for intra-corpus work; use lag1 directly or peak-specificity methodology per `feedback_peak_specificity_for_periods_geq_7.md`
- **(c)** External grounding (physical reconstruction or independent attribution)

Crazy-expert's read: (b) for next text-statistical attempt, (c) for honest progress past procedural ceiling.

### Constraint actions

- NO new constraint registered (C2054 number remains available)
- Phase count increments (PHASE_722 INDEX exists)
- Constraint count unchanged at 2045
- Memory note `feedback_bootstrap_ratio_at_noise_floor.md` added
