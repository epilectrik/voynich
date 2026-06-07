# Dark Pipeline = Intermediate-State Naming? (PRE-REGISTRATION)

**Status:** LOCKED before running. 2026-06-05.
**Class:** exploratory hypothesis-generation → at most a Tier-3 candidate. Echo-class if it
proposes a referent; needs external grounding for any promotion.
**Origin:** a POST-HOC pattern from the negative-audit dark-pipeline re-tests (`SYSTEM/NEGATIVE_AUDIT.md`
Disposition 4). This is a **noticing, not a result.** The operational-story-first trap applies hard.

---

## The hypothesis

The dark pipeline (C1135–C1141: a folio/section-local identification/nominalization layer) does
NOT name **input materials** (tested-and-failed, Disposition 4: cross-folio Mantel null + folio
material→dark negative). The alternative: it names **intermediate states / products of a
transformation** — each transformation step coins a name for the new state of the substance.

**Generating observation (the circularity source):** dark-MIDDLE count is high in *single-substance
iterative* procedures (ferment multiplication f103r=35, mercury coagulation f107r=33, f112r=30) and
low in multi-material recipes (lunaria preps, element separations). I.e. dark proliferates where one
substance cycles through many transformations.

## The primary threat (name it up front)

**Dark-MIDDLE count is dominated by folio length (Spearman +0.665).** The "iterative" folios
(f103r ntok=522, f107r=488, f112r=394) are also among the *longer* folios. So the entire generating
observation may be **nothing but the length confound** — iterative recipes happen to match longer
folios, and long folios have more dark MIDDLEs of every kind. **The test is worthless unless the
transformation signal survives folio-length control.** This is the most likely way it dies.

## Predictor (defined independently, BEFORE re-touching dark counts)

`transformation_count` per recipe = number of explicit **repetition / cycling / state-change**
instructions in the matched SISMEL recipe (Latin+Catalan), counted from a LOCKED lexicon:
- explicit iteration: `reitera*`, `vegad*`/`vice*`/`vicib*` with or without a numeral, `toties`,
  `iterum`, `de novo`, numeral+operation
- state-transition cycling: distinct *sequential* operation-pairs where a product re-enters
  (sublimation→fixation→re-sublimation; solution↔congelation cycles; "super … reduc" loops)

This is DISTINCT from `operation_count` (distinct operation TYPES, already tested → dark null) and
from `material_count` (distinct material TYPES, already tested → dark negative). The claim is that
*cycling/iteration*, not operation-variety or material-variety, drives the dark layer.

## Test

Response = folio `dark_count` (distinct dark MIDDLEs). N=16 matched folios.

1. **PRIMARY:** partial Spearman(`transformation_count`, `dark_count` | folio `n_tokens`).
2. **DISCRIMINATOR (floor-vs-discriminator):** it must BEAT both already-tested predictors —
   transformation→dark | len  >  operation→dark | len (≈0) and  >  material→dark | len (≈ −0.3).
3. **SPECIFICITY CONTROL:** transformation→**core** | len should be ≈ 0 (cycling inflates the
   *identification* layer, not the grammar layer).
4. **CIRCULARITY GUARD (mandatory):** re-run PRIMARY with the three generating folios
   (f103r, f107r, f112r) REMOVED. If the effect vanishes without them, it was the post-hoc anecdote,
   not a real regularity → KILL.

## Pre-registered kill conditions (ALL must pass to survive)

- **K1 — length-confound:** transformation→dark | n_tokens < **+0.30** OR not significant → KILL
  (dark is length-driven, not transformation-driven). *Expected failure mode.*
- **K2 — non-discriminating:** transformation→dark does not exceed operation→dark by ≥ 0.25 → KILL
  (not specific to cycling; it's generic recipe complexity).
- **K3 — circular:** effect disappears when the 3 generating folios are removed → KILL (anecdote).
- **K4 — multiplicity:** with ≤ ~5 correlations on N=16, require the surviving p to clear a
  Bonferroni/holm correction, not a raw p<0.05.

## Ceiling / what a survival licenses

- Best outcome = a **Tier-3 candidate**: "dark-layer size tracks transformation-cycling beyond
  length/operations/materials." It would NOT identify *what* the intermediate states are (C171),
  and it must be stated as a *structural measurement* (dark-size ↔ cycling), NOT as "dark MIDDLEs
  = state names" (that's the death-zone-grade operational claim, needs external grounding).
- Power is marginal (N=16, dark length-dominated). If the pre-gate (achievable partial-r resolution
  at N=16 after removing 3 folios → N=13) can't resolve +0.30, declare **UNDERPOWERED**, not null.

## Honest prior

Given the +0.665 length confound and N=16, the modal outcome is **K1 (length) or K3 (circular)**.
This is registered as the disciplined next step IF the dark pipeline's referent is pursued, not as
a promising lead. Run only if the dark-layer-function question is worth the spend.
