# Voynich Manuscript Computational Analysis

Systematic computational analysis of the Voynich Manuscript (Beinecke MS 408), a 15th-century codex written in an unknown script. This project uses statistical morphology, grammar extraction, and structural constraint analysis to determine what the manuscript encodes — without attempting translation.

**New here?** Read **[GUIDE.md](GUIDE.md)** for a plain-English walkthrough of all four manuscript systems and what they do.

## Project Status

**Core model: CLOSED** | **Characterization: ACTIVE**

| Metric | Value |
|--------|-------|
| Validated constraints | 1,349 |
| Research phases completed | 538 |
| Model fits tested | 75 |
| Constraint tiers | 0 (frozen fact) through 4 (exploratory) |

## Core Finding

> The Voynich Manuscript's Currier B text encodes a family of **closed-loop, kernel-centric control programs** designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

This is not a natural language. This is not a cipher. It is a **control system grammar** — a collection of structured programs whose architecture is consistent with maintaining a physical process within safe operating limits. Structural comparison with Hieronymus Brunschwig's *Liber de arte distillandi* (1500) suggests reflux distillation as one plausible domain (Tier 3 interpretation — see Brunschwig Connection below).

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
| Generative closure | 49-class Markov + quintile position conditioning + symmetric forbidden suppression passes 21/21 metrics (M2.1 frontier; distributional, sequential, morphological, structural, positional, and directional tests all pass — C1025/C1034/C1364/C1365). See **[Markov Model Evolution](context/MARKOV_MODEL_EVOLUTION.md)** for the full progression from M0 (73%) to M2.1 (21/21). |
| Instruction encoding | MIDDLEs decompose as HEAD+MOD*+TERM — frame predicts 64% of category, modifiers shift 36%. Co-occurrence avoidance dominates ordering (8/15 pairs never co-occur; no strict stacking rule — C1472). 18 atoms, 5 HEAD domains, 6 exit conditions (C1393-C1394) |
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

- **ARTICULATOR** (q, y, s, d) is an optional line-position marker present on 4.41% of B tokens. It is 6.48x enriched at line-initial position, selects for e-HEAD MIDDLEs (stability operations), suppresses suffix attachment (0.34–0.55x normal rate), and adds zero information about operational category beyond what MIDDLE provides (CMI=0.000 bits; C1416-C1421). It is orthogonal to the content chain — it marks *where* in the line a token sits, not *what* it does.
- **PREFIX** encodes the operational domain AND line position via a base-modifier positional grammar: each PREFIX decomposes into [MODIFIER (position 0)] + [BASE (position 1)], where the base character determines which MIDDLE content domain is legal (within-base cosine 0.950 vs between-base 0.515; C1218-C1219). PREFIXes predict operational categories with structured selectivity (V=0.311, C1297) and read as two-atom instructions: [VERB]+[TARGET] (e.g., ok="operate heat", ch="adjust watch"). Sister pairs (ch/sh, ok/ot) achieve category divergence through vocabulary SELECTION, not transformation — the same MIDDLE keeps its category regardless of which sister selects it (C1305). Tier 3 glosses grounded in Tier 2 structural differentiation (C911, C661)
- **MIDDLE** encodes the core action as a compositional compound: **HEAD + MOD\* + TERM**. The HEAD atom (a, e, o, k, t) sets the operational domain; an ordered modifier stack (p→f→i→c→d→s) parametrizes the action; a TERMINAL atom (y, l, r, h, m, n) sets the exit condition. The frame (HEAD+TERM) predicts 64% of operational category; modifiers shift the remaining 36% (C1393-C1394). Approximately 30 core MIDDLEs handle 67.6% of all tokens. The TERMINAL `h` ("watch") is transparent — it lets HEAD+MODS determine category (V=0.988), unlike opaque terminals like `r` (99% FLOW). Headless compounds (20.6% of tokens) form a specialized subgrammar for infrastructure operations at boundary positions (C1394 T8-T11). Note: structural decomposition and category assignments are Tier 2; English glosses like "watch" are Tier 3 interpretive labels (C1195).
- **SUFFIX** is a parallel compositional domain using a 16-atom subset of MIDDLE's inventory (missing k, t, p, f, c — the action-specific atoms). Like MIDDLE, suffix decomposes as **HEAD + TERM** with strong ordering (76.6% HEAD-initial, 100% TERM-terminal, zero violations). The first atom selects operational category (V=0.277); the last atom selects line position/scope (R²=0.059). Crucially, atoms carry **different information by position** — the same character means different things in suffix vs MIDDLE (0/12 shared atoms maintain identical profiles; C1408-C1409). Two suffix modes coexist within paragraphs (C1229): Mode A = THERMAL/MONITORING atoms {d,e,h,y}; Mode B = STAGING/FLOW atoms {a,i,l,m,n,o,r,s} (C1410). Each token's mode is ~80% determined by its own MIDDLE content, not by sequential alternation — lines persist in a mode (60.6% same-mode) and the line-to-line switch rate (39.4%) is below chance (C1422-C1424). Suffix selection is dominated by the MIDDLE TERMINAL atom (V=0.503), not PREFIX (V=0.166) — PREFIX's influence on suffix is fully mediated through MIDDLE (C1411-C1413). Entropy: 1.475 bits of suffix freedom given MIDDLE (C1002, C1004).

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
- **Illustration anchoring**: Root-emphasized plant illustrations correlate with preparation-class PREFIX operations (r = 0.366, p = 0.0007)

