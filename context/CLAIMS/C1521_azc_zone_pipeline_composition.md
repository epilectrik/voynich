# C1521: AZC Zone Pipeline Composition Varies

**Tier:** 2
**Scope:** AZC, zone, pipeline, bridge, dark, exclusive, o-HEAD, C1139, C1272
**Phase:** AZC_ZONE_ATOMIZATION (Phase 541)

## Claim

AZC zones have systematically different pipeline compositions. Bridge MIDDLEs dominate all zones (62-80%) but S-zone has the lowest bridge rate (61.9%) and highest dark (16.8%) and exclusive (21.4%) rates. P-zone is most bridge-dominated (80.4%) with lowest exclusive rate (9.8%). Within each zone, dark pipeline MIDDLEs concentrate o-HEAD at 34.5% vs bridge MIDDLEs at 18.7% (1.84x ratio) -- dark vocabulary is more arrangement-oriented regardless of zone. This extends C1272 (AZC mediates bridge-dark sorting) with atom-level resolution: the sorting mechanism operates through HEAD domain selection, with dark MIDDLEs being disproportionately o-domain (arrangement/configuration).

## Evidence

- Pipeline composition by zone:
  - R (N=1326): bridge=76.6%, dark=10.4%, exclusive=13.0%
  - C (N=629): bridge=78.5%, dark=8.1%, exclusive=13.4%
  - S (N=501): bridge=61.9%, dark=16.8%, exclusive=21.4%
  - P (N=397): bridge=80.4%, dark=9.8%, exclusive=9.8%
  - L (N=68): bridge=72.1%, dark=7.4%, exclusive=20.6%
  - AZC overall: bridge=74.2%, dark=11.1%, exclusive=14.8%
- o-HEAD rate by pipeline type within zone:
  - Bridge overall: 18.7%
  - Dark overall: 34.5% (1.84x bridge)
  - Exclusive overall: 32.1% (1.72x bridge)
- S-zone dark MIDDLEs: 44.0% o-HEAD (highest of any zone-pipeline combination)
- C-zone dark MIDDLEs: 41.2% o-HEAD (second highest)

## Relationship to Prior Constraints

- **Extends C1272**: Bridge-dark zone sorting confirmed at atom level; dark vocabulary is o-HEAD enriched across all zones
- **Extends C1500**: Bridge enriched in e/k/t (executable backbone) -- bridge's lower o-HEAD confirms they carry execution domain atoms
- **Extends C1505**: Dark pipeline MARKING-dominant (nominalization) -- o-HEAD enrichment in dark MIDDLEs is consistent with arrangement/labeling function
- **Connects C1139**: Bridge and dark completely disjoint -- their different HEAD profiles persist across all AZC zones
- **Connects C1517**: Zone-level o-HEAD variation is partially pipeline-mediated: zones with more dark MIDDLEs (S) are more o-enriched

## Source

`phases/AZC_ZONE_ATOMIZATION/results/azc_zone_atomization.json` (T9)
