# C1139: Dark Pipeline and Bridge Backbone Are Completely Disjoint

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / A-B pipeline
**Phase:** 407 (DARK_PIPELINE_FUNCTIONAL_TEST)

## Finding

The 300 dark-pipeline PP MIDDLEs and the 85 bridge MIDDLEs (C1013) have **zero overlap**. These are completely separate vocabulary populations serving different structural functions.

| Population | Count | Function |
|-----------|-------|----------|
| Dark pipeline | 300 | HT/UN identification substrate (C1137) |
| Bridge backbone | 85 | Cross-system manifold backbone (C1013, C1014) |
| Overlap | 0 | — |

Both populations are PP MIDDLEs (shared between A and B), but they partition into non-overlapping functional roles:
- Bridge MIDDLEs appear in grammar-classified tokens and carry 91% of archetype-predictive signal (C1014)
- Dark-pipeline MIDDLEs appear exclusively in HT/UN tokens at low frequency (mean 5.7 tokens)

## Evidence

- Phase 407, Test 3: Set intersection of 300 dark-pipeline MIDDLEs with 85 bridge MIDDLEs
- Intersection = empty set

## Implication

The A-B vocabulary pipeline has three cleanly separated channels:
1. **Bridge MIDDLEs (85):** High-frequency, grammar-classified, carry dynamical/behavioral information across systems
2. **Non-bridge matched PPs (~4):** Grammar-classified but not bridges
3. **Dark-pipeline MIDDLEs (300):** Low-frequency, exclusively HT/UN, carry identification/specification information

The bridge backbone and the dark pipeline are parallel but independent pathways through the shared vocabulary pool. Bridge MIDDLEs structure B's operational behavior; dark-pipeline MIDDLEs structure B's identification vocabulary. Neither population borrows from the other.

## Provenance

- Source: Phase 407, Test 3
- Related: C1013 (85 bridge MIDDLEs), C1014 (bridge archetype signal), C1135 (dark pipeline characterization), C1137 (100% HT substrate)
