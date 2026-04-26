# C1962: 4-Axis O-Prefix Runtime Channel Taxonomy

**Tier:** 3 (within-sample fit; out-of-sample validation pending)
**Scope:** B, PREFIX, o-prefix, taxonomy, channels, recipe-correspondence
**Phase:** PHASE_648_VESSEL_4AXIS_RECIPE
**Date:** 2026-04-25
**Extends:** C1388 (o-atom arrangement domain marker, 100% category purity), C1316 (O-PREFIX categorical distinction), C1958 (ot transfer rate, broadened by this constraint)
**Relates to:** C874 (ol = continue), C1304 (ok/ot category divergence position-independent), C539 (or LATE morphological class), C1961 (paragraph-level fire/vessel partition)
**Refines:** C1388 (ol gloss sharpened), C1958 (ot broadened from drip-rate to general transfer/iteration)

---

## Statement

The four o-prefixes encode four distinct physical-channel readings within the vessel-side block of C1961:

| Prefix | Refined gloss |
|---|---|
| `ol` | Vessel-content state monitoring — what is in which vessel, with what identity, in what configuration |
| `ot` | Material transfer / addition / iteration cycles — drip-rate (C1958) is the f83r-specific manifestation |
| `ok` | Thermal regime / fire-degree state on contents — what kind of fire produces what state |
| `or` | Outcome / completion state — line-final closure marker (per C539 LATE class) |

Glosses derived from reading SISMEL Catalan recipe text for the 16 matched folios. Each prefix's dominant folios cluster on recipes with a coherent physical-emphasis signature.

---

## Empirical evidence

### Within-sample text-grounded predictions (Phase 648, Step 4)

| Predictor | Top-1 accuracy | Top-2 strict | Random baseline |
|---|---|---|---|
| Label-based (Round 1) | 6/16 = 37.5% | — | 25% |
| **Text-grounded (Round 2)** | **16/16 = 100%** | **7/16 = 43.8%** | **17%** |

**Caveat:** definitions were derived from reading these same texts. The 100% top-1 fit is within-sample confirmation, not out-of-sample test. The top-2 strict accuracy (43.8% vs 17% random) is the more informative number — secondary predictions required additional judgment beyond the obvious dominant pattern.

### Recipe groupings (text-derived)

| Prefix | Matched folios where dominant | Recipe content signature |
|---|---|---|
| **ol** (8 folios) | f75r, f84r, f79r, f77v, f81v, f82v, f80r, f83r | Batch-keeping ("metràs a part"), apparatus arrangement, vessel-naming chapters, sealed-state, multi-vessel coordination |
| **ot** (6 folios) | f103r, f76v, f112r, f112v, f116r, f107r | Cohobation, chamber-to-chamber combination, addition, repeated cycles, color-cycle iteration |
| **ok** (2 folios) | f76r, f82r | Theoretical fire-regime chapters, calcination-driven preparation |
| **or** (0 folios) | — | No matched recipes; or enriches on herbal-B + small recipes-section folios |

### Position-resolution (Phase 648, Step 6)

All four o-prefixes are positionally uniform within paragraphs (early/base ratios 0.75–1.13×). This rules out an alternative reading where ol could have functioned as a setup-phase declaration (paragraph-initial). All four are runtime monitoring channels.

---

## Channel-by-channel detail

### ol = vessel-content state monitoring

Sharpens C1388 ("ol = arrange+state = STAGING/LINK") to specify the substantive content within the STAGING category. Preserves C1174 deflation: ol is a morphological component, not a functional LINK layer.

Evidence from Catalan text:
- f75r aqua vitae: explicit batch identity ("la primera aygua... la segona aygua... la terça aygua") kept separate, used differently
- f84r gold dissolution: apparatus arrangement (alembic on cucurbit, vessel in balneum)
- f80r vessels chapter: literal vessel-naming ("distillatori, dissolutori, putrefactori, calcinatori, congelatori, sublimatori")
- f83r G-liquefaction: sealed-state in ampoule with cera comuna for 2 days

### ot = material transfer / addition / iteration

