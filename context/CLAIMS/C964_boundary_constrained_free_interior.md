# C964: Boundary-Constrained Free-Interior Grammar

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR

## Statement

Currier B lines operate as boundary-constrained control blocks with a free interior. Token-level grammar exists at boundaries (positional exclusivity, mandatory bigrams, opener-length coupling) but is primarily structural (role-driven). The WORK zone interior is unordered and role-free at the token level. The system is essentially role-complete.

## Evidence (Integrated Verdict)

- Grammar strength score: 0.500 (MODERATE)
- Tests 01, 02, 03: PASS (boundary effects)
- Tests 05, 06, 08: FAIL (interior/vocabulary effects absent)
- Tests 04, 07, 09: PARTIAL/WEAK
- Negative control: 3/4 effects are STRUCTURAL (survive token-identity destruction)
- Dominant signal source: boundary_grammar

## Key Findings

1. **Boundaries constrained:** 192/334 tokens zone-exclusive, 26 mandatory bigrams, opener class determines line length (+24.9% R^2)
2. **Interior free:** Within-zone ordering absent (tau ~ 0), phases interleave rather than block, body lines homogeneous
3. **Role-complete:** Negative control proves constraints are role-driven; 49 classes and 5 roles capture all syntactic structure
4. **Two token-specific exceptions:** chey->chedy and chey->shedy forbidden (same ENERGY class)

## Architectural Interpretation

The distiller chooses WHERE to place each operation type (role), but which SPECIFIC token delivers that operation is largely interchangeable. The system minimizes lexical syntax to reduce cognitive load and error — the right operation type matters more than the specific word chosen.

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/10_integrated_verdict.py`
- Synthesizes results from Tests 00-09
- Related: C556, C543, C813, C357, C124
