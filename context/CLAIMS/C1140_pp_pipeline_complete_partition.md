# C1140: PP Pipeline Is a Complete Four-Way Partition

**Tier:** 2
**Status:** Active
**Scope:** A-B pipeline architecture
**Phase:** 408 (PP_PIPELINE_ATOM_DECOMPOSITION)

## Finding

The 404 PP MIDDLEs (shared A/B vocabulary) partition into exactly four mutually exclusive, collectively exhaustive populations:

| Population | Count | Function | Key Properties |
|-----------|-------|----------|----------------|
| Bridge MIDDLEs | 85 | Cross-system dynamical backbone (C1013) | SHORT (2.27 chars), 67% atomic |
| Non-bridge matched | 4 | Edge-case grammar participants | c, ch, cho, otc; AUXILIARY-dominant |
| Dark pipeline | 300 | HT/UN identification substrate (C1137) | 66.7% compound, Herf 0.716 |
| B-absent phantoms | 15 | A-present, B-absent artifacts | All ch- or sh- prefixed, 0 A tokens |

Partition is exhaustive (85 + 4 + 300 + 15 = 404) with all six pairwise intersections empty.

### Non-Bridge Matched Profiles

| MIDDLE | Classes | Dominant Role | B Tokens | B Folios |
|--------|---------|---------------|----------|----------|
| c | 2 (19, 27) | AUXILIARY | 5 | 5 |
| ch | 5 (1, 4, 16, 17, 18) | AUXILIARY | 4 | 4 |
| cho | 1 (13) | AUXILIARY | 3 | 2 |
| otc | 1 (12) | AUXILIARY | 1 | 1 |

All four are short (1-3 chars), non-compound, low-frequency, AUXILIARY-dominant. They are grammar-classified but not cross-system bridges.

### B-Absent Phantom Profile

All 15 phantoms share a ch- or sh- prefix (11 ch-, 4 sh-), 40% compound, mean length 3.6 chars, and have **zero A tokens** (mean_a_token_count = 0.0). These are morphologically extracted MIDDLEs that appear as substrings of A tokens but never surface as independent tokens in either system.

## Evidence

- Phase 408, Test 1: Set algebra verification on 404 PP MIDDLEs
- Six pairwise intersection tests: all empty

## Implication

The A-B vocabulary pipeline has a closed, four-population architecture. Three populations are functionally active (bridges, dark pipeline, non-bridge matched) and one is artifactual (phantoms). The pipeline is now fully decomposed with no unaccounted vocabulary.

## Provenance

- Source: Phase 408, Test 1
- Related: C1013 (85 bridges), C1135 (300 dark pipeline), C1137 (100% HT substrate), C1139 (bridge-dark disjoint)
