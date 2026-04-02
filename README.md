# Voynich Manuscript Computational Analysis

The Voynich Manuscript's main text (Currier B, 23,243 tokens across 83 folios) encodes closed-loop control programs in a purpose-built operational notation. Each folio is a self-contained program. The notation uses a systematic grammar of 49 instruction types built from an 18-atom compositional architecture. It is not a language, not a cipher, and not a translation of any known text.

The leading interpretive hypothesis identifies the source tradition as **Pseudo-Lullian alchemy** — specifically the *Testamentum* (Practica and Liber Mercuriorum). 3 folio-chapter correspondences are supported by independent structural evidence beyond the matching features, with ~12 more showing plausible correspondence in an 8-dimensional feature space. Theoretical and descriptive chapters produce zero validated matches — the manuscript encodes only procedural content.

Think of sheet music: if you found scores in an unknown notation, you couldn't translate notes into words — because notes aren't words. But structural analysis would reveal patterns matching the harmonic series. You could prove the documents encode music without hearing a note played. We take the same approach: we recovered the formal operating logic without translating individual tokens. The structure *is* the semantics.

This conclusion rests on 1,933 validated constraints from 635 research phases across 37,957 tokens.

---

## What We Claim / What We Do Not Claim

**We claim** (Tier 0-2: proven from the data):
- Currier B forms a closed executable grammar — 49 instruction classes with 100% coverage
- 17 state transitions are structurally forbidden, organized into 5 hazard classes
- A three-level safety architecture provides defense-in-depth (vocabulary exclusion, hazard typing, transition prohibition)
- Four registers (A, B, AZC, HT) share a common 18-atom compositional substrate
- The notation is not natural language (C132) and not cipher (C207, 0/18 tests passed)
- A generative model using the discovered grammar passes 21/21 structural metrics
- Specific tokens encode identifiable operational functions: `dar` = material introduction (6/6 cross-folio partition), `chekar` = post-thermal quality check (7/7 folios)
- The manuscript encodes only procedural content — theoretical and descriptive source chapters produce zero atom-validated matches

**We claim** (Tier 2-3: framework established, specific assignments interpretive):
- The best-fit historical source tradition is Pseudo-Lullian alchemy, calibrated against the *Testamentum* and independently against Brunschwig's distillation manual (1500)
- 3 folio-chapter correspondences are supported by independent structural evidence (f75r/Ch19, f76r/Ch18P, f84r/Ch14P); ~12 more show plausible correspondence via 8D feature matching (permutation p<0.001)
- Section B folios (f75-f84) show concentrated alignment with Liber Mercuriorum chapters (8/11); Section S folios (f103-f116) align with transmutation chapters
- A product chain is interpretively reconstructed: f75r (quintessence) feeds f84r (gold tincture), inferred through the *Testamentum*'s cipher key (Tier 3)

**We do not claim:** plaintext translation, exact substance identification from tokens alone, one-to-one text equivalence with any source, authorship proof, or that operational glosses are proven translations. See **[WHAT_WE_CLAIM.md](WHAT_WE_CLAIM.md)** for the full statement with constraint citations.

---

## Key Results

| Finding | Evidence |
|---------|----------|
| 49 instruction classes | 9.8x compression from 479 token types, 100% coverage |
| 83 programs (folios) | 23,243 Currier B instructions, each folio structurally distinct |
| 17 forbidden transitions | 5 hazard classes with near-orthogonal atom territories |
| Three-level safety | Construction exclusion + hazard typing + transition prohibition |
| 18-atom instruction encoding | HEAD+MOD*+TERM compositional grammar; frame predicts 64% of category |
| 18-atom instruction encoding | Every token decomposes structurally; 8 atoms have locked operational glosses, 6 solid, 5 plausible |
| Pseudo-Lullian source tradition | 3 confirmed + ~12 supported folio-chapter correspondences with *Testamentum* Practica + Mercuriorum |
| Product chain | Explicit: f75r quintessence = f84r input ("vegetable G" per PL cipher key) |
| Cross-folio vocabulary | `dar` = material introduction (6/6), `chekar` = quality check (7/7) |
| Section-level correspondence | f75-f84 = Liber Mercuriorum (8/11 folios); Section S = transmutation chapters |
| Brunschwig alignment | 28 tests across 4 suites — recovery architecture, fire degrees, material-apparatus separation |
| Generative closure | M2.1 model passes 21/21 metrics ([full progression](context/MARKOV_MODEL_EVOLUTION.md)) |

