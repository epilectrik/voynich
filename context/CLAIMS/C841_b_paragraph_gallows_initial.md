# C841: B Paragraph Gallows-Initial Markers

**Tier:** 2
**Scope:** B
**Phase:** B_PARAGRAPH_STRUCTURE

## Constraint

71.5% of B paragraph-initial tokens begin with gallows characters (p/t/k/f), matching the gallows-initial paragraph structure in Currier A. This shared boundary marker suggests parallel organizational logic.

## Evidence

From paragraph_analysis.json:

**First character of paragraph-initial tokens:**

| Character | Percentage |
|-----------|------------|
| p | 43.6% |
| t | 19.3% |
| o | 12.0% |
| k | 5.5% |
| f | 3.1% |
| **Gallows total** | **71.5%** |

**Comparison to Currier A:**
- A paragraphs: defined by gallows-initial lines (C827)
- B paragraphs: 71.5% gallows-initial (this constraint)

The same boundary marker is used in both systems.

## Interpretation

Gallows characters (p, t, k, f) serve as **paragraph boundary markers** across both Currier A and Currier B. This is a manuscript-wide organizational convention, not system-specific.

The dominance of `p` (43.6%) in B parallels the prevalence of `p`-initial gallows in the manuscript generally.

## Provenance

- Script: `phases/B_PARAGRAPH_STRUCTURE/investigate_paragraphs_v2.py`
- Data: `phases/B_PARAGRAPH_STRUCTURE/results/paragraph_analysis.json`
- Depends: C827 (A paragraph operational unit)

## Status

CONFIRMED - Direct count from paragraph-initial tokens.
