# Phase 537: DISPLACED_HEAD_GRAMMAR

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints:** C1494-C1498

---

## Research Question

C1493 found that 35.7% of "headless" compound MIDDLEs contain HEAD atoms {a,e,o,k,t} at non-initial positions. Are these "displaced HEADs" functioning as domain selectors in an alternative compositional order (MOD+HEAD+TERM), or are HEAD-set characters carrying a different functional role when not in position 0?

## Verdict

**HEAD_SET_CHARACTER_NOT_FUNCTIONING_AS_HEAD**

Displaced HEAD-set characters are NOT functioning as domain selectors. The first atom (pseudo-HEAD) determines operational category 2.68x more accurately than the displaced HEAD atom. The HEAD-set character in non-initial position carries a different functional role (modifier/terminal), consistent with the dual-role behavior already documented for k/t (C1394, C1478). The "headless" label is structurally accurate: these compounds lack a HEAD in the grammatical sense even though they contain HEAD-set characters.

## Key Findings

### Population (C1494)

1,182 displaced-HEAD tokens (35.7% of headless, 7.3% of all compound tokens), 334 types.

HEAD-set character frequency is INVERTED relative to canonical HEAD usage:
- k: 42.0% displaced vs 7.9% canonical (5.31x enriched)
- t: 18.5% displaced vs 2.7% canonical (6.90x enriched)
- o: 14.6% displaced vs 18.1% canonical (0.81x -- near parity)
- a: 12.6% displaced vs 23.5% canonical (0.54x depleted)
- e: 12.2% displaced vs 47.8% canonical (0.26x strongly depleted)

This inversion maps directly to the k/t dual-role property (C1394): k and t function as TERMINAL atoms when not in position 0, explaining their enrichment. e, which is almost never terminal, is strongly depleted.

### Category Prediction (C1495)

The decisive test: does the displaced HEAD or the pseudo-HEAD (first atom) better predict operational category?

| Predictor | Accuracy | N |
|-----------|----------|---|
| Pseudo-HEAD (first atom) | 35.1% | 1,084 |
| Displaced HEAD atom | 13.1% | 1,084 |
| **Ratio** | **2.68x** | |

Additional evidence:
- 0/5 displaced HEADs share the same dominant category as their canonical HEAD counterpart
- Displaced tokens are MORE similar to same-pseudo-HEAD genuine headless tokens (JSD=0.510) than to same-HEAD canonical tokens (JSD=0.529)
- k canonical = THERMAL (70.6%), k displaced = OPERATION (40.8%)
- e canonical = OPERATION (36.7%), e displaced = MARKING (70.5%)
- t canonical = FLOW (65.1%), t displaced = MONITORING (46.4%)

### c-Modifier Displacement Context (C1496)

The modifier 'c' is the primary displacement trigger:
- 87.1% of c-initial headless tokens contain a displaced HEAD (533/612)
- c+k specifically: 365 tokens (68.5% of c-initial displaced)
- c+t: 167 tokens (31.3% of c-initial displaced)
- Pattern MH (modifier+HEAD) accounts for 28.9% of all displaced tokens

The ck/ct MIDDLEs are the structural backbone: ck=197 tokens, ckh=127, ct=95, cth=49. These are c-modifier + k/t-terminal compounds where k and t function in their TERMINAL role (C1478), not as domain-selecting HEADs.

q-initial tokens (92.3% displacement rate, 96/104) are a separate phenomenon -- these are PREFIX characters leaking into MIDDLE position (98% BARE, 100% UNK category), not part of the instruction grammar.

### Suffix Rate Anomaly (C1497)

Displaced-HEAD tokens have dramatically elevated suffix rates:
- Displaced: 89.8%
- Canonical headed: 35.7%
- Genuine headless: 24.0%

This 2.51x enrichment vs canonical is the strongest morphological signature. Per pseudo-HEAD: c-initial 96.3%, l-initial 83.8%, y-initial 90.0%. The elevated suffix rate indicates these tokens are PARAMETRIC (requiring suffix specification), unlike genuine headless d/i-initial tokens which are BARE (binary operations, C1492).

