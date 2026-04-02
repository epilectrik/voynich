# Methods and Tools

This document covers the project's research methodology, tools, and repository structure. For AI agent instructions, see `CLAUDE.md`. For project findings, see `README.md`.

---

## Methodology

This project was built using AI-assisted computational analysis over 635 research phases. The primary development environment was [Claude Code](https://claude.ai/claude-code) (Anthropic), which wrote the analysis scripts, maintained the constraint system, and performed statistical validation. GPT-5 (OpenAI) provided independent cross-validation at key decision points. All claims are grounded in statistical evidence from the transcript data — no result depends on AI intuition or pattern-matching alone.

### Progressive Context Architecture

The central methodological innovation is a **progressive context system** — a growing body of validated constraints that accumulates across research phases and is always available to the AI agents performing analysis.

1. **Every finding becomes a constraint.** When a research phase produces a statistically validated result, it is encoded as a numbered constraint (e.g., C267: "Every Currier B token decomposes as PREFIX + MIDDLE + SUFFIX") with an explicit tier level and provenance chain.

2. **Constraints are tiered by confidence.** Tier 0 = frozen facts. Tier 1 = falsified hypotheses (cannot be retried). Tier 2 = high-confidence structural findings. Tiers 3-4 = speculative or exploratory.

3. **Context is always loaded.** Every new analysis session begins with the full constraint system available. Phase 552 benefits from all constraints accumulated across the previous 551 phases.

4. **Structural contracts provide fast lookup.** Key subsystems are summarized into API-like contracts (YAML files) that encode essential properties in a single file.

5. **Falsification is permanent.** When a hypothesis fails, it is recorded as Tier 1 and can never be retried. Over 30 hypotheses have been permanently closed.

6. **Expert validation prevents drift.** An embedded expert-advisor agent carries all constraints pre-loaded. It validates new findings against the full body of existing knowledge, catching contradictions and tier violations.

The result: knowledge compounds across phases. No individual analysis session could discover 49 instruction classes, 17 forbidden transitions, 6 macro states, an 18-atom instruction encoding architecture, the Brunschwig alignment, and 30 individual recipe-folio correspondences — but 635 phases, each building on validated prior work, could.

---

## Constraint Tier System

| Tier | Meaning | Count |
|------|---------|-------|
| 0 | FROZEN FACT — proven, do not reopen | 25 |
| 1 | FALSIFICATION — rejected, do not retry | 16 |
| 2 | STRUCTURAL — high-confidence, bounded | ~1,890 |
| 3 | SPECULATIVE — interpretive layer | ~40 |
| 4 | EXPLORATORY — idea generation only | 2 |

Total: 1,933 validated constraints.

---

## Tools

### Core Library

```python
from scripts.voynich import Transcript, Morphology, BFolioDecoder

# Iterate tokens (H-track, labels excluded automatically)
tx = Transcript()
for token in tx.currier_b():
    print(token.word, token.folio, token.section)

# Morphological analysis (PREFIX/MIDDLE/SUFFIX split)
morph = Morphology()
m = morph.extract('otchedy')
print(m.prefix, m.prefix2, m.middle, m.suffix)  # ot, ch, edy, None

# Atom-level decomposition (HEAD+MOD*+TERM — 100% coverage)
a = morph.atomize('qokeedy')
print(a.prefix)    # 'qo'
print(a.atoms)     # [('k','HEAD','heat'), ('e','MOD','cool'), ('e','MOD','cool'),
                    #  ('d','MOD','mark'), ('y','TERM','end')]
print(a.e_depth)   # 2 (gentle/stabilized heat — balneum mariae signature)
print(a.gloss)     # 'qo:heat.cool.cool.mark.end'

# Full folio decode with structural annotation
decoder = BFolioDecoder()
print(decoder.decode_summary('f76r', mode='interpretive'))
```

### Folio Renderer

```
python scripts/show_b_folio.py f76r -p         # Paragraph view (gloss + tokens)
python scripts/show_b_folio.py f76r --flow     # Control-flow view (macro states)
python scripts/show_b_folio.py f76r --detail 4 # Full metadata dump
```

Renders any Currier B folio with morphological parse, structural roles, interpretive glosses, and macro classification. See [`scripts/DECODER.md`](scripts/DECODER.md) for full documentation.

### AI Expert Mode

Running [Claude Code](https://claude.ai/claude-code) in this repository automatically creates a Voynich expert with the full constraint system loaded as permanent context. The `CLAUDE.md` instructions, context architecture, and embedded agent definitions give the AI access to all 1,933 constraints, 6 structural contracts, and 75 model fits.

### Recipe-Folio Matching System

The 8D residual matching system (Phase 628) maps historical recipe chapters to Voynich folios:

1. **Feature extraction:** Both PL chapter text and Voynich folio tokens produce 8-dimensional feature vectors measuring thermal intensity, monitoring density, correction rate, termination rate, and 4 structural dimensions.
2. **Residual matching:** Mean-center both sets, standardize jointly, compute Euclidean distances.
3. **Validation:** Permutation test (1,000 shuffles, p<0.001), cross-family replication (features generalize to unseen operation families), wrong-regime negative control (collapses as expected).
4. **Atom-level confirmation:** Individual token decomposition on matched folios independently validates recipe correspondence at paragraph resolution.

Infrastructure: `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/shared_628.py`

---

## Directory Structure

```
voynich/
  context/            # Constraint system (1,933 validated constraints)
    CLAUDE_INDEX.md   # Start here for full documentation
    CLAIMS/           # Individual constraint files
    FOLIOS/           # Per-folio analysis notes (30 documented folios)
    ARCHITECTURE/     # System architecture docs
    STRUCTURAL_CONTRACTS/  # API-layer contracts (CASC, BCSC, ACT, HTSC, PSC)
    MODEL_FITS/       # 75 tested model fits
    SPECULATIVE/      # Tier 3-4 interpretations
    GLOSSING.md       # Atom gloss system documentation
  data/               # Transcript, dictionaries, Brunschwig recipes
  scripts/            # voynich.py core library + analysis tools
  sources/            # Historical texts (PL Testamentum, Brunschwig, Codicillus)
  phases/             # 635 completed research phases
  results/            # Legacy analysis outputs (early phases)
  folio_analysis/     # Per-folio hazard maps
  archive/            # Archived scripts and old documentation
```

> **Note on repo size:** This repository is large and rough in spots. Every research phase, intermediate result, and dead end has been preserved — the accuracy of the constraint system depends on being able to trace any finding back to the script and data that produced it. We chose reproducibility over tidiness.
