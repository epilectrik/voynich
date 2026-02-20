# C1137: Dark Pipeline MIDDLEs Are 100% HT/UN Substrate

**Tier:** 2
**Status:** Active
**Scope:** B vocabulary / A-B pipeline
**Phase:** 407 (DARK_PIPELINE_FUNCTIONAL_TEST)
**Follows:** C1135 (unmatched PP characterization)

## Finding

The 300 dark-pipeline PP MIDDLEs (shared A/B vocabulary that bypasses B's 49-class grammar) produce **exclusively** HT/UN tokens when they appear in Currier B. Zero dark-pipeline tokens are grammar-classified.

| Metric | Dark Pipeline | Matched PP (89) |
|--------|--------------|-----------------|
| Total B tokens | 1,696 | 20,009 |
| Grammar-classified | 0 (0.0%) | 16,054 (80.2%) |
| HT/UN | 1,696 (100.0%) | 3,955 (19.8%) |
| Unique word types | 1,099 | — |
| Grammar types | 0 | — |
| Mean tokens/MIDDLE | 5.7 | 224.8 |

All 300 MIDDLEs are pure-HT — none produce any grammar-classified tokens. This is not a tendency but a complete partition: unmatched PP MIDDLEs are the exclusive vocabulary substrate for B's identification layer.

## Positional and Section Characterization

Dark-pipeline tokens follow the general HT positional and section pattern:
- Folio line-1 rate: 6.9% (HT baseline: 6.5%, delta +0.4pp) -- HEADER_NEUTRAL
- Paragraph line-1 rate: 37.1% (HT baseline: 34.7%, delta +2.4pp)
- Section profile: JS(dark, HT) = 0.0005 vs JS(dark, grammar) = 0.0109 -- 22x closer to HT
- Token-level Herfindahl: 0.339 (vs C1135 MIDDLE-level 0.716 -- tokens are more dispersed than types)

## Evidence

- Phase 407, Test 1: Classification trace using `class_token_map.json` (480 classified tokens)
- 23,096 B tokens scanned (H-track, labels/uncertain excluded)
- Mean tokens/MIDDLE validates C1135's 5.7 exactly

## Implication

The A-B vocabulary pipeline has a clean functional partition: 89 matched PP MIDDLEs produce the 49-class operational grammar (80.2% grammar-classified), while 300 unmatched PP MIDDLEs produce exclusively the HT/UN identification vocabulary. The "dark pipeline" is not dark — it is the construction channel for B's compound specification layer (C935).

## Provenance

- Source: Phase 407, Tests 1, 4, 5
- Related: C1135 (dark pipeline characterization), C610 (UN morphological profile), C740 (HT=UN), C935 (compound specification)
