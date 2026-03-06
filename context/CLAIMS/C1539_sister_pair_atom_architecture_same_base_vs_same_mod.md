# C1539: Sister Pair Atom Architecture -- ok/ot is SAME_MOD While ch/sh and da/sa are SAME_BASE

**Tier:** 2
**Scope:** GLOBAL, PREFIX, atom, sister-pair, ch, sh, ok, ot, da, sa, SAME_BASE, SAME_MOD, HEAD, JSD, C408, C409, C1478, C1534, C1536
**Phase:** PREFIX_ATOM_TAXONOMY (Phase 544)
**Date:** 2026-03-06

## Claim

The three known sister pairs decompose into two structural types at atom level: ch/sh and da/sa share BASE but differ in MODIFIER (SAME_BASE type), while ok/ot shares MODIFIER (o) but differs in BASE (k vs t) (SAME_MOD type). Despite this structural asymmetry, all three pairs have HEAD JSD < 0.01 (content-equivalent). ok/ot has the smallest JSD (0.0034) because k and t are terminal mirrors (C1478). Non-content differentiation: ch/sh diverges on suffix rate (53.0% vs 40.7%) and articulator rate (3.9% vs 13.2%); ok/ot and da/sa show near-identical profiles on all non-content dimensions. SAME_BASE pairs differentiate on non-content axes; the SAME_MOD pair does not.

## Evidence

### Atom decomposition

| Sister Pair | Modifier 1 | Base 1 | Modifier 2 | Base 2 | Structure |
|---|---|---|---|---|---|
| ch / sh | c | h | s | h | SAME_BASE |
| ok / ot | o | k | o | t | SAME_MOD |
| da / sa | d | a | s | a | SAME_BASE |

### HEAD selection similarity

| Pair | HEAD JSD | Structure |
|---|---|---|
| ch / sh | 0.0089 | SAME_BASE |
| ok / ot | 0.0034 | SAME_MOD |
| da / sa | 0.0028 | SAME_BASE |

All JSD < 0.01: the sister pairs select functionally identical HEAD domains, confirming C408 (equivalence classes) at atom resolution.

### Non-content differentiation

| Metric | ch | sh | delta | ok | ot | delta | da | sa | delta |
|---|---|---|---|---|---|---|---|---|---|
| Suffix rate % | 53.0 | 40.7 | **12.3** | 28.5 | 27.1 | 1.4 | 19.9 | 20.7 | 0.8 |
| Articulator rate % | 3.9 | 13.2 | **9.3** | 0.8 | 0.8 | 0.0 | 3.4 | 2.7 | 0.7 |
| Headless rate % | 10.4 | 6.6 | 3.8 | 7.7 | 8.6 | 0.9 | 95.9 | 96.0 | 0.1 |
| N | 3,492 | 2,329 | | 1,476 | 1,448 | | 1,083 | 329 | |

ch/sh shows the largest non-content divergence (suffix 12.3pp, articulator 9.3pp). ok/ot and da/sa are near-identical on all dimensions.

## Interpretation

Sister pairs achieve content equivalence (identical HEAD domain) through two different structural mechanisms: SAME_BASE (shared base imposes shared domain, different modifiers provide variant selection) and SAME_MOD (shared modifier provides shared framing, different bases happen to be terminal mirrors producing the same domain). The ch/sh non-content divergence (suffix rate, articulator rate) maps to the sensory modality discrimination documented in C929 (ch=active test, sh=passive monitor). The ok/ot non-content identity is consistent with k/t being terminal mirrors (C1478) -- if the bases are structural mirrors, ALL properties (not just HEAD selection) are expected to converge.

## Falsification Criteria

1. If any sister pair HEAD JSD exceeds 0.05
2. If ok/ot shows non-content divergence comparable to ch/sh (>5pp on any dimension)
3. If a new sister pair is identified that contradicts the SAME_BASE/SAME_MOD typology

## Source

`phases/PREFIX_ATOM_TAXONOMY/results/prefix_atom_taxonomy.json`
