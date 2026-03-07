# C1552: 5 of 9 Hazard Source MIDDLEs Are Phantom Types Absent from Corpus

**Tier:** 2
**Scope:** B, MIDDLE, hazard, phantom, forbidden, corpus, chey, shey, chedy, shedy, chol, C1531, C1178, C1546, C1551
**Phase:** HAZARD_PREFIX_INTEGRATION (Phase 546)
**Date:** 2026-03-06

## Claim

Of the 9 unique MIDDLEs that appear as hazard sources in the 17 forbidden transition pairs, 5 are PHANTOM types with exactly 0 corpus tokens: chey, shey, chedy, shedy, chol. The remaining 4 corpus-present sources (dy=675, l=855, c=177, he=253) account for 100% of actual hazard source tokens. The phantom sources are ch/sh-initial MIDDLEs that would be HEADED (e-HEAD or o-HEAD) if they existed — but they do not exist in the corpus. This connects C1531 (forbidden MIDDLEs include phantom types) with C1546 (universal HEAD immunity): the grammar defines forbidden transitions involving headed source MIDDLEs, but the vocabulary system categorically excludes those MIDDLEs from the corpus.

## Evidence

### Complete hazard source MIDDLE inventory (B corpus, Phase 546)

| Source MIDDLE | Corpus tokens | HEAD status | Hazard class |
|---|---|---|---|
| l | 855 | HEADLESS | CONTAINMENT_TIMING |
| dy | 675 | HEADLESS | PHASE_ORDERING |
| he | 253 | HEADLESS (h-initial) | ENERGY_OVERSHOOT |
| c | 177 | HEADLESS | RATE_MISMATCH |
| chey | 0 | PHANTOM (would be e-HEAD) | PHASE_ORDERING |
| shey | 0 | PHANTOM (would be e-HEAD) | PHASE_ORDERING |
| chedy | 0 | PHANTOM (would be e-HEAD) | PHASE_ORDERING |
| shedy | 0 | PHANTOM (would be e-HEAD) | PHASE_ORDERING |
| chol | 0 | PHANTOM (would be o-HEAD?) | CONTAINMENT_TIMING |

5/9 source MIDDLEs = 0 tokens. These phantoms account for 7 of the 17 forbidden transition pairs (41%).

### Phantom source analysis

All 5 phantom sources begin with ch- or sh-. If parsed as MIDDLE atoms:
- chey = ch + e + y → would contain e-HEAD at position 1 (not position 0, so technically headless compound per C1493-C1498)
- shey = sh + e + y → same structure
- chedy = ch + e + d + y → same
- shedy = sh + e + d + y → same
- chol = ch + o + l → would contain o-HEAD at position 1

Per C1178, ch/sh-initial MIDDLE is a "dead naming pattern" — these MIDDLEs were defined in the forbidden transition system but never instantiated in the corpus. The forbidden topology was designed to cover POTENTIAL MIDDLEs that the vocabulary system then excluded.

### Effective forbidden transition count

Of 17 defined forbidden pairs:
- 10 involve at least one corpus-present source MIDDLE → can actually occur
- 7 involve phantom sources → structurally impossible in current corpus
- Actual violation corpus (C1360): 11 violations in 20,676 transitions = 0.053% rate

## Interpretation

The forbidden transition topology was designed CONSERVATIVELY — it prohibits transitions that the vocabulary system subsequently made impossible. This is consistent with C1178 (phantom MIDDLEs are morphologically isolated remnants of a dead naming pattern) and suggests the hazard topology was defined at a level of generality that exceeds the actual vocabulary. The grammar encodes a broader safety net than the vocabulary requires, providing defense-in-depth: even if phantom MIDDLEs were to appear (e.g., in a different manuscript section or scribal variant), the forbidden transition system would catch them.

## Falsification Criteria

1. If any phantom source MIDDLE is discovered in uncounted corpus sections
2. If the 5 phantom sources are shown to have different morphological origins than the dead ch/sh-initial pattern (C1178)
3. If forbidden transitions involving phantom sources are found to serve a different structural purpose than hazard prevention

## Source

`phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json`
