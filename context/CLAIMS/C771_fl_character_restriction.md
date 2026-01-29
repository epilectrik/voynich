# C771: FL Character Restriction

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

## Constraint

FL MIDDLE inventory is restricted to exactly 9 characters: {a, d, i, l, m, n, o, r, y}. FL excludes 6 of the 15 primitive characters: {c, e, h, k, s, t}.

## Evidence

From t1_fl_inventory.py:

**FL Character Census:**
- Characters used: a, d, i, l, m, n, o, r, y
- Total: 9 characters

**Excluded Characters:**
| Character | Role in Grammar |
|-----------|-----------------|
| k         | KERNEL (energy modulator) |
| h         | KERNEL (phase manager) |
| e         | KERNEL (stability anchor) |
| c         | Helper (appears in CC, EN, AX) |
| s         | Helper (appears in CC, EN, FQ, AX) |
| t         | Helper (appears in EN, AX) |

**FL MIDDLE Inventory (17 types):**
```
al, am, ar, dy, i, ii, im, in, l, ly, m, n, o, ol, r, ry, y
```

**Morphological Profile:**
- Mean MIDDLE length: 1.58 characters
- 93.8% have no SUFFIX
- 40.3% have no PREFIX

## Interpretation

FL's restricted alphabet defines a "primitive flow layer" in the grammar:
1. FL chars are the substrate for material movement
2. Kernel chars (k, h, e) provide energy/phase/stability modulation
3. Helper chars (c, s, t) provide additional modulation

Other roles (EN, CC, FQ, AX) build on FL's primitive character set by adding kernel and helper characters.

## Provenance

- t1_fl_inventory.json: characters_used, missing_primitives
- Relates to: C085 (10 single-char primitives), C768 (role-compound correlation)

## Status

CONFIRMED - FL uses a strict subset of grammar characters.
