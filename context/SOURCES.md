# Source Texts Index

Inventory of primary/secondary source texts available under `sources/`. Check here before asking the user whether we have a text — chances are we already do.

**Last updated:** 2026-05-15

---

## Pseudo-Lull Testamentum — TWO EDITIONS (don't confuse them)

### `sismel_testamentum/` — Pereira-Spaggiari 1999 (SISMEL critical edition) ⭐ **AUTHORITATIVE**

**This is the canonical recipe-text source for all correspondence work.** Use this, not the early-modern prints, whenever the Latin or Catalan recipe wording matters.

Bilingual Latin (verso) + Old Catalan (recto) critical edition of the Oxford Corpus Christi College 244 base codex. Includes full critical apparatus, sigla (Ol, Oc, K, α, β, π, Ms, G), introductory essays, and appendices.

| File | Contents |
|------|----------|
| `sismel_testamentum.pdf` | 809 pages, full book facsimile (75.9 MB) |
| `sismel_testamentum_assembled.txt` | Full OCR (2.5 MB, 38K lines), per-spread markers |
| `scans/` | 808 page JPGs + cover.jpg |
| `ocr/` | 808 per-page `.txt` files |
| `scripts/assemble.py`, `build_pdf.py` | Rebuild pipeline |

**Structure:** Part I Theorica (97 ch.) · Part II Practica (31 ch.) · Part III Liber Mercuriorum (~46 ch., alchemical recipe core). Author colophon 1332 London St. Katherine.

**Use for:** recipe-level correspondence work (PCI-V2, RECIPE_FOLIO_CORRESPONDENCE, ATOM_GLOSS_RECIPE_VALIDATION), apparatus-backed comparisons, dating and manuscript-stemma work.

### `pseudo_lull_testamentum/` — Early-modern prints (1566/1567/1600) ⚠️ **SUPERSEDED**

Reconstruction from 1566 Cologne / 1567 Mercuriorum / 1600 Basel prints. **Known to carry substantive textual corruption** relative to the critical text — dropped ingredients (e.g., *lunaria*, *brescis*/honeycomb), mangled operational criteria, occasional numerical errors (Ch. 19 reflux count "9x" here vs "4x" in SISMEL), and missing sub-recipes.

Prior correspondence work (all phases before 2026-04-24) used these files. **New correspondence work must use SISMEL.** When re-checking an old match, compare against SISMEL before treating the old alignment as load-bearing.

| File | Contents |
|------|----------|
| `testamentum_1566_seville.pdf` | 1566 Seville Latin edition facsimile |
| `testamentum_complete_latin.txt` | Reconstructed Latin text |
| `testamentum_complete_english.txt` | English translation (from the reconstructed Latin) |
| `mercuriorum_1567.pdf` | 1567 Liber Mercuriorum separate printing |
| `libelli_chemici_1600.pdf` | 1600 chemical corpus containing Testamentum |

**Keep for:** traceability of prior phase work; comparing early-modern vs critical readings; the English translation (until SISMEL-based English is produced).

---

## Distillation Curriculum (Voynich correspondence backbone)

### `puff_von_schrick/` — Michael Puff, *Büchlein von den ausgebrannten Wässern* (1501 Ulm)

Early-printed German distilled-waters manual. 83 chapters, material registry + therapeutic indications. Ch. 71 (Küdreck) is the only animal chapter.

| File | Contents |
|------|----------|
| `puff_1501_ulm.pdf` | Facsimile |
| `puff_1501_german.txt` | Early New High German OCR |
| `puff_1501_english.txt` | English translation |
| `pages/` | Per-page scans |

### `brunschwig_1500/` — Brunschwig *Small Book* (1500 Strasbourg)

**AKA:** *Liber de arte distillandi de simplicibus* / *Kleines Distillierbuch*. First printed distillation manual combining method + material. 3 parts: methods/apparatus, illustrated herbal, disease register.

| File | Contents |
|------|----------|
| `brunschwig_1500_small_book.pdf` | Facsimile |
| `brunschwig_1500_corrected.txt` | Cleaned OCR (use this) |
| `brunschwig_1500_english.txt` | English translation |
| `brunschwig_1500_text.txt` | Raw OCR |
| `DO_NOT_USE_raw_ocr_brunschwig_1500.txt` | Named for a reason |

### `brunschwig_1512/` — Brunschwig *Large Book* (1512)

**AKA:** *Liber de arte distillandi de compositis* / *Grosses Distillierbuch*. Expanded sequel to the Small Book. Assembly is COMPLETE (see memory).

