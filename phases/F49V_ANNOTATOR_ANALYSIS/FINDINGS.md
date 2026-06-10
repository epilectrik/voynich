# f49v Margin Column: Evidence for a Later Annotator (the Manuscript's First Analyst)

**Date:** 2026-06-08 | **Status:** COMPLETE (exploratory close-read, written up at user request)
**Class:** measurements Tier-2-grade (reproducible below); interpretation Tier 3–4 (clearly marked)
**Origin:** user hypothesis ("the margin characters were added by someone later, looking at the
lines and making notes") tested against ink, structure, and the scholarly record.
**Image source:** Beinecke MS 408 IIIF, image id 1006171 (f49v), full resolution 2935×3769
(`https://collections.library.yale.edu/iiif/2/1006171/full/full/0/default.jpg`).

---

## Summary

The f49v left-margin column (26 single Voynichese characters + Western digits 1–5) is, on the
combined evidence, **a single later annotation layer — a reader's analysis attempt — not an
authorial instructional apparatus.** This directly challenges the interpretive half of C497
("the manuscript teaches its own reading"), whose *structural* observations remain valid.

---

## Measurements

### M1. The six illegible labels resolved from ink

The transcription (and the project's 2026-01 visual pass) records six labels as `*` (lines 6,
11, 14, 15, 18, 21). At full resolution, **five of the six are the same glyph**: a small
"2"-shaped curl of the EVA r/s family (ambiguous between r and s — which is exactly why careful
transcribers starred it); line 15's mark is a small curl as well, possibly y. The full column:

```
f | o r y e ʂ | k s p | o ʂ y e ʂ | ʂ | p | o ʂ y e ʂ | d y s k y
       1 2 3 4 5
```

### M2. The column is a numbered, REVISED, repeating frame

- A five-slot frame `o · y e ·` repeats three times, separated by gallows characters
  (f | k s p | p), with the digits 1–5 indexing the slots of the first repetition and a coda
  `d y s k y`.
- **The frame is revised between passes:** pass 1 slot 2 = `r`; passes 2 and 3 slot 2 = the
  curl. Lines 14–15 (doubled curls) read as insertion/correction. This is drafting behavior —
  iteration on a unit-inventory hypothesis — not copying and not decoration.

### M3. The labels are independent of their lines (kills "exemplification")

Tested against all 20 securely-read label/line pairs:
- label = line-initial character: **1/20**
- label = line-final character: **0/20**
- several lines contain **zero** instances of their own label character (the `r` line has no r,
  the `y` line no y, the `e` line no e, the `k` line no k, both `p` lines no p, the `s` line
  no s). Whatever the pairing is, the lines do not exemplify the labels. (Whether the
  zero-containment is itself non-random is untested — see follow-ups.)

### M4. Ink and pen: the margin column patterns as ONE population, distinct from the text

Full-resolution pixel analysis (ink = pixels >45 below local background median; stroke width =
median horizontal dark-run):

| population | ink px | mean ink value | R−B (redness) | stroke width |
|---|---|---|---|---|
| digits 1–5 | 6,536 | 80.1 (darker) | 41.0 | **1.0 px** |
| character labels | 8,082 | 87.4 | 39.1 | **1.0 px** |
| main text | 346,809 | 101.6 (lighter) | 28.4 | **2.0 px** |

The digits and the Voynichese labels share a **finer pen (~half stroke width)** and a
**redder-browner, darker ink** than the main text, and pattern *with each other* on every
measure. Caveats: single JPEG, one lighting pass, margins fade differently than text blocks;
"different pen + ink" is necessary but not sufficient for "different hand, later."

### M5. The naive-cryptanalysis frequency story fails; the structural story fits

- His numbered five are NOT the top-5 raw-frequency characters (on f49v: o=2, e=6, y=8, s=12,
  r=14) — he was not doing al-Kindi frequency counting.
- But the class structure is right: every numbered character is a small/ordinary-shaped letter;
  the unnumbered dividers (f, k, p) are gallows. And his coda lands on the real terminal
  family: on f49v, `y` is the #1 word-final character, and `-dy` is the #1 word-final unit in
  the manuscript, with `-ky`/`-sy` its siblings — `d y s k y` reads naturally as the endings
  inventory (d-y, s-y, k-y).

## Scholarly prior

Jim Reeds (transcription commentary, via voynich.nu transliteration file): the digits "seem to
be in the same hand as the **folio numbers**" — i.e., the later foliator. The character column
has traditionally been *impressionistically* called contemporaneous; M4 is, to our knowledge,
the first measurement, and it groups the characters with the digits, not the text.

---

## Interpretation (Tier 3–4, hold loosely)

**The column is one later annotation layer: a reader — plausibly the foliator — attempting to
analyze the script.** The reconstruction of his method, each step grounded above: (1) he
separated the gallows class from the small-letter class (M2 dividers — correct structure);
(2) he drafted a candidate inventory of "basic" small letters, numbered 1–5, and revised it on
a second pass (M2 revision); (3) he identified the terminal family (-dy/-ky/-sy; M5 coda —
correct structure); (4) the attempt ends with this page — the closed-small-alphabet assumption
(cipher-key thinking, natural for a digit-literate 15th–16th c. reader confronting a script
full of digit-shaped glyphs) cannot survive contact with the script's combinatorial depth.
Under this reading f49v preserves **the earliest recorded analysis of the Voynich manuscript**,
parallel in genre to the f1r marginal alphabet key — and its results, in modern terms, were:
morphological classes correctly separated, terminal family correctly identified, no key found.

## Implications for the constraint base

- **C497's interpretive half is under substantive doubt.** The structural observations stand
  (26 L-labels, alternation, ordinals, exclusive vocabulary). The reading "instructional
  apparatus / demonstrates morphology for training / the manuscript teaches its own reading"
  assumed the column is authorial; M3 (no exemplification) + M4 (different pen/ink, grouping
  with the foliator's digits) + the Reeds prior point to a later annotation layer instead.
  C497 annotated in `context/CLAIMS/currier_a.md` and flagged in the INDEX row.
- Arguments elsewhere that leaned on "the manuscript teaches itself" (e.g., as an anti-hoax
  point: "why teach readers of a prop?") are weakened and should not be reused without noting
  this finding. Other anti-hoax legs (HT coupling, f75r external counts, C2077) are unaffected.
- The "f49v ordinal groups may map to the atom system" idea (fresh-eyes list, 2026-06-08) is
  CLOSED: the ordinals are the annotator's, not the author's.

## Follow-ups (cheap → decisive)

1. **Paint-layering: RUN 2026-06-08 — INCONCLUSIVE BY GEOMETRY.** At full resolution, the
   margin column has NO genuine contact with the green pigment: 1 stroke-grade ink pixel of
   3,263 falls within the (dilated) green zone; the column floats in clean parchment. A first
   pass with a loose ink threshold produced an apparent "labels-over-paint vs text-under-paint"
   controlled result — RETRACTED within minutes: the in-wash "ink" was wash mottling (darkness
   116 vs true strokes' ~47) and the "text-under-paint" population was largely dark paint
   itself. Lesson logged: stroke-grade thresholds + visual verification before any layering
   claim. The test cannot decide layering on this folio; M3/M4/Reeds remain the evidence base.
2. **Digit paleography:** the form of the `4` (open-top in our crops) is datable; compare with
   the foliation digits formally.
3. **Zero-containment statistics:** is "lines avoid their own label character" (6-ish of 20 at
   zero) beyond char-frequency chance?
4. **Decisive:** multispectral / ink-composition data for the f49v margin (Beinecke MSI program;
   McCrone 2009 already showed foliation ink differs from text ink). A curatorial request, not
   a script.

## Reproduction

All analyses inline (this exploration was off-books); the load-bearing ones:
- glyph reading: IIIF full-res, label-column band x≈[678,762] of 2935, blob-detected 26 rows
  (`evidence/f49v_blobs.jpg`, `evidence/f49v_mid.jpg` = lines 10–16 close-up)
- ink statistics: bands numerals x[600,676], labels x[678,762], text x[776,1886]; ink threshold
  bg−45; stroke = median horizontal run (M4 table)
- label/line independence: H-track transcript, f49v, 20 secure pairs (M3)
