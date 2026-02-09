# Legacy Code - Falsified Hypotheses

This directory contains scripts and data from early project phases that tested hypotheses which were subsequently **falsified through rigorous testing**.

## Purpose of Preservation

This code is preserved for the **scientific record**. It demonstrates:

1. The hypothesis rejection process that led to the frozen model
2. Alternative approaches that were tested and ruled out
3. The evolution of understanding from semantic to operational interpretation

## Contents

### `translation_attempts/`

Scripts that attempted to decode the Voynich Manuscript as natural language or meaningful text.

**Status**: FALSIFIED (Phase X.5)
- Reference rate: 0.19% (threshold was 5%)
- Role consistency: 23.8% (threshold was 80%)
- Verdict: Text does not behave as language

### `dictionary_building/`

Scripts that built lexicons and word-meaning mappings.

**Status**: SUPERSEDED
- These lexicons were built under the assumption of semantic encoding
- The operational grammar model renders them obsolete
- Preserved for historical reference only

### `semantic_analysis/`

Scripts that analyzed the text as if it encoded semantic meaning.

**Status**: FALSIFIED (Phase 19)
- 0 identifier tokens found
- 0 translation-eligible zones
- PURE_OPERATIONAL verdict

## Do Not Use

These scripts will not produce meaningful results under the current model. They are preserved only for documentation purposes.

## What Replaced This Approach

The current model (documented in CLAUDE.md) interprets the manuscript as:

- An **executable operational control grammar**
- 49 instruction equivalence classes (9.8x compression)
- 83 programs describing apparatus operation
- No semantic layer, no translation possible

See `phases/` directories for the analysis that established this model.
