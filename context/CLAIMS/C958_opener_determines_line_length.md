# C958: Opener Class Determines Line Length

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR

## Statement

The instruction class of a line's opening token explains 24.9% of line length variance beyond what folio and regime alone predict. The combination of folio + specific opener token explains 93.7% of all line length variance.

## Evidence

- 2,420 Currier B lines, mean length 9.54 +/- 3.25 tokens
- Hierarchical R-squared:
  - +folio: 0.300
  - +regime: 0.300 (+0.000, regime is redundant with folio)
  - +opener_class: 0.548 (+0.249)
  - +opener_token: 0.937 (+0.388)
  - +par_position: 0.942 (+0.005)
- Folio alone: R^2 = 0.300 (strongest single predictor)
- Opener class alone: R^2 = 0.018 (weak without folio conditioning)
- The partial R^2 of 24.9% means: within a given folio, the opener's class strongly constrains how many tokens the line will contain

## Interpretation

Line length is not random or purely folio-determined. The opener acts as a role-level "length signal" — different instruction classes produce different-length control blocks. This is the strongest token-level finding in the phase.

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/03_line_length_determinants.py`
- Related: C357, C557, C677
