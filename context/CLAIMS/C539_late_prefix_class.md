# C539: LATE Prefix Morphological Class

**Tier:** 2
**Scope:** B
**Status:** CLOSED
**Source:** ACTION_SEQUENCE_TEST

---

## Statement

Three prefixes (al, ar, or) form a distinct morphological class characterized by:
1. Shared [VOWEL]+[LIQUID] structural pattern
2. Strong line-final positional preference (3.78x enrichment)
3. Suffix depletion (68-70% suffixless vs 49.5% baseline)
4. Short MIDDLE preference (om, am, y enriched)

These are designated "LATE prefixes" due to their line-end clustering.

---

## Evidence

### Positional Clustering

| Prefix | Mean Line Position | Token Count |
|--------|-------------------|-------------|
| al | 0.692 | 173 |
| ar | 0.744 | 136 |
| or | 0.664 | 173 |
| **Total** | **0.70** | **482** |

Position scale: 0 = line start, 1 = line end.

### Line-Final Enrichment

| Metric | Value |
|--------|-------|
| LATE tokens at absolute line end | 191/482 (39.6%) |
| Baseline (any token at line end) | 10.5% |
| **Enrichment** | **3.78x** |

### Suffix Depletion

| Prefix | No-Suffix Rate | Baseline |
|--------|---------------|----------|
| al | 43.9% | 49.5% |
| ar | **68.4%** | 49.5% |
| or | **70.5%** | 49.5% |

ar and or strongly resist suffixes, suggesting terminal form status.

### Contrast with ol (V+L but MIDDLE position)

| Prefix | Position | No-Suffix Rate | Classification |
|--------|----------|---------------|----------------|
| al | 0.692 (LATE) | 43.9% | LATE class |
| ar | 0.744 (LATE) | 68.4% | LATE class |
| or | 0.664 (LATE) | 70.5% | LATE class |
| ol | 0.560 (MIDDLE) | 27.8% | CORE_CONTROL |

ol shares V+L morphology but has opposite suffix behavior (suffix-requiring, not depleted) and MIDDLE position. V+L is necessary but not sufficient for LATE class membership.

### SHORT MIDDLE Preference

MIDDLEs enriched with LATE prefixes:

| MIDDLE | Enrichment |
|--------|------------|
| om | 15.33x |
| ched | 9.58x |
| am | 6.69x |
| y | 5.44x |
| ai | 4.13x |
| o | 3.57x |
| ain | 3.55x |

LATE prefixes combine preferentially with minimal/short MIDDLEs.

### Context Transitions

When LATE tokens are not line-final, they are followed by:

| Following Prefix | Rate |
|-----------------|------|
| (none/prefixless) | 21.0% |
| ch | 16.5% |
| qo | 10.0% |
| sh | 8.9% |
| ot | 8.9% |

ENERGY operators (ch, qo, sh) follow LATE tokens, suggesting cycle reset.

### Vocabulary Provenance

LATE prefix is a **B-internal grammatical operation** applied to PP vocabulary:

| Level | B-Exclusive | Shared with A |
|-------|-------------|---------------|
| **Tokens** (full words) | **85.4%** (176/206) | 14.6% (30/206) |
| **MIDDLEs** | 23.8% (19/80) | **76.2%** (61/80 PP) |

The MIDDLEs under LATE prefixes are predominantly PP (pipeline-participating), but B applies the LATE prefix itself to create B-exclusive token forms.

**Implication:** A provides discriminative content (MIDDLEs) through the pipeline; B decides where to apply LATE marking based on its own positional grammar. LATE prefixes are part of B's control infrastructure, not content flowing from A.

---

## Structural Interpretation

### Morphological Distinction

LATE prefixes are structurally opposite to ENERGY prefixes:

| Class | Pattern | Examples |
|-------|---------|----------|
| ENERGY | Consonant-initial | ch, sh, qo, tch, pch, dch |
| LATE | Vowel+Liquid | al, ar, or |

This is a fundamental morphological distinction, not just positional.

### Position in Control Loop

From ACTION_SEQUENCE_TEST phase:
- EARLY position (line start): 79.4% ENERGY_OPERATOR tokens
- MIDDLE position: Mixed roles (working phase)
- LATE position: 100% "OTHER" (non-CCM family)

The LATE prefixes occupy a grammatically distinct slot at line boundaries.

---

## What This Constraint Does NOT Say

- Does NOT claim semantic meaning for LATE prefixes
- Does NOT interpret what "completion" means procedurally
- Does NOT assume LATE prefixes encode output recording

Functional interpretations are Tier 3 (see INTERPRETATION_SUMMARY.md).

---

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C371 | Extends: PREFIX positional grammar now has quantified LATE cluster |
| C492 | Parallel: Different prefix, different positional constraint |
| C466-467 | Compatible: LATE class is distinct from intervention/core/anchor |

---

## Provenance

- Phase: ACTION_SEQUENCE_TEST
- Scripts: `action_sequence_mapping.py`, `prefix_semantic_analysis.py`, `late_prefix_analysis.py`, `late_provenance_check.py`
- Date: 2026-01-25
