# S vs B Operational Structure (Tier 4 Synthesis — REVISED)

**Status:** Tier 4 substantive interpretation (Tier 2-3 anchors), revised after three-tier control test
**Date:** 2026-05-04 (revised)
**Phase:** 685

## Revision Note

Original synthesis (drafted 2026-05-04, revised same day) proposed S as "continuous-state thermal tracking" vs B as "discrete-batch thermal programming." User pushback: no medieval source corpus (Brunschwig, Pseudo-Lull, Pseudo-Geber, Mesue, Antidotarium Nicolai) has token-by-token thermal description — all are stage-bound. The continuous-state reading required the Voynich to do something no source has been shown to do.

**Three-tier autocorrelation control test** (s4_three_tier_test.py) confirmed the user's pushback. Tier C (cross-PREFIX, genuinely operationally distinct pairs) collapses in Section S to z=-0.01. The original z=+1.51 aggregate finding was driven by Tier A near-relatives (qokedy → qokeedy etc.), not by genuine state-coupling across distinct operations.

Continuous-state interpretation **rejected**.

## What the Decomposition Actually Shows

Three-tier breakdown of C1994's S-vs-B autocorrelation:

| Tier | Description | S mean z | B mean z |
|------|-------------|----------|----------|
| A | Near-relatives (Lev≤1 OR same MIDDLE) | +5.43 | +4.53 |
| B | Same-PREFIX, different MIDDLE | +0.79 | +0.36 |
| C | Cross-PREFIX (operationally distinct) | -0.01 | -1.47 |

Two genuine findings emerge from the decomposition:

### Finding 1: Section S is operationally compact

S folios have **more near-relative pairs in proportion** (3.0% of pairs vs 2.0% in B). When tokens cluster as morphological neighbors (qokedy → qokeedy → qokeey, same stem with MOD-count variation), they cluster densely within paragraphs. This is consistent with **pharmacy-index or short-recipe-list format**: dense same-stem runs reflect listing variants of one operation rather than progressing through different operations.

### Finding 2: Section B exhibits operational alternation

B's Tier C is anti-correlated (z=-1.47, p=0.0001 vs S's null). Cross-PREFIX adjacent pairs in B systematically have **opposing e-depth values** — when a high-e operation is followed by a different-PREFIX operation, the next operation tends to be low-e, and vice versa.

This is consistent with **multi-step alchemical procedures with thermal cycling**: balneum-warm step → cool extraction step → warm distillation → cool collection. Each step uses a different PREFIX class, and adjacent steps deliberately *alternate* thermal regimes.

f80r (z=-2.77 in original killer test) is the most extreme case — a Section B folio where adjacent operations alternate aggressively. Not anomalous, just an extreme exemplar of B's general pattern.

## What This Means in Plain Terms

**Cooking analogy (revised):**

- **Section S** reads like *"infusion of X. infusion of X with Y. infusion of X with Z. decoction of X. decoction of X with Y..."* — a list of variants on a few base operations. The morphological clustering reflects "same operation, different ingredient/dose."

- **Section B** reads like *"warm in bath. cool. distill. collect. heat strongly. cool. add..."* — a sequence of operations that alternate thermal regimes. The cross-PREFIX anti-correlation reflects deliberate cycling between heat states across operation types.

## Relationship to Source Corpora

This revised reading aligns naturally with what we'd expect:

- **Section B** matches the multi-step alchemical recipes of Pseudo-Lull's *Testamentum* (already validated, C1924-C1928). Multi-step alchemical procedures with explicit thermal-regime cycling.
- **Section S** would match medieval pharmacy-index literature: *Antidotarium Nicolai*, *Mesue's Grabadin*, simple-collections, herbal-preparation lists. Many short entries, each a variant of base operations, rather than long multi-step procedures.

Crucially, **neither section requires the Voynich to do something no source corpus does.** Both readings are realizable in known medieval programming styles.

## What Falls Through the Cracks

The "continuous thermal trajectory" reading was attractive because it gave Section S a distinctive *operational identity*. The revised reading is more conservative — S is "dense pharmacy-list" — but this is closer to what medieval pharmacy texts actually look like, and doesn't require a unique-to-Voynich encoding scheme.

What we DO lose:
- The poetic alignment with C1768-C1771 (Stars monitoring axis as operational philosophy) — the revised reading doesn't directly extend this.
- The mapping of Section S to "closed-loop continuous-state programming" — a sharper architectural claim that would have differentiated medieval pharmacy from medieval alchemy.

What we GAIN:
- A simpler interpretation that survives parsimony.
- A new finding (B's cross-PREFIX anti-correlation, Finding 2) that wasn't visible at aggregate level.
- Discoverable historical match candidates for S (pharmacy-index literature).

## Open Questions

1. **Can we predict S vs B classification from external recipe-source structure?** Pharmacy-index sources should match S folios; multi-step alchemy sources should match B folios.
2. **Is f80r (z=-2.77, most-anti-correlated B folio) a genuinely distinct sub-procedure within B?** Or just an extreme tail of the alternation pattern?
3. **Does B's cross-PREFIX anti-correlation predict specific operation-pair structures?** E.g., do qok-PREFIX tokens systematically follow ch-PREFIX tokens with opposing e-counts?
4. **The H folios that survived the killer test (f55v, f95r2, f43v, f66v) — do they share the S compactness pattern, or are they H-specific?** Small-n cases worth checking.

## Methodological Lessons (revised)

1. **Pre-registered controls don't catch all confounds.** The killer test had 5 confounds controlled but missed near-relative-clustering — caught only by user pushback and post-hoc decomposition.

2. **Source-corpus absence is a real epistemic constraint.** Interpretations that require the Voynich to do something no source has been shown to do bear an extraordinary-claim burden. The user's instinct (sources are stage-bound, so the continuous-state reading overreaches) was decisive.

3. **The aggregate finding can hide multiple sub-findings.** C1994's z=+1.51 vs -0.36 was a real difference, but it decomposed into two distinct phenomena (S compactness + B alternation), neither matching the original interpretation.

4. **Demoting an interpretation is not retracting the structural fact.** C1994 remains Tier 2. C1995 was revised, not retracted. The data didn't lie; the reading did.

5. **Crazy-expert's three-tier test design was the cleanest possible discriminator.** Tier C (cross-PREFIX) avoided circularity by definition — pairs that share neither stem nor PREFIX are operationally distinct, so any signal there can't be explained by stem-locality.
