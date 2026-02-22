# C1197: Atom Extensibility Partition

**Tier:** 2
**Scope:** B
**Phase:** ATOM_EXTENSIBILITY (Phase 425)
**Depends on:** C1190 (MIDDLE behavioral atomicity), C901 (extended e stability gradient, A-scoped)

## Constraint

The 20 characters that appear in Currier B MIDDLEs fall into two classes:

| Class | Atoms | Count | Behavior |
|-------|-------|-------|----------|
| **EXTENSIBLE** | e, i | 2 | Support consecutive repetition at structural levels (1555 and 1554 tokens respectively) |
| **BINARY** | a, c, d, f, g, h, k, l, m, n, o, p, q, r, s, t, x, y | 18 | Present once or absent; never repeat consecutively except at trace noise levels (<15 tokens) |

Threshold: >20 tokens with consecutive repetition = structural. Trace-level repeats (ll=13, oo=12, hh=9, dd=4) are transcription artifacts or boundary collisions (e.g., hh only in ckhh/cphh gallows compounds).

## Evidence

Census of all 23,096 Currier B tokens with MIDDLEs:
- 188 unique MIDDLEs contain `ee` (1,555 tokens)
- 61 unique MIDDLEs contain `ii` (1,554 tokens)
- 14 atoms NEVER repeat: a, c, f, g, k, m, n, p, q, r, s, t, x, y
- 4 atoms show only trace repetition: d(4), h(9), l(13), o(12)

The extensibility partition creates **ratio families**: MIDDLEs sharing the same atom set but differing in e/i repetition count (e.g., ke/kee/keee, in/iin/iiin). 129 such families exist.

Extends C901 (extended e stability gradient) from Currier A to Currier B and adds the binary/extensible classification.

## Falsification

Would be falsified if a non-e/non-i character is found to repeat consecutively at structural levels (>20 tokens) in a validated H-track transcription.

## Provenance

- `phases/ATOM_EXTENSIBILITY/scripts/atom_extensibility_test.py` (T1)
- `phases/ATOM_EXTENSIBILITY/results/atom_extensibility_results.json`
