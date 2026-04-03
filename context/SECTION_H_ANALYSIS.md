# Section H Analysis: Herbal Folio Process Classification

**Status:** EXPLORATORY (Tier 4) | **Date:** 2026-04-02
**Method:** Dark pipeline clustering + bridge MIDDLE comparison + Brunschwig recipe type matching

---

## Summary

Section H contains 32 Currier B folios with plant illustrations. They cluster into three process types by dark pipeline profile, but individual recipe identification requires the plant illustrations — the text encodes PROCESS TYPE and OPERATIONAL PARAMETERS, the illustration encodes MATERIAL IDENTITY.

---

## Three Process Types

### Type 1: Simple Distillation (22 folios, 69%)

**Folios:** f26r, f26v, f31v, f33r, f33v, f34r, f34v, f39v, f40r, f41r, f41v, f46r, f48r, f48v, f50v, f55r, f55v, f94r, f94v, f95r1, f95r2, f95v1

**Dark pipeline:** No material/process markers (no fch, no cs, no eckh, no rai, no tsh, no ro). Dark tokens present but only universal equipment identifiers (lch, lk) or folio-specific unknowns.

**Operational profile:** Default herbal — moderate qo (9.4%), moderate ch (16.7%), standard gentle heat (7.5%). Each folio IS operationally distinct (different PREFIX distributions, paragraph structures, thermal profiles) but they lack MATERIAL IDENTIFIER vocabulary because each processes a single plant material identified by the illustration.

**Brunschwig correspondence:** Simple degree-2 ash distillation from the Small Book. "Take the herb, chop, distill." The Small Book's 2-3 step entries per plant. Cannot be individually matched because the recipes are too operationally thin.

**Why they can't be matched individually:** The text encodes HOW to distill — which fire degree, how many passes, what to monitor. But the HOW is similar across all simple plant distillations. The differentiating content is WHICH PLANT — and that's in the illustration, not the text. This is consistent with C138 (illustrations don't constrain text) — the text and illustration are COMPLEMENTARY, not redundant.

### Type 2: Alcohol Compound (4 folios, 12.5%)

**Folios:** f39r, f40v, f50r, f66v

**Dark pipeline:** fch (mercury/alcohol solvent) present on all 4. No eckh, no rai, no cs.

**Operational profile:** Distinct from simple distillation — higher dar per folio (2.2 vs 1.2), higher dal (1.5 vs 0.5), higher da (8.2% vs 6.2%), enriched kch (precision heat, 2.85x), depleted m (closure, 0.22x) and or (portioning, 0.41x). These folios encode compound preparations where herbs are dissolved in aqua vitae (vegetable Mercury / alcohol) before distillation.

**Brunschwig correspondence:** Compound aqua vitae recipes from the Large Book Chapter XXVI. 16 distinct recipes identified, varying across 5 operational dimensions (complexity, heat regime, cohobation, digestion method, post-distillation enrichment).

**Matching limitation:** The 4 folios cannot be matched to SPECIFIC Brunschwig compound recipes because the simple compound recipes (R4, R5, R14, R15) have nearly identical operational profiles. The distinguishing factor is which herbs/spices are used — which requires knowing the plant material, not the procedure.

**Note:** f39r is already matched to Ch7-10M (pearl-making) and f66v to Ch26P (inceration) — these are PL matches, not Brunschwig. The fch on these folios indicates mercury/alcohol is used as part of the procedure, consistent with the PL recipes which DO use mercury preparations.

### Type 3: Full Compound (1 folio, 3%)

**Folio:** f31r

**Dark pipeline:** fch (mercury/alcohol) + eckh (volatile liquid) + rai (metallic). Three material markers = the most complex preparation in Section H.

**Operational profile:** Dramatically different from both other types — gentle heat 15% (vs 5.8% compound, 7.5% simple), eol (sustain) at 7x the normal rate, qo=18% (highest of all three types). Balneum-dominant with extended sustaining operations.

**Brunschwig correspondence:** Identified as rosewater candidate via structural profile scoring. Brunschwig's rosewater recipe has extensive operational detail (cohobation, 5 quality tests, rectification, sun exposure 40 days, 3-year shelf life). The three material markers match: alcohol solvent (fch), volatile plant extract (eckh), and metallic component (rai — Brunschwig adds gold leaf to premium rose preparations, and silver testing equipment is described).

---

## The Text-Illustration Complementarity Model

Section H demonstrates that the Voynich manuscript uses a two-channel information system:

| Channel | Encodes | Examples |
|---------|---------|---------|
| **Text** (Currier B tokens) | Process type, fire degree, monitoring protocol, iteration count, apparatus management | Simple vs compound, degree 1/2/3, cohobation vs single-pass |
| **Illustration** (plant drawing) | Material identity — which plant is being processed | Rose, sage, rosemary, chamomile, etc. |

Neither channel alone is sufficient for a complete recipe. The text says HOW. The illustration says WHAT. Together they form a complete instruction: "distill THIS PLANT using THIS PROCESS."

This is consistent with:
- **C138:** Illustrations don't constrain text (swap invariance). The same process could apply to any plant.
- **C171:** Semantic ceiling. The text encodes operational behavior, not material names.
- **C120:** PURE_OPERATIONAL. Material identity is externalized to the practitioner's knowledge — or in this case, to the illustration.

The Mercuriorum folios (Section B) DON'T need illustrations because they combine MULTIPLE materials that need to be DISTINGUISHED within the text — hence dark pipeline material identifiers (fch, cs, eckh). Section H folios process SINGLE plants — no disambiguation needed because the illustration already identifies the material.

---

## Open Questions

1. Can the 22 simple-distillation folios be grouped further by REGIME or fire degree (R1 vs R2 vs R4)?
2. Do the 4 alcohol-compound folios' bridge MIDDLE enrichments (kch 2.85x, eek 4.99x) correspond to specific Brunschwig compound preparation techniques?
3. Can plant illustrations be matched to Brunschwig's herbal entries to complete the recipe identification?
4. Does the text-illustration complementarity model predict which folios SHOULD have illustrations and which shouldn't? (Section B and S folios mostly lack plant illustrations — correctly predicted by the model since they don't encode single-plant recipes.)

---

*This document is Tier 4 exploratory work. The three-type classification is derived from dark pipeline analysis (Phase 637, C1941) and bridge MIDDLE comparison. For the dark pipeline dictionary, see [DARK_PIPELINE_DICTIONARY.md](DARK_PIPELINE_DICTIONARY.md).*
