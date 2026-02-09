# C932: B Paragraph Body Vocabulary Gradient

**Tier:** 2
**Scope:** B
**Phase:** PARAGRAPH_EXECUTION_SEQUENCE

## Constraint

Within B paragraph body lines (lines 2+), vocabulary rarity decreases monotonically from early to late. Early body lines contain folio-unique and rare MIDDLEs (specification); late body lines contain universal MIDDLEs (generic execution). This refines C842's "flat body" finding: HT fraction is flat, but MIDDLE rarity is not.

## Evidence

Analysis of 80 B paragraphs with 8+ lines, divided into quintiles:

**MIDDLE rarity by paragraph quintile:**

| Rarity Class | Q0 | Q1 | Q2 | Q3 | Q4 | Trend |
|--------------|-----|-----|-----|-----|-----|-------|
| UNIQUE (1 folio) | 4.3% | 3.9% | 3.6% | 3.4% | 3.5% | r=-0.80 |
| RARE (2-5 folios) | 4.3% | 3.9% | 3.5% | 3.3% | 3.1% | r=-0.97 |
| UNIVERSAL (51+) | 74.3% | 75.6% | 77.2% | 78.4% | 80.0% | r=+0.92 |

**Vocabulary density by quintile:**

| Metric | Q0 | Q4 | Trend |
|--------|-----|-----|-------|
| Unique MIDDLEs / token | 17.6% | 13.8% | r=-0.91 |
| Hapax rate | 17.6% | 13.8% | r=-0.91 |

**Line properties by quintile:**

| Property | Q0 | Q4 | Trend |
|----------|-----|-----|-------|
| Tokens per line | 10.3 | 8.7 | r=-0.97 |
| Terminal suffix % | 30.2% | 25.2% | r=-0.89 |
| Bare suffix % | 46.8% | 51.3% | r=+0.90 |
| Iterate suffix % | 7.4% | 8.6% | r=+0.83 |
| K (heat) % | 11.8% | 12.6% | r=+0.84 |
| E (cool) % | 7.9% | 9.1% | r=+0.83 |

All correlations computed across 5 quintiles.

## Interpretation

B paragraph bodies have a specification→execution gradient:

```
Line 1:     HEADER (HT identification, C840/C842)
Lines 2-N:  BODY
  Early body: SPECIFICATION
    - Longer lines (10.3 tokens)
    - More unique/rare vocabulary
    - More terminal suffixes (parameter setting)
    - Folio-specific compound MIDDLEs
  Late body: EXECUTION LOOP
    - Shorter lines (8.7 tokens)
    - More universal vocabulary
    - More bare suffixes (continuation)
    - More iterate suffixes (looping)
    - Higher kernel % (active control)
```

This is consistent with a "job card" model: early lines specify *what's different this time* (materials, parameters), late lines invoke a *generic control loop* that's largely shared across folios.

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C840 | EXTENDS - C840 establishes header/body; this reveals body internal gradient |
| C842 | REFINES - C842 shows HT step is flat in body; vocabulary rarity is NOT flat |
| C845 | COMPATIBLE - Self-containment: each paragraph specifies its own parameters |
| C671 | COMPATIBLE - MIDDLE novelty shape at folio level |

## Provenance

- Script: `scratchpad/spec_exec_vocabulary_test.py`
- Script: `scratchpad/line_role_gradient.py`
- Phase: PARAGRAPH_EXECUTION_SEQUENCE

## Status

CONFIRMED - All trend correlations |r| > 0.80.
