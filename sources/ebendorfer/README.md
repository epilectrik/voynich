# Thomas Ebendorfer: Chronica Austriae

## Source

- **Author:** Thomas Ebendorfer (1388-1464), Vienna University professor and theologian
- **Work:** Chronica Austriae (Chronicle of Austria)
- **Date range covered:** Origins to 1463; later sections (1450s-1460s) are partly in diary form
- **Language:** Latin
- **Critical edition:** Alphons Lhotsky (ed.), *Thomas Ebendorfer, Chronica Austriae*, MGH Scriptores Rerum Germanicarum, Nova Series, vol. 13 (Berlin-Zurich: Weidmann, 1967), 602 pp.

## Digital Sources

| Source | URL |
|--------|-----|
| Internet Archive (restricted) | https://archive.org/details/thomasebendorfer0000hera |
| openMGH digital edition | https://www.mgh.de/en/digital-mgh/openmgh/mgh-editions-in-openmgh |
| Direct download (TEI-XML ZIP) | https://data.mgh.de/openmgh/bsb00000693.zip |

## License

The text is in the public domain. TEI-XML annotations by MGH and Bavarian State Library (BSB) are distributed under [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/).

## Files

| File | Description |
|------|-------------|
| `ebendorfer_chronica_austriae.txt` | Full extracted plain text (~908 KB, 597 pages, ~16,000 lines) |
| `extracted/bsb00000693.xml` | Original TEI-XML from openMGH (2 MB) |
| `bsb00000693.zip` | Original downloaded ZIP archive |
| `_extract_text.py` | Extraction script (XML to plain text) |

## Context: Relevance to Voynich Research

Thomas Ebendorfer was a prominent Vienna University professor, contemporary with **Michael Puff von Schrick** (c. 1400-1473), who was at the height of his career at Vienna during the 1450s-1460s. Ebendorfer's chronicle provides:

- **First-person accounts** of Vienna University life and Austrian politics during the period when Puff von Schrick was active as a medical faculty member
- **Diary-form sections** from the 1450s-1460s with detailed contemporary observations
- **References to the University of Vienna** (universitas studii Wiennensis), its scholars, and institutional life
- **Political context** of Frederick III's reign, Austrian factional conflicts, and the broader environment in which Puff von Schrick operated

The chronicle's later books (particularly Liber Quintus, covering events through 1463) are the most relevant sections for establishing the intellectual and institutional context of mid-15th century Vienna.

## Structure

The Lhotsky edition page numbers are preserved as `[Page N]` markers in the text file:

- **Pages (1)-7:** Prologus
- **Pages 8-395:** Books I-IV (early Austrian history through ~1440s)
- **Pages 396-600:** Books IV-V (1440s-1463, diary sections)
- **Pages 601-602:** Anhang (Appendix: fragment from Cathalogus presulum Laureacensium)

## Extraction Notes

- Split words (hyphenated across line breaks in the critical edition) have been reconstituted using the `lemma` attributes from the TEI-XML markup
- Editorial additions in angle brackets (e.g., `<depinxi>`) are preserved as Unicode angle brackets
- Page numbers refer to the Lhotsky 1967 printed edition
- Each line in the text file corresponds to one line in the printed edition
