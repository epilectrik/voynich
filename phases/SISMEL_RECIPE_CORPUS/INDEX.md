# Phase: SISMEL Recipe Corpus Build

> **Source correction (2026-09-27, scan-verified — `sources/sismel_testamentum/OCR_CORRECTIONS.md`):** III.19 reads *"per quatre vegades **aliter** ix vegades"* = "four times, **otherwise** nine times". The quotation *"… aliter broicé e triblé; e aprés ix vegades"* used below is an OCR splice from the capon passage three lines lower. ×4 and ×9 are **alternative counts for one repeated step**, not two sequential phases; any reading below that treats them as "×4 first, then ×9" is void. The count facts (C1889, C2034) are unaffected. See `context/SYSTEM/STRATEGIC_REVIEW_2026-09-27.md` §2.

**Status:** INFRASTRUCTURE-COMPLETE (refinement ongoing)
**Started:** 2026-04-24
**Purpose:** Convert the SISMEL Pereira-Spaggiari 1999 OCR into a structured, paragraph-aligned recipe corpus that can replace the 1566/1567 reconstruction as the authoritative source for all Testamentum-based correspondence work.

## Background

The pre-2026-04-24 recipe pipeline used `sources/pseudo_lull_testamentum/testamentum_complete_latin.txt` — a reconstruction from the 1566 Cologne / 1567 Mercuriorum / 1600 Basel early-modern prints. Head-to-head comparison against SISMEL on Ch. 18 and Ch. 19 Liber Mercuriorum revealed the print tradition carries substantive corruption (dropped ingredient names, mangled operational criteria, numerical errors — 1566 "per novem vices" vs SISMEL "per quatuor vices"). See `context/SOURCES.md` and memory entry `project_sismel_authoritative.md`.

SISMEL offers the critical Latin + parallel Old Catalan text of Oxford CCC 244, with full apparatus. This phase builds the infrastructure to exploit it.

## Goal

Produce `sismel_corpus.json` with per-chapter, per-paragraph records:

```json
{
  "part": "III",
  "chapter_num": 18,
  "title_latin": "De aquis et medicinis pro humano corpore",
  "title_catalan": "Del aygues e medicines per le cors humanal",
  "folio_refs": ["f. 63va"],
  "paragraphs": [
    {
      "idx": 1,
      "latin": "Nunc dicemus composicionem aque potabilis simplicis...",
      "catalan": "Ara direm la composició de l'aygua potable simpla...",
      "apparatus": []
    }
  ],
  "source_spreads": ["285_L", "285_R"]
}
```

## Unlocks

Once this corpus exists, these PENDING_TESTS entries become executable:

