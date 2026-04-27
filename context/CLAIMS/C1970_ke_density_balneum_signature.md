# C1970: Token-Internal ke Density Tracks Dampened Thermal Regime on CONFIRMED-Tier Matches

**Tier:** 3
**Scope:** B, paragraph, ke/ek, balneum-mariae, indirect-heat, recipe-correspondence, match-tier, C1225, C1226, C1735, C1872, C1899
**Phase:** PHASE_664_CONFIRMED_TIER_STRATIFICATION
**Date:** 2026-04-26
**Refines:** C1226 (ke/ek = process-context conditioning) with external Catalan recipe-content alignment
**Pairs with:** C1225 (e-depth as gentle/stabilized heat), C1394 (HEAD+MOD+TERM atom model), C1899 (atom-decode validation on CONFIRMED matches)
**Distinct from:** C1969 (qok-density specificity for f75r ×9 anchor)

---

## Statement

On the 3 CONFIRMED-tier recipe-folio matches (f75r/III.19, f76r/II.18, f84r/II.14), where the matched Catalan source explicitly specifies balneum mariae or indirect-heat operations, paragraph-level ke pattern density (count of tokens containing 'ke' substring relative to count containing 'ek') is elevated approximately **2× above both supported-tier matches and the corpus baseline**.

`ke` within a token decomposes as k(HEAD heat) + e(MOD thermal-intensity dampener) per the atom system (C1394, C1225). High `ke` density therefore indicates dampened/indirect thermal regime at folio resolution.

---

## Empirical evidence

### Primary test (pre-registered, Phase 664 T1)

| Group | n paragraphs | mean ke/ek |
|---|:---:|---:|
| CONFIRMED matches (f75r, f76r, f84r) | 12 | 9.74 |
| Supported-tier matches | 83 | 5.03 |

- Cohen's d = **+1.04** (large effect)
- One-sided permutation p = **0.0023**
- 10,000-permutation null

### Sanity check vs corpus baseline (Phase 664 T2)

| Group | n paragraphs | mean ke/ek |
|---|:---:|---:|
| CONFIRMED matches | 12 | 9.74 |
| Corpus-wide (all unmatched, ≥8 tokens) | 468 | 4.68 |

- Cohen's d = **+0.97**
- p = **0.0057**

CONFIRMED elevated above BOTH supported tier AND unselected baseline — disambiguates from "supported-tier below average" interpretation.

### Leave-one-folio-out safeguard

Each CONFIRMED folio dropped in turn:

| Drop | n | Cohen's d | p |
|---|:---:|---:|---:|
| Drop f75r | 9 | +0.92 | 0.0109 |
| Drop f76r | 8 | +1.21 | 0.0061 |
| Drop f84r | 7 | +1.09 | 0.0119 |

**All three splits maintain d ≥ 0.8.** Effect is not carried by any single folio. Min d across LOO = +0.92.

---

## Operational interpretation

The 3 CONFIRMED matches all use balneum mariae or indirect-heat operations in their matched Catalan recipes:

| Folio | Matched chapter | Catalan operation |
|---|---|---|
| f75r | III.19 (aqua vitae) | distillation `en bany` (in bath) — 9-cycle reflux |
| f84r | II.14 (gold dissolution) | `met al bany` (place in bath) — sustained warm bath + putrefaction |
| f76r | II.18 (element separation) | controlled-bath separation procedure |

Token-internal `ke` density on these folios is consistent with the recipes' explicit use of dampened/indirect heat. The phrasing here is **dampened/indirect thermal regime**, not "balneum mariae" specifically — a 3-folio sample cannot distinguish balneum from cognate gentle-heat operations (sand bath, ash bath, dung bath) on cs1225's e-depth axis.

---

## Methodological caveats (registered)

1. **Pre-registration motivation:** Phase 664 was motivated by Phase 663's pre-registered sensitivity check. Phase 664 PRE_REGISTRATION.md transparently disclosed this. The T2 corpus-wide control was specifically designed to mitigate the HARKing concern — it confirmed CONFIRMED elevation against an unselected baseline, not just against the cherry-picked supported-tier comparator.

2. **Selection-bias bound:** CONFIRMED-tier matches were selected by structural-decode quality. Selection criteria did not directly include ke/ek but did include thermal-monitoring features (8D feature set, atom-level decode validation per C1899). Some portion of the d=+1.04 effect may be attributable to selection-on-related-features. The LOO safeguard bounds the within-CONFIRMED concentration concern (no single folio carries the effect).

3. **Small-N inference scope:** 12 paragraphs across 3 folios. Statistical significance achieved (p < 0.01 on T1 and T2; LOO d ≥ 0.8 on all splits). The inference is robust within its scope but fundamentally about the 3 specific CONFIRMED matches, not the corpus broadly.

4. **Tier 3 rationale:** Statistical evidence is Tier 2 caliber. The interpretive routing through Catalan recipe content (`en bany`, `met al bany`) and the C1225 atom-glossing chain places the substantive claim at Tier 3 (interpretive layer). The pure structural claim — that the 3 CONFIRMED folios share a paragraph-level ke/ek elevation distinguishable from corpus baseline — is Tier 2 by itself but registered jointly here.

5. **HARKing-borderline disclosure:** The CONFIRMED-vs-supported partition was suggested by Phase 663's sensitivity check, not blind theory. Pre-registration locked methodology before run. Failure mode specified. T2 + LOO safeguards added. Both expert-advisor and crazy-expert (consultation, 2026-04-26) converged on Tier 3 registration with tight scoping — this constraint reflects that consensus.

---

## Related work

| ID | Relation |
|---|---|
| C1225 | e-depth suffix parametricity (gentle/stabilized heat marker — atom level) |
| C1226 | ke/ek = process-context conditioning (REGIME/section, structural) |
| C1394 | HEAD+MOD+TERM atom encoding (compositional substrate) |
| C1735 | Brunschwig fire-degree intensity tracks VMS structure within Stars |
| C1872 | k_ratio inversely tracks REGIME thermal intensity (k indexes management not delivery) |
| C1899 | 8/8 atom-prediction validation on f75r CONFIRMED match |
| C1928 | f75r → f84r product chain (vegetable G = quintessence) |
| C1959 | Paragraph layout-order tracks recipe-phase order |
| C1969 | Window-density qok-class specificity for f75r ×9 anchor |

C1226 said ke/ek is REGIME/section-conditioned (Tier 2 structural). This constraint adds the external recipe-content alignment: ke density specifically elevates on CONFIRMED matches with indirect-heat recipes. New, more specific claim.

---

## What this enables (NOT committed in this phase)

- Phase 665 candidate: corpus-wide screen ranking all 82 Currier B folios by `ke + ek` density. Top decile = candidate indirect-heat folios. Cross-check against C1872 R2 enrichment, Stars R1 high e-to-y (C1735), pending recipe-correspondence assignments. Pre-register before looking at rankings.

This is a note, not a commitment.

## What this does NOT claim

- No specific token has been translated. C171 semantic ceiling holds.
- No claim that all balneum operations produce ke/ek elevation — the test only validates direction in 3 known cases.
- No claim that ke density is sufficient for folio-recipe matching (single-feature alignment was tested in 8D framework and produced this folio's match strength only when combined with other features).
- No claim about supported-tier matches being "wrong" — they may simply be operationally heterogeneous (some use indirect heat, some use direct or non-thermal procedures).
