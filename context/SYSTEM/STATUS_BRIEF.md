# Status Brief — what currently stands (v7.29, 2026-09-28)

This page is the short, authoritative orientation to the current state of the model. Living documents written before
the September 2026 review may still present withdrawn claims as structure; where they conflict with this brief, this
brief and the generated registry win.

**Authority order:**
1. `context/CONSTRAINT_TABLE.txt` (generated): a constraint missing from it is dead; Tier 3 in it means demoted or
   speculative.
2. `context/CLAIMS/INDEX.md` rows: they give the reason for each status.
3. This brief.
4. Everything else.

Full record of the review: `SYSTEM/STRATEGIC_REVIEW_2026-09-27.md`. Changelog: `SYSTEM/CHANGELOG.md`.

---

## 1. Tier 0 (restated 2026-09-28, human sign-off)
> Currier B is written in a single, compact token grammar: 49 classes covering 69.5% of its tokens, organised by line
> with positional zones and word-boundary glyph coupling, and applied in folio units that share the grammar while
> carrying their own vocabulary. This structure is not reproduced by copy-and-modify generation or by the Naibbe cipher
> as published.

Basis: C121, C124 (as corrected); C956, C357; C1212, C1563 (with PHASE_761); C531, C1790; C2077, C2080.
Only C121 and C124 carry Tier 0 in the registry; the other basis rows are Tier-2 measurements. Fifteen rows that
still carried a leftover Tier-0 label (C670–C681, C747, C748, C750) were re-tiered to Tier 2 on 2026-09-28.

**Working interpretation (Tier 3):** the grammar is read as procedural notation (a family of programs for a
process). No current measurement distinguishes this reading from other constrained notations. The supports it used
to have (a kernel of core operators, closed-loop control, hazard avoidance, convergence) are withdrawn (section 3).

## 2. Measurements that stand (Tier 2 unless noted)
- **Grammar:** 49 classes, closed over the grammar's own 480-type vocabulary (the class map holds 480 types; some older
  rows say 479) (69.5% of B tokens; HT/UN defined by
  exclusion: C121, C124, C566, C740).
- **Line organisation:**
  - positional zones (C956);
  - line regularity (C357);
  - boundary glyph coupling, i.e. the last glyph of a token predicts the first glyph of the next (C1212, C1563). This
    is robust to spacing uncertainty and replicated on ZL (PHASE_761).
- **Word-ending routing (C2082):** a token's two-glyph ending predicts the next token's class beyond that coupling,
  above composition, zones and edge counts. Neither Naibbe nor Timm reproduces it.
- **Common-token zero bigrams reduce** to line composition, zones and boundary coupling (C2081). No prohibition layer
  remains.
- **Family preference:**
  - qo tokens are rich in the gallows k, and ok tokens in e (C1313);
  - qo tokens alternate with ch/sh tokens above composition (C549);
  - qok→ok/oke above composition (C2056).
- **Folio units:** shared grammar with folio-unique vocabulary (C531); no duplicate lines or paragraphs (C1790).
- **Occupancy:** 57.8% of folios end in their dominant macro-state (C074, measurement only).
- **Sequence structure beyond Markov:** the class-transition eigenstructure λ2/λ3 (C2061, C2067), established against
  a character 5-gram null. That null is window-blind (C2066), so the λ2/λ3 claim needs a re-check under N5 before it
  is relied on.
- **Physical layout:** the Aberdeen negative control shows the bifolium pipeline is SPECIFIC (PHASE_759). The
  Voynich bifolium contrast is reported but not registered.