---

## Reading Path

| Order | Document | What it covers |
|-------|----------|---------------|
| 1 | **[GUIDE.md](GUIDE.md)** | Conceptual walkthrough — grammar, atom encoding, recipe matching (start here) |
| 2 | **[WHAT_WE_CLAIM.md](WHAT_WE_CLAIM.md)** | Precise claims and limits with tier markings and constraint citations |
| 3 | **[ARCHITECTURE.md](phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md)** | Formal specification — the definitive technical reference |
| 4 | **[OPERATOR_MODEL.md](phases/OPERATOR_USAGE_MODEL/OPERATOR_MODEL.md)** | How a practitioner would have used the manuscript (Tier 3) |
| 5 | **[Markov Model Evolution](context/MARKOV_MODEL_EVOLUTION.md)** | Why the model is trustworthy — progression from M0 (73%) to M2.1 (21/21) |
| 6 | **[Historical Network](phases/HISTORICAL_NETWORK/HISTORICAL_NETWORK.md)** | Medieval provenance and intellectual context |

---

## Four-Layer Architecture

| Layer | System | Tokens | Function |
|-------|--------|--------|----------|
| **Execution** | Currier B | 23,243 (61.9%) | Operational procedures — what to do, what to avoid |
| **Distinction** | Currier A | 11,415 (30.5%) | Vocabulary catalog — what operations exist, what is compatible |
| **Context** | AZC | 3,299 (8.7%) | Positional legality — where each operation is permitted |
| **Orientation** | HT | 7,042* | Operator orientation — where you are, what is coming |

*HT tokens are a morphological subset of B, already counted in the B total.

---

## Historical Source Tradition

The Pseudo-Lullian *Testamentum* — a 14th-15th century alchemical treatise attributed to Ramon Llull but written by an unknown practitioner — provides the closest match to the manuscript's operational content. Statistical matching using 8 locked feature dimensions identifies specific *Testamentum* chapters for ~30 Currier B folios, validated by:

- **Permutation testing:** Real chapter-to-folio assignment beats 1,000 random shuffles (p<0.001)
- **Cross-family replication:** Features derived from distillation chapters generalize to sublimation, fermentation, fixation, and dissolution families without retuning
- **Negative controls:** Wrong-regime matching collapses (1/16 confident vs 9/16 for correct regime); theoretical and descriptive chapters produce zero atom-validated matches
- **Atom-level confirmation:** Individual tokens on matched folios produce readings that independently align with recipe operations (18 folios checked, zero contradictions for locked atom glosses)

The manuscript reorganizes this content for workshop use: preparation procedures cluster in Herbal B (f75-f84), transmutation and multiplication procedures cluster in Section S (f103-f116). The ordering follows product chains, not book order. Theoretical content is entirely absent.

Brunschwig's *Liber de arte distillandi* (1500) provides independent calibration — the first printed distillation manual, published decades after the Voynich's radiocarbon date (1404-1438). 28 structural tests confirm alignment: recovery architecture matches Brunschwig's bounded retry rule, fire degrees correlate with stability proxy, and both systems encode procedures independently of materials.

---

## Atom-Level Instruction Encoding

Every Currier B token decomposes as: **PREFIX + MIDDLE + SUFFIX**, where MIDDLE further decomposes as **HEAD + MOD\* + TERM**.

18 single-character atoms have operational glosses at four confidence tiers:

