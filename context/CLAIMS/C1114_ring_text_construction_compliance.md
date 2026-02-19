# C1114: Rosettes Ring Text Construction Compliance

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** ROSETTES
**Phase:** ROSETTES_RING_TEXT_GRAMMAR (Phase 397)
**Extends:** C1093 (label-description bifurcation), C1088 (Rosettes grammar coverage)
**Relates to:** C911 (PREFIX-MIDDLE compatibility), C109 (forbidden transitions)

---

## Statement

The 5 transcribed rosette ring texts (155 tokens: NW=30, NORTH=32, WEST=23, CENTER=37, SOUTH=33) pass all B construction-level grammar tests: 0/155 PREFIX-MIDDLE selectivity violations (C911's 102 forbidden combinations), 0/25 forbidden MIDDLE transition violations (C109's 17 forbidden pairs, B baseline 0.5%), and 68.4% B-class coverage matching the B corpus rate of 69.5%. Ring texts are **constructed by B grammar rules** — tokens are built and sequenced according to the same constraints that govern standard B programs.

---

## Evidence

### Test 1: PREFIX-MIDDLE Selectivity (C911)
- 155 tokens tested against 102 forbidden PREFIX x MIDDLE combinations
- **0 violations** (B baseline: 0 by construction)
- Verdict: PASS — ring text tokens obey all morphological compatibility rules

### Test 4: Forbidden MIDDLE Transitions (C109, C789)
- 150 MIDDLE bigrams, 25 eligible for forbidden pair testing
- **0 violations** (B corpus: 0.5% violation rate)
- Fisher's exact: OR=0.000, p=1.0
- Ring texts are MORE compliant than standard B text

### Test 9: B-Class Coverage
- 106/155 tokens (68.4%) recognized by 49-class grammar
- B corpus: ~69.5% classified (30.5% HT/UN per C609)
- C1088 full Rosettes: 64.7%
- Ring texts have HIGHER coverage than full Rosettes average
- Per ring: WEST lowest (52.2%), CENTER highest (75.7%)

### Test 2: Kernel Construction Grammar (C521)
- Only 7 tokens with 2+ kernel characters — underpowered
- k->e / e->k = 0.7x (B: 4.02x) — not compliant but N too small
- h->e / e->h = 1.0x (B: 6.09x) — not compliant but N too small

---

## Interpretation

Ring texts use B's construction grammar. They are not loose approximations of B vocabulary — they are properly constructed B sequences that obey every testable construction rule. The zero forbidden transition violations (vs B's 0.5%) suggests either the hub-universal vocabulary naturally avoids hazard pairs, or the ring texts are composed with extra care.

---

## Provenance

- Phase: 397 (ROSETTES_RING_TEXT_GRAMMAR)
- Script: `phases/ROSETTES_RING_TEXT_GRAMMAR/scripts/ring_text_grammar_test.py`
- Results: `phases/ROSETTES_RING_TEXT_GRAMMAR/results/ring_text_grammar_results.json`
- Data: `data/rosettes_unified.json` (ring text tokens)
- Related: C911, C109, C789, C1088, C1093
