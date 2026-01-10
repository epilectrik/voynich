# C420: Currier A Folio-Initial Positional Exception

**Tier:** 2 | **Status:** CLOSED | **Scope:** A

---

## Statement

In Currier A, the first token of a folio occupies a structurally exceptional position that permits otherwise illegal but morphologically compatible prefix variants (notably C+vowel forms such as `ko-`, `to-`, `po-`), which do not occur elsewhere in the registry.

---

## Evidence

### Quantitative

| Metric | Value |
|--------|-------|
| Folios analyzed | 48 |
| Position-1 classification failure | 75% |
| Position-2 classification failure | 31% |
| Position-3 classification failure | 29% |
| C+vowel in position 1 | 47.9% |
| C+vowel in position 2 | 0.0% |
| C+vowel in position 3 | 0.0% |
| Fisher exact p-value | < 0.0001 |

### C+vowel Prefix Distribution (Position 1 Only)

| Prefix | Count | % of Position 1 |
|--------|-------|-----------------|
| po- | 9 | 18.8% |
| ko- | 6 | 12.5% |
| to- | 3 | 6.2% |
| fo- | 2 | 4.2% |

### Morphological Compatibility

The position-restricted variants share morphological structure with standard families:

| Variant | Standard Family | Suffix Jaccard | Direct Equivalents |
|---------|-----------------|----------------|-------------------|
| ko- | ok- | 0.214 | koaiin↔okaiin, koar↔okar |
| to- | ot- | (inferred) | - |

100% of ko- suffixes are valid ok- suffixes, ruling out gibberish or damage.

### Falsified Alternatives

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| Random noise | REJECTED | p < 0.0001 |
| Section-conditioned | REJECTED | Quire chi2 p = 0.86 |
| Damage artifacts | REJECTED | Morphological compatibility |
| Sequential enumeration | REJECTED | No ordering pattern, 97.9% unique |
| HT intrusion | REJECTED | Different failure type from positions 2-3 |

---

## Interpretation

This reflects **positional tolerance** at physical (codicological) boundaries — a phenomenon common in medieval registries where boundary positions permit variant forms.

This does **NOT** imply:
- Chapter markers or headers
- Functional labeling or titles
- Numbering or enumeration systems
- New semantic categories or subsystems

---

## Relationship to Other Constraints

| Constraint | Status |
|------------|--------|
| C240 (8 Marker Families) | **UNCHANGED** — ko-, po-, to- are positional variants, not new families |
| C234 (POSITION_FREE) | **UNCHANGED** — applies to entries, not folio boundary artifacts |
| C267 (Compositional Morphology) | **CONSISTENT** — variants use same PREFIX+MIDDLE+SUFFIX structure |

---

## Additional Observations

### Recto/Verso Asymmetry

| Page Side | C+vowel % | p-value |
|-----------|-----------|---------|
| Recto | 29.2% | |
| Verso | 66.7% | 0.02 |

C+vowel variants show verso preference (not required for constraint, but documented).

### Token Uniqueness

97.9% of position-1 tokens are unique (47/48). Only `pchor` repeats (19r, 21r). This argues against enumeration or sequential systems.

---

## Phase Documentation

Research conducted: 2026-01-09

Scripts archived at: `phases/exploration/first_token_*.py`

Data files:
- `phases/exploration/first_token_data.json`
- `phases/exploration/first_token_morphology_results.json`
- `phases/exploration/first_token_position_results.json`

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
