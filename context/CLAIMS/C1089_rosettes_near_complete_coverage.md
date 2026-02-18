# C1089: Rosettes Near-Complete Vocabulary Coverage

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** AZC
**Phase:** ROSETTES_SYSTEM_CLASSIFICATION (Phase 387-388H)
**Extends:** C438 (AZC practically complete basis, 83%)
**Strengthens:** C1095 (Rosettes metalayer status)
**Relates to:** C121 (49 instruction classes), C1000 (hub MIDDLEs)

---

## Statement

The Rosettes foldout contains 48/49 instruction classes (98.0%), 23/23 hub MIDDLEs (100%), and 93.1% of core B vocabulary (MIDDLEs appearing in 20+ folios: 67/72 covered). This significantly exceeds normal AZC folio coverage (83% per C438). Entropy analysis confirms the Rosettes samples the grammar more evenly than B corpus: macro-state entropy 1.767 vs 1.458, prefix role entropy 2.223 vs 1.997.

---

## Evidence

### Coverage Metrics

| Metric | Rosettes | Normal AZC (C438) | B Corpus |
|--------|----------|-------------------|----------|
| 49-class coverage | 48/49 (98.0%) | ~83% per folio | 49/49 (100%) |
| Hub MIDDLE coverage | 23/23 (100%) | — | 23/23 (100%) |
| Core vocabulary (20+ folio MIDDLEs) | 67/72 (93.1%) | — | 72/72 (100%) |

### Entropy Comparison (Higher = More Even Sampling)

| Distribution | B Corpus | Rosettes |
|-------------|----------|----------|
| Macro-state | 1.458 | 1.767 |
| Prefix role | 1.997 | 2.223 |

Rosettes samples all grammatical categories more evenly than running B text, consistent with a reference/index function rather than procedural execution.

---

## Interpretation

Near-complete vocabulary coverage with elevated entropy indicates the Rosettes foldout functions as a master vocabulary index or reference system, sampling the full grammatical space rather than executing within a subset of it. This is structurally distinct from both normal AZC (which achieves 83% coverage) and B (which achieves 100% but with skewed execution distributions).

---

## Method

- Class coverage: class_token_map.json (480 tokens to 49 classes)
- Hub MIDDLE coverage: BFolioDecoder.HUB_SUB_ROLE (23 entries)
- Core vocabulary: MIDDLEs with 20+ folio spread in B corpus
- Entropy: Shannon entropy of macro-state and prefix role distributions

**Script:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/_explainer_probe.py`

---

## Verdict

**NEAR_COMPLETE_COVERAGE**: Rosettes contains 98% of instruction classes, 100% of hub vocabulary, and 93% of core MIDDLEs, exceeding normal AZC coverage and sampling more evenly than B execution text.
