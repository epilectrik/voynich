# What We Claim / What We Do Not Claim

This document states the project's claims explicitly, with their evidence tier and constraint basis. It was rewritten
on 2026-09-28 after the September 2026 review ([STRATEGIC_REVIEW_2026-09-27.md](context/SYSTEM/STRATEGIC_REVIEW_2026-09-27.md)),
which re-tested the central claims against external controls. The generated
[CONSTRAINT_TABLE.txt](context/CONSTRAINT_TABLE.txt) is authoritative for which constraints are live and at what tier.

---

## 1. Measurements (Tier 2: reproduced under controls)

These are statements about the text. They do not depend on any interpretation of what it means.

- **Boundary glyph coupling.** The last glyph of a word predicts the first glyph of the next within a line: 0.228 bits
  beyond a within-line shuffle on the H transcription, 0.243 on the ZL transcription, and 0.215 at definite spaces alone
  (uncertain spaces behave like word-internal transitions and inflate the pooled value by about 16%). (C1212, C1563;
  PHASE_761)
- **Positional vocabulary.** Common words are tied to line start or line end: 192 of 334 common tokens are excluded from at
  least one line zone; zone dependence 0.172 bits beyond shuffle. (C956; PHASE_757)
- **Adjacent-word structure.** Adjacent words share a prefix less often than line composition implies (qo/ch/sh
  interleaving) and share an ending more often; kept slots persist rather than rotate; adjacent identical words occur at
  chance. (C549, C1002, C2079; PHASE_757, PHASE_760)
- **Low order information.** Beyond the boundary link, the previous word adds 0.040 bits per token of held-out
  predictive information. (PHASE_757)
- **Word form.** Tokens decompose into prefix, core and ending; the parts interact pairwise and carry no three-way
  synergy (C1003). Several letter-level regularities are properties of the EVA transcription (single glyphs spelled as
  letter strings): the bench glyphs ch/sh, the benched gallows and the minim groups (PHASE_754). Longer e-runs are followed
  more often by y and less often by d, across the script (C1225 as rescoped; PHASE_758).
- **Grammar.** 49 token classes cover the grammar's own 480-type vocabulary — 69.5% of Currier B tokens; the rest (HT,
  unclassified) is defined by exclusion. The same classes are used on every Currier B folio. (C121, C124)
- **Section-level e-depth structure.** Section B paragraphs show a period-2 e-depth alternation (not shown to be a section
  property independent of paragraph length); a paragraph-channel e-depth gradient (qo > ch > sh). Both reproduce on a
  second transcription. (C2031, C1967; PHASE_755, PHASE_758)
- **Transcription reliability.** e-run lengths are read consistently across transcriptions (κ 0.95–0.96, an upper bound
  since the transcriptions are not independent readings). (PHASE_758)

**Reported measurement, not yet registered:** pages on the same bifolium share vocabulary beyond distance and length
effects while facing pages do not — the reverse of the Aberdeen Bestiary, a normal codex used as a negative control
(herbal pure-A p = 0.0007; Q13 p = 0.013; Q20 p = 0.017). Registration waits on a second-transcription replication and
the pre-registered gate. (PHASE_752, PHASE_759)

## 2. Rivals tested and excluded (Tier 2, negative knowledge)

- **Naibbe verbose homophonic cipher (Greshko 2025), as published:** excluded on all 64 declared variants (both code
  versions; Latin recipe, Latin pharmacy, Italian and Latin prose plaintexts; two layouts; two spacing and two noise
  settings; 1,000 ciphertexts each). Any cipher proposed for Currier B must reproduce boundary coupling, chance-level
  repetition, line-position vocabulary and B's low order information. (C2080; PHASE_757)
- **Timm & Schinner self-citation generation:** excluded. (C2077)
- **Natural language written one token per word:** excluded (C132, C2015, C2022). **Token ≈ word codes, atom-level
  polyalphabetic cipher, three published decipherments:** excluded (C1976, C2017).
- **Tokens produced by walking a table of coordinates:** no signature (C2079).
- **"Forbidden transitions":** the token-level zero bigrams reduce to line composition, positional zones and boundary
  coupling under a joint null (C2081, superseding C957); the class-level "17 transitions in 5 hazard classes" was demoted
  (C783) and its taxonomy found imposed (C2060).

## 3. Open hypotheses

- **The project's working interpretation (Tier 0, frozen by human sign-off):** Currier B encodes a family of closed-loop,
  kernel-centric control programs governed by a single shared grammar. The grammar and kernel structure stand; the
  support formerly drawn from forbidden transitions and hazard classes has been withdrawn (section 2). The wording
  "narrow viability regime" is flagged for human review.
- **Content — the Pseudo-Lullian *Testamentum* tradition:** open.
  - Against the chapter-level matching: a metalwork treatise (Theophilus) matches the same folios (C2052); no source —
    *Testamentum*, Theophilus or Codicillus — matches the Voynich pages better than its own chapters with the features
    shuffled; the part → section mapping and recto/verso adjacent-chapter pattern do not appear under automated,
    similarity-matched testing; the permutation test behind the former "p < 0.001" returns p < 0.01 for random numbers.
    The chapter → folio assignments and everything inferred from them are Tier 3. (PHASE_762)
  - Still standing: the parchment date (1404–1438) falls inside the *Testamentum*'s circulation; the imagery; the argument
    that an execution-level notation should be more detailed than its source recipes; and one specific coincidence —
    f75r, the only Currier B folio with a four-token repeat (C1889), was paired with III.19, the only SISMEL Catalan
    sub-recipe mentioning "four times, otherwise nine times" (C2034). That pairing came from the generic matcher and the
    ×4 feature was noticed afterwards; it needs a prospective test.
- **Encoding — cipher or notation:** open beyond the excluded classes. Untested: modified or coarser-unit cipher designs
  (syllable- or word-level codebooks) and the Rugg grille.

## 4. What we do not claim

- **No translation.** No token has a demonstrated equivalent in any language. (C171)
- **No specific source text.** The *Testamentum* correspondence is an open hypothesis (section 3), not a finding.
- **No operational meanings.** Atom and token glosses (k = heat, `dar` = material introduction, …) are role hypotheses,
  not recovered meanings.
- **No "hazard" or "safety" layer.** Withdrawn (section 2).
- **No closure.** The analysis is not complete; the referents of the notation are not recovered.

## 5. What would change our mind

- A decodable cipher — modified Naibbe, a syllable- or word-level codebook, or another design — that reproduces the four
  properties in section 2 would reopen the cipher reading for that class and weaken the notation reading.
- A prospective test in which predictions derived from unexamined recipes are frozen and then confirmed on unexamined
  folios would move the *Testamentum* reading from open to supported; a failure would weaken it further.
- A second-transcription failure of the boundary coupling or of the bifolium contrast would retract those measurements.

---

*Pre-review versions of this document and of GUIDE.md, RECIPE_MATCHING.md and METHODS_AND_TOOLS.md are in the git
history; the latter three are kept in the repository, marked as pre-review.*
