# C658: PP Material Gradient

**Tier:** 2 | **Status:** CLOSED | **Scope:** A

## Finding

Material class creates a weak gradient in PP co-occurrence structure, not a discrete partition. Forced co-occurrence clusters reduce material class entropy by 36.2% (overall 1.885 bits → within-pool 1.203 bits), but NMI(pool, material)=0.129 indicates low mutual information. Chi-squared pool×material is significant (p=0.002, Cramér's V=0.392) confirming non-random material association, but no pool is material-pure. The largest pool (69/203 members) is 54% MIXED material. All other axes show even weaker signal: pathway NMI=0.032, lane NMI=0.062, section NMI=0.087.

## Evidence

- 203 PP, forced into 20 co-occurrence pools (silhouette 0.016, below threshold)
- Material class entropy: overall 1.885 bits, within-pool mean 1.203 bits
- Entropy reduction: 0.681 bits (36.2%)
- NMI(pool, material) = 0.129 — well below 0.8 redundancy threshold
- Chi-squared: chi2=93.4, p=0.002, df=57, Cramér's V=0.392
- NMI(pool, pathway) = 0.032 — near zero
- NMI(pool, lane) = 0.062 — near zero
- NMI(pool, section) = 0.087 — near zero
- ARI(new pools, existing pp_classification clusters) = 0.057 — independent
- Pool 18: 69 members (34%), material: MIXED=37, HERB=18, ANIMAL=12, NEUTRAL=2
- Pool 11: 3 members, all ANIMAL — only pure-material pool

## Interpretation

PP co-occurrence structure carries some material-class information, but as a gradient: ANIMAL-enriched PP and HERB-enriched PP partially segregate, but the majority of PP (MIXED + NEUTRAL = 56%) occupy the middle of the gradient. No axis (material, pathway, lane, section) captures more than 13% of pool structure. The PP vocabulary is multi-dimensionally continuous — each MIDDLE occupies a unique position in a space defined by weak, independent gradients.

## Cross-References

- C538: PP material class distribution (ANIMAL 63, HERB 113, MIXED 67, NEUTRAL 161)
- C505: Individual PP enrichment ratios (te 16.1x, ho 8.6x in animal)
- C642: A records actively mix material classes (below-chance consistency) — consistent
- C656: Co-occurrence itself is continuous

## Provenance

PP_POOL_CLASSIFICATION, Script 1 (pp_cooccurrence_clustering.py), Test 3
