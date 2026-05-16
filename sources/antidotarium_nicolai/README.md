# Antidotarium Nicolai

Late 11th / early 12th-century Latin pharmacopoeia compiled in the
Schola Medica Salernitana. Approximately 150 compound preparations
(electuaries, syrups, ointments, troches), alphabetically arranged.
First printed Venice 1471. Foundational compound-pharmacy reference
text used across medieval Latin Europe.

## Source

W.S. van den Berg (ed.), *Antidotarium Nicolaï: Ms. 15624-15641
Kon. Bibl. te Brussel*, N.V. Boekhandel en drukkerij voorheen
E.J. Brill, Leiden, 1917. Parallel Middle Dutch + Latin (text of the
1471 Venice first printed edition) on facing pages, with critical
apparatus citing manuscripts L1, L2, F1, F2, NM.

PDF mirror: <https://www.dbnl.org/tekst/_ant004wsva01_01/_ant004wsva01_01.pdf>

## Why this source

Voynich Section S (pharmacy section) appears to be compound-pharmacy
material per C1995. Brunschwig 1500/1512 was triaged out (project memory
`section_s_source_genre_gap.md`). The Antidotarium is the canonical
12th-century Latin compound-pharmacy reference and the most likely
match candidate for Section S folios. Section B alchemy material is
already matched (Pseudo-Lull Testamentum); the Antidotarium tests
whether the same matching method extends to Section S, or whether
pharmacy material requires a different feature set than operational
alchemy.

## Files

| File | Description |
|------|-------------|
| `antidotarium_nicolai_vandenberg_1917.pdf` | Source PDF (DBNL, 1.6 MB, 360 pages) |
| `antidotarium_nicolai_pdftotext.txt` | Raw `pdftotext -layout` extraction (UTF-8, 14k lines) |
| `antidotarium_nicolai_latin.txt` | Paragraph-marked Latin (with §N labels) |
| `antidotarium_nicolai_dutch.txt` | Paragraph-marked Middle Dutch (parallel reference) |
| `antidotarium_nicolai_latin_plain.txt` | **Primary corpus.** Clean Latin, one paragraph per line, footnote/folio markers stripped |
| `_extract_latin.py` | Extractor pipeline |
| `_stats.py` | Corpus statistics |

## Corpus volume

```
Latin paragraphs : 231
Total chars      : 123,235
Word tokens      : 17,344
Unique types     : 3,771
Top vocab        : et (1247) cum (368) ān (333) in (328) ad (214)
                   recipe (138) quod (127) vel (118) valet (89) datur (83)
```

For comparison: Brunschwig 1512 is 51,237 lines (~25× larger). The
Antidotarium is compact because it is a recipe digest, not an
encyclopedia. 17K tokens is adequate for token-frequency / chapter-level
matching.

## Extraction pipeline

The DBNL edition is parallel Dutch/Latin on facing pages. The pipeline:

1. Restrict to recipe body (skip front matter L1-1567 and glossary L10474+)
2. Drop page-break markers and standalone folio numbers
3. Drop footnote blocks (lines starting with `N)` and their indented continuations)
4. Merge consecutive text lines into paragraphs (pdftotext puts blank lines between every text line)
5. Classify each paragraph as Latin/Dutch by vocabulary scoring + pharmacy symbol detection
6. Post-clean: strip Dutch footnote bleed-through (`ontbreekt`, `NM:`, `F1:`, etc.) by truncating paragraphs at the first contamination marker

## Known limitations

- A few paragraphs have residual fragmentation where pdftotext layout
  inserted a paragraph break mid-sentence — joining is heuristic.
- Recipe numbering from the edition (1.-133.) is not currently preserved
  in the plain-text output. If recipe-level alignment is needed for
  matching, re-extract with header annotations from `_extract_latin.py`.
- Quantity/proportion symbols (ʒ ℈ Ѕ ān̄ ℞) are preserved in plain-text
  but may need normalization for some downstream tools.

## Status

Corpus is ready for matching. Section S folio alignment not yet
attempted. The recommendation in memory note
`project_section_s_source_genre_gap.md` was that Section S source
matching requires this text — that gap is now closed.
