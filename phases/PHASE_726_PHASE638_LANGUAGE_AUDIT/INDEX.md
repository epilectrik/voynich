# PHASE_726 — Phase 638 matcher language audit

**Run:** 2026-05-21 (script + result on disk; INDEX written and registered 2026-09-27 during the registry reconciliation).
**Status:** COMPLETE — provenance finding, no new constraint. Annotations placed on C1882 and C2052.

## Question
Does the recipe-side feature extractor used by the Phase 638 / 8D matching work (`phases/PER_DOMAIN_BRIDGE_CALIBRATION/scripts/pl_channel_features.py`, also used by RECIPE_FOLIO_CORRESPONDENCE and PHASE_641) operate on the Latin source or on an English translation?

## Result (`results/language_audit.json`)
| Regex set | English Testamentum (162k chars) | Latin Testamentum (121k) | SISMEL Latin+Catalan (342k) |
|---|---|---|---|
| English keyword regexes (fire, heat, degree, furnace, bath, ashes…) | 1,500 hits | 16 | 24 |
| Latin regexes | 74 | 1,327 | 1,576 |

The matcher input file is `testamentum_complete_english.txt`. The Pseudo-Lull channel features are therefore **keyword densities in an English translation**, not in the Latin text.

## Disposition (lean-expert, 2026-09-27)
- Provenance annotation, not a retraction: features are translation-mediated.
- The Latin path cannot simply be swapped in (16 hits → near-zero vectors that would collapse toward the C2026 attractor); a lemmatized Latin lexicon is needed first.
- Check language parity in C2052's controls (Theophilus, Antidotarium, Codicillus); C2052's operative conclusion (match breadth is not evidence) stands either way.
- Translation-invariance control: featurize two independent translations of one text.
- Affected: C1882–C1888, C1895, C1933, C1935, C1956, C2026, C2052 and assignments inherited by C1943–C1955, C1969, C1971–C1975, C1988. Unaffected: C2034 (native Catalan regex) and C1889 (corpus fact).
