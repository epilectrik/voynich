# Phase 538: Cross-Layer Atom Decomposition -- Bridge vs Dark Pipeline

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1499-C1505 (7 new)
**Predictions:** 4/5 confirmed (P1, P2, P4, P5 PASS; P3 FAIL)

## Research Question

Is the HEAD+MOD*+TERM atom grammar (C1393-C1394) manuscript-wide or B-local? Do bridge and dark pipeline MIDDLEs differ at atom-level slot composition?

## Context

C1394 established that compound MIDDLEs encode instructions as HEAD + MOD* + TERM with 18 atoms partitioned into 4 slot roles (5 HEAD, 6 MOD, 6 TERM, 2 dual). C1395 showed this encoding is shared between A and B MIDDLEs. C1140 partitioned the 404 PP MIDDLEs into bridge (85, dynamical backbone) and dark (300, identification substrate). C1141 showed dark compounds are built from bridge atoms at 96.5% coverage. This phase tests whether the slot grammar itself -- the proportions of HEAD, MOD, and TERM atoms -- differentiates across pipeline channels.

## Method

10 tests (a-j) across 7 channels: bridge (85), dark (300), a_exclusive (579), b_only (900), all_A (972), all_B (1293), all_AZC (617). Each MIDDLE decomposed into HEAD initial atom, TERMINAL final atom, and MODIFIER interior atoms using the C1393 slot grammar. JSD matrices computed for all 7x7 channel pairs across HEAD, TERMINAL, and MODIFIER distributions.

## Key Findings

### Test a: HEAD domain profiles
Bridge enriched in executable HEADs e/k/t (37.6% combined) vs dark (31.0%). Dark enriched in o-HEAD (28.7% vs bridge 16.5%, 1.74x) and o+headless combined (63.3% vs 51.8%). AZC shows strongest o-HEAD enrichment of any channel (31.8%, 2.70x vs B baseline).

### Test b: Terminal tier profiles
Bridge is the terminal-tier OUTLIER -- highest LOCKED rate (8.2%), highest CHANNELED (23.5%), lowest bare (58.8%). Dark prefers bare (74.7%) + DIFFUSE/h (15.7%). TERM JSD bridge-to-others: 0.039-0.082 (5-20x larger than between non-bridge channels).

### Test c: Modifier profiles
All channels use same 6 modifiers {p,c,i,f,d,s}. c dominant everywhere. MOD JSD between non-bridge channels: 0.002-0.007. Bridge outlier (MOD JSD 0.074-0.088) driven by lower modifier rate (77.7%) and different proportions.

### Test d: Headless rates
Bridge 35.3%, dark 34.7% -- virtually identical. A-exclusive highest at 44.7%. AZC lowest at 25.9%. Headless rate does not differentiate bridge from dark.

### Test e: Category stability
Bridge HEAD categories match C1475 taxonomy: k=THERMAL 50%, t=FLOW 83%, a=TRANSITION 50%. Bridge distributes balanced across all 8 categories (V=0.4427). Dark is MARKING-dominant (36.0%) with FLOW secondary (20.2%) and depleted TRANSITION (2.1%).

### Test f: Bridge redistribution
Same bridge MIDDLEs undergo dramatic morphological redistribution between A and B: suffix -edy ~50x B-enriched, PREFIX ct ~12x A-enriched, PREFIX qo ~2x B-enriched. HEAD JSD between A-weighted and B-weighted bridge profiles: 0.0767.

### Test g: AZC HEAD enrichment
AZC o-HEAD 2.70x enriched (type-level), confirming and extending C1381. k-HEAD 0.314x, t-HEAD 0.488x depleted. AZC is arrangement-dominated, execution-depleted.

### Test h: JSD matrices (HEAD/TERM/MOD)
Bridge is the outlier in all three matrices. Non-bridge channels cluster tightly (HEAD JSD mean ~0.020, TERM ~0.005, MOD ~0.004). Bridge TERM JSD to others is the largest divergence (0.039-0.082).

### Test i: Compound depth
Bridge mean length 2.27 atoms (simplest). Dark 3.33, a_exclusive 4.52, b_only 4.50. Atom Jaccard minimum 0.895 (bridge-dark and bridge-a_exclusive). All channels share the same substrate.

### Test j: Atom Jaccard similarity
Minimum pairwise Jaccard: 0.895. All channels draw from the same 18-atom core. Differences of 1-2 rare atoms (g in bridge/AZC, x in B/AZC) do not alter the fundamental substrate identity.

## Predictions

| # | Prediction | Result | Key metric |
|---|-----------|--------|------------|
| P1 | Bridge enriched in e/k/t HEADs | **PASS** | Bridge 37.6% > dark 31.0% |
| P2 | Dark enriched in o-HEAD + headless | **PASS** | Dark 63.3% > bridge 51.8% |
| P3 | Dark prefers CHANNELED terminals (h,n,y) | **FAIL** | Dark DIFFUSE+CHANNELED 21.7% < bridge 32.9% |
| P4 | Bridge tolerates more LOCKED terminals (m,r) | **PASS** | Bridge 8.2% > dark 3.7% |
| P5 | Same atoms, different slot proportions | **PASS** | Jaccard 0.895, HEAD JSD 0.024 |

**P3 failure explanation:** Dark does NOT prefer CHANNELED terminals (y,l,n). Instead, dark strongly prefers bare (74.7%) + DIFFUSE/h (15.7%), actively avoiding CHANNELED y/n terminals (0.064x and 0.072x vs B). The prediction wrongly assumed dark would use n/y terminals; in fact, dark's identification function requires maximally transparent terminals that impose no category constraint.

## Verdict

**SHARED_SUBSTRATE_GRADED_SLOTS:** The HEAD+MOD*+TERM slot grammar is manuscript-wide (atom Jaccard >= 0.895, modifier JSD < 0.007 between non-bridge channels). Channels differentiate through slot PROPORTIONS, not slot INVENTORIES. Bridge is the systematic outlier across all three slot types, reflecting its unique dual-system role as the dynamical backbone connecting A registry to B execution. Dark pipeline uses the same atoms but in identification-optimized proportions: o-HEAD dominant, bare/h-terminal dominant, full modifier complement.

## Constraints Produced

| # | Constraint | Tier |
|---|-----------|------|
| C1499 | Atom ontology is manuscript-wide shared substrate | 2 |
| C1500 | Bridge-dark HEAD domain differentiation | 2 |
| C1501 | Bridge terminal tier outlier | 2 |
| C1502 | AZC o-HEAD domain enrichment (2.70x) | 2 |
| C1503 | Bridge atom redistribution across A/B | 2 |
| C1504 | Modifier grammar universality | 2 |
| C1505 | Dark pipeline MARKING-dominant category profile | 2 |

## Files

- Script: `phases/CROSS_LAYER_ATOM_DECOMPOSITION/scripts/cross_layer_atoms.py`
- Results: `phases/CROSS_LAYER_ATOM_DECOMPOSITION/results/cross_layer_atoms.json`
- Constraints: `context/CLAIMS/C1499.md` through `context/CLAIMS/C1505.md`
