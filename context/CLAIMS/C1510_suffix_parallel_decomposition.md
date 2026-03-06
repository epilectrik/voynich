# C1510: Suffix parallel HEAD+TERM decomposition with attenuated HEAD and amplified TERM

**Tier:** 2
**Scope:** B, suffix, atom, decomposition, HEAD, TERM, parallel, position, category
**Phase:** SUFFIX_ATOM_TAXONOMY (Phase 540)

## Claim

The suffix layer shows PARALLEL HEAD+TERM decomposition analogous to MIDDLE: first-atom selects operational category (V=0.277), last-atom encodes positional scope (R2=0.059). However, suffix HEAD is attenuated to 53% of MIDDLE HEAD category selectivity (V=0.277 vs 0.520), while suffix TERM positional signal is amplified 1.68x above MIDDLE TERM (R2=0.059 vs 0.035). Only 5 atoms appear as suffix terminals: y (53.5%), n (19.5%), r (13.1%), l (10.8%), m (3.1%). The suffix is a NARROWER compositional domain -- same grammar, compressed inventory, shifted emphasis from domain-selection toward positional-scope.

## Evidence

- Multi-atom suffixed tokens: N=9,515
- V(suffix first-atom x category) = 0.277; V(MIDDLE HEAD x category) = 0.520; ratio = 0.53
- R2(suffix last-atom -> position) = 0.059; R2(MIDDLE TERM -> position) = 0.035; ratio = 1.68
- First-atom distribution: a (36.1%), e (26.7%), d (10.5%), h (9.0%), o (7.9%), ee (6.3%)
- Last-atom distribution: y (53.5%), n (19.5%), r (13.1%), l (10.8%), m (3.1%)
- m-terminal suffix: mean position 0.924, line-final 83.2% (7.89x enrichment)
- Verdict: PARALLEL_DECOMPOSITION (first/last ratio >1.3x on both axes)

## Relationship to Prior Constraints

- **Extends C1408**: Confirmed HEAD->TERM structure at full resolution with quantified attenuation/amplification
- **Extends C1440-C1445**: m-terminal line-final (7.89x) in suffix matches MIDDLE m-terminal (196x) -- same closure grammar, lower magnitude
- **Parallels C1393-C1394**: Same HEAD+MOD*+TERM grammar at suffix level, confirming universal construction principle
- **Connects C1487**: 5 suffix terminal atoms are subset of 6 MIDDLE terminal atoms (g absent as expected)

## Source

`phases/SUFFIX_ATOM_TAXONOMY/results/suffix_atom_taxonomy.json` (T3, T4, T5)
