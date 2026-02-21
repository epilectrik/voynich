# C1178: Phantom MIDDLEs Are Morphologically Isolated ch/sh Naming Slots

**Tier:** 2
**Scope:** B, dark pipeline, phantoms
**Phase:** DARK_PIPELINE_COMBINATORICS (Phase 419)
**Depends on:** C1140, C475

## Statement

The 15 B-absent phantom MIDDLEs (C1140: all ch/sh-prefixed, 0 A tokens) are morphologically isolated from the productive dark pipeline. 0/15 achieve VALID_UNFILLED status; 11/15 are PARTIALLY_VALID (pass bridge-atom or C475 tests but fail analogous-form test); 4/15 are STRUCTURALLY_INVALID (fail all testable criteria). The critical failure: zero dark-pipeline MIDDLEs share the ch/sh-initial MIDDLE morphology, making the phantoms a dead naming pattern with no productive analogs in B. The 6 compound phantoms (chee, cheo, cheod, chod, chot, sheo) contain bridge atoms (ee, eo, eod, od, ot) and are C475-compatible, but were never instantiated. The 9 atomic phantoms (cha, chd, che, ches, chk, chs, shch, she, sho) have no bridge atom content.

## Evidence

### Classification Summary
| Category | Count | Examples |
|----------|-------|---------|
| VALID_UNFILLED | 0 | - |
| PARTIALLY_VALID | 11 | chee, cheo, chod, cheod, sho |
| STRUCTURALLY_INVALID | 4 | cha, chk, shch, she |

### Test Results by Phantom Type
| Phantom Type | n | Bridge Pass | C475 Pass | Analogous Pass |
|-------------|---|-------------|-----------|----------------|
| Compound (ch/sh + atom) | 6 | 6/6 | 4/6 | 0/6 |
| Atomic | 9 | 0/9 testable | 6/9 | 0/9 |

### Prefix Distribution
| Prefix | Count |
|--------|-------|
| ch- | 11 |
| sh- | 4 |

## Interpretation

The phantoms represent a naming morphology (ch/sh-initial MIDDLEs) that exists in the A-system's morphological possibility space but was never instantiated in B. In the standard morphological extraction, "ch" and "sh" are typically extracted as PREFIXES, not as parts of the MIDDLE. The phantoms are MIDDLEs that INCLUDE the ch/sh component — an atypical morphological pattern. Since no dark-pipeline MIDDLEs share this pattern, the ch/sh-initial MIDDLE slot is a dead branch of the naming system: morphologically possible but never filled by actual material identifiers. This is consistent with the Tier 4 interpretation that the naming system can generate more names than it needs (finite material set requires only a subset of possible names).

## Provenance

- Phase 419 Test 5: PHANTOM_MIDDLE_ANALYSIS
- Script: `phases/DARK_PIPELINE_COMBINATORICS/scripts/dark_pipeline_combinatorics.py`
- Results: `phases/DARK_PIPELINE_COMBINATORICS/results/dark_pipeline_combinatorics.json` -> test5_phantom_middle_analysis