## Historical Context

The manuscript's radiocarbon date (1404-1438) and known provenance chain place it within a specific intellectual network centered on Vienna, Northern Italy, and the Upper Rhine. Phase 491 maps this network: 58 persons, 98 edges, and 16 contemporary cipher parallels across the Voynich's temporal-geographic zone.

Key findings:
- **Cipher use was normal** in this zone — Giovanni Fontana (c.1420) used invented glyphs, the *Buch der heiligen Dreifaltigkeit* (c.1410) encrypted alchemical knowledge, and the *Alchymey Teuczsch* (1426) is a full cipher manuscript
- **Selective encryption of commercially valuable knowledge** was standard practice among apothecaries and distillers
- **Brunschwig's 1512 publication** explicitly marks the transition from secrecy to openness ("*geoffenbart*" — revealed/made public)
- **The Vienna medical faculty** (c.1400-1440) sits at the intersection of all structural, temporal, and domain evidence

Full documentation: [`phases/HISTORICAL_NETWORK/HISTORICAL_NETWORK.md`](phases/HISTORICAL_NETWORK/HISTORICAL_NETWORK.md)

## What This Project Does NOT Claim

- Specific product or material identities (semantic ceiling: C171)
- Natural language meanings for any token
- Historical identity of the author
- That illustrations carry semantic content (C138: illustrations do not constrain text)
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

### AI Expert Mode

