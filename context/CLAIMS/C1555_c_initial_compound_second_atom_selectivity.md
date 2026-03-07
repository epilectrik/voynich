# C1555: c-Initial Compound Second-Atom Selectivity

**Tier:** 2
**Scope:** B, MIDDLE, atom, c-initial, h-atom, second-atom, selectivity, compound, positional, C1389, C1553, C1472, C1484
**Phase:** PHANTOM_MIDDLE_MECHANISM (Phase 547)
**Date:** 2026-03-06

## Claim

Of 55 c-initial compound MIDDLEs (3+ characters, 291 tokens), 49 (89.1%) contain the h atom -- but h is ALWAYS at position 2 or later, never at position 1. The construction pattern is c+[k/t/f/p]+h (e.g., ckh, cth, cfh, cph), where an intervening atom separates c from h. The ch bigram at positions 0-1 is categorically absent in compound MIDDLEs despite both c-initial and h-containing compounds being individually common. This demonstrates that the ch/sh positional partition (C1553) operates at bigram granularity: c and h are individually compatible in MIDDLE compounds, but their adjacency at the initial position is specifically prohibited.

## Evidence

### c-initial compound MIDDLE h-atom positioning

| Metric | Value |
|---|---|
| c-initial compound MIDDLEs (3+ chars) | 55 types, 291 tokens |
| Containing h atom | 49 types (89.1%) |
| h at position 1 (c+h adjacency) | 0 types (0%) |
| h at position 2+ | 49 types (100% of h-containing) |

### Common c-initial construction patterns

| Pattern | Example MIDDLEs | h position |
|---|---|---|
| c+k+h | ckh, ckhey, ckhy | Position 2 |
| c+t+h | cth, cthy | Position 2 |
| c+f+h | cfh, cfhy | Position 2 |
| c+p+h | cph, cphy | Position 2 |

### Contrast with s-initial compounds

s-initial compound MIDDLEs (3+ chars): 20 types, 176 tokens. Only 2 contain h (sche, sh) -- both at position 1 but these are 2-char primitives expanded. The s+h pattern is even rarer than c+h.

### Connection to C1553

The ch bigram absence at MIDDLE-initial is not simply a c-atom prohibition (c freely starts 55 compound types) or an h-atom prohibition (h appears in 89% of c-initial compounds). It is specifically the c-h ADJACENCY at positions 0-1 that is excluded. This confirms C1553 at sub-bigram resolution: the positional partition operates on the specific character pair, not on individual characters.

## Interpretation

The c atom in MIDDLE position functions as a main-loop modifier (C1389) that pairs with other modifier/HEAD atoms before eventually reaching h as a terminal. The intervening atom (typically k, t, f, or p) provides the HEAD or secondary modifier context. The ch bigram, by contrast, is a PREFIX-domain unit that selects operational domains at the instruction level (C1534, C1536). The second-atom selectivity ensures that c-initial MIDDLEs cannot be confused with ch PREFIXes even at the atom level.

## Falsification Criteria

1. If any c-initial compound MIDDLE with h at position 1 is discovered in the corpus
2. If the h-position pattern is shown to be a frequency artifact of limited c-initial vocabulary
3. If other MIDDLE-initial bigrams show comparable adjacency avoidance, weakening the ch-specificity claim

## Source

`phases/PHANTOM_MIDDLE_MECHANISM/results/phantom_middle_mechanism.json`
