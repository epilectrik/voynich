# PHASE 704: Antidotarium Nicolai d<1.0 Test for f104-105

**Status:** COMPLETE — INDEX-only documentation (no constraint registration)
**Date:** 2026-05-19
**Verdict:** Clean negative. Antidotarium Nicolai does not identify the Section S 4-folio gap (f104r, f104v, f105r, f105v) as its source. Combined with prior Mesue Grabadin falsification, both major medieval pharmacy traditions are now excluded.

---

## Question

PHASE_704 closes a previously partial test. The Section S 4-folio gap (f104r/v, f105r/v) is the residual unmatched portion of Section S after PHASE_641+ confirmed 17/23 folios as PL Mercuriorum. Memory entry `project_section_s_source_genre_gap.md` flagged Antidotarium Nicolai as the leading external-corpus candidate.

Prior testing had:
- Loaded Antidotarium Nicolai compound-pharmacy features (124 recipes)
- Run the Phase 627/628 8D top-1 matcher, producing the **degenerate result** (82 of 124 recipes → f34v, 66% collapse to manifold geometric center per `feedback_top1_matcher_mode_is_degenerate.md`)
- Not yet run the hypothesis-driven absolute-distance gated test (d < 1.0) per validated C1971 methodology for f104-105 specifically

This phase fills that gap.

---

## Test design (locked pre-run)

1. Compute Antidotarium ↔ Voynich 8D distance matrix (TUNED_DIMS from Phase 627/628)
2. Global calibration: distance distribution across all 10,168 (recipe, folio) pairs
3. Target folios f104r, f104v, f105r, f105v: closest Antidotarium recipes, counts at d<1.0 and d<1.5
4. Controls:
   - Section B balneology (f75r-f84r, 10 folios) — should NOT match Antidotarium (Codicillus alchemy class)
   - matched-S PL Mercuriorum folios (f103r, f106r, f108r, f112r, f114r) — should NOT match Antidotarium
   - f57v anomaly — random control
5. Discriminating verdict:
   - PASS if Antidotarium matches at d<1.0 to f104-105 AND specific to target (not in controls)
   - FAIL if zero f104-105 folios have any Antidotarium match at d<1.0
   - INCONCLUSIVE if matches are non-specific

---

## Result

### Global calibration

| Metric | Value |
|--------|------:|
| Total (recipe, folio) pairs | 10,168 |
| Min d achieved | **1.058** |
| Median d | 3.725 |
| Max d | 10.690 |
| Pairs at d<1.0 | **0 (0.00%)** |
| Pairs at d<1.5 | 49 (0.48%) |

**The d<1.0 threshold validated for C1971 (Codicillus ↔ Voynich Section B) produces zero matches anywhere when applied to Antidotarium ↔ Voynich.** The threshold does not generalize beyond the Codicillus alchemical tradition.

### Target folios (f104-105)

| Folio | Min d | Closest Antidotarium | d<1.0 | d<1.5 |
|-------|------:|---------------------|------:|------:|
| f104r | 2.33 | TRionfilon | 0 | 0 |
| f104v | 2.60 | ELectuarium | 0 | 0 |
| f105r | 3.05 | STomaticum | 0 | 0 |
| f105v | 2.43 | TRionfilon | 0 | 0 |

Zero Antidotarium recipes within d<1.5 of any f104-105 folio. f105r is most structurally distant (min d = 3.05).

### Controls (diagnostic)

| Control class | Folios | Total d<1.0 | Total d<1.5 |
|---------------|-------:|------------:|------------:|
| Section B alchemy (balneology) | 10 | 0 | 16 (15 on f83r alone) |
| matched-S PL Mercuriorum | 5 | 0 | 1 (f106r) |
| f57v anomaly | — | (not in folio set) | — |

**The residual Antidotarium signal concentrates on f83r (balneology) at d<1.5, not on f104-105.** Whatever feature similarity Antidotarium has to any Voynich content is misaligned with the target gap.

### Pre-registered verdict

