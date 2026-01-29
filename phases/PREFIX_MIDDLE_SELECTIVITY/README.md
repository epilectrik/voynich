# PREFIX_MIDDLE_SELECTIVITY Phase

## Result: PREFIX IS A BEHAVIORAL TRANSFORMER

PREFIX fundamentally transforms MIDDLE behavior. The same MIDDLE with different PREFIXes produces behavioral divergence (JSD=0.425) nearly as large as that between entirely different MIDDLEs (JSD=0.436 computed, 0.537 C657 reference). PREFIX reduces instruction class membership by 75% (median 82%). EN PREFIXes (ch/sh/qo) channel MIDDLEs into EN classes at 94.1%.

Despite this transformative power, most PP MIDDLEs are PREFIX-promiscuous: only 3.9% are locked to a single PREFIX. The B grammar freely recombines PREFIXes with MIDDLEs. This resolves the PP continuity puzzle: MIDDLEs don't form discrete pools (C656-C657) because their functional identity is determined by the PREFIX+MIDDLE combination, not MIDDLE alone.

## Key Findings

| Finding | Value |
|---------|-------|
| PP MIDDLEs observed in B | 404 (all) |
| Distinct PREFIXes with PP | 36 |
| PREFIX-locked MIDDLEs (>=10 tokens) | 5/128 (3.9%) |
| PREFIX-promiscuous MIDDLEs | 59/128 (46.1%) |
| QO MIDDLEs with qo-PREFIX dominant | 23/23 (100%) |
| Within-MIDDLE between-PREFIX JSD | 0.425 (mean) |
| Between-MIDDLE JSD (computed) | 0.436 |
| Effect ratio (within/between) | 0.975 |
| Mean class reduction by PREFIX | 75% (median 82%) |
| EN PREFIX -> EN class rate | 94.1% |
| Effective PREFIX x MIDDLE pairs | 501 (1.24x from 404) |
| Best pair clustering silhouette | 0.350 (k=2) |
| C657 MIDDLE-only silhouette | 0.237 |

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C660 | PREFIX x MIDDLE Selectivity Spectrum | 46.1% promiscuous, 3.9% locked; QO 100% qo-locked |
| C661 | PREFIX x MIDDLE Behavioral Interaction | Effect ratio 0.79-0.98; PREFIX transforms behavior |
| C662 | PREFIX Role Reclassification | 75% class reduction; EN->EN 94.1%, AX->AX/FQ 70.8% |
| C663 | Effective PREFIX x MIDDLE Inventory | 501 effective pairs, sil=0.350 at k=2 |

## Scripts

| Script | Tests | Purpose |
|--------|-------|---------|
| `prefix_middle_inventory.py` | 1-4 | Contingency table, selectivity spectrum, lane alignment, A-vs-B |
| `prefix_middle_interaction.py` | 5-7 | Behavioral interaction, role reclassification, effective inventory |

## Interpretation

The PP vocabulary system works as follows:

1. **MIDDLE defines the material/technique identity** (continuous, no discrete pools per C656)
2. **PREFIX determines what role that technique plays** (EN, AX, FQ, INFRA, etc.)
3. **The same technique (MIDDLE) can serve completely different roles** depending on PREFIX
4. **QO-predicting MIDDLEs are the exception** — they're locked to qo PREFIX (100%)
5. **B freely recombines** PREFIX and MIDDLE beyond what A records show (B_WIDER)

The combination (PREFIX, MIDDLE) is the functional unit of the B grammar, not MIDDLE alone. This explains why PP MIDDLE clustering (C656-C659) found continuous distributions: looking at MIDDLEs without PREFIX is like looking at nouns without verbs.