Generalizes C1958 ("ot = transfer rate / drip rate monitoring") to the broader operational class. The f83r drip-counting case (L22 ot×3 at Catalan drop-counting positions, validated) is the literal-drip subset. C1958 itself notes ot encodes "control actions around drip monitoring, not numerical values" — the broadening is a valid generalization.

Evidence from Catalan text:
- f112r cohobation: explicit "distill in balneum 3 times. After each distillation, put the water onto the viscous earth..." — repeated transfer cycles
- f103r ferment multiplication: "the two chambers, mix into one for resolution of liquefaction"
- f76v ferment conversion: "convert it into liquefaction by ADDING H according to weight"
- f116r fixation: "reiterate the sublimation of the unfixed part onto the fixed thing"

### ok = thermal regime / fire-degree state on contents

Extends C1304 (ok/ot position-independent category divergence) and C1313 (q-modifier on o-base = THERMAL channel) to specify ok as the *vessel-side thermal monitor* (distinct from qo which is the fire-side heat-application driver).

Evidence from Catalan text:
- f82r lunaria maceration: theoretical fire-regime chapter — heavy "multiplicació del foch", "calor temprada", "calor naturall", "calor excellent", "lent foch"
- f76r element separation: calcination-driven preparation ("preparació de O e de L se fa a fi que ells recobren maior humiditat")

### or = outcome / completion state

**Tentative gloss** — `or` does not dominate any matched recipe, so this gloss has no recipe-text anchor. The reading is constrained by:
- C1388: or = arrange+respond = FLOW (100% category purity)
- C539: or is in the LATE morphological class (line-final, suffix-depleted)
- Distributional: or enriches only on herbal-B and small recipes-section folios (mean rate 2.14% vs 5–7% for other o-prefixes)

The "outcome/completion" reading is consistent with all three anchors but is interpretively underdetermined. Stronger candidate readings (e.g., crazy-expert's "emergent / non-operator-caused state" — fermentation, settling, color-emergence in herbal preparations) are plausible but lack independent structural support and are flagged as Tier 3-speculative future work.

---

## Refinement of C1958

**Refined 2026-04-25 (Phase 648):** ot's gloss is generalized from "transfer rate / drip rate monitoring" to "material transfer / addition / iteration cycles." The f83r drip-counting case (L22 ot×3 at Catalan drop-counting positions) is the f83r-specific manifestation of the broader transfer/iteration channel. C1958 itself notes ot encodes "control actions around drip monitoring, not numerical values" — the broadening is consistent with the original constraint's mechanism.

## Refinement of C1388

**Refined 2026-04-25 (Phase 648):** Within C1388's STAGING category, ol on matched recipes corresponds specifically to vessel-content-state operations (batch identity, vessel role, content configuration). Preserves C1174 deflation — ol is a morphological component carrying STAGING content, not a functional LINK substrate.

---

## Falsification

Would be falsified if:

1. Out-of-sample test on unmatched folios shows the predicted prefix-dominance fails to match recipe content reliably (e.g., a Brunschwig herbal distillation recipe with predicted-channel signature not matching the candidate folio)
2. MIDDLE-pool analysis reveals the four o-prefixes share MIDDLE distributions at fixed paragraph position (would indicate they are allomorphs, not distinct channels)
3. The C539 LATE positional class for `or` is shown to be incompatible with any plausible "outcome/completion" reading

---

## Pending validation

Three tests recommended by crazy-expert before pushing this constraint to Tier 2:

1. **Out-of-sample recipe match** — pick an unmatched ot-dominant or ol-dominant Currier B folio, predict recipe content from prefix profile, attempt match against PL Testamentum or Brunschwig
2. **MIDDLE-pool comparison** — compute MIDDLE distributions for ok/ot/ol/or at fixed paragraph position; test for distinctness
3. **Within-paragraph sequencing** — test whether the predicted control-loop topology (qo→ol→ok→ot→ch/sh→qo) appears at the line-bigram level

---

## Provenance

- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/scripts/s1_profile_o_prefixes.py`
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/scripts/s3_recipe_text_by_prefix_group.py`
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/scripts/s4_retest_refined_definitions.py`
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/scripts/s6_position_resolve_and_permute.py`
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/refined_test.json`
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/grouped_text.txt` (full SISMEL Catalan recipe text grouped by dominant o-prefix)
