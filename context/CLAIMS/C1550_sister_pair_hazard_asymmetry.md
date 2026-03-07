# C1550: Sister Pair Hazard Source Asymmetry (ch/sh 1.80x, ok/ot 0.66x Inverted)

**Tier:** 2
**Scope:** B, PREFIX, sister pair, hazard, asymmetry, ch, sh, ok, ot, da, sa, ta, C1449, C1539, C1187, C1298, C1299
**Phase:** HAZARD_PREFIX_INTEGRATION (Phase 546)
**Date:** 2026-03-06

## Claim

Sister pairs show significant hazard source rate asymmetry. ch/sh ratio = 1.804x (ch 4.73% vs sh 2.76%). ok/ot ratio = 0.664x (ok 6.09% vs ot 9.17%) — INVERTED relative to ch/sh, with the second sister being MORE hazardous. da/sa ratio = 1.537x (da 12.33% vs sa 7.79%). da/ta ratio = 1.354x (da 12.33% vs ta 9.05%). da/ka ratio = 1.529x (da 12.33% vs ka 7.64%). Sister pair hazard asymmetry extends C1449 (PREFIX channel hazard with sister parity) at atom resolution: sister pairs that share the same BASE (ch/sh, da/sa) show consistent modifier-driven asymmetry, while same-MODIFIER pairs (ok/ot) show base-driven asymmetry.

## Evidence

### Sister pair hazard source rates (B corpus, Phase 546)

| Sister A | Source rate | Sister B | Source rate | Ratio A/B |
|---|---|---|---|---|
| ch | 4.73% | sh | 2.76% | 1.804x |
| ok | 6.09% | ot | 9.17% | 0.664x |
| da | 12.33% | sa | 7.79% | 1.537x |
| da | 12.33% | ta | 9.05% | 1.354x |
| da | 12.33% | ka | 7.64% | 1.529x |

### Same-base pairs (modifier effect)

ch vs sh (both h-base): ch has 1.80x higher hazard than sh. Both access the same h-base MIDDLE vocabulary. The divergence comes from modifier-driven MIDDLE selection within the same base domain.

da vs sa vs ta vs ka (all a-base): da consistently highest at 12.33%. All a-base modifiers access headless MIDDLEs (C1537: a-base is 94-96% headless). The d-modifier routes to slightly different headless configurations than s, t, or k modifiers.

### Same-modifier pair (base effect)

ok vs ot (both o-modifier + k/t base): ok is SAFER (6.09%) than ot (9.17%). This INVERTS the ch/sh pattern. The difference is base-driven: k-base (ok) has 2.02% overall source rate vs t-base (ot) which is intermediate. k-base's lower hazard reflects its higher k-HEAD proportion.

### Connection to C1449

C1449 found PREFIX channel hazard with sister parity at the aggregate level. This decomposition shows the parity holds approximately (both sisters are in the same hazard tier) but with consistent internal asymmetry driven by the modifier or base atom's specific HEAD routing profile.

## Interpretation

Sister pairs are SAME_BASE (ch/sh, da/sa) or SAME_MOD (ok/ot) per C1539. Same-base pairs differ by modifier, which controls MIDDLE vocabulary selection within the base's domain. Same-modifier pairs differ by base, which controls HEAD proportion and thus hazard exposure. The ch>sh asymmetry is consistent with C1299 (ch-sh B-specific category divergence) and C929 (ch=active test, sh=passive monitor): active testing involves more diverse MIDDLE configurations including some hazard-adjacent ones.

## Falsification Criteria

1. If sister pair hazard rates equalize after controlling for MIDDLE vocabulary
2. If the ch>sh asymmetry reverses in any section
3. If the ok<ot inversion disappears (both are base-driven; if base effect vanishes, so does inversion)

## Source

`phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json`
