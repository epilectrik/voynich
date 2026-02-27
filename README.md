# Voynich Manuscript Computational Analysis

Systematic computational analysis of the Voynich Manuscript (Beinecke MS 408), a 15th-century codex written in an unknown script. This project uses statistical morphology, grammar extraction, and structural constraint analysis to determine what the manuscript encodes — without attempting translation.

**New here?** Read **[GUIDE.md](GUIDE.md)** for a plain-English walkthrough of all four manuscript systems and what they do.

## Project Status

**Core model: CLOSED** | **Characterization: ACTIVE**

| Metric | Value |
|--------|-------|
| Validated constraints | 1,201 |
| Research phases completed | 473 |
| Model fits tested | 75 |
| Constraint tiers | 0 (frozen fact) through 4 (exploratory) |

## Core Finding

> The Voynich Manuscript's Currier B text encodes a family of **closed-loop, kernel-centric control programs** designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

This is not a natural language. This is not a cipher. This is a **control system reference manual** for a physical process. Structural comparison with Hieronymus Brunschwig's *Liber de arte distillandi* (1500) suggests reflux distillation as the most likely domain (Tier 3 interpretation — see Brunschwig Connection below).

### The Approach: Structure, Not Translation

Think of sheet music. If a researcher discovered musical scores without knowing the notation, they could never translate notes into words — because notes aren't words. But structural analysis would reveal patterns that fit the harmonic series: forbidden combinations matching dissonant intervals, positional rules matching musical form. They could prove the documents encode music without ever hearing a note played.

We take the same approach with the Voynich Manuscript. We don't translate tokens into meanings. We prove that the manuscript's internal structure — 49 instruction classes, 17 forbidden transitions in 5 hazard classes, kernel-centric convergence, bounded recovery — fits the domain of thermodynamic process control. The forbidden transitions map onto physical failure modes. The convergence behavior matches distillation physics. The recovery architecture matches historical practice. The structure fits the domain the way sheet music fits harmonics.

**[GUIDE.md](GUIDE.md)** provides a full walkthrough of all four manuscript systems and how they work together.

## Key Results

| Finding | Evidence |
|---------|----------|
| 49 instruction classes | 9.8x vocabulary compression from 479 token types |
| 83 programs (folios) | 23,243 Currier B instructions |
| 100% grammar coverage | Every token participates in the grammar |
| 17 forbidden transitions | In 5 hazard classes (PHASE, COMPOSITION, CONTAINMENT, RATE, ENERGY) |
| 0 translation-eligible zones | PURE_OPERATIONAL verdict — no natural language content |
| 8 operational categories | THERMAL, CONTAINMENT, FLOW, MONITORING, OPERATION, STAGING, MARKING, TRANSITION — organize all four systems (C1250) |
| 6-state macro-automaton | 8.17x class compression; AXM attractor (self=0.697); 6 folio-level archetypes orthogonal to REGIMEs |
| Generative sufficiency | 49-class Markov + symmetric forbidden suppression reproduces 87% of measurable structure (M2 frontier; 15/15 tests after B4+C2+B5 corrections, C1025/C1030/C1033/C1034) |
| Cross-system categories | A records are category-themed (d=9.7); AZC zones sort bridge vocabulary by category; categories predict B escape dynamics (THERMAL→escape rho=+0.780) |
| Process control match | 5 PCs / 80% variance matches modern distillation, not Brunschwig recipes (3 PCs) |
| Apparatus vocabulary | 5 apparatus profiles from marker MIDDLEs; REGIME encodes apparatus type; aii (unseal) 41x enriched in R3 (C1247-C1249) |
| Brunschwig alignment | 28 tests across 4 test suites (see below) |

## Four-Layer Architecture

The manuscript comprises four structurally distinct systems that form a layered control architecture:

| Layer | System | Tokens | Function |
|-------|--------|--------|----------|
| **Execution** | Currier B | 23,243 (61.9%) | Controls what you do over time |
| **Distinction** | Currier A | 11,415 (30.5%) | Catalogs where distinctions matter |
| **Context** | AZC | 3,299 (8.7%) | Static positional lookup table classifying vocabulary |
| **Orientation** | HT (Human Track) | 7,042* | Compound specifications redundant with body lines; keeps operator oriented during production |

*HT tokens are a morphological subset of Currier B — they are already counted in the B total. They use the same morphology but do not participate in the 49-class grammar.

## Token Morphology

Every Currier B token decomposes as: **[ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]**