| File | Contents |
|------|----------|
| `brunschwig_1512_assembled.txt` | Assembled full text (51,237 lines) — **primary** |
| `brunschwig_1512_english.txt` | English translation |
| `brunschwig_1512_corrected.txt` | Cleaned OCR |
| `brunschwig_1512_large_book.txt` | Raw source OCR (92,557 lines) |

---

## Negative-control Corpora (matcher audit)

### `theophilus/` — Theophilus Presbyter, *De Diversis Artibus* (~1120, Hendrie 1847 ed.)

Medieval Latin technical manual on **painting (Book I), glassmaking (Book II), and metalwork (Book III)**. Operationally rich (heat/vessel/transfer/monitor/iterate vocabulary) but from a different domain than alchemy/distillation. Used as negative control for the 8D matcher (C1882-C1888): if Theophilus chapters produce confident folio matches at rates indistinguishable from Pseudo-Lull, the matcher is generic-procedural-text not alchemy-specific.

| File | Contents |
|------|----------|
| `theophilus_hendrie_1847.pdf` | Hendrie's 1847 Latin-English parallel edition facsimile (26 MB) |
| `theophilus_hendrie_1847.txt` | DjVu OCR plain text (1 MB, 22,278 lines) — Latin/English alternating |

**Status:** Acquired 2026-05-14. Not yet tested. See `theophilus/README.md` for chapter line ranges and binding test criteria.

---

## Pharmacy Corpora (Section S candidates)

### `antidotarium_nicolai/` — Antidotarium Nicolai (van den Berg 1917 DBNL ed.)

12th-century Salernitan compound pharmacopoeia. ~150 alphabetically-ordered recipes for electuaries, syrups, ointments, troches. First printed Venice 1471. Foundational Latin compound-pharmacy reference text. Acquired 2026-05-15 to close the Section S source gap flagged in `project_section_s_source_genre_gap.md` (Brunschwig 1500/1512 triaged out as wrong genre).

| File | Contents |
|------|----------|
| `antidotarium_nicolai_vandenberg_1917.pdf` | DBNL source PDF (1.6 MB, 360 pages, parallel Latin + Middle Dutch) |
| `antidotarium_nicolai_pdftotext.txt` | Raw `pdftotext -layout` UTF-8 extraction |
| `antidotarium_nicolai_latin_plain.txt` | **Primary corpus.** 231 Latin paragraphs, 17,344 tokens, 3,771 types |
| `antidotarium_nicolai_latin.txt` | Same with §-paragraph labels |
| `antidotarium_nicolai_dutch.txt` | Parallel Middle Dutch (reference) |
| `_extract_latin.py` | Heuristic Latin/Dutch separator with footnote stripping |

**Status:** Acquired, extracted, footnote-cleaned. 8D matcher baseline run 2026-05-15 confirmed TUNED_DIMS doesn't port — see C2026. Genre is pure compound-pharmacy (ingredient lists with proportions); operational-channel matcher needs replacement for pharmacy text.

### `mesue_grabadin/` — Mesue's Grabadin (1602 Lyon Opera + 1513 Venice incunable)

