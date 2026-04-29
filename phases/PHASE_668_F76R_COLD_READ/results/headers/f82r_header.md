# Validated Reading: f82r ↔ III.19.1-5 Medicinal Waters 2-6 (Multi-Recipe)

**Match tier:** Strong-supported (multi-recipe per C1937)
**Expert verdict:** Coherent under multi-recipe hypothesis (4/8 PASS, 3 PARTIAL, 1 FAIL)
**Full token listing:** `data/f82r_cold_read.txt` (275 tokens, 32 lines)

---

## How to Read This Document

This folio encodes five related sub-recipes from III.19 — the second through sixth medicinal waters, all prepared from a single capon/chicken. The combined recipe text is 1,251 characters (~230 words). The folio is 275 tokens — a 1.2:1 ratio under the multi-recipe model.

C1937 established that "short related procedures are consolidated onto single folios" (f80r = Ch21-25, f77r = Ch2+3+6). f82r follows this pattern: five brief water preparations sharing the same source material (capon parts), each with 1-2 operational steps.

The single-recipe test (f82r ↔ III.19.3 alone) returned PARTIALLY COHERENT with three tensions: 275 tokens for a 369-character recipe (scale mismatch), 13 dar for a recipe with 1 material addition, and 9 paragraphs for a 2-step recipe. All three tensions resolve under the multi-recipe hypothesis: 5 waters × ~50 tokens each, 13 dar for 5 "take..." instructions, 9 paragraphs for 5 operations plus transitions.

**What makes this match credible:**
- **P5 triple okain** (sealing step) maps to the 4th water's glass+wax sealing per C1929
- **P2 lowest e-depth** (0.47) + active monitoring + kam closure maps to 3rd water's ash distillation with "beware burning" warning
- **P8 extreme transfer concentration** (t-HEAD = 20.5%) maps to bone distillation's "take all their liquor"
- **dar distributed across 7/9 paragraphs** tracks 5 distinct material introductions
- **Alternating heat modes**: balneum (P1, P6-P8 high e-depth) vs ashes (P2, P5 low e-depth)

Every token on every line appears in this document.

---

## The Recipes (III.19.1-5, combined)

### Catalan (Part III cipher, no letter codes)

**2nd water (III.19.1):** Pren una capó veel o una gallina e plomen-lo, e gita'n los budells; e separa los pes e los ossos. E tota la carn sia picada; e aprés met-la dedins lo alembich e en bany; distilla tota l'aygua.

**3rd water (III.19.2):** Pren la carn de la gallina o del capó e sobre cenres distilla sa humiditat ab foch mijà bé continuat; e guarda't de la combustibilitat de la carn.

**4th water (III.19.3):** Pren de la humiditat simpla de la dita lunaria, e mit .iii. parts sobre la substancia de la dit carn. Puys tapa la carabasa ab son cubertor de vidre ab cera communa, e posa-u tot sobre cendres per .iii. dies naturalls ab foch de serradura composta. Puis distilla tota l'aygua per lo bany.

**5th water (III.19.4):** Pren de la substancia de la dita gallina o del capó, e sobre cendres separa tota la humiditat per distillació.

**6th water (III.19.5):** Pren los ossos del dit capó o de la gallina, e ben menudament picats mit-los en lo alembich e sobre cendres; pren tota lur liquor ab distillació.

### English (combined)

- **2nd water:** Take capon/hen, pluck, gut, separate feet and bones. Mince all flesh, put in alembic in balneum, distill all water.
- **3rd water:** Take the flesh, distill moisture on ashes with moderate continuous fire. **Beware burning the flesh.**
- **4th water:** Take lunaria moisture, put 3 parts on flesh substance. **Seal cucurbit with glass cover + common wax.** Place on ashes 3 days with sawdust fire. Then distill through balneum.
- **5th water:** Take flesh substance, distill all moisture on ashes.
- **6th water:** Take the bones, mince finely, put in alembic on ashes, take all liquor by distillation.

### Combined Structure

| Water | Material | Heat | Special |
|-------|----------|------|---------|
| 2nd | Minced flesh | balneum | butchery first |
| 3rd | Flesh | ashes (moderate) | "beware burning" |
| 4th | Lunaria + flesh | ashes → balneum | **seal** (glass+wax), ×3 |
| 5th | Flesh substance | ashes | brief extraction |
| 6th | Bones (minced) | ashes | final extraction |

---

## Structural Predictions (multi-recipe)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | 9 paragraphs ≈ 5 operations + transitions | 5 waters + prep/transitions | **MATCH** |
| 2 | Multiple dar (5+ distinct introductions) | each water "take..." | **MATCH** — 13 dar across 7/9 paragraphs |
| 3 | Alternating balneum/ashes | waters alternate heat modes | **PARTIAL** — e-depth varies but not cleanly binary |
| 4 | Sealing signature in P5 | 4th water glass+wax seal (C1929) | **MATCH** — triple okain |
| 5 | "Beware burning" quality gate | 3rd water warning | **PARTIAL** — P2 has monitoring + kam closure |
| 6 | Transfer concentration at end | 6th water "take all liquor" | **MATCH** — P8 t-HEAD 20.5% |
| 7 | Bone processing at end | last water processes bones | **PARTIAL** — P8-P9 are folio-final |
| 8 | ×3 counting for 4th water | ".iii. parts", ".iii. dies" | **FAIL** — no 3-token counting run |

**Score: 4 MATCH, 3 PARTIAL, 1 FAIL. Multi-recipe wins 8/10 criteria vs single-recipe.**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 275 |
| Lines | 32 |
| Paragraphs | 9 |
| dar (material-add) | 13 |
| Quality checks (chek/shek class) | 1 |
| Observation MIDDLEs | ckh×3, cth×1 |
| hh (extended observation) | 0 |
