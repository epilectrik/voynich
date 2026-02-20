# C1141: Dark Pipeline Compounds Are Built from Bridge Atoms

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / morphological construction
**Phase:** 408 (PP_PIPELINE_ATOM_DECOMPOSITION)

## Finding

Dark-pipeline compound MIDDLEs are overwhelmingly constructed from bridge MIDDLEs as atomic building blocks, despite having zero MIDDLE-level overlap with bridges (C1139).

| Metric | Value |
|--------|-------|
| Compound dark-pipeline MIDDLEs | 200 (66.7% of 300) |
| Atomic dark-pipeline MIDDLEs | 100 |
| Unique atoms found | 50 |
| Atoms classified BRIDGE | 43 (86.0% of types) |
| Atoms classified DARK_PIPELINE | 6 (12.0%) |
| Atoms classified OTHER | 1 (2.0%) |
| Bridge atom occurrence fraction | 91.6% |
| Compounds with >= 1 bridge atom | 193/200 (96.5%) |
| Mean atoms per compound | 1.44 |

### Atom Count Distribution

| Atoms per compound | Count |
|-------------------|-------|
| 1 | 123 |
| 2 | 67 |
| 3 | 10 |

### Top Atoms by Frequency

The most frequent atoms in dark-pipeline compounds are all bridge MIDDLEs: eo (28), od (25), ai (22), ed (18), ol (15), ee (15), ok (13), al (13), ot (12), or (11).

## Evidence

- Phase 408, Test 2: Decomposition of 200 compound dark-pipeline MIDDLEs using `MiddleAnalyzer.get_maximal_atoms()`
- Atom classification against bridge set (85), matched PP set (89), dark pipeline set (300)

## Implication

The three A-B pipeline channels (C1139) are connected at construction level: bridge MIDDLEs serve as the atomic alphabet from which dark-pipeline compounds are assembled. The MIDDLE-level disjointness (C1139) masks an atom-level dependency: identification vocabulary is morphologically derived FROM dynamical vocabulary. This establishes a construction hierarchy:

```
Bridge atoms (85, short, universal)
    |
    | Compositional construction (1-3 atoms per compound)
    v
Dark-pipeline compounds (200, section-concentrated)
    |
    | Token construction (PREFIX + compound MIDDLE + SUFFIX)
    v
HT/UN identification tokens (1,696, C1137)
```

The bridge backbone is thus both the dynamical backbone of B's 49-class grammar AND the morphological substrate of B's identification vocabulary.

## Provenance

- Source: Phase 408, Test 2
- Related: C1013 (bridge topological selection), C1139 (bridge-dark disjoint), C1137 (100% HT substrate), C924 (97.9% HT contain PP atoms), C766 (UN derived vocabulary)