### Terminal Exclusion Gate (C1498)

Terminal atom categorically controls whether displacement occurs:
- n-terminal: 0.36% displacement rate (3/828) -- near-categorical exclusion
- y-terminal: 0.39% displacement rate (3/775) -- near-categorical exclusion
- bare (no terminal): 83.9% displacement rate (908/1082) -- strong predictor

This connects to C1487: n and y are CHANNELED terminals that lock category (TRANSITION, OPERATION respectively). They impose their category so strongly that HEAD-set atoms cannot appear alongside them without creating a grammatical conflict. Bare-terminal (DIFFUSE, no category lock) permits HEAD-set atoms freely because no terminal category conflicts.

### Hazard Profile

Displaced-HEAD tokens are categorically safe:
- High-frame hazard: 0.08% (vs 28.9% canonical, 31.7% genuine headless)
- r-terminal: 1.4% (vs 9.1% canonical)

This is consistent with the LOCKED tier depletion in headless compounds (C1490).

### PREFIX Profile

PREFIX distribution of displaced tokens is closer to canonical headed (JSD=0.378) than to genuine headless (JSD=0.410). Top PREFIXes for displaced: ch (28.3%), BARE (29.2%), sh (10.9%), qo (10.3%). This contrasts sharply with genuine headless which is dominated by da (25.7%), BARE (11.7%), sa (8.7%).

The ch/sh/qo PREFIXes in displaced tokens reflect the operational grammar context these tokens participate in -- they function within the standard instruction system, not in the headless-specific da/sa/ta channel.

### Line Position

No significant positional difference: displaced mean=0.512, canonical=0.498, genuine headless=0.504. Mann-Whitney p=0.187 (displaced vs canonical). These tokens are not spatially specialized.

## Implications

1. **C1493's "displaced HEAD" population is resolved**: HEAD-set characters in non-initial positions function as MODIFIERS or TERMINALS, not as HEADs. The term "displaced HEAD" is a misnomer -- there is no alternative compositional order MOD+HEAD+TERM. The correct characterization is: headless compounds that happen to contain atoms from the HEAD set operating in their non-HEAD role.

2. **k/t dual-role confirmed at population scale**: The k/t terminal mirror (C1478) is the mechanistic explanation for k/t enrichment in displacement. When k appears after a modifier (e.g., ck, lk), it functions as a terminal atom carrying OPERATION or CONTAINMENT semantics, not as a THERMAL domain HEAD.

3. **The headless domain is genuinely headless**: Even the 35.7% with HEAD-set characters do not have a functional HEAD. The instruction grammar has exactly two compositional modes: HEAD+MOD*+TERM (canonical, position-0 HEAD is domain selector) and pseudoHEAD+MOD*+TERM (headless, position-0 modifier/terminal acts as pseudo-HEAD with different category mapping per C1489).

4. **c-modifier as operational context**: c-initial tokens with k/t content (ck, ckh, ct, cth) are the dominant displaced pattern. These are c(adjust) + k/t(terminal) compounds -- the 'c' modifier selects for OPERATION/CONTAINMENT domains (C1389), and k/t serve as terminals rather than HEADs.

## Constraints Produced

| # | Constraint | Tier |
|---|-----------|------|
| C1494 | Displaced HEAD k/t enrichment with inverted frequency | 2 |
| C1495 | HEAD-set atoms do not function as domain selectors when displaced | 2 |
| C1496 | c-modifier primary displacement context | 2 |
| C1497 | Displaced HEAD extreme suffix rate (89.8%) | 2 |
| C1498 | n/y-terminal categorical displacement exclusion | 2 |

## Files

- Script: `phases/DISPLACED_HEAD_GRAMMAR/scripts/displaced_head_grammar.py`
- Results: `phases/DISPLACED_HEAD_GRAMMAR/results/displaced_head_grammar.json`
