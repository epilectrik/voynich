# Voynich Manuscript Computational Analysis

The Voynich Manuscript's main text (Currier B) is a set of operational procedures for running a controlled process — most likely thermal distillation. Each page is a self-contained program. The notation encodes what to do, when to intervene, and what to avoid, using a systematic grammar of 49 instruction types. It is not a language, not a cipher, and not a recipe book.

Think of sheet music: if you found scores in an unknown notation, you couldn't translate notes into words — because notes aren't words. But structural analysis would reveal patterns matching the harmonic series. You could prove the documents encode music without hearing a note played. We take the same approach: we recovered the formal operating logic without translating individual tokens. The structure *is* the semantics.

This conclusion rests on 1,711 validated constraints from 589 research phases across 37,957 tokens.

---

## What We Claim / What We Do Not Claim

**We claim** (Tier 0-2: proven from the data):
- Currier B forms a closed executable grammar — 49 instruction classes with 100% coverage
- 17 state transitions are structurally forbidden, organized into 5 hazard classes
- A three-level safety architecture provides defense-in-depth (vocabulary exclusion, hazard typing, transition prohibition)
- Four registers (A, B, AZC, HT) share a common 18-atom compositional substrate
- The notation is not natural language (C132) and not cipher (C207, 0/18 tests passed)
- A generative model using the discovered grammar reproduces 87% of measurable structure (21/21 metrics)

**We claim** (Tier 3: consistent with evidence, not proven):
- Structural alignment with Brunschwig's distillation manual suggests reflux distillation as the domain (28 tests)
- The manuscript functions as a multi-register technical control notation for expert practitioners

**We do not claim:** plaintext translation, exact substance identification, apparatus schematics, one-to-one Brunschwig equivalence, authorship proof, or that operational labels like "thermal" are proven translations. See **[WHAT_WE_CLAIM.md](WHAT_WE_CLAIM.md)** for the full statement with constraint citations.

---

## Key Results

| Finding | Evidence |
|---------|----------|
| 49 instruction classes | 9.8x compression from 479 token types, 100% coverage |
| 83 programs (folios) | 23,243 Currier B instructions, each folio structurally distinct |
| 17 forbidden transitions | 5 hazard classes with near-orthogonal atom territories |
| Three-level safety | Construction exclusion + hazard typing + transition prohibition |
| 18-atom instruction encoding | HEAD+MOD*+TERM compositional grammar; frame predicts 64% of category |
| 6-state macro-automaton | 8.17x class compression; AXM attractor; 6 folio-level archetypes |
| Generative closure | M2.1 model passes 21/21 metrics ([full progression](context/MARKOV_MODEL_EVOLUTION.md)) |
| 8 operational categories | THERMAL, CONTAINMENT, FLOW, MONITORING, OPERATION, STAGING, MARKING, TRANSITION |
| Brunschwig alignment | 28 tests across 4 suites — recovery architecture, fire degrees, material-apparatus separation |

---

## Reading Path

| Order | Document | What it covers |
|-------|----------|---------------|
| 1 | **[GUIDE.md](GUIDE.md)** | Conceptual walkthrough of all four layers (start here) |
| 2 | **[ARCHITECTURE.md](phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md)** | Formal specification — the definitive technical reference |
| 3 | **[OPERATOR_MODEL.md](phases/OPERATOR_USAGE_MODEL/OPERATOR_MODEL.md)** | How a practitioner would have used the manuscript (Tier 3) |
| 4 | **[GENRE_ANALYSIS.md](phases/HISTORICAL_GENRE_PLACEMENT/GENRE_ANALYSIS.md)** | Medieval document classification — proposed OPERATIONAL CONTROL CODEX (Tier 3) |
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

## Falsified Hypotheses

These approaches have been structurally ruled out (Tier 1 — cannot be retried):

- Natural language encoding (C132: language encoding CLOSED)
- Cipher / substitution system (C130: 0.19% reference rate to any known language)
- Glossolalia / random generation (C124: 100% grammar coverage rules out meaningless text)
- Illustrations constrain text (C138: swap invariance confirmed)
- Calendar / seasonal encoding of Zodiac pages (F-AZC-010: 0/4 predictions confirmed)
- Simple cycle topology for AZC diagrams (C455)

---

## Brunschwig Connection

Structural comparison with Hieronymus Brunschwig's *Liber de arte distillandi* (1500) — the first printed distillation manual — provides the strongest external domain alignment. **This is a Tier 3 interpretation:** the structural grammar (Tier 0-2) is proven; the identification of distillation as the specific domain is an inference from structural parallels.

28 tests across 4 suites. Key alignments: recovery architecture matches Brunschwig's bounded retry rule; fire degrees correlate with stability proxy (rho=-0.457); both systems encode procedures independently of materials; both use categorical sensory tests without instruments.

The manuscript's radiocarbon date (1404-1438) places it in the pre-publication secrecy window. Brunschwig published in 1500 what practitioners had been keeping proprietary. Full historical context: [HISTORICAL_NETWORK.md](phases/HISTORICAL_NETWORK/HISTORICAL_NETWORK.md).

---

## How This Was Built

This project used AI-assisted computational analysis over 589 research phases. Every finding became a numbered constraint with an explicit confidence tier and provenance chain. Falsified hypotheses were permanently closed (Tier 1) — they cannot be retried, preventing circular investigation. An embedded expert-advisor agent validates new findings against all existing constraints in each phase.

The result: knowledge compounds across phases. Early phases discovered morphology, middle phases built grammar, late phases tested external comparisons — and none of this work was ever lost. For methodology details, tools, and repository structure, see **[METHODS_AND_TOOLS.md](METHODS_AND_TOOLS.md)**.

---

## Project Status

| Metric | Value |
|--------|-------|
| Validated constraints | 1,711 |
| Research phases | 589 |
| Model fits tested | 75 |
| Constraint tiers | 0 (frozen fact) through 4 (exploratory) |

**Core model: CLOSED** | **Characterization: ACTIVE**

---

## Data Source

Transcript: EVA (Extensible Voynich Alphabet) interlinear format, H transcriber track. 37,957 tokens across 225 folios. The Voynich Manuscript is held by the Beinecke Rare Book & Manuscript Library, Yale University (MS 408). Manuscript and transcript data are in the public domain.

---

## Beyond This Project

The structural analysis establishes what the manuscript encodes (a control grammar) and what it does not (natural language). The questions that remain — who wrote it, what specific materials are processed, how notation maps to specific operations — are beyond internal structural analysis. The next breakthroughs will likely come from **uncatalogued archives** (Central European medical faculties, apothecary guilds, court collections) or **external domain expertise** (practicing distillers, historical chemists, process engineers who may recognize operational patterns). The [folio decoder](scripts/DECODER.md) renders any Currier B folio with full structural annotation for expert review.

---

## License

This analysis is provided for research purposes. The Voynich Manuscript itself is in the public domain.