Running [Claude Code](https://claude.ai/claude-code) in this repository automatically creates a Voynich expert with the full constraint system loaded as permanent context. The `CLAUDE.md` project instructions, progressive context architecture (`context/`), and embedded agent definitions (`.claude/agents/`) give the AI complete access to all 1,315 validated constraints, 6 structural contracts, and 75 model fits — no manual setup required. Ask it anything about manuscript structure and it will answer with constraint citations.

## Directory Structure

```
voynich/
  context/            # Constraint system (1,241 validated constraints)
    CLAUDE_INDEX.md   # Start here for full documentation
    CLAIMS/           # Individual constraint files
    ARCHITECTURE/     # System architecture docs (A, B, AZC, cross-system)
    STRUCTURAL_CONTRACTS/  # API-layer contracts (CASC, BCSC, ACT, HTSC, PSC)
    MODEL_FITS/       # 75 tested model fits
    SPECULATIVE/      # Tier 3-4 interpretations
  data/               # Transcript, dictionaries, Brunschwig recipes
  scripts/            # voynich.py core library + analysis tools
  phases/             # 530 completed research phases
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
| 1 | FALSIFICATION — rejected, do not retry | 16 |
| 2 | STRUCTURAL — high-confidence, bounded | 1,160 |
| 3 | SPECULATIVE — interpretive layer | 35 |
| 4 | EXPLORATORY — idea generation only | 2 |

## Methodology

This project was built using AI-assisted computational analysis over 506 research phases. The primary development environment was [Claude Code](https://claude.ai/claude-code) (Anthropic), which wrote the analysis scripts, maintained the constraint system, and performed statistical validation. GPT-5 (OpenAI) provided independent cross-validation and alternative analytical perspectives at key decision points. All claims are grounded in statistical evidence from the transcript data — no result depends on AI intuition or pattern-matching alone.

### Progressive Context Architecture

The central methodological innovation is a **progressive context system** — a growing body of validated constraints that accumulates across research phases and is always available to the AI agents performing analysis.

The system works as follows:

1. **Every finding becomes a constraint.** When a research phase produces a statistically validated result, it is encoded as a numbered constraint (e.g., C267: "Every Currier B token decomposes as PREFIX + MIDDLE + SUFFIX") with an explicit tier level and provenance chain back to the script and data that produced it.

2. **Constraints are tiered by confidence.** Tier 0 constraints are frozen facts that cannot be reopened. Tier 1 constraints are falsified hypotheses that cannot be retried. Tier 2 constraints are high-confidence structural findings. Tiers 3-4 are speculative or exploratory. This prevents the system from drifting backward or re-deriving known results.

3. **Context is always loaded.** Every new analysis session begins with the full constraint system available. The AI doesn't start from scratch — it starts from everything that has already been proven, disproven, or established. This means phase 507 benefits from all constraints accumulated across the previous phases.

4. **Structural contracts provide fast lookup.** As the constraint count grew, key subsystems were summarized into API-like contracts (YAML files) that encode the essential properties of each manuscript layer in a single file. These contracts are the "shallow API" — check the contract first, drill into individual constraints only when needed.

5. **Falsification is permanent.** When a hypothesis fails, it is recorded as a Tier 1 falsification and can never be retried. This prevents circular investigation and forces the analysis forward. Over 30 hypotheses have been permanently closed this way, including natural language encoding, cipher systems, calendar theories, and character-level semantics.

6. **Expert validation prevents drift.** An embedded expert-advisor agent carries a consolidated version of the entire constraint system — all constraints, structural contracts, fit results, and architectural documentation — pre-loaded into its system prompt. When a research phase proposes new constraints, interpretive extensions, or structural changes, the expert-advisor validates them against the full body of existing knowledge in a single pass. This catches contradictions, tier violations, and semantic drift that would be invisible to any individual research phase working with partial context. The expert's consolidated context is regenerated from source whenever the constraint system changes, ensuring it always reflects the current state of knowledge.

The result is a system where knowledge compounds: early phases discover basic morphology, middle phases build grammar and classification, late phases test external comparisons and characterize edge cases — and none of this work is ever lost or forgotten. Every constraint is traceable to specific statistical evidence.

This architecture is what allowed the project to reach conclusions that would be impossible in a single analytical pass. No individual analysis session could discover 49 instruction classes, 17 forbidden transitions, 6 macro states, an 18-atom instruction encoding architecture, and the Brunschwig alignment — but hundreds of phases, each building on validated prior work, could.

## Data Source

Transcript: EVA (Extensible Voynich Alphabet) interlinear format, H transcriber track (primary). 37,957 tokens across 225 folios.

The Voynich Manuscript is held by the Beinecke Rare Book & Manuscript Library, Yale University (MS 408). The manuscript and all transcript data are in the public domain.

## Where Further Answers May Be Found

Computational analysis has established what the manuscript encodes (a control system grammar for thermodynamic process control) and what it does not encode (natural language, cipher, or glossolalia). But the questions that remain — who wrote it, what specific materials are being processed, and how the notation maps to specific operations — are beyond the reach of internal structural analysis. The grammar was designed to work without encoding that information.

The next breakthroughs will likely come from two directions:

- **Uncatalogued archives.** The manuscript's provenance chain passes through Central European medical faculties, apothecary guilds, and court collections from the early 15th century. Many archives in Vienna, Prague, Padua, and the Upper Rhine region contain uncatalogued material from this period — guild records, apothecary inventories, teaching manuscripts, and private correspondence. A single confirmed parallel notation system or explicit reference to encoded distillation knowledge would transform the analysis.

- **External distillation domain expertise.** The structural findings describe a specific control grammar — 49 instruction classes, 5 hazard classes, 3 kernel operators, bounded recovery architecture. A practicing distiller, historical chemist, or process engineer familiar with pre-industrial reflux distillation may recognize operational patterns that computational analysis can identify structurally but cannot name. The [folio decoder](scripts/DECODER.md) renders any Currier B folio with full structural annotation for domain expert review.

## License

This analysis is provided for research purposes. The Voynich Manuscript itself is in the public domain (Beinecke Rare Book & Manuscript Library, Yale University).
