# C1218: PREFIX Internal Positional Grammar

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** PREFIX_ATOM_ROLES (Phase 434)
**Extends:** C1001 (PREFIX dual encoding), C1193 (PREFIX composition low additivity)
**Relates to:** C1209 (MIDDLE atom positional syntax), C1191 (atom positional consistency)

---

## Statement

PREFIX characters have strong positional preferences within the PREFIX string, forming a base-modifier grammar. Characters partition into three roles: **dedicated modifiers** (position-0 only: q, d, f, p, y), **dedicated bases** (position-1/final only: e, h), and **dual-role** characters (appearing in both positions: o, k, l, t, c, a, r). This parallels the INITIAL/TERMINAL syntax in MIDDLEs (C1209) but operates on a different axis: where MIDDLE positions encode operational sequences, PREFIX positions encode mode selection.

### Character Positional Profiles

| Char | POS-0 | POS-1 | POS-2 | Total | Primary | Conc |
|------|-------|-------|-------|-------|---------|------|
| q | 4069 | 0 | 0 | 4069 | POS-0 | 100% |
| d | 1313 | 0 | 0 | 1313 | POS-0 | 100% |
| f | 57 | 0 | 0 | 57 | POS-0 | 100% |
| p | 381 | 0 | 0 | 381 | POS-0 | 100% |
| y | 314 | 0 | 0 | 314 | POS-0 | 100% |
| s | 2847 | 116 | 0 | 2963 | POS-0 | 96% |
| c | 3552 | 1031 | 0 | 4583 | POS-0 | 78% |
| h | 0 | 5821 | 1147 | 6968 | POS-1 | 84% |
| e | 0 | 548 | 0 | 548 | POS-1 | 100% |
| a | 309 | 1887 | 0 | 2196 | POS-1 | 86% |
| r | 41 | 309 | 0 | 350 | POS-1 | 88% |
| k | 642 | 2228 | 0 | 2870 | POS-1 | 78% |
| t | 813 | 1508 | 0 | 2321 | POS-1 | 65% |
| l | 869 | 1048 | 0 | 1917 | POS-1 | 55% |
| o | 3972 | 4683 | 0 | 8655 | POS-1 | 54% |

### Positional Role Classes

| Role | Characters | Definition |
|------|-----------|------------|
| Dedicated Modifier | q, d, f, p, y, s | >=96% POS-0 |
| Dedicated Base | h, e | 100% POS-1+ |
| Base-leaning | a, r, k | 78-88% POS-1 |
| Dual-role | t, l, o, c | 54-78% primary position |

### Population

- 18,032 two-character PREFIXes, 1,147 three-character PREFIXes
- 15 distinct characters participate in PREFIXes
- POS-2 occupied only by h (in 3-char PREFIXes: pch, tch, dch, lch, kch, fch, rch, lsh)

---

## Interpretation

PREFIXes are not frozen units but internally structured: a modifier selects a mode variant within a base-defined operational domain. The dedicated modifiers (q, d, f, p, y, s) never serve as bases, meaning they encode pure modification. The dedicated bases (h, e) define the fundamental operational mode. Dual-role characters (especially o) can function as either base or modifier depending on context: 'o' is the base in qo/so/to/po/do/ko but a modifier in ok/ot/ol/or.

This reinterprets C1193's low additivity finding: PREFIX characters ARE compositional, but they encode a different part-of-speech than the same characters in MIDDLEs. The "low additivity" reflects role-switching, not non-compositionality.

---

## Method

- 23,096 Currier B tokens with non-empty MIDDLEs
- Decomposed all PREFIXes into individual characters, recording position within PREFIX string
- Character frequency at each position, concentration = fraction at primary position
- 32 PREFIXes with 30+ tokens included

**Script:** `phases/PREFIX_ATOM_ROLES/scripts/prefix_atom_test.py` (T1)
**Results:** `phases/PREFIX_ATOM_ROLES/results/prefix_atom_results.json`
