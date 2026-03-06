# C1516: AZC HEAD Domain Differentiation Across Zones

**Tier:** 2
**Scope:** AZC, zone, atom, HEAD, differentiation, domain, chi2, V=0.115
**Phase:** AZC_ZONE_ATOMIZATION (Phase 541)

## Claim

AZC positional zones (R, C, S, P) show statistically significant differentiation at the HEAD atom slot level (chi2=112.3, V=0.115, p=5.81e-17, N=2,853 tokens across 4 major zones). The HEAD atom (domain selector, C1475) varies by zone: S-zone is most o-HEAD enriched (29.3%, 2.49x B), a-HEAD enriched (22.2%); R-zone is most e-HEAD enriched (34.6%) and least o-HEAD (17.7%, 1.51x B); C-zone is intermediate o-HEAD (26.2%, 2.23x B); P-zone has highest k-HEAD (6.0%) and highest headless rate (33.0%). This REFINES C1271 (AZC zone atom-level uniformity null): raw character-level (AXIS cluster) analysis found null because it mixed atoms across slot positions. HEAD slot decomposition (C1394) reveals the differentiation is in WHICH DOMAIN each zone selects, not in raw character frequencies.

## Evidence

- N=3,227 AZC tokens decomposed, 2,853 in major zones (R/C/S/P)
- chi2=112.3, p=5.81e-17, Cramer's V=0.115 (4 zones x 6 HEAD categories)
- HEAD profiles by zone:
  - R (N=1326): a=16.5%, e=34.6%, o=17.7%, k=2.3%, t=1.6%, headless=27.3%
  - C (N=629): a=14.3%, e=28.9%, o=26.2%, k=1.6%, t=1.1%, headless=27.8%
  - S (N=501): a=22.2%, e=26.1%, o=29.3%, k=1.2%, t=0.0%, headless=21.2%
  - P (N=397): a=8.8%, e=32.0%, o=19.1%, k=6.0%, t=1.0%, headless=33.0%
- Overall AZC: a=15.3%, e=30.8%, o=22.4%, k=2.6%, t=1.1%, headless=27.9%
- B baseline: a=13.3%, e=30.3%, o=11.8%, k=13.4%, t=4.0%, headless=27.2%

## Relationship to Prior Constraints

- **Refines C1271**: C1271 found 0/8 AXIS clusters significant at Bonferroni using KW per-folio test. Phase 541 uses HEAD slot decomposition (C1394) on individual tokens, finding V=0.115 significant -- atoms differentiate when slot-decomposed but not when raw-counted
- **Extends C1269**: Zone category specialization (V=0.084) now has an atom-level mechanism -- HEAD domain selection mediates category differences
- **Connects C1475**: HEAD as domain selector operates in AZC exactly as in B (5 HEAD atoms + headless)
- **Connects C1502**: o-HEAD enrichment confirmed as zone-graded (see C1517)
- **Extends C1499**: Shared substrate confirmed in AZC at HEAD+MOD+TERM resolution

## Source

`phases/AZC_ZONE_ATOMIZATION/results/azc_zone_atomization.json` (T2, T8)
