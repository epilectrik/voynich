# C772: FL Primitive Substrate

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

## Constraint

FL provides the primitive character substrate for the grammar. Other roles (EN, CC, FQ, AX) are built by adding kernel characters (k, h, e) and helper characters (c, s, t) to FL-like bases. EN is the most kernel-enriched role at 60.7% kernel-containing MIDDLEs.

## Evidence

From t3_fl_primitive_substrate.py:

**Layer Architecture:**
```
LAYER 0: FL SUBSTRATE
  Characters: {a, d, i, l, m, n, o, r, y}
  Kernel chars: 0
  Example MIDDLEs: al, am, in, ol, ly, ry

LAYER 1: FL + KERNEL
  Characters: FL chars + {k, h, e}
  Many EN/FQ/AX MIDDLEs = FL base + kernel addition

LAYER 2: FULL GRAMMAR
  Characters: FL + kernel + {c, s, t}
  Complete vocabulary
```

**Kernel Distribution by Role:**
| Role | MIDDLEs | Any Kernel |
|------|---------|------------|
| FL   | 17      | 0.0%       |
| FQ   | varies  | 29.0%      |
| AX   | varies  | variable   |
| EN   | 61      | 60.7%      |
| CC   | 10      | 100.0%     |

**FL-Compatible MIDDLEs in Other Roles:**
- 32.9% of non-FL MIDDLEs use only FL characters
- 67.1% require kernel or helper characters

**Decomposition Example:**
Many EN/AX MIDDLEs can be decomposed as:
- FL characters + kernel characters only
- Confirms additive layer model

## Interpretation

The grammar has a three-layer character architecture:
1. **FL Layer (substrate):** Pure material flow using 9 primitive chars
2. **Kernel Layer (+k,h,e):** Energy/phase/stability modulation
3. **Full Layer (+c,s,t):** Complete grammar with helper modulation

FL is not a simplified version of other roles - it IS the primitive base that other roles elaborate. EN's 60.7% kernel rate makes it the primary "modulated flow" role.

## Provenance

- t3_fl_primitive_substrate.json: fl_compatible_rate, en_kernel_rate
- Relates to: C103-C105 (kernel operators), C770 (FL kernel exclusion), C771 (FL character restriction)

## Status

CONFIRMED - FL provides primitive substrate; kernel is additive modulation layer.
