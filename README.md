# Voynich Manuscript Computational Analysis

A long-running computational study of the Voynich Manuscript (Beinecke MS 408), focused on its Currier B text
(23,243 tokens on 83 folios in the H transcription). Every finding is recorded as a numbered constraint with an
evidence tier and a provenance chain; tests that carry weight are pre-registered before they are run, and the registry
is audited and corrected in the open.

> **September 2026 review.** The project re-tested its central claims against external controls and rival generators.
> Some held, several did not. This page states the current position. Documents written before the review
> (GUIDE, RECIPE_MATCHING, METHODS_AND_TOOLS) are kept for traceability and are marked as such. The full record is in
> [`context/SYSTEM/STRATEGIC_REVIEW_2026-09-27.md`](context/SYSTEM/STRATEGIC_REVIEW_2026-09-27.md) and
> [`context/SYSTEM/CHANGELOG.md`](context/SYSTEM/CHANGELOG.md).

---

## What the text reliably shows

**The project's Tier-0 conclusion** (restated 2026-09-28 by human sign-off) is itself a measurement:

> Currier B is written in a single, compact token grammar: 49 classes covering 69.5% of its tokens, organised by line with positional zones and word-boundary glyph coupling, and applied in folio units that share the grammar while carrying their own vocabulary. This structure is not reproduced by copy-and-modify generation or by the Naibbe cipher as published.

Until 2026-09-28 the Tier-0 sentence was the control-program reading; that is now a working interpretation (see Open hypotheses). The table lists the measurements behind it and others.

These are measurements, reproduced under controls and, where noted, on a second transcription.

| Property | Measurement | Basis |
|---|---|---|
| Words are linked across the word boundary | The last glyph of a word predicts the first glyph of the next: 0.23 bits beyond a within-line shuffle (0.24 on the ZL transcription); 0.215 bits at definite spaces alone | C1212, C1563; PHASE_761 |
| Vocabulary is tied to line position | Many common words occur only at line start or only at line end; zone dependence 0.17 bits beyond shuffle | C956; PHASE_757 |
| Prefixes alternate, endings run | Adjacent words share a prefix less often than chance (qo/ch/sh interleaving) and share an ending more often | C549, C1002; PHASE_760 |
| Repetition at chance | Adjacent identical words occur at the rate the line's own word mix predicts | PHASE_757 |
| Little order information | Beyond the boundary link, the previous word adds only 0.040 bits/token of predictive information — below the average of every Naibbe encryption of real text we tested | PHASE_757 |
| Sheets written as units | Pages on the same bifolium share vocabulary beyond distance and length effects; facing pages do not. A normal codex (the Aberdeen Bestiary) shows the reverse. Not yet registered: that waits on a second-transcription replication | PHASE_752, PHASE_759 |
| A slot-structured word form | Words decompose into prefix, core and ending whose parts interact pairwise, not as an arbitrary three-way code. Some internal regularities are spelling conventions of the script (EVA writes single glyphs as letter strings) | C1003, C1394; PHASE_754, PHASE_758 |
| A shared instruction grammar | 49 token classes cover the grammar's own 480-type vocabulary, which is 69.5% of B tokens; the rest is defined by exclusion | C121, C124 |
| Stable transcription | e-run lengths read consistently across transcriptions (κ 0.95–0.96); the Section B e-depth alternation and paragraph-channel gradient reproduce on a second transcription | PHASE_758 |

## Rivals tested and excluded

| Rival | Result | Basis |
|---|---|---|
| Naibbe verbose homophonic cipher (Greshko 2025), as published | Excluded on all 64 variants (2 code versions × 4 plaintexts × 2 layouts × 2 spacing × 2 noise settings). B has boundary coupling, chance-level repetition and line-position vocabulary that Naibbe lacks, and less order information than the average of every variant | C2080; PHASE_757 |
| Timm & Schinner self-citation generator | Excluded | C2077 |
| Natural language written one token per word | Excluded on several independent grounds | C132, C2015, C2022 |
| Token ≈ word codes; atom-level polyalphabetic cipher; three published decipherments | Excluded | C1976, C2017 |
| Tokens as coordinates read off a table (a "table walk") | No signature: adjacent words do not step through neighbouring cells | C2079; PHASE_760 |
| A language written syllable by syllable (Chinese-style, or an invented syllabary), one spelling per syllable | Excluded on unit inventory: B has 5,141 types per 20,000 tokens; syllable-written Mandarin, Vietnamese, Lahu and syllabified European texts have 685–1,338 | C2085; PHASE_767 |

