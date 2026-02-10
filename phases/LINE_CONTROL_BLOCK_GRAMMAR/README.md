# LINE_CONTROL_BLOCK_GRAMMAR Phase

**Status:** CLOSED
**Verdict:** MODERATE — Boundary-constrained control blocks with free interior
**Tests:** 11 (00-10) | **Constraints:** C956-C964
**Scope:** Currier B (23,243 tokens, 2,420 lines, 83 folios)

## Governing Premise

Each Currier B line is a control block. Role-level positional grammar (C556: SETUP/WORK/CHECK/CLOSE) is established. This phase tests whether a TOKEN-level grammar layer exists beyond role-level effects.

Central question:
> Is Currier B primarily a role-grammar with lexical decoration,
> or a two-level grammar where token identity carries additional syntactic force?

## Results Summary

| Test | Topic | Verdict | Key Finding |
|------|-------|---------|-------------|
| T00 | Token-Shape Negative Control | 3/4 structural | Most effects survive token-identity destruction |
| T01 | Positional Token Exclusivity | **PASS** | 192/334 tokens zone-exclusive (2.7x shuffle, p=0.000) |
| T02 | Mandatory/Forbidden Bigrams | **PASS** | 26 mandatory, 9 forbidden (2 token-specific), p=0.000 |
| T03 | Line Length Determinants | **PASS** | Opener class adds 24.9% partial R^2 beyond folio+regime |
| T04 | Opener Instruction Header | PARTIAL | Role accuracy 29.2% (1.46x chance); token JSD not significant |
| T05 | Boundary Constraint Sets | FAIL | Gini 0.47 (below 0.60); boundary vocab is open, not closed |
| T06 | Within-Zone Ordering | FAIL | EN tau ~ 0, AX tau ~ 0; WORK zone is unordered |
| T07 | Phase Interleaving | PARTIAL | Weak clustering (p<0.001) but not sequential; compliance 32.7% |
| T08 | Paragraph Line Progression | FAIL | Only length progression (rho=-0.23); composition flat after control |
| T09 | Zone-Specific Bigrams | WEAK | KL=1.05 bits at INITIAL; only 1 zone significant vs shuffle |
| T10 | Integrated Verdict | **MODERATE** | Grammar strength 0.500; dominant signal: boundary_grammar |

## Negative Control (Test 00)

Synthetic corpus preserving role/position but destroying token identity:
- Exclusivity: STRUCTURAL (survives)
- Forbidden bigrams: STRUCTURAL (survives)
- Opener classification: STRUCTURAL (survives)
- Boundary Gini: LEXICAL (vanishes)

Interpretation: 3/4 effects are driven by role/position, not token identity.

## Final Characterization

Currier B lines are **boundary-constrained control blocks with a free interior**:

1. **Boundaries are constrained:** Positional exclusivity (192 tokens zone-exclusive), mandatory bigrams (26), and line length determination (opener class explains 24.9% variance) all operate at line edges.
2. **Interior is free:** Within the WORK zone, tokens of the same role show no ordering (tau ~ 0), phases interleave rather than forming blocks, and any same-role token can substitute for another.
3. **Constraints are role-level:** The negative control proves most effects are structural — they survive when token identity is destroyed. The system routes by ROLE, not by specific TOKEN.
4. **Two genuine token-level signals:** (a) chey cannot precede chedy or shedy (same ENERGY class, genuinely forbidden), (b) boundary Gini is lexical (the specific vocabulary at boundaries matters slightly beyond role).

The system is essentially **role-complete**: the 49 instruction classes and 5 roles capture nearly all syntactic structure. Token-level effects are consequences of role membership, not independent constraints.

## Architectural Interpretation

> The distiller writing a control procedure chooses WHERE to place each operation type (role),
> but which SPECIFIC token delivers that operation is largely interchangeable. The system
> minimizes lexical syntax to reduce error — an expert-only safety system where getting the
> operation type right matters more than the specific word chosen to express it.

## Stop Conditions

- Grammar strength 0.50 = MODERATE range
- Negative control confirms structural origin
- No further token-level investigation warranted unless new role-independent signal emerges

## Scripts

| Script | Test | Output |
|--------|------|--------|
| 00_token_shape_negative_control.py | Negative control | 00_*.json |
| 01_positional_token_exclusivity.py | T01 | 01_*.json |
| 02_mandatory_forbidden_bigrams.py | T02 | 02_*.json |
| 03_line_length_determinants.py | T03 | 03_*.json |
| 04_opener_instruction_header.py | T04 | 04_*.json |
| 05_opener_closer_constraint_sets.py | T05 | 05_*.json |
| 06_within_zone_ordering.py | T06 | 06_*.json |
| 07_phase_interleaving.py | T07 | 07_*.json |
| 08_paragraph_line_progression.py | T08 | 08_*.json |
| 09_positional_bigram_grammar.py | T09 | 09_*.json |
| 10_integrated_verdict.py | T10 | 10_*.json |

## Provenance

- Designed following expert review identifying line-level grammar as biggest remaining gap
- Pre-registered pass/fail criteria per test
- Token-shape negative control (Test 00) included per expert recommendation
- All shuffle controls: 1000 iterations, seed=42, within-line permutation
