# C1215: Compound MIDDLE Slot Compliance

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** COMPOUND_SLOT_GRAMMAR (Phase 432)
**Relates to:** C1210 (MIDDLE slot syntax forbidden combinations), C1209 (positional grammar), C1190 (MIDDLE behavioral atomicity)

---

## Statement

Compound MIDDLEs (those containing embedded core MIDDLEs as substrings) obey the same C1210 forbidden INITIAL→TERMINAL combinations as atomic MIDDLEs. The forbidden pairs a→y, e→n, k→n are near-categorical in both populations. Compound slot syntax is weaker overall (V=0.329 vs V=0.416 atomic, MI=1.09 vs 1.44) reflecting greater INITIAL→TERMINAL diversity, but the forbidden rules are scale-invariant.

### C1210 Forbidden Pair Compliance

| Pair | Atomic obs/total | Rate | Compound obs/total | Rate |
|------|-----------------|------|-------------------|------|
| a→y | 0/1,593 | 0.000% | 1/1,422 | 0.070% |
| e→n | 0/2,163 | 0.000% | 1/3,972 | 0.025% |
| k→n | 0/542 | 0.000% | 0/475 | 0.000% |

### Slot Syntax Strength

| Population | N | Cramer's V | MI (bits) |
|------------|---|-----------|-----------|
| Atomic | 8,335 | 0.416 | 1.440 |
| Compound | 7,818 | 0.329 | 1.090 |

Compounds have weaker overall slot syntax because they span more diverse INITIAL→TERMINAL combinations (the intervening embedded atoms create paths to TERMINAL characters that atomic MIDDLEs cannot reach). But the forbidden combinations remain inviolable.

---

## Method

- 16,153 Currier B tokens with MIDDLE length >= 2
- Compound identification via MiddleAnalyzer (core MIDDLEs = 20+ folios, 72 core types)
- 8,335 atomic, 7,818 compound
- INITIAL = first character, TERMINAL = last character of whole MIDDLE

**Script:** `phases/COMPOUND_SLOT_GRAMMAR/scripts/compound_slot_test.py` (T1)
**Results:** `phases/COMPOUND_SLOT_GRAMMAR/results/compound_slot_results.json`
