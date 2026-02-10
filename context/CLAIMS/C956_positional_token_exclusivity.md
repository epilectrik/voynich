# C956: Positional Token Exclusivity

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR

## Statement

192 out of 334 common token types (57.5%) are excluded from at least one positional zone (INITIAL, MEDIAL, or FINAL). This is 2.72x the shuffle expectation (70.6). The effect is STRUCTURAL — it survives when token identity is destroyed but role/position are preserved.

## Evidence

- 334 token types with 10+ occurrences in Currier B (2,420 lines)
- 192 zone-exclusive tokens vs 70.6 shuffle mean (p = 0.000, max shuffle = 89)
- 16 tokens with Fisher exact p < 0.01
- Suffix-stripping pass: 157/331 stems exclusive; 93 survive suffix stripping (true lexical), 99 lost (suffix-driven)
- Negative control: effect survives on synthetic corpus (STRUCTURAL, not lexical)

## Notable Tokens

- `aiin` (351 occurrences): never INITIAL (Fisher p = 2.4e-17)
- `al` (186): never INITIAL (p = 1.8e-09)
- `chdy` (132): never INITIAL (p = 9.5e-07)
- `sheedy` (82): never FINAL (p = 1.9e-04)

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/01_positional_token_exclusivity.py`
- Cross-referenced with Test 00 negative control
