# Hieronymus Brunschwig - Liber de arte distillandi de compositis (1512)

## Publication Details

- **Author:** Hieronymus Brunschwig (Jheronimo bruschwick)
- **Title:** Liber de arte Distillandi de Compositis. Das buch der waren kunst zu distillieren die Composita und simplicia, und dz Buch thesaurus pauperum, Ein schatz d'armen genant Micarium, die brosamlin gefallen von den buchern d'Artzny, und durch Experiment von mir Jheronimo bruschwick uff geclubt und geoffenbart zu trost denen die es begeren.
- **Also known as:** Grosses Destillierbuch (Large Book of Distillation)
- **Publisher:** Johann Gruninger, Strasbourg, 1512
- **Language:** Early New High German (Fruhneuhochdeutsch), printed in Fraktur/blackletter
- **Key feature:** Title contains "geoffenbart" (revealed) -- explicit secrecy-to-openness marker. Brunschwig frames the entire work as a revelation of hidden/secret knowledge for the common benefit.

## Relationship to the 1500 Small Book

This is the EXPANDED 1512 edition, distinct from the 1500 "Kleines Destillierbuch" (Liber de arte distillandi de simplicibus), which is already in the repository at `sources/brunschwig_1500_text.txt`.

Key differences:
- The 1500 book covers **simples** (individual plant/mineral distillations)
- The 1512 book covers **composites** (compound preparations: syrups, electuaries, pills, oximels, etc.)
- The 1512 book includes the "Thesaurus pauperum" (Treasure of the Poor) section
- The 1512 book is roughly 3-4x larger than the 1500 edition
- Approximately 1/3 of the quintessence chapters derive from Johannes Rupescissa (Jean de Roquetaillade), cited 7+ times (OCR renders his name as "Johannes rubiciscus" / "Johannes rubicissi" due to Fraktur long-s)

## Files in This Directory

| File | Lines | Size | Source | Quality |
|------|-------|------|--------|---------|
| `brunschwig_1512_large_book.txt` | 92,557 | 2.5 MB | NLM via Archive.org (DjVu OCR) | **BEST** - Primary text file |
| `archive_wellcome_fulltext.txt` | 125,997 | 2.6 MB | Wellcome via Archive.org (DjVu OCR) | Good in body text, poor early pages |
| `google_books_text.txt` | 79,281 | 2.5 MB | Google Books PDF text layer | OK but words often run together (no spaces) |
| `nlm_ocr_raw.txt` | 62,258 | 2.3 MB | NLM direct OCR download | Poorest quality - heavy character substitution |

The primary file (`brunschwig_1512_large_book.txt`) is the NLM copy scanned from a 751-page physical book. OCR quality is moderate -- this is 16th-century Fraktur, so expect character-level errors. However, the text is largely readable for keyword searching and computational analysis. Notable OCR artifacts:
- Long-s (ſ) is sometimes preserved, sometimes rendered as f
- Ligatures and abbreviation marks (e.g., nasal tilde over vowels) partially preserved
- "geoffenbart" correctly captured 76 times throughout the text
- "quinta essentia" / "quintam essentiam" captured ~90 times
- Rupescissa references captured but with garbled spelling

## Digitized Source URLs

1. **Archive.org (NLM copy):** https://archive.org/details/2225013R.nlm.nih.gov (751 pages, OCR text + PDF)
2. **Archive.org (Wellcome copy):** https://archive.org/details/hin-wel-all-00000060-001 (751 pages, OCR text + PDF with text layer)
3. **Google Books (BSB copy):** https://books.google.com/books?id=Js5VAAAAcAAJ (844 pages with Google OCR, PDF/EPUB download)
4. **Science History Institute:** https://digital.sciencehistory.org/works/1jcqz5i/viewer/td3s00z (142 page images, no OCR text)
5. **Wellcome Collection:** https://wellcomecollection.org/works/uhz33wb2 (749 images, PDF download)
6. **Gallica / BnF:** https://gallica.bnf.fr/ark:/12148/btv1b2100006k.item (OCR may be available but access was restricted)
7. **NLM Digital Collections:** https://collections.nlm.nih.gov/catalog/nlm:nlmuid-2225013R-bk (PDF + OCR text download)
8. **University of Frankfurt (OPUS 4):** https://publikationen.ub.uni-frankfurt.de/frontdoor/index/index/year/2007/docId/17473 (76 MB PDF)

## Content Structure

The book is organized into multiple "Bucher" (books):

1. **First Book:** Quinta essentia (quintessence) -- how to extract it from wine, herbs, gold (Aurum potabile), etc. Heavy Rupescissa influence.
2. **Second Book:** Compound waters (distilled waters for ailments organized by body part, head to foot)
3. **Third Book:** Syrups, oximels, and liquid preparations
4. **Fourth Book:** Electuaries, pills, and solid preparations
5. **Fifth Book:** Medical recipes and treatments organized by condition

Key vocabulary appearing in the text:
- "geoffenbart" (revealed), "offenbaren" (to reveal) -- 76 occurrences
- "quinta essentia" / "quintam essentiam" -- ~90 occurrences
- "distillieren" / "distillierũg" -- hundreds of occurrences
- "Aurum potabile" (drinkable gold) -- multiple chapters
- "Balsamum" / "balsam" -- extensive discussion
- "Johannes rubiciscus" = Johannes Rupescissa (OCR garbling of Fraktur)

## Notes on OCR Quality

All OCR texts were generated from scans of 16th-century Fraktur (blackletter) printing. No manually corrected transcription of this work appears to exist in digital form as of February 2026. The texts are useful for:
- Keyword searching and frequency analysis
- Identifying structural patterns (chapter divisions, recipe formats)
- Cross-referencing with the 1500 Small Book text

They are NOT suitable for:
- Character-level linguistic analysis without extensive manual correction
- Direct quotation without visual verification against page images
- Computational paleography (the OCR layer, not the images, is what we have)
