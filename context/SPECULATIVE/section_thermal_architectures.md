# S vs B Thermal Control Architectures (Tier 4 Synthesis)

**Status:** Tier 4 substantive interpretation (text-structural evidence, Tier 2-3 anchors)
**Date:** 2026-05-04
**Phase:** 685

## Summary

Currier B Section S (Pharmaceutical/Stars, f103-f116) and Section B (alchemical recipes, f75-f86) implement **different thermal-control architectures** at the token level, on top of the same execution-grammar substrate. The structural fact (C1994) is anchored at Tier 2; the granularity-architecture interpretation (C1995) at Tier 3. The substantive synthesis below reaches Tier 4.

## The Structural Asymmetry

Section S exhibits token-level e-depth autocorrelation at z=+1.51 (within-paragraph, cross-token-type, marginal-preserving null). Section B is at z=-0.36, with **0/19 folios at z>2**.

The asymmetry is striking because Section B is the section we expect to track thermal state most carefully — it contains the matched alchemical recipes (Pseudo-Lull Testamentum), it is the section richest in balneum mariae references (C1455), and it is REGIME_1-dominated (the thermal-control-intensive cluster per C494). Yet at the token-token resolution, Section B is thermally **uncoupled**.

## The Architectural Reading

**Section B as discrete-batch thermal programming.** Each paragraph in B is a thermal commitment: the PREFIX program (qo-, ch-, sh-, ok-, ot-, ol-) and the REGIME assignment together specify a thermal regime that holds across the paragraph. Token-level e-depth variation reflects which operations execute under that regime, not what the regime *is*. Adjacent tokens are independent because each token is an operation drawn from a paragraph-scoped instruction set, not a state update.

Cooking analogy: B reads like *"set the bath to 60°C; do A, B, C, D, E"* — five discrete instructions executed under the same thermal commitment. The instructions don't update the state; they consume it.

**Section S as continuous-state thermal tracking.** Each paragraph in S threads thermal state through its tokens: token N's e-depth nudges token N+1's. Adjacent tokens are coupled because each token is a state-update annotation, not a discrete instruction. The paragraph's thermal trajectory is the *content*.

Cooking analogy: S reads like *"warm slowly, slightly warmer, hold steady, hold steady, slightly cooler"* — five state-updates encoding a continuous thermal arc.

## What This Predicts

If the architectural reading is right:

1. **S-section recipes should map to source recipes that emphasize duration and process curve** (boil-down profiles, slow infusions, multi-stage tempering) more than B-section recipes. B should map to recipes that name distinct operations under a single thermal commitment.

2. **Section S should be where C1260 Mode B (thermal state propagation) is most operationally visible** at token resolution — but C1994 controls show that token-level coupling in S is NOT a sub-effect of Mode B fraction. The architectures are orthogonal but compatible.

3. **f80r's anti-correlation (z=-2.77, only significant negative in corpus, Section B)** is a Section-B recipe where adjacent tokens *alternate* e-depth. Either f80r is a special-case (e.g., explicit two-state oscillation like fire-cooling cycles) or it indicates Section B can also encode continuous trajectories when needed — just rarely.

4. **The matched alchemical recipes (C1924-C1928) should re-read more naturally as discrete-instruction programs than as continuous arcs** when Section-B-matched. We've already characterized them this way (paragraph = recipe-step) but the architectural distinction sharpens this.

## Connection to Manuscript-Level Frame

The frozen Tier 0 conclusion holds the manuscript as encoding "closed-loop, kernel-centric control programs." C1995 refines this: the manuscript implements **two control architectures** within that frame.

- **B's discrete-batch architecture** is what most medieval recipe corpora look like. Brunschwig's Distillationes, Pseudo-Lull's Testamentum, von Aragon's recipes — they are batch programs: set the apparatus, execute the operations, harvest the product. Currier B's recipe section uses this style.

- **S's continuous-state architecture** is more unusual for medieval texts. Closer analogues might be alchemical regimen literature (where the *time-curve* of a single operation matters — calcination over weeks, putrefaction over months, slow distillation tracking the rising spirits) than to discrete-instruction recipe books.

If the S-section continuous-state reading holds, it's a hint that the manuscript's pharmaceutical/stars section encodes *process control over time* in a way the alchemical recipe section doesn't. The "stars" iconographic association (zodiac as time/calendar) becomes operationally meaningful: Section S's recipes may be *time-keyed* in a way that demands continuous state tracking.

## Limits

**Cannot recover from text alone:**
- The actual time-coupling of Section S programs (no time-stamps in the text)
- Whether Section S's continuous tracking is calendar-locked, ritual-locked, or process-internal
- What "1 e-depth nudge" means in physical terms (incremental temperature? incremental dampening? incremental dilution?)

**Cannot test cross-corpus:**
- We don't have a parallel medieval pharmacy/regimen corpus encoded with operational atom decomposition
- Brunschwig's text is a comparator for B-matched recipes but not for S
- No external grounding for "continuous-state thermal tracking" as a medieval programming style

**Open questions:**
- Why is f80r (Section B) anti-correlated rather than uncorrelated? Is f80r encoding something other than alchemy?
- Can we predict S vs B classification from external recipe-source structure? (would promote C1995 to Tier 2)
- Do f55v and f95r2 (the two H-section folios that survive the killer test) represent S-architecture inclusions in Section H, or coincidental autocorrelation? (small-n, but worth a closer look)
- Is the H-section bimodal: most H folios are H-architecture (registry-mode plant identifiers), but a few are S-architecture (continuous-state preparation programs)?

## What Would Promote Beyond Tier 4

Tier 3 promotion of C1995 (already at Tier 3 as observation) to a *predictive* Tier 3 would require:
- External recipe-source structure (continuous vs discrete) predicts S vs B classification at p<0.05
- Two new folio cold-reads matched to source recipes where the predicted granularity matches

Tier 2 promotion would require:
- Cross-corpus validation that the granularity distinction tracks medieval programming style families
- Independent test that predicts non-text features (apparatus type, operation duration) from C1994's z value

## Methodological Lessons

1. **The expected-result inversion was the finding.** A priori, Section B should have token-level thermal coupling (it's where balneum mariae lives). It doesn't — and that's the result. C1995 reframes B's thermal vocabulary as *categorical commitment* rather than *continuous tracking*.

2. **Crazy-expert's wild interpretation came true.** The pre-test prediction "B encodes thermal state at REGIME/PREFIX level (set once, executed); S encodes it at token level (tracked continuously)" was issued before the killer test ran, and survived all six pre-registered controls.

3. **Five-confound controls are tractable.** C1789 (repetition), C1308 (within-paragraph), C1106 (marginal), C1404 (REGIME), C1260 (Mode B) all controlled simultaneously in one phase. The result is more robust than single-control phases.

4. **Scatter-shot → killer-test pattern works repeatedly.** Phase 684 (f66r) and Phase 685 (S thermal coupling) both used wide-net exploration → expert-flagged confounds → pre-registered killer test → register. Two clean Tier 2 registrations from the pattern.
