# C1514: Cross-system suffix atom inventory identical (A=B=13 atoms, JSD=0.050)

**Tier:** 2
**Scope:** GLOBAL, suffix, atom, cross-system, A, B, inventory, identity, JSD=0.050
**Phase:** SUFFIX_ATOM_TAXONOMY (Phase 540)

## Claim

Currier A and Currier B use IDENTICAL suffix atom inventories (both 13 single-char atoms, 0 system-exclusive atoms) with highly similar frequency distributions (JSD=0.050). B amplifies execution-related suffix atoms (d 2.0x, e 2.5x, i 2.9x) while A amplifies state/scope atoms (o 3.3x, h 1.7x, l 1.7x, s 2.0x). The most cross-system-stable suffix atom is y (ratio A/B=0.98). This extends C1499 (manuscript-wide shared substrate) to the suffix layer: suffix composition grammar is a GLOBAL property, not system-specific. The B-enriched atoms (d, e, i) are those involved in execution specification; the A-enriched atoms (o, h, l, s) are those involved in arrangement/monitoring description.

## Evidence

- Currier A suffixed tokens: 4,808 (33 unique suffixes)
- Currier B suffixed tokens: 11,151 (35 unique suffixes)
- A suffix atoms: 13 {a,d,e,g,h,i,l,m,n,o,r,s,y}
- B suffix atoms: 13 {a,d,e,g,h,i,l,m,n,o,r,s,y}
- A-only: 0; B-only: 0
- JSD(A suffix atoms, B suffix atoms) = 0.0497
- Key ratios (A/B): y=0.98, a=0.77, n=0.85, d=0.50, e=0.41, i=0.35, o=3.31, h=1.71, l=1.67, s=2.01
- B-enriched (ratio<0.5): e (0.41), i (0.35), d (0.50) -- all execution atoms
- A-enriched (ratio>1.5): o (3.31), h (1.71), l (1.67), s (2.01) -- all state/arrangement atoms

## Relationship to Prior Constraints

- **Extends C1499**: Shared substrate confirmed for suffix position, not just MIDDLE
- **Parallels C1503**: Bridge atoms redistribute across A/B (same inventory, different frequencies) -- suffix atoms show same pattern
- **Parallels C1507**: A prefers o-HEAD/arrangement in MIDDLE; A suffix also enriched for o (3.31x) confirming A's arrangement emphasis extends to suffix layer
- **Connects C1395**: Cross-system instruction encoding extends to suffix grammar -- same atoms, same HEAD+TERM structure, system-specific frequency weighting

## Source

`phases/SUFFIX_ATOM_TAXONOMY/results/suffix_atom_taxonomy.json` (T10)
