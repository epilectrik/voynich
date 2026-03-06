# C1535: i-Atom Categorically Excluded from PREFIX -- Iteration Mechanism Absent from Channel Selection

**Tier:** 2
**Scope:** GLOBAL, PREFIX, MIDDLE, atom, i-atom, exclusion, iteration, extensibility, C1197, C1204, C1205, C1394, C1499, C1511
**Phase:** PREFIX_ATOM_TAXONOMY (Phase 544)
**Date:** 2026-03-06

## Claim

The atom 'i' (iteration/extensibility in MIDDLE, C1197/C1204/C1205) is categorically absent from PREFIX position despite being one of the 6 MIDDLE MOD atoms {p,i,c,f,d,s}. The other 5 MIDDLE MODs all appear in PREFIX. PREFIX uses 15 of MIDDLE's 20 characters, excluding exactly {i,m,n,g,x}: i (iteration MOD), m (TRANSITION TERM), n (CONTAINMENT TERM), g (rare structural), x (rare coordinate). PREFIX cannot encode iteration depth, transition closure, or containment binding -- these are MIDDLE-internal concerns excluded from channel selection.

## Evidence

### Cross-slot atom inventory

| Slot | Character Count | Characters |
|---|---|---|
| PREFIX | 15 | a,c,d,e,f,h,k,l,o,p,q,r,s,t,y |
| MIDDLE | 20 | a,c,d,e,f,g,h,**i**,k,l,**m**,**n**,o,p,q,r,s,t,**x**,y |
| SUFFIX | 13 | a,d,e,g,h,i,l,m,n,o,r,s,y |

### MIDDLE MOD overlap

| MIDDLE MOD atom | In PREFIX? | In SUFFIX? |
|---|---|---|
| p | YES | NO (C1511) |
| i | **NO** | YES |
| c | YES | NO (C1511) |
| f | YES | NO (C1511) |
| d | YES | YES |
| s | YES | YES |

'i' is the ONLY MIDDLE MOD atom present in suffix but absent from PREFIX. Conversely, {p,f,c} are present in PREFIX but absent from suffix (C1511). The three slots partition the 6 MIDDLE MODs into overlapping but non-identical subsets.

### Jaccard similarities

- PREFIX-MIDDLE: 0.750 (15/20)
- PREFIX-SUFFIX: 0.474 (9/19)
- MIDDLE-SUFFIX: 0.650 (13/20)

## Interpretation

The i-exclusion from PREFIX is structurally coherent: PREFIX selects operational domain (channel), while 'i' encodes iteration depth within the MIDDLE instruction. Iteration is a parameter of the instruction, not a parameter of the channel. This parallels C1511 (suffix excludes {k,t,p,f,c} -- ACTION HEADs and EXECUTIVE MODs): each slot excludes the atoms that encode information belonging to a different slot. PREFIX excludes iteration (MIDDLE-internal), MIDDLE keeps everything, suffix excludes actions and parameters (PREFIX-internal). The three slots form a complementary partition of functional information.

## Falsification Criteria

1. If 'i' is found in any PREFIX at >0.1% rate
2. If another MIDDLE MOD atom (not i) is found absent from PREFIX
3. If i-exclusion can be explained by purely phonological/scribal constraints

## Source

`phases/PREFIX_ATOM_TAXONOMY/results/prefix_atom_taxonomy.json`