Not yet tested: modified or coarser-unit ciphers (syllables written with spelling variation, word-level codebooks),
the Rugg grille.

## Open hypotheses

- **Working interpretation (Tier 3): procedural notation — a family of programs for a process.** No current
  measurement distinguishes this from other constrained notations. Until 2026-09-28 the Tier-0 sentence was the
  more specific "closed-loop, kernel-centric control programs". On re-check its supports did not hold: the only
  test behind "kernel-centric" was uninformative (it ranked single EVA letters, where "h" is half of one glyph, and
  its pass criterion did not depend on the data), and all four "closed-loop" legs — LINK monitoring, kernel
  intervention, hazard avoidance, convergence — were withdrawn (C171, C783, C2081, C1401–C1403). A fair glyph-level
  re-test (PHASE_763, pre-registered) came back mixed: the glyph k shows nothing special, and the one signal that
  passed — glyphs inside a word predicting the class of the next word — comes from the word's ending (its last two
  glyphs), not from a kernel (C2082).
- **Content: the Pseudo-Lullian *Testamentum* tradition.** Open. The chapter-level recipe matching did not survive
  controls: a metalwork treatise matches the same folios (C2052), no source matches better than its own shuffled
  features, the section mapping and recto/verso adjacency do not reproduce, and the headline permutation test was
  uninformative (PHASE_762). What remains is the date (parchment 1404–1438, inside the *Testamentum*'s circulation),
  the imagery, the granularity argument, and one specific coincidence: f75r, the only folio with a four-token repeat, is
  paired with III.19, the only chapter that says "four times". That pairing came from the generic matcher and needs a
  prospective test.
- **Encoding: cipher or notation.** Open beyond the excluded classes above.

## Retired in the September 2026 review

- "51 *Testamentum* chapters matched to 41 folios (96%), p < 0.0001": the matcher is generic and carries no
  chapter-level signal; the p-value test cannot distinguish noise (C1882–C1975 triage, PHASE_762).
- "17 forbidden transitions in 5 hazard classes" and the "three-level safety architecture" (withdrawn: C783 demoted,
  C2060, C2063, C2081).
- "100% coverage" (it is 100% of the grammar's own vocabulary, 69.5% of tokens).
- Atom glosses as locked meanings (k = heat, e = cool, …): they are role hypotheses; the e-depth "parameter" was a parser
  artifact (C171 demoted; PHASE_758).
- The "0.19% reference rate" and "glossolalia ruled out by 100% coverage".
- "Core model closed" and other closure language.

## Reading path

| Document | What it is |
|---|---|
| [WHAT_WE_CLAIM.md](WHAT_WE_CLAIM.md) | Current claims and limits with constraint citations |
| [STRATEGIC_REVIEW_2026-09-27.md](context/SYSTEM/STRATEGIC_REVIEW_2026-09-27.md) | The review, its tests and the forward plan |
| `phases/PHASE_753…763/INDEX.md` | The review's pre-registered tests, each with its pre-registration and results |
| [context/CLAIMS/INDEX.md](context/CLAIMS/INDEX.md) and [CONSTRAINT_TABLE.txt](context/CONSTRAINT_TABLE.txt) | The full registry; the generated table is authoritative for live rows and tiers |
| [GUIDE.md](GUIDE.md), [RECIPE_MATCHING.md](RECIPE_MATCHING.md), [METHODS_AND_TOOLS.md](METHODS_AND_TOOLS.md) | Pre-review documents (May 2026), kept for traceability |

## Status

| | |
|---|---|
| Live constraints | 1,892 (Tier 0: 2, Tier 1: 38, Tier 2: 1,682, Tier 3: 166, Tier 4: 4) |
| Research phases | 767 |
| Method | Pre-registration for load-bearing tests; negative controls; external rival generators; test designs audited before lock by a separate statistics-only reviewer (same model, restricted context — a rigor check, not independent confirmation) |

## Data

Transcriptions: the EVA interlinear file (H track primary; other tracks for cross-checks) and the ZL 3b transliteration
(Zandbergen–Landini, 2025). The Voynich Manuscript is held by the Beinecke Rare Book & Manuscript Library, Yale University
(MS 408); manuscript and transcription data are in the public domain. Third-party code used in tests (the Naibbe cipher)
is cited in its phase and not redistributed.

## License

This analysis is provided for research purposes. The Voynich Manuscript itself is in the public domain.
