# C1553: ch/sh-Initial Compound MIDDLE Categorical Absence

**Tier:** 2
**Scope:** B, MIDDLE, atom, ch, sh, compound, positional-partition, PREFIX, categorical-absence, C1178, C1394, C1534, C1552
**Phase:** PHANTOM_MIDDLE_MECHANISM (Phase 547)
**Date:** 2026-03-06

## Claim

The character bigrams ch and sh appear 5,821 times as PREFIX (ch=3,492, sh=2,329) but exactly 0 times as MIDDLE-initial bigram in compound MIDDLEs of length 3 or more. This is a categorical positional partition: ch/sh is a PREFIX-domain pattern that does not extend to MIDDLE position. The individual atoms c, s, and h all appear freely in MIDDLE position -- c-initial compound MIDDLEs number 55 types (291 tokens), s-initial compound MIDDLEs number 12 types (14 tokens), and h appears as terminal or dual-role in hundreds of MIDDLEs. The prohibition is specific to the ch and sh bigrams at MIDDLE-initial, not to any individual atom.

## Evidence

### MIDDLE-initial bigram census (Currier B corpus)

| Pattern | Types | Tokens | Note |
|---|---|---|---|
| ch as PREFIX | (not applicable) | 3,492 | PREFIX position |
| sh as PREFIX | (not applicable) | 2,329 | PREFIX position |
| ch-initial MIDDLE (all lengths) | 1 ("ch") | 4 | Bare bigram only |
| sh-initial MIDDLE (all lengths) | 1 ("sh") | 5 | Bare bigram only |
| **ch-initial compound MIDDLE (3+ chars)** | **0** | **0** | Categorical absence |
| **sh-initial compound MIDDLE (3+ chars)** | **0** | **0** | Categorical absence |
| c-initial compound MIDDLE (3+ chars) | 55 | 291 | Active pattern |
| s-initial compound MIDDLE (3+ chars) | 12 | 14 | Active pattern |

PREFIX:MIDDLE ratio for ch/sh bigram: **5,821:0**.

The bare MIDDLEs "ch" (4 tokens) and "sh" (5 tokens) exist but are single-bigram primitives, not compound constructions. No compound MIDDLE ever begins with the ch or sh bigram.

### Cross-system confirmation

ch/sh-initial compound MIDDLEs are absent across all three systems (B, A, AZC). The positional partition is manuscript-wide.

### Connection to phantom MIDDLEs

All 5 hazard phantom MIDDLEs (chey, shey, chedy, shedy, chol) identified in C1552 are instances of this categorical absence. They are ch/sh-initial compounds that the positional partition prevents from existing. The forbidden transition topology references MIDDLEs that the vocabulary system categorically excludes.

## Interpretation

ch/sh occupies a dedicated PREFIX niche in the instruction grammar. At PREFIX level, ch and sh are the most frequent bases (C1534, C1536) selecting specific MIDDLE families. The same bigram in MIDDLE position would create ambiguity between PREFIX and MIDDLE domains -- the positional partition maintains clean domain separation. This extends C1394 (HEAD+MOD*+TERM instruction encoding) by showing that the encoding grammar also prohibits PREFIX-domain bigrams from appearing as MIDDLE-initial sequences, keeping the two compositional domains unambiguous.

## Falsification Criteria

1. If any ch/sh-initial compound MIDDLE (3+ chars) is discovered in any corpus section
2. If the positional partition is shown to be a frequency artifact rather than categorical
3. If ch/sh-initial compound MIDDLEs are found in uncounted folios or variant transcriptions

## Source

`phases/PHANTOM_MIDDLE_MECHANISM/results/phantom_middle_mechanism.json`