- **PREFIX** encodes the operational domain AND line position via a base-modifier positional grammar: each PREFIX decomposes into [MODIFIER (position 0)] + [BASE (position 1)], where the base character determines which MIDDLE content domain is legal (within-base cosine 0.950 vs between-base 0.515; C1218-C1219). PREFIXes predict operational categories with structured selectivity (V=0.311, C1297) and read as two-atom instructions: [VERB]+[TARGET] (e.g., ok="operate heat", ch="adjust watch"). Sister pairs (ch/sh, ok/ot) achieve category divergence through vocabulary SELECTION, not transformation — the same MIDDLE keeps its category regardless of which sister selects it (C1305). Tier 3 glosses grounded in Tier 2 structural differentiation (C911, C661)
- **MIDDLE** encodes the core action (e.g. apply heat, check hazards, let settle — Tier 3 glosses grounded in Tier 2 behavioral profiles; C267, C506.b)
- **SUFFIX** encodes role-dependent and positional markers (line-final clustering, role selectivity — but carries zero unique cross-token prediction beyond MIDDLE class; C1002, C1004)

This compositional structure was derived statistically from distributional analysis of the transcript.

## Brunschwig Connection

The strongest external corroboration comes from systematic comparison with Brunschwig's distillation manual (1500):

| Test Suite | Score |
|------------|-------|
| 6-Axis Structural Comparison | 4 MATCH, 1 PARTIAL, 1 informative MISMATCH |
| Reverse Brunschwig V1 (10 tests) | 2 STRONG, 5 SUPPORT, 2 WEAK, 1 NEUTRAL |
| Reverse Brunschwig V2 (6 tests) | 1 CONFIRMED, 2 SUPPORT, 3 NOT SUPPORTED |
| Reverse Brunschwig V3 (6 tests) | 5 PASS or informative |

Key alignments:
- **Recovery architecture**: 89% reversibility with bounded retry, matching Brunschwig's "no more than twice" reinfusion rule (mean escape chain: 1.19 tokens)
- **Fire degrees**: Brunschwig's 4 fire degrees correlate with Voynich LINK/FL ratio as stability proxy (rho = -0.457, p < 0.0001)
- **Material-apparatus separation**: Both systems encode procedures independently of materials
- **Sensory modalities**: Both use categorical sensory tests without instruments
- **Illustration anchoring**: Root-emphasized plant illustrations correlate with POUND/CHOP operations (r = 0.366, p = 0.0007)

## What This Project Does NOT Claim

- Specific product or material identities (semantic ceiling: C171)
- Natural language meanings for any token
- Historical identity of the author
- That illustrations carry semantic content (C138: illustrations are epiphenomenal)
- Token-level "translation" — operational roles are not word meanings

## Falsified Hypotheses

These approaches have been structurally ruled out (Tier 1):

- Natural language encoding (C132)
- Cipher/substitution system (C130: 0.19% reference rate)
- Illustrations constrain text (C138)
- Calendar/seasonal encoding of Zodiac pages (F-AZC-010: 0/4 predictions)
- Simple cycle topology for AZC (C455)
- Glossolalia / random generation (C124: 100% grammar coverage)

## Tools

### Core Library

```python
from scripts.voynich import Transcript, Morphology, BFolioDecoder

# Iterate tokens (H-track, labels excluded automatically)
tx = Transcript()
for token in tx.currier_b():
    print(token.word, token.folio, token.section)

# Morphological analysis
morph = Morphology()
m = morph.extract('otchedy')
print(m.prefix, m.prefix2, m.middle, m.suffix)  # ot, ch, edy, None

# Full folio decode with Brunschwig-grounded glossing
decoder = BFolioDecoder()
print(decoder.decode_summary('f76r', mode='interpretive'))
```

### Folio Renderer

```
python scripts/show_b_folio.py f76r -p         # Paragraph view (gloss + tokens)
python scripts/show_b_folio.py f76r --flow     # Control-flow view (macro states + FL stages)
python scripts/show_b_folio.py f76r --detail 4 # Full metadata dump (all classification layers)
```

Renders any Currier B folio with morphological parse, structural roles, interpretive glosses, 6-state macro classification, and hub/affordance metadata. See [`scripts/DECODER.md`](scripts/DECODER.md) for full documentation of all 6 rendering modes and flags.

## Directory Structure

```
voynich/
  context/            # Constraint system (1,201 validated constraints)
    CLAUDE_INDEX.md   # Start here for full documentation
    CLAIMS/           # Individual constraint files
    ARCHITECTURE/     # System architecture docs (A, B, AZC, cross-system)
    STRUCTURAL_CONTRACTS/  # API-layer contracts (CASC, BCSC, ACT, HTSC, PSC)
    MODEL_FITS/       # 75 tested model fits
    SPECULATIVE/      # Tier 3-4 interpretations
  data/               # Transcript, dictionaries, Brunschwig recipes
  scripts/            # voynich.py core library + analysis tools
  phases/             # 473 completed research phases
  results/            # Legacy analysis outputs (early phases; new results go in phases/)
  folio_analysis/     # Per-folio hazard maps
  annotation_data/    # Folio annotation work
  archive/            # Archived scripts and old documentation
```

