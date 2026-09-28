# Aberdeen Bestiary (Aberdeen, University Library, MS 24): per-page Latin corpus and collation

This directory holds a page-level Latin text corpus and a collation with conjugate leaves, built for use as a **codicological negative control**. The Aberdeen Bestiary is a real manuscript (England, c. 1200; lapidary added in the later 13th century) with known quire structure, known losses, and a known change of hand.

| File | What it is |
|---|---|
| `aberdeen_pages.json` | 206 records, f1r..f103v in order: `folio, leaf, side, latin_raw, latin_norm, n_words` (+ `title`, `has_transcription`, `linebreak_style`) |
| `collation.json` | 15 quires with folio membership, leaf positions, conjugate pairs, status and verbatim evidence |
| `extraction_stats.json` | counts, rule counts and examples for every normalization rule |
| `linebreak_decisions.json` | every ambiguous line-break decision (folio, fragments, model score, join/split), for auditing |
| `linebreak_validation.json` | held-out accuracy of the line-break model |
| `spot_check.txt` | spot-check output (see below) |
| `fetch_pages.py` | polite cached crawler (writes `html/`) |
| `extract_latin.py`, `linebreak_model.py` | builds `aberdeen_pages.json` |
| `validate_linebreaks.py`, `spot_check.py` | validation and audit |
| `build_collation.py` | builds `collation.json`; pulls every quote verbatim from `html/` and asserts it exists |
| `html/` | raw cached HTML: `f1r.html` .. `f103v.html`, plus `_index`, `_codicology`, `_help`, `_introduction`, `_about`, `_policies` |
| `ref/` | `folio-marks.jpg` (the site's leaf-mark table), `codicology_text.txt`, the 2002 Wayback copy of the old codicology page |

Rebuild: `python fetch_pages.py` (only fetches what is not cached), `python extract_latin.py`, `python validate_linebreaks.py`, `python build_collation.py`, `python spot_check.py [--all]`.

---

## Source, access, and terms

- **Source:** University of Aberdeen, *The Aberdeen Bestiary* digital edition. Index: https://www.abdn.ac.uk/bestiary/ms24. Pages: `https://www.abdn.ac.uk/bestiary/ms24/f{N}{r|v}`. The index links exactly f1r..f103v (206 pages; verified, no gaps or extras).
- **Accessed:** 2026-09-27. Fetched with `requests` and a descriptive `VoynichResearch-AberdeenBestiaryCorpus/1.0` User-Agent (see `fetch_pages.py`), with a 1.5 s delay between requests. All 206 pages returned HTTP 200 (`fetch_log.txt`). Nothing is fetched twice.
- **Credits** (from `introduction.php`): "The text was transcribed and translated, supported by a commentary and introduction." The 1996 team included "Morton Gauld and Colin McLaren, both consultants for the transcription and translation" and "Jane Geddes, commentary". The site adds: "The transcription and translation remain the same but the commentary has been updated where necessary."
- **Licence / terms: the site states no explicit licence for the transcription text.** These are the only rights-related statements it shows:
  - Each folio page has a download button titled **"Download image for personal, teaching or research purposes"**. The help page says: **"Download image for personal, research or teaching purposes"**.
  - Each folio page has a "Copyright" icon and a footer "Policies" link, both pointing to https://www.abdn.ac.uk/collections/about/policies/. That page is only an index of collection policies (Access, Digitisation, etc.) and contains no licence text.
  - Footer: "University Collections, Library, University of Aberdeen, Bedford Road, Aberdeen, AB24 3AA The University of Aberdeen is a charity registered in Scotland No.SC013683".
  - Help page: **"It is not part of the project to provide a definitive edition of the text of the Bestiary, but to help readers by providing a transcription and translation of the text."**

  Treat the transcription as © University of Aberdeen, for research use. **This repository is mirrored to a public GitHub remote.** Consider whether `html/` and the full-text JSON should be committed before pushing. Nothing here has been committed.

---

## Extraction method

**Where the Latin is.** Each folio page has a tab block `<dd id="transcription">` containing `<div class="transcription"><h2>Transcription</h2> …Latin… </div>`, followed by a separate `<div class="translation">`. A copy of the English translation also appears in `<div id="translation">` beside the image. Only `div.transcription` is read, with its `<h2>` removed. Pages without that block (blank leaves, full-page pictures) get `latin_raw = ""`. The translation is never used as a fallback.

**`latin_raw`** is the panel text verbatim, with all editorial marks kept. Only whitespace is tidied: CRLF becomes LF, runs of spaces are collapsed, and ends are trimmed. The site's editorial conventions (`help.php`), quoted:
> "The original capitalisation is retained, but capitals have been added for personal and place names … The original punctuation … is represented by comma, full stop and question-mark; a colon has been inserted before quotations. Suggested readings are in [ ]. Variants from other Bestiary texts (eg Ashmole 1511 and Patrologia Latina 176) are added where they indicate a corruption, elucidate a meaning and replace excised text. They are represented as [A: PL:]"

The site also marks every manuscript line end with `\`. That convention is undocumented but consistent.

**`latin_norm`** is lowercase, with only a–z and single spaces. u/v and i/j are left as given. It is meant to approximate *what is written on the page*. The rules, in order (see `extract_latin.py`):

| Rule | Pattern | Action | Count |
|---|---|---|---|
| B2 | `[a inserted]` | keep the letters (interlinear insertion present in the MS) | 2 |
| B1 | in-word `x[ab]y`, `x[ab]`, `[ab]y` (1–4 lowercase letters, no siglum) | keep the letters, drop the brackets (mostly editor-supplied letters: `[e]st`, `pen[n]arum`, `[N]ux`) | 47 |
| B3 | any other `[...]` / `(...)` | **remove**, leaving a hard word boundary (A:/PL: variants, emendations such as `cecetur [secetur]`, supplied words, supplied rubrics `[De parandro]`, text supplied for excised areas `[excised, A: ...]`, `deleted`/`expuncted` notes, `[......]`, `[10]`) | 325 |
| H | `ab-\ cd`, `ab-cd` | join (a hyphen touching a removed bracket goes with the bracket, so the fragment stands alone) | – |
| L1 | whitespace + `\` | word boundary | – |
| L2 | `ab\cd` | join (mid-word line break) | – |
| L3 | `ab\ cd` | ambiguous; decided by the segmentation model below | 2,778 |

**Line-break ambiguity (important).** On most pages the site writes a mid-word break as `par\dis` and a between-word break as `et\ vulpibus`. On **49 pages, f41r–f64v (quires G, H, I) plus f65r and f70r**, every break is written `\ `, so `sur\ git` (one word) and `fractis\ cervicibus` (two words) look the same. The explicit-convention pages also contain a few mid-word breaks written `\ ` (for example `poste\ rior`, `ada\ mas`).

`linebreak_model.py` decides each case with a unigram word model plus a character 6-gram backoff. It is trained on tokens whose boundaries are certain. It joins `ab\ cd` if log P(`abcd`) − [log P(`ab`) + log P(`cd`)] > 1.5. A right-hand fragment with an initial capital is always a boundary.

- **Validation** (`linebreak_validation.json`): trained on even leaves and tested on odd leaves, and vice versa. The test set is the explicit-convention pages, where truth is given by the site's convention. At threshold 1.5 the model has **96.3% agreement on 2,831 breaks, with net word-count bias 0** (52 false joins, 52 missed joins). This is a lower bound, because several "false joins" are genuine mid-word breaks that the site wrote as `\ `.
- **Result:** 1,108 ambiguous breaks on the space-style pages (404 joined), and 1,670 on explicit pages (30 joined; all inspected; all are mid-word breaks such as `ada\ mas` or `poste\ rior`, or the compound `quodam\ modo`). Expect roughly one word-boundary error per space-style page, with no systematic effect on `n_words`.

**Counts** (`extraction_stats.json`):

| | |
|---|---|
| pages | 206 (f1r–f103v) |
| pages with a transcription block | 200 |
| **pages with text** | **199** |
| empty pages | f3v, f4r, f6r, f6v (blank); f4v, f5r (full-page pictures, no text); **f45r** (see problems) |
| **total words** (`latin_norm`) | **43,800** |
| words per page, min / median / max | **26 (f61v) / 233 / 344 (f101v)**; mean 220.1 |

**Spot check** (`spot_check.txt`). Stored fields were compared with the page's transcription panel, read by an independent path (plain regex over the HTML, no BeautifulSoup), and with the translation panel shown to confirm it was not what was extracted. Pages checked: f1r, f7r, f18v, f55v, f94r, f103v, f6r and f45r. All match the page. `python spot_check.py --all` repeats the comparison for **all 206 pages: 0 mismatches**. Sample, f7r: page panel `Incipit liber de naturis bestiarum. De leonibus et pardis et tigribus, lupis et\ vulpibus, …` → norm `incipit liber de naturis bestiarum de leonibus et pardis et tigribus lupis et vulpibus …`. Sample, f55v (space-style): `sur\ git. Huius figu\ ram … Po\ testatem … ani\ mam` → `surgit huius figuram … potestatem … animam`.

**Known problems and limits:**
1. **f45r has no Latin on the site.** It is a text page ("the vulture, continued") and the site gives an English translation, but its transcription block is empty. It is recorded as empty, and **its text is missing from the corpus**. f44v ends "…qui corpus\" and f45v begins "carnalibus desderiis…".
2. **f20r**: text lost to the excision of the sheep miniature on f20v is supplied in brackets. On three lines the transcriber closed a bracket without opening one (`…vera cum recto]`, `…speciebus]`, `…operati]`). The start of the supplied text on those lines cannot be known, so up to about 3 lines of supplied (non-manuscript) text may remain in f20r's `latin_norm`.
3. **f21r**: a stray `[ecus` (evidently `[p]ecus`, Isidore's "hoc pecus") is kept as the fragment `ecus`.
4. **Bracketed dittographies** are kept by rule B1 (for example `g[ra]ravi`, `reli[li]gionis`, `advenien\[en]tem`). In-word bracket use on the site is mixed: mostly supplied letters, some superfluous ones. About 47 cases in all; see `rule_examples.B1_inword`.
5. **Excision lacunae**: supplied text for excised areas is removed, so pages with excisions show gaps and word fragments (f13r, f13v, f20r, f28r, f28v, f39v, f54v, f73r). This is intended, because the corpus follows what is on the page.
6. **Site artifacts in `latin_raw`**: f60r ends with `', '', '',` (a data-export artifact on the site), f62r has `[,i>PL, …]`, and f100v has entry numbers `7 Mardonicus…`. All are stripped from `latin_norm` by the letters-only rule. The bold headings on f18v and f19r (`<b>Item de natura canum.</b>`) are kept as plain text.
7. **Transcription quirks** are kept as given: run-together words on f18v (`regemab`, `agminefacto`), and f95r opens with a bracketed repetition of the end of f94v (removed by B3).
8. **Page-boundary splits**: a word broken across pages counts on both pages (for example f7r ends `…Leonis vocab`).

---

## Collation (`collation.json`)

### Sources

- **Digital edition** (primary; all quotes pulled verbatim by `build_collation.py`):
  - `codicology.php`, "Gatherings, quire marks, folio marks". It quotes M. R. James: *"The quire system was examined by MR James when the book was being rebound and he was able to produce the following analysis of the gatherings: A8 (wants folio 2, 8); B8 (4,5); C8 (4,8); D8 (4,5); E8-L8 (1); M8; N8; O6; P4 (4)."* It also says: *"Some are missing with the result that the sequence runs -,B,C,D,E,F,G,H,I,K,-(folio missing),M,N."* and *"Although there were eight folios only the first four needed marking because they were folded with the last four."*
  - The per-folio **Commentary** notes, which record every quire letter and leaf ("folio") mark.
  - The **Folio Marks** table image (`ref/folio-marks.jpg`), which gives explicit ranges: B f.7–f.12v, D f.19–f.24v, E f.25–f.32v, F f33–f40v, G "f.42–f.48v" [sic], I f.57–f.64v, L f.73–f.79v, M f.80–f.87v.
- **W. B. Clark, *A Medieval Book of Beasts* (2006), Cat. no. 1**, read through Internet Archive full-text-search snippets (item `medievalbookofbe0000clar`, lending-restricted). It gives **no collation formula**. The codicology line reads: *"302 x 210 (185 x 110/115), 1+103 folios … Rebound by Brit. Mus. 1931-32 … Assembly marks in a variety of forms in lead point, most in outer margins, lower corners, ff. 21, 26-28, 33-36, 41-44, 57, 58, 60, 73, 75, 80-83 (forms shown on the Website). Quire signatures in capital letters are later additions; 2 leaves blank (ff. 3v-4, 6-6v), 2 leaves glued together (ff. 56v-57, 93v-94)."* It also lists the missing leaves: *"… antelope - elephant (betw. ff. 9v and 10); crocodile - parandrus (betw. ff. 15v and 16); dog (betw. ff. 18v and 19); bullock - horse (betw. ff. 21v and 22); great fish and fish 'carpet' (betw. ff. 72 and 73)."*
- **M. R. James, *A Catalogue of the Medieval Manuscripts in the University Library, Aberdeen* (Cambridge, 1932)** was **not consulted directly**: it is paywalled on Cambridge Core and not on Internet Archive or HathiTrust in open form. It is known here only through the site's quotation.
- **Not found**: any quire diagram, and any library-catalogue (CALM) record with a collation. The Wayback copy of the 2002 site's codicology page has the same wording. The site's "Open Book View" pairs openings (for example `compare/f6v-f7r`), not bifolia, so it is not evidence of conjugacy.

### How the formula closes

The formula as quoted gives 24 leaves for A–D (f1–f24). "E8-L8 (1)" is ambiguous. If every quire E–L wanted leaf 1, E would lack its first leaf, but f25r carries both the quire mark 'e' and the first-leaf mark (one "match stick"). The same holds for F (f33r), G (f41r), I (f57r, mark 'C') and M. Only L lacks its first leaf: f73r carries "Folio mark 'll' … This represents folio 2 of quire 'L', but folio 1 is missing". So **"E8-L8 (1)" = E, F, G, H, I, K, L of eight, with L wanting leaf 1.**

The quire letters then fall exactly where the arithmetic puts them: e f25r, f f33r, g f41r, h f49r, I f57r, K f65r, (L lacking) f73–79, M f80r, N f88r, O f95r, P f101r. That gives A–D 24 + E–K 48 + L 7 + M 8 + N 8 + O 6 + P 3 = **104 leaves** against **103 foliation numbers**. The difference is **f93**, which is two leaves pasted back to back and foliated once (f93r: "This page is glued to f.93v"; codicology: "f.93r is glued to f.93v"). N = f88–f94 has 7 folio numbers but 8 leaves, which matches **N8**.

**f56 is also two pasted leaves** (f56r: "Thus f. 56r and 56v are actually two sheets stuck back to back"; codicology: "The two pages after the phoenix are blank and glued together"). That would give H **nine** leaves, which "E8" cannot accommodate. H is therefore left **undetermined**.

The resulting physical text block is 105 leaves (plus 1 flyleaf per Clark). Clark's page references for the pasted pairs ("56v-57, 93v-94") do not fit the site's foliation, since f56v, f57r, f93v and f94r all carry text. The pasted pairs are located from the site's own per-page notes.

### Result

Conjugacy uses the regular-quire model on which James's formula is written: in a quire of 2n leaves, leaf k pairs with leaf 2n+1−k. Leaf ids `56a`/`56b` and `93a`/`93b` are the two physical leaves of f56 and f93 (a bears the recto page, b the verso page).

| Quire | Folios | Structure | Positions 1…n (– = wanting) | Conjugate pairs | Singletons (conjugate lost) | Status |
|---|---|---|---|---|---|---|
| A | f1–f6 | 8 wants 2, 8 | 1, –, 2, 3, 4, 5, 6, – | [2,5] [3,4] | 1, 6 | determined |
| B | f7–f12 | 8 wants 4, 5 | 7, 8, 9, –, –, 10, 11, 12 | [7,12] [8,11] [9,10] | – | determined |
| C | f13–f18 | 8 wants 4, 8 | 13, 14, 15, –, 16, 17, 18, – | [14,18] [15,17] | 13, 16 | determined |
| D | f19–f24 | 8 wants 4, 5 | 19, 20, 21, –, –, 22, 23, 24 | [19,24] [20,23] [21,22] | – | determined |
| E | f25–f32 | 8 | 25…32 | [25,32] [26,31] [27,30] [28,29] | – | determined |
| F | f33–f40 | 8 | 33…40 | [33,40] [34,39] [35,38] [36,37] | – | determined |
| G | f41–f48 | 8 | 41…48 | [41,48] [42,47] [43,46] [44,45] | – | determined |
| **H** | f49–f56 | James 8; 9 physical leaves (49–55, 56a, 56b) | – | **null** | – | **undetermined** |
| I | f57–f64 | 8 | 57…64 | [57,64] [58,63] [59,62] [60,61] | – | determined |
| K | f65–f72 | 8 | 65…72 | [65,72] [66,71] [67,70] [68,69] | – | determined |
| L | f73–f79 | 8 wants 1 | –, 73, 74, 75, 76, 77, 78, 79 | [73,78] [74,77] [75,76] | 79 | determined |
| M | f80–f87 | 8 | 80…87 | [80,87] [81,86] [82,85] [83,84] | – | determined |
| N | f88–f94 | 8 (f93 = 2 leaves) | 88, 89, 90, 91, 92, 93a, 93b, 94 | [88,94] [89,93b] [90,93a] [91,92] | – | determined |
| O | f95–f100 | 6 | 95…100 | [95,100] [96,99] [97,98] | – | determined |
| P | f101–f103 | 4 wants 4 | 101, 102, 103, – | [102,103] | 101 | determined |

That is 45 conjugate pairs in 14 determined quires. A–N are the original 12th-century quires. The lapidary begins in a later hand halfway down **f94r**, the last leaf of N and still on the original parchment (f94v: "This folio marks the end of the high quality twelfth-century parchment"). It continues on the added quires O and P (f95r: "From f.95r the quality of the parchment changes …"; "Quire 'P' begins here" on f101r).

**Supporting quotes by quire** (all verbatim in `collation.json` → `evidence`):
- **A**: no quire mark ('-'). B begins at f7r ("The start of quire B is indicated by the letter 'b' in the centre of the lower margin."). Lost leaf 2 falls between f1v (day 2) and f2r (day 5): f1v "Two illustrations of the Creation sequence are missing…", and Clark "Missing Text: Creation days 3, 4". Consistency check: the quire's central opening is f3v/f4r, the two facing blank pages ("This page and f.4r were deliberately left blank and probably intended to be glued together.").
- **B**: f8r "There is a '*' on the top right corner to indicate the second folio of quire B." The lost central bifolium falls at f9v/f10r: "…pages for the antelope, unicorn, lynx, griffon and the illustration of the elephant are missing between f.9v and f.10r."
- **C**: f13r "…a very faint 'c', indicating the start of the next quire." Losses at f15v/f16r ("there are pages missing for leocrota, crocodile, manticore, and start of parander") and after f18v ("After this page a leaf is missing…").
- **D**: f19r "a quire mark (d) at the bottom"; f21r "Folio mark of three nested chevrons" (third leaf); f21v "After f.21v two leaves are missing…".
- **E / F / G**: 'e' f25r, 'f' f33r, 'g' f41r. Leaf marks 1–4 on f25r–f28r (match sticks), f33r–f36r (horizontal match sticks) and f41r–f44r (chevrons).
- **H**: 'h' f49r; 'I' f57r; codicology "In quire H (f.49r-f.56v)…"; f56 is two leaves (quotes above).
- **I**: f57r "Quire indicator 'I'… Folio mark 'C'"; f58r "CC"; f59r "The folio mark (which should be 'CCC') is missing."; f60r "Folio mark 'CCCC'".
- **K**: f65r "Quire mark 'K' at bottom centre."; bounded by L's second leaf at f73.
- **L**: f73r "Folio mark 'll'… This represents folio 2 of quire 'L', but folio 1 is missing."; f75r "folio mark 'llll'"; f72v "A page is missing after f.72v…".
- **M**: f80r "Quire mark … 'M', and folio mark '+'"; f81r "*"; f82r "Quire mark 'M'… Folio mark *"; f83r "* in circle".
- **N**: f88r "quire mark 'N'"; f93r/f93v glued; O begins at f95r ("Bottom right quire mark "0".").
- **O**: f96r "Folio marks "II II""; f97r "Folio mark "III""; P begins at f101r.

### What is uncertain

- **H is undetermined.** Its membership (f49r–f56v) is certain, but its leaf count (8 per James vs 9 physical) and conjugacy are not. No source says which leaf is additional, and no leaf marks are recorded for H.
- **"Determined" means determined by James's formula read on the regular-quire model, checked against marks and losses.** No source consulted gives a physical conjugacy check (a quire diagram, or stubs observed in the binding).
  - Independent corroboration of leaf positions: leaf marks on leaves 1–4 in B, D, E, F, G, I, L, M, O, and text losses exactly where the "wants" fall in A, B, C, D, L.
  - Quires with **no independent corroboration beyond James**: **K** (no leaf marks), **N** (depends on counting the pasted f93 pair as two leaves), and **P** (its lost 4th leaf is attested only by James; f103v ends on a complete sentence).
- The reading "E8-L8 (1)" = "L wants 1" is an inference, but the site's own leaf marks force it (see above).
- The site's leaf-mark table gives G as "f.42–f.48v". This is treated as a typo, since the 'g' and the first chevron are on f41r.
- Clark's references to the pasted leaves ("ff. 56v-57, 93v-94") are inconsistent with the site's foliation, as noted above.

Note: `context/SOURCES.md` (the repository's source inventory) has **not** been updated. Per task instructions, nothing outside this directory was modified.
