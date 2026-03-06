# C1461: e→y CHSH-Channel with sh Enrichment and qo/BARE Exclusion

**Tier:** 2
**Scope:** B, PREFIX, MIDDLE, atom, e-HEAD, y-terminal, channel, sh, ch, qo, BARE, C929, C1300, C1461
**Phase:** 525 (EY_SAFE_PATHWAY)
**Date:** 2026-03-05

## Claim

e→y is a CHSH-channel token with dramatic sh enrichment (2.45x) and ch enrichment (1.74x). The ch/sh ratio for e→y is 1.07 vs corpus ratio 1.50 — significantly sh-biased. qo is nearly excluded (0.04x), BARE categorically excluded (0.002x), and da absent (0.00x). e→y operates on monitoring/verification channels (ch/sh) and vessel/transfer channels (ok/ot), not on the heat source (qo) or infrastructure (BARE/da) channels.

## Evidence

### PREFIX distribution

| PREFIX | e→y count | Enrichment | Interpretation |
|--------|----------|------------|----------------|
| sh | 859 | 2.45x | Monitor-verify (passive) |
| ch | 915 | 1.74x | Test-check (active) |
| lch | 177 | 3.74x | Hold-test |
| lsh | 70 | 4.01x | Hold-monitor |
| ok | 329 | 1.48x | Vessel thermal check |
| ot | 353 | 1.62x | Vessel transfer check |
| qo | 23 | 0.04x | Heat source (almost excluded) |
| BARE | 1 | 0.002x | Categorically excluded |
| da | 0 | 0.00x | Categorically excluded |

### Sister pair ratio

- e→y ch/sh ratio: 1.07
- Corpus ch/sh ratio: 1.50
- e→y is sh-enriched relative to corpus norm

## Interpretation

e→y's sh-enrichment confirms its role as passive monitoring/verification rather than active diagnostic testing (C929: sh = passive monitor, ch = active test). The near-total exclusion from qo (heat source channel, C1300) means cooling-end operations are never applied to the fire — they operate on the vessel and process channels. The BARE/da exclusion means e→y always requires a channel specification; it is never a standalone infrastructure operation. This channel profile is consistent with e→y as steady-state process verification: "check that cooling is proceeding" rather than "intervene in the heat source."

## Falsification Criteria

1. If qo enrichment exceeds 0.50x
2. If BARE enrichment exceeds 0.10x
3. If ch/sh ratio exceeds 1.40 (matching corpus norm)

## Method

- 3,475 e→y tokens classified by PREFIX
- Enrichment computed as (e→y PREFIX fraction) / (corpus PREFIX fraction)
- ch/sh ratio computed for e→y and corpus separately

**Script:** `phases/EY_SAFE_PATHWAY/scripts/ey_safe_pathway.py`
**Results:** `phases/EY_SAFE_PATHWAY/results/ey_safe_pathway.json`

## Dependencies

- C929 (ch/sh sensory modality discrimination: ch=active test, sh=passive monitor)
- C1300 (qo near-pure THERMAL channel)
- C1411 (PREFIX→MIDDLE selectivity hierarchy)
- C1449 (PREFIX channel hazard with sister parity)
