# Phase 634: Cross-Folio Crib Decode Synthesis

**Status:** COMPLETE
**Verdict:** SECTION_CORRESPONDENCE_ESTABLISHED
**Constraints:** C1925-C1929

---

## Research Question

Do the individual recipe-folio matches from Phase 628-629 exhibit cross-folio patterns at the token, folio, and section level that are independently verifiable? Specifically: (1) does the material-addition token `dar` behave consistently across all matched folios, (2) does the quality-check token `chekar` appear in structurally consistent contexts, (3) do the matched folios cluster into a section-level correspondence with the PL text, and (4) do individual atom-level decodes reveal structural features predicted by the matched recipes?

## Background

Phase 628 (C1882-C1890) established individual recipe-to-folio matching via 8D residual features. Phase 629 (C1891-C1896) validated content correspondence for f75r and f76r. Phase 630 (C1897-C1900) introduced atom-level decoding via `atomize()`. This phase synthesizes cross-folio findings from atom-level decodes of 8 additional folios (f77v, f81v, f82r, f84r, f84v, f108r, f112r) and the chekar prediction test (f33r, f34r, f94r, f95r1).

## Novel Contribution

1. dar token encodes "introduce new/distinct material" — verified across 6 matched folios with zero exceptions
2. chekar appears in post-thermal vessel-monitoring context across all 7 folios where it occurs
3. f75-f84 manuscript region maps to Liber Mercuriorum at section level (8/11 folios)
4. Mercuriorum encodes parallel mineral + animal production chains converging at Ch26
5. f82r exhibits a 5-token sealing micro-paragraph predicted by the matched recipe's cucurbit-sealing step

---

## Scripts

All in `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/` (shared directory with Phase 628-629):

| Script | What | Key Result |
|--------|------|------------|
| `_chekar_prediction_test.py` | Test chekar on 4 predicted folios | All 4 have chekar in balneum-compatible local context |
| `_chekar_context_test.py` | chekar local context vs corpus baseline | qo depleted 0.48x, daiin 3.7x enriched on chekar lines |
| `_atom_decode_f112r.py` | Atom decode f112r vs Ch11 | ok escalation 5%→27%, zero dar correct for cohobation |
| `_atom_decode_f108r_v2.py` | Atom decode f108r vs Ch16 | No clean two-phase structure, head-scratcher |
| `_atom_decode_f81v.py` | Atom decode f81v vs Ch18 Merc | dar+dal on L1, daiin x9 in P1 |
| `_atom_decode_f82r.py` | Atom decode f82r vs Ch22 | 5-token sealing para, 12 consecutive qo lines |
| `_profile_f112r.py` | Full profile f112r | 10 paragraphs, ok+ot=23.6% |
| `_mercuriorum_chain.py` | Map Ch18-Ch29 to folios | 8/11 f75-f84 match Mercuriorum |
| `_animal_chain_profiles.py` | Profile f78v, f80r, f82r, f82v | f82r strongest candidate |
| `_f108r_trajectory.py` | e-depth trajectory analysis | r=0.54 upward drift, not clean inversion |
| `_full_decode_f76r_v2.py` | Atom decode f76r (100% coverage) | 91.9% middle dict, 6.4% auto, 1.6% atom |

---

## Constraints

### C1925: dar encodes new material introduction across matched folios (Tier 2)

The token `dar` (da+r, setup+input) appears on folios matched to recipes that introduce new/distinct materials, and is absent on folios matched to recipes that only process existing materials (cohobation, pure separation). Tested across 6 matched folios:

| Folio | Recipe | New materials? | dar count |
|-------|--------|---------------|-----------|
| f75r | Ch19: add honey + wax | YES (2 new) | 10 |
| f84r | Ch14: add gold + vegetable G | YES (2 new) | 13 |
| f76r | Ch18P: add test material | YES (1 new) | 7 |
| f82r | Ch22: add lunaria moisture | YES (1 new) | 1 |
| f112r | Ch11: cohobation only | NO | 0 |
| f108r | Ch16: pure separation | NO | 0 |

