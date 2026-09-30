# PHASE_773 — Zodiac figures against medieval degree tables

**Status: STOPPED AT DESIGN STAGE (no comparison computed).** The figure attributes lack the within-sign, figure-by-figure
variation that a per-degree test needs. The degree tables' per-sign contents have **not** been read, so a future test
with better-coded attributes remains blind.

## What was done
- **Design intent** committed before any data (38a6806, `DESIGN_INTENT.md`). The pairings were:
  - pitted degrees with figures with tubs;
  - light degrees with figures holding stars;
  - fortune degrees with crowned figures;
  - (exploratory) masculine/feminine degrees with clothing.
- **Degree tables** (`data/degree_tables.json`, `data/SOURCES.md`), collected by an agent kept away from all Voynich
  data.
  - Tables: masculine/feminine, light/dark/smoky/void, pitted, azemena, increasing fortune, monomoiria, Egyptian terms
    and faces.
  - Sources: al-Qabisi (1482, 1485, 1521 printings), Bonatti (1491), Leopold of Austria (1489), al-Biruni (tr. Wright
    1934), Lilly (1647) and Paulus Alexandrinus (1586).
  - Variants between sources are documented.
- **Figure codes** (`data/nymph_attributes.json`, `data/CODING_NOTES.md`), from a blind coding agent not told the
  hypothesis.
  - All 298 slots are coded (confidence: 70 high, 167 medium, 61 low).
  - Crops for human checking are kept locally in `data/crops/` (about 150 MB, not committed).
  - Known mismatches: Gemini ring 1 has one extra figure; Libra ring 1 may be off by one; Cancer has two slots at
    07:00.

## Why it stopped (figure side only)
| Attribute | Where it varies | Consequence |
|---|---|---|
| Tub / barrel | Pisces 29/29, Aries 30/30, Taurus 20/30, Gemini 3/29, and none on the six later signs | Within-sign variation only on Taurus (by page and ring) and Gemini (one cluster of 3). **P1 has no power.** |
| Crown | 3 in the whole zodiac | **P3 has no power.** |
| Star held vs near | Varies in 8 signs (e.g. Pisces 13/16; Libra 22/8) | The coder flagged held vs near as often a pixel's judgement, so **P2 depends on an unreliable attribute** |
| Clothed | Aries and Taurus only, **by page**: the light-animal pages are clothed, the dark-animal pages naked; Gemini 3 | Page-level design, not figure-level variation. P4 (exploratory) has no power |

## Descriptive iconographic findings (from the blind codes)
- **Two-page signs.** On Aries and Taurus, the page with the light animal has clothed figures, and the page with the
  dark animal has naked figures, with a few exceptions.
- **Gemini.** Its only tubs belong to a run of three consecutive clothed figures in ring 1.
- **Page-level design.** Tubs occupy the first zodiac pages (Pisces, Aries, the light Taurus page and the dark Taurus
  page's inner ring) and are absent from Cancer through Sagittarius.

## What would reopen it
A human- or better-coded attribute with genuine figure-by-figure variation would be needed: poses, hand positions,
objects, colours of stars, or hair. With that, the committed pairings, or new pairings fixed before opening the tables,
can be tested against `data/degree_tables.json` under a lean-audited pre-registration.
