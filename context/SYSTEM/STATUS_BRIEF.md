# Status Brief — what currently stands (v7.39, 2026-09-30)

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
- **The e-run dial is set above the word** (C2086, PHASE_769).
  - With the word frame, position, paragraph length, section and hand fixed, the choice of e vs ee still varies
    by folio, shared across different words (z 4.3; confirmed on ZL and on runs both transcribers read alike).
  - There is no per-procedure (paragraph) setting.
  - It survives removal of the preceding token's two-glyph ending (C2087, PHASE_770), so neighbour context
    combined with folio vocabulary does not produce it.
  - Its shape over the page is unresolved under the pre-registered rule (the gate failed narrowly). Descriptively,
    static page-setting models fit poorly, but no mechanism is distinguished.
  - Sharing with ch/sh, k/t or the minim count is unresolved (the test is underpowered).
  - No carry-over across page turns is detected, but that test is uninformative.
  - Its source (content, writing session, pen, copying) is not identified.
- **Minim counts** (1 vs 2+, ain vs aiin) are read alike by H and ZL (kappa 0.97, PHASE_770 design check); the
  older F transcription reads extra minims (kappa 0.42 against H) and is not used for minim statistics.
  e-run lengths are reliable (kappa 0.95-0.96, PHASE_758).
- **Labels' initial o** (C2088, PHASE_771; ZL; MIXED / UNRESOLVED, fragile).
  - Label o-words are not "o added in front of an ordinary word": w_add 0.00, and ≤ 0.03 in every analysis.
  - With the primary references they are not a pure dropped-q qo class (w_qo 0.19, CI up to 0.42), though the qo
    weight depends on how the references are weighted.
  - They sit nearest ordinary o-words, but no mixture of the three length-matched references fits (p 0.0005). There
    are fewer o-l and o-k than the best fit.
  - The zodiac-led departure may be an AZC property.
- **Line-edge forms at drawing breaks** (C2089, PHASE_771; ZL; UNRESOLVED).
  - Words beside a `<->` break sit between mid-line and line-edge profiles (edge index 0.37 to 0.74).
  - Descriptively, articulated starts follow a break at 57–69% of the line-start rate.
  - Line-final *-m* follows the line end, not the break.
  - No mechanism is distinguished.
- **Zodiac labels are not a repeated per-sign set** (C2090, PHASE_772; ZL; partly unblinded).
  - Most labels occur in no other sign: 77% at N1, 65% at N2. A 1–30 set repeated in every sign (degree or day
    numbers) is excluded under the modelled spelling variation.
  - Repeats lean within-sign, but PALETTE was not called.
  - Partial inventories, affixed or running counts, names and descriptions remain.
- **Occupancy:** 57.8% of folios end in their dominant macro-state (C074, measurement only).
- **Class-level sequence reduces to the boundary rules** (C2094, PHASE_776). Fix each word's edges, the previous
  word's two-unit ending and the page's composition, and the class-pair dependence left is +0.004 bits (at most about
  0.009), below every class chain fitted to B (≥ +0.016). What carries the dependence beyond own edges is the ending
  routing (C2082).
  - The eigenstructure of C2061/C2067 is real against a character 5-gram but is **not shown** to be sequence beyond
    the boundary rules: the routing-preserving null reproduces 97% of λ2's excess over the shuffle floor. That reading
    is Tier 3; the measurements stand.
  - With C2091 (no recurring 5-token phrase) and C2093 (rank-level neighbours independent within ending contexts), the
    three searches for sequence in B all come back to the boundary rules.
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
- **Syllable writing, or a syllable codebook, with one spelling per syllable:** tested and excluded on unit
  inventory (C2085, PHASE_767).
  - B has 5,141 types per 20,000 tokens. The syllable-written controls (Mandarin Pinyin, Vietnamese, Lahu Si and
    five syllabified European texts) have 685–1,338.
  - Syllable texts need more than 16 random spellings per syllable to reach B's vocabulary.
  - This does not say B's tokens are words or language.
- **A whole-word code with one spelling per word, of a text that repeats its phrases:** excluded (C2091,
  PHASE_774).
  - B's P-text has no within-line 5-token sequence that recurs at all: 0 windows, against an exact permutation null
    mean of 0.04. B-fitted first-order generators usually give 0 too.
  - Every tested plaintext with 8 or more repeated 5-word windows would show them: pharmacy prose, six NT
    translations, and the recipe, alchemy and verse segments.
  - Not excluded: two or more spellings per word, stem codes of low-repetition text, letter-level ciphers, lists,
    names and meaningless text.
  - With interchangeable spellings, repeat statistics mostly go blind. Merges recover hidden units only in special
    cases (C2092).
