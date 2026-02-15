# C1067: Terminal Character Determines Compound Position

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE (Phase 380)
**Extends:** C1060 (gateway/terminal atoms), C521 (kernel ordering)
**Relates to:** C985 (character-level features insufficient for discrimination), C1065 (atom bigram grammar)

---

## Statement

The terminal character (last character) of an atom **predicts its position** within compound MIDDLEs (chi²=105.5, p=3.5e-12, V=0.231). Initial characters also predict position but more weakly (chi²=53.5, p=6.3e-6, V=0.164).

Terminal character positional signatures (n >= 10):

| Char | n | Mean pos | INIT | MED | FIN | Bias |
|------|---|----------|------|-----|-----|------|
| p | 24 | 0.075 | 20 | 2 | 2 | **INITIAL** (83%) |
| y | 36 | 0.249 | 15 | 12 | 9 | initial-leaning |
| l | 93 | 0.261 | 39 | 37 | 17 | **INITIAL** (42%) |
| h | 133 | 0.241 | 48 | 38 | 47 | neutral |
| k | 131 | 0.262 | 62 | 30 | 39 | initial-leaning |
| a | 36 | 0.258 | 16 | 13 | 7 | initial-leaning |
| e | 132 | 0.322 | 51 | 43 | 38 | neutral |
| i | 67 | 0.465 | 13 | 19 | 35 | **FINAL** (52%) |
| d | 125 | 0.397 | 36 | 21 | 68 | **FINAL** (54%) |
| c | 14 | 0.599 | 0 | 2 | 12 | **FINAL** (86%) |

**The kc paradox resolves:** kc is FINAL not because of k-content but because of c-terminal character. The 'c' terminal drives FINAL position (12/14=86%, mean=0.599). At token-level: kc is FINAL in 24/26=92.3% of token occurrences.

H3 (line-position hypothesis) rejected: kc-FINAL tokens do not differ in line position from kc-non-FINAL (MW p=1.0).

Initial character signatures: 'o'-initial atoms lean INITIAL (90/171=53%, mean=0.243). 'a'-initial atoms lean FINAL (56/144=39% FINAL, mean=0.415).

---

## Interpretation

The terminal character encodes a positional code for compound assembly:
- **Gateway characters** ('p', 'l', 'k'): atoms ending in these tend toward compound-INITIAL position
- **Terminal characters** ('c', 'd', 'i'): atoms ending in these tend toward compound-FINAL position
- **Neutral** ('h', 'e'): no strong positional bias

This resolves C1060's kc paradox completely: kc's FINAL preference is driven by the 'c' terminal, not the 'k' content. The k-kernel in kc is irrelevant to its compound position — what matters is that the atom ends in 'c', which is the strongest FINAL-directing character (86%). This is consistent with C985 (character-level features insufficient for MIDDLE discrimination) because positional encoding is orthogonal to discriminative encoding.

The initial-character effect (V=0.164 vs terminal V=0.231) suggests a weaker but complementary "opening character" code. Together, the initial and terminal characters form a positional addressing system: the first and last characters of an atom specify where it belongs in a compound.

---

## Method

- 996 atom observations from 449 compound MIDDLEs (type-level)
- Terminal character: last character of each atom string
- Initial character: first character of each atom string
- Position class: INITIAL (starts at index 0), MEDIAL (neither), FINAL (ends at compound end)
- Chi-square contingency: character x position-class table (filtered to chars with >= 10 observations)
- kc case study: type-level (n=14) and token-level (n=26) FINAL rate. H3 tested via Mann-Whitney on line positions.

**Script:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/scripts/morphological_joint_space.py`
**Results:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t5_terminal_character_bias.json`