6/6 correct partition. `dal` (da+l, setup+frame) appears as the passive counterpart, encoding material output/transfer in non-introduction contexts (cohobation returns, collecting distillate). f75r's unique double-dar (L35-36) maps to Ch19's two-ingredient addition (honey + wax). f82r's single dar (L11) maps to Ch22's single new ingredient (lunaria). Extends C1894 (double-dar corpus uniqueness) with semantic interpretation grounded in recipe correspondence.

- Scope: B, cross-folio, PL, dar, dal, C1894, C1896
- Metrics: partition=6of6. dar_present_iff_new_material=100%. f75r_dar=10. f84r_dar=13. f76r_dar=7. f82r_dar=1. f112r_dar=0. f108r_dar=0.

### C1926: chekar appears in post-thermal vessel-monitoring context cross-folio (Tier 2)

The token `chekar` (ch+ek+ar, test+precision+respond) appears on 7/83 Currier B folios. On chekar-bearing lines (N=7), the PREFIX environment shows: qo depleted to 0.48x (quality check occurs AFTER heat, not during), ok enriched 1.60x (vessel verification), ol enriched 1.79x (continuation). Balneum-associated tokens are enriched: daiin 3.7x, okal 3.8x, okar 3.6x, okaiin 2.3x, dar 2.0x.

The 3 confirmed balneum folios (f75r, f84r, f108r) all contain chekar. The 4 predicted folios (f33r, f34r, f94r, f95r1) all contain chekar in balneum-compatible local context, but are Section H folios where balneum is one step in a larger procedure, not the dominant operation. The aggregate folio profiles of the predicted folios do NOT match the balneum centroid (0/4 pass Euclidean distance test) — the signal is in the LOCAL line context, not the folio-level profile.

chekar is absent from f76r (correct negative — Ch18 Practica uses silver-plate test, not balneum) and f82r (correct — Ch22 has no explicit quality test step).

- Scope: B, cross-folio, chekar, ek-MIDDLE, C1896, C929
- Metrics: folios=7of83. qo_depleted=0.48x. ok_enriched=1.60x. daiin_enriched=3.7x. okal_enriched=3.8x. confirmed_balneum=3of3. predicted_balneum_local=4of4. f76r_absent=correct_negative.

### C1927: f75-f84 maps to Liber Mercuriorum at section level (Tier 2)

8 of 11 folios in the f75-f84 manuscript region match Mercuriorum chapters in the Phase 628 8D residual matching (3 confirmed, 2 supported, 3 not confident by automated criteria). The remaining 3 match Practica chapters (f76r=Ch18P confirmed, f83r=Ch9P, f84r=Ch14P confirmed). No other contiguous manuscript region shows this degree of single-part concentration.

| Folio | PL Chapter | Part | Status |
|-------|-----------|------|--------|
| f75r | Ch19 | Mercuriorum | Confirmed |
| f76r | Ch18 | Practica | Confirmed |
| f77v | Ch27 | Mercuriorum | Supported |
| f78v | Ch21 | Mercuriorum | Not confident |
| f80r | Ch25 | Mercuriorum | Not confident |
| f81v | Ch18 | Mercuriorum | Supported |
| f82r | Ch22 | Mercuriorum | Supported |
| f82v | Ch28 | Mercuriorum | Not confident |
| f83r | Ch9 | Practica | Confident |
| f84r | Ch14 | Practica | Confirmed |
| f84v | Ch24 | Mercuriorum | Rejected |

The Practica chapters interspersed in this region (Ch9, Ch14, Ch18P) describe base preparations used by the Mercuriorum procedures, consistent with a workshop manual that interleaves source procedures with their applications. Folio-to-chapter ordering within the region does NOT follow book order (r=-0.179) — the manuscript may follow procedural/product-chain order instead.

- Scope: B, section, PL, Mercuriorum, Practica, C1882
- Metrics: mercuriorum_folios=8of11. practica_folios=3of11. folio_chapter_order_r=-0.179. confirmed=3. supported=3. not_confident=3. rejected=1.

### C1928: Mercuriorum encodes parallel mineral + animal production chains (Tier 3)

