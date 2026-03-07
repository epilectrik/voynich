# C1565: Paragraph Header Modifier Divergence Exceeds HEAD Divergence 10x

**Tier:** 2
**Scope:** B, paragraph, header, atom, modifier, HEAD, divergence, specification, executive, C1287, C1396, C1468, C1479, C1543
**Phase:** ATOM_ARCHITECTURE_CLEANUP (Phase 549)
**Date:** 2026-03-06

## Claim

Paragraph headers and body lines have near-identical HEAD profiles (JSD=0.008) but divergent modifier profiles (JSD=0.085, 10.6x the HEAD divergence). Headers enrich EXECUTIVE modifiers p (3.66x) and f (3.90x) while depleting iteration modifier i (0.51x). Headers also enrich h-terminal (2.35x, the TRANSPARENT terminal per C1487) and deplete n-terminal (0.54x). Paragraph specification operates through modifier selection, not HEAD domain -- headers say HOW (with which parametric modifiers) not WHAT (in which operational domain). Resolves C1287's "MARKING-enriched header" finding: the MARKING enrichment arises from modifier profile, not HEAD selection.

## Evidence

### Slot-level JSD (header vs body)

| Slot | JSD | Interpretation |
|---|---|---|
| HEAD | 0.008 | Near-identical |
| TERMINAL | 0.019 | Very weak |
| **MODIFIER** | **0.085** | **Moderate divergence** |
| Category | 0.022 | Weak |

### Modifier enrichments in headers

| Modifier | Header Rate | Body Rate | Enrichment |
|---|---|---|---|
| **p** | 15.6% | 1.8% | **3.66x** |
| **f** | 5.2% | 0.6% | **3.90x** |
| c | 22.9% | 17.8% | 1.30x |
| d | 34.9% | 43.2% | 0.81x |
| **i** | 16.2% | 31.7% | **0.51x** |
| s | 5.5% | 4.9% | 1.12x |

### Terminal enrichments in headers

| Terminal | Header | Body | Enrichment |
|---|---|---|---|
| **h** | 12.1% | 5.2% | **2.35x** |
| **n** | 5.5% | 10.2% | **0.54x** |
| y | 19.0% | 21.1% | 0.90x |
| m | 0.8% | 1.2% | 0.67x |

### HEAD enrichments in headers (weak)

| HEAD | Header | Body | Enrichment |
|---|---|---|---|
| t | 6.2% | 3.8% | 1.62x |
| o | 14.2% | 10.7% | 1.33x |
| k | 10.2% | 13.5% | 0.76x |
| a | 9.9% | 12.4% | 0.80x |
| e | 29.1% | 30.7% | 0.95x |

HEAD divergence (JSD=0.008) is too small to carry the specification signal. The modifier slot (JSD=0.085) carries 10.6x more information about header-vs-body status.

## Interpretation

Paragraph specification operates through MODIFIER SELECTION not HEAD DOMAIN. Headers use the same operational domains (HEAD atoms) as body lines but apply different modifier profiles -- emphasizing executive/arrangement modifiers (p, f) associated with setup/configuration (C1543, C1479) over iteration modifier (i) which drives body processing. This aligns with:

- C1468: headers do infrastructure-first (p/f=marking/arrangement), not safety-first
- C1396: prep PREFIXes show structural differentiation through modifier/position, not content
- C1543: p/f are o-HEAD arrangement-affiliated modifiers

The enrichment of h-terminal (TRANSPARENT, C1487) in headers means headers use more specification-carrying suffix-attached tokens -- consistent with headers needing to encode more parametric detail.

## Falsification Criteria

1. If the modifier divergence collapses under PREFIX control
2. If headers in certain sections show HEAD-level divergence comparable to modifier-level
3. If p/f enrichment in headers is a section composition artifact

## Source

`phases/ATOM_ARCHITECTURE_CLEANUP/results/atom_cleanup.json`
