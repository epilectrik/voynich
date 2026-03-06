# C1512: MIDDLE terminal atom dominates suffix content selection (V=0.513)

**Tier:** 2
**Scope:** B, MIDDLE, suffix, atom, terminal, gating, content, selectivity, V=0.513
**Phase:** SUFFIX_ATOM_TAXONOMY (Phase 540)

## Claim

MIDDLE terminal atom is the PRIMARY determinant of suffix content (V=0.513), stronger than MIDDLE HEAD atom (V=0.305, 1.68x weaker). Terminal gating is a two-level mechanism: (1) opacity gates whether suffix attaches at all (h-terminal 98.7% vs y-terminal 1.6% vs n-terminal 0.8%), and (2) WHICH suffix atoms appear is terminal-determined. h-terminal selects e-first suffix (753/1267 = 59.4%, i.e., e-initial suffixes like -edy, -ey, -eey). bare MIDDLE terminals (no explicit terminal atom) select a-first (2964) and e-first (1785) broadly. r-terminal routes to a-first (279/383 = 72.8%). l-terminal routes to o-first (159/431 = 36.9%) and a-first (110/431 = 25.5%). The suffix content is thereby controlled at the MIDDLE's exit point, not its entry point.

## Evidence

- V(MIDDLE TERMINAL x suffix first-atom) = 0.513
- V(MIDDLE HEAD x suffix first-atom) = 0.305
- Ratio TERM/HEAD = 1.68x
- Suffix rate by MIDDLE terminal:
  - bare: 89.0% (8963/10066 tokens)
  - h-terminal: 98.7% (1267/1284)
  - r-terminal: 19.5% (383/1962)
  - l-terminal: 16.8% (431/2568)
  - m-terminal: 4.2% (12/289)
  - y-terminal: 1.6% (77/4780)
  - n-terminal: 0.8% (18/2147)
- h-terminal top suffix first-atom: e (753, 59.4%)
- bare top suffix first-atom: a (2964, 33.1%), e (1785, 19.9%)
- r-terminal top: a (279, 72.8%)
- l-terminal top: o (159, 36.9%), a (110, 25.5%)

## Relationship to Prior Constraints

- **Extends C1412**: Confirmed MIDDLE terminal dominance at suffix atom level (not just suffix string)
- **Extends C1440-C1445**: Three-tier opacity confirmed with full content profiles for each tier
- **Refines C1413**: PREFIX-SUFFIX is MIDDLE-mediated specifically through TERMINAL atom, not HEAD
- **Connects C1485**: HEAD x TERM affinity structure (e->y 72.7%, a->n/m 59-60%) now traced through to suffix selection

## Source

`phases/SUFFIX_ATOM_TAXONOMY/results/suffix_atom_taxonomy.json` (T6, T7)