13th-century Latin pharmacopoeia attributed to Pseudo-Mesue. ~400 compound preparations organized by preparation type (electuaries, syrups, oils, ointments, troches, pills). **"The most popular compendium of drugs in medieval Europe"**. Acquired 2026-05-15 per crazy-expert recommendation — Mesue is the practicing-apothecary reference (vs Nicolai's curated teaching canon), more plausible Voynich-compiler source.

| File | Contents |
|------|----------|
| `mesue_1602_lyon_djvu.txt` | 1602 Opera raw ABBYY OCR (3.7 MB, 97K lines, Roman type, rough OCR) |
| `mesue_1513_venice_djvu.txt` | 1513 Venice incunable OCR (1.5 MB) — **gothic typeface, OCR is poor**, kept for reference (contains Grabadin + Antidotarium Nicolai together) |
| `mesue_grabadin_liber_primus.txt` | **Primary corpus part 1.** Antidotarium / compound preparations. 7,517 paragraphs, 249K tokens |
| `mesue_grabadin_liber_secundus.txt` | **Primary corpus part 2.** De Appropriatis / specific applications by body part. 1,001 paragraphs, 80K tokens |
| `mesue_grabadin_latin_full.txt` | Combined L1+L2 with book markers (2.6 MB) |
| `_extract.py` | Extractor pipeline |

**Status:** Acquired, segmented into the two Grabadin books. **329K tokens total** (~19x the Nicolai corpus). OCR is rough but workable for keyword search and lexical comparison. Not yet aligned to Voynich Section S folios. Includes Petrus Abano's *Additio* (early 14th-c. supplementary recipes) interleaved with primary Mesue text.

---

## Other Alchemical Texts

### `rupescissa/` — Johannes de Rupescissa, *Liber de consideratione quintae essentiae* (14th c.)

Quintessence doctrine — foundational to Pseudo-Lull Testamentum alchemical program.

| File | Contents |
|------|----------|
| `rupescissa_latin_1561.txt` | Latin (1561 edition) |
| `rupescissa_latin_quintae_essentiae.pdf` | Latin facsimile |
| `rupescissa_german_cpg233.pdf` | German translation (CPG 233) |
| `rupescissa_complete_translation.txt` | Full English |
| `rupescissa_english_translation.txt` | English extract |

### `codicillus/` — Pseudo-Lull *Codicillus* (companion alchemical treatise)

| File | Contents |
|------|----------|
| `codicillus_complete_latin.txt` | Full Latin |
| `codicillus_complete_english.txt` | Full English |
| `codicillus_channel_features.json` | Pre-computed recipe-channel features |
| `transcription_p*.md` | Per-page transcription notes |

---

## Cipher-Manuscript Comparanda (15th c.)

### `alchymey_teuczsch/` — *Alchymey teuczsch* (1426, Bavaria)

Partially enciphered German alchemy compilation. Heidelberg Cod. Pal. germ. 597. **README only** — no OCR yet.

### `fontana/` — Giovanni Fontana cipher manuscripts (c. 1420-1455)

*Bellicorum instrumentorum liber* (BSB Cod.icon. 242) and other Fontana works using invented cipher script. Contemporary Venetian comparandum. **README only** — no OCR.

### `hartlieb/` — Johannes Hartlieb, *Buch aller verbotenen Kunst* (1456)

Treatise on forbidden arts. CPG 478. **README only** — no OCR.

---

## Historical / Prosopographical Context

Letters, chronicles, and academic records — useful for dating, authorship, and circulation questions.

| Dir | Text | Era |
|-----|------|-----|
| `piccolomini/` | Aeneas Silvius Piccolomini *Briefwechsel* vol. 1 (1431-1445) | pre-papacy letters |
| `celtis/` | Conrad Celtis *Briefwechsel* (1934 edition) | humanist correspondence |
| `schedel/` | Hartmann Schedel *Briefwechsel* (1452-1478) | Nuremberg physician/chronicler |
| `tichtel/` | Johannes Tichtel diary (1477-1495) | Viennese physician |
| `ebendorfer/` | Thomas Ebendorfer *Chronica Austriae* | Austrian chronicle |
| `vienna_medical_faculty/` | *Acta Facultatis Medicae* (1436-1501) | university records |

---

## Video / Modern Secondary

### `transcripts/`

Transcripts of talks and documentary videos about the Voynich — external commentary, not primary sources.

- `yale_voynich_transcript.txt`
- `voynich_engineer_ru_transcript.txt`
- `voynich_manuscript_solved_an_engineer's_translation_transcript.txt`
- `voynich_materiality_transcript.txt`
- `voynich_ru.ru.srt`

---

## Other

### `brunchwig-zip/` — legacy zipped artifacts

Older Brunschwig 1500 derivation work. Mostly superseded by `brunschwig_1500/` proper. Keep until consolidation pass confirms no unique content.

---

## Quick "do we have it?" lookup

| If you want... | Check... |
|----------------|----------|
| Recipe text for correspondence (Latin + Catalan, authoritative) | `sismel_testamentum/sismel_testamentum_assembled.txt` ⭐ |
| Recipe text for correspondence (English) | `pseudo_lull_testamentum/testamentum_complete_english.txt` (from superseded reconstruction; use with caution) |
| Critical apparatus / stemma / folio refs | `sismel_testamentum/sismel_testamentum_assembled.txt` |
| Distilled-water material registry | `puff_von_schrick/puff_1501_german.txt` (+ english) |
| Brunschwig Small Book (1500) | `brunschwig_1500/brunschwig_1500_corrected.txt` |
| Brunschwig Large Book (1512) | `brunschwig_1512/brunschwig_1512_assembled.txt` |
| Quintessence doctrine | `rupescissa/rupescissa_latin_1561.txt` |
| Companion alchemical treatise | `codicillus/codicillus_complete_latin.txt` |
| 15th c. cipher comparandum | `fontana/README.md`, `alchymey_teuczsch/README.md` |
| Physician/humanist biographical context | `piccolomini/`, `schedel/`, `tichtel/`, `celtis/` |
| Out-of-domain procedural text (matcher negative control) | `theophilus/theophilus_hendrie_1847.txt` |
| Compound-pharmacy reference (Section S candidate) | `antidotarium_nicolai/antidotarium_nicolai_latin_plain.txt` |
| Practicing-apothecary polypharmacy reference (Section S candidate, larger corpus) | `mesue_grabadin/mesue_grabadin_latin_full.txt` |