- **PT-016** — Paragraph↔step alignment (Phase 641's 8D battery was null vs 1566; re-run against SISMEL)
- **PT-017** — t-atom gloss revision (near-significant at p=0.13 with N=16; paragraph-level N should disambiguate)
- **PT-001 / PT-013** — Atom profiles & Catalan-grounded glosses at expanded scale
- **PT-014 / PT-015** — f82r, f112v gloss replication
- **PT-020 / PT-021** — Three-part vocabulary + leaf-level tests
- **PT-022 through PT-029** — Count-encoding typology validation (incl. f78r/f108r/f108v fresh predictions)
- **PT-023b** — Testamentum-internal recipe-DAG / presupposition encoding

## Layout Facts (verified from `sismel_testamentum_assembled.txt`)

- **L pages (verso) = Latin critical text**
- **R pages (recto) = Old Catalan** (author's native language)
- Part III "TESTAMENTUM · III" running header spans spreads ~272-340
- Chapter numbers appear on their own line (e.g., `                    18                    f. 63va`)
- Body has margin line numbers at multiples of 5
- Apparatus block follows `─────────────────────────` at page foot

## Scripts

| Script | Purpose |
|--------|---------|
| `s1_parse_sismel.py` | Parse assembled text → raw per-page structured records |
| `s2_build_recipe_corpus.py` | Merge pages into chapter records, pair Latin + Catalan |
| `s3_validate_corpus.py` | Alignment checks, stats, spot-check exports |

## Scope

- **In scope:** Parts I, II, III (all numbered chapters in the main body) plus their critical apparatus.
- **Out of scope (for now):** Introduction, appendices, indices. Those are reference material accessible via the PDF.

## Results (2026-04-24 first build)

| Metric | Count |
|--------|-------|
| Chapters extracted | 179 (I: 97, II: 30, III: 47+ variants) |
| Paragraph-aligned (Latin count = Catalan count) | 127/179 (71%) |
| Matched folios present in corpus | **16/16** ✓ |
| Matched folios paragraph-aligned | 13/16 |
| Remaining off-by-one mismatches | f82v (Ch 28), f112r (Ch 11), f80r (Ch 21) |

## Key findings (2026-04-24)

### Finding 1: Chapter-numbering discrepancy between 1566 Cologne and SISMEL critical

1566 Cologne split SISMEL's multi-sub-recipe chapters into separately numbered chapters:

| 1566 Cologne | Content | SISMEL |
|--|--|--|
| Cap. XIX (Mercuriorum) | Primary aqua vitae + honey/wax reflux | Ch. 19 primary (III.19.0) |
| Cap. XX | Constitutione secunde aquae (capon depluma) | Ch. 19 sub-recipe b (III.19.1) |
| Cap. XXI | Constitutione tertie aquae | Ch. 19 sub-recipe c (III.19.2) |
| **Cap. XXII** | **Constitutione quarte aquae (lunaria + 3-day sealed)** | **Ch. 19 sub-recipe d (III.19.3)** |
| Cap. XXIII | Constitutione quinte aquae | Ch. 19 sub-recipe e (III.19.4) |
| Cap. XXIV | Constitutione sexte aquae (bones) | Ch. 19 sub-recipe f (III.19.5) |

After Cap. XXIV, 1566 chapters continue ~5 ahead of SISMEL numbering. Practica has its own ~2-chapter offset.

### Finding 2: Content-based remap of 16 matched folios

Using Latin-content cosine similarity between the 1566 chapter text and every SISMEL sub-recipe (results: `results/match_remap.md`):

| Folio | 1566 Ch | SISMEL best | Notes |
|-------|---------|-------------|-------|
| f75r | III.19 | **III.19.0–19.3** (all high) | f75r content strongly associates with Ch 19 overall; sub-recipe resolution inconclusive via pure fingerprinting |
| **f82r** | **III.22** | **III.19.3** (sim 0.468) | **Lunaria + 3-day sealed — confirmed as Ch 19 sub-recipe d** ⭐ |
| f82v | III.28 | III.21 (sim 0.491) | Vessels — SISMEL Ch 21 "De vasis" |
| f77v | III.27 | III.20 (sim 0.431) | Furnaces — SISMEL Ch 20 "De furnis et vasis" |
| f76r | II.18 | II.16 (sim 0.751) | Practica offset by 2 |
| f83r | II.9 | II.7 (sim 0.609) | Practica offset by 2 |
| f84r | II.14 | II.12 (sim 0.517) | Practica offset by 2 |
| f76v | III.15 | III.16 (weak, sim 0.171) | Unclear, likely still Ch 15 |
| f112v | III.1 | III.1 (sim 0.494) | Numbering matches |
| f116r | III.4 | III.4 (sim 0.585) | Numbering matches |
| f103r | III.16 | III.16 (sim 0.445) | Numbering matches |
| f112r | III.11 | III.11 (sim 0.391) | Numbering matches |
| f79r | III.12 | III.12 (sim 0.461) | Numbering matches |
| f81v | III.18 | III.18 (sim 0.470) | Numbering matches |
| f80r | III.21 | (extract failed) | 1566 Ch 21 content lives in a merged page header "XIX-XXII"; cannot isolate |
| f107r | III.44 | (extract failed) | Same issue |

### Finding 3: Ch 19 is a multi-folio recipe cluster

**f75r** (primary aqua vitae) **and f82r** (lunaria+3-day) **both map to sub-recipes of SISMEL Ch. 19.** This is the first direct evidence that **different Voynich folios encode different sub-recipes of the same SISMEL chapter** — a sub-recipe-level granularity signal the chapter-level pipeline could not have produced.

### Finding 4: Recto/verso leaf-level continuation supported

f82 leaf spans SISMEL Ch 19 → Ch 21 (lunaria sub-recipe on recto, vessel specification on verso). Both sit in the same thematic cluster (post-aqua-vitae workshop operations + their apparatus). That's PT-021-style leaf-level continuation at *chapter-cluster* granularity.

### Finding 5: Catalan preserves counts Latin drops

Spot-check of Ch. 19 surfaced **a reading preserved only in the Catalan**:

> Catalan: *"per **quatre** vegades aliter broicé e triblé; e **aprés ix vegades**"*
> (= "by **four** times, alternatively 'pounded and ground'; and then **nine** times")

The SISMEL Catalan preserves BOTH iteration counts (4x for honey-wax primary reflux, then 9x for a follow-up). This reconciles f75r's **two count clusters** (4 identical `qokedy` at L13 + the 10-cluster at L36-L41 = 1+9 cycles) with the recipe text — both counts are explicitly present in the Catalan. The 1566 Latin has only "nouem vices" (9x); the critical Latin has only "per quatuor vices" (4x). Only SISMEL's Catalan contains both.

This is direct vindication of the PT-022c/d finding and strengthens the recipe-DAG / presupposition-encoding hypothesis (PT-023b) substantially.

## Known limitations

- **Sub-recipe conflation.** When OCR lost blank lines between sub-recipes within a single chapter (e.g., "Confeccio secunde aque:", "Confeccio tercie aque:", ...), those merge into one paragraph. Fine-grained split on these phrase-markers is a planned refinement.
- **Off-by-one paragraph mismatches** in ~30% of chapters are almost all single-paragraph boundary differences between the two language OCRs. Manual cleanup per chapter as needed.
- **Title truncation on some chapters** where the title wraps 3+ lines or contains unusual punctuation. Single-line wrap works; multi-wrap can drop the tail.

## Files

| File | Purpose |
|------|---------|
| `scripts/s1_parse_sismel.py` | Page-level parser |
| `scripts/s2_build_recipe_corpus.py` | Chapter-assembly + Latin/Catalan pairing |
| `scripts/s3_validate_matched.py` | Check all 16 matched recipes present, export reference MD |
| `scripts/s4_extract_counts.py` | Extract numerical counts from each matched chapter |
| `scripts/s5_split_subrecipes.py` | Split chapters on "Confeccio N aque:" etc. markers |
| `scripts/s6_remap_matches.py` | Content-based remap of 1566→SISMEL sub-recipe IDs |
| `results/sismel_pages.json` | Raw per-page records |
| `results/sismel_corpus.json` | Structured chapter corpus |
| `results/sismel_subrecipes.json` | Chapter→sub-recipe expansion (189 records from 179 chapters) |
| `results/sismel_corpus_summary.md` | Build stats |
| `results/matched_recipes.md` | Readable reference for our 16 matched recipes |
| `results/matched_recipes_status.json` | Machine-readable alignment status |
| `results/matched_recipe_counts.json` | Per-chapter numerical-count extraction |
| `results/match_remap.json` / `match_remap.md` | 1566→SISMEL sub-recipe remap |
