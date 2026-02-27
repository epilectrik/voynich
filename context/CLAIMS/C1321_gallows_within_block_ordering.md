# C1321: Gallows Within-Block Ordering

**Tier:** 2
**Scope:** B
**Phase:** BLOCK_GALLOWS_ORDERING (463)
**Date:** 2026-02-26

## Finding

Gallows letters show strong positional ordering within visual text blocks. t-gallows clusters late while k/f/p cluster early:

- k: mean normalized position = 0.255 (n=17)
- p: mean normalized position = 0.281 (n=121)
- f: mean normalized position = 0.319 (n=12)
- t: mean normalized position = 0.700 (n=167)

The positional split is k/f/p (early, 0.255-0.319) vs t (late, 0.700):
- Opener (k/f) mean: 0.282 vs mode (p/t) mean: 0.524
- Mann-Whitney z=2.48, p=0.010
- Permutation p=0.002 (1000 shuffles, seed 42)

The 4x4 gallows transition matrix within blocks is highly non-uniform (chi-sq=64.88, df=9, p<0.001):
- k→t: 77%, p→t: 74%, f→t: 56% — universal flow toward t
- t→t: 72% — t self-continues in late-block position
- t→p: 25% — occasional return to p

131 blocks with 2+ gallows-initial paragraphs tested, 186 total within-block transitions.

## Interpretation

Gallows encode paragraph PHASE within a block (when), not paragraph TYPE (what — see C1322). The pattern is:
- k/f/p: initiation/specification phase (early block)
- t: continuation/sustained execution phase (late block)

This partially supports C869's opener/mode model but revises the grouping: the split is k/f/p vs t, not k/f vs p/t as C869 predicted. p behaves as an early-block gallows (position 0.281), not a distributed "mode" like t.

## Negative Control

Permutation test: gallows letters shuffled within each block, preserving block sizes. 1000 permutations produce null distribution centered at 0.000 positional difference. Observed opener-mode difference (0.242) falls outside 99.8% of null distribution.

## Extends

- C864 (gallows paragraph marker, 81.5%) — gallows are not just delimiters but carry positional information
- C865 (gallows folio position: k/f front-biased) — extends folio-level position bias to block-level ordering
- C867 (p-t transition dynamics: p self-continuing, t→p) — block-level transitions differ: t is self-continuing (72%) within blocks
- C1317 (block census) — blocks have internal ordered structure

## Revises

- C869 (Tier 3: f/k=openers, p/t=modes) — partially supported (k/f are early) but p is also early; the real split is k/f/p vs t, not k/f vs p/t

## Falsifiability

Would be falsified if t mean normalized position drops below 0.5 (i.e., t is no longer late-block), or if the transition matrix chi-squared becomes non-significant (p>0.01) with corrected block detection.

## Evidence Files

- `phases/BLOCK_GALLOWS_ORDERING/results/block_gallows_ordering.json` (T3)
