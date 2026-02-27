# C1355: Dark Successor Entropy Difference Is Partially Frequency-Mediated

**Tier:** 2
**Scope:** B
**Phase:** LAYERED_GRAMMAR_TEST (473)

## Constraint

The dark-bridge successor entropy difference (C1351: 2.59 vs 4.18 bits) survives frequency matching (bridge MIDDLEs of similar token frequency still show higher entropy: Z=-5.60, p<0.001) but collapses under subsampling (bridge MIDDLEs subsampled to dark observation counts show equivalent entropy: Z=-0.55, p=0.50). This means dark successor narrowness is partially genuine (frequency-matched result) and partially a sampling artifact (subsampling result). The true effect is between these bounds.

## Evidence

From layered_grammar_test.py test T1 (57 dark MIDDLEs, 76 bridge MIDDLEs with ≥5 classified successors):

**Frequency-matched comparison:**

| Population | Median entropy | N |
|------------|---------------|---|
| Dark MIDDLEs | 2.585 | 57 |
| Freq-matched bridge | 3.528 | varies |
| Mann-Whitney Z | -5.601 | |
| p | <0.001 | |

**Subsampled comparison (bridge subsampled to median dark n=8):**

| Population | Median entropy | N |
|------------|---------------|---|
| Dark MIDDLEs | 2.585 | 57 |
| Subsampled bridge | 2.666 | 70 |
| Mann-Whitney Z | -0.555 | |
| p | 0.505 | |

Dark median frequency: lower than bridge median frequency. The frequency-matched test finds bridge MIDDLEs with similar total B token counts, but those bridge MIDDLEs still accumulate more classified successor observations because they are more likely to be followed by classified tokens. Subsampling equalizes observation counts directly.

## Interpretation

C1351's Z=-7.45 finding is genuine at the frequency-matched level: bridge MIDDLEs of comparable rarity still show broader successor distributions. But when observation counts are equalized by subsampling, the effect vanishes. This means:

1. Dark MIDDLEs genuinely appear in more restricted grammar environments than frequency-matched bridge MIDDLEs (real effect)
2. But the magnitude of the entropy difference is inflated by sampling: with only ~8 successor observations, you mechanically can't observe many distinct classes

The true characterization is: dark MIDDLEs have **restricted successor environments** (fewer distinct contexts) rather than inherently narrow successor entropy. They appear in a limited set of grammatical neighborhoods, and the entropy reflects this environmental restriction rather than active grammar constraint.

## Provenance

- layered_grammar_test.json: test T1
- Refines: C1351 (dark successor entropy — the difference is real at frequency level but inflated at observation level)
- Extends: C1350 (dark atomistic distribution — restricted environments are consistent with folio-specific deployment)

## Status

CONFIRMED — dark successor entropy difference survives frequency matching (Z=-5.60) but collapses under subsampling (Z=-0.55). The effect is partially genuine, partially sampling artifact.
