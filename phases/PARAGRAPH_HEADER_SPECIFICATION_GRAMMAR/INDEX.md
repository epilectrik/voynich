# Phase 614: Paragraph Header Specification Grammar

**Status:** COMPLETE
**Date:** 2026-03-20
**Blocks:** Phase 611 (C1772-C1777)
**Version:** 5.86

## Research Question

Does the paragraph header line function as a structured specification
register with internal positional grammar, and how does header content
relate to body composition beyond what the gallows type alone predicts?

## Blocking Tests

| Test | Question | Result | Verdict |
|------|----------|--------|---------|
| BT1 | Header predicts body beyond gallows+section+folio? | dR2=+0.020, z=1.98, p=0.045 | MARGINAL |
| BT2 | Monotonic position decay in prediction power? | pos2 r=0.238 declining to pos7 r=0.089 | PASS |
| BT3 | Header echo independent of gallows type? | R2=0.15 on BT-residualized body (n=75) | PASS |
| BT4 | Cross-folio header-body correspondence? | Stars r=0.123, Bio r=0.049, Herbal r=0.050, all p<0.01 | PASS |

## Key Findings

1. **Atom echo, not token echo** (C1786): Header-to-body coupling operates at
   atom resolution (z=6.18), not whole-token (z=0.90). C670's zero token
   coupling is preserved -- the echo is compositional, not lexical.

2. **Internal positional grammar** (C1787): Header positions 2-10 have
   monotonically decaying prediction power. Position 2 is strongest (r=0.238),
   dominated by sh-prefix tokens (22.2%). The header is not a flat bag of atoms.

3. **Specification register** (C1788): Headers concentrate executive/modifier
   atoms (p 7.8x, f 7.7x, h 1.9x, c 1.5x) while depleting thermal-work
   atoms (e 0.75x, k 0.72x). Fixed width ~10 tokens.

4. **Vocabulary exclusivity** (C1789): 86.0% of boundary token types never
   appear in bodies. Header non-BT tokens: 54.2% exclusive. Same atom pool,
   different token inventory.

5. **Complete uniqueness** (C1790): Zero duplicate lines (0/2420) or paragraphs
   (0/591). Zero near-duplicates (Jaccard>=0.8). Only 10 trigrams in 3+ folios.

6. **Universal grammar** (C1791): Atom echo is section-independent and
   survives gallows residualization. Incremental prediction beyond
   gallows+section is small but significant (dR2=+0.020, z=1.98, p=0.045).

## Constraints

| ID | Claim | Tier | Scope |
|----|-------|------|-------|
| C1786 | Header atom echo into body (z=6.18) not token echo (z=0.90) | 2 | B, paragraph, header, body, atom |
| C1787 | Header internal positional structure (pos2 r=0.238 decaying monotonically) | 2 | B, paragraph, header, position |
| C1788 | Header specification register (p 7.8x, f 7.7x enriched; e/k depleted) | 2 | B, paragraph, header, specification |
| C1789 | 86.0% boundary token types exclusive to boundaries | 2 | B, paragraph, header, vocabulary |
| C1790 | Zero duplicates at all levels (lines, paragraphs, near-dupes) | 2 | B, paragraph, uniqueness |
| C1791 | Universal atom echo, small increment beyond gallows+section (dR2=0.020) | 2 | B, paragraph, header, universal |

## Scripts

| Script | Runtime | Output |
|--------|---------|--------|
| header_specification_grammar.py | ~90s | header_specification_results.json |

## Verdict

**HEADER_SPECIFICATION_CONFIRMED**

Paragraph headers are a structured specification register operating at atom
resolution with internal positional grammar. The specification signal echoes
into body composition through shared atoms, not shared tokens -- resolving the
apparent contradiction between C670 (zero token coupling) and C1772 (gallows
predict body). Headers concentrate instruction-tier atoms ({p,f,c,h}) and
deplete thermal-work atoms ({e,k}). Each paragraph is a unique specification;
the grammar generates unique sequences from shared atoms. The header's
incremental information beyond gallows type is genuine but small (~2%
additional R2), meaning the gallows atom is the PRIMARY specification channel
and the remaining header tokens provide modest refinement.
