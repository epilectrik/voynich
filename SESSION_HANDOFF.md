# Session Handoff: Full-Spectrum Recipe Matching

**Date:** 2026-04-01
**Last commit:** `ce017e2`
**Current branch:** master
**Version:** 6.07 | **Constraints:** 1929 | **Phases:** 634
**Status:** Phase 634 complete, 28 documented folios, ready for full-spectrum matching

---

## What We Did This Session

### Phase 634: Cross-Folio Crib Decode Synthesis (C1925-C1929)

Formalized 5 constraints from accumulated exploratory work:
- **C1925:** dar encodes new material introduction (6/6 partition across matched folios)
- **C1926:** chekar appears in post-thermal vessel-monitoring context (7 folios)
- **C1927:** f75-f84 = Liber Mercuriorum section correspondence (8/11 folios)
- **C1928:** Mercuriorum parallel mineral + animal production chains
- **C1929:** f82r 5-token sealing micro-paragraph

### Mercuriorum Chain Mapping (20/25 chapters matched)

Decoded and documented 17 NEW folios beyond Phase 629's confirmed pair:

| Ch | Folio | Content | Verdict |
|----|-------|---------|---------|
| Ch1 | f112v | Lunaria → quicksilver (pipeline origin) | Supported |
| Ch4 | f116r | Fixation, fusibility test | Supported |
| Ch11 | f112r | Red mercury tincture | Supported |
| Ch12 | **f79r** | Mercury sublimation → elixir | **Supported (strong, d=1.02)** |
| Ch14M | f78v | Composite ferments | Moderate |
| Ch15 | **f76v** | Ferment conversion (join H + bind) | **Supported (P4 n-atom explosion)** |
| Ch16M | **f103r** | Ferment multiplication | **Strongly supported (balneum + escalation)** |
| Ch18M | f81v | Potable gold / water of life | Supported |
| Ch19M | f75r | 9x reflux aqua vitae | CONFIRMED |
| Ch21-25 | f80r | Animal ash chain (multi-chapter) | Supported |
| Ch22 | **f82r** | Lunaria maceration | **Supported (strong, sealing para)** |
| Ch27 | f77v | Furnace specification | Supported |
| Ch28 | f82v | Vessel specification (twin of f77v) | Supported |
| Ch9P | f83r | First distillation (grinding) | Moderate |
| Ch14P | f84r | Gold dissolution | CONFIRMED |
| Ch18P | f76r | Element separation | CONFIRMED |
| Ch16P | f108r | Element separation | Head-scratcher |
| Ch24 | f84v | Bone distillation | REJECTED |

Also profiled: f83v (Ch2 partial), f80v (Ch3 failed), f111v (Ch10 unclear), f79v (balneum candidate).

### Key Methodological Finding

The 8D aggregate matching (Phase 628) is a good FILTER but misses structural correspondence. The atom-level decode catches things no automated system would flag:
- f82r's 5-token sealing paragraph (ratio 0.791, NOT confident by 8D)
- f79r's P7 monitoring spike for color endpoint (not in Phase 628 at all)
- f76v's P4 n-atom explosion for binding (not directly matched)

Three improvements identified for the matching algorithm:
1. **dar/dal as a feature dimension** — cleanest single discriminator (6/6)
2. **Expand beyond distillation family** — found f79r, f103r, f116r
3. **Size-complexity gate** — catches f84v-type false positives

---

## Next Session: Path A — Full-Spectrum Matcher

### Goal
Scan the FULL Testamentum (209 chapters) + Codicillus against ALL 83 Currier B folios. Find section-level correspondences beyond the Mercuriorum.

### Approach
1. Build improved matching script incorporating:
   - dar/dal as matching dimension
   - All operation families (not just distillation)
   - Size-complexity gate
   - Paragraph-count sanity check
2. Run full scan: 209 PL chapters × 83 folios + Codicillus chapters × 83 folios
3. Identify clusters: which folio neighborhoods match which PL sections?
4. Atom-decode the top candidates from new section matches

### What We Know About PL Structure
- **Practica** (~30 chapters): Only 4 matched so far (Ch9, Ch14, Ch16, Ch18). ~26 untested.
- **Mercuriorum** (29 chapters): 20 matched. Nearly complete.
- **Theorica** (~80 chapters): Mostly theoretical, but some may be procedural.
- **Other parts:** De Essentia, De Inventione, etc. Unknown procedural content.

### What We Know About Folio Coverage
- **f75-f84 (Herbal B):** Mercuriorum section. 20 folios, nearly fully mapped.
- **Section S (f103-f116):** 5 matches found (f103r, f108r, f112r, f112v, f116r). May correspond to a different PL part.
- **Section H (Herbal):** Only illustration matches (f31r, f46v, f55r) and chekar prediction folios. Unexplored for recipe matching.
- **Rest of Herbal B (f43-f74, f85-f102):** Completely unmapped. ~40 folios.

### Codicillus
Fully transcribed and translated (`sources/codicillus/`). 205 pages, heavy on mercury preparation. Never matched against Voynich folios. Three candidates flagged (f79r, f79v, f80r) but never tested.

---

## Critical Files

| File | What |
|------|------|
| `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/shared_628.py` | 8D matching infrastructure (TUNED_DIMS, residual_match) |
| `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/_match_unmatched_merc.py` | Expanded matching script |
| `phases/PER_DOMAIN_BRIDGE_CALIBRATION/results/` | PL chapter feature data |
| `results/folio_operational_profiles_v3.json` | Folio operational profiles |
| `phases/ATOM_FOLIO_ATLAS/results/folio_atlas.json` | Atom-level folio atlas |
| `sources/pseudo_lull_testamentum/testamentum_complete_english.txt` | PL English (209 chapters) |
| `sources/codicillus/codicillus_complete_english.txt` | Codicillus English |
| `context/FOLIOS/` | 28 documented folios |
| `context/CLAIMS/INDEX.md` | 1929 constraints, v6.07 |

---

## dar Hypothesis Status (C1925)

Tested on 6 folios, 6/6 correct. Untested on 14+ new matches from this session. Quick validation pass recommended before building it into the matcher.

| Folio | Recipe adds new material? | dar | Status |
|-------|--------------------------|-----|--------|
| f75r | YES (honey+wax) | 10 | ✓ |
| f84r | YES (gold+quintessence) | 13 | ✓ |
| f76r | YES (test material) | 7 | ✓ |
| f82r | YES (lunaria) | 1 | ✓ |
| f112r | NO (cohobation) | 0 | ✓ |
| f108r | NO (pure separation) | 0 | ✓ |
| f79r | YES (mercury+water+stone-water) | 3 | untested |
| f78v | YES (ferment components) | 2 | untested |
| f116r | YES (quicksilver) | 5 | untested |
| f103r | YES (chamber mixtures) | 2 | untested |
| f76v | YES? (join H) | 0 dar, 2 dal | needs review |
| f81v | YES (gold) | 3 | untested |
| f80r | YES (multiple materials) | 3 | untested |