| Tier | Atoms | Examples |
|------|-------|---------|
| **LOCKED** (8) | k=heat, e=cool, h=watch, y=end, i=iterate, n=bind, a=yield, m=final | Validated against 91 compound appearances + 18 recipe-matched folios |
| **SOLID** (6) | d=complete, t=transfer, l=state, o=arrange, c=adjust, p=pause | Validated against compound decomposition |
| **PLAUSIBLE** (5) | f=flag, s=sequence, r=respond, g=?, x=diagram | Partial evidence |

Every token can be structurally decomposed into atoms; the 8 locked glosses produce operationally consistent readings across independently-matched recipe folios. The remaining atom glosses are provisional — the majority of compound readings depend on SOLID or PLAUSIBLE atoms whose glosses may be refined.

These glosses describe **operational function**, not material content. `k=heat` means the atom governs thermal operations — not that it "translates" to the word "heat." The system is consistent with C171 (semantic ceiling): the notation encodes what to DO, not what something IS.

The e/k pair composes non-literally: k+e = sustained heat, k+ee = gentle/balneum heat, k+eee = deep balneum. Opposite thermal poles create a modulation gradient rather than independent concepts.

---

## Falsified Hypotheses

These approaches have been structurally ruled out (Tier 1 — cannot be retried):

- Natural language encoding (C132: language encoding CLOSED)
- Cipher / substitution system (C130: 0.19% reference rate to any known language)
- Glossolalia / random generation (C124: 100% grammar coverage rules out meaningless text)
- Illustrations constrain text (C138: swap invariance confirmed)
- Calendar / seasonal encoding of Zodiac pages (F-AZC-010: 0/4 predictions confirmed)
- Simple cycle topology for AZC diagrams (C455)
- Theorica / Furnis chapters as source material (C1932: zero atom-validated matches)

---

## How This Was Built

This project used AI-assisted computational analysis over 635 research phases. Every finding became a numbered constraint with an explicit confidence tier and provenance chain. Falsified hypotheses were permanently closed (Tier 1) — they cannot be retried, preventing circular investigation. An embedded expert-advisor agent (carrying all 1,933 constraints) validates new findings against the full body of existing knowledge.

The result: knowledge compounds across phases. Early phases discovered morphology, middle phases built grammar, late phases tested external comparisons and matched individual recipes — and none of this work was ever lost. For methodology details, tools, and repository structure, see **[METHODS_AND_TOOLS.md](METHODS_AND_TOOLS.md)**.

---

## Project Status

| Metric | Value |
|--------|-------|
| Validated constraints | 1,933 |
| Research phases | 635 |
| Model fits tested | 75 |
| Documented folios | 30 (of 83 Currier B) with per-folio analysis notes |
| Recipe-matched folios | 3 confirmed + ~12 supported (of 83 Currier B) |
| Atom decomposition | 100% structural coverage; 8 atoms locked, 6 solid, 5 plausible |

**Core model: CLOSED** | **Characterization: ACTIVE** | **Recipe matching: ACTIVE**

---

## Data Source

Transcript: EVA (Extensible Voynich Alphabet) interlinear format, H transcriber track. 37,957 tokens across 225 folios. The Voynich Manuscript is held by the Beinecke Rare Book & Manuscript Library, Yale University (MS 408). Manuscript and transcript data are in the public domain.

---

## Beyond This Project

The structural analysis establishes what the manuscript encodes (a control grammar for Pseudo-Lullian alchemical procedures) and what it does not (natural language). The identification of the *Testamentum* as the source tradition opens new directions: matching the ~53 remaining folios to other texts in the Pseudo-Lullian corpus, testing atom glosses against recipe content for refinement, and identifying specific materials through the product chain. The next breakthroughs will likely come from **alchemical historians** who can evaluate the recipe matches against the broader Pseudo-Lullian tradition, or **uncatalogued archives** that might preserve workshop manuals in the same lineage.

---

## License

This analysis is provided for research purposes. The Voynich Manuscript itself is in the public domain.
