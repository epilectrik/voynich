# Theophilus Presbyter — *De Diversis Artibus*

**Negative-control corpus for the 8D recipe-matcher framework.**

Use this to test whether the 8D matcher (C1882-C1888) detects alchemy/distillation specifically, or any medieval procedural text generically. If Theophilus chapters produce confident matches against Voynich folios at rates indistinguishable from Pseudo-Lull, the recipe-correspondence claim weakens.

## What this is

Theophilus's *De Diversis Artibus* (also titled *Schedula Diversarum Artium*) is a c. 1100-1125 Latin technical manual on three medieval arts:

- **Book I** — Painting and pigments (~40 chapters: color preparation, gold leaf, fresco)
- **Book II** — Glassmaking (~31 chapters: furnace construction, glass production, windows, mosaic)
- **Book III** — Metalwork (~96 chapters: forge construction, smelting, casting, soldering, gilding, niello, gem-setting, organ pipes, bell casting) — the operationally richest and best test material

The author writes as a Benedictine monk and was likely Roger of Helmarshausen (German goldsmith, fl. 1107).

## Why this corpus for negative control

| Property | Theophilus | Pseudo-Lull (positive corpus) | Same? |
|---|---|---|---|
| Era | ~1120 | ~1330 | similar century-range |
| Document type | Technical procedural manual | Technical procedural manual | yes |
| Language | Latin | Latin (+ Catalan in SISMEL) | yes |
| Operational vocabulary | heat, vessel, transfer, monitor, iterate | heat, vessel, transfer, monitor, iterate | yes (overlapping) |
| Domain | metalworking/glass/painting | alchemy/distillation | **NO** |
| Expected matcher behavior | minimal matches if matcher is alchemy-specific | confident matches | controls the test |

## Files

| File | Contents |
|---|---|
| `theophilus_hendrie_1847.pdf` | Robert Hendrie's 1847 Latin-English parallel edition facsimile (26 MB) |
| `theophilus_hendrie_1847.txt` | DjVu OCR plain text (~1 MB, 22,278 lines) — Latin and English alternating |
| `README.md` | This file |

## Source

Downloaded from Internet Archive: <https://archive.org/details/theophiliquietru00theouoft>

Robert Hendrie, *Theophili qui et Rugerus, presbyteri et monachi, libri III de diversis artibus, seu Diversarum artium schedula: opera et studio R. Hendrie*. London: John Murray, 1847.

This is the **first English translation** of Theophilus, with Latin and English in parallel. The standard modern translation (Hawthorne & Smith, 1979) is borrow-only on Internet Archive — use Hendrie 1847 for fully-public access. Both editions translate the same critical Latin text.

## Structural roadmap

OCR is decent but has typical artifacts (page headers, broken hyphenation, footnotes inline, paratext in the first ~1700 lines).

| Section | Line range | Notes |
|---|---|---|
| Front matter / Hendrie's preface | 1-1700 | English preface, paratext, illustrations — skip |
| Book I Latin (CAPUT I-XL) | 2242-? | "INCIPIT LIBER PRIMUS" at L2242 |
| Book I English (CHAPTER I-XL) | 2278-4283 | "EXPLICIT LIBER PRIMUS" at L4283 |
| Book I notes | 4315-7212 | "NOTES TO BOOK I" — exclude from matcher |
| Book II Latin | 7213-? | "INCIPIT LIBER SECUNDUS" at L7213 |
| Book II English | 7520-9147 | "EXPLICIT LIBER SECUNDUS" at L9147 |
| Book II notes | 9178-10536 | exclude |
| Book III Latin | 10537-? | "LIBER TERTIUS" at L10537, "INCIPIT" at L10540 |
| Book III English | 11337-20528 | longest section, ~96 chapters |
| Book III notes | 20528-end | exclude |

Chapter markers in both Latin (CAPUT N.) and English (CHAPTER N.) make per-chapter segmentation tractable.

## Use case

**Pre-registered negative-control test for the 8D matcher** (C1882-C1888). See `phases/PHASE_*/scripts/_theophilus_negative_control.py` once authored. Run the unchanged 8D feature extractor against Theophilus chapter-units; match against all 82 Currier B folios; pre-register failure criteria before looking at output.

Binding falsification criteria (per expert-advisor + crazy-expert convergence, 2026-05-14):
- ≤2/30 confident matches (ratio ≥ 1.15) expected
- Mean ratio ≤ 1.10
- Permutation p ≥ 0.10
- Matches should NOT concentrate on the Section B alchemy folios already matched to PL

If any of these fail, demote C1882-C1956 from "operational correspondence" to "structural attraction to medieval procedural text."

## Status

**Acquired 2026-05-14.** Not yet tested. Next step: chapter-segmentation and running the negative-control test.