> **Note on repo size:** This repository is large and rough in spots. Every research phase, intermediate result, and dead end has been preserved intentionally — the accuracy of the constraint system depends on being able to trace any finding back to the script and data that produced it. We chose reproducibility over tidiness.

## Constraint Tier System

| Tier | Meaning | Count |
|------|---------|-------|
| 0 | FROZEN FACT — proven, do not reopen | 25 |
| 1 | FALSIFICATION — rejected, do not retry | 15 |
| 2 | STRUCTURAL — high-confidence, bounded | 1,124 |
| 3 | SPECULATIVE — interpretive layer | 35 |
| 4 | EXPLORATORY — idea generation only | 2 |

## Methodology

This project was built using AI-assisted computational analysis. The primary development environment was [Claude Code](https://claude.ai/claude-code) (Anthropic), which wrote the analysis scripts, maintained the constraint system, and performed statistical validation. GPT-5 (OpenAI) provided independent cross-validation and alternative analytical perspectives at key decision points. All claims are grounded in statistical evidence from the transcript data — no result depends on AI intuition or pattern-matching alone.

### Progressive Context Architecture

The central methodological innovation is a **progressive context system** — a growing body of validated constraints that accumulates across research phases and is always available to the AI agents performing analysis.

The system works as follows:

1. **Every finding becomes a constraint.** When a research phase produces a statistically validated result, it is encoded as a numbered constraint (e.g., C267: "Every Currier B token decomposes as PREFIX + MIDDLE + SUFFIX") with an explicit tier level and provenance chain back to the script and data that produced it.

2. **Constraints are tiered by confidence.** Tier 0 constraints are frozen facts that cannot be reopened. Tier 1 constraints are falsified hypotheses that cannot be retried. Tier 2 constraints are high-confidence structural findings. Tiers 3-4 are speculative or exploratory. This prevents the system from drifting backward or re-deriving known results.

3. **Context is always loaded.** Every new analysis session begins with the full constraint system available. The AI doesn't start from scratch — it starts from everything that has already been proven, disproven, or established. This means phase 473 benefits from all 1,201 constraints accumulated across the previous 472 phases.

4. **Structural contracts provide fast lookup.** As the constraint count grew, key subsystems were summarized into API-like contracts (YAML files) that encode the essential properties of each manuscript layer in a single file. These contracts are the "shallow API" — check the contract first, drill into individual constraints only when needed.

5. **Falsification is permanent.** When a hypothesis fails, it is recorded as a Tier 1 falsification and can never be retried. This prevents circular investigation and forces the analysis forward. Over 30 hypotheses have been permanently closed this way, including natural language encoding, cipher systems, calendar theories, and character-level semantics.

6. **Expert validation prevents drift.** An embedded expert-advisor agent carries a consolidated version of the entire constraint system — all 1,201 constraints, structural contracts, fit results, and architectural documentation — pre-loaded into its system prompt. When a research phase proposes new constraints, interpretive extensions, or structural changes, the expert-advisor validates them against the full body of existing knowledge in a single pass. This catches contradictions, tier violations, and semantic drift that would be invisible to any individual research phase working with partial context. The expert's consolidated context is regenerated from source whenever the constraint system changes, ensuring it always reflects the current state of knowledge.

The result is a system where knowledge compounds: early phases discover basic morphology, middle phases build grammar and classification, late phases test external comparisons and characterize edge cases — and none of this work is ever lost or forgotten. Every constraint is traceable to specific statistical evidence.

This architecture is what allowed the project to reach conclusions that would be impossible in a single analytical pass. No individual analysis session could discover 49 instruction classes, 17 forbidden transitions, 6 macro states, and the Brunschwig alignment — but 473 phases, each building on validated prior work, could.

## Data Source

Transcript: EVA (Extensible Voynich Alphabet) interlinear format, H transcriber track (primary). 37,957 tokens across 225 folios.

The Voynich Manuscript is held by the Beinecke Rare Book & Manuscript Library, Yale University (MS 408). The manuscript and all transcript data are in the public domain.

## License

This analysis is provided for research purposes. The Voynich Manuscript itself is in the public domain (Beinecke Rare Book & Manuscript Library, Yale University).
