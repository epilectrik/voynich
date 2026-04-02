# Phase 635: Full-Spectrum Recipe Scan

**Status:** COMPLETE
**Verdict:** PROCEDURAL_CONTENT_ONLY
**Constraints:** C1930-C1933

---

## Research Question

Does the full Testamentum (209 chapters) + Codicillus produce recipe-folio matches beyond the Mercuriorum distillation-family matches from Phase 628? Do other PL parts (Theorica, Furnis) match to Voynich folios? Does the Codicillus add new assignments?

## Background

Phase 628 (C1882-C1890) matched 16 distillation-family chapters to R1 folios. Phase 634 (C1925-C1929) synthesized cross-folio crib decode findings and established the f75-f84 = Mercuriorum section correspondence. This phase expands the matching to ALL PL chapters across all operation families, and tests the Codicillus as an alternative source.

## Novel Contribution

1. Mercuriorum content splits across TWO manuscript sections (B and S)
2. B-grammar recipe content exists in Section T ring diagram format
3. Theorica and Furnis produce zero atom-validated matches — manuscript is procedural only
4. Expanded matching beyond distillation family generalizes with minimal distance penalty
5. Codicillus adds zero folio assignments beyond Testamentum coverage

---

## Scripts

| Script | Location | What |
|--------|----------|------|
| `_full_spectrum_matcher.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | 194 procedural chapters × 82 folios, 8D residual matching |
| `_combined_spectrum_matcher.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Testamentum + Codicillus combined scan |
| `_match_unmatched_merc.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Expanded non-distillation Mercuriorum matching |
| `_featurize_codicillus.py` | sources/codicillus/ | Codicillus 19-segment featurization |
| `_atom_decode_f79r.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch12M sublimation → elixir (strongest expanded match) |
| `_atom_decode_f107r.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch44M quicksilver coagulation |
| `_atom_decode_f66r.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch24P fixation in ring diagram |
| `_atom_decode_f76v.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch15M ferment conversion |
| `_atom_decode_f112v.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch1M lunaria → quicksilver |
| `_atom_decode_f116r_f103r.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch4M fixation + Ch16M multiplication |
| `_atom_decode_f78v.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch14M composite ferments |
| `_atom_decode_f111v.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch10M pearl finishing (unclear) |
| `_atom_decode_f83v.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch2M coagulation (partial) |
| `_atom_decode_f80v.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Ch3M sublimation (failed — too short) |
| `_quick_decode_f105v_f86v5.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Both rejected as noise |
| `_animal_chain_profiles.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Animal waters sub-chain comparison |
| `_mercuriorum_chain.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Chapter-to-folio ordering analysis |
| `_check_gaps.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Undocumented folios in f75-f84 |

---

## Constraints

### C1930: Mercuriorum splits across two manuscript sections (Tier 2, extends C1927)

The Liber Mercuriorum maps to TWO distinct manuscript neighborhoods:
- **Section B (f75-f84):** Preparation chapters Ch1-Ch28 (mercury pipeline, animal waters, infrastructure). 14 folios matched.
- **Section S (f103-f116):** Transmutation/multiplication chapters Ch40+ (coagulation, ferment multiplication). 6 folios matched: f103r (Ch16M, strongly supported), f107r (Ch44M, supported), f108r (Ch16P, inconclusive), f112r (Ch11M, supported), f112v (Ch1M, supported), f116r (Ch4M, supported).

The split is functional: preparation procedures cluster in Herbal B, while transmutation/application procedures cluster in Pharmaceutical S. Folio-to-chapter ordering within each section does NOT follow PL book order (r=-0.179 per C1927).

- Scope: B, S, PL, Mercuriorum, C1927
- Metrics: section_B=14_folios. section_S=6_folios. preparation=Ch1-28. transmutation=Ch40+.

### C1931: B-grammar recipe content in Section T ring format (Tier 2)

Folio f66r is physically located in Section T (zodiac) and uses ring diagram layout (R-placement, 297 tokens), but contains exclusively Currier B grammar (language=B, 349 H-track tokens, 0 Currier A, 0 AZC). The operational profile matches Ch24 Practica (fixation): da=10.0% (rank 5/82), 82% dry heat, 62 folio-unique words, dar=4. This is B-language recipe content in a ring physical format, NOT AZC metalayer content (contrast C1127: rosettes are AZC-like grammar with cosine 0.49-0.82 to AZC).

- Scope: B, T, f66r, ring, C1127
- Metrics: B_tokens=349. A_tokens=0. AZC_tokens=0. da_pct=10.0. da_rank=5of82. dry_heat=82%. unique_words=62.

### C1932: Theorica and Furnis produce zero atom-validated matches (Tier 2)

Full-spectrum scan of all 209 PL chapters against 82 B folios: 194 chapters have nonzero operational features. Of 120 "theoretical"-family chapters that passed the feature filter, all confident matches (ratio > 1.2) either collapse onto universal attractor folios (f84v absorbs 24 chapters, f34v absorbs 17) or are false positives from metaphorical keyword use (Ch73 "separation" = Hermetic metaphor, not operational separation — atom decode of f75v confirmed). The 30 Furnis chapters produce 2 genuine matches (Ch27→f77v furnace spec, Ch28→f82v vessel spec, both already in Phase 634) and noise. The manuscript encodes procedural Practica and Mercuriorum content only.

- Scope: B, PL, Theorica, Furnis, C171
- Metrics: theorica_chapters=96. furnis_chapters=30. atom_validated_theorica=0. atom_validated_furnis=2(already_registered). attractor_folios=f84v(24ch)+f34v(17ch).

### C1933: Expanded matching beyond distillation family generalizes (Tier 2)

Extending the Phase 628 8D residual matching from distillation-only (16 chapters) to all operation families (82 procedural chapters): mean distance increases only 1.07x (2.358 vs 2.214). 8+ new atom-validated matches found including f79r←Ch12M (d=1.02, strongest expanded match: 3 dar at 3 predicted material positions, P7 monitoring spike for color endpoint, sublimation thermal profile). Other validated matches: f103r←Ch16M (strongly supported), f107r←Ch44M (supported), f116r←Ch4M (supported), f76v←Ch15M (supported), f78v←Ch14M (moderate). The 8D feature space captures operational similarity across families, not just distillation.

- Scope: B, PL, matching, C1882
- Metrics: distillation_mean_dist=2.214. expanded_mean_dist=2.358. ratio=1.07x. new_validated=8+. best_expanded=f79r(d=1.02).

---

## Folio Notes Created This Phase

| Folio | Match | Verdict |
|-------|-------|---------|
| f66r | Ch24P fixation (ring diagram) | Supported |
| f76v | Ch15M ferment conversion | Supported |
| f78v | Ch14M composite ferments | Moderate |
| f79r | Ch12M mercury sublimation | Supported (strong) |
| f79v | Ch20? balneum candidate | Speculative |
| f80r | Ch21-25M animal ash chain | Supported |
| f82v | Ch28M vessel specification | Supported |
| f83r | Ch9P first distillation | Moderate |
| f103r | Ch16M ferment multiplication | Strongly supported |
| f107r | Ch44M quicksilver coagulation | Supported |
| f111v | Ch10M or Ch20M | Unclear |
| f112v | Ch1M lunaria → quicksilver | Supported |
| f116r | Ch4M fixation | Supported |

Also updated: f84r (product chain), f108r (trajectory, dar hypothesis)

---

## Summary

The full-spectrum scan confirms that the Voynich manuscript's Currier B text encodes procedural content from the Pseudo-Lull Testamentum's Practica and Mercuriorum sections. Theoretical and construction chapters do not match. The Codicillus adds no new assignments. The Mercuriorum production chain spans two manuscript sections (B for preparation, S for transmutation), with one fixation recipe encoded in a Section T ring diagram. 30 folios now documented with recipe correspondences.
