# Research Agenda — open questions and the tests that would move them (v7.27, 2026-09-28)

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
   - The original design follows.
   - What: run the full discriminator panel on text people produced deliberately without meaning. The Gaskell & Bowern
     corpus (github.com/danielgaskell/voynich) is the natural source.
   - Panel: PHASE_757 D2–D6; C2082 word-ending routing; the C2081 zero-cell structure; line zones.
   - Resolves: if human gibberish reproduces B's profile, the grammar is evidence of a *writing process*, not of content.
     If it doesn't, we have the first measured contrast between B and *human-produced* meaningless text. The
     algorithmic kind is already excluded (C2077). Gaskell & Bowern report that human gibberish shares several
     Voynich statistics, which makes it the strongest meaningless rival still standing.
   - Kill conditions and discriminator thresholds must be set on controls before looking at B again (calibration rule).
2. **The untested rival generators.**
   - What: the Rugg grille (Parisel's public code), a syllable- or word-level codebook cipher and a modified verbose
     cipher, each through the PHASE_757 harness with noise parity.
   - Resolves: which generating mechanisms can and cannot produce the measured grammar. C2082 is new here: neither
     Naibbe nor Timm reproduces it, so it may be the sharpest discriminator available.
3. **Unit and transliteration invariance of the Tier-0 measurements.**
   - What: re-measure C121/C124 coverage, C956, C1212/C1563 and C2082 on ZL (done in part: PHASE_761, PHASE_763) and on
     at least one more transliteration (GC or CD). Also measure them on glyph units, with uncertain spaces treated both
     ways (Rozanova & Temerev: uncertain spaces are mostly word-internal).
   - Resolves: whether the core measurements are properties of the manuscript or of the EVA/H transcription.

## Tier B — structure that would constrain what kind of content it is

4. **Long-range sequence structure under the right null.**
   - What: re-run the λ2/λ3 class-transition eigenstructure (C2061, C2067) on N5 samples, which preserve composition,
     zones and boundary coupling.
   - Resolves: whether anything program-like (structure beyond the next token) exists, or whether the sequence is
     boundary coupling plus endings.
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
- **Toward "notation for procedures":** long-range, program-like structure beyond endings survives N5 (#4), *and* a
  prospective content anchor lands (#7).
- **Toward "language or cipher of language":** a rival from #2 that encodes real text reproduces B's profile, or the
  unit re-analysis (#3) finds word-like units with natural-language statistics.
