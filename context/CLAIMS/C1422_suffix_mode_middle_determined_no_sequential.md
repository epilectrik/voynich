# C1422: Suffix Mode is MIDDLE-Determined Without Sequential Dependency

**Tier:** 2 (ESTABLISHED)
**Scope:** B, suffix, mode, MIDDLE, sequential, token-level
**Phase:** SUFFIX_MODE_CYCLING_MECHANISM (Phase 518)
**Extends:** C1338 (MIDDLE suffix selectivity), C1412 (MIDDLE dominates suffix determination), C1346 (contextual modulation decomposition)
**Relates to:** C1229 (alternating suffix modes), C1410 (suffix mode atom partition)

---

## Statement

Token-level suffix mode is ~80% MIDDLE-determined and ~20% contextually modulated, with NO meaningful sequential dependency. Joint token features (PREFIX + HEAD + TERMINAL) explain 21.4% of suffix mode entropy (accuracy 0.682, 1.33x baseline). Previous token mode adds only 1.64% beyond token features (CMI=0.0164 bits). The 0.3% raw sequential MI (MI=0.0027 bits) is fully absorbed by token identity features.

### Token-Level Mode Prediction Hierarchy

| Predictor | MI (bits) | % of H(mode) | N |
|-----------|-----------|---------------|---|
| Full MIDDLE (C1412) | 0.422 | 42.2% | 10,940 |
| Joint (PREFIX+HEAD+TERM) | 0.214 | 21.4% | 10,940 |
| HEAD only | 0.097 | 9.6% | 10,940 |
| TERMINAL only | 0.053 | 5.3% | 10,940 |
| PREFIX only | 0.028 | 2.8% | 10,940 |
| Previous token mode | 0.003 | 0.3% | 10,405 |
| Previous mode GIVEN features | 0.016 | 1.64% | 10,405 |

### Implication

Suffix mode cycling within paragraphs is NOT driven by a sequential alternation mechanism. Each token's mode is determined by its own MIDDLE identity (primarily the TERMINAL atom), with mild contextual modulation from PREFIX and environment. The appearance of "cycling" emerges from the mixture of Mode A and Mode B MIDDLEs in the paragraph vocabulary, not from any feedback or oscillation process.

---

## Falsification Criteria

1. If CMI(prev_mode; curr_mode | features) exceeds 5% of H(mode), sequential dependency is non-trivial
2. If a hidden state variable with memory is found that predicts token mode beyond MIDDLE identity, the MIDDLE-determined model is incomplete

---

## Method

- 10,940 Currier B tokens with non-MIXED suffix mode
- 10,405 sequential pairs within paragraphs
- Joint features: PREFIX + MIDDLE HEAD + MIDDLE TERMINAL (all base chars)
- Mutual information, conditional mutual information, majority-vote accuracy

**Script:** `phases/SUFFIX_MODE_CYCLING_MECHANISM/scripts/suffix_mode_mechanism.py` (T6)
**Results:** `phases/SUFFIX_MODE_CYCLING_MECHANISM/results/suffix_mode_mechanism.json`