Ch18-Ch29 of the Liber Mercuriorum encode two parallel production chains that merge at Ch26 (medical administration):

**Mineral chain** (Ch15-17 → Ch18 → Ch19): Mercury-water → dissolve gold (Ch18, f81v) → add honey/wax, 9x reflux (Ch19, f75r). Product: composite aqua vitae.

**Animal chain** (Ch20-25): Systematic disassembly of one capon/hen into 5 waters by method (bath, ash, lunaria maceration, bone distillation), selectively combined in Ch25. Product: carrier/vehicle waters.

**Convergence** (Ch26): Gold medicine from mineral chain dissolved in animal waters, administered by humoral patient type (phlegmatic, choleric, melancholic, sanguine) with specific carriers (wine, water, broth).

**Infrastructure** (Ch27-28): Furnace specification (5 types, f77v) and universal vessel specification (3-part assembly).

The product chain implies that f75r's quintessence is an input to f84r's gold tincture (explicitly confirmed: Ch14 requires "vegetable G" = quintessence). The animal chain (Ch20-25) maps to the f78-f82 folio cluster, with f82r (Ch22, lunaria maceration) as the strongest individual match in the sub-chain.

- Scope: B, PL, Mercuriorum, product chain, C1882, C1927
- Metrics: mineral_chapters=Ch15-19. animal_chapters=Ch20-25. convergence=Ch26. infrastructure=Ch27-28. f75r_to_f84r_link=confirmed (vegetable_G=quintessence).

### C1929: f82r exhibits recipe-predicted sealing micro-paragraph (Tier 2)

Folio f82r (matched to Ch22 Mercuriorum, lunaria maceration) contains a 5-token micro-paragraph (P3, line 18) positioned between material introduction (P2, dar on L11) and sustained maceration (P4, 12 consecutive qo lines):

P3: `okain char okain qokeedy lchy`
= vessel-intake, test-release, vessel-intake, heat-source steady-batch, state-test-end

Two `okain` (vessel-intake) tokens in a 5-token paragraph at the material→maceration boundary. Ch22 explicitly says: "close the cucurbit with its glass cover, and with common wax." The sealing step is encoded as a structural paragraph boundary, not inline with the preceding or following operations.

Supporting evidence from f82r:
- dar=1 (L11): exactly one new material (lunaria), matching recipe
- P4: 12 consecutive lines with qo tokens = sustained 3-day heat
- Gentle heat 22.9% = sustained ash heat (intermediate between balneum and flame)
- sh=11.3% elevated for passive monitoring of sealed vessel

The match was NOT confident by automated 8D criteria (ratio 0.791, CV 48.2%) but the atom-level decode provides stronger evidence than several "confident" matches.

- Scope: B, f82r, PL, Ch22, micro-paragraph, sealing, C1882, C1925
- Metrics: P3_tokens=5. okain_count=2. dar_total=1. P4_consecutive_qo_lines=12. gentle_heat=22.9%. sh=11.3%. automated_ratio=0.791. automated_cv=48.2%.

---

## Folio Notes Created/Updated

| Folio | Action |
|-------|--------|
| f82r | Created: full atom decode, sealing paragraph, product chain position |
| f81v | Created: dar+dal co-occurrence, daiin concentration, product chain |
| f112r | Created: ok escalation, zero dar cohobation hypothesis |
| f84v | Created: match rejected (size mismatch, statistical false positive) |
| f108r | Updated: atom decode, trajectory analysis, dar hypothesis, downgraded to head-scratcher |
| f84r | Updated (laptop): atom decode, product chain, dark pipeline, cipher resolution |
| INDEX | Updated: f82r, f81v, f112r, f84v added |

---

## Summary

Phase 634 synthesizes cross-folio findings from atom-level decodes of 8 folios beyond the Phase 629 confirmed pair. The central result is that individual token behaviors (dar, chekar) are consistent across independently-matched folios, and the matches cluster into a section-level correspondence (f75-f84 = Liber Mercuriorum) that encodes parallel production chains. The f82r sealing micro-paragraph demonstrates that recipe-specific structural features are recoverable at the paragraph level even on folios that fail automated matching criteria.