- **"The word-boundary rule is a cipher key":** no signature (C2093, PHASE_775; detection-only, no exclusion).
  - Re-labelling tokens by rank within the previous ending gives a negative key gain on B, like every no-key control.
  - The test misses some keyed ciphers, so this is not an exclusion.
  - Descriptively, once glyph edges and folio composition are fixed, B's neighbour dependence among frequent tokens is
    small, and within ending contexts it is at null.
- **"One glyph per word is the message, the rest rule-built filler":** no payload at the word start (C2095,
  PHASE_777).
  - Repeated 7-runs of the first or second glyph unit within lines, under an exact null that keeps the junction
    coupling and the two-unit routing and scrambles the start symbol: second unit z7 1.6 (clean NONE), first unit 3.3
    (the pre-registered residual band, not a payload call, source unidentified); every payload control gave ≥ 18.
  - Excluded at the second unit for every tested plaintext, also with up to 10% of symbols corrupted; at the first unit
    for noise-free payloads only. Not excluded: subsets of words, several positions, short-token carriers, units larger
    than letters, homophonic spellings, end-of-word positions (descriptive only).
- **Table-and-grille generation (Rugg): tested, NOT EXCLUDED as a method** (C2096, PHASE_778).
  - The published configuration's partial fits are excluded: no configuration as Hyde & Rugg describe it reaches B's
    composition, and every one is outside on edge-glyph coupling (z ≥ 139) and line-zone dependence (z ≥ 19.6).
  - One fitted variant each in the extended and steelman families is not excluded under the locked rule: adjacent
    repetition at chance and B's cross-folio trigram excess at z 2.5–2.7 (above all or nearly all 2,000 members, below
    the 3.0 bar), while B is outside the same ensembles on order information and line-zone dependence by 10 to 69
    standard deviations and, where counted, on edge-glyph coupling by 164.
  - No tested configuration reproduces line-zone dependence, or edge-glyph coupling where counted.
- **The minimal device: a sampler of the three measured rules does not reproduce B's other registered
  regularities** (C2097, PHASE_779). Page × line-type stocks, zone tables and two-unit routing, sampled by a
  within-cell Metropolis sampler with B's own tables, are not outside B on edge-glyph coupling and line-zone
  dependence (its inputs), adjacent repetition and cross-folio trigram recurrence, but are INCOMPLETE on order
  information beyond the edge (D5: 0.0145 against B's 0.038). Whether the D5 shortfall belongs to the rules or to
  this sampler is not resolved (a sequential with-replacement variant is not outside on D5 but differs in two ways
  and is outside on line-zone dependence).
  - Five registered regularities lie outside the sampler and outside the within-cell shuffle, with the same status
    on every variant and smoothing setting: line-level glyph-unit homogeneity (C1214's family, z +12.6),
    within-folio paragraph PREFIX composition (C1811/C1812, z +6.9), adjacent e-run persistence (z +7.5, partly
    unblinded), qo / ch-sh alternation (C549, z +9.2, partly unblinded), the e-run medial gradient (C1671/C1566,
    z +16.5). They are not shown to follow from these rules as sampled; the missing structure is not identified,
    and the five are not shown to be independent of one another or of the D5 shortfall.
  - Three show no detectable excess over the within-cell shuffle under the locked rule: hapax dispersion (rank
    996 of 1,000), the C2056 qok→ok lane as defined there (z +1.8), and pair zeros in C2081's form (B 10 at the
    pooled maximum, tie inside; fewer zeros than the shuffle). Nothing is REPRODUCED: no registered row is shown
    to follow from composition, zones and routing. Not being outside the sampler is not evidence of generation.
- **Untested:** syllables written with spelling variation (including homophonic syllable codebooks), morpheme-sized
  units, word-level codebooks with two or more spellings per word, modified verbose ciphers, grilles with boundary or
  line-position rules, and improvisation in a practised script at book scale. Excluding a rival is not evidence for
  the working interpretation. Not excluding one is not evidence that it generated B.

## 5. How to annotate a stale citation (for anyone editing living docs)
- **The claim is still presented as structure:** rewrite the passage to state the current status in plain words and
  cite the governing row. Example: "(C475, demoted to Tier 3: the percentage measured sparsity, not prohibition)".
- **The citation is incidental:** add a short bracketed status note next to it. Example: "[C089 superseded by
  C2082]".
- **A whole section rests on a withdrawn construct:** put a one-line banner at its head, "**[Withdrawn v7.24/7.25 —
  historical; see STATUS_BRIEF §3]**", and leave the text for traceability. Do not delete history.
- **Never** upgrade a claim, add a new claim, or edit the registry (INDEX.md, CONSTRAINT_TABLE.txt) from a living doc.
  Registry anomalies go to the maintainer.