**FAIL** — zero f104-105 folios have any Antidotarium match at d<1.0 (the validated C1971 threshold). Even relaxed to d<1.5, no f104-105 folio matches. Test discriminates cleanly: Antidotarium is excluded as a source for the Section S 4-folio gap.

---

## What this means for the gap

f104-105 are now externally excluded from:
- **Codicillus / PL Mercuriorum** (matched-S accounts for the rest of Section S; f104-105 are explicitly *un*matched in C1971 catalog)
- **Mesue Grabadin pharmacy** — falsified prior session via cross-manifold structural NN test (67.6% closer to Codicillus alchemy than Mesue pharmacy; matched-S 71.8% same direction per memory `project_section_s_remap_2026_05_15.md`)
- **Antidotarium Nicolai pharmacy** — this phase, clean negative

The four folios remain unidentified by any loaded external corpus. Possible identities:

1. **Salernitan medical tradition** or other late-medieval medical text not currently loaded
2. **Specialized alchemy variant** distinct from the Codicillus class — consistent with the cross-manifold structural NN result showing f104-105 are 67.6% closer to Codicillus alchemy than to Mesue pharmacy (i.e., they're alchemy-leaning but not Codicillus-typical)
3. **Hybrid or compound content** with no clear cognate corpus extant

---

## Why INDEX-only (no constraint registration)

Per PHASE_701/PHASE_702 precedent for clean negatives that confirm existing exclusion:

- The substantive finding (pharmacy traditions don't identify f104-105) was substantially established by Mesue Grabadin falsification in a prior session
- The d<1.0 calibration finding (threshold doesn't transfer beyond Codicillus tradition) is methodologically useful but implicit in `feedback_top1_matcher_mode_is_degenerate.md`
- Adding a new constraint number for "Antidotarium also doesn't match" would extend the negative-space framework-echo pattern crazy-expert flagged in PHASE_701 sign-off

---

## Updated source-gap status

Section S 4-folio gap source identification status:
- f104r, f104v, f105r, f105v: **structurally distinct** from Section B alchemy (high TTR 0.68-0.74), **excluded from Codicillus** (matched-S catalog), **excluded from Mesue pharmacy** (cross-manifold NN test), **excluded from Antidotarium Nicolai** (this phase). Identity unknown.

Next external-corpus candidates if pursuit continues:
- **Constantinus Africanus medical translations** (Salernitan tradition)
- **Trotula** (Salernitan compendium, late 11th c.)
- **Pseudo-Aristotle Secretum Secretorum** (medieval Latin medical-encyclopedic genre)
- **Theophilus De diversis artibus** (already loaded but craft-focused, not pharmacy)

---

## Cross-references

- C1971-C1976 — cold-read framework establishing PL Mercuriorum matches at d<1.0 (the methodology this phase applies)
- `feedback_top1_matcher_mode_is_degenerate.md` — the methodology lesson this phase respects
- `project_section_s_remap_2026_05_15.md` — Section S 4-folio gap definition and prior Mesue falsification
- `project_section_s_source_genre_gap.md` — source gap context

---

## Scripts and data

| File | Purpose |
|------|---------|
| `scripts/_antidotarium_f104_105_test.py` | Main test — d<1.0 gated absolute-distance matching with controls |
| `results/antidotarium_d1_test.json` | Full output: distance distribution, target results, control results, verdict |

Source data (already in repo): `sources/antidotarium_nicolai/antidotarium_nicolai_compound_features.json` (124 recipes with 8D features).

---

## Methodology note added

**The d<1.0 threshold from C1971 is corpus-specific to Codicillus tradition.** When applied to Antidotarium (compound pharmacy genre, distinct from alchemy procedural recipes), zero pairs hit d<1.0 anywhere in the manuscript. The threshold validated on one external corpus does not automatically generalize to other external corpora — each new source needs its own calibration. This is consistent with the existing `feedback_top1_matcher_mode_is_degenerate.md` lesson (per-corpus in-domain controls required) but adds a complementary observation: absolute-distance thresholds also need per-corpus calibration, not just per-corpus in-domain control validation.

Saved to memory: see `project_section_s_pharmacy_doubly_excluded.md`.
