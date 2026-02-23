# C1219: Base Character Determines MIDDLE Content

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** PREFIX_ATOM_ROLES (Phase 434)
**Extends:** C1218 (PREFIX positional grammar), C911 (PREFIX-MIDDLE compatibility)
**Relates to:** C1207 (atom correlation clusters), C1217 (lane atom content separation), C1001 (PREFIX dual encoding)

---

## Statement

The base (final) character of a PREFIX is the dominant predictor of that PREFIX's MIDDLE atom content. PREFIXes sharing the same base character carry nearly identical MIDDLE profiles (within-base mean cosine = 0.950), while PREFIXes with different bases carry divergent profiles (between-base mean cosine = 0.515). The within/between ratio of 1.84 establishes base character as the primary axis of PREFIX differentiation.

### Base Group MIDDLE Profiles

| Base | PREFIXes | N | ITER | ENRG | STAB | MON | CLOS | STRC | FREE |
|------|----------|---|------|------|------|-----|------|------|------|
| a | da, ka, sa, ta | 1887 | 80% | 11% | 0% | 2% | 2% | 1% | 0% |
| o | qo, so, do, ko, po, to | 4683 | 7% | 42% | 14% | 15% | 5% | 5% | 11% |
| h | ch, sh, pch, tch, dch, lch, lsh, kch, fch, rch | 6968 | 4% | 10% | 32% | 8% | 31% | 11% | 3% |
| e | ke, te | 548 | 3% | 4% | 26% | 2% | 53% | 12% | 1% |
| k | ok, lk, yk | 2228 | 41% | 5% | 27% | 2% | 18% | 5% | 0% |
| t | ot, ct | 1508 | 37% | 6% | 23% | 3% | 22% | 6% | 0% |
| r | ar, or | 309 | 57% | 9% | 5% | 3% | 9% | 13% | 1% |
| l | al, ol | 1048 | 19% | 23% | 19% | 6% | 21% | 8% | 2% |

### Base Character Functional Domains

| Base | Dominant Axis | Interpretation |
|------|--------------|----------------|
| a | ITERATION (80%) | Metadata/parameter carrier |
| o | ENERGY (42%) | Heating/energy operations |
| h | STABILITY+CLOSURE (63%) | Stabilization and sealing |
| e | CLOSURE (53%) | Completion/finishing |
| k | ITERATION+STABILITY (68%) | Vessel parametric operations |
| t | ITERATION+STABILITY (60%) | Mixed (but ct is outlier at 72% MONITORING) |
| r | ITERATION (57%) | Output/resolution metadata |
| l | Mixed | Balanced across axes |

### Cosine Similarity

- Within-base mean cosine: 0.950 (73 pairs)
- Between-base mean cosine: 0.515 (392 pairs)
- Ratio: 1.84

---

## Interpretation

The base character defines which MIDDLE atom content is permitted, functioning as a mode selector:
- **a-base** PREFIXes specify iteration parameters (a, i, n atoms) -- pure metadata
- **o-base** PREFIXes specify energy operations (k, l atoms) -- the heating lane (C1217)
- **h-base** PREFIXes specify stability and closure (e, d, y atoms) -- the cooling/monitoring lane
- **e-base** PREFIXes specify completion/closure (d, y atoms)

This aligns with C1217's two-stream architecture: o-base PREFIXes are the ENERGY lane, h-base PREFIXes are the STABILITY lane, and a-base PREFIXes are the ITERATION (metadata) stream.

The modifier character (C1218 POS-0) then selects a variant within the base-defined domain. Within each base group, modifiers create subtle but measurable differentiation (see C1220).

---

## Method

- 23,096 Currier B tokens with non-empty MIDDLEs
- Grouped 32 PREFIXes (30+ tokens each) by their final character
- Computed per-PREFIX MIDDLE atom profiles using AXIS map from C1207
- Calculated pairwise cosine similarity within and between base groups
- 73 within-base pairs, 392 between-base pairs

**Script:** `phases/PREFIX_ATOM_ROLES/scripts/prefix_atom_test.py` (T2)
**Results:** `phases/PREFIX_ATOM_ROLES/results/prefix_atom_results.json`
