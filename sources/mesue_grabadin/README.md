# Mesue's Grabadin

13th-century Latin pharmacopoeia traditionally attributed to "Mesue the Younger" (Pseudo-Mesue, Johannes filius Mesue). The Latin corpus is now believed to be the original work of one or possibly two 13th-century European individuals — likely Italian or French — who used the pseudonym to give authority to the text.

Described in modern scholarship as **"the most popular compendium of drugs in medieval Europe"**. ~400 compound preparations, organized by preparation type (electuaries, syrups, oils, ointments, troches, pills) rather than by ingredient. Practical apothecary's reference text — exactly the genre our `project_section_s_source_genre_gap.md` predicts for Voynich Section S.

## Source

Mesue, Johannes (Pseudo-Mesue), *Opera de medicamentorum purgantium delectu, castigatione, & vsu* + *Grabadin, hoc est compendij secretorum medicamentorum, libri duo*. Lyon, 1602 (the same recipe canon was first printed Venice 1471 and reprinted continuously through the 17th century — text is substantively stable across editions).

Internet Archive: <https://archive.org/details/bub_gb_7d7kepnAb-EC>
Source PDF: `bub_gb_7d7kepnAb-EC.pdf` (48.9 MB, 591 pages, scanned by Google Books from the National Central Library of Rome)

OCR: ABBYY FineReader 11.0 (Roman type, ~80% accuracy — rough but readable).

## Why this source

Per crazy-expert recommendation (2026-05-15): the Antidotarium Nicolai is a Salernitan teaching canon — over-curated 12th-century reference text. A Voynich practitioner working ~1404-1438 would more plausibly have worked from Mesue's Grabadin, the practicing apothecary's reference. The Grabadin is polypharmacy-heavy (>5 ingredients per recipe is the norm), matching Section S's predicted compound-pharmacy genre. Larger corpus than Nicolai (329K tokens vs 17K) provides more matching surface.

The 8D matcher baseline (C2026) showed TUNED_DIMS doesn't port to compound-pharmacy. A future pharmacy-appropriate matcher (per crazy-expert option 2) or hypothesis-driven distance gating against individual Section S folios (per C1943/C1955 method) is the path forward — Grabadin is the corpus that path needs.

## Files

| File | Description |
|------|-------------|
| `mesue_1602_lyon_djvu.txt` | Raw ABBYY OCR plain text (3.7 MB, 97,191 lines) |
| `mesue_1513_venice_djvu.txt` | 1513 Venice incunable OCR (1.5 MB) — gothic typeface, OCR is poor; **kept for reference only** (contains both Grabadin AND Antidotarium Nicolai for cross-comparison) |
| `mesue_grabadin_liber_primus.txt` | **Primary corpus part 1.** Liber Primus = Antidotarium / Compound Preparations. 7,517 paragraphs, 249K tokens |
| `mesue_grabadin_liber_secundus.txt` | **Primary corpus part 2.** Liber Secundus = De Appropriatis / Specific Applications by body part. 1,001 paragraphs, 80K tokens |
| `mesue_grabadin_latin_full.txt` | Combined Liber Primus + Secundus with book markers. 2.6 MB |
| `_extract.py` | Extractor pipeline |

## Corpus volume

```
Liber Primus  (Antidotarium):      7,517 paragraphs,  249,282 tokens
Liber Secundus (De Appropriatis):  1,001 paragraphs,   79,753 tokens
Combined:                          8,518 paragraphs,  329,035 tokens
```

Unique-type counts are inflated by OCR errors (each misspelling adds a "type"). Real distinct Latin vocabulary is likely 5-10K types after normalization.

For comparison:
- Antidotarium Nicolai (van den Berg 1917): 17K tokens, 3.8K types — much cleaner OCR
- Brunschwig 1512 (English): 51K lines, validated featurized
- This corpus is ~19x the Nicolai token count, ~6x the Brunschwig English

## Known limitations

**OCR is rough:**
- 1602 Roman type but processed by ABBYY FineReader 11 — common artifacts include f/s confusion, c/e confusion, ñ for various nasals, &/et substitutions, broken italic ligatures.
- Paragraph segmentation is over-aggressive (pdftotext put paragraph breaks at OCR line wraps). Real recipe segmentation needs to detect "Recipe X..." starts and join continuation lines.
- Index entries, page-repeat headers, and commentary by later editors (Sylvius, Costa, Bonyn) are interleaved with primary text. The extractor strips page headers but not all commentary.

**Edition is late (1602):**
- The Grabadin text canon is substantively stable across 1471-1602 (~250 reprintings), but specific recipe variants may differ from the recension Voynich's compiler would have known. The 1513 Venice incunable in this directory is closer in date but the gothic-type OCR is too rough to use directly.
- For close textual work, prefer the 1513 PDF facsimile and read directly; use the 1602 djvu.txt for keyword search / lexical work.

**Petrus Abano's Additio (Additions):**
- Petrus Abano (c. 1257-1316) added supplementary recipes to the Mesue canon that are included in printed editions. Our 1602 extraction includes these. They may be useful or may be confounders for chronological matching — flag if needed.

## Status

Corpus acquired and extracted 2026-05-15. **Not yet aligned to Voynich Section S folios.** Next moves per crazy-expert / expert-advisor consultation:
- Build pharmacy-appropriate matcher with different features (ingredient-name distinct-types, recipe-length distribution, proportion-symbol density, recipe-segmentation count per folio)
- OR run hypothesis-driven distance tests against pre-identified candidate Section S folios using the C1943/C1955 method (token-verb ratio, fch positions, e_depth structure, structural co-criteria)

## See also

- `sources/antidotarium_nicolai/README.md` — companion Salernitan pharmacy text, simpler / curated / earlier
- `project_section_s_source_genre_gap.md` — memory note tracking the Section S source-matching effort
- `phases/RECIPE_FOLIO_CORRESPONDENCE/results/antidotarium_baseline.json` — yesterday's baseline that demonstrated the 8D matcher doesn't port to pharmacy
- C2026 in `context/CLAIMS/INDEX.md` — registered baseline result
