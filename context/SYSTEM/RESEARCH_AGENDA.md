# Research Agenda — open questions and the tests that would move them (v7.39, 2026-09-30)

**Companion to** `SYSTEM/STATUS_BRIEF.md` (what stands) and `SYSTEM/STRATEGIC_REVIEW_2026-09-27.md` (review record).
**Principle:** after ~760 phases on one corpus there is no untouched holdout. New channels are the only genuinely
out-of-sample evidence: second transcriptions, images, external corpora, generator panels and prospective anchors.
Rank tests by what they would **resolve**, and pre-register each one (lean-expert design audit before lock).

---

## The question
What produced Currier B's grammar: a language written in an unfamiliar way, a cipher, a notation for procedures, or
text made to look meaningful? And, if it carries content, what content?

**Where things stand:**
- The grammar is real and specific. It survives copy-and-modify generation (C2077) and the Naibbe cipher (C2080), and
  it has measured line-level and word-boundary structure: C956, C1212/C1563, C2081, C2082.
- Against meaningless text, one generator has been tested:
  - Timm & Schinner's self-citation (copy-and-modify) generator, the main academic "meaningless" hypothesis, is
    excluded (C2077).
  - Human-improvised gibberish was tested at folio scale in PHASE_764: unresolved (below). The Rugg grille has
    not been tested.
  - The older "glossolalia ruled out by 100% coverage" argument was circular (the 100% is the grammar's own vocabulary)
    and is retired.
  - C420's "ruling out gibberish" shows internal consistency only.
  - No measurement yet positively shows that the text carries meaning.
- Nothing ties the text to an external source.
- The working interpretation (procedural notation) is unconstrained by current measurements.

---

## Tier A — decides whether the grammar is evidence of meaning at all

1. **Human-gibberish control.** Done: PHASE_764 returned MIXED / UNRESOLVED at folio scale.
   - B's coupling exceeds most samples (AUC 0.825), but the lower bound missed 0.80.
   - Meaningful text is equally far below B, so this is not a meaning discriminator.
   - Lead: B's position-in-line dependence far exceeds gibberish (descriptive AUC 0.986). It needs new data to
     confirm.
     - PHASE_782 (Codex Seraphinianus, OCR transliteration): UNRESOLVED; the Codex's value lies in the band the
       design could not separate (about 0.02 to at least 0.15 bits) because its noise is unknown. Descriptively the
       Codex carries a line-position dependence of its own (0.097 bits; B 0.234; Brunschwig print 0.04-0.05,
       Aberdeen Bestiary 0.007, not like for like). Next: measure the transliteration's first-character error by line
       zone on a hand-transliterated sample outside Ponzi's training words, then degrade B to the measured
       zone-specific rates instead of the conservative heavy setting; or use a clean second book-length
       pseudo-script. Either needs a new pre-registered phase.
   - The original design follows.
   - What: run the full discriminator panel on text people produced deliberately without meaning. The Gaskell & Bowern
     corpus (github.com/danielgaskell/voynich) is the natural source.
   - Panel: PHASE_757 D2–D6; C2082 word-ending routing; the C2081 zero-cell structure; line zones.
   - Resolves: if human gibberish reproduces B's profile, the grammar is evidence of a *writing process*, not of content.
     If it doesn't, we have the first measured contrast between B and *human-produced* meaningless text. The
     algorithmic kind is already excluded (C2077). Gaskell & Bowern report that human gibberish shares several
     Voynich statistics, which makes it the strongest meaningless rival still standing.
   - Kill conditions and discriminator thresholds must be set on controls before looking at B again (calibration rule).
1b. **Step-notation comparison.** Done: PHASE_765, C2083 — NOT SUPPORTED.
    - B's low-level profile is nearest to improvised gibberish and farthest from knitting notation and assembly
      code.
    - Open: procedures written as fluent word-like tokens, and structure at line, paragraph and page level
      (line position is B's strongest difference from gibberish, PHASE_764).
1c. **Token-unit (syllable) test.** Done: PHASE_767, C2085 — plain syllable writing EXCLUDED on unit inventory.
    - B has 5,141 types per 20,000 tokens; syllable-written controls 685–1,338; k* > 16 spellings per syllable.
    - Open: syllables written with spelling variation, morpheme-sized units (item 2).
2. **The untested rival generators.**
   - What: the Rugg grille (done: PHASE_778, C2096, below), a word-level codebook, a syllable codebook with spelling variation
     (one spelling per syllable is excluded, C2085) and a modified verbose cipher, each through the PHASE_757
     harness with noise parity.
   - Word-level codebooks (PHASE_774):
     - excluded with one spelling per word, for plaintexts that repeat their phrases (C2091);
     - with two or more spellings per word, repeat statistics at B's size cannot see them (C2092). They remain open
       for the discriminator panel.
   - A cipher keyed by the previous word's ending (PHASE_775, C2093): no signature by rank decoding. The test is
     detection-only, so this is no exclusion.
     - Descriptively, B's local order is carried by the glyph edges; within ending contexts, neighbours' ranks are
       independent.
     - Possible follow-up: rerun under a corpus-wide EF to test why B-fitted generators show more neighbour dependence
       than B.
   - One letter per word at the first or second glyph unit, the rest rule-built filler (PHASE_777, C2095): NO
     START-POSITION PAYLOAD. Second unit clean NONE (excluded for every tested plaintext, up to 10% corruption); first
     unit in the pre-registered residual band (noise-free payloads excluded only).
     - Open: the word end (needs a null keyed on the following token's ending; EF-L keeps only its first unit);
       payloads in a subset of words or over several positions; the source of the F1 residual (no-payload habits and
       corrupted payloads both land there).
   - Table-and-grille generation (PHASE_778, C2096): PUBLISHED EXCLUDED (PARTIAL FITS ONLY); EXTENDED and STEELMAN
     NOT EXCLUDED under the locked rule, one fitted variant each (the d = 2 / keep walks, V0; V1 borderline;
     d2/reset/keep UNSTABLE-TO-FIT). Tier 0 unchanged.
     - Open: a follow-up is a new pre-registered phase whose discriminator is certified on controls before it sees
       these variants; extending PHASE_778's N or adding discriminators to re-decide it is not allowed. Grilles with
       boundary or line-position rules are untested.
   - The minimal device (PHASE_779, C2097): a Metropolis sampler of page × line-type stocks, zone tables and
     two-unit routing is INCOMPLETE on D5; B lies outside it on five of eight registered regularities (line
     glyph-unit homogeneity, paragraph PREFIX composition, e-run persistence, qo/ch-sh alternation, e-run medial
     gradient: not shown to follow from the rules as sampled, missing structure not identified) and is outside
     neither the sampler nor the within-cell shuffle on three (hapax dispersion, the C2056 lane, pair zeros).
     Layer map only; no production claim.
     - Open: whether the D5 shortfall belongs to the rules or to the sampler (a sequential with-replacement variant
       is not outside on D5 but differs in two ways; a new phase with a whole-token order statistic in its fidelity
       gate decides); which added rule (line memory, paragraph
       palette, interior e-run rule, family alternation) accounts for each extra layer, one plant at a time, each
       a pre-registered phase; the C1435 and C1811/C1812 definition checks still stand.
   - Resolves: which generating mechanisms can and cannot produce the measured grammar. C2082 is new here: neither
     Naibbe nor Timm reproduces it, so it may be the sharpest discriminator available.
3. **Unit and transliteration invariance of the Tier-0 measurements.**
   - What: re-measure C121/C124 coverage, C956, C1212/C1563 and C2082 on ZL (done in part: PHASE_761, PHASE_763) and on
     at least one more transliteration (GC or CD). Also measure them on glyph units, with uncertain spaces treated both
     ways (Rozanova & Temerev: uncertain spaces are mostly word-internal).
   - Resolves: whether the core measurements are properties of the manuscript or of the EVA/H transcription.

## Tier B — structure that would constrain what kind of content it is

4. **Long-range sequence structure under the right null.** Done: PHASE_776, C2094 — ROUTING-REDUCIBLE.
   - The class-pair dependence and the λ2/λ3 eigenstructure reduce to junction coupling, two-unit ending routing and
     folio × line-type composition (an exact null, EF-K2, replacing the N5 chain).
   - Open: a within-line residual beyond two-unit routing (descriptives at nominal p < 0.05, uncorrected) as its own
     pre-registered question; longer boundary keys; narrow token-level effects (C549, C2056).
5. **Word-ending routing, characterised.**
   - What: which endings route to which next classes; whether this is one mechanism with C1212/C1563 (a two-glyph
     boundary context) or a separate one; whether it holds within scribes or quires.
   - Resolves: whether this is the grammar's main sequential rule. It is the positive lead from PHASE_763.
6. **Currier A ↔ B relation after the audits.**
   - What: restate the A-side characterisation (June corrections) against the live registry.
   - Resolves: whether A and B are two notations, two registers of one, or one system with two scribal conventions.

## Tier C — content (only with prospective, blind designs)

7. **Prospective anchors.**
   - What: pre-register specific predictions from a candidate source (e.g. the *Testamentum* tradition) about folios
     not yet examined, with a genre baseline (other alchemical and pharmacy texts) and blind scoring.
   - Resolves: whether any content correspondence exists. The chapter matching carries no signal (PHASE_762, C2052).
8. **Pictures and text, powered.**
   - What: label-to-image grounding with blind image coding, with labels re-transcribed from IIIF first (C2004/C2005
     gaps). The earlier nulls had n ≈ 30 and little power (VIS, ILL-TOP-1).
   - Resolves: whether the text refers to what is drawn.
   - First test done: PHASE_766, C2084 — NO SIGNAL (bounded). No pharmaceutical fragment label recurs on the
     herbal page of its visually matched plant (13 pairs; MDE80 = 2 pairs). Next: designs that do not assume a
     label is a word of the herbal text (e.g. label agreement within the pharmaceutical section across fragments
     of the same plant), which needs more text-blind plant identifications.
   - Precondition met: PHASE_769, C2086: the e-run dial has a folio-level component shared across words, with no
     per-procedure setting.
   - PHASE_770, C2087: it survives removal of the preceding token's two-glyph ending. Its shape, sharing and
     page-turn continuity are unresolved under the pre-registered rules; descriptively, static page settings fit
     poorly.
   - The picture gate passed. Next: a blind picture-coding test within one section and hand that codes page
     regions or position-resolved features, not only whole folios, and that tests multi-step copying and
     writing-session drift as rival sources.
   - **Herbal pages, whole-page features (PHASE_780, C2098): NOT DETECTED (unpowered).** Blind two-set coding of the
     91 hand-1 herbal drawings against page text, with drift, quire, sheet, layout, spelling-dial and style controls
     and a matched Brunschwig 1500 positive control (genre power 0.61, an upper bound; its link runs mostly through
     plant names).
     - Open: power is the limit; no fresh herbal population of comparable size exists (V-B2 has N = 20, another
       hand). The head-of-page form was tried next (PHASE_781, below) and is weaker still; these 91 pages have now
       been seen, so any further test on them is not independent of PHASE_780 (including its line-interior
       companion).
     - **Head of the page (PHASE_781): stopped at its pre-registered gate.** On the Brunschwig 1500 herbal, a
       head-of-page text–picture test at 91 entries and the Voynich first-line lengths detected the herbal's own link
       in at most 18% of samples (Wilson 13–24%; bar 85%). The Voynich first lines were not tested against the
       drawings and remain unexposed. This is a fact about the test's power, not about the Voynich.
     - **Next for this route:** the PHASE_780/781 statistic family does not reach the 85% bar against Brunschwig
       1500's link at N = 91 in the whole-page form (0.61, an upper bound; C2098) or the first-line form (at most
       0.18); it is powered only against dense planted descriptors (C2098: 80% at about one descriptor per coded
       feature per page). No more hand-1 herbal pages exist (V-B2: hand 2, N = 20). A further test needs a different
       statistic with its own power gate. If the statistic is chosen after seeing Brunschwig's ablations, the gate
       must use an illustrated herbal other than Brunschwig 1500, and should first show that any statistic reaches the
       bar at N = 91. One untested candidate: a statistic aimed at links concentrated in a few page pairs (for example
       nearest-neighbour retrieval), which covers only naming systems that share name parts.
     - PHASE_780 and PHASE_781 are the planned family of text–picture tests on these 91 pages; the family bound
       (≤ 0.02 for at least one false positive) has been spent only by PHASE_780. Exposure record: whole-page text
       exposed (C2098 and its companions, including the line-interior value); first lines unexposed. Any further test
       on these pages must be justified on controls and carry the family bound.
   - **The zodiac crib** (PHASE_772, C2090): the labels are not a repeated per-sign set (no numeral crib of the simple
     kind).
     - PHASE_773 (the figures against medieval per-degree tables) stopped at design. The blind-coded attributes vary by
       page, not by figure, so no comparison was computed.
     - The degree tables stay unread, ready for a better-coded, figure-level attribute set.
   - **Merged spellings** (PHASE_774, C2091/C2092):
     - no recurring 5-token phrase in B;
     - interchangeable spellings mostly defeat repeat statistics.
     - Content therefore needs an external anchor (known plaintext at a known place), not more internal statistics of
       this kind.
   - Labels (PHASE_771, C2088):
     - label o-words fit no mixture of ordinary o-words, dropped-q qo-words and "o + word";
     - next, pre-register AZC ring text as the reference for AZC labels (s7 fit ordinary o-words alone), and test the
       s2 / s8 dependence of the qo weight.
   - Line organisation (PHASE_771, C2089):
     - the edge index at drawing breaks is unresolved;
     - next, check the post-break aiin and pre-break -m cases on H and the scans;
     - split post-break articulators into C1898's opener and embedded groups.
   - Pending:
     - the blind scan check of 100 minim groups (PHASE_770 section 14, human-coded), before any minim-dial claim;
     - the floor ("every hand drifts") as its own phase: one hand, known page order, 60 or more pages, 3,000 or more
       within-frame choices.
9. **Physical structure.**
   - What: PHASE_752 v2 steps 2–3 (bifolium and quire effects on the second transcription), for Malta (video due
     2026-11-09). The Aberdeen negative control is SPECIFIC (PHASE_759).
   - Resolves: whether page layout carries structure, and whether binding order can be used at all.

## Methodological debts (re-checks owed before relying on these rows)
- **PHASE_760:** its N_EDGE arm ran at β = 4, which does not mix (PHASE_756). Re-run at β = 2.
- **C2045 and the other sequence claims** validated only against a character 5-gram: re-test under token shuffle or
  N5 (C2066 window-blindness).
- **The 41 rows with parser-reliability notes** (PHASE_758): re-measure the ones still cited.
- **C2031/C2032:** an N-matched, length-stratified re-run with lag2 − lag1 (PHASE_755).
- **Measurement/gloss split** (strategic review §6): C1195, C1196, C1934, C1388–C1392, C1925, C1926, C1958 (the last three already demoted to Tier 3, PHASE_762) and the
  mapping clauses of C929/C931 mix a measurement with a gloss. Split each into a Tier-2 measurement row and a Tier-3
  gloss row; `ATOM_GLOSSES` in `scripts/voynich.py` are labels meanwhile.
- **Registry decisions left open by the v7.26 cascade:** C1005 (Tier 4, possibly a Tier-1 falsification); C179
  (4-regime clustering: scope-tagged, demotion defensible); C311/C456 (possibly retract like C434/C435); C193–C195;
  the C894 row's numbers are stale (C894 demoted to Tier 3 in v7.26) (its detail file moved the signal to REGIME_2); two LINK definitions coexist
  (C861 class 29 vs C609 'ol'); OPS correlations partly built in (C190, C180, C188).
- **Residual unannotated citations of non-live constraints:** see `SYSTEM/REGISTRY_INTEGRITY_REPORT.md`, and regenerate
  after every registry change.
- **Working rules not yet in place:** a test ledger (script hash, null, kill, outcome for every confirmatory test) and
  sheet-blocked cross-fitting for anything fitted (strategic review §7).

## What would change the working interpretation
- **Toward "meaningless but systematic":** Tier A #1 or #2 reproduces B's discriminator profile.
- **Toward "notation for procedures":** (#4 is done and found nothing beyond the boundary rules, C2094) a new,
  pre-registered sequence measurement beyond the boundary rules would be needed, *and* a
  prospective content anchor lands (#7).
- **Toward "language or cipher of language":** a rival from #2 that encodes real text reproduces B's profile, or the
  unit re-analysis (#3) finds word-like units with natural-language statistics.
