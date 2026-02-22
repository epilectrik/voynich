# C1194: Position-Specific Pair Discrimination

**Tier:** 2
**Phase:** 423 (POSITIONAL_ATOMICITY)
**Scope:** Currier B atom behavioral profiles

## Statement

Near-identical atom pairs that are behaviorally indistinguishable with global (position-agnostic) profiles become clearly separated when measured with position-specific profiles. All 4 tested pairs show discrimination:

| Pair | Global r | PREFIX r | MIDDLE r | SUFFIX r | Min r | Verdict |
|------|----------|----------|----------|----------|-------|---------|
| k-t | 0.993 | 0.568 | 0.993 | --- | 0.568 | SEPARATED |
| d-o | 0.945 | 0.296 | 0.852 | 0.976 | 0.296 | SEPARATED |
| p-t | 0.935 | 0.467 | 0.867 | --- | 0.467 | SEPARATED |
| l-r | 0.919 | 0.806 | 0.935 | 0.971 | 0.806 | SEPARATED |

Global behavioral identity was masking genuine positional distinctions. Pairs that appeared redundant are operationally distinct — they merely share similar MIDDLE-position behavior while diverging in PREFIX deployment.

## Implications

1. The current behavioral feature set IS sufficient to distinguish atoms — the distinction was hidden by position-averaging
2. Gloss assignments for near-identical pairs (k="heat" vs t="transfer", d="mark" vs o="near") are potentially validated by PREFIX separation
3. The 18-atom vocabulary has at least 18 distinct behavioral signatures (no true redundancy), but this distinctness requires position-specific measurement

## Provenance

- Script: `phases/POSITIONAL_ATOMICITY/scripts/positional_atomicity_test.py` (T3)
- Strengthens: C1190, C1191
- Cross-references: C1065 (atom ordering grammar), C521 (kernel directional asymmetry)