## 3. Withdrawn or demoted — do not present as structure
| Construct | Status | Where |
|---|---|---|
| Kernel k/h/e as the "core" of the grammar | Superseded. At glyph level k shows nothing; e/bench signal = word-ending routing | C089 → C2082; C085, C103–C105 Tier 3 |
| "Closed-loop" control; operational purpose class | Tier 3, all four legs withdrawn | C171, C120 |
| LINK as a monitoring operator (38%) | 13.2% true density; morphological artifact of "ol" | C609, C1174 |
| 17 forbidden transitions, 5 hazard classes, hazard topology, "safety architecture" | Class level demoted; taxonomy imposed; 13 class-level violations; token zeros reduce | C783, C2060, C2063, C2081 (C957 superseded), C109 scoped, C216 |
| Convergence to STATE-C / MONOSTATE as a target; completion gradient | Withdrawn: occupancy only; no sequential convergence; section confound | C074 (T2 measurement), C079 and C084 (demoted), C1401–C1403 |
| Recovery architecture, execution clamp vs recovery freedom | Demoted: frequency shadow | C458, C105 |
| MIDDLE incompatibility "X% of pairs forbidden" | Demoted: sparsity denominator | C475 (and dependants) |
| Hub savings | Broken baseline (dead) | C476 |
| Testamentum chapter ↔ folio matching, recto/verso chapter pairs, section = book part | No correspondence signal; 20 rows Tier 3 | C2052, PHASE_762, C1882–C1975 triage |
| "Nobody has tested…" / closure banners ("ANALYSIS CLOSED", "explanatory saturation", "definitively irrecoverable") | Retired language | Strategic review §5 |
| EVA-letter statistics inside ch/sh, benched gallows, minim groups | Transliteration identities | C1440, C1209, C1207, C1484, C521 (partly orthographic) |
| e-run class claim C1225 | Parser artifact | PHASE_758 |
| R-series ordering, S/R division | Transcription artifact (retracted) | C434, C435 |
| REGIME as 4 crisp classes; REGIME = fire degree | Retired (the fire-degree gloss absorbed a sign flip; C1872 records the sign convention and stays live) | C1712, C2070 |
| C2031/C2032 section alternation contrast | Length-confounded | PHASE_755 |
| Mensural-notation hypothesis | Falsified | project memory; C2032 axis |
| Virtual-apparatus family as manuscript knowledge | Model diagnostics, not text facts | C1581–C1680 (review §5) |
| Rows resting on the constructs above (registry cascade, v7.26) | 31 demoted to Tier 3; 67 scope-tagged at Tier 2 (they measure a defined set, e.g. the 17 zero pairs or 'ol' tokens, not a hazard or monitoring layer) | See CHANGELOG v7.26 |

## 4. Rivals excluded (negative knowledge, scoped)
- Natural language written one token per word (C132, C2015, C2022). C130's "0.19% reference rate" is tainted and not
  relied on.
- Token ≈ word codes, atom-level polyalphabetic ciphers, three published decipherments (C1976, C2017).
- The Naibbe verbose homophonic cipher as published (C2080).
- Timm & Schinner copy-and-modify (C2077).
- A table walk over a coordinate lookup (C2079).
- **"B looks like a modern step notation":** not supported (C2083, PHASE_765).
  - On coupling, repetition and near-repetition, B is nearest to improvised gibberish, then constrained
    generators. Knitting notation and assembly code are the farthest classes.
  - In all 11 needlework books, the book's prose is nearer to B than its notation.
  - The "discrete operations" reading loses this support, not its standing.
- **Fragment labels as words of their plant's herbal page:** not found (C2084, PHASE_766).
  - In 13 visually matched pharmaceutical–herbal pairs, no fragment label recurs on its plant's herbal page,
    exactly or within one glyph. The test would detect 2 of 13 such pairs (80% power).
  - Labels as codes, contents or differently written names are not excluded.
- **Human-improvised gibberish** (Gaskell & Bowern, 38 modern volunteers): **tested at folio scale, unresolved**
  (PHASE_764).
  - B's boundary coupling exceeds most samples (AUC 0.825, 95% CI 0.71–0.92; variants 0.81–0.98), but the
    pre-registered bar was not met.
  - Meaningful text sits about as far below B (AUC 0.775) and is indistinguishable from gibberish on this statistic.
  - Descriptively, B is more rule-bound than both groups: stronger position-in-line dependence, more adjacent
    repetition and near-repetition, and a narrower word-initial choice.
- **Untested:** syllable- or word-level codebooks, modified verbose ciphers, the Rugg grille, and improvisation in a
  practised script at book scale. Excluding a rival is not
  evidence for the working interpretation.

## 5. How to annotate a stale citation (for anyone editing living docs)
- **The claim is still presented as structure:** rewrite the passage to state the current status in plain words and
  cite the governing row. Example: "(C475, demoted to Tier 3: the percentage measured sparsity, not prohibition)".
- **The citation is incidental:** add a short bracketed status note next to it. Example: "[C089 superseded by
  C2082]".
- **A whole section rests on a withdrawn construct:** put a one-line banner at its head, "**[Withdrawn v7.24/7.25 —
  historical; see STATUS_BRIEF §3]**", and leave the text for traceability. Do not delete history.
- **Never** upgrade a claim, add a new claim, or edit the registry (INDEX.md, CONSTRAINT_TABLE.txt) from a living doc.
  Registry anomalies go to the maintainer.
