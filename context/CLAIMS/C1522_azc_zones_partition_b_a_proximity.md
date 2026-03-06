# C1522: AZC Zones Partition Between B-Proximate and A-Proximate

**Tier:** 2
**Scope:** AZC, zone, HEAD, JSD, B, A, proximity, partition, system-alignment
**Phase:** AZC_ZONE_ATOMIZATION (Phase 541)

## Claim

AZC zones are not uniformly intermediate between B and A atom profiles. They partition into B-proximate zones (R, P) and A-proximate zones (C, S, L) based on HEAD domain JSD. R-zone (JSD to B=0.042, to A=0.063) and P-zone (JSD to B=0.029, to A=0.034) are HEAD-closer to B. C-zone (JSD to B=0.065, to A=0.042), S-zone (JSD to B=0.103, to A=0.084), and L-zone (JSD to B=0.100, to A=0.036) are HEAD-closer to A. Overall AZC is near-equidistant (JSD to B=0.048, to A=0.045). The B-proximate zones (R, P) are those with lowest o-HEAD enrichment and highest bridge rate; the A-proximate zones (C, S, L) are those with highest o-HEAD enrichment and more dark/exclusive vocabulary. This partitioning extends C301 (AZC is HYBRID B=69.7%, A=65.4%) with zone-level resolution: the hybridity is not uniform but zone-graded.

## Evidence

- HEAD JSD from AZC zones to B and A:
  - R: vs_B=0.042, vs_A=0.063 -- closer to B
  - C: vs_B=0.065, vs_A=0.042 -- closer to A
  - S: vs_B=0.103, vs_A=0.084 -- closer to A
  - P: vs_B=0.029, vs_A=0.034 -- closer to B (closest to B overall)
  - L: vs_B=0.100, vs_A=0.036 -- closer to A (closest to A overall)
  - AZC overall: vs_B=0.048, vs_A=0.045 -- near-equidistant, slight A edge
- B-proximate zones (R, P): lower o-HEAD (17.7%, 19.1%), higher bridge (76.6%, 80.4%)
- A-proximate zones (C, S, L): higher o-HEAD (26.2%, 29.3%, 30.9%), more dark/exclusive
- Initial-atom (not HEAD-decomposed) JSD tells similar story with R and P still B-proximate

## Relationship to Prior Constraints

- **Refines C301**: AZC hybrid nature (B=69.7%, A=65.4% overlap) is zone-graded, not uniform
- **Extends C1516**: Zone HEAD differentiation maps onto system-proximity gradient
- **Connects C1507**: A selects o-HEAD/headless (arrangement emphasis); A-proximate zones show the same emphasis
- **Connects C435**: S/R positional division (boundary/interior) may correspond to A-proximate/B-proximate partition
- **Connects C1517**: o-HEAD gradient across zones drives system-proximity partition

## Source

`phases/AZC_ZONE_ATOMIZATION/results/azc_zone_atomization.json` (T10)
