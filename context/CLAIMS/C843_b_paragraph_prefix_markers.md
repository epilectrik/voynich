# C843: B Paragraph Prefix Identification Markers

**Tier:** 2
**Scope:** B
**Phase:** B_PARAGRAPH_STRUCTURE

## Constraint

The prefixes pch- and po- account for 33.5% of B paragraph-initial tokens with 78-86% HT rate, functioning as paragraph identification markers rather than operational instructions.

## Evidence

From paragraph_analysis.json:

**Top prefixes in paragraph-initial tokens:**

| Prefix | Frequency | HT Rate |
|--------|-----------|---------|
| pch | 16.9% | 78.8% |
| po | 16.6% | 85.6% |
| sh | 11.6% | 94.1% |
| tch | 6.5% | 65.8% |
| to | 4.4% | 80.8% |

**Combined pch- + po-:** 33.5% of initiators, predominantly HT

**Contrast with operational prefixes:**

| Prefix | HT Rate | Role |
|--------|---------|------|
| qo | 35.7% | Mostly operational (kernel-adjacent) |
| ok | 40.9% | Mixed |

## Interpretation

Paragraph-initial tokens serve an **identification function** rather than operational execution:
1. High HT rate (78-94%) means they're outside the 49-class grammar
2. Specific prefixes (pch-, po-, sh-) cluster in this position
3. These are not random HT tokens but a specific marker vocabulary

This parallels RI tokens in Currier A paragraphs: specific vocabulary for identification, separate from operational vocabulary.

## Provenance

- Script: `phases/B_PARAGRAPH_STRUCTURE/investigate_paragraphs_v2.py`
- Data: `phases/B_PARAGRAPH_STRUCTURE/results/paragraph_analysis.json`
- Depends: C840 (paragraph mini-program), C166 (HT identification)

## Status

CONFIRMED - Prefix distribution directly observed.
